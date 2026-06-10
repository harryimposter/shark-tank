#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_ivol.py — daily ATM implied-vol snapshot for the client-book scanner.

No paid feed, NO API key, and NO third-party packages — standard library only
(same discipline as fetch_earnings.py). Pulls option chains from Yahoo with a
cookie+crumb handshake, then computes implied vol *ourselves* by inverting
Black-Scholes on the option mark. We do not trust Yahoo's own impliedVolatility
field (it returns ~0); we use the bid/ask mid, or lastPrice when the market is
shut, and solve for sigma.

Appends a dated snapshot per name to ivol_history.json (a CI/cron fetcher that
writes a json; the stdlib renderer just reads it). US single names get a
*sourced* ATM ~360D IV + 90% put skew. The IV percentile is rank-vs-own-history,
so it stays "estimated" until the file accumulates ~60 daily snapshots. EU single
names (LVMH/SAP/TTE) are not on Yahoo's option feed — their seeded estimate is
left untouched and stays flagged estimated.

    python fetch_ivol.py            # update ivol_history.json
"""
import os, json, math, urllib.request, urllib.parse, http.cookiejar
from datetime import date, datetime, timezone

IVOL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ivol_history.json")
TODAY = date.today().isoformat()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

RISK_FREE = 0.045          # ~3m T-bill; short-dated ATM IV is barely sensitive to this
TARGET_DAYS = 360          # Observable O5 wants ATM ~360D IV as the vol-regime anchor

# book ticker -> Yahoo symbol (US listed options only)
YH = {"MU US": "MU", "NVDA US": "NVDA", "AVGO US": "AVGO", "AMD US": "AMD", "SPY US": "SPY"}


# ---- Black-Scholes + implied-vol inversion --------------------------------
def _ncdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _bs_price(S, K, T, r, sigma, call=True):
    if sigma <= 0 or T <= 0:
        return max(0.0, (S - K) if call else (K - S))
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if call:
        return S * _ncdf(d1) - K * math.exp(-r * T) * _ncdf(d2)
    return K * math.exp(-r * T) * _ncdf(-d2) - S * _ncdf(-d1)


def implied_vol(price, S, K, T, r, call=True):
    """Bisection — robust where Newton/vega blow up near the wings or at expiry."""
    intrinsic = max(0.0, (S - K) if call else (K - S))
    if price <= intrinsic + 1e-6 or T <= 0:
        return None
    lo, hi = 1e-4, 5.0
    if _bs_price(S, K, T, r, hi, call) < price:    # price above model ceiling -> unsolvable
        return None
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _bs_price(S, K, T, r, mid, call) > price:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# ---- Yahoo option chain (stdlib: cookie + crumb) --------------------------
def _session():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    try:
        op.open(urllib.request.Request("https://fc.yahoo.com", headers=UA), timeout=15)
    except Exception:
        pass  # the 404/consent page still sets the cookie we need
    crumb = op.open(urllib.request.Request(
        "https://query1.finance.yahoo.com/v1/test/getcrumb", headers=UA), timeout=15).read().decode()
    return op, crumb


def _chain(op, crumb, symbol, date_ts=None):
    url = (f"https://query1.finance.yahoo.com/v7/finance/options/{symbol}"
           f"?crumb={urllib.parse.quote(crumb)}")
    if date_ts:
        url += f"&date={date_ts}"
    d = json.load(op.open(urllib.request.Request(url, headers=UA), timeout=20))
    return d["optionChain"]["result"][0]


def _mid(c):
    bid, ask, last = float(c.get("bid") or 0), float(c.get("ask") or 0), float(c.get("lastPrice") or 0)
    if bid > 0 and ask > 0:
        return (bid + ask) / 2.0, "bid/ask"
    if last > 0:
        return last, "last"
    return None, None


def _iv_at(contracts, target_strike, spot, T, call):
    if not contracts:
        return None, None
    row = min(contracts, key=lambda c: abs(c["strike"] - target_strike))
    price, src = _mid(row)
    if price is None:
        return None, None
    return implied_vol(price, spot, float(row["strike"]), T, RISK_FREE, call=call), src


def atm_iv_for(op, crumb, symbol):
    res = _chain(op, crumb, symbol)
    spot = float(res["quote"]["regularMarketPrice"])
    exps = res.get("expirationDates", [])
    if not exps:
        return None

    def days(ts):
        return (datetime.fromtimestamp(ts, tz=timezone.utc).date() - date.today()).days

    target_ts = min(exps, key=lambda ts: abs(days(ts) - TARGET_DAYS))
    res2 = _chain(op, crumb, symbol, date_ts=target_ts)
    opt = res2["options"][0]
    calls, puts = opt.get("calls", []), opt.get("puts", [])
    T = max(days(target_ts), 1) / 365.0

    c_iv, c_src = _iv_at(calls, spot, spot, T, True)
    p_iv, p_src = _iv_at(puts, spot, spot, T, False)
    atm_ivs = [v for v in (c_iv, p_iv) if v]
    if not atm_ivs:
        return None
    atm = sum(atm_ivs) / len(atm_ivs)
    sk_iv, _ = _iv_at(puts, 0.9 * spot, spot, T, False)    # 90% put skew
    skew = round((sk_iv - atm) * 100, 1) if sk_iv else None
    return {"atm_iv_pct": round(atm * 100, 1), "skew": skew, "spot": round(spot, 2),
            "tenor_days": days(target_ts), "expiry": datetime.fromtimestamp(target_ts, tz=timezone.utc).date().isoformat(),
            "price_source": c_src or p_src}


def main():
    with open(IVOL_PATH, encoding="utf-8") as f:
        data = json.load(f)
    hist = data.setdefault("history", {})
    op, crumb = _session()

    for book_tk, yh in YH.items():
        try:
            r = atm_iv_for(op, crumb, yh)
        except Exception as ex:
            print(f"  {book_tk}: skip ({type(ex).__name__}: {str(ex)[:80]})")
            continue
        if not r:
            print(f"  {book_tk}: no solvable ATM IV")
            continue
        # keep only prior *sourced* snapshots — drop the estimated seed and today's, so the
        # percentile ranks against real history, never the placeholder
        series = [s for s in hist.get(book_tk, [])
                  if s.get("date") != TODAY and s.get("confidence") == "sourced"]
        ivs = [s["atm_iv_pct"] for s in series] + [r["atm_iv_pct"]]
        pct = round(100 * sum(1 for v in ivs if v <= r["atm_iv_pct"]) / len(ivs))
        sourced_rank = len(ivs) >= 60
        series.append({
            "date": TODAY, "atm_iv_pct": r["atm_iv_pct"],
            "iv_percentile_est": pct, "skew": r["skew"],
            "confidence": "sourced",                       # ATM level computed from live option marks
            "rank_confidence": "sourced" if sourced_rank else "estimated",
            "note": (f'ATM-{r["tenor_days"]}d IV solved from {r["price_source"]} option marks '
                     f'(Black-Scholes inversion); rank vs {len(ivs)} day(s) of own history '
                     f'{"(sourced)" if sourced_rank else "(building to 60d)"}.'),
            "spot": r["spot"], "expiry": r["expiry"],
        })
        hist[book_tk] = series
        print(f'  {book_tk}: ATM-{r["tenor_days"]}d IV {r["atm_iv_pct"]}% · skew {r["skew"]} '
              f'· {pct}th pctile ({len(ivs)}d) · {r["price_source"]}')

    meta = data.setdefault("_meta", {})
    meta["last_fetch"] = TODAY
    meta["source"] = ("ATM IV computed by Black-Scholes inversion on Yahoo option marks (stdlib cookie+crumb, "
                      "no key, no deps). US single names sourced; EU names estimated (not on feed); "
                      "IV percentile = rank vs own history, estimated until 60 daily snapshots.")
    with open(IVOL_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"wrote {IVOL_PATH}")


if __name__ == "__main__":
    main()
