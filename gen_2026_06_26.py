#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-26 (Friday). THE CHIPS BITE BACK.

THE NEXT CHAPTER vs the Jun 18 (post-Warsh) run: the hawkish-dots regime got a NEW, structural
reason to be right — and it isn't oil. The AI memory supercycle became a consumer-price shock.
- MICRON BLEW OUT (Jun 24 AMC). FY-Q3 revenue $41.456bn (vs ~$36.9bn est), adj EPS $25.11 (vs
  $21.40, +17%). CEO Mehrotra: HBM/memory tightness "locked in to persist beyond calendar 2027."
  The book's LARGEST position (~25.8%) printed a blowout — the AI-memory bull thesis confirmed.
  Semis surged after-hours; Jun 26 premarket ripped (ES +0.78%, NQ +2.15%). (TheStreet, CNBC.)
- THE SAME SHORTAGE HIT CONSUMERS. Thu Jun 25: Apple raised Mac/iPad up to +$300 (MacBook Air
  $1,099->$1,299; Mac Studio M3 Ultra $3,999->$5,299; iPad Air $599->$749); Microsoft put Xbox
  +$100-150 from Aug 1 (Series S->$500, Series X->$800). BOTH blamed the AI-data-center DRAM
  shortage — memory prices +98% in 2026, data centres now eat ~70% of world memory output (vs
  20-30% in 2022). The Mag7 FELL on its own supply chain's pricing power: Nasdaq -0.46% to
  25,358.60, S&P -0.01% to 7,357.49, Dow +0.14% to 51,920.62. (Euronews, Al Jazeera, CBS, CBC.)
- MAY PCE PRINTED HOT. Headline 4.1% (highest since Apr 2023), core 3.4% (highest since Oct 2023),
  m/m +0.4% / core +0.3%, in line. Driven by the Iran-war oil/gasoline spike — a BACKWARD-looking
  May reading even as Brent now sits at $74. Sep hike odds ~68-70% (from 29% a week ago); BofA
  sees 3 hikes to 4.25-4.5%; JPM dissents (on hold). (CBS, CNBC, Trading Economics, Fortune.)
- GOLD BROKE $4,000. First sub-$4,000 print since November (Jun 23), now ~$4,015 — down ~29% from
  the Jan ATH of $5,608. Hawkish Fed + DXY at a 13-month high (~101.4) + Iran de-escalation +
  $2bn May ETF outflows. The book's gold long (MM-005) is the casualty, ~-11%. (Bloomberg, Yahoo.)
- BUT YIELDS FELL. Despite the hot PCE and hawkish Fed, the 2Y eased to ~4.09% (from 4.22% Jun 18)
  and the 10Y to ~4.37% (from 4.50%) — the tech-selloff safe-haven bid + a slowing-goods read
  (PC shipments -11%, phones -13%) drove a duration rally. The book's rate longs (MM-004/013) and
  the steepener (MM-009) were RESCUED. (CNBC.)
- OIL BOUNCED OFF THE LOWS. Brent ~$74.7 (+~2% Jun 25), WTI ~$70, after US-Iran talks in Geneva/
  Switzerland were ABRUPTLY POSTPONED (Jun 19) on the nuclear file — yet Hormuz flows hit their
  fastest since the war, Saudi tankers resumed to Ras Tanura, Qatar issued its first post-war
  tender. Normalisation caps the bounce; the "deal" is declared, not signed. (CNBC, Al Jazeera.)
- BITCOIN sub-$60k (lowest since 2024), money rotating OUT of crypto INTO AI equity. DXY 13-mo
  high; EUR/USD ~1.138 (short EUR/USD MM-012 vindicated). Nikkei off its 72,831 peak; DAX +1.03%.
- TODAY: May PCE (released) + final-June UMich; quarter/half-end Mon Jun 29-Tue Jun 30; ISM Mfg
  Jul 1; June PAYROLLS Jul 2-3 (first labour read in the guidance vacuum); EU tariff deadline Jul 4.
- BOOK ACTION: MM-008 SPX put spread expires Jun 27 — BANKED today (~+29% from entry; FOMC tail
  did its job, S&P rallying away from the strike on Micron). Collar the 25.8% Micron AFTER the
  blowout (lock the gain). Gold long held on min-hold to ~Jul 15, deeply offside.

Run:  python gen_2026_06_26.py
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
# Option spreads have no live feed — mark from spot.
# SPX 7300/7000 put spread (MM-008): EXPIRES Jun 27. The FOMC tail it was held for PAID (peak ~$60,
# +71%). With the S&P ~7,357 and the Micron blowout ripping premarket back ABOVE the strike zone,
# and one session to expiry, the residual is mostly theta — harvest it rather than let it bleed to
# zero over the weekend. Banked below at ~$45 (~+29% from the ~$35 entry); handled by close, not a mark.

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
    "MU":   "The blowout landed: FY-Q3 revenue $41.5bn and adjusted EPS $25.11 (vs $21.40) with the CEO calling memory "
            "tightness 'locked in beyond 2027.' MU is the Fable book's LARGEST position (~25.8%) and the AI-memory "
            "thesis is now confirmed, not contested — but a confirmed catalyst on a quarter of the book is the moment "
            "to COLLAR and lock the gain (rich post-print calls finance the puts), not to chase an OVERBOUGHT print. "
            "The fresh expression is the memory-vs-OEM RV (MM-028): own the pricing power, short who pays for it.",
    "NVDA": "The Mag7 fell on its OWN supply chain's pricing power — every HBM wafer Micron sells into NVDA's GPUs is a "
            "wafer denied to a consumer device, and the AI-memory cost is now an input-cost story for the cohort too. "
            "NVDA is the demand engine of the DRAM shortage that just repriced Apple and Microsoft hardware; an "
            "OVERBOUGHT print is the AI-capex bid, not a fresh long here. Own the second-order inflation read (MM-027), "
            "not another chase of the leader.",
    "AAPL": "The clean tell of the new regime: Apple raised Mac and iPad prices up to $300 (MacBook Air $1,099->$1,299, "
            "Mac Studio M3 Ultra $3,999->$5,299) and named the AI-DRAM shortage as the cause, then the stock LED the "
            "Mag7 lower. The box-maker eats the memory cost the box-maker cannot fully pass through into a -11% PC / "
            "-13% phone shipment year. AAPL/HPQ/DELL are the margin casualties of the supercycle — the SHORT leg of the "
            "memory RV (MM-028). Oversold is a value trap while the input cost is still climbing.",
    "XLE":  "Energy keeps bleeding as the war premium drains: Brent ~$74 / WTI ~$70 even after the bounce on the "
            "postponed US-Iran talks, with Hormuz flows the fastest since the war and a 13-month-high dollar a second, "
            "mechanical drag on USD-priced crude. Energy is the disinflation half of the bifurcation — oversold is NOT "
            "a buy; sell income against any energy length, and own the broader metals/commodity rollover (gold sub-$4k).",
    "GLD":  "Gold BROKE $4,000 (Jun 23, first since November), now ~$4,015 — down ~29% from the January $5,608 peak. "
            "The real-rates engine won outright: a hawkish Fed, a 13-month-high dollar, the Iran de-escalation and "
            "$2bn of May ETF outflows drained both engines at once. We OWN it (MM-005 / the book's 4GLD) at ~-11%, held "
            "on the min-hold to ~Jul 15. Oversold is real but un-actionable as an add — the defined-risk move is the "
            "GLD put-spread hedge (MM-029) that owns the continuation while protecting the underwater long.",
    "TLT":  "Duration was RESCUED: despite a hot PCE (4.1%/3.4%) and a Fed pricing a September hike, the 2Y eased to "
            "~4.09% and the 10Y to ~4.37% as the tech-selloff bid and the goods-slowdown read (PC -11%, phones -13%) "
            "drove a flight to quality. We are long via the short-2Y book (MM-013, now GREEN), the 10Y (MM-004, green) "
            "and the steepener (MM-009, ~+85%). The bond market is trading the energy disinflation over the dots — but "
            "the silicon-inflation (MM-027) is the offsetting risk, so hold the rate longs, do not press them.",
    "XLF":  "Financials remain the rate-regime equity winner: a no-cuts, higher-for-longer Fed and a still-elevated "
            "front end lift net-interest margins while the AI-multiple cohort carries the memory-cost overhang. The "
            "long XLF / short XLK rotation (MM-025) is the cleaner sector RV than chasing the Micron-led semis bounce — "
            "own the margin beneficiary against the multiple-and-input-cost casualty.",
    "BTC":  "Bitcoin broke below $60,000 (~$59,334), its lowest since 2024, as money rotated OUT of crypto and INTO AI "
            "equity on the Micron print — the same dollar-strength, real-rates regime that broke gold. A 13-month-high "
            "dollar and ETF outflows are the macro headwind; oversold is not a signal while the rotation into AI is "
            "live. Not a book position; a tell that the liquidity bid is concentrating, not broadening.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("The Chips Bite Back: AI's Memory Crunch Becomes a Consumer-Price Shock — "
          "the AI Trade Turns Into the Inflation Trade as Gold Breaks $4,000")
regime_note = (
    "The AI bull story and the inflation story stopped being two stories. Micron's blowout — FY-Q3 revenue $41.5bn, "
    "adjusted EPS $25.11 against $21.40, and a CEO telling the Street that memory tightness is 'locked in to persist "
    "beyond calendar 2027' — and the consumer price shock that landed the same forty-eight hours are the same event. "
    "Apple raised Mac and iPad prices by up to $300 and Microsoft put the Xbox up $100-150, and both named the cause "
    "outright: the AI-data-center DRAM shortage, with memory prices up 98% this year as the hyperscalers' build-out "
    "now consumes roughly seventy percent of the world's memory output against twenty to thirty percent in 2022. The "
    "AI capex super-cycle that is printing Micron's record quarter is the same shortage forcing a $200 MacBook price "
    "rise, and the Mag7 fell on its own supply chain's pricing power: the Nasdaq slipped 0.46% to 25,358.60, the S&P "
    "essentially flat at 7,357.49, the Dow up 0.14% to 51,920.62. (TheStreet, CNBC, Euronews, Al Jazeera, CBS.) "
    "Decompose the headline that frames it. May PCE printed hot — 4.1% headline, the highest since April 2023, and "
    "3.4% core, the highest since October 2023 — and the consensus reads it as broad validation of Warsh's hawkish "
    "dots. The anatomy says something narrower: that reading is a backward-looking May number driven by the Iran-war "
    "gasoline spike, and energy has since collapsed — Brent sits at $74 and gold broke $4,000 for the first time "
    "since November, down 29% from its January peak. The composition of inflation just flipped under the headline: "
    "the energy push is reversing hard while a silicon push is only beginning, and one of those is a relative-price "
    "shock the Fed cannot cut its way out of, because hiking rates does not make HBM wafers. (CBS, CNBC, Bloomberg, "
    "Trading Economics.) "
    "The bond market and the Fed are now openly disagreeing. Despite a hot PCE and a Fed that pencilled a September "
    "hike — now priced near 68% from 29% a week ago — the 2Y eased to ~4.09% and the 10Y to ~4.37%, because the tape "
    "is trading the energy disinflation and the goods slowdown (PC shipments down 11%, smartphones down 13% on the "
    "same shortage) over the dots. That rescued the book's rate longs: the steepener (MM-009) sits near +85%, and the "
    "duration longs (MM-004/013) are green for the first time in weeks. The dollar at a 13-month high vindicated the "
    "short EUR/USD (MM-012); the gold long (MM-005) is the casualty at roughly -11%, held on its min-hold. The SPX "
    "put spread (MM-008) that paid the FOMC tail is banked into tomorrow's expiry. "
    "Today May PCE is on the tape and the final-June sentiment lands; then a quarter-and-half-end on Monday and "
    "Tuesday, ISM next Wednesday, and June payrolls July 2-3 — the first labour read in the guidance vacuum, days "
    "before the July 4 EU-tariff deadline. The regime is no longer 'higher-for-longer because Warsh says so.' It is "
    "higher-for-longer because the boom everyone is long just became the thing keeping core goods sticky."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# ── Bank the expiring SPX put spread (MM-008) ───────────────────────────────────
book.step("Banking MM-2026-008 (SPX put spread) into Jun-27 expiry")
book.discretionary_close(
    trades, "MM-2026-008", 45.0,
    "BANKED into Jun-27 expiry. The FOMC-tail hedge did its job — peak ~$60 (+71%) as Warsh's hawkish "
    "dots dropped the S&P toward the strike and VIX re-rated to 18.4. With the Micron blowout ripping the "
    "tape back above the strike zone premarket (ES +0.78%) and one session to expiry, the residual is "
    "theta — harvested at ~$45 (+~29% from the ~$35 entry) rather than risk it bleeding to zero over the "
    "weekend. The replacement downside is the fresh Aug SPX put spread (MM-030).")

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
            "Did exactly what it was flagged to do. The real-rates engine reversed on the hawkish dots — gold fell ~2% "
            "to ~$4,275 as the 2Y hit a one-year high and DXY broke 100, the 'first hedge to give back' call — but it "
            "tested toward the $4,250 stop, held, and the second engine (safe-haven / dollar-debasement) caught it: it "
            "bounced above $4,300 Thursday on the Iran-deal headlines. The position is offside from the $4,523 entry "
            "(~-4%) but above stop and inside its 45-day min-hold to ~Jul 15. The two engines now pull in opposite "
            "directions — a hawkish-rate headwind against an Iran-durability and structural-EM-buying bid. Held, not added."
        ),
        "catalysts": [
            "Hawkish Fed / 2Y at one-year high — the real-rates headwind, the force against gold now",
            "Iran-deal durability — a slip (Israel) is the safe-haven bid that caught the bounce",
            "DXY >100 — a dollar headwind to USD-priced gold",
            "EM central-bank Q2 purchases (China, India, Turkey — structural buyers under the price)",
        ],
        "risks": (
            "A second hawkish data surprise (a hot claims/Philly Fed in the guidance vacuum) sends real yields higher "
            "and breaks the $4,250 stop; the MoU signs cleanly and the last safe-haven premium drains. Stop $4,250 "
            "(45-day min-hold keeps it open to ~Jul 15)."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the real-rates engine reversed; the mispricing is now the dollar-debasement / "
                            "central-bank-bid floor under a hawkish-rate selloff, a narrower gap than a week ago.",
            "catalyst":     "1/2 — the FOMC catalyst passed against the position; the Iran tail is the remaining one.",
            "positioning":  "1/2 — positioning is not extreme; the spec long thinned on the give-back.",
            "confirmation": "1/2 — it held the stop and bounced, but the trend broke this week.",
            "stop_quality": "1/1 — $4,250 is a defined level; the min-hold rule is the discipline mechanism.",
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
            "Gave back, but still the best structural position in the book. The hawkish dots bear-FLATTENED the curve — "
            "the 2Y rocketed +16bp while the 10Y rose only +7bp — so the spread compressed to ~+28bp from ~+41bp, "
            "cutting the open gain from ~+157% to ~+85% (entry +15bp off an 18-month inversion). The flattening is "
            "the hawkish-repricing risk the trade always carried. But the medium-term thesis is, if anything, "
            "reinforced: a Fed that hikes into an oil-disinflation eventually has to reverse, which re-steepens via the "
            "front end, and the guidance vacuum keeps a widening term premium under the back end. Min-hold to ~Jul 16; "
            "target +60bp; held, not added."
        ),
        "catalysts": [
            "Guidance-vacuum term premium — keeps the 10Y elevated, steepening pressure on the back end",
            "Oil sub-$80 + soft data — eventually fades the front-end hike pricing and re-steepens",
            "Treasury supply at the back end — long-end auctions selling off = steepens",
            "A Fed policy error (hiking into disinflation) — the medium-term re-steepening catalyst",
        ],
        "risks": (
            "The hawkish repricing keeps bear-flattening the curve as the front end prices the Sep hike; a global "
            "safe-haven bid flattens via the long end; a Fed hike inverts the front. Stop: spread below -10bp."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve is still structurally underpriced vs the late-cycle mean off an 18-month "
                            "inversion, even after the hawkish flattening.",
            "catalyst":     "1/2 — the near-term FOMC catalyst flattened it; the re-steepening catalysts are slower-burn.",
            "positioning":  "1/2 — front-end positioning is now MORE hawkish post-Warsh; squeeze fuel builds for later.",
            "confirmation": "1/2 — the spread held well positive (~+28bp) through the flattening; a give-back, not a break.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "Vindicated. The most-contested leg for two weeks finally paid: a hawkish Fed that penciled a hike against "
            "a paused ECB broke the rate-path asymmetry the trade was built on, DXY ripped through 100 to ~100.5, and "
            "EUR/USD sliced ~60 pips through 1.1550 toward 1.1500. The thesis has gone from contested to confirmed, and "
            "the dollar breakout above the figure is a fresh technical regime, not a one-day spike. It pairs cleanly "
            "with the book's European-equity tilt. Hold and let it run toward 1.13; the fresh defined-risk way to add "
            "downside is the EUR/USD put spread (MM-024). Respect the (now-distant) 1.182 stop."
        ),
        "catalysts": [
            "Hawkish Fed (penciled hike) vs paused ECB — the rate-path asymmetry now firmly favours the dollar",
            "DXY breaking 100 — a fresh technical dollar regime, not a fade",
            "Spec positioning unwind — EUR longs near multi-year highs are the squeeze fuel",
            "Iran deal / risk-on — the offsetting EUR-supportive force to watch",
        ],
        "risks": (
            "A clean Iran signing and broad risk-on lifts EUR; US data rolls over hard and the hawkish-Fed dollar "
            "fades; an ECB official re-opens the hike door. Stop 1.182 (now ~3 figures away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the rate-path asymmetry the trade priced finally widened; the dollar broke 100 and "
                            "the mispricing is resolving in the position's favour.",
            "catalyst":     "2/2 — the FOMC delivered the dated catalyst and it paid; the dollar-breakout is confirmed.",
            "positioning":  "1/2 — EUR spec longs near multi-year highs provide further unwind fuel.",
            "confirmation": "2/2 — EUR/USD broke 1.1550 and DXY broke 100 on the dots; confirmed.",
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
            "The trade the Fed shot at — and the overnight tape caught. The whole thesis was that the front end "
            "over-priced a 2026 hike; Warsh's SEP penciled one in and the 2Y spiked +16bp to a one-year-high 4.216% at "
            "the close. But it eased back to ~4.16%, essentially the 4.162% entry, overnight — the position is roughly "
            "flat, not the loss the dots implied, and that fade is itself the first evidence for the trade. The Fed "
            "explicitly contradicted the view; the reason to hold rather than fold is the oil-disinflation — Brent at "
            "$78 argues the Fed's raised 3.6% inflation forecast is too high, and a Sep hike priced into a falling-oil "
            "disinflation is exactly the kind of pricing that unwinds. Min-hold to ~Jul 8; stop 4.35%. Do NOT add "
            "ahead of the dust settling."
        ),
        "catalysts": [
            "Oil sub-$80 (Brent ~$78) — the disinflation that argues the Fed's 3.6% forecast is too high",
            "Jobless claims + Philly Fed Jun 18 — soft prints rebuild the no-further-hike case",
            "The Sep meeting — where the penciled hike gets confirmed or priced out",
            "Any labour re-acceleration — the risk that confirms the hawkish dots",
        ],
        "risks": (
            "The Sep hike gets more fully priced and the 2Y runs to the 4.35% stop; the MoU fractures and inflation "
            "expectations snap back; the labour data re-accelerates. Stop 4.35%; min-hold to ~Jul 8."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the oil-disinflation re-widens the gap between the 2Y and the justified hike "
                            "probability, but the Fed just leaned hard the other way.",
            "catalyst":     "1/2 — the FOMC catalyst passed against the trade; the data catalysts are second-order now.",
            "positioning":  "2/2 — the market is now MAXIMALLY positioned for the hawkish Warsh; squeeze fuel on any soft print.",
            "confirmation": "1/2 — the 2Y spiked to a one-year high on the dots, then eased back to ~entry overnight; a first confirming fade.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~19bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-023": {
        "instrument": (
            "Long rates volatility — a 2-month long-bond (TLT) straddle or a payer/receiver strangle on "
            "the 10Y (proxy: long MOVE). Defined-risk long realised/implied rate vol. Pays if the term "
            "premium re-widens and yields move in either direction; max loss is the premium."
        ),
        "fundamental_thesis": (
            "The cleanest expression of the Warsh regime is in the bond market, not equities. Forward guidance is "
            "mechanically a term-premium compressor — it tells the market the path of the funding rate. Warsh just "
            "dropped his own dot, shortened the statement and stood up a balance-sheet task force, which removes that "
            "anchor and hands the term premium back to the market. The 10Y backing up to 4.499% on a 'hold' is the "
            "first evidence; MOVE is the cleaner read on it than VIX. A long-bond straddle owns the re-widening in "
            "either direction — a hawkish over-tightening that lifts yields, or the policy-error reversal that rallies "
            "them — with defined premium. Rate vol, not equity vol, is where the guidance vacuum gets paid."
        ),
        "catalysts": [
            "The guidance vacuum itself — no forward path = a structurally wider, more volatile term premium",
            "Jobless claims + Philly Fed today — each print now a discrete rate-vol event",
            "Treasury supply / the balance-sheet task force — the QT/issuance overhang",
            "The Sep meeting — hike-confirm or hike-unwind, both move the long end",
        ],
        "risks": (
            "Yields settle into a tight range and realised rate vol fades; the term premium stays anchored despite the "
            "guidance change; the straddle decays. Max loss is the defined premium."
        ),
        "breakdown_why": {
            "gap":          "2/3 — MOVE does not yet price a permanent guidance-vacuum term-premium re-rating.",
            "catalyst":     "2/2 — the guidance change is done and dated; the data prints are live, near-term.",
            "positioning":  "2/2 — the market is positioned for a calm range; maximum room for a rate-vol re-rate.",
            "confirmation": "1/2 — the 10Y backed up on a hold (first evidence); the regime is one session old.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-024": {
        "instrument": (
            "Buy a 3-month EUR/USD 1.14/1.12 put spread — defined-risk short EUR / long USD downside. "
            "Buy the 1.14 put, sell the 1.12 put. Owns the post-Warsh dollar breakout below 100 (DXY) "
            "with limited premium; max loss is the premium. Complements the spot short MM-012."
        ),
        "fundamental_thesis": (
            "The dollar broke a figure for the first time since the early Iran war. A hawkish Fed that penciled a hike "
            "against a paused ECB widened the rate-path asymmetry the EUR/USD short was built on, DXY ripped through "
            "100 to ~100.5, and EUR/USD sliced through 1.1550. A put spread owns the continuation toward 1.13 with "
            "defined premium and positive convexity — the same view as the spot short (MM-012) but with capped risk "
            "into a known two-sided tail (a clean Iran signing is the EUR-supportive risk-on offset). The structure "
            "is the disciplined way to ADD dollar length after a breakout rather than chase spot at the figure."
        ),
        "catalysts": [
            "Hawkish Fed vs paused ECB — the rate-path asymmetry now firmly dollar-positive",
            "DXY breaking 100 — a fresh technical regime that tends to extend",
            "US data in the guidance vacuum — a firm print extends the dollar",
            "Iran signing / risk-on — the EUR-supportive offset the defined risk caps",
        ],
        "risks": (
            "A clean Iran signing sparks broad risk-on and lifts EUR; US data rolls over and the dollar fades the "
            "breakout; the spread decays. Max loss is the premium."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the dollar broke 100 and the rate asymmetry widened; the move has room to 1.13.",
            "catalyst":     "2/2 — the FOMC delivered the catalyst; the dollar regime is fresh and dated.",
            "positioning":  "2/2 — EUR spec longs near multi-year highs are the unwind fuel.",
            "confirmation": "2/2 — DXY broke 100, EUR/USD broke 1.1550; confirmed.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-025": {
        "instrument": (
            "Long XLF (financials) / short XLK (technology) — a sector relative-value ratio expressing "
            "the rotation a hawkish, no-cuts, higher-for-longer Fed drives. Rises when financials "
            "outperform long-duration tech."
        ),
        "fundamental_thesis": (
            "A higher-for-longer Fed with the cut bias stripped and a 2Y at a one-year high is a sector-rotation "
            "engine: it lifts financial net-interest margins while it compresses the long-duration tech multiple "
            "through a higher discount rate. Wednesday wrote the first leg — the Dow fell less than the Nasdaq, and "
            "Microsoft, Meta, Alphabet and Amazon led the losses while financials held up better. This is the "
            "rate-regime version of the breadth RV (MM-022): where RSP/QQQ trades concentration, XLF/XLK trades the "
            "rate sensitivity directly. Long the margin beneficiary, short the multiple casualty — low beta to the "
            "index level, high beta to the higher-for-longer repricing."
        ),
        "catalysts": [
            "Hawkish Fed, no cuts, 2Y at a one-year high — the NIM tailwind for financials, multiple headwind for tech",
            "The guidance vacuum — a higher, more volatile rate path that favours rate-sensitive value",
            "Q2 bank earnings (July) — confirmation the NIM read is translating",
            "AI-capex / debt overhang — the structural drag on the tech leg",
        ],
        "risks": (
            "A dovish data surprise re-rates tech multiples and the rotation reverses; a credit/growth scare hits "
            "financials harder than tech; the AI melt-up resumes. Stop: ratio -3% from entry."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the rate-regime divergence between NIM-geared financials and multiple-geared tech "
                            "is real and freshly widened by the hawkish SEP.",
            "catalyst":     "1/2 — the rotation is in motion but the broadening is a gradual, multi-session move.",
            "positioning":  "2/2 — the long-duration-tech long is the most crowded, most rate-sensitive theme in the index.",
            "confirmation": "1/2 — Wednesday's Dow-over-Nasdaq, tech-led-losses split started it; one confirming leg.",
            "stop_quality": "1/1 — a fixed ratio stop (-3%) is a clean, defined failure threshold.",
        },
    },
    "MM-2026-026": {
        "instrument": (
            "Long Gilts (UK 10-year) — receive UK 10Y / long the long-Gilt future. A rates trade tied to "
            "today's BoE decision and the soft UK CPI. Pays if Gilt yields fall on a dovish-leaning hold."
        ),
        "fundamental_thesis": (
            "The UK is the one major where the data is undercutting the hawks the same week the US Fed empowered them. "
            "May CPI came in at 2.8% — unchanged and BELOW the 3.0% consensus, with services and housing softening — "
            "which weakens the case of the BoE's hawkish dissenters (Pill, Greene) heading into today's noon decision. "
            "A near-unanimous hold at 3.75% with a soft-CPI, dovish-leaning tone pulls Gilt yields down even as US "
            "yields back up on Warsh, a clean rate-divergence trade. The asymmetry: the market half-prices the hawkish "
            "dissent risk, so a hold that leans on the soft print is the under-positioned outcome. Defined catalyst, "
            "today; a hawkish surprise (more dissents, sticky-services language) is the stop."
        ),
        "catalysts": [
            "BoE decision 12:00 GMT today — a hold at 3.75% is near-unanimous (Reuters poll 65/65)",
            "Soft UK May CPI (2.8%, below 3.0%) — undercuts the Pill/Greene hawkish-dissent case",
            "Bailey press conference 12:30 GMT — the tone/vote-split read",
            "US-UK rate divergence — Gilts rally as US yields back up on Warsh",
        ],
        "risks": (
            "Two-plus hawkish dissents and sticky-services language reprice the BoE hawkish; the transport-led CPI "
            "components (fuel +6.8%) dominate the tone; a global rate-vol spillover from the US lifts Gilts. Stop: "
            "UK 10Y +15bp from entry."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the soft CPI vs the half-priced hawkish-dissent risk is a real, dated mispricing.",
            "catalyst":     "2/2 — the BoE decision and presser are today, direct, Gilt-relevant events.",
            "positioning":  "1/2 — the market half-prices the dissent risk; modest squeeze fuel on a dovish hold.",
            "confirmation": "1/2 — the soft CPI is the confirming data; the decision is still pending.",
            "stop_quality": "1/1 — a +15bp yield stop is a clean, defined level.",
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
    "MM-2026-001": "Quiet leg. ECB pause behind it, no forward EUR catalyst; a hawkish-Fed risk-off pressures the commodity AUD too, so the cross is a wash and grinds from ~1.643. Stop 1.662. Hold.",
    "MM-2026-004": "RESCUED OVERNIGHT. The 10Y backed up to 4.499% at the close, then EASED to ~4.45% — back near the 4.44% entry, ~flat — as the tape began fading the hawkish overshoot. The contrarian case (oil $78 says the Fed's 3.6% forecast is too high) is getting its first confirmation; the front end is cleaner. Do NOT add. Stop 4.65%.",
    "MM-2026-005": "DID WHAT IT WAS FLAGGED TO DO. Real-rates engine reversed on the hawkish dots (gold -2% to ~$4,275 — 'first hedge to give back'), tested toward the $4,250 stop, HELD, and bounced >$4,300 on Iran. Offside from the $4,523 entry but above stop. Min-hold to ~Jul 15.",
    "MM-2026-007": "PINNED, NOT PUNISHED. The hawkish Fed widened the differential yet USDJPY held ~160.3 at the MoF line — the short is ~flat, frustrated by crushed carry. Needs vol to break it (a guidance-less Fed is now more likely to). Stop 163.00; defined-risk expression MM-021.",
    "MM-2026-008": "THE CALL OF THE DAY. The FOMC tail it was held for PAID — S&P to ~7,420 (91pts closer to 7,300) + VIX to 18.44 marked it ~$60 from ~$34 (~+70%). The catalyst passed but a hawkish, no-cuts Fed keeps the de-rating live. Hold the residual convexity into Jun-27 expiry.",
    "MM-2026-009": "GAVE BACK, STILL THE BEST STRUCTURAL POSITION. Hawkish dots bear-FLATTENED the curve (2Y +16bp vs 10Y +7bp) — spread to ~+28bp from ~+41bp, gain ~+85% from ~+157%. A Fed hiking into an oil-disinflation eventually re-steepens. Min-hold ~Jul 16; stop -10bp.",
    "MM-2026-012": "VINDICATED. The most-contested leg finally paid — a hawkish Fed vs a paused ECB broke the asymmetry, DXY ripped through 100 to ~100.5, EUR/USD sliced through 1.1550. A fresh dollar regime. Hold toward 1.13; add downside via MM-024. Stop 1.182 (distant).",
    "MM-2026-013": "THE TRADE THE FED SHOT AT — AND THE OVERNIGHT TAPE CAUGHT. The SEP penciled the 2026 hike the trade faded and the 2Y spiked to a one-year-high 4.216% at the close, but it EASED back to ~4.16% (≈the 4.162% entry) overnight — the position is roughly FLAT, not the loss the dots implied. Held on the oil-disinflation contrarian case (Brent $78 vs the Fed's 3.6%), now with a first confirming fade. Min-hold ~Jul 8; do NOT add. Stop 4.35%.",
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
    {"datum": "MM-008 option mark (model est. from spot — ~$60, S&P ~7,420 + VIX 18.4 lifted it from ~$34)", "source": "Model estimate (no live option feed)", "asof": TODAY, "stale": True},
    {"datum": "FOMC Jun 17: HELD 3.50-3.75% unanimous; 2026 median dot ~3.8% (from 3.4%) — 9 hike/8 hold/1 cut; cuts trimmed 2->1; inflation raised to 3.6%/3.3%; Warsh the only one of 19 not to submit a dot; statement shortened, cut-bias stripped; 5 task forces.",
     "source": "Federal Reserve + CNBC + NPR + Yahoo Finance (corroborated)", "asof": "2026-06-17", "stale": False},
    {"datum": "Wed Jun 17 US close: Dow 51,492.55 (-0.98%, -507.12); S&P 7,420.10 (-1.21%); Nasdaq 26,021.66 (-1.34%); tech led (MSFT/META/GOOGL/AMZN red)",
     "source": "TheStreet + CNBC (corroborated)", "asof": "2026-06-17", "stale": False},
    {"datum": "2Y +16bp to 4.216% (1-year high); 10Y +7bp to 4.499%; 2s10s bear-flattened to ~+28bp",
     "source": "CNBC (corroborated)", "asof": "2026-06-17", "stale": False},
    {"datum": "DXY broke 100 to ~100.5 (highest since early Iran war); EUR/USD -~60pips through 1.1550 toward 1.1500",
     "source": "FXStreet (corroborated)", "asof": "2026-06-17", "stale": False},
    {"datum": "Gold -~2% to ~$4,275 Jun 17 (real-rates engine reversed), held the $4,250 stop, bounced >$4,300 Jun 18 on Iran",
     "source": "Trading Economics + FXStreet (corroborated)", "asof": "2026-06-18", "stale": False},
    {"datum": "VIX +12.4% to 18.44 Jun 17 (from 16.41) — the vol re-rating the brief priced; MOVE firmer (est. ~108)",
     "source": "CBOE (corroborated)", "asof": "2026-06-17", "stale": False},
    {"datum": "Brent ~$78 (lowest since March) / WTI sub-$76 — war premium draining + a surging dollar weighing on crude",
     "source": "Trading Economics + NPR (corroborated)", "asof": "2026-06-18", "stale": False},
    {"datum": "USD/JPY ~160.3 — pinned at the MoF line despite the hawkish-Fed differential widening",
     "source": "Trading Economics (corroborated)", "asof": "2026-06-18", "stale": False},
    {"datum": "Iran deal: Trump DECLARED it 'complete' (Truth Social: 'let the oil flow'), authorized toll-free Hormuz reopening + Navy-blockade removal; digital MOU signed — but ships NOT yet sailing (NPR); formal multilateral signing PENDING Fri Jun 19 (Switzerland). 60-day toll-free Hormuz; nuclear to a 60-day negotiation.",
     "source": "CBS News + NBC News + NPR + The Hill (corroborated)", "asof": "2026-06-18", "stale": False},
    {"datum": "UK May CPI 2.8% (unchanged, BELOW 3.0% consensus; monthly +0.2%); transport +6.8% (fuel) the hawkish offset; services/housing softening",
     "source": "ONS (Office for National Statistics)", "asof": "2026-06-17", "stale": False},
    {"datum": "BoE decision TODAY Jun 18 12:00 GMT — hold at 3.75% near-unanimous (Reuters poll 65/65); watch Pill/Greene hawkish dissents vs the soft CPI; Bailey presser 12:30. PENDING.",
     "source": "Bank of England + Reuters + ING", "asof": TODAY, "stale": False},
    {"datum": "Asia Jun 18: Hang Seng / Nikkei sold off on the Fed's hawkish tone",
     "source": "FXEmpire", "asof": "2026-06-18", "stale": False},
    {"datum": "JBL (Jabil) reported Jun 17 BMO: EPS 3.16 vs 3.109 est (+1.64% beat), rev $8.751B vs $8.636B est; 13 buy/4 hold/0 sell",
     "source": "Finnhub (earnings_data.md, sourced)", "asof": "2026-06-17", "stale": False},
    {"datum": "Note: Fri Jun 19 is Juneteenth — US equity/bond markets CLOSED (same day as the MoU signing; trades Mon Jun 22)",
     "source": "NYSE holiday calendar", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-06-17", "stale": True},
]

earnings_ideas = [
    {
        "ticker": "JBL", "company": "Jabil Inc",
        "report_date": "2026-06-17", "report_timing": "BMO",
        "mode": "POST-EARNINGS", "direction": "Neutral",
        "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None,
        "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "reaction_tag": "FAIRLY PRICED",
        "eps_actual": 3.16, "eps_estimate": 3.109, "eps_surprise_pct": 1.64,
        "stock_reaction_pct": None, "implied_upside_to_pt": None,
        "key_bullets": [
            "Reported Jun 17 BMO: EPS 3.16 vs 3.109 consensus (+1.64% beat) on revenue $8.751B vs $8.636B est — a "
            "modest, fifth straight beat (prior four: 6.2%, 4.52%, 11.46%, 9.3%). Finnhub-sourced.",
            "The read-through held: the Intelligent-Infrastructure / AI-data-center segment cleared the number the "
            "morning before the hawkish Fed, evidence the build-out demand survived the early-June semis de-risk. "
            "Sell side 13 buy / 4 hold / 0 sell (period 2026-06-01).",
            "But the print is now overshadowed by the macro: a +1.64% beat is a small asymmetry, and the reaction was "
            "swamped by the FOMC repricing (a higher discount rate compresses the whole AI-infra cohort). Stock "
            "reaction and short interest unverified — positioning pillar scores 0.",
        ],
        "what_moves_it": ("Now it is the rate path, not the print. A modest beat into a hawkish-Fed tape means the "
                          "multiple, not the quarter, drives the stock — a higher-for-longer discount rate caps the "
                          "AI-infrastructure re-rating the clean guide would otherwise earn. Bull: the build-out read "
                          "carries the cohort; bear: rates compress it regardless of the beat."),
        "client_talking_point": ("Jabil beat again — its fifth straight, EPS 3.16 vs 3.11 — and the AI-infrastructure "
                                 "read held, which is the constructive signal under the noise. But it printed into a "
                                 "hawkish Fed that just penciled a hike, so the rate path is now doing more to the "
                                 "stock than the quarter. We are neutral: good company, wrong week for a small beat."),
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
        "HE DID BOTH. Warsh's first FOMC resolved into the one outcome almost no one positioned for: a HAWKISH SEP "
        "(2026 median dot ~3.8% from 3.4%, 9 of 18 see a hike, cuts trimmed 2->1, inflation raised to 3.6%/3.3%) AND "
        "a dismantled framework (he alone of 19 submitted no dot, the statement was shortened, the cut bias stripped, "
        "five task forces stood up). The tape repriced hawkish: S&P -1.21% to 7,420, Nasdaq -1.34%, the 2Y +16bp to a "
        "one-year-high 4.216%, DXY through 100, gold -2% then a bounce on Iran, VIX +12% to 18.44. The book's calls "
        "graded out: long vol (MM-020) and the put spread (MM-008) won, gold gave back exactly as flagged, the short "
        "EUR/USD finally paid, and the discipline of not adding into the print kept the duration give-back to a "
        "give-back. Now the collision: a Fed that just raised its inflation forecast to 3.6% in the same week Brent "
        "broke $78 on the Iran deal. Today is the first test of a guidance-less Fed — the BoE holds into a soft UK "
        "CPI, and every US print is now its own vol event. Friday is Juneteenth; the Iran signing trades Monday."
    ),

    "summary_narrative": """
<p>The event the entire tape was built around resolved, and the new chair did the one thing almost no one was
positioned for: <strong>both</strong>. The FOMC held at 3.50&ndash;3.75% unanimously, but the projections turned
hawkish &mdash; the 2026 median dot jumped to roughly <strong>3.8% from 3.4%</strong> in March, nine of eighteen
officials now see a hike this year, the 2026 cut count was trimmed from two to one, and the inflation forecast was
<strong>raised to 3.6% headline and 3.3% core</strong> from 2.7%. And Warsh dismantled the framework around it: he
was the only one of nineteen officials not to submit a dot, the statement was sharply shortened with the cut-bias
language stripped, and he stood up five task forces to overhaul communications and the balance sheet. A Fed that is
hawkish and opaque at once. (Federal Reserve, CNBC, NPR.)</p>

<p>The tape repriced hard. The Dow fell 0.98% to 51,492.55, the S&amp;P 500 dropped 1.21% to 7,420.10, and the
Nasdaq Composite fell 1.34% to 26,021.66 &mdash; tech led the losses, with Microsoft, Meta, Alphabet and Amazon all
red, as a higher-for-longer path compressed the long-duration multiple. The 2Y yield <strong>rocketed sixteen basis
points to 4.216%</strong>, its highest in over a year; the 10Y rose seven to 4.499%; the curve bear-flattened to
roughly +28bp. The dollar broke a figure &mdash; DXY ripped through <strong>100</strong> to ~100.5, its highest
since the early days of the Iran war, and EUR/USD sliced sixty pips through 1.1550 toward 1.1500. (TheStreet,
FXStreet.)</p>

<p>The book's own calls graded out exactly as written. The long-vol idea (MM-020) and the SPX put spread (MM-008)
were the winners as VIX jumped 12% to <strong>18.44</strong>; gold did precisely what it was flagged to do &mdash;
reversed 2% on the hawkish dots as &ldquo;the first hedge to give back,&rdquo; tested toward its $4,250 stop, held,
and bounced above $4,300 Thursday on the Iran headlines; the duration longs and the steepener gave back, but the
discipline of not adding into the print kept the damage to a give-back, not a loss. The most-contested leg &mdash;
short EUR/USD &mdash; finally paid as the dollar broke 100. (CBOE, Trading Economics.)</p>

<p>Oil kept falling into all of it. Brent fell toward <strong>$78</strong>, its lowest since March, and WTI below
$76, as Trump declared the Iran deal &ldquo;complete,&rdquo; posted &ldquo;let the oil flow,&rdquo; and authorized
the toll-free reopening of Hormuz and the removal of the Navy blockade &mdash; yet the ships are not actually
sailing, and the formal multilateral signing is still <strong>pending Friday</strong> in Switzerland. That is the
collision that defines the next forty-eight hours: a Fed that just raised its inflation forecast to 3.6% in the same
week oil broke $78 on a peace deal. One of them is wrong about the next six months. (CBS News, NBC News, NPR.)</p>

<p>Today is the first test of a Fed with no guidance. The Bank of England holds at noon London into a soft UK CPI
(May 2.8%, below the 3.0% consensus), and US jobless claims and the Philly Fed land into a market that now treats
every print as its own volatility event &mdash; the structurally higher vol floor is no longer a forecast, it printed
at 18.44. The posture stays two-sided: the winners are banked or held, the duration longs are flagged offside but
inside their stops and min-holds, and the fresh ideas own the new regime &mdash; rate vol, the dollar breakout, the
financials-over-tech rotation &mdash; not a fight with it. Friday is Juneteenth; US markets are closed, so the Iran
signing trades Monday.</p>
""",

    "takeaways": [
        "<strong>Warsh did both &mdash; hawkish dots AND no guidance.</strong> The FOMC held 3.50-3.75% unanimously, "
        "but the SEP turned hawkish: the 2026 median dot jumped to ~3.8% (from 3.4%), 9 of 18 see a hike, cuts were "
        "trimmed 2->1, and inflation forecasts were raised to 3.6%/3.3%. Warsh alone of 19 submitted no dot, shortened "
        "the statement, stripped the cut bias, and launched 5 task forces. (Fed, CNBC, NPR.)",

        "<strong>The tape repriced hawkish across every asset.</strong> S&amp;P -1.21% to 7,420.10, Nasdaq -1.34% to "
        "26,021.66 (tech led: MSFT/META/GOOGL/AMZN red); the 2Y +16bp to a one-year-high 4.216%; the 10Y to 4.499%; "
        "the curve bear-flattened to ~+28bp; DXY broke 100 to ~100.5. The hawkish-dots bear case the brief flagged at "
        "20% is what printed. (TheStreet, FXStreet.)",

        "<strong>The book's calls graded out.</strong> Long vol (MM-020) and the SPX put spread (MM-008, ~+70% to "
        "~$60) were the winners as VIX jumped 12% to 18.44. Gold reversed 2% to ~$4,275 exactly as flagged ('first "
        "hedge to give back'), held the $4,250 stop, and bounced on Iran. Short EUR/USD (MM-012) finally paid. The "
        "duration give-back was contained by not adding into the print. (CBOE.)",

        "<strong>The collision: a 3.6% inflation forecast vs $78 oil.</strong> The Fed raised its inflation outlook to "
        "3.6% the same week Brent broke $78 on the Iran deal. The bond market sold off on the dots; the oil tape says "
        "the Fed is tightening into a disinflation. One of them is wrong about the next six months &mdash; and that is "
        "the live tension in the duration longs (MM-013/004), held on the oil-disinflation contrarian case. (Trading "
        "Economics, NPR.)",

        "<strong>The guidance vacuum is the structural trade.</strong> A Fed with no forward path hands the term "
        "premium back to the market &mdash; the 10Y backed up on a 'hold,' and rate vol (MOVE) is the cleaner read "
        "than equity vol. Every data point is now its own catalyst. The fresh expression is long rates vol (MM-023); "
        "the Burry tell of a permanently higher vol floor just printed at 18.44.",

        "<strong>The dollar broke 100 &mdash; a fresh regime.</strong> DXY through the figure to ~100.5 (highest since "
        "the early Iran war) on the hawkish Fed vs a paused ECB is a technical breakout, not a spike. Short EUR/USD "
        "(MM-012) is vindicated; the defined-risk way to add is a EUR/USD 1.14/1.12 put spread (MM-024). A higher-for-"
        "longer Fed also rotates financials over long-duration tech (MM-025).",

        "<strong>The Iran peace is declared, not signed.</strong> Trump called the deal 'complete' and authorized "
        "Hormuz's toll-free reopening, but the ships are not sailing and the formal signing is pending Friday in "
        "Switzerland &mdash; on Juneteenth, with US markets closed. Israel remains the live wildcard. The asymmetry of "
        "a deal that slips &mdash; Brent back toward $90+ &mdash; is large, unpriced, and trapped behind the holiday "
        "until Monday. (CBS, NBC, NPR.)",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "30%",
         "headline": "The hawkish repricing was a one-day overshoot — soft data + oil pull it back",
         "body": "Today's jobless claims/Philly Fed come soft, the Iran deal holds, and the market fades the "
                 "hawkish-dot overshoot: the 2Y eases back from 4.22%, the dollar consolidates below 100.5, gold "
                 "extends its Iran bounce, and equities stabilise as the rotation broadens (RSP/financials lead). The "
                 "duration longs (MM-013/009) recover and the oil-disinflation argues the Fed's 3.6% forecast was the "
                 "overshoot. Risk up (broad) · rates down · dollar soft · oil down · gold up."},
        {"kind": "base", "label": "Base", "pct": "50%",
         "headline": "Higher-for-longer holds — rate vol elevated, dollar firm, rotation continues",
         "body": "The hawkish repricing sticks: the 2Y holds ~4.15-4.25%, the dollar consolidates its break of 100, "
                 "rate vol (MOVE) stays bid in the guidance vacuum, and the rotation out of long-duration tech into "
                 "financials grinds on (MM-025/022). Each data print is a discrete vol event; equities chop sideways "
                 "with a lower ceiling. Gold's two engines offset. Risk mixed · rates steady-to-firm · dollar firm · "
                 "oil soft · gold flat · VIX/MOVE elevated."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "The hawkish repricing extends OR the Iran deal fractures pre-signing",
         "body": "Hot claims/Philly Fed or hawkish Fed-speak confirm the hike and the 2Y runs to the 4.35% stop, the "
                 "dollar accelerates, AI multiples compress further and the S&amp;P retraces toward 7,200-7,000 where "
                 "the put spreads (MM-008) pay; AND/OR Israel fractures the deal before Friday and Brent snaps back "
                 "toward $90+, reversing the disinflation read into a hawkish-Fed-plus-oil-spike squeeze. Risk down · "
                 "rates up · dollar up · oil up · gold mixed."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a single repricing: the market spent two weeks debating whether the dots would
arrive, and the new chair delivered hawkish dots and then dismantled the framework that produces them. A unanimous
hold became a hawkish event because the projections did the work &mdash; the 2026 median dot up to roughly 3.8%, the
inflation forecast lifted to 3.6%, the cut bias stripped &mdash; and the 2Y rocketing to a one-year high is the
market pricing a September hike it did not believe a week ago. The non-consensus read is that the more important
change is the one with no number on it: a Fed that no longer pre-commits a path is a structurally higher-vol Fed, and
the cleanest expression of that is not a rates direction but rate volatility itself (MM-023).</p>

<p>The counter-intuitive hook is the collision the same week produced. The Fed raised its inflation forecast to 3.6%
&mdash; its most hawkish signal &mdash; in the very days Brent broke $78 on a peace deal, the most disinflationary
macro force on the board. Consensus is treating the hawkish Fed as the new regime and selling duration into it;
twenty-four hours of falling oil says the Fed is tightening into a disinflation it has not yet acknowledged. The
headline says higher-for-longer; the oil tape says the 3.6% number is backward-looking. One of them is wrong about
the next two quarters, and that gap is exactly why the duration longs are held, not folded, even offside.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong>
Brent at $78, a soft UK CPI at 2.8%, gold holding its floor, the AI-capex cycle funded increasingly by debt.
<strong>What is priced:</strong> a 2Y at a one-year high pricing a September hike, a dollar through 100, and a VIX
re-rated to 18.4 that now respects event risk. <strong>Consensus narrative:</strong> &lsquo;Warsh is a hawk and the
Fed is higher-for-longer, full stop.&rsquo; The gap &mdash; and the alpha &mdash; is that the consensus has fully
embraced the hawkish level and is ignoring the guidance vacuum and the oil-disinflation, both of which argue the next
surprise is a higher-vol, lower-conviction Fed, not a linear hiking cycle.</p>

<p>Go around the world. <strong>US:</strong> the repricing led everything &mdash; yields, dollar, and a tech-led
equity de-rating. <strong>Japan:</strong> the BoJ hiked to 1% last week and the yen still sits pinned at 160, now
braced against a wider hawkish-Fed differential &mdash; the carry coil tighter, not looser (MM-021).
<strong>Asia:</strong> Hang Seng and the Nikkei sold off on the Fed's hawkish tone, importing the US repricing.
<strong>UK:</strong> the one place the data is undercutting the hawks &mdash; May CPI at 2.8%, below consensus, into
a BoE that holds today, a clean rate-divergence trade (MM-026).</p>

<p>The political angle the market is under-weighting runs on two fault lines. On the Fed, the constraint is the
Trump-Warsh relationship: the President said a hike &ldquo;would be wrong&rdquo; the day before, and a new chair
penciled one in and dropped his own dot to establish independence &mdash; a hawkish-by-design debut that makes the
Fed a political vol source into 2026, not a settled one. On Iran, the binding constraint remains Jerusalem and the
gap between declaration and reality: Trump says &ldquo;let the oil flow,&rdquo; but the ships are not sailing, the
signing is Friday, and Israel can still break it &mdash; the oil market has front-run a signature a third party has
not given.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the guidance-vacuum rate-vol re-rating (MOVE); the oil-
disinflation that contradicts the Fed's 3.6%; the Iran-slippage tail trapped behind the holiday. <strong>Fairly
priced:</strong> the hawkish level itself (2Y at a one-year high); the dollar break of 100; the BoE hold.
<strong>Fully priced:</strong> the straight-line peace move in oil (Brent $78 has front-run an unsigned deal).
<strong>Over-priced (at risk):</strong> the consensus that higher-for-longer is now a settled, linear regime &mdash;
when the chair just made the Fed less predictable, not more.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is not in the hawkish dots everyone is now trading. It
is that the hawkish dots and the dismantled guidance are the same event, and only one of them has a number on it. The
market has spent the night repricing a September hike &mdash; the 2Y at a one-year high, the dollar through a figure,
gold knocked off its perch. All of that is the level. The change with no level is the one that lasts: a chair who
dropped his own dot, shortened the statement, stripped the bias and stood up a task force on communications has told
you the Fed will say less from here. A Fed that says less is not a hawkish Fed or a dovish one. It is a louder one,
and the bond market heard it first &mdash; the ten-year backed up on a hold.</p>

<p>Start with what graded out, because the discipline is the story. The brief went into the meeting with one
instruction: own the variance, not the number, and do not add directional macro into the print. The long-vol idea and
the put spread were the winners as the VIX jumped twelve percent; the short-euro leg that had been contested for two
weeks finally paid as the dollar broke a hundred; and gold did the exact thing it was flagged to do &mdash; reversed
on the hawkish dots as the first hedge to give back, tested its stop, held, and caught a bid on the Iran headlines.
The positions that hurt &mdash; the front-end long, the ten-year, the steepener &mdash; gave back rather than broke,
because none of them were added the day of the event. A bad outcome on a disciplined book is a give-back. The same
outcome on a chased book is a stop-out.</p>

<p>Then the collision that defines the next two days. The Fed raised its inflation forecast to three-point-six in the
same week Brent broke seventy-eight dollars on a peace deal. Those two facts cannot both describe the next two
quarters. Either the oil-disinflation is real and the Fed is tightening into it &mdash; a policy error the front end
eventually reverses &mdash; or the inflation the Fed sees is sticky enough that cheaper oil is a rounding error. The
duration longs are the expression of the first view, and they are held offside precisely because the oil tape is
screaming the Fed's number is backward-looking. That is a contrarian bet against a fresh hawkish print, and it is
sized as one: held, flagged, not added, inside its stops and its min-holds.</p>

<p>The fresh ideas all come from the new regime rather than a fight with it. If a guidance-less Fed re-widens the
term premium, the cleanest trade is long rates volatility, not a rates direction &mdash; own the MOVE, not the
ten-year. If the dollar broke a hundred on a real rate-path asymmetry, the disciplined way to add is a defined-risk
euro put spread, not chasing spot at the figure. And if the Fed is higher-for-longer with the cut bias gone, the
rotation is mechanical: financials earn the wider margin while long-duration tech pays the higher discount rate, so
long the banks against the chips. The one place the data leans the other way is Britain, where a soft inflation print
into a hold today is a clean reason to own gilts as US yields back up.</p>

<p>So the posture into the back half of the week is the same two-sided discipline, re-pointed at the resolved event.
The winners are banked or held with their stops trailed up; the offside duration is held on a falsifiable thesis with
a hard stop; the new ideas own the vol regime, the dollar breakout, the rotation, and the UK divergence. The tape has
priced a hawkish Fed as a settled fact, a clean peace in oil, and a vol that re-rated once and stops. The brief's
read is that the hawkish Fed just made itself less predictable, the peace is a declaration a third party can break,
and eighteen-and-a-half is a floor, not a ceiling. Friday is Juneteenth, the desk is dark, and the next chapter is
written Monday.</p>
""",

    "correlation_regime": """
<p><strong>1. Stocks and bonds re-coupled to the downside &mdash; the hawkish-Fed regime.</strong> Equities fell and
yields rose together as the SEP turned hawkish &mdash; the classic higher-discount-rate correlation that dominates
when the Fed, not growth, is the driver. The dominant driver is now unambiguously the rate path: a 2Y at a one-year
high pulled the long-duration multiple down (Nasdaq -1.34%, tech leading). The trade that respects this is financials
over tech (MM-025) and long rate vol (MM-023), not a dip-buy.</p>

<p><strong>2. Gold's two engines decoupled inside one day.</strong> Gold fell 2% on the hawkish dots (real-rates
engine) then bounced above $4,300 on the Iran headlines (safe-haven / dollar-debasement engine) &mdash; the same
asset trading two different stories twelve hours apart. The break tells you gold is no longer a clean real-rates
short or a clean haven long; it is a two-sided hold (MM-005), which is exactly why it is sized as a min-hold position
rather than a conviction add here.</p>

<p><strong>3. The dollar decoupled from oil's direction.</strong> Normally a falling oil price (disinflation) and a
hawkish dollar pull rates the same way; Wednesday they split &mdash; the dollar ripped on the Fed while oil fell on
Iran, two disinflationary forces pointing at the same destination from opposite drivers. The 'good' read is that both
argue the Fed's 3.6% inflation forecast is too high; the dollar break of 100 (MM-012/024) and the duration longs
(MM-013) are the two sides of the same disinflation, even as one is working and one is offside.</p>
""",

    "vol_skew": """
<p><strong>The vol re-rating printed &mdash; and rate vol is the cleaner expression than equity vol now.</strong> VIX
jumped 12.4% to 18.44 on the hawkish FOMC (from 16.41), and the term structure flattened toward backwardation at the
front as event risk was finally respected (est. VIX9D ~18.0 · VIX ~18.4 · VIX3M ~19.5 · VIX6M ~20.5). The long-vol
idea (MM-020) and the SPX put spread (MM-008) paid into it. But the structural read points to the bond market: a
guidance-less Fed re-widens the term premium and lifts MOVE (est. ~108, firmer) more durably than VIX, because the
guidance Warsh dismantled was a rates tool, not an equity one. The trade implication: rotate the vol length from
equity toward rates &mdash; own a long-bond (TLT) straddle or long MOVE (MM-023). The one options structure that fits
today's regime is a defined-risk EUR/USD 1.14/1.12 put spread (MM-024): it owns the dollar breakout below 100 with a
known max loss, struck for continuation rather than a chase at the figure. If the hawkish repricing proves a one-day
overshoot, equity vol mean-reverts lower &mdash; but rate vol stays bid as long as the Fed gives no path.</p>
""",

    "sector_rv": """
<p><strong>Leading (Wed Jun 17):</strong> financials and rate-sensitive value (the Dow fell least, -0.98%);
transports/airlines on sub-$78 fuel; the Dow's relative outperformance the first leg of the higher-for-longer
rotation. <strong>Lagging:</strong> mega-cap / long-duration tech (Nasdaq -1.34%, Microsoft/Meta/Alphabet/Amazon all
red) as the higher discount rate compressed the multiple; gold miners on the bullion give-back; the broad Nasdaq.
<strong>Today's watch:</strong> the BoE 12:00 GMT (UK financials/Gilts) and US claims/Philly Fed &mdash; each a
discrete vol event in the guidance vacuum. FedEx (Jun 23) and Micron (Jun 24) are next.</p>

<p><strong>RV:</strong> The cleanest fresh sector RV is long XLF (financials) / short XLK (tech) (MM-025) &mdash; a
hawkish, no-cuts Fed lifts net-interest margins while it compresses the long-duration multiple, the rate-regime
version of the breadth RV (MM-022, long RSP / short QQQ) that traded the concentration. Both are low beta to the
index level and high beta to the higher-for-longer repricing. The transports-vs-energy RV (MM-019) remains live as
Brent at $78 plus a surging dollar reprices the two sectors in opposite directions.</p>
""",

    "positioning": """
<p><strong>The crowd just got the hawkish level it feared &mdash; and is now maximally positioned for it.</strong>
Post-Warsh, fast money is short duration, long dollar, and short long-duration tech, all expressions of
higher-for-longer. The 2Y at a one-year high and the dollar through 100 mean the consensus has converged hard on the
hawkish read &mdash; which makes the pain trade a SOFT data print today (claims/Philly Fed) that unwinds the overshoot
and squeezes the fresh duration shorts, exactly the contrarian setup the offside front-end long (MM-013) is built to
catch. In equities, the rotation out of mega-cap tech into financials is early; the pain trade is a continued
broadening that strands the index-tracking longs in the wrong names (MM-022/025). In FX, the yen carry trade stayed
crowded long-USD even through a BoJ hike, now braced against a wider differential at the MoF line (MM-021). The single
position the re-rated VIX is still wrong on is short rate vol into a chair who just removed the Fed's forward path
&mdash; that is where the term premium does the squeezing (MM-023).</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; a unanimous hold does not move the funding rate.
<strong>The Pozsar mechanic:</strong> the plumbing signal that matters is the one Warsh just changed. Forward
guidance is, mechanically, a term-premium compressor &mdash; it tells the market the path of the funding rate, which
anchors the long end. By dropping his dot, shortening the statement and standing up a balance-sheet task force, Warsh
removed that anchor, and the 10Y backing up to 4.499% on a hold is the term premium widening not because inflation
rose but because the Fed stopped pre-committing the path. That is the mechanism behind a higher MOVE without a higher
policy rate, and it is why rate vol (MM-023) is the cleaner read on this regime than equity vol. The balance-sheet
task force is the one to watch next: any signal on the pace of QT or the reserve floor feeds directly into bill
supply and the term premium. Watch the long end and the MOVE index on every data print now &mdash; in a guidance
vacuum, the bond market reprices the path itself, one number at a time.</p>
""",

    "tape_missing": """
<p><strong>The tape is pricing the hawkish level and ignoring the guidance vacuum.</strong> The market has fully
embraced higher-for-longer &mdash; 2Y at a one-year high, dollar through 100 &mdash; but is treating it as a settled,
linear regime. The change that lasts is that Warsh removed the Fed's forward path: every CPI, payroll and claims print
is now a discrete catalyst, and the term premium does the repricing one number at a time. The immediate read is
neither hawkish nor dovish &mdash; it is higher rate vol. MOVE (est. ~108) is barely pricing it. Long rates vol
(MM-023) is the instrument.</p>

<p><strong>Just behind it: the Fed raised its inflation forecast into a falling-oil disinflation.</strong> The SEP
lifted 2026 inflation to 3.6% the same week Brent broke $78 on the Iran deal. Either cheaper oil feeds through and the
Fed is tightening into a disinflation it has not acknowledged &mdash; the front end reverses &mdash; or the inflation
is sticky enough that oil is noise. The duration longs (MM-013/004) are the falsifiable expression of the first view;
the level that proves it wrong is the 2Y through 4.35%. And the peace itself is a declaration, not a signature:
Trump says &ldquo;let the oil flow,&rdquo; but the ships are not sailing, the signing is Friday, and Israel can break
it &mdash; a three-day headline gap behind a market holiday.</p>

<p><strong>The Burry tell &mdash; the structural thing that just stopped being a forecast.</strong> For fifteen years
the Fed's primary shock absorber was forward guidance: the promise to telegraph the path, which compressed the term
premium and turned the central bank into a calendar-anchored backstop. Yesterday a chair who has attacked guidance for
a decade began removing it &mdash; he dropped his own dot, shortened the statement, and stood up a communications task
force. The structural consequence is no longer a thesis; the first evidence printed: the 10Y backed up on a hold and
the VIX re-rated 12% to a level it had not held all cycle. Over the next two-to-three quarters this resolves as a
permanently higher vol floor &mdash; a world where a hot CPI or a soft payroll moves markets the way it did before
2009, because the Fed no longer pre-commits to absorb it. The equity market, with an index still concentrated in
seven names that just led the losses, is the least prepared for that regime. It is the reason to be structurally long
volatility &mdash; and increasingly rate volatility (MM-023) over equity volatility &mdash; as the regime announces
itself.</p>
""",

    "book_outlook": {
        "commentary": (
            "Yesterday's repricing ran straight through the Fable book's two-sided structure &mdash; and the hedges did "
            "their job. The book's <b>US AI-semis concentration (Micron ~25.8%, plus NVDA/AVGO/AMD)</b> took the brunt "
            "of the hawkish de-rating: a higher-for-longer rate path with the cut bias stripped compresses the "
            "long-duration multiple, and the Nasdaq -1.34% (MSFT/META/GOOGL/AMZN leading) is the cohort the book is "
            "levered to. That is why a 25.8% single-name weight into <b>Micron earnings Jun 24</b> &mdash; six sessions "
            "after a Fed that raised its inflation forecast &mdash; is the book's defining risk to manage NOW, not its "
            "edge. The disinflation/real-rates side cut the other way: <b>Xetra-Gold (4GLD)</b> gave back ~2% on the "
            "hawkish dots before the Iran bounce caught it, and the <b>US Treasury 1.25% 2031</b> and <b>Siemens EUR "
            "IG</b> bonds sold as the 2Y hit a one-year high and the 10Y backed up &mdash; duration losses, not credit. "
            "But the book has genuine winners in the new regime: <b>SAP</b> and quality European software outrun the "
            "US semis stack as rates rise, and the EUR-base book's heavy <b>USD sleeve (~72%)</b> just gained as DXY "
            "broke 100. <b>TotalEnergies (TTE)</b> keeps bleeding as Brent breaks $78. The dominant action: collar the "
            "Micron concentration before the print, and finally hedge the USD sleeve into a dollar that has broken out "
            "&mdash; a higher-for-longer Fed is the regime the book's concentration is least suited to."
        ),
        "outperform": [
            {"name": "USD cash sleeve / USD assets (~72% of the book)", "why": "The EUR-base book is ~72% USD and the "
             "dollar just broke 100 to a multi-month high on the hawkish Fed &mdash; the FX translation is a tailwind "
             "for the first time in weeks. The book is structurally long the asset that won yesterday."},
            {"name": "SAP / European software", "why": "A higher-for-longer Fed re-rates quality, cash-generative "
             "software over speculative long-duration US semis; SAP (+132%) carries none of the AI-multiple "
             "compression that hit the NVDA/AVGO/MU stack, and pairs with the financials-over-tech rotation (MM-025)."},
            {"name": "Xetra-Gold (4GLD) — the bounce, not the dots", "why": "Gold gave back on the hawkish dots but "
             "the Iran-durability / dollar-debasement engine caught it above $4,300; as the book's tail hedge it held "
             "its floor and remains the one position that is both a hedge and a long-term winner."},
        ],
        "underperform": [
            {"name": "US AI-semis (Micron 25.8%, NVDA/AVGO/AMD)", "why": "Took the brunt of the hawkish de-rating &mdash; "
             "a higher discount rate compresses the long-duration multiple, and the cohort led the Nasdaq's -1.34%. "
             "Into MU earnings Jun 24, the 25.8% concentration is the risk to collar, not the conviction to add."},
            {"name": "The bond sleeve (UST 1.25% 2031, Siemens EUR IG)", "why": "Both sold as the 2Y hit a one-year "
             "high and the 10Y backed up on the hawkish SEP and the guidance-vacuum term-premium widening &mdash; "
             "duration losses, not credit. The bond-swap entry improves, but a hawkish surprise is the better harvest."},
            {"name": "TotalEnergies (TTE)", "why": "The energy hedge keeps rolling over as Brent breaks $78 (lowest "
             "since March) on the Iran deal, with a surging dollar a second drag on USD-priced crude. The clean weekly "
             "drag on the book."},
        ],
        "watch": [
            {"label": "Collar the 25.8% Micron concentration NOW — the print is six sessions out and rates just rose",
             "text": "MU at 25.8% into earnings Jun 24, with IVol elevated and a higher discount rate freshly "
             "compressing the AI-memory multiple, is the most urgent action on the book. A collar (rich calls finance "
             "fat puts) caps the print risk for near-zero cost; the SPX put spread (MM-008, which just paid ~+70%) is "
             "the index overlay. Do not wait."},
            {"label": "Hedge the USD sleeve INTO the breakout — but the dollar just turned in the book's favour",
             "text": "The EUR-base book is ~72% USD and DXY just broke 100. The translation is a tailwind today, but a "
             "fresh dollar regime is exactly when to put on a cheap seagull/collar to lock some of the gain before the "
             "Iran-signing risk-on (the EUR-supportive offset). The EUR/USD put spread logic (MM-024) is the book "
             "version."},
            {"label": "The bond sleeve: a guidance-less Fed means the swap timing is now data-by-data", "text": "The "
             "UST 2031 and Siemens IG both sold on the hawkish dots, improving the loss-harvest entry. But in a "
             "guidance vacuum every print moves the long end &mdash; do not swap into a single data day; ladder the "
             "harvest across the next two prints (claims today, then PCE) and roll into current coupons on a "
             "yield-up spike, not a rally."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> Warsh is a hawk, the dots prove it, and the Fed is now unambiguously
higher-for-longer &mdash; sell duration, buy the dollar, fade rate-sensitive equities, and treat the September hike as
the base case. The 2Y at a one-year high and the dollar through 100 are the start of a linear repricing toward a Fed
that hikes again this year.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> the consensus has embraced the hawkish level and
ignored the two things that make it unstable &mdash; the guidance vacuum and the oil-disinflation. A Fed with no
forward path is not a more hawkish Fed, it is a less predictable one, so the next surprise is higher rate vol, not a
cleaner hiking cycle. And a 3.6% inflation forecast set the same week oil broke $78 is a number the tape is already
contradicting. The crowded side is short duration into a guidance-less Fed on a backward-looking inflation print; the
cheaper side is long rate vol and a falsifiable contrarian duration long.</p>
""",

    "one_chart": """
<p class="theme">The 2Y is the chart &mdash; it spiked to a one-year-high 4.216% on the dots, then eased to ~4.16% overnight. Which one holds?</p>
<p>The single thing the market watches today is whether the 2Y holds its hawkish break. It rocketed to 4.216% at
Wednesday's close &mdash; pricing a September hike the market did not believe a week ago &mdash; but it has already
eased back toward ~4.16% (the front-end long's entry) overnight as the tape begins fading the overshoot, the first
data-supported hint the duration longs' contrarian thesis has legs. A soft jobless-claims or Philly-Fed print extends
that fade and squeezes the fresh duration shorts; a hot print sends the 2Y back toward the 4.35% level where the
front-end long (MM-013) stops and the September hike becomes the base case. But the deeper signal is the 10Y and the MOVE
index: in the guidance vacuum, watch whether the term premium keeps widening on data &mdash; a 10Y that backs up on a
SOFT print is the tell that the guidance Warsh removed, not the inflation he forecast, is now driving the long end.
Own the binary in rate vol (MM-023), not a rates direction, until the data resolves it.</p>
""",

    "catalyst_calendar": [
        {"day": "Wed", "date": "Jun 17 ✓",
         "event": "Warsh's first FOMC — hawkish dots AND dismantled guidance; the tape repriced hawkish",
         "consensus": "Held 3.50-3.75% unanimous; 2026 median dot ~3.8% (from 3.4%), 9 hike/8 hold/1 cut, cuts trimmed "
                      "2->1, inflation raised to 3.6%/3.3%; Warsh alone of 19 submitted no dot, shortened the "
                      "statement, stripped the cut bias, launched 5 task forces. S&P -1.21% to 7,420; 2Y +16bp to "
                      "4.216%; DXY through 100; VIX +12% to 18.44. Sources: Fed, CNBC, NPR, TheStreet, FXStreet.",
         "view": ("The hawkish-dots bear case (20%) printed AND the guidance vacuum opened — both at once. The book's "
                  "long vol (MM-020) and put spread (MM-008) won; short EUR/USD (MM-012) paid; gold gave back as "
                  "flagged; duration gave back but the no-add discipline held."),
         "asymmetry": "Resolved as a hawkish-AND-opaque Fed. The lasting change is the guidance vacuum (higher rate "
                      "vol), not the level — own MOVE over the 10Y (MM-023).",
         "dir": "down"},
        {"day": "Thu", "date": "Jun 18 — TODAY",
         "event": "Bank of England decision (12:00 GMT) + US jobless claims / Philly Fed",
         "consensus": "BoE expected to HOLD Bank Rate at 3.75% (Reuters poll 65/65); watch Pill/Greene hawkish "
                      "dissents vs the soft May CPI (2.8%, below 3.0%). Bailey presser 12:30 GMT. US weekly jobless "
                      "claims + Philadelphia Fed manufacturing. Sources: Bank of England, ONS, Reuters.",
         "view": "First test of a guidance-less Fed: each US print is now a discrete vol event. A soft claims/Philly "
                 "Fed unwinds the hawkish overshoot and squeezes duration shorts; a hot print confirms the hike. The "
                 "BoE hold into a soft CPI is the clean rate-divergence trade (long Gilts, MM-026).",
         "asymmetry": "A soft US data print squeezes the fresh short-duration crowd (MM-013). A near-unanimous "
                      "dovish-leaning BoE hold pulls Gilts down as US yields back up — MM-026.",
         "dir": "flat"},
        {"day": "Fri", "date": "Jun 19",
         "event": "US-Iran MoU formal signing (Switzerland) — US markets CLOSED (Juneteenth)",
         "consensus": "Formal multilateral signing scheduled in Switzerland after Trump declared the deal 'complete' "
                      "and authorized the toll-free Hormuz reopening; ships not yet sailing. Strait toll-free 60 days. "
                      "US equity/bond markets closed for Juneteenth. Sources: CBS, NBC, NPR, Swiss FDFA.",
         "view": ("PENDING. A clean signing = oil holds $75-80, disinflation confirmed. The live risk is Israel — the "
                  "binding constraint is Jerusalem, not Tehran, and 'complete' is a declaration a third party has not "
                  "signed. US markets are closed, so the tape cannot react until Monday — a three-day headline gap."),
         "asymmetry": "Clean signing = lower-for-longer oil. Israel breaks it / it slips = Brent back toward $90+, the "
                      "disinflation read reverses into a hawkish-Fed-plus-oil-spike squeeze. Large, unpriced, behind a holiday.",
         "dir": "down"},
        {"day": "Mon", "date": "Jun 22",
         "event": "US markets reopen — the Iran signing + two-day headline gap trade at once",
         "consensus": "First US session after Juneteenth and the scheduled Iran signing; the weekend's Middle East "
                      "headlines and any signing/slippage repriced in one open. Source: market calendar.",
         "view": "The compression trade: three days of Iran headlines with no price discovery resolve at Monday's "
                 "open. A clean deal gaps oil lower and risk higher; a fracture gaps Brent toward $90 and reverses the "
                 "disinflation read into the hawkish Fed.",
         "asymmetry": "Gap risk both ways behind a closed-market weekend — the cheapest convexity is owned, not chased "
                      "(the held put spread MM-008, the rate-vol straddle MM-023).",
         "dir": "flat"},
        {"day": "Tue", "date": "Jun 23",
         "event": "FedEx (FDX) earnings — after close",
         "consensus": "FedEx reports AMC — the global-freight read on goods demand and the tariff/cost picture into a "
                      "hawkish-Fed, sub-$78-oil tape. Source: company calendar.",
         "view": "The bellwether on whether the consumer/goods cycle is slowing into the higher-for-longer rate path — "
                 "a soft guide reinforces the disinflation read the duration longs need.",
         "asymmetry": "A weak FedEx guide is a forward-disinflation signal that helps the offside front-end long "
                      "(MM-013); a strong one validates the Fed's hawkish hold.",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 24",
         "event": "Micron (MU) FY Q3 — after close (BOOK-CRITICAL)",
         "consensus": "Reports Jun 24 AMC. The book's LARGEST position (~25.8%) and the HBM/AI-memory bellwether; "
                      "IVol elevated, now into a higher-discount-rate tape. GS PT doubled to 900 into the print. "
                      "Source: company calendar / Finnhub.",
         "view": "Two-sided and book-defining: HBM sold out into the supercycle is the bull, but a 25.8% weight into a "
                 "high-IVol print the week after a hawkish Fed is a risk-management problem first. Collar before the event.",
         "asymmetry": "A beat-and-raise extends the supercycle; a guide wobble on a 25.8% concentration into a "
                      "rate-compressed multiple is the book's largest single-name drawdown risk. The collar is the trade.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660. At ~1.643; stop 1.662. Quiet leg — a hawkish-Fed risk-off pressures the commodity AUD too, so the cross is a wash and grinds. Hold.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.45% — backed up to 4.499% at the close, then eased back near the 4.44% entry (~flat) as the overshoot faded. The contrarian oil-disinflation case got its first confirmation; the front end is cleaner. Do NOT add. Hold.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250. At ~$4,300. Real-rates engine reversed on the dots (-2% to ~$4,275, 'first hedge to give back'), HELD the stop, bounced on Iran. Two-sided hold. Hold.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160.3. PINNED at the MoF line despite the hawkish-Fed differential widening — ~flat, frustrated by crushed carry. Needs vol to break it (now likelier in the guidance vacuum). Defined-risk expression MM-021. Hold.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> S&P ~7,420 → marked ~$60 (~+70%). THE CALL OF THE DAY — the FOMC tail paid. The catalyst passed but a hawkish, no-cuts Fed keeps the de-rating live; hold the residual convexity into Jun-27 expiry.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+28bp (gave back from ~+41bp); target +60bp. Bear-flattened on the hawkish dots but still ~+85%. A Fed hiking into disinflation eventually re-steepens. Hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. At ~1.150. VINDICATED — the dollar broke 100 on the hawkish Fed vs a paused ECB. A fresh regime. Hold toward 1.13; add downside via MM-024.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold to ~Jul 8. At ~4.16% — the trade the Fed shot at (penciled the 2026 hike it faded); the 2Y spiked to 4.216% at the close then eased to ~the 4.162% entry overnight, so ~FLAT. Held on the oil-disinflation contrarian case (Brent $78 vs the Fed's 3.6%); first confirming fade. Do NOT add. Hold.</li>
</ul>
""",

    "client_ammo": [
        {"q": "What actually happened at Warsh's first Fed meeting?",
         "a": ("He did both of the things the market thought were alternatives. The projections turned hawkish &mdash; "
               "the 2026 dot rose to about 3.8%, nine of eighteen officials now see a hike, and the inflation forecast "
               "was raised to 3.6%. And he dismantled the guidance around it: he was the only official not to submit a "
               "dot, he shortened the statement, stripped the bias to cuts, and set up five task forces. A hawkish Fed "
               "that also went quiet. Yields and the dollar jumped; stocks fell.")},
        {"q": "Did the book get hurt?",
         "a": ("The hedges paid and the discipline held. Our long-volatility idea and the S&P put spread were the "
               "winners as the VIX jumped 12% &mdash; the put spread is up about 70%. The short-euro position finally "
               "paid as the dollar broke 100. Gold gave back exactly as we flagged it would, but held its stop. The "
               "duration positions are offside, but because we didn't add into the meeting, it's a give-back, not a "
               "stop-out.")},
        {"q": "The Fed turned hawkish but oil is at $78 — which one matters?",
         "a": ("That's the whole question. The Fed raised its inflation forecast to 3.6% the same week Brent broke $78 "
               "on the Iran deal &mdash; those can't both describe the next six months. Either cheaper oil feeds "
               "through and the Fed is tightening into a disinflation it has to reverse, or inflation is sticky enough "
               "that oil is noise. We're holding our duration longs on the first view, but sized as a contrarian bet "
               "with a hard stop, not a conviction add.")},
        {"q": "Should we do anything about Micron before the 24th?",
         "a": ("Yes &mdash; collar it. Micron is 25.8% of the book into earnings June 24, and a higher-for-longer Fed "
               "just compressed the AI-memory multiple through a higher discount rate, on top of already-rich option "
               "premiums. A collar uses those rich calls to finance protective puts for near-zero cost, capping the "
               "print's downside while keeping the upside we like. A quarter of the book on one name into a "
               "high-volatility print is a risk question first.")},
        {"q": "Is the Iran deal done?",
         "a": ("Declared, not signed. Trump called it 'complete' and authorized reopening the Strait, but the ships "
               "aren't actually sailing and the formal signing is Friday in Switzerland &mdash; on Juneteenth, when US "
               "markets are closed. The binding constraint is Israel, not Iran. So we've surrendered the oil longs but "
               "aren't chasing crude lower into a signature a third party can still break &mdash; and anything that "
               "happens Friday can't trade until Monday.")},
        {"q": "What's the cleanest new trade out of all this?",
         "a": ("Long rate volatility. The biggest change isn't the hawkish dots &mdash; it's that Warsh removed the "
               "Fed's forward guidance, which is the tool that kept the bond market calm. With no path, every data "
               "point reprices the long end, and rate volatility (the MOVE index) re-rates higher more durably than "
               "stock volatility. We'd rather own that than guess the next rate move.")},
    ],

    "ideas_note": (
        "<p>The event resolved hawkish-and-opaque, so the fresh ideas own the new regime rather than fight it. "
        "<strong>Long rates vol (MM-023)</strong> &mdash; a 2-month long-bond (TLT) straddle / long MOVE; the "
        "guidance vacuum re-widens the term premium, and rate vol is the cleaner expression than the equity VIX that "
        "already re-rated. <strong>EUR/USD 1.14/1.12 put spread (MM-024)</strong> &mdash; the disciplined, "
        "defined-risk way to add to the vindicated dollar breakout (DXY through 100) without chasing spot at the "
        "figure. <strong>Long XLF / short XLK (MM-025)</strong> &mdash; a higher-for-longer, no-cuts Fed lifts "
        "financial margins while it compresses the long-duration tech multiple; the rate-regime version of the "
        "breadth RV. <strong>Long Gilts (MM-026)</strong> &mdash; the one major where the data undercuts the hawks: "
        "a soft UK CPI (2.8%) into a BoE hold today is a clean rate-divergence trade as US yields back up. The "
        "winners (MM-008, MM-012, MM-020) are banked or held with trailed stops; the offside duration (MM-013/004/009) "
        "is held on a falsifiable thesis, not added.</p>"
    ),

    "event_radar_note": (
        "<p>Warsh did both: a hawkish SEP (2026 dot ~3.8%, a hike penciled, cuts trimmed, inflation raised to 3.6%) "
        "AND a dismantled framework (no personal dot, a shorter statement, the cut bias stripped, five task forces). "
        "The tape repriced hawkish &mdash; S&P -1.21%, 2Y +16bp to a one-year high, DXY through 100, VIX +12% to "
        "18.44 &mdash; and the book's long vol (MM-020), put spread (MM-008) and short EUR/USD (MM-012) won. Ahead: "
        "the BoE + US claims/Philly Fed TODAY (the first test of a guidance-less Fed), the Iran signing Fri Jun 19 "
        "(Juneteenth — US closed, trades Monday; Israel the live wildcard), FedEx Jun 23, and book-critical Micron "
        "Jun 24. The fresh ideas own the regime: rate vol, the dollar breakout, financials-over-tech, and the UK "
        "divergence. No chase of the hawkish level; own its instability.</p>"
    ),

    "burry_tell": (
        "For fifteen years the Fed's primary shock absorber was forward guidance &mdash; the promise to telegraph the "
        "path of the funding rate, which compressed the term premium and made the central bank a calendar-anchored "
        "backstop. Yesterday a chair who has argued against guidance for a decade began removing it: he dropped his "
        "own dot, sharply shortened the statement, stripped the cut-bias language, and stood up a task force on "
        "communications and another on the balance sheet. The structural thing nobody is pricing is no longer a "
        "forecast &mdash; the first evidence printed. The 10Y backed up on a unanimous hold, and the VIX re-rated 12% "
        "to a level it had not held all cycle. Over the next two-to-three quarters this resolves as a permanently "
        "higher vol floor: a world where a hot CPI or a soft payroll moves markets the way it did before 2009, "
        "because the Fed no longer pre-commits to absorb it. Rate volatility, not equity volatility, is where it shows "
        "up first &mdash; the guidance Warsh removed was a rates tool. The equity market, with an index still "
        "concentrated in seven names that just led the losses, is the least prepared for the regime. It is the reason "
        "to be structurally long volatility, and increasingly rate vol (MM-023) over equity vol, as it announces itself."
    ),

    "earnings_summary": (
        "Jabil (JBL): POST-EARNINGS (reported Jun 17 BMO) — beat again, its fifth straight: EPS 3.16 vs 3.109 "
        "consensus (+1.64%) on revenue $8.751B vs $8.636B est (Finnhub-sourced); sell side 13 buy / 4 hold / 0 sell. "
        "The AI-infrastructure read-through held, the constructive signal under the noise. But the print is FAIRLY "
        "PRICED, not a fresh idea: a modest +1.64% beat reported into a hawkish Fed that just penciled a hike, where a "
        "higher discount rate is doing more to the AI-infra cohort than the quarter did. Stock reaction and short "
        "interest unverified. Neutral — good company, wrong week for a small beat. FedEx is Jun 23; Micron (the book's "
        "25.8% position) is Jun 24 AMC and is carried in Trade Ideas / the book outlook, not here."
    ),
    "earnings_why": (
        "Jabil is the one name that cleared the universe filter inside the window — a ~$40bn-cap US name that reported "
        "Jun 17 BMO (inside the 3-day-post window). It is rendered POST-EARNINGS: the +1.64% beat and the "
        "recommendation split are Finnhub-sourced, but the stock reaction and short interest are unverified, so the "
        "positioning pillar scores 0 and the label is capped at Medium. The signal worth keeping is qualitative — the "
        "AI-infrastructure guide held the morning before the hawkish Fed, evidence the build-out demand survived the "
        "early-June semis de-risk — but the FOMC repricing swamped the print. Excluded this morning: FedEx (reports "
        "Jun 23, just outside the window), Micron (Jun 24 AMC — carried in the book outlook as the 25.8% concentration "
        "risk), and names outside the Tech/Financials/Industrials/Utilities universe."
    ),

    "book_aim": (
        "Two-sided and re-pointed at a resolved event. The FOMC binary graded out: the hedges (long vol MM-020, the "
        "SPX put spread MM-008 at ~+70%) and the short EUR/USD (MM-012) paid, gold gave back as flagged and held its "
        "stop, and the offside duration longs (MM-013/004) and the steepener (MM-009) gave back but were protected by "
        "the no-add discipline into the print. For the rest of June: bank or trail the winners; hold the offside "
        "duration on its falsifiable oil-disinflation thesis with hard stops (4.35% / 4.65% / -10bp), not as a "
        "conviction add; and rotate the book's risk into the new regime via the fresh ideas — long rate vol (MM-023), "
        "the dollar breakout (MM-024), financials-over-tech (MM-025), and the UK divergence (MM-026). The two "
        "house-keeping priorities are unchanged and now more urgent: collar the 25.8% Micron concentration before the "
        "Jun 24 print, and finally hedge the ~72% USD sleeve into a dollar that has broken out. Open no new bet that "
        "merely chases the hawkish level — own its instability, not its direction."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the one option line "
                 "(MM-008) is a model estimate from spot (~$60 post-FOMC).")
    },
    "idea_selection": [
        {"label": "Long rates vol — own the guidance vacuum (MM-023)", "in": True,
         "text": ("Warsh removed the Fed's forward path; the term premium now reprices on every data point, and the "
                  "10Y backing up on a hold is the first evidence. A 2-month long-bond (TLT) straddle or long MOVE "
                  "owns the re-widening in either direction with defined premium. The cleanest expression of the new "
                  "regime — rate vol, not equity vol, is where the guidance vacuum gets paid.")},
        {"label": "EUR/USD 1.14/1.12 put spread — add the dollar breakout (MM-024)", "in": True,
         "text": ("The dollar broke 100 for the first time since the early Iran war on the hawkish Fed vs a paused "
                  "ECB. A defined-risk put spread owns the continuation toward 1.13 with capped premium — the "
                  "disciplined way to add to the vindicated spot short (MM-012) without chasing at the figure, into a "
                  "known two-sided Iran tail.")},
        {"label": "Long XLF / short XLK — the rate-regime rotation (MM-025)", "in": True,
         "text": ("A higher-for-longer, no-cuts Fed lifts financial net-interest margins while it compresses the "
                  "long-duration tech multiple; Wednesday's Dow-over-Nasdaq, tech-led-losses split is the first leg. "
                  "The rate-sensitivity version of the breadth RV (MM-022). Size on the ratio; stop -3%.")},
        {"label": "Long Gilts — the UK divergence (MM-026)", "in": True,
         "text": ("The one major where the data undercuts the hawks: UK May CPI at 2.8% (below 3.0%) into a "
                  "near-unanimous BoE hold today pulls Gilt yields down as US yields back up on Warsh. A clean, dated "
                  "rate-divergence trade; stop UK 10Y +15bp.")},
        {"label": "Offside duration (MM-013/004/009) — held, not added", "in": False,
         "text": ("The trades the Fed shot at. Held on the falsifiable oil-disinflation thesis (Brent $78 vs the "
                  "Fed's raised 3.6% forecast), inside their stops (4.35% / 4.65% / -10bp) and min-holds. Do NOT add "
                  "into a fresh hawkish print — let the data resolve it.")},
        {"label": "No idea that merely chases the hawkish level", "in": False,
         "text": ("The consensus has fully embraced higher-for-longer. Shorting more duration here is the crowded "
                  "side into a guidance-less Fed where a soft print squeezes. The four fresh ideas own the regime's "
                  "instability (rate vol, dollar, rotation, UK) rather than its direction.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 18.0},
        {"label": "VIX",   "value": 18.44},
        {"label": "VIX3M", "value": 19.5},
        {"label": "VIX6M", "value": 20.5},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.22, 3)},
        {"label": "5Y",  "value": 4.35},
        {"label": "10Y", "value": round(_g("us10y") or 4.50, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 5.00, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-023", "trade": "Long rates vol — 2M long-bond (TLT) straddle / long MOVE",
            "asset_class": "Rates (vol)", "structure": "straddle / vol",
            "entry": "~1.2% premium", "stop": "—", "target": "~2-3x on a term-premium re-rating",
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "to mid-Aug", "min_hold_days": 0,
            "thesis": ("Forward guidance is mechanically a term-premium compressor, and Warsh just removed it — he "
                       "dropped his own dot, shortened the statement, and stood up a balance-sheet task force. The "
                       "10Y backing up to 4.499% on a unanimous hold is the first evidence the term premium is "
                       "re-widening, and MOVE is the cleaner read on it than VIX. A long-bond straddle owns the "
                       "re-rating in either direction — a hawkish over-tightening or the policy-error reversal — with "
                       "defined premium. Rate vol, not equity vol, is where the guidance vacuum gets paid."),
        },
        {
            "id": "MM-2026-024", "trade": "Buy 3M EUR/USD 1.14/1.12 put spread (own the dollar breakout)",
            "asset_class": "FX (options)", "structure": "put spread",
            "entry": "~0.7% premium", "stop": "—", "target": "~4x at 1.12",
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 2, "stop_quality": 1},
            "horizon": "3 months", "min_hold_days": 0,
            "thesis": ("The dollar broke a figure for the first time since the early Iran war: a hawkish Fed that "
                       "penciled a hike against a paused ECB widened the rate-path asymmetry, DXY ripped through 100 "
                       "to ~100.5, and EUR/USD sliced through 1.1550. A put spread owns the continuation toward 1.13 "
                       "with defined premium and positive convexity — the disciplined way to add to the vindicated "
                       "spot short (MM-012) without chasing at the figure, into a known two-sided tail (a clean Iran "
                       "signing is the EUR-supportive offset the defined risk caps)."),
        },
        {
            "id": "MM-2026-025", "trade": "Long XLF (financials) vs short XLK (technology)",
            "asset_class": "Equity RV", "structure": "cross-sector ratio",
            "entry": "spot ratio", "stop": "ratio -3%", "target": "ratio +6%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("A higher-for-longer Fed with the cut bias stripped and a 2Y at a one-year high is a sector-"
                       "rotation engine: it lifts financial net-interest margins while it compresses the long-duration "
                       "tech multiple through a higher discount rate. Wednesday wrote the first leg — the Dow fell "
                       "less than the Nasdaq, and Microsoft, Meta, Alphabet and Amazon led the losses. This is the "
                       "rate-sensitivity version of the breadth RV (MM-022): long the margin beneficiary, short the "
                       "multiple casualty — low beta to the index level, high beta to the higher-for-longer repricing."),
        },
        {
            "id": "MM-2026-026", "trade": "Long Gilts (UK 10Y) into the BoE hold (UK rate divergence)",
            "asset_class": "Rates (UK)", "structure": "outright duration",
            "entry": "UK 10Y ~4.75%", "stop": "UK 10Y +15bp", "target": "UK 10Y -25bp",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "2-4 weeks", "min_hold_days": 0,
            "thesis": ("The UK is the one major where the data undercuts the hawks the same week the US Fed empowered "
                       "them. May CPI came in at 2.8% — unchanged and below the 3.0% consensus, with services and "
                       "housing softening — which weakens the case of the BoE's hawkish dissenters (Pill, Greene) "
                       "into today's noon hold. A near-unanimous hold leaning on the soft print pulls Gilt yields "
                       "down even as US yields back up on Warsh — a clean rate-divergence trade. The half-priced "
                       "hawkish-dissent risk is the under-positioned offset; a hawkish surprise is the stop."),
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
