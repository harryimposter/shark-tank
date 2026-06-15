#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-15 (Monday).

THE REGIME PIVOT vs the Jun 11 run: war premium -> peace dividend.
- US-Iran MoU announced Jun 14 by mediators; to be SIGNED Jun 19; ends the
  conflict within 60 days. 14-point draft: lift oil sanctions; Iran reopens the
  Strait of Hormuz within 30 days. Pakistan PM: final text reached. Iran FM:
  deal "never been closer." (ABC News, Reuters via Trading Economics, CNN.)
  PENDING — written as upcoming (signing Jun 19), NOT done.
  Caveats kept honest: renewed IDF strikes in the Beirut area Jun 14 (US
  restrained Iran's response); a conflicting Iranian-media draft; a senior
  Hezbollah commander (Ali Musa Daqduq) killed in S. Lebanon; Trump warned both
  sides not to "blow it."
- OIL COLLAPSED: Brent -4%+ Friday to below $86.5 — the lowest since early March
  — as the entire Kharg/war premium unwound. WTI below $85. (CNBC, TradingEconomics.)
  This is a forward-disinflation impulse that REHABILITATES the long-duration
  trades (MM-004 short 10Y, MM-013 short 2Y) that hot PPI had pressured Friday,
  and STOPS the oil longs (MM-002, MM-011). The book's MoU binary paid off on
  the duration side exactly as designed.
- Friday Jun 12 US close (risk-on): S&P +0.5% to 7,431.46; Nasdaq +0.31% to
  25,888.84; Dow +0.7% to 51,202.26. (CNBC, Yahoo Finance.)
- SpaceX (SPCX) debut Jun 12: +19% to close $160.95 (peaked $176.52, +31%
  intraday), >$2T market cap — biggest IPO ever ($75B raised). The feared
  liquidity drain did NOT drag the tape; risk rallied. (NPR, CNBC.)
- Adobe Jun 11 AMC: BEAT-AND-RAISE — record rev $6.62B, adj EPS $5.96, FY26
  guide RAISED to $24.35-24.45 EPS / $26.5-26.6B rev, first AI ARR print, $25B
  buyback. Stock -6.25% to a 52-wk low $218.09 — on CFO Dan Durn's abrupt exit
  to Marvell (eff. Jun 15) atop the CEO search. Governance, not fundamentals.
  (TIKR, Seeking Alpha, Yahoo Finance.)
- FOMC Jun 16-17 is Kevin Warsh's FIRST meeting as chair (Powell's term ended
  May 15). 98-99% priced HOLD at 3.50-3.75%. The event is the dot plot / a
  possible bias shift (easing -> neutral/tightening); Dec-26 hike odds ~54%.
  (Polymarket, TheStreet, CME FedWatch via IndexBox.)

Run:  python gen_2026_06_15.py
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
# SPX 7300/7000 put spread: S&P rallied back ABOVE 7,300 (Fri close ~7,431) so the
# spread is OUT of the money again — only time value + the FOMC tail remain.
levels["MM-2026-008"] = 38.0
# Brent 100/115 call spread: Brent collapsed to ~$84 on the MoU — $100 strike now
# ~$14 away, the catalyst is dead; mark near the $1 discipline level (then closed).
levels["MM-2026-011"] = 1.1

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
    "ADBE": "We are BUYERS. The -6% to a 52-week low ($218) was a beat-and-raise (record rev $6.62B, FY EPS guide "
            "raised, first AI ARR print, $25B buyback) sold purely on the CFO's exit to Marvell — governance, not "
            "fundamentals. An oversold ADBE here is the dislocation, not the breakdown. This is idea MM-014.",
    "XOM":  "Energy is rolling over as the war premium bleeds out (Brent below $86.5, lowest since March). Oversold "
            "is NOT a buy here — the MoU signs Jun 19 and the Strait reopens within 30 days; we'd sell income against "
            "energy (reverse convertible), not chase the dip until the sanctions-relief supply is digested.",
    "NVDA": "Constructive lower: the 195-235 consolidation is intact and the peace-driven risk-on (S&P +0.5% Fri) "
            "supports the AI cohort. An oversold NVDA into support is where the desk adds, not where it fades.",
    "MU":   "We like it higher: HBM is sold out into the AI-memory supercycle and the SpaceX-drain fear that hung "
            "over semis never materialised. Oversold here is the dip we add on — book's largest equity position.",
    "ORCL": "POST-PRINT capex overhang still digesting (FY27 ~$70B capex + ~$40B raise vs $638B RPO). Oversold but we "
            "own this through the capital-protected note (idea 101), not the naked equity — participate in the OCI "
            "re-rate, protected against the dilution.",
    "FDX":  "Read-only into the print (~Jun 18 AMC). Peace + cheaper jet fuel is a margin tailwind; tariff-driven "
            "freight-volume softness is the offset. Neutral until the guide — the bellwether read on global trade.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("Peace Dividend: Oil -$8 on US-Iran MoU (signs Jun 19); Warsh's First FOMC Wed; "
          "SpaceX +19% Debut")
regime_note = (
    "The regime has flipped. For two weeks the tape priced an escalating war premium that peaked Jun 11 with "
    "Trump's threat to seize Kharg Island. Over the weekend it reversed: on June 14 mediators announced a "
    "US-Iran memorandum of understanding, to be SIGNED June 19, that ends the conflict within 60 days. The "
    "14-point draft lifts oil sanctions and commits Iran to reopen the Strait of Hormuz within 30 days; "
    "Pakistan's PM said a final text is agreed and Iran's foreign minister said the deal has 'never been closer.' "
    "Written as PENDING — the signing is Friday, not done. (Sources: ABC News, Reuters via Trading Economics, CNN.) "
    "The market did not wait. Brent collapsed more than 4% on Friday to below $86.5 — its lowest since early "
    "March — as the entire war premium unwound; WTI fell below $85. (CNBC, Trading Economics.) "
    "That oil crash is the single most important macro fact this morning, and it works two ways. First, it is a "
    "forward-disinflation impulse: a $40-off-the-highs move in crude is a CPI cut the post-PPI hawkish FedWatch "
    "has not yet booked. It REHABILITATES the long-duration trades (MM-004 short 10Y, MM-013 short 2Y) that hot "
    "PPI had put under pressure Friday — the 10Y eased to 4.48% and the 2Y to 4.09% as oil fell. Second, it STOPS "
    "the oil longs: MM-002 (long Brent) broke its $87 weekly-close exit and is closed; MM-011 (the $100/$115 call "
    "spread) is closed near its discipline level as the Hormuz tail it owned is being legislated away. This is the "
    "book's MoU binary resolving exactly as it was designed to — the duration side pays, the oil hedge is "
    "surrendered. "
    "Risk rallied into the news. Friday's US close: S&P +0.5% to 7,431.46, Nasdaq +0.31% to 25,888.84, Dow +0.7% "
    "to 51,202.26 (CNBC, Yahoo). SpaceX debuted on Nasdaq under SPCX and closed +19% at $160.95 (peaked $176.52, "
    "+31% intraday), a >$2T market cap and the largest IPO ever at ~$75B raised — and the feared liquidity drain "
    "never dragged the tape (NPR, CNBC). Europe ran harder: DAX +1.76% to 24,635, STOXX 600 +1.8%, on lower oil "
    "and peace hopes — good for the long-DAX / short-Nasdaq ratio (MM-010). "
    "The one corporate wrinkle is Adobe: a clean beat-and-raise Thursday night (record rev $6.62B, adj EPS $5.96, "
    "FY26 guide raised to $24.35-24.45, the first AI ARR print, a $25B buyback) fell 6.25% to a 52-week low of "
    "$218.09 — not on the numbers but on CFO Dan Durn's abrupt departure to Marvell (effective today) on top of "
    "the ongoing CEO search. The market sold the org chart, not the P&L. (TIKR, Seeking Alpha, Yahoo.) "
    "Everything now points at Wednesday. FOMC June 16-17 is Kevin Warsh's FIRST meeting as chair — Powell's term "
    "ended May 15. A hold at 3.50-3.75% is 98-99% priced; the event is the dot plot and whether the new, more "
    "hawkish chair shifts the bias from easing toward neutral or tightening (Dec-26 hike odds are already ~54%). "
    "The relief rally has crushed VIX to 17.7 and priced Warsh's debut as a non-event. That is the tail worth "
    "owning. The honest caveats on the peace trade: the deal is not signed until Friday, the IDF struck the Beirut "
    "area again Saturday (the US restrained Iran's response), a conflicting Iranian-media draft is circulating, and "
    "Trump warned both sides not to 'blow it.' Managed de-escalation, not yet a done peace."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

# ── Discretionary closes — the MoU breaks the oil-long thesis ────────────────────
# Note: with Brent below its $84 hard stop, mark_to_market auto-closes MM-002 as
# STOPPED. The call below is a fallback (no-op once already closed) for the case
# where Brent sits between the $84 stop and the $87 weekly-close exit.
book.step("Discretionary closes on the peace MoU")
_brent_lvl = levels.get("MM-2026-002") or 86.3
book.discretionary_close(
    trades, "MM-2026-002", _brent_lvl,
    reason=("MoU to be signed Jun 19 (Strait reopens within 30 days, sanctions lifted) removed the re-escalation "
            "premium the trade was built on. Brent broke the $87 weekly-close exit and kept falling below $84 — "
            "the lowest since March. The book's MoU binary paid off on the duration side instead; the oil hedge is "
            "surrendered by design, not by surprise."))
book.discretionary_close(
    trades, "MM-2026-011", 1.1,
    reason=("Peace deal deflated the Hormuz tail the call spread owned: with Brent ~$84 the $100 strike is $16 away "
            "and the catalyst is dead. Closed near the $1 discipline level to recover residual premium rather than "
            "ride a defined-risk position to zero."))

# ── Per-trade enrichment (instrument descriptions, full thesis, catalysts, risks,
#    and per-criterion WHY for the conviction breakdown) ────────────────────────
TRADE_ENRICHMENTS = {
    "MM-2026-001": {
        "instrument": (
            "EUR/AUD spot FX cross-rate. EUR = euro (ECB-managed); AUD = Australian dollar "
            "(commodity-linked, RBA-managed). Driven by relative ECB-vs-RBA rate paths, iron-ore "
            "prices (Australia's largest export = AUD tailwind), global risk sentiment, and the "
            "2-year eurozone-vs-Australia rate spread."
        ),
        "fundamental_thesis": (
            "The ECB delivered its +25bp hike to 2.25% on Jun 11 and Lagarde signalled 'not pre-committing to a "
            "particular rate path' — the pause that removes the marginal EUR buyer. With the hike behind it, EUR "
            "has no forward catalyst, while the AUD keeps a terms-of-trade tailwind from firm iron ore. The "
            "peace-driven risk-on is a mild AUD positive (commodity-currency beta), which argues for patience rather "
            "than pressing; the cross drifting around 1.642 is consistent with a slow grind lower toward target."
        ),
        "catalysts": [
            "ECB pause signal (Jun 11) now in the price — no forward EUR catalyst",
            "Iron-ore price action / any China demand or PBoC stimulus headline = AUD tailwind",
            "RBA June meeting — a hawkish hold supports AUD vs a paused ECB",
            "FOMC Jun 16-17 — a USD move spills into both legs; watch the EUR cross-rate, not just EUR/USD",
        ],
        "risks": (
            "Risk-off flips the commodity-currency beta and AUD sells harder than EUR; a China demand shock pulls "
            "iron ore and the AUD tailwind; an ECB official re-opens the hike door and EUR squeezes. Stop 1.662."
        ),
        "breakdown_why": {
            "gap":          "3/3 — the cross sits a full figure above where the 2yr spread implies, with a "
                            "pause-signalling ECB against an RBA still leaning tight.",
            "catalyst":     "1/2 — the dated ECB catalyst has passed; what remains is slower-burn (RBA, iron ore).",
            "positioning":  "1/2 — EUR longs into the hike are now trapped flat, offering some unwind fuel.",
            "confirmation": "1/2 — the cross sold off from 1.66 but has not broken cleanly lower.",
            "stop_quality": "1/1 — 1.662 is a clean technical level, tight to the target move.",
        },
    },
    "MM-2026-004": {
        "instrument": (
            "US 10-year Treasury yield. Shorting the yield = buying duration (long bonds / 10Y "
            "futures / TLT). Driven by the Fed path (front-end anchored), inflation expectations, "
            "fiscal supply/term premium, and the safe-haven bid."
        ),
        "fundamental_thesis": (
            "This is now the WINNING side of the MoU binary, and the original thesis is back. The trade was entered "
            "on the view that an oil-disinflation impulse would pull headline CPI lower and force a less-hawkish "
            "Fed. Friday's hot PPI (+6.5% YoY) was a genuine headwind to that — but the weekend oil collapse "
            "overwhelms it. Brent down ~$40 from the war highs to ~$84 is a forward CPI cut the post-PPI FedWatch "
            "has not booked, and the 10Y has already eased to 4.48% from 4.55%. The position is roughly flat to "
            "entry (4.44%) and the catalyst is two days out: if Warsh delivers a data-dependent hold Wednesday, the "
            "10Y extends toward 4.30%. The honest risk: Warsh leans hawkish on the dots regardless of oil, and the "
            "long end sells on supply rather than rallying on disinflation. Do not add into the print; let the FOMC "
            "resolve it."
        ),
        "catalysts": [
            "Oil collapse (Brent <$86.5, lowest since March) = forward CPI cut not yet in FedWatch",
            "FOMC dot plot Jun 16-17 — data-dependent hold = 10Y toward 4.30%; hawkish dots = stop tested",
            "May Retail Sales Jun 17 — soft print reinforces the disinflation read",
            "Treasury supply at the long end — the offsetting risk to the duration rally",
        ],
        "risks": (
            "Warsh delivers an explicitly hawkish dot plot despite the oil relief; the long end sells on fiscal "
            "supply rather than rallying on disinflation; the MoU collapses pre-signing and oil/inflation snap back. "
            "Stop 4.65% (now ~4.48%, ~17bp away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — restored from 1: the oil crash re-opens the disinflation gap that hot PPI had "
                            "narrowed. The net inflation signal is now firmly lower.",
            "catalyst":     "2/2 — FOMC Jun 16-17 and Retail Sales Jun 17 are dated, direct, 10Y-relevant events.",
            "positioning":  "1/2 — consensus is still cautiously short duration; squeeze fuel on a dovish hold.",
            "confirmation": "1/2 — the 10Y has eased 7bp off the high on the oil move; one confirming leg.",
            "stop_quality": "1/1 — 4.65% is a clear technical level; ~17bp of risk.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold in USD. The inverse of real rates, driven by the Fed path "
            "and real yields, USD strength, EM central-bank buying, geopolitical premia, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "Honest re-mark: two of gold's three engines just weakened. The geopolitical safe-haven bid is "
            "deflating on the MoU (gold ~$4,310, softer on the month), and the oil collapse softens the "
            "inflation-hedge engine. What is left — and what the position now depends on — is the real-rates engine: "
            "if Warsh signals a data-dependent hold Wednesday and real yields fall, gold re-rates. The stop ($4,250) "
            "was touched Jun 10 but the 45-day minimum hold (to ~Jul 15) keeps the position structural, not "
            "tactical. This is the loser of the MoU binary on the safe-haven leg, held for its FOMC optionality and "
            "the structural EM-central-bank bid, not chased."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — dovish/data-dependent hold = real yields down, gold up; hawkish = capped",
            "US-Iran MoU signing Jun 19 — further de-escalation bleeds the residual safe-haven premium",
            "Oil/inflation path — a sustained crude drop softens the inflation-hedge leg",
            "EM central-bank Q2 gold purchases (China, India, Turkey — structural buyers)",
        ],
        "risks": (
            "Warsh delivers hawkish dots and real yields surge; the MoU signs cleanly and the last safe-haven "
            "premium drains; a gold-specific spec flush. Stop $4,250 (touched Jun 10; 45-day min-hold override "
            "keeps it open to ~Jul 15)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — gold's decoupling from real rates is still a mispricing, but the geopolitical "
                            "leg that widened it is now deflating.",
            "catalyst":     "2/2 — FOMC dots are a dated, direct real-rate catalyst with clean gold transmission.",
            "positioning":  "1/2 — positioning is not extreme; not a cleanly crowded long.",
            "confirmation": "0/2 — no fresh technical confirmation; price is well below entry ($4,310 vs $4,523).",
            "stop_quality": "1/1 — $4,250 is a defined level; the min-hold rule is the discipline mechanism.",
        },
    },
    "MM-2026-007": {
        "instrument": (
            "USD/JPY spot FX (dollar-yen). Driven by the US-Japan 2yr rate differential, BoJ "
            "normalisation, the Fed path, risk sentiment (JPY is a crisis safe-haven), and Japanese "
            "MoF intervention risk above ~162-163."
        ),
        "fundamental_thesis": (
            "USD/JPY at ~160.2 with the MoF on intervention watch and a BoJ September hike >50% priced. The "
            "differential that has kept yen weak is set to narrow from both ends — a BoJ that is normalising and a "
            "Fed whose oil-driven disinflation argues against further tightening. The peace-driven risk-on is a "
            "near-term headwind (carry stays on when vol is low), which is why this is a patient short with the "
            "MoF ceiling at 163 as the backstop, not a momentum trade."
        ),
        "catalysts": [
            "BoJ meetings — September hike increasingly priced; hawkish language = yen rally",
            "MoF intervention — explicit warnings above 162-163; physical action forces stop-hunting",
            "FOMC Jun 16-17 — a data-dependent Fed narrows the US-Japan differential",
            "Japan CPI — any upside surprise supports BoJ normalisation",
        ],
        "risks": (
            "A hawkish Warsh widens the differential again; the BoJ delays or sounds dovish (Ueda has surprised "
            "dovishly before); low-vol risk-on keeps the carry trade alive. Stop 163.00."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is ~1500 pips above where the 2yr differential has historically implied.",
            "catalyst":     "2/2 — BoJ hike probability and the MoF intervention threat are both dated and credible.",
            "positioning":  "1/2 — the yen carry trade is crowded long-USD; unwind needs a catalyst to fire.",
            "confirmation": "1/2 — price rejected the 160+ handle once; one confirmation of the ceiling.",
            "stop_quality": "1/1 — 163.00 is a clean MoF-intervention ceiling; 2.8 pts risk vs ~10 to target.",
        },
    },
    "MM-2026-008": {
        "instrument": (
            "SPX Jun-27 7300/7000 put spread — defined-risk. Buy the 7300 put, sell the 7000 put. "
            "Max profit $300/unit if SPX <=7000 at expiry; max loss = the $35 premium; break-even "
            "~7265. Driven by the SPX level (~7,431), implied vol (VIX ~17.7), and time to expiry."
        ),
        "fundamental_thesis": (
            "The hedge did its job through CPI and Oracle, marked as high as ~$80 (+129%), and has now given most "
            "of that back: Friday's relief rally took the S&P to ~7,431, back ABOVE the 7,300 strike, so the spread "
            "is out of the money again and marked ~$38 — only time value plus the FOMC tail. The single reason to "
            "keep it is Wednesday: Warsh's first dot plot sits inside the Jun 27 expiry, and the relief rally has "
            "crushed VIX to 17.7, making this residual downside convexity cheap to hold into a binary the market is "
            "treating as a non-event. Hold through FOMC; the residual value IS the dot-plot tail."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — hawkish dots push SPX toward 7,000 and the spread toward intrinsic",
            "May Retail Sales Jun 17 — a soft print plus hawkish dots is the bear combination",
            "MoU signing risk Jun 19 — a collapse pre-signing reopens the geopolitical downside",
        ],
        "risks": (
            "SPX grinds higher on a clean dovish hold and the spread expires near zero; time decay into Jun 27; a "
            "VIX crush as the relief rally extends. Max loss remains the $35 premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — downgraded from 3: the in-the-money move has been given back; the gap now is "
                            "the under-priced FOMC tail, not realised intrinsic value.",
            "catalyst":     "2/2 — FOMC and Retail Sales both land inside expiry.",
            "positioning":  "2/2 — the market is complacent again (VIX 17.7); maximum room for a re-pricing.",
            "confirmation": "0/2 — the SPX is back above the strike; no technical confirmation right now.",
            "stop_quality": "1/1 — defined-risk; max loss is the $35 premium. The stop is conceptual.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (receive/own cut optionality), short "
            "the 10Y (short fiscal-supply risk). Pays when 10Y-minus-2Y widens. Currently ~2Y 4.09% "
            "/ 10Y 4.48%, spread ~+39bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "The steepener is the cleaner of the two duration expressions now. The oil-disinflation impulse pulls "
            "the front end down (a data-dependent Fed) while the long end is anchored by fiscal supply — the exact "
            "configuration that steepens. Entered at +15bp after an 18-month inversion, the spread sits ~+39bp, "
            "+160% on the position. A dovish-leaning Warsh Wednesday is the accelerant; a hawkish dot plot that "
            "flattens the front end is the risk. Min-hold to ~Jul 16 keeps it structural through the meeting."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — a pause signal drops the 2Y faster than the 10Y = steepens",
            "Oil disinflation — pulls front-end cut pricing without compressing the long end",
            "Treasury supply at the back end — long-end auctions selling off = steepens",
            "May Retail Sales Jun 17 — a soft print reinforces the front-end rally",
        ],
        "risks": (
            "A hawkish Warsh forces aggressive front-end repricing and the curve re-flattens; a global safe-haven "
            "bid flattens via the long end; a Fed hike inverts the front end. Stop: spread below -10bp."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the curve is still structurally underpriced versus the late-cycle mean off an "
                            "18-month inversion; the near-term path is FOMC-dependent.",
            "catalyst":     "2/2 — FOMC dots and Retail Sales are direct, dated front-end catalysts.",
            "positioning":  "1/2 — front-end positioning offers some squeeze fuel on a dovish hold.",
            "confirmation": "1/2 — the spread has held its widening through the oil move; one confirmation.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-010": {
        "instrument": (
            "Long DAX / short Nasdaq Composite price ratio. Buy German large-caps (financial/industrial "
            "heavy), sell US tech. The ratio rises when DAX outperforms — driven by ECB-vs-Fed "
            "divergence, EUR/USD, European banks vs US tech, and AI-multiple compression."
        ),
        "fundamental_thesis": (
            "Both legs worked into the weekend. Friday the DAX ran +1.76% to 24,635 (Deutsche Bank +6.6%) on lower "
            "oil, peace hopes and the delivered ECB hike feeding bank NIMs, while the Nasdaq added only +0.31% — the "
            "ratio recovers off its 0.949 near-stop. The structural case is intact: European financials with a "
            "tightening ECB behind them against a US tech complex still digesting Oracle's capex shock and facing a "
            "hawkish-leaning Warsh. Hold through FOMC; the divergence is structural, not sentiment."
        ),
        "catalysts": [
            "ECB hike (delivered Jun 11) — DAX financials NIM tailwind, confirmed",
            "FOMC Jun 16-17 — a hawkish dot plot pressures US tech multiples = ratio up",
            "Oracle capex overhang — keeps a lid on the US AI-cloud cohort",
            "EUR/USD — a softer euro flatters DAX exporters and the USD-denominated ratio",
        ],
        "risks": (
            "A clean dovish hold re-rates the Nasdaq and the ratio falls toward the 0.943 stop; a EUR squeeze on "
            "hawkish ECB commentary hurts DAX exporters; German growth fears resurface. Stop ratio 0.943."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the cross-region divergence (financials vs AI multiples) is a real structural gap.",
            "catalyst":     "1/2 — the dated ECB catalyst has passed; what remains is event-dependent (FOMC, tech).",
            "positioning":  "2/2 — the US-tech long is crowded; any unwind is maximum fuel for the ratio.",
            "confirmation": "1/2 — the Friday DAX-vs-Nasdaq decoupling confirmed; not yet a sustained 2.",
            "stop_quality": "1/1 — 0.943 is a clean technical level; ~tight risk vs the target.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "The sell-the-fact is executing. The ECB delivered +25bp Jun 11 and Lagarde's 'not pre-committing' "
            "removed the forward catalyst for the EUR longs built from 1.08 to 1.15; EUR/USD has been fading and "
            "sits ~1.157. The complication today is the peace-driven risk-on, which is mildly EUR-supportive — so "
            "this is the most contested of the FX positions. It is held because the rate-path asymmetry still "
            "favours the dollar (a paused ECB vs a Fed that holds with a hawkish bias), and it pairs cleanly with "
            "long DAX. Respect the 1.182 stop; do not add into the FOMC."
        ),
        "catalysts": [
            "ECB pause (Jun 11) — sell-the-fact catalyst, in train",
            "FOMC Jun 16-17 — a hawkish-bias hold supports the dollar vs a paused ECB",
            "Risk-on/peace flows — the offsetting EUR-supportive force to watch",
            "Spec positioning unwind — EUR longs near multi-year highs",
        ],
        "risks": (
            "Peace risk-on lifts EUR broadly; US data disappoints and EUR/USD re-rates higher; a safe-haven EUR bid "
            "in a risk-off shock. Stop 1.182."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the mispricing is contained: the ECB hike is priced and the gap is the "
                            "press-conference reaction, not a regime-level dislocation.",
            "catalyst":     "2/2 — FOMC Jun 16-17 is a precise, dated catalyst with a clear payoff trigger.",
            "positioning":  "1/2 — EUR spec longs near multi-year highs provide unwind fuel.",
            "confirmation": "1/2 — EUR/USD has faded from the post-ECB high; one confirming move.",
            "stop_quality": "1/1 — 1.182 is a clean prior high; tight risk vs the target.",
        },
    },
    "MM-2026-013": {
        "instrument": (
            "Short US 2-year Treasury yield (receive 2Y swap / long 2Y notes). The 2Y is the market's "
            "real-time forecast of the Fed path over two years — the most policy-sensitive point on the "
            "curve."
        ),
        "fundamental_thesis": (
            "Rehabilitated alongside MM-004. Friday's hot PPI re-armed hike pricing and pushed the 2Y as a risk; "
            "the weekend oil collapse reverses it. A $40-off crude move is a disinflation impulse that argues "
            "against the December hike the curve is ~54% pricing, and the 2Y has eased to 4.09%. The structural "
            "thesis — that the front end over-extrapolated a single payroll into a hiking cycle — is back in force "
            "with the oil tailwind behind it. The FOMC is still the gate: a data-dependent Warsh drops the 2Y "
            "15-20bp; a hawkish debut sends it toward the 4.35% stop. Min-hold through Jun 16. Do not add."
        ),
        "catalysts": [
            "Oil collapse = forward disinflation that fades the Dec-26 hike pricing (~54%)",
            "FOMC dot plot Jun 16-17 — data-dependent hold drops the 2Y; hawkish dots test the stop",
            "May Retail Sales Jun 17 — a soft print reinforces the no-further-hike read",
            "Jobless claims — any spike weakens the hiking case",
        ],
        "risks": (
            "Warsh delivers a hawkish debut dot plot regardless of oil; the MoU collapses pre-signing and "
            "inflation expectations snap back; a re-acceleration in the labour data. Stop 4.35%; min-hold through "
            "Jun 16."
        ),
        "breakdown_why": {
            "gap":          "2/3 — restored from 1: the oil-disinflation impulse re-widens the gap between the 2Y "
                            "and the justified hiking probability.",
            "catalyst":     "2/2 — the FOMC dot plot is a precise, dated catalyst with direct 2Y transmission.",
            "positioning":  "2/2 — the market is still positioned for a hawkish Warsh; squeeze fuel on a dovish hold.",
            "confirmation": "1/2 — the 2Y eased on the oil move; one confirming leg.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~26bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-014": {
        "instrument": (
            "Adobe Inc. (ADBE) — US software. Creative Cloud, Document Cloud, Experience Cloud, plus "
            "the Firefly generative-AI suite. Revenue is subscription ARR; the bull/bear axis is whether "
            "generative AI is net-new ARR (upsell) or cannibalises Creative Cloud seats."
        ),
        "fundamental_thesis": (
            "Decompose the -6.25%. Adobe printed a clean beat-and-raise Thursday night: record revenue $6.62B, "
            "adjusted EPS $5.96, FY26 guidance RAISED to $24.35-24.45 EPS on $26.5-26.6B revenue, the first "
            "meaningful AI ARR disclosure, and a fresh $25B buyback. The stock fell to a 52-week low of $218.09 — "
            "and not one cent of the move was the fundamentals. It was CFO Dan Durn's abrupt exit to Marvell "
            "(effective today) landing on top of an unresolved CEO search: two C-suite transitions in three months. "
            "The market sold the org chart and ignored a P&L that improved. The AI-tax-vs-tailwind question that "
            "hung over the name resolved firmly tailwind. Buy the governance dislocation; the buyback is a floor."
        ),
        "catalysts": [
            "New CFO appointment / CEO-search resolution — removes the governance overhang",
            "$25B buyback execution — a structural bid under a 52-week-low stock",
            "AI ARR disclosure cadence — each print that shows net-new ARR re-rates the cohort",
            "Software-cohort sentiment into and out of FOMC",
        ],
        "risks": (
            "The governance overhang deepens (a weak CFO hire, or the CEO search drags); a broad software de-rate "
            "on a hawkish FOMC; AI ARR decelerates next quarter and the cannibalisation bears are vindicated. "
            "Stop $199 (below the 52-week low and the round number)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — a beat-and-raise at a 52-week low is a clear price-vs-fundamentals gap; not a 3 "
                            "because the governance overhang is real and near-term.",
            "catalyst":     "1/2 — the catalysts (CFO hire, CEO search) are real but not precisely dated.",
            "positioning":  "2/2 — sentiment is washed out at a 52-week low into a $25B buyback; the crowd is short "
                            "the org chart, not the business.",
            "confirmation": "1/2 — the raised guide is the fundamental confirmation; the chart needs a base.",
            "stop_quality": "1/1 — $199 is a clean level below the low and the round number.",
        },
    },
    "MM-2026-015": {
        "instrument": (
            "Long transports (IYT — airlines, rail, freight) vs short energy (XLE — integrated oil, "
            "E&P, services). A cross-sector relative-value ratio expressing the oil price as a "
            "two-sided input: a cost for transports, a revenue for energy."
        ),
        "fundamental_thesis": (
            "The peace dividend reprices two sectors in opposite directions off the same number. Brent is down ~$8 "
            "from the Kharg highs to ~$84 and the MoU points lower still — jet fuel is ~25-30% of airline opex and "
            "diesel is the freight cost line, so the move is a direct margin tailwind to transports and a top-line "
            "hit to energy. The trade is market-neutral-ish and carries low beta to Wednesday's FOMC binary, which "
            "is the point two days before the Fed: own the de-escalation theme without taking a directional macro "
            "bet. Size it on the ratio, not the legs."
        ),
        "catalysts": [
            "MoU signing Jun 19 + Strait reopening (30 days) — sanctioned Iranian barrels = lower-for-longer oil",
            "Crude inventory / OPEC+ response to sanctions relief",
            "FedEx print (~Jun 18) — the freight read-through on volumes and fuel",
            "Summer travel demand data — the airline top-line confirmation",
        ],
        "risks": (
            "The MoU collapses pre-signing and oil snaps back (energy outperforms, transports give back); a global "
            "growth scare hits cyclical transports harder than integrated energy; OPEC+ cuts to defend price. "
            "Stop: ratio -3% from entry."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the two sectors have not fully repriced the oil move relative to each other yet.",
            "catalyst":     "1/2 — the oil-path catalysts are real but the relative move is gradual.",
            "positioning":  "1/2 — energy length built during the war premium is now offside and unwinding.",
            "confirmation": "1/2 — Friday's lower-oil tape started the rotation; one confirming session.",
            "stop_quality": "1/1 — a fixed ratio stop (-3%) is a clean, defined failure threshold.",
        },
    },
    "MM-2026-016": {
        "instrument": (
            "SPX put structure expiring just after the FOMC (e.g. a Jul-2 6950/6650 put spread, ~1% of "
            "notional). A cheap, defined-risk way to own equity downside convexity across Warsh's first "
            "dot plot — separate from, and nearer-dated than, the held MM-008."
        ),
        "fundamental_thesis": (
            "The relief rally has done the work for us. VIX collapsed to 17.7 and the market now prices Warsh's "
            "first FOMC at 98-99% hold as a non-event — exactly when a new, more hawkish chair's debut dot plot is "
            "the least-priced binary on the calendar (Dec-26 hike odds are already ~54%). Low vol makes downside "
            "convexity cheap right before the event that can re-rate it. This is the fresh expression of the FOMC "
            "tail now that MM-008 has decayed back out of the money; defined risk, ~1% of notional, expiring just "
            "after the meeting."
        ),
        "catalysts": [
            "FOMC dot plot Jun 16-17 — a hawkish bias shift is the payoff trigger",
            "May Retail Sales Jun 17 — a soft print plus hawkish dots is the bear combination",
            "Post-rally positioning — complacency (VIX 17.7) is the fuel",
        ],
        "risks": (
            "A clean dovish hold and the structure decays to near zero; the relief rally extends and VIX falls "
            "further; the premium bleeds with no catalyst. Max loss is the ~1% premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — implied vol is mispricing a binary the market has decided to ignore.",
            "catalyst":     "2/2 — the FOMC is a precise, dated, high-variance event inside the tenor.",
            "positioning":  "2/2 — maximum complacency (VIX 17.7) right before a new chair's debut dots.",
            "confirmation": "0/2 — no technical confirmation; this is a pre-event convexity buy.",
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
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},   # FOMC at 3.50-3.75% (held); funding unmoved
    {"name": "MOVE", "level": "~104 (est)", "chg": "easing", "dir": "down"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Fri 12 Jun · TradingView"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~104", "chg": "easing (est)", "dir": "down"},
]

# Per-trade open-book notes (shown in the "yesterday, graded" table).
NOTES = {
    "MM-2026-001": "ECB pause behind it (Jun 11); no forward EUR catalyst. AUD keeps the iron-ore tailwind; peace risk-on a mild AUD positive. Slow grind lower from ~1.642. Stop 1.662.",
    "MM-2026-004": "REHABILITATED. The weekend oil collapse (Brent <$86.5) is a forward CPI cut that overwhelms Friday's hot PPI; 10Y eased to 4.48%, roughly flat to entry. WINNING side of the MoU binary. FOMC Wed is the gate; data-dependent hold = 10Y toward 4.30%. Do not add. Stop 4.65%.",
    "MM-2026-005": "Re-marked honestly. Two of three engines weakened — geopolitical bid deflating on the MoU, inflation-hedge softened by the oil crash. Held for the real-rates engine (a dovish Warsh) + structural EM bid. ~$4,310. Min-hold to ~Jul 15; stop $4,250 (touched, override).",
    "MM-2026-007": "Near flat ~160.2. Differential set to narrow (BoJ Sept hike >50% priced; a data-dependent Fed). Low-vol risk-on is the near-term headwind. MoF ceiling 163 is the backstop. Stop 163.00.",
    "MM-2026-008": "Gave back the spike. S&P back above 7,300 (Fri ~7,431) so the put spread is OUT of the money again, marked ~$38 vs $35 (+8.6%). The only reason to hold is the FOMC tail inside Jun 27 expiry — VIX 17.7 makes it cheap convexity. Hold through Wed; do not lift.",
    "MM-2026-009": "BEST OPEN POSITION (+160%). The cleaner duration expression: oil-disinflation pulls the front end down while fiscal supply anchors the long end = steepens. ~+39bp; target +60bp. A dovish Warsh is the accelerant. Min-hold to ~Jul 16; stop -10bp.",
    "MM-2026-010": "Both legs worked Friday: DAX +1.76% (Deutsche Bank +6.6%) vs Nasdaq +0.31% on lower oil + ECB NIM relief — ratio recovering off the 0.949 near-stop. Structural divergence intact into FOMC. Stop ratio 0.943.",
    "MM-2026-012": "Sell-the-fact executing; EUR/USD ~1.157. Most contested FX leg — peace risk-on is mildly EUR-supportive, but the rate-path asymmetry (paused ECB vs hawkish-bias Fed) still favours USD. Pairs with long DAX. Do not add into FOMC. Stop 1.182.",
    "MM-2026-013": "REHABILITATED. Oil collapse fades the Dec-26 hike pricing (~54%); 2Y eased to 4.09%. The over-extrapolation thesis is back with the oil tailwind behind it. FOMC Wed is the gate; data-dependent hold drops it 15-20bp. Min-hold through Jun 16; stop 4.35%. Do not add.",
}

# Notes for the closed ledger (keyed by id; falls back to the exit reason).
CLOSED_NOTES = {
    "MM-2026-006": ("STOPPED June 8. Q2 beat but the Q3 AI guide ($16.0B vs buy-side $17.2B) missed the number that "
                    "mattered at 41x; payrolls finished it."),
    "MM-2026-002": ("The US-Iran MoU (announced Jun 14, signs Jun 19, reopens the Strait within 30 days) removed the "
                    "re-escalation premium the long was built on. Brent broke the $87 weekly-close exit and the $84 "
                    "stop, falling below $84 — its lowest since March. The book's MoU binary paid off on the "
                    "duration side instead; the oil hedge surrendered by design, not by surprise."),
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
    {"datum": "MM-008 option mark (model est. from spot — OTM, ~$38)", "source": "Model estimate (no live option feed)", "asof": TODAY, "stale": True},
    {"datum": "US-Iran MoU: announced Jun 14 by mediators; to be SIGNED Jun 19; ends conflict within 60 days; 14-point draft lifts oil sanctions + reopens Strait of Hormuz within 30 days. PENDING.",
     "source": "ABC News + Reuters (via Trading Economics) + CNN (corroborated)", "asof": "2026-06-14", "stale": False},
    {"datum": "Brent closed below $86.5 Fri Jun 12 (-4%+, lowest since early March); WTI below $85 — war premium unwound",
     "source": "CNBC + Trading Economics (corroborated)", "asof": "2026-06-12", "stale": False},
    {"datum": "Fri Jun 12 US close: S&P 7,431.46 (+0.5%); Nasdaq 25,888.84 (+0.31%); Dow 51,202.26 (+0.7%)",
     "source": "CNBC + Yahoo Finance (corroborated)", "asof": "2026-06-12", "stale": False},
    {"datum": "SpaceX (SPCX) debut Jun 12: +19% to $160.95 (peaked $176.52); >$2T cap; $75B raise — biggest IPO ever",
     "source": "NPR + CNBC (corroborated)", "asof": "2026-06-12", "stale": False},
    {"datum": "Adobe (ADBE) Q2 Jun 11 AMC: beat-and-raise (rev $6.62B, adj EPS $5.96, FY26 guide raised, $25B buyback); -6.25% to 52-wk low $218.09 on CFO Durn exit to Marvell",
     "source": "TIKR + Seeking Alpha + Yahoo Finance (corroborated)", "asof": "2026-06-11", "stale": False},
    {"datum": "US Treasury close Jun 12: 10Y 4.48%, 2Y 4.09% (2s10s ~+39bp) — eased as oil collapsed",
     "source": "ETFtrends + Fed H.15 (corroborated)", "asof": "2026-06-12", "stale": False},
    {"datum": "VIX 17.68 close Jun 12 (from 19.44 Jun 11) — vol crushed on the relief rally",
     "source": "Yahoo Finance / Trading Economics", "asof": "2026-06-12", "stale": False},
    {"datum": "FOMC Jun 16-17: Warsh's first meeting as chair (Powell term ended May 15); 98-99% priced HOLD at 3.50-3.75%; dot plot/bias-shift the event; Dec-26 hike odds ~54%",
     "source": "Polymarket + TheStreet + CME FedWatch (via IndexBox)", "asof": "2026-06-15", "stale": False},
    {"datum": "FedEx (FDX) FY Q4 — reporting ~Jun 18 AMC; consensus EPS $5.80 (-4.5% YoY); beat last 4 quarters",
     "source": "Yahoo Finance / TipRanks", "asof": "2026-06-15", "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-06-12", "stale": True},
]

earnings_ideas = [
    {
        "ticker": "ADBE", "company": "Adobe Inc",
        "report_date": "2026-06-11", "report_timing": "AMC",
        "mode": "POST-EARNINGS", "direction": "Long",
        "conviction_score": 6, "conviction_label": "High — data gap flagged",
        "conviction_rationale": (
            "A clean beat-and-raise (record rev $6.62B, adj EPS $5.96, FY26 guide raised to $24.35-24.45 EPS / "
            "$26.5-26.6B rev, first AI ARR print, $25B buyback) sold off 6.25% to a 52-week low of $218.09 PURELY on "
            "CFO Dan Durn's abrupt exit to Marvell (effective Jun 15) atop the CEO search. The dislocation is "
            "governance, not fundamentals — the asymmetry is real and attributable to the data."
        ),
        "research_conflict": False,
        "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 1, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "BEAT-AND-RAISE: record revenue $6.62B, adj EPS $5.96; FY26 guide RAISED to $24.35-24.45 EPS on "
            "$26.5-26.6B revenue; first meaningful AI ARR disclosure; new $25B buyback.",
            "REACTION: -6.25% to a 52-week low $218.09 — the driver was CFO Dan Durn leaving for Marvell "
            "(effective Jun 15), on top of the ongoing CEO search. Two C-suite transitions in three months.",
            "READ: the AI-tax-vs-tailwind question resolved firmly tailwind; the market sold the org chart. "
            "This is the basis for trade idea MM-014 (long the dislocation).",
        ],
        "what_moves_it": ("A new CFO hire / CEO-search resolution removes the overhang; continued AI-ARR disclosure "
                          "re-rates the whole software cohort. Bear: governance drags or AI ARR decelerates."),
        "client_talking_point": ("Adobe beat and raised, printed AI ARR, and announced a $25B buyback — and fell to "
                                 "a 52-week low because the CFO is leaving. That is a governance dislocation, not a "
                                 "fundamental one. We are buyers (idea MM-014); the buyback is a floor."),
        "reaction_tag": "OVERSOLD",
        "eps_actual": "$5.96", "eps_estimate": "$5.01", "eps_surprise_pct": "+19%",
        "stock_reaction_pct": "-6.25%", "implied_upside_to_pt": "mid-teens % to consensus PT",
    },
    {
        "ticker": "FDX", "company": "FedEx Corp",
        "report_date": "2026-06-18", "report_timing": "AMC",
        "mode": "PRE-EARNINGS", "direction": "Neutral",
        "conviction_score": 5, "conviction_label": "Medium conviction",
        "conviction_rationale": None, "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 1, "catalyst": 2, "positioning": 1},
        "pillar_confidence": {"asymmetry": "estimated", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Reports ~Jun 18 AMC. Consensus EPS $5.80 (-4.5% YoY from $6.07); FedEx has beaten in each of the last "
            "four quarters.",
            "The bellwether read on global trade and the freight cycle into Warsh's first FOMC. Two-sided: peace + "
            "cheaper jet fuel/diesel is a margin tailwind; tariff-driven volume softness is the offset.",
            "The guide, not the headline, is the catalyst — watch the freight-volume and DRIVE cost-out commentary.",
        ],
        "what_moves_it": ("Volume trajectory and the fuel-cost tailwind vs the tariff drag. The read-through feeds "
                          "trade idea MM-015 (long transports vs short energy)."),
        "client_talking_point": ("FedEx is the freight bellwether — it tells us whether the tariff drag or the "
                                 "cheaper-fuel tailwind is winning. We do not pre-position the print; we use it to "
                                 "size the transports-vs-energy RV (idea MM-015)."),
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
        "PEACE DIVIDEND. A US-Iran MoU (announced Jun 14, signs Jun 19) collapsed Brent below $86.5 — the lowest "
        "since March — unwinding the entire war premium. That oil crash is a forward CPI cut that rehabilitates the "
        "book's long-duration trades (MM-004/013) and stops the oil longs (MM-002/011 closed). Risk rallied Friday "
        "(S&P +0.5% to 7,431; SpaceX +19% debut to $160.95). Adobe beat-and-raised but fell 6% on its CFO's exit — "
        "a governance dislocation, not fundamentals. Everything points at Warsh's FIRST FOMC, Wed Jun 16-17: a hold "
        "is 98-99% priced and VIX has been crushed to 17.7 — the dot-plot tail is the cheapest binary on the board."
    ),

    "summary_narrative": """
<p>The regime flipped over the weekend. For two weeks the tape priced an escalating war premium that peaked
Thursday with Trump's threat to seize Kharg Island. On Saturday the mediators delivered the opposite: a
US-Iran <strong>memorandum of understanding</strong>, announced June 14 and set to be <strong>signed June
19</strong>, that ends the conflict within 60 days. The 14-point draft lifts oil sanctions and commits Iran
to reopen the Strait of Hormuz within 30 days; Pakistan's prime minister said a final text is agreed and
Iran's foreign minister said the deal has &ldquo;never been closer.&rdquo; Written as pending &mdash; the
signing is Friday, not done. (Sources: ABC News, Reuters via Trading Economics, CNN.)</p>

<p>The market did not wait for the signature. Brent collapsed more than 4% on Friday to <strong>below
$86.5</strong> &mdash; its lowest since early March &mdash; as the entire war premium drained out; WTI fell
below $85. (CNBC, Trading Economics.) That crash is the single most important macro fact this morning, and it
cuts two ways. First, it is a forward-disinflation impulse: crude down roughly $40 from the war highs is a CPI
cut that the post-PPI hawkish FedWatch has not yet booked, and it <strong>rehabilitates the long-duration
trades</strong> (MM-004 short 10Y, MM-013 short 2Y) that Thursday's hot PPI had put under pressure &mdash; the
10Y eased to 4.48% and the 2Y to 4.09%. Second, it <strong>stops the oil longs</strong>: MM-002 (long Brent)
broke its $87 weekly-close exit and is closed; MM-011 (the $100/$115 call spread) is closed near its discipline
level as the Hormuz tail it owned is legislated away. This is the book's MoU binary resolving exactly as it was
built to &mdash; the duration side pays, the oil hedge is surrendered.</p>

<p>Risk rallied into the news. Friday's US close: the S&amp;P rose 0.5% to 7,431.46, the Nasdaq added 0.31% to
25,888.84, the Dow gained 0.7% to 51,202.26. (CNBC, Yahoo.) <strong>SpaceX</strong> debuted on Nasdaq under
SPCX and closed <strong>+19% at $160.95</strong> (it peaked at $176.52, +31% intraday) for a market cap above
$2 trillion &mdash; the largest IPO ever at roughly $75B raised &mdash; and the liquidity drain that was feared
last week never dragged the tape. (NPR, CNBC.) Europe ran harder still: the DAX rose 1.76% to 24,635 (Deutsche
Bank +6.6%) and the STOXX 600 added 1.8% on lower oil and peace hopes, which is precisely the configuration the
long-DAX / short-Nasdaq ratio (MM-010) was built for.</p>

<p>The one corporate wrinkle is Adobe. A clean <strong>beat-and-raise</strong> Thursday night &mdash; record
revenue $6.62B, adjusted EPS $5.96, FY26 guidance raised to $24.35&ndash;24.45, the first AI ARR print, and a
$25B buyback &mdash; fell 6.25% to a 52-week low of $218.09. Not on the numbers: on CFO Dan Durn's abrupt
departure to Marvell, effective today, landing on top of the unresolved CEO search. The market sold the org
chart, not the P&amp;L, and the AI-tax-vs-tailwind question resolved firmly tailwind. We are buyers of the
dislocation (idea MM-014). (TIKR, Seeking Alpha, Yahoo.)</p>

<p>Everything now points at Wednesday. FOMC June 16&ndash;17 is <strong>Kevin Warsh's first meeting as
chair</strong> &mdash; Powell's term ended May 15. A hold at 3.50&ndash;3.75% is 98&ndash;99% priced; the event
is the dot plot and whether the new, more hawkish chair shifts the bias from easing toward neutral or
tightening (December hike odds are already ~54%). The relief rally has crushed VIX to 17.7 and priced Warsh's
debut as a non-event &mdash; which makes the dot-plot tail the cheapest binary on the board. The honest caveats
on the peace trade: the deal is not signed until Friday, the IDF struck the Beirut area again Saturday (the US
restrained Iran's response), a conflicting Iranian-media draft is circulating, and Trump warned both sides not
to &ldquo;blow it.&rdquo; Managed de-escalation, not yet a done peace.</p>
""",

    "takeaways": [
        "<strong>The regime flipped from war premium to peace dividend.</strong> A US-Iran MoU was announced "
        "Jun 14 by mediators and is set to be signed Jun 19, ending the conflict within 60 days; the 14-point "
        "draft lifts oil sanctions and reopens the Strait of Hormuz within 30 days. Written as PENDING — the "
        "signing is Friday, not done. The caveats are real: renewed IDF strikes in the Beirut area Saturday, a "
        "conflicting Iranian-media draft, and Trump's warning not to 'blow it.' (ABC News, Reuters via Trading "
        "Economics, CNN.)",

        "<strong>Oil collapsed and that is the trade.</strong> Brent fell more than 4% Friday to below $86.5 — "
        "the lowest since early March — unwinding the entire war premium; WTI below $85. This is a forward CPI "
        "cut the post-PPI hawkish FedWatch has not booked. It REHABILITATES the long-duration trades (MM-004 "
        "short 10Y, MM-013 short 2Y) — the 10Y eased to 4.48%, the 2Y to 4.09% — and STOPS the oil longs. The "
        "book's MoU binary resolved exactly as designed. (CNBC, Trading Economics.)",

        "<strong>Two oil legs closed; the duration side paid.</strong> MM-002 (long Brent) broke its $87 "
        "weekly-close exit and is closed at ~$84; MM-011 (the $100/$115 call spread) is closed near its $1 "
        "discipline level as the Hormuz tail it owned is being legislated away. The 2s10s steepener (MM-009, "
        "+160%) and the rehabilitated rates longs are the other side of the same binary — that is the value of "
        "owning both sides of a catalyst rather than guessing the resolution.",

        "<strong>Risk rallied; the SpaceX drain never came.</strong> Friday: S&amp;P +0.5% to 7,431.46, Nasdaq "
        "+0.31%, Dow +0.7%. SpaceX (SPCX) debuted +19% to $160.95 (peaked $176.52), >$2T cap, the biggest IPO "
        "ever — and the feared $75B liquidity drain failed to drag tech. Europe ran harder: DAX +1.76% to "
        "24,635. The long-DAX / short-Nasdaq ratio (MM-010) is recovering off its near-stop. (NPR, CNBC, Yahoo.)",

        "<strong>Adobe is a governance dislocation, not a fundamental one.</strong> A beat-and-raise (record rev "
        "$6.62B, adj EPS $5.96, FY26 guide raised to $24.35-24.45, first AI ARR print, $25B buyback) fell 6.25% "
        "to a 52-week low of $218.09 — because CFO Dan Durn is leaving for Marvell (effective today) on top of "
        "the CEO search. The AI-tax-vs-tailwind question resolved tailwind. We buy the dislocation (idea MM-014); "
        "the buyback is a floor. (TIKR, Seeking Alpha, Yahoo.)",

        "<strong>The SPX hedge gave back the spike — hold it for the FOMC tail.</strong> The 7300/7000 put spread "
        "(MM-008) marked as high as ~$80 (+129%) through CPI and Oracle; Friday's rally took the S&amp;P back "
        "above 7,300, so it is out of the money again, marked ~$38. The only reason to hold is Wednesday: Warsh's "
        "dot plot is inside the Jun 27 expiry and VIX at 17.7 makes the residual convexity cheap. Do not lift.",

        "<strong>FOMC Jun 16-17 is the whole week, and the market is complacent.</strong> A hold is 98-99% "
        "priced; the event is the dot plot and whether the new, more hawkish chair shifts the bias toward "
        "tightening (Dec-26 hike odds ~54%). With VIX crushed to 17.7, the debut dot plot is the least-priced "
        "binary on the calendar. That is the tail the held put spread and the fresh idea (MM-016) own. Plus "
        "Empire State + Industrial Production today, Retail Sales Wed, and FedEx (~Jun 18) on the freight cycle.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "MoU signs clean + Warsh data-dependent hold — disinflationary melt-up",
         "body": "The MoU is signed Jun 19, the Strait reopening is confirmed, and Brent settles toward $80-83. "
                 "Warsh emphasises the oil-disinflation impulse, signals a data-dependent hold and keeps a cut on "
                 "the table for H2 — the 2Y falls 15-20bp, the curve steepens, equity risk re-opens led by the "
                 "beaten-up software cohort (Adobe). Risk up · rates down · dollar soft · oil down · gold "
                 "consolidates."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "Peace holds, Warsh hawkish-neutral — relief rally digests",
         "body": "The deal signs but messily; Brent holds $84-88 on sanctioned-barrel uncertainty. Warsh holds at "
                 "3.50-3.75% and shifts the bias to neutral — no cut signal, no hike signal — with firm "
                 "language on inflation vigilance. The 2Y holds ~4.05-4.15%, the steepener grinds, equities "
                 "range after the Friday pop. Risk mixed · rates steady · dollar firm · oil soft · gold flat."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "MoU collapses pre-signing OR Warsh hawks up the dots",
         "body": "The Iranian-media draft fractures the deal before Friday and oil snaps back toward $95-100 on "
                 "re-escalation; AND/OR Warsh delivers an explicitly hawkish debut dot plot (a hike penciled in) "
                 "on the still-hot PPI evidence — the 2Y jumps toward the 4.35% stop, the rates longs are "
                 "pressured, AI multiples compress and the S&amp;P retraces toward 7,000 where the put spreads "
                 "pay. Risk down · rates up · dollar up · oil/gold spike."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is a single price: Brent below $86.5. Decompose what it does. A crude move
of roughly $40 off the war highs is not a commodity story &mdash; it is a <strong>monetary</strong> story,
because it is a forward disinflation impulse arriving exactly as Kevin Warsh prepares his first dot plot. The
FedWatch curve repriced hawkishly after Thursday's hot PPI (+6.5% YoY) and is still carrying ~54% odds of a
December hike. That pricing was built on a producer-price pipeline that an $86 Brent undercuts. The
non-consensus read: the oil collapse has quietly handed the new chair the cover to stay patient, and the market
&mdash; fixated on Warsh's hawkish reputation &mdash; is not pricing the dovish-hold path. That is why the
rehabilitated rates longs (MM-004, MM-013) and the steepener (MM-009) are the cleanest expressions in the book.</p>

<p>The counter-intuitive hook is the equity tape. Consensus spent last week fearing the SpaceX IPO as a $75B
liquidity drain that would force selling across tech. The opposite happened: SPCX debuted +19% to $160.95, the
broad market <em>rose</em>, and the drain that was supposed to crater semiconductors never materialised. The
lesson is about flows, not fundamentals &mdash; a marquee new issue in a risk-on tape pulls money <em>in</em>
(retail and momentum chasing the debut) rather than only draining it out. The book never traded the drain
thesis; it is noted here as a consensus error that resolved.</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong>
oil down hard, the 10Y at 4.48%, a 2s10s curve at +39bp, an equity tape making new local highs, and a beaten
software cohort (Adobe at a 52-week low on a beat-and-raise). <strong>What is priced:</strong> a 98-99% FOMC
hold and, beneath it, a complacent VIX at 17.7 that treats Warsh's debut as a non-event. <strong>Consensus
narrative:</strong> &lsquo;the new chair is a hawk, so the risk is a hawkish surprise.&rsquo; The gap &mdash;
and the alpha &mdash; is that the same complacent vol that under-prices a hawkish surprise <em>also</em>
under-prices a dovish one; the oil collapse makes the dovish-hold path more likely than the market believes,
and either tail is cheap to own at VIX 17.7.</p>

<p>Go around the world. <strong>Asia:</strong> lower oil is an unambiguous positive for the energy-importing
North-Asian complex (Japan, Korea, India); the AI-memory supply chain (HBM, Micron) is intact and the
SpaceX-drain fear that hung over semis is gone. <strong>Japan:</strong> USD/JPY ~160 with the MoF on watch and
a BoJ September hike >50% priced &mdash; the carry unwind is a question of when, and a low-vol risk-on tape
delays it. <strong>Europe:</strong> the DAX's +1.76% Friday on lower oil plus delivered ECB NIM relief is the
long-DAX / short-Nasdaq thesis working; European financials are the cleanest beneficiary of a tightening ECB
into a peace dividend.</p>

<p>The political angle is the one the market is under-weighting. The MoU is a Trump-administration deliverable
days before a contested signing, and the incentive to declare victory is enormous &mdash; which is precisely
why the conflicting Iranian-media draft (US withdrawals, reconstruction funding) matters: the two sides may not
be signing the same document. The non-consensus political read is that the <em>announcement</em> is real but
the <em>terms</em> are not yet reconciled, so the oil market's straight-line move to $86 has front-run a
signature that could still slip. That is the asymmetry behind not chasing crude lower here, even as the oil
longs are surrendered on the stop.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> the FOMC dot-plot binary in both directions (VIX 17.7 is
complacent); the dovish-hold path that the oil collapse has quietly made more likely; the Adobe re-rate once
the CFO seat is filled. <strong>Fairly priced:</strong> the FOMC hold itself (98-99%); the ECB pause; the DAX
NIM tailwind. <strong>Fully priced:</strong> the straight-line peace move in oil (Brent at $86 has front-run an
unsigned deal). <strong>Over-priced (at risk):</strong> the consensus framing that the only FOMC risk is a
hawkish one &mdash; the oil-disinflation impulse cuts the other way.</p>
""",

    "wrap": """
<p>The second-order effect the consensus is missing this morning is monetary, not geopolitical: an $86 Brent is
a rate cut the Federal Reserve has not yet acknowledged, arriving two days before a new chair has to publish his
first set of dots. Everyone is watching the peace deal for the oil price. The trade is what the oil price does to
the Fed.</p>

<p>Start with the number that moved everything. Brent fell more than 4% on Friday to below $86.5 a barrel, its
lowest since early March, as the market priced a US-Iran memorandum of understanding announced June 14 and
scheduled to be signed June 19 (Sources: ABC News, Reuters via Trading Economics, CNN). The fourteen-point draft
lifts oil sanctions and reopens the Strait of Hormuz within thirty days. Two weeks ago this brief was carrying a
Kharg Island seizure tail and a $130 Bloomberg forecast; today that tail is being legislated away. The oil book
paid for that view on the way up and surrenders it now on the way down: the long Brent position broke its
eighty-seven-dollar weekly-close exit and is closed, and the hundred-dollar call spread is closed near its
discipline level. There is no regret in that. The whole point of running both sides of the MoU binary &mdash;
long oil against long duration &mdash; was that one of them would be wrong, and the other would be more right.
The duration side is the winner.</p>

<p>Because the same oil collapse is a forward disinflation impulse, and it lands at the worst possible moment for
a hawkish narrative. Thursday's producer-price print was genuinely hot, +6.5% year-on-year, and the FedWatch
curve repriced toward a December hike on it. But a forty-dollar move down in crude is the single fastest
disinflationary force in the macro toolkit, and it undercuts the pipeline the PPI was measuring. The two rates
longs that were under pressure on Friday &mdash; short the 10Y, short the 2Y &mdash; are rehabilitated: the
ten-year eased to 4.48% and the two-year to 4.09%, and the 2s10s steepener is the cleanest expression of the
configuration, with the front end falling on disinflation while fiscal supply anchors the long end. The
consensus has decided that the only risk from Kevin Warsh's first meeting is a hawkish surprise. The oil price
has quietly made the dovish-hold path more likely than that framing allows.</p>

<p>The equity tape confirmed the regime change rather than fighting it. The S&amp;P rose half a percent to
7,431, the Nasdaq added a third of a percent, and SpaceX &mdash; the largest initial public offering in history
&mdash; debuted up nineteen percent to close at $160.95, above a two-trillion-dollar valuation, with the
liquidity drain that consensus feared nowhere in evidence (NPR, CNBC). Europe was stronger still, the DAX up
1.76% on lower oil and the delivered ECB hike feeding bank net interest margins, which is the long-DAX /
short-Nasdaq ratio doing precisely what it was constructed to do. The put spread that protected the book through
CPI and Oracle has given back most of its gain as the index rallied back above the seven-thousand-three-hundred
strike; it is held now for one reason only, which is that Wednesday's dot plot sits inside its expiry and a VIX
crushed to 17.7 has made that residual convexity cheap.</p>

<p>The single corporate story worth the client's time is Adobe, because it is a clean lesson in what the market
will and will not forgive. The company beat and raised &mdash; record revenue, raised full-year guidance, the
first real artificial-intelligence ARR disclosure, a twenty-five-billion-dollar buyback &mdash; and the stock
fell more than six percent to a fifty-two-week low because the chief financial officer is leaving for Marvell on
top of an unfinished chief-executive search (TIKR, Seeking Alpha, Yahoo). The fundamental question that has
hung over the name for a year, whether generative AI eats the software incumbent or feeds it, was answered in
the company's favour, and the equity sold anyway on the org chart. That is a governance dislocation, not a
fundamental one, and it is the cleanest single-name long in this brief.</p>

<p>The book's posture into the week is therefore disciplined and two-sided. The oil longs are closed on their
stop without regret; the rates longs and the steepener are rehabilitated and held but not added to ahead of the
Fed; the SPX put spread and a fresh, cheaper put structure own the dot-plot tail that VIX 17.7 is giving away;
the long-DAX ratio and the short-EUR position carry the cross-region and FX views; and the one new directional
bet, long Adobe, is idiosyncratic enough to be uncorrelated to Wednesday's binary. The honest caveat sits over
all of it: the peace deal is not signed until Friday, the IDF struck Lebanon again on Saturday, and the two
sides may not be signing the same document. The tape has priced a clean peace. The brief has not.</p>
""",

    "correlation_regime": """
<p><strong>1. Oil and rates re-coupled the right way.</strong> For two weeks oil and yields rose together on the
war-premium/stagflation read. That broke Friday: Brent collapsed below $86.5 and the 10Y eased to 4.48% — oil
down is now disinflation, and bonds rallied with it. The correlation flipped from the stagflation regime
(positive oil/yields) back to the disinflation regime (oil down, bonds up). That flip is the whole bull case for
the rehabilitated rates longs (MM-004, MM-013).</p>

<p><strong>2. Equities and the SpaceX 'drain' decoupled from the fear.</strong> Consensus had the largest IPO
ever as a $75B liquidity drain that would force tech selling. Instead SPCX debuted +19% and the broad market
rose. The expected negative correlation (new issue up, existing tech down) simply did not appear — a risk-on
tape pulled money in, not out. The drain thesis is dead; do not trade it.</p>

<p><strong>3. Adobe decoupled from its own fundamentals.</strong> A beat-and-raise printed a 52-week low. The
normal correlation between an improving P&amp;L and the stock broke on a single governance event (CFO exit). A
break like that is a dislocation, not a signal about the business — which is exactly why it is a buy (MM-014),
not a warning.</p>
""",

    "vol_skew": """
<p><strong>The relief rally has crushed vol into the one event that matters.</strong> VIX closed 17.68 Friday,
down from 19.44 Thursday, and the term structure has re-steepened into contango (est. VIX9D ~16.5 · VIX ~17.7 ·
VIX3M ~19.5 · VIX6M ~20.8) — the classic complacent shape. The problem with that shape is its timing: it is
pricing Kevin Warsh's first dot plot, two days out, as a non-event. A new and more hawkish chair's debut SEP is
a genuine two-sided binary (Dec-26 hike odds are already ~54%), and complacent front-month vol under-prices
<em>both</em> tails. The trade implication: own gamma into Wednesday cheaply. The held 7300/7000 put spread
(MM-008) is the legacy expression; the fresh idea (MM-016) is a Jul-2 6950/6650 put spread at ~1% of notional —
roughly $30 of premium to own a $300 payoff if the dots send the S&amp;P toward 7,000.</p>
""",

    "sector_rv": """
<p><strong>Leading:</strong> European financials (DAX +1.76% Fri; Deutsche Bank +6.6% on delivered ECB NIM
relief), transports/airlines (lower jet fuel = margin tailwind), beaten software (Adobe the dislocation),
North-Asian energy importers (Japan/Korea on cheaper crude).
<strong>Lagging:</strong> energy producers (XLE rolling over as the war premium unwinds; sanctioned Iranian
barrels are the overhang), gold/precious (safe-haven bid deflating on the MoU), defense (de-escalation fades
the war bid).
<strong>This week's watch:</strong> FedEx (~Jun 18) on the freight cycle and the fuel tailwind; the read-through
sizes the transports-vs-energy RV (MM-015).</p>

<p><strong>RV:</strong> The cleanest fresh RV is long transports (IYT) / short energy (XLE) — the oil collapse
is a two-sided input that reprices the two sectors in opposite directions, with low beta to Wednesday's FOMC
(idea MM-015). The standing cross-region RV, long DAX / short Nasdaq (MM-010), is recovering off its 0.949
near-stop as European financials lead and US tech digests the Oracle capex overhang. Hold through FOMC.</p>
""",

    "positioning": """
<p><strong>The energy longs built during the war premium are now the trapped crowd.</strong> Spec net length in
crude was rebuilt through the Kharg escalation; the MoU has left those positions offside into a falling market
with sanctioned barrels coming, so the unwind has fuel and the path of least resistance in oil is still lower —
which is why we surrender our oil longs rather than fight the tape. In rates, the crowd repriced hawkishly on
Thursday's PPI and is now positioned for a hawkish Warsh; the oil-disinflation impulse sets up a squeeze if he
holds data-dependent, which is the upside for the rehabilitated rates longs and the steepener. In FX, EUR longs
that bought the ECB hike are trapped flat (MM-001, MM-012). The pain trade for the broad market is a dovish-hold
FOMC that the complacent VIX 17.7 is not positioned for in either direction.</p>
""",

    "funding": """
<p>SOFR near 3.62% — unchanged through the peace repricing. <strong>The Pozsar mechanic:</strong> with the FOMC
held at 3.50-3.75% and the 2Y eased to 4.09%, secured funding still sits below the 2Y, but the oil-disinflation
impulse narrows the stress for every floating-rate borrower issued in 2023-24 on a cut assumption — a
data-dependent Warsh on Wednesday narrows it further; a hawkish dot plot widens it again. The MOVE index is
easing (est. ~104) as the oil-driven bond rally pulls realised rate vol lower. IG spreads are the tell to watch
into the Fed: they tighten if the market reads the dots as the terminal-rate ceiling, and gap out if Warsh
re-opens the hike door.</p>
""",

    "tape_missing": """
<p><strong>The tape is not pricing the dovish-hold path.</strong> The market has fixed on Warsh's hawkish
reputation and decided the only FOMC risk is a hawkish surprise, so a 98-99% hold sits over a complacent VIX of
17.7. The oil collapse — crude down ~$40 from the war highs — is a forward CPI cut that hands the new chair
cover to stay patient. If Wednesday's dots keep a 2026 cut alive and Warsh leans on the disinflation impulse,
the 2Y falls 15-20bp, the curve steepens hard, and the beaten cohorts (software, rate-sensitives) re-rate. That
path is barely in the price. The rehabilitated rates longs (MM-004, MM-013) and the steepener (MM-009) are the
instruments for it.</p>

<p><strong>Just behind it: the two sides may not be signing the same MoU.</strong> The announcement is real but a
conflicting Iranian-media draft (US withdrawals, reconstruction funding) is circulating, and the signing is not
until Friday. The oil market has front-run a clean peace to $86; if the terms fracture before Jun 19, Brent
snaps back toward $95-100 and the whole disinflation read reverses. We are not chasing crude lower here precisely
because the signature is not in hand. The asymmetry of a deal that slips is large and almost entirely unpriced.</p>

<p><strong>The Burry tell — the structural thing nobody is looking at.</strong> The AI infrastructure trade has
quietly become a capital-markets trade, and Oracle was the first crack: $90-95bn of annual capex funded by a
$40bn raise, the stock punished even as $638bn of RPO confirmed the demand. The question nobody is pricing is
what happens when Microsoft, Google, Amazon and Meta face the same equation and the equity market starts
demanding the same dilution discount from all of them. The free-cash-flow inflection on the hyperscaler build is
three-to-four years out, not twelve-to-eighteen months, and the market is still pricing the backlog without
pricing the capital drag. That resolves badly for the most-owned cohort in the index sometime in the next two to
three quarters — and a hawkish Warsh would be the accelerant.</p>
""",

    "book_outlook": {
        "commentary": (
            "The peace dividend reshapes the book's two-sided exposure. The oil-disinflation impulse is a tailwind "
            "to the book's <b>largest risk — the US AI-semis concentration (Micron ~25.8%, plus NVDA/AVGO/AMD)</b> "
            "— because a possible dovish-hold FOMC eases the real-rate pressure on high-growth multiples, and the "
            "SpaceX-drain fear that hung over semis last week is dead (SPCX debuted +19% with the broad tape up). "
            "It is also a tailwind to the book's <b>duration (US Treasury 1.25% 2031)</b> as the 10Y eased to 4.48%. "
            "The two underwater drags flip the other way: the <b>Xetra-Gold (4GLD)</b> safe-haven bid deflates on "
            "the MoU (gold ~$4,310, softer on the month), and any energy exposure rolls over as the war premium "
            "unwinds. <b>LVMH</b> gets a twin tailwind for once — lower energy costs and a softer euro. The one "
            "risk that dominates everything is Wednesday: a hawkish Warsh dot plot would compress the semis "
            "concentration hardest. Hedge the concentration into the Fed; do not add to it."
        ),
        "outperform": [
            {"name": "US AI-semis (Micron 25.8%, NVDA/AVGO/AMD)", "why": "Risk-on Friday (S&P +0.5%) plus the dead "
             "SpaceX-drain fear plus a possible dovish-hold FOMC easing real-rate pressure on the multiple — the "
             "book's largest position is, for once, leaning the right way today. Do not chase it higher into the Fed."},
            {"name": "US Treasury 1.25% 2031", "why": "The oil-disinflation impulse eased the 10Y to 4.48%; the bond "
             "rallies with the rehabilitated rates book. The winning side of the MoU binary."},
            {"name": "LVMH (MC FP)", "why": "A twin tailwind for the first time in weeks: lower energy costs and a "
             "softer euro post-ECB-pause both flatter the European-luxury consumer."},
        ],
        "underperform": [
            {"name": "Xetra-Gold (4GLD)", "why": "The safe-haven bid deflates on the MoU (gold ~$4,310, -9% on the "
             "month). Held for the FOMC real-rates optionality, but a laggard today as the geopolitical premium drains."},
            {"name": "Any energy / oil-linked exposure", "why": "Energy rolls over as the war premium unwinds (Brent "
             "below $86.5); sanctioned Iranian barrels are the supply overhang into the Jun 19 signing."},
        ],
        "watch": [
            {"label": "Hedge the semis concentration into the Fed", "text": "Micron at 25.8% plus the semis stack is "
             "the book's amplifier in both directions, and a hawkish Warsh dot plot compresses it hardest. Keep the "
             "SPX put structures (MM-008 / MM-016) as the index hedge; do not add semis before Wednesday 2pm."},
            {"label": "Add software, not more semis", "text": "Adobe at a 52-week low on a governance event (idea "
             "MM-014) is the cleaner add than chasing the AI-capex cohort higher — it diversifies the book's tech "
             "risk away from the most-owned, most-crowded semis concentration."},
            {"label": "FX into the FOMC", "text": "The short-EUR (MM-012) is the most contested leg — peace risk-on "
             "is mildly EUR-supportive. Do not add; the rate-path asymmetry still favours USD, and the long-DAX "
             "ratio pairs with it."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> Kevin Warsh is a hawk, so his first FOMC is a hawkish risk — the dots will
shift toward tightening on the still-hot PPI, real yields rise, and the relief rally is the moment to fade
equities and duration. The new chair has every incentive to establish credibility early, and CPI 4.2% plus PPI
6.5% give him the cover.</p>

<p><strong>The strongest argument against — the OFFER:</strong> the oil collapse changed the inflation picture
after the PPI print, not before it. Brent down ~$40 is a disinflation impulse that hands Warsh cover to hold
data-dependent without looking dovish, and a complacent VIX at 17.7 is positioned for neither tail. The
consensus has pre-committed to the hawkish read; the oil price has quietly tilted the odds the other way, and
that is the cheaper side to own going into Wednesday.</p>
""",

    "one_chart": """
<p class="theme">Brent below $86.5 is the chart — because it is a rate cut the Fed has not acknowledged, two days
before the dots.</p>
<p>The single thing the market watches today is crude, but for the wrong reason. The level that changes the
story is not in oil — it is the 2Y at 4.09%. If Brent holds below $87 into Wednesday, the disinflation impulse
is real and a data-dependent Warsh sends the 2Y toward 3.90% and steepens the curve. If the MoU fractures
pre-signing and Brent snaps back above $92, the impulse reverses, the PPI hawkishness reasserts, and the 2Y
runs at the 4.35% stop. Watch the oil price; trade the front end.</p>
""",

    "catalyst_calendar": [
        {"day": "Sat", "date": "Jun 14 ✓",
         "event": "US-Iran MoU announced by mediators — to be SIGNED Jun 19",
         "consensus": "14-point draft: lift oil sanctions, reopen Strait of Hormuz within 30 days, end conflict "
                      "within 60 days. Pakistan PM: final text agreed. Iran FM: 'never been closer.' "
                      "Sources: ABC News, Reuters via Trading Economics, CNN.",
         "view": ("PENDING — written as upcoming. The announcement collapsed Brent below $86.5 and rehabilitated "
                  "the rates longs. But the signing is Friday and a conflicting Iranian-media draft circulates — "
                  "the two sides may not be signing the same document."),
         "asymmetry": "Clean signing Jun 19 = oil toward $80-83, dovish cover for Warsh. Fracture pre-signing = "
                      "Brent back to $95-100, disinflation read reverses. Do not chase crude lower into the signature.",
         "dir": "down"},
        {"day": "Thu", "date": "Jun 11 ✓",
         "event": "Adobe (ADBE) Q2 — PRINTED: beat-and-raise, -6% on CFO exit",
         "consensus": "Record rev $6.62B, adj EPS $5.96, FY26 guide raised to $24.35-24.45 EPS / $26.5-26.6B rev, "
                      "first AI ARR print, $25B buyback. Stock -6.25% to 52-wk low $218.09 on CFO Dan Durn exit to "
                      "Marvell (eff. Jun 15) + CEO search. Sources: TIKR, Seeking Alpha, Yahoo.",
         "view": ("Governance dislocation, not fundamental. The AI-tax-vs-tailwind question resolved tailwind. "
                  "Buy the dislocation (idea MM-014); the $25B buyback is a floor."),
         "asymmetry": "CFO hire / CEO resolution = re-rate toward $258. Governance drag or AI ARR decel = retest of "
                      "lows. The 52-week low on a raised guide is the gap.",
         "dir": "up"},
        {"day": "Fri", "date": "Jun 12 ✓",
         "event": "SpaceX (SPCX) Nasdaq debut — +19% to $160.95",
         "consensus": "Priced $135; debuted +19% to close $160.95 (peaked $176.52, +31% intraday); >$2T cap; ~$75B "
                      "raise — biggest IPO ever. Sources: NPR, CNBC.",
         "view": ("The feared $75B liquidity drain never dragged the tape — risk rallied. A marquee new issue in a "
                  "risk-on tape pulls money in, not only out. The drain thesis is dead; no book action."),
         "asymmetry": "Resolved positive: no tech drain. Watch only for a second-day fade in SPCX as flippers exit.",
         "dir": "up"},
        {"day": "Mon", "date": "Jun 15 ← TODAY",
         "event": "US Empire State Manufacturing + Industrial Production (May)",
         "consensus": "Empire State and IP (May) — second-tier prints, but the first US data into the FOMC blackout.",
         "view": "A soft manufacturing read reinforces the disinflation/data-dependent-hold path and supports the "
                 "rehabilitated rates longs; a hot print is a minor hawkish offset.",
         "asymmetry": "Low individually; matters only as a marginal input to Wednesday's dot-plot framing.",
         "dir": "flat"},
        {"day": "Tue-Wed", "date": "Jun 16-17",
         "event": "FOMC + dot plot — Warsh's FIRST meeting, 98-99% hold priced",
         "consensus": "Hold at 3.50-3.75% (98-99% priced); the dots and any bias shift (easing -> neutral/"
                      "tightening) are the entire event. Dec-26 hike odds ~54%. Decision Wed 2pm ET. "
                      "Sources: Polymarket, TheStreet, CME FedWatch.",
         "view": ("Three paths: (1) data-dependent hold leaning on the oil-disinflation impulse — 2Y -15-20bp, "
                  "steepener accelerates, software/rate-sensitives re-rate; (2) hawkish-neutral — bias to neutral, "
                  "no cut signal, range; (3) hawkish dots (a hike penciled in) — 2Y toward 4.35% stop, AI multiples "
                  "compress, put spreads pay. VIX 17.7 under-prices ALL of these."),
         "asymmetry": "The market is positioned only for the hawkish tail. The oil collapse makes the dovish-hold "
                      "path more likely than priced — own gamma both ways into Wednesday (MM-008, MM-016).",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 17",
         "event": "US May Retail Sales + Lennar earnings",
         "consensus": "Retail Sales (May) lands the same day as the FOMC; Lennar reports on housing demand under "
                      "high rates. (Homebuilder — outside our earnings universe.)",
         "view": "A soft Retail Sales print plus a hawkish dot plot is the bear combination for equities; a firm "
                 "consumer plus a data-dependent hold is the melt-up combination. Reinforces, doesn't lead.",
         "asymmetry": "The consumer is the swing read on whether disinflation is demand-led (bad) or supply-led "
                      "(good). Watch the control group.",
         "dir": "flat"},
        {"day": "Thu", "date": "Jun 18",
         "event": "FedEx (FDX) FY Q4 — after close",
         "consensus": "Consensus EPS $5.80 (-4.5% YoY); beat last 4 quarters. The freight/global-trade bellwether. "
                      "Source: Yahoo Finance / TipRanks.",
         "view": "Two-sided: peace + cheaper fuel is a margin tailwind; tariff-driven volume softness is the "
                 "offset. The guide sizes the transports-vs-energy RV (MM-015). Do not pre-position.",
         "asymmetry": "A volume beat with the fuel tailwind = transports leg of MM-015 confirmed; a tariff-driven "
                      "volume miss = the freight cycle is rolling, fade transports.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660. At ~1.642; stop 1.662. ECB pause behind it, no forward EUR catalyst; peace risk-on a mild AUD positive. Slow grind lower. Hold.</li>
<li><strong>MM-2026-002 · Long Brent:</strong> CLOSED (discretionary). Broke the $87 weekly-close exit near $84 as the MoU (signs Jun 19, Strait reopens 30d) removed the re-escalation premium. The MoU binary paid off on the duration side instead.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.48%, roughly flat to entry. REHABILITATED: the oil collapse is a forward CPI cut that overwhelms Friday's hot PPI. WINNING side of the MoU binary. Data-dependent FOMC = 10Y toward 4.30%. Do NOT add. Hold.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250 (touched, override). At ~$4,310. Two of three engines weakened (geopolitical + inflation) on the MoU/oil crash; held for the real-rates engine (dovish Warsh) + structural EM bid. Hold.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160.2. Differential set to narrow (BoJ Sept hike >50% priced; data-dependent Fed); low-vol risk-on is the near-term headwind. MoF ceiling 163 is the backstop. Hold.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> S&P back above 7,300 → OUT of the money, marked ~$38 (from ~$80). Held only for the FOMC tail inside Jun 27 expiry; VIX 17.7 makes it cheap convexity. Hold through Wed; do not lift.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+39bp; target +60bp. The cleanest duration expression — oil-disinflation drops the front end, fiscal supply anchors the long end. A dovish Warsh is the accelerant. Hold.</li>
<li><strong>MM-2026-010 · Long DAX / short Nasdaq:</strong> stop ratio 0.943. DAX +1.76% Fri vs Nasdaq +0.31% on lower oil + ECB NIM relief — recovering off the near-stop. Structural divergence intact. Hold through FOMC.</li>
<li><strong>MM-2026-011 · Brent 100/115 call spread:</strong> CLOSED (discretionary). Peace deflated the Hormuz tail; with Brent ~$84 the $100 strike is $16 away. Closed near the $1 discipline level to recover residual premium.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. At ~1.157. Sell-the-fact executing; most contested FX leg (peace risk-on mildly EUR-supportive) but rate-path asymmetry still favours USD. Pairs with long DAX. Do not add into FOMC. Hold.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold through Jun 16. At ~4.09%. REHABILITATED: oil collapse fades the Dec-26 hike pricing (~54%). Data-dependent FOMC drops it 15-20bp. Do NOT add. Hold.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The Iran war looks like it's ending — what does that do to our book?",
         "a": ("A US-Iran MoU was announced Saturday and is set to be signed Friday Jun 19 — it lifts oil sanctions "
               "and reopens the Strait of Hormuz within 30 days. Brent collapsed below $86.5 on it. For the book "
               "that's a clean two-sided outcome: we deliberately ran the oil longs AGAINST the long-duration "
               "trades, so one side had to be wrong. The oil longs are closed on their stop; the rates longs and "
               "the curve steepener are the winners, because cheaper oil is a forward inflation cut. One honest "
               "caveat: it's not signed yet, and a conflicting Iranian draft is circulating — so we are not "
               "chasing oil lower here.")},
        {"q": "Why is the oil price suddenly a Fed story?",
         "a": ("Because crude down ~$40 from the war highs is the fastest disinflationary force there is, and it "
               "arrives two days before Kevin Warsh publishes his first dot plot as Fed chair. The market repriced "
               "hawkishly on Thursday's hot PPI and now assumes the only FOMC risk is a hawkish one. The oil "
               "collapse quietly hands Warsh cover to hold data-dependent without looking soft. That dovish-hold "
               "path is barely priced — VIX is at 17.7 — and it's the path our rehabilitated rates positions are "
               "set up for.")},
        {"q": "SpaceX was supposed to drain the market — what happened?",
         "a": ("The opposite. SPCX debuted up 19% to $160.95, a >$2T valuation and the biggest IPO ever, and the "
               "broad market rose with it — the $75B 'liquidity drain' that consensus feared never materialised. "
               "In a risk-on tape a marquee new issue pulls money in, it doesn't only drain it out. We never "
               "traded the drain thesis; it's a consensus fear that resolved.")},
        {"q": "Adobe beat and raised but the stock fell 6% — should we be worried?",
         "a": ("No — we're buyers. Adobe printed record revenue, raised full-year guidance, disclosed its first AI "
               "ARR, and announced a $25B buyback. The stock fell to a 52-week low purely because the CFO is "
               "leaving for Marvell on top of the CEO search — two C-suite exits in three months. That's a "
               "governance dislocation, not a fundamental one. The AI question that hung over the name resolved in "
               "its favour. We're long the dislocation (idea MM-014); the buyback is a floor at $219.")},
        {"q": "Should we take profit on the SPX hedge after that big gain?",
         "a": ("We already gave most of it back — and we hold anyway. The 7300/7000 put spread marked as high as "
               "+129% through CPI and Oracle; Friday's rally took the S&P back above 7,300 so it's out of the "
               "money again at ~$38. The one reason to keep it is Wednesday: Warsh's first dot plot is inside the "
               "expiry, and with VIX crushed to 17.7 the residual downside convexity is cheap to hold into a "
               "binary the market is treating as a non-event. Don't lift it before the Fed.")},
        {"q": "What's the single most important thing this week?",
         "a": ("Wednesday's FOMC — Warsh's first as chair. A hold is 98-99% priced, so the decision isn't the "
               "event; the dot plot is. The market is positioned only for a hawkish surprise, but the oil collapse "
               "has made a dovish-hold more likely than priced, and VIX 17.7 under-prices both tails. We own that "
               "binary cheaply through the put spread and a fresh put structure, and we don't open new directional "
               "macro bets until after 2pm Wednesday.")},
    ],

    "ideas_note": (
        "<p>Disciplined into Warsh's first FOMC (Wed). The book's macro posture is set; the fresh ideas are "
        "deliberately low-correlation to the dot-plot binary. <strong>Long Adobe (MM-014)</strong> — an "
        "idiosyncratic governance dislocation (beat-and-raise at a 52-week low on the CFO exit), uncorrelated to "
        "the Fed. <strong>Long transports / short energy (MM-015)</strong> — a market-neutral-ish peace-dividend "
        "RV off the oil collapse. <strong>SPX put structure (MM-016)</strong> — owns the dot-plot tail that VIX "
        "17.7 is giving away. <strong>No new directional macro bets before Wednesday 2pm.</strong> The "
        "rehabilitated rates longs (MM-004, MM-013) and the steepener (MM-009) are held, not added.</p>"
    ),

    "event_radar_note": (
        "<p>The regime pivoted over the weekend: a US-Iran MoU (announced Jun 14, signs Jun 19) collapsed oil and "
        "rehabilitated the rates book. Confirmed since the last refresh: Adobe beat-and-raised but fell on the CFO "
        "exit (Jun 11 ✓); SpaceX debuted +19% with no liquidity drain (Jun 12 ✓); Brent broke below $86.5 (Jun 12 "
        "✓). Ahead: Empire State + Industrial Production today, the FOMC dot plot Jun 16-17 (Warsh's first — the "
        "event of the week), Retail Sales Jun 17, and FedEx ~Jun 18. The oil longs are closed on their stop; the "
        "rates longs are the winning side of the binary. No new directional macro bets before the Fed.</p>"
    ),

    "burry_tell": (
        "The AI infrastructure trade has quietly become a capital-markets trade, and Oracle was the first crack — "
        "$90-95bn of annual capex funded by a $40bn raise, the stock punished even as a $638bn RPO confirmed the "
        "demand. The structural thing nobody is pricing: what happens when Microsoft, Google, Amazon and Meta all "
        "face the same equation and the equity market starts demanding the same dilution discount from each of "
        "them. The free-cash-flow inflection on the hyperscaler build is three-to-four years out, not "
        "twelve-to-eighteen months, and the market is still pricing the backlog without pricing the capital drag. "
        "That resolves badly for the most-owned cohort in the index over the next two-to-three quarters — and a "
        "hawkish Warsh on Wednesday would be the accelerant. It is not a trade today; it is the thing to be early "
        "on before the next hyperscaler raise forces the comparison."
    ),

    "earnings_summary": (
        "Adobe: POST-PRINT (Jun 11 AMC) — beat-and-raise (record rev $6.62B, adj EPS $5.96, FY26 guide raised to "
        "$24.35-24.45, first AI ARR print, $25B buyback) yet -6.25% to a 52-week low $218.09 on CFO Dan Durn's "
        "exit to Marvell + the CEO search. OVERSOLD on governance, not fundamentals — the basis for long-ADBE "
        "(MM-014). FedEx: PRE-PRINT (~Jun 18 AMC) — consensus EPS $5.80 (-4.5% YoY); the freight/global-trade "
        "bellwether; peace + cheaper fuel tailwind vs tariff volume drag; the guide sizes the transports-vs-energy "
        "RV (MM-015). Do not pre-position."
    ),
    "earnings_why": (
        "Adobe and FedEx are the two prints that bracket the week's themes. Adobe answers whether generative AI is "
        "a software incumbent's tailwind or tax — it answered tailwind, and the equity dislocated on a governance "
        "event, which is the cleanest single-name long in the brief. FedEx is the freight/global-trade bellwether "
        "into the FOMC and the read-through on whether the tariff drag or the cheaper-fuel tailwind dominates. "
        "Both clear the universe filter — $10bn+ cap, US, Tech/Industrials, inside the 5-day-pre / 3-day-post "
        "window. Lennar (Wed) and Kroger are excluded as homebuilder/consumer-staples — outside the "
        "Tech/Financials/Industrials/Utilities universe. Consensus EPS is Finnhub/Yahoo-sourced; implied-move and "
        "positioning fields are supplemented by web search (tagged estimated)."
    ),

    "book_aim": (
        "Two-sided and disciplined into Warsh's first FOMC. The MoU binary resolved: the oil longs (MM-002, "
        "MM-011) are closed on their stop without regret, and the rates longs (MM-004, MM-013) plus the steepener "
        "(MM-009) are rehabilitated by the oil-disinflation impulse — held, not added, ahead of the Fed. The SPX "
        "put spread (MM-008) and a fresh put structure (MM-016) own the dot-plot tail that VIX 17.7 is giving "
        "away. The long-DAX ratio (MM-010) and short-EUR (MM-012) carry the cross-region and FX views. The one new "
        "directional bet — long Adobe (MM-014) — is idiosyncratic enough to be uncorrelated to Wednesday. For the "
        "rest of June: let the steepener and the FX/RV legs carry P&L, execute the fresh ideas on their own "
        "triggers, and open no new directional macro bets before the dot plot lands."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the one option line "
                 "(MM-008) is a model estimate from spot.")
    },
    "idea_selection": [
        {"label": "Long Adobe (MM-014) — entry today", "in": True,
         "text": ("The cleanest single-name long: a beat-and-raise at a 52-week low on a governance event (CFO "
                  "exit), not a fundamental one. Entry ~$219, stop $199, target $258. Idiosyncratic — "
                  "uncorrelated to Wednesday's FOMC. The $25B buyback is the floor. Size up to 3% of book.")},
        {"label": "Long transports / short energy (MM-015) — entry today", "in": True,
         "text": ("A market-neutral-ish peace-dividend RV: the oil collapse is a margin tailwind to transports and "
                  "a top-line hit to energy. Low beta to the FOMC binary — the point two days before the Fed. "
                  "Size on the ratio; stop -3%.")},
        {"label": "SPX put structure (MM-016) — own the dot-plot tail", "in": True,
         "text": ("VIX at 17.7 makes downside convexity cheap right before Warsh's debut dots. A Jul-2 6950/6650 "
                  "put spread at ~1% of notional owns a ~$300 payoff if the dots send the S&P toward 7,000. "
                  "Defined risk; complements the decayed MM-008.")},
        {"label": "Rehabilitated rates longs (MM-004/013/009) — held, not added", "in": False,
         "text": ("The oil-disinflation impulse restored these; they are the winning side of the MoU binary. But "
                  "the FOMC is the gate — do not add size before Wednesday. Respect the stops (4.65% / 4.35% / "
                  "-10bp).")},
        {"label": "No new directional macro before Wednesday 2pm", "in": False,
         "text": ("Warsh's first dot plot is the regime-defining event for the rest of Q2. Forcing a new macro bet "
                  "in front of it is noise, not edge. The three fresh ideas are deliberately low-correlation to "
                  "the binary.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 16.5},
        {"label": "VIX",   "value": 17.7},
        {"label": "VIX3M", "value": 19.5},
        {"label": "VIX6M", "value": 20.8},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.09, 3)},
        {"label": "5Y",  "value": 4.22},
        {"label": "10Y", "value": round(_g("us10y") or 4.48, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 4.95, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-014", "trade": "Long Adobe (ADBE) — governance dislocation",
            "asset_class": "Equity", "structure": "long stock",
            "entry": 219.0, "stop": 199.0, "target": 258.0,
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks-months", "min_hold_days": 0,
            "thesis": ("A beat-and-raise (record rev $6.62B, adj EPS $5.96, FY26 guide raised to $24.35-24.45, first "
                       "AI ARR print, $25B buyback) fell 6.25% to a 52-week low of $218.09 — purely on CFO Dan "
                       "Durn's exit to Marvell atop the CEO search. The market sold the org chart, not the P&L; the "
                       "AI-tax-vs-tailwind question resolved tailwind. Buy the dislocation; the buyback is the floor."),
        },
        {
            "id": "MM-2026-015", "trade": "Long transports (IYT) vs short energy (XLE)",
            "asset_class": "Equity RV", "structure": "cross-sector ratio",
            "entry": "spot ratio", "stop": "ratio -3%", "target": "ratio +5%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 1, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("The peace dividend reprices two sectors in opposite directions off one input: Brent down "
                       "~$8 to ~$84 (lower still on the MoU) is a fuel-cost tailwind to airlines/freight and a "
                       "top-line hit to E&P. Market-neutral-ish, low beta to Wednesday's FOMC — own the "
                       "de-escalation theme without a directional macro bet."),
        },
        {
            "id": "MM-2026-016", "trade": "Buy SPX Jul-2 6950/6650 put spread (own the dot-plot)",
            "asset_class": "Derivatives (options)", "structure": "put spread",
            "entry": "~$30 premium (~1% notional)", "stop": "—", "target": "~$300",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "to Jul 2", "min_hold_days": 0,
            "thesis": ("The relief rally crushed VIX to 17.7 and priced Warsh's first FOMC at 98-99% hold as a "
                       "non-event — exactly when a new, more hawkish chair's debut dot plot is the least-priced "
                       "binary on the board (Dec-26 hike odds ~54%). Cheap downside convexity expiring just after "
                       "the meeting; the fresh expression of the FOMC tail now MM-008 has decayed OTM."),
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
