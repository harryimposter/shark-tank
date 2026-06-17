#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Market Map / Shark Tank brief generator — 2026-06-17 (Wednesday). FOMC DECISION DAY.

THE NEXT CHAPTER vs the Jun 16 run: the melt-up DIGESTED — by rotation, not retreat —
and the decision the whole tape is waiting for may not arrive in the form it expects.
- Tuesday Jun 16 was a ROTATION, not a sell-off. The Dow rose 0.64% to 51,999.67 — a
  SECOND straight record close — while the S&P slipped 0.57% to 7,511.35 and the Nasdaq
  Composite FELL 1.15% to 26,376.34. The Philadelphia Semiconductor Index dropped ~5.7%;
  NVDA -2.37% to 207.41. Monday's worst-to-first reversed to first-to-worst as money
  rotated out of semis/tech into financials (+1.5%) and industrials ahead of the Fed.
  (Yahoo Finance, TheStreet.)
- OIL fell FURTHER and broke a line: Brent dropped ~5% to ~$79 — its first sub-$80 print
  since March — and WTI ~$77 (4th down session). The disinflation impulse deepened again
  as the US-Iran MoU moved to a confirmed Fri Jun 19 signing. (CNBC, Fortune, Trading Eco.)
- BoJ HIKED to 1.00% (from 0.75%) — the highest policy rate since 1995 — on a 7-1 vote,
  with Governor Ueda HOSPITALIZED and ABSENT (first BoJ meeting ever without the governor;
  Deputy Himino chaired). Yet the yen WEAKENED: the hike was priced, USDJPY sits pinned
  near 160 at the MoF intervention line. The short-USDJPY book (MM-007) is frustrated, not
  vindicated — historic hike, no yen rally. (Bloomberg, forex.com, FXStreet.)
- GOLD extended to ~$4,331 (Jun 16 close) then went flat ~$4,326 ahead of the Fed — the
  real-rates engine intact. (Trading Economics, GoldSilver.)
- EMPIRE STATE manufacturing COLLAPSED to 5.7 (from 19.6; consensus ~13) — a soft data
  point that reinforces the disinflation/dovish read into the dots. (NY Fed.)
- FOMC TODAY, Wed Jun 17, decision 2pm ET — Kevin Warsh's FIRST meeting as chair. A hold
  at 3.50-3.75% is ~98% priced. The market is positioned entirely around the dot plot. THE
  TELL: Warsh is a longtime forward-guidance critic, and FT-sourced reporting says he may
  begin DISMANTLING the dots / stripping bias language as soon as this meeting. The event
  the tape is waiting for may dissolve. 2026 cuts have faded to ~zero; ~47% price a 2026
  HIKE. Trump (Jun 16): a hike "would be wrong"; separately, the chair should "do whatever
  he wants." PENDING — written as upcoming. (Conference Board, REX Shares, FXStreet, WaPo.)
- US-Iran MoU: Switzerland (FDFA) confirmed a Fri Jun 19 signing at Bürgenstock (Pakistan +
  Qatar mediating). A digital framework was reportedly signed Jun 15-16; Bloomberg published
  a 14-point draft (end war all fronts incl. Lebanon; lift blockade in 30 days; 60-day
  nuclear window). Open disputes remain: Hormuz toll-free only 60 days, Iran's ~440kg HEU,
  ~$12B frozen assets, the Lebanon clause. THE LIVE CAVEAT hardened: Iran's joint military
  command warned Israel to "expect a hard response"; Netanyahu refused VP Vance's ask to
  scale back in south Lebanon; Katz says Israel won't withdraw. PENDING. (Bloomberg, Times
  of Israel, NBC, PBS, People's Daily.)
- Note: Fri Jun 19 is JUNETEENTH — US equity/bond markets CLOSED — the same day as the MoU
  signing, so the tape reacts Monday Jun 22.

Run:  python gen_2026_06_17.py
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
# SPX 7300/7000 put spread (MM-008): Tuesday's rotation pulled the S&P back to ~7,511 from
# 7,554 — ~211pts above the 7,300 strike, still deep OUT of the money. But today IS the FOMC
# and VIX ticked back up (~16.4), so the residual is pure event premium. Mark ~$34 (up from
# ~$30 Jun 16 as spot fell toward the strike and the catalyst is now hours, not days, away).
levels["MM-2026-008"] = 34.0

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
    "NVDA": "Constructive but disciplined, and Tuesday is why. The +3% Monday rip on the $25B bond gave way to a "
            "-2.4% Tuesday (NVDA $207.41) as the SOX fell ~5.7% and money rotated out of semis into the Dow ahead "
            "of the Fed. The book owns NVDA (-10.5%) via the bullish range note (idea 101); an OVERBOUGHT print here "
            "is where we hedge the concentration into the 2pm dots, not where we add.",
    "MU":   "Still our highest-conviction add-on-weakness, but the clock is the story now. HBM is sold out into the "
            "AI-memory supercycle, yet MU is the Fable book's LARGEST position (~25.8%) into TWO catalysts in seven "
            "sessions: the Fed today and MU earnings Jun 24. Tuesday's semis rotation (SOX -5.7%) is the warning — "
            "collar the 25.8% concentration before 2pm and before the print; do not chase.",
    "ADBE": "We remain BUYERS of the dislocation, and Tuesday's rotation OUT of high-beta semis INTO quality "
            "software is the tell. The Jun 11 -6% to a 52-week low ($218) was a beat-and-raise sold purely on the "
            "CFO's exit to Marvell — governance, not fundamentals. A guidance-light, oil-disinflation Fed re-rates "
            "software over semis. This is the carried single-name long (idea MM-014).",
    "XLE":  "Energy keeps rolling over as the war premium bleeds out — Brent broke $80 (first time since March) with "
            "the MoU signing Fri Jun 19 and the Strait reopening toll-free for 60 days. Oversold is NOT a buy: we are "
            "SHORT energy as the transports-vs-energy RV (idea MM-019). Sell income against any energy length.",
    "GLD":  "Gold's real-rates engine is intact: it extended to ~$4,331 then went flat ~$4,326 ahead of the dots. We "
            "OWN it (MM-005 / the book's 4GLD). A dovish-or-guidance-light Warsh extends it; an explicitly hawkish "
            "dot plot (if he still gives one) is the one thing that reverses it first — the first hedge to give back.",
    "TLT":  "Duration is the winning side of the disinflation impulse: the 2Y eased to ~4.06% and the curve held its "
            "steepening as oil broke $80 and Empire State collapsed to 5.7. We are long via the short-2Y book "
            "(MM-013) and the steepener (MM-009). An oversold long-bond proxy into a possible dovish hold is the "
            "add — but not before 2pm Wednesday.",
}

# ── Regime ─────────────────────────────────────────────────────────────────────
regime = ("Tech De-Risks Into Warsh's First Decision: Oil Sub-$80, a Record Dow, "
          "and the Dot Plot Itself in Doubt — 2pm ET")
regime_note = (
    "The melt-up did not retreat; it rotated — and the one event the whole tape is built around may not arrive in "
    "the form it expects. Tuesday Jun 16 was a de-risking ROTATION, not a sell-off: the Dow rose 0.64% to a SECOND "
    "straight record close at 51,999.67 while the S&P slipped 0.57% to 7,511.35 and the Nasdaq Composite fell 1.15% "
    "to 26,376.34. The Philadelphia Semiconductor Index dropped ~5.7% and NVIDIA fell 2.37% to $207.41 — Monday's "
    "worst-to-first inverted to first-to-worst as money left semis for financials (+1.5%) and industrials the day "
    "before Kevin Warsh's first FOMC. (Yahoo Finance, TheStreet.) "
    "Oil broke a line. Brent fell ~5% to ~$79 — its first sub-$80 print since March — and WTI to ~$77, a fourth down "
    "session, as the US-Iran MoU moved to a confirmed Friday Jun 19 signing at Bürgenstock in Switzerland. The "
    "disinflation impulse the book's duration trades are built on deepened again, and a soft Empire State (5.7, from "
    "19.6) added to it. (CNBC, Fortune, NY Fed.) "
    "Overnight, the Bank of Japan HIKED to 1.00% — the highest since 1995 — on a 7-1 vote, with Governor Ueda "
    "hospitalised and absent (the first BoJ meeting ever held without its governor; Deputy Himino chaired). And yet "
    "the yen WEAKENED: the hike was fully priced, and USD/JPY sits pinned near 160 at the MoF's intervention line. "
    "The book's short-USD/JPY (MM-007) is frustrated, not vindicated — a historic tightening with no yen rally is "
    "the cleanest evidence that a VIX-16 carry tape ignores fundamentals until vol returns. (Bloomberg, forex.com.) "
    "Now the decision. A hold at 3.50-3.75% is ~98% priced; the market is positioned entirely around the dot plot "
    "and the bias shift. The non-consensus tell: Warsh has criticised forward guidance for a decade, and "
    "FT-sourced reporting says he may begin DISMANTLING the dots and stripping bias language as soon as today. The "
    "event the tape is waiting for may dissolve — and a guidance-light Fed is not a dovish or hawkish outcome, it is "
    "a structurally higher-vol one that a VIX crushed near 16 prices in no direction at all. 2026 cuts have faded to "
    "roughly zero, ~47% now price a 2026 hike, and Trump said Tuesday a hike 'would be wrong' even as he allowed the "
    "chair should 'do whatever he wants.' (Conference Board, REX Shares, WaPo.) "
    "The honest caveats hardened. Switzerland confirmed the Friday signing, Bloomberg published a 14-point draft, "
    "and a digital framework was reportedly signed Monday — but Hormuz is toll-free for only 60 days, the enriched "
    "uranium and the frozen assets are unresolved, and Iran's joint military command warned Israel to 'expect a "
    "hard response' while Netanyahu refused to pull back from south Lebanon. The tape has priced a clean peace, a "
    "non-event Fed and a vol that never returns. The brief has priced none of the three. And Friday is Juneteenth — "
    "US markets are closed — so the signing trades Monday."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Mark to market ─────────────────────────────────────────────────────────────
book.step("Marking open trades to live levels")
book.mark_to_market(trades, levels)

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
            "The ECB delivered its +25bp hike to 2.25% on Jun 11 and Lagarde signalled a pause — the move that "
            "removes the marginal EUR buyer. The risk-on tape keeps a bid under the AUD (commodity-currency beta), "
            "which presses the short cross lower; with no forward EUR catalyst the cross grinds toward target. "
            "Patience over pressing — there is no dated event to force it, so let carry and the spread do the work."
        ),
        "catalysts": [
            "ECB pause signal (Jun 11) now in the price — no forward EUR catalyst",
            "Risk-on tape / firm iron ore = AUD commodity-currency tailwind",
            "RBA path — a hawkish hold supports AUD vs a paused ECB",
            "FOMC Jun 17 — a USD move spills into both legs; watch the cross-rate, not just EUR/USD",
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
            "confirmation": "1/2 — the risk-on AUD beta helps but the cross has not broken cleanly lower.",
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
            "The slower-burn duration leg, and the configuration is intact even as the long end lags the front. "
            "Brent breaking $80 is a forward CPI cut, and a soft Empire State (5.7) reinforces it, but the 10Y "
            "backed up to ~4.47% Tuesday on the equity rotation and supply concerns — so the trade sits modestly "
            "offside from entry (4.44%). The catalyst is today: a data-dependent or guidance-light Warsh extends the "
            "10Y toward 4.30%; an explicitly hawkish dot plot on the still-firm CPI is the risk. Do not add into the "
            "print — the front end (MM-013) is the cleaner expression of the same disinflation view."
        ),
        "catalysts": [
            "Oil sub-$80 (first since March) + soft Empire State = forward CPI cut not fully in the long end",
            "FOMC Jun 17 2pm — data-dependent/guidance-light = 10Y toward 4.30%; hawkish dots = stop tested",
            "May Retail Sales Jun 17 8:30am — a soft print reinforces the disinflation read",
            "Treasury supply at the long end — the offsetting fiscal risk to the duration rally",
        ],
        "risks": (
            "Warsh delivers an explicitly hawkish dot plot despite the oil relief; the long end sells on fiscal "
            "supply rather than rallying on disinflation; the MoU collapses pre-signing and oil/inflation snap back. "
            "Stop 4.65% (now ~4.47%, ~18bp away)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the sub-$80 oil move widens the disinflation gap; the net inflation signal is "
                            "lower, but the long end carries fiscal-supply risk that capped Tuesday's rally.",
            "catalyst":     "2/2 — FOMC Jun 17 and Retail Sales Jun 17 are dated, direct, 10Y-relevant events.",
            "positioning":  "1/2 — consensus is still cautiously short duration; squeeze fuel on a dovish hold.",
            "confirmation": "0/2 — the 10Y backed up Tuesday on the rotation; no confirmation this session.",
            "stop_quality": "1/1 — 4.65% is a clear technical level; ~18bp of risk.",
        },
    },
    "MM-2026-005": {
        "instrument": (
            "Gold (XAU/USD) — spot gold in USD. The inverse of real rates, driven by the Fed path "
            "and real yields, USD strength, EM central-bank buying, geopolitical premia, and "
            "inflation/stagflation fears."
        ),
        "fundamental_thesis": (
            "Working on the real-rates engine, not the safe-haven one. The peace did not deflate gold — it extended "
            "to ~$4,331 (Jun 16) as the oil collapse cut hike odds and pulled real yields down, then went flat "
            "~$4,326 ahead of the dots. The position is comfortably back above its $4,250 stop (touched Jun 10; the "
            "45-day min-hold to ~Jul 15 keeps it structural). A dovish or guidance-light Warsh extends it; an "
            "explicitly hawkish dot plot is the one catalyst that reverses it first — so it is the book's first "
            "hedge to give back on hawkish dots."
        ),
        "catalysts": [
            "FOMC dot plot Jun 17 — dovish/guidance-light = real yields down, gold up; hawkish = capped",
            "Oil sub-$80 — sustained crude weakness keeps hike odds (and real yields) low = gold supported",
            "US-Iran MoU signing Jun 19 — residual safe-haven premium drains, but the real-rates engine dominates",
            "EM central-bank Q2 gold purchases (China, India, Turkey — structural buyers)",
        ],
        "risks": (
            "Warsh delivers hawkish dots and real yields surge; the MoU signs cleanly and the last safe-haven "
            "premium drains faster than the real-rate tailwind builds; a gold-specific spec flush. Stop $4,250 "
            "(45-day min-hold override keeps it open to ~Jul 15)."
        ),
        "breakdown_why": {
            "gap":          "2/3 — gold's decoupling from the safe-haven driver has resolved into a real-rates "
                            "trade; the mispricing is now the dovish/guidance-light path the market under-weights.",
            "catalyst":     "2/2 — FOMC dots are a dated, direct real-rate catalyst with clean gold transmission.",
            "positioning":  "1/2 — positioning is not extreme; not a cleanly crowded long.",
            "confirmation": "2/2 — three up sessions to ~$4,331 confirm the real-rates engine; held flat into the Fed.",
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
            "Frustrated by the very event that should have helped it. The BoJ HIKED to 1.00% overnight — the highest "
            "since 1995, with Ueda hospitalised and absent — and the yen WEAKENED, because the hike was fully priced "
            "and a crushed-vol carry tape ignores a known differential. USD/JPY is pinned near 160 at the MoF line. "
            "The structural case (a normalising BoJ, a Fed whose oil-disinflation argues against tightening) is "
            "intact and arguably stronger after the hike, but the trade needs vol to return — which is precisely "
            "what a guidance-light Warsh could deliver. Patient short with the 163 ceiling as the backstop; the "
            "fresh, defined-risk way to own the intervention tail is MM-021."
        ),
        "catalysts": [
            "BoJ hiked to 1.00% (Jun 16) — done, priced; the next leg is forward guidance / Ueda's return",
            "MoF intervention — explicit warnings at the 160 line; physical action forces stop-hunting",
            "FOMC Jun 17 — a guidance-light Fed that re-rates vol is what reactivates the carry unwind",
            "Japan CPI — any upside surprise supports further BoJ normalisation",
        ],
        "risks": (
            "A hawkish Warsh widens the differential again and carry stays on; the BoJ's next guidance sounds dovish "
            "despite the hike; vol stays crushed and the carry trade persists. Stop 163.00."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is ~1500 pips above where the 2yr differential has historically implied, "
                            "and the BoJ hike widens that gap further.",
            "catalyst":     "2/2 — the MoF intervention threat at 160 and a guidance-light Fed are both live, dated.",
            "positioning":  "1/2 — the yen carry trade is crowded long-USD; the crushed-vol tape delays the unwind.",
            "confirmation": "0/2 — the yen weakened on a historic hike; no confirmation of the turn this session.",
            "stop_quality": "1/1 — 163.00 is a clean MoF-intervention ceiling; ~3 pts risk vs ~10 to target.",
        },
    },
    "MM-2026-008": {
        "instrument": (
            "SPX Jun-27 7300/7000 put spread — defined-risk. Buy the 7300 put, sell the 7000 put. "
            "Max profit $300/unit if SPX <=7000 at expiry; max loss = the $35 premium; break-even "
            "~7265. Driven by the SPX level (~7,511), implied vol (VIX ~16.4), and time to expiry."
        ),
        "fundamental_thesis": (
            "The hedge that paid +129% through CPI and Oracle, gave it back into the melt-up, and earns its keep for "
            "exactly one reason today: the FOMC sits inside the Jun 27 expiry. Tuesday's rotation pulled the S&P "
            "back to ~7,511 from 7,554, so the spread is ~211pts out of the money, marked ~$34 — pure event premium. "
            "With VIX near 16.4 this residual downside convexity is the cheapest insurance on the board into a "
            "decision the market treats as a non-event and a chair who may re-write the vol regime. Hold through the "
            "2pm dots; the residual value IS the tail. The fresh, nearer-dated complement is MM-008's successor "
            "MM-017 (carried) plus today's vol idea MM-020."
        ),
        "catalysts": [
            "FOMC dot plot Jun 17 2pm — hawkish dots or a guidance shock push SPX toward 7,000 and the spread to intrinsic",
            "May Retail Sales Jun 17 8:30am — a soft print plus a hawkish surprise is the bear combination",
            "MoU signing risk Jun 19 (Juneteenth, US closed; trades Mon 22) — a collapse pre-signing reopens downside",
        ],
        "risks": (
            "SPX grinds higher on a clean dovish hold and the spread expires near zero; time decay into Jun 27; a "
            "post-event VIX crush. Max loss remains the $35 premium — defined risk."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the gap is the under-priced FOMC/guidance tail (VIX 16.4), not realised intrinsic "
                            "value; the index is well above the strike.",
            "catalyst":     "2/2 — FOMC and Retail Sales both land inside expiry, today.",
            "positioning":  "2/2 — the market is maximally complacent (VIX ~16); maximum room for a re-pricing.",
            "confirmation": "0/2 — the SPX is far above the strike; no technical confirmation right now.",
            "stop_quality": "1/1 — defined-risk; max loss is the $35 premium. The stop is conceptual.",
        },
    },
    "MM-2026-009": {
        "instrument": (
            "2s10s US Treasury curve steepener — long the 2Y (receive/own cut optionality), short "
            "the 10Y (short fiscal-supply risk). Pays when 10Y-minus-2Y widens. Currently ~2Y 4.06% "
            "/ 10Y 4.47%, spread ~+41bp. The 2Y is Fed-driven; the 10Y is supply/term-premium-driven."
        ),
        "fundamental_thesis": (
            "The best position in the book and the cleanest duration expression, and Tuesday's tape helped it: the "
            "2Y eased to ~4.06% on the oil/data softness while the 10Y held up on the rotation and supply, widening "
            "the spread to ~+41bp — ~+175% on the position from the +15bp entry off an 18-month inversion. A "
            "dovish-leaning or guidance-light Warsh is the accelerant (the front end falls faster than the back); an "
            "explicitly hawkish dot plot that flattens the front is the risk. Min-hold to ~Jul 16 keeps it "
            "structural through the meeting. Target +60bp; held, not added, into 2pm."
        ),
        "catalysts": [
            "FOMC dot plot Jun 17 — a pause/guidance-light signal drops the 2Y faster than the 10Y = steepens",
            "Oil sub-$80 + soft Empire State — pulls front-end cut pricing without compressing the long end",
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
            "catalyst":     "2/2 — FOMC dots and Retail Sales are direct, dated front-end catalysts, today.",
            "positioning":  "1/2 — front-end positioning offers some squeeze fuel on a dovish hold.",
            "confirmation": "2/2 — the spread widened to ~+41bp through the oil/data softness; confirmed.",
            "stop_quality": "1/1 — a negative spread is a clean, well-defined failure threshold.",
        },
    },
    "MM-2026-012": {
        "instrument": (
            "EUR/USD spot — short euro, long dollar. Driven by ECB-vs-Fed policy, eurozone-vs-US "
            "growth, risk sentiment (USD safe-haven), the oil price, and speculative positioning."
        ),
        "fundamental_thesis": (
            "The most contested leg, and back to roughly flat. The ECB delivered +25bp Jun 11 and Lagarde's pause "
            "removed the forward EUR catalyst — but the risk-on tape and a DXY pinned below 100 (~99.5) keep EUR/USD "
            "firm near 1.158 rather than fading. It is held because the rate-path asymmetry still favours the dollar "
            "(a paused ECB vs a Fed holding with at least a hawkish-bias tail) and it pairs cleanly with the book's "
            "European-equity tilt. Today is the resolving event: a hawkish Warsh is the catalyst that finally "
            "separates the legs. Respect the 1.182 stop; do not add into the FOMC."
        ),
        "catalysts": [
            "ECB pause (Jun 11) — sell-the-fact catalyst, in train",
            "FOMC Jun 17 — a hawkish-bias hold supports the dollar vs a paused ECB",
            "Risk-on flows + sub-100 DXY — the offsetting EUR-supportive force to watch",
            "Spec positioning unwind — EUR longs near multi-year highs",
        ],
        "risks": (
            "Peace risk-on and a sub-100 DXY lift EUR broadly; US data disappoints and EUR/USD re-rates higher; a "
            "dovish or guidance-light Warsh sinks the dollar. Stop 1.182."
        ),
        "breakdown_why": {
            "gap":          "1/3 — the mispricing is contained: the ECB hike is priced and the sub-100 dollar leans "
                            "against the position right now.",
            "catalyst":     "2/2 — FOMC Jun 17 is a precise, dated catalyst with a clear payoff trigger.",
            "positioning":  "1/2 — EUR spec longs near multi-year highs provide unwind fuel.",
            "confirmation": "0/2 — EUR held firm on the sub-100 DXY; no confirmation this session.",
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
            "Working, and the cleanest expression of the whole disinflation view. Brent sub-$80 and a soft Empire "
            "State argue against the 2026 hike the curve still partly prices (~47%), and the 2Y eased to ~4.06% "
            "(+2.45% on the position from the 4.162% entry). The structural thesis — that the front end "
            "over-extrapolated a single payroll into a hiking cycle — is in force with the oil tailwind behind it. "
            "Today is the gate: a data-dependent or guidance-light Warsh drops the 2Y 15-20bp; an explicitly hawkish "
            "debut dot plot sends it toward the 4.35% stop. Min-hold to ~Jul 8; do not add ahead of the dots."
        ),
        "catalysts": [
            "Oil sub-$80 + soft Empire State = forward disinflation fading the 2026-hike pricing (~47%)",
            "FOMC dot plot Jun 17 — data-dependent/guidance-light hold drops the 2Y; hawkish dots test the stop",
            "May Retail Sales Jun 17 — a soft print reinforces the no-further-hike read",
            "Jobless claims Jun 18 — any spike weakens the hiking case",
        ],
        "risks": (
            "Warsh delivers a hawkish debut dot plot regardless of oil; the MoU collapses pre-signing and "
            "inflation expectations snap back; a re-acceleration in the labour data. Stop 4.35%; min-hold to ~Jul 8."
        ),
        "breakdown_why": {
            "gap":          "2/3 — the oil-disinflation impulse re-widens the gap between the 2Y and the justified "
                            "hiking probability, which has eased toward ~47%.",
            "catalyst":     "2/2 — the FOMC dot plot is a precise, dated catalyst with direct 2Y transmission, today.",
            "positioning":  "2/2 — the market is still positioned for a hawkish Warsh; squeeze fuel on a dovish hold.",
            "confirmation": "2/2 — the 2Y eased to ~4.06% across the oil/data softness; confirmed.",
            "stop_quality": "1/1 — 4.35% is a clear technical level; ~29bp of risk.",
        },
    },
    # ── New ideas generated today (cards only; book entry per idea_selection) ────
    "MM-2026-020": {
        "instrument": (
            "Long VIX Jul 18/24 call spread (or a 1-month SPX 25-delta strangle) — defined-risk long "
            "volatility into and through the FOMC. Pays if realised/implied vol re-rates higher; max "
            "loss is the premium. The expression of a guidance-regime change, not a directional bet."
        ),
        "fundamental_thesis": (
            "VIX near 16.4 prices Warsh's first decision as a non-event, but the real risk is not hawkish or dovish "
            "— it is structural. Warsh has criticised forward guidance for a decade, and the reporting is that he "
            "may begin dismantling the dot plot and stripping bias language today. A guidance-light Fed removes the "
            "calendar Fed-put and turns every CPI, payroll and auction into its own catalyst — which permanently "
            "lifts the vol floor. At the most complacent vol into a Fed meeting this cycle, owning convexity on that "
            "re-rating is cheap and one-directional in its risk. Defined premium; the cleanest way to be long the "
            "regime change the tape is not hedging."
        ),
        "catalysts": [
            "FOMC + SEP Jun 17 2pm — the guidance/dot-plot structure itself is the trigger, not just the level",
            "Warsh press conference 2:30pm — first articulation of his reaction-function and guidance philosophy",
            "Post-melt-up complacency (VIX ~16) — maximum room for a vol re-rating",
            "A data-dependent regime turns Retail Sales, CPI, payrolls each into a discrete vol event",
        ],
        "risks": (
            "Warsh keeps the dots intact, delivers a clean status-quo hold, and VIX bleeds lower post-event; the "
            "premium decays with no vol re-rating; the carry tape simply resumes. Max loss is the defined premium."
        ),
        "breakdown_why": {
            "gap":          "2/3 — implied vol (16.4) prices a status-quo Fed; it does not price a guidance-regime change.",
            "catalyst":     "2/2 — the FOMC/SEP and the press conference are precise, dated, high-variance events.",
            "positioning":  "2/2 — maximum complacency right before a new chair who may re-write the framework.",
            "confirmation": "0/2 — no technical confirmation; this is a pre-event convexity buy.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-021": {
        "instrument": (
            "Buy a 3-month USD/JPY 158/153 put spread — defined-risk long yen / short USD-JPY downside. "
            "Buy the 158 put, sell the 153 put. Owns the MoF-intervention / vol-return tail at a fraction "
            "of the spot risk; max loss is the premium. Complements the spot short MM-007."
        ),
        "fundamental_thesis": (
            "The BoJ hiked to 1.00% — the highest since 1995 — and the yen still weakened, pinning USD/JPY near 160 "
            "at the exact level the MoF defends. That is the setup, not the disappointment: the carry trade is "
            "maximally stretched against a now-tightening BoJ, and the only thing keeping it alive is crushed vol. A "
            "guidance-light Warsh that re-rates vol, or a single MoF intervention, snaps USD/JPY several figures "
            "lower in days. A spot short bleeds carry; a put spread owns the same downside with defined premium and "
            "positive convexity into exactly the catalyst (vol returning) that the spot trade is waiting for."
        ),
        "catalysts": [
            "MoF intervention at the 160 line — the most-telegraphed FX backstop on the board",
            "FOMC Jun 17 — a guidance-light, vol-re-rating Fed is what reactivates the carry unwind",
            "BoJ post-hike guidance / Ueda's return from hospital — the normalisation path",
            "Any global risk-off — JPY is the funding currency that snaps back hardest when vol returns",
        ],
        "risks": (
            "Vol stays crushed, the MoF stays silent, and the carry trade persists with USD/JPY grinding higher; the "
            "put spread decays. A hawkish Warsh widens the differential and delays the turn. Max loss is the premium."
        ),
        "breakdown_why": {
            "gap":          "2/3 — USD/JPY is far above 2yr-differential fair value and the BoJ just widened the gap.",
            "catalyst":     "2/2 — the MoF line and a vol-re-rating Fed are both live, dated, near-term.",
            "positioning":  "2/2 — the carry trade is maximally crowded long-USD at the intervention line.",
            "confirmation": "0/2 — the yen weakened on the hike; no confirmation of the turn yet — a convexity buy.",
            "stop_quality": "1/1 — defined-risk; the premium is the max loss.",
        },
    },
    "MM-2026-022": {
        "instrument": (
            "Long RSP (S&P 500 equal-weight) / short QQQ (Nasdaq-100) — a market-neutral-ish ratio "
            "expressing the rotation OUT of mega-cap semis/tech INTO the broad market. Rises when "
            "the equal-weight index outperforms the cap-weighted tech complex."
        ),
        "fundamental_thesis": (
            "Tuesday wrote the thesis in one session: the Dow printed a second record while the Nasdaq fell 1.15% "
            "and the SOX dropped ~5.7% — money rotated out of the most-crowded, now AI-debt-levered semis into "
            "financials and industrials ahead of the Fed. Two forces extend it. A guidance-light, oil-disinflation "
            "Fed broadens leadership beyond the seven names that carried the index. And the AI complex is funding "
            "its capex with debt (NVDA's $25B bond), which the equity has not yet discounted. Long the breadth, "
            "short the concentration — low beta to the FOMC level, high beta to the rotation it accelerates."
        ),
        "catalysts": [
            "FOMC Jun 17 — a guidance-light/dovish hold broadens leadership beyond mega-cap tech",
            "Semis de-risking (SOX -5.7% Tue) — the rotation already in motion",
            "AI-debt supply (NVDA $25B, Oracle) — the leverage overhang the cap-weighted index carries",
            "Q2 breadth / earnings season — confirmation the median stock is participating",
        ],
        "risks": (
            "A clean dovish hold re-rates mega-cap tech and the cap-weighted index leads again (Monday's tape); a "
            "growth scare hits cyclical equal-weight harder than defensive mega-cap; the AI melt-up resumes. "
            "Stop: ratio -3% from entry."
        ),
        "breakdown_why": {
            "gap":          "2/3 — extreme index concentration vs the median stock is a real, wide structural gap.",
            "catalyst":     "1/2 — the rotation is in motion but the broadening is a gradual, multi-session move.",
            "positioning":  "2/2 — the mega-cap-tech long is the most crowded, now most-levered, theme in the index.",
            "confirmation": "1/2 — Tuesday's Dow-record/Nasdaq-down split started the rotation; one confirming leg.",
            "stop_quality": "1/1 — a fixed ratio stop (-3%) is a clean, defined failure threshold.",
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
    {"name": "SOFR", "level": "~3.62%", "chg": "", "dir": "flat"},   # FOMC decision today (held expected); funding unmoved
    {"name": "MOVE", "level": "~104 (est)", "chg": "firmer", "dir": "up"},
]

rates_levels = [
    {"name": "SOFR (o/n)", "level": "3.62%", "chg": "funding", "dir": "flat",
     "vid": "sofr-v", "cid": "sofr-c", "asof": "Tue 16 Jun · TradingView"},
    _row("US 2Y",   "us02y", _yld, bp=True),
    _row("US 10Y",  "us10y", _yld, bp=True),
    _row("US 30Y",  "us30y", _yld, bp=True),
    {"name": "2s10s", "level": f'{(_g("us10y")-_g("us02y"))*100:+.0f}bp' if _g("us10y") and _g("us02y") else "—",
     "chg": "steeper", "dir": "up"},
    _row("Bund 10Y", "de10y", _yld, bp=True),
    _row("Gilt 10Y", "gb10y", _yld, bp=True),
    {"name": "MOVE", "level": "~104", "chg": "firmer (est)", "dir": "up"},
]

# Per-trade open-book notes (shown in the "yesterday, graded" table).
NOTES = {
    "MM-2026-001": "ECB pause behind it; no forward EUR catalyst. Risk-on keeps an AUD bid (commodity beta) that presses the short. Slow grind lower from ~1.643. Stop 1.662. Hold.",
    "MM-2026-004": "Slower-burn duration leg. Brent sub-$80 + soft Empire State are a forward CPI cut, but the 10Y backed up to ~4.47% on Tuesday's rotation/supply — modestly offside. FOMC today is the gate; guidance-light = 10Y toward 4.30%. Do not add. Stop 4.65%.",
    "MM-2026-005": "WORKING on the real-rates engine. Extended to ~$4,331 then flat ~$4,326 into the dots; comfortably above the $4,250 stop. A dovish/guidance-light Warsh extends it; hawkish dots reverse it first. Min-hold to ~Jul 15.",
    "MM-2026-007": "FRUSTRATED BY THE HIKE. BoJ went to 1.00% (highest since 1995, Ueda absent) and the yen WEAKENED — priced, and crushed vol keeps carry on. Pinned ~160 at the MoF line. Needs vol to return (a guidance-light Fed). Stop 163.00; fresh defined-risk expression MM-021.",
    "MM-2026-008": "Deep OTM after the melt-up — S&P ~7,511, ~211pts above the 7,300 strike, marked ~$34. Held ONLY for the FOMC tail inside Jun 27 expiry; VIX ~16.4 makes it the cheapest insurance on the board into a chair who may re-write the vol regime. Hold through 2pm; do not lift.",
    "MM-2026-009": "BEST OPEN POSITION (~+175%). The cleanest duration expression: the 2Y eased to ~4.06% while the 10Y held on the rotation — spread widened to ~+41bp. Target +60bp. A guidance-light Warsh is the accelerant. Min-hold to ~Jul 16; stop -10bp.",
    "MM-2026-012": "MOST CONTESTED LEG. Risk-on + sub-100 DXY (~99.5) keeps EUR firm near 1.158 — back to ~flat. Held on the rate-path asymmetry (paused ECB vs hawkish-bias Fed); pairs with the European-equity tilt. Today resolves it. Do not add into FOMC. Stop 1.182.",
    "MM-2026-013": "WORKING (+2.45%). Oil sub-$80 + soft Empire State faded the 2026-hike pricing to ~47%; 2Y eased to ~4.06%. The cleanest disinflation expression. FOMC today is the gate; guidance-light drops it 15-20bp. Min-hold to ~Jul 8; do not add. Stop 4.35%.",
}

# Notes for the closed ledger (keyed by id; falls back to the exit reason).
CLOSED_NOTES = {
    "MM-2026-006": ("STOPPED June 8. Q2 beat but the Q3 AI guide ($16.0B vs buy-side $17.2B) missed the number that "
                    "mattered at 41x; payrolls finished it."),
    "MM-2026-002": ("The US-Iran MoU (signs Jun 19, reopens the Strait toll-free for 60 days) removed the "
                    "re-escalation premium the long was built on. Brent broke the $87 weekly-close exit and the $84 "
                    "stop; now sub-$80. The book's MoU binary paid off on the duration side instead — surrendered by "
                    "design, not by surprise."),
    "MM-2026-011": ("Peace deflated the Hormuz tail the call spread owned. With Brent sub-$80 the $100 strike is ~$21 "
                    "away and the catalyst is dead. Closed near the $1 discipline level to recover residual premium."),
    "MM-2026-010": ("STOPPED on the melt-up Jun 16: Monday's +3.07% Nasdaq (NVDA $25B bond + buyback) against a "
                    "+1.05% DAX broke the 0.943 ratio stop. The relief rally re-rated US tech faster than European "
                    "financials — the risk the trade always carried. Tuesday's tech reversal came one session too "
                    "late. Re-expressed as the broadening RV MM-022."),
    "MM-2026-003": ("STOPPED June 10. The Brent-WTI spread compressed as the Hormuz premium drained out of the "
                    "Atlantic-basin grade faster than Cushing — the de-escalation hit Brent's relative premium "
                    "hardest. Defined spread risk; the stop did its job."),
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
    {"datum": "MM-008 option mark (model est. from spot — deep OTM after the melt-up, ~$34)", "source": "Model estimate (no live option feed)", "asof": TODAY, "stale": True},
    {"datum": "FOMC decision + dot plot/SEP: Wed Jun 17 2pm ET — Warsh's FIRST; ~98% priced HOLD at 3.50-3.75%; dot-plot/guidance the event; 2026-hike odds ~47%, 2026 cuts ~0. PENDING.",
     "source": "CME FedWatch + Conference Board + REX Shares + FXStreet", "asof": TODAY, "stale": False},
    {"datum": "Tue Jun 16 US close: Dow 51,999.67 (+0.64%, 2nd record); S&P 7,511.35 (-0.57%); Nasdaq 26,376.34 (-1.15%); SOX ~-5.7%; NVDA $207.41 (-2.37%)",
     "source": "Yahoo Finance + TheStreet (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "Brent ~$79 (-5%, first sub-$80 since March) / WTI ~$77 Jun 16 — war premium draining toward the Jun 19 MoU signing",
     "source": "CNBC + Fortune + Trading Economics (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "BoJ hiked to 1.00% (from 0.75%, highest since 1995) Jun 16 on a 7-1 vote; Gov. Ueda hospitalised/absent (Himino chaired); yen weakened, USDJPY ~160",
     "source": "Bloomberg + forex.com + FXStreet (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "Gold ~$4,331 close Jun 16 (3rd up session) then flat ~$4,326 into the Fed — real-rates engine; Silver ~$71.2",
     "source": "Trading Economics + GoldSilver (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "Empire State manufacturing 5.7 (June, from 19.6; consensus ~13) — sharp miss, soft data into the dots",
     "source": "NY Fed + Advisor Perspectives (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "DXY ~99.5 (sub-100) Jun 16; EURUSD ~1.159; Bund 10Y 2.94%; Gilt 10Y 4.81%",
     "source": "Trading Economics (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "US-Iran MoU: Switzerland (FDFA) confirmed Fri Jun 19 signing at Bürgenstock (Pakistan + Qatar mediating); digital framework reportedly signed Jun 15-16; Bloomberg 14-point draft. Hormuz toll-free 60 days only; HEU/assets/Lebanon unresolved. PENDING.",
     "source": "Bloomberg + Times of Israel + People's Daily (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "CAVEAT: Iran's joint military command warned Israel 'expect a hard response'; Netanyahu refused VP Vance's ask to scale back south Lebanon; Katz says Israel won't withdraw",
     "source": "Times of Israel + NBC + PBS (corroborated)", "asof": "2026-06-16", "stale": False},
    {"datum": "Trump (Jun 16): a rate increase 'would be wrong'; separately the chair should 'do whatever he wants'",
     "source": "Washington Post + NBC News", "asof": "2026-06-16", "stale": False},
    {"datum": "JBL (Jabil) reports Jun 17 BMO — consensus EPS 3.109, rev ~$8.64B; 13 buy/4 hold/0 sell; beat last 4 quarters",
     "source": "Finnhub (earnings_data.md, sourced)", "asof": "2026-06-16", "stale": False},
    {"datum": "Note: Fri Jun 19 is Juneteenth — US equity/bond markets CLOSED (same day as the MoU signing; trades Mon Jun 22)",
     "source": "NYSE holiday calendar", "asof": TODAY, "stale": False},
    {"datum": "SOFR ~3.62%", "source": "NY Fed (rail)", "asof": "2026-06-16", "stale": True},
]

earnings_ideas = [
    {
        "ticker": "JBL", "company": "Jabil Inc",
        "report_date": "2026-06-17", "report_timing": "BMO",
        "mode": "PRE-EARNINGS", "direction": "Long",
        "conviction_score": 6, "conviction_label": "High — data gap flagged",
        "conviction_rationale": (
            "Jabil is the under-the-radar AI-infrastructure hardware play, and the asymmetry is a consistent-beat "
            "machine reporting BMO TODAY into the exact theme that survived Tuesday's rotation: even as the SOX fell "
            "5.7%, the build-out read held. It has beaten consensus four quarters running (6.2%, 4.52%, 11.46%, "
            "9.3%), carries TTM revenue growth of 19% and EPS growth of 78.78%, and the sell side is 13 buy / 4 hold "
            "/ 0 sell. The data gap is positioning (short-interest unavailable), which caps the label."
        ),
        "research_conflict": False,
        "pillars": {"asymmetry": 1, "consensus": 2, "catalyst": 2, "positioning": 1},
        "pillar_confidence": {"asymmetry": "sourced", "consensus": "sourced",
                              "catalyst": "sourced", "positioning": "estimated"},
        "key_bullets": [
            "Reports TODAY Jun 17 BMO. Consensus EPS 3.109 on revenue ~$8.64B (Finnhub-sourced; street range "
            "~$3.03-3.11 / ~$8.5-8.6B). Beat in each of the last four quarters — a high-probability beat machine.",
            "Growth is real: TTM revenue +19%, EPS +78.78% YoY; 52-week range $175.08-$398.89. Sell side 13 buy / "
            "4 hold / 0 sell, period 2026-06-01.",
            "The catalyst the consensus underprices: Jabil's Intelligent-Infrastructure / AI-data-center segment is "
            "the read on whether Tuesday's semis de-risk was rotation or the start of a demand wobble. A clean guide "
            "says rotation; a soft guide validates the SOX -5.7%.",
        ],
        "what_moves_it": ("The AI/data-center hardware guide and margin trajectory vs an already-buy-heavy sell "
                          "side. A raise extends the AI-infra read-through and rebuts Tuesday's semis de-risk; a "
                          "cautious guide on tariff/freight cost — or on hardware demand — confirms the rotation. "
                          "Bear: a guide-down into a tape that just sold the cohort."),
        "client_talking_point": ("Jabil is the quiet AI-infrastructure beat machine — four straight beats, +79% EPS "
                                 "growth, 13 buys and no sells — reporting this morning, the day after semis fell "
                                 "5.7%. Its guide is the cleanest test of whether Tuesday was rotation or a demand "
                                 "crack. We like it long into the print; the only gap is positioning data we can't "
                                 "verify."),
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
        "THE DOTS THAT MAY NOT COME. The melt-up digested by rotation, not retreat: Tuesday the Dow printed a SECOND "
        "record (51,999.67, +0.64%) while the Nasdaq fell 1.15% and the SOX dropped ~5.7% — money left semis for "
        "financials ahead of the Fed. Oil broke $80 (Brent ~$79, first since March); the BoJ hiked to 1.00% "
        "(highest since 1995, Ueda absent) yet the yen WEAKENED; Empire State collapsed to 5.7. The decision lands "
        "today at 2pm: a hold is ~98% priced, the market is positioned entirely around the dot plot — and Warsh, a "
        "decade-long guidance critic, may begin dismantling the dots themselves. A guidance-light Fed is not dovish "
        "or hawkish; it is a structurally higher-vol regime that VIX 16.4 prices in no direction. The book is the "
        "winning side on duration and gold; the discipline is to own the binary cheaply and open no new directional "
        "macro before 2pm. Friday is Juneteenth — the MoU signing trades Monday."
    ),

    "summary_narrative": """
<p>The melt-up did not retreat &mdash; it rotated &mdash; and the one event the entire tape is built around may not
arrive in the form it expects. Tuesday June 16 was a de-risking <strong>rotation</strong>, not a sell-off: the Dow
rose 0.64% to a <strong>second straight record close at 51,999.67</strong> while the S&amp;P slipped 0.57% to
7,511.35 and the Nasdaq Composite fell 1.15% to 26,376.34. The Philadelphia Semiconductor Index dropped about
<strong>5.7%</strong> and NVIDIA fell 2.37% to $207.41 &mdash; Monday's worst-to-first inverted to first-to-worst as
money left semis for financials and industrials the day before Kevin Warsh's first FOMC. (Yahoo Finance,
TheStreet.)</p>

<p>Oil broke a line. Brent fell roughly 5% to <strong>~$79</strong>, its first sub-$80 print since March, and WTI to
~$77, a fourth down session, as the US-Iran memorandum moved to a confirmed <strong>signing Friday June 19</strong>
at B&uuml;rgenstock in Switzerland. The disinflation impulse the book's duration trades are built on deepened again,
and a soft Empire State (5.7, down from 19.6, consensus ~13) added to it. (CNBC, Fortune, NY Fed.)</p>

<p>Overnight, the Bank of Japan <strong>hiked to 1.00%</strong> &mdash; the highest since 1995 &mdash; on a 7-1
vote, with Governor Ueda hospitalised and absent (the first BoJ meeting ever held without its governor; Deputy
Himino chaired). And yet the yen <strong>weakened</strong>: the hike was fully priced, and USD/JPY sits pinned near
160 at the MoF's intervention line. The book's short USD/JPY (MM-007) is frustrated, not vindicated &mdash; a
historic tightening with no yen rally is the cleanest proof that a crushed-vol carry tape ignores fundamentals until
vol returns. (Bloomberg, forex.com.)</p>

<p>Now the decision, at 2pm ET. A hold at 3.50&ndash;3.75% is ~98% priced; the market is positioned entirely around
the dot plot and the bias shift. The non-consensus tell: Warsh has criticised forward guidance for a decade, and
reporting suggests he may begin <strong>dismantling the dots</strong> and stripping bias language as soon as today.
The event the tape is waiting for may dissolve &mdash; and a guidance-light Fed is not a dovish or hawkish outcome,
it is a structurally higher-vol one that a VIX near 16.4 prices in no direction at all. 2026 cuts have faded to
roughly zero, ~47% now price a 2026 hike, and Trump said Tuesday a hike &ldquo;would be wrong&rdquo; even as he
allowed the chair should &ldquo;do whatever he wants.&rdquo; (Conference Board, REX Shares, Washington Post.)</p>

<p>The honest caveats hardened. Switzerland confirmed the Friday signing, Bloomberg published a 14-point draft, and
a digital framework was reportedly signed Monday &mdash; but Hormuz is toll-free for only sixty days, the enriched
uranium and the frozen assets are unresolved, and Iran's joint military command warned Israel to &ldquo;expect a
hard response&rdquo; while Netanyahu refused to pull back from south Lebanon. The tape has priced a clean peace, a
non-event Fed, and a vol that never returns. The brief has priced none of the three &mdash; the posture is
two-sided, the concentration is hedged, and no new directional macro bet is opened before the dots. Friday is
Juneteenth; US markets are closed, so the signing trades Monday.</p>
""",

    "takeaways": [
        "<strong>The melt-up digested by rotation, not retreat.</strong> Tuesday: Dow +0.64% to 51,999.67 (a "
        "second straight record), S&amp;P -0.57% to 7,511.35, Nasdaq -1.15% to 26,376.34, SOX ~-5.7%, NVDA -2.37% "
        "to $207.41. Money left the most-crowded semis for financials (+1.5%) and industrials ahead of the Fed. "
        "Monday's worst-to-first inverted to first-to-worst. (Yahoo Finance, TheStreet.)",

        "<strong>Oil broke $80 &mdash; the disinflation impulse deepened.</strong> Brent -5% to ~$79 (first sub-$80 "
        "since March), WTI ~$77 (4th down session), as the US-Iran MoU moved to a confirmed Jun 19 signing that "
        "reopens the Strait toll-free for 60 days. A soft Empire State (5.7, from 19.6) reinforced the read. The "
        "duration book (MM-013 +2.45%, MM-009 ~+175%) is the winning side. (CNBC, Fortune, NY Fed.)",

        "<strong>The BoJ hiked to 1% &mdash; and the yen fell.</strong> The highest policy rate since 1995 (7-1 "
        "vote, Ueda hospitalised and absent), yet USD/JPY held near 160 because the hike was priced and crushed vol "
        "keeps carry on. The short-USDJPY book (MM-007) is frustrated, not vindicated &mdash; it needs vol to "
        "return, which is exactly what a guidance-light Fed could deliver. Fresh defined-risk expression: MM-021. "
        "(Bloomberg, forex.com.)",

        "<strong>The dot plot itself is the unpriced event.</strong> A hold is ~98% priced and the whole tape is "
        "positioned around the dots &mdash; but Warsh, a decade-long forward-guidance critic, may begin dismantling "
        "them today. A guidance-light Fed is not dovish or hawkish; it removes the calendar Fed-put and structurally "
        "re-rates vol higher. VIX 16.4 prices none of it &mdash; the cleanest long-vol setup of the cycle (MM-020). "
        "(Conference Board, REX Shares, FXStreet.)",

        "<strong>Gold is working on the real-rates engine.</strong> It extended to ~$4,331 then went flat ~$4,326 "
        "ahead of the dots, comfortably above its $4,250 stop. Lower oil cut hike odds and pulled real yields down. "
        "MM-005 (the book's 4GLD) is held; a dovish or guidance-light Warsh extends it, an explicitly hawkish dot "
        "plot is the one thing that reverses it first. (Trading Economics, GoldSilver.)",

        "<strong>The rotation is a tradeable regime, not noise.</strong> A record Dow against a -1.15% Nasdaq and "
        "a -5.7% SOX is the broadening a guidance-light, oil-disinflation Fed accelerates &mdash; and the AI complex "
        "is funding capex with debt (NVDA's $25B bond) the equity hasn't discounted. The stopped DAX/Nasdaq ratio "
        "(MM-010) is re-expressed cleaner as long RSP / short QQQ (MM-022).",

        "<strong>The peace is not signed, and Israel hardened.</strong> Switzerland confirmed the Jun 19 signing and "
        "Bloomberg published a 14-point draft, but Hormuz is toll-free only 60 days, the HEU and frozen assets are "
        "unresolved, Iran warned Israel of a 'hard response,' and Netanyahu refused to pull back from south Lebanon. "
        "The asymmetry of a deal that slips &mdash; Brent back toward $90+ &mdash; is large and unpriced. Friday is "
        "Juneteenth, so it trades Monday.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "35%",
         "headline": "Data-dependent / guidance-light hold leans dovish — disinflation tape broadens",
         "body": "Warsh holds at 3.50-3.75%, leans on the oil-disinflation impulse and the soft Empire State, and "
                 "keeps a 2026 cut alive (or removes the dots in a way the market reads as flexibility). The 2Y "
                 "falls 15-20bp, the curve steepens hard, gold extends on lower real yields, and the rotation "
                 "broadens to the median stock (RSP over QQQ). Risk up (broad) · rates down · dollar soft · oil "
                 "down · gold up."},
        {"kind": "base", "label": "Base", "pct": "45%",
         "headline": "Hawkish-neutral hold + guidance downgrade — vol re-rates, rotation continues",
         "body": "Warsh holds, shifts the bias toward neutral with firm inflation-vigilance language, and begins "
                 "downgrading forward guidance / the dots &mdash; no cut signal, no hike penciled, but a less "
                 "predictable Fed. Realised vol drifts higher (MM-020 pays), the front end holds ~4.05-4.15%, the "
                 "steepener grinds, and money keeps rotating out of mega-cap tech. Risk mixed · rates steady · "
                 "dollar firm · oil soft · gold flat · VIX up."},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "Explicitly hawkish dots OR the MoU fractures pre-signing",
         "body": "Warsh pencils a 2026 hike into the dots on the still-firm CPI and frames the oil move as "
                 "transitory &mdash; the 2Y jumps toward the 4.35% stop, gold gives back, AI multiples compress and "
                 "the S&amp;P retraces toward 7,200-7,000 where the put spreads pay; AND/OR Israel's rejection "
                 "fractures the deal before Friday and Brent snaps back toward $90+. Risk down · rates up · dollar "
                 "up · oil/gold spike."},
    ],

    "insights_layers": """
<p>The dominant driver this morning is positioning, not a print: the whole market has crowded onto one side of an
event whose rules the new chair may change. A hold at 3.50&ndash;3.75% is ~98% priced, so the decision is not the
event &mdash; the dot plot and the forward-guidance framework are. The non-consensus read is that Kevin Warsh, who
has argued against forward guidance for a decade, may use his first meeting to begin <em>dismantling</em> the dots
rather than shading them, and a Fed that gives less guidance is not a dovish or a hawkish Fed &mdash; it is a
higher-vol one. That is why the cleanest expression today is not a rates bet but a vol bet (MM-020), and why the
duration longs (MM-013) and the steepener (MM-009) are held but not added into the print.</p>

<p>The counter-intuitive hook is Tuesday's tape. A second straight record on the Dow sounds like a melt-up
continuing, until you find the Nasdaq fell 1.15% and the Philadelphia Semiconductor Index dropped 5.7% underneath
it. Consensus read Monday's +3% Nasdaq as the AI trade re-accelerating; twenty-four hours later the same cohort was
the funding source for a rotation into financials and industrials. The headline index masks a leadership change:
money is leaving the seven names that carried the market into the breadth a guidance-light, oil-disinflation Fed
would broaden. The headline says melt-up; the anatomy says rotation, and the rotation is the trade (MM-022).</p>

<p>Now the gap between real economy, what is priced, and the consensus narrative. <strong>Real economy:</strong>
Brent below $80, a 2Y at ~4.06%, a 2s10s near +41bp, an Empire State that collapsed to 5.7, gold firm on real
rates. <strong>What is priced:</strong> a ~98% FOMC hold and, beneath it, a VIX near 16.4 that treats Warsh's debut
as a non-event and assumes the dots arrive intact. <strong>Consensus narrative:</strong> &lsquo;the new chair is a
hawk, so the only risk is a hawkish dot plot.&rsquo; The gap &mdash; and the alpha &mdash; is that the market is
debating the <em>level</em> of the dots while the real variance is in whether the dots <em>exist</em>; a guidance
regime change is the one outcome the complacent vol prices in no direction.</p>

<p>Go around the world. <strong>Japan:</strong> the BoJ delivered a historic hike to 1% with its governor in
hospital, and the yen weakened anyway &mdash; the carry trade is maximally stretched at the MoF line, a coiled
spring that only vol can release (MM-021). <strong>Asia:</strong> China data stayed soft (May retail sales -0.6%
y/y, the first annual decline since 2022; property in its 35th month of decline), a disinflationary drag the West
keeps importing. <strong>Europe:</strong> the DAX held near records and ASML became the continent's most valuable
company ever, even as US semis sold &mdash; the cross-region divergence the book now expresses through breadth, not
the stopped DAX/Nasdaq ratio.</p>

<p>The political angle the market is under-weighting is no longer the deal's existence &mdash; it is its
durability, and the new fault line is the Fed. On the MoU, the binding constraint remains Jerusalem: Iran's military
warned Israel of a &ldquo;hard response,&rdquo; Netanyahu refused VP Vance's request to scale back in south Lebanon,
and the oil market has front-run a signature a third party can still break. On rates, the constraint is the
Trump-Warsh relationship: the President said a hike &ldquo;would be wrong&rdquo; the day before the decision, which
makes a hawkish dot plot not just a market event but a political one &mdash; and a new chair establishing
independence may lean <em>more</em> hawkish precisely to prove he is not taking the instruction.</p>

<p>Priced-versus-not. <strong>Under-priced:</strong> a guidance-regime change and the vol re-rating it implies (VIX
16.4); the broadening rotation; the MoU slippage tail. <strong>Fairly priced:</strong> the FOMC hold itself
(~98%); the ECB pause; the BoJ hike (it just happened and the yen fell). <strong>Fully priced:</strong> the
straight-line peace move in oil (Brent sub-$80 has front-run an unsigned deal). <strong>Over-priced (at risk):</strong>
the consensus that the only FOMC risk is a hawkish level &mdash; and the assumption that the dots arrive at all.</p>
""",

    "wrap": """
<p>The second-order effect consensus is missing this morning is not in the level of the dots. It is that the dots
may not come. The entire tape has crowded onto a debate about whether Kevin Warsh pencils a 2026 hike, and almost
no one is positioned for the possibility that a chair who has spent a decade attacking forward guidance uses his
first meeting to start dismantling it. A Fed that says less is not a dovish Fed or a hawkish one. It is a louder one
&mdash; every data point becomes its own shock &mdash; and that is a vol story the market has priced at sixteen.</p>

<p>Start with Tuesday, because the rotation is the tell. The Dow closed at a second straight record while the Nasdaq
fell more than a percent and the semiconductor index dropped almost six (Yahoo Finance, TheStreet). Monday's
worst-to-first became Tuesday's first-to-worst, and the money that left Nvidia and the chips did not leave the
market &mdash; it moved into financials and industrials. This is what a leadership change looks like in real time:
the index holds while its internals turn over. The book felt none of it on the downside, because the position that
the Monday melt-up stopped &mdash; the long-DAX, short-Nasdaq ratio &mdash; was already closed; the cleaner way to
own the same idea now is long the equal-weight market against the cap-weighted tech complex, and Tuesday wrote that
thesis for us.</p>

<p>The macro underneath kept moving the same direction. Brent broke eighty dollars for the first time since March, a
fourth down session, and a soft Empire State survey reinforced the disinflation the oil collapse already implied.
The front end heard it: the two-year eased to 4.06% and the steepener widened to forty-one basis points, the best
position in the book. The long end did not fully cooperate &mdash; it backed up on the equity rotation and the
supply overhang &mdash; which is why the cleanest disinflation expression is the front end and the curve, not the
ten-year outright, and why the book holds those into the meeting rather than adding the day of the print.</p>

<p>Japan is the lesson in what crushed vol does to fundamentals. The Bank of Japan raised its policy rate to one
percent, the highest since 1995, with its governor in a hospital bed and a deputy in the chair, and the yen
weakened. A historic tightening produced a weaker currency because the move was fully priced and a carry tape with
volatility at sixteen does not care about a known differential. That is not a reason to abandon the short; it is the
reason to change its shape. A spot short bleeds carry waiting for the turn; a put spread owns the same downside with
defined premium and pays into exactly the catalyst &mdash; vol returning &mdash; that the spot trade needs. The yen
at the intervention line is a coiled spring, and the spring is volatility.</p>

<p>So the posture into 2pm is the same discipline as yesterday, sharpened by the new information. The duration longs
and the steepener are the winning side and are held, not added. Gold is held on its real-rate engine, flagged as
the first hedge to give back if the dots come in hawkish. The contested short-EUR leg is not touched into the event
that resolves it. The fresh ideas are a long-vol structure for the guidance-regime risk, a defined-risk yen-downside
spread for the BoJ coil, and the breadth-over-concentration rotation &mdash; and not one of them is a directional
bet on the Fed's level, because the day a new chair may re-write the framework is the day to own the variance, not
to guess the number. The tape has priced a clean peace, a quiet Fed, and a vol that never returns. Israel says the
first is not binding, Warsh may say the second is not his job, and sixteen says the third is free to doubt.</p>
""",

    "correlation_regime": """
<p><strong>1. The index decoupled from its own leaders.</strong> The Dow printed a record while the Nasdaq fell
1.15% and the SOX dropped 5.7% &mdash; a textbook breadth rotation. The dominant driver flipped in a single session:
from 'AI mega-cap leads everything' (Monday) to 'everything-but-AI leads' (Tuesday). A correlation break this sharp
means the leadership regime is turning, which is why the trade is now long breadth (RSP) / short concentration (QQQ),
idea MM-022 &mdash; the cleaner heir to the stopped DAX/Nasdaq ratio.</p>

<p><strong>2. The BoJ hiked and the yen fell &mdash; rate-differential logic broke.</strong> A 25bp hike to a
30-year-high policy rate should lift a currency; the yen weakened instead. The break tells you the driver of USD/JPY
right now is not the differential but the vol regime: at VIX 16 the carry trade overrides policy. The correlation
re-couples the moment vol returns &mdash; which is the entire thesis of owning yen downside as a convexity structure
(MM-021) rather than fighting it in spot.</p>

<p><strong>3. The long end decoupled from the front end.</strong> The 2Y eased to ~4.06% on the disinflation while
the 10Y backed up to ~4.47% on the equity rotation and supply &mdash; the curve steepened not because the back end
rallied but because the front did the work. That is the 'good steepening' the position (MM-009) is built for, and it
confirms the front end, not the 10Y outright, is the clean expression of the oil-disinflation view today.</p>
""",

    "vol_skew": """
<p><strong>The vol regime, not the vol level, is the trade today.</strong> VIX closed ~16.4 Tuesday (a touch firmer
on mild pre-Fed hedging), and the term structure is in contango (est. VIX9D ~15.5 · VIX ~16.4 · VIX3M ~18.5 · VIX6M
~20.0) &mdash; the complacent shape into a binary the market treats as settled. The mispricing is structural: a new
chair who may strip forward guidance turns a predictable, calendar-anchored Fed into a data-dependent one, and a
data-dependent Fed means higher realised vol as each print becomes its own event. The trade implication: own
convexity on the regime, not a direction. The held 7300/7000 put spread (MM-008, ~$34, deep OTM) is the legacy
downside tail; the fresh expression (MM-020) is a VIX Jul 18/24 call spread (or a 1-month SPX 25-delta strangle) &mdash;
cheap, defined-risk length in vol itself, struck for a re-rating rather than a crash. If Warsh keeps the dots intact
and delivers a clean status-quo hold, the structure decays to its premium; that defined premium is the cost of
owning the one outcome the tape has priced at zero.</p>
""",

    "sector_rv": """
<p><strong>Leading (Tue Jun 16):</strong> financials (+1.5%) and industrials &mdash; the rotation destinations;
the Dow to a second record; transports/airlines on sub-$80 fuel; defensives bid into the Fed.
<strong>Lagging:</strong> US semis &amp; AI (SOX ~-5.7%, NVDA -2.37%) as the most-crowded cohort funded the
rotation; energy producers (XLE rolling over with Brent sub-$80; sanctioned Iranian barrels the overhang); the
broad Nasdaq (-1.15%).
<strong>Today's watch:</strong> Jabil (Jun 17 BMO) on AI/data-center hardware demand &mdash; the cleanest test of
whether Tuesday's semis de-risk was rotation or the first crack in the build-out. FedEx is Jun 23.</p>

<p><strong>RV:</strong> The cleanest fresh RV is long RSP (S&amp;P equal-weight) / short QQQ (Nasdaq-100) &mdash;
Tuesday's record-Dow/falling-Nasdaq split is the rotation a guidance-light, oil-disinflation Fed broadens, and the
AI-debt overhang (NVDA $25B bond) is the structural tailwind to the short leg (idea MM-022, the heir to the stopped
DAX/Nasdaq ratio). The transports-vs-energy RV (MM-019) remains live as the deeper oil move (sub-$80) reprices the
two sectors in opposite directions, low beta to the 2pm decision.</p>
""",

    "positioning": """
<p><strong>The crowd is positioned for a level when the risk is a regime.</strong> Going into 2pm, fast money is
short duration into a hawkish dot plot, long the dollar, and short vol &mdash; all bets on <em>where</em> the dots
land. The pain trade is not a dovish surprise; it is Warsh removing or downgrading the dots entirely, which leaves
the hawkish-dot shorts with nothing to trade against and re-rates vol against the short-vol crowd. In equities, the
melt-up left positioning maximally long the seven mega-caps that just started to roll (SOX -5.7%), and the rotation
into financials/industrials is early &mdash; the pain trade there is a continued broadening that strands the
index-tracking longs in the wrong names. In FX, the yen carry trade is the most crowded it has been, stretched to
the MoF line even through a BoJ hike. In rates, the front end still half-prices a 2026 hike (~47%) &mdash; squeeze
fuel for the steepener and the 2Y long on any guidance-light hold. The single position the complacent VIX is wrong
on in <em>every</em> direction is short volatility into a chair who may change the rules.</p>
""",

    "funding": """
<p>SOFR near 3.62% &mdash; unchanged, and the decision is unlikely to move it (a hold is ~98% priced).
<strong>The Pozsar mechanic:</strong> the plumbing signal that matters today is not repo but the term premium and
the guidance channel. Forward guidance is, mechanically, a tool that compresses the term premium by telling the
market the path of the funding rate; if Warsh dismantles it, he removes a structural anchor on the long end, and the
term premium widens not because inflation rose but because the Fed stopped pre-committing the path. That is the
mechanism behind a steeper curve <em>and</em> a higher MOVE at once &mdash; the 10Y backing up Tuesday (~4.47%) even
as the 2Y fell is the first hint of it. Rates vol (MOVE est. ~104, firmer) is the cleaner read on this than equity
vol. Watch the long-end reaction to the press conference, not just the dot grid: if the term premium widens on a
guidance downgrade, the steepener (MM-009) accelerates and the case for owning vol (MM-020) is made in the bond
market before the equity market notices.</p>
""",

    "tape_missing": """
<p><strong>The tape is not pricing a guidance regime change.</strong> The whole market is debating the level of the
dots; almost no one is positioned for Warsh removing or downgrading them. A ~98% hold sits over a VIX of 16.4 that
assumes the framework is unchanged. If the new chair strips bias language and de-emphasises the dot grid, the
immediate read is neither dovish nor hawkish &mdash; it is that the Fed is now less predictable, every print becomes
a discrete catalyst, and realised vol re-rates higher. That outcome is barely in the price. The vol structure
(MM-020) and the held put spread (MM-008) are the instruments for it.</p>

<p><strong>Just behind it: the peace still has a third party that says it won't sign.</strong> Switzerland confirmed
the Jun 19 signing and Bloomberg published a 14-point draft, but Hormuz is toll-free for only sixty days, the
enriched uranium and frozen assets are unresolved, Iran's military warned Israel of a 'hard response,' and
Netanyahu refused to scale back in south Lebanon. The oil market has front-run a clean peace below $80; if Jerusalem
breaks it, Brent snaps back toward $90+ and the disinflation read reverses. We do not chase crude lower here because
the binding constraint is a party not at the signing table. The signing is Friday &mdash; Juneteenth &mdash; so the
market cannot react until Monday, which leaves a three-day gap of headline risk with no price discovery.</p>

<p><strong>The Burry tell &mdash; the structural thing nobody is looking at.</strong> The Fed has been the market's
shock absorber for fifteen years through one tool above all: forward guidance, the promise to telegraph the path. A
chair who dismantles that is not making a single dovish or hawkish decision &mdash; he is removing the calendar
Fed-put and handing volatility back to the market permanently. The consequence that resolves over the next two-to-three
quarters is a structurally higher vol floor: a world where a hot CPI or a soft payroll moves markets the way it did
before 2009, because the Fed no longer pre-commits to absorb it. The equity market, with VIX at 16 and an
index concentrated in seven names that already started to wobble, is the least prepared for that regime. It is not a
crash call; it is a reason to be structurally long volatility (MM-020) and long breadth over concentration (MM-022)
before the regime announces itself.</p>
""",

    "book_outlook": {
        "commentary": (
            "Tuesday's rotation ran against the book's core for the first time in a week, and today's 2pm decision is "
            "the swing. The book's <b>US AI-semis concentration (Micron ~25.8%, plus NVDA/AVGO/AMD)</b> took the "
            "brunt of the SOX's ~5.7% drop &mdash; the same names that led Monday's +3% led Tuesday's reversal, which "
            "is precisely why a 25.8% single-name weight into TWO catalysts in seven sessions (the Fed today, MU "
            "earnings Jun 24) is the book's defining risk, not its edge. The disinflation side helped: <b>Xetra-Gold "
            "(4GLD)</b> held its real-rates gain near $4,331, and the <b>front end</b> of the book's rate exposure "
            "improved as the 2Y eased to ~4.06% &mdash; though the <b>US Treasury 1.25% 2031</b> gave a little back "
            "as the 10Y backed up to ~4.47%. <b>TotalEnergies (TTE)</b>, the energy hedge, keeps bleeding as Brent "
            "broke $80. The dominant risk is the 2pm dots: an explicitly hawkish Warsh compresses the 25.8% semis "
            "concentration hardest AND reverses gold first; a guidance-light Warsh re-rates vol, which is bad for a "
            "concentrated, levered-long-semis book regardless of direction. Collar the Micron concentration before "
            "2pm and before the print; do not chase the rotation's losers or winners into the decision."
        ),
        "outperform": [
            {"name": "Xetra-Gold (4GLD)", "why": "Held its real-rates gain near $4,331 while the equity book "
             "rotated &mdash; the one position that is both a hedge and a winner. Lower oil and a soft Empire State "
             "keep hike odds (and real yields) low; a dovish or guidance-light Warsh extends it."},
            {"name": "SAP / European software", "why": "Tuesday's rotation OUT of high-beta US semis INTO quality "
             "software favours the book's SAP (+132%) over its NVDA/AVGO/MU stack; a guidance-light, oil-disinflation "
             "Fed re-rates software over semis, and SAP carries none of the SOX-5.7% beta."},
            {"name": "US Treasury 1.25% 2031 (front-end-led)", "why": "The disinflation impulse pulled the 2Y to "
             "~4.06%; the bond's duration works on any guidance-light hold, even as the 10Y back-up capped Tuesday's "
             "gain. The winning side of the macro for the book's rate sleeve."},
        ],
        "underperform": [
            {"name": "US AI-semis (Micron 25.8%, NVDA/AVGO/AMD)", "why": "Took the brunt of Tuesday's SOX ~-5.7% "
             "rotation; the book's amplifier ran against it. Into the 2pm dots AND MU earnings Jun 24, the 25.8% "
             "concentration is the risk &mdash; an explicitly hawkish Warsh compresses it hardest."},
            {"name": "TotalEnergies (TTE)", "why": "The energy hedge keeps rolling over as Brent breaks $80 (first "
             "since March); sanctioned Iranian barrels are the supply overhang into the Jun 19 signing. The clean "
             "drag on the book this week."},
        ],
        "watch": [
            {"label": "Collar the 25.8% Micron concentration NOW — two catalysts in seven sessions", "text": "MU at "
             "25.8% into the Fed today AND earnings Jun 24, with IVol elevated, is the most urgent action on the "
             "book. A collar (rich calls finance fat puts) caps both the 2pm and the print risk for near-zero cost; "
             "the SPX put structures (MM-008) are the index overlay. Do not wait for 2pm."},
            {"label": "The risk today is vol, not just direction", "text": "A guidance-light Warsh re-rates realised "
             "vol higher, which is corrosive for a concentrated, levered-long-semis book even on a 'neutral' "
             "outcome. The book benefits from owning the vol idea (MM-020) as an overlay rather than guessing the "
             "dot-plot level."},
            {"label": "Hedge the USD sleeve into a sub-100 dollar; hold the bond swap for the print", "text": "The "
             "EUR-base book is ~72% USD with DXY below 100 &mdash; a seagull or collar on the USD sleeve is overdue. "
             "On the bonds (UST 2031, Siemens), a guidance-light hold rallies them and improves the swap entry; a "
             "hawkish surprise is the better harvest moment. Wait for 2pm before acting on either."},
        ],
    },

    "consensus": """
<p><strong>Consensus BID:</strong> Kevin Warsh is a hawk, so the risk from his first FOMC is a hawkish dot plot &mdash;
the median dot shifts toward tightening on the still-firm CPI, real yields rise, and the rotation-weary melt-up is
the moment to fade equities, gold and duration. The new chair has every incentive to establish credibility early,
and the hot inflation data gives him the cover.</p>

<p><strong>The strongest argument against &mdash; the OFFER:</strong> the market is fighting over the level of the
dots while the real variance is whether the dots survive. A chair who has attacked forward guidance for a decade is
more likely to change the framework than to merely shade it, and a guidance downgrade is neither the hawkish nor the
dovish outcome the consensus is positioned for &mdash; it is a higher-vol one that VIX 16.4 prices in no direction.
Consensus has pre-committed to a debate about a number; the cheaper, less-crowded side is to own the variance of the
framework itself.</p>
""",

    "one_chart": """
<p class="theme">The dot grid is the chart &mdash; not where the dots land, but whether Warsh still draws them.</p>
<p>The single thing the market watches today is the 2pm dot plot, and the level that changes the story is the 2Y at
4.06% read against it. A data-dependent or guidance-light Warsh sends the 2Y toward 3.90% and steepens the curve; an
explicitly hawkish dot plot that pencils a 2026 hike sends it toward the 4.35% stop and compresses everything the
rotation has not already sold. But the real signal is structural: if the dot grid is downgraded or the bias language
is stripped, watch the long end and the MOVE index, not the 2Y &mdash; a widening term premium on a guidance
downgrade is the tell that vol is re-rating. With VIX at 16.4 the market is pricing neither the level nor the
framework risk. Own the binary cheaply until 2pm.</p>
""",

    "catalyst_calendar": [
        {"day": "Tue", "date": "Jun 16 ✓",
         "event": "Rotation, not retreat — Dow 2nd record, Nasdaq -1.15%, SOX -5.7%; oil breaks $80; BoJ hikes to 1%",
         "consensus": "Dow +0.64% to 51,999.67 (2nd record); S&P -0.57% to 7,511.35; Nasdaq -1.15% to 26,376.34; "
                      "SOX ~-5.7%; NVDA -2.37%. Brent -5% to ~$79. BoJ +25bp to 1.00% (Ueda absent), yen weakened. "
                      "Empire State 5.7. Sources: Yahoo, TheStreet, CNBC, Bloomberg, NY Fed.",
         "view": ("The melt-up digested by rotation. Confirmed the disinflation regime (duration/gold winning) and "
                  "revealed the leadership turn (semis funding the rotation) — the basis for the breadth RV MM-022."),
         "asymmetry": "Resolved as a rotation, not a top. The semis de-risk into the Fed is the broadening a "
                      "guidance-light Warsh accelerates — own breadth over concentration (MM-022).",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 17 — THE EVENT (← TODAY)",
         "event": "FOMC decision + dot plot/SEP — Warsh's FIRST, 2pm ET; ~98% hold priced",
         "consensus": "Hold at 3.50-3.75% (~98% priced); the dots, the SEP, and any forward-guidance change are the "
                      "entire event. 2026 cuts ~0, ~47% price a 2026 hike. Press conference 2:30pm. "
                      "Sources: CME FedWatch, Conference Board, REX Shares, FXStreet.",
         "view": ("Three paths: (1) data-dependent/guidance-light hold leaning dovish — 2Y -15-20bp, steepener "
                  "accelerates, gold and breadth re-rate; (2) hawkish-neutral + guidance downgrade — vol re-rates "
                  "(MM-020 pays), rotation continues; (3) explicitly hawkish dots (a hike penciled) — 2Y toward "
                  "4.35% stop, gold gives back, AI multiples compress, put spreads pay. VIX 16.4 under-prices ALL."),
         "asymmetry": "The market debates the dots' LEVEL; the unpriced risk is whether Warsh keeps the dots at all. "
                      "Own the variance of the framework, not the number (MM-020).",
         "dir": "flat"},
        {"day": "Wed", "date": "Jun 17",
         "event": "US May Retail Sales (8:30am) + Jabil (JBL) earnings (BMO)",
         "consensus": "Retail Sales (May) at 8:30am ET, before the FOMC; Jabil reports BMO — consensus EPS 3.109, "
                      "rev ~$8.64B; the AI/data-center hardware read (Finnhub-sourced).",
         "view": "A soft Retail Sales print into a guidance-light Fed is the disinflation combination; a firm "
                 "consumer plus hawkish dots is the bear combination. Jabil is the test of whether Tuesday's "
                 "semis de-risk was rotation or a demand crack.",
         "asymmetry": "JBL: four straight beats into a supportive AI-infra tape the day after semis fell 5.7% = the "
                      "asymmetry; a clean guide rebuts the de-risk, a soft guide validates it.",
         "dir": "flat"},
        {"day": "Thu", "date": "Jun 18",
         "event": "Bank of England decision + US jobless claims / Philly Fed",
         "consensus": "BoE expected to HOLD Bank Rate at 3.75% (prior 8-1 vote); UK CPI ~2.8% and projected to rise. "
                      "US weekly jobless claims + Philadelphia Fed manufacturing. Sources: Bank of England.",
         "view": "BoE hold is near-certain; the read is the vote split and the inflation language. US claims/Philly "
                 "Fed are the post-FOMC data check on the disinflation-vs-stall debate.",
         "asymmetry": "A jobless-claims spike post-FOMC reinforces the front-end long (MM-013); a hawkish BoE "
                      "dissent count is a minor Gilt/Sterling signal.",
         "dir": "flat"},
        {"day": "Fri", "date": "Jun 19",
         "event": "US-Iran MoU signing (Switzerland) — US markets CLOSED (Juneteenth)",
         "consensus": "Signing scheduled at Bürgenstock (Pakistan + Qatar mediating); Strait reopens toll-free for "
                      "60 days, US lifts blockade. US equity/bond markets closed for Juneteenth. Sources: Swiss "
                      "FDFA, Bloomberg, NPR.",
         "view": ("PENDING. A clean signing = oil toward $75-80, disinflation confirmed. The live risk is Israel — "
                  "it warned of a 'hard response' and refuses to leave south Lebanon. US markets are closed, so the "
                  "tape cannot react until Monday — a three-day headline gap with no price discovery."),
         "asymmetry": "Clean signing = lower-for-longer oil. Israel breaks it / it slips = Brent back to $90+, the "
                      "disinflation read reverses. Large, unpriced, and trapped behind a market holiday.",
         "dir": "down"},
        {"day": "Wed", "date": "Jun 24",
         "event": "Micron (MU) FY Q3 — after close (BOOK-CRITICAL)",
         "consensus": "Reports Jun 24 AMC. The book's LARGEST position (~25.8%) and the HBM/AI-memory bellwether; "
                      "IVol elevated. GS PT doubled to 900 into the print. Source: company calendar / Finnhub.",
         "view": "Two-sided and book-defining: HBM sold out into the supercycle is the bull, but a 25.8% weight into "
                 "a high-IVol print the week of the Fed is a risk-management problem first. Collar before the event.",
         "asymmetry": "A beat-and-raise extends the supercycle; a guide wobble on a 25.8% concentration is the "
                      "book's largest single-name drawdown risk. The collar is the trade, not a directional bet.",
         "dir": "flat"},
    ],

    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 · Short EURAUD:</strong> close above 1.660. At ~1.643; stop 1.662. ECB pause behind it, no forward EUR catalyst; risk-on keeps a mild AUD bid. Slow grind lower. Hold.</li>
<li><strong>MM-2026-004 · Short US 10Y yield:</strong> stop 4.65%. At ~4.47% — backed up on Tuesday's rotation/supply, modestly offside. The slower-burn duration leg; the front end is the cleaner expression. Guidance-light FOMC = 10Y toward 4.30%. Do NOT add. Hold.</li>
<li><strong>MM-2026-005 · Long gold:</strong> min hold to ~Jul 15; stop $4,250. At ~$4,326. WORKING on the real-rates engine; held flat into the dots. A dovish/guidance-light Warsh extends it; hawkish dots reverse it first. Hold.</li>
<li><strong>MM-2026-007 · Short USDJPY:</strong> stop 163.00. At ~160. FRUSTRATED — the BoJ hiked to 1% and the yen WEAKENED (priced; crushed vol keeps carry on). Needs vol to return. Pinned at the MoF line. Fresh defined-risk expression MM-021. Hold.</li>
<li><strong>MM-2026-008 · SPX put spread:</strong> S&P ~7,511 → deep OUT of the money, marked ~$34. Held only for the FOMC tail inside Jun 27 expiry; VIX 16.4 + a chair who may re-write the vol regime make it the cheapest insurance on the board. Hold through 2pm; do not lift.</li>
<li><strong>MM-2026-009 · 2s10s steepener:</strong> min hold to ~Jul 16; stop -10bp. At ~+41bp; target +60bp. BEST OPEN POSITION (~+175%). The 2Y eased while the 10Y held — the 'good steepening'. A guidance-light Warsh is the accelerant. Hold.</li>
<li><strong>MM-2026-012 · Short EURUSD:</strong> stop 1.182. At ~1.158. MOST CONTESTED — risk-on + sub-100 DXY keeps EUR firm. Held on the rate-path asymmetry; today resolves it. Do not add into FOMC. Hold.</li>
<li><strong>MM-2026-013 · Short US 2Y yield:</strong> stop 4.35%; min hold to ~Jul 8. At ~4.06%. WORKING (+2.45%): oil sub-$80 + soft Empire State faded 2026-hike pricing to ~47%. The cleanest disinflation expression. Guidance-light FOMC drops it 15-20bp. Do NOT add. Hold.</li>
</ul>
""",

    "client_ammo": [
        {"q": "The Dow hit a record but the Nasdaq fell — what actually happened Tuesday?",
         "a": ("Rotation, not a top. The Dow rose to a second straight record while the Nasdaq fell 1.15% and the "
               "chip index dropped almost 6% — money left the most-crowded AI mega-caps for financials and "
               "industrials ahead of the Fed. Monday's leaders became Tuesday's funding source. It's a leadership "
               "change, and we're positioning for it to broaden, long the equal-weight market against the "
               "cap-weighted tech complex.")},
        {"q": "Everyone says the Fed is a non-event — is it?",
         "a": ("The decision is — a hold is 98% priced. The event is the dot plot, and the thing almost no one is "
               "positioned for is that Warsh, who has criticised forward guidance for a decade, may start "
               "dismantling the dots at his first meeting. A Fed that gives less guidance isn't dovish or hawkish — "
               "it's more volatile, because every data point becomes its own shock. With VIX at 16, that's the "
               "cheapest risk on the board to own.")},
        {"q": "The Bank of Japan hiked to a 30-year-high rate — why did the yen fall?",
         "a": ("Because the hike was fully priced and volatility is crushed. At VIX 16 the carry trade ignores a "
               "known rate differential — a historic tightening with the yen already where it is doesn't move it. "
               "That's not a reason to give up on the short; it's the reason to own yen downside as a defined-risk "
               "option structure that pays when volatility returns, rather than bleeding carry in spot.")},
        {"q": "Should we be doing anything about Micron before today?",
         "a": ("Yes — collar it. Micron is 25.8% of the book into two catalysts in seven sessions: the Fed this "
               "afternoon and its own earnings June 24, with option premiums already rich. A collar uses those rich "
               "calls to finance protective puts for near-zero cost, capping both events' downside while keeping "
               "the upside we like. A 25.8% single-name weight into a high-volatility print is a risk-management "
               "question first, a view second.")},
        {"q": "Is the Iran peace deal done?",
         "a": ("Not yet — it's set to be signed Friday in Switzerland, and the wildcard hardened: Iran's military "
               "warned Israel to 'expect a hard response,' and Netanyahu refused to pull back from south Lebanon. "
               "The binding constraint is Jerusalem, not Tehran. And Friday is Juneteenth, so US markets are closed "
               "— if anything breaks, we can't react until Monday. That's why we've surrendered the oil longs but "
               "are not chasing crude lower into a signature a third party can break.")},
        {"q": "Gold is near a record again — do we take profit?",
         "a": ("Not into the Fed. Gold is working on a different engine than people assume — not the war, but real "
               "rates: lower oil cut the odds of Fed hikes, real yields fell, and that lifted bullion to ~$4,331. "
               "It's the one position that's both a hedge and a winner. The single risk is an explicitly hawkish "
               "dot plot this afternoon, which would be the first thing to reverse it — so we hold it but flag it "
               "as the first hedge to give back.")},
    ],

    "ideas_note": (
        "<p>The day a new chair may re-write the framework, the discipline is to own the variance, not guess the "
        "number. The book's macro posture is set; the fresh ideas are deliberately low-correlation to the dot-plot "
        "level. <strong>Long vol into the guidance-regime risk (MM-020)</strong> — a VIX Jul 18/24 call spread (or "
        "1-month SPX strangle); at VIX 16.4 the cheapest way to own a structural vol re-rating if Warsh strips the "
        "dots. <strong>USD/JPY downside spread (MM-021)</strong> — the BoJ hiked and the yen fell; a defined-risk "
        "put spread owns the MoF-intervention / vol-return tail the spot short (MM-007) is waiting for. <strong>Long "
        "RSP / short QQQ (MM-022)</strong> — Tuesday's record-Dow/falling-Nasdaq rotation as a breadth-over-"
        "concentration RV, the cleaner heir to the stopped DAX/Nasdaq ratio. <strong>No fourth idea, and no new "
        "directional macro before 2pm</strong> — forcing a bet on the dot-plot level the day a new chair may scrap "
        "the dots is the trap, not the trade. The duration longs (MM-013), the steepener (MM-009) and gold (MM-005) "
        "are held, not added.</p>"
    ),

    "event_radar_note": (
        "<p>The melt-up digested by rotation: Tuesday the Dow printed a 2nd record while the Nasdaq fell 1.15% and "
        "the SOX dropped ~5.7%; oil broke $80; the BoJ hiked to 1% (Ueda absent) yet the yen weakened; Empire State "
        "collapsed to 5.7. Ahead: the FOMC decision + dot plot TODAY at 2pm (Warsh's first — the event of the week, "
        "and the dots themselves may be downgraded), Retail Sales + Jabil today, the BoE Thu Jun 18, and the US-Iran "
        "MoU signing Fri Jun 19 (Juneteenth — US closed, so it trades Monday; Israel the live wildcard). MU earnings "
        "Jun 24 is book-critical. The book is the winning side on duration and gold; the fresh ideas own the vol "
        "regime, the yen coil, and the rotation. No new directional macro before the dots.</p>"
    ),

    "burry_tell": (
        "Forward guidance has been the Fed's primary shock absorber for fifteen years — the promise to telegraph the "
        "path of the funding rate, which compresses the term premium and turns the central bank into a calendar-anchored "
        "backstop. Kevin Warsh has argued against it for a decade, and his first meeting is the moment he can begin "
        "to dismantle it. The structural thing nobody is pricing: a chair who downgrades the dots and strips bias "
        "language is not making a dovish or a hawkish decision — he is removing the calendar Fed-put and handing "
        "volatility back to the market permanently. The consequence that resolves over the next two-to-three "
        "quarters is a higher vol floor: a world where a hot CPI or a soft payroll moves markets the way it did "
        "before 2009, because the Fed no longer pre-commits to absorb it. The equity market — VIX at 16, an index "
        "concentrated in seven names that already started to wobble Tuesday — is the least prepared for that regime. "
        "It is not a crash call; it is the reason to be structurally long volatility (MM-020) and long breadth over "
        "concentration (MM-022) before the regime announces itself."
    ),

    "earnings_summary": (
        "Jabil (JBL): PRE-PRINT (reports TODAY Jun 17 BMO) — the under-the-radar AI-infrastructure hardware play. "
        "Consensus EPS 3.109 on revenue ~$8.64B (Finnhub-sourced; street ~$3.03-3.11 / ~$8.5-8.6B); beat in each of "
        "the last four quarters (6.2%, 4.52%, 11.46%, 9.3%); TTM revenue +19%, EPS +78.78%; sell side 13 buy / 4 "
        "hold / 0 sell. It reports the morning after the SOX fell 5.7%, so its Intelligent-Infrastructure guide is "
        "the cleanest test of whether Tuesday's semis de-risk was rotation or the start of a demand wobble. "
        "Long-leaning into the print; the only data gap is unverifiable positioning. FedEx is Jun 23; Micron (the "
        "book's 25.8% position) is Jun 24 AMC and is carried in Trade Ideas / the book outlook, not here."
    ),
    "earnings_why": (
        "Jabil is the one name that clears the universe filter inside the window this morning. It is a ~$40bn-cap US "
        "name reporting Jun 17 BMO (inside the 5-day-pre window), and it is the clean read on whether the AI/data-"
        "center hardware demand the tape is debating — after Tuesday's SOX -5.7% — is still translating into orders "
        "for the infrastructure builders. Consensus EPS and the recommendation split are Finnhub-sourced; short-"
        "interest/positioning is unavailable and tagged estimated, which caps the conviction label. Excluded this "
        "morning: FedEx (reports Jun 23, outside the window), Micron (Jun 24 AMC — carried in the book outlook as "
        "the 25.8% concentration risk), and homebuilders/other names outside the Tech/Financials/Industrials/"
        "Utilities universe."
    ),

    "book_aim": (
        "Two-sided and deliberately uncrowded into Warsh's first decision. The MoU binary resolved on the book's "
        "terms — the oil longs (MM-002, MM-011) are closed without regret, and the duration longs (MM-013) plus the "
        "steepener (MM-009, ~+175%) are the winning side, deepened by Brent breaking $80 — held, not added, ahead of "
        "the 2pm dots. Gold (MM-005) is working on the real-rates engine and is held with the hawkish-dots reversal "
        "flagged. The SPX put spread (MM-008) and the fresh vol structure (MM-020) own the framework risk that VIX "
        "16.4 is giving away. The stopped DAX/Nasdaq ratio (MM-010) is re-expressed cleaner as long RSP / short QQQ "
        "(MM-022), and the frustrated short-USDJPY (MM-007) gets a defined-risk complement (MM-021) that pays when "
        "vol returns. For the rest of June: let the steepener, gold and the front-end long carry P&L; collar the "
        "book's 25.8% Micron concentration ahead of the Fed today AND the Jun 24 print; and open no new directional "
        "macro bet on the dot-plot level before 2pm Wednesday."
    ),
    "book_pnl": {
        "note": ("Open book P&L is the equal-weight average of the marked-to-live open positions; realised is the "
                 "average of closed trades. Position-level marks are live (TradingView); the one option line "
                 "(MM-008) is a model estimate from spot.")
    },
    "idea_selection": [
        {"label": "Long vol — own the guidance-regime risk (MM-020)", "in": True,
         "text": ("VIX at 16.4 prices Warsh's first decision as a non-event and assumes the dots arrive intact. A "
                  "VIX Jul 18/24 call spread (or 1-month SPX 25-delta strangle) is cheap, defined-risk length on a "
                  "structural vol re-rating if the chair strips forward guidance. The cleanest expression today, "
                  "because it owns the variance of the framework, not the dot-plot level.")},
        {"label": "USD/JPY downside spread — the BoJ coil (MM-021)", "in": True,
         "text": ("The BoJ hiked to 1% and the yen still weakened, pinning USD/JPY at the MoF line. A 3M 158/153 put "
                  "spread owns the intervention / vol-return tail with defined premium — the convexity the frustrated "
                  "spot short (MM-007) is waiting for, without bleeding carry. Pairs with, not replaces, the spot.")},
        {"label": "Long RSP / short QQQ — the rotation RV (MM-022)", "in": True,
         "text": ("Tuesday's record-Dow/falling-Nasdaq/SOX-5.7% split is the broadening a guidance-light, oil-"
                  "disinflation Fed accelerates, and the AI-debt overhang is the tailwind to the short leg. The "
                  "cleaner heir to the stopped DAX/Nasdaq ratio — low beta to the FOMC level, high beta to the "
                  "rotation. Size on the ratio; stop -3%.")},
        {"label": "Duration longs + steepener (MM-013/009/004) — held, not added", "in": False,
         "text": ("The winning side of the disinflation impulse, deepened by Brent sub-$80. But the FOMC is the "
                  "gate — do not add size before 2pm. Respect the stops (4.35% / -10bp / 4.65%).")},
        {"label": "No new directional macro before 2pm", "in": False,
         "text": ("Warsh's first decision is the regime-defining event for the rest of Q2 — and the dots themselves "
                  "may change form. Forcing a new macro bet on the level in front of it, into the most complacent "
                  "vol of the cycle, is noise, not edge. The three fresh ideas are deliberately low-correlation to "
                  "the dot-plot number.")},
    ],
    "screen": screen,
    "screener_notes": SCREENER_NOTES,

    "vix_term": [
        {"label": "VIX9D", "value": 15.5},
        {"label": "VIX",   "value": 16.4},
        {"label": "VIX3M", "value": 18.5},
        {"label": "VIX6M", "value": 20.0},
    ],
    "yield_curve_pts": [
        {"label": "2Y",  "value": round(_g("us02y") or 4.06, 3)},
        {"label": "5Y",  "value": 4.22},
        {"label": "10Y", "value": round(_g("us10y") or 4.47, 3)},
        {"label": "30Y", "value": round(_g("us30y") or 4.97, 3)},
    ],

    "new_ideas": [
        {
            "id": "MM-2026-020", "trade": "Long VIX Jul 18/24 call spread (own the guidance-regime vol re-rating)",
            "asset_class": "Derivatives (vol)", "structure": "call spread / strangle",
            "entry": "~1.0% premium", "stop": "—", "target": "~3-4x on a vol re-rating",
            "conviction": 7,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "to mid-Jul", "min_hold_days": 0,
            "thesis": ("VIX near 16.4 prices Warsh's first FOMC as a non-event and assumes the dot plot arrives "
                       "intact. The unpriced risk is structural, not directional: a chair who has attacked forward "
                       "guidance for a decade may begin dismantling the dots today, which removes the calendar "
                       "Fed-put and re-rates realised vol higher as every print becomes its own catalyst. A VIX Jul "
                       "18/24 call spread (or a 1-month SPX 25-delta strangle) is cheap, defined-risk length on that "
                       "re-rating — the one outcome the complacent tape prices at zero."),
        },
        {
            "id": "MM-2026-021", "trade": "Buy 3M USDJPY 158/153 put spread (the BoJ coil / MoF tail)",
            "asset_class": "FX (options)", "structure": "put spread",
            "entry": "~0.8% premium", "stop": "—", "target": "~5x at 153",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
            "horizon": "3 months", "min_hold_days": 0,
            "thesis": ("The BoJ hiked to 1.00% — the highest since 1995, with Ueda absent — and the yen WEAKENED, "
                       "pinning USDJPY near 160 at the MoF intervention line because the hike was priced and vol is "
                       "crushed. The carry trade is maximally stretched against a now-tightening BoJ; a single MoF "
                       "intervention or a vol-re-rating Fed snaps it several figures lower in days. A put spread owns "
                       "that downside with defined premium and positive convexity into the vol-return catalyst the "
                       "spot short (MM-007) is waiting for — without bleeding carry."),
        },
        {
            "id": "MM-2026-022", "trade": "Long RSP (S&P equal-weight) vs short QQQ (Nasdaq-100)",
            "asset_class": "Equity RV", "structure": "cross-index ratio",
            "entry": "spot ratio", "stop": "ratio -3%", "target": "ratio +5%",
            "conviction": 6,
            "conviction_breakdown": {"gap": 2, "catalyst": 1, "positioning": 2, "confirmation": 1, "stop_quality": 1},
            "horizon": "weeks", "min_hold_days": 0,
            "thesis": ("Tuesday wrote the thesis: the Dow printed a 2nd record while the Nasdaq fell 1.15% and the "
                       "SOX dropped ~5.7% — money rotated out of the most-crowded, now AI-debt-levered semis into "
                       "the broad market. A guidance-light, oil-disinflation Fed broadens leadership beyond the "
                       "seven names that carried the index, and the AI-capex-funded-by-debt overhang (NVDA's $25B "
                       "bond) is the structural tailwind to the short leg. Long breadth, short concentration — the "
                       "cleaner heir to the stopped DAX/Nasdaq ratio, low beta to the FOMC level."),
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
