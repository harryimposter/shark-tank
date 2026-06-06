#!/usr/bin/env python3
"""fetch_earnings.py — Finnhub earnings data fetcher.

Runs via GitHub Actions every weekday at 6am UTC.
Writes earnings_data.md to the repo root.
Claude Code reads this file locally during the daily Market Map run.

Requires env var: FINNHUB_API_KEY
Standard library only — no pip installs needed.
Rate limit: ~60 req/min on free tier; 0.25s sleep between calls.
"""

import os
import json
import urllib.request
import urllib.error
import time
from datetime import date, timedelta

# ── Auth ──────────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("FINNHUB_API_KEY", "")
if not API_KEY:
    print("ERROR: FINNHUB_API_KEY env var required.")
    raise SystemExit(1)

BASE = "https://finnhub.io/api/v1"

# ── Universe filter ───────────────────────────────────────────────────────────
# Finnhub uses its own industry strings — map to our sector buckets
SECTOR_KEYWORDS = {
    "Technology":   ["semiconductor", "software", "technology", "electronic",
                     "hardware", "internet", "telecom", "communication"],
    "Financials":   ["bank", "financial", "insurance", "asset management",
                     "capital markets", "diversified financial", "mortgage", "reit"],
    "Industrials":  ["aerospace", "defense", "industrial", "machinery",
                     "transport", "logistics", "construction", "engineering"],
    "Utilities":    ["utility", "utilities", "electric", "gas", "water", "power"],
}
MIN_MKT_CAP_BN  = 10          # market cap in $bn (Finnhub returns $millions)
GEOGRAPHIES     = {"US", "KR"}

# ── Date windows ──────────────────────────────────────────────────────────────
TODAY      = date.today()
PRE_END    = (TODAY + timedelta(days=5)).isoformat()
POST_START = (TODAY - timedelta(days=3)).isoformat()


# ── HTTP helper ───────────────────────────────────────────────────────────────
def _get(path: str, params: dict = None, _retries: int = 3):
    qs = "&".join(f"{k}={v}" for k, v in (params or {}).items())
    url = f"{BASE}{path}?token={API_KEY}" + (f"&{qs}" if qs else "")
    for attempt in range(_retries):
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = 60 * (attempt + 1)
                print(f"  Rate limited — sleeping {wait}s...")
                time.sleep(wait)
                continue
            if exc.code != 403:
                print(f"  HTTP {exc.code} on {path}")
            return None
        except Exception as exc:
            print(f"  Error on {path}: {exc}")
            return None
    return None


# ── Sector classifier ─────────────────────────────────────────────────────────
def classify_sector(finnhub_industry: str):
    ind = (finnhub_industry or "").lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(kw in ind for kw in keywords):
            return sector
    return None


# ── Finnhub calls ─────────────────────────────────────────────────────────────
def fetch_calendar() -> list:
    data = _get("/calendar/earnings", {"from": POST_START, "to": PRE_END})
    return (data or {}).get("earningsCalendar", [])


def fetch_profile(symbol: str) -> dict:
    return _get("/stock/profile2", {"symbol": symbol}) or {}


def fetch_recommendations(symbol: str) -> dict:
    data = _get("/stock/recommendation", {"symbol": symbol})
    if not data:
        return {}
    r = data[0]  # most recent period
    return {
        "buy_count":  (r.get("buy") or 0) + (r.get("strongBuy") or 0),
        "hold_count":  r.get("hold"),
        "sell_count": (r.get("sell") or 0) + (r.get("strongSell") or 0),
        "rec_period":  r.get("period"),
    }


def fetch_surprises(symbol: str) -> list:
    data = _get("/stock/earnings", {"symbol": symbol, "limit": "4"})
    if not data:
        return []
    return [
        {
            "period":       f"{i.get('year')} Q{i.get('quarter')}",
            "actual":       i.get("actual"),
            "estimate":     i.get("estimate"),
            "surprise_pct": round(i["surprisePercent"], 2) if i.get("surprisePercent") else None,
        }
        for i in data
    ]


def fetch_metrics(symbol: str) -> dict:
    data = _get("/stock/metric", {"symbol": symbol, "metric": "all"})
    m = (data or {}).get("metric", {})
    return {
        "week52_high":          m.get("52WeekHigh"),
        "week52_low":           m.get("52WeekLow"),
        "revenue_growth_yoy":   m.get("revenueGrowthTTMYoy"),
        "eps_growth_yoy":       m.get("epsGrowthTTMYoy"),
        "short_ratio":          m.get("shortRatio"),
        "short_interest":       m.get("shortInterest"),
    }


# ── Markdown writer ───────────────────────────────────────────────────────────
def _val(v) -> str:
    return str(v) if v is not None else "unavailable"


HOUR_MAP = {"bmo": "BMO (before open)", "amc": "AMC (after close)",
            "dmh": "DMH (during hours)"}


def write_markdown(rows: list) -> None:
    lines = [
        "# Finnhub Earnings Data",
        f"Generated: {TODAY.isoformat()} 06:00 UTC",
        f"Pre-earnings window:  {TODAY.isoformat()} to {PRE_END}",
        f"Post-earnings window: {POST_START} to {TODAY.isoformat()}",
        "Universe: large cap (>$10bn) · US + Korea · "
        "Tech / Financials / Industrials / Utilities",
        "Source: Finnhub.io",
        "",
    ]

    if not rows:
        lines.append("_No qualifying companies in this window._")
    else:
        for d in rows:
            mode   = d["mode"]
            timing = HOUR_MAP.get(d.get("report_timing", ""), d.get("report_timing", "TBD"))
            lines += [
                f"## {d['symbol']} — {d['company']}",
                f"- **Mode:** {mode}",
                f"- **Report date:** {d['report_date']}",
                f"- **Report timing:** {timing}",
                f"- **Sector:** {_val(d.get('sector'))}",
                f"- **Market cap:** ${round(d['market_cap_mn'] / 1000, 1)}bn",
                "",
                "### Consensus estimates (Finnhub — sourced)",
                f"- EPS estimate:     {_val(d.get('eps_estimate'))}",
                f"- Revenue estimate: {_val(d.get('rev_estimate'))}",
            ]
            if mode == "POST-EARNINGS":
                lines += [
                    f"- EPS actual:      {_val(d.get('eps_actual'))}",
                    f"- Revenue actual:  {_val(d.get('rev_actual'))}",
                ]
            lines += [
                "",
                "### Analyst recommendations (Finnhub — sourced)",
                f"- Buy/Strong buy: {_val(d.get('buy_count'))}",
                f"- Hold:           {_val(d.get('hold_count'))}",
                f"- Sell/Strong sell: {_val(d.get('sell_count'))}",
                f"- Period:         {_val(d.get('rec_period'))}",
                "",
                "### Earnings surprise history — last 4 quarters (Finnhub — sourced)",
            ]
            surprises = d.get("surprises", [])
            if surprises:
                for s in surprises:
                    surp = f" ({s['surprise_pct']}%)" if s.get("surprise_pct") is not None else ""
                    lines.append(
                        f"- {s['period']}: actual {_val(s.get('actual'))} "
                        f"vs est {_val(s.get('estimate'))}{surp}"
                    )
            else:
                lines.append("- unavailable")

            lines += [
                "",
                "### Growth & technicals (Finnhub — sourced)",
                f"- Revenue growth YoY (TTM): {_val(d.get('revenue_growth_yoy'))}%",
                f"- EPS growth YoY (TTM):     {_val(d.get('eps_growth_yoy'))}%",
                f"- 52-week high:             {_val(d.get('week52_high'))}",
                f"- 52-week low:              {_val(d.get('week52_low'))}",
                f"- Short ratio:              {_val(d.get('short_ratio'))}",
                f"- Short interest:           {_val(d.get('short_interest'))}",
                "",
                "---",
                "",
            ]

    with open("earnings_data.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Written earnings_data.md — {len(rows)} companies")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Fetching earnings calendar from Finnhub...")
    calendar = fetch_calendar()
    print(f"  {len(calendar)} events in window")

    results = []
    seen = set()

    for ev in calendar:
        symbol = ev.get("symbol", "")
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)

        # Fetch profile to apply universe filter
        time.sleep(1.1)
        profile = fetch_profile(symbol)
        if not profile:
            continue

        country = profile.get("country", "")
        if country not in GEOGRAPHIES:
            continue

        mkt_cap_mn = profile.get("marketCapitalization") or 0
        if mkt_cap_mn < MIN_MKT_CAP_BN * 1000:
            continue

        sector = classify_sector(profile.get("finnhubIndustry", ""))
        if not sector:
            continue

        # ── Mode check: epsActual presence is authoritative ──────────────────
        # Finnhub calendar dates can be mis-stated; treat a non-null epsActual
        # as proof the company has already printed regardless of date field.
        has_reported = ev.get("epsActual") is not None
        report_date  = ev.get("date", "")

        if has_reported:
            # Post-earnings: must have reported within the lookback window
            if report_date < POST_START or report_date > TODAY.isoformat():
                print(f"  {symbol} — skipped (reported {report_date}, outside post window)")
                continue
            mode = "POST-EARNINGS"
        else:
            # Pre-earnings: date must be in the future
            if report_date < TODAY.isoformat():
                # Calendar date is in the past but no actual yet — data lag, skip
                print(f"  {symbol} — skipped (date {report_date} is past but no actual reported)")
                continue
            mode = "PRE-EARNINGS"

        print(f"  {symbol} ({profile.get('finnhubIndustry')}) — ${mkt_cap_mn/1000:.0f}bn [{mode}]")

        time.sleep(1.1)
        recs = fetch_recommendations(symbol)

        time.sleep(1.1)
        surprises = fetch_surprises(symbol)

        time.sleep(1.1)
        metrics = fetch_metrics(symbol)

        results.append({
            "symbol":        symbol,
            "company":       profile.get("name", symbol),
            "report_date":   report_date,
            "report_timing": ev.get("hour", ""),
            "mode":          mode,
            "sector":        sector,
            "market_cap_mn": mkt_cap_mn,
            "eps_estimate":  ev.get("epsEstimate"),
            "rev_estimate":  ev.get("revenueEstimate"),
            "eps_actual":    ev.get("epsActual"),
            "rev_actual":    ev.get("revenueActual"),
            **recs,
            "surprises": surprises,
            **metrics,
        })

    write_markdown(results)


if __name__ == "__main__":
    main()
