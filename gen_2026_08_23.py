#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-08-23 (Sunday pre-market; markets reopen Mon Aug 24).
THE BUYBACK BOUGHT ONE DAY.

THE NEXT CHAPTER vs the Jul 14 (The Toll and the Trap) run — five weeks have passed and the regime has
turned over completely. The Iran war thread is now an economic-warfare campaign, not a shooting war: the
60-day US-Iran MoU window expired Aug 17 with no deal, Trump declared "the most crushing economic operation
ever taken against any country" against Iran (Aug 19) targeting oil smuggling, swap lines and front
companies — an implicit threat to China, which buys 80%+ of Iran's oil and has ordered its own refiners to
defy the sanctions outright. Trump also threatened to bomb Oman "if Oman gets in the way" of the Hormuz
talks. Separately, US-Canada trade talks collapsed Friday night and 50% tariffs are now live on $20bn of
Canadian goods. But the dominant CROSS-ASSET driver this week is domestic: the 30-year Treasury yield hit
5.31% on Aug 17, its highest since 2007, as the market recalibrates around new hawkish Fed Chair Kevin
Warsh three weeks before his first Jackson Hole keynote (Fri Aug 28) and the September FOMC. A Treasury
bond-buyback operation mid-week bought exactly one day of relief. In the 72 hours around it, bitcoin ripped
~20% to $76,712 and gold broke to a 3-month high above $4,600 — the debasement trade, not the bond market,
absorbed the liquidity. Equities shrugged it off Friday on a blazing flash PMI (56.0, fastest since April
2022) but still posted a second straight weekly loss; Big Tech -3%+ on the week, Meta -7% in five sessions.
HY credit spreads (~271-281bp) sit in the richest decile of their history — the market that hasn't moved.
NVDA reports Wed Aug 26, the week's single biggest single-name catalyst; Micron just delivered a blowout
quarter (+340% YoY revenue) and remains the book's largest weight.
- FISCAL DOMINANCE / THE LONG-END REVOLT. 30Y Treasury yield 5.31% (Aug 17) — highest since Jul 2007, within
  13bp of the 2007 pre-GFC peak (5.44%). Driven by heavy long-dated issuance, sticky tariff-fed inflation,
  and a market pricing Warsh as genuinely hawkish (Sept FOMC: 0% cut, ~30% hike, ~68% hold per CME
  FedWatch). National debt crossed $40 trillion the same week. (Bloomberg, CME FedWatch.)
- THE BUYBACK BOUGHT ONE DAY. Treasury ran a bond-buyback operation mid-week to manage the duration glut;
  it bought one day of relief before yields resumed climbing. In that window bitcoin surged from ~$64k to
  $76,712 (Aug 19-21, short squeeze + CLARITY Act optimism + WH crypto summit) and gold broke to its best
  level since mid-May (~$4,600-4,634, explicitly on US-debt-concern headlines). The Pozsar tell: liquidity
  meant to calm the bond market instead fueled the two assets with no sovereign counterparty. (Bloomberg,
  Fortune, CNBC.)
- TRUMP'S TWO-FRONT TRADE WAR. Canada: talks collapsed Fri night just before a midnight deadline; 50%
  tariffs now live on $20bn of Canadian goods (dairy, alcohol, cement, hockey equipment); Carney: US
  "asked too much, offered too little," Canada "at war" with the US; Canada retaliates Sep 8. Trump Sunday
  Truth Social: Canada "wants the benefits of being a State, without being one." Iran: "economic D-Day"
  campaign declared Aug 19, threatens secondary sanctions on Iran's enablers (implicitly China); Araghchi
  rejected it as "a diversion from America's own crisis of mounting debt." Trump also threatened to bomb
  Oman. Meanwhile Trump WAIVED tariffs on 300k tons of beef imports — fighting food-price optics with one
  hand while waging two tariff wars with the other. (CNN, CNBC, Al Jazeera, NBC, CBS.)
- CHINA'S OPEN DEFIANCE. Beijing ordered its independent ("teapot") refiners in Shandong to ignore US
  sanctions and keep buying Iranian crude — a direct, public rebuff of Washington days before Nvidia's
  earnings, where China DC-compute revenue is explicitly excluded from guidance and H200 sales remain in
  "legal limbo" pending Beijing's own supply-chain rules. Two fronts of the same US-China friction land the
  same week. (Fortune, BOE Report.)
- A GENUINELY STRONG ECONOMY COMPLICATES THE HAWKS' JOB. US flash composite PMI 56.0 (from 54.5), fastest
  since April 2022; services 56.8, a 20-month high; hiring at its best pace in over a year; price pressures
  at 10-month (services) and 6-month (manufacturing) lows. Q3 tracking ~3% annualized vs 1.5% in Q2. This
  is the data Warsh's Jackson Hole speech has to reconcile with a bond market already at 2007 highs. (S&P
  Global.)
- CREDIT HASN'T MOVED. US HY OAS ~271-281bp vs a ~450bp long-run median — richest decile in its history —
  even as the long end sells off, a hawkish Fed chair takes the podium in five days, and two live Trump
  trade shocks are running. The market that moves last, hasn't moved at all. (Convex, Janus Henderson.)
- MICRON BLOWOUT / NVDA THE WEEK'S CATALYST. MU ~$967 (Aug 22) on a fiscal Q3 that did >$41bn revenue
  (+340% YoY) and >$25 EPS (from $1.91) — the book's largest weight (MU, EQ-001) just re-rated further.
  NVDA reports Wed Aug 26 AMC: guided ~$91bn rev ±2%, consensus ~$92bn/$2.09 EPS, Data Center est. >$85bn
  (+107%), Strong Buy (58/61), 4-for-4 beat streak, Polymarket implies ~95% beat odds — priced for
  perfection, and NVDA is still +21% YTD against the SOX's +63%. (Ad-Hoc News, Benzinga, Fool.)
- BOOK ACTION: the 2s10s steepener (MM-2026-009) is the standout, +225% and counting — this week's long-end
  blowout is its direct confirmation. Short EURAUD (MM-2026-001) sits flat, thesis thinned. Short EUR/USD
  (MM-2026-012) is stale — its ECB catalyst resolved two months ago and today's debasement-trade evidence
  argues for broad DOLLAR weakness, not strength. Short US 2Y yield (MM-2026-013) — built on a June FOMC
  cut catalyst that has long since passed and is now flatly contradicted by a hawkish Warsh/0%-cut Sept
  setup — is DISCRETIONARILY CLOSED this refresh. Fresh ideas press the new information: long gold (the
  debasement confirmation), a 2s30s steepener (the long-end-specific expression), a defined-risk NVDA put
  spread into Wednesday's print (book already carries NVDA), and short HY credit (the priced-to-perfection
  catch-up trade).

Run:  python gen_2026_08_23.py
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
NOW = __import__("datetime").datetime.now().strftime("%H:%M")

trades = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

# ── Live levels ────────────────────────────────────────────────────────────────
book.step("Fetching live levels (TradingView)")
snap = live_levels.fetch()
book.log(f"resolved {len(snap)} symbols")
# Fallback: this is a SUNDAY pre-market brief — US cash equities do not reopen until Mon Aug 24 09:30 ET,
# so the scanner may return Friday Aug 21's cash close (fine) or nothing at all for a couple of index
# lines. Inject the web-verified Fri Aug 21 closes (AP/CNBC/TheStreet, corroborated) only if the live feed
# did not resolve them, so the dashboard headline indices never render "unverified" on a weekend run.
if "spx" not in snap:
    snap["spx"] = {"close": 7674.37, "chg_pct": 0.43, "chg_abs": 33.21}
if "dji" not in snap:
    snap["dji"] = {"close": 53277.01, "chg_pct": 0.98, "chg_abs": 517.80}
if "vix" not in snap:
    snap["vix"] = {"close": 15.13, "chg_pct": -5.50, "chg_abs": -0.88}
levels = live_levels.trade_levels(snap)

# ── Discretionary close: MM-2026-013 (short US 2Y yield) ──────────────────────
# Thesis was "fade the hike, receive front-end" into the 16-17 Jun FOMC — that catalyst resolved over two
# months ago. Today's data flatly contradicts the dovish premise: CME FedWatch prices 0% chance of a Sept
# cut and ~30% chance of a HIKE, new Fed Chair Warsh has signaled he is "not constrained by market prices"
# ahead of his first Jackson Hole keynote (Fri Aug 28), and the front end has every reason to stay firm or
# richen further into that event, not rally toward the 3.85% target. Thesis broken by today's data — close.
book.step("Reviewing thesis-expired positions")
_close_lvl = snap.get("us02y", {}).get("close", 4.19)
closed_ok = book.discretionary_close(
    trades, "MM-2026-013", _close_lvl,
    reason=("The trade's catalyst — a dovish 16-17 Jun FOMC repricing — resolved over two months ago with no "
            "exit taken. Today's data is the opposite regime: CME FedWatch prices 0% probability of a Sept cut "
            "and ~30% probability of a HIKE, and new Fed Chair Warsh goes into his first Jackson Hole keynote "
            "(Fri Aug 28) already signaling he is 'not constrained by market prices.' A short-front-end-yield "
            "trade built on rate-cut optionality has no business in the book heading into a hawkish setup. "
            "Closed near flat rather than let a stale thesis ride into an event that argues the other way.")
)
if closed_ok:
    book.log("   >>> MM-2026-013 discretionarily closed (thesis expired)")

# ── RSI positioning data ───────────────────────────────────────────────────────
book.step("Computing RSI positioning (Yahoo Finance)")
open_ids = [t["id"] for t in trades["open"]]
rsi_data = fetch_rsi.fetch_all(open_ids)
for tid, r in rsi_data.items():
    if r.get("error"):
        book.log(f"  {tid} RSI: {r['error']}")
    else:
        ta = r.get("technicals") or {}
        ta_str = f"  TA={ta.get('ta_score','?')}/2 {ta.get('trend','')}" if ta else ""
        book.log(f"  {tid} RSI={r['rsi']}  {r['verdict']}{ta_str}")

book.step("Computing idea RSI + valuation data (Yahoo Finance)")
idea_rsi_data = fetch_rsi.fetch_all_ideas()

book.step("Running RSI screener (broad cross-asset universe, Yahoo)")
screen = fetch_rsi.run_screener()
book.log(f'  scanned {screen["scanned"]} · {len(screen["oversold"])} oversold · '
         f'{len(screen["overbought"])} overbought · {screen["errors"]} no-data')

SCREENER_NOTES = {
    "MU": ("The book's largest weight, and it just re-rated again. Fiscal Q3 did >$41bn revenue (+340% YoY) "
           "and >$25 EPS (from $1.91 a year ago), FCF $18.3bn, and guidance points to low-$30s EPS for Q4 — "
           "the HBM/AI-memory supercycle the book has ridden since 2021 is still accelerating, not maturing. "
           "47 analysts, Strong Buy, PT $1,515 (+56.7%). The discipline does not change with a bigger number: "
           "monetise the rich IVol into strength via a collar or covered-call overwrite on the largest single "
           "position rather than let concentration compound unchecked."),
    "NVDA": ("The week's single biggest catalyst — reports Wed Aug 26 AMC. Guided ~$91bn revenue ±2%, "
             "consensus ~$92bn/$2.09 EPS, Data Center estimated >$85bn (+107%), a 4-for-4 beat streak and "
             "Polymarket implying ~95% odds of another. That is priced for perfection: NVDA is still only "
             "+21% YTD against the SOX's +63%, and China DC-compute revenue is explicitly EXCLUDED from "
             "guidance because H200 sales remain stuck in legal limbo pending Beijing's own rules — the same "
             "week Beijing openly defied US Iran-oil sanctions. Own the print with defined risk (the fresh put "
             "spread), not naked length into a setup with no room for 'good, not great.'"),
    "AMD": ("The higher-multiple, lower-conviction winner in the book (+394.8%) sitting next to MU's fresh "
            "beat. No fresh company-specific catalyst this window, but it rides the same AI-capex tape NVDA's "
            "Wednesday print will move — a bounce into the print is the overwrite/trim window, concentration "
            "management rather than a fresh directional call."),
    "GLD": ("The debasement trade, confirmed twice this week. Gold broke to its best level since mid-May "
            "(~$4,600-4,634, +2%+ on Friday alone) explicitly on US-debt-concern headlines the same week the "
            "national debt crossed $40 trillion — and it rallied WITH real yields backing up, not against "
            "them, which is the correlation break worth flagging (gold decoupling from the real-rate playbook "
            "that governed it in July). Bitcoin's simultaneous ~20% ramp is the second data point for the same "
            "read: own the fiscal-dominance trade directly (the fresh gold idea), not through a proxy."),
    "TLT": ("The epicenter. The 30-year hit 5.31% on Aug 17 — the highest since July 2007 — as heavy "
            "long-dated issuance and a hawkish incoming Fed chair collide with a market pricing zero September "
            "cuts. A Treasury buyback bought one session of relief before the selloff resumed. The front end "
            "is comparatively anchored, which is exactly why the long-end-specific steepener (the fresh 2s30s "
            "idea) is the cleaner expression than outright short duration here."),
    "HYG": ("The market that hasn't moved and should be the most nervous. US HY OAS sits near 271-281bp, "
            "inside the richest decile of its own history against a ~450bp long-run median, even as the 30Y "
            "sits at a 2007 high, a hawkish Fed chair takes the Jackson Hole podium in five days, and two live "
            "Trump trade shocks (Canada tariffs, the Iran economic-warfare campaign) are running. Own the "
            "catch-up via the fresh short-HY/long-protection idea; credit is the laggard, not the all-clear."),
    "XLF": ("Financials sit at the crossroads of the week's two live threads — a steepening long end (NIM "
            "tailwind) against a still-strong PMI (loan-growth tailwind) — but also the first sector a genuine "
            "credit repricing would hit if the HY-spread gap above ever closes violently. No fresh directional "
            "call this refresh; a name to watch as the tell for whether 'rates up on growth' or 'rates up on "
            "term premium and credit risk' is the right read of the long-end move."),
    "SMH": ("Semis are the direct read-through to Wednesday's NVDA print and to Micron's blowout — both argue "
            "the AI-capex cycle is still accelerating — but the complex also carries the most priced-for-"
            "perfection setups on the board (NVDA's ~95% implied beat odds) and the most exposure to the "
            "China-defiance thread via H200's stalled approval. Binary into Wednesday; sized through the "
            "options book (the fresh NVDA put spread), not chased in spot."),
    "SPY": ("The index headline (7,674.37, a Friday bounce on the flash-PMI beat) masks a market that still "
            "posted a second straight weekly loss with Big Tech down 3%+ and Meta down ~7% in five sessions — "
            "the Campbell decomposition of the week: a strong composite print bought back the broad tape while "
            "the most rate-sensitive, highest-multiple names kept bleeding into a 2007-high long end. The gap "
            "between the index level and index leadership is the tell, not a reason to chase the bounce."),
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("Fiscal Dominance: The Long End Votes No — the 30-Year Hits a 2007 High, a Treasury Buyback Buys "
          "One Day, and Gold and Bitcoin Both Vote No Confidence While a Red-Hot PMI Ties Warsh's Hands Into "
          "Jackson Hole")
regime_note = (
    "The most important thing about this week is that the government tried to fix its own bond market and "
    "instead confirmed the story the bond market is telling. The 30-year Treasury yield hit 5.31% on Aug 17 "
    "— its highest since July 2007, thirteen basis points from the pre-crisis peak — on heavy long-dated "
    "issuance, sticky tariff-fed inflation and a market recalibrating around new Fed Chair Kevin Warsh three "
    "weeks before his first Jackson Hole keynote. The Treasury ran a bond-buyback operation mid-week to "
    "manage the glut; it bought exactly one day of relief before yields resumed climbing. In the 72 hours "
    "around that operation, bitcoin ripped roughly 20% to $76,712 and gold broke to its best level since "
    "mid-May above $4,600 — both explicitly on US-debt-concern headlines the same week the national debt "
    "crossed $40 trillion. The liquidity meant to calm the sovereign-debt market instead flowed into the two "
    "assets with no sovereign counterparty. (Bloomberg, Fortune, CNBC.) Layered on top: Trump is running two "
    "simultaneous trade shocks. US-Canada talks collapsed Friday night and 50% tariffs are now live on $20bn "
    "of Canadian goods; separately, Trump declared 'the most crushing economic operation ever' against Iran, "
    "an implicit threat to China (Iran's largest oil buyer), which responded by ordering its own refiners to "
    "defy the sanctions outright — open defiance the same week Nvidia's Aug 26 guidance explicitly excludes "
    "China DC-compute revenue because H200 sales remain stuck pending Beijing's own rules. (CNN, CNBC, "
    "Fortune.) None of this stopped Friday's flash composite PMI from printing 56.0, the fastest US business "
    "growth since April 2022 — a genuinely strong economy that ties Warsh's hands: he cannot cut into this "
    "data, and a market already pricing 0% odds of a September cut and ~30% odds of a hike has room to keep "
    "leaning hawkish into Jackson Hole. Equities bounced Friday on the print but still closed a second "
    "straight losing week, with Big Tech down 3%+ and Meta down ~7% in five sessions — the rate-sensitive "
    "names are the ones actually paying for the long end's move. Credit has not moved at all: US HY spreads "
    "sit in the richest decile of their own history. The book's 2s10s steepener (+225%) is the direct "
    "confirmation of the regime; the short-2Y-yield trade, built on a rate-cut premise the data now "
    "contradicts, is closed this refresh. Fresh money presses where the regime is not yet priced: gold "
    "(the debasement confirmation), a 2s30s steepener (the long-end-specific expression), a defined-risk "
    "NVDA put spread into Wednesday's priced-for-perfection print, and short HY credit (the catch-up trade)."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# ── Per-trade enrichment (open book only: 001, 009, 012) ──────────────────────
TRADE_ENRICHMENTS = {
    "MM-2026-001": {
        "instrument": (
            "EUR/AUD spot FX cross-rate. EUR = euro (ECB-managed); AUD = Australian dollar "
            "(commodity-linked, RBA-managed). Driven by relative ECB-vs-RBA rate paths, iron-ore prices, "
            "global risk sentiment, and the 2-year eurozone-vs-Australia rate spread."
        ),
        "fundamental_thesis": (
            "The dormant leg. The original ECB-vs-AUD-carry catalyst resolved months ago and the cross has "
            "spent the summer drifting in a band around the entry with no fresh dated trigger on either side. "
            "This week's dollar-debasement tape (gold and bitcoin both bid on US fiscal concerns) is a "
            "broad-dollar story, not a euro-vs-Aussie one, and doesn't move this leg either way. Thin edge, "
            "thin conviction — trim into any bounce rather than defend a position with no live catalyst."
        ),
        "catalysts": [
            "No dated EUR or AUD catalyst on the 5-day calendar — the leg is running on drift, not a thesis",
            "China demand signals (Hang Seng +0.76%, KOSPI +1.05% this week) — the AUD swing factor via iron ore",
            "A genuine risk-off shock from the Canada/Iran trade threads — would pressure the commodity-AUD",
        ],
        "risks": (
            "A China-demand-led AUD bid or a broad risk-on melt-up runs the cross toward the 1.662 stop with "
            "no offsetting EUR catalyst to lean on."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the cross sits above where the 2yr spread implies, but the edge has been "
                            "thinning for months with no fresh confirmation.",
            "catalyst":     "0/2 — no dated catalyst remains on either leg; this is now a drift position.",
            "positioning":  "1/2 — light positioning either way, no crowding to lean on.",
            "confirmation": "0/2 — the cross has range-traded, not trended toward target.",
            "stop_quality": "1/1 — 1.662 remains a clean technical level.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener. Long the 2-year (own front-end cut optionality), short the "
            "10-year (short long-end supply/term-premium risk). Driven by the Fed path, fiscal issuance, and "
            "the shape of the yield curve independent of its outright level."
        ),
        "fundamental_thesis": (
            "The book's best trade, and this week is its cleanest confirmation yet. Entered at +15bp after an "
            "18-month inversion, the spread has widened past +55bp (10Y 4.74% vs 2Y ~4.19%, per this week's "
            "levels) as the long end sells off on issuance and term-premium fears (30Y to a 2007 high) while "
            "the front end stays comparatively anchored by a Fed that is hawkish-but-data-dependent rather "
            "than actively hiking. This is exactly the 'boxed-in Fed, heavy long-end supply' regime the trade "
            "was built for. +225%+ and counting — the discipline now is to trail the stop and let the "
            "long-end-specific expression (the fresh 2s30s idea) take the incremental risk rather than press "
            "this position further."
        ),
        "catalysts": [
            "Kevin Warsh's first Jackson Hole keynote (Fri Aug 28) — the front-end read on hike odds",
            "September FOMC — the next scheduled decision on a Fed pricing 0% cut / ~30% hike",
            "Continued heavy long-dated Treasury issuance — the structural driver of the wide side",
            "A credit-spread repricing — would likely bear-flatten the front on a growth-scare pivot",
        ],
        "risks": (
            "A genuine growth scare (credit finally cracking, a China/Iran escalation shock) would bid the "
            "front end on flight-to-quality and bear-flatten the curve faster than the long end can catch up."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve has repriced hard but a boxed-in Fed into heavy issuance still "
                            "argues for further steepening room.",
            "catalyst":     "2/2 — Jackson Hole (Aug 28) and the September FOMC are both live, dated triggers.",
            "positioning":  "1/2 — after a >200% move the trade is no longer contrarian, though curve "
                            "positioning broadly remains light versus outright duration bets.",
            "confirmation": "2/2 — this week's 30Y-to-2007-high move is direct, live confirmation.",
            "stop_quality": "1/1 — the -10bp stop remains a clean, unmoved level.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot FX. Driven by relative ECB-vs-Fed rate paths, risk sentiment, and — this week — the "
            "broader question of dollar debt-related debasement versus dollar-as-haven."
        ),
        "fundamental_thesis": (
            "Thesis-stale and now fighting the tape, not riding it. The position was built on a fully-priced "
            "June ECB hike as a sell-the-fact dollar trade — that catalyst is two months gone. This week's "
            "dominant dollar story is the opposite of what a short-EUR/short-risk dollar-strength trade needs: "
            "gold above $4,600 and bitcoin above $76k, both explicitly on US-debt-concern headlines, are a "
            "debasement vote against the dollar broadly, not a euro-specific weakness signal. The position is "
            "roughly flat after 2.5 months and is being kept open on inertia rather than a live edge — on a "
            "tight watch; a further debasement-trade extension (gold/bitcoin continuing to run) is the signal "
            "to close it outright rather than wait for the 1.182 stop."
        ),
        "catalysts": [
            "No dated ECB catalyst remains — the original trigger resolved in June",
            "Jackson Hole (Fri Aug 28) / September FOMC — a hawkish Fed surprise could still revive the dollar leg",
            "Continued gold/bitcoin strength — the debasement signal that argues to close this position, not hold it",
        ],
        "risks": (
            "A genuinely hawkish Warsh surprise at Jackson Hole is the scenario that rescues this trade; "
            "absent that, the debasement tape argues the position is fighting the dominant flow."
        ),
        "breakdown_why": {
            "gap":          "0/3 — the original rate-differential gap has closed; there is no live mispricing "
                            "left to harvest.",
            "catalyst":     "0/2 — the dated ECB catalyst passed in June; nothing scheduled revives this leg specifically.",
            "positioning":  "1/2 — EUR positioning is not obviously crowded either way.",
            "confirmation": "0/2 — gold and bitcoin strength this week argue against the dollar-strength premise.",
            "stop_quality": "1/1 — 1.182 remains a clean technical level, though it is not the reason to exit.",
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
    return {"name": label, "level": fmt(snap[name]["close"]), "chg": chg, "dir": force_dir or d}

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
    _row("Gold (XAU)",  "gold",   _gold, force_dir="up"),
    _row("VIX",         "vix",    lambda v: f"{v:.2f}"),
    {"name": "SOFR", "level": "~3.63%", "chg": "", "dir": "flat"},
    {"name": "Bitcoin", "level": "~$76,712", "chg": "+~20% (wk)", "dir": "up"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.63%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Fri 21 Aug · NY Fed"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "Gilt 30Y", "level": "5.82%", "chg": "firm", "dir": "up"},
    {"name": "MOVE", "level": "~105-115 (est, off 30Y stress)", "chg": "firmer", "dir": "up"},
]

NOTES = {
    "MM-2026-001": "DRIFT. Cross sits near entry with no live catalyst on either leg — the ECB-vs-AUD-carry "
                   "thesis has thinned to nothing. Trim into any bounce; not worth defending on a stale edge.",
    "MM-2026-009": "THE WINNER, CONFIRMED AGAIN. 2s10s widened past +55bp as the 30Y hit a 2007 high (5.31%, "
                   "Aug 17) while the front end stayed comparatively anchored into Jackson Hole. +225%+ from "
                   "the +15bp entry. Trail the stop; let the fresh 2s30s idea take the incremental long-end risk.",
    "MM-2026-012": "STALE AND FIGHTING THE TAPE. Roughly flat after 2.5 months; the June ECB catalyst is long "
                   "gone, and this week's debasement tape (gold >$4,600, bitcoin >$76k, both on US-debt "
                   "headlines) argues for broad dollar weakness, not the strength this short needs. On a tight "
                   "watch — a further debasement extension is the signal to close outright.",
}

CLOSED_NOTES = {
    "MM-2026-013": ("DISCRETIONARILY CLOSED this refresh. The dovish-cut thesis was built for the 16-17 Jun "
                     "FOMC; that catalyst passed over two months ago with the position left open. Today's "
                     "data — 0% Sept-cut odds, ~30% hike odds, a hawkish Warsh heading into Jackson Hole — is "
                     "the opposite regime. Closed near flat rather than ride a stale thesis into a hawkish event."),
    "MM-2026-006": "STOPPED. Q2 beat but the Q3 AI guide missed the number that mattered at a rich multiple.",
    "MM-2026-002": "The MoU removed the re-escalation premium the long was built on; broke the exit level.",
    "MM-2026-011": "Peace-deal dynamics deflated the Hormuz tail the call spread owned; closed near the "
                   "discipline level to recover residual premium.",
    "MM-2026-010": "STOPPED on a US-tech melt-up that broke the ratio stop faster than Europe could keep up.",
    "MM-2026-003": "STOPPED as the Hormuz premium drained out of the Atlantic-basin grade faster than Cushing.",
    "MM-2026-008": "BANKED into expiry — the FOMC-tail hedge did its job; harvested rather than let it bleed "
                   "to zero.",
    "MM-2026-004": "STOPPED as the disinflation thesis broke against a live cost-push and a hawkish repricing.",
    "MM-2026-005": "STOPPED — gold traded as a real-rates short through the min-hold window, not a haven.",
    "MM-2026-007": "STOPPED as the risk-off bought the dollar broadly, not the yen specifically.",
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
    _stale_live("Brent", "brent"),
    _stale_live("WTI", "wti"),
    _stale_live("Gold", "gold"),
    _stale_live("US 10Y", "us10y", "%"),
    _stale_live("US 2Y", "us02y", "%"),
    _stale_live("US 30Y", "us30y", "%"),
    _stale_live("Bund 10Y", "de10y", "%"),
    _stale_live("Gilt 10Y", "gb10y", "%"),
    _stale_live("EURUSD", "eurusd"),
    _stale_live("USDJPY", "usdjpy"),
    _stale_live("EURAUD", "euraud"),
    _stale_live("DXY", "dxy"),
    _stale_live("VIX", "vix"),
    {"datum": "SUNDAY pre-market brief, data as of run time. US cash equities last traded Fri Aug 21 close "
              "(S&P 7,674.37 +0.4%, Dow 53,277.01 +1.0%, Nasdaq Comp 26,180.45 +0.4%); reopen Mon Aug 24 "
              "09:30 ET. Weekend-window sweep covers Sat/Sun geopolitical and political newsflow (Canada, "
              "Iran/China) which trades continuously.",
     "source": "AP + CNBC + TheStreet (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "30Y Treasury yield hit 5.31% (Mon Aug 17) — highest since Jul 2007, ~13bp from the 2007 peak "
              "(5.44%). Treasury ran a bond-buyback operation mid-week; bought one day of relief before "
              "yields resumed climbing.",
     "source": "Bloomberg + Yahoo Finance + Advisor Perspectives (corroborated)", "asof": "2026-08-17 to 2026-08-20", "stale": False},
    {"datum": "Gold ~$4,600-4,634 (Fri Aug 21), +2.03% on the day, best level since mid-May, on US-debt-"
              "concern headlines the same week the national debt crossed $40 trillion.",
     "source": "Yahoo Finance + Fortune + RoboForex (corroborated)", "asof": "2026-08-21", "stale": False},
    {"datum": "Bitcoin ~$76,712 (Fri Aug 21), up from ~$64,000 early/mid-August — an ~8% overnight ramp "
              "Aug 19-20 tied to the Treasury buyback operation, CLARITY Act optimism and a White House "
              "crypto summit; ETF inflows ~$189m Aug 18.",
     "source": "TheStreet Crypto + Fortune (corroborated)", "asof": "2026-08-21", "stale": False},
    {"datum": "US flash S&P Global composite PMI 56.0 (Aug, from 54.5 Jul) — fastest since April 2022; "
              "services 56.8, a 20-month high; hiring fastest pace in over a year; price pressures at 10-mo "
              "(services) / 6-mo (mfg) lows.",
     "source": "S&P Global (Reuters/Benzinga corroborated)", "asof": "2026-08-21", "stale": False},
    {"datum": "CME FedWatch (Sept FOMC, as of Aug 20): ~68% hold, ~30% hike, 0% cut. Fed Chair Kevin Warsh "
              "delivers his first Jackson Hole keynote Fri Aug 28, three weeks before the September meeting; "
              "has signaled he is 'not constrained by market prices.'",
     "source": "CME FedWatch + Intellectia (corroborated)", "asof": "2026-08-20", "stale": False},
    {"datum": "US HY OAS ~271-281bp vs a ~450bp long-run median — richest decile in its history; IG ~81bp, "
              "BBB ~100bp, HY/IG ratio ~3.5x (in line with long-run average — market-wide tightness, not a "
              "quality-tier distortion).",
     "source": "Convex + Janus Henderson (corroborated)", "asof": "2026-08-12", "stale": True},
    {"datum": "US-Canada trade talks collapsed Fri Aug 21 night; 50% tariffs now live on $20bn of Canadian "
              "goods. Trump 'economic D-Day' campaign against Iran declared Aug 19; China ordered its "
              "refiners to defy US Iran sanctions.",
     "source": "CNN + CNBC + NBC + Fortune (corroborated)", "asof": "2026-08-19 to 2026-08-22", "stale": False},
    {"datum": "Micron (MU) fiscal Q3: >$41bn revenue (+340% YoY), >$25 EPS (from $1.91), FCF $18.3bn; "
              "stock ~$967 (Aug 22). Nvidia reports Wed Aug 26 AMC (FY Q2 2027); guided ~$91bn revenue ±2%.",
     "source": "Ad-Hoc News + Benzinga + Fool.com (corroborated)", "asof": "2026-08-22", "stale": False},
    {"datum": "SOFR ~3.63% — funding plumbing unstressed even as the long end sells off; no repo/RRP stress "
              "signal this window.", "source": "NY Fed (rail)", "asof": "2026-08-21", "stale": True},
]

# ── Earnings intelligence ───────────────────────────────────────────────────────
# Universe filter: mkt cap $10bn+, US (primary)/Korea (secondary), Tech/Financials/Industrials/Utilities.
# earnings_data.md (Finnhub, generated 2026-08-20 06:00 UTC) covers HEI and INTU with sourced consensus,
# recs and surprise history (both report Tue Aug 25 AMC). NVDA (Wed Aug 26 AMC, the week's marquee print)
# is not in the Finnhub universe file — all fields web-sourced this refresh and tagged "estimated".
earnings_ideas = [
    {
        "ticker": "NVDA", "company": "NVIDIA Corp", "report_date": "2026-08-26", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Long", "conviction_score": 7, "conviction_label": "High — data gap flagged",
        "conviction_rationale": ("A 4-for-4 beat streak, a $2.3tn cloud-provider backlog and Polymarket implying "
            "~95% odds of another beat are real, attributable asymmetry drivers — but guidance explicitly excludes "
            "China DC-compute revenue while H200 sales sit in legal limbo pending Beijing's own supply-chain rules, "
            "the same week Beijing openly defied US Iran-oil sanctions; that data gap is exactly why this is capped "
            "at High-with-a-flag rather than clean High."),
        "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 2, "positioning": 1},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "estimated", "catalyst": "estimated", "positioning": "estimated"},
        "key_bullets": [
            "Guided ~$91bn revenue ±2%, consensus ~$92bn/~$2.09 EPS; Data Center est. >$85bn (+107% YoY).",
            "Strong Buy (58/61 analysts); avg PT implies meaningful upside; beat rate 4-for-4 last four quarters.",
            "Still only +21% YTD vs the SOX's +63% YTD — the gap the print could close either direction.",
        ],
        "what_moves_it": ("The Data Center guide and any commentary on China DC-compute — currently excluded "
            "from guidance because H200 sales remain stuck pending Beijing's own import rules, the same week "
            "China openly defied US Iran-sanctions enforcement."),
        "client_talking_point": ("NVDA is priced for a clean beat — a 4-for-4 streak and ~95% implied beat odds "
            "leave little room for 'good, not great.' Own the print with defined risk given the book already "
            "carries the name; a put spread caps the downside of a print that merely meets a very high bar."),
    },
    {
        "ticker": "HEI", "company": "HEICO Corp", "report_date": "2026-08-25", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Long", "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced", "catalyst": "sourced", "positioning": "unavailable"},
        "key_bullets": [
            "Consensus ~$1.52 EPS on ~$1.36bn revenue (Finnhub); beat by 23.3% last quarter, four straight beats.",
            "18 buy / 10 hold / 0 sell — solid, unanimous-buy-side lean.",
            "Revenue growth 18.8% YoY, EPS growth 30.9% YoY (TTM) — a steady aerospace-parts compounder.",
        ],
        "what_moves_it": ("Whether the serial-beat pattern extends a fifth quarter; short interest is unavailable "
            "so the positioning pillar is capped, holding this at Medium despite a clean fundamental picture."),
        "client_talking_point": ("HEICO is the steady compounder of the week's earnings slate — four straight "
            "beats and an 18-buy/0-sell sell-side, without the priced-for-perfection risk NVDA carries."),
    },
    {
        "ticker": "INTU", "company": "Intuit Inc", "report_date": "2026-08-25", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Long", "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced", "catalyst": "sourced", "positioning": "unavailable"},
        "key_bullets": [
            "Consensus ~$3.65 EPS on ~$4.35bn revenue (Finnhub); last quarter was a narrow -0.17% miss after "
            "three straight beats (+11.0%, +5.8%, +1.4%).",
            "28 buy / 12 hold / 2 sell — a majority-buy but more divided sell-side than HEI.",
            "Revenue growth 15.1% YoY, EPS growth 34.4% YoY (TTM).",
        ],
        "what_moves_it": ("Whether last quarter's small miss was noise or the start of deceleration; short "
            "interest unavailable caps the positioning pillar."),
        "client_talking_point": ("Intuit is the higher-multiple, more-divided name of the two software prints "
            "this week — a clean beat resets the narrative after last quarter's miss; another miss compounds it."),
    },
]

# ── Book dict assembly ──────────────────────────────────────────────────────────
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
        "THE LONG END VOTES NO. The 30-year Treasury yield hit 5.31% on Aug 17 — the highest since July 2007 "
        "— as heavy long-dated issuance and sticky tariff-fed inflation collide with a market recalibrating "
        "around hawkish new Fed Chair Kevin Warsh three weeks before his first Jackson Hole keynote (Fri Aug "
        "28). A Treasury bond-buyback operation mid-week bought exactly one day of relief before yields "
        "resumed climbing. In that window bitcoin ripped ~20% to $76,712 and gold broke to a 3-month high "
        "above $4,600 — both explicitly on US-debt-concern headlines the same week the national debt crossed "
        "$40 trillion. Equities bounced Friday on a blazing flash PMI (56.0, fastest since April 2022) but "
        "still closed a second straight losing week, with Big Tech down 3%+ and Meta down ~7% in five "
        "sessions. Layered on top: US-Canada trade talks collapsed and 50% tariffs are live on $20bn of "
        "Canadian goods; Trump declared an 'economic D-Day' campaign against Iran that implicitly threatens "
        "China, which responded by ordering its refiners to defy the sanctions outright — the same week "
        "Nvidia's Aug 26 guidance excludes China DC-compute revenue entirely. US HY credit spreads sit in "
        "the richest decile of their own history — the market that hasn't moved. The book's 2s10s steepener "
        "(+225%) is the regime's cleanest confirmation; the short-2Y-yield trade, built on a rate-cut premise "
        "the data now contradicts, is closed this refresh. Fresh money presses gold, a 2s30s steepener, a "
        "defined-risk NVDA put spread into Wednesday's print, and short HY credit."
    ),

    "summary_narrative": """
<p><strong>L1 &mdash; The driver.</strong> Fiscal dominance is reasserting itself: the 30-year Treasury yield hit
5.31% on Aug 17, the highest since July 2007 and within 13bp of the pre-crisis peak, as heavy long-dated issuance
and sticky tariff-fed inflation meet a market pricing new Fed Chair Kevin Warsh as genuinely hawkish three weeks
before his first Jackson Hole keynote (Fri Aug 28). CME FedWatch prices 0% odds of a September cut and ~30% odds
of a hike. A Treasury bond-buyback operation mid-week bought exactly one day of relief.</p>
<p><strong>L2 &mdash; Counter-intuitive hook.</strong> The government's own fix for the bond selloff is what lit
the debasement trade. In the 72 hours around the buyback, bitcoin ripped ~20% to $76,712 and gold broke to a
3-month high above $4,600 &mdash; both explicitly on US-debt-concern headlines. Liquidity meant to calm the
sovereign-debt market instead flowed into the two assets with no sovereign counterparty at all.</p>
<p><strong>L3 &mdash; The gap.</strong> Real economy: flash composite PMI 56.0, the fastest since April 2022,
services at a 20-month high, hiring at its best pace in over a year. What's priced: US HY spreads near 271-281bp,
the richest decile of their own history. Consensus narrative: the bond selloff is a technical supply story and
credit is right to look through it because growth is fine. The gap: strong growth, a hawkish Fed chair, and two
live Trump trade shocks (Canada tariffs, an Iran economic-warfare campaign that has provoked open Chinese
defiance) argue the cheapest, most-priced-to-perfection asset on the board &mdash; high-yield credit &mdash; is
not going to stay untouched.</p>
""",

    "takeaways": [
        "<strong>The 30-year hit its highest yield since 2007.</strong> 5.31% on Aug 17, ~13bp from the 2007 "
        "pre-crisis peak (5.44%), on heavy issuance, sticky inflation and a hawkish Warsh setup into Jackson "
        "Hole (Fri Aug 28). (Bloomberg.)",

        "<strong>The buyback bought one day.</strong> A Treasury bond-buyback operation mid-week gave one "
        "session of relief before yields resumed climbing. In that window bitcoin ripped ~20% to $76,712 and "
        "gold broke to a 3-month high above $4,600 &mdash; the debasement trade absorbed the liquidity, not "
        "the bond market. (Bloomberg, Fortune, TheStreet Crypto.)",

        "<strong>A red-hot PMI complicates the hawks' job.</strong> US flash composite 56.0, fastest since "
        "April 2022, services at a 20-month high, hiring at its best pace in over a year &mdash; genuine "
        "strength that ties Warsh's hands from riding to the rescue of a stressed long end. (S&P Global.)",

        "<strong>Two live Trump trade shocks.</strong> US-Canada talks collapsed Friday night; 50% tariffs "
        "now live on $20bn of Canadian goods. Trump's 'economic D-Day' campaign against Iran implicitly "
        "threatens China, which responded by ordering its refiners to defy the sanctions outright. (CNN, "
        "CNBC, Fortune.)",

        "<strong>Credit hasn't moved.</strong> US HY spreads sit near 271-281bp, the richest decile of their "
        "own history, even as the long end hits a 2007 high and a hawkish Fed chair takes the podium in five "
        "days. The market that moves last, hasn't moved at all. (Convex.)",

        "<strong>Micron blowout, NVDA the week's marquee catalyst.</strong> MU did >$41bn revenue (+340% "
        "YoY) and re-rated to ~$967, the book's largest weight. NVDA reports Wed Aug 26 AMC, priced for a "
        "clean beat (~95% implied odds) with China DC-compute revenue explicitly excluded from guidance. "
        "(Ad-Hoc News, Benzinga.)",

        "<strong>The trade is the catch-up, not the recycled winner.</strong> The book's 2s10s steepener "
        "(+225%) is held and trailed, not pressed further; fresh risk goes into gold, a 2s30s steepener, a "
        "defined-risk NVDA put spread, and short HY credit &mdash; where this week's regime is not yet priced.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "30%",
         "headline": "Warsh threads the needle; long end stabilizes; NVDA confirms the AI cycle",
         "body": "Jackson Hole (Aug 28) lands data-dependent rather than overtly hawkish, the 30Y pulls back "
                 "from its 2007-high test as term-premium fears ease, and growth stays strong enough that a "
                 "September hold reads as benign. Canada and Iran frictions plateau rather than escalate. "
                 "NVDA beats and the Data Center guide confirms the cycle Wednesday. Credit holds its tights "
                 "because growth really is this good. Risk up, curve holds its steepness on a lower long end, "
                 "gold/bitcoin consolidate their debasement gains, HY spreads stay tight."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "Hawkish-but-data-dependent Warsh; long end stays elevated; credit starts to lag",
         "body": "Warsh reiterates inflation-fighting credibility without an explicit hike signal; the 30Y "
                 "ranges just below its 5.31% high into the September FOMC. Canada and Iran frictions grind on "
                 "without a fresh shock. NVDA beats but the print is 'good, not great' given the China "
                 "exclusion, and the stock digests rather than melts up. HY spreads start to lag/widen modestly "
                 "as the term-premium story slowly bites. Risk choppy, curve stays steep, gold/bitcoin hold "
                 "their bid."},
        {"kind": "bear", "label": "Bear", "pct": "25%",
         "headline": "A genuinely hawkish surprise breaks the 2007 peak; credit finally cracks",
         "body": "Warsh delivers explicit hike-optionality language, the 30Y takes out 5.44% (the 2007 peak), "
                 "and HY spreads snap wider off their priced-to-perfection tights. China escalates its Iran-"
                 "sanctions defiance into broader trade retaliation that also clouds the chip-export detente, "
                 "hurting NVDA's Wednesday read; Canada's Sept 8 retaliation lands on top. Risk down sharply, "
                 "credit widens, gold and bitcoin extend even as risk assets fall &mdash; a genuine stagflation-"
                 "adjacent print."},
    ],

    "insights_layers": """
<p>The dominant driver this week is that the government tried to fix its own bond market and instead confirmed
the story the bond market is telling. The 30-year Treasury yield hit 5.31% on Aug 17 &mdash; the highest since
July 2007, thirteen basis points from the pre-crisis peak &mdash; on heavy long-dated issuance, sticky tariff-fed
inflation, and a market recalibrating around new Fed Chair Kevin Warsh three weeks before his first Jackson Hole
keynote. A Treasury bond-buyback operation mid-week bought exactly one day of relief before yields resumed
climbing.</p>
<p>The counter-intuitive hook is where the relief liquidity actually went. Everyone expects a bond-market stress
episode to send money into duration and out of risk; instead, in the 72 hours around the buyback, bitcoin ripped
roughly 20% to $76,712 and gold broke to its best level since mid-May above $4,600 &mdash; both explicitly on
US-debt-concern headlines the same week the national debt crossed $40 trillion. Two assets with no sovereign
counterparty priced the country's own balance sheet before the bond market that actually funds it finished doing
so.</p>
<p>Now the gap. Real economy: flash composite PMI 56.0, the fastest since April 2022, services at a 20-month
high, hiring at its best pace in over a year, price pressures at multi-month lows. What's priced: US high-yield
spreads near 271-281bp, inside the richest decile of their own history against a roughly 450bp long-run median.
Consensus narrative: the bond selloff is a technical issuance story, and credit and equities are right to look
through it because the PMI proves growth is fine. The gap &mdash; and where the alpha lives &mdash; is that
growth this strong, a Fed chair who says he is not constrained by market prices, and two live Trump-manufactured
trade shocks running simultaneously is not a combination that leaves the cheapest, most-priced-to-perfection
asset on the board untouched. Credit is the market that moves last, and this week it has not moved at all.</p>
<p>Go around the world. <strong>US:</strong> a genuinely strong PMI print bought back the index Friday while the
most rate-sensitive, highest-multiple names kept bleeding &mdash; Big Tech down 3%+ on the week, Meta down ~7% in
five sessions &mdash; the index headline and index leadership have diverged. <strong>Asia:</strong> the Nikkei
fell on the yield-sensitivity trade while the Hang Seng and KOSPI both rose on improving China-demand signals,
even as Beijing openly defies Washington on Iran-sanctions enforcement. <strong>Europe:</strong> the DAX, CAC and
FTSE all posted modest Friday gains but the region still tracked for a weekly decline on the same global bond
stress, with UK gilts elevated (10Y ~5.05%, 30Y ~5.82%) ahead of an Autumn Budget expected to raise taxes.</p>
<p>The political angle runs on two constraints. The Papic read: Warsh needs inflation credibility at his very
first Jackson Hole podium, but he is speaking into an economy running at its best pace in over four years and a
White House simultaneously waging two trade wars (Canada, Iran) that are their own inflation impulse &mdash; and
that same White House waived tariffs on beef imports the same week to fight food-price optics. He cannot be
hawkish enough to satisfy the bond market without drawing direct political friction from an administration that
needs growth to keep running hot. The second constraint sits with Beijing: China has now openly defied US
sanctions enforcement on Iranian oil the same week Nvidia's guidance depends on Beijing's cooperation to
monetise approved-but-undelivered H200 chip sales &mdash; two fronts of the same US-China friction converging on
one earnings print.</p>
<p>Priced-versus-not. <strong>Under-priced:</strong> a genuinely hawkish Jackson Hole outcome (CME shows ~30%
hike odds; equities aren't discounting that risk at all) and US high-yield credit risk. <strong>Fairly priced:</strong>
the debasement trade in gold and bitcoin &mdash; both already reflect the fiscal story cleanly. <strong>Over-priced
(at risk):</strong> NVDA's 'clean setup' narrative into Wednesday &mdash; a 4-for-4 beat streak and ~95% implied
beat odds leave no room for a print that is merely good.</p>
""",

    "wrap": """
<p>Consensus read this week as a bond-supply story: the Treasury oversupplies the long end, buyers demand a
bigger term premium, the 30-year backs up to 5.31% &mdash; its highest since July 2007 &mdash; and equities,
sensibly, look through it because Friday's flash PMI just printed the fastest US business growth since April
2022. The second-order effect nobody priced is that the Treasury's own fix for the selloff is what lit the
debasement trade. Mid-week the Treasury ran a bond-buyback operation to manage the duration glut it created; it
bought exactly one day of relief before the 30-year resumed climbing toward the 2007 peak. In the 72 hours around
that operation, bitcoin ripped roughly 20% to $76,712 and gold broke to a three-month high above $4,600. The
government tried to reassure its own bond market and instead confirmed, in real time, that it has to actively
manage the market for its own debt &mdash; and the money went straight into the two assets with no government
promise behind them.</p>

<p>Decompose the headline that Friday's rally papered over. The S&amp;P closed the week at 7,674.37 and the Dow
added over 500 points on a genuinely strong composite PMI &mdash; 56.0, services at a 20-month high, hiring at
its best pace since the start of last year. That is not a fragile print; it is the real economy accelerating into
a hawkish central bank. But the major indices still posted a second straight weekly loss, Big Tech shed over 3%
on the week and Meta is down almost 7% in five sessions &mdash; priced-for-perfection growth stocks are exactly
the instrument a rising discount rate hurts first, and Friday's bounce was breadth buying back the index, not
leadership returning to the names that actually drove the selloff. So what, who's wrong, what's the trade: a
strong economy walking into a hawkish Fed is not obviously bullish for the highest-multiple names carrying the
index, and the gap between the index headline and index leadership is where the mispricing sits.</p>

<p>L1 &mdash; the driver explaining most of this week's cross-asset moves: fiscal dominance is reasserting
itself, and the long end is voting no on the country's own funding math while a genuinely strong labor and
services economy ties the Fed's hands from riding to anyone's rescue. Call it the long-end revolt. The 30-year at
5.31% sits thirteen basis points from the 2007 pre-crisis peak of 5.44%, driven by heavy long-dated issuance,
tariff-fed inflation that refuses to fade, and a market recalibrating around new Fed Chair Kevin Warsh three
weeks before his first Jackson Hole keynote. CME pricing has flipped decisively: 0% probability of a September
cut, roughly 30% probability of a hike. A hawkish Fed chair, a red-hot PMI, and a bond market already at
multi-decade highs is not a setup where the central bank rescues anyone.</p>

<p>L2 &mdash; the counter-intuitive hook: everyone expects a bond-market stress episode to send money into
duration and out of risk. Instead the flight went into the two assets that have nothing to do with sovereign
credit at all. Bitcoin's overnight ramp above $69,000 and on to $76,712 traces directly to the week's Treasury
liquidity operation and a fresh regulatory tailwind &mdash; a short squeeze riding a government-funding story.
Gold's break above $4,600, its best level since mid-May, came explicitly on US-debt-concern headlines, with the
national debt crossing $40 trillion the same week. Two assets built to carry no counterparty risk are pricing the
country's own balance sheet before the bond market that actually funds it finishes doing so &mdash; the Pozsar
mechanic made literal: trace the flow, not the narrative, and the flow ran straight from a sovereign-debt
operation into the two instruments that owe nobody anything.</p>

<p>L3 &mdash; the gap. Real economy: composite PMI 56.0, the fastest since April 2022, services at 56.8, hiring
at its best pace in over a year, price pressures at a 10-month low in services. What's priced: US high-yield
spreads sit near 271-281bp, inside the richest decile of their entire history against a roughly 450bp long-run
median &mdash; priced as if none of the following exists. Consensus narrative: the bond selloff is a technical
supply story, and credit and equities are right to look through it because the PMI proves growth is fine. The
gap: growth this strong, a Fed chair signalling he is not constrained by market prices, a two-year note
re-pricing real hike odds, and two live Trump-manufactured trade shocks &mdash; a 50% Canada tariff imposed after
talks collapsed, and an economic-warfare campaign against Iran that explicitly threatens China, the buyer of
over 80% of Iran's oil &mdash; is not a combination that should leave the cheapest, most-priced-to-perfection
asset on the board untouched. Credit is the market that moves last, and it has not moved at all.</p>

<p>The Burry tell: NVDA is still only +21% year-to-date against the SOX's +63%, a gap that has persisted for
months and that Wednesday's print could close either direction &mdash; except the print itself carries a
structural blind spot nobody is pricing. Guidance explicitly excludes China data-center compute revenue, because
approved H200 sales remain stuck in legal limbo pending Beijing's own new supply-chain rules. The same week,
China openly defied Washington by ordering its refiners to keep buying sanctioned Iranian crude. A government
willing to publicly ignore US sanctions enforcement on oil has no particular reason to quietly smooth chip-import
approvals for a company whose stock is priced for a clean beat. That is a structural risk sitting entirely outside
the earnings model, and nobody is building it into Wednesday's implied move.</p>

<p>The Papic constraint closes the loop: Warsh needs credible hawkishness at his very first Jackson Hole podium
to establish inflation-fighting credentials, but he is speaking into an economy running at its best pace in over
four years, for a White House simultaneously waging two separate trade wars that are their own inflation impulse
&mdash; the same administration that waived tariffs on beef imports this week specifically to fight food-price
optics. He cannot lean hawkish enough to satisfy a bond market at 2007 highs without drawing direct political
friction from a White House that needs growth to keep running hot. The posture into the week: hold and trail the
book's steepener, which is this regime's cleanest confirmation; close out the dovish front-end trade the data now
contradicts; and press fresh risk into gold, a long-end-specific steepener, defined-risk protection on NVDA's
priced-for-perfection setup, and the credit market that has not caught up to any of it yet.</p>
""",

    "correlation_regime": """
<p><strong>1. Gold decoupled from real rates &mdash; now trading fiscal, not monetary.</strong> The textbook
says gold falls when real yields rise. This week gold rallied 2%+ to a 3-month high WHILE the 30-year backed up
to a 2007 high &mdash; the correlation that governed gold in July has broken. Gold is now pricing the debt/
issuance story directly, not the real-rate path. Own the debasement trade directly (the fresh gold idea); a
real-rate framework will keep mis-signalling this move.</p>
<p><strong>2. Bitcoin decoupled from risk sentiment &mdash; trading the same debasement story as gold.</strong>
A hawkish Fed setup and a stressed bond market would normally be risk-negative for a speculative asset like
bitcoin. Instead it ripped ~20% in the same window the 30-year hit its 2007 high, moving WITH gold rather than
against risk generally. Two assets normally uncorrelated to each other moved together on the same fiscal-concern
catalyst &mdash; that alignment is the tell that this is a debasement trade, not a risk-on trade.</p>
<p><strong>3. Index headline decoupled from index leadership.</strong> The S&amp;P closed the week at 7,674.37
on a Friday PMI-driven bounce, but Big Tech fell 3%+ on the week and Meta fell ~7% in five sessions &mdash; the
rate-sensitive, highest-multiple names are the ones actually paying for the 30-year's move, while the broad index
absorbed a growth-data bounce. A strong index close with a weak growth-stock cohort underneath it is not the same
signal as genuine broad-based strength.</p>
<p><strong>4. Credit decoupled from rates &mdash; the widest lag on the board.</strong> The 30-year hit a 2007
high and equities are digesting a real repricing, but HY spreads (271-281bp) sit inside the richest decile of
their own history, unmoved. Credit typically leads or confirms a rates-driven risk repricing; here it has simply
not shown up yet. That gap is where the fresh short-HY idea sits.</p>
""",

    "vol_skew": """
<p><strong>VIX term structure:</strong> VIX closed Friday at 15.13 (-5.5% on the day), still elevated off the
Aug 16 2026-low of 14.2 given the week's bond-vol stress. Structure is likely modestly in contango into a quiet
opening week before Wednesday's NVDA print and Friday's Jackson Hole keynote &mdash; both real, dated catalysts
the front end should be pricing more than it appears to be.</p>
<div style="height:8px"></div>
<p><strong>Rates vol (MOVE, est.):</strong> elevated off recent lows given the 30-year's move to a 2007 high;
the bond-vol story this week is real even where equity vol stayed contained &mdash; a genuine gap between the
two, and the cheaper convexity sits in rates and single-name (NVDA) options, not the index.</p>
<p><strong>Credit as a vol proxy:</strong> HY OAS in its richest-ever decile (271-281bp) is itself a
volatility signal &mdash; spreads this tight embed close to zero probability of the credit-repricing tail the
rates and political backdrop argue for. The structure that fits this regime: sell the calm in credit (short
HYG/long protection) and buy defined-risk optionality on the one binary event with real implied-move pricing
this week &mdash; NVDA's Wednesday print (the fresh put spread). Both are cheaper convexity than an index-level
VIX trade given the index itself is not where this week's real dispersion sits.</p>
""",

    "sector_rv": """
<div class="grid-2">
  <div class="tile tile-green">
    <div class="tile-head">Strongest &mdash; Memory / AI hardware (Micron confirmation)</div>
    <div class="tile-body">MU delivered >$41bn fiscal Q3 revenue (+340% YoY) and re-rated to ~$967 &mdash; the
    HBM/AI-memory supercycle the book's largest position rides is still accelerating. Sets up Wednesday's NVDA
    print as the read-through for the rest of the complex.</div>
  </div>
  <div class="tile tile-green">
    <div class="tile-head">Strongest &mdash; China-demand-linked Asia (Hang Seng, KOSPI)</div>
    <div class="tile-body">Hang Seng +0.76%, KOSPI +1.05% (Aug 21) on improving China-demand signals, even as
    Beijing openly defies US Iran-sanctions enforcement &mdash; a reminder that China's economic signals and its
    geopolitical posture are moving somewhat independently right now.</div>
  </div>
</div>
<div class="grid-2">
  <div class="tile tile-red">
    <div class="tile-head">Weakest &mdash; Long-duration growth / Big Tech</div>
    <div class="tile-body">Big Tech down 3%+ on the week, Meta down ~7% in five sessions, as the 30-year's move
    to a 2007 high hit the highest-multiple names hardest &mdash; the direct casualty of the long-end revolt,
    masked by Friday's index-level PMI bounce.</div>
  </div>
  <div class="tile tile-red">
    <div class="tile-head">Weakest &mdash; Japan (Nikkei, rate-sensitive)</div>
    <div class="tile-body">Nikkei -0.33% (Aug 21) as global yield pressure hits rate-sensitive real estate and
    tech hardest in a market with its own domestic yield story running in parallel.</div>
  </div>
</div>
<div class="tile tile-gold">
  <div class="tile-head">RV: Short US HY credit vs the long-end move (the catch-up trade)</div>
  <div class="tile-claim">HY spreads (271-281bp) have not repriced against a 30Y at a 2007 high, a hawkish Fed
  chair five days from Jackson Hole, and two live Trump trade shocks</div>
  <div class="tile-body">Credit is the market that moves last and, this week, has not moved at all. The gap
  between rates-market stress and credit-market complacency is the cleanest relative-value read on the board;
  express it as the fresh short-HY/long-protection idea rather than fight equities' PMI-driven bounce directly.</div>
</div>""",

    "positioning": """
<p><strong>The crowd is long the PMI-driven bounce, short vol, and has not repriced credit for a hawkish Fed
chair or a 2007-high long end &mdash; that combination is the pain trade.</strong> The loudest lean is the
'growth is fine so look through the bond stress' read: Friday's rally bought the index back on a strong flash
PMI while HY spreads sat in their richest-ever decile, unmoved. That is the crowded, complacent side. In rates,
fast money is still positioned for a Fed that eventually cuts; the 0%-cut/~30%-hike CME pricing and a hawkish
Warsh setup into Jackson Hole is the pain trade against that positioning (the closed short-2Y trade was on the
wrong side of exactly this). In FX, the crowd is still broadly dollar-constructive on haven flows; gold and
bitcoin both ripping on debasement concerns the same week is the early tell that the crowded dollar-strength
read is thinning (why MM-2026-012 is under review). In equities, the crowd is long the mega-cap growth names
that just absorbed the week's real damage (Big Tech -3%+, Meta -7%) while treating the index close as an
all-clear &mdash; the gap between index-level and leadership-level positioning is the trade. Into Wednesday,
NVDA options positioning implies near-certainty of a beat (~95% per Polymarket); a print that is merely good,
not great, is the crowded side's pain trade.</p>
""",

    "funding": """
<div class="tile tile-muted">
  <div class="tile-claim">SOFR ~3.63% &mdash; funding plumbing unstressed even as the long end sells off to a
  2007 high; no repo/RRP stress signal this window.</div>
  <div class="tile-body">The Pozsar mechanic made literal this week: the stress isn't in short-term funding, it's
  in the market for the government's own long-dated debt, and the government's attempted fix (the mid-week bond
  buyback) bought exactly one session of relief. Trace the flow, not the headline &mdash; liquidity meant to calm
  the Treasury market instead showed up as an ~8% overnight bitcoin ramp and a fresh gold breakout within 72
  hours. That is not normal funding-market behaviour; it is the debasement trade pricing the government's own
  balance sheet in real time. Watch whether the Treasury runs a second buyback operation into Jackson Hole week
  &mdash; a repeat operation with a shrinking half-life of relief is the plumbing tell that the supply/demand
  mismatch is structural, not one-off.</div>
</div>""",

    "tape_missing": """
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>US high-yield credit has not repriced for a hawkish Fed chair or a 2007-high long
  end &mdash; and it is the market that moves last.</strong> HY OAS sits near 271-281bp against a ~450bp
  long-run median, inside the richest decile of its own history. The falsifiable level: spreads widening through
  300bp on confirmation of a hawkish Jackson Hole says the credit catch-up trade is live and the short-HY idea
  pays; spreads holding sub-280bp through the September FOMC says growth genuinely is strong enough to justify
  the tightness and the trade should be cut. Watch HY OAS against the 30Y yield &mdash; the two should not stay
  this far apart through a hawkish Fed event.</div>
</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>A hawkish Jackson Hole outcome is not priced in equities at all.</strong> CME
  FedWatch shows ~30% odds of a September hike, yet the S&amp;P closed the week within a few percent of its
  highs. The falsifiable line: a Warsh speech Friday that explicitly raises hike optionality and sends the 30Y
  through 5.44% (the 2007 peak) is the level that should force an equity repricing that Friday's bounce is not
  currently discounting; a data-dependent, non-committal Warsh is the level that validates the current calm.</div>
</div>
<div class="canary">
  <div class="cdot"></div>
  <div class="ctext"><strong>The Burry tell: NVDA's Wednesday print carries a structural risk sitting entirely
  outside the earnings model.</strong> Guidance explicitly excludes China data-center compute revenue because
  approved H200 sales remain stuck in legal limbo pending Beijing's own new supply-chain rules &mdash; and the
  same week, China openly defied Washington by ordering its refiners to keep buying sanctioned Iranian crude. A
  government willing to publicly ignore US sanctions enforcement on oil has no obvious reason to quietly smooth
  chip-import approvals for a stock priced for a clean beat. Over the next one-to-two quarters this resolves one
  of two ways: China cooperation improves and the excluded revenue becomes a fresh upside surprise; or the
  broader US-China friction (visible now in the Iran-sanctions defiance) hardens and the China DC-compute
  opportunity stays permanently excluded from the model. Nobody is pricing this into Wednesday's implied move.</div>
</div>""",

    "consensus": """
<p><strong>Consensus BID:</strong> the bond selloff is a technical, supply-driven story &mdash; heavy issuance,
nothing more &mdash; and Friday's flash-PMI-driven bounce proves equities are right to look through it because
the real economy is genuinely strong. Warsh talks tough at Jackson Hole but ultimately stays data-dependent;
NVDA beats Wednesday as it almost always does; credit stays tight because growth justifies it.</p>
<p><strong>The strongest argument against &mdash; the OFFER:</strong> a 30-year at 5.31% is not merely a supply
story when it coincides with a hawkish incoming Fed chair, 0% priced cut odds, and two live Trump-manufactured
trade shocks generating their own inflation impulse. Gold and bitcoin have already voted with a debasement
rally; credit — the market that moves last — has not moved at all, which is precisely the gap the tightest,
most-complacent asset on the board should not be allowed to hold through a week with this much scheduled
catalyst risk (Jackson Hole, the September FOMC build, NVDA). The crowded side is long the PMI bounce and short
credit protection; the cheaper side owns the catch-up (short HY), the long-end-specific expression (2s30s), the
fiscal-debasement confirmation (gold), and defined-risk protection into a priced-for-perfection NVDA print.</p>
""",

    "one_chart": """
<p class="theme">The US HY OAS spread against the 30-year Treasury yield &mdash; the widest, least-priced gap on
the board.</p>
<p>The single thing worth watching this week is not an index level, it's the distance between two lines that
should be moving together and aren't: US high-yield credit spreads (271-281bp, richest decile of their own
history) against a 30-year Treasury yield at a 2007 high (5.31%). A hawkish Jackson Hole speech Friday that
pushes the 30Y through the 2007 peak (5.44%) without HY spreads moving in sympathy is the signal that credit is
mispricing a genuine repricing event; HY spreads finally widening through 300bp on the same catalyst is the
signal the catch-up trade (short HY/long protection) is live. Either way, watch the two lines against each
other &mdash; the gap is where this week's real risk is sitting, not in the index headline.</p>
""",

    "catalyst_calendar": [
        {"day": "Mon", "date": "Aug 24",
         "event": "US cash markets reopen post-Canada-tariff collapse; digesting Friday's PMI beat",
         "consensus": "No major scheduled US macro print. Markets reopen after a weekend of Canada-tariff "
                      "fallout (50% tariffs now live) and continued Iran/China friction. Sources: CNN, CNBC.",
         "view": "The open sets the tone for a week with three real dated catalysts (NVDA Wed, Jackson Hole "
                 "opens Thu, Warsh speaks Fri) — early positioning into all three starts here.",
         "asymmetry": "A gap-down on Canada/Iran headline risk is the entry window for the fresh gold and "
                      "short-HY ideas; a clean open validates Friday's PMI-driven calm.",
         "dir": "flat"},
        {"day": "Tue", "date": "Aug 25",
         "event": "HEICO (HEI) + Intuit (INTU) + Semtech + Zoom earnings — all AMC",
         "consensus": "HEI consensus ~$1.52 EPS (Finnhub, sourced); INTU consensus ~$3.65 EPS (Finnhub, "
                      "sourced). Both PRE-EARNINGS in the qualifying universe. Sources: Finnhub.",
         "view": "The warm-up act before NVDA — a clean beat from either sets a constructive tone for "
                 "Wednesday's much bigger print; a miss (as INTU had last quarter) raises the bar Wednesday "
                 "has to clear.",
         "asymmetry": "HEI's 4-straight-beat streak and unanimous buy-side skew the risk to the upside; INTU's "
                      "narrow prior-quarter miss makes it the more two-sided print of the two.",
         "dir": "flat"},
        {"day": "Wed", "date": "Aug 26",
         "event": "NVIDIA (NVDA) Q2 FY2027 earnings — AMC — the week's marquee catalyst",
         "consensus": "Guided ~$91bn revenue ±2%; consensus ~$92bn/~$2.09 EPS; Data Center est. >$85bn "
                      "(+107% YoY); China DC-compute revenue explicitly excluded from guidance. Sources: "
                      "Investing.com, Alphastreet, Rex Shares.",
         "view": "Priced for a clean beat (4-for-4 streak, ~95% implied odds per Polymarket) with a structural "
                 "blind spot: the China exclusion sits on the same fault line as this week's China-Iran-"
                 "sanctions defiance story.",
         "asymmetry": "A beat-and-raise with a constructive China DC-compute update is the upside tail; a "
                      "print that is merely 'in line' against ~95% implied beat odds is the disproportionate "
                      "downside the fresh put spread owns.",
         "dir": "up"},
        {"day": "Thu-Fri", "date": "Aug 27-28",
         "event": "Jackson Hole Economic Policy Symposium — Kevin Warsh's first keynote as Fed Chair (Fri)",
         "consensus": "Theme: 'Financial Innovation: Implications for Payments and Policy.' Warsh has signaled "
                      "he is 'not constrained by market prices' — read as a hawkish tell. Three weeks before "
                      "the September FOMC. Sources: Kansas City Fed, Intellectia, TechTimes.",
         "view": "The week's true macro event. A genuinely hawkish speech is the catalyst that could push the "
                 "30Y through its 2007 peak and finally force a credit repricing; a data-dependent, non-"
                 "committal tone validates the current calm across risk assets.",
         "asymmetry": "Hawkish surprise: 30Y through 5.44%, HY spreads widen, equities (esp. Big Tech) sell "
                      "off further. Dovish-leaning/data-dependent: long end stabilizes, the PMI-driven bounce "
                      "extends, credit stays tight.",
         "dir": "up"},
        {"day": "Mon", "date": "Sep 8 (look-ahead)",
         "event": "Canada's retaliatory tariffs take effect",
         "consensus": "Steel, dairy, appliances, agricultural equipment, pulp, paper and electronics — "
                      "Canada's response to the US's 50% tariffs on $20bn of Canadian goods. Sources: CBC, NPR.",
         "view": "Beyond the immediate 5-day window but the next dated milestone in the Canada trade-war "
                 "thread; sets up whether the friction plateaus or escalates into the September FOMC build.",
         "asymmetry": "A negotiated de-escalation before Sept 8 is the bull case for the trade-war thread; a "
                      "clean implementation with no talks resuming keeps a live inflation-impulse risk in the "
                      "September FOMC calculus.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 &middot; Short EURAUD:</strong> no live catalyst remains on either leg; close above 1.662
(the stop) or on any further drift with no fresh confirmation. Trim into strength rather than defend a dormant
position.</li>
<li><strong>MM-2026-009 &middot; 2s10s steepener:</strong> stop -10bp; target +60bp. At ~+55bp and +225%+ &mdash;
this week's 30Y-to-2007-high move is direct confirmation. Trail the stop; a credit-repricing-driven bear-flattener
(front bid on flight to quality) is the scenario that would reverse this fastest.</li>
<li><strong>MM-2026-012 &middot; Short EURUSD:</strong> stop 1.182, but the real signal is the debasement tape,
not the stop. A further extension in gold/bitcoin (both already on US-debt-concern headlines) is the trigger to
close this outright &mdash; a stale dollar-strength thesis has no business surviving a live dollar-debasement
tape. Only a genuinely hawkish Jackson Hole surprise rescues the position.</li>
<li><strong>MM-2026-013 &middot; Short US 2Y yield &mdash; CLOSED this refresh.</strong> The dovish-cut thesis was
built for a FOMC that resolved over two months ago; today's 0%-cut/~30%-hike CME pricing into a hawkish Warsh
setup is the opposite regime. Closed near flat; redeployed into the fresh 2s30s steepener, which expresses the
long-end-specific version of the same regime without fighting front-end hike risk.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The 30-year hit a 2007 high — should we be worried about the bond market?",
         "a": ("Worried about the wrong thing if you're only watching bonds. The move is real — 5.31%, the "
               "highest since before the financial crisis — but the more important tell is where the relief "
               "money went when the Treasury tried to calm it down. It ran a bond buyback mid-week, bought one "
               "day of relief, and in that window bitcoin jumped 20% and gold broke to a three-month high. "
               "That's not a bond-market story anymore, it's a government-debt-credibility story, and we're "
               "positioning the book for that directly with fresh gold exposure rather than just shortening "
               "duration.")},
        {"q": "Stocks bounced Friday on the jobs/growth data — is the worst behind us?",
         "a": ("For the index, maybe. For the names that actually drove the selloff, no. Big Tech is still "
               "down over 3% on the week and Meta is down nearly 7% in five days — the highest-multiple names "
               "are the ones actually paying for higher long-term rates, and Friday's bounce was a broad, "
               "PMI-driven relief rally, not those specific names catching a bid. We'd read the index level "
               "and the leadership underneath it as two different signals right now.")},
        {"q": "What's the new Fed chair going to say at Jackson Hole?",
         "a": ("Nobody knows for certain, but he's tipped his hand: he's said he's 'not constrained by market "
               "prices,' which in Fed-speak usually means don't assume he'll validate what futures are pricing. "
               "He's speaking three weeks before a September meeting where the market already prices real hike "
               "odds, into an economy that just posted its best growth data in over four years. That's a "
               "genuinely two-sided event and we're not pre-positioning hard into it either way — we closed the "
               "trade that was betting on him being dovish.")},
        {"q": "Should we be worried about the Canada and Iran headlines?",
         "a": ("They matter more for what they signal than for direct portfolio exposure. Both are Trump-"
               "manufactured trade shocks running at the same time — 50% tariffs on Canada, an economic-warfare "
               "campaign on Iran that's pushed China into openly defying US sanctions. Individually neither "
               "moves the book much. Together they're a live inflation impulse arriving at the same moment the "
               "Fed is trying to sound tough — that combination is exactly why we like owning the credit-market "
               "catch-up trade; spreads haven't priced any of this yet.")},
        {"q": "Micron just had a blowout quarter — does that change anything for Nvidia this week?",
         "a": ("It raises the bar. Micron's number confirms the AI-memory cycle is still accelerating, which is "
               "good context, but it also means the market walks into Wednesday's Nvidia print already primed "
               "for good news — a 4-for-4 beat streak and near-certain odds of another beat priced in. We'd "
               "rather own that print with a defined-risk structure than add more straight exposure into a "
               "setup that's priced for perfection, especially with the China piece of the guide still an open "
               "question.")},
        {"q": "Where's the cleanest new money going this week?",
         "a": ("Into what this week's data actually supports and the market hasn't caught up to. Gold, because "
               "it's now trading the fiscal-debt story directly, confirmed twice — once by its own breakout, "
               "once by bitcoin moving the same way. The long end of the curve specifically, because the 30-"
               "year is where the real stress is, not the front end. Defined-risk protection into Nvidia's "
               "print. And credit — high-yield spreads haven't moved at all this week, and that's the gap "
               "we're least comfortable calling fairly priced.")},
    ],

    "ideas_note": (
        "<p>Today's ideas press the regime the market hasn't fully priced &mdash; the long-end revolt, the "
        "debasement confirmation, and NVDA's priced-for-perfection setup &mdash; rather than recycle the book's "
        "existing winner. <strong>Long gold (spot)</strong> &mdash; the debasement trade, confirmed twice this "
        "week by gold's own breakout and by bitcoin moving the same way on the same catalyst. <strong>2s30s "
        "Treasury steepener</strong> &mdash; the long-end-specific expression of this week's move, distinct "
        "from the book's existing 2s10s (MM-2026-009), which is held and trailed rather than pressed further. "
        "<strong>NVDA defined-risk put spread</strong> &mdash; protection into Wednesday's priced-for-perfection "
        "print, sized against the book's existing NVDA holding. <strong>Short US HY credit / long protection</strong> "
        "&mdash; the catch-up trade: spreads sit in the richest decile of their own history and have not "
        "repriced for a hawkish Fed chair, a 2007-high long end, or two live Trump trade shocks. The steepener "
        "(MM-2026-009) is held and trailed; short EURAUD (MM-2026-001) and short EURUSD (MM-2026-012) are held "
        "on tight watches with no fresh catalyst; the short-2Y trade (MM-2026-013) is closed this refresh, "
        "thesis expired.</p>"
    ),

    "event_radar_note": (
        "<p>The buyback bought one day. The 30-year Treasury yield hit 5.31% on Aug 17 &mdash; the highest "
        "since 2007 &mdash; and a mid-week Treasury bond-buyback operation bought exactly one session of "
        "relief before yields resumed climbing. Bitcoin ripped ~20% to $76,712 and gold broke to a 3-month "
        "high above $4,600 in that window, both on US-debt-concern headlines the same week the national debt "
        "crossed $40 trillion. Equities bounced Friday on a strong flash PMI (56.0, fastest since April 2022) "
        "but still closed a second straight losing week, with Big Tech down 3%+ and Meta down ~7%. US-Canada "
        "trade talks collapsed and 50% tariffs are now live on $20bn of Canadian goods; Trump's 'economic "
        "D-Day' campaign against Iran has pushed China into openly defying US sanctions on Iranian oil, the "
        "same week Nvidia's Aug 26 guidance excludes China DC-compute revenue entirely. US HY credit spreads "
        "sit in the richest decile of their own history, unmoved. The book's 2s10s steepener (+225%) is the "
        "regime's cleanest confirmation; the short-2Y trade is closed this refresh, thesis expired. Fresh ideas "
        "press gold, a 2s30s steepener, a defined-risk NVDA put spread, and short HY credit.</p>"
    ),

    "burry_tell": (
        "NVDA's Wednesday print looks like an earnings event; the structural risk inside it is that a real "
        "slice of the guided opportunity depends on a government that just demonstrated, in public, that it "
        "will not cooperate with Washington when it doesn't want to. Guidance for the Aug 26 print explicitly "
        "excludes China data-center compute revenue, because Nvidia's approved-but-undelivered H200 chip sales "
        "to China remain stuck in legal limbo pending Beijing's own new supply-chain rules — the company itself "
        "has said it does not know whether any imports will be allowed. That would be a minor footnote in a "
        "normal week. This week, China's Ministry of Commerce openly rebuffed Trump's 'economic D-Day' campaign "
        "against Iran, called US sanctions a diversion, and — more concretely — ordered its own independent "
        "refiners in Shandong province, which account for roughly a fifth of China's refining capacity, to "
        "keep buying sanctioned Iranian crude in direct defiance of US Treasury sanctions on those same "
        "refiners. That is not a rhetorical objection; it is Beijing choosing to eat a direct sanctions hit "
        "rather than comply. A government making that calculation on oil has no obvious incentive to quietly "
        "smooth chip-import approvals for an American company's stock that is already priced for a clean beat. "
        "Over the next one-to-two quarters this resolves one of two ways: US-China friction cools from its "
        "current temperature and the excluded China DC-compute revenue becomes a fresh, un-modelled upside "
        "surprise for Nvidia; or it hardens — and it has real reason to harden, given the two live fronts "
        "(chips, Iran sanctions) converging on the same relationship — and the China opportunity stays "
        "permanently outside the model, quietly capping the multiple the market is currently paying for a "
        "'clean' AI-capex story. Nobody is pricing this into Wednesday's implied move; it does not show up in "
        "a beat/miss number, only in the guide's fine print."
    ),

    "earnings_summary": (
        "Three ideas this refresh. NVDA (Long, High &mdash; data gap flagged): the week's marquee print, "
        "Wed Aug 26 AMC — priced for a clean beat (4-for-4 streak, ~95% implied odds) but capped below clean "
        "High because guidance excludes China DC-compute revenue entirely, a data gap tied directly to this "
        "week's China-Iran-sanctions defiance story. HEI (Long, Medium): a steady four-straight-beat compounder, "
        "capped at Medium only because short interest is unavailable. INTU (Long, Medium): a more divided "
        "sell-side coming off a narrow prior-quarter miss, also capped by unavailable positioning data. All "
        "three report inside the next three trading days; NVDA is the one genuine binary event of the week, "
        "the other two are the warm-up act."
    ),
    "earnings_why": (
        "The universe filter is applied before scanning: market cap $10bn+, geographies US (primary) and South "
        "Korea (secondary), sectors Technology / Financials / Industrials / Utilities only. earnings_data.md "
        "(Finnhub, 2026-08-20 06:00 UTC) returns HEI and INTU as the qualifying pre-earnings names reporting "
        "inside the window (both Aug 25 AMC); their consensus EPS/revenue, recommendation splits and surprise "
        "history are SOURCED from Finnhub, with short interest unavailable so the positioning pillar is capped "
        "at 0 for both. NVDA is added despite sitting outside the Finnhub feed's coverage this refresh because "
        "it is the single largest scheduled catalyst of the week (Aug 26 AMC) and the book already carries the "
        "name (EQ-003) — every field for NVDA is web-sourced this refresh and tagged 'estimated' per the "
        "fallback rule. Other names in the Aug 20-25 window (SMTC, ZM, UI, DE, ADI, NDSN, JKHY, KEYS) either "
        "fall outside the 5-day pre / 3-day post window from today's run date or lack a sufficiently "
        "differentiated asymmetry case to clear the conviction bar; padding the section with the full cohort "
        "would dilute the signal rather than sharpen it."
    ),

    "book_aim": (
        "Astride the fiscal-dominance repricing, with the book's best trade (the 2s10s steepener) confirmed "
        "hard this week and one stale position closed outright. The 2s10s steepener (MM-2026-009) is the "
        "standout: +225%+ and rising as the 30-year's move to a 2007 high widened the spread while the front "
        "end stayed anchored — held and trailed, not pressed further, with the incremental long-end risk "
        "routed instead into a fresh 2s30s steepener. The short-2Y-yield trade (MM-2026-013) is discretionarily "
        "closed this refresh: its dovish-cut premise directly contradicts a Fed pricing 0% September cut odds "
        "and ~30% hike odds into a hawkish Warsh's first Jackson Hole keynote. Short EURAUD (MM-2026-001) and "
        "short EURUSD (MM-2026-012) sit on tight, largely inertial watches with no live catalyst; MM-2026-012 "
        "specifically is now fighting this week's dollar-debasement tape (gold and bitcoin both bid on US-debt "
        "concerns) rather than riding it, and a further debasement extension is the trigger to close it "
        "outright rather than wait for the stop. Fresh risk for the week: long gold (the debasement "
        "confirmation, doubled by bitcoin's simultaneous move), the 2s30s steepener (the long-end-specific "
        "expression), a defined-risk NVDA put spread into Wednesday's priced-for-perfection print (sized "
        "against the book's existing NVDA holding), and short US HY credit (the catch-up trade against a "
        "spread market that has not repriced for any of this week's stress). Into Jackson Hole (Fri Aug 28) "
        "and the September FOMC build: hold and trail the steepener; keep the two stale FX/rates legs on tight "
        "watches; do not add index-level equity beta while the index headline and index leadership are telling "
        "different stories."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is "
                 "the average of closed trades. Position-level marks are live (TradingView) where the feed "
                 "resolves; Fri Aug 21 web-verified closes are injected as a fallback only where the weekend "
                 "feed did not resolve a headline index. MM-2026-013 was discretionarily closed this refresh "
                 "on thesis-expiry grounds; its P&L reflects the close level, not a live mark.")
    },
    "idea_selection": [
        {"label": "Long gold (spot) — the debasement confirmation", "in": True,
         "text": ("The marquee fresh idea. Gold broke to a 3-month high above $4,600 explicitly on US-debt-"
                  "concern headlines, and bitcoin's simultaneous ~20% ramp on the same catalyst is independent "
                  "confirmation. Own the fiscal-dominance trade directly rather than through a rates proxy.")},
        {"label": "2s30s Treasury steepener — the long-end-specific expression", "in": True,
         "text": ("Distinct from the book's existing 2s10s (MM-2026-009), which is held and trailed. The 30-"
                  "year's move to a 2007 high is a long-end-specific story (issuance, term premium) that a "
                  "2s30s spread captures more directly than the 2s10s, which also carries front-end Fed-path "
                  "risk into Jackson Hole.")},
        {"label": "NVDA defined-risk put spread — protection into Wednesday's print", "in": True,
         "text": ("The options completion of the book's existing NVDA exposure. A 4-for-4 beat streak and ~95% "
                  "implied beat odds leave no room for a merely-good print, and the China DC-compute exclusion "
                  "is a real, un-modelled risk. Defined-risk protection, not a directional bearish call.")},
        {"label": "Short US HY credit / long protection — the catch-up trade", "in": True,
         "text": ("HY OAS (271-281bp) sits in the richest decile of its own history, unmoved by a 30-year at a "
                  "2007 high, a hawkish Fed chair five days from Jackson Hole, or two live Trump trade shocks. "
                  "Credit is the market that moves last; own the gap between rates stress and credit calm.")},
        {"label": "2s10s steepener (MM-2026-009) — held and trailed, not pressed", "in": False,
         "text": ("+225%+ and the cleanest confirmation of the week's regime. Held and trailed; the incremental "
                  "long-end risk goes into the fresh 2s30s idea instead of adding to an already-large winner.")},
        {"label": "Short EURAUD / short EURUSD (MM-2026-001, MM-2026-012) — tight watches, no fresh catalyst", "in": False,
         "text": ("Both are running on inertia rather than a live edge. MM-2026-012 specifically is now fighting "
                  "this week's dollar-debasement tape; a further gold/bitcoin extension is the trigger to close "
                  "it outright rather than a fresh idea to add to.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 14.5},
        {"label": "VIX",   "value": round(_g("vix") or 15.13, 2)},
        {"label": "VIX3M", "value": 16.5},
        {"label": "VIX6M", "value": 17.5},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.19, 3)},
        {"label": "10Y", "value": round(_g("us10y") or 4.74, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 5.28, 3)},
    ],

    "new_ideas": [
        {
            "id": "IDEA-A", "trade": "Long gold (spot) — the fiscal-debasement confirmation",
            "asset_class": "Commodity", "structure": "spot / cash",
            "entry": 4610, "stop": 4400, "target": 5100,
            "conviction": 8,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 2, "stop_quality": 1},
            "horizon": "months", "min_hold_days": 30,
            "thesis": ("Gold broke to a 3-month high above $4,600 explicitly on US-debt-concern headlines the "
                       "same week the national debt crossed $40 trillion and the 30-year hit a 2007-high yield. "
                       "Bitcoin's independent ~20% ramp on the same catalyst is confirmation this is a "
                       "debasement trade, not a single-asset move. Jackson Hole (Aug 28) and the September FOMC "
                       "build are the near-term catalysts; a genuinely hawkish real-rate shock is the risk, but "
                       "the fiscal story argues gold decouples from that playbook, as it already has this week."),
        },
        {
            "id": "IDEA-B", "trade": "2s30s UST curve steepener — the long-end-specific expression",
            "asset_class": "Rates", "structure": "spread",
            "entry": "~+112bp (30Y − 2Y)", "stop": "+70bp", "target": "+175bp",
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "3 months", "min_hold_days": 30,
            "thesis": ("The book's existing 2s10s steepener (MM-2026-009) is held and trailed after a 225%+ run; "
                       "this is the long-end-specific version. The 30-year's move to a 2007 high is driven by "
                       "issuance and term premium, distinct from the front-end Fed-path risk the 2s10s also "
                       "carries into Jackson Hole. If Warsh leans hawkish, the front end could firm even as the "
                       "long end keeps cheapening on supply — a scenario where 2s30s outperforms 2s10s."),
        },
        {
            "id": "IDEA-C", "trade": "Buy an NVDA put spread into the Aug 26 print (defined-risk protection)",
            "asset_class": "Equity (options)", "structure": "put spread",
            "entry": "~5%/12%-OTM, Sep expiry", "stop": "—", "target": "~4-5x on a disappointing print",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to Sep expiry", "min_hold_days": 0,
            "thesis": ("The options completion of the book's existing NVDA holding. A 4-for-4 beat streak and "
                       "~95% Polymarket-implied beat odds mean the stock is priced for a clean beat with no "
                       "room for 'good, not great' — and guidance explicitly excludes China DC-compute revenue "
                       "amid a live US-China friction episode (Beijing's open defiance on Iran sanctions the "
                       "same week). A defined-risk put spread caps the downside of a print that merely meets a "
                       "very high bar, without selling the book's core long exposure into the event."),
        },
        {
            "id": "IDEA-D", "trade": "Short US HY credit / long protection — the priced-to-perfection catch-up",
            "asset_class": "Credit", "structure": "CDX HY protection / short HYG",
            "entry": "~271-281bp OAS", "stop": "OAS < 240bp", "target": "OAS > 340bp",
            "conviction": 7,
            "conviction_breakdown": {"gap": 3, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("HY OAS sits in the richest decile of its own history against a ~450bp long-run median, "
                       "unmoved by a 30-year at a 2007 high, a hawkish Fed chair five days from his first "
                       "Jackson Hole keynote, or two live Trump-manufactured trade shocks (Canada tariffs, the "
                       "Iran economic-warfare campaign). Credit is the market that moves last; a hawkish Jackson "
                       "Hole surprise or any confirmation that the long-end move is a genuine repricing, not "
                       "just supply noise, is the catalyst that closes this gap fast."),
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

# ── Book outlook — "So what for the book" (Summary tab closer) ────────────────
brief["book_outlook"] = {
    "commentary": (
        "This week hands the book its cleanest macro confirmation and its clearest overdue exit in the same "
        "session. The <b>2s10s steepener</b> is the standout: the 30-year's move to a 2007-high yield widened "
        "the spread past +55bp from a +15bp entry, up 225%+ — the toll-free version of exactly the regime the "
        "trade was built for. The book's largest single-name weight, <b>Micron</b>, just delivered a blowout "
        "fiscal Q3 (>$41bn revenue, +340% YoY) and re-rated to ~$967, reinforcing rather than cracking the "
        "AI-memory thesis this desk has ridden since 2021 — though concentration discipline says monetise the "
        "rich IVol into strength, not just hold. <b>NVDA</b> is the live risk into Wednesday: priced for a "
        "clean beat with China DC-compute revenue excluded from guidance the same week Beijing openly defied "
        "US Iran-sanctions enforcement — a genuine, un-modelled risk sitting outside the print itself. The "
        "book's <b>fixed-income sleeve</b> (UST 2031, Siemens EUR IG) sits directly in this week's story: both "
        "are underwater on a 30-year at a 2007 high, and the bond-swap logic (harvest the loss, roll into "
        "current coupons at ~3x the running yield) is more urgent, not less, with long rates this stressed. "
        "<b>Xetra-Gold</b> is the one holding that should behave differently than July's playbook: gold is now "
        "decoupled from the real-rate framework that governed it a month ago and is trading the same fiscal-"
        "debasement story bitcoin just confirmed independently — treat it as a live hedge working as designed, "
        "not a rate trade to second-guess. The <b>USD sleeve</b> (~72% of the book) is more two-sided than it "
        "has been all summer: a debasement tape (gold, bitcoin both bid on US-debt concerns) argues the "
        "haven-dollar tailwind the scanner has flagged all year is thinning, which matters directly for an "
        "EUR-base client."
    ),
    "outperform": [
        {"name": "Micron (MU, ~30% of the book) — the blowout gets bigger", "why": "Fiscal Q3 did >$41bn "
         "revenue (+340% YoY) and >$25 EPS; the stock re-rated to ~$967 with a Street PT near $1,515. The "
         "AI-memory cycle confirmed again — but the largest single weight in a private-bank book still calls "
         "for monetising the rich option premium into strength, not letting concentration compound unchecked."},
        {"name": "Xetra-Gold (4GLD) — the hedge that changed its own playbook and is finally paying", "why": "Gold "
         "decoupled from the real-rate framework that hurt it in July and is now trading the fiscal-debasement "
         "story directly — confirmed independently by bitcoin's simultaneous ~20% move on the same US-debt-"
         "concern catalyst. Let the tail hedge run; this is the scenario it was built for."},
        {"name": "The USD sleeve (~72% of the book) — still a tailwind, but thinning", "why": "The dollar has "
         "not broken down, and the euro value of the book's US assets still benefits from any residual haven "
         "bid. But gold and bitcoin both voting against fiat-debasement risk this week is the early signal that "
         "this tailwind needs watching, not assuming, into Jackson Hole."},
    ],
    "underperform": [
        {"name": "NVDA (loss position) — the live risk of the week", "why": "Reports Wed Aug 26 into a setup "
         "priced for perfection (4-for-4 beat streak, ~95% implied odds) with China DC-compute revenue "
         "excluded from guidance amid open US-China friction. A defined-risk put spread protects the existing "
         "position into the print rather than adding or trimming outright before the number."},
        {"name": "UST 2031 & Siemens EUR IG (bond sleeve) — the 2007-high long end makes the swap more urgent", "why": "Both "
         "bonds are underwater on rates, not credit, and this week's 30-year move to a 2007 high only widens "
         "the case: the bond-swap (harvest the loss, roll into current coupons at roughly 3x the running "
         "carry) is a live, time-sensitive trade this window, not a standing watch item."},
        {"name": "AVGO & LVMH (existing losses) — no fresh catalyst this window", "why": "Neither name has a "
         "dated trigger inside the next five trading days; both remain candidates for the standing buffered-"
         "note re-entry (AVGO) and reverse-convertible (LVMH) structures already flagged, unchanged by this "
         "week's macro news."},
    ],
    "watch": [
        {"label": "Re-check the USD hedge before Jackson Hole, not after",
         "text": "The scanner's standing seagull/collar flag on the ~72% USD sleeve deserves a fresh look this "
                 "week specifically: a genuinely hawkish Warsh speech Friday would extend the dollar tailwind "
                 "further, while a data-dependent tone alongside a continuing gold/bitcoin debasement bid is "
                 "the scenario that erodes it. Better to price the hedge ahead of the event than react to it."},
        {"label": "Size the NVDA protection to the position, not the headline",
         "text": "The fresh put spread idea is designed to sit alongside the existing NVDA holding as portfolio "
                 "insurance into Wednesday's print, not as a fresh directional bet. Confirm sizing against the "
                 "live position before the print, not after a reaction has already happened."},
        {"label": "The bond-swap window is open — Bund/UST context favors acting this week",
         "text": "Both underwater bonds are pure rate-duration losses in a week where long rates are the entire "
                 "story. Harvesting the loss and rolling into current coupons is a timing-sensitive trade; "
                 "waiting for a rate pullback to \"improve the entry\" risks missing the point — the entry has "
                 "already improved relative to where these bonds were purchased, and the running-yield pickup "
                 "is available now."},
    ],
}

# ── Shark Tank pages ───────────────────────────────────────────────────────────
book.step("Rendering Shark Tank pages + fragments")
shark_format.render_all(brief, trades, regime_log, scan=scan)

# ── Persist state ──────────────────────────────────────────────────────────────
book.step("Saving trades.json + regime_log.json")
book.save_json(book.TRADES_PATH, trades)
book.save_json(book.REGIME_PATH, regime_log)

book.log(f"Open trades: {len(trades['open'])}  ·  Closed trades: {len(trades['closed'])}")
for t in trades["open"]:
    book.log(f"  {t['id']} | {t['trade'][:50]} | pnl {t.get('current_pnl_pct',0):+.2f}%")
