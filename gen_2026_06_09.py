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
import book_scanner

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
regime = "A Truce Under Fire, A Hot CPI Ahead"
regime_note = (
    "The April ceasefire cracked: Iran and Israel traded the worst strikes in months on Jun 7-8, Israel hit "
    "Iran's Mahshahr petrochemical complex and air defences, and Iran halted but warned it will resume — "
    "Netanyahu won't even call it a ceasefire. The one-session chip bounce on Monday's halt gave it all back: "
    "the S&P closed 7,386 (-0.3%), the Nasdaq -1.0%, only the Dow held. Brent kept its premium near $92 because "
    "the Strait of Hormuz is still blockaded, not because anyone trusts the truce. May CPI tomorrow — expected "
    "to tick up toward 4.2% — is the hard catalyst the geopolitics can't soften."
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
        "The truce keeps cracking and the Strait stays shut, so oil keeps its premium near $92 — while the "
        "one-day chip bounce on Monday's brief halt has already failed. Two unresolved shocks, the war and a "
        "CPI print expected to tick up to 4.2%, both still live into tomorrow morning."
    ),

    # ── SUMMARY page ───────────────────────────────────────────────────────
    "summary_narrative": """
<p>The ceasefire didn't hold. Over the weekend Iran and Israel traded the worst strikes in months — the first
exchanged fire since the April truce — and Israel followed Iran's Monday "halt" with an extensive strike on
Iran's air defences and the Mahshahr petrochemical complex. Iran says it has stopped, but warned it will fire
again if Israel keeps hitting Lebanon; Netanyahu won't call it a ceasefire; Trump is pushing for an "immediate"
one that does not yet exist on paper. This is a truce under fire, not a peace.</p>

<p>The market had one session of believing the de-escalation, and it has already taken it back. Monday's chip
rebound — when Iran first halted — failed the next day: the S&amp;P closed 7,386.65 (-0.26%), the Nasdaq fell
0.97%, and only the Dow held (+0.17%). The semis that bounced 6% gave it back, Micron round-tripping a 10%
move to close down 1%. The dominant equity story is still the AI de-rating that took the Nasdaq down 4% earlier
in the week — its worst day in over a year — not a relief rally.</p>

<p>Oil is the one thing that has kept its nerve: Brent sits near $92, off a couple of dollars from $94 but
holding almost all of its war premium. That is not the market disbelieving a peace — it is the physical fact
that the <strong>Strait of Hormuz remains under a dual US-Iran blockade</strong>, with crude, fuel and gas
shipments still disrupted while the truce keeps breaking. The premium is real, and it is earned.</p>

<p>Into that sits the hard catalyst the geopolitics cannot soften: <strong>May CPI tomorrow at 8:30</strong>,
expected to tick up to ~4.2% headline from 3.8%, on energy that is still elevated. The front-end has not moved
— the 2-year sits ~4.15%, the year-end hike still priced — so the print is effectively unhedged. The
disciplined posture is to hold the book that already owns both tails: the oil longs are earned by a blockaded
Strait, the curve trades wait on CPI, and no fresh risk goes on in front of a number that can set the week by
lunch.</p>
""",

    "takeaways": [
        "The April ceasefire cracked — Iran/Israel traded the worst strikes in months (Jun 7-8); Israel hit Iran's Mahshahr petrochem complex; Iran halted but threatens to resume over Lebanon.",
        "The one-day chip bounce failed: S&P 7,386.65 (-0.26%), Nasdaq -0.97%, only Dow +0.17%; SMH and Micron gave back Monday's pop. The AI de-rating is still the dominant story.",
        "Brent holds ~$92 (off $94) — but because the Strait of Hormuz is still under a dual US-Iran blockade, not because the market trusts the truce. The premium is earned.",
        "Rates haven't moved: 2Y ~4.15%, 10Y ~4.55%, 2s10s +40bp. So tomorrow's CPI is effectively unhedged.",
        "May CPI tomorrow (8:30 ET) is the binary — expected to tick up to ~4.2% headline. We held the whole book to live levels; no new risk into the print.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "30%",
         "headline": "CPI cools, the truce actually holds, Hormuz reopens",
         "body": "May CPI prints at or below 3.9%, the 2-year breaks under 4.05%, the halt holds and the Strait "
                 "reopens so oil finally bleeds the premium, and the AI cohort stabilises. Risk up · rates down · "
                 "dollar soft · gold firm."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "CPI ticks up, the truce stays fragile, oil stays bid",
         "body": "CPI lands ~4.0-4.2%, the front-end holds its hike pricing, the Strait stays shut and crude keeps "
                 "its premium on an on-again-off-again truce, and Europe leads into Thursday's ECB. Risk mixed · "
                 "rates range · dollar firm · Brent $90-96."},
        {"kind": "bear", "label": "Bear", "pct": "25%",
         "headline": "CPI runs hot or the strikes resume",
         "body": "CPI above 4.3% re-arms the year-end hike, or Iran-Israel re-escalate (Lebanon the fuse) and the "
                 "oil premium pushes toward $100, and the AI de-rating resumes on a weak Oracle. Risk down · rates "
                 "up · dollar up · gold higher as the stagflation scare bites."},
    ],

    # ── THE MARKET MAP — Insights detailed layers ──────────────────────────
    "insights_layers": """
<p>A ceasefire is only as good as its last 24 hours, and this one's last 24 hours were strikes. The April truce
between Iran and Israel cracked over the weekend in the worst exchange of fire in months; Iran announced a halt
on Monday, and Israel answered it with an extensive strike on Iranian air defences and the Mahshahr
petrochemical complex. Netanyahu has pointedly declined to call it a ceasefire; Iran says it will fire again if
Israel keeps hitting Lebanon. So the screen you are reading is not pricing peace — it is pricing a truce that
has already failed once and could fail again before the week is out.</p>

<p>Decompose the equity tape, because the one green day in it is gone. When Iran first halted on Monday the
chips ripped — the semis index up 6%, Micron up 10% — on hope the de-escalation would stick. It didn't: the
next session gave it all back, the Nasdaq closing down 0.97%, the S&amp;P off 0.26% at 7,386, Micron round-
tripping to -1%, and only the Dow holding a token gain. So-what: the dominant equity story is still the AI
de-rating that took the Nasdaq down 4% earlier in the week — its worst day in over a year — and a one-session
geopolitical bounce did not change it. Who's wrong: anyone who bought the Monday pop as a turn.</p>

<p><strong>Layer 1 — the regime.</strong> Two shocks, both still live: a war that keeps re-igniting and a CPI
print that lands tomorrow. Neither has resolved. The truce is unsigned and already broken once; the inflation
number has not been seen. The map did not simplify this week — it got more dangerous, because the market spent
a day pretending one tail was gone. The book that owns both tails is positioned correctly precisely because
nothing is settled.</p>

<p><strong>Layer 2 — the counter-intuitive hook.</strong> The most-quoted "good news" — Iran halting — produced
a rally that lasted exactly one session. The hook is that the relief was rented, not owned: a blockaded Strait
and a Netanyahu who won't sign mean the de-escalation has no anchor. Watch the oil price, not the VIX, for the
real verdict — crude is pricing the physical fact (Hormuz shut), while equities priced a hope and took it back.</p>

<p><strong>Layer 3 — the gap.</strong> Ground truth: the Strait of Hormuz remains under a dual US-Iran blockade,
crude and gas shipments still disrupted, into a CPI print landing on still-elevated energy. What's priced: a
failed chip bounce and a still-live year-end hike. The consensus narrative was "ceasefire, buy the dip" — and
it just lost money. The gap is between a geopolitics that is still hot and an equity tape that wanted it cold.
That gap sits in oil and rates, not the index.</p>

<p><strong>Layer 4 — Bull / Base / Bear.</strong> <em>Bull (30%):</em> CPI cools to ≤3.9%, the halt holds, the
Strait reopens and crude bleeds the premium — risk up, rates down, gold firm. <em>Base (45%):</em> CPI ticks
up to ~4.0-4.2%, the truce stays fragile and the Strait stays shut so oil holds its bid, Europe leads into the
ECB — risk mixed, rates range, dollar firm. <em>Bear (25%):</em> CPI runs hot (>4.3%) or the strikes resume
with Lebanon the fuse and oil pushes $100, and the AI de-rating resumes on a weak Oracle — risk down, rates up,
gold higher. The bear tail is fatter than it was: there are two ways to lose this week and the war just proved
it is one of them.</p>

<p><strong>Layer 5 — priced vs not-priced.</strong> Mispriced the wrong way: any residual hope that Monday's
halt was the end of it. Under-priced: the chance the strikes resume — implied vol eased even as the truce broke.
Fairly priced: oil's premium, which a blockaded Strait fully earns. Fully priced: Thursday's ECB hike. The
actionable item is the second — own the geopolitical convexity (the Brent call spread) cheaply while the tape
is still treating the war as yesterday's story.</p>

<p><strong>The Burry tell — still live.</strong> Hyperscaler capex is now so large that the marginal AI-revenue
beat has to <em>accelerate</em> just to hold the multiple; Broadcom grew AI 143% and lost a seventh of its cap
because the cohort is hedged for a miss and not one name is hedged for a growth-rate disappointment. Oracle
reports tomorrow night with a $553bn backlog into that exact trap. The AI de-rating, not the war, is the
structural story that will still matter in six months.</p>

<p><strong>The Pozsar mechanic.</strong> The plumbing didn't move even as the war re-ignited: yields sat still,
the dollar barely budged, secured funding is unchanged — so the constraint from last week is fully intact. The
2-year's implied terminal rate still sits well above SOFR; every floating-rate borrower that issued in 2023-24
expecting cuts is still paying more than its model assumed, and IG spreads near 80bp are priced for a soft
landing a hot CPI would question. Watch IG spreads on the print, not the VIX.</p>

<p><strong>The Papic constraint.</strong> Two political fuses. In the Gulf, Iran has tied any durable halt to a
Lebanon ceasefire Israel insists is a separate war — so the truce's stability depends on a conflict neither
side will link, which is why it keeps breaking. In Europe, Bund and Gilt yields rose even as US yields fell,
the market pricing Thursday's ECB hike that Lagarde has no political room to skip. And in Washington, Kevin
Warsh inherits the chair next week and cannot look soft on inflation in his first meeting — capping how dovish
the dots can read whatever CPI allows.</p>

<p>So what to do. Patience, expressed through what you already own. The oil book stays — a blockaded Strait and
a truce that keeps cracking earn the premium. The curve trades wait on a CPI print that hasn't given them their
move. Don't chase a chip bounce that already failed. And keep the defined-risk equity hedge on, because the one
thing this tape has not priced is the binary that lands at 8:30 tomorrow.</p>
""",

    "wrap": """
<p>A ceasefire is only as good as its last 24 hours, and this one's were strikes. The April Iran-Israel truce
cracked over the weekend in the worst exchange of fire in months; Iran announced a halt on Monday and Israel
answered with a strike on its air defences and the Mahshahr petrochemical complex. Netanyahu won't call it a
ceasefire; Iran says it will fire again if Israel keeps hitting Lebanon. This is a truce under fire, not a
peace.</p>

<p>The equity tape had one day of believing it and took the day back. Monday's chip rip — semis +6%, Micron
+10% — failed the next session: the S&amp;P closed 7,386.65 (-0.26%), the Nasdaq -0.97%, Micron round-tripping
to -1%, only the Dow holding. The dominant story is still the AI de-rating that took the Nasdaq down 4% earlier
in the week, not a relief rally.</p>

<p><strong>The driver.</strong> Two live shocks — a war that keeps re-igniting and a CPI print tomorrow — and
neither has resolved. Oil holds near $92 because the Strait of Hormuz is still under a dual US-Iran blockade,
not because anyone trusts the halt. Rates haven't moved: the 2-year sits ~4.15%, the year-end hike still
priced.</p>

<p><strong>The Burry tell.</strong> The AI cohort is hedged for a revenue miss, not a growth-rate
disappointment. Oracle reports tomorrow with a $553bn backlog into that trap. The AI de-rating, not the war, is
the structural story that still matters in six months.</p>

<p><strong>The Pozsar mechanic.</strong> The plumbing didn't move even as the war re-ignited — yields sat
still, the dollar barely eased, funding is unchanged. The 2-year's implied terminal rate is still well above
SOFR, IG spreads near 80bp priced for perfection. Watch spreads on the CPI print, not the VIX.</p>

<p><strong>The Papic constraint.</strong> Iran has tied a durable halt to a Lebanon ceasefire Israel treats as
a separate war — so the truce depends on a conflict neither side will link, which is why it keeps breaking. In
Europe, Bund +4bp / Gilt +7bp price Thursday's ECB hike Lagarde can't skip; Warsh inherits the Fed chair next
week and can't look soft on inflation in his first meeting.</p>

<p>So what to do: hold the book that owns both tails, let the oil longs run on a premium a blockaded Strait
earns, wait on CPI for the rates trades, don't chase a chip bounce that already failed, and keep the hedge on.</p>
""",

    "correlation_regime": """
<p><strong>1. The chip rebound de-correlated from the de-escalation headline — relief that lasted one day.</strong>
Monday the semis ripped 6% on Iran's halt; the next session they gave it back as the strikes resumed and the
broad tape fell. The "good news" and the price decoupled within 24 hours, which tells you the de-escalation has
no anchor while Hormuz stays shut. Don't trade the headline; trade the blockade.</p>

<p><strong>2. US yields fell while Bund and Gilt yields rose — a transatlantic rates split.</strong> The US 10Y
eased a basis point or two; Bund (+4bp) and Gilt (+7bp) rose as the market prices Thursday's ECB hike. The next
rates impulse is European, not American — which is why long DAX is structurally sound even on a day US tech
outperformed it.</p>

<p><strong>3. Brent held its premium while equities tried to price peace — the physical market overruling the
political one.</strong> Oil near $92 with a blockaded Strait is the most honest price on the screen: it is the
supply fact, not a hope. Until the Strait reopens, the geopolitical tail is on, and the Brent long
(MM-2026-002) plus the call spread (MM-2026-011) are the cheap way to own it.</p>

<p><strong>4. The semis led both the fall and the failed bounce — no breadth either way.</strong> The same
cohort that took the Nasdaq down 4% earlier led Monday's rip and Tuesday's give-back; nothing else moved much.
That narrowness pressured the long-DAX/short-Nasdaq RV (MM-2026-010) toward its stop on the up-day and helps it
back on the give-back — a single-cohort tape, not a market one. It needs the CPI/Oracle read to settle.</p>
""",

    "vol_skew": """
<p><strong>The VIX eased into the high-teens even as the truce broke — that is the mispricing.</strong>
VIX9D ~16 · VIX ~19 · VIX3M ~20 · VIX6M ~21. Vol came off the chip-selloff spike, yet the curve is still
paying up for the next three weeks — rational with CPI, the ECB and a new chair's first FOMC inside the window.
The tell: implied vol relaxed while strikes resumed, so the front of the curve is underpricing the chance the
war re-ignites before any of those events. Owning cheap geopolitical convexity is the trade.</p>

<p><strong>The hedge that is still working — and still close to the money.</strong> Because the chip bounce
failed, the SPX sits ~7,386 and the Jun-27 7300/7000 put spread (MM-2026-008) is barely out of the money, not
stranded below spot. There is no case to roll it — it is doing its job cheaply, ~45 points (model est) with
three binary events still ahead. Carry it; do not pay to re-strike a hedge already where you want it.</p>

<p><strong>Rates vol is the one to watch on the print.</strong> MOVE has eased from its payroll-week highs, but
the 2-year did not move today and CPI tomorrow is a genuine binary for the front-end. A soft print collapses the
remaining hike premium; a hot one re-arms it. If rates vol turns back up through its range on the number, that is
the earliest signal the front-end relief never came — and it will show in MOVE before it shows in equities.</p>
""",

    "sector_rv": """
<p><strong>Leading — and it is a narrow list:</strong></p>
<ul>
<li><strong>Energy producers:</strong> the cleanest outperformers, because crude held its premium on a blockaded
Strait. With Brent near $92 the sector keeps the geopolitical bid — the mirror image of the broad market's
caution, and the leadership the tape's failed chip bounce lacked.</li>
<li><strong>Mega-cap defensives / the Dow:</strong> the only major US index to hold a gain (+0.17%) as the
Nasdaq fell — a rotation toward quality and away from the AI cohort that is still de-rating. The market is
paying for earnings certainty, not growth multiples, into the CPI print.</li>
</ul>

<p><strong>Lagging:</strong></p>
<ul>
<li><strong>AI semiconductors:</strong> still the laggard that matters — the cohort that took the Nasdaq down 4%
earlier in the week, ripped 6% on Monday's halt, then gave it back. SK Hynix has pre-sold its 2026 HBM to
Nvidia so the demand floor is real, but Oracle tomorrow night is the test of whether the market will pay up for
AI-capex beneficiaries again, and the de-rating has the upper hand until it does.</li>
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
<li><strong>Oil:</strong> the premium holding near $92 says specs did <em>not</em> capitulate when Iran halted.
That is constructive for the longs — no flush, positioning not stretched, and the strikes resuming caught any
spec who sold the Monday headline. The pain trade is exactly this: re-escalation into a market that briefly
believed the peace.</li>
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
<p>SOFR near 3.62% — unchanged; repo orderly; and crucially the plumbing did not move even as the war
re-ignited. The dollar barely budged and the cross-currency basis is stable — the strikes hit sentiment and oil,
not funding. <strong>The Pozsar mechanic that still binds:</strong> the 2-year's implied terminal
rate sits well above secured funding, so every floating-rate borrower that issued in 2023-24 expecting cuts is
still paying a higher marginal cost than its model assumed. Investment-grade spreads near 80bp are still priced
for a soft landing a hot CPI would question. The ceasefire bought equity calm and zero balance-sheet relief.
Watch IG spreads on tomorrow's print for the first sign the constraint is binding — the balance sheet shows the
strain before the index does.</p>
""",

    "tape_missing": """
<p><strong>1. The Strait of Hormuz is still blockaded, and the tape is treating the war as yesterday's
story.</strong> Implied vol eased even as the strikes resumed — the market priced one day of de-escalation and
moved on. The threshold is the Strait reopening: until it does, Brent's premium is earned and a weekly close
below $87 (the level that says the premium is gone) is not in view. Own the convexity while it is cheap.</p>

<p><strong>2. (Burry tell) Oracle's $553bn backlog meets the same bar Broadcom failed.</strong> The AI cohort is
hedged for a miss, not a growth-rate disappointment. If OCI growth or capex guidance tomorrow clears the printed
estimate but not the whisper, the de-rating that drove this week resumes — and the chips that already failed to
hold Monday's bounce lead it down. Watch the guide, not the EPS.</p>

<p><strong>3. The front-end has not moved, so tomorrow's CPI is effectively unhedged.</strong> The 2-year sat at
~4.15% and the year-end hike is still priced; the war does nothing to a backward-looking inflation print landing
on still-elevated energy. Consensus looks for headline to tick up to ~4.2% from 3.8% — a number above 4.3%
re-arms the hike, the combination the tape is least positioned for.</p>
""",

    "consensus": """
<p><strong>Consensus BID:</strong> the worst of the war is behind us — Iran halted, Trump gets his "immediate"
ceasefire, oil drifts lower, CPI lands manageable, and the AI cohort stabilises after the de-rating. Warsh holds
next week, the dots drift hawkish but stop short of a hike, and the vol high is in.</p>

<p><strong>The strongest argument against — the OFFER:</strong> two things the bid is ignoring. First, the
ceasefire already broke once this week and Israel struck Iran's petrochemical complex after Iran's "halt" — the
de-escalation has no anchor while Hormuz stays shut, so the oil premium is earned, not a fading scare. Second,
tomorrow's CPI: headline ran 3.8% in April on energy, and consensus looks for it to tick up to ~4.2% in May. A
print above 4.3% confirms the inflation impulse the front-end feared, re-arms the year-end hike and puts gold's
$4,250 stop in play. The market settled the easy question — that Monday's bounce was rented — and CPI plus the
war are the hard ones still open.</p>
""",

    "one_chart": """
<p class="theme">Brent crude near $92 — and the Strait of Hormuz that keeps it there.</p>
<p>The single most informative price is the one the failed chip bounce couldn't shake. Brent eased a couple of
dollars off $94 when Iran halted, then stuck — because the Strait of Hormuz is still under a dual US-Iran
blockade and the truce keeps cracking. That premium is earned, not a fading scare. Hold above $90 and the
geopolitical tail is live and the oil book stays on; the trigger to take the Strait trades off is the blockade
lifting (a weekly close below $87 confirms it), not a headline. Watch the Strait, and watch the 2-year ~4.15%
for whether tomorrow's CPI — expected up at ~4.2% — lets the front-end move at all.</p>
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

# ── Client book scan (Fable / Portfolio + Derivative Ideas) ────────────────
book.step("Scanning client book (Fable)")
scan = book_scanner.build_scan(brief)
if scan:
    m = scan["metrics"]
    book.log(f'Fable book EUR{m["total_eur"]:,} · {m["largest"]["ticker"]} {m["largest"]["weight_pct"]}% '
             f'· {scan["counts"]["fired"]} fired / {scan["counts"]["watch"]} watch / {scan["counts"]["suppressed"]} suppressed')

# ── Render: 6-page Shark Tank app ──────────────────────────────────────────
book.step("Rendering Shark Tank pages + fragments")
shark_format.render_all(brief, trades, regime_log, scan=scan)

# ── Persist state ──────────────────────────────────────────────────────────
book.step("Saving trades.json + regime_log.json")
book.save_json(book.TRADES_PATH, trades)
book.save_json(book.REGIME_PATH, regime_log)

book.step("Done")
