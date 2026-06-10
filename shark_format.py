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
/* ---- client book module (Portfolio + Derivative Ideas) ---- */
.statgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:.4rem 0 .5rem}
.stat{background:var(--surface);border:.5px solid var(--line);border-radius:var(--rad);padding:.7rem .85rem}
.stat .sl{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:3px}
.stat .sv{font-size:20px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.1}
.stat .ss{font-size:11px;color:var(--ink-soft);margin-top:2px}
.holdtbl{width:100%;border-collapse:collapse;font-size:13px}
.holdtbl th{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mute);font-weight:500;text-align:left;padding:7px 8px;border-bottom:.5px solid var(--line)}
.holdtbl td{padding:8px;border-bottom:.5px solid var(--line);vertical-align:middle}
.holdtbl tr:last-child td{border-bottom:none}
.holdtbl .nm{font-weight:600}.holdtbl .tk{font-size:11px;color:var(--ink-mute);font-family:ui-monospace,monospace}
.num{text-align:right;font-variant-numeric:tabular-nums}
.wbar{position:relative;height:5px;background:var(--line);border-radius:3px;width:64px;margin-top:4px}
.wbar>span{position:absolute;left:0;top:0;height:100%;border-radius:3px;background:var(--ink-soft)}
.wbar.flag>span{background:var(--gold)}.wbar.act>span,.wbar.urgent>span{background:var(--red)}
.vpill{font-size:10px;font-weight:600;letter-spacing:.04em;border-radius:20px;padding:2px 9px;white-space:nowrap;border:.5px solid}
.v-like{color:var(--green);border-color:var(--green);background:rgba(26,122,69,.06)}
.v-neutral{color:var(--ink-soft);border-color:var(--line);background:var(--surface)}
.v-avoid{color:var(--red);border-color:var(--red);background:rgba(192,57,43,.06)}
.v-hedge{color:var(--gold);border-color:var(--gold);background:rgba(184,150,12,.06)}
.cflag{font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--red);font-weight:600;margin-left:5px}
.cflag.flag{color:var(--gold)}
.srcdot{display:inline-block;width:6px;height:6px;border-radius:50%;vertical-align:middle;margin-right:3px}
.src-sourced{background:var(--green)}.src-estimated{background:var(--gold)}.src-unverified{background:var(--red)}
.viewcard{border:.5px solid var(--line);border-radius:var(--rad);padding:.7rem .9rem;margin-bottom:8px;background:var(--bg)}
.viewcard .vh{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:.35rem}
.viewcard .vt{font-weight:600;font-size:13px}
.viewcard .vr{font-size:12.5px;color:var(--ink-soft);line-height:1.55;margin-bottom:.4rem}
.viewcard ul{margin:.2rem 0 .3rem;padding-left:1.1rem}.viewcard li{font-size:11.5px;color:var(--ink-soft);margin-bottom:2px}
.viewcard .lock{font-size:11px;color:var(--ink-mute);border-left:2px solid var(--gold);padding:.25rem .6rem;background:var(--surface);border-radius:0 6px 6px 0;margin-top:.3rem}
.idea{border:.5px solid var(--line);border-radius:var(--rad-lg);padding:1rem 1.15rem;margin-bottom:12px;background:var(--bg)}
.idea.fire{border-left:3px solid var(--gold)}.idea.watch{border-left:3px solid var(--ink-mute)}.idea.suppress{border-left:3px solid var(--line);background:var(--surface)}
.idea .ih{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:.5rem}
.idea .it{font-size:15px;font-weight:600;line-height:1.35}
.idea .inum{color:var(--ink-mute);font-weight:600}
.idea .meta-row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:.6rem}
.tag{font-size:10px;letter-spacing:.04em;border:.5px solid var(--line);border-radius:20px;padding:1px 8px;color:var(--ink-soft);background:var(--surface)}
.rules-tag{font-size:10px;font-weight:600;letter-spacing:.06em;color:var(--gold);border:.5px solid var(--gold);border-radius:20px;padding:1px 8px}
.tier{font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;border-radius:6px;padding:2px 8px}
.tier.fire{color:#fff;background:var(--gold)}.tier.watch{color:var(--ink-soft);background:var(--surface);border:.5px solid var(--line)}.tier.suppress{color:var(--ink-mute);background:var(--surface);border:.5px solid var(--line)}
.conv8{display:flex;align-items:center;gap:8px;margin:.2rem 0 .55rem;flex-wrap:wrap}
.pips8{display:flex;gap:3px}.pip8{width:20px;height:5px;border-radius:2px;background:var(--line)}.pip8.on{background:var(--gold)}
.subs{font-size:11px;color:var(--ink-mute);display:flex;gap:10px;flex-wrap:wrap}
.idea .blk{font-size:13px;line-height:1.6;margin:.45rem 0}
.idea .blk b{font-weight:600}
.idea .moves{color:var(--ink-soft)}
.idea .note{font-size:12.5px;color:var(--ink-soft);background:var(--surface);border-radius:var(--rad);padding:.55rem .75rem;margin-top:.5rem;line-height:1.55}
.idea .risk{font-size:11.5px;color:var(--red);border-left:2px solid var(--red);padding:.3rem .6rem;margin-top:.5rem;line-height:1.5;background:rgba(192,57,43,.04);border-radius:0 6px 6px 0}
.findings{list-style:none;padding:0;margin:.2rem 0 0}
.findings li{position:relative;padding:.4rem 0 .4rem 1.1rem;border-bottom:.5px solid var(--line);font-size:13px;line-height:1.5;color:var(--ink-soft)}
.findings li:before{content:"";position:absolute;left:0;top:.85rem;width:5px;height:5px;border-radius:50%;background:var(--gold)}
.findings li b{color:var(--ink)}
"""

NAV = [
    ("index.html", "Summary", "Market Map · overnight read"),
    ("insights.html", "Insights", "the detailed map"),
    ("earnings.html", "Earnings", "Earnings Intelligence"),
    ("trades.html", "Trade Ideas", "ideas + live book"),
    ("portfolio.html", "Portfolio", "Fable · client book"),
    ("ideas.html", "Derivative Ideas", "structured-product scan"),
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
        parts.append(_level_block("Rates & funding · last close", rt, note))
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


def _shell(active, title, regime, regime_note, lhs_html, brief, masthead_html=None):
    masthead = masthead_html or (
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
    if brief.get("ideas_note"):
        lhs.append('<div class="section-label">Positioning stance today</div>')
        lhs.append(f'<div class="wrap-body" style="font-size:14px">{brief["ideas_note"]}</div>')
    lhs.append('<div class="section-label">New Trade Ideas</div>')
    cards = "".join(_trade_tile(i) for i in reactive + prepos)
    lhs.append('<div class="cardgrid">' + cards + '</div>' if cards
               else '<p class="mute" style="font-size:13px">No new idea today — into a binary print, forcing a trade is the trade.</p>')
    lhs.append('<div class="section-label">Live Book · click any trade to expand</div>')
    lhs.append('<iframe src="frag/book.html" class="bookframe" title="Live book"></iframe>')
    return "".join(lhs)


# --------------------------------------------------------------------------
# Client book module — Portfolio + Derivative Ideas
# --------------------------------------------------------------------------
_VIEW_CLS = {"LIKE": "v-like", "NEUTRAL": "v-neutral", "AVOID": "v-avoid",
             "LIKE-as-hedge": "v-hedge", "-": "v-neutral"}
_CLASS_SHORT = {"equity": "Equity", "equity_etf": "ETF", "govt_bond": "Govt bond",
                "corp_bond": "Corp bond", "commodity_etc": "Gold ETC"}


def _eurm(n):
    return f"&euro;{n/1e6:.1f}m"


def _ccy(cur):
    return "$" if cur == "USD" else "&euro;"


def _view_pill(view):
    return f'<span class="vpill {_VIEW_CLS.get(view, "v-neutral")}">{e(view)}</span>'


def _portfolio_masthead(scan):
    c, m = scan["client"], scan["metrics"]
    return (
        '<div class="masthead">'
        f'<div class="regime-tag">{e(c.get("base_currency","EUR"))} base &middot; MiFID Professional</div>'
        f'<h1 class="article-title">{e(c.get("display_name","Fable"))} / Portfolio</h1>'
        f'<p class="meta">Client book scan &middot; as of {e(c.get("as_of", scan["as_of"]))} '
        f'&middot; marks live via TradingView &middot; {_eurm(m["total_eur"])} &middot; not investment advice</p>'
        f'<p style="font-size:13px;color:var(--ink-soft);margin:.6rem 0 0">'
        f'{_eurm(m["total_eur"])} across {len(scan["positions"])} holdings + cash. '
        f'Largest position {e(m["largest"]["ticker"])} at {m["largest"]["weight_pct"]}% (policy cap 10%); '
        f'{m["usd_pct"]}% USD against a EUR base; {m["cash_pct"]}% idle cash.</p>'
        '</div>'
    )


def _ideas_masthead(scan):
    cnt = scan["counts"]
    return (
        '<div class="masthead">'
        '<div class="regime-tag">Book Scanner &middot; Ruleset v2</div>'
        '<h1 class="article-title">Portfolio / Derivative Ideas</h1>'
        f'<p class="meta">{e(scan["client"].get("display_name","Fable"))} book scan &middot; {e(scan["as_of"])} '
        f'&middot; {cnt["fired"]} fired &middot; {cnt["watch"]} watch &middot; {cnt["suppressed"]} suppressed</p>'
        f'<p style="font-size:13px;color:var(--ink-soft);margin:.6rem 0 0">'
        f'The House View Engine ran first, then the structure ladder. Every idea is consistency-locked to today’s '
        f'market-map regime &mdash; <b>{e(scan.get("regime",""))}</b> &mdash; so no single-name structure contradicts the brief’s live bear case.</p>'
        '</div>'
    )


def _holdings_table(positions):
    rows = []
    for p in positions:
        w = p.get("weight_pct", 0)
        tier = p.get("conc_tier", "")
        flag = (f'<span class="cflag {tier}">{tier}</span>' if tier else "")
        pnl = p.get("pnl_pct")
        pnl_cls = "g" if (pnl or 0) > 0 else ("r" if (pnl or 0) < 0 else "mute")
        day = p.get("day_chg_pct")
        day_html = (f'<span class="{"g" if day>0 else ("r" if day<0 else "mute")}">{day:+.2f}%</span>'
                    if isinstance(day, (int, float)) else '<span class="mute">&mdash;</span>')
        iv = p.get("iv_pct")
        conf = p.get("iv_confidence", "estimated")
        iv_lab = "live" if conf == "sourced" else "est"
        iv_html = (f'<span class="srcdot src-{e(conf)}"></span>{iv:.0f}% &middot; '
                   f'{p.get("iv_percentile_est","?")}th <span class="mute">{iv_lab}</span>'
                   if iv else '<span class="mute">&mdash;</span>')
        mark = p.get("mark_price")
        unit = "" if p.get("quantity_type") == "nominal" else ""
        mark_html = f'{_ccy(p["currency"])}{mark:,.2f}' if isinstance(mark, (int, float)) else "&mdash;"
        rows.append(
            '<tr>'
            f'<td><div class="nm">{e(p["name"])}</div><div class="tk">{e(p["ticker"])}</div></td>'
            f'<td class="mute">{e(_CLASS_SHORT.get(p.get("asset_class",""), p.get("asset_class","")))}</td>'
            f'<td class="num">{w}%{flag}<div class="wbar {tier}"><span style="width:{min(100,w*3)}%"></span></div></td>'
            f'<td class="num">{mark_html}</td>'
            f'<td class="num {pnl_cls}">{pnl:+.1f}%</td>'
            f'<td class="num">{day_html}</td>'
            f'<td>{_view_pill(p.get("house_view","-"))}</td>'
            f'<td class="num">{iv_html}</td>'
            '</tr>'
        )
    return ('<table class="holdtbl"><thead><tr>'
            '<th>Holding</th><th>Class</th><th class="num">Weight</th><th class="num">Mark</th>'
            '<th class="num">P&amp;L</th><th class="num">Day</th><th>House view</th><th class="num">ATM IV</th>'
            '</tr></thead><tbody>' + "".join(rows) + '</tbody></table>')


def _cash_liab_block(scan):
    c = scan["client"]; eurusd = c.get("fx_reference", {}).get("EURUSD", 1.154)
    out = ['<div class="section-label">Cash &amp; liabilities</div>', '<table class="holdtbl"><tbody>']
    for ca in scan.get("cash", []):
        out.append(
            f'<tr><td><div class="nm">{_ccy(ca["currency"])}{ca["amount"]:,.0f}</div>'
            f'<div class="tk">{e(ca["currency"])} cash &middot; {e(ca["id"])}</div></td>'
            f'<td class="mute">earning {ca.get("yield_pct",0)}%</td>'
            f'<td colspan="5" class="mute" style="font-size:12px">{e(ca.get("notes",""))}</td></tr>'
        )
    for l in scan.get("liabilities", []):
        out.append(
            f'<tr><td><div class="nm" style="color:var(--red)">&minus;{_ccy(l["currency"])}{l["annual"]:,.0f}/yr</div>'
            f'<div class="tk">{e(l["kind"])} &middot; to {e(l.get("until",""))}</div></td>'
            f'<td class="mute">liability</td>'
            f'<td colspan="5" class="mute" style="font-size:12px">{e(l.get("note",""))}</td></tr>'
        )
    out.append('</tbody></table>')
    return "".join(out)


def _findings(m):
    items = [
        f'<b>Concentration.</b> {e(m["largest"]["ticker"])} is {m["largest"]["weight_pct"]}% of the book on a ~10x gain, into earnings 24-Jun with options premium rich &mdash; collar, SBL against the hedged stock, then decumulate after the print.',
        f'<b>FX.</b> A EUR-base client is {m["usd_pct"]}% USD; net of the mortgage liability and earmarked cash the hedgeable mismatch is ~{m["net_usd_pct"]}% &mdash; seagull the residual after Thursday’s ECB.',
        '<b>Losses.</b> AVGO and LVMH are the harvest / reverse-convertible candidates; NVDA is the range-note (Phoenix/BREN) name &mdash; earnings-timing checked.',
        '<b>Bonds.</b> Both bonds are underwater on rates, not credit &mdash; a swap harvests the loss and roughly triples the running coupon. CPI and ECB are the timing gates.',
        f'<b>Cash.</b> {m["cash_pct"]}% idle &mdash; deposit campaign (EUR), T-bill ladder against the mortgage and a cash-secured NVDA put (USD).',
    ]
    return '<ul class="findings">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def _view_engine_panel(scan):
    out = ['<div class="section-label">House View Engine &middot; formed today, with receipts</div>']
    meta = scan.get("views_meta", {})
    if meta.get("note"):
        out.append(f'<p style="font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin:0 0 .8rem">{e(meta["note"])}</p>')
    for v in scan.get("house_views", []):
        ev = "".join(f"<li>{e(x)}</li>" for x in v.get("evidence", []))
        lock = (f'<div class="lock">Brief consistency: {e(v["brief_consistency"])}</div>'
                if v.get("brief_consistency") else "")
        out.append(
            '<div class="viewcard"><div class="vh">'
            f'<span class="vt">{e(v["ticker"])} {_view_pill(v["view"])}</span>'
            f'<span class="subs"><span class="srcdot src-{e(v.get("confidence","estimated"))}"></span>{e(v.get("confidence",""))}</span>'
            '</div>'
            f'<div class="vr">{e(v.get("rationale",""))}</div>'
            + (f'<ul>{ev}</ul>' if ev else "")
            + lock + '</div>'
        )
    return "".join(out)


def _page_portfolio(scan):
    m = scan["metrics"]
    lhs = ['<div class="section-label">Book at a glance</div>']
    lhs.append(
        '<div class="statgrid">'
        f'<div class="stat"><div class="sl">AUM</div><div class="sv">{_eurm(m["total_eur"])}</div><div class="ss">{len(scan["positions"])} holdings + cash</div></div>'
        f'<div class="stat"><div class="sl">Largest</div><div class="sv" style="color:var(--red)">{m["largest"]["weight_pct"]}%</div><div class="ss">{e(m["largest"]["ticker"])} &middot; cap 10%</div></div>'
        f'<div class="stat"><div class="sl">USD exposure</div><div class="sv">{m["usd_pct"]}%</div><div class="ss">net ~{m["net_usd_pct"]}% after liabilities</div></div>'
        f'<div class="stat"><div class="sl">Idle cash</div><div class="sv" style="color:var(--gold)">{m["cash_pct"]}%</div><div class="ss">{_eurm(m["cash_eur"])} earning ~0</div></div>'
        '</div>'
    )
    lhs.append('<div class="section-label">Headline scanner findings</div>')
    lhs.append(_findings(m))
    lhs.append('<div class="section-label">Holdings &middot; marked live</div>')
    lhs.append(_holdings_table(scan["positions"]))
    if scan.get("refresh_notes"):
        lhs.append(f'<div class="asof">Live refresh: {e("; ".join(scan["refresh_notes"]))}. '
                   'Bonds derived from yields; gold from spot; ATM IV estimated until ivol_history.json reaches 60d.</div>')
    lhs.append(_cash_liab_block(scan))
    lhs.append(_view_engine_panel(scan))
    lhs.append('<div style="margin-top:1.5rem">'
               '<a href="ideas.html" style="font-size:13px;color:var(--gold);font-weight:600;text-decoration:none">'
               'See the structured-product scan &rarr; Derivative Ideas</a></div>')
    return "".join(lhs)


def _pips8(score):
    try:
        n = int(round(float(score)))
    except (TypeError, ValueError):
        n = 0
    return '<div class="pips8">' + "".join(
        f'<div class="pip8 {"on" if i < n else ""}"></div>' for i in range(8)) + '</div>'


def _idea_subs(i):
    labels = [("setup", "Setup"), ("pricing", "Pricing"), ("catalyst", "Catalyst"), ("fit", "Client fit")]
    parts = []
    for k, lab in labels:
        sc = i["subs"].get(k, 0)
        src = i["sub_src"].get(k, "estimated")
        parts.append(f'<span><span class="srcdot src-{e(src)}"></span>{lab} {sc}/2</span>')
    return '<span class="subs">' + "".join(parts) + '</span>'


def _render_idea(i):
    tier = i["tier"].lower()
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in i.get("tags", []))
    tickers = "".join(f'<span class="tag">{e(t)}</span>' for t in i.get("tickers", []))
    risk = (f'<div class="risk"><b>Risk:</b> {e(i["risk"])}</div>' if i.get("risk") else "")
    return (
        f'<div class="idea {tier}">'
        '<div class="ih">'
        f'<div class="it"><span class="inum">{i["num"]}.</span> {e(i["title"])}</div>'
        f'<span class="tier {tier}">{e(i["tier"])} &middot; {i["score"]}/8</span>'
        '</div>'
        '<div class="meta-row">'
        f'<span class="rules-tag">{e(i["rules"])}</span>{tickers}'
        '</div>'
        f'<div class="conv8">{_pips8(i["score"])}{_idea_subs(i)}</div>'
        f'<div class="blk">{e(i["what_it_is"])}</div>'
        f'<div class="blk moves"><b>What moves it:</b> {e(i["what_moves_it"])}</div>'
        f'<div class="note"><b>Client note:</b> {e(i["client_note"])}</div>'
        + risk
        + f'<div class="meta-row" style="margin-top:.6rem">{tags}</div>'
        '</div>'
    )


def _page_ideas(scan):
    lhs = []
    meta = scan.get("ivol_meta", {})
    lhs.append('<div class="section-label">Fired &middot; conviction &ge; 5/8</div>')
    lhs.append("".join(_render_idea(i) for i in scan["fired"]))
    if scan.get("watch"):
        lhs.append('<div class="section-label">Watch &middot; 3&ndash;4/8 &middot; promote on a data refresh</div>')
        lhs.append("".join(_render_idea(i) for i in scan["watch"]))
    if scan.get("suppressed"):
        lhs.append('<div class="section-label">Suppressed &middot; rule fired, override held</div>')
        lhs.append("".join(_render_idea(i) for i in scan["suppressed"]))
    lhs.append(
        '<div class="asof" style="margin-top:1.4rem">'
        'Conviction /8 = setup &middot; pricing &middot; catalyst &middot; client fit (0&ndash;2 each). '
        'Green dot = sourced, gold = estimated, red = unverified. '
        f'{e(meta.get("source", meta.get("honesty","")))} '
        'Issuer credit: every note is senior unsecured paper &mdash; cap any single issuer at 20% of the structure book. '
        'Demo book, not investment advice.</div>'
    )
    return "".join(lhs)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def render_all(brief, trades, regime_log=None, scan=None):
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

    # client book module — two extra tabs, only when a scan is supplied
    if scan:
        for fname, title, lhs_html, mast in (
            ("portfolio.html", "Fable / Portfolio", _page_portfolio(scan), _portfolio_masthead(scan)),
            ("ideas.html", "Portfolio / Derivative Ideas", _page_ideas(scan), _ideas_masthead(scan)),
        ):
            htmldoc = _shell(fname, title, regime, note, lhs_html, brief, masthead_html=mast)
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
