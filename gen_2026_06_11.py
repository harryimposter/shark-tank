#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-11 (Thursday).

Oracle reported after yesterday's close — capex panic selloff: revenue ~$19.2B
(slight beat), OCI +93%, Cloud +47%, RPO surged to ~$638B. BUT FY26 capex came in
at $55.7B (above ~$50B guide), FY27 guided to ~$70B + $20-25B component prepayments,
funded by ~$40B debt-and-equity raise (~$20B share sale component). Stock -7 to -11%
AH. Market read: capital and capacity problem, not a demand problem.

ECB decision DAY: +25bp to 2.25% WIDELY EXPECTED but has NOT happened yet as of
this run. Decision is TODAY (Jun 11). Framed as imminent/upcoming throughout.

US-Iran Day-2 strikes ongoing; Brent climbing toward $95; SPX put spread in the
money (S&P -1.62% yesterday to ~7,267). Adobe reports after close tonight.
FOMC June 16-17 next week.

Run:  python gen_2026_06_11.py
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
levels["MM-2026-008"] = 80.0   # SPX put spread: 7300/7000 now in the money after S&P -1.62% to ~7,267
levels["MM-2026-011"] = 2.5    # Brent 100/115 call spread: gaining as Brent climbs toward $95

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
    "MU":  "We like it higher: HBM is sold out into the AI-memory supercycle and the name has just washed out into "
           "the 24-Jun print. Oversold here is the dip we would add on, not the breakdown to fade.",
    "MC.PA": "Oversold but we are NOT buyers: luxury end-demand is soft and the house view is NEUTRAL — this is a "
             "level to sell income against (reverse convertible), not to chase.",
    "NVDA": "Constructive lower: the 195-235 consolidation is intact and the de-rate was rates-driven, not "
            "franchise-driven. Oversold into support is where the desk gets paid to add.",
    "AVGO": "Oversold after the whisper-miss, but NEUTRAL — there is no near-term catalyst to re-rate it, so this is "
            "a harvest-and-buffered-re-entry name, not a clean long.",
    "TSM":  "Higher: the Asia semis complex is the supply-chain spine of the AI build-out; an oversold TSMC is a "
            "buy-the-dip in the toll-road, not a trend break.",
    "ORCL": "Post-print CAPEX PANIC: Revenue ~$19.2B (slight beat), OCI +93%, Cloud +47%, RPO surged to ~$638B "
            "(from ~$553B). BUT FY26 capex $55.7B beat the ~$50B guide, FY27 guided ~$70B PLUS $20-25B component "
            "prepayments — total capital commitment ~$90-95B in one year. Funded via ~$40B debt+equity raise "
            "(incl. ~$20B share sale). Stock -7 to -11% AH. Market read: demand confirmed ($638B RPO), "
            "execution and capital structure are the constraint. "
            "Capital-protected note: absorbs the near-term dilution, participates in the OCI re-rate.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = "Oracle Capex Panic: $70B FY27 Guided; ECB Decision Today; Day-Two Strikes"
regime_note = (
    "Oracle reported Q4 FY26 after yesterday's close and it is a capex panic, not a dilution story. Revenue "
    "came in ~$19.2bn (slight beat), OCI grew 93% YoY, Cloud +47%, and — the headline bull number — the RPO "
    "backlog surged to ~$638bn (up from ~$553bn). Every demand metric confirmed the AI thesis. Then the market "
    "read the cost of delivering it: FY26 capex came in at $55.7bn, above the ~$50bn guide. Oracle then guided "
    "FY27 capex to ~$70bn PLUS an additional $20-25bn in component prepayments — a total capital commitment of "
    "~$90-95bn in one fiscal year. To fund it, Oracle announced a ~$40bn debt-and-equity raise (including ~$20bn "
    "in new shares). Stock fell 7-11% after hours. The market is not saying 'the demand is bad' — the $638bn RPO "
    "proves otherwise. The market is saying 'we don't trust the capital structure to fund this without destroying "
    "shareholder value.' That distinction — capital and capacity problem, not a demand problem — is the trade. "
    "A capital-protected note participates in the re-rate if Oracle executes, absorbs the dilution hangover if it "
    "doesn't. The ECB decision is TODAY (Jun 11) — +25bp to 2.25% is the consensus at near-100% probability, "
    "but the decision has NOT been announced as this script runs. Lagarde's press conference tone is the "
    "live EUR catalyst. EUR/USD is ~1.15 pre-decision. Geopolitically, the US-Iran conflict entered a second "
    "day of strikes; Iran fired back targeting Gulf states; ceasefire declared 'practically meaningless'; "
    "Qatari mediators left empty-handed. Brent is climbing toward $93-95. Adobe reports after the close tonight. "
    "FOMC June 16-17 is the final gate."
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
            "(commodity-linked, RBA-managed). The cross is driven by: (1) relative central bank "
            "rate paths (ECB vs RBA); (2) iron ore prices — Australia's largest export, so a strong "
            "ore price = AUD tailwind; (3) global risk sentiment; (4) the 2-year interest-rate "
            "spread between the eurozone and Australia."
        ),
        "fundamental_thesis": (
            "The ECB decision is TODAY (Jun 11) — +25bp to 2.25% is consensus at near-100% probability, "
            "but as yet unannounced. The 'buy the rumour, sell the fact' setup is the trade: EUR was bid "
            "from 1.08 to ~1.15 as the market priced in this hike cycle. Once the hike is delivered, "
            "the marginal buyer disappears, and the rate differential at these levels has already been "
            "extracted. Lagarde's press conference tone ('data-dependent pause' vs 'further hikes') sets "
            "the EUR direction into next week. The AUD carries a terms-of-trade tailwind from firm iron "
            "ore (~$105/t). EURAUD drifting lower from 1.66 is consistent with the thesis."
        ),
        "catalysts": [
            "ECB Jun 11 decision (PENDING — +25bp consensus at ~99%; delivery = sell-the-fact trigger; "
            "Lagarde presser wording on 'further hikes' vs 'data-dependent pause' is the live EUR driver)",
            "Iron ore price action (any Chinese demand headline or PBOC stimulus = AUD tailwind)",
            "RBA June meeting (if hawkish, AUD further supported vs EUR)",
            "FOMC Jun 16-17 (Fed hold = USD strengthens vs EUR, compresses EUR/AUD further)",
        ],
        "risks": (
            "ECB explicitly signals another hike (EUR squeezes above 1.162 on EURAUD cross); iron ore "
            "collapses on China demand shock (AUD loses its tailwind); broader risk-off drives USD "
            "safe-haven bid rather than EUR/AUD move; stop at 1.662."
        ),
        "breakdown_why": {
            "gap":          "3/3 — the cross is ~170 pips above the 2yr spread's implied fair value; "
                            "a full-figure mispricing between a dovish-terminal ECB and an RBA still "
                            "in tightening mode. Sell-the-fact setup intact pre-decision.",
            "catalyst":     "2/2 — ECB Jun 11 decision (TODAY, PENDING) and FOMC Jun 16-17 are both "
                            "near-dated, directly EUR-relevant events. Two dated catalysts in the window.",
            "positioning":  "1/2 — EUR longs into the ECB are crowded (spec long at multi-year highs "
                            "vs AUD), providing squeeze fuel if Lagarde leans data-dependent pause.",
            "confirmation": "1/2 — the cross sold off from the 1.66 handle, giving one technical "
                            "confirmation; needs a clean break lower for a 2.",
            "stop_quality": "1/1 — 1.662 is a clear technical level; tight relative to the target move.",
        },
    },
    "MM-2026-002": {
        "instrument": (
            "Brent crude oil — ICE Brent front-month futures contract (BRN1!). The global oil "
            "benchmark, priced in USD. Driven by: OPEC+ production quotas, Middle East geopolitics "
            "(Strait of Hormuz = chokepoint for ~20% of world oil supply), USD strength, China/global "
            "demand, US shale supply, and tanker/shipping availability."
        ),
        "fundamental_thesis": (
            "The thesis just got re-confirmed: the US launched a second day of Iran strikes and Brent "
            "climbed toward $93.50, approaching $95. Iran fired back at Bahrain, Kuwait and Jordan. "
            "The Strait of Hormuz is at ~15% of pre-war traffic (JPMorgan) and Qatari mediators left "
            "Tehran empty-handed on Thursday — uranium enrichment and frozen assets remain the sticking "
            "points. The SPR is heading toward its lowest level since the early 1980s. Forecasts from "
            "Bloomberg Intelligence: Brent averages $130/bbl in July-August if the Strait stays shut. "
            "This remains the right-tail hedge — asymmetric upside into a scenario that is physically, "
            "not sentimentally, priced."
        ),
        "catalysts": [
            "Strait of Hormuz traffic (currently ~15% pre-war; any mine/tanker incident = $100+ gap)",
            "US-Iran talks timeline (Qatari mediation failed Thu; Turkey urging both sides to return "
            "to negotiations — next diplomatic signal is the catalyst)",
            "OPEC+ emergency meeting (supply cut = price floor lifted)",
            "Weekly US crude inventory data (EIA Wednesdays); SPR drawdown trajectory",
        ],
        "risks": (
            "Genuine ceasefire + Strait reopening (premium collapses toward $84 support); demand "
            "destruction from global recession fears; SPR release program accelerates; stop at weekly "
            "close below $87."
        ),
        "breakdown_why": {
            "gap":          "3/3 — Hormuz at 15% pre-war traffic, Brent below forecasted $130 July avg; "
                            "the physical constraint is more severe than the price currently implies. "
                            "Upgraded to 3 after day-two US strikes re-confirmed the tail.",
            "catalyst":     "2/2 — second day of US strikes is the confirmation; Qatari talks failed; "
                            "Turkey urging restraint = negotiations still live but fragile. Direct, "
                            "datable catalysts on the horizon.",
            "positioning":  "1/2 — specs cut net length but are not cleanly short; modest support.",
            "confirmation": "1/2 — Brent breaking above $93 on day-two strikes gives one technical "
                            "confirmation; not yet a clean re-acceleration above $95.",
            "stop_quality": "1/1 — weekly close below $87 is a clean structural level with clear "
                            "fundamental interpretation (war premium gone).",
        },
    },
    "MM-2026-003": {
        "instrument": (
            "Brent-WTI crude oil price spread. Long Brent (ICE, North Sea / Atlantic basin benchmark) "
            "vs short WTI (NYMEX, Cushing Oklahoma, US benchmark). The spread is driven by: "
            "Hormuz/Middle East risk premium (Brent-specific), US shale pipeline capacity to Cushing, "
            "Atlantic-basin tanker availability, and regional refining margins. When Middle East "
            "supply risk rises, Brent reprices more than WTI because Brent is the waterway-exposed "
            "benchmark; WTI prices the US pipeline system."
        ),
        "fundamental_thesis": (
            "The Hormuz premium is Brent-specific — it prices the waterway risk, not Cushing storage. "
            "If the MoU frays, the Atlantic-basin grade reprices the de-mining risk and the spread "
            "widens; if it holds, physical carry caps the downside near current levels. A cleaner, "
            "lower-beta way to own the same re-escalation tail with defined spread risk."
        ),
        "catalysts": [
            "Strait of Hormuz escalation or confirmed closure (widens spread sharply)",
            "US crude inventory build at Cushing (narrows spread)",
            "OPEC+ differential cuts targeting Brent vs WTI grades",
        ],
        "risks": (
            "Hormuz reopens (both legs fall, but spread narrows as Brent-specific premium collapses); "
            "US pipeline capacity constraint eases (WTI catches up); stronger US shale production "
            "narrows the spread organically; stop $1.50."
        ),
        "breakdown_why": {
            "gap":          "2/3 — Brent-WTI spread is structurally elevated on a closed Hormuz; "
                            "but not as extreme a mispricing as the outright Brent long.",
            "catalyst":     "1/2 — the same geopolitical catalysts as MM-002 apply but the spread "
                            "mechanism is less direct; requires a Brent-specific supply shock.",
            "positioning":  "1/2 — spread positioning is not as extreme as outright oil; modest "
                            "supportive lean.",
            "confirmation": "0/2 — spread traded below entry before recovering; no clear "
                            "technical confirmation signal yet.",
            "stop_quality": "1/1 — $1.50 is a well-defined floor that matches the structural "
                            "carry; $1.80 of risk vs $3.20 reward.",
        },
    },
    "MM-2026-004": {
        "instrument": (
            "US 10-year Treasury yield. Shorting the yield = buying duration (long bonds, "
            "equivalent to long TLT or 10Y Treasury futures). Driven by: Fed policy path "
            "(front-end anchored), inflation expectations, fiscal deficit/Treasury supply, "
            "global risk sentiment (Treasuries = safe haven), and real growth outlook."
        ),
        "fundamental_thesis": (
            "May CPI printed yesterday: headline 4.2% (all energy), core +0.2% m/m / 2.9% — BELOW "
            "consensus. The soft core is the signal: the Fed is not forced to hike on energy-driven "
            "inflation it routinely looks through. The 10Y eased to ~4.52% on the print. The trade "
            "is now in its payoff window: soft core = front-end eases, FOMC Jun 16-17 is the "
            "confirmation catalyst. Warsh cannot look dovish in week one — but a zero-cut dot at "
            "3.75% already IS the hold, not a hike. The disinflation thesis holds."
        ),
        "catalysts": [
            "May CPI Jun 10 DONE: 4.2% headline / 2.9% core (below 0.3% forecast) — soft core "
            "gave the front-end relief the trade needed; 10Y eased to ~4.52%",
            "FOMC dot plot Jun 16-17 — zero-cut median = yield up, test stop; one-cut held = yield "
            "falls 15-20bp; Warsh's first presser tone is the edge",
            "Treasury supply (June/July refunding — supply shock risk at the long end)",
            "Any core re-acceleration in June CPI (Jul 10) = bear case",
        ],
        "risks": (
            "Warsh proves hawkish at first FOMC (dot plot = zero cuts, hike bias); energy dragging "
            "core up next month; fiscal supply shock pushes term premium; geopolitical re-escalation "
            "re-inflates commodity prices and spills into core. Stop at 4.65% (now ~4.52%, ~13bp away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the disinflation impulse from oil is real but the market has "
                            "not priced it; not a 3 because the front-end is already pricing some "
                            "easing and the supply risk is a genuine offset.",
            "catalyst":     "1/2 — CPI and FOMC are the catalysts but both are binary (the trade "
                            "can go either way on each); no soft catalyst between now and then.",
            "positioning":  "1/2 — consensus is still long duration (was already rallied 26bp); "
                            "not a cleanly crowded short to squeeze.",
            "confirmation": "0/2 — the yield has NOT confirmed the move lower yet; still offside "
                            "at 4.53% vs 4.44% entry; no technical confirmation.",
            "stop_quality": "1/1 — 4.65% is a clear technical level (prior high); ~12bp risk.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold priced in US dollars. A safe-haven/real-asset that is "
            "the inverse of real interest rates (nominal rates minus inflation expectations). "
            "Driven by: Fed policy path and real yields, USD strength, central bank purchases "
            "(EM central banks are structurally large buyers), geopolitical risk premiums, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "Gold is now working on two separate engines simultaneously. First, the safe-haven "
            "engine: US-Iran day-two strikes and Iran hitting Gulf states sent the geopolitical bid "
            "back in — gold at $4,104+ and rising 0.80% while equities struggle. Second, the "
            "real-rates engine: May CPI core at 2.9% (below consensus) eased the 10Y to ~4.52%, "
            "reducing the real-rate pressure that had been capping gold. Both the bull scenarios are "
            "now firing at once. The narrow path where gold loses (strong growth + stable oil + "
            "aggressive Fed) is precisely NOT the current environment."
        ),
        "catalysts": [
            "US-Iran Day 2 strikes (Jun 11) — safe-haven bid active NOW; Brent toward $95 = "
            "inflation + risk premium both supporting gold",
            "FOMC dot plot Jun 16-17 — zero-cut median caps gold; one-cut held = gold +2%",
            "May CPI core DONE (2.9%, below est.) — real-rate pressure eased to ~4.52% 10Y",
            "EM central bank Q2 gold purchase data (China, India, Turkey structural buyers)",
        ],
        "risks": (
            "Warsh surprises hawkishly at FOMC (real yields surge, gold sells); rapid Strait "
            "reopening + genuine ceasefire removes the geopolitical bid; gold-specific spec flush; "
            "strong USD spike on FOMC or escalation-safe-haven dollar bid. "
            "NOTE: Stop touched Jun 10 ($4,200 vs $4,250 stop) but min_hold 45d rule applies — "
            "position stays open; gold has since recovered to $4,104 and rising."
        ),
        "breakdown_why": {
            "gap":          "2/3 — gold's decoupling from the long bond at 4.98% is a clear "
                            "mispricing signal — real rates should be bearish at that level. "
                            "Not a 3 because the premium was already partially re-inserted.",
            "catalyst":     "2/2 — FOMC dot plot and CPI are both dated, near-term events with "
                            "direct gold transmission; clear catalyst window.",
            "positioning":  "1/2 — gold positioning is not extreme; not a cleanly crowded long "
                            "that would hurt on an unwind.",
            "confirmation": "0/2 — no fresh technical confirmation; price is below entry "
                            "($4,200 vs $4,523 entry).",
            "stop_quality": "1/1 — $4,250 is a well-defined structural level; min_hold "
                            "constraint is the discipline mechanism.",
        },
    },
    "MM-2026-007": {
        "instrument": (
            "USD/JPY spot FX (dollar-yen). One of the world's most-traded FX pairs. "
            "Driven by: US-Japan 2-year interest rate differential (primary driver), BoJ policy "
            "normalisation, Fed policy, risk sentiment (JPY is a global safe-haven during vol "
            "spikes — yen strengthens in crises), and Japanese Ministry of Finance intervention "
            "threat above ~160-162."
        ),
        "fundamental_thesis": (
            "USDJPY at 159.37 with Finance Minister Katayama explicitly threatening intervention. "
            "BoJ September hike >50% priced vs Fed on hold — narrowing the rate differential that "
            "has kept yen weak. 3.63 pts of downside to stop vs 9.37 pts to target at 150. "
            "Intervention is the backstop: the MoF will not let this test 162 twice."
        ),
        "catalysts": [
            "BoJ meetings (September hike increasingly priced; any hawkish language = yen rally)",
            "MoF intervention (explicit warning above 162-163; physical intervention forces stop-hunting)",
            "FOMC Jun 16-17 (Fed on hold narrows US-Japan differential further)",
            "Japan CPI data (any upside surprise supports BoJ normalisation)",
        ],
        "risks": (
            "Fed turns more hawkish (widens differential again); BoJ delays hike or sounds dovish "
            "(Ueda has a history of surprising dovishly); carry-unwind fails to materialise; "
            "risk-off event where USD is the safe haven (rare but possible); stop at 163.00."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USDJPY is ~1500 pips above where the 2yr US-Japan "
                            "differential has historically implied; clear structural gap.",
            "catalyst":     "2/2 — BoJ hike probability and MoF intervention threat are both "
                            "dated and credible; binary catalyst window is defined.",
            "positioning":  "1/2 — the yen carry trade is very crowded (speculators are long "
                            "USD/short JPY), providing squeeze fuel; not a 2 because unwinding "
                            "requires a catalyst to force it.",
            "confirmation": "1/2 — price rejected from 160+ handle once already; one "
                            "technical confirmation of the ceiling.",
            "stop_quality": "1/1 — 163.00 is a clear MoF intervention zone ceiling; "
                            "3.63 pts risk vs 9.37 to target.",
        },
    },
    "MM-2026-008": {
        "instrument": (
            "SPX Jun-27 7300/7000 put spread — a defined-risk options position. Buy the $7300 "
            "put (right to sell SPX at 7300), sell the $7000 put (capping downside protection at "
            "7000). Expires Jun 27. Structure: maximum profit $300/unit if SPX ≤7000 at expiry; "
            "maximum loss = $35 premium paid; break-even ~$7265. Driven by: SPX price level "
            "(currently ~7386), implied volatility (VIX ~19), and time to expiry."
        ),
        "fundamental_thesis": (
            "VIX at 15.3 when purchased — cheap for 4 binary events in 15 days. The hedge is now "
            "IN THE MONEY: SPX fell -1.62% yesterday to ~7,267, below the 7300 strike. The 7300/7000 "
            "put spread now has intrinsic value and the mark is estimated at ~$80 (from $35 premium "
            "paid — +$45 gain, +129%). Two events remain: FOMC Jun 16-17 and Adobe's print tonight. "
            "The hedge paid for itself before half the catalysts even landed. The question is whether "
            "to lock in gains or carry it through FOMC."
        ),
        "catalysts": [
            "May CPI Jun 10 DONE: hot headline (4.2%) sold equities; S&P -1.62% yesterday to ~7,267 "
            "— put spread is NOW IN THE MONEY (7300 strike breached)",
            "Oracle Jun 10 AMC DONE: beat fundamentals, -10%+ on $20B dilution; AI cohort de-rated",
            "ECB Jun 11 DONE: +25bp as expected; limited additional catalyst today",
            "FOMC dot plot Jun 16-17 — zero-cut median = more equity selling; hedge's final catalyst",
            "Adobe Jun 11 AMC tonight — software de-rating risk if guidance disappoints",
        ],
        "risks": (
            "SPX rebounds sharply on a peace deal or Warsh dovish surprise (spread moves out of "
            "money, gains erode); time decay — 16 days to Jun 27 expiry; VIX crush if risk-on "
            "returns. Max loss remains the $35 premium paid — defined risk structure."
        ),
        "breakdown_why": {
            "gap":          "3/3 — vol was cheap vs 4 binary events; now proven correct: VIX "
                            "spiked, S&P -1.62%, spread in the money. Gap confirmed.",
            "catalyst":     "2/2 — CPI and ORCL both triggered; FOMC and ADBE remain live. "
                            "Full catalogue of catalysts materialising on schedule.",
            "positioning":  "2/2 — market was complacent (VIX 15.3); unwind is now underway "
                            "— max fuel confirmed. Score maintained.",
            "confirmation": "2/2 — SPX broke below 7300; the hedge is working technically and "
                            "fundamentally. Full confirmation.",
            "stop_quality": "1/1 — defined-risk structure; max loss was $35; gain is ~$45. "
                            "The defined-risk format means the stop is conceptual.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury yield curve steepener — long the 2-year yield (equivalent to "
            "long 2Y notes / receiving fixed on a 2Y swap), short the 10-year yield (short "
            "10Y notes / paying fixed on a 10Y swap). The position makes money when the gap "
            "between 10Y and 2Y yields widens (curve steepens). Currently: 2Y ~4.13%, 10Y ~4.53%, "
            "spread ~+40bp. Driven by: Fed policy expectations (dominate the 2Y), fiscal "
            "supply/term premium/growth (dominate the 10Y)."
        ),
        "fundamental_thesis": (
            "2s10s at +15bp at entry (Jun 1) after an 18-month inversion. Buy 2Y (owns cut "
            "optionality — front-end falls if Fed cuts or pauses), short 10Y (short fiscal "
            "supply risk — back-end sells off if deficits persist). June 5 payrolls at 89k + "
            "Fed pause reprices front-end. ECB hiking cycle lifts global long rates. "
            "The steepener is paid whether the Fed cuts (2Y rallies) or the back-end sells "
            "off (supply), and the late-cycle pattern after a prolonged inversion historically "
            "supports further steepening."
        ),
        "catalysts": [
            "May CPI Jun 10 (soft print = 2Y rallies most, steepener accelerates)",
            "FOMC dot plot Jun 16-17 (any pause signal = 2Y falls faster than 10Y = steepens)",
            "ECB hiking cycle (lifts global long rates, pressuring US 10Y up from the long end)",
            "Treasury supply (back-end auctions sell-off = steepen)",
        ],
        "risks": (
            "Curve flattens/re-inverts if hot CPI forces aggressive front-end repricing "
            "(2Y up more than 10Y); global rates fall together (safe-haven bid from geopolitics "
            "flattens curve); Fed surprises with a hike (front-end blows out, curve inverts); "
            "stop: spread below -10bp."
        ),
        "breakdown_why": {
            "gap":          "2/3 — curve at +15bp post 18-month inversion was structurally "
                            "underpriced vs the historical late-cycle mean; not a 3 because the "
                            "near-term path is CPI-dependent.",
            "catalyst":     "2/2 — CPI and FOMC dots are both direct and dated catalysts "
                            "for the front-end repricing this trade needs.",
            "positioning":  "1/2 — positioning in 2Y was short (market priced hikes), "
                            "providing some squeeze fuel.",
            "confirmation": "1/2 — payrolls (Jun 5) already showed 89k — one "
                            "confirming data point for the 'soft landing = no hike' thesis.",
            "stop_quality": "1/1 — negative spread is a well-defined structural failure "
                            "threshold; clear stop.",
        },
    },
    "MM-2026-010": {
        "instrument": (
            "Long DAX / short Nasdaq Composite price ratio. Buy German equities (DAX = 40 "
            "large-cap German companies, heavily financial and industrial), sell US tech "
            "(Nasdaq Composite). A cross-region equity relative-value trade. The DAX/Nasdaq "
            "ratio rises when DAX outperforms: driven by ECB vs Fed policy divergence, "
            "EUR/USD (EUR strength hurts DAX exporters but helps the ratio vs USD-denominated "
            "Nasdaq), European banks outperforming US tech, and AI multiple compression."
        ),
        "fundamental_thesis": (
            "The two legs of the trade are both working. ECB decision is TODAY (Jun 11, PENDING) "
            "— if +25bp as expected, the DAX's financial sector gets a direct NIM tailwind. "
            "Nasdaq fell -1.98% yesterday on Oracle's capex panic and CPI-driven tech selling. "
            "The DAX/Nasdaq ratio should have recovered from the 0.949 near-stop. Oracle's "
            "$70B FY27 capex guide confirmed the AI-capex bill thesis (Nasdaq de-rate on cost, "
            "not demand). The structural divergence — European financials vs US tech, ECB on "
            "the way to 2.25% vs Fed holding at 3.75% — is the durable driver."
        ),
        "catalysts": [
            "ECB Jun 11 decision (PENDING — +25bp consensus; if confirmed, DAX financials "
            "benefit from higher NIM; ratio should recover from 0.949 near-stop)",
            "Oracle Jun 10 AMC DONE: capex panic (-7 to -11%) = Nasdaq cohort de-rated; "
            "Nasdaq -1.98% yesterday confirms the AI-cost leg-down catalyst",
            "FOMC Jun 16-17 — Fed hold (96-98% probability) = USD bids; dovish dot = Nasdaq "
            "bid = ratio pressure",
            "Adobe tonight — software de-rating risk on guidance = another Nasdaq leg down",
        ],
        "risks": (
            "Nasdaq rebounds sharply if ADBE prints positive AI guidance tonight or FOMC "
            "surprises dovish (ratio falls back to stop at 0.943); EUR strength on hawkish "
            "Lagarde tone hurts DAX exporters; German recession fears resurface."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the 4.2% single-day DAX/Nasdaq divergence on a US-specific "
                            "factor was a clear structural gap; Europe has no AI multiple to "
                            "de-rate.",
            "catalyst":     "1/2 — ECB is the near-term catalyst but it's already priced; the "
                            "cleaner catalyst is AI-cohort disappointment (Oracle), which is "
                            "softer/event-dependent.",
            "positioning":  "2/2 — the AI/US-tech trade is very crowded; spec positioning is "
                            "long US tech heavy; any unwind = max fuel for DAX/Nasdaq ratio.",
            "confirmation": "1/2 — one-session decoupling (Jun 6) confirmed the thesis; "
                            "not yet sustained enough for a 2.",
            "stop_quality": "1/1 — ratio stop at 0.943 is a clean technical level; "
                            "~30bp of risk vs ~60bp to target.",
        },
    },
    "MM-2026-011": {
        "instrument": (
            "Brent crude $100/$115 call spread — buy the $100 call on Brent, sell the $115 call "
            "(capping upside at $115). A defined-risk bullish options position. Current mark: ~$2.0 "
            "(down from $3.0 entry as Brent eased from $96 to ~$91). Maximum profit: $15/barrel if "
            "Brent ≥$115 at expiry (1 month). Maximum loss: $3 premium paid. This is Brent's own "
            "'tail option' — cheap insurance on the Hormuz escalation scenario."
        ),
        "fundamental_thesis": (
            "Brent is now at $93.50 and climbing toward $95 — the call spread's $100 strike is "
            "$6.50 away. Day-two US strikes on Iran and Iran firing at Gulf states directly "
            "reprices the Hormuz tail. Hormuz traffic at ~15% pre-war levels (JPMorgan). "
            "Bloomberg forecasts $130/bbl average in July-August. The premium has NOT been "
            "fully priced out. Defined-risk: max loss still the $3 premium paid; mark now ~$2.5."
        ),
        "catalysts": [
            "US-Iran day-two strikes (Jun 11) — Brent at $93.50 approaching $100 strike; "
            "further escalation gap to $100+ is the call-spread trigger",
            "Confirmed mine/tanker incident in the Strait (immediate $110+ gap)",
            "Strait traffic data — any reduction below current 15% = supply shock",
            "Brent weekly close above $95 (momentum confirmation; $100 strike then in sight)",
        ],
        "risks": (
            "Ceasefire holds and Brent falls well below $100 (premium decays; current mark ~$2, "
            "stop $1.0); time decay over the 1-month tenor; Brent supply rises faster than "
            "demand; geopolitical premium fully deflates."
        ),
        "breakdown_why": {
            "gap":          "2/3 — at entry, the Hormuz tail was priced only partially in Brent "
                            "spot; the call spread captured event-specific asymmetry cheaply.",
            "catalyst":     "2/2 — explicit geopolitical catalysts (mine, strike, escalation) "
                            "directly detectable and dated within the 1-month tenor.",
            "positioning":  "1/2 — oil call skew was elevated but not extreme at entry; "
                            "not the most stretched positioning.",
            "confirmation": "1/2 — Brent gapping +3% at entry gave momentum confirmation.",
            "stop_quality": "1/1 — defined-risk structure (max loss = $3 premium); stop at "
                            "$1.0 (down 67%) is a discipline rule, not a true stop.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot FX — short euro, long dollar. One of the world's most liquid FX pairs. "
            "Driven by: ECB vs Fed policy differential, eurozone vs US growth, risk sentiment "
            "(USD is the global safe-haven), oil price (EUR has mild inverse correlation to oil "
            "via energy import costs), and speculative positioning."
        ),
        "fundamental_thesis": (
            "The ECB decision is TODAY (Jun 11, PENDING). The market has priced +25bp to 2.25% "
            "at near-100% probability — EUR ran from 1.08 to ~1.15 as this hike cycle was priced "
            "in. Once the hike is delivered, the 'buy the rumour' crowd is done and the marginal "
            "EUR buyer disappears. EUR/USD at ~1.15 pre-decision is the 'fully priced' level. "
            "The 'sell the fact' unwind begins on delivery. Lagarde's presser — 'data-dependent "
            "pause' language (base case given inflation is energy-led) = EUR fades; 'further "
            "hikes' = EUR spike and respect the 1.182 stop. FOMC Jun 16-17 is the next catalyst."
        ),
        "catalysts": [
            "ECB Jun 11 decision (PENDING — +25bp consensus; delivery = sell-the-fact trigger; "
            "Lagarde presser: 'data-dependent pause' = EUR toward 1.140; 'further hikes' = stop test)",
            "FOMC Jun 16-17 — Fed holds at 3.75% (96-98% probability); USD bids on the 'Fed "
            "still careful' narrative vs ECB that just hiked = spread widens for EUR/USD",
            "Spec positioning unwind (EUR longs near multi-year highs = crowded unwind fuel)",
        ],
        "risks": (
            "ECB surprise hawkishness (explicit 'further hikes' tone lifts EUR above 1.182 stop); "
            "US data disappoints and EUR/USD re-rates higher; safe-haven EUR bid in extreme "
            "risk-off; stop at 1.182."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the mispricing is real but contained (the ECB hike is fully "
                            "priced; the gap is the reaction to the press conference wording, not "
                            "a regime-level mispricing); hence 1 not 2.",
            "catalyst":     "2/2 — ECB Jun 11 decision (PENDING TODAY) is a precise, dated "
                            "catalyst with a well-defined payoff trigger (specific presser tone).",
            "positioning":  "1/2 — EUR spec longs at multi-year highs provide unwind fuel; "
                            "not a 2 because the crowding was anticipated (already partially "
                            "faded before entry).",
            "confirmation": "1/2 — EUR/USD started selling off from 1.165 before entry; "
                            "one confirming move.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; 2.2 pips of risk vs "
                            "3.0 pips to target.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receiving fixed on a 2-year interest rate swap, or "
            "equivalently long 2Y Treasury notes). The 2-year yield is the market's best real-time "
            "forecast of the Fed funds rate over the next 2 years. Driven almost entirely by: "
            "near-term Fed expectations, inflation data, employment data, and FOMC communications. "
            "The 2Y is the most policy-sensitive point on the yield curve."
        ),
        "fundamental_thesis": (
            "The market prices ~70% probability of a year-end rate hike based on one 172k payroll "
            "with unemployment steady at 4.3%. The Fed does not hike into a labor market that is "
            "firm-but-not-overheating with a richly-valued equity tape just beginning to crack. "
            "The 2-year at 4.16% — a 16-month high — has over-extrapolated a single data point. "
            "The June 17 dot plot is the catalyst to reprice it. Pre-position, not an event scalp."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 (any pause signal = 2Y falls 15-20bp immediately)",
            "May CPI Jun 10 (below 3.7% = 2Y falls 10-15bp today)",
            "Initial jobless claims (any spike = Fed hiking case weakens)",
            "Warsh's first press conference language on rate path",
        ],
        "risks": (
            "Hot CPI re-arms the hike pricing (2Y to 4.35% stop); Warsh proves hawkish in first "
            "FOMC; additional strong employment data; inflation re-accelerates on oil; stop at "
            "4.35%; min_hold 30 days to Jun 16 FOMC at minimum."
        ),
        "breakdown_why": {
            "gap":          "2/3 — 2Y at 4.16% (16-month high) on one payroll print with "
                            "unemployment at 4.3% is a clear over-extrapolation gap vs "
                            "the actual hiking probability.",
            "catalyst":     "2/2 — FOMC dot plot is a precise, dated catalyst with direct "
                            "2Y transmission; CPI is a secondary near-term gate.",
            "positioning":  "2/2 — the market is very heavily short 2Y duration (positioned "
                            "for a hike); any unwind is a large, fast move = maximum squeeze "
                            "fuel.",
            "confirmation": "0/2 — no technical confirmation yet; the yield has not broken "
                            "lower to confirm the trade.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; 19bp of risk.",
        },
    },
    "MM-2026-006": {
        "instrument": (
            "Broadcom Inc. (AVGO) — US-listed semiconductor and infrastructure software company. "
            "Key business: custom AI ASICs (application-specific integrated circuits) for "
            "hyperscalers (Google TPU, Meta MTIA, Apple Neural Engine), plus networking chips and "
            "the VMware software acquisition. Revenue driven by AI capital spending from the "
            "three hyperscaler ASIC customers + the VMware enterprise software subscription base."
        ),
        "fundamental_thesis": (
            "Q2 earnings Jun 3. AI revenue guide +140% YoY ($0.7B). Six consecutive AI revenue "
            "beats. Computex 2026 tailwind. Beat-and-raise at 41x earnings moves stock 10-15%; "
            "in-line exits same day. The hyperscaler AI capex cycle was still accelerating at "
            "entry."
        ),
        "catalysts": [
            "AVGO Q2 FY26 earnings June 3 (AMC)",
            "AI revenue segment guidance (whisper: $17.2B for FY guidance)",
            "VMware integration update",
        ],
        "risks": (
            "STOPPED June 8. Q2 beat the printed estimate but Q3 AI guide $16.0B missed the buy-side "
            "whisper of $17.2B — the number that mattered at 41x earnings. Payrolls (Jun 5, +172k "
            "with no cuts priced) finished the selloff. Held 7 days. P&L: -13.6%. "
            "The lesson: at a rich multiple, clearing the printed estimate is not enough; "
            "the market is hedged for a miss, not a growth-rate disappointment."
        ),
        "breakdown_why": {
            "gap":          "2/3 — AI revenue trajectory was clearly under-priced by the "
                            "consensus EPS number vs the whisper; real gap existed.",
            "catalyst":     "2/2 — earnings date was precise, well-defined, and imminent.",
            "positioning":  "1/2 — the stock was up pre-print but not at euphoric levels; "
                            "some headroom.",
            "confirmation": "2/2 — six consecutive AI revenue beats provided maximum "
                            "confirmation signal.",
            "stop_quality": "1/1 — $228 stop ($22 below $250 entry) was tight; $35 target "
                            "vs $22 risk.",
        },
    },
}

# ── Regime / dashboard (same as gen_2026_06_09) ────────────────────────────────
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
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},   # unchanged; ECB decision pending Jun 11
    {"name": "MOVE", "level": "~108 (est)", "chg": "", "dir": "flat"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Thu 11 Jun · TradingView"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~108", "chg": "easing (est)", "dir": "down"},
]

NOTES = {
    "MM-2026-001": "ECB decision PENDING today (Jun 11) — +25bp to 2.25% is consensus at ~99%. EUR/USD ~1.15 pre-decision. Sell-the-fact thesis: once delivered, EUR longs unwind. Lagarde's presser is the live catalyst post-decision. Stop 1.662.",
    "MM-2026-002": "Working hard — and validated a second time. US launched Day 2 of Iran strikes; Iran fired at Gulf states; ceasefire declared 'meaningless.' Brent at $93.50 and climbing toward $95. Conviction 3 upgraded on re-escalation confirmation. Exit on weekly close below $87. Target $104.",
    "MM-2026-003": "Building momentum. Brent-WTI spread benefits directly from Day 2 strikes — Brent-specific war premium is widening again. The spread's purpose is confirmed. Stop 1.50.",
    "MM-2026-004": "Working — soft CPI core eased the 10Y to ~4.52% from yesterday's 4.55% high. Disinflation impulse confirmed. FOMC dot plot Jun 16-17 is the next catalyst. Do not add; let the steepener carry it. Stop 4.65%.",
    "MM-2026-005": "Recovering well. Gold at $4,104 (+0.80% today) getting a dual bid: safe-haven from Day 2 US-Iran strikes AND real-rate relief from the soft CPI core. Two-engine rally. Min hold to ~July 15; stop $4,250.",
    "MM-2026-007": "Near flat. USDJPY holding ~160.2 — the USD did not strengthen materially on the ceasefire-is-dead news. BoJ September hike still >50% priced; MoF intervention threat above 163 remains the ceiling. Stop 163.00.",
    "MM-2026-008": "BEST PERFORMER: put spread is now IN THE MONEY. S&P fell -1.62% yesterday to ~7,267, below the 7300 strike. Mark ~80 vs $35 premium paid (+$45, +129%). Two catalysts remain (ADBE tonight, FOMC next week). Hold through expiry Jun 27; do not lift early.",
    "MM-2026-009": "Best structural position, still running strong. 2s10s curve steepened further on the soft CPI core; 10Y eased while front-end stays anchored. Min hold to July 16; target +60bp. FOMC next week is the next catalyst. Hold.",
    "MM-2026-010": "Oracle capex panic confirmed the Nasdaq de-rate leg — stock -7-11% AH, Nasdaq -1.98% yesterday. ECB decision PENDING today (Jun 11, +25bp consensus) — if confirmed, DAX financials get NIM tailwind. Ratio should recover from 0.949 near-stop. Structural case intact — do not trim ahead of FOMC next week.",
    "MM-2026-011": "Gaining. Brent at $93.50 and approaching $95 — the $100 strike is only $6.50 away. Mark ~$2.50 (model est) vs $3 premium. Day-2 strikes bring the $100 trigger into range. Defined risk; hold through the Strait crisis.",
    "MM-2026-012": "ECB decision PENDING today. EUR/USD ~1.15 pre-decision — buy-the-rumour crowd fully positioned. Delivery of the +25bp (PENDING) triggers the sell-the-fact unwind. Lagarde's presser tone is the pace-setter post-decision. Stop 1.182; target 1.130.",
    "MM-2026-013": "Progressing. 2Y holding near ~4.15%; soft CPI core from yesterday validated the 'over-extrapolated hike' thesis. FOMC Jun 16-17 dot plot is the payoff catalyst. Min hold 30d through Jun 16. Stop 4.35%.",
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
    {"datum": "May payrolls +172k",  "source": "BLS June 5",                          "asof": "2026-06-05", "stale": False},
    {"datum": "ORCL Q4 FY26 actuals: EPS $2.11, rev $19.2B, OCI +93%",
     "source": "Oracle IR / web search (Jun 10 AMC)",                                  "asof": "2026-06-10", "stale": False},
    {"datum": "ADBE Q2 FY26 — reporting tonight after close",
     "source": "Finnhub / BusinessWire (Jun 11 AMC)",                                  "asof": "2026-06-11", "stale": True},
    {"datum": "SAIL Q1 FY27: EPS $0.05 beat, rev $280M +22% YoY; -11% pre-market on slight rev miss",
     "source": "GrufuFocus / MarketBeat (Jun 9 BMO)",                                  "asof": "2026-06-09", "stale": False},
    {"datum": "SOFR ~3.62% / MOVE",  "source": "NY Fed (rail) / MOVE unverified",     "asof": "2026-06-10", "stale": True},
    {"datum": "ECB deposit rate: +25bp to 2.25% PENDING (decision TODAY Jun 11, consensus ~99%)",
     "source": "Market pricing / web search (decision not yet announced)",               "asof": "2026-06-11", "stale": False},
]

earnings_ideas = [
    {
        "ticker": "ADBE", "company": "Adobe Inc",
        "report_date": "2026-06-11", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 5, "conviction_label": "Medium conviction — REPORTS TONIGHT",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 1, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Reports TONIGHT after close. Analysts expect non-GAAP EPS $5.01, revenue $6.43-6.48B; "
            "market implies +/-9.47% move. Stock -10.86% since last earnings near 52-week lows.",
            "Split sell-side: 19 buy / 22 hold / 4 sell. The asymmetry is upside — beaten-down into the print.",
            "Key question: is Firefly AI additive to ARR (upsell) or cannibalising Creative Cloud seats? "
            "Guidance tone, not headline EPS, moves this.",
        ],
        "what_moves_it": ("Evidence that AI monetisation is net-new ARR, not subscription cannibalisation. "
                          "A positive AI guide re-rates the whole beaten-down software cohort."),
        "client_talking_point": ("Adobe reports tonight — the cleanest test of AI as tax or tailwind. Near "
                                 "52-week lows, so the downside may be priced; asymmetry is in the upside guide. "
                                 "We enter the CSP (idea 102) post-print. Do not pre-position."),
    },
    {
        "ticker": "ORCL", "company": "Oracle Corp",
        "report_date": "2026-06-10", "report_timing": "AMC",
        "mode": "POST-EARNINGS", "direction": "Neutral",
        "conviction_score": 6, "conviction_label": "High conviction post-print — capital-protected note NOW",
        "conviction_rationale": (
            "Beat every fundamental metric: OCI +93% to $4.9bn, revenue +21% to $19.2bn, "
            "EPS $2.11 vs $1.97 est, RPO surged to $638bn (from $553bn). BUT: -7 to -11% AH on "
            "capex shock — FY26 capex $55.7bn (above ~$50bn guide), FY27 guided ~$70bn PLUS "
            "$20-25bn component prepayments, funded by ~$40bn debt+equity raise (~$20bn share sale). "
            "Market read: capital and capacity problem, not a demand problem. "
            "Capital-protected note (idea 101) holds the OCI conviction while absorbing dilution. Enter today."
        ),
        "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "sourced"},
        "key_bullets": [
            "BEAT: OCI +93% YoY to $4.9bn; Q4 total revenue +21% to $19.2bn; EPS $2.11 vs $1.97 est; "
            "RPO surged to $638bn (from $553bn last quarter) — demand confirmed.",
            "CAPEX PANIC: FY26 capex $55.7bn (above ~$50bn guide); FY27 guided ~$70bn PLUS $20-25bn "
            "component prepayments — total ~$90-95bn annual commitment. Funded by ~$40bn debt+equity "
            "raise (~$20bn share sale). Stock -7 to -11% AH. Capital structure, not fundamentals.",
            "STRUCTURE: Capital-protected note (idea 101) — 70-80% upside participation, full downside "
            "protection. Enter the post-print window today. $638bn RPO is the floor thesis.",
        ],
        "what_moves_it": ("OCI revenue recognition pace vs capital deployment costs of the ~$90-95bn annual "
                          "capex commitment and $40bn raise. Bull: $638bn RPO converts faster than capex burns; "
                          "bear: dilution and balance-sheet leverage cap near-term price recovery."),
        "client_talking_point": ("Oracle proved the fundamentals — OCI +93%, $638bn RPO, record revenues. "
                                 "The stock fell on a capital structure shock ($70bn+ FY27 capex / $40bn raise), "
                                 "not on demand. That is precisely what a capital-protected note is built for: "
                                 "participate in the OCI re-rate, fully protected against the dilution overhang. "
                                 "Post-print window is open — enter the note today."),
    },
    {
        "ticker": "SAIL", "company": "SailPoint Inc",
        "report_date": "2026-06-09", "report_timing": "BMO",
        "mode": "POST-EARNINGS", "direction": "Neutral",
        "conviction_score": 3, "conviction_label": "Read only — not a position",
        "conviction_rationale": (
            "SailPoint BEAT EPS ($0.05 vs $0.04 est) but revenue slightly missed estimates; "
            "stock -11% pre-market on the reaction. ARR +26% YoY to $1.16B; SaaS ARR +36%. "
            "Raised FY27 guidance. The -11% on a beat is a crowded-positioning tell: the market "
            "was positioned for a much larger ARR acceleration. Identity security demand is firm "
            "but the multiple was pricing perfection."
        ),
        "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "sourced"},
        "key_bullets": [
            "BEAT: EPS $0.05 vs $0.04 (+25%); revenue $280M +21.6% YoY; ARR $1.16B +26% YoY.",
            "REACTION: -11% pre-market on a beat — market was positioned for larger ARR acceleration.",
            "PATTERN: Third name in a row where beating the print isn't enough — same as AVGO and ORCL.",
        ],
        "what_moves_it": "ARR growth durability and net-retention vs the whisper, not the stated consensus.",
        "client_talking_point": ("SailPoint confirms the pattern: beating the print is no longer enough. "
                                 "The AI-era multiple requires an accelerating beat, not just a beat. "
                                 "This is a data point, not a trade."),
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
        "Oracle's capex panic: $638B RPO confirmed the AI demand — but $70B FY27 capex + $20-25B prepayments "
        "+ $40B raise punished the stock. ECB decision TODAY (Jun 11): +25bp pending, sell-the-fact setup. "
        "Day-two US-Iran strikes push Brent toward $95. SPX put spread in the money (+129%). "
        "Adobe reports tonight. FOMC June 16-17 is the final gate. The book is positioned correctly."
    ),

    "summary_narrative": """
<p><strong>Oracle's Q4 FY26 print is the defining event of this tape</strong>, and it is a capex panic, not
a dilution story. The demand numbers are extraordinary: OCI infrastructure grew 93% YoY, Cloud +47%, total
revenue ~$19.2bn (slight beat), and the remaining performance obligations backlog surged to
<strong>~$638bn</strong> — up from ~$553bn last quarter, the largest confirmed AI order book in enterprise
software history. The AI demand thesis is confirmed. What punished the stock (-7 to -11% after hours) was
the cost of delivering it: FY26 capex came in at $55.7bn, above the ~$50bn guide; Oracle then guided
FY27 capex to <strong>~$70bn plus $20-25bn in component prepayments</strong> — a total capital commitment
of ~$90-95bn in one fiscal year. To fund this, Oracle announced a ~$40bn debt-and-equity raise (including
~$20bn in new shares). The market is not saying the demand is bad. It is saying: <em>we don't trust the
capital structure to fund this without destroying shareholder value.</em> That distinction — capital and
capacity problem, not a demand problem — is the thesis for the capital-protected note (idea 101).</p>

<p>The <strong>ECB decision is TODAY (Jun 11)</strong> and has not been announced as this brief is published.
The consensus is +25bp to 2.25% at near-100% probability — the first hike since September 2023 — fully
priced into EUR/USD (~1.15 pre-decision). The 'buy the rumour' crowd is fully positioned. Once the hike is
delivered, the sell-the-fact dynamic takes over; Lagarde's press conference tone is the pace-setter. A
'data-dependent pause' signal is the base case and accelerates MM-2026-012; any 'further hikes' language
squeezes EUR and requires respecting the 1.182 stop.</p>

<p>Geopolitically, the US-Iran conflict entered a <strong>second day of strikes</strong>. Iran fired back
targeting Gulf states. Tehran's foreign ministry declared the April ceasefire "practically meaningless."
Qatari mediators left empty-handed — uranium enrichment and frozen assets remain the sticking points.
<strong>Brent is climbing toward $93-95</strong>, Strait of Hormuz at ~15% of pre-war traffic, and
Bloomberg Intelligence forecasts $130/bbl for July-August if the Strait stays shut.</p>

<p>The SPX 7300/7000 put spread (MM-2026-008) is now <strong>in the money</strong> — the S&amp;P fell
-1.62% yesterday to ~7,267, through the 7300 strike. Mark ~$80 vs $35 premium paid (+129%). FOMC Jun 16-17
remains inside the Jun 27 expiry — the final catalyst in the window. Adobe reports after the close tonight
(idea 102 CSP gate opens post-print; do not pre-position).</p>
""",

    "takeaways": [
        "Oracle CAPEX PANIC: Revenue ~$19.2B (slight beat), OCI +93%, Cloud +47%, RPO $638B. BUT FY26 capex "
        "$55.7B (above guide), FY27 guided ~$70B + $20-25B prepayments. ~$40B raise (~$20B shares). Stock "
        "-7-11% AH. Market read: demand confirmed, capital structure is the problem. Capital-protected note "
        "(idea 101): protect vs dilution hangover, participate in OCI re-rate. Entry window NOW OPEN.",
        "ECB decision TODAY (Jun 11): +25bp to 2.25% PENDING at ~99% probability — decision not yet "
        "announced. Sell-the-fact setup: EUR/USD ~1.15 pre-decision = buy-the-rumour fully priced. "
        "MM-012 (short EUR/USD) is the trade. Lagarde presser post-decision is the pace-setter.",
        "Day-two US-Iran strikes. Iran fired at Bahrain, Kuwait, Jordan. Qatari talks failed. Ceasefire "
        "'meaningless.' Brent climbing toward $93-95. Strait at ~15% pre-war traffic. Oil longs earned.",
        "SPX put spread in the money: S&P -1.62% yesterday to ~7,267, below 7300 strike. Mark ~$80 vs "
        "$35 premium paid (+129%). Hold through FOMC Jun 16-17 — final catalyst inside Jun 27 expiry.",
        "Adobe reports after close tonight: EPS est $5.01 (Finnhub), rev $6.43-6.48B, ±9.47% implied move. "
        "CSP entry gate (idea 102) opens post-print. Do NOT pre-position.",
        "FOMC Jun 16-17 next week: 96-98% hold probability at 3.75%. Warsh's first presser is the dot-plot "
        "edge. Short-2Y (MM-013) and steepener (MM-009) are pre-positions that profit from a pause signal.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "30%",
         "headline": "FOMC pauses + Strait cracks open; Oracle dilution absorbed",
         "body": "Warsh signals data-dependent pause at FOMC Jun 16-17 — 2Y falls 15-20bp, equities recover, "
                 "Oracle dilution overhang fades as OCI growth data flows. Turkey/Qatar mediation produces "
                 "an interim Strait deal, Brent eases toward $88 from $95 — inflation narrative cools. "
                 "Risk up · rates down · dollar soft · gold consolidates."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "Grind — war premium stays, FOMC holds but no signal, Oracle rebuilds",
         "body": "Strait stays at 15-20% capacity, Brent holds $90-96. FOMC holds with zero-cut dots but "
                 "Warsh signals caution without hawkishness — no relief rally. Oracle's $20B raise proves "
                 "well-timed as OCI rev acceleration continues; dilution absorbed over weeks. Adobe prints "
                 "mixed AI monetisation data tonight. Risk mixed · rates range · dollar firm vs EUR."},
        {"kind": "bear", "label": "Bear", "pct": "25%",
         "headline": "Escalation to $100 oil or FOMC hawkish surprise triggers a re-rating",
         "body": "Day-three strikes, a confirmed mine incident or Strait closure to <10% traffic pushes Brent "
                 "toward $100-$110 (SPR running low); or Warsh's dot plot median shows zero cuts with a hike "
                 "bias — front-end blows out 20bp, AI multiples compress again. Adobe disappointment adds "
                 "to the AI-as-tax narrative. Risk down · rates up · gold up · SPX toward 7,000."},
    ],

    "insights_layers": """
<p>The Oracle print is the most important data point in the AI infrastructure build-out since Broadcom's
March quarter, and the market is reading it correctly — just not for the reason most people think.
The demand numbers are extraordinary: OCI +93%, RPO surged to ~$638bn (+15% vs last quarter alone),
total revenue ~$19.2bn. This is not a demand problem. The problem is the cost of serving the demand.
FY26 capex landed at $55.7bn — above the ~$50bn guide that was already making analysts nervous. Then
Oracle guided FY27 to ~$70bn in capex PLUS $20-25bn in component prepayments. That is a capital
commitment of ~$90-95bn in a single fiscal year from a company with ~$70bn in annual revenue. To fund
it: a ~$40bn debt-and-equity raise including ~$20bn in new shares — the largest capital raise in
Oracle's history. Stock fell 7-11% after hours. The market is not selling the AI thesis. It is selling
the equity structure of a company that has committed more capital than it can generate organically.
The non-consensus read: the $638bn RPO is the most bullish number in enterprise software history;
the $90bn annual capex commitment is the most frightening. Both can be true. A capital-protected note
is the instrument that lets you hold both positions simultaneously — participate in the OCI re-rate
if Oracle executes, absorb the dilution hangover if it can't fund the pipeline without further raises.</p>

<p>The ECB decision is <strong>TODAY (Jun 11) and has not been announced</strong> as this brief is
published. The consensus is +25bp to 2.25% at near-100% probability. EUR/USD is at approximately
~1.15 pre-decision — the level the market has been building to since the rate-hike narrative began.
The 'sell the fact' setup is not a prediction; it is a positioning observation. EUR ran from 1.08 to
1.15 on this hike cycle. The marginal buyer — the spec account pricing in the rate differential —
is fully positioned. Once delivery happens, the catalyst for EUR ownership is gone and the unwind
begins. Lagarde's press conference is the pace-setter: 'data-dependent pause' language accelerates
the short-EUR/USD (MM-012); explicit 'further hikes' language is the stop-test. The structural case
for the trade — ECB hiking into a soft European growth backdrop while the Fed holds — is intact
regardless of today's press conference specifics.</p>

<p>Geopolitically, the conflict is following the managed-grind playbook precisely as the
non-consensus read predicted. Day-two US strikes on Iran; Iran firing back at Gulf states; ceasefire
declared "meaningless"; Qatari mediators leaving empty-handed. The sticking points — uranium enrichment,
frozen assets — are the same as day one. The Strait of Hormuz remains at ~15% of pre-war traffic.
Bloomberg forecasts $130/bbl for July-August. The SPR is at multi-decade lows. The oil longs are not
overstayed; they were earned by a physical blockade and remain earned as long as the Strait is shut.</p>

<p>Go around the world. <strong>Asia:</strong> the AI-memory supply chain is intact — HBM demand is
the spine of every hyperscaler build, and Oracle's $638bn RPO implies accelerating HBM procurement.
NVDA consolidating 195-235 is a range, not a trend break. <strong>Japan:</strong> USD/JPY ~160,
MoF threatening intervention above 163, BoJ September hike >50% priced — carry unwind is coming,
not today. <strong>Europe:</strong> the ECB decision today is the event the DAX/Nasdaq ratio trade
was built for — if confirmed, European financials get NIM relief while US tech is still digesting
the Oracle capex shock.</p>

<p>Priced-versus-not: <strong>under-priced</strong> — the $90-95bn Oracle annual capex commitment
propagating through the AI infrastructure cohort (if Oracle needs $70B, what do Microsoft/Google/Amazon
need?); the $130/bbl July Brent scenario (call spread $100 strike only ~$6 away); FOMC hawkish
surprise (Warsh cannot look soft in week one). <strong>Fairly priced:</strong> Brent outright ~$93-95;
the ECB hike itself (fully in the price). <strong>Fully priced:</strong> Oracle revenue beat (already
discounted — the stock reacted to capex, not EPS); the soft CPI core (10Y already at 4.52%).</p>
""",

    "wrap": """
<p>Oracle's capex panic confirmed the AI demand and scared the capital markets in the same breath. OCI +93%,
RPO ~$638bn, revenue ~$19.2bn — every demand number was right. Then: $55.7bn FY26 capex (above guide),
$70bn FY27 guided + $20-25bn prepayments, $40bn raise. Stock -7-11% AH. The market isn't selling AI;
it's selling Oracle's equity structure. ECB decision is TODAY — +25bp is consensus at ~99%, not yet
announced. Sell-the-fact setup is the trade. US-Iran day-two strikes; Brent toward $95; SPX put spread
in the money at +129%.</p>

<p><strong>The driver.</strong> Oracle's capex guide is the read-through for the whole AI infrastructure
cohort: if Oracle needs $70bn per year, Microsoft/Google/Amazon face the same equation. The market hasn't
priced the capital-structure consequence of the AI buildout — only the revenue upside.</p>

<p><strong>So what to do.</strong> Hold all positions. The Oracle note window is open (idea 101). The ECB
sell-the-fact is pending (MM-012). The oil longs are earned. The SPX hedge is in the money. Do not add
before Adobe tonight — the CSP entry gate (idea 102) opens post-print only.</p>
""",

    "correlation_regime": """
<p><strong>1. Equities and bonds decoupled again — the safe-haven rotation is working.</strong> Yesterday:
S&amp;P -1.62% / Nasdaq -1.98% while the 10Y held at 4.52% and gold +0.80% to ~$4,104. Geopolitical
escalation → bond and gold bid. This is the barbell the book holds — long both tails simultaneously.</p>

<p><strong>2. EUR/USD and the ECB decision are the live cross-asset watch today.</strong> EUR/USD ~1.15
pre-decision: if +25bp delivers as consensus, the sell-the-fact dynamic begins. If EUR barely moves on
delivery (as the rate differential is fully priced), that IS the confirmation of the trade thesis — not
a contradiction of it. Watch EUR/USD in the hour after the announcement.</p>

<p><strong>3. Brent and equities are telling different stories.</strong> Brent rising toward $95 is an
oil-war supply story. Equity futures bouncing on "strikes complete" is a ceasefire-optimism story.
These should not trade together for long — the physical Strait blockade is more durable than the
headline-optimism bid. When they diverge, Brent stays bid longer.</p>
""",

    "vol_skew": """
<p><strong>The VIX is finally repricing the event calendar, but slowly.</strong> Estimated VIX9D ~18 · VIX ~21 ·
VIX3M ~22 · VIX6M ~23 — roughly 2-3 points higher than last week's complacency at 15.3. The S&amp;P is now
below the 7300 put strike, which means the hedge paid. The tell: the term curve is still flat (VIX ≈ VIX3M)
when it should be backwardated into the FOMC dot plot on Jun 16-17. The near-dated vol is catching up; the
term structure is not yet reflecting that the biggest macro catalyst of the summer (Warsh's first presser)
is six days away.</p>
""",

    "sector_rv": """
<p><strong>Leading:</strong> Energy producers (Brent ~$93-95 and rising), gold/metals (dual safe-haven + real-
rate bid at ~$4,104), European financials (ECB decision PENDING today — if hikes as expected, NIM relief).
<strong>Lagging:</strong> US tech/AI semis (Nasdaq -1.98% yesterday on Oracle capex panic; NVDA/AMD/AVGO
in range-mode), European luxury (LVMH: energy inflation + ECB tightening = twin headwind).</p>

<p><strong>RV:</strong> Long DAX / short Nasdaq (MM-2026-010) should recover today — Nasdaq -1.98% yesterday
was a tailwind; ECB decision (PENDING) is the catalyst for the DAX financials leg. The ratio dipped toward
0.949 (vs 0.943 stop) and today's dynamics should provide recovery. This is the structural case the trade
was built for: ECB rate hike = European banks rerate; US tech premium compresses on capex shock + war.</p>
""",

    "positioning": """
<p><strong>The EUR long crowd just got the hike it bought and is now trapped.</strong> Specs built EUR longs
into today's ECB and the delivery was as-expected; with EUR barely moving post-hike, the crowd that bought the
rumour is now sitting on a flat position that needs Lagarde to signal further hikes to make money —
and she isn't. The sell-the-fact unwind has begun (EUR/USD 1.1533 vs 1.162 at peak EUR) and should continue
as positioning unwinds over the next 2-5 sessions. Oil: spec positioning stayed constructive through the
truce headlines — no capitulation means the longs didn't need to be rebuilt; they're already there at $93.50.
Front-end rates: consensus is still positioned for a 2026 hike (the 2Y holds near 4.15%); a FOMC
data-dependent pause signal next week starts the unwind.</p>
""",

    "funding": """
<p>SOFR near 3.62% — unchanged. The plumbing is unmoved even through two days of US-Iran strikes and an ECB
hike. <strong>The Pozsar mechanic remains live:</strong> FOMC at 3.50-3.75% (held) means secured funding sits
well below the 2Y yield (~4.15%), and every floating-rate borrower issued in 2023-24 expecting two-to-three
cuts is still cash-flow negative versus its model. A FOMC pause signal next week narrows that gap; a hawkish
dot plot widens it. IG spreads are the tell — they tighten when the market believes the terminal rate is falling
and gap out when the hike narrative re-emerges.</p>
""",

    "tape_missing": """
<p><strong>1. The Oracle dilution story is masking the fundamental re-rate.</strong> The market punished the
raise (-10% AH) and is pricing the equity dilution math. It is not yet pricing what Oracle's $553bn backlog
converts to in OCI free cash flow in 18-24 months. The note structure (capital-protected, 70-80% participation)
is the right way to express this: you don't need to buy the dilution hangover, you just need to be there when
the OCI growth-rate compounds.</p>

<p><strong>2. The FOMC risk is asymmetric in the wrong direction for consensus.</strong> The market is at 96-98%
hold probability — which means it is priced for a do-nothing Fed. Warsh's first presser is the source of the
only non-trivial asymmetry left in US rates. He cannot afford to look soft with inflation at 4.2% headline; the
risk is hawkish surprise, not dovish pivot. The front end is under-pricing that tail.</p>

<p><strong>3. Brent approaching $100 is not in the equity VIX.</strong> At $93.50, the Brent call spread's
$100 strike is $6.50 away. A move to $100 — one mine incident, one confirmed Strait-closure escalation — and
the Bloomberg $130 forecast is the tape, not the tail. The SPX vol curve has not priced a $100+ oil scenario.</p>
""",

    "book_outlook": {
        "commentary": (
            "The book's best day yet on the derivatives side: the <b>SPX put spread is in the money at +129%</b>, "
            "the Brent call spread's $100 strike is only ~$6 away, and MM-012 (short EUR/USD) is positioned for "
            "the ECB sell-the-fact that fires TODAY. The equity sleeve remains the pressure point — Micron 25.8% "
            "concentration is squarely in the AI semis correction — but the <b>hedge book has now done more than "
            "offset the equity drag</b>. Today's live events: ECB decision PENDING (sell-the-fact setup on delivery); "
            "Oracle post-print capex panic overhang on semis/tech (RPO $638B confirmed, $90-95B capex commitment "
            "is the shock); Brent climbing toward $95; Adobe reports tonight (do NOT pre-position)."
        ),
        "outperform": [
            {"name": "Brent positions (MM-002, MM-003, MM-011)", "why": "Brent $93.50 climbing toward $95, Strait at "
             "15% capacity, Bloomberg $130 Jul-Aug forecast. The war premium is not a trade to be cut. The call "
             "spread's $100 strike is only $6.50 away from being in the money."},
            {"name": "Xetra-Gold (4GLD)", "why": "Gold at $4,104 (+0.80% yesterday) running on both engines: "
             "geopolitical safe haven (day-2 strikes) and real-rate compression (10Y at 4.52%, soft core). "
             "Dual bid — do not trim."},
            {"name": "Short EUR/USD (MM-012)", "why": "ECB decision PENDING today — sell-the-fact trigger fires on "
             "delivery. EUR ~1.15 pre-decision = buy-the-rumour fully priced. Lagarde presser tone sets the pace."},
            {"name": "SPX put spread (MM-008)", "why": "Now in the money at ~$80 vs $35 premium paid (+129%). Hold "
             "through FOMC Jun 16-17 — the final catalyst in the 26-day window."},
        ],
        "underperform": [
            {"name": "Micron (MU) — 25.8%", "why": "The book's largest equity risk, in the epicentre of the AI semis "
             "correction. Oracle dilution overhang bleeds across the cohort. The concentration is the amplifier."},
            {"name": "NVDA / AVGO / AMD", "why": "Same AI-capex-doubt complex. Oracle's $20B raise signals OCI needs "
             "capital at scale — the cohort de-rates on the bill, not the revenue. Range-bound at best."},
            {"name": "LVMH (MC FP)", "why": "ECB decision today + energy inflation = twin headwind for European "
             "luxury: rate tightening compresses the multiple; consumer budgets squeezed by oil prices."},
            {"name": "US Treasury 1.25% 2031", "why": "The underwater bond is above water on a mark-to-live basis "
             "as the 10Y stays at 4.52%, but it is still the tail risk if Warsh delivers hawkish dots next week."},
        ],
        "watch": [
            {"label": "Do not pre-position Adobe", "text": "The CSP entry gate for idea 102 opens only after tonight's "
             "print. Hold cash, set the entry level ($385 CSP if ADBE trades down to support), and let the "
             "implied-move settle before sizing."},
            {"label": "Maintain the SPX hedge", "text": "The put spread is +129% but FOMC Jun 16-17 is still inside "
             "the Jun 27 expiry. Do not take profit early — this is the book-level tail protection for the "
             "highest-risk event remaining in the window."},
            {"label": "Oracle note window open", "text": "The capital-protected note (idea 101) is the post-print "
             "entry vehicle: full downside protection against the $20B dilution hangover, 70-80% participation "
             "in the OCI re-rate. The window opened last night and typically runs 5-10 sessions."},
            {"label": "FOMC positioning", "text": "Short-2Y (MM-013) and the steepener (MM-009) are the pre-positions "
             "that profit from a Warsh pause signal. Do not add new risk; let the existing book work."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> Oracle's capex shock is a structural problem — $70bn FY27 capex + $20-25bn
prepayments = ~$90-95bn annual capital commitment from a ~$70bn revenue company. The $40bn raise is just
year one. The equity is correctly down 7-11% because the free-cash-flow inflection is now 2-3 years away,
not 12-18 months, and each subsequent year will need similar capital raises. The AI theme is right but
Oracle's equity structure makes it uninvestable at current multiples.</p>

<p><strong>The strongest argument against — the OFFER:</strong> Oracle's RPO surged to ~$638bn — the AI
demand is not only confirmed, it is accelerating. The $90-95bn capex is funding a pipeline that has
already been contracted. A company that can grow its OCI backlog by $85bn in one quarter and convert it
at 93% YoY growth is not impaired — it is capital-constrained. A structure (note, protected equity)
that lets you hold the conviction without the equity-dilution risk is the right instrument. The note
window is open today.</p>
""",

    "one_chart": """
<p class="theme">SPX put spread: $35 paid, ~$80 mark, +129% — and the FOMC catalyst is still inside expiry.</p>
<p>The SPX 7300/7000 put spread (MM-2026-008) is now in the money. The S&amp;P fell to ~7,267 yesterday
(-1.62%), through the 7300 strike, marking the biggest single-session move in the derivatives book to date.
The spread was entered at $35; current estimated mark is $80. The Jun 27 expiry has one major catalyst
remaining inside it: the FOMC dot plot on June 16-17. Warsh cannot look soft in his first meeting with
headline CPI at 4.2%; a zero-cut dot median would push the S&amp;P toward 7,000 and the spread moves toward
full intrinsic ($300). Hold through FOMC — this is exactly what the hedge was designed for.</p>
""",

    "catalyst_calendar": [
        {"day": "Wed", "date": "Jun 10 ✓",
         "event": "US May CPI — DONE: 4.2% headline, 2.9% core",
         "consensus": "Headline +0.5% m/m / 4.2% y/y (highest since Apr-23); core +0.2% m/m / 2.9%, BELOW the 0.3% forecast. Energy ~60% of the rise (BLS).",
         "view": ("Hot headline, soft core — the inflation is energy, not breadth, and the Fed can look through it. "
                  "The 10Y eased to ~4.52%; the soft core hands the short-2Y (MM-013) and steepener (MM-009) their thesis."),
         "asymmetry": "DONE: core undershoot = front-end relief confirmed. Risk is energy base dragging core higher next month.",
         "dir": "down"},
        {"day": "Wed", "date": "Jun 10 ✓",
         "event": "Oracle (ORCL) Q4 FY26 — PRINTED: capex panic selloff",
         "consensus": "Revenue ~$19.2bn (slight beat), OCI +93%, Cloud +47%, RPO surged to ~$638bn. "
                      "FY26 capex: $55.7bn (above ~$50bn guide). FY27 guided ~$70bn + $20-25bn prepayments. "
                      "~$40bn debt+equity raise (~$20bn share sale). Stock -7 to -11% AH.",
         "view": ("Demand confirmed ($638B RPO); capital structure is the problem ($90-95bn annual commitment). "
                  "Market read: capital and capacity problem, not a demand problem. Capital-protected note (idea 101): "
                  "absorbs dilution hangover, participates in OCI re-rate. Entry window NOW OPEN."),
         "asymmetry": "DONE: note window open. If OCI growth accelerates in Q1 FY27 without further raises, re-rate.",
         "dir": "down"},
        {"day": "Thu", "date": "Jun 11 ← TODAY (PENDING)",
         "event": "ECB rate decision — +25bp to 2.25% PENDING (consensus ~99%)",
         "consensus": "+25bp expected at ~99%; first hike since September 2023. EUR/USD ~1.15 pre-decision.",
         "view": "Sell-the-fact setup: EUR was bid from 1.08 to 1.15 pricing this hike. Once delivered, the "
                 "marginal EUR buyer is done. Lagarde's presser tone ('data-dependent pause' vs 'further hikes') "
                 "sets the EUR/USD direction post-decision. MM-012 is the trade.",
         "asymmetry": "Delivery + pause signal: EUR/USD -0.5 to -1%; 'further hikes' language: EUR spike then fade (respect 1.182 stop)",
         "dir": "down"},
        {"day": "Thu", "date": "Jun 11 (tonight)",
         "event": "Adobe (ADBE) Q2 — after close",
         "consensus": "Consensus EPS $5.01 (Finnhub); rev $6.43-6.48bn; implied move ±9.47%. Near 52-week lows.",
         "view": "Cleanest remaining test of whether generative-AI is a software tax or tailwind. DO NOT pre-position — "
                 "wait for the print to open the CSP entry gate (idea 102: $385 cash-secured put).",
         "asymmetry": "AI additive to ARR: software relief +8-10%; cannibalisation read: ADBE toward $330s, CSP assigned",
         "dir": "flat"},
        {"day": "Tue-Wed", "date": "Jun 16-17",
         "event": "FOMC + dot plot — Warsh's first meeting, 96-98% hold priced",
         "consensus": "Hold at 3.50-3.75% consensus; dots are the whole event. Warsh cannot look soft with 4.2% CPI.",
         "view": "Zero-cut median: 2Y +10bp, gold sells, S&P -1.5%. One-cut held: 2Y -15bp, gold +2%, S&P +1%. "
                 "Short-2Y (MM-013) and steepener (MM-009) are positioned for the pause signal.",
         "asymmetry": "0-cut dots: DXY +0.7%, 2Y +10bp; 1-cut held: 2Y -15bp, gold +2%; hike bias: 2Y +25bp, S&P -3%",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660. At ~1.636; stop 1.662. ECB decision PENDING today — Lagarde's presser post-decision is the live catalyst. 'Further hikes' language = stop test.</li>
<li><strong>MM-2026-002 · Long Brent:</strong> exit on weekly close below $87 — war premium gone. At ~$93.50, climbing. The Strait is still shut. Hold.</li>
<li><strong>MM-2026-003 · Long Brent/Short WTI spread:</strong> discretionary close below $2.00. At ~$3.40. Stop 1.50. Day-2 strikes widen the quality premium.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop at 4.65%. At ~4.52%. CPI core undershot (2.9%) — working. FOMC Jun 16-17 is the catalyst. Do not add.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to July 15. Stop $4,250. At ~$4,104, dual bid (geopolitical + real-rate). Min_hold rule applies; do not force exit.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160.2. BoJ Sept hike >50% priced. Carry unwind coming, not today.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> now in the money (+129%). Hold through FOMC Jun 16-17 — final catalyst inside Jun 27 expiry. No change.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to July 16. At ~+43bp; target +60bp. FOMC is the catalyst. Hold.</li>
<li><strong>MM-2026-010 · Long DAX / short Nasdaq:</strong> stop ratio 0.943. ECB decision PENDING today (DAX financials tailwind if confirmed); Nasdaq -1.98% yesterday on Oracle capex panic. Ratio should recover. Hold.</li>
<li><strong>MM-2026-011 · Brent 100/115 call spread:</strong> gaining. $100 strike only ~$6 away at ~$93-95. Hold. Exit: Brent falls below $85 for 3 sessions.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. EUR ~1.15 pre-ECB decision (PENDING today). Sell-the-fact trigger fires on delivery. Hold.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold 30 days. At ~4.15%. Core CPI soft. FOMC next week is the payoff. Do not add.</li>
</ul>
""",

    "client_ammo": [
        {"q": "Oracle beat everything — why is the stock down 7-11%?",
         "a": ("Because the market is pricing the capex bill, not the revenue beat. Oracle's RPO surged to $638bn "
               "— the largest AI backlog in enterprise software history. The demand is confirmed. The problem is "
               "the cost: FY26 capex came in at $55.7bn (above the $50bn guide), then Oracle guided FY27 to "
               "$70bn PLUS $20-25bn in component prepayments. That's ~$90-95bn in capital commitment in one "
               "fiscal year from a company with $70bn in annual revenue. To fund it: $40bn raise including "
               "$20bn in new shares. The market read: capital and capacity problem, not a demand problem. "
               "A capital-protected note is the right instrument — you get 70-80% participation in the OCI "
               "re-rate if Oracle executes, and 100% capital protection if the capital structure buckles.")},
        {"q": "The ECB decision is today — what should I expect?",
         "a": ("The hike is already priced — +25bp to 2.25% at near-100% probability. EUR ran from 1.08 to 1.15 "
               "pricing this in. So the hike delivery is a non-event by itself. What matters is Lagarde's press "
               "conference: if she signals 'data-dependent pause' (the base case, given the inflation is energy-led "
               "and the European growth backdrop is soft), EUR fades from ~1.15 and the short EUR/USD trade "
               "(MM-012) accelerates. If she signals 'further hikes ahead', EUR spikes short-term, we respect "
               "the 1.182 stop. The bet is on the presser, not the hike.")},
        {"q": "We've had two days of US-Iran strikes. Is it escalating or de-escalating?",
         "a": ("Neither — and that is the correct answer. The market keeps pricing a binary (deal or war). The "
               "political reality is a managed, on-again-off-again conflict: Trump wants both the deal headline "
               "and the 'we hit them hard' headline. Iranian domestic politics cannot survive a visible concession "
               "on enrichment. Qatari mediators left Tehran empty-handed. The Strait is at 15% capacity. Brent "
               "is at $93.50 and Bloomberg forecasts $130 for July-August if it stays shut. The trade is not to "
               "predict the outcome; it's to own the premium while the Strait is physically shut.")},
        {"q": "Adobe reports tonight — should I be doing something?",
         "a": ("No position before the print. The entry gate for the cash-secured put (idea 102) opens only "
               "after we see the number. If ADBE beats on AI ARR contribution — software relief, we wait for a "
               "better entry. If it misses on AI cannibalisation — ADBE trades down toward $330s and the CSP "
               "gets assigned at the $385 strike, owning shares at a 10% discount to today. Either way, "
               "pre-positioning is not edge; it's guessing. The discipline is to wait.")},
    ],

    "ideas_note": (
        "<p>Two entry triggers are live today. The Oracle capital-protected note (idea 101) window opened "
        "post-print last night: the ~$90-95bn annual capex commitment is the near-term overhang; the $638bn "
        "RPO is the long-term thesis. The note structure holds both. The ECB decision is PENDING today "
        "(idea 1 / MM-012: sell-the-fact on delivery) — the entry thesis fires once the hike is confirmed "
        "and Lagarde's presser tone is heard. The Brent call spread (idea 11) has its $100 strike "
        "only ~$6 away at ~$93-95. Adobe tonight is the gate for idea 102 CSP — do not pre-position. "
        "No net-new ideas today: the 17 existing ideas cover every regime dimension.</p>"
    ),

    "event_radar_note": (
        "<p>Two of five catalysts are confirmed behind us: CPI Jun 10 (hot headline, soft core ✓) and Oracle "
        "Jun 10 AH (capex panic selloff ✓). Three remain: ECB Jun 11 (PENDING TODAY — +25bp consensus, "
        "sell-the-fact on delivery), Adobe after tonight's close (AI tax or tailwind — CSP entry gate opens "
        "post-print), and Kevin Warsh's first FOMC dot plot June 16-17 (the biggest remaining macro event, "
        "zero-cut vs pause-signal asymmetry). The book is pre-positioned for the FOMC via short-2Y and "
        "the steepener; no action needed before the Adobe print.</p>"
    ),

    "burry_tell": (
        "Oracle guided $70bn in FY27 capex plus $20-25bn in component prepayments — roughly $90-95bn "
        "total capital commitment from a company with $70bn in annual revenue. The RPO of $638bn means the "
        "demand is real. The problem is the ratio: Oracle is committing more capital in one year than it "
        "generates in revenue. Nobody is asking what this implies when Microsoft ($70-100bn), Google, "
        "Amazon and Meta face the same equation. The AI infrastructure trade has quietly become a "
        "<em>capital markets trade</em> — who can fund the build without a structural dilution cycle? "
        "Oracle just showed the equity market's answer: it will punish the announcement even when "
        "the demand is confirmed. The structural point that nobody is pricing: the $638bn RPO is the most "
        "bullish demand number in enterprise software history, but the capital structure required to deliver "
        "it means the free-cash-flow inflection is 3-4 years away, not 12-18 months. Pricing the backlog "
        "without pricing the capital drag is the consensus error."
    ),

    "earnings_summary": (
        "Oracle: POST-PRINT capex panic. Revenue ~$19.2B (slight beat), OCI +93%, Cloud +47%, RPO ~$638B. "
        "FY26 capex $55.7B (above ~$50B guide); FY27 guided ~$70B + $20-25B prepayments; ~$40B raise. "
        "Stock -7-11% AH. Capital and capacity problem, not a demand problem. Note structure (idea 101) "
        "is the entry: protect against the capital-structure overhang, participate in the OCI re-rate. "
        "SailPoint: POST-PRINT, beat but cautious guide (-11% pre-market). "
        "Adobe: PRE-PRINT tonight — EPS $5.01 est (Finnhub), rev $6.43-6.48B, implied move ±9.47%. "
        "CSP gate (idea 102: $385 put) opens post-print. Do not pre-position."
    ),
    "earnings_why": (
        "Oracle and Adobe are the two software/cloud prints that bracket the AI-capex debate the macro book is "
        "built around: Oracle confirms or denies the OCI infrastructure thesis; Adobe confirms or denies whether "
        "generative AI is a software incumbents' tailwind or tax. SailPoint is the early-bird identity-security "
        "read. All three cleared the universe filter — $10bn+ cap, US/Korea, Tech/Financials/Industrials/Utilities, "
        "reporting inside the 5-day-pre / 3-day-post window. Consensus EPS and recommendation splits are "
        "Finnhub-sourced; implied-move and positioning fields supplemented by web search (tagged estimated)."
    ),

    "book_aim": (
        "Hold all positions, collect the confirms. The SPX put spread is in the money (+129%); the Brent call spread "
        "is $6.50 from its $100 strike; the short-EUR/USD sell-the-fact is running; the rates pre-positions are "
        "pointed at FOMC Jun 16-17. The aim for the rest of June: survive the FOMC with the book intact, "
        "let the derivatives carry the P&L while the equity sleeve consolidates, and execute the Oracle note "
        "and Adobe CSP entries post-print to compound the structural AI thesis without adding naked equity risk. "
        "No new directional bets until after June 17."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the two option lines are "
                 "model estimates from spot.")
    },
    "idea_selection": [
        {"label": "Oracle note (idea 101) — entry open", "in": True,
         "text": ("Post-print window opened last night. The $20bn dilution is the overhang; the 93% OCI growth is "
                  "the thesis. Capital-protected note: 100% capital protection + 70-80% participation in "
                  "ORCL re-rate. Size: up to 5% of book; 12-18 month tenor. Entry window: 5-10 sessions.")},
        {"label": "Adobe CSP (idea 102) — gate opens tonight", "in": False,
         "text": ("Do NOT enter before tonight's print. If ADBE trades down on AI cannibalisation fears: "
                  "$385 put / Jun 27 or Jul 18 expiry. If ADBE beats on ARR contribution: wait for a better "
                  "entry at lower support. The gate is the print, not the pre-positioning.")},
        {"label": "Brent longs (MM-002/003/011)", "in": True,
         "text": ("Kept, not added. Earned by a Strait still at 15% capacity. Brent $93.50 and rising. "
                  "The call spread's $100 strike is $6.50 away. Exit: weekly close below $87.")},
        {"label": "No net-new ideas until post-FOMC", "in": False,
         "text": ("FOMC Jun 16-17 is 6 days away. Warsh's first dot plot is the regime-defining event for "
                  "the rest of Q2. The existing 17 ideas cover all regime dimensions — oil, rates, FX, equity "
                  "single-names, vol. Forcing a new idea in front of the Fed is noise, not edge.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 18.5},
        {"label": "VIX",   "value": 21.2},
        {"label": "VIX3M", "value": 22.0},
        {"label": "VIX6M", "value": 23.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.15, 3)},
        {"label": "5Y",  "value": 4.36},
        {"label": "10Y", "value": round(_g("us10y") or 4.55, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 5.02, 3)},
    ],

    "new_ideas":          [],
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
