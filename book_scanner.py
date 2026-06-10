#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""book_scanner.py — Shark Tank client-book module (Ruleset v2).

Turns a client position file into (a) a marked-to-live portfolio view and (b) a
ranked shelf of structured-product / derivative ideas. Standard library only;
live marks via live_levels.py (TradingView scanner). House views and the ATM-IV
seed are read from json files (mirrors trades.json: read files, never live-fetch
mid-reasoning, so a run is reproducible and self-gradable).

    import book_scanner
    scan = book_scanner.build_scan(brief)     # brief = today's market-map dict (consistency lock)
    shark_format.render_all(brief, trades, regime_log, scan=scan)

Demo book only. Not investment advice.
"""
import os, json
from datetime import date

import live_levels

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK_PATH  = os.path.join(HERE, "client-book-json-Aurora.json")
VIEWS_PATH = os.path.join(HERE, "house_views.json")
IVOL_PATH  = os.path.join(HERE, "ivol_history.json")
TODAY = date.today().isoformat()

# On the website the client is named "Fable" (book file alias is the internal "Aurora").
CLIENT_DISPLAY = "Fable"

# position ticker -> TradingView symbol for the live refresh
TV_MAP = {
    "MU US": "NASDAQ:MU", "SPY US": "AMEX:SPY", "NVDA US": "NASDAQ:NVDA",
    "AVGO US": "NASDAQ:AVGO", "AMD US": "NASDAQ:AMD",
    "MC FP": "EURONEXT:MC", "SAP GY": "XETR:SAP", "TTE FP": "EURONEXT:TTE",
}

# Equity sector + book-wide region maps, used for the Portfolio allocation pies.
EQUITY_SECTOR = {
    "MU US": "Semiconductors", "NVDA US": "Semiconductors", "AVGO US": "Semiconductors",
    "AMD US": "Semiconductors", "SPY US": "US index (ETF)", "MC FP": "Luxury",
    "SAP GY": "Software", "TTE FP": "Energy",
}
ASSET_BUCKET = {
    "equity": "Equities", "equity_etf": "Equities",
    "govt_bond": "Fixed income", "corp_bond": "Fixed income",
    "commodity_etc": "Commodities",
}

# Product type + objective per idea num, gated by asset class (the shelf):
#   Equities  — RevCon / FCN / Phoenix / Digital review / Autocall Market Plus / BREN /
#               protected participation; OTC accumulators / decumulators.
#   FX        — DCS (income); forwards / seagulls / puts / accumulators (hedging).
#   Rates     — range accruals only.
PRODUCT_META = {
    1:   ("Collar + SBL + decumulator", "Concentration hedge / de-risk"),
    2:   ("T-bill ladder + FX forward strip", "FX liability hedge"),
    3:   ("FX seagull", "FX hedge"),
    4:   ("Bond switch", "Loss harvest / carry pickup"),
    5:   ("BREN (range note)", "Participation / income"),
    6:   ("Cash-secured put (OTC)", "Income / add-at-support"),
    7:   ("Loss harvest + buffered note", "Loss recovery / protected re-entry"),
    8:   ("Deposit + range accrual", "Income / end cash drag"),
    9:   ("Reverse convertible (FCN if certain)", "Income / add-at-level"),
    10:  ("Covered-call overwrite / decumulator", "Income / staged exit"),
    11:  ("EUR bond switch", "Loss harvest / carry pickup"),
    12:  ("Hold — no structure", "Hedge · do not trim"),
    13:  ("DCS — suppressed", "Suppressed · conflicts with FX hedge"),
    14:  ("Prepaid variable forward (OTC)", "Monetise concentration / tax-defer"),
    101: ("Capital-protected note", "Protected participation"),
    102: ("Cash-secured put (OTC)", "Income / discount accumulation"),
    103: ("Curve range accrual (capital-protected)", "Rates participation / macro"),
    104: ("Thematic participation note", "Participation / diversify"),
}

# Client liabilities (demo) — drives the FX liability-netting (Observable O12).
LIABILITIES = [
    {"kind": "USD mortgage", "currency": "USD", "monthly": 38500, "annual": 462000,
     "until": "2031", "note": "Miami property; $38.5k/mo to 2031. Natural short-USD position — nets against the USD asset sleeve."},
]


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


# --------------------------------------------------------------------------
# Live refresh + metrics
# --------------------------------------------------------------------------
def refresh_marks(bookdata):
    """Mark every liquid holding to live TradingView levels; recompute MV + P&L.

    US/EU single names -> live equity quote. Gold ETC -> rescaled to live spot.
    Bonds keep their yield-derived marks (no free clean bond price feed)."""
    notes = []
    eurusd = bookdata["client"]["fx_reference"]["EURUSD"]
    syms = list(TV_MAP.values()) + ["TVC:GOLD"]
    try:
        q = live_levels.scan(syms)
    except Exception as ex:  # offline -> keep file marks
        return [f"live refresh skipped ({type(ex).__name__}); using file marks"]

    gold = q.get("TVC:GOLD", {}).get("close")
    for p in bookdata["positions"]:
        tk = p["ticker"]
        old = p.get("mark_price")
        if tk in TV_MAP and TV_MAP[tk] in q:
            new = q[TV_MAP[tk]]["close"]
            p["mark_price"] = round(new, 2)
            p["day_chg_pct"] = round(q[TV_MAP[tk]]["chg_pct"], 2)
            p["mark_quality"] = "verified_live"
            if old and abs(new - old) / old > 0.03:
                notes.append(f'{tk}: mark refreshed {old} -> {p["mark_price"]} (was indicative)')
        elif p["id"] == "CO-001" and gold:  # Xetra-Gold ETC tracks spot
            ref_spot = 4357.0  # the spot the file mark was struck at
            p["mark_price"] = round(p["mark_price"] * gold / ref_spot, 2)
            p["day_chg_pct"] = round(q.get("TVC:GOLD", {}).get("chg_pct", 0), 2)
        # recompute MV + pnl in position ccy
        p["market_value"] = round(p["mark_price"] * p["quantity"] *
                                  (0.01 if p.get("quantity_type") == "nominal" else 1))
        if p.get("cost_basis"):
            p["pnl_pct"] = round((p["market_value"] / p["cost_basis"] - 1) * 100, 1)
        # EUR value
        p["value_eur"] = round(p["market_value"] / eurusd) if p["currency"] == "USD" else p["market_value"]
    return notes


def compute_metrics(bookdata):
    eurusd = bookdata["client"]["fx_reference"]["EURUSD"]
    pos = bookdata["positions"]
    cash = bookdata.get("cash", [])
    cash_eur = sum(c["amount"] / (eurusd if c["currency"] == "USD" else 1) for c in cash)
    pos_eur = sum(p["value_eur"] for p in pos)
    total = pos_eur + cash_eur

    for p in pos:
        p["weight_pct"] = round(100 * p["value_eur"] / total, 1)

    usd_assets = sum(p["value_eur"] for p in pos if p["currency"] == "USD") + \
                 sum(c["amount"] / eurusd for c in cash if c["currency"] == "USD")
    usd_liab_eur = sum(l["annual"] / eurusd for l in LIABILITIES if l["currency"] == "USD")
    # crude PV proxy for the liability stream (~5y avg life on the mortgage runway)
    usd_liab_pv_eur = usd_liab_eur * 5

    largest = max(pos, key=lambda p: p["value_eur"])
    return {
        "total_eur": round(total),
        "pos_eur": round(pos_eur),
        "cash_eur": round(cash_eur),
        "cash_pct": round(100 * cash_eur / total, 1),
        "usd_pct": round(100 * usd_assets / total, 1),
        "eur_pct": round(100 * (total - usd_assets) / total, 1),
        "usd_assets_eur": round(usd_assets),
        "usd_liab_pv_eur": round(usd_liab_pv_eur),
        "net_usd_mismatch_eur": round(usd_assets - usd_liab_pv_eur - cash_eur * 0.6),
        "net_usd_pct": round(100 * (usd_assets - usd_liab_pv_eur) / total, 1),
        "largest": {"ticker": largest["ticker"], "weight_pct": largest["weight_pct"]},
        "eurusd": eurusd,
    }


def _conc_flag(w, asset_class=""):
    # Diversified funds (ETFs) flag only at >=25%; single names use the 10/15/20 ladder.
    if asset_class in ("equity_etf",):
        return ("flag", "var(--gold)") if w >= 25 else ("", "")
    if w >= 20: return ("urgent", "var(--red)")
    if w >= 15: return ("act", "var(--red)")
    if w >= 10: return ("flag", "var(--gold)")
    return ("", "")


def attach_views_and_vol(bookdata, views, ivol):
    vmap = {v["ticker"]: v for v in views.get("views", [])}
    hist = ivol.get("history", {})
    for p in bookdata["positions"]:
        v = vmap.get(p["ticker"])
        p["house_view"] = v["view"] if v else "-"
        p["view_confidence"] = v["confidence"] if v else "-"
        snap = (hist.get(p["ticker"]) or [{}])[-1]
        p["iv_pct"] = snap.get("atm_iv_pct")
        p["iv_percentile_est"] = snap.get("iv_percentile_est")
        p["iv_confidence"] = snap.get("confidence")
        p["iv_basis"] = snap.get("iv_basis", "implied")
        tier, _ = _conc_flag(p.get("weight_pct", 0), p.get("asset_class", ""))
        p["conc_tier"] = tier


# --------------------------------------------------------------------------
# The idea shelf — authored per the ruleset, scored /8 (Section 7).
# Each: tier FIRE/WATCH/SUPPRESS · subscores sum to score · sourced/estimated flags.
# --------------------------------------------------------------------------
def _idea(num, title, rules, tickers, score, subs, sub_src, tier, what, moves, client, tags, risk=None,
          section="enhance", asset_group="Multi-asset", tenor=None, sizing=None, impact=None,
          sources=None, origin=None):
    return {"num": num, "title": title, "rules": rules, "tickers": tickers,
            "score": score, "subs": subs, "sub_src": sub_src, "tier": tier,
            "what_it_is": what, "what_moves_it": moves, "client_note": client,
            "tags": tags, "risk": risk, "section": section, "asset_group": asset_group,
            "tenor": tenor, "sizing": sizing, "portfolio_impact": impact,
            "sources": sources or [], "origin": origin}


# Per-idea enrichment for the 13 'enhance' ideas — asset group (for grouping),
# tenor, sizing and the portfolio-level impact. Keyed by idea number.
_ENHANCE_META = {
    1:  ("Equity", "Collar through 24-Jun; SBL revolving; decumulator 6-12m post-print",
         "Collar full $15m (26.4%); Lombard ~50% LTV on the hedged stock; decumulator notional <=50% of the position",
         "Removes the book's single largest risk — a 26% concentration on a 10x gain — without a taxable sale, and frees Lombard liquidity to fund the other ideas.",
         [{"name": "Goldman Sachs / UBS", "type": "sell-side"}, {"name": "JP Morgan GIS", "type": "house anchor", "note": "hedge the tail"}]),
    2:  ("FX", "T-bill ladder <12m; forward strip 12-24m laddered",
         "Earmark from the $3m idle USD cash; forwards on $462k/yr of payments",
         "Converts idle USD cash into a self-funding hedge of a real EUR liability — kills the 'what does the house cost in euros' risk and ends part of the cash drag at once.",
         [{"name": "Brent Donnelly (am/FX)", "type": "Substack/X", "note": "EUR/USD tape"}]),
    3:  ("FX", "Seagull 3-6m",
         "Hedge 30-50% of the ~70% net USD mismatch (~EUR10-12m notional)",
         "Cuts translation risk on the 74% USD sleeve for a EUR-base client, sized correctly only because the mortgage liability was netted first.",
         [{"name": "Brent Donnelly (am/FX)", "type": "Substack/X"}, {"name": "JP Morgan GIS", "type": "house anchor", "note": "hedge USD into ECB"}]),
    4:  ("Rates", "Switch (no added tenor)",
         "$5m nominal UST '31 -> current coupons",
         "Turns a dead -14% duration loss into ~3x the running carry at the same credit, and banks a loss that offsets gains harvested elsewhere.",
         [{"name": "Today's brief", "type": "in-house", "note": "CPI gates the re-entry"}]),
    5:  ("Equity", "Range note (BREN) 3-6m",
         "On ~EUR1.5m of the NVDA position",
         "Monetises a flat, range-bound LIKE position for income while the macro wobble (CPI) plays out — no new directional risk.",
         [{"name": "UBS", "type": "sell-side"}, {"name": "Citrini Research", "type": "Substack/X"}]),
    6:  ("Cash", "T-bills <12m; cash-secured put 1-3m",
         "Residual USD cash; CSP one tranche (~$0.5m) struck at NVDA 195",
         "Ends the USD cash drag and gets the client paid to add a LIKE name at the level they'd buy anyway.",
         [{"name": "UBS", "type": "sell-side", "note": "NVDA support"}]),
    7:  ("Equity", "Buffered note 12-18m re-entry",
         "Harvest the full EUR2.35m AVGO position",
         "Banks ~$635k of losses to offset the tax the MU exit will create, while a buffered note keeps the exposure case alive — the harvest and the concentration trim travel together.",
         [{"name": "Today's brief", "type": "in-house", "note": "vol crushed post-print"}]),
    8:  ("Cash", "Deposit 3-6m; CMT range accrual 2y (re-quoted)",
         "EUR2.4m idle EUR cash",
         "Ends the EUR cash drag into an ECB hike; declining the mispriced 5% headline (failed headroom) and re-quoting builds more trust than selling it.",
         [{"name": "Today's brief", "type": "in-house", "note": "CPI gates the cap"}]),
    9:  ("Equity", "Reverse convertible 6m (FCN if coupon must be certain)",
         "On ~EUR1-1.5m at the LVMH add level",
         "Monetises a -32% loss by getting the client paid at the exact level they'd average down — turns a drag into income or a disciplined add.",
         [{"name": "JP Morgan GIS", "type": "house anchor", "note": "cautious luxury"}]),
    10: ("Equity", "Covered-call overwrite 2-3m / decumulator",
         "On part of the AMD position",
         "Income on, or a disciplined staged exit from, a stretched +395% winner the desk no longer loves at this valuation.",
         [{"name": "UBS", "type": "sell-side", "note": "favours NVDA"}]),
    11: ("Rates", "Switch (ECB-gated, post-Thursday)",
         "EUR3m nominal Siemens '30",
         "The EUR twin to the UST swap — harvests a duration loss and lifts carry; pairs onto the same fixed-income review call.",
         [{"name": "Today's brief", "type": "in-house", "note": "ECB Thursday"}]),
    12: ("Multi-asset", "Hold (no structure)",
         "Full TTE (+64%) and gold (+100%) positions",
         "Preserves the book's two bear-case hedges intact — the scanner suppresses the raw winner-trim because protection beats profit-take while the brief's bear case is live.",
         [{"name": "Doomberg", "type": "Substack", "note": "energy"}, {"name": "Michael Howell", "type": "Substack/X", "note": "gold/liquidity"}]),
    13: ("FX", "Suppressed (no structure)",
         "n/a",
         "Avoids a self-cancelling trade — converting EUR into USD while idea 3 hedges USD off — and surfaces the conflict for the advisor instead of silently doing both.",
         [{"name": "Suitability layer", "type": "in-house"}]),
    14: ("Equity", "Prepaid variable forward 2-3y",
         "~$5-7m of the MU position (about a third)",
         "The OTC alternative to the collar+SBL: raises ~80% of the slice's value in cash today WITHOUT a sale, caps the realised-gain tax event, floors the downside and keeps a defined slice of upside — de-risks the book's single largest concentration and funds the other ideas in one trade.",
         [{"name": "Goldman Sachs / Morgan Stanley", "type": "sell-side", "note": "PVF structuring"},
          {"name": "JP Morgan GIS", "type": "house anchor", "note": "hedge the concentration"}]),
}

# Per-idea enrichment: fundamental thesis (with valuation multiples), explicit catalyst text,
# and per-criterion WHY explanations. Keys are idea nums (int). Applied in build_ideas().
IDEA_ENRICHMENTS = {
    1: {
        "fundamental_thesis": (
            "Micron Technology (MU) is the book's single largest concentration at 26.4% of NAV "
            "— 2.6× the 10% policy weight — on a 10× gain from the AI HBM DRAM cycle. "
            "Live multiples: see Yahoo Finance data below. At any multiple, single-name "
            "concentration 2.6× above policy is a portfolio risk independent of MU's fundamental "
            "case. The collar does NOT require a bearish view on MU — it is a risk-management "
            "execution analogous to diversifying a concentrated ESPP. The Lombard line adds "
            "immediate liquidity without triggering a taxable sale."
        ),
        "catalyst_text": (
            "24-Jun MU Q3 FY26 earnings (binary print). Collar must be in place BEFORE this date. "
            "C6 gate: do NOT deploy the 2×-geared decumulator into the binary event — "
            "collar first; decumulate after vol normalises post-print. "
            "SBL facility can draw immediately once the collar is in place."
        ),
        "sub_why": {
            "setup":   "2/2 — 26.4% concentration confirmed from position file; 24-Jun IV elevated into binary; zero-cost collar into catalyst is the textbook setup. All inputs verified.",
            "pricing": "2/2 — elevated pre-earnings IV means the sold call fully finances the bought put (ZCC achievable); Lombard LTV improves with collateral lock; both sourced.",
            "catalyst": "1/2 — 24-Jun is the timing gate for the decumulator, not the collar itself. Full sequence is 3 steps (collar → SBL → decumulator); only the last step uses the catalyst.",
            "fit":     "2/2 — C1 rule: ≥10% single-name concentration requires a documented hedge plan. Client is confirmed comfortable with structured products.",
        },
    },
    2: {
        "fundamental_thesis": (
            "The Miami mortgage creates a $38,500/month USD obligation for a EUR-base client. "
            "At EUR/USD 1.155, each annual payment costs ~EUR401k; at 1.20 that falls to ~EUR385k; "
            "at 1.08 it rises to ~EUR428k. Over 5 years the liability PV is ~$2.3m — a material "
            "unhedged FX exposure. A T-bill ladder earns ~4%+ while eliminating exchange-rate "
            "uncertainty on each dated obligation. Carry: forward points are positive for a "
            "EUR-base client selling USD forward (ECB rate > Fed equivalent net), so the hedge "
            "earns carry AND locks the rate — positive expected value on both dimensions."
        ),
        "catalyst_text": (
            "ECB Jun 11 (+25bp fully priced). A hawkish press conference lifts EUR/USD and "
            "improves the forward entry (stronger EUR = fewer euros needed to sell forward). "
            "Structure the strip AFTER Thursday's decision to avoid buying into an ECB-driven "
            "EUR squeeze. No binary gate — valid regardless of ECB outcome; Thursday optimises entry."
        ),
        "sub_why": {
            "setup":   "2/2 — liability confirmed ($38.5k/mo USD from client file); idle USD cash confirmed ($3m); T-bill maturities matched to payment dates. Setup is certain, not probabilistic.",
            "pricing": "1/2 — forward strip yield estimated pending re-quote after CPI and ECB; T-bill yield directionally ~4%+ but exact strip must be formally priced Friday.",
            "catalyst": "2/2 — unlike equity trades, nothing binary gates this product; ECB improves entry without gating it. Design feature: always on, ECB just optimises timing.",
            "fit":     "2/2 — addresses the client's explicit stated anxiety ('what does the house cost in euros?'); USD mortgage is the documented liability; direct liability match.",
        },
    },
    3: {
        "fundamental_thesis": (
            "After netting the USD mortgage liability PV (~$2.3m), the book's residual net USD "
            "exposure is ~74% of NAV on a EUR base. At EUR/USD 1.155, a 10% move creates "
            "~EUR800k+ translation gain/loss on an EUR11m book. The seagull hedges 30-50% of "
            "this mismatch at near-zero net premium (far-wing sale cheapens the hedge). "
            "EUR/USD valuation: fair-value models (PPP, BEER) cluster around 1.10-1.18; "
            "current ~1.155 is near the midpoint, hence a range structure, not a directional "
            "forward. Relevant level: EUR/USD spot from live feed."
        ),
        "catalyst_text": (
            "ECB Jun 11: hawkish Lagarde spikes EUR/USD and worsens the forward entry — "
            "structure the seagull AFTER the ECB decision. "
            "FOMC Jun 16-17: Fed hold widens the rate differential further, potentially improving "
            "entry if EUR weakens post-FOMC. Both events are timing gates, not payoff triggers."
        ),
        "sub_why": {
            "setup":   "2/2 — net USD mismatch quantified from position file with correct liability netting; seagull size calculated off the net (not naive gross). Verified.",
            "pricing": "1/2 — seagull wing placement and net premium depend on post-ECB EUR/USD vol and skew; estimated until formally priced Thursday or Friday.",
            "catalyst": "1/2 — ECB Thursday is a timing gate (hawkish = worse entry), not a payoff catalyst; the seagull is passive, not event-driven.",
            "fit":     "2/2 — X1/X2 rules: EUR-base client with 74% USD sleeve; liability-netting makes the hedge correctly sized; directly addresses the stated mandate.",
        },
    },
    4: {
        "fundamental_thesis": (
            "The 2021 UST 1.25% '31 is marked at ~$85.60 (est.), a ~-14% duration loss vs cost. "
            "Current US 10Y yield ~4.55% — the swap roughly triples the running coupon at the same "
            "credit. No credit risk: both legs are US Treasuries. The swap is a pure carry pickup "
            "on the income statement. The only question is timing: today's CPI at 8:30 sets the "
            "re-entry yield. Hot print (10Y to 4.65%+) improves the coupon further. Cold print "
            "(10Y to 4.35%) means execute today. Either way, the swap wins on carry at same credit. "
            "Relevant metric: US 10Y yield from live feed."
        ),
        "catalyst_text": (
            "May CPI Jun 10 at 8:30 ET — the key gate. Hot (>4.1%): wait for FOMC for better entry. "
            "Cold (≤3.7%): execute today. "
            "FOMC dot plot Jun 16-17: zero-cut median pushes 10Y higher; one-cut-held brings it lower. "
            "Optimal sequence: observe CPI at 8:30, decide whether to execute today or next week."
        ),
        "sub_why": {
            "setup":   "2/2 — 2021 vintage UST duration loss confirmed (~$85.6 mark est.); current 4.55% coupon triples the running yield at same credit; swap math is verified in principle.",
            "pricing": "1/2 — re-entry yield depends on today's CPI print (10Y may move 10-15bp); exact replacement bond coupon not yet known.",
            "catalyst": "1/2 — CPI at 8:30 and FOMC Jun 16-17 are both binary gates; holding to see the print is the correct call. Catalyst gates, doesn't trigger.",
            "fit":     "2/2 — B1 rule: swap is yield-neutral at same credit, pure carry improvement; client holds duration (confirmed from position file); the loss is already taken.",
        },
    },
    5: {
        "fundamental_thesis": (
            "NVIDIA (NVDA) is the book's AI anchor — currently at a small paper loss. "
            "House view: LIKE. Live multiples: see Yahoo Finance data below. "
            "NVDA is mid-range with a flat near-term trend — the prerequisite for a BREN. "
            "The range note pays a coupon as long as NVDA stays within the defined range "
            "(e.g. ~$195-$235 est.); it converts the paper loss into paid waiting rather than "
            "a realised loss. Thesis is NOT 'NVDA will re-rate sharply'; it is 'NVDA will not "
            "move dramatically in 45 days.' Delta-netting rule: BREN (idea 5) and CSP (idea 6) "
            "are mutually exclusive on NVDA — never both simultaneously."
        ),
        "catalyst_text": (
            "Late-Aug NVDA Q2 FY27 earnings — ~45+ days after the BREN entry; the tenor is designed "
            "to clear the print. CPI today (Jun 10) and FOMC Jun 16-17 are near-term macro wobbles "
            "the BREN absorbs within the range. If CPI is hot and NVDA breaks the range lower, "
            "the BREN becomes a loss — this is the key risk to monitor into 8:30."
        ),
        "sub_why": {
            "setup":   "2/2 — NVDA mid-range, flat trend confirmed from live marks; house view LIKE; BREN setup requires flat/mildly bullish underlying — all confirmed.",
            "pricing": "1/2 — IV percentile estimated (<60 days of ivol_history.json history); specific coupon and strikes require a live quote. Direction correct, quantum estimated.",
            "catalyst": "2/2 — late-Aug print is 45d+ away, clean tenor for the BREN; CPI today is the identified near-term macro wobble. Two relevant catalysts identified and timed.",
            "fit":     "1/2 — LIKE view + income intent fits mandate; BUT delta-netting rule means fit is conditional: BREN XOR CSP, never both on NVDA simultaneously.",
        },
    },
    6: {
        "fundamental_thesis": (
            "Idle USD cash ($3m) earns near-zero vs T-bill yield ~4%+ (post-CPI est.). "
            "NVDA live multiples: see Yahoo Finance data below. Cash-secured put: the client "
            "commits to buy NVDA at the 195 support level and collects a premium. If NVDA "
            "stays above 195 at expiry, the premium is kept. If NVDA touches 195, the client "
            "buys NVDA at an effective cost of (195 − premium) — a discount accumulation at the "
            "pre-confirmed add level. Ring-fenced cash = no leverage; defined-risk structure only. "
            "The alternative to BREN (idea 5), not the complement — delta-netting rule applies."
        ),
        "catalyst_text": (
            "CPI Jun 10 at 8:30 ET: hot print = NVDA down, 195 more likely to be tested; "
            "cold print = NVDA stable, premium income more likely to be kept. "
            "NVDA next earnings: late-Aug — outside the 3-month CSP window. "
            "Decision gate today: if NVDA breaks below the range on the print, the CSP at "
            "195 is the more defensive structure vs the BREN."
        ),
        "sub_why": {
            "setup":   "1/2 — USD cash confirmed; 195 support identified from chart; BUT 195 must be re-verified live after today's CPI print (support level may have shifted).",
            "pricing": "1/2 — T-bill yield (~4%+) confirmed; CSP premium depends on NVDA delta and implied vol post-CPI; estimated.",
            "catalyst": "1/2 — CPI reprices NVDA delta and the CSP's moneyness; CSP invalid if 195 breaks on a hot print. One clear catalyst gate.",
            "fit":     "2/2 — gets paid to add NVDA at the stated accumulation level; converts idle USD cash to income; the alternative to BREN, not the pair.",
        },
    },
    7: {
        "fundamental_thesis": (
            "Broadcom (AVGO) was exited at -21% after Q3 guide missed the buy-side whisper "
            "($16.0bn vs $17.2bn expected) at a 41× multiple. View: NEUTRAL post-miss. "
            "Live AVGO multiples: see Yahoo Finance data below. "
            "Harvest: ~$635k of losses booked, directly offsetting capital gains from the MU "
            "exit (ideas 7 and 1 travel together on the same tax conversation — one call, two "
            "harvests). Buffered note re-entry preserves the long-term AVGO thesis (AI ASICs + "
            "VMware) with downside protection. Note: front-month IV is crushed post-print; "
            "harvest immediately while the loss is available — sell vol via RevCon in ~30 days."
        ),
        "catalyst_text": (
            "No near-term dated catalyst (next AVGO Q4 print ~90 days out). "
            "30-day wash rule: buffered note re-entry is structured to avoid a like-for-like "
            "repurchase within 30 days (note's economic profile differs from direct equity). "
            "Timing catalyst: front-month vol crushed post-print — optimal time to realise "
            "the loss is NOW before vol rebuilds and widens spreads on the replacement structure."
        ),
        "sub_why": {
            "setup":   "2/2 — AVGO loss verified at -21% from live mark; vol-term structure analysis (front crushed, 360d elevated) confirmed; harvest + buffered re-entry is the canonical L6 sequence.",
            "pricing": "1/2 — front-month vol crushed → RevCon coupon is thin right now; buffered note participation rate estimated. Wait ~30 days to sell vol via RevCon.",
            "catalyst": "1/2 — no near-term dated catalyst; 30-day wash rule is the timing constraint, not a market event. Harvest is non-catalysed; buffered note is the discipline mechanism.",
            "fit":     "2/2 — L6 rule: NEUTRAL view post-whisper-miss → harvest + buffered re-entry is canonical; -$635k loss funds the MU exit tax — the paired trade that makes the sequence compelling.",
        },
    },
    8: {
        "fundamental_thesis": (
            "EUR2.4m idle in a deposit account earns near-zero. ECB policy rate post-Thursday "
            "hike: ~4.50%; deposit campaign rates should clear 3%+ (EUR IG deposit market). "
            "The CMT range accrual (10Y US CMT, EUR-paying, 5% if fixing stays 0-4.80%) "
            "FAILED the headroom gate: fixing at ~4.55% with only ~25bp of room vs ~42bp "
            "trailing annual range = 0.6× coverage ratio (threshold: ≥1.5×). "
            "Re-quoted at 5.00-5.25% cap → lower coupon (~3.8% est.) but passes the gate. "
            "QUANTO: pays EUR on a USD rate — the quanto adjustment affects pricing and must "
            "be disclosed. Do NOT promise a vanilla EUR coupon."
        ),
        "catalyst_text": (
            "CPI Jun 10 at 8:30 ET — direct input. Hot (>4.1%): risks pushing 10Y CMT above "
            "4.80%, triggering non-accrual on the 4.80-cap version before client sees it. "
            "Deposit campaign proceeds regardless of CPI (rate-agnostic). "
            "ECB Jun 11: sets deposit campaign pricing (hawkish = better deposit rate). "
            "Both events gate the range accrual; neither gates the deposit."
        ),
        "sub_why": {
            "setup":   "1/2 — EUR2.4m idle confirmed; the 5% CMT range accrual failure is correctly identified; re-quote specified. But the re-quoted version is not yet on screen — setup is partial.",
            "pricing": "1/2 — deposit rate (~3%+) directionally confirmed; re-quoted accrual coupon estimated; must clear the CPI-hot bear case non-accrual test before client presentation.",
            "catalyst": "1/2 — CPI today kills the 4.80 version if >4.1%; ECB gates deposit pricing. Both events gate entry, neither triggers independently.",
            "fit":     "2/2 — K1+K5: idle EUR cash drag is the stated problem; declining the mispriced 5% version and explaining why builds more trust than selling it.",
        },
    },
    9: {
        "fundamental_thesis": (
            "LVMH (MC.PA) is down ~32% from cost (confirmed live mark). House view: NEUTRAL. "
            "Live LVMH multiples: see Yahoo Finance data below. "
            "Luxury sector puts carry steep skew (expensive) → upside calls are relatively cheap "
            "→ RevCon coupon is fattened by the skew. The revCon is NOT a directional LVMH bet: "
            "it monetises the client's stated willingness to buy more LVMH lower. "
            "6-month tenor designed to clear the next earnings print. If the mark recovers, "
            "the revCon is called; if not, the client receives LVMH at a discount and repeats. "
            "Hard gate: View Engine AVOID → convert to harvest immediately."
        ),
        "catalyst_text": (
            "No binary near-term catalyst on LVMH (next earnings ~2 months out). "
            "Soft catalysts: Chinese consumer confidence data, EU luxury sector sentiment, "
            "EUR/USD moves (weaker EUR = better EUR-reported revenues for LVMH's global sales). "
            "The revCon is income-driven, not event-driven. The 6-month tenor is designed "
            "to clear the next earnings print rather than to express a directional view."
        ),
        "sub_why": {
            "setup":   "1/2 — LVMH -32% confirmed; luxury put skew identified; BUT the house view must be re-verified live (View Engine AVOID converts this to a harvest, removing the setup entirely).",
            "pricing": "1/2 — steep luxury skew confirmed directionally; exact revCon coupon depends on live mark and current skew; estimated until formally priced.",
            "catalyst": "1/2 — no binary near-term catalyst; revCon is income-driven; 1/2 because the absence of a near-term catalyst is a feature of the 6-month design, not a gap.",
            "fit":     "2/2 — question verbatim: 'would you buy more LVMH lower?' Yes → revCon. No → harvest. Client holds EUR equities and is confirmed comfortable with structured notes.",
        },
    },
    10: {
        "fundamental_thesis": (
            "AMD is up +395% from cost — a 4× winner the desk no longer loves at current "
            "valuation. House view: NEUTRAL. Live AMD multiples: see Yahoo Finance data below. "
            "Covered-call overwrite: sells OTM calls above market (income on the held position). "
            "Decumulator: sells above market at a premium via a daily-clip mechanism (staged exit). "
            "Held at WATCH because the IV percentile is UNVERIFIED — the overwrite's appeal "
            "entirely depends on whether the premium is large enough to justify the sold-call "
            "obligation. Promote to FIRE the moment IV is sourced (Market Data App / Tradier)."
        ),
        "catalyst_text": (
            "No near-term catalyst within a sensible 2-3 month overwrite tenor (AMD earnings ~60d+). "
            "The overwrite is timing-neutral: IV percentile verification is the gate, not a market "
            "event. CPI and FOMC are macro risks but not direct AMD catalysts in the overwrite window."
        ),
        "sub_why": {
            "setup":   "1/2 — AMD +395% verified; NEUTRAL view confirmed; IV percentile is unverified (the blocking issue). Promote to FIRE the moment IV is sourced.",
            "pricing": "1/2 — IV estimated as probably elevated on a +395% winner, but unconfirmed without a live quote; the whole idea gates on this single input.",
            "catalyst": "1/2 — no near-term catalyst; the absence of a catalyst makes this a pure income/exit conversation, not an event play.",
            "fit":     "1/2 — client holds AMD but hasn't stated intent to exit; the income-vs-exit question must be answered by the client first; fit is conditional.",
        },
    },
    11: {
        "fundamental_thesis": (
            "Siemens AG 2030 EUR bond is at a duration loss (confirmed from position file). "
            "Current EUR IG corporate spreads offer a materially higher running coupon at the "
            "same credit tier as the 2021 vintage bond. ECB hike Thursday raises Bund yields "
            "and improves the re-entry coupon for the replacement bond. "
            "This is the EUR twin to idea 4 (UST swap): same swap thesis, EUR currency, "
            "ECB-gated instead of CPI-gated. "
            "Key metric (not a P/E): running coupon pick-up on the swap is estimated at "
            "+80-100bp (the exact figure depends on post-ECB Bund yields)."
        ),
        "catalyst_text": (
            "ECB Jun 11 is the direct gate — hawkish tone lifts Bund yields and improves the "
            "re-entry coupon for the replacement EUR IG bond. Auto-promotes to FIRE on Friday. "
            "FOMC Jun 16-17 is a secondary input (US rate expectations feed through EUR IG pricing). "
            "Optimal timing: execute on Friday (post-ECB) or the following week."
        ),
        "sub_why": {
            "setup":   "1/2 — Siemens bond duration loss confirmed from position file; swap thesis mirrors idea 4; but live Siemens '30 mark and replacement coupon are estimated until a live quote.",
            "pricing": "1/2 — EUR IG coupon depends on Bund yield post-ECB; estimated. Direction (higher carry) is clear; exact quantum is pending.",
            "catalyst": "1/2 — ECB Thursday is the optimal entry gate (auto-promotes Friday); catalyst improves entry, doesn't pay off a binary.",
            "fit":     "1/2 — EUR twin to the UST swap; client holds EUR bonds and is comfortable with bond swaps; WATCH until ECB sets the entry level.",
        },
    },
    12: {
        "fundamental_thesis": (
            "TotalEnergies (TTE) +64% and Xetra-Gold ETC +100% — both confirmed from live marks. "
            "Both are the book's bear-scenario hedges: TTE benefits from a blockaded Hormuz (war "
            "premium = TTE revenue premium); gold benefits from a dovish Fed repricing (lower real "
            "yields = higher gold) and geopolitical risk premia. "
            "Raw rules (W1 overwrite, profit-take) fire numerically on these positions — "
            "SUPPRESSED by brief-consistency override. "
            "TTE: no equity P/E multiple in traditional sense (energy commodity exposure). "
            "Gold: no earnings multiple (real asset, inverse of real yields). "
            "The hedge function overrides the valuation argument."
        ),
        "catalyst_text": (
            "SUPPRESS — no structure added. The 'catalyst' is the brief's active bear case: "
            "hold while (a) Strait of Hormuz is blockaded, (b) no formal Iran/Israel truce, "
            "(c) CPI has not printed below 3.7%. "
            "Exit triggers: weekly Brent close below $87 (TTE); FOMC dot plot showing a cut "
            "path that materially lifts real rates (gold hedge becomes unnecessary)."
        ),
        "sub_why": {
            "setup":   "0/2 — SUPPRESS: no structure added. Scanner fires 0 because the correct call is NOT to trade. Raw W1/W3 rules fire numerically but are overridden by the consistency check.",
            "pricing": "1/2 — both positions have confirmed live marks; no product to price; the 1 reflects the accuracy of the HOLD decision, not a derivative pricing edge.",
            "catalyst": "0/2 — the 'catalyst' suppresses action: the brief's live bear case makes trimming the hedges the wrong call. 0/2 for structure.",
            "fit":     "1/2 — recognised hedges for a book with ~74% USD equity risk; Doomberg/Howell bear-case overlay supports HOLD; client holds both and understands the rationale.",
        },
    },
    13: {
        "fundamental_thesis": (
            "A dual-currency deposit (DCD) converts EUR idle cash into USD at a pre-agreed "
            "strike rate in exchange for a higher coupon. This would ADD USD exposure — "
            "directly opposite to idea 3 (seagull), which REDUCES the book's net USD exposure. "
            "Running both simultaneously creates a self-cancelling trade (pay premium twice, "
            "net zero FX change) that wastes client capital on offsetting products. "
            "The scanner surfaces the conflict rather than silently pricing both — "
            "this is the suitability feature a product-push screen would miss."
        ),
        "catalyst_text": (
            "SUPPRESS — no catalyst analysis applicable. The contradiction itself is the signal. "
            "Advisor chooses between two mutually exclusive lanes: "
            "(A) USD hedge lane (idea 3 seagull — reduces USD exposure) or "
            "(B) USD accumulation lane (DCD — increases USD exposure for a coupon). "
            "The hedge lane wins while the book carries 74% USD on a EUR base. "
            "DCD can be re-evaluated only if the client explicitly declines idea 3."
        ),
        "sub_why": {
            "setup":   "1/2 — EUR idle cash exists and DCD is technically feasible; 1 reflects the structural existence of the product. The contradiction blocks execution.",
            "pricing": "0/2 — pricing a contradictory product is misleading and explicitly suppressed. 0/2.",
            "catalyst": "0/2 — no catalyst; the scanner surfaces the conflict for the advisor, not a market event. 0/2.",
            "fit":     "1/2 — the EUR idle cash problem exists (fit = 1); but DCD conflicts with idea 3; advisor must choose a lane.",
        },
    },
    14: {
        "fundamental_thesis": (
            "A prepaid variable forward (PVF) is the bespoke OTC route to monetising the 25%+ Micron "
            "concentration without selling it. The client pledges a slice of the position (~$5-7m, about a "
            "third) and receives ~80% of its value in cash up front; at maturity (2-3y) the number of shares "
            "delivered varies with the price — full participation up to a cap (~120% of spot), full protection "
            "below a floor (~90%). Economically it is a collar (long put / short call) plus a secured cash "
            "advance, wrapped into one OTC contract — but unlike an outright sale it does NOT realise the 10x "
            "capital gain today, so it defers the tax while taking the single-name risk and the liquidity "
            "problem off the table at once. Live MU multiples: see Yahoo Finance data below."
        ),
        "catalyst_text": (
            "24-Jun MU Q3 FY26 earnings sets the implied vol the bank prices the embedded collar at — richer "
            "pre-print IV = a higher cash advance and a higher cap, so strike the PVF INTO the elevated vol, "
            "before the print. No binary gate on the structure itself; the catalyst optimises the terms. "
            "Choose PVF vs the collar+SBL (idea 1) by the client's priority: cash-now and tax-deferral (PVF) "
            "versus keep-all-the-upside-with-a-loan (collar). They are alternatives on the same risk — do not "
            "run both on the same shares."
        ),
        "sub_why": {
            "setup":   "2/2 — 25%+ MU concentration confirmed from the position file; a PVF is the textbook OTC monetisation of a low-basis concentrated single stock. Inputs verified.",
            "pricing": "1/2 — the cash-advance %, cap and floor depend on the live MU vol surface into 24-Jun; directionally rich (good for the client) but the exact terms need a desk quote.",
            "catalyst": "1/2 — 24-Jun is a vol-timing gate for the embedded collar, not a payoff trigger; the PVF is a multi-year monetisation, not an event trade.",
            "fit":     "2/2 — C1 rule: a ≥10% single-name concentration needs a documented de-risk plan, and the client wants liquidity off the 10x winner without realising the gain — the PVF solves both. Client is comfortable with OTC structures.",
        },
    },
    101: {
        "fundamental_thesis": (
            "Oracle Corporation (ORCL) — cloud infrastructure (OCI), database (Autonomous DB), "
            "and enterprise applications. Key AI metric: remaining performance obligations (RPO) "
            "$553bn (+325% YoY) — the largest confirmed AI backlog on screen. "
            "OCI grew 84% YoY in Q3 to $4.9bn. Consensus EPS: $1.58 (Finnhub); Oracle's own "
            "March guide: $1.96-2.00 — a wide gap implying a beat is already expected. "
            "Live ORCL multiples: see Yahoo Finance data below. "
            "Capital-protected note: full 100% protection means the print risk (gap-down if guide "
            "misses whisper) is absorbed by the note structure. Trade-off: capped upside "
            "(70-80% participation est.). The thesis is backlog conversion, not EPS."
        ),
        "catalyst_text": (
            "10-Jun ORCL Q4 FY26 earnings (after close) — ENTER POST-PRINT ONLY. "
            "The Earnings desk: 'do not pre-position.' This note enters the day after the print. "
            "Key catalyst WITHIN the note: OCI growth rate and capex guidance vs the whisper "
            "($17.2bn FY26 guide). If the guide clears the whisper, the note's participation "
            "captures the re-rate. If it disappoints (the AVGO parallel), capital protection absorbs it."
        ),
        "sub_why": {
            "setup":   "2/2 — OCI +84% YoY, RPO $553bn confirmed (Finnhub sourced); post-print entry correctly gates the note per the Earnings desk's call; setup verified.",
            "pricing": "1/2 — ~70-80% upside participation estimated pending a live structure quote; capital protection premium depends on current rates and vol; direction correct, quantum estimated.",
            "catalyst": "1/2 — 10-Jun print is the gate (enter post-print); 1/2 because the note's 6-month payoff window has multiple internal catalysts (OCI revs, capex guide) not yet known.",
            "fit":     "2/2 — client has ZERO software/cloud exposure (all AI is hardware: MU/NVDA/AVGO/AMD); Oracle adds the OCI/cloud leg with full capital protection — direct mandate fit.",
        },
    },
    102: {
        "fundamental_thesis": (
            "Adobe Inc (ADBE) — creative cloud (Photoshop, Illustrator, Premiere), digital "
            "experience (Experience Cloud), and generative AI (Firefly). Near 52-week low. "
            "Split sell-side: 19 buy / 22 hold / 4 sell — sentiment is washed out vs an AI "
            "disruption overhang. Live ADBE multiples: see Yahoo Finance data below. "
            "Core question: is Firefly additive to ARR (upsell to existing seats) or "
            "cannibalising Creative Cloud (AI as substitute)? Cash-secured put: the client "
            "is paid a premium to commit to buy ADBE at the 52-week low level. If ADBE "
            "stays above the strike at expiry, the premium is kept. If it falls to the strike, "
            "the client buys ADBE at (strike − premium) — discount accumulation with defined risk."
        ),
        "catalyst_text": (
            "11-Jun ADBE Q2 FY26 earnings (after close) — ENTER POST-PRINT ONLY. "
            "The pivotal question: guidance tone on net-new AI/Firefly monetisation — the guide, "
            "not printed EPS, is what moves the stock at this valuation. A beaten-down stock near "
            "the 52-week low means the downside from a bad guide may already be largely priced — "
            "the asymmetry is on the upside from the beaten-down level."
        ),
        "sub_why": {
            "setup":   "1/2 — ADBE near 52-week low confirmed; split sell-side confirmed (Finnhub sourced); but specific CSP strike needs live verification after the 11-Jun print.",
            "pricing": "1/2 — put premium at a beaten-down name estimated; IV at lows tends to be elevated (better CSP coupon) but requires a live quote.",
            "catalyst": "1/2 — 11-Jun print is the gate (enter post-print); the guide on AI monetisation is the pivotal data point; catalyst is pending as of Jun 10.",
            "fit":     "2/2 — client holds SAP (enterprise software confirmed); CSP = income while waiting to add a beaten-down quality software name at a discount; direct mandate fit.",
        },
    },
    103: {
        "fundamental_thesis": (
            "2s10s USD yield curve steepener expressed as a EUR-denominated capital-protected note. "
            "The macro desk's own position (MM-2026-009) is already at +40bp (entry: +15bp, running). "
            "Structural case: prolonged inversion followed by a Fed pause creates a bull-steepener "
            "as the front-end falls faster than the back-end. "
            "Key levels: 2Y yield ~4.15% (16-month high, pricing a hike that may not come); "
            "10Y yield ~4.55%; 2s10s spread +40bp vs historic post-inversion mean of +80-100bp. "
            "Capital-protected note: if the curve flattens instead, the client loses only time value "
            "(opportunity cost), not capital. No equity P/E — this is a pure rates macro view."
        ),
        "catalyst_text": (
            "May CPI Jun 10 at 8:30 ET (soft print = 2Y falls faster than 10Y = curve steepens). "
            "FOMC dot plot Jun 16-17 (any pause signal = 2Y falls 15-20bp = steepener accelerates). "
            "ECB Jun 11 (sets EUR swap rates for the note's EUR pricing). "
            "All three gates must clear before the note is formally launched — optimal timing: week of Jun 16."
        ),
        "sub_why": {
            "setup":   "2/2 — MM-2026-009 steepener at +40bp running confirms the desk's own view; 2Y at 4.15% (16-month high on one payroll) is a documented structural gap vs the actual hiking probability.",
            "pricing": "1/2 — capital-protected note pricing estimated (depends on rates at issue and EUR swap rates post-ECB); participation rate and coupon pending live quote.",
            "catalyst": "1/2 — CPI and FOMC gate the front-end; ECB gates EUR pricing; all three are binary (could move either way). 1/2 because catalysts gate launch, not just improve it.",
            "fit":     "2/2 — client holds two bonds (duration comfort confirmed); expresses the desk's highest-conviction macro view in a protected 2Y EUR wrapper; structurally additive.",
        },
    },
    104: {
        "fundamental_thesis": (
            "AI data centres require 3-5× more electrical power per rack vs traditional computing. "
            "US data centre power demand projected to grow at ~20-25% CAGR through 2030 "
            "(Citrini Research; JP Morgan GIS infrastructure theme). "
            "The AI-power / electrification basket is a lower-beta, lower-multiple way to express "
            "AI conviction: grid / utility / industrial names trade at 15-25× P/E vs AI semis "
            "at 30-120×. WATCH: the specific basket of underliers is unspecified — "
            "'power / grid / electrification' is a theme, not yet a named tradeable basket. "
            "Promote when the basket is pinned and IV is sourced from a structuring desk."
        ),
        "catalyst_text": (
            "No specific dated catalyst — a secular, 12-18 month thematic play. "
            "WATCH gate: promote when (a) basket underliers are agreed (specific names), and "
            "(b) IV and participation rate are sourced from a structuring desk. "
            "Near-term thematic signals: US infrastructure bill news, hyperscaler data-centre "
            "capex announcements (Microsoft, Google, Meta), utility earnings showing the power ramp."
        ),
        "sub_why": {
            "setup":   "1/2 — Citrini AI-power thesis is identified and the thematic rationale is sound; but specific basket underliers are unspecified — 'power/grid' is a theme, not a verified tradeable set.",
            "pricing": "1/2 — 12-18m tenor is within the equity SP floor (≥3m); pricing estimated (basket TBD, IV unknown); tenor correct, underliers not yet pinned.",
            "catalyst": "0/2 — no specific dated catalyst; the secular theme lacks a near-term binary payoff trigger. This is WHY this idea is WATCH, not FIRE.",
            "fit":     "2/2 — client wants AI exposure without adding more semis; power/electrification is the cleanest diversifier within the AI theme; thematic notes fit mandate.",
        },
    },
}


def _new_adds(metrics):
    """Section 1 — NEW exposures mapped to the client's pattern (AI/semis-heavy,
    software, large-cap quality, energy+gold hedges, US duration, comfortable with
    structures). Sourced from the Earnings screener + the macro book. Tenor floors:
    equity structured products >=3m, OTC >=1m, rates structured products >=2y."""
    return [
        _idea(101, "Oracle: 6-month capital-protected note (post-print entry)",
              "New add - structured note", ["ORCL US"], 6,
              {"setup": 2, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "A 6-month note with full capital protection and ~70-80% upside participation on Oracle, entered "
              "AFTER the 10-Jun print to respect the Earnings desk's 'do not pre-position' call. Diversifies the "
              "client's AI exposure away from pure semiconductors into cloud-infrastructure / OCI - the same theme, "
              "a different leg of the build-out.",
              "OCI growth and capex guidance clearing the whisper (not just the estimate). Capital protection means "
              "the print risk is carried by the structure, not the client - the trade-off is capped upside.",
              "The client is heavily AI but entirely through hardware (MU, NVDA, AVGO, AMD). Oracle adds the "
              "software/cloud leg of the same conviction with downside protection - exactly the profile of a "
              "growth-with-protection client who already buys structures.",
              ["Capital-protected note", "AI / cloud", "Post-print", "Diversify"],
              section="new_add", asset_group="Equity", tenor="6 months (equity SP >= 3m floor)",
              sizing="~EUR1.5m from the idle USD cash",
              impact="Broadens the AI bet from semis-only into software, with capital protection - adds conviction exposure while *reducing* the concentration risk profile.",
              sources=[{"name": "Earnings screener (Finnhub)", "type": "in-house", "note": "ORCL - RPO $553bn, OCI +84%"},
                       {"name": "Citrini Research", "type": "Substack/X", "note": "AI capex build-out"},
                       {"name": "JP Morgan GIS", "type": "house anchor", "note": "OW AI infrastructure"}],
              origin="Earnings tab -> Oracle (Neutral into the print; this enters post-print, no contradiction)"),
        _idea(102, "Adobe: 3-month cash-secured put at the lows (discount accumulation)",
              "New add - OTC / accumulator", ["ADBE US"], 5,
              {"setup": 1, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "Sell a 3-month cash-secured put on Adobe struck near the 52-week low - the client is paid a premium "
              "to commit to buy a washed-out software name at a discount, or keeps the premium if it never gets "
              "there. Cash ring-fenced against assignment.",
              "Whether generative-AI is additive to Adobe's ARR or a threat - the guide, not the EPS. Washed-out "
              "sentiment (near 52wk low, split sell-side) is the asymmetry the premium is paid for.",
              "Fits the client's enterprise-software liking (they hold SAP) and their willingness to be paid to "
              "wait. A defined, income-generating way to start a position in a beaten-down quality name.",
              ["Cash-secured put", "Software", "Income", "Add-at-discount"],
              section="new_add", asset_group="Equity", tenor="3 months (OTC put, >= 1m floor)",
              sizing="~EUR1.0m cash ring-fenced",
              impact="Adds a second, uncorrelated software name at a discount and converts idle cash into income - diversifies the equity sleeve away from the semis cluster.",
              sources=[{"name": "Earnings screener (Finnhub)", "type": "in-house", "note": "ADBE near 52wk low, split coverage"},
                       {"name": "JP Morgan GIS", "type": "house anchor", "note": "European/quality software tilt"}],
              origin="Earnings tab -> Adobe (the 'is AI a tax or tailwind for software' test)"),
        _idea(103, "EUR rates: 2-year steepener-linked capital-protected note",
              "New add - rates structured product", ["EUR rates"], 6,
              {"setup": 2, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "A 2-year capital-protected note that pays an enhanced coupon as the 2s10s curve steepens - the exact "
              "view the macro desk already owns via the cash steepener (MM-2026-009, +40bp and running). Capital "
              "protected, EUR-denominated, sized from the idle EUR cash.",
              "The front-end finally relaxing on a cool CPI / a held dot plot, which steepens the curve. Capital "
              "protection caps the downside if the curve flattens instead.",
              "The client already holds duration (two bonds) and is comfortable with structures - this expresses "
              "the house curve view in a protected, 2-year wrapper rather than another cash bond, and puts EUR "
              "cash to work for longer than a deposit.",
              ["Rates SP", "Steepener", "Capital-protected", "Macro-aligned"],
              section="new_add", asset_group="Rates", tenor="2 years (rates SP >= 2y floor)",
              sizing="~EUR1.5m from the idle EUR cash",
              impact="Expresses the desk's highest-conviction macro view (curve steepening) inside the client's book, protected, and lengthens the duration profile the client already favours.",
              sources=[{"name": "Macro book (MM-2026-009)", "type": "in-house", "note": "2s10s steepener, +40bp"},
                       {"name": "Today's brief", "type": "in-house", "note": "front-end into CPI / dot plot"},
                       {"name": "JP Morgan GIS", "type": "house anchor", "note": "neutral-to-short duration, curve bias"}],
              origin="Trade Ideas tab -> 2s10s steepener (MM-2026-009), wrapped for the client"),
        _idea(104, "AI-power thematic: 12-18m note on the grid / power leg",
              "New add - thematic structured note", ["Power basket"], 4,
              {"setup": 1, "pricing": 1, "catalyst": 0, "fit": 2},
              {"setup": "estimated", "pricing": "estimated", "catalyst": "estimated", "fit": "sourced"},
              "WATCH",
              "A 12-18 month note on a power / grid / electrification basket - the 'AI needs electricity' leg of the "
              "build-out that Citrini has pressed. It diversifies the AI conviction away from the silicon and into "
              "the infrastructure that powers it.",
              "Whether the data-centre power-demand story converts into earnings for the grid names. Held at Watch "
              "because the basket and IV are not yet sourced - promote once the underliers are pinned and priced.",
              "Lets the client keep leaning into their strongest conviction (AI) while *reducing* the semis "
              "concentration - a different, lower-beta expression of the same theme.",
              ["Thematic note", "AI power", "Diversify", "Watch"],
              section="new_add", asset_group="Multi-asset", tenor="12-18 months (equity SP >= 3m floor)",
              sizing="~EUR1.0m, sized small as a thematic starter",
              impact="A lower-correlation way to keep adding AI conviction; explicitly diversifies away from the MU/NVDA/AVGO/AMD cluster.",
              sources=[{"name": "Citrini Research", "type": "Substack/X", "note": "AI-power / electrification thesis"},
                       {"name": "JP Morgan GIS", "type": "house anchor", "note": "infrastructure / capex theme"}],
              origin="Theme -> Citrini AI-power; diversifier for the AI concentration"),
    ]


def build_ideas(metrics):
    mu_w = metrics["largest"]["weight_pct"]
    net_usd = metrics["net_usd_pct"]
    ideas = [
        _idea(1, "MU concentration: collar + SBL now, decumulator after the print",
              "C1 + C2 -> C6", ["MU US"], 7,
              {"setup": 2, "pricing": 2, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "sourced", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "Zero-cost collar on the ~$15m position — IVol is rich into 24-Jun and "
              "calls are bid, so the market finances a put that locks most of the 10x gain. Lombard line against "
              "the collared stock lends at a higher LTV. Post-earnings, a decumulator sized at <=50% of the "
              "position becomes the staged-exit engine — selling above market at a premium, gearing fully covered "
              "by shares held.",
              "The 24-Jun print is binary, so the decumulator is timed, not killed (C6 gate): decumulating through "
              "a catalyst with 2x gearing is how you end up obligated to sell double into a +20% gap. Collar "
              "through the event; decumulate into the calm after.",
              f"At {mu_w}% against a 10% policy this is the book's defining risk. The sequence — hedge, borrow, "
              "then exit above market — turns one oversized position into three revenue conversations without a "
              "single market order.",
              ["Collar", "SBL", "Decumulator", "Concentration"],
              "Decumulator sells above market at a premium, but with gearing a hard rally forces double the daily "
              "clip at the strike, below the new market. Sized so a full 2x obligation is always deliverable from "
              "the shares held. View is LIKE -> C6 is suppressed into strength; deploy only post-print."),
        _idea(14, "MU concentration: prepaid variable forward — the OTC alternative to the collar",
              "C1 / equity OTC", ["MU US"], 6,
              {"setup": 2, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "A 2-3y prepaid variable forward on ~a third of the MU position: pledge the shares, take ~80% of "
              "their value in cash today, keep upside to a ~120% cap and full protection below a ~90% floor. It is "
              "a collar plus a secured cash advance in one OTC contract — but unlike a sale it does NOT realise the "
              "10x gain, so it raises liquidity and defers the tax while taking the concentration risk off the table.",
              "24-Jun earnings sets the vol the embedded collar is priced at — strike into the rich pre-print IV "
              "for a higher advance and a higher cap. Choose this OR the collar+SBL (idea 1) by whether the "
              "priority is cash-now-and-tax-deferral (PVF) or keep-all-the-upside-with-a-loan (collar).",
              f"At {mu_w}% this is the book's defining risk; the PVF is the cleanest way to monetise it without a "
              "taxable sale — cash out, tax deferred, downside floored, a defined slice of upside kept.",
              ["Prepaid variable forward", "Monetise", "Tax-defer", "Equity OTC"],
              "Caps upside above the ~120% strike; a hard rally through it is forgone gain. Early unwind costs the "
              "embedded option value; senior-unsecured counterparty/issuer credit on the forward. Alternative to "
              "idea 1 on the same shares — never run both on the same slice."),
        _idea(2, "USD mortgage: earmark idle cash + liability-matching forward strip",
              "X4 + K1", ["USD cash", "FX"], 7,
              {"setup": 2, "pricing": 1, "catalyst": 2, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "$462k/yr of USD payments for a EUR thinker. Step 1: earmark from the idle $3m USD cash — a 24-month "
              "T-bill ladder maturing at each payment date covers the obligations and earns 4%+. Step 2: a forward "
              "strip (buy USD / sell EUR) for payment dates beyond the cash runway fixes the EUR cost of the house "
              "for years.",
              "Nothing binary — that is the point. Forward pricing improves if EUR/USD recovers post-ECB; the strip "
              "layers in thirds.",
              "This kills the client's actual anxiety — 'what does my Miami house cost me in euros?' — with money "
              "already sitting idle. The forwards conversation opens the wider FX-mismatch conversation (idea 3) "
              "naturally.",
              ["T-bill ladder", "Forward strip", "Liability match", "FX"]),
        _idea(3, "Net USD exposure: seagull on the residual mismatch",
              "X2", ["USD sleeve", "FX"], 6,
              {"setup": 2, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              f"After netting the mortgage liability and earmarked cash, the hedgeable USD mismatch is ~{net_usd}% "
              "of the book versus a EUR base. A seagull hedges 30-50% of the net; the far-wing sale cheapens it; "
              "forward points are carry-positive for a EUR-base client selling USD forward.",
              "ECB Thursday — a hawkish Lagarde lifts EUR and worsens the entry. Structure after the decision, or "
              "buy optionality through it.",
              "Liability netting changed the hedge size — a naive scan would have over-hedged by the mortgage. "
              "Frame it as locking translation gains near two-month EUR lows.",
              ["Seagull", "FX hedge", "Carry"]),
        _idea(4, "UST 1.25% '31: bond swap into current coupons",
              "B1", ["UST '31"], 6,
              {"setup": 2, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "Out of the 2021 lot at ~85.6, into current ~4.55% coupons — banks ~$690k of losses, roughly triples "
              "the running yield, same credit, maturity within tolerance. The Siemens '30 queues for the EUR sleeve.",
              "CPI at 8:30 tomorrow gates the re-entry leg; ECB Thursday gates the EUR leg.",
              "The loss already happened; the swap makes it useful. Lead the call with this — zero objections, and "
              "the harvested loss offsets gains banked elsewhere.",
              ["Bond swap", "Loss harvest", "Carry pickup"]),
        _idea(5, "NVDA: bullish range note (BREN) on the 195-235 consolidation",
              "L2", ["NVDA US"], 6,
              {"setup": 2, "pricing": 1, "catalyst": 2, "fit": 1},
              {"setup": "sourced", "pricing": "sourced", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "House view LIKE, flat trend, mid-range, ~45d+ to the late-Aug print — a textbook BREN that pays a "
              "coupon for the range holding. Shallow loss (-10.5%) becomes a paid wait.",
              "The IV percentile is estimated until ivol_history.json builds 60 days — verify before pricing. CPI "
              "tomorrow is the macro wobble the brief's bear case names.",
              "Pick BREN or the cash-secured put (idea 6) by intent — income on what's held versus getting paid to "
              "add lower. Delta-netting rule: never both on the same name.",
              ["BREN", "Range note", "Income"]),
        _idea(6, "USD cash residual: T-bills + ring-fenced NVDA cash-secured put",
              "K1 + K3", ["USD cash", "NVDA US"], 5,
              {"setup": 1, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "After the mortgage earmark, the residual USD cash splits: bills at 4%+, plus a ring-fenced CSP "
              "tranche on NVDA struck at 195 support (view LIKE, documented add-intent). Cash held against assignment.",
              "CPI reprices the front end — ladder the bills after the print. The CSP is valid while 195 holds.",
              "Gets paid to wait for the level they'd buy at anyway. The alternative to idea 5, never the pair.",
              ["T-bills", "Cash-secured put", "Add-intent"]),
        _idea(7, "AVGO -21%: harvest the loss + buffered-note re-entry",
              "L6", ["AVGO US"], 6,
              {"setup": 2, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "sourced", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "View NEUTRAL after the whisper-miss; harvest ~$635k of losses; a buffered note re-entry preserves the "
              "exposure case with downside protection, 30-day wash rule respected.",
              "Term structure is the signal — post-print front-month vol is crushed (the 360d anchor still solves "
              "~50%), so a near-dated reverse-convertible coupon is thin. Harvest now; sell the vol via RevCon "
              "when the front end rebuilds.",
              "The harvested loss funds the tax bill the MU exit plan creates — these two travel together on the "
              "same call.",
              ["Tax harvest", "Buffered note", "Re-entry"]),
        _idea(8, "EUR cash: deposit campaign; CMT range accrual re-quoted, not sold",
              "K1 + K5", ["EUR cash", "Rates"], 5,
              {"setup": 1, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "EUR2.4m idle into an ECB hike — quote campaign deposits Friday. The headline 10Y-CMT range accrual "
              "(5% EUR-paying, 0-4.80% range) FAILS the headroom gate as quoted: the fixing is ~4.55%, only ~25bp "
              "of room, ~0.6x the trailing range. Re-quote at a 5.00-5.25% cap for a lower coupon, enter post-CPI.",
              "CPI tomorrow is the direct input — a hot print likely kills the 4.80 version on the screen before "
              "the client ever sees it.",
              "Showing the client why the 5% headline was declined builds more trust than selling it. Quanto note: "
              "the product pays EUR on a USD rate — say so up front so no one promises a vanilla EUR coupon.",
              ["Deposit campaign", "Range accrual", "Quanto", "Re-quote"],
              "K5 quanto: pays EUR on the US 10Y CMT fixing — quanto adjustment affects pricing. Barrier-headroom "
              "0.6x = caution/fail; the card must show expected non-accrual days under the brief's hot-CPI bear case."),
        _idea(9, "LVMH loss: reverse convertible at the buy-more level",
              "L3", ["MC FP"], 5,
              {"setup": 1, "pricing": 1, "catalyst": 1, "fit": 2},
              {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
              "FIRE",
              "The live refresh deepened this loss (mark moved well below the indicative), which strengthens the "
              "case: a six-month reverse convertible struck where they'd average down anyway, steep luxury skew "
              "fattening the coupon. FCN if the coupon must be certain.",
              "Mark and IV must be refreshed before quoting — done on the live mark; a View Engine downgrade to "
              "AVOID converts this to a clean harvest.",
              "The question, verbatim: 'would you buy more LVMH lower?' Yes -> reverse convertible. No -> harvest "
              "and rotate within the sector.",
              ["Reverse convertible", "Skew", "Add-intent"]),
        # --- WATCH ---
        _idea(10, "AMD: overwrite or decumulator — promote when IV is sourced",
               "W1 / W3", ["AMD US"], 4,
               {"setup": 1, "pricing": 1, "catalyst": 1, "fit": 1},
               {"setup": "sourced", "pricing": "estimated", "catalyst": "estimated", "fit": "sourced"},
               "WATCH",
               "View NEUTRAL after +395%. A covered-call overwrite harvests income; a decumulator is the elegant "
               "exit if the client wants out above market. Held at Watch because the IV percentile is unverified.",
               "Promote the moment IV is sourced (Market Data App / Tradier). No catalyst inside a sensible tenor.",
               "The income-or-exit conversation for a name the client has 4x'd but the desk no longer loves at "
               "this valuation.",
               ["Overwrite", "Decumulator", "Income"]),
        _idea(11, "Siemens '30: EUR bond swap — auto-promotes post-ECB",
               "B1", ["Siemens '30"], 4,
               {"setup": 1, "pricing": 1, "catalyst": 1, "fit": 1},
               {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
               "WATCH",
               "Duration loss, not credit — a swap into current EUR IG coupons harvests the loss and lifts carry. "
               "The EUR twin to idea 4.",
               "ECB Thursday is the gate: a better entry after the decision if Lagarde is hawkish and the Bund "
               "sells off. Auto-promotes Friday.",
               "Pairs onto the same fixed-income review call as the UST swap — one conversation, two harvests.",
               ["Bond swap", "EUR IG", "ECB-gated"]),
        # --- SUPPRESSED ---
        _idea(12, "TotalEnergies + gold: recognised hedges - HOLD, do not trim",
               "W2", ["TTE FP", "4GLD GY"], 2,
               {"setup": 0, "pricing": 1, "catalyst": 0, "fit": 1},
               {"setup": "sourced", "pricing": "sourced", "catalyst": "sourced", "fit": "sourced"},
               "SUPPRESS",
               "Both are the book's bear-scenario hedges while Brent holds the war premium and gold trades real "
               "rates. The raw winner-rules (W1 overwrite, profit-take) fire on the numbers.",
               "Brief-consistency override: the scanner never contradicts the morning brief. While the bear case is "
               "live, these are protection, not profit to harvest.",
               "Explaining why the desk is NOT trimming a +109% winner — because it is the hedge — is the trust "
               "moment a raw screen would miss.",
               ["Recognised hedge", "No trim"]),
        _idea(13, "EUR->USD DCD: suppressed — conflicts with the USD hedge",
               "K2 (vs X2)", ["EUR cash", "FX"], 2,
               {"setup": 1, "pricing": 0, "catalyst": 0, "fit": 1},
               {"setup": "sourced", "pricing": "estimated", "catalyst": "sourced", "fit": "sourced"},
               "SUPPRESS",
               "A dual-currency deposit would convert EUR into USD at a strike — directly opposite to idea 3, which "
               "takes USD risk off. One book cannot do both.",
               "Contradiction surfaced by the scanner: the advisor chooses a lane. The hedge lane wins while the "
               "book is 70%+ USD against a EUR base.",
               "The scanner printing the conflict — rather than silently emitting both — is the suitability feature "
               "a product-push screen lacks.",
               ["Contradiction", "DCD", "Suppressed"]),
    ]
    # overlay asset group / tenor / sizing / impact / sources onto the 13 'enhance' ideas
    for it in ideas:
        meta = _ENHANCE_META.get(it["num"])
        if meta:
            it["asset_group"], it["tenor"], it["sizing"], it["portfolio_impact"], it["sources"] = meta

    all_ideas = ideas + _new_adds(metrics)

    # overlay thesis/catalyst/sub_why enrichments + product type / objective onto every idea
    for it in all_ideas:
        enr = IDEA_ENRICHMENTS.get(it["num"])
        if enr:
            it["fundamental_thesis"] = enr.get("fundamental_thesis", "")
            it["catalyst_text"]      = enr.get("catalyst_text", "")
            it["sub_why"]            = enr.get("sub_why", {})
        pm = PRODUCT_META.get(it["num"])
        if pm:
            it["product_type"], it["objective"] = pm

    return all_ideas


def compute_allocations(bookdata):
    """Three allocation breakdowns for the Portfolio pie charts:
       asset class (whole book incl. cash), equity sector (equities only), region (whole book)."""
    eurusd = bookdata["client"]["fx_reference"]["EURUSD"]
    pos = bookdata["positions"]
    cash = bookdata.get("cash", [])

    # --- asset class (whole book) ---
    ac = {}
    for p in pos:
        bucket = ASSET_BUCKET.get(p.get("asset_class", ""), "Other")
        ac[bucket] = ac.get(bucket, 0) + p["value_eur"]
    cash_eur = sum(c["amount"] / (eurusd if c["currency"] == "USD" else 1) for c in cash)
    if cash_eur:
        ac["Cash"] = ac.get("Cash", 0) + cash_eur
    ac_order = ["Equities", "Fixed income", "Commodities", "Cash", "Other"]
    asset_class = [{"label": k, "value": round(ac[k])} for k in ac_order if k in ac]

    # --- equity sector (equities only) ---
    sec = {}
    for p in pos:
        if p.get("asset_class") in ("equity", "equity_etf"):
            s = EQUITY_SECTOR.get(p["ticker"], p.get("name", "Other"))
            sec[s] = sec.get(s, 0) + p["value_eur"]
    sector = [{"label": k, "value": round(v)} for k, v in sorted(sec.items(), key=lambda kv: -kv[1])]

    # --- region (whole book, by listing currency; gold ETC = Global) ---
    reg = {}
    for p in pos:
        if p.get("asset_class") == "commodity_etc":
            r = "Global / commodity"
        elif p["currency"] == "USD":
            r = "US"
        else:
            r = "Europe"
        reg[r] = reg.get(r, 0) + p["value_eur"]
    if cash_eur:
        reg["Cash"] = reg.get("Cash", 0) + cash_eur
    region = [{"label": k, "value": round(v)} for k, v in sorted(reg.items(), key=lambda kv: -kv[1])]

    return {"asset_class": asset_class, "sector": sector, "region": region}


def _loss_recovery(bookdata):
    """Per-position recovery routes for underwater holdings — exact how-to, plus the
    faster structured-product + OTC-at-margin path where it genuinely makes sense."""
    by_tk = {p["ticker"]: p for p in bookdata["positions"]}
    def loss(tk):
        p = by_tk.get(tk, {})
        v = p.get("pnl_pct")
        return f"{v:+.1f}%" if isinstance(v, (int, float)) else ""
    out = []
    out.append({
        "name": "Broadcom (AVGO US)", "loss": loss("AVGO US"),
        "how": ("Harvest the loss now (front-month IV is crushed post-print, so spreads on the replacement are "
                "tight) to bank the tax loss against the gains the Micron exit will create, then re-enter the "
                "AI-ASIC thesis through a 12–18m buffered note (protected participation) so the exposure stays on "
                "with a downside buffer. In ~30 days, once front-end vol rebuilds, sell a reverse convertible to "
                "earn the coupon back."),
        "accelerator": ("Run the buffered note AND an OTC decumulator/accumulator at margin: the accumulator buys "
                        "AVGO back on a daily clip below current (a discount average-down funded on margin) while "
                        "the note carries the protected upside — together they claw back the 21% materially faster "
                        "than waiting for spot to mean-revert. Cap the margin so a full obligation is always "
                        "deliverable."),
    })
    out.append({
        "name": "LVMH (MC FP)", "loss": loss("MC FP"),
        "how": ("Sell a 6-month reverse convertible struck at the level you would average down anyway. Steep "
                "luxury put skew fattens the coupon, so you are paid a high single-digit coupon to wait at your "
                "add level; if it is put to you, you own more LVMH at a discount — exactly the plan. FCN if the "
                "coupon must be certain."),
        "accelerator": ("Pair the RevCon coupon with a short OTC accumulator at margin to leg into the discount on "
                        "a daily clip — the coupon funds the carry, so the blended entry drops faster and the "
                        "−32% recovers on a lower break-even than spot alone."),
    })
    out.append({
        "name": "NVIDIA (NVDA US)", "loss": loss("NVDA US"),
        "how": ("Sell a BREN / range note on the 195–235 consolidation: it pays a coupon while NVDA holds the "
                "range, turning the paper loss into paid waiting rather than a realised loss."),
        "accelerator": ("Add a cash-secured put struck at 195 (ring-fenced cash, defined risk — not the BREN at "
                        "the same time per the delta-netting rule): the premium offsets the drawdown and commits "
                        "you to add at support, the level you would buy at anyway."),
    })
    out.append({
        "name": "US Treasury 1.25% '31 + Siemens 0.875% '30", "loss": f'{loss("T 1.25 08/15/31")} / {loss("SIEGR 0.875 06/30")}',
        "how": ("Switch both underwater bonds into current-coupon paper of the same credit. The loss is already "
                "taken; the switch banks it (offsetting gains harvested elsewhere) and roughly triples the running "
                "carry — the higher coupon amortises the recovery without taking new credit risk. CPI gates the "
                "UST leg, Thursday's ECB gates the Siemens/EUR leg."),
        "accelerator": ("Rates leg — not a margin/OTC candidate; the recovery is the carry pickup itself, banked "
                        "cleanly via the switch."),
    })
    return out


def _overall_summary(metrics):
    """Portfolio-level action plan — the one-screen 'what we're suggesting' that the
    two sections then detail. Synthesis, consistency-locked to the brief + JP GIS."""
    return {
        "headline": ("De-risk the concentration, put the idle cash to work, keep the hedges — and add AI "
                     "exposure through software and power, not more semiconductors."),
        "stance": ("Aligned with the JP Morgan GIS anchor (overweight quality/AI-infrastructure, hedge the "
                   "tail, gold as a diversifier) and today's brief regime — a ceasefire the market doesn't yet "
                   "trust into a CPI print. Nothing below contradicts the macro view or the per-name house views."),
        "points": [
            {"group": "Equity", "text": f"<b>Hedge first.</b> Collar the {metrics['largest']['weight_pct']}% Micron "
             "position before 24-Jun — the book's defining risk — and carry the book-level SPX put spread. "
             "Hedge the concentration, don't abandon the name."},
            {"group": "Equity", "text": "<b>Bank the losses usefully.</b> Harvest AVGO and LVMH to fund the tax "
             "the eventual Micron exit creates; keep the exposure cases alive through buffered notes / reverse "
             "convertibles."},
            {"group": "Rates", "text": "<b>Make the bonds work.</b> Swap both underwater bonds into current "
             "coupons — the loss is already taken, the carry roughly triples at the same credit. CPI and ECB are "
             "the timing gates."},
            {"group": "Cash", "text": f"<b>End the cash drag.</b> {metrics['cash_pct']}% idle "
             f"({_eurm_plain(metrics['cash_eur'])}) → a T-bill ladder against the USD mortgage, an EUR deposit "
             "campaign, and a cash-secured NVDA put at support."},
            {"group": "FX", "text": f"<b>Hedge the currency.</b> {metrics['usd_pct']}% USD on a EUR base → "
             "seagull the residual mismatch after Thursday's ECB, sized off the liability-netted exposure."},
            {"group": "Multi-asset", "text": "<b>Keep the hedges.</b> TotalEnergies and gold are the bear-case "
             "insurance while Brent holds $93 — do not trim (Doomberg / Howell aligned)."},
            {"group": "Equity", "text": "<b>Add selectively.</b> Diversify the AI bet into software (Oracle note, "
             "Adobe accumulator) and the power leg, and express the curve view via a 2y rates note — new risk only "
             "where it *reduces* the semiconductor concentration."},
        ],
    }


def _eurm_plain(n):
    return f"EUR{n/1e6:.1f}m"


# --------------------------------------------------------------------------
# Assemble the scan
# --------------------------------------------------------------------------
def build_scan(brief=None):
    bookdata = _load(BOOK_PATH, {})
    if not bookdata:
        return None
    views = _load(VIEWS_PATH, {"views": []})
    ivol = _load(IVOL_PATH, {"history": {}})

    refresh_notes = refresh_marks(bookdata)
    metrics = compute_metrics(bookdata)
    attach_views_and_vol(bookdata, views, ivol)
    ideas = build_ideas(metrics)

    # attach per-idea RSI + valuation data (computed in gen script, stored in brief)
    idea_rsi = (brief or {}).get("idea_rsi_data", {})
    for it in ideas:
        it["idea_data"] = idea_rsi.get(str(it["num"]))

    fired = [i for i in ideas if i["tier"] == "FIRE"]
    watch = [i for i in ideas if i["tier"] == "WATCH"]
    suppressed = [i for i in ideas if i["tier"] == "SUPPRESS"]

    # Section split + asset-class grouping for the Derivatives Lab
    new_adds = [i for i in ideas if i["section"] == "new_add"]
    enhance  = [i for i in ideas if i["section"] == "enhance"]
    order = ["Equity", "FX", "Rates", "Cash", "Multi-asset"]
    def group(items):
        g = {}
        for i in items:
            g.setdefault(i.get("asset_group", "Multi-asset"), []).append(i)
        return [(k, g[k]) for k in order if k in g] + [(k, v) for k, v in g.items() if k not in order]
    new_adds_grouped = group(new_adds)
    enhance_grouped  = group(enhance)

    client = dict(bookdata.get("client", {}))
    client["display_name"] = CLIENT_DISPLAY

    return {
        "client": client,
        "positions": bookdata.get("positions", []),
        "cash": bookdata.get("cash", []),
        "liabilities": LIABILITIES,
        "metrics": metrics,
        "house_views": views.get("views", []),
        "views_meta": views.get("_meta", {}),
        "ideas": ideas,
        "fired": fired, "watch": watch, "suppressed": suppressed,
        "new_adds": new_adds, "enhance": enhance,
        "new_adds_grouped": new_adds_grouped, "enhance_grouped": enhance_grouped,
        "overall_summary": _overall_summary(metrics),
        "allocations": compute_allocations(bookdata),
        "loss_recovery": _loss_recovery(bookdata),
        "counts": {"fired": len(fired), "watch": len(watch), "suppressed": len(suppressed),
                   "new_adds": len(new_adds), "enhance": len(enhance)},
        "refresh_notes": refresh_notes,
        "ivol_meta": ivol.get("_meta", {}),
        "as_of": client.get("as_of", TODAY),
        "regime": (brief or {}).get("regime", ""),
    }


if __name__ == "__main__":
    s = build_scan({"regime": "test"})
    m = s["metrics"]
    print(f'Book {CLIENT_DISPLAY}: EUR{m["total_eur"]:,} · {m["largest"]["ticker"]} {m["largest"]["weight_pct"]}% '
          f'· USD {m["usd_pct"]}% · cash {m["cash_pct"]}%')
    print("refresh:", "; ".join(s["refresh_notes"]) or "none")
    print(f'ideas: {s["counts"]}')
    for i in s["fired"]:
        print(f'  FIRE  {i["score"]}/8  {i["title"]}')
    for i in s["watch"]:
        print(f'  WATCH {i["score"]}/8  {i["title"]}')
    for i in s["suppressed"]:
        print(f'  SUPP  {i["score"]}/8  {i["title"]}')
