#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-08-13 (Thursday; US PRE-MARKET into PPI + the 30Y auction,
Asia closed, Europe mid-session). DEMAND DOES THE DIPLOMACY.

FIRST FULL NARRATIVE REFRESH SINCE JUL 14 (The Toll and the Trap) — a month of data-only fallbacks sits between
the chapters, so the bridge is stated explicitly:
- Since Jul 14 the book closed three legs on stops: gold (MM-005, Jul 15, -10.9%), short USDJPY (MM-007, Jul 22,
  -2.3%), short 10Y (MM-004, Jul 23, -5.4%). The 2s10s steepener kept widening: ~+50bp, +232%, 10bp from target.
- The hike storyline round-tripped: Sept hike odds ~64% (Jul 14) -> ~82% late July on war-energy costs -> collapsed
  after the big July jobs miss (Aug 7) -> ~40% after Wednesday's in-line July CPI. (CNBC, Kalshi, CNN.)
- The KOSPI round-tripped harder: -8.95% crash (Jul 13) -> re-entered a BULL MARKET, +3.56% to 6,813 today, 4th
  straight gain, Samsung +4.9%, SK Hynix +5.9%. (CNBC, Korea JoongAng Daily.) The Topix closed at a record, 7th
  straight gain. The AI trade did not die; it changed religion — from glut-panic to shortage-forever in 20 sessions.
TODAY'S WINDOW (Aug 12 ~11:30 BST -> Aug 13 ~11:30 BST):
- JULY CPI IN LINE (Wed 08:30 ET): headline +0.1% m/m / 3.4% y/y, core +0.2% m/m / 2.5% y/y — core the slowest
  since 2021. September HIKE odds fell to ~40% from ~50%. (CNBC, Babypips, Kalshi.) This is a Warsh Fed debating a
  HIKE, not a cut — Trump phones his own chair pressing for cuts (Bloomberg, Aug 10).
- THE LONG END DID NOT RATIFY IT. The $42B 10Y auction tailed: high yield 4.683% vs 4.580% prior, bid-to-cover
  2.53 vs 2.59; the 10Y closed ~4.69% after a post-CPI dip. $25B of 30Y paper prints TODAY 1pm ET, July PPI 08:30
  ET (cons +0.2% m/m) — both PENDING. (CNBC, Newsquawk.)
- AI MELTED UP: Super Micro +19%, CoreWeave +19% (rev $2.58B, +112% y/y), Lumentum +14%, Nebius +34%; Cisco beat a
  record quarter ($17.3B rev +18%, EPS $1.22) and FELL ~4.6% after hours on gross-margin mix; Cerebras beat on
  revenue (+103% y/y core) and sank after hours. AMAT reports TONIGHT. (CNBC, Investing.com, Motley Fool.)
- OIL FELL WITH THE STRAIT STILL SHUT. Trump (Truth Social, Aug 12): "The U.S.A. has total control over the Strait
  of Hormuz. I THINK WE WILL KEEP IT!" Iran: the strait "remains blocked"; Araghchi warns of "an even bigger
  miscalculation." A Houthi double-tap killed 6 on the Tihamah (Aug 11). And Brent still fell ~1.2% to ~$87.9 —
  because the EIA printed a +17.4m bbl US crude build and BOTH the IEA and OPEC cut 2026 demand: the IEA now sees
  demand FALLING 1.6m b/d in 2026 on high prices + disruption. Demand destruction is doing the diplomacy.
  (ABC, Al Jazeera, CNBC, OilPrice.)
- THE HIKERS ARE EVERYWHERE BUT WASHINGTON: ECB hiked in June (first in 3 years) and September is ~fully priced;
  BoE hikes priced by December; and Bloomberg reports Japan's government now BACKS a faster BoJ hike (Sept/Oct) with
  Japan PPI at 7.2% y/y and USDJPY ~159.4 after the Aug 1 US-Japan joint intervention — the first since 1998.
- BOOK ACTION: the steepener (MM-009) is 10bp from target — trail it, don't press. Fresh ideas press the NEW
  information: short USD/JPY (the double compression: BoJ hiking with government blessing while the Fed hike fades),
  a Brent put spread (own demand destruction with the war risk capped), a 5s30s steepener (rotate the winner into
  the long-end supply story), and an EWY put spread (fade the KOSPI's 20-session religion swap with defined risk).

Run:  python gen_2026_08_13.py
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
# Fallback: this is a Thursday PRE-MARKET brief (US cash open ~09:30 ET) into an 08:30 ET PPI and a 1pm 30Y
# auction. If the live feed does not resolve the US cash indices, inject the web-verified Wed Aug 12 closes
# (Motley Fool + Yahoo Finance, corroborated) so the dashboard never renders "unverified".
if "spx" not in snap:
    snap["spx"] = {"close": 7748.50, "chg_pct": 0.26, "chg_abs": 20.30}
if "dji" not in snap:
    snap["dji"] = {"close": 53770.27, "chg_pct": -0.04, "chg_abs": -21.60}
levels = live_levels.trade_levels(snap)

# Supplemental live lines for today's narrative (probed working symbols, 2026-08-13).
try:
    _extra = live_levels.scan(["KRX:KOSPI", "FX_IDC:USDKRW", "NASDAQ:SOX", "TVC:US05Y"])
except Exception:
    _extra = {}
def _x(tk, fallback):
    return _extra[tk]["close"] if tk in _extra else fallback
KOSPI_LVL  = _x("KRX:KOSPI", 6813.34)
USDKRW_LVL = _x("FX_IDC:USDKRW", 1421.0)
SOX_LVL    = _x("NASDAQ:SOX", 12399.4)
US05Y_LVL  = _x("TVC:US05Y", 4.348)

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

# ── RSI screener ───────────────────────────────────────────────────────────────
book.step("Running RSI screener (broad cross-asset universe, Yahoo)")
screen = fetch_rsi.run_screener()
book.log(f'  scanned {screen["scanned"]} · {len(screen["oversold"])} oversold · '
         f'{len(screen["overbought"])} overbought · {screen["errors"]} no-data')

# Authored screener notes — desk view keyed by ticker; live names without a note get a templated read.
SCREENER_NOTES = {
    "MU":   "The book's largest weight (~30% of the Fable book) just got its narrative back — and that is exactly why "
            "the discipline holds. Twenty sessions ago Korea Investment was cutting SK Hynix's numbers and the KOSPI "
            "crashed 9%; today the KOSPI is BACK IN A BULL MARKET (+3.56%, 4th straight gain), SK Hynix +5.9%, and "
            "management talks a memory shortage lasting 'beyond 2030.' Same fabs, same capacity race, opposite "
            "religion. A crowd that swings glut-to-shortage in a month is trading narrative, not supply — monetise "
            "the rich IVol into THIS strength (collar/overwrite at far better levels than July's panic), never add "
            "to the 30% weight into a melt-up.",
    "NVDA": "The AI-capex flagship in a tape that just re-crowned the trade: CoreWeave +19% on +112% revenue growth, "
            "Super Micro +19%, the KOSPI in a bull market. The fade risk is no longer the glut headline — it is the "
            "margin line Cisco just flagged (record quarter, stock down ~4.6% after hours on hardware-mix gross "
            "margin). Own the leader, but the fresh convexity is on the froth's edges (EWY put spread, MM-055), not "
            "on more mega-cap length at VIX ~15.",
    "AMD":  "Still the high-multiple challenger the book HOLDS (+394%) — and the melt-up is the exit door, not the "
            "entry. The complex re-rated in a straight line for four sessions; a name at a triple-digit multiple is "
            "the first casualty when the PPI or the 30Y auction taxes the rally. Trim the exhausted winner into "
            "strength — concentration management — and let the defined-risk Korea fade (MM-055) own the downside.",
    "XLE":  "Energy is the day's laggard and the tell: Brent FELL ~1.2% to ~$87.9 with the strait still shut, Houthis "
            "killing sailors and Araghchi threatening 'miscalculation' — because the EIA printed a +17.4m bbl build "
            "and the IEA/OPEC both cut 2026 demand (IEA: -1.6m b/d). Demand destruction is doing the diplomacy. The "
            "book's TotalEnergies length has had its war; own the downside of the premium with a defined-risk Brent "
            "put spread (MM-053), don't add energy beta at $88.",
    "GLD":  "Gold reclaimed $4,400 — a two-month high, NOT a record (the record is ~$5,600, January) — as the cool "
            "core buried the September hike and real-rate pressure eased. The bitter coda: the book's gold long was "
            "stopped Jul 15 at ~$4,000 in the toll regime; the thesis was right, the regime was wrong. The lesson "
            "stands — gold trades the Fed, not the war. It only re-enters this book with a defined-risk structure "
            "and a rate catalyst, not on spot momentum.",
    "TLT":  "Duration still has no friends at the long end: the 10Y auction TAILED at 4.683% (b/c 2.53) a day after "
            "an in-line CPI, and $25B of 30Y paper prints today at 1pm. Record Treasury supply plus record AI-capex "
            "IG issuance is a term-premium machine — the long end is being asked to fund the deficit AND the data "
            "centres. Own the curve (2s10s ~+50bp, MM-009 near target; fresh 5s30s, MM-054), not outright duration — "
            "the same lesson that stopped MM-004 in July.",
    "HYG":  "Credit is priced close to perfection — HY OAS ~270-280bp vs a long-run median near 450 — in the richest "
            "decile of history, while IG issuance runs at a record pace on AI capex borrowing. Nothing in the window "
            "widened it: the melt-up keeps the valve shut. That is exactly why the up-in-quality bias costs so "
            "little. No fresh position today; the growth-scare tail is owned in oil (MM-053) where the demand crack "
            "is actually printing.",
    "XLF":  "The quiet leadership: European banks +1.2% this morning as the ECB's September hike sits ~fully priced, "
            "and US financials get the same gift — a steeper curve (2s10s ~+50bp) without a Fed cut cycle killing "
            "the front book. The banks-vs-chips RV from July has done its work; the curve trade (MM-009/MM-054) is "
            "now the cleaner expression of the same regime.",
    "SMH":  "US semis +2.5% Wednesday and the KOSPI in a bull market — the July catch-down never fully came, and the "
            "complex round-tripped into shortage-forever euphoria instead. AMAT reports TONIGHT (cons ~$3.45, 39 buy "
            "/ 6 hold, four straight ~5% beats) into a four-day melt-up: good news is priced, margin news is not "
            "(ask Cisco). The defined-risk fade lives in Korea (EWY, MM-055) where the froth is loudest.",
    "SPY":  "Within ~0.1% of the record (7,757.64, Aug 7) at VIX ~15, into a PPI print and a 30Y auction the SAME "
            "day, 24 hours after the 10Y tailed. The index is priced for the front end's relief and blind to the "
            "long end's invoice. Not a fresh short — the July put spreads taught the premium-bleed lesson — but no "
            "chase either: the marginal dollar goes to the curve and the defined-risk fades.",
    "EEM":  "EM's tell is the divergence: the KOSPI surged 3.56% INTO a weaker won (~1,421), India's RBI is selling "
            "dollars to cap a record-weak rupee (~95.3), and the PBoC is guiding the yuan to its strongest fixings "
            "since 2023 (~6.745). Equity euphoria without FX endorsement is hedged, hot-money buying — it leaves "
            "fast. The Korea froth fade (MM-055) owns exactly that seam with defined risk.",
    "BTC":  "Bitcoin is the melt-up's conscientious objector: ~$63.5k, range-bound $62-66k since early July, 30-day "
            "implied vol at its lowest since September, puts still over calls. The speculative long tail refuses to "
            "confirm the AI froth — the marginal risk dollar is going into chips and neoclouds, not coins. A tell "
            "on how narrow the mania is. Not a book position.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("Demand Does the Diplomacy: A Cool Core Buries the September Hike and the AI Trade Roars Back From Its "
          "Own Crash — While the Long End Taxes the Rally at Auction, Oil Falls With the Strait Still Shut, and "
          "Every Central Bank but the Fed Is Hiking")
regime_note = (
    "The most important thing about the last 24 hours is what refused to confirm. Wednesday's July CPI printed "
    "exactly in line — headline +0.1% m/m and 3.4% y/y, core +0.2% and 2.5%, the slowest core since 2021 — and the "
    "market did what it has waited a month to do: it buried the September hike, taking the odds from ~50% to ~40%, "
    "and re-crowned the AI trade. Super Micro and CoreWeave rose 19% apiece, Lumentum 14%, the KOSPI surged 3.56% "
    "back into a bull market and the Topix closed at a record. (CNBC, Motley Fool, Korea JoongAng Daily.) But two "
    "markets refused to ratify the party. The long end tailed its own auction — $42B of 10-year notes stopped at "
    "4.683% against 4.580% last month, bid-to-cover 2.53, the same day the front end rallied — and oil FELL with "
    "the Strait of Hormuz still shut, Houthi missiles killing six sailors on the Tihamah, and Iran's foreign "
    "minister warning of 'an even bigger miscalculation.' Brent dropped ~1.2% to ~$87.9 because the EIA printed a "
    "+17.4 million barrel US crude build and both the IEA and OPEC cut 2026 demand — the IEA now expects demand to "
    "FALL 1.6m b/d this year. (Newsquawk, ABC, Al Jazeera, OilPrice.) The Doomberg pivot: consensus reads the oil "
    "pullback as peace getting closer; the second-order truth is the opposite — demand destruction is doing the "
    "diplomacy, the cure for $90 oil is $90 oil, and a barrel that falls while the war stands still is a demand "
    "signal, not a peace signal. So what, who's wrong, what's the trade: the equity tape is pricing the front "
    "end's relief and ignoring the long end's invoice — own the curve, own the demand crack in oil with defined "
    "risk, and fade the loudest froth, not the index. "
    "Decompose the rally and the Campbell anatomy says the same thing. The S&P sits within a tenth of a percent of "
    "its record at VIX ~15, but the leadership is a handful of AI-infrastructure names re-rating on the same "
    "religion that crashed them in July — the KOSPI swung from a 9% glut-panic crash to shortage-'beyond-2030' "
    "euphoria in twenty sessions on the same fabs and the same capacity race. Cisco printed a RECORD quarter, +18% "
    "revenue, raised its AI targets — and fell 4.6% after hours on gross-margin mix. The headline says AI boom; the "
    "anatomy says the boom is now taxing its own suppliers' margins and its own funding curve: hyperscaler AI capex "
    "is driving record IG issuance into the same long end the Treasury is flooding, which is why the 10-year tails "
    "a day after a friendly CPI. The Pozsar mechanic: the long end is being asked to fund the deficit and the data "
    "centres at once — term premium is the funding constraint of the AI buildout, and today's $25B 30-year auction "
    "prices it in public at 1pm. "
    "The Papic constraint has rotated inside the Fed itself. Trump got his chair in Kevin Warsh — and Bloomberg "
    "reports he now phones him pressing for cuts while Warsh's own market prices a live HIKE debate into a midterm "
    "year; the White House is simultaneously being sued over a $1.2M-a-year 'Truth API' selling early access to "
    "the very posts that move oil. Meanwhile every other G10 central bank is hiking into the same energy shock the "
    "Fed is told to look through: the ECB's September hike is ~fully priced, the BoE is priced to hike by December, "
    "and Japan's government — per Bloomberg — now BACKS a faster BoJ hike with wholesale inflation at 7.2% and the "
    "yen defended by the first joint US-Japan intervention since 1998. September is a three-central-bank hike "
    "window with the Fed the least likely hiker in it. The non-consensus read: the Fed-independence risk is "
    "inverted — the danger is not Trump capturing the Fed, it is Warsh hiking into Trump's economy and forcing the "
    "rupture into the open. "
    "The book comes into this chapter carrying the scar tissue and the winner. Since Jul 14 the stops took out "
    "gold (-10.9% — stopped at $4,000; it trades $4,400 a month later, the thesis right and the regime wrong), the "
    "short-USDJPY (-2.3% — three weeks before the government started backing BoJ hikes), and the short-10Y (-5.4% "
    "— duration never got its haven bid). What survived is the point: the 2s10s steepener is +232% at ~+50bp, ten "
    "basis points from target, and the tailed auction plus today's 30-year supply is exactly its regime. The trade "
    "now is rotation, not repetition: trail the 2s10s and rotate the same supply logic out the curve (5s30s), "
    "re-enter the yen from the NEW data (a hiking BoJ with government blessing against a Fed whose hike is "
    "fading), own oil's demand crack with a defined-risk put spread instead of fighting Hormuz headlines, and fade "
    "Korea's twenty-session religion swap with an EWY put spread while vol is cheap. The regime is not risk-off — "
    "it is a melt-up whose bill is being priced at the long end, in the barrel, and in Seoul's froth, and the book "
    "gets paid for reading the bill before the tape does."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)
# No close action today: none of the four open legs is at stop or target. MM-009 (2s10s) sits ~10bp from its
# +60bp target — trailed, not pressed. MM-012's thesis is on a tight leash (ECB hiking into a fading Fed hike),
# but the position is green and the stop (1.182) governs; the discipline is the trim signal at 1.16, not an
# early exit at a profit into a still-firm dollar tape.

# ── Per-trade enrichment ────────────────────────────────────────────────────────
TRADE_ENRICHMENTS = {
    "MM-2026-001": {
        "instrument": (
            "EUR/AUD spot FX cross-rate. EUR = euro (ECB-managed); AUD = Australian dollar (commodity-linked, "
            "RBA-managed). Driven by relative ECB-vs-RBA rate paths, iron-ore/commodity terms of trade, global "
            "risk sentiment, and the 2-year eurozone-vs-Australia rate spread."
        ),
        "fundamental_thesis": (
            "The stale leg, modestly green (~+0.6% at ~1.635) and running out of reasons to exist. The original "
            "edge — a paused ECB against a firm AUD — has inverted: the ECB is now HIKING (June done, September "
            "~fully priced), which is structurally EUR-supportive, while the AI melt-up and firm commodity complex "
            "keep the AUD bid the other way. Two live forces, neither ours. The 1.61 target needs a risk-off AUD "
            "crack that today's bull-market tape argues against. Hold only on the tight leash: stop 1.662, and "
            "treat any push toward 1.645 as the trim."
        ),
        "catalysts": [
            "ECB September hike (~fully priced) — structurally EUR-supportive, AGAINST the short",
            "The AI melt-up / commodity bid — keeps the AUD firm, also against the target",
            "RBA path and China credit data (due by ~Aug 15) — the AUD swing factor",
            "A risk-off crack (hot PPI, failed 30Y auction) — the one route to 1.61",
        ],
        "risks": (
            "An ECB hike into a fading Fed hike squeezes EUR crosses broadly and runs the 1.662 stop; firm China "
            "data lifts the AUD's terms of trade against us too — the trade can lose on either leg now. Stop 1.662."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the rate-path gap the short was built on has inverted with the ECB hiking; what "
                            "is left is positioning residue, not mispricing.",
            "catalyst":     "0/2 — no dated catalyst works for the short; the dated events (ECB, China data) work "
                            "against it.",
            "positioning":  "1/2 — EUR shorts are no longer crowded; some unwind fuel remains, two-way.",
            "confirmation": "1/2 — the cross has drifted our way (~+0.6%) but on no thesis of ours.",
            "stop_quality": "1/1 — 1.662 is a clean level; the leash is the whole risk case.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (own the front's anchor/cut optionality), short the "
            "10Y (short fiscal-supply/term-premium risk). Pays when 10Y-minus-2Y widens. Now ~2Y 4.17% / 10Y "
            "4.67%, spread ~+50bp from a +15bp entry."
        ),
        "fundamental_thesis": (
            "The champion, ten basis points from the finish line — and the last 24 hours were a demonstration of "
            "exactly why it worked. An in-line CPI rallied the FRONT end (September hike odds ~40%), while the "
            "long end TAILED its own $42B auction at 4.683% and faces $25B of 30-year supply today — the front "
            "trades the Fed, the back trades the flood. Record Treasury issuance plus record AI-capex IG "
            "borrowing keeps the long end heavy in either CPI outcome. At ~+50bp of a +60bp target and +232%, the "
            "job now is harvest discipline: trail the stop up through the auction, take the target if it prints, "
            "and rotate the same logic out the curve (5s30s, MM-054) rather than pressing a nearly-done trade."
        ),
        "catalysts": [
            "TODAY: July PPI 08:30 ET + the $25B 30Y auction 1pm ET — both steepen on a tail or a hot print",
            "The tailed 10Y auction (4.683%, b/c 2.53) — the supply/term-premium engine, live and confirmed",
            "Sept hike odds ~40% and falling — the front-end anchor",
            "Risk: a hot PPI re-arms the hike and bear-flattens via the front — the one adverse path",
        ],
        "risks": (
            "A hot PPI (cons +0.2% m/m) within 24h of the cool CPI re-prices the September hike and backs up the "
            "2Y faster than the 10Y; a stellar 30Y auction relieves the term-premium bid. Stop: spread below "
            "-10bp (structural), trailed in practice near +35bp; target +60bp, ~10bp away."
        ),
        "breakdown_why": {
            "gap":          "2/3 — most of the 18-month-inversion normalisation is banked; the remaining gap to "
                            "target is supply-driven, not mean-reversion.",
            "catalyst":     "2/2 — PPI and the 30Y auction land TODAY; the 10Y tail already confirmed the engine.",
            "positioning":  "1/2 — the steepener is closer to consensus than in June; less pain-trade fuel left.",
            "confirmation": "2/2 — +50bp through a friendly-CPI week and a tailed auction; the widening is durable.",
            "stop_quality": "1/1 — a trailed stop into a dated target; the failure threshold is clean.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US growth, risk "
            "sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "Green but living on borrowed thesis. The short is +0.6% at ~1.153 with a distant 1.182 stop — but "
            "the policy engine has flipped: the ECB is hiking (September ~fully priced, Lagarde warning on "
            "second-round energy effects) while the Fed's September hike FADED to ~40% on the cool CPI. The rate "
            "differential is now moving euro-positive; what keeps the short alive is the dollar's haven bid and "
            "the euro area's terms-of-trade drag from $88 oil. That is a hedge's thesis, not a conviction short's. "
            "The discipline: hold while the tape pays, trim on a EUR reclaim of 1.16, and do not add — the "
            "asymmetry has left."
        ),
        "catalysts": [
            "ECB September hike ~fully priced vs a fading Fed hike — the differential turning AGAINST the short",
            "TODAY'S PPI — a hot print revives the Fed hike and the dollar; a cool one hands the euro the carry",
            "Oil ~$88 — the euro-negative terms-of-trade drag, now itself fading on demand cuts",
            "US-Japan intervention regime — official dollar-SELLING is in the market for the first time since 1998",
        ],
        "risks": (
            "The ECB hikes into a Fed that doesn't, the differential compresses and EUR/USD squeezes through 1.16 "
            "then toward the 1.182 stop; official US participation in yen intervention is a standing dollar-"
            "selling presence. Stop 1.182; trim signal 1.16."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the rate-differential edge has inverted; what remains is the haven bid and the "
                            "oil drag, both fading.",
            "catalyst":     "1/2 — today's PPI is dated but two-sided for this leg.",
            "positioning":  "1/2 — short-EUR is no longer crowded; squeeze risk on a cool PPI is real.",
            "confirmation": "1/2 — price still confirms (green, dollar firm) while the thesis erodes — the "
                            "definition of a tight leash.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; the 1.16 trim line is the real discipline.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receive 2Y swap / long 2Y notes). The 2Y is the market's real-time "
            "forecast of the Fed path over two years — the most policy-sensitive point on the curve."
        ),
        "fundamental_thesis": (
            "The fade that finally got its catalyst — and is still barely flat. The 2Y sits ~4.17% against a "
            "4.162% entry after the cool CPI took September hike odds to ~40%: the front end is repricing the "
            "hike OUT, which is exactly this trade's engine. The thesis — the front end over-prices a 2026 hike "
            "into a cracking labour market (the July jobs miss that collapsed the odds from ~82%) — is now "
            "CONFIRMED by the data path, but the P&L has lagged because the oil premium keeps a floor under the "
            "front. Today's PPI is the decider in both directions: a cool print pays the fade toward 4.05%; a hot "
            "one re-arms the hike and backs the 2Y toward the 4.35% stop. Min-hold elapsed; the curve (MM-009) "
            "remains the higher-conviction sibling."
        ),
        "catalysts": [
            "TODAY: July PPI 08:30 ET — the second inflation print of the two-print week; the decider",
            "Sept hike odds ~40%, down from ~82% late July — the repricing is running our way",
            "The July jobs miss (Aug 7) — the labour crack that started the collapse in hike odds",
            "Jackson Hole (late Aug) — Warsh's first symposium; the venue for walking the hike fully off",
        ],
        "risks": (
            "A hot PPI within 24 hours of a cool CPI re-prices the September hike and backs the 2Y toward the "
            "4.35% stop; a renewed oil spike (Hormuz 'miscalculation') does the same via the energy channel. "
            "Stop 4.35%; target 3.85%."
        ),
        "breakdown_why": {
            "gap":          "2/3 — a front end still pricing ~40% of a hike into a labour crack and a cooling core "
                            "is a real, data-attributable mispricing.",
            "catalyst":     "2/2 — PPI is TODAY; Jackson Hole is dated; the jobs-miss path is live.",
            "positioning":  "1/2 — fast money flipped from ~82% hike pricing; the squeeze has partly run.",
            "confirmation": "1/2 — odds confirm, price barely does (~flat); the tape owes the trade its move.",
            "stop_quality": "1/1 — 4.35% is a clean level, ~18bp of risk against a 30bp+ target path.",
        },
    },
    # ── New ideas generated today ────────────────────────────────────────────────
    "MM-2026-052": {
        "instrument": (
            "Short USD/JPY spot (long yen). Driven by the US-Japan rate differential (the widest engine in G10), "
            "BoJ normalisation, Fed path, risk sentiment, and — uniquely now — an OFFICIAL ceiling: the Aug 1 "
            "US-Japan joint yen-buying intervention (the first since 1998) defended ~164, with Bessent signalling "
            "readiness for more."
        ),
        "fundamental_thesis": (
            "The re-entry the NEW data justifies. The book's July yen short was stopped at 163 in the oil-funder "
            "regime; three weeks later every input has flipped. Bloomberg reports Japan's government now BACKS a "
            "faster BoJ hike (September or October) — the Takaichi administration's incentive flipped by a "
            "40-year-low yen and 7.2% wholesale inflation; three of nine BoJ board members already argue for a "
            "faster pace; markets price ~60-74% for September. Against that, the Fed's September hike faded to "
            "~40% on a cool core. The differential compresses from BOTH sides for the first time in the cycle — "
            "and the trade carries an official backstop: the first joint US-Japan intervention since 1998 sits at "
            "~164, meaning officialdom fights the move that would stop us out. Entry ~159.4; stop 164.5 (above "
            "the intervention line); target 153."
        ),
        "catalysts": [
            "Bloomberg (Aug 13): Japan's government said to support a faster BoJ hike — Sept/Oct live",
            "Japan July PPI 7.2% y/y — the imported-inflation pressure forcing the government's hand",
            "Fed September hike fading (~40% post-CPI) — the US side of the compression",
            "The Aug 1 joint intervention at ~164 + Bessent's 'ready for more' — the official ceiling",
        ],
        "risks": (
            "The BoJ scoop is single-sourced (Bloomberg) — a denial re-widens the differential; a hot US PPI "
            "re-arms the Fed hike and the carry; the yen remains the funding leg of every risk-on melt-up day. "
            "Stop 164.5, above the intervention ceiling — if officialdom loses that line, the thesis is wrong."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY at ~159 prices none of a September BoJ hike with government blessing; "
                            "the differential math says low-150s on the compression.",
            "catalyst":     "2/2 — BoJ Sept/Oct is dated; the government-backing scoop is fresh; Jackson Hole "
                            "dates the Fed side.",
            "positioning":  "2/2 — the yen carry is the most crowded funder in G10 and the crowd is short the "
                            "yen against an official buyer — the pain trade is violent.",
            "confirmation": "1/2 — the yen has stabilised (~159 vs 164) but not yet trended; one confirming leg.",
            "stop_quality": "1/1 — 164.5 sits above a publicly defended intervention line; the cleanest stop in FX.",
        },
    },
    "MM-2026-053": {
        "instrument": (
            "Buy a Brent Dec-26 $85/$75 put spread — defined-risk downside on the waterborne barrel. Max loss is "
            "the premium. Brent ~$88 still carries a war premium (the strait is SHUT), while the demand data just "
            "broke: EIA +17.4m bbl US build, IEA and OPEC both cutting 2026 demand (IEA: -1.6m b/d)."
        ),
        "fundamental_thesis": (
            "Own the demand destruction, cap the war risk. The single most information-rich move of the window is "
            "a barrel that FELL ~1.2% while Houthi missiles killed sailors, Iran called the strait 'blocked' and "
            "Araghchi threatened 'an even bigger miscalculation' — the demand side (a 17.4m bbl build, two "
            "agencies cutting 2026 demand, the IEA now seeing demand FALL 1.6m b/d) is overwhelming a live war "
            "premium. And the non-consensus path is bearish too: the Iran-Oman corridor is technically finished — "
            "a corridor-first PARTIAL reopening returns barrels without any grand bargain the market is waiting "
            "for. A put spread owns both paths — demand rot and corridor supply — while the capped premium is all "
            "that is at risk if Hormuz produces the miscalculation instead. The spot longs and call spreads of "
            "the war regime are the wrong shape now; the put spread is the right one."
        ),
        "catalysts": [
            "EIA +17.4m bbl US crude build (Wed) — the demand crack printing in inventories",
            "IEA AND OPEC 2026 demand cuts in the same window (IEA: demand to FALL 1.6m b/d)",
            "The Iran-Oman corridor — technically agreed; a partial reopening is the unpriced middle path",
            "Risk catalyst: Araghchi's 'bigger miscalculation' — the spike path the spread's premium caps",
        ],
        "risks": (
            "A Hormuz miscalculation or Houthi escalation gaps Brent through $95 and the spread expires "
            "worthless — max loss is the premium, by construction; a fast grand-bargain reopening would pay the "
            "spread faster than the thesis needs. Defined risk; no stop required."
        ),
        "breakdown_why": {
            "gap":          "2/3 — Brent ~$88 prices a supply war that inventories and demand forecasts are "
                            "actively contradicting; the premium is stale against the flow data.",
            "catalyst":     "2/2 — the EIA build and the twin demand cuts are in-window and dated; the corridor "
                            "is a live second catalyst.",
            "positioning":  "1/2 — the crowd is long the war premium but has started trimming; one-sided but "
                            "less extreme than July.",
            "confirmation": "1/2 — six sessions of gains just cracked ~1-2%; the turn is one leg old.",
            "stop_quality": "1/1 — defined risk; the premium is the max loss.",
        },
    },
    "MM-2026-054": {
        "instrument": (
            "5s30s US Treasury curve steepener — long the 5Y (~4.35%), short the 30Y (~5.24%), spread ~+89bp. "
            "Pays when the 30Y cheapens vs the belly. The belly trades the Fed path; the 30Y trades supply, term "
            "premium, and the marginal buyer's balance sheet."
        ),
        "fundamental_thesis": (
            "Rotate the winner's logic out the curve. The 2s10s (MM-009) is 10bp from target with +232% banked — "
            "the normalisation from inversion is done. What is NOT done is the supply story, and it lives at the "
            "30-year point: the 10Y just TAILED its auction (4.683% vs 4.580%, b/c 2.53), $25B of 30Y paper "
            "prints TODAY, Treasury coupon supply is at records, Germany alone issues €82bn of 10Y bunds this "
            "year — and the AI buildout has turned the hyperscalers into record IG borrowers competing for the "
            "same duration dollar. The Pozsar mechanic made into a trade: the long end must fund the deficit AND "
            "the data centres, so the term premium is structurally under-supplied with buyers. The belly, "
            "meanwhile, is anchored by a Fed whose hike is fading. 5s30s at ~+89bp with a +130bp target owns the "
            "next leg of the same regime that paid the 2s10s."
        ),
        "catalysts": [
            "TODAY 1pm ET: the $25B 30Y auction — the public price of the term premium, one day after a 10Y tail",
            "Record Treasury coupon supply + record AI-capex IG issuance — the structural duration competition",
            "Sept hike fading (~40%) — anchors the belly while the long end floats",
            "Global long-end supply (Germany €82bn 10Y bund programme; every G10 hiker issuing) — the echo",
        ],
        "risks": (
            "A stellar 30Y auction (strong indirects, no tail) relieves the term-premium bid and flattens the "
            "spread; a genuine growth scare bull-flattens via the long end harder than the belly rallies. Stop: "
            "spread below +60bp; target +130bp."
        ),
        "breakdown_why": {
            "gap":          "2/3 — +89bp of 5s30s does not price a record dual-supply calendar against a fading "
                            "hike; late-cycle re-steepenings have run well past +130bp.",
            "catalyst":     "2/2 — the 30Y auction is TODAY and the 10Y tail already fired the signal.",
            "positioning":  "1/2 — curve steepeners are popular at 2s10s; the 5s30s expression is less crowded.",
            "confirmation": "2/2 — the tail, the record issuance run-rate, and 2s10s widening all confirm the "
                            "supply engine.",
            "stop_quality": "1/1 — +60bp is a clean structural floor; ~29bp of risk against ~41bp to target.",
        },
    },
    "MM-2026-055": {
        "instrument": (
            "Buy an EWY (iShares MSCI South Korea ETF) put spread — ~5%/15%-OTM, Oct expiry, defined-risk "
            "downside on the KOSPI complex. Max loss is the premium. The KOSPI re-entered a bull market today "
            "(+3.56%, 4th straight gain, ~+30% off the July low per local press) with Samsung +4.9% and SK Hynix "
            "+5.9% — while the won WEAKENED to ~1,421."
        ),
        "fundamental_thesis": (
            "Fade the religion swap, not the technology. Twenty sessions ago this index crashed 9% in a day on an "
            "analyst cutting SK Hynix's numbers; today it is back in a bull market on management talk of a memory "
            "shortage 'beyond 2030.' Same fabs, same capacity race, same demand assumption — opposite narrative. "
            "A market that repriced the same asset from glut to infinite shortage in a month is trading story, "
            "not supply, and the tell is the currency: the KOSPI surged INTO a weakening won — equity euphoria "
            "without FX endorsement is hedged hot money that leaves as fast as it came. With index vol cheap "
            "(VIX ~15) and the melt-up four sessions old into tonight's AMAT print and today's PPI, a defined-"
            "risk EWY put spread buys the convexity on the swing back at its cheapest. It is also the book's "
            "hedge: the Fable book is 30% Micron — the same narrative, one border over."
        ),
        "catalysts": [
            "KOSPI +3.56% into a WEAKER won (~1,421) — euphoria without FX endorsement, the outflow tell",
            "AMAT reports TONIGHT into a four-day melt-up — the margin risk Cisco just demonstrated",
            "TODAY'S PPI + 30Y auction — the macro taxes the froth pays first",
            "The 20-session glut-to-shortage narrative swap — sentiment, not supply, moved",
        ],
        "risks": (
            "The melt-up extends — memory pricing power is real, AMAT beats and guides up, and the spread decays; "
            "a US-Korea trade or supply headline squeezes the index further. Max loss is the premium — defined "
            "risk, sized as a hedge on the book's 30% Micron weight."
        ),
        "breakdown_why": {
            "gap":          "2/3 — a 30%-in-a-month rally on a narrative inversion, against a weakening won, is "
                            "sentiment outrunning verifiable supply data.",
            "catalyst":     "2/2 — AMAT tonight, PPI and the 30Y auction today; the froth meets three dated tests "
                            "inside 24 hours.",
            "positioning":  "2/2 — four straight up-days, a bull-market headline, retail momentum — the crowd is "
                            "maximally long the story at its top tick.",
            "confirmation": "0/2 — nothing has cracked yet; this is convexity bought BEFORE confirmation, priced "
                            "accordingly with defined risk.",
            "stop_quality": "1/1 — defined risk; the premium is the max loss.",
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
    {"name": "KOSPI", "level": f"~{KOSPI_LVL:,.0f}", "chg": "+3.56%", "dir": "up"},
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
    _row("WTI Crude",   "wti",    _usd, force_dir="down"),
    _row("Brent Crude", "brent",  _usd, force_dir="down"),
    _row("Gold (XAU)",  "gold",   _gold),
    _row("VIX",         "vix",    lambda v: f"{v:.2f}"),
    {"name": "SOFR", "level": "~3.63%", "chg": "", "dir": "flat"},   # NY Fed / FRED-consistent, Aug 10
    {"name": "BTC", "level": "~$63.5k", "chg": "range-bound", "dir": "flat"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.63%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Mon 10 Aug · NY Fed"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    {"name": "US 5Y", "level": f"{US05Y_LVL:.2f}%", "chg": "belly anchored", "dir": "flat"},
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    {"name": "5s30s", "level": f'{(_g("us30y")-US05Y_LVL)*100:+.0f}bp' if _g("us30y") else "—",
     "chg": "the next leg", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
]

# Per-trade open-book notes (shown in the "yesterday, graded" table).
NOTES = {
    "MM-2026-001": "STALE. ~1.635 (+0.6%) — green on no thesis of ours: the ECB is now HIKING (Sept ~fully priced), "
                   "which supports EUR, while the melt-up bids the AUD. Both live forces point against the 1.61 "
                   "target. Tight leash: stop 1.662, trim toward 1.645.",
    "MM-2026-009": "THE CHAMPION, 10bp FROM TARGET. 2s10s ~+50bp, +232% from the +15bp entry. The window proved the "
                   "engine: a cool CPI rallied the FRONT (hike odds ~40%) while the 10Y TAILED its $42B auction at "
                   "4.683% — the front trades the Fed, the back trades the flood. $25B of 30Y prints today. Trail "
                   "the stop, take +60bp if it prints, rotate the logic into 5s30s (MM-054).",
    "MM-2026-012": "GREEN ON BORROWED THESIS. ~1.153 (+0.6%), stop 1.182 distant — but the engine flipped: the ECB "
                   "hikes September (~fully priced) while the Fed's hike faded to ~40%. The haven dollar and the "
                   "$88-oil drag on the euro are what's left. Hold while it pays; trim on a 1.16 reclaim; do NOT add.",
    "MM-2026-013": "THE FADE GOT ITS CATALYST — AND OWES US THE MOVE. 2Y ~4.17% vs 4.162 entry (~flat) after the "
                   "cool CPI cut Sept hike odds to ~40% (from ~82% late July, broken by the Aug 7 jobs miss). "
                   "Today's PPI is the decider: cool pays the fade toward 4.05%; hot backs it toward the 4.35% stop.",
}

# Notes for the closed ledger (keyed by id; falls back to the exit reason).
CLOSED_NOTES = {
    "MM-2026-006": ("STOPPED June 8. Q2 beat but the Q3 AI guide ($16.0B vs buy-side $17.2B) missed the number that "
                    "mattered at 41x; payrolls finished it."),
    "MM-2026-002": ("The US-Iran MoU removed the re-escalation premium the long was built on. Brent broke the $87 "
                    "weekly-close exit and the $84 stop. Surrendered by design, not by surprise."),
    "MM-2026-011": ("Peace deflated the Hormuz tail the call spread owned. Closed near the $1 discipline level to "
                    "recover residual premium."),
    "MM-2026-010": ("STOPPED on the melt-up Jun 16: the relief rally re-rated US tech faster than European "
                    "financials and broke the 0.943 ratio stop."),
    "MM-2026-003": ("STOPPED June 10. The Brent-WTI spread compressed as the Hormuz premium drained out of the "
                    "Atlantic-basin grade faster than Cushing. Defined spread risk; the stop did its job."),
    "MM-2026-008": ("BANKED Jun 27 at ~$45 (~+29%, peak +71%). The FOMC-tail hedge did its job; harvested rather "
                    "than bled to zero."),
    "MM-2026-005": ("STOPPED Jul 15 at ~$4,000 (-10.9%) in the toll regime, when a bigger war meant higher real "
                    "yields and gold traded as a real-rates short. The coda is the lesson: gold trades $4,400 a "
                    "month later, once the HIKE faded — the thesis was right, the regime was wrong, and the stop "
                    "plus the min-hold did exactly their job."),
    "MM-2026-007": ("STOPPED Jul 22 at 163 — the oil-importing yen was the war's funder, not its haven. The regime "
                    "that would have saved it (a government-backed faster BoJ hike) arrived three weeks later; "
                    "re-entered Aug 13 on the NEW data as MM-052."),
    "MM-2026-004": ("STOPPED Jul 23 at ~4.65%. Duration never got its haven bid — supply and the war premium kept "
                    "the long end heavy through everything. The lesson became the book's best trade: own the curve "
                    "(MM-009, then MM-054), never outright long-end duration in a dual-supply regime."),
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
    {"datum": f"KOSPI {KOSPI_LVL:,.2f} (+3.56%, 4th straight gain — re-entered a bull market; Samsung +4.89%, SK "
              f"Hynix +5.91%); USD/KRW ~{USDKRW_LVL:,.0f} (won WEAKER into the equity surge); SOX {SOX_LVL:,.0f} "
              f"(+2.5% Wed); US 5Y {US05Y_LVL:.2f}%.",
     "source": "TradingView (live) + CNBC + Korea JoongAng Daily (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "US PRE-MARKET Thu Aug 13 into July PPI (08:30 ET, cons +0.2% m/m), jobless claims, and the $25B 30Y "
              "auction (1pm ET) — ALL PENDING. Applied Materials reports TONIGHT AMC (PENDING). Brief covers the "
              "Wed Aug 12 US session (in-line CPI, AI melt-up, tailed 10Y auction) and the Thu Asia/Europe sessions.",
     "source": "BLS + Treasury/Newsquawk + AMAT IR calendars", "asof": TODAY, "stale": False},
    {"datum": "July CPI (Wed Aug 12): headline +0.1% m/m / 3.4% y/y (from 3.5%); core +0.2% m/m / 2.5% y/y — "
              "slowest core since 2021; all four readings in line with consensus. September HIKE odds fell to ~40% "
              "from ~50% (had been ~82% late July before the Aug 7 jobs miss).",
     "source": "CNBC + Babypips + Kalshi/CME-derived (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "10Y AUCTION TAILED (Wed): $42B, high yield 4.683% vs 4.580% prior, bid-to-cover 2.53 vs 2.59; "
              "indirects 76.7%. 10Y ended ~4.69% after a post-CPI dip; ~4.67% this morning. Refunding week "
              "concludes with $25B 30Y today.",
     "source": "Treasury results via BigGo/louisvelazquez (secondary, figures agree) + CNBC", "asof": TODAY, "stale": False},
    {"datum": "AI MELT-UP (Wed): Super Micro +19%, CoreWeave +19% (Q2 rev $2.58B, +112% y/y), Lumentum +14%, "
              "Nebius +34%. AFTER HOURS: Cisco beat a record FQ4 ($17.3B rev +18%, EPS $1.22) and FELL ~4.6% on "
              "gross-margin mix; Cerebras beat on revenue (core +103% y/y) and sank.",
     "source": "CNBC + Motley Fool + Investing.com (corroborated; AH moves indicative)", "asof": TODAY, "stale": False},
    {"datum": "HORMUZ (Aug 12-13): Trump on Truth Social: 'The U.S.A. has total control over the Strait of Hormuz. "
              "I THINK WE WILL KEEP IT!' Iran says the strait 'remains blocked'; FM Araghchi warns of 'an even "
              "bigger miscalculation.' Houthi double-tap on the Tihamah (Aug 11) killed 6 — first deadly attack on "
              "shipping since Feb. Talks deadlocked; Iran-Oman corridor agreed but NOT opened.",
     "source": "ABC + CNN + Al Jazeera + NBC/Semafor (corroborated; Araghchi single-sourced)", "asof": TODAY, "stale": False},
    {"datum": "OIL FELL ANYWAY: Brent ~$87.9 (-1.2%), WTI ~$82. EIA weekly: +17.4m bbl US crude build. IEA and "
              "OPEC BOTH cut 2026 demand — IEA now sees demand FALLING 1.6m b/d in 2026 on high prices + "
              "disruption; EIA STEO has Brent averaging ~$87 in 2026.",
     "source": "CNBC (IEA) + OilPrice + OGJ/EIA (corroborated; EIA build figure single-sourced)", "asof": TODAY, "stale": False},
    {"datum": "JAPAN: Bloomberg — Japan's government said to SUPPORT a faster BoJ hike (Sept or Oct); July PPI "
              "+7.2% y/y; BoJ at 1.00%, 3 of 9 board members argue for a faster pace (July Summary of Opinions); "
              "USDJPY ~159.4 after the Aug 1 joint US-Japan intervention (~164 defended; first since 1998; "
              "Bessent: 'countered disorderly yen movements').",
     "source": "Bloomberg (scoop, single-sourced) + CNBC + Al Jazeera + Fortune (intervention corroborated)", "asof": TODAY, "stale": False},
    {"datum": "EUROPE/UK: ECB hiked in June (depo 2.25%, first in 3 years), September ~fully priced; Stoxx 600 "
              "+0.2% this morning with BANKS +1.2%, basic resources -2.9%; UK GDP +0.3% m/m June (cons -0.1%), Q2 "
              "+0.4%; gilt 10Y ~4.97% (live); BoE hikes priced by December. Maersk +4.6% (raised guidance on war "
              "freight rates), Adyen +12% (raised guidance).",
     "source": "Reuters + Bloomberg + CNBC/Euronews + ONS (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "FED POLITICS: Warsh chairs (since May 22); Bloomberg (Aug 10): Trump periodically phones Warsh "
              "pressing for cuts. Trump Media sued (Aug 12) over the $1.2M/yr 'Truth API' selling early access to "
              "Trump's posts — pitched at Wall Street traders.",
     "source": "Bloomberg + NPR + AP (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Credit: HY OAS ~270-280bp (richest decile of history; long-run median ~450bp); IG issuance at a "
              "record 2026 pace on AI-capex borrowing (Alphabet, Amazon, Meta among leading borrowers); Monday saw "
              "19 IG issuers, the most since January.",
     "source": "FRED/BAML via Convex + Bloomberg + Schwab (corroborated in direction; OAS to-the-bp unverified)", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.63% — no funding stress through CPI week or the auction tail.", "source": "NY Fed / FRED-consistent (Aug 10)", "asof": "2026-08-10", "stale": True},
]

# ── Earnings intelligence ───────────────────────────────────────────────────────
# Feed: earnings_data.md (Finnhub, generated 2026-08-13 06:00 UTC). Universe filter applied by the feed
# (>$10bn, US+Korea, Tech/Financials/Industrials/Utilities). Short interest = unavailable -> positioning
# pillar "estimated". Three ideas rendered (AMAT pre; CSCO + SMCI post); the rest of the feed noted, not padded.
earnings_ideas = [
    {
        "ticker": "AMAT", "company": "Applied Materials", "report_date": "2026-08-13", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Long", "conviction_score": 5, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced", "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Consensus ~$3.45 EPS on ~$9.2B revenue (Finnhub); four straight beats, all modest (+1.6% to +5.9%).",
            "39 buy / 6 hold / 0 sell — the strongest consensus support in the feed; the WFE bellwether.",
            "Reports TONIGHT into a four-day AI melt-up (SOX +2.5% Wed, KOSPI +3.56% today) — good news is "
            "largely pre-paid; the margin line is the live risk after Cisco's record-quarter-but-margin-miss.",
        ],
        "what_moves_it": ("China revenue mix and the gross-margin line more than the headline beat — Cisco just "
                          "showed a record AI quarter can sell off ~4.6% on hardware-margin mix; a modest-beat "
                          "serial like AMAT into a hot tape has the same asymmetry."),
        "client_talking_point": ("AMAT is the equipment bellwether reporting into a tape that already believes — "
                                 "a 4-quarter beat streak of ~5% is pre-paid at these levels, so the print is a "
                                 "margin-and-China test, not an EPS test. Own it with defined risk if at all; the "
                                 "cleaner trade is the cohort's froth, not the bellwether's print."),
    },
    {
        "ticker": "CSCO", "company": "Cisco Systems", "report_date": "2026-08-12", "report_timing": "AMC",
        "mode": "POST-EARNINGS", "direction": "Long", "conviction_score": 6, "conviction_label": "High — data gap flagged",
        "conviction_rationale": ("A record quarter — $17.3B revenue +18% y/y, EPS $1.22 vs $1.19, FY27 guided "
                                 "~+15% with quarterly AI orders above $4B vs $3.7B guided — sold off ~4.6% after "
                                 "hours purely on gross-margin mix; a mix-driven margin dip on surging hardware "
                                 "demand is the kind of print that re-rates back once the tape re-reads it."),
        "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced", "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Actual EPS $1.22 vs $1.19 consensus (+2.2% surprise, Finnhub-consistent); revenue $17.3B, +18% y/y — a record.",
            "FY27 guide $72.2-73.4B (~+15% mid); AI orders >$4B in the quarter vs $3.7B guided.",
            "Stock +2.9% in the regular session, then ~-4.6% after hours on gross-margin mix (options had priced ~8%).",
        ],
        "reaction_tag": "OVERSOLD",
        "eps_actual": 1.22, "eps_estimate": 1.1937, "eps_surprise_pct": 2.2, "stock_reaction_pct": -4.6,
        "implied_upside_to_pt": None,
        "what_moves_it": ("Whether the market re-reads the margin dip as mix (bullish — it means hardware demand "
                          "is surging) or as structural AI-era margin compression (bearish); 23 buy / 10 hold with "
                          "no sells says the sell-side will defend it."),
        "client_talking_point": ("Cisco grew 18% — its best in years — raised the AI numbers, and fell 4.6% on the "
                                 "margin optics of its own success. For a cash-flow tech name at a non-AI multiple, "
                                 "a mix-driven dip is an entry, not a warning; the AI-margin question is real but "
                                 "it is priced at 40x in the leaders, not at Cisco's multiple."),
    },
    {
        "ticker": "SMCI", "company": "Super Micro Computer", "report_date": "2026-08-11", "report_timing": "AMC",
        "mode": "POST-EARNINGS", "direction": "Short", "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 0, "catalyst": 2, "positioning": 0},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced", "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Surged +19% Wednesday on a guidance beat — but the sell-side is NOT behind it: 10 buy / 13 hold / 4 "
            "sell, the weakest consensus split in the feed.",
            "Surprise history is violent in both directions (+74%, +32%, +39%, -15% the last four quarters) — a "
            "structurally low-visibility model being priced like a compounder.",
            "The +19% pop is the froth edge of the melt-up: an assembler with commodity margins re-rating on the "
            "cohort's narrative, into tonight's AMAT print and today's PPI.",
        ],
        "reaction_tag": "OVERBOUGHT",
        "eps_actual": None, "eps_estimate": 0.9767, "eps_surprise_pct": None, "stock_reaction_pct": 19.0,
        "implied_upside_to_pt": None,
        "what_moves_it": ("Any wobble in the AI-infra tape — a margin headline (Cisco just supplied one), an AMAT "
                          "guide-down, or a macro tax (PPI/30Y auction) — hits the lowest-conviction, "
                          "highest-beta name in the cohort first."),
        "client_talking_point": ("Not a name to own after a +19% guidance pop that the covering analysts "
                                 "themselves won't endorse — more holds and sells than buys. If you want the AI "
                                 "buildout, own it through the leaders or the equipment layer; fading this pop "
                                 "with defined risk is the higher-quality expression."),
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
        "DEMAND DOES THE DIPLOMACY. Wednesday's July CPI printed in line (headline +0.1% m/m / 3.4% y/y; core "
        "+0.2% / 2.5% — slowest core since 2021) and buried the September hike (~40% from ~50%; ~82% late July). "
        "The AI trade roared back: Super Micro +19%, CoreWeave +19% (+112% revenue), Lumentum +14%; the KOSPI "
        "surged +3.56% back into a BULL MARKET (Samsung +4.9%, SK Hynix +5.9%), the Topix closed at a record. Two "
        "markets refused to ratify it: the 10Y TAILED its $42B auction (4.683% vs 4.580%, b/c 2.53) with $25B of "
        "30Y printing TODAY — and oil FELL with the strait still SHUT (Trump: 'total control'; Iran: 'remains "
        "blocked'; a Houthi strike killed 6) because the EIA printed a +17.4m bbl build and the IEA/OPEC both cut "
        "2026 demand (IEA: -1.6m b/d). Meanwhile every central bank but the Fed is hiking: ECB September ~fully "
        "priced, BoE by December, and Bloomberg reports Japan's government now BACKS a faster BoJ hike (PPI 7.2%) "
        "behind the first joint US-Japan yen intervention since 1998. Cisco's record quarter fell 4.6% after "
        "hours on margin mix; Cerebras beat and sank; AMAT reports TONIGHT into July PPI + the 30Y auction TODAY "
        "(all PENDING). The book: the 2s10s steepener is +232%, ten basis points from target — trail it. Fresh "
        "ideas press the NEW information: short USD/JPY (MM-052), a Brent put spread (MM-053), a 5s30s steepener "
        "(MM-054), and an EWY put spread fading Korea's 20-session religion swap (MM-055)."
    ),

    "summary_narrative": """
<p>The first full brief since July 14 opens on a market that swapped religions while the narrative was away. The
last chapter closed with Korea's chips crashing 9% on a glut downgrade and a September hike priced at two-in-three;
this one opens with the KOSPI back in a <strong>bull market</strong> &mdash; +3.56% today, a fourth straight gain,
Samsung +4.9%, SK Hynix +5.9% &mdash; and the hike buried at ~40% after Wednesday's July CPI printed exactly in
line: headline +0.1% on the month, 3.4% on the year, core +0.2% and 2.5%, the slowest core since 2021. The AI
complex answered like a spring uncoiling: Super Micro +19%, CoreWeave +19% on 112% revenue growth, Lumentum +14%,
the Topix at a record on a seventh straight gain. (CNBC, Motley Fool, Korea JoongAng Daily.)</p>

<p>Two markets refused to ratify the party, and they are the story. The first is the long end: the same day the
front end rallied on the cool print, the Treasury's $42B 10-year auction <strong>tailed</strong> &mdash; a 4.683%
stop against 4.580% last month, bid-to-cover 2.53 &mdash; and $25B of 30-year paper prints at 1pm today, an hour
class after a PPI print at 08:30. The front end trades the Fed; the back end trades the flood &mdash; record
Treasury coupon supply meeting record AI-capex IG issuance from the hyperscalers, both asking the same duration
buyer for balance sheet. That is why the book's 2s10s steepener sits at ~+50bp, +232%, ten basis points from
target. (Newsquawk, CNBC, Bloomberg.)</p>

<p>The second dissenter is the barrel. The Strait of Hormuz is still shut &mdash; Trump posted that America has
&lsquo;total control&rsquo; of the strait and will keep it, Iran answered that it &lsquo;remains blocked,&rsquo;
Araghchi warned of &lsquo;an even bigger miscalculation,&rsquo; and a Houthi double-tap killed six sailors on the
Tihamah &mdash; and Brent FELL ~1.2% to ~$87.9 anyway, because the EIA printed a +17.4 million barrel US crude
build and both the IEA and OPEC cut 2026 demand, the IEA now expecting demand to <strong>fall</strong> 1.6m b/d
this year. Demand destruction is doing the diplomacy: the cure for $90 oil is $90 oil. (ABC, Al Jazeera, CNBC,
OilPrice.)</p>

<p>And the policy map has inverted since the last chapter: every major central bank but the Fed is now hiking.
The ECB's September hike is ~fully priced; the BoE is priced to hike by December; and Bloomberg reports Japan's
government now <strong>backs</strong> a faster BoJ hike &mdash; September or October &mdash; with wholesale
inflation at 7.2% and the yen defended at ~164 by the first joint US-Japan intervention since 1998. September is
a three-central-bank hike window in which the Fed &mdash; whose chair is being phoned by the President pressing
for cuts &mdash; is the least likely hiker. (Bloomberg, CNBC, Fortune.)</p>

<p>The book carries the scar tissue and the winner into this chapter. The July stops took gold at $4,000 (it
trades $4,400 today &mdash; right thesis, wrong regime), the yen short at 163 (the regime that saves it arrived
three weeks late &mdash; re-entered today on the new data), and the 10Y short (duration never got its haven bid).
The steepener is ten basis points from the finish line. The posture: trail the champion, rotate its logic out the
curve (5s30s), re-enter the yen from the BoJ's side, own oil's demand crack with defined risk, and fade Korea's
twenty-session religion swap with a put spread while vol is cheap.</p>
""",

    "takeaways": [
        "<strong>The cool core buried the September hike.</strong> July CPI in line across the board (3.4% "
        "headline, 2.5% core y/y &mdash; slowest core since 2021); September hike odds ~40%, from ~50% pre-print "
        "and ~82% in late July before the jobs miss. The two-print week concludes TODAY with PPI at 08:30 ET "
        "(cons +0.2% m/m) &mdash; a hot print flips the hike back on within 24 hours. (CNBC, Babypips, Kalshi.)",

        "<strong>The AI trade roared back from its own crash.</strong> Super Micro +19%, CoreWeave +19% (+112% "
        "revenue), Lumentum +14%, Nebius +34%; the KOSPI re-entered a BULL MARKET (+3.56%, Samsung +4.9%, SK "
        "Hynix +5.9%), the Topix closed at a record. Twenty sessions ago this complex was crashing on a glut "
        "downgrade &mdash; same fabs, opposite religion. (CNBC, Korea JoongAng Daily.)",

        "<strong>The long end refused to ratify it.</strong> The $42B 10Y auction TAILED at 4.683% (vs 4.580% "
        "prior, b/c 2.53) the same day the front end rallied; $25B of 30Y prints at 1pm TODAY. Record Treasury "
        "supply + record AI-capex IG issuance = the term-premium machine. The 2s10s steepener (MM-009) is +232%, "
        "10bp from target; the fresh expression rotates to 5s30s (MM-054). (Newsquawk, Bloomberg.)",

        "<strong>Oil fell with the strait still shut &mdash; demand is doing the diplomacy.</strong> Trump: "
        "'total control' of Hormuz; Iran: 'remains blocked'; Araghchi: 'an even bigger miscalculation'; a Houthi "
        "strike killed 6. Brent still FELL to ~$87.9: EIA +17.4m bbl build, IEA and OPEC both cut 2026 demand "
        "(IEA: -1.6m b/d). Own the crack with a defined-risk Brent put spread (MM-053). (ABC, Al Jazeera, CNBC.)",

        "<strong>Everyone is hiking except the Fed.</strong> ECB September ~fully priced (June hike done); BoE "
        "priced by December; Bloomberg: Japan's government now BACKS a faster BoJ hike (Sept/Oct) with PPI at "
        "7.2% and the yen defended by the first joint US-Japan intervention since 1998. The yen re-entry (short "
        "USD/JPY, MM-052) owns the only differential compressing from both sides. (Bloomberg, CNBC, Fortune.)",

        "<strong>The margin tell: Cisco's record quarter fell 4.6%.</strong> $17.3B revenue +18%, EPS $1.22, "
        "raised AI targets &mdash; and sold off after hours on gross-margin mix. Cerebras beat on revenue and "
        "sank. The AI boom is starting to tax its own suppliers' margins; AMAT reports TONIGHT into a four-day "
        "melt-up. (Investing.com, CNBC.)",

        "<strong>The book: harvest the champion, press the new information.</strong> The 2s10s steepener is 10bp "
        "from its +60bp target &mdash; trail, don't press. Fresh ideas: short USD/JPY (MM-052), Brent $85/$75 "
        "put spread (MM-053), 5s30s steepener (MM-054), EWY put spread on Korea's froth (MM-055). The EUR/USD "
        "short survives on a tight leash &mdash; the ECB's hike has flipped its engine.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "30%",
         "headline": "Cool PPI + a clean 30Y auction — the hike dies, the melt-up broadens",
         "body": "PPI prints at or below +0.2%, the 30Y auction stops through, and the two-print week ends with "
                 "the September hike effectively off the table. The front end rallies hard (MM-013 finally pays "
                 "toward 4.05%), the melt-up broadens beyond AI, gold extends through $4,400, and the yen "
                 "strengthens as the differential compresses (MM-052 pays). The curve bull-steepens more gently "
                 "(MM-009 reaches target and is banked; MM-054 grinds). The froth fades (MM-055) decay — that is "
                 "what their defined risk is for. Risk up · front-end yields down · dollar soft · gold up · oil "
                 "soft on demand."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "In-line data, heavy supply — the front anchors, the long end floats, the froth churns",
         "body": "PPI lands near consensus, the 30Y auction is sloppy-but-absorbed (a small tail), and the tape "
                 "keeps both stories: hike odds pinned ~35-45%, the melt-up churns higher with rotation and "
                 "margin-tax casualties (Cisco-style), oil ranges $85-90 as the war premium and the demand rot "
                 "cancel. The steepeners grind (MM-009 tags +60bp and is banked; MM-054 widens toward +100bp), "
                 "the yen firms slowly on BoJ drumbeat (MM-052), Korea churns (MM-055 optionality lives), and "
                 "the EUR short bleeds toward its 1.16 trim line. Risk mixed · curve steeper · dollar mixed · "
                 "oil ranging."},
        {"kind": "bear", "label": "Bear", "pct": "25%",
         "headline": "A hot PPI or a Hormuz miscalculation — the hike revives into a crowded melt-up at VIX 15",
         "body": "Either PPI prints hot (+0.4%+) and the September hike re-arms within 24 hours of the cool CPI "
                 "— backing the 2Y toward MM-013's 4.35% stop, bear-flattening the front, and taxing a four-day "
                 "AI melt-up priced at VIX ~15 — or Araghchi's 'bigger miscalculation' happens and oil gaps "
                 "through $95, re-arming the energy-inflation loop with the Houthis already killing sailors. "
                 "Either way the froth pays first (MM-055 fires, SMCI-type pops unwind), the 30Y auction tails "
                 "badly (MM-054 pays), the dollar bids (MM-012 vindicated), and the Warsh-vs-Trump rupture goes "
                 "public. Risk down · long-end yields up · dollar bid · oil two-way · vol up hard."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a divergence inside the good news: the disinflation the market celebrated
on Wednesday was ratified by the front end of the curve and rejected by the back. July CPI printed exactly in
line — 3.4% headline, a 2.5% core that is the slowest since 2021 — and the September hike faded to ~40%. The
same afternoon, the Treasury's $42B 10-year auction tailed by more than ten basis points against last month's
stop, and today the government asks the market to absorb $25B of 30-year bonds an hour after a PPI print. A tape
that rallies the 2-year and tails the 10-year auction on the same day is telling you the constraint is no longer
the Fed — it is the supply. The non-consensus read: the binding price in this market is the term premium, and it
is being set by an auction calendar, not a dot plot.</p>

<p>The counter-intuitive hook is the barrel. Every headline out of the Gulf in the window was bearish for peace —
Trump claiming 'total control' of a strait Iran says 'remains blocked,' the foreign minister threatening 'an even
bigger miscalculation,' six sailors killed by Houthi missiles — and oil FELL. The resolution is that the demand
side broke first: a 17.4 million barrel US crude build, and the IEA and OPEC cutting 2026 demand in the same
window, the IEA now expecting demand to fall 1.6m b/d this year. Six months of war premium has done what the
diplomats could not — rationed demand. A barrel that falls while the war stands still is a demand signal wearing
a peace costume, and the trade is to own the crack with defined risk (MM-053), not to celebrate the de-escalation
that has not happened.</p>

<p>Now the gap between real economy, what is priced, and the narrative. <strong>Real economy:</strong> core
inflation at 2.5% and slowing, a labour market that missed big in July, wholesale inflation in Japan at 7.2%,
oil demand falling, and an AI capex machine whose funding needs are now visible in record IG issuance.
<strong>What is priced:</strong> a ~40% September hike, VIX ~15, the S&amp;P within a tenth of its record, a
KOSPI up ~30% in a month, HY spreads in their richest decile. <strong>The narrative:</strong> 'the hike is dead,
the AI shortage runs beyond 2030, buy the melt-up.' The gap — and the alpha — is that the long end and the
barrel are pricing the constraints the equity narrative ignores: term premium and demand destruction.</p>

<p>Go around the world. <strong>US:</strong> pre-market flat-to-firm into PPI, claims, the 30Y auction and AMAT
tonight — four dated tests of the melt-up inside 24 hours. <strong>Asia:</strong> the KOSPI's bull-market
re-entry (+3.56%) came with a WEAKER won (~1,421) — euphoria without FX endorsement is hedged hot money; the
Topix's record run now has the government publicly backing a faster BoJ hike; China's onshore tape is quiet with
July credit data due by ~Aug 15 and forecast dismal (new loans ~45bn yuan vs 1.61trn in June). <strong>Europe:
</strong> the hikers' bloc — banks +1.2% this morning as the ECB's September hike sits fully priced; the UK grew
+0.3% in June against a forecast contraction and gilts still trade near 5% because the BoE is priced to hike.
<strong>Middle East:</strong> deadlocked, with the Houthis escalating and the Iran-Oman corridor agreed but
unopened — the unpriced middle path in both directions.</p>

<p>The political layer runs on one inversion. The consensus Fed-independence fear — Trump captures the Fed and
cuts — has it backwards: Trump already has his chair, Bloomberg reports he phones Warsh pressing for cuts, and
Warsh's own market is debating a HIKE into a midterm year while the White House is sued over a $1.2M-a-year
'Truth API' selling Wall Street early access to the very posts that move oil. The Papic constraint: Warsh cannot
cut without confirming capture, and cannot hike without open war with the White House — so he holds, which pins
the front end and hands the whole adjustment to the long end. That is the same steepener regime the book has been
paid for all summer, now with a political engine underneath it.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the term premium into a record dual-supply calendar (5s30s,
MM-054); a government-backed BoJ hiking cycle (short USD/JPY, MM-052); oil's demand crack and the corridor-first
partial reopening (MM-053). <strong>Fairly priced:</strong> the steepener's normalisation leg (MM-009 — 10bp
from target, harvest); the September Fed hold. <strong>Over-priced:</strong> Korea's shortage-forever re-rating
(+30% in a month into a weakening won — MM-055); the melt-up's low vol (VIX ~15 into four dated catalysts);
HY spreads in the richest decile of history with the up-in-quality swap nearly free.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is that the market's two best pieces of news are
taxing each other. The disinflation that buried the September hike is the same force that un-anchors the long
end — because a Fed that neither hikes nor cuts hands the entire adjustment to supply, and supply is what the
long end has too much of. Wednesday made the mechanism public: the front end rallied on a 2.5% core while the
Treasury's ten-year auction tailed by a dime, and today the sequence runs PPI at eight-thirty, thirty-year
auction at one, Applied Materials after the close — the melt-up's bill, presented in three instalments.</p>

<p>Decompose the melt-up itself, because the anatomy is narrower than the headline. The S&amp;P sits a tenth of
a percent from its record, but the engine is one cohort — the AI-infrastructure complex — re-rating on the same
religion that crashed it in July. Twenty sessions ago the KOSPI fell nine percent in a day because one analyst
cut SK Hynix's numbers; today the same index is back in a bull market on management talk of a shortage running
'beyond 2030,' and the won weakened into the surge. Same fabs, same capacity race, same demand assumption —
opposite story, and the currency refusing to endorse it. Cisco supplied the second tell: a record quarter, +18%
revenue, raised AI targets — and a 4.6% after-hours drop on gross-margin mix, because the boom is beginning to
tax its own suppliers. So what, who is wrong, what is the trade: the crowd is paying record multiples for a
narrative that inverted once already this summer, and the cheap side of the tape is the defined-risk fade of its
frothiest edge — Korea — not the index.</p>

<p>Trace the rates story to a flow and it stops being about inflation at all. The hyperscalers are now record
investment-grade borrowers — Alphabet, Amazon and Meta among the year's largest issuers, nineteen IG deals on
Monday alone, the heaviest day since January — while the Treasury runs a record coupon calendar into the same
buyers. The AI buildout has become a bond-supply machine: the long end is being asked to fund the deficit and
the data centres simultaneously, which is why a friendly CPI could not stop a ten-year tail, and why the
thirty-year auction at one o'clock matters more than the PPI at eight-thirty. The Pozsar mechanic in one line:
term premium is the funding constraint of the AI trade, and it is priced at auction, in public, twice this week.
Own the curve — the 2s10s ten basis points from target, the 5s30s as the fresh leg — and never outright
long-end duration in a dual-supply regime.</p>

<p>The barrel is the quiet confirmation of the whole framework. Oil fell one percent through a window in which
the strait stayed shut, the foreign minister of Iran threatened miscalculation and the Houthis killed six
sailors — because inventories built seventeen million barrels and both agencies cut demand. Demand destruction
is doing the diplomacy. That is not a peace dividend; it is the war's own price rationing its way to a lower
equilibrium, and it converts every future Hormuz headline from a trend-changer into a spike-risk — exactly the
shape a put spread owns and a spot position cannot. The same logic re-arms the yen: for the first time in the
cycle the US-Japan rate differential is compressing from both sides — a government-backed BoJ hiking into a
fading Fed hike — with the first joint intervention since 1998 standing above the market as an official ceiling.
The book re-enters the yen short-dollar today not because the last attempt worked — it was stopped at 163 —
but because the data that stopped it has inverted.</p>

<p>So the posture is harvest and rotate, not press and hope. The steepener that carried the book all summer is
ten basis points from its target and gets trailed, not added to. The fresh risk goes where the last twenty-four
hours actually moved the facts: the 5s30s for the supply the disinflation cannot fix, the yen for the only
differential compressing from both ends, the Brent put spread for the demand crack wearing a peace costume, and
the Korea put spread for the crowd that changed religions in twenty sessions and calls it conviction. The tape
is celebrating the death of a hike. The bill for the celebration prints at one o'clock.</p>
""",

    "correlation_regime": """
<p><strong>1. Oil decoupled from geopolitics — the demand signal wearing a peace costume.</strong> The strait is
shut, the Houthis are killing sailors, Araghchi threatens 'an even bigger miscalculation' — and Brent FELL to
~$87.9 on a +17.4m bbl build and twin agency demand cuts (IEA: -1.6m b/d in 2026). The war premium is being
overwhelmed by demand rot, not by peace. The break is the trade: own the downside with a defined-risk put spread
(MM-053) that caps the ever-present spike risk instead of fighting it.</p>

<p><strong>2. The front end decoupled from the long end — the auction beat the CPI.</strong> A cool core rallied
the 2Y and cut hike odds to ~40%, and the SAME DAY the 10Y tailed its auction at 4.683%. The front trades the
Fed; the back trades a record dual-supply calendar (Treasury coupons + AI-capex IG issuance). That split IS the
steepener regime: MM-009 at +50bp/+232% (harvest), MM-054 (5s30s, ~+89bp) as the fresh leg with the 30Y auction
pricing the term premium at 1pm today.</p>

<p><strong>3. The KOSPI decoupled from the won — euphoria without FX endorsement.</strong> Korea's equity index
surged +3.56% into a bull market while its currency WEAKENED to ~1,421 and India's RBI defended a record-weak
rupee. Foreign money is buying the story hedged — hot money that leaves as fast as it came. Equity strength the
FX market refuses to fund is the classic froth tell; MM-055 (EWY put spread) owns the seam with defined risk.</p>

<p><strong>4. Record revenue decoupled from the stock price — the margin tax arrives.</strong> Cisco grew 18% to
a record, raised AI targets, and fell ~4.6% after hours on gross-margin mix; Cerebras beat on revenue and sank.
For the first time this cycle, the AI tape is punishing the P&amp;L shape of its own boom — hardware mix
compressing margins even as orders surge. The read-through is tonight's AMAT print and the whole
picks-and-shovels layer: the boom's next casualty list is drawn from its own suppliers.</p>
""",

    "vol_skew": """
<p><strong>Vol is priced for the party, not the bill — and the bill has four due dates inside 24 hours.</strong>
US equity vol sits ~15 (VIX ~14.6-15.4 across the window) with the S&amp;P a tenth of a percent from its record —
into TODAY'S July PPI (the second print of the two-print week), a $25B 30Y auction one day after the 10Y tailed,
jobless claims, and AMAT after the close. Rates vol has the live event (the auction), yet the term structure is
only gently kinked (est. VIX9D ~14 · VIX ~14.6 · VIX3M ~16.5 · VIX6M ~17.5, estimates flagged). Crypto vol
confirms the complacency from the other side: bitcoin 30-day implied at its lowest since September with puts
still over calls — the speculative tail refusing to confirm the melt-up. The cheap convexity is where the froth
is loudest and the catalysts are dated: the EWY put spread (MM-055) on a KOSPI up ~30% in a month into a
weakening won, and the Brent $85/$75 put spread (MM-053) where implied still carries war premium while the
demand data rots underneath it. The expensive mistake would be chasing index puts at a record high into in-line
data — the July lesson (put spreads bleeding through a melt-up) stands. Own dated, defined-risk convexity at the
edges; let the index carry itself.</p>
""",

    "sector_rv": """
<p><strong>Leading (Wed US / Thu Asia-Europe):</strong> AI infrastructure and neoclouds (SMCI/CRWV +19%, LITE
+14%, SOX +2.5%); Korea (+3.56%, bull-market re-entry) and Japan (Topix record, 7th straight gain); European
BANKS (+1.2% this morning — the hikers' cohort, ECB September ~fully priced); industrials led the US session.
<strong>Lagging:</strong> energy (Brent -1.2% on the demand cuts; Europe's energy -0.7%); basic resources
(-2.9% Europe); duration-sensitive defensives into the tailed auction; Cisco (-4.6% AH on margin mix) as the
first margin-tax casualty. <strong>This week:</strong> PPI + claims + the $25B 30Y auction TODAY; AMAT tonight;
China July credit data by ~Aug 15; KEYS + JKHY Tue Aug 18 AMC (Finnhub).</p>

<p><strong>RV:</strong> Two fit today's tape. First, the curve RV: the 2s10s (MM-009) is 10bp from target — the
normalisation is done — so the fresh expression is 5s30s (MM-054), long the Fed-anchored belly against the
supply-heavy 30Y, with the auction pricing the term premium at 1pm. Second, the froth RV: fade Korea (EWY put
spread, MM-055) against the book's existing US AI length rather than shorting the leaders — the KOSPI re-rated
~30% in a month on a narrative inversion while its own currency weakened, making it the highest-froth,
cheapest-vol expression of the same trade the S&amp;P is running at record highs. Both are low index beta, high
beta to this week's dated catalysts — the auction, the PPI, and AMAT's margin line.</p>
""",

    "positioning": """
<p><strong>The crowd is long the melt-up at VIX 15, short the yen against an official buyer, long the war
premium against rotting demand, and long Korea's story against Korea's own currency — four crowded rooms, four
pain trades.</strong> The loudest lean is AI-infrastructure length: four straight up-days, a KOSPI bull-market
headline, +19% single-day pops in the cohort's lowest-conviction names (SMCI: 10 buy / 13 hold / 4 sell), and
July's fund-manager survey already showed equity overweights at +42% with a record 54% expecting 'no landing.'
The pain trade is any margin or macro tax — Cisco just previewed it — and MM-055 owns the frothiest edge with
defined risk. In FX, the yen carry remains G10's most crowded funder while the first joint US-Japan intervention
since 1998 stands above the market and the BoJ now hikes with government blessing — the short-USDJPY re-entry
(MM-052) is long the pain trade with an official ceiling as the stop. In oil, the war premium is long and stale:
the EIA build and twin demand cuts caught the crowd leaning on headlines (MM-053). In rates, the steepener is no
longer contrarian at 2s10s — which is precisely why the harvest discipline applies there — but the 5s30s
(MM-054) still is, because the term-premium story is priced at auctions, not in positioning surveys. Gold's
crowd re-built as the hike faded (a two-month high, NOT a record — the record is ~$5,600 from January); the
book stays out of spot after July's lesson. The pain trade everywhere is the same — the crowd is positioned for
the celebration, and the long end is holding the bill.</p>
""",

    "funding": """
<p>SOFR sits ~3.63% — no funding stress through CPI week, the auction tail, or the melt-up; the plumbing is
quiet. <strong>The Pozsar mechanic:</strong> the flow that matters this cycle is not in repo, it is in the
primary market. The hyperscalers have become record IG borrowers — Alphabet, Amazon and Meta among 2026's
largest issuers, nineteen investment-grade deals on Monday alone (the most since January) — at the same time as
the Treasury runs a record coupon calendar: $58B of 3s, $42B of 10s (TAILED at 4.683%), $25B of 30s TODAY. The
AI buildout is a bond-supply machine: every data centre is funded by the same duration dollar the deficit needs,
so the long end cheapens even on friendly inflation data — which is why the 2s10s paid +232% and why the fresh
risk rotates to 5s30s (MM-054) rather than duration. The tell to watch is not SOFR; it is the auction stats —
today's 30Y bid-to-cover and indirect share price the term premium in public — and HY spreads (~270-280bp, the
richest decile of history), the one valve that has not yet acknowledged any of it. Underneath, the yen is the
system's other funding leg: a government-backed BoJ hiking cycle plus a standing US-Japan intervention ceiling
is slow-motion tightening of the world's favourite carry funder (MM-052) — the plumbing story of the next
quarter, not this one's.</p>
""",

    "tape_missing": """
<p><strong>The two-print week is only half done — and the tape is trading it as finished.</strong> The cool CPI
buried the hike at ~40%, but July PPI prints at 08:30 TODAY (cons +0.2% m/m after -0.3%), and a hot wholesale
print re-arms the September hike within 24 hours of the celebration. The falsifiable line: PPI at or below
+0.2% with a clean 30Y auction kills the hike into Jackson Hole (MM-013 pays toward 4.05%); PPI at +0.4%+ backs
the 2Y toward the 4.35% stop and taxes the melt-up at VIX 15. The core-vs-headline gap (2.5% vs 3.4%) is the
energy shock passing through — which makes the wholesale pipeline, not the CPI, the live risk.</p>

<p><strong>The corridor is the unpriced middle path in oil — in BOTH directions.</strong> The market prices
Hormuz as a binary: grand bargain (oil collapses) or miscalculation (oil spikes). The Iran-Oman safe-corridor
coordinates are agreed — a partial, corridor-first reopening that returns barrels WITHOUT a deal is live and
priced by no one, and it lands on a market whose demand is already falling 1.6m b/d. The falsifiable level:
Brent closing below $85 with the strait still 'blocked' confirms the demand thesis (MM-053 pays); a corridor
opening accelerates it; only an actual miscalculation breaks it, and the spread's premium caps that.</p>

<p><strong>The Burry tell: the religion swap IS the signal.</strong> The same Korean memory complex that crashed
9% in a day on a glut downgrade twenty sessions ago is now in a bull market on 'shortage beyond 2030' — while
the won weakens, the capacity race runs unchanged, and the book's 30% Micron weight sits on a +1,082% gain. When
the narrative inverts twice on the same facts, the facts were never the driver — positioning was. Over the next
two-to-three quarters either AI demand keeps outrunning the capacity (and the melt-up is early, not wrong), or
the glut the July downgrade previewed arrives into a market that has re-priced it away — and the fall will be
blamed on whatever headline is nearest. The discipline is unchanged and cheaper than ever to express: monetise
Micron's rich IVol into THIS strength, and own the swing-back with defined risk (MM-055), not conviction.</p>
""",

    "book_outlook": {
        "commentary": (
            "The melt-up is this book's tape: the AI sleeve that took July's crash on the chin just got the whole "
            "narrative back. <b>Micron</b> (~30% of the book, +1,082%) is the direct beneficiary of the KOSPI's "
            "bull-market re-entry (+3.56%, SK Hynix +5.9%) and the 'shortage beyond 2030' talk — which is "
            "precisely why the discipline bites NOW: a crowd that swung glut-to-shortage in twenty sessions is "
            "trading narrative, and narrative reverts. Monetise the rich IVol into THIS strength — collar or "
            "overwrite at far better strikes than July's panic offered — never add to a 30% weight in a "
            "melt-up. <b>NVDA</b>, <b>AVGO</b>, <b>AMD</b> (+394%) and the <b>SPY</b> core all ride the same "
            "re-crowning; AMD is the trim candidate into strength (triple-digit multiple, first casualty of any "
            "margin tax — Cisco just fell 4.6% on a RECORD quarter's margin mix). The rate sleeve is the "
            "morning's live risk: the <b>UST 1.25% 2031</b> and <b>Siemens IG</b> sit in front of a $25B 30Y "
            "auction one day after the 10Y TAILED — do not add duration before 1pm; the curve, not the coupon, "
            "is where rate risk pays (the desk's 2s10s is +232%, 10bp from target; fresh 5s30s today). "
            "<b>TotalEnergies</b> (+55%) is the laggard's seat: Brent fell ~1.2% on the demand cuts with the "
            "strait still shut — the war has stopped paying the energy length; the desk owns the downside via a "
            "Brent put spread (MM-053). <b>Xetra-Gold</b> (+109%) gets its redemption arc — gold at $4,400, a "
            "two-month high, exactly the real-rate relief the July regime denied it. The EUR base currency note: "
            "the ECB's September hike is ~fully priced while the Fed's fades — the ~72% USD sleeve's FX tailwind "
            "from July is turning into a headwind risk; the EUR 2.4m cash pile finally has a hiking ECB behind "
            "deposit campaigns. And for a client who watched the yen intervention headlines: the desk re-entered "
            "short USD/JPY today (MM-052) — the first differential in the cycle compressing from both sides."
        ),
        "outperform": [
            {"name": "Micron (MU, ~30%, +1,082%) — the narrative came back to the largest weight",
             "why": "The KOSPI re-entered a bull market (+3.56%, SK Hynix +5.9%, Samsung +4.9%) and memory talk "
             "flipped to 'shortage beyond 2030' — the book's biggest position leads today's tape. That is the "
             "monetisation window, not the add window: sell the rich IVol into strength (collar/overwrite), "
             "because the same crowd inverted this narrative once already this summer."},
            {"name": "Xetra-Gold (4GLD, +109%) — the redemption arc",
             "why": "Gold reclaimed $4,400, a two-month high, as the cool core buried the September hike and "
             "real-rate pressure eased — the exact relief the toll regime denied it in July (when the desk's "
             "gold trade was stopped at ~$4,000). The rate path, not the war, is gold's engine — today the rate "
             "path is the friend."},
            {"name": "The AI sleeve (NVDA, AVGO, SPY core) — re-crowned by the cohort",
             "why": "CoreWeave and Super Micro +19%, Lumentum +14%, SOX +2.5%, the Topix at a record — the "
             "whole complex re-rated. Ride it with the trim discipline on the frothiest holdings (AMD at a "
             "triple-digit multiple) and let the desk's defined-risk Korea fade (MM-055) act as the sleeve's "
             "cheap hedge."},
        ],
        "underperform": [
            {"name": "TotalEnergies (TTE, +55%) — the war stopped paying",
             "why": "Brent fell ~1.2% to ~$87.9 with the strait still shut: a +17.4m bbl build and IEA/OPEC "
             "demand cuts are rotting the premium from underneath. The energy length had its war in June-July; "
             "today it lags the tape. The desk owns the downside path with a defined-risk Brent put spread "
             "(MM-053) rather than selling the strategic holding."},
            {"name": "The bond sleeve (UST 2031, Siemens IG) — supply day",
             "why": "The 10Y tailed its auction at 4.683% and $25B of 30Y prints at 1pm today, with record IG "
             "issuance (the AI borrowers) competing for the same duration dollar. Hold, do NOT add before the "
             "auction — the curve steepeners (MM-009/MM-054) are how this book gets paid for rate risk."},
            {"name": "AMD (+394%) — the froth-edge trim candidate",
             "why": "The highest-multiple holding in the sleeve after a four-day cohort melt-up, into tonight's "
             "AMAT margin test and today's PPI/auction taxes. Cisco just demonstrated what happens to rich AI "
             "hardware stories on margin mix (-4.6% on a record quarter). Trim into strength — concentration "
             "management, not a view change."},
        ],
        "watch": [
            {"label": "Monetise Micron's IVol into the melt-up — the window is NOW, and it is better than July's",
             "text": "In July the discipline said collar the 30% weight into panic; today it says collar into "
             "euphoria — strikes and premia are far more favourable with the stock bid and vol still rich. A "
             "crowd that swapped glut for 'shortage beyond 2030' in twenty sessions can swap back on one "
             "downgrade. Overwrite/collar into THIS strength; never add."},
            {"label": "No duration before 1pm — the 30Y auction is the day's real event",
             "text": "The 10Y tailed at 4.683% a day after a FRIENDLY CPI — supply, not inflation, is setting "
             "the long end. If today's 30Y tails too, the bond sleeve marks lower again; if it stops through, "
             "add-points improve. Either way the desk expresses rate views via the curve (2s10s near target; "
             "fresh 5s30s), and the sleeve waits for the auction verdict."},
            {"label": "Put the EUR cash to work behind a hiking ECB — and watch the USD sleeve's FX seam",
             "text": "EUR 2.4m sits idle while the ECB hikes (September ~fully priced) and deposit campaigns "
             "reprice — the cash-drag fix is finally paid to happen. Simultaneously the FX engine that helped "
             "the ~72% USD sleeve all summer is turning: ECB hiking into a fading Fed hike compresses the "
             "differential euro-positive. The desk's EUR/USD short is on a 1.16 trim leash for the same reason "
             "— revisit the USD-sleeve hedge if EUR/USD reclaims 1.16."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> the hike is dead and the AI shortage is real — buy the melt-up. The cool core
(slowest since 2021) plus the July jobs miss took the September hike to ~40% and falling; CoreWeave's +112%
growth, Cisco's record revenue and SK Hynix's shortage-beyond-2030 talk prove the demand; Korea's bull-market
re-entry confirms the cycle turned. Dips are for buying, VIX 15 is fine, and oil falling means peace is close.</p>

<p><strong>The strongest argument against — the OFFER:</strong> the two markets with the least narrative in them
are refusing to confirm. The long end tailed a $42B auction the same day the front end rallied — record Treasury
supply plus record AI-capex IG borrowing is a term-premium machine no CPI print fixes, and $25B of 30s price it
at 1pm. Oil fell with the strait SHUT — a 17.4m bbl build and twin demand cuts, demand destruction wearing a
peace costume. The KOSPI surged into a WEAKENING won — euphoria the FX market won't fund. And the froth is
re-rating on a narrative that inverted once already this summer, on the same facts. The cheaper side owns the
curve (MM-054), the yen's double compression (MM-052), the demand crack (MM-053) and the froth's defined-risk
fade (MM-055) — the bill, not the party.</p>
""",

    "one_chart": """
<p class="theme">Today is a doubleheader: July PPI at 08:30 and the $25B 30Y auction at 1pm — the inflation test and the supply test of the same melt-up, six hours apart.</p>
<p>The single thing to watch is the pairing, not either print alone. The morning question is whether wholesale
inflation ratifies the cool CPI (cons +0.2% m/m after -0.3%): at or below consensus and the September hike is
effectively dead into Jackson Hole — the front end rallies, MM-013 finally pays, the melt-up gets its macro
all-clear. The afternoon question is whether the long end will fund the party: the 10Y TAILED at 4.683% a day
after friendly CPI, so a second tail in the 30Y confirms that supply — record coupons meeting record AI-capex IG
issuance — has replaced the Fed as the binding constraint (MM-009 tags its target; MM-054 is the fresh leg). The
trap pairing is a cool PPI followed by a bad auction: the tape would rally the morning and pay for it by two
o'clock. The tell pairing is hot PPI + clean auction: the hike re-arms and the froth (MM-055) pays first. Watch
the 1pm stop-through against 4.68% on the 10Y as the reference — the term premium is priced in public today.</p>
""",

    "catalyst_calendar": [
        {"day": "Thu", "date": "Aug 13 — TODAY",
         "event": "July PPI (08:30 ET) + jobless claims + $25B 30Y auction (1pm ET) + AMAT AMC — ALL PENDING",
         "consensus": "PPI cons +0.2% m/m (prior -0.3%); claims cons ~202K (single-sourced); the 30Y concludes "
                      "refunding week after the 10Y TAILED at 4.683% (b/c 2.53); AMAT cons ~$3.45 EPS / ~$9.2B "
                      "rev (Finnhub), four straight ~5% beats. Sources: BLS, Newsquawk, Finnhub.",
         "view": "The doubleheader: the inflation test and the supply test of the melt-up in one session, with "
                 "the equipment bellwether's margin line after the close. The auction is the day's real event.",
         "asymmetry": "Cool PPI + clean auction = the all-clear (MM-013 pays, melt-up broadens). Hot PPI or a "
                      "second tail = the bill arrives (MM-054/MM-055 pay, MM-013 at risk). A cool-PPI-bad-auction "
                      "split is the trap: morning rally, afternoon tax.",
         "dir": "down"},
        {"day": "Fri", "date": "Aug 14",
         "event": "Digestion day: weekly flows + China July credit window (through ~Aug 15)",
         "consensus": "BofA's weekly Flow Show and any China July money/credit release (forecast dismal: new "
                      "loans ~45bn yuan vs 1.61trn in June per Reuters poll; Commerzbank flags PBoC easing risk). "
                      "Sources: Reuters, Caixin, FXStreet.",
         "view": "The first read on whether the melt-up pulled in real money or just momentum — and whether "
                 "China's credit impulse is weak enough to force the PBoC's hand into a strong-yuan policy.",
         "asymmetry": "A dismal China credit print + PBoC easing talk pressures the AUD leg of MM-001 and feeds "
                      "the global-demand crack MM-053 owns; heavy melt-up inflows would mark the froth's top "
                      "cleaner for MM-055.",
         "dir": "flat"},
        {"day": "Mon", "date": "Aug 17",
         "event": "Hormuz corridor watch + Taiwan drills conclude + melt-up week two",
         "consensus": "The Iran-Oman corridor remains agreed-but-unopened; Han Kuang drills end Aug 14; no "
                      "US-Iran principal-level meeting scheduled. Sources: Al Jazeera, ABC, WaPo.",
         "view": "The unpriced middle path: a corridor-first partial reopening returns barrels without a grand "
                 "bargain — bearish oil on top of falling demand. Watch tanker traffic and UKMTO advisories, not "
                 "the principals' rhetoric.",
         "asymmetry": "Corridor movement accelerates MM-053; an Araghchi-style 'miscalculation' is the capped "
                      "spike risk the spread's premium already pays for. Either way the defined-risk shape wins "
                      "over spot.",
         "dir": "flat"},
        {"day": "Tue", "date": "Aug 18",
         "event": "Keysight + Jack Henry AMC (Finnhub feed) + US retail bellwethers week begins",
         "consensus": "KEYS cons $2.52 EPS (16 buy / 3 hold, four straight beats incl. +21%); JKHY cons $1.47 "
                      "(16 buy / 5 hold, four straight double-digit-to-high-single beats). Big-box retail "
                      "reports cluster this week (dates unverified — flagged). Sources: Finnhub.",
         "view": "The breadth test: whether the earnings tape beyond AI-infrastructure — test/measurement, "
                 "fintech plumbing, the consumer — can carry the melt-up's second week.",
         "asymmetry": "Strong non-AI prints broaden the rally and decay the fades; a consumer wobble into "
                      "record-high indices is the first genuine growth-scare input the tape has had in a month.",
         "dir": "flat"},
        {"day": "Late Aug", "date": "Aug 27-29 (look-ahead)",
         "event": "Jackson Hole — Warsh's first symposium as Chair (dates per press; single-sourced)",
         "consensus": "The venue where the September decision gets framed: hike odds ~40% and falling after the "
                      "cool CPI; Trump phones Warsh pressing for cuts (Bloomberg); the ECB and BoJ septembers are "
                      "both live. Sources: Bloomberg, CNBC, Kalshi.",
         "view": "The Papic setup of the quarter: Warsh cannot cut without confirming capture and cannot hike "
                 "without open war with the White House — the hold that results pins the front end and hands the "
                 "long end to supply. Every trade in the book is downstream of that bind.",
         "asymmetry": "A hawkish Warsh re-arms the hike (MM-013's risk, MM-012's friend); a dovish pivot "
                      "compresses the US-Japan differential harder (MM-052's accelerant) and steepens via the "
                      "front (MM-009/054).",
         "dir": "flat"},
        {"day": "Sept", "date": "Sep 15-17 (look-ahead)",
         "event": "The three-central-bank hike window: FOMC + BoJ + ECB septembers",
         "consensus": "Fed: ~40% hike and falling. ECB: 25bp ~fully priced. BoJ: ~60-74% for September per "
                      "market pricing, with Bloomberg reporting government backing for a faster pace. Exact "
                      "dates per usual calendars; Fed dates single-sourced. Sources: CNBC, Bloomberg, Kalshi.",
         "view": "The month the differential math resolves: if the ECB and BoJ hike while the Fed holds, the "
                 "dollar loses BOTH its carry edges in the same fortnight — the engine behind MM-052 and the "
                 "leash on MM-012.",
         "asymmetry": "ECB+BoJ hikes with a Fed hold = the yen and euro compress against the dollar (MM-052 "
                      "pays; MM-012 trims at 1.16). A surprise Fed hike into a midterm year = the rupture goes "
                      "public and the front end (MM-013) takes the hit.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> stop 1.662; trim toward 1.645. At ~1.635 (+0.6%) — green on no thesis of ours: the ECB hiking supports EUR, the melt-up bids AUD. A China-credit disappointment (due ~Aug 15) is the one remaining route to 1.61; an ECB-driven EUR squeeze is the exit signal.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> target +60bp, ~10bp away; stop trailed near +35bp. The tailed 10Y auction confirmed the engine; today's 30Y prices it publicly. A stop-through auction plus a cool PPI that rallies the LONG end is the take-the-target signal; a hot PPI bear-flattening via the front is the trailing-stop's job.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182; TRIM LINE 1.16. At ~1.153 (+0.6%) — green on borrowed thesis; the ECB hikes while the Fed hike fades. A EUR reclaim of 1.16 is the mechanical trim; a hot US PPI extending the dollar is the hold. Do not add.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; target 3.85%. At ~4.17% (~flat) with the catalyst finally delivered (hike odds ~40% from ~82%). TODAY'S PPI decides: at/below +0.2% m/m confirms the fade toward 4.05%; +0.4%+ re-arms the hike and the stop governs. Jackson Hole is the second gate.</li>
<li><strong>MM-2026-052 · Short USD/JPY (new):</strong> stop 164.5 (above the intervention ceiling); target 153. The thesis dies if the BoJ scoop is denied AND the September hike passes without action, or if officialdom abandons the ~164 line — an uncontested break above it says the differential math lost to the carry.</li>
<li><strong>MM-2026-053 · Brent $85/$75 put spread (new):</strong> defined risk, premium = max loss. The thesis is wrong if inventories flip to draws and the IEA/OPEC demand cuts reverse — a demand RECOVERY, not a war headline, is the falsifier. A Hormuz spike is the capped, accepted risk, not a thesis break.</li>
<li><strong>MM-2026-054 · 5s30s steepener (new):</strong> stop +60bp; target +130bp from ~+89bp. Two consecutive strong long-end auctions (today's 30Y stopping through, the next 10Y clean) would say the duration buyer returned and the term-premium thesis is early — reduce. A growth scare that bull-flattens the long end is the stop's job.</li>
<li><strong>MM-2026-055 · EWY put spread (new):</strong> defined risk, premium = max loss. The fade is wrong if the shortage narrative gets DATA (memory contract prices re-accelerating, capex discipline announcements) rather than management talk — narrative confirmed by numbers is a trend, not froth; let the spread expire and stand down.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The AI trade is ripping again — should we chase it?",
         "a": ("Ride what you own, don't chase what you don't. This complex crashed nine percent in a day in "
               "July on a glut downgrade and is now in a bull market on 'shortage beyond 2030' — same factories, "
               "opposite story, twenty sessions apart. You're heavily long the winners already; the move is to "
               "monetise the rich option premium on the biggest position into this strength and keep a small, "
               "defined-risk hedge on the frothiest corner, Korea. That way the melt-up pays you twice — once in "
               "price, once in premium — and a narrative swap back can't hurt the core.")},
        {"q": "Why did oil fall if the strait is still closed?",
         "a": ("Because demand broke before the diplomats did. US inventories built seventeen million barrels "
               "last week and both the IEA and OPEC cut next year's demand — the IEA now expects demand to FALL "
               "this year. Six months of war prices rationed consumption; the cure for ninety-dollar oil is "
               "ninety-dollar oil. That's why we own the downside in oil with a defined-risk put spread rather "
               "than celebrating a peace that hasn't happened — and why the energy holding lags today.")},
        {"q": "Is the Fed done — no September hike?",
         "a": ("Priced at about forty percent and falling, from eighty in late July — the cool core did real "
               "work. But the week is only half done: wholesale prices print this morning, and a hot number "
               "re-arms the hike within a day. The deeper point is that the Fed is the LEAST likely hiker in "
               "September — the ECB is fully priced to hike, and Tokyo's government now backs a faster BoJ. The "
               "dollar losing both its carry edges in one month is the bigger trade than the FOMC itself.")},
        {"q": "My bonds keep bleeding even on good inflation news. Why?",
         "a": ("Because the long end has a supply problem, not an inflation problem. The day after a friendly "
               "CPI, the ten-year auction still tailed — record Treasury borrowing is now competing with record "
               "corporate borrowing from the AI builders for the same buyers. We're not adding duration before "
               "today's thirty-year auction; the way we get paid for rate risk is the curve — our steepener is "
               "up over two hundred percent and near target, and we rotated the same logic into a fresh leg "
               "today.")},
        {"q": "Gold's back at $4,400 — weren't we stopped out of gold?",
         "a": ("We were, at four thousand, and the stop was right even though the thesis was too: in July's "
               "regime a bigger war meant higher real yields, which caps gold. What changed is the rate path — "
               "the September hike faded, real-rate pressure eased, and gold got its relief. Your Xetra-Gold "
               "holding captures that. We'd re-enter a trading position only with defined risk and a rate "
               "catalyst — gold trades the Fed, not the war; July proved it in both directions.")},
        {"q": "What does the yen intervention mean for us?",
         "a": ("It means the world's two biggest treasuries are now sellers of dollars above one-sixty-four — "
               "the first joint operation since 1998 — while Tokyo's government backs a faster BoJ hiking cycle "
               "and Washington's hike fades. We re-entered the short-dollar-yen trade today: it's the only major "
               "pair where the rate gap is closing from both sides, and the intervention line gives us the "
               "cleanest stop in FX. For your dollar-heavy book, it's also the early warning on the FX tailwind "
               "turning — the euro side of that story is why your idle euro cash finally earns something behind "
               "a hiking ECB.")},
    ],

    "ideas_note": (
        "<p>Today's ideas press the NEW information — the tailed auction, the twin demand cuts, the BoJ scoop, "
        "and Korea's narrative inversion — and rotate the nearly-done winner rather than pressing it. <strong>"
        "Short USD/JPY (MM-052)</strong> — the re-entry the new data justifies: a government-backed BoJ hiking "
        "cycle against a fading Fed hike, with the first joint US-Japan intervention since 1998 standing above "
        "the market as the stop. <strong>Brent $85/$75 put spread (MM-053)</strong> — demand destruction is "
        "doing the diplomacy (EIA +17.4m bbl build; IEA and OPEC both cutting 2026 demand); own the crack with "
        "the war's spike risk capped at the premium. <strong>5s30s steepener (MM-054)</strong> — rotate the "
        "2s10s champion's logic out the curve: the term premium is the funding constraint of the AI buildout, "
        "priced at auction TODAY. <strong>EWY put spread (MM-055)</strong> — fade the twenty-session religion "
        "swap in the froth's epicentre, where the equity surge came with a WEAKENING won. The 2s10s (MM-009) is "
        "trailed 10bp from target; the EUR/USD short (MM-012) survives on its 1.16 trim leash; the EURAUD short "
        "(MM-001) is on notice; the 2Y fade (MM-013) gets its PPI verdict this morning.</p>"
    ),

    "event_radar_note": (
        "<p>Demand does the diplomacy: the cool core buried the September hike (~40%), the AI trade roared back "
        "(SMCI/CRWV +19%, KOSPI +3.56% into a bull market, Topix record) — and the two narrative-free markets "
        "dissented. The 10Y TAILED its auction at 4.683% with $25B of 30Y printing TODAY at 1pm, an hour after "
        "July PPI (08:30 ET, cons +0.2%) — the supply test and the inflation test of the same melt-up. Oil FELL "
        "with the strait still shut (Trump: 'total control'; Iran: 'remains blocked'; Houthi strike killed 6) on "
        "a +17.4m bbl build and twin IEA/OPEC demand cuts. Cisco's record quarter fell 4.6% after hours on "
        "margin mix; AMAT reports TONIGHT. The ECB and BoJ septembers are both live hikes while the Fed's "
        "fades — and the book's steepener sits 10bp from target with four fresh ideas pressing the new "
        "information (MM-052 yen, MM-053 Brent puts, MM-054 5s30s, MM-055 Korea fade).</p>"
    ),

    "burry_tell": (
        "The tell is no longer in the memory market — it is in how the memory market changed its mind. Twenty "
        "sessions ago the KOSPI crashed nine percent in a day because one analyst cut SK Hynix's operating "
        "profit eight percent on slower HBM4 shipments; today the same index is back in a bull market, up "
        "roughly thirty percent from the July low, because management says the shortage runs 'beyond 2030.' "
        "Nothing in the physical world changed in those twenty sessions — the same fabs are pouring the same "
        "capital into the same capacity race against the same demand assumption. What changed was the story, "
        "and a market that can re-price the identical facts from glut to infinite shortage in a month is a "
        "market in which positioning, not information, sets the price. The confirming details: the won WEAKENED "
        "into the equity surge (the FX market declining to fund the story), the froth concentrated in the "
        "lowest-conviction names (Super Micro +19% with more sell-side holds and sells than buys), and the "
        "boom's own suppliers started paying a margin tax (Cisco, record quarter, -4.6%). Over the next "
        "two-to-three quarters this resolves the same two ways it always has: either AI demand genuinely "
        "outruns the capacity and the July downgrade was noise — or the glut that downgrade previewed arrives "
        "into a market that has re-priced it away entirely, and the fall gets blamed on whatever headline is "
        "nearest. The book is 30% Micron with a +1,082% gain and no need to guess: monetise the rich implied "
        "vol into THIS euphoria — the strikes are better than July's panic offered — and own the swing-back "
        "with a defined-risk Korea put spread. When the same crowd holds opposite convictions a month apart, "
        "sell them the insurance both times."
    ),

    "earnings_summary": (
        "Three ideas this refresh from the Finnhub feed (generated 06:00 UTC today). AMAT (Long, Medium, "
        "PRE — reports TONIGHT AMC): the WFE bellwether with the feed's strongest sell-side backing (39 buy / 6 "
        "hold) and four straight ~5% beats — but it reports into a four-day melt-up that has pre-paid the beat, "
        "so the print is a China-mix and gross-margin test, not an EPS test; defined risk only. CSCO (Long, "
        "High — data gap flagged, POST): a record FQ4 ($17.3B +18%, EPS $1.22 vs $1.19, FY27 ~+15%, AI orders "
        ">$4B) sold off ~4.6% after hours on gross-margin MIX — a disproportionate reaction to the optics of "
        "its own success; tagged OVERSOLD with the sell-side (23 buy / 10 hold / 0 sell) likely to defend. SMCI "
        "(Short, Medium, POST): +19% on a guidance beat that its own covering analysts won't endorse (10 buy / "
        "13 hold / 4 sell — the weakest split in the feed) with violent surprise history in both directions; "
        "tagged OVERBOUGHT — the froth edge of the melt-up, fade with defined risk. Positioning pillars are "
        "'estimated' throughout (Finnhub short interest unavailable), which caps CSCO at 'High — data gap "
        "flagged.' Noted, not padded: CoreWeave (+112% revenue, +19%), Lumentum (+14%) and Cerebras (revenue "
        "beat, sank after hours) are the cohort context; KEYS and JKHY (both Aug 18 AMC, both serial beaters) "
        "are next week's breadth test."
    ),
    "earnings_why": (
        "The universe filter is applied by the feed before scanning: market cap $10bn+, geographies US "
        "(primary) and South Korea (secondary), sectors Technology / Financials / Industrials / Utilities "
        "only. Today's earnings_data.md (Finnhub, 2026-08-13 06:00 UTC) returns 16 qualifying names — 5 "
        "pre-earnings (AMAT tonight; PS today BMO; KEYS, JKHY Aug 18) and 11 post-earnings from the Aug 10-12 "
        "cluster (CSCO, CBRS, COHR, TRMB, CRWV, LITE, QNT, SMCI, APGE, ASTS, BBIO, RKLB). Three are surfaced: "
        "AMAT as the highest-signal pending print (the equipment bellwether into a melt-up), CSCO as the "
        "highest-asymmetry post-print reaction (record quarter sold on margin mix = OVERSOLD), and SMCI as the "
        "cleanest froth fade (a +19% pop against the feed's weakest analyst split = OVERBOUGHT). The rest are "
        "noted but not rendered: the biotech/space names (APGE, ASTS, BBIO, RKLB) are outside the desk's "
        "core-sector edge despite passing the feed's filter, and padding the section dilutes the signal. "
        "Consensus EPS/revenue, recommendation splits and surprise history are SOURCED from Finnhub; short "
        "interest is unavailable, so every positioning pillar is tagged estimated; after-hours reaction "
        "figures are press-corroborated but tagged estimated until today's cash session confirms them."
    ),

    "book_aim": (
        "Harvest the champion, rotate into the new information, and let the melt-up pay the book twice. The "
        "2s10s steepener (MM-009) — the trade that carried the summer — is +232% at ~+50bp, ten basis points "
        "from its +60bp target, with today's $25B 30Y auction as the public pricing of its whole thesis: trail "
        "it, take the target if it prints, and do not press. The rotation is already on: the 5s30s (MM-054) "
        "carries the supply logic forward at ~+89bp, the yen re-entry (MM-052) owns the only differential in "
        "G10 compressing from both sides with an official intervention ceiling as the stop, the Brent put "
        "spread (MM-053) owns demand destruction with the war's spike risk capped, and the EWY put spread "
        "(MM-055) fades the froth's epicentre while doubling as the cheap hedge on the Fable book's 30% Micron "
        "weight. The survivors run on discipline lines: the EUR/USD short (MM-012) is green but its engine "
        "flipped (ECB hiking, Fed fading) — 1.16 is the mechanical trim; the EURAUD short (MM-001) is green on "
        "no thesis of ours and exits on any ECB-driven EUR squeeze; the 2Y fade (MM-013) finally has its "
        "catalyst (~40% hike odds from ~82%) and gets its verdict from this morning's PPI. The aim for the "
        "week: bank the curve target into the auction if it comes, keep every fresh expression defined-risk or "
        "official-ceiling-stopped in a tape at VIX 15 with four dated catalysts inside 24 hours, and treat the "
        "melt-up as a monetisation window — for the book's option premium and the client's concentration — "
        "not an invitation."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is "
                 "the average of closed trades. Position-level marks are live (TradingView); the fresh option "
                 "structures (MM-053, MM-055) are marked from spot and labelled. This is a Thursday PRE-MARKET "
                 "brief (US cash open ~09:30 ET) into an 08:30 PPI and a 1pm 30Y auction, so US equity-index "
                 "and rate marks may reflect the Wed Aug 12 close / live futures until the cash session prints.")
    },
    "idea_selection": [
        {"label": "Short USD/JPY — the differential compressing from both sides (MM-052)", "in": True,
         "text": ("The re-entry the NEW data justifies: Bloomberg reports Japan's government backs a faster BoJ "
                  "hike (Sept/Oct) with wholesale inflation at 7.2%, while the Fed's September hike fades to "
                  "~40% — the first both-sides compression of the cycle. The Aug 1 joint intervention (~164, "
                  "first since 1998, Bessent 'ready for more') is the official ceiling that makes 164.5 the "
                  "cleanest stop in FX. Replaces nothing; the July short was stopped in a different regime.")},
        {"label": "Brent Dec $85/$75 put spread — demand does the diplomacy (MM-053)", "in": True,
         "text": ("Oil fell with the strait still shut: a +17.4m bbl EIA build and BOTH the IEA and OPEC "
                  "cutting 2026 demand (IEA: -1.6m b/d) overwhelmed a live war premium. The put spread owns the "
                  "demand crack AND the corridor-first partial-reopening path, with the Hormuz spike risk "
                  "capped at the premium — the right shape for a market where the tail is violent in both "
                  "directions.")},
        {"label": "5s30s steepener — rotate the champion's logic out the curve (MM-054)", "in": True,
         "text": ("The 2s10s is 10bp from target; the supply story is not done. The 10Y tailed at 4.683%, $25B "
                  "of 30Y prints today, Treasury coupons run at records and the hyperscalers are record IG "
                  "borrowers — the long end funds the deficit AND the data centres. Long the Fed-anchored belly "
                  "vs the supply-heavy 30Y at ~+89bp, target +130bp, stop +60bp.")},
        {"label": "EWY put spread — fade the twenty-session religion swap (MM-055)", "in": True,
         "text": ("The KOSPI re-entered a bull market (+3.56%, ~+30% off the July low) on a narrative that "
                  "inverted from glut to 'shortage beyond 2030' in twenty sessions — while the won WEAKENED to "
                  "~1,421. Euphoria without FX endorsement, priced at cheap vol, into AMAT tonight and the "
                  "PPI/auction today. Defined risk; doubles as the hedge on the Fable book's 30% Micron weight.")},
        {"label": "2s10s steepener (MM-009) — trail and take the target, don't press", "in": False,
         "text": ("+232% at ~+50bp of a +60bp target. The tailed 10Y auction confirmed the engine and today's "
                  "30Y prices it publicly — but a nearly-done trade gets harvested, not pressed. The stop is "
                  "trailed near +35bp; the fresh supply risk lives in MM-054 at better asymmetry.")},
        {"label": "EUR/USD short (MM-012) — hold on the 1.16 trim leash", "in": False,
         "text": ("Green (+0.6%) but the engine flipped: the ECB hikes September (~fully priced) while the "
                  "Fed's hike fades — the differential is turning euro-positive and only the haven bid and the "
                  "oil drag remain. The 1.182 stop governs; 1.16 is the mechanical trim; no adds. The EURAUD "
                  "short (MM-001) is on the same notice for the same ECB reason.")},
        {"label": "Gold spot re-entry — declined despite the $4,400 reclaim", "in": False,
         "text": ("Gold at a two-month high (NOT a record — that is ~$5,600 from January) as the hike fades is "
                  "the regime the July long needed and did not get. Chasing it back now, post-move, at spot, "
                  "repeats July's error in mirror image. Gold re-enters this book only with defined risk and a "
                  "dated rate catalyst — Jackson Hole is the candidate, not today.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 14.0},
        {"label": "VIX",   "value": round(_g("vix") or 15.0, 2)},
        {"label": "VIX3M", "value": 16.5},
        {"label": "VIX6M", "value": 17.5},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.17, 3)},
        {"label": "5Y",  "value": round(US05Y_LVL, 3)},
        {"label": "10Y", "value": round(_g("us10y") or 4.67, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 5.24, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-052", "trade": "Short USD/JPY (the differential compressing from both sides)",
            "asset_class": "FX", "structure": "spot",
            "entry": "~159.4", "stop": "164.50 (above the intervention ceiling)", "target": "153.00",
            "conviction": 8,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "into the Sept/Oct BoJ window", "min_hold_days": 0,
            "thesis": ("The re-entry the NEW data justifies. Bloomberg reports Japan's government now BACKS a "
                       "faster BoJ hike (September or October) — wholesale inflation at 7.2% and a 40-year-low "
                       "yen flipped the Takaichi administration's incentive — while the Fed's September hike "
                       "faded to ~40% on the cool core. The US-Japan differential compresses from BOTH sides "
                       "for the first time in the cycle, and the trade carries an official backstop: the Aug 1 "
                       "joint US-Japan intervention (the first since 1998) defended ~164 with Bessent signalling "
                       "readiness for more — officialdom fights the move that would stop us out. The July short "
                       "was stopped at 163 in the oil-funder regime; every input has since flipped."),
        },
        {
            "id": "MM-2026-053", "trade": "Buy Brent Dec-26 $85/$75 put spread (demand does the diplomacy)",
            "asset_class": "Commodities (options)", "structure": "put spread",
            "entry": "~$85/$75 strikes vs ~$88 spot", "stop": "— (defined risk)", "target": "~3-4x on a demand break",
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "to Dec expiry", "min_hold_days": 0,
            "thesis": ("Own the demand crack, cap the war risk. Brent FELL ~1.2% through a window in which the "
                       "strait stayed shut, Houthi missiles killed six sailors and Araghchi threatened 'an even "
                       "bigger miscalculation' — because the EIA printed a +17.4m bbl build and BOTH the IEA "
                       "and OPEC cut 2026 demand (IEA: demand to FALL 1.6m b/d). Demand destruction is doing "
                       "the diplomacy. The unpriced middle path is bearish too: the Iran-Oman corridor is "
                       "technically agreed — a corridor-first partial reopening returns barrels without any "
                       "grand bargain. The put spread owns both paths; the premium caps the ever-present "
                       "Hormuz spike."),
        },
        {
            "id": "MM-2026-054", "trade": "5s30s UST steepener (the term premium funds the AI buildout)",
            "asset_class": "Rates (curve)", "structure": "long 5Y vs short 30Y",
            "entry": "~+89bp", "stop": "+60bp", "target": "+130bp",
            "conviction": 8,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 2, "stop_quality": 1},
            "horizon": "months", "min_hold_days": 0,
            "thesis": ("Rotate the champion's logic out the curve. The 2s10s (MM-009) is 10bp from target — the "
                       "inversion normalisation is done, but the supply story is not: the 10Y TAILED its $42B "
                       "auction at 4.683% (b/c 2.53) a day after a FRIENDLY CPI, $25B of 30Y prints today, "
                       "Treasury coupons run at records, and the hyperscalers are record IG borrowers — the "
                       "long end is being asked to fund the deficit AND the data centres. The belly is anchored "
                       "by a Fed whose hike is fading; the 30Y floats on supply. Long 5Y vs short 30Y at ~+89bp "
                       "owns the next leg of the regime that paid the 2s10s +232%."),
        },
        {
            "id": "MM-2026-055", "trade": "Buy EWY put spread (fade Korea's twenty-session religion swap)",
            "asset_class": "Equity (options)", "structure": "put spread",
            "entry": "~5%/15%-OTM, Oct expiry", "stop": "— (defined risk)", "target": "~4-5x on a froth unwind",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Oct expiry", "min_hold_days": 0,
            "thesis": ("Fade the religion swap, not the technology. Twenty sessions after crashing 9% in a day "
                       "on a glut downgrade, the KOSPI is back in a BULL MARKET (+3.56%, ~+30% off the July "
                       "low, Samsung +4.9%, SK Hynix +5.9%) on management talk of a shortage 'beyond 2030' — "
                       "while the won WEAKENED to ~1,421. Same fabs, same capacity race, opposite narrative, "
                       "and the FX market refusing to fund it. With vol cheap (VIX ~15) into AMAT tonight and "
                       "the PPI/30Y auction today, a defined-risk EWY put spread buys the swing-back at its "
                       "cheapest — and doubles as the hedge on the Fable book's 30% Micron weight."),
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
