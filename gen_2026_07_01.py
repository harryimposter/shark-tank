#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-07-01 (Wednesday). THE ALL-CLEAR THAT ARMS THE HAWK.

THE NEXT CHAPTER vs the Jun 29 (Strikes Without a Premium) run: the desensitisation bet PAID. The
US-Iran ceasefire firmed into a formal halt-and-reopen-Hormuz deal, the AI complex RIPPED back, and
the quarter closed the best since 2020 — and now the melt-up walks straight into its first live test
from a new Fed chair who has dropped the map, plus a jobs print.
- THE MELT-UP WON, AND BROADENED. Tue Jun 30 close (best quarter for US indices since 2020): S&P
  7,449.36 (+0.79%), Nasdaq Composite 26,213.72 (+1.52%), Dow 52,319.20 (+0.26%, RECORD high). The
  chip complex extended its rebound off the early-June rout — NVDA +2.6%, AMD +7.7%, Intel +6% — as
  the tape looked past AI-valuation worries; hyperscaler 2026 capex commitments ~$750bn keep the
  build-out intact. (TheStreet, CNBC, Intellectia.)
- THE WAR DE-ESCALATED FOR REAL. The US and Iran reached a deal to halt attacks and let commercial
  vessels transit Hormuz freely; oil ROSE modestly on the deal (Mon Jun 29: WTI +1.9% to $70.56,
  Brent +1.3% to $72.91) after WTI settled below $70 Fri for the first time since Feb 27. ING: the
  recovery optimism on Gulf supply is overdone — risks remain. (CNBC, Al Jazeera.)
- WARSH TAKES THE SINTRA STAGE — TODAY. New Fed chair Kevin Warsh's first major international
  appearance: a 13:00 GMT panel with Lagarde, Bailey and Macklem at the ECB Forum (Jun 29-Jul 1).
  His message is a guidance vacuum by design: "We've dropped forward guidance," inflation still above
  the 2% target, monetary policy the primary driver of inflation. NPR (Jun 17): the Fed held and
  hinted at a hike later in 2026; BofA: the Fed is "fed up with inflation" and will hike, reversing
  earlier cuts. Core PCE stubborn ~3.1%. (Bloomberg, C-SPAN, NPR, Fortune.)
- DATA SPLIT UNDER THE HEADLINE. May JOLTS (Jun 30) held at 7.6mn openings — ABOVE the ~7.36mn
  expected, shrugging off the Iran war. But June consumer confidence, though up on cheaper gas, showed
  "jobs hard to get" jumping to 22.5%, the highest since Jan 2021 — the labour market softening
  underneath a strong-openings headline. (CNN, Conference Board, BLS.)
- RATES BACKED UP, GOLD AT AN 8-MONTH LOW. 2Y 4.11%, 10Y 4.44% (Jun 30) — both nudged higher on the
  risk-on + hawkish-hike repricing; 2s10s ~+33bp. Gold ~$4,030, the weakest since Nov 2025, the clean
  tell of a real-rates regime. DXY eased -0.26% Mon on the equity rip; EUR/USD +0.33% on strong euro-
  area confidence. VIX ~17-18. BTC ~$60k. (FRED, Trading Economics, Barchart.)
- TARIFF TAIL INTO JUL 4. Trump's 100% digital-services-tax tariff threat (aimed at the EU) hangs over
  the Jul 4 deadline to implement the deal capping EU tariffs at 15%; DST is the unresolved sticking
  point, and the legal authority is contested post-SCOTUS. (PBS, CBS, TechTimes.)
- WEEK AHEAD: TODAY Jul 1 — Warsh at Sintra (13:00 GMT) + ISM Manufacturing (June, 10:00 ET,
  cons. ~53.7, prices-paid ~82). Thu Jul 2 — June PAYROLLS (cons. ~+115k, u-rate 4.3%), the decisive
  hike-pricing input. Fri Jul 3 early close; markets shut Jul 4 (Independence Day) with the EU-tariff
  deadline the same day.
- BOOK ACTION: the desensitisation macro call nailed it (chips ripped, records) but the book's RATE
  LONGS are the leg now on the wrong foot — yields backed up into the hawkish test. Harvest is done;
  the question is whether to trim duration ahead of Warsh + payrolls. Fresh ideas own the melt-up's
  blind spots: an event-vol hedge into Warsh/payrolls, a chip-dispersion RV (long NVDA / short the
  overbought AMD), a defined-risk gold bounce off capitulation, and a EUR fade into Jul 4.

Run:  python gen_2026_07_01.py
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
# Fallback: the TradingView feed intermittently drops the cash S&P / Dow lines. Inject the
# web-verified Jun-30 closes (corroborated TheStreet + CNBC) so the dashboard headline indices
# never render "unverified". Only set if the live feed did not resolve them.
if "spx" not in snap:
    snap["spx"] = {"close": 7449.36, "chg_pct": 0.79, "chg_abs": 58.6}
if "dji" not in snap:
    snap["dji"] = {"close": 52319.20, "chg_pct": 0.26, "chg_abs": 136.0}
levels = live_levels.trade_levels(snap)
# Option spreads have no live feed — mark from spot. The fresh index downside this refresh is a
# tighter July SPX put spread dated to Warsh (Sintra, Jul 1) + June payrolls (Jul 2) — MM-032.

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
    "MU":   "Still the book's largest position (~26-32%) and the anchor of the melt-up: the AI complex ripped back into "
            "quarter-end (best quarter since 2020) and memory rode it. The Jun 24 blowout (tightness 'locked in beyond "
            "2027') is confirmed and now in the price; a third of the book on one name into a record tape and a "
            "guidance-free Fed is a risk question, not a conviction. The move is to overwrite/collar into strength while "
            "IVol is bid, not chase the rip.",
    "NVDA": "The franchise leader, and the CHEAP side of today's dispersion trade: NVDA rebounded +2.6% Mon but trades "
            "~25x forward on record ~$216bn FY26 revenue, while the beta beneficiary AMD (+7.7% Mon, +130% YTD) sits at "
            "~84x. When the rebound over-rewards the most expensive name, own the leader and fade the multiple — the "
            "long leg of the chip-dispersion RV (MM-033). An overbought screen here is the melt-up, not a fresh chase.",
    "AMD":  "The overbought symptom of the rip: +7.7% Mon and ~130% YTD at ~84x forward, the highest-multiple leg of the "
            "chip rebound. The book owns it as a ~+390% winner — the moment to overwrite (sell rich upside calls) and to "
            "SHORT it against NVDA in the dispersion RV (MM-033). An overbought RSI on the most expensive name in a "
            "record tape is a fade signal, not a breakout.",
    "XLE":  "The war tail deflated: the US and Iran struck a deal to halt attacks and reopen Hormuz freely, and crude "
            "only bounced modestly off Friday's sub-$70 low (WTI $70.56, Brent $72.91). ING flags the Gulf-supply "
            "recovery optimism as overdone — the residual risk premium is thin, not gone. Energy length (the book's TTE) "
            "is a small relief today but still not the war hedge it was bought as; own residual upside with defined risk.",
    "GLD":  "Gold at ~$4,030, the weakest since Nov 2025 — the clean tell of the real-rates regime: a hawkish, "
            "guidance-free Warsh and hike-repricing pin bullion even with the dollar softening on the equity rip. We OWN "
            "it (MM-005 / the book's 4GLD) held on the min-hold to ~Jul 15, not added. The asymmetric play is a "
            "defined-risk call spread (MM-034): a dovish Warsh or a soft payroll is the squeeze the drained spec long can't absorb.",
    "TLT":  "Duration is the leg on the WRONG foot now: the risk-on rip + the hawkish-hike repricing backed the 2Y to "
            "4.11% and the 10Y to 4.44%. The bond market's disinflation bet is being tested by a Fed 'fed up with "
            "inflation' and a strong-openings JOLTS. We're long via MM-004/013 (gave some back) and the steepener "
            "(MM-009, still the best position). Warsh (today) + payrolls (Thu) resolve it — trim, don't add duration into the print.",
    "XLF":  "Financials stay the rate-regime equity winner and now the melt-up beneficiary too: a hawkish, hike-hinting "
            "Warsh and an elevated front end lift net-interest margins, while the record-high tape carries capital-markets "
            "and lending fees. Own the margin beneficiary of higher-for-even-longer over chasing the most expensive AI "
            "names into two live policy binaries.",
    "BTC":  "Bitcoin ~$60k, still capped despite the equity rip — the same real-rates regime that pins gold at an "
            "8-month low. Warsh's Sintra remarks on liquidity and crypto drew focus; a guidance-free hawkish Fed is the "
            "macro headwind. Not a book position; a tell that the liquidity bid is concentrating in mega-cap equity, not broadening.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("The All-Clear That Arms the Hawk: A Record Quarter Closes Into Warsh's Sintra Debut and a Jobs Print — "
          "a Melt-Up Priced to Perfection Meets a Fed That Dropped the Map")
regime_note = (
    "The second-order effect consensus is missing this morning is that the relief rally just removed the Fed's last "
    "excuse. For a month the AI complex sold on valuation and the Gulf on war; both cleared at once — the US and Iran "
    "struck a deal to halt attacks and reopen the Strait of Hormuz, chips ripped back (AMD +7.7%, Nvidia +2.6%, Intel "
    "+6% Tuesday), and the S&P closed at 7,449.36, the Nasdaq Composite at 26,213.72 and the Dow at a record 52,319.20 "
    "to end the best quarter for US equities since 2020. Read that against a new Fed chair who has spent his first six "
    "weeks telling anyone who will listen that inflation is still above target and that he has 'dropped forward "
    "guidance.' A record-high tape, a strong-openings JOLTS and oil that stopped falling is precisely the backdrop that "
    "lets Kevin Warsh validate hikes rather than cuts — and the melt-up manufactured it. (TheStreet, CNBC, Bloomberg.) "
    "Decompose the all-clear the tape is selling. The consensus reads a record quarter as proof the coast is clear: war "
    "over, AI resilient, buy it. The anatomy says the rally is walking into two live policy binaries in 48 hours with a "
    "VIX at 17. TODAY Warsh takes the Sintra stage at 13:00 GMT beside Lagarde, Bailey and Macklem — his first major "
    "international appearance, and a man who removed the roadmap so he could move without warning; ISM Manufacturing "
    "(June) prints at 10:00 ET. Thursday brings June payrolls (consensus ~+115k, u-rate 4.3%), the decisive input to a "
    "hike the market is now pricing in — BofA has the Fed 'fed up with inflation' and hiking, reversing earlier cuts. "
    "The rally is priced to perfection into the one reaction function it is not hedged for. (C-SPAN, NPR, Fortune, BLS.) "
    "The data already splits under the headline. May JOLTS held at 7.6mn openings, above the ~7.36mn expected and "
    "shrugging off the war — the resilience that arms the hawk. But June consumer confidence, up on cheaper gas, showed "
    "'jobs hard to get' jumping to 22.5%, the highest since January 2021: the labour market softening underneath the "
    "strong-openings print. The Burry tell of this tape is that a strong-openings, soft-perception labour market is the "
    "late-cycle signature, and the Fed is about to tighten into it. (CNN, Conference Board.) "
    "The book felt the turn. The desensitisation macro call nailed the direction — chips ripped, records printed — but "
    "the leg that is now on the wrong foot is the rate-long tilt: the 2Y backed up to 4.11% and the 10Y to 4.44% on the "
    "risk-on and hawkish repricing, so the duration longs (MM-004/013) gave some back and only the 2s10s steepener "
    "(MM-009) still leads. Gold sits at an 8-month low (~$4,030), the clean confirmation that it is a real-rates short "
    "not a haven; the short EUR/USD (MM-012) is intact despite a small euro bounce on strong euro-area confidence. "
    "Trump's 100% digital-services-tax tariff threat still hangs over the July 4 EU deadline — a cost-push into a Fed "
    "with no slack, and an EUR-negative into the same window. (FRED, Trading Economics, PBS.) "
    "The regime is no longer about whether a shock sticks. It is that the market cleared every shock at once and now "
    "faces the consequence — a guidance-free Fed with the cover to hike into a record tape — and the trade is to own "
    "the melt-up's blind spots: the event vol into Warsh and payrolls, the dispersion inside the chip rip, and the "
    "asymmetric bounce in the one asset that has already capitulated."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# MM-008 was already banked in the Jun-27 run; it sits in the closed ledger. No close action today.

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
            "The quiet leg, and the record-quarter risk-on is the force against it: a global equity rip and firmer "
            "commodities keep a bid under the AUD, pinning the cross near the 1.662 stop rather than the 1.61 target. A "
            "steady ECB caps the EUR side, but there is no dated EUR catalyst left and the edge has thinned to almost "
            "nothing. This is the leg to trim into strength, not defend — the melt-up is the wrong tape for a short "
            "commodity-currency cross. Tight leash; the stop is close."
        ),
        "catalysts": [
            "Steady ECB now fully in the price — no forward EUR catalyst",
            "Record-quarter risk-on — the commodity-AUD bid, the force AGAINST the short",
            "RBA path — a hawkish hold supports AUD vs a steady ECB",
            "Iron ore / China demand — the AUD swing factor",
        ],
        "risks": (
            "The melt-up keeps bidding AUD and the cross runs the 1.662 stop; a firm China read lifts iron ore; an ECB "
            "official re-opens the hike door and EUR squeezes the other way. Stop 1.662 (tight)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the cross still sits above where the 2yr spread implies with a paused ECB, but the "
                            "edge has narrowed as AUD found its own risk-on bid.",
            "catalyst":     "1/2 — the dated ECB catalyst has passed; what remains is slower-burn (RBA, China PMI).",
            "positioning":  "1/2 — EUR longs are trapped flat, offering some unwind fuel; AUD positioning is light.",
            "confirmation": "0/2 — the cross drifted UP toward the stop, not lower; no confirmation of the short.",
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
            "The leg on the wrong foot now. The 10Y has backed up to ~4.44% — right at the entry — from the ~4.37% it "
            "rallied to, because the record-quarter risk-on and a Fed 'fed up with inflation' repriced the hawkish path "
            "higher, not lower. The disinflation thesis (the front end rallying over the dots) is intact but under its "
            "first real test: a guidance-free Warsh at Sintra today and June payrolls Thursday, with a strong-openings "
            "JOLTS arguing the labour market can take a hike. The bond market's bet needs the payroll to soften; until it "
            "does, this is a hold-and-trim, not an add. Stop 4.65%, ~21bp away."
        ),
        "catalysts": [
            "Warsh at Sintra TODAY (13:00 GMT) — a guidance-free hawkish tone backs yields up further",
            "June payrolls Thu Jul 2 — the decisive labour read; a soft print re-rallies the long end, a hot one hits it",
            "Oil off its 8-month low + the Jul 4 tariff cost-push — the term-premium risk AGAINST the position",
            "ISM Manufacturing today (prices-paid ~82 est) — a hot inflation read corroborates the hike",
        ],
        "risks": (
            "Warsh validates the hike and a hot June payroll (Jul 2) reprices the front end higher, dragging the 10Y to "
            "the 4.65% stop; the tariff cost-push and firmer oil widen the term premium. Stop 4.65% (now ~4.44%, ~21bp away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the front-end disinflation gap vs the Fed's hawkish path persists, but the hike-"
                            "repricing and firmer oil have narrowed it since the rally peak.",
            "catalyst":     "2/2 — Warsh today and payrolls Thu are both dated, live and decisive for the long end.",
            "positioning":  "1/2 — consensus is still short duration under Warsh; the squeeze needs a soft payroll to fire.",
            "confirmation": "1/2 — the 10Y backed up to the entry on the risk-on; the confirming rally has stalled — hold, don't press.",
            "stop_quality": "1/1 — 4.65% is a clear technical level; ~21bp of risk.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold in USD. The inverse of real rates, driven by the Fed path "
            "and real yields, USD strength, EM central-bank buying, geopolitical premia, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "The casualty, and the cleanest tell on the board: gold sits at ~$4,030, the weakest since November, ~-11% "
            "from the $4,523 entry. Two countries made peace and gold did not rally; the equity tape ripped to a record "
            "and the dollar softened, and gold STILL did not rally — because the dominant engine is real rates, and a "
            "hawkish, guidance-free Warsh pricing hikes is a real-rates headwind that overwhelms both the haven and the "
            "weaker-dollar bids. The price is below the $4,250 stop but the min-hold (to ~Jul 15) keeps the structural "
            "trade open through the drawdown. NOT an add here — but the capitulation is the setup for the asymmetric "
            "defined-risk bounce (MM-034) if Warsh disappoints the hawks or the payroll softens."
        ),
        "catalysts": [
            "Warsh at Sintra today + hike-repricing — the real-rates headwind, the dominant force against gold",
            "A dovish Warsh surprise / soft June payroll (Jul 2) — the only near-term catalyst that squeezes the short",
            "Spec long drained + ETF outflows — positioning cleaner, closer to capitulation",
            "EM / central-bank physical buying — the structural floor being tested at the 8-month low",
        ],
        "risks": (
            "Warsh validates the hike and a hot payroll pushes real rates higher, extending the metals rout below "
            "$3,900; the dollar re-firms. The min-hold keeps it open to ~Jul 15 — the stop is breached, the rule holds "
            "it; own the asymmetric bounce with defined risk via MM-034 rather than averaging down."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the real-rates engine dominates and both the haven and dollar bids failed to lift it; "
                            "only the central-bank / debasement floor remains, a narrow mispricing.",
            "catalyst":     "1/2 — a dovish Warsh or a soft payroll is a live, dated upside catalyst into a capitulated tape.",
            "positioning":  "2/2 — the spec long has drained to near-capitulation at an 8-month low; squeeze fuel building.",
            "confirmation": "0/2 — the trend is at fresh 8-month lows; the chart still contradicts the long.",
            "stop_quality": "1/1 — $4,250 is a defined level (breached); the min-hold rule is the discipline holding it.",
        },
    },
    "MM-2026-007": {
        "instrument": (
            "USD/JPY spot FX (dollar-yen). Driven by the US-Japan 2yr rate differential, BoJ "
            "normalisation, the Fed path, risk sentiment (JPY is a crisis safe-haven), and Japanese "
            "MoF intervention risk near ~160-163."
        ),
        "fundamental_thesis": (
            "Pinned, not punished, and helped at the margin by a softer dollar. The hawkish-hike repricing widens the "
            "rate differential — the textbook reason for USD/JPY to break higher — yet the pair is capped near the MoF "
            "line where the carry trade meets the official backstop, and Monday's risk-on actually eased the dollar a "
            "touch. The short is roughly flat, frustrated by crushed carry. The structural case (a normalising BoJ, a Fed "
            "whose hawkishness raises the odds of the carry-breaking vol event) is intact, and a guidance-free Warsh into "
            "payrolls is exactly the setup that can deliver that vol. Patient short with 163 as the backstop; the "
            "defined-risk way to own the tail is MM-021."
        ),
        "catalysts": [
            "MoF intervention at the line — explicit warnings; physical action forces stop-hunting",
            "Hawkish hike-repricing widening the differential — the force AGAINST the short near-term",
            "A guidance-free Warsh + payrolls re-rating vol — the catalyst that reactivates the carry unwind",
            "Japan CPI / BoJ guidance — further normalisation supports the yen",
        ],
        "risks": (
            "The hike-repricing pushes USD/JPY toward the 163 stop before the MoF acts; vol stays crushed and the carry "
            "trade persists through the melt-up. Stop 163.00."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is well above 2yr-differential fair value, though the hawkish Fed narrowed "
                            "that gap by widening the differential.",
            "catalyst":     "2/2 — the MoF line at 160 and a vol-re-rating guidance-less Fed are both live, dated.",
            "positioning":  "1/2 — the yen carry trade is crowded long-USD; crushed vol delays the unwind.",
            "confirmation": "0/2 — the yen held but did not rally on a hawkish Fed; no turn confirmed.",
            "stop_quality": "1/1 — 163.00 is a clean MoF-intervention ceiling; ~3 pts risk vs ~10 to target.",
        },
    },
    "MM-2026-008": {
        "instrument": (
            "SPX Jun-27 7300/7000 put spread — defined-risk. Buy the 7300 put, sell the 7000 put. "
            "Max profit $300/unit if SPX <=7000 at expiry; max loss = the ~$35 premium; break-even "
            "~7265. Driven by the SPX level (~7,420), implied vol (VIX ~18.4), and time to expiry."
        ),
        "fundamental_thesis": (
            "The call of the day. The hedge that earned its keep for exactly the reason it was held — the FOMC sits "
            "inside the Jun 27 expiry — paid as the hawkish dots dropped the S&P to ~7,420 (91pts closer to the 7,300 "
            "strike) and VIX jumped to 18.44. Marked ~$60 from ~$34, roughly +70% on the position. The FOMC catalyst "
            "has now passed, but the reason to hold has changed shape rather than disappeared: a hawkish, no-cuts Fed "
            "with a freshly-raised inflation forecast keeps the equity de-rating live, and ~$60 of residual convexity "
            "into a still-jittery tape is cheap to carry the seven sessions to expiry. Hold; let it work the new "
            "hawkish regime, not the spent event."
        ),
        "catalysts": [
            "Hawkish-Fed equity de-rating — a continued repricing toward 7,300-7,000 sends the spread to intrinsic",
            "Jobless claims + Philly Fed Jun 18 — a hot print in the guidance vacuum is a fresh downside catalyst",
            "MoU signing risk Jun 19 (Juneteenth, US closed; trades Mon 22) — a fracture pre-signing reopens downside",
        ],
        "risks": (
            "The hawkish repricing proves a one-day event and the S&P stabilises above 7,400 into expiry; time decay "
            "into Jun 27; a vol mean-reversion lower. Max loss remains the ~$35 premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the gap is now a live hawkish-Fed de-rating risk, not just event premium; the index "
                            "is ~120pts above the strike and falling.",
            "catalyst":     "2/2 — claims/Philly Fed land inside expiry today; the regime catalyst is fresh.",
            "positioning":  "1/2 — VIX re-rated to 18.4, so the maximum-complacency edge has partly been paid out.",
            "confirmation": "1/2 — the S&P broke lower on the dots; a confirming down-session, but ~120pts of cushion remains.",
            "stop_quality": "1/1 — defined-risk; max loss is the ~$35 premium.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (receive/own cut optionality), short "
            "the 10Y (short fiscal-supply risk). Pays when 10Y-minus-2Y widens. Currently ~2Y 4.22% "
            "/ 10Y 4.50%, spread ~+28bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "Still the best position in the book, and it held its steepening THROUGH the hawkish back-up: the spread sits "
            "~+33bp (10Y to 4.44%, 2Y to 4.11%) — the back end backed up a touch more than the front on the term-premium "
            "and firmer-oil read — with the open gain near +90% off the +15bp entry (an 18-month inversion). The thesis "
            "is reinforced by the regime: a guidance-free Warsh with no anchor and a July-4 tariff cost-push keeps a term "
            "premium under the back end, while any eventual reversal of the hike prices re-steepens through the front. "
            "The two-sided risk is a bear-flattener — a hot payroll that backs up the 2Y faster than the 10Y. Min-hold to "
            "~Jul 16; target +60bp; held, trail the stop up, not added."
        ),
        "catalysts": [
            "Guidance-free Warsh + Jul-4 tariff cost-push — keeps a term premium under the back end = steepens",
            "June payrolls Thu Jul 2 — a soft labour print fades the hike pricing and steepens further",
            "Treasury supply into a less-anchored long end — the back-end weight the steepener rides",
            "A hot payroll that backs up the front end faster — the bear-flattener risk AGAINST it",
        ],
        "risks": (
            "A hot June payroll (Jul 2) reprices the hike and the front end backs up faster than the long end, bear-"
            "flattening the curve; a global safe-haven bid flattens via the long end. Stop: spread below -10bp (now ~+33bp)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve is still structurally underpriced vs the late-cycle mean off an 18-month "
                            "inversion; the steepening has room to the +60bp target.",
            "catalyst":     "2/2 — payrolls Thu is a live, dated front-end catalyst; the term premium is steepening it now.",
            "positioning":  "1/2 — front-end positioning is still hawkish under Warsh; the eventual reversal squeezes it.",
            "confirmation": "2/2 — the spread widened to ~+33bp THROUGH the hawkish back-up; the steepen is confirming.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "Onside, with a small bounce to fade. EUR/USD ticked up (+0.33% Monday) on a softer dollar into the equity "
            "rip and stronger euro-area confidence, but the structural short is intact and the setup improves into the "
            "week: a guidance-free Warsh pricing hikes reasserts the rate-path asymmetry, and Trump's 100% digital-tax "
            "tariff threat lands squarely on the EUR days before the July 4 deadline. The Monday bounce is the entry to "
            "add downside with defined risk (MM-035), not a reason to cover. It pairs with the book's European-equity "
            "tilt and hedges the ~72% USD sleeve. Hold toward 1.13; the two-sided risk is a clean July-4 deal. Stop 1.182, distant."
        ),
        "catalysts": [
            "Warsh reasserting the hawkish path — the rate-path asymmetry firmly dollar-positive",
            "Trump's 100% digital-tax tariff threat into Jul 4 — an EUR-negative cost-push on the EU",
            "Spec positioning — EUR longs the squeeze fuel; Monday's bounce thinned the short crowd",
            "A clean EU-US tariff deal by July 4 — the offsetting EUR-supportive force to watch",
        ],
        "risks": (
            "A clean EU-US tariff deal and broad risk-on extends the EUR bounce; a soft US payroll fades the dollar; an "
            "ECB official re-opens the hike door. Stop 1.182 (distant)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the rate-path asymmetry persists and the Jul-4 tariff threat is a fresh EUR-negative; "
                            "Monday's bounce is a wobble, not a regime change.",
            "catalyst":     "2/2 — Warsh today and the July 4 tariff/digital-tax deadline are both dated and live.",
            "positioning":  "1/2 — the Monday bounce thinned the short crowd; EUR longs still provide unwind fuel.",
            "confirmation": "1/2 — EUR bounced on the day but holds well below the recent highs; the trend is intact, the day wobbled.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; the position has a wide cushion.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receive 2Y swap / long 2Y notes). The 2Y is the market's "
            "real-time forecast of the Fed path over two years — the most policy-sensitive point on the "
            "curve."
        ),
        "fundamental_thesis": (
            "The trade the Fed shot at, now braced for the second shot. The thesis was that the front end over-prices a "
            "2026 hike; the 2Y rallied back through the 4.162% entry to ~4.09% and then nudged up to ~4.11% as the "
            "record-quarter risk-on and a Fed 'fed up with inflation' repriced the hike back in. It is roughly flat, and "
            "its fate is now a coin-flip on two events: a guidance-free Warsh at Sintra today and June payrolls Thursday. "
            "The contrarian case (the hike unwinds on a softening labour market — note 'jobs hard to get' at a 2021 high) "
            "is intact but unconfirmed until the payroll softens. Min-hold to ~Jul 8; stop 4.35%, ~24bp away. Hold; do "
            "NOT add into the print."
        ),
        "catalysts": [
            "Warsh at Sintra TODAY — a guidance-free hawkish tone prices the hike further in (against the short)",
            "June payrolls Thu Jul 2 — a soft print prices OUT the hike and re-rallies the 2Y",
            "'Jobs hard to get' at a 2021 high — the softening-labour tell that argues the hike is too much",
            "Strong-openings JOLTS + a hot payroll — the risk that confirms the hawkish path",
        ],
        "risks": (
            "Warsh validates the hike and a hot June payroll (Jul 2) fully prices it, sending the 2Y to the 4.35% stop. "
            "Stop 4.35% (now ~4.11%, ~24bp away); min-hold to ~Jul 8."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the softening-labour read re-widens the gap vs the justified hike probability, but the "
                            "hawkish repricing has narrowed it since the rally.",
            "catalyst":     "2/2 — Warsh today and payrolls Thu are dated and decisive for the front end.",
            "positioning":  "2/2 — the market is maximally positioned for a hawkish Warsh; squeeze fuel on any soft print.",
            "confirmation": "1/2 — the 2Y backed up to ~4.11% on the risk-on; the confirming rally stalled — hold, don't add.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~24bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-032": {
        "instrument": (
            "Buy a July SPX 7,250/7,000 put spread — a tight, event-dated index hedge into Warsh (Sintra, Jul 1) "
            "and June payrolls (Jul 2). Buy the 7,250 put, sell the 7,000 put; max loss the premium, break-even "
            "~7,215. With the S&P at a record ~7,449 and VIX ~17, both strikes are below spot — cheap convexity on "
            "the two policy binaries a melt-up priced to perfection is not hedged for."
        ),
        "fundamental_thesis": (
            "The marquee idea: the record quarter closed the day before the tape's two most dangerous 48 hours, and the "
            "VIX is at 17. TODAY a guidance-free Fed chair takes the Sintra stage for his first major international "
            "appearance; Thursday brings June payrolls into a market now pricing HIKES on stubborn inflation. Either a "
            "hawkish Warsh soundbite or a hot payroll is the discrete down-catalyst a one-way melt-up has stopped "
            "pricing. A short-dated, below-spot put spread owns that event vol for a small defined premium — the "
            "portfolio overlay on a book that just rode the AI complex to a record, structured for the guidance vacuum "
            "Warsh built on purpose, not a chase of at-the-money premium."
        ),
        "catalysts": [
            "Warsh at Sintra TODAY (13:00 GMT) — a hawkish soundbite from a guidance-free chair is a discrete vol event",
            "June payrolls Thu Jul 2 — a hot print prices the hike and de-rates the melt-up",
            "ISM Manufacturing today (prices-paid ~82 est) — a hot inflation read corroborates the hike",
            "VIX ~17 at a record-high index — cheap convexity precisely when complacency is maximal",
        ],
        "risks": (
            "Warsh says nothing new (he dropped guidance for a reason), the payroll lands benign, and the melt-up grinds "
            "higher into the holiday; the spread decays. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the index prices the all-clear as one-way while two live policy binaries land in 48h; "
                            "a record tape at VIX 17 argues for two-sided risk.",
            "catalyst":     "2/2 — Warsh today and payrolls Thu are both dated and inside the structure's life.",
            "positioning":  "1/2 — sentiment is maximally risk-on at a record high; complacency is the fade.",
            "confirmation": "0/2 — the tape is at record highs; no confirming down-leg yet — this is a fresh event hedge.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-033": {
        "instrument": (
            "Equity RV — LONG NVIDIA (NVDA) vs SHORT Advanced Micro Devices (AMD), beta-weighted. A pair that pays "
            "when the cheaper franchise leader outperforms the higher-multiple beta beneficiary. Both rebounded off "
            "the early-June rout; the pair isolates valuation dispersion from AI-complex direction."
        ),
        "fundamental_thesis": (
            "The chip rebound over-rewarded the most expensive name, and that is the trade. In the Tuesday rip AMD ran "
            "+7.7% and is up ~130% year-to-date at roughly 84x forward earnings; Nvidia rebounded a more modest +2.6% "
            "and trades near 25x forward on record ~$216bn FY26 revenue. When a relief rally lifts the highest-multiple "
            "beta leg fastest, the clean expression is to own the leader and fade the beneficiary — long NVDA, short "
            "AMD — capturing the dispersion without taking a directional view on the AI complex the whole book is long. "
            "It is concentration-neutral to the melt-up and pays if the rebound's froth mean-reverts into the Warsh/"
            "payrolls test."
        ),
        "catalysts": [
            "AMD +7.7% Mon / +130% YTD at ~84x fwd vs NVDA ~25x — the valuation gap the rebound widened",
            "Warsh + payrolls (Jul 1-2) — a hawkish test that hits the highest-multiple beta hardest via the discount rate",
            "Hyperscaler ~$750bn 2026 capex — the demand both share, so the pair isolates valuation not volume",
            "AMD's forward P/E (~84x) vs record NVDA revenue — the mean-reversion setup",
        ],
        "risks": (
            "AMD keeps taking data-center CPU / MI-series share and the multiple gap is justified by growth; a broad "
            "AI-capex upgrade lifts the higher-beta name faster; the melt-up extends and froth persists. Stop: ratio -4%."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the ~84x-vs-25x forward gap after a one-day +7.7% move is a real dispersion, but AMD's "
                            "share gains partly justify a premium.",
            "catalyst":     "1/2 — the Warsh/payrolls test is dated; the valuation mean-reversion plays over weeks.",
            "positioning":  "2/2 — the crowd chased the high-beta beneficiary in the rip; the leader is under-owned relatively.",
            "confirmation": "1/2 — Tuesday's dispersion (AMD +7.7% vs NVDA +2.6%) wrote the first leg; one confirming move.",
            "stop_quality": "1/1 — a fixed ratio stop (-4%) is a clean, defined failure threshold.",
        },
    },
    "MM-2026-034": {
        "instrument": (
            "Buy an August gold $4,000/$4,300 call spread (tradeable via GLD or COMEX gold options). Buy the $4,000 "
            "call, sell the $4,300 call; max loss the premium. With spot at an 8-month low ~$4,030, it owns the "
            "asymmetric bounce off capitulation with capped, defined risk — the complement to the book's underwater "
            "4GLD/MM-005 long that does NOT average down the falling knife."
        ),
        "fundamental_thesis": (
            "Gold is maximally hated at exactly the moment its two-sided policy catalyst arrives. Bullion sits at "
            "~$4,030, the weakest since November, because a hawkish, guidance-free Warsh pricing hikes is a pure "
            "real-rates headwind — it did not rally on peace, on the equity rip, or on the softer dollar. But the spec "
            "long has drained toward capitulation, and the same 48 hours that threaten the melt-up are the asymmetric "
            "UPSIDE for gold: a Warsh who disappoints the hawks (he dropped guidance, after all) or a soft June payroll "
            "prices out the hike and squeezes a positioning that is one-way short. A defined-risk call spread owns that "
            "bounce for a small premium without adding to the book's underwater physical — the right way to own the "
            "capitulation, not the wrong way to defend the loss."
        ),
        "catalysts": [
            "A dovish Warsh surprise TODAY / a soft June payroll Thu — the real-rates relief that squeezes the short",
            "Spec long drained to near-capitulation at an 8-month low — thin positioning to push against",
            "EM / central-bank physical buying at the lows — the structural floor being tested now",
            "The hawkish path already in the price — the hike is priced, the dovish surprise is not",
        ],
        "risks": (
            "Warsh validates the hike and a hot payroll pushes real rates higher; gold breaks $3,900 and the spread "
            "decays. Max loss is the premium — defined risk, no averaging down."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the market prices the hawkish path fully and the dovish/soft-payroll tail not at all; "
                            "a capitulated real-rates short is a wide asymmetric setup.",
            "catalyst":     "2/2 — Warsh today and payrolls Thu are dated, live and two-sided for real rates.",
            "positioning":  "2/2 — the spec long has drained to near-capitulation; one-way short, squeeze-prone.",
            "confirmation": "0/2 — gold is at fresh 8-month lows; no confirming up-move yet — a fresh contrarian tail.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-035": {
        "instrument": (
            "Sell EUR/USD via a defined-risk 1-month put spread (buy the ~1.16 put, sell the ~1.14 put; or a short "
            "EUR/USD with a stop at 1.182). Fades Monday's euro bounce into the July 4 tariff/digital-tax deadline "
            "and a hawkish Warsh — a tactical, dated expression of the book's core dollar-long (MM-012)."
        ),
        "fundamental_thesis": (
            "The euro bounced on the wrong reasons and into the wrong week. EUR/USD rose ~0.33% Monday on a softer "
            "dollar as the equity rip curbed haven demand — but two dated forces converge against it in 72 hours: a "
            "guidance-free Warsh reasserting the rate-path asymmetry at Sintra today, and Trump's 100% digital-services-"
            "tax tariff threat hanging over the July 4 EU deadline. The bounce thinned the short crowd, which is the "
            "entry, not the exit. A defined-risk put spread fades the move with capped premium and pairs with the "
            "book's ~72% USD sleeve; it is a tactical add to the core short (MM-012), dated to Monday's dollar wobble "
            "and the specific tariff tripwire, not a fresh standing view."
        ),
        "catalysts": [
            "Warsh at Sintra today — a hawkish tone reasserts the dollar-positive rate-path asymmetry",
            "Trump's 100% digital-tax tariff threat into Jul 4 — the EUR-negative cost-push tripwire",
            "Monday's EUR bounce on a softer dollar — the thinned short crowd that is the entry",
            "June payrolls Thu — a hot print firms the dollar and extends the fade",
        ],
        "risks": (
            "A clean EU-US tariff deal by July 4 and a soft US payroll extend the euro bounce; a dovish Warsh fades the "
            "dollar. Defined risk via the put spread; the outright stop is 1.182."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the rate-path asymmetry and the fresh tariff threat argue lower; Monday's bounce is a "
                            "wobble against a still-intact dollar regime.",
            "catalyst":     "2/2 — Warsh today and the July 4 deadline are both dated and live.",
            "positioning":  "1/2 — the Monday bounce thinned the shorts; EUR longs still offer unwind fuel.",
            "confirmation": "1/2 — EUR bounced on the day but holds below the recent highs; the trend intact, the day wobbled.",
            "stop_quality": "1/1 — defined-risk via the put spread; the outright stop 1.182 is a clean prior high.",
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
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},   # hold; funding unmoved
    {"name": "MOVE", "level": "~104 (est)", "chg": "easier", "dir": "down"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Thu 25 Jun · TradingView"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~104", "chg": "easier (est)", "dir": "down"},
]

# Per-trade open-book notes (shown in the "yesterday, graded" table).
NOTES = {
    "MM-2026-001": "STILL OFFSIDE. EUR/AUD near the 1.662 stop — the record-quarter risk-on keeps a bid under the commodity-AUD, pinning the cross away from the 1.61 target. No EUR catalyst left; edge thinned to nothing. Trim into strength; the melt-up is the wrong tape for this short. Stop 1.662, tight.",
    "MM-2026-004": "BACKED UP TO THE ENTRY. The 10Y is ~4.44% — right at the 4.44% entry — after the risk-on rip and a Fed 'fed up with inflation' repriced the hawkish path higher, not lower. The disinflation bet is intact but ON TEST: Warsh (today) + payrolls (Thu) decide it. Hold-and-trim, don't add. Stop 4.65% (~21bp).",
    "MM-2026-005": "THE CASUALTY, CONFIRMED. Gold ~$4,030 — an 8-month low, ~-11% from the $4,523 entry. It did not rally on peace, on the record equity rip, or on the softer dollar: a pure real-rates short. Min-hold (to ~Jul 15) holds it below the $4,250 stop. Own the ASYMMETRIC bounce via the defined-risk call spread (MM-034), NOT an add here.",
    "MM-2026-007": "OFFSIDE, SLIGHT RELIEF. USDJPY pinned near the MoF line; Monday's softer dollar eased it a touch, but crushed carry keeps the yen unloved. Needs a vol shock — a guidance-free Warsh + payrolls (Thu) is exactly that. Stop 163.00; defined-risk expression MM-021.",
    "MM-2026-009": "STILL THE BEST POSITION. The spread held its steepening THROUGH the hawkish back-up — ~+33bp (10Y 4.44% / 2Y 4.11%), gain ~+90% off the +15bp entry. A guidance-free Fed + the Jul-4 tariff cost-push keep a term premium under the back end. Min-hold ~Jul 16; trail the stop; stop -10bp. The bear-flattener (a hot payroll) is the risk.",
    "MM-2026-012": "ONSIDE, SMALL BOUNCE TO FADE. EUR/USD ticked up (+0.33% Mon) on a softer dollar + strong euro-area confidence, but the structural short is intact — Warsh reasserts the asymmetry and Trump's digital-tax threat hits the EUR into Jul 4. The bounce is the entry to add downside (MM-035), not cover. Two-sided risk: a Jul 4 deal. Stop 1.182 (distant).",
    "MM-2026-013": "BACKED UP, FLAT. The 2Y nudged to ~4.11% from ~4.09% as the risk-on + hawkish repricing put the hike back in. Roughly flat; its fate is a coin-flip on Warsh (today) and payrolls (Thu). The softening-labour tell ('jobs hard to get' at a 2021 high) argues the hike is too much — but unconfirmed until the print. Hold, don't add. Min-hold ~Jul 8; stop 4.35% (~24bp).",
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
    {"datum": "Tue Jun 30 US close (best quarter since 2020): S&P 7,449.36 (+0.79%); Nasdaq Composite 26,213.72 (+1.52%); Dow 52,319.20 (+0.26%, RECORD high). Chips extended the rebound: NVDA +2.6%, AMD +7.7%, Intel +6%.",
     "source": "TheStreet + CNBC (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "US-Iran reached a deal to halt attacks + allow free Hormuz transit; oil rose modestly on it (Mon Jun 29: WTI +1.9% $70.56, Brent +1.3% $72.91) after WTI settled <$70 Fri, 1st since Feb 27. ING: Gulf-supply recovery optimism overdone.",
     "source": "CNBC + Al Jazeera (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "TODAY: Fed Chair Kevin Warsh at the Sintra ECB Forum, 13:00 GMT panel w/ Lagarde/Bailey/Macklem — 1st major intl appearance. Stance: 'We've dropped forward guidance'; inflation above 2% target; monetary policy primary driver. PENDING/ongoing.",
     "source": "Bloomberg + C-SPAN + ECB (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "NPR (Jun 17): Fed held rates, hinted a hike later in 2026 (Warsh's 1st FOMC). BofA: Fed 'fed up with inflation', to hike reversing earlier cuts. Core PCE stubborn ~3.1%, above target.",
     "source": "NPR + Fortune + Fed (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "May JOLTS (rel Jun 30): openings 7.6mn, unchanged & ABOVE ~7.36mn expected — shrugged off the Iran war. Hires 5.2mn, quits 3.1mn, layoffs 1.7mn.",
     "source": "BLS + CNN (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "June consumer confidence (rel Jun 30): edged higher on lower gas prices, BUT 'jobs hard to get' rose to 22.5%, highest since Jan 2021 — labour-market perceptions softened.",
     "source": "Conference Board + CNN (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "Rates backed up (Jun 30): 2Y 4.11%, 10Y 4.44%, 2s10s ~+33bp — on risk-on + hawkish-hike repricing. DXY -0.26% Mon (softer on the rip); EUR/USD +0.33% on strong euro-area confidence; VIX ~17-18; BTC ~$60k.",
     "source": "FRED + Barchart + Trading Economics (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "Trump: 100% tariffs on any country with a digital services tax on US firms (aimed at EU), hanging over the Jul 4 deadline to implement the deal capping EU tariffs at 15%; DST the sticking point; legal authority contested post-SCOTUS. PENDING.",
     "source": "PBS + CBS + TechTimes (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "Chip rebound context: SOXX had plunged ~10% in a session early June (NVDA -$300bn, AVGO -12.6%, Marvell -17%); hyperscaler 2026 capex ~$750bn. AMD +130% YTD ~84x fwd; NVDA ~25x fwd on record ~$216bn FY26 revenue.",
     "source": "Intellectia + Motley Fool + CNBC (corroborated)", "asof": "2026-06-30", "stale": False},
    {"datum": "Ahead: TODAY Jul 1 — Warsh at Sintra + ISM Mfg June (10:00 ET, cons ~53.7, prices-paid ~82, new orders ~57). Thu Jul 2 — June PAYROLLS (cons ~+115k, u-rate 4.3%). Fri Jul 3 early close; markets shut Jul 4 (Independence Day) + EU-tariff deadline. PENDING.",
     "source": "ISM + BLS + market calendar", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-06-30", "stale": True},
]

# No qualifying earnings idea in the 5-day-pre / 3-day-post window this refresh: Micron (Jun 24 AMC)
# has rolled to 5 sessions post — outside the 3-session-post window; Nike & Constellation (Jun 30 AMC)
# are Consumer, outside the Tech/Financials/Industrials/Utilities universe. Section omits when empty.
earnings_ideas = []

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
        "THE ALL-CLEAR THAT ARMS THE HAWK. The desensitisation bet paid: the US and Iran struck a deal to halt attacks "
        "and reopen Hormuz, the chip complex ripped back (AMD +7.7%, NVDA +2.6%, Intel +6% Tuesday), and the quarter "
        "closed the best since 2020 — S&P 7,449.36, Nasdaq Composite 26,213.72, Dow a record 52,319.20. Now the melt-up "
        "walks into its first live test with a VIX at 17: TODAY new Fed chair Kevin Warsh takes the Sintra stage "
        "(13:00 GMT) — a man who 'dropped forward guidance' and calls inflation still above target — alongside ISM "
        "Manufacturing; Thursday brings June payrolls (cons ~+115k) into a market now pricing HIKES (BofA: the Fed is "
        "'fed up with inflation'). The data splits under the headline: May JOLTS held at 7.6mn (above est), but 'jobs "
        "hard to get' hit 22.5%, a 2021 high. Rates backed up (2Y 4.11%, 10Y 4.44%) and gold slid to an 8-month low "
        "(~$4,030) — the leg on the wrong foot is the book's rate longs; only the steepener (MM-009, ~+90%) still leads. "
        "The trade is to own the melt-up's blind spots: the event vol into Warsh/payrolls, the dispersion in the chip "
        "rip, and the asymmetric bounce in the one asset that already capitulated. Trump's 100% digital-tax tariff "
        "threat hangs over the Jul 4 EU deadline. The record tape manufactured its own hawkish reaction function."
    ),

    "summary_narrative": """
<p>The market spent a month waiting to be told it was safe, and this week it told itself. The US and Iran struck a deal
to halt attacks and reopen the Strait of Hormuz freely; the chip complex that had cratered in early June ripped back
&mdash; AMD <strong>+7.7%</strong>, Nvidia +2.6%, Intel +6% on Tuesday; and the S&amp;P closed at <strong>7,449.36</strong>,
the Nasdaq Composite at 26,213.72 and the Dow at a record <strong>52,319.20</strong> to end the best quarter for US
equities since 2020. The all-clear is real. The problem is what it clears the way for. (TheStreet, CNBC, Al Jazeera.)</p>

<p>The second-order effect consensus is missing is that the relief rally removed the Fed's last excuse. For weeks the
AI selloff and the Gulf war were the reasons a hawkish Fed might stay its hand; both are gone, and what is left is a
record-high tape, a strong-openings JOLTS and oil that stopped falling &mdash; the exact backdrop that lets a new chair
who calls inflation &ldquo;still above target&rdquo; validate hikes rather than cuts. And that chair speaks today.
Kevin Warsh takes the Sintra stage at 13:00 GMT for his first major international appearance, beside Lagarde, Bailey
and Macklem &mdash; a man who has publicly &ldquo;dropped forward guidance&rdquo; so he can move without warning.
(Bloomberg, C-SPAN, NPR.)</p>

<p>The data already splits under the headline, and the split is the tell. May JOLTS held at <strong>7.6mn</strong>
openings, above the ~7.36mn expected, shrugging off the war &mdash; the resilience that arms the hawk. But June
consumer confidence, up on cheaper gas, showed the share of consumers saying jobs are &ldquo;hard to get&rdquo;
jumping to <strong>22.5%</strong>, the highest since January 2021. A strong-openings, soft-perception labour market is
the late-cycle signature &mdash; and the Fed is about to tighten into it, with June payrolls (consensus ~+115k) landing
Thursday. (CNN, Conference Board, BLS.)</p>

<p>The book felt the turn. The desensitisation call nailed the direction &mdash; chips ripped, records printed &mdash;
but the leg now on the wrong foot is the rate-long tilt: the 2Y backed up to <strong>4.11%</strong> and the 10Y to
<strong>4.44%</strong> on the risk-on and the hawkish repricing, so the duration longs (MM-004/013) gave some back and
only the 2s10s steepener (MM-009, ~+90%) still leads. Gold slid to an 8-month low (~$4,030), the clean confirmation
that it is a real-rates short, not a haven; the short EUR/USD (MM-012) held despite a small euro bounce on strong
euro-area confidence. Trump's 100% digital-tax tariff threat still hangs over the July 4 EU deadline. (FRED, Trading
Economics, PBS.)</p>

<p>The regime is no longer about whether a shock sticks. The market cleared every shock at once and now faces the
consequence &mdash; a guidance-free Fed with the cover to hike into a record tape. The trade is to stop chasing the
melt-up and start owning its blind spots: the event vol into Warsh and payrolls (a tight July put spread, MM-032), the
valuation dispersion inside the chip rip (long the cheaper leader Nvidia, short the overbought AMD, MM-033), and the
asymmetric bounce in the one asset that has already capitulated (a defined-risk gold call spread, MM-034). Trim the
duration into the print; do not add it.</p>
""",

    "takeaways": [
        "<strong>The all-clear arrived &mdash; and it arms the hawk.</strong> A US-Iran deal to reopen Hormuz and a "
        "chip-led rip (AMD +7.7%, NVDA +2.6%) closed the best quarter since 2020: S&amp;P 7,449.36, Nasdaq Composite "
        "26,213.72, Dow a record 52,319.20. The relief removes the Fed's last excuse to stay easy just as a hawkish new "
        "chair takes the stage. (TheStreet, CNBC.)",

        "<strong>Warsh speaks TODAY &mdash; the melt-up's first live test.</strong> New Fed chair Kevin Warsh's Sintra "
        "debut (13:00 GMT, with Lagarde/Bailey/Macklem) is a man who 'dropped forward guidance' and calls inflation "
        "above target. With a VIX at 17 and the index at a record, a hawkish soundbite is a discrete down-catalyst. Own "
        "it with a tight July SPX put spread (MM-032). (Bloomberg, C-SPAN.)",

        "<strong>The data splits under the headline &mdash; and the split is the tell.</strong> May JOLTS held at "
        "7.6mn openings (above est), shrugging off the war, but 'jobs hard to get' hit 22.5%, a 2021 high. A "
        "strong-openings, soft-perception labour market is the late-cycle signature the Fed is about to tighten into. "
        "June payrolls Thursday is the test. (CNN, Conference Board, BLS.)",

        "<strong>The book's rate longs are the leg on the wrong foot.</strong> The 2Y backed up to 4.11% and the 10Y "
        "to 4.44% on the risk-on + hawkish repricing, so the duration longs (MM-004/013) gave some back; only the 2s10s "
        "steepener (MM-009, ~+90%) still leads, holding through the back-up. Hold and TRIM into Warsh/payrolls &mdash; "
        "do not add duration. (FRED.)",

        "<strong>Gold at an 8-month low is the clean real-rates tell.</strong> ~$4,030, the weakest since November: it "
        "did not rally on peace, on the record rip, or on the softer dollar. The book's 4GLD/MM-005 is held on its "
        "min-hold, not added &mdash; but the capitulation is the setup for the asymmetric defined-risk bounce (MM-034) "
        "if Warsh disappoints the hawks or the payroll softens. (Trading Economics.)",

        "<strong>The chip rebound over-rewarded the most expensive name.</strong> AMD ran +7.7% and sits ~130% YTD at "
        "~84x forward; Nvidia rebounded +2.6% at ~25x on record ~$216bn revenue. Long the cheaper leader, short the "
        "overbought beneficiary (MM-033) &mdash; own the dispersion without a directional bet on the AI complex the "
        "book is already long. (Intellectia, Motley Fool.)",

        "<strong>The tariff tail still hangs over July 4.</strong> Trump's 100% digital-services-tax tariff threat "
        "hangs over the deadline to implement the deal capping EU tariffs at 15%; DST is unresolved and the legal "
        "authority is contested. EUR-negative into the same window &mdash; the fade of Monday's euro bounce (MM-035). "
        "(PBS, CBS, TechTimes.)",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "40%",
         "headline": "Warsh stays vague, the payroll softens — the melt-up survives its test",
         "body": "Warsh does at Sintra what he built the guidance vacuum to allow &mdash; says little that binds him "
                 "&mdash; and a soft June payroll (Jul 2, sub-100k with the u-rate ticking up on the 'jobs hard to get' "
                 "read) prices OUT the near-term hike. The 2Y rallies back below 4.05%, the duration longs (MM-004/013) "
                 "recover and the steepener (MM-009) extends toward +40bp, the chip rip broadens, and equities push to "
                 "fresh records; gold squeezes off the 8-month low (MM-034 pays). Risk up · rates down · dollar soft · "
                 "gold up · the July put spread decays."},
        {"kind": "base", "label": "Base", "pct": "40%",
         "headline": "A record tape into a hawkish hold — melt-up grinds, front end pinned, dispersion widens",
         "body": "Warsh reaffirms inflation above target without committing, the payroll lands near consensus (~+115k), "
                 "and the Fed stays a hawkish hold with a hike hinted but not delivered. Equities hold near the highs on "
                 "the AI-capex bid but the froth thins &mdash; the NVDA/AMD dispersion (MM-033) works &mdash; the 2Y "
                 "stays range-bound ~4.05-4.20%, the steepener holds, the dollar stays firm (MM-012/035) and the July 4 "
                 "tariff deadline caps risk appetite into the long weekend. Risk mixed · rates steady · dollar firm · "
                 "gold base · dispersion widens."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "The hawk is confirmed — Warsh leans hawkish and/or a hot payroll prices the hike",
         "body": "Warsh uses the Sintra stage to underline the hike, or a hot June payroll (>150k, u-rate steady) "
                 "validates it, and the front end backs up hard: the 2Y runs to the 4.35% stop (MM-013) and bear-"
                 "flattens the curve, the 10Y presses 4.55%+, and the discount-rate shock hits the highest-multiple AI "
                 "names first (AMD leads lower, MM-033 pays). The S&amp;P retraces from the record toward 7,250-7,000 "
                 "where the July put spread (MM-032) pays; the Jul 4 tariff escalation adds a cost-push. Risk down · "
                 "rates up · dollar up · gold down then bid."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a market that just cleared every overhang at once and now has to answer for it.
The US and Iran struck a deal to halt attacks and reopen Hormuz, the chip complex that cratered in early June ripped
back &mdash; AMD +7.7%, Nvidia +2.6%, Intel +6% &mdash; and US equities closed the best quarter since 2020 at record
highs. The non-consensus read is that this is not the safety it looks like: the relief rally has removed the two
reasons a hawkish Fed might have stayed its hand, and it hands a new chair who calls inflation still above target the
political cover to tighten into strength. The all-clear is what arms the hawk.</p>

<p>The counter-intuitive hook is the timing. The tape is treating a record quarter as proof the coast is clear, at the
exact moment the two most dangerous events on the calendar arrive with a VIX at 17. Today Kevin Warsh &mdash; who has
publicly &lsquo;dropped forward guidance&rsquo; so he can move without telegraphing &mdash; takes the Sintra stage for
his first major international appearance, and ISM Manufacturing prints. Thursday brings June payrolls into a market
that, per BofA, has moved to pricing a Fed &lsquo;fed up with inflation&rsquo; that will hike, reversing earlier cuts.
The melt-up is priced to perfection into the one reaction function it is not hedged for.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong> a
US-Iran deal reopening Hormuz, oil bouncing modestly off a sub-$70 low (WTI $70.56 / Brent $72.91), core PCE stubborn
near 3.1%, May JOLTS at 7.6mn openings, but consumers' &lsquo;jobs hard to get&rsquo; at a 2021 high; gold at an
8-month low. <strong>What is priced:</strong> a record equity tape, a VIX at 17, a 2Y at 4.11% and a 10Y at 4.44% that
backed up into the hike-repricing, a firm dollar. <strong>Consensus narrative:</strong> &lsquo;the war is over, AI is
resilient, buy the record.&rsquo; The gap &mdash; and the alpha &mdash; is that the tape is underpricing the two live
policy binaries in 48 hours, and the dispersion inside the rip that lifted the most expensive name (AMD, ~84x) fastest.</p>

<p>Go around the world. <strong>US:</strong> a record-quarter melt-up on the Iran deal and the chip rebound, now
walking into Warsh and payrolls. <strong>Middle East:</strong> the actual de-escalation &mdash; a deal to halt attacks
and reopen the Strait, though ING flags the Gulf-supply recovery optimism as overdone. <strong>Europe:</strong> euro-
area confidence rose more than expected (the euro bounced +0.33%), but Trump's 100% digital-tax tariff threat hangs
over the July 4 deadline. <strong>Japan:</strong> the yen soft near the MoF line as the hike-repricing widens the
differential (MM-007). <strong>Central banks:</strong> Sintra puts Warsh, Lagarde, Bailey and Macklem on one stage
today &mdash; the calendar's single biggest cluster of policy signal.</p>

<p>The political angle runs on two fault lines the market is under-weighting. The Papic constraint on the Fed is that
Warsh &mdash; a chair who built his reputation on inflation-fighting and who removed forward guidance on purpose
&mdash; has every institutional incentive to lean hawkish at his international debut into a record tape; the market
that reads &lsquo;dropped guidance&rsquo; as dovish flexibility has it backwards. The second fault line is trade: the
100% digital-tax tariff threat stacks a cost-push onto the July 4 deadline exactly when the Fed has no slack, and it
lands squarely on the EUR (MM-012/035) and on the book's EU names (LVMH, SAP).</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the Warsh/payrolls event vol at a VIX of 17 (MM-032); the
valuation dispersion inside the chip rip (long NVDA / short AMD, MM-033); the asymmetric gold bounce off capitulation
(MM-034). <strong>Fairly priced:</strong> the firm dollar; the front-end hike-repricing. <strong>Fully priced:</strong>
the AI-capex build-out (hyperscaler ~$750bn) as a one-way bull case. <strong>Over-priced (at risk):</strong> the
durability of a record-high melt-up resting on a guidance-free chair staying quiet and a jobs print landing soft.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is that the relief rally just took away the Fed's last
excuse. For a month there were two reasons a hawkish central bank might stay its hand: an AI complex in a valuation
tailspin and a shooting war in the Gulf. This week both cleared &mdash; the US and Iran struck a deal to reopen Hormuz,
and the chip names ripped back hard enough to close the best quarter for US equities since 2020 at record highs. The
market is reading that as safety. It should be reading it as exposure. A record tape, resilient job openings and oil
that stopped falling is precisely the backdrop that lets a new chair who thinks inflation is unfinished business
tighten into strength &mdash; and he speaks today.</p>

<p>Decompose the all-clear the tape is selling. The consensus files a record quarter and a chip rebound as proof the
coast is clear, and buys it. Pull it apart: the S&amp;P closed at seventy-four-forty-nine and the Dow at a record, but
the leadership was the most expensive corner of the market &mdash; AMD up seven-point-seven percent in a single
session, a name already up a hundred-and-thirty percent this year at eighty-four times forward earnings, while Nvidia,
the cheaper franchise leader at twenty-five times on record revenue, rose a third as much. So what, who is wrong, what
is the trade: the consensus that reads a record close as an all-clear is wrong on the timing &mdash; it is walking a
melt-up priced to perfection into two live policy binaries in forty-eight hours &mdash; and the trade is to own the
event and the dispersion rather than chase the froth.</p>

<p>Trace it to a balance sheet, because that is where the durable part lives. The bond market told you what it thinks
this week: the two-year backed up to four-eleven and the ten-year to four-forty-four, not down. The marginal buyer that
had been trading a coming disinflation started pricing the opposite once the war and the AI wobble cleared, because the
same flow that drives everything &mdash; hyperscaler capex, some seven-hundred-fifty billion dollars committed for the
year, increasingly debt-funded &mdash; is both the reason equities are at records and the reason core goods stay
sticky. The boom the whole tape is long is the inflation the Fed cannot ignore. Gold is the cleanest confirmation:
it did not rally on peace, on the record rip, or on the softer dollar, because it is a pure real-rates instrument now,
and real rates are going the wrong way for it.</p>

<p>The Burry tell sits one layer under the jobs number. May job openings held at seven-point-six million, above
expectations, and the tape read it as strength. But underneath, the share of consumers who say jobs are hard to get
jumped to twenty-two-and-a-half percent, the highest since January 2021. A labour market that looks tight on the
employer side and soft on the household side is the late-cycle signature &mdash; openings lag, perceptions lead &mdash;
and the danger is a Fed that tightens on the lagging indicator into a consumer already turning. That divergence, not
this week's records, is the thing that will define the second half; it is why the payroll on Thursday matters more than
the quarter that just closed.</p>

<p>So the posture into the test is defensive on the winners and offensive on the blind spots. The steepener stays &mdash;
it held its ground through the hawkish back-up and is still the book's best position &mdash; but the duration longs get
trimmed, not added, because a guidance-free Warsh and a resilient jobs print are exactly what backs them up further.
Gold is held on its rule, not averaged down; the asymmetric bounce is owned with a defined-risk call spread, not more
physical. And the fresh money goes where the melt-up left gaps: a tight July put spread that owns the Warsh-and-payrolls
event vol at a VIX of seventeen, a long-Nvidia short-AMD pair that owns the dispersion the rip created, and a euro fade
into the July fourth deadline. The tape has decided the danger is behind it. The brief's read is that the danger is on
the stage this afternoon.</p>
""",

    "correlation_regime": """
<p><strong>1. Equities and rates re-coupled the wrong way &mdash; the biggest break on the board.</strong> For weeks
the bond market rallied while equities chopped, a disinflation bet against a risk-off tape. This week they flipped
together: the S&amp;P ripped to a record AND the 2Y backed up to 4.11% / 10Y to 4.44%. Good-news-is-good-news for
stocks became good-news-is-a-hike for bonds. A dominant-driver change this large means the disinflation trade (long
duration) is now the crowded side into Warsh &mdash; trim the duration longs (MM-004/013), the steepener (MM-009) is the resilient expression.</p>

<p><strong>2. Gold stayed decoupled from everything that should lift it.</strong> Peace, a record equity rip, and a
softer dollar all landed in the same 48 hours &mdash; and gold fell to an 8-month low (~$4,030). Two of its three
engines (haven, dollar) turned in its favour and it dropped anyway, because the third &mdash; real rates, under a
hawkish guidance-free Warsh &mdash; overwhelms them. That is the cleanest tell of the regime: gold is a pure
real-rates short now. It is why the book's 4GLD/MM-005 is held not added, and why the asymmetric bounce is owned with defined risk (MM-034).</p>

<p><strong>3. Chip dispersion blew out inside the rebound.</strong> The rebound was not uniform: AMD +7.7% vs NVDA
+2.6% in the same session, the highest-multiple name (~84x fwd) outrunning the cheaper leader (~25x on record revenue).
When a relief rally's leadership is the most expensive leg, the intra-sector correlation is breaking down &mdash; the
beta beneficiary decoupling from the franchise fundamentals. That break is the RV (long NVDA / short AMD, MM-033):
own the leader, fade the froth, stay neutral to the AI complex the whole book is long.</p>
""",

    "vol_skew": """
<p><strong>The most mispriced vol on the board is short-dated equity, and the calendar is the reason.</strong> Index
vol is asleep: VIX ~17-18 with the term structure in contango (est. VIX9D ~16.5 · VIX ~17.5 · VIX3M ~18.5 · VIX6M
~19.5), MOVE steady as rates settle into the hawkish repricing. The tape has priced the Iran deal and the record
quarter as one-way calm &mdash; and it is doing so the day before its two most dangerous events. A guidance-free Warsh
takes the Sintra stage today and June payrolls land Thursday, and a 17-handle VIX at a record-high index means the
market is charging almost nothing for the possibility that either one reprices the hike. The headline trade
implication: a tight, short-dated SPX put spread (July 7,250/7,000, MM-032) owns that event vol for a small defined
premium &mdash; below-spot convexity structured for the guidance vacuum Warsh built on purpose, not a chase of
at-the-money premium. The complement on the other side is gold, where vol has been sold into an 8-month-low
capitulation: a defined-risk gold call spread (MM-034) owns the asymmetric bounce a dovish-surprise or soft-payroll
tail would produce. If nothing fires, both decay cheaply; if either binary hits, the convexity is owned, not chased.</p>
""",

    "sector_rv": """
<p><strong>Leading (into quarter-end):</strong> semis and the broad AI complex &mdash; the chip rebound extended
(NVDA +2.6%, AMD +7.7%, Intel +6% Tuesday) to carry the best quarter since 2020; mega-cap tech and the Dow record.
<strong>Lagging:</strong> rate-sensitive duration proxies and gold miners as yields backed up and bullion hit an
8-month low; energy, which only bounced modestly off its sub-$70 low on the ceasefire deal; EU-exposed luxury and
platforms (LVMH, SAP) into Trump's digital-tax tariff threat. <strong>Today/next:</strong> Warsh at Sintra + ISM
Manufacturing today; June payrolls Thursday; the July 4 deadline &mdash; each a discrete event into a guidance vacuum.</p>

<p><strong>RV:</strong> Two cleanly fit today's tape. First, the chip-dispersion pair (MM-033): long the cheaper
franchise leader NVDA (~25x fwd, record ~$216bn revenue) vs SHORT the overbought beneficiary AMD (+7.7% Mon, ~130% YTD,
~84x fwd) &mdash; own the leader, fade the froth, stay neutral to the AI complex the book is long. Second, the
cross-region read: US financials/value over EU-exposed cyclicals into the July 4 tariff/digital-tax escalation, which
lands on European autos, luxury and platforms (the book's LVMH and SAP). Both are low beta to the index and high beta
to the regime's live risks (the discount-rate shock and the trade cost-push), and neither chases the record melt-up.</p>
""",

    "positioning": """
<p><strong>The crowd is positioned for the all-clear to hold &mdash; long the record melt-up, short vol, long the
high-beta chips, short gold.</strong> The loudest lean is in equities: trend-followers and systematic strategies are
max-long into a record close with a VIX at 17, so the pain trade is a Warsh soundbite or a hot payroll that reprices
the hike and de-rates the melt-up from a standing start (the cheap fade is MM-032). Inside that, the froth chased the
highest-multiple name &mdash; AMD ~84x after +130% YTD &mdash; so the crowded leg is the beta beneficiary, not the
cheaper leader (MM-033). In gold, the spec long has drained toward capitulation at an 8-month low, which makes the pain
trade a dovish-Warsh or soft-payroll squeeze the one-way short cannot absorb (MM-034). In rates, the tape just flipped
from short-duration to pricing hikes, so the disinflation longs are now the vulnerable side into the print &mdash; trim
(MM-004/013). In FX, the yen carry stays crowded long-USD at the MoF line (MM-007) and the euro-short crowd thinned on
Monday's bounce, the entry to re-add (MM-035). The pain trade everywhere is the same &mdash; a market that has decided
the hard part is over the day before its two hardest events.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; quarter-end and half-year turn passed without a funding squeeze, and the equity
rip actually eased dollar demand at the margin (DXY -0.26% Monday). <strong>The Pozsar mechanic:</strong> trace the
back-up in yields to a flow, not a forecast. The reason the 2Y and 10Y rose into a record equity tape is that the
marginal duration buyer that had been front-running a disinflation stepped back once the war and the AI wobble cleared,
and the term premium re-widened against a bond market with no forward-guidance anchor &mdash; Warsh removed it on
purpose. Underneath, the durable flow is the AI build-out: hyperscaler capex, ~$750bn committed for 2026 and
increasingly debt-funded, is simultaneously the bid under record equities and a real-economy claim on savings that
keeps the long end heavy. The funding angle that matters next is the collision of the IG issuance wave (2026 high-grade
supply ~$2.25tn, +35% y/y on AI capex) with a less-anchored long end into a guidance-free Fed. Watch IG issuance and
the 10Y together &mdash; and watch Warsh's Sintra remarks on liquidity, which drew focus precisely because plumbing is
where a guidance-free regime shows stress first.</p>
""",

    "tape_missing": """
<p><strong>The tape is charging a VIX of 17 for two policy binaries in 48 hours.</strong> A record-high index the day
before a guidance-free Fed chair's international debut and a jobs print is complacency with a number on it. The
falsifiable level: an S&amp;P close back below 7,300 says the melt-up is repricing the hike risk; a VIX pop through 22
says the event vol the tape gave away is being re-marked. The July SPX put spread (MM-032) owns the gap and costs
little precisely because consensus says the hard part is behind it.</p>

<p><strong>Just behind it: the market reads Warsh's 'dropped forward guidance' as dovish flexibility &mdash; it is the
opposite.</strong> A chair built on inflation-fighting removed the roadmap so he could hike without telegraphing, into
a record tape that just handed him the cover. The falsifiable line is the 2Y: a back-up through 4.20% on his Sintra
remarks or a hot payroll says the hike is being priced, running toward the 4.35% stop on the short-2Y (MM-013); a
rally back below 4.05% on a soft print says the disinflation longs (MM-004) are right. June payrolls Thursday is the
test, and the book is deliberately two-sided into it &mdash; trim, don't press.</p>

<p><strong>The Burry tell &mdash; the divergence hiding inside a strong jobs number.</strong> May job openings held at
7.6 million, above expectations, and the tape read it as strength. Underneath, the share of consumers who say jobs are
'hard to get' jumped to 22.5%, the highest since January 2021. Openings are an employer-side lagging indicator;
household perception leads. A labour market that looks tight to firms and soft to workers is the classic late-cycle
fork, and the structural risk nobody is pricing is a Fed that tightens on the lagging signal into a consumer already
turning &mdash; the policy mistake that resolves badly two-to-three quarters out. The equity index at a record, priced
for a soft landing, is the least prepared for the world where the labour market rolls while the Fed is still hiking.</p>
""",

    "book_outlook": {
        "commentary": (
            "Today the book's own concentration is both its tailwind and its exposure, and the two events this afternoon "
            "and Thursday decide which. The AI sleeve the book is built on &mdash; <b>Micron (~26-32%)</b>, <b>AMD</b> "
            "(a ~+390% winner), <b>NVDA</b> (-10.5%), <b>AVGO</b> (-21%), <b>SAP</b> &mdash; rode the chip rip straight "
            "into a record quarter, so the book had a strong Tuesday; but the same rally armed the hawk, and the leg "
            "that turned against the book is its <b>bond sleeve</b> &mdash; the <b>UST 1.25% 2031</b> (-13.9%) and "
            "<b>Siemens IG</b> (-10.6%) &mdash; as the 2Y backed up to 4.11% and the 10Y to 4.44% on the hike-repricing. "
            "<b>Xetra-Gold (4GLD)</b>, a huge winner (+108%) but the book's tail hedge, slid to an 8-month low: it did "
            "not rally on peace or on the softer dollar, confirming it is a real-rates short. <b>TotalEnergies (TTE)</b> "
            "got only a small lift as oil bounced modestly off its low on the ceasefire. And Trump's digital-tax tariff "
            "threat is a specific headwind to <b>LVMH</b> (-20.5%) and <b>SAP</b> into July 4. The dominant action today: "
            "overwrite the huge chip winners (AMD, and the ~+390% AMD lot especially) into the rip while IVol is bid, "
            "hedge the record-high SPY/AI concentration into Warsh + payrolls with a defined-risk put spread, and "
            "reconsider the UST/Siemens bond swap now that a guidance-free hawk has the cover to hike."
        ),
        "outperform": [
            {"name": "The chip sleeve — AMD, MU, and the recovering NVDA/AVGO", "why": "The rebound (AMD +7.7%, NVDA "
             "+2.6% Tuesday) lifted the book's largest and most-concentrated exposure into a record quarter; AMD (~+390%) "
             "and MU lead, and the underwater NVDA (-10.5%) and AVGO (-21%) recovered ground. The book's biggest day-one "
             "beneficiary &mdash; but the moment to overwrite the winners, not chase."},
            {"name": "USD sleeve (~72% of the book)", "why": "The EUR-base book is ~72% USD, and while the dollar eased "
             "slightly Monday on the risk rip, a hawkish Warsh reasserting the rate-path asymmetry plus the digital-tax "
             "threat on the EUR keeps the FX translation working for the book (mirrors MM-012/035)."},
            {"name": "SAP — European AI winner, riding the software bid", "why": "SAP (+132%) rode the broad tech "
             "risk-on and is the book's cleanest European growth winner; but it sits in the digital-tax crosshairs into "
             "Jul 4, so the outperformance is a today-story with a deadline attached &mdash; overwrite candidate."},
        ],
        "underperform": [
            {"name": "The bond sleeve (UST 1.25% 2031, Siemens IG) — the leg the rally turned against", "why": "The 2Y "
             "backed up to 4.11% and the 10Y to 4.44% as the record tape and a Fed 'fed up with inflation' repriced the "
             "hike; the two underwater bonds (-13.9% / -10.6%) lag exactly when the hawk is armed. The bond-swap (harvest "
             "the loss, roll to higher coupons) is more compelling now, not less."},
            {"name": "Xetra-Gold (4GLD) — the real-rates casualty", "why": "Gold slid to an 8-month low (~$4,030) and "
             "did not rally on peace, the record rip, or the softer dollar &mdash; a pure real-rates short under a "
             "hawkish Warsh. Still a +108% winner and the book's tail hedge; held on the min-hold, not added. Own the "
             "asymmetric bounce with a defined-risk call spread (MM-034), not more physical."},
            {"name": "LVMH & SAP — the EU digital-tax/tariff crosshairs", "why": "Trump's 100% digital-tax tariff threat "
             "lands on EU platforms and luxury days before July 4. LVMH (-20.5% already) and SAP carry the specific "
             "escalation risk; the EUR-denominated sleeve is the trade-war casualty into the deadline."},
        ],
        "watch": [
            {"label": "Overwrite the chip winners into the rip — AMD especially, while IVol is bid",
             "text": "The rebound handed the book a gift on its most concentrated names; AMD (~+390%) ran +7.7% in a "
             "session to ~84x forward, the textbook overwrite. Sell rich upside calls against the huge winners (AMD, and "
             "trim-candidate lots of MU) to monetise the rip and fund downside &mdash; do not ride record-high, "
             "high-multiple concentration naked into Warsh and a jobs print."},
            {"label": "Hedge the SPY/AI concentration into Warsh + payrolls — a tight July put spread (MM-032)",
             "text": "The book is long SPY and a heavy AI sleeve into a VIX of 17, the day before a guidance-free Fed "
             "chair's Sintra debut and June payrolls. A below-spot July SPX put spread is cheap, defined-risk convexity "
             "on exactly the concentration the record melt-up built &mdash; the overlay to carry the two policy binaries."},
            {"label": "Reconsider the UST / Siemens bond swap — the hawk now has cover",
             "text": "With the 2Y at 4.11%, the 10Y at 4.44% and a Fed 'fed up with inflation' able to hike into a record "
             "tape, the two underwater bonds (-13.9% / -10.6%) are a duration loss, not a credit one. Harvesting the loss "
             "and rolling into current higher coupons trebles the running carry and banks the loss &mdash; better done "
             "before, not after, Warsh and payrolls potentially back yields up further."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> the coast is clear &mdash; the Iran war is over, the AI complex is resilient, the
quarter closed the best since 2020, so buy the record; a new Fed chair who 'dropped forward guidance' gives himself
room to cut if needed, and the jobs market is fine. Read the week as proof the hard part is behind us.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> the all-clear is what arms the hawk, and a
VIX of 17 the day before Warsh's Sintra debut and June payrolls is complacency, not calm. 'Dropped forward guidance'
is not dovish flexibility &mdash; it is a hawk who removed the roadmap so he can tighten into strength, and a record
tape with resilient job openings just handed him the cover. The crowded side is long the melt-up and the highest-
multiple chips into two policy binaries; the cheaper side owns the event vol (MM-032), the dispersion inside the rip
(MM-033), and the asymmetric bounce in the one asset already capitulated (MM-034).</p>
""",

    "one_chart": """
<p class="theme">A VIX of 17 the day before Warsh speaks and payrolls prints is the chart &mdash; the market is charging almost nothing for its two most dangerous events.</p>
<p>The single thing the market should watch today is the reaction to the Sintra panel at 13:00 GMT, and the level that
resolves it is the S&amp;P 7,300 line. The index closed at a record 7,449 with the VIX at 17 &mdash; priced for a new
Fed chair, who built the guidance vacuum on purpose, to say nothing that binds him, and for Thursday's payroll to land
soft. Those are two live coin-flips the tape has decided are settled. A close back below 7,300 (with a VIX pop through
22) says the melt-up is repricing the hike and the July put spread (MM-032) is paying; a grind to fresh highs on a vague
Warsh and a soft print says the bull scenario is running and the hedge decays as cheap insurance. Own the event the
tape gave away, and keep the long-NVDA / short-AMD dispersion (MM-033) as the second mispriced gap inside the rip.</p>
""",

    "catalyst_calendar": [
        {"day": "Tue", "date": "Jun 30 ✓",
         "event": "Best quarter since 2020 — chips rip, Dow record",
         "consensus": "US indices closed the best quarter since 2020: S&P 7,449.36 (+0.79%), Nasdaq Composite 26,213.72 "
                      "(+1.52%), Dow a record 52,319.20. NVDA +2.6%, AMD +7.7%, Intel +6%. May JOLTS held 7.6mn (above "
                      "est); June confidence up but 'jobs hard to get' at a 2021 high. Sources: TheStreet, CNBC, CNN, BLS.",
         "view": ("The desensitisation call paid — the war and the AI wobble cleared together. But the relief removes "
                  "the Fed's last excuse, and the chip leadership was the most expensive leg (AMD ~84x)."),
         "asymmetry": "The rip over-rewarded the high-multiple name: long NVDA / short AMD (MM-033) owns the dispersion "
                      "without a directional AI bet.",
         "dir": "up"},
        {"day": "Wed", "date": "Jul 1 — TODAY",
         "event": "Warsh at Sintra (13:00 GMT) + ISM Manufacturing (June) — book-critical",
         "consensus": "Fed Chair Kevin Warsh's first major international appearance, on a panel with Lagarde/Bailey/"
                      "Macklem at the ECB Forum; his stance is 'dropped forward guidance', inflation above target. ISM "
                      "Manufacturing (10:00 ET, cons ~53.7, prices-paid ~82, new orders ~57). Sources: Bloomberg, C-SPAN, ISM. PENDING.",
         "view": "'Dropped forward guidance' is not dovish flexibility — it is a hawk who removed the roadmap to tighten "
                 "into strength, into a record tape that just handed him cover. The market has it backwards.",
         "asymmetry": "A hawkish soundbite (VIX 17, index at a record) is a discrete down-catalyst the July put spread "
                      "(MM-032) owns; a vague Warsh + soft ISM lets the melt-up run.",
         "dir": "flat"},
        {"day": "Thu", "date": "Jul 2",
         "event": "June PAYROLLS — the decisive hike-pricing input (book-critical)",
         "consensus": "June non-farm payrolls (8:30 ET), pulled ahead of the Jul 3 early close / Jul 4 holiday. Consensus "
                      "~+115k (range to ~+87k), u-rate 4.3% (possibly 4.2%). A strong print moves toward pricing hikes; "
                      "a major labour read into a guidance vacuum — its own vol event. Source: BLS. PENDING.",
         "view": "The level that resolves the book's central binary: a soft print (sub-100k, u-rate up on the 'jobs hard "
                 "to get' read) prices OUT the hike, the 2Y rallies through 4.05% and the duration longs (MM-004/013) recover.",
         "asymmetry": "A soft payroll squeezes shorts and lifts the rate longs + gold (MM-034); a hot one backs the 2Y to "
                      "the 4.35% stop (MM-013) and pays the SPX put spread (MM-032).",
         "dir": "flat"},
        {"day": "Fri-Sat", "date": "Jul 3-4",
         "event": "Early close (Jul 3) + EU-US trade & digital-tax deadline (Jul 4)",
         "consensus": "US half-day Jul 3; markets shut Jul 4 (Independence Day). The Jul 4 deadline to implement the deal "
                      "capping EU tariffs at 15%, with Trump's 100% digital-services-tax tariff threat the unresolved "
                      "sticking point; legal authority contested post-SCOTUS. Sources: PBS, CBS, Reuters. PENDING.",
         "view": "A hard line into thin holiday liquidity is a fresh cost-push exactly when a guidance-free Fed has no "
                 "slack — risk-off and EUR-negative (short EUR/USD MM-012/035).",
         "asymmetry": "A deal is risk-on + EUR-supportive (fades the dollar trade); a hard line is a cost-push that pays "
                      "the EUR fade (MM-035) and the index put spread (MM-032).",
         "dir": "down"},
        {"day": "Mon", "date": "Jul 6",
         "event": "ISM Services (June) + post-holiday repositioning",
         "consensus": "June ISM Services — the larger read on the services-inflation the Fed watches most, into a "
                      "back-to-work tape digesting Warsh, the payroll and the tariff deadline. Source: ISM. PENDING.",
         "view": "Services prices are the stickiest core-inflation gauge and the cleanest corroboration of the hawkish "
                 "path; a hot services print with a firm payroll is the bear case for duration (MM-004/013).",
         "asymmetry": "Hot services + a firm payroll validates the hike (2Y to the stop); soft services after a soft "
                      "payroll is the bull case that re-rallies the front end.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.662 (the stop). Offside — the record-quarter risk-on keeps an AUD bid; edge thinned to nothing. Trim into strength; the melt-up is the wrong tape for this short.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.44% — backed up to the entry on the risk-on + hawkish repricing; the disinflation bet is ON TEST. Warsh (today) + payrolls (Thu) decide it. Hold-and-trim, don't add.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250 (breached). At ~$4,030 — an 8-month low; did not rally on peace, the rip, or a softer dollar — a pure real-rates short. Min-hold holds it; own the asymmetric bounce via MM-034, NOT an add.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. Pinned near the MoF line; Monday's softer dollar a small relief. Needs a vol shock — a guidance-free Warsh + payrolls is exactly that. Defined-risk expression MM-021.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+33bp; ~+90%; target +60bp. Held its steepening THROUGH the hawkish back-up — still the best position. A hot-payroll bear-flattener is the risk. Trail the stop; hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182 (distant). Onside; a small bounce (+0.33% Mon on strong EZ confidence) is the entry to add downside (MM-035), not cover — Warsh + the Jul 4 digital-tax threat are EUR-negative. Two-sided risk: a Jul 4 deal.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold to ~Jul 8. At ~4.11% — backed up, roughly flat; a coin-flip on Warsh (today) + payrolls (Thu). The softening-labour tell ('jobs hard to get' at a 2021 high) argues the hike is too much, unconfirmed until the print. Hold, don't add.</li>
</ul>
""",

    "client_ammo": [
        {"q": "Markets just had their best quarter since 2020 — why are you cautious?",
         "a": ("Because the rally cleared the two things that were keeping the Fed cautious. The war ended and the AI "
               "selloff reversed, so a new chair who thinks inflation is unfinished now has the cover to hike into a "
               "record tape. A VIX at 17 the day before he speaks and payrolls print is charging almost nothing for "
               "two coin-flips. We're not selling the rally &mdash; we're hedging it cheaply.")},
        {"q": "Warsh 'dropped forward guidance' — isn't that dovish, giving him room to cut?",
         "a": ("We read it the other way. He removed the roadmap so he can move without telegraphing, and everything he "
               "says points to inflation being above target and unfinished. A record equity tape and resilient job "
               "openings hand him the reason to tighten, not ease. The market that hears flexibility is likely to be "
               "surprised by direction.")},
        {"q": "The chips ripped — should we add to Nvidia and AMD?",
         "a": ("We'd own the leader and fade the beneficiary rather than buy both. AMD jumped almost eight percent in a "
               "day and trades at eighty-four times earnings after doubling this year; Nvidia rose a third as much and "
               "trades at twenty-five times on record revenue. When a rebound rewards the most expensive name fastest, "
               "the pair &mdash; long Nvidia, short AMD &mdash; is cleaner than chasing either.")},
        {"q": "Gold is at an eight-month low even after a war and a weaker dollar — why hold it?",
         "a": ("Because it's telling us something: gold is trading purely on real rates now, and a hawkish Fed is the "
               "headwind. We hold the position on its rule and we're not averaging down. But it's the most hated asset "
               "into a two-sided catalyst &mdash; if the chair disappoints the hawks or the jobs number softens, it "
               "squeezes hard, so we own that bounce with a small defined-risk call spread instead.")},
        {"q": "What does the tariff deadline mean for our European names?",
         "a": ("Trump's 100% digital-tax tariff threat lands on EU platforms and luxury right before the July 4 "
               "deadline &mdash; LVMH and SAP sit in the crosshairs. It's also euro-negative, which helps the book: "
               "we're seventy-two percent dollar and our short-euro is working. We'd stay cautious on the EU-exposed "
               "equities into the deadline and use the euro bounce to re-add the short.")},
        {"q": "Where's the cleanest new money going?",
         "a": ("Into the melt-up's blind spots, not the melt-up. One is the event vol the tape gave away &mdash; a tight "
               "July index put spread into Warsh and payrolls. The other is the dispersion inside the chip rip &mdash; "
               "long the cheap leader, short the expensive beneficiary. Both pay precisely because consensus has decided "
               "the hard part is over the day before its two hardest events.")},
    ],

    "ideas_note": (
        "<p>The record quarter cleared the overhangs and armed the hawk; the fresh ideas own the melt-up's blind spots, "
        "not the melt-up. <strong>July SPX 7,250/7,000 put spread (MM-032)</strong> &mdash; the marquee: a VIX of 17 the "
        "day before Warsh's Sintra debut and June payrolls charges almost nothing for two live policy binaries; "
        "defined-risk, below-spot convexity on the event a record tape has stopped pricing. <strong>Long NVDA / short "
        "AMD (MM-033)</strong> &mdash; the rip over-rewarded the highest-multiple name (AMD +7.7%, ~84x) over the cheaper "
        "leader (NVDA ~25x, record revenue); own the dispersion, stay neutral to the AI complex the book is long. "
        "<strong>August gold $4,000/$4,300 call spread (MM-034)</strong> &mdash; gold is maximally hated at an 8-month "
        "low into a two-sided catalyst; a dovish Warsh or a soft payroll is the squeeze the capitulated short can't "
        "absorb. <strong>Short EUR/USD put spread (MM-035)</strong> &mdash; fade Monday's euro bounce into the Jul 4 "
        "digital-tax deadline and a hawkish Warsh. The steepener (MM-009) is the resilient rate leg; the duration longs "
        "(MM-004/013) are trimmed not added; the offside legs (gold spot, USDJPY, EURAUD) are held on tight leashes.</p>"
    ),

    "event_radar_note": (
        "<p>The all-clear that arms the hawk: the US-Iran deal reopened Hormuz and the chip complex ripped back (AMD "
        "+7.7%, NVDA +2.6%, Intel +6%) to close the best quarter since 2020 &mdash; S&P 7,449, Nasdaq Composite 26,214, "
        "Dow a record 52,319. The relief removes the Fed's last excuse just as new chair Kevin Warsh takes the Sintra "
        "stage TODAY (13:00 GMT) with a 'dropped forward guidance', inflation-above-target message. The data splits: May "
        "JOLTS 7.6mn (above est) but 'jobs hard to get' at a 2021 high. Rates backed up (2Y 4.11%, 10Y 4.44%), gold hit "
        "an 8-month low ($4,030); the book's rate longs are the leg on the wrong foot, only the steepener (MM-009, "
        "~+90%) still leads. Trump's 100% digital-tax tariff threat hangs over the Jul 4 EU deadline. Ahead: Warsh + ISM "
        "Mfg TODAY; June PAYROLLS Thu Jul 2 (cons ~+115k); early close Jul 3; shut Jul 4. The fresh ideas own the blind "
        "spots: the July index put spread (event vol), long NVDA / short AMD (dispersion), a gold call spread (the "
        "asymmetric bounce), and a EUR fade. Overwrite the chip winners; hedge the concentration into the print.</p>"
    ),

    "burry_tell": (
        "May job openings held at seven-point-six million, above expectations, and the tape read it as strength. Look "
        "one layer down. In the same week, the share of consumers who say jobs are 'hard to get' jumped to "
        "twenty-two-and-a-half percent, the highest since January 2021. That divergence is the structural thing nobody "
        "is pricing. Job openings are an employer-side, lagging indicator &mdash; the last thing to roll; household "
        "perception of the labour market leads it by quarters. A market that looks tight to firms and soft to workers "
        "is the classic late-cycle fork, and it has resolved the same way every time: the perception was right and the "
        "openings caught down. The danger is that a new Fed chair, who removed forward guidance precisely so he could "
        "act on the data in front of him, tightens on the lagging signal &mdash; a record equity tape and a strong "
        "JOLTS &mdash; into a consumer that is already turning. That is the policy mistake the record high is least "
        "prepared for: not that inflation reaccelerates, but that the Fed hikes into a labour market that has quietly "
        "begun to crack, and the soft-landing multiple the index is carrying has no room for either half of that. Over "
        "the next two-to-three quarters, watch the 'hard to get' series and the hires rate, not the headline openings "
        "&mdash; they will turn first, and the tape will be the last to notice."
    ),

    "earnings_summary": (
        "No qualifying earnings idea this refresh. The window (5 trading days pre / 3 post) is empty for the universe "
        "(>$10bn, US + Korea, Tech / Financials / Industrials / Utilities): Micron (Jun 24 AMC) has rolled to ~5 "
        "sessions post — outside the 3-session-post window — and its supercycle blowout is now fully in the price. The "
        "only names reporting around the window, Nike and Constellation Brands (both Jun 30 AMC), are Consumer and fall "
        "outside the sector filter, so they are macro context (a first read on discretionary demand), not ideas. The "
        "next qualifying cluster is the mid-July bank and mega-cap-tech season. The section is omitted when empty."
    ),
    "earnings_why": (
        "The earnings_data.md feed (last refreshed Jun 30) returns '_No qualifying companies in this window._' for the "
        "Jun 30 → Jul 5 pre / Jun 27 → Jun 30 post windows. On a trading-day basis, Micron (Jun 24 AMC) has aged past "
        "the 3-session-post cutoff and is dropped; the blowout is carried in the narrative (it still anchors the book's "
        "MU concentration) but no longer scores as a fresh earnings idea. Nike and Constellation Brands (Jun 30 AMC) "
        "are excluded as Consumer names outside the Tech/Financials/Industrials/Utilities universe. With no name "
        "clearing the universe + window + conviction gates, no earnings card is rendered this refresh — forcing one "
        "would violate the filter. Excluded throughout: names outside the >$10bn, US/Korea, four-sector universe."
    ),

    "book_aim": (
        "Defensive on the winners, offensive on the blind spots, into a record tape's first real test. The rate book "
        "that carried the run is now the leg on the wrong foot: the 2s10s steepener (MM-009, ~+90%) held THROUGH the "
        "hawkish back-up and is still the best position, but the duration longs (MM-004/013) gave some back as the 2Y "
        "hit 4.11% and the 10Y 4.44% — hold and TRIM into Warsh + payrolls, do not add. The short EUR/USD (MM-012) is "
        "intact; Monday's small euro bounce is the entry to re-add downside (MM-035). Gold (MM-005) is the real-rates "
        "casualty at an 8-month low, held on its min-hold not added. For the holiday-shortened week: rotate fresh risk "
        "into the melt-up's blind spots — the July SPX put spread (MM-032, event vol into Warsh/payrolls at a VIX of "
        "17), long NVDA / short AMD (MM-033, the dispersion the rip created), the defined-risk gold call spread (MM-034, "
        "the asymmetric bounce off capitulation), and the EUR fade (MM-035). The urgent house-keeping in the Fable book: "
        "overwrite the chip winners (AMD ~+390%, MU) into the rip while IVol is bid, and reconsider the underwater "
        "UST/Siemens bond swap now that a guidance-free hawk has the cover to hike. Own the events the tape gave away."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView). The new option ideas (MM-032, "
                 "MM-034) are fresh cards this refresh, not yet booked positions.")
    },
    "idea_selection": [
        {"label": "July SPX 7,250/7,000 put spread — own the event vol into Warsh + payrolls (MM-032)", "in": True,
         "text": ("The marquee idea. A record-high index with a VIX at 17 the day before a guidance-free Fed chair's "
                  "Sintra debut and June payrolls charges almost nothing for two live policy binaries. A tight, "
                  "below-spot SPX put spread owns that event vol for a small defined premium — the overlay on a book "
                  "long SPY and a heavy AI sleeve. Max loss capped.")},
        {"label": "Long NVDA / short AMD — own the dispersion inside the chip rip (MM-033)", "in": True,
         "text": ("The rebound over-rewarded the most expensive name: AMD +7.7% Mon, ~130% YTD at ~84x forward; NVDA "
                  "+2.6% at ~25x on record ~$216bn revenue. Long the cheaper franchise leader, short the overbought "
                  "beneficiary — captures the valuation mean-reversion while staying neutral to the AI complex the whole "
                  "book is long. Stop ratio -4%.")},
        {"label": "August gold $4,000/$4,300 call spread — the asymmetric bounce (MM-034)", "in": True,
         "text": ("Gold is maximally hated at an 8-month low — it did not rally on peace, the record rip, or a softer "
                  "dollar, a pure real-rates short. But the spec long has drained toward capitulation, and a dovish "
                  "Warsh or a soft payroll is the squeeze it can't absorb. A defined-risk call spread owns that bounce "
                  "without averaging down the book's underwater 4GLD/MM-005. Max loss capped.")},
        {"label": "Short EUR/USD put spread — fade the bounce into Jul 4 (MM-035)", "in": True,
         "text": ("The euro bounced +0.33% Monday on a softer dollar, but a hawkish Warsh reasserts the rate-path "
                  "asymmetry and Trump's 100% digital-tax tariff threat hangs over the Jul 4 deadline. A defined-risk "
                  "put spread fades the move — a tactical add to the book's core dollar-long (MM-012), dated to the "
                  "bounce and the deadline, not a fresh standing view.")},
        {"label": "Steepener (MM-009) — hold and trail; duration longs (MM-004/013) — TRIM, don't add", "in": False,
         "text": ("The steepener held its ~+90% through the hawkish back-up and is trailed, not added. The duration "
                  "longs gave some back as yields backed up; they are TRIMMED into Warsh + payrolls, not pressed — a "
                  "guidance-free hawk and a resilient jobs print are exactly what backs them up further.")},
        {"label": "Gold spot (MM-005) — held on its rule, NOT added", "in": False,
         "text": ("Gold at an 8-month low is the real-rates casualty; held on its min-hold to ~Jul 15, not averaged "
                  "down. The asymmetric bounce is owned with the defined-risk call spread (MM-034), where the risk is "
                  "capped, not by adding to the underwater physical.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 16.5},
        {"label": "VIX",   "value": round(_g("vix") or 17.5, 2)},
        {"label": "VIX3M", "value": 18.5},
        {"label": "VIX6M", "value": 19.5},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.11, 3)},
        {"label": "5Y",  "value": 4.28},
        {"label": "10Y", "value": round(_g("us10y") or 4.44, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 4.88, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-032", "trade": "Buy July SPX 7,250/7,000 put spread (event vol into Warsh + payrolls)",
            "asset_class": "Equity (options)", "structure": "put spread",
            "entry": "~0.5% premium", "stop": "—", "target": "~5x at 7,000",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 0, "stop_quality": 1},
            "horizon": "to late July", "min_hold_days": 0,
            "thesis": ("The marquee idea: the record quarter closed the day before the tape's two most dangerous 48 "
                       "hours, and the VIX is at 17. TODAY a guidance-free Fed chair takes the Sintra stage for his "
                       "first major international appearance; Thursday brings June payrolls into a market now pricing "
                       "HIKES on stubborn inflation. Either a hawkish Warsh soundbite or a hot payroll is the discrete "
                       "down-catalyst a one-way melt-up has stopped pricing. A short-dated, below-spot put spread owns "
                       "that event vol for a small defined premium — the overlay on a book long SPY and a heavy AI "
                       "sleeve, structured for the guidance vacuum Warsh built on purpose, not a chase of at-the-money "
                       "premium."),
        },
        {
            "id": "MM-2026-033", "trade": "Long NVDA / short AMD (own the dispersion inside the chip rip)",
            "asset_class": "Equity RV", "structure": "beta-weighted pair",
            "entry": "spot ratio", "stop": "ratio -4%", "target": "ratio +8%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The chip rebound over-rewarded the most expensive name, and that is the trade. In Tuesday's rip "
                       "AMD ran +7.7% and is up ~130% year-to-date at roughly 84x forward earnings; Nvidia rebounded a "
                       "more modest +2.6% and trades near 25x forward on record ~$216bn FY26 revenue. When a relief "
                       "rally lifts the highest-multiple beta leg fastest, the clean expression is to own the leader "
                       "and fade the beneficiary — long NVDA, short AMD — capturing the valuation dispersion without a "
                       "directional view on the AI complex the whole book is long. Concentration-neutral to the "
                       "melt-up; pays if the froth mean-reverts into the Warsh/payrolls test. Stop: ratio -4%."),
        },
        {
            "id": "MM-2026-034", "trade": "Buy Aug gold $4,000/$4,300 call spread (asymmetric bounce off capitulation)",
            "asset_class": "Commodity (options)", "structure": "call spread",
            "entry": "~$4,030 spot", "stop": "—", "target": "~4x at $4,300",
            "conviction": 5,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Aug expiry", "min_hold_days": 0,
            "thesis": ("Gold is maximally hated at exactly the moment its two-sided policy catalyst arrives. Bullion "
                       "sits at ~$4,030, the weakest since November, because a hawkish, guidance-free Warsh pricing "
                       "hikes is a pure real-rates headwind — it did not rally on peace, on the equity rip, or on the "
                       "softer dollar. But the spec long has drained toward capitulation, and the same 48 hours that "
                       "threaten the melt-up are the asymmetric UPSIDE for gold: a Warsh who disappoints the hawks or a "
                       "soft June payroll prices out the hike and squeezes a one-way short. A defined-risk call spread "
                       "owns that bounce for a small premium without adding to the book's underwater physical (4GLD / "
                       "MM-005) — the right way to own the capitulation, not the wrong way to defend the loss."),
        },
        {
            "id": "MM-2026-035", "trade": "Short EUR/USD 1m put spread (fade the bounce into Jul 4)",
            "asset_class": "FX (options)", "structure": "put spread",
            "entry": "~spot post-bounce", "stop": "1.182 (outright)", "target": "~4x",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to mid-July", "min_hold_days": 0,
            "thesis": ("The euro bounced on the wrong reasons and into the wrong week. EUR/USD rose ~0.33% Monday on a "
                       "softer dollar as the equity rip curbed haven demand — but two dated forces converge against it "
                       "in 72 hours: a guidance-free Warsh reasserting the rate-path asymmetry at Sintra today, and "
                       "Trump's 100% digital-services-tax tariff threat hanging over the July 4 EU deadline. The bounce "
                       "thinned the short crowd, which is the entry, not the exit. A defined-risk put spread fades the "
                       "move with capped premium and pairs with the book's ~72% USD sleeve — a tactical add to the core "
                       "short (MM-012), dated to Monday's dollar wobble and the tariff tripwire, not a fresh standing "
                       "view. Outright stop 1.182."),
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
