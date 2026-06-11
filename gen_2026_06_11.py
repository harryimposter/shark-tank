#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-11 (Thursday).

CRITICAL CORRECTIONS vs prior run:
- May PPI (BLS Jun 11) is HOT, NOT soft: Final-demand +1.1% MoM, +6.5% YoY
  (largest 12-month rise since Nov 2022). Stage-1 intermediate demand +12.3% YoY.
  Source: bls.gov/news.release/archives/ppi_06112026.htm + Trading Economics.
  This SUPPORTS hawkish Fed read — remove all "soft PPI / reduces hawkish-surprise" framing.

NEW NEWS (all June 11 2026, verified):
- Trump threatened to SEIZE Kharg Island (~90% of Iran's crude exports), vowed a
  3rd consecutive night of strikes on Iran. (Bloomberg, Axios, CNBC)
- UAE and Iran held first face-to-face meeting since the war began (de-escalation). (Bloomberg, Al Jazeera)
- SpaceX IPO priced $135/share, ~$1.77T valuation, 555.6M shares (~$75B raise),
  Nasdaq debut JUNE 12 under ticker SPCX, Goldman lead — biggest IPO ever. (CNBC)
- ECB decision: CONFIRMED DONE Jun 11 — hiked +25bp to 2.25%, first hike in ~3 years.
  Explicitly cited Iran-war-driven inflation (euro-area CPI 3.2% May, above 2% target).
  Lagarde: upside risks to inflation, downside risks to growth, "not pre-committing to a
  particular rate path." Sources: CNBC, Bloomberg, Reuters, FXStreet (4 sources agree).
  Sell-the-fact dynamic confirmed: EUR/USD fading from ~1.15 post-delivery.

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
regime = "Hot PPI +6.5% YoY; ECB Hiked to 2.25%; Kharg Island Seizure Threat; SpaceX IPO Tomorrow"
regime_note = (
    "Four themes collide on June 11. First: May PPI came in HOT — final-demand producer prices +1.1% MoM and "
    "+6.5% YoY (BLS, the largest 12-month rise since November 2022). Stage-1 intermediate demand surged +12.3% "
    "YoY, meaning the pipeline is re-accelerating. This is explicitly hawkish for the Fed: Warsh cannot look "
    "dovish into a FOMC with CPI headline at 4.2% AND PPI at +6.5%. The rates pre-positions (short 2Y, steepener) "
    "are now facing a genuine headwind — the PPI print re-arms the hike-pricing that the soft core CPI had "
    "temporarily defused. "
    "Second, the geopolitical situation escalated sharply: Trump vowed a THIRD consecutive night of strikes on "
    "Iran and — in a significant escalation beyond anything in Day 1 or Day 2 — threatened to SEIZE Kharg Island, "
    "Iran's primary oil export terminal handling roughly 90% of Iran's crude exports. A seizure would remove "
    "~2.5-3M bbl/day from world markets at a stroke. Even as a threat, this is the most oil-bullish single "
    "statement since the war began. Brent is moving toward $95-100. The Brent $100 call spread (MM-011) is now "
    "close to in the money. "
    "Counterweight: the UAE and Iran held their first face-to-face meeting since hostilities began — a "
    "de-escalation signal that prevents the market from pricing a straight-line escalation. The two-sided "
    "tension (Trump threatening Kharg vs UAE-Iran talking) is the correct frame: managed conflict, not total war. "
    "Third, Oracle's capex panic from last night continues to weigh on AI semis: OCI +93%, RPO $638bn, revenue "
    "$19.2bn — but the $55.7bn FY26 capex and $70bn+ FY27 commitment funded by a $40bn raise is the equity-"
    "structure shock. "
    "Fourth and finally: SpaceX priced its IPO last night at $135/share with a ~$1.77T valuation, raising ~$75bn, "
    "the largest IPO in history. It debuts on Nasdaq tomorrow (Jun 12) under ticker SPCX, with Goldman as lead. "
    "The liquidity drag — $75bn in capital committed to a single new issue — is a cross-market event. "
    "The ECB DELIVERED the +25bp hike to 2.25% today (Jun 11) — its first hike in nearly three years. "
    "The Bank explicitly cited Iran-war-driven inflation as the rationale, with euro-area CPI at 3.2% in May, "
    "above the 2% target. Lagarde flagged upside risks to inflation and downside risks to growth, and pointedly "
    "said the ECB is 'not pre-committing to a particular rate path' — the pause signal the sell-the-fact trade "
    "needed. EUR/USD has faded from ~1.15 post-delivery, confirming the MM-012 short-EUR thesis. "
    "FOMC June 16-17 is the terminal gate."
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
            "The ECB DELIVERED the +25bp hike to 2.25% today (Jun 11) — its first hike in nearly three "
            "years — and the sell-the-fact dynamic is confirmed. EUR was bid from 1.08 to ~1.15 as the "
            "market priced this hike cycle. Lagarde's press conference delivered exactly what the trade "
            "needed: 'not pre-committing to a particular rate path' — a pause signal that removes the "
            "marginal EUR buyer. EUR/USD fading post-delivery. Additionally, hot PPI (+6.5% YoY) adds a "
            "USD-broadly-supportive overlay: the Fed must stay restrictive, which is USD-positive. Dual "
            "tailwind confirmed. The AUD carries a terms-of-trade tailwind from firm iron ore (~$105/t). "
            "EURAUD drifting lower from 1.66 is consistent with the thesis."
        ),
        "catalysts": [
            "ECB Jun 11 decision — DONE: +25bp to 2.25% delivered. Lagarde: 'not pre-committing' = "
            "pause signal confirmed. Sell-the-fact unwind now active. EUR/USD fading from ~1.15.",
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
                            "a full-figure mispricing between a pause-signalling ECB and an RBA still "
                            "in tightening mode. Sell-the-fact confirmed post-delivery.",
            "catalyst":     "2/2 — ECB Jun 11 DELIVERED (+25bp, pause signal confirmed) and FOMC Jun 16-17 "
                            "are both near-dated, directly EUR-relevant events. Two dated catalysts in the window.",
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
            "The thesis just got a material upgrade. Trump vowed a THIRD consecutive night of strikes "
            "on Iran and — in the single most oil-bullish statement since hostilities began — threatened "
            "to SEIZE KHARG ISLAND, Iran's primary oil export terminal handling ~90% of Iran's crude "
            "exports (~2.5-3M bbl/day). A physical seizure would be the largest single supply shock in "
            "oil-market history. Even as a threat, this pushes Brent toward $95-100 and compresses the "
            "gap to the Bloomberg Intelligence $130/bbl July-August forecast. Counterweight: the UAE "
            "and Iran held their first face-to-face meeting since the war began — a de-escalation signal "
            "that prevents a straight-line spike. The framing: managed escalation with a dramatic "
            "right tail, not a ceasefire. Strait of Hormuz remains at ~15% pre-war traffic. SPR at "
            "multi-decade lows. May PPI +6.5% YoY confirms the inflation pipeline is accelerating — "
            "further support for an oil price that is both supply-constrained and re-inflating."
        ),
        "catalysts": [
            "Kharg Island seizure threat (Trump Jun 11) — if executed: removes ~90% of Iran's crude "
            "exports; Brent gaps to $110+. Even as threat: floor bid materially raised.",
            "Strait of Hormuz traffic (currently ~15% pre-war; any mine/tanker incident = $100+ gap)",
            "Iran-UAE talks (first face-to-face since war; any de-escalation deal = Strait premium collapses)",
            "Day-3 US strikes on Iran (vowed for tonight) — escalation confirms the tail risk",
            "OPEC+ emergency meeting (supply cut = price floor lifted)",
            "Weekly US crude inventory data (EIA Wednesdays); SPR drawdown trajectory",
        ],
        "risks": (
            "Iran-UAE diplomatic deal extends to Strait re-opening (premium collapses toward $84 support); "
            "Trump Kharg Island threat proves rhetorical without follow-through (headline fade); demand "
            "destruction from global recession fears; SPR release program accelerates; stop at weekly "
            "close below $87."
        ),
        "breakdown_why": {
            "gap":          "3/3 — Hormuz at 15% pre-war traffic, Kharg Island seizure threat now live; "
                            "the physical constraint is MORE severe than the price currently implies. "
                            "May PPI +6.5% YoY adds an inflation-pipeline overlay. Gap widened further today.",
            "catalyst":     "2/2 — Day-3 strikes vowed for tonight; Kharg Island seizure is a dated, "
                            "direct catalyst. Iran-UAE talks are the counterweight but not the resolution.",
            "positioning":  "1/2 — specs cut net length but not cleanly short; modest supportive lean.",
            "confirmation": "1/2 — Brent above $93 on day-three escalation; not yet a clean re-acceleration "
                            "above $95 to confirm. Kharg threat accelerates this.",
            "stop_quality": "1/1 — weekly close below $87 is a clean structural level; war premium gone.",
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
            "This position is now facing a genuine headwind and must be framed honestly. The original "
            "thesis rested on soft core CPI (May: 2.9%, below consensus) reducing the probability of "
            "a Fed hike. That signal was real and the 10Y eased to ~4.52%. But today's May PPI print "
            "(BLS) is HOT: final-demand PPI +1.1% MoM and +6.5% YoY — the largest 12-month rise since "
            "November 2022, with stage-1 intermediate demand at +12.3% YoY. The pipeline is re-accelerating. "
            "PPI leads CPI: a +6.5% producer price rise will not stay contained at the consumer level for "
            "long. Warsh now faces CPI at 4.2% headline AND PPI at +6.5% — he cannot look dovish in his "
            "first FOMC. The trade is not wrong yet (10Y at ~4.52% vs 4.44% entry = only ~8bp offside) "
            "but the narrative risk has shifted from 'soft landing' to 'stagflation'; the 10Y faces "
            "upward pressure from re-accelerating inflation expectations. The stop at 4.65% is now "
            "closer to relevant. Do not add. Monitor FOMC dot-plot signals carefully."
        ),
        "catalysts": [
            "May CPI Jun 10 DONE: 4.2% headline / 2.9% core (below 0.3% forecast) — soft core "
            "gave one-day relief; 10Y eased to ~4.52%",
            "May PPI Jun 11 HOT: +1.1% MoM / +6.5% YoY (BLS) — largest since Nov 2022; "
            "pipeline re-acceleration. This is a HEADWIND for the long-duration thesis.",
            "FOMC dot plot Jun 16-17 — zero-cut median AND hike signal = yield up, stop tested; "
            "data-dependent pause = yield falls 10-15bp. Warsh presser tone in the context of "
            "CPI 4.2% + PPI 6.5% is now MORE hawkish than previously framed.",
            "Treasury supply (June/July refunding — supply shock risk at the long end)",
            "June CPI (Jul 10) = if PPI pipeline feeds through to core, stop is tested",
        ],
        "risks": (
            "Warsh delivers explicitly hawkish FOMC (dot plot = hike bias; PPI print supports this); "
            "PPI-to-CPI pipeline accelerates core above 3.5% in June or July; fiscal supply shock "
            "at the long end; Kharg Island seizure + oil at $100 re-inflates inflation expectations. "
            "Stop at 4.65% (now ~4.52%, ~13bp away — closer than it looks given PPI + FOMC risk)."
        ),
        "breakdown_why": {
            "gap":          "1/3 — downgraded from 2: the soft core CPI is now offset by hot PPI "
                            "+6.5% YoY. The net inflation signal is ambiguous. The long-duration gap "
                            "thesis has narrowed materially.",
            "catalyst":     "1/2 — FOMC is still a dated catalyst but the PPI print makes the "
                            "hawkish scenario more likely; the trade can now go either way with higher "
                            "probability on the wrong side.",
            "positioning":  "1/2 — consensus is still long duration; no change.",
            "confirmation": "0/2 — no technical confirmation; yield has not broken lower from entry; "
                            "hot PPI adds to the headwind, not the thesis.",
            "stop_quality": "1/1 — 4.65% is still a clear technical level; ~13bp risk.",
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
            "Gold is now working on THREE engines, with one turning ambiguous. Engine 1 — "
            "geopolitical safe-haven: Trump threatened to SEIZE Kharg Island (Day-3 strikes vowed), "
            "the most aggressive oil escalation since hostilities began. Gulf states at risk; "
            "ceasefire 'meaningless.' The safe-haven bid is now STRONGER than yesterday. "
            "Engine 2 — inflation hedge: May PPI came in HOT at +6.5% YoY (BLS, Jun 11), the "
            "largest rise since November 2022. Accelerating producer prices feed into inflation "
            "expectations — a direct gold tailwind. Engine 3 — real rates (now AMBIGUOUS): the "
            "soft core CPI (2.9%) eased the 10Y to ~4.52%, reducing real-rate pressure. But hot "
            "PPI complicates this — if the inflation pipeline flows through, real rates could "
            "re-price higher and cap gold. Net: two engines (safe-haven + inflation hedge) are "
            "stronger than before; the real-rates engine is the risk. Stop touched Jun 10 "
            "($4,200 vs $4,250 stop) but min_hold 45d rule applies; position held; gold is "
            "recovering from the low."
        ),
        "catalysts": [
            "Kharg Island seizure threat (Jun 11) — strongest geopolitical bid yet; Brent toward $100 = "
            "stagflation premium + safe-haven bid reinforce each other",
            "US-Iran Day-3 strikes (vowed for tonight, Jun 11) — escalation confirms tail risk",
            "May PPI +6.5% YoY (BLS Jun 11) — hot producer prices = inflation-hedge thesis strengthened",
            "FOMC dot plot Jun 16-17 — hawkish dots = real yields up, gold capped; dovish pause = gold up",
            "EM central bank Q2 gold purchase data (China, India, Turkey structural buyers)",
        ],
        "risks": (
            "Warsh delivers hawkish FOMC with explicit hike bias (real yields surge sharply, gold sells "
            "despite geopolitics); Iran-UAE talks produce genuine de-escalation deal (geopolitical bid fades "
            "faster than PPI bid supports); gold-specific spec flush; strong DXY spike on FOMC. "
            "NOTE: Stop touched Jun 10 ($4,200 vs $4,250 stop) but min_hold 45d rule applies — "
            "position stays open."
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
            "This position must be re-marked for hot PPI. The original thesis: the 2Y at ~4.16% "
            "was over-extrapolating a single payroll print (172k, unchanged unemployment) and a "
            "hike was not justified. The soft core CPI (2.9% May) supported that view. However, "
            "today's May PPI (BLS, Jun 11) came in HOT: +1.1% MoM and +6.5% YoY — the largest "
            "12-month rise since November 2022. Stage-1 intermediate demand at +12.3% YoY. Hot "
            "PPI re-arms the market's hike pricing — the 2Y at ~4.11% is now at RISK of moving "
            "back toward 4.30-4.35% stop level. Warsh faces both headline CPI 4.2% and PPI 6.5%; "
            "he cannot signal a dovish tilt without being seen as reckless. The thesis is not "
            "broken (the 2Y was over-extrapolating a single payroll; that structural view stands) "
            "but the timing risk has increased materially. The FOMC catalyst is still the payoff "
            "gate, but the probability distribution has shifted toward a hawkish outcome. Minimum "
            "hold applies; do not add; respect the stop."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — if Warsh signals data-dependent pause: 2Y falls 15-20bp "
            "(trade works); if zero-cut dots with hike bias: 2Y rises to stop at 4.35%",
            "May CPI Jun 10 DONE: core 2.9% = modest support; now offset by hot PPI",
            "May PPI Jun 11 HOT: +6.5% YoY (BLS) — HEADWIND; re-arms hike pricing",
            "Initial jobless claims (any spike = Fed hiking case weakens; support for the trade)",
            "Kharg Island oil shock (Brent to $100+ = stagflation = hike risk rises = further headwind)",
        ],
        "risks": (
            "Hot PPI already partially re-prices the 2Y higher (stop at 4.35% closer than before); "
            "Warsh delivers explicitly hawkish dot plot at first FOMC (2Y +25bp, stop taken); "
            "oil shock from Kharg Island seizure re-inflates via the energy pipeline; "
            "stop at 4.35%; min_hold 30 days through Jun 16 FOMC."
        ),
        "breakdown_why": {
            "gap":          "1/3 — downgraded from 2: hot PPI +6.5% YoY means the Fed's 'inflation "
                            "is energy-driven, look-through' case is harder to make. The gap between "
                            "the 2Y yield and the justified hiking probability has narrowed.",
            "catalyst":     "2/2 — FOMC dot plot remains a precise, dated catalyst with direct "
                            "2Y transmission; still 2/2 but the directional probability has shifted.",
            "positioning":  "2/2 — market is still heavily short 2Y duration; squeeze fuel remains "
                            "if FOMC surprises dovishly.",
            "confirmation": "0/2 — no technical confirmation; yield has not broken lower; "
                            "hot PPI adds downside risk.",
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
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},   # unchanged; ECB delivered +25bp to 2.25% Jun 11
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
    "MM-2026-001": "ECB DELIVERED +25bp to 2.25% today (Jun 11) — first hike in ~3 years. Lagarde: 'not pre-committing to a particular rate path' = pause signal confirmed. EUR/USD fading from ~1.15 post-hike. Sell-the-fact underway. Hot PPI (+6.5% YoY) adds USD-broadly-supportive overlay. Dual tailwind confirmed. Stop 1.662.",
    "MM-2026-002": "UPGRADED — Day-3 strikes vowed by Trump tonight; Kharg Island seizure THREATENED (~90% of Iran's crude). Most oil-bullish single statement since the war began. Brent moving toward $95-100. Bloomberg $130/bbl Jul-Aug if Strait stays shut. Counterweight: UAE-Iran held first talks. Conviction holds at max. Exit on weekly close below $87.",
    "MM-2026-003": "Building strongly. Brent-WTI spread widens on Kharg Island escalation — Brent-specific supply shock is what this spread was designed for. Structural case confirmed Day 3. Stop $1.50.",
    "MM-2026-004": "HEADWIND — re-mark required. Hot PPI (+1.1% MoM / +6.5% YoY, BLS Jun 11 — largest since Nov 2022) counters the soft core CPI (2.9%) that had been supporting the thesis. Pipeline re-accelerating. Warsh cannot look dovish with CPI 4.2% AND PPI 6.5%. Position ~8bp offside (entry ~4.44%, current ~4.52%). Stop 4.65% is now closer. Do not add; FOMC Jun 16-17 is the terminal gate — if Warsh signals pause, trade recovers; if hawkish, stop is hit.",
    "MM-2026-005": "THREE engines running. Kharg Island seizure threat = geopolitical bid strongest yet. Hot PPI +6.5% YoY = inflation-hedge case strengthened. Real-rates engine ambiguous (10Y at 4.52% on soft core CPI; but hot PPI could push real rates up). Net: two of three engines bullish. Min hold to ~July 15; stop $4,250.",
    "MM-2026-007": "Near flat. USDJPY ~160.5. Hot PPI may support USD modestly vs JPY via higher US rate expectations. BoJ Sept hike >50% priced. MoF intervention ceiling at 163. Stop 163.00.",
    "MM-2026-008": "BEST PERFORMER: put spread IN THE MONEY. S&P fell -1.62% to ~7,267, below 7300 strike. Mark ~$80 vs $35 premium paid (+129%). Hot PPI → hawkish Fed → equity headwind. SpaceX IPO tomorrow ($75B raise) = liquidity drain. Hold through FOMC Jun 16-17; do not lift early.",
    "MM-2026-009": "RE-ASSESS. Hot PPI (+6.5% YoY) COMPLICATES the steepener: if PPI feeds into long-end inflation expectations, 10Y could rise with the front end instead of steepening. Thesis was: front end anchored by Fed hold, long end drifts lower. Hot PPI: long end could sell off faster. The steepener still works if Warsh signals pause (front end falls), but the short leg is now under PPI pressure. Min hold to July 16; monitor. Do not add.",
    "MM-2026-010": "Oracle capex panic confirmed Nasdaq de-rate. ECB DELIVERED +25bp today — DAX financials get NIM tailwind as confirmed. Hot PPI supports European financials additionally (higher-for-longer globally). Lagarde 'not pre-committing' = no further shock to European growth outlook. Ratio at ~0.964 recovering from 0.949 near-stop. Structural case intact. Hold through FOMC next week.",
    "MM-2026-011": "ACCELERATING. Brent toward $95-100 on Kharg Island seizure threat. $100 strike now only ~$5-6 away. Day-3 strikes vowed. Mark ~$2.50 vs $3.00 premium. Kharg execution = $100 call goes deep in the money within sessions. Defined risk; hold.",
    "MM-2026-012": "ECB DELIVERED +25bp to 2.25% — sell-the-fact CONFIRMED. Lagarde said 'not pre-committing to a particular rate path' = pause signal. EUR/USD fading from ~1.15. Hot PPI supports USD broadly (higher-for-longer Fed = USD bid). Dual tailwind materialised. Stop 1.182; target 1.130.",
    "MM-2026-013": "HEADWIND — re-mark required. Hot PPI +6.5% YoY (BLS Jun 11) re-arms hike pricing. 2Y at ~4.11%, holding; but if PPI feeds through to CPI and Warsh turns hawkish at FOMC, 2Y rises back toward 4.35% stop. The structural over-extrapolation thesis stands but timing has shifted more hawkish. Min hold 30d through Jun 16. Stop 4.35%. Do not add.",
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
    {"datum": "May PPI (released Jun 11) — HOT: final-demand +1.1% MoM / +6.5% YoY (largest 12-month rise since Nov 2022); stage-1 intermediate demand +12.3% YoY",
     "source": "BLS bls.gov/news.release/archives/ppi_06112026.htm + Trading Economics (corroborated)",
     "asof": "2026-06-11", "stale": False},
    {"datum": "May payrolls +172k",  "source": "BLS June 5",                          "asof": "2026-06-05", "stale": False},
    {"datum": "ORCL Q4 FY26 actuals: EPS $2.11, rev $19.2B, OCI +93%",
     "source": "Oracle IR / web search (Jun 10 AMC)",                                  "asof": "2026-06-10", "stale": False},
    {"datum": "ADBE Q2 FY26 — reporting tonight after close",
     "source": "Finnhub / BusinessWire (Jun 11 AMC)",                                  "asof": "2026-06-11", "stale": True},
    {"datum": "SAIL Q1 FY27: EPS $0.05 beat, rev $280M +22% YoY; -11% pre-market on slight rev miss",
     "source": "GrufuFocus / MarketBeat (Jun 9 BMO)",                                  "asof": "2026-06-09", "stale": False},
    {"datum": "SOFR ~3.62% / MOVE",  "source": "NY Fed (rail) / MOVE unverified",     "asof": "2026-06-10", "stale": True},
    {"datum": "ECB deposit rate: HIKED +25bp to 2.25% ✓ (Jun 11) — first hike in ~3 years; Lagarde: upside inflation risk, 'not pre-committing to a particular rate path'",
     "source": "CNBC + Bloomberg + Reuters + FXStreet (4 sources corroborated)",          "asof": "2026-06-11", "stale": False},
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
        "HOT PPI (+6.5% YoY, BLS) + Kharg Island seizure threat + Oracle capex panic. May PPI is the "
        "largest 12-month producer price rise since Nov 2022 — hawkish for Fed, headwind for rates pre-positions. "
        "Trump threatened to seize Kharg Island (~90% of Iran's crude) and vowed Day-3 strikes — most oil-bullish "
        "statement since the war; Brent toward $95-100. SpaceX IPO tomorrow (SPCX, $135/share, $75B raise — biggest ever). "
        "ECB decision PENDING today. SPX put spread in the money (+129%). Adobe reports tonight."
    ),

    "summary_narrative": """
<p><strong>Four themes dominate the June 11 tape — and one prior framing requires an immediate correction.</strong></p>

<p><strong>1. May PPI is HOT — pipeline re-accelerating.</strong> BLS released May producer prices this
morning: final-demand PPI <strong>+1.1% MoM and +6.5% YoY</strong>, the largest 12-month rise since
November 2022 (sources: BLS bls.gov/news.release/archives/ppi_06112026.htm + Trading Economics).
Stage-1 intermediate demand rose +12.3% YoY — the pipeline is not clearing; it is accelerating. The
previous framing of PPI as soft was wrong and is corrected here. The honest re-mark: Warsh walks into
FOMC June 16-17 with CPI at 4.2% headline <em>and</em> PPI at +6.5%. He cannot credibly signal a
dovish tilt. The rates pre-positions (short 2Y MM-013, short 10Y MM-004) now face a genuine headwind;
they are flagged honestly as under pressure rather than as straightforward winning setups.</p>

<p><strong>2. Kharg Island — escalation to a new level.</strong> Trump vowed a third consecutive night
of strikes on Iran and threatened to <em>seize Kharg Island</em>, Iran's main oil export terminal
handling roughly <strong>90% of Iran's crude exports</strong> (~2.5-3M bbl/day). Even as a threat,
this is the most oil-bullish single statement since hostilities began. (Sources: Bloomberg, Axios, CNBC.)
The counterweight: UAE and Iran held their <strong>first face-to-face meeting since the war began</strong>
— a de-escalation channel now open. (Sources: Bloomberg, Al Jazeera.) Brent moves toward $95-100. The
$100 strike on the call spread (MM-011) is ~$5-6 away. Bloomberg's $130/bbl July-August forecast is
now the base case, not the tail, if the Strait stays at 15% capacity.</p>

<p><strong>3. Oracle capex panic (from last night's close).</strong> Revenue ~$19.2bn (slight beat),
OCI +93%, Cloud +47%, RPO surged to <strong>~$638bn</strong> from ~$553bn — the largest confirmed AI
backlog in enterprise software history. The AI demand thesis is confirmed. What punished the stock
(-7 to -11% AH): FY26 capex $55.7bn (above guide), FY27 guided ~$70bn + $20-25bn prepayments, ~$40bn
raise. Capital and capacity problem, not a demand problem. The capital-protected note (idea 101) is the
post-print entry: absorb the dilution overhang, participate in the OCI re-rate.</p>

<p><strong>4. SpaceX IPO — biggest in history, debuts tomorrow.</strong> Priced last night at
$135/share, ~$1.77T valuation, ~$75bn raise, Nasdaq debut tomorrow (Jun 12) under ticker
<strong>SPCX</strong>, Goldman lead. (Source: CNBC.) The cross-market impact: $75bn in capital
allocation to a single new issue is the largest IPO liquidity drain in history. Cash deployment into
SPCX is a marginal headwind for risk assets tonight and tomorrow.</p>

<p>The <strong>ECB delivered its +25bp hike to 2.25%</strong> today (Jun 11) — the first hike in nearly
three years — explicitly citing Iran-war-driven inflation (euro-area CPI 3.2% in May, above the 2%
target). Lagarde flagged upside risks to inflation, downside risks to growth, and said the ECB is
<em>"not pre-committing to a particular rate path"</em> — the pause signal. Sell-the-fact confirmed:
EUR/USD fading from ~1.15 post-delivery, dual tailwind with hot PPI supporting USD broadly. (Sources:
CNBC, Bloomberg, Reuters, FXStreet.) MM-012 short-EUR thesis is executing.</p>

<p>The SPX put spread (MM-2026-008) is <strong>in the money</strong> — S&amp;P -1.62% yesterday to
~7,267, through the 7300 strike. Mark ~$80 vs $35 premium paid (+129%). Hot PPI + SpaceX IPO drain both
add to equity headwind. FOMC Jun 16-17 is still inside Jun 27 expiry. Adobe reports tonight (idea 102
CSP gate opens post-print; do not pre-position).</p>
""",

    "takeaways": [
        "<strong>CORRECTION — May PPI is HOT:</strong> BLS released final-demand PPI at +1.1% MoM and +6.5% YoY on "
        "June 11 — the largest 12-month rise since November 2022 — with stage-1 intermediate demand up +12.3% YoY. "
        "The pipeline is re-accelerating, not clearing. This is explicitly hawkish: Warsh walks into FOMC June 16–17 "
        "facing CPI at 4.2% headline <em>and</em> PPI at 6.5%, which makes a credibly dovish tilt very difficult. "
        "The rates pre-positions (MM-013 short 2Y, MM-004 short 10Y) entered on a soft-inflation thesis that PPI "
        "has now materially complicated — do not add to either; stops at 4.35% and 4.65% are now risk-live.",

        "<strong>ECB delivered +25bp to 2.25%</strong> today (Jun 11) — the first hike in nearly three years — "
        "explicitly citing Iran-war-driven inflation, with euro-area CPI at 3.2% in May. Lagarde's press conference "
        "provided exactly the pause signal the sell-the-fact trade required: she said the ECB is 'not pre-committing "
        "to a particular rate path,' removing the forward catalyst for EUR longs. EUR/USD is fading from ~1.15 "
        "post-delivery, and hot PPI adds USD-broadly-supportive context on top — two confirmed tailwinds for "
        "MM-012. (Sources: CNBC, Bloomberg, Reuters, FXStreet.)",

        "<strong>Kharg Island escalation — most oil-bullish statement of the war:</strong> Trump vowed a third "
        "consecutive night of strikes on Iran and threatened to physically seize Kharg Island, the terminal "
        "handling roughly 90% of Iran's crude exports (~2.5-3M bbl/day). Even as a threat, this is unprecedented "
        "and has pushed Brent toward $95–100. The Brent call spread's $100 strike is only ~$5–6 away. "
        "The counterweight is the UAE–Iran first face-to-face meeting since the war began, which opens a "
        "de-escalation channel and prevents the market pricing a straight-line seizure. The oil longs are "
        "well-earned and should be held. (Bloomberg, Axios, CNBC; UAE–Iran: Bloomberg, Al Jazeera.)",

        "<strong>Oracle capex panic (from Tuesday night's close):</strong> Revenue ~$19.2B was a slight beat, "
        "OCI grew 93%, and RPO surged to $638B — the largest AI backlog in enterprise software history. "
        "The demand story is unambiguously confirmed. What punished the stock 7–11% after hours was the "
        "capital-structure arithmetic: FY26 capex at $55.7B above guide, FY27 guided to ~$70B plus $20–25B "
        "in component prepayments, funded by a $40B raise including $20B in new equity. The capital-protected "
        "note (idea 101) is the correct post-print instrument — 70–80% participation in the OCI re-rate with "
        "100% capital protection against the dilution overhang. The window is open.",

        "<strong>SpaceX IPO debuts tomorrow on Nasdaq (ticker SPCX):</strong> Priced at $135/share with a "
        "~$1.77T valuation, raising ~$75B — the largest IPO in history by capital raised (Goldman lead, "
        "Source: CNBC). The cross-market implication is not about SpaceX's fundamentals; it is that $75B "
        "in new capital allocation is being funded from existing equity portfolios, disproportionately "
        "concentrated in large-cap tech and AI. Expect marginal selling pressure in semiconductors and "
        "cloud names tomorrow as institutional allocations are funded — not a fundamental short signal, "
        "but a real one-session liquidity drain.",

        "<strong>SPX put spread is in the money at +129%:</strong> The S&amp;P fell 1.62% to ~7,267 yesterday, "
        "taking it through the 7,300 strike. The spread was entered at $35; the estimated mark is ~$80. "
        "The key point is that the FOMC on June 16–17 — now a more hawkish event given PPI — remains inside "
        "the June 27 expiry. Hot PPI and the SpaceX IPO liquidity drain both add to the equity headwind "
        "into that date. Do not take early profit; the residual value is the FOMC tail.",

        "<strong>Adobe reports after the close tonight</strong> with consensus EPS at $5.01 (Finnhub), "
        "revenue guided $6.43–6.48B, and an implied move of ±9.47%. This is the cleanest remaining test "
        "of whether generative AI is a software incumbent's tailwind or tax. The cash-secured put entry "
        "gate (idea 102: $385 put) opens only after the print — there is no edge in pre-positioning; "
        "the discipline is to wait and act on the outcome.",

        "<strong>FOMC June 16–17 is the terminal gate — context has shifted hawkish:</strong> Coming into "
        "last week the market assigned 96–98% probability to a hold with no hawkish signal. Hot PPI at "
        "+6.5% YoY changes that calculus: Warsh faces CPI 4.2% plus PPI 6.5% in his first meeting as "
        "chair and cannot credibly signal a dovish tilt. The non-trivial probability is now a hawkish "
        "surprise — a hike bias or explicit 'further tightening' language. MM-013 and MM-009 remain "
        "open as pre-positions but their thesis is contested. Stops matter.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "20%",
         "headline": "UAE-Iran deal + FOMC signals pause; PPI spike proves transitory",
         "body": "UAE-Iran talks produce a Strait interim deal — Brent falls toward $86-88, inflation fears "
                 "cool. Warsh at FOMC Jun 16-17 emphasises core CPI (2.9%) over PPI headline, signals "
                 "data-dependent pause — 2Y falls 15-20bp, equity risk re-opens. Oracle dilution overhang "
                 "fades as OCI growth data flows. SpaceX IPO demand is met without crowding out. "
                 "Risk up · rates down · dollar soft · oil falls · gold consolidates."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "Kharg threat proves rhetorical; grind — PPI-elevated rates, war premium stays",
         "body": "Trump's Kharg Island threat is not executed — a tactical pressure statement. Brent holds "
                 "$90-96 on ongoing Strait restriction but no new supply shock. FOMC holds at 3.75% with "
                 "zero-cut dots; Warsh acknowledges hot PPI without signalling hikes — rates grind higher "
                 "near the stop, not through it. Oracle rebuilds over weeks; Adobe mixed tonight. "
                 "SpaceX IPO absorbs well. Risk mixed · rates elevated · dollar firm · gold bid on PPI."},
        {"kind": "bear", "label": "Bear", "pct": "35%",
         "headline": "Kharg Island seized OR Warsh hawks up — stagflation + credit crunch",
         "body": "Trump executes on Kharg Island threat: ~2.5-3M bbl/day removed, Brent gaps to $110-130 "
                 "(Bloomberg forecast materialises), stagflation spike. AND/OR Warsh delivers explicitly hawkish "
                 "dot plot (hike bias) on PPI +6.5% + CPI 4.2% evidence — 2Y +25bp, rates pre-positions stopped, "
                 "AI multiples compress sharply, SPX toward 6,800-7,000. SpaceX IPO absorbs badly, liquidity "
                 "crunch adds to the sell. Risk sharply down · rates up hard · gold up · oil spike."},
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

<p>The ECB <strong>delivered the +25bp hike to 2.25%</strong> today (Jun 11) — the first in nearly
three years — explicitly citing Iran-war-driven inflation as the rationale. Euro-area CPI was 3.2%
in May, above the 2% target, and the Bank said it could not remain passive while supply-shock
inflation entrenched. Lagarde's press conference was precisely the pause signal the sell-the-fact
trade required: she flagged upside risks to inflation but simultaneously noted downside risks to
growth, and declined to pre-commit to a future path. That nuanced wording is the inflection: the
marginal EUR buyer — the spec account that had built a multi-year EUR long from 1.08 to 1.15
pricing in this hike — now has the event behind it and no forward catalyst for additional hikes.
The unwind has begun. EUR/USD is fading from ~1.15 post-delivery. The structural case strengthens
with hot PPI: if the US must keep rates higher-for-longer (PPI +6.5% YoY forces Warsh's hand),
the USD carry advantage widens further versus a pause-signalling ECB. MM-012 has dual tailwinds.
(Sources: CNBC, Bloomberg, Reuters, FXStreet.)</p>

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

<p>This morning's May PPI is the most important macro data point since the CPI print. Final-demand PPI
<strong>+1.1% MoM and +6.5% YoY</strong> (BLS) — the largest 12-month rise since November 2022. Stage-1
intermediate demand at +12.3% YoY confirms the pipeline is not clearing; it is accelerating. Correct the
prior framing: this is not disinflation broadening. This is the opposite — producer-price re-acceleration.
The implication for the Fed: Warsh now faces CPI 4.2% AND PPI 6.5% entering FOMC Jun 16-17. The core
CPI (2.9%) gives him the look-through argument on energy at the consumer level; the hot PPI undermines
that argument at the producer level. Net: the balance of risk has shifted toward hawkish. The FOMC is
no longer a coin-flip on pause vs nothing; it is now a coin-flip on data-dependent hold vs hike signal.</p>

<p>Priced-versus-not: <strong>under-priced</strong> — Kharg Island physical seizure scenario (if executed:
Brent gaps to $110-130, removes ~90% of Iran's crude; the market is priced for Strait restriction, not
for Kharg); FOMC hawkish surprise (Warsh has CPI 4.2% + PPI 6.5% forcing his hand); SpaceX IPO liquidity
drain ($75B capital allocation = cross-market; not priced in the VIX). <strong>Fairly priced:</strong>
Brent outright ~$93-95 on Strait restriction; the ECB hike (fully in the price).
<strong>Fully priced:</strong> Oracle revenue beat (already discounted); the Strait partial blockade
(already in $93-95 Brent). <strong>Over-priced (at risk):</strong> the long-duration trades (short 10Y,
short 2Y) — they were entered on a soft-inflation thesis that hot PPI has materially challenged.</p>
""",

    "wrap": """
<p>Thursday's tape was defined by three events arriving inside a six-hour window, each pulling in a
different direction and together producing the most complex macro set-up of the year so far. By midday
London, the picture was clear: stagflation risk is back on the table, the ECB has blinked first among
major central banks, and the oil market is one presidential threat away from a supply shock that would
make the 1973 embargo look modest.</p>

<p>Begin with the number that changes everything: May producer prices came in at +1.1% month-on-month and
+6.5% year-on-year, the largest twelve-month rise in final-demand PPI since November 2022 (BLS,
corroborated by Trading Economics). Stage-one intermediate demand surged +12.3% year-on-year. This is
not a blip — it is pipeline re-acceleration. The prior framing of "soft PPI / dovish Fed" was wrong,
and this brief corrects it in full. What it means for Kevin Warsh walking into FOMC on June 16–17 is
stark: he faces headline CPI at 4.2% <em>and</em> PPI at 6.5%, simultaneously, in his first meeting as
chair. He cannot credibly signal a dovish tilt without an immediate credibility problem. The core CPI
print of 2.9% gives him a technical look-through argument on energy at the consumer level, but the
+6.5% producer-price reading undermines that argument the moment it passes through to the next CPI
vintage. The market is still pricing a 96–98% probability of a hold; the probability of a hawkish
surprise — a hike bias, an explicit "further tightening may be warranted" — is materially
underweighted. The SPX put spread held through CPI, held through Oracle, and is in the money at +129%.
PPI makes the FOMC tail larger, not smaller.</p>

<p>In Frankfurt, the ECB delivered what the market expected but framed it in a way that immediately
triggered the sell-the-fact trade. The +25 basis-point hike to 2.25% — the Bank's first in nearly three
years — was unanimous and explicitly justified by Iran-war-driven energy inflation, with euro-area CPI
holding at 3.2% in May against a 2% target. What made the difference was Lagarde's press conference:
she flagged upside risks to inflation and downside risks to growth in the same breath, and declined to
pre-commit to any future rate path. That measured, two-handed language is exactly what the spec community
that had built EUR longs from 1.08 to 1.15 did not want to hear. The marginal EUR buyer needed a
commitment to further hikes to justify holding the position; the "not pre-committing" formulation
removes that rationale entirely. EUR/USD began fading from ~1.15 within minutes of the presser. Add hot
US PPI — which forces the Fed to stay restrictive and therefore widens the USD carry advantage — and
MM-012 now has two confirmed tailwinds rather than one speculative one. (Sources: CNBC, Bloomberg live
blog, Reuters, FXStreet — four sources corroborated.)</p>

<p>In the Middle East, Donald Trump raised the escalation stakes to a level that has no precedent in
this conflict. Having vowed a third consecutive night of strikes on Iran, he went further and threatened
to physically seize Kharg Island — Iran's main oil export terminal, handling roughly 90% of the
country's crude exports, or approximately 2.5 to 3 million barrels per day. Even as a threat, this is
the most oil-bullish single statement since the war began. Bloomberg's $130/barrel July–August forecast,
which looked aggressive two weeks ago, is now the base case if the Strait of Hormuz stays at 15% of
pre-war traffic. The counterweight is real but not decisive: the UAE and Iran held their first
face-to-face meeting since hostilities began, opening a de-escalation channel that prevents the market
from pricing a straight-line seizure. The correct frame is managed escalation with a credible right
tail — not a ceasefire, not total war. Brent is pushing toward $95–100. The call spread's $100 strike
is five or six dollars away. (Sources: Bloomberg, Axios, CNBC for Trump threat; Bloomberg, Al Jazeera
for UAE–Iran talks.)</p>

<p>Last night's Oracle print is still reverberating through the AI semiconductor complex. Revenue of
$19.2 billion was a slight beat; OCI +93%, cloud +47%, RPO surging to $638 billion from $553 billion —
the largest confirmed AI backlog in enterprise software history. The AI demand thesis is not in doubt.
What punished the stock 7–11% after hours was the capital-structure arithmetic: FY26 capex came in at
$55.7 billion above guide, FY27 is guided at $70 billion plus $20–25 billion in component prepayments,
and the whole package is funded via a $40 billion debt-and-equity raise. That is a company committing
more capital in one fiscal year than it earns in revenue. The equity market's verdict — sell the raise,
own the backlog through a protected structure — is exactly what the capital-protected note (idea 101)
was designed for. The window is open.</p>

<p>Tomorrow, SpaceX debuts on Nasdaq under ticker SPCX at $135 per share, a $1.77 trillion valuation,
with Goldman Sachs as lead on what is the largest IPO in history at roughly $75 billion raised. (Source:
CNBC.) The cross-market read is not about SpaceX the business — it is about where $75 billion in
capital is coming from. It is coming from existing equity portfolios, disproportionately concentrated
in large-cap tech and AI names. Expect marginal selling pressure in semiconductors and cloud names
tomorrow morning as institutional allocations are funded. It is not a structural short signal; it is a
one-session liquidity drain that explains any tech underperformance tomorrow that otherwise lacks a
fundamental catalyst.</p>

<p>The book's posture into the close is straightforward. The put spread is in the money and held — the
FOMC remains inside the June 27 expiry and is now a larger tail, not a smaller one. The oil longs are
earning and upgraded; the Kharg Island right-tail is the largest non-consensus risk in the market and
the call spread is the correct expression of it. Short EUR/USD is executing with confirmed dual tailwinds.
Gold's three-engine thesis (safe-haven, inflation-hedge, real-rates uncertainty) is intact. The only
honest admissions: the short 2Y and short 10Y positions entered on a soft-inflation thesis that hot PPI
has materially challenged. Stops at 4.35% and 4.65% are risk-live. Do not add. Adobe reports after the
close tonight — the cash-secured put entry gate (idea 102) opens only after the print, not before.</p>
""",

    "correlation_regime": """
<p><strong>1. Bonds and equities: no more safe-haven comfort in Treasuries.</strong> Hot PPI (+6.5% YoY)
breaks the classic risk-off flight-to-bonds: if inflation is re-accelerating, the 10Y is not a safe haven
— it is a source of risk. Gold has taken over the safe-haven role (up $4,104+) as it offers both
the inflation-hedge and the geopolitical-risk premium simultaneously. Watch for the bond/equity
correlation to flip from negative (usual safe-haven) toward positive (stagflation regime).</p>

<p><strong>2. EUR/USD sell-the-fact confirmed after ECB delivered.</strong> The ECB hiked +25bp to 2.25%
today (Jun 11), Lagarde signalled "not pre-committing to a rate path" = pause. EUR/USD fading from ~1.15
post-delivery. Hot PPI adds a USD-broadly-supportive overlay: the Fed must stay restrictive, widening
the USD carry advantage. ECB sell-the-fact + US higher-for-longer = double confirmed tailwind for
short-EUR/USD (MM-012).</p>

<p><strong>3. Brent and equities are telling different stories — and hot PPI widens the gap.</strong>
Brent rising toward $95-100 on Kharg Island threat + PPI re-acceleration is a supply AND inflation
story. Equities are being squeezed by: Oracle capex shock (top-line fear), hot PPI (rate-hike fear),
and SpaceX IPO liquidity drain tomorrow. The divergence between energy and equities should widen. Oil
longs and the SPX put spread are both positioned for exactly this configuration.</p>
""",

    "vol_skew": """
<p><strong>The VIX is catching up but still not pricing all the tails.</strong> Estimated VIX9D ~18 ·
VIX ~21 · VIX3M ~22 · VIX6M ~23 — repricing from 15.3 last week, but still materially under-priced
for the calendar: FOMC Jun 16-17 + Kharg Island tail + SpaceX IPO tomorrow all in the same window.
The term curve is flat when it should be steeply backwardated. The skew story: hot PPI should be
pushing put skew higher (inflation + hawkish Fed = equity downside risk), but the VIX term structure
hasn't incorporated the full PPI-to-FOMC pipeline. The SPX put spread is in the money; the hedge paid
before the main event (FOMC) even arrived. The residual value in the put spread is the FOMC tail.</p>
""",

    "sector_rv": """
<p><strong>Leading:</strong> Energy producers (Brent toward $95-100 on Kharg Island threat; Day-3 strikes;
SpaceX IPO not relevant), gold/metals (PPI inflation hedge + geopolitical bid; three engines running).
ECB DELIVERED +25bp — European financials get NIM relief confirmed (DAX tailwind active). Hot PPI broadly
supportive of financials globally (higher-for-longer = wider margins).
<strong>Lagging:</strong> US tech/AI semis (Oracle capex panic + hot PPI hike risk = dual multiple
compression); long-duration bond-proxies (utilities, REITs — hot PPI pushes real yields higher);
European luxury (LVMH: energy inflation + ECB tightening = twin headwind).
<strong>Tomorrow watch:</strong> SpaceX (SPCX) IPO debut on Nasdaq — space tech, satellites, Starlink
revenue; $1.77T valuation. Peers: Boeing, L3Harris, Iridium. The IPO supply overhang drains tech liquidity.</p>

<p><strong>RV:</strong> Long DAX / short Nasdaq (MM-2026-010) structural case confirmed: Nasdaq under
Oracle + hot PPI pressure; ECB hike (+25bp, DONE) delivered the DAX financials NIM-relief catalyst.
Ratio recovered from 0.949 near-stop. Hot PPI supports European financials via higher-for-longer global
rate environment. Hold through FOMC next week.</p>
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
<p>SOFR near 3.62% — unchanged. The plumbing is unmoved even through three days of US-Iran strikes and the
ECB's +25bp hike to 2.25% (delivered Jun 11, first in ~3 years). <strong>The Pozsar mechanic remains live:</strong>
FOMC at 3.50-3.75% (held) means secured funding sits
well below the 2Y yield (~4.15%), and every floating-rate borrower issued in 2023-24 expecting two-to-three
cuts is still cash-flow negative versus its model. A FOMC pause signal next week narrows that gap; a hawkish
dot plot widens it. IG spreads are the tell — they tighten when the market believes the terminal rate is falling
and gap out when the hike narrative re-emerges.</p>
""",

    "tape_missing": """
<p><strong>1. The Oracle dilution story is masking the fundamental re-rate.</strong> The market punished the
raise (-10% AH) and is pricing the equity dilution math. It is not yet pricing what Oracle's $638bn RPO
converts to in OCI free cash flow in 18-24 months. The note structure (capital-protected, 70-80% participation)
lets you hold the backlog conviction without the dilution hangover.</p>

<p><strong>2. The FOMC risk is now MORE hawkish than the market prices.</strong> The 96-98% hold probability
means the market is priced for nothing. Hot PPI +6.5% YoY changes the calculus: Warsh faces CPI 4.2% AND PPI
6.5% in his first presser. He cannot signal a dovish tilt without a credibility problem. The non-trivial
asymmetry is now a HAWKISH surprise, not a dovish signal. The SPX put spread is the correct hedge for this
tail; MM-013 and MM-004 are exposed to it — their stops matter now.</p>

<p><strong>3. Kharg Island physical seizure is not in the price.</strong> Trump threatened to seize Kharg
Island — ~90% of Iran's crude exports (~2.5-3M bbl/day). If executed: Brent gaps to $110-130. The $100
call spread strike (MM-011) is only ~$5-6 away. The VIX curve has not priced this tail. The oil longs and
call spread are the right instruments for a scenario the equity market has entirely ignored.</p>

<p><strong>4. SpaceX IPO liquidity drain is not in the VIX.</strong> The largest IPO in history ($75B raise)
debuts tomorrow on Nasdaq. The cross-market allocation drag — cash pulled from existing equities to fund
SPCX — is a marginal headwind for AI/tech that is not priced in the VIX term structure. Watch for
tomorrow-dated equity selling that is IPO-driven, not macro-driven.</p>
""",

    "book_outlook": {
        "commentary": (
            "The book is correctly positioned for the tape — but one prior framing requires correction. "
            "<b>Hot PPI (+6.5% YoY, BLS Jun 11)</b> is the key re-mark: the rates pre-positions (short 2Y MM-013, "
            "short 10Y MM-004) were framed as gaining a softer entry; that is wrong. They are under pressure from "
            "hawkish PPI re-acceleration. The <b>SPX put spread is in the money at +129%</b>, the Brent longs are "
            "upgraded on Kharg Island seizure threat, gold is running on three engines (safe-haven + inflation-hedge + "
            "real-rates), and MM-012 has hot-PPI USD support on top of the ECB sell-the-fact. "
            "Today's confirmed events: ECB DELIVERED +25bp to 2.25% (sell-the-fact active, MM-012 executing); "
            "Day-3 strikes + Kharg threat = Brent toward $95-100; SpaceX IPO tomorrow ($75B drain); "
            "Adobe reports tonight (do NOT pre-position). "
            "Respect stops on MM-013 (4.35%) and MM-004 (4.65%) — PPI has moved the goalposts."
        ),
        "outperform": [
            {"name": "Brent positions (MM-002, MM-003, MM-011)", "why": "Kharg Island seizure threat (Day-3 strikes, "
             "Trump statement) + Strait at 15% capacity + Bloomberg $130 Jul-Aug forecast. $100 call spread strike "
             "only ~$5-6 away. UAE-Iran talks are the only counterweight. The war premium has a new right tail. Do not trim."},
            {"name": "Xetra-Gold (4GLD)", "why": "Three engines: geopolitical safe-haven (Day-3 strikes, Kharg threat), "
             "inflation hedge (PPI +6.5% YoY = stagflation overlay), and real-rates (10Y at 4.52%, uncertain direction). "
             "Net: bullish. Min hold to ~Jul 15; stop $4,250."},
            {"name": "Short EUR/USD (MM-012)", "why": "ECB DELIVERED +25bp to 2.25% today — sell-the-fact CONFIRMED. "
             "Lagarde said 'not pre-committing to a particular rate path' = pause signal. EUR/USD fading from ~1.15. "
             "Hot PPI adds USD-broadly-supportive overlay (higher-for-longer Fed = USD bid). Dual tailwind confirmed. "
             "Stop 1.182."},
            {"name": "SPX put spread (MM-008)", "why": "In the money at +129%. Hot PPI + SpaceX IPO liquidity drain "
             "both add to equity headwind. FOMC hawkish surprise risk now HIGHER (not lower) after PPI. "
             "Hold through Jun 16-17 — maximum residual value in the FOMC tail."},
        ],
        "underperform": [
            {"name": "Micron (MU) — 25.8%", "why": "The book's largest equity risk. Oracle capex panic + hot PPI "
             "(hawkish Fed risk) = dual AI semis headwind. Hot PPI → higher real rates → multiple compression for "
             "high-growth semis. The concentration is the amplifier."},
            {"name": "NVDA / AVGO / AMD", "why": "Oracle capex shock + PPI-driven rate risk = two vectors of multiple "
             "compression. SpaceX IPO tomorrow drains marginal capital from existing tech/semis. Range-bound at best."},
            {"name": "LVMH (MC FP)", "why": "ECB decision today + energy inflation (Brent toward $100) + PPI "
             "re-acceleration = triple headwind for European luxury: rate tightening, energy costs, consumer squeeze."},
            {"name": "US Treasury 1.25% 2031", "why": "Hot PPI +6.5% YoY directly challenges this bond's thesis: "
             "if inflation re-accelerates, the 10Y could move from 4.52% toward the 4.65% danger zone. "
             "The Warsh hawkish scenario — now more likely — tests this position hardest."},
        ],
        "watch": [
            {"label": "Do not pre-position Adobe", "text": "The CSP entry gate for idea 102 opens only after tonight's "
             "print. Hold cash, set the entry level ($385 CSP if ADBE trades down to support). Do not guess the print."},
            {"label": "Maintain the SPX hedge", "text": "Put spread at +129% with FOMC Jun 16-17 still inside expiry. "
             "Hot PPI has increased the probability of a hawkish dot plot — the tail the hedge was bought for. "
             "Do not take profit early; the residual value is the FOMC tail."},
            {"label": "Oracle note window open", "text": "Capital-protected note (idea 101): full downside protection "
             "against the dilution hangover, 70-80% participation in the OCI re-rate. Window open; $638bn RPO thesis."},
            {"label": "WATCH stops on rates trades", "text": "Hot PPI has shifted the FOMC probability toward hawkish. "
             "MM-013 stop 4.35% and MM-004 stop 4.65% are now risk-live. Do not add to either position. "
             "If FOMC delivers hawkish dots, stops are hit — that is the correct outcome, not a surprise."},
            {"label": "SpaceX IPO tomorrow (SPCX, Nasdaq)", "text": "Biggest IPO ever ($75B raise). Watch for marginal "
             "equity selling pressure in AI/tech tomorrow as capital is allocated to SPCX. Not a structural event "
             "but a temporary liquidity drain. No action needed — just context for tomorrow's equity tape."},
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
         "view": ("Hot headline, soft core — the 10Y eased to ~4.52% on the print. HOWEVER: the next-day hot PPI "
                  "(+6.5% YoY) materially complicates this read. Soft core at the consumer level does not stay "
                  "soft if the producer pipeline re-accelerates. The CPI gave one day of relief; the PPI took it back."),
         "asymmetry": "DONE: one-day relief on soft core. Subsequent hot PPI reverses the FOMC-dovish-probability read.",
         "dir": "flat"},
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
        {"day": "Thu", "date": "Jun 11 ✓",
         "event": "US May PPI — RELEASED: HOT (+1.1% MoM / +6.5% YoY)",
         "consensus": "Final-demand PPI +1.1% MoM / +6.5% YoY — largest 12-month rise since November 2022. "
                      "Stage-1 intermediate demand +12.3% YoY. Pipeline re-accelerating. "
                      "Source: BLS bls.gov/news.release/archives/ppi_06112026.htm + Trading Economics (corroborated).",
         "view": ("HAWKISH re-read. Warsh walks into FOMC Jun 16-17 with CPI 4.2% AND PPI 6.5% — cannot signal "
                  "a dovish tilt without credibility damage. Rates pre-positions (MM-013, MM-004) face headwinds. "
                  "Oil positions reinforced (PPI pipeline = inflation stays high, oil bid). Gold inflation-hedge "
                  "case strengthened. Short-EUR/USD gets USD-broadly-supportive overlay."),
         "asymmetry": "Hot PPI = FOMC hawkish surprise risk higher; 2Y toward stop 4.35%. Gold/oil up. "
                      "If Warsh ignores PPI (looks through energy), rates relief resumes but credibility damaged.",
         "dir": "up"},
        {"day": "Thu", "date": "Jun 11 ✓",
         "event": "ECB rate decision — DONE: +25bp to 2.25% delivered; first hike in ~3 years",
         "consensus": "Hiked +25bp to 2.25% as expected. Euro-area CPI 3.2% May (above 2% target). "
                      "Lagarde cited Iran-war-driven inflation explicitly. EUR/USD ~1.15 at delivery, now fading. "
                      "Sources: CNBC, Bloomberg, Reuters, FXStreet (4 corroborated).",
         "view": "Sell-the-fact CONFIRMED: EUR bid from 1.08 to 1.15 on the hike cycle; once delivered, the "
                 "marginal EUR buyer is done. Lagarde's 'not pre-committing to a particular rate path' = pause "
                 "signal. EUR/USD fading. Hot PPI adds USD-broadly-supportive overlay = dual tailwind for MM-012.",
         "asymmetry": "DONE: sell-the-fact underway (EUR/USD -0.5 to -1% expected over 2-5 sessions). "
                      "Hot PPI + Fed higher-for-longer widens USD carry advantage further.",
         "dir": "down"},
        {"day": "Thu", "date": "Jun 11 (tonight)",
         "event": "Adobe (ADBE) Q2 — after close",
         "consensus": "Consensus EPS $5.01 (Finnhub); rev $6.43-6.48bn; implied move ±9.47%. Near 52-week lows.",
         "view": "Cleanest remaining test of whether generative-AI is a software tax or tailwind. DO NOT pre-position — "
                 "wait for the print to open the CSP entry gate (idea 102: $385 cash-secured put).",
         "asymmetry": "AI additive to ARR: software relief +8-10%; cannibalisation read: ADBE toward $330s, CSP assigned",
         "dir": "flat"},
        {"day": "Fri", "date": "Jun 12 ← TOMORROW",
         "event": "SpaceX IPO Nasdaq debut — ticker SPCX, $135/share, ~$1.77T valuation",
         "consensus": "Priced Jun 11 at $135/share, 555.6M shares, ~$75B raise (Goldman lead). Biggest IPO in history. "
                      "Nasdaq debut tomorrow (Source: CNBC). No comparable precedent for $75B single-day IPO capital allocation.",
         "view": ("Cross-market liquidity event: $75B capital drain from existing equities. AI/tech is most exposed. "
                  "Not a fundamental short signal — SpaceX is an extraordinary business — but the IPO-supply overhang "
                  "is a marginal headwind for tech liquidity tomorrow. Watch for SPX/NDX early weakness."),
         "asymmetry": "High demand absorbs smoothly: limited market impact. Overhang selling: AI/tech -1-2% intraday. "
                      "No action needed from the book — just context for tomorrow's tape.",
         "dir": "down"},
        {"day": "Tue-Wed", "date": "Jun 16-17",
         "event": "FOMC + dot plot — Warsh's first meeting, 96-98% hold priced",
         "consensus": "Hold at 3.50-3.75% consensus; dots are the whole event. "
                      "Warsh now faces CPI 4.2% AND PPI 6.5% — BOTH above acceptable levels for a soft presser.",
         "view": ("UPDATED — hawkish scenario now more likely after hot PPI. Three scenarios: "
                  "(1) Hold + hike bias (CPI+PPI justify it): 2Y +20-25bp, stops MM-013/MM-004 triggered, SPX -2-3%; "
                  "(2) Hold + data-dependent (core CPI look-through): 2Y -5-10bp, limited relief; "
                  "(3) Hold + pause signal (ignores PPI): 2Y -15-20bp — credibility risk for Warsh. "
                  "MM-008 (put spread) benefits from all but scenario 3."),
         "asymmetry": "Hike bias: 2Y +25bp, SPX -3%, put spread pays; pause signal: 2Y -15bp, gold +2%; "
                      "data-dependent neutral: range. Probability distribution shifted hawkish post-PPI.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660. At ~1.637; stop 1.662. ECB DELIVERED +25bp today — Lagarde said 'not pre-committing' = pause signal confirmed. Sell-the-fact underway, hot PPI supports USD broadly. 'Further hikes' language absent — stop test risk reduced.</li>
<li><strong>MM-2026-002 · Long Brent:</strong> exit on weekly close below $87 — war premium gone. At ~$92-95, climbing on Kharg threat. The Strait is still shut. Day-3 strikes vowed. Hold.</li>
<li><strong>MM-2026-003 · Long Brent/Short WTI spread:</strong> close below $2.00. At ~$3.40. Stop 1.50. Kharg Island threat = Brent-specific supply shock = spread widens. Hold.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop at 4.65%. At ~4.52%. HEADWIND: hot PPI +6.5% YoY shifts balance toward hawkish FOMC. Position ~8bp offside. Do NOT add. Stop 4.65% is risk-live. FOMC Jun 16-17 is the terminal gate.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to July 15. Stop $4,250 (already touched Jun 10, min_hold override). At ~$4,075. Three-engine bid: geopolitical + inflation-hedge (PPI) + real-rates uncertainty. Hold.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160.5. Hot PPI may support USD modestly. BoJ Sept hike >50% priced. Carry unwind coming, not today.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> in the money (+129%). Hot PPI raised FOMC hawkish probability — maximum remaining value is in the FOMC tail. Hold through Jun 16-17 expiry. Do not take early profit.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to July 16. At ~+40bp; target +60bp. COMPLICATION: hot PPI can push 10Y higher alongside the front end rather than steepening. Monitor. Do not add. Stop is the 30-day min-hold discipline.</li>
<li><strong>MM-2026-010 · Long DAX / short Nasdaq:</strong> stop ratio 0.943. ECB DELIVERED today — DAX financials NIM tailwind confirmed. Oracle + hot PPI compresses Nasdaq multiple. Hot PPI globally supportive of bank NIM = DAX financials. Ratio recovering. Hold.</li>
<li><strong>MM-2026-011 · Brent 100/115 call spread:</strong> $100 strike ~$5-6 away at current Brent ~$94-95. Kharg Island seizure threat = $100 trigger in range. Defined risk; hold. Exit: Brent falls below $85 for 3 sessions.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. ECB DELIVERED +25bp — sell-the-fact CONFIRMED, EUR fading from ~1.15. Lagarde 'not pre-committing' = no further-hike squeeze risk near-term. Hot PPI USD support = dual tailwind both confirmed. Hold.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold 30d. At ~4.11%. HEADWIND: hot PPI re-arms hike pricing. 2Y risk of moving back toward stop. Do NOT add. The structural over-extrapolation thesis stands but timing shifted hawkish. Respect stop.</li>
</ul>
""",

    "client_ammo": [
        {"q": "PPI was reported hot today — what does that mean for the Fed and our rates positions?",
         "a": ("May PPI came in at +1.1% MoM and +6.5% YoY (BLS, Jun 11) — the largest 12-month producer price "
               "rise since November 2022. Stage-1 intermediate demand is up +12.3% YoY. This means the inflation "
               "pipeline is re-accelerating. The read-through for the Fed: Warsh now walks into FOMC June 16-17 "
               "facing both CPI at 4.2% headline and PPI at +6.5%. He cannot credibly signal a dovish tilt. "
               "For our rates positions (short 2Y, short 10Y), this is an honest headwind — we entered on a "
               "soft-inflation thesis that the CPI supported, but PPI complicates. We are not adding to either "
               "position. The stops (4.35% on 2Y, 4.65% on 10Y) are now risk-live and we respect them.")},
        {"q": "What's the Kharg Island story and why does it matter for oil?",
         "a": ("Trump vowed a third consecutive night of strikes on Iran and, in an extraordinary step, threatened "
               "to SEIZE Kharg Island — Iran's primary oil export terminal handling roughly 90% of Iran's crude "
               "exports (~2.5-3M bbl/day). A physical seizure of Kharg would be the largest single oil-supply "
               "shock in modern history; Brent would gap toward $110-130. Even as a threat, it has pushed Brent "
               "toward $95-100. Our Brent call spread's $100 strike is now only ~$5-6 away. The counterweight: "
               "the UAE and Iran held their first face-to-face meeting since the war began — a de-escalation channel. "
               "The correct framing is managed escalation with a credible right tail, not binary war/peace.")},
        {"q": "SpaceX is IPO-ing tomorrow — is it relevant to us?",
         "a": ("Directly relevant as a cross-market liquidity event, not as a holding. SpaceX priced at $135/share, "
               "~$1.77T valuation, ~$75B raise — the largest IPO in history. Nasdaq debut tomorrow under SPCX. "
               "(Source: CNBC.) The impact: $75B in capital is being allocated to a single new issue. That cash "
               "comes from existing equity holdings — mostly tech. Expect marginal selling pressure in AI/semis "
               "tomorrow as investors fund the allocation. It's not a fundamental catalyst, but it's a real "
               "liquidity drag that explains tomorrow's equity tape if tech underperforms without news.")},
        {"q": "Oracle beat everything — why is the stock down 7-11%?",
         "a": ("The market is pricing the capex bill, not the revenue beat. Oracle's RPO surged to $638bn — the "
               "largest AI backlog in enterprise software history. The demand is confirmed. But FY26 capex came "
               "in at $55.7bn (above the $50bn guide), then Oracle guided FY27 to $70bn PLUS $20-25bn component "
               "prepayments — ~$90-95bn in capital commitment in one year from a $70bn revenue company. To fund "
               "it: $40bn raise including $20bn in new shares. Capital and capacity problem, not a demand problem. "
               "The capital-protected note (idea 101) is the right instrument: 70-80% participation in the OCI "
               "re-rate, 100% capital protection against the dilution overhang.")},
        {"q": "The ECB hiked today — what happened and what does it mean for us?",
         "a": ("The ECB delivered exactly what the sell-the-fact trade required. It hiked +25bp to 2.25% — the "
               "first rate rise in nearly three years — explicitly citing Iran-war-driven inflation, with euro-area "
               "CPI at 3.2% in May. Then Lagarde said the ECB is 'not pre-committing to a particular rate path.' "
               "That phrase is the inflection: the spec community that had built EUR longs from 1.08 to 1.15 "
               "pricing in a full hike cycle now has no forward catalyst to keep holding. The sell-the-fact "
               "unwind has begun; EUR/USD is fading from ~1.15. On top of that, hot PPI (+6.5% YoY) forces the "
               "Fed's hand too — higher US rates for longer = wider USD carry advantage versus a pause-signalling "
               "ECB. MM-012 now has two confirmed tailwinds, not one speculative one. (Sources: CNBC, Bloomberg, "
               "Reuters, FXStreet.)")},
        {"q": "Adobe reports tonight — should I be doing something?",
         "a": ("No position before the print. The entry gate for the cash-secured put (idea 102) opens only "
               "after we see the number. If ADBE beats on AI ARR — software relief, we wait. If it misses on "
               "AI cannibalisation — ADBE trades down toward $330s and the CSP gets assigned at the $385 strike, "
               "owning shares at a discount. Pre-positioning is guessing. The discipline is to wait.")},
    ],

    "ideas_note": (
        "<p>Three confirmed catalysts shaping entry discipline. (1) <strong>Oracle note (idea 101)</strong> — "
        "window opened post-print; capex overhang is near-term noise against a $638bn RPO long-term thesis. "
        "(2) <strong>Brent call spread (idea 11)</strong> — $100 strike is ~$5-6 from spot on Kharg Island "
        "seizure threat; hold at current premium, do not chase. "
        "(3) <strong>Adobe CSP (idea 102)</strong> — gate opens tonight post-print only. "
        "ECB delivered +25bp today — <strong>MM-012 short-EUR/USD executing</strong> (sell-the-fact confirmed, "
        "Lagarde 'not pre-committing'). "
        "<strong>Rates ideas (short 2Y / short 10Y):</strong> hot PPI (+6.5% YoY) is a genuine headwind — "
        "do NOT add size. Stops at 4.35% (2Y) and 4.65% (10Y) are risk-live ahead of FOMC Jun 16-17.</p>"
    ),

    "event_radar_note": (
        "<p>Four of six catalysts are confirmed: CPI Jun 10 (hot 4.2% headline ✓), Oracle Jun 10 AH "
        "(capex panic selloff ✓), PPI Jun 11 (HOT +1.1% MoM / +6.5% YoY — hawkish ✓), and ECB Jun 11 "
        "(DELIVERED ✓ — +25bp to 2.25%, Lagarde 'not pre-committing', sell-the-fact confirmed). Two remain: "
        "Adobe tonight's close (AI tax or tailwind — CSP entry gate opens post-print only), and "
        "Kevin Warsh's first FOMC dot plot June 16-17 (now MORE hawkish given PPI heat — "
        "hike-bias vs data-dependent-hold asymmetry). The book's rates pre-positions are facing headwind; "
        "stops are risk-live. No additional action before the Adobe print.</p>"
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
        "Three things confirmed today, one still in question. Confirmed: ECB delivered +25bp to 2.25% with "
        "a pause signal — MM-012 sell-the-fact executing with dual tailwind (ECB pause + hot PPI USD support). "
        "Confirmed: hot PPI +6.5% YoY is a genuine headwind for the short-2Y and short-10Y positions — do NOT "
        "add; stops at 4.35% / 4.65% are risk-live. Confirmed: Kharg Island seizure threat upgrades Brent's "
        "right tail — call spread $100 strike within reach, hold. In question: FOMC Jun 16-17 — Warsh faces "
        "CPI 4.2% + PPI 6.5%; hawkish surprise risk is higher, not lower. "
        "For the rest of June: let the derivatives (Brent spread, SPX put spread) carry P&L, "
        "execute the Oracle note and Adobe CSP post-print on their own entry triggers, "
        "and do not open new directional bets until after June 17."
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
