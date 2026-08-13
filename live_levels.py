#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""live_levels.py — pull live cross-asset levels from TradingView's scanner.

Same data source as the right-rail widget, but read **headlessly** (no key, no
browser) so the trade book can be marked to *real* levels instead of hand-typed
guesses. Standard library only.

    import live_levels
    snap = live_levels.fetch()                 # {name: {close, chg_pct, chg_abs}}
    levels = live_levels.trade_levels(snap)    # {trade_id: level} for book.mark_to_market
    # derived spreads/ratios (Brent-WTI, 2s10s, DAX/Nasdaq) are computed here.

Caveats: unofficial endpoint (can change); non-US lines may be ~15min delayed;
values are point-in-time at the moment of the call. Options (put/call spreads)
have no free live feed — mark those from spot separately and label them.
"""
import json
import urllib.request

SCAN_URL = "https://scanner.tradingview.com/global/scan"

# friendly name -> TradingView ticker (probed working symbols, 2026-06)
SYMBOLS = {
    "brent":  "ICEEUR:BRN1!",   # Brent front month
    "wti":    "NYMEX:CL1!",     # WTI front month
    "gold":   "TVC:GOLD",
    "eurusd": "FX:EURUSD",
    "usdjpy": "FX:USDJPY",
    "euraud": "OANDA:EURAUD",
    "gbpusd": "FX:GBPUSD",
    "usdcnh": "FX:USDCNH",
    "dxy":    "TVC:DXY",
    "us02y":  "TVC:US02Y",
    "us10y":  "TVC:US10Y",
    "us30y":  "TVC:US30Y",
    "de10y":  "TVC:DE10Y",      # Bund
    "gb10y":  "TVC:GB10Y",      # Gilt
    "vix":    "TVC:VIX",
    "spx":    "SP:SPX",
    "ndx":    "NASDAQ:NDX",
    "ixic":   "NASDAQ:IXIC",    # Nasdaq Composite (the leg in the DAX RV)
    "dax":    "XETR:DAX",
    "dji":    "DJ:DJI",
    "ftse":   "FTSE:UKX",
    "nikkei": "TVC:NI225",
}


def scan(tickers, timeout=20):
    """Generic: return {ticker: {"close","chg_pct","chg_abs"}} for any TradingView tickers."""
    tickers = list(dict.fromkeys(tickers))
    body = json.dumps({"symbols": {"tickers": tickers},
                       "columns": ["close", "change", "change_abs"]}).encode()
    req = urllib.request.Request(
        SCAN_URL, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    data = json.load(urllib.request.urlopen(req, timeout=timeout))
    got = {row["s"]: row["d"] for row in data.get("data", [])}
    out = {}
    for tk in tickers:
        if tk in got and got[tk] and got[tk][0] is not None:
            close, chg, chg_abs = got[tk]
            out[tk] = {"close": close, "chg_pct": chg, "chg_abs": chg_abs}
    return out


def fetch(timeout=20):
    """Return {name: {"close", "chg_pct", "chg_abs"}} for every named macro symbol that resolves."""
    raw = scan(list(SYMBOLS.values()), timeout=timeout)
    out = {}
    for name, tk in SYMBOLS.items():
        if tk in raw:
            out[name] = raw[tk]
    return out


def trade_levels(snap):
    """Map the live snapshot onto open trade ids (incl. derived spreads/ratios).

    Excludes the two option structures (MM-008 put spread, MM-011 call spread) —
    those have no free live feed and must be marked from spot and labelled.
    """
    g = lambda k: snap[k]["close"] if k in snap else None
    lv = {}
    if g("euraud") is not None:                         lv["MM-2026-001"] = round(g("euraud"), 5)
    if g("brent") is not None:                          lv["MM-2026-002"] = round(g("brent"), 2)
    if g("brent") is not None and g("wti") is not None: lv["MM-2026-003"] = round(g("brent") - g("wti"), 2)
    if g("us10y") is not None:                          lv["MM-2026-004"] = round(g("us10y"), 3)
    if g("gold") is not None:                           lv["MM-2026-005"] = round(g("gold"), 2)
    if g("usdjpy") is not None:                         lv["MM-2026-007"] = round(g("usdjpy"), 3)
    if g("us10y") is not None and g("us02y") is not None: lv["MM-2026-009"] = round(g("us10y") - g("us02y"), 4)
    if g("dax") is not None and g("ixic") is not None:  lv["MM-2026-010"] = round(g("dax") / g("ixic"), 4)
    if g("eurusd") is not None:                         lv["MM-2026-012"] = round(g("eurusd"), 5)
    if g("us02y") is not None:                          lv["MM-2026-013"] = round(g("us02y"), 3)
    if g("us10y") is not None:                          lv["MM-2026-014"] = round(g("us10y"), 3)
    return lv


def _fmt_chg(name, snap, bp=False):
    if name not in snap:
        return "", "flat"
    chg_pct = snap[name]["chg_pct"]
    chg_abs = snap[name]["chg_abs"]
    direction = "up" if chg_pct > 0.03 else ("down" if chg_pct < -0.03 else "flat")
    if bp:
        return f'{chg_abs*100:+.0f}bp', direction
    return f'{chg_pct:+.2f}%', direction


if __name__ == "__main__":
    snap = fetch()
    print(f"resolved {len(snap)}/{len(SYMBOLS)} symbols\n")
    for k, v in snap.items():
        print(f'  {k:8s} {v["close"]:>12.4f}  {v["chg_pct"]:+.2f}%')
    print("\ntrade levels:")
    for tid, lvl in trade_levels(snap).items():
        print(f'  {tid}  {lvl}')
