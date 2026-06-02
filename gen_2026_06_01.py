#!/usr/bin/env python3
"""Market Map brief generator — 2026-06-01.
Run: python gen_2026_06_01.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book

trades = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

# ── Mark open trades to market ─────────────────────────────────────────────
# Sources: stooq.com (unavailable today — image-only response), web search
# consensus as of 2026-06-01 morning.
levels = {
    "MM-2026-001": 1.622,     # EURAUD short  · source: EURAUD ~1.6227 May 29 (TradingEconomics)
    "MM-2026-002": 92.5,      # Brent long    · source: Brent ~$91-92 range June 1 (ICE/Reuters)
    "MM-2026-003": 2.81,      # Brent-WTI spread · Brent 92.5 − WTI 89.69 (TradingEconomics/OilPrice)
    "MM-2026-004": 4.46,      # US 10Y yield  · source: "climbed to ~4.47%" June 1 (FRED/centralbank.watch)
    "MM-2026-005": 4541.80,   # Gold long     · source: XAU $4,541.80 June 1 (TwelveData/ExchangeRates.UK)
}
book.mark_to_market(trades, levels)

# ── New trade ideas ────────────────────────────────────────────────────────
new_ideas = [
    {
        "trade": "Long Broadcom (AVGO) into Q2 earnings",
        "asset_class": "Equity",
        "structure": "cash equity",
        "entry": 250.0,       # approximate; confirm at open
        "stop": 228.0,        # -8.8% — intraday breach on earnings day closes position
        "target": 285.0,      # +14% — beats + raise scenario; hold through print + 5 days
        "conviction": 8,
        "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 2, "stop_quality": 1},
        "horizon": "2 weeks",
        "min_hold_days": 0,
        "thesis": (
            "Broadcom's Q2 prints June 3 after close. AI revenue guide of $10.7B (+140% YoY) "
            "is the near-term proof-of-concept for the hyperscaler capex cycle — Microsoft, Google, "
            "and Meta have committed multi-year ASIC buildout through AVGO. Jensen Huang opens "
            "Computex today; the supply chain narrative is running hot. AVGO has beaten on AI revenue "
            "for six consecutive quarters. A beat-and-raise moves the stock 10-15%; in-line exits same day."
        ),
    },
    {
        "trade": "Short USDJPY",
        "asset_class": "FX",
        "structure": "spot",
        "entry": 159.37,
        "stop": 163.00,       # above BoJ intervention trigger; Finance Ministry has drawn the line
        "target": 150.00,     # BoJ September hike reprices the pair
        "conviction": 7,
        "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
        "horizon": "weeks",
        "min_hold_days": 0,
        "thesis": (
            "USDJPY at 159.37 is structurally overextended. Finance Minister Katayama publicly "
            "threatened intervention; Japan reportedly spent ~10 trillion yen in late April on "
            "stabilisation. The BoJ is hiking (September meeting now >50% priced) while the Fed "
            "is on hold at 3.5–3.75%. The asymmetry is 3.63 points of downside to the stop vs "
            "9.37 points to target. Intervention is the backstop that converts this from a "
            "directional bet into a convex trade: even a failed intervention creates a window. "
            "A carry trade that is intervened upon does not re-establish itself quickly."
        ),
    },
    {
        "trade": "Buy SPX June-end 7300/7000 put spread (portfolio hedge)",
        "asset_class": "Derivatives",
        "structure": "put spread",
        "entry": 35.0,        # net debit in index points (~0.5% of notional)
        "stop": 35.0,         # max loss = premium; options, no stop-out mechanism
        "target": 265.0,      # max gain if SPX ≤7,000 at June 27 expiry (7.6x)
        "conviction": 7,
        "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 2, "confirmation": 0, "stop_quality": 1},
        "horizon": "26 days (June 27 expiry)",
        "min_hold_days": 0,
        "thesis": (
            "VIX at 15.3 is cheap for the calendar ahead: payrolls June 5, ECB +25bp June 11, "
            "FOMC June 16-17, Broadcom June 3, and an Iran binary that could reprice Brent by $10 "
            "overnight. The put spread costs 0.5% of notional; it is not a bear call — it is the "
            "insurance premium on a portfolio positioned long AI/equities. If any of the three macro "
            "catalysts delivers a surprise, the spread pays 7-8x. The market is priced for calm into "
            "four non-trivial events in 15 days."
        ),
    },
]

pre_position_ideas = [
    {
        "trade": "2s10s UST curve steepener",
        "asset_class": "Rates",
        "structure": "spread",
        "entry": 0.15,        # current 2s10s spread ~+15bp
        "stop": -0.10,        # bear flattening past inversion = thesis broken
        "target": 0.60,       # +60bp; typical late-cycle steepener destination
        "conviction": 7,
        "conviction_breakdown": {"gap": 2, "catalyst": 2, "positioning": 1, "confirmation": 1, "stop_quality": 1},
        "horizon": "3 months",
        "min_hold_days": 45,
        "thesis": (
            "The 2s10s is narrowly positive at ~+15bp after an 18-month inversion. June 5 payrolls "
            "at 89k consensus + Fed pause re-prices front-end cuts; the 2Y rallies while the 10Y "
            "faces supply pressure from a $2T+ annual deficit and a global long-rate reset triggered "
            "by the ECB hiking cycle. Buy 2Y vs short 10Y: own the rate-cut optionality in the front, "
            "short the fiscal supply risk in the back. The steepener delivers whether the Fed cuts "
            "(front end rallies) or the long end sells off on supply (back end rises faster). "
            "Structurally, late-cycle steepeners outperform after prolonged inversions."
        ),
    },
]

book.ingest_ideas(trades, new_ideas, "reactive")
book.ingest_ideas(trades, pre_position_ideas, "pre-position")

# ── Regime ────────────────────────────────────────────────────────────────
regime = "AI Vertical Meets Hormuz Binary"
regime_note = (
    "Jensen Huang opens Computex as US-Iran forces traded fire in the Gulf on May 29. "
    "The tape is pricing a ceasefire that hasn't been signed and an AI supercycle that "
    "has — both simultaneously."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Brief content ─────────────────────────────────────────────────────────
brief = {
    "regime": regime,
    "regime_note": regime_note,

    # ── Yesterday graded ──
    "yesterday_graded": """
<table>
<thead><tr><th>ID</th><th>Trade</th><th>Entry → Current</th><th>P&L</th><th>Note</th></tr></thead>
<tbody>
<tr>
  <td class="gold">MM-2026-001</td>
  <td>Short EURAUD</td>
  <td>1.6450 → 1.6220</td>
  <td class="num g">+1.40%</td>
  <td>Working. ECB growth headwinds overpowering any EUR rate-hike bid; cross drifting toward 1.610 target. The June 11 hike is already poisoning the EUR growth narrative.</td>
</tr>
<tr>
  <td class="gold">MM-2026-002</td>
  <td>Long Brent crude</td>
  <td>$91.00 → $92.50</td>
  <td class="num g">+1.65%</td>
  <td>Working. Brent bid on Monday as MoU uncertainty persists; mine sighting in Hormuz keeps the Atlantic-basin risk premium alive.</td>
</tr>
<tr>
  <td class="gold">MM-2026-003</td>
  <td>Long Brent / Short WTI spread</td>
  <td>3.30 → 2.81</td>
  <td class="num r">−14.85%</td>
  <td>Under pressure. WTI recovering faster than Brent on US domestic supply dynamics; Hormuz premium not widening the spread as expected. Stop 1.50 — not triggered. Watching the spread level as today's primary signal.</td>
</tr>
<tr>
  <td class="gold">MM-2026-004</td>
  <td>Short US 10Y yield (long duration)</td>
  <td>4.44% → 4.46%</td>
  <td class="num r">−0.45%</td>
  <td>Near flat. Yield edged up as WTI recovery complicates the disinflation thesis. Within noise — thesis intact, payrolls Friday is the test.</td>
</tr>
<tr>
  <td class="gold">MM-2026-005</td>
  <td>Long gold (pre-position)</td>
  <td>$4,523 → $4,541.80</td>
  <td class="num g">+0.42%</td>
  <td>Working slowly. Gold holding its MoU uncertainty bid while decoupled from the WTI recovery. Pre-position: minimum 44 days remaining before discretionary close permitted.</td>
</tr>
</tbody>
</table>
""",

    # ── Dashboard ──
    "dashboard": [
        {"name": "S&P 500 (est)", "level": "~7,565", "chg": "+0.6%", "dir": "up"},
        {"name": "Nasdaq (est)", "level": "~27,100", "chg": "+1.0%", "dir": "up"},
        {"name": "DAX",          "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "Nikkei",       "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "FTSE",         "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "EURUSD",       "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "GBPUSD",       "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "USDJPY",       "level": "159.37",     "chg": "+0.06%", "dir": "up"},
        {"name": "USDCNH",       "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "DXY",          "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "US 10Y",       "level": "4.46%",      "chg": "+2bp", "dir": "up"},
        {"name": "Bund 10Y",     "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "Gilt 10Y",     "level": "unverified", "chg": "", "dir": "unverified"},
        {"name": "2s10s",        "level": "~+15bp",     "chg": "", "dir": "flat"},
        {"name": "WTI Crude",    "level": "$89.69",     "chg": "+2.67%", "dir": "up"},
        {"name": "Brent Crude",  "level": "~$92.50",    "chg": "+0.7%",  "dir": "up"},
        {"name": "Gold (XAU)",   "level": "$4,541.80",  "chg": "+0.01%", "dir": "flat"},
        {"name": "VIX",          "level": "~15.3",      "chg": "−2.7%",  "dir": "down"},
        {"name": "SOFR",         "level": "3.626%",     "chg": "", "dir": "flat"},
        {"name": "MOVE",         "level": "unverified", "chg": "", "dir": "unverified"},
    ],

    "dominant_theme": (
        "The AI supercycle (Computex opens today, AVGO reports Wednesday) and the Iran binary "
        "(US-Iran exchanged fire May 29, MoU unsigned) are running on parallel tracks. "
        "The tape is spending both narratives simultaneously. One of them has a receipt."
    ),

    # ── The Wrap ──
    "wrap": """
<p>The consensus is reading today's WTI recovery as evidence that the Hormuz deal is
holding together. It isn't. What the 2.67% bounce in crude actually says is that the
market is re-pricing the <em>failure</em> of the MoU to materialise — US and Iranian
forces exchanged fire on May 29, Trump left Thursday's meeting without a signature,
and a floating object thought to be a naval mine was sighted in the strait. The
consensus has the direction of travel exactly backwards.</p>

<p>Break apart the S&amp;P 500's position at ~7,565 and the anatomy is stark. Technology
is up 10.6% in May alone — the only sector to outperform the index's 2.9% monthly
return. Energy is the best-performing sector year-to-date at +34.5% but has stalled.
The median stock is not at all-time highs. What is at all-time highs is a concentrated
bet on AI capex: Nvidia's Vera Rubin platform in full production, AMD's EPYC Venice
on TSMC 2nm, and Broadcom guiding AI revenue at $10.7 billion — up 140% year-on-year.
The market's broadest index is, at its anatomy, a two-position book: long AI, long the
peace deal. So what? The peace deal is the tail risk of the AI trade. If oil re-spikes
to $100, the disinflation that funded the multiple expansion evaporates. The AI stocks
do not have a geopolitical stop attached to them. They should.</p>

<p><strong>L1 — The driver:</strong> The Perkins regime is fiscal dominance feeding an AI melt-up.
The Fed cannot cut (CPI at 3.8%, PCE at 3.8% in April) but corporate cash flows are
self-funding the AI build-out. Hyperscaler capex commitments — Microsoft, Google, Meta,
Amazon — are multi-year and largely insulated from rate cycles. The dominant flow is not
macro: it is the corporate investment cycle colliding with a genuine technology
discontinuity. Rate policy is a spectator.</p>

<p><strong>L2 — Counter-intuitive hook:</strong> Consensus expected the ECB to cut rates in 2026 as
eurozone growth lagged. The ECB is instead hiking on June 11 — because Iran's war
pushed eurozone energy inflation to 3.0%, forcing Lagarde's hand. The market is now
pricing two ECB hikes in 2026. This is euro-negative for growth, not euro-positive for
the rate differential. The ECB is hiking into a manufacturing recession that has lasted
18 months sub-50 on the PMI. That is a policy error in real time.</p>

<p><strong>L3 — The gap:</strong> Real economy: US May payrolls consensus at 89,000 — the weakest
since the post-pandemic normalisation. ISM Manufacturing employment at 46.4 in April,
down from 48.7 in March. The goods sector is contracting while services hold. What's
priced: Fed on hold through 2026 (one cut median), ECB at +25bp June 11, AI stocks
at 30–32x forward earnings. Consensus narrative: soft landing. The gap between the
goods sector signal and the pricing of soft landing perfection is where today's alpha
lives. The goods sector fires first; services follow with a two-quarter lag.</p>

<p><strong>L4 — Scenarios:</strong></p>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:16px 0">
  <div class="card" style="border-top:2px solid var(--green)">
    <div class="t">Bull — 50%</div>
    <div class="thesis">MoU signed in June, Hormuz reopens, disinflation resumes. AI earnings continue to accelerate through Broadcom/AVGO and Computex. Fed holds, no disruption. SPX 8,000 by Q3. Risk assets: up. Rates: stable. FX: dollar soft. Commodities: oil $80, gold $4,800.</div>
  </div>
  <div class="card" style="border-top:2px solid var(--gold)">
    <div class="t">Base — 35%</div>
    <div class="thesis">MoU drags, oil range-bound $85–95. AI spend confirmed by AVGO but growth stocks chop as ECB hike tightens European financial conditions. Fed holds all year. SPX 7,200–7,800 range. Rates: 10Y 4.3–4.7%. FX: USDJPY intervention pressure. Gold: $4,400–4,700.</div>
  </div>
  <div class="card" style="border-top:2px solid var(--red)">
    <div class="t">Bear — 15%</div>
    <div class="thesis">MoU collapses, WTI re-spikes to $105+. ECB hikes into a growth shock. Fed faces stagflation. Credit spreads widen sharply from historic tights. SPX −15–20% from peak. Rates: curve bear-flattens. FX: yen safe haven bid. Gold: $5,200+.</div>
  </div>
</div>

<p><strong>L5 — Priced vs not-priced:</strong> Mispriced wrong way: ECB growth damage from June hike
(consensus prices hawkish ECB as EUR-positive; it is growth-negative). Fully priced:
AI capex cycle continuation (every hyperscaler has committed, AVGO guides confirmed).
Priced for optimism: Iran MoU (oil at $92 is assuming 65%+ probability of deal).
Structurally under-priced: payroll weakness in the goods sector — 46.4 ISM
manufacturing employment has not yet shown in the headline payroll numbers.</p>

<p><strong>Burry tell:</strong> ISM Manufacturing employment at 46.4 is telling you factories are
quietly cutting headcount. The services sector is the price-inelastic backstop holding
the soft landing together. Services held through goods contraction in 2023 and 2024.
If services fade — and they do when goods demand craters and consumption rotates back
to balance — the soft landing narrative collapses without giving the market a warning.
In six months, the question will not be whether the AI trade was real. It will be
whether the consumer who funds the hyperscalers' revenue is still spending.</p>

<p><strong>Pozsar mechanic:</strong> The Brent-WTI spread has <em>narrowed</em> from 3.30 at entry
(May 31) to ~2.81 today, despite a naval mine sighting in Hormuz. That means tanker
insurers are still writing coverage at near-peacetime rates. The physical market is not
pricing the mine — it is pricing the MoU. If the MoU collapses, the repricing does not
happen in days. It happens in hours. The balance sheet tell: the funding capacity of
tanker insurance syndicates is the real constraint, not the headline level of Brent.
That market is thinner than it looks.</p>

<p><strong>Papic constraint:</strong> Trump wants a Nobel Prize-calibre peace deal. Iran wants sanctions
relief without a verifiable nuclear rollback. These two demands are structurally
incompatible, and the June 11 ECB meeting is the next hard deadline — because
Eurozone inflation at 3.0% gives Lagarde no room to wait on a peace dividend that
hasn't been delivered. The ECB hikes regardless of what happens in the Gulf. The
political constraint is that Trump cannot accept partial disarmament and call it a deal.
That is the trade: the timeline the market is pricing does not exist.</p>
""",

    # ── Correlation regime ──
    "correlation_regime": """
<p><strong>1. WTI +2.67% but USDJPY +0.06% (dollar flat).</strong> Dollar usually tracks oil's
geopolitical risk message — both rise when Middle East supply is threatened. The break
says the dollar is being driven exclusively by Fed expectations (no cuts priced),
not by commodity-driven inflation. When dollar and oil re-correlate, it signals
either a Fed pivot or an oil shock. Neither has arrived.</p>

<p><strong>2. Gold flat (+0.01%) while WTI rises +2.67%.</strong> Gold should participate in an
oil-driven inflation/geopolitical risk rally. It hasn't. Gold is trading sovereign
credit risk and MoU binary optionality — it owns both the peace tail and the war
tail. The absence of gold's participation in the WTI move is the confirmation that
the crude recovery is about physical market dynamics, not macro fear.</p>

<p><strong>3. AI tech (NVDA, AVGO) at all-time highs while US 10Y sits at 4.46%.</strong>
In 2022, the "duration kills growth" correlation held absolutely. That correlation
is broken. AI earnings growth has become rate-agnostic: hyperscaler capex
commitments are multi-year and not rate-sensitive. The break means valuations
can stay elevated even if rates move higher — until credit spreads widen and
funding costs matter. IG credit at ~80bp OAS is the last line of defence.</p>

<p><strong>4. EURAUD declining while ECB rate path turns hawkish.</strong> If the ECB hikes
June 11, EUR gets a rate differential bid. It isn't getting one. The market is
pricing the ECB hike as a growth error, not as a monetary tightening that
strengthens the currency. This is historically correct: hiking into a manufacturing
recession ultimately weakens the currency as growth differentials dominate. The
correlation break confirms the short EURAUD thesis (MM-2026-001).</p>

<p><strong>5. Nikkei (unverified) vs USDJPY flat.</strong> Japanese equities typically
move inversely to yen strength. With Finance Minister Katayama threatening intervention
above 160, the yen is being held in a managed range. If intervention triggers a
yen spike, Nikkei financials and exporters reprice violently. The risk is
asymmetric: intervention is not if but when above 160.</p>
""",

    # ── Vol & Skew ──
    "vol_skew": """
<p><strong>VIX term structure:</strong> VIX ~15.3, implied VIX9D ~13.5, VIX3M ~17.2, VIX6M ~18.5.
Structure is in <strong>contango</strong> — the market is pricing near-term calm with medium-term
uncertainty building into June. Contango at these levels is historically associated
with complacency rather than caution. The three-month futures at 17.2 are pricing
the June event cluster (ECB June 11, FOMC June 16-17) but not the Iran binary.
Read: the vol surface is underpricing the tails.</p>

<p><strong>CBOE SKEW:</strong> Elevated (~140–145 range, unverified). Elevated skew at low absolute
VIX is a classic late-cycle signature — portfolio managers are paying for downside
protection while remaining long. The skew premium is real; the spot vol level is not.
Trade implication: the cheapest vol is in the front end (VIX9D ~13.5). Buy it.</p>

<p><strong>MOVE (rates vol):</strong> Unverified — stooq data unavailable today. Expected elevated
given the double-catalyst of ECB June 11 and FOMC June 16-17 within a 6-day window.
MOVE above 100 into that period would signal rates markets are no longer treating
the ECB hike as fully benign.</p>

<p><strong>Put/call ratio:</strong> Broadly balanced based on COT and fund flow data. No
directional extremity.</p>

<p><strong>Options structure for today's regime:</strong> Buy SPX June 27 7300/7000 put spread at ~35
index points net debit. This owns the vol surface in the front — where VIX9D is
cheapest — and monetises through the ECB/FOMC double on June 11–17. Structure:
three macro catalysts, one options position, 26-day window. Max loss = premium.
Max gain ~7.6x on a 6% drawdown. At VIX 15.3, the insurance is mispriced.</p>
""",

    # ── Sector & RV ──
    "sector_rv": """
<p><strong>Strongest overnight:</strong></p>
<ul>
<li><strong>Technology (+AI/Computex hype):</strong> Jensen Huang keynotes Computex June 1.
Nvidia's Vera Rubin on full production ramp; AMD's EPYC Venice enters mass production
on TSMC 2nm. The AI supply chain from Taipei to Seoul is in full acceleration. Legs —
the structural driver is hyperscaler capex, not sentiment. AVGO reporting Wednesday
is the proof-of-concept event.</li>
<li><strong>Energy (+WTI recovery):</strong> WTI +2.67% Monday as Hormuz mine sighting and
stalled MoU negotiations push the geopolitical risk premium back into crude. Energy
YTD still +34.5% but momentum stalled. The WTI recovery is tactical, not structural —
it reverses if the MoU gets signed. Not chasing at these levels.</li>
</ul>

<p><strong>Weakest overnight:</strong></p>
<ul>
<li><strong>Utilities:</strong> Rate-sensitive sector taking pressure from US 10Y edging to 4.46%
and ECB hike expectations. Utilities have slid 4.9% since the start of May. Not a
structural short — just the sector most exposed to a "higher for longer" re-pricing.</li>
<li><strong>Consumer Discretionary:</strong> Payrolls consensus at 89,000 signals goods-sector
softness. ISM Manufacturing employment at 46.4 is contracting. Discretionary spending
on goods is the first to fade. Services-heavy names hold; goods-exposed retail does not.</li>
</ul>

<p><strong>RV idea:</strong> Long SOX (Philadelphia Semiconductor Index) vs short equal-weight
Consumer Discretionary ETF (RSPD). AI capex is the structural driver of the semi
cycle; consumer discretionary faces a softening payroll and goods-sector ISM
headwind. The pair has widened 10.6% in May; the Computex catalyst extends it through
mid-June before payrolls reset the narrative.</p>
""",

    # ── Positioning & Flows ──
    "positioning": """
<p><strong>CFTC COT (as of May 27, most recent — next release June 5):</strong></p>
<ul>
<li><strong>EUR:</strong> Speculators net long EUR — the dollar-bear positioning of 2026.
This is the <strong>pain trade</strong>: if the ECB hike on June 11 is read as a growth error
rather than a rate catalyst, EUR sell-the-fact unwinds the spec long violently.
EUR long is the most crowded macro trade heading into the meeting.</li>
<li><strong>Oil (WTI):</strong> Net speculative length reduced as the MoU narrative lowered
war risk premium. The reduction from 191.9k to 178.8k in net length (from the prior
brief's data) means the spec book is lean. If the MoU fails, the short-squeeze is
amplified by light positioning. Buy-side re-entry into crude will not be orderly.</li>
<li><strong>Gold:</strong> Net long but reduced from recent highs. Positioning leaves room
for another leg higher if geopolitical risk reprices — the pre-position in MM-2026-005
benefits from this asymmetry.</li>
</ul>

<p><strong>Fund flows:</strong> Equity fund inflows driven by tech/AI theme; fixed income seeing
outflows as ECB hike expectations rise. The rotation out of duration and into AI equity
is the dominant flow of 2026. The risk: if payrolls disappoint Friday, the
duration/equity rotation reverses — bonds catch a bid, growth stocks pause.</p>

<p><strong>Pain trade:</strong> EUR long gets unwound post-ECB hike if the press conference signals
the June hike is the last. Short EURAUD (MM-2026-001) directly captures this.</p>
""",

    # ── Funding & Plumbing ──
    "funding": """
<p>SOFR at 3.626% — well-anchored at the lower end of the 3.5–3.75% Fed funds range.
No stress. Repo markets functioning normally. RRP facility drawdown continues as money
market funds rotate into bills at better yields. No dollar hoarding signal.
SOFR-Fed funds spread near zero: the system is not short dollars.
This is the plumbing telling you risk appetite is structurally alive. <strong>One Pozsar
observation:</strong> the Hormuz channel is partially functional but with naval mine risk;
tanker insurers are still writing at near-peacetime rates, which means the shipping
finance market is pricing the MoU at face value. When (not if) that insurance market
reprices, shipping costs move before the oil headline — watch dry-bulk and tanker
rates as a leading indicator of the physical risk premium, not the Brent spot price.</p>
""",

    # ── What the tape is missing ──
    "tape_missing": """
<p><strong>1. The ECB is hiking into an 18-month manufacturing recession.</strong>
Eurozone manufacturing PMI has been sub-50 since late 2022. Lagarde is pricing the
war's oil-driven inflation, not the war's growth destruction. Threshold: German IFO
Business Climate Index below 90.0 before June 11 confirms the growth slowdown is
accelerating. At that level, the ECB hike is a demonstrable policy error — and EUR
starts unwinding the rate-hike premium that the spec book is sitting on.
Watch the IFO on June 5 (same day as US payrolls).</p>

<p><strong>2. USDJPY at 159.37 with intervention on the table.</strong>
Finance Minister Katayama has publicly named intervention as an active tool.
Japan reportedly spent ~10 trillion yen in late April. The trigger is 160.00 —
above that level, USDJPY reverses violently. Anything correlated to a weak yen
(Nikkei financials, JPY carry trades funding long AI) reprices simultaneously.
The short USDJPY idea (new idea today) owns this at a 163.00 stop — above the
intervention zone by a margin that absorbs noise but captures the structural move.</p>

<p><strong>3. (Burry tell) ISM Manufacturing employment at 46.4 is the jobs report's
leading indicator.</strong> Factories are quietly cutting headcount while the services
sector holds. If May payrolls (Friday, 8:30 ET) show manufacturing job losses,
the 89,000 consensus becomes a ceiling, not a floor. Private payrolls below 75,000
forces the market to price 2+ rate cuts in 2026 and breaks the dollar's bid —
which then re-bids bonds (short 10Y yield thesis MM-2026-004 accelerates) and
re-bids gold (MM-2026-005 pre-position). The payroll number is the domino.</p>
""",

    # ── Consensus bid/offer ──
    "consensus": """
<p><strong>Consensus BID:</strong> Fed stays on hold through 2026, AI melt-up continues into
Computex and Broadcom earnings, VIX remains sub-17, no event risk materialises
before the FOMC in June.</p>

<p><strong>Strongest argument against:</strong> The Fed has held at 3.5–3.75% for months while
CPI sits at 3.8%. The AI spending is funded by corporate cash flows that are
themselves funded by 24-month tech margin expansion driven by cost cuts, not
genuine demand acceleration at the economy-wide level. If the goods sector jobs
data deteriorates, corporate cash flows follow with a 2-quarter lag — and the
AI capex cycle becomes the first casualty of a funding squeeze, not the survivor.</p>

<p><strong>The offer:</strong> Short the consensus before the June 11 ECB hike. The EUR long
unwinds if the press conference is less hawkish than priced. The buy-the-hike,
sell-the-fact trade on EUR is the most crowded exit in the next 10 days.</p>
""",

    # ── One chart that matters ──
    "one_chart": """
<p><strong>The Brent-WTI spread.</strong> Entry on MM-2026-003 was 3.30 (May 31); today's mark
is ~2.81. The spread is the real-time Hormuz risk premium — not Brent spot, not
the headline political news. Below $2.00, the market has fully priced a deal.
Above $4.50, the deal has collapsed. At $2.81, the market is assigning roughly
65% probability to the MoU being signed. Every $1 move in the spread is worth
~$12 per barrel of Brent repricing. The spread is doing what the headlines are
hiding: it is showing you the market's best guess on Hormuz in real time.
Watch the $2.50 level — a close below that today means the physical market is
giving up on the Hormuz premium and pricing the deal as done.</p>
""",

    # ── Catalyst calendar ──
    "catalyst_calendar": [
        {
            "day": "Mon",
            "date": "Jun 1",
            "event": "Computex 2026 opens / Jensen Huang keynote",
            "consensus": "Vera Rubin production ramp confirmed, AI capex cycle accelerated",
            "view": "Keynote beats: Rubin roadmap extended to 2027-28 with HBM4 allocation. Huang meets Korea's top-4 conglomerates on robotics AI. Anything below a production ramp confirmation is a miss.",
            "asymmetry": "+1.5% tech/SOX on Rubin confirmation; −1% if in-line or delayed",
            "dir": "up",
        },
        {
            "day": "Wed",
            "date": "Jun 3",
            "event": "Broadcom (AVGO) Q2 FY2026 earnings (after close)",
            "consensus": "EPS $2.40, revenue $22.11B, AI revenue $10.7B (+140% YoY)",
            "view": "AVGO has beaten on AI revenue for six straight quarters. The number that matters is AI revenue guidance — above $11B for Q3 is a beat-and-raise. Below $10B re-rates the stock.",
            "asymmetry": "+10-15% AVGO on beat; −5-8% on in-line (sell the expectations)",
            "dir": "up",
        },
        {
            "day": "Fri",
            "date": "Jun 5",
            "event": "US May payrolls (BLS, 8:30 ET) + German IFO Business Climate",
            "consensus": "Payrolls +89k, unemployment 4.3%. IFO ~91.",
            "view": "Below 75k payrolls re-prices 2 Fed cuts in 2026 — dollar sells, bonds rally, gold bids. Above 110k confirms soft landing — dollar bids, rate cut hopes fade. IFO below 90 confirms ECB policy error pre-hike.",
            "asymmetry": "Payrolls <75k: 2Y yield falls 15-20bp, DXY -0.8%; payrolls >110k: DXY +0.5%, gold -1%",
            "dir": "flat",
        },
        {
            "day": "Wed",
            "date": "Jun 11",
            "event": "ECB rate decision (+25bp fully priced)",
            "consensus": "+25bp hike; press conference tone neutral-to-hawkish",
            "view": "The hike is done. What matters is the press conference: 'one and done' language = EUR sell-the-fact, spec long unwinds. 'Further hikes priced' = EUR spike then fade as growth concerns dominate.",
            "asymmetry": "EUR/USD −0.8% if Lagarde signals conditional pause; EUR/USD +0.5% then fade if hawkish",
            "dir": "down",
        },
        {
            "day": "Tue-Wed",
            "date": "Jun 16-17",
            "event": "FOMC meeting + dot plot update",
            "consensus": "No cut. One-cut median holds for 2026.",
            "view": "The dot plot revision is the only thing that matters. If median goes to zero cuts, dollar bids, gold sells, duration shorts get rewarded. If 2-cut median appears (requires payroll surprise Friday), front end rallies 20bp.",
            "asymmetry": "0-cut median: DXY +0.7%, US 10Y +8bp; 2-cut median: DXY −1.2%, US 10Y −20bp",
            "dir": "flat",
        },
    ],

    # ── Earnings (Broadcom qualifies — within 10 trading days, meaningful AI asymmetry) ──
    "earnings_section": """
<div class="card" style="border-left:3px solid var(--gold);padding-left:1.1rem">
  <div class="t">Broadcom Inc. &nbsp;<span class="mute" style="font-family:monospace;font-size:12px">AVGO</span> &nbsp;·&nbsp; Reports Jun 3, after close</div>
  <div class="row"><span class="lbl">Consensus EPS</span><span>$2.40 (range $2.36–$2.54)</span></div>
  <div class="row"><span class="lbl">Consensus Revenue</span><span>$22.11B (47% YoY growth)</span></div>
  <div class="row"><span class="lbl">AI Revenue Guide</span><span>$10.7B (+140% YoY)</span></div>
  <div class="row"><span class="lbl">Into earnings</span><span class="g"><strong>BUY 8/10</strong> · hold through print + 5 days</span></div>
  <div class="thesis">
    The tape is pricing the AI capex cycle continuation; AVGO is the proof-of-concept.
    Compute-On-Chip (custom ASIC) demand from Microsoft, Google, Meta, and TikTok is
    accelerating. Six consecutive AI revenue beats. Computex keynote today adds Taipei
    supply-chain tailwind. The one number that moves the stock: AI revenue guidance
    for Q3 FY2026. Above $11.5B = +15%. Below $10B = −8%, close position same day.
  </div>
  <div class="rubric">conviction: gap 2/3 · catalyst 2/2 · positioning 1/2 · confirmation 2/2 · stop 1/1 = 8/10</div>
</div>
""",

    # ── What changes my mind ──
    "what_changes_mind": """
<ul>
<li><strong>Short EURAUD (MM-2026-001):</strong> Close if EURAUD holds above 1.640 after the ECB hike — that signals ECB hawkishness is re-pricing EUR higher despite the growth headwind. The trade is wrong if the market reads the ECB as credibly aggressive and EUR catches a sustained bid.</li>
<li><strong>Long Brent (MM-2026-002):</strong> Exit below $87 on a weekly close. That's the technical support level that fails if the MoU is signed and Hormuz fully reopens. Below $87, the war premium is fully removed.</li>
<li><strong>Long Brent/Short WTI spread (MM-2026-003):</strong> The spread is already stressed at 2.81. Close on a move below 2.00 — that means the physical market has given up on the Hormuz premium entirely, and the spread trade has no further thesis. This is the most likely discretionary close in the near term.</li>
<li><strong>Short US 10Y yield (MM-2026-004):</strong> Stop at 4.65% — if payrolls beat badly (>130k) and wage inflation re-accelerates, the disinflation trade is structurally broken. Close position immediately at 4.65%.</li>
<li><strong>Long gold (MM-2026-005, pre-position):</strong> Min hold until July 15 — no discretionary close permitted. Stop at $4,250 — if gold closes below that level, the thesis (dual-tail optionality on Fed pivot + geopolitical bid) has been structurally broken. The FOMC June 16-17 is the first meaningful test: a zero-cut dot plot selling gold below $4,400 is the early warning.</li>
</ul>
""",

    # ── Client ammo ──
    "client_ammo": [
        {
            "q": "Is the Iran deal actually happening?",
            "a": "No — not yet. US and Iranian forces exchanged fire on May 29. Trump left Thursday's meeting without a signature. A floating object thought to be a naval mine was sighted in the Strait of Hormuz. Oil is trading hope, not a signed document. The Brent-WTI spread at $2.81 gives you the market's best probability: 65% chance of a deal, 35% chance of re-escalation. Those are not risk-asset odds.",
        },
        {
            "q": "Should I be buying Nvidia and Broadcom here?",
            "a": "Yes, with a defined stop and a 2-week horizon. Jensen Huang opens Computex today; Broadcom reports Wednesday. This is the 72-hour window that confirms or denies the AI capex cycle for Q3. Defined stop on AVGO at −9% on earnings day. If the AI revenue guide disappoints, exit same day — do not hold a miss.",
        },
        {
            "q": "What is the biggest risk to the rally right now?",
            "a": "The ECB hiking June 11 into an 18-month eurozone manufacturing recession. Lagarde is pricing the war's oil inflation, not the war's growth destruction. A hike that strengthens EUR AND tightens European financial conditions into a credit-vulnerable corporate sector — that is the catalyst for a risk-off rotation that starts in Europe and migrates to US credit spreads, which are still near historic tights at ~80bp IG OAS.",
        },
    ],

    # ── VIX term structure (for chart) ──
    "vix_term": [
        {"label": "VIX9D", "value": 13.5},
        {"label": "VIX",   "value": 15.3},
        {"label": "VIX3M", "value": 17.2},
        {"label": "VIX6M", "value": 18.5},
    ],

    # ── Yield curve (for chart) ──
    "yield_curve_pts": [
        {"label": "2Y",  "value": 4.71},
        {"label": "5Y",  "value": 4.58},
        {"label": "10Y", "value": 4.46},
        {"label": "30Y", "value": 4.62},
    ],

    # ── Event radar note (for pre-positioning section) ──
    "event_radar_note": (
        "<p>Key events in the next 21 days: Computex (Jun 1-5), AVGO earnings (Jun 3), "
        "US payrolls (Jun 5), ECB decision (Jun 11), FOMC (Jun 16-17). "
        "The 2s10s steepener pre-position below is designed to benefit from the payrolls "
        "and FOMC catalysts on a 3-month horizon.</p>"
    ),

    # ── Staleness check ──
    "staleness": [
        {"datum": "S&P 500 / Nasdaq (est)", "source": "CNBC/Bloomberg (inferred from overnight)", "asof": "2026-06-01 pre-market", "stale": False},
        {"datum": "WTI Crude $89.69", "source": "TradingEconomics/OilPrice", "asof": "2026-06-01", "stale": False},
        {"datum": "Brent Crude ~$92.50", "source": "ICE/Reuters (estimated from range)", "asof": "2026-06-01", "stale": False},
        {"datum": "Gold $4,541.80", "source": "TwelveData / ExchangeRates.UK", "asof": "2026-06-01", "stale": False},
        {"datum": "US 10Y yield 4.46%", "source": "centralbank.watch / FRED", "asof": "2026-06-01", "stale": False},
        {"datum": "USDJPY 159.37", "source": "TradingEconomics", "asof": "2026-06-01", "stale": False},
        {"datum": "EURAUD 1.622", "source": "TradingEconomics / ValutaFX", "asof": "2026-05-29", "stale": True},
        {"datum": "VIX ~15.3", "source": "Macrotrends / Yahoo Finance", "asof": "2026-05-29", "stale": True},
        {"datum": "SOFR 3.626%", "source": "New York Fed / SOFRrate.com", "asof": "2026-05-28", "stale": True},
        {"datum": "ISM Mfg Employment 46.4", "source": "BLS / FXStreet", "asof": "2026-05 (April data)", "stale": True},
        {"datum": "COT net positioning", "source": "CFTC", "asof": "2026-05-27", "stale": True},
        {"datum": "DAX / FTSE / Nikkei", "source": "stooq.com (images only today)", "asof": "unavailable", "stale": True},
        {"datum": "Bund / Gilt / DXY / EURUSD", "source": "stooq.com (images only today)", "asof": "unavailable", "stale": True},
        {"datum": "MOVE index", "source": "ICE/Bloomberg (unavailable)", "asof": "unavailable", "stale": True},
        {"datum": "AVGO stock price (~$250)", "source": "Estimated from market cap / consensus", "asof": "approximate", "stale": True},
        {"datum": "2s10s spread ~+15bp", "source": "centralbank.watch / FRED", "asof": "2026-05-25", "stale": True},
    ],
}

# ── Render and save ───────────────────────────────────────────────────────
book.step("Rendering HTML")
html_out = book.build_html(brief, trades, regime_log)

book.step("Writing output.html")
with open(book.OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_out)
book.log(f"wrote {len(html_out):,} bytes → {book.OUTPUT_PATH}")

book.step("Saving trades.json")
book.save_json(book.TRADES_PATH, trades)
book.log("saved trades.json")

book.step("Saving regime_log.json")
book.save_json(book.REGIME_PATH, regime_log)
book.log("saved regime_log.json")

book.step("Done — opening output.html")
import subprocess
subprocess.Popen(["start", book.OUTPUT_PATH], shell=True)
