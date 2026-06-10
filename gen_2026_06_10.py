#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-10 (Wednesday).

May CPI day — and it printed: hot headline 4.2%, soft core 2.9%. Iran/Israel truce still fragile;
Brent has eased from $93 to ~$91 but the Strait is still shut. The AI de-rating
story is still the dominant equity narrative — Oracle earnings tonight is the next
data point. Gold stop was touched but held (min_hold 45d rule). Book unchanged.

Run:  python gen_2026_06_10.py
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
levels["MM-2026-008"] = 45.0
levels["MM-2026-011"] = 2.0

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
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = "Hot Headline, Soft Core — Truce Still Under Fire"
regime_note = (
    "May CPI printed this morning and split the difference: headline +0.5% m/m / 4.2% y/y — the highest since "
    "April 2023 and a third straight acceleration — but core just +0.2% m/m / 2.9% y/y, BELOW the 0.3% forecast "
    "(BLS). The hot headline is energy: the Iran shock pushed energy ~23.5% y/y and it drove over 60% of the "
    "monthly increase, while the core stayed contained. The bond market read the soft core as relief — the 10Y "
    "eased to ~4.52% from a 4.55% intraday high. Equities still fell (S&P -0.37%, Nasdaq -0.42%, Dow -0.78%), and "
    "the swing driver was Trump: after floating a deal 'in two or three days' on Monday (stocks up, Brent -3%), he "
    "told reporters today the US is 'going to be attacking them very hard' and would hit Iran the same day, citing "
    "a downed US Apache in the Strait — a Truth Social post called Iran's military 'a complete and total mess.' "
    "That headline whipsaw drove the intraday tape; Brent holds ~$91.4 on the blockaded Strait. Oracle reports "
    "after the close and the ECB hikes tomorrow."
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
            "The ECB rate path has been repriced dovish after weaker eurozone data, while the AUD "
            "carries a terms-of-trade tailwind from firm iron ore (~$105/t). The EURAUD cross sits "
            "roughly one full figure (~170 pips) above where the 2-year EUR-AUD rate differential "
            "implies fair value. That gap is the edge — a mean-reversion trade with the rate path "
            "and the commodity both pointing the same direction."
        ),
        "catalysts": [
            "ECB rate decision Thu 11 Jun (+25bp fully priced; press conference sets the euro direction "
            "— 'data-dependent pause' language = sell EUR)",
            "Iron ore price action (any Chinese demand headline or PBOC stimulus)",
            "RBA June meeting (if hawkish, AUD further supported)",
        ],
        "risks": (
            "ECB more hawkish than expected (EUR squeezed higher); iron ore collapses on China "
            "demand shock (AUD loses its tailwind); broader risk-off drives USD safe-haven bid "
            "rather than a EUR/AUD move; stop at 1.662."
        ),
        "breakdown_why": {
            "gap":          "3/3 — the cross is ~170 pips above the 2yr spread's implied fair value; "
                            "a full-figure mispricing between a dovish ECB and an RBA still hiking.",
            "catalyst":     "1/2 — ECB on Thu is the trigger, but it is already mostly priced; "
                            "the edge is in the press conference tone, not the hike itself.",
            "positioning":  "1/2 — EUR longs into the ECB are crowded (spec long at multi-year highs "
                            "vs AUD), which provides squeeze fuel if the meeting disappoints.",
            "confirmation": "1/2 — the cross sold off from the 1.66 handle, giving one technical "
                            "confirmation; not yet a clean breakdown.",
            "stop_quality": "1/1 — 1.662 is a clear technical level; 17 pips above entry; tight "
                            "relative to the 35-pip target move.",
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
            "The market removed the war premium from crude before the war risk was removed from "
            "the Gulf. Tehran rejected MoU terms, the Strait of Hormuz remains under a dual US-Iran "
            "blockade, and speculative net length was cut from 191.9k to 178.8k — leaving squeeze fuel. "
            "Asymmetric: ~$7 of downside to recent floor vs ~$13 to a re-escalation reprice. "
            "This is the right-tail hedge on a portfolio barbell, not a directional peace call."
        ),
        "catalysts": [
            "Strait of Hormuz status (any confirmed mine/tanker incident = $100+ gap)",
            "Iran/Israel re-escalation (Lebanese front is the fuse Netanyahu will not link to the truce)",
            "OPEC+ emergency meeting (supply cut = price floor lifted)",
            "Weekly US crude inventory data (EIA Wednesdays)",
        ],
        "risks": (
            "Genuine ceasefire + Strait reopening (premium collapses toward $84 support); demand "
            "destruction from recession fears (China demand miss); dollar spike on hot CPI."
        ),
        "breakdown_why": {
            "gap":          "2/3 — clear mispricing: Hormuz blockade premium was removed from price "
                            "before the physical constraint was removed. Not a regime-level 3 because "
                            "some war premium was already re-inserted.",
            "catalyst":     "2/2 — dated geopolitical catalysts (truce breakdowns) and physical events "
                            "(tanker/mine) are on the near-term horizon; well-defined payoff triggers.",
            "positioning":  "1/2 — specs cut net length but are not cleanly short; no pure squeeze "
                            "fuel. Neutral to slightly supportive.",
            "confirmation": "0/2 — no technical confirmation yet; the price has not broken to new "
                            "highs to confirm re-acceleration.",
            "stop_quality": "1/1 — weekly close below $84 is a clean structural level; $7 risk vs "
                            "$13 reward = disciplined R/R.",
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
            "Brent crude -17% at the time of trade entry is a forward CPI cut the FedWatch "
            "distribution (67.8% no-cuts in 2026) has not priced. Bonds already rallied 26bp "
            "off the 4.70% high; the disinflation impulse from falling energy rolls headline "
            "CPI lower into autumn. Deliberately the opposite macro leg to the Brent longs — "
            "the book owns both sides of the oil binary and gets paid on either resolution."
        ),
        "catalysts": [
            "May CPI (Jun 10, 8:30 ET) — below 3.7% triggers front-end rally; above 4.1% stops trade",
            "FOMC dot plot Jun 16-17 — zero-cut median = yield up, test stop; one-cut held = yield falls",
            "Warsh's first FOMC meeting — can't look soft on inflation in week one",
            "Treasury supply (June/July refunding — supply shock risk to the long end)",
        ],
        "risks": (
            "Hot CPI re-arms the year-end hike; Warsh proves hawkish; fiscal supply shock pushes "
            "term premium higher; geopolitical re-escalation drives commodity prices and re-inflates. "
            "Stop at 4.65% (currently near 4.53%, ~12bp away)."
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
            "Gold has already decoupled from the 4.98% long bond — pricing both MoU tails at once. "
            "It wins if oil disinflation forces a dovish Fed (real yields fall) AND it wins if the "
            "MoU fails and the geopolitical bid returns. It only loses on the narrow path: "
            "strong growth + stable oil + aggressive hawkish Fed together. This is the asymmetry "
            "pre-positioning is built for. Minimum 45-day hold — not an event-day scalp."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — zero-cut median bearish for gold; one-cut held = gold bids",
            "May CPI Jun 10 — hot print tests $4,250 stop; soft print lifts real rates outlook",
            "Warsh's first press conference tone on inflation vs productivity",
            "EM central bank Q2 gold purchase data (China, India, Turkey structural buyers)",
        ],
        "risks": (
            "Hot CPI + aggressive hawkish dot plot (real yields surge, gold tests $4,250 stop — "
            "stop already touched Jun 10 at $4,200 but min_hold rule preventing close); strong "
            "USD spike; gold-specific spec flush; competing safe-haven assets (Treasuries) outbid."
            " NOTE: Stop touched 10 Jun ($4,200 vs $4,250 stop) but min_hold 45d rule applies — "
            "position stays open per pre-position ruleset."
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
            "VIX at 15.3 when purchased was cheap for 4 non-trivial events in 15 days: AVGO Jun 3, "
            "payrolls Jun 5, ECB Jun 11, FOMC Jun 16-17. 0.5% notional cost; 7.6x payoff if SPX "
            "draws down 6% to 7000. Insurance on a portfolio long AI equities — not a directional "
            "short but a tail hedge that is still close to the money after the chip bounce failed."
        ),
        "catalysts": [
            "May CPI Jun 10 (above 4.1% re-arms hike, sells equity)",
            "Oracle Q4 earnings Jun 10 AMC (AI-capex de-rating risk)",
            "ECB Jun 11 (hawkish surprise = risk-off)",
            "FOMC dot plot Jun 16-17 (0-cut median = market sell-off)",
        ],
        "risks": (
            "SPX rallies through 7500+ (premium decays to zero but max loss is limited to $35 "
            "paid); VIX collapses (vol crush); time decay if no sell-off before Jun 27 expiry. "
            "Risk is fully defined — no further loss beyond the $35 premium."
        ),
        "breakdown_why": {
            "gap":          "2/3 — vol was cheap (VIX 15.3) vs 4 binary events in 15 days; "
                            "clear mispricing of event risk.",
            "catalyst":     "2/2 — multiple dated catalysts (CPI, ECB, FOMC, earnings) all "
                            "within the 26-day expiry window.",
            "positioning":  "2/2 — the market was positioned long/complacent (VIX low, "
                            "specs long equities) = maximum fuel for a vol spike if events "
                            "disappoint; best-in-book positioning score.",
            "confirmation": "0/2 — no technical confirmation on entry (bought when SPX was "
                            "still near highs); insurance bought at inception.",
            "stop_quality": "1/1 — defined-risk structure; max loss is the $35 premium paid, "
                            "not a dynamic stop.",
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
            "Friday's selloff was a single-factor US event — AI concentration plus a hawkish "
            "payroll — and Europe decoupled outright (DAX +0.2% vs Nasdaq -4.2%). The ECB hikes "
            "Thursday into a financials-heavy DAX index that has no AI capex cycle to give back. "
            "The divergence is structural, not sentiment: different sector composition, different "
            "central bank cycle, different valuation multiple."
        ),
        "catalysts": [
            "ECB Jun 11 (+25bp priced; financials = ECB hike beneficiary; DAX leg up)",
            "Oracle earnings Jun 10 AMC (AI cohort re-rates = Nasdaq leg down)",
            "Any AI capex disappointment (de-rates Nasdaq multiple vs DAX)",
            "EUR/USD: weaker EUR flatters DAX exporters in EUR terms, pairs with short-EURUSD",
        ],
        "risks": (
            "AI cohort keeps leading through CPI/FOMC (Nasdaq outperforms, ratio falls to stop); "
            "German recession fears resurface (ECB seen as policy mistake); EUR spikes on hawkish "
            "ECB, hurting DAX exporters; ratio at 0.9544, stop at 0.943 — one more Nasdaq-led "
            "session triggers the stop."
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
            "The Hormuz tail was already firing when this was entered: Israel hit western/central Iran, "
            "US hit Iranian radar sites, Iran fired at Kuwait/Bahrain, Brent gapped +3% to $96 with "
            "MoU deadlocked on $24bn frozen assets. A confirmed mine or tanker hit takes the Strait "
            "premium toward $110+. Defined-risk momentum entry above spot; max loss is the $3 premium."
        ),
        "catalysts": [
            "Confirmed mine/tanker incident in the Strait of Hormuz (immediate gap to $110+)",
            "Iran resumes strikes (Lebanon fuse Netanyahu won't link)",
            "OPEC+ emergency meeting on supply cuts",
            "Brent weekly close above $97 (momentum confirmation)",
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
            "Thursday's 25bp ECB hike is 99% priced — the rate-differential tailwind for EUR is "
            "already fully in the price. A hawkish US repricing (payrolls + inflation fears) "
            "widened the differential gap the other way. Classic buy-rumour-sell-fact setup into "
            "a fully-priced central bank. Pairs cleanly with long DAX (a weaker EUR flatters the "
            "German exporters in the DAX)."
        ),
        "catalysts": [
            "ECB Jun 11 press conference tone ('data-dependent pause' = sell EUR immediately)",
            "FOMC Jun 16-17 (Fed holds, dollar bids, EUR falls)",
            "May CPI Jun 10 (hot print = USD strengthens, EUR/USD falls)",
            "Spec positioning unwind (EUR longs near multi-year highs = crowded unwind fuel)",
        ],
        "risks": (
            "ECB surprise hawkishness (hawkish tone lifts EUR above 1.182 stop); US data "
            "disappoints and EUR/USD re-rates higher; safe-haven EUR bid (rare but possible in "
            "extreme risk-off); stop at 1.182."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the mispricing is real but contained (the ECB hike IS priced; "
                            "the gap is the reaction to the press conference wording, not a "
                            "regime-level mispricing); hence 1 not 2.",
            "catalyst":     "2/2 — ECB press conference is a precise, dated catalyst with "
                            "well-defined payoff trigger (specific phrase/tone).",
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
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},
    {"name": "MOVE", "level": "~108 (est)", "chg": "", "dir": "flat"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Wed 10 Jun · TradingView"},
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
    "MM-2026-001": "Working. EURAUD drifted to ~1.636 as iron ore eased; the cross sits below entry. Thesis intact into Thursday's ECB — the hike is a growth error and EUR sells the fact. Stop 1.662.",
    "MM-2026-002": "Working — and validated by the tape. Brent held ~$93 despite the ceasefire headline; the war premium did not leave. Kept as the cheap re-escalation hedge. Exit on a weekly close below $87. Target $104.",
    "MM-2026-003": "Open, near flat. Brent-WTI spread ~$3.26 versus the 3.30 entry — nowhere near the $2.00 exit. The market did not collapse the Hormuz-specific premium; the spread is doing what it should. Stop 1.50.",
    "MM-2026-004": "Working at last. The soft CPI core eased the 10Y to ~4.52% from a 4.55% intraday high — the disinflation impulse the trade needs finally showed up. Stop 4.65%, ~13bp away. Let it run into the dot plot; do not add.",
    "MM-2026-005": "Stop touched ($4,200 vs $4,250 stop) but min_hold 45d rule applies — position held per pre-position ruleset. Gold near $4,344 decoupled from oil and trading real rates. Min hold to ~July 15.",
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
    {"datum": "May payrolls +172k",  "source": "BLS June 5",                          "asof": "2026-06-05", "stale": True},
    {"datum": "ORCL/ADBE/SAIL est",  "source": "Finnhub (earnings_data.md, Jun 8 6am)","asof": "2026-06-08", "stale": True},
    {"datum": "SOFR ~3.62% / MOVE",  "source": "NY Fed (rail) / MOVE unverified",     "asof": "2026-06-08", "stale": True},
]

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
        "May CPI came in hot on the headline (4.2%) but soft on the core (2.9%, +0.2% m/m) — the inflation is "
        "energy, not breadth — so the 10Y eased to ~4.52% even as equities fell on fresh US-Iran strikes. The "
        "tape's verdict: a war premium in oil and a contained core in rates, with Oracle tonight and the ECB "
        "tomorrow the next live catalysts."
    ),

    "summary_narrative": """
<p>The number everyone waited for landed, and it cut both ways. May CPI ran to <strong>4.2% headline</strong>
(+0.5% m/m) — the hottest since April 2023 and a third straight monthly acceleration — but the <strong>core was
soft: +0.2% m/m, 2.9% y/y, below the 0.3% consensus</strong> (BLS). The split is the whole story: the headline
is energy, not breadth. The Iran shock pushed the energy index up ~23.5% year-on-year and energy alone drove
over 60% of the monthly increase, while the core — the part the Fed actually targets — stayed contained.</p>

<p>The bond market sided with the core. The US 10-year <strong>eased to ~4.52%</strong> after touching 4.55%
intraday, taking the print as evidence the energy shock has not yet spilled into broad price pressure
(Trading Economics). That is the relief our front-end trades were waiting for. Equities did not get the memo:
the <strong>S&amp;P fell 0.37%, the Nasdaq 0.42% and the Dow 0.78%</strong>, with tech, industrials and
discretionary leading lower (TheStreet) — and the swing factor was the President. <strong>Trump whipsawed the
tape on the wire</strong>: on Monday he floated a deal with Iran "in two or three days," which rallied stocks
and knocked ~3% off Brent; today he told reporters the US is "going to be attacking them very hard" and would
hit Iran the same day, citing Iran downing a US Apache in the Strait, with a Truth Social post calling Iran's
military "a complete and total mess." Risk-on to risk-off in 24 hours, on headlines, not data.</p>

<p>Oil keeps its nerve: <strong>Brent ~$91.4, WTI ~$88.3</strong>, the war premium intact on a Strait of Hormuz
that is still effectively blockaded as the strikes resume. That premium is earned by a physical fact, not a
sentiment, which is exactly why a hot energy-led headline does not change the rates call — the core says the
Fed is not forced to hike on this.</p>

<p>Two live catalysts are left in the window: <strong>Oracle reports after the close</strong> — the first real
test of whether its $553bn AI backlog converts without capex blowing out the model — and the <strong>ECB hikes
+25bp tomorrow</strong> into euro-area inflation at 3.2%. The disciplined posture holds: the oil longs are
earned by the blockade, the rates trades (short 2Y, the steepener) just got the soft-core tailwind, and the
book carries both tails into the dot plot next week.</p>
""",

    "takeaways": [
        "May CPI is OUT: headline hot at 4.2% y/y (+0.5% m/m, highest since Apr 2023, 3rd straight acceleration) but core SOFT at +0.2% m/m / 2.9%, below the 0.3% forecast (BLS). The inflation is energy, not breadth.",
        "Energy did it: the Iran shock lifted energy ~23.5% y/y and drove >60% of the monthly increase. Strip it out and the core says the Fed is not forced to hike.",
        "The 10Y eased to ~4.52% (off a 4.55% intraday high) — the bond market took the soft core as relief. That's the tailwind our short-2Y and steepener were waiting for.",
        "Trump was the swing driver, not the data: Monday he floated an Iran deal 'in two or three days' (stocks up, Brent -3%); today he said the US is 'going to be attacking them very hard' and would hit Iran the same day. Equities fell — S&P -0.37%, Nasdaq -0.42%, Dow -0.78% — Brent held ~$91.4. Headlines, not fundamentals, moved the tape.",
        "Two catalysts left in the window: Oracle after the close ($553bn AI backlog vs the capex bill) and the ECB +25bp tomorrow. We held the whole book; the rates trades just got cheaper to be right.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "The market trusts the soft core; the front end relaxes",
         "body": "The soft 2.9% core is taken as the signal — energy is a one-off shock, not breadth — the 2-year "
                 "breaks under 4.05%, the year-end hike prices out, Oracle's backlog clears and the strikes cool. "
                 "Risk up · rates down · dollar soft · gold firm."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "Hot headline vs soft core stand-off; oil keeps its premium",
         "body": "The market splits the difference: the 10Y holds ~4.5%, the front-end drifts lower on the core but "
                 "won't commit before the dot plot, the Strait stays shut so Brent holds $88-95, and Europe leads on "
                 "the ECB hike. Risk mixed · rates range-to-lower · dollar firm."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "The strikes escalate or core re-accelerates next month",
         "body": "Iran-Israel re-escalate and oil pushes toward $100, feeding the next headline and threatening to "
                 "drag the core up too, or Oracle's capex bill spooks the AI cohort into another de-rating. "
                 "Risk down · rates up · dollar up · gold higher as the stagflation scare bites."},
    ],

    "insights_layers": """
<p>Build the picture forward from where we left it on 9 June, when the only question that mattered was what CPI
would do to a tape already rattled by the truce breaking. Now we know, and the print cut both ways. Headline May
CPI ran to 4.2% (+0.5% m/m) — the hottest since April 2023 and a third straight acceleration — but the core came
in soft at +0.2% m/m and 2.9%, below the 0.3% consensus (BLS). The single most useful fact in the last 24 hours
is that the inflation is <em>energy, not breadth</em>: the Iran shock pushed the energy index up about 23.5%
year-on-year and energy alone drove over 60% of the monthly increase, while the core — the part the Fed targets
— stayed contained. A hot headline that the Fed can look through is not the same animal as a hot core, and the
distinction is the trade.</p>

<p>The tell of the day is that two markets read the same number differently. The bond market sided with the
core: the US 10-year eased to ~4.52% off a 4.55% intraday high, taking the soft core as evidence the energy
shock has not yet leaked into broad prices (Trading Economics). Equities sided with the geopolitics: the
S&amp;P fell 0.37%, the Nasdaq 0.42% and the Dow 0.78% as the US and Iran traded fresh military strikes
(TheStreet), with tech, industrials and discretionary leading lower. That divergence is the gap that matters —
ground truth is an energy-led headline and a Strait of Hormuz still effectively shut; what's priced in rates is
relief and what's priced in equities is risk; the right resolution is that the core wins the rates call and the
war keeps the oil premium, which is exactly how the book is positioned.</p>

<p>Go around the world and the same divergence repeats with a regional accent. <strong>Asia</strong> is where the
quietest but most important single-name signal sits: the AI-memory supply chain ran hot overnight — Korea's
HBM names (SK Hynix, Samsung) are the spine of every hyperscaler accelerator, and any headline on who is buying
whose high-bandwidth memory moves the whole semis complex before the US wakes up. KOSPI and the SOX track each
other tick-for-tick now; this is one market, not two, and the read is set in Seoul and Taipei first. <strong>Japan</strong>
carries the other live wire: USD/JPY at ~160 with the MoF openly threatening intervention and a BoJ September
hike creeping into the price — the Nikkei is hostage to the yen, and a carry unwind there would be a global
risk event, not a local one. <strong>Europe and the UK</strong> have decoupled outright: the DAX is a
financials-and-industrials index with no AI multiple to give back, it hikes into an ECB that goes Thursday, and
Bund and Gilt yields rose (+4bp, +7bp) while the US 10Y eased — the next rates impulse is European, not American.</p>

<p>The politics are the constraint behind every one of those moves, and this is where consensus is lazy.
The market is treating the ceasefire as a diplomatic process; it is a domestic-politics problem, and right now
it is being run on a wire. <strong>Trump is the single biggest intraday market-mover in this tape.</strong> On
Monday he said an Iran deal was in its "final stages" and could land "in two or three days" — stocks rallied,
Brent fell ~3%. By today he had flipped to "we're going to be attacking them very hard," promising to hit Iran
the same day after it downed a US Apache in the Strait, with a Truth Social post dismissing Iran's military as
"a complete and total mess." Same President, opposite tape, 24 hours apart. <strong>Netanyahu will not sign
anything he can frame as a concession</strong> before his coalition is safe, and Trump wants both the
"dealmaker" headline and the "we hit them hard" headline — which is precisely why the truce keeps breaking on
the seam (Lebanon) neither will own. The non-consensus read: the path of least resistance is not peace and not
all-out war but a managed, on-again-off-again conflict run by headline — so the trade is not to bet on the
outcome but to own the convexity (cheap vol, the oil tail) and treat each Trump deal-or-strike line as noise
around a Hormuz premium that stays bid for months. The market keeps pricing a binary; the politics deliver a
grind punctuated by headlines. In Europe, the
ECB can hike, but the German fiscal-political backdrop means a hawkish Lagarde will be framed at home as a
growth error before the autumn regional votes — the constraint is the trade. And next week Kevin Warsh chairs
his first FOMC: a brand-new chair cannot afford to look soft on inflation in week one, so the risk into the dot
plot is skewed hawkish regardless of what one CPI print says — the market's "he'll be dovish" lean is the
mispricing.</p>

<p>Net it out on the priced-versus-not spectrum, post-print. Under-priced: the chance the strikes escalate from
here — implied vol stayed calm through the CPI, so the geopolitical convexity is still cheap to own. Also
under-priced, more subtly: that a soft core lets the Fed hold even with a 4-handle headline, which the front end
has only half-believed. Fairly priced: oil's premium, earned by the blockade. Fully priced: tomorrow's ECB hike,
and most of the year-end Fed-hike fear the 2-year still carries — which is why the short-2Y and the steepener
just got the cheaper, better entry the soft core handed them. The disciplined posture is unchanged: own both
tails — the oil longs earned by a shut Strait, the rates trades now with a real tailwind — let Oracle and the
ECB come to us, and add nothing new in front of next week's dot plot.</p>
""",

    "wrap": """
<p>May CPI landed and split the tape. Headline ran hot to 4.2% (+0.5% m/m), the hottest since April 2023, but
the core was soft — +0.2% m/m, 2.9% y/y, under the 0.3% consensus (BLS). The inflation is energy: the Iran
shock lifted the energy index ~23.5% y/y and energy drove over 60% of the monthly rise, while the core stayed
contained.</p>

<p>Two markets, two readings. The 10-year eased to ~4.52% as the bond market took the soft core as relief; the
S&amp;P (-0.37%), Nasdaq (-0.42%) and Dow (-0.78%) fell as the US and Iran traded fresh strikes. Brent holds
~$91.4 — the Strait of Hormuz is still effectively shut and the war premium is earned.</p>

<p><strong>The driver.</strong> A hot energy-led headline the Fed can look through, against a contained core
the rates market believes. That is a softer rates picture than the 2-year priced, and a still-live geopolitical
tail in oil.</p>

<p><strong>So what to do.</strong> Hold the book that owns both tails — the soft core just handed the short-2Y
and the steepener a better entry, the oil longs are earned by the blockade — let Oracle (tonight) and the ECB
(tomorrow) come to us, and keep the hedge on into next week's dot plot.</p>
""",

    "correlation_regime": """
<p><strong>1. The chip rebound de-correlated from the de-escalation headline — relief that lasted one day.</strong>
Monday the semis ripped 6% on Iran's halt; the next session they gave it back. The "good news" and the price
decoupled within 24 hours. Don't trade the headline; trade the blockade.</p>

<p><strong>2. US yields fell while Bund and Gilt yields rose — a transatlantic rates split.</strong> The US 10Y
eased; Bund (+4bp) and Gilt (+7bp) rose as the market prices Thursday's ECB hike. The next rates impulse is
European, not American.</p>

<p><strong>3. Brent held its premium while equities tried to price peace.</strong> Oil near $92 with a blockaded
Strait is the most honest price on the screen. Until the Strait reopens, the geopolitical tail is on.</p>
""",

    "vol_skew": """
<p><strong>The VIX stayed in the high-teens through a hot CPI headline and fresh strikes — that is the mispricing.</strong>
VIX9D ~16 · VIX ~19 · VIX3M ~20 · VIX6M ~21. The tell: implied vol didn't budge on either the print or the
US-Iran strikes, so the front of the curve is underpricing the chance the war re-ignites before the ECB/FOMC
window closes. Owning cheap geopolitical convexity is the trade.</p>
""",

    "sector_rv": """
<p><strong>Leading:</strong> Energy producers (Brent premium held) and mega-cap defensives / Dow (rotation
toward quality, away from AI cohort). <strong>Lagging:</strong> AI semiconductors (dominant laggard — failed
Monday's bounce) and rate-proxy defensives (capped by a long end that has not eased).</p>

<p><strong>RV:</strong> Long DAX / short Nasdaq (MM-2026-010) pressured to its stop at ratio ~0.949 vs 0.943
stop. Structural case intact — ECB hikes into a financials-heavy index — but the single-cohort bounce is exactly
the tape that hurts it. One more down session forces the stop.</p>
""",

    "positioning": """
<p><strong>The crowded short just got squeezed by the soft core.</strong> Front-end rates: consensus chased the
year-end hike after the strong payroll; the 2-year sitting up near a 16-month high was the crowded position, and
a soft 2.9% core is exactly the catalyst that starts to squeeze it — the 10Y already eased to ~4.52%. Oil specs
never capitulated on the truce headlines — constructive for the longs. Euro: specs sit long into tomorrow's ECB
— a buy-the-rumour-sell-the-fact setup if Lagarde leans 'data-dependent pause.'</p>
""",

    "funding": """
<p>SOFR near 3.62% — unchanged. The plumbing did not move even as the war re-ignited. <strong>The Pozsar
mechanic:</strong> the 2-year's implied terminal rate sits well above secured funding; every floating-rate
borrower that issued in 2023-24 expecting cuts is still paying a higher cost than its model assumed. The soft
core nudges that terminal rate lower at the margin — watch IG spreads, where the balance sheet shows relief or
strain before the index does.</p>
""",

    "tape_missing": """
<p><strong>1. The market is treating an energy headline like a core problem.</strong> CPI's 4.2% is ~60%+
energy; the core printed 2.9% and undershot. If the next month's energy base effect fades, the headline rolls
over fast — the front end is still too short.</p>

<p><strong>2. Oracle's $553bn backlog meets the capex bill, not just the whisper.</strong> The stock is -12.9%
on the week into the print; the real question is whether converting the backlog needs ~$80bn of capex before
free cash flow turns positive. Watch the capex guide, not the EPS.</p>

<p><strong>3. The geopolitical convexity is still cheap.</strong> Implied vol stayed calm through CPI even as
US-Iran strikes resumed. Own the tail while the Strait is shut.</p>
""",

    "consensus": """
<p><strong>Consensus BID:</strong> a 4.2% headline is a hawkish print — it keeps the year-end hike alive, the
Fed can't ease into a 4-handle, and the energy shock risks bleeding into the core next.</p>

<p><strong>The strongest argument against — the OFFER:</strong> the core <em>undershot</em> at +0.2% / 2.9%, the
headline is ~60% energy the Fed routinely looks through, and the 10Y eased on the print. The hawkish read is
fighting the bond market's own verdict — the front end is mispriced for a hike that a contained core doesn't
justify.</p>
""",

    "one_chart": """
<p class="theme">The core, not the headline — +0.2% m/m says the Fed isn't forced to hike.</p>
<p>The single most informative number today is the one under the scary headline. A 4.2% print sounds hawkish
until you see the core came in at +0.2% m/m and 2.9% y/y, below consensus, with energy doing over 60% of the
work. The bond market got it — the 10Y eased to ~4.52%. Watch the 2-year: if it follows the 10Y lower and breaks
under ~4.05%, the year-end-hike pricing unwinds and the short-2Y / steepener pay off; if energy keeps climbing
and drags the core up next month, that's the bear case.</p>
""",

    "catalyst_calendar": [
        {"day": "Wed", "date": "Jun 10 ✓",
         "event": "US May CPI — PRINTED: 4.2% headline, 2.9% core",
         "consensus": "Headline +0.5% m/m / 4.2% y/y (highest since Apr-23); core +0.2% m/m / 2.9%, BELOW the 0.3% forecast. Energy ~60% of the rise (BLS).",
         "view": ("Hot headline, soft core — the inflation is energy, not breadth, and the Fed can look through it. "
                  "The 10Y eased to ~4.52%; the soft core hands the short-2Y (MM-013) and steepener (MM-009) a better entry."),
         "asymmetry": "Done: core undershoot = front-end relief; risk now is energy dragging the core up next month",
         "dir": "down"},
        {"day": "Wed", "date": "Jun 10",
         "event": "Oracle (ORCL) Q4 FY26 — after close (tonight)",
         "consensus": "Finnhub EPS $1.58 vs Oracle's March guide $1.96-2.00; OCI +84% prior Q; RPO $553bn.",
         "view": "The next read on the AI-capex multiple after Broadcom. The backlog is the bull case; the test is whether OCI growth clears the whisper.",
         "asymmetry": "Guide clears whisper: cohort re-rates +; merely-good guide: de-rating resumes",
         "dir": "flat"},
        {"day": "Thu", "date": "Jun 11",
         "event": "ECB rate decision — +25bp (99% priced)",
         "consensus": "+25bp confirmed; press conference neutral-to-hawkish.",
         "view": "'Data-dependent pause' = EUR sell-the-fact, MM-2026-012 accelerates. 'Further hikes' = EUR spike then fade.",
         "asymmetry": "Pause signal: EUR/USD -0.8%; hawkish: EUR +0.4% spike then fade",
         "dir": "down"},
        {"day": "Thu", "date": "Jun 11",
         "event": "Adobe (ADBE) Q2 — after close",
         "consensus": "Consensus EPS ~$5.94; near 52-week lows; split sell-side.",
         "view": "Cleanest test of whether generative-AI is a tax or a tailwind for software incumbents. Hold, do not chase.",
         "asymmetry": "AI additive to ARR: software relief; cannibalisation read: another leg down",
         "dir": "flat"},
        {"day": "Tue-Wed", "date": "Jun 16-17",
         "event": "FOMC + dot plot — Warsh's first meeting, no cut priced",
         "consensus": ">80% hold in June; March median one cut; the dots are the whole event.",
         "view": "A new chair who cannot look soft on inflation in his first meeting. Zero-cut median: 2Y +10bp, gold sells. One-cut held: 2Y -15bp, gold +2%.",
         "asymmetry": "0-cut dots: DXY +0.7%, 2Y +10bp; 1-cut held: 2Y -15bp, gold +2%",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660 after Thursday's ECB press conference. At ~1.636; stop 1.662.</li>
<li><strong>MM-2026-002 · Long Brent:</strong> exit on a weekly close below $87 — the war premium gone. At ~$91.</li>
<li><strong>MM-2026-003 · Long Brent/Short WTI spread:</strong> discretionary close below $2.00. At ~$3.26. Stop 1.50.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop at 4.65%. At ~4.52%, eased on the soft CPI core. Working; let it run into the dot plot, do not add.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~July 15. Stop $4,250; at ~$4,200 (stop touched, held by min_hold rule).</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160.1.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> hold through CPI, ECB and dot plot.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to July 16. At +40bp; target +60bp. Hold.</li>
<li><strong>MM-2026-010 · Long DAX / short Nasdaq:</strong> stop ratio 0.943; at ~0.949. Hold to the line.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. Base case sell-the-fact on a fully-priced hike.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold 30 days. Wait on CPI.</li>
</ul>
""",

    "client_ammo": [
        {"q": "Trump said a deal was days away, then said he'd hit Iran hard — what do I believe?",
         "a": ("Believe the oil price, not the President. He floated a deal 'in two or three days' on Monday and "
               "flipped to 'attacking them very hard' today, and the tape whipsawed on each line — but Brent still "
               "sits ~$91.4 with the Strait shut. The crude market is pricing the physical fact, not the headline. "
               "We trade the premium and treat the deal-or-strike soundbites as noise; we held the whole book "
               "rather than chase either one.")},
        {"q": "Then why are you still long oil if the war is ending?",
         "a": ("Because the price says it isn't ending — not yet. We marked Brent live to ~$91 and the Brent/WTI "
               "spread to ~$3.26. The premium is intact. The exit is a weekly close below $87. You do not sell the "
               "fire insurance the hour the fire is contained but still smoking.")},
        {"q": "What should I actually watch from here?",
         "a": ("The 2-year and Oracle. CPI is behind us and the core undershot, so watch whether the 2-year follows "
               "the 10Y down through ~4.05% — that's the year-end hike pricing out and our rates trades paying. "
               "Then Oracle after the close: not the EPS, the capex guide — whether that $553bn AI backlog converts "
               "without blowing out the model. Tomorrow it's the ECB.")},
    ],

    "ideas_note": (
        "<p>No new idea today — and that is the call. CPI is out and it broke our way on the core, so the right move "
        "is not a fresh trade but to let the existing rates pre-positions (short 2Y, the steepener) run on the "
        "better-priced entry the soft core just handed them. With Oracle tonight and the ECB tomorrow, adding new "
        "risk in front of two live catalysts is the opposite of edge.</p>"
    ),

    "event_radar_note": (
        "<p>With CPI behind us (hot headline, soft core), two live catalysts remain in the window plus next week's "
        "Fed: Oracle after tonight's close (the $553bn AI backlog vs the capex bill), the ECB tomorrow (+25bp "
        "locked; the press conference sets the euro), and Kevin Warsh's first FOMC dot plot on June 16-17.</p>"
    ),

    "burry_tell": (
        "Hyperscaler capex is now so large that the marginal AI-revenue beat has to <em>accelerate</em> just to "
        "hold the multiple. Broadcom grew AI revenue 143% and still lost a seventh of its market cap, because the "
        "whole cohort is hedged for a miss and not one name is hedged for a growth-rate <em>disappointment</em>. "
        "Oracle reports tonight into that exact trap with a $553bn backlog. The structural point nobody is pricing: "
        "the AI trade has quietly become a second-derivative trade — it is no longer enough to grow fast, you have "
        "to grow faster than last quarter — and that is the regime in which a cohort de-rates without a single bad "
        "print, just a string of merely-very-good ones."
    ),

    "earnings_summary": (
        "Three names in the window, all NEUTRAL — we are not pre-positioning into any of them. Oracle (tonight) is "
        "the next read on whether the AI-capex multiple holds after Broadcom; Adobe (Thu) is the cleanest test of "
        "whether generative-AI is a tax or a tailwind for software incumbents; SailPoint (reported) is a small-cap "
        "tell on whether security spend is still defensive. The trade is the read, not the position."
    ),
    "earnings_why": (
        "These three cleared the universe filter — $10bn+ cap, US/Korea, Tech/Financials/Industrials/Utilities, "
        "reporting inside the 5-day-pre / 3-day-post window — and nothing else in the universe qualified this run. "
        "Oracle and Adobe are the two software/cloud prints that bracket the AI-capex debate the macro book is "
        "built around; SailPoint is the early-bird identity-security read. Consensus EPS, recommendation splits and "
        "growth metrics are Finnhub-sourced (earnings_data.md); the implied-move and positioning fields are "
        "supplemented by web search and tagged estimated."
    ),

    "book_aim": (
        "Carry a barbell that is paid on either resolution of the oil binary and waits on CPI for the rates trades — "
        "long the Hormuz tail (Brent outright + call spread + Brent/WTI), short the over-extrapolated front end "
        "(2Y, 2s10s steepener), a cross-region RV (long DAX / short Nasdaq) and a defined-risk SPX hedge, with gold "
        "as the two-tailed anchor. The aim at this point in June is to be flat-to-up into the 16-17 Jun FOMC without "
        "taking directional CPI risk, and to let the structural pre-positions (steepener, gold) do the compounding."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the two option lines are "
                 "model estimates from spot.")
    },
    "idea_selection": [
        {"label": "No new idea today", "in": False,
         "text": ("CPI is out and the core broke our way, so the edge is in letting the existing rates trades run on "
                  "the better entry, not in forcing a fresh one in front of Oracle tonight and the ECB tomorrow. "
                  "We marked the whole book to live levels — that is information, not an entry.")},
        {"label": "Brent longs (MM-002/003/011)", "in": True,
         "text": ("kept, not added — earned by a Strait that is still shut. These are the trades the book is "
                  "expressing the geopolitical tail through; the RSI screener and the oil tape both still support "
                  "carrying them. Exit is a weekly Brent close below $87.")},
        {"label": "2s10s steepener (MM-009) + short 2Y (MM-013)", "in": True,
         "text": ("held as the structural rates pre-position — the front end is over-extrapolating one payroll, and "
                  "the dot plot on 16-17 Jun is the catalyst. Min-hold rules keep these on through the noise.")},
        {"label": "Long DAX / short Nasdaq (MM-010)", "in": False,
         "text": ("flagged but NOT added to today — it sits on its 0.943 stop and the narrow chip-led bounce is "
                  "exactly the tape that hurts it. Structural case intact; we do not add while US tech leads.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

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
