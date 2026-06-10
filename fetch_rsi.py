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


def analyse_one(trade_id):
    """
    Returns dict:
      {
        "trade_id": str,
        "ticker":   str,
        "note":     str,
        "rsi":      float,          # current (most-recent) RSI
        "mean":     float,          # mean of last 21 RSI values
        "std":      float,          # std dev of last 21 RSI values
        "sd_dist":  float,          # (rsi - mean) / std  (signed)
        "verdict":  str,            # CROWDED_HIGH | CROWDED_LOW | NEUTRAL
        "crowd_vs_us": bool,        # True if the crowding hurts our position
        "error":    None | str,     # error string if not computable
      }
    """
    if trade_id not in TRADE_TICKERS:
        return {"trade_id": trade_id, "error": "no ticker mapping for this instrument"}

    yahoo_tk, direction, note = TRADE_TICKERS[trade_id]
    closes = _fetch_closes(yahoo_tk)
    if not closes:
        return {"trade_id": trade_id, "ticker": yahoo_tk, "note": note,
                "error": f"could not fetch price history from Yahoo ({yahoo_tk})"}

    rsi_vals = _rsi_series(closes)
    if len(rsi_vals) < 21:
        return {"trade_id": trade_id, "ticker": yahoo_tk, "note": note,
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

    # Does the crowding hurt our position?
    crowd_vs_us = (
        (verdict == "CROWDED_HIGH" and direction == "long") or
        (verdict == "CROWDED_LOW"  and direction == "short")
    )

    return {
        "trade_id":    trade_id,
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


def fetch_all(trade_ids=None):
    """Return {trade_id: rsi_result} for all known or specified trade ids."""
    ids = trade_ids or list(TRADE_TICKERS.keys())
    return {tid: analyse_one(tid) for tid in ids}


if __name__ == "__main__":
    results = fetch_all()
    for tid, r in results.items():
        if r.get("error"):
            print(f"  {tid}  ERROR: {r['error']}")
        else:
            print(f"  {tid}  RSI={r['rsi']:.1f}  mean={r['mean']:.1f}  "
                  f"SD={r['sd_dist']:+.2f}  {r['verdict']}"
                  + ("  *** CROWDED vs us" if r['crowd_vs_us'] else ""))
