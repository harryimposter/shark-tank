#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-09 (Tuesday).

The story since June 8: Iran and Israel halted attacks and President Trump began
brokering an immediate ceasefire. Brent unwound the war premium from ~$98 toward
the low-$90s; equities staged a relief rally; the VIX slipped back below 19; gold
steadied near $4,330; the dollar eased off a two-month high. But Friday's actual
shock was the rates repricing, not the oil — and May CPI (Jun 10), Oracle (Jun 10),
the ECB (Jun 11) and new Fed Chair Warsh's first dot plot (Jun 16-17) are all still
in front of us. Book action: closed the dead Brent/WTI spread; rolled the equity
hedge up and out. Voice: measured, analytical — decompose the headline, land on
so-what.

Run:  python gen_2026_06_09.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book
import shark_format

trades     = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

# ── Regime ─────────────────────────────────────────────────────────────────
regime = "A Ceasefire, Not an All-Clear"
regime_note = (
    "Iran and Israel halted attacks and Trump is pushing an immediate ceasefire; Brent gave back "
    "the war premium from ~$98 toward the low-$90s and equities staged a relief rally. But the shock "
    "that de-rated the tape on Friday was the rates repricing, not the oil. May CPI tomorrow, the "
    "ECB on Thursday and Warsh's first dot plot next week are still unresolved. The geopolitical "
    "tail eased; the inflation tail did not."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark the book to market (June 9 levels) ────────────────────────────────
# Survivors marked; MM-2026-003 closed discretionarily below; gold held (min-hold).
levels = {
    "MM-2026-001": 1.646,    # Short EURAUD — roughly flat
    "MM-2026-002": 90.20,    # Long Brent — war premium round-tripped, kept as truce hedge
    "MM-2026-004": 4.50,     # Short 10Y yield — yield eased on the oil unwind
    "MM-2026-005": 4330.0,   # Long gold (pre-position) — steadied, min hold to ~Jul 15
    "MM-2026-007": 159.20,   # Short USDJPY — dollar slipped, back below 160
    "MM-2026-008": 50.0,     # SPX Jun-27 put spread — gave back gains into the relief rally
    "MM-2026-009": 0.40,     # 2s10s steepener — bull-steepened further
    "MM-2026-010": 0.967,    # Long DAX / short Nasdaq — relief rally favoured US tech
    "MM-2026-011": 1.30,     # Brent call spread — upside tail deflated, defined risk kept
    "MM-2026-012": 1.158,    # Short EURUSD — roughly flat into the ECB
    "MM-2026-013": 4.10,     # Short 2Y yield — working as hike pricing eased
}
book.step("Marking open trades to market")
book.mark_to_market(trades, levels)

# Discretionary close: the Brent/WTI spread — the Hormuz premium it was built to
# capture is gone now that the Strait risk is de-escalating; it traded through the
# $2.00 line we set as the exit.
book.step("Discretionary close MM-2026-003")
book.discretionary_close(
    trades, "MM-2026-003", 1.95,
    reason="Ceasefire removes the Hormuz-specific Brent premium the spread was meant to own; "
           "traded through the $2.00 exit. Banked the loss, stand aside.",
)

# ── One new idea: roll the equity hedge up and out ─────────────────────────
# The Jun-27 put spread (MM-008) paid off and is now struck well below a higher
# spot. Into three events in eight sessions — CPI, ECB, and Warsh's first FOMC —
# keep a defined-risk hedge, re-centred to the new SPX level. Measured, not a call.
new_ideas_raw = [
    {
        "asset_class": "Derivatives",
        "trade": "Buy SPX Jul-3 7200/6950 put spread (re-centre the hedge)",
        "structure": "put spread",
        "entry": 42.0,
        "stop": 0.0,
        "target": 250.0,
        "conviction": 6,
        "conviction_breakdown": {"gap": 1, "catalyst": 2, "positioning": 1,
                                 "confirmation": 1, "stop_quality": 1},
        "horizon": "24 days",
        "min_hold_days": 0,
        "thesis": (
            "The Jun-27 hedge (MM-2026-008) did its job and is now struck a long way below a higher "
            "spot after the relief rally. Three binary events sit inside the next eight sessions — May "
            "CPI tomorrow, the ECB on Thursday, and Kevin Warsh's first FOMC with a fresh dot plot on "
            "the 16-17th. This is not a directional bear call; it is paying ~0.5% of notional to keep "
            "defined-risk protection re-centred near the money while the cheaper, deeper hedge rolls "
            "off. Trim the old spread into strength, carry the new one through the event cluster."
        ),
    },
]
book.step("Ingesting new idea MM-2026-014")
book.ingest_ideas(trades, new_ideas_raw, "reactive")

# Pull the freshly-minted card(s) back out for rendering.
new_today_ids   = {"MM-2026-014"}
new_ideas_cards = [t for t in trades["open"] if t["id"] in new_today_ids]
prepos_cards    = []   # no new pre-position today

# ── Earnings intelligence (Finnhub-sourced; earnings_data.md) ──────────────
earnings_ideas = [
    {
        "ticker": "ORCL", "company": "Oracle Corp",
        "report_date": "2026-06-10", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 5, "conviction_label": "Medium conviction",
        "conviction_rationale": None,
        "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "key_bullets": [
            "OCI grew 84% YoY in Q3 to $4.9bn; remaining performance obligations $553bn, +325% YoY.",
            "Finnhub consensus EPS $1.58; Oracle's own March guide pointed to $1.96-2.00 — a wide gap.",
            "40 buy vs 8 hold; the bull case is the backlog, the test is converting it without straining capex.",
        ],
        "what_moves_it": (
            "Whether OCI growth and capex guidance clear the *whisper*, not just the printed estimate — "
            "the same bar Broadcom missed at a rich multiple last week."
        ),
        "client_talking_point": (
            "Oracle is the next read on whether the AI-capex multiple holds after AVGO. The backlog is "
            "real; the risk is a guide that is merely very good into a tape that re-rates 'very good.' "
            "We are not pre-positioning into the print."
        ),
    },
    {
        "ticker": "ADBE", "company": "Adobe Inc",
        "report_date": "2026-06-11", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None,
        "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 1, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "key_bullets": [
            "Consensus EPS $5.94; the stock sits near its 52-week low (224) versus a 421 high — sentiment is washed out.",
            "Split book: 19 buy / 22 hold / 4 sell — the market is undecided on AI as friend or threat.",
            "The question is net-new Firefly/AI monetisation, not headline EPS, which the model already knows.",
        ],
        "what_moves_it": (
            "Evidence that generative-AI is additive to ARR rather than cannibalising Creative Cloud seats. "
            "Guidance tone outweighs the print."
        ),
        "client_talking_point": (
            "Adobe is the cleanest test of the 'is AI a tax or a tailwind for incumbents' debate. Beaten-down "
            "into the print, so the asymmetry is in the guide, not the quarter. Hold, do not chase either way."
        ),
    },
    {
        "ticker": "SAIL", "company": "SailPoint Inc",
        "report_date": "2026-06-09", "report_timing": "BMO",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None,
        "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "key_bullets": [
            "Identity-security; 26 buy / 3 hold / 1 sell — strong sell-side support at a $10bn cap.",
            "Revenue growth 24% YoY (TTM); a serial beater (last four surprises all positive, two large).",
            "Reports before the open today — a small-cap read on whether security spend is still defensive.",
        ],
        "what_moves_it": "ARR growth and net-retention — the durability metrics, not the penny EPS.",
        "client_talking_point": (
            "A small but clean tell on enterprise software demand into a higher-rate tape. Not a position; "
            "a data point for the broader software read."
        ),
    },
]

# ── Brief ──────────────────────────────────────────────────────────────────
brief = {
    "regime":      regime,
    "regime_note": regime_note,

    # ── Dashboard (The Open) ───────────────────────────────────────────────
    "dashboard": [
        {"name": "S&P 500",      "level": "~7,510",    "chg": "+1.1%",  "dir": "up"},
        {"name": "Nasdaq 100",   "level": "~26,900",   "chg": "+1.5%",  "dir": "up"},
        {"name": "Dow",          "level": "~51,300",   "chg": "+0.9%",  "dir": "up"},
        {"name": "DAX",          "level": "~25,050",   "chg": "+0.5%",  "dir": "up"},
        {"name": "Nikkei 225",   "level": "~65,500",   "chg": "+2.3%",  "dir": "up"},
        {"name": "FTSE 100",     "level": "~10,470",   "chg": "+0.5%",  "dir": "up"},
        {"name": "EURUSD",       "level": "1.1580",    "chg": "+0.4%",  "dir": "up"},
        {"name": "GBPUSD",       "level": "unverified","chg": "",       "dir": "unverified"},
        {"name": "USDJPY",       "level": "159.20",    "chg": "-0.7%",  "dir": "down"},
        {"name": "USDCNH",       "level": "unverified","chg": "",       "dir": "unverified"},
        {"name": "DXY",          "level": "~99.9",     "chg": "-0.6%",  "dir": "down"},
        {"name": "US 10Y",       "level": "4.50%",     "chg": "-4bp",   "dir": "down"},
        {"name": "US 2Y",        "level": "4.10%",     "chg": "-6bp",   "dir": "down"},
        {"name": "Bund 10Y",     "level": "~2.9%",     "chg": "ECB Thu","dir": "flat"},
        {"name": "2s10s",        "level": "+40bp",     "chg": "+2bp",   "dir": "up"},
        {"name": "WTI Crude",    "level": "~$86.8",    "chg": "-5.0%",  "dir": "down"},
        {"name": "Brent Crude",  "level": "~$90.2",    "chg": "-4.6%",  "dir": "down"},
        {"name": "Gold (XAU)",   "level": "~$4,330",   "chg": "-0.5%",  "dir": "down"},
        {"name": "VIX",          "level": "~17.2",     "chg": "-8.5%",  "dir": "down"},
        {"name": "SOFR",         "level": "~3.62%",    "chg": "",       "dir": "flat"},
        {"name": "MOVE",         "level": "~108",      "chg": "easing", "dir": "down"},
    ],

    "dominant_theme": (
        "The relief rally is spending a peace dividend on a problem peace does not solve. Oil gave back "
        "its war premium and equities exhaled — but Friday's selloff was authored by the front-end of the "
        "US curve, and that bill comes due tomorrow at 8:30 with May CPI."
    ),

    # ── SUMMARY page (the overnight read) — measured, lands on so-what ──────
    "summary_narrative": """
<p>Markets got the headline they wanted overnight. Iran and Israel agreed to stop firing at each other,
President Trump put his name to an immediate ceasefire, and the oil market did what oil markets do when a
supply scare passes — it handed back the premium almost as fast as it took it. Brent, which printed above
$98 intraday on Monday, is back near $90; West Texas is in the high-$80s; the VIX has slipped under 18; and
equities are higher for a second session. On the surface, the storm has passed.</p>

<p>It is worth being precise about what actually moved the tape last week, because the relief rally is
quietly answering the wrong question. Friday's 2.6% fall in the S&amp;P and 4.2% fall in the Nasdaq were not
a war story. They were a rates story — 172,000 jobs against an 80,000 consensus, two months of upward
revisions, and a front-end that lurched toward pricing a Fed <em>hike</em> by year-end. Oil added a second
shock over the weekend, but it was always the smaller of the two. The ceasefire retires the oil shock. It
does nothing about the 2-year Treasury, and it does nothing about the May CPI print that lands tomorrow
morning.</p>

<p>So the honest read is narrower than the tape's mood: a genuine de-escalation has removed a real tail,
and that is worth a relief rally and worth taking the Strait-of-Hormuz trades off the book. But the same
ceasefire that lifts equities also pulls oil lower, which pulls forward inflation lower, which — if
tomorrow's CPI cooperates — is the disinflation the bond market has been waiting for. The cleanest
expression of today is not "buy the all-clear." It is to fade the year-end-hike panic in the front end,
keep a re-centred equity hedge on through a three-event fortnight, and let the print, not the headline,
set the direction.</p>
""",

    "takeaways": [
        "The ceasefire retires the oil tail; it does not retire the rates tail — and rates, not oil, drove last week's selloff.",
        "Brent round-tripped its entire war premium toward $90; we closed the Brent/WTI spread and took the Strait trades off risk.",
        "Front-end hike pricing for December has eased from ~70% Friday toward the high-40s as the oil-inflation impulse fades.",
        "May CPI (Jun 10, 8:30 ET) is now the single binary that matters; consensus near 3.8% with the Cleveland Fed nowcast closer to 4.0%.",
        "Oracle tomorrow night is the next read on whether the AI-capex multiple holds after Broadcom's guide-miss de-rating.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "CPI cools, the front-end relaxes, the AI dip was a gift",
         "body": "May CPI prints at or below 3.7%, the 2-year falls back through 4.05%, and the year-end hike "
                 "is priced out. Equities extend the relief rally, Oracle's backlog reassures, and the AI cohort "
                 "re-rates. Risk up · rates down · dollar soft · gold firm."},
        {"kind": "base", "label": "Base", "pct": "50%",
         "headline": "CPI roughly in line, a hawkish hold, Europe leads",
         "body": "CPI lands 3.8-4.0%, Warsh's Fed holds in June and lets the dots drift hawkish without "
                 "committing to a 2026 hike. The US chops as Europe outperforms into an ECB hike. Risk mixed · "
                 "rates range · dollar firm · oil drifts lower on the truce."},
        {"kind": "bear", "label": "Bear", "pct": "15%",
         "headline": "CPI runs hot, the dots show a hike, the truce wobbles",
         "body": "CPI above 4.1% revives the year-end-hike trade, a renewed missile exchange re-opens the oil "
                 "premium, and the AI de-rating turns into a sector-wide de-gross. Risk down hard · rates up · "
                 "dollar up · gold down then up as the growth scare arrives."},
    ],

    # ── THE MARKET MAP — Insights page detailed layers (the centrepiece) ───
    "insights_layers": """
<p>Every relief rally tells you what the market was most afraid of, by watching what it buys back first.
Overnight it bought back equities and sold oil — which is to say it treated the weekend's Hormuz scare as
the thing that broke the tape on Friday. It was not. The Strait was a frightening sideshow; the main event
was a labour-market print that pushed the front-end of the US curve toward a hike, and a discount rate that
moved against the longest-duration assets in the index two days after Broadcom reminded everyone how richly
those assets are priced. The ceasefire is real and it matters. It just does not solve the problem the tape
actually has.</p>

<p>Decompose the move, because the averages flatter it. Friday's 2.6% in the S&amp;P and 4.2% in the Nasdaq
were not a growth scare — they were the opposite, a <em>strength</em> scare. The economy printed too hot,
the 2-year jumped to a sixteen-month high near 4.16%, and the assets with the most duration baked into them
repriced hardest. Today's recovery has the front-end easing — the 2-year back toward 4.10%, December-hike
odds slipping from roughly 70% on Friday toward the high-40s — precisely because the ceasefire pulls oil,
and therefore forward inflation, lower. The same headline is doing two jobs at once: lifting risk, and
quietly relieving the rates pressure that caused the selloff in the first place. That is the genuinely
constructive part of today, and it is not the part the equity tape is celebrating.</p>

<p><strong>Layer 1 — the regime.</strong> Call it what it is: a <em>two-tailed tape with one tail removed</em>.
For a week the book carried two shocks — an oil-supply tail and a rates-repricing tail — and was paid to own
both sides of the binary. The ceasefire amputates the oil tail. What remains is a single, cleaner driver: the
path of the front-end into tomorrow's CPI and next week's first dot plot under a new Fed chair. The map
simplifies. That is good for clarity and bad for anyone still positioned for the geopolitical premium to
persist.</p>

<p><strong>Layer 2 — the counter-intuitive hook.</strong> The de-escalation is, on paper, disinflationary and
therefore <em>dovish</em> — and yet it arrives on the same morning the market is still pricing a year-end
hike. Those two facts cannot both stay true through tomorrow. Either CPI confirms the inflation impulse and
the hike pricing firms despite cheaper oil, or CPI cools and the ceasefire's disinflation does the Fed's work
for it. The interesting trade is not equities here; it is the contradiction in the front-end, which is still
carrying a panic that the oil move has begun to undercut.</p>

<p><strong>Layer 3 — the gap.</strong> Ground truth: the labour market is firm and oil has just fallen
several dollars, a forward-inflation impulse now running the <em>right</em> way for the disinflation case.
What is priced: a still-elevated year-end hike and a partial AI valuation reset. The consensus narrative:
"the all-clear sounded, buy the dip." The gap sits between a front-end still leaning toward a hike and a
commodity complex that just removed one of the reasons to hike. That gap is where this week's edge lives — in
rates, not in the index.</p>

<p><strong>Layer 4 — Bull / Base / Bear.</strong> <em>Bull (35%):</em> CPI cools, the 2-year breaks back
under 4.05%, the year-end hike is priced out and the AI cohort re-rates — risk up, rates down, dollar soft,
gold firm. <em>Base (50%):</em> CPI lands in line, Warsh's Fed holds and lets the dots drift hawkish without
committing to a hike, the US chops while Europe leads into Thursday's ECB — risk mixed, rates range, dollar
firm. <em>Bear (20% of the risk, 15% probability):</em> CPI runs hot, the dots show a hike, the truce wobbles
on a fresh exchange, and the AI de-rating becomes a sector-wide de-gross — risk down hard, rates up, dollar
up. The probabilities sum to one; the asymmetry is that the base case is comfortable and the bear case is
violent.</p>

<p><strong>Layer 5 — priced vs not-priced.</strong> Mispriced the wrong way: a December hike still carrying
high odds after oil has fallen — the front-end has not finished digesting the ceasefire. Half-priced: European
equity outperformance into an ECB that hikes Thursday for reasons the oil move just weakened. Fairly priced: a
firm but no longer surging dollar. Fully priced: the ECB's 25bp itself, at 99% on the strip. The actionable
item is the first one — the gap between a front-end priced for a hike and a Fed that will not hike into one
firm payroll with unemployment at 4.3% and crude falling.</p>

<p><strong>The Burry tell — still live, just quieter.</strong> The thing nobody is hedged for has not gone
away; it has been postponed by a relief rally. Hyperscaler capex is now so large that the marginal AI-revenue
beat has to <em>accelerate</em> simply to hold the multiple. Broadcom grew AI revenue 143% and lost a seventh
of its market value, because the cohort is hedged for a revenue <em>miss</em> and not one name is hedged for a
revenue-growth-rate <em>disappointment</em>. Oracle reports tomorrow night with a $553bn backlog and the same
trap in front of it: a guide that is merely very good, into a tape that has started to re-rate "very good." The
ceasefire bought the AI trade a few days of calm. It did not change the arithmetic that turned Broadcom's
exceptional quarter into a selloff.</p>

<p><strong>The Pozsar mechanic.</strong> Trace today back to the plumbing. The dollar's slip off a two-month
high and a modest tightening reversal in the cross-currency basis say the same thing the equity rally does — a
little risk-premium left the system overnight. But the structural tell from last week is intact: the 2-year's
implied terminal rate still sits well above secured funding, which means every floating-rate corporate that
borrowed in 2023-24 on the assumption of cuts is carrying a higher marginal cost than its model assumed.
Investment-grade spreads near 80bp are priced for a soft landing that a hot CPI would call into question. The
ceasefire did not touch that. Watch IG spreads, not the VIX, for where the real constraint shows up first.</p>

<p><strong>The Papic constraint.</strong> Two political limits frame the week. In Frankfurt, Christine Lagarde
will almost certainly hike 25bp on Thursday — the decision is politically locked by an inflation profile she
has already guided higher — even though the ceasefire's effect on energy prices weakens the very rationale for
the move; she hikes anyway, and the press-conference verb tense, not the hike, sets the euro. In Washington,
Kevin Warsh inherits the chair on the 17th believing AI productivity can stem inflation, which is a dovish
instinct, into a committee in no mood to ease and a market daring him to hike. The constraint is the trade: a
new chair cannot afford to look soft on inflation in his first meeting, which caps how dovish the dots can
read even if the data would allow it.</p>

<p>So what to do with all of it. The cleanest expression today is not a view on the ceasefire or on AI — it is
to fade the front-end panic that the oil move has started to undercut, while keeping defined-risk equity
protection on through a fortnight that contains May CPI, an ECB hike and a new chair's first dot plot. Take the
Strait trades off the book; they did their job and the thesis behind them has been overtaken by events. Keep
the curve steepener and the short front-end, which are the trades that get paid whether the ceasefire holds or
the CPI cools. And resist the temptation to chase the relief rally into a print that can erase it before
lunch.</p>
""",

    # wrap drives the legacy single-page output.html — reuse the detailed map
    "wrap": """
<p>Markets got the headline they wanted overnight, and oil markets did what oil markets do when a supply
scare passes — handed back the premium almost as fast as they took it. Brent is back near $90 from above $98,
the VIX is under 18, and equities are higher for a second session. The storm, on the surface, has passed.</p>

<p>Be precise about what actually moved the tape last week, because the relief rally is answering the wrong
question. Friday's 2.6% in the S&amp;P and 4.2% in the Nasdaq were a rates story, not a war story — 172,000
jobs against an 80,000 consensus and a front-end that lurched toward pricing a year-end hike. Oil was the
smaller of the two shocks. The ceasefire retires the oil shock and does nothing about the 2-year, and nothing
about the CPI print that lands tomorrow.</p>

<p><strong>The driver.</strong> A two-tailed tape with one tail removed. The map simplifies to a single
question — the path of the front-end into tomorrow's CPI and Warsh's first dot plot next week. The ceasefire
also pulls oil, and therefore forward inflation, lower: December-hike odds have slipped from ~70% Friday toward
the high-40s. That is the genuinely constructive part of today, and it is showing up in rates, not in the
index the equity tape is celebrating.</p>

<p><strong>The Burry tell.</strong> Hyperscaler capex is now so large the marginal AI-revenue beat has to
accelerate just to hold the multiple. Broadcom grew AI 143% and lost a seventh of its cap; the cohort is hedged
for a miss and not one name is hedged for a growth-rate disappointment. Oracle reports tomorrow with a $553bn
backlog and the same trap in front of it. The ceasefire bought the AI trade calm, not a change in the
arithmetic.</p>

<p><strong>The Pozsar mechanic.</strong> A little risk-premium left the system overnight — the dollar slipped,
the basis eased. But the 2-year's implied terminal rate still sits well above secured funding, so every
floating-rate corporate that borrowed assuming cuts carries a higher cost than its model assumed. IG spreads
near 80bp are priced for a soft landing a hot CPI would question. Watch spreads, not the VIX.</p>

<p><strong>The Papic constraint.</strong> Lagarde hikes Thursday into an inflation profile she has guided
higher, even as the ceasefire weakens the rationale; the press-conference verb tense sets the euro, not the
hike. Warsh inherits the chair believing AI can stem inflation, into a committee in no mood to ease — a new
chair cannot look soft on inflation in his first meeting, which caps how dovish the dots can read.</p>

<p>So what to do: fade the front-end panic the oil move has begun to undercut, keep a re-centred equity hedge
through the event fortnight, take the Strait trades off the book, and let the print — not the headline — set
the direction.</p>
""",

    # ── Correlation regime ─────────────────────────────────────────────────
    "correlation_regime": """
<p><strong>1. Equities up while oil and the dollar fall together — a clean de-escalation signature.</strong>
Last week risk and the dollar rose together on haven demand; today they have split, with stocks higher and the
DXY off a two-month high. That recoupling is the tell that overnight was a genuine risk-premium release, not a
fresh growth impulse. When equities rally <em>and</em> the dollar softens, the move is being driven by falling
fear, not rising growth — read it as relief, and do not extrapolate it into a durable trend.</p>

<p><strong>2. Gold steady near $4,330 while oil plunges — the geopolitical bid has left both, but only gold
held.</strong> If this were still a war tape, gold would be falling with oil as the premium drains. Instead it
is flat: gold has stopped trading the Strait and gone back to trading real rates, which are easing as
front-end hike pricing relaxes. That decoupling is constructive for the gold thesis — it says the metal's next
move keys off the dot plot, not the headline, which is exactly the leg the pre-position was built for.</p>

<p><strong>3. The 2-year falls faster than the 10-year — a bull-steepening on the ceasefire.</strong> Cheaper
oil eases the inflation impulse the front-end was most exposed to, so the 2-year drops 6bp to the 10-year's 4bp
and 2s10s pushes to +40bp. This is a healthier steepener than last week's stagflation version — it is the curve
pricing <em>less</em> Fed, not more risk. The steepener and the short front-end are the two positions that
benefit, and they do so whether or not the equity rally lasts.</p>

<p><strong>4. US tech outpaces European equity on the relief — complicating last week's decoupling.</strong>
Friday's selloff was a US-specific, AI-concentration event and Europe sat it out; today's bounce is also led by
US tech, which narrows the DAX-over-Nasdaq divergence the cross-region trade was built on. The structural case
(ECB hiking into financials, no AI multiple to give back) is intact, but the ceasefire's relief favours the
high-beta US names first. The trade needs the CPI/Oracle read to re-assert the structural gap; until then it is
contested, and sized accordingly.</p>
""",

    # ── Vol & Skew ─────────────────────────────────────────────────────────
    "vol_skew": """
<p><strong>VIX back under 18 — but the term structure has not fully relaxed.</strong>
VIX9D ~15 · VIX ~17.2 · VIX3M ~19 · VIX6M ~21. The spot has unwound most of Friday's spike, yet the curve is
flatter than a true all-clear would leave it: the market is still paying up for the next three weeks, which is
rational with CPI, the ECB and a new chair's first FOMC all inside the window. The options market is not calling
the event cluster benign; it is taking a breath between catalysts.</p>

<p><strong>The hedge that worked, and what to do with it.</strong> The Jun-27 SPX put spread (MM-2026-008) ran
from 35 to ~80 points on Friday and has given back to ~50 as equities recovered — still up roughly 43% and now
struck a long way below a higher spot. The disciplined move is to trim it into the relief and roll the
protection up and out: a Jul-3 7200/6950 put spread (the new MM-2026-014) re-centres the defence near the money
for ~0.5% of notional, carrying it through the print, the ECB and the dot plot. This is risk management, not a
directional call — keep the convexity, refresh the strike.</p>

<p><strong>MOVE easing, but rates vol is the one to watch.</strong> Rates volatility is coming off its
payroll-week highs as front-end hike pricing relaxes, but tomorrow's CPI is a genuine binary for the 2-year. A
soft print collapses the remaining hike premium; a hot one re-arms it. If MOVE turns back up through its recent
range on the print, that is the earliest signal that the front-end relief is over and the stagflation steepener
is back — and it will show in rates vol before it shows in equities.</p>
""",

    # ── Sector & RV ────────────────────────────────────────────────────────
    "sector_rv": """
<p><strong>Leading the relief:</strong></p>
<ul>
<li><strong>Semiconductors and AI hardware:</strong> the cohort that led Friday's fall is leading the bounce —
Korea's chip names recovered after the KOSPI's circuit-breaker session, and the read-through to US semis is
positive. Worth being clear-eyed: this is a multiple re-rating recovering, not new demand arriving. SK Hynix has
pre-sold its 2026 HBM to Nvidia and demand is intact, which is why the bounce is credible — but the Oracle print
tomorrow is the next test of whether the market will pay up for AI-capex beneficiaries again.</li>
<li><strong>Transport, consumer and other oil-sensitives:</strong> the quiet winners of a $90 Brent versus a
$98 one. The ceasefire's clearest first-order effect is a lower input cost for the parts of the economy that
spent the spring absorbing an energy tax. This is the cleaner, less-crowded way to own the de-escalation than
chasing the index.</li>
</ul>

<p><strong>Lagging:</strong></p>
<ul>
<li><strong>Energy producers:</strong> the mirror image of the longs that just came off the book. With Brent
unwinding the war premium, the sector gives back the geopolitical bid it caught last week. Not a short into a
fragile truce — but no longer a place to be long, either.</li>
<li><strong>Defensives and rate-proxy sectors:</strong> utilities and staples lag a risk-on relief tape, and a
still-elevated long end keeps the rate-sensitive names capped. They become interesting again only if CPI runs
hot and the bid for safety returns.</li>
</ul>

<p><strong>RV — Long DAX / short Nasdaq (MM-2026-010), now contested.</strong> The structural case is intact —
the ECB hikes Thursday into a financials-heavy index with no AI multiple to surrender — but today's US-tech-led
relief narrows the gap the trade is built on. Hold it as a structural position, not a momentum one, and let the
CPI and Oracle reads tell you whether the decoupling re-asserts. If US tech keeps leading through the print, the
trade is early and should be sized down rather than added to.</p>
""",

    # ── Positioning & Flows ────────────────────────────────────────────────
    "positioning": """
<p><strong>The crowd was long the war and short duration into Friday — and is now unwinding the first.</strong></p>
<ul>
<li><strong>Oil:</strong> speculative length had been rebuilt through the escalation; the ceasefire forces that
length back out, which is part of why the unwind toward $90 is moving as fast as it is. With specs flushing
longs, the pain trade now runs the other way — a fresh missile exchange would catch a market that has just
sold, but absent that, the path of least resistance is lower as the premium bleeds.</li>
<li><strong>Front-end rates:</strong> the consensus chased the year-end hike after payrolls. That is the
crowded position the oil unwind is quietly working against. If CPI cools tomorrow, the squeeze is in the front
end — the 2-year reverses as the hike is priced out, which is exactly what the short-2Y (MM-2026-013) and the
steepener (MM-2026-009) are positioned for.</li>
<li><strong>Euro:</strong> specs sit long into Thursday's ECB. A 25bp hike is fully priced, so the risk is
sell-the-fact: if Lagarde signals a data-dependent pause, the crowded long unwinds. Short EURUSD (MM-2026-012)
owns that exit; a weaker euro also flatters the long-DAX leg.</li>
</ul>

<p><strong>Flows:</strong> the relief is pulling money back into the AI-beta that bled on Friday and out of the
short-dated safety that caught a bid last week — a mirror of the post-payrolls rotation, running in reverse.
The tell to watch is whether it sticks through CPI: a hot print reverses it again within a session, which is why
the re-centred equity hedge stays on.</p>
""",

    # ── Funding & Plumbing ─────────────────────────────────────────────────
    "funding": """
<p>SOFR near 3.62% — unchanged; repo is orderly and the overnight de-escalation released a little risk-premium
rather than creating any funding stress. The dollar's slip off a two-month high and a modest easing in the
cross-currency basis are the plumbing equivalent of the equity rally: fear leaving the system at the margin.
<strong>The Pozsar mechanic that still binds:</strong> the 2-year's implied terminal rate sits well above
secured funding, so every floating-rate borrower that issued in 2023-24 expecting cuts is paying a higher
marginal cost than its model assumed. Investment-grade spreads near 80bp are priced for a soft landing that a
hot CPI would question. The ceasefire did not touch that constraint — it bought time. Watch IG spreads for the
first sign the time has run out; the balance sheet shows the strain before the index does.</p>
""",

    # ── What the tape is missing ───────────────────────────────────────────
    "tape_missing": """
<p><strong>1. The front-end is still pricing a hike the ceasefire has begun to argue against.</strong>
December-hike odds eased from ~70% Friday toward the high-40s, but cheaper oil is a forward-inflation cut the
distribution has not fully booked. The threshold is tomorrow's CPI: a print at or below 3.7% takes the 2-year
back through 4.05% and prices the hike out; above 4.1% re-arms it. The market is treating the ceasefire as an
equity event when its sharper effect is in rates.</p>

<p><strong>2. (Burry tell) Oracle's $553bn backlog meets the same bar Broadcom failed.</strong>
The AI cohort is hedged for a revenue miss and not one name is hedged for a growth-rate disappointment. Oracle
reports tomorrow night into a tape that just took a seventh of Broadcom's cap for guiding "merely exceptional."
If OCI growth or capex guidance clears the printed estimate but not the whisper, the de-rating that paused this
week resumes — and it will not wait for the ceasefire's permission. Watch the guide, not the EPS.</p>

<p><strong>3. The truce is one headline from breaking, and the book that just sold the oil tail is the most
exposed to it.</strong> A fragile ceasefire that has already survived one threatened violation is not a signed
peace. The Brent long (MM-2026-002) is kept deliberately as the cheap re-escalation hedge for exactly this
reason; the threshold is a weekly close below $87, at which point the war premium is gone and the position
comes off. Above that, it is insurance worth carrying while the truce is unproven.</p>
""",

    # ── Consensus bid/offer ─────────────────────────────────────────────────
    "consensus": """
<p><strong>Consensus BID:</strong> the all-clear sounded — the ceasefire holds, oil keeps falling, CPI lands
benign, and the relief rally extends as the AI dip proves a gift. Warsh holds in June, the dots drift hawkish
but stop short of a hike, and the year's high in volatility is behind us.</p>

<p><strong>The strongest argument against — the OFFER:</strong> tomorrow's CPI. Headline ran 3.8% in April with
energy doing the work, and the Cleveland Fed nowcast points nearer 4.0% for May — before the ceasefire's lower
oil shows up in the data, which it will not for another month. A print above 4.1% confirms the inflation
impulse the front-end was right to fear, re-arms the year-end hike, sends the 2-year back toward 4.30% and puts
gold's $4,250 stop in play — and it does all of that while oil is already falling, which is the uncomfortable
combination: sticky core inflation that a cheaper barrel does not fix. The ceasefire settles the easy question.
CPI settles the hard one.</p>
""",

    # ── One chart that matters ──────────────────────────────────────────────
    "one_chart": """
<p class="theme">The 2-year Treasury yield at ~4.10%.</p>
<p>It is the one number that carries the whole repricing, and it is now caught between two forces pulling in
opposite directions. The ceasefire and a cheaper barrel argue it lower; a firm labour market and a still-elevated
year-end-hike probability argue it higher. Tomorrow's CPI casts the deciding vote. Hold below 4.15% through the
16-17 June FOMC and the front-end has conceded the hike — the steepener and the short-2Y get paid and gold's
catalyst turns supportive. Break back above 4.30% on a hot print and Friday's panic was right, the year-end hike
firms despite falling oil, and every long-duration asset on the tape — megacap tech, gold, the long bond — takes
another leg down. Everything else on this page keys off that one level, and it resolves at 8:30 tomorrow.</p>
""",

    # ── Catalyst calendar ──────────────────────────────────────────────────
    "catalyst_calendar": [
        {"day": "Wed", "date": "Jun 10",
         "event": "US May CPI (BLS, 8:30 ET) — the deciding print",
         "consensus": "Headline ~3.8% YoY; core ~2.8-3.3%. Cleveland Fed nowcast nearer 4.0%.",
         "view": ("The single binary of the week. At/below 3.7%: the 2-year breaks under 4.05%, the year-end "
                  "hike prices out, MM-2026-013/009 accelerate, gold bids. Above 4.1%: the hike re-arms, the "
                  "2-year heads back to 4.30%, gold tests its $4,250 stop. Cheaper oil will not show up in this "
                  "print — it is a backward-looking number landing into a forward-looking ceasefire."),
         "asymmetry": "<3.7%: 2Y -15bp, gold +2%; >4.1%: 2Y +15-20bp, DXY +0.5%, gold -2%",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 10",
         "event": "Oracle (ORCL) Q4 FY26 — after close",
         "consensus": "Finnhub EPS $1.58 vs Oracle's March guide $1.96-2.00; OCI +84% prior Q; RPO $553bn.",
         "view": ("The next read on the AI-capex multiple after Broadcom. The backlog is the bull case; the test "
                  "is whether OCI growth and capex guidance clear the whisper, not just the estimate. We are not "
                  "pre-positioning — the lesson of AVGO is that 'very good' can be a sell at this multiple."),
         "asymmetry": "Guide clears whisper: AI cohort re-rates +; merely-good guide: de-rating resumes",
         "dir": "flat"},
        {"day": "Thu", "date": "Jun 11",
         "event": "ECB rate decision — +25bp (99% priced; at least one more priced by year-end)",
         "consensus": "+25bp confirmed; press conference neutral-to-hawkish.",
         "view": ("The hike is locked; the verb tense sets the euro. 'Data-dependent pause' = EUR sell-the-fact, "
                  "the crowded spec long unwinds, MM-2026-012 accelerates. 'Further hikes' = EUR spike then fade "
                  "as growth damage and a now-cheaper-oil inflation profile dominate. The ceasefire quietly "
                  "weakened the rationale for the hike Lagarde will deliver anyway."),
         "asymmetry": "Pause signal: EUR/USD -0.8%; hawkish: EUR +0.4% spike then fade",
         "dir": "down"},
        {"day": "Wed", "date": "Jun 11",
         "event": "Adobe (ADBE) Q2 — after close",
         "consensus": "Consensus EPS ~$5.94; stock near 52-week lows; split sell-side (19 buy / 22 hold / 4 sell).",
         "view": ("The cleanest test of whether generative-AI is a tax or a tailwind for software incumbents. "
                  "Washed-out into the print, so the asymmetry is in the guide and the Firefly/AI monetisation "
                  "commentary, not the EPS the model already knows. Hold, do not chase."),
         "asymmetry": "AI additive to ARR: relief rally in software; cannibalisation read: another leg down",
         "dir": "flat"},
        {"day": "Tue-Wed", "date": "Jun 16-17",
         "event": "FOMC + dot plot — Warsh's first meeting, no cut priced",
         "consensus": ">80% hold in June; March median one cut; the dots are the whole event.",
         "view": ("A new chair who believes AI productivity can stem inflation, into a committee in no mood to "
                  "ease. He cannot look soft on inflation in his first meeting, which caps how dovish the dots "
                  "can read. Zero-cut median: 2Y +10bp, gold sells, MM-2026-004 nears its stop. One-cut held: "
                  "the market exhales, MM-2026-013 accelerates. CPI tomorrow shapes what members signal."),
         "asymmetry": "0-cut dots: DXY +0.7%, 2Y +10bp; 1-cut held: 2Y -15bp, gold +2%",
         "dir": "flat"},
    ],

    "earnings_ideas": earnings_ideas,

    # ── What changes my mind ────────────────────────────────────────────────
    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660 after Thursday's ECB press conference —
a rate-hike bid overriding the growth-error read. At ~1.646; stop 1.662.</li>

<li><strong>MM-2026-002 · Long Brent:</strong> exit on a weekly close below $87 — the war premium is gone and
the truce is holding. At ~$90; kept deliberately as the cheap re-escalation hedge while the ceasefire is
unproven, not as a directional oil call.</li>

<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop at 4.65%. At ~4.50% the oil unwind has helped; a hot
CPI tomorrow is the risk that sends it back toward the stop. Do not add.</li>

<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~July 15 — no discretionary close. Stop $4,250; at
~$4,330, $80 of room. Gold has gone back to trading real rates, so the dot plot, not the headline, is the
catalyst. A zero-cut median with gold under $4,400 is the early warning.</li>

<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. Back below 160 as the dollar slipped; the BoJ
September hike and the intervention backstop remain the structural support. Size for convexity.</li>

<li><strong>MM-2026-008 · SPX put spread:</strong> trim into the relief rally — it did its job at +43%. The
residual carries the FOMC tail; the re-centred Jul-3 spread (MM-2026-014) is the primary hedge now.</li>

<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to July 16. At +40bp, up ~167%; target +60bp. The
bull-steepening on the ceasefire is the healthy version of the thesis — hold through CPI and the dot plot.</li>

<li><strong>MM-2026-010 · Long DAX / short Nasdaq:</strong> stop ratio 0.943. Contested by today's US-tech-led
relief; hold as a structural position and let CPI/Oracle tell you whether the decoupling re-asserts. Do not add
while US tech leads.</li>

<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. Close on a hawkish ECB surprise above 1.182; the
base case is sell-the-fact on a fully-priced hike. Target 1.130.</li>

<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold 30 days. Working as the oil unwind
eases hike pricing. Close if CPI prints above 4.1% — that confirms the hike and makes the 2-year fair, not
excessive.</li>

<li><strong>MM-2026-014 · SPX Jul-3 put spread:</strong> the re-centred hedge. No stop — defined-risk premium;
carry it through CPI, the ECB and the dot plot. Trim if SPX falls 6%+ and the spread multiplies before the FOMC.</li>
</ul>
""",

    # ── Client ammo ────────────────────────────────────────────────────────
    "client_ammo": [
        {"q": "The ceasefire is here — is the all-clear real?",
         "a": ("The de-escalation is real and worth a relief rally; we have taken the Strait-of-Hormuz trades off "
               "the book. But it answers the easy question, not the hard one. Friday's selloff was a rates event, "
               "not a war event — 172,000 jobs and a front-end lurching toward a year-end hike. The ceasefire "
               "retires the oil tail and does nothing about the 2-year or tomorrow's CPI. Treat it as a real but "
               "partial all-clear: one of two tails removed, the bigger one still open.")},
        {"q": "If oil is falling, why keep any oil exposure at all?",
         "a": ("We closed the Brent/WTI spread and the upside call-spread tail — those theses are spent. We are "
               "keeping a small Brent long deliberately, as cheap insurance: the truce has already survived one "
               "threatened violation, and a single fresh exchange re-opens the premium in hours. The exit is a "
               "weekly close below $87, at which point the war premium is gone and the hedge comes off. You do "
               "not sell the fire insurance the hour the fire is contained but still smoking.")},
        {"q": "What should I actually watch tomorrow?",
         "a": ("The 2-year Treasury at 4.10% and the CPI print at 8:30. Below 3.7% on headline and the year-end "
               "hike prices out — the front-end relaxes, gold and duration catch a bid, equities extend. Above "
               "4.1% and the hike re-arms despite cheaper oil, the 2-year heads back toward 4.30%, and the AI "
               "de-rating that paused this week can resume. Oracle after the close is the second event — the next "
               "read on whether the market will pay up for AI-capex names after Broadcom. Two prints, one day.")},
    ],

    # ── Trade idea note (Trade Ideas page) ─────────────────────────────────
    "ideas_note": (
        "<p>One new idea today, and it is a hedge re-centre, not a directional bet. With three binary events "
        "inside the next eight sessions — May CPI tomorrow, the ECB on Thursday, and Warsh's first dot plot — the "
        "highest-expected-value action is to manage what is on, not to add risk into a print that can erase it by "
        "lunch. We took the Strait trades off (closed the Brent/WTI spread), and we roll the equity hedge up and "
        "out. The trades that get paid whether the ceasefire holds or the CPI cools — the curve steepener and the "
        "short front-end — are already on. Forcing a fourth idea into a CPI binary is the opposite of edge.</p>"
    ),

    # ── Rates rail (RHS) ───────────────────────────────────────────────────
    "rates_levels": [
        {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
         "vid": "sofr-v", "cid": "sofr-c", "asof": "Tue 9 Jun"},
        {"name": "US 2Y",   "level": "4.10%",   "chg": "-6bp",         "dir": "down"},
        {"name": "US 10Y",  "level": "4.50%",   "chg": "-4bp",         "dir": "down"},
        {"name": "US 30Y",  "level": "~5.02%",  "chg": "term premium", "dir": "warn"},
        {"name": "2s10s",   "level": "+40bp",   "chg": "steeper",      "dir": "up"},
        {"name": "Bund 10Y","level": "~2.9%",   "chg": "ECB Thu (est)","dir": "flat"},
        {"name": "MOVE",    "level": "~108",    "chg": "easing (est)", "dir": "down"},
        {"name": "Fed odds","level": "~48%",    "chg": "hike by Dec",  "dir": "down"},
    ],

    # ── Yesterday / week graded (output.html legacy page) ──────────────────
    "yesterday_graded": """
<table>
<thead><tr><th>ID</th><th>Trade</th><th>Entry &rarr; Current</th><th>P&amp;L</th><th>Note</th></tr></thead>
<tbody>
<tr><td class="mute">MM-2026-001</td><td>Short EURAUD</td><td>1.6450 &rarr; 1.646</td><td class="num mute">&minus;0.06%</td>
<td>Roughly flat into Thursday's ECB. Thesis intact: the hike is a growth error and EUR sells the fact on the press conference. Stop 1.662.</td></tr>
<tr><td class="mute">MM-2026-002</td><td>Long Brent crude</td><td>$91.00 &rarr; $90.20</td><td class="num mute">&minus;0.88%</td>
<td>Round-tripped the war premium as the ceasefire took hold. Kept deliberately as the cheap re-escalation hedge; exit on a weekly close below $87.</td></tr>
<tr><td class="r">&#x26D4; MM-2026-003</td><td>Long Brent / Short WTI spread</td><td>3.30 &rarr; 1.95</td><td class="num r">&minus;40.91%</td>
<td>CLOSED (discretionary). The ceasefire removes the Hormuz-specific premium the spread was built to own; it traded through the $2.00 exit. Banked the loss, stood aside. Held 9 days.</td></tr>
<tr><td class="r">MM-2026-004</td><td>Short US 10Y yield</td><td>4.44% &rarr; 4.50%</td><td class="num r">&minus;1.35%</td>
<td>The oil unwind eased the yield back from 4.544%. Stop 4.65%. CPI tomorrow is the risk in both directions. Do not add.</td></tr>
<tr><td class="r">MM-2026-005</td><td>Long gold (pre-position)</td><td>$4,523 &rarr; $4,330</td><td class="num r">&minus;4.27%</td>
<td>Steadied as it decoupled from oil and went back to trading real rates. Stop $4,250; min hold to ~July 15. The dot plot, not the headline, is the catalyst.</td></tr>
<tr><td class="g">MM-2026-007</td><td>Short USDJPY</td><td>159.37 &rarr; 159.20</td><td class="num g">+0.11%</td>
<td>Back below 160 as the dollar slipped off its high. BoJ September hike and the intervention backstop remain the support. Stop 163.00.</td></tr>
<tr><td class="g">MM-2026-008</td><td>SPX Jun-27 7300/7000 put spread</td><td>35 &rarr; 80 &rarr; 50 pts</td><td class="num g">+42.86%</td>
<td>Did its job at +128% Friday; gave back into the relief rally to +43%. Trim into strength; the re-centred Jul-3 spread (MM-2026-014) is the primary hedge now.</td></tr>
<tr><td class="g">MM-2026-009</td><td>2s10s UST steepener (pre-pos)</td><td>+15bp &rarr; +40.0bp</td><td class="num g">+166.67%</td>
<td>Best structural position. The ceasefire bull-steepened the curve further as the 2Y fell faster than the 10Y. Min hold to July 16; target +60bp. Hold.</td></tr>
<tr><td class="mute">MM-2026-010</td><td>Long DAX vs short Nasdaq</td><td>0.9722 &rarr; 0.967</td><td class="num r">&minus;0.53%</td>
<td>Contested. Today's US-tech-led relief narrows the decoupling. Structural case intact (ECB hiking financials, no AI multiple); hold, don't add while US tech leads. Stop 0.943.</td></tr>
<tr><td class="r">MM-2026-011</td><td>Brent $100/$115 call spread</td><td>3.0 &rarr; 1.30</td><td class="num r">&minus;56.67%</td>
<td>The upside tail deflated as the ceasefire took the Strait premium out. Defined-risk; kept the residual on a fragile truce rather than pay to close. Stop 1.0.</td></tr>
<tr><td class="g">MM-2026-012</td><td>Short EUR/USD (sell-the-fact)</td><td>1.1600 &rarr; 1.158</td><td class="num g">+0.17%</td>
<td>Roughly flat into Thursday's ECB. The setup is a fully-priced hike and a crowded spec long. Stop 1.182; target 1.130.</td></tr>
<tr><td class="g">MM-2026-013</td><td>Short US 2Y yield (pre-pos)</td><td>4.162% &rarr; 4.10%</td><td class="num g">+1.49%</td>
<td>Working. The oil unwind eased December-hike pricing from ~70% toward the high-40s. Min hold 30 days; stop 4.35%. Close if CPI prints above 4.1%.</td></tr>
</tbody>
</table>
""",

    # ── Event radar note (legacy page) ─────────────────────────────────────
    "event_radar_note": (
        "<p>Three binary events sit inside the next eight sessions and resolve every open position's thesis: "
        "May CPI tomorrow (the deciding print on the year-end hike), the ECB on Thursday (+25bp locked; the "
        "press conference sets the euro), and Kevin Warsh's first FOMC dot plot on June 16-17. The trades "
        "positioned to get paid on either resolution — the 2s10s steepener and the short 2-year — are already "
        "on; today we add only a re-centred equity hedge, not fresh directional risk.</p>"
    ),

    # ── VIX term structure (chart) ─────────────────────────────────────────
    "vix_term": [
        {"label": "VIX9D", "value": 15.0},
        {"label": "VIX",   "value": 17.2},
        {"label": "VIX3M", "value": 19.0},
        {"label": "VIX6M", "value": 21.0},
    ],

    # ── Yield curve (chart) ────────────────────────────────────────────────
    "yield_curve_pts": [
        {"label": "2Y",  "value": 4.10},
        {"label": "5Y",  "value": 4.36},
        {"label": "10Y", "value": 4.50},
        {"label": "30Y", "value": 5.02},
    ],

    # ── Staleness check ────────────────────────────────────────────────────
    "staleness": [
        {"datum": "S&P 500 ~7,510",     "source": "CNBC / Yahoo Finance June 9",        "asof": "2026-06-09", "stale": False},
        {"datum": "Nasdaq 100 ~26,900", "source": "Web search (estimated) June 9",      "asof": "2026-06-09", "stale": False},
        {"datum": "Brent ~$90.2",       "source": "TradingEconomics / Reuters June 9",   "asof": "2026-06-09", "stale": False},
        {"datum": "WTI ~$86.8",         "source": "Derived from Brent / spread June 9",  "asof": "2026-06-09", "stale": False},
        {"datum": "Gold ~$4,330",       "source": "CNBC / TradingEconomics June 9",      "asof": "2026-06-09", "stale": False},
        {"datum": "US 10Y 4.50%",       "source": "TradingEconomics June 9",             "asof": "2026-06-09", "stale": False},
        {"datum": "US 2Y 4.10%",        "source": "TradingEconomics June 9",             "asof": "2026-06-09", "stale": False},
        {"datum": "2s10s +40bp",        "source": "Derived from 2Y/10Y levels",          "asof": "2026-06-09", "stale": False},
        {"datum": "USDJPY 159.20",      "source": "TradingEconomics June 9",             "asof": "2026-06-09", "stale": False},
        {"datum": "EURUSD 1.158",       "source": "FXStreet June 9",                     "asof": "2026-06-09", "stale": False},
        {"datum": "DXY ~99.9",          "source": "Barchart / Investing.com June 9",     "asof": "2026-06-09", "stale": False},
        {"datum": "VIX ~17.2",          "source": "Yahoo Finance / CBOE June 9",         "asof": "2026-06-09", "stale": False},
        {"datum": "Dec-hike odds ~48%", "source": "CME FedWatch (web search) June 9",    "asof": "2026-06-09", "stale": False},
        {"datum": "Iran-Israel ceasefire", "source": "Reuters / Yahoo Finance June 9",   "asof": "2026-06-09", "stale": False},
        {"datum": "May payrolls +172k", "source": "BLS June 5",                          "asof": "2026-06-05", "stale": True},
        {"datum": "ORCL/ADBE/SAIL est", "source": "Finnhub (earnings_data.md, Jun 8 6am)","asof": "2026-06-08", "stale": True},
        {"datum": "SOFR ~3.62%",        "source": "NY Fed (auto-updates in rail)",       "asof": "2026-06-08", "stale": True},
        {"datum": "GBPUSD / USDCNH",    "source": "Unverified this refresh",             "asof": "unavailable", "stale": True},
        {"datum": "Bund / Gilt 10Y",    "source": "Unverified this refresh",             "asof": "unavailable", "stale": True},
        {"datum": "MOVE index",         "source": "Unverified this refresh (est)",       "asof": "unavailable", "stale": True},
    ],

    # ── Trade cards ────────────────────────────────────────────────────────
    "new_ideas":          new_ideas_cards,
    "pre_position_ideas": prepos_cards,
}

# ── Render: legacy single page (output.html) ───────────────────────────────
book.step("Rendering output.html")
html_out = book.build_html(brief, trades, regime_log)
with open(book.OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_out)
book.log(f"wrote {len(html_out):,} bytes -> {book.OUTPUT_PATH}")

# ── Render: 4-page Shark Tank app (index / insights / earnings / trades) ───
book.step("Rendering Shark Tank pages + fragments")
shark_format.render_all(brief, trades, regime_log)

# ── Persist state ──────────────────────────────────────────────────────────
book.step("Saving trades.json + regime_log.json")
book.save_json(book.TRADES_PATH, trades)
book.save_json(book.REGIME_PATH, regime_log)

book.step("Done")
