#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-16 (Tuesday).

THE NEXT CHAPTER vs the Jun 15 run: the relief rally we flagged arrived — bigger.
- Monday Jun 15 was a melt-up. S&P +1.65% to 7,554.29; Nasdaq +3.07% to 26,683.94
  (worst-to-first); Dow +0.92% to 51,671.03. Driven by the US-Iran peace MoU and
  collapsing oil. (TheStreet, Yahoo Finance, Motley Fool.)
- OIL fell FURTHER: Brent plunged ~4% toward ~$83 — a two-month low — as the war
  premium kept draining. (Trading Economics, investingLive.) The forward-disinflation
  impulse deepened.
- NVIDIA sold $25B of high-grade bonds (first offering since 2021, boosted from
  $20B, ~3x oversubscribed at ~$85B of orders) AND fresh buyback — powering an
  AI/semis rip (Micron, Intel, Meta, Western Digital all up). The Burry tell made
  concrete: AI capex has become an AI debt boom. (Bloomberg, Futunn, SEC 424B5.)
- VIX crushed to 16.20 (-8.37% Mon) — MAXIMUM complacency 24h before Warsh's dots.
- GOLD ROSE to ~$4,316 (3rd up session) — NOT the safe-haven deflation we modelled
  Jun 15. Lower oil cut hike odds, pulled real rates down, and the REAL-RATES engine
  re-rated gold. The book's gold (MM-005, holding 4GLD) is now working for a new
  reason. (CBS, discoveryalert, Sunday Guardian.)
- US-Iran MoU: signing ceremony Fri Jun 19 in Switzerland (Pakistan PM Sharif
  mediating). Strait reopens immediately without tolls; prewar shipping ~30 days;
  US lifts blockade + issues sanctions waivers. Trump on Truth Social: "Ships of the
  World, start your engines. Let the oil flow!" PENDING — written as upcoming.
  THE LIVE CAVEAT: Israel says it won't be bound by the deal and vows to stay in
  south Lebanon; renewed IDF strikes in the Beirut area Jun 14 (US restrained Iran's
  response so the MoU could proceed); a conflicting Iranian-media draft circulates.
  (NPR, NBC, Fortune, Times of Israel, PBS.)
- FOMC Jun 16-17 is Kevin Warsh's FIRST meeting as chair (sworn in May 22). Decision
  Wed Jun 17 2pm ET. ~98% priced HOLD at 3.50-3.75%. The event is the dot plot / a
  bias shift (easing -> neutral). 2026-hike odds eased to ~47% (from ~54% pre-MoU)
  as oil collapsed. (CME FedWatch, FXStreet, Bitcoin News, Kiplinger.)

Run:  python gen_2026_06_16.py
"""
import sys, os
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book
import shark_format
import live_levels
import book_scanner
import fetch_rsi

TODAY = date.today().isoformat()

trades     = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

# ── Live levels ────────────────────────────────────────────────────────────────
book.step("Fetching live levels (TradingView)")
snap = live_levels.fetch()
book.log(f"resolved {len(snap)} symbols")
levels = live_levels.trade_levels(snap)
# Option spreads have no live feed — mark from spot.
# SPX 7300/7000 put spread: Monday's melt-up took the S&P to ~7,554 — even deeper OUT
# of the money than Friday. Only time value + the FOMC tail remain; mark ~$30 (decayed
# from ~$38 Fri, ~$80 peak). Held into Jun 27 expiry purely for the dot-plot tail.
levels["MM-2026-008"] = 30.0

# ── RSI positioning data ───────────────────────────────────────────────────────
book.step("Computing RSI positioning (Yahoo Finance, 1-month window)")
open_ids = [t["id"] for t in trades["open"]]
rsi_data = fetch_rsi.fetch_all(open_ids)
for tid, r in rsi_data.items():
    if r.get("error"):
        book.log(f"  {tid} RSI: {r['error']}")
    else:
        ta = r.get("technicals") or {}
        ta_str = f"  TA={ta.get('ta_score','?')}/2 {ta.get('trend','')}" if ta else ""
        flag = "  *** FLAGGED vs us" if r.get("crowd_vs_us") else ""
        book.log(f"  {tid} RSI={r['rsi']}  {r['verdict']}{ta_str}{flag}")

book.step("Computing idea RSI + valuation data (Yahoo Finance)")
idea_rsi_data = fetch_rsi.fetch_all_ideas()
for ik, r in idea_rsi_data.items():
    if r.get("error"):
        book.log(f"  idea {ik}: {r['error']}")
    elif r.get("rsi") is not None:
        val = r.get("valuation") or {}
        pe_str = f"  P/E={val.get('trailing_pe_fmt','N/A')}" if not val.get("error") else ""
        ta = r.get("technicals") or {}
        ta_str = f"  TA={ta.get('ta_score','?')}/2 {ta.get('trend','')}" if ta else ""
        book.log(f"  idea {ik} RSI={r['rsi']}  {r['verdict']}{ta_str}{pe_str}")

# ── RSI screener (curated cross-asset universe, absolute 30/70) ──────────────────
book.step("Running RSI screener (broad ~140-name cross-asset universe, Yahoo)")
screen = fetch_rsi.run_screener()
book.log(f'  scanned {screen["scanned"]} · {len(screen["oversold"])} oversold · '
         f'{len(screen["overbought"])} overbought · {screen["errors"]} no-data')

# Authored screener notes overlay the live mechanical read with a desk view where we
# genuinely have one (keyed by ticker). Live names without a note get a templated read.
SCREENER_NOTES = {
    "NVDA": "We are constructive but disciplined. Monday's rip was powered by NVDA's $25B bond sale (first since "
            "2021, ~3x oversubscribed) plus a fresh buyback — bullish flow now, but the same debt-funded AI capex "
            "is the structural Burry tell. An OVERBOUGHT NVDA here is where we hedge the book's concentration into "
            "the dots, not where we add. The book owns NVDA (-10.5%) through the bullish range note (idea 101).",
    "MU":   "Still our highest-conviction add-on-weakness. HBM is sold out into the AI-memory supercycle and the "
            "Monday melt-up lifted it with the cohort. But it is the Fable book's largest position (~25.8%) into "
            "earnings Jun 24 — overbought into the dots means hedge the concentration, do not chase it higher.",
    "ADBE": "We remain BUYERS of the dislocation. The Jun 11 -6% to a 52-week low ($218) was a beat-and-raise sold "
            "purely on the CFO's exit to Marvell — governance, not fundamentals. An oversold/washed-out ADBE here "
            "is the dip, not the breakdown. This is the carried single-name long (idea MM-014).",
    "XLE":  "Energy is rolling over as the war premium bleeds out (Brent ~$83, two-month low; the MoU signs Jun 19 "
            "and the Strait reopens immediately without tolls). Oversold is NOT a buy — we are SHORT energy as the "
            "transports-vs-energy RV (idea MM-019). Sell income against any energy length, don't chase the dip.",
    "GLD":  "Gold's real-rates engine kicked in: lower oil cut hike odds, real yields fell, and bullion rose a "
            "third session to ~$4,316. We OWN it (MM-005 / the book's 4GLD). A dovish Warsh extends it; a hawkish "
            "dot plot is the one thing that reverses it — it is the first hedge to give back on hawkish dots.",
    "TLT":  "Duration is the winning side of the MoU binary: the 10Y eased toward ~4.45% on the oil-disinflation "
            "impulse. We are long via the short-10Y/short-2Y book (MM-004/013) and the steepener (MM-009). An "
            "oversold long-bond proxy into a possible dovish-hold is the add — but not before Wednesday 2pm.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("Disinflationary Melt-Up Into Warsh's First Dot Plot: Oil ~$83, VIX 16, "
          "Nasdaq +3% — Decision Wed 2pm")
regime_note = (
    "The peace dividend became a melt-up, and now the tape sits at maximum complacency 24 hours before the only "
    "event it has not priced. Monday Jun 15 was a risk-on rout to the upside: the S&P rose 1.65% to 7,554.29, the "
    "Nasdaq jumped 3.07% to 26,683.94 — worst-to-first — and the Dow added 0.92% to 51,671.03. (TheStreet, Yahoo, "
    "Motley Fool.) The relief rally this brief flagged Friday arrived, and it arrived bigger than modelled. "
    "Oil kept falling: Brent plunged ~4% toward ~$83, a two-month low, as the war premium drained out and the "
    "US-Iran MoU moved toward a Friday Jun 19 signing in Switzerland — the Strait reopens immediately without "
    "tolls, prewar shipping inside 30 days, the US blockade lifts. Trump on Truth Social: 'Ships of the World, "
    "start your engines. Let the oil flow!' Written as PENDING — the signing is Friday, not done. "
    "(NPR, NBC, Fortune, Trading Economics.) "
    "Two things changed the book's read since Friday. First, gold did NOT deflate on the peace as we modelled — it "
    "ROSE a third session to ~$4,316, because the oil collapse cut hike odds, pulled real rates lower, and the "
    "real-rates engine re-rated bullion. The book's gold (MM-005) is working for a new reason. (CBS, Sunday "
    "Guardian.) Second, the AI complex ripped on a fact that is also the structural warning: NVIDIA sold $25B of "
    "high-grade bonds — its first offering since 2021, boosted from $20B, roughly three times oversubscribed at "
    "~$85B of orders — and paired it with a fresh buyback. The market cheered the borrowing; it is the very "
    "capital-markets dependency the Burry tell warned of, now arriving at the chip vendor itself, not just the "
    "hyperscalers. (Bloomberg, Futunn.) "
    "The relief crushed VIX to 16.20 (-8.37% Monday) — the most complacent vol of the cycle, into Kevin Warsh's "
    "first FOMC. The decision lands Wednesday at 2pm ET: a hold at 3.50-3.75% is ~98% priced; the event is the dot "
    "plot and whether the new chair shifts the bias from easing toward neutral. The oil collapse has eased "
    "2026-hike odds to ~47% from ~54% (CME FedWatch) — which means the consensus framing that the only risk is a "
    "hawkish surprise is now wrong in both directions: at VIX 16, a dovish-hold tail and a hawkish-dots tail are "
    "BOTH cheap to own. That asymmetry is the single best trade on the board, and it is what the held put spread "
    "(MM-008) and the fresh dot-plot tail (MM-017) are for. "
    "The honest caveats hardened, they did not soften: Israel's ministers say Israel will NOT be bound by the Iran "
    "deal and vow to stay in south Lebanon; renewed IDF strikes hit the Beirut area Jun 14 (the US restrained "
    "Iran's response so the MoU could move forward); and a conflicting Iranian-media draft circulates. The tape "
    "has priced a clean peace and a non-event Fed. The brief has priced neither."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# ── Per-trade enrichment (instrument descriptions, full thesis, catalysts, risks,
#    and per-criterion WHY for the conviction breakdown) ────────────────────────
TRADE_ENRICHMENTS = {
    "MM-2026-001": {
        "instrument": (
            "EUR/AUD spot FX cross-rate. EUR = euro (ECB-managed); AUD = Australian dollar "
            "(commodity-linked, RBA-managed). Driven by relative ECB-vs-RBA rate paths, iron-ore "
            "prices (Australia's largest export = AUD tailwind), global risk sentiment, and the "
            "2-year eurozone-vs-Australia rate spread."
        ),
        "fundamental_thesis": (
            "The ECB delivered its +25bp hike to 2.25% on Jun 11 and Lagarde signalled 'not pre-committing to a "
            "particular rate path' — the pause that removes the marginal EUR buyer. Monday's risk-on melt-up is a "
            "tailwind to the AUD (commodity-currency beta), which presses the short cross lower; with no forward EUR "
            "catalyst the cross grinds toward target. Patience over pressing — the peace risk-on does the work."
        ),
        "catalysts": [
            "ECB pause signal (Jun 11) now in the price — no forward EUR catalyst",
            "Risk-on melt-up / iron-ore firmness = AUD commodity-currency tailwind",
            "RBA June meeting — a hawkish hold supports AUD vs a paused ECB",
            "FOMC Jun 16-17 — a USD move spills into both legs; watch the cross-rate, not just EUR/USD",
        ],
        "risks": (
            "Risk-off flips the commodity-currency beta and AUD sells harder than EUR; a China demand shock pulls "
            "iron ore and the AUD tailwind; an ECB official re-opens the hike door and EUR squeezes. Stop 1.662."
        ),
        "breakdown_why": {
            "gap":          "3/3 — the cross sits a full figure above where the 2yr spread implies, with a "
                            "pause-signalling ECB against an RBA still leaning tight.",
            "catalyst":     "1/2 — the dated ECB catalyst has passed; what remains is slower-burn (RBA, iron ore).",
            "positioning":  "1/2 — EUR longs into the hike are now trapped flat, offering some unwind fuel.",
            "confirmation": "1/2 — the risk-on AUD beta helps but the cross has not broken cleanly lower.",
            "stop_quality": "1/1 — 1.662 is a clean technical level, tight to the target move.",
        },
    },
    "MM-2026-004": {
        "instrument": (
            "US 10-year Treasury yield. Shorting the yield = buying duration (long bonds / 10Y "
            "futures / TLT). Driven by the Fed path (front-end anchored), inflation expectations, "
            "fiscal supply/term premium, and the safe-haven bid."
        ),
        "fundamental_thesis": (
            "The winning side of the MoU binary, now confirmed by a deeper oil move. Brent at ~$83 is a forward CPI "
            "cut the post-PPI FedWatch has not fully booked, and the 10Y eased to ~4.45% (intraday lows the lowest "
            "in a month). The trade is roughly flat-to-positive from entry (4.44%) and the catalyst is one day out: "
            "a data-dependent Warsh hold Wednesday extends the 10Y toward 4.30%. Do not add into the print; the dot "
            "plot, not the level, is the gate. The honest risk is a hawkish dot plot that sells the long end on the "
            "still-hot PPI evidence regardless of oil."
        ),
        "catalysts": [
            "Oil collapse (Brent ~$83, two-month low) = forward CPI cut not fully in FedWatch",
            "FOMC dot plot Jun 16-17 — data-dependent hold = 10Y toward 4.30%; hawkish dots = stop tested",
            "May Retail Sales Jun 17 — soft print reinforces the disinflation read",
            "Treasury supply at the long end — the offsetting risk to the duration rally",
        ],
        "risks": (
            "Warsh delivers an explicitly hawkish dot plot despite the oil relief; the long end sells on fiscal "
            "supply rather than rallying on disinflation; the MoU collapses pre-signing and oil/inflation snap back. "
            "Stop 4.65% (now ~4.45%, ~20bp away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the deeper oil move widens the disinflation gap; the net inflation signal is "
                            "firmly lower, but the long end carries fiscal-supply risk.",
            "catalyst":     "2/2 — FOMC Jun 16-17 and Retail Sales Jun 17 are dated, direct, 10Y-relevant events.",
            "positioning":  "1/2 — consensus is still cautiously short duration; squeeze fuel on a dovish hold.",
            "confirmation": "2/2 — the 10Y eased to one-month lows on the oil move; two confirming sessions.",
            "stop_quality": "1/1 — 4.65% is a clear technical level; ~20bp of risk.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold in USD. The inverse of real rates, driven by the Fed path "
            "and real yields, USD strength, EM central-bank buying, geopolitical premia, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "Re-marked UP, and for a different engine than we entered on. The Jun 15 thesis modelled gold deflating "
            "as the geopolitical bid drained on the MoU. The opposite happened: gold rose a third straight session "
            "to ~$4,316 because the oil collapse cut hike odds, pulled real yields lower, and the REAL-RATES engine "
            "took over from the safe-haven engine. The position is back above its $4,250 stop (touched Jun 10; 45-day "
            "min-hold to ~Jul 15 keeps it structural). A dovish Warsh Wednesday extends it; a hawkish dot plot is the "
            "one catalyst that reverses it — so it is the book's first hedge to give back on hawkish dots."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — dovish/data-dependent hold = real yields down, gold up; hawkish = capped",
            "Oil/inflation path — sustained crude weakness keeps hike odds (and real yields) low = gold supported",
            "US-Iran MoU signing Jun 19 — residual safe-haven premium drains, but the real-rates engine dominates now",
            "EM central-bank Q2 gold purchases (China, India, Turkey — structural buyers)",
        ],
        "risks": (
            "Warsh delivers hawkish dots and real yields surge; the MoU signs cleanly and the last safe-haven "
            "premium drains faster than the real-rate tailwind builds; a gold-specific spec flush. Stop $4,250 "
            "(45-day min-hold override keeps it open to ~Jul 15)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — gold's decoupling from the old safe-haven driver is resolving into a real-rates "
                            "trade; the mispricing is now the dovish-hold path the market under-weights.",
            "catalyst":     "2/2 — FOMC dots are a dated, direct real-rate catalyst with clean gold transmission.",
            "positioning":  "1/2 — positioning is not extreme; not a cleanly crowded long.",
            "confirmation": "2/2 — three up sessions to ~$4,316 confirm the real-rates engine; fresh technical lift.",
            "stop_quality": "1/1 — $4,250 is a defined level; the min-hold rule is the discipline mechanism.",
        },
    },
    "MM-2026-007": {
        "instrument": (
            "USD/JPY spot FX (dollar-yen). Driven by the US-Japan 2yr rate differential, BoJ "
            "normalisation, the Fed path, risk sentiment (JPY is a crisis safe-haven), and Japanese "
            "MoF intervention risk above ~162-163."
        ),
        "fundamental_thesis": (
            "USD/JPY near 160 with the MoF on intervention watch and a BoJ September hike >50% priced. The "
            "differential that keeps yen weak is set to narrow from both ends — a normalising BoJ and a Fed whose "
            "oil-driven disinflation argues against further tightening. Monday's low-vol risk-on melt-up is the "
            "near-term headwind (carry stays on when vol is crushed and VIX is 16), which is why this is a patient "
            "short with the MoF ceiling at 163 as the backstop, not a momentum trade."
        ),
        "catalysts": [
            "BoJ meetings — September hike increasingly priced; hawkish language = yen rally",
            "MoF intervention — explicit warnings above 162-163; physical action forces stop-hunting",
            "FOMC Jun 16-17 — a data-dependent Fed narrows the US-Japan differential",
            "Japan CPI — any upside surprise supports BoJ normalisation",
        ],
        "risks": (
            "A hawkish Warsh widens the differential again; the BoJ delays or sounds dovish (Ueda has surprised "
            "dovishly before); low-vol risk-on keeps the carry trade alive. Stop 163.00."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is ~1500 pips above where the 2yr differential has historically implied.",
            "catalyst":     "2/2 — BoJ hike probability and the MoF intervention threat are both dated and credible.",
            "positioning":  "1/2 — the yen carry trade is crowded long-USD; the low-vol melt-up delays the unwind.",
            "confirmation": "1/2 — price rejected the 160+ handle once; one confirmation of the ceiling.",
            "stop_quality": "1/1 — 163.00 is a clean MoF-intervention ceiling; ~3 pts risk vs ~10 to target.",
        },
    },
    "MM-2026-008": {
        "instrument": (
            "SPX Jun-27 7300/7000 put spread — defined-risk. Buy the 7300 put, sell the 7000 put. "
            "Max profit $300/unit if SPX <=7000 at expiry; max loss = the $35 premium; break-even "
            "~7265. Driven by the SPX level (~7,554), implied vol (VIX ~16.2), and time to expiry."
        ),
        "fundamental_thesis": (
            "The hedge did its job through CPI and Oracle (marked as high as ~$80, +129%) and has given it back: "
            "Monday's melt-up took the S&P to ~7,554, ~250 points above the 7,300 strike, so the spread is deep out "
            "of the money, marked ~$30 — only time value plus the FOMC tail. The single reason to keep it is "
            "Wednesday: Warsh's first dot plot sits inside the Jun 27 expiry, and a VIX crushed to 16.2 makes this "
            "residual downside convexity the cheapest insurance on the board into a binary the market is treating as "
            "a non-event. Hold through FOMC; the residual value IS the dot-plot tail. The fresh, nearer-dated "
            "expression is MM-017."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — hawkish dots push SPX toward 7,000 and the spread toward intrinsic",
            "May Retail Sales Jun 17 — a soft print plus hawkish dots is the bear combination",
            "MoU signing risk Jun 19 — a collapse pre-signing reopens the geopolitical downside",
        ],
        "risks": (
            "SPX grinds higher on a clean dovish hold and the spread expires near zero; time decay into Jun 27; a "
            "further VIX crush. Max loss remains the $35 premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the gap now is the under-priced FOMC tail (VIX 16.2), not realised intrinsic "
                            "value; the index is well above the strike.",
            "catalyst":     "2/2 — FOMC and Retail Sales both land inside expiry.",
            "positioning":  "2/2 — the market is maximally complacent (VIX 16.2); maximum room for a re-pricing.",
            "confirmation": "0/2 — the SPX is far above the strike; no technical confirmation right now.",
            "stop_quality": "1/1 — defined-risk; max loss is the $35 premium. The stop is conceptual.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (receive/own cut optionality), short "
            "the 10Y (short fiscal-supply risk). Pays when 10Y-minus-2Y widens. Currently ~2Y 4.08% "
            "/ 10Y 4.45%, spread ~+37bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "The cleanest duration expression in the book, and the configuration is intact: the oil-disinflation "
            "impulse pulls the front end down (a data-dependent Fed) while the long end is anchored by fiscal "
            "supply — the exact shape that steepens. Entered at +15bp after an 18-month inversion; the spread sits "
            "near +37bp, ~+150% on the position. A dovish-leaning Warsh Wednesday is the accelerant; a hawkish dot "
            "plot that flattens the front end is the risk. Min-hold to ~Jul 16 keeps it structural through the meeting."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — a pause signal drops the 2Y faster than the 10Y = steepens",
            "Oil disinflation — pulls front-end cut pricing without compressing the long end",
            "Treasury supply at the back end — long-end auctions selling off = steepens",
            "May Retail Sales Jun 17 — a soft print reinforces the front-end rally",
        ],
        "risks": (
            "A hawkish Warsh forces aggressive front-end repricing and the curve re-flattens; a global safe-haven "
            "bid flattens via the long end; a Fed hike inverts the front end. Stop: spread below -10bp."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve is still structurally underpriced versus the late-cycle mean off an "
                            "18-month inversion; the near-term path is FOMC-dependent.",
            "catalyst":     "2/2 — FOMC dots and Retail Sales are direct, dated front-end catalysts.",
            "positioning":  "1/2 — front-end positioning offers some squeeze fuel on a dovish hold.",
            "confirmation": "2/2 — the spread held its widening through two oil-driven sessions; confirmed.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-010": {
        "instrument": (
            "Long DAX / short Nasdaq Composite price ratio. Buy German large-caps (financial/industrial "
            "heavy), sell US tech. The ratio rises when DAX outperforms — driven by ECB-vs-Fed "
            "divergence, EUR/USD, European banks vs US tech, and AI-multiple compression."
        ),
        "fundamental_thesis": (
            "This is the one position the melt-up hurt. Monday the Nasdaq ripped +3.07% (NVDA's $25B bond + buyback "
            "powering the AI cohort) while the DAX added only 1.05% — the short-Nasdaq leg ran against us and the "
            "ratio fell back toward its 0.943 stop. The structural case is unchanged: European financials with a "
            "tightening ECB behind them against a US tech complex carrying record AI-capex leverage into a "
            "hawkish-leaning Warsh. But respect the stop — a clean dovish hold that re-rates the Nasdaq is the trade "
            "that stops it. Held into the FOMC unless 0.943 trips."
        ),
        "catalysts": [
            "ECB hike (delivered Jun 11) — DAX financials NIM tailwind, confirmed",
            "FOMC Jun 16-17 — a hawkish dot plot pressures US tech multiples = ratio up",
            "AI-capex leverage (NVDA $25B bond) — the structural overhang on the US tech cohort",
            "EUR/USD — a softer euro flatters DAX exporters and the USD-denominated ratio",
        ],
        "risks": (
            "A clean dovish hold re-rates the Nasdaq further and the ratio breaks the 0.943 stop; a EUR squeeze on "
            "hawkish ECB commentary hurts DAX exporters; the AI melt-up extends. Stop ratio 0.943."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the cross-region divergence (financials vs AI multiples) is a real structural gap.",
            "catalyst":     "1/2 — the dated ECB catalyst has passed; what remains is event-dependent (FOMC, tech).",
            "positioning":  "2/2 — the US-tech long is crowded and now AI-debt-levered; any unwind is maximum fuel.",
            "confirmation": "0/2 — Monday's +3% Nasdaq ran against the ratio; no confirmation, near the stop.",
            "stop_quality": "1/1 — 0.943 is a clean technical level; the trade is on a short leash here.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "The most contested leg in the book. The ECB delivered +25bp Jun 11 and Lagarde's 'not pre-committing' "
            "removed the forward EUR catalyst — but Monday's risk-on melt-up is mildly EUR-supportive and the DXY "
            "slipped below 100 to ~99.6, so EUR/USD has firmed rather than faded. It is held because the rate-path "
            "asymmetry still favours the dollar (a paused ECB vs a Fed that holds with a hawkish bias) and it pairs "
            "cleanly with long DAX. Respect the 1.182 stop; do not add into the FOMC, which is the resolving event."
        ),
        "catalysts": [
            "ECB pause (Jun 11) — sell-the-fact catalyst, in train",
            "FOMC Jun 16-17 — a hawkish-bias hold supports the dollar vs a paused ECB",
            "Risk-on/peace flows + sub-100 DXY — the offsetting EUR-supportive force to watch",
            "Spec positioning unwind — EUR longs near multi-year highs",
        ],
        "risks": (
            "Peace risk-on and a sub-100 DXY lift EUR broadly; US data disappoints and EUR/USD re-rates higher; a "
            "dovish Warsh sinks the dollar. Stop 1.182."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the mispricing is contained: the ECB hike is priced and the risk-on tape is "
                            "leaning against the position right now.",
            "catalyst":     "2/2 — FOMC Jun 16-17 is a precise, dated catalyst with a clear payoff trigger.",
            "positioning":  "1/2 — EUR spec longs near multi-year highs provide unwind fuel.",
            "confirmation": "0/2 — EUR firmed on the melt-up and the sub-100 DXY; no confirmation this session.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; tight risk vs the target.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receive 2Y swap / long 2Y notes). The 2Y is the market's "
            "real-time forecast of the Fed path over two years — the most policy-sensitive point on the "
            "curve."
        ),
        "fundamental_thesis": (
            "Working, with the oil tailwind deepening. Brent at ~$83 is a disinflation impulse that argues against "
            "the 2026 hike the curve was ~54% pricing — and that pricing has eased to ~47% as oil fell. The 2Y has "
            "eased to ~4.08%. The structural thesis — that the front end over-extrapolated a single payroll into a "
            "hiking cycle — is in force with the oil tailwind behind it. The FOMC is still the gate: a data-dependent "
            "Warsh drops the 2Y 15-20bp; a hawkish debut sends it toward the 4.35% stop. Min-hold through Jun 16. "
            "Do not add ahead of the dots."
        ),
        "catalysts": [
            "Oil collapse (~$83) = forward disinflation fading the 2026-hike pricing (~47%, from ~54%)",
            "FOMC dot plot Jun 16-17 — data-dependent hold drops the 2Y; hawkish dots test the stop",
            "May Retail Sales Jun 17 — a soft print reinforces the no-further-hike read",
            "Jobless claims — any spike weakens the hiking case",
        ],
        "risks": (
            "Warsh delivers a hawkish debut dot plot regardless of oil; the MoU collapses pre-signing and "
            "inflation expectations snap back; a re-acceleration in the labour data. Stop 4.35%; min-hold elapsed."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the oil-disinflation impulse re-widens the gap between the 2Y and the justified "
                            "hiking probability, which has visibly eased (~54% -> ~47%).",
            "catalyst":     "2/2 — the FOMC dot plot is a precise, dated catalyst with direct 2Y transmission.",
            "positioning":  "2/2 — the market is still positioned for a hawkish Warsh; squeeze fuel on a dovish hold.",
            "confirmation": "2/2 — the 2Y eased across two sessions and hike odds fell; confirmed.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~27bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-017": {
        "instrument": (
            "SPX Jul-2 7200/6900 put spread — defined-risk, expiring just after the FOMC. Buy the 7200 "
            "put, sell the 6900 put. Cheap downside convexity across Warsh's first dot plot; nearer-dated "
            "than the held MM-008 and struck closer to a stretched ~7,554 index."
        ),
        "fundamental_thesis": (
            "The relief rally has done the work for us — twice over. VIX collapsed to 16.20 (-8.37% Monday), the "
            "most complacent vol of the cycle, exactly when a new and more hawkish chair's debut dot plot is the "
            "least-priced binary on the board. The market prices Wednesday at ~98% hold and treats it as a "
            "non-event; the dots and the bias shift are the actual event, and at VIX 16 the downside convexity to "
            "own them is the cheapest insurance available. This is the fresh, nearer-dated expression of the FOMC "
            "tail now MM-008 has decayed deep out of the money — defined risk, ~0.9% of notional, expiring Jul 2."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — a hawkish bias shift is the payoff trigger",
            "May Retail Sales Jun 17 — a soft print plus hawkish dots is the bear combination",
            "Post-melt-up positioning — maximum complacency (VIX 16.2) is the fuel",
        ],
        "risks": (
            "A clean dovish hold and the structure decays to near zero; the melt-up extends and VIX falls further; "
            "the premium bleeds with no catalyst. Max loss is the ~0.9% premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — implied vol (16.2) is mispricing a binary the market has decided to ignore.",
            "catalyst":     "2/2 — the FOMC is a precise, dated, high-variance event inside the tenor.",
            "positioning":  "2/2 — maximum complacency (VIX 16.2) right before a new chair's debut dots.",
            "confirmation": "0/2 — no technical confirmation; this is a pre-event convexity buy.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-018": {
        "instrument": (
            "Buy 5y CDX IG protection (or LQD puts) — long credit-spread convexity on the US "
            "investment-grade complex. Pays as IG spreads widen. A defined way to own the second-order "
            "risk of the AI debt boom without shorting any single AI equity."
        ),
        "fundamental_thesis": (
            "NVIDIA just sold $25B of high-grade bonds — its first offering since 2021, boosted from $20B, roughly "
            "three times oversubscribed — and the equity market cheered it. That is the Burry tell made concrete: "
            "the AI capex cycle has become an AI debt boom, and the chip vendor itself is now issuing into it "
            "alongside the hyperscalers (Oracle's $40B raise was the first crack). IG spreads near cycle tights "
            "(~52bp) do not price the supply wave or the dilution/leverage discount the market will eventually "
            "demand. This is a structural pre-position — cheap convexity on the most-owned, now most-levered theme "
            "in the index — sized small, with a hawkish Warsh as the near-term accelerant."
        ),
        "catalysts": [
            "AI debt supply — more mega-cap AI issuance (hyperscalers following NVDA/Oracle) widens IG",
            "FOMC Jun 16-17 — a hawkish dot plot is the near-term spread-widening accelerant",
            "Any AI-capex-return wobble — the equity tell that re-prices the credit",
            "IG net issuance / fund-flow data into a heavy supply calendar",
        ],
        "risks": (
            "The melt-up tightens spreads through 45bp and the convexity bleeds carry; a dovish hold extends the "
            "risk-on credit bid; the AI-capex return narrative stays intact for longer than the structure's tenor. "
            "Sized as a small, carry-aware pre-position; stop on IG through ~45bp."
        ),
        "breakdown_why": {
            "gap":          "2/3 — IG at cycle tights does not price the AI supply wave or the leverage discount.",
            "catalyst":     "1/2 — the supply catalyst is structural and gradual, not a single dated event.",
            "positioning":  "2/2 — the AI complex is the most-owned, now most-levered theme; crowded and complacent.",
            "confirmation": "0/2 — spreads are tight and the equity is celebrating the debt; no confirmation yet.",
            "stop_quality": "1/1 — a spread level (~45bp) is a clean, defined failure threshold.",
        },
    },
    "MM-2026-019": {
        "instrument": (
            "Long transports (IYT — airlines, rail, freight) vs short energy (XLE — integrated oil, "
            "E&P, services). A cross-sector relative-value ratio expressing the oil price as a "
            "two-sided input: a cost for transports, a revenue for energy."
        ),
        "fundamental_thesis": (
            "The peace dividend reprices two sectors in opposite directions off one input, and the input moved "
            "again: Brent fell to ~$83 (two-month low) with the MoU signing Jun 19 and the Strait reopening "
            "immediately without tolls — lower-for-longer once sanctioned Iranian barrels return. Jet fuel is "
            "~25-30% of airline opex and diesel is the freight cost line, so the move is a direct margin tailwind to "
            "transports and a top-line hit to energy. The trade is market-neutral-ish with low beta to Wednesday's "
            "FOMC binary — own the de-escalation theme without a directional macro bet the day before the dots. "
            "Size on the ratio, not the legs."
        ),
        "catalysts": [
            "MoU signing Jun 19 + Strait reopening (immediate, no tolls) — sanctioned barrels = lower-for-longer oil",
            "Crude inventory / OPEC+ response to sanctions relief",
            "FedEx print (Jun 23 AMC) — the freight read-through on volumes and fuel",
            "Summer travel demand data — the airline top-line confirmation",
        ],
        "risks": (
            "The MoU collapses pre-signing and oil snaps back (energy outperforms, transports give back); a global "
            "growth scare hits cyclical transports harder than integrated energy; OPEC+ cuts to defend price. "
            "Stop: ratio -3% from entry."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the two sectors have not fully repriced the deeper oil move relative to each other.",
            "catalyst":     "1/2 — the oil-path catalysts are real but the relative move is gradual.",
            "positioning":  "1/2 — energy length built during the war premium is now offside and unwinding.",
            "confirmation": "1/2 — two lower-oil sessions started the rotation; one confirming leg.",
            "stop_quality": "1/1 — a fixed ratio stop (-3%) is a clean, defined failure threshold.",
        },
    },
}

# ── Regime / dashboard ─────────────────────────────────────────────────────────
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
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},   # FOMC at 3.50-3.75% (held); funding unmoved
    {"name": "MOVE", "level": "~102 (est)", "chg": "easing", "dir": "down"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Mon 15 Jun · TradingView"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~102", "chg": "easing (est)", "dir": "down"},
]

# Per-trade open-book notes (shown in the "yesterday, graded" table).
NOTES = {
    "MM-2026-001": "ECB pause behind it; no forward EUR catalyst. Monday's risk-on melt-up is an AUD tailwind (commodity beta) that presses the short. Slow grind lower from ~1.642. Stop 1.662. Hold.",
    "MM-2026-004": "WORKING. Brent ~$83 is a forward CPI cut; the 10Y eased to ~4.45% (one-month lows). The winning side of the MoU binary. FOMC Wed is the gate; data-dependent hold = 10Y toward 4.30%. Do not add. Stop 4.65%.",
    "MM-2026-005": "FLIPPED TO WORKING — for a new reason. We modelled gold deflating on the MoU; instead it rose a 3rd session to ~$4,316 as lower oil cut hike odds and the REAL-RATES engine took over. A dovish Warsh extends it; hawkish dots reverse it first. Min-hold to ~Jul 15; stop $4,250.",
    "MM-2026-007": "Near flat ~160. Differential set to narrow (BoJ Sept hike >50% priced; data-dependent Fed). The low-vol melt-up (VIX 16) keeps carry on — the near-term headwind. MoF ceiling 163 is the backstop. Stop 163.00.",
    "MM-2026-008": "Deep OTM after the melt-up — S&P ~7,554, ~250pts above the 7,300 strike, marked ~$30 (from ~$80 peak). Held ONLY for the FOMC tail inside Jun 27 expiry; VIX 16.2 makes it the cheapest insurance on the board. Hold through Wed; do not lift.",
    "MM-2026-009": "BEST OPEN POSITION (~+150%). The cleanest duration expression: oil-disinflation pulls the front end down while fiscal supply anchors the long end = steepens. ~+37bp; target +60bp. A dovish Warsh is the accelerant. Min-hold to ~Jul 16; stop -10bp.",
    "MM-2026-010": "THE POSITION THE MELT-UP HURT. Nasdaq +3.07% (NVDA's $25B bond + buyback) vs DAX +1.05% drove the ratio back toward the 0.943 stop. Structural divergence intact but on a short leash. Held into FOMC unless 0.943 trips.",
    "MM-2026-012": "MOST CONTESTED LEG. Risk-on melt-up + sub-100 DXY (~99.6) firmed EUR/USD against us. Held on the rate-path asymmetry (paused ECB vs hawkish-bias Fed); pairs with long DAX. Do not add into FOMC. Stop 1.182.",
    "MM-2026-013": "WORKING. Oil ~$83 faded the 2026-hike pricing to ~47% (from ~54%); 2Y eased to ~4.08%. The over-extrapolation thesis is in force. FOMC Wed is the gate; data-dependent hold drops it 15-20bp. Min-hold elapsed; do not add. Stop 4.35%.",
}

# Notes for the closed ledger (keyed by id; falls back to the exit reason).
CLOSED_NOTES = {
    "MM-2026-006": ("STOPPED June 8. Q2 beat but the Q3 AI guide ($16.0B vs buy-side $17.2B) missed the number that "
                    "mattered at 41x; payrolls finished it."),
    "MM-2026-002": ("The US-Iran MoU (signs Jun 19, reopens the Strait immediately without tolls) removed the "
                    "re-escalation premium the long was built on. Brent broke the $87 weekly-close exit and the $84 "
                    "stop; now ~$83. The book's MoU binary paid off on the duration side instead — surrendered by "
                    "design, not by surprise."),
    "MM-2026-011": ("Peace deflated the Hormuz tail the call spread owned. With Brent ~$83 the $100 strike is ~$17 "
                    "away and the catalyst is dead. Closed near the $1 discipline level to recover residual premium."),
    "MM-2026-010": ("STOPPED on the melt-up: Monday's +3.07% Nasdaq (NVDA $25B bond + buyback) against a +1.05% DAX "
                    "broke the 0.943 ratio stop. The relief rally re-rated US tech faster than European financials — "
                    "the risk the trade always carried."),
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
for t in trades["closed"]:
    ex = t.get("exit", {})
    result = ex.get("result", "CLOSED")
    note = ex.get("reason") or CLOSED_NOTES.get(t["id"], "")
    graded_rows.append(
        f'<tr><td class="r">&#x26D4; {t["id"]}</td><td>{book.e(t.get("trade",""))}</td>'
        f'<td>{book.e(t.get("entry"))} &rarr; {book.e(ex.get("level"))}</td>'
        f'<td class="num r">{ex.get("pnl_pct",0):+.2f}%</td>'
        f'<td>{book.e(result)} {book.e(ex.get("date",""))}. {book.e(note)} Held {ex.get("days_held","")} days.</td></tr>'
    )
yesterday_graded = (
    '<table><thead><tr><th>ID</th><th>Trade</th><th>Entry &rarr; Current</th>'
    '<th>P&amp;L</th><th>Note</th></tr></thead><tbody>' + "".join(graded_rows) + '</tbody></table>'
)

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
    {"datum": "MM-008 option mark (model est. from spot — deep OTM after the melt-up, ~$30)", "source": "Model estimate (no live option feed)", "asof": TODAY, "stale": True},
    {"datum": "US-Iran MoU: signing ceremony Fri Jun 19 in Switzerland (Pakistan PM Sharif mediating); Strait reopens immediately without tolls, prewar shipping ~30 days, US lifts blockade + sanctions waivers. PENDING.",
     "source": "NPR + NBC News + Fortune (corroborated)", "asof": "2026-06-15", "stale": False},
    {"datum": "Brent ~$83 (-4%+, two-month low) Jun 15 — war premium kept draining toward the MoU signing",
     "source": "Trading Economics + investingLive (corroborated)", "asof": "2026-06-15", "stale": False},
    {"datum": "Mon Jun 15 US close: S&P 7,554.29 (+1.65%); Nasdaq 26,683.94 (+3.07%); Dow 51,671.03 (+0.92%)",
     "source": "TheStreet + Yahoo Finance + Motley Fool (corroborated)", "asof": "2026-06-15", "stale": False},
    {"datum": "NVIDIA $25B high-grade bond sale Jun 15 — first since 2021, boosted from $20B, ~3x oversubscribed (~$85B orders) + fresh buyback; powered the AI/semis rip",
     "source": "Bloomberg + Futunn + SEC 424B5 (corroborated)", "asof": "2026-06-15", "stale": False},
    {"datum": "VIX 16.20 close Jun 15 (-8.37%) — vol crushed to cycle-complacent into the FOMC",
     "source": "Yahoo Finance / CBOE", "asof": "2026-06-15", "stale": False},
    {"datum": "Gold ~$4,316 Jun 15 (3rd up session) — real-rates engine, NOT safe-haven, drove it",
     "source": "CBS News + Sunday Guardian (corroborated)", "asof": "2026-06-15", "stale": False},
    {"datum": "DXY 99.56 (-0.19%) Jun 15 — dollar slipped below 100 on the risk-on/dovish-hold repricing",
     "source": "Trading Economics", "asof": "2026-06-15", "stale": False},
    {"datum": "FOMC Jun 16-17: Warsh's first meeting (sworn in May 22); decision Wed 2pm ET; ~98% priced HOLD at 3.50-3.75%; dot plot/bias-shift the event; 2026-hike odds eased to ~47% (from ~54%)",
     "source": "CME FedWatch + FXStreet + Kiplinger", "asof": "2026-06-16", "stale": False},
    {"datum": "CAVEAT: Israel says it won't be bound by the Iran deal, vows to stay in south Lebanon; IDF struck Beirut area Jun 14 (US restrained Iran's response); conflicting Iranian-media draft circulates",
     "source": "Times of Israel + PBS + Fortune (corroborated)", "asof": "2026-06-15", "stale": False},
    {"datum": "JBL (Jabil) reports Jun 17 BMO — consensus EPS 3.109, rev ~$8.64B; 13 buy/4 hold/0 sell; beat last 4 quarters",
     "source": "Finnhub (earnings_data.md, sourced)", "asof": "2026-06-15", "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-06-15", "stale": True},
]

earnings_ideas = [
    {
        "ticker": "JBL", "company": "Jabil Inc",
        "report_date": "2026-06-17", "report_timing": "BMO",
        "mode": "PRE-EARNINGS", "direction": "Long",
        "conviction_score": 6, "conviction_label": "High — data gap flagged",
        "conviction_rationale": (
            "Jabil is the under-the-radar AI-infrastructure hardware play, and the asymmetry is a consistent-beat "
            "machine reporting into the exact tailwind the tape is celebrating. It has beaten consensus four "
            "quarters running (6.2%, 4.52%, 11.46%, 9.3%), carries TTM revenue growth of 19% and EPS growth of "
            "78.78%, and the sell side is 13 buy / 4 hold / 0 sell — into a session where the AI-capex/data-center "
            "build (NVDA's $25B bond) is the dominant theme. The data gap is positioning (short-interest "
            "unavailable), which caps the label."
        ),
        "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 2, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Reports Jun 17 BMO. Consensus EPS 3.109 on revenue ~$8.64B (Finnhub-sourced). Beat in each of the last "
            "four quarters — a high-probability beat machine into a supportive tape.",
            "Growth is real: TTM revenue +19%, EPS +78.78% YoY; 52-week range $175.08–$386.64. Sell side 13 buy / "
            "4 hold / 0 sell, period 2026-06-01.",
            "The catalyst the consensus may underprice: Jabil is levered to the data-center/AI-infrastructure build "
            "that powered Monday's rip (NVDA $25B bond, hyperscaler capex). The guide on AI/cloud hardware demand "
            "is the swing.",
        ],
        "what_moves_it": ("The AI/data-center hardware guide and margin trajectory vs an already-buy-heavy sell "
                          "side. A raise extends the AI-infra read-through; a cautious guide on tariff/freight "
                          "cost is the offset. Bear: a guide-down on hardware demand into a stretched tape."),
        "client_talking_point": ("Jabil is the quiet AI-infrastructure beat machine — four straight beats, +79% EPS "
                                 "growth, 13 buys and no sells — reporting Wednesday morning into the exact "
                                 "data-center theme the market is paying up for. We like it long into the print; the "
                                 "only gap is positioning data we can't verify."),
    },
]

brief = {
    "regime":      regime,
    "regime_note": regime_note,
    "dashboard":   dashboard,
    "rates_levels": rates_levels,
    "staleness":   staleness,
    "yesterday_graded": yesterday_graded,
    "earnings_ideas": earnings_ideas,
    "trade_enrichments": TRADE_ENRICHMENTS,
    "rsi_data": rsi_data,
    "idea_rsi_data": idea_rsi_data,

    "dominant_theme": (
        "MAXIMUM COMPLACENCY INTO THE DOTS. The peace dividend became a melt-up: Monday the S&P rose 1.65% to "
        "7,554, the Nasdaq jumped 3.07%, and Brent fell to ~$83 as the US-Iran MoU moved toward a Fri Jun 19 "
        "signing. NVIDIA's $25B oversubscribed bond + buyback powered an AI rip — the Burry tell made concrete. "
        "Gold ROSE to ~$4,316 as the real-rates engine took over from the safe-haven engine. VIX crushed to 16.2 — "
        "the most complacent vol of the cycle — 24 hours before Warsh's FIRST dot plot (Wed 2pm). A hold is ~98% "
        "priced; the dots are the event, and at VIX 16 BOTH tails are cheap to own. The book is leaning the right "
        "way; the discipline is to hedge the concentration and open no new directional macro before 2pm Wednesday."
    ),

    "summary_narrative": """
<p>The peace dividend became a melt-up, and the tape now sits at the most complacent vol of the cycle one day
before the only event it has not priced. Monday June 15 was a risk-on rout to the upside: the S&amp;P 500 rose
1.65% to <strong>7,554.29</strong>, the Nasdaq Composite jumped <strong>3.07%</strong> to 26,683.94 &mdash;
worst-to-first &mdash; and the Dow added 0.92% to 51,671.03. (TheStreet, Yahoo, Motley Fool.) The relief rally
this brief flagged on Friday arrived, and it arrived bigger than we modelled.</p>

<p>Oil kept falling. Brent plunged roughly 4% toward <strong>$83</strong>, a two-month low, as the war premium
drained and the US-Iran memorandum of understanding moved toward a <strong>signing Friday June 19</strong> in
Switzerland &mdash; the Strait of Hormuz reopens immediately without tolls, prewar shipping resumes within thirty
days, and the US blockade lifts. Trump posted to Truth Social: &ldquo;Ships of the World, start your engines. Let
the oil flow!&rdquo; Written as pending &mdash; the signing is Friday, not done. (NPR, NBC, Fortune, Trading
Economics.) The deeper oil move only sharpens the disinflation impulse the book's duration trades are built on.</p>

<p>Two things changed our read since Friday. First, <strong>gold did not deflate on the peace &mdash; it
rose</strong>, a third straight session to roughly $4,316, because the oil collapse cut hike odds, pulled real
yields lower, and the real-rates engine took over from the safe-haven engine. The book's gold (MM-005, the live
4GLD) is working for a new reason. (CBS, Sunday Guardian.) Second, the AI complex ripped on a fact that is also
the structural warning: <strong>NVIDIA sold $25B of high-grade bonds</strong> &mdash; its first offering since
2021, boosted from $20B, roughly three times oversubscribed at about $85B of orders &mdash; and paired it with a
fresh buyback. The market cheered the borrowing. It is the very capital-markets dependency the Burry tell warned
of, now arriving at the chip vendor itself, not only the hyperscalers. (Bloomberg, Futunn.)</p>

<p>The relief crushed VIX to <strong>16.20</strong> (down 8.37% on the day), the most complacent vol of the
cycle, into Kevin Warsh's first FOMC. The decision lands <strong>Wednesday at 2pm ET</strong>: a hold at
3.50&ndash;3.75% is ~98% priced; the event is the dot plot and whether the new chair shifts the bias from easing
toward neutral. The oil collapse has eased 2026 hike odds to ~47% from ~54% (CME FedWatch) &mdash; which means
the consensus framing that the only risk is a hawkish surprise is now wrong in both directions. At VIX 16 a
dovish-hold tail and a hawkish-dots tail are both cheap to own, and that asymmetry is the single best trade on
the board.</p>

<p>The honest caveats hardened rather than softened. Israel's ministers say Israel will <strong>not be bound by
the Iran deal</strong> and vow to stay in south Lebanon; renewed IDF strikes hit the Beirut area on June 14 (the
US restrained Iran's response so the MoU could move forward); and a conflicting Iranian-media draft is
circulating. The tape has priced a clean peace and a non-event Fed. The brief has priced neither &mdash; the
posture is two-sided, the concentration is hedged, and no new directional macro bet is opened before the dots.</p>
""",

    "takeaways": [
        "<strong>The relief rally arrived &mdash; bigger than modelled.</strong> Monday: S&amp;P +1.65% to "
        "7,554.29, Nasdaq +3.07% to 26,683.94 (worst-to-first), Dow +0.92%. Friday's flagged peace bounce became a "
        "full melt-up. Brent fell further to ~$83 (two-month low) as the US-Iran MoU heads to a Jun 19 signing that "
        "reopens the Strait immediately without tolls. (TheStreet, Yahoo, NPR, Trading Economics.)",

        "<strong>Gold flipped to working &mdash; for a NEW reason.</strong> We modelled gold deflating on the peace; "
        "instead it rose a third session to ~$4,316. Lower oil cut hike odds, real yields fell, and the real-rates "
        "engine took over from the safe-haven engine. MM-005 (the book's 4GLD) is back above its $4,250 stop. A "
        "dovish Warsh extends it; hawkish dots reverse it first. (CBS, Sunday Guardian.)",

        "<strong>NVIDIA's $25B bond is the Burry tell made concrete.</strong> First offering since 2021, boosted "
        "from $20B, ~3x oversubscribed (~$85B of orders), paired with a buyback &mdash; and the market cheered the "
        "borrowing. The AI capex cycle has become an AI debt boom, now at the chip vendor itself, not just the "
        "hyperscalers. It powered the semis rip AND is the structural risk we now own via fresh IG-protection "
        "convexity (MM-018). (Bloomberg, Futunn.)",

        "<strong>VIX 16.2 is the trade.</strong> The melt-up crushed vol to the most complacent of the cycle, 24h "
        "before Warsh's first dot plot. A hold is ~98% priced; the dots are the event; 2026-hike odds eased to ~47% "
        "from ~54% (CME FedWatch). At VIX 16 BOTH tails are mispriced &mdash; the held put spread (MM-008) and the "
        "fresh, nearer-dated dot-plot tail (MM-017) own that asymmetry cheaply. (FXStreet, Kiplinger.)",

        "<strong>The melt-up hurt exactly one position.</strong> Long-DAX / short-Nasdaq (MM-010): Monday's +3.07% "
        "Nasdaq (NVDA bond + buyback) against a +1.05% DAX drove the ratio back toward its 0.943 stop. The "
        "structural divergence is intact but on a short leash &mdash; a clean dovish hold that re-rates the Nasdaq "
        "is the trade that stops it. Held into FOMC unless 0.943 trips.",

        "<strong>The duration book is the winning side, confirmed.</strong> Brent ~$83 deepened the disinflation "
        "impulse: the 10Y eased to one-month lows ~4.45% (MM-004), the 2Y to ~4.08% (MM-013), and the 2s10s "
        "steepener (MM-009, ~+150%) is the cleanest expression. Held, not added &mdash; the dot plot is the gate, "
        "and adding duration into the print is not edge.",

        "<strong>The peace is not signed, and Israel is the wildcard.</strong> Israel says it won't be bound by "
        "the deal and vows to stay in south Lebanon; the IDF struck the Beirut area Jun 14; a conflicting "
        "Iranian-media draft circulates. The signing is Friday. The asymmetry of a deal that slips &mdash; Brent "
        "back toward $92-100, the whole disinflation read reversing &mdash; is large and almost entirely unpriced.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "Warsh data-dependent hold + MoU signs clean — disinflationary melt-up extends",
         "body": "Warsh leans on the oil-disinflation impulse, holds at 3.50-3.75%, keeps a 2026 cut on the table "
                 "and lets the dots drift dovish; the MoU signs Jun 19 and Brent settles toward $78-82. The 2Y "
                 "falls 15-20bp, the curve steepens hard, gold extends on lower real yields, and the beaten cohorts "
                 "(software/Adobe, rate-sensitives) re-rate. Risk up · rates down · dollar soft · oil down · gold up."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "Hawkish-neutral hold — bias to neutral, melt-up digests",
         "body": "Warsh holds and shifts the bias from easing to neutral with firm inflation-vigilance language, no "
                 "cut signal and no hike penciled. Brent holds $82-86 on sanctioned-barrel uncertainty. The 2Y "
                 "holds ~4.05-4.15%, the steepener grinds, equities range after the +3% Nasdaq pop and the most "
                 "complacent vol of the cycle gives back. Risk mixed · rates steady · dollar firm · oil soft · gold flat."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "Hawkish dots OR the MoU fractures pre-signing",
         "body": "Warsh pencils a 2026 hike into the dots on the still-hot PPI and frames the oil move as transitory "
                 "&mdash; the 2Y jumps toward the 4.35% stop, gold gives back, AI multiples compress and the S&amp;P "
                 "retraces toward 7,200-7,000 where the put spreads pay; AND/OR Israel's refusal to be bound "
                 "fractures the deal before Friday and Brent snaps back toward $92-100. Risk down · rates up · "
                 "dollar up · oil/gold spike."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a single number that has not yet been recognised as a monetary one: Brent
at $83. A crude move of roughly $45 off the war highs is not a commodity story &mdash; it is a forward
disinflation impulse arriving exactly as Kevin Warsh prepares his first dot plot. The FedWatch curve repriced
hawkishly after the hot PPI and was carrying ~54% odds of a 2026 hike; that pricing has already eased to ~47% as
oil fell. The non-consensus read: the oil collapse has quietly handed the new chair the cover to stay patient,
and the market &mdash; fixated on Warsh's hawkish reputation &mdash; is mispricing the dovish-hold path. That is
why the duration longs (MM-004, MM-013) and the steepener (MM-009) are the cleanest expressions in the book, and
why gold (MM-005) flipped to working on the real-rate channel rather than the safe-haven one.</p>

<p>The counter-intuitive hook is what the equity tape chose to celebrate. NVIDIA sold $25B of high-grade bonds,
its first since 2021 and roughly three times oversubscribed, and the stock led a +3% Nasdaq day. Consensus read
the borrowing as a vote of confidence in the AI build. The second-order effect it is missing: the marquee name in
the AI trade is now funding its capex with debt, joining Oracle's $40B raise, and the equity market is paying up
for leverage it will eventually demand a discount for. The flow is bullish today; the structure is the warning.
This is the Burry tell made concrete, and it is the basis for owning cheap IG-spread convexity here (MM-018).</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong>
oil at $83, the 10Y at one-month lows ~4.45%, a 2s10s curve near +37bp, an equity tape at fresh highs, gold rising
on real rates. <strong>What is priced:</strong> a ~98% FOMC hold and, beneath it, a VIX of 16.2 that treats
Warsh's debut as a non-event. <strong>Consensus narrative:</strong> &lsquo;the new chair is a hawk, so the only
risk is a hawkish surprise.&rsquo; The gap &mdash; and the alpha &mdash; is that the same complacent vol that
under-prices a hawkish surprise also under-prices a dovish one; the oil collapse makes the dovish path more likely
than the market believes, and either tail is the cheapest insurance on the board at VIX 16.</p>

<p>Go around the world. <strong>Asia:</strong> lower oil is an unambiguous positive for the energy-importing
North-Asian complex (Japan, Korea, India), and the AI-memory chain (HBM, Micron) ripped with the cohort.
<strong>Japan:</strong> USD/JPY near 160 with the MoF on watch and a BoJ September hike >50% priced &mdash; the
carry unwind is a question of when, and a VIX-16 melt-up delays it. <strong>Europe:</strong> the DAX added 1.05%
but lagged a +3% Nasdaq, which is the one place the divergence trade hurt &mdash; European financials still carry
the cleanest ECB-NIM tailwind into a peace dividend, but the AI melt-up is the near-term counterforce.</p>

<p>The political angle the market is under-weighting is no longer the deal's existence &mdash; it is Israel. The
MoU reportedly bundles an Israel-Hezbollah ceasefire requiring Hezbollah disarmament and an IDF withdrawal from
south Lebanon, yet Israeli ministers say plainly that Israel will not be bound by the US-Iran agreement and will
stay in the south. The non-consensus read: the binding constraint on this peace is not Tehran or Washington but
Jerusalem, and the oil market's straight-line move to $83 has front-run a signature that a third party can still
break. That is the asymmetry behind not chasing crude lower even as the oil longs are surrendered.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the FOMC dot-plot binary in both directions (VIX 16.2 is the
cheapest it has been into a Fed meeting this cycle); the dovish-hold path the oil collapse has made more likely;
the AI-debt leverage discount. <strong>Fairly priced:</strong> the FOMC hold itself (~98%); the ECB pause.
<strong>Fully priced:</strong> the straight-line peace move in oil (Brent at $83 has front-run an unsigned deal).
<strong>Over-priced (at risk):</strong> the consensus framing that the only FOMC risk is hawkish &mdash; and the
durability of a peace Israel says it will not honour.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is not in the peace deal and not in the dot plot. It
is that the market has spent the disinflation, celebrated the leverage, and crushed the vol &mdash; all before the
one event that can revalue every one of those positions. The tape has priced a clean peace, a non-event Fed, and
an AI complex that can borrow its way to the buildout. The trade is owning the gap between that complacency and
Wednesday at 2pm.</p>

<p>Start with the melt-up, because its scale is the story. The Nasdaq Composite rose more than three percent on
Monday and the S&amp;P closed at 7,554, both on the back of a US-Iran memorandum heading to a Friday signing and
a Brent price that fell to eighty-three dollars, a two-month low (TheStreet, Yahoo, Trading Economics). This brief
flagged the relief rally on Friday; it did not flag its size, and the honest lesson is that a regime change priced
in real time runs further than the model that anticipates it. The oil book paid for the war view on the way up and
surrendered it on the way down without regret &mdash; the long Brent and the call spread are closed &mdash; and
the duration side of the same binary is the clean winner, with the ten-year at one-month lows and the two-year at
4.08%.</p>

<p>The deeper oil move is what makes this a Fed story rather than a commodity one. A forty-five-dollar collapse in
crude from the war highs is the fastest disinflationary force in the macro toolkit, and it has already pulled the
market-implied odds of a 2026 hike from roughly fifty-four percent to forty-seven. Consensus has decided that the
only risk from Kevin Warsh's first meeting is a hawkish surprise, on the strength of his reputation and a hot PPI.
The oil price has quietly made the dovish-hold path more likely than that framing allows, and a VIX crushed to
16.2 prices neither tail. That is the cleanest mispricing on the board: not a directional bet on the Fed, but a
cheap bet that the Fed matters at all, which is why the held put spread and a fresh, nearer-dated put structure
are the two instruments carried into Wednesday.</p>

<p>Gold and Nvidia are the two single-name lessons of the session, and they point in opposite directions. Gold
rose a third day to roughly $4,316, and the reason matters: not the safe-haven bid we modelled draining on the
peace, but the real-rate channel re-rating bullion as hike odds fell. The position is working for a different
engine than the one it was entered on, which is a reminder to track the mechanism, not the label. Nvidia, meanwhile,
sold twenty-five billion dollars of bonds to roughly eighty-five billion of orders and the equity celebrated
(Bloomberg, Futunn). The market read the demand as confirmation; the brief reads the issuance as the moment the AI
capex cycle became an AI debt boom at the vendor level, not just the hyperscaler level. The flow is a tailwind
today and the structure is a tell for the next two-to-three quarters, and the cheap way to own that tell is
investment-grade spread convexity while spreads sit at cycle tights.</p>

<p>The book's posture into the meeting is therefore two-sided and deliberately uncrowded. The duration longs and
the steepener are the winning side of the MoU binary, held but not added ahead of the dots. Gold is held on its
new real-rate engine, flagged as the first hedge to give back if Warsh hawks up. The long-DAX ratio is the one
position the melt-up hurt and is on a short leash at its stop. The short-EUR leg is contested by a sub-100 dollar
and is not added into the Fed. The fresh ideas are the dot-plot tail at VIX 16, the IG-protection convexity behind
the Nvidia bond, and the transports-versus-energy relative value off the oil move &mdash; none of them a
directional macro bet, because the discipline the day before a new chair's first dot plot is to own the binary
cheaply and force nothing. The tape has priced a clean peace and a quiet Fed. Israel says the first is not
binding, and VIX 16 says the second is free to doubt.</p>
""",

    "correlation_regime": """
<p><strong>1. Gold de-coupled from the peace and re-coupled to real rates.</strong> The intuitive correlation was
peace-down-gold; that broke. Gold rose a third session to ~$4,316 even as the geopolitical premium drained,
because the oil collapse cut hike odds and pulled real yields down. The dominant driver of gold just switched from
the safe-haven channel to the real-rate channel &mdash; which is why MM-005 is now a Fed trade, not a war trade.</p>

<p><strong>2. The DAX / Nasdaq divergence inverted for a session.</strong> The long-DAX / short-Nasdaq thesis
relies on US tech lagging European financials. Monday it ran the other way: the Nasdaq +3.07% (NVDA's $25B bond +
buyback) crushed the DAX's +1.05%. A one-session inversion driven by a single AI-credit event is not a regime
change &mdash; but it pushed the ratio to its 0.943 stop, so the position is now hostage to whether Wednesday
re-rates or de-rates US tech.</p>

<p><strong>3. AI equity and AI credit are decoupling in plain sight.</strong> Nvidia's stock rose on the same news
&mdash; a $25B debt sale &mdash; that should widen its credit. The equity is pricing the buildout; the credit is
not yet pricing the leverage. That gap between an exuberant equity and complacent IG spreads is the cleanest
correlation break in the tape, and the basis for owning IG protection (MM-018) before the two re-converge.</p>
""",

    "vol_skew": """
<p><strong>The melt-up crushed vol into the one event that matters &mdash; again.</strong> VIX closed 16.20 on
Monday, down 8.37%, and the term structure is in steep contango (est. VIX9D ~15.0 · VIX ~16.2 · VIX3M ~18.5 ·
VIX6M ~20.0) &mdash; the textbook complacent shape. The problem is the timing: it prices Kevin Warsh's first dot
plot, one day out, as a non-event. A new and more hawkish chair's debut SEP is a genuine two-sided binary
(2026-hike odds ~47%), and complacent front-month vol under-prices <em>both</em> tails. The trade implication: own
gamma into Wednesday at the cheapest level of the cycle. The held 7300/7000 put spread (MM-008) is the legacy
expression, now deep OTM after the +3% Nasdaq day; the fresh idea (MM-017) is a Jul-2 7200/6900 put spread at
~0.9% of notional &mdash; struck closer to a stretched 7,554 index, expiring just after the meeting, ~$30 of
premium for a ~$300 payoff if the dots send the S&amp;P toward 7,000.</p>
""",

    "sector_rv": """
<p><strong>Leading:</strong> US semis &amp; AI (Nasdaq +3.07%; NVDA's $25B bond + buyback, Micron/Intel/Western
Digital/Meta), transports/airlines (lower jet fuel = margin tailwind), beaten software (Adobe the dislocation),
North-Asian energy importers (Japan/Korea on cheaper crude).
<strong>Lagging:</strong> energy producers (XLE rolling over as the war premium unwinds; sanctioned Iranian
barrels are the overhang), defense (de-escalation fades the war bid), European exporters relative to US tech this
session.
<strong>This week's watch:</strong> Jabil (Jun 17 BMO) on AI/data-center hardware demand; the read-through feeds
the AI-infra cohort. FedEx is Jun 23 (out of this week's window).</p>

<p><strong>RV:</strong> The cleanest fresh RV is long transports (IYT) / short energy (XLE) &mdash; the deeper oil
move (~$83) reprices the two sectors in opposite directions, with low beta to Wednesday's FOMC (idea MM-019). The
standing cross-region RV, long DAX / short Nasdaq (MM-010), is the position the melt-up hurt &mdash; at its 0.943
stop after the +3% Nasdaq day. Hold into FOMC; a hawkish dot plot is what rescues it.</p>
""",

    "positioning": """
<p><strong>The crowd is maximally long risk and maximally short vol into a new chair's first dot plot.</strong>
The melt-up pushed the Nasdaq +3% and VIX to 16.2 &mdash; complacency is the position, and a hawkish surprise is
the pain trade for the broad market. In rates, the crowd repriced toward the hawkish read on the PPI and is now
caught as oil drains hike odds toward ~47%; the squeeze on a data-dependent hold is the upside for the duration
longs and the steepener. In credit, IG sits at cycle tights as mega-cap AI names (NVDA, Oracle) flood the
high-grade market &mdash; the crowd is long the issuance and not pricing the leverage, which is the setup for
IG-protection convexity. In FX, EUR longs that bought the ECB hike are being bailed out by the risk-on melt-up and
a sub-100 dollar (MM-012 contested). The single pain trade that the complacent VIX is positioned for in neither
direction is a Warsh dot plot that surprises &mdash; hawkish OR dovish.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged through the melt-up. <strong>The Pozsar mechanic:</strong> the more telling
plumbing signal this week is in primary credit, not repo. NVIDIA's $25B high-grade deal drawing ~$85B of orders is
a balance-sheet event &mdash; the AI buildout is migrating from cash-funded capex to debt-funded capex, and the
high-grade market is absorbing it at cycle-tight spreads because reserves are ample and the reach-for-yield bid is
intact. That is benign while liquidity is easy; it is the transmission belt that snaps first if Warsh re-prices the
front end higher and funding tightens for every floating-rate and newly-levered AI borrower at once. The MOVE index
is easing (est. ~102) as the oil-driven bond rally pulls realised rate vol lower. Watch IG spreads into the Fed:
they tighten further if the dots read as the terminal ceiling, and gap out if Warsh re-opens the hike door &mdash;
the latter is exactly the convexity MM-018 owns.</p>
""",

    "tape_missing": """
<p><strong>The tape is not pricing the dovish-hold path.</strong> The market has fixed on Warsh's hawkish
reputation and decided the only FOMC risk is hawkish, so a ~98% hold sits over a VIX of 16.2 &mdash; the most
complacent vol into a Fed meeting this cycle. The oil collapse to $83 is a forward CPI cut that hands the new chair
cover to stay patient, and it has already pulled 2026-hike odds to ~47%. If Wednesday's dots keep a 2026 cut alive
and Warsh leans on the disinflation impulse, the 2Y falls 15-20bp, the curve steepens hard, gold extends, and the
beaten cohorts re-rate. That path is barely in the price. The duration longs (MM-004, MM-013), the steepener
(MM-009) and gold (MM-005) are the instruments for it.</p>

<p><strong>Just behind it: the peace has a third party that says it won't sign.</strong> Israel's ministers state
Israel will not be bound by the US-Iran MoU and will stay in south Lebanon, even as the deal reportedly bundles an
Israel-Hezbollah ceasefire. The signing is Friday; the IDF struck the Beirut area Jun 14. The oil market has
front-run a clean peace to $83; if Jerusalem breaks it before Jun 19, Brent snaps back toward $92-100 and the whole
disinflation read reverses. We do not chase crude lower here precisely because the binding constraint is a party
not at the signing table. The asymmetry of a deal that slips is large and almost entirely unpriced.</p>

<p><strong>The Burry tell &mdash; the structural thing nobody is looking at.</strong> The AI infrastructure trade
has become a capital-markets trade, and Nvidia's $25B bond is the confirmation: the vendor at the centre of the
cohort is now funding the buildout with debt, after Oracle funded $90-95bn of annual capex with a $40bn raise. The
question nobody is pricing is what happens when Microsoft, Google, Amazon and Meta all face the same equation and
the market starts demanding a leverage-and-dilution discount from each of them at once. The free-cash-flow
inflection on the hyperscaler build is three-to-four years out, not twelve-to-eighteen months, and the equity is
still pricing the backlog without pricing the capital drag. That resolves badly for the most-owned cohort in the
index over the next two-to-three quarters &mdash; and a hawkish Warsh would be the accelerant. The cheap way to be
early is IG-spread convexity at cycle tights (MM-018), not shorting the equity into a melt-up.</p>
""",

    "book_outlook": {
        "commentary": (
            "The melt-up leaned the book the right way and changed two of its underwater stories. The "
            "oil-disinflation impulse and the AI rip are a double tailwind to the book's <b>largest risk &mdash; "
            "the US AI-semis concentration (Micron ~25.8%, plus NVDA/AVGO/AMD)</b> &mdash; which had its best "
            "session in weeks (Nasdaq +3.07%, led by NVDA's $25B oversubscribed bond + buyback). The "
            "<b>US Treasury 1.25% 2031</b> rallied as the 10Y eased to one-month lows ~4.45%. And the story that "
            "flipped: <b>Xetra-Gold (4GLD)</b> &mdash; we expected the peace to deflate it, but it ROSE to ~$4,316 "
            "as the real-rates engine took over, so the book's tail hedge is, for now, also a winner. The drag is "
            "<b>TotalEnergies (TTE)</b>, the book's energy hedge, which rolls over as the war premium unwinds "
            "(Brent ~$83). The dominant risk is tomorrow 2pm: a hawkish Warsh dot plot compresses the 25.8% semis "
            "concentration hardest AND is the one thing that reverses gold first. Hedge the concentration into the "
            "dots; do not chase it higher into the most complacent vol of the cycle."
        ),
        "outperform": [
            {"name": "US AI-semis (Micron 25.8%, NVDA/AVGO/AMD)", "why": "Best session in weeks &mdash; Nasdaq "
             "+3.07% led by NVDA's $25B oversubscribed bond + buyback; the SpaceX-drain fear is dead and a possible "
             "dovish-hold eases real-rate pressure on the multiple. The book's largest position is leaning the right "
             "way &mdash; but do not chase it into the dots."},
            {"name": "Xetra-Gold (4GLD)", "why": "Flipped to working: rose to ~$4,316 (3rd session) as lower oil cut "
             "hike odds and the real-rates engine re-rated bullion &mdash; the opposite of the peace-deflation we "
             "modelled Friday. A dovish Warsh extends it."},
            {"name": "US Treasury 1.25% 2031", "why": "The 10Y eased to one-month lows ~4.45% on the deeper oil "
             "move; the bond rallies with the winning side of the MoU binary."},
        ],
        "underperform": [
            {"name": "TotalEnergies (TTE)", "why": "The book's energy hedge rolls over as the war premium unwinds "
             "(Brent ~$83); sanctioned Iranian barrels are the supply overhang into the Jun 19 signing."},
            {"name": "USD cash sleeve ($3.0m idle)", "why": "Opportunity cost on a +3% Nasdaq day &mdash; cash "
             "earning ~SOFR while the melt-up runs. The fix is to put it to work selling cash-secured NVDA puts to "
             "add the name lower, after the Fed."},
        ],
        "watch": [
            {"label": "Hedge the 25.8% semis concentration into the dots", "text": "Micron at 25.8% plus the semis "
             "stack is the book's amplifier in both directions, and a hawkish Warsh dot plot compresses it hardest. "
             "Keep the SPX put structures (MM-008 / MM-017) as the index hedge; do not add semis before Wed 2pm."},
            {"label": "Gold is now a real-rates trade, not a war hedge", "text": "4GLD rose on falling real yields, "
             "not on geopolitics &mdash; so it is the first hedge to give back on hawkish dots. Let it run into a "
             "dovish-hold, but recognise the engine changed and size the tail accordingly."},
            {"label": "Put the idle cash to work after the Fed", "text": "€2.4m sits idle into a paused ECB and "
             "$3.0m into a ~4% T-bill; the USD sleeve funds cash-secured NVDA puts to add the name lower post-dots. "
             "Do not redeploy into the melt-up before Wednesday."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> Kevin Warsh is a hawk, so his first FOMC is a hawkish risk &mdash; the dots
will shift toward tightening on the still-hot PPI, real yields rise, and the melt-up is the moment to fade
equities, gold and duration. The new chair has every incentive to establish credibility early, and the hot PPI
gives him the cover.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> the oil collapse changed the inflation
picture after the PPI print, not before it. Brent down to $83 is a disinflation impulse that has already pulled
2026-hike odds to ~47% and hands Warsh cover to hold data-dependent without looking dovish, and a VIX at 16.2 is
positioned for neither tail. Consensus has pre-committed to the hawkish read; the oil price has quietly tilted the
odds the other way, and at the most complacent vol of the cycle that is the cheaper side to own going into
Wednesday.</p>
""",

    "one_chart": """
<p class="theme">VIX 16.2 is the chart &mdash; the cheapest insurance into a Fed meeting this cycle, one day
before a new chair's first dot plot.</p>
<p>The single thing the market watches today is the melt-up, but the level that changes the story is the 2Y at
4.08% read against the dots. A data-dependent Warsh leaning on $83 oil sends the 2Y toward 3.90% and steepens the
curve; a hawkish dot plot that pencils a 2026 hike sends it toward the 4.35% stop and compresses everything the
melt-up just bid. With VIX at 16.2 the market is pricing neither. Watch the 2Y reaction at 2pm Wednesday; own the
binary cheaply until then.</p>
""",

    "catalyst_calendar": [
        {"day": "Mon", "date": "Jun 15 ✓",
         "event": "Risk-on melt-up — Nasdaq +3.07%, Brent ~$83, NVDA $25B bond",
         "consensus": "S&P +1.65% to 7,554.29; Nasdaq +3.07% to 26,683.94; Dow +0.92%. Brent ~$83 (two-month low). "
                      "NVDA sold $25B of bonds (first since 2021, ~3x oversubscribed) + buyback. VIX -8.37% to 16.20. "
                      "Sources: TheStreet, Yahoo, Bloomberg, Trading Economics.",
         "view": ("The relief rally we flagged Friday arrived bigger. Confirmed the regime; the duration longs and "
                  "gold are the winners. The NVDA bond is the Burry tell made concrete (idea MM-018)."),
         "asymmetry": "Resolved positive for risk, but it crushed vol to 16.2 right before the dots — that "
                      "complacency is the asymmetry to own (MM-017).",
         "dir": "up"},
        {"day": "Tue", "date": "Jun 16 ← TODAY",
         "event": "FOMC begins (day 1) — Empire State / housing data; FOMC blackout",
         "consensus": "The two-day meeting opens; no decision today (Wed 2pm ET). Second-tier US data only. Pre-dots "
                      "positioning day into the most complacent vol of the cycle.",
         "view": "The day to set the hedge, not to add directional risk. Own the dot-plot tail cheaply (MM-008, "
                 "MM-017); do not chase the melt-up or add semis.",
         "asymmetry": "Low individually; today is about positioning into Wednesday, not a catalyst in itself.",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 17 — THE EVENT",
         "event": "FOMC decision + dot plot — Warsh's FIRST, 2pm ET; ~98% hold priced",
         "consensus": "Hold at 3.50-3.75% (~98% priced); the dots and any bias shift (easing -> neutral/tightening) "
                      "are the entire event. 2026-hike odds ~47%. Press conference 2:30pm. "
                      "Sources: CME FedWatch, FXStreet, Kiplinger.",
         "view": ("Three paths: (1) data-dependent hold leaning on the oil-disinflation impulse — 2Y -15-20bp, "
                  "steepener accelerates, gold and software/rate-sensitives re-rate; (2) hawkish-neutral — bias to "
                  "neutral, no cut signal, range; (3) hawkish dots (a hike penciled) — 2Y toward 4.35% stop, gold "
                  "gives back, AI multiples compress, put spreads pay. VIX 16.2 under-prices ALL of these."),
         "asymmetry": "The market is positioned only for the hawkish tail. The oil collapse makes the dovish-hold "
                      "path more likely than priced — own gamma both ways (MM-008, MM-017).",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 17",
         "event": "US May Retail Sales + Jabil (JBL) earnings (BMO)",
         "consensus": "Retail Sales (May) lands the same day as the FOMC; Jabil reports BMO — consensus EPS 3.109, "
                      "rev ~$8.64B; the AI/data-center hardware read (Finnhub-sourced).",
         "view": "A soft Retail Sales print plus a hawkish dot plot is the bear combination; a firm consumer plus a "
                 "data-dependent hold is the melt-up combination. Jabil is the long-into-the-print AI-infra read.",
         "asymmetry": "JBL: four straight beats into a supportive AI-capex tape = the asymmetry; the guide on "
                      "hardware demand is the swing.",
         "dir": "flat"},
        {"day": "Fri", "date": "Jun 19",
         "event": "US-Iran MoU signing ceremony — Switzerland",
         "consensus": "Signing scheduled in Switzerland (Pakistan PM Sharif mediating); Strait reopens immediately "
                      "without tolls, US lifts blockade, sanctions waivers. Sources: NPR, NBC, Fortune.",
         "view": ("PENDING. A clean signing = oil toward $78-82, dovish cover confirmed. The live risk is Israel — "
                  "it says it won't be bound by the deal and vows to stay in south Lebanon. Do not chase crude lower "
                  "into the signature."),
         "asymmetry": "Clean signing = lower-for-longer oil. Israel breaks it / it slips = Brent back to $92-100, "
                      "the disinflation read reverses. Large and almost entirely unpriced.",
         "dir": "down"},
        {"day": "Mon", "date": "Jun 23",
         "event": "FedEx (FDX) FY Q4 — after close",
         "consensus": "Reports Jun 23 AMC (not Jun 18). FY26 adj EPS guided $19.30-20.10; Q4 midpoint ~$5.80. The "
                      "freight/global-trade bellwether. Source: Yahoo Finance / TipRanks.",
         "view": "Two-sided: peace + cheaper fuel is a margin tailwind; tariff-driven volume softness is the "
                 "offset. The guide sizes the transports-vs-energy RV (MM-019). Outside this week's window.",
         "asymmetry": "A volume beat with the fuel tailwind = transports leg of MM-019 confirmed; a tariff-driven "
                      "volume miss = the freight cycle is rolling, fade transports.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660. At ~1.642; stop 1.662. ECB pause behind it, no forward EUR catalyst; the risk-on melt-up is a mild AUD tailwind. Slow grind lower. Hold.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.45% (one-month lows). WORKING: Brent ~$83 deepened the forward CPI cut. The winning side of the MoU binary. Data-dependent FOMC = 10Y toward 4.30%. Do NOT add. Hold.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250. At ~$4,316. FLIPPED TO WORKING on the real-rates engine (not the safe-haven engine). A dovish Warsh extends it; hawkish dots reverse it first. Hold.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160. Differential set to narrow (BoJ Sept hike >50% priced; data-dependent Fed); the VIX-16 melt-up keeps carry on — the near-term headwind. MoF ceiling 163 the backstop. Hold.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> S&P ~7,554 → deep OUT of the money, marked ~$30 (from ~$80 peak). Held only for the FOMC tail inside Jun 27 expiry; VIX 16.2 makes it the cheapest insurance on the board. Hold through Wed; do not lift.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+37bp; target +60bp. The cleanest duration expression — oil-disinflation drops the front end, fiscal supply anchors the long end. A dovish Warsh is the accelerant. Hold.</li>
<li><strong>MM-2026-010 · Long DAX / short Nasdaq:</strong> stop ratio 0.943. THE POSITION THE MELT-UP HURT — Nasdaq +3.07% (NVDA bond) vs DAX +1.05% drove the ratio to the stop. On a short leash. Held into FOMC unless 0.943 trips; a hawkish dot plot rescues it.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. At ~1.157. MOST CONTESTED — risk-on + sub-100 DXY firmed EUR against us. Held on the rate-path asymmetry (paused ECB vs hawkish-bias Fed); pairs with long DAX. Do not add into FOMC. Hold.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold elapsed. At ~4.08%. WORKING: oil ~$83 faded 2026-hike pricing to ~47%. Data-dependent FOMC drops it 15-20bp. Do NOT add. Hold.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The market melted up — did we miss it?",
         "a": ("No — the book is leaning the right way. Monday's +3% Nasdaq and +1.65% S&P were powered by the same "
               "two forces our positions are built on: collapsing oil (Brent ~$83) and a possible dovish-hold Fed. "
               "Our duration longs and the curve steepener are the winners, gold flipped to working, and the "
               "semis-heavy side of the book ripped. The one thing we did NOT do is chase it — the day before a new "
               "Fed chair's first dot plot, the discipline is to hedge, not to add.")},
        {"q": "Why did gold go UP if the war is ending?",
         "a": ("Because the engine changed. We expected the peace to deflate gold's safe-haven premium. Instead the "
               "oil collapse cut the odds of Fed hikes, real yields fell, and lower real yields are the single "
               "biggest driver of gold — so it rose a third session to ~$4,316. It's now a real-rates trade, not a "
               "war trade. The one risk: a hawkish Warsh tomorrow is the first thing that would reverse it.")},
        {"q": "Nvidia sold $25bn of bonds and the stock went up — is that good or bad?",
         "a": ("Both, and that's the point. Short term it's a tailwind — the deal was three times oversubscribed and "
               "came with a buyback, so the flow is bullish. Structurally it's the warning: the centre of the AI "
               "trade is now funding its buildout with debt, after Oracle did the same. The equity is pricing the "
               "demand; the credit isn't pricing the leverage yet. We own a small, cheap hedge on that gap (idea "
               "MM-018) rather than shorting a stock into a melt-up.")},
        {"q": "What's the single most important thing this week?",
         "a": ("Wednesday's FOMC at 2pm — Warsh's first as chair. A hold is ~98% priced, so the decision isn't the "
               "event; the dot plot is. The market is positioned only for a hawkish surprise, but the oil collapse "
               "has made a dovish-hold more likely than priced, and VIX at 16.2 — the most complacent of the cycle — "
               "under-prices both tails. We own that binary cheaply through the put spreads and open no new "
               "directional macro bets until after 2pm Wednesday.")},
        {"q": "Is the peace deal actually done?",
         "a": ("Not yet — it's set to be signed Friday in Switzerland, and there's a real wildcard: Israel says it "
               "will NOT be bound by the US-Iran agreement and intends to stay in south Lebanon, even though the "
               "deal reportedly includes an Israel-Hezbollah ceasefire. The binding constraint on this peace isn't "
               "Tehran or Washington — it's Jerusalem. That's why we've surrendered the oil longs but are NOT "
               "chasing crude lower into a signature a third party can still break.")},
        {"q": "Should we take profit on the SPX hedge after that move?",
         "a": ("We already gave the gain back, and we hold anyway. The 7300/7000 put spread marked as high as +129% "
               "through CPI and Oracle; Monday's melt-up took the S&P to ~7,554, so it's deep out of the money at "
               "~$30. The one reason to keep it is tomorrow: Warsh's first dot plot is inside the expiry, and with "
               "VIX crushed to 16.2 it's the cheapest downside insurance on the board. Don't lift it before the Fed.")},
    ],

    "ideas_note": (
        "<p>The day before Warsh's first dot plot, the discipline is to own the binary cheaply and force nothing. "
        "The book's macro posture is set; the fresh ideas are deliberately low-correlation to the dot-plot event. "
        "<strong>SPX dot-plot tail (MM-017)</strong> — at VIX 16.2 the cheapest downside convexity of the cycle "
        "into the meeting, nearer-dated than the decayed MM-008. <strong>IG-protection convexity (MM-018)</strong> "
        "— the Burry tell made tradeable: own cheap credit-spread convexity behind the AI debt boom (NVDA's $25B "
        "bond) while IG sits at cycle tights. <strong>Long transports / short energy (MM-019)</strong> — a "
        "market-neutral-ish peace-dividend RV off the deeper oil move. <strong>No fourth idea, and no new "
        "directional macro before Wednesday 2pm</strong> — forcing a bet in front of the dots is the trap, not the "
        "trade. The duration longs (MM-004, MM-013), the steepener (MM-009) and gold (MM-005) are held, not added.</p>"
    ),

    "event_radar_note": (
        "<p>The relief rally we flagged Friday arrived bigger: Monday the Nasdaq jumped +3.07%, the S&P closed "
        "7,554, Brent fell to ~$83, and NVDA sold $25B of bonds (~3x oversubscribed) + a buyback. Gold flipped to "
        "working on the real-rates engine; VIX crushed to 16.2. Ahead: the FOMC begins today (day 1, no decision), "
        "the dot plot Wed Jun 17 2pm (Warsh's first — the event of the week), Retail Sales + Jabil (JBL) Wed, and "
        "the US-Iran MoU signing Fri Jun 19 (with Israel the live wildcard). The book is the winning side of the "
        "binary on duration and gold; the one position the melt-up hurt is the DAX/Nasdaq ratio (at its stop). No "
        "new directional macro bets before the dots.</p>"
    ),

    "burry_tell": (
        "Nvidia's $25B bond sale — its first since 2021, roughly three times oversubscribed, paired with a buyback "
        "and cheered by the equity — is the AI infrastructure trade completing its transformation into a "
        "capital-markets trade. Oracle was the first crack ($90-95bn of annual capex funded by a $40bn raise); now "
        "the chip vendor at the centre of the cohort is funding the buildout with debt too. The structural thing "
        "nobody is pricing: what happens when Microsoft, Google, Amazon and Meta all face the same equation and the "
        "market starts demanding a leverage-and-dilution discount from each of them at once. The free-cash-flow "
        "inflection on the hyperscaler build is three-to-four years out, not twelve-to-eighteen months, and the "
        "equity is still pricing the backlog without pricing the capital drag. That resolves badly for the "
        "most-owned cohort in the index over the next two-to-three quarters — and a hawkish Warsh would be the "
        "accelerant. It is not a short into a melt-up; it is a reason to own investment-grade spread convexity "
        "(MM-018) while spreads sit at cycle tights, before the equity and the credit re-converge."
    ),

    "earnings_summary": (
        "Jabil (JBL): PRE-PRINT (Jun 17 BMO) — the under-the-radar AI-infrastructure hardware play. Consensus EPS "
        "3.109 on revenue ~$8.64B (Finnhub-sourced); beat in each of the last four quarters (6.2%, 4.52%, 11.46%, "
        "9.3%); TTM revenue +19%, EPS +78.78%; sell side 13 buy / 4 hold / 0 sell. Reports into the exact "
        "data-center/AI-capex theme that powered Monday's rip (NVDA's $25B bond). Long-leaning into the print; the "
        "guide on AI/cloud hardware demand is the swing, and the only data gap is unverifiable positioning. FedEx "
        "is Jun 23 (out of the 5-day window); Adobe (Jun 11) is now outside the 3-day post-window — the long-ADBE "
        "dislocation is carried in Trade Ideas (MM-014), not the earnings section."
    ),
    "earnings_why": (
        "Jabil is the one name that clears the universe filter inside the window this morning. It is a $40.8bn-cap "
        "US name reporting Jun 17 BMO (inside the 5-day-pre window), and it is the clean read on whether the "
        "AI/data-center hardware demand that the tape is paying up for (NVDA's $25B bond, hyperscaler capex) is "
        "translating into orders for the infrastructure builders. Consensus EPS and the recommendation split are "
        "Finnhub-sourced; short-interest/positioning is unavailable and tagged estimated, which caps the conviction "
        "label. Excluded this morning: FedEx (reports Jun 23, outside the window), Lennar (homebuilder, outside the "
        "Tech/Financials/Industrials/Utilities universe), and Adobe (Jun 11 print now outside the 3-day post-window; "
        "carried as a trade idea instead)."
    ),

    "book_aim": (
        "Two-sided and deliberately uncrowded the day before Warsh's first dot plot. The MoU binary has resolved on "
        "the book's terms: the oil longs (MM-002, MM-011) are closed without regret, and the duration longs "
        "(MM-004, MM-013) plus the steepener (MM-009) are the winning side, deepened by Brent at ~$83 — held, not "
        "added, ahead of the Fed. Gold (MM-005) flipped to working on the real-rates engine and is held with the "
        "hawkish-dots reversal flagged. The SPX put spread (MM-008) and a fresh, nearer-dated put structure "
        "(MM-017) own the dot-plot tail that VIX 16.2 is giving away. The long-DAX ratio (MM-010) is the one "
        "position the melt-up hurt — on a short leash at its 0.943 stop. The fresh ideas (MM-017 vol, MM-018 "
        "IG-protection, MM-019 transports/energy RV) are all low-correlation to the dots. For the rest of June: let "
        "the steepener, gold and the RV legs carry P&L, hedge the semis concentration, and open no new directional "
        "macro bets before the dot plot lands at 2pm Wednesday."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the one option line "
                 "(MM-008) is a model estimate from spot.")
    },
    "idea_selection": [
        {"label": "SPX dot-plot tail (MM-017) — own the binary cheaply", "in": True,
         "text": ("VIX at 16.2 makes downside convexity the cheapest of the cycle right before Warsh's debut dots. A "
                  "Jul-2 7200/6900 put spread at ~0.9% of notional owns a ~$300 payoff if the dots send the S&P "
                  "toward 7,000. Defined risk; the fresh, nearer-dated complement to the decayed MM-008.")},
        {"label": "IG-protection convexity (MM-018) — the Burry tell, tradeable", "in": True,
         "text": ("Buy 5y CDX IG protection (or LQD puts) behind the AI debt boom — NVDA's $25B bond is the tell. IG "
                  "at cycle tights (~52bp) does not price the supply wave or the leverage discount. A small, "
                  "carry-aware structural pre-position; a hawkish Warsh is the near-term accelerant. Stop on IG "
                  "through ~45bp.")},
        {"label": "Long transports / short energy (MM-019) — peace-dividend RV", "in": True,
         "text": ("A market-neutral-ish RV: the deeper oil move (~$83) is a margin tailwind to transports and a "
                  "top-line hit to energy. Low beta to the FOMC binary — own the de-escalation theme without a "
                  "directional macro bet the day before the dots. Size on the ratio; stop -3%.")},
        {"label": "Duration longs + steepener (MM-004/013/009) — held, not added", "in": False,
         "text": ("The winning side of the MoU binary, deepened by Brent ~$83. But the FOMC is the gate — do not add "
                  "size before Wednesday 2pm. Respect the stops (4.65% / 4.35% / -10bp).")},
        {"label": "No new directional macro before Wednesday 2pm", "in": False,
         "text": ("Warsh's first dot plot is the regime-defining event for the rest of Q2. Forcing a new macro bet "
                  "in front of it — especially into the most complacent vol of the cycle — is noise, not edge. The "
                  "three fresh ideas are deliberately low-correlation to the binary.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 15.0},
        {"label": "VIX",   "value": 16.2},
        {"label": "VIX3M", "value": 18.5},
        {"label": "VIX6M", "value": 20.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.08, 3)},
        {"label": "5Y",  "value": 4.20},
        {"label": "10Y", "value": round(_g("us10y") or 4.45, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 4.92, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-017", "trade": "Buy SPX Jul-2 7200/6900 put spread (own the dot-plot tail)",
            "asset_class": "Derivatives (options)", "structure": "put spread",
            "entry": "~$30 premium (~0.9% notional)", "stop": "—", "target": "~$300",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Jul 2", "min_hold_days": 0,
            "thesis": ("The melt-up crushed VIX to 16.20 — the most complacent vol of the cycle — and priced Warsh's "
                       "first FOMC at ~98% hold as a non-event, exactly when a new, more hawkish chair's debut dot "
                       "plot is the least-priced binary on the board (2026-hike odds ~47%). Cheap downside convexity "
                       "struck closer to a stretched 7,554 index, expiring just after the meeting; the fresh, "
                       "nearer-dated expression of the FOMC tail now MM-008 has decayed deep OTM."),
        },
        {
            "id": "MM-2026-018", "trade": "Buy 5y CDX IG protection (the AI debt boom)",
            "asset_class": "Credit", "structure": "credit-spread convexity",
            "entry": "IG ~52bp", "stop": "tightens through ~45bp", "target": "IG +15bp",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "structural / weeks-months", "min_hold_days": 0,
            "thesis": ("NVIDIA's $25B high-grade bond (first since 2021, ~3x oversubscribed) joins Oracle's $40B "
                       "raise: the AI capex cycle has become an AI debt boom, and the equity is celebrating leverage "
                       "the credit isn't pricing. IG at cycle tights (~52bp) does not price the supply wave or the "
                       "eventual leverage/dilution discount. Cheap convexity on the most-owned, now most-levered "
                       "theme in the index; a hawkish Warsh is the accelerant. Sized small, carry-aware."),
        },
        {
            "id": "MM-2026-019", "trade": "Long transports (IYT) vs short energy (XLE)",
            "asset_class": "Equity RV", "structure": "cross-sector ratio",
            "entry": "spot ratio", "stop": "ratio -3%", "target": "ratio +5%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The peace dividend reprices two sectors in opposite directions off one input, and the input "
                       "moved again: Brent to ~$83 (two-month low) with the MoU signing Jun 19 and the Strait "
                       "reopening immediately without tolls. Jet fuel is ~25-30% of airline opex and diesel is the "
                       "freight cost line — a margin tailwind to transports, a top-line hit to E&P. "
                       "Market-neutral-ish, low beta to Wednesday's FOMC."),
        },
    ],
    "pre_position_ideas": [],
}

# ── Legacy output.html ─────────────────────────────────────────────────────────
book.step("Rendering output.html")
html_out = book.build_html(brief, trades, regime_log)
with open(book.OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_out)
book.log(f"wrote {len(html_out):,} bytes -> {book.OUTPUT_PATH}")

# ── Client book scan ───────────────────────────────────────────────────────────
book.step("Scanning client book (Fable)")
scan = book_scanner.build_scan(brief)
if scan:
    m = scan["metrics"]
    book.log(f'Fable book EUR{m["total_eur"]:,} · {m["largest"]["ticker"]} {m["largest"]["weight_pct"]}% '
             f'· {scan["counts"]["fired"]} fired / {scan["counts"]["watch"]} watch / {scan["counts"]["suppressed"]} suppressed')

# ── Shark Tank pages ───────────────────────────────────────────────────────────
book.step("Rendering Shark Tank pages + fragments")
shark_format.render_all(brief, trades, regime_log, scan=scan)

# ── Persist state ──────────────────────────────────────────────────────────────
book.step("Saving trades.json + regime_log.json")
book.save_json(book.TRADES_PATH, trades)
book.save_json(book.REGIME_PATH, regime_log)

book.step("Done")
