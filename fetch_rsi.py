#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_rsi.py — 1-month RSI positioning check for open trades (stdlib only).

Fetches 3 months of daily closes from Yahoo Finance for each instrument,
computes 14-period RSI, then measures the current RSI versus its 21-session
(~1-month) trailing mean and std-dev.

Verdict:
  CROWDED_HIGH  RSI > mean + 1 SD  (overbought; reduces conviction if we're long)
  CROWDED_LOW   RSI < mean - 1 SD  (oversold; reduces conviction if we're short)
  NEUTRAL       within ± 1 SD

Returns None for any instrument where the data can't be fetched.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Trade-id -> (yahoo_ticker, direction_note)
# direction_note: "long" or "short" — affects whether overbought/oversold is bearish
TRADE_TICKERS = {
    "MM-2026-001": ("EURAUD=X",  "short",  "EUR/AUD cross (EURAUD=X)"),
    "MM-2026-002": ("BZ=F",      "long",   "Brent crude front month (BZ=F)"),
    "MM-2026-003": ("BZ=F",      "long",   "Brent crude as spread proxy (BZ=F)"),
    "MM-2026-004": ("^TNX",      "short",  "US 10Y yield (^TNX); short yield = long duration"),
    "MM-2026-005": ("GC=F",      "long",   "Gold futures (GC=F)"),
    "MM-2026-007": ("JPY=X",     "short",  "USD/JPY (JPY=X); short USDJPY"),
    "MM-2026-008": ("^GSPC",     "long",   "S&P 500 index underlying (^GSPC); long put spread = short underlying"),
    "MM-2026-009": ("^TNX",      "long",   "10Y yield proxy for steepener; full spread RSI not directly available"),
    "MM-2026-010": ("^GDAXI",    "long",   "DAX index (^GDAXI); ratio RSI requires both legs"),
    "MM-2026-011": ("BZ=F",      "long",   "Brent crude underlying for call spread (BZ=F)"),
    "MM-2026-012": ("EURUSD=X",  "short",  "EUR/USD (EURUSD=X); short EUR"),
    "MM-2026-013": ("^IRX",      "short",  "13-week T-bill rate as 2Y proxy (^IRX)"),
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research/1.0)"}


def _fetch_closes(ticker, timeout=15):
    """Fetch ~3 months of daily closing prices from Yahoo Finance."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?range=3mo&interval=1d&includePrePost=false")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        result = (data.get("chart", {}).get("result") or [None])[0]
        if not result:
            return None
        closes = result["indicators"]["quote"][0].get("close", [])
        # strip None values
        closes = [c for c in closes if c is not None]
        return closes if len(closes) >= 20 else None
    except Exception:
        return None


def _rsi_series(closes, period=14):
    """Return list of RSI values (same length as closes, padded with None at start)."""
    if len(closes) < period + 1:
        return []
    deltas = [closes[i+1] - closes[i] for i in range(len(closes) - 1)]
    gains  = [max(0.0,  d) for d in deltas]
    losses = [max(0.0, -d) for d in deltas]

    # Wilder smoothing seed
    avg_g = sum(gains[:period])  / period
    avg_l = sum(losses[:period]) / period
    rsi = []
    for i in range(period, len(deltas)):
        avg_g = (avg_g * (period - 1) + gains[i])  / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
        rs    = avg_g / avg_l if avg_l > 0 else 100.0
        rsi.append(100.0 - 100.0 / (1.0 + rs))
    return rsi


def _analyse(yahoo_tk, direction, note):
    """Core RSI analysis for any (ticker, direction, note) triple."""
    closes = _fetch_closes(yahoo_tk)
    if not closes:
        return {"ticker": yahoo_tk, "note": note, "direction": direction,
                "error": f"could not fetch price history from Yahoo ({yahoo_tk})"}
    rsi_vals = _rsi_series(closes)
    if len(rsi_vals) < 21:
        return {"ticker": yahoo_tk, "note": note, "direction": direction,
                "error": f"insufficient RSI history ({len(rsi_vals)} values, need ≥21)"}
    window = rsi_vals[-21:]
    current_rsi = window[-1]
    mean = sum(window) / len(window)
    variance = sum((x - mean) ** 2 for x in window) / len(window)
    std = variance ** 0.5 if variance > 0 else 0.01
    sd_dist = (current_rsi - mean) / std
    if   sd_dist >  1.0: verdict = "CROWDED_HIGH"
    elif sd_dist < -1.0: verdict = "CROWDED_LOW"
    else:                verdict = "NEUTRAL"
    crowd_vs_us = (
        (verdict == "CROWDED_HIGH" and direction == "long") or
        (verdict == "CROWDED_LOW"  and direction == "short")
    )
    return {
        "ticker":      yahoo_tk,
        "note":        note,
        "direction":   direction,
        "rsi":         round(current_rsi, 1),
        "mean":        round(mean, 1),
        "std":         round(std, 1),
        "sd_dist":     round(sd_dist, 2),
        "verdict":     verdict,
        "crowd_vs_us": crowd_vs_us,
        "error":       None,
    }


def analyse_one(trade_id):
    """
    Returns dict:
      {
        "trade_id": str,
        "ticker":   str,
        "note":     str,
        "rsi":      float,
        "mean":     float,
        "std":      float,
        "sd_dist":  float,
        "verdict":  str,            # CROWDED_HIGH | CROWDED_LOW | NEUTRAL
        "crowd_vs_us": bool,
        "error":    None | str,
      }
    """
    if trade_id not in TRADE_TICKERS:
        return {"trade_id": trade_id, "error": "no ticker mapping for this instrument"}
    yahoo_tk, direction, note = TRADE_TICKERS[trade_id]
    result = _analyse(yahoo_tk, direction, note)
    result["trade_id"] = trade_id
    return result


def fetch_all(trade_ids=None):
    """Return {trade_id: rsi_result} for all known or specified trade ids."""
    ids = trade_ids or list(TRADE_TICKERS.keys())
    return {tid: analyse_one(tid) for tid in ids}


# --------------------------------------------------------------------------
# Derivatives Lab ideas — RSI positioning + live valuation multiples
# --------------------------------------------------------------------------

# idea_num (str) -> (yahoo_ticker, direction, note)
IDEA_TICKERS = {
    "1":   ("MU",       "long",  "Micron Technology (MU) — underlying for the collar"),
    "2":   ("EURUSD=X", "short", "EUR/USD — FX liability-hedge direction"),
    "3":   ("EURUSD=X", "short", "EUR/USD — seagull FX hedge, reducing net USD exposure"),
    "4":   ("^TNX",     "long",  "US 10Y yield (^TNX) — bond swap into current coupons"),
    "5":   ("NVDA",     "long",  "NVIDIA Corp (NVDA) — BREN on long position"),
    "6":   ("NVDA",     "long",  "NVIDIA Corp (NVDA) — CSP committed-to-buy at support"),
    "7":   ("AVGO",     "long",  "Broadcom (AVGO) — buffered-note re-entry"),
    "9":   ("MC.PA",    "long",  "LVMH Moët Hennessy (MC.PA Euronext Paris) — RevCon at buy-more level"),
    "10":  ("AMD",      "long",  "Advanced Micro Devices (AMD) — overwrite or decumulator"),
    "12":  ("GC=F",     "long",  "Gold futures (GC=F) — recognised hedge"),
    "101": ("ORCL",     "long",  "Oracle Corp (ORCL) — capital-protected note post-print"),
    "102": ("ADBE",     "long",  "Adobe Inc (ADBE) — cash-secured put accumulator"),
    "103": ("^TNX",     "long",  "US 10Y yield as front-end steepener proxy (^TNX)"),
}

# Single-name equities for which we also fetch live valuation multiples
VALUATION_TICKERS = {
    "1":   "MU",
    "5":   "NVDA",
    "6":   "NVDA",
    "7":   "AVGO",
    "9":   "MC.PA",
    "10":  "AMD",
    "101": "ORCL",
    "102": "ADBE",
}


def fetch_valuation_stats(ticker, timeout=12):
    """Fetch P/E, fwd P/E, EV/EBITDA, P/S from Yahoo Finance quoteSummary.
    Returns a dict with formatted strings; sets error key if unavailable."""
    url = (f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
           f"?modules=defaultKeyStatistics,summaryDetail")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        res = ((data.get("quoteSummary", {}).get("result") or [None])[0]) or {}
        stats   = res.get("defaultKeyStatistics", {})
        summary = res.get("summaryDetail", {})

        def _v(d, k):
            val = d.get(k, {})
            return val.get("raw") if isinstance(val, dict) else (val if val else None)

        def _fmt(v, dec=1):
            return f"{v:.{dec}f}x" if v is not None else "N/A"

        trailing_pe = _v(summary, "trailingPE")
        forward_pe  = _v(summary, "forwardPE")
        p_to_s      = _v(summary, "priceToSalesTrailing12Months")
        ev_ebitda   = _v(stats,   "enterpriseToEbitda")
        ev_revenue  = _v(stats,   "enterpriseToRevenue")

        if trailing_pe is None and forward_pe is None and ev_ebitda is None:
            return {"error": "no valuation data returned", "source": "Yahoo Finance",
                    "ticker": ticker, "asof": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
        return {
            "ticker":          ticker,
            "trailing_pe":     trailing_pe,
            "forward_pe":      forward_pe,
            "price_to_sales":  p_to_s,
            "ev_to_ebitda":    ev_ebitda,
            "ev_to_revenue":   ev_revenue,
            "trailing_pe_fmt": _fmt(trailing_pe),
            "forward_pe_fmt":  _fmt(forward_pe),
            "p_to_s_fmt":      _fmt(p_to_s),
            "ev_ebitda_fmt":   _fmt(ev_ebitda),
            "ev_revenue_fmt":  _fmt(ev_revenue),
            "source":          "Yahoo Finance",
            "asof":            datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "error":           None,
        }
    except Exception as ex:
        return {"error": str(ex)[:120], "source": "Yahoo Finance",
                "ticker": ticker, "asof": datetime.now(timezone.utc).strftime("%Y-%m-%d")}


def analyse_idea(idea_key):
    """RSI + valuation for a single idea key (str). Returns combined result dict."""
    if idea_key in IDEA_TICKERS:
        yahoo_tk, direction, note = IDEA_TICKERS[idea_key]
        result = _analyse(yahoo_tk, direction, note)
        result["idea_key"] = idea_key
    else:
        result = {"idea_key": idea_key, "error": f"no ticker mapped for idea {idea_key}"}
    result["valuation"] = (fetch_valuation_stats(VALUATION_TICKERS[idea_key])
                           if idea_key in VALUATION_TICKERS else None)
    return result


def fetch_all_ideas(idea_keys=None):
    """Return {idea_key: result} for all known or specified idea keys."""
    all_keys = list(set(list(IDEA_TICKERS.keys()) + list(VALUATION_TICKERS.keys())))
    keys = idea_keys or all_keys
    return {k: analyse_idea(k) for k in keys}


if __name__ == "__main__":
    results = fetch_all()
    for tid, r in results.items():
        if r.get("error"):
            print(f"  {tid}  ERROR: {r['error']}")
        else:
            print(f"  {tid}  RSI={r['rsi']:.1f}  mean={r['mean']:.1f}  "
                  f"SD={r['sd_dist']:+.2f}  {r['verdict']}"
                  + ("  *** CROWDED vs us" if r['crowd_vs_us'] else ""))
