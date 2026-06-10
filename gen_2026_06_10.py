#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-10 (Wednesday).

May CPI day. The big number lands at 8:30 ET. Iran/Israel truce still fragile;
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
        book.log(f"  {tid} RSI={r['rsi']}  SD={r['sd_dist']:+.2f}  {r['verdict']}")

book.step("Computing idea RSI + valuation data (Yahoo Finance)")
idea_rsi_data = fetch_rsi.fetch_all_ideas()
for ik, r in idea_rsi_data.items():
    if r.get("error"):
        book.log(f"  idea {ik}: {r['error']}")
    elif r.get("rsi") is not None:
        val = r.get("valuation") or {}
        pe_str = f"  P/E={val.get('trailing_pe_fmt','N/A')}" if not val.get("error") else ""
        book.log(f"  idea {ik} RSI={r['rsi']}  SD={r['sd_dist']:+.2f}  {r['verdict']}{pe_str}")

# ── Regime ─────────────────────────────────────────────────────────────────────
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
    "MM-2026-004": "Offside. The 10Y sat at ~4.55%, barely moved by the ceasefire — the disinflation impulse the trade needs has not arrived. Stop 4.65%, ~10bp away. CPI today is the binary. Do not add.",
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
        "The truce keeps cracking and the Strait stays shut, so oil keeps its premium near $92 — while the "
        "one-day chip bounce on Monday's brief halt has already failed. Two unresolved shocks, the war and a "
        "CPI print expected to tick up to 4.2%, both still live into this morning."
    ),

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

<p>Into that sits the hard catalyst the geopolitics cannot soften: <strong>May CPI this morning at 8:30</strong>,
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
        "Rates haven't moved: 2Y ~4.15%, 10Y ~4.55%, 2s10s +40bp. So today's CPI is effectively unhedged.",
        "May CPI today (8:30 ET) is the binary — expected to tick up to ~4.2% headline. We held the whole book to live levels; no new risk into the print.",
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

    "insights_layers": """
<p>A ceasefire is only as good as its last 24 hours, and this one's last 24 hours were strikes. The April truce
between Iran and Israel cracked over the weekend in the worst exchange of fire in months; Iran announced a halt
on Monday, and Israel answered it with an extensive strike on Iranian air defences and the Mahshahr
petrochemical complex. Netanyahu has pointedly declined to call it a ceasefire; Iran says it will fire again if
Israel keeps hitting Lebanon. So the screen you are reading is not pricing peace — it is pricing a truce that
has already failed once and could fail again before the week is out.</p>

<p><strong>Layer 1 — the regime.</strong> Two shocks, both still live: a war that keeps re-igniting and a CPI
print landing this morning. Neither has resolved. The truce is unsigned and already broken once; the inflation
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
it just lost money. The gap is between a geopolitics that is still hot and an equity tape that wanted it cold.</p>

<p><strong>Layer 4 — Bull / Base / Bear.</strong> <em>Bull (30%):</em> CPI cools to ≤3.9%, the halt holds, the
Strait reopens and crude bleeds the premium — risk up, rates down, gold firm. <em>Base (45%):</em> CPI ticks
up to ~4.0-4.2%, the truce stays fragile and the Strait stays shut so oil holds its bid, Europe leads into the
ECB — risk mixed, rates range, dollar firm. <em>Bear (25%):</em> CPI runs hot (>4.3%) or the strikes resume
with Lebanon the fuse and oil pushes $100, and the AI de-rating resumes on a weak Oracle — risk down, rates up,
gold higher. The bear tail is fatter than it was: there are two ways to lose this week.</p>

<p><strong>Layer 5 — priced vs not-priced.</strong> Mispriced the wrong way: any residual hope that Monday's
halt was the end of it. Under-priced: the chance the strikes resume — implied vol eased even as the truce broke.
Fairly priced: oil's premium. Fully priced: Thursday's ECB hike. Own the geopolitical convexity cheaply while
the tape is still treating the war as yesterday's story.</p>

<p><strong>The Burry tell.</strong> Hyperscaler capex is now so large that the marginal AI-revenue beat has to
accelerate just to hold the multiple; Broadcom grew AI 143% and lost a seventh of its cap because the cohort
is hedged for a miss and not one name is hedged for a growth-rate disappointment. Oracle reports tonight with
a $553bn backlog into that exact trap.</p>
""",

    "wrap": """
<p>A ceasefire is only as good as its last 24 hours, and this one's were strikes. The April Iran-Israel truce
cracked over the weekend; Iran announced a halt on Monday and Israel answered with a strike on its air defences
and the Mahshahr petrochemical complex. Netanyahu won't call it a ceasefire; Iran says it will fire again if
Israel keeps hitting Lebanon. This is a truce under fire, not a peace.</p>

<p>The equity tape had one day of believing it and took the day back. Monday's chip rip — semis +6%, Micron
+10% — failed the next session: the S&amp;P closed 7,386.65 (-0.26%), the Nasdaq -0.97%, only the Dow holding.
The dominant story is still the AI de-rating, not a relief rally.</p>

<p><strong>The driver.</strong> Two live shocks — a war that keeps re-igniting and May CPI this morning — and
neither has resolved. Oil holds near $92 because the Strait of Hormuz is still under a dual US-Iran blockade.
Rates haven't moved: the 2-year sits ~4.15%, the year-end hike still priced.</p>

<p><strong>So what to do.</strong> Hold the book that owns both tails, let the oil longs run, wait on CPI for
the rates trades, and keep the hedge on.</p>
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
<p><strong>The VIX eased into the high-teens even as the truce broke — that is the mispricing.</strong>
VIX9D ~16 · VIX ~19 · VIX3M ~20 · VIX6M ~21. The tell: implied vol relaxed while strikes resumed, so the
front of the curve is underpricing the chance the war re-ignites before the CPI/ECB/FOMC window closes.
Owning cheap geopolitical convexity is the trade.</p>
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
<p><strong>The crowd is long the truce in equities and short it in oil — and oil is winning.</strong>
Oil specs did not capitulate when Iran halted — constructive for the longs. Front-end rates: consensus chased
the year-end hike after payrolls; the 2-year at 4.15% is the crowded position a soft CPI would squeeze.
Euro: specs sit long into Thursday's ECB — sell-the-fact setup if 'data-dependent pause' is the signal.</p>
""",

    "funding": """
<p>SOFR near 3.62% — unchanged. The plumbing did not move even as the war re-ignited. <strong>The Pozsar
mechanic:</strong> the 2-year's implied terminal rate sits well above secured funding; every floating-rate
borrower that issued in 2023-24 expecting cuts is still paying a higher cost than its model assumed. Watch IG
spreads on today's CPI print — the balance sheet shows the strain before the index does.</p>
""",

    "tape_missing": """
<p><strong>1. The Strait of Hormuz is still blockaded.</strong> Implied vol eased even as strikes resumed.
Own the convexity while it's cheap.</p>

<p><strong>2. Oracle's $553bn backlog meets the same bar Broadcom failed.</strong> If the guide disappoints the
whisper, the de-rating that drove this week resumes. Watch the guide, not the EPS.</p>

<p><strong>3. Today's CPI is effectively unhedged.</strong> The 2-year at ~4.15% and the year-end hike is
priced; a number above 4.3% re-arms the hike.</p>
""",

    "consensus": """
<p><strong>Consensus BID:</strong> the worst of the war is behind us — Iran halted, Trump gets his ceasefire,
oil drifts lower, CPI lands manageable, AI cohort stabilises, Warsh holds next week.</p>

<p><strong>The strongest argument against — the OFFER:</strong> the ceasefire already broke once this week and
Israel struck Iran's petrochemical complex after Iran's "halt." And today's CPI: headline at 3.8% in April on
energy, consensus ~4.2% in May. A print above 4.3% re-arms the hike.</p>
""",

    "one_chart": """
<p class="theme">Brent crude near $92 — and the Strait of Hormuz that keeps it there.</p>
<p>The single most informative price is the one the failed chip bounce couldn't shake. Brent eased a couple of
dollars off $94 when Iran halted, then stuck — because the Strait of Hormuz is still under a dual US-Iran
blockade and the truce keeps cracking. That premium is earned, not a fading scare. Hold above $90 and the
geopolitical tail is live; the trigger is a weekly close below $87. Watch the Strait, and watch the 2-year
~4.15% for whether today's CPI lets the front-end move at all.</p>
""",

    "catalyst_calendar": [
        {"day": "Wed", "date": "Jun 10",
         "event": "US May CPI (BLS, 8:30 ET) — the deciding print",
         "consensus": "Headline ~3.8% YoY; core ~2.8-3.3%. Cleveland Fed nowcast nearer 4.0%.",
         "view": ("The single binary of the week. At/below 3.7%: the 2-year breaks under 4.05%, the hike prices "
                  "out, MM-2026-013/009 finally get their move, gold bids. Above 4.1%: the hike re-arms."),
         "asymmetry": "<3.7%: 2Y -15bp, gold +2%; >4.1%: 2Y +15-20bp, DXY +0.5%, gold -2%",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 10",
         "event": "Oracle (ORCL) Q4 FY26 — after close",
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
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop at 4.65%. At ~4.53%. CPI today is the binary. Do not add.</li>
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
        {"q": "The ceasefire is here — is the all-clear real?",
         "a": ("Look at oil before you answer. A genuine end hands back the war premium, and Brent gave back exactly "
               "one dollar to ~$93. The crude market is telling you it does not trust the truce. We held the whole "
               "book rather than chase it.")},
        {"q": "Then why are you still long oil if the war is ending?",
         "a": ("Because the price says it isn't ending — not yet. We marked Brent live to ~$91 and the Brent/WTI "
               "spread to ~$3.26. The premium is intact. The exit is a weekly close below $87. You do not sell the "
               "fire insurance the hour the fire is contained but still smoking.")},
        {"q": "What should I actually watch today?",
         "a": ("Two prints. May CPI at 8:30 — below 3.7% prices the year-end hike out and the front-end relaxes; "
               "above 4.1% re-arms it. Then Oracle after the close — the next read on whether the market will pay "
               "up for AI-capex names after Broadcom. The 2-year at 4.15% carries the first answer; Oracle's guide "
               "carries the second.")},
    ],

    "ideas_note": (
        "<p>No new idea today — and that is the call. We marked the entire book to live levels and found a tape "
        "that refused to move on a ceasefire. With May CPI at 8:30, the highest-expected-value action is to add "
        "nothing. Forcing a trade into a binary is the opposite of edge.</p>"
    ),

    "event_radar_note": (
        "<p>Three binary events inside the next eight sessions resolve every open position's thesis: May CPI "
        "this morning (the deciding print on the year-end hike), ECB Thursday (+25bp locked; press conference "
        "sets the euro), and Kevin Warsh's first FOMC dot plot on June 16-17.</p>"
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
