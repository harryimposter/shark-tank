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
    return ideas + _new_adds(metrics)


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
