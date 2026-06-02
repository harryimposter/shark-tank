"""Trusted-source allowlist for Market Map.

Every factual claim in the brief must trace to a source whose domain (or
named author) appears below. Anything that appears ONLY off this list is
dropped. Sources are cited by name in-text -- never as a URL.
"""

# Wires / data / press
WIRES = {
    "reuters.com": "Reuters",
    "bloomberg.com": "Bloomberg",
    "ft.com": "Financial Times",
    "wsj.com": "Wall Street Journal",
    "apnews.com": "AP",
    "telegraph.co.uk": "The Telegraph",
    "theguardian.com": "The Guardian",
    "aljazeera.com": "Al Jazeera",
}

# Official / central banks / statistical agencies
OFFICIAL = {
    "federalreserve.gov": "Federal Reserve",
    "ecb.europa.eu": "ECB",
    "bankofengland.co.uk": "Bank of England",
    "boj.or.jp": "Bank of Japan",
    "bls.gov": "BLS",
    "bea.gov": "BEA",
    "treasury.gov": "US Treasury",
    "cftc.gov": "CFTC",
    "imf.org": "IMF",
    "oecd.org": "OECD",
}

# Exchanges / vol venues
EXCHANGES = {
    "cmegroup.com": "CME",
    "cboe.com": "Cboe",
    "ice.com": "ICE",
}

# Independent macro (cited by author name)
INDEPENDENT = {
    "doomberg.substack.com": "Doomberg",
    "apolloacademy.com": "Apollo (Slok)",
    "fedguy.com": "Joseph Wang (Fed Guy)",
}

ALLOWLIST = {**WIRES, **OFFICIAL, **EXCHANGES, **INDEPENDENT}

# Domains passed to the web_search tool's allowed_domains parameter.
ALLOWED_DOMAINS = sorted(ALLOWLIST.keys())

# Human-readable names, used in the system prompt so the model cites correctly.
SOURCE_NAMES = sorted(set(ALLOWLIST.values()))


def allowlist_block() -> str:
    """Render the allowlist for injection into the model prompt."""
    lines = ["TRUSTED SOURCES (cite by name in-text; drop anything off-list):"]
    lines.append("  Wires/data: " + ", ".join(WIRES.values()))
    lines.append("  Official:   " + ", ".join(OFFICIAL.values()))
    lines.append("  Exchanges:  " + ", ".join(EXCHANGES.values()))
    lines.append("  Independent macro: " + ", ".join(INDEPENDENT.values()))
    return "\n".join(lines)
