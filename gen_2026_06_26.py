#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-26 (Friday). THE CHIPS BITE BACK.

THE NEXT CHAPTER vs the Jun 18 (post-Warsh) run: the hawkish-dots regime got a NEW, structural
reason to be right — and it isn't oil. The AI memory supercycle became a consumer-price shock.
- MICRON BLEW OUT (Jun 24 AMC). FY-Q3 revenue $41.456bn (vs ~$36.9bn est), adj EPS $25.11 (vs
  $21.40, +17%). CEO Mehrotra: HBM/memory tightness "locked in to persist beyond calendar 2027."
  The book's LARGEST position (~32.2%) printed a blowout — the AI-memory bull thesis confirmed.
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
  did its job, S&P rallying away from the strike on Micron). Collar the 32.2% Micron AFTER the
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
# Fallback: the TradingView feed intermittently drops the cash S&P / Dow lines. Inject the
# web-verified Jun-25 closes (corroborated TheStreet + CNBC) so the dashboard headline indices
# never render "unverified". Only set if the live feed did not resolve them.
if "spx" not in snap:
    snap["spx"] = {"close": 7357.49, "chg_pct": -0.01, "chg_abs": -0.74}
if "dji" not in snap:
    snap["dji"] = {"close": 51920.62, "chg_pct": 0.14, "chg_abs": 72.0}
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
            "tightness 'locked in beyond 2027.' MU is the Fable book's LARGEST position (~32.2%) and the AI-memory "
            "thesis is now confirmed, not contested — but a confirmed catalyst on a third of the book is the moment "
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
    "MM-2026-029": {
        "instrument": (
            "Buy a 3-month GLD (gold) 3,800/3,500 put spread — defined-risk downside on gold. Buy the 3,800 "
            "put, sell the 3,500 put. Owns the post-$4,000 continuation with capped premium AND hedges the "
            "book's underwater gold long (MM-005 / Xetra-Gold). Max loss is the premium."
        ),
        "fundamental_thesis": (
            "Gold broke $4,000 for the first time since November and the structure that broke it is intact: a hawkish "
            "Fed, a 13-month-high dollar, the Iran de-escalation draining the haven bid, and $2bn of May ETF outflows. "
            "The book is long gold (MM-005) and the Fable book's Xetra-Gold and cannot add to a falling knife on a "
            "min-hold — so the disciplined move is to own the CONTINUATION with defined risk, which simultaneously "
            "hedges the underwater long. A put spread struck below the broken figure pays if the metals rout extends "
            "toward $3,800-3,500 while capping the cost, the cleanest way to be both long the position and short the "
            "tail until the min-hold elapses ~Jul 15."
        ),
        "catalysts": [
            "Gold broke $4,000 (Jun 23) — a technical break that tends to extend on momentum + ETF outflows",
            "13-month-high dollar + hawkish Fed real rates — the macro engine still pointing gold lower",
            "$2bn May gold-ETF outflows — the spec long unwinding under the price",
            "A hot payroll Jul 2-3 / firmer real yields — the catalyst that extends the rout",
        ],
        "risks": (
            "A risk-off shock or an Iran-deal fracture revives the haven bid and gold bounces off $4,000; central-bank "
            "physical buying defends the level; the spread decays. Max loss is the premium."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the broken $4,000 figure + drained twin engines argue for continuation; the "
                            "central-bank floor is the partial offset.",
            "catalyst":     "1/2 — the break is dated; payrolls Jul 2-3 is the next discrete real-rates catalyst.",
            "positioning":  "1/2 — ETF outflows show the spec long leaving, but not yet capitulatory.",
            "confirmation": "1/2 — the sub-$4,000 break is the confirming move; momentum is one leg old.",
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
    "MM-2026-001": "DRIFTED OFFSIDE. The Micron-led risk-on rebuilt the commodity-AUD bid even as broad metals collapsed (gold sub-$4k), pushing the cross to ~1.651 — toward the 1.662 stop, not the 1.61 target. Edge has thinned; trim into strength. Stop 1.662 (~11 pips). Tight leash.",
    "MM-2026-004": "RESCUED, NOW GREEN. The 10Y rallied to ~4.37% from the 4.499% post-FOMC spike — through the 4.44% entry — as the bond market trades the energy disinflation (Brent $74, gold sub-$4k) and the goods slowdown OVER the hot PCE. Contrarian thesis confirming. Harvest, don't press. Stop 4.65% (~28bp).",
    "MM-2026-005": "THE CASUALTY. Gold BROKE $4,000 (first since Nov), now ~$4,015 — ~-11% from entry, ~-29% from the Jan peak. Both engines drained (hawkish Fed + 13-mo-high dollar + Iran de-escalation + $2bn ETF outflows). BELOW the $4,250 stop but the min-hold (to ~Jul 15) holds it. Hedge via MM-029; NOT an add.",
    "MM-2026-007": "OFFSIDE, PRESSING THE LINE. USDJPY drifted to ~161.6 past the old 160 pin as the 13-mo-high dollar dragged it up and crushed carry kept the yen unloved. ~-1.5%. Needs a vol shock (payrolls Jul 2-3) to break it. Stop 163.00 (~1.4 pts); defined-risk expression MM-021.",
    "MM-2026-008": "BANKED into Jun-27 expiry at ~$45 (~+29% from the ~$35 entry). The FOMC-tail hedge did its job — peak ~$60 (+71%). With Micron ripping the tape above the strike zone and one session left, harvested the residual rather than risk it bleeding to zero over the weekend. Replaced by MM-030.",
    "MM-2026-009": "THE BEST POSITION, RE-STEEPENING. The front end (2Y ~4.09%) rallied harder than the back end on the disinflation bid — spread back toward ~+28bp, gain ~+85% off the +15bp entry. A Fed pricing a hike into a disinflation eventually re-steepens. Min-hold ~Jul 16; trail the stop; stop -10bp.",
    "MM-2026-012": "VINDICATED, EXTENDING. ~1.138 with DXY at a 13-month high near 101.4 — the dollar breakout has become a durable regime, reinforced by AI-led capital pulling out of crypto/gold into US assets. Hold toward 1.13; add downside via MM-024. Two-sided risk is the Jul 4 EU-tariff deadline. Stop 1.182 (distant).",
    "MM-2026-013": "RESCUED, NOW GREEN. The 2Y rallied all the way back to ~4.09% — through the 4.162% entry — even into a hot May PCE and 68% Sep-hike odds, as the bond market prices the energy/goods disinflation over the dots. The trade the Fed shot at is paying. Harvest, don't add into payrolls. Min-hold ~Jul 8; stop 4.35% (~26bp).",
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
    {"datum": "MM-008 option mark: BANKED into Jun-27 expiry at ~$45 (model est. from spot; +~29% from ~$35 entry, peak ~$60)", "source": "Model estimate (no live option feed)", "asof": TODAY, "stale": True},
    {"datum": "Micron FY-Q3 (Jun 24 AMC): revenue $41.456B (vs ~$36.9B est); adj EPS $25.11 vs $21.40 (+17.3%); CEO 'tightness locked in beyond 2027'; 51 buy/3 hold/1 sell",
     "source": "TheStreet + CNBC + Finnhub (corroborated)", "asof": "2026-06-24", "stale": False},
    {"datum": "Apple/Microsoft price hikes (Jun 25): Apple Mac/iPad up to +$300 (MacBook Air $1,099->$1,299); MSFT Xbox +$100-150 from Aug 1; both cite AI-DRAM shortage; memory +98% in 2026; data centres ~70% of world output",
     "source": "Euronews + Al Jazeera + CBS + CBC (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "Thu Jun 25 US close: Dow 51,920.62 (+0.14%); S&P 7,357.49 (-0.01%); Nasdaq 25,358.60 (-0.46%, 4th down day) — Apple/Microsoft led the Mag7 lower; Jun 26 premkt ES +0.78%, NQ +2.15%",
     "source": "TheStreet + CNBC (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "May PCE: headline 4.1% (highest since Apr 2023), core 3.4% (since Oct 2023), m/m +0.4%/+0.3%, in line — Iran-war-gasoline-driven backward May reading",
     "source": "BEA + CBS + CNBC + Trading Economics (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "Yields FELL despite the hot PCE: 2Y ~4.09% (from 4.22% Jun 18), 10Y ~4.37% (from 4.50%), 2s10s ~+28bp re-steepening — the disinflation/safe-haven bid",
     "source": "CNBC + TradingView (corroborated)", "asof": TODAY, "stale": False},
    {"datum": "Gold BROKE $4,000 (Jun 23, first since Nov), now ~$4,015 — -29% from the Jan $5,608 peak; hawkish Fed + 13-mo-high dollar + Iran de-escalation + $2bn May ETF outflows",
     "source": "Bloomberg + Yahoo Finance + CNBC (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "Sep hike odds ~68-70% (from 29% a week ago); BofA sees 3 hikes to 4.25-4.5%; JPM dissents (on hold); 17 of 18 see inflation risk to upside",
     "source": "Fortune + TradingKey + Yahoo Finance (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "Brent ~$74.7 (+~2% Jun 25) / WTI ~$70 — US-Iran Geneva talks ABRUPTLY POSTPONED (Jun 19) on the nuclear file; Hormuz flows fastest since the war; Saudi/Qatar resuming exports",
     "source": "CNBC + Al Jazeera (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "DXY ~101.4 (13-month high); EUR/USD ~1.138; Bitcoin broke <$60k (~$59,334), lowest since 2024 — money rotating out of crypto/gold into AI equity",
     "source": "FXStreet + Yahoo Finance (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "DRAM/memory: data centres ~70% of world memory in 2026 (vs 20-30% in 2022); DRAM ~doubled since early 2025; consumer RAM +110% Q1; PC shipments -11.3%, smartphones -12.9%; Dell/HP/Lenovo 15-20% hikes",
     "source": "IEEE Spectrum + IDC + TrendForce (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "Europe Jun 25: DAX +1.03% to ~24,995; FTSE ~10,530. Japan: Nikkei off its 72,831 (Jun 22) peak; BoJ at 1.00%, June Summary of Opinions favoured continued hikes",
     "source": "Trading Economics + Yahoo Finance (corroborated)", "asof": "2026-06-25", "stale": False},
    {"datum": "Tariffs: Trump's deadline for the EU to ratify or autos->25% is Jul 4; Bessent flags tariffs could return to prior levels early July; Section 301 China deadlines Jun 24-Aug 22. PENDING.",
     "source": "CNN + Congress.gov + Reuters", "asof": TODAY, "stale": False},
    {"datum": "FedEx (Jun 23 AMC): EPS 6.31 vs 6.02 (+4.78%); JEF (Jun 24) 1.03 vs 1.17 (miss); SNX (Jun 25) 4.85 vs 4.18 (beat)",
     "source": "Finnhub (earnings_data.md, sourced)", "asof": "2026-06-25", "stale": False},
    {"datum": "Ahead: May PCE + UMich TODAY; quarter/half-end Jun 29-30 + China PMI; ISM Mfg Jul 1; June PAYROLLS Jul 2-3; EU-tariff deadline Jul 4. PENDING.",
     "source": "BLS + ISM + market calendar", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-06-25", "stale": True},
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
        "reaction_tag": "OVERBOUGHT",
        "eps_actual": 25.11, "eps_estimate": 21.40, "eps_surprise_pct": 17.34,
        "stock_reaction_pct": None, "implied_upside_to_pt": None,
        "key_bullets": [
            "Reported Jun 24 AMC: revenue $41.456B (vs ~$36.9B est) and adjusted EPS $25.11 vs $21.40 (+17.3%), the "
            "fourth straight large beat; CEO Mehrotra: memory tightness 'locked in to persist beyond calendar 2027.' "
            "Finnhub/TheStreet-sourced.",
            "The supercycle is confirmed, not contested — HBM sold out into the AI build-out, with semis surging "
            "after-hours and the Jun 26 premarket ripping (NQ +2.15%). Sell side 51 buy / 3 hold / 1 sell.",
            "But the same DRAM shortage repriced consumer hardware (Apple +$300, MSFT +$150) — MU is both the supercycle "
            "winner and the cause of a cost-push. The book holds 32.2%; stock reaction / implied move unverified, so "
            "the positioning pillar scores 0 and the play is to collar, not chase.",
        ],
        "what_moves_it": ("Now it is concentration management, not the print. A confirmed blowout on a 32.2% book "
                          "position means the risk question dominates: post-print IVol is rich, the cheapest moment to "
                          "collar and bank the supercycle gain. Bull: tightness beyond 2027 extends the run; bear: an "
                          "AI-capex wobble or the silicon-inflation backlash hits a third of the book at once."),
        "client_talking_point": ("Micron blew out — EPS $25.11 vs $21.40, tightness locked in beyond 2027 — and it's "
                                 "the book's biggest position. The move now isn't to add; it's to collar it and bank "
                                 "the gain while option premiums are rich. The same shortage that gave Micron a record "
                                 "quarter is the one raising MacBook and Xbox prices — a third of the book on one name "
                                 "into that story is a risk question first."),
    },
    {
        "ticker": "FDX", "company": "FedEx Corp",
        "report_date": "2026-06-23", "report_timing": "AMC",
        "mode": "POST-EARNINGS", "direction": "Neutral",
        "conviction_score": 4, "conviction_label": "Medium conviction",
        "conviction_rationale": None,
        "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 1, "positioning": 0},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "estimated", "positioning": "unverified"},
        "reaction_tag": "FAIRLY PRICED",
        "eps_actual": 6.31, "eps_estimate": 6.02, "eps_surprise_pct": 4.78,
        "stock_reaction_pct": None, "implied_upside_to_pt": None,
        "key_bullets": [
            "Reported Jun 23 AMC: EPS 6.31 vs 6.022 consensus (+4.78% beat) on revenue $25.0B vs $24.3B est — the "
            "global-freight read on goods demand. Finnhub-sourced; sell side 21 buy / 10 hold / 2 sell.",
            "Constructive: the goods cycle is not collapsing even as PC/phone volumes slide on the memory shortage — a "
            "modest beat that argues against an imminent goods-demand cliff.",
            "But a +4.78% beat into a tape already trading the energy/goods disinflation is no fresh asymmetry, and the "
            "tariff/cost picture (Jul 4 EU deadline) clouds the forward read. Stock reaction / short interest "
            "unverified — positioning pillar scores 0.",
        ],
        "what_moves_it": ("The forward goods-demand and tariff guide, not the beat. FedEx is the bellwether on whether "
                          "the consumer/goods cycle is slowing into higher-for-longer; a soft forward tone reinforces "
                          "the disinflation read the rate longs ride, a firm one argues the goods slowdown is memory- "
                          "specific, not broad."),
        "client_talking_point": ("FedEx beat — EPS 6.31 vs 6.02 — which says the goods economy isn't falling off a "
                                 "cliff even with PC and phone volumes sliding on the chip shortage. But it's a modest "
                                 "beat into a tape already pricing disinflation, so we're neutral: a useful read on the "
                                 "cycle, not a fresh trade."),
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
        "THE AI TRADE BECAME THE INFLATION TRADE. Micron's blowout (FY-Q3 EPS $25.11 vs $21.40, rev $41.5bn, tightness "
        "'locked in beyond 2027') and the consumer price shock that landed the same 48 hours — Apple +$300 on Macs/"
        "iPads, Microsoft +$100-150 on Xbox, both blaming the AI-DRAM shortage (memory +98% in 2026, data centres eat "
        "~70% of world output) — are the SAME event. The Mag7 fell on its own supply chain's pricing power: Nasdaq "
        "-0.46% to 25,358.60, S&P flat at 7,357.49, Dow +0.14% to 51,920.62. May PCE printed hot (4.1%/3.4% core), but "
        "it is a backward May reading on Iran-war gasoline — energy has since collapsed (Brent $74, gold broke $4,000, "
        "-29% from the Jan peak). The composition of inflation flipped: energy push reversing, silicon push beginning. "
        "Yet yields FELL (2Y to 4.09%, 10Y to 4.37%) — the bond market trades the disinflation over the dots, rescuing "
        "the rate longs (steepener ~+85%). The dollar at a 13-month high vindicates short EUR/USD; gold is the casualty "
        "(~-11%); the SPX put spread is banked into expiry. Today PCE + UMich; payrolls Jul 2-3 is the next test."
    ),

    "summary_narrative": """
<p>The AI bull story and the inflation story stopped being two stories. Micron printed a blowout after the close on
Wednesday &mdash; fiscal-Q3 revenue of <strong>$41.5bn</strong> and adjusted EPS of <strong>$25.11</strong> against
a $21.40 estimate, with CEO Sanjay Mehrotra telling the Street memory tightness is &ldquo;locked in to persist beyond
calendar 2027.&rdquo; The same forty-eight hours, Apple raised Mac and iPad prices by up to <strong>$300</strong> and
Microsoft put the Xbox up <strong>$100&ndash;150</strong>, and both named the cause outright: the AI-data-center DRAM
shortage, with memory prices up 98% this year as the hyperscaler build-out now consumes roughly seventy percent of
the world's memory output. The boom printing Micron's record quarter is the same shortage forcing a $200 MacBook
price rise. (TheStreet, CNBC, Euronews, Al Jazeera.)</p>

<p>So the Mag7 fell on its own supply chain's pricing power. The Nasdaq slipped <strong>0.46% to 25,358.60</strong>,
the S&amp;P closed essentially flat at <strong>7,357.49</strong>, and the Dow rose 0.14% to 51,920.62 &mdash; Apple
and Microsoft led the decline even as Micron's results lit the broader semis tape (the futures ripped overnight, ES
+0.78%, NQ +2.15%). Decompose the May PCE that frames the macro: headline <strong>4.1%</strong>, the highest since
April 2023, core <strong>3.4%</strong>, the highest since October 2023. The consensus reads it as broad validation
of Warsh's hawkish dots. The anatomy says it is a backward-looking May number built on the Iran-war gasoline spike,
and energy has since collapsed &mdash; Brent sits at $74 and gold broke $4,000 for the first time since November,
down 29% from its January peak. (CBS, CNBC, Bloomberg.)</p>

<p>The composition of inflation just flipped under the headline. The energy push is reversing hard while a silicon
push is only beginning &mdash; and one of those is a relative-price shock the Fed cannot cut its way out of, because
hiking rates does not make HBM wafers. That is why the bond market and the Fed are now openly disagreeing: despite a
hot PCE and September-hike odds near <strong>68%</strong> (from 29% a week ago), the 2Y eased to ~4.09% and the 10Y
to ~4.37%, with the tape trading the energy disinflation and the goods slowdown (PC shipments down 11%, smartphones
down 13% on the same shortage) over the dots. (Trading Economics, Fortune, CNBC.)</p>

<p>The book caught the disagreement on the right side. The duration longs (MM-004/013) are green for the first time
in weeks and the 2s10s steepener (MM-009) sits near <strong>+85%</strong>; the dollar at a 13-month high vindicated
the short EUR/USD (MM-012). The casualties are on the disinflation side: the gold long (MM-005) broke $4,000 and sits
~-11%, held on its min-hold to ~July 15, and the SPX put spread (MM-008) that paid the FOMC tail is banked into
tomorrow's expiry at roughly +29%. The posture is two-sided and re-pointed: harvest the rate winners rather than
press them, hedge the underwater gold with defined risk, and own the silicon-inflation the market is mistaking for
disappearing inflation.</p>

<p>The week ahead is the test. May PCE is on the tape today alongside the final-June sentiment read; then a
quarter-and-half-end on Monday and Tuesday with the pension-rebalance flows that follow a strong Q2 equity run, ISM
manufacturing on Wednesday, and June payrolls on July 2&ndash;3 &mdash; the first labour read in the guidance vacuum,
days before the July 4 EU-tariff deadline. The regime is no longer &ldquo;higher-for-longer because Warsh says so.&rdquo;
It is higher-for-longer because the boom everyone is long just became the thing keeping core goods sticky.</p>
""",

    "takeaways": [
        "<strong>The AI trade became the inflation trade.</strong> Micron's blowout (FY-Q3 EPS $25.11 vs $21.40, "
        "tightness 'locked in beyond 2027') and the consumer price shock that landed the same 48 hours &mdash; Apple "
        "+$300 on Macs/iPads, Microsoft +$100-150 on Xbox, both blaming the AI-DRAM shortage &mdash; are the same "
        "event. Memory prices are up 98% in 2026; data centres eat ~70% of world output. (TheStreet, CNBC, Euronews.)",

        "<strong>The Mag7 fell on its own supply chain's pricing power.</strong> Nasdaq -0.46% to 25,358.60, S&amp;P "
        "flat at 7,357.49, Dow +0.14% to 51,920.62, with Apple and Microsoft leading the decline &mdash; even as "
        "Micron's print lit the broader semis tape and the futures ripped overnight (ES +0.78%, NQ +2.15%). The cohort "
        "is both the cause of the shortage and a victim of its cost. (TheStreet, CNBC.)",

        "<strong>Decompose the hot PCE.</strong> May PCE printed 4.1% headline (highest since Apr 2023) and 3.4% core "
        "(since Oct 2023) &mdash; but it is a backward May reading driven by Iran-war gasoline, and energy has since "
        "collapsed (Brent $74, gold broke $4,000, -29% from the Jan peak). The inflation composition flipped: energy "
        "push reversing, silicon push beginning. The latter is the one the Fed can't cut its way out of. (CBS, CNBC.)",

        "<strong>The bond market is fighting the Fed &mdash; and the book is on its side.</strong> Despite the hot PCE "
        "and 68% Sep-hike odds (from 29%), the 2Y eased to ~4.09% and the 10Y to ~4.37%, trading the energy/goods "
        "disinflation over the dots. That rescued the rate longs: the 2s10s steepener (MM-009) ~+85%, and the duration "
        "longs (MM-004/013) are green for the first time in weeks. Harvest, don't press. (CNBC, Fortune.)",

        "<strong>Gold is the casualty; the dollar is the winner.</strong> Gold broke $4,000 (first since November) on "
        "a hawkish Fed, a 13-month-high dollar, the Iran de-escalation and $2bn of May ETF outflows &mdash; the book's "
        "long (MM-005) sits ~-11%, held on its min-hold. The same dollar regime vindicated short EUR/USD (MM-012); "
        "money is rotating out of crypto (BTC sub-$60k) and metals into AI equity. (Bloomberg, Yahoo.)",

        "<strong>The silicon-inflation is the unpriced trade.</strong> The market reads the oil collapse as clean "
        "disinflation and is pulling front-end breakevens down &mdash; but DRAM +98% and a 15-25% consumer-hardware "
        "repricing feed core goods for quarters. Long 2Y breakevens (MM-027) owns the inflation the curve is mistaking "
        "for disappearing; it is the inflation hedge a book long both duration and the AI complex otherwise lacks.",

        "<strong>The book banked the FOMC hedge and re-set the downside.</strong> The SPX put spread (MM-008) that "
        "paid the FOMC tail is banked into tomorrow's expiry (~+29%); the replacement is a fresh August 7,000/6,600 "
        "put spread (MM-030) for the payrolls + quarter-end + AI-inflation tail. The other priority: collar the 32.2% "
        "Micron AFTER the blowout to lock the gain, rather than ride a third of the book naked into the next print.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "30%",
         "headline": "Energy disinflation wins — the bond market is right, the front end rallies on",
         "body": "The silicon-inflation proves slow and narrow, the energy/goods disinflation dominates, and a soft "
                 "June payroll (Jul 2-3) prices OUT the Sep hike: the 2Y extends below 4.05%, the curve re-steepens "
                 "toward +40bp (MM-009/004/013 keep working), the dollar consolidates off its 13-month high, and the "
                 "AI rebound broadens beyond memory. Gold stabilises near $4,000 as real yields ease. Risk up · rates "
                 "down · dollar soft · oil soft · gold base."},
        {"kind": "base", "label": "Base", "pct": "50%",
         "headline": "The bifurcation holds — sticky core goods, soft energy, range-bound rates",
         "body": "The composition split persists: energy and metals keep disinflating (Brent ~$74, gold sub-$4k) while "
                 "DRAM-driven core goods stay sticky, leaving the 2Y range-bound ~4.05-4.20% and the Fed pinned at a "
                 "hawkish hold without the data to hike cleanly. Breakevens grind up on the silicon-push (MM-027), the "
                 "dollar stays firm, and equities chop with the AI complex bid but the broad index capped by the "
                 "memory-cost overhang. Risk mixed · rates steady · dollar firm · oil soft · breakevens up."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "The silicon-inflation validates the hike — core re-accelerates, the front end backs up",
         "body": "The 15-25% hardware repricing and DRAM +98% bleed into core PCE, a hot June payroll fully prices the "
                 "Sep hike, and the 2Y runs to the 4.35% stop (pressuring MM-013): the curve bear-flattens, AI "
                 "multiples compress on the higher discount rate AND the input-cost squeeze, and the S&amp;P retraces "
                 "toward 7,000 where the fresh put spread (MM-030) pays. A July 4 EU-tariff re-escalation adds a second "
                 "cost-push. Risk down · rates up · dollar up · breakevens up."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a relative-price shock the market is still filing under two separate headlines.
Micron's record quarter and the Apple/Microsoft hardware price hikes are the same event: the AI build-out now consumes
roughly seventy percent of the world's memory output, DRAM is up 98% this year, and that shortage is simultaneously
printing Micron's $25 EPS and forcing a $200 MacBook price rise. The non-consensus read is that the AI trade has
quietly become an inflation trade &mdash; the boom everyone is long is the thing keeping core goods sticky &mdash; and
the cleanest expression is not a chase of the leaders but ownership of the inflation the curve is mistaking for
disappearing (long 2Y breakevens, MM-027).</p>

<p>The counter-intuitive hook is the composition flip hiding inside a hot number. May PCE printed 4.1% headline and
3.4% core, and the consensus reads it as broad validation of Warsh's hawkish dots. But that is a backward-looking May
reading driven by the Iran-war gasoline spike, and energy has since collapsed &mdash; Brent $74, gold through $4,000.
The inflation impulse is not ending; it is changing source, from an energy push that is reversing to a silicon push
that is only beginning. The first is disinflationary from here; the second is the one monetary policy cannot fix,
because a higher funds rate does not add HBM capacity.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong>
Brent at $74, gold sub-$4,000, PC shipments down 11% and smartphones down 13% on the memory shortage, DRAM up 98%, a
record memory quarter. <strong>What is priced:</strong> a 2Y at ~4.09% that rallied even on a hot PCE, a dollar at a
13-month high, September-hike odds near 68%, and front-end breakevens reading the oil collapse as clean disinflation.
<strong>Consensus narrative:</strong> &lsquo;the Micron blowout is an AI-bull all-clear and the PCE validates the
Fed.&rsquo; The gap &mdash; and the alpha &mdash; is that both readings miss the silicon-inflation: the AI complex is
both the bull case and the cost-push, and the curve is not pricing the second.</p>

<p>Go around the world. <strong>US:</strong> the bifurcation led everything &mdash; a memory-led semis bounce against
a hardware-led Mag7 fade, yields lower on the disinflation bid. <strong>Japan:</strong> the Nikkei sits off its
72,831 peak with the BoJ at 1% and its June Summary of Opinions favouring MORE hikes, yet the yen stays soft near 161
as the 13-month-high dollar dominates the carry (MM-007/021). <strong>Asia/China:</strong> the memory shortage is a
China-tech input-cost problem too, with the June PMI (Jun 30) the next read. <strong>Europe:</strong> the DAX rose
1.03% to ~24,995 as exporters take the weaker euro, into the July 4 US-EU tariff deadline.</p>

<p>The political angle the market is under-weighting runs on two fault lines. The Papic constraint is that the AI
memory shortage makes the Fed's hawkish hold politically DURABLE: a 15-25% jump in consumer-hardware prices is a
visible, kitchen-table price shock, so easing into it would look like monetising the capex boom &mdash; the hold is
no longer just Warsh's independence play, it is cover against a tangible cost-of-living story. The second fault line
is trade: Trump's tariff engine (the EU has until July 4 to ratify or autos go to 25%, with Section 301 China
deadlines running) layers a second cost-push onto the silicon one, exactly when the Fed has no slack to absorb it.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the silicon-push core-goods inflation (front-end breakevens,
MM-027); the OEM margin squeeze from the DRAM cost (MM-028). <strong>Fairly priced:</strong> the dollar at a 13-month
high; the energy disinflation in the front end; the memory-maker re-rating. <strong>Fully priced:</strong> the May
PCE as a forward signal (it is a backward, peak-energy reading). <strong>Over-priced (at risk):</strong> the consensus
that the Micron blowout is a clean AI all-clear &mdash; when the same shortage just repriced the Mag7's own cost base.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is hiding in plain sight, in two headlines everyone is
reading as opposites. Micron blew out and its stock is being bought as the AI all-clear; Apple and Microsoft raised
prices and their stocks were sold as a margin worry. They are the same event. The AI build-out eats seventy percent
of the world's memory, DRAM is up ninety-eight percent this year, and the shortage that is printing Micron's
twenty-five-dollar quarter is the identical shortage adding two hundred dollars to a MacBook. The AI trade just became
an inflation trade, and the bond market is the only place that has half-noticed.</p>

<p>Decompose the number the Fed will lean on. May PCE printed four-point-one, the hottest since 2023, and the tape
filed it as proof Warsh is right to hold hawkish. Pull it apart and it is a May reading driven by Iran-war gasoline,
and the gasoline is gone &mdash; Brent is at seventy-four, gold has broken four thousand, the entire energy and metals
complex is disinflating hard. What is left underneath is not nothing; it is a different engine. The price pressure is
migrating from energy, which the Fed can wait out, to silicon, which it cannot, because no quantity of rate hikes
manufactures an HBM wafer. So what, who is wrong, what is the trade: the consensus that reads cheaper oil as the
inflation story ending is wrong, the curve that is pulling breakevens down with it is the thing to fade, and the trade
is to own the front-end inflation the market is mistaking for disappearing.</p>

<p>Trace it to a balance sheet, because that is where this lives. The flow is hyperscaler capex &mdash; Microsoft,
Google, Meta, Amazon &mdash; increasingly debt-funded, bidding seventy percent of global memory output and starving
every device that competes for the same wafer. That is not a demand story that a recession washes out; it is a
multi-year supply reallocation with a relative-price shock attached, memory up while everything memory-dependent
re-prices. And it meets a bond market the Fed has handed back to itself: the same week the dots said higher, the
ten-year rallied to four-thirty-seven, because the marginal buyer is trading the energy disinflation and the
goods-volume collapse &mdash; PCs down eleven percent, phones down thirteen &mdash; over a forecast it does not
believe. The book is positioned on the bond market's side of that argument, and it is paying.</p>

<p>The Burry tell sits one layer deeper than the trade. For two years the consensus has held that AI is structurally
deflationary &mdash; cheaper cognition, automated everything. The next eighteen months are going to argue the
opposite at the checkout: the capex super-cycle is cannibalising the consumer-electronics supply chain, and it shows
up as either margin destruction at the box-makers or sticky core-goods inflation that traps the Fed, probably both.
The thing nobody is pricing is that the most disinflationary technology of the decade is, in its build-out phase, an
inflation machine. That is the structural observation; the tradeable edges off it are long breakevens, short the OEM
casualties, and a healthy respect for how durable a hawkish hold becomes once the price shock is on a kitchen-table
receipt.</p>

<p>So the posture into quarter-end is two-sided and re-pointed. The rate winners &mdash; the steepener near
plus-eighty-five, the duration longs green at last &mdash; get harvested and their stops trailed, not pressed, because
the silicon-inflation is the live thing that flattens them. The gold long is the casualty, held on its rule through a
broken four thousand, and hedged with defined risk rather than averaged down. The FOMC put spread is banked into its
expiry and replaced with a fresh August one for the payrolls-and-tariff tail. And the new money goes where the gap is:
long the inflation the curve denies, short the OEMs the memory cost is squeezing. The tape has priced the Micron print
as an all-clear. The brief's read is that the all-clear and the price shock are the same telegram, and only one line
of it has been read.</p>
""",

    "correlation_regime": """
<p><strong>1. Equities and yields decoupled &mdash; the bond market broke ranks with the Fed.</strong> The hot PCE
and a 68%-priced September hike should have lifted yields; instead the 2Y rallied to ~4.09% and the 10Y to ~4.37%
even as equities chopped. The break tells you the dominant driver is no longer the dots but the disinflation/growth
read underneath them &mdash; cheaper energy, collapsing goods volumes. The trade that respects it is the steepener and
the duration longs (MM-009/004/013), held and harvested, not a fight with the front-end rally.</p>

<p><strong>2. The AI complex split from itself &mdash; memory up, hardware down.</strong> The single most important
correlation break is intra-tech: Micron and the memory makers ripped on the supercycle while Apple and Microsoft &mdash;
the box-makers that buy the memory &mdash; led the Mag7 lower on the cost of it. The same shortage is a tailwind for
the suppliers and a margin headwind for the assemblers. That is a dominant-driver change inside the index, and it is
the entire basis of the memory-vs-OEM RV (MM-028).</p>

<p><strong>3. Gold decoupled from its own safe-haven reflex.</strong> A hot inflation print would normally bid gold;
instead it broke $4,000, because the real-rates and dollar engine overwhelmed the inflation-hedge engine and the Iran
de-escalation drained the haven bid &mdash; with $2bn of May ETF outflows confirming the spec long is leaving. Gold is
trading as a real-rates short, not an inflation hedge; that is why the book's long (MM-005) is the casualty and the
disciplined add is the defined-risk put-spread hedge (MM-029), not an average-down.</p>
""",

    "vol_skew": """
<p><strong>Vol eased as the Micron print drained the event premium &mdash; but the tails are mispriced for the wrong
reason.</strong> VIX sits ~18.9, off the 18.44 FOMC spike but elevated, and the term structure has re-steepened into
contango as the immediate catalyst (the print) passed (est. VIX9D ~17.5 · VIX ~18.9 · VIX3M ~19.5 · VIX6M ~20.0).
MOVE has eased toward ~104 as the front-end rally calmed the rates tape. The market is pricing the AI rebound as a
one-way melt-up into a quiet quarter-end &mdash; but June payrolls (Jul 2-3) land in the guidance vacuum, the July 4
EU-tariff deadline is a discrete cost-push risk, and the Mag7's own input-cost overhang is not in index vol. The trade
implication: re-establish cheap, defined-risk downside now that the banked MM-008 has expired &mdash; an August SPX
7,000/6,600 put spread (MM-030) struck below spot, structured for the discrete-event vol the guidance vacuum keeps
manufacturing rather than a chase of at-the-money premium. The complementary structure is the defined-risk GLD put
spread (MM-029), which owns the broken-$4,000 continuation while hedging the underwater bullion long. If the melt-up
extends, both decay cheaply; if either tail fires, the convexity is owned, not chased.</p>
""",

    "sector_rv": """
<p><strong>Leading (Thu Jun 25 / overnight):</strong> the memory/semis complex on the Micron blowout (the futures
ripped, NQ +2.15%); financials and rate-sensitive value as the curve re-steepens; the Dow (+0.14%) over the Nasdaq.
<strong>Lagging:</strong> the consumer-hardware Mag7 &mdash; Apple and Microsoft led the decline as the AI-DRAM cost
hit their own box-economics; gold miners as bullion broke $4,000; the broad energy complex on Brent $74; crypto as
BTC broke $60k. <strong>Today/next:</strong> May PCE + final-June UMich today; quarter-end rebalance Mon-Tue; ISM Jul
1; June payrolls Jul 2-3 &mdash; each a discrete event into the guidance vacuum.</p>

<p><strong>RV:</strong> The cleanest fresh sector RV is the memory-vs-OEM split the Micron print exposed: long the
memory/Micron complex (which the book already holds) vs SHORT the PC/handset OEMs &mdash; Dell, HP and the hardware
sleeve &mdash; that eat the DRAM cost and the -11%/-13% volume decline (MM-028). It pairs with the standing
financials-over-tech rotation (MM-025): a no-cuts, higher-for-longer Fed lifts net-interest margins while the
long-duration AI multiple carries both a higher discount rate AND the memory-cost overhang. Both are low beta to the
index, high beta to the silicon-inflation regime.</p>
""",

    "positioning": """
<p><strong>The crowd just re-embraced the AI complex on the Micron print &mdash; and is leaning the wrong way on two
things.</strong> Sentiment flipped risk-on overnight (the futures ripped on memory), so the pain trade in equities is
a continued narrowing into the memory winners that strands the index in the consumer-hardware names the same shortage
is squeezing (MM-028). In rates, fast money is still net-short duration post-Warsh, so the pain trade is the
front-end rally extending on a soft June payroll (Jul 2-3) &mdash; exactly the squeeze the rescued duration longs
(MM-004/013) are positioned to ride. In FX, the yen carry stayed crowded long-USD through a BoJ at 1%, braced against
the 13-month-high dollar at the MoF line (MM-007/021). The cleanest under-positioned trade is front-end inflation:
breakevens sit near cycle lows as the crowd shorts inflation on the oil collapse, blind to the silicon-push (MM-027).
The pain trade everywhere is the same &mdash; a market that read the energy disinflation as the whole inflation story.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged; the hold does not move the funding rate.
<strong>The Pozsar mechanic:</strong> trace the inflation everyone is debating back to a flow, and it is on the
hyperscalers' balance sheets. Microsoft, Google, Meta and Amazon are funding the AI build-out increasingly with debt,
and that capex bids roughly seventy percent of global memory output &mdash; a real-economy supply reallocation that
shows up as a relative-price shock, memory up while every memory-dependent good re-prices. The funding angle that
matters next is the collision of that issuance with a less-anchored long end: the term premium widened post-Warsh, and
a wave of hyperscaler IG supply to fund capex meets a bond market with no forward-guidance anchor. Watch IG issuance
and the 10Y together &mdash; the same capex that is the equity bull case is also a Treasury-market supply-and-term-
premium story. The balance-sheet task-force signal on QT/reserves feeds the same plumbing. The cleanest read is that
the AI cycle is now a macro funding flow, not just an equity theme.</p>
""",

    "tape_missing": """
<p><strong>The tape is reading the oil collapse as the end of inflation and missing the silicon-push that replaces
it.</strong> Front-end breakevens are falling with Brent, but DRAM is up 98% this year and a 15-25% consumer-hardware
repricing feeds core goods for quarters. The composition of inflation flipped from an energy push that is reversing to
a silicon push that is only beginning &mdash; and the curve is not pricing the second. The falsifiable level: 2Y
breakevens through their cycle low says the market is doubling down on the disinflation read; long breakevens (MM-027)
is the instrument that pays if core goods stay sticky into Q3.</p>

<p><strong>Just behind it: the bond market is right and the Fed is fighting last quarter's war.</strong> The hot May
PCE (4.1%) is a backward, peak-energy reading, and the 2Y rallying to ~4.09% on it says the marginal buyer agrees.
Either the energy/goods disinflation dominates and the Fed is tightening into it &mdash; the front end keeps rallying
(MM-004/013/009) &mdash; or the silicon-inflation validates the hike and the 2Y backs up to 4.35%. That level is the
falsifiable line; June payrolls (Jul 2-3) is the test. The two-sided structure of the book owns both ends of it.</p>

<p><strong>The Burry tell &mdash; the structural thing that just stopped being a forecast.</strong> For two years the
consensus has held that AI is structurally deflationary: cheaper cognition, automation, falling unit costs. The next
eighteen months will argue the opposite at the checkout. The build-out phase of the most disinflationary technology of
the decade is an inflation machine &mdash; it cannibalises the consumer-electronics supply chain, with every HBM wafer
for a GPU a wafer denied to a laptop or a phone (shipments down 11% and 13% this year). The first evidence is no
longer a thesis: Apple and Microsoft just raised hardware prices 15-25% and named the AI-DRAM shortage as the cause,
and the May PCE underneath the energy is sticky. Over the next two-to-three quarters this resolves as either margin
destruction at the box-makers or a core-goods inflation that traps the Fed &mdash; probably both. The equity index,
still concentrated in the seven names that are both the cause and the victims of the shortage, is the least prepared
for the world where the AI trade and the inflation trade are the same trade.</p>
""",

    "book_outlook": {
        "commentary": (
            "The book's defining holding just printed the quarter of the cycle &mdash; and the right move is to lock it, "
            "not celebrate it. <b>Micron (~32.2% of the book)</b> blew out (FY-Q3 EPS $25.11 vs $21.40, tightness "
            "'locked in beyond 2027'), confirming the AI-memory supercycle the book is levered to and putting the "
            "single-name gain at a fresh high. But a third of the book riding on one name AFTER its catalyst has "
            "fired, into a tape where the same DRAM shortage just repriced consumer hardware, is the moment to COLLAR "
            "and bank the gain &mdash; rich post-print calls finance protective puts for near-zero cost. The new regime "
            "cuts two ways through the rest of the book. The duration sleeve was RESCUED: the <b>US Treasury 1.25% "
            "2031</b> and <b>Siemens EUR IG</b> bonds rallied as the 2Y eased to ~4.09% and the 10Y to ~4.37% on the "
            "disinflation bid &mdash; the loss-harvest window is closing, not opening. <b>Xetra-Gold (4GLD)</b> is now "
            "the casualty, broken below $4,000 as the real-rates and dollar engine overwhelmed the haven bid &mdash; "
            "the tail hedge is the drawdown. The EUR-base book's heavy <b>USD sleeve (~72%)</b> keeps gaining as the "
            "dollar holds a 13-month high, and <b>SAP</b> / quality software carries none of the memory-cost overhang "
            "now weighing the box-makers. <b>TotalEnergies (TTE)</b> bleeds on Brent $74. The dominant action: collar "
            "Micron to bank the blowout, hedge the underwater gold with defined risk, and own the silicon-inflation "
            "the book's own AI concentration is creating."
        ),
        "outperform": [
            {"name": "Micron (~32.2%) — the blowout, now lock it", "why": "The FY-Q3 beat (EPS $25.11 vs $21.40) and "
             "the 'tightness beyond 2027' guide confirmed the supercycle and lifted the book's largest position to a "
             "fresh high. It leads today &mdash; but the play is to collar and bank the gain after the catalyst, not "
             "ride a third of the book naked into the next print."},
            {"name": "USD cash sleeve / USD assets (~72% of the book)", "why": "The EUR-base book is ~72% USD and the "
             "dollar holds a 13-month high as AI-led capital concentrates in US assets (out of crypto and gold) &mdash; "
             "the FX translation keeps adding. The book is structurally long the currency that is winning."},
            {"name": "The bond sleeve (UST 1.25% 2031, Siemens EUR IG)", "why": "RESCUED &mdash; both rallied as the 2Y "
             "eased to ~4.09% and the 10Y to ~4.37% on the energy/goods disinflation bid, even through a hot PCE. The "
             "duration drawdown reversed; this is the leg the rate longs (MM-004/013) mirror."},
        ],
        "underperform": [
            {"name": "Xetra-Gold (4GLD)", "why": "The casualty &mdash; gold broke $4,000 (first since November), -29% "
             "from the January peak, as a hawkish Fed, a 13-month-high dollar, the Iran de-escalation and ETF outflows "
             "drained both engines. The tail hedge is now the book's clean weekly drag; hedge it via MM-029, do not add."},
            {"name": "Consumer-hardware exposure (via SPY / the Mag7)", "why": "Apple and Microsoft led the Mag7 lower "
             "as the AI-DRAM shortage repriced their own box-economics &mdash; the book's index exposure carries the "
             "memory-cost overhang on the assemblers. The memory-vs-OEM RV (MM-028) is the hedge to the assembler leg."},
            {"name": "TotalEnergies (TTE)", "why": "The energy hedge keeps rolling over as Brent sits at ~$74 on the "
             "Iran normalisation, with a 13-month-high dollar a second drag on USD-priced crude. The disinflation half "
             "of the regime is a clean drag on the position."},
        ],
        "watch": [
            {"label": "Collar the 32.2% Micron AFTER the blowout — lock the gain while IVol is rich",
             "text": "MU just printed its catalyst, and post-print implied vol is elevated &mdash; the cheapest moment "
             "to collar a third of the book. Rich calls finance protective puts for near-zero cost, banking the "
             "supercycle gain while keeping defined upside. The fresh August SPX put spread (MM-030) is the index "
             "overlay now that the FOMC-tail spread (MM-008) is banked. Do not ride 32.2% naked into the next print."},
            {"label": "The bond sleeve: the harvest window is CLOSING — the duration rallied back",
             "text": "The UST 2031 and Siemens IG rallied as yields fell on the disinflation bid, so the loss-harvest "
             "entry has improved AWAY, not toward. Do not chase the swap into a rally; if you intend to roll into "
             "current coupons, wait for a yield-up spike on a hot payroll (Jul 2-3) or the silicon-inflation, not this "
             "rally. The rate longs (MM-004/013) say hold the duration here."},
            {"label": "Add the inflation hedge the book lacks — long front-end breakevens (MM-027)",
             "text": "The book is long both duration and the AI complex, and is structurally short the one risk its own "
             "concentration creates: silicon-driven goods inflation. Front-end breakevens near cycle lows are the cheap "
             "way to own it &mdash; an inflation hedge that pays if the DRAM-driven core-goods stickiness validates the "
             "Fed, exactly the scenario that would hurt the duration longs. Pair it with the gold put-spread (MM-029)."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> the Micron blowout is the AI all-clear &mdash; the supercycle is confirmed,
tightness runs beyond 2027, buy the memory complex and the broader AI trade; the May PCE validates a hawkish Fed, so
the macro is higher-for-longer but the AI engine is intact. Read the print as a clean growth signal and the dip in the
Mag7 as a buyable wobble.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> the same print is a cost-push, not just a growth
signal. The shortage that gave Micron $25 of EPS is the shortage that just put Apple's MacBook up $200 and is feeding
core goods while the curve prices the oil collapse as clean disinflation. The crowded side is long the AI complex as a
one-way bull and short front-end inflation on cheaper energy &mdash; blind to the silicon-push the AI boom itself is
creating. The cheaper side is long breakevens (MM-027), short the OEM casualties (MM-028), and on the bond market's
side of its disagreement with the Fed.</p>
""",

    "one_chart": """
<p class="theme">DRAM is the chart &mdash; memory prices are up 98% in 2026, and the curve is pricing inflation as if oil is the only input.</p>
<p>The single thing the market should watch is the divergence between the memory-price line and the front-end breakeven
line. DRAM is up 98% this year, Apple and Microsoft just passed 15-25% of it to consumers, and yet 2Y breakevens are
falling with Brent as if the energy collapse is the whole inflation story. Those two lines cannot both be right about
the next two quarters: either the silicon-push feeds core goods and breakevens are too low (long them, MM-027), or the
goods-volume collapse (-11% PCs, -13% phones) turns the shortage into demand destruction and the energy disinflation
wins outright (the rate longs MM-004/013/009 keep paying). The level that resolves it is the 2Y &mdash; a rally
through 4.05% on June payrolls (Jul 2-3) says the disinflation wins; a back-up to 4.35% says the silicon-inflation
validated the hike. Own both ends: long breakevens for the inflation the curve denies, the duration longs for the
disinflation it is finally pricing.</p>
""",

    "catalyst_calendar": [
        {"day": "Wed", "date": "Jun 24 ✓",
         "event": "Micron (MU) FY-Q3 — BLOWOUT (after close)",
         "consensus": "Reported AMC: revenue $41.5bn (vs ~$36.9bn est), adjusted EPS $25.11 (vs $21.40, +17%); CEO "
                      "Mehrotra called memory tightness 'locked in to persist beyond calendar 2027.' The book's LARGEST "
                      "position (~32.2%). Semis surged after-hours. Sources: TheStreet, CNBC, Finnhub.",
         "view": ("The supercycle confirmed — but it is also the cost-push. The same shortage that drove the beat just "
                  "repriced Apple/Microsoft hardware. The book's 32.2% concentration printed a fresh high; the action "
                  "is to COLLAR and bank, not ride it naked into the next print."),
         "asymmetry": "The blowout validated the long but exposed the second-order inflation: long memory pricing power, "
                      "short the OEM casualties (MM-028); own the silicon-inflation the curve denies (MM-027).",
         "dir": "up"},
        {"day": "Thu", "date": "Jun 25 ✓",
         "event": "Apple/Microsoft consumer price hikes + the Mag7 fade",
         "consensus": "Apple raised Mac/iPad up to +$300 (MacBook Air $1,099->$1,299), Microsoft put Xbox +$100-150 "
                      "from Aug 1, both citing the AI-DRAM shortage (memory +98% YTD). Nasdaq -0.46% to 25,358.60, "
                      "S&P flat 7,357.49, Dow +0.14% to 51,920.62. Sources: Euronews, Al Jazeera, CBS, TheStreet.",
         "view": ("The tell of the new regime: the AI build-out leaked into the CPI basket and the Mag7 fell on its own "
                  "supply chain's pricing power. The AI trade became the inflation trade."),
         "asymmetry": "Confirms the silicon-push the front-end breakeven curve is not pricing — long 2Y breakevens "
                      "(MM-027) is the under-positioned expression.",
         "dir": "down"},
        {"day": "Fri", "date": "Jun 26 — TODAY",
         "event": "May PCE (on the tape) + final-June UMich sentiment & inflation expectations",
         "consensus": "May PCE printed 4.1% headline (highest since Apr 2023) / 3.4% core (since Oct 2023), m/m +0.4% / "
                      "+0.3%, in line — an Iran-war-gasoline-driven May reading. Final-June UMich 5-10y inflation "
                      "expectations the watch. Sources: BEA, CBS, CNBC, University of Michigan.",
         "view": "Decompose it: a backward, peak-energy reading even as Brent sits at $74. The bond market already "
                 "trades the disinflation over it (2Y ~4.09%). Watch UMich long-run expectations for the silicon-push.",
         "asymmetry": "A jump in UMich long-run inflation expectations is the first survey evidence of the silicon-push "
                      "(bullish breakevens, MM-027); a soft read keeps the disinflation duration longs working.",
         "dir": "flat"},
        {"day": "Mon-Tue", "date": "Jun 29-30",
         "event": "Quarter / half-year-end — rebalancing flows + China June PMI (Jun 30)",
         "consensus": "Half-year-end after a strong Q2 equity run; model/pension rebalancing tends to sell equities and "
                      "buy bonds into the close. China June PMI Jun 30 — the read on the memory-shortage's other side "
                      "(China-tech input costs). Sources: market calendar, NBS.",
         "view": "A mechanical, non-fundamental flow: a rebalance that sells the Q2 winners (semis) and buys duration "
                 "reinforces the front-end rally (MM-009/004/013) into month-end. A soft China PMI is a global-goods tell.",
         "asymmetry": "The rebalance is a tailwind to the rate longs and a headwind to the just-bounced semis — a "
                      "reason not to chase the Micron-led melt-up into the close.",
         "dir": "flat"},
        {"day": "Wed", "date": "Jul 1",
         "event": "ISM Manufacturing (June) + JOLTS",
         "consensus": "June ISM Manufacturing (incl. prices-paid) and JOLTS job openings — the first hard reads on the "
                      "goods cycle and labour demand post-Micron. ISM prices-paid is the cleanest read on whether the "
                      "DRAM cost is bleeding into broad goods. Source: ISM, BLS.",
         "view": "ISM prices-paid is the silicon-inflation thermometer: a jump corroborates the cost-push (MM-027); a "
                 "soft new-orders/JOLTS print reinforces the goods-slowdown disinflation the duration longs ride.",
         "asymmetry": "Hot prices-paid + soft orders is the worst mix for the Fed (stagflationary) and the bull case for "
                      "long breakevens against the rate longs.",
         "dir": "flat"},
        {"day": "Thu-Fri", "date": "Jul 2-3",
         "event": "June PAYROLLS — the first labour read in the guidance vacuum (book-critical)",
         "consensus": "June non-farm payrolls (likely Jul 2 ahead of the Jul 3-4 holiday). The decisive input to the "
                      "September-hike pricing (~68%), and the first major labour print since Warsh removed forward "
                      "guidance — each number now its own vol event. Source: BLS.",
         "view": "The level that resolves the book's central binary: a soft print prices OUT the Sep hike, the 2Y rallies "
                 "through 4.05% and the rate longs (MM-004/013/009) extend; a hot print backs the 2Y to the 4.35% stop.",
         "asymmetry": "A soft payroll squeezes the crowded short-duration trade (MM-013 pays); a hot one validates the "
                      "hike and the silicon-inflation, pressuring the rate longs and paying the SPX put spread (MM-030).",
         "dir": "flat"},
        {"day": "Sat", "date": "Jul 4",
         "event": "EU-US trade deadline — autos to 25% if the EU does not ratify",
         "consensus": "Trump's deadline for the EU to ratify the trade deal or face autos/trucks tariffs to 25%; "
                      "Bessent has flagged tariffs could return to prior levels by early July. A second cost-push onto "
                      "the silicon one. Sources: CNN, Congress.gov, Reuters.",
         "view": "A re-escalation is a fresh tariff cost-push exactly when the Fed has no slack to absorb the "
                 "silicon-inflation — risk-off and EUR-supportive (the two-sided risk to short EUR/USD MM-012/024).",
         "asymmetry": "A deal is risk-on + EUR-supportive (caps the dollar trade); a re-escalation is a second cost-push "
                      "that compounds the silicon-inflation and pays the index put spread (MM-030).",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.662 (the stop). At ~1.651 — drifted offside as the Micron-led risk-on rebuilt the AUD bid; edge thinned, ~11 pips of room. Trim into strength; tight leash.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.37% — RESCUED, now green; the bond market trades the energy/goods disinflation over the hot PCE. The silicon-inflation (MM-027) is the offset. Harvest, don't press.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250 (breached). At ~$4,015 — BROKE $4,000, the casualty (~-11%), both engines drained. The min-hold rule holds it; hedge via MM-029, NOT an add.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~161.6 — offside, past the old 160 pin as the 13-month-high dollar dragged it up. Needs a vol shock (payrolls Jul 2-3) to break it. Defined-risk expression MM-021. Tight leash.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> BANKED into Jun-27 expiry at ~$45 (~+29%). The FOMC-tail hedge did its job (peak ~$60). Replaced by the fresh August 7,000/6,600 put spread (MM-030).</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+28bp, RE-STEEPENING on the front-end rally; ~+85%; target +60bp. The silicon-inflation re-flattens it — that's the risk. Trail the stop; hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182 (distant). At ~1.138. VINDICATED — DXY at a 13-month high, a durable dollar regime. Hold toward 1.13; add downside via MM-024. Two-sided risk: the Jul 4 EU-tariff deadline.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold to ~Jul 8. At ~4.09% — RESCUED, now green; rallied through the 4.162% entry even on a hot PCE as the bond market fights the dots. June payrolls Jul 2-3 is the test. Harvest, don't add.</li>
</ul>
""",

    "client_ammo": [
        {"q": "Micron blew out — why isn't this just a clean buy signal?",
         "a": ("Because the same thing that gave Micron a record quarter just raised the price of a MacBook. The AI "
               "build-out now eats about seventy percent of the world's memory, DRAM is up ninety-eight percent this "
               "year, and that shortage is both Micron's windfall and a cost-push: Apple and Microsoft hiked hardware "
               "prices fifteen to twenty-five percent and named it as the cause. The AI trade has quietly become an "
               "inflation trade. We own the winner but we're collaring it to bank the gain, not chasing it.")},
        {"q": "PCE came in hot at 4.1% — does that mean the Fed is right to stay hawkish?",
         "a": ("It's a backward-looking May number built on the Iran-war gasoline spike, and gasoline is gone &mdash; "
               "oil's at $74 and gold just broke $4,000. The inflation isn't ending, it's changing source: from energy, "
               "which is collapsing, to silicon, which is only starting. The bond market gets it &mdash; yields fell "
               "even on the hot print. We're positioned with the bond market: our rate trades are green and the "
               "steepener's up about eighty-five percent.")},
        {"q": "Why did the Mag7 fall if the AI news was good?",
         "a": ("Apple and Microsoft are the ones who buy the memory, not sell it &mdash; so the shortage that lifts "
               "Micron squeezes their margins, and their stocks led the decline. That split, memory up and "
               "box-makers down, is the cleanest trade out of this: long the memory makers' pricing power, short the "
               "hardware names paying for it. The book already owns the long side via Micron; the fresh leg is the "
               "short.")},
        {"q": "What should we do about Micron now?",
         "a": ("Collar it &mdash; now, after the print, while the option premiums are still rich. Micron is a third of "
               "the book and its catalyst has fired; riding that concentration naked into the next quarter is a risk "
               "question, not a conviction. Selling the rich calls to finance protective puts banks the supercycle gain "
               "for near-zero cost while keeping defined upside. The biggest position should not be the biggest "
               "unmanaged risk.")},
        {"q": "Is gold a buy down here after breaking $4,000?",
         "a": ("Not yet, and we're not adding to ours. Gold's trading as a real-rates short, not an inflation hedge &mdash; "
               "a hawkish Fed, a thirteen-month-high dollar, the Iran calm and two billion of ETF outflows all pulled "
               "the same way. We hold our position on its rule, but the disciplined move is a defined-risk put spread "
               "that owns the continuation lower and hedges the underwater long, not catching a falling knife.")},
        {"q": "What's the cleanest new trade out of all this?",
         "a": ("Owning the inflation the market thinks is disappearing. Everyone is reading cheaper oil as the end of "
               "inflation and pricing the front end accordingly &mdash; but the silicon-driven goods inflation is only "
               "beginning, and it's the one the Fed can't fix with rate hikes. We'd rather be long that, and short the "
               "hardware makers the memory cost is squeezing, than guess the next move in oil.")},
    ],

    "ideas_note": (
        "<p>The Micron blowout and the consumer price shock are the same event, so the fresh ideas trade the "
        "silicon-inflation the market is still filing under two headlines. <strong>Long 2Y breakevens (MM-027)</strong> "
        "&mdash; the marquee: the curve reads the oil collapse as clean disinflation and is missing the DRAM-driven "
        "core-goods stickiness; this owns the inflation a book long both duration and the AI complex otherwise lacks. "
        "<strong>Long memory vs short the OEMs (MM-028)</strong> &mdash; the supercycle is a margin transfer; the book "
        "holds the winners (MU), so the fresh leg is shorting Dell/HP, the box-makers eating the cost and the volume "
        "decline. <strong>GLD 3,800/3,500 put spread (MM-029)</strong> &mdash; defined-risk downside that hedges the "
        "underwater gold long after the $4,000 break. <strong>August SPX 7,000/6,600 put spread (MM-030)</strong> "
        "&mdash; the replacement index hedge after MM-008 was banked, for the payrolls + quarter-end + tariff tail. "
        "The rate winners (MM-009/004/013) are harvested and trailed; the offside legs (gold, USDJPY, EURAUD) are held "
        "on tight leashes or hedged, not added.</p>"
    ),

    "event_radar_note": (
        "<p>The AI trade became the inflation trade: Micron blew out (EPS $25.11 vs $21.40, tightness 'beyond 2027') "
        "and the SAME DRAM shortage repriced Apple/Microsoft hardware 15-25% &mdash; the Mag7 fell on its own supply "
        "chain (Nasdaq -0.46%, S&P flat). May PCE printed hot (4.1%) but on backward Iran-war gasoline, even as Brent "
        "$74 and gold broke $4,000. Yet yields FELL (2Y 4.09%, 10Y 4.37%) &mdash; the bond market trades the "
        "disinflation over the dots, rescuing the rate longs (steepener ~+85%). Ahead: May PCE + UMich TODAY; "
        "quarter/half-end Jun 29-30; ISM Jul 1; June PAYROLLS Jul 2-3 (the first labour read in the guidance vacuum); "
        "the EU-tariff deadline Jul 4. The fresh ideas own the silicon-inflation: long breakevens, long memory / short "
        "the OEMs, a gold put-spread hedge, and a fresh index put spread. Collar the 32.2% Micron after the blowout.</p>"
    ),

    "burry_tell": (
        "For two years the consensus has held that AI is structurally deflationary &mdash; cheaper cognition, "
        "automation everywhere, falling unit costs. The next eighteen months are going to argue the opposite at the "
        "checkout, and this week is the first evidence. The build-out phase of the most disinflationary technology of "
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
        "Micron (MU): POST-EARNINGS (reported Jun 24 AMC) — the BLOWOUT and the book's defining name. FY-Q3 revenue "
        "$41.456B (vs ~$36.9B est) and adjusted EPS $25.11 vs $21.40 (+17.3%, Finnhub-sourced), with the CEO calling "
        "memory tightness 'locked in beyond 2027'; sell side 51 buy / 3 hold / 1 sell. OVERBOUGHT reaction risk: the "
        "supercycle is confirmed, but the book already owns a 32.2% weight — the play is NEUTRAL/manage (collar to bank "
        "the gain), not chase. FedEx (FDX): POST-EARNINGS (Jun 23 AMC) — EPS 6.31 vs 6.02 (+4.78% beat), the "
        "global-freight read; FAIRLY PRICED, a constructive goods-cycle signal but no fresh asymmetry into the "
        "disinflation tape. JEF (Jun 24) MISSED (1.03 vs 1.17) and SNX (Jun 25) beat — both noted, neither a fresh idea."
    ),
    "earnings_why": (
        "The post-earnings window (Jun 23-26) brought four qualifying names; two carry signal. Micron is rendered "
        "POST-EARNINGS as the marquee: the +17.3% EPS beat and the 51/3/1 recommendation split are Finnhub-sourced, "
        "but because the stock has already re-rated and the book is a 32.2% holder, the trade is to manage the "
        "concentration (collar), not add — so it is carried in the book outlook and Trade Ideas as much as here. FedEx "
        "cleared the Industrials filter (Jun 23 AMC, +4.78% beat): a constructive read that the goods cycle is not "
        "collapsing, but a modest beat into a tape already trading the disinflation, so FAIRLY PRICED. Jefferies "
        "(Financials, Jun 24) missed at 1.03 vs 1.17 and TD Synnex (Jun 25) beat at 4.85 vs 4.18 — both inside the "
        "window, neither a differentiated idea. Excluded: names outside the Tech/Financials/Industrials/Utilities, "
        ">$10bn, US/Korea universe."
    ),

    "book_aim": (
        "Two-sided and on the right side of the bond market's disagreement with the Fed. The rate book is the winner: "
        "the 2s10s steepener (MM-009) ~+85% and the duration longs (MM-004/013) green for the first time in weeks as "
        "yields fell on the energy/goods disinflation even through a hot PCE; the short EUR/USD (MM-012) is vindicated "
        "by a 13-month-high dollar; the SPX put spread (MM-008) is banked into expiry (~+29%). The casualties are on "
        "the disinflation side — gold (MM-005) broke $4,000 and is held on its min-hold, hedged not added. For the "
        "rest of June and into payrolls: harvest and trail the rate winners (do NOT press them — the silicon-inflation "
        "is the live two-sided risk); hold the offside legs on tight leashes or defined-risk hedges; and rotate fresh "
        "risk into the silicon-inflation the market is mispricing — long 2Y breakevens (MM-027), long memory / short "
        "the OEMs (MM-028), a GLD put-spread hedge (MM-029), and a fresh August SPX put spread (MM-030). The urgent "
        "house-keeping: collar the 32.2% Micron AFTER the blowout to lock the gain. Own the silicon-inflation, not the "
        "energy headline."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the option line (MM-008) was "
                 "banked at a ~$45 model estimate into its Jun-27 expiry (+~29%).")
    },
    "idea_selection": [
        {"label": "Long 2Y inflation breakevens — own the silicon-push (MM-027)", "in": True,
         "text": ("The marquee idea. The curve reads the oil collapse as clean disinflation and is pulling front-end "
                  "breakevens down — but DRAM +98% and a 15-25% consumer-hardware repricing feed core goods for "
                  "quarters. Long 2Y breakevens owns the inflation the market is mistaking for disappearing, and it is "
                  "the inflation hedge a book long both duration and the AI complex otherwise lacks. Stop: -20bp.")},
        {"label": "Long memory vs short PC/handset OEMs (MM-028)", "in": True,
         "text": ("The DRAM supercycle is a margin transfer: Micron captures the price, Dell/HP eat the input cost and "
                  "the -11%/-13% volume decline. The book already owns the long leg via MU, so the fresh, "
                  "concentration-neutral expression is the SHORT — the box-makers who cannot fully pass the cost "
                  "through. Long who sets the price, short who pays it; stop ratio -4%.")},
        {"label": "GLD 3,800/3,500 put spread — hedge the broken-$4k gold long (MM-029)", "in": True,
         "text": ("Gold broke $4,000 with the real-rates and dollar engine intact and the haven bid drained. The book "
                  "is long gold on a min-hold and cannot add to a falling knife — so the disciplined move is to own "
                  "the continuation with defined risk, which simultaneously hedges the underwater long (MM-005 / "
                  "Xetra-Gold). Defined premium; max loss capped.")},
        {"label": "August SPX 7,000/6,600 put spread — re-set the index hedge (MM-030)", "in": True,
         "text": ("The FOMC-tail spread (MM-008) is banked into expiry; the reasons to carry index downside did not "
                  "expire with it. June payrolls (Jul 2-3), the quarter-end rebalance, the July 4 tariff deadline and "
                  "the Mag7's own memory-cost overhang are the tail, into a tape pricing the Micron rebound as one-way. "
                  "Struck below spot for cheap convexity; defined risk.")},
        {"label": "Rate winners (MM-009/004/013) — harvest and trail, don't press", "in": False,
         "text": ("The steepener ~+85% and the duration longs green on the disinflation bid. Held and trailed, not "
                  "added: the silicon-inflation (MM-027) is the live two-sided risk that re-flattens the curve and "
                  "backs the front end up. Let June payrolls resolve it; the breakeven long is the hedge to this leg.")},
        {"label": "No idea that merely chases the Micron melt-up", "in": False,
         "text": ("The consensus is buying the AI complex as a one-way all-clear. Adding more long-memory beta here, "
                  "into a 32.2% MU book, is the crowded side. The fresh ideas own the regime's second-order "
                  "inflation (breakevens, the OEM short) rather than the first-order growth headline.")},
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
            "id": "MM-2026-029", "trade": "Buy 3M GLD 3,800/3,500 put spread (hedge the gold long)",
            "asset_class": "Commodity (options)", "structure": "put spread",
            "entry": "~0.8% premium", "stop": "—", "target": "~4x at 3,500",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "3 months", "min_hold_days": 0,
            "thesis": ("Gold broke $4,000 for the first time since November and the structure that broke it is intact: "
                       "a hawkish Fed, a 13-month-high dollar, the Iran de-escalation draining the haven bid, and $2bn "
                       "of May ETF outflows. The book is long gold (MM-005) and the Fable book's Xetra-Gold and cannot "
                       "add to a falling knife on a min-hold — so the disciplined move is to own the CONTINUATION with "
                       "defined risk, which simultaneously hedges the underwater long. A put spread struck below the "
                       "broken figure pays toward $3,800-3,500 while capping the cost — both long the position and "
                       "short the tail until the min-hold elapses ~Jul 15."),
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
