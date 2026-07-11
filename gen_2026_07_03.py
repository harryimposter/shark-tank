#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-07-03 (Friday, US markets CLOSED). THE HAWK DISARMED.

THE NEXT CHAPTER vs the Jun 29 (Strikes Without a Premium) / Jul 1 (All-Clear Arms the Hawk) runs:
the desensitisation bet paid, the record quarter closed, Warsh took the Sintra stage insisting prices
are too high — and then a +57k payroll with -74k of revisions DISARMED him inside 24 hours. The
September hike went from a coin-flip-plus to a coin-flip; the dollar rolled; gold ripped; and the
rate book that was on the wrong foot into the hawkish test got rescued by the data.
- THE PAYROLL BROKE THE HAWK. Thu Jul 2 June NFP printed +57,000 vs ~115k consensus — the weakest in
  four months — with April/May revised DOWN a combined 74,000. The unemployment rate FELL to 4.2%,
  but only because participation collapsed 0.3pp to 61.5%, the lowest since Mar 2021. A soft print
  wearing a strong-u-rate costume. (BLS, CNBC, Yahoo Finance.)
- THE HIKE GOT PRICED OUT. CME September-hike odds fell to ~53% from ~64% the day before; the 2Y
  dropped to 4.137% while the 10Y held ~4.485% (sticky on term premium/supply), so the 2s10s
  steepened to ~+35bp — the steepener (MM-009) ripped to ~+132%. (CNBC, FRED.)
- THE DOLLAR ROLLED. DXY broke below 101 to ~100.7 (−0.66% on the week), EUR/USD bounced to ~1.145,
  USD/JPY eased to ~161.1. The 13-month-high dollar regime that vindicated short EUR/USD (MM-012) is
  now the leg on the wrong foot — the rate-differential engine that drove it just lost its fuel.
  (FXStreet, Trading Economics.)
- GOLD RIPPED, THE MELT-UP BROADENED, CHIPS LAGGED. Gold climbed toward $4,200 on Fri — the
  real-rates relief the book's pre-position long (MM-005) was built for. Thu close: Dow 52,900.07
  (+1.14%, RECORD), S&P 7,483.24 (flat), Nasdaq Composite 25,832.67 (−0.80%) as chips slid; DAX
  +3.69%, FTSE +1.38%, Nikkei −0.91%. VIX ~16.6. (TheStreet, Trading Economics.)
- WARSH v THE DATA. Jul 1 at Sintra Warsh: "prices are too high," the Fed still "in the price
  stability business" even amid AI-productivity open-mindedness. Jul 2 the labour data undercut the
  hawk. Core PCE still ~3.1%. The new chair is politically boxed into a hawkish line the data no
  longer supports. (CNBC, C-SPAN, Bloomberg.)
- TARIFF TAIL INTO A CLOSED WEEKEND. US equity + bond markets are CLOSED Fri Jul 3 (Independence Day
  observed). The Jul 4 deadline to lock the EU deal capping tariffs at 15% is live; the digital-
  services-tax fight is unresolved and Trump's 100% tariff threat "supersedes" the deal. A binary
  over a 3-day weekend the tape is closed for. (CBS, PBS, Euronews.)
- IRAN/HORMUZ: Doha talks made "positive progress"; but Iran issued a fresh warning on Hormuz transit
  routes Jul 2 as vessels drift to the Omani coast, eroding Tehran's leverage. The 60-day ceasefire
  (from Jun 12, MoU Jun 17) holds; sticking points are frozen assets and Hormuz tolls. (CNN.)
- BOOK ACTION: the rate longs (MM-009/013) are the winners of the disarming; MM-004 (short 10Y) lags
  on a sticky back end; gold (MM-005) is finally paying. The leg on the wrong foot is short EUR/USD
  (MM-012) as the dollar top forms — trim, don't defend. Fresh ideas own the disarmed-hawk regime:
  a gold call spread, a chip-dispersion RV (long NVDA / short overbought AMD), a defined-risk EUR/USD
  tariff-tail put spread into Jul 4, and an index put spread over the closed weekend.

Run:  python gen_2026_07_03.py
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
# Fallback: the TradingView feed intermittently drops the cash S&P / Dow lines, and US cash markets
# are CLOSED today (Jul 3, Independence Day observed). Inject the web-verified Jul-2 closes
# (corroborated TheStreet + Trading Economics) so the dashboard headline indices never render
# "unverified". Only set if the live feed did not resolve them.
if "spx" not in snap:
    snap["spx"] = {"close": 7483.24, "chg_pct": 0.00, "chg_abs": 0.0}
if "dji" not in snap:
    snap["dji"] = {"close": 52900.07, "chg_pct": 1.14, "chg_abs": 594.83}
levels = live_levels.trade_levels(snap)
# Option spreads have no live feed — mark from spot. No live option line is open this refresh; the
# fresh index/vol expressions are the July SPX put spread (MM-039) and the gold call spread (MM-036).

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
    "GLD":  "The name the soft payroll just handed a catalyst. Gold ripped toward $4,200 on Fri as the +57k print "
            "collapsed September-hike odds to ~53% and pulled real yields lower — the exact real-rates relief the "
            "book's pre-position long (MM-005) was built for and never got until now. This is the tell that gold has "
            "flipped from a real-rates SHORT (which it traded as through the June strikes) back to a rate-cut LONG. "
            "Own the continuation with defined risk (MM-036), not a chase of spot.",
    "TLT":  "The disarmed hawk is duration's friend, but only at the front. The 2Y fell to 4.137% on the weak jobs "
            "print while the 10Y held ~4.485% on term premium and supply — so the front end rallied and the long end "
            "did not, which is why the steepener (MM-009) ripped to ~+132% and the 10Y short (MM-004) lagged. Own the "
            "curve shape, not outright long-end duration, until the back end confirms.",
    "MU":   "Still the book's structural anchor (the Fable book's largest weight) and the silicon-inflation story that "
            "keeps core goods sticky — the reason Warsh can stay hawkish even as the labour data cracks. The memory "
            "supercycle ('tightness beyond 2027') is intact, but the AI complex LAGGED the record tape on Jul 2 "
            "(Nasdaq −0.80% into a Dow record). A confirmed supercycle on a jittery, broadening tape is a name to "
            "collar and hold, not chase — the fresh leg is the chip-dispersion RV (MM-037).",
    "NVDA": "The reasonably-priced leg of the dispersion. NVDA is up ~13% YTD at ~32x on $81.6B Q1 revenue (+85% y/y), "
            "against AMD up ~150% YTD at ~175x — and both sold as a unit on Jul 2 on AI-margin and rate worries. Own "
            "the leader against the overbought name (MM-037): a chip selloff that punishes the cohort indiscriminately "
            "is the setup for the valuation gap to close. An OVERSOLD print here is the long leg, not a fade.",
    "AMD":  "The overbought casualty-in-waiting and the SHORT leg of the dispersion RV (MM-037). Up ~150% YTD at ~175x "
            "trailing earnings versus NVDA's ~32x on a fraction of the revenue base — a valuation the AI-margin and "
            "rate-repricing selloff targets first. The Fable book HOLDS AMD (+394%), so the RV doubles as the "
            "concentration-management trade: trim the exhausted winner, own the cheaper leader.",
    "XLE":  "Energy is the disinflation drag again. WTI ~$68 and Brent ~$71 as Hormuz transits keep recovering (vessels "
            "now drifting to the Omani coast, eroding Iran's leverage) and Doha talks make 'positive progress.' Cheap "
            "oil is a tailwind to the soft-landing read and a headwind to the book's energy length (TotalEnergies). "
            "The war tail is a cheap option, not a spot long — and it is NOT what the tape is pricing today.",
    "XLF":  "Financials led the record-tape broadening — the Dow's +594-point record on Jul 2 is a value/financials "
            "story, not a mega-cap-tech one (Nasdaq fell). A steeper curve (2s10s ~+35bp) lifts net-interest margins "
            "even as the hike gets priced out. Own the broadening (financials/value) over the narrow AI concentration "
            "that lagged the record.",
    "AAPL": "The consumer-hardware casualty of the silicon-inflation the Fed can't ignore. The DRAM shortage that made "
            "Micron's quarter is the input-cost squeeze on the box-makers; a soft labour market plus a Jul 4 tariff "
            "cost-push is a demand-and-cost pincer. Oversold is a value trap while the input cost climbs and the "
            "consumer participation rate falls.",
    "SPY":  "The index closed a record quarter and set a Dow record on the disarmed hawk — then shut for a 3-day "
            "weekend with a live Jul 4 tariff binary and a labour market cracking under a flattering u-rate. VIX at "
            "~16.6 is cheap insurance on that gap. The melt-up reads the soft payroll as goldilocks; the index put "
            "spread (MM-039) owns the stagflation-trap tail it is ignoring.",
    "BTC":  "Bitcoin ~$60k, still capped, not participating in the risk-on the way the Dow is — the same real-rates "
            "regime that finally let gold rip has not re-lit the crypto bid. A tell that the liquidity rotation favours "
            "hard assets and value over the speculative long tail. Not a book position.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("The Hawk Disarmed: A +57k Payroll Undoes Warsh's Sintra Line in 24 Hours — a Record-Tape Melt-Up "
          "Reads a Cracking Labour Market as Goldilocks While the Stagflation Trap Quietly Sets")
regime_note = (
    "The most important thing that happened in the last 24 hours is that the data mugged the new Fed chair. Kevin "
    "Warsh spent his international debut at Sintra on Tuesday insisting 'prices are too high' and that the Fed is still "
    "'in the price stability business' — arming the market for a September hike it had priced near 64%. On Thursday "
    "June payrolls printed +57,000 against a ~115k consensus, the weakest in four months, with April and May revised "
    "down a combined 74,000, and the September-hike odds collapsed to ~53%. The dollar rolled (DXY below 101 to "
    "~100.7), the 2Y fell to 4.137%, and gold ripped toward $4,200. The hawk was disarmed by his own labour market "
    "inside a single session. (BLS, CNBC, FRED, FXStreet.) "
    "Decompose the number the tape is celebrating. The headline the melt-up latched onto is the unemployment rate "
    "FALLING to 4.2% — but it fell for the wrong reason: participation collapsed 0.3pp to 61.5%, the lowest since "
    "March 2021. A soft print (+57k, negative revisions) wearing a strong-u-rate costume. The anatomy says the labour "
    "market is not tight, it is emptying — people are leaving the workforce faster than jobs are being lost, which "
    "flatters the rate and hides the crack. So what, who's wrong, what's the trade: the consensus that reads a "
    "record Dow and a disarmed hike as clean goldilocks is wrong; the bond market that has fought the dots for a "
    "month just got the data, and the front-end rally has room. (BLS, Yahoo Finance.) "
    "The second-order effect consensus is missing is the trap. A labour market softening THIS fast while core PCE is "
    "still ~3.1% and two cost-push fronts are live — the silicon-DRAM inflation and a July 4 tariff deadline — is not "
    "goldilocks, it is the front edge of stagflation. The Fed cannot hike into a cracking labour market and cannot "
    "cut into sticky inflation. The melt-up is pricing the dovish half and ignoring the sticky half. Warsh is now "
    "politically boxed: he staked his credibility on hawkishness at Sintra and the data undercut him a day later, so "
    "he holds a line he can no longer fully justify — which keeps the front end volatile and the back end heavy. "
    "(CNBC, C-SPAN.) "
    "The book sits on the right side of the disarming. The 2s10s steepener (MM-009) ripped to ~+132% as the front end "
    "rallied harder than the back; the short-2Y (MM-013) is green as the hike it fades gets priced out; the short-10Y "
    "(MM-004) lags because the long end is sticky on term premium and supply. Gold (MM-005), held through a brutal "
    "drawdown on its min-hold, is finally paying as real yields fall. The leg now on the wrong foot is the short "
    "EUR/USD (MM-012): the 13-month-high dollar that vindicated it is topping as the rate-differential engine reverses "
    "— trim it, do not defend it, and let the July 4 tariff deadline be the only reason to hold any short-EUR risk. "
    "The tape is closed for a three-day weekend over a live tariff binary. The regime is no longer 'no shock sticks.' "
    "It is that the one shock that stuck — a cracking labour market — is being mistaken for good news, and the trade "
    "is to own the disinflation the curve is finally pricing while hedging the stagflation the melt-up is not."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# No close action today. MM-005 (gold) stays open on its 45-day min-hold (to ~Jul 15) and is now
# recovering; MM-012 (short EUR/USD) is green with a distant 1.182 stop but is flagged as the leg to
# trim as the dollar tops. All other legs inside their stops/min-holds.

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
            "The quiet leg, and it is roughly flat near 1.649 as the risk-on melt-up keeps a bid under the "
            "commodity-AUD. A paused ECB still caps the EUR side, but the record-tape broadening and a softening US "
            "labour market that lifts risk appetite rebuild the AUD carry bid, pinning the cross to the middle of its "
            "range rather than toward the 1.61 target. There is no dated EUR catalyst left; the edge has thinned, and "
            "this is the leg to trim into strength rather than defend. Stop 1.662, close by."
        ),
        "catalysts": [
            "ECB pause fully in the price — no forward EUR catalyst",
            "Risk-on melt-up (record Dow) — rebuilds the commodity-AUD bid, the force AGAINST the short",
            "RBA path — a hawkish hold supports AUD vs a paused ECB",
            "Iron ore / China demand — the AUD swing factor",
        ],
        "risks": (
            "The soft-payroll risk-on keeps bidding AUD and the cross runs the 1.662 stop; a firm China read lifts iron "
            "ore; an ECB official re-opens the hike door and EUR squeezes higher. Stop 1.662 (close)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the cross still sits above where the 2yr spread implies with a paused ECB, but AUD's "
                            "own risk-on bid has narrowed the edge.",
            "catalyst":     "1/2 — the dated ECB catalyst has passed; what remains is slower-burn (RBA, China).",
            "positioning":  "1/2 — EUR longs trapped flat offer some unwind fuel; AUD positioning is light.",
            "confirmation": "0/2 — the cross has drifted UP, not lower; no confirmation of the short.",
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
            "The laggard of the rate book, and the tell about the back end. The soft +57k payroll priced out the hike "
            "and rallied the FRONT end hard — but the 10Y barely moved, holding ~4.485% versus the 4.44% entry, "
            "because term premium and Treasury supply pin the long end even as the Fed path softens. The disinflation "
            "thesis is intact and now data-supported, but the expression that pays is the curve (MM-009), not outright "
            "long-end duration, until the back end confirms. Hold on a tight rein; the stop is 4.65%, ~16bp away."
        ),
        "catalysts": [
            "June payrolls +57k (released) — the soft print that priced out the hike; a front-end, not long-end, event so far",
            "Sticky core PCE ~3.1% + Treasury supply — the term-premium anchor keeping the 10Y heavy",
            "Warsh's hawkish Sintra line vs the data — the volatility source at the front, spilling into the back",
            "Next CPI / quarterly refunding — the dated catalysts that decide whether the long end joins the rally",
        ],
        "risks": (
            "The stagflation read wins and the long end sells on term premium and fiscal supply while the front rallies; "
            "a tariff cost-push (Jul 4) re-lifts inflation expectations. Stop 4.65% (now ~4.485%, ~16bp away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the disinflation is now data-confirmed (soft payroll), widening the gap vs the "
                            "Fed's hawkish line, but the long end's supply/term-premium overhang caps it.",
            "catalyst":     "1/2 — the payroll catalyst fired but landed at the front end; the long end's dated "
                            "catalyst (CPI/refunding) is ahead.",
            "positioning":  "1/2 — the crowd is still short duration; the rally is squeezing the front, less so the back.",
            "confirmation": "0/2 — the 10Y did NOT rally on the soft payroll; the back end has not confirmed the thesis.",
            "stop_quality": "1/1 — 4.65% is a clear technical level; ~16bp of risk.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold in USD. The inverse of real rates, driven by the Fed path "
            "and real yields, USD strength, EM central-bank buying, geopolitical premia, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "The trade that finally got its catalyst. Gold ripped toward $4,200 on the soft payroll — the real-rates "
            "relief the pre-position long was built for and had been denied through a hawkish-Fed, strong-dollar June "
            "that pinned it as a real-rates SHORT. The disarming of the September hike is exactly the mechanism: lower "
            "expected policy rates, a topping dollar, and a stagflation read that revives the debasement bid all lift "
            "gold at once. The long is ~-7.6% from the $4,523 entry and recovering hard, held through the drawdown on "
            "its 45-day min-hold (to ~Jul 15). The rule that took the pain is now capturing the turn. Hold; the fresh, "
            "defined-risk way to press the continuation is the call spread (MM-036), not adding spot into the bounce."
        ),
        "catalysts": [
            "June payrolls +57k → ~53% Sep-hike odds — the real-rates relief driving the bounce",
            "A topping dollar (DXY sub-101) — the second engine turning in gold's favour",
            "Stagflation read (soft labour + sticky core PCE + tariff cost-push) — the debasement bid returning",
            "EM / central-bank physical buying — the structural floor that held through the drawdown",
        ],
        "risks": (
            "The soft payroll proves a blip and a hot CPI re-arms the hike; the dollar stabilises; ETF flows stay "
            "negative. The min-hold keeps it open to ~Jul 15; stop $4,250 (price now back below it but recovering) — "
            "the rule holds it, and MM-036 caps fresh risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — both engines (real rates, dollar) have turned in gold's favour after a month "
                            "against it; the mispricing is closing but the debasement leg has room.",
            "catalyst":     "2/2 — the soft payroll is the dated, live catalyst; the next CPI decides the follow-through.",
            "positioning":  "1/2 — spec length was washed out in June; positioning is clean, squeeze-prone on the turn.",
            "confirmation": "1/2 — gold rallied off the lows on the payroll; one confirming leg, not yet a trend break higher.",
            "stop_quality": "1/1 — $4,250 is a defined level; the min-hold rule is the discipline that captured the turn.",
        },
    },
    "MM-2026-007": {
        "instrument": (
            "USD/JPY spot FX (dollar-yen). Driven by the US-Japan 2yr rate differential, BoJ "
            "normalisation, the Fed path, risk sentiment (JPY is a crisis safe-haven), and Japanese "
            "MoF intervention risk near ~160-163."
        ),
        "fundamental_thesis": (
            "Finally getting a tailwind from the right engine. The soft payroll narrowed the US-Japan rate differential "
            "and rolled the dollar, easing USD/JPY back to ~161.1 from the 162.4 spike into the print — the short is "
            "~-1.1%, improving. The structural case (a BoJ that has normalised toward 1.00%, a Fed whose September hike "
            "just got priced out) is now reinforced by a topping dollar rather than fighting a rising one. The MoF line "
            "near 160 remains the backstop below. Patient short; 163 is the stop, the defined-risk expression is the "
            "put/seagull the desk carries."
        ),
        "catalysts": [
            "Soft US payroll → priced-out hike — the differential-narrowing that finally helps the short",
            "A topping dollar (DXY sub-101) — the broad-USD engine turning the pair's way",
            "MoF intervention at the 160 line — the official backstop below",
            "Japan CPI / BoJ guidance — further normalisation supports the yen",
        ],
        "risks": (
            "A hot US CPI re-arms the hike and re-widens the differential, pushing USD/JPY back toward the 163 stop; "
            "risk-on keeps the carry alive. Stop 163.00."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is above 2yr-differential fair value and the differential is now narrowing "
                            "with the disarmed hike.",
            "catalyst":     "2/2 — the soft payroll and the topping dollar are both live; the MoF line is the backstop.",
            "positioning":  "1/2 — the yen carry is still crowded long-USD; the dollar top is the unwind fuel.",
            "confirmation": "1/2 — the pair eased off the 162.4 spike on the payroll; a first confirming move.",
            "stop_quality": "1/1 — 163.00 is a clean MoF-intervention ceiling; ~2 pts risk.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (receive/own cut optionality), short "
            "the 10Y (short fiscal-supply risk). Pays when 10Y-minus-2Y widens. Currently ~2Y 4.14% "
            "/ 10Y 4.49%, spread ~+35bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "The best position in the book and the cleanest expression of the whole regime. The soft payroll rallied "
            "the front end (2Y to 4.137%) while the back end held ~4.485% on term premium and supply — a textbook "
            "bull-steepening — and the spread widened to ~+35bp, taking the open gain to ~+132% off the +15bp entry "
            "(an 18-month inversion). This is exactly the trade for a disarmed hawk: a Fed that can no longer hike into "
            "a cracking labour market re-steepens the curve through the front, while the fiscal-supply and "
            "sticky-inflation overhang keeps the back end heavy. Min-hold to ~Jul 16; target +60bp; held, trail the "
            "stop up, do not add into the run."
        ),
        "catalysts": [
            "Soft payroll → priced-out hike — the front-end rally that is the re-steepening engine, working now",
            "Sticky core PCE + Treasury supply — the term premium keeping the back end heavy = steepens",
            "Jul 4 tariff cost-push — a fresh inflation risk that pressures the long end and steepens further",
            "A hot CPI — the risk that re-arms the hike, backs up the front end and re-flattens the curve",
        ],
        "risks": (
            "A hot CPI re-prices the hike and the front end backs up, bear-flattening the curve; a global risk-off bid "
            "flattens via the long end. Stop: spread below -10bp (now ~+35bp)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve is still underpriced vs the late-cycle mean off an 18-month inversion; the "
                            "re-steepening has room to the +60bp target.",
            "catalyst":     "2/2 — the payroll is the live front-end catalyst; the tariff/supply story keeps the back "
                            "end heavy.",
            "positioning":  "1/2 — front-end positioning is still hawkish post-Warsh; the rally is squeezing it.",
            "confirmation": "2/2 — the spread widened to ~+35bp on the front-end rally; the re-steepen is confirming.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "The leg now on the wrong foot — the position to trim, not defend. EUR/USD bounced to ~1.145 and DXY broke "
            "below 101 to ~100.7 as the soft payroll priced out the September hike and knocked out the rate-differential "
            "engine that drove the 13-month-high dollar. The trade is still green (~+1.3% from the 1.16 entry) with a "
            "distant 1.182 stop, but the thesis — a Fed pricing a hike vs a paused ECB — is precisely what just "
            "reversed. The ONLY reason left to carry short-EUR risk is the July 4 tariff/digital-tax deadline, an "
            "EUR-negative binary over a closed weekend; that is a defined-risk options trade (MM-038), not a reason to "
            "hold the spot short into a topping dollar. Trim toward flat; let MM-038 own the tariff tail."
        ),
        "catalysts": [
            "Soft payroll → priced-out hike + DXY sub-101 — the dollar top, the force AGAINST the short",
            "Jul 4 EU tariff/digital-tax deadline — the only remaining EUR-negative catalyst (own via MM-038)",
            "ECB on hold — the paused EUR side, now the relative winner as the Fed softens",
            "Spec positioning — a crowded short-EUR unwind is the squeeze risk as the dollar tops",
        ],
        "risks": (
            "The dollar top extends on a soft-landing repricing and EUR/USD squeezes toward 1.16+; a clean EU-US deal "
            "removes the tariff tail. Stop 1.182 (distant) — but the thesis has turned; trim rather than wait for it."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the rate-path asymmetry the trade priced has REVERSED; the mispricing that remains "
                            "is thin and tariff-dependent, not rate-driven.",
            "catalyst":     "1/2 — the only live catalyst is the Jul 4 tariff binary; the rate catalyst now cuts the other way.",
            "positioning":  "1/2 — a crowded short-EUR is unwind fuel AGAINST the position as the dollar tops.",
            "confirmation": "0/2 — EUR/USD bounced and DXY broke 101; the tape is no longer confirming the short.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; the position has a cushion, but the edge has gone.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receive 2Y swap / long 2Y notes). The 2Y is the market's "
            "real-time forecast of the Fed path over two years — the most policy-sensitive point on the "
            "curve."
        ),
        "fundamental_thesis": (
            "The trade the Fed shot at, vindicated by the data. The thesis was that the front end over-priced a 2026 "
            "hike; Warsh armed it at Sintra, but the +57k payroll disarmed it, dropping September-hike odds to ~53% and "
            "the 2Y to 4.137% — through the 4.162% entry, so the position is GREEN. The fade is the thesis confirming: "
            "a labour market cracking under a flattering u-rate is exactly the data that prices OUT a hike. The residual "
            "risk is a hot CPI or a tariff cost-push that re-arms the hawk. Min-hold to ~Jul 8; stop 4.35%, now ~21bp "
            "away. Harvest and hold; the curve (MM-009) is the higher-conviction expression of the same view."
        ),
        "catalysts": [
            "June payrolls +57k → ~53% Sep-hike odds — the print that fades the hike, working now",
            "Falling participation (61.5%) — the labour-market crack the front end is finally pricing",
            "Warsh's hawkish line vs the data — the source of two-way front-end vol",
            "A hot CPI / Jul 4 tariff cost-push — the risk that re-arms the hike and backs up the 2Y",
        ],
        "risks": (
            "A hot CPI or a tariff-driven inflation scare re-prices the September hike and backs the 2Y up to the 4.35% "
            "stop. Stop 4.35% (now ~4.14%, ~21bp away); min-hold to ~Jul 8."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the soft payroll widens the gap between the 2Y and the justified hike probability; a "
                            "tariff/CPI cost-push is the partial offset.",
            "catalyst":     "2/2 — the payroll fired in the position's favour; the next CPI is the decisive follow-up.",
            "positioning":  "2/2 — the market was maximally positioned for hawkish Warsh; the soft print is squeezing it.",
            "confirmation": "2/2 — the 2Y rallied THROUGH the entry on the weak jobs data; the contrarian thesis confirmed.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~21bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-036": {
        "instrument": (
            "Buy an August gold $4,200/$4,500 call spread — defined-risk upside on spot gold (tradeable via COMEX "
            "gold options or a GLD call spread). Buy the $4,200 call, sell the $4,500 call. Owns the continuation of "
            "the soft-payroll → lower-real-rates move with capped premium; max loss is the premium. With spot ~$4,200, "
            "the lower strike is at-the-money — cheap convexity on the rate-cut repricing the tape just began."
        ),
        "fundamental_thesis": (
            "The marquee idea: the payroll flipped gold's engine and the move has just started. For a month gold traded "
            "as a real-rates SHORT — it fell as the dollar hit a 13-month high and the Fed stayed hawkish, and it "
            "barely moved on literal US-Iran strikes. The +57k print reverses that: September-hike odds fell to ~53%, "
            "the dollar broke below 101, and gold ripped toward $4,200. Lower expected policy rates, a topping dollar, "
            "and a stagflation read that revives the debasement bid all push the same way. A call spread struck at spot "
            "owns the continuation with defined risk — and it is the disciplined way to press the book's existing cash "
            "gold long (MM-005) without averaging spot into the bounce."
        ),
        "catalysts": [
            "June payrolls +57k → ~53% Sep-hike odds — the real-rates relief that turned gold",
            "DXY sub-101 (−0.66% on the week) — the topping dollar, the second engine",
            "Sticky core PCE ~3.1% + Jul 4 tariff cost-push — the stagflation/debasement bid",
            "The next CPI — the dated catalyst that confirms or re-arms the hike",
        ],
        "risks": (
            "A hot CPI re-arms the September hike, the dollar stabilises, and gold gives back the payroll bounce; the "
            "spread decays as insurance that did not extend. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "3/3 — the market spent a month pricing gold as a real-rates short; the payroll flipped the "
                            "driver and the repricing has barely begun — a wide gap.",
            "catalyst":     "2/2 — the soft payroll is live and dated; the next CPI is the confirming catalyst.",
            "positioning":  "1/2 — spec length was washed out in June, so the bid is squeeze-prone; not yet crowded.",
            "confirmation": "1/2 — gold rallied off the lows on the print; one confirming leg, not yet a trend.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-037": {
        "instrument": (
            "Equity RV — LONG NVDA vs SHORT AMD (dollar-neutral pair, or long NVDA calls / short AMD calls). A ratio "
            "that rises when the reasonably-valued AI leader outperforms the overbought, richly-valued challenger. "
            "NVDA ~32x trailing on $81.6B Q1 revenue (+85% y/y); AMD ~175x on $10.3B (+38% y/y), up ~150% YTD vs NVDA "
            "~13%. The Fable book holds both — long NVDA (−10.5%) and long AMD (+394%)."
        ),
        "fundamental_thesis": (
            "The chip complex sold as a unit on July 2 even as the Dow set a record — AI-margin worries, the rate "
            "repricing, and mega-IPO rotation chatter punished the cohort indiscriminately. That indiscriminate selling "
            "is the setup for the valuation gap to close: AMD is up ~150% this year at ~175x trailing earnings on a "
            "fraction of NVDA's revenue base, while NVDA trades ~32x after a mere ~13% YTD gain on $81.6B of quarterly "
            "revenue. Own the leader, short the overbought name. It is concentration-neutral to the index and low-beta "
            "to the AI direction, high-beta to the dispersion — and it doubles as book housekeeping: trim the exhausted "
            "AMD winner, add to the laggard NVDA the house still likes."
        ),
        "catalysts": [
            "Jul 2 chip selloff (Nasdaq −0.80% into a Dow record) — the indiscriminate-selling setup",
            "Valuation gap: AMD ~175x / +150% YTD vs NVDA ~32x / +13% YTD — the mispricing the RV owns",
            "Q2 chip earnings (late July) — the catalyst that rewards revenue quality over multiple",
            "Mega-AI-IPO supply — the rotation risk that hits the most-crowded, highest-multiple name first",
        ],
        "risks": (
            "A broad AI-capex re-acceleration lifts the whole cohort and AMD's momentum outruns NVDA; an AMD-specific "
            "product win re-rates it. Stop: ratio -5% from entry."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the ~175x-vs-32x valuation divergence is wide and real, but partly reflects AMD's "
                            "higher growth optionality.",
            "catalyst":     "1/2 — Q2 earnings are the dated catalyst; the dispersion plays out gradually until then.",
            "positioning":  "2/2 — the crowd is long the high-multiple momentum name (AMD); NVDA is under-owned relative "
                            "to its revenue base.",
            "confirmation": "1/2 — the Jul 2 cohort selloff is the first leg; not yet a sustained dispersion move.",
            "stop_quality": "1/1 — a fixed ratio stop (-5%) is a clean, defined failure threshold.",
        },
    },
    "MM-2026-038": {
        "instrument": (
            "Buy a 1-week EUR/USD put spread — e.g. buy the 1.135 put, sell the 1.115 put — defined-risk downside on "
            "the euro into the July 4 EU tariff/digital-tax deadline. Max loss is the premium. With spot ~1.145 after "
            "the soft-payroll bounce, both strikes are out-of-the-money — cheap convexity on the weekend tariff binary "
            "the closed tape is not pricing."
        ),
        "fundamental_thesis": (
            "The dollar is topping on the disarmed hike, so an outright short EUR/USD is fighting the tape — but the "
            "July 4 deadline is a specific, dated, EUR-negative binary that falls over a three-day weekend the US "
            "market is closed for. Trump's threat of a 100% tariff that 'supersedes' the 15% EU deal if the "
            "digital-services-tax fight is unresolved is exactly the kind of holiday-weekend escalation the tape gaps on "
            "at the Monday reopen. The soft-payroll bounce to ~1.145 is a BETTER entry for owning that tail cheaply. A "
            "defined-risk put spread owns the specific catalyst without betting against the topping dollar — and it lets "
            "the book trim the spot short (MM-012) while keeping the tariff hedge on."
        ),
        "catalysts": [
            "Jul 4 EU tariff / digital-tax deadline — the dated, EUR-negative binary over a closed weekend",
            "Trump's 100% 'supersede-the-deal' tariff threat — the escalation tripwire the tape isn't pricing",
            "EU 'respond swiftly and decisively' rhetoric — the retaliation risk that compounds the euro hit",
            "The soft-payroll EUR bounce to ~1.145 — the better entry for owning the downside tail",
        ],
        "risks": (
            "A clean EU-US deal by Jul 4 removes the tariff tail and the topping dollar lifts EUR/USD through 1.15; the "
            "spread decays as insurance that did not fire. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the market has priced the tariff tail to near-nil after the May 15% deal, but the "
                            "unresolved DST fight and a 100% threat keep it live.",
            "catalyst":     "2/2 — the Jul 4 deadline is dated and inside the structure's life; the closed weekend "
                            "amplifies the gap risk.",
            "positioning":  "1/2 — the market is complacent on the deal holding; a hard line is the pain trade.",
            "confirmation": "0/2 — EUR/USD is rising on the dollar top; no confirming down-move — a fresh, contrarian tail.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-039": {
        "instrument": (
            "Buy a July SPX 7,300/7,050 put spread — defined-risk index downside over the three-day weekend into the "
            "Jul 4 tariff deadline and a labour market cracking under a flattering u-rate. Buy the 7,300 put, sell the "
            "7,050 put. Max loss is the premium; the portfolio overlay on a book long AI equities. With the S&P at "
            "~7,483, both strikes are below spot — cheap convexity with VIX at ~16.6."
        ),
        "fundamental_thesis": (
            "The melt-up read the soft payroll as goldilocks and set a Dow record — then shut for a three-day weekend "
            "with a live Jul 4 tariff binary and a labour market softening under a participation-flattered 4.2% "
            "u-rate. That is the stagflation-trap tail the record tape is ignoring: the Fed can't hike into a cracking "
            "labour market and can't cut into sticky core PCE, and a tariff cost-push lands on top. VIX at ~16.6 makes "
            "below-spot convexity cheap. A July 7,300/7,050 put spread re-establishes the index hedge the book wants on "
            "an AI-heavy concentration that LAGGED the record (Nasdaq −0.80% on Jul 2) — structured for the discrete "
            "weekend-gap risk, not a chase of at-the-money premium."
        ),
        "catalysts": [
            "Jul 4 EU tariff / digital-tax deadline — a discrete risk-off catalyst over a closed weekend",
            "Labour market cracking (+57k, participation 61.5%) — the stagflation risk under the flattering u-rate",
            "Chips lagging the record (Nasdaq −0.80% Jul 2) — the AI-concentration vulnerability the index carries",
            "Warsh's hawkish line vs soft data — the policy-error risk the melt-up is not pricing",
        ],
        "risks": (
            "A clean tariff deal and a soft-landing repricing extend the melt-up and the S&P grinds higher into a calm "
            "reopen; vol stays crushed and the spread decays. Max loss is the premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the index prices the soft payroll as clean goldilocks while the stagflation trap and "
                            "the tariff tail argue for two-sided risk.",
            "catalyst":     "2/2 — the Jul 4 deadline is dated and inside the structure's life; the closed weekend adds gap risk.",
            "positioning":  "1/2 — sentiment is euphoric on the record; complacency (VIX ~16.6) is the room to fade.",
            "confirmation": "0/2 — the tape is at a record; no confirming down-leg — this is a fresh, pre-emptive hedge.",
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
    {"name": "MOVE", "level": "~100 (est)", "chg": "easier", "dir": "down"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Thu 2 Jul · NY Fed"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~100", "chg": "easier (est)", "dir": "down"},
]

# Per-trade open-book notes (shown in the "yesterday, graded" table).
NOTES = {
    "MM-2026-001": "FLAT, OFFSIDE-ISH. EUR/AUD ~1.649 — the record-tape risk-on keeps a bid under the commodity-AUD, pinning the cross mid-range, not toward the 1.61 target. No EUR catalyst left; edge thinned. Trim into strength. Stop 1.662 (close). Tight leash.",
    "MM-2026-004": "THE LAGGARD. 10Y ~4.485%, ~-1.0% from the 4.44% entry — the soft payroll rallied the FRONT end, not the back; term premium + supply pin the 10Y. Disinflation thesis intact but expressed better via the curve (MM-009). Hold on a tight rein. Stop 4.65% (~16bp).",
    "MM-2026-005": "FINALLY PAYING. Gold ripped toward $4,200 (~-7.6% from the $4,523 entry, recovering hard) as the +57k payroll priced out the hike and turned real rates — the exact relief this pre-position was built for. Held through the drawdown on its min-hold (to ~Jul 15); the rule captured the turn. Press via MM-036, not spot.",
    "MM-2026-007": "IMPROVING. USDJPY ~161.1, eased from the 162.4 pre-payroll spike as the soft print narrowed the differential and rolled the dollar. ~-1.1%. The topping dollar is finally the tailwind. Stop 163.00; defined-risk expression on the desk.",
    "MM-2026-009": "THE WINNER. 2s10s ~+35bp, ~+132% off the +15bp entry — a textbook bull-steepen as the front end rallied (2Y 4.137%) and the back end held (10Y 4.485%). The cleanest expression of the disarmed hawk. Min-hold ~Jul 16; trail the stop; stop -10bp; target +60bp.",
    "MM-2026-012": "THE WRONG FOOT. ~1.145 with DXY below 101 — the soft payroll knocked out the rate-differential engine that drove the 13-month-high dollar. Still green (~+1.3%), stop 1.182 distant, but the thesis has REVERSED. Trim toward flat; own only the Jul 4 tariff tail via MM-038.",
    "MM-2026-013": "GREEN, VINDICATED. 2Y ~4.14%, through the 4.162% entry, as the +57k print dropped Sep-hike odds to ~53% — the hike this trade fades is being priced out. Min-hold ~Jul 8; stop 4.35% (~21bp). Harvest and hold; the curve (MM-009) is the higher-conviction sibling.",
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
    {"datum": "US EQUITY + BOND MARKETS CLOSED Fri Jul 3 (Independence Day observed; Jul 4 is a Saturday). Brief covers the Thu Jul 2 session + Fri FX/gold + the weekend Jul 4 tariff binary. Reopen Mon Jul 6.",
     "source": "NYSE/Nasdaq + SIFMA calendar", "asof": TODAY, "stale": False},
    {"datum": "JUNE PAYROLLS (Thu Jul 2): +57,000 vs ~115k consensus — weakest in 4 months; Apr+May revised DOWN a combined 74,000. Unemployment FELL to 4.2% but participation dropped 0.3pp to 61.5% (lowest since Mar 2021). Wages +0.3% m/m.",
     "source": "BLS + CNBC + Yahoo Finance (corroborated)", "asof": "2026-07-02", "stale": False},
    {"datum": "September-hike odds fell to ~53% (CME FedWatch) from ~64% the prior day; 2Y 4.137% (−2bp), 10Y ~4.485% (sticky), 2s10s ~+35bp. The front end rallied, the long end did not.",
     "source": "CME FedWatch + FRED + CNBC (corroborated)", "asof": "2026-07-02", "stale": False},
    {"datum": "Thu Jul 2 US close: Dow 52,900.07 (+1.14%, +594.83, RECORD); S&P 500 7,483.24 (flat); Nasdaq Composite 25,832.67 (−0.80%) as chips slid. VIX ~16.6.",
     "source": "TheStreet + Trading Economics (corroborated)", "asof": "2026-07-02", "stale": False},
    {"datum": "FX/dollar (Fri Jul 3): DXY broke below 101 to ~100.7 (−0.66% on the week); EUR/USD bounced to ~1.145; USD/JPY eased to ~161.1. The rate-differential dollar bid reversed on the soft payroll.",
     "source": "FXStreet + Trading Economics (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Gold ripped toward $4,200 (Fri) on the soft payroll — the real-rates relief; WTI ~$68, Brent ~$71 as Hormuz transits keep recovering (vessels drifting to the Omani coast).",
     "source": "Trading Economics + Forbes (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Europe/Asia (Thu Jul 2): DAX +3.69%, FTSE +1.38%, STOXX 600 +1.96% on the soft-US-payroll risk-on; Nikkei −0.91% (TOPIX +1.30%). BTC ~$60k.",
     "source": "T. Rowe + Trading Economics (corroborated)", "asof": "2026-07-02", "stale": False},
    {"datum": "Warsh at Sintra (Tue Jul 1): 'prices are too high,' the Fed still 'in the price stability business' amid AI-productivity open-mindedness — a hawkish line the +57k payroll undercut a day later. Core PCE ~3.1%.",
     "source": "CNBC + C-SPAN + Bloomberg (corroborated)", "asof": "2026-07-01", "stale": False},
    {"datum": "Trump / Jul 4: deadline to lock the EU deal capping tariffs at 15%; the digital-services-tax fight is unresolved and Trump's 100% tariff threat would 'supersede' the deal. EU: 'respond swiftly and decisively.' PENDING.",
     "source": "CBS + PBS + Euronews (corroborated)", "asof": "2026-06-26", "stale": False},
    {"datum": "Iran/Hormuz: Doha talks made 'positive progress' (Jul 1); Iran issued a fresh warning on Hormuz transit routes (Jul 2) as vessels drift to the Omani coast. 60-day ceasefire from Jun 12 (MoU Jun 17) holds; sticking points = frozen assets, Hormuz tolls.",
     "source": "CNN (corroborated)", "asof": "2026-07-02", "stale": False},
    {"datum": "Credit near multi-decade tights: IG OAS ~80bp; benign. Semis: AMD ~+150% YTD at ~175x vs NVDA ~+13% YTD at ~32x (NVDA Q1 $81.6B +85% y/y; AMD $10.3B +38%).",
     "source": "S&P Global + Intellectia + Yahoo Finance (corroborated)", "asof": "2026-07-02", "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-07-02", "stale": True},
]

# No qualifying earnings names in the window (earnings_data.md, Jul 3 06:00 UTC: "No qualifying companies").
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
        "THE HAWK DISARMED. Kevin Warsh spent his Sintra debut (Jul 1) insisting 'prices are too high' — then June "
        "payrolls printed +57k vs ~115k with Apr+May revised down 74k, and the September-hike odds collapsed to ~53% "
        "from ~64%. The unemployment rate FELL to 4.2%, but only because participation dropped to 61.5% (lowest since "
        "Mar 2021) — a soft print in a strong-u-rate costume. The dollar rolled (DXY sub-101), the 2Y fell to 4.137%, "
        "gold ripped toward $4,200, and the Dow set a record (52,900.07, +1.14%) while the Nasdaq fell 0.80% as chips "
        "lagged. The book's rate longs won the disarming — the 2s10s steepener (MM-009) ~+132%, short-2Y (MM-013) "
        "green, gold (MM-005) finally paying; the leg on the wrong foot is short EUR/USD (MM-012) as the dollar tops. "
        "US markets are CLOSED today (Jul 3) into a Jul 4 EU-tariff binary. The melt-up reads a cracking labour market "
        "as goldilocks; the trade is to own the disinflation the curve is pricing and hedge the stagflation it is not."
    ),

    "summary_narrative": """
<p>The most important thing about the last 24 hours is that the data mugged the new Fed chair. Kevin Warsh spent his
international debut at Sintra on Tuesday insisting &ldquo;prices are too high&rdquo; and that the Fed remains
&ldquo;in the price stability business&rdquo; &mdash; arming the market for a September hike it had priced near 64%.
On Thursday June payrolls printed <strong>+57,000</strong> against a ~115k consensus, the weakest in four months, with
April and May revised down a combined <strong>74,000</strong>. September-hike odds collapsed to <strong>~53%</strong>,
the dollar broke below 101, the 2Y fell to 4.137%, and gold ripped toward $4,200. The hawk was disarmed by his own
labour market inside a single session. (BLS, CNBC, FRED.)</p>

<p>Decompose the number the tape is celebrating. The headline the melt-up latched onto is the unemployment rate
<em>falling</em> to 4.2% &mdash; but it fell for the wrong reason: participation collapsed 0.3pp to <strong>61.5%</strong>,
the lowest since March 2021. A soft print wearing a strong-u-rate costume. The anatomy says the labour market is not
tight, it is emptying: people are leaving the workforce faster than jobs are lost, which flatters the rate and hides
the crack. So what, who is wrong, what is the trade &mdash; the consensus that reads a record Dow and a disarmed hike
as clean goldilocks is wrong; the bond market that fought the dots for a month just got its data, and the front-end
rally has room. (BLS, Yahoo Finance.)</p>

<p>The second-order effect consensus is missing is the trap. A labour market softening this fast while core PCE is
still ~3.1% and two cost-push fronts are live &mdash; the silicon-DRAM inflation and a July 4 tariff deadline &mdash;
is not goldilocks, it is the front edge of stagflation. The Fed cannot hike into a cracking labour market and cannot
cut into sticky inflation. The melt-up is pricing the dovish half and ignoring the sticky half. And Warsh is now
politically boxed: he staked his credibility on hawkishness at Sintra and the data undercut him a day later, so he
holds a line he can no longer fully justify. (CNBC, C-SPAN.)</p>

<p>The book sits on the right side of the disarming. The 2s10s steepener (MM-009) ripped to <strong>~+132%</strong> as
the front end rallied harder than the back; the short-2Y (MM-013) is green as the hike it fades gets priced out; the
short-10Y (MM-004) lags because the long end is sticky on term premium and supply. Gold (MM-005), held through a
brutal drawdown on its min-hold, is finally paying. The leg now on the wrong foot is short EUR/USD (MM-012): the
13-month-high dollar that vindicated it is topping as the rate-differential engine reverses &mdash; trim it, do not
defend it, and let the July 4 tariff deadline be the only reason to hold any short-euro risk.</p>

<p>The tape is closed for a three-day weekend over a live tariff binary (US markets shut today, Independence Day
observed, reopen Monday). The regime is no longer &lsquo;no shock sticks.&rsquo; It is that the one shock that stuck
&mdash; a cracking labour market &mdash; is being mistaken for good news, and the trade is to own the disinflation the
curve is finally pricing while hedging the stagflation the melt-up is not.</p>
""",

    "takeaways": [
        "<strong>A +57k payroll disarmed the hawk in 24 hours.</strong> Warsh insisted 'prices are too high' at Sintra "
        "Tuesday; Thursday's print (+57k vs ~115k, Apr+May revised −74k) dropped September-hike odds to ~53% from ~64%. "
        "The bond market that fought the dots for a month just got its data. (BLS, CNBC.)",

        "<strong>The u-rate fell for the wrong reason.</strong> Unemployment dropped to 4.2%, but only because "
        "participation collapsed to 61.5% &mdash; the lowest since March 2021. A soft labour market in a strong-u-rate "
        "costume: people are leaving the workforce, not finding jobs. The headline says tight; the anatomy says "
        "emptying. (BLS, Yahoo Finance.)",

        "<strong>The disarming is the trade &mdash; and the book is on it.</strong> A Fed that can't hike into a "
        "cracking labour market re-steepens the curve through the front: the 2s10s steepener (MM-009) ripped to "
        "~+132%, the short-2Y (MM-013) is green, and gold (MM-005) is finally paying as real rates fall. The front-end "
        "rally has room; the 10Y (MM-004) lags on a sticky back end. (CME, FRED.)",

        "<strong>The dollar top is the risk to the euro short.</strong> DXY broke below 101 to ~100.7 and EUR/USD "
        "bounced to ~1.145 as the rate-differential engine reversed. Short EUR/USD (MM-012) is still green but its "
        "thesis has turned &mdash; trim toward flat and own only the July 4 tariff tail via a defined-risk put spread "
        "(MM-038). (FXStreet, Trading Economics.)",

        "<strong>The melt-up is a Dow record, not a tech one.</strong> Thursday's +594-point Dow record (52,900.07) "
        "was a value/financials broadening; the Nasdaq FELL 0.80% as chips slid, and the S&amp;P finished flat at "
        "7,483.24. The narrow AI concentration lagged the record &mdash; own the dispersion (long NVDA / short "
        "overbought AMD, MM-037), not the crowd. (TheStreet, Intellectia.)",

        "<strong>The stagflation trap is the unpriced tail.</strong> A cracking labour market + sticky core PCE (~3.1%) "
        "+ two cost-pushes (silicon-DRAM, July 4 tariff) is not goldilocks. The tape shut for a three-day weekend over "
        "a live tariff binary with VIX at ~16.6 &mdash; a July SPX put spread (MM-039) owns the gap the record tape is "
        "ignoring.",

        "<strong>Gold flipped engines.</strong> After a month trading as a real-rates short &mdash; it barely moved on "
        "literal US-Iran strikes &mdash; gold ripped toward $4,200 on the soft payroll. Lower policy rates, a topping "
        "dollar, and a stagflation debasement bid all push the same way. Own the continuation with defined risk "
        "(MM-036), not a chase of spot. (Trading Economics.)",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "Clean disinflationary soft landing — the disarmed hike becomes cuts and the melt-up broadens",
         "body": "The soft payroll is the start of a benign cooling: the next CPI confirms disinflation, the Fed drops "
                 "the hawkish line, and September-hike odds fall toward zero as cut-pricing begins for late 2026. The "
                 "2Y extends below 4.05%, the curve steepens toward +50bp (MM-009/013 keep working), the dollar top "
                 "holds (MM-012 to trim), gold extends (MM-005/036), and the record tape broadens beyond a narrow AI "
                 "cohort. A clean EU-US deal removes the tariff tail. Risk up · rates down (front) · dollar soft · "
                 "gold up · oil soft."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "The stagflation bind holds — soft labour, sticky core, a boxed-in Fed and range-bound risk",
         "body": "The labour market keeps softening under a flattering u-rate while core PCE stays ~3.1% and the "
                 "silicon/tariff cost-pushes keep goods sticky. Warsh holds a hawkish hold he can't justify or execute; "
                 "the 2Y ranges ~4.05-4.20%, the curve stays steep (MM-009), gold grinds higher on the debasement bid "
                 "(MM-036), and the dollar drifts lower (trim MM-012). Equities chop at the record as the July 4 "
                 "tariff outcome caps risk appetite. Risk mixed · rates steady · dollar soft · gold firm · curve steep."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "A shock re-arms the hawk or breaks the melt-up — hot CPI/tariff or a labour-led risk-off",
         "body": "Either a hot CPI or a July 4 tariff escalation re-lifts inflation expectations and re-arms the "
                 "September hike, backing the 2Y toward the 4.35% stop and bear-flattening the curve (the risk to "
                 "MM-009/013) while gold gives back the bounce; or the labour crack accelerates into a growth scare "
                 "that hits the AI-concentrated index (the Nasdaq that already lagged the record), and the S&amp;P "
                 "retraces toward 7,300 where MM-039 pays. Either way the melt-up's goldilocks read breaks. Risk down · "
                 "rates two-way · dollar bid (risk-off) · gold two-way."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a Fed chair who got disarmed by his own data. Kevin Warsh used his Sintra debut
to insist prices are too high and keep a September hike live; a day later June payrolls printed +57,000 with the prior
two months revised down 74,000, and the hike odds fell from ~64% to ~53%. The dollar rolled below 101, the front end
of the curve rallied, and gold ripped. The non-consensus read is that this is not the clean disinflation the record
Dow is celebrating: a labour market softening this fast while core PCE holds ~3.1% and two cost-pushes run into a July
4 deadline is the front edge of stagflation, and a Fed that can neither hike nor cut is the trap under the melt-up.</p>

<p>The counter-intuitive hook is hiding in the unemployment rate. It FELL to 4.2%, which reads as strength and would
ordinarily re-arm the hawk &mdash; but it fell because participation collapsed 0.3pp to 61.5%, the lowest since March
2021. The labour market is not tightening, it is emptying: the denominator is shrinking faster than jobs are lost. The
market took the falling rate as reassurance; the composition says the opposite, and it is the composition that decides
whether the next print is a soft landing or the start of a contraction.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong> +57k
payrolls, −74k revisions, participation 61.5%, core PCE ~3.1%, gold $4,200, DXY sub-101, chips lagging a record Dow.
<strong>What is priced:</strong> ~53% September-hike odds, a 2Y at 4.137%, a 2s10s at +35bp, a record Dow and a flat
S&amp;P, VIX ~16.6, a July 4 tariff deal assumed to hold. <strong>Consensus narrative:</strong> &lsquo;the hike is off
the table, inflation is beaten, buy the goldilocks melt-up.&rsquo; The gap &mdash; and the alpha &mdash; is that the
market is pricing the dovish half of a stagflation bind and ignoring the sticky half, and it is complacent on a tariff
binary it shut the tape for.</p>

<p>Go around the world. <strong>US:</strong> a Dow record on the disarmed hike, but the Nasdaq fell 0.80% as chips
slid &mdash; a value/financials broadening, not a tech melt-up. <strong>Europe:</strong> the biggest beneficiary of the
soft US payroll &mdash; the DAX +3.69%, FTSE +1.38%, STOXX 600 +1.96% on the risk-on and a softer dollar, but LVMH and
the platforms sit in the July 4 tariff/digital-tax crosshairs. <strong>Japan:</strong> the Nikkei −0.91% (TOPIX
+1.30%), the yen firming toward 161 as the dollar tops (MM-007). <strong>Middle East:</strong> Doha talks made
'positive progress' but Iran issued a fresh Hormuz-route warning as tankers drift to the Omani coast &mdash; the
ceasefire holds, the war tail is cheap and unpriced.</p>

<p>The political angle runs on two constraints. The Papic read on the Fed: Warsh is a brand-new chair who staked his
international debut on hawkishness and watched the data undercut him 24 hours later &mdash; he is boxed into holding a
line he cannot justify, which keeps the front end volatile and the policy path uncertain. The second constraint is
trade: the July 4 deadline to lock the 15% EU deal collides with an unresolved digital-services-tax fight and a 100%
tariff threat that 'supersedes' the deal. The non-consensus read is that Trump has every incentive to escalate the DST
fight over a closed weekend, and the market &mdash; shut for three days &mdash; is not positioned for the Monday gap.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the stagflation trap (the curve steepener, MM-009, and the index
hedge, MM-039); the gold continuation off the engine-flip (MM-036); the July 4 tariff tail (MM-038); the chip
dispersion (MM-037). <strong>Fairly priced:</strong> the disarmed September hike; the front-end rally.
<strong>Fully priced:</strong> the falling u-rate as a sign of labour strength (it is the opposite).
<strong>Over-priced (at risk):</strong> the durability of the 13-month-high dollar (MM-012, to trim) and the goldilocks
read of a record tape resting on a cracking labour market.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is the trap hiding inside a soft jobs number everyone
read as good news. Kevin Warsh spent his first turn on the international stage in Sintra telling the world prices were
too high and the Fed would keep a hike on the table; the next day the labour market printed fifty-seven thousand jobs,
revised away seventy-four thousand more, and priced the hike he was defending out to a coin flip. The tape cheered
&mdash; the Dow closed at a record. But a labour market cracking this fast while core inflation sticks near three and a
tenth, with a chip-driven goods shock and a tariff deadline both live, is not the all-clear. It is the front edge of a
bind where the Fed can neither hike nor cut, and the market is pricing only the pleasant half of it.</p>

<p>Decompose the number, because the composition is the whole story. The unemployment rate fell to four-point-two, and
the melt-up treated that as strength. It was not. The rate fell because the participation rate collapsed three-tenths
to sixty-one-and-a-half percent, the lowest since the pandemic aftermath &mdash; people left the workforce faster than
jobs disappeared, and a shrinking denominator flattered the headline. So what, who is wrong, what is the trade: the
consensus reading a falling rate as a tight labour market is wrong at the level of arithmetic, and the trade is to side
with the bond market, which looked through the headline, rallied the front end, and told you the hike is dead.</p>

<p>Trace it to a flow, because the durable move is in the dollar, not the equity print. The greenback broke below a
hundred-and-one and gave back its week because the single engine driving it &mdash; a rate differential built on a
hawkish Fed pricing a hike &mdash; lost its fuel the instant the payroll hit. The thirteen-month-high dollar was never
a growth story; it was a positioning, a rates-carry bid that pulled capital into US assets on the promise of higher
policy rates. Kill the hike and you kill the bid, and the unwind is faster than the build because the crowd is all on
one side. That is why the book's short-euro leg is the one now on the wrong foot, and why the only reason left to hold
any short-euro risk is a tariff deadline, not a rate view.</p>

<p>The Burry tell sits one number below the one everyone watched. Forget the payroll count; watch participation. A
labour force shrinking to a sixty-one-and-a-half handle is not a one-month wobble &mdash; it is the intersection of
demographics, a post-pandemic behavioural shift that never fully reversed, and the first faint signal of AI displacement
in the professional-and-business-services line that has carried hiring. If participation keeps falling, the
unemployment rate will keep looking benign while the actual labour market deteriorates underneath it, and the Fed &mdash;
anchored to a rate that lies &mdash; will be late again, either holding hawkish into a contraction or capitulating into
sticky inflation. The number that matters over the next six months is the one the melt-up ignored.</p>

<p>So the posture into a closed three-day weekend is to press what the disarming pays and hedge what it hides. The
curve steepener is the cleanest expression on the board and it is trailed, not chased; the front-end short is harvested
and held; gold, denied its catalyst for a month, finally has one, and the continuation is owned with defined risk
rather than a chase of spot. The euro short is trimmed toward flat because its engine reversed, its remaining edge
carried only in a defined-risk tariff-tail put spread. And fresh money buys the two things the record tape is not
pricing: the dispersion inside a chip cohort that lagged the record, and an index hedge into a tariff binary the market
shut its doors for. The tape decided a cracking labour market is good news. The brief's read is that it is the one shock
that finally stuck &mdash; and the melt-up will find that out on the other side of the weekend.</p>
""",

    "correlation_regime": """
<p><strong>1. The dollar decoupled from the equity melt-up &mdash; the biggest break on the board.</strong> A record
Dow would normally travel with a firm dollar; instead DXY broke below 101 to ~100.7 while equities set records,
because the soft payroll killed the rate-differential bid that drove the dollar even as it fed the goldilocks equity
read. The dominant driver in FX just changed from rate-carry to relative-growth, and the crowded 13-month-high dollar
long is the wrong side. That is exactly why short EUR/USD (MM-012) is the leg to trim, not defend.</p>

<p><strong>2. Gold re-coupled to real rates &mdash; the opposite of last week.</strong> Through the June strikes gold
traded as a real-rates SHORT: it fell on a hawkish Fed and barely moved on literal US-Iran fire. The +57k payroll
flipped it &mdash; gold ripped toward $4,200 as hike odds collapsed and the dollar rolled. The driver switched from
'dollar/real-rates headwind' back to 'rate-cut/debasement tailwind,' and that regime change is why the book's long
(MM-005) finally pays and the continuation is worth owning (MM-036).</p>

<p><strong>3. The curve decoupled from the level &mdash; a bull-steepening the Fed's line denies.</strong> The soft
payroll rallied the 2Y to 4.137% but left the 10Y at ~4.485%, so the 2s10s widened to ~+35bp. Front and back are now
driven by different forces: the front by a disarmed hike, the back by term premium and supply that a stagflation read
and a July 4 tariff cost-push keep heavy. A steepening this clean means the dominant rates driver split in two &mdash;
own the shape (MM-009), not outright long-end duration (why MM-004 lags).</p>

<p><strong>4. US tech decoupled from the US index.</strong> The Dow set a record while the Nasdaq fell 0.80% &mdash; the
melt-up broadened into value and financials as the narrow AI cohort lagged. The correlation break says the leadership
baton is passing from concentration to breadth on the disarmed hike; inside the laggard cohort, own the dispersion
(long NVDA ~32x vs short AMD ~175x, MM-037) rather than the index-level chase.</p>
""",

    "vol_skew": """
<p><strong>The cheapest convexity on the board is an index hedge into a tariff binary the market shut its doors
for.</strong> VIX closed ~16.6, the term structure in contango (est. VIX9D ~15.5 · VIX ~16.6 · VIX3M ~18.0 · VIX6M
~19.0), and MOVE eased toward ~100 as the front-end rally calmed rates vol. The tape is pricing the disarmed hike as
one-way goldilocks and closed for a three-day weekend at a record &mdash; precisely when a July 4 tariff escalation or
a Monday-gap risk-off is cheap to own. The headline trade implication: a July SPX 7,300/7,050 put spread (MM-039),
defined-risk below-spot convexity on the stagflation-trap tail the record tape is ignoring. The FX complement is a
1-week EUR/USD put spread (MM-038) &mdash; own the specific July 4 EU digital-tax/tariff tail over the closed weekend,
struck below the soft-payroll bounce to ~1.145. And the commodity leg is a long-gamma gold call spread (MM-036) that
owns the rate-cut repricing that just began. If nothing sticks, all three decay cheaply; if any tail fires over the
weekend, the convexity is owned, not chased at the Monday open.</p>
""",

    "sector_rv": """
<p><strong>Leading (Thu Jul 2 into the close):</strong> value, financials and the broadening trade &mdash; the Dow set
a +594-point record on the disarmed hike and a steeper curve that lifts net-interest margins; European equities were
the biggest winners of the softer dollar (DAX +3.69%, FTSE +1.38%, STOXX 600 +1.96%). Gold miners and bullion on the
real-rates turn. <strong>Lagging:</strong> the AI/semis complex &mdash; the Nasdaq fell 0.80% into a Dow record as
chips slid on AI-margin and mega-IPO-rotation worries; energy as crude sits ~$68/$71 on the Hormuz recovery; the
consumer-hardware box-makers eating the DRAM cost. <strong>Today/next:</strong> US markets CLOSED (Jul 3); the July 4
tariff deadline over the weekend; the next CPI is the catalyst that confirms the disinflation or re-arms the hawk.</p>

<p><strong>RV:</strong> Two fit today's tape cleanly. First, the chip dispersion (MM-037): long NVDA (~32x on $81.6B Q1
revenue) vs SHORT AMD (~175x, +150% YTD) &mdash; the cohort sold as a unit on Jul 2, the setup for the valuation gap to
close, and it doubles as book housekeeping (trim the exhausted AMD winner, add the laggard NVDA). Second, the
cross-region read: US financials/value over EU-exposed platforms and luxury (LVMH, the software names) into the July 4
tariff/digital-tax escalation. Both are low beta to the index and high beta to the regime's live drivers &mdash; the
leadership rotation and the tariff binary &mdash; and neither chases the record.</p>
""",

    "positioning": """
<p><strong>The crowd is positioned for a clean soft landing &mdash; long the melt-up, long the dollar, short
duration into a hike that just died.</strong> The loudest lean is the dollar: the 13-month-high DXY long is a crowded
rate-carry position that lost its engine when the September hike was priced out, so the pain trade is the dollar
unwinding faster than it built (why MM-012 is the leg to trim, not defend). In rates, fast money is still net-short
duration post-Warsh, so the pain trade is the front-end rally extending on the soft data &mdash; the squeeze the
rescued longs (MM-009/013) ride, with the RSI on the 2Y confirming the front end is not yet overbought. In equities,
the record tape is euphoric and narrow at the same time: long the index at a record while the AI cohort that carried it
lagged, so the pain trade is the concentration cracking (the dispersion, MM-037; the index hedge, MM-039). In gold, the
spec long was washed out through June, leaving clean, squeeze-prone positioning into the payroll turn (MM-005/036). The
pain trade everywhere is the same &mdash; a market that has decided a cracking labour market is unambiguously good news.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; the disarmed hike does not move the funding rate, and the soft payroll produced
no stress in the plumbing. <strong>The Pozsar mechanic:</strong> trace the dollar move to a flow, not a narrative. The
13-month-high dollar was never a growth story &mdash; it was a rate-carry bid, capital pulled into US assets on the
promise of a higher policy rate, a positioning built on the Fed's hawkish path. The +57k payroll cut September-hike
odds to ~53% and severed that bid at the source, which is why DXY broke below 101 in a single session: kill the
differential and the carry flow reverses, and it reverses faster than it accumulated because the crowd is all on one
side. Underneath, the durable real-economy flow is unchanged &mdash; hyperscaler capex (Microsoft, Google, Meta,
Amazon), increasingly debt-funded, still bidding the memory supply chain and keeping core goods sticky, which is the
sticky-inflation half of the stagflation bind. The funding angle that matters next is the collision of a heavy IG
issuance calendar (2026 high-grade supply ~$2.25tn, +35% y/y on AI capex) with a long end that would NOT rally on the
soft payroll &mdash; the 10Y held ~4.485% while the 2Y fell. Watch IG issuance and the 10Y together: the back end is
where the fiscal-supply-plus-sticky-inflation flow shows up, and it is why the curve, not duration, is the trade.</p>
""",

    "tape_missing": """
<p><strong>The market took a falling unemployment rate as strength &mdash; it is the opposite.</strong> The u-rate fell
to 4.2% only because participation collapsed to 61.5%, the lowest since March 2021; the labour force is shrinking
faster than jobs are lost. The falsifiable level: another sub-62% participation print alongside sub-100k payrolls says
the labour market is contracting behind a benign headline, and the Fed &mdash; anchored to a rate that lies &mdash; is
late. Watch participation and the payroll trend together; if both keep falling, the goldilocks read breaks and the
index hedge (MM-039) pays.</p>

<p><strong>Just behind it: the long end refused to rally on the soft payroll.</strong> The 2Y fell to 4.137% but the
10Y held ~4.485% &mdash; the bond market rallied the Fed path and left the term premium alone, because fiscal supply
and a July 4 tariff cost-push keep the back end heavy. The falsifiable line: a 10Y that breaks below 4.40% says the
disinflation is winning the whole curve (MM-004 finally pays); a 10Y that backs up toward 4.60% on supply/tariffs says
the stagflation read is right and the steepener (MM-009) is the only rate trade that works. The next CPI and the
quarterly refunding are the tests.</p>

<p><strong>The Burry tell &mdash; the number below the number.</strong> Everyone watched the payroll count; the
structural signal is participation at 61.5%. A labour force shrinking to a sixty-one handle is the intersection of
demographics, a post-pandemic behavioural shift that never reversed, and the first faint read of AI displacement in the
professional-and-business-services hiring that has carried the cycle. Over the next two-to-three quarters this resolves
one of two ways: either participation keeps falling and the unemployment rate stays artificially low while the real
labour market deteriorates &mdash; trapping a hawkish Fed into a contraction &mdash; or the displacement thesis is
premature and hiring re-accelerates into the sticky inflation, forcing the hike back on. Both are stagflationary; the
equity index, at a record and concentrated in the AI names that are simultaneously the productivity promise and the
displacement cause, is the least prepared for either.</p>
""",

    "book_outlook": {
        "commentary": (
            "The soft payroll is a two-sided event for this book, and the split is the story today. The rate/real-asset "
            "side got paid: <b>Xetra-Gold (4GLD)</b>, the book's tail hedge, finally fired &mdash; gold ripped toward "
            "$4,200 as the +57k print priced out the hike and turned real rates, exactly the scenario 4GLD exists for "
            "after a month of doing nothing on literal Gulf strikes. The <b>UST 1.25% 2031</b> and <b>Siemens EUR IG</b> "
            "get a modest bid from the front-end rally, but the long end stayed sticky (10Y ~4.485%), so the duration "
            "relief is partial. The problem side is the currency: the book is ~72% USD against an EUR base, and the "
            "dollar broke below 101 on the payroll &mdash; the FX translation is now a HEADWIND, the mirror image of the "
            "tailwind it was through June (this is the same regime turn that puts the desk's short EUR/USD, MM-012, on "
            "the wrong foot). The AI sleeve &mdash; <b>Micron</b> (largest weight), <b>NVDA</b> (−10.5%), <b>AVGO</b> "
            "(−21.3%), <b>AMD</b> (+394%) &mdash; LAGGED the record: the Dow set a record while the Nasdaq fell 0.80% as "
            "chips slid, so the concentration underperformed the broadening. And <b>LVMH</b> and <b>SAP</b> carry the "
            "specific July 4 EU digital-tax/tariff tail over the closed weekend. The dominant action: recognise 4GLD is "
            "finally working and let it run (do not take profit into the turn); trim the overbought <b>AMD</b> winner "
            "into the NVDA/AMD dispersion (MM-037); hedge the USD-translation and the tariff tail rather than the AI "
            "names; and note the bond sleeve's relief is a front-end story, not a long-end one."
        ),
        "outperform": [
            {"name": "Xetra-Gold (4GLD) — the tail hedge that finally fired", "why": "Gold ripped toward $4,200 on the "
             "soft payroll as September-hike odds fell to ~53% and real rates turned &mdash; the exact real-rates relief "
             "4GLD is held for. After doing nothing on literal Gulf strikes, the hedge is working; this is the day it "
             "leads the book (mirrors the desk's MM-005/036)."},
            {"name": "The bond sleeve (UST 1.25% 2031, Siemens EUR IG) — front-end relief", "why": "The +57k print "
             "rallied the 2Y to 4.137% and priced out the hike, giving both underwater bonds a bid &mdash; but the 10Y "
             "held ~4.485%, so the relief is partial and front-end-led. It leads the defensive part of the book (mirrors "
             "the rate longs MM-009/013), not a full duration recovery."},
            {"name": "AMD (+394%) — but trim it into the dispersion", "why": "AMD is the book's biggest chip winner and "
             "held up better than the cohort, but at ~175x vs NVDA's ~32x it is the overbought leg the next AI selloff "
             "targets first. It 'outperforms' today only as the trim candidate &mdash; sell into strength to fund the "
             "NVDA/AMD dispersion (MM-037)."},
        ],
        "underperform": [
            {"name": "USD sleeve / USD assets (~72% of the book)", "why": "The dollar broke below 101 on the soft "
             "payroll, so the FX translation flipped from tailwind to HEADWIND for the EUR-base book &mdash; the exact "
             "regime turn that puts the desk's short EUR/USD (MM-012) on the wrong foot. The book is structurally long "
             "the currency now losing; hedge the translation, don't ride it."},
            {"name": "The AI concentration (Micron, NVDA, AVGO) — lagged the record", "why": "The Dow set a record "
             "while the Nasdaq fell 0.80% as chips slid on AI-margin and rotation worries. A book this concentrated in "
             "the AI cohort underperformed the value/financials broadening the disarmed hike drove &mdash; the "
             "concentration is the drag on a record day."},
            {"name": "LVMH & SAP — the July 4 EU tariff/digital-tax crosshairs", "why": "Trump's 100% "
             "'supersede-the-deal' tariff threat targets EU platforms and luxury, and the DST fight is unresolved into "
             "the July 4 deadline &mdash; over a weekend the tape is closed for. LVMH (−20.5%) and SAP carry the "
             "specific Monday-gap risk; own the tail via MM-038, don't sit naked."},
        ],
        "watch": [
            {"label": "Let 4GLD run — the tail hedge is finally paying, don't take profit into the turn",
             "text": "For a month gold did nothing while the book needed it; the soft payroll flipped its engine and it "
             "ripped to $4,200. This is not the moment to bank the hedge &mdash; lower policy rates, a topping dollar "
             "and a stagflation debasement bid all push the same way. Recognise 4GLD as the protective winner it was "
             "held to be, and press the continuation with a defined-risk call spread (MM-036) rather than adding spot."},
            {"label": "Hedge the USD translation, not the AI names — the dollar top is the new headwind",
             "text": "The book's ~72% USD sleeve just turned from FX tailwind to headwind as the dollar broke 101. The "
             "clean fix is a EUR-USD hedge on part of the sleeve (a seagull or collar) to lock the June translation gain "
             "before the rate-differential narrative fully turns &mdash; the mirror of trimming the desk's short "
             "EUR/USD (MM-012). Separately, own the specific July 4 tariff tail on the EUR-exposed equities via a "
             "defined-risk EUR/USD put spread (MM-038)."},
            {"label": "Trim AMD into the NVDA dispersion — manage the chip concentration on the laggard tape",
             "text": "The chip sleeve lagged the record, and within it AMD (~175x, +150% YTD) is the exhausted winner "
             "against NVDA (~32x, the house-liked laggard the book is down on). Trim AMD into strength and rotate toward "
             "NVDA &mdash; the RV (MM-037) is concentration-neutral and doubles as the housekeeping the record-tape "
             "underperformance calls for. Do not add to the AI cohort naked into the next selloff."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> the September hike is dead, inflation is beaten, and the soft payroll is clean
goldilocks &mdash; a Fed that steps back, a dollar that eases, a record Dow that broadens. Buy the melt-up; the labour
cooling is the disinflation the doves wanted, and the July 4 tariff deadline will be papered over like every one before
it.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> 'clean goldilocks' misreads both the number and
the setup. The unemployment rate fell only because participation collapsed to a March-2021 low &mdash; the labour
market is emptying, not tightening &mdash; and core PCE is still ~3.1% with two live cost-pushes (silicon-DRAM, a July
4 tariff). That is a stagflation bind, not a soft landing: a Fed that can neither hike nor cut. The crowded side is long
a record tape and a topping dollar; the cheaper side owns the curve steepener (MM-009), the gold continuation (MM-036),
the tariff tail (MM-038), and the index hedge (MM-039) into a weekend the market shut its doors for.</p>
""",

    "one_chart": """
<p class="theme">The labour force participation rate at 61.5% is the chart &mdash; the number below the number that says the falling unemployment rate is a mirage.</p>
<p>The single thing the market should watch is participation, not the payroll count. The unemployment rate fell to 4.2%
and the tape read strength; it fell because participation dropped 0.3pp to 61.5%, the lowest since March 2021. That is
the difference between a tight labour market and an emptying one, and it decides whether the Fed is looking at a soft
landing or the front edge of a contraction. The level that resolves it is participation on the next print: a further
fall alongside sub-100k payrolls confirms the labour market is deteriorating behind a benign headline &mdash; the
stagflation read that keeps the curve steep (MM-009), the index hedged (MM-039) and gold bid (MM-036); a rebound toward
62%+ with firmer payrolls says the softness was a blip and re-arms the September hike (the risk to the rate longs). Own
the steepener and the hedges while the participation trend points down, and keep the gold continuation as the play on
the real-rates turn the payroll just began.</p>
""",

    "catalyst_calendar": [
        {"day": "Tue", "date": "Jul 1 ✓",
         "event": "Warsh's Sintra debut — hawkish 'prices are too high'",
         "consensus": "New Fed chair Kevin Warsh's first major international appearance, on a panel with Lagarde, Bailey "
                      "and Macklem at the ECB Forum. He insisted the Fed remains 'in the price stability business' and "
                      "that prices are too high, keeping a September hike live (~64% odds). Sources: CNBC, C-SPAN, Bloomberg.",
         "view": ("The hawk armed the market &mdash; and set himself up to be disarmed a day later. A brand-new chair "
                  "staking his credibility on hawkishness is politically boxed when the data turns."),
         "asymmetry": "The hawkish line is a two-way front-end vol source: it makes the soft-payroll squeeze (MM-013) "
                      "sharper and the hot-CPI re-arm (the risk to the rate longs) more violent.",
         "dir": "flat"},
        {"day": "Thu", "date": "Jul 2 ✓",
         "event": "June PAYROLLS — the print that disarmed the hawk",
         "consensus": "June NFP +57,000 vs ~115k consensus, weakest in four months; Apr+May revised DOWN 74,000. "
                      "Unemployment FELL to 4.2% on a participation collapse to 61.5% (lowest since Mar 2021). "
                      "September-hike odds fell to ~53% from ~64%; the 2Y dropped to 4.137%. Sources: BLS, CNBC, FRED.",
         "view": "The soft print priced out the hike and rallied the front end &mdash; but the falling u-rate is a "
                 "participation mirage, not labour strength. The stagflation bind, not the soft landing.",
         "asymmetry": "The front-end rally squeezes the crowded short-duration trade (MM-009/013 pay); the sticky "
                      "long end (10Y ~4.485%) keeps the steepener the higher-conviction expression than outright duration.",
         "dir": "up"},
        {"day": "Fri", "date": "Jul 3 — TODAY",
         "event": "US equity + bond markets CLOSED (Independence Day observed)",
         "consensus": "NYSE, Nasdaq and (per SIFMA) the bond market are closed Friday July 3, as July 4 falls on a "
                      "Saturday. FX and gold trade; the dollar sits sub-101 and gold near $4,200. Reopen Monday July 6. "
                      "Sources: NYSE/Nasdaq calendar, SIFMA.",
         "view": "A closed tape into a live tariff binary is a gap-risk setup: any July 4 escalation is priced only at "
                 "the Monday open, and the market is not positioned for it.",
         "asymmetry": "Own the weekend gap with defined risk &mdash; the EUR/USD tariff-tail put spread (MM-038) and "
                      "the SPX put spread (MM-039); both decay cheaply if nothing sticks.",
         "dir": "flat"},
        {"day": "Sat", "date": "Jul 4",
         "event": "EU-US trade & digital-services-tax deadline",
         "consensus": "The deadline to lock the EU deal capping most tariffs at 15%. The digital-services-tax fight is "
                      "unresolved and Trump's threat of a 100% tariff that 'supersedes' the deal is live; the EU says it "
                      "will 'respond swiftly and decisively.' Sources: CBS, PBS, Euronews.",
         "view": "A binary over a closed weekend: a clean deal is risk-on and EUR-supportive; a hard line on the DST is "
                 "a fresh cost-push that lands on EU platforms/luxury and reprices the euro at the Monday open.",
         "asymmetry": "A hard line is EUR-negative + EU-equity-negative (MM-038 pays, LVMH/SAP hit); a deal caps the "
                      "euro downside and confirms the dollar top (trim MM-012).",
         "dir": "down"},
        {"day": "Mon", "date": "Jul 6",
         "event": "Reopen — the weekend gap gets priced",
         "consensus": "US markets reopen and price three days of tariff headlines, weekend geopolitics (Iran/Hormuz "
                      "Doha talks, Hormuz-route warnings) and the follow-through on the disarmed-hike repricing. Source: market calendar.",
         "view": "The first session that marks the July 4 outcome and tests whether the soft-payroll dollar top and "
                 "front-end rally hold. The steepener (MM-009) and gold (MM-036) are the base-case winners.",
         "asymmetry": "A benign weekend extends the melt-up and the dollar top (MM-012 trim, MM-036 pays); an "
                      "escalation gaps risk lower (MM-039 pays) and re-bids the dollar as a haven.",
         "dir": "flat"},
        {"day": "Next wk", "date": "Jul (TBC)",
         "event": "June CPI — the decider between soft landing and stagflation",
         "consensus": "The next CPI is the catalyst that confirms the disinflation the soft payroll implied or re-arms "
                      "the September hike Warsh is defending. Core PCE is running ~3.1%. Source: BLS.",
         "view": "The single number that resolves the regime: a soft CPI confirms the disarmed hike and the front-end "
                 "rally; a hot one (silicon/tariff cost-push) re-arms the hawk and backs up the 2Y.",
         "asymmetry": "A soft CPI extends the steepener and gold (MM-009/036); a hot one backs the 2Y toward the 4.35% "
                      "stop (MM-013 risk) and pays the index hedge (MM-039).",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.662 (the stop). At ~1.649 — flat, pinned mid-range as the record-tape risk-on keeps an AUD bid; edge thinned, stop close. Trim into strength; tight leash.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.485% — the LAGGARD; the soft payroll rallied the front end, not the back (term premium + supply pin the 10Y). Expressed better via the curve (MM-009). A break below 4.40% is the confirmation; hold on a tight rein.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250. At ~$4,200 — FINALLY PAYING; the +57k payroll turned real rates and the engine flipped from real-rates short to rate-cut long. Held through the drawdown on its min-hold; press via MM-036, not spot.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~161.1 — improving, eased off the 162.4 pre-payroll spike as the differential narrowed and the dollar topped. The topping dollar is the tailwind. Tight leash.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+35bp; ~+132%; target +60bp. The cleanest expression of the disarmed hawk — a bull-steepen as the front rallied and the back held. Trail the stop; hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182 (distant). At ~1.145. THE WRONG FOOT — the soft payroll knocked out the rate-differential engine and DXY broke 101; the thesis reversed. Trim toward flat; own only the Jul 4 tariff tail via MM-038.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold to ~Jul 8. At ~4.14% — GREEN, vindicated; the +57k print dropped Sep-hike odds to ~53%, pricing out the hike this trade fades. Harvest and hold; the curve (MM-009) is the higher-conviction sibling. A hot CPI is the risk.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The jobs number was weak but the Dow hit a record — what's going on?",
         "a": ("The market decided a weak labour market is good news because it kills the rate hike Warsh was defending "
               "&mdash; jobs came in at fifty-seven thousand versus a hundred-and-fifteen expected, and September-hike "
               "odds fell from about sixty-four to fifty-three percent. The catch is that the unemployment rate only "
               "fell because people left the workforce, not because they found jobs. So the melt-up is celebrating the "
               "dovish half of the story and ignoring that a cracking labour market with sticky inflation is a trap for "
               "the Fed, not an all-clear.")},
        {"q": "Why did the unemployment rate drop if only 57,000 jobs were added?",
         "a": ("Because participation collapsed &mdash; the share of people working or looking fell to 61.5%, the lowest "
               "since early 2021. When people give up looking, they leave the unemployment math entirely, so the rate "
               "falls even as the labour market weakens. It's the number below the number: watch participation, not the "
               "headline rate, because the rate is flattering a labour market that's actually emptying out.")},
        {"q": "Our book is 72% dollars — does the weaker dollar hurt us?",
         "a": ("On the margin, yes, and that's the flip side of the last month. The dollar hit a 13-month high on the "
               "promise of higher Fed rates; the soft payroll priced that out and the dollar broke below 101, so the "
               "currency translation on your US assets just turned from a tailwind into a headwind. We'd hedge part of "
               "the dollar sleeve to lock the gain from the strong-dollar period &mdash; a collar or seagull &mdash; "
               "rather than ride the turn.")},
        {"q": "Gold finally moved — should we add?",
         "a": ("Gold ripped toward $4,200 because the soft payroll turned its main driver: lower expected rates and a "
               "weaker dollar are exactly what gold wants, after a month where it did nothing even on the Iran strikes. "
               "Your Xetra-Gold position is the tail hedge finally doing its job, so we'd let it run rather than take "
               "profit. If you want to press it, do it with a defined-risk call spread &mdash; own the continuation "
               "cheaply instead of chasing spot.")},
        {"q": "What's the risk over the July 4 weekend?",
         "a": ("The market is closed Friday and Saturday, but the deadline to lock the EU trade deal is Saturday, and "
               "the digital-tax fight is unresolved with a 100% tariff threat hanging over it. If it escalates, we only "
               "find out at Monday's open &mdash; that's a gap risk the closed tape isn't pricing. We'd own it cheaply "
               "with a defined-risk EUR/USD put spread and a small index put spread; both cost little if nothing "
               "happens.")},
        {"q": "Where's the cleanest new money going?",
         "a": ("Into what the disarmed hike pays and what the record tape ignores. The clearest is the yield-curve "
               "steepener &mdash; a Fed that can't hike into a weak labour market steepens the curve, and that trade is "
               "up sharply. Then the gold continuation on the rate turn, and inside the chip complex that lagged the "
               "record, owning the reasonably-priced leader against the overbought name rather than the whole cohort.")},
    ],

    "ideas_note": (
        "<p>The disarming of the September hike sets the marquee idea, and the stagflation bind under the record tape "
        "sets the rest. <strong>Gold call spread (MM-036)</strong> &mdash; the marquee: the +57k payroll flipped gold "
        "from a real-rates short back to a rate-cut long, and the move has just started; defined-risk upside on the "
        "continuation. <strong>NVDA/AMD dispersion (MM-037)</strong> &mdash; the chip cohort sold as a unit into a Dow "
        "record; own the ~32x leader against the ~175x overbought name, concentration-neutral and doubling as book "
        "housekeeping. <strong>EUR/USD tariff-tail put spread (MM-038)</strong> &mdash; the dollar is topping so an "
        "outright euro short fights the tape, but the July 4 DST/tariff binary over a closed weekend is a dated, "
        "EUR-negative tail worth owning cheaply. <strong>July SPX put spread (MM-039)</strong> &mdash; the index hedge "
        "into the weekend gap and the stagflation-trap tail, with VIX at ~16.6. The rate winners (MM-009/013) are "
        "harvested and trailed; the euro short (MM-012) is trimmed as the dollar tops; gold (MM-005) is held on its "
        "min-hold as it finally pays.</p>"
    ),

    "event_radar_note": (
        "<p>The hawk disarmed: Warsh armed the market for a September hike at Sintra (Jul 1), then June payrolls printed "
        "+57k vs ~115k with −74k of revisions (Jul 2), and the hike odds collapsed to ~53%. The unemployment rate fell "
        "to 4.2% only on a participation drop to 61.5% (lowest since Mar 2021) &mdash; a soft print in a strong-u-rate "
        "costume. The dollar broke below 101, the 2Y fell to 4.137%, gold ripped toward $4,200, and the Dow set a "
        "record (52,900.07) while the Nasdaq fell 0.80% as chips slid. The rate longs won the disarming (steepener "
        "MM-009 ~+132%, short-2Y MM-013 green); the euro short (MM-012) is on the wrong foot as the dollar tops. US "
        "markets are CLOSED today (Jul 3) into a Jul 4 EU-tariff/digital-tax binary; reopen Mon Jul 6; the next CPI is "
        "the decider. Fresh ideas own the regime: a gold call spread, a chip dispersion RV, a tariff-tail EUR/USD put "
        "spread, and an index put spread over the closed weekend.</p>"
    ),

    "burry_tell": (
        "Everyone watched the payroll count; the structural signal is participation. The labour force participation "
        "rate fell to 61.5%, the lowest since March 2021, and that is not a one-month wobble &mdash; it is the "
        "intersection of demographics, a post-pandemic behavioural shift that never fully reversed, and the first faint "
        "read of AI displacement in the professional-and-business-services hiring that has carried the cycle. The thing "
        "nobody is pricing is that a shrinking labour force keeps the unemployment rate looking benign while the real "
        "labour market deteriorates underneath it &mdash; and a Fed anchored to a rate that lies is late by "
        "construction. Over the next two-to-three quarters this resolves one of two ways: participation keeps falling "
        "and the low u-rate masks a contraction, trapping a hawkish Fed; or the displacement thesis is premature and "
        "hiring re-accelerates into sticky core inflation, forcing the hike back on. Both outcomes are stagflationary, "
        "and the equity index &mdash; at a record and concentrated in the AI names that are simultaneously the "
        "productivity promise and the displacement cause &mdash; is the least prepared for either. The way to own it is "
        "the curve steepener (MM-009) and a defined-risk index hedge (MM-039), before the consensus re-labels a falling "
        "participation rate from 'tight labour market' to 'shrinking one.'"
    ),

    "earnings_summary": (
        "No qualifying earnings ideas this refresh. The Finnhub feed (earnings_data.md, generated 2026-07-03 06:00 UTC) "
        "returns 'no qualifying companies' for both the pre-earnings window (Jul 3-8) and the post-earnings window "
        "(Jun 30-Jul 3) within the universe filter (>$10bn, US + Korea, Technology / Financials / Industrials / "
        "Utilities). The holiday-shortened week (US markets closed Jul 3) has no in-universe reporters; the Micron "
        "post-earnings signal from Jun 24 has now rolled outside the 3-session-post window. The earnings section is "
        "omitted rather than padded with out-of-universe or stale names."
    ),
    "earnings_why": (
        "The universe filter is applied before scanning: market cap $10bn+, geographies US (primary) and South Korea "
        "(secondary), sectors Technology / Financials / Industrials / Utilities only. The earnings_data.md feed "
        "(Finnhub, 2026-07-03 06:00 UTC) explicitly reports no qualifying companies in either window &mdash; the "
        "Independence-Day-shortened calendar has no in-universe reporters pre (Jul 3-8) or post (Jun 30-Jul 3). Micron "
        "(Jun 24 AMC), FedEx and the late-June names have all rolled outside the 3-day-post window. With nothing "
        "qualifying and no data to source, no idea is rendered; padding the section with Consumer names or stale "
        "post-prints would violate the filter and the no-fabrication rule."
    ),

    "book_aim": (
        "On the right side of the disarmed hike, and rotating fresh risk into what the record tape is not pricing. The "
        "rate book is the winner: the 2s10s steepener (MM-009) ~+132% and the short-2Y (MM-013) green as the +57k "
        "payroll priced out the September hike Warsh was defending; gold (MM-005), held through a brutal drawdown on its "
        "min-hold, is finally paying as real rates turn. The laggard is the short-10Y (MM-004) on a sticky back end, and "
        "the leg on the wrong foot is short EUR/USD (MM-012) as the 13-month-high dollar tops. For the holiday-shortened "
        "week into a closed Jul 4 weekend: harvest and trail the rate winners (do NOT press &mdash; a hot CPI or a "
        "tariff cost-push re-arms the hawk); trim the euro short toward flat and carry the tariff tail only in "
        "defined-risk options; hold gold as it finally works; and rotate fresh risk into the disarmed-hawk regime "
        "&mdash; the gold call spread (MM-036, the real-rates turn), the NVDA/AMD dispersion (MM-037, the chip cohort "
        "that lagged the record), the EUR/USD tariff-tail put spread (MM-038, the Jul 4 binary), and the July SPX put "
        "spread (MM-039, the weekend gap + stagflation tail). The urgent house-keeping: recognise gold is the hedge "
        "finally firing and let it run; own the tails the goldilocks read is ignoring."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); no option line is open this "
                 "refresh. US cash markets are closed today (Jul 3), so equity-index marks reflect the Jul 2 close.")
    },
    "idea_selection": [
        {"label": "Gold Aug $4,200/$4,500 call spread — own the real-rates turn (MM-036)", "in": True,
         "text": ("The marquee idea. The +57k payroll priced out the September hike, broke the dollar below 101 and "
                  "flipped gold from a real-rates short back to a rate-cut long &mdash; gold ripped toward $4,200 and "
                  "the move has just started. A defined-risk call spread struck at spot owns the continuation and "
                  "presses the book's cash gold long (MM-005) without averaging spot. Max loss capped.")},
        {"label": "Long NVDA / short AMD — the chip dispersion (MM-037)", "in": True,
         "text": ("The chip cohort sold as a unit on Jul 2 even as the Dow set a record. AMD is up ~150% YTD at ~175x "
                  "vs NVDA's ~32x on a far larger revenue base &mdash; the indiscriminate selling is the setup for the "
                  "valuation gap to close. Concentration-neutral to the index, and it doubles as book housekeeping: "
                  "trim the exhausted AMD winner, own the cheaper leader. Stop: ratio -5%.")},
        {"label": "EUR/USD 1-week put spread — own the Jul 4 tariff tail (MM-038)", "in": True,
         "text": ("The dollar is topping so an outright euro short fights the tape &mdash; but the July 4 EU "
                  "digital-tax/tariff deadline is a dated, EUR-negative binary over a closed weekend the tape can only "
                  "price at the Monday open. The soft-payroll bounce to ~1.145 is a better entry for owning that tail "
                  "cheaply. Lets the book trim the spot short (MM-012) while keeping the tariff hedge. Max loss capped.")},
        {"label": "July SPX 7,300/7,050 put spread — hedge the weekend gap (MM-039)", "in": True,
         "text": ("The melt-up read a cracking labour market as goldilocks and set a Dow record, then shut for three "
                  "days over a live tariff binary. With VIX at ~16.6, below-spot convexity is cheap on the "
                  "stagflation-trap tail the record tape is ignoring &mdash; and on an AI concentration that LAGGED the "
                  "record (Nasdaq −0.80%). Defined risk; structured for the discrete weekend gap.")},
        {"label": "Rate winners (MM-009/013) — harvest and trail, don't press", "in": False,
         "text": ("The steepener ~+132% and the short-2Y green; they won the disarming. Held and trailed, not added: a "
                  "hot CPI or a Jul 4 tariff cost-push is the live risk that re-arms the hawk and re-flattens the curve. "
                  "Let the next CPI resolve it; the steepener is the higher-conviction expression than outright duration.")},
        {"label": "Short EUR/USD (MM-012) — trim toward flat, don't defend", "in": False,
         "text": ("The 13-month-high dollar that vindicated the short is topping as the rate-differential engine "
                  "reverses. Still green, stop distant, but the thesis has turned. Trim toward flat; the only short-EUR "
                  "risk worth carrying is the defined-risk Jul 4 tariff tail (MM-038), not the spot.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 15.5},
        {"label": "VIX",   "value": round(_g("vix") or 16.6, 2)},
        {"label": "VIX3M", "value": 18.0},
        {"label": "VIX6M", "value": 19.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.137, 3)},
        {"label": "5Y",  "value": 4.28},
        {"label": "10Y", "value": round(_g("us10y") or 4.485, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 4.90, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-036", "trade": "Buy Aug gold $4,200/$4,500 call spread (own the real-rates turn)",
            "asset_class": "Commodity (options)", "structure": "call spread",
            "entry": "~$4,200 spot", "stop": "—", "target": "~5x at $4,500",
            "conviction": 7,
            "conviction_breakdown": {"gap": 3, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to Aug expiry", "min_hold_days": 0,
            "thesis": ("The marquee idea: the payroll flipped gold's engine and the move has just begun. For a month "
                       "gold traded as a real-rates short &mdash; it fell as the dollar hit a 13-month high and barely "
                       "moved on literal US-Iran strikes. The +57k print reversed that: September-hike odds fell to "
                       "~53%, the dollar broke below 101, and gold ripped toward $4,200. Lower expected policy rates, a "
                       "topping dollar, and a stagflation debasement bid all push the same way. A call spread struck at "
                       "spot owns the continuation with defined risk &mdash; the disciplined way to press the book's "
                       "cash gold long (MM-005) without averaging spot into the bounce."),
        },
        {
            "id": "MM-2026-037", "trade": "Long NVDA vs short AMD (the chip dispersion)",
            "asset_class": "Equity RV", "structure": "cross-name ratio",
            "entry": "spot ratio", "stop": "ratio -5%", "target": "ratio +10%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks-months", "min_hold_days": 0,
            "thesis": ("The chip complex sold as a unit on Jul 2 even as the Dow set a record &mdash; AI-margin worries, "
                       "the rate repricing and mega-IPO rotation chatter punished the cohort indiscriminately. That is "
                       "the setup for the valuation gap to close: AMD is up ~150% YTD at ~175x trailing earnings on a "
                       "fraction of NVDA's revenue base, while NVDA trades ~32x after a ~13% YTD gain on $81.6B of "
                       "quarterly revenue. Own the leader, short the overbought name. Concentration-neutral to the "
                       "index, low-beta to AI direction, high-beta to the dispersion &mdash; and it doubles as book "
                       "housekeeping: trim the exhausted AMD winner, add the laggard NVDA the house still likes."),
        },
        {
            "id": "MM-2026-038", "trade": "Buy 1w EUR/USD 1.135/1.115 put spread (own the Jul 4 tariff tail)",
            "asset_class": "FX (options)", "structure": "put spread",
            "entry": "~1.145 spot", "stop": "—", "target": "~4x at 1.115",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Jul 10", "min_hold_days": 0,
            "thesis": ("The dollar is topping on the disarmed hike, so an outright short EUR/USD fights the tape &mdash; "
                       "but the July 4 deadline is a dated, EUR-negative binary over a three-day weekend the US market "
                       "is closed for. Trump's threat of a 100% tariff that 'supersedes' the 15% EU deal if the "
                       "digital-services-tax fight is unresolved is exactly the kind of holiday-weekend escalation the "
                       "tape gaps on at the Monday reopen. The soft-payroll bounce to ~1.145 is a better entry for "
                       "owning that tail cheaply. A defined-risk put spread owns the specific catalyst without betting "
                       "against the topping dollar, and lets the book trim the spot short (MM-012) while keeping the "
                       "tariff hedge on."),
        },
        {
            "id": "MM-2026-039", "trade": "Buy July SPX 7,300/7,050 put spread (hedge the weekend gap)",
            "asset_class": "Equity (options)", "structure": "put spread",
            "entry": "~0.5% premium", "stop": "—", "target": "~5x at 7,050",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 0, "stop_quality": 1},
            "horizon": "to late Jul", "min_hold_days": 0,
            "thesis": ("The melt-up read the soft payroll as goldilocks and set a Dow record, then shut for a three-day "
                       "weekend with a live Jul 4 tariff binary and a labour market softening under a "
                       "participation-flattered 4.2% u-rate. That is the stagflation-trap tail the record tape is "
                       "ignoring: the Fed can't hike into a cracking labour market and can't cut into sticky core PCE, "
                       "and a tariff cost-push lands on top. VIX at ~16.6 makes below-spot convexity cheap. A July "
                       "7,300/7,050 put spread re-establishes the index hedge on an AI-heavy concentration that LAGGED "
                       "the record (Nasdaq −0.80% on Jul 2) &mdash; structured for the discrete weekend-gap risk, not a "
                       "chase of at-the-money premium."),
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
