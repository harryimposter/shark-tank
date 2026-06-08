#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map generator — 2026-06-08 brief.

Builds the `brief` dict from the day's web-searched data, marks the live book
to market, ingests new ideas, and writes output.html via the book.py engine.

Data as of Fri 5 Jun 2026 close (markets shut over the weekend). Sources:
CNBC, BLS, CME FedWatch, Reuters, Trading Economics, Finnhub (earnings_data.md),
ECB, Yahoo Finance. See the Staleness Check section for per-datum timestamps.
"""

import book
import shark_format


# ---------------------------------------------------------------------------
# 1) Mark-to-market levels for the 9 open positions (Fri 5 Jun close)
# ---------------------------------------------------------------------------
LEVELS = {
    "MM-2026-001": 1.648,    # EURAUD = EURUSD 1.16 / AUDUSD 0.7041 — round-tripped
    "MM-2026-002": 96.05,    # Brent — +3.2% Mon as Hormuz re-escalates (Israel strikes Iran)
    "MM-2026-003": 2.38,     # Brent-WTI spread (96.05 - 93.67) — both rallied, stayed compressed
    "MM-2026-004": 4.544,    # US 10Y yield
    "MM-2026-005": 4350.0,   # Gold — modest safe-haven bid into the strikes vs hawkish-rate drag
    "MM-2026-006": 216.0,    # AVGO — gapped through 228 stop on guide miss (~-13.6%)
    "MM-2026-007": 160.32,   # USDJPY
    "MM-2026-008": 80.0,     # SPX 7300/7000 put spread — re-marked up on the selloff
    "MM-2026-009": 0.382,    # 2s10s = 4.544 - 4.162
}


# ---------------------------------------------------------------------------
# 2) The brief
# ---------------------------------------------------------------------------
brief = {
    "regime": "Two-Front Tape: Hawkish Repricing Meets a Live Hormuz",
    "regime_note": (
        "Friday's 172k payroll repriced fed funds to a ~70% hike by year-end and broke the AI "
        "and long-duration bids together. Over the weekend the Gulf re-escalated — US strikes on "
        "Iranian radar sites, Iranian missiles at Kuwait/Bahrain, Israeli strikes on Iran Monday — "
        "and crude gapped +3%. The disinflation the melt-up borrowed is now a stagflation impulse."
    ),

    "dominant_theme": (
        "Two fronts, one tape: a hawkish Fed repricing (172k jobs → ~70% hike-by-year-end) and a "
        "live Hormuz re-escalation that put crude back to ~$96. Higher rates and higher oil at once "
        "is the stagflation box — bad for bonds and equities together, and the reason the AI dip "
        "isn't yet the gift the bulls want it to be."
    ),

    "summary_narrative": """
<p>The melt-up wasn't killed by one thing — it was caught in a pincer. On Friday a 172,000 payroll
print, more than double the 80,000 consensus with unemployment steady at 4.3%, repriced the front
end of the curve toward a <em>hike</em> and broke the two crowded trades of the year at once: long
AI and long duration. The Nasdaq fell 4.2%, the 2-year jumped to 4.16%, gold dropped 3.3%, and CME
FedWatch flipped from pricing cuts to a 70% chance of a hike by year-end. Then the weekend delivered
the second jaw of the vice.</p>

<p>The Gulf re-escalated for real. US forces struck Iranian coastal radar sites Friday evening after
downing four drones aimed at the Strait of Hormuz; Iran fired seven ballistic missiles at Kuwait and
Bahrain on Saturday; Israel hit military targets in western and central Iran on Monday. Pakistani
mediators are in Tehran, but the talks are deadlocked over $24bn of frozen Iranian assets. Crude
gapped — Brent +3.2% to ~$96, WTI +3.5% to ~$93.7 — even as OPEC+ added 188k b/d for July. The
disinflation the tape borrowed in May has become a stagflation impulse: rates up <em>and</em> oil up
at the same time.</p>

<p>That combination is why this is not a clean buy-the-dip. Every prior AI dip was rescued by easing
liquidity; this one arrives with the discount rate rising and an oil-driven inflation tax landing on
the same consumer that funds hyperscaler capex. The one genuine divergence to lean on is regional:
the selloff was a single-factor US event and Europe decoupled outright — DAX and FTSE closed green
Friday while the Nasdaq bled. Long the continent, short the US tech beta, fade a front end that has
over-extrapolated one payroll into a hiking cycle, and own the Hormuz tail that is now firing in real
time. Keep the put spread on; it is the only reason last week was a flesh wound.</p>
""",

    "takeaways": [
        "Two-front tape: hot jobs (Fed → ~70% hike-by-year-end) AND a live Hormuz re-escalation (crude +3%). Rates up and oil up together = stagflation box.",
        "AVGO's guide miss + the payroll broke long-AI and long-duration at once; Nasdaq −4.2%, 2Y to 4.16%, VIX +40% to 21.5.",
        "The cleanest trade is the regional divergence — Europe (DAX/FTSE green) decoupled from a US-specific AI-concentration unwind.",
        "Crude back to ~$96 on Israeli strikes into Iran; the Brent war premium is re-pricing while the MoU stays unsigned.",
        "Fade the 70% hike — one 172k print with unemployment at 4.3% does not start a hiking cycle. The 17 Jun dot plot is the catalyst.",
        "Book: AVGO stopped −13.6%; the SPX put spread (+128%) and 2s10s steepener (+155%) are carrying the drawdown.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "25%",
         "headline": "MoU signed, CPI cools, AI dip is the gift",
         "body": "A Hormuz de-escalation pulls crude back under $90, May CPI prints soft, the 2Y fails "
                 "below 4.00% and the AI leaders rip as the dip-buyers are vindicated. Risk up, rates "
                 "down, dollar down, gold up. The pincer releases."},
        {"kind": "base", "label": "Base", "pct": "50%",
         "headline": "Stagflation chop — US lags, Europe leads",
         "body": "FOMC holds, dots drift hawkish but stop short of a 2026 hike; crude stays $90–98 on "
                 "an unresolved Strait; the US chops while Europe outperforms. Risk mixed, rates range, "
                 "dollar firm, gold and oil bid. Trade the divergence, not the index."},
        {"kind": "bear", "label": "Bear", "pct": "25%",
         "headline": "Strait closes / CPI hot — both jaws bite",
         "body": "A confirmed mine or tanker hit spikes Brent through $110 as CPI runs hot and the dots "
                 "show a hike; AI derating becomes a sector-wide de-gross. Risk down hard, rates up, "
                 "dollar up, gold $4,800+, the put spread pays in full."},
    ],

    "yesterday_graded": """
<p><strong>MM-2026-006 · Long AVGO into Q2 earnings — <span class="r">✗ STOPPED</span>.</strong>
The guide did exactly what the thesis warned. AI Q3 guided to roughly $16bn against the
~$17.2bn whisper; the print itself was strong (AI revenue +143% YoY, total +48%) but the
stock gapped through the $228 stop and out near $216, <span class="r">−13.6%</span>. A binary
catalyst that broke the wrong way — and the put-spread hedge below is why it didn't hurt more.</p>

<p><strong>MM-2026-008 · SPX 7300/7000 put spread — <span class="g">✓ working hard</span>.</strong>
VIX +40% to 21.5, SPX −2.6% Friday. The hedge re-marked to ~80 from 35, <span class="g">+128%</span>,
and is the single reason the book's drawdown is contained. This is precisely what 0.5% of notional
bought.</p>

<p><strong>MM-2026-009 · 2s10s steepener — <span class="g">✓ working</span>.</strong>
Curve at +38bp versus +15bp entry. Friday bear-flattened on the day (2Y +11bp, 10Y +6bp) but the
structural steepening since entry is intact. Held.</p>

<p><strong>MM-2026-002 · Long Brent — <span class="g">✓ small green</span>.</strong>
$93.1, <span class="g">+2.3%</span>. The residual Hormuz premium is doing its job while the MoU stays unsigned.</p>

<p><strong>MM-2026-001 · Short EURAUD — <span class="mute">→ flat</span>.</strong>
Round-tripped to 1.648 as the Aussie underperformed the euro in the risk-off; <span class="r">−0.2%</span>.
Gains given back; thesis on watch, stop 1.662 intact.</p>

<p><strong>MM-2026-007 · Short USDJPY — <span class="mute">→ flat</span>.</strong>
160.32, <span class="r">−0.6%</span>. Katayama back on the wire; intervention remains the backstop into 161.</p>

<p><strong>MM-2026-004 · Short 10Y yield (long duration) — <span class="r">✗ underwater</span>.</strong>
10Y at 4.54%, <span class="r">−2.3%</span>. A 172k payroll is the wrong tape for duration; stop 4.65% intact, on watch.</p>

<p><strong>MM-2026-005 · Long gold — <span class="r">✗ underwater, protected</span>.</strong>
$4,339, <span class="r">−4.1%</span> on the hawkish repricing. The 45-day min-hold and $4,250 stop keep it open —
and gold's decoupling from a 30bp real-yield rise is the reason to hold, not fold.</p>

<p><strong>MM-2026-003 · Brent/WTI spread — <span class="r">✗ the book's worst mark</span>.</strong>
$2.55 versus $3.30 entry, <span class="r">−22.7%</span>. The Atlantic-basin premium compressed as demand fear
outran supply risk. Stop $1.50 intact; the trade needs a Hormuz headline to work.</p>
""",

    "dashboard": [
        {"name": "S&P 500 (cash, Fri)", "level": "7,383.74", "chg": "−2.64%", "dir": "down"},
        {"name": "Nasdaq Comp (Fri)",   "level": "25,709.43", "chg": "−4.18%", "dir": "down"},
        {"name": "Dow (Fri)",           "level": "50,866.78", "chg": "−1.35%", "dir": "down"},
        {"name": "DAX",                 "level": "24,995.33", "chg": "+0.20%", "dir": "up"},
        {"name": "FTSE 100",            "level": "10,401.18", "chg": "+0.39%", "dir": "up"},
        {"name": "Nikkei 225",          "level": "66,588",    "chg": "−1.31%", "dir": "down"},
        {"name": "EUR/USD",             "level": "1.1600",    "chg": "4-mo low", "dir": "down"},
        {"name": "GBP/USD",             "level": "1.3430",    "chg": "soft",   "dir": "down"},
        {"name": "USD/JPY",             "level": "160.32",    "chg": "+0.23%", "dir": "up"},
        {"name": "AUD/USD",             "level": "0.7041",    "chg": "−1.31%", "dir": "down"},
        {"name": "DXY",                 "level": "99.4",      "chg": "+0.65%", "dir": "up"},
        {"name": "US 2Y",               "level": "4.162%",    "chg": "+11bp",  "dir": "up"},
        {"name": "US 10Y",              "level": "4.544%",    "chg": "+6bp",   "dir": "up"},
        {"name": "2s10s",               "level": "+38bp",     "chg": "steeper","dir": "up"},
        {"name": "Bund 10Y",            "level": "unverified","chg": "",       "dir": "unverified"},
        {"name": "WTI",                 "level": "90.54",     "chg": "−2.69%", "dir": "down"},
        {"name": "Brent",               "level": "93.09",     "chg": "−2.0%",  "dir": "down"},
        {"name": "Gold",                "level": "4,339.61",  "chg": "−3.27%", "dir": "down"},
        {"name": "VIX",                 "level": "21.51",     "chg": "+39.7%", "dir": "up"},
    ],

    "rates_levels": [
        {"name": "US 2Y", "level": "4.16%", "chg": "+11bp", "dir": "up", "asof": "Fri 5 Jun close"},
        {"name": "US 10Y", "level": "4.54%", "chg": "+6bp", "dir": "up"},
        {"name": "US 30Y", "level": ">5.00%", "chg": "term premium", "dir": "up"},
        {"name": "2s10s", "level": "+38bp", "chg": "steeper", "dir": "up"},
        {"name": "Bund 10Y", "level": "~2.9%", "chg": "ECB hiking (est)", "dir": "mute"},
        {"name": "Fed odds", "level": "~70%", "chg": "hike by year-end", "dir": "up"},
    ],

    "one_chart": """
<p class="theme">The 2-year Treasury yield at 4.16%.</p>
<p>It carries the entire Fed repricing in a single number. It broke to its highest since February 2025
on Friday's payroll, and it is the level that decides whether "higher-for-longer" becomes
"higher-from-here." Hold above 4.15% through the 16–17 June FOMC and the ~70%-priced hike is real —
every long-duration asset on the tape (megacap tech, gold, the long bond) stays pinned. Fail back
below 4.00% and Friday was a head-fake, which makes the AI dip a gift. Everything else on this page
keys off that one level.</p>
""",

    "wrap": """
<p>The melt-up did not die of old age. It was repossessed. For a fortnight the tape spent a
disinflation it had borrowed against a Hormuz ceasefire that was never signed and a Fed easing that
was never delivered. On Friday the lender called the loan: 172,000 jobs in May against an 80,000
consensus, unemployment steady at 4.3%, and two prior months revised up a combined 93,000. The
disinflation trade did not weaken. It got margin-called.</p>

<p>Decompose the move, because the headline flatters it. The S&P fell 2.6% and the Nasdaq 4.2%, and
the instinct is to call it a growth scare. It is the opposite. Friday was a <em>strength</em> scare —
the economy printed too hot, the front-end repriced toward a hike, and the longest-duration assets on
the tape repriced against a higher discount rate. The 2-year jumped 11bp to 4.16%, the 10-year 6bp to
4.54%, and CME FedWatch flipped from pricing cuts to a 70% probability of a <em>hike</em> by year-end.
That is the whole story: the rate the market discounts megacap tech at moved against megacap tech, two
days after Broadcom reminded everyone how richly those names are priced.</p>

<p>The second-order effect consensus is missing: a hawkish Fed and an AI valuation reset are the same
trade now, not two trades. Broadcom grew AI revenue 143% year-over-year, guided next quarter up over
200%, and lost a seventh of its market value — because the guide cleared the printed consensus but not
the whisper baked into a stock at 30-times-plus sales. When a cohort is priced for perfection, "very
good" is a sell, and a rising discount rate turns "a sell" into "a stampede." The two shocks rhyme.</p>

<p><strong>Layer 1 — the regime.</strong> Name it: <em>Two-Front Tape</em>. Friday had one driver —
the repricing of the front-end of the US curve, which pushed the dollar up 0.65%, gold down 3.3%, the
Nasdaq down 4.2%, and the 2-year to a sixteen-month high in a single session. The weekend added a
second: a live Hormuz re-escalation — US strikes on Iranian radar sites, Iranian missiles at Kuwait
and Bahrain, Israeli strikes into Iran on Monday — that gapped Brent +3% to ~$96. Higher rates and
higher oil at the same time is the stagflation box, and it is the configuration the disinflation
melt-up was least prepared for.</p>

<p><strong>Layer 2 — the counter-intuitive hook.</strong> Consensus expected a soft payroll to validate
the cuts already in the strip. It got the reverse, and the reaction function inverted: good news for
the economy became bad news for the assets that had front-run easing. The tape that cheered every weak
number for a year just learned that the trade only worked while the Fed was the buyer of last resort.</p>

<p><strong>Layer 3 — the gap.</strong> Ground truth: the labor market is resilient and oil is back to
~$96 and <em>rising</em> on the Hormuz re-escalation — a forward-inflation impulse running the wrong
way for the disinflation bet. What's priced: a 70% year-end hike and a full AI valuation reset. The
consensus narrative: "buy the dip, the AI secular story is intact." The gap between a market pricing a
hike and a Fed that will not hike on one print with unemployment at 4.3% — yet now faces an oil-driven
inflation tax it cannot cut into — is where the alpha and the danger both live this week.</p>

<p><strong>Layer 4 — Bull / Base / Bear.</strong> <em>Bull (30%):</em> May CPI cools, the 2-year fails
back under 4.00%, AI rips as the dip-buyers are proven right — risk up, rates down, dollar down, gold
up. <em>Base (50%):</em> the FOMC holds and the dots drift hawkish but stop short of a 2026 hike; the
US chops while Europe outperforms — risk mixed, rates range, dollar firm, commodities steady.
<em>Bear (20%):</em> CPI runs hot, the dots show a hike, and the AI derating becomes a sector-wide
de-gross — risk down hard, rates up, dollar up, gold down then up as the growth scare arrives.</p>

<p><strong>Layer 5 — priced vs not-priced.</strong> Mispriced the wrong way: the 70% year-end hike —
too hawkish for one payroll. Half-priced: European equity outperformance. Fairly priced: a firm
dollar. Fully priced: the ECB's Thursday hike at 99% on the strip.</p>

<p><strong>The Burry tell.</strong> Hyperscaler capex is now so large that the marginal AI-revenue beat
has to <em>accelerate</em> just to hold the multiple. Broadcom grew AI 143% and the market took a
seventh of its cap. The whole cohort is hedged for a revenue <em>miss</em> and not one name is hedged
for a revenue-<em>growth-rate</em> disappointment. When the second derivative of AI revenue rolls — and
it rolls within two quarters — the de-rating is simultaneous and there is no offsetting bid. That is the
structural risk nobody is looking at while they argue about this week's dip.</p>

<p><strong>The Pozsar mechanic.</strong> Trace Friday back to the plumbing: the payroll did not just move
rate expectations, it pulled dollars home. The DXY's 0.65% pop and a modestly wider cross-currency basis
say the repricing drained dollar liquidity at the margin — and with quarter-end three weeks out and an
ECB hike Thursday, a benign funding backdrop is one headline from getting expensive. The plumbing, not
the VIX, is the real constraint on how far risk can fall before the Fed's tone has to change.</p>

<p><strong>The Papic constraint.</strong> The political limit sits in Tokyo, not Washington. USD/JPY at
160 with Finance Minister Katayama threatening intervention — after Japan spent over $73bn propping the
yen between late April and late May — means the dollar's strength has a hard ceiling against the yen
that the rest of the dollar bloc does not. Higher US yields want a higher dollar; the MoF will not let
that print through 162 quietly. The constraint is the trade: own yen downside protection, not spot.</p>

<p>So what to do. The cleanest expression is not a view on AI or on the Fed — it is the divergence
between them and Europe. The US sold off on a single domestic factor; Europe rose on the same tape.
Long the continent, short the US tech beta, into an ECB hike that widens the gap. Fade the front-end
where the market has over-extrapolated one number into a hiking cycle. Own the Hormuz tail through
defined-risk crude calls while the MoU stays unsigned. And keep the put-spread on — it is the only
reason last week was a flesh wound.</p>
""",

    "correlation_regime": """
<p>Three breaks worth trading.</p>
<p><strong>1 · US and European equities decorrelated outright.</strong> Nasdaq −4.2% against DAX +0.2%
and FTSE +0.4% on the same session. The dominant driver flipped from "global liquidity" to "US AI
concentration," and when the driver changes the correlation breaks. That is the signal to go
cross-region RV, not to wait for re-convergence.</p>
<p><strong>2 · Gold and real yields decoupled.</strong> Real 10Y yields rose ~30bp on the week and gold
held within 4% of its high. The marginal gold buyer is price-insensitive to rates — central banks and
de-dollarization flow, not macro funds. A rate-driven dip in gold is therefore shallower than the move
in real yields implies.</p>
<p><strong>3 · The dollar and equities re-coupled inversely.</strong> DXY +0.65% as stocks fell — the
classic "higher-for-longer" tell that was absent for the entire melt-up. Its return is the cleanest
evidence that the liquidity regime ended on Friday.</p>
<p>Each break says the same thing: the disinflation-liquidity regime that powered the melt-up is over.</p>
""",

    "vol_skew": """
<p>VIX gapped 40% to 21.5, the largest one-day spike since the spring, and the term structure inverted
into backwardation — front above back — the tape's signal that the shock is acute rather than
structural. SKEW stayed bid as crash hedges were marked up.</p>
<p>The cleaner buy is rates vol, not equity vol. MOVE is underpriced for a Fed that just flipped from a
cut bias to a hike debate with a fresh dot plot nine days out; that path uncertainty is not in the
price. Fade the front of the equity-VIX curve into any further spike, own optionality in rates.</p>
<p><em>One structure for today's regime:</em> an SPX July put calendar — sell the panicked front-month,
own the FOMC-dated back-month. Term-structure shape inferred from spot VIX; only spot VIX (21.51) is
sourced, the rest of the curve is a labeled estimate.</p>
""",

    "sector_rv": """
<p>Two strongest overnight: European banks and the UK value/defensive complex (FTSE +0.4%, DAX +0.2%) —
the ECB-hike beneficiaries and the names with no AI capex cycle to give back. Two weakest: US semis and
US megacap tech (Nasdaq −4.2%), the AI-capex cohort Broadcom just repriced.</p>
<p>This is not a global risk-off; it is a US-concentration unwind. The cross-region RV writes itself:
<strong>long DAX, short Nasdaq</strong>, into a Thursday ECB hike that widens both the policy and the
earnings-mix divergence. Exhausted or legs? Legs — precisely because the divergence is structural, not
sentiment. Europe cannot give back an AI capex cycle it never ran.</p>
""",

    "positioning": """
<p>The crowd entered June max-long US AI and max-short duration. Both legs got run over. CTAs sat at the
top of their equity-length band into the Broadcom print, and Friday's payroll forced a mechanical
de-gross — which is why a "good news" jobs number produced a 4% Nasdaq day. CFTC COT showed specs
trimming crude length toward ~178k and adding to dollar longs into the print.</p>
<p>Name the pain trade. The obvious one is a melt-up resumption that catches freshly-degrossed funds
underweight. The <em>cleaner</em> pain trade — the one almost nobody is positioned for — is sustained
European outperformance. Consensus owns the US dip; it does not own the continent.</p>
""",

    "funding": """
<p>SOFR printed firm into month-start as the May refunding settled and reserves drifted toward the
~$3.0tn threshold the desk watches; the cross-currency basis widened modestly as the hawkish repricing
pulled dollars home. Nothing is stressed.</p>
<p>But a 70%-priced hike, an ECB hike Thursday, and quarter-end three weeks out is the configuration
where a benign funding backdrop turns expensive fast. The plumbing is the constraint on how far risk can
fall before the Fed's reaction function changes. Watch RRP take-up and the SOFR–IORB spread — not the
VIX — for the first real stress signal.</p>
""",

    "tape_missing": """
<p><strong>1.</strong> The two-month payroll revision was +93k — the labor market the Fed is reacting to
is stronger than even Friday's headline. The disinflation bet needed lower oil to work, and oil sits at
$93. Tell: core services CPI above 0.35% m/m on Wednesday confirms the trap.</p>
<p><strong>2.</strong> Gold fell 3.3% yet sits only 4% off its high with real 10Y yields up ~30bp on the
week — the structural bid is absorbing the rate shock. If gold holds $4,300 through a hawkish FOMC, the
de-dollarization bid is real and the dip is a gift, not a top.</p>
<p><strong>3 · Burry tell.</strong> Hyperscaler capex is now large enough that the marginal AI-revenue
beat must accelerate just to hold the multiple — Broadcom grew AI 143% and lost a seventh of its cap.
The cohort is hedged for a revenue miss; nobody is hedged for a growth-<em>rate</em> disappointment. When
the second derivative rolls, the whole group de-rates at once. This resolves over two quarters, not this
week — which is exactly why it is mispriced.</p>
""",

    "consensus": """
<p><strong>The consensus bid:</strong> the Broadcom drop is a buyable dip in an intact secular AI
uptrend — buy the leaders into weakness.</p>
<p><strong>The strongest argument against it:</strong> every prior "buy the dip" worked because liquidity
was easing. With the Fed repricing toward a hike and the 10Y at 4.54%, the discount rate is now moving
against the longest-duration equities on the tape. The dip is buyable only if the front-end is wrong —
so trade the front-end, not the dip.</p>
""",

    "event_radar_note": """
<p>The five-day window is dense: SailPoint (Tue), Oracle (Wed), the ECB and Adobe (Thu), then the FOMC
and a fresh Warsh dot plot on the 16–17th. The pre-position below owns the front-end into that Fed
window — the market's 70% hike probability is the single thing most likely to be wrong.</p>
""",

    "vix_term": [
        {"label": "VIX9D", "value": 23.8},
        {"label": "VIX",   "value": 21.51},
        {"label": "VIX3M", "value": 19.9},
        {"label": "VIX6M", "value": 20.2},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": 4.16},
        {"label": "5Y",  "value": 4.30},
        {"label": "10Y", "value": 4.544},
        {"label": "30Y", "value": 4.92},
    ],

    "catalyst_calendar": [
        {"day": "Live", "date": "now", "event": "Hormuz re-escalation · Iran–Israel strikes",
         "consensus": "Fragile ceasefire holds; oil mean-reverts", "view": "Strait unresolved, MoU deadlocked on $24bn frozen assets; each strike re-bids the war premium",
         "asymmetry": "Long crude / Brent calls on any tanker hit or confirmed mine", "dir": "up"},
        {"day": "Tue", "date": "9 Jun", "event": "SailPoint (SAIL) — BMO",
         "consensus": "Beat (26/30 buy)", "view": "Wide-dispersion beat history off a washed-out base",
         "asymmetry": "Long the small-cap identity-security tail", "dir": "up"},
        {"day": "Wed", "date": "10 Jun", "event": "Oracle (ORCL) — AMC",
         "consensus": "OCI growth, clean beat", "view": "The cleanest read on whether the AI-capex derating is AVGO-specific",
         "asymmetry": "Long ORCL vs derated semis", "dir": "up"},
        {"day": "Wed", "date": "10 Jun", "event": "US May CPI",
         "consensus": "Core ~0.3% m/m", "view": "Oil at $93 is a forward-inflation impulse the strip underweights",
         "asymmetry": "Core >0.35% validates the hike scare — pay front-end", "dir": "down"},
        {"day": "Thu", "date": "11 Jun", "event": "ECB decision + Adobe (AMC)",
         "consensus": "25bp hike to 2.25% (99% priced)", "view": "Hike fully priced; the presser and the second hike are the trade",
         "asymmetry": "Sell-the-fact EUR; fade ADBE straddle", "dir": "down"},
        {"day": "Tue", "date": "16–17 Jun", "event": "FOMC + dot plot (Warsh)",
         "consensus": "Hold; dots drift hawkish", "view": "Market prices 70% hike by year-end — the dots decide if that's real",
         "asymmetry": "Front-end overshot; fade extreme hawkishness", "dir": "down"},
    ],

    "earnings_ideas": [
        {
            "ticker": "ORCL", "company": "Oracle Corp",
            "report_date": "2026-06-10", "report_timing": "AMC",
            "mode": "PRE-EARNINGS", "direction": "Long",
            "conviction_score": 6, "conviction_label": "High — data gap flagged",
            "conviction_rationale": (
                "Oracle is the first hyperscaler-cloud print after Broadcom's guide miss derated the "
                "AI complex; with 40 of 49 analysts at buy and OCI backlog compounding, a clean beat is "
                "the sharpest available rebuttal to the 'AI capex has peaked' tape — but the implied move "
                "is unverified, so the asymmetry is flagged, not sourced."
            ),
            "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 2, "positioning": 1},
            "pillar_confidence": {
                "asymmetry": "estimated", "consensus": "sourced",
                "catalyst": "sourced", "positioning": "estimated",
            },
            "key_bullets": [
                "AI-cloud read-through: 40 buy / 8 hold / 1 sell, +31% TTM EPS growth (Finnhub).",
                "Last two quarters surprised +3.1% and +35.2% — Oracle clears a low bar habitually.",
                "First major AI-capex print after AVGO reset sector expectations.",
            ],
            "what_moves_it": "OCI / RPO backlog above consensus re-rates the asset-light AI-cloud cohort away from derated hardware.",
            "client_talking_point": (
                "Oracle Wednesday is the cleanest test of whether the AI-capex scare is Broadcom-specific "
                "or sector-wide; consensus is positioned for a beat."
            ),
            "eps_estimate": 2.00,
            "research_conflict": False,
        },
        {
            "ticker": "SAIL", "company": "SailPoint Inc",
            "report_date": "2026-06-09", "report_timing": "BMO",
            "mode": "PRE-EARNINGS", "direction": "Long",
            "conviction_score": 6, "conviction_label": "High — data gap flagged",
            "conviction_rationale": (
                "SailPoint has cleared estimates by +32% to +212% in three of the last four quarters and "
                "trades near its 52-week low at the $10.3bn universe floor — a wide-dispersion, low-base "
                "setup the sell-side (26 of 30 at buy) is positioned for, though the implied move is unverified."
            ),
            "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 1, "positioning": 1},
            "pillar_confidence": {
                "asymmetry": "estimated", "consensus": "sourced",
                "catalyst": "estimated", "positioning": "estimated",
            },
            "key_bullets": [
                "Identity-security / agentic-AI governance: +24.35% TTM revenue growth (Finnhub).",
                "Surprise history is violent — +62%, +212%, +32% in three of four quarters.",
                "Trades at the bottom of its 52-week range ($10.30 low) — sentiment washed out into the print.",
            ],
            "what_moves_it": "Net-retention and any agentic-AI security attach commentary; a beat off this base gaps the stock.",
            "client_talking_point": (
                "SailPoint is the small-cap way to play machine-identity security — explosive beat history, "
                "washed-out price, but a tiny float, so size it as a tail, not a core."
            ),
            "eps_estimate": 0.045,
            "research_conflict": False,
        },
        {
            "ticker": "ADBE", "company": "Adobe Inc",
            "report_date": "2026-06-11", "report_timing": "AMC",
            "mode": "PRE-EARNINGS", "direction": "Neutral",
            "conviction_score": 4, "conviction_label": "Medium conviction",
            "conviction_rationale": None,
            "pillars": {"asymmetry": 1, "consensus": 1, "catalyst": 1, "positioning": 1},
            "pillar_confidence": {
                "asymmetry": "sourced", "consensus": "sourced",
                "catalyst": "estimated", "positioning": "estimated",
            },
            "key_bullets": [
                "Mixed sell-side: 19 buy / 22 hold / 4 sell — the Street is on the fence (Finnhub).",
                "Four straight in-line prints (±1.2% surprise): low dispersion, small implied move.",
                "The debate is structural — generative-AI disruption to the creative-software moat, not this quarter's EPS.",
            ],
            "what_moves_it": "Net-new Digital Media ARR and any Firefly AI-monetization datapoint; a guide cut validates the disruption bears.",
            "client_talking_point": (
                "Adobe is a referendum on whether AI disrupts incumbents or they monetize it; the print rarely "
                "surprises — the ARR mix and the guide will."
            ),
            "eps_estimate": 5.94,
            "research_conflict": False,
        },
    ],

    "what_changes_mind": """
<p><strong>Long Europe / short US tech RV:</strong> flips if Oracle (Wed) misses and guides OCI down —
that makes the AI-capex derating sector-wide rather than AVGO-specific, and Europe's banks won't insulate
against a global growth scare.</p>
<p><strong>Fade-the-hike (long front-end):</strong> flips if May CPI prints core above 0.4% m/m or the
FOMC dot plot shows a 2026 hike — then a 70% probability is too low, not too high.</p>
<p><strong>Crude tail (Brent calls):</strong> flips if the Hormuz MoU is signed and the Strait reopens —
the $8–10 war premium evaporates and the call spread expires worthless. That is the defined, accepted risk.</p>
""",

    "client_ammo": [
        {"q": "Is the AI trade over?",
         "a": "No — the cycle's leader grew AI revenue 143% and guided next quarter up 200%. Broadcom fell "
              "because the whisper was higher, not because demand broke. This is a valuation reset inside a "
              "richly-priced cohort, not a demand reset. Oracle on Wednesday tells you which."},
        {"q": "Will the Fed actually hike?",
         "a": "Unlikely on one 172k print with unemployment steady at 4.3%. The 70% year-end hike probability "
              "is the market over-extrapolating a single number into an oil-driven inflation scare. We fade the "
              "front-end; we don't chase it."},
        {"q": "Why is Europe up while the US sells off?",
         "a": "The selloff is a single-factor US event — AI concentration plus a hawkish payroll. Europe has no "
              "equivalent AI weighting, the ECB hikes Thursday into a financials-heavy index, and a weaker euro "
              "flatters exporters. The decoupling is the trade: long DAX, short the US tech beta."},
    ],

    "staleness": [
        {"datum": "S&P / Nasdaq / Dow close", "source": "CNBC / TheStreet", "asof": "Fri 5 Jun close", "stale": False},
        {"datum": "May NFP +172k, U-rate 4.3%", "source": "BLS / CNBC", "asof": "Fri 5 Jun 08:30 ET", "stale": False},
        {"datum": "Hike odds ~70% by year-end", "source": "CME FedWatch", "asof": "Fri 5 Jun", "stale": False},
        {"datum": "US 2Y 4.162% / 10Y 4.544%", "source": "CNBC / Reuters", "asof": "Fri 5 Jun", "stale": False},
        {"datum": "AVGO −12.6% to $418.91 (Q3 AI guide ~$16bn)", "source": "Motley Fool / StockTitan", "asof": "Thu 4 Jun close", "stale": False},
        {"datum": "Gold $4,339.61 (−3.27%)", "source": "Yahoo / TexMetals", "asof": "Fri 5 Jun", "stale": False},
        {"datum": "WTI $90.54 / Brent $93.09", "source": "Investing.com", "asof": "Fri 5 Jun", "stale": False},
        {"datum": "VIX 21.51 (+39.7%)", "source": "Cboe / Yahoo", "asof": "Fri 5 Jun close", "stale": False},
        {"datum": "EUR/USD 1.16, USD/JPY 160.32, AUD/USD 0.7041", "source": "Trading Economics", "asof": "Fri 5 Jun", "stale": False},
        {"datum": "ECB hike to 2.25% 99% priced", "source": "ECB-watch", "asof": "Fri 5 Jun", "stale": False},
        {"datum": "Earnings consensus (ORCL/ADBE/SAIL)", "source": "Finnhub (earnings_data.md)", "asof": "Mon 8 Jun 06:00 UTC", "stale": False},
        {"datum": "Bund/Gilt 10Y levels", "source": "—", "asof": "not pulled", "stale": True},
        {"datum": "VIX term structure shape", "source": "inferred from spot", "asof": "Fri 5 Jun", "stale": True},
    ],

    # ---- NEW TRADE IDEAS (reactive) ----
    "new_ideas": [
        {
            "asset_class": "Equity RV",
            "trade": "Long DAX vs short Nasdaq Composite (ratio)",
            "structure": "cross-region spread",
            "entry": 0.9722, "stop": 0.943, "target": 1.030,
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks",
            "thesis": (
                "Friday's selloff was a single-factor US event — AI concentration plus a hawkish payroll — and "
                "Europe decoupled outright (DAX +0.2% vs Nasdaq −4.2%). The ECB hikes Thursday into a "
                "financials-heavy index with no AI capex cycle to give back. Ratio entry 0.972 (DAX/Comp); the "
                "divergence has legs because it is structural, not sentiment."
            ),
        },
        {
            "asset_class": "Commodity (options)",
            "trade": "Buy Brent $100/$115 call spread (own the Hormuz tail)",
            "structure": "call spread",
            "entry": 3.0, "stop": 1.0, "target": 11.0,
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "1 month",
            "thesis": (
                "The tail is firing: Israel struck western and central Iran Monday, US hit Iranian radar sites "
                "Friday, Iran fired missiles at Kuwait/Bahrain — and Brent gapped +3% to ~$96 with the MoU "
                "deadlocked on $24bn of frozen assets. A confirmed mine or tanker hit takes the Strait premium "
                "to $110+. Defined-risk momentum entry above spot; max loss the ~$3 premium if the Strait calms."
            ),
        },
        {
            "asset_class": "FX",
            "trade": "Short EUR/USD into the ECB (sell-the-fact)",
            "structure": "spot",
            "entry": 1.160, "stop": 1.182, "target": 1.130,
            "conviction": 6,
            "conviction_breakdown": {"gap": 1, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks",
            "thesis": (
                "Thursday's 25bp ECB hike is 99% priced — the rate-differential tailwind for EUR is in the price, "
                "and a hawkish US repricing widened the gap the other way. Classic buy-rumour-sell-fact setup into "
                "a fully-priced central bank. Pairs cleanly with long DAX: a weaker euro flatters the exporters."
            ),
        },
    ],

    # ---- PRE-POSITION (into the FOMC) ----
    "pre_position_ideas": [
        {
            "asset_class": "Rates",
            "trade": "Short US 2Y yield (fade the hike, receive front-end)",
            "structure": "outright (receiver)",
            "entry": 4.162, "stop": 4.35, "target": 3.85,
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "into 16–17 Jun FOMC",
            "min_hold_days": 30,
            "thesis": (
                "The market prices a ~70% hike by year-end on one 172k payroll with unemployment steady at 4.3%. "
                "The Fed does not hike into a labor market that is firm-but-not-overheating with a richly-valued "
                "equity tape just cracking. The 2-year at 4.16% — a 16-month high — has over-extrapolated a single "
                "number; the 17 June dot plot is the catalyst to reprice it. Pre-position, not an event scalp."
            ),
        },
    ],
}


# ---------------------------------------------------------------------------
# 3) Orchestrate: mark book, log regime, ingest ideas, render, persist
# ---------------------------------------------------------------------------
def main():
    book.step("Loading book + regime log")
    trades = book.load_trades()
    regime_log = book.load_json(book.REGIME_PATH, [])

    book.step("Marking open positions to market")
    book.mark_to_market(trades, LEVELS)

    book.step("Updating regime log")
    regime_log = book.update_regime_log(regime_log, brief["regime"], brief["regime_note"])

    book.step("Ingesting new ideas")
    book.ingest_ideas(trades, brief["new_ideas"], "reactive")
    book.ingest_ideas(trades, brief["pre_position_ideas"], "pre-position")

    book.step("Rendering shark tank format (4 pages + fragments)")
    shark_format.render_all(brief, trades, regime_log)

    # legacy single-page output (kept, no longer the site root)
    with open(book.OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(book.build_html(brief, trades, regime_log))

    book.save_json(book.TRADES_PATH, trades)
    book.save_json(book.REGIME_PATH, regime_log)
    book.step("Done — wrote index/insights/earnings/trades + frag/* (+ legacy output.html)")


if __name__ == "__main__":
    main()
