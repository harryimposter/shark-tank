#!/usr/bin/env python3
"""Market Map brief generator — 2026-06-08.
Key events since June 1: May NFP +172k (2× 85k consensus), AVGO Q2 beat but
Q3 AI guide missed buy-side ($16B vs $17.2B), Israel struck Iran defence sites,
US hit Iranian radar, Iran fired at Kuwait/Bahrain. Four new trades opened.
Run: python gen_2026_06_08.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book
import shark_format

trades     = book.load_trades()
regime_log = book.load_json(book.REGIME_PATH, [])

# ── Regime ─────────────────────────────────────────────────────────────────
regime = "Payrolls Shock Meets Hormuz Fire"
regime_note = (
    "May NFP +172k (2x the 85k consensus) re-priced a Fed hike and de-rated the AI multiple "
    "in a single session. Israel struck Iran's defence systems over the weekend; US hit Iranian "
    "radar sites; Iran fired missiles at Kuwait and Bahrain. Brent gapped to $96. The tape is "
    "repositioning, not recovering."
)
regime_log = book.update_regime_log(regime_log, regime, regime_note)

# ── Extract new trades opened today (already in trades.json) ───────────────
new_today_ids    = {"MM-2026-010", "MM-2026-011", "MM-2026-012"}
prepos_today_ids = {"MM-2026-013"}
new_ideas_cards  = [t for t in trades["open"] if t["id"] in new_today_ids]
prepos_cards     = [t for t in trades["open"] if t["id"] in prepos_today_ids]

# ── Brief ──────────────────────────────────────────────────────────────────
brief = {
    "regime":      regime,
    "regime_note": regime_note,

    # ── Week graded (June 1 -> June 8) ────────────────────────────────────
    "yesterday_graded": """
<table>
<thead><tr><th>ID</th><th>Trade</th><th>Entry &rarr; Current</th><th>P&amp;L</th><th>Note</th></tr></thead>
<tbody>
<tr>
  <td class="r">MM-2026-001</td>
  <td>Short EURAUD</td>
  <td>1.6450 &rarr; 1.648</td>
  <td class="num r">&minus;0.18%</td>
  <td>Working against. ECB June 11 hike priced at 99% lifted EUR; AUD held on iron ore. Stop 1.662 &mdash; 14bp away. Thesis intact: the hike will be a growth error and EUR sells the fact post-press conference.</td>
</tr>
<tr>
  <td class="g">MM-2026-002</td>
  <td>Long Brent crude</td>
  <td>$91.00 &rarr; $96.05</td>
  <td class="num g">+5.55%</td>
  <td>Working. Israel struck western/central Iranian defence sites; US hit Iranian radar; Iran fired at Kuwait and Bahrain. Brent gapped +4%+ Monday. MoU deadlocked on $24bn frozen assets. Target $104 intact.</td>
</tr>
<tr>
  <td class="r">MM-2026-003</td>
  <td>Long Brent / Short WTI spread</td>
  <td>3.30 &rarr; 2.38</td>
  <td class="num r">&minus;27.88%</td>
  <td>Under pressure. WTI caught up to Brent as US domestic supply rebounded; spread compressed from 2.81 to 2.38. Stop 1.50 not triggered. Below $2.00 = discretionary close. Highest-risk open position; watching daily.</td>
</tr>
<tr>
  <td class="r">MM-2026-004</td>
  <td>Short US 10Y yield</td>
  <td>4.44% &rarr; 4.544%</td>
  <td class="num r">&minus;2.34%</td>
  <td>Payrolls +172k drove 10Y to 4.57% intraday Friday. Stop at 4.65% &mdash; only 10bp away. CPI Wednesday and dot plot June 17 are the two remaining catalysts. Do not add. Survival mode.</td>
</tr>
<tr>
  <td class="r">MM-2026-005</td>
  <td>Long gold (pre-position)</td>
  <td>$4,523 &rarr; $4,350</td>
  <td class="num r">&minus;3.82%</td>
  <td>Payrolls drove DXY to ~100.5 and re-priced a hike &mdash; both headwinds for gold. Stop $4,250 &mdash; $100 of room. Min hold to July 15; no discretionary close. Dot plot June 17 is gold's catalyst, not the geopolitical headline.</td>
</tr>
<tr>
  <td class="r">&#x26D4; MM-2026-006</td>
  <td>Long AVGO (STOPPED)</td>
  <td>$250.00 &rarr; $216.00</td>
  <td class="num r">&minus;13.60%</td>
  <td>STOPPED June 8. Q2 beat consensus (AI $10.8B vs $10.7B est) but Q3 AI guide $16.0B missed buy-side $17.2B &mdash; the number that mattered at 41x. Stock fell 16% afterhours June 3; payrolls tech selloff Friday finished it. Stop $228 triggered. Days held: 7.</td>
</tr>
<tr>
  <td class="r">MM-2026-007</td>
  <td>Short USDJPY</td>
  <td>159.37 &rarr; 160.32</td>
  <td class="num r">&minus;0.60%</td>
  <td>Payrolls dollar strength pushed USDJPY above 160 &mdash; inside the intervention trigger. Finance Ministry Katayama watching. Stop 163.00. When intervention fires: 3-5% in hours.</td>
</tr>
<tr>
  <td class="g">MM-2026-008</td>
  <td>SPX Jun-27 7300/7000 put spread</td>
  <td>35 &rarr; 80 pts</td>
  <td class="num g">+128.57%</td>
  <td>Best performer. Nasdaq &minus;4.2% Friday + Phil Sox &minus;6% tripled the insurance. ECB, CPI, FOMC all still inside the 26-day window. Hold through the event calendar.</td>
</tr>
<tr>
  <td class="g">MM-2026-009</td>
  <td>2s10s UST steepener (pre-pos)</td>
  <td>+15bp &rarr; +38.2bp</td>
  <td class="num g">+154.67%</td>
  <td>Best structural position. Payrolls drove 2Y +10bp (hike repricing) while 10Y rose less &mdash; curve steepened 23bp in 5 days. Min hold from June 1. Target +60bp. Thesis on track.</td>
</tr>
</tbody>
</table>
""",

    # ── Dashboard ──────────────────────────────────────────────────────────
    "dashboard": [
        {"name": "S&P 500",      "level": "~7,427",    "chg": "+0.8%",  "dir": "up"},
        {"name": "Nasdaq 100",   "level": "~26,500",   "chg": "+1.5%",  "dir": "up"},
        {"name": "DAX",          "level": "~24,917",   "chg": "-0.75%", "dir": "down"},
        {"name": "Nikkei 225",   "level": "64,024",    "chg": "-3.85%", "dir": "down"},
        {"name": "FTSE 100",     "level": "~10,416",   "chg": "+0.07%", "dir": "up"},
        {"name": "EURUSD",       "level": "1.1536",    "chg": "-0.55%", "dir": "down"},
        {"name": "GBPUSD",       "level": "unverified","chg": "",       "dir": "unverified"},
        {"name": "USDJPY",       "level": "160.32",    "chg": "+0.59%", "dir": "up"},
        {"name": "USDCNH",       "level": "unverified","chg": "",       "dir": "unverified"},
        {"name": "DXY",          "level": "~100.5",    "chg": "+0.4%",  "dir": "up"},
        {"name": "US 10Y",       "level": "4.544%",    "chg": "+8bp",   "dir": "up"},
        {"name": "US 2Y",        "level": "4.162%",    "chg": "+10bp",  "dir": "up"},
        {"name": "Bund 10Y",     "level": "unverified","chg": "",       "dir": "unverified"},
        {"name": "2s10s",        "level": "+38.2bp",   "chg": "+23bp wk","dir": "up"},
        {"name": "WTI Crude",    "level": "$93.67",    "chg": "+4.0%",  "dir": "up"},
        {"name": "Brent Crude",  "level": "$96.05",    "chg": "+4.1%",  "dir": "up"},
        {"name": "Gold (XAU)",   "level": "$4,350",    "chg": "-0.5%",  "dir": "down"},
        {"name": "VIX",          "level": "18.80",     "chg": "-12.8%", "dir": "down"},
        {"name": "SOFR",         "level": "~3.62%",    "chg": "",       "dir": "flat"},
        {"name": "MOVE",         "level": "unverified","chg": "",       "dir": "unverified"},
    ],

    "dominant_theme": (
        "Payrolls +172k shattered the rate-cut narrative and de-rated the AI multiple "
        "simultaneously. AVGO's Q3 guide ($16B vs $17.2B buy-side) confirmed the deceleration. "
        "Then Israel hit Iran. The market that opened last Monday is not the market that opens today."
    ),

    # ── The Wrap ───────────────────────────────────────────────────────────
    "wrap": """
<p>Three things happened in 96 hours that redrew the map. On Wednesday June 3, Broadcom proved
the AI cycle is real: $22.2B in revenue, $10.8B of AI semiconductor income, $16B guided for Q3.
On Friday June 5, payrolls printed 172,000 &mdash; double the 85,000 consensus &mdash; and the same market
that cheered AVGO's beat sold every name with an AI multiple attached. And over the weekend,
Israel struck western and central Iranian defence systems while the US hit Iranian radar sites
and Iran fired missiles at Kuwait and Bahrain. That is not an escalation calendar. It is the
absence of a de-escalation one.</p>

<p>Break apart what happened to AVGO and the anatomy is instructive. The stock beat every consensus
estimate &mdash; but the buy side needed $17.2 billion in Q3 AI revenue guidance to justify 41&times;
forward earnings. AVGO guided $16.0 billion. The guide was the 93rd percentile of any company's AI
revenue guidance in history. The market priced the 100th. That gap &mdash; between what was delivered
and what was needed &mdash; explains the 16% afterhours drop. The thesis is not broken. The multiple was.
There is a difference, and it determines when and how to re-enter.</p>

<p><strong>L1 &mdash; The driver:</strong> The payrolls shock restructured both halves of the macro consensus.
At 172k vs 85k expected, markets repriced 57% probability of zero cuts in 2026, up from below 50%
before the data. The Fed holds at 3.5&ndash;3.75% in June (99.2% priced) but September and December
are now genuinely live for a hike, not a cut. That is not a marginal revision. It reprices every
duration position and every high-multiple equity simultaneously.</p>

<p><strong>L2 &mdash; Counter-intuitive hook:</strong> Gold is down while oil is up. The classical geopolitical
risk playbook says buy both when missiles are in the air. Gold fell to $4,350 while Brent rallied to $96.
The divergence is exact: gold is pricing real rates (higher on payrolls repricing), not war premium.
Oil is pricing physical supply disruption. Two different primary drivers in two different assets on
the same headline. Gold's catalyst is not the Strait of Hormuz. It is the June 17 dot plot.</p>

<p><strong>L3 &mdash; The gap:</strong> AVGO guided $16B vs $17.2B buy-side. At 41&times; forward earnings,
that 7.5% guide miss is the first evidence that the hyperscaler capex cycle has shifted from
open-ended demand to budgeted allocation. Google, Anthropic, OpenAI, and Meta are now telling AVGO
what they will deploy quarter by quarter &mdash; not what they need. That shift from demand-pull to
supply-allocation is what the tape is beginning to price, even if Q2 was a beat on every metric.</p>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:16px 0">
  <div class="card" style="border-top:2px solid var(--green)">
    <div class="t">Bull &mdash; 40%</div>
    <div class="thesis">ECB hikes Thursday, signals pause. FOMC dot plot holds at one cut.
    Iran stays air-only &mdash; no Hormuz closure. Equities recover; AI names re-rate as $16B Q3
    delivery proves the cycle is intact. SPX 7,700 by July.</div>
  </div>
  <div class="card" style="border-top:2px solid var(--gold)">
    <div class="t">Base &mdash; 40%</div>
    <div class="thesis">ECB sounds hawkish, dot plot goes to zero cuts. EUR rallies into ECB
    then fades on stagflation read. AI multiple stays compressed. Brent $90&ndash;100 on Hormuz
    standoff. SPX 7,000&ndash;7,500 chop. 2s10s steepens further to +55bp.</div>
  </div>
  <div class="card" style="border-top:2px solid var(--red)">
    <div class="t">Bear &mdash; 20%</div>
    <div class="thesis">Hormuz physical disruption confirmed (mine or tanker hit). FOMC signals
    hike. CPI above 4%. Credit cracks from 80bp IG OAS. Tech &minus;15%.
    USDJPY intervention unwinds yen carry globally. Oil $110+.</div>
  </div>
</div>

<p><strong>Burry tell:</strong> The Brent-WTI spread compressed from $3.30 to $2.38 even as Brent
rallied to $96. WTI caught up faster &mdash; US domestic supply at Cushing was unaffected by the
Hormuz exchanges. The spread should have <em>widened</em> on an escalation specifically targeting
the strait. It narrowed. The physical market is still not pricing Hormuz closure as probable &mdash;
tanker insurers still write coverage at near-peacetime rates. In six months, the question will be
whether that was the trade of the year (spread widens dramatically on confirmed closure) or the
correct read (air strikes, no sea denial). The tell is the $2.00 level: below that, the market
has priced the deal. Above $3.00, physical disruption is beginning to arrive before the headline.</p>

<p><strong>Pozsar mechanic:</strong> The 2Y at 4.16% is pricing a hike the Fed does not deliver in June
but might in September. The spread between the 2Y implied terminal rate (~4.3%) and SOFR (3.62%)
is 68bp &mdash; the widest shadow-banking refinancing spread of 2026. Every corporate that issued
floating-rate debt in 2023&ndash;24 assuming cuts faces higher marginal costs than the issuance model
assumed. IG OAS at 80bp is priced for soft landing perfection. The payrolls print bought approximately
one FOMC meeting before that credit repricing begins. Watch September &mdash; if the dot plot June 17
moves the terminal rate higher, credit starts moving in July.</p>

<p><strong>Papic constraint:</strong> The ECB hike Thursday is politically locked &mdash; Lagarde cannot
pause with eurozone inflation at 3.2% and Germany's election cycle demanding anti-inflation credibility.
She hikes. But the press conference language on future meetings is where the policy error is authored:
if she pre-commits to further hikes, EUR catches a brief bid then fades as growth damage from
hiking into an 18-month manufacturing recession compounds. The trade is not the hike itself.
It is the verb tense in the press conference. Short EURUSD (MM-2026-012) is positioned for the
"data-dependent pause" that follows the June hike.</p>
""",

    # ── Correlation regime ──────────────────────────────────────────────────
    "correlation_regime": """
<p><strong>1. Brent +4% while Gold &minus;0.5% &mdash; geopolitical premium splits by asset class.</strong>
Missiles in the air over the weekend should have driven both higher. Gold fell on DXY
strengthening from payrolls; oil rallied on physical supply fear. The split is diagnostic:
gold prices real rates; oil prices physical flow disruption. Do not conflate the two theses &mdash;
they have different catalysts and different resolution timelines.</p>

<p><strong>2. VIX &minus;12.8% Monday as S&amp;P recovers, but Nikkei &minus;3.85% &mdash; selective optimism.</strong>
US large-cap recovered; Asian semiconductor names did not. Phil Sox &minus;6% Friday sent a signal
to Japan's tech exporters that has not been reversed. The 'VIX is falling' narrative understates
the geographic dispersion of the risk repricing. The recovery is exclusively US large-cap. It has
not been validated globally.</p>

<p><strong>3. 2s10s steepened +23bp in 5 days &mdash; fastest steepening of 2026.</strong>
2Y rose 10bp on hike repricing; 10Y rose less, capped by flight-to-quality from Asia's selloff.
The curve tells two stories: the Fed will be tighter than priced (2Y up), but growth is fragile
enough to bid long duration (10Y constrained). That is not a healthy steepener &mdash; it is a
stagflation premium entering the short end. MM-2026-009 is the structural beneficiary.</p>

<p><strong>4. DAX +0.2% vs Nasdaq &minus;4.2% on Friday &mdash; AI multiple compressed, European
financials immune.</strong>
Friday was a clean test. The same payrolls print that caused AI de-rating left European
financials untouched. No AI capex multiple to give back; ECB hiking is margin-positive for
European banks. MM-2026-010 (Long DAX vs short Nasdaq) is a bet that this structural
composition divergence has legs beyond a single session.</p>
""",

    # ── Vol & Skew ─────────────────────────────────────────────────────────
    "vol_skew": """
<p><strong>VIX term structure &mdash; moderate contango, recovering from Friday spike to ~21.6:</strong>
VIX9D ~15.5 &middot; VIX 18.80 &middot; VIX3M ~20.0 &middot; VIX6M ~21.5.
The structure is flatter than pre-payrolls contango &mdash; front-end risk is not fully priced out.
Three catalysts remain in the window: CPI June 10, ECB June 11, FOMC June 16&ndash;17.
The options market is not calling an all-clear; it is taking a breath.</p>

<p><strong>SPX put spread (MM-2026-008) &mdash; up 128%, decision point approaching:</strong>
Friday's Nasdaq &minus;4.2% moved the spread from 35 to 80 pts. With three events remaining,
the question is hold vs partial profit. Case for holding: CPI above 4% Wednesday + hawkish
dot plot = second selloff leg. Case for trimming: VIX at 18.80 is elevated but recovering;
a sustained equity rally compresses the spread. Trim to half if SPX recovers above 7,500
before Wednesday CPI &mdash; take the gain on half, keep the FOMC tail exposure on the rest.</p>

<p><strong>MOVE (rates vol) &mdash; unverified but structurally elevated expected:</strong>
Fed hike repricing on payrolls + ECB binary = MOVE should be above 120. If confirmed above that
level, rates markets are signalling June 11 and June 17 are binary events. MOVE above 130
is the warning before credit spreads begin to move.</p>
""",

    # ── Sector & RV ────────────────────────────────────────────────────────
    "sector_rv": """
<p><strong>Strongest Monday:</strong></p>
<ul>
<li><strong>Energy (+4%+):</strong> Brent $96, WTI $94 as Israel-Iran exchanges drove the supply
premium the MoU hope trade had removed. MM-2026-002 (Long Brent) the clearest winner of the week
at +5.55%. Iran missiles at Kuwait and Bahrain widened the geographic risk &mdash; no longer a
Hormuz-only story. MM-2026-011 (Brent $100/$115 call spread) bought today to own the tail.</li>
<li><strong>European Financials (DAX selective):</strong> ECB hiking Thursday is net-interest-income
positive for European banks &mdash; NII expands with each 25bp. No AI multiple to give back.
MM-2026-010 (Long DAX vs short Nasdaq) captures the structural composition difference.</li>
</ul>

<p><strong>Weakest:</strong></p>
<ul>
<li><strong>AI Semiconductors (Phil Sox &minus;6% Friday, partial recovery Monday):</strong>
AVGO &minus;16% afterhours, SOX &minus;6% on payrolls Friday. Partial Monday bounce.
The AI multiple is re-rating &mdash; not collapsing. The capex cycle is intact; AVGO's $16B guide
is historically exceptional. But at 41&times; forward earnings, "exceptional but below buy-side"
is insufficient. Re-entry: AVGO below $220 structurally interesting when multiple normalises to 30&ndash;32&times;.</li>
<li><strong>Japan (Nikkei &minus;3.85%):</strong> Dual headwind &mdash; AI semiconductor contagion from SOX
and USDJPY above 160 triggering MoF intervention watch. Short USDJPY (MM-2026-007) above the
stated intervention trigger zone.</li>
</ul>

<p><strong>RV &mdash; Long DAX / Short Nasdaq (MM-2026-010):</strong>
Entry ratio 0.9722 on June 8. Friday: DAX +0.2% vs Nasdaq &minus;4.2%. ECB hiking is margin-positive
for European banks; Nasdaq AI concentration faces multiple compression. This is an index
composition trade, not a sentiment one &mdash; structural legs beyond the single session.</p>
""",

    # ── Positioning & Flows ────────────────────────────────────────────────
    "positioning": """
<p><strong>CFTC COT (June 3 release, June 1 data &mdash; most recent available):</strong></p>
<ul>
<li><strong>Oil:</strong> Large spec net at &minus;9.2k (nearly flat). After Israel-Iran strikes,
there is almost no spec long to slow a new escalation headline &mdash; momentum buyers drive the
next leg vertically. MM-2026-002 and MM-2026-011 own the squeeze fuel.</li>
<li><strong>Gold:</strong> Spec longs at 154.3k (down from 159.8k before payrolls). Post-payrolls
selling has likely reduced this further. Lighter positioning is constructive for the next leg
if the dot plot delivers a dovish surprise. MM-2026-005 holds to July 15.</li>
<li><strong>EUR:</strong> Speculators net long into the ECB hike. Thursday is the pain trade exit
&mdash; if Lagarde signals "data-dependent pause," the spec long unwinds aggressively.
MM-2026-012 (Short EURUSD at 1.16) is positioned for exactly that exit.</li>
</ul>

<p><strong>Post-payrolls fund flows:</strong> AI equity outflows Thursday&ndash;Friday as AVGO's drop
spread to the sector. Short-duration fixed income inflows as the 2Y repriced the hike. The rotation
was from AI multiples into cash and short duration &mdash; not out of equities entirely. DXY above 100
tells you the dollar flow is real. Watch for CPI Wednesday to determine reversal or continuation.</p>
""",

    # ── Funding & Plumbing ─────────────────────────────────────────────────
    "funding": """
<p>SOFR ~3.62% &mdash; unchanged. Repo markets functioning normally. No dollar hoarding signal.
The system is not stressed despite the equity selloff and Hormuz escalation.
<strong>Pozsar mechanic:</strong> The gap between the 2Y implied terminal rate (~4.3%) and SOFR
(3.62%) is 68bp &mdash; the widest shadow-banking refinancing spread of 2026. Every corporate
that issued floating-rate debt in 2023&ndash;24 assuming cuts faces higher marginal funding costs
than the issuance model assumed. IG credit at 80bp OAS is priced for soft landing perfection.
The payrolls print bought approximately one FOMC meeting before the credit repricing begins.
Watch IG OAS for the first move &mdash; that is where the balance sheet constraint appears before
it appears in equities.</p>
""",

    # ── What the tape is missing ────────────────────────────────────────────
    "tape_missing": """
<p><strong>1. AVGO's $16B Q3 AI guide is exceptional by any historical standard &mdash;
and the market punished it.</strong>
The shift from "beat every metric" to "missed the buy-side extrapolation" is the most
important signal in the AI trade. Google, Anthropic, OpenAI, and Meta are now telling
AVGO what they will deploy quarter by quarter. That shift &mdash; from demand-pull to
supply-allocation &mdash; is the structural change the tape is beginning to price.
In six months, the question will be whether AI semiconductor names trade like enterprise
software (budgeted quarterly cycles) or secular growth (open-ended TAM). That re-rating,
if it arrives, compresses multiples from 41&times; to 25&times;.</p>

<p><strong>2. (Burry tell) The Nikkei fell 3.85% &mdash; its largest single-day drop since April &mdash;
while USDJPY sits above 160, the line Finance Minister Katayama drew explicitly.</strong>
Japan's Finance Ministry spent ~10 trillion yen in late April to defend 155. The yen
carry trade that funds long AI equities is now challenged on both legs simultaneously:
the AI multiple is compressing and yen shorts face violent intervention. When Japan
intervenes above 163, it is not just USDJPY that moves &mdash; it is every global carry-funded
equity position that unwinds in the same session. Short USDJPY (MM-2026-007) owns this
convexity with a 163 stop.</p>

<p><strong>3. The Brent-WTI spread compression signals the physical market still does not
believe in Hormuz closure &mdash; even after live missile exchanges.</strong>
Spread at $2.38 with Brent at $96 means zero Hormuz closure premium in the physical
differential. If tanker insurers start excluding Hormuz from coverage, the WTI-Brent spread
widens violently &mdash; Atlantic-basin crude (Brent) becomes harder to deliver while Cushing
(WTI) stays accessible. That repricing arrives in tanker insurance before it arrives in
Brent spot. Watch MM-2026-003's spread above $3.00 as the signal that physical disruption
has begun to price before the headline arrives.</p>
""",

    # ── Consensus bid/offer ─────────────────────────────────────────────────
    "consensus": """
<p><strong>Consensus BID:</strong> Equity recovery continues Monday &mdash; AVGO's Q2 beat overrides
the Q3 guide miss on reflection. ECB hike is benign (fully priced). FOMC dot plot holds at
one cut. Iran stays air-only. Tech names re-rate back to pre-payrolls within two weeks.</p>

<p><strong>Strongest argument against &mdash; the OFFER:</strong> CPI Wednesday. May CPI above 4%
is possible given energy's contribution to April's 3.8% reading and WTI now $5 higher than April.
If CPI lands above 4%, the payrolls re-pricing gets a second confirmation &mdash; the 2Y breaks
above 4.35%, gold tests the $4,250 stop, and the dot plot is live for zero cuts plus hike language.
At that point, every position priced for soft landing (AI at 30&ndash;41&times;, IG at 80bp, gold under
$4,500) faces simultaneous revision. The CPI number Wednesday is the binary that settles whether
last Friday was the repricing or just the opening act. Given WTI was $89 for April's CPI and is
$94 today, that is not a guaranteed outcome.</p>
""",

    # ── One chart that matters ──────────────────────────────────────────────
    "one_chart": """
<p><strong>The 2-year Treasury yield at 4.162%.</strong>
The 2Y is at its highest level in 16 months &mdash; pricing a Fed hike that does not arrive in June
(99.2% hold) but might arrive in September. The 2Y is the market's best real-time signal of where
the Fed funds rate is going: more accurate than statements, more immediate than dot plots. At 4.162%,
it sits 41bp above the top of the current Fed funds target (3.75%). That gap does not close without
either the Fed hiking or the market backing down. Two catalysts in 10 days decide which:
CPI June 10 and FOMC dot plot June 17.</p>

<p>Short US 2Y yield (MM-2026-013, pre-position) is the trade for the "market backs down" scenario.
If the dot plot holds at one cut &mdash; unchanged from March &mdash; the 2Y reverses 15&ndash;20bp in a
single session. The asymmetry: the hike is not in the Fed's own dots, only in the futures market.
When they diverge this far, one of them is wrong. The dot plot is the resolution mechanism.</p>
""",

    # ── Catalyst calendar ──────────────────────────────────────────────────
    "catalyst_calendar": [
        {
            "day": "Wed",
            "date": "Jun 10",
            "event": "US May CPI (BLS, 8:30 ET) — final pre-FOMC data point",
            "consensus": "CPI +3.8% YoY; core +3.3%. Energy elevated given WTI $93.",
            "view": (
                "Above 4.0%: 2Y tests 4.35%, gold breaks $4,250 stop, dot plot live for zero "
                "cuts + hike language. Below 3.5%: 2Y reverses 15bp, gold bids, "
                "MM-2026-004/013 accelerate. This binary settles whether Friday was the "
                "repricing or the opening act."
            ),
            "asymmetry": ">4%: DXY +0.5%, 10Y +10bp, gold -2%; <3.5%: 2Y -15bp, gold +2%",
            "dir": "flat",
        },
        {
            "day": "Thu",
            "date": "Jun 11",
            "event": "ECB rate decision — +25bp (99% priced; DFR to 2.25%)",
            "consensus": "+25bp confirmed. Press conference: neutral-to-hawkish.",
            "view": (
                "'Data-dependent pause' language = EUR sell-the-fact; spec long unwinds; "
                "MM-2026-012 accelerates. 'September hike priced' = EUR brief spike then "
                "fade as growth damage dominates. MM-2026-010 (Long DAX) benefits from ECB "
                "margin expansion for financials regardless of press conference tone."
            ),
            "asymmetry": "Pause signal: EUR/USD -0.8%; hawkish: EUR +0.4% spike then fade to -0.5%",
            "dir": "down",
        },
        {
            "day": "Tue-Wed",
            "date": "Jun 16-17",
            "event": "FOMC meeting + dot plot — no cut priced, hike narrative building",
            "consensus": "Hold at 3.5-3.75%. March median: one cut. Revision: 0 vs 1 vs hike signal.",
            "view": (
                "Zero-cut dot: 2Y +10bp, DXY +0.7%, gold sells hard, MM-2026-004 approaches "
                "4.65% stop. One-cut unchanged: markets exhale — gold bids, 2Y -15-20bp, "
                "MM-2026-013 accelerates. Hike dot (tail): VIX to 25+, risk-off. "
                "CPI Wednesday determines which language members signal before the blackout."
            ),
            "asymmetry": "0-cut: DXY +0.7%, 10Y +8bp; 1-cut unchanged: 2Y -15bp, gold +2%",
            "dir": "flat",
        },
        {
            "day": "Ongoing",
            "date": "Jun 8+",
            "event": "Iran/Israel/Hormuz — live military exchanges, MoU deadlocked",
            "consensus": "Air strikes remain air-only; no Hormuz closure; deal before month-end.",
            "view": (
                "Iran fired at Kuwait and Bahrain. MoU deadlocked on $24bn frozen assets. "
                "A confirmed tanker hit or mine detonation takes Brent to $110+ immediately. "
                "Watch tanker insurance pricing as the leading physical indicator — it moves "
                "before Brent spot reprices. MM-2026-002 and MM-2026-011 own the tail."
            ),
            "asymmetry": "Tanker hit: Brent +10-15% in hours, tanker insurance excludes Hormuz",
            "dir": "up",
        },
        {
            "day": "Ongoing",
            "date": "Jun 8+",
            "event": "USDJPY 160.32 — above MoF stated trigger; intervention watch",
            "consensus": "MoF will intervene above 162-163. No immediate trigger at 160.",
            "view": (
                "Finance Ministry Katayama spent 10 trillion yen in April to defend 155. "
                "Now above 160 with payrolls driving the dollar. BOJ September hike >50% priced. "
                "Intervention timing is when, not if. When it fires: USDJPY -3-5% in hours, "
                "yen carry trades unwind globally. Short USDJPY (MM-2026-007) stop 163."
            ),
            "asymmetry": "Intervention: USDJPY -3-5% in hours; yen carry unwind hits global equities",
            "dir": "down",
        },
    ],

    "earnings_ideas": [],

    # ── What changes my mind ────────────────────────────────────────────────
    "what_changes_mind": """
<ul>
<li><strong>MM-2026-001 &middot; Short EURAUD:</strong> Close if EURAUD holds above 1.660 after
June 11 ECB press conference &mdash; signals rate-hike bid overriding growth-error read. Currently 1.648; stop 1.662.</li>

<li><strong>MM-2026-002 &middot; Long Brent:</strong> Exit below $87 weekly close &mdash; MoU signed
and Hormuz reopened. Currently $96.05. Iran escalation has strengthened the thesis. Target $104.</li>

<li><strong>MM-2026-003 &middot; Long Brent/Short WTI spread:</strong> Discretionary close below $2.00
&mdash; physical market has priced the deal. Currently $2.38. Most likely near-term close. Watching daily.</li>

<li><strong>MM-2026-004 &middot; Short US 10Y yield:</strong> Stop at 4.65% &mdash; only 10bp away
at 4.544%. CPI above 4% Wednesday or zero-cut dot June 17 triggers the stop. Do not add.</li>

<li><strong>MM-2026-005 &middot; Long gold:</strong> Min hold to July 15 &mdash; no discretionary close.
Stop $4,250. Gold at $4,350 &mdash; $100 from stop. Zero-cut dot + gold below $4,400 June 17 is the
early warning of thesis break.</li>

<li><strong>MM-2026-007 &middot; Short USDJPY:</strong> Stop 163.00. Currently 160.32 &mdash; above the
stated intervention trigger. Size conservatively: the payoff if intervention fires is convex.</li>

<li><strong>MM-2026-008 &middot; SPX put spread:</strong> Trim to half if SPX recovers above 7,500
before Wednesday CPI. Take the gain on half, keep the FOMC tail exposure on the rest.
Up 128% &mdash; protect some of the gain.</li>

<li><strong>MM-2026-009 &middot; 2s10s steepener:</strong> Min hold to July 16. Up 154% at +38.2bp;
target +60bp. FOMC dot plot delivers the next leg &mdash; hold.</li>

<li><strong>MM-2026-010 &middot; Long DAX / Short Nasdaq:</strong> Stop ratio 0.943. Thesis breaks if
CPI/FOMC drives a global risk-off that hits all equity markets indiscriminately. Needs two more
sessions to confirm the structural divergence.</li>

<li><strong>MM-2026-012 &middot; Short EURUSD:</strong> Stop 1.182. Close if EUR/USD spikes above 1.182
on ECB press conference &mdash; hawkish surprise overrides the sell-the-fact setup. Target 1.130.</li>

<li><strong>MM-2026-013 &middot; Short US 2Y yield:</strong> Stop 4.35%. Min hold 30 days. Close if CPI
Wednesday above 4% &mdash; that confirms the hike repricing and the 2Y level is fair, not excessive.
Thesis: dot plot June 17 holds at one cut; 2Y reverses 15&ndash;20bp.</li>
</ul>
""",

    # ── Client ammo ────────────────────────────────────────────────────────
    "client_ammo": [
        {
            "q": "AVGO beat on every metric — why was it stopped out?",
            "a": (
                "Because the market was pricing the 100th percentile of AI revenue guidance and AVGO "
                "delivered the 93rd. Q2 AI revenue $10.8B vs $10.7B consensus &mdash; a beat. Q3 AI guide "
                "$16.0B vs buy-side $17.2B &mdash; a miss on the number that mattered at 41x. The guide was "
                "the highest AI revenue guidance in corporate history. The buy side needed higher. At that "
                "multiple, 'exceptional but below the extrapolation' is not enough. The cycle is not over; "
                "the multiple compressed. Re-entry below $220 when the multiple normalises to 30-32x."
            ),
        },
        {
            "q": "How serious is the Hormuz escalation — should I be hedging oil?",
            "a": (
                "More serious than last week. This weekend moved from diplomatic standoff to live military "
                "exchanges: Israel struck Iranian defence systems, US hit Iranian radar, Iran fired missiles "
                "at Kuwait and Bahrain. The MoU is deadlocked on $24bn frozen assets. Brent at $96 is "
                "actual risk premium, not hope. The signal to watch is tanker insurance pricing &mdash; if "
                "writers start excluding Hormuz from coverage, physical delivery of Atlantic-basin crude "
                "freezes before Brent reprices. We own the tail through Long Brent (MM-2026-002) and "
                "the new Brent $100/$115 call spread (MM-2026-011)."
            ),
        },
        {
            "q": "What does payrolls +172k mean for the Fed — are hikes back on the table?",
            "a": (
                "In June: no &mdash; 99.2% probability of hold. But September and December are now "
                "genuinely live for a hike, not a cut. Markets price 57% probability of zero cuts in "
                "2026, up from below 50% before the data. The June 17 dot plot decides. If the median "
                "goes to zero cuts, the 2Y at 4.16% is confirmed and every duration position takes "
                "another leg of pain. If the median holds at one cut (unchanged from March), the 2Y "
                "reverses 15-20bp in a session. CPI Wednesday is the deciding print: above 4% confirms "
                "the repricing; below 3.5% reverses it."
            ),
        },
    ],

    # ── VIX term structure (for chart) ─────────────────────────────────────
    "vix_term": [
        {"label": "VIX9D", "value": 15.5},
        {"label": "VIX",   "value": 18.80},
        {"label": "VIX3M", "value": 20.0},
        {"label": "VIX6M", "value": 21.5},
    ],

    # ── Yield curve (for chart) ─────────────────────────────────────────────
    "yield_curve_pts": [
        {"label": "2Y",  "value": 4.162},
        {"label": "5Y",  "value": 4.42},
        {"label": "10Y", "value": 4.544},
        {"label": "30Y", "value": 4.70},
    ],

    # ── Event radar note (for pre-positioning section) ──────────────────────
    "event_radar_note": (
        "<p>Three events in the next 10 days that resolve every open position's thesis: "
        "CPI June 10 (payrolls follow-through test), ECB June 11 (+25bp confirmed; press conference "
        "determines EUR trajectory), FOMC June 16&ndash;17 (dot plot is the binary that settles whether "
        "Friday's repricing was a shock or a regime change). "
        "Short US 2Y yield (pre-position below) is sized for the dot plot 'one-cut-maintained' scenario "
        "where the market's hike pricing reverses in a single session.</p>"
    ),

    # ── Staleness check ─────────────────────────────────────────────────────
    "staleness": [
        {"datum": "S&P 500 ~7,427",      "source": "Investtech / web search June 8",     "asof": "2026-06-08", "stale": False},
        {"datum": "Nasdaq 100 ~26,500",  "source": "Web search (estimated) June 8",      "asof": "2026-06-08", "stale": False},
        {"datum": "DAX ~24,917",         "source": "TradingEconomics / web search",       "asof": "2026-06-08", "stale": False},
        {"datum": "Nikkei 64,024",       "source": "TradingEconomics June 8",             "asof": "2026-06-08", "stale": False},
        {"datum": "FTSE 100 ~10,416",    "source": "TradingEconomics June 8",             "asof": "2026-06-08", "stale": False},
        {"datum": "EURUSD 1.1536",       "source": "TradingEconomics / FXStreet June 8",  "asof": "2026-06-08", "stale": False},
        {"datum": "USDJPY 160.32",       "source": "TradingEconomics June 8",             "asof": "2026-06-08", "stale": False},
        {"datum": "DXY ~100.5",          "source": "TradingEconomics (estimated) June 8", "asof": "2026-06-08", "stale": False},
        {"datum": "WTI $93.67",          "source": "OilPrice.com / derived from spread",  "asof": "2026-06-08", "stale": False},
        {"datum": "Brent $96.05",        "source": "ICE / OilPrice.com June 8",           "asof": "2026-06-08", "stale": False},
        {"datum": "Gold $4,350",         "source": "CNBC / LiteFinance June 8",           "asof": "2026-06-08", "stale": False},
        {"datum": "US 10Y 4.544%",       "source": "TradingEconomics / CNBC June 8",      "asof": "2026-06-08", "stale": False},
        {"datum": "US 2Y 4.162%",        "source": "CNBC / TheStreet June 8",             "asof": "2026-06-08", "stale": False},
        {"datum": "2s10s +38.2bp",       "source": "Derived from 2Y/10Y levels",          "asof": "2026-06-08", "stale": False},
        {"datum": "VIX 18.80",           "source": "Yahoo Finance / CBOE June 8",         "asof": "2026-06-08", "stale": False},
        {"datum": "May payrolls +172k",  "source": "BLS / Fox Business June 5",           "asof": "2026-06-05", "stale": False},
        {"datum": "AVGO Q2 results",     "source": "SEC 8-K / PR Newswire June 3",        "asof": "2026-06-03", "stale": False},
        {"datum": "SOFR ~3.62%",         "source": "NY Fed (June 6 publication)",         "asof": "2026-06-06", "stale": True},
        {"datum": "COT oil/gold",        "source": "CFTC (June 3 release, Jun 1 data)",   "asof": "2026-06-01", "stale": True},
        {"datum": "GBPUSD",              "source": "Unverified this refresh",             "asof": "unavailable", "stale": True},
        {"datum": "Bund / Gilt 10Y",     "source": "Unverified this refresh",             "asof": "unavailable", "stale": True},
        {"datum": "MOVE index",          "source": "Unverified this refresh",             "asof": "unavailable", "stale": True},
        {"datum": "USDCNH",              "source": "Unverified this refresh",             "asof": "unavailable", "stale": True},
    ],

    # ── Trade cards (already in trades.json; no ingest needed) ─────────────
    "new_ideas":          new_ideas_cards,
    "pre_position_ideas": prepos_cards,

    # ── Extra fields for shark_format / index.html ──────────────────────────
    "summary_narrative": """
<p>Three things happened in 96 hours that redrew the map. On Wednesday June 3, Broadcom proved
the AI cycle is real: $22.2B in revenue, $10.8B of AI semiconductor income, $16B guided for Q3.
On Friday June 5, payrolls printed 172,000 &mdash; double the 85,000 consensus &mdash; and the same market
that cheered AVGO's beat sold every name with an AI multiple attached. And over the weekend,
Israel struck western and central Iranian defence systems while the US hit Iranian radar sites
and Iran fired missiles at Kuwait and Bahrain. That is not an escalation calendar. It is the
absence of a de-escalation one.</p>

<p>Break apart what happened to AVGO and the anatomy is instructive. The stock beat every consensus
estimate &mdash; but the buy side needed $17.2 billion in Q3 AI revenue guidance to justify 41&times;
forward earnings. AVGO guided $16.0 billion. The guide was the 93rd percentile of any company's AI
revenue guidance in history. The market priced the 100th. That gap &mdash; between what was delivered
and what was needed &mdash; explains the 16% afterhours drop. The thesis is not broken. The multiple was.</p>

<p><strong>The driver:</strong> Payrolls +172k repriced 57% probability of zero cuts in 2026, up from below 50%.
The Fed holds at 3.5&ndash;3.75% in June (99.2% priced) but September and December are now genuinely live
for a hike, not a cut. That reprices every duration position and every high-multiple equity simultaneously.</p>

<p><strong>Counter-intuitive hook:</strong> Gold is down while oil is up. Gold fell to $4,350 while Brent
rallied to $96. Gold prices real rates (higher on payrolls repricing), not war premium. Oil prices physical
supply disruption. Two different primary drivers in two different assets on the same headline.</p>

<p><strong>The gap:</strong> At 41&times; forward earnings, "exceptional but below buy-side" is insufficient.
The shift from demand-pull to supply-allocation is what the tape is beginning to price. Three catalysts
in 10 days decide the next leg: May CPI June 10, ECB June 11, FOMC dot plot June 16&ndash;17.</p>
""",

    "takeaways": [
        "May NFP +172k (2× the 85k consensus) repriced a Fed hike and de-rated the AI multiple simultaneously in a single session.",
        "AVGO stopped June 8: Q3 AI guide $16.0B vs buy-side $17.2B at 41× forward earnings — the 93rd percentile wasn't enough for the multiple.",
        "Israel struck Iran's defence systems; US hit Iranian radar; Iran fired at Kuwait and Bahrain — Brent gapped to $96.",
        "Four new trades added: Long DAX/short Nasdaq (010), Brent call spread (011), Short EURUSD (012), Short US 2Y (013).",
        "Three binary catalysts remain: May CPI Jun 10, ECB Jun 11, FOMC dot plot Jun 16-17 — the book holds both tails.",
    ],

    "scenarios": [
        {"kind": "bull", "label": "Bull", "pct": "40%",
         "headline": "ECB pauses, dot plot holds one cut, Iran stays air-only",
         "body": ("ECB hikes Thursday, signals pause. FOMC dot plot holds at one cut. Iran stays air-only — "
                  "no Hormuz closure. AI names re-rate as $16B Q3 delivery proves the cycle intact. SPX 7,700 by July.")},
        {"kind": "base", "label": "Base", "pct": "40%",
         "headline": "ECB hawkish, dot plot 0 cuts, Brent $90–100 on Hormuz standoff",
         "body": ("ECB sounds hawkish, dot plot goes to zero cuts. EUR fades on stagflation read. "
                  "AI multiple stays compressed. Brent $90–100 on Hormuz standoff. SPX 7,000–7,500 chop. 2s10s to +55bp.")},
        {"kind": "bear", "label": "Bear", "pct": "20%",
         "headline": "Hormuz closure confirmed, FOMC hike signal, CPI above 4%",
         "body": ("Physical disruption confirmed (mine or tanker hit). FOMC signals hike. CPI above 4%. "
                  "Credit cracks from 80bp IG OAS. Tech −15%. USDJPY intervention unwinds yen carry globally. Oil $110+.")},
    ],

    "rates_levels": [
        {"name": "SOFR (o/n)", "level": "~3.62%", "chg": "funding", "dir": "flat",
         "vid": "sofr-v", "cid": "sofr-c", "asof": "Mon 8 Jun · NY Fed"},
        {"name": "US 2Y",    "level": "4.162%",     "chg": "+10bp wk",  "dir": "up"},
        {"name": "US 10Y",   "level": "4.544%",     "chg": "+8bp wk",   "dir": "up"},
        {"name": "US 30Y",   "level": "4.70%",      "chg": "est",       "dir": "up"},
        {"name": "2s10s",    "level": "+38.2bp",    "chg": "+23bp wk",  "dir": "up"},
        {"name": "Bund 10Y", "level": "unverified", "chg": "",          "dir": "flat"},
        {"name": "Gilt 10Y", "level": "unverified", "chg": "",          "dir": "flat"},
        {"name": "MOVE",     "level": "~120 (est)", "chg": "elevated",  "dir": "up"},
    ],

    "ideas_note": (
        "<p>Three new reactive ideas (MM-010, 011, 012) and one pre-position (MM-013) were added today "
        "on a regime re-rate to 'Payrolls Shock Meets Hormuz Fire'. The payrolls shock and Hormuz escalation "
        "changed both the rates and geopolitics thesis simultaneously. Trades are sized conservatively &mdash; "
        "three binary events (CPI, ECB, FOMC) remain in the next 10 days. AVGO position stopped at $216.</p>"
    ),
}

# ── Render: legacy single page (output.html) ──────────────────────────────
book.step("Rendering output.html")
html_out = book.build_html(brief, trades, regime_log)
with open(book.OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_out)
book.log(f"wrote {len(html_out):,} bytes -> {book.OUTPUT_PATH}")

# ── Render: Shark Tank pages + fragments ──────────────────────────────────
book.step("Rendering Shark Tank pages + fragments (index.html, insights, earnings, trades, frag/*)")
shark_format.render_all(brief, trades, regime_log)

# ── Persist state ──────────────────────────────────────────────────────────
book.step("Saving trades.json + regime_log.json")
book.save_json(book.TRADES_PATH, trades)
book.save_json(book.REGIME_PATH, regime_log)

book.step("Done")
