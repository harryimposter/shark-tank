#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-07-14 (Tuesday; PRE-MARKET into CPI + big-bank earnings). THE TOLL AND THE TRAP.

THE NEXT CHAPTER vs the Jul 13 (The Strait Shuts) run:
the reprice the reopen began did not de-escalate overnight — it ESCALATED. Trump reimposed the naval blockade
AND announced a 20% toll on ALL cargo transiting Hormuz ("Guardian of the Strait"); Brent posted its biggest
single-day gain in over six years (+9.59% to a $83.30 settle); the KOSPI CRASHED -8.95% on a chip rout. And it
all lands into an 08:30 ET June CPI — a BACKWARD-LOOKING print blind to July's $84 oil — reported the same
morning as the big-bank Q2 kickoff. The maximum-divergence day: a disinflation print into an inflation shock.
- THE 20% HORMUZ TOLL — a self-inflicted cost-push tax. On Truth Social (Jul 13) Trump said the US is
  "resuming the 'Iran Blockade'" and will charge "at the rate of 20% on all cargo shipped" through the Strait,
  calling the US the "Guardian of the Strait of Hormuz." The blockade resumes Tue Jul 14 4pm ET (CENTCOM).
  Citi: the toll "materially raises the risk of further military escalation." A tariff on ~1/5 of world oil,
  landing as inflation the CPI can't see. (Euronews, CNBC, Bloomberg, NPR, Axios.)
- THE WAR ESCALATED FURTHER. A third night of US strikes hit Bandar Abbas, Kish, Qeshm and Abu Musa; Iran
  said it struck/disabled two "rogue supertankers" — the UAE confirmed Iranian missiles hit two tankers in
  Omani waters, killing one crew member. The April-era ceasefire has effectively collapsed. (CNN, Al Jazeera.)
- OIL'S BIGGEST DAY IN SIX YEARS. Brent settled +9.59% at $83.30 (Mon) — its biggest single-day % gain in
  6+ years — WTI +~4%. Pre-market Tue: Brent Sep ~$84.84 (+1.85%), WTI Aug ~$79.78 (+2%). The Brent–WTI spread
  is widening (seaborne premium; refs $2→$9) — MM-044 (the Jul 13 widener) is VINDICATED. (CNBC, Al Jazeera.)
- GOLD FELL AGAIN. Gold dropped ~2.9% to ~$4,001-4,020 (Mon) — a SECOND down day — as the 10Y rose 6bp to
  ~4.62% and the war re-armed inflation/higher-for-longer. The war STILL trades as a real-rates short for gold,
  not a haven. MM-005 (cash gold) is deep underwater; min-hold to ~Jul 15 (tomorrow). (Trading Economics, tmgm.)
- THE CHIPS CRASHED. KOSPI -8.95% (near circuit-breaker), KOSDAQ -4.55%; SK Hynix -15.46%, Samsung -10.53%,
  SK Square -17.67%. Korea Investment CUT SK Hynix's Q2 op-profit outlook ~8% below consensus (HBM4 shipments
  slower) — the glut/demand crack showing in ESTIMATES now, not just price. Nikkei -1.92%. The Burry tell is
  deepening; the book is 30% Micron. (Seoul Economic Daily, CNBC.) Prior close (Mon Jul 13): S&P 7,515.34
  (-0.79%), Nasdaq Comp 25,873.18 (-1.55%), Dow 52,498.64 (-0.26%), VIX ~16.2, Brent $83.30, gold ~$4,010.
- THE HAWK IS RE-ARMED — AND WALLER SAID IT. Waller: the Fed should hike "in the near term" if this week's CPI
  and PPI are "hot." Sept hike ~64%, hike-this-year still priced; 10Y ~4.62%, 2Y ~4.28%, 2s10s ~+34bp.
  (Wolf Street, CME FedWatch.)
- THE CPI IS A BACKWARD-LOOKING TRAP — PENDING. June CPI Tue Jul 14 8:30 ET (cons: headline −0.1% m/m →
  ~3.9% y/y, driven by a ~10% June gasoline DROP from the mid-June ceasefire; core +0.2-0.3% m/m → ~2.9% y/y).
  June was the calm month — the print contains NONE of July's $84 Brent or the 20% toll. The trap is a soft
  headline that sparks a dip-buy while core stays sticky and July's oil re-arms the NEXT print. (BLS, Kiplinger.)
- BIG-BANK EARNINGS SAME MORNING — PENDING. Tue Jul 14 BMO: JPM (~$5.74, implied move ~4.4%), GS (~$14.46,
  +32% IB fees y/y, implied move ~6.0%), C (~$2.76, ~5.5%), BAC (~$1.13, ~4.5%), WFC (~$1.73, ~5.5%); Jul 15
  MS/BLK/BNY. A steeper curve = NIM tailwind, but same-day CPI + a war gap can swamp any print. (Finnhub, Zacks.)
- BOOK ACTION: the oil hedge had its best day in years — TotalEnergies + MM-044 (Brent–WTI) lead, Jul 11's SPX
  put spread and EUR/USD put spread still work. The AI sleeve is in a genuine chip CRASH (KOSPI -9%, an analyst
  cutting SK Hynix numbers = the second, bigger crack). Fresh ideas press the NEW information (the toll, the
  print-vs-reality gap, the chip catch-down): long US 5Y breakeven inflation (the toll the CPI can't see), a
  banks-vs-chips RV (long XLF vs short SMH), a semis put spread (the US catch-down to the KOSPI crash), and long
  USD/KRW (the EM oil-importer hit by both the toll and the equity outflow).

Run:  python gen_2026_07_14.py
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
# Fallback: this is a Tuesday PRE-MARKET brief (US cash open ~09:30 ET) into an 08:30 ET CPI. Cash indices
# have not printed the new session yet, and if the live feed does not resolve a futures proxy, inject the
# web-verified Mon Jul 13 closes (CNBC + Yahoo + Motley Fool, corroborated) so the dashboard headline indices
# never render "unverified". Only set if the live feed did not resolve them; direction is risk-off (oil bid,
# chips crashing, CPI + banks the two-sided catalyst).
if "spx" not in snap:
    snap["spx"] = {"close": 7515.34, "chg_pct": -0.79, "chg_abs": -59.85}
if "dji" not in snap:
    snap["dji"] = {"close": 52498.64, "chg_pct": -0.26, "chg_abs": -138.37}
levels = live_levels.trade_levels(snap)
# Option spreads have no live feed — the fresh index/vol/FX/commodity expressions (MM-040..043) are
# marked from spot; no live option line is open this refresh.

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
    "MU":   "The name in the eye of the chip crash — and the book's largest weight (~30% of the Fable book). Monday the "
            "SK Hynix rout went from a wobble to a crash: KOSPI -8.95%, SK Hynix -15.46%, Samsung -10.53%, and Korea "
            "Investment CUT SK Hynix's Q2 op-profit ~8% below consensus on slower HBM4 shipments — the glut/demand crack "
            "showing up in ESTIMATES, not just price. That is the Burry tell made literal, and Micron is the single best "
            "expression of the 'broken chip cycle' bet. The discipline hardens: monetise the still-rich IVol into ANY "
            "bounce (collar/overwrite) now that the second, bigger crack has printed — never add into the largest weight.",
    "NVDA": "The AI leader dragged down by the cohort, not leading it. A war-driven risk-off plus an oil cost-push that "
            "backs real yields up (10Y ~4.62%) is a direct hit to the long-duration AI-capex trade, and the Korea crash "
            "is the read-through. At ~32x it is the reasonably-priced leg against the ~175x AMD challenger, so it holds "
            "up better on a relative basis — own the leader against the overbought name (the dispersion RV) and against "
            "the semis complex via the fresh long-XLF/short-SMH RV (MM-049), do not fight the whole cohort lower.",
    "AMD":  "The overbought casualty and the SHORT leg of the chip dispersion. Up ~150% YTD at ~175x trailing earnings "
            "versus NVDA's ~32x on a fraction of the revenue base — the richest name in the cohort the market is now "
            "de-risking hardest as the KOSPI crash bleeds into US semis. The Fable book HOLDS AMD (+394%), so the trim "
            "doubles as concentration management: sell the exhausted winner into any bounce, own the cheaper leader, and "
            "own the catch-down of the whole complex with the defined-risk semis put spread (MM-050).",
    "XLE":  "The one part of the tape with its best day in years. Brent settled +9.59% at $83.30 (Mon) — its biggest "
            "single-day gain in 6+ years — as Trump reimposed the blockade and slapped a 20% toll on ALL Hormuz cargo. "
            "The book's energy length (TotalEnergies) is the war hedge that had a monster session; the fresh upside is "
            "the waterborne premium — long Brent vs WTI (MM-044, VINDICATED, spread widening) — not more spot into a "
            "binary-on-Trump tape.",
    "GLD":  "Still the haven that will not show up. Gold FELL ~2.9% to ~$4,001-4,020 (Mon) — a SECOND down day — as the "
            "10Y rose 6bp to ~4.62% and the toll re-armed inflation/higher-for-longer, so gold traded as a real-rates "
            "short, not a war hedge. The book's cash gold long (MM-005) is deep underwater on its min-hold (to ~Jul 15, "
            "tomorrow). The coil is still the trade: if the war deepens into a growth scare that forces the Fed dovish, "
            "the real-rate cap breaks — own that tail with the defined-risk Sep call spread (MM-046), not more spot.",
    "TLT":  "The oil cost-push is duration's enemy, and now there's a toll on top. The 10Y rose 6bp to ~4.62% and the "
            "front firmed as the 20% Hormuz toll re-lit inflation risk and Waller said the Fed should hike 'in the near "
            "term' if CPI/PPI run hot — so the short-10Y (MM-004) is the laggard and the short-2Y (MM-013) is offside. "
            "Own the curve SHAPE (the steepener MM-009, ~+34bp) and the inflation the print can't see (long 5Y "
            "breakevens, MM-048), not outright long-end duration, into a backward-looking June CPI.",
    "HYG":  "The laggard still catching up. Oil, the dollar, rates and equity vol have all repriced the war; HY credit "
            "spreads have moved less — a growth scare from a 20% oil-transit toll and a chip crash is exactly what "
            "widens spreads, and credit is late. Own the tail with long HY protection / short HYG (MM-047, held from "
            "Jul 13); it is the cross-asset completion of the 'war under-priced' thesis, in the market that moves last.",
    "XLF":  "The cohort that reports into the collision — and the one the war HELPS. Big banks kick off Q2 season Tue "
            "Jul 14 BMO (JPM, GS, C, BAC, WFC) into a steeper curve (2s10s ~+34bp = NIM support), the one equity cohort "
            "the war-driven steepening benefits. GS carries the widest implied move (~6.0%); own the earnings-vol leader "
            "with defined risk (MM-043 held) and the banks-vs-chips story via the fresh long-XLF/short-SMH RV (MM-049) — "
            "long the cohort the curve helps, short the one crashing.",
    "SMH":  "The US catch-down leg. The KOSPI crashed -8.95% (SK Hynix -15%, Samsung -10%) but US semis have not fully "
            "repriced the Korea rout, the toll or the CPI risk, and index vol is cheap (VIX only ~16). Own the "
            "catch-down with a defined-risk semis put spread (MM-050) and as the SHORT leg against banks (MM-049) — the "
            "cohort the war-steepening hurts against the one it helps.",
    "SPY":  "The complacency trade still repricing. The war escalated further Monday (blockade + 20% toll) and the S&P "
            "fell 0.79% to 7,515 — but VIX is only ~16 into a two-sided June CPI and the bank kickoff. The SPX put "
            "spread (MM-041, held from Jul 11) owns exactly this — the gap the record tape ignored, still printing as "
            "the war deepens and the CPI trap looms.",
    "EEM":  "Korea is the epicentre. The KOSPI crashed -8.95% (near a circuit breaker), SK Hynix -15%, Samsung -10%, as "
            "the chip rout and the oil-importer's 20%-toll terms-of-trade shock collided; the Nikkei fell -1.92%. EM "
            "Asia is where the AI-durability crack and the war premium hit hardest — express it cleanly in FX via long "
            "USD/KRW (MM-051), the oil-importer hit by both the toll and the equity outflow.",
    "BTC":  "Bitcoin still capped, not the haven in a war either — the same backing-up-real-rates regime that sank gold "
            "keeps a lid on the speculative long tail, and a risk-off tape pulls it with the Nasdaq, not against it. A "
            "tell that in this regime the only havens paying are the dollar and oil, not duration, gold or crypto. Not "
            "a book position.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("The Toll and the Trap: Trump Taxes Hormuz as June CPI Prints the Calm Before It — Brent's Biggest Day in "
          "Six Years and a 20% Oil-Transit Toll Collide With a Backward-Looking Disinflation Print and the Big-Bank "
          "Tape, While Korea's Chips Crash 9%")
regime_note = (
    "The most important thing that happened yesterday is that the war did not de-escalate — it escalated into a tax, "
    "and the single most inflationary event of the year lands on the same morning as the most disinflationary data "
    "print of the year. On Truth Social Monday, Trump reimposed the naval blockade of Iranian ports AND declared the "
    "US will charge 'at the rate of 20% on all cargo shipped' through the Strait of Hormuz, casting the United States "
    "as the self-appointed 'Guardian of the Strait.' A third night of US strikes hit Bandar Abbas, Kish, Qeshm and "
    "Abu Musa; Iran said it disabled two 'rogue supertankers' and the UAE confirmed Iranian missiles hit two tankers "
    "in Omani waters, killing a crew member. Brent answered with its biggest single-day percentage gain in over six "
    "years, +9.59% to a $83.30 settle; pre-market it trades ~$84.84. (Euronews, CNBC, Bloomberg, CNN, Al Jazeera.) "
    "Decompose what the toll actually is. The consensus files it as another war headline to look through. The anatomy "
    "says it is a structural cost-push the market has never priced before: a 20% tariff on roughly a fifth of the "
    "world's seaborne oil, imposed by the United States itself, mechanically lifting the delivered price of every "
    "barrel that clears Hormuz — and Citi's own read is that it 'materially raises the risk of further military "
    "escalation.' This is not a supply scare that de-escalation reverses cleanly; it is a toll with a price tag "
    "attached, and it lands into a June CPI that cannot see a cent of it. So what, who's wrong, what's the trade: the "
    "crowd is about to trade a June print that measured the calm, and the trade is to own the inflation the print is "
    "structurally blind to — breakevens, the waterborne barrel, the curve — not the headline. (CNBC, Wolf Street.) "
    "The second-order effect consensus is missing is the maximum-divergence trap Tuesday morning. June was the calm "
    "month: gasoline fell ~10% on the mid-June ceasefire, so the consensus June headline is −0.1% m/m (~3.9% y/y) — "
    "mechanically soft, containing none of July's $84 Brent or the 20% toll. The danger is a tape that gaps on the "
    "war, then rallies on a soft headline it misreads as disinflation, while core holds +0.2-0.3%, Waller says the "
    "Fed should hike 'in the near term' if CPI/PPI run hot, and July's oil already re-arms the next print. The Papic "
    "constraint is sharper than a binary now: Trump owns the strike, the blockade AND the toll — the oil premium is "
    "not a market variable, it is a policy lever he pulls, and he has just monetised it. The Burry tell stopped being "
    "a forecast and printed in estimates: Korea Investment cut SK Hynix's Q2 operating profit ~8% below consensus on "
    "slower HBM4 shipments, the KOSPI crashed 8.95%, SK Hynix fell 15% and Samsung 10% — the glut/demand crack the "
    "capacity race was always going to produce, now visible in the numbers, not just the price. The book is 30% "
    "Micron; this is the second, bigger crack. "
    "The book sits astride the reprice and the oil hedge just had its best day in years. TotalEnergies and the Jul 13 "
    "Brent–WTI widener (MM-044) lead as crude posted a six-year single-day record; Jul 11's SPX put spread (MM-041) "
    "and EUR/USD put spread (MM-042) still work on the risk-off and the haven dollar; the 2s10s steepener (MM-009) "
    "holds ~+34bp as the one rate expression the toll confirms, while the short-10Y (MM-004) and short-2Y (MM-013) "
    "lag as yields back up and gold (MM-005) fell a second day. Short EUR/USD (MM-012) works. The trade now is to "
    "press the NEW information: own the inflation the CPI is blind to (long 5Y breakevens), own the one equity cohort "
    "the war-steepening helps against the one it is crashing (long XLF vs short semis), own the US catch-down to "
    "Korea's crash (a semis put spread), and own the EM oil-importer hit by both the toll and the outflow (long "
    "USD/KRW). The regime is no longer 'the tape is being forced to price a war.' It is a market that must reconcile "
    "the most inflationary policy shock of the year with the most disinflationary data print of the year, in the same "
    "eight-thirty minute — and the trap is that the backward-looking number wins the morning while the toll wins the "
    "quarter."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# No close action today. MM-005 (gold) stays open on its 45-day min-hold (to ~Jul 15, now 1 day out) though
# spot is well below the $4,250 stop — the rule holds it to the decision date; the June CPI print lands the day
# before. MM-009 min-hold (to ~Jul 16) still governs. All other legs inside their stops/min-holds.

# ── Per-trade enrichment ────────────────────────────────────────────────────────
TRADE_ENRICHMENTS = {
    "MM-2026-001": {
        "instrument": (
            "EUR/AUD spot FX cross-rate. EUR = euro (ECB-managed); AUD = Australian dollar "
            "(commodity-linked, RBA-managed). Driven by relative ECB-vs-RBA rate paths, iron-ore "
            "prices (Australia's largest export = AUD tailwind), global risk sentiment, and the "
            "2-year eurozone-vs-Australia rate spread."
        ),
        "fundamental_thesis": (
            "The quiet leg, roughly flat near the entry as two forces cancel. The war-driven risk-off pressures the "
            "commodity-AUD (good for the short), but an $84 Brent and a broad commodity bid lift the AUD's terms of "
            "trade the other way, pinning the cross mid-range rather than toward the 1.61 target. A paused ECB caps the "
            "EUR side; there is no dated EUR catalyst left and the edge has thinned. This is the leg to trim into any "
            "risk-off AUD weakness rather than defend into a war-premium AUD bid. Stop 1.662, close by."
        ),
        "catalysts": [
            "ECB pause fully in the price — no forward EUR catalyst",
            "AI-led risk-on melt-up — rebuilds the commodity-AUD bid, the force AGAINST the short",
            "RBA path — a hawkish hold supports AUD vs a paused ECB",
            "Iron ore / China demand — the AUD swing factor",
        ],
        "risks": (
            "The risk-on melt-up keeps bidding AUD and the cross runs the 1.662 stop; a firm China read lifts iron "
            "ore; an ECB official re-opens the hike door and EUR squeezes higher. Stop 1.662 (close)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the cross still sits above where the 2yr spread implies with a paused ECB, but AUD's "
                            "own risk-on/commodity bid has narrowed the edge.",
            "catalyst":     "1/2 — the dated ECB catalyst has passed; what remains is slower-burn (RBA, China).",
            "positioning":  "1/2 — EUR longs trapped flat offer some unwind fuel; AUD positioning is light.",
            "confirmation": "0/2 — the cross has drifted, not fallen; no confirmation of the short.",
            "stop_quality": "1/1 — 1.662 is a clean technical level, now close — the discipline mechanism.",
        },
    },
    "MM-2026-004": {
        "instrument": (
            "US 10-year Treasury yield. Shorting the yield = buying duration (long bonds / 10Y "
            "futures / TLT). Driven by the Fed path (front-end anchored), inflation expectations, "
            "fiscal supply/term premium, and the safe-haven bid."
        ),
        "fundamental_thesis": (
            "The laggard, and the cleanest tell that this war bids oil, not bonds. The 10Y rose another 6bp to ~4.62% "
            "from the 4.44% entry as Trump's 20% Hormuz toll sent Brent to a six-year single-day record and re-armed "
            "the inflation trade — a shooting war produced NO haven bid for duration, because a cost-push, and now a "
            "literal oil-transit tax, is bearish bonds. The disinflation thesis is on the wrong side of a live oil "
            "shock, a Waller 'hike in the near term' warning, and a CPI print (this morning) that can't see July's oil "
            "or the toll. The expression that pays is the curve (MM-009), not outright long-end duration; the "
            "inflation itself is owned via breakevens (MM-048). Stop 4.65%, now ~3bp away — a very tight rein."
        ),
        "catalysts": [
            "June CPI Tue Jul 14 08:30 ET (core +0.2-0.3% m/m cons) — the print that confirms or breaks the long-end backup",
            "The 20% Hormuz toll / $84 Brent — the fresh, structural cost-push pinning the 10Y",
            "Treasury supply + term premium — the anchor keeping the long end heavy",
            "A Hormuz de-escalation / toll withdrawal — the disinflation relief that would let the 10Y rally",
        ],
        "risks": (
            "A hot core CPI plus the toll-driven oil premium sells the long end toward and through the 4.65% stop; only "
            "a clean de-escalation and a soft CORE rescue it. Stop 4.65% (now ~4.62%, ~3bp away)."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the disinflation gap the trade was built on has narrowed against a live oil "
                            "cost-push; the mispricing is now thin and CPI-dependent.",
            "catalyst":     "1/2 — the CPI is the dated catalyst, but it is a two-sided risk to this leg, not a tailwind.",
            "positioning":  "1/2 — the crowd is still short duration; the war/oil backup is going the crowd's way, not ours.",
            "confirmation": "0/2 — the 10Y backed UP, not down; the tape is not confirming the long.",
            "stop_quality": "1/1 — 4.65% is a clear technical level; ~9bp of risk — a tight leash.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold in USD. The inverse of real rates, driven by the Fed path "
            "and real yields, USD strength, EM central-bank buying, geopolitical premia, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "The trade the war keeps refusing to save. Gold FELL a second day to ~$4,001-4,020, now underwater ~-11% "
            "from the $4,523 entry, because the 10Y rose 6bp to ~4.62% on the toll's inflation impulse and gold trades "
            "as a real-rates SHORT, not a haven. The lesson holds and hardens: a 20% oil-transit tax is inflationary, "
            "which lifts real yields, which caps gold — bullion needs a lower-real-rate path, not a bigger war. The "
            "min-hold (to ~Jul 15, tomorrow) now sits one day past June CPI, so the print decides the exit. The "
            "asymmetric upside — a war that deepens into a growth scare and forces the Fed dovish — is owned with "
            "DEFINED risk via the Sep call spread (MM-046), not by adding underwater spot. Stop $4,250 (price well "
            "below it; the rule holds it to the decision)."
        ),
        "catalysts": [
            "June CPI Tue Jul 14 08:30 ET — a soft CORE is the real-rates relief gold needs; a hot one confirms the exit",
            "Real yields / the 10Y at ~4.62% — the headwind that keeps gold capped through the war",
            "The 20% Hormuz toll — inflationary, so it lifts real yields and caps the debasement bid",
            "EM / central-bank physical buying — the structural floor under the drawdown",
        ],
        "risks": (
            "A hot CPI plus the toll-driven yield backup keeps gold well below the $4,250 stop and the ~Jul 15 min-hold "
            "exit crystallises the loss; only a soft CORE and a real-rate turn rescue it. Min-hold to ~Jul 15; stop "
            "$4,250 (price now well below it — the rule holds it to the decision date)."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the real-rates engine turned AGAINST gold this week; the debasement gap is intact "
                            "structurally but the cyclical driver is a headwind into CPI.",
            "catalyst":     "1/2 — the CPI is the dated catalyst but it is two-sided; the war did not become one.",
            "positioning":  "1/2 — spec length was washed out; positioning is clean but there is no squeeze without a rate turn.",
            "confirmation": "0/2 — gold fell on the war and the yield backup; no confirming move.",
            "stop_quality": "1/1 — $4,250 is a defined level; the min-hold rule governs the decision date.",
        },
    },
    "MM-2026-007": {
        "instrument": (
            "USD/JPY spot FX (dollar-yen). Driven by the US-Japan 2yr rate differential, BoJ "
            "normalisation, the Fed path, risk sentiment (JPY is a crisis safe-haven), and Japanese "
            "MoF intervention risk near ~160-163."
        ),
        "fundamental_thesis": (
            "Offside and pressured by the haven bid. USD/JPY sits ~162.1, above the 159.37 entry (~-1.7%), as the "
            "war-driven risk-off bought the DOLLAR, not the yen — Japan is a net energy importer, so an $84 Brent and "
            "a 20% Hormuz toll are a yen NEGATIVE, and the oil-led yield backup re-widened the US-Japan differential. "
            "The yen is the funder in this war, not the haven. The structural case (a BoJ normalising toward 1.00%, a "
            "Fed that cannot sustain a hawkish repricing into a labour crack) is intact but on hold, and the MoF line "
            "near 163 is the backstop. The cleaner war-haven expression is long CHF/JPY (MM-045); the sharper "
            "oil-importer expression is long USD/KRW (MM-051). Patient short on a tight leash; 163 is the stop, now "
            "~0.9pt away."
        ),
        "catalysts": [
            "June CPI Tue — the print that decides whether the US-Japan differential widens or narrows",
            "$84 Brent + the 20% toll — the terms-of-trade drag on the energy-importing yen, widening the differential against the short",
            "MoF intervention near the 163 line — the official backstop above",
            "Oil-led yield backup + haven-dollar bid — the forces working against the short",
        ],
        "risks": (
            "A hot US CPI re-widens the differential and pushes USD/JPY toward the 163 stop; the haven-dollar bid keeps "
            "the carry alive. Stop 163.00 (now ~162.4, ~0.6 pts away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is above 2yr-differential fair value, but the differential re-widened on the "
                            "oil-led backup, narrowing the near-term edge.",
            "catalyst":     "1/2 — the CPI is the dated catalyst but two-sided; long CHF/JPY (MM-045) is the cleaner haven expression.",
            "positioning":  "1/2 — the yen carry is still crowded long-USD; the unwind needs a rate-path turn.",
            "confirmation": "0/2 — the yen weakened as the risk-off bought the dollar, not the yen; no confirming move.",
            "stop_quality": "1/1 — 163.00 is a clean MoF-intervention ceiling; ~0.6 pts risk.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (receive/own cut optionality), short "
            "the 10Y (short fiscal-supply risk). Pays when 10Y-minus-2Y widens. Currently ~2Y 4.25% "
            "/ 10Y 4.62%, spread ~+34bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "The best position in the book and the one expression the toll confirms. Both ends are up on the oil "
            "cost-push — the 2Y ~4.28%, the 10Y ~4.62% — but the spread widened to ~+34bp, keeping the open gain near "
            "~+125% off the +15bp entry (an 18-month inversion). This is the right trade for the whole regime: a Fed "
            "boxed between a labour crack and a toll-driven oil-CPI can neither hike hard nor cut, which pins the "
            "front, while fiscal supply and the war's inflation premium keep the long end heavy — a structural "
            "steepener in either CPI outcome (a soft headline bull-steepens the front; a sticky core bear-steepens the "
            "back). Min-hold to ~Jul 16; target +60bp; held, trail the stop up, do not add into the run."
        ),
        "catalysts": [
            "June CPI Tue — a hot core steepens via the long end; a soft one steepens via the front (bull-steepen)",
            "Oil cost-push + Treasury supply — the term premium keeping the back end heavy = steeper",
            "A 35% Canada tariff (Aug 1) — a fresh cost-push that pressures the long end",
            "A hot-enough CPI that re-arms a near-term hike and bear-flattens the front — the risk",
        ],
        "risks": (
            "A CPI hot enough to re-price a July/September hike backs up the FRONT end faster than the back and "
            "bear-flattens the curve; a global risk-off bid flattens via the long end. Stop: spread below -10bp "
            "(now ~+35bp)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve is still underpriced vs the late-cycle mean off an 18-month inversion; the "
                            "re-steepening has room to the +60bp target.",
            "catalyst":     "2/2 — the CPI steepens the curve in either direction the trade cares about; supply keeps the back heavy.",
            "positioning":  "1/2 — front-end positioning is two-way post-payroll/oil; the steepener is the consensus-agnostic expression.",
            "confirmation": "2/2 — the spread held ~+35bp through a week of backing-up yields; the steepen is durable.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "Working on the haven dollar. EUR/USD sits ~1.1390 and DXY firm ~100.9 as the escalation bought the dollar "
            "for safety and the oil-led yield backup (10Y ~4.62%) widened the rate differential — and an $84 Brent "
            "plus a 20% Hormuz toll is a euro-negative terms-of-trade shock, because the euro area imports its energy. "
            "The short is green (~+1.8% from the 1.16 entry) with a distant 1.182 stop. June CPI (this morning) is the "
            "swing: a hot core extends the dollar; a soft headline the market misreads as dovish is the trim risk. Hold "
            "the core short; own the specific hot-CPI/haven-dollar upside via the defined-risk put spread (MM-042, held)."
        ),
        "catalysts": [
            "June CPI Tue — a hot core re-arms the Fed and bids the dollar; a soft one revives the euro",
            "Brent ~$84 + the 20% toll — the euro-negative terms-of-trade shock supporting the short",
            "DXY firm ~100.96 on the haven bid — the dollar back in the short's favour",
            "ECB on hold — the paused EUR side vs a Fed that cannot fully commit to cuts",
        ],
        "risks": (
            "A soft CPI revives the dollar roll and EUR/USD squeezes toward 1.16+; a clean Hormuz de-escalation drops "
            "oil and lifts the euro's terms of trade. Stop 1.182 (distant)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the oil terms-of-trade shock and a stalled dollar top restore part of the "
                            "rate-differential edge the Jul 3 roll had removed.",
            "catalyst":     "2/2 — the CPI is the dated, live catalyst; the oil premium is the euro-negative support.",
            "positioning":  "1/2 — a crowded short-EUR is unwind fuel on a soft CPI, but the oil shock caps the squeeze.",
            "confirmation": "1/2 — EUR/USD stalled near 1.14 and the dollar held 101; a first re-confirming leg.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; the position has a comfortable cushion.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receive 2Y swap / long 2Y notes). The 2Y is the market's "
            "real-time forecast of the Fed path over two years — the most policy-sensitive point on the "
            "curve."
        ),
        "fundamental_thesis": (
            "Offside on the oil re-arm. The 2Y firmed to ~4.28%, above the 4.162% entry (~flat-to-red), as the toll, an "
            "$84 Brent cost-push and Waller's 'hike in the near term' warning re-priced near-term hike risk against the "
            "short. The thesis — that the front end over-prices a 2026 hike into a cracking labour market — is intact "
            "structurally, but the war is going the crowd's way, not ours, in the near term. June CPI (this morning) is "
            "the decider: a soft core re-confirms the fade; a sticky one plus the oil premium backs the 2Y toward the "
            "4.35% stop. Min-hold elapsed; stop 4.35%. Hold on a tight rein; the curve (MM-009) is the "
            "higher-conviction, consensus-agnostic expression of the same view."
        ),
        "catalysts": [
            "June CPI Tue — the decider: soft re-confirms the fade, hot re-arms the hike",
            "Oil cost-push (~$84 Brent + the 20% toll) — the fresh inflation risk backing up the 2Y",
            "Waller: hike 'in the near term' if CPI/PPI run hot — the hawkish anchor the trade fades",
            "The next labour print — the crack that ultimately prices the hike out",
        ],
        "risks": (
            "A hot CPI plus a sustained oil premium re-prices a 2026 hike and backs the 2Y up to the 4.35% stop. Stop "
            "4.35% (now firmer, above the 4.162% entry)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the 2Y still over-prices a hike into a labour crack, but the oil cost-push narrows "
                            "the near-term gap.",
            "catalyst":     "1/2 — the CPI is dated and decisive, but a two-sided risk to this leg rather than a tailwind.",
            "positioning":  "1/2 — front-end positioning swung back toward hawkish on the oil re-arm; less squeeze fuel than Jul 2.",
            "confirmation": "0/2 — the 2Y backed UP to the entry; the tape is no longer confirming the fade this week.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~14bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-048": {
        "instrument": (
            "Long US 5-year breakeven inflation — buy 5Y TIPS, sell nominal 5Y Treasuries (or the equivalent inflation "
            "swap). The breakeven is the market's priced inflation rate; it rises when the market lifts its inflation "
            "expectations. A 20% toll on ~1/5 of world seaborne oil is a mechanical, structural cost-push that a "
            "backward-looking June CPI cannot capture — the cleanest expression of 'own the inflation the print is "
            "blind to.'"
        ),
        "fundamental_thesis": (
            "The marquee fresh idea: the most inflationary policy shock of the year lands the same morning as the most "
            "disinflationary data print of the year, and breakevens are the instrument that owns the gap. Trump's 20% "
            "Hormuz toll and an $84 Brent are a delivered-price cost-push on a fifth of world oil; June CPI, measured "
            "in the calm pre-toll month, prints soft (−0.1% headline on a 10% June gasoline drop). If the tape misreads "
            "the soft headline as disinflation and breakevens sit still, the trade owns the re-arm; if the market wakes "
            "to the toll, breakevens widen directly. It is the rates-market completion of the same thesis the curve "
            "(MM-009) and the oil widener (MM-044) express."
        ),
        "catalysts": [
            "The 20% Hormuz toll + $84 Brent — a structural, delivered-price cost-push",
            "June CPI Tue 08:30 ET — a backward-looking soft headline that under-prices the forward inflation",
            "Waller: hike 'in the near term' if CPI/PPI run hot — the Fed acknowledging the risk",
            "July PPI + the next CPI — the prints that will contain the toll the June one can't",
        ],
        "risks": (
            "A genuine de-escalation and toll withdrawal drains the oil premium and breakevens compress; a growth scare "
            "severe enough to crush demand expectations can pull breakevens down even with high spot oil. Stop: 5Y "
            "breakeven back through its pre-escalation level."
        ),
        "breakdown_why": {
            "gap":          "3/3 — a 20% toll on a fifth of world oil is a structural cost-push breakevens have not "
                            "priced while the market fixates on a backward-looking June headline.",
            "catalyst":     "2/2 — the toll is live and the CPI is dated this morning; both fire on the trade.",
            "positioning":  "1/2 — the market is positioned for disinflation into a soft June print; the re-arm is the pain trade.",
            "confirmation": "1/2 — oil, the curve and the dollar already price the inflation impulse; breakevens lag — one confirming leg.",
            "stop_quality": "1/1 — a clean pre-escalation breakeven level as the failure threshold.",
        },
    },
    "MM-2026-049": {
        "instrument": (
            "Long XLF (US banks/financials) vs short SMH (US semiconductors) — a beta-neutral equity sector RV. Banks "
            "report Q2 into a steeper curve (2s10s ~+34bp) that lifts net-interest margin — the one cohort the "
            "war-driven steepening HELPS; semis are the cohort the KOSPI's -8.95% crash and the AI-glut crack are "
            "hitting hardest. The pair owns the two dominant stories of the day in one low-index-beta expression."
        ),
        "fundamental_thesis": (
            "The cleanest banks-vs-chips expression of the split tape. The same regime that crushes semis — a war-driven "
            "steepening, an oil cost-push, real yields backing up — is the regime that helps banks, because a steeper "
            "curve is a NIM tailwind and the big-bank cohort reports into it this morning (GS +32% IB fees, the widest "
            "implied move). Meanwhile the KOSPI crash and Korea Investment's SK Hynix profit cut are the glut crack the "
            "US semis complex has not fully repriced. Long XLF / short SMH owns the divergence with little index beta — "
            "a relative-value trade on which cohort the toll-and-curve regime rewards and which it punishes."
        ),
        "catalysts": [
            "Big-bank Q2 kickoff Tue BMO (JPM, GS, C, BAC, WFC) into a +34bp curve — the NIM tailwind",
            "KOSPI -8.95% / SK Hynix -15% / Korea Investment profit cut — the glut crack hitting semis",
            "The 20% toll / oil-led steepening — helps banks, hurts long-duration semis",
            "June CPI — a hot core steepens further (banks win); a soft one is neutral-to-both",
        ],
        "risks": (
            "A bank earnings miss (credit build, IB disappointment) with a semis bounce inverts the pair; a soft-CPI "
            "risk-on rally lifts semis harder than banks. Beta-neutral construction bounds the index risk. Stop: the "
            "XLF/SMH ratio back through its pre-earnings level."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the market treats banks and semis as one 'risk' bucket; the toll-and-curve regime "
                            "splits them and the pair is under-owned.",
            "catalyst":     "2/2 — bank earnings and the chip crash are both live and dated this morning.",
            "positioning":  "1/2 — the crowd is long semis (AI) and light banks; the rotation is the pain trade.",
            "confirmation": "2/2 — the curve is steepening and the KOSPI crashed; both legs are already moving in the trade's favour.",
            "stop_quality": "1/1 — a clean ratio stop at the pre-earnings level.",
        },
    },
    "MM-2026-050": {
        "instrument": (
            "Buy an SMH (US semis ETF) put spread — e.g. the ~5%-OTM / ~12%-OTM put spread, defined-risk downside on "
            "US semiconductors. Max loss is the premium. The KOSPI crashed -8.95% (SK Hynix -15%, Samsung -10%) but US "
            "semis have not fully repriced the Korea rout, the toll or the CPI risk, and index vol is cheap (VIX ~16) — "
            "cheap convexity on the catch-down."
        ),
        "fundamental_thesis": (
            "The options expression of the chip catch-down. Korea — the memory heart of the AI-capex trade — crashed "
            "overnight on an analyst cutting SK Hynix's numbers, and the US semis complex has only partly followed. "
            "With VIX still ~16, a defined-risk SMH put spread buys convexity on the gap between the KOSPI's -9% and "
            "the SOX's smaller move, into a two-sided CPI and an escalating war. It is the vol-market completion of the "
            "book's Micron/AI-glut view (the Burry tell) and the short leg of MM-049 in options form — own the "
            "catch-down with capped risk rather than fight the whole complex in spot."
        ),
        "catalysts": [
            "KOSPI -8.95% / SK Hynix -15% / Samsung -10% — the Korea crash the US hasn't fully matched",
            "Korea Investment cut SK Hynix Q2 op-profit ~8% below consensus — the glut crack in estimates",
            "VIX ~16 — cheap index/semis vol into a two-sided CPI and an escalating war",
            "June CPI + the toll — the macro accelerants that could extend the de-risk",
        ],
        "risks": (
            "A soft-CPI risk-on rally squeezes semis higher and the put spread decays; the US complex may already "
            "discount more of the Korea move than it appears. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the US semis complex has not fully repriced the KOSPI crash or the CPI/toll risk; "
                            "the catch-down is under-priced with vol cheap.",
            "catalyst":     "2/2 — the Korea crash and the SK Hynix profit cut are live; CPI is dated this morning.",
            "positioning":  "1/2 — the crowd is still long AI/semis; a catch-down is the pain trade.",
            "confirmation": "1/2 — Korea has already crashed; the US lag is the one confirming leg still to come.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-051": {
        "instrument": (
            "Long USD/KRW spot — buy the dollar, sell the Korean won. Korea is a near-total energy importer, so a 20% "
            "Hormuz toll and an $84 Brent are a direct terms-of-trade shock; it is simultaneously the epicentre of the "
            "chip crash (KOSPI -8.95%), which drives equity-outflow won selling. The cross owns the EM oil-importer "
            "penalty and the risk-off outflow in one expression the crowded long-USD-major trade does not touch."
        ),
        "fundamental_thesis": (
            "The FX expression of the day's two shocks landing on one country. Korea imports essentially all its oil, "
            "so the toll is a pure terms-of-trade drag on the won; and Korea is the semiconductor heart of the AI "
            "trade, so the KOSPI's -8.95% crash forces equity-related won selling. Long USD/KRW owns both — the "
            "oil-importer penalty and the capital-outflow bid for dollars — in a cross with far less crowding than the "
            "long-USD-vs-EUR/JPY majors trade the whole market is already in. It is the EM-FX completion of the same "
            "toll-and-chip-crash thesis MM-048/049/050 express in rates and equities."
        ),
        "catalysts": [
            "20% Hormuz toll + $84 Brent — the terms-of-trade shock on the oil-importing won",
            "KOSPI -8.95% / SK Hynix -15% — the equity-outflow won selling",
            "A hawkish-for-longer Fed (Waller, the toll) — the dollar-rate side of the cross",
            "BoK response / FX-reserve intervention — the two-way risk to watch",
        ],
        "risks": (
            "A fast de-escalation and toll withdrawal drains the oil premium and the KOSPI bounces, reversing the won "
            "selling; the Bank of Korea can lean against sharp won weakness with reserves. Stop below the recent "
            "USD/KRW range low."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the won carries both the oil-importer penalty and the chip-crash outflow, a "
                            "double-shock the crowded long-USD-majors trade under-prices.",
            "catalyst":     "2/2 — the toll and the KOSPI crash are both live and dated; both legs fire now.",
            "positioning":  "1/2 — a lower-crowding dollar-long than the EUR/JPY majors; won longs are being forced out.",
            "confirmation": "1/2 — the KOSPI has already crashed and oil is bid; one confirming leg.",
            "stop_quality": "1/1 — a clean range-low stop below the pre-escalation base.",
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
    _row("WTI Crude",   "wti",    _usd, force_dir="up"),
    _row("Brent Crude", "brent",  _usd, force_dir="up"),
    _row("Gold (XAU)",  "gold",   _gold),
    _row("VIX",         "vix",    lambda v: f"{v:.2f}"),
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},   # hold; funding unmoved
    {"name": "MOVE", "level": "~108 (est)", "chg": "firmer", "dir": "up"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Mon 13 Jul · NY Fed"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~105", "chg": "firmer (est)", "dir": "up"},
]

# Per-trade open-book notes (shown in the "yesterday, graded" table).
NOTES = {
    "MM-2026-001": "FLAT. EUR/AUD near entry — the war risk-off pressures the AUD while an $84 Brent and a broad commodity bid lift its terms of trade the other way, pinning the cross mid-range. No EUR catalyst left; edge thinned. Trim into any risk-off AUD weakness. Stop 1.662 (close). Tight leash.",
    "MM-2026-004": "THE LAGGARD. 10Y ~4.62%, up another 6bp from the 4.44% entry as Trump's 20% Hormuz toll sent Brent to a six-year single-day record and re-armed inflation — the war gives duration NO haven bid. Better expressed via the curve (MM-009); own the inflation via breakevens (MM-048). Stop 4.65% (~3bp) — a very tight rein into CPI.",
    "MM-2026-005": "THE WAR STILL DIDN'T SAVE IT. Gold FELL a second day to ~$4,010 (~-11% from the $4,523 entry) — the 10Y rose to 4.62% on the toll and gold traded as a real-rates short. Held on its min-hold (to ~Jul 15, now one day past CPI). The coiled upside is owned via the defined-risk call spread (MM-046).",
    "MM-2026-007": "OFFSIDE. USDJPY ~162.1, above the 159.37 entry (~-1.7%), as the risk-off bought the DOLLAR not the yen and an $84 Brent + the toll hit the energy-importing yen. Stop 163.00, now ~0.9pt away — tight. The cleaner haven is CHF/JPY (MM-045); the sharper oil-importer expression is USD/KRW (MM-051).",
    "MM-2026-009": "THE WINNER. 2s10s ~+34bp, ~+125% off the +15bp entry — the spread widened as the toll confirms it: a Fed boxed between a labour crack and a toll-driven oil-CPI. The one rate expression the war doesn't break. Min-hold ~Jul 16; trail the stop; stop -10bp; target +60bp.",
    "MM-2026-012": "WORKING. ~1.1390 with DXY firm ~100.9 — the risk-off bought the haven dollar and an $84 Brent + the toll hit the euro's terms of trade. Green (~+1.8%), stop 1.182 distant. Hold the core short; own the hot-CPI/haven-dollar tail via MM-042 (held).",
    "MM-2026-013": "OFFSIDE. 2Y ~4.28%, above the 4.162% entry (~flat-to-red) as the toll, an $84 Brent and Waller's 'hike in the near term' warning re-priced near-term hike risk against the short. Min-hold elapsed; stop 4.35%. CPI this morning is the decider; the curve (MM-009) is the higher-conviction sibling.",
}

# Notes for the closed ledger (keyed by id; falls back to the exit reason).
CLOSED_NOTES = {
    "MM-2026-006": ("STOPPED June 8. Q2 beat but the Q3 AI guide ($16.0B vs buy-side $17.2B) missed the number that "
                    "mattered at 41x; payrolls finished it."),
    "MM-2026-002": ("The US-Iran MoU removed the re-escalation premium the long was built on. Brent broke the $87 "
                    "weekly-close exit and the $84 stop; now sub-$80. The book's MoU binary paid off on the duration "
                    "side instead — surrendered by design, not by surprise."),
    "MM-2026-011": ("Peace deflated the Hormuz tail the call spread owned. With Brent sub-$80 the $100 strike is far "
                    "away and the catalyst is dead. Closed near the $1 discipline level to recover residual premium."),
    "MM-2026-010": ("STOPPED on the melt-up Jun 16: Monday's +3.07% Nasdaq against a +1.05% DAX broke the 0.943 ratio "
                    "stop. The relief rally re-rated US tech faster than European financials. Re-expressed as the "
                    "broadening RV MM-022."),
    "MM-2026-003": ("STOPPED June 10. The Brent-WTI spread compressed as the Hormuz premium drained out of the "
                    "Atlantic-basin grade faster than Cushing. Defined spread risk; the stop did its job."),
    "MM-2026-008": ("BANKED Jun 27 at ~$45 (~+29% from the ~$35 entry, peak ~$60/+71%). The FOMC-tail hedge did its "
                    "job — Warsh's hawkish dots dropped the S&P toward the strike and VIX re-rated. Harvested into "
                    "expiry rather than risk it bleeding to zero over the weekend."),
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
    {"datum": "US PRE-MARKET Tue Jul 14 into an 08:30 ET June CPI + big-bank Q2 kickoff (BMO). Brief covers the Mon Jul 13 session (blockade + 20% toll, oil's biggest day in 6 years, KOSPI crash) and the Tuesday setup. Both CPI and bank prints are PENDING.",
     "source": "NYSE/Nasdaq + SIFMA + BLS calendar", "asof": TODAY, "stale": False},
    {"datum": "20% HORMUZ TOLL + BLOCKADE (Jul 13): Trump on Truth Social said the US is 'resuming the Iran Blockade' and will charge 'at the rate of 20% on all cargo shipped' through the Strait, calling the US the 'Guardian of the Strait of Hormuz.' Blockade resumes Tue Jul 14 4pm ET (CENTCOM). Citi: the toll 'materially raises the risk of further escalation.'",
     "source": "Euronews + CNBC + Bloomberg + NPR + Axios (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "WAR ESCALATED (Jul 13): a third night of US strikes hit Bandar Abbas, Kish, Qeshm and Abu Musa; Iran said it disabled two 'rogue supertankers'; the UAE confirmed Iranian missiles hit two tankers in Omani waters, killing one crew member. The April-era ceasefire has effectively collapsed.",
     "source": "CNN + Al Jazeera + NPR (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Oil: Brent settled +9.59% at $83.30 (Mon) — its BIGGEST single-day % gain in 6+ years — WTI +~4%. Pre-market Tue: Brent Sep ~$84.84 (+1.85%), WTI Aug ~$79.78 (+2%). Brent-WTI spread widening on the seaborne premium (MM-044 vindicated).",
     "source": "CNBC + Al Jazeera + Bloomberg (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Gold ~$4,001-4,020 — FELL ~2.9% (Mon), a SECOND down day, as the 10Y rose 6bp to ~4.62% and the toll re-armed inflation/higher-for-longer; gold traded as a real-rates short, NOT a haven.",
     "source": "Trading Economics + tmgm (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Rates (Mon Jul 13): US 10Y ~4.62% (+6bp), 2Y ~4.28%, 2s10s ~+34bp on the toll cost-push. Sept hike ~64%; hike-this-year still priced (July Jul 28-29 hold expected). Fed's Waller: the Fed should hike 'in the near term' if this week's CPI/PPI are 'hot.'",
     "source": "Wolf Street + CME FedWatch + Fed H.15 (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "FX (Mon Jul 13 → Tue pre-market): DXY ~100.9 firm on a safe-haven bid; USD/JPY ~162.1 (yen the funder in an oil shock); EUR/USD ~1.1390-1.1408; the toll is a terms-of-trade drag on oil-importer currencies (JPY, KRW, EUR).",
     "source": "Vantage + Trading Economics + Bloomberg (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Asia (Tue Jul 14): KOSPI CRASHED -8.95% (near a circuit breaker), KOSDAQ -4.55%; SK Hynix -15.46%, Samsung -10.53%, SK Square -17.67%. Korea Investment CUT SK Hynix's Q2 op-profit ~8% below consensus on slower HBM4 shipments. Nikkei -1.92%. The glut/demand crack is in ESTIMATES now.",
     "source": "Seoul Economic Daily + CNBC + Trading Economics (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Prior close (Mon Jul 13): S&P 500 7,515.34 (−0.79%); Nasdaq Composite 25,873.18 (−1.55%); Dow 52,498.64 (−0.26%); VIX ~16.2. Semis led the decline on the toll + oil.",
     "source": "CNBC + Yahoo Finance + Motley Fool (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "June CPI PENDING — Tue Jul 14 08:30 ET. Consensus: headline −0.1% m/m (~3.9% y/y, from May 4.2%), driven by a ~10% June gasoline DROP from the mid-June ceasefire; core +0.2-0.3% m/m (~2.9% y/y). BACKWARD-LOOKING: the print contains NONE of July's $84 Brent or the 20% toll.",
     "source": "BLS + Kiplinger + IG (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Big-bank Q2 earnings PENDING — Tue Jul 14 BMO: JPM (~$5.74 EPS, implied move ~4.4%), GS (~$14.46, +32% IB fees y/y, implied move ~6.0%), C (~$2.76, ~5.5%), BAC (~$1.13, ~4.5%), WFC (~$1.73, ~5.5%); Jul 15: MS, BLK, BNY. Steeper curve = NIM tailwind; same-day CPI + war gap can swamp it.",
     "source": "Finnhub + Zacks + Intellectia (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.62% — funding unmoved by the war/oil spike/toll; no plumbing stress.", "source": "NY Fed (rail)", "asof": "2026-07-13", "stale": True},
]

# ── Earnings intelligence ───────────────────────────────────────────────────────
# Big banks kick off Q2 season Jul 14-15 — all Financials, all >$10bn, US: qualify. Consensus fields are
# SOURCED from earnings_data.md (Finnhub, generated 2026-07-10 06:00 UTC). Short interest = unavailable →
# positioning pillar tagged "estimated". Three ideas rendered; the rest of the cohort noted, not padded.
earnings_ideas = [
    {
        "ticker": "GS", "company": "Goldman Sachs", "report_date": "2026-07-14", "report_timing": "BMO",
        "mode": "PRE-EARNINGS", "direction": "Long", "conviction_score": 6, "conviction_label": "High — data gap flagged",
        "conviction_rationale": ("Goldman carries the widest implied move in the cohort (~6%) into a Q2 where "
            "investment-banking and trading — the line the sell-side is most split on (15 buy / 15 hold / 2 sell) — is "
            "re-accelerating; a beat on IB against a divided book is a real, data-attributable asymmetry."),
        "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 1, "catalyst": 2, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced", "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Consensus ~$14.46 EPS on ~$16.4B revenue (Finnhub); beat four straight quarters (Q1 +3.3%, Q4 +16.5%).",
            "Widest implied move in the cohort (~6%) and the most divided sell-side (15 buy / 15 hold / 2 sell).",
            "Reports into a 2s10s at ~+34bp (NIM/curve tailwind) and a re-opening capital-markets pipeline.",
        ],
        "what_moves_it": ("Investment-banking and trading revenue vs a divided consensus; the same-morning June CPI and "
            "an escalating war (blockade + 20% Hormuz toll) are the macro cross-currents that can swamp a good print."),
        "client_talking_point": ("GS is the highest-beta way to own the bank-earnings kickoff — a ~6% implied move and a "
            "split sell-side mean an IB beat has room to re-rate; own it with a defined-risk call spread, not naked, "
            "because CPI and a war gap both land the same morning."),
    },
    {
        "ticker": "JPM", "company": "JPMorgan Chase", "report_date": "2026-07-14", "report_timing": "BMO",
        "mode": "PRE-EARNINGS", "direction": "Long", "conviction_score": 5, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced", "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Consensus ~$5.74 EPS on ~$49.9B revenue (Finnhub); beat four straight quarters (Q1 +7.95%).",
            "17 buy / 13 hold / 0 sell — solid but not differentiated; the cohort bellwether.",
            "Steeper curve (2s10s ~+34bp) supports NIM; the read-through sets the tone for the whole group.",
        ],
        "what_moves_it": ("Net-interest margin on a steeper curve and the credit-reserve build; as the bellwether, the "
            "guide moves the cohort more than the stock."),
        "client_talking_point": ("JPM is the sector tell, not the highest-beta trade — a clean NIM print and benign "
            "credit set the tone for the group; a well-owned bellwether has less asymmetry than GS into the same tape."),
    },
    {
        "ticker": "C", "company": "Citigroup", "report_date": "2026-07-14", "report_timing": "BMO",
        "mode": "PRE-EARNINGS", "direction": "Long", "conviction_score": 5, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced", "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Consensus ~$2.76 EPS on ~$24.0B revenue (Finnhub); the biggest serial beater — last 4 quarters +13% to +20%.",
            "22 buy / 6 hold / 0 sell; the cheapest large-cap bank on the transformation re-rating.",
            "A steeper curve plus the restructuring self-help is a two-engine story into the print.",
        ],
        "what_moves_it": ("Whether the serial-beat pattern (13-20% surprises) holds and the transformation cost line "
            "keeps improving; a beat on a cheap multiple re-rates faster than a bellwether."),
        "client_talking_point": ("Citi is the value leg of the bank trade — it has beaten by double digits four quarters "
            "running and trades cheapest; a fifth beat on a steeper curve is the re-rating catalyst."),
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
        "THE TOLL AND THE TRAP. The war did not de-escalate — it escalated into a tax. Trump reimposed the naval "
        "blockade and declared a 20% toll on ALL cargo transiting Hormuz ('Guardian of the Strait'); a third night of "
        "US strikes hit Bandar Abbas, Kish, Qeshm and Abu Musa, and Iran hit two tankers in Omani waters. Brent posted "
        "its BIGGEST single-day gain in 6+ years (+9.59% to $83.30; ~$84.84 pre-market). The cross-asset answer: the "
        "dollar bid (DXY ~100.9, USD/JPY ~162.1), the 10Y +6bp to ~4.62%, gold DOWN a second day (~$4,010 — a "
        "cost-push, not a haven), and the KOSPI CRASHED -8.95% (SK Hynix -15%, Samsung -10%) as Korea Investment cut "
        "SK Hynix's Q2 profit ~8% below consensus — the AI-glut crack now in ESTIMATES, not just price. And it all "
        "lands the same morning as June CPI (08:30 ET, PENDING) — a BACKWARD-LOOKING print measured in the calm "
        "pre-toll month (soft headline on a 10% June gasoline drop) that contains none of July's $84 oil — and the "
        "big-bank Q2 kickoff (JPM, GS, C, BAC, WFC BMO, PENDING). The oil hedge had its best day in years: "
        "TotalEnergies + the Jul 13 Brent–WTI widener (MM-044) lead; Jul 11's SPX and EUR/USD put spreads still work. "
        "The fresh trade presses the NEW information: long 5Y breakevens (the inflation the CPI can't see), long XLF vs "
        "short semis (the cohort the curve helps vs the one crashing), a semis put spread (the US catch-down to "
        "Korea), and long USD/KRW (the oil-importer hit by both the toll and the outflow)."
    ),

    "summary_narrative": """
<p>The most important thing about Monday is that the war did not de-escalate &mdash; it escalated into a tax, and the
most inflationary policy shock of the year now lands on the same morning as the most disinflationary data print of the
year. On Truth Social, Trump reimposed the naval blockade of Iranian ports and declared the United States will charge
&lsquo;at the rate of 20% on all cargo shipped&rsquo; through the Strait of Hormuz, casting America as the self-appointed
<strong>Guardian of the Strait</strong>. A third night of US strikes hit Bandar Abbas, Kish, Qeshm and Abu Musa; Iran
said it disabled two &lsquo;rogue supertankers&rsquo; and the UAE confirmed Iranian missiles hit two tankers in Omani
waters, killing a crew member. Brent answered with its biggest single-day gain in over six years, +9.59% to a $83.30
settle. (Euronews, CNBC, Bloomberg, CNN, Al Jazeera.)</p>

<p>Decompose what the toll actually is, because it is not another headline to look through. The consensus files it with
every prior Hormuz flare-up. The anatomy says it is a structural cost-push the market has never priced: a 20% tariff on
roughly a fifth of the world&rsquo;s seaborne oil, imposed by the United States itself, mechanically lifting the
delivered price of every barrel that clears the Strait &mdash; and Citi&rsquo;s own read is that it materially raises the
risk of further escalation. This is not a supply scare that de-escalation reverses cleanly; it is a toll with a price
tag. So what, who is wrong, what is the trade: the crowd is about to trade a June print that measured the calm, and the
trade is to own the inflation that print is structurally blind to.</p>

<p>The second-order effect consensus is missing is the maximum-divergence trap at 08:30. June was the calm month:
gasoline fell about 10% on the mid-June ceasefire, so the consensus June headline is &minus;0.1% month-on-month
(~3.9% annual) &mdash; mechanically soft, containing none of July&rsquo;s $84 Brent or the 20% toll. The danger is a
tape that gaps on the war, then rallies on a soft headline it misreads as disinflation, while core holds +0.2&ndash;0.3%,
Waller says the Fed should hike &lsquo;in the near term&rsquo; if this week&rsquo;s CPI and PPI run hot, and July&rsquo;s
oil already re-arms the next print. The Burry tell stopped being a forecast and printed: Korea Investment cut SK
Hynix&rsquo;s Q2 operating profit ~8% below consensus on slower HBM4 shipments, the KOSPI crashed 8.95%, SK Hynix fell
15% and Samsung 10% &mdash; the glut crack now visible in the numbers. The book is 30% Micron; this is the second,
bigger crack.</p>

<p>The book sits astride the reprice and the oil hedge just had its best day in years. TotalEnergies and the Jul 13
Brent&ndash;WTI widener (MM-044) lead as crude posted a six-year single-day record; Jul 11&rsquo;s SPX put spread
(MM-041) and EUR/USD put spread (MM-042) still work on the risk-off and the haven dollar; the 2s10s steepener (MM-009)
holds ~+34bp as the one rate expression the toll confirms, while the short-10Y (MM-004) and short-2Y (MM-013) lag as
yields back up and gold (MM-005) fell a second day. Short EUR/USD (MM-012) works.</p>

<p>The regime is no longer &lsquo;the tape is being forced to price a war.&rsquo; It is a market that must reconcile the
most inflationary policy shock of the year with the most disinflationary data print of the year in the same eight-thirty
minute &mdash; and the trap is that the backward-looking number wins the morning while the toll wins the quarter. The
posture is to press the new information: own the inflation the CPI is blind to (breakevens), own the one cohort the
war-steepening helps against the one it is crashing (banks vs semis), own the US catch-down to Korea, and own the EM
oil-importer hit by both the toll and the outflow.</p>
""",

    "takeaways": [
        "<strong>Trump taxed Hormuz: a 20% toll on ALL cargo + a reinstated blockade.</strong> On Truth Social he "
        "declared the US the 'Guardian of the Strait,' charging 20% on all transiting cargo; the blockade resumes Tue "
        "4pm ET. A third night of US strikes hit Bandar Abbas, Kish, Qeshm and Abu Musa; Iran hit two tankers in Omani "
        "waters. Citi: the toll 'materially raises the risk of further escalation.' (Euronews, CNBC, Bloomberg.)",

        "<strong>Oil's biggest day in six years.</strong> Brent settled +9.59% at $83.30 (Mon) &mdash; its largest "
        "single-day gain in 6+ years &mdash; WTI +~4%; pre-market Brent ~$84.84, WTI ~$79.78. The Brent&ndash;WTI "
        "spread is widening on the seaborne premium: the Jul 13 widener (MM-044) is vindicated and TotalEnergies leads "
        "the book. (CNBC, Al Jazeera.)",

        "<strong>Korea's chips CRASHED.</strong> The KOSPI fell -8.95% (near a circuit breaker), SK Hynix -15.46%, "
        "Samsung -10.53%, as Korea Investment CUT SK Hynix's Q2 op-profit ~8% below consensus on slower HBM4 shipments "
        "&mdash; the AI-glut crack now in ESTIMATES, not just price. The book is 30% Micron: the second, bigger crack. "
        "(Seoul Economic Daily, CNBC.)",

        "<strong>Gold fell again; the dollar bid; the hawk re-armed.</strong> Gold dropped ~2.9% to ~$4,010 (a second "
        "down day) as the 10Y rose 6bp to ~4.62% &mdash; the toll is a cost-push, not a haven. Waller: hike 'in the "
        "near term' if CPI/PPI run hot. The short-10Y (MM-004) and short-2Y (MM-013) lag; only the steepener (MM-009, "
        "~+34bp) holds. (Trading Economics, Wolf Street.)",

        "<strong>June CPI is a backward-looking trap &mdash; PENDING.</strong> June was the calm month (gasoline "
        "&minus;10% on the ceasefire), so a soft headline (&minus;0.1% m/m, ~3.9% y/y) contains none of July's $84 "
        "Brent or the 20% toll. The risk is the tape misreads it as all-clear while core stays +0.2-0.3% and the toll "
        "re-arms the next print. (BLS, Kiplinger.)",

        "<strong>The maximum-divergence morning: banks report into the collision.</strong> JPM, GS, C, BAC, WFC report "
        "BMO (PENDING) the SAME 08:30 minute as CPI, into a war gap. GS has the widest implied move (~6.0%); a steeper "
        "curve is the NIM tailwind, but CPI + the war can swamp any print. (Finnhub, Zacks.)",

        "<strong>The trade is the inflation the print can't see.</strong> Jul 11's SPX (MM-041) and EUR/USD (MM-042) "
        "put spreads still work; MM-044 (Brent&ndash;WTI) is vindicated. Fresh money presses the NEW information: long "
        "5Y breakevens, long XLF vs short semis, a semis put spread, and long USD/KRW &mdash; not the recycled winners.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "De-escalation + soft CPI — the toll is walked back and the dip gets bought",
         "body": "Trump lifts or dilutes the toll (it is his lever to pull), the blockade eases, oil drains toward $75, "
                 "and a soft June headline (backward-looking, oil-light) revives the disinflation read: hike-this-year "
                 "odds fall, the 2Y rallies (MM-013 re-confirms), the curve bull-steepens (MM-009), gold gets real-rate "
                 "relief (MM-005 rescued at the min-hold), and the chip-led selloff is bought back. Breakevens (MM-048) "
                 "and the semis put spread (MM-050) decay; XLF/SMH (MM-049) narrows. The catch: the tape chases a "
                 "headline that can't see July's oil or the toll's second-round effects. Risk up · rates down (front) · "
                 "dollar soft · gold up · oil soft."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "The toll sticks and a boxed-in Fed — steep curve, firm oil, banks lead, semis lag, choppy risk",
         "body": "The toll stays on the books and oil holds a premium ~$82-86, June CPI prints a soft headline over a "
                 "sticky +0.2-0.3% core, and the labour crack caps the hike; Warsh's Fed holds a hawkish hold it can "
                 "neither justify nor execute. The 2Y ranges, the curve stays steep (MM-009 the winner) and breakevens "
                 "grind wider (MM-048), energy holds (TotalEnergies/MM-044), the banks lead their cohort on NIM while "
                 "semis lag (MM-049), gold chops below $4,100, the dollar stays firm (MM-012, MM-051 hold), and "
                 "equities chop as the war-gap partly retraces. Risk mixed · rates steady/steeper · dollar firm · oil "
                 "firm · curve steep."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "Escalation or a hot core — oil spikes through $90, the chip crash spreads, credit widens",
         "body": "Either Iran answers the toll and oil spikes through $90 (MM-044 and TotalEnergies pay hard, MM-048 "
                 "breakevens and MM-046 gold convexity fire), the Korea chip crash extends to US semis and the S&amp;P "
                 "(MM-050 and MM-041 pay, MM-049 widens), and HY spreads finally gap (MM-047 pays); or a hot core CPI "
                 "on top re-arms a near-term hike, backs the 2Y toward the 4.35% stop (MM-013 risk) and bear-flattens "
                 "the front. Either way the toll is IN the price and the disinflation trade breaks. Risk down · rates "
                 "two-way · dollar bid · oil up · credit wider."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a single collision: the most inflationary policy shock of the year and the most
disinflationary data print of the year land in the same 08:30 minute. Monday Trump turned the war into a tax &mdash; a
20% toll on all Hormuz cargo and a reinstated blockade &mdash; and Brent posted its biggest single-day gain in six
years. Tuesday, June CPI prints the calm month before any of it. The non-consensus read is that the toll is not a
headline to look through: it is a structural cost-push on a fifth of the world's seaborne oil, imposed by the US itself,
and the market is about to trade a June number that cannot see a cent of it.</p>

<p>The counter-intuitive hook is that a bigger war made gold fall, again. A shooting war with a blockade and a toll
would, in the textbook, send bullion and duration higher; instead gold dropped a second day to ~$4,010 and the 10Y rose
6bp to ~4.62%. A 20% oil-transit tax is inflationary, which lifts inflation expectations and real yields, which caps
gold and sells bonds. The only havens paying in this regime are the dollar and oil itself. That is the whole regime in
one line: a war that transmits as inflation, not as fear &mdash; and now with a literal price tag attached.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong> a 20%
Hormuz toll, Brent ~$84, the 10Y at 4.62%, core PCE near 3%, a Waller warning to hike 'in the near term,' and a memory
capacity race whose glut just showed up in SK Hynix's cut numbers. <strong>What is priced:</strong> a soft June headline
assumed, VIX only ~16, HY spreads still catching up, breakevens lagging the oil move. <strong>Consensus narrative:</strong>
&lsquo;the war is contained to oil, June CPI will be soft, buy the dip.&rsquo; The gap &mdash; and the alpha &mdash; is
that the forward inflation the toll guarantees is not in breakevens, and the chip crack is not yet in US semis.</p>

<p>Go around the world. <strong>US:</strong> futures gap lower pre-CPI; the AI-concentrated index is the epicentre, but
the bank cohort reporting into a steeper curve is the one green shoot. <strong>Korea/Asia:</strong> the KOSPI CRASHED
-8.95% (SK Hynix -15%, Samsung -10%) on an analyst cutting SK Hynix's profit &mdash; both the chip heart AND an
oil-importer taxed by the toll; the Nikkei fell -1.92%. <strong>Europe:</strong> an energy-importing bloc hit by an $84
Brent, the natural underperformer. <strong>Middle East:</strong> the blockade resumes Tue 4pm ET; Trump alone owns the
toll, the strike and the off-ramp.</p>

<p>The political angle runs on two constraints. The Papic read is sharper than a binary now: Trump owns the strike, the
blockade AND the toll &mdash; the oil premium is not a market variable, it is a policy lever he has just monetised,
which makes it a step-change, not a drift. The second constraint is the Fed: a toll-driven oil spike is a cost-push that
boxes a central bank (Warsh) already leaning hawkish &mdash; it cannot cut into an oil-CPI and cannot hike hard into a
labour crack, so it holds a hawkish hold. The non-consensus read is that the market's real risk is not the war headline
but the CPI trap underneath it: a soft, backward-looking June print that invites a dip-buy just as July's oil and the
toll re-arm the next one.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the forward inflation the toll guarantees (long 5Y breakevens,
MM-048); the US semis catch-down to Korea (MM-050, MM-049 short leg); the growth scare in credit (HY protection, MM-047,
held). <strong>Fairly priced:</strong> the haven dollar (MM-012, MM-051, MM-045); the steeper curve (MM-009); the
waterborne premium (MM-044, already moving). <strong>Now pricing (was over-priced):</strong> equity complacency &mdash;
the SPX gap (MM-041, held) is printing. <strong>Over-priced (at risk):</strong> a soft June headline read as all-clear
while July's oil and a 20% toll are already in the pipeline.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is that the war stopped being a supply scare and became a
tax. On Monday, having spent the weekend bombing Iran a third time, the President did something no prior Hormuz flare-up
had produced: he reimposed the naval blockade and announced that the United States would charge a twenty-percent toll on
every cargo transiting the Strait of Hormuz, styling America the &lsquo;Guardian&rsquo; of the waterway and the fee its
compensation. Brent answered with its largest single-day gain in more than six years, up almost ten percent to a
settle above eighty-three dollars. And it all lands into an eight-thirty CPI that measures June &mdash; the one calm
month, after the mid-June ceasefire dropped gasoline ten percent and before any of this. The most inflationary event of
the year and the most disinflationary print of the year, in the same minute.</p>

<p>Decompose what the toll actually is, because the market is about to misfile it. The consensus reads it as another war
headline, one more escalation to look through until the next off-ramp. The anatomy says it is a structural cost-push the
market has never had to price: a twenty-percent tariff on roughly a fifth of the world&rsquo;s seaborne oil, imposed not
by an embargo or an accident but by the guarantor of the sea lane itself, mechanically added to the delivered cost of
every barrel that clears Hormuz. Citi&rsquo;s own read is that the fee raises the odds of further military escalation, not
lowers them. So what, who is wrong, what is the trade: the crowd is about to trade a June number that captured the calm,
and the trade is to own the inflation that number is structurally blind to &mdash; not the headline it prints.</p>

<p>Trace it to a flow, because the durable move is mechanical, not narrative. A toll is not a probability, it is a price.
Where a closed Strait was a supply risk the market could discount by the odds of reopening, a twenty-percent levy is a
cash cost stamped on the waterborne barrel &mdash; Brent, priced off the cargoes that must transit Hormuz &mdash; and
barely at all on the landlocked American grade fed by pipeline from Cushing. That is why the Brent&ndash;WTI spread is
widening and why the widener put on yesterday is already paying. And the same levy lands on the Treasury market as an
inflation impulse with a coupon: the ten-year backed up six basis points rather than rallying in a shooting war, the
curve steepened rather than flattened, and breakevens &mdash; the instrument that prices exactly this &mdash; have not
yet caught up. Own the inflation the CPI cannot see, and you own the gap between the print and the pipeline.</p>

<p>The Burry tell stopped being a forecast overnight and printed in the numbers. For weeks the argument was that the
capacity race the AI narrative funds does not pause, that Hynix, Samsung and Micron keep pouring capital into
high-bandwidth memory into the same demand assumption, and that memory is a commodity whose cycle has never been broken,
only postponed. On Monday Korea Investment cut SK Hynix&rsquo;s second-quarter operating profit some eight percent below
consensus on slower HBM4 shipments, the Korean index crashed almost nine percent, and the memory names fell fifteen. The
glut is no longer a thesis about price; it is a downgrade in an analyst&rsquo;s model. The book is thirty percent Micron,
the single cleanest expression of the bet that the cycle is dead, and this is the second and larger crack. The
discipline is to monetise the still-rich volatility into any bounce, never to buy the dip on the largest weight while the
crack is spreading.</p>

<p>So the posture is to press the new information, not to recycle the vindicated trades. Yesterday&rsquo;s widener and
the earlier index and euro put spreads already own this move and are held, not chased. The fresh money goes where the
toll and the crash have not yet been priced: long five-year breakevens, because a twenty-percent oil-transit tax is
forward inflation a backward-looking June print cannot contain; long the banks against the semiconductors, because the
one cohort a war-driven steepening rewards reports this morning while the one it punishes is crashing in Seoul; a
defined-risk semis put spread for the American catch-down to a Korean rout that vol at sixteen is not pricing; and long
the dollar against the Korean won, the oil-importer taxed by the toll and bled by the outflow at once. The tape decided a
war it could look through. The President just gave it an invoice &mdash; and the June CPI, blind to it, is the trap that
could make the market forget for a morning.</p>
""",

    "correlation_regime": """
<p><strong>1. Banks decoupled from semis &mdash; the split that defines the day.</strong> The whole equity market has
traded AI and financials as one 'risk' bucket; the toll-and-curve regime just split them. Semis are crashing (KOSPI
-8.95%, SK Hynix -15%) on the AI-glut crack, while banks report into a 2s10s at ~+34bp that lifts NIM &mdash; the one
cohort the war-driven steepening rewards. The break is the trade: long XLF vs short SMH (MM-049), and own the semis
catch-down with defined risk (MM-050).</p>

<p><strong>2. Gold stayed decoupled from geopolitics &mdash; still glued to real rates.</strong> A blockade AND a toll
did not bid gold: it FELL a second day to ~$4,010 while the 10Y rose 6bp to ~4.62%, so gold traded as a real-rates short
again, not a haven. The book's gold long (MM-005) is deep underwater despite an escalating war. The break is durable
&mdash; gold only re-couples if the war becomes a growth scare that forces real yields DOWN, exactly the tail the Sep
call spread (MM-046) owns.</p>

<p><strong>3. Breakevens decoupled from the oil price &mdash; the new laggard.</strong> Brent posted its biggest day in
six years and a 20% oil-transit toll is now policy, but 5Y breakevens have not fully repriced the forward inflation the
toll guarantees &mdash; the market is fixated on a soft backward-looking June headline. The instrument that prices this
directly is the one that has moved least. Own the laggard (long 5Y breakevens, MM-048); it is the rates-market
completion of the 'own the inflation the print can't see' thesis.</p>

<p><strong>4. The curve stayed decoupled from the level.</strong> Both the 2Y and 10Y are up on the toll cost-push, but
the 2s10s widened to ~+34bp &mdash; the front pinned by a boxed-in Fed, the back heavy on supply and the war premium. A
steepener that survives rising yields is a structural signal: the dominant rates driver is the bind, not the direction.
Own the shape (MM-009), not outright duration (why MM-004 lags).</p>
""",

    "vol_skew": """
<p><strong>The vol bid is loud in oil, quiet in equities &mdash; and that gap between a VIX at sixteen and a chip index
crashing nine percent is the cheapest convexity on the board.</strong> OVX (oil vol) is where the real bid sits: the
blockade and a 20% toll are a live gamma event in crude, and WTI 1-month implied vol ran to ~68% last week. Yet US
equity vol is still only ~16.2 even as the KOSPI crashed -8.95% overnight and June CPI + the bank tape land at 08:30.
The term structure is only modestly kinked (est. VIX9D ~17 · VIX ~16-17 · VIX3M ~18 · VIX6M ~19). MOVE stays firm
(~108) as the toll-led yield backup lifts rates vol. The fresh structure that fits today is a defined-risk SMH (US semis)
put spread (MM-050): the KOSPI has already crashed, the US complex has not fully followed, and index vol is cheap &mdash;
so the catch-down convexity is under-priced. The gold Sep $4,200/$4,600 call spread (MM-046, held) is still the cheap
regime-change tail, subdued because bullion trades as a rate-trade. The equity index hedge (MM-041, held) is working, not
fresh &mdash; don't chase richened puts. If the toll is walked back and CPI's core is soft, the semis and gold convexity
decay cheaply; if the war holds or core runs hot, both are owned, not chased.</p>
""",

    "sector_rv": """
<p><strong>Leading (Mon Jul 13 / Tue pre-market):</strong> Energy on the toll premium (Brent +9.59% to $83.30, its
biggest day in 6 years); the haven dollar. Banks set up as the day's relative winner &mdash; the one cohort a +34bp
curve rewards, reporting BMO. <strong>Lagging:</strong> AI/semis and memory &mdash; the KOSPI crashed -8.95% (SK Hynix
-15%, Samsung -10%), the AI-glut crack now in SK Hynix's cut numbers; European equities as an energy importer hit by $84
Brent; duration-sensitive defensives as the 10Y rose to ~4.62%. <strong>This week:</strong> June CPI Tue (the
backward-looking decider); big-bank earnings Tue-Wed (JPM, GS, C, BAC, WFC &rarr; MS, BLK, BNY) into the war gap; the
Hormuz toll/blockade start (Tue 4pm ET).</p>

<p><strong>RV:</strong> Two fit today's tape. First, the banks-vs-chips split: long XLF vs short SMH (MM-049) &mdash; the
curve helps banks reporting into it while the KOSPI crash bleeds into US semis, a beta-neutral way to own the day's two
dominant stories. Within semis, the chip dispersion still stands: long NVDA (~32x) vs the overbought ~175x AMD, as the
complex de-risks the richest multiple falls first and it doubles as concentration management. Second, the waterborne
crude RV: long Brent vs WTI (MM-044, vindicated) &mdash; the toll hits the seaborne benchmark far harder than the
landlocked one, a lower-beta way to own the war than outright crude. All are low index beta and high beta to the week's
live catalysts &mdash; the bank prints, the chip de-risk and the Hormuz toll.</p>
""",

    "positioning": """
<p><strong>The crowd is long the AI trade, short vol at 16, leaning dovish into a soft June headline, and positioned for
disinflation &mdash; the toll is the pain trade for all of it.</strong> The loudest lean is the disinflation bet: the
market is trading a backward-looking June print (soft on a 10% June gasoline drop) as if it were the current regime,
while a 20% oil-transit toll and an $84 Brent re-arm the next one. Breakevens have not moved &mdash; that is the pain
trade in rates (long 5Y breakevens, MM-048). In equities, the crowd is long semis (AI) and light banks; the KOSPI crash
and a +34bp curve are the rotation the crowd is on the wrong side of (long XLF vs short SMH, MM-049; the semis put spread
MM-050 the catch-down). The US semis complex has not fully repriced Korea's -8.95% &mdash; the catch-down is the
pain-trade convexity while VIX is only 16. In FX, the market crowds into long-USD vs the majors for haven, so the
lower-crowding won short (long USD/KRW, MM-051) and the franc cross (CHF/JPY, MM-045) own the same risk-off with less
positioning risk. In rates, fast money is hawkish on the oil re-arm and Waller's warning, so the front-end squeeze is
two-way &mdash; the consensus-agnostic steepener (MM-009) is cleaner than the directional 2Y fade (MM-013). In gold, spec
length was washed out; positioning is clean but there is no squeeze without a rate turn (MM-005/MM-046 need the war to
become a growth scare). The pain trade everywhere is the same &mdash; a market positioned for the calm month while the
President just taxed the oil that prices the next one.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; the blockade, the toll and the oil spike produced no stress in the plumbing, and
the hawkish repricing does not move the funding rate. <strong>The Pozsar mechanic:</strong> trace the rates backup to a
flow, not a narrative &mdash; and this flow now has a coupon. A 20% Hormuz toll is a levy stamped on roughly a fifth of
the world's seaborne crude at the point of transit; it is not a probability the market discounts by the odds of a
reopening, it is a cash cost added to every delivered barrel. That levy transmits into the Treasury market as a
term-premium/inflation impulse with a price tag: the 10Y rose to ~4.62% not on growth but because a toll-driven cost-push
plus a heavy fiscal-supply calendar keeps the long end heavy while a boxed-in Fed pins the front. That is the whole
steepener (MM-009) and the reason breakevens should widen (MM-048). The tell the plumbing is flagging for next: watch
BREAKEVENS and CREDIT, not funding. The inflation-swap and 5Y breakeven markets price the toll directly and have lagged;
HY spreads are the growth-scare valve. Underneath it all, the AI-capex machine is where the crack finally shows &mdash;
the memory capacity race did not pause for the war, and Korea Investment just cut SK Hynix's Q2 profit ~8% below
consensus, the glut arriving in an analyst's model even as the CPI's June headline can't see July's oil.</p>
""",

    "tape_missing": """
<p><strong>Breakevens have not priced the toll &mdash; the widest cross-asset lag on the board.</strong> Oil posted its
biggest day in six years and a 20% oil-transit levy is now policy, yet 5Y breakevens have barely moved because the market
is anchored on a soft backward-looking June CPI. The falsifiable level: the 5Y breakeven breaking above its
pre-escalation range on the toll's confirmation says the forward inflation was mispriced and MM-048 pays; breakevens
holding flat on a clean toll withdrawal says the disinflation crowd was right. Watch the 5Y breakeven against the Brent
price &mdash; the two should not stay this far apart.</p>

<p><strong>The June CPI is a backward-looking trap the tape could walk into at 08:30.</strong> June was the calm month
&mdash; gasoline fell ~10% on the mid-June ceasefire &mdash; so a soft headline (&minus;0.1% m/m) is mechanical and
contains none of July's $84 Brent or the toll. The falsifiable line: a soft headline that sparks a dip-buy while core
holds +0.2-0.3% and the 2Y/dollar stay bid is the trap (MM-042 pays on a hot core, MM-041 on the reversal, MM-048 on the
forward inflation); a genuinely soft core at or below +0.2% revives the disinflation read and rescues gold
(MM-005/MM-046). The core, not the headline, is the test.</p>

<p><strong>The Burry tell just printed &mdash; the glut is in the numbers now, not only the price.</strong> For weeks the
argument was that the capacity race the AI narrative funds does not pause; Monday Korea Investment cut SK Hynix's Q2
operating profit ~8% below consensus on slower HBM4 shipments, and the KOSPI crashed -8.95%. Memory is a commodity whose
cycle has never been broken, only postponed, and the crack has moved from a thesis to a downgrade. Over the next
two-to-three quarters this resolves one of two ways: AI demand keeps outrunning supply and the 'broken cycle' story
survives; or the capacity lands ahead of demand, memory prices roll, and the most levered names fall hardest &mdash; a
fall the tape will blame on the next headline but is really the glut. The Fable book is 30% Micron, the single best
expression of the bet that the cycle is dead; the discipline is to monetise the still-rich volatility into any bounce,
not buy the dip.</p>
""",

    "book_outlook": {
        "commentary": (
            "The toll handed the book its best oil day in years and its second, bigger chip crack in the same session. "
            "The standout winner is <b>TotalEnergies</b>, the energy length: Trump's 20% Hormuz toll sent Brent +9.59% "
            "to $83.30, its biggest single-day gain in over six years &mdash; the war hedge the equity tape refused to "
            "build, already in the book and now paying hard. But the story this morning is the AI sleeve, and it got "
            "worse, not better. The KOSPI CRASHED -8.95% overnight (SK Hynix -15%, Samsung -10%) after Korea Investment "
            "cut SK Hynix's Q2 profit ~8% below consensus &mdash; the memory glut arriving in an analyst's model, not "
            "just the price &mdash; and the whole complex (<b>Micron</b> ~30%, <b>NVDA</b>, <b>AVGO</b>, <b>AMD</b>, the "
            "<b>SPY</b> core) reprices DOWN. The Burry tell stopped being a forecast: the book is 30% long the single "
            "cleanest expression of the 'broken cycle' bet at the exact moment the cycle showed. The one genuine offset "
            "for an EUR-base client is the ~72% <b>USD sleeve</b> &mdash; the haven-dollar bid (DXY firm ~100.9, EUR "
            "~1.1390) lifts the euro value of the book's US assets, doing the FX-hedge work the scanner flagged. The "
            "laggards are the assets that should work in a war and don't: <b>Xetra-Gold (4GLD)</b> FELL a second day as "
            "the 10Y rose to ~4.62% (the tail hedge inverted &mdash; the toll is a cost-push, not a haven bid), and the "
            "bond sleeve (<b>UST 1.25% 2031</b>, <b>Siemens EUR IG</b>) is marked lower. European names <b>LVMH</b> and "
            "<b>SAP</b> sit in the energy-importing bloc an $84 Brent hits hardest. The dominant action: the energy "
            "length is the working war hedge &mdash; press it convexly (Brent-vs-WTI), not spot; treat the chip crash "
            "as the SECOND crack of the capacity tell and monetise Micron's still-rich IVol into any bounce with real "
            "urgency, do NOT buy the dip on the 30% weight; let the haven dollar do the FX work; and do NOT add duration "
            "into a June CPI (08:30) blind to July's oil and the toll."
        ),
        "outperform": [
            {"name": "TotalEnergies (TTE, +54.8%) — the war hedge's best day in years", "why": "Trump's 20% Hormuz toll "
             "sent Brent +9.59% to $83.30, its biggest single-day gain in 6+ years &mdash; the book's energy length is "
             "the standout winner. Press the upside convexly via the Brent-vs-WTI widener (the desk's MM-044, already "
             "paying), not by adding spot into a binary-on-Trump tape."},
            {"name": "The USD sleeve (~72% of the book) — the haven dollar is a tailwind", "why": "The risk-off bought "
             "the dollar for safety (DXY firm ~100.9, EUR ~1.1390), lifting the euro value of the book's US assets for "
             "an EUR-base client &mdash; the war is doing the FX-hedge work the scanner flagged (mirrors the desk's "
             "MM-012 working). Let it run rather than hedging it away into the bid."},
            {"name": "NVDA (−10.5%) — the relative winner in the chip crash", "why": "As the complex crashes, the richest "
             "multiples fall first &mdash; NVDA at ~32x holds up better than the ~175x AMD and the de-rated AVGO. It "
             "'outperforms' only on a relative basis (the long leg of the dispersion, and the notional long in the "
             "banks-vs-chips RV MM-049); the whole sleeve is sharply lower this morning."},
        ],
        "underperform": [
            {"name": "Micron (MU, ~30%, +1082%) — the second, bigger crack", "why": "The KOSPI crashed -8.95% and Korea "
             "Investment cut SK Hynix's Q2 profit ~8% below consensus &mdash; the memory glut in an analyst's model, "
             "not just the tape &mdash; and the book's largest weight takes the direct hit. This is the Burry tell "
             "printing: monetise the still-rich IVol into any bounce (collar/overwrite) with urgency, do NOT buy the "
             "dip on the 30% weight."},
            {"name": "AMD (+394%) & the AVGO/SPY sleeve — the chip crash spreads", "why": "AMD at ~175x is the overbought "
             "leg the de-risk targets first; AVGO (−21.3%) and the SPY core gap lower as the KOSPI rout bleeds into US "
             "semis. Trim the exhausted AMD winner into any bounce &mdash; concentration management &mdash; and own the "
             "US catch-down with the defined-risk semis put spread (MM-050)."},
            {"name": "Xetra-Gold (4GLD, +108.6%) & the bond sleeve — the havens that didn't fire", "why": "Gold FELL a "
             "second day (~$4,010) as the 10Y rose 6bp to ~4.62% &mdash; the tail hedge inverted because the toll is a "
             "cost-push; the UST 2031 and Siemens IG marked lower. Own gold's regime-change tail via the defined-risk "
             "call spread (MM-046), not more spot; do NOT add duration into the CPI/oil/toll risk."},
        ],
        "watch": [
            {"label": "Monetise Micron's IVol NOW — the second crack is bigger, don't buy the dip",
             "text": "The crash looks like geopolitics; underneath, the memory glut just printed in SK Hynix's cut "
             "numbers, and the book is 30% long exactly that bet. Sell Micron's still-elevated option premium into any "
             "bounce with a collar or covered-call overwrite &mdash; own the name with a floor. The urgency is higher "
             "than yesterday: the tell is no longer a forecast, it is a downgrade."},
            {"label": "Let the haven dollar do the FX work — don't hedge the USD sleeve away into the bid",
             "text": "The scanner flagged the ~72% USD exposure for a seagull/collar; the war-driven dollar rally (DXY "
             "firm, EUR ~1.1390) is now doing that hedging FOR the EUR-base client. Hold the hedge fire while the haven "
             "bid runs; the collar entry has improved, but the immediate risk is de-hedging a tailwind, not leaving the "
             "USD open."},
            {"label": "Don't add duration before the 08:30 CPI — own the inflation the print can't see instead",
             "text": "The UST 2031 and Siemens IG are the Tuesday risk: the 10Y rose to ~4.62% and a soft June headline "
             "can flip to a hot-core sell-off, with July's $84 oil and the toll re-arming the next print. Hold the "
             "sleeve but do NOT average down; own rate value via the curve steepener (MM-009) and the inflation via 5Y "
             "breakevens (MM-048); carry the hot-core dollar tail via the EUR/USD put spread (MM-042). Press the energy "
             "length with the Brent-vs-WTI widener (MM-044)."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> buy the dip &mdash; the toll is a negotiating tactic Trump will walk back like every
prior Hormuz flare-up, June CPI will print soft and revive the disinflation story, and the AI trade resumes once the
headlines calm. The Monday gap and the Korea crash are an overshoot to fade; the chips that crashed will lead back up.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> this is not a flare-up to look through, because
the war stopped being a supply scare and became a tax &mdash; a 20% levy on a fifth of the world's seaborne oil, a cash
cost, not a probability. Oil, the dollar, rates and the KOSPI have all repriced; breakevens and US semis &mdash; the
markets that move last &mdash; still have not. The crowded side is long the AI dip, short vol at 16, and positioned for
disinflation into a backward-looking June headline it will misread as all-clear while July's $84 oil and the toll are
already in the next print. The cheaper side owns the inflation the CPI can't see (MM-048), the banks-vs-chips split
(MM-049), the US semis catch-down (MM-050), and the oil-importer won (MM-051) &mdash; the toll where it is not yet priced.</p>
""",

    "one_chart": """
<p class="theme">June core CPI at 08:30 is the number &mdash; the headline is the trap, the core is the tell, and the toll is what neither can see.</p>
<p>The single thing the market watches today is the June core CPI print at 08:30 ET, reported the same minute as the
bank cohort and into a war gap. The headline will print soft (consensus &minus;0.1% m/m, on a ~10% June gasoline drop)
&mdash; that is the trap, mechanical and backward-looking, containing none of July's $84 Brent or the 20% toll. The
level that decides the morning is the CORE: a core at or below +0.2% m/m revives the disinflation read, rallies the 2Y
(MM-013), rescues gold (MM-005/MM-046) and lets the AI dip get bought; a core at +0.3% or hotter confirms the hawk
(Waller's 'hike in the near term'), extends the dollar (MM-012/MM-042), steepens via the front, and validates the
breakeven and steepener trades (MM-048/MM-009). Either way the toll is the pipeline the June number can't measure &mdash;
watch the core against Brent, because the print prices the calm and the toll prices the quarter.</p>
""",

    "catalyst_calendar": [
        {"day": "Tue", "date": "Jul 14 — TODAY",
         "event": "June CPI (08:30 ET) + big-bank Q2 earnings (BMO) — both PENDING",
         "consensus": "June CPI consensus: headline −0.1% m/m (~3.9% y/y, on a ~10% June gasoline drop), core +0.2-0.3% "
                      "m/m (~2.9% y/y). Same morning: JPM (~$5.74 EPS), GS (~$14.46, implied move ~6.0%), C (~$2.76), "
                      "BAC (~$1.13), WFC (~$1.73) report BMO. Sources: BLS, Kiplinger, Finnhub, Zacks.",
         "view": "The maximum-divergence morning. A BACKWARD-LOOKING June print (the calm month) that can't see July's "
                 "$84 Brent or the 20% toll, meeting the bank cohort into a war gap. The core, not the headline, is the "
                 "tell.",
         "asymmetry": "A soft headline the tape misreads as all-clear is the fade (MM-041/042 pay on a hot core, MM-048 "
                      "on the forward inflation); a genuinely soft CORE (≤+0.2%) rescues gold (MM-005/046) and the AI "
                      "dip. GS is the highest-beta bank print (MM-043 held); banks lead semis (MM-049).",
         "dir": "down"},
        {"day": "Tue", "date": "Jul 14 · 4pm ET",
         "event": "Hormuz blockade + 20% toll take effect",
         "consensus": "CENTCOM's reinstated naval blockade of Iranian ports resumes and the 20% cargo toll begins. "
                      "Trump: the US is the 'Guardian of the Strait.' Citi: the toll 'materially raises the risk of "
                      "further escalation.' Sources: Axios, CNBC, Bloomberg.",
         "view": "The Papic step-change: the oil premium is no longer a market variable priced by the odds of a "
                 "reopening &mdash; it is a policy lever Trump has monetised. A cash cost, not a probability.",
         "asymmetry": "The toll live keeps the Brent widener (MM-044) and breakevens (MM-048) paying; a toll walk-back "
                      "(his lever to pull) is the bull-case that fades the war trade and revives the AI dip.",
         "dir": "up"},
        {"day": "Wed", "date": "Jul 15",
         "event": "June PPI + bank earnings wave 2 (MS, BLK, BNY)",
         "consensus": "June PPI (the other print Waller flagged) and Morgan Stanley, BlackRock and BNY Mellon BMO, "
                      "extending the Financials read into wealth/asset management and custody. The market digests CPI "
                      "and the toll. Sources: BLS, Finnhub.",
         "view": "The confirmation session: a hot PPI on top of CPI is the pipeline-inflation tell the toll guarantees; "
                 "whether the bank cohort's NIM/IB tailwind survives a risk-off tape.",
         "asymmetry": "A hot PPI confirms the breakeven/steepener trade (MM-048/009) and the hawk; a soft double print "
                      "lets the AI dip and gold's rate relief (MM-046) run.",
         "dir": "flat"},
        {"day": "Thu", "date": "Jul 16",
         "event": "US retail sales + jobless claims + Hormuz shipping data",
         "consensus": "June retail sales and weekly claims for the first read on whether the oil shock is denting the "
                      "consumer and the labour market the Fed is boxed by; plus Strait traffic (UKMTO advisories, "
                      "tanker rerouting under the toll). Sources: Census, DoL, UKMTO.",
         "view": "The growth-scare tell: whether the toll cost-push is starting to bite demand, the thing credit "
                 "(MM-047, held) and the semis catch-down (MM-050) are positioned for.",
         "asymmetry": "Softening claims/sales + a persistent toll is the growth-scare cocktail (MM-047/050 pay); strong "
                      "data + a toll walk-back drains the premium (MM-044 gives back little by design).",
         "dir": "flat"},
        {"day": "Fri", "date": "Jul 17",
         "event": "Regional-bank earnings (FITB, RF) + housing starts",
         "consensus": "Fifth Third (~$0.98) and Regions Financial (~$0.65) report BMO, extending the NIM/curve read "
                      "into the regionals; June housing starts. The week's Financials verdict lands. Sources: Finnhub, "
                      "Census.",
         "view": "The regional read confirms or breaks the money-centre NIM story (MM-049); the toll/oil follow-through "
                 "into a summer Friday sets the weekend gap risk.",
         "asymmetry": "A clean regional NIM beat broadens the banks-vs-chips RV (MM-049); a credit-cost warning is the "
                      "first growth-scare crack in the cohort the curve was supposed to help.",
         "dir": "flat"},
        {"day": "Mon", "date": "Jul 20 (look-ahead)",
         "event": "Hormuz toll follow-through + into the Jul 28-29 FOMC",
         "consensus": "A week of toll/blockade operation and its shipping/insurance data, plus the market's build "
                      "toward the Jul 28-29 FOMC (hold expected, hawkish hold with hike optionality). Sources: UKMTO, "
                      "CME FedWatch.",
         "view": "Whether the toll is a durable cost-push (structural, own breakevens/steepener) or a negotiating lever "
                 "walked back; the FOMC is the next scheduled decision on a Fed boxed by an oil-CPI and a labour crack.",
         "asymmetry": "A durable toll into a hawkish-hold FOMC is the steepener/breakeven regime (MM-009/048); a "
                      "walk-back plus soft data is the disinflation relief (MM-013/005/046).",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.662 (the stop). Near entry &mdash; flat, the risk-off AUD pressure and an $84-Brent commodity-AUD bid cancel out mid-range; edge thinned, stop close. Trim into any risk-off AUD weakness; tight leash.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.62% &mdash; the LAGGARD; the toll sent the 10Y UP another 6bp and the war gave duration no haven bid. Expressed better via the curve (MM-009); own the inflation via breakevens (MM-048). A break below 4.40% on a soft CORE is the confirmation; ~3bp from the stop &mdash; a very tight rein into the print.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15 (now one day past CPI); stop $4,250. At ~$4,010 &mdash; the war STILL didn't save it; yields rose to 4.62% and gold traded as a real-rates short. Own the regime-change tail via MM-046; the print decides the min-hold exit.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00, now ~0.9pt away. At ~162.1 &mdash; offside (~-1.7%); the risk-off bought the DOLLAR, not the yen, and an $84 Brent + the toll hit the energy-importing yen. Cleaner haven: CHF/JPY (MM-045); sharper oil-importer: USD/KRW (MM-051). Tight leash.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+34bp; ~+125%; target +60bp. The one expression the toll confirms &mdash; the spread widened through the yield backup. Trail the stop; hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182 (distant). At ~1.1390 &mdash; WORKING; the haven-dollar bid and an $84 Brent + the toll hit the euro's terms of trade. Hold the core short; own the hot-CPI/haven-dollar tail via MM-042. A soft CORE that revives the dollar roll is the only trim signal.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold elapsed. At ~4.28% &mdash; offside; the toll, an $84 Brent and Waller's 'hike in the near term' warning re-priced near-term hike risk against it. CPI this morning is the decider; the curve (MM-009) is the higher-conviction sibling. A hot core toward the 4.35% stop is the risk.</li>
</ul>
""",

    "client_ammo": [
        {"q": "A 20% toll on the Strait of Hormuz — is that actually a big deal for markets?",
         "a": ("It's the biggest deal on the tape, because it changes the war from a risk into a price. Every prior "
               "flare-up, the market could discount by the odds of a reopening; a twenty-percent levy on a fifth of "
               "the world's seaborne oil is a cash cost stamped on every barrel, imposed by the US itself. That's why "
               "Brent had its biggest day in six years. It's inflation with a coupon &mdash; and the June CPI this "
               "morning can't see a cent of it.")},
        {"q": "So why would the market rally on the CPI if the war's this bad?",
         "a": ("That's exactly the trap. The June number measures the calm month &mdash; before the toll, when gasoline "
               "had fallen ten percent on the ceasefire &mdash; so the headline prints soft and can look like "
               "disinflation. The tape could grab that and rally for a morning while the underlying core stays sticky "
               "and July's eighty-four-dollar oil re-arms the next print. We read the core, not the headline, and "
               "we're positioned for the inflation that's actually in the pipeline.")},
        {"q": "Should we buy this dip in our tech names?",
         "a": ("Not the biggest one, and less than yesterday. Overnight Korea's chip index crashed nine percent and an "
               "analyst cut SK Hynix's profit numbers &mdash; the memory glut we've been flagging is now in the "
               "estimates, not just the price. You're thirty percent Micron. We'd monetise the still-rich option "
               "premium into any bounce with a collar and own it with a floor, rather than average down on the largest "
               "weight while the crack is spreading.")},
        {"q": "The dollar is up — is that hurting us?",
         "a": ("The opposite this morning. You're a euro-based client with about seventy-two percent in US assets, and "
               "the war-driven flight into the dollar is lifting the euro value of that sleeve &mdash; the war is doing "
               "the currency-hedging work we'd flagged. We'd let it run rather than hedge it away into the bid; the "
               "collar entry has improved, but the immediate risk is de-hedging a tailwind.")},
        {"q": "Why isn't gold rallying in a war?",
         "a": ("Same reason, harder: this war comes through the oil price, and now a literal oil tax, so it's a "
               "cost-push, not a flight to safety. Higher oil lifts real yields, gold hates rising real yields &mdash; "
               "the ten-year rose to about four-point-six and gold fell a second day. Your Xetra-Gold is a rate trade "
               "right now, not a war trade. It only fires if the war becomes a growth scare that forces the Fed to "
               "cut, and we own that specific tail with a small, defined-risk call spread rather than more spot.")},
        {"q": "Where's the cleanest new money going?",
         "a": ("Into the inflation the June number can't see and the split the toll is creating. The cleanest is owning "
               "breakevens &mdash; the market's priced inflation rate, which hasn't caught up to a twenty-percent oil "
               "toll. Then the banks against the chips: the one cohort a steeper curve rewards reports this morning "
               "while the semis are crashing. And the Korean won, the oil-importer taxed by the toll and bled by the "
               "chip-crash outflow at once.")},
    ],

    "ideas_note": (
        "<p>Today's ideas press the NEW information &mdash; the toll, the print-vs-reality gap, and the chip catch-down "
        "&mdash; and do not recycle the vindicated Brent widener (held, paying). <strong>Long 5Y breakevens "
        "(MM-048)</strong> &mdash; the marquee: a 20% oil-transit toll is forward inflation a backward-looking June CPI "
        "cannot contain; own the inflation the print is blind to. <strong>Long XLF vs short SMH (MM-049)</strong> "
        "&mdash; the banks-vs-chips split: the one cohort a +34bp curve rewards reports this morning while the KOSPI "
        "crash bleeds into US semis. <strong>SMH put spread (MM-050)</strong> &mdash; the US catch-down to Korea's "
        "-8.95% crash, defined-risk convexity while VIX is only 16. <strong>Long USD/KRW (MM-051)</strong> &mdash; the "
        "EM oil-importer hit by both the toll's terms-of-trade shock and the chip-crash outflow. The vindicated hedges "
        "(Brent&ndash;WTI MM-044, SPX put spread MM-041, EUR/USD put spread MM-042) are held; the steepener (MM-009) is "
        "trailed; gold spot (MM-005) is held on its min-hold; the gold call spread (MM-046) and HY protection (MM-047) "
        "are held; GS earnings vol (MM-043) is held into the print.</p>"
    ),

    "event_radar_note": (
        "<p>The toll and the trap: the war escalated into a tax. Trump reimposed the blockade and declared a 20% toll "
        "on ALL Hormuz cargo ('Guardian of the Strait'); a third night of US strikes hit Bandar Abbas, Kish, Qeshm and "
        "Abu Musa; Iran hit two tankers in Omani waters. Brent posted its biggest single-day gain in 6+ years (+9.59% "
        "to $83.30; ~$84.84 pre-market). The dollar is bid (DXY ~100.9, USD/JPY ~162.1), the 10Y +6bp to ~4.62%, gold "
        "FELL a second day (~$4,010 &mdash; the cost-push, not the haven), and the KOSPI CRASHED -8.95% (SK Hynix -15%) "
        "as Korea Investment cut its Q2 profit. It all lands the same morning as June CPI (08:30, PENDING) &mdash; a "
        "backward-looking trap blind to July's oil &mdash; and the big-bank kickoff (JPM, GS, C, BAC, WFC BMO, "
        "PENDING). MM-044 (Brent&ndash;WTI) is vindicated; TotalEnergies leads; MM-041/042 still work; the steepener "
        "(MM-009) widened; the short-10Y (MM-004) and short-2Y (MM-013) lag. Fresh ideas press the new information: "
        "long 5Y breakevens, long XLF vs short semis, a semis put spread, and long USD/KRW.</p>"
    ),

    "burry_tell": (
        "The chip crash looks like it is about Iran; the structural signal is that it isn't &mdash; and this week the "
        "signal stopped hiding. The capacity race the AI narrative funds does not pause for a war: Hynix, Samsung and "
        "Micron keep pouring capital into high-bandwidth memory into the same demand assumption, and memory is a "
        "commodity whose cycle has never actually been broken, only postponed. For weeks that was a thesis about price. "
        "On Monday it became a number: Korea Investment cut SK Hynix's Q2 operating profit some 8% below consensus on "
        "slower-than-expected HBM4 shipments, the Korean index crashed almost 9%, and the memory names fell 15%. A war "
        "headline is the perfect cover for a glut to build &mdash; when the tape falls on Iran, the decline reads as "
        "geopolitics &mdash; but the capacity added ahead of demand, how every glut in the history of the industry has "
        "been built, is now visible in an analyst's model, not just the tape. Over the next two-to-three quarters this "
        "resolves one of two ways: AI demand keeps outrunning the new supply and the 'broken cycle' story survives "
        "another few quarters; or the capacity lands first, memory prices roll, and the most levered names fall hardest "
        "&mdash; a fall the market will blame on the next headline rather than the supply. The Fable book is 30% "
        "Micron, the single best expression of the bet that the cycle is dead, and this is the second and larger crack. "
        "The discipline is to monetise the still-rich volatility into any bounce with a collar or overwrite &mdash; not "
        "to buy the dip on a name whose real risk the war is conveniently hiding."
    ),

    "earnings_summary": (
        "Three ideas this refresh, all from the big-bank Q2 kickoff (Tue Jul 14 BMO, reporting into the 08:30 CPI). GS "
        "(Long, High &mdash; data gap flagged): the widest implied move in the cohort (~6.0%) and the most divided "
        "sell-side (15 buy / 15 hold / 2 sell) mean an investment-banking beat has the most room to re-rate into a "
        "steeper curve. JPM (Long, Medium): the bellwether &mdash; a clean NIM print on a +34bp 2s10s sets the cohort "
        "tone, but a well-owned name has less asymmetry. C (Long, Medium): the value leg &mdash; the biggest serial "
        "beater (13-20% surprises four quarters running) on the cheapest large-cap multiple, a fifth beat is the "
        "re-rating catalyst. All positioning pillars are tagged 'estimated' (Finnhub short-interest unavailable), so GS "
        "is capped at 'High &mdash; data gap flagged' rather than clean High. The macro cross-current is now doubled: "
        "the cohort reports the SAME 08:30 minute as June CPI and into a war that escalated into a 20% Hormuz toll and "
        "an $84 Brent &mdash; either can swamp a good print, hence the defined-risk (call-spread) expression on GS, and "
        "the banks-vs-chips RV (MM-049) that owns the cohort the steeper curve rewards against the semis it doesn't."
    ),
    "earnings_why": (
        "The universe filter is applied before scanning: market cap $10bn+, geographies US (primary) and South Korea "
        "(secondary), sectors Technology / Financials / Industrials / Utilities only. The earnings_data.md feed "
        "(Finnhub, 2026-07-13 06:00 UTC) returns the qualifying Financials reporting Jul 14-17 as Q2 bank season opens: "
        "JPM, GS, C, BAC, WFC (Jul 14), MS, BLK, BNY (Jul 15) and FITB, RF (Jul 17) &mdash; all >$10bn, all US, all "
        "Financials. Three are surfaced (GS, JPM, C) as the highest-asymmetry expressions of the same steeper-curve/"
        "IB-re-acceleration thesis; the money-centre names with the clearest read and the widest implied moves. The "
        "regionals (FITB, RF) and the wealth/custody names (MS, BLK, BNY) are noted but not rendered as separate ideas "
        "&mdash; they are lower-beta reads on the same NIM tailwind, and padding the section with the full cohort would "
        "dilute the signal. Consensus EPS/revenue, recommendation splits and surprise history are all SOURCED from "
        "Finnhub; short interest is unavailable, so the positioning pillar is tagged estimated."
    ),

    "book_aim": (
        "Astride the toll reprice, with the oil hedge on its best day in years and fresh risk rotating into the "
        "inflation and the chip crack the tape hasn't priced. The energy length is the standout war hedge: "
        "TotalEnergies leads as Trump's 20% Hormuz toll sent Brent +9.59% to $83.30, its biggest single-day gain in "
        "6+ years &mdash; press it convexly (Brent-vs-WTI, MM-044, already paying), not with spot. The AI sleeve is the "
        "loser: the KOSPI crashed -8.95% and Korea Investment cut SK Hynix's Q2 profit ~8% below consensus, so the 30% "
        "Micron weight takes the direct hit &mdash; the SECOND, bigger crack of the capacity-race tell, so monetise the "
        "still-rich IVol into any bounce with urgency, do NOT buy the dip. The rate book: the 2s10s steepener (MM-009) "
        "widened to ~+34bp as the one expression the toll confirms, while the short-10Y (MM-004) and short-2Y (MM-013) "
        "lag on the yield backup and gold (MM-005) fell a second day. The FX offset is real &mdash; the ~72% USD sleeve "
        "is a tailwind on the haven-dollar bid, so let it run rather than hedge into it. For the week into June CPI "
        "(Tue 08:30, a backward-looking trap) and the bank kickoff: hold and trail the steepener; do NOT add duration; "
        "hold the euro short (MM-012) and carry the hot-core tail in options (MM-042 held); hold gold's regime-change "
        "tail (MM-046) and HY protection (MM-047) at the min-hold; and rotate fresh risk into the toll where it isn't "
        "priced &mdash; long 5Y breakevens (MM-048), long XLF vs short semis (MM-049), a semis put spread (MM-050), and "
        "long USD/KRW (MM-051). The vindicated hedges (MM-044/041/042) and GS earnings vol (MM-043) are held, not chased."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); no option line is open this "
                 "refresh. This is a Tuesday PRE-MARKET brief (US cash open ~09:30 ET) into an 08:30 CPI, so "
                 "equity-index and rate marks may reflect the Mon Jul 13 close / live futures until the cash session "
                 "prints.")
    },
    "idea_selection": [
        {"label": "Long US 5Y breakeven inflation — own the inflation the June CPI can't see (MM-048)", "in": True,
         "text": ("The marquee fresh idea. A 20% toll on a fifth of world seaborne oil is a structural cost-push a "
                  "backward-looking June CPI (soft on a 10% June gasoline drop) contains none of. Breakevens price the "
                  "forward inflation directly and have lagged the oil move &mdash; own the gap between the print and "
                  "the pipeline. The rates-market completion of the curve (MM-009) and the oil widener (MM-044).")},
        {"label": "Long XLF vs short SMH — the banks-vs-chips split (MM-049)", "in": True,
         "text": ("The beta-neutral expression of the day's two stories. Banks report into a +34bp curve that lifts NIM "
                  "&mdash; the one cohort the war-steepening rewards &mdash; while the KOSPI's -8.95% crash and Korea "
                  "Investment's SK Hynix profit cut bleed into US semis. Long the cohort the toll-and-curve regime "
                  "helps, short the one it crashes, with little index beta.")},
        {"label": "SMH put spread — the US catch-down to Korea's crash (MM-050)", "in": True,
         "text": ("The vol expression of the chip catch-down. The KOSPI crashed -8.95% (SK Hynix -15%, Samsung -10%) but "
                  "US semis have only partly followed, and index vol is cheap (VIX ~16). A defined-risk put spread buys "
                  "convexity on the gap into a two-sided CPI and an escalating war. The options completion of the book's "
                  "Micron/AI-glut view. Max loss capped.")},
        {"label": "Long USD/KRW — the oil-importer hit by the toll and the outflow (MM-051)", "in": True,
         "text": ("Korea imports essentially all its oil, so the toll is a terms-of-trade drag on the won; and it is the "
                  "chip heart, so the -8.95% crash forces equity-outflow won selling. Long USD/KRW owns both in one "
                  "cross with less crowding than the long-USD-majors trade. The EM-FX completion of the toll-and-crash "
                  "thesis. Complements the book's short USD/JPY (MM-007).")},
        {"label": "Vindicated hedges (Brent–WTI MM-044, SPX put spread MM-041, EUR/USD put spread MM-042) — held, in the money", "in": False,
         "text": ("MM-044 caught Brent's biggest day in six years; MM-041/042 own the index gap and the haven dollar. "
                  "Held, not chased and not re-added; the fresh money presses the NEW information (MM-048/049/050/051), "
                  "because recycling a trade that has already paid is not an edge. GS earnings vol (MM-043), the gold "
                  "call spread (MM-046) and HY protection (MM-047) are also held.")},
        {"label": "2s10s steepener (MM-009) — harvest and trail, don't press", "in": False,
         "text": ("The one rate expression the toll confirms: ~+34bp, ~+125%, widening through the yield backup. Held "
                  "and trailed, not added &mdash; a hot core could bear-flatten the front. The consensus-agnostic "
                  "steepener remains the higher-conviction rate trade than the directional front-end fade (MM-013).")},
        {"label": "Long gold spot (MM-005) — hold on the min-hold; own the tail via MM-046 instead", "in": False,
         "text": ("Underwater ~-11% and well below its $4,250 stop, but held to the ~Jul 15 min-hold (now one day past "
                  "CPI). The war STILL didn't save it &mdash; yields rose to 4.62% and gold traded as a real-rates "
                  "short. The asymmetric upside is owned with DEFINED risk via the Sep call spread (MM-046), not by "
                  "adding underwater spot.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 17.0},
        {"label": "VIX",   "value": round(_g("vix") or 16.2, 2)},
        {"label": "VIX3M", "value": 18.0},
        {"label": "VIX6M", "value": 19.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.24, 3)},
        {"label": "5Y",  "value": 4.42},
        {"label": "10Y", "value": round(_g("us10y") or 4.62, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 5.05, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-048", "trade": "Long US 5Y breakeven inflation (own the inflation the CPI can't see)",
            "asset_class": "Rates (inflation)", "structure": "TIPS vs nominal / inflation swap",
            "entry": "~market breakeven", "stop": "breakeven < pre-escalation level", "target": "+25-40bp wider",
            "conviction": 7,
            "conviction_breakdown": {"gap": 3, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The marquee fresh idea: the most inflationary policy shock of the year lands the same morning as "
                       "the most disinflationary data print of the year, and breakevens own the gap. Trump's 20% Hormuz "
                       "toll and an $84 Brent are a delivered-price cost-push on a fifth of world seaborne oil; June "
                       "CPI, measured in the calm pre-toll month (soft on a 10% June gasoline drop), contains none of "
                       "it. If the tape misreads the soft headline as disinflation and breakevens sit still, the trade "
                       "owns the re-arm; if the market wakes to the toll, breakevens widen directly. It is the "
                       "rates-market completion of the curve (MM-009) and the oil widener (MM-044)."),
        },
        {
            "id": "MM-2026-049", "trade": "Long XLF vs short SMH (banks the curve helps vs chips it crashes)",
            "asset_class": "Equity (sector RV)", "structure": "beta-neutral pair",
            "entry": "~market ratio", "stop": "XLF/SMH ratio < pre-earnings level", "target": "+5-8% ratio",
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 2, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The cleanest banks-vs-chips expression of the split tape. The same regime that crushes semis "
                       "&mdash; a war-driven steepening, an oil cost-push, real yields backing up &mdash; is the regime "
                       "that helps banks, because a +34bp curve is a NIM tailwind and the big-bank cohort reports into "
                       "it this morning (GS +32% IB fees, the widest implied move). Meanwhile the KOSPI's -8.95% crash "
                       "and Korea Investment's SK Hynix profit cut are the glut crack US semis have not fully repriced. "
                       "Long XLF / short SMH owns the divergence with little index beta &mdash; which cohort the "
                       "toll-and-curve regime rewards and which it punishes."),
        },
        {
            "id": "MM-2026-050", "trade": "Buy an SMH put spread (the US catch-down to Korea's crash)",
            "asset_class": "Equity (options)", "structure": "put spread",
            "entry": "~5%/12%-OTM", "stop": "—", "target": "~4-5x on a semis catch-down",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to Aug expiry", "min_hold_days": 0,
            "thesis": ("The options expression of the chip catch-down. Korea &mdash; the memory heart of the AI-capex "
                       "trade &mdash; crashed 8.95% overnight on an analyst cutting SK Hynix's numbers, and the US "
                       "semis complex has only partly followed. With VIX still ~16, a defined-risk SMH put spread buys "
                       "convexity on the gap between the KOSPI's -9% and the SOX's smaller move, into a two-sided CPI "
                       "and an escalating war. It is the vol-market completion of the book's Micron/AI-glut view (the "
                       "Burry tell) and the short leg of MM-049 in options form &mdash; own the catch-down with capped "
                       "risk rather than fight the whole complex in spot."),
        },
        {
            "id": "MM-2026-051", "trade": "Long USD/KRW (the oil-importer hit by the toll and the outflow)",
            "asset_class": "FX", "structure": "spot",
            "entry": "~market", "stop": "recent range low", "target": "+3-4%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The FX expression of the day's two shocks landing on one country. Korea imports essentially all "
                       "its oil, so the 20% Hormuz toll and an $84 Brent are a pure terms-of-trade drag on the won; and "
                       "Korea is the semiconductor heart of the AI trade, so the KOSPI's -8.95% crash forces "
                       "equity-related won selling. Long USD/KRW owns both &mdash; the oil-importer penalty and the "
                       "capital-outflow bid for dollars &mdash; in a cross with far less crowding than the "
                       "long-USD-vs-EUR/JPY majors trade the whole market is already in. The EM-FX completion of the "
                       "same toll-and-chip-crash thesis MM-048/049/050 express in rates and equities."),
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
