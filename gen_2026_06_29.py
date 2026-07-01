#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-29 (Monday). STRIKES WITHOUT A PREMIUM.

THE NEXT CHAPTER vs the Jun 26 (Chips Bite Back) run: the Gulf went kinetic over the weekend and
the market REFUSED to price it. The AI-inflation regime carries forward; a shooting war gets layered
on top and oil FELL anyway.
- THE GULF WENT KINETIC. Sat Jun 27 the US struck five Iranian coastal sites (missile/drone/radar/
  air-defense/minelayer) in retaliation for an alleged Iranian drone attack on a cargo ship in
  Hormuz (Thu Jun 25). Sun Jun 28 Iran fired ballistic missiles + drones at the US Ali Al Salem Air
  Base (Kuwait) and the US Fifth Fleet HQ (Bahrain). Trump: Iran "will no longer exist" if strikes
  continue, threatened to "complete the job"; Vance: "violence will be met with violence." Then a US
  official said the two sides would "stand down for now." The Jun 17 ceasefire MoU is fragile but
  holding. (CNN, Al Jazeera, NBC, RFE/RL.)
- THE TELL: OIL FELL ON US STRIKES ON IRAN. Brent Aug settled $71.99 (-4.34%) Fri, WTI $69.23
  (-3.74%) — the lowest since Feb 27 — as Hormuz transits ACCELERATED to ~75% of prewar volume.
  The market has fully desensitised to the Hormuz tail: flows kept recovering through the fighting,
  so missiles between the US and Iran moved crude DOWN, not up. (CNBC, OilPrice.)
- MONDAY FUTURES RIPPED ON THE "STAND DOWN." ES +0.5%, NQ +0.6%, YM +0.3% premarket as the halt
  to US-Iran attacks was called. Risk-on melt-up resumes into a holiday-shortened, quarter-end week.
  (Yahoo Finance.)
- FRIDAY WAS A 5TH STRAIGHT NASDAQ LOSS. Jun 26 close: S&P 7,354.02 (-0.05%), Nasdaq Composite
  25,297.62 (-0.24%, 5th down day), Dow 51,876.11 (-0.09%) — a global tech sell-off on AI
  data-center costs + a reported OpenAI IPO delay. The silicon-inflation story (Micron blowout +
  Apple/Microsoft +15-25% hardware hikes, DRAM +98% YTD) is still the structural backdrop. (TheStreet, CNBC.)
- TRUMP OPENED A SECOND TARIFF FRONT. Sun Jun 28 on Truth Social he threatened 100% tariffs on any
  country imposing a digital services tax on US companies (aimed at the EU): the tariff "will
  supersede trade deals... immediately imposed." A fresh cost-push days before the Jul 4 EU deadline.
  (CNBC, Social Media Today.)
- GOLD BARELY MOVED. ~$4,040, up a second session post-PCE — a muted haven bid even on literal
  strikes, the clean tell that gold is trading as a real-rates short, not a war hedge. The book's
  long (MM-005) is ~-10%, held on its min-hold to ~Jul 15. (Trading Economics.)
- RATES STEADY, DOLLAR HIGH. 10Y ~4.39%, 2Y ~4.09%, 2s10s ~+27-30bp; DXY at a 13-month high;
  EUR/USD ~1.143; VIX ~18.9. The rate longs (MM-004/013) green, the steepener (MM-009) ~+80%, short
  EUR/USD (MM-012) vindicated. Sep-hike odds split: CME ~73% vs prediction markets ~44%. (CNBC, FXStreet.)
- ASIA/EUROPE SOLD THE AI TAPE. Nikkei -2.65% on the week, Shanghai -2.26% to 4,027, HSCEI into a
  bear market; DAX -1.0% to 24,894 (Infineon -6.3%), Germany Composite PMI 48 (3rd monthly fall),
  euro-area Flash Composite 49.5 (best since March). BTC ~$60.4k. (T. Rowe, Trading Economics.)
- WEEK AHEAD: Jun 29 quiet (quarter/half-end); Jun 30 consumer confidence + JOLTS + Nike (Q4) &
  Constellation Brands AMC; ISM Mfg Jul 1; June PAYROLLS pulled to Thu Jul 2 (Jul 3 early close,
  Jul 4 holiday); EU-tariff deadline Jul 4.
- BOOK ACTION: MM-008 was banked Jun 27 (~+29%). The fresh marquee idea is the mispriced war tail —
  a Brent call spread (MM-031) the tape is giving away at $69 even as missiles fly. Collar the 32%
  Micron; the silicon-inflation breakeven long (MM-027) carries. Energy hedge (TTE) the book laggard.

Run:  python gen_2026_06_29.py
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
# web-verified Jun-25 closes (corroborated TheStreet + CNBC) so the dashboard headline indices
# never render "unverified". Only set if the live feed did not resolve them.
if "spx" not in snap:
    snap["spx"] = {"close": 7357.49, "chg_pct": -0.01, "chg_abs": -0.74}
if "dji" not in snap:
    snap["dji"] = {"close": 51920.62, "chg_pct": 0.14, "chg_abs": 72.0}
levels = live_levels.trade_levels(snap)
# Option spreads have no live feed — mark from spot. MM-008 (SPX put spread) was BANKED Jun 27 at
# ~$45 (~+29%) and now sits in the closed ledger; no live option line is open this refresh. The fresh
# index downside is the August 7,000/6,600 put spread (MM-030) and the Brent call spread (MM-031).

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
    "MU":   "Still the book's LARGEST position (~32.2%) and the structural backdrop: the Jun 24 blowout (EPS $25.11 vs "
            "$21.40, tightness 'locked in beyond 2027') confirmed the supercycle, but the AI tape sold off into the "
            "weekend (Nasdaq's 5th down day on data-center-cost worries). A confirmed catalyst on a third of the book "
            "into a jittery tape is the moment to COLLAR and lock the gain, not chase. The fresh leg is the memory-vs-"
            "OEM RV (MM-028): own the pricing power, short who pays for it.",
    "NVDA": "The demand engine of the DRAM shortage, and the reason the AI complex sold for a week — every HBM wafer is "
            "an input-cost story for the cohort and a data-center-cost worry for the index. An OVERBOUGHT print is the "
            "AI-capex bid; an OVERSOLD one is the cost-overhang fade, not a fresh long. Own the second-order inflation "
            "read (MM-027) over another chase of the leader.",
    "AAPL": "The clean tell of the silicon-inflation regime: Apple raised Mac/iPad prices up to $300 and named the "
            "AI-DRAM shortage, then led the Mag7 lower. The box-maker eats the memory cost it cannot fully pass through "
            "into a -11% PC / -13% phone year. AAPL/HPQ/DELL are the margin casualties — the SHORT leg of the memory RV "
            "(MM-028). Oversold is a value trap while the input cost is still climbing.",
    "XLE":  "The tape's loudest tell this weekend: the US and Iran traded missile strikes and crude FELL — Brent "
            "$71.99 / WTI $69.23, the lowest since February — as Hormuz transits ran at ~75% of prewar. The war "
            "premium is not just drained, it is NEGATIVE: the market gives the Hormuz tail away. Energy length is the "
            "disinflation drag, but the cheap, defined-risk way to own the mispriced re-escalation is the Brent call "
            "spread (MM-031), not the equity ETF.",
    "GLD":  "Gold barely moved on literal US strikes on Iran — ~$4,040, up a muted second session post-PCE. That is "
            "the tell: bullion is trading as a real-rates short, not a war hedge, with a 13-month-high dollar and a "
            "hawkish Fed the dominant engine. We OWN it (MM-005 / the book's 4GLD) ~-10%, held on the min-hold to "
            "~Jul 15. Not an add; own the war tail in OIL (MM-031) where it is mispriced, not gold where it is not.",
    "TLT":  "Duration is holding its rescue: despite a hot PCE (4.1%/3.4%) and a Fed the CME prices ~73% to hike in "
            "September, the 2Y sits ~4.09% and the 10Y ~4.39% as the bond market trades the energy/goods disinflation "
            "over the dots. We are long via the short-2Y book (MM-013, GREEN), the 10Y (MM-004, green) and the "
            "steepener (MM-009, ~+80%). The silicon-inflation (MM-027) is the offsetting risk — hold, don't press.",
    "XLF":  "Financials remain the rate-regime equity winner: a no-cuts, higher-for-longer Fed and a still-elevated "
            "front end lift net-interest margins while the AI-multiple cohort carries the memory-cost overhang and a "
            "week of selling. Own the margin beneficiary against the multiple-and-input-cost casualty rather than "
            "chasing the narrow quarter-end melt-up.",
    "BTC":  "Bitcoin ~$60.4k, capped below the $61-62k repair zone after the late-June liquidation — the same "
            "dollar-strength, real-rates regime that pins gold. A 13-month-high dollar is the macro headwind; oversold "
            "is not a signal while the rotation favours US dollar assets. Not a book position; a tell that the "
            "liquidity bid is concentrating, not broadening.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("Strikes Without a Premium: The Gulf Goes Kinetic and the Tape Refuses to Price It — "
          "a Quarter-End Melt-Up Layered on a Desensitised War Tape and a Silicon-Inflation Backdrop")
regime_note = (
    "The most important thing that happened this weekend is what did NOT happen. The US struck five Iranian coastal "
    "sites on Saturday; Iran answered Sunday with ballistic missiles and drones at the US air base in Kuwait and the "
    "Fifth Fleet headquarters in Bahrain; Trump warned Iran 'will no longer exist' if the strikes continue and "
    "threatened to 'complete the job' — and crude FELL. Brent settled the week at $71.99 and WTI at $69.23, the "
    "lowest since February, because Hormuz transits accelerated to roughly seventy-five percent of prewar volume "
    "even as the missiles flew. The second-order effect consensus is missing is the desensitisation itself: the "
    "market has stopped pricing the Strait of Hormuz, so a shooting war between the US and Iran moved oil DOWN, and "
    "by Monday futures were higher (ES +0.5%, NQ +0.6%) on a 'stand down for now.' The single cheapest tail in the "
    "market is now the energy upside the tape is giving away. (CNN, Al Jazeera, CNBC, OilPrice, Yahoo Finance.) "
    "Decompose what is actually driving the melt-up. The consensus reads risk-on into quarter-end as confirmation "
    "the world is calm — a Gulf ceasefire holding, the AI complex resilient. The anatomy says the opposite: Friday "
    "was the Nasdaq's fifth straight down day on AI-data-center cost worries and an OpenAI IPO delay, the S&P closed "
    "at 7,354.02 and the Composite at 25,297.62, and the structural backdrop is still the silicon-inflation the prior "
    "session exposed — Micron's blowout (EPS $25.11 vs $21.40, tightness 'locked in beyond 2027') and the Apple/"
    "Microsoft hardware hikes of 15-25% are the same DRAM shortage, with memory up 98% this year. The melt-up is "
    "narrow and the index is being carried over a tape that sold tech for a week. (TheStreet, CNBC.) "
    "Trace the political layer, because there are now two cost-push fronts running into one deadline. On Sunday Trump "
    "threatened 100% tariffs on any country imposing a digital services tax on US companies — aimed at the EU, the "
    "tariff to 'supersede trade deals' and be 'immediately imposed' — days before the July 4 EU deadline that already "
    "carried an autos-to-25% threat. A geopolitical cost-push (oil, were the desensitisation to break) and a trade "
    "cost-push (tariffs) both converge on a Fed with no slack to absorb either, because the silicon-inflation already "
    "has core goods sticky. (CNBC, Social Media Today.) "
    "The book sits on the right side of the bond market's quiet disagreement with the Fed. Despite a hot May PCE "
    "(4.1%/3.4% core) and a September hike the CME prices near 73%, the 2Y holds ~4.09% and the 10Y ~4.39%, the "
    "steepener (MM-009) is up ~+80% and the duration longs (MM-004/013) are green; the dollar at a 13-month high "
    "vindicates the short EUR/USD (MM-012). Gold barely moved on literal strikes — the cleanest tell that bullion is "
    "a real-rates short now, not a war hedge — so the long (MM-005) is held, not added. "
    "The week is holiday-shortened: a quiet, quarter-and-half-end Monday; consumer confidence, JOLTS and Nike/"
    "Constellation earnings Tuesday; ISM Wednesday; and June payrolls pulled forward to Thursday July 2 — the first "
    "labour read in the guidance vacuum — ahead of the July 4 tariff deadline. The regime is no longer about whether "
    "the war reprices oil. It is that the market has decided no shock sticks — and the trade is to own the tail it is "
    "giving away while staying long the disinflation the curve is finally pricing."
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
            "The quiet leg, and it has drifted back to roughly flat-to-offside near 1.651 as the AUD finds a bid the "
            "trade did not want. A paused ECB still caps the EUR side, but the Micron-led risk-on rebuilt the "
            "commodity-currency bid even as the broad metals complex (gold sub-$4,000) collapsed — a split that leaves "
            "the cross grinding higher toward the 1.662 stop rather than toward the 1.61 target. There is no dated EUR "
            "catalyst left; the edge has thinned, and this is the leg to trim into strength rather than defend. "
            "Patience, but a tight leash — the stop is ~11 pips away."
        ),
        "catalysts": [
            "ECB pause now fully in the price — no forward EUR catalyst",
            "Risk-on rebound (Micron) — rebuilt the commodity-AUD bid, the force AGAINST the short",
            "RBA path — a hawkish hold supports AUD vs a paused ECB",
            "Iron ore / China demand — the AUD swing factor (China PMI Jun 30)",
        ],
        "risks": (
            "The AI-led risk-on keeps bidding AUD and the cross runs the 1.662 stop; a firm China PMI lifts iron ore; "
            "an ECB official re-opens the hike door and EUR squeezes the other way. Stop 1.662 (~11 pips)."
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
            "Rescued and now green. The 10Y has rallied to ~4.37% from the 4.499% post-FOMC spike — through the 4.44% "
            "entry — for the cleanest possible reason: the bond market is trading the energy disinflation and the "
            "goods slowdown OVER the hawkish dots and the hot May PCE. Brent at $74, gold sub-$4,000 and a -11% / -13% "
            "PC-and-phone shipment year are the forward-disinflation signals that say the Fed's May inflation read is "
            "backward-looking. The live risk to the thesis is the silicon half of the inflation it would otherwise "
            "ignore — a DRAM-driven core-goods stickiness — so harvest, do not press. Stop 4.65%, now ~28bp away."
        ),
        "catalysts": [
            "Brent $74 + gold sub-$4,000 = the energy/commodity disinflation the long end is rallying on",
            "June payrolls Jul 2-3 — the first labour read in the guidance vacuum; a soft print extends the rally",
            "Silicon-push goods inflation (DRAM +98%) — the term-premium risk AGAINST the position",
            "Treasury supply + quarter-end duration extension — the offsetting flows into month-end",
        ],
        "risks": (
            "The silicon-inflation (MM-027) overwhelms the energy disinflation and core goods re-accelerate; the long "
            "end sells on fiscal supply and a wider term premium; a hot payroll Jul 2-3 reprices the hike. "
            "Stop 4.65% (now ~4.37%, ~28bp away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the Brent-$74 / gold-sub-$4k disinflation widens the gap vs the Fed's hawkish path; "
                            "the silicon-inflation is the partial offset that caps the gap.",
            "catalyst":     "1/2 — payrolls Jul 2-3 is the next dated catalyst; the FOMC has passed.",
            "positioning":  "1/2 — consensus is still short duration post-Warsh; the rally is squeezing it, fuel remains.",
            "confirmation": "2/2 — the 10Y rallied THROUGH the entry on a hot PCE; the contrarian thesis is confirming.",
            "stop_quality": "1/1 — 4.65% is a clear technical level; ~28bp of risk.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold in USD. The inverse of real rates, driven by the Fed path "
            "and real yields, USD strength, EM central-bank buying, geopolitical premia, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "The casualty. Both engines drained at once and gold broke $4,000 for the first time since November — now "
            "~$4,015, down ~29% from the January $5,608 peak and ~-11% from the $4,523 entry. The real-rates engine "
            "lost to a hawkish Fed and a 13-month-high dollar; the safe-haven engine lost to the Iran de-escalation; "
            "and $2bn of May ETF outflows confirm the spec long is leaving. The price is BELOW the $4,250 stop, but "
            "the 45-day min-hold (to ~Jul 15) keeps a pre-position structural trade open through the drawdown — the "
            "rule that protects against a wash-out bottom is the rule taking the pain here. NOT an add; the route back "
            "is the defined-risk GLD put-spread hedge (MM-029), not averaging down a falling knife."
        ),
        "catalysts": [
            "Hawkish Fed + DXY 13-month high — the real-rates / dollar headwind, the dominant force against gold",
            "Iran de-escalation — the safe-haven premium that has drained out (a fracture is the only upside tail)",
            "$2bn May gold-ETF outflows — the spec long unwinding under the price",
            "EM / central-bank physical buying (China, India, Turkey) — the structural floor being tested now",
        ],
        "risks": (
            "The silicon-inflation does NOT translate into a real-rates relief and the metals rout extends below "
            "$3,900; the dollar pushes higher; ETF outflows accelerate. The min-hold keeps it open to ~Jul 15 — the "
            "stop is breached, the rule is what holds it; hedge via MM-029."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the real-rates and safe-haven engines both reversed; only the central-bank / "
                            "debasement floor remains, a much narrower mispricing than at entry.",
            "catalyst":     "0/2 — no near-term catalyst favours the long; the Iran tail is the only one, and it faded.",
            "positioning":  "1/2 — the spec long is unwinding (ETF outflows); positioning is cleaner but not yet capitulatory.",
            "confirmation": "0/2 — the trend broke $4,000 decisively; the chart contradicts the long.",
            "stop_quality": "1/1 — $4,250 is a defined level (now breached); the min-hold rule is the discipline holding it.",
        },
    },
    "MM-2026-007": {
        "instrument": (
            "USD/JPY spot FX (dollar-yen). Driven by the US-Japan 2yr rate differential, BoJ "
            "normalisation, the Fed path, risk sentiment (JPY is a crisis safe-haven), and Japanese "
            "MoF intervention risk near ~160-163."
        ),
        "fundamental_thesis": (
            "Pinned, not punished. The hawkish Fed widened the rate differential — the textbook reason for USD/JPY to "
            "break higher — yet the pair held near 160.3, capped at the MoF intervention line where the carry trade "
            "meets the official backstop. The short is roughly flat, frustrated by the same crushed-carry dynamic and "
            "now braced against a wider differential. The structural case (a BoJ that just hiked to 1.00%, a Fed whose "
            "oil-disinflation argues its hawkishness is misplaced) is intact, and the trade needs vol to break the "
            "carry — which a guidance-less Fed is now structurally more likely to deliver. Patient short with 163 as "
            "the backstop; the defined-risk way to own the tail is MM-021."
        ),
        "catalysts": [
            "MoF intervention at the 160 line — explicit warnings; physical action forces stop-hunting",
            "Hawkish Fed widening the differential — the force AGAINST the short near-term",
            "A guidance-less Fed re-rating vol — the catalyst that reactivates the carry unwind",
            "Japan CPI / BoJ guidance — further normalisation supports the yen",
        ],
        "risks": (
            "The hawkish-Fed differential pushes USD/JPY through 161-162 and toward the 163 stop before the MoF acts; "
            "vol stays crushed and the carry trade persists. Stop 163.00."
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
            "The best position in the book, and re-steepening. The spread has widened back toward ~+28bp as the front "
            "end (2Y to ~4.09%) rallied harder than the back end on the energy-disinflation bid — the open gain sits "
            "near +85% off the +15bp entry (an 18-month inversion). The medium-term thesis is intact and reinforced: a "
            "Fed pricing a hike into a goods-and-energy disinflation eventually reverses, which re-steepens through the "
            "front end, while the guidance vacuum keeps a term premium under the back end. The silicon-inflation is the "
            "two-sided risk — if core goods re-accelerate, the front end backs up and flattens it again. Min-hold to "
            "~Jul 16; target +60bp; held, trail the stop up, not added."
        ),
        "catalysts": [
            "Front-end rally on the energy/goods disinflation — the re-steepening engine working now",
            "June payrolls Jul 2-3 — a soft labour print fades the hike pricing and steepens further",
            "Guidance-vacuum term premium + Treasury supply — keeps the back end heavy = steepens",
            "Silicon-push core-goods inflation — the risk that re-flattens via a front-end back-up",
        ],
        "risks": (
            "The DRAM-driven goods inflation reprices a Sep hike and the front end backs up, bear-flattening the curve "
            "again; a global safe-haven bid flattens via the long end. Stop: spread below -10bp (now ~+28bp)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve is still structurally underpriced vs the late-cycle mean off an 18-month "
                            "inversion; the re-steepening has room to the +60bp target.",
            "catalyst":     "2/2 — payrolls Jul 2-3 is a live, dated front-end catalyst; the energy disinflation is steepening it now.",
            "positioning":  "1/2 — front-end positioning is still hawkish post-Warsh; the rally is squeezing it.",
            "confirmation": "2/2 — the spread widened back to ~+28bp on the front-end rally; the re-steepen is confirming.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "Vindicated and extending. EUR/USD is ~1.138 with DXY at a 13-month high near 101.4 — the dollar breakout "
            "that started on Warsh's hawkish dots has become a durable regime, not a one-day spike. The rate-path "
            "asymmetry (a Fed pricing a hike vs a paused ECB) is reinforced by the AI-led capital pulling money into "
            "US assets and out of crypto and gold. It pairs cleanly with the book's European-equity tilt and hedges "
            "the ~72% USD sleeve. Hold toward 1.13; the defined-risk way to add downside is the EUR/USD put spread "
            "(MM-024). The two-sided risk is the July 4 EU-tariff deadline — a deal is EUR-supportive. Stop 1.182, distant."
        ),
        "catalysts": [
            "Hawkish Fed vs paused ECB + 13-month-high dollar — the rate-path asymmetry firmly dollar-positive",
            "AI-led US capital concentration — the second engine pulling the dollar higher (out of BTC/gold)",
            "Spec positioning unwind — EUR longs near multi-year highs are the squeeze fuel",
            "EU-US tariff deal by July 4 — the offsetting EUR-supportive force to watch",
        ],
        "risks": (
            "A clean EU-US tariff deal and broad risk-on lifts EUR; US data rolls over hard and the dollar fades; an "
            "ECB official re-opens the hike door. Stop 1.182 (now ~4 figures away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the rate-path asymmetry the trade priced has widened further; the dollar holds its "
                            "break and the mispricing keeps resolving in the position's favour toward 1.13.",
            "catalyst":     "2/2 — the dollar regime is confirmed; the July 4 tariff deadline is the next dated catalyst.",
            "positioning":  "1/2 — EUR spec longs near multi-year highs provide further unwind fuel.",
            "confirmation": "2/2 — EUR/USD holds below 1.14 and DXY at a 13-month high; confirmed.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; the position has a wide cushion now.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receive 2Y swap / long 2Y notes). The 2Y is the market's "
            "real-time forecast of the Fed path over two years — the most policy-sensitive point on the "
            "curve."
        ),
        "fundamental_thesis": (
            "The trade the Fed shot at — and the tape caught. The thesis was that the front end over-priced a 2026 "
            "hike; Warsh penciled one and the 2Y spiked to 4.216%, but it has since rallied all the way back to "
            "~4.09% — through the 4.162% entry — so the position is now GREEN. The fade is the thesis confirming: even "
            "into a hot May PCE and 68% Sep-hike odds, the bond market is pricing the energy disinflation and the "
            "goods slowdown over the dots. The contrarian case (a Sep hike priced into a falling-oil, slowing-goods "
            "tape unwinds) is paying. The live offset is the silicon-inflation (MM-027) that could yet validate the "
            "hike. Min-hold to ~Jul 8; stop 4.35%, now ~26bp away. Harvest, do NOT add into payrolls."
        ),
        "catalysts": [
            "Energy/commodity disinflation (Brent $74, gold sub-$4k) — argues the Fed's hawkish path is too high",
            "June payrolls Jul 2-3 — a soft labour print prices OUT the Sep hike and extends the rally",
            "The Sep meeting — where the penciled hike gets confirmed or priced out",
            "Silicon-push core-goods inflation / a hot payroll — the risk that confirms the hawkish dots",
        ],
        "risks": (
            "The DRAM-driven goods inflation re-accelerates core and a hot payroll Jul 2-3 fully prices the Sep hike, "
            "sending the 2Y to the 4.35% stop. Stop 4.35% (now ~4.09%, ~26bp away); min-hold to ~Jul 8."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the energy disinflation re-widens the gap between the 2Y and the justified hike "
                            "probability, but the silicon-inflation is the partial offset.",
            "catalyst":     "2/2 — payrolls Jul 2-3 is the dated, decisive front-end catalyst; the FOMC has passed.",
            "positioning":  "2/2 — the market is maximally positioned for the hawkish Warsh; squeeze fuel on any soft print.",
            "confirmation": "2/2 — the 2Y rallied THROUGH the entry on a hot PCE; the contrarian thesis is confirming.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~26bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-027": {
        "instrument": (
            "Long US 2-year inflation breakevens — buy 2Y TIPS / sell the 2Y nominal (or long a short-dated "
            "breakeven swap). Pays if realised + expected inflation runs above what the front-end nominal "
            "prices. The market reads the oil collapse as pure disinflation; this owns the silicon-push it misses."
        ),
        "fundamental_thesis": (
            "The marquee idea: the composition of inflation just flipped and the breakeven curve has not noticed. The "
            "tape is trading Brent at $74 and gold sub-$4,000 as a clean disinflation, pulling front-end breakevens "
            "down — but the May PCE that printed 4.1% / 3.4% core is being replaced, not ended, as an inflation engine. "
            "DRAM is up 98% this year, Apple and Microsoft just repriced consumer hardware 15-25%, and that goods "
            "inflation feeds core PCE for quarters because the AI build-out that causes it has a multi-year lead time. "
            "Long 2Y breakevens owns the silicon-push the market is mistaking for disappearing inflation, and it is "
            "the inflation hedge a book long both duration (MM-004/013) and the AI complex otherwise lacks."
        ),
        "catalysts": [
            "May PCE 4.1% / 3.4% core (released) — the hot reading the breakeven curve is fading too quickly",
            "DRAM +98% / consumer-hardware price hikes — the forward core-goods inflation feeding through H2",
            "June payrolls + ISM prices-paid (Jul 1-3) — the next dated reads on goods/services inflation",
            "A second oil leg lower — the offsetting force that keeps headline breakevens capped near-term",
        ],
        "risks": (
            "The energy disinflation dominates and headline breakevens fall faster than core goods rise; a demand "
            "shock (the -11% PC / -13% phone slowdown) turns the goods story into deflation; the carry bleeds. "
            "Stop: 2Y breakeven 20bp below entry."
        ),
        "breakdown_why": {
            "gap":          "3/3 — the market prices the oil collapse as disinflation and ignores the silicon-push; the "
                            "mispricing between the breakeven curve and the DRAM-driven goods inflation is wide.",
            "catalyst":     "2/2 — May PCE is on the tape today; payrolls/ISM prices land Jul 1-3 — dated and live.",
            "positioning":  "1/2 — breakevens sit near cycle lows as the crowd shorts inflation on oil; some squeeze fuel.",
            "confirmation": "1/2 — the hot PCE confirms the level, but oil clouds the near-term breakeven read.",
            "stop_quality": "1/1 — a 20bp breakeven stop is a clean, defined level.",
        },
    },
    "MM-2026-028": {
        "instrument": (
            "Equity RV — long the memory/Micron complex (SOXX or MU) vs SHORT a PC/handset-OEM basket "
            "(Dell, HP, and the hardware sleeve of XLK). A ratio that rises when the memory-makers' pricing "
            "power outruns the box-makers who eat the DRAM cost. The book already holds the long leg via MU."
        ),
        "fundamental_thesis": (
            "The DRAM supercycle is a margin transfer, and the market is only pricing one side of it. Micron just "
            "printed a record quarter on memory tightness 'locked in beyond 2027'; the same shortage forced Apple to "
            "raise the MacBook $200 and Microsoft the Xbox $150, into a year where PC shipments fall 11% and phones "
            "13%. The memory-makers capture the price; the OEMs eat the input cost AND the volume decline. The book is "
            "already long the winners (MU, ~32.2%), so the un-owned, fresh leg is the SHORT — Dell, HP and the "
            "hardware OEMs that cannot fully pass the cost through. Express it as the RV to stay concentration-neutral "
            "to the index: long who sets the price, short who pays it."
        ),
        "catalysts": [
            "Micron's 'tightness beyond 2027' guide — confirms the memory-maker pricing power (the long leg)",
            "Apple/Microsoft hardware price hikes + 15-20% OEM contract resets — the OEM margin squeeze (the short)",
            "PC -11% / smartphone -13% 2026 shipment forecasts — the volume decline compounding the cost hit",
            "Q2 OEM earnings (July) — confirmation the input-cost hit is landing on the box-makers' margins",
        ],
        "risks": (
            "The OEMs pass the cost through cleanly and protect margin; a demand recovery lifts hardware volumes; the "
            "memory cycle rolls over faster than guided and the long leg de-rates. Stop: ratio -4% from entry."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the margin-transfer divergence is real and freshly evidenced, but partly visible in "
                            "the memory-maker re-rate already.",
            "catalyst":     "1/2 — the price hikes are dated; the margin impact shows up gradually over Q2 OEM prints.",
            "positioning":  "2/2 — the crowd is long the AI/memory winners and under-short the OEM casualties.",
            "confirmation": "1/2 — Micron's blowout and the AAPL/MSFT hikes wrote the first leg; one confirming move.",
            "stop_quality": "1/1 — a fixed ratio stop (-4%) is a clean, defined failure threshold.",
        },
    },
    "MM-2026-031": {
        "instrument": (
            "Buy a Brent September $80/$90 call spread — defined-risk upside on crude (tradeable via Brent "
            "futures options or a USO/BNO call spread). Buy the $80 call, sell the $90 call. Owns the "
            "Hormuz re-escalation tail with capped premium; max loss is the premium. With Brent ~$72 spot, "
            "both strikes are out-of-the-money — cheap convexity on the war the market has stopped pricing."
        ),
        "fundamental_thesis": (
            "The weekend handed the market a clean test and the market failed to react: the US struck five Iranian "
            "coastal sites Saturday, Iran fired ballistic missiles and drones at US bases in Kuwait and Bahrain Sunday, "
            "Trump warned Iran 'will no longer exist' — and Brent settled at $71.99, the lowest since February, "
            "because Hormuz transits ran at roughly 75% of prewar volume through the strikes. The market prices a "
            "near-zero probability that the Strait closes while two militaries actively trade fire on a ceasefire each "
            "accuses the other of breaking. A call spread struck above spot owns the re-escalation the tape gives away "
            "— small premium, large payoff if the MoU fractures, a tanker is hit or transits stall — and it is the "
            "protection the book's energy length (TotalEnergies) and gold both failed to provide this weekend."
        ),
        "catalysts": [
            "US-Iran strikes + a fragile 'stand down' — a ceasefire each side accuses the other of breaking",
            "Hormuz transits at ~75% of prewar — a recovery the tape has fully extrapolated to permanence",
            "A tanker strike / mining / transit stall — the discrete trigger that reprices the tail from a standing start",
            "Trump's 'complete the job' rhetoric — the political tripwire the oil market is not positioned for",
        ],
        "risks": (
            "The truce holds, Hormuz fully normalises, and oil drifts toward $65 on the supply recovery; the spread "
            "decays as cheap insurance that did not fire. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "3/3 — a US-Iran shooting war moved crude to an eight-month low; the gap between the "
                            "near-zero priced closure risk and the live fighting is as wide as it gets.",
            "catalyst":     "2/2 — the strikes are live and dated; a fragile MoU with active fire is the catalyst.",
            "positioning":  "1/2 — spec length has bled out and no war premium is carried; the crowd is on the no-shock side.",
            "confirmation": "0/2 — oil is FALLING; there is no confirming up-move yet — this is a fresh, contrarian tail.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-030": {
        "instrument": (
            "Buy an August SPX 7,000/6,600 put spread — the replacement index hedge after MM-008 expires Jun 27. "
            "Buy the 7,000 put, sell the 6,600 put. Defined-risk downside into the Sep-hike + payrolls + "
            "AI-inflation tail. Max loss is the premium; the portfolio overlay on a book long AI equities."
        ),
        "fundamental_thesis": (
            "The book just banked the FOMC-tail put spread (MM-008) into expiry, and the reasons to carry index "
            "downside did not expire with it. The S&P sits near 7,357 with the Mag7 already cracking on its own "
            "supply-chain pricing power; a guidance-less Fed runs into June payrolls Jul 2-3, a quarter-end "
            "rebalance, and the July 4 EU-tariff deadline, into a tape that has priced the AI rebound as a one-way "
            "Micron-led melt-up. An August 7,000/6,600 put spread re-establishes the cheap convexity the book wants "
            "on a 32.2%-Micron, AI-heavy concentration — struck below spot so it costs little, structured for the "
            "discrete-event vol the guidance vacuum keeps manufacturing, not a chase of at-the-money premium."
        ),
        "catalysts": [
            "June payrolls Jul 2-3 — the first labour read in the guidance vacuum, a discrete equity-vol event",
            "Quarter/half-end rebalance (Jun 29-30) — pension de-risking after a strong Q2 equity run",
            "July 4 EU-tariff deadline — a re-escalation is a fresh cost-push + risk-off catalyst",
            "AI-inflation tail — the memory-cost overhang on the Mag7 the index is not pricing",
        ],
        "risks": (
            "The Micron-led melt-up extends and the S&P grinds higher into a calm month-end; vol stays crushed and the "
            "spread decays; payrolls land benign. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the index prices the AI rebound as one-way while the Mag7's own input-cost overhang "
                            "and a guidance-less Fed argue for two-sided risk.",
            "catalyst":     "2/2 — payrolls Jul 2-3 and the tariff deadline are dated and inside the structure's life.",
            "positioning":  "1/2 — sentiment re-embraced risk on Micron; complacency is rebuilding, room to fade.",
            "confirmation": "0/2 — the tape is rallying premarket; no confirming down-leg yet — this is a fresh hedge.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
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
    "MM-2026-001": "STILL OFFSIDE. EUR/AUD near ~1.651 — the risk-on melt-up keeps a bid under the commodity-AUD even with crude at $69, pinning the cross toward the 1.662 stop, not the 1.61 target. No EUR catalyst left; edge thinned. Trim into strength. Stop 1.662 (~11 pips). Tight leash.",
    "MM-2026-004": "GREEN, HOLDING. The 10Y sits ~4.39%, through the 4.44% entry, as the bond market trades the energy/goods disinflation over the hot PCE — and the weekend strikes did NOT lift yields (no war bid). Contrarian thesis intact. Harvest, don't press; the silicon-inflation (MM-027) is the offset. Stop 4.65% (~26bp).",
    "MM-2026-005": "THE CASUALTY, BUT NOT RALLYING ON WAR. Gold ~$4,040 (~-10.7% from the $4,523 entry) — a muted bounce even as the US and Iran traded strikes. That is the tell: bullion is a real-rates short now, not a war hedge. Min-hold (to ~Jul 15) holds it below the $4,250 stop. Own the war tail in OIL (MM-031); NOT an add here.",
    "MM-2026-007": "OFFSIDE, PRESSING THE LINE. USDJPY ~161.5 past the old 160 pin as the 13-mo-high dollar drags it up and crushed carry keeps the yen unloved — the Iran strikes drew no safe-haven yen bid. ~-1.3%. Needs a vol shock (payrolls Jul 2) to break. Stop 163.00; defined-risk expression MM-021.",
    "MM-2026-008": "CLOSED (banked Jun 27 at ~$45, ~+29% from the ~$35 entry). The FOMC-tail hedge did its job — peak ~$60 (+71%). In the closed ledger. The replacement index downside is the August 7,000/6,600 put spread (MM-030).",
    "MM-2026-009": "THE BEST POSITION. The front end (2Y ~4.09%) holds its rally vs the back end (10Y ~4.39%) — spread ~+27-30bp, gain ~+80% off the +15bp entry. A Fed pricing a hike into a disinflation eventually re-steepens; the war did not flatten it. Min-hold ~Jul 16; trail the stop; stop -10bp.",
    "MM-2026-012": "VINDICATED. ~1.143 with DXY at a 13-month high — the dollar regime is durable, and Trump's Sunday digital-tax tariff threat at the EU is a fresh EUR headwind into Jul 4. Hold toward 1.13; add downside via MM-024. The two-sided risk is a Jul 4 EU deal. Stop 1.182 (distant).",
    "MM-2026-013": "GREEN, HOLDING. The 2Y holds ~4.09%, through the 4.162% entry, even into a hot PCE and ~73% CME Sep-hike odds, as the bond market prices the disinflation over the dots — and shrugged the weekend strikes. The trade the Fed shot at is paying. Harvest, don't add into payrolls. Min-hold ~Jul 8; stop 4.35% (~26bp).",
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
    {"datum": "WEEKEND: US struck 5 Iranian coastal sites (Sat Jun 27); Iran fired missiles/drones at US bases in Kuwait (Ali Al Salem) & Bahrain (5th Fleet HQ) (Sun Jun 28); Trump: Iran 'will no longer exist', 'complete the job'; US official: both 'stand down for now'. Jun 17 MoU fragile.",
     "source": "CNN + Al Jazeera + NBC + RFE/RL (corroborated)", "asof": "2026-06-28", "stale": False},
    {"datum": "OIL FELL ON THE STRIKES: Brent Aug settled $71.99 (-4.34%), WTI $69.23 (-3.74%) Fri — lowest since Feb 27 — as Hormuz transits ran ~75% of prewar. Mon Jun 29 premkt: ES +0.5%, NQ +0.6%, YM +0.3% on the 'stand down'.",
     "source": "CNBC + OilPrice + Yahoo Finance (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Trump (Truth Social, Sun Jun 28): 100% tariffs on any country with a digital services tax on US firms (aimed at EU); to 'supersede trade deals... immediately imposed'. Days before the Jul 4 EU deadline (also autos->25%). PENDING.",
     "source": "CNBC + Social Media Today (corroborated)", "asof": "2026-06-28", "stale": False},
    {"datum": "Fri Jun 26 US close: S&P 7,354.02 (-0.05%); Nasdaq Composite 25,297.62 (-0.24%, 5th straight down day); Dow 51,876.11 (-0.09%) — global tech sell-off on AI data-center costs + reported OpenAI IPO delay",
     "source": "TheStreet + CNBC (corroborated)", "asof": "2026-06-26", "stale": False},
    {"datum": "Gold ~$4,040 — barely moved on literal US-Iran strikes, up a muted 2nd session post-PCE; a real-rates short not a war hedge (13-mo-high dollar + hawkish Fed dominate)",
     "source": "Trading Economics + LiteFinance (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Yields steady, no war bid: 2Y ~4.09%, 10Y ~4.39%, 2s10s ~+27-30bp; DXY 13-month high; EUR/USD ~1.143; VIX ~18.9 (18.89 Jun 25)",
     "source": "CNBC + FRED + FXStreet (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Sep-hike odds SPLIT: CME FedWatch ~73% hike vs prediction markets ~44%. Fed dots: 9 of 18 see a hike, 6 see two; PCE projected 3.6% end-2026. May PCE 4.1%/3.4% core (3-yr high), in line.",
     "source": "CME + Polymarket + Fed + CBS (corroborated)", "asof": "2026-06-26", "stale": False},
    {"datum": "Micron FY-Q3 (Jun 24 AMC): revenue $41.456B (vs ~$36.9B est); adj EPS $25.11 vs $21.40 (+17.3%); CEO 'tightness locked in beyond 2027'; 51 buy/3 hold/1 sell. AI tape sold off all week despite it.",
     "source": "TheStreet + CNBC + Finnhub (corroborated)", "asof": "2026-06-24", "stale": False},
    {"datum": "Silicon-inflation backdrop: Apple Mac/iPad +up to $300, MSFT Xbox +$100-150 (Jun 25), both citing AI-DRAM shortage; memory +98% in 2026; data centres ~70% of world output; PC -11%, phones -13%",
     "source": "Euronews + Al Jazeera + IDC + TrendForce (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "Asia/Europe (week): Nikkei -2.65%, Shanghai -2.26% to 4,027, HSCEI into bear market; DAX -1.0% to 24,894 (Infineon -6.3%), Germany Composite PMI 48 (3rd fall), euro-area Flash 49.5. BTC ~$60.4k.",
     "source": "T. Rowe + Trading Economics + S&P Global (corroborated)", "asof": "2026-06-26", "stale": False},
    {"datum": "Credit near multi-decade tights: IG ~80bp, HY ~285bp (BBG HY OAS ~2.7% vs 20-yr avg 4.9%). 2026 IG supply forecast ~$2.25tn (+35% y/y) on AI capex.",
     "source": "Schwab + PineBridge + ICE BofA (corroborated)", "asof": "2026-06-26", "stale": False},
    {"datum": "MM-008 (SPX put spread): CLOSED — banked Jun 27 at ~$45 (model est.; +~29% from ~$35 entry, peak ~$60). In the closed ledger; no live option line open.",
     "source": "Model estimate (no live option feed)", "asof": "2026-06-27", "stale": False},
    {"datum": "Ahead: quiet quarter/half-end TODAY (Jun 29); consumer confidence + JOLTS + Nike/Constellation Jun 30 + China PMI; ISM Mfg Jul 1; June PAYROLLS pulled to Thu Jul 2; early close Jul 3; EU-tariff/digital-tax deadline Jul 4. PENDING.",
     "source": "Conference Board + BLS + ISM + market calendar", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-06-26", "stale": True},
]

earnings_ideas = [
    {
        "ticker": "MU", "company": "Micron Technology Inc",
        "report_date": "2026-06-24", "report_timing": "AMC",
        "mode": "POST-EARNINGS", "direction": "Neutral",
        "conviction_score": 6, "conviction_label": "High — data gap flagged",
        "conviction_rationale": ("The asymmetry is real and attributable to the data: a +17.3% EPS beat with a CEO "
                                 "guide of memory tightness 'locked in beyond 2027' confirms the supercycle — but the "
                                 "stock reaction/implied move are unverified and the book is already a 32.2% holder, so "
                                 "the actionable edge is to MANAGE the concentration (collar), capping the label at "
                                 "High-gap and the direction at Neutral rather than a fresh add."),
        "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 2, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "unverified"},
        "reaction_tag": "FAIRLY PRICED",
        "eps_actual": 25.11, "eps_estimate": 21.40, "eps_surprise_pct": 17.34,
        "stock_reaction_pct": None, "implied_upside_to_pt": None,
        "key_bullets": [
            "Reported Jun 24 AMC: revenue $41.456B (vs ~$36.9B est) and adjusted EPS $25.11 vs $21.40 (+17.3%), the "
            "fourth straight large beat; CEO Mehrotra: memory tightness 'locked in to persist beyond calendar 2027.' "
            "Finnhub/TheStreet-sourced. Now 3 sessions post — the carried name that still defines the book.",
            "The supercycle is confirmed, but the tape did NOT reward it: the AI complex sold for the rest of the week "
            "(Nasdaq's 5th straight down day Jun 26) on data-center-cost worries and an OpenAI IPO-delay report. The "
            "blowout is in the price; the cost-overhang is the new marginal story. Sell side 51 buy / 3 hold / 1 sell.",
            "The same DRAM shortage repriced consumer hardware (Apple +$300, MSFT +$150) — MU is both the supercycle "
            "winner and the cause of a cost-push. The book holds ~32.2%; with the stock no longer rallying on good news, "
            "the positioning pillar scores 0 and the play is to collar and bank, not chase.",
        ],
        "what_moves_it": ("Concentration management, not the print. A confirmed blowout that the tape then SOLD for a "
                          "week says the risk question dominates a 32.2% position: post-print IVol is still rich, the "
                          "moment to collar and bank the supercycle gain. Bull: tightness beyond 2027 extends the run; "
                          "bear: the AI-cost-overhang selloff or the silicon-inflation backlash hits a third of the book at once."),
        "client_talking_point": ("Micron blew out — EPS $25.11 vs $21.40, tightness locked in beyond 2027 — and it's "
                                 "the book's biggest position, but notice the AI tape sold off all week anyway on "
                                 "data-center costs. When a stock won't rally on a record quarter, you stop adding and "
                                 "start protecting: collar it and bank the gain while option premiums are rich."),
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
        "STRIKES WITHOUT A PREMIUM. The US and Iran traded missile strikes over the weekend — US hits on five Iranian "
        "coastal sites Saturday, Iranian missiles/drones at US bases in Kuwait and Bahrain Sunday, Trump warning Iran "
        "'will no longer exist' — and crude FELL: Brent $71.99, WTI $69.23, the lowest since February, as Hormuz flows "
        "ran at ~75% of prewar. The market has fully desensitised to the Strait; a 'stand down for now' had Monday "
        "futures higher (ES +0.5%, NQ +0.6%). The structural backdrop is unchanged — Friday was the Nasdaq's 5th "
        "straight down day on AI data-center costs (S&P 7,354.02, Composite 25,297.62), the silicon-inflation (Micron "
        "blowout + Apple/Microsoft +15-25% hardware hikes, DRAM +98%) still sticky. Trump opened a second front Sunday: "
        "100% tariffs on countries taxing US tech, days before the Jul 4 EU deadline. Rates steady (2Y 4.09%, 10Y "
        "4.39%), dollar at a 13-month high (short EUR/USD vindicated, steepener ~+80%), gold barely moved on war "
        "($4,040) — a real-rates short, not a hedge. The cheapest tail in the market is the energy upside the tape "
        "gives away. Today quiet (quarter-end); payrolls pulled to Thu Jul 2 is the test."
    ),

    "summary_narrative": """
<p>The most important thing about the weekend is what the tape refused to do with it. The US struck five Iranian
coastal sites on Saturday; Iran answered Sunday with ballistic missiles and drones at the US air base in Kuwait and
the Fifth Fleet headquarters in Bahrain; Trump warned Iran &ldquo;will no longer exist&rdquo; if the strikes continue
and threatened to &ldquo;complete the job.&rdquo; And crude <strong>fell</strong> &mdash; Brent settled the week at
<strong>$71.99</strong> and WTI at <strong>$69.23</strong>, the lowest since February, because Hormuz transits had
already accelerated to roughly seventy-five percent of prewar volume and kept flowing through the fighting. By Monday
a &ldquo;stand down for now&rdquo; had futures higher (ES +0.5%, NQ +0.6%). (CNN, Al Jazeera, CNBC, OilPrice.)</p>

<p>The second-order effect consensus is missing is the desensitisation itself. A shooting war between the US and Iran
moved oil <em>down</em>, which means the market has stopped pricing the Strait of Hormuz as a tail at all &mdash; and
a tail nobody prices is the cheapest one to own. Decompose the melt-up the tape is treating as an all-clear: Friday
was the Nasdaq Composite's <strong>fifth straight down day</strong>, closing at 25,297.62 with the S&amp;P at
7,354.02, on AI-data-center cost worries and a reported OpenAI IPO delay. The quarter-end bid is narrow, carried by a
handful of names over a tape that sold technology for a week. (TheStreet, CNBC.)</p>

<p>The structural backdrop has not changed, it has only gone quiet under the geopolitics. The silicon-inflation the
prior session exposed is intact: Micron's blowout (EPS <strong>$25.11</strong> vs $21.40, tightness &ldquo;locked in
beyond 2027&rdquo;) and the Apple/Microsoft hardware hikes of 15&ndash;25% are the same DRAM shortage, with memory up
98% this year. And a second cost-push opened Sunday &mdash; Trump threatened <strong>100% tariffs</strong> on any
country imposing a digital services tax on US firms, aimed at the EU, days before the July 4 deadline that already
carried an autos-to-25% threat. (CNBC, Social Media Today.)</p>

<p>The book sits on the right side of the bond market's quiet disagreement with the Fed. Despite a hot May PCE
(4.1%/3.4% core) and a September hike the CME prices near <strong>73%</strong>, the 2Y holds ~4.09% and the 10Y
~4.39%, the 2s10s steepener (MM-009) is up near <strong>+80%</strong> and the duration longs (MM-004/013) are green;
the dollar at a 13-month high vindicated the short EUR/USD (MM-012). Gold barely moved on literal strikes &mdash;
~$4,040, a muted bounce &mdash; the cleanest tell that bullion is a real-rates short now, not a war hedge, so the long
(MM-005) is held on its min-hold, not added. The SPX put spread (MM-008) that paid the FOMC tail is banked.</p>

<p>The week is holiday-shortened: a quiet, quarter-and-half-end Monday; consumer confidence, JOLTS and Nike/
Constellation earnings Tuesday; ISM Wednesday; and June payrolls pulled forward to <strong>Thursday July 2</strong>
&mdash; the first labour read in the guidance vacuum &mdash; ahead of the July 4 tariff deadline. The regime is no
longer about whether the war reprices oil. It is that the market has decided no shock sticks, and the trade is to own
the tail it is giving away while staying long the disinflation the curve is finally pricing.</p>
""",

    "takeaways": [
        "<strong>A shooting war broke out and oil fell.</strong> The US struck five Iranian sites Saturday; Iran fired "
        "missiles and drones at US bases in Kuwait and Bahrain Sunday; Trump warned Iran 'will no longer exist.' Brent "
        "settled $71.99, WTI $69.23 &mdash; the lowest since February &mdash; as Hormuz transits ran at ~75% of prewar. "
        "The market has stopped pricing the Strait of Hormuz. (CNN, Al Jazeera, CNBC, OilPrice.)",

        "<strong>The desensitisation is the trade.</strong> A tail nobody prices is the cheapest one to own: the war "
        "premium in crude is not just drained, it is negative. The disciplined expression is defined-risk energy "
        "upside &mdash; a Brent call spread (MM-031) the tape is giving away at $69 even as the US and Iran trade "
        "strikes &mdash; not the gold the same regime is pinning. (CNBC, OilPrice.)",

        "<strong>The melt-up is narrow and the backdrop is unchanged.</strong> Monday futures rose on a 'stand down' "
        "(ES +0.5%, NQ +0.6%), but Friday was the Nasdaq Composite's 5th straight down day (25,297.62; S&amp;P "
        "7,354.02) on AI-data-center cost worries and an OpenAI IPO delay. The silicon-inflation (Micron blowout, "
        "Apple/Microsoft +15-25% hikes, DRAM +98%) is still the structural story under the geopolitics. (TheStreet, CNBC.)",

        "<strong>The bond market is fighting the Fed &mdash; and the book is on its side.</strong> Despite a hot PCE "
        "(4.1%/3.4%) and ~73% CME September-hike odds, the 2Y holds ~4.09% and the 10Y ~4.39% &mdash; and the weekend "
        "strikes drew no war bid. The 2s10s steepener (MM-009) is ~+80% and the duration longs (MM-004/013) are green. "
        "Harvest, don't press. (CNBC, FXStreet.)",

        "<strong>Gold barely moved on literal strikes.</strong> ~$4,040, a muted second-session bounce &mdash; the "
        "clean tell that bullion is trading as a real-rates short, not a war hedge, with a 13-month-high dollar the "
        "dominant engine. The book's long (MM-005) is ~-10%, held on its min-hold, not added. The same dollar regime "
        "vindicated short EUR/USD (MM-012). (Trading Economics, FXStreet.)",

        "<strong>Trump opened a second cost-push front.</strong> Sunday on Truth Social he threatened 100% tariffs on "
        "any country imposing a digital services tax on US firms &mdash; aimed at the EU, to 'supersede trade deals' "
        "and be 'immediately imposed' &mdash; days before the July 4 deadline that already carried autos-to-25%. A "
        "trade cost-push stacking onto the silicon one, EUR-relevant into MM-012. (CNBC, Social Media Today.)",

        "<strong>The silicon-inflation is still the unpriced structural trade.</strong> The curve reads the oil "
        "collapse as clean disinflation and is pulling front-end breakevens down &mdash; but DRAM +98% and a 15-25% "
        "hardware repricing feed core goods for quarters. Long 2Y breakevens (MM-027) owns the inflation a book long "
        "both duration and the AI complex otherwise lacks. Collar the 32% Micron after its blowout to lock the gain.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "No shock sticks — the desensitised melt-up broadens into quarter-end",
         "body": "The Iran 'stand down' holds, Hormuz keeps flowing, and a soft June payroll (Jul 2) prices OUT the Sep "
                 "hike: the 2Y extends below 4.05%, the curve re-steepens toward +40bp (MM-009/004/013 keep working), "
                 "the AI rebound broadens beyond a handful of names, and equities grind to new highs. Oil drifts toward "
                 "$65 on the normalisation; the Brent call spread (MM-031) decays as cheap insurance. Risk up · rates "
                 "down · dollar soft · oil soft · gold base."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "The bifurcation holds under a fragile truce — narrow melt-up, sticky core goods, range-bound rates",
         "body": "The ceasefire holds but stays fragile, oil chops in the high-$60s/low-$70s, and the silicon-inflation "
                 "keeps core goods sticky while the AI complex carries a narrow index. The 2Y stays range-bound "
                 "~4.05-4.20% and the Fed is pinned at a hawkish hold without the data to hike cleanly; breakevens "
                 "grind up on the silicon-push (MM-027), the dollar stays firm (MM-012), and the Jul 4 tariff deadline "
                 "caps risk appetite. Risk mixed · rates steady · dollar firm · oil rangey · breakevens up."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "A shock finally sticks — the truce breaks or the cost-push validates the hike",
         "body": "Either the ceasefire fractures and Hormuz actually closes (the desensitised tape repriced violently, "
                 "Brent gaps through $90 and MM-031 pays multiples), or the 15-25% hardware repricing plus a Jul 4 "
                 "tariff escalation bleeds into core PCE and a hot payroll fully prices the Sep hike, running the 2Y to "
                 "the 4.35% stop and bear-flattening the curve. AI multiples compress on the discount rate and the "
                 "input-cost squeeze; the S&amp;P retraces toward 7,000 where MM-030 pays. Risk down · rates/oil up · breakevens up."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a market that has decided no shock sticks. Over the weekend the US struck five
Iranian sites and Iran fired missiles at US bases in Kuwait and Bahrain, and crude <em>fell</em> to its lowest since
February because Hormuz transits never stopped recovering &mdash; they ran at roughly seventy-five percent of prewar
volume through the fighting. By Monday a 'stand down for now' had futures higher. The non-consensus read is that the
desensitisation is itself the signal: when a shooting war moves oil down, the market has stopped pricing the Strait of
Hormuz as a tail at all, and a tail nobody prices is the cheapest one to own (a Brent call spread, MM-031).</p>

<p>The counter-intuitive hook is that the calm is narrow and borrowed. The tape is treating quarter-end risk-on as
proof the world is benign, but Friday was the Nasdaq Composite's fifth straight down day &mdash; the S&amp;P closed at
7,354.02 and the Composite at 25,297.62 on AI-data-center cost worries and a reported OpenAI IPO delay. The melt-up is
a handful of names carrying an index that sold technology for a week, layered on top of a silicon-inflation backdrop
that has not gone away, only gone quiet under the geopolitics. The boom everyone is long is still the thing keeping
core goods sticky; the war just gave the tape something louder to ignore.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong> US
and Iranian forces trading strikes, Brent $72 / WTI $69, gold inert at $4,040, DRAM up 98%, hardware repricing 15-25%,
PC shipments down 11% and phones down 13%. <strong>What is priced:</strong> a 2Y at ~4.09% that held even on a hot PCE,
a dollar at a 13-month high, ~73% September-hike odds, oil at an eight-month low, and a VIX under 19.
<strong>Consensus narrative:</strong> &lsquo;the ceasefire holds, the AI complex is resilient, buy the quarter-end
melt-up.&rsquo; The gap &mdash; and the alpha &mdash; is on both ends: the market is underpricing the re-escalation
tail in energy AND the silicon-push inflation in the front end, while overpricing the durability of a one-handful rally.</p>

<p>Go around the world. <strong>US:</strong> a narrow, desensitised melt-up on the Iran halt over a tech tape that
sold for a week. <strong>Middle East:</strong> the actual war &mdash; US strikes, Iranian retaliation at Gulf bases,
a fragile 'stand down' on a Jun 17 MoU each side accuses the other of breaking. <strong>Japan:</strong> the Nikkei
fell 2.65% on the week in the global tech sell-off, the yen soft near 161 as the 13-month-high dollar dominates the
carry (MM-007/021). <strong>Asia/China:</strong> Shanghai -2.26% to 4,027 and the HSCEI into a bear market on the tech
rout; China June PMI (Jun 30) the next read. <strong>Europe:</strong> the DAX fell 1.0% to 24,894 (Infineon -6.3%),
Germany's composite PMI at 48 for a third straight monthly contraction, into a July 4 tariff deadline Trump just
widened to digital taxes.</p>

<p>The political angle runs on two fault lines the market is under-weighting. The Papic constraint in the Gulf is that
Trump has tied his own hands rhetorically &mdash; 'Iran will no longer exist,' 'complete the job' &mdash; so the next
Iranian provocation forces a response the oil market is not positioned for; the desensitisation is a positioning, not a
fact. The second fault line is trade: Sunday's 100% digital-tax tariff threat stacks a fresh cost-push onto the
silicon one and onto the existing autos-to-25% threat, exactly when the Fed has no slack to absorb any of it, and it
lands squarely on the EUR (MM-012) days before July 4.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the Hormuz re-escalation tail in energy (Brent call spread,
MM-031); the silicon-push core-goods inflation (front-end breakevens, MM-027); the OEM margin squeeze (MM-028).
<strong>Fairly priced:</strong> the dollar at a 13-month high; the energy disinflation in the front end.
<strong>Fully priced:</strong> the May PCE as a forward signal (a backward, peak-energy reading). <strong>Over-priced
(at risk):</strong> the durability of a narrow quarter-end melt-up resting on a 'stand down' between two sides still
trading missile strikes.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is the one hiding inside a non-event. The US bombed Iran
on Saturday, Iran threw ballistic missiles at two US bases on Sunday, the president said the country might cease to
exist &mdash; and oil fell to its lowest since February. Read that twice. A shooting war between the United States and
the holder of the Strait of Hormuz is a <em>bearish</em> oil catalyst now, because the tankers kept moving, transits
ran at three-quarters of prewar volume through the strikes, and the market has simply stopped believing the Strait can
close. The desensitisation is the story, and a tail nobody prices is the cheapest insurance on the board.</p>

<p>Decompose the calm the tape is selling as an all-clear. Monday's futures are up on a 'stand down for now,' and the
consensus files it as the world being fine. Pull it apart: Friday was the Nasdaq's fifth straight losing session, the
S&amp;P closed at seventy-three-fifty-four on data-center cost worries and an OpenAI listing delay, and the bounce is a
handful of mega-caps carrying an index that sold technology all week. So what, who is wrong, what is the trade: the
consensus that reads quarter-end risk-on as proof no shock matters is wrong on both flanks &mdash; it is underpricing
the re-escalation tail in energy and the silicon-push inflation in the front end at the same time &mdash; and the trade
is to own both cheaply rather than chase the melt-up.</p>

<p>Trace it to a balance sheet, because that is where the durable part lives. Underneath the geopolitics the flow has
not changed: hyperscaler capex &mdash; Microsoft, Google, Meta, Amazon &mdash; increasingly debt-funded, bidding
seventy percent of global memory output and starving every device that competes for the same wafer. That is a
multi-year supply reallocation with a relative-price shock attached, memory up while everything memory-dependent
re-prices, and it meets a bond market that rallied even on a hot PCE: the ten-year holds four-thirty-nine, the two-year
four-oh-nine, because the marginal buyer is trading the energy disinflation and the goods-volume collapse over a
forecast it does not believe. The weekend strikes did not move yields, which tells you the safe-haven bid the war
'should' have produced went nowhere &mdash; the bond rally is about disinflation, not fear. The book is on that side,
and it is paying.</p>

<p>The Burry tell sits one layer deeper than any of it. For two years the consensus has held that AI is structurally
deflationary &mdash; cheaper cognition, automated everything. The next eighteen months are going to argue the opposite
at the checkout: the build-out phase of the most disinflationary technology of the decade is an inflation machine, it
cannibalises the consumer-electronics supply chain, and it shows up as either margin destruction at the box-makers or
sticky core-goods inflation that traps the Fed &mdash; probably both. Apple and Microsoft just raised hardware prices
fifteen to twenty-five percent and named the AI-DRAM shortage as the cause; the core PCE underneath the collapsing
energy is sticky. The market has shelved this story under the louder one from the Gulf. It will be back.</p>

<p>So the posture into quarter-end is two-sided and patient. The rate winners &mdash; the steepener near plus-eighty,
the duration longs green &mdash; get harvested and trailed, not pressed, because the silicon-inflation is the live thing
that flattens them. The gold long is held on its rule, not added, precisely because it did not rally on a war: it is a
real-rates short wearing a safe-haven costume. The FOMC put spread is banked, the August replacement carries the
equity tail, and the fresh money goes where the gaps are widest &mdash; long the Hormuz re-escalation the tape gives
away, long the inflation the curve denies, short the OEMs the memory cost is squeezing. The tape has decided no shock
sticks. The brief's read is that two of them are mispriced precisely because everyone agrees with the tape.</p>
""",

    "correlation_regime": """
<p><strong>1. Oil decoupled from war &mdash; the biggest correlation break on the board.</strong> US strikes on Iran
and Iranian missiles at US Gulf bases is, historically, a crude-up event; instead Brent settled $71.99 and WTI $69.23,
the lowest since February. The Hormuz-closure premium has not merely drained, the sign flipped: the market reads
escalation through the lens of transits that keep recovering. A dominant-driver change this large means the consensus
positioning (no war premium) is the crowded side &mdash; the cheap fade is owning the re-escalation tail (MM-031).</p>

<p><strong>2. Gold decoupled from its own safe-haven reflex.</strong> Two countries trading missile strikes would
normally bid gold; instead it sat at $4,040, a muted second-session bounce. The real-rates and dollar engine
(13-month-high DXY, ~73% Sep-hike odds) overwhelms the haven engine outright. Gold is trading as a real-rates short,
not a war hedge &mdash; that is exactly why the book's long (MM-005) is held but not added, and why the war tail is
better owned in oil than in bullion.</p>

<p><strong>3. Equities and yields stayed decoupled &mdash; the bond market keeps fighting the Fed.</strong> The hot
PCE and a ~73%-priced September hike should lift yields; instead the 2Y holds ~4.09% and the 10Y ~4.39%, and the
weekend strikes drew no safe-haven bid either. The dominant driver in rates is the disinflation/growth read &mdash;
cheaper energy, collapsing goods volumes &mdash; not the dots and not the war. The steepener and duration longs
(MM-009/004/013) respect it; hold and harvest, do not fight the front-end.</p>
""",

    "vol_skew": """
<p><strong>The most mispriced vol on the board is energy, not equities &mdash; the war tail is being sold at an
eight-month low in crude.</strong> Index vol is calm: VIX ~18.9 with the term structure in contango (est. VIX9D ~17.5
· VIX ~18.9 · VIX3M ~19.5 · VIX6M ~20.0), MOVE eased toward ~104 as rates settle. The tape is pricing the Iran 'stand
down' and the quarter-end melt-up as one-way calm. But oil vol has collapsed alongside the price even as the US and
Iran trade strikes &mdash; the implied probability of a Hormuz disruption is now near nil, which is precisely when a
re-escalation is cheap to own. The headline trade implication: a Brent (or USO) call spread struck above spot
(MM-031), defined-risk upside on the tail the market gives away. The complement is the equity side &mdash; the August
SPX 7,000/6,600 put spread (MM-030) re-establishes cheap, below-spot convexity now that MM-008 is banked, structured
for the June payrolls (Jul 2), the quarter-end rebalance and the July 4 tariff deadline. If nothing sticks, both decay
cheaply; if either tail fires, the convexity is owned, not chased.</p>
""",

    "sector_rv": """
<p><strong>Leading (week into Monday):</strong> rate-sensitive value and financials as the curve holds its steepening;
the quarter-end mega-cap bid on the Iran halt. <strong>Lagging:</strong> the AI/semis complex &mdash; the Nasdaq's
5th straight down week on data-center cost worries and an OpenAI IPO delay, with Asia confirming (Nikkei -2.65%,
Infineon -6.3%, HSCEI into a bear market); energy as crude fell to an eight-month low even on the strikes; luxury and
EU-exposed names into Trump's digital-tax tariff threat. <strong>Today/next:</strong> quiet quarter/half-end Mon;
consumer confidence + JOLTS + Nike/Constellation Tue; ISM Wed; June payrolls Thu Jul 2 &mdash; each a discrete event
into the guidance vacuum.</p>

<p><strong>RV:</strong> Two cleanly fit today's tape. First, the memory-vs-OEM split (MM-028): long the memory/Micron
complex (which the book holds) vs SHORT the PC/handset OEMs &mdash; Dell, HP &mdash; that eat the DRAM cost and the
-11%/-13% volume decline. Second, the cross-region read: US financials/value over EU-exposed cyclicals into the July 4
tariff/digital-tax escalation, which lands on European autos, luxury and platforms. Both are low beta to the index and
high beta to the regime's two live cost-pushes (silicon and trade), and neither chases the narrow quarter-end melt-up.</p>
""",

    "positioning": """
<p><strong>The crowd is positioned for nothing to stick &mdash; short oil vol, long the melt-up, short front-end
inflation.</strong> The loudest lean is in energy: spec and systematic length has bled out and the market carries
essentially no Hormuz premium, so the pain trade is a re-escalation that the desensitised tape has to reprice from a
standing start (the cheap fade is MM-031). In equities, the quarter-end bid is narrow and trend-followers are chasing
a handful of names over a tape that sold tech for a week &mdash; the pain trade is the melt-up failing on a payroll or
a tariff headline (MM-030). In rates, fast money is still net-short duration post-Warsh, so the pain trade is the
front-end rally extending on a soft June payroll (Jul 2) &mdash; the squeeze the rescued duration longs (MM-004/013)
ride. In FX, the yen carry stays crowded long-USD at the MoF line (MM-007/021). And breakevens sit near cycle lows as
the crowd shorts inflation on the oil collapse, blind to the silicon-push (MM-027). The pain trade everywhere is the
same &mdash; a market that has decided every shock resolves benignly.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; the hold does not move the funding rate, and the weekend strikes produced no
dash-for-dollars in the plumbing. <strong>The Pozsar mechanic:</strong> trace the calm back to a flow. The reason a
Gulf war did not bid the dollar in funding markets is that the structural dollar bid is already maxed &mdash; DXY at a
13-month high on the rate-path asymmetry and AI-led capital concentration &mdash; so there is no incremental
safe-haven move left to make; the haven trade is fully on before the shock arrives. Underneath, the durable flow is
unchanged: hyperscaler capex (Microsoft, Google, Meta, Amazon), increasingly debt-funded, bids roughly seventy percent
of global memory output &mdash; a real-economy supply reallocation that shows up as a relative-price shock. The
funding angle that matters next is the collision of that IG issuance wave (2026 high-grade supply forecast ~$2.25tn,
+35% y/y) with a less-anchored long end: a term premium that widened post-Warsh meets a bond market with no
forward-guidance anchor. Watch IG issuance and the 10Y together &mdash; the AI cycle is a macro funding flow, not just
an equity theme.</p>
""",

    "tape_missing": """
<p><strong>The tape has priced a zero probability on Hormuz closing &mdash; while the US and Iran are actively trading
strikes.</strong> Crude at an eight-month low through a weekend of US bombing and Iranian retaliation says the market
has fully extrapolated the transit recovery. The falsifiable level: Brent reclaiming $80 says the desensitisation is
breaking; a clean re-escalation (the MoU fractures, a tanker is hit, transits stall) reprices the tail violently
from a standing start. The Brent call spread (MM-031) is the defined-risk way to own the gap; it costs little
precisely because consensus says it cannot happen.</p>

<p><strong>Just behind it: the bond market is right and the Fed is fighting last quarter's war.</strong> The hot May
PCE (4.1%) is a backward, peak-energy reading, and the 2Y holding ~4.09% on it &mdash; through a war that drew no
haven bid &mdash; says the marginal buyer agrees. Either the energy/goods disinflation dominates and the Fed is
tightening into it (the front end keeps rallying, MM-004/013/009), or the silicon-inflation plus the tariff cost-push
validates the hike and the 2Y backs up to 4.35%. That level is the falsifiable line; June payrolls (Jul 2) is the
test. The two-sided book owns both ends.</p>

<p><strong>The Burry tell &mdash; the structural thing the war has temporarily buried.</strong> For two years the
consensus has held that AI is structurally deflationary: cheaper cognition, automation, falling unit costs. The next
eighteen months will argue the opposite at the checkout. The build-out phase of the most disinflationary technology of
the decade is an inflation machine &mdash; it cannibalises the consumer-electronics supply chain, with every HBM wafer
for a GPU a wafer denied to a laptop or a phone (shipments down 11% and 13% this year). The first evidence is no
longer a thesis: Apple and Microsoft just raised hardware prices 15-25% and named the AI-DRAM shortage as the cause,
and the core PCE underneath the collapsing energy is sticky. Over the next two-to-three quarters this resolves as
either margin destruction at the box-makers or a core-goods inflation that traps the Fed &mdash; probably both. The
equity index, still concentrated in the seven names that are both the cause and the victims of the shortage, is the
least prepared for the world where the AI trade and the inflation trade are the same trade.</p>
""",

    "book_outlook": {
        "commentary": (
            "The weekend put the book's two hedges to the test &mdash; and both failed to do their job, which is the "
            "story for this book today. <b>TotalEnergies (TTE)</b> is the book's energy/war hedge; the US and Iran "
            "traded missile strikes and crude fell to an eight-month low, so the position meant to protect against a "
            "Gulf shock is a laggard <em>into</em> a Gulf shock. <b>Xetra-Gold (4GLD)</b> is the book's tail hedge; "
            "two countries exchanged fire and gold barely moved (~$4,040), confirming it is trading as a real-rates "
            "short, not a war hedge &mdash; the protection is hollow exactly when it was supposed to pay. Meanwhile the "
            "AI sleeve the book is concentrated in &mdash; <b>Micron (~32.2%)</b>, <b>NVDA</b>, <b>AVGO</b>, <b>AMD</b>, "
            "<b>SAP</b> &mdash; sold for a week on data-center costs and is now riding a narrow quarter-end melt-up on "
            "the Iran halt, with the silicon-inflation Micron's blowout exposed still the structural overhang. And "
            "Trump's Sunday digital-tax tariff threat is a fresh, specific headwind to the EUR sleeve: <b>LVMH</b> and "
            "<b>SAP</b> sit squarely in the EU-platform/luxury crosshairs days before July 4. The dominant action: "
            "collar the 32% Micron to bank the blowout, recognise the energy and gold hedges are not protecting and "
            "own the war tail in OIL instead (MM-031), and hold the rescued bond sleeve (the duration rally is real)."
        ),
        "outperform": [
            {"name": "USD sleeve / USD assets (~72% of the book)", "why": "The EUR-base book is ~72% USD and the dollar "
             "holds a 13-month high &mdash; reinforced by Trump's Sunday tariff threat pressuring the EUR. The FX "
             "translation keeps adding; the book is structurally long the currency winning today (mirrors MM-012)."},
            {"name": "The bond sleeve (UST 1.25% 2031, Siemens EUR IG)", "why": "Holds its rescue &mdash; the 2Y sits "
             "~4.09% and the 10Y ~4.39%, and the weekend strikes drew no yield back-up, so the duration rally on the "
             "disinflation bid is intact. This leg leads the defensive part of the book and mirrors the rate longs (MM-004/013)."},
            {"name": "Micron (~32.2%) — leads the melt-up, but lock it", "why": "The blowout still anchors the AI bull "
             "case and MU leads on the quarter-end risk-on bounce &mdash; but after a week of AI selling and with a "
             "third of the book on one name, the play is to collar and bank, not ride it naked into the next print."},
        ],
        "underperform": [
            {"name": "TotalEnergies (TTE) — the hedge that isn't hedging", "why": "The book's energy/war hedge LAGGED "
             "through a literal US-Iran shooting war: crude fell to an eight-month low (Brent $72, WTI $69) as Hormuz "
             "kept flowing. The protective thesis is broken for now; the war tail is better owned via the defined-risk "
             "Brent call spread (MM-031) than this length."},
            {"name": "Xetra-Gold (4GLD) — the tail hedge that didn't pay", "why": "Gold barely moved (~$4,040) on the "
             "strikes &mdash; a real-rates short, not a war hedge, with a 13-month-high dollar the dominant engine. The "
             "book's long is ~-10%, held on its min-hold to ~Jul 15, not added. The hedge is hollow when it was meant to work."},
            {"name": "LVMH & SAP — the EU-tariff/digital-tax crosshairs", "why": "Trump's Sunday Truth Social threat of "
             "100% tariffs on countries taxing US tech lands on EU platforms and luxury days before July 4. LVMH "
             "(-20% already) and SAP carry the specific re-escalation risk; the EUR sleeve is the trade-war casualty today."},
        ],
        "watch": [
            {"label": "Collar the 32% Micron — bank the blowout while IVol is still rich",
             "text": "MU's catalyst has fired and the AI tape just sold for a week; a third of the book on one name into "
             "that is a risk question, not a conviction. Rich calls finance protective puts for near-zero cost, banking "
             "the supercycle gain with defined upside. The August SPX put spread (MM-030) is the index overlay now that "
             "the FOMC-tail spread (MM-008) is banked. Do not ride 32% naked into the next print."},
            {"label": "The two hedges are not protecting — re-source the protection",
             "text": "TotalEnergies did not rise on a Gulf war and gold did not rise on missile strikes, so the book's "
             "two thematic hedges are hollow in the exact scenario they exist for. Own the re-escalation tail with "
             "defined risk where it is actually mispriced &mdash; the Brent call spread (MM-031) &mdash; rather than "
             "relying on equity energy length or bullion that trade on the dollar, not the war."},
            {"label": "Add the inflation hedge the book still lacks — long front-end breakevens (MM-027)",
             "text": "The book is long both duration and the AI complex, structurally short the one risk its own "
             "concentration creates: silicon-driven goods inflation, now compounded by the Jul 4 tariff cost-push. "
             "Front-end breakevens near cycle lows are the cheap way to own it &mdash; an inflation hedge that pays in "
             "exactly the scenario (a hot payroll / sticky core goods) that would hurt the rescued bond sleeve."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> the Iran flare-up is contained &mdash; the 'stand down' holds, Hormuz keeps
flowing, oil is cheap and falling, so the geopolitics is a non-event; buy the quarter-end melt-up, the AI complex is
resilient and the ceasefire is the floor. Read the weekend as proof that no shock sticks.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> 'no shock sticks' is a positioning, not a fact.
The market is short the Hormuz tail at an eight-month low in crude <em>while the US and Iran are actively trading
missile strikes</em>, and it is short front-end inflation on cheaper energy while DRAM and a fresh tariff threat feed
core goods. The crowded side is long a narrow melt-up resting on a fragile truce; the cheaper side owns the
re-escalation tail (MM-031), the silicon-push inflation (MM-027), and sits on the bond market's side of its
disagreement with the Fed.</p>
""",

    "one_chart": """
<p class="theme">Brent at an eight-month low is the chart &mdash; the market is pricing a zero probability that Hormuz closes while missiles fly across it.</p>
<p>The single thing the market should watch is the Brent line against the Gulf newswire. Crude settled at $71.99 and
WTI at $69.23, the lowest since February, through a weekend in which the US struck Iran and Iran struck US bases &mdash;
because Hormuz transits ran at ~75% of prewar and never stopped. The price is telling you the closure probability is
near zero; the headlines are telling you two militaries are exchanging fire on a ceasefire each side accuses the other
of breaking. Those cannot both be right. The level that resolves it is Brent $80 &mdash; a reclaim says the
desensitisation is breaking and the re-escalation tail is repricing (the Brent call spread, MM-031, pays); a drift
toward $65 says the normalisation is real and the tail decays as cheap insurance. Own the upside the tape is giving
away, and keep the silicon-inflation breakeven long (MM-027) as the second mispriced gap.</p>
""",

    "catalyst_calendar": [
        {"day": "Sat-Sun", "date": "Jun 27-28 ✓",
         "event": "US-Iran strikes, then a 'stand down' — oil FELL",
         "consensus": "Sat: US struck five Iranian coastal sites (in retaliation for an alleged Iranian drone hit on a "
                      "Hormuz cargo ship). Sun: Iran fired missiles/drones at US bases in Kuwait and Bahrain; Trump "
                      "warned Iran 'will no longer exist'; a US official then said both would 'stand down for now.' "
                      "Brent settled $71.99, WTI $69.23 (lowest since Feb). Sources: CNN, Al Jazeera, CNBC.",
         "view": ("The defining tell: a US-Iran shooting war moved crude DOWN because Hormuz kept flowing. The market "
                  "has stopped pricing the Strait — desensitisation that is itself the mispricing."),
         "asymmetry": "The re-escalation tail is given away at an eight-month low: own it with defined risk via the "
                      "Brent call spread (MM-031). A reclaim of $80 says the desensitisation is breaking.",
         "dir": "down"},
        {"day": "Sun", "date": "Jun 28 ✓",
         "event": "Trump opens a second tariff front — 100% on digital taxes",
         "consensus": "On Truth Social Trump threatened 100% tariffs on any country imposing a digital services tax on "
                      "US companies (aimed at the EU): the tariff to 'supersede trade deals' and be 'immediately "
                      "imposed.' Days before the Jul 4 EU deadline that already carries autos-to-25%. Sources: CNBC, Social Media Today.",
         "view": "A trade cost-push stacked onto the silicon one, landing on EU platforms/luxury and on the EUR right "
                 "before the deadline — vindicates the short EUR/USD (MM-012) and the EU-equity caution.",
         "asymmetry": "A hard line into Jul 4 is EUR-negative + EU-equity-negative; a last-minute deal is the two-sided "
                      "risk that caps the dollar trade.",
         "dir": "down"},
        {"day": "Mon", "date": "Jun 29 — TODAY",
         "event": "Quarter / half-year-end — quiet tape, rebalancing flows",
         "consensus": "No major US data or earnings. Half-year-end after a strong Q2 equity run; model/pension "
                      "rebalancing tends to sell equities and buy bonds into the close. Monday futures up on the Iran "
                      "'stand down' (ES +0.5%, NQ +0.6%). Sources: market calendar, Yahoo Finance.",
         "view": "A mechanical, non-fundamental flow: a rebalance that sells Q2 equity winners and buys duration "
                 "reinforces the front-end rally (MM-009/004/013) into month-end — a reason not to chase the melt-up.",
         "asymmetry": "The rebalance is a tailwind to the rate longs and a headwind to the narrow quarter-end equity "
                      "bid; fade the chase, hold the duration.",
         "dir": "flat"},
        {"day": "Tue", "date": "Jun 30",
         "event": "Consumer confidence + JOLTS + Nike / Constellation Brands (AMC)",
         "consensus": "June consumer confidence and May JOLTS job openings; Nike Q4 (cons. EPS ~$0.12 on rev ~$10.85bn, "
                      "a y/y decline) and Constellation Brands Q1 FY27 (cons. EPS ~$3.28) after the close. China June "
                      "PMI also lands. Sources: Conference Board, BLS, AlphaStreet, Zacks, NBS.",
         "view": "The consumer reads (confidence, Nike's DTC/China commentary, beverage volumes) are the first "
                 "kitchen-table check on whether the hardware price hikes + tariff threat are denting demand.",
         "asymmetry": "Soft confidence/JOLTS reinforces the goods-slowdown disinflation (rate longs); a weak Nike "
                      "guide is a discretionary-demand tell, not yet an index mover.",
         "dir": "flat"},
        {"day": "Wed", "date": "Jul 1",
         "event": "ISM Manufacturing (June) — prices-paid the watch",
         "consensus": "June ISM Manufacturing including prices-paid and new orders — the first hard read on the goods "
                      "cycle. ISM prices-paid is the cleanest gauge of whether the DRAM cost and the tariff threat are "
                      "bleeding into broad goods. Source: ISM.",
         "view": "ISM prices-paid is the silicon/tariff-inflation thermometer: a jump corroborates the cost-push "
                 "(MM-027); soft new orders reinforce the goods-slowdown disinflation the duration longs ride.",
         "asymmetry": "Hot prices-paid + soft orders is the worst mix for the Fed (stagflationary) and the bull case for "
                      "long breakevens against the rate longs.",
         "dir": "flat"},
        {"day": "Thu", "date": "Jul 2",
         "event": "June PAYROLLS (pulled forward) — first labour read in the guidance vacuum (book-critical)",
         "consensus": "June non-farm payrolls, moved to Thursday ahead of the Jul 3 early close and Jul 4 holiday. The "
                      "decisive input to the September-hike pricing (CME ~73%), and a major labour print since Warsh "
                      "removed forward guidance — its own vol event. Source: BLS.",
         "view": "The level that resolves the book's central binary: a soft print prices OUT the Sep hike, the 2Y "
                 "rallies through 4.05% and the rate longs (MM-004/013/009) extend; a hot print backs the 2Y to the 4.35% stop.",
         "asymmetry": "A soft payroll squeezes the crowded short-duration trade (MM-013 pays); a hot one validates the "
                      "hike and the cost-push, pressuring the rate longs and paying the SPX put spread (MM-030).",
         "dir": "flat"},
        {"day": "Fri-Sat", "date": "Jul 3-4",
         "event": "Early close (Jul 3) + EU-US trade & digital-tax deadline (Jul 4)",
         "consensus": "US half-day Jul 3, closed Jul 4. Trump's EU deadline: ratify or face autos-to-25%, now widened "
                      "by Sunday's 100% digital-tax threat. A second cost-push onto the silicon one. Sources: CNN, CNBC, Reuters.",
         "view": "A re-escalation is a fresh tariff cost-push exactly when the Fed has no slack — risk-off and "
                 "EUR-negative (the trade for short EUR/USD MM-012/024 and the index put spread MM-030).",
         "asymmetry": "A deal is risk-on + EUR-supportive (caps the dollar trade); a hard line is a second cost-push "
                      "that compounds the silicon-inflation and pays the index put spread (MM-030).",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.662 (the stop). At ~1.651 — offside as the risk-on melt-up keeps an AUD bid even with crude at $69; edge thinned, ~11 pips of room. Trim into strength; tight leash.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.39% — GREEN; the bond market trades the disinflation over the hot PCE and shrugged the weekend strikes (no war bid). Silicon-inflation (MM-027) is the offset. Harvest, don't press.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250 (breached). At ~$4,040 — barely moved on literal strikes (~-10%), the tell that it's a real-rates short not a war hedge. Min-hold holds it; own the war tail in OIL (MM-031), NOT an add here.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~161.5 — offside, past the old 160 pin; the strikes drew no safe-haven yen. Needs a vol shock (payrolls Jul 2) to break. Defined-risk expression MM-021. Tight leash.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> CLOSED — banked Jun 27 at ~$45 (~+29%). The FOMC-tail hedge did its job (peak ~$60). Replaced by the August 7,000/6,600 put spread (MM-030).</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+27-30bp; ~+80%; target +60bp. Held its steepening through the war. The silicon-inflation re-flattens it — that's the risk. Trail the stop; hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182 (distant). At ~1.143. VINDICATED — DXY at a 13-month high, reinforced by Trump's Sunday digital-tax tariff threat. Hold toward 1.13; add downside via MM-024. Two-sided risk: a Jul 4 EU deal.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold to ~Jul 8. At ~4.09% — GREEN; holds through a hot PCE and ~73% CME Sep-hike odds as the bond market fights the dots. June payrolls Jul 2 is the test. Harvest, don't add.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The US bombed Iran over the weekend — why is the market up and oil down?",
         "a": ("Because the market has stopped believing the Strait of Hormuz can close. Tankers kept moving through "
               "the strikes &mdash; transits are back to about three-quarters of prewar &mdash; so even a US-Iran "
               "shooting war moved crude to an eight-month low, and Monday futures rose on a 'stand down.' The catch "
               "is that this desensitisation is a bet, not a fact, and the two sides are still trading missiles. That's "
               "why the cheapest insurance on the board is energy upside.")},
        {"q": "If the war doesn't matter, why hold any hedge against it?",
         "a": ("Because a tail nobody prices is the one that hurts most if it fires. The market is giving away the "
               "Hormuz re-escalation at an eight-month low in oil. We'd rather own a defined-risk call spread on Brent "
               "&mdash; small premium, large payoff if the truce breaks &mdash; than rely on energy stocks or gold, "
               "which this weekend proved trade on the dollar, not the war.")},
        {"q": "Gold didn't move on actual strikes — is it still a safe haven?",
         "a": ("Not right now. Gold barely budged while two countries exchanged fire, which tells you it's trading as "
               "a real-rates short &mdash; a thirteen-month-high dollar and a hawkish Fed are pulling harder than any "
               "haven bid. We hold our position on its rule, but we're not adding, and we're not relying on it to "
               "protect the book. The protection has to come from somewhere that actually responds to the risk.")},
        {"q": "What should we do about Micron now?",
         "a": ("Collar it. Micron is a third of the book, its blowout catalyst has fired, and the AI tape just sold off "
               "for a week on data-center costs &mdash; riding that concentration naked into the next print is a risk "
               "question, not a conviction. Selling the still-rich calls to finance protective puts banks the "
               "supercycle gain for near-zero cost while keeping defined upside.")},
        {"q": "Trump just threatened 100% tariffs on EU tech — does that change anything?",
         "a": ("It's a second cost-push stacked on the chip one, and it lands on our European names &mdash; LVMH and "
               "SAP sit in the digital-tax and luxury crosshairs days before the July 4 deadline. It also reinforces "
               "the strong dollar, which helps us: the book is seventy-two percent dollar and our short-euro position "
               "is working. We'd stay cautious on EU-exposed equities into the deadline.")},
        {"q": "Where's the cleanest new money going?",
         "a": ("Two mispriced gaps. One is the war tail the tape gives away &mdash; a defined-risk Brent call spread. "
               "The other is the inflation the curve denies: everyone's reading cheaper oil as the end of inflation, "
               "but the chip-driven goods inflation is only starting and the Fed can't fix it with rate hikes, so we'd "
               "own front-end breakevens. Both pay precisely because consensus says they won't.")},
    ],

    "ideas_note": (
        "<p>The weekend's tell &mdash; a US-Iran shooting war that moved oil DOWN &mdash; sets the marquee idea, and "
        "the silicon-inflation backdrop sets the rest. <strong>Brent call spread (MM-031)</strong> &mdash; the "
        "marquee: the market has stopped pricing Hormuz, giving away the re-escalation tail at an eight-month low in "
        "crude; defined-risk upside on the tail consensus says cannot happen. <strong>Long 2Y breakevens "
        "(MM-027)</strong> &mdash; the curve reads the oil collapse as clean disinflation and is missing the DRAM-driven "
        "core-goods stickiness; the inflation a book long both duration and the AI complex otherwise lacks. "
        "<strong>Long memory vs short the OEMs (MM-028)</strong> &mdash; the supercycle is a margin transfer; the book "
        "holds the winners (MU), so the fresh leg is shorting Dell/HP, the box-makers eating the cost and the volume "
        "decline. <strong>August SPX 7,000/6,600 put spread (MM-030)</strong> &mdash; the replacement index hedge after "
        "MM-008 was banked, for the payrolls + quarter-end + tariff tail. The rate winners (MM-009/004/013) are "
        "harvested and trailed; the offside legs (gold, USDJPY, EURAUD) are held on tight leashes, not added.</p>"
    ),

    "event_radar_note": (
        "<p>Strikes without a premium: the US struck Iran and Iran struck US Gulf bases over the weekend, yet crude "
        "FELL to an eight-month low (Brent $72, WTI $69) as Hormuz kept flowing &mdash; the market has stopped pricing "
        "the Strait. Monday futures rose on a 'stand down' (ES +0.5%, NQ +0.6%). The structural backdrop holds: Friday "
        "was the Nasdaq's 5th straight down day on AI data-center costs; the silicon-inflation (DRAM +98%, Apple/MSFT "
        "+15-25% hikes) is sticky. Yields held (2Y 4.09%, 10Y 4.39%) with no war bid; the rate longs are green "
        "(steepener ~+80%). Trump opened a second tariff front (100% on EU digital taxes) into Jul 4. Ahead: quiet "
        "quarter/half-end TODAY; consumer confidence + JOLTS + Nike/Constellation Jun 30; ISM Jul 1; June PAYROLLS "
        "pulled to Thu Jul 2; the EU deadline Jul 4. The fresh ideas own the two mispriced gaps: the Brent call spread "
        "(the war tail), long breakevens (the silicon-inflation), long memory / short OEMs, and an index put spread. "
        "Collar the 32% Micron.</p>"
    ),

    "burry_tell": (
        "For two years the consensus has held that AI is structurally deflationary &mdash; cheaper cognition, "
        "automation everywhere, falling unit costs. The next eighteen months are going to argue the opposite at the "
        "checkout, and last week was the first evidence &mdash; now temporarily buried under the noise from the Gulf. "
        "The build-out phase of the most disinflationary technology of "
        "the decade is, mechanically, an inflation machine: the data centres now consume roughly seventy percent of "
        "the world's memory output, every HBM wafer for an Nvidia GPU is a wafer denied to a laptop or a phone "
        "(shipments down eleven and thirteen percent this year), and DRAM is up ninety-eight percent. The structural "
        "thing nobody is pricing is no longer a forecast: Apple and Microsoft just raised hardware prices fifteen to "
        "twenty-five percent and named the AI shortage as the cause, and the core PCE underneath the collapsing energy "
        "is sticky. Over the next two-to-three quarters this resolves as either margin destruction at the box-makers or "
        "a core-goods inflation that traps the Fed &mdash; probably both. The equity index, still concentrated in the "
        "seven names that are simultaneously the cause and the victims of the shortage, is the least prepared for the "
        "world where the AI trade and the inflation trade are the same trade. Long front-end breakevens (MM-027) and "
        "short the OEM casualties (MM-028) are the way to own it before the consensus re-labels it."
    ),

    "earnings_summary": (
        "Micron (MU): POST-EARNINGS (reported Jun 24 AMC, now 3 sessions post) — the carried name that still defines "
        "the book. FY-Q3 revenue $41.456B (vs ~$36.9B est) and adjusted EPS $25.11 vs $21.40 (+17.3%, Finnhub-sourced), "
        "with the CEO calling memory tightness 'locked in beyond 2027'; sell side 51 buy / 3 hold / 1 sell. The tell is "
        "the NON-reaction: the AI complex sold for the rest of the week despite the blowout (Nasdaq's 5th straight down "
        "day) on data-center-cost worries — the supercycle is confirmed but in the price, so the play on a 32.2% weight "
        "is NEUTRAL/manage (collar to bank the gain), not chase. No qualifying NEW pre-earnings name in the universe "
        "this week: Nike and Constellation Brands report Jun 30 but are Consumer (outside the Tech/Financials/"
        "Industrials/Utilities filter), so they are context, not ideas."
    ),
    "earnings_why": (
        "The earnings_data.md feed (last refreshed Jun 26) carries only post-earnings names from Jun 23-25; on a "
        "trading-day basis Micron (Jun 24 AMC) sits right at the 3-session-post boundary and is the only one still "
        "carrying signal, so it is the sole rendered idea — the +17.3% beat and 51/3/1 split are Finnhub-sourced, but "
        "with the stock no longer rallying on good news and the book a 32.2% holder, the trade is to manage the "
        "concentration (collar), not add. FedEx (Industrials, Jun 23), Jefferies (Financials, Jun 24) and TD Synnex "
        "(Jun 25) have rolled outside the 3-session-post window and are dropped. This week's pre-earnings calendar "
        "(Nike, Constellation Brands, both Jun 30) falls outside the sector universe (Consumer), so no fresh "
        "pre-earnings idea qualifies. Excluded throughout: names outside the Tech/Financials/Industrials/Utilities, "
        ">$10bn, US/Korea universe."
    ),

    "book_aim": (
        "Two-sided and on the right side of a market that has decided no shock sticks. The rate book is the winner: the "
        "2s10s steepener (MM-009) ~+80% and the duration longs (MM-004/013) green as yields held through both a hot PCE "
        "and a weekend of US-Iran strikes that drew no war bid; the short EUR/USD (MM-012) is vindicated by a "
        "13-month-high dollar and reinforced by Trump's digital-tax tariff threat; the SPX put spread (MM-008) is "
        "banked (~+29%). The casualties are the two thematic hedges that failed to fire on the war — gold (MM-005), "
        "held on its min-hold not added, and (in the Fable book) TotalEnergies. For the holiday-shortened week into "
        "payrolls: harvest and trail the rate winners (do NOT press — the silicon-inflation and the tariff cost-push "
        "are the live two-sided risks); hold the offside legs on tight leashes; and rotate fresh risk into the two "
        "mispriced gaps — the Brent call spread (MM-031, the war tail the tape gives away), long 2Y breakevens (MM-027), "
        "long memory / short OEMs (MM-028), and a fresh August SPX put spread (MM-030). The urgent house-keeping: "
        "collar the 32.2% Micron to lock the blowout. Own the tails consensus says cannot happen."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the option line (MM-008) was "
                 "banked at a ~$45 model estimate into its Jun-27 expiry (+~29%).")
    },
    "idea_selection": [
        {"label": "Brent call spread — own the war tail the tape gives away (MM-031)", "in": True,
         "text": ("The marquee idea. The US and Iran traded missile strikes and crude FELL to an eight-month low because "
                  "Hormuz kept flowing — the market prices a near-zero closure probability while two militaries "
                  "exchange fire. A defined-risk Brent (or USO) call spread struck above spot owns the re-escalation "
                  "tail consensus says cannot happen; small premium, large payoff if the truce breaks. Max loss capped.")},
        {"label": "Long 2Y inflation breakevens — own the silicon-push (MM-027)", "in": True,
         "text": ("The curve reads the oil collapse as clean disinflation and is pulling front-end breakevens down — but "
                  "DRAM +98%, a 15-25% hardware repricing and the fresh tariff threat feed core goods for quarters. Long "
                  "2Y breakevens owns the inflation the market is mistaking for disappearing, the hedge a book long both "
                  "duration and the AI complex otherwise lacks. Stop: -20bp.")},
        {"label": "Long memory vs short PC/handset OEMs (MM-028)", "in": True,
         "text": ("The DRAM supercycle is a margin transfer: Micron captures the price, Dell/HP eat the input cost and "
                  "the -11%/-13% volume decline. The book already owns the long leg via MU, so the fresh, "
                  "concentration-neutral expression is the SHORT — the box-makers who cannot fully pass the cost "
                  "through. Long who sets the price, short who pays it; stop ratio -4%.")},
        {"label": "August SPX 7,000/6,600 put spread — re-set the index hedge (MM-030)", "in": True,
         "text": ("The FOMC-tail spread (MM-008) is banked; the reasons to carry index downside did not expire with it. "
                  "June payrolls (Jul 2), the quarter-end rebalance, the July 4 tariff deadline and the AI cost-overhang "
                  "are the tail, into a tape pricing the Iran halt as a one-way melt-up. Struck below spot for cheap "
                  "convexity; defined risk.")},
        {"label": "Rate winners (MM-009/004/013) — harvest and trail, don't press", "in": False,
         "text": ("The steepener ~+80% and the duration longs green; they held through the war with no yield back-up. "
                  "Held and trailed, not added: the silicon-inflation (MM-027) and the tariff cost-push are the live "
                  "two-sided risks that re-flatten the curve. Let June payrolls resolve it; breakevens are the hedge.")},
        {"label": "Gold long (MM-005) — held on its rule, NOT added", "in": False,
         "text": ("Gold barely moved on literal strikes — a real-rates short, not a war hedge. Held on its min-hold to "
                  "~Jul 15, not averaged down. The war tail is owned in OIL (MM-031) where it is mispriced, not in "
                  "bullion where the dollar dominates.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 17.5},
        {"label": "VIX",   "value": round(_g("vix") or 18.9, 2)},
        {"label": "VIX3M", "value": 19.5},
        {"label": "VIX6M", "value": 20.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.09, 3)},
        {"label": "5Y",  "value": 4.22},
        {"label": "10Y", "value": round(_g("us10y") or 4.37, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 4.85, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-027", "trade": "Long US 2Y inflation breakevens (own the silicon-push)",
            "asset_class": "Rates (inflation)", "structure": "TIPS vs nominal / breakeven",
            "entry": "2Y breakeven ~spot", "stop": "-20bp", "target": "+40bp",
            "conviction": 8,
            "conviction_breakdown": {"gap": 3, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to early Sep", "min_hold_days": 0,
            "thesis": ("The marquee idea: the composition of inflation just flipped and the breakeven curve has not "
                       "noticed. The tape trades Brent $74 and gold sub-$4,000 as clean disinflation, pulling "
                       "front-end breakevens down — but the May PCE that printed 4.1% / 3.4% core is being replaced, "
                       "not ended, as an inflation engine. DRAM is up 98%, Apple and Microsoft just repriced consumer "
                       "hardware 15-25%, and that goods inflation feeds core PCE for quarters because the AI build-out "
                       "causing it has a multi-year lead time. Long 2Y breakevens owns the silicon-push the market is "
                       "mistaking for disappearing inflation — the hedge a book long both duration and the AI complex "
                       "otherwise lacks."),
        },
        {
            "id": "MM-2026-028", "trade": "Long memory (SOXX/MU) vs short PC/handset OEMs (Dell, HP)",
            "asset_class": "Equity RV", "structure": "cross-industry ratio",
            "entry": "spot ratio", "stop": "ratio -4%", "target": "ratio +8%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks-months", "min_hold_days": 0,
            "thesis": ("The DRAM supercycle is a margin transfer, and the market is pricing one side of it. Micron "
                       "printed a record quarter on tightness 'locked in beyond 2027'; the same shortage forced Apple "
                       "to raise the MacBook $200 and Microsoft the Xbox $150, into a year where PC shipments fall 11% "
                       "and phones 13%. The memory-makers capture the price; the OEMs eat the input cost AND the "
                       "volume decline. The book already owns the winners (MU, ~32.2%), so the fresh, "
                       "concentration-neutral leg is the SHORT — Dell, HP and the hardware OEMs that cannot fully pass "
                       "the cost through. Long who sets the price, short who pays it."),
        },
        {
            "id": "MM-2026-031", "trade": "Buy Brent Sep $80/$90 call spread (own the war tail the tape gives away)",
            "asset_class": "Commodity (options)", "structure": "call spread",
            "entry": "~$72 spot", "stop": "—", "target": "~5x at $90",
            "conviction": 7,
            "conviction_breakdown": {"gap": 3, "catalyst": 2, "positioning": 1, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Sep expiry", "min_hold_days": 0,
            "thesis": ("The marquee idea, straight out of the weekend's tell: the US struck five Iranian sites and Iran "
                       "fired missiles at US bases in Kuwait and Bahrain, and crude FELL to its lowest since February "
                       "because Hormuz transits ran at ~75% of prewar through the strikes. The market has priced a "
                       "near-zero probability that the Strait closes — while two militaries actively trade fire on a "
                       "ceasefire each accuses the other of breaking. A Brent (or USO) call spread struck above spot "
                       "owns the re-escalation tail consensus says cannot happen: small premium, large payoff if the "
                       "truce fractures, a tanker is hit or transits stall. It is the cheapest convexity on the board "
                       "precisely because everyone agrees the war does not matter — and it is the protection the book's "
                       "energy length (TTE) and gold failed to provide this weekend."),
        },
        {
            "id": "MM-2026-030", "trade": "Buy Aug SPX 7,000/6,600 put spread (re-set the index hedge)",
            "asset_class": "Equity (options)", "structure": "put spread",
            "entry": "~0.6% premium", "stop": "—", "target": "~5x at 6,600",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 0, "stop_quality": 1},
            "horizon": "to mid-Aug", "min_hold_days": 0,
            "thesis": ("The book just banked the FOMC-tail put spread (MM-008) into expiry, and the reasons to carry "
                       "index downside did not expire with it. The S&P sits near 7,357 with the Mag7 already cracking "
                       "on its own supply-chain pricing power; a guidance-less Fed runs into June payrolls Jul 2-3, a "
                       "quarter-end rebalance, and the July 4 EU-tariff deadline, into a tape pricing the AI rebound as "
                       "a one-way Micron-led melt-up. An August 7,000/6,600 put spread re-establishes cheap convexity "
                       "on a 32.2%-Micron, AI-heavy concentration — struck below spot for the discrete-event vol the "
                       "guidance vacuum keeps manufacturing, not a chase of at-the-money premium."),
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
