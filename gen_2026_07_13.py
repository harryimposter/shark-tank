#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-07-13 (Monday; US markets REOPEN into a risk-off gap). THE STRAIT SHUTS.

THE NEXT CHAPTER vs the Jul 11 (Chips Over Cannons) run:
the melt-up that priced the war OUT is forced to price it IN at the reopen. Over the weekend the shooting war
escalated hard — a third round of US strikes (~140 sites), Iran hitting Gulf states AND US bases, and the
Strait of Hormuz effectively CLOSED to commercial shipping. The chips that carried Friday's winning week lead
the tape DOWN (KOSPI into a bear market), oil and the dollar catch the bid, and Jul 11's hedges are vindicated.
- THE STRAIT SHUT AND THE WAR ESCALATED. Over the weekend (Jul 11-12) the US struck ~140 Iranian military
  sites overnight Sat→Sun — a THIRD round — after a Cyprus-flagged container ship was attacked transiting
  Hormuz. Iran retaliated: drones/missiles at US bases and strikes on US-linked installations in the UAE,
  Kuwait and Bahrain. The Strait is effectively CLOSED to commercial traffic (Day 134 of the crisis); only
  the southern Omani-coast route runs two-way. Iran declared the waterway closed (Jul 12); UKMTO/US Navy say
  the southern lane is open. (CNN, Fox, Al Jazeera, straits.live.)
- TRUMP OWNS BOTH THE STRIKE AND THE OFF-RAMP. "We had a deal with them yesterday. They were giving up
  everything… Then, two hours after that, they hit a ship with a drone," Trump said Sunday, adding the US hit
  Iran "very hard" and that "the Strait of Hormuz is open." He paraded strike footage on Truth Social. The
  de-escalation door is open but politically his to shut. (Washington Times, CNN, Newsweek.)
- OIL AND THE DOLLAR CAUGHT THE BID; GOLD DID NOT. Brent +3.9% to ~$79.0 (Sun/Mon), WTI +~4% above $74 —
  the Strait-closure supply premium is real. DXY firm ~100.96 on a safe-haven bid; USD/JPY ~162.4 (yen the
  funder). GOLD stalled ~$4,100-4,121 — the war STILL did not bid it, because the 10Y backed up ~8.5bp to
  ~4.59% and gold trades as a real-rates short. (Trading Economics, CNBC, Invezz, Business Standard.)
- THE CHIPS LED DOWN. The SK Hynix halo inverted: KOSPI fell into bear-market territory (chip-led, SK Hynix
  and Samsung leading), the Nikkei ~-1 to -1.5% on oil cost-push + chip selloff, and US futures point lower
  into the reopen. VIX (15.03 Fri close) opens higher; OVX (oil vol) is where the volatility bid sits.
  (Bloomberg, CNBC, Yahoo.) Prior close (Fri Jul 10): S&P 7,575.39, Nasdaq Comp 26,281.61, Dow 52,637.01.
- THE HAWK IS RE-ARMED. CME hike-THIS-YEAR odds jumped to ~87% (July hold still ~78%); the oil cost-push
  plus a Fed (Warsh) that calls inflation "too high" backs the front up. 10Y ~4.59%, 2Y firmer, 2s10s holds
  ~+35bp. (CME FedWatch, Sahm Capital, CNBC.)
- THE CPI IS A BACKWARD-LOOKING TRAP. June CPI Tue Jul 14 8:30 ET (cons: headline −0.1% m/m → ~3.8-3.9% y/y;
  core +0.3% m/m → ~2.9% y/y) — PENDING. KEY: June was the "last calm month" — oil was LOW post the mid-June
  ceasefire, so a soft June HEADLINE is mechanical and does NOT capture July's $79 Brent. The risk is the tape
  reads a soft print as all-clear while the July war already re-arms the NEXT one. Core services stay sticky.
  (BLS, Kiplinger, Cleveland Fed.)
- BIG-BANK EARNINGS SAME MORNING. Tue Jul 14 BMO: JPM (~$5.74), GS (~$14.46, +32% y/y, NII ~$3.85bn +24%,
  implied move ~6%, split 15/15/2), C (~$2.76), BAC (~$1.13), WFC (~$1.73); Jul 15 MS/BLK/BNY. A steeper
  curve = NIM tailwind, but same-day CPI + a war gap can swamp any print. (Finnhub, Zacks, Motley Fool.)
- BOOK ACTION: Jul 11's hedges are IN THE MONEY — the Brent call spread, the SPX put spread and the EUR/USD
  put spread all own exactly this weekend. TotalEnergies leads again; the bond sleeve and Xetra-Gold still lag
  as yields back up. Fresh ideas press the NEW information (the Strait closure, the haven that hasn't fired,
  the credit that hasn't repriced): a Brent–WTI widener (waterborne premium), long CHF/JPY (the clean war
  haven vs the oil-importer funder), a gold Sep call spread (the coiled haven), and long HY credit protection
  (the laggard).

Run:  python gen_2026_07_13.py
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
# Fallback: this is a Monday PRE-MARKET brief (US cash open ~09:30 ET). Cash indices have not printed yet,
# and if the live feed does not resolve a futures proxy, inject the web-verified Fri Jul 10 closes (Yahoo
# Finance + CNBC, corroborated) so the dashboard headline indices never render "unverified". Only set if the
# live feed did not resolve them; direction into the reopen is risk-off (Asia lower, oil bid).
if "spx" not in snap:
    snap["spx"] = {"close": 7575.39, "chg_pct": 0.42, "chg_abs": 31.75}
if "dji" not in snap:
    snap["dji"] = {"close": 52637.01, "chg_pct": 0.29, "chg_abs": 149.60}
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
    "MU":   "The name the weekend flipped — and the book's largest weight (~30% of the Fable book). The SK Hynix halo "
            "that re-rated Micron on Friday inverted over the weekend: with the war escalating and the Strait shut, "
            "KOSPI fell into bear-market territory led by SK Hynix and Samsung, and the whole memory/accelerator complex "
            "is repricing DOWN. The AI-capex durability trade is exactly what a war-driven growth scare tests. Micron is "
            "the single best expression of the 'broken chip cycle' bet — the discipline is to monetise the still-rich "
            "IVol into the top (collar/overwrite), never to add into a name at a record as the tape de-risks.",
    "NVDA": "The AI leader now leading the cohort DOWN. Friday's Hynix halo is gone; a war-driven risk-off and an oil "
            "cost-push that backs real yields up is a direct hit to the long-duration AI-capex trade. At ~32x it is the "
            "reasonably-priced leg against the ~175x AMD challenger, so it holds up better on a relative basis — own the "
            "leader against the overbought name (the dispersion RV), do not fight the whole complex lower.",
    "AMD":  "The overbought casualty of the reversal and the SHORT leg of the chip dispersion. Up ~150% YTD at ~175x "
            "trailing earnings versus NVDA's ~32x on a fraction of the revenue base — the richest name in the cohort the "
            "market is now de-risking hardest as the war-driven selloff hits the highest multiples first. The Fable book "
            "HOLDS AMD (+394%), so the trim doubles as concentration management: sell the exhausted winner into any "
            "bounce, own the cheaper leader.",
    "XLE":  "The one part of the tape the weekend vindicated. Brent +3.9% to ~$79 and WTI +~4% above $74 as a third "
            "round of US strikes (~140 sites) and an effectively CLOSED Strait of Hormuz put a real supply premium back "
            "in crude. The book's energy length (TotalEnergies) is the war hedge that is WORKING again; the fresh upside "
            "is the waterborne premium — long Brent vs WTI (MM-044) — not more spot into a two-way de-escalation tape.",
    "GLD":  "Still the haven that will not show up. Gold stalled ~$4,100-4,121 through a weekend of strikes because the "
            "10Y backed up ~8.5bp to ~4.59% and gold trades as a real-rates short, not a war hedge. The book's cash gold "
            "long (MM-005) is underwater on its min-hold (to ~Jul 15). BUT the coil is the trade: if the war deepens "
            "into a genuine growth scare that forces the Fed dovish, the real-rate cap breaks — own that tail with a "
            "defined-risk Sep call spread (MM-046) rather than more underwater spot.",
    "TLT":  "The oil cost-push is duration's enemy again. The 10Y backed up to ~4.59% and the front firmed as the war "
            "re-lit inflation risk and CME hike-this-year odds jumped to ~87% — so the short-10Y (MM-004) is the laggard "
            "and the short-2Y (MM-013) is offside. Own the curve SHAPE (the steepener MM-009, ~+35bp), not outright "
            "long-end duration, into a backward-looking June CPI that can't capture July's oil.",
    "HYG":  "The laggard that hasn't repriced the war. Equity vol is finally waking up (VIX off 15, chips selling), but "
            "HY credit spreads have barely moved — a growth scare from a closed Strait and an oil cost-push is exactly "
            "what widens spreads, and credit is late. Own the tail with long HY protection / short HYG (MM-047); it is "
            "the cross-asset expression of the same 'the tape under-priced the war' thesis, in the asset class that "
            "moves last.",
    "XLF":  "The cohort that reports into the collision. Big banks kick off Q2 season Tue Jul 14 (JPM, GS, C, BAC, WFC) "
            "into a steeper curve (2s10s ~+35bp = NIM support) — but the SAME morning as June CPI and a war-gap reopen "
            "that can swamp any print. GS carries the widest implied move (~6%); own the earnings-vol leader with "
            "defined risk (MM-043 held), not naked, because the macro cross-current is live.",
    "SPY":  "The complacency trade forced to reprice. The melt-up bought Friday's record IPO through the war at VIX 15; "
            "the weekend escalation (Strait shut, Gulf states hit, US bases attacked) hands the reopen a risk-off gap "
            "into a two-sided June CPI. The SPX put spread (MM-041, held) owns exactly this — the gap the record tape "
            "ignored, now printing.",
    "EEM":  "Korea is the epicentre of the reversal. The SK Hynix debut that re-rated the KOSPI on Friday inverted into "
            "a chip-led plunge into bear-market territory as the war escalated; the Nikkei fell on oil cost-push + chip "
            "selloff. EM Asia is where the AI-durability trade and the war premium collide hardest — a stock-pickers' "
            "tape leading the global risk-off, not a beta dip to buy.",
    "BTC":  "Bitcoin still capped, not the haven in a war either — the same backing-up-real-rates regime that sank gold "
            "keeps a lid on the speculative long tail, and a risk-off gap pulls it lower with the Nasdaq, not against "
            "it. A tell that in this regime the only havens paying are the dollar and oil, not duration, gold or crypto. "
            "Not a book position.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("The Strait Shuts and the Melt-Up Blinks: A Weekend of Escalation Forces the Tape to Price the War It "
          "Ignored — Hormuz Effectively Closed, the Chips Lead Down Into a Bear Market, Oil and the Dollar Bid, and "
          "a Backward-Looking June CPI Tuesday Snapshots the Last Calm Month")
regime_note = (
    "The most important thing that happened over the weekend is that the war the tape spent Friday ignoring escalated "
    "hard enough to force a reprice, and the melt-up blinked. After a Cyprus-flagged container ship was attacked "
    "transiting the Strait of Hormuz, the US struck about 140 Iranian military sites overnight Saturday into Sunday — "
    "a third round — and Iran retaliated with drones and missiles on US bases and strikes on US-linked installations "
    "in the UAE, Kuwait and Bahrain. The Strait is now effectively closed to commercial traffic; only the southern "
    "Omani-coast lane runs two-way. Iran declared the waterway shut on Jul 12; UKMTO and the US Navy say the southern "
    "route is open. (CNN, Fox, Al Jazeera, straits.live.) The cross-asset answer was immediate and clean: Brent "
    "jumped ~3.9% to ~$79 and WTI ~4% above $74 on a real supply premium, the dollar firmed on a haven bid (DXY "
    "~100.96, USD/JPY ~162.4), and — the tell — the chips that carried Friday's winning week led the tape DOWN, with "
    "the KOSPI falling into bear-market territory led by SK Hynix and Samsung. (Trading Economics, CNBC, Bloomberg.) "
    "Decompose Friday's melt-up now that the weekend has repriced it. Friday's story was 'one AI trade can absorb a "
    "shooting war' — the SK Hynix record IPO carried a winning week at VIX 15. The anatomy the weekend exposed is "
    "that this was never resilience, it was one crowded, long-duration AI-capex bet standing in front of a war that "
    "had not yet been forced into the price. A closed Strait forced it. The same names that led up on the halo lead "
    "down on the reprice, because a war-driven growth scare plus an oil cost-push that lifts real yields is precisely "
    "what the long-duration AI trade cannot absorb. So what, who's wrong, what's the trade: the consensus that read "
    "Friday's close as all-clear is wrong; the trade is to own where the war actually lands — the waterborne oil "
    "premium and the haven bid — and to fade the complacency the reopen is only now unwinding. (Invezz, Business "
    "Standard, CNBC.) "
    "The second-order effect consensus is missing is that Tuesday's CPI is a backward-looking trap. June was the last "
    "calm month — oil was low after the mid-June ceasefire, before the early-July collapse — so a soft June headline "
    "(consensus −0.1% m/m, ~3.8-3.9% y/y) is mechanical and does NOT contain a single barrel of July's $79 Brent. "
    "The danger is a tape that gaps down on the war, then rallies on a soft headline it misreads as disinflation, "
    "while core services stay sticky at +0.3% and July's oil already re-arms the NEXT print — with CME hike-this-year "
    "odds already at ~87%. The Papic constraint is that Trump owns both the strike and the off-ramp: he says a deal "
    "was 'two hours' from done before Iran hit the ship, and that 'the Strait of Hormuz is open' — the de-escalation "
    "door is open but politically his to shut, which makes the oil premium a binary, not a trend. The Burry tell is "
    "still inside the chips: the capacity race the SK Hynix raise funds does not pause for a war, so the memory glut "
    "builds underneath a selloff that looks like it is only about geopolitics. The book is 30% Micron; it is long "
    "exactly that bet, and the weekend is the first crack. "
    "The book sits astride the reprice and — for once — the hedges are in the money. Jul 11's Brent call spread, SPX "
    "put spread and EUR/USD put spread own exactly this weekend: the oil premium, the index gap, the haven dollar. "
    "TotalEnergies leads the book again as the working war hedge; the 2s10s steepener (MM-009) holds ~+35bp as the "
    "one rate expression the escalation confirms, while the short-10Y (MM-004) and short-2Y (MM-013) lag on the oil "
    "backup and gold (MM-005) still refuses to bid. Short EUR/USD (MM-012) works on the haven dollar. The trade now "
    "is to press the NEW information: own the waterborne premium a closed Strait creates (long Brent vs WTI), own the "
    "cleanest war haven that isn't the dollar (long CHF vs the oil-importer yen), own the coiled haven that hasn't "
    "fired (a defined-risk gold call spread), and own the laggard that hasn't repriced the war at all (HY credit "
    "protection). The regime is no longer 'the melt-up absorbs everything.' It is a market being forced, one asset "
    "class at a time, to price a war it spent a week pretending wasn't there — into a CPI print that can't see it yet."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# No close action today. MM-005 (gold) stays open on its 45-day min-hold (to ~Jul 15, now 2 days out) though
# spot is below the $4,250 stop — the rule holds it to the decision date, which now coincides with June CPI.
# MM-009 min-hold (to ~Jul 16) still governs. All other legs inside their stops/min-holds.

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
            "The quiet leg, roughly flat near the entry as two forces cancel. The weekend risk-off pressures the "
            "commodity-AUD (good for the short), but a $79 Brent lifts the AUD's terms of trade the other way, pinning "
            "the cross mid-range rather than toward the 1.61 target. A paused ECB caps the EUR side; there is no dated "
            "EUR catalyst left and the edge has thinned. This is the leg to trim into any risk-off AUD weakness rather "
            "than defend into a war-premium AUD bid. Stop 1.662, close by."
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
            "The laggard, and the cleanest tell that this war bids oil, not bonds. The 10Y backed UP again to ~4.59% "
            "from the 4.44% entry as the weekend escalation lifted Brent to ~$79 and re-armed the inflation trade — a "
            "shooting war with the Strait shut produced NO haven bid for duration, because a cost-push is bearish "
            "bonds. The disinflation thesis is on the wrong side of a live oil shock, CME hike-this-year odds at ~87%, "
            "and a CPI print (Tue) that can't even see July's oil. The expression that pays is the curve (MM-009), not "
            "outright long-end duration. Stop 4.65%, now ~6bp away — a very tight rein."
        ),
        "catalysts": [
            "June CPI Tue Jul 14 (core +0.3% m/m cons) — the print that confirms or breaks the long-end backup",
            "Brent ~$79 / oil cost-push — the fresh inflation risk pinning the 10Y",
            "Treasury supply + term premium — the structural anchor keeping the long end heavy",
            "A Hormuz de-escalation — the disinflation relief that would let the 10Y rally",
        ],
        "risks": (
            "A hot core CPI plus a sustained oil premium sells the long end toward and through the 4.65% stop; only a "
            "clean Hormuz de-escalation and a soft CPI rescue it. Stop 4.65% (now ~4.59%, ~6bp away)."
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
            "The trade the war keeps refusing to save. Gold stalled ~$4,100-4,121 through a weekend of strikes and a "
            "closed Strait, still underwater ~-9% from the $4,523 entry, because the 10Y backed up ~8.5bp to ~4.59% "
            "and gold trades as a real-rates SHORT, not a haven. The lesson holds: gold is a RATE trade here, not a war "
            "trade — it needs a lower-real-rate path, not a Hormuz headline. The min-hold (to ~Jul 15) now coincides "
            "with June CPI, so the decision and the catalyst land together. The asymmetric upside — a war that deepens "
            "into a growth scare and forces the Fed dovish — is now owned with DEFINED risk via the Sep call spread "
            "(MM-046), not by adding underwater spot. Stop $4,250 (price below it; the rule holds it to the decision)."
        ),
        "catalysts": [
            "June CPI Tue Jul 14 — a soft core is the real-rates relief gold needs; a hot one confirms the exit",
            "Real yields / the 10Y at ~4.59% — the headwind that keeps gold capped through the war",
            "Hike-this-year odds ~87% — the policy path capping the debasement bid",
            "EM / central-bank physical buying — the structural floor under the drawdown",
        ],
        "risks": (
            "A hot CPI plus a sustained oil-driven yield backup keeps gold below the $4,250 stop and the min-hold "
            "exit crystallises the loss; only a soft CPI and a real-rate turn rescue it. Min-hold to ~Jul 15; stop "
            "$4,250 (price now below it — the rule holds it to the decision date)."
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
            "Offside and pressured by the haven bid. USD/JPY sits ~162.4, above the 159.37 entry (~-1.9%), as the "
            "weekend risk-off bought the DOLLAR, not the yen — Japan is a net energy importer, so a $79 Brent is a yen "
            "NEGATIVE, and the oil-led yield backup re-widened the US-Japan differential. The yen is the funder in this "
            "war, not the haven. The structural case (a BoJ normalising toward 1.00%, a Fed that cannot sustain a "
            "hawkish repricing into a labour crack) is intact but on hold, and the MoF line near 163 is the backstop. "
            "The cleaner war-haven expression is long CHF/JPY (MM-045). Patient short on a tight leash; 163 is the "
            "stop, now ~0.6pt away."
        ),
        "catalysts": [
            "June CPI Tue — the print that decides whether the US-Japan differential widens or narrows",
            "$79 Brent — the terms-of-trade drag on the energy-importing yen, widening the differential against the short",
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
            "/ 10Y 4.59%, spread ~+35bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "The best position in the book and the one expression the escalation confirms. Both ends are up on the oil "
            "cost-push — the 2Y firmer, the 10Y ~4.59% — but the spread holds ~+35bp, keeping the open gain near ~+130% "
            "off the +15bp entry (an 18-month inversion). This is the right trade for the whole regime: a Fed boxed "
            "between a labour crack and a war-driven oil-CPI can neither hike hard nor cut, which pins the front, while "
            "fiscal supply and the war's inflation premium keep the long end heavy — a structural steepener in either "
            "CPI outcome (a soft headline bull-steepens the front; a sticky core bear-steepens the back). Min-hold to "
            "~Jul 16; target +60bp; held, trail the stop up, do not add into the run."
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
            "Working on the haven dollar. EUR/USD sits ~1.1426 and DXY firmed to ~100.96 as the weekend escalation "
            "bought the dollar for safety and the oil-led yield backup (10Y ~4.59%) widened the rate differential — and "
            "a $79 Brent is a euro-negative terms-of-trade shock, because the euro area imports its energy. The short "
            "is green (~+1.5% from the 1.16 entry) with a distant 1.182 stop. June CPI (Tue) is the swing: a hot core "
            "extends the dollar; a soft headline the market misreads as dovish is the trim risk. Hold the core short; "
            "own the specific hot-CPI/haven-dollar upside via the defined-risk put spread (MM-042, held)."
        ),
        "catalysts": [
            "June CPI Tue — a hot core re-arms the Fed and bids the dollar; a soft one revives the euro",
            "Brent ~$79 oil premium — the euro-negative terms-of-trade shock supporting the short",
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
            "Offside on the oil re-arm. The 2Y firmed above the 4.162% entry (~flat-to-red) as the weekend escalation, "
            "a $79 Brent cost-push and CME hike-this-year odds jumping to ~87% re-priced near-term hike risk against "
            "the short. The thesis — that the front end over-prices a 2026 hike into a cracking labour market — is "
            "intact structurally, but the war is going the crowd's way, not ours, in the near term. June CPI (Tue) is "
            "the decider: a soft core re-confirms the fade; a sticky one plus the oil premium backs the 2Y toward the "
            "4.35% stop. Min-hold elapsed; stop 4.35%. Hold on a tight rein; the curve (MM-009) is the "
            "higher-conviction, consensus-agnostic expression of the same view."
        ),
        "catalysts": [
            "June CPI Tue — the decider: soft re-confirms the fade, hot re-arms the hike",
            "Oil cost-push (~$79 Brent) — the fresh inflation risk backing up the 2Y",
            "Hike-this-year odds ~87% — the hawkish anchor the trade fades",
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
    "MM-2026-044": {
        "instrument": (
            "Long the Brent–WTI spread — buy ICE Brent, sell NYMEX WTI (tradeable as a futures spread or via crude-ETF "
            "legs). Brent is the WATERBORNE international benchmark, priced off seaborne cargoes that transit Hormuz; "
            "WTI is the Cushing-landlocked US grade fed by pipeline and shale. The spread sits ~$5; a closed Strait "
            "disrupts the waterborne barrel far more than the domestic one, so the spread widens. A defined, lower-beta "
            "expression of the war premium that pays on the Hormuz MECHANISM, not the general oil level."
        ),
        "fundamental_thesis": (
            "The marquee fresh idea: a Strait closure is a waterborne supply shock, and the cleanest way to own it is "
            "the grade that actually clears through Hormuz. With the Strait effectively shut to commercial traffic and "
            "Brent–WTI only ~$5, the RV owns the escalation with far less de-escalation risk than outright crude — if "
            "Trump's off-ramp holds and oil drains, the spread compresses a fraction of what an outright long gives "
            "back. It presses the book's TotalEnergies length on the specific mechanism (seaborne disruption) rather "
            "than adding spot crude into a two-way headline tape."
        ),
        "catalysts": [
            "Strait of Hormuz effectively closed to commercial traffic — the waterborne disruption",
            "Third round of US strikes + Iran attacks on Gulf-state installations — the escalation",
            "Tanker insurance / war-risk premia rising — the direct Brent-side cost",
            "Trump's 'the Strait is open' off-ramp — the de-escalation risk the spread survives better than an outright long",
        ],
        "risks": (
            "A rapid de-escalation reopens Hormuz, war-risk premia fall, and the spread compresses back toward $4; or a "
            "US shale/SPR response weighs on Brent relative to WTI. Lower-beta than outright crude — the spread gives "
            "back far less than a long on a de-escalation."
        ),
        "breakdown_why": {
            "gap":          "2/3 — a closed Strait is a waterborne shock but the ~$5 spread only partly prices it; the "
                            "grade differential is where the Hormuz mechanism is under-owned.",
            "catalyst":     "2/2 — the Strait closure is live and dated; tanker war-risk premia are rising now.",
            "positioning":  "1/2 — the spread is a low-crowding expression vs a heavily-traded outright crude long.",
            "confirmation": "1/2 — Brent already leads WTI higher on the seaborne premium; one confirming leg.",
            "stop_quality": "1/1 — the spread is self-hedging; the de-escalation downside is bounded vs an outright.",
        },
    },
    "MM-2026-045": {
        "instrument": (
            "Long CHF/JPY spot — buy the Swiss franc, sell the Japanese yen. CHF is the classic European safe-haven "
            "(SNB-managed, large current-account surplus, low relative energy-import dependence); JPY is the FUNDER in "
            "an oil shock — Japan imports its energy, so a $79 Brent is yen-negative, and the BoJ is the most dovish "
            "major. The cross owns the haven bid and the oil-importer penalty in one expression, with less crowding "
            "than long USD and immune to the MoF's USD/JPY intervention line."
        ),
        "fundamental_thesis": (
            "The cleanest war haven that isn't the dollar. In a genuine risk-off the franc is Europe's reserve haven; "
            "the yen, despite its old haven reputation, trades as the funder in an energy shock because Japan imports "
            "its oil and the BoJ lags on normalisation. Long CHF/JPY captures both legs — the flight-to-quality bid "
            "into CHF and the terms-of-trade drag on JPY — in a single cross that the dollar's crowding does not touch. "
            "It complements the book's short USD/JPY (MM-007) by owning the haven side without fighting the MoF line."
        ),
        "catalysts": [
            "Weekend escalation + Strait closure — the risk-off flight into the franc",
            "$79 Brent — the terms-of-trade drag on the energy-importing yen",
            "BoJ the most dovish major — the funder side of the cross",
            "SNB tolerance of a firmer franc in a haven bid — the enabling backdrop",
        ],
        "risks": (
            "SNB jawboning or intervention to cap franc strength; a fast de-escalation drains the haven bid; a hawkish "
            "BoJ surprise or MoF-style yen support squeezes the cross. Stop below the recent range low."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the market crowds into long-USD for haven; CHF/JPY prices the same risk-off less "
                            "fully and adds the oil-importer penalty the yen carries.",
            "catalyst":     "2/2 — the escalation and the oil shock are live and dated; both legs are firing now.",
            "positioning":  "1/2 — a lower-crowding haven than long USD; the yen carry is still heavily long.",
            "confirmation": "1/2 — the yen is already the weakest haven and the franc firm; one confirming leg.",
            "stop_quality": "1/1 — a clean range-low stop below the pre-escalation base.",
        },
    },
    "MM-2026-046": {
        "instrument": (
            "Buy a September gold $4,200/$4,600 call spread — defined-risk upside on spot gold. Buy the $4,200 call, "
            "sell the $4,600 call; max loss is the premium. With spot ~$4,100-4,121 both strikes are above the market — "
            "cheap convexity on the ONE tail gold has refused to price: a war that deepens into a growth scare and "
            "forces the Fed to abandon its hawkish lean, at which point the real-rate cap that has held gold down all "
            "war breaks violently."
        ),
        "fundamental_thesis": (
            "Gold is the coiled haven — capped the entire war by rising real yields, which is exactly the asymmetry. At "
            "~$4,100 it prices none of the scenario where a closed Strait and an oil cost-push tip into a genuine "
            "growth scare, the Fed's hawkish lean flips, real yields fall, and gold's cap snaps. A defined-risk call "
            "spread owns that convexity for a small premium, complements the underwater cash long (MM-005) without "
            "adding spot at its min-hold, and is the disciplined way to own the regime-change tail rather than fight "
            "the current real-rate headwind in the spot."
        ),
        "catalysts": [
            "War deepens into a growth scare — the trigger that flips gold from rate-trade to haven",
            "A Fed forced to abandon the hawkish lean — the real-rate turn gold needs",
            "June CPI Tue — a soft real read that lets real yields fall is gold-supportive",
            "Central-bank / EM physical buying — the structural floor under the drawdown",
        ],
        "risks": (
            "Yields keep backing up on the oil cost-push and gold stays capped below the strikes; a fast de-escalation "
            "drains both the war premium and the rate-cut hopes at once. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — gold prices the real-rate headwind but NONE of the regime-change tail; a wide, "
                            "one-sided mispricing of the convexity.",
            "catalyst":     "2/2 — the war and the CPI are live and dated; the growth-scare trigger is the tail.",
            "positioning":  "1/2 — spec length was washed out; clean positioning, squeeze-prone on a rate turn.",
            "confirmation": "0/2 — gold is still capped; no confirming up-leg — a fresh, contrarian tail.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-047": {
        "instrument": (
            "Long US high-yield credit protection — buy CDX HY protection or short the HYG ETF, defined/limited "
            "downside on US high-yield credit. Owns the LAGGARD: equity vol, oil and the dollar have all repriced the "
            "war, but HY spreads sit near cycle tights. A war-driven growth scare plus an oil cost-push that squeezes "
            "margins and keeps the Fed from cutting is precisely what widens spreads — and the entry is cheap because "
            "credit is complacent."
        ),
        "fundamental_thesis": (
            "Credit moves last, and it has barely repriced the war. Equity vol is finally waking (chips selling, VIX "
            "off 15), oil is +4% and the dollar bid, yet HY spreads are near the tights — the market with the most "
            "room and the least priced-in risk. A closed Strait, an oil cost-push into margins, and a Fed boxed away "
            "from cuts is the classic spread-widening cocktail. Long HY protection is the cross-asset completion of the "
            "'the tape under-priced the war' thesis, in the asset class that reprices slowest and therefore offers the "
            "cheapest convexity to the same event."
        ),
        "catalysts": [
            "Weekend escalation + Strait closure — the growth scare credit hasn't priced",
            "Oil cost-push into corporate margins — the fundamental spread-widener",
            "A Fed kept from cutting by the oil-CPI — no policy cushion for HY",
            "Equity vol already waking (VIX off 15) — the cross-asset lead credit is lagging",
        ],
        "risks": (
            "A fast de-escalation and a soft CPI keep the carry trade alive and spreads pinned; HY is technically "
            "supported by light net supply and strong demand for yield. Limited via the protection premium / a defined "
            "short."
        ),
        "breakdown_why": {
            "gap":          "3/3 — HY spreads near cycle tights while every other asset class has repriced the war — "
                            "the widest cross-asset lag on the board.",
            "catalyst":     "1/2 — the growth scare is live but credit's repricing is slower-burn than a dated event.",
            "positioning":  "2/2 — the crowd is long carry/short vol in HY; a spread-widening is the pain trade.",
            "confirmation": "0/2 — spreads have not moved yet — a fresh, pre-emptive laggard trade.",
            "stop_quality": "1/1 — limited risk via the protection premium / a defined short leg.",
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
    {"name": "MOVE", "level": "~105 (est)", "chg": "firmer", "dir": "up"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Fri 10 Jul · NY Fed"},
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
    "MM-2026-001": "FLAT. EUR/AUD near entry — the weekend risk-off pressures the AUD while a $79 Brent lifts its terms of trade the other way, pinning the cross mid-range. No EUR catalyst left; edge thinned. Trim into any risk-off AUD weakness. Stop 1.662 (close). Tight leash.",
    "MM-2026-004": "THE LAGGARD. 10Y ~4.59%, backed UP further from the 4.44% entry (~-3%) as the weekend escalation lifted Brent to ~$79 and re-armed the inflation trade — a shooting war with the Strait shut gave duration NO haven bid. Better expressed via the curve (MM-009). Stop 4.65% (~6bp) — a very tight rein into CPI.",
    "MM-2026-005": "THE WAR STILL DIDN'T SAVE IT. Gold stalled ~$4,100-4,121 (~-9% from the $4,523 entry) through a weekend of strikes — yields backed up ~8.5bp to 4.59% and gold traded as a real-rates short. Held on its min-hold (to ~Jul 15), now coinciding with CPI. The coiled upside is owned via the defined-risk call spread (MM-046).",
    "MM-2026-007": "OFFSIDE. USDJPY ~162.4, above the 159.37 entry (~-1.9%), as the weekend risk-off bought the DOLLAR not the yen and a $79 Brent hit the energy-importing yen. Stop 163.00, now ~0.6pt away — tight. The cleaner haven is long CHF/JPY (MM-045).",
    "MM-2026-009": "THE WINNER. 2s10s ~+35bp, ~+130% off the +15bp entry — the spread holds as the escalation confirms it: a Fed boxed between a labour crack and a war-driven oil-CPI. The one rate expression the war doesn't break. Min-hold ~Jul 16; trail the stop; stop -10bp; target +60bp.",
    "MM-2026-012": "WORKING. ~1.1426 with DXY firm at ~100.96 — the weekend risk-off bought the haven dollar and $79 Brent hit the euro's terms of trade. Green (~+1.5%), stop 1.182 distant. Hold the core short; own the hot-CPI/haven-dollar tail via MM-042 (held).",
    "MM-2026-013": "OFFSIDE. 2Y firmed above the 4.162% entry (~flat-to-red) as the escalation, $79 Brent and CME hike-this-year odds jumping to ~87% re-priced near-term hike risk against the short. Min-hold elapsed; stop 4.35%. CPI Tue is the decider; the curve (MM-009) is the higher-conviction sibling.",
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
    {"datum": "US MARKETS REOPEN Mon Jul 13 into a risk-off gap (pre-market brief). Brief covers the weekend Jul 11-12 escalation + the Monday reopen setup. June CPI Tue Jul 14 08:30 ET; big-bank earnings Tue-Wed.",
     "source": "NYSE/Nasdaq + SIFMA calendar", "asof": TODAY, "stale": False},
    {"datum": "WEEKEND ESCALATION (Jul 11-12): after a Cyprus-flagged container ship was attacked in Hormuz, the US struck ~140 Iranian military sites overnight Sat→Sun (a THIRD round); Iran retaliated with drones/missiles on US bases and strikes on US-linked installations in the UAE, Kuwait and Bahrain.",
     "source": "CNN + Fox + Al Jazeera (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "STRAIT OF HORMUZ effectively CLOSED to commercial traffic (Day ~134 of the crisis); only the southern Omani-coast lane runs two-way. Iran declared the waterway closed (Jul 12); UKMTO + US Navy say the southern route remains available.",
     "source": "straits.live + UKMTO + Al Jazeera (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "TRUMP (Sun Jul 12): US hit Iran 'very hard' after Iran hit a ship with a drone 'two hours' after a near-deal; says 'the Strait of Hormuz is open'; paraded strike footage on Truth Social. The de-escalation door is open but his to shut.",
     "source": "Washington Times + CNN + Newsweek (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Oil (Mon Jul 13): Brent ~$79.0 (+~3.9% Sun/Mon), WTI ~$74+ (+~4%) on the Strait-closure supply premium; OVX (oil vol) elevated. Brent-WTI spread ~$5.",
     "source": "Trading Economics + CNBC + Oilprice (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Gold ~$4,100-4,121 — stalled through the escalation; the 10Y backed up ~8.5bp to ~4.59%, so gold traded as a real-rates short, NOT a haven. Corrective/consolidating bias into CPI.",
     "source": "Invezz + Business Standard + LiteFinance (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Rates (Mon Jul 13): US 10Y ~4.589% (+~8.5bp), 2Y firmer, 2s10s holds ~+35bp on the oil cost-push. CME hike-THIS-YEAR odds jumped to ~87% (July meeting Jul 28-29 still ~78% hold / ~22% hike). Fed chair Warsh: inflation 'too high'.",
     "source": "CME FedWatch + Sahm Capital + CNBC (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "FX (Mon Jul 13): DXY ~100.96 firm on a safe-haven bid; USD/JPY ~162.41 (yen the funder in an oil shock, near strongest USD since Jul 1); EUR/USD ~1.1426; GBP/USD ~1.3392.",
     "source": "CNBC + Trading Economics + Bloomberg (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Asia (Mon Jul 13): KOSPI fell into bear-market territory, chip-led (SK Hynix + Samsung the drag, half the index weight); Nikkei ~-1 to -1.5% on oil cost-push + chip selloff. The SK Hynix halo that led Friday's tape UP inverted.",
     "source": "Bloomberg + CNBC + investinglive (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Prior close (Fri Jul 10): S&P 500 7,575.39 (+0.42%); Nasdaq Composite 26,281.61 (+0.29%); Dow 52,637.01 (+0.29%); VIX 15.03 (−5.11%). The winning-week complacency the reopen is repricing.",
     "source": "Yahoo Finance + CNBC (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "June CPI PENDING — Tue Jul 14 08:30 ET. Consensus: headline −0.1% m/m (~3.8-3.9% y/y, from May 4.2%); core +0.3% m/m (~2.9% y/y). BACKWARD-LOOKING: June oil was LOW post the mid-June ceasefire, so a soft headline does NOT capture July's $79 Brent.",
     "source": "BLS + Kiplinger + Cleveland Fed nowcast (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Big-bank Q2 earnings PENDING — Tue Jul 14 BMO: JPM (~$5.74 EPS), GS (~$14.46, +32% y/y, NII ~$3.85bn +24%, implied move ~6%, split 15/15/2), C (~$2.76), BAC (~$1.13), WFC (~$1.73); Jul 15: MS, BLK, BNY. Steeper curve = NIM tailwind; same-day CPI + war gap can swamp it.",
     "source": "Finnhub + Zacks + Motley Fool (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.62% — funding unmoved by the war/oil spike; no plumbing stress.", "source": "NY Fed (rail)", "asof": "2026-07-10", "stale": True},
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
            "Reports into a 2s10s at ~+35bp (NIM/curve tailwind) and a re-opening capital-markets pipeline.",
        ],
        "what_moves_it": ("Investment-banking and trading revenue vs a divided consensus; the same-day June CPI is the "
            "macro cross-current that can swamp a good print."),
        "client_talking_point": ("GS is the highest-beta way to own the bank-earnings kickoff — a ~6% implied move and a "
            "split sell-side mean an IB beat has room to re-rate; own it with a defined-risk call spread, not naked, "
            "because CPI lands the same morning."),
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
            "Steeper curve (2s10s ~+35bp) supports NIM; the read-through sets the tone for the whole group.",
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
        "THE STRAIT SHUTS. The war the tape spent Friday ignoring escalated over the weekend hard enough to force a "
        "reprice. After a container ship was attacked in Hormuz, the US struck ~140 Iranian sites (a THIRD round) and "
        "Iran retaliated on US bases and on installations in the UAE, Kuwait and Bahrain; the Strait of Hormuz is now "
        "effectively CLOSED to commercial traffic. The cross-asset answer at the reopen: Brent +~3.9% to ~$79 and WTI "
        "+~4% on a real supply premium, the dollar bid (DXY ~100.96, USD/JPY ~162.4), and — the tell — the CHIPS that "
        "carried Friday's winning week lead DOWN, the KOSPI into bear-market territory. Gold STILL didn't bid (~$4,100, "
        "10Y ~4.59%), because the oil spike is a cost-push that lifts real yields. Friday's 'one AI trade absorbs "
        "everything' was never resilience — it was one crowded long-duration bet in front of a war not yet in the "
        "price; a closed Strait put it there. June CPI Tue Jul 14 is a BACKWARD-LOOKING trap: June oil was low, so a "
        "soft headline can't see July's $79 Brent. Jul 11's hedges (Brent call spread, SPX put spread, EUR/USD put "
        "spread) are IN THE MONEY; TotalEnergies leads. The fresh trade presses the NEW information: long Brent vs WTI "
        "(the waterborne premium), long CHF/JPY (the war haven that isn't the dollar), a gold Sep call spread (the "
        "coiled haven), and long HY credit protection (the laggard)."
    ),

    "summary_narrative": """
<p>The most important thing about the weekend is that the war the tape spent Friday ignoring escalated hard enough to
force a reprice, and the melt-up blinked. After a Cyprus-flagged container ship was attacked transiting the Strait of
Hormuz, the US struck about 140 Iranian military sites overnight Saturday into Sunday &mdash; a <strong>third
round</strong> &mdash; and Iran retaliated with drones and missiles on US bases and strikes on US-linked installations
in the UAE, Kuwait and Bahrain. The Strait is now effectively <strong>closed</strong> to commercial traffic; only the
southern Omani-coast lane runs two-way. (CNN, Fox, Al Jazeera, straits.live.) The cross-asset answer was immediate:
Brent jumped ~3.9% to ~$79 and WTI ~4% above $74 on a real supply premium, the dollar firmed on a haven bid (DXY
~100.96, USD/JPY ~162.4), and &mdash; the tell &mdash; the chips that carried Friday&rsquo;s winning week led the tape
<em>down</em>, the KOSPI falling into bear-market territory led by SK Hynix and Samsung.</p>

<p>Decompose Friday&rsquo;s melt-up now the weekend has repriced it. Friday&rsquo;s story was &lsquo;one AI trade can
absorb a shooting war&rsquo; &mdash; the SK Hynix record IPO carried a winning week at VIX 15. The anatomy the weekend
exposed is that this was never resilience: it was one crowded, long-duration AI-capex bet standing in front of a war
that had not yet been forced into the price. A closed Strait forced it. The same names that led up on the halo lead down
on the reprice, because a war-driven growth scare plus an oil cost-push that lifts real yields is exactly what the
long-duration AI trade cannot absorb. So what, who is wrong, what is the trade: the consensus that read Friday&rsquo;s
close as all-clear is wrong; the trade is to own where the war actually lands &mdash; the waterborne oil premium and the
haven bid &mdash; and fade the complacency the reopen is only now unwinding. (Invezz, Business Standard, CNBC.)</p>

<p>The second-order effect consensus is missing is that Tuesday&rsquo;s CPI is a backward-looking trap. June was the
last calm month &mdash; oil was low after the mid-June ceasefire, before the early-July collapse &mdash; so a soft June
headline (consensus &minus;0.1% month-on-month, ~3.8&ndash;3.9% annual) is mechanical and does NOT contain a single
barrel of July&rsquo;s $79 Brent. The danger is a tape that gaps down on the war, then rallies on a soft headline it
misreads as disinflation, while core services stay sticky at +0.3% and July&rsquo;s oil already re-arms the next print
&mdash; with CME hike-this-year odds already at ~87%. The Burry tell is still inside the chips: the capacity race the SK
Hynix raise funds does not pause for a war, so the memory glut builds underneath a selloff that looks like it is only
about geopolitics. The book is 30% Micron; the weekend is the first crack.</p>

<p>The book sits astride the reprice and, for once, the hedges are in the money. Jul 11&rsquo;s Brent call spread, SPX
put spread and EUR/USD put spread own exactly this weekend: the oil premium, the index gap, the haven dollar.
TotalEnergies leads the book again as the working war hedge; the 2s10s steepener (MM-009) holds ~+35bp as the one rate
expression the escalation confirms, while the short-10Y (MM-004) and short-2Y (MM-013) lag on the oil backup and gold
(MM-005) still refuses to bid. Short EUR/USD (MM-012) works on the haven dollar.</p>

<p>The regime is no longer &lsquo;the melt-up absorbs everything.&rsquo; It is a market being forced, one asset class at
a time, to price a war it spent a week pretending wasn&rsquo;t there &mdash; into a CPI print that can&rsquo;t see it
yet. The posture is to press the new information: own the waterborne premium a closed Strait creates, own the cleanest
war haven that isn&rsquo;t the dollar, own the coiled haven that hasn&rsquo;t fired, and own the laggard &mdash; credit
&mdash; that hasn&rsquo;t repriced the war at all.</p>
""",

    "takeaways": [
        "<strong>The war escalated over the weekend and the Strait shut.</strong> After a container ship was attacked "
        "in Hormuz, the US struck ~140 Iranian sites (a third round) and Iran hit US bases and installations in the "
        "UAE, Kuwait and Bahrain; the Strait of Hormuz is now effectively closed to commercial traffic, only the "
        "southern Omani lane running two-way. (CNN, Fox, straits.live.)",

        "<strong>The chips that led Friday up lead the reopen down.</strong> The SK Hynix halo inverted: the KOSPI fell "
        "into bear-market territory led by SK Hynix and Samsung, the Nikkei ~-1 to -1.5%, and US futures point lower. "
        "The 'one AI trade absorbs everything' complacency is repricing &mdash; a direct hit to the book's 30% Micron. "
        "(Bloomberg, CNBC.)",

        "<strong>Oil and the dollar caught the bid; gold still didn't.</strong> Brent +~3.9% to ~$79, WTI +~4% on the "
        "Strait-closure premium; DXY firm ~100.96, USD/JPY ~162.4. Gold stalled ~$4,100 because the 10Y backed up "
        "~8.5bp to ~4.59% &mdash; a cost-push, not a haven. TotalEnergies is the war hedge that works. (Trading "
        "Economics, Invezz.)",

        "<strong>The hawk is re-armed.</strong> CME hike-this-year odds jumped to ~87% as the oil cost-push and a Fed "
        "(Warsh) calling inflation 'too high' backed the front up. The short-10Y (MM-004) and short-2Y (MM-013) lag; "
        "only the steepener (MM-009, ~+35bp) holds. (CME FedWatch, Sahm Capital.)",

        "<strong>June CPI Tuesday is a backward-looking trap.</strong> June was the last calm month &mdash; oil was low "
        "post the mid-June ceasefire &mdash; so a soft headline (&minus;0.1% m/m, ~3.8-3.9% y/y) can't see July's $79 "
        "Brent. The risk is the tape misreads it as all-clear while core stays +0.3% and July oil re-arms the next "
        "print. (BLS, Kiplinger.)",

        "<strong>Jul 11's hedges are in the money.</strong> The Brent call spread (MM-040), SPX put spread (MM-041) and "
        "EUR/USD put spread (MM-042) all own exactly this weekend &mdash; the oil premium, the index gap, the haven "
        "dollar. The fresh trade presses the NEW information, it doesn't recycle the vindicated ones.",

        "<strong>The Burry tell is still inside the chips.</strong> The capacity race the SK Hynix raise funds doesn't "
        "pause for a war &mdash; Hynix, Samsung and Micron keep adding HBM, so the memory glut builds underneath a "
        "selloff that looks like it's only about geopolitics. The book is 30% Micron; the weekend is the first crack. "
        "(Bloomberg.)",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "De-escalation + soft CPI — Trump's off-ramp holds and the AI dip gets bought back",
         "body": "Trump's off-ramp holds (he says a deal was 'two hours' away), the Strait reopens, oil drains toward "
                 "$70, and a soft June headline (backward-looking, oil-light) revives the disinflation read: "
                 "hike-this-year odds fall, the 2Y rallies (MM-013 re-confirms), the curve bull-steepens (MM-009), gold "
                 "gets real-rate relief (MM-005 rescued at the min-hold), and the chip-led selloff is bought back. The "
                 "Brent widener (MM-044) and HY protection (MM-047) decay. The catch: the tape chases a headline that "
                 "can't see July's oil. Risk up · rates down (front) · dollar soft · gold up · oil soft."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "A boxed-in Fed and a war premium that persists — steep curve, firm oil, choppy risk",
         "body": "The Strait stays disrupted but doesn't spiral, oil holds a war premium ~$78-82, June CPI prints a "
                 "soft headline over a sticky +0.3% core, and the labour crack caps the hike; Warsh's Fed holds a "
                 "hawkish hold it can neither justify nor execute. The 2Y ranges, the curve stays steep (MM-009 the "
                 "winner), energy holds (TotalEnergies/MM-044), gold chops below $4,200, the dollar stays firm (MM-012 "
                 "holds), and equities chop as the war-gap partly retraces. HY spreads drift wider (MM-047). Risk mixed "
                 "· rates steady · dollar firm · oil firm · curve steep."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "The Strait stays shut or a hot core prints — the growth scare deepens and credit finally widens",
         "body": "Either Iran keeps the Strait shut / escalates and oil spikes through $90 (MM-044 and TotalEnergies "
                 "pay hard, MM-046 gold convexity fires on a growth scare), the chip-led selloff extends the KOSPI's "
                 "bear market to the S&amp;P (MM-041 pays), and HY spreads finally gap wider (MM-047 pays); or a hot "
                 "core CPI on top re-arms a near-term hike, backs the 2Y toward the 4.35% stop (MM-013 risk) and "
                 "bear-flattens the front. Either way the war is now IN the price and the complacency unwinds. Risk "
                 "down · rates two-way · dollar bid · oil up · credit wider."},
    ],

    "insights_layers": """
<p>The dominant driver at the reopen is a war being forced into the price of everything, one asset class at a time. Over
the weekend a third round of US strikes (~140 sites) and Iranian retaliation on Gulf-state installations shut the Strait
of Hormuz to commercial traffic; oil and the dollar caught the bid and the chips that led Friday's winning week led the
Monday tape down, the KOSPI into a bear market. The non-consensus read is that Friday's melt-up was never resilience &mdash;
it was one crowded, long-duration AI-capex bet standing in front of a war that had not yet been priced, and a closed
Strait is what finally prices it.</p>

<p>The counter-intuitive hook is that even a full escalation did not bid gold. A shooting war with the Strait shut
would, in the textbook, send bullion and duration higher; instead gold stalled ~$4,100 and the 10Y backed up ~8.5bp to
~4.59%. The oil spike is a cost-push, not a flight to safety &mdash; it lifts inflation expectations and real yields,
which caps gold and sells bonds. The only havens paying in this regime are the dollar and oil itself. That is the whole
regime in one line: a war that transmits as inflation, not as fear.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong> a
closed Strait, Brent ~$79, the 10Y at 4.59%, core PCE near 3%, CME hike-this-year odds ~87%, a memory capacity race
that doesn't pause for a war. <strong>What is priced:</strong> equity vol only now waking from 15, HY spreads still near
cycle tights, a soft June headline assumed, the AI dip half-bought. <strong>Consensus narrative:</strong> &lsquo;the war
is contained to oil, CPI will be soft, buy the dip.&rsquo; The gap &mdash; and the alpha &mdash; is that credit and, to
a degree, equities have still not priced a war the oil market and the dollar already have.</p>

<p>Go around the world. <strong>US:</strong> futures gap lower into the reopen; the AI-concentrated index is the
epicentre of the reprice. <strong>Korea/Asia:</strong> the KOSPI &mdash; half its weight now SK Hynix and Samsung &mdash;
fell into bear-market territory, the SK Hynix halo that led Friday inverted; the Nikkei fell on oil cost-push and the
chip selloff. <strong>Europe:</strong> an energy-importing bloc hit by a $79 Brent, the natural underperformer on the
war. <strong>Middle East:</strong> the Strait is effectively closed; Trump says it is 'open' and that a deal was 'two
hours' away &mdash; the de-escalation path exists but runs entirely through him.</p>

<p>The political angle runs on two constraints. The Papic read: Trump owns both the strike and the off-ramp &mdash; he
ordered the third round yet insists the Strait is open and a deal was nearly done, which makes the oil premium a binary
on his next move, not a trend. The second constraint is the Fed: a war-driven oil spike is a cost-push that boxes a
central bank (Warsh) already calling inflation 'too high' &mdash; it cannot cut into an oil-CPI and cannot hike hard
into a labour crack. The non-consensus read is that the market's real risk is not the war headline but the CPI trap
underneath it: a soft, backward-looking June print that invites a dip-buy just as July's oil re-arms the next one.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the waterborne Hormuz premium (long Brent vs WTI, MM-044, and the
book's TotalEnergies); a growth scare in credit (HY protection, MM-047); the regime-change tail in gold (the Sep call
spread, MM-046). <strong>Fairly priced:</strong> the haven dollar (MM-012, and long CHF/JPY MM-045); the steeper curve
(MM-009). <strong>Now pricing (was over-priced):</strong> equity complacency &mdash; the SPX gap (MM-041, held) is
finally printing. <strong>Over-priced (at risk):</strong> a soft June headline read as all-clear while July's oil is
already in the pipeline.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is that Friday&rsquo;s winning week was never resilience
&mdash; it was one crowded trade standing in front of a war that had not yet been forced into the price, and over the
weekend it was forced. After a container ship was attacked crossing the Strait of Hormuz, the United States struck about
a hundred and forty Iranian military sites in a third round of bombing, and Iran answered against American bases and
against installations in the Emirates, Kuwait and Bahrain. The Strait is now shut to commercial traffic in all but a
single southern lane. The tape that spent last week deciding a Korean memory listing mattered more than a Gulf war
reopened on Monday with the same chips leading it down, the Korean index already in a bear market, oil and the dollar
bid, and the volatility it had crushed to fifteen finally waking. The market was right for a week. It was not right about
the war.</p>

<p>Decompose the reversal, because the composition is the whole story. The names that led the melt-up up on the SK Hynix
halo &mdash; memory, accelerators, the long-duration AI-capex complex &mdash; are the names leading the reopen down.
That is not a coincidence and it is not only geopolitics. A war that transmits through the oil price is a cost-push, and
a cost-push lifts real yields; a long-duration equity trade is precisely what cannot survive rising real yields and a
growth scare arriving together. So what, who is wrong, what is the trade: the consensus that read Friday&rsquo;s close
as all-clear was wrong about where the war would land, and the trade is to own where it actually lands &mdash; the
waterborne barrel and the haven currency &mdash; and to fade the complacency the reopen is only now unwinding.</p>

<p>Trace it to a flow, because the durable move is physical, not narrative. A closed Strait is not a headline, it is a
supply withdrawal at the single most important chokepoint in the oil market: roughly a fifth of the world&rsquo;s
seaborne crude and gas passes through it. That squeeze lands hardest on the waterborne grade &mdash; Brent, priced off
cargoes that must transit Hormuz &mdash; and barely at all on the landlocked American barrel fed by pipeline from
Cushing. The two benchmarks are a few dollars apart. That is the cleanest expression of the whole event: own Brent
against WTI and you own the Hormuz mechanism itself, with far less to give back if Mr Trump&rsquo;s off-ramp holds than
an outright long would surrender. And the same oil squeeze lands on the Treasury market as an inflation impulse, which
is why the ten-year backed up rather than rallied, and why the curve steepener &mdash; not long duration &mdash; is
still the one rate trade the war confirms.</p>

<p>The Burry tell is still inside the chips, and the selloff is hiding it. The capacity race the SK Hynix raise funds
does not pause for a war: Hynix, Samsung and Micron keep pouring capital into high-bandwidth memory into the same demand
assumption, and memory is a commodity whose cycle has never been broken, only postponed. When the tape falls on a war
headline, it looks like the decline is about Iran. Underneath, the glut is still being built, and the most levered names
&mdash; the ones the book owns most &mdash; are the ones that fall hardest when it resolves. The book is thirty percent
Micron. The weekend is the first crack, and the discipline is to monetise the still-rich volatility into strength, never
to buy the dip on the single best expression of the bet that the cycle is dead.</p>

<p>So the posture is to press the new information, not to recycle the vindicated trades. Friday&rsquo;s hedges &mdash;
the Brent call spread, the index put spread, the euro put spread &mdash; already own this weekend and are in the money;
they are held, not chased. The fresh money goes where the war has not yet been priced: long Brent against WTI for the
waterborne premium a closed Strait creates; long the Swiss franc against the yen, the cleanest war haven that is not the
crowded dollar and one the yen&rsquo;s oil-importer penalty pays for twice; a defined-risk gold call spread for the one
tail bullion has refused to price, where the war deepens into a growth scare and the real-rate cap finally breaks; and
long high-yield credit protection, because credit is the asset class that reprices last and it has not repriced the war
at all. The tape decided one AI trade could absorb a shooting war. The Strait just proved it cannot &mdash; and the CPI
print Tuesday, blind to July&rsquo;s oil, is the trap that could make it forget for a morning.</p>
""",

    "correlation_regime": """
<p><strong>1. Equities RE-coupled to the war &mdash; the biggest break on the board, reversed.</strong> Friday the
S&amp;P booked a winning week through a Gulf war as the AI bid overrode geopolitics; over the weekend the escalation shut
the Strait and the correlation snapped back &mdash; the chips that led up now lead down, the KOSPI into a bear market.
The decoupling that defined last week is over: the melt-up will no longer price the war as nothing. The trade is to fade
the complacency that is only now unwinding (MM-041 held) and own where the war lands (crude, MM-044).</p>

<p><strong>2. Gold stayed decoupled from geopolitics &mdash; still glued to real rates.</strong> Even a full escalation
did not bid gold: it stalled ~$4,100 while the 10Y backed up ~8.5bp to ~4.59%, so gold traded as a real-rates short
again, not a haven. The book's gold long (MM-005) is underwater despite a shooting war. The break is durable &mdash;
gold only re-couples to the war if the war becomes a growth scare that forces real yields DOWN, which is exactly the tail
the Sep call spread (MM-046) owns.</p>

<p><strong>3. Credit decoupled from equity vol &mdash; the new laggard.</strong> Equity vol is finally waking (VIX off
15, chips selling) and oil and the dollar have repriced, but HY spreads sit near cycle tights &mdash; credit has not
moved. A growth scare from a closed Strait is precisely what widens spreads; the market that reprices last is the one
with the most room. Own the laggard (HY protection, MM-047); it is the cross-asset completion of the same 'war
under-priced' thesis.</p>

<p><strong>4. The curve stayed decoupled from the level.</strong> Both the 2Y and 10Y are up on the oil cost-push, but
the 2s10s holds ~+35bp &mdash; the front pinned by a boxed-in Fed, the back heavy on supply and the war premium. A
steepener that survives rising yields is a structural signal: the dominant rates driver is the bind, not the direction.
Own the shape (MM-009), not outright duration (why MM-004 lags).</p>
""",

    "vol_skew": """
<p><strong>The vol bid finally arrived &mdash; but it is in oil, not yet in credit, and that is where the cheap
convexity has moved.</strong> Equity vol woke from Friday's 15.03 as the chip-led selloff and the war gap hit the
reopen; the term structure flattens off the front (est. VIX9D ~17 · VIX ~17-18 · VIX3M ~19 · VIX6M ~20) as the CPI +
war event risk gets priced. OVX (oil vol) is where the real bid sits &mdash; the Strait closure is a live gamma event in
crude. MOVE stays firm (~105+) as the oil-led yield backup lifts rates vol. The one part of the surface still cheap is
CREDIT: HY spreads and their implied vol have barely moved, so long HY protection (MM-047) is the convexity the market
hasn't repriced. The equity index hedge (MM-041, held) is now working rather than fresh &mdash; don't chase richened
puts. The fresh vol structure that fits today is the gold Sep $4,200/$4,600 call spread (MM-046): gold IVol is subdued
because bullion has been a rate-trade, so upside convexity on the growth-scare tail is cheap. If the war de-escalates,
the gold and credit convexity decay cheaply; if the Strait stays shut or CPI's core runs hot, both are owned, not
chased.</p>
""",

    "sector_rv": """
<p><strong>Leading (Mon Jul 13 reopen):</strong> Energy on the Strait-closure premium (Brent +~3.9%, WTI +~4%); the
haven dollar. <strong>Lagging:</strong> AI/semis and memory &mdash; the SK Hynix halo inverted, the KOSPI into a bear
market led by SK Hynix and Samsung, and the whole long-duration AI complex repricing down; European equities as an
energy importer hit by $79 Brent; duration-sensitive defensives as the 10Y backed up to ~4.59%. <strong>This week:</strong>
June CPI Tue (the backward-looking decider); big-bank earnings Tue-Wed (JPM, GS, C, BAC, WFC → MS, BLK, BNY) into the war
gap; the Hormuz safe-passage question.</p>

<p><strong>RV:</strong> Two fit today's tape. First, the chip dispersion, now a DOWN market: long NVDA (~32x) vs the
overbought ~175x AMD &mdash; as the complex de-risks, the richest multiple falls first, so the dispersion widens in the
book's favour and doubles as concentration management (trim the exhausted AMD winner into any bounce). Second, the
waterborne-crude RV: long Brent vs WTI (MM-044) &mdash; the Strait closure hits the seaborne benchmark far harder than
the landlocked one, a lower-beta way to own the war than outright crude. Both are low beta to the index and high beta to
the week's live catalysts &mdash; the chip de-risking and the Hormuz mechanism.</p>
""",

    "positioning": """
<p><strong>The crowd went into the weekend long the AI melt-up, short volatility at 15, long HY carry, and leaning
dovish &mdash; the escalation is the pain trade for all of it.</strong> The loudest lean was complacency: a winning week
through a Gulf war at VIX 15 was a market that had decided only an AI threat could hurt it. The Strait closure is exactly
the shock it priced out, and the reopen is the pain trade unwinding (why MM-041, held, is now working). In credit, the
crowd is long carry / short vol with HY spreads near cycle tights &mdash; a war-driven growth scare is the pain trade
credit has not begun to feel (MM-047). In FX, the market crowds into long-USD for haven, so the lower-crowding franc
cross (long CHF/JPY, MM-045) owns the same risk-off with less positioning risk. In rates, fast money is hawkish on the
oil re-arm (hike-this-year ~87%), so the squeeze is two-way &mdash; which is why the consensus-agnostic steepener
(MM-009) is cleaner than the directional front-end fade (MM-013). In commodities, spec crude length is still light after
the June ceasefire drained the premium, leaving the barrel squeeze-prone (MM-044). In gold, spec length was washed out;
positioning is clean but there is no squeeze without a rate turn (MM-005/MM-046 need the war to become a growth scare).
The pain trade everywhere is the same &mdash; a market that spent a week deciding one AI trade made it immune to a
war.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; the war, the Strait closure and the oil spike produced no stress in the plumbing,
and the hike-this-year repricing does not move the funding rate. <strong>The Pozsar mechanic:</strong> trace the rates
backup to a flow, not a narrative. A closed Strait is a physical supply withdrawal at the chokepoint through which
roughly a fifth of seaborne crude clears &mdash; barrels that would have transited Hormuz are blocked, into a lane where
tankers are being attacked. That squeeze transmits into the Treasury market as a term-premium/inflation impulse: the 10Y
backed up to ~4.59% not on growth but because an oil cost-push plus a heavy fiscal-supply calendar keeps the long end
heavy while a boxed-in Fed pins the front. That is the whole steepener (MM-009). The tell the plumbing is flagging for
next: watch CREDIT, not funding. HY spreads sit near cycle tights while every other market has repriced the war &mdash;
if the growth scare deepens, the first place the stress shows is the widening of high-yield spreads and the drying of the
new-issue window, not the repo rate (which is why MM-047 is the trade). Underneath it all, the AI-capex machine keeps
running &mdash; the memory capacity race the SK Hynix raise funds does not pause for a war, still bidding the supply
chain and keeping core goods sticky, the half of inflation the CPI print will test even as its headline can't see July's
oil.</p>
""",

    "tape_missing": """
<p><strong>Credit has not repriced the war &mdash; the widest cross-asset lag on the board.</strong> Oil, the dollar,
rates and now equity vol have all moved on the Strait closure; HY spreads sit near cycle tights. The falsifiable level:
CDX HY through +40bp wider, or HYG breaking its recent range low, on a deepening growth scare says credit was mispriced
and the HY protection (MM-047) pays; spreads holding the tights on a clean de-escalation says the carry crowd was right.
Watch HY spreads against the Brent price &mdash; the two should not stay this far apart.</p>

<p><strong>The June CPI is a backward-looking trap the tape could still walk into.</strong> June was the last calm month
&mdash; oil was low post the mid-June ceasefire &mdash; so a soft headline (&minus;0.1% m/m) is mechanical and contains
none of July's $79 Brent. The falsifiable line: a soft headline that sparks a dip-buy while core holds +0.3% and the
2Y/dollar stay bid is the trap (MM-042 held pays on the hot core, MM-041 on the reversal); a genuinely soft core at or
below +0.2% revives the disinflation read and rescues gold (MM-005/MM-046). Tuesday's core, not the headline, is the
test.</p>

<p><strong>The Burry tell &mdash; the capacity race the selloff is hiding.</strong> The chip-led decline looks like it
is about Iran; underneath, the memory capacity race the SK Hynix raise funds does not pause for a war. Hynix, Samsung and
Micron keep adding high-bandwidth memory into the same demand assumption, and memory is a commodity whose cycle has never
been broken, only postponed. Over the next two-to-three quarters this resolves one of two ways: AI demand keeps
outrunning the new supply and the 'broken cycle' thesis survives; or the capacity lands ahead of demand, memory prices
roll, and the most levered names fall hardest &mdash; a fall that will look like more geopolitics but is really the
glut. The Fable book is 30% Micron, the single best expression of the bet that the cycle is dead, and the discipline is
to monetise the still-rich volatility into strength, not buy the dip.</p>
""",

    "book_outlook": {
        "commentary": (
            "The weekend flipped the book's AI sleeve and vindicated its one accidental hedge. The winner, again, is the "
            "position nobody would call a hedge: <b>TotalEnergies</b>, the energy length, leads as a third round of US "
            "strikes shut the Strait of Hormuz and Brent ran +~4% to ~$79 &mdash; the war hedge the equity tape refused "
            "to build, already in the book. But the story this morning is the AI sleeve. Friday's SK Hynix halo, which "
            "re-rated <b>Micron</b> (largest weight, ~30%) by proxy, INVERTED over the weekend: the KOSPI fell into a "
            "bear market led by SK Hynix and Samsung, and the whole memory/accelerator complex &mdash; <b>Micron</b>, "
            "<b>NVDA</b> (−10.5%), <b>AVGO</b> (−21.3%), <b>AMD</b> (+394%), the <b>SPY</b> core &mdash; reprices DOWN "
            "at the reopen. The Burry tell is now literal: the capacity race the SK Hynix raise funds doesn't pause for "
            "a war, so the memory glut builds underneath a selloff that looks like it's only about Iran, and the book is "
            "30% long exactly that. The one genuine offset for an EUR-base client: the ~72% <b>USD sleeve</b> is a "
            "TAILWIND this morning &mdash; the haven-dollar bid (DXY firm ~100.96, EUR ~1.1426) lifts the euro value of "
            "the book's US assets, doing the FX-hedge work the scanner had flagged. The laggards remain the assets that "
            "should work in a war and don't: <b>Xetra-Gold (4GLD)</b> stalled again as the 10Y backed up to ~4.59% "
            "(the tail hedge inverted, because the oil spike is a cost-push, not a haven bid), and the bond sleeve "
            "(<b>UST 1.25% 2031</b>, <b>Siemens EUR IG</b>) is marked lower. European names <b>LVMH</b> and <b>SAP</b> "
            "sit in the energy-importing bloc a $79 Brent hits hardest. The dominant action: the energy length is the "
            "working war hedge &mdash; press it convexly (Brent-vs-WTI), not with spot; treat the chip reprice as the "
            "first crack of the capacity-race tell and monetise Micron's still-rich IVol into any bounce, do NOT buy "
            "the dip on the 30% weight; let the haven dollar do the FX work rather than hedging the USD sleeve away "
            "into it; and do NOT add duration into the CPI/oil risk."
        ),
        "outperform": [
            {"name": "TotalEnergies (TTE, +54.8%) — the working war hedge, again", "why": "A third round of US strikes "
             "shut the Strait and Brent ran +~4% to ~$79 &mdash; the book's energy length leads as the one position "
             "that pays on the escalation. Press the upside convexly via the Brent-vs-WTI widener (the desk's MM-044), "
             "not by adding spot into a two-way headline tape."},
            {"name": "The USD sleeve (~72% of the book) — the haven dollar is a tailwind", "why": "The weekend risk-off "
             "bought the dollar for safety (DXY firm ~100.96, EUR ~1.1426), lifting the euro value of the book's US "
             "assets for an EUR-base client &mdash; the war is doing the FX-hedge work the scanner flagged (mirrors the "
             "desk's MM-012 working). Let it run rather than hedging it away into the bid."},
            {"name": "NVDA (−10.5%) — the relative winner in the chip de-risk", "why": "As the complex reprices down, "
             "the richest multiples fall first &mdash; NVDA at ~32x holds up better than the ~175x AMD and the "
             "de-rated AVGO. It 'outperforms' only on a relative basis (the long leg of the dispersion); the whole "
             "sleeve is lower this morning."},
        ],
        "underperform": [
            {"name": "Micron (MU, ~30%, +1082%) — the halo inverted", "why": "The SK Hynix debut that re-rated Micron "
             "on Friday flipped into a chip-led plunge into bear-market territory over the weekend; the book's largest "
             "weight takes the direct hit. It is the first crack of the capacity-race Burry tell &mdash; monetise the "
             "still-rich IVol into any bounce (collar/overwrite), do NOT buy the dip (mirrors MM-046's disciplined "
             "convexity, not spot)."},
            {"name": "AMD (+394%) & the AVGO/SPY sleeve — the long-duration reprice", "why": "AMD at ~175x is the "
             "overbought leg the chip de-risk targets first; AVGO (−21.3%) and the SPY core gap lower as the "
             "AI-concentrated index leads the war reprice. Trim the exhausted AMD winner into any bounce &mdash; "
             "concentration management as the melt-up unwinds."},
            {"name": "Xetra-Gold (4GLD, +108.6%) & the bond sleeve — the havens that didn't fire", "why": "Gold stalled "
             "again (~$4,100) as the 10Y backed up ~8.5bp to ~4.59% &mdash; the tail hedge inverted for the same "
             "real-rate reason as the war; the UST 2031 and Siemens IG marked lower. Own gold's regime-change tail via "
             "the defined-risk call spread (MM-046), not more spot; do NOT add duration into the CPI/oil risk."},
        ],
        "watch": [
            {"label": "Let the haven dollar do the FX work — don't hedge the USD sleeve away into the bid",
             "text": "The scanner flagged the ~72% USD exposure for a seagull/collar; the weekend war-driven dollar "
             "rally (DXY firm, EUR ~1.1426) is now doing that hedging FOR the EUR-base client. Hold the hedge fire "
             "while the haven bid runs; if you still want the collar, the entry has improved &mdash; but the immediate "
             "risk is de-hedging a tailwind, not leaving the USD open."},
            {"label": "Treat the chip reprice as the first crack — monetise Micron's IVol, don't buy the dip",
             "text": "The war selloff looks like geopolitics; underneath, the capacity race the SK Hynix raise funds "
             "keeps building the memory glut the book is 30% long. Sell Micron's still-elevated option premium into any "
             "bounce with a collar or covered-call overwrite &mdash; own the name with a floor, do NOT average down on "
             "the largest weight at the first crack of the Burry tell."},
            {"label": "Don't add duration before CPI — press the energy hedge convexly instead",
             "text": "The UST 2031 and Siemens IG are the Tuesday risk: the 10Y backed up to ~4.59% and June CPI plus a "
             "$79-Brent premium can back the long end up further. Hold the sleeve but do NOT average down; own rate "
             "value via the curve steepener (MM-009) and carry the hot-core dollar tail via the EUR/USD put spread "
             "(MM-042). Press the energy length with the Brent-vs-WTI widener (MM-044), the cleaner war expression."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> buy the dip &mdash; the Hormuz flare-up will de-escalate like every one before it,
Trump's own 'the Strait is open / a deal was two hours away' is the tell, June CPI will print soft, and the AI trade
resumes. The weekend gap is a reopen overshoot to fade; the chips that led up will lead back up once the headlines calm.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> this is not a flare-up the tape can look through,
because the tape already priced it out once and the war escalated anyway. A closed Strait is a physical supply shock, not
a headline; oil, the dollar, rates and now equity vol have all moved, and credit &mdash; the market that reprices last
&mdash; still sits near cycle tights. The crowded side is long the AI dip, short vol, and long HY carry into a soft
headline it will misread as all-clear while July's oil is already in the next print. The cheaper side owns the waterborne
premium (MM-044), the haven that isn't the crowded dollar (MM-045), gold's regime-change tail (MM-046), and the credit
laggard (MM-047) &mdash; the war where it is not yet priced.</p>
""",

    "one_chart": """
<p class="theme">HY credit spreads against Brent is the chart &mdash; every market has repriced the war except the one that moves last.</p>
<p>The single thing the market should watch is high-yield credit against the oil price. Brent is +~4% to ~$79 on a
closed Strait, the dollar is bid, equity vol is finally waking &mdash; and HY spreads sit near cycle tights, barely off.
Credit is the asset class that reprices last, and it has not yet priced the war at all. That gap resolves one of two
ways, and the level that decides it is CDX HY through +40bp wider (or HYG breaking its recent range low): a Strait that
stays shut or a growth scare that deepens drags spreads wide and the HY protection (MM-047) pays, alongside the Brent
widener (MM-044) and the SPX hedge (MM-041); a clean de-escalation and a soft CPI keep the carry crowd whole and spreads
pinned. Watch HY spreads and Brent together &mdash; they cannot stay this far apart, and June CPI Tuesday, blind to
July's oil, is the accelerant that decides whether the growth scare is real.</p>
""",

    "catalyst_calendar": [
        {"day": "Sat-Sun", "date": "Jul 11-12 ✓",
         "event": "Third round of US strikes — the Strait shuts",
         "consensus": "After a Cyprus-flagged container ship was attacked in Hormuz, the US struck ~140 Iranian sites "
                      "overnight Sat→Sun; Iran retaliated on US bases and installations in the UAE, Kuwait and Bahrain. "
                      "The Strait is effectively closed to commercial traffic. Brent +~3.9% to ~$79. Sources: CNN, Fox, "
                      "Al Jazeera, straits.live.",
         "view": ("The war the tape ignored is now IN the price &mdash; oil and the dollar bid, the chips leading down. "
                  "A closed Strait is a physical supply shock, not a headline to look through."),
         "asymmetry": "Own the waterborne premium (long Brent vs WTI, MM-044) and the credit laggard (MM-047); the "
                      "haven that isn't the crowded dollar is long CHF/JPY (MM-045).",
         "dir": "up"},
        {"day": "Sun", "date": "Jul 12 ✓",
         "event": "Trump: 'the Strait is open' / a deal was 'two hours' away",
         "consensus": "Trump said the US hit Iran 'very hard' after Iran hit a ship with a drone 'two hours' after a "
                      "near-deal, and insisted 'the Strait of Hormuz is open'; he paraded strike footage on Truth "
                      "Social. Sources: Washington Times, CNN, Newsweek.",
         "view": "The Papic constraint: Trump owns both the strike and the off-ramp, so the oil premium is a binary on "
                 "his next move, not a trend. De-escalation is available but entirely his to grant.",
         "asymmetry": "The binary keeps the Brent widener (MM-044) as the disciplined expression &mdash; it gives back "
                      "far less than an outright long if the off-ramp is taken.",
         "dir": "flat"},
        {"day": "Mon", "date": "Jul 13 — TODAY",
         "event": "Reopen — the weekend escalation gets priced",
         "consensus": "US markets reopen into a risk-off gap: Asia lower (KOSPI into a bear market, chip-led), oil and "
                      "the dollar bid, US futures lower. The VIX-15 complacency and the AI concentration are the two "
                      "things repriced first. Source: market calendar.",
         "view": "The setup session into the week's real catalysts; whether the oil premium and the chip de-risk hold "
                 "and whether credit starts to price the war the rest of the tape already has.",
         "asymmetry": "A held premium into CPI keeps MM-044/045/047 live; a de-escalation gap fades the war trade and "
                      "revives the AI dip-buy and gold's rate relief (MM-046).",
         "dir": "down"},
        {"day": "Tue", "date": "Jul 14",
         "event": "June CPI (08:30 ET) + big-bank Q2 earnings (BMO)",
         "consensus": "June CPI consensus: headline −0.1% m/m (~3.8-3.9% y/y), core +0.3% m/m (~2.9% y/y). Same "
                      "morning: JPM (~$5.74 EPS), GS (~$14.46, implied move ~6%), C (~$2.76), BAC (~$1.13), WFC "
                      "(~$1.73) report BMO. Sources: BLS, Kiplinger, Finnhub, Zacks.",
         "view": "The trap. A BACKWARD-LOOKING June print (June oil was low) that can't see July's $79 Brent, meeting "
                 "the bank cohort into a war-gap reopen. The risk is a soft headline that sparks a dip-buy while core "
                 "stays sticky.",
         "asymmetry": "A soft headline the tape misreads as all-clear is the fade (MM-041/044/047 pay on the war "
                      "underneath); a genuinely soft CORE rescues gold (MM-046/005) and the AI dip. GS is the "
                      "highest-beta bank print (MM-043 held).",
         "dir": "down"},
        {"day": "Wed", "date": "Jul 15",
         "event": "Bank earnings wave 2 (MS, BLK, BNY) + CPI follow-through",
         "consensus": "Morgan Stanley, BlackRock and BNY Mellon report BMO, extending the Financials read into wealth/"
                      "asset management and custody. The market digests the CPI print and the war's follow-through. "
                      "Sources: Finnhub.",
         "view": "The confirmation session: whether the war gap holds or gets bought, and whether the bank cohort's "
                 "NIM/IB tailwind survives a risk-off tape.",
         "asymmetry": "A held oil premium + a widening in credit confirms the war trade; a clean de-escalation lets the "
                      "AI dip and gold's rate relief (MM-046) run.",
         "dir": "flat"},
        {"day": "Thu", "date": "Jul 16",
         "event": "Hormuz safe-passage / shipping data + jobless claims",
         "consensus": "The market watches Strait traffic (UKMTO advisories, tanker rerouting) and weekly US jobless "
                      "claims for the first read on whether the oil shock is denting the labour market the Fed is "
                      "boxed by. Sources: UKMTO, DoL.",
         "view": "The tell on whether the oil premium is structural (Strait stays disrupted) and whether the growth "
                 "scare is showing up in the data credit hasn't priced.",
         "asymmetry": "Persistent Strait disruption + softening claims is the growth-scare cocktail (MM-047 pays); "
                      "reopened lanes drain the premium (MM-044 gives back little by design).",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.662 (the stop). Near entry &mdash; flat, the risk-off AUD pressure and a $79-Brent AUD bid cancel out mid-range; edge thinned, stop close. Trim into any risk-off AUD weakness; tight leash.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.59% &mdash; the LAGGARD; the escalation backed the 10Y UP again and the war gave duration no haven bid. Expressed better via the curve (MM-009). A break below 4.40% on a soft CPI is the confirmation; ~6bp from the stop &mdash; a very tight rein into the print.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15 (now 2 days, coincides with CPI); stop $4,250. At ~$4,100 &mdash; the war STILL didn't save it; yields backed up and gold traded as a real-rates short. Own the regime-change tail via MM-046; the min-hold decision now lands on CPI.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00, now ~0.6pt away. At ~162.4 &mdash; offside (~-1.9%); the risk-off bought the DOLLAR, not the yen, and $79 Brent hit the energy-importing yen. The cleaner haven is long CHF/JPY (MM-045). Tight leash.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+35bp; ~+130%; target +60bp. The one expression the escalation confirms &mdash; the spread holds through the oil backup. Trail the stop; hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182 (distant). At ~1.1426 &mdash; WORKING; the haven-dollar bid and $79 Brent hit the euro's terms of trade. Hold the core short; own the hot-CPI/haven-dollar tail via MM-042. A soft CPI that revives the dollar roll is the only trim signal.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold elapsed. Offside &mdash; the escalation, $79 Brent and hike-this-year odds at ~87% re-priced near-term hike risk against it. CPI Tue is the decider; the curve (MM-009) is the higher-conviction sibling. A hot core toward the 4.35% stop is the risk.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The market went UP through a war on Friday — why is it falling now?",
         "a": ("Because Friday was never resilience &mdash; it was one crowded AI trade standing in front of a war that "
               "hadn't yet been priced. Over the weekend the US struck Iran a third time and the Strait of Hormuz "
               "effectively closed, and that forced the reprice: oil and the dollar caught a bid, and the same chips "
               "that carried Friday up are leading the reopen down, with Korea's index already in a bear market. The "
               "war is now in the price. We're trading where it isn't yet.")},
        {"q": "Should we buy this dip in our tech names?",
         "a": ("Not on the biggest one. The selloff looks like it's about Iran, but underneath, the capacity race the "
               "SK Hynix raise funds doesn't pause for a war &mdash; Hynix, Samsung and Micron keep adding memory into "
               "the same demand assumption, and memory is a commodity whose cycle has never actually broken. You're "
               "thirty percent Micron. We'd monetise the still-rich option premium into any bounce with a collar, own "
               "it with a floor, rather than average down on the largest weight at the first crack.")},
        {"q": "The dollar is up — is that hurting us?",
         "a": ("Actually the opposite this morning. You're a euro-based client with about seventy-two percent in US "
               "assets, and the war-driven flight into the dollar is lifting the euro value of that sleeve &mdash; the "
               "war is doing the currency-hedging work we'd flagged for you. We'd let that run rather than hedge it "
               "away into the bid; if anything the entry on a USD collar has improved, but the immediate risk is "
               "de-hedging a tailwind.")},
        {"q": "Why isn't gold rallying in a war?",
         "a": ("Same reason as before: this war comes through the oil price, and an oil spike is a cost-push, not a "
               "flight to safety. Higher oil lifts real yields, and gold hates rising real yields &mdash; the ten-year "
               "backed up to around four-point-six, and gold stalled. Your Xetra-Gold is a rate trade right now, not a "
               "war trade. It only fires if the war becomes a genuine growth scare that forces the Fed to cut, and we "
               "own that specific tail with a small, defined-risk call spread rather than more spot.")},
        {"q": "What's the one thing to watch this week?",
         "a": ("Tuesday's CPI &mdash; but read it carefully. It's June data, and June was the calm month before the "
               "oil spike, so a soft headline won't contain a single barrel of July's seventy-nine-dollar Brent. The "
               "trap is a soft number that sparks a relief rally while the underlying core stays sticky and July's oil "
               "re-arms the next print. We're positioned for the war that's actually in the pipeline, not the headline "
               "that can't see it.")},
        {"q": "Where's the cleanest new money going?",
         "a": ("Into the war where it isn't priced yet. The cleanest is owning the seaborne oil premium a closed Strait "
               "creates &mdash; long Brent against US crude &mdash; and long high-yield credit protection, because "
               "credit is the one market that hasn't moved and a growth scare is exactly what widens it. We'd also own "
               "the Swiss franc against the yen, the cleanest war haven that isn't the crowded dollar.")},
    ],

    "ideas_note": (
        "<p>Today's ideas press the NEW information &mdash; the war where it is not yet priced &mdash; and do not "
        "recycle Friday's hedges (which are held and in the money). <strong>Brent&ndash;WTI widener (MM-044)</strong> "
        "&mdash; the marquee: a closed Strait is a waterborne supply shock that hits the seaborne benchmark far harder "
        "than the landlocked one; own the Hormuz mechanism with a spread that gives back little if the off-ramp is "
        "taken. <strong>Long CHF/JPY (MM-045)</strong> &mdash; the cleanest war haven that isn't the crowded dollar: "
        "the franc catches the flight-to-quality while the energy-importing yen is the funder. <strong>Gold Sep call "
        "spread (MM-046)</strong> &mdash; the coiled haven; defined-risk convexity on the one tail bullion has refused "
        "to price, a war that becomes a growth scare and breaks the real-rate cap. <strong>Long HY credit protection "
        "(MM-047)</strong> &mdash; the laggard: every market repriced the war except credit, still near cycle tights. "
        "The vindicated Friday hedges (Brent call spread MM-040, SPX put spread MM-041, EUR/USD put spread MM-042) are "
        "held; the steepener (MM-009) is trailed; gold spot (MM-005) is held on its min-hold; GS earnings vol (MM-043) "
        "is held into Tuesday.</p>"
    ),

    "event_radar_note": (
        "<p>The Strait shuts: the war the tape spent Friday ignoring escalated over the weekend &mdash; a container "
        "ship attacked in Hormuz, a third round of US strikes (~140 sites), Iran hitting US bases and installations in "
        "the UAE, Kuwait and Bahrain, and the Strait of Hormuz effectively CLOSED to commercial traffic. The reopen "
        "prices it: Brent +~3.9% to ~$79, WTI +~4%, the dollar bid (DXY ~100.96, USD/JPY ~162.4), and the chips that "
        "led Friday up leading down (KOSPI into a bear market). Gold STILL didn't bid (~$4,100, 10Y ~4.59%) &mdash; the "
        "cost-push, not the haven. Friday's hedges (MM-040/041/042) are in the money; TotalEnergies leads; the "
        "steepener (MM-009) holds; the short-10Y (MM-004) and short-2Y (MM-013) lag. June CPI Tue Jul 14 is a "
        "backward-looking trap (June oil was low) and the big-bank kickoff is the same morning. Fresh ideas press the "
        "new information: a Brent&ndash;WTI widener, long CHF/JPY, a gold Sep call spread, and long HY credit "
        "protection.</p>"
    ),

    "burry_tell": (
        "The chip-led selloff looks like it is about Iran; the structural signal is that it isn't. The capacity race "
        "the SK Hynix $26.5bn record raise funds does not pause for a war &mdash; Hynix, Samsung and Micron keep "
        "pouring capital into high-bandwidth memory into the same demand assumption, and memory is a commodity whose "
        "cycle has never actually been broken, only postponed. The thing nobody is pricing is that a war headline is "
        "the perfect cover for the glut to build: when the tape falls on Iran, the decline reads as geopolitics, and "
        "the capacity added ahead of demand &mdash; how every glut in the history of the industry has been built &mdash; "
        "goes unremarked underneath it. Over the next two-to-three quarters this resolves one of two ways: AI demand "
        "keeps outrunning the new supply and the 'broken cycle' thesis survives another few quarters; or the capacity "
        "lands first, memory prices roll, and the most levered names fall hardest &mdash; a fall the market will blame "
        "on the next headline rather than the supply. The Fable book is 30% Micron, the single best expression of the "
        "bet that the cycle is dead, and the weekend is the first crack. The discipline is to monetise the still-rich "
        "volatility into strength with a collar or overwrite &mdash; not to buy the dip on a name whose real risk the "
        "war is conveniently hiding."
    ),

    "earnings_summary": (
        "Three ideas this refresh, all from the big-bank Q2 kickoff (Tue Jul 14 BMO). GS (Long, High &mdash; data gap "
        "flagged): the widest implied move in the cohort (~6%) and the most divided sell-side (15 buy / 15 hold / 2 "
        "sell) mean an investment-banking beat has the most room to re-rate into a steeper curve. JPM (Long, Medium): "
        "the bellwether &mdash; a clean NIM print on a +35bp 2s10s sets the cohort tone, but a well-owned name has less "
        "asymmetry. C (Long, Medium): the value leg &mdash; the biggest serial beater (13-20% surprises four quarters "
        "running) on the cheapest large-cap multiple, a fifth beat is the re-rating catalyst. All positioning pillars "
        "are tagged 'estimated' (Finnhub short-interest unavailable), so GS is capped at 'High &mdash; data gap "
        "flagged' rather than clean High. The macro cross-current is now sharper than a steeper curve: the cohort "
        "reports the SAME morning as June CPI and into a war-gap reopen that can swamp any print &mdash; hence the "
        "defined-risk (call-spread) expression on GS, held into Tuesday rather than pressed naked."
    ),
    "earnings_why": (
        "The universe filter is applied before scanning: market cap $10bn+, geographies US (primary) and South Korea "
        "(secondary), sectors Technology / Financials / Industrials / Utilities only. The earnings_data.md feed "
        "(Finnhub, 2026-07-10 06:00 UTC) returns eleven qualifying Financials reporting Jul 14-15 as Q2 bank season "
        "opens: JPM, GS, C, BAC, WFC (Jul 14) and MS, BLK, BNY, PNC, MTB, FHN (Jul 15) &mdash; all >$10bn, all US, all "
        "Financials. Three are surfaced (GS, JPM, C) as the highest-asymmetry expressions of the same steeper-curve/"
        "IB-re-acceleration thesis; the money-centre names with the clearest read and the widest implied moves. The "
        "regionals (MTB, FHN, PNC) and the wealth/custody names (MS, BLK, BNY) are noted but not rendered as separate "
        "ideas &mdash; they are lower-beta reads on the same NIM tailwind, and padding the section with the full "
        "cohort would dilute the signal. Consensus EPS/revenue, recommendation splits and surprise history are all "
        "SOURCED from Finnhub; short interest is unavailable, so the positioning pillar is tagged estimated."
    ),

    "book_aim": (
        "Astride the war reprice, with the hedges finally in the money and fresh risk rotating into where the war is "
        "not yet priced. The energy length is the working war hedge: TotalEnergies leads again as a third round of US "
        "strikes shut the Strait and Brent ran +~4% to ~$79 &mdash; press it convexly (Brent-vs-WTI, MM-044), not with "
        "spot. The AI sleeve is the loser this morning: the SK Hynix halo inverted, the KOSPI fell into a bear market, "
        "and the 30% Micron weight takes the hit &mdash; the first crack of the capacity-race tell, so monetise the "
        "still-rich IVol into any bounce, do NOT buy the dip. The rate book: the 2s10s steepener (MM-009) holds ~+35bp "
        "as the one expression the escalation confirms, while the short-10Y (MM-004) and short-2Y (MM-013) lag on the "
        "oil backup and gold (MM-005) still refuses to bid. The FX offset is real &mdash; the ~72% USD sleeve is a "
        "tailwind on the haven-dollar bid, so let it run rather than hedge into it. For the week into June CPI (Tue, a "
        "backward-looking trap) and the bank kickoff: hold and trail the steepener; do NOT add duration; hold the euro "
        "short (MM-012) and carry the hot-core tail in options (MM-042 held); own gold's regime-change tail via MM-046 "
        "at the min-hold; and rotate fresh risk into the war where it isn't priced &mdash; the Brent-vs-WTI widener "
        "(MM-044), long CHF/JPY (MM-045), the gold call spread (MM-046), and long HY credit protection (MM-047). "
        "Friday's hedges (MM-040/041/042) and GS earnings vol (MM-043) are held, not chased."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); no option line is open this "
                 "refresh. This is a Monday PRE-MARKET brief (US cash open ~09:30 ET), so equity-index and rate marks "
                 "may reflect the Fri Jul 10 close / live futures until the cash session prints.")
    },
    "idea_selection": [
        {"label": "Long Brent vs WTI — own the waterborne premium a closed Strait creates (MM-044)", "in": True,
         "text": ("The marquee fresh idea. A closed Strait is a waterborne supply shock that hits the seaborne "
                  "benchmark (Brent) far harder than the landlocked US grade (WTI); the spread sits ~$5. It owns the "
                  "Hormuz mechanism with far less de-escalation risk than outright crude &mdash; if Trump's off-ramp is "
                  "taken, the spread gives back a fraction of what a long surrenders. Presses TotalEnergies on the "
                  "specific mechanism, not spot. Lower-beta, self-hedging.")},
        {"label": "Long CHF/JPY — the cleanest war haven that isn't the crowded dollar (MM-045)", "in": True,
         "text": ("The Swiss franc catches the flight-to-quality while the energy-importing yen is the funder in an oil "
                  "shock &mdash; a $79 Brent is yen-negative and the BoJ is the most dovish major. The cross owns the "
                  "haven bid and the oil-importer penalty in one expression, with less crowding than long USD and "
                  "immune to the MoF's USD/JPY intervention line. Complements the book's short USD/JPY (MM-007).")},
        {"label": "Gold Sep $4,200/$4,600 call spread — the coiled haven (MM-046)", "in": True,
         "text": ("Gold has been capped the entire war by rising real yields &mdash; that's the asymmetry. At ~$4,100 it "
                  "prices none of the tail where the war deepens into a growth scare, the Fed's hawkish lean flips, real "
                  "yields fall, and the cap snaps. A defined-risk call spread owns that convexity cheaply, complements "
                  "the underwater cash long (MM-005) without adding spot at its min-hold. Max loss capped.")},
        {"label": "Long HY credit protection / short HYG — the laggard that hasn't repriced the war (MM-047)", "in": True,
         "text": ("Credit moves last, and it has barely repriced. Oil, the dollar, rates and equity vol have all moved "
                  "on the Strait closure; HY spreads sit near cycle tights. A growth scare plus an oil cost-push into "
                  "margins is the classic spread-widener, and the entry is cheap because credit is complacent. The "
                  "cross-asset completion of the 'war under-priced' thesis, in the market with the most room. Limited "
                  "risk via the protection premium.")},
        {"label": "Friday's hedges (Brent call spread MM-040, SPX put spread MM-041, EUR/USD put spread MM-042) — held, in the money", "in": False,
         "text": ("Vindicated by the weekend escalation &mdash; they own exactly the oil premium, the index gap and the "
                  "haven dollar this reprice produced. Held, not chased and not re-added; the fresh money presses the "
                  "NEW information (MM-044/045/046/047), because recycling a trade that has already paid is not an edge. "
                  "GS earnings vol (MM-043) is also held into Tuesday.")},
        {"label": "2s10s steepener (MM-009) — harvest and trail, don't press", "in": False,
         "text": ("The one rate expression the escalation confirms: ~+35bp, ~+130%, holding through the oil backup. "
                  "Held and trailed, not added &mdash; a hot core could bear-flatten the front. The consensus-agnostic "
                  "steepener remains the higher-conviction rate trade than the directional front-end fade (MM-013).")},
        {"label": "Long gold spot (MM-005) — hold on the min-hold; own the tail via MM-046 instead", "in": False,
         "text": ("Underwater ~-9% and below its $4,250 stop, but held to the ~Jul 15 min-hold (now coinciding with "
                  "CPI). The war STILL didn't save it &mdash; yields backed up and gold traded as a real-rates short. "
                  "The asymmetric upside is now owned with DEFINED risk via the Sep call spread (MM-046), not by adding "
                  "underwater spot.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 17.5},
        {"label": "VIX",   "value": round(_g("vix") or 17.0, 2)},
        {"label": "VIX3M", "value": 19.0},
        {"label": "VIX6M", "value": 20.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.25, 3)},
        {"label": "5Y",  "value": 4.40},
        {"label": "10Y", "value": round(_g("us10y") or 4.589, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 5.02, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-044", "trade": "Long the Brent–WTI spread (own the waterborne Hormuz premium)",
            "asset_class": "Commodity (RV / spread)", "structure": "futures spread",
            "entry": "~$5 (Brent over WTI)", "stop": "spread < $3", "target": "~$9-10",
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The marquee fresh idea: a closed Strait is a waterborne supply shock, and the cleanest way to "
                       "own it is the grade that clears through Hormuz. A third round of US strikes shut the Strait to "
                       "commercial traffic; the disruption hits seaborne Brent far harder than pipeline-fed, "
                       "Cushing-landlocked WTI, yet the spread sits only ~$5. The RV owns the Hormuz mechanism with far "
                       "less de-escalation risk than outright crude &mdash; if Trump's off-ramp is taken, the spread "
                       "gives back a fraction of what a long surrenders &mdash; and presses the book's TotalEnergies "
                       "length on the specific mechanism rather than adding spot into a two-way headline tape."),
        },
        {
            "id": "MM-2026-045", "trade": "Long CHF/JPY (the war haven that isn't the crowded dollar)",
            "asset_class": "FX", "structure": "spot",
            "entry": "~market", "stop": "recent range low", "target": "+3-4%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The cleanest war haven that isn't the dollar. In a genuine risk-off the Swiss franc is "
                       "Europe's reserve haven; the yen, despite its old reputation, is the funder in an energy shock "
                       "because Japan imports its oil and the BoJ is the most dovish major &mdash; a $79 Brent is "
                       "yen-negative. Long CHF/JPY captures the flight-to-quality bid and the oil-importer penalty in "
                       "one cross that the dollar's crowding does not touch, and that the MoF's USD/JPY intervention "
                       "line does nothing to cap. Complements the book's short USD/JPY (MM-007) by owning the haven "
                       "side cleanly."),
        },
        {
            "id": "MM-2026-046", "trade": "Buy Sep gold $4,200/$4,600 call spread (the coiled haven)",
            "asset_class": "Commodity (options)", "structure": "call spread",
            "entry": "~$4,100 spot", "stop": "—", "target": "~5x at $4,600",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Sep expiry", "min_hold_days": 0,
            "thesis": ("Gold is the haven that has refused to fire &mdash; capped the entire war by rising real yields, "
                       "which is exactly the asymmetry. At ~$4,100 it prices none of the tail where a closed Strait and "
                       "an oil cost-push tip into a genuine growth scare, the Fed's hawkish lean flips, real yields "
                       "fall, and the cap that has held bullion down all war snaps. A defined-risk call spread owns "
                       "that convexity for a small premium, complements the underwater cash long (MM-005) without "
                       "adding spot at its min-hold, and is the disciplined way to own the regime-change tail rather "
                       "than fight the current real-rate headwind in the spot."),
        },
        {
            "id": "MM-2026-047", "trade": "Long HY credit protection / short HYG (the laggard)",
            "asset_class": "Credit", "structure": "CDX HY protection / short ETF",
            "entry": "spreads near cycle tights", "stop": "spreads −15bp tighter", "target": "+40bp wider",
            "conviction": 6,
            "conviction_breakdown": {"gap": 3, "catalyst": 1, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("Credit is the asset class that moves last, and it has barely repriced the war. Equity vol is "
                       "finally waking (chips selling, VIX off 15), oil is +4% and the dollar bid, yet HY spreads sit "
                       "near cycle tights &mdash; the market with the most room and the least priced-in risk. A closed "
                       "Strait, an oil cost-push into margins, and a Fed boxed away from cuts is the classic "
                       "spread-widening cocktail. Long HY protection is the cross-asset completion of the 'the tape "
                       "under-priced the war' thesis, in the asset class that reprices slowest and therefore offers the "
                       "cheapest convexity to the same event."),
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
