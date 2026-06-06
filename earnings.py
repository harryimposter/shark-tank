"""earnings.py — Earnings Intelligence renderer for Market Map.

Pure stdlib, zero dependencies. Matches the pattern of charts.py and book.py.
Called by book.py via:

    import earnings
    ...
    earnings_html = earnings.render_earnings_section(brief.get("earnings_ideas", []))

Receives earnings_ideas list from the brief dict populated by Claude Code
following the PROMPT.md earnings intelligence spec.
"""

from datetime import datetime

_P = {
    "bg":          "#fff",
    "surface":     "#f7f7f5",
    "ink":         "#1a1a1a",
    "ink_soft":    "#6b6b6b",
    "ink_mute":    "#9a9a9a",
    "gold":        "#b8960c",
    "gold_light":  "#fdf6e3",
    "red":         "#c0392b",
    "red_light":   "#fdf0ef",
    "green":       "#27864a",
    "green_light": "#edf7f1",
    "amber":       "#d4860a",
    "amber_light": "#fef9ec",
    "line":        "#e5e5e3",
}


def _e(s) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _pip_bar(score: int, max_score: int = 8) -> str:
    pct = score / max_score if max_score else 0
    colour = _P["green"] if pct >= 0.75 else (_P["amber"] if pct >= 0.5 else _P["red"])
    pips = []
    for i in range(max_score):
        bg = colour if i < score else _P["line"]
        pips.append(
            f'<span style="display:inline-block;width:9px;height:9px;'
            f'border-radius:2px;background:{bg};margin-right:2px"></span>'
        )
    return "".join(pips)


def _badge(text, bg, fg) -> str:
    return (
        f'<span style="font-size:11px;font-weight:600;padding:2px 9px;'
        f'border-radius:3px;background:{bg};color:{fg}">{_e(text)}</span>'
    )


def _conviction_badge(label: str) -> str:
    lo = label.lower()
    if lo.startswith("high conviction") and "gap" not in lo:
        return _badge(label, _P["green_light"], _P["green"])
    if "high" in lo:
        return _badge(label, _P["amber_light"], _P["amber"])
    return _badge(label, _P["surface"], _P["ink_soft"])


def _direction_badge(direction: str) -> str:
    d = direction.upper()
    if d == "LONG":
        return _badge(d, _P["green_light"], _P["green"])
    if d == "SHORT":
        return _badge(d, _P["red_light"], _P["red"])
    return _badge(d, _P["surface"], _P["ink_soft"])


def _reaction_badge(tag: str) -> str:
    t = tag.upper()
    if t == "OVERSOLD":
        return _badge(t, _P["green_light"], _P["green"])
    if t == "OVERBOUGHT":
        return _badge(t, _P["red_light"], _P["red"])
    return _badge(t, _P["surface"], _P["ink_soft"])


def _pillar_grid(pillars: dict, confidences: dict) -> str:
    defs = [
        ("asymmetry",   "Asymmetry signal"),
        ("consensus",   "Sell-side consensus"),
        ("catalyst",    "Catalyst clarity"),
        ("positioning", "Positioning"),
    ]
    cells = []
    for key, label in defs:
        score = pillars.get(key, "—")
        conf  = confidences.get(key, "unverified")
        conf_c = (_P["green"] if conf == "sourced" else
                  _P["amber"] if conf == "estimated" else _P["red"])
        cells.append(
            f'<div style="background:{_P["surface"]};border-radius:4px;'
            f'padding:7px 9px">'
            f'<div style="font-size:10px;color:{_P["ink_mute"]};margin-bottom:3px">'
            f'{_e(label)}</div>'
            f'<div style="display:flex;align-items:center;'
            f'justify-content:space-between">'
            f'<span style="font-size:14px;font-weight:600;color:{_P["ink"]}">'
            f'{score}'
            f'<span style="font-size:10px;font-weight:400;'
            f'color:{_P["ink_mute"]}"> /2</span></span>'
            f'<span style="font-size:10px;color:{conf_c};font-weight:500">'
            f'{_e(conf)}</span>'
            f'</div></div>'
        )
    return (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;'
        f'gap:6px;margin-top:8px">'
        + "".join(cells) + "</div>"
    )


def render_idea_card(idea: dict) -> str:
    ticker     = idea.get("ticker", "")
    company    = idea.get("company", "")
    rdate      = idea.get("report_date", "")
    timing     = idea.get("report_timing", "")
    mode       = idea.get("mode", "PRE-EARNINGS").upper()
    direction  = idea.get("direction", "NEUTRAL")
    score      = int(idea.get("conviction_score", 0))
    conv_label = idea.get("conviction_label", "Medium conviction")
    rationale  = idea.get("conviction_rationale")
    bullets    = idea.get("key_bullets", [])
    what_moves = idea.get("what_moves_it", "")
    client_tp  = idea.get("client_talking_point", "")
    conflict   = idea.get("research_conflict", False)
    pillars    = idea.get("pillars", {})
    confs      = idea.get("pillar_confidence", {})

    # post-earnings fields
    reaction_tag = idea.get("reaction_tag")
    eps_actual   = idea.get("eps_actual")
    eps_estimate = idea.get("eps_estimate")
    eps_surprise = idea.get("eps_surprise_pct")
    stock_react  = idea.get("stock_reaction_pct")
    imp_upside   = idea.get("implied_upside_to_pt")

    mode_colour = _P["gold"] if mode == "PRE-EARNINGS" else _P["ink_soft"]

    out = [
        f'<div style="border-left:3px solid {_P["gold"]};'
        f'border:0.5px solid {_P["line"]};border-left:3px solid {_P["gold"]};'
        f'border-radius:0 6px 6px 0;padding:14px 16px;margin-bottom:12px;'
        f'background:{_P["bg"]}">'
    ]

    # header row
    out.append(
        f'<div style="display:flex;align-items:center;flex-wrap:wrap;'
        f'gap:8px;margin-bottom:10px">'
        f'<span style="font-size:15px;font-weight:700;color:{_P["ink"]}">'
        f'{_e(company)}</span>'
        f'<span style="font-size:12px;font-family:monospace;'
        f'color:{_P["ink_mute"]}">{_e(ticker)}</span>'
        f'<span style="font-size:11px;color:{mode_colour};font-weight:600;'
        f'margin-left:4px">{_e(mode)}</span>'
        f'<span style="font-size:11px;color:{_P["ink_mute"]};margin-left:auto">'
        f'{_e(rdate)} · {_e(timing)}</span>'
        f'</div>'
    )

    # direction + conviction row
    out.append(
        f'<div style="display:flex;align-items:center;gap:8px;'
        f'flex-wrap:wrap;margin-bottom:8px">'
        + _direction_badge(direction)
        + f'<span style="font-size:13px;font-weight:600;color:{_P["ink"]}">'
        f'{score}/8</span>'
        + _pip_bar(score)
        + _conviction_badge(conv_label)
    )
    if conflict:
        out.append(
            f'<span style="font-size:11px;color:{_P["amber"]};'
            f'background:{_P["amber_light"]};padding:2px 8px;'
            f'border-radius:3px">⚠ consensus conflict</span>'
        )
    out.append("</div>")

    # post-earnings reaction row
    if mode == "POST-EARNINGS" and reaction_tag:
        out.append(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'flex-wrap:wrap;margin-bottom:8px;font-size:12px;'
            f'color:{_P["ink_soft"]}">Reaction: '
            + _reaction_badge(reaction_tag)
        )
        if eps_actual is not None and eps_estimate is not None:
            surprise_str = f" ({eps_surprise}%)" if eps_surprise is not None else ""
            out.append(
                f'<span>EPS: <strong>{_e(eps_actual)}</strong> '
                f'vs est {_e(eps_estimate)}{_e(surprise_str)}</span>'
            )
        if stock_react is not None:
            out.append(f'<span>Stock: <strong>{_e(stock_react)}%</strong></span>')
        if imp_upside:
            out.append(f'<span>Upside to PT: {_e(imp_upside)}</span>')
        out.append("</div>")

    # conviction rationale
    if rationale:
        out.append(
            f'<div style="border-left:2px solid {_P["green"]};'
            f'padding:6px 10px;margin-bottom:8px;font-size:12px;'
            f'color:{_P["ink_soft"]};font-style:italic">'
            f'{_e(rationale)}</div>'
        )

    # pillar grid
    out.append(_pillar_grid(pillars, confs))

    # bullets
    if bullets:
        out.append(
            f'<ul style="margin:10px 0 8px;padding-left:16px;font-size:13px;'
            f'color:{_P["ink_soft"]};line-height:1.55">'
        )
        for b in bullets[:3]:
            out.append(f'<li style="margin-bottom:4px">{_e(b)}</li>')
        out.append("</ul>")

    # what moves it
    if what_moves:
        out.append(
            f'<div style="font-size:12px;margin-bottom:6px">'
            f'<span style="color:{_P["ink_mute"]};font-weight:600;'
            f'letter-spacing:.06em;font-size:10px">WHAT MOVES IT — </span>'
            f'<span style="color:{_P["ink"]}">{_e(what_moves)}</span></div>'
        )

    # client talking point
    if client_tp:
        out.append(
            f'<div style="font-size:12px;color:{_P["ink_soft"]};'
            f'background:{_P["surface"]};border-radius:4px;'
            f'padding:7px 10px;margin-top:4px">'
            f'<span style="font-size:10px;font-weight:600;'
            f'letter-spacing:.06em;color:{_P["ink_mute"]}">CLIENT — </span>'
            f'{_e(client_tp)}</div>'
        )

    out.append("</div>")
    return "".join(out)


def render_earnings_section(ideas: list) -> str:
    """Render the full Earnings Intelligence section.

    Returns empty string if no qualifying ideas — section is omitted cleanly.
    """
    if not ideas:
        return ""

    pre  = [i for i in ideas
            if i.get("mode", "").upper() == "PRE-EARNINGS"
            and "low" not in i.get("conviction_label", "").lower()]
    post = [i for i in ideas
            if i.get("mode", "").upper() == "POST-EARNINGS"
            and "low" not in i.get("conviction_label", "").lower()]

    if not pre and not post:
        return ""

    out = ['<div style="margin-bottom:24px">']

    if pre:
        out.append(
            f'<div style="font-size:11px;font-weight:700;letter-spacing:1px;'
            f'color:{_P["gold"]};text-transform:uppercase;margin-bottom:10px">'
            f'Pre-earnings · next 5 days</div>'
        )
        for idea in pre:
            out.append(render_idea_card(idea))

    if post:
        out.append(
            f'<div style="font-size:11px;font-weight:700;letter-spacing:1px;'
            f'color:{_P["ink_soft"]};text-transform:uppercase;'
            f'margin-bottom:10px;{"margin-top:16px;" if pre else ""}">'
            f'Post-earnings · last 3 days</div>'
        )
        for idea in post:
            out.append(render_idea_card(idea))

    out.append(
        f'<p style="font-size:10px;color:{_P["ink_mute"]};margin-top:8px">'
        f'Universe: large cap ($10bn+) · US &amp; Korea · '
        f'Tech / Financials / Industrials / Utilities · '
        f'Data sourced from Finnhub (earnings_data.md) where available. '
        f'Low conviction ideas excluded.</p>'
        f'</div>'
    )
    return "".join(out)


if __name__ == "__main__":
    # Smoke test: python earnings.py → writes earnings_demo.html
    sample = [
        {
            "ticker": "NVDA", "company": "NVIDIA Corporation",
            "report_date": "2026-06-10", "report_timing": "AMC",
            "mode": "PRE-EARNINGS", "direction": "Long",
            "conviction_score": 7, "conviction_label": "High — data gap flagged",
            "conviction_rationale": (
                "Implied straddle prices a 6% move vs 9.8% historical average — "
                "market underpricing by ~4pp at the quarter where AI revenue guide "
                "is the most-watched number."
            ),
            "pillars": {"asymmetry": 2, "consensus": 2, "catalyst": 2, "positioning": 1},
            "pillar_confidence": {
                "asymmetry":  "sourced",
                "consensus":  "sourced",
                "catalyst":   "sourced",
                "positioning": "unverified",
            },
            "key_bullets": [
                "Implied move 6% vs 9.8% historical — market underpricing the event.",
                "AI revenue guide ($0.7bn, +140% YoY) is the hyperscaler proof point.",
                "Six consecutive beats; positive revision trend last 30 days.",
            ],
            "what_moves_it": "AI revenue guidance above $0.75bn re-rates +10%.",
            "client_talking_point": (
                "NVDA reports into the strongest AI capex cycle on record — "
                "options are pricing a smaller move than history supports."
            ),
            "research_conflict": False,
        },
    ]
    html = (
        "<html><body style='max-width:680px;margin:40px auto;"
        "font-family:Georgia,serif;padding:20px'>"
        + render_earnings_section(sample)
        + "</body></html>"
    )
    with open("earnings_demo.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote earnings_demo.html — {datetime.now():%H:%M:%S}")
