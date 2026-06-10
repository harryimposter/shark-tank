#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_rsi.py — RSI positioning + technical analysis for the book (stdlib only).

Two jobs, both off one year of daily Yahoo Finance closes per instrument:

1. RSI (14-period, Wilder) read on the CLASSIC ABSOLUTE convention — no averaging,
   no standard-deviation-from-a-rolling-mean (that earlier approach washed the
   signal out and was wrong):
        RSI >= 70  ->  OVERBOUGHT  (extended; bearish for a long, supportive for a short)
        RSI <= 30  ->  OVERSOLD    (washed out; bullish for a long, bearish for a short)
        30 < RSI < 70  ->  NEUTRAL
   A position is "crowded against us" when the tape is overbought and we are long,
   or oversold and we are short.

2. Technical analysis — 50/100/200-day moving averages (trend + golden/death cross),
   20-day Bollinger Bands (mean-reversion / squeeze read), and Fibonacci retracement
   levels off the trailing ~6-month swing. Each is scored for how much it confirms
   the trade's direction and comes with a plain-English read.

Plus a cross-asset RSI SCREENER over a curated ~50-name universe, used to surface
oversold names to buy and overbought names to fade.

Returns graceful error dicts (never raises) so a refresh is reproducible offline.
"""

import json
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

# Trade-id -> (yahoo_ticker, direction, note)
# direction: "long" or "short" — sets whether overbought/oversold is for or against us
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


# --------------------------------------------------------------------------
# Yahoo price history
# --------------------------------------------------------------------------
def _fetch_ohlc(ticker, rng="1y", timeout=15, retries=2):
    """Fetch ~1y of daily OHLC from Yahoo. Returns dict of close/high/low lists,
    or None. One year gives enough history for a 200-day MA + Fibonacci swing."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?range={rng}&interval=1d&includePrePost=false")
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            result = (data.get("chart", {}).get("result") or [None])[0]
            if not result:
                return None
            q = result["indicators"]["quote"][0]
            closes = q.get("close", [])
            highs  = q.get("high", [])
            lows   = q.get("low", [])
            # keep only rows where close is present, aligning the other series
            c, h, l = [], [], []
            for i, cc in enumerate(closes):
                if cc is None:
                    continue
                c.append(cc)
                h.append(highs[i] if i < len(highs) and highs[i] is not None else cc)
                l.append(lows[i]  if i < len(lows)  and lows[i]  is not None else cc)
            if len(c) < 20:
                return None
            return {"close": c, "high": h, "low": l}
        except urllib.error.HTTPError as ex:
            last_err = ex
            if ex.code == 429 and attempt < retries:
                time.sleep(1.2 * (attempt + 1))   # back off on rate limit
                continue
            return None
        except Exception:
            return None
    return None


def _fetch_closes(ticker, timeout=15):
    """Back-compat helper: just the close series."""
    ohlc = _fetch_ohlc(ticker, timeout=timeout)
    return ohlc["close"] if ohlc else None


# --------------------------------------------------------------------------
# RSI (14-period, Wilder smoothing) — read on the absolute 30/70 convention
# --------------------------------------------------------------------------
def _rsi_series(closes, period=14):
    if len(closes) < period + 1:
        return []
    deltas = [closes[i + 1] - closes[i] for i in range(len(closes) - 1)]
    gains  = [max(0.0,  d) for d in deltas]
    losses = [max(0.0, -d) for d in deltas]
    avg_g = sum(gains[:period])  / period
    avg_l = sum(losses[:period]) / period
    rsi = []
    for i in range(period, len(deltas)):
        avg_g = (avg_g * (period - 1) + gains[i])  / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
        rs    = avg_g / avg_l if avg_l > 0 else 100.0
        rsi.append(100.0 - 100.0 / (1.0 + rs))
    return rsi


def rsi_verdict(rsi):
    """Classic absolute convention. No averaging."""
    if rsi >= 70:
        return "OVERBOUGHT"
    if rsi <= 30:
        return "OVERSOLD"
    return "NEUTRAL"


# --------------------------------------------------------------------------
# Technical analysis — moving averages, Bollinger Bands, Fibonacci
# --------------------------------------------------------------------------
def _sma(vals, n):
    return sum(vals[-n:]) / n if len(vals) >= n else None


def _stdev(vals):
    if len(vals) < 2:
        return 0.0
    m = sum(vals) / len(vals)
    return (sum((x - m) ** 2 for x in vals) / len(vals)) ** 0.5


def technicals(ohlc, direction):
    """Compute 50/100/200 DMA, Bollinger(20,2) and Fibonacci retracements off the
    trailing ~6-month swing, then score how much the picture confirms `direction`.

    Returns a dict with raw levels, a per-direction TA score (0-2) and a read.
    """
    if not ohlc:
        return None
    closes = ohlc["close"]
    highs  = ohlc.get("high", closes)
    lows   = ohlc.get("low", closes)
    price  = closes[-1]

    sma50  = _sma(closes, 50)
    sma100 = _sma(closes, 100)
    sma200 = _sma(closes, 200)

    # Bollinger Bands (20-period SMA ± 2 SD of close)
    bb_win = closes[-20:] if len(closes) >= 20 else closes
    bb_mid = sum(bb_win) / len(bb_win)
    bb_sd  = _stdev(bb_win)
    bb_up  = bb_mid + 2 * bb_sd
    bb_lo  = bb_mid - 2 * bb_sd
    bb_pctb = (price - bb_lo) / (bb_up - bb_lo) if bb_up > bb_lo else 0.5  # 0 = lower band, 1 = upper
    bb_bw   = (bb_up - bb_lo) / bb_mid if bb_mid else 0.0                  # bandwidth (squeeze gauge)

    # Fibonacci retracement off the trailing ~6-month (126-session) swing
    fib_win_h = highs[-126:] if len(highs) >= 126 else highs
    fib_win_l = lows[-126:]  if len(lows)  >= 126 else lows
    swing_hi = max(fib_win_h)
    swing_lo = min(fib_win_l)
    rng = swing_hi - swing_lo
    fib_levels = {
        "0.0%":   swing_hi,
        "23.6%":  swing_hi - 0.236 * rng,
        "38.2%":  swing_hi - 0.382 * rng,
        "50.0%":  swing_hi - 0.5   * rng,
        "61.8%":  swing_hi - 0.618 * rng,
        "100.0%": swing_lo,
    }
    # nearest fib level to the current price
    nearest_fib = min(fib_levels.items(), key=lambda kv: abs(kv[1] - price))

    # ---- trend read from the MA stack ----
    above = lambda ma: (ma is not None and price > ma)
    n_above = sum(1 for ma in (sma50, sma100, sma200) if above(ma))
    cross = None
    if sma50 is not None and sma200 is not None:
        cross = "golden" if sma50 > sma200 else "death"
    if n_above == 3:
        trend = "uptrend"          # price above all three MAs
    elif n_above == 0:
        trend = "downtrend"
    else:
        trend = "mixed"

    # ---- score for the trade's direction (0-2) ----
    # A trade is confirmed when the trend agrees AND the entry isn't chasing an
    # exhausted band (long into the lower half of the bands / short into the upper half).
    long_ta = direction == "long"
    trend_agrees = (trend == "uptrend" and long_ta) or (trend == "downtrend" and not long_ta)
    trend_against = (trend == "downtrend" and long_ta) or (trend == "uptrend" and not long_ta)
    # entry quality off Bollinger %B: longs prefer the lower half, shorts the upper half
    entry_good = (long_ta and bb_pctb <= 0.55) or (not long_ta and bb_pctb >= 0.45)

    if trend_agrees and entry_good:
        ta_score = 2
    elif trend_agrees or entry_good or trend == "mixed":
        ta_score = 1
    else:
        ta_score = 0
    if trend_against and not entry_good:
        ta_score = 0

    def _pct_from(ma):
        return round((price / ma - 1) * 100, 1) if ma else None

    # ---- plain-English read ----
    ma_txt = []
    for lab, ma in (("50d", sma50), ("100d", sma100), ("200d", sma200)):
        if ma is not None:
            ma_txt.append(f"{'above' if price > ma else 'below'} the {lab} ({ma:,.2f}, "
                          f"{_pct_from(ma):+}% )")
    cross_txt = ("a golden cross (50d above 200d) confirms the medium-term uptrend"
                 if cross == "golden" else
                 "a death cross (50d below 200d) confirms the medium-term downtrend"
                 if cross == "death" else "")
    bb_txt = (f"%B {bb_pctb:.2f} — "
              + ("riding the upper band (stretched)" if bb_pctb >= 0.9 else
                 "in the upper half" if bb_pctb >= 0.55 else
                 "hugging the lower band (washed out)" if bb_pctb <= 0.1 else
                 "in the lower half" if bb_pctb <= 0.45 else "mid-band")
              + (f"; bands tight ({bb_bw*100:.0f}% bandwidth — a squeeze, expect expansion)"
                 if bb_bw < 0.08 else f"; bandwidth {bb_bw*100:.0f}%"))
    fib_txt = (f"price sits nearest the {nearest_fib[0]} retracement ({nearest_fib[1]:,.2f}) of the "
               f"6-month {swing_lo:,.2f}–{swing_hi:,.2f} range")

    read = (f"Price {price:,.2f} is " + ", ".join(ma_txt) + ". "
            + (cross_txt + ". " if cross_txt else "")
            + f"Bollinger: {bb_txt}. Fibonacci: {fib_txt}.")

    how = ("How we use it: the 50/100/200-day MAs define the trend and the golden/death "
           "cross; Bollinger %B flags whether the entry is stretched (near a band) or has "
           "room; Fibonacci levels off the 6-month swing mark the support/resistance the "
           "stop and target are hung on.")

    return {
        "price": round(price, 4),
        "sma50": round(sma50, 4) if sma50 else None,
        "sma100": round(sma100, 4) if sma100 else None,
        "sma200": round(sma200, 4) if sma200 else None,
        "pct_vs_50": _pct_from(sma50), "pct_vs_100": _pct_from(sma100), "pct_vs_200": _pct_from(sma200),
        "cross": cross, "trend": trend,
        "bb_mid": round(bb_mid, 4), "bb_up": round(bb_up, 4), "bb_lo": round(bb_lo, 4),
        "bb_pctb": round(bb_pctb, 2), "bb_bandwidth_pct": round(bb_bw * 100, 1),
        "fib_high": round(swing_hi, 4), "fib_low": round(swing_lo, 4),
        "fib_levels": {k: round(v, 4) for k, v in fib_levels.items()},
        "nearest_fib": {"level": nearest_fib[0], "price": round(nearest_fib[1], 4)},
        "ta_score": ta_score, "direction": direction,
        "read": read, "how": how,
    }


# --------------------------------------------------------------------------
# Core analysis: RSI verdict + technicals for any instrument
# --------------------------------------------------------------------------
def _analyse(yahoo_tk, direction, note):
    ohlc = _fetch_ohlc(yahoo_tk)
    if not ohlc:
        return {"ticker": yahoo_tk, "note": note, "direction": direction,
                "error": f"could not fetch price history from Yahoo ({yahoo_tk})"}
    closes = ohlc["close"]
    rsi_vals = _rsi_series(closes)
    if not rsi_vals:
        return {"ticker": yahoo_tk, "note": note, "direction": direction,
                "error": f"insufficient RSI history for {yahoo_tk}"}
    current_rsi = rsi_vals[-1]
    verdict = rsi_verdict(current_rsi)
    crowd_vs_us = (
        (verdict == "OVERBOUGHT" and direction == "long") or
        (verdict == "OVERSOLD"  and direction == "short")
    )
    supports = (
        (verdict == "OVERSOLD"   and direction == "long") or
        (verdict == "OVERBOUGHT" and direction == "short")
    )
    return {
        "ticker":      yahoo_tk,
        "note":        note,
        "direction":   direction,
        "rsi":         round(current_rsi, 1),
        "verdict":     verdict,            # OVERBOUGHT | OVERSOLD | NEUTRAL
        "crowd_vs_us": crowd_vs_us,
        "supports":    supports,
        "technicals":  technicals(ohlc, direction),
        "error":       None,
    }


def analyse_one(trade_id):
    if trade_id not in TRADE_TICKERS:
        return {"trade_id": trade_id, "error": "no ticker mapping for this instrument"}
    yahoo_tk, direction, note = TRADE_TICKERS[trade_id]
    result = _analyse(yahoo_tk, direction, note)
    result["trade_id"] = trade_id
    return result


def fetch_all(trade_ids=None):
    ids = trade_ids or list(TRADE_TICKERS.keys())
    return {tid: analyse_one(tid) for tid in ids}


# --------------------------------------------------------------------------
# Derivatives Desk ideas — RSI + technicals + live valuation multiples
# --------------------------------------------------------------------------
IDEA_TICKERS = {
    "1":   ("MU",       "long",  "Micron Technology (MU) — underlying for the collar"),
    "14":  ("MU",       "long",  "Micron Technology (MU) — prepaid variable forward underlier"),
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

VALUATION_TICKERS = {
    "1":   "MU",
    "14":  "MU",
    "5":   "NVDA",
    "6":   "NVDA",
    "7":   "AVGO",
    "9":   "MC.PA",
    "10":  "AMD",
    "101": "ORCL",
    "102": "ADBE",
}


def fetch_valuation_stats(ticker, timeout=12):
    """Fetch P/E, fwd P/E, EV/EBITDA, P/S from Yahoo Finance quoteSummary."""
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
    all_keys = list(set(list(IDEA_TICKERS.keys()) + list(VALUATION_TICKERS.keys())))
    keys = idea_keys or all_keys
    return {k: analyse_idea(k) for k in keys}


# --------------------------------------------------------------------------
# Cross-asset RSI SCREENER — curated ~50-name universe
# --------------------------------------------------------------------------
# (yahoo_ticker, display_name, sector, region). Edit here to change the universe.
SCREEN_UNIVERSE = [
    # --- US mega-cap tech / semis ---
    ("NVDA",  "NVIDIA",            "Semiconductors", "US"),
    ("AMD",   "Adv. Micro Devices","Semiconductors", "US"),
    ("AVGO",  "Broadcom",          "Semiconductors", "US"),
    ("MU",    "Micron",            "Semiconductors", "US"),
    ("INTC",  "Intel",             "Semiconductors", "US"),
    ("QCOM",  "Qualcomm",          "Semiconductors", "US"),
    ("TSM",   "TSMC (ADR)",        "Semiconductors", "Asia"),
    ("AAPL",  "Apple",             "Tech hardware",  "US"),
    ("MSFT",  "Microsoft",         "Software",       "US"),
    ("GOOGL", "Alphabet",          "Internet",       "US"),
    ("AMZN",  "Amazon",            "Internet",       "US"),
    ("META",  "Meta Platforms",    "Internet",       "US"),
    ("ORCL",  "Oracle",            "Software",       "US"),
    ("ADBE",  "Adobe",             "Software",       "US"),
    ("CRM",   "Salesforce",        "Software",       "US"),
    ("PLTR",  "Palantir",          "Software",       "US"),
    ("TSLA",  "Tesla",             "Autos",          "US"),
    ("NFLX",  "Netflix",           "Media",          "US"),
    # --- US financials / industrials / energy / consumer ---
    ("JPM",   "JPMorgan",          "Financials",     "US"),
    ("BAC",   "Bank of America",   "Financials",     "US"),
    ("GS",    "Goldman Sachs",     "Financials",     "US"),
    ("CAT",   "Caterpillar",       "Industrials",    "US"),
    ("BA",    "Boeing",            "Industrials",    "US"),
    ("GE",    "GE Aerospace",      "Industrials",    "US"),
    ("XOM",   "Exxon Mobil",       "Energy",         "US"),
    ("CVX",   "Chevron",           "Energy",         "US"),
    ("WMT",   "Walmart",           "Consumer",       "US"),
    ("COST",  "Costco",            "Consumer",       "US"),
    ("MCD",   "McDonald's",        "Consumer",       "US"),
    ("LLY",   "Eli Lilly",         "Healthcare",     "US"),
    ("UNH",   "UnitedHealth",      "Healthcare",     "US"),
    # --- ETFs / cross-asset proxies ---
    ("SPY",   "S&P 500 ETF",       "US equity",      "US"),
    ("QQQ",   "Nasdaq 100 ETF",    "US tech",        "US"),
    ("SMH",   "Semis ETF",         "Semiconductors", "US"),
    ("IWM",   "Russell 2000 ETF",  "US small-cap",   "US"),
    ("XLF",   "Financials ETF",    "Financials",     "US"),
    ("XLE",   "Energy ETF",        "Energy",         "US"),
    ("GLD",   "Gold ETF",          "Commodity",      "Global"),
    ("TLT",   "20y+ Treasury ETF", "Rates",          "US"),
    ("HYG",   "HY Credit ETF",     "Credit",         "US"),
    # --- Europe / UK ---
    ("SAP.DE","SAP",               "Software",       "Europe"),
    ("ASML",  "ASML (ADR)",        "Semiconductors", "Europe"),
    ("MC.PA", "LVMH",              "Luxury",         "Europe"),
    ("SIE.DE","Siemens",           "Industrials",    "Europe"),
    ("SHEL",  "Shell (ADR)",       "Energy",         "UK"),
    ("AZN",   "AstraZeneca (ADR)", "Healthcare",     "UK"),
    ("HSBC",  "HSBC (ADR)",        "Financials",     "UK"),
    # --- Asia / Japan / Korea ---
    ("BABA",  "Alibaba (ADR)",     "Internet",       "Asia"),
    ("TM",    "Toyota (ADR)",      "Autos",          "Japan"),
    ("SONY",  "Sony (ADR)",        "Tech hardware",  "Japan"),
    ("MUFG",  "Mitsubishi UFJ",    "Financials",     "Japan"),
    # --- AI supply-chain sleeve (HBM / optical / connectivity / semicap) ---
    ("MRVL",  "Marvell",           "Semiconductors", "US"),
    ("ARM",   "Arm Holdings",      "Semiconductors", "US"),
    ("SWKS",  "Skyworks",          "Semiconductors", "US"),
    ("LITE",  "Lumentum",          "AI optical",     "US"),
    ("COHR",  "Coherent",          "AI optical",     "US"),
    ("AXTI",  "AXT Inc",           "AI optical",     "US"),
    ("ALAB",  "Astera Labs",       "AI connectivity","US"),
    ("CRDO",  "Credo Technology",  "AI connectivity","US"),
    ("SITM",  "SiTime",            "AI connectivity","US"),
    ("ONTO",  "Onto Innovation",   "Semicap",        "US"),
    ("ACLS",  "Axcelis",           "Semicap",        "US"),
    ("AMAT",  "Applied Materials", "Semicap",        "US"),
    ("VRT",   "Vertiv",            "AI power/cooling","US"),
]


def screen_one(ticker, name, sector, region):
    ohlc = _fetch_ohlc(ticker, rng="6mo")
    if not ohlc:
        return None
    rsi_vals = _rsi_series(ohlc["close"])
    if not rsi_vals:
        return None
    rsi = round(rsi_vals[-1], 1)
    return {
        "ticker": ticker, "name": name, "sector": sector, "region": region,
        "rsi": rsi, "verdict": rsi_verdict(rsi),
        "price": round(ohlc["close"][-1], 2),
        "technicals": technicals(ohlc, "long"),   # neutral 'long' lens for the trend read
    }


def run_screener(universe=None, low=30.0, high=70.0):
    """Scan the universe and split into oversold (<=low) and overbought (>=high)."""
    uni = universe or SCREEN_UNIVERSE
    oversold, overbought, errors = [], [], 0
    for tk, name, sector, region in uni:
        r = screen_one(tk, name, sector, region)
        if not r:
            errors += 1
            continue
        if r["rsi"] <= low:
            oversold.append(r)
        elif r["rsi"] >= high:
            overbought.append(r)
    oversold.sort(key=lambda x: x["rsi"])         # most oversold first
    overbought.sort(key=lambda x: -x["rsi"])      # most overbought first
    universe = [{"ticker": tk, "name": name, "sector": sector, "region": region}
                for tk, name, sector, region in uni]
    return {
        "oversold": oversold, "overbought": overbought,
        "scanned": len(uni), "errors": errors,
        "low": low, "high": high, "universe": universe,
        "asof": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


if __name__ == "__main__":
    results = fetch_all()
    for tid, r in results.items():
        if r.get("error"):
            print(f"  {tid}  ERROR: {r['error']}")
        else:
            print(f"  {tid}  RSI={r['rsi']:.1f}  {r['verdict']}"
                  + ("  *** CROWDED vs us" if r['crowd_vs_us'] else "")
                  + (f"  TA={r['technicals']['ta_score']}/2 {r['technicals']['trend']}" if r.get("technicals") else ""))
    print("\nScreener:")
    sc = run_screener()
    print(f'  scanned {sc["scanned"]}, {sc["errors"]} errors')
    print("  oversold:", [(x["ticker"], x["rsi"]) for x in sc["oversold"]])
    print("  overbought:", [(x["ticker"], x["rsi"]) for x in sc["overbought"]])
