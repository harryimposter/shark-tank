#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-09 (Tuesday).

Marked to LIVE TradingView levels via live_levels.py (not hand-typed). The story
the levels actually tell: Iran and Israel halted attacks and Trump is brokering a
ceasefire — and the tape barely moved. Brent eased a single dollar to ~$93 and kept
its war premium; the broad market was flat-to-down (S&P +0.3%, DAX and Dow lower)
while the bounce was confined to the chips force-sold on Friday (Nasdaq, Nikkei).
Yields did not budge. The market is treating the truce as unproven, and May CPI
tomorrow — not the ceasefire — is the event that matters.

Book action: mark to market only. Hold the oil book (the premium held, which
validates it); the rates trades wait for CPI. No new risk into the print.

Run:  python gen_2026_06_09.py
"""
import sys, os
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book
import shark_format
import live_levels

TODAY = date.today().isoformat()

trades     = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

# ── Live levels (TradingView scanner) ──────────────────────────────────────
book.step("Fetching live levels (TradingView)")
snap = live_levels.fetch()
book.log(f"resolved {len(snap)} symbols")
levels = live_levels.trade_levels(snap)
# Options have no free live feed — mark from spot, conservatively, and label.
levels["MM-2026-008"] = 45.0   # SPX Jun-27 7300/7000 put spread (model est, SPX ~7406, VIX ~19)
levels["MM-2026-011"] = 2.0    # Brent 100/115 call spread (model est, Brent ~$93)

# ── Regime ─────────────────────────────────────────────────────────────────
regime = "A Ceasefire, Not an All-Clear"
regime_note = (
    "Iran and Israel halted attacks and Trump is brokering a ceasefire — and the tape barely moved. "
    "Brent eased a single dollar to ~$93 and kept its war premium; the broad market was flat-to-down "
    "(S&P +0.3%, DAX and Dow lower) while the bounce was confined to the chips force-sold on Friday "
    "(Nasdaq, Nikkei). Yields did not budge. The market is treating the truce as unproven — and May CPI "
    "tomorrow, not the ceasefire, is the event that matters."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market (all open trades, from live levels) ─────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)
# No discretionary closes today: the Brent/WTI spread is ~3.26 (near its 3.30 entry),
# nowhere near the $2.00 exit — the Hormuz premium it owns is intact. Hold the book.

# No new ideas today. With May CPI at 8:30 tomorrow and the truce unproven, the
# highest-expected-value action is to hold the book that already owns both tails.
new_ideas_cards = []
prepos_cards    = []

# ── Helpers to build snapshot-driven tiles ─────────────────────────────────
def _g(name):
    return snap[name]["close"] if name in snap else None

def _row(label, name, fmt, bp=False, force_dir=None):
    if name not in snap:
        return {"name": label, "level": "unverified", "chg": "", "dir": "unverified"}
    chg, d = live_levels._fmt_chg(name, snap, bp=bp)
    return {"name": label, "level": fmt(snap[name]["close"]),
            "chg": chg, "dir": force_dir or d}

_idx  = lambda v: f"~{v:,.0f}"
_fx   = lambda v: f"{v:,.4f}"
_yld  = lambda v: f"{v:.2f}%"
_usd  = lambda v: f"${v:,.2f}"
_gold = lambda v: f"${v:,.0f}"

dashboard = [
    _row("S&P 500",     "spx",    _idx),
    _row("Nasdaq 100",  "ndx",    _idx),
    _row("Dow",         "dji",    _idx),
    _row("DAX",         "dax",    _idx),
    _row("Nikkei 225",  "nikkei", _idx),
    _row("FTSE 100",    "ftse",   _idx),
    _row("EURUSD",      "eurusd", _fx),
    _row("GBPUSD",      "gbpusd", _fx),
    _row("USDJPY",      "usdjpy", _fx),
    _row("USDCNH",      "usdcnh", _fx),
    _row("DXY",         "dxy",    lambda v: f"{v:,.2f}"),
    _row("US 10Y",      "us10y",  _yld, bp=True),
    _row("US 2Y",       "us02y",  _yld, bp=True),
    _row("Bund 10Y",    "de10y",  _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "unverified",
     "chg": "steeper", "dir": "up"},
    _row("WTI Crude",   "wti",    _usd),
    _row("Brent Crude", "brent",  _usd),
    _row("Gold (XAU)",  "gold",   _gold),
    _row("VIX",         "vix",    lambda v: f"{v:.2f}"),
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},
    {"name": "MOVE", "level": "~108 (est)", "chg": "", "dir": "flat"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Tue 9 Jun · TradingView"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~108", "chg": "easing (est)", "dir": "down"},
]

# ── Yesterday/week graded — built from the freshly-marked book ─────────────
NOTES = {
    "MM-2026-001": "Working. EURAUD drifted to ~1.636 as iron ore eased; the cross sits below entry. Thesis intact into Thursday's ECB — the hike is a growth error and EUR sells the fact. Stop 1.662.",
    "MM-2026-002": "Working — and validated by the tape. Brent held ~$93 despite the ceasefire headline; the war premium did not leave. Kept as the cheap re-escalation hedge. Exit on a weekly close below $87. Target $104.",
    "MM-2026-003": "Open, near flat. Brent-WTI spread ~$3.26 versus the 3.30 entry — nowhere near the $2.00 exit. The market did not collapse the Hormuz-specific premium; the spread is doing what it should. Stop 1.50.",
    "MM-2026-004": "Offside. The 10Y sat at ~4.55%, barely moved by the ceasefire — the disinflation impulse the trade needs has not arrived. Stop 4.65%, ~10bp away. CPI tomorrow is the binary. Do not add.",
    "MM-2026-005": "Firm, not falling. Gold held ~$4,344, decoupled from oil and back to trading real rates. Stop $4,250; min hold to ~July 15. The dot plot, not the headline, is the catalyst.",
    "MM-2026-007": "Slightly offside. USDJPY held ~160.1 — the dollar did not slip on the ceasefire. BoJ September hike and the intervention backstop above 162-163 remain the support. Stop 163.00.",
    "MM-2026-008": "Hedge held its value — SPX only ~7,406, so the 7300/7000 spread is close to the money, not stranded by a rally. Marked ~45 (model est). Carry it through CPI, the ECB and the dot plot.",
    "MM-2026-009": "Best structural position, up ~165%. 2s10s held +39.8bp. The curve has not given back the post-payrolls steepening. Min hold to July 16; target +60bp. Hold.",
    "MM-2026-010": "Under pressure — near the stop. Today's narrow, chip-led bounce lifted Nasdaq while DAX fell, dropping the ratio to ~0.949 against a 0.943 stop. Structural case intact; do not add while US tech leads. One more down session forces the stop.",
    "MM-2026-011": "Deflated but alive. Brent at ~$93 leaves the 100/115 call spread ~$2.0 (model est) versus the $3 premium. Defined risk; kept the residual on a fragile truce rather than pay to close. Stop 1.0.",
    "MM-2026-012": "Working slightly. EURUSD ~1.1546 into Thursday's ECB. Fully-priced hike, crowded spec long — the setup is sell-the-fact. Stop 1.182; target 1.130.",
    "MM-2026-013": "Roughly flat. The 2Y held ~4.15% — the front-end did NOT relax on the ceasefire, so the thesis (the hike is over-extrapolated) is unproven and waits on CPI and the dot plot. Min hold 30d; stop 4.35%.",
}

def _pnl_cls(p):
    return "g" if p > 0.05 else ("r" if p < -0.05 else "mute")

def _fmt_lvl(t):
    cur = t.get("current")
    if isinstance(cur, float):
        if abs(cur) < 10:    return f"{cur:.3f}"
        if abs(cur) < 1000:  return f"{cur:,.2f}"
        return f"{cur:,.0f}"
    return str(cur)

graded_rows = []
for t in trades["open"]:
    p = t.get("current_pnl_pct", 0.0) or 0.0
    cls = _pnl_cls(p)
    graded_rows.append(
        f'<tr><td class="{cls}">{t["id"]}</td><td>{book.e(t.get("trade",""))}</td>'
        f'<td>{book.e(t.get("entry"))} &rarr; {_fmt_lvl(t)}</td>'
        f'<td class="num {cls}">{p:+.2f}%</td>'
        f'<td>{NOTES.get(t["id"], "")}</td></tr>'
    )
# closed AVGO line
for t in trades["closed"]:
    ex = t.get("exit", {})
    graded_rows.append(
        f'<tr><td class="r">&#x26D4; {t["id"]}</td><td>{book.e(t.get("trade",""))}</td>'
        f'<td>{book.e(t.get("entry"))} &rarr; {book.e(ex.get("level"))}</td>'
        f'<td class="num r">{ex.get("pnl_pct",0):+.2f}%</td>'
        f'<td>STOPPED June 8. Q2 beat but the Q3 AI guide ($16.0B vs buy-side $17.2B) missed the number that mattered at 41x; payrolls finished it. Held {ex.get("days_held","")} days.</td></tr>'
    )
yesterday_graded = (
    '<table><thead><tr><th>ID</th><th>Trade</th><th>Entry &rarr; Current</th>'
    '<th>P&amp;L</th><th>Note</th></tr></thead><tbody>' + "".join(graded_rows) + '</tbody></table>'
)

# ── Staleness — live block + flagged stale block ───────────────────────────
def _stale_live(label, name, unit=""):
    if name not in snap:
        return {"datum": label, "source": "Unverified this refresh", "asof": "unavailable", "stale": True}
    return {"datum": f'{label} {snap[name]["close"]:,.2f}{unit}',
            "source": "TradingView scanner (live)", "asof": TODAY, "stale": False}

staleness = [
    _stale_live("S&P 500", "spx"),
    _stale_live("Nasdaq 100", "ndx"),
    _stale_live("DAX", "dax"),
    _stale_live("Nikkei", "nikkei"),
    _stale_live("Brent", "brent", ""),
    _stale_live("WTI", "wti", ""),
    _stale_live("Gold", "gold", ""),
    _stale_live("US 10Y", "us10y", "%"),
    _stale_live("US 2Y", "us02y", "%"),
    _stale_live("Bund 10Y", "de10y", "%"),
    _stale_live("Gilt 10Y", "gb10y", "%"),
    _stale_live("EURUSD", "eurusd"),
    _stale_live("USDJPY", "usdjpy"),
    _stale_live("EURAUD", "euraud"),
    _stale_live("DXY", "dxy"),
    _stale_live("VIX", "vix"),
    {"datum": "MM-008 / MM-011 option marks", "source": "Model estimate from spot (no live option feed)", "asof": TODAY, "stale": True},
    {"datum": "May payrolls +172k",  "source": "BLS June 5",                          "asof": "2026-06-05", "stale": True},
    {"datum": "ORCL/ADBE/SAIL est",  "source": "Finnhub (earnings_data.md, Jun 8 6am)","asof": "2026-06-08", "stale": True},
    {"datum": "SOFR ~3.62% / MOVE",  "source": "NY Fed (rail) / MOVE unverified",     "asof": "2026-06-08", "stale": True},
]

# ── Earnings intelligence (Finnhub-sourced; earnings_data.md) ──────────────
earnings_ideas = [
    {
        "ticker": "ORCL", "company": "Oracle Corp",
        "report_date": "2026-06-10", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 5, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "key_bullets": [
            "OCI grew 84% YoY in Q3 to $4.9bn; remaining performance obligations $553bn, +325% YoY.",
            "Finnhub consensus EPS $1.58; Oracle's own March guide pointed to $1.96-2.00 — a wide gap.",
            "40 buy vs 8 hold; the bull case is the backlog, the test is converting it without straining capex.",
        ],
        "what_moves_it": ("Whether OCI growth and capex guidance clear the *whisper*, not just the printed "
                          "estimate — the same bar Broadcom missed at a rich multiple last week."),
        "client_talking_point": ("Oracle is the next read on whether the AI-capex multiple holds after AVGO. "
                                 "The backlog is real; the risk is a guide that is merely very good into a tape "
                                 "that re-rates 'very good.' We are not pre-positioning into the print."),
    },
    {
        "ticker": "ADBE", "company": "Adobe Inc",
        "report_date": "2026-06-11", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 1, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "key_bullets": [
            "Consensus EPS $5.94; the stock sits near its 52-week low (224) versus a 421 high — sentiment is washed out.",
            "Split book: 19 buy / 22 hold / 4 sell — the market is undecided on AI as friend or threat.",
            "The question is net-new Firefly/AI monetisation, not headline EPS, which the model already knows.",
        ],
        "what_moves_it": ("Evidence that generative-AI is additive to ARR rather than cannibalising Creative "
                          "Cloud seats. Guidance tone outweighs the print."),
        "client_talking_point": ("Adobe is the cleanest test of the 'is AI a tax or a tailwind for incumbents' "
                                 "debate. Beaten-down into the print, so the asymmetry is in the guide, not the "
                                 "quarter. Hold, do not chase either way."),
    },
    {
        "ticker": "SAIL", "company": "SailPoint Inc",
        "report_date": "2026-06-09", "report_timing": "BMO",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "key_bullets": [
            "Identity-security; 26 buy / 3 hold / 1 sell — strong sell-side support at a $10bn cap.",
            "Revenue growth 24% YoY (TTM); a serial beater (last four surprises all positive, two large).",
            "Reports before the open today — a small-cap read on whether security spend is still defensive.",
        ],
        "what_moves_it": "ARR growth and net-retention — the durability metrics, not the penny EPS.",
        "client_talking_point": ("A small but clean tell on enterprise software demand into a higher-rate tape. "
                                 "Not a position; a data point for the broader software read."),
    },
]

# ── Brief ──────────────────────────────────────────────────────────────────
brief = {
    "regime":      regime,
    "regime_note": regime_note,
    "dashboard":   dashboard,
    "rates_levels": rates_levels,
    "staleness":   staleness,
    "yesterday_graded": yesterday_graded,
    "earnings_ideas": earnings_ideas,

    "dominant_theme": (
        "The ceasefire's real tell is in crude, not equities: a supply scare that supposedly ended gave back "
        "a single dollar of premium. The market does not believe the truce — and the front-end that de-rated "
        "the tape on Friday has not moved into tomorrow's CPI."
    ),

    # ── SUMMARY page ───────────────────────────────────────────────────────
    "summary_narrative": """
<p>The headline was the one the market had been waiting for: Iran and Israel agreed to stop firing, and
President Trump put his name to a ceasefire he is still brokering. The reaction was the surprise. Stocks
did not surge, oil did not collapse, and the front-end of the curve did not move. The S&amp;P added 0.3%,
the Dow and the DAX fell, and Brent gave back a single dollar to around $93 — keeping almost all of the war
premium it built last week. The only real movers were the chips that had been force-sold on Friday: the
Nasdaq, Korea and Japan bounced. Strip those out and there was no relief rally at all.</p>

<p>That is the tell, and it is worth sitting with. When a supply scare genuinely ends, the supply-sensitive
asset hands back its premium — and oil barely budged. The crude market is pricing this truce as unproven,
which is a more honest verdict than the equity tape's narrow bounce. The war premium still sitting in Brent
is, in effect, the market's own probability that the ceasefire fails. So the "all-clear" the chip rally
implies is contradicted by the oil price two screens over, and when those two disagree, oil is usually the
one telling the truth.</p>

<p>So the read is narrower than the headline: a real de-escalation that the market does not yet trust, into a
May CPI print tomorrow morning that the ceasefire does nothing to soften. Friday's selloff was a rates event,
and rates have not moved — the 2-year is still 4.15%, the year-end hike still priced. The disciplined posture
is to hold the book that already owns both tails rather than chase the bounce: the oil longs are validated by
crude refusing to fall, the curve steepener and short front-end wait on CPI, and no fresh risk goes on in
front of an 8:30 print that can settle the week by lunch.</p>
""",

    "takeaways": [
        "The ceasefire was announced and the tape shrugged — S&P +0.3%, Dow and DAX lower; the bounce was only the force-sold chips (Nasdaq, Nikkei, Korea).",
        "Oil barely moved: Brent held ~$93 and WTI ~$90, keeping the war premium — the crude market is pricing the truce as unproven.",
        "Rates did not budge: 2Y ~4.15%, 10Y ~4.55%, 2s10s +40bp. The front-end that drove Friday's selloff is unchanged into CPI.",
        "We marked the whole book to live TradingView levels and held everything — no closes, no new risk. The Brent/WTI spread is ~$3.26, nowhere near its exit.",
        "May CPI tomorrow (8:30 ET) is the binary; the long-DAX/short-Nasdaq RV is the one position near its stop after today's narrow tech leadership.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "CPI cools, the truce holds, the front-end finally relaxes",
         "body": "May CPI prints at or below 3.7%, the 2-year breaks under 4.05%, oil keeps bleeding the premium "
                 "as the ceasefire sticks, and the AI cohort extends today's bounce. Risk up · rates down · "
                 "dollar soft · gold firm."},
        {"kind": "base", "label": "Base", "pct": "50%",
         "headline": "CPI roughly in line, a skeptical chop, oil stays bid",
         "body": "CPI lands 3.8-4.0%, the front-end holds its hike pricing, crude keeps most of its premium on a "
                 "truce no one trusts, and Europe leads into an ECB hike. Risk mixed · rates range · dollar firm · "
                 "Brent $90-95."},
        {"kind": "bear", "label": "Bear", "pct": "15%",
         "headline": "CPI runs hot or the truce breaks",
         "body": "CPI above 4.1% re-arms the year-end hike, or a fresh exchange re-opens the oil premium toward "
                 "$100, and the AI de-rating resumes on a weak Oracle. Risk down · rates up · dollar up · "
                 "gold down then up as the growth scare arrives."},
    ],

    # ── THE MARKET MAP — Insights detailed layers ──────────────────────────
    "insights_layers": """
<p>The most informative thing a market does is refuse to move. Overnight the headline was unambiguous — a
ceasefire, brokered by the President, between two states that were exchanging missiles seventy-two hours ago —
and the reaction was a shrug. The S&amp;P added a third of a percent, the Dow and the DAX fell, and Brent
handed back exactly one dollar of a premium it had spent a week building. The only thing that rallied with
conviction was the cohort that had been force-sold on Friday: semiconductors in the US, Korea and Japan. That
is not a relief rally. It is a short-cover in the most-oversold corner, dressed up as one.</p>

<p>Decompose it, because the screen's green flatters the day. The VIX fell 12% and the Nasdaq rose, which
reads as risk-on — until you notice that gold rose too, the dollar did not fall, oil did not fall, and the
2-year did not move. A genuine de-escalation hands back the war premium in the asset that carries it; crude
gave back a dollar on a ceasefire, which is the market politely declining to believe it. The premium still
priced into Brent is the probability the tape assigns to the truce failing, and at $93 that probability is
still high. So-what: the equity bounce and the oil price are telling two different stories, and when they
diverge, the commodity — closer to the physical fact — usually wins.</p>

<p><strong>Layer 1 — the regime.</strong> Last week's frame was a two-tailed tape carrying an oil-supply tail
and a rates-repricing tail at once. The correction to make today is that <em>neither tail has actually been
removed</em>. The ceasefire was announced but crude did not price it; CPI has not printed. The map did not
simplify — it only looks calmer. Both tails are live into a fragile truce and an 8:30 inflation number, and
the book that owns both sides of that binary is positioned correctly precisely because nothing has resolved.</p>

<p><strong>Layer 2 — the counter-intuitive hook.</strong> Good news arrived and the things that should have
moved on good news didn't. A durable ceasefire is disinflationary, risk-positive and dollar-negative; instead
oil held, the dollar held, and only the force-sold chips bounced. The hook is that the market's most
supply-sensitive instrument refused the story the headline told. Watch crude, not the VIX, for the real
verdict on the truce — the VIX is measuring relief in equities, while oil is measuring belief in the peace.</p>

<p><strong>Layer 3 — the gap.</strong> Ground truth: oil holding $93 says the physical and geopolitical risk
is still priced, into a CPI print landing on still-elevated April energy. What's priced: a narrow tech relief
and a still-live year-end hike. The consensus narrative: "ceasefire, buy the dip." The gap is between an
equity tape that booked relief and an oil tape that refused it. That disagreement is the week's edge — and it
sits in commodities and rates, not in the index.</p>

<p><strong>Layer 4 — Bull / Base / Bear.</strong> <em>Bull (35%):</em> CPI cools below 3.7%, the 2-year breaks
under 4.05%, the truce holds and crude finally bleeds the premium — risk up, rates down, dollar soft, gold
firm. <em>Base (50%):</em> CPI lands in line, the front-end holds its hike pricing, oil keeps most of its
premium on a truce no one trusts, and Europe leads into Thursday's ECB — risk mixed, rates range, dollar firm.
<em>Bear (15%):</em> CPI runs hot or a fresh exchange re-opens the oil premium toward $100, and the AI
de-rating resumes on a weak Oracle — risk down, rates up, dollar up. The base case got heavier today: the
market's refusal to celebrate is itself a vote for chop.</p>

<p><strong>Layer 5 — priced vs not-priced.</strong> Mispriced the wrong way: the chip bounce treating the
truce as durable while oil says otherwise — one of those two is wrong. Half-priced: European long-end repricing
(Bund and Gilt yields rose today as the US front-end sat still). Fairly priced: a firm, range-bound dollar.
Fully priced: Thursday's ECB hike at 99%. The actionable item is the first — do not buy the tech bounce as an
all-clear the oil price is refusing to ratify.</p>

<p><strong>The Burry tell — still live, and today's bounce feeds it.</strong> Hyperscaler capex is now so large
that the marginal AI-revenue beat has to <em>accelerate</em> just to hold the multiple; Broadcom grew AI 143%
and lost a seventh of its cap because the cohort is hedged for a miss and not one name is hedged for a
growth-rate disappointment. Oracle reports tomorrow night with a $553bn backlog into that exact trap — and the
dip-buying that lifted the chips today is precisely the behaviour that precedes the next leg down if Oracle's
guide is merely very good. The ceasefire bought the AI trade a calm session, not a change in its arithmetic.</p>

<p><strong>The Pozsar mechanic.</strong> The cleanest read of the plumbing today is that it didn't move. Yields
sat still, the dollar barely eased, and secured funding is unchanged — which means the constraint from last
week is fully intact. The 2-year's implied terminal rate still sits well above SOFR, so every floating-rate
borrower that issued in 2023-24 expecting cuts is still paying more than its model assumed, and investment-grade
spreads near 80bp are still priced for a soft landing a hot CPI would question. The ceasefire relieved equity
sentiment; it relieved none of the balance-sheet pressure. Watch IG spreads on the CPI print, not the VIX.</p>

<p><strong>The Papic constraint.</strong> The political tell today was in the European long end. Bund yields
rose four basis points and Gilts seven, even as US yields fell — the market pricing Thursday's ECB hike in real
time. Christine Lagarde will deliver it because her inflation profile and the politics around it leave no room
to pause, even though the ceasefire's lower-oil path quietly weakens her rationale. And in Washington, Kevin
Warsh inherits the chair next week believing AI productivity can stem inflation, into a committee in no mood to
ease — a new chair who cannot afford to look soft on inflation in his first meeting, which caps how dovish the
dots can read whatever the data allows.</p>

<p>So what to do with all of it. The honest posture is patience expressed through what you already own. The oil
book stays — the market just validated it by refusing to sell the premium. The curve steepener and the short
front-end wait on a CPI print that has not yet given them their move. Don't chase the chip bounce; it is the
most-oversold names mean-reverting, not a regime turn. And keep the defined-risk equity hedge on, because the
one thing this tape has not done is price the binary that lands at 8:30 tomorrow.</p>
""",

    "wrap": """
<p>The headline was the one the market had been waiting for — a ceasefire between Iran and Israel, brokered by
Trump — and the reaction was a shrug. Stocks did not surge, oil did not collapse, and the front-end did not
move. The S&amp;P added 0.3%, the Dow and DAX fell, and Brent gave back a single dollar to ~$93. The only real
movers were the chips force-sold on Friday: the Nasdaq, Korea and Japan bounced. Strip those out and there was
no relief rally.</p>

<p>That is the tell. When a supply scare genuinely ends, the supply-sensitive asset hands back its premium —
and oil barely moved. The crude market is pricing the truce as unproven, a more honest verdict than the equity
bounce. The premium still in Brent is the market's probability the ceasefire fails, and at $93 it is high.
The equity tape and the oil price disagree, and oil usually wins that argument.</p>

<p><strong>The driver.</strong> Neither tail has actually been removed. The ceasefire was announced but crude
did not price it; CPI has not printed. The map did not simplify — it only looks calmer. Friday's selloff was a
rates event, and rates have not moved: the 2-year is still 4.15%, the year-end hike still priced.</p>

<p><strong>The Burry tell.</strong> The AI cohort is hedged for a revenue miss, not a growth-rate
disappointment. Oracle reports tomorrow with a $553bn backlog into that trap, and today's dip-buying in chips
is the behaviour that precedes the next leg if the guide is merely very good. The ceasefire bought calm, not a
change in the arithmetic.</p>

<p><strong>The Pozsar mechanic.</strong> The plumbing didn't move — yields sat still, the dollar barely eased,
funding is unchanged. The 2-year's implied terminal rate is still well above SOFR, IG spreads near 80bp still
priced for perfection. The ceasefire relieved sentiment, not balance-sheet pressure. Watch spreads on the CPI
print, not the VIX.</p>

<p><strong>The Papic constraint.</strong> The tell was the European long end — Bund +4bp, Gilt +7bp as US
yields fell, the market pricing Thursday's ECB hike in real time even as cheaper oil weakens the rationale.
Warsh inherits the chair next week and cannot look soft on inflation in his first meeting.</p>

<p>So what to do: hold the book that owns both tails, let the oil longs run on a premium the market just
refused to sell, wait on CPI for the rates trades, don't chase the chip bounce, and keep the hedge on.</p>
""",

    "correlation_regime": """
<p><strong>1. Equities (chips) up while oil, gold and the dollar barely move — the risk-on is fake breadth.</strong>
A real risk-on rally sells gold and the dollar and lifts the whole tape. Today gold rose, the dollar held, the
broad index was flat-to-down, and only the force-sold semis bounced. Read it as mean-reversion in the most
oversold cohort, not a regime turn — and do not extrapolate a third of a percent on the S&amp;P into an
all-clear.</p>

<p><strong>2. US yields fell while Bund and Gilt yields rose — a transatlantic rates split.</strong> The 10Y
eased a basis point or two on the ceasefire's disinflation hint, but Bund (+4bp) and Gilt (+7bp) rose as the
market prices Thursday's ECB hike. The divergence says the next rates impulse is European, not American — and
it is why long DAX is structurally sound even on a day the trade lost ground.</p>

<p><strong>3. Brent held its premium while the ceasefire headline screamed de-escalation — the physical market
disbelieving the truce.</strong> This is the day's most important non-correlation: the supply-sensitive asset
refused the supply-good news. Until crude actually rolls over, the geopolitical tail is still on, and the Brent
long (MM-2026-002) plus the call spread (MM-2026-011) are the cheap way to own it.</p>

<p><strong>4. Nasdaq +1.6% vs DAX −0.6% and Dow −0.2% — the bounce has no breadth.</strong> The same names that
led Friday's fall led today's rise, and nothing else participated. That narrowness is exactly what pressured
the long-DAX/short-Nasdaq RV (MM-2026-010) toward its stop — a single-cohort move, not a market one. The trade
needs the CPI/Oracle read to restore breadth; until then it is contested and capped in size.</p>
""",

    "vol_skew": """
<p><strong>VIX down 12% to ~18.9 — relief, but still elevated and the term structure has not fully relaxed.</strong>
VIX9D ~16 · VIX 18.9 · VIX3M ~20 · VIX6M ~21. The spot unwound part of Friday's spike, yet the curve is still
paying up for the next three weeks — rational with CPI, the ECB and a new chair's first FOMC inside the window.
The options market is not calling the truce or the event cluster benign; it is taking a breath.</p>

<p><strong>The hedge that is still working — and still close to the money.</strong> Because there was no real
relief rally, the SPX sits at ~7,406 and the Jun-27 7300/7000 put spread (MM-2026-008) is barely out of the
money, not stranded a thousand points below spot. That is the opposite of the picture a true bounce would have
left, and it is why there is no case to roll it today — it is doing its job cheaply, ~45 points (model est) with
three binary events still ahead. Carry it; do not pay to re-strike a hedge that is already where you want it.</p>

<p><strong>Rates vol is the one to watch on the print.</strong> MOVE has eased from its payroll-week highs, but
the 2-year did not move today and CPI tomorrow is a genuine binary for the front-end. A soft print collapses the
remaining hike premium; a hot one re-arms it. If rates vol turns back up through its range on the number, that is
the earliest signal the front-end relief never came — and it will show in MOVE before it shows in equities.</p>
""",

    "sector_rv": """
<p><strong>Leading — and it is a narrow list:</strong></p>
<ul>
<li><strong>Semiconductors and AI hardware:</strong> the cohort that led Friday's fall led today's bounce —
Korea and Japan's chip names recovered and the US semis followed. Be clear-eyed: this is a multiple re-rating
mean-reverting, not new demand. SK Hynix has pre-sold its 2026 HBM to Nvidia, so the bounce is credible, but
Oracle tomorrow night is the test of whether the market will pay up for AI-capex beneficiaries again.</li>
<li><strong>Energy producers:</strong> quiet outperformers, because crude refused to fall. With Brent holding
~$93 the sector keeps the geopolitical bid — the mirror image of the broad market's caution.</li>
</ul>

<p><strong>Lagging:</strong></p>
<ul>
<li><strong>European equities (DAX, broad):</strong> down on the day even as US tech rose — no AI cohort to
bounce, and a rising Bund yield into Thursday's ECB. Structurally still the right place to be long versus US
tech, but today the narrow US-chip leadership ran against it.</li>
<li><strong>Rate-proxy defensives:</strong> utilities and staples lag a (narrow) risk-on tape and stay capped by
a long end that has not eased. They become interesting again only if CPI runs hot and the safety bid returns.</li>
</ul>

<p><strong>RV — Long DAX / short Nasdaq (MM-2026-010), pressured to its stop.</strong> The ratio fell to ~0.949
against a 0.943 stop as Nasdaq rose and DAX fell. The structural case is intact — the ECB hikes Thursday into a
financials-heavy index with no AI multiple to give back — but today's single-cohort bounce is exactly the tape
that hurts it. Hold to the line; do not add while US tech leads. One more down session forces the stop, and that
is acceptable: the trade is wrong if the AI cohort keeps leading through CPI.</p>
""",

    "positioning": """
<p><strong>The crowd is long the truce in equities and short it in oil — and oil is winning.</strong></p>
<ul>
<li><strong>Oil:</strong> the premium holding near $93 says specs did <em>not</em> capitulate on the ceasefire
headline. That is constructive for the longs — there is no flush, the positioning is not stretched, and a fresh
escalation would catch a market that is still leaning the wrong way. The pain trade is a re-escalation into
specs who sold the headline.</li>
<li><strong>Front-end rates:</strong> the consensus chased the year-end hike after payrolls and has not let go —
the 2-year sat at 4.15% today. That is the crowded position a soft CPI would squeeze. If tomorrow's print cools,
the unwind is in the front end, which is what the short-2Y (MM-2026-013) and the steepener (MM-2026-009) own.</li>
<li><strong>Euro:</strong> specs sit long into Thursday's ECB. A 25bp hike is fully priced, so the risk is
sell-the-fact: a data-dependent-pause signal unwinds the crowded long. Short EURUSD (MM-2026-012) owns that exit
and a weaker euro flatters the long-DAX leg.</li>
</ul>

<p><strong>Flows:</strong> today's money went back into the chips that bled on Friday and nowhere else — a narrow,
tactical reversal, not a broad re-risking. The tell is whether it survives CPI; a hot print reverses it within a
session, which is why the equity hedge stays on and no new risk went on today.</p>
""",

    "funding": """
<p>SOFR near 3.62% — unchanged; repo orderly; and crucially the plumbing did not move on the ceasefire. The
dollar barely eased and the cross-currency basis is stable — the overnight headline relieved equity sentiment
without touching funding. <strong>The Pozsar mechanic that still binds:</strong> the 2-year's implied terminal
rate sits well above secured funding, so every floating-rate borrower that issued in 2023-24 expecting cuts is
still paying a higher marginal cost than its model assumed. Investment-grade spreads near 80bp are still priced
for a soft landing a hot CPI would question. The ceasefire bought equity calm and zero balance-sheet relief.
Watch IG spreads on tomorrow's print for the first sign the constraint is binding — the balance sheet shows the
strain before the index does.</p>
""",

    "tape_missing": """
<p><strong>1. Oil refusing to fall is the loudest signal on the screen, and the tape is reading the VIX
instead.</strong> A ceasefire that takes one dollar off Brent is a ceasefire the crude market does not trust.
The threshold is a weekly close below $87 — that is when the war premium is actually gone and the Strait trades
come off. Above it, the premium priced into Brent is the market's live probability the truce fails, and it is
the cleanest real-time gauge of the geopolitics there is.</p>

<p><strong>2. (Burry tell) Oracle's $553bn backlog meets the same bar Broadcom failed, and today's dip-buyers
are walking into it.</strong> The AI cohort is hedged for a miss, not a growth-rate disappointment. If OCI growth
or capex guidance tomorrow clears the printed estimate but not the whisper, the de-rating that paused this week
resumes — and the chips that bounced today lead it down. Watch the guide, not the EPS.</p>

<p><strong>3. The front-end has not moved, so tomorrow's CPI is effectively unhedged by the ceasefire.</strong>
The 2-year sat at 4.15% and the year-end hike is still priced; the truce does nothing to a backward-looking
inflation print landing on still-elevated April energy. A number above 4.1% re-arms the hike with oil already
falling — sticky core that a cheaper barrel does not fix — and that combination is the one the relief tape is
least positioned for.</p>
""",

    "consensus": """
<p><strong>Consensus BID:</strong> the ceasefire is the all-clear — the truce holds, oil drifts lower, CPI lands
benign, and today's chip bounce broadens into a proper relief rally. Warsh holds next week, the dots drift
hawkish but stop short of a hike, and the volatility high is behind us.</p>

<p><strong>The strongest argument against — the OFFER:</strong> two things the bid is ignoring. First, oil did
not fall, which means the market itself does not believe the premise of the bid. Second, tomorrow's CPI: headline
ran 3.8% in April on energy, and the Cleveland Fed nowcast points nearer 4.0% for May — a backward-looking number
that the ceasefire's cheaper oil will not touch for another month. A print above 4.1% confirms the inflation
impulse the front-end feared, re-arms the year-end hike, and puts gold's $4,250 stop in play — while crude is
already softening, which is the uncomfortable combination of sticky core that a cheaper barrel does not fix. The
ceasefire settled the easy question; CPI settles the hard one, and the oil market is quietly siding with the
offer.</p>
""",

    "one_chart": """
<p class="theme">Brent crude at ~$93 — the truce's lie detector.</p>
<p>Forget the VIX and the chip bounce; the single most informative price today is the one that refused to move.
A genuine end to a Gulf supply scare hands back the premium, and Brent gave back a dollar. That stickiness is the
market pricing the ceasefire as unproven — the premium left in crude is the probability the tape assigns to the
truce failing. Hold above $90 and the geopolitical tail is still live and the oil book stays on; a weekly close
below $87 is the level that says the war premium is finally gone, at which point the Strait trades come off and
the disinflation it implies hands the front-end its move. The equity tape booked relief today. Watch whether
crude ever agrees — and watch the 2-year at 4.15% for whether tomorrow's CPI lets it.</p>
""",

    "catalyst_calendar": [
        {"day": "Wed", "date": "Jun 10",
         "event": "US May CPI (BLS, 8:30 ET) — the deciding print",
         "consensus": "Headline ~3.8% YoY; core ~2.8-3.3%. Cleveland Fed nowcast nearer 4.0%.",
         "view": ("The single binary of the week, and the ceasefire does nothing to it. At/below 3.7%: the 2-year "
                  "breaks under 4.05%, the hike prices out, MM-2026-013/009 finally get their move, gold bids. "
                  "Above 4.1%: the hike re-arms while oil is already falling — sticky core a cheaper barrel does "
                  "not fix — the 2-year heads to 4.30% and gold tests $4,250."),
         "asymmetry": "<3.7%: 2Y -15bp, gold +2%; >4.1%: 2Y +15-20bp, DXY +0.5%, gold -2%",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 10",
         "event": "Oracle (ORCL) Q4 FY26 — after close",
         "consensus": "Finnhub EPS $1.58 vs Oracle's March guide $1.96-2.00; OCI +84% prior Q; RPO $553bn.",
         "view": ("The next read on the AI-capex multiple after Broadcom, and today's dip-buyers are positioned "
                  "into it. The backlog is the bull case; the test is whether OCI growth and capex guidance clear "
                  "the whisper, not the estimate. We are not pre-positioning — 'very good' can be a sell at this "
                  "multiple."),
         "asymmetry": "Guide clears whisper: cohort re-rates +; merely-good guide: the de-rating resumes",
         "dir": "flat"},
        {"day": "Thu", "date": "Jun 11",
         "event": "ECB rate decision — +25bp (99% priced; at least one more priced by year-end)",
         "consensus": "+25bp confirmed; press conference neutral-to-hawkish.",
         "view": ("The hike is locked — Bund and Gilt yields rose today pricing it — and the verb tense sets the "
                  "euro. 'Data-dependent pause' = EUR sell-the-fact, the crowded spec long unwinds, MM-2026-012 "
                  "accelerates. 'Further hikes' = EUR spike then fade as a now-cheaper-oil inflation profile and "
                  "growth damage dominate."),
         "asymmetry": "Pause signal: EUR/USD -0.8%; hawkish: EUR +0.4% spike then fade",
         "dir": "down"},
        {"day": "Wed", "date": "Jun 11",
         "event": "Adobe (ADBE) Q2 — after close",
         "consensus": "Consensus EPS ~$5.94; stock near 52-week lows; split sell-side (19 buy / 22 hold / 4 sell).",
         "view": ("The cleanest test of whether generative-AI is a tax or a tailwind for software incumbents. "
                  "Washed-out into the print, so the asymmetry is in the Firefly/AI monetisation commentary, not "
                  "the EPS the model already knows. Hold, do not chase."),
         "asymmetry": "AI additive to ARR: software relief; cannibalisation read: another leg down",
         "dir": "flat"},
        {"day": "Tue-Wed", "date": "Jun 16-17",
         "event": "FOMC + dot plot — Warsh's first meeting, no cut priced",
         "consensus": ">80% hold in June; March median one cut; the dots are the whole event.",
         "view": ("A new chair who believes AI productivity can stem inflation, into a committee in no mood to "
                  "ease. He cannot look soft on inflation in his first meeting, which caps how dovish the dots can "
                  "read. Zero-cut median: 2Y +10bp, gold sells, MM-2026-004 nears its stop. One-cut held: the "
                  "market exhales, MM-2026-013 accelerates. CPI tomorrow shapes the signal."),
         "asymmetry": "0-cut dots: DXY +0.7%, 2Y +10bp; 1-cut held: 2Y -15bp, gold +2%",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660 after Thursday's ECB press conference — a
rate-hike bid overriding the growth-error read. At ~1.636; stop 1.662.</li>

<li><strong>MM-2026-002 · Long Brent:</strong> exit on a weekly close below $87 — the war premium gone and the
truce holding. At ~$93; the market refusing to sell the premium today validates the position. Kept as the
re-escalation hedge, not a directional oil call.</li>

<li><strong>MM-2026-003 · Long Brent / Short WTI spread:</strong> discretionary close below $2.00 — physical
market giving up the Hormuz premium. At ~$3.26, near its 3.30 entry and nowhere close. Stop 1.50. Hold.</li>

<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop at 4.65%. At ~4.55%, barely moved by the ceasefire —
a hot CPI is the risk that sends it to the stop. Do not add.</li>

<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~July 15 — no discretionary close. Stop $4,250; at
~$4,344, firm and back to trading real rates. The dot plot, not the headline, is the catalyst.</li>

<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160.1 — the dollar did not slip on the
ceasefire. BoJ September hike and the intervention backstop remain the support. Size for convexity.</li>

<li><strong>MM-2026-008 · SPX put spread:</strong> hold — SPX never rallied away from it, so the hedge is still
near the money at ~45. Carry through CPI, the ECB and the dot plot; the FOMC tail is the reason it is on.</li>

<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to July 16. At +40bp, up ~165%; target +60bp. The
steepening held; the next leg is CPI/the dot plot. Hold.</li>

<li><strong>MM-2026-010 · Long DAX / short Nasdaq:</strong> stop ratio 0.943; at ~0.949 after today's narrow tech
leadership. Hold to the line, do not add. The trade is wrong if the AI cohort keeps leading through CPI — accept
the stop if it triggers.</li>

<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. Close on a hawkish ECB surprise above 1.182; base
case is sell-the-fact on a fully-priced hike. Target 1.130.</li>

<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold 30 days. The 2-year did not move today
— the thesis is unproven and waits on CPI. Close if the print is above 4.1%, which makes the level fair, not
excessive.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The ceasefire is here — is the all-clear real?",
         "a": ("Look at oil before you answer. A genuine end to a Gulf supply scare hands back the war premium, "
               "and Brent gave back exactly one dollar to ~$93. The crude market is telling you it does not trust "
               "the truce. The equity bounce was narrow — just the chips that were force-sold Friday — while the "
               "broad market, the dollar and yields barely moved. So: a real de-escalation the market does not yet "
               "believe, into a CPI print tomorrow the ceasefire does nothing to soften. We held the whole book "
               "rather than chase it.")},
        {"q": "Then why are you still long oil if the war is ending?",
         "a": ("Because the price says it isn't ending — not yet. We marked Brent to a live $93 and the Brent/WTI "
               "spread to ~$3.26, basically where we entered. The premium is intact, which validates the long as "
               "cheap insurance: the truce has already survived one wobble, and a single fresh exchange re-opens "
               "the premium toward $100 in hours. The exit is a weekly close below $87. You do not sell the fire "
               "insurance the hour the fire is contained but still smoking.")},
        {"q": "What should I actually watch tomorrow?",
         "a": ("Two prints, one day. May CPI at 8:30 — below 3.7% prices the year-end hike out and the front-end "
               "finally relaxes; above 4.1% re-arms it while oil is already falling, which is sticky core a cheaper "
               "barrel won't fix. Then Oracle after the close — the next read on whether the market will pay up for "
               "AI-capex names after Broadcom. The 2-year at 4.15% is the level that carries the first answer; "
               "Oracle's guide, not its EPS, carries the second.")},
    ],

    "ideas_note": (
        "<p>No new idea today — and that is the call. We marked the entire book to live levels and found a tape "
        "that refused to move on a ceasefire: oil held its premium, the broad market was flat-to-down, and the "
        "front-end did not budge. That validated the oil longs (we did <em>not</em> close the Brent/WTI spread — "
        "it is ~$3.26, near entry, nowhere near its exit) and left the rates trades waiting on tomorrow's CPI. "
        "With an 8:30 inflation print that can settle the week by lunch, and a book that already owns both tails, "
        "the highest-expected-value action is to add nothing. Forcing a trade into a binary is the opposite of "
        "edge.</p>"
    ),

    "event_radar_note": (
        "<p>Three binary events sit inside the next eight sessions and resolve every open position's thesis: May "
        "CPI tomorrow (the deciding print on the year-end hike — the ceasefire does nothing to it), the ECB on "
        "Thursday (+25bp locked; the press conference sets the euro), and Kevin Warsh's first FOMC dot plot on "
        "June 16-17. The trades positioned to get paid on either resolution — the 2s10s steepener and the short "
        "2-year — are already on; today we added nothing into the print.</p>"
    ),

    "vix_term": [
        {"label": "VIX9D", "value": 16.0},
        {"label": "VIX",   "value": 18.9},
        {"label": "VIX3M", "value": 20.0},
        {"label": "VIX6M", "value": 21.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.15, 3)},
        {"label": "5Y",  "value": 4.36},
        {"label": "10Y", "value": round(_g("us10y") or 4.55, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 5.02, 3)},
    ],

    "new_ideas":          new_ideas_cards,
    "pre_position_ideas": prepos_cards,
}

# ── Render: legacy single page (output.html) ───────────────────────────────
book.step("Rendering output.html")
html_out = book.build_html(brief, trades, regime_log)
with open(book.OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_out)
book.log(f"wrote {len(html_out):,} bytes -> {book.OUTPUT_PATH}")

# ── Render: 4-page Shark Tank app ──────────────────────────────────────────
book.step("Rendering Shark Tank pages + fragments")
shark_format.render_all(brief, trades, regime_log)

# ── Persist state ──────────────────────────────────────────────────────────
book.step("Saving trades.json + regime_log.json")
book.save_json(book.TRADES_PATH, trades)
book.save_json(book.REGIME_PATH, regime_log)

book.step("Done")
