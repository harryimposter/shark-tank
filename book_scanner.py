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
        tier, _ = _conc_flag(p.get("weight_pct", 0), p.get("asset_class", ""))
        p["conc_tier"] = tier


# --------------------------------------------------------------------------
# The idea shelf — authored per the ruleset, scored /8 (Section 7).
# Each: tier FIRE/WATCH/SUPPRESS · subscores sum to score · sourced/estimated flags.
# --------------------------------------------------------------------------
def _idea(num, title, rules, tickers, score, subs, sub_src, tier, what, moves, client, tags, risk=None):
    return {"num": num, "title": title, "rules": rules, "tickers": tickers,
            "score": score, "subs": subs, "sub_src": sub_src, "tier": tier,
            "what_it_is": what, "what_moves_it": moves, "client_note": client,
            "tags": tags, "risk": risk}


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
    return ideas


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
        "counts": {"fired": len(fired), "watch": len(watch), "suppressed": len(suppressed)},
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
