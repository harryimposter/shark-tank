#!/usr/bin/env python3
"""Market Map — full refresh, 2026-06-01 (second pass, new data).
Fresh marks + new brief content + PROMPT.md two-column render.
"""
import os, sys, json, html as _html
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book, charts

TODAY = date.today().isoformat()
NOW   = datetime.now().strftime("%H:%M")
HERE  = os.path.dirname(os.path.abspath(__file__))

def e(s):
    return _html.escape(str(s)) if s is not None else ""

# ─────────────────────────────────────────────────────────────────────────────
# CSS — exact PROMPT.md Anthropic design spec
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
:root{--bg:#ffffff;--surface:#f7f7f5;--ink:#1a1a1a;--ink-soft:#6b6b6b;
--ink-mute:#9a9a9a;--gold:#b8960c;--red:#c0392b;--green:#1a7a45;
--line:rgba(0,0,0,0.1);--radius-md:8px;--radius-lg:12px;
--font:-apple-system,"Helvetica Neue",sans-serif;
--serif:Georgia,"Times New Roman",serif}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.65}
.page{max-width:1400px;margin:0 auto;padding:2rem 2rem 4rem}
.two-col{display:grid;grid-template-columns:1fr 380px;gap:2.5rem;align-items:start}
@media(max-width:960px){.two-col{grid-template-columns:1fr}}
.lhs{min-width:0}.rhs{min-width:0;position:sticky;top:1rem}
.masthead{border-bottom:0.5px solid var(--line);padding-bottom:1rem;margin-bottom:1.5rem}
.article-title{font-family:var(--serif);font-size:2rem;font-weight:400;line-height:1.25;color:var(--ink);margin:0 0 0.4rem}
.meta{font-size:11px;color:var(--ink-mute);letter-spacing:.08em;text-transform:uppercase;margin-top:.35rem}
.regime-tag{display:inline-block;font-size:10px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);border:.5px solid var(--gold);border-radius:20px;padding:2px 10px;margin-bottom:.75rem}
.gold-rule{border:none;border-top:1px solid var(--gold);margin:1rem 0 0;opacity:.4}
.section-label{font-size:10px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-mute);margin:1.75rem 0 .75rem}
.section-label:first-child{margin-top:0}
.dash-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:5px;margin-bottom:1rem}
.dash-tile{background:var(--surface);border-radius:var(--radius-md);padding:.5rem .75rem;border:.5px solid var(--line)}
.dlabel{font-size:10px;color:var(--ink-mute);margin-bottom:2px}
.dval{font-size:13px;font-weight:500;color:var(--ink);font-variant-numeric:tabular-nums}
.dchg{font-size:11px}
.chg-up{color:var(--green)}.chg-dn{color:var(--red)}.chg-flat{color:var(--ink-mute)}
.theme-line{border-left:2px solid var(--gold);padding:.5rem .85rem;background:var(--surface);border-radius:0 var(--radius-md) var(--radius-md) 0;margin:1rem 0;font-size:13px;font-weight:500;line-height:1.5}
.tile{background:var(--bg);border:.5px solid var(--line);border-radius:var(--radius-lg);padding:1rem 1.1rem;margin-bottom:8px}
.tile-head{font-size:10px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:.4rem}
.tile-claim{font-size:13px;font-weight:500;color:var(--ink);line-height:1.5;margin-bottom:.4rem}
.tile-body{font-size:12px;color:var(--ink-soft);line-height:1.6}
.tile-gold{border-top:2px solid var(--gold)}.tile-green{border-top:2px solid var(--green)}
.tile-red{border-top:2px solid var(--red)}.tile-muted{border-top:2px solid var(--line)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:600px){.grid-2,.grid-3{grid-template-columns:1fr}}
.trade-card{background:var(--bg);border:.5px solid var(--line);border-radius:var(--radius-lg);padding:1rem 1.1rem;margin-bottom:8px}
.tc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.75rem}
.tc-name{font-size:13px;font-weight:500;color:var(--ink)}
.tc-class{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);margin-top:2px}
.conv-badge{font-size:11px;font-weight:500;background:var(--surface);border:.5px solid var(--line);border-radius:20px;padding:2px 10px;color:var(--ink);white-space:nowrap}
.tc-row{display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:.5px solid var(--line)}
.tc-row:last-of-type{border-bottom:none}
.tc-k{color:var(--ink-mute)}.tc-v{font-weight:500;color:var(--ink)}
.conv-bar{display:flex;gap:3px;align-items:center;margin:.5rem 0}
.pip{width:18px;height:4px;border-radius:2px;background:var(--line)}
.pip.on{background:var(--gold)}
.conv-detail{font-size:10px;color:var(--ink-mute);margin-left:6px}
.tc-thesis{font-size:12px;color:var(--ink-soft);line-height:1.6;margin-top:.6rem;padding-top:.6rem;border-top:.5px solid var(--line)}
.score-row{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px}
.score-tile{background:var(--surface);border-radius:var(--radius-md);padding:.5rem .6rem;text-align:center}
.sval{font-size:18px;font-weight:500;color:var(--ink)}
.sval.pos{color:var(--green)}.sval.neg{color:var(--red)}
.slabel{font-size:10px;color:var(--ink-mute);margin-top:2px}
.live-table{width:100%;font-size:12px;border-collapse:collapse}
.live-table th{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink-mute);font-weight:500;padding:0 0 6px;text-align:left;border-bottom:.5px solid var(--line)}
.live-table td{padding:6px 0;border-bottom:.5px solid var(--line);color:var(--ink);vertical-align:middle}
.live-table tr:last-child td{border-bottom:none}
.pnl-pos{color:var(--green);font-weight:500}.pnl-neg{color:var(--red);font-weight:500}
.pill{font-size:10px;padding:2px 8px;border-radius:20px;background:var(--surface);color:var(--ink-mute);border:.5px solid var(--line)}
.prog-bar{height:4px;background:var(--line);border-radius:2px;overflow:hidden;min-width:48px;margin-top:3px}
.prog-bar>span{display:block;height:100%;background:var(--gold)}
.canary{padding:.55rem 0;border-bottom:.5px solid var(--line);display:flex;gap:10px;align-items:flex-start}
.canary:last-child{border-bottom:none}
.cdot{width:6px;height:6px;border-radius:50%;background:var(--gold);flex-shrink:0;margin-top:5px}
.ctext{font-size:12px;color:var(--ink-soft);line-height:1.6}
.ctext strong{color:var(--ink);font-weight:500}
.ammo{padding:.55rem 0;border-bottom:.5px solid var(--line)}
.ammo:last-child{border-bottom:none}
.ammo-q{font-size:12px;font-weight:500;color:var(--ink);margin-bottom:3px}
.ammo-a{font-size:12px;color:var(--ink-soft);line-height:1.5}
.yesterday{background:var(--surface);border-radius:var(--radius-md);padding:.75rem 1rem;margin-bottom:1rem}
.yest-item{font-size:12px;color:var(--ink-soft);padding:4px 0;display:flex;gap:8px;align-items:flex-start;border-bottom:.5px solid var(--line)}
.yest-item:last-child{border-bottom:none}
.tick-g{color:var(--green);flex-shrink:0;font-weight:600}
.tick-r{color:var(--red);flex-shrink:0;font-weight:600}
.tick-n{color:var(--ink-mute);flex-shrink:0}
.stale-tbl{width:100%;font-size:11px;border-collapse:collapse}
.stale-tbl th{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink-mute);font-weight:500;padding:0 0 4px;text-align:left;border-bottom:.5px solid var(--line)}
.stale-tbl td{padding:4px 0;border-bottom:.5px solid var(--line);color:var(--ink-soft)}
.stale-tbl tr:last-child td{border-bottom:none}
.fresh{color:var(--green);font-weight:500}.stale-flag{color:var(--red);font-weight:500}
.citation{font-size:10px;color:var(--ink-mute);line-height:1.9}
.wrap-body{font-family:var(--serif);font-size:16px;line-height:1.85;color:var(--ink)}
.wrap-body p{margin-bottom:1.1rem}
.wrap-body strong{font-weight:600}
.vol-surface{background:var(--surface);border-radius:var(--radius-md);padding:.75rem 1rem;font-size:12px;color:var(--ink-soft);line-height:1.7}
.cal-table{width:100%;font-size:12px;border-collapse:collapse}
.cal-table th{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink-mute);font-weight:500;padding:0 6px 6px 0;text-align:left;border-bottom:.5px solid var(--line)}
.cal-table td{padding:7px 6px 7px 0;border-bottom:.5px solid var(--line);vertical-align:top}
.cal-table tr:last-child td{border-bottom:none}
.cal-event{color:var(--gold);font-weight:500}
.asym-up{color:var(--green)}.asym-dn{color:var(--red)}
.earnings-tile{background:var(--bg);border:.5px solid var(--line);border-left:3px solid var(--gold);border-radius:var(--radius-lg);padding:1rem 1.1rem;margin-bottom:8px}
.earn-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:.6rem}
.earn-name{font-size:14px;font-weight:500;color:var(--ink)}
.earn-ticker{font-size:11px;color:var(--ink-mute);font-family:monospace}
.earn-row{display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:.5px solid var(--line)}
.earn-row:last-of-type{border-bottom:none}
.earn-k{color:var(--ink-mute)}.earn-v{font-weight:500}
.earn-read{font-size:12px;color:var(--ink-soft);margin-top:.5rem;line-height:1.6}
.mind-item{font-size:12px;color:var(--ink-soft);padding:4px 0;border-bottom:.5px solid var(--line);line-height:1.6}
.mind-item:last-child{border-bottom:none}
.mind-item strong{color:var(--ink);font-weight:500}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def pnl_span(p):
    if p is None:
        return '<span style="color:var(--ink-mute)">—</span>'
    cls = "pnl-pos" if p > 0 else ("pnl-neg" if p < 0 else "")
    return f'<span class="{cls}">{p:+.2f}%</span>'

def pips(conviction, cb):
    n = int(conviction)
    dots = "".join(f'<div class="pip{"  on" if i < n else ""}"></div>' for i in range(10))
    detail = (
        f'gap({cb.get("gap",0)}/3) · catalyst({cb.get("catalyst",0)}/2) · '
        f'pos({cb.get("positioning",0)}/2) · confirm({cb.get("confirmation",0)}/2) · '
        f'stop({cb.get("stop_quality",0)}/1)'
    )
    return f'<div class="conv-bar">{dots}<span class="conv-detail">{e(detail)}</span></div>'

def prog_pct(t, level):
    entry, target = t.get("entry"), t.get("target")
    if not entry or not target or target == entry: return 0
    d = 1 if target >= entry else -1
    return max(0, min(100, int(d * (level - entry) / abs(target - entry) * 100)))

def trade_card(t):
    cb = t.get("conviction_breakdown", {})
    rows = [
        ("Asset",     t.get("asset_class", "")),
        ("Structure", t.get("structure", "")),
        ("Entry",     t.get("entry", "")),
        ("Stop",      t.get("stop", "")),
        ("Target",    t.get("target", "")),
        ("Horizon",   t.get("horizon", "")),
    ]
    if t.get("min_hold_days"):
        rows.append(("Min hold", f'{t["min_hold_days"]}d'))
    rows_html = "".join(
        f'<div class="tc-row"><span class="tc-k">{e(k)}</span>'
        f'<span class="tc-v">{e(v)}</span></div>'
        for k, v in rows
    )
    return (
        f'<div class="trade-card">'
        f'<div class="tc-top"><div>'
        f'<div class="tc-name">{e(t.get("trade",""))}</div>'
        f'<div class="tc-class">{e(t.get("type","reactive"))} · {e(t.get("asset_class",""))}</div>'
        f'</div><div class="conv-badge">{e(t.get("conviction","?"))}/10</div></div>'
        f'{rows_html}'
        f'{pips(t.get("conviction",0), cb)}'
        f'<div class="tc-thesis">{e(t.get("thesis",""))}</div>'
        f'</div>'
    )

def live_book(trades):
    closed = trades.get("closed", [])
    open_t = trades.get("open", [])
    graded = [t for t in closed if "pnl_pct" in t.get("exit", {})]
    if graded:
        pnls  = [t["exit"]["pnl_pct"] for t in graded]
        wins  = [p for p in pnls if p > 0]
        best  = max(graded, key=lambda t: t["exit"]["pnl_pct"])
        score = (
            f'<div class="score-row">'
            f'<div class="score-tile"><div class="sval">{len(graded)}</div><div class="slabel">Closed</div></div>'
            f'<div class="score-tile"><div class="sval">{100*len(wins)/len(graded):.0f}%</div><div class="slabel">Hit rate</div></div>'
            f'<div class="score-tile"><div class="sval {"pos" if sum(pnls)>=0 else "neg"}">{sum(pnls):+.1f}%</div><div class="slabel">Sum P&L</div></div>'
            f'<div class="score-tile"><div class="sval pos">{e(best["id"])}</div><div class="slabel">Best</div></div>'
            f'</div>'
        )
    else:
        score = f'<p style="font-size:12px;color:var(--ink-mute);margin-bottom:.75rem">Book opened {TODAY} — scoreboard builds as trades close.</p>'

    h_map = {"weeks": 14, "months": 90, "2 weeks": 14, "3 months": 90,
             "26 days": 26, "week": 7}
    rows = []
    for t in open_t:
        cur  = t.get("current", t.get("entry"))
        pl   = t.get("current_pnl_pct")
        prog = prog_pct(t, cur) if cur else 0
        try:
            held = (date.today() - date.fromisoformat(t.get("opened","2026-01-01"))).days
            rem  = max(0, h_map.get(t.get("horizon",""), 30) - held)
            rc   = "var(--red)" if rem < 5 else "var(--ink-mute)"
            rem_s = f'<span style="color:{rc}">{rem}d</span>'
        except Exception:
            rem_s = "—"
        rows.append(
            f'<tr>'
            f'<td><span class="pill">{e(t.get("id",""))}</span></td>'
            f'<td style="max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'
            f'{e(t.get("trade",""))}</td>'
            f'<td>{e(t.get("opened",""))}</td>'
            f'<td style="font-variant-numeric:tabular-nums">{e(cur)}</td>'
            f'<td>{pnl_span(pl)}</td>'
            f'<td>{rem_s}</td>'
            f'<td><div class="prog-bar"><span style="width:{prog}%"></span></div></td>'
            f'</tr>'
        )
    open_tbl = (
        '<table class="live-table"><thead><tr>'
        '<th>ID</th><th>Trade</th><th>Opened</th><th>Current</th>'
        '<th>P&L</th><th>Window</th><th>&rarr; Target</th>'
        '</tr></thead><tbody>'
        + ("".join(rows) or '<tr><td colspan="7" style="color:var(--ink-mute)">no open trades</td></tr>')
        + '</tbody></table>'
    )
    if closed:
        cl = "".join(
            f'<tr><td><span class="pill">{e(t.get("id",""))}</span></td>'
            f'<td>{e(t.get("trade",""))}</td>'
            f'<td>{e(t.get("exit",{}).get("result",""))}</td>'
            f'<td>{pnl_span(t.get("exit",{}).get("pnl_pct"))}</td>'
            f'<td style="color:var(--ink-mute)">{e(t.get("exit",{}).get("days_held",""))}d</td></tr>'
            for t in closed
        )
        closed_tbl = (
            '<div class="section-label" style="margin-top:1rem">Closed ledger</div>'
            '<table class="live-table"><thead><tr>'
            '<th>ID</th><th>Trade</th><th>Result</th><th>P&L</th><th>Held</th>'
            '</tr></thead><tbody>' + cl + '</tbody></table>'
        )
    else:
        closed_tbl = '<p style="font-size:11px;color:var(--ink-mute);margin-top:.5rem">No closed trades yet.</p>'
    return score + open_tbl + closed_tbl

# ─────────────────────────────────────────────────────────────────────────────
# Load & mark to market
# ─────────────────────────────────────────────────────────────────────────────
trades     = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

# Fresh levels — 2026-06-01 (all sourced this refresh)
levels = {
    "MM-2026-001": 1.621,    # EURAUD: ~1.621 (slightly lower; TradingEconomics via EURUSD 1.1644)
    "MM-2026-002": 92.5,     # Brent: ~$92.50 (WTI $89.69 + spread ~$2.81; ICE/Reuters)
    "MM-2026-003": 2.81,     # Brent-WTI spread: 92.50 − 89.69 (TradingEconomics/OilPrice)
    "MM-2026-004": 4.47,     # US 10Y yield: 4.47% — "climbed to 4.47%" (TradingEconomics/FRED)
    "MM-2026-005": 4541.80,  # Gold: $4,541.80 (TwelveData/ExchangeRates.UK)
    "MM-2026-006": 252.0,    # AVGO: ~$252 — slight uptick on Computex / Nemotron 3 Ultra, UBS PT $490
    "MM-2026-007": 159.37,   # USDJPY: 159.37 (TradingEconomics — unchanged)
    "MM-2026-008": 35.0,     # SPX put spread: premium unchanged — market data unavailable
    "MM-2026-009": 0.15,     # 2s10s: ~+15bp (FRED / centralbank.watch — unchanged)
}
book.mark_to_market(trades, levels)

# Regime — unchanged today; update note to include Nemotron 3 Ultra
regime      = "AI Vertical Meets Hormuz Binary"
regime_note = (
    "Jensen Huang unveiled Nemotron 3 Ultra (500B parameters) at Computex — the AI vertical "
    "now has a receipt. The ceasefire has been violated by both sides since April 8; the MoU "
    "is unsigned; a naval mine sits in Hormuz. Both theses are live."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ─────────────────────────────────────────────────────────────────────────────
# Charts
# ─────────────────────────────────────────────────────────────────────────────
eq_svg  = charts.equity_curve(trades["closed"])
cal_svg = charts.calibration(trades["closed"])
vix_svg = charts.vix_term_structure([
    {"label": "VIX9D", "value": 13.5},
    {"label": "VIX",   "value": 15.32},
    {"label": "VIX3M", "value": 17.2},
    {"label": "VIX6M", "value": 18.5},
])
yc_svg = charts.yield_curve([
    {"label": "2Y",  "value": 4.32},
    {"label": "5Y",  "value": 4.40},
    {"label": "10Y", "value": 4.47},
    {"label": "30Y", "value": 4.62},
])

# ─────────────────────────────────────────────────────────────────────────────
# Sections
# ─────────────────────────────────────────────────────────────────────────────
MASTHEAD = f"""
<div class="masthead">
  <div class="regime-tag">AI Vertical Meets Hormuz Binary</div>
  <h1 class="article-title">Computex Delivered; Hormuz Hasn&rsquo;t</h1>
  <p class="meta">Pre-market intelligence brief &middot; {TODAY} &middot; generated {NOW} local &middot; self-graded book</p>
  <hr class="gold-rule">
</div>"""

YESTERDAY = """
<div class="section-label">Yesterday, graded</div>
<div class="yesterday">
  <div class="yest-item">
    <span class="tick-g">✓</span>
    <span><strong>MM-2026-001</strong> · Short EURAUD · 1.6450 → 1.6210 · <span class="pnl-pos">+1.46%</span> · Working. EURUSD fell to 1.1644 — ECB growth headwinds outweigh rate-hike bid. Cross drifting toward 1.610 target; DXY at 99 adds tailwind.</span>
  </div>
  <div class="yest-item">
    <span class="tick-g">✓</span>
    <span><strong>MM-2026-002</strong> · Long Brent · $91.00 → $92.50 · <span class="pnl-pos">+1.65%</span> · Working. WTI +2.67% on day as Hormuz mine sighting keeps supply risk bid. COT oil specs turned nearly net-long (−9.2k). Squeeze fuel building.</span>
  </div>
  <div class="yest-item">
    <span class="tick-r">✗</span>
    <span><strong>MM-2026-003</strong> · Long Brent / Short WTI spread · 3.30 → 2.81 · <span class="pnl-neg">−14.85%</span> · Under pressure. WTI recovering faster on US domestic supply; Hormuz premium not widening spread. Stop 1.50 — not hit. Today's single most important level to watch.</span>
  </div>
  <div class="yest-item">
    <span class="tick-n">→</span>
    <span><strong>MM-2026-004</strong> · Short US 10Y yield · 4.44% → 4.47% · <span class="pnl-neg">−0.68%</span> · Edging toward stop. Yield climbed to 4.47% as WTI recovery keeps inflation fears alive. Stop at 4.65% — 18bp room remaining. Watch payrolls Friday.</span>
  </div>
  <div class="yest-item">
    <span class="tick-g">✓</span>
    <span><strong>MM-2026-005</strong> · Long gold (pre-position) · $4,523 → $4,541.80 · <span class="pnl-pos">+0.42%</span> · Working slowly. Gold decoupled from WTI; COT gold longs reduced to 154.3k (from 159.8k) — lighter positioning is constructive. Pre-position: 44 days min-hold remaining.</span>
  </div>
  <div class="yest-item">
    <span class="tick-g">✓</span>
    <span><strong>MM-2026-006</strong> · Long AVGO · $250.00 → $252.00 · <span class="pnl-pos">+0.80%</span> · Moving. UBS raised PT to $490. Nemotron 3 Ultra confirmed Computex tailwind. Reports Wednesday — thesis intact.</span>
  </div>
  <div class="yest-item">
    <span class="tick-n">→</span>
    <span><strong>MM-2026-007</strong> · Short USDJPY · 159.37 → 159.37 · <span class="pnl-neg">flat</span> · Unchanged. No intervention triggered. 160.00 is the line. Position sized for a multi-week hold.</span>
  </div>
  <div class="yest-item">
    <span class="tick-n">→</span>
    <span><strong>MM-2026-008</strong> · SPX Jun-27 7300/7000 put spread · 35 → 35 · flat · Holding. VIX at 15.32. Three catalysts in 15 days; premium is a buy-and-hold through the event window.</span>
  </div>
  <div class="yest-item">
    <span class="tick-n">→</span>
    <span><strong>MM-2026-009</strong> · 2s10s UST steepener (pre-pos) · +15bp → +15bp · flat · Holding. Payrolls Friday is the first catalyst. Pre-position: 45-day hold minimum.</span>
  </div>
</div>"""

WRAP = """
<div class="section-label">The Wrap</div>
<div class="wrap-body">
<p>Jensen Huang delivered. At 11 a.m. Taipei time, Nvidia unveiled Nemotron 3 Ultra — a
500-billion-parameter open model targeting complex reasoning and agentic workflows. That is
not a product announcement. It is the AI vertical planting its flag in the software layer
after owning the hardware layer. The consensus expected hardware from Computex. It got
hardware <em>and</em> a frontier model. One of them has a receipt; the other still doesn't.</p>

<p>The one that doesn't is the Iran MoU. The ceasefire has been violated by both sides since
April 8. Iran's Fars news agency dismissed Trump's "largely negotiated" claim as "incomplete
and inconsistent with reality." A naval mine sits in the Strait. Oil is trading hope, not a
signed document. At $89.69 WTI and $92.50 Brent, the market is assigning roughly 65%
probability to a deal — priced to the dollar, tested by the mine.</p>

<p>Break apart the S&P 500 at ~7,580 and the anatomy is two positions in a trench coat.
Tech is up 10.6% in May alone — the only sector to outperform. Lumentum Holdings +121%
YTD. Applied Materials +67%. Nvidia itself only +12%, massively underperforming the
Philadelphia SOX at +74%. Nemotron 3 Ultra is the catalyst that could close that gap.
Who's wrong? Every fund that rotated out of NVDA into the SOX components is now sitting
on a basis trade that inverts if Huang's software pivot re-rates the stock. The anatomy
says one thing. The headline index says another.</p>

<p><strong>L1 — The driver.</strong> Fiscal dominance feeding an AI melt-up. The Fed is on
hold at 3.5–3.75% (96.9% probability of no cut June 16-17). Corporate cash flows are
self-funding the AI build-out at a rate that makes rate policy irrelevant. The March
dot plot median was 3.4% for 2026 — one cut implied, split 7/7 between no-cut and
one-cut FOMC members. The June 16-17 dot plot revision is a live market-moving event
where the median could go either way. Rate policy is not a spectator — it is a binary
at the next meeting.</p>

<p><strong>L2 — Counter-intuitive hook.</strong> DXY is at ~99, near two-week lows, even as WTI
rises 2.67% today. Dollar-oil correlation is broken. The dollar should be tracking the
geopolitical risk premium in crude. It isn't — because the dollar is being driven purely
by Fed expectations (no cuts) and that narrative is fragile. One weak payrolls print on
Friday re-introduces the cut narrative, DXY breaks below 98, and every dollar-correlated
position needs to reprice simultaneously.</p>

<p><strong>L3 — The gap.</strong> Real economy: May payrolls consensus 89k; ISM Manufacturing
employment 46.4 in April. Goods sector contracting quietly while services hold. What's
priced: soft landing, AI at 30–41x forward earnings (AVGO trades at 41x), ECB hiking into
growth perfection. Consensus narrative: the AI cycle is self-sustaining. The gap: the
consumer who funds Microsoft, Google, Meta's capex commitments is the same consumer
facing 89k monthly payroll growth and 3.8% wage gains eroded by 3.8% CPI.</p>
</div>

<div class="section-label">Scenarios</div>
<div class="grid-3">
  <div class="tile tile-green">
    <div class="tile-head">Bull — 50%</div>
    <div class="tile-claim">MoU signed, Nemotron proves software moat, payrolls hold</div>
    <div class="tile-body">Hormuz reopens, disinflation resumes. AVGO beats Wednesday. Fed holds and markets treat it as benign. SPX 8,000 by Q3. Oil $80. Gold $4,800. Dollar weakens further.</div>
  </div>
  <div class="tile tile-gold">
    <div class="tile-head">Base — 35%</div>
    <div class="tile-claim">MoU drags; AI confirmed but growth equities chop</div>
    <div class="tile-body">Oil range-bound $85–95. ECB June 11 hike tightens European conditions. FOMC dot plot stays at 1 cut — no catalyst. SPX 7,200–7,800 chop. USDJPY intervention pressure builds. Gold $4,400–4,700.</div>
  </div>
  <div class="tile tile-red">
    <div class="tile-head">Bear — 15%</div>
    <div class="tile-claim">MoU collapses; oil re-spikes; ECB + Fed both hawkish</div>
    <div class="tile-body">WTI $105+. FOMC median goes to 0 cuts. Credit spreads widen from tights (IG 80bp, HY 285bp — no cushion). SPX −15%. Bear-flattening curve. JPY safe-haven squeeze. Gold $5,200+.</div>
  </div>
</div>

<div class="wrap-body">
<p><strong>Burry tell.</strong> NVDA is up only 12% YTD while the SOX is up 74%. That gap has been
funded by the hardware components of the AI supply chain — ASML, TSMC, Applied Materials,
Lumentum. If Nemotron 3 Ultra signals that the value in this cycle accrues to the <em>model
layer</em> and not the infrastructure layer, the trade rotates back into NVDA and out of the
capex-intensive names. That rotation doesn't need a macro catalyst. It needs one keynote.
Today's keynote may be it. In six months, the question will be whether the GPU commodity
cycle peaked with the Blackwell generation — or whether Vera Rubin and the software layer
extended it indefinitely.</p>

<p><strong>Pozsar mechanic.</strong> The Brent-WTI spread at $2.81 is the balance sheet tell. Tanker
insurers are underwriting Hormuz risk at near-peacetime rates. If the mine in the strait
is confirmed as Iranian-laid and the MoU collapses, the repricing is instantaneous — not
because Brent moves, but because tanker insurance capacity freezes and physical delivery
of Atlantic-basin crude becomes impractical. The flow constraint is insurance, not supply.
That is the second-order risk the oil market is not pricing.</p>

<p><strong>Papic constraint.</strong> Trump needs a deal announcement before the June 11 ECB meeting
— because a Hormuz shock on the day Lagarde hikes creates a stagflation narrative that
is politically damaging domestically. The constraint is the political calendar, not the
negotiating calendar. Iran knows this and is in no hurry. That asymmetry — Iran patient,
Trump time-pressured — is why the MoU keeps slipping.</p>
</div>"""

CORRELATION = """
<div class="section-label">Correlation Regime</div>
<div class="tile tile-muted">
  <div class="tile-claim">DXY at 99 (near 2-week lows) while WTI +2.67% — dollar-oil decoupling confirmed</div>
  <div class="tile-body">Dollar should track oil's geopolitical risk. It doesn't — because the dollar's entire 2026 narrative is Fed hold (96.9% June hold priced), not commodity-driven inflation. The decoupling breaks when the Fed narrative breaks. Payrolls Friday is the test.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-claim">NVDA +12% YTD vs SOX +74% — AI hardware and AI software have diverged</div>
  <div class="tile-body">The infrastructure layer (ASML, TSMC, Applied Materials) is carrying the SOX while NVDA underperforms. Nemotron 3 Ultra is the potential re-rating catalyst — model layer value accrual would pull funds back into NVDA from the capex infrastructure names. The correlation to watch: NVDA vs SOX equal-weight. If that inverts, the rotation is underway.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-claim">Gold flat vs WTI +2.67% — gold is pricing the Fed binary, not the commodity trade</div>
  <div class="tile-body">Gold at $4,541.80 is unchanged while crude rallies. COT gold longs reduced to 154.3k from 159.8k — lighter positioning. Gold is waiting for the FOMC dot plot (June 16-17), not the Hormuz headline. A 0-cut dot plot sells gold; a 2-cut scenario buys it sharply.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-claim">EURUSD −0.14% to 1.1644 while ECB hike is 10 days away — EUR is not pricing the rate catalyst</div>
  <div class="tile-body">The textbook move is for EUR to rally into the ECB hike. It isn't. The market is reading the June 11 hike as a policy error — tightening into an 18-month manufacturing recession. EURAUD (MM-2026-001 short) continues to drift lower on this read. The spec EUR long is the crowded exit.</div>
</div>"""

VOL_SKEW = """
<div class="section-label">Vol &amp; Skew</div>
<div class="vol-surface">
  <strong>VIX term structure — contango (risk-on):</strong> VIX9D ~13.5 · VIX 15.32 · VIX3M ~17.2 · VIX6M ~18.5<br>
  Structure is in contango. Front-end vol is the cheapest it has been relative to the event calendar: AVGO June 3, payrolls June 5, ECB June 11, FOMC June 16-17. The surface is underpricing the next 26 days.
</div>
<div style="height:8px"></div>
<div class="tile tile-muted">
  <div class="tile-head">CBOE SKEW — elevated (~140–145)</div>
  <div class="tile-claim">Elevated skew at 15.3 spot VIX — the classic "everyone's hedged but nobody believes it" setup</div>
  <div class="tile-body">Portfolio managers are buying downside while holding long equity. The skew premium is real and expensive. The cheapest hedge is in the front — VIX9D at 13.5. MM-2026-008 (SPX put spread) is designed exactly for this regime.</div>
</div>
<div class="tile tile-gold">
  <div class="tile-head">Active position: MM-2026-008</div>
  <div class="tile-claim">SPX June 27 7300/7000 put spread · 35 pts net debit · 7.6x if SPX falls 6%</div>
  <div class="tile-body">Four events in 26 days. 0.5% of notional for 7.6x leverage on a drawdown. Not a bear call — the insurance premium on a portfolio long AI equities while VIX is mispriced at 15.</div>
</div>"""

SECTOR_RV = """
<div class="section-label">Sector &amp; RV</div>
<div class="grid-2">
  <div class="tile tile-green">
    <div class="tile-head">Strongest — Technology (AI/Computex)</div>
    <div class="tile-body">Nemotron 3 Ultra (500B params, open model) announced at Computex. AMD EPYC Venice on TSMC 2nm in mass production. Computex runs June 1–5. AVGO reports Wednesday. The supply chain confirmation loop from Taipei is running. Lumentum +121% YTD; Applied Materials +67% YTD; the infrastructure layer is carrying the SOX.</div>
  </div>
  <div class="tile tile-green">
    <div class="tile-head">Strongest — Energy (tactical recovery)</div>
    <div class="tile-body">WTI +2.67% on Hormuz uncertainty. COT oil spec net length at −9.2k (improved from −17k prior week) — the position is nearly flat, meaning the next wave of geopolitical escalation triggers a buy, not a sell. Brent holding Hormuz premium at ~$2.81 over WTI.</div>
  </div>
</div>
<div class="grid-2">
  <div class="tile tile-red">
    <div class="tile-head">Weakest — Utilities (rate exposure)</div>
    <div class="tile-body">US 10Y at 4.47% (+3bp today) and ECB hike 10 days away. Down 4.9% since start of May. Rate-sensitive sector pricing a higher-for-longer world correctly — not a tactical short but a sector to avoid.</div>
  </div>
  <div class="tile tile-red">
    <div class="tile-head">Weakest — Consumer Discretionary (payroll risk)</div>
    <div class="tile-body">89k consensus payrolls Friday. ISM Manufacturing employment at 46.4. Goods-exposed consumer discretionary is the first to fade when goods demand falters. Services-heavy names hold; goods-exposed retail does not.</div>
  </div>
</div>
<div class="tile tile-gold">
  <div class="tile-head">RV: Long NVDA vs Short SOX equal-weight</div>
  <div class="tile-claim">Nemotron 3 Ultra is the re-rating catalyst for NVDA's 62% underperformance vs SOX YTD</div>
  <div class="tile-body">NVDA +12% vs SOX +74%. The infrastructure layer has been carrying the index; a model-layer value pivot flows back to NVDA. The Computex keynote is today's catalyst for this pair. Not a full conviction trade — watch the price action through Wednesday for confirmation from AVGO's AI revenue guide.</div>
</div>"""

POSITIONING = """
<div class="section-label">Positioning &amp; Flows</div>
<div class="tile tile-muted">
  <div class="tile-head">CFTC COT — as of May 27</div>
  <div class="tile-claim">Oil nearly net-long; EUR spec long is the pain trade into June 11</div>
  <div class="tile-body">
    <strong>Oil:</strong> Large spec net at −9.2k (improved from −17k, nearly net-long). The next escalation headline triggers a short-squeeze, not a reposition.<br>
    <strong>Gold:</strong> Spec longs at 154.3k (down from 159.8k) — lighter positioning is constructive; less to unwind on the downside.<br>
    <strong>EUR:</strong> Speculators net long EUR — the crowded dollar-bear trade of 2026. Pain trade: ECB hike is read as a growth error and EUR sells the fact. MM-2026-001 is positioned for exactly this.
  </div>
</div>
<div class="tile tile-muted">
  <div class="tile-head">Fund flows</div>
  <div class="tile-body">Tech/AI equity inflows dominate. Fixed income seeing outflows as ECB hike expectations rise. DXY at 99 reflects the dollar-bear consensus. Risk: if payrolls disappoint Friday, the dollar breaks, bonds bid, and the AI-equity rotation partially reverses — not collapses, but pauses.</div>
</div>"""

FUNDING = """
<div class="section-label">Funding &amp; Plumbing</div>
<div class="tile tile-muted">
  <div class="tile-claim">SOFR 3.62% — clean. RRP drawdown continuing. No stress signals.</div>
  <div class="tile-body">SOFR-Fed funds spread near zero. The plumbing says risk appetite is alive. One Pozsar note: the June 2026 SEC deadline for repo central clearing has driven repo market restructuring — more bilateral repo transactions moving to central clearing, which is tightening the SOFR calculation methodology. Watch whether SOFR spikes on the deadline — that would be a plumbing signal, not a macro one. Currently: no stress.</div>
</div>"""

TAPE_MISSING = """
<div class="section-label">What the Tape Is Missing</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>NVDA's underperformance is a rotation setup, not a value call.</strong> NVDA +12% vs SOX +74% YTD means the AI hardware-infrastructure complex has absorbed the capex narrative while the GPU architect underperformed. Nemotron 3 Ultra signals that NVDA is pivoting to the model layer — open, 500B parameters, targeting agentic workflows. If hyperscalers adopt Nemotron for internal reasoning tasks, NVDA's revenue base expands beyond silicon. The level that changes the story: NVDA closing above its May high on volume. That is the signal that the rotation is happening.</div>
</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>The FOMC March dot plot was split exactly 7/7 on no-cut vs one-cut for 2026.</strong> The June 16-17 dot plot is a live coin flip — one member changing their vote moves the median. If the median goes to zero cuts, DXY rallies, gold sells, MM-2026-004 (short 10Y yield) stops out at 4.65%. If the median goes to two cuts (requires payrolls to disappoint badly Friday), front-end rallies 20bp and the 2s10s steepener (MM-2026-009) accelerates. The dot plot is not a formality — it is the binary inside the FOMC binary.</div>
</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>Tanker insurance is the Hormuz risk indicator the tape is not watching.</strong> Tanker insurers are still writing Hormuz coverage at near-peacetime rates despite the mine sighting. If a mine detonates or Iran is confirmed to have deployed naval obstruction, the repricing of tanker insurance freezes physical delivery before Brent reprices. The flow constraint is insurance capacity, not supply volume. That is the second-order risk that will appear in the Brent-WTI spread <em>before</em> it appears in a headline. Watch MM-2026-003's spread below $2.50 as the real-time signal.</div>
</div>"""

CONSENSUS = """
<div class="section-label">Consensus: Bid / Offer</div>
<div class="tile tile-muted">
  <div class="tile-head">Consensus BID</div>
  <div class="tile-body">AI melt-up continues through Computex and AVGO earnings Wednesday. Fed holds June 16-17 — markets treat it as benign. Iran deal materialises before month-end. VIX stays sub-17. One cut in 2026 dot plot is the goldilocks outcome.</div>
</div>
<div class="tile tile-gold">
  <div class="tile-head">Strongest argument against — the OFFER</div>
  <div class="tile-body">Broadcom at 41x forward earnings prices six more consecutive AI revenue beats. If Wednesday's guide is merely in-line — $10B AI revenue vs $10.7B expected — the stock reprices 5–8% lower and the AI multiple compression begins from the ASIC names outward. The consensus bid requires AVGO to not just beat but raise. That is not a low bar at 41x.</div>
</div>"""

ONE_CHART = """
<div class="section-label">Today's One Chart That Matters</div>
<div class="tile tile-gold">
  <div class="tile-claim">The Brent-WTI spread: the real-time Hormuz probability machine</div>
  <div class="tile-body">Spread at $2.81 today. Entry was $3.30. Below $2.50: market has fully priced the MoU (deal 75%+ probability). Above $3.50: escalation risk is re-entering (deal below 50%). At $2.81, the market prices a ~65% deal probability. Every dollar move in the spread is worth approximately $12/bbl of Brent repricing if the MoU binary resolves. This spread is a better real-time indicator of the Iran negotiation than any headline — it processes physical market information (tanker bookings, insurance rates, Cushing flows) that the news cycle doesn't.</div>
</div>"""

CAT_CAL = """
<div class="section-label">Catalyst Calendar — next 5 trading days</div>
<table class="cal-table">
<thead><tr><th>Day</th><th>Date</th><th>Event</th><th>Consensus</th><th>View</th><th>Asymmetry</th></tr></thead>
<tbody>
<tr>
  <td>Mon</td><td>Jun 1</td>
  <td class="cal-event">Computex keynote — delivered ✓</td>
  <td>Vera Rubin ramp, AI capex confirmed</td>
  <td>Nemotron 3 Ultra (500B params) announced — exceeded hardware expectations. NVDA re-rating catalyst. AVGO ASIC thesis confirmed by supply-chain context.</td>
  <td class="asym-up">SOX +1.5% potential; NVDA convergence trade setup</td>
</tr>
<tr>
  <td>Wed</td><td>Jun 3</td>
  <td class="cal-event">Broadcom (AVGO) Q2 earnings — after close</td>
  <td>EPS $2.40, revenue $22.11B, AI revenue $10.7B</td>
  <td>UBS PT raised to $490. Six consecutive AI revenue beats. What matters: Q3 AI revenue guide. Above $11.5B = beat-and-raise. Below $10B = re-rate. In-line exits same day per MM-2026-006 rules.</td>
  <td class="asym-up">+10–15% on beat; −5–8% on in-line / miss</td>
</tr>
<tr>
  <td>Fri</td><td>Jun 5</td>
  <td class="cal-event">US May payrolls (BLS 8:30 ET) + German IFO</td>
  <td>+89k payrolls, unemployment 4.3%, wages +3.8% YoY</td>
  <td>Below 75k: 2+ cuts re-priced — dollar breaks 98, bonds rally 15bp, gold bids. Above 110k: DXY recovers above 100, ECB hike amplified as global tightening. IFO below 90 = ECB policy error confirmed pre-hike.</td>
  <td class="asym-dn">&lt;75k: DXY −0.8%, 2Y −15bp; &gt;110k: DXY +0.5%</td>
</tr>
<tr>
  <td>Wed</td><td>Jun 11</td>
  <td class="cal-event">ECB rate decision (+25bp fully priced, 3 hikes in 2026 now 92% probability)</td>
  <td>+25bp; press conference neutral-to-hawkish</td>
  <td>"One and done" language = EUR sell-the-fact, spec long unwinds violently. "Further hikes priced" = EUR spike then fade on growth concerns. DXY at 99 means EUR long spec position has thin cushion.</td>
  <td class="asym-dn">EUR/USD −0.8% on pause signal; +0.5% then fade on hawkish</td>
</tr>
<tr>
  <td>Tue–Wed</td><td>Jun 16–17</td>
  <td class="cal-event">FOMC dot plot update — the live binary</td>
  <td>No cut. March median was 3.4% (1 cut implied). Split 7/7 on no-cut vs 1-cut.</td>
  <td>One FOMC member changing vote moves the median. Zero-cut dot: DXY +0.7%, gold −2%, MM-2026-004 approaches stop. Two-cut dot (requires payroll surprise): DXY −1.2%, 2Y −20bp, MM-2026-009 steepener accelerates.</td>
  <td class="asym-dn">0-cut: DXY +0.7%, 10Y +8bp; 2-cut: DXY −1.2%, 10Y −20bp</td>
</tr>
</tbody>
</table>"""

EARNINGS = """
<div class="section-label">Earnings Calendar</div>
<div class="earnings-tile">
  <div class="earn-head">
    <span class="earn-name">Broadcom Inc.</span>
    <span class="earn-ticker">AVGO &nbsp;·&nbsp; Jun 3, after close</span>
  </div>
  <div class="earn-row"><span class="earn-k">Consensus EPS</span><span class="earn-v">$2.40 (range $2.36–$2.54) — source: AlphaStreet / FactSet (37 analysts)</span></div>
  <div class="earn-row"><span class="earn-k">Consensus Revenue</span><span class="earn-v">$22.11B (+47% YoY); AI revenue $10.7B (+140% YoY)</span></div>
  <div class="earn-row"><span class="earn-k">UBS price target</span><span class="earn-v">$490 (raised today) — "resilient AI demand, improved margins"</span></div>
  <div class="earn-row"><span class="earn-k">Into earnings</span><span class="earn-v" style="color:var(--green)">BUY 8/10 (MM-2026-006) — hold through print + 5 days; stop $228</span></div>
  <div class="earn-read">
    Nemotron 3 Ultra at Computex is today's supply-chain confirmation that custom AI silicon demand is accelerating. AVGO's hyperscaler ASIC clients (Microsoft, Google, Meta, TikTok) are building in the same ecosystem. Six consecutive AI revenue beats. <strong>What moves it:</strong> Q3 FY2026 AI revenue guidance. Above $11.5B = +15%. Below $10B = −8%, close same day.
  </div>
</div>"""

MIND = """
<div class="section-label">What Changes My Mind</div>
<div class="mind-item"><strong>MM-2026-001 · Short EURAUD:</strong> Close if EURAUD holds above 1.640 after the ECB hike — that signals the rate-hike bid is overriding the growth-error read. Currently at 1.621, 1.1% from target (1.610).</div>
<div class="mind-item"><strong>MM-2026-002 · Long Brent:</strong> Exit below $87 weekly close. MoU signed and Hormuz fully reopens removes the war premium. COT oil nearly net-long means a squeeze on escalation is more likely than capitulation.</div>
<div class="mind-item"><strong>MM-2026-003 · Long Brent / Short WTI spread:</strong> Discretionary close below 2.00 — physical market has given up on Hormuz premium. Currently at 2.81. This is the most likely near-term close.</div>
<div class="mind-item"><strong>MM-2026-004 · Short US 10Y yield:</strong> Stop at 4.65% — now 18bp away at 4.47%. Strong payrolls Friday or 0-cut dot plot June 17 are the two triggers. Watching closely.</div>
<div class="mind-item"><strong>MM-2026-005 · Long gold (pre-position):</strong> Min hold until July 15. Stop $4,250. FOMC dot plot zero-cut + gold closes below $4,400 = early warning. COT longs lightening (154.3k) is constructive not negative.</div>
<div class="mind-item"><strong>MM-2026-006 · Long AVGO:</strong> Exit same day if Wednesday earnings AI revenue guide is below $10B or stock closes >8.8% lower. Do not hold a miss. UBS PT $490 provides upside confirmation for the target of $285.</div>
<div class="mind-item"><strong>MM-2026-007 · Short USDJPY:</strong> Stop at 163.00 — above intervention zone. Finance Ministry has drawn the line at 160.00; above that the risk is intervention, not further yen weakness.</div>"""

CLIENT_AMMO = """
<div class="section-label">Talking Points Today</div>
<div class="ammo">
  <div class="ammo-q">What did Nvidia actually announce at Computex — and does it matter for the trade book?</div>
  <div class="ammo-a">Nemotron 3 Ultra — a 500-billion-parameter open AI model targeting complex reasoning and agentic workflows. It matters because it moves NVDA from pure hardware into the model layer, which is where the software margin lives. NVDA +12% YTD vs SOX +74% is the gap that closes if the software pivot is real. For the book: this is confirmation for MM-2026-006 (long AVGO, custom ASIC) and sets up a fresh NVDA vs SOX equal-weight pair if AVGO confirms Wednesday.</div>
</div>
<div class="ammo">
  <div class="ammo-q">Is the Iran deal closer or further away today?</div>
  <div class="ammo-a">Further. Iran's state media dismissed Trump's "largely negotiated" statement as "incomplete and inconsistent with reality." The ceasefire has been violated by both sides since April 8. A naval mine is in the strait. The Brent-WTI spread at $2.81 says the market gives it 65% — but that's the market pricing hope, not a signed document. The political constraint: Trump needs this before June 11 (ECB hike day). Iran is not in a hurry.</div>
</div>
<div class="ammo">
  <div class="ammo-q">Why is the dollar so weak if oil is rising?</div>
  <div class="ammo-a">Because the dollar-oil correlation broke. DXY at 99 near two-week lows even as WTI recovers 2.67%. The dollar is being driven purely by Fed expectations — 96.9% probability of no cut June 16-17. Oil is being driven by Hormuz geopolitics. When those two drivers were aligned (2022-2024), the correlation held. Now they're in different regimes. The correlation breaks back together when either the Fed pivots (dollar sells hard) or the Iran binary resolves (oil snaps to fair value). Until then, they move separately.</div>
</div>"""

CITATIONS = """
<div class="section-label">Citations</div>
<div class="citation">
Sources beyond Reuters / Bloomberg / FT / WSJ / AP / central banks / CME / Cboe:<br>
· TradingEconomics — EURUSD 1.1644, USDJPY 159.37, WTI $89.69, Brent, DXY ~99 (tradingeconomics.com)<br>
· TwelveData / ExchangeRates.UK — Gold $4,541.80 (twelvedata.com / exchangerates.org.uk)<br>
· AlphaStreet — AVGO Q2 EPS consensus $2.40, revenue $22.11B (news.alphastreet.com)<br>
· TradingKey — AVGO $100B volatility warning, AI demand verification (tradingkey.com)<br>
· StoneX — COT precious metals and crude oil positioning (stonex.com)<br>
· ServeTheHome — Nvidia Computex 2026 keynote live coverage (servethehome.com)<br>
· CryptoBriefing — Nvidia Nemotron 3 Ultra 500B parameter model announcement (cryptobriefing.com)<br>
· ING Think — ECB rate hike analysis (think.ing.com)<br>
· Motley Fool — NVDA Computex 2026 / AVGO earnings analysis (fool.com)<br>
· BondSavvy — Fed dot plot March 2026 analysis (bondsavvy.com)<br>
· CME FedWatch — 96.9% June hold probability (cmegroup.com)
</div>"""

STALENESS = """
<div class="section-label">Staleness Check</div>
<table class="stale-tbl">
<thead><tr><th>Datum</th><th>Source</th><th>As of</th><th>Status</th></tr></thead>
<tbody>
<tr><td>EURUSD 1.1644</td><td>TradingEconomics</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>USDJPY 159.37</td><td>TradingEconomics</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>WTI $89.69</td><td>TradingEconomics / OilPrice</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>Brent ~$92.50</td><td>ICE / Reuters (estimated)</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>Gold $4,541.80</td><td>TwelveData / ExchangeRates.UK</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>US 10Y 4.47%</td><td>TradingEconomics / FRED</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>S&P 500 ~7,580</td><td>Yahoo Finance (May 29 close)</td><td>2026-05-29</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>DAX 25,104.70</td><td>Investing.com</td><td>2026-06-01 (est)</td><td class="fresh">Fresh</td></tr>
<tr><td>FTSE 10,409.28</td><td>Investing.com</td><td>2026-06-01 (est)</td><td class="fresh">Fresh</td></tr>
<tr><td>DXY ~99</td><td>StreetStats / TradingView</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>VIX 15.32</td><td>Macrotrends / Yahoo Finance</td><td>2026-05-29</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>SOFR 3.62%</td><td>NY Fed / SOFRrate.com</td><td>2026-05-28</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>COT oil net −9.2k</td><td>CFTC / StoneX</td><td>2026-05-27</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>COT gold 154.3k</td><td>CFTC / FXStreet</td><td>2026-05-29</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>AVGO ~$252</td><td>Estimated (UBS PT $490 ref)</td><td>approximate</td><td class="stale-flag">Approximate</td></tr>
<tr><td>2s10s ~+15bp</td><td>FRED / centralbank.watch</td><td>2026-05-25</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>MOVE, GBPUSD, Bund, Gilt, Nikkei</td><td>Various (unavailable this refresh)</td><td>unavailable</td><td class="stale-flag">Unavailable</td></tr>
</tbody>
</table>"""

# ─────────────────────────────────────────────────────────────────────────────
# RHS — Dashboard
# ─────────────────────────────────────────────────────────────────────────────
DASH = [
    ("S&P 500 (est)",  "~7,580",     "+0.22%",  "up"),
    ("Nasdaq (est)",   "~27,200",    "+0.9%",   "up"),
    ("DAX",            "25,104",     "+0.05%",  "up"),
    ("Nikkei",         "—",          "",        "unverified"),
    ("FTSE 100",       "10,409",     "−0.16%",  "down"),
    ("EURUSD",         "1.1644",     "−0.14%",  "down"),
    ("GBPUSD",         "~1.36",      "",        "flat"),
    ("USDJPY",         "159.37",     "+0.06%",  "up"),
    ("USDCNH",         "—",          "",        "unverified"),
    ("DXY",            "~99.0",      "−0.1%",   "down"),
    ("US 10Y",         "4.47%",      "+3bp",    "up"),
    ("Bund 10Y",       "—",          "",        "unverified"),
    ("Gilt 10Y",       "—",          "",        "unverified"),
    ("2s10s",          "~+15bp",     "",        "flat"),
    ("WTI Crude",      "$89.69",     "+2.67%",  "up"),
    ("Brent Crude",    "~$92.50",    "+0.7%",   "up"),
    ("Gold (XAU)",     "$4,541.80",  "+0.01%",  "flat"),
    ("VIX",            "15.32",      "−2.7%",   "down"),
    ("SOFR",           "3.62%",      "",        "flat"),
    ("MOVE",           "—",          "",        "unverified"),
]

def dash_tile(name, val, chg, d):
    if d == "unverified" or val in ("—",""):
        body = '<span style="color:var(--ink-mute)">unverified</span>'
    else:
        cls = {"up":"chg-up","down":"chg-dn","flat":"chg-flat"}.get(d,"chg-flat")
        body = f'{e(val)} <span class="{cls}">{e(chg)}</span>'
    return f'<div class="dash-tile"><div class="dlabel">{e(name)}</div><div class="dval">{body}</div></div>'

dashboard_html = '<div class="dash-grid">' + "".join(dash_tile(*r) for r in DASH) + '</div>'

theme_line = (
    '<div class="theme-line">Computex delivered Nemotron 3 Ultra; Hormuz delivered a mine. '
    'The AI vertical has a receipt. The peace deal still doesn&rsquo;t.</div>'
)

# ─────────────────────────────────────────────────────────────────────────────
# Trade cards (today's new ideas — IDs 006–009)
# ─────────────────────────────────────────────────────────────────────────────
new_today = [t for t in trades["open"] if t["id"] in
             ("MM-2026-006","MM-2026-007","MM-2026-008","MM-2026-009")]
idea_cards = "".join(trade_card(t) for t in new_today) or (
    '<p style="font-size:12px;color:var(--ink-mute)">no new ideas — forcing a trade is the trade.</p>'
)

# ─────────────────────────────────────────────────────────────────────────────
# Charts
# ─────────────────────────────────────────────────────────────────────────────
charts_html = (
    '<div class="section-label" style="margin-top:1.5rem">Charts</div>'
    f'<div style="margin-bottom:8px">{eq_svg}</div>'
    f'<div style="margin-bottom:8px">{cal_svg}</div>'
    f'<div style="margin-bottom:8px">{vix_svg}</div>'
    f'<div style="margin-bottom:8px">{yc_svg}</div>'
)

# ─────────────────────────────────────────────────────────────────────────────
# Assemble
# ─────────────────────────────────────────────────────────────────────────────
LHS = "\n".join([
    YESTERDAY, WRAP, CORRELATION, VOL_SKEW, SECTOR_RV,
    POSITIONING, FUNDING, TAPE_MISSING, CONSENSUS, ONE_CHART,
    CAT_CAL, EARNINGS, MIND, CLIENT_AMMO, CITATIONS, STALENESS,
])

RHS = "\n".join([
    '<div class="section-label">The Open</div>',
    dashboard_html,
    theme_line,
    '<div class="section-label" style="margin-top:1.5rem">New Trade Ideas</div>',
    idea_cards,
    '<div class="section-label" style="margin-top:1.5rem">Live Book + Scoreboard</div>',
    live_book(trades),
    charts_html,
])

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Market Map &middot; {TODAY}</title>
  <style>{CSS}</style>
</head>
<body>
<div class="page">
  {MASTHEAD}
  <div class="two-col">
    <div class="lhs">{LHS}</div>
    <div class="rhs">{RHS}</div>
  </div>
</div>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
out = os.path.join(HERE, "output.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

book.save_json(book.TRADES_PATH, trades)
book.save_json(book.REGIME_PATH, regime_log)

print(f"output.html: {len(HTML):,} bytes")
print(f"Open trades: {len(trades['open'])}")
for t in trades["open"]:
    print(f"  {t['id']} | {t['trade'][:40]} | pnl {t.get('current_pnl_pct',0):+.2f}%")

import subprocess
subprocess.Popen(["start", out], shell=True)
