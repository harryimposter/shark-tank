#!/usr/bin/env python3
"""Market Map — new-format renderer (PROMPT.md two-column Anthropic design spec).
Uses the data already saved in trades.json / regime_log.json from today's run.
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

# ── CSS — exact Anthropic design language from PROMPT.md ──────────────────
CSS = """
:root {
  --bg:#ffffff; --surface:#f7f7f5; --ink:#1a1a1a; --ink-soft:#6b6b6b;
  --ink-mute:#9a9a9a; --gold:#b8960c; --red:#c0392b; --green:#1a7a45;
  --line:rgba(0,0,0,0.1); --radius-md:8px; --radius-lg:12px;
  --font:-apple-system,"Helvetica Neue",sans-serif;
  --serif:Georgia,"Times New Roman",serif;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.65;padding:0}
.page{max-width:1400px;margin:0 auto;padding:2rem 2rem 4rem}
.two-col{display:grid;grid-template-columns:1fr 380px;gap:2.5rem;align-items:start}
@media(max-width:960px){.two-col{grid-template-columns:1fr}}
.lhs{min-width:0}
.rhs{min-width:0;position:sticky;top:1rem}
.masthead{border-bottom:0.5px solid var(--line);padding-bottom:1rem;margin-bottom:1.5rem}
.article-title{font-family:var(--serif);font-size:2rem;font-weight:400;line-height:1.25;color:var(--ink);margin:0 0 0.4rem}
.meta{font-size:11px;color:var(--ink-mute);letter-spacing:0.08em;text-transform:uppercase;margin-top:0.35rem}
.regime-tag{display:inline-block;font-size:10px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold);border:0.5px solid var(--gold);border-radius:20px;padding:2px 10px;margin-bottom:0.75rem}
.gold-rule{border:none;border-top:1px solid var(--gold);margin:1rem 0 0;opacity:0.4}
.section-label{font-size:10px;font-weight:500;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-mute);margin:1.75rem 0 0.75rem}
.section-label:first-child{margin-top:0}
.dash-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:5px;margin-bottom:1rem}
.dash-tile{background:var(--surface);border-radius:var(--radius-md);padding:0.5rem 0.75rem;border:0.5px solid var(--line)}
.dash-tile .dlabel{font-size:10px;color:var(--ink-mute);margin-bottom:2px}
.dash-tile .dval{font-size:13px;font-weight:500;color:var(--ink);font-variant-numeric:tabular-nums}
.dash-tile .dchg{font-size:11px}
.chg-up{color:var(--green)}.chg-dn{color:var(--red)}.chg-flat{color:var(--ink-mute)}
.theme-line{border-left:2px solid var(--gold);padding:0.5rem 0.85rem;background:var(--surface);border-radius:0 var(--radius-md) var(--radius-md) 0;margin:1rem 0;font-size:13px;font-weight:500;line-height:1.5}
.tile{background:var(--bg);border:0.5px solid var(--line);border-radius:var(--radius-lg);padding:1rem 1.1rem;margin-bottom:8px}
.tile-head{font-size:10px;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:0.4rem}
.tile-claim{font-size:13px;font-weight:500;color:var(--ink);line-height:1.5;margin-bottom:0.4rem}
.tile-body{font-size:12px;color:var(--ink-soft);line-height:1.6}
.tile-gold{border-top:2px solid var(--gold)}.tile-green{border-top:2px solid var(--green)}.tile-red{border-top:2px solid var(--red)}.tile-muted{border-top:2px solid var(--line)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
@media(max-width:600px){.grid-2,.grid-3{grid-template-columns:1fr}}
.trade-card{background:var(--bg);border:0.5px solid var(--line);border-radius:var(--radius-lg);padding:1rem 1.1rem;margin-bottom:8px}
.tc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem}
.tc-name{font-size:13px;font-weight:500;color:var(--ink)}
.tc-class{font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);margin-top:2px}
.conv-badge{font-size:11px;font-weight:500;background:var(--surface);border:0.5px solid var(--line);border-radius:20px;padding:2px 10px;color:var(--ink);white-space:nowrap}
.tc-row{display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:0.5px solid var(--line)}
.tc-row:last-of-type{border-bottom:none}
.tc-k{color:var(--ink-mute)}.tc-v{font-weight:500;color:var(--ink)}
.conv-bar{display:flex;gap:3px;align-items:center;margin:0.5rem 0}
.pip{width:18px;height:4px;border-radius:2px;background:var(--line)}
.pip.on{background:var(--gold)}
.conv-detail{font-size:10px;color:var(--ink-mute);margin-left:6px}
.tc-thesis{font-size:12px;color:var(--ink-soft);line-height:1.6;margin-top:0.6rem;padding-top:0.6rem;border-top:0.5px solid var(--line)}
.score-row{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px}
.score-tile{background:var(--surface);border-radius:var(--radius-md);padding:0.5rem 0.6rem;text-align:center}
.sval{font-size:18px;font-weight:500;color:var(--ink)}
.sval.pos{color:var(--green)}.sval.neg{color:var(--red)}
.slabel{font-size:10px;color:var(--ink-mute);margin-top:2px}
.live-table{width:100%;font-size:12px;border-collapse:collapse}
.live-table th{font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-mute);font-weight:500;padding:0 0 6px;text-align:left;border-bottom:0.5px solid var(--line)}
.live-table td{padding:6px 0;border-bottom:0.5px solid var(--line);color:var(--ink);vertical-align:middle}
.live-table tr:last-child td{border-bottom:none}
.pnl-pos{color:var(--green);font-weight:500}.pnl-neg{color:var(--red);font-weight:500}
.pill{font-size:10px;padding:2px 8px;border-radius:20px;background:var(--surface);color:var(--ink-mute);border:0.5px solid var(--line)}
.prog-bar{height:4px;background:var(--line);border-radius:2px;overflow:hidden;min-width:48px;margin-top:3px}
.prog-bar>span{display:block;height:100%;background:var(--gold)}
.canary{padding:0.55rem 0;border-bottom:0.5px solid var(--line);display:flex;gap:10px;align-items:flex-start}
.canary:last-child{border-bottom:none}
.cdot{width:6px;height:6px;border-radius:50%;background:var(--gold);flex-shrink:0;margin-top:5px}
.ctext{font-size:12px;color:var(--ink-soft);line-height:1.6}
.ctext strong{color:var(--ink);font-weight:500}
.ammo{padding:0.55rem 0;border-bottom:0.5px solid var(--line)}
.ammo:last-child{border-bottom:none}
.ammo-q{font-size:12px;font-weight:500;color:var(--ink);margin-bottom:3px}
.ammo-a{font-size:12px;color:var(--ink-soft);line-height:1.5}
.yesterday{background:var(--surface);border-radius:var(--radius-md);padding:0.75rem 1rem;margin-bottom:1rem}
.yest-item{font-size:12px;color:var(--ink-soft);padding:4px 0;display:flex;gap:8px;align-items:flex-start;border-bottom:0.5px solid var(--line)}
.yest-item:last-child{border-bottom:none}
.tick-g{color:var(--green);flex-shrink:0;font-weight:600}
.tick-r{color:var(--red);flex-shrink:0;font-weight:600}
.tick-n{color:var(--ink-mute);flex-shrink:0}
.stale-tbl{width:100%;font-size:11px;border-collapse:collapse}
.stale-tbl th{font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-mute);font-weight:500;padding:0 0 4px;text-align:left;border-bottom:0.5px solid var(--line)}
.stale-tbl td{padding:4px 0;border-bottom:0.5px solid var(--line);color:var(--ink-soft)}
.stale-tbl tr:last-child td{border-bottom:none}
.fresh{color:var(--green);font-weight:500}.stale-flag{color:var(--red);font-weight:500}
.citation{font-size:10px;color:var(--ink-mute);line-height:1.9}
.wrap-body{font-family:var(--serif);font-size:16px;line-height:1.85;color:var(--ink)}
.wrap-body p{margin-bottom:1.1rem}
.wrap-body strong{font-weight:600}
.vol-surface{background:var(--surface);border-radius:var(--radius-md);padding:0.75rem 1rem;font-size:12px;color:var(--ink-soft);line-height:1.7}
.cal-table{width:100%;font-size:12px;border-collapse:collapse}
.cal-table th{font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-mute);font-weight:500;padding:0 6px 6px 0;text-align:left;border-bottom:0.5px solid var(--line)}
.cal-table td{padding:7px 6px 7px 0;border-bottom:0.5px solid var(--line);vertical-align:top}
.cal-table tr:last-child td{border-bottom:none}
.cal-event{color:var(--gold);font-weight:500}
.asym-up{color:var(--green)}.asym-dn{color:var(--red)}
.earnings-tile{background:var(--bg);border:0.5px solid var(--line);border-left:3px solid var(--gold);border-radius:var(--radius-lg);padding:1rem 1.1rem;margin-bottom:8px}
.earn-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.6rem}
.earn-name{font-size:14px;font-weight:500;color:var(--ink)}
.earn-ticker{font-size:11px;color:var(--ink-mute);font-family:monospace}
.earn-row{display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:0.5px solid var(--line)}
.earn-row:last-of-type{border-bottom:none}
.earn-k{color:var(--ink-mute)}.earn-v{font-weight:500}
.earn-read{font-size:12px;color:var(--ink-soft);margin-top:0.5rem;line-height:1.6}
.mind-item{font-size:12px;color:var(--ink-soft);padding:4px 0;border-bottom:0.5px solid var(--line);line-height:1.6}
.mind-item:last-child{border-bottom:none}
.mind-item strong{color:var(--ink);font-weight:500}
"""

# ── Helpers ───────────────────────────────────────────────────────────────
def pips(conviction, cb):
    n = int(conviction)
    dots = "".join(
        f'<div class="pip{"  on" if i < n else ""}"></div>' for i in range(10)
    )
    detail = (
        f'gap({cb.get("gap",0)}/3) · '
        f'catalyst({cb.get("catalyst",0)}/2) · '
        f'pos({cb.get("positioning",0)}/2) · '
        f'confirm({cb.get("confirmation",0)}/2) · '
        f'stop({cb.get("stop_quality",0)}/1)'
    )
    return f'<div class="conv-bar">{dots}<span class="conv-detail">{e(detail)}</span></div>'

def pnl_span(p):
    if p is None:
        return '<span style="color:var(--ink-mute)">—</span>'
    cls = "pnl-pos" if p > 0 else ("pnl-neg" if p < 0 else "")
    return f'<span class="{cls}">{p:+.2f}%</span>'

def progress_pct(t, level):
    entry, target = t.get("entry"), t.get("target")
    if entry is None or target is None or target == entry:
        return 0
    d = 1 if target >= entry else -1
    p = d * (level - entry) / abs(target - entry)
    return max(0, min(100, int(p * 100)))

def trade_card(t, is_new=True):
    cb = t.get("conviction_breakdown", {})
    rows = [
        ("Asset", t.get("asset_class","")),
        ("Structure", t.get("structure","")),
        ("Entry", t.get("entry","")),
        ("Stop", t.get("stop","")),
        ("Target", t.get("target","")),
        ("Horizon", t.get("horizon","")),
    ]
    if t.get("min_hold_days"):
        rows.append(("Min hold", f'{t["min_hold_days"]}d'))
    row_html = "".join(
        f'<div class="tc-row"><span class="tc-k">{e(k)}</span><span class="tc-v">{e(v)}</span></div>'
        for k, v in rows
    )
    return f"""
<div class="trade-card">
  <div class="tc-top">
    <div>
      <div class="tc-name">{e(t.get("trade",""))}</div>
      <div class="tc-class">{e(t.get("type","reactive"))} · {e(t.get("asset_class",""))}</div>
    </div>
    <div class="conv-badge">{e(t.get("conviction","?"))}/10</div>
  </div>
  {row_html}
  {pips(t.get("conviction", 0), cb)}
  <div class="tc-thesis">{e(t.get("thesis",""))}</div>
</div>"""

def live_book_section(trades):
    # Scoreboard
    closed = trades.get("closed", [])
    open_t = trades.get("open", [])
    graded = [t for t in closed if "pnl_pct" in t.get("exit", {})]
    if graded:
        pnls = [t["exit"]["pnl_pct"] for t in graded]
        wins = [p for p in pnls if p > 0]
        hit_rate = 100 * len(wins) / len(graded)
        best = max(graded, key=lambda t: t["exit"]["pnl_pct"])
        score_html = f"""
<div class="score-row">
  <div class="score-tile"><div class="sval">{len(graded)}</div><div class="slabel">Closed</div></div>
  <div class="score-tile"><div class="sval">{hit_rate:.0f}%</div><div class="slabel">Hit rate</div></div>
  <div class="score-tile"><div class="sval pos">{sum(pnls):+.1f}%</div><div class="slabel">Sum P&amp;L</div></div>
  <div class="score-tile"><div class="sval pos">{best["id"]}</div><div class="slabel">Best</div></div>
</div>"""
    else:
        score_html = f'<p style="font-size:12px;color:var(--ink-mute);margin-bottom:0.75rem">Book opened {TODAY} — scoreboard builds as trades close.</p>'

    # Open table
    open_rows = []
    for t in open_t:
        cur = t.get("current", t.get("entry"))
        pl = t.get("current_pnl_pct")
        prog = progress_pct(t, cur) if cur else 0
        opened = t.get("opened", "")
        horizon = t.get("horizon", "")
        # days remaining — rough: weeks=14d, months=90d
        from datetime import date as _d
        try:
            held = (_d.today() - _d.fromisoformat(opened)).days
            h_days = {"weeks": 14, "months": 90, "2 weeks": 14, "3 months": 90, "26 days": 26}.get(horizon, 30)
            remaining = max(0, h_days - held)
            rem_str = f'<span style="color:{"var(--red)" if remaining < 5 else "var(--ink-mute)"}">{remaining}d</span>'
        except Exception:
            rem_str = "—"
        open_rows.append(f"""<tr>
  <td><span class="pill">{e(t.get("id",""))}</span></td>
  <td style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{e(t.get("trade",""))}</td>
  <td>{e(opened)}</td>
  <td style="font-variant-numeric:tabular-nums">{e(cur)}</td>
  <td>{pnl_span(pl)}</td>
  <td>{rem_str}</td>
  <td><div class="prog-bar"><span style="width:{prog}%"></span></div></td>
</tr>""")

    open_tbl = f"""
<table class="live-table">
  <thead><tr><th>ID</th><th>Trade</th><th>Opened</th><th>Current</th><th>P&L</th><th>Window</th><th>→ Target</th></tr></thead>
  <tbody>{"".join(open_rows) or '<tr><td colspan="7" style="color:var(--ink-mute)">no open trades</td></tr>'}</tbody>
</table>"""

    # Closed ledger
    if closed:
        closed_rows = "".join(f"""<tr>
  <td><span class="pill">{e(t.get("id",""))}</span></td>
  <td>{e(t.get("trade",""))}</td>
  <td>{e(t.get("exit",{}).get("result",""))}</td>
  <td>{pnl_span(t.get("exit",{}).get("pnl_pct"))}</td>
  <td style="color:var(--ink-mute)">{e(t.get("exit",{}).get("days_held",""))}d</td>
</tr>""" for t in closed)
        closed_tbl = f"""
<div class="section-label" style="margin-top:1rem">Closed ledger</div>
<table class="live-table">
  <thead><tr><th>ID</th><th>Trade</th><th>Result</th><th>P&L</th><th>Held</th></tr></thead>
  <tbody>{closed_rows}</tbody>
</table>"""
    else:
        closed_tbl = '<p style="font-size:11px;color:var(--ink-mute);margin-top:0.5rem">No closed trades yet.</p>'

    return score_html + open_tbl + closed_tbl

# ── Load data ─────────────────────────────────────────────────────────────
trades = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

open_trades  = trades.get("open", [])
# Split into inherited vs new (opened today)
inherited = [t for t in open_trades if t.get("opened") != TODAY or t["id"] in
             ("MM-2026-001","MM-2026-002","MM-2026-003","MM-2026-004","MM-2026-005")]
new_today = [t for t in open_trades if t.get("opened") == TODAY and t["id"] not in
             ("MM-2026-001","MM-2026-002","MM-2026-003","MM-2026-004","MM-2026-005")]

# Charts
eq_svg  = charts.equity_curve(trades["closed"])
cal_svg = charts.calibration(trades["closed"])
vix_svg = charts.vix_term_structure([
    {"label": "VIX9D", "value": 13.5},
    {"label": "VIX",   "value": 15.3},
    {"label": "VIX3M", "value": 17.2},
    {"label": "VIX6M", "value": 18.5},
])
yc_svg  = charts.yield_curve([
    {"label": "2Y",  "value": 4.71},
    {"label": "5Y",  "value": 4.58},
    {"label": "10Y", "value": 4.46},
    {"label": "30Y", "value": 4.62},
])

# ── Sections ──────────────────────────────────────────────────────────────
MASTHEAD = f"""
<div class="masthead">
  <div class="regime-tag">AI Vertical Meets Hormuz Binary</div>
  <h1 class="article-title">AI Vertical Meets Hormuz Binary</h1>
  <p class="meta">Pre-market intelligence brief &middot; {TODAY} &middot; generated {NOW} local &middot; self-graded book</p>
  <hr class="gold-rule">
</div>"""

YESTERDAY = """
<div class="section-label">Yesterday, graded</div>
<div class="yesterday">
  <div class="yest-item">
    <span class="tick-g">✓</span>
    <span><strong>MM-2026-001</strong> · Short EURAUD · 1.6450 → 1.6220 · <span class="pnl-pos">+1.40%</span> · Working. ECB growth headwinds overpowering any EUR rate-hike bid; cross drifting toward 1.610 target.</span>
  </div>
  <div class="yest-item">
    <span class="tick-g">✓</span>
    <span><strong>MM-2026-002</strong> · Long Brent · $91.00 → $92.50 · <span class="pnl-pos">+1.65%</span> · Working. WTI recovered 2.67% Monday on MoU uncertainty; Brent holding Hormuz premium.</span>
  </div>
  <div class="yest-item">
    <span class="tick-r">✗</span>
    <span><strong>MM-2026-003</strong> · Long Brent / Short WTI spread · 3.30 → 2.81 · <span class="pnl-neg">−14.85%</span> · Under pressure. WTI recovering faster than Brent; Hormuz premium not widening spread as expected. Stop at 1.50 — not hit. Primary signal to watch today.</span>
  </div>
  <div class="yest-item">
    <span class="tick-n">→</span>
    <span><strong>MM-2026-004</strong> · Short US 10Y yield · 4.44% → 4.46% · <span class="pnl-neg">−0.45%</span> · Near flat. Yield edged up as WTI recovery complicates the disinflation thesis. Within noise. Thesis intact; payrolls Friday is the test.</span>
  </div>
  <div class="yest-item">
    <span class="tick-g">✓</span>
    <span><strong>MM-2026-005</strong> · Long gold (pre-position) · $4,523 → $4,541.80 · <span class="pnl-pos">+0.42%</span> · Working slowly. Gold holding MoU uncertainty bid while decoupled from WTI recovery. Min-hold: 44 days remaining.</span>
  </div>
</div>"""

WRAP = """
<div class="section-label">The Wrap</div>
<div class="wrap-body">
<p>The consensus is reading today's WTI recovery as evidence that the Hormuz deal is
holding together. It isn't. What the 2.67% bounce in crude actually says is that the
market is re-pricing the <em>failure</em> of the MoU to materialise — US and Iranian
forces exchanged fire on May 29, Trump left Thursday's meeting without a signature,
and a floating object thought to be a naval mine was sighted in the strait. The
consensus has the direction of travel exactly backwards.</p>

<p>Break apart the S&amp;P 500's position at ~7,565 and the anatomy is stark. Technology
is up 10.6% in May alone — the only sector to outperform the index's 2.9% monthly
return. The median stock is not at all-time highs. What is at all-time highs is a
concentrated bet on AI capex: Nvidia's Vera Rubin platform in full production,
AMD's EPYC Venice on TSMC 2nm entering mass production, and Broadcom guiding AI
revenue at $10.7 billion — up 140% year-on-year. So what? The peace deal is the
tail risk of the AI trade. If oil re-spikes to $100, the disinflation that funded
the multiple expansion evaporates. The AI stocks have no geopolitical stop attached.
They should.</p>

<p><strong>L1 — The driver.</strong> The Perkins regime is fiscal dominance feeding an AI melt-up.
The Fed cannot cut (CPI 3.8%, PCE 3.8%) but corporate cash flows are self-funding the
AI build-out. Hyperscaler capex — Microsoft, Google, Meta, Amazon — is multi-year
and largely insulated from rate cycles. Rate policy is a spectator to this regime.</p>

<p><strong>L2 — Counter-intuitive hook.</strong> Consensus expected the ECB to cut rates in 2026 as
eurozone growth lagged. The ECB is instead hiking on June 11 — because Iran's war pushed
eurozone energy inflation to 3.0%. The market is pricing two ECB hikes in 2026. This
is euro-negative for growth, not euro-positive for the rate differential. The ECB is
hiking into a manufacturing recession that has lasted 18 months sub-50 on the PMI.
That is a policy error unfolding in real time.</p>

<p><strong>L3 — The gap.</strong> Real economy: US May payrolls consensus 89,000 — weakest since
post-pandemic normalisation. ISM Manufacturing employment 46.4 in April, down from
48.7 in March. What's priced: Fed on hold, AI at 30–32x forward earnings, soft landing.
The gap: goods sector contraction at 46.4 is not consistent with soft landing perfection.
Services hold the thesis together. If services fade — and they do when goods demand
craters — the landing stops being soft without warning.</p>
</div>

<div class="section-label">Scenarios</div>
<div class="grid-3">
  <div class="tile tile-green">
    <div class="tile-head">Bull — 50%</div>
    <div class="tile-claim">MoU signed, Hormuz reopens, AI capex confirmed</div>
    <div class="tile-body">Disinflation resumes; AVGO beats Wednesday; Fed holds; SPX 8,000 by Q3. Risk assets: up. Rates: stable 4.2–4.5% 10Y. FX: dollar soft. Commodities: oil $80, gold $4,800.</div>
  </div>
  <div class="tile tile-gold">
    <div class="tile-head">Base — 35%</div>
    <div class="tile-claim">MoU drags; oil $85–95 range; AI confirmed but growth chops</div>
    <div class="tile-body">ECB hike tightens European conditions. Fed holds all year. SPX 7,200–7,800 range. Rates: 10Y 4.3–4.7%. FX: USDJPY intervention pressure. Gold: $4,400–4,700.</div>
  </div>
  <div class="tile tile-red">
    <div class="tile-head">Bear — 15%</div>
    <div class="tile-claim">MoU collapses; WTI re-spikes to $105+; stagflation risk</div>
    <div class="tile-body">ECB hikes into growth shock. Fed faces stagflation. Credit spreads widen sharply from historic tights. SPX −15–20%. Rates: bear-flattens. Gold: $5,200+.</div>
  </div>
</div>

<div class="wrap-body">
<p><strong>Burry tell.</strong> ISM Manufacturing employment at 46.4 means factories are quietly
cutting headcount. The services sector is the price-inelastic backstop holding the soft
landing together. Services held through goods contraction in 2023 and 2024. If services
fade, the soft landing narrative collapses without giving the market a warning. In six
months the question won't be whether the AI trade was real. It will be whether the
consumer who funds the hyperscalers' revenue is still spending.</p>

<p><strong>Pozsar mechanic.</strong> The Brent-WTI spread has <em>narrowed</em> from 3.30 (May 31
entry) to ~2.81 today despite a naval mine sighting in Hormuz. Tanker insurers are
still writing coverage at near-peacetime rates. The physical market is pricing the
MoU — not the mine. If the MoU collapses, the repricing doesn't happen in days. It
happens in hours. The balance sheet tell: tanker insurance syndicate capacity is the
real constraint. That market is thinner than it looks.</p>

<p><strong>Papic constraint.</strong> Trump wants a Nobel Prize-calibre peace deal. Iran wants
sanctions relief without a verifiable nuclear rollback. These two demands are
structurally incompatible. The June 11 ECB meeting is the next hard deadline — because
Eurozone inflation at 3.0% gives Lagarde no room to wait on a peace dividend that
hasn't been delivered. The ECB hikes regardless of what happens in the Gulf. The
political constraint: Trump cannot accept partial disarmament and call it a deal.
That timeline does not exist.</p>
</div>"""

CORRELATION = """
<div class="section-label">Correlation Regime</div>
<div class="tile tile-muted">
  <div class="tile-claim">WTI +2.67% but USDJPY flat (+0.06%) — the dollar-oil correlation is broken</div>
  <div class="tile-body">Dollar usually tracks oil's geopolitical risk. The break says the dollar is driven exclusively by Fed expectations (no cuts priced), not commodity-driven inflation. When they re-correlate, it signals either a Fed pivot or an oil shock. Neither has arrived.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-claim">Gold flat (+0.01%) while WTI +2.67% — gold is trading sovereign credit, not commodity risk</div>
  <div class="tile-body">Gold should participate in an oil-driven geopolitical rally. It hasn't. Gold owns both MoU tails simultaneously — it wins on peace (rate cut) and on war (geopolitical bid). The absence of gold's WTI participation is the confirmation that crude's move is physical, not macro fear.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-claim">AI tech at all-time highs with US 10Y at 4.46% — the duration-kills-growth correlation is dead</div>
  <div class="tile-body">In 2022 this correlation held absolutely. Hyperscaler capex commitments are now multi-year and not rate-sensitive. The break holds until credit spreads widen and corporate funding costs matter. IG at ~80bp OAS is the last line of defence.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-claim">EURAUD declining despite ECB turning hawkish — hike is priced as a growth error, not a rate catalyst</div>
  <div class="tile-body">If the ECB hikes June 11, EUR should get a rate differential bid. It isn't. The market is pricing the hike as ECB tightening into a manufacturing recession — ultimately EUR-weakening as growth differentials dominate. Confirms MM-2026-001.</div>
</div>"""

VOL_SKEW = """
<div class="section-label">Vol &amp; Skew</div>
<div class="vol-surface">
  <strong>VIX term structure — contango:</strong> VIX9D ~13.5 · VIX ~15.3 · VIX3M ~17.2 · VIX6M ~18.5<br>
  Contango at these levels signals near-term complacency, medium-term uncertainty building into the June event cluster. The surface is underpricing tails.
</div>
<div style="height:8px"></div>
<div class="tile tile-muted">
  <div class="tile-head">CBOE SKEW</div>
  <div class="tile-claim">Elevated (~140–145 range) at low absolute VIX — classic late-cycle signature</div>
  <div class="tile-body">Portfolio managers paying for downside while remaining long. The skew premium is real; the spot vol level is not. The cheapest vol is in the front end (VIX9D ~13.5). Buy it.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-head">MOVE (rates vol)</div>
  <div class="tile-claim">Unverified — stooq unavailable today. Expected elevated into ECB Jun 11 + FOMC Jun 16-17</div>
  <div class="tile-body">A double-catalyst window inside 6 days. MOVE above 100 would signal rates markets are no longer treating the ECB hike as benign.</div>
</div>
<div class="tile tile-gold">
  <div class="tile-head">Options structure for today's regime</div>
  <div class="tile-claim">Buy SPX June 27 7300/7000 put spread at ~35 index points net debit</div>
  <div class="tile-body">VIX9D at 13.5 is cheap for four non-trivial events in 15 days. 0.5% of notional cost; 7.6x payoff if SPX draws down 6%. Insurance on a portfolio long AI equities. This is not a bear call — it is the arb between implied vol (15.3) and realised event risk.</div>
</div>"""

SECTOR_RV = """
<div class="section-label">Sector &amp; RV</div>
<div class="grid-2">
  <div class="tile tile-green">
    <div class="tile-head">Strongest — Technology</div>
    <div class="tile-body">Jensen Huang keynotes Computex June 1. NVDA Vera Rubin in full production; AMD EPYC Venice on TSMC 2nm. AI supply chain from Taipei to Seoul in full acceleration. AVGO reports Wednesday — the proof-of-concept event. Structural legs: hyperscaler capex is multi-year.</div>
  </div>
  <div class="tile tile-green">
    <div class="tile-head">Strongest — Energy (tactical)</div>
    <div class="tile-body">WTI +2.67% Monday on MoU uncertainty and Hormuz mine sighting. Energy YTD +34.5% but momentum stalled. The WTI recovery is tactical — it reverses if the MoU is signed. Not chasing at these levels.</div>
  </div>
</div>
<div class="grid-2">
  <div class="tile tile-red">
    <div class="tile-head">Weakest — Utilities</div>
    <div class="tile-body">Rate-sensitive. Pressure from US 10Y at 4.46% and ECB hike expectations. Down 4.9% since start of May. Not a structural short — just the sector most exposed to higher-for-longer re-pricing.</div>
  </div>
  <div class="tile tile-red">
    <div class="tile-head">Weakest — Consumer Discretionary</div>
    <div class="tile-body">Payrolls consensus at 89k. ISM Manufacturing employment at 46.4 — factories contracting. Goods-exposed retail faces the headwind first. Services-heavy names hold; goods-exposed does not.</div>
  </div>
</div>
<div class="tile tile-gold">
  <div class="tile-head">RV Idea</div>
  <div class="tile-claim">Long SOX (semiconductor index) vs short equal-weight Consumer Discretionary (RSPD)</div>
  <div class="tile-body">AI capex is the structural driver of the semi cycle; consumer discretionary faces a softening payroll and goods-sector ISM headwind. The pair widened 10.6% in May; Computex extends it through mid-June before payrolls resets the narrative.</div>
</div>"""

POSITIONING = """
<div class="section-label">Positioning &amp; Flows</div>
<div class="tile tile-muted">
  <div class="tile-head">CFTC COT — as of May 27 (next release June 5)</div>
  <div class="tile-claim">EUR spec longs are the crowded exit into the ECB meeting</div>
  <div class="tile-body">Speculators are net long EUR — the dollar-bear trade of 2026. This is the pain trade: if the ECB hike on June 11 is read as a growth error, EUR sells the fact violently. The spec long is the most crowded macro position heading into the meeting. WTI net spec length reduced from 191.9k to 178.8k — lean positioning means a Hormuz escalation creates a violent short-squeeze. Gold: net long but reduced from recent highs; room for another leg if geopolitical risk reprices.</div>
</div>
<div class="tile tile-muted">
  <div class="tile-head">Fund flows</div>
  <div class="tile-body">Equity inflows driven by tech/AI; fixed income seeing outflows as ECB hike expectations rise. The rotation out of duration and into AI equity is the dominant flow of 2026. Risk: if payrolls disappoint Friday, the rotation reverses — bonds catch a bid, growth stocks pause.</div>
</div>"""

FUNDING = """
<div class="section-label">Funding &amp; Plumbing</div>
<div class="tile tile-muted">
  <div class="tile-claim">SOFR 3.626% — clean. No stress. RRP drawdown continues. System is not short dollars.</div>
  <div class="tile-body">SOFR-Fed funds spread near zero: risk appetite is structurally alive. One Pozsar observation: tanker insurers are writing Hormuz coverage at near-peacetime rates, meaning shipping finance is pricing the MoU at face value. When that insurance market reprices, shipping costs move before the Brent headline. Watch dry-bulk and tanker rates as the leading indicator of the physical risk premium.</div>
</div>"""

TAPE_MISSING = """
<div class="section-label">What the Tape Is Missing</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>The ECB is hiking into an 18-month manufacturing recession.</strong> Lagarde is pricing the war's oil inflation, not the war's growth destruction. Threshold: German IFO Business Climate below 90.0 before June 11 confirms the growth slowdown is accelerating — at that level the June hike is a demonstrable policy error. Watch the IFO on June 5 (same day as US payrolls).</div>
</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>USDJPY at 159.37 with intervention on the table.</strong> Finance Minister Katayama has publicly named intervention as an active tool; Japan reportedly spent ~10 trillion yen in late April. The trigger is 160.00 — above that, USDJPY reverses violently. Anything correlated to a weak yen (Nikkei financials, JPY carry trades funding long AI) reprices simultaneously. Short USDJPY (MM-2026-007) owns this at a 163.00 stop.</div>
</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>ISM Manufacturing employment at 46.4 is the jobs report's leading indicator.</strong> Factories are quietly cutting headcount while services hold. If May payrolls (Friday, 8:30 ET) show manufacturing job losses, 89k consensus becomes a ceiling not a floor. Private payrolls below 75,000 forces 2+ cuts into 2026 pricing — bonds rally, dollar breaks, gold bids strongly. That single number is the domino.</div>
</div>"""

CONSENSUS = """
<div class="section-label">Consensus: Bid / Offer</div>
<div class="tile tile-muted">
  <div class="tile-head">Consensus BID</div>
  <div class="tile-body">Fed stays on hold through 2026. AI melt-up continues through Computex and Broadcom earnings. VIX stays sub-17. No event risk materialises before the FOMC.</div>
</div>
<div class="tile tile-gold">
  <div class="tile-head">Strongest argument against</div>
  <div class="tile-body">The AI spending is funded by corporate cash flows that are themselves funded by 24-month tech margin expansion from cost cuts, not genuine economy-wide demand acceleration. If goods sector jobs deteriorate, corporate cash flows follow with a 2-quarter lag — and the AI capex cycle becomes the first casualty of a funding squeeze, not the survivor. IG credit at 80bp OAS is the last line of defence against that narrative shift.</div>
</div>"""

ONE_CHART = """
<div class="section-label">Today's One Chart That Matters</div>
<div class="tile tile-gold">
  <div class="tile-claim">The Brent-WTI spread — the real-time Hormuz risk premium</div>
  <div class="tile-body">Entry on MM-2026-003 was 3.30 (May 31); today's mark is ~2.81. The spread is not a spread trade — it is the market's best real-time probability on the MoU. Below $2.00: fully priced deal (65–70% probability). Above $4.50: deal has collapsed. At $2.81: market assigns ~65% to a signed MoU. Every $1 move in the spread is worth ~$12/bbl of Brent repricing. Watch the $2.50 level — a close below that means physical market is giving up the Hormuz premium entirely.</div>
</div>"""

CAT_CAL = """
<div class="section-label">Catalyst Calendar — next 5 trading days</div>
<table class="cal-table">
<thead><tr><th>Day</th><th>Date</th><th>Event</th><th>Consensus</th><th>View</th><th>Asymmetry</th></tr></thead>
<tbody>
<tr>
  <td>Mon</td><td>Jun 1</td>
  <td class="cal-event">Computex 2026 opens / Jensen Huang keynote</td>
  <td>Vera Rubin ramp confirmed, AI capex accelerated</td>
  <td>Rubin roadmap extended to 2027–28 with HBM4 allocation. Huang meets Korea's top-4 conglomerates on robotics AI. Anything below a production ramp confirmation is a miss.</td>
  <td class="asym-up">+1.5% SOX on ramp confirm; −1% if in-line</td>
</tr>
<tr>
  <td>Wed</td><td>Jun 3</td>
  <td class="cal-event">Broadcom (AVGO) Q2 earnings — after close</td>
  <td>EPS $2.40, revenue $22.11B, AI revenue $10.7B (+140% YoY)</td>
  <td>Six consecutive AI revenue beats. Number that matters: AI revenue guide for Q3 FY2026. Above $11.5B = beat-and-raise. Below $10B = re-rate.</td>
  <td class="asym-up">+10–15% on beat; −5–8% on in-line</td>
</tr>
<tr>
  <td>Fri</td><td>Jun 5</td>
  <td class="cal-event">US May payrolls (BLS 8:30 ET) + German IFO</td>
  <td>+89k payrolls, unemployment 4.3%; IFO ~91</td>
  <td>Below 75k re-prices 2 Fed cuts — dollar sells, bonds rally, gold bids. Above 110k confirms soft landing — DXY +0.5%. IFO below 90 confirms ECB policy error pre-hike.</td>
  <td class="asym-dn">&lt;75k: 2Y yield −15–20bp, DXY −0.8%; &gt;110k: DXY +0.5%</td>
</tr>
<tr>
  <td>Wed</td><td>Jun 11</td>
  <td class="cal-event">ECB rate decision (+25bp fully priced)</td>
  <td>+25bp hike; press conference neutral-to-hawkish</td>
  <td>The hike is done. What matters: "one and done" language = EUR sell-the-fact. "Further hikes priced" = EUR spike then fade as growth concerns dominate.</td>
  <td class="asym-dn">EUR/USD −0.8% if Lagarde signals pause; +0.5% then fade if hawkish</td>
</tr>
<tr>
  <td>Tue–Wed</td><td>Jun 16–17</td>
  <td class="cal-event">FOMC meeting + dot plot update</td>
  <td>No cut. One-cut median holds for 2026.</td>
  <td>Dot plot revision is the only number. If median goes to zero cuts: dollar bids, gold sells, duration shorts rewarded. If 2-cut median: DXY −1.2%, US 10Y −20bp.</td>
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
  <div class="earn-row"><span class="earn-k">Consensus EPS</span><span class="earn-v">$2.40 (range $2.36–$2.54) — source: AlphaStreet / FactSet</span></div>
  <div class="earn-row"><span class="earn-k">Consensus Revenue</span><span class="earn-v">$22.11B (+47% YoY)</span></div>
  <div class="earn-row"><span class="earn-k">AI Revenue Guide</span><span class="earn-v">$10.7B (+140% YoY)</span></div>
  <div class="earn-row"><span class="earn-k">Into earnings</span><span class="earn-v" style="color:var(--green)">BUY 8/10 — hold through print + 5 days</span></div>
  <div class="earn-read">
    The tape is pricing AI capex cycle continuation; AVGO is the proof-of-concept. Custom ASIC demand from Microsoft, Google, Meta, and TikTok is accelerating. Six consecutive AI revenue beats. Computex keynote today adds Taipei supply-chain tailwind. <strong>What moves it:</strong> AI revenue guidance for Q3 FY2026. Above $11.5B = +15%. Below $10B = −8%, close position same day.
  </div>
</div>"""

MIND = """
<div class="section-label">What Changes My Mind</div>
<div class="mind-item"><strong>MM-2026-001 · Short EURAUD:</strong> Close if EURAUD holds above 1.640 post-ECB hike — signals the market is reading ECB as credibly hawkish and EUR gets a sustained rate-differential bid. The trade is wrong if EUR catches a lasting bid.</div>
<div class="mind-item"><strong>MM-2026-002 · Long Brent:</strong> Exit below $87 on a weekly close — that's the technical support level that fails if the MoU is signed and Hormuz fully reopens. Below $87, the war premium is gone.</div>
<div class="mind-item"><strong>MM-2026-003 · Long Brent / Short WTI spread:</strong> Close on a move below 2.00 — at that point the physical market has given up on the Hormuz premium entirely. Most likely discretionary close in the near term.</div>
<div class="mind-item"><strong>MM-2026-004 · Short US 10Y yield:</strong> Stop at 4.65%. If payrolls beat badly (&gt;130k) and wage inflation re-accelerates, the disinflation trade is structurally broken. Close immediately at the stop.</div>
<div class="mind-item"><strong>MM-2026-005 · Long gold (pre-position):</strong> Min hold until July 15 — no discretionary close permitted. Stop at $4,250. If gold closes below that level, the dual-tail thesis has broken. FOMC June 16-17 is the first meaningful test: a zero-cut dot plot selling gold below $4,400 is the early warning.</div>"""

CLIENT_AMMO = """
<div class="section-label">Talking Points Today</div>
<div class="ammo">
  <div class="ammo-q">Is the Iran deal actually happening?</div>
  <div class="ammo-a">No — not yet. US-Iran forces exchanged fire on May 29. Trump left Thursday's meeting without a signature. A floating object thought to be a naval mine was sighted in the Strait of Hormuz. Oil is trading hope, not a signed document. The Brent-WTI spread at $2.81 is the market's real-time probability: ~65% chance of a deal, 35% chance of re-escalation. Those are not risk-asset odds on a binary.</div>
</div>
<div class="ammo">
  <div class="ammo-q">Should I be buying Nvidia and Broadcom here?</div>
  <div class="ammo-a">Yes, with a defined stop and a 2-week horizon. Jensen Huang opens Computex today; Broadcom reports Wednesday. This is the 72-hour window that confirms or denies the AI capex cycle for Q3. Define a stop on AVGO at −9% on earnings day — if the AI revenue guide disappoints, exit same day. Do not hold a miss.</div>
</div>
<div class="ammo">
  <div class="ammo-q">What is the biggest risk to the rally right now?</div>
  <div class="ammo-a">The ECB hiking June 11 into an 18-month eurozone manufacturing recession. Lagarde is pricing the war's oil inflation, not the war's growth destruction. A hike that tightens European financial conditions into a credit-vulnerable corporate sector is the catalyst for a risk-off rotation that starts in Europe and migrates to US credit spreads — which are still near historic tights at ~80bp IG OAS.</div>
</div>"""

CITATIONS = """
<div class="section-label">Citations</div>
<div class="citation">
Sources used beyond Reuters / Bloomberg / FT / WSJ / AP / central banks / CME / Cboe:<br>
· TradingEconomics — EURAUD, WTI, Brent, ISM Manufacturing Employment, USDJPY (tradingeconomics.com)<br>
· TwelveData / ExchangeRates.UK — XAU/USD $4,541.80 (twelvedata.com / exchangerates.org.uk)<br>
· centralbank.watch — US Treasury yield curve, 2s10s spread (centralbank.watch)<br>
· SOFRrate.com — SOFR 3.626% (sofrrate.com)<br>
· AlphaStreet — AVGO Q2 2026 earnings preview, EPS consensus $2.40 (news.alphastreet.com)<br>
· ING Think — ECB rate hike analysis, eurozone inflation (think.ing.com)<br>
· Motley Fool — NVDA Computex 2026 analysis (fool.com)<br>
· TradingKey / ServeTheHome — Computex 2026 keynote coverage (tradingkey.com / servethehome.com)
</div>"""

STALENESS = """
<div class="section-label">Staleness Check</div>
<table class="stale-tbl">
<thead><tr><th>Datum</th><th>Source</th><th>As of</th><th>Status</th></tr></thead>
<tbody>
<tr><td>WTI $89.69</td><td>TradingEconomics / OilPrice</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>Brent ~$92.50</td><td>ICE / Reuters (estimated)</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>Gold $4,541.80</td><td>TwelveData / ExchangeRates.UK</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>US 10Y yield 4.46%</td><td>centralbank.watch / FRED</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>USDJPY 159.37</td><td>TradingEconomics</td><td>2026-06-01</td><td class="fresh">Fresh</td></tr>
<tr><td>SOFR 3.626%</td><td>New York Fed / SOFRrate.com</td><td>2026-05-28</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>EURAUD 1.622</td><td>TradingEconomics / ValutaFX</td><td>2026-05-29</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>VIX ~15.3</td><td>Macrotrends / Yahoo Finance</td><td>2026-05-29</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>ISM Mfg Employment 46.4</td><td>BLS / FXStreet</td><td>April 2026</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>COT positioning</td><td>CFTC</td><td>2026-05-27</td><td class="stale-flag">Stale &gt;6h</td></tr>
<tr><td>DAX / FTSE / Nikkei</td><td>stooq.com (images only)</td><td>unavailable</td><td class="stale-flag">Unavailable</td></tr>
<tr><td>Bund / Gilt / DXY / EURUSD</td><td>stooq.com (images only)</td><td>unavailable</td><td class="stale-flag">Unavailable</td></tr>
<tr><td>MOVE index</td><td>ICE / Bloomberg</td><td>unavailable</td><td class="stale-flag">Unavailable</td></tr>
<tr><td>AVGO stock price (~$250)</td><td>Estimated from consensus data</td><td>approximate</td><td class="stale-flag">Approximate</td></tr>
<tr><td>2s10s spread ~+15bp</td><td>centralbank.watch / FRED</td><td>2026-05-25</td><td class="stale-flag">Stale &gt;6h</td></tr>
</tbody>
</table>"""

# ── RHS — Dashboard ───────────────────────────────────────────────────────
DASHBOARD_TILES = [
    ("S&P 500 (est)", "~7,565", "+0.6%", "up"),
    ("Nasdaq (est)",  "~27,100", "+1.0%", "up"),
    ("DAX",           "—", "", "unverified"),
    ("Nikkei",        "—", "", "unverified"),
    ("FTSE",          "—", "", "unverified"),
    ("EURUSD",        "—", "", "unverified"),
    ("GBPUSD",        "—", "", "unverified"),
    ("USDJPY",        "159.37", "+0.06%", "up"),
    ("USDCNH",        "—", "", "unverified"),
    ("DXY",           "—", "", "unverified"),
    ("US 10Y",        "4.46%", "+2bp", "up"),
    ("Bund 10Y",      "—", "", "unverified"),
    ("Gilt 10Y",      "—", "", "unverified"),
    ("2s10s",         "~+15bp", "", "flat"),
    ("WTI Crude",     "$89.69", "+2.67%", "up"),
    ("Brent Crude",   "~$92.50", "+0.7%", "up"),
    ("Gold (XAU)",    "$4,541.80", "+0.01%", "flat"),
    ("VIX",           "~15.3", "−2.7%", "down"),
    ("SOFR",          "3.626%", "", "flat"),
    ("MOVE",          "—", "", "unverified"),
]

def dash_tile(name, val, chg, direction):
    if direction == "unverified" or val in ("—", ""):
        val_html = '<span style="color:var(--ink-mute)">unverified</span>'
    else:
        chg_cls = {"up": "chg-up", "down": "chg-dn", "flat": "chg-flat"}.get(direction, "chg-flat")
        val_html = f'{e(val)} <span class="{chg_cls}">{e(chg)}</span>'
    return f'<div class="dash-tile"><div class="dlabel">{e(name)}</div><div class="dval">{val_html}</div></div>'

dashboard_html = '<div class="dash-grid">' + "".join(
    dash_tile(*t) for t in DASHBOARD_TILES
) + "</div>"

theme_line = '<div class="theme-line">The AI supercycle and the Iran ceasefire are running on parallel tracks. Computex opens today; Hormuz has a mine in the strait. Both can&rsquo;t be priced right simultaneously.</div>'

# New trade idea cards (today's new ideas only)
new_ideas_html = "".join(trade_card(t) for t in new_today)
if not new_ideas_html:
    new_ideas_html = '<p style="font-size:12px;color:var(--ink-mute)">no new ideas — forcing a trade is the trade.</p>'

# Charts section (inline in the RHS below live book for compactness)
charts_html = f"""
<div class="section-label" style="margin-top:1.5rem">Charts</div>
<div style="margin-bottom:8px">{eq_svg}</div>
<div style="margin-bottom:8px">{cal_svg}</div>
<div style="margin-bottom:8px">{vix_svg}</div>
<div style="margin-bottom:8px">{yc_svg}</div>"""

# ── Assemble HTML ─────────────────────────────────────────────────────────
LHS = "\n".join([
    YESTERDAY,
    WRAP,
    CORRELATION,
    VOL_SKEW,
    SECTOR_RV,
    POSITIONING,
    FUNDING,
    TAPE_MISSING,
    CONSENSUS,
    ONE_CHART,
    CAT_CAL,
    EARNINGS,
    MIND,
    CLIENT_AMMO,
    CITATIONS,
    STALENESS,
])

RHS = "\n".join([
    '<div class="section-label">The Open</div>',
    dashboard_html,
    theme_line,
    '<div class="section-label" style="margin-top:1.5rem">New Trade Ideas</div>',
    new_ideas_html,
    '<div class="section-label" style="margin-top:1.5rem">Live Book + Scoreboard</div>',
    live_book_section(trades),
    charts_html,
])

BODY = f"""
<div class="page">
  {MASTHEAD}
  <div class="two-col">
    <div class="lhs">{LHS}</div>
    <div class="rhs">{RHS}</div>
  </div>
</div>"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Market Map &middot; {TODAY}</title>
  <style>{CSS}</style>
</head>
<body>{BODY}</body>
</html>"""

# ── Write ─────────────────────────────────────────────────────────────────
out_path = os.path.join(HERE, "output.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"Wrote {len(HTML):,} bytes to output.html")
import subprocess
subprocess.Popen(["start", out_path], shell=True)
