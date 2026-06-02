#!/usr/bin/env python3
"""Market Map — book + render engine (standard library only).

This module holds every piece of non-API logic the project needs: trade-book
persistence, mark-to-market math, the scoreboard, regime logging, and the full
inline-SVG HTML assembly. There are NO third-party imports and NO network calls.

The workflow: Claude Code gathers the data (web searches following PROMPT.md),
builds a `brief` dict matching the schema in PROMPT.md, then calls:

    import book, json
    trades = book.load_trades()
    regime_log = book.load_json(book.REGIME_PATH, [])
    book.mark_to_market(trades, {"MM-2026-001": 1.6312, ...})   # levels I fetched
    regime_log = book.update_regime_log(regime_log, brief["regime"], brief["regime_note"])
    book.ingest_ideas(trades, brief["new_ideas"], "reactive")
    book.ingest_ideas(trades, brief["pre_position_ideas"], "pre-position")
    html = book.build_html(brief, trades, regime_log)
    open(book.OUTPUT_PATH, "w", encoding="utf-8").write(html)
    book.save_json(book.TRADES_PATH, trades)
    book.save_json(book.REGIME_PATH, regime_log)
"""

import json
import os
import re
import html
from datetime import datetime, date

import charts

HERE = os.path.dirname(os.path.abspath(__file__))
TRADES_PATH = os.path.join(HERE, "trades.json")
REGIME_PATH = os.path.join(HERE, "regime_log.json")
OUTPUT_PATH = os.path.join(HERE, "output.html")
TODAY = date.today().isoformat()


# --------------------------------------------------------------------------
# Terminal progress
# --------------------------------------------------------------------------
def log(msg):
    print(f"  · {msg}", flush=True)


def step(msg):
    print(f"\n[{datetime.now():%H:%M:%S}] {msg}", flush=True)


# --------------------------------------------------------------------------
# State persistence
# --------------------------------------------------------------------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_trades():
    data = load_json(TRADES_PATH, {"open": [], "closed": []})
    data.setdefault("open", [])
    data.setdefault("closed", [])
    return data


# --------------------------------------------------------------------------
# Trade math
# --------------------------------------------------------------------------
def trade_direction(t):
    """Return +1 for long, -1 for short. Infer from the trade text, fall back
    to the geometry of stop/target around entry."""
    txt = (t.get("trade", "") + " " + t.get("structure", "")).lower()
    has_short = bool(re.search(r"\b(short|sell|fade|bear)\b", txt))
    has_long = bool(re.search(r"\b(long|buy|bull|own)\b", txt))
    if has_short and not has_long:
        return -1
    if has_long and not has_short:
        return 1
    # ambiguous (e.g. a spread "long X vs short Y") or no keyword:
    # fall back to the geometry of stop/target around entry
    entry, target = t.get("entry"), t.get("target")
    if entry is not None and target is not None:
        return 1 if target >= entry else -1
    return 1


def pnl_pct(t, level):
    entry = t.get("entry")
    if not entry:
        return 0.0
    return trade_direction(t) * (level - entry) / entry * 100.0


def hit_stop(t, level):
    d = trade_direction(t)
    stop = t.get("stop")
    if stop is None:
        return False
    return level <= stop if d > 0 else level >= stop


def hit_target(t, level):
    d = trade_direction(t)
    target = t.get("target")
    if target is None:
        return False
    return level >= target if d > 0 else level <= target


def days_held(t, exit_date=None):
    try:
        o = date.fromisoformat(t["opened"])
        e = date.fromisoformat(exit_date) if exit_date else date.today()
        return (e - o).days
    except Exception:
        return 0


def progress_to_target(t, level):
    entry, target = t.get("entry"), t.get("target")
    if entry is None or target is None or target == entry:
        return 0.0
    p = (level - entry) / (target - entry)
    return max(0.0, min(1.0, p))


# --------------------------------------------------------------------------
# Mark open trades to market
# --------------------------------------------------------------------------
def mark_to_market(trades, levels):
    """`levels` maps trade id -> current level (float) or None if unverified.
    Appends a dated history entry with directional P&L%, and rolls stopped/
    target trades into `closed`."""
    still_open = []
    for t in trades["open"]:
        level = levels.get(t["id"]) if levels else None
        if level is None:
            log(f"   {t['id']} level unverified — holding last mark")
            still_open.append(t)
            continue
        level = float(level)
        pl = round(pnl_pct(t, level), 2)
        log(f"   {t['id']} @ {level}  ->  {pl:+.2f}%")

        if hit_target(t, level):
            close_trade(trades, t, level, "TARGET", pl)
        elif hit_stop(t, level):
            close_trade(trades, t, level, "STOPPED", pl)
        else:
            t["history"].append(
                {"date": TODAY, "level": level, "pnl_pct": pl, "status": "open"}
            )
            t["current"] = level
            t["current_pnl_pct"] = pl
            still_open.append(t)
    trades["open"] = still_open


def close_trade(trades, t, level, result, pl, reason=None):
    log(f"   >>> {result} {t['id']} at {level}  ({pl:+.2f}%)")
    t["history"].append(
        {"date": TODAY, "level": level, "pnl_pct": pl, "status": result.lower()}
    )
    t["exit"] = {
        "date": TODAY,
        "level": level,
        "result": result,
        "pnl_pct": pl,
        "days_held": days_held(t, TODAY),
    }
    if reason:
        t["exit"]["reason"] = reason
    t["current"] = level
    t["current_pnl_pct"] = pl
    if t in trades["open"]:
        trades["open"].remove(t)
    trades["closed"].append(t)


def discretionary_close(trades, trade_id, level, reason):
    """Close on a broken thesis — but NEVER before min_hold_days has elapsed."""
    for t in list(trades["open"]):
        if t.get("id") != trade_id:
            continue
        held = days_held(t, TODAY)
        min_hold = int(t.get("min_hold_days", 0) or 0)
        if held < min_hold:
            log(f"   refuse discretionary close: {trade_id} held {held}d "
                f"< min_hold {min_hold}d")
            return False
        pl = round(pnl_pct(t, float(level)), 2)
        close_trade(trades, t, float(level), "DISCRETIONARY", pl, reason=reason)
        return True
    log(f"   discretionary close: {trade_id} not found in open book")
    return False


# --------------------------------------------------------------------------
# Regime log
# --------------------------------------------------------------------------
def update_regime_log(regime_log, regime, note):
    if not regime:
        return regime_log
    last = regime_log[-1]["regime"] if regime_log else None
    if regime.strip() != (last or "").strip():
        regime_log.append({"date": TODAY, "regime": regime.strip(), "note": note or ""})
        log(f"regime changed -> {regime}")
    else:
        log("regime unchanged")
    return regime_log


# --------------------------------------------------------------------------
# Ingest new ideas into the trade book
# --------------------------------------------------------------------------
def next_id(trades, year):
    nums = []
    for t in trades["open"] + trades["closed"]:
        m = re.match(rf"MM-{year}-(\d+)", t.get("id", ""))
        if m:
            nums.append(int(m.group(1)))
    return f"MM-{year}-{(max(nums) + 1 if nums else 1):03d}"


def ingest_ideas(trades, raw_ideas, trade_type):
    added = []
    year = TODAY[:4]
    for idea in raw_ideas or []:
        # skip the explicit "no Nth idea" placeholder
        if not idea.get("entry") or float(idea.get("conviction", 0)) <= 0:
            continue
        tid = next_id(trades, year)
        min_hold = int(idea.get("min_hold_days", 30 if trade_type == "pre-position" else 0))
        if trade_type == "pre-position":
            min_hold = max(30, min_hold)
        entry = float(idea["entry"])
        t = {
            "id": tid,
            "opened": TODAY,
            "type": trade_type,
            "asset_class": idea.get("asset_class", ""),
            "trade": idea.get("trade", ""),
            "structure": idea.get("structure", "outright"),
            "entry": entry,
            "stop": idea.get("stop"),
            "target": idea.get("target"),
            "conviction": idea.get("conviction"),
            "conviction_breakdown": idea.get("conviction_breakdown", {}),
            "horizon": idea.get("horizon", ""),
            "min_hold_days": min_hold,
            "thesis": idea.get("thesis", ""),
            "current": entry,
            "current_pnl_pct": 0.0,
            "history": [
                {"date": TODAY, "level": entry, "pnl_pct": 0.0, "status": "open"}
            ],
        }
        trades["open"].append(t)
        added.append(tid)
    if added:
        log(f"added {trade_type} ideas: {', '.join(added)}")
    return added


# --------------------------------------------------------------------------
# Scoreboard
# --------------------------------------------------------------------------
def scoreboard(closed):
    graded = [t for t in closed if "pnl_pct" in t.get("exit", {})]
    n = len(graded)
    if n == 0:
        return {"count": 0}
    pnls = [t["exit"]["pnl_pct"] for t in graded]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    best = max(graded, key=lambda t: t["exit"]["pnl_pct"])
    worst = min(graded, key=lambda t: t["exit"]["pnl_pct"])
    return {
        "count": n,
        "hit_rate": 100.0 * len(wins) / n,
        "avg_win": sum(wins) / len(wins) if wins else 0.0,
        "avg_loss": sum(losses) / len(losses) if losses else 0.0,
        "sum_pnl": sum(pnls),
        "best": (best["id"], best["exit"]["pnl_pct"]),
        "worst": (worst["id"], worst["exit"]["pnl_pct"]),
    }


# --------------------------------------------------------------------------
# JSON helper (string-aware, nested-safe) — handy if a brief arrives as text
# --------------------------------------------------------------------------
def _balanced_objects(text):
    objs, depth, start = [], 0, None
    in_str = esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                objs.append(text[start:i + 1])
    return objs


def extract_json(text):
    """Largest top-level brace-balanced blob that parses (nested-safe)."""
    candidates = _balanced_objects(text)
    candidates.sort(key=len, reverse=True)
    for c in candidates:
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            continue
    return None


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------
def e(s):
    return html.escape(str(s)) if s is not None else ""


def pnl_span(p):
    if p is None:
        return '<span class="mute">—</span>'
    cls = "g" if p > 0 else ("r" if p < 0 else "mute")
    return f'<span class="{cls}">{p:+.2f}%</span>'


def dir_class(d):
    return {"up": "g", "down": "r", "flat": "mute", "unverified": "mute"}.get(d, "mute")


CSS = """
:root{--bg:#fff;--paper:#f7f7f5;--ink:#1a1a1a;--ink-soft:#6b6b6b;--ink-mute:#9a9a9a;--gold:#b8960c;--red:#c0392b;--green:#27864a;--line:#e5e5e3}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:Georgia,'Times New Roman',serif;font-size:18px;line-height:1.65;margin:0;padding:56px 18px 120px;-webkit-font-smoothing:antialiased}
.wrap{max-width:640px;margin:0 auto}
.cards{max-width:960px;margin:0 auto}
h1{font-size:30px;letter-spacing:-.5px;margin:0 0 4px}
.sub{color:var(--ink-mute);font-size:14px;margin:0 0 26px}
.g{color:var(--green)}.r{color:var(--red)}.mute{color:var(--ink-mute)}.gold{color:var(--gold)}
.banner{border-top:2px solid var(--gold);border-bottom:1px solid var(--line);color:var(--gold);font-size:21px;font-weight:bold;letter-spacing:.3px;padding:16px 0;margin:8px 0 6px}
.banner small{display:block;color:var(--ink-soft);font-weight:normal;font-size:14px;letter-spacing:0;margin-top:4px}
.sec{margin:40px auto;max-width:640px}
.sec h2{font-size:13px;letter-spacing:2px;text-transform:uppercase;color:var(--ink-mute);border-bottom:1px solid var(--line);padding-bottom:7px;margin:0 0 16px}
.sec p{margin:0 0 14px}
.theme{font-weight:bold;font-size:19px;border-left:3px solid var(--gold);padding-left:14px;margin:18px 0}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line)}
th{color:var(--ink-mute);font-weight:normal;font-size:12px;letter-spacing:1px;text-transform:uppercase}
td.num{font-variant-numeric:tabular-nums;text-align:right}
.dash{max-width:640px}
.cardgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:18px 20px;font-size:15px;line-height:1.5}
.card .t{font-weight:bold;font-size:16px;margin-bottom:8px}
.card .row{display:flex;justify-content:space-between;border-bottom:1px dotted var(--line);padding:3px 0}
.card .lbl{color:var(--ink-mute)}
.card .thesis{margin-top:10px;color:var(--ink-soft);font-size:14px}
.rubric{margin-top:10px;font-size:12.5px;color:var(--ink-mute);font-variant-numeric:tabular-nums}
.chip{display:inline-block;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--ink-mute);border:1px solid var(--line);border-radius:10px;padding:1px 8px}
.bar{height:7px;background:var(--line);border-radius:4px;overflow:hidden;min-width:70px}
.bar>span{display:block;height:100%;background:var(--gold)}
.chart{margin:22px 0}
.score{display:flex;flex-wrap:wrap;gap:14px;margin:14px 0}
.score div{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:10px 16px;font-size:14px;min-width:120px}
.score b{display:block;font-size:20px}
.cal li{margin:3px 0}
.regtl{list-style:none;padding:0;font-size:15px}
.regtl li{padding:6px 0;border-bottom:1px solid var(--line)}
.regtl .d{color:var(--ink-mute);font-size:13px}
.stale{font-size:12.5px;color:var(--ink-mute)}
.stale td,.stale th{padding:4px 8px}
.amm{margin:0 0 12px}
.amm .q{font-weight:bold}
.amm .a{color:var(--ink-soft)}
"""


def render_dashboard(rows):
    if not rows:
        return "<p class='mute'>dashboard unavailable</p>"
    cells = []
    for row in rows:
        lvl = row.get("level", "unverified")
        chg = row.get("chg", "")
        d = row.get("dir", "unverified")
        if d == "unverified" or lvl == "unverified":
            val = '<span class="mute">unverified</span>'
        else:
            val = f'{e(lvl)} <span class="{dir_class(d)}">{e(chg)}</span>'
        cells.append(
            f'<tr><td>{e(row.get("name",""))}</td>'
            f'<td class="num">{val}</td></tr>'
        )
    return (
        '<table class="dash"><thead><tr><th>Instrument</th>'
        '<th style="text-align:right">Level · 24h</th></tr></thead><tbody>'
        + "".join(cells) + "</tbody></table>"
    )


def render_trade_card(idea):
    if not idea.get("entry") or float(idea.get("conviction", 0)) <= 0:
        return (
            '<div class="card"><div class="t">'
            f'{e(idea.get("trade","no further idea today — forcing a trade is the trade"))}'
            '</div></div>'
        )
    cb = idea.get("conviction_breakdown", {}) or {}
    rubric = (
        f'gap {cb.get("gap",0)}/3 · catalyst {cb.get("catalyst",0)}/2 · '
        f'positioning {cb.get("positioning",0)}/2 · confirmation {cb.get("confirmation",0)}/2 · '
        f'stop {cb.get("stop_quality",0)}/1'
    )
    rows = [
        ("Asset", idea.get("asset_class", "")),
        ("Structure", idea.get("structure", "")),
        ("Entry", idea.get("entry")),
        ("Stop", idea.get("stop")),
        ("Target", idea.get("target")),
        ("Horizon", idea.get("horizon", "")),
    ]
    if idea.get("min_hold_days"):
        rows.append(("Min hold", f'{idea["min_hold_days"]}d'))
    row_html = "".join(
        f'<div class="row"><span class="lbl">{e(k)}</span><span>{e(v)}</span></div>'
        for k, v in rows
    )
    return (
        '<div class="card">'
        f'<div class="t">{e(idea.get("trade",""))}</div>'
        f'<div class="chip">conviction {e(idea.get("conviction"))}/10</div>'
        + row_html
        + f'<div class="thesis">{e(idea.get("thesis",""))}</div>'
        + f'<div class="rubric">{rubric}</div>'
        + "</div>"
    )


def render_live_book(trades):
    rows = []
    for t in trades["open"]:
        cur = t.get("current", t.get("entry"))
        pl = t.get("current_pnl_pct")
        prog = int(progress_to_target(t, cur) * 100) if cur is not None else 0
        rows.append(
            "<tr>"
            f'<td>{e(t.get("id",""))}</td>'
            f'<td>{e(t.get("trade",""))}</td>'
            f'<td><span class="chip">{e(t.get("type",""))}</span></td>'
            f'<td>{e(t.get("opened",""))}</td>'
            f'<td class="num">{e(t.get("entry"))}</td>'
            f'<td class="num">{e(cur)}</td>'
            f'<td class="num">{pnl_span(pl)}</td>'
            f'<td class="num">{e(t.get("conviction"))}</td>'
            f'<td><div class="bar"><span style="width:{prog}%"></span></div></td>'
            "</tr>"
        )
    open_tbl = (
        '<table><thead><tr><th>ID</th><th>Trade</th><th>Type</th><th>Opened</th>'
        '<th>Entry</th><th>Current</th><th>P&amp;L</th><th>Conv</th><th>→Target</th>'
        '</tr></thead><tbody>'
        + ("".join(rows) or '<tr><td colspan="9" class="mute">no open trades</td></tr>')
        + "</tbody></table>"
    )

    sb = scoreboard(trades["closed"])
    if sb["count"] == 0:
        score_html = '<p class="mute">no closed trades yet — scoreboard builds as the book matures</p>'
    else:
        score_html = (
            '<div class="score">'
            f'<div>Closed<b>{sb["count"]}</b></div>'
            f'<div>Hit rate<b>{sb["hit_rate"]:.0f}%</b></div>'
            f'<div>Avg winner<b class="g">{sb["avg_win"]:+.2f}%</b></div>'
            f'<div>Avg loser<b class="r">{sb["avg_loss"]:+.2f}%</b></div>'
            f'<div>Sum P&amp;L<b>{sb["sum_pnl"]:+.2f}%</b></div>'
            f'<div>Best<b class="g">{e(sb["best"][0])} {sb["best"][1]:+.1f}%</b></div>'
            f'<div>Worst<b class="r">{e(sb["worst"][0])} {sb["worst"][1]:+.1f}%</b></div>'
            "</div>"
        )

    closed_rows = []
    for t in trades["closed"]:
        ex = t.get("exit", {})
        closed_rows.append(
            "<tr>"
            f'<td>{e(t.get("id",""))}</td>'
            f'<td>{e(t.get("trade",""))}</td>'
            f'<td>{e(ex.get("result",""))}</td>'
            f'<td class="num">{e(t.get("entry"))}</td>'
            f'<td class="num">{e(ex.get("level"))}</td>'
            f'<td class="num">{pnl_span(ex.get("pnl_pct"))}</td>'
            f'<td class="num">{e(ex.get("days_held"))}d</td>'
            f'<td>{e(ex.get("date",""))}</td>'
            "</tr>"
        )
    closed_tbl = (
        '<table><thead><tr><th>ID</th><th>Trade</th><th>Result</th><th>Entry</th>'
        '<th>Exit</th><th>P&amp;L</th><th>Held</th><th>Closed</th></tr></thead><tbody>'
        + ("".join(closed_rows) or '<tr><td colspan="8" class="mute">no closed trades</td></tr>')
        + "</tbody></table>"
    )
    return open_tbl + score_html + "<h3 class='mute' style='font-size:13px;letter-spacing:1px'>CLOSED LEDGER</h3>" + closed_tbl


def render_catalyst(rows):
    if not rows:
        return "<p class='mute'>no genuine-asymmetry events on the 5-day horizon</p>"
    out = ['<table><thead><tr><th>Day</th><th>Date</th><th>Event</th>'
           '<th>Consensus</th><th>View</th><th>Asymmetry</th></tr></thead><tbody>']
    for r in rows:
        cls = dir_class(r.get("dir", "flat"))
        out.append(
            "<tr>"
            f'<td>{e(r.get("day",""))}</td>'
            f'<td>{e(r.get("date",""))}</td>'
            f'<td class="gold">{e(r.get("event",""))}</td>'
            f'<td>{e(r.get("consensus",""))}</td>'
            f'<td>{e(r.get("view",""))}</td>'
            f'<td class="{cls}">{e(r.get("asymmetry",""))}</td>'
            "</tr>"
        )
    out.append("</tbody></table>")
    return "".join(out)


def render_regime_timeline(regime_log):
    if not regime_log:
        return "<p class='mute'>no regime history yet</p>"
    items = []
    for r in reversed(regime_log):
        items.append(
            f'<li><span class="d">{e(r["date"])}</span> · '
            f'<span class="gold">{e(r["regime"])}</span>'
            + (f'<br><span class="mute">{e(r.get("note",""))}</span>' if r.get("note") else "")
            + "</li>"
        )
    return '<ul class="regtl">' + "".join(items) + "</ul>"


def render_staleness(rows):
    if not rows:
        return "<p class='mute'>no data points logged</p>"
    out = ['<table class="stale"><thead><tr><th>Datum</th><th>Source</th>'
           '<th>As of</th><th>Status</th></tr></thead><tbody>']
    for r in rows:
        stale = r.get("stale")
        status = '<span class="r">STALE &gt;6h</span>' if stale else '<span class="g">fresh</span>'
        out.append(
            "<tr>"
            f'<td>{e(r.get("datum",""))}</td>'
            f'<td>{e(r.get("source",""))}</td>'
            f'<td>{e(r.get("asof",""))}</td>'
            f'<td>{status}</td>'
            "</tr>"
        )
    out.append("</tbody></table>")
    return "".join(out)


def render_client_ammo(rows):
    if not rows:
        return ""
    out = []
    for r in rows:
        out.append(
            f'<div class="amm"><div class="q">{e(r.get("q",""))}</div>'
            f'<div class="a">{e(r.get("a",""))}</div></div>'
        )
    return "".join(out)


def sec(num, title, body, wide=False):
    cls = "sec cards" if wide else "sec"
    style = ' style="max-width:960px"' if wide else ""
    head = f'<h2>{num} · {title}</h2>' if num is not None else f'<h2>{title}</h2>'
    return f'<section class="{cls}"{style}>{head}{body}</section>'


def build_html(brief, trades, regime_log):
    d = brief
    reactive = [render_trade_card(i) for i in d.get("new_ideas", [])]
    prepos = [render_trade_card(i) for i in d.get("pre_position_ideas", [])]

    eq_svg = charts.equity_curve(trades["closed"])
    cal_svg = charts.calibration(trades["closed"])
    vix_svg = charts.vix_term_structure(d.get("vix_term", []))
    yc_svg = charts.yield_curve(d.get("yield_curve_pts", []))

    parts = []
    parts.append('<div class="wrap">')
    parts.append('<h1>Market Map</h1>')
    parts.append(f'<p class="sub">Pre-market intelligence brief · {e(TODAY)} · generated {datetime.now():%H:%M} local · self-graded book</p>')

    # REGIME BANNER
    parts.append(
        f'<div class="banner">{e(d.get("regime","—"))}'
        + (f'<small>{e(d.get("regime_note",""))}</small>' if d.get("regime_note") else "")
        + "</div>"
    )
    parts.append("</div>")  # close wrap; sections manage their own width

    # YESTERDAY GRADED
    parts.append(sec(None, "Yesterday, graded", d.get("yesterday_graded", "")))

    # 0 THE OPEN
    open_body = render_dashboard(d.get("dashboard", []))
    if d.get("dominant_theme"):
        open_body += f'<p class="theme">{e(d["dominant_theme"])}</p>'
    parts.append(sec("0", "The Open", open_body))

    parts.append(sec("1", "Today's One Chart That Matters", d.get("one_chart", "")))
    parts.append(sec("2", "The Wrap", d.get("wrap", "")))
    parts.append(sec("3", "Correlation Regime", d.get("correlation_regime", "")))
    parts.append(sec("4", "Vol &amp; Skew", d.get("vol_skew", "")))
    parts.append(sec("5", "Sector &amp; RV", d.get("sector_rv", "")))
    parts.append(sec("6", "Positioning &amp; Flows", d.get("positioning", "")))
    parts.append(sec("7", "Funding &amp; Plumbing", d.get("funding", "")))
    parts.append(sec("8", "What the Tape Is Missing", d.get("tape_missing", "")))
    parts.append(sec("9", "The Consensus: Bid/Offer", d.get("consensus", "")))

    # 10 NEW IDEAS
    parts.append(sec("10", "New Trade Ideas (reactive)",
                     '<div class="cardgrid">' + "".join(reactive) + "</div>", wide=True))

    # 11 EVENT RADAR + PRE-POSITIONING
    ev_body = d.get("event_radar_note", "")
    ev_body += '<div class="cardgrid">' + "".join(prepos) + "</div>"
    parts.append(sec("11", "Event Radar + Pre-positioning", ev_body, wide=True))

    # 12 LIVE BOOK
    parts.append(sec("12", "Live Book", render_live_book(trades), wide=True))

    # 13 CHARTS
    charts_body = (
        f'<div class="chart">{eq_svg}</div>'
        f'<div class="chart">{cal_svg}</div>'
        f'<div class="chart">{vix_svg}</div>'
        f'<div class="chart">{yc_svg}</div>'
    )
    parts.append(sec("13", "Charts", charts_body, wide=True))

    # 14 CATALYST CALENDAR
    parts.append(sec("14", "Catalyst Calendar (5 trading days)",
                     render_catalyst(d.get("catalyst_calendar", [])), wide=True))

    # 15 WHAT CHANGES MY MIND
    parts.append(sec("15", "What Changes My Mind", d.get("what_changes_mind", "")))

    # 16 CLIENT-CALL AMMO
    parts.append(sec("16", "Client-Call Ammo", render_client_ammo(d.get("client_ammo", []))))

    # 17 REGIME TIMELINE
    parts.append(sec("17", "Regime Timeline", render_regime_timeline(regime_log)))

    # 18 STALENESS CHECK
    parts.append(sec("18", "Staleness Check", render_staleness(d.get("staleness", []))))

    body = "".join(parts)
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>Market Map · {e(TODAY)}</title><style>{CSS}</style></head>"
        f"<body>{body}</body></html>"
    )
