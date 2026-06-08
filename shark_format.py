#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""shark_format.py — the "shark tank format" renderer (standard library only).

Emits a 4-page, two-halves brief from the same `brief` dict + trades + earnings
that book.py consumes. Pages share a header + hamburger nav; every page carries a
sticky right rail with a live TradingView market-quotes widget (equities / FX /
rates / commodities). Detailed sub-sections on Insights are embedded as half-width
iframes; the trade book on Trade Ideas is an expandable <details> accordion.

    import shark_format
    shark_format.render_all(brief, trades, regime_log)   # writes index/insights/earnings/trades + frag/*

Reuses book.py (escaping, progress math) and earnings.py (earnings section) as-is.
"""

import os
import html as _html
from datetime import date, datetime

import book
import earnings

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG_DIR = os.path.join(HERE, "frag")
TODAY = date.today().isoformat()


def e(s):
    return _html.escape(str(s)) if s is not None else ""


# --------------------------------------------------------------------------
# Shared CSS — the two-halves Anthropic design language (from market_brief.html)
# --------------------------------------------------------------------------
CSS = """
:root{--bg:#fff;--surface:#f7f7f5;--ink:#1a1a1a;--ink-soft:#6b6b6b;--ink-mute:#9a9a9a;
--gold:#b8960c;--red:#c0392b;--green:#1a7a45;--line:rgba(0,0,0,.1);--rad:8px;--rad-lg:12px;
--font:-apple-system,"Helvetica Neue",sans-serif;--serif:Georgia,"Times New Roman",serif}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.65;margin:0;padding:0;-webkit-font-smoothing:antialiased}
a{color:inherit}
.topbar{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.92);backdrop-filter:blur(8px);border-bottom:.5px solid var(--line);display:flex;align-items:center;gap:14px;padding:.7rem 1.2rem}
.burger{cursor:pointer;border:none;background:none;padding:6px;display:flex;flex-direction:column;gap:4px}
.burger span{width:20px;height:2px;background:var(--ink);display:block}
.brand{font-family:var(--serif);font-size:18px;font-weight:400}
.brand b{color:var(--gold);font-weight:400}
.navwrap{margin-left:auto;font-size:11px;color:var(--ink-mute);letter-spacing:.08em;text-transform:uppercase}
.menu{display:none;position:fixed;top:0;left:0;height:100%;width:260px;background:var(--bg);border-right:.5px solid var(--line);box-shadow:2px 0 24px rgba(0,0,0,.06);z-index:60;padding:1.4rem 1.1rem}
.menu.open{display:block}
.menu .mh{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-mute);margin:0 0 1rem}
.menu a{display:block;padding:.7rem .6rem;border-radius:var(--rad);text-decoration:none;font-size:15px;margin-bottom:2px}
.menu a:hover{background:var(--surface)}
.menu a.active{background:var(--surface);color:var(--gold);font-weight:500}
.scrim{display:none;position:fixed;inset:0;background:rgba(0,0,0,.18);z-index:55}
.scrim.open{display:block}
.page{max-width:1400px;margin:0 auto;padding:1.6rem 2rem 4rem}
.masthead{border-bottom:.5px solid var(--line);padding-bottom:1rem;margin-bottom:1.5rem}
.regime-tag{display:inline-block;font-size:10px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);border:.5px solid var(--gold);border-radius:20px;padding:2px 10px;margin-bottom:.7rem}
.article-title{font-family:var(--serif);font-size:2rem;font-weight:400;line-height:1.25;margin:0 0 .4rem}
.meta{font-size:11px;color:var(--ink-mute);letter-spacing:.08em;text-transform:uppercase}
.two-col{display:grid;grid-template-columns:1fr 380px;gap:2.5rem;align-items:start}
@media(max-width:960px){.two-col{grid-template-columns:1fr}}
.lhs{min-width:0}.rhs{min-width:0}
.section-label{font-size:10px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-mute);margin:1.9rem 0 .8rem}
.wrap-body{font-family:var(--serif);font-size:16px;line-height:1.8}
.wrap-body p{margin:0 0 1rem}.wrap-body strong{font-weight:700}
.theme-line{border-left:2px solid var(--gold);padding:.6rem .9rem;background:var(--surface);border-radius:0 var(--rad) var(--rad) 0;margin:1rem 0;font-size:13px;font-weight:500;line-height:1.5}
.takeaways{list-style:none;padding:0;margin:0}
.takeaways li{position:relative;padding:.45rem 0 .45rem 1.2rem;border-bottom:.5px solid var(--line);font-size:14px;line-height:1.55}
.takeaways li:before{content:"";position:absolute;left:0;top:.95rem;width:6px;height:6px;border-radius:50%;background:var(--gold)}
.scen-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin:.5rem 0}
@media(max-width:760px){.scen-grid{grid-template-columns:1fr}}
.scen{border:.5px solid var(--line);border-top:2px solid var(--line);border-radius:var(--rad);padding:.9rem 1rem;background:var(--bg)}
.scen.bull{border-top-color:var(--green)}.scen.base{border-top-color:var(--gold)}.scen.bear{border-top-color:var(--red)}
.scen .sh{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute);display:flex;justify-content:space-between;margin-bottom:.5rem}
.scen .st{font-size:13px;font-weight:600;margin-bottom:.4rem;line-height:1.4}
.scen .sb{font-size:12px;color:var(--ink-soft);line-height:1.55}
.cardgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.trade-card{background:var(--bg);border:.5px solid var(--line);border-radius:var(--rad-lg);padding:1rem 1.1rem}
.tc-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:.7rem}
.tc-name{font-size:14px;font-weight:600;line-height:1.35}
.tc-class{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);margin-top:3px}
.conv-badge{font-size:11px;font-weight:500;background:var(--surface);border:.5px solid var(--line);border-radius:20px;padding:2px 10px;white-space:nowrap}
.tc-row{display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:.5px solid var(--line)}
.tc-row:last-of-type{border-bottom:none}.tc-k{color:var(--ink-mute)}.tc-v{font-weight:500}
.conv-bar{display:flex;gap:3px;align-items:center;margin:.6rem 0}
.pip{width:16px;height:4px;border-radius:2px;background:var(--line)}.pip.on{background:var(--gold)}
.conv-detail{font-size:10px;color:var(--ink-mute);margin-left:6px}
.tc-thesis{font-size:12px;color:var(--ink-soft);line-height:1.6;margin-top:.6rem;padding-top:.6rem;border-top:.5px solid var(--line)}
.iframe-2col{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:.5rem}
@media(max-width:760px){.iframe-2col{grid-template-columns:1fr}}
.iframe-2col iframe{width:100%;height:340px;border:.5px solid var(--line);border-radius:var(--rad);background:var(--bg)}
.bookframe{width:100%;height:520px;border:.5px solid var(--line);border-radius:var(--rad);background:var(--bg)}
table.cal{border-collapse:collapse;width:100%;font-size:13px}
table.cal th,table.cal td{text-align:left;padding:7px 9px;border-bottom:.5px solid var(--line);vertical-align:top}
table.cal th{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);font-weight:500}
.cal .ev{color:var(--gold);font-weight:500}.g{color:var(--green)}.r{color:var(--red)}.mute{color:var(--ink-mute)}
.one-chart{background:var(--surface);border-radius:var(--rad);padding:1rem 1.2rem;font-family:var(--serif);font-size:15px;line-height:1.7}
.foot{font-size:11px;color:var(--ink-mute);margin-top:3rem;padding-top:1rem;border-top:.5px solid var(--line);line-height:1.8}
.tv-wrap{border:.5px solid var(--line);border-radius:var(--rad);overflow:hidden}
.rhs .section-label{margin-top:1.4rem}.rhs .section-label:first-child{margin-top:0}
.rates-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.rtile{background:var(--surface);border:.5px solid var(--line);border-radius:8px;padding:.5rem .7rem}
.rtile .rl{font-size:10px;color:var(--ink-mute);margin-bottom:2px}
.rtile .rv{font-size:15px;font-weight:600;font-variant-numeric:tabular-nums}
.rtile .rc{font-size:11px}
.asof{font-size:10px;color:var(--ink-mute);margin-top:.5rem;letter-spacing:.04em}
"""

NAV = [
    ("index.html", "Summary", "Market Map · overnight read"),
    ("insights.html", "Insights", "the detailed map"),
    ("earnings.html", "Earnings", "Earnings Intelligence"),
    ("trades.html", "Trade Ideas", "ideas + live book"),
]

# --------------------------------------------------------------------------
# TradingView live right rail (market-quotes widget — no key, live, all classes)
# --------------------------------------------------------------------------
# Symbols chosen to quote ~24h (CFD / continuous / TVC index) so cells are never
# blank when a cash market is shut — the widget then shows the last/prev-close level.
# showSymbolLogo:false (no icons); height sized to fit every row (no internal scroll).
TV_WIDGET = """
<div class="tv-wrap">
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-quotes.js" async>
  {
  "width":"100%","height":864,"colorTheme":"light","isTransparent":true,"locale":"en","showSymbolLogo":false,
  "symbolsGroups":[
    {"name":"Equities (live · 24h CFD)","symbols":[
      {"name":"CAPITALCOM:US500","displayName":"S&P 500"},
      {"name":"CAPITALCOM:US100","displayName":"Nasdaq 100"},
      {"name":"CAPITALCOM:US30","displayName":"Dow"},
      {"name":"CAPITALCOM:DE40","displayName":"DAX"},
      {"name":"CAPITALCOM:UK100","displayName":"FTSE 100"},
      {"name":"CAPITALCOM:J225","displayName":"Nikkei 225"},
      {"name":"KRX:KOSPI","displayName":"KOSPI"},
      {"name":"NASDAQ:SOX","displayName":"PHLX Semis"},
      {"name":"NASDAQ:AVGO","displayName":"Broadcom"}]},
    {"name":"FX","symbols":[
      {"name":"FX:EURUSD","displayName":"EUR/USD"},
      {"name":"FX:GBPUSD","displayName":"GBP/USD"},
      {"name":"FX:USDJPY","displayName":"USD/JPY"},
      {"name":"FX:AUDUSD","displayName":"AUD/USD"},
      {"name":"CAPITALCOM:DXY","displayName":"Dollar Index"}]},
    {"name":"Commodities","symbols":[
      {"name":"TVC:USOIL","displayName":"WTI"},
      {"name":"TVC:UKOIL","displayName":"Brent"},
      {"name":"TVC:GOLD","displayName":"Gold"},
      {"name":"TVC:SILVER","displayName":"Silver"},
      {"name":"TVC:VIX","displayName":"VIX"},
      {"name":"BINANCE:BTCUSDT","displayName":"Bitcoin"}]}
  ]}
  </script>
</div>
</div>
"""


# Live SOFR from the NY Fed public API (CORS-friendly); falls back to the baked
# value if the fetch fails. The rest of the rate tiles are last-close (no free feed).
RATES_JS = """
<script>
(function(){
  function set(id,v){var el=document.getElementById(id);if(el)el.textContent=v;}
  function pull(){
    fetch('https://markets.newyorkfed.org/api/rates/secured/sofr/last/1.json')
      .then(function(r){return r.json();})
      .then(function(j){
        var rr=(j.refRates||[])[0]||{};var p=rr.percentRate;
        if(typeof p==='number'&&p>0.5&&p<8){
          set('sofr-v',p.toFixed(2)+'%');
          set('sofr-c','live · NY Fed '+(rr.effectiveDate||''));
        }
      }).catch(function(){});
  }
  pull(); setInterval(pull,600000);
})();
</script>
"""


def _level_block(label, items, note=None):
    """Baked last-close tiles (used for equities + rates — the asset classes the free
    TradingView widget can't reliably show when their cash market is shut)."""
    if not items:
        return ""
    cells = []
    for r in items:
        cls = {"up": "g", "down": "r", "warn": "r"}.get(r.get("dir", ""), "mute")
        vid = f' id="{e(r["vid"])}"' if r.get("vid") else ""
        cid = f' id="{e(r["cid"])}"' if r.get("cid") else ""
        cells.append(
            f'<div class="rtile"><div class="rl">{e(r.get("name",""))}</div>'
            f'<div class="rv"{vid}>{e(r.get("level",""))}</div>'
            f'<div class="rc {cls}"{cid}>{e(r.get("chg",""))}</div></div>'
        )
    out = (f'<div class="section-label">{e(label)}</div>'
           '<div class="rates-grid">' + "".join(cells) + '</div>')
    if note:
        out += f'<div class="asof">{e(note)}</div>'
    return out


def _rhs(brief):
    # Live 24h widget on top (equities via CFD, FX, commodities); rates baked below
    # (no free 24h cash-yield feed). KOSPI/SOX are live in-session, last close otherwise.
    parts = ['<div class="section-label">Live levels · equities · FX · commodities</div>', TV_WIDGET]
    rt = brief.get("rates_levels", [])
    if rt:
        note = f'as of {rt[0]["asof"]} · SOFR auto-updates (NY Fed)' if rt[0].get("asof") else None
        parts.append(_level_block("Rates &amp; funding · last close", rt, note))
    theme = brief.get("dominant_theme", "")
    if theme:
        parts.append(f'<div class="theme-line">{e(theme)}</div>')
    parts.append(RATES_JS)
    return "".join(parts)


def _menu(active):
    links = []
    for href, label, _sub in NAV:
        cls = " class=\"active\"" if href == active else ""
        links.append(f'<a href="{href}"{cls}>{e(label)}</a>')
    return (
        '<div class="scrim" id="scrim" onclick="closeMenu()"></div>'
        '<nav class="menu" id="menu"><div class="mh">Shark Tank · Market Map</div>'
        + "".join(links) + "</nav>"
    )


def _topbar(active):
    return (
        '<div class="topbar">'
        '<button class="burger" onclick="openMenu()" aria-label="menu"><span></span><span></span><span></span></button>'
        '<div class="brand">Market Map <b>· Shark Tank</b></div>'
        f'<div class="navwrap">{e(dict((h,l) for h,l,_ in NAV).get(active,""))}</div>'
        '</div>'
    )


MENU_JS = (
    "<script>function openMenu(){document.getElementById('menu').classList.add('open');"
    "document.getElementById('scrim').classList.add('open');}"
    "function closeMenu(){document.getElementById('menu').classList.remove('open');"
    "document.getElementById('scrim').classList.remove('open');}</script>"
)


def _shell(active, title, regime, regime_note, lhs_html, brief):
    masthead = (
        '<div class="masthead">'
        + (f'<div class="regime-tag">{e(regime)}</div>' if regime else "")
        + f'<h1 class="article-title">{e(title)}</h1>'
        + f'<p class="meta">Pre-market intelligence brief &middot; {e(TODAY)} '
          f'&middot; generated {datetime.now():%H:%M} local &middot; self-graded book</p>'
        + (f'<p style="font-size:13px;color:var(--ink-soft);margin:.6rem 0 0">{e(regime_note)}</p>' if regime_note else "")
        + '</div>'
    )
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{e(title)} · Shark Tank Market Map</title><style>{CSS}</style></head><body>"
        + _menu(active) + _topbar(active)
        + '<div class="page">' + masthead
        + '<div class="two-col"><div class="lhs">' + lhs_html + '</div>'
        + '<div class="rhs">' + _rhs(brief) + '</div></div>'
        + '<div class="foot">Shark Tank format · live levels via TradingView · '
          'earnings via Finnhub · book self-graded. Not investment advice.</div>'
        + '</div>' + MENU_JS + "</body></html>"
    )


# --------------------------------------------------------------------------
# Component renderers
# --------------------------------------------------------------------------
def _scenarios(scenarios):
    if not scenarios:
        return ""
    tiles = []
    for s in scenarios:
        cls = s.get("kind", "base")
        tiles.append(
            f'<div class="scen {cls}"><div class="sh"><span>{e(s.get("label",""))}</span>'
            f'<span>{e(s.get("pct",""))}</span></div>'
            f'<div class="st">{e(s.get("headline",""))}</div>'
            f'<div class="sb">{e(s.get("body",""))}</div></div>'
        )
    return '<div class="scen-grid">' + "".join(tiles) + "</div>"


def _takeaways(items):
    if not items:
        return ""
    return '<ul class="takeaways">' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"


def _pips(score, total=10):
    try:
        n = int(round(float(score)))
    except (TypeError, ValueError):
        n = 0
    return "".join(f'<div class="pip {"on" if i < n else ""}"></div>' for i in range(total))


def _trade_tile(idea):
    cb = idea.get("conviction_breakdown", {}) or {}
    rubric = (f'gap({cb.get("gap",0)}/3) · catalyst({cb.get("catalyst",0)}/2) · '
              f'pos({cb.get("positioning",0)}/2) · confirm({cb.get("confirmation",0)}/2) · '
              f'stop({cb.get("stop_quality",0)}/1)')
    rows = [("Asset", idea.get("asset_class", "")), ("Structure", idea.get("structure", "")),
            ("Entry", idea.get("entry")), ("Stop", idea.get("stop")),
            ("Target", idea.get("target")), ("Horizon", idea.get("horizon", ""))]
    if idea.get("min_hold_days"):
        rows.append(("Min hold", f'{idea["min_hold_days"]}d'))
    row_html = "".join(f'<div class="tc-row"><span class="tc-k">{e(k)}</span>'
                       f'<span class="tc-v">{e(v)}</span></div>' for k, v in rows)
    kind = idea.get("_kind", "reactive")
    return (
        '<div class="trade-card"><div class="tc-top"><div>'
        f'<div class="tc-name">{e(idea.get("trade",""))}</div>'
        f'<div class="tc-class">{e(kind)} · {e(idea.get("asset_class",""))}</div></div>'
        f'<div class="conv-badge">{e(idea.get("conviction"))}/10</div></div>'
        + row_html
        + f'<div class="conv-bar">{_pips(idea.get("conviction"))}<span class="conv-detail">{rubric}</span></div>'
        + f'<div class="tc-thesis">{e(idea.get("thesis",""))}</div></div>'
    )


def _catalyst(rows):
    if not rows:
        return "<p class='mute'>no genuine-asymmetry events on the 5-day horizon</p>"
    out = ['<table class="cal"><thead><tr><th>Day</th><th>Date</th><th>Event</th>'
           '<th>Consensus</th><th>View</th><th>Asymmetry</th></tr></thead><tbody>']
    for r in rows:
        cls = {"up": "g", "down": "r"}.get(r.get("dir", ""), "mute")
        out.append(
            f'<tr><td>{e(r.get("day",""))}</td><td>{e(r.get("date",""))}</td>'
            f'<td class="ev">{e(r.get("event",""))}</td><td>{e(r.get("consensus",""))}</td>'
            f'<td>{e(r.get("view",""))}</td><td class="{cls}">{e(r.get("asymmetry",""))}</td></tr>'
        )
    out.append("</tbody></table>")
    return "".join(out)


# --------------------------------------------------------------------------
# Standalone iframe fragments
# --------------------------------------------------------------------------
FRAG_CSS = """
*{box-sizing:border-box}body{margin:0;padding:16px 18px;font-family:-apple-system,"Helvetica Neue",sans-serif;
color:#1a1a1a;font-size:13.5px;line-height:1.6;background:#fff}
h3{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#9a9a9a;margin:0 0 .8rem;border-bottom:.5px solid rgba(0,0,0,.1);padding-bottom:.5rem}
p{margin:0 0 .7rem}strong{font-weight:600}.g{color:#1a7a45}.r{color:#c0392b}.gold{color:#b8960c}
.amm{margin:0 0 .8rem;padding-bottom:.6rem;border-bottom:.5px solid rgba(0,0,0,.07)}
.amm .q{font-weight:600;margin-bottom:.2rem}.amm .a{color:#6b6b6b}
details{border:.5px solid rgba(0,0,0,.12);border-radius:8px;padding:.5rem .8rem;margin-bottom:8px;background:#fafaf9}
details[open]{background:#fff}summary{cursor:pointer;font-weight:600;font-size:13px;list-style:none;display:flex;justify-content:space-between;gap:8px}
summary::-webkit-details-marker{display:none}
.det-row{display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:.5px dotted rgba(0,0,0,.1)}
.det-k{color:#9a9a9a}.pill{font-size:10px;border:.5px solid rgba(0,0,0,.15);border-radius:20px;padding:1px 7px;color:#6b6b6b}
.det-thesis{font-size:12px;color:#6b6b6b;margin-top:.5rem;line-height:1.55}
"""


def _frag_doc(title, body):
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<style>{FRAG_CSS}</style></head><body><h3>{e(title)}</h3>{body}</body></html>")


def _client_ammo_body(rows):
    if not rows:
        return "<p class='mute'>—</p>"
    return "".join(f'<div class="amm"><div class="q">{e(r.get("q",""))}</div>'
                   f'<div class="a">{e(r.get("a",""))}</div></div>' for r in rows)


def _book_accordion(trades):
    out = []
    for t in trades.get("open", []) + trades.get("closed", []):
        closed = "exit" in t
        pl = t.get("current_pnl_pct")
        pl_cls = "g" if (pl or 0) > 0 else ("r" if (pl or 0) < 0 else "mute")
        status = (f'<span class="{pl_cls}">{pl:+.2f}%</span>' if pl is not None else "—")
        if closed:
            ex = t["exit"]
            status = f'<span class="r">{e(ex.get("result"))} {ex.get("pnl_pct"):+.2f}%</span>'
        rows = [
            ("Asset class", t.get("asset_class", "")),
            ("Structure", t.get("structure", "")),
            ("Opened", t.get("opened", "")),
            ("Entry", t.get("entry")),
            ("Current", t.get("current")),
            ("Stop", t.get("stop")),
            ("Target", t.get("target")),
            ("Conviction", f'{t.get("conviction","")}/10'),
            ("Horizon", t.get("horizon", "")),
        ]
        if t.get("min_hold_days"):
            rows.append(("Min hold", f'{t["min_hold_days"]}d'))
        cb = t.get("conviction_breakdown") or {}
        if cb:
            rows.append(("Score", f'gap{cb.get("gap",0)} · cat{cb.get("catalyst",0)} · '
                                  f'pos{cb.get("positioning",0)} · conf{cb.get("confirmation",0)} · '
                                  f'stop{cb.get("stop_quality",0)}'))
        det_rows = "".join(f'<div class="det-row"><span class="det-k">{e(k)}</span>'
                           f'<span>{e(v)}</span></div>' for k, v in rows)
        out.append(
            f'<details><summary><span><span class="pill">{e(t.get("id",""))}</span> '
            f'{e(t.get("trade",""))}</span>{status}</summary>'
            + det_rows
            + f'<div class="det-thesis"><strong>Thesis &amp; what I\'m watching:</strong> '
              f'{e(t.get("thesis",""))}</div></details>'
        )
    return "".join(out) or "<p class='mute'>no positions</p>"


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def _page_summary(brief):
    lhs = []
    lhs.append('<div class="section-label">The overnight read</div>')
    lhs.append(f'<div class="wrap-body">{brief.get("summary_narrative", brief.get("wrap",""))}</div>')
    if brief.get("takeaways"):
        lhs.append('<div class="section-label">Today\'s takeaways</div>')
        lhs.append(_takeaways(brief["takeaways"]))
    if brief.get("scenarios"):
        lhs.append('<div class="section-label">Scenarios · Bull / Base / Bear</div>')
        lhs.append(_scenarios(brief["scenarios"]))
    if brief.get("tape_missing"):
        lhs.append('<div class="section-label">What the Tape Is Missing</div>')
        lhs.append(f'<div class="wrap-body" style="font-size:14px">{brief["tape_missing"]}</div>')
    return "".join(lhs)


def _page_insights(brief):
    lhs = []
    lhs.append('<div class="section-label">The detailed map</div>')
    lhs.append(f'<div class="wrap-body">{brief.get("insights_layers", brief.get("wrap",""))}</div>')
    if brief.get("one_chart"):
        lhs.append('<div class="section-label">Today\'s One Chart That Matters</div>')
        lhs.append(f'<div class="one-chart">{brief["one_chart"]}</div>')
    lhs.append('<div class="section-label">Catalyst Calendar (5 trading days)</div>')
    lhs.append(_catalyst(brief.get("catalyst_calendar", [])))
    lhs.append('<div class="section-label">Deep dives</div>')
    lhs.append(
        '<div class="iframe-2col">'
        '<iframe src="frag/consensus.html" title="Consensus"></iframe>'
        '<iframe src="frag/talking.html" title="Talking Points"></iframe>'
        '<iframe src="frag/correlation.html" title="Correlation Regime"></iframe>'
        '<iframe src="frag/volskew.html" title="Vol & Skew"></iframe>'
        '<iframe src="frag/sectorrv.html" title="Sector & RV"></iframe>'
        '<iframe src="frag/positioning.html" title="Positioning & Flows"></iframe>'
        '</div>'
    )
    return "".join(lhs)


def _page_earnings(brief):
    body = earnings.render_earnings_section(brief.get("earnings_ideas", []))
    if not body:
        body = "<p class='mute'>No qualifying earnings in the window.</p>"
    return '<div class="section-label">Earnings Intelligence · Finnhub-sourced</div>' + body


def _page_trades(brief):
    lhs = []
    reactive = [dict(i, _kind="reactive") for i in brief.get("new_ideas", [])]
    prepos = [dict(i, _kind="pre-position") for i in brief.get("pre_position_ideas", [])]
    lhs.append('<div class="section-label">New Trade Ideas</div>')
    lhs.append('<div class="cardgrid">' + "".join(_trade_tile(i) for i in reactive + prepos) + '</div>')
    lhs.append('<div class="section-label">Live Book · click any trade to expand</div>')
    lhs.append('<iframe src="frag/book.html" class="bookframe" title="Live book"></iframe>')
    return "".join(lhs)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def render_all(brief, trades, regime_log=None):
    os.makedirs(FRAG_DIR, exist_ok=True)
    regime = brief.get("regime", "")
    note = brief.get("regime_note", "")

    pages = {
        "index.html":    ("Summary",     "Market Map / Summary",   _page_summary(brief)),
        "insights.html": ("Insights",    "Market Map / Insights",  _page_insights(brief)),
        "earnings.html": ("Earnings",    "Earnings Intelligence",  _page_earnings(brief)),
        "trades.html":   ("Trade Ideas", "Trade Ideas + Live Book", _page_trades(brief)),
    }
    for fname, (active, title, lhs) in pages.items():
        htmldoc = _shell(fname, title, regime, note, lhs, brief)
        with open(os.path.join(HERE, fname), "w", encoding="utf-8") as f:
            f.write(htmldoc)

    # iframe fragments
    frags = {
        "consensus.html":   ("The Consensus · Bid / Offer", brief.get("consensus", "")),
        "talking.html":     ("Talking Points Today", _client_ammo_body(brief.get("client_ammo", []))),
        "correlation.html": ("Correlation Regime", brief.get("correlation_regime", "")),
        "volskew.html":     ("Vol & Skew", brief.get("vol_skew", "")),
        "sectorrv.html":    ("Sector & RV", brief.get("sector_rv", "")),
        "positioning.html": ("Positioning & Flows", brief.get("positioning", "")),
        "book.html":        ("Live Book", _book_accordion(trades)),
    }
    for fname, (title, body) in frags.items():
        with open(os.path.join(FRAG_DIR, fname), "w", encoding="utf-8") as f:
            f.write(_frag_doc(title, body))

    book.log(f"shark format written: {', '.join(pages)} + frag/*")
