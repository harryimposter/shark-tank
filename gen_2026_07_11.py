#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-07-11 (Saturday; US markets CLOSED). CHIPS OVER CANNONS.

THE NEXT CHAPTER vs the Jul 3 (The Hawk Disarmed) run:
the disarmed-hawk trade got PARTLY re-armed, a literal ceasefire collapsed into a shooting war, and the
tape chose the chips anyway. SK Hynix's record US IPO out-shouted an 80-target US strike on Iran, equities
booked a winning week, VIX fell to 15, gold FELL — and the June CPI print Tuesday is the one catalyst
neither the AI bid nor the war can soften.
- THE CEASEFIRE COLLAPSED INTO A SHOOTING WAR. At the NATO summit in Turkey (~Jul 7) Trump declared the
  Iran ceasefire "over." Jul 8: US bombed 80+ Iranian targets (air defence, C2, radar, anti-ship, small
  boats) after Iran attacked merchant ships in Hormuz. Jul 9: CENTCOM struck again, degrading Iran's
  shipping-attack capability (60+ IRGC boats). Treasury REVOKED Iran's oil-sale waiver (was to Aug 21).
  Iran warned it will close Hormuz. (Al Jazeera, NBC, CNBC, Bloomberg, CNN.)
- OIL RE-PRICED THE WAR — EQUITIES DID NOT. WTI jumped 4.4% to $73.52 and Brent 5.2% to $78.02 on Jul 8;
  by Fri WTI ~$71.2 (+3.5% wk), Brent ~$76 (+5% wk). The premium the Jul 3 tape had drained is BACK.
  (CNBC, Forbes, Trading Economics.)
- SK HYNIX RE-LIT THE AI-MEMORY TRADE. Jul 10 SK Hynix (SKHY) debuted on Nasdaq — $26.5B raised at $149,
  the BIGGEST FOREIGN IPO IN US HISTORY (past Alibaba 2014), +13% on day one. Bloomberg framed it as "a
  bet that AI breaks the boom-and-bust chip cycle." A direct read-across to the book's 30% Micron weight —
  and the capacity-race tell underneath it. (Bloomberg, TechCrunch, WaPo.)
- THE MELT-UP WON THE WEEK. Fri Jul 10 close: S&P 7,575.39 (+0.42%, +>1% wk), Nasdaq Composite 26,281.61
  (+0.29%), Dow 52,637.01 (+0.29%, off the Jul 2 record ~52,900). VIX 15.03 (−5.11%). Europe/Asia lagged
  on the war: DAX −2.76% wk (Fri +0.78% to 25,779), Nikkei −1.70% wk. (Yahoo, CNBC, T. Rowe.)
- THE HAWK GOT PARTLY RE-ARMED. Yields BACKED UP on the oil cost-push and supply: 10Y ~4.56% (from ~4.485%),
  2Y ~4.21% (from ~4.137%), 2s10s ~+35bp. Fed held 3.50-3.75% (Jun 17); July odds ~74.9% hold / 25.1% hike.
  GOLD FELL on the week (~$4,103 spot / $4,135 Aug fut, from ~$4,200) as real rates rose — the war did NOT
  bid it. (ETF Trends, Fortune, Yahoo, CME.)
- THE EU TAIL RESOLVED; A CANADA TAIL OPENED. The Jul 4 EU deadline passed benignly — the EU cut duties on
  US industrial goods from Jul 1. Jul 10 Trump threatened CANADA with a 35% tariff effective Aug 1. The
  tariff binary rolled forward, it did not close. (EU Commission, CNBC, Bloomberg.)
- THE WEEK AHEAD IS THE DECIDER. June CPI Tue Jul 14 8:30 ET (cons: headline −0.1% m/m → ~3.9% y/y; core
  +0.3% m/m → ~2.9% y/y) — PENDING. Big-bank Q2 earnings Tue Jul 14 (JPM, GS, C, BAC, WFC) + Wed... Jul 15
  (MS, BLK, BNY): a steeper curve = NIM tailwind; GS implied move ~6%. (BLS, Finnhub, Zacks, Motley Fool.)
- BOOK ACTION: the war is the book's ENERGY tailwind (TotalEnergies leads); SK Hynix is the Micron halo AND
  the capacity-race risk (monetise IVol, don't chase); the bond sleeve and Xetra-Gold LAGGED as yields backed
  up. Fresh ideas own the split: a Brent call spread (own the re-armed Hormuz premium the tape priced out),
  an SPX put spread into CPI + a live war at VIX 15, a EUR/USD put spread into a hot-core-CPI dollar tail,
  and a GS earnings-vol long into the widest implied move of the bank cohort.

Run:  python gen_2026_07_11.py
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
# Fallback: US cash markets are CLOSED today (Sat Jul 11, weekend). Inject the web-verified Fri Jul 10
# closes (corroborated Yahoo Finance + CNBC + NBC Palm Springs) so the dashboard headline indices never
# render "unverified". Only set if the live feed did not resolve them.
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
    "MU":   "The name the SK Hynix debut just re-rated by proxy — and the book's largest weight (~30% of the Fable "
            "book). Hynix's $26.5B record IPO (biggest foreign US listing ever, +13% day one) is a direct read-across "
            "to Micron's HBM/AI-memory supercycle: the same demand that drew a $26.5B bid at $149 is Micron's demand. "
            "But the Bloomberg frame — 'a bet that AI breaks the boom-and-bust chip cycle' — is the two-sided tell: the "
            "IPO FUNDS a capacity race (Hynix, Samsung, Micron all adding HBM), and memory is a commodity. Own the "
            "supercycle but monetise the elevated IVol into the top (overwrite/collar), do not chase spot.",
    "NVDA": "The AI leader that catches the SK Hynix halo. Hynix's record debut re-lit the whole memory/accelerator "
            "complex — NVDA is the pull-through demand for the HBM Hynix and Micron sell. At ~32x on $81.6B Q1 revenue "
            "(+85% y/y) it is the reasonably-priced leg against the ~175x AMD challenger; own the leader against the "
            "overbought name (the dispersion RV) rather than chase the cohort into a capacity-race top.",
    "AMD":  "The overbought casualty-in-waiting and the SHORT leg of the chip dispersion. Up ~150% YTD at ~175x "
            "trailing earnings versus NVDA's ~32x on a fraction of the revenue base — the richest name in a cohort the "
            "SK Hynix IPO just pulled fresh supply into. The Fable book HOLDS AMD (+394%), so the trim doubles as "
            "concentration management: sell the exhausted winner into the halo, own the cheaper leader.",
    "XLE":  "Energy is the trade the equity tape refused to make. WTI ~$71 (+3.5% wk) and Brent ~$76 (+5% wk) as the "
            "US-Iran ceasefire collapsed into an 80-target strike and Treasury revoked Iran's oil-sale waiver — a real "
            "supply premium is rebuilding in crude while the S&P booked a winning week and VIX fell to 15. The book's "
            "energy length (TotalEnergies) is the accidental war hedge that IS working; the upside is owned cheaply via "
            "the Brent call spread (MM-040), not chased in spot.",
    "GLD":  "The haven that did NOT show up for the war. Gold FELL on the week (~$4,103 spot, from ~$4,200) even as the "
            "US and Iran traded strikes — because yields backed up (10Y 4.56%) and the oil spike is an inflation/"
            "real-rates story, not a flight-to-safety one. The Jul 3 'gold finally paying' thesis reversed: the book's "
            "cash gold long (MM-005) is underwater on its min-hold (to ~Jul 15). Gold is a rate trade, not a war trade "
            "— it needs a soft CPI Tuesday, not a Hormuz headline.",
    "TLT":  "The oil cost-push is duration's enemy again. The 10Y backed up to ~4.56% and the 2Y to ~4.21% as the war "
            "re-lit the inflation risk and the supply/term-premium overhang held — so the short-10Y (MM-004) is the "
            "laggard and the short-2Y (MM-013) gave back its edge. Own the curve SHAPE (the steepener MM-009, ~+35bp), "
            "not outright long-end duration, into a CPI print that could back the whole curve up further.",
    "XLF":  "The cohort that reports first and reports into a tailwind. Big banks kick off Q2 season Tue Jul 14 (JPM, "
            "GS, C, BAC, WFC) into a steeper curve (2s10s ~+35bp = NIM support) and a re-accelerating IB pipeline; GS "
            "carries the widest implied move (~6%). Own the earnings-vol leader (GS, MM-043) — a beat on investment "
            "banking against a split sell-side (15 buy / 15 hold / 2 sell) is the asymmetry.",
    "SPY":  "The melt-up bought a record IPO through a shooting war and booked a winning week with VIX at 15 — a "
            "complacency read into a two-sided June CPI (Tue) and a live Hormuz blockade. The index is pricing AI "
            "durability and a benign print at the same time; the SPX put spread (MM-041) owns the gap the record tape "
            "is ignoring, structured for the discrete CPI + war-headline risk, not a chase of at-the-money premium.",
    "EEM":  "Korea is the story the IPO tells and the war complicates. SK Hynix's US debut is a Korean-champion event "
            "that re-rates the KOSPI memory complex; the Nikkei (−1.70% wk) and Asia broadly lagged on the Gulf strikes "
            "and a firmer yen. The AI-memory bid and the war premium pull EM Asia two ways — a stock-pickers' tape, not "
            "a beta one.",
    "BTC":  "Bitcoin still capped, not participating in the AI-led risk-on the way the Nasdaq is — the same "
            "backing-up-real-rates regime that sank gold keeps a lid on the speculative long tail. A tell that the "
            "liquidity is rotating into AI equity and energy, not into duration or crypto. Not a book position.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("Chips Over Cannons: A Record IPO Out-Shouts a Re-Ignited Gulf War — the Melt-Up Bought SK Hynix's "
          "$26.5bn Debut Through an 80-Target US Strike, Booked a Winning Week at VIX 15, and Left June CPI "
          "Tuesday as the One Catalyst Neither the AI Bid Nor the War Can Soften")
regime_note = (
    "The most important thing that happened in the last week is that a literal ceasefire collapsed into a shooting "
    "war and the tape chose the chips. At the NATO summit in Turkey around Jul 7 Trump declared the Iran ceasefire "
    "'over'; on Jul 8 the US bombed more than 80 Iranian targets after Tehran attacked merchant ships in Hormuz, on "
    "Jul 9 CENTCOM struck again to degrade Iran's shipping-attack capability, and the Treasury revoked Iran's "
    "oil-sale waiver. Oil re-priced it — WTI +4.4% to $73.52, Brent +5.2% to $78.02 on Jul 8, both up ~3.5-5% on the "
    "week. And equities booked a WINNING week anyway: the S&P closed 7,575.39, up over 1% on the week, the Nasdaq at "
    "26,281.61, and VIX FELL to 15.03. The reason has a name and a ticker: SK Hynix (SKHY) debuted Jul 10 in the "
    "biggest foreign IPO in US history — $26.5B at $149, +13% on day one — and re-lit the AI-memory trade through a "
    "real war. (Al Jazeera, CNBC, Bloomberg, Yahoo Finance.) "
    "Decompose the week the tape is celebrating. The headline is a winning week for US equities during a Gulf war — "
    "which reads as resilience. The anatomy says something narrower: the gain is an AI-capex event (a $26.5B bid for "
    "Korean memory) layered on a market that has fully desensitised to the Gulf, while the assets that SHOULD move in "
    "a war moved the wrong way. Gold FELL. Bonds SOLD (10Y to 4.56%). The dollar barely firmed (DXY ~100.97). The "
    "classic war-haven trade inverted because the oil spike is a cost-push, not a flight to safety — it lifts "
    "inflation risk and real yields, which is bearish gold and bearish duration. So what, who's wrong, what's the "
    "trade: the consensus that reads a winning week as broad resilience is wrong; the resilience is one trade (AI "
    "memory) doing all the work while a real war premium rebuilds in crude that the equity tape has priced out. "
    "(Fortune, ETF Trends, CNBC.) "
    "The second-order effect consensus is missing is the collision Tuesday. A tape at VIX 15, long AI durability and "
    "a benign CPI at the same time, walks into June CPI on Jul 14 (consensus core +0.3% m/m, ~2.9% y/y) with a fresh "
    "oil cost-push in the pipeline and a Fed already leaning nine-of-eighteen toward a hike. The melt-up is pricing "
    "the dovish tail (a soft print that revives the rate-cut story) and ignoring the cost-push tail (a hot core plus "
    "$76 Brent that re-arms the hawk it thought the July 2 payroll disarmed). The Papic constraint runs through both "
    "fronts: Trump owns the 'ceasefire is over' declaration, so de-escalation is politically expensive, and he opened "
    "a second tariff front (a 35% Canada tariff, Aug 1) the same week — the tariff binary rolled forward, it did not "
    "close. The Burry tell is inside the IPO everyone cheered: SK Hynix's record debut is, in Bloomberg's own frame, "
    "'a bet that AI breaks the boom-and-bust chip cycle' — and the more capital the AI narrative pulls in at the top, "
    "the more HBM capacity Hynix, Samsung and Micron add, and the more violently the eventual glut resolves. The "
    "book is 30% Micron; it is long exactly that bet. "
    "The book sits astride the split. The war is the ENERGY tailwind the equity tape refused to price: TotalEnergies "
    "is the position that leads. The rate book is mixed — the 2s10s steepener (MM-009) is the winner at ~+35bp, but "
    "the short-10Y (MM-004) and short-2Y (MM-013) gave back edge as yields backed up, and gold (MM-005) is underwater "
    "on its min-hold as the war sank it rather than saved it. Short EUR/USD (MM-012) is back to modestly working as "
    "the dollar base-built at 101. The trade into Tuesday is to own the war premium the tape priced out (a Brent call "
    "spread), hedge the complacent index into a two-sided CPI (an SPX put spread at VIX 15), own the hot-core dollar "
    "tail (a EUR/USD put spread), and press the bank cohort that reports into a steeper curve (GS earnings vol). The "
    "regime is not 'resilience.' It is a market that has decided one AI trade can absorb a shooting war — and a CPI "
    "print that is about to test whether it can absorb an oil-driven inflation scare too."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# No close action today. MM-005 (gold) stays open on its 45-day min-hold (to ~Jul 15) though spot is below
# the $4,250 stop — the rule holds it to the decision date. All other legs inside their stops/min-holds.

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
            "The quiet leg, roughly flat near the entry as a risk-on melt-up keeps a bid under the commodity-AUD. A "
            "paused ECB still caps the EUR side, but the AI-led risk-on and firmer oil (an AUD-adjacent commodity bid) "
            "rebuild the AUD carry, pinning the cross to the middle of its range rather than toward the 1.61 target. "
            "There is no dated EUR catalyst left; the edge has thinned, and this is the leg to trim into strength "
            "rather than defend. Stop 1.662, close by."
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
            "The laggard, and the tell about the war's inflation transmission. The 10Y backed UP to ~4.56% from the "
            "4.44% entry as the oil spike (Brent $76, +5% on the week) re-lit inflation expectations and the "
            "supply/term-premium overhang held — the safe-haven bid a shooting war should produce never showed, "
            "because a cost-push is bearish duration. The disinflation thesis is now on the wrong side of a live oil "
            "shock and a CPI print (Tue) that could back the whole curve up further. The expression that pays is the "
            "curve (MM-009), not outright long-end duration. Stop 4.65%, ~9bp away — a tight rein."
        ),
        "catalysts": [
            "June CPI Tue Jul 14 (core +0.3% m/m cons) — the print that confirms or breaks the long-end backup",
            "Brent $76 / oil cost-push — the fresh inflation risk pinning the 10Y",
            "Treasury supply + term premium — the structural anchor keeping the long end heavy",
            "A Hormuz de-escalation — the disinflation relief that would let the 10Y rally",
        ],
        "risks": (
            "A hot core CPI plus a sustained oil premium sells the long end toward and through the 4.65% stop; only a "
            "clean Hormuz de-escalation and a soft CPI rescue it. Stop 4.65% (now ~4.56%, ~9bp away)."
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
            "The trade the war was supposed to save — and didn't. Gold FELL on the week toward ~$4,103 (from ~$4,200), "
            "underwater ~-9% from the $4,523 entry, even as the US and Iran traded strikes. The Jul 3 'gold finally "
            "paying' thesis reversed: with yields backing up (10Y 4.56%) on the oil cost-push, gold traded as a "
            "real-rates SHORT again, not a haven. The lesson is that gold is a RATE trade here, not a war trade — it "
            "needs a soft CPI Tuesday and a lower-real-rate path, not a Hormuz headline. Held through the drawdown on "
            "its 45-day min-hold (to ~Jul 15); the decision comes at the min-hold, and a hot CPI is the risk that "
            "forces the exit."
        ),
        "catalysts": [
            "June CPI Tue Jul 14 — a soft core is the real-rates relief gold needs; a hot one confirms the exit",
            "Real yields / the 10Y at 4.56% — the headwind that sank gold through the war",
            "The Fed's 9-of-18 hike lean — the policy path capping the debasement bid",
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
            "Offside but improving at the margin. USD/JPY sits ~161.6, above the 159.37 entry (~-1.4%), as the oil-led "
            "yield backup re-widened the US-Japan differential and the dollar base-built at 101 — the opposite of the "
            "Jul 3 dollar-top tailwind. The offset is domestic: Japan is weighing measures to push pension funds into "
            "domestic assets, which firmed the yen on Friday, and the MoF line near 160 is the backstop below. The "
            "structural case (a BoJ normalised toward 1.00%, a Fed that cannot sustain a hawkish repricing into a "
            "labour crack) is intact but on hold until CPI resolves the rate path. Patient short; 163 is the stop."
        ),
        "catalysts": [
            "June CPI Tue — the print that decides whether the US-Japan differential widens or narrows",
            "Japan pension-fund domestic-asset measures — the yen-supportive flow that firmed it Friday",
            "MoF intervention at the 160 line — the official backstop below",
            "Oil-led yield backup — the differential-widener working against the short",
        ],
        "risks": (
            "A hot US CPI re-widens the differential and pushes USD/JPY toward the 163 stop; risk-on keeps the carry "
            "alive. Stop 163.00 (now ~161.6, ~1.4 pts away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is above 2yr-differential fair value, but the differential re-widened on the "
                            "oil-led backup, narrowing the near-term edge.",
            "catalyst":     "1/2 — the CPI is the dated catalyst but two-sided; the pension flow is the slow-burn support.",
            "positioning":  "1/2 — the yen carry is still crowded long-USD; the unwind needs a rate-path turn.",
            "confirmation": "1/2 — the yen firmed Friday on the pension chatter; a first, small confirming move.",
            "stop_quality": "1/1 — 163.00 is a clean MoF-intervention ceiling; ~1.4 pts risk.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (receive/own cut optionality), short "
            "the 10Y (short fiscal-supply risk). Pays when 10Y-minus-2Y widens. Currently ~2Y 4.21% "
            "/ 10Y 4.56%, spread ~+35bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "The best position in the book and the one expression the war did not break. Both ends backed up this week "
            "on the oil cost-push — the 2Y to ~4.21%, the 10Y to ~4.56% — but the spread held ~+35bp, keeping the open "
            "gain near ~+130% off the +15bp entry (an 18-month inversion). This is the right trade for the whole "
            "regime: a Fed boxed between a labour crack and an oil-CPI can neither hike hard nor cut, which pins the "
            "front, while fiscal supply and the war's inflation premium keep the long end heavy — a structural steepener "
            "in either CPI outcome. Min-hold to ~Jul 16; target +60bp; held, trail the stop up, do not add into the run."
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
            "Back to modestly working as the dollar top stalled. EUR/USD sits ~1.1415 and DXY base-built at ~100.97 — "
            "the Jul 3 dollar-roll paused because the oil-led yield backup (10Y 4.56%) rebuilt some of the "
            "rate-differential bid, and a firmer oil price is a euro-negative terms-of-trade shock (the euro area "
            "imports its energy). The short is green (~+1.6% from the 1.16 entry) with a distant 1.182 stop. The June "
            "CPI (Tue) is the swing: a hot core re-arms the Fed and extends the dollar; a soft one revives the roll and "
            "argues to trim. Hold the core short; own the specific hot-CPI upside via the defined-risk put spread "
            "(MM-042)."
        ),
        "catalysts": [
            "June CPI Tue — a hot core re-arms the Fed and bids the dollar; a soft one revives the euro",
            "Brent $76 oil premium — the euro-negative terms-of-trade shock supporting the short",
            "DXY base-building at 101 — the dollar top that stalled, back in the short's favour",
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
            "Vindicated on Jul 2, partly given back on the oil re-arm. The 2Y backed up to ~4.21% from the 4.137% "
            "post-payroll low, just above the 4.162% entry (~flat-to-slightly-red), as the war's oil cost-push and a "
            "Fed leaning 9-of-18 toward a hike re-priced some near-term hike risk. The thesis — that the front end "
            "over-prices a 2026 hike into a cracking labour market — is intact, but the June CPI (Tue) is the decider: "
            "a soft core re-confirms the fade and re-rallies the 2Y; a hot one, plus $76 Brent, re-arms the hike and "
            "backs the 2Y toward the 4.35% stop. Min-hold elapsed; stop 4.35%, now ~14bp away. Hold on a tight rein; "
            "the curve (MM-009) is the higher-conviction, consensus-agnostic expression of the same view."
        ),
        "catalysts": [
            "June CPI Tue — the decider: soft re-confirms the fade, hot re-arms the hike",
            "Oil cost-push ($76 Brent) — the fresh inflation risk backing up the 2Y",
            "The Fed's 9-of-18 hike lean — the hawkish anchor the trade fades",
            "The next labour print — the crack that ultimately prices the hike out",
        ],
        "risks": (
            "A hot CPI plus a sustained oil premium re-prices a 2026 hike and backs the 2Y up to the 4.35% stop. Stop "
            "4.35% (now ~4.21%, ~14bp away)."
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
    "MM-2026-040": {
        "instrument": (
            "Buy an August Brent $78/$88 call spread — defined-risk upside on the international crude benchmark "
            "(tradeable via ICE Brent options or a crude/energy-ETF call spread). Buy the $78 call, sell the $88 call. "
            "Owns the re-armed Hormuz war premium the equity tape has priced out, with capped premium; max loss is the "
            "premium. With Brent ~$76 after a +5% week, the lower strike is near-the-money — cheap convexity on a "
            "supply premium that is rebuilding, not draining."
        ),
        "fundamental_thesis": (
            "The marquee idea: the war the tape refused to price is a live supply shock in crude. The ceasefire "
            "collapsed into an 80-target US strike, Iran attacked merchant ships and warned it will close Hormuz, and "
            "the Treasury revoked Iran's oil-sale waiver — a genuine supply premium — yet the S&P booked a winning "
            "week and VIX fell to 15. Brent re-priced +5% but sits ~$76, far below where a real Hormuz disruption "
            "clears. A call spread struck near spot owns the escalation tail with defined risk, and it is the "
            "disciplined way to press the book's existing energy length (TotalEnergies) without adding spot crude into "
            "a two-way headline tape."
        ),
        "catalysts": [
            "Ceasefire 'over' + 80-target US strike + Hormuz ship attacks — the live supply premium",
            "Treasury oil-waiver revocation — the sanctions squeeze on Iranian barrels",
            "Iran's threat to close Hormuz — the tail the $88 strike owns",
            "Weekend Oman-brokered Hormuz talks — the de-escalation risk (the premium's fade)",
        ],
        "risks": (
            "The Oman-brokered two-route Hormuz proposal holds, ships get safe passage, and the premium drains back "
            "toward the pre-war $69; the spread decays as insurance that did not extend. Max loss is the premium — "
            "defined risk."
        ),
        "breakdown_why": {
            "gap":          "3/3 — the equity tape priced the war OUT (VIX 15, winning week) while a real supply "
                            "premium rebuilt in crude — a wide, cross-asset mispricing.",
            "catalyst":     "2/2 — the strikes and the waiver revocation are live and dated; the Hormuz binary is the tail.",
            "positioning":  "1/2 — spec crude length is light after the ceasefire drained the premium; squeeze-prone on escalation.",
            "confirmation": "1/2 — Brent already re-priced +5% on the week; one confirming leg, not yet a trend.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-041": {
        "instrument": (
            "Buy a July SPX 7,400/7,150 put spread — defined-risk index downside into June CPI (Tue Jul 14) and a live "
            "Gulf war, on a tape that booked a winning week at VIX 15. Buy the 7,400 put, sell the 7,150 put. Max loss "
            "is the premium; the portfolio overlay on a book long AI equities. With the S&P at ~7,575, both strikes "
            "are below spot — cheap convexity with VIX at ~15."
        ),
        "fundamental_thesis": (
            "The melt-up bought a record IPO through an 80-target strike and priced a benign CPI at the same time — "
            "VIX fell to 15 into a two-sided print. That is the gap: June CPI (core +0.3% m/m consensus, ~2.9% y/y) "
            "lands with a fresh $76-Brent oil cost-push in the pipeline and a Fed leaning 9-of-18 toward a hike, while "
            "the tape is long AI durability and short volatility. A hot core re-arms the hike the market thought the "
            "July 2 payroll disarmed; a Hormuz re-escalation over the print is a second, uncorrelated tail. A July "
            "7,400/7,150 put spread re-establishes the index hedge on an AI-concentrated book, structured for the "
            "discrete CPI + war-headline risk — not a chase of at-the-money premium into cheap vol."
        ),
        "catalysts": [
            "June CPI Tue Jul 14 (core +0.3% m/m cons) — the two-sided print at VIX 15",
            "Brent $76 oil cost-push — the inflation risk that re-arms the hawk on a hot core",
            "Live Hormuz war — the uncorrelated risk-off tail over the print",
            "Big-bank earnings Tue/Wed — the read on the real economy that can undercut the melt-up",
        ],
        "risks": (
            "A soft CPI plus a Hormuz de-escalation extends the melt-up and the S&P grinds higher into a calm tape; "
            "vol stays crushed and the spread decays. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the index prices AI durability and a benign CPI at once while an oil cost-push and a "
                            "live war argue for two-sided risk.",
            "catalyst":     "2/2 — the CPI is dated and inside the structure's life; the war headline is the second tail.",
            "positioning":  "2/2 — VIX 15 into a two-sided print is complacency; the crowd is short vol and long the melt-up.",
            "confirmation": "0/2 — the tape is near a record; no confirming down-leg — a fresh, pre-emptive hedge.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-042": {
        "instrument": (
            "Buy a 1-week EUR/USD 1.135/1.115 put spread — defined-risk downside on the euro into June CPI (Tue). Buy "
            "the 1.135 put, sell the 1.115 put. Max loss is the premium. With spot ~1.1415, both strikes are "
            "out-of-the-money — cheap convexity on the hot-core-CPI dollar tail the market is not pricing after the "
            "dollar top stalled."
        ),
        "fundamental_thesis": (
            "The dollar top stalled and the euro is the cleanest way to own the hot-CPI tail. DXY base-built at ~101 as "
            "the oil-led yield backup rebuilt the rate-differential bid, and a $76-Brent premium is a euro-negative "
            "terms-of-trade shock — the euro area imports its energy. June CPI (Tue, core +0.3% m/m consensus) is the "
            "trigger: a hot core re-arms the Fed the July 2 payroll disarmed, extends the dollar, and drops EUR/USD "
            "toward the 1.13 handle. A defined-risk put spread owns that specific print without fighting a two-way spot "
            "tape, and it lets the book hold its core short (MM-012) while carrying the CPI tail cheaply."
        ),
        "catalysts": [
            "June CPI Tue (core +0.3% m/m cons) — the hot-core dollar trigger",
            "Brent $76 — the euro-negative energy terms-of-trade shock",
            "DXY base-building at 101 — the stalled dollar top, back in the short's favour",
            "The Fed's 9-of-18 hike lean — the hawkish anchor a hot CPI reactivates",
        ],
        "risks": (
            "A soft CPI revives the dollar roll and EUR/USD squeezes back toward 1.16; a Hormuz de-escalation drops oil "
            "and lifts the euro. The spread decays as insurance that did not fire. Max loss is the premium — defined "
            "risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the market faded the dollar after Jul 2; a hot core plus an oil shock is the "
                            "re-arm it is under-pricing.",
            "catalyst":     "2/2 — the CPI is dated and inside the structure's life; the oil premium compounds it.",
            "positioning":  "1/2 — the market leaned dovish/short-dollar after the payroll; a hot print is the pain trade.",
            "confirmation": "0/2 — EUR/USD is near 1.14 with no down-move yet — a fresh, contrarian tail.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-043": {
        "instrument": (
            "Long Goldman Sachs (GS) into Q2 earnings (Tue Jul 14 BMO) — expressed as long stock or a long "
            "call/call-spread to own the widest implied move in the bank cohort (~6%) with defined risk. A bet that "
            "investment-banking and trading re-acceleration beats a split sell-side into a steeper curve."
        ),
        "fundamental_thesis": (
            "The bank cohort reports into a tailwind and GS is the highest-beta way to own it. Big banks kick off Q2 "
            "season Tue Jul 14 (JPM, GS, C, BAC, WFC) into a 2s10s at ~+35bp — a NIM tailwind — and a re-accelerating "
            "capital-markets pipeline. GS carries the widest implied move (~6%) and the most divided sell-side (15 buy "
            "/ 15 hold / 2 sell, Finnhub), on a consensus of ~$14.46 EPS and ~$16.4B revenue after beating four "
            "straight quarters. The asymmetry is a beat on investment banking against a split book: the names most "
            "consensus doubts have the most room to re-rate. Own the earnings vol with defined risk (a call spread), "
            "not the whole cohort — JPM and the NIM-only regionals are lower-beta to the IB re-acceleration."
        ),
        "catalysts": [
            "GS Q2 earnings Tue Jul 14 BMO — the ~6% implied move, the widest in the cohort",
            "2s10s ~+35bp — the steeper curve = NIM tailwind for the whole group",
            "IB/trading re-acceleration — the line the sell-side is most split on (15/15/2)",
            "The June CPI same day — the macro cross-current that can swamp the print",
        ],
        "risks": (
            "A hot CPI same-day sinks the whole tape and swamps a good print; a trading/IB miss or a credit-reserve "
            "build disappoints on a stock that has beaten four straight quarters. Defined risk via a call spread caps "
            "the downside to the premium."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the ~6% implied move and a split sell-side leave room to re-rate on an IB beat; the "
                            "stock is not priced for the pipeline re-acceleration.",
            "catalyst":     "2/2 — the print is dated (Jul 14 BMO) and inside the structure's life.",
            "positioning":  "1/2 — the divided book (15 buy / 15 hold / 2 sell) is the room; not a crowded long.",
            "confirmation": "1/2 — the cohort's steeper-curve tailwind is confirming; the print is the test.",
            "stop_quality": "1/1 — defined-risk via a call spread; the premium is the max loss.",
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
    "MM-2026-001": "FLAT. EUR/AUD near entry — the AI-led risk-on keeps a bid under the commodity-AUD, pinning the cross mid-range, not toward the 1.61 target. No EUR catalyst left; edge thinned. Trim into strength. Stop 1.662 (close). Tight leash.",
    "MM-2026-004": "THE LAGGARD. 10Y ~4.56%, backed UP from the 4.44% entry (~-2.7%) as the oil cost-push re-lit inflation and supply pinned the long end — the war produced NO haven bid. Better expressed via the curve (MM-009). Stop 4.65% (~9bp) — a tight rein into CPI.",
    "MM-2026-005": "THE WAR DIDN'T SAVE IT. Gold FELL to ~$4,103 (~-9% from the $4,523 entry) even as US-Iran traded strikes — yields backed up and gold traded as a real-rates short, not a haven. Held on its min-hold (to ~Jul 15); a soft CPI Tue is the only rescue. Decision at the min-hold.",
    "MM-2026-007": "OFFSIDE, IMPROVING. USDJPY ~161.6, above the 159.37 entry (~-1.4%), as the oil-led yield backup re-widened the differential; the yen firmed Friday on Japan pension-domestic-asset chatter. Stop 163.00; CPI is the swing. Tight leash.",
    "MM-2026-009": "THE WINNER. 2s10s ~+35bp, ~+130% off the +15bp entry — the spread held through a week of backing-up yields. The one expression the war didn't break: a Fed boxed between a labour crack and an oil-CPI. Min-hold ~Jul 16; trail the stop; stop -10bp; target +60bp.",
    "MM-2026-012": "BACK TO WORKING. ~1.1415 with DXY base-built at ~101 — the Jul 3 dollar roll stalled as the oil-led yield backup rebuilt the rate-differential bid and $76 Brent hit the euro's terms of trade. Green (~+1.6%), stop 1.182 distant. Hold the core short; own the hot-CPI tail via MM-042.",
    "MM-2026-013": "GAVE BACK EDGE. 2Y ~4.21%, backed up to just above the 4.162% entry (~flat-to-red) as the oil cost-push and the Fed's 9-of-18 hike lean re-priced near-term hike risk. Min-hold elapsed; stop 4.35% (~14bp). CPI Tue is the decider; the curve (MM-009) is the higher-conviction sibling.",
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
    {"datum": "US EQUITY + BOND MARKETS CLOSED Sat Jul 11 (weekend). Brief covers the week to Fri Jul 10 close + the weekend Iran/Hormuz diplomacy. Reopen Mon Jul 13; June CPI Tue Jul 14; big-bank earnings Tue-Wed.",
     "source": "NYSE/Nasdaq + SIFMA calendar", "asof": TODAY, "stale": False},
    {"datum": "US-IRAN CEASEFIRE COLLAPSED: Trump declared it 'over' at the NATO summit (~Jul 7); Jul 8 US struck 80+ Iranian targets after Iran attacked merchant ships in Hormuz; Jul 9 CENTCOM struck 60+ IRGC boats; Treasury revoked Iran's oil-sale waiver. Iran threatens to close Hormuz.",
     "source": "Al Jazeera + NBC + CNBC + Bloomberg (corroborated)", "asof": "2026-07-09", "stale": False},
    {"datum": "Weekend Jul 11: Iran FM Araghchi met his Omani counterpart; Oman drafting a tentative two-route Hormuz traffic proposal. US says talks can't progress until ships get safe passage; Trump warns of further strikes on fresh vessel attacks.",
     "source": "CNN + RFE/RL (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "SK HYNIX (SKHY) US IPO Jul 10: $26.5bn raised at $149/ADS, the BIGGEST FOREIGN IPO IN US HISTORY (past Alibaba 2014), +13% on debut. Framed as a bet AI breaks the boom-and-bust chip cycle; urged to build US fabs (Indiana packaging).",
     "source": "Bloomberg + TechCrunch + Washington Post (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "Fri Jul 10 US close: S&P 500 7,575.39 (+0.42%, +31.75; +>1% wk); Nasdaq Composite 26,281.61 (+0.29%, +74.72); Dow 52,637.01 (+0.29%, +149.60; off the Jul 2 record ~52,900). VIX 15.03 (−5.11%).",
     "source": "Yahoo Finance + CNBC + NBC Palm Springs (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "Oil (Fri Jul 10): WTI ~$71.2 (+3.5% wk), Brent ~$76 (+5% wk) on the Hormuz supply premium. Jul 8 spike: WTI +4.4% to $73.52, Brent +5.2% to $78.02. Brent-WTI spread ~$5.",
     "source": "CNBC + Forbes + Trading Economics (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "Gold FELL on the week to ~$4,103 spot / $4,135 Aug fut (from ~$4,200) as yields backed up — the war produced no haven bid; gold traded as a real-rates short.",
     "source": "Fortune + Yahoo Finance (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "Rates (Fri Jul 10): US 10Y ~4.56% (from ~4.485%), 2Y ~4.21% (from ~4.137%), 2s10s ~+35bp — the oil cost-push backed the curve UP. Fed held 3.50-3.75% (Jun 17); July odds ~74.9% hold / 25.1% hike; 9 of 18 members see a 2026 hike.",
     "source": "ETF Trends + CME FedWatch + Fed SEP (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "FX (Fri Jul 10): DXY ~100.97 (+0.06%, base-building at 101); EUR/USD ~1.1415 (−0.13%); USD/JPY ~161.6 (−0.41%, yen firmer on Japan pension-domestic-asset chatter).",
     "source": "Trading Economics + Vantage + MQL5 (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "Europe/Asia (wk to Jul 10): DAX −2.76% wk (Fri +0.78% to 25,779.31); Nikkei −1.70% wk (~69,737 Mon) — both lagged US on the Gulf strikes. Turbulent week ended on an uptick.",
     "source": "T. Rowe Price + Sharecast (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "June CPI PENDING — Tue Jul 14 08:30 ET. Consensus: headline −0.1% m/m (~3.9% y/y); core +0.3% m/m (~2.9% y/y). The decider between the disinflation read and an oil cost-push re-arm.",
     "source": "BLS + Kiplinger + Cleveland Fed nowcast (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Big-bank Q2 earnings PENDING — Tue Jul 14 BMO: JPM (EPS est ~$5.74), GS (~$14.46, rev ~$16.4B, implied move ~6%), C (~$2.76), BAC (~$1.13), WFC (~$1.73); Jul 15: MS, BLK, BNY. Steeper curve = NIM tailwind.",
     "source": "Finnhub + Zacks + Motley Fool (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Trump threatened CANADA with a 35% tariff effective Aug 1 (Jul 10); the Jul 4 EU deadline passed benignly (EU cut duties on US industrial goods from Jul 1). The tariff binary rolled forward.",
     "source": "CNBC + Bloomberg + EU Commission (corroborated)", "asof": "2026-07-10", "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-07-10", "stale": True},
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
        "CHIPS OVER CANNONS. A literal ceasefire collapsed into a shooting war — Trump declared the Iran ceasefire "
        "'over' (~Jul 7), the US struck 80+ Iranian targets (Jul 8) and 60+ IRGC boats (Jul 9) after Iran attacked "
        "ships in Hormuz, and the Treasury revoked Iran's oil-sale waiver — and the tape chose the chips. SK Hynix's "
        "$26.5bn Nasdaq debut (Jul 10), the biggest foreign IPO in US history, re-lit the AI-memory trade; the S&P "
        "booked a winning week to 7,575.39 and VIX FELL to 15.03. But the war repriced OIL (Brent ~$76, +5% wk) not "
        "equities, and gold FELL and bonds SOLD (10Y ~4.56%) — the classic war-haven trade inverted because the oil "
        "spike is a cost-push, not a flight to safety. The book's energy length (TotalEnergies) is the accidental war "
        "hedge that IS working; the bond sleeve and Xetra-Gold lagged. June CPI Tue Jul 14 (core +0.3% m/m cons) and "
        "the big-bank earnings kickoff are the deciders. The trade: own the war premium the tape priced out (Brent "
        "call spread), hedge the complacent index into a two-sided CPI (SPX put spread at VIX 15), own the hot-core "
        "dollar tail (EUR/USD put spread), and press the bank cohort into a steeper curve (GS earnings vol)."
    ),

    "summary_narrative": """
<p>The most important thing about the last week is that a literal ceasefire collapsed into a shooting war and the tape
chose the chips. At the NATO summit in Turkey around July 7 Trump declared the Iran ceasefire &ldquo;over&rdquo;; on
July 8 the US bombed more than 80 Iranian targets after Tehran attacked merchant ships in the Strait of Hormuz, on July
9 CENTCOM struck again, and the Treasury revoked Iran&rsquo;s oil-sale waiver. Oil re-priced it &mdash; Brent jumped
5.2% to $78 on the strikes and held ~$76 into Friday, up 5% on the week. And US equities booked a <strong>winning
week anyway</strong>: the S&amp;P closed 7,575.39, up over 1%, and VIX <em>fell</em> to 15.03. The reason has a ticker:
SK Hynix debuted July 10 in the <strong>biggest foreign IPO in US history</strong> &mdash; $26.5bn at $149, +13% on day
one &mdash; and re-lit the AI-memory trade through a real war. (Al Jazeera, CNBC, Bloomberg, Yahoo Finance.)</p>

<p>Decompose the week the tape is celebrating. A winning week during a Gulf war reads as resilience; the anatomy says
something narrower. The gain is one trade &mdash; a $26.5bn bid for Korean memory &mdash; layered on a market that has
fully desensitised to the Gulf, while the assets that <em>should</em> move in a war moved the wrong way. Gold FELL.
Bonds SOLD, the 10Y backing up to 4.56%. The dollar barely firmed. The classic war-haven trade inverted because the oil
spike is a cost-push, not a flight to safety &mdash; it lifts inflation risk and real yields, which is bearish gold and
bearish duration. So what, who is wrong, what is the trade: the consensus reading a winning week as broad resilience is
wrong; the resilience is AI memory doing all the work while a real supply premium rebuilds in crude the equity tape has
priced out. (Fortune, ETF Trends, CNBC.)</p>

<p>The second-order effect consensus is missing is the collision Tuesday. A tape at VIX 15, long AI durability and a
benign CPI at once, walks into June CPI on July 14 &mdash; consensus core +0.3% month-on-month, ~2.9% annual &mdash;
with a fresh $76-Brent oil cost-push in the pipeline and a Fed already leaning nine-of-eighteen toward a hike. The
melt-up is pricing the dovish tail and ignoring the cost-push tail: a hot core plus expensive crude re-arms the hike the
market thought the July 2 payroll disarmed. And the Burry tell sits inside the IPO everyone cheered &mdash; SK
Hynix&rsquo;s record debut is, in Bloomberg&rsquo;s frame, a bet that AI breaks the boom-and-bust chip cycle. The more
capital the AI narrative pulls in at the top, the more HBM capacity Hynix, Samsung and Micron add, and the more
violently the eventual glut resolves. The book is 30% Micron; it is long exactly that bet.</p>

<p>The book sits astride the split. The war is the ENERGY tailwind the equity tape refused to price &mdash; TotalEnergies
leads. The rate book is mixed: the 2s10s steepener (MM-009) is the winner at ~+35bp and the one expression the war
didn&rsquo;t break, but the short-10Y (MM-004) and short-2Y (MM-013) gave back edge as yields backed up, and gold
(MM-005) is underwater on its min-hold because the war sank it rather than saved it. Short EUR/USD (MM-012) is back to
modestly working as the dollar base-built at 101 and a $76 Brent hit the euro&rsquo;s terms of trade.</p>

<p>The regime is not &lsquo;resilience.&rsquo; It is a market that has decided one AI trade can absorb a shooting war
&mdash; and a CPI print Tuesday that is about to test whether it can absorb an oil-driven inflation scare too. The
posture into the print is to own the war premium the tape priced out, hedge the complacent index at VIX 15, own the
hot-core dollar tail, and press the bank cohort that reports into a steeper curve.</p>
""",

    "takeaways": [
        "<strong>A ceasefire collapsed into a shooting war and the tape chose the chips.</strong> Trump declared the "
        "Iran truce 'over' (~Jul 7); the US struck 80+ targets (Jul 8) and 60+ IRGC boats (Jul 9) after Iran hit ships "
        "in Hormuz, and the Treasury revoked Iran's oil waiver &mdash; yet the S&amp;P booked a winning week and VIX "
        "fell to 15. (Al Jazeera, CNBC.)",

        "<strong>SK Hynix's record IPO did the heavy lifting.</strong> The Korean memory maker's $26.5bn Nasdaq debut "
        "(Jul 10) &mdash; the biggest foreign IPO in US history, +13% day one &mdash; re-lit the AI-memory trade and "
        "carried the week. A direct read-across to the book's 30% Micron weight. (Bloomberg, TechCrunch.)",

        "<strong>The war repriced OIL, not equities &mdash; and inverted the haven trade.</strong> Brent +5% on the "
        "week to ~$76, but gold FELL (~$4,103) and bonds SOLD (10Y 4.56%) because the oil spike is a cost-push, not a "
        "flight to safety. The book's energy length (TotalEnergies) is the war hedge that actually worked. (Fortune, "
        "ETF Trends.)",

        "<strong>The hawk got partly re-armed.</strong> Yields backed up on the oil cost-push and supply &mdash; 10Y "
        "~4.56%, 2Y ~4.21%, 2s10s ~+35bp. The July 2 disarmed-hike trade gave back edge; the short-10Y (MM-004) and "
        "short-2Y (MM-013) lagged, and only the steepener (MM-009) held. (CME, FRED.)",

        "<strong>June CPI Tuesday is the collision.</strong> A tape at VIX 15 walks into a two-sided print (core +0.3% "
        "m/m cons, ~2.9% y/y) with a fresh $76-Brent cost-push and a Fed leaning 9-of-18 toward a hike. The SPX put "
        "spread (MM-041) owns the gap the complacent index is ignoring. (BLS, Kiplinger.)",

        "<strong>The tariff binary rolled forward, it didn't close.</strong> The Jul 4 EU deadline passed benignly (EU "
        "cut industrial-goods duties Jul 1) &mdash; but Trump opened a 35% Canada tariff for Aug 1 (Jul 10). The "
        "cost-push front stays live; the EU tail on LVMH/SAP lifted. (CNBC, Bloomberg.)",

        "<strong>The Burry tell is inside the IPO.</strong> SK Hynix's debut is a bet AI breaks the boom-and-bust chip "
        "cycle &mdash; it FUNDS a capacity race (Hynix, Samsung, Micron all adding HBM). The more capital the AI "
        "narrative pulls in at the top, the more violently the eventual memory glut resolves. The book is long exactly "
        "that. (Bloomberg.)",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "Soft CPI + Hormuz de-escalation — the melt-up broadens and the AI bid keeps winning",
         "body": "June CPI comes in soft (core at/below +0.3%), the Oman-brokered Hormuz proposal holds and oil drains "
                 "back toward $70, and the disarmed-hike story revives: September-hike odds fall, the 2Y rallies back "
                 "through 4.10% (MM-013 re-confirms), the curve steepens toward +50bp (MM-009), gold gets its "
                 "real-rates relief (MM-005 rescued at the min-hold), and the SK Hynix-led AI tape broadens. The euro "
                 "short (MM-012) is trimmed as the dollar rolls again. Risk up · rates down (front) · dollar soft · "
                 "gold up · oil soft."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "A boxed-in Fed and a two-front cost-push — steep curve, firm oil, range-bound risk",
         "body": "Core CPI holds ~2.9% and the $76-Brent premium keeps goods sticky while the labour crack caps the "
                 "hike; Warsh's Fed holds a hawkish hold it can neither justify nor execute. The 2Y ranges ~4.15-4.25%, "
                 "the curve stays steep (MM-009 the winner), oil holds a war premium (MM-040/TotalEnergies), gold "
                 "chops below $4,200, and the dollar base-builds at 101 (MM-012 holds). Equities chop near the record "
                 "as CPI and bank earnings cap risk appetite. Risk mixed · rates steady · dollar firm · oil firm · "
                 "curve steep."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "A hot CPI or a Hormuz shock breaks the melt-up — the oil cost-push re-arms the hawk",
         "body": "Either a hot core CPI plus $76+ Brent re-arms a near-term hike, backs the 2Y toward the 4.35% stop "
                 "(risk to MM-013), bear-flattens the front and sells the AI-concentrated index (MM-041 pays); or Iran "
                 "closes Hormuz, oil spikes through $90 (MM-040 pays hard), and the growth scare hits the melt-up. "
                 "Either way VIX 15 was the wrong price and the S&amp;P retraces toward 7,400 where the put spread "
                 "works. Risk down · rates two-way · dollar bid · oil up · gold two-way (haven vs real-rate)."},
    ],

    "insights_layers": """
<p>The dominant driver this week is an AI-capex bid that has become an all-weather force. SK Hynix's $26.5bn Nasdaq
debut &mdash; the biggest foreign IPO in US history, +13% on day one &mdash; re-lit the memory/accelerator complex and
carried US equities to a winning week through a Gulf war that would ordinarily have bid havens and sunk risk. The
non-consensus read is that this is not broad resilience: it is one trade doing all the work while a real supply premium
rebuilds in crude, and the market has priced the war OUT of everything except oil.</p>

<p>The counter-intuitive hook is the inverted haven trade. A ceasefire collapsed into an 80-target US strike, Iran
attacked ships in Hormuz, and the Treasury revoked Iran's oil-sale waiver &mdash; and gold FELL, bonds SOLD, and the
dollar barely moved. Consensus expected a war to bid gold and duration; instead the oil spike acted as a cost-push,
lifting inflation expectations and real yields, which is bearish both. The market took the equity melt-up as the signal;
the cross-asset tape says the signal is inflation, and it is the inflation read that CPI decides on Tuesday.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong> Brent
~$76 (+5% on the week) on a live Hormuz blockade, the 10Y at 4.56%, core PCE near 3%, a Fed leaning 9-of-18 toward a
hike, a $26.5bn memory IPO funding a capacity race. <strong>What is priced:</strong> VIX at 15, a near-record S&amp;P, a
2s10s at +35bp, ~74.9% odds the Fed holds in July, a benign CPI assumed. <strong>Consensus narrative:</strong> &lsquo;AI
is all-weather, the war is contained, the print will be soft, buy the melt-up.&rsquo; The gap &mdash; and the alpha
&mdash; is that the tape is pricing AI durability and a benign CPI at the same time while a real war premium and an oil
cost-push argue the opposite.</p>

<p>Go around the world. <strong>US:</strong> a winning week on the SK Hynix-led AI bid, the Dow off its Jul 2 record but
resilient. <strong>Korea/Asia:</strong> the IPO is a Korean-champion event that re-rates the KOSPI memory complex, but
the Nikkei fell 1.70% on the week and Asia broadly lagged on the Gulf strikes and a firmer yen. <strong>Europe:</strong>
the DAX dropped 2.76% on the week (a Friday +0.78% bounce), the biggest laggard as the war and a $76 Brent hit an
energy-importing bloc &mdash; though the Jul 4 EU tariff tail lifted benignly. <strong>Middle East:</strong> the war is
live; weekend Oman-brokered talks on a two-route Hormuz proposal are the only de-escalation path, and US officials say
talks can't progress until ships get safe passage.</p>

<p>The political angle runs on two constraints. The Papic read on the war: Trump owns the &lsquo;ceasefire is
over&rsquo; declaration, so de-escalation is politically expensive for him, and he opened a second tariff front (a 35%
Canada tariff, Aug 1) the same week &mdash; the cost-push agenda is a feature, not a bug. The second constraint is the
Fed: a war-driven oil spike is a cost-push that boxes a central bank already leaning toward a hike &mdash; it cannot cut
into an oil-CPI and cannot hike hard into a labour crack. The non-consensus read is that the market's assumption of a
soft CPI and a contained war is a single bet wearing two hats, and Tuesday tests both.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the Hormuz war premium in crude (the Brent call spread, MM-040,
and the book's TotalEnergies); the two-sided CPI at VIX 15 (the SPX put spread, MM-041); the hot-core dollar tail (the
EUR/USD put spread, MM-042). <strong>Fairly priced:</strong> the steeper curve (MM-009); the bank cohort's NIM tailwind
(GS earnings vol, MM-043). <strong>Fully priced:</strong> AI-memory durability as all-weather (the SK Hynix halo).
<strong>Over-priced (at risk):</strong> a benign CPI and a contained war both assumed at once by a tape short volatility
at 15.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this week is that a winning week during a Gulf war is not resilience
&mdash; it is one trade doing all the work while the war hides in plain sight in the oil price. A ceasefire collapsed
into a shooting war: Trump called the truce over from a NATO stage, the US bombed more than eighty Iranian targets after
Tehran attacked ships in the Strait of Hormuz, and the Treasury pulled Iran's licence to sell oil. The tape&rsquo;s
answer was to buy the biggest foreign IPO in American history &mdash; SK Hynix, twenty-six and a half billion dollars
raised, up thirteen percent on its first day &mdash; and close the week higher with the volatility index at fifteen. The
market decided a Korean memory listing was the more important event than a war, and on the week&rsquo;s price action it
was right. The question is whether it stays right through Tuesday.</p>

<p>Decompose it, because the composition is the whole story. Strip out the AI-memory bid and the week was a war: oil up
five percent on a real Hormuz premium, gold down, bonds down, the ten-year backed up to four-and-a-half. Those are not
the prints of a market pricing safety &mdash; they are the prints of a market pricing inflation. The haven trade
inverted because an oil shock is a cost-push, not a flight to quality: it lifts breakevens and real yields, and that
sinks both gold and duration. So what, who is wrong, what is the trade: the consensus reading a firm equity tape as
all-clear is wrong at the level of the cross-asset tape, and the trade is to own the thing the equity market priced out
&mdash; the war premium in crude &mdash; and to hedge the thing it priced in, a benign inflation print.</p>

<p>Trace it to a flow, because the durable move is in oil and rates, not the equity headline. The Treasury revoking
Iran&rsquo;s oil waiver is not a headline, it is a supply withdrawal: barrels that were clearing the market under a
sanctions exemption are now blocked, into a Strait where tankers are already being attacked. That is a physical squeeze
on the marginal barrel, and it lands on a Treasury market with a heavy supply calendar and a term premium that will not
fall. The ten-year did not back up on growth &mdash; it backed up because an oil cost-push plus fiscal supply is exactly
the combination that keeps the long end heavy while the front is pinned by a boxed-in Fed. That is why the curve
steepener is the one rate trade that worked through the week, and why buying duration outright fought the tape.</p>

<p>The Burry tell is inside the IPO everyone cheered. SK Hynix&rsquo;s debut was described, by Bloomberg&rsquo;s own
headline, as a bet that AI breaks the boom-and-bust chip cycle. Read that as a warning, not a boast. Memory is a
commodity; its cycle has never been broken, only postponed. A twenty-six-billion-dollar equity raise at the top of an
AI-capex wave is capital that funds capacity &mdash; Hynix, Samsung and Micron all racing to add high-bandwidth memory
&mdash; and capacity added into a demand assumption is how every glut in the history of the industry has been built. The
more the narrative insists the cycle is dead, the more capital it pulls in, and the more violent the eventual
correction. The book is thirty percent Micron. It is long the single best expression of that bet, and the discipline is
to monetise the elevated volatility into the top, not to add into it.</p>

<p>So the posture into a two-sided Tuesday is to own the war the tape ignored and hedge the print the tape assumes. The
energy length is the accidental war hedge that is already working, and the upside is pressed with a defined-risk Brent
call spread rather than chased in spot. The index is hedged into the CPI collision with a put spread bought while
volatility is cheap at fifteen. The hot-core dollar tail is owned with a euro put spread as the dollar base-builds at a
hundred-and-one. And the bank cohort that reports into a steeper curve is pressed through its highest-beta name. The
tape decided one AI trade can absorb a shooting war. The brief&rsquo;s read is that it cannot also absorb an oil-driven
inflation scare &mdash; and Tuesday is where it finds out.</p>
""",

    "correlation_regime": """
<p><strong>1. Equities decoupled from the war &mdash; the biggest break on the board.</strong> A ceasefire collapse,
an 80-target US strike, and a Hormuz blockade would normally sink risk and bid havens; instead the S&amp;P booked a
winning week and VIX fell to 15. The dominant equity driver is no longer geopolitics &mdash; it is the AI-capex bid, and
SK Hynix's record IPO overrode a shooting war. The break says the melt-up will price almost anything except a threat to
the AI story itself; the trade is to own the war premium where it DID land (crude, MM-040) rather than fight the equity
tape.</p>

<p><strong>2. Gold decoupled from geopolitics &mdash; and re-coupled to real rates.</strong> Gold FELL through a week of
US-Iran strikes, the opposite of the textbook haven response, because yields backed up (10Y 4.56%) on the oil cost-push
and gold traded as a real-rates short. The driver switched from 'war premium' to 'real-rate headwind,' which is why the
book's gold long (MM-005) is underwater despite the conflict. Gold is a CPI trade now, not a Hormuz trade &mdash; it
needs Tuesday's print soft, not the war hot.</p>

<p><strong>3. Oil decoupled from equities.</strong> Crude priced a real supply shock (+5% on the week) while equities
priced none of it. Front and back of the risk complex are now driven by different forces: oil by a physical Hormuz
squeeze and a sanctions withdrawal, equities by an AI-memory bid. A gap this wide means one of them is wrong &mdash; and
the physical barrel is harder to argue with than a narrative. Own the crude premium (MM-040); hedge the complacent index
(MM-041).</p>

<p><strong>4. The curve decoupled from the level.</strong> Both the 2Y and 10Y backed up on the week, but the 2s10s held
~+35bp &mdash; the front pinned by a boxed-in Fed, the back heavy on the oil cost-push and supply. A steepener that
survives a week of rising yields is a structural signal: the dominant rates driver is the bind, not the direction. Own
the shape (MM-009), not outright duration (why MM-004 lags).</p>
""",

    "vol_skew": """
<p><strong>The cheapest convexity on the board is an index hedge into a two-sided CPI on a tape that priced a shooting
war as nothing.</strong> VIX closed 15.03 (−5.11%), the term structure in contango (est. VIX9D ~14.0 · VIX ~15.0 ·
VIX3M ~17.5 · VIX6M ~18.5), and MOVE firmed toward ~105 as the oil-led yield backup lifted rates vol. The tape is
pricing AI durability and a benign June CPI at the same time, with a fresh $76-Brent cost-push in the pipeline and a
live Hormuz war &mdash; precisely when below-spot convexity is cheap. The headline trade implication: a July SPX
7,400/7,150 put spread (MM-041), defined-risk downside into the CPI + war-headline collision. The FX complement is a
1-week EUR/USD 1.135/1.115 put spread (MM-042) &mdash; own the hot-core dollar tail as the dollar base-builds at 101.
And the commodity leg is a long-gamma Brent $78/$88 call spread (MM-040) that owns the Hormuz escalation the equity tape
refuses to price. Rates vol (MOVE ~105) is the one part of the surface that is NOT cheap &mdash; the market already sees
the CPI risk in bonds even as it ignores it in stocks. If nothing sticks, the equity and FX spreads decay cheaply; if
the print runs hot or Hormuz re-escalates over the weekend, the convexity is owned, not chased.</p>
""",

    "sector_rv": """
<p><strong>Leading (week to Fri Jul 10):</strong> AI/semis and memory &mdash; the SK Hynix debut re-lit the complex and
carried US indices to a winning week; energy on the Hormuz premium (WTI +3.5%, Brent +5% wk). Financials firmed into the
Q2 earnings kickoff on a steeper curve. <strong>Lagging:</strong> European equities (DAX −2.76% wk) as the war and a $76
Brent hit an energy importer; gold miners and bullion on the real-rates backup; duration-sensitive defensives as the 10Y
backed up. <strong>This week:</strong> June CPI Tue (the two-sided decider); big-bank earnings Tue-Wed (JPM, GS, C, BAC,
WFC → MS, BLK, BNY); the Hormuz diplomacy over safe-passage.</p>

<p><strong>RV:</strong> Two fit today's tape. First, the chip dispersion: long NVDA (~32x on $81.6B Q1 revenue) vs the
overbought ~175x AMD &mdash; the SK Hynix halo lifts the whole cohort, but the valuation gap closes on the leader, and
it doubles as book housekeeping (trim the exhausted AMD winner). Second, the bank RV: long GS (highest-beta to the IB
re-acceleration, ~6% implied move, split sell-side, MM-043) against the lower-beta NIM-only names &mdash; own the
earnings vol where consensus is most divided, not the well-owned bellwether. Both are low beta to the index and high
beta to the week's live catalysts &mdash; the AI capacity race and the bank-earnings kickoff.</p>
""",

    "positioning": """
<p><strong>The crowd is long the AI melt-up, short volatility at 15, and leaning dovish/short-dollar into a CPI that
could re-arm the hawk.</strong> The loudest lean is complacency: a winning week through a shooting war with VIX at 15 is
a market that has decided nothing except an AI threat can hurt it, so the pain trade is a two-sided CPI or a Hormuz shock
that the index has priced out (why MM-041 is the hedge). In FX, the market faded the dollar after the Jul 2 payroll, so
a hot core plus a $76-oil cost-push is the pain trade that re-bids it (MM-042; MM-012 back to working). In rates, fast
money swung back toward hawkish on the oil re-arm, so the squeeze is now two-way &mdash; which is exactly why the
consensus-agnostic steepener (MM-009) is the cleaner expression than the directional front-end fade (MM-013). In
commodities, spec crude length is LIGHT after the June ceasefire drained the premium, leaving the barrel squeeze-prone
on escalation (MM-040). In gold, spec length was washed out; positioning is clean but there is no squeeze without a rate
turn (MM-005 needs a soft CPI). The pain trade everywhere is the same &mdash; a market that has decided one AI trade
makes it immune to a war and a print.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; the war and the oil spike produced no stress in the plumbing, and the disarmed/
re-armed hike debate does not move the funding rate. <strong>The Pozsar mechanic:</strong> trace the rates backup to a
flow, not a narrative. The Treasury revoking Iran's oil-sale waiver is a supply withdrawal &mdash; barrels that cleared
the market under a sanctions exemption are now blocked, into a Strait where tankers are being attacked. That is a
physical squeeze on the marginal barrel, and it transmits into the Treasury market as a term-premium/inflation impulse:
the 10Y backed up to 4.56% not on growth but because an oil cost-push plus a heavy fiscal-supply calendar is the
combination that keeps the long end heavy while a boxed-in Fed pins the front. That is the whole steepener (MM-009).
Underneath, the durable real-economy flow is the AI-capex machine that SK Hynix's $26.5bn raise just refuelled &mdash;
hyperscaler and memory capex, increasingly debt- and equity-funded, still bidding the supply chain and keeping core
goods sticky, which is the sticky-inflation half the CPI print will test. The funding angle that matters next is the
collision of a heavy IG issuance calendar (2026 high-grade supply ~$2.25tn, +35% y/y on AI capex) with a long end that
backed up on the oil premium &mdash; watch IG issuance and the 10Y together into CPI: the back end is where the
supply-plus-cost-push flow shows up, and it is why the curve, not duration, is the trade.</p>
""",

    "tape_missing": """
<p><strong>The equity tape priced a shooting war as nothing &mdash; the oil market did not.</strong> The S&amp;P booked
a winning week and VIX fell to 15 through an 80-target US strike, a Hormuz blockade, and a sanctions withdrawal, while
Brent priced +5%. The falsifiable level: Brent through $85 on a Hormuz closure says the equity market's complacency was
mispriced and the SPX put spread (MM-041) and Brent call spread (MM-040) both pay; Brent back below $70 on a clean
Oman-brokered de-escalation says the tape was right to look through it. Watch the Strait's safe-passage talks and the
Brent price together.</p>

<p><strong>Just behind it: the market faded the dollar and the hike into a two-sided CPI.</strong> After the Jul 2
payroll disarmed the September hike, positioning leaned dovish/short-dollar &mdash; but the 10Y backed up to 4.56% and
the dollar base-built at 101 on the oil cost-push. The falsifiable line: a core CPI at or above +0.4% m/m with $76 Brent
re-arms the hike, backs the 2Y toward 4.35% (MM-013 risk) and bids the dollar (MM-042 pays); a core at or below +0.2%
revives the disinflation read and the dollar roll. Tuesday's core print is the test.</p>

<p><strong>The Burry tell &mdash; the capacity race inside the record IPO.</strong> Everyone cheered SK Hynix's $26.5bn
debut; the structural signal is what it funds. A record equity raise at the top of an AI-capex wave is capital deployed
into capacity &mdash; Hynix, Samsung and Micron all adding high-bandwidth memory into a demand assumption &mdash; and
memory is a commodity whose cycle has never been broken, only postponed. Over the next two-to-three quarters this
resolves one of two ways: AI demand keeps outrunning the new supply and the 'broken cycle' thesis holds a while longer;
or the capacity lands ahead of demand and memory prices roll, taking the most levered names down first. The Fable book is
30% Micron &mdash; the single best expression of the bet that the cycle is dead &mdash; and the discipline is to
monetise the elevated volatility into the top, not add into it.</p>
""",

    "book_outlook": {
        "commentary": (
            "This week split the book cleanly along the war-versus-rates seam, and the split is the story. The winner is "
            "the one nobody would call a hedge: <b>TotalEnergies</b>, the book's energy length, is the position that "
            "led as the US-Iran ceasefire collapsed into an 80-target strike and Brent ran +5% to ~$76 on the Hormuz "
            "premium &mdash; the war hedge the equity tape refused to build, sitting in the book already. On the AI "
            "side, <b>Micron</b> (largest weight, ~30%) got a direct re-rating by proxy: SK Hynix's $26.5bn record "
            "Nasdaq debut (the biggest foreign US IPO ever, +13% day one) validated the HBM/AI-memory supercycle Micron "
            "is levered to, and pulled the whole sleeve &mdash; <b>NVDA</b> (−10.5%), <b>AVGO</b> (−21.3%), <b>AMD</b> "
            "(+394%) &mdash; up with it. But the Bloomberg frame, 'a bet AI breaks the boom-and-bust chip cycle,' is the "
            "two-sided tell: the IPO funds a capacity race that resolves the cycle badly later, and the book is long "
            "exactly that. The losers are the assets that should have worked in a war and didn't: <b>Xetra-Gold "
            "(4GLD)</b> FELL as yields backed up &mdash; the tail hedge inverted, because the oil spike is a cost-push, "
            "not a haven bid &mdash; and the bond sleeve (<b>UST 1.25% 2031</b>, <b>Siemens EUR IG</b>) got hurt as the "
            "10Y backed up to 4.56%. On the currency, the book's ~72% USD sleeve stabilised: the dollar base-built at "
            "101, so the FX translation is roughly neutral again after the Jul 3 headwind. And the July 4 tail on "
            "<b>LVMH</b> and <b>SAP</b> LIFTED &mdash; the EU deal passed benignly; the new 35% Canada tariff (Aug 1) "
            "doesn't touch them. The dominant action: recognise the energy length is the working war hedge and press "
            "the upside with defined risk, not spot; monetise Micron's elevated IVol into the SK Hynix capacity-race "
            "top rather than adding; do NOT add duration into a hot-CPI risk; and treat 4GLD as a rate trade needing a "
            "soft CPI, not a war trade."
        ),
        "outperform": [
            {"name": "TotalEnergies (TTE, +54.8%) — the accidental war hedge that worked", "why": "The ceasefire "
             "collapsed into an 80-target US strike and Brent ran +5% to ~$76 on the Hormuz premium &mdash; the book's "
             "energy length is the war hedge the equity tape refused to build, and it led the book this week (mirrors "
             "the desk's Brent call spread MM-040)."},
            {"name": "Micron (MU, ~30%, +1082%) — the SK Hynix halo", "why": "SK Hynix's $26.5bn record Nasdaq debut "
             "(+13% day one) validated the HBM/AI-memory supercycle Micron is levered to and re-rated the whole memory "
             "complex. The book's largest weight caught the direct read-across &mdash; but it is the trim/overwrite "
             "candidate into the capacity-race top, not an add."},
            {"name": "The USD sleeve (~72% of the book) — translation stabilised", "why": "The dollar base-built at 101 "
             "(DXY ~100.97) as the oil-led yield backup rebuilt the rate-differential bid, so the FX translation on the "
             "book's US assets is roughly neutral again after the Jul 3 headwind (mirrors the desk's MM-012 back to "
             "working)."},
        ],
        "underperform": [
            {"name": "Xetra-Gold (4GLD, +108.6%) — the tail hedge that inverted", "why": "Gold FELL through a week of "
             "US-Iran strikes because the oil spike backed up real yields (10Y 4.56%) and gold traded as a real-rates "
             "short, not a haven. The hedge you'd expect to fire in a war did the opposite &mdash; it is a CPI trade "
             "now, needing Tuesday's print soft (mirrors MM-005 underwater on its min-hold)."},
            {"name": "The bond sleeve (UST 1.25% 2031, Siemens EUR IG) — the yield backup", "why": "The 10Y backed up "
             "to ~4.56% on the oil cost-push and supply, marking both underwater bonds lower &mdash; the war produced "
             "no duration bid. Do NOT add duration into a hot-CPI risk (mirrors the short-10Y MM-004 lagging); the "
             "curve, not the long end, is where the rate value is."},
            {"name": "AMD (+394%) — the trim candidate into the capacity race", "why": "AMD caught the SK Hynix halo "
             "but at ~175x vs NVDA's ~32x it is the overbought leg the next chip selloff targets first, on a tape the "
             "record IPO just pulled fresh memory supply into. It 'outperforms' today only as the sell-into-strength "
             "leg of the NVDA/AMD dispersion &mdash; concentration management, not conviction."},
        ],
        "watch": [
            {"label": "Press the energy length with defined risk — the war premium is a cheap option, not a spot chase",
             "text": "TotalEnergies is the working war hedge, but a real Hormuz disruption is a binary the book should "
             "own convexly, not by adding spot crude exposure into a two-way headline tape. Press the upside with a "
             "defined-risk Brent call spread (the desk's MM-040) &mdash; own the escalation tail cheaply while the "
             "weekend Oman-brokered talks could still drain the premium."},
            {"label": "Monetise Micron's IVol into the SK Hynix capacity-race top — don't add",
             "text": "The record IPO re-rated Micron and lifted its option premium; the Burry tell is that the raise "
             "funds a capacity race (Hynix, Samsung, Micron all adding HBM) that resolves the cycle badly later. The "
             "book is 30% Micron &mdash; the single best expression of that bet. Sell the elevated volatility into the "
             "top with a collar or covered-call overwrite rather than adding to a name at a record."},
            {"label": "Don't add duration before CPI — the bond sleeve is the Tuesday risk",
             "text": "The UST 2031 and Siemens IG got hurt as the 10Y backed up to 4.56% on the oil cost-push. June CPI "
             "Tue (core +0.3% m/m cons) plus a $76-Brent premium is a two-sided risk that can back the long end up "
             "further. Hold the sleeve but do NOT average down into the print; own the rate value via the curve "
             "steepener (the desk's MM-009), and carry the hot-core dollar tail via the EUR/USD put spread (MM-042)."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> the AI-capex bid is all-weather &mdash; SK Hynix's record IPO proves it, the war is
contained to oil, June CPI will print soft, and the Fed steps back. Buy the melt-up; the winning week through a shooting
war is the proof of resilience, and the Hormuz flare-up will de-escalate like every one before it.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> 'all-weather resilience' misreads a week that was
one trade doing all the work. Strip out the AI-memory bid and the tape was a war: oil +5%, gold down, bonds down, the
10Y at 4.56%. The haven trade inverted because an oil shock is a cost-push, not safety &mdash; and that cost-push, plus
$76 Brent and a Fed leaning 9-of-18 toward a hike, is exactly what a hot June CPI (Tue) re-arms. The crowded side is long
AI durability and short volatility at 15; the cheaper side owns the war premium (MM-040), the CPI hedge (MM-041), and the
hot-core dollar tail (MM-042) into a print and a Hormuz binary the melt-up has priced out.</p>
""",

    "one_chart": """
<p class="theme">Brent crude at ~$76 against a VIX at 15 is the chart &mdash; the oil market pricing a war the equity market says isn't there.</p>
<p>The single thing the market should watch is the gap between crude and equity volatility. Brent priced the Hormuz war
+5% on the week to ~$76 while the S&amp;P booked a winning week and VIX fell to 15 &mdash; two markets looking at the
same shooting war and disagreeing completely. That gap resolves one of two ways, and the level that decides it is Brent
through $85: a Hormuz closure or a failed Oman-brokered safe-passage deal takes crude toward $90, drags breakevens and
the 10Y up, and forces the equity tape to finally price the war (the SPX put spread MM-041 and the Brent call spread
MM-040 both pay); a clean de-escalation drops Brent back below $70, vindicates the melt-up's complacency, and hands gold
(MM-005) its real-rates relief. Own the crude premium and the index hedge while the Strait's safe-passage talks are
unresolved and Brent holds its war bid; the June CPI print Tuesday is the accelerant that decides whether the oil
cost-push becomes an inflation scare.</p>
""",

    "catalyst_calendar": [
        {"day": "Wed-Thu", "date": "Jul 8-9 ✓",
         "event": "US strikes Iran — the ceasefire collapses",
         "consensus": "After Trump declared the ceasefire 'over' at the NATO summit, the US struck 80+ Iranian targets "
                      "(Jul 8, after Iran attacked ships in Hormuz) and 60+ IRGC boats (Jul 9); the Treasury revoked "
                      "Iran's oil-sale waiver. Brent jumped 5.2% to $78. Sources: Al Jazeera, NBC, CNBC, Bloomberg.",
         "view": ("The war repriced OIL, not equities, and inverted the haven trade &mdash; gold fell, bonds sold. A "
                  "cost-push, not a flight to safety. The premium the Jul 3 tape drained is back."),
         "asymmetry": "Own the crude premium the equity tape priced out (MM-040, TotalEnergies); the Hormuz-closure "
                      "tail is the upside the melt-up is ignoring at VIX 15.",
         "dir": "up"},
        {"day": "Fri", "date": "Jul 10 ✓",
         "event": "SK Hynix IPO — the biggest foreign US listing ever",
         "consensus": "SK Hynix (SKHY) debuted on Nasdaq: $26.5bn raised at $149/ADS, past Alibaba 2014 as the largest "
                      "foreign IPO in US history, +13% on day one. Framed as a bet AI breaks the boom-and-bust chip "
                      "cycle; the S&P closed the week +>1%. Sources: Bloomberg, TechCrunch, Yahoo Finance.",
         "view": "The AI-memory bid that carried a winning week through a war &mdash; and the capacity-race tell "
                 "underneath it. A direct re-rating of the book's 30% Micron weight.",
         "asymmetry": "The halo lifts the cohort, but the valuation gap closes on the leader &mdash; long NVDA (~32x) "
                      "vs overbought AMD (~175x); monetise Micron's IVol into the top rather than chase.",
         "dir": "up"},
        {"day": "Sat", "date": "Jul 11 — TODAY",
         "event": "Weekend Hormuz diplomacy — Oman's two-route proposal",
         "consensus": "Iran's FM Araghchi met his Omani counterpart; Oman is drafting a tentative proposal to manage "
                      "Hormuz traffic through two separately controlled routes. US officials say talks can't progress "
                      "until ships are assured safe passage; Trump warns of further strikes on fresh attacks. Sources: "
                      "CNN, RFE/RL.",
         "view": "The only de-escalation path, and the swing factor for the oil premium. A safe-passage deal drains "
                 "Brent; a breakdown or a fresh tanker attack spikes it at the Monday reopen.",
         "asymmetry": "A breakdown gaps oil higher (MM-040 pays) and risk lower (MM-041); a deal drains the premium and "
                      "hands gold its real-rates relief (MM-005).",
         "dir": "flat"},
        {"day": "Mon", "date": "Jul 13",
         "event": "Reopen — the weekend Hormuz outcome gets priced",
         "consensus": "US markets reopen and price the weekend Iran/Hormuz diplomacy and the run-up into CPI and bank "
                      "earnings. Brent's war premium and the VIX-15 complacency are the two things repriced first. "
                      "Source: market calendar.",
         "view": "The setup session into the week's real catalysts; whether the oil premium holds and whether the tape "
                 "starts to price the CPI risk it ignored all week.",
         "asymmetry": "A held oil premium into CPI keeps MM-040/041 live; a de-escalation gap lets the melt-up run into "
                      "the print and revives the gold trade (MM-005).",
         "dir": "flat"},
        {"day": "Tue", "date": "Jul 14",
         "event": "June CPI (08:30 ET) + big-bank Q2 earnings (BMO)",
         "consensus": "June CPI consensus: headline −0.1% m/m (~3.9% y/y), core +0.3% m/m (~2.9% y/y). Same morning: "
                      "JPM (~$5.74 EPS), GS (~$14.46, implied move ~6%), C (~$2.76), BAC (~$1.13), WFC (~$1.73) report "
                      "BMO. Sources: BLS, Kiplinger, Finnhub, Zacks.",
         "view": "The collision. A two-sided CPI with a $76-Brent cost-push in the pipeline meets the bank cohort "
                 "reporting into a steeper curve. The single day that resolves the disinflation-vs-cost-push regime.",
         "asymmetry": "A hot core re-arms the hike, backs the 2Y toward 4.35% (MM-013 risk), bids the dollar (MM-042) "
                      "and pays the index hedge (MM-041); a soft core revives the melt-up and gold (MM-005). GS is the "
                      "highest-beta bank print (MM-043).",
         "dir": "down"},
        {"day": "Wed", "date": "Jul 15",
         "event": "Bank earnings wave 2 (MS, BLK, BNY) + CPI follow-through",
         "consensus": "Morgan Stanley, BlackRock and BNY Mellon report BMO, extending the Financials read into wealth/"
                      "asset management and custody. The market digests the CPI print and the first-day bank reactions. "
                      "Sources: Finnhub.",
         "view": "The confirmation session: whether the bank cohort's NIM/IB tailwind holds beyond the money-centre "
                 "names and whether the CPI reaction sticks.",
         "asymmetry": "A clean bank-cohort read plus a benign CPI extends the financials/broadening trade; a hot CPI "
                      "swamps even good prints and the whole tape de-risks.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.662 (the stop). Near entry &mdash; flat, pinned mid-range as the AI-led risk-on keeps an AUD bid; edge thinned, stop close. Trim into strength; tight leash.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.56% &mdash; the LAGGARD; the oil cost-push backed the 10Y UP and the war gave no haven bid. Expressed better via the curve (MM-009). A break below 4.40% on a soft CPI is the confirmation; ~9bp from the stop &mdash; a tight rein into the print.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250. At ~$4,103 &mdash; the war did NOT save it; yields backed up and gold traded as a real-rates short. Needs a soft CPI Tue, not a Hormuz headline. Decision at the min-hold; a hot CPI forces the exit.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~161.6 &mdash; offside (~-1.4%) as the oil-led yield backup re-widened the differential; the yen firmed Friday on Japan pension-domestic-asset chatter. CPI is the swing. Tight leash.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+35bp; ~+130%; target +60bp. The one expression the war didn't break &mdash; the spread held through a week of backing-up yields. Trail the stop; hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182 (distant). At ~1.1415 &mdash; BACK TO WORKING; the dollar base-built at 101 and $76 Brent hit the euro's terms of trade. Hold the core short; own the hot-CPI tail via MM-042. A soft CPI that revives the dollar roll is the trim signal.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold elapsed. At ~4.21% &mdash; gave back edge as the oil cost-push re-priced near-term hike risk. CPI Tue is the decider; the curve (MM-009) is the higher-conviction sibling. A hot core toward the 4.35% stop is the risk.</li>
</ul>
""",

    "client_ammo": [
        {"q": "There was a US-Iran war this week and the market went UP — how?",
         "a": ("Because one trade did all the work: SK Hynix's twenty-six-and-a-half-billion-dollar IPO, the biggest "
               "foreign listing in US history, re-lit the AI-memory bid and carried a winning week. But the war didn't "
               "disappear &mdash; it repriced OIL. Brent is up five percent on the week, and tellingly gold FELL and "
               "bonds sold, which is the opposite of a normal war reaction. The market priced the conflict out of "
               "everything except crude, and that's the gap we're trading.")},
        {"q": "Why did gold fall during a war? Isn't it a safe haven?",
         "a": ("Normally, yes &mdash; but this war came through the oil price, and an oil spike is a cost-push, not a "
               "flight to safety. Higher oil lifts inflation expectations and real yields, and gold hates rising real "
               "yields. The ten-year backed up to four-point-five-six, and gold traded as a rate bet, not a haven. "
               "That's why your Xetra-Gold position lagged: gold needs a soft inflation print Tuesday, not a Hormuz "
               "headline, to work from here.")},
        {"q": "The SK Hynix IPO was huge — is that good for our Micron position?",
         "a": ("On the surface, very &mdash; it validated the exact AI-memory supercycle Micron is levered to, and the "
               "whole complex re-rated. But read Bloomberg's own framing: it's a bet that AI 'breaks the boom-and-bust "
               "chip cycle.' That raise funds a capacity race &mdash; Hynix, Samsung and Micron all adding memory "
               "&mdash; and memory is a commodity whose cycle has never actually broken. You're thirty percent Micron, "
               "so we'd monetise the elevated option premium into this top with a collar rather than add into it.")},
        {"q": "What's the one thing to watch this week?",
         "a": ("Tuesday. June CPI lands at eight-thirty with a hot-oil backdrop, and the big banks report the same "
               "morning. The market is priced for a soft print and short volatility at fifteen &mdash; if core comes "
               "in hot with Brent at seventy-six, it re-arms the rate hike everyone thought was dead and the "
               "complacent tape has to reprice. We own that risk cheaply with a small index put spread and a euro put "
               "spread.")},
        {"q": "Is the energy position finally helping?",
         "a": ("Yes &mdash; TotalEnergies is the standout this week and the accidental war hedge the rest of the "
               "market refused to build. The Hormuz blockade and the strikes put a real supply premium back in crude, "
               "and your energy length captured it. We'd press the upside with a defined-risk Brent call spread rather "
               "than adding spot, because the weekend Oman-brokered talks could still drain the premium overnight.")},
        {"q": "Where's the cleanest new money going?",
         "a": ("Into the war the equity tape priced out and the print it's ignoring. The clearest is owning the oil "
               "premium with a Brent call spread, then hedging the index into Tuesday's CPI with a put spread while "
               "volatility is cheap at fifteen. On the rate book, the yield-curve steepener is still the cleanest "
               "expression &mdash; it held through a week of rising yields &mdash; and into bank earnings, Goldman is "
               "the highest-beta name with the widest implied move.")},
    ],

    "ideas_note": (
        "<p>The split between a war the equity tape priced out and a CPI it assumes benign sets every idea today. "
        "<strong>Brent call spread (MM-040)</strong> &mdash; the marquee: the ceasefire collapsed into an 80-target "
        "strike and a Hormuz blockade, the Treasury pulled Iran's oil waiver, and crude repriced +5% while equities "
        "booked a winning week; own the escalation tail with defined risk. <strong>SPX put spread (MM-041)</strong> "
        "&mdash; the index hedge into a two-sided June CPI (Tue) on a tape short volatility at 15, structured for the "
        "CPI + Hormuz collision. <strong>EUR/USD put spread (MM-042)</strong> &mdash; own the hot-core dollar tail as "
        "the dollar base-builds at 101 and a $76 Brent hits the euro's terms of trade. <strong>GS earnings vol "
        "(MM-043)</strong> &mdash; the bank cohort reports into a steeper curve; Goldman carries the widest implied "
        "move (~6%) and the most divided sell-side, so an IB beat has the most room to re-rate. The rate winner "
        "(MM-009) is held and trailed; the euro short (MM-012) is back to working; gold (MM-005) is held on its "
        "min-hold as a CPI trade, not a war trade.</p>"
    ),

    "event_radar_note": (
        "<p>Chips over cannons: a literal ceasefire collapsed into a shooting war &mdash; Trump called the truce 'over' "
        "(~Jul 7), the US struck 80+ Iranian targets (Jul 8) and 60+ IRGC boats (Jul 9), and the Treasury revoked "
        "Iran's oil waiver &mdash; and the tape chose the chips. SK Hynix's $26.5bn Nasdaq debut (Jul 10), the biggest "
        "foreign US IPO ever, re-lit the AI-memory trade; the S&P booked a winning week to 7,575.39 and VIX fell to 15. "
        "But the war repriced OIL (Brent ~$76, +5% wk), gold FELL and bonds SOLD (10Y ~4.56%) &mdash; the haven trade "
        "inverted on the cost-push. The steepener (MM-009) is the rate winner; the short-10Y (MM-004) and short-2Y "
        "(MM-013) lagged; gold (MM-005) is underwater on its min-hold. US markets are CLOSED today (Sat Jul 11); the "
        "weekend Oman-brokered Hormuz talks are live; June CPI Tue Jul 14 and the big-bank earnings kickoff are the "
        "deciders. Fresh ideas own the split: a Brent call spread, an SPX put spread into CPI, a EUR/USD put spread, "
        "and GS earnings vol.</p>"
    ),

    "burry_tell": (
        "Everyone cheered SK Hynix's $26.5bn record IPO; the structural signal is what it funds. A record equity raise "
        "at the top of an AI-capex wave &mdash; the biggest foreign listing in US history, framed by Bloomberg as a bet "
        "that AI breaks the boom-and-bust chip cycle &mdash; is capital deployed into capacity. Hynix, Samsung and "
        "Micron are all racing to add high-bandwidth memory into the same demand assumption, and memory is a commodity "
        "whose cycle has never actually been broken, only postponed. The thing nobody is pricing is that the louder the "
        "narrative insists the cycle is dead, the more capital it pulls in at the top, and the more violent the "
        "eventual correction: capacity added ahead of demand is how every glut in the history of the industry has been "
        "built. Over the next two-to-three quarters this resolves one of two ways &mdash; AI demand keeps outrunning "
        "the new supply and the 'broken cycle' thesis survives another few quarters; or the capacity lands first, "
        "memory prices roll, and the most levered names fall hardest. The Fable book is 30% Micron, the single best "
        "expression of the bet that the cycle is dead, and the discipline is to monetise the elevated volatility into "
        "this top with a collar or overwrite &mdash; not to add into a record on a narrative that history says breaks."
    ),

    "earnings_summary": (
        "Three ideas this refresh, all from the big-bank Q2 kickoff (Tue Jul 14 BMO). GS (Long, High &mdash; data gap "
        "flagged): the widest implied move in the cohort (~6%) and the most divided sell-side (15 buy / 15 hold / 2 "
        "sell) mean an investment-banking beat has the most room to re-rate into a steeper curve. JPM (Long, Medium): "
        "the bellwether &mdash; a clean NIM print on a +35bp 2s10s sets the cohort tone, but a well-owned name has less "
        "asymmetry. C (Long, Medium): the value leg &mdash; the biggest serial beater (13-20% surprises four quarters "
        "running) on the cheapest large-cap multiple, a fifth beat is the re-rating catalyst. All positioning pillars "
        "are tagged 'estimated' (Finnhub short-interest unavailable), so GS is capped at 'High &mdash; data gap "
        "flagged' rather than clean High. The same-morning June CPI is the macro cross-current that can swamp any print "
        "&mdash; hence the defined-risk (call-spread) expression on GS."
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
        "Astride the war-versus-rates split, and rotating fresh risk into what the record-IPO tape priced out. The "
        "surprise winner is the energy length: TotalEnergies led as the US-Iran ceasefire collapsed into an 80-target "
        "strike and Brent ran +5% to ~$76 &mdash; the war hedge the equity tape refused to build, already in the book. "
        "The AI sleeve caught the SK Hynix halo (a direct re-rating of the 30% Micron weight), but that record IPO is "
        "also the capacity-race tell that argues to monetise volatility into the top, not add. The rate book is mixed: "
        "the 2s10s steepener (MM-009) held through a week of backing-up yields and is the winner, but the short-10Y "
        "(MM-004) and short-2Y (MM-013) gave back edge on the oil cost-push, and gold (MM-005) is underwater on its "
        "min-hold because the war sank it. For the week into June CPI (Tue) and the bank-earnings kickoff: hold and "
        "trail the steepener; do NOT add duration into a hot-CPI risk; hold the euro short (MM-012, back to working) "
        "and carry the hot-core tail in defined-risk options (MM-042); treat gold as a CPI trade at its min-hold; and "
        "rotate fresh risk into the split &mdash; the Brent call spread (MM-040, the war premium the tape ignored), "
        "the SPX put spread (MM-041, the CPI + Hormuz collision at VIX 15), the EUR/USD put spread (MM-042, the "
        "hot-core dollar tail), and GS earnings vol (MM-043, the bank cohort into a steeper curve). The urgent "
        "house-keeping: recognise the energy length is the working war hedge and press it convexly; monetise Micron's "
        "IVol into the SK Hynix top."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); no option line is open this "
                 "refresh. US cash markets are closed today (Sat Jul 11), so equity-index and rate marks reflect the "
                 "Fri Jul 10 close.")
    },
    "idea_selection": [
        {"label": "Brent Aug $78/$88 call spread — own the war premium the tape priced out (MM-040)", "in": True,
         "text": ("The marquee idea. The ceasefire collapsed into an 80-target US strike, Iran attacked ships in "
                  "Hormuz, and the Treasury revoked Iran's oil waiver &mdash; a real supply premium &mdash; yet the "
                  "S&P booked a winning week and VIX fell to 15. Brent repriced +5% but sits ~$76, far below where a "
                  "Hormuz disruption clears. A call spread struck near spot owns the escalation tail with defined risk "
                  "and presses the book's TotalEnergies length without adding spot crude. Max loss capped.")},
        {"label": "July SPX 7,400/7,150 put spread — hedge the CPI + Hormuz collision (MM-041)", "in": True,
         "text": ("The melt-up bought a record IPO through a shooting war and priced a benign CPI at the same time &mdash; "
                  "VIX 15 into a two-sided print. June CPI (core +0.3% m/m cons) lands with a $76-Brent cost-push in the "
                  "pipeline and a Fed leaning 9-of-18 toward a hike, plus a live Hormuz war as a second tail. Below-spot "
                  "convexity is cheap; the put spread owns the gap the complacent index is ignoring. Defined risk.")},
        {"label": "EUR/USD 1-week 1.135/1.115 put spread — own the hot-core dollar tail (MM-042)", "in": True,
         "text": ("The dollar top stalled and base-built at 101 as the oil-led yield backup rebuilt the rate "
                  "differential, and $76 Brent is a euro-negative terms-of-trade shock. A hot June CPI re-arms the Fed "
                  "the July 2 payroll disarmed and drops EUR/USD toward 1.13. A defined-risk put spread owns that print "
                  "without fighting a two-way spot tape, and lets the book hold its core short (MM-012). Max loss capped.")},
        {"label": "Long GS into Q2 earnings (call spread) — the widest implied move in the bank cohort (MM-043)", "in": True,
         "text": ("Big banks kick off Q2 season Tue Jul 14 into a 2s10s at +35bp (NIM tailwind). GS carries the widest "
                  "implied move (~6%) and the most divided sell-side (15 buy / 15 hold / 2 sell) on ~$14.46 EPS after "
                  "beating four straight quarters &mdash; an IB beat against a split book has the most room to re-rate. "
                  "Own the earnings vol with a defined-risk call spread, not naked, because CPI lands the same morning.")},
        {"label": "2s10s steepener (MM-009) — harvest and trail, don't press", "in": False,
         "text": ("The one rate expression the war didn't break: ~+35bp, ~+130%, held through a week of backing-up "
                  "yields. Held and trailed, not added &mdash; a hot CPI could bear-flatten the front. The "
                  "consensus-agnostic steepener remains the higher-conviction rate trade than the directional front-end "
                  "fade (MM-013).")},
        {"label": "Long gold (MM-005) — hold on the min-hold, it's a CPI trade now", "in": False,
         "text": ("Underwater ~-9% and below its $4,250 stop, but held to the ~Jul 15 min-hold. The war did NOT save it "
                  "&mdash; yields backed up and gold traded as a real-rates short. It needs a soft CPI Tuesday, not a "
                  "Hormuz headline; a hot print at the min-hold forces the exit. Not a fresh add.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 14.0},
        {"label": "VIX",   "value": round(_g("vix") or 15.03, 2)},
        {"label": "VIX3M", "value": 17.5},
        {"label": "VIX6M", "value": 18.5},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.21, 3)},
        {"label": "5Y",  "value": 4.36},
        {"label": "10Y", "value": round(_g("us10y") or 4.56, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 4.98, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-040", "trade": "Buy Aug Brent $78/$88 call spread (own the Hormuz war premium)",
            "asset_class": "Commodity (options)", "structure": "call spread",
            "entry": "~$76 spot", "stop": "—", "target": "~5x at $88",
            "conviction": 7,
            "conviction_breakdown": {"gap": 3, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to Aug expiry", "min_hold_days": 0,
            "thesis": ("The marquee idea: the war the equity tape refused to price is a live supply shock in crude. The "
                       "ceasefire collapsed into an 80-target US strike, Iran attacked merchant ships and warned it "
                       "will close Hormuz, and the Treasury revoked Iran's oil-sale waiver &mdash; a genuine supply "
                       "premium &mdash; yet the S&P booked a winning week and VIX fell to 15. Brent repriced +5% but "
                       "sits ~$76, far below where a real Hormuz disruption clears. A call spread struck near spot owns "
                       "the escalation tail with defined risk, and it is the disciplined way to press the book's energy "
                       "length (TotalEnergies) without adding spot crude into a two-way headline tape."),
        },
        {
            "id": "MM-2026-041", "trade": "Buy July SPX 7,400/7,150 put spread (hedge the CPI + Hormuz collision)",
            "asset_class": "Equity (options)", "structure": "put spread",
            "entry": "~0.5% premium", "stop": "—", "target": "~5x at 7,150",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "to late Jul", "min_hold_days": 0,
            "thesis": ("The melt-up bought a record IPO through an 80-target strike and priced a benign CPI at the same "
                       "time &mdash; VIX fell to 15 into a two-sided print. June CPI (core +0.3% m/m consensus, ~2.9% "
                       "y/y) lands with a fresh $76-Brent oil cost-push in the pipeline and a Fed leaning 9-of-18 "
                       "toward a hike, while a live Hormuz war is a second, uncorrelated tail. A July 7,400/7,150 put "
                       "spread re-establishes the index hedge on an AI-concentrated book, structured for the discrete "
                       "CPI + war-headline risk &mdash; not a chase of at-the-money premium into cheap vol."),
        },
        {
            "id": "MM-2026-042", "trade": "Buy 1w EUR/USD 1.135/1.115 put spread (own the hot-core CPI dollar tail)",
            "asset_class": "FX (options)", "structure": "put spread",
            "entry": "~1.1415 spot", "stop": "—", "target": "~4x at 1.115",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Jul 17", "min_hold_days": 0,
            "thesis": ("The dollar top stalled and the euro is the cleanest way to own the hot-CPI tail. DXY base-built "
                       "at ~101 as the oil-led yield backup rebuilt the rate-differential bid, and a $76-Brent premium "
                       "is a euro-negative terms-of-trade shock &mdash; the euro area imports its energy. June CPI "
                       "(Tue, core +0.3% m/m consensus) is the trigger: a hot core re-arms the Fed the July 2 payroll "
                       "disarmed, extends the dollar, and drops EUR/USD toward the 1.13 handle. A defined-risk put "
                       "spread owns that specific print without fighting a two-way spot tape, and lets the book hold "
                       "its core short (MM-012) while carrying the CPI tail cheaply."),
        },
        {
            "id": "MM-2026-043", "trade": "Long GS into Q2 earnings (call spread, ~6% implied move)",
            "asset_class": "Equity (single-name / earnings vol)", "structure": "call spread",
            "entry": "spot / Jul expiry", "stop": "premium at risk", "target": "~3x on an IB beat",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to Jul 17 (earnings Jul 14)", "min_hold_days": 0,
            "thesis": ("The bank cohort reports into a tailwind and GS is the highest-beta way to own it. Big banks "
                       "kick off Q2 season Tue Jul 14 into a 2s10s at ~+35bp (NIM support) and a re-accelerating "
                       "capital-markets pipeline. GS carries the widest implied move (~6%) and the most divided "
                       "sell-side (15 buy / 15 hold / 2 sell) on ~$14.46 EPS and ~$16.4B revenue after beating four "
                       "straight quarters. The asymmetry is a beat on investment banking against a split book &mdash; "
                       "the name consensus doubts most has the most room to re-rate. Own the earnings vol with defined "
                       "risk (a call spread), not the whole cohort; the same-day CPI is the risk that caps it."),
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
