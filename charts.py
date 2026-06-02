"""Pure-Python inline SVG chart generators for Market Map.

No external chart libraries, no JavaScript, no CDN. Every function returns a
self-contained <svg> string that inherits the page palette. Charts are drawn
on a fixed user-space viewBox and scaled to 100% width by the container.
"""

from datetime import datetime

PALETTE = {
    "bg": "#fff",
    "paper": "#f7f7f5",
    "ink": "#1a1a1a",
    "ink_soft": "#6b6b6b",
    "ink_mute": "#9a9a9a",
    "gold": "#b8960c",
    "red": "#c0392b",
    "green": "#27864a",
    "line": "#e5e5e3",
}

# Default plotting box (user-space units; rendered responsive via width:100%).
_W, _H = 640, 320
_PAD_L, _PAD_R, _PAD_T, _PAD_B = 52, 18, 26, 40


def _esc(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _open(w=_W, h=_H) -> str:
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'font-family="Georgia, serif" '
        f'role="img" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:100%;height:auto;display:block">'
    )


def _placeholder(msg, w=_W, h=140) -> str:
    return (
        _open(w, h)
        + f'<rect x="0" y="0" width="{w}" height="{h}" fill="{PALETTE["paper"]}" '
        f'rx="6"/>'
        + f'<text x="{w/2}" y="{h/2}" text-anchor="middle" '
        f'dominant-baseline="middle" font-size="15" '
        f'fill="{PALETTE["ink_mute"]}" font-style="italic">{_esc(msg)}</text>'
        + "</svg>"
    )


def _title(text, w=_W) -> str:
    return (
        f'<text x="{_PAD_L}" y="16" font-size="12" letter-spacing="1.5" '
        f'fill="{PALETTE["ink_mute"]}">{_esc(text.upper())}</text>'
    )


def _scale(v, vmin, vmax, pmin, pmax):
    if vmax == vmin:
        return (pmin + pmax) / 2
    return pmin + (v - vmin) * (pmax - pmin) / (vmax - vmin)


def _nice_bounds(values, pad_frac=0.08):
    lo, hi = min(values), max(values)
    if lo == hi:
        lo -= 1
        hi += 1
    span = hi - lo
    return lo - span * pad_frac, hi + span * pad_frac


def _grid_and_yaxis(vmin, vmax, fmt="{:.1f}", w=_W, h=_H, ticks=4):
    px_top, px_bot = _PAD_T, h - _PAD_B
    out = []
    for i in range(ticks + 1):
        val = vmin + (vmax - vmin) * i / ticks
        y = _scale(val, vmin, vmax, px_bot, px_top)
        out.append(
            f'<line x1="{_PAD_L}" y1="{y:.1f}" x2="{w-_PAD_R}" y2="{y:.1f}" '
            f'stroke="{PALETTE["line"]}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{_PAD_L-7}" y="{y+4:.1f}" text-anchor="end" '
            f'font-size="11" fill="{PALETTE["ink_mute"]}">{_esc(fmt.format(val))}</text>'
        )
    return "".join(out)


def _xlabels(labels, w=_W, h=_H):
    px_l, px_r = _PAD_L, w - _PAD_R
    n = len(labels)
    out = []
    for i, lab in enumerate(labels):
        x = px_l if n == 1 else _scale(i, 0, n - 1, px_l, px_r)
        out.append(
            f'<text x="{x:.1f}" y="{h-_PAD_B+18}" text-anchor="middle" '
            f'font-size="11" fill="{PALETTE["ink_mute"]}">{_esc(lab)}</text>'
        )
    return "".join(out)


def _polyline(values, vmin, vmax, color, w=_W, h=_H, width=2.2, dash=None):
    px_l, px_r = _PAD_L, w - _PAD_R
    px_t, px_b = _PAD_T, h - _PAD_B
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = px_l if n == 1 else _scale(i, 0, n - 1, px_l, px_r)
        y = _scale(v, vmin, vmax, px_b, px_t)
        pts.append(f"{x:.1f},{y:.1f}")
    d = f' stroke-dasharray="{dash}"' if dash else ""
    line = (
        f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{d}/>'
    )
    dots = "".join(
        f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="2.6" '
        f'fill="{color}"/>'
        for p in pts
    )
    return line + dots


def _legend(items, w=_W):
    # items: list of (label, color, dashed)
    out = []
    x = _PAD_L
    y = _H - 6
    for label, color, dashed in items:
        dash = ' stroke-dasharray="4 3"' if dashed else ""
        out.append(
            f'<line x1="{x}" y1="{y-4}" x2="{x+18}" y2="{y-4}" stroke="{color}" '
            f'stroke-width="2.4"{dash}/>'
        )
        out.append(
            f'<text x="{x+24}" y="{y}" font-size="11" '
            f'fill="{PALETTE["ink_soft"]}">{_esc(label)}</text>'
        )
        x += 30 + len(label) * 6.6
    return "".join(out)


# --------------------------------------------------------------------------
# 13a -- EQUITY CURVE
# --------------------------------------------------------------------------
def equity_curve(closed):
    """Cumulative conviction-weighted P&L of the closed book over time, with an
    equal-weight line drawn behind it for comparison."""
    pts = [t for t in closed if t.get("exit", {}).get("date") and "pnl_pct" in t.get("exit", {})]
    pts.sort(key=lambda t: t["exit"]["date"])
    if not pts:
        return _placeholder("equity curve: no closed trades yet")

    cum_w, cum_e = 0.0, 0.0
    weighted, equal, labels = [], [], []
    for t in pts:
        conv = float(t.get("conviction", 5)) / 10.0
        pnl = float(t["exit"]["pnl_pct"])
        cum_w += pnl * conv
        cum_e += pnl
        weighted.append(cum_w)
        equal.append(cum_e)
        labels.append(t["exit"]["date"][5:])  # MM-DD

    allv = weighted + equal + [0.0]
    vmin, vmax = _nice_bounds(allv)

    svg = [_open(), _title("equity curve  ·  cumulative P&L (%)")]
    svg.append(_grid_and_yaxis(vmin, vmax, "{:+.1f}", ticks=4))
    # zero line
    zy = _scale(0, vmin, vmax, _H - _PAD_B, _PAD_T)
    svg.append(
        f'<line x1="{_PAD_L}" y1="{zy:.1f}" x2="{_W-_PAD_R}" y2="{zy:.1f}" '
        f'stroke="{PALETTE["ink_mute"]}" stroke-width="1" stroke-dasharray="2 3"/>'
    )
    svg.append(_xlabels(labels))
    svg.append(_polyline(equal, vmin, vmax, PALETTE["ink_mute"], width=1.6, dash="4 3"))
    svg.append(_polyline(weighted, vmin, vmax, PALETTE["gold"], width=2.6))
    svg.append(_legend([("conviction-weighted", PALETTE["gold"], False),
                        ("equal-weight", PALETTE["ink_mute"], True)]))
    svg.append("</svg>")
    return "".join(svg)


# --------------------------------------------------------------------------
# 13b -- CALIBRATION
# --------------------------------------------------------------------------
def calibration(closed, min_trades=10):
    """Stated conviction bucket (x) vs realised hit-rate (y), with 45° diagonal.
    A trade is a 'hit' if its realised P&L was positive."""
    graded = [t for t in closed if "pnl_pct" in t.get("exit", {}) and t.get("conviction")]
    if len(graded) < min_trades:
        need = min_trades - len(graded)
        return _placeholder(f"calibration: {need} more closed trade(s) needed")

    # bucket by conviction 1..10
    buckets = {}
    for t in graded:
        c = int(round(float(t["conviction"])))
        c = max(1, min(10, c))
        buckets.setdefault(c, []).append(1 if float(t["exit"]["pnl_pct"]) > 0 else 0)

    px_l, px_r = _PAD_L, _W - _PAD_R
    px_t, px_b = _PAD_T, _H - _PAD_B

    def cx(conv):  # conviction 1..10 -> x
        return _scale(conv, 1, 10, px_l, px_r)

    def cy(rate):  # hit-rate 0..1 -> y
        return _scale(rate, 0, 1, px_b, px_t)

    svg = [_open(), _title("calibration  ·  conviction vs realised hit-rate")]
    # y grid 0..100%
    for i in range(5):
        r = i / 4
        y = cy(r)
        svg.append(
            f'<line x1="{px_l}" y1="{y:.1f}" x2="{px_r}" y2="{y:.1f}" '
            f'stroke="{PALETTE["line"]}"/>'
        )
        svg.append(
            f'<text x="{px_l-7}" y="{y+4:.1f}" text-anchor="end" font-size="11" '
            f'fill="{PALETTE["ink_mute"]}">{int(r*100)}%</text>'
        )
    # x labels 1..10
    for c in range(1, 11):
        svg.append(
            f'<text x="{cx(c):.1f}" y="{px_b+18}" text-anchor="middle" '
            f'font-size="11" fill="{PALETTE["ink_mute"]}">{c}</text>'
        )
    # 45 degree diagonal: conviction c implies expected hit-rate c/10
    svg.append(
        f'<line x1="{cx(1):.1f}" y1="{cy(0.1):.1f}" x2="{cx(10):.1f}" '
        f'y2="{cy(1.0):.1f}" stroke="{PALETTE["ink_mute"]}" stroke-width="1.4" '
        f'stroke-dasharray="5 4"/>'
    )
    # realised points (radius ~ sample size)
    pts = []
    for c in sorted(buckets):
        vals = buckets[c]
        rate = sum(vals) / len(vals)
        r = 3 + min(8, len(vals))
        svg.append(
            f'<circle cx="{cx(c):.1f}" cy="{cy(rate):.1f}" r="{r:.1f}" '
            f'fill="{PALETTE["gold"]}" fill-opacity="0.85"/>'
        )
        svg.append(
            f'<text x="{cx(c):.1f}" y="{cy(rate)-r-4:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{PALETTE["ink_soft"]}">n={len(vals)}</text>'
        )
        pts.append((cx(c), cy(rate)))
    if len(pts) > 1:
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        svg.append(
            f'<polyline points="{path}" fill="none" stroke="{PALETTE["gold"]}" '
            f'stroke-width="1.6"/>'
        )
    svg.append(_legend([("realised", PALETTE["gold"], False),
                        ("perfect calibration", PALETTE["ink_mute"], True)]))
    svg.append("</svg>")
    return "".join(svg)


# --------------------------------------------------------------------------
# 13c -- VIX TERM STRUCTURE
# --------------------------------------------------------------------------
def vix_term_structure(points):
    """points: list of {"label","value"} across VIX9D/VIX/VIX3M/VIX6M."""
    pts = [p for p in (points or []) if isinstance(p.get("value"), (int, float))]
    if len(pts) < 2:
        return _placeholder("VIX term structure: unverified")
    labels = [p["label"] for p in pts]
    values = [float(p["value"]) for p in pts]
    vmin, vmax = _nice_bounds(values, 0.18)

    shape = "contango" if values[-1] > values[0] else "backwardation"
    color = PALETTE["green"] if shape == "contango" else PALETTE["red"]

    svg = [_open(), _title(f"VIX term structure  ·  {shape}")]
    svg.append(_grid_and_yaxis(vmin, vmax, "{:.1f}", ticks=4))
    svg.append(_xlabels(labels))
    svg.append(_polyline(values, vmin, vmax, color, width=2.6))
    svg.append("</svg>")
    return "".join(svg)


# --------------------------------------------------------------------------
# 13d -- YIELD CURVE
# --------------------------------------------------------------------------
def yield_curve(points):
    """points: list of {"label","value"} across 2s/5s/10s/30s UST."""
    pts = [p for p in (points or []) if isinstance(p.get("value"), (int, float))]
    if len(pts) < 2:
        return _placeholder("UST curve: unverified")
    labels = [p["label"] for p in pts]
    values = [float(p["value"]) for p in pts]
    vmin, vmax = _nice_bounds(values, 0.22)

    svg = [_open(), _title("UST yield curve  ·  2s / 5s / 10s / 30s (%)")]
    svg.append(_grid_and_yaxis(vmin, vmax, "{:.2f}", ticks=4))
    svg.append(_xlabels(labels))
    svg.append(_polyline(values, vmin, vmax, PALETTE["ink"], width=2.6))
    svg.append("</svg>")
    return "".join(svg)


if __name__ == "__main__":  # quick visual smoke test
    demo_closed = [
        {"conviction": 7, "exit": {"date": "2026-05-10", "pnl_pct": 2.1}},
        {"conviction": 5, "exit": {"date": "2026-05-14", "pnl_pct": -1.3}},
        {"conviction": 8, "exit": {"date": "2026-05-20", "pnl_pct": 3.4}},
    ]
    out = (
        "<html><body style='max-width:640px;margin:auto'>"
        + equity_curve(demo_closed)
        + calibration(demo_closed)
        + vix_term_structure([
            {"label": "VIX9D", "value": 14.2},
            {"label": "VIX", "value": 15.1},
            {"label": "VIX3M", "value": 16.8},
            {"label": "VIX6M", "value": 17.9},
        ])
        + yield_curve([
            {"label": "2Y", "value": 3.82},
            {"label": "5Y", "value": 3.91},
            {"label": "10Y", "value": 4.18},
            {"label": "30Y", "value": 4.55},
        ])
        + "</body></html>"
    )
    with open("charts_demo.html", "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote charts_demo.html", datetime.now())
