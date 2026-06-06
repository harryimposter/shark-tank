#!/usr/bin/env python3
"""fetch_earnings.py — FactSet earnings data fetcher.

Runs via GitHub Actions every weekday at 6am UTC.
Writes earnings_data.md to the repo root.
Claude Code reads this file locally during the daily Market Map run.

Requires env vars: FACTSET_USERNAME, FACTSET_PASSWORD
Standard library only — no pip installs needed.
"""

import os
import json
import base64
import urllib.request
import urllib.error
from datetime import date, timedelta

# ── Auth ──────────────────────────────────────────────────────────────────────
USERNAME = os.environ.get("FACTSET_USERNAME", "")
PASSWORD = os.environ.get("FACTSET_PASSWORD", "")

if not USERNAME or not PASSWORD:
    print("ERROR: FACTSET_USERNAME and FACTSET_PASSWORD env vars required.")
    raise SystemExit(1)

_auth = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {_auth}",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}
BASE = "https://api.factset.com/content"

# ── Universe filter ───────────────────────────────────────────────────────────
SECTORS         = {"Technology", "Financials", "Industrials", "Utilities"}
MIN_MKT_CAP_BN  = 10
GEOGRAPHIES     = {"US", "KR"}

# ── Date windows ──────────────────────────────────────────────────────────────
TODAY      = date.today()
PRE_START  = TODAY.isoformat()
PRE_END    = (TODAY + timedelta(days=5)).isoformat()
POST_START = (TODAY - timedelta(days=3)).isoformat()
POST_END   = TODAY.isoformat()


# ── HTTP helper (stdlib only) ─────────────────────────────────────────────────
def _post(path: str, body: dict) -> dict:
    url  = BASE + path
    data = json.dumps(body).encode()
    req  = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as exc:
        print(f"  HTTP {exc.code} on {path}: {exc.read().decode()[:300]}")
        return {}
    except Exception as exc:
        print(f"  Error on {path}: {exc}")
        return {}


# ── FactSet calls ─────────────────────────────────────────────────────────────
def fetch_calendar() -> list:
    resp = _post("/factset-estimates/v2/calendar/events", {
        "startDate":    POST_START,
        "endDate":      PRE_END,
        "eventTypes":   ["Earnings"],
        "universeType": "EQUITY",
    })
    return resp.get("data", [])


def fetch_entity_id(ticker: str):
    resp = _post("/symbology/v2/identifier", {
        "ids":               [ticker],
        "inputSymbolType":   "TICKER",
        "outputSymbolTypes": ["FSYM_ID"],
    })
    items = resp.get("data", [])
    return items[0].get("fsymId") if items else None


def fetch_estimates(fsym_id: str) -> dict:
    resp = _post("/factset-estimates/v2/consensus/estimates", {
        "ids":               [fsym_id],
        "metrics":           ["EPS", "SALES"],
        "periodicity":       "QTR",
        "fiscalPeriodStart": "NOW",
        "fiscalPeriodEnd":   "NOW",
    })
    items = resp.get("data", [])
    eps = next((i for i in items if i.get("metric") == "EPS"),  {})
    rev = next((i for i in items if i.get("metric") == "SALES"), {})
    return {
        "eps_mean":     eps.get("mean"),
        "eps_high":     eps.get("high"),
        "eps_low":      eps.get("low"),
        "eps_count":    eps.get("numEstimates"),
        "eps_revision": eps.get("revisionDirection"),
        "rev_mean":     rev.get("mean"),
    }


def fetch_ratings(fsym_id: str) -> dict:
    resp = _post("/factset-estimates/v2/consensus/ratings", {"ids": [fsym_id]})
    r = (resp.get("data") or [{}])[0]
    return {
        "buy_count":     r.get("buyCount"),
        "hold_count":    r.get("holdCount"),
        "sell_count":    r.get("sellCount"),
        "consensus_pt":  r.get("priceTarget"),
        "current_price": r.get("price"),
    }


def fetch_surprises(fsym_id: str) -> list:
    resp = _post("/factset-estimates/v2/surprise", {
        "ids":               [fsym_id],
        "metrics":           ["EPS"],
        "periodicity":       "QTR",
        "fiscalPeriodStart": "NOW-4",
        "fiscalPeriodEnd":   "NOW-1",
    })
    return [
        {
            "period":       i.get("fiscalPeriod"),
            "actual":       i.get("actual"),
            "estimate":     i.get("estimate"),
            "surprise_pct": i.get("surprisePercent"),
        }
        for i in resp.get("data", [])
    ]


def fetch_ownership(fsym_id: str) -> dict:
    resp = _post("/factset-ownership/v1/holders/shares", {
        "ids":        [fsym_id],
        "date":       TODAY.isoformat(),
        "holderType": "INSTITUTIONS",
    })
    r = (resp.get("data") or [{}])[0]
    return {
        "short_interest_pct":    r.get("shortInterestPct"),
        "inst_ownership_change": r.get("changePercent"),
    }


def fetch_options(fsym_id: str) -> dict:
    resp = _post("/factset-options/v1/options/prices", {
        "ids":      [fsym_id],
        "date":     TODAY.isoformat(),
        "exchange": "USA",
    })
    r = (resp.get("data") or [{}])[0]
    return {"implied_vol": r.get("impliedVolatility")}


# ── Markdown writer ───────────────────────────────────────────────────────────
def _val(v) -> str:
    return str(v) if v is not None else "unavailable"


def write_markdown(rows: list) -> None:
    lines = [
        "# FactSet Earnings Data",
        f"Generated: {TODAY.isoformat()} 06:00 UTC",
        f"Pre-earnings window:  {PRE_START} to {PRE_END}",
        f"Post-earnings window: {POST_START} to {POST_END}",
        "Universe: large cap (>$10bn) · US + Korea · "
        "Tech / Financials / Industrials / Utilities",
        "",
    ]

    if not rows:
        lines.append("_No qualifying companies in this window._")
    else:
        for d in rows:
            mode = "POST-EARNINGS" if d["report_date"] <= TODAY.isoformat() \
                   else "PRE-EARNINGS"
            lines += [
                f"## {d['ticker']} — {d['company']}",
                f"- **Mode:** {mode}",
                f"- **Report date:** {d['report_date']}",
                f"- **Report timing:** {_val(d.get('report_timing'))}",
                f"- **Sector:** {_val(d.get('sector'))}",
                f"- **Market cap:** ${_val(d.get('market_cap_bn'))}bn",
                "",
                "### Consensus estimates (FactSet — sourced)",
                f"- EPS mean:           {_val(d.get('eps_mean'))}",
                f"- EPS high:           {_val(d.get('eps_high'))}",
                f"- EPS low:            {_val(d.get('eps_low'))}",
                f"- EPS estimate count: {_val(d.get('eps_count'))}",
                f"- EPS revision (30d): {_val(d.get('eps_revision'))}",
                f"- Revenue mean:       {_val(d.get('rev_mean'))}",
                "",
                "### Analyst ratings (FactSet — sourced)",
                f"- Buy/OW:        {_val(d.get('buy_count'))}",
                f"- Hold:          {_val(d.get('hold_count'))}",
                f"- Sell/UW:       {_val(d.get('sell_count'))}",
                f"- Consensus PT:  {_val(d.get('consensus_pt'))}",
                f"- Current price: {_val(d.get('current_price'))}",
                "",
                "### Earnings surprise history — last 4 quarters (FactSet — sourced)",
            ]
            surprises = d.get("surprises", [])
            if surprises:
                for s in surprises:
                    lines.append(
                        f"- {_val(s.get('period'))}: actual {_val(s.get('actual'))} "
                        f"vs est {_val(s.get('estimate'))} "
                        f"({_val(s.get('surprise_pct'))}%)"
                    )
            else:
                lines.append("- unavailable")

            lines += [
                "",
                "### Positioning (FactSet — sourced)",
                f"- Short interest % of float:            {_val(d.get('short_interest_pct'))}",
                f"- Institutional ownership change (qtr): {_val(d.get('inst_ownership_change'))}",
                "",
                "### Options / implied move (FactSet — sourced if available)",
                f"- Implied volatility (ATM): {_val(d.get('implied_vol'))}",
                "",
                "---",
                "",
            ]

    with open("earnings_data.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Written earnings_data.md — {len(rows)} companies")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Fetching earnings calendar from FactSet...")
    calendar = fetch_calendar()
    print(f"  {len(calendar)} events returned")

    qualifying = []
    for ev in calendar:
        if ev.get("sector") not in SECTORS:
            continue
        if float(ev.get("marketCapBn") or 0) < MIN_MKT_CAP_BN:
            continue
        if ev.get("isoCountry") not in GEOGRAPHIES:
            continue
        qualifying.append(ev)

    print(f"  {len(qualifying)} pass universe filter")

    results = []
    for ev in qualifying:
        ticker = ev.get("ticker", "")
        print(f"  Fetching {ticker}...")
        fsym_id = fetch_entity_id(ticker)
        if not fsym_id:
            print(f"    No FactSet ID for {ticker} — skipping")
            continue

        results.append({
            "ticker":        ticker,
            "company":       ev.get("companyName", ticker),
            "report_date":   ev.get("eventDate", ""),
            "report_timing": ev.get("eventTime", "TBD"),
            "sector":        ev.get("sector", ""),
            "market_cap_bn": ev.get("marketCapBn"),
            **fetch_estimates(fsym_id),
            **fetch_ratings(fsym_id),
            "surprises": fetch_surprises(fsym_id),
            **fetch_ownership(fsym_id),
            **fetch_options(fsym_id),
        })

    write_markdown(results)


if __name__ == "__main__":
    main()
