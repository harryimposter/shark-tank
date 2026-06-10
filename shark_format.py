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
from datetime import date, datetime, timedelta

import book
import earnings
import charts

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
.page{max-width:1760px;margin:0 auto;padding:1.6rem 2.2rem 4rem}
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
/* ---- Derivatives Lab + house-view dropdowns ---- */
.summary-box{border:.5px solid var(--line);border-left:3px solid var(--gold);border-radius:var(--rad-lg);padding:1rem 1.2rem;background:var(--surface);margin-bottom:.6rem}
.summary-box .sh{font-family:var(--serif);font-size:18px;line-height:1.4;margin-bottom:.5rem}
.summary-box .stance{font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin-bottom:.5rem}
.sumpts{list-style:none;padding:0;margin:.3rem 0 0}
.sumpts li{font-size:13px;line-height:1.55;padding:.5rem 0;border-top:.5px solid var(--line);display:flex;gap:9px;align-items:flex-start}
.sumpts li .gchip{flex-shrink:0;font-size:9px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--ink-mute);border:.5px solid var(--line);border-radius:5px;padding:1px 6px;background:#fff;margin-top:1px;min-width:62px;text-align:center}
.grp{display:flex;align-items:center;gap:10px;margin:1.5rem 0 .7rem}
.grp .gname{font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink)}
.grp .gline{flex:1;height:1px;background:var(--line)}
.grp .gcount{font-size:10px;color:var(--ink-mute)}
.badge{font-size:10px;border:.5px solid var(--line);border-radius:6px;padding:1px 7px;color:var(--ink-soft);background:var(--surface);white-space:nowrap}
.badge b{color:var(--ink);font-weight:600}
.srcrow{display:flex;flex-wrap:wrap;gap:5px;margin-top:.55rem}
.srcchip{font-size:10px;border:.5px solid var(--line);border-radius:20px;padding:1px 8px;color:var(--ink-soft);background:#fff}
.srcchip .st{color:var(--ink-mute)}
.impact{font-size:12.5px;color:var(--ink);background:rgba(184,150,12,.06);border-left:2px solid var(--gold);border-radius:0 6px 6px 0;padding:.5rem .75rem;margin-top:.55rem;line-height:1.55}
.impact b{font-weight:600}
.conv-how{font-size:11px;color:var(--ink-mute);margin:.15rem 0 .5rem}
.origin{font-size:11px;color:var(--ink-mute);font-style:italic;margin-bottom:.5rem}
/* ---- trade dropdowns ---- */
details.trade-drop{border:.5px solid var(--line);border-left:3px solid var(--ink-mute);border-radius:var(--rad-lg);padding:.75rem 1.05rem;margin-bottom:10px;background:var(--bg)}
details.trade-drop[open]{border-left-color:var(--gold);background:#fff}
details.trade-drop>summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
details.trade-drop>summary::-webkit-details-marker{display:none}
details.trade-drop>summary .td-name{font-size:14px;font-weight:600;line-height:1.35}
details.trade-drop>summary .td-meta{display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end;flex-shrink:0}
.trade-body{padding-top:.75rem;margin-top:.65rem;border-top:.5px solid var(--line)}
.tb-label{font-size:9.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute);margin:.9rem 0 .25rem}
.tb-label:first-child{margin-top:0}
.tb-text{font-size:13px;color:var(--ink-soft);line-height:1.6}
.tb-risk{font-size:12.5px;color:var(--red);border-left:2px solid var(--red);padding:.3rem .65rem;margin-top:.4rem;background:rgba(192,57,43,.04);border-radius:0 6px 6px 0;line-height:1.5}
.rsi-block{background:var(--surface);border:.5px solid var(--line);border-radius:var(--rad);padding:.5rem .75rem;margin-top:.35rem;font-size:12px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.rsi-block .rv{font-weight:600;font-size:13px;font-variant-numeric:tabular-nums}
.rsi-crowded{color:var(--red);font-weight:700;letter-spacing:.04em}
.rsi-neutral{color:var(--green);font-weight:700;letter-spacing:.04em}
.rsi-na{color:var(--ink-mute);font-style:italic}
/* ---- conviction legend ---- */
.conv-legend{background:var(--surface);border:.5px solid var(--line);border-left:3px solid var(--gold);border-radius:var(--rad-lg);padding:1rem 1.2rem;margin-bottom:1.2rem}
.conv-legend .cl-title{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:.6rem}
.conv-legend table{width:100%;border-collapse:collapse;font-size:12px}
.conv-legend th{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);font-weight:500;text-align:left;padding:5px 6px;border-bottom:.5px solid var(--line)}
.conv-legend td{padding:5px 6px;border-bottom:.5px dotted var(--line);vertical-align:top}
.conv-legend td:first-child{font-weight:600;white-space:nowrap}
.conv-legend td:nth-child(2){color:var(--ink-mute);text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
/* ---- icon legend ---- */
.icon-legend{background:var(--surface);border:.5px solid var(--line);border-radius:var(--rad-lg);padding:.9rem 1.1rem;margin-bottom:1rem}
.icon-legend .il-title{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:.65rem}
.il-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px 18px}
.il-row{display:flex;align-items:flex-start;gap:8px;font-size:12px;line-height:1.55;flex-wrap:wrap}
.il-row .il-key{flex-shrink:0;min-width:70px;max-width:100%}
.il-row .il-val{color:var(--ink-soft);flex:1 1 170px;min-width:170px}
details.idea-d{border:.5px solid var(--line);border-left:3px solid var(--ink-mute);border-radius:var(--rad-lg);padding:.7rem 1rem;margin-bottom:9px;background:var(--bg)}
details.idea-d[open]{border-left-color:var(--gold);background:#fff}
details.idea-d>summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:10px}
details.idea-d>summary::-webkit-details-marker{display:none}
details.idea-d>summary .stitle{font-size:14px;font-weight:600;line-height:1.35}
details.idea-d>summary .smeta{display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.idea-body{padding-top:.7rem;margin-top:.6rem;border-top:.5px solid var(--line)}
.vsum{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:8px}
.vsum::-webkit-details-marker{display:none}
.conv-mini{font-size:11px;color:var(--ink-mute)}
.convtbl{width:100%;border-collapse:collapse;font-size:11.5px;margin:.5rem 0}
.convtbl td{padding:3px 6px;border-bottom:.5px dotted var(--line);vertical-align:top}
.convtbl td.k{color:var(--ink);font-weight:600;white-space:nowrap}
.convtbl td.s{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink-mute);white-space:nowrap}
.convtbl td.w{color:var(--ink-soft)}
/* ---- section headings (black, normal weight, look like headings) ---- */
.section-h{font-family:var(--serif);font-size:1.2rem;font-weight:400;color:#000;letter-spacing:-.005em;line-height:1.25;margin:2.1rem 0 .8rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
.section-h:first-child{margin-top:.3rem}
.section-h .sh-sub{display:block;font-family:var(--font);font-size:11px;font-weight:500;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-mute);margin-top:.4rem}
/* ---- methodology / positioning explainer ---- */
.method-box{background:var(--surface);border:.5px solid var(--line);border-left:3px solid var(--ink);border-radius:var(--rad-lg);padding:.9rem 1.1rem;margin:.3rem 0 1.1rem}
.method-box .mb-t{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ink);margin-bottom:.5rem}
.method-box p{margin:.35rem 0;font-size:12.5px;color:var(--ink-soft);line-height:1.62}
.method-box b{color:var(--ink);font-weight:600}
.method-box ul{margin:.3rem 0;padding-left:1.1rem}.method-box li{font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin-bottom:3px}
/* ---- RSI screener ---- */
.scr-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:.5rem}
@media(max-width:760px){.scr-grid{grid-template-columns:1fr}}
.scr-col h4{font-size:14px;font-weight:700;margin:0 0 .6rem;display:flex;align-items:center;gap:8px}
.scr-col.under h4{color:var(--green)}.scr-col.over h4{color:var(--red)}
.scr-col .scr-sub{font-size:11px;color:var(--ink-mute);font-weight:400}
.rsi-chip{font-variant-numeric:tabular-nums;font-weight:700;border-radius:6px;padding:1px 8px;font-size:12.5px;white-space:nowrap}
.rsi-chip.os{color:var(--green);background:rgba(26,122,69,.1)}
.rsi-chip.ob{color:var(--red);background:rgba(192,57,43,.1)}
.rsi-chip.nu{color:var(--ink-soft);background:var(--surface)}
.scr-empty{font-size:12px;color:var(--ink-mute);font-style:italic;padding:.5rem 0}
/* ---- technical-analysis block ---- */
.ta-block{background:var(--surface);border:.5px solid var(--line);border-radius:var(--rad);padding:.55rem .8rem;margin-top:.35rem;font-size:12px;line-height:1.6}
.ta-grid{display:flex;flex-wrap:wrap;gap:6px;margin:.35rem 0}
.ta-tag{font-size:10.5px;border:.5px solid var(--line);border-radius:6px;padding:1px 7px;background:#fff;color:var(--ink-soft);white-space:nowrap}
.ta-tag b{color:var(--ink);font-weight:600}
.ta-tag.up{border-color:rgba(26,122,69,.5);color:var(--green)}
.ta-tag.dn{border-color:rgba(192,57,43,.5);color:var(--red)}
.ta-how{font-size:11px;color:var(--ink-mute);margin-top:.3rem;line-height:1.5}
/* ---- product-type / objective tags (Derivatives Desk) ---- */
.ptag{font-size:10px;font-weight:600;letter-spacing:.03em;border-radius:6px;padding:1px 8px;border:.5px solid var(--gold);color:var(--gold);background:rgba(184,150,12,.07);white-space:nowrap}
.otag{font-size:10px;font-weight:600;border-radius:6px;padding:1px 8px;border:.5px solid var(--ink-mute);color:var(--ink-soft);background:var(--surface);white-space:nowrap}
/* ---- portfolio pie row (3 compact tiles in one line) ---- */
.pie-row{display:grid;grid-template-columns:1fr;gap:12px;margin:.4rem 0 1.1rem}
@media(min-width:680px){.pie-row{grid-template-columns:repeat(3,1fr)}}
.pie-card{border:.5px solid var(--line);border-radius:var(--rad-lg);padding:.7rem .8rem .4rem;background:var(--bg)}
.pie-card .pc-t{font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--ink);margin-bottom:.2rem;text-align:center}
/* ---- half/half two-column layout for long card lists ---- */
.split2{display:grid;grid-template-columns:1fr;gap:12px;align-items:start}
@media(min-width:900px){.split2{grid-template-columns:1fr 1fr}}
/* ---- two-column prose for long narrative pages (fills the page breadth) ---- */
.cols2{column-count:1;column-gap:2.6rem}
@media(min-width:900px){.cols2{column-count:2}}
.cols2>p:first-child{margin-top:0}
.cols2 p{break-inside:avoid-column}
/* ---- live book P&L header ---- */
.pnl-head{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:.3rem 0 .7rem}
.pnl-tile{background:var(--surface);border:.5px solid var(--line);border-radius:var(--rad);padding:.6rem .8rem}
.pnl-tile .pl{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mute)}
.pnl-tile .pv{font-size:21px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1;margin-top:2px}
.pnl-tile .pv.g{color:var(--green)}.pnl-tile .pv.r{color:var(--red)}
.aim-line{font-size:12.5px;color:var(--ink-soft);background:rgba(184,150,12,.06);border-left:2px solid var(--gold);border-radius:0 6px 6px 0;padding:.5rem .8rem;margin:.2rem 0 .8rem;line-height:1.6}
.aim-line b{color:var(--ink)}
.select-box{border:.5px solid var(--line);border-left:3px solid var(--gold);border-radius:var(--rad-lg);padding:.9rem 1.1rem;background:var(--surface);margin:.3rem 0 1rem}
.select-box .sb-t{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);margin-bottom:.5rem}
.select-box ul{margin:.3rem 0 0;padding-left:0;list-style:none}
.select-box li{font-size:12.5px;line-height:1.6;padding:.4rem 0;border-top:.5px solid var(--line);display:flex;gap:8px;align-items:flex-start}
.select-box li:first-child{border-top:none}
.select-box .tk{flex-shrink:0;font-size:9px;font-weight:700;text-transform:uppercase;border-radius:5px;padding:1px 7px;margin-top:1px;min-width:54px;text-align:center}
.select-box .tk.in{color:#fff;background:var(--green)}
.select-box .tk.out{color:var(--ink-soft);background:#fff;border:.5px solid var(--line)}
"""

NAV = [
    ("index.html", "Summary", "Market Map · overnight read"),
    ("insights.html", "Insights", "the detailed map"),
    ("earnings.html", "Earnings", "Earnings Intelligence"),
    ("trades.html", "Trade Ideas", "ideas + live book"),
    ("portfolio.html", "Portfolio", "Fable · client book"),
    ("ideas.html", "Derivatives Desk", "structured products + OTC"),
]


def _h(label, sub=None):
    """A real section heading — black, larger, looks like a heading."""
    sub_html = f'<span class="sh-sub">{e(sub)}</span>' if sub else ""
    return f'<h2 class="section-h">{e(label)}{sub_html}</h2>'

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


def _coverage_bar():
    """Dynamic 'now − 24h' window stamp, computed from the actual run time, on every tab."""
    now = datetime.now()
    start = now - timedelta(hours=24)
    same_day = start.date() == now.date()
    win = (f'{start:%a %d %b %H:%M} → {now:%a %d %b %H:%M}' if not same_day
           else f'{start:%H:%M} → {now:%H:%M}, {now:%a %d %b}')
    return (
        '<div style="font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-mute);'
        'border:.5px solid var(--line);border-radius:var(--rad);background:var(--surface);'
        'padding:.45rem .7rem;margin:0 0 1.2rem;line-height:1.6">'
        f'<b style="color:var(--ink);font-weight:600">24-hour window</b> &middot; {win} local '
        '&middot; live levels, marks, RSI &amp; technicals fetched at run time &middot; '
        'macro narrative web-sourced for this window'
        '</div>'
    )


def _shell(active, title, regime, regime_note, lhs_html, brief, masthead_html=None):
    now = datetime.now()
    masthead = masthead_html or (
        '<div class="masthead">'
        + (f'<div class="regime-tag">{e(regime)}</div>' if regime else "")
        + f'<h1 class="article-title">{e(title)}</h1>'
        + f'<p class="meta">Pre-market intelligence brief &middot; {now:%a %d %b %Y} '
          f'&middot; generated {now:%H:%M} local &middot; self-graded book</p>'
        + (f'<p style="font-size:13px;color:var(--ink-soft);margin:.6rem 0 0">{e(regime_note)}</p>' if regime_note else "")
        + '</div>'
    )
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{e(title)} · Shark Tank Market Map</title><style>{CSS}</style></head><body>"
        + _menu(active) + _topbar(active)
        + '<div class="page">' + masthead + _coverage_bar()
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


def _rsi_block(rsi):
    """Render the RSI positioning check on the CLASSIC ABSOLUTE convention
    (>=70 overbought, <=30 oversold, 30–70 neutral). No averaging."""
    if not rsi:
        return '<div class="rsi-block"><span class="rsi-na">RSI: no data available for this instrument</span></div>'
    if rsi.get("error"):
        return f'<div class="rsi-block"><span class="rsi-na">RSI: {e(rsi["error"])}</span></div>'
    verdict   = rsi.get("verdict", "NEUTRAL")
    rsi_val   = rsi.get("rsi", "—")
    crowd     = rsi.get("crowd_vs_us", False)
    supports  = rsi.get("supports", False)
    direction = rsi.get("direction", "")
    note      = rsi.get("note", rsi.get("ticker", ""))

    if verdict == "OVERBOUGHT":
        v_html = '<span class="rsi-crowded">OVERBOUGHT (≥70)</span>'
        interp = "RSI ≥ 70 — the tape has run up and is technically overbought; vulnerable to a sell-off."
    elif verdict == "OVERSOLD":
        v_html = '<span class="rsi-neutral">OVERSOLD (≤30)</span>'
        interp = "RSI ≤ 30 — the tape is washed out and technically oversold; set up to bounce."
    else:
        v_html = '<span class="rsi-neutral" style="color:var(--ink-soft)">NEUTRAL (30–70)</span>'
        interp = "RSI between 30 and 70 — no overbought/oversold extreme; positioning signal is neutral."

    impact = ""
    if crowd:
        impact = (f' <span style="color:var(--red);font-weight:600">— ⚑ FLAGGED: against our {e(direction)} '
                  f'(an overbought long / oversold short is chasing an extreme → −1 conviction point)</span>')
    elif supports:
        impact = f' <span style="color:var(--green);font-weight:600">— SUPPORTS our {e(direction)} position</span>'

    return (
        f'<div class="rsi-block">'
        f'<span class="rv">RSI {rsi_val}</span>'
        f'<span>{v_html}{impact}</span>'
        f'<span style="color:var(--ink-mute);font-size:11px">{e(note)} · 14-period RSI (Wilder), 1y daily closes · absolute 30/70 convention</span>'
        f'<span style="color:var(--ink-soft);font-size:11px">{e(interp)}</span>'
        f'</div>'
    )


def _ta_block(ta):
    """Render the technical-analysis read (50/100/200 DMA, Bollinger, Fibonacci)."""
    if not ta:
        return '<div class="ta-block"><span class="rsi-na">Technical analysis: no price history available</span></div>'
    if ta.get("error"):
        return f'<div class="ta-block"><span class="rsi-na">Technical analysis: {e(ta["error"])}</span></div>'
    trend = ta.get("trend", "mixed")
    trend_cls = {"uptrend": "up", "downtrend": "dn"}.get(trend, "")
    cross = ta.get("cross")
    cross_cls = "up" if cross == "golden" else ("dn" if cross == "death" else "")
    tags = []
    for lab, key, ma in (("50d", "pct_vs_50", ta.get("sma50")), ("100d", "pct_vs_100", ta.get("sma100")),
                         ("200d", "pct_vs_200", ta.get("sma200"))):
        pct = ta.get(key)
        if ma is None or pct is None:
            continue
        cls = "up" if pct >= 0 else "dn"
        tags.append(f'<span class="ta-tag {cls}"><b>{lab}</b> {ma:,.2f} ({pct:+}%)</span>')
    tags.append(f'<span class="ta-tag {trend_cls}"><b>Trend</b> {e(trend)}</span>')
    if cross:
        tags.append(f'<span class="ta-tag {cross_cls}"><b>{e(cross)} cross</b></span>')
    nf = ta.get("nearest_fib", {})
    if nf:
        tags.append(f'<span class="ta-tag"><b>Fib</b> {e(nf.get("level",""))} @ {nf.get("price",0):,.2f}</span>')
    tags.append(f'<span class="ta-tag"><b>Boll %B</b> {ta.get("bb_pctb","?")}</span>')
    score = ta.get("ta_score")
    score_html = ""
    if score is not None:
        sc_cls = "var(--green)" if score == 2 else ("var(--gold)" if score == 1 else "var(--red)")
        score_html = (f'<span class="ta-tag" style="border-color:{sc_cls};color:{sc_cls}">'
                      f'<b>TA score {score}/2</b></span>')
    return (
        '<div class="ta-block">'
        + f'<div class="ta-grid">{"".join(tags)}{score_html}</div>'
        + f'<div>{e(ta.get("read",""))}</div>'
        + f'<div class="ta-how">{e(ta.get("how",""))}</div>'
        + '</div>'
    )


def _positioning_method():
    """How 'crowded vs not' is assessed — shown on Trade Ideas, Live Book, Derivatives Desk."""
    return (
        '<div class="method-box">'
        '<div class="mb-t">How we judge whether a trade is crowded</div>'
        '<p>Positioning is the question: <b>is the crowd already on the side we want to be on?</b> '
        'If everyone is long what we are buying, there is no one left to buy and the unwind risk is high. '
        'We assess it from three reads, not an average of anything:</p>'
        '<ul>'
        '<li><b>RSI on the absolute convention.</b> RSI ≥ 70 = overbought (the buyers are exhausted); '
        'RSI ≤ 30 = oversold (the sellers are exhausted). We do <i>not</i> average RSI against a rolling mean — '
        'an oversold tape is oversold whatever its recent average was. An overbought reading on a long, or an '
        'oversold reading on a short, is <b>flagged</b> and costs a conviction point.</li>'
        '<li><b>Moving-average stretch &amp; Bollinger Bands.</b> How far is price from its 50/100/200-day '
        'moving averages, and where does it sit in its Bollinger Bands? Price riding the upper band and stretched '
        'far above the 200-day means the move is extended and the late longs are crowded (fade-prone); hugging the '
        'lower band well below the MAs means the sellers are exhausted (squeeze-prone). A Bollinger <i>squeeze</i> '
        '(tight bands) says a crowded, low-vol consensus is about to break — we read these the same way for '
        'crowding as we read RSI.</li>'
        '<li><b>Speculative positioning / flow.</b> CFTC CoT net length for FX and commodities, fund-flow and '
        'options-skew reads for equities — where the money already sits and how stretched it is.</li>'
        '<li><b>Pain trade.</b> The direction that hurts the most people forces the biggest move; if our trade '
        'is also the pain trade for the consensus, positioning scores high.</li>'
        '</ul>'
        '<p>The positioning component scores <b>0–2</b>: 2 = the crowd is offside our trade (maximum fuel); '
        '1 = neutral/mildly supportive; 0 = the crowd is already with us (high unwind risk).</p>'
        '</div>'
    )


def _screener_conv(item, kind):
    """Systematic technical-conviction /5 for a screened name, with per-criterion WHY.
    kind = 'under' (oversold → buy) or 'over' (overbought → fade)."""
    rsi = item.get("rsi", 50)
    ta  = item.get("technicals") or {}
    pctb = ta.get("bb_pctb", 0.5)
    p200 = ta.get("pct_vs_200")
    rows = []
    score = 0
    # 1) RSI extremity (0-2)
    if kind == "under":
        ext = 2 if rsi <= 22 else (1 if rsi <= 30 else 0)
        ext_why = f"RSI {rsi} — {'deeply' if ext==2 else 'modestly'} oversold (≤30 trigger); the lower the RSI the more washed-out the selling."
    else:
        ext = 2 if rsi >= 78 else (1 if rsi >= 70 else 0)
        ext_why = f"RSI {rsi} — {'deeply' if ext==2 else 'modestly'} overbought (≥70 trigger); the higher the RSI the more exhausted the buying."
    score += ext
    rows.append(("RSI extremity", ext, 2, ext_why))
    # 2) Bollinger confirmation (0-2)
    if kind == "under":
        bb = 2 if pctb <= 0.1 else (1 if pctb <= 0.25 else 0)
        bb_why = f"Bollinger %B {pctb} — {'tagging the lower band (statistically stretched, snap-back-prone)' if bb==2 else 'in the lower half' if bb==1 else 'not yet at the band'}."
    else:
        bb = 2 if pctb >= 0.9 else (1 if pctb >= 0.75 else 0)
        bb_why = f"Bollinger %B {pctb} — {'riding the upper band (statistically stretched, fade-prone)' if bb==2 else 'in the upper half' if bb==1 else 'not yet at the band'}."
    score += bb
    rows.append(("Bollinger confirmation", bb, 2, bb_why))
    # 3) Trend/structure quality (0-1)
    if kind == "under":
        st = 1 if (p200 is not None and p200 > -8) else 0
        st_why = ("Still near/above the 200-day MA — an oversold dip inside an intact uptrend is the higher-quality bounce."
                  if st else "Well below the 200-day MA — oversold but in a downtrend; bounces here are lower quality.")
    else:
        st = 1 if (p200 is not None and p200 > 0) else 0
        st_why = ("Extended above the 200-day MA — an overbought name far from trend support has the most room to mean-revert."
                  if st else "Already below trend support — overbought on a bear rally; the fade is lower quality.")
    score += st
    rows.append(("Trend / structure", st, 1, st_why))
    return score, rows


def _screener_card(item, kind, note=None):
    chip_cls = "os" if kind == "under" else "ob"
    rsi = item.get("rsi", "?")
    score, rows = _screener_conv(item, kind)
    conv_tbl = (
        '<table class="convtbl">'
        f'<tr><td class="k">Technical conviction</td><td class="s">{score}/5</td>'
        f'<td class="w">RSI extremity · Bollinger · trend (systematic, no fundamentals)</td></tr>'
        + "".join(f'<tr><td class="k">{e(k)}</td><td class="s">{v}/{mx}</td><td class="w">{e(w)}</td></tr>'
                  for k, v, mx, w in rows)
        + "</table>"
    )
    if note:
        why = note
    elif kind == "under":
        why = (f"Mechanically surfaced as oversold (RSI {rsi} ≤ 30). The case to go higher is mean reversion: "
               f"selling is exhausted and the technical picture below supports a bounce back toward the moving-average stack.")
    else:
        why = (f"Mechanically surfaced as overbought (RSI {rsi} ≥ 70). The case to sell off is mean reversion: "
               f"buying is exhausted and the technical picture below shows a stretched tape with room to revert.")
    return (
        '<details class="trade-drop">'
        '<summary><div>'
        f'<div class="td-name">{e(item.get("name",""))}</div>'
        f'<div style="font-size:11px;color:var(--ink-mute);margin-top:2px">{e(item.get("ticker",""))} · '
        f'{e(item.get("sector",""))} · {e(item.get("region",""))}</div>'
        '</div><div class="td-meta">'
        f'<span class="rsi-chip {chip_cls}">RSI {rsi}</span>'
        f'<span style="font-size:11px;color:var(--ink-mute)">&#9656; expand</span>'
        '</div></summary>'
        '<div class="trade-body">'
        f'<div class="tb-label">Why it {"should go higher" if kind=="under" else "should sell off"}</div>'
        f'<div class="tb-text">{e(why)}</div>'
        '<div class="tb-label">Technical picture (50/100/200 DMA · Bollinger · Fibonacci)</div>'
        f'{_ta_block(item.get("technicals"))}'
        '<div class="tb-label">Technical conviction · how each score was earned</div>'
        f'{conv_tbl}'
        '</div></details>'
    )


def _rsi_screener(screen, notes=None):
    """Two-column RSI screener: oversold names to buy, overbought names to fade."""
    if not screen:
        return ""
    notes = notes or {}
    under = screen.get("oversold", [])
    over  = screen.get("overbought", [])
    # full universe list, grouped by region then sector
    uni = screen.get("universe", [])
    uni_html = ""
    if uni:
        by_region = {}
        for u in uni:
            by_region.setdefault(u.get("region", "—"), []).append(u)
        blocks = []
        for region in ["US", "Europe", "UK", "Japan", "Asia", "Global"]:
            items = by_region.get(region)
            if not items:
                continue
            chips = " ".join(f'<span class="ta-tag" title="{e(u["name"])} · {e(u["sector"])}">{e(u["ticker"])}</span>'
                             for u in items)
            blocks.append(f'<div style="margin:.4rem 0"><b style="font-size:11px;color:var(--ink-mute);'
                          f'text-transform:uppercase;letter-spacing:.06em">{e(region)}</b>'
                          f'<div class="ta-grid" style="margin-top:.25rem">{chips}</div></div>')
        uni_html = ('<details style="margin-top:.5rem"><summary style="cursor:pointer;font-size:12px;'
                    f'font-weight:600;color:var(--gold)">Show the full scanned universe ({len(uni)} names) &#9656;</summary>'
                    f'<div style="margin-top:.4rem">{"".join(blocks)}</div></details>')
    method = (
        '<div class="method-box">'
        '<div class="mb-t">How these names are found — and the universe we scan</div>'
        f'<p>Each refresh we scan a curated <b>{screen.get("scanned","~60")}-name cross-asset universe</b> and '
        'compute the <b>14-period RSI</b> (Wilder) on six months of daily closes, splitting on the '
        '<b>absolute convention</b>: <b>RSI ≤ 30 = oversold</b> (left — set up to go higher), '
        '<b>RSI ≥ 70 = overbought</b> (right — run too far, should sell off). No averaging.</p>'
        '<p>The universe is built from five buckets: <b>(1) US mega-cap tech &amp; semis</b>; '
        '<b>(2) US financials, industrials, energy, healthcare &amp; consumer</b>; '
        '<b>(3) cross-asset ETFs</b> (equity, small-cap, rates/TLT, credit/HYG, gold); '
        '<b>(4) Europe, UK, Japan &amp; Korea</b> names; and <b>(5) an AI supply-chain sleeve</b> — '
        'HBM / optical / connectivity / semicap — which is exactly where names like '
        '<b>LITE (Lumentum), AXTI, COHR, ALAB, CRDO, SITM, MRVL, ARM, SWKS, VRT</b> live. '
        'The list is editable in one place (<code>fetch_rsi.SCREEN_UNIVERSE</code>); flag any name and it goes in.</p>'
        f'<p style="font-size:11px;color:var(--ink-mute)">Universe scanned {screen.get("asof","")}; '
        f'{screen.get("errors",0)} symbol(s) returned no data this run.</p>'
        + uni_html +
        '</div>'
    )
    left = ('<div class="scr-col under"><h4>Oversold &mdash; names to go higher '
            f'<span class="scr-sub">RSI ≤ {int(screen.get("low",30))}</span></h4>'
            + ("".join(_screener_card(i, "under", notes.get(i["ticker"])) for i in under)
               if under else '<div class="scr-empty">No name in the universe is oversold this refresh.</div>')
            + '</div>')
    right = ('<div class="scr-col over"><h4>Overbought &mdash; names that should sell off '
             f'<span class="scr-sub">RSI ≥ {int(screen.get("high",70))}</span></h4>'
             + ("".join(_screener_card(i, "over", notes.get(i["ticker"])) for i in over)
                if over else '<div class="scr-empty">No name in the universe is overbought this refresh.</div>')
             + '</div>')
    return method + '<div class="scr-grid">' + left + right + '</div>'


def _conviction_legend():
    """Return the 'How conviction is scored' explainer section."""
    rows = [
        ("Gap (0–3)", "0–3", "How far is the current price from fair value / your view? "
         "3 = extreme regime-level mispricing (>3 SDs or a fundamental regime shift not priced); "
         "2 = clear gap (~1–2 SDs or a well-documented mispricing); "
         "1 = minor gap; 0 = no gap or price is against you."),
        ("Catalyst (0–2)", "0–2", "Is there a specific, dated event that can close the gap? "
         "2 = precise near-term dated catalyst (earnings, FOMC, CPI, ECB) with a clear payoff trigger; "
         "1 = soft or undated catalyst; 0 = no catalyst or catalyst is ambiguous."),
        ("Positioning (0–2)", "0–2", "Does existing market positioning provide fuel for the trade? "
         "2 = the crowd is on the other side of your trade (maximum squeeze potential); "
         "1 = neutral or mildly supportive; 0 = crowd is with you (high unwind risk)."),
        ("Confirmation (0–2)", "0–2", "Do independent signals confirm the thesis? "
         "2 = multiple confirming signals (technical breakout + fundamental data + flow); "
         "1 = one confirming signal; 0 = no confirmation or contradicting signals."),
        ("Stop quality (0–1)", "0–1", "Is the stop loss clearly defined and tight relative to the move? "
         "1 = stop at a clean technical/structural level with a disciplined R/R ratio; "
         "0 = wide, arbitrary, or no defined stop."),
        ("Technical analysis (0–2) ★ NEW", "0–2", "Does the chart confirm the trade? We read the "
         "50/100/200-day moving averages (trend + golden/death cross), 20-day Bollinger Bands (is the "
         "entry stretched at a band or does it have room?), and Fibonacci retracements off the trailing "
         "6-month swing (the support/resistance the stop and target hang on). "
         "2 = trend agrees with the trade AND the entry is not chasing an exhausted band; "
         "1 = mixed; 0 = the chart contradicts the trade."),
        ("RSI positioning (0–1) ★ NEW", "0–1", "Crowding check on the CLASSIC ABSOLUTE convention — "
         "RSI ≥ 70 overbought, RSI ≤ 30 oversold, 30–70 neutral. No averaging against a rolling mean. "
         "If the tape is overbought and we are long, or oversold and we are short, the position is "
         "chasing an extreme: it is FLAGGED and scores 0 (−1 conviction point). Otherwise = 1."),
    ]
    tbl = ('<table><thead><tr><th>Criterion</th><th>Max</th><th>What earns points</th></tr></thead><tbody>'
           + "".join(f'<tr><td>{e(r[0])}</td><td style="text-align:right">{e(r[1])}</td><td style="color:var(--ink-soft)">{e(r[2])}</td></tr>'
                     for r in rows)
           + "</tbody></table>")
    return (
        '<div class="conv-legend">'
        '<div class="cl-title">How conviction is scored · live total /13</div>'
        + tbl +
        '<div style="font-size:11px;color:var(--ink-mute);margin-top:.6rem">'
        '<b>Live conviction = core 10 + technical analysis (0–2) + RSI check (0–1) = /13.</b> '
        'The core (gap 3 + catalyst 2 + positioning 2 + confirmation 2 + stop 1) is struck at entry; the '
        'technical-analysis score (moving-average trend + Bollinger stretch + Fibonacci) and the RSI check are '
        'recomputed live every refresh and <b>count toward the score shown on the badge</b>, so a trade that goes '
        'technically offside loses conviction points in real time. The Derivatives Desk uses the same idea on its '
        'base /8 (→ live /11).</div>'
        '</div>'
    )


def _icon_legend():
    """Return the visible icon/badge legend for the Derivatives Lab page."""
    items = [
        # tier badges
        ('<span class="tier fire" style="font-size:11px">FIRE</span>',
         "Top-conviction idea — all four conviction sub-scores high; deploy now."),
        ('<span class="tier watch" style="font-size:11px">WATCH</span>',
         "Interesting but incomplete — typically waiting on a data point, IV sourcing, or a catalyst gate. Promote to FIRE when the missing piece arrives."),
        ('<span class="tier suppress" style="font-size:11px">SUPPRESS</span>',
         "Algorithmically flagged but deliberately held back — either contradicts another idea on the same name or the brief's current regime says 'hold, don't trim.'"),
        # house view pills
        ('<span class="vpill v-like" style="font-size:11px">LIKE</span>',
         "House view: constructive / bullish on this name or instrument. Supports adding or holding."),
        ('<span class="vpill v-neutral" style="font-size:11px">NEUTRAL</span>',
         "House view: no strong directional view. Hold existing positions; do not add."),
        ('<span class="vpill v-avoid" style="font-size:11px">AVOID</span>',
         "House view: negative / bearish. Reduce or hedge existing exposure; do not add."),
        ('<span class="vpill v-hedge" style="font-size:11px">LIKE-as-hedge</span>',
         "House view: hold this position specifically as a portfolio hedge or tail risk offset — not for directional upside."),
        # source dots
        ('<span style="display:inline-flex;align-items:center;gap:4px"><span class="srcdot src-sourced"></span>green dot</span>',
         "Data point is <b>sourced</b> — from a named sell-side report, Finnhub, TradingView live feed, or a public filing."),
        ('<span style="display:inline-flex;align-items:center;gap:4px"><span class="srcdot src-estimated"></span>gold dot</span>',
         "Data point is <b>estimated</b> — derived, model-computed, or from an analyst's thematic note rather than a hard data source."),
        ('<span style="display:inline-flex;align-items:center;gap:4px"><span class="srcdot src-unverified"></span>red dot</span>',
         "Data point is <b>unverified</b> — not yet confirmed this session; treat with caution."),
        # conviction pips
        ('<div style="display:inline-flex;gap:2px">'
         + "".join(f'<div class="pip8 {"on" if i < 6 else ""}" style="width:12px"></div>' for i in range(8))
         + '</div>',
         "Conviction pips: filled gold bars = score earned, empty = not earned (Derivatives Desk live /11, Trade book live /13)."),
    ]
    rows = "".join(
        f'<div class="il-row"><div class="il-key">{sym}</div><div class="il-val">{desc}</div></div>'
        for sym, desc in items
    )
    return (
        '<div class="icon-legend">'
        '<div class="il-title">Legend &mdash; what every badge, pill, dot and bar means</div>'
        f'<div class="il-grid">{rows}</div>'
        '</div>'
    )


def _trade_dropdown(idea, enrichments=None, rsi_data=None):
    """Render a trade as a self-contained expandable <details> dropdown."""
    tid  = idea.get("id", "")
    enr  = (enrichments or {}).get(tid, {})
    rsi  = (rsi_data or {}).get(tid)
    cb   = idea.get("conviction_breakdown", {}) or {}
    kind = idea.get("_kind", idea.get("type", "reactive"))
    conv = idea.get("conviction", 0)
    # P&L badge
    pl   = idea.get("current_pnl_pct")
    if pl is not None:
        pl_cls = "g" if pl > 0 else ("r" if pl < 0 else "mute")
        pl_html = f'<span class="{pl_cls}" style="font-size:12px;font-weight:600">{pl:+.2f}%</span>'
    else:
        pl_html = ""
    # Closed badge
    closed_badge = ""
    if idea.get("exit"):
        ex = idea["exit"]
        c_cls = "g" if (ex.get("pnl_pct", 0) or 0) > 0 else "r"
        closed_badge = (f'<span class="{c_cls}" style="font-size:11px;font-weight:600">'
                        f'{e(ex.get("result","CLOSED"))} {ex.get("pnl_pct",0):+.1f}%</span>')
    # Conviction breakdown table with WHY
    why = enr.get("breakdown_why", {})
    crit = [
        ("Gap",          cb.get("gap", 0),          3, why.get("gap",          "—")),
        ("Catalyst",     cb.get("catalyst", 0),      2, why.get("catalyst",     "—")),
        ("Positioning",  cb.get("positioning", 0),   2, why.get("positioning",  "—")),
        ("Confirmation", cb.get("confirmation", 0),  2, why.get("confirmation", "—")),
        ("Stop quality", cb.get("stop_quality", 0),  1, why.get("stop_quality", "—")),
    ]
    # Technical-analysis criterion (0-2) — folded into the live total
    ta = (rsi or {}).get("technicals") if rsi else None
    ta_pt = ta_max = 0
    if ta and not ta.get("error") and ta.get("ta_score") is not None:
        ta_pt, ta_max = ta["ta_score"], 2
        crit.append(("Technical analysis ★", ta_pt, 2, why.get("technical_analysis",
            f'{ta.get("trend","?")} ({ta.get("cross","no")} cross); Bollinger %B {ta.get("bb_pctb","?")}; '
            f'nearest Fib {ta.get("nearest_fib",{}).get("level","?")} — chart '
            + ("confirms" if ta_pt == 2 else "is mixed on" if ta_pt == 1 else "contradicts")
            + " the trade.")))
    # RSI criterion (absolute 30/70) — folded into the live total
    rsi_pt = rsi_max = 0
    if rsi and not rsi.get("error"):
        crowd_vs_us = rsi.get("crowd_vs_us", False)
        rsi_pt, rsi_max = (0 if crowd_vs_us else 1), 1
        crit.append(("RSI check ★", rsi_pt, 1, why.get("rsi_positioning",
            f'RSI {rsi.get("rsi","?")} · {rsi.get("verdict","?")} — '
            + ("⚑ overbought long / oversold short, chasing an extreme: 0 pts" if crowd_vs_us
               else "neutral or supportive: 1 pt"))))
    live_total = conv + ta_pt + rsi_pt
    live_max   = 10 + ta_max + rsi_max
    conv_tbl = (
        '<table class="convtbl">'
        f'<tr><td class="k">Live conviction</td><td class="s">{live_total}/{live_max}</td>'
        f'<td class="w">core (10, struck at entry) + technical analysis + RSI, recomputed live</td></tr>'
        + "".join(f'<tr><td class="k">{e(k)}</td><td class="s">{v}/{mx}</td>'
                  f'<td class="w">{e(w)}</td></tr>'
                  for k, v, mx, w in crit)
        + "</table>"
    )
    # Catalyst list
    cats = enr.get("catalysts", [])
    cat_html = ("<ul style='margin:.3rem 0 0;padding-left:1.2rem'>"
                + "".join(f"<li style='font-size:12.5px;color:var(--ink-soft);margin-bottom:3px'>{e(c)}</li>" for c in cats)
                + "</ul>") if cats else '<span class="tb-text">—</span>'
    # Trade rows
    rows_data = [
        ("Direction", ("Short" if "short" in (idea.get("trade","") + " " + idea.get("structure","")).lower()
                       and "long" not in (idea.get("trade","") + " " + idea.get("structure","")).lower()
                       else "Long")),
        ("Asset class", idea.get("asset_class", "")),
        ("Structure",   idea.get("structure", "")),
        ("Entry",       idea.get("entry")),
        ("Stop",        idea.get("stop")),
        ("Target",      idea.get("target")),
        ("Horizon",     idea.get("horizon", "")),
    ]
    if idea.get("min_hold_days"):
        rows_data.append(("Min hold", f'{idea["min_hold_days"]}d'))
    if pl is not None:
        rows_data.insert(0, ("Current P&L", f'{pl:+.2f}%'))
    trade_tbl = (
        '<table class="convtbl" style="margin:.3rem 0">'
        + "".join(f'<tr><td class="k" style="width:110px">{e(k)}</td>'
                  f'<td class="s" style="text-align:left">{e(v)}</td><td class="w"></td></tr>'
                  for k, v in rows_data if v is not None)
        + "</table>"
    )
    # Status note (open book note)
    note_html = ""
    if enr.get("risks"):
        note_html = f'<div class="tb-risk">{e(enr["risks"])}</div>'
    return (
        f'<details class="trade-drop">'
        f'<summary>'
        f'<div>'
        f'<div class="td-name">{e(idea.get("trade",""))}</div>'
        f'<div style="font-size:11px;color:var(--ink-mute);margin-top:2px">{e(tid)} · {e(kind)} · {e(idea.get("asset_class",""))}</div>'
        f'</div>'
        f'<div class="td-meta">'
        + (pl_html or closed_badge)
        + f'<span class="conv-badge">{live_total}/{live_max}</span>'
        f'<span style="font-size:11px;color:var(--ink-mute)">&#9656; expand</span>'
        f'</div>'
        f'</summary>'
        f'<div class="trade-body">'
        # instrument
        + (f'<div class="tb-label">What this instrument is &amp; what drives it</div>'
           f'<div class="tb-text">{e(enr.get("instrument",""))}</div>'
           if enr.get("instrument") else "")
        # trade view
        + f'<div class="tb-label">Trade view · entry / stop / target / horizon</div>'
        + trade_tbl
        # fundamental thesis
        + (f'<div class="tb-label">Fundamental thesis</div>'
           f'<div class="tb-text">{e(enr.get("fundamental_thesis", idea.get("thesis","")))}</div>'
           if enr.get("fundamental_thesis") else
           f'<div class="tb-label">Thesis</div><div class="tb-text">{e(idea.get("thesis",""))}</div>')
        # catalysts
        + f'<div class="tb-label">Catalyst(s)</div>{cat_html}'
        # conviction
        + f'<div class="tb-label">Full conviction breakdown</div>'
        + conv_tbl
        # technical analysis
        + f'<div class="tb-label">Technical analysis · 50/100/200 DMA · Bollinger · Fibonacci</div>'
        + _ta_block(ta)
        # RSI
        + f'<div class="tb-label">RSI positioning check (absolute 30/70)</div>'
        + _rsi_block(rsi)
        # risks
        + (f'<div class="tb-label">Risks / what would make this wrong</div>' + note_html
           if enr.get("risks") else "")
        + f'</div>'
        f'</details>'
    )


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


def _book_accordion(trades, enrichments=None, rsi_data=None):
    enr = enrichments or {}
    rsi = rsi_data or {}
    out = []
    for t in trades.get("open", []) + trades.get("closed", []):
        tid    = t.get("id", "")
        te     = enr.get(tid, {})
        trsi   = rsi.get(tid)
        closed = "exit" in t
        pl     = t.get("current_pnl_pct")
        pl_cls = "g" if (pl or 0) > 0 else ("r" if (pl or 0) < 0 else "mute")
        if closed:
            ex  = t["exit"]
            pl_cls = "g" if (ex.get("pnl_pct", 0) or 0) > 0 else "r"
            status_html = (f'<span class="{pl_cls}">{e(ex.get("result","CLOSED"))} '
                           f'{ex.get("pnl_pct",0):+.2f}%</span>')
        else:
            status_html = (f'<span class="{pl_cls}">{pl:+.2f}%</span>' if pl is not None else
                           '<span class="mute">open</span>')

        cb = t.get("conviction_breakdown") or {}
        why = te.get("breakdown_why", {})
        crit = [
            ("Gap",          cb.get("gap",0),          3, why.get("gap","—")),
            ("Catalyst",     cb.get("catalyst",0),      2, why.get("catalyst","—")),
            ("Positioning",  cb.get("positioning",0),   2, why.get("positioning","—")),
            ("Confirmation", cb.get("confirmation",0),  2, why.get("confirmation","—")),
            ("Stop quality", cb.get("stop_quality",0),  1, why.get("stop_quality","—")),
        ]
        tta = (trsi or {}).get("technicals") if trsi else None
        ta_pt = ta_max = rsi_pt = rsi_max = 0
        if tta and not tta.get("error") and tta.get("ta_score") is not None:
            ta_pt, ta_max = tta["ta_score"], 2
            crit.append(("Technical analysis ★", ta_pt, 2,
                         f'{tta.get("trend","?")} · {tta.get("cross","no")} cross · Boll %B {tta.get("bb_pctb","?")} · '
                         f'nearest Fib {tta.get("nearest_fib",{}).get("level","?")}'))
        if trsi and not trsi.get("error"):
            crowd = trsi.get("crowd_vs_us", False)
            rsi_pt, rsi_max = (0 if crowd else 1), 1
            crit.append(("RSI check ★", rsi_pt, 1,
                         f'RSI {trsi.get("rsi","?")} · {trsi.get("verdict","?")} (absolute 30/70) · '
                         + ("⚑ chasing an extreme" if crowd else "neutral/supportive")))
        core_conv = t.get("conviction", 0) or 0
        live_total = core_conv + ta_pt + rsi_pt
        live_max   = 10 + ta_max + rsi_max
        conv_tbl = (
            '<table class="convtbl">'
            f'<tr><td class="k">Live conviction</td><td class="s">{live_total}/{live_max}</td>'
            f'<td class="w">core {core_conv}/10 at entry + technical analysis + RSI, live</td></tr>'
            + "".join(f'<tr><td class="k">{e(k)}</td><td class="s">{v}/{mx}</td>'
                      f'<td class="w">{e(w)}</td></tr>' for k, v, mx, w in crit)
            + "</table>"
        )

        cats = te.get("catalysts", [])
        cat_html = ("<ul style='margin:.25rem 0 0;padding-left:1.1rem'>"
                    + "".join(f"<li style='font-size:12px;color:#6b6b6b;margin-bottom:2px'>{e(c)}</li>" for c in cats)
                    + "</ul>") if cats else ""

        rows_data = [
            ("Opened", t.get("opened","")),
            ("Asset class", t.get("asset_class","")),
            ("Structure", t.get("structure","")),
            ("Entry", t.get("entry")),
            ("Current", t.get("current")),
            ("Stop", t.get("stop")),
            ("Target", t.get("target")),
            ("Horizon", t.get("horizon","")),
        ]
        if t.get("min_hold_days"):
            rows_data.append(("Min hold", f'{t["min_hold_days"]}d'))
        if closed:
            ex = t["exit"]
            rows_data += [("Exit date", ex.get("date","")), ("Exit level", ex.get("level")),
                          ("Days held", f'{ex.get("days_held","")}d')]
        det_rows = "".join(f'<div class="det-row"><span class="det-k">{e(k)}</span>'
                           f'<span>{e(v)}</span></div>' for k, v in rows_data if v is not None)

        body = det_rows
        if te.get("instrument"):
            body += (f'<div class="det-thesis"><strong>Instrument:</strong> {e(te["instrument"])}</div>')
        if te.get("fundamental_thesis") or t.get("thesis"):
            body += (f'<div class="det-thesis"><strong>Thesis:</strong> '
                     f'{e(te.get("fundamental_thesis", t.get("thesis","")))} </div>')
        if cats:
            body += f'<div class="det-thesis"><strong>Catalysts:</strong></div>{cat_html}'
        body += f'<div class="det-thesis"><strong>Conviction breakdown:</strong></div>{conv_tbl}'
        # Technical analysis in FRAG_CSS context — inline block
        if tta and not tta.get("error"):
            body += '<div class="det-thesis"><strong>Technical analysis (50/100/200 DMA · Bollinger · Fibonacci):</strong></div>'
            body += (f'<div style="background:#f7f7f5;border:.5px solid rgba(0,0,0,.1);border-radius:6px;'
                     f'padding:.4rem .6rem;font-size:11px;margin-top:.3rem;line-height:1.55">'
                     f'<b>{e(tta.get("trend","?"))}</b> · {e(tta.get("cross","no"))} cross · '
                     f'Bollinger %B {tta.get("bb_pctb","?")} · nearest Fib {e(tta.get("nearest_fib",{}).get("level","?"))} · '
                     f'TA score <b>{tta.get("ta_score","?")}/2</b><br>{e(tta.get("read",""))}</div>')
        # RSI in FRAG_CSS context — absolute 30/70 convention
        if trsi and not trsi.get("error"):
            body += '<div class="det-thesis"><strong>RSI positioning (absolute 30/70):</strong></div>'
            body += (f'<div style="background:#f7f7f5;border:.5px solid rgba(0,0,0,.1);border-radius:6px;'
                     f'padding:.4rem .6rem;font-size:11px;margin-top:.3rem">'
                     f'RSI {trsi.get("rsi","?")} · <b>{e(trsi.get("verdict","?"))}</b>'
                     + (" · <b style=\"color:#c0392b\">&#9873; FLAGGED — chasing an extreme vs our position</b>" if trsi.get("crowd_vs_us") else "")
                     + f' · {e(trsi.get("note",""))}'
                     + '</div>')
        elif trsi and trsi.get("error"):
            body += f'<div style="font-size:11px;color:#9a9a9a;margin-top:.3rem">{e(trsi["error"])}</div>'
        if te.get("risks"):
            body += f'<div class="det-thesis" style="color:#c0392b"><strong>Risks:</strong> {e(te["risks"])}</div>'

        out.append(
            f'<details><summary><span><span class="pill">{e(tid)}</span> '
            f'{e(t.get("trade",""))}</span>{status_html}</summary>'
            + body + '</details>'
        )
    return "".join(out) or "<p class='mute'>no positions</p>"


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def _page_summary(brief):
    lhs = []
    lhs.append(_h("The overnight read", "Pre-market summary · what happened in the last 24 hours"))
    lhs.append(f'<div class="wrap-body cols2">{brief.get("summary_narrative", brief.get("wrap",""))}</div>')
    if brief.get("takeaways"):
        lhs.append(_h("Today's takeaways"))
        lhs.append(_takeaways(brief["takeaways"]))
    if brief.get("scenarios"):
        lhs.append(_h("Scenarios", "Bull / Base / Bear"))
        lhs.append(_scenarios(brief["scenarios"]))
    if brief.get("tape_missing"):
        lhs.append(_h("What the tape is missing"))
        lhs.append(f'<div class="wrap-body" style="font-size:14px">{brief["tape_missing"]}</div>')
    return "".join(lhs)


def _burry_block(text):
    if not text:
        return ""
    return ('<div class="method-box" style="border-left-color:var(--gold)">'
            '<div class="mb-t" style="color:var(--gold)">The Burry tell &mdash; what nobody is looking at</div>'
            f'<p>{text}</p></div>')


def _page_insights(brief):
    lhs = []
    lhs.append(_h("The detailed map", "How the pieces connect · the regime, the gap, what's priced"))
    lhs.append(f'<div class="wrap-body cols2">{brief.get("insights_layers", brief.get("wrap",""))}</div>')
    if brief.get("scenarios"):
        lhs.append(_h("Bull / Base / Bear", "the three paths, with probabilities"))
        lhs.append(_scenarios(brief["scenarios"]))
    if brief.get("burry_tell"):
        lhs.append(_h("The Burry tell", "the structural thing that matters in 6 months"))
        lhs.append(_burry_block(brief["burry_tell"]))
    if brief.get("one_chart"):
        lhs.append(_h("Today's one chart that matters"))
        lhs.append(f'<div class="one-chart">{brief["one_chart"]}</div>')
    lhs.append(_h("Catalyst calendar", "next 5 trading days"))
    lhs.append(_catalyst(brief.get("catalyst_calendar", [])))
    lhs.append(_h("Deep dives", "correlation · vol & skew · sector RV · positioning · consensus · talking points"))
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


def _earnings_criteria():
    rows = [
        ("Asymmetry signal (0–2)", "Does the implied move misprice the historical average move, or is "
         "estimate dispersion unusually wide? 2 = clear mispricing of the event; 1 = moderate; 0 = none."),
        ("Sell-side consensus (0–2)", "Is the sell-side aligned — majority buy, upside to price target, "
         "positive revisions? 2 = strong support; 1 = mixed; 0 = contradicts. If unverified, conviction caps at Medium."),
        ("Catalyst clarity (0–2)", "Pre-print: is there an identifiable catalyst the consensus hasn't priced? "
         "Post-print: is the reaction disproportionate to the print (oversold/overbought)? 2 = clear edge; 1 = plausible; 0 = none."),
        ("Positioning & sentiment (0–2)", "Short interest >10% of float or an extreme positioning setup? "
         "2 = extreme; 1 = notable lean; 0 = neutral/unavailable."),
    ]
    tbl = ('<table><thead><tr><th>Pillar</th><th>What earns points</th></tr></thead><tbody>'
           + "".join(f'<tr><td style="font-weight:600;white-space:nowrap;vertical-align:top">{e(k)}</td>'
                     f'<td style="color:var(--ink-soft)">{e(v)}</td></tr>'
                     for k, v in rows)
           + "</tbody></table>")
    return (
        '<div class="conv-legend">'
        '<div class="cl-title">How the conviction rating is built · /8 (four pillars, 0–2 each)</div>'
        + tbl +
        '<div style="font-size:11px;color:var(--ink-mute);margin-top:.6rem">'
        'Label rules: <b>High</b> = score ≥6 with no pillar at 0 and all pillars sourced; '
        '<b>High — data gap flagged</b> = ≥6 but a pillar is estimated/unverified; '
        '<b>Medium</b> = 4–5 or any pillar 0 or consensus unverified; <b>Low</b> (&lt;4) is excluded. '
        'Green/gold/red dots on each pillar = sourced / estimated / unverified.</div>'
        '</div>'
    )


def _page_earnings(brief):
    lhs = [_h("Earnings intelligence", "Finnhub-sourced · single-name read into and out of the print")]
    # summary line of today's ideas
    summ = brief.get("earnings_summary")
    if summ:
        lhs.append(f'<div class="aim-line"><b>Today&rsquo;s read:</b> {summ}</div>')
    # why these names were picked + sources
    why = brief.get("earnings_why")
    lhs.append(
        '<div class="method-box">'
        '<div class="mb-t">Why these names — and how they clear the universe filter</div>'
        '<p>We scan a defined universe and skip everything outside it silently: <b>market cap $10bn+</b>, '
        'geographies <b>US (primary) and South Korea (secondary)</b>, sectors <b>Technology, Financials, '
        'Industrials, Utilities</b>, reporting within <b>5 days pre- or 3 days post-print</b>. '
        'Consensus estimates, recommendations, surprise history and growth metrics are pre-fetched from '
        '<b>Finnhub</b> (earnings_data.md, tagged &ldquo;sourced&rdquo;); anything missing is supplemented by '
        'web search and tagged &ldquo;estimated&rdquo;.</p>'
        + (f'<p>{why}</p>' if why else '')
        + '</div>'
    )
    lhs.append(_h("The conviction rating, defined"))
    lhs.append(_earnings_criteria())
    lhs.append(_h("Today's earnings ideas"))
    body = earnings.render_earnings_section(brief.get("earnings_ideas", []))
    if not body:
        body = "<p class='mute'>No qualifying earnings in the window.</p>"
    lhs.append(body)
    lhs.append('<div style="margin-top:1.5rem"><a href="ideas.html" '
               'style="font-size:13px;color:var(--gold);font-weight:600;text-decoration:none">'
               'These screens feed the client desk &rarr; see which map to Fable&rsquo;s book as New Adds on the '
               'Derivatives Desk</a></div>')
    return "".join(lhs)


def _book_pnl_header(brief, trades):
    """Overall book P&L (%) + the stated aim at this point."""
    bp = brief.get("book_pnl") or {}
    opens  = [t for t in trades.get("open", []) if isinstance(t.get("current_pnl_pct"), (int, float))]
    closed = [t for t in trades.get("closed", []) if isinstance(t.get("exit", {}).get("pnl_pct"), (int, float))]
    open_avg = bp.get("open_avg")
    if open_avg is None and opens:
        open_avg = sum(t["current_pnl_pct"] for t in opens) / len(opens)
    realized = bp.get("realized")
    if realized is None and closed:
        realized = sum(t["exit"]["pnl_pct"] for t in closed) / len(closed)
    wins = sum(1 for t in closed if t["exit"]["pnl_pct"] > 0)
    hit = bp.get("hit_rate")
    if hit is None and closed:
        hit = 100 * wins / len(closed)

    def tile(label, val, suffix="%"):
        if val is None:
            return f'<div class="pnl-tile"><div class="pl">{e(label)}</div><div class="pv">&mdash;</div></div>'
        cls = "g" if val > 0 else ("r" if val < 0 else "")
        sign = "+" if (suffix == "%" and val > 0) else ""
        return (f'<div class="pnl-tile"><div class="pl">{e(label)}</div>'
                f'<div class="pv {cls}">{sign}{val:.1f}{suffix}</div></div>')

    tiles = (
        tile("Open book P&L", open_avg)
        + tile("Realised (closed)", realized)
        + tile("Hit rate", hit)
        + f'<div class="pnl-tile"><div class="pl">Open / closed</div><div class="pv">{len(opens)}/{len(closed)}</div></div>'
    )
    aim = brief.get("book_aim", "")
    aim_html = f'<div class="aim-line"><b>The aim at this point:</b> {aim}</div>' if aim else ""
    note = bp.get("note", "")
    note_html = (f'<p style="font-size:11px;color:var(--ink-mute);margin:.2rem 0 .6rem">{e(note)}</p>'
                 if note else "")
    return f'<div class="pnl-head">{tiles}</div>' + note_html + aim_html


def _idea_selection(sel):
    """Summary: which of today's flagged ideas go into the book, and why / why not the rest."""
    if not sel:
        return ""
    items = "".join(
        f'<li><span class="tk {"in" if s.get("in") else "out"}">{"ADD" if s.get("in") else "PASS"}</span>'
        f'<span><b>{e(s.get("label",""))}</b> &mdash; {s.get("text","")}</span></li>'
        for s in sel)
    return ('<div class="select-box"><div class="sb-t">What we are putting in the book today &mdash; and what we are not</div>'
            f'<ul>{items}</ul></div>')


def _page_trades(brief, trades):
    enr  = brief.get("trade_enrichments", {})
    rsi  = brief.get("rsi_data", {})
    lhs  = []
    lhs.append(_h("How conviction & positioning are scored"))
    lhs.append(_conviction_legend())
    lhs.append(_positioning_method())
    reactive = [dict(i, _kind="reactive") for i in brief.get("new_ideas", [])]
    prepos   = [dict(i, _kind="pre-position") for i in brief.get("pre_position_ideas", [])]
    if brief.get("ideas_note"):
        lhs.append(_h("Positioning stance today"))
        lhs.append(f'<div class="wrap-body" style="font-size:14px">{brief["ideas_note"]}</div>')
    lhs.append(_h("New trade ideas", "each idea expands to its full thesis, conviction, technicals & RSI"))
    if reactive + prepos:
        lhs.append('<div class="split2">' + "".join(_trade_dropdown(i, enr, rsi) for i in reactive + prepos) + '</div>')
    else:
        lhs.append('<p class="mute" style="font-size:13px">No new idea today — into a binary print, forcing a trade is the trade.</p>')
    # RSI screener
    if brief.get("screen"):
        lhs.append(_h("RSI screener", "oversold names to buy · overbought names to fade"))
        lhs.append(_rsi_screener(brief["screen"], brief.get("screener_notes")))
    # Open book + P&L header + selection summary
    lhs.append(_h("Open book", "overall P&L, the aim, and what we are adding today"))
    lhs.append(_book_pnl_header(brief, trades))
    lhs.append(_idea_selection(brief.get("idea_selection")))
    lhs.append('<p style="font-size:12px;color:var(--ink-mute);margin:.2rem 0 .5rem">Click any trade for the full breakdown — thesis, conviction, technical analysis and RSI.</p>')
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
        '<div class="regime-tag">Derivatives Desk &middot; Ruleset v2</div>'
        '<h1 class="article-title">Derivatives Desk</h1>'
        f'<p class="meta">Structured products + OTC &middot; {e(scan["as_of"])} '
        f'&middot; {cnt.get("new_adds",0)} new adds &middot; {cnt.get("enhance",0)} enhancements</p>'
        f'<p style="font-size:13px;color:var(--ink-soft);margin:.6rem 0 0">'
        f'Where the desk’s ideas become this client’s trades. The Earnings screener and macro book feed '
        f'<b>New Adds</b>; the Book Scanner turns existing holdings into <b>Enhancements</b>. Everything is sized to '
        f'the book and consistency-locked to today’s regime &mdash; <b>{e(scan.get("regime",""))}</b> &mdash; '
        f'and to the per-name house views.</p>'
        '</div>'
    )


def _product_shelf():
    return (
        '<div class="method-box">'
        '<div class="mb-t">The product shelf — a guideline, not a limit</div>'
        '<p>Every recommendation is tagged with its <b>product type</b> and its <b>objective</b>. The list below is '
        'the <b>house guideline</b> for what trades cleanly today — not a hard limit. If an idea genuinely needs a '
        'structure outside it, we will still suggest it and flag: <b>&ldquo;please check with your derivs team on '
        'feasibility of trading.&rdquo;</b> In <b>OTC, essentially anything is possible</b> — the guideline just '
        'tells you what is standard vs. what needs a feasibility check. The asset-class gating:</p>'
        '<ul>'
        '<li><b>Equities — Income:</b> reverse convertibles, fixed-coupon notes (FCN), Phoenix autocalls, '
        'digital review notes. <b>Income + participation:</b> autocallable Market Plus notes. '
        '<b>Participation:</b> BREN (bullish range / enhanced-return note). '
        '<b>Protected participation:</b> 100% (or minimal-loss) principal-protected with upside to a cap. '
        '<b>OTC — full creative latitude:</b> accumulators / decumulators, call &amp; put spreads, risk reversals, '
        'collars, prepaid variable forwards, total-return swaps, worst-of / dispersion and variance / vol — '
        'whatever genuinely fits the book.</li>'
        '<li><b>FX — Income:</b> DCS (dual-currency security) only. '
        '<b>Hedging:</b> forwards, seagulls, puts — accumulators / decumulators where they genuinely fit.</li>'
        '<li><b>Rates:</b> range accruals only.</li>'
        '</ul>'
        '<p style="font-size:11px;color:var(--ink-mute)">Issuer credit: every note is senior unsecured paper — '
        'cap any single issuer at 20% of the structure book.</p>'
        '</div>'
    )


def _loss_recovery_block(scan):
    lr = scan.get("loss_recovery")
    if not lr:
        return ""
    items = "".join(
        '<div class="idea" style="border-left:3px solid var(--gold)">'
        f'<div class="it" style="margin-bottom:.3rem">{e(x.get("name",""))} '
        f'<span style="font-size:11px;color:var(--red);font-weight:600">{e(x.get("loss",""))}</span></div>'
        f'<div class="blk"><b>How to recover it:</b> {x.get("how","")}</div>'
        + (f'<div class="impact"><b>Faster path (structured + OTC at margin):</b> {x.get("accelerator","")}</div>'
           if x.get("accelerator") else "")
        + '</div>'
        for x in lr)
    return (_h("Recovering losses", "exactly how to claw each one back — and the faster, margined path")
            + '<p style="font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin:0 0 .6rem">'
              'For every underwater position the desk gives a precise recovery route. Where it makes sense you '
              'can run a capital-protected / income structure <b>and</b> an OTC trade at margin alongside it, so '
              'the position recovers faster than waiting for the mark to come back on its own.</p>'
            + '<div class="split2">' + items + '</div>')


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
        basis = p.get("iv_basis", "implied")
        iv_lab = "RV 3m" if basis == "realized" else ("live" if conf == "sourced" else "est")
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
            '<th class="num">P&amp;L</th><th class="num">Day</th><th>House view</th><th class="num">Vol (IV&middot;RV)</th>'
            '</tr></thead><tbody>' + "".join(rows) + '</tbody></table>')


def _cash_liab_block(scan):
    c = scan["client"]; eurusd = c.get("fx_reference", {}).get("EURUSD", 1.154)
    out = [_h("Cash & liabilities"), '<table class="holdtbl"><tbody>']
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


def _sources_row(sources):
    if not sources:
        return ""
    chips = "".join(
        f'<span class="srcchip">{e(s.get("name",""))}'
        + (f' <span class="st">&middot; {e(s.get("type",""))}</span>' if s.get("type") else "")
        + (f' <span class="st">&middot; {e(s.get("note",""))}</span>' if s.get("note") else "")
        + '</span>' for s in sources)
    return f'<div class="srcrow">{chips}</div>'


def _conv_table(rows, total, total_max, caption="how we scored it"):
    body = "".join(
        f'<tr><td class="k">{e(r["k"])}</td><td class="s">{r["v"]}/{r["max"]}</td>'
        f'<td class="w">{e(r["why"])}</td></tr>' for r in rows)
    return (f'<table class="convtbl"><tr><td class="k">Conviction</td>'
            f'<td class="s">{total}/{total_max}</td><td class="w">{e(caption)}</td></tr>{body}</table>')


def _macro_anchors_block(meta):
    a = meta.get("macro_anchors", {})
    if not a:
        return ""
    authors = " ".join(
        f'<span class="srcchip">{e(au.get("name",""))} <span class="st">&middot; {e(au.get("platform",""))}</span></span>'
        for au in a.get("authors", []))
    return (
        '<div class="summary-box" style="border-left-color:var(--ink-mute)">'
        '<div class="stance" style="margin-bottom:.4rem"><b>House anchor &mdash; JP Morgan GIS:</b> '
        f'{e(a.get("jp_gis",""))}</div>'
        f'<div class="srcrow">{authors}</div>'
        + (f'<div class="conv-how" style="margin-top:.5rem">{e(a.get("disclaimer",""))}</div>' if a.get("disclaimer") else "")
        + '</div>'
    )


def _view_engine_panel(scan):
    out = []
    meta = scan.get("views_meta", {})
    if meta.get("note"):
        out.append(f'<p style="font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin:0 0 .7rem">{e(meta["note"])}</p>')
    out.append(_macro_anchors_block(meta))
    cards = []
    for v in scan.get("house_views", []):
        ev = "".join(f"<li>{e(x)}</li>" for x in v.get("evidence", []))
        conv = v.get("conviction")
        conv_tbl = _conv_table(v.get("conv_breakdown", []), conv, 10) if v.get("conv_breakdown") else ""
        lock = (f'<div class="lock">Brief consistency: {e(v["brief_consistency"])}</div>'
                if v.get("brief_consistency") else "")
        conv_badge = (f'conviction {conv}/10' if conv is not None else e(v.get("confidence", "")))
        cards.append(
            '<details class="viewcard">'
            '<summary class="vsum">'
            f'<span class="vt">{e(v["ticker"])} {_view_pill(v["view"])}</span>'
            f'<span class="conv-mini"><span class="srcdot src-{e(v.get("confidence","estimated"))}"></span>'
            f'{conv_badge} &nbsp;&#9656;</span>'
            '</summary>'
            '<div class="idea-body">'
            f'<div class="vr">{e(v.get("detail", v.get("rationale","")))}</div>'
            + conv_tbl
            + (f'<div class="conv-how">Why &mdash; the receipts:</div><ul>{ev}</ul>' if ev else "")
            + _sources_row(v.get("sources", []))
            + lock
            + '</div></details>'
        )
    out.append('<div class="split2">' + "".join(cards) + '</div>')
    return "".join(out)


def _allocation_pies(scan):
    alloc = scan.get("allocations") or {}
    cards = []
    for key, title in (("asset_class", "Asset allocation"),
                       ("sector", "Equity sector allocation"),
                       ("region", "Regional allocation")):
        segs = alloc.get(key)
        if not segs:
            continue
        cards.append('<div class="pie-card">'
                     f'<div class="pc-t">{e(title)}</div>'
                     + charts.donut_chart(segs, "")
                     + '</div>')
    if not cards:
        return ""
    return '<div class="pie-row">' + "".join(cards) + '</div>'


def _iv_explainer():
    return (
        '<div class="method-box">'
        '<div class="mb-t">How the implied-vol column is calculated</div>'
        '<p>The vol column is computed by us, not taken from a vendor field. For <b>US single names with '
        'listed options</b> (MU, NVDA, AVGO, AMD, SPY) we pull the Yahoo Finance option chain at the '
        '~360-day expiry, take the at-the-money option mark (bid/ask mid, or last price when the market is '
        'shut), and <b>invert Black–Scholes</b> to solve for the implied volatility &sigma; — we do not trust '
        'Yahoo&rsquo;s own impliedVolatility field, which returns ~0. We also read the 90% put skew the same way. '
        'These are tagged <b>&ldquo;live&rdquo;</b> with a green source dot.</p>'
        '<p>For <b>EU names and the gold ETC</b> (LVMH, SAP, TotalEnergies, Xetra-Gold), which have no listed '
        'options on Yahoo, we compute <b>3-month realized volatility</b> from a year of daily closes and use it '
        'as an implied-vol proxy, tagged <b>&ldquo;RV 3m&rdquo;</b>. Bonds are derived from yields; gold from spot. '
        'The percentile is the rank of today&rsquo;s reading against the name&rsquo;s own history — sourced for the '
        'realized series, and &ldquo;estimated&rdquo; for the US implied series until it accumulates 60 daily snapshots.</p>'
        '</div>'
    )


def _page_portfolio(scan):
    m = scan["metrics"]
    lhs = [_h("Book at a glance", f'{scan["client"].get("display_name","Fable")} · marked live')]
    lhs.append(
        '<div class="statgrid">'
        f'<div class="stat"><div class="sl">AUM</div><div class="sv">{_eurm(m["total_eur"])}</div><div class="ss">{len(scan["positions"])} holdings + cash</div></div>'
        f'<div class="stat"><div class="sl">Largest</div><div class="sv" style="color:var(--red)">{m["largest"]["weight_pct"]}%</div><div class="ss">{e(m["largest"]["ticker"])} &middot; cap 10%</div></div>'
        f'<div class="stat"><div class="sl">USD exposure</div><div class="sv">{m["usd_pct"]}%</div><div class="ss">net ~{m["net_usd_pct"]}% after liabilities</div></div>'
        f'<div class="stat"><div class="sl">Idle cash</div><div class="sv" style="color:var(--gold)">{m["cash_pct"]}%</div><div class="ss">{_eurm(m["cash_eur"])} earning ~0</div></div>'
        '</div>'
    )
    pies = _allocation_pies(scan)
    if pies:
        lhs.append(_h("Allocation", "by asset class, equity sector, and region"))
        lhs.append(pies)
    lhs.append(_h("Headline scanner findings"))
    lhs.append(_findings(m))
    lhs.append(_h("Holdings", "marked live · vol column computed by us"))
    lhs.append(_iv_explainer())
    lhs.append(_holdings_table(scan["positions"]))
    if scan.get("refresh_notes"):
        lhs.append(f'<div class="asof">Live refresh: {e("; ".join(scan["refresh_notes"]))}.</div>')
    lhs.append(_cash_liab_block(scan))
    lhs.append(_h("House view engine", "click any name for the full thesis, score & sources"))
    lhs.append(
        '<p style="font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin:0 0 .7rem">'
        f'<b>Universe:</b> the <b>{len(scan["positions"])} positions the client actually holds</b> — this is a '
        'whole-book scan, not a market screen, so every holding gets an independent house view (LIKE / NEUTRAL / '
        'AVOID / LIKE-as-hedge) scored on a fixed /10 rubric and consistency-locked to the morning brief and the '
        'JP Morgan GIS anchor. New names (outside the book) are screened separately on the Earnings tab and the '
        'Trade Ideas RSI screener, then arrive here as Derivatives Desk <i>New Adds</i>.</p>')
    lhs.append(_view_engine_panel(scan))
    lhs.append('<div style="margin-top:1.5rem">'
               '<a href="ideas.html" style="font-size:13px;color:var(--gold);font-weight:600;text-decoration:none">'
               'Take these into the structuring desk &rarr; Derivatives Desk</a></div>')
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


_SUB_DESC = {"setup": ("Setup signal", "chart vs the product"),
             "pricing": ("Pricing edge", "IV / skew / headroom"),
             "catalyst": ("Catalyst clarity", "event window / gating"),
             "fit": ("Client fit", "solves a stated problem")}


def _idea_conv_table(i):
    rows = ""
    for k in ("setup", "pricing", "catalyst", "fit"):
        lab, desc = _SUB_DESC[k]
        sc, src = i["subs"].get(k, 0), i["sub_src"].get(k, "estimated")
        rows += (f'<tr><td class="k">{lab}</td><td class="s">{sc}/2</td>'
                 f'<td class="w"><span class="srcdot src-{e(src)}"></span>{desc} &middot; {e(src)}</td></tr>')
    return (f'<table class="convtbl"><tr><td class="k">Conviction</td><td class="s">{i["score"]}/8</td>'
            f'<td class="w">setup &middot; pricing &middot; catalyst &middot; fit (0-2 each)</td></tr>{rows}</table>')


def _idea_body(i):
    p = []
    if i.get("origin"):
        p.append(f'<div class="origin">From: {e(i["origin"])}</div>')
    badges = []
    if i.get("tenor"):
        badges.append(f'<span class="badge"><b>Tenor</b> {e(i["tenor"])}</span>')
    if i.get("sizing"):
        badges.append(f'<span class="badge"><b>Size</b> {e(i["sizing"])}</span>')
    if badges:
        p.append('<div class="meta-row">' + "".join(badges) + '</div>')
    p.append(f'<div class="blk">{e(i["what_it_is"])}</div>')
    p.append(f'<div class="blk moves"><b>What moves it:</b> {e(i["what_moves_it"])}</div>')
    p.append('<div class="conv-how">How we arrived at the conviction score:</div>')
    p.append(_idea_conv_table(i))
    p.append(f'<div class="note"><b>Client fit:</b> {e(i["client_note"])}</div>')
    if i.get("portfolio_impact"):
        p.append(f'<div class="impact"><b>How it helps the book:</b> {e(i["portfolio_impact"])}</div>')
    if i.get("risk"):
        p.append(f'<div class="risk"><b>Risk:</b> {e(i["risk"])}</div>')
    p.append(_sources_row(i.get("sources", [])))
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in i.get("tags", []))
    if tags:
        p.append(f'<div class="meta-row" style="margin-top:.55rem">{tags}</div>')
    return "".join(p)


def _val_block(val):
    """Render live valuation multiples for single-name equities."""
    if not val:
        return '<div class="rsi-block"><span class="rsi-na">Valuation multiples: not available (macro/FX/rates instrument or no ticker mapped)</span></div>'
    if val.get("error"):
        return f'<div class="rsi-block"><span class="rsi-na">Valuation multiples: {e(str(val["error"])[:120])} (Yahoo Finance)</span></div>'
    ticker = val.get("ticker", "")
    asof   = val.get("asof", "")
    def badge(label, key):
        v = val.get(key, "N/A")
        return f'<span class="badge"><b>{label}</b>&nbsp;{e(str(v))}</span>'
    badges = " ".join([badge("P/E (ttm)", "trailing_pe_fmt"),
                       badge("Fwd P/E",   "forward_pe_fmt"),
                       badge("EV/EBITDA", "ev_ebitda_fmt"),
                       badge("P/S",       "p_to_s_fmt"),
                       badge("EV/Rev",    "ev_revenue_fmt")])
    return (f'<div class="rsi-block" style="margin-top:.4rem">'
            f'<span style="font-weight:600;font-size:12px">Live multiples ({e(ticker)})</span>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:.25rem">{badges}</div>'
            f'<span style="color:var(--ink-mute);font-size:11px">Source: Yahoo Finance · as of {e(asof)}</span>'
            f'</div>')


def _idea_full_conv_table(i):
    """Conviction table with per-criterion WHY — base /8 PLUS live technical analysis
    (0-2: MAs + Bollinger + Fib) and the RSI check (0-1), folded into a live total /11."""
    rows = ""
    for k in ("setup", "pricing", "catalyst", "fit"):
        lab, _ = _SUB_DESC[k]
        sc  = i["subs"].get(k, 0)
        why = i.get("sub_why", {}).get(k, "")
        rows += (f'<tr><td class="k">{lab}</td><td class="s">{sc}/2</td>'
                 f'<td class="w">{e(why)}</td></tr>')
    idea_data = i.get("idea_data") or {}
    ta = idea_data.get("technicals")
    ta_pt = ta_max = rsi_pt = rsi_max = 0
    if ta and not ta.get("error") and ta.get("ta_score") is not None:
        ta_pt, ta_max = ta["ta_score"], 2
        rows += (f'<tr><td class="k">Technical analysis ★</td><td class="s">{ta_pt}/2</td>'
                 f'<td class="w">{e(ta.get("trend","?"))} ({e(ta.get("cross","no"))} cross); Bollinger %B '
                 f'{ta.get("bb_pctb","?")}; nearest Fib {e(ta.get("nearest_fib",{}).get("level","?"))} — chart '
                 + ("confirms" if ta_pt == 2 else "is mixed on" if ta_pt == 1 else "contradicts") + " the structure.</td></tr>")
    if idea_data and not idea_data.get("error") and idea_data.get("rsi") is not None:
        crowd = idea_data.get("crowd_vs_us", False)
        rsi_pt, rsi_max = (0 if crowd else 1), 1
        rows += (f'<tr><td class="k">RSI check ★</td><td class="s">{rsi_pt}/1</td>'
                 f'<td class="w">RSI {idea_data.get("rsi","?")} · {e(idea_data.get("verdict","?"))} (absolute 30/70) — '
                 + ("⚑ chasing an extreme: 0 pts" if crowd else "neutral or supportive: 1 pt") + "</td></tr>")
    live_total = i["score"] + ta_pt + rsi_pt
    live_max   = 8 + ta_max + rsi_max
    return (f'<table class="convtbl">'
            f'<tr><td class="k">Live conviction</td><td class="s">{live_total}/{live_max}</td>'
            f'<td class="w">setup · pricing · catalyst · fit (/8) + technical analysis + RSI, live</td></tr>'
            f'{rows}</table>')


def _idea_full_dropdown(i):
    """Full 8-section expandable dropdown for a Derivatives Lab idea."""
    tier      = i["tier"].lower()
    tickers   = "".join(f'<span class="tag">{e(t)}</span>' for t in i.get("tickers", []))
    idea_data = i.get("idea_data") or {}
    val       = idea_data.get("valuation") if idea_data else None

    def sec(label, body_html):
        return (f'<div class="tb-label">{e(label)}</div>'
                f'<div class="tb-text">{body_html}</div>')

    # 1 — What does [X] do
    s1 = sec("What it does", e(i["what_it_is"]))

    # 2 — Catalyst
    cat_text = i.get("catalyst_text") or i.get("what_moves_it", "")
    s2 = sec("Catalyst", e(cat_text))

    # 3 — Fundamental thesis + valuation
    thesis = i.get("fundamental_thesis") or ""
    s3 = sec("Fundamental thesis", e(thesis) + _val_block(val))

    # 4 — Technical analysis (50/100/200 DMA · Bollinger · Fibonacci)
    ta = (idea_data or {}).get("technicals")
    s4 = sec("Technical analysis · 50/100/200 DMA · Bollinger · Fibonacci", _ta_block(ta))

    # 5 — RSI positioning (absolute 30/70)
    s5 = sec("RSI positioning (absolute 30/70)",
             _rsi_block(idea_data if idea_data else None))

    # 6 — Conviction score with WHY per criterion
    s6 = sec("Conviction score", _idea_full_conv_table(i))

    # 7 — Client fit
    s7c = sec("Client fit", e(i["client_note"]))

    # 7 — Risk / what would make it wrong
    risk_text = i.get("risk") or i.get("what_moves_it", "")
    s7 = (f'<div class="tb-label">Risk / what would make it wrong</div>'
          f'<div class="tb-risk">{e(risk_text)}</div>')

    # 8 — How it helps the book
    impact = i.get("portfolio_impact") or ""
    s8 = sec("How it helps the book", e(impact))

    badges = []
    if i.get("product_type"):
        badges.append(f'<span class="ptag">Product · {e(i["product_type"])}</span>')
    if i.get("objective"):
        badges.append(f'<span class="otag">Objective · {e(i["objective"])}</span>')
    if i.get("tenor"):
        badges.append(f'<span class="badge"><b>Tenor</b>&nbsp;{e(i["tenor"])}</span>')
    if i.get("sizing"):
        badges.append(f'<span class="badge"><b>Size</b>&nbsp;{e(i["sizing"])}</span>')
    meta_row = ('<div class="meta-row">' + "".join(badges) + '</div>') if badges else ""
    origin_row = (f'<div class="origin">From: {e(i["origin"])}</div>') if i.get("origin") else ""
    tags_row = ""
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in i.get("tags", []))
    if tags:
        tags_row = f'<div class="meta-row" style="margin-top:.55rem">{tags}</div>'

    body = (
        f'<div class="trade-body">'
        + origin_row + meta_row
        + f'<div class="meta-row"><span class="rules-tag">{e(i["rules"])}</span>{tickers}</div>'
        + s1 + s2 + s3 + s4 + s5 + s6 + s7c + s7 + s8
        + _sources_row(i.get("sources", []))
        + tags_row
        + '</div>'
    )

    # live conviction for the badge: base /8 + TA (0-2) + RSI (0-1)
    _ta_ok = bool(ta and not ta.get("error") and ta.get("ta_score") is not None)
    _rsi_ok = bool(idea_data and not idea_data.get("error") and idea_data.get("rsi") is not None)
    _ta_pt = ta["ta_score"] if _ta_ok else 0
    _rsi_pt = (0 if idea_data.get("crowd_vs_us") else 1) if _rsi_ok else 0
    live_total = i["score"] + _ta_pt + _rsi_pt
    live_max   = 8 + (2 if _ta_ok else 0) + (1 if _rsi_ok else 0)

    summary_tags = ""
    if i.get("product_type"):
        summary_tags += f'<span class="ptag">{e(i["product_type"])}</span>'
    return (
        f'<details class="trade-drop">'
        f'<summary>'
        f'<div>'
        f'<div class="td-name">{e(i["title"])}</div>'
        f'<div style="font-size:11px;color:var(--ink-mute);margin-top:2px">'
        f'{e(i["rules"])} &middot; {e(i.get("asset_group",""))} &middot; {e(i.get("tenor",""))}'
        f'</div>'
        f'</div>'
        f'<div class="td-meta">'
        + summary_tags
        + f'<span class="tier {tier}">{e(i["tier"])}</span>'
        f'<span class="conv-badge">{live_total}/{live_max}</span>'
        f'<span style="font-size:11px;color:var(--ink-mute)">&#9656; expand</span>'
        f'</div>'
        f'</summary>'
        + body
        + '</details>'
    )


def _render_new_add(i):
    return _idea_full_dropdown(i)


def _render_enhance(i):
    return _idea_full_dropdown(i)


def _group_block(grouped, render_fn):
    out = []
    for gname, items in grouped:
        out.append(f'<div class="grp"><span class="gname">{e(gname)}</span><span class="gline"></span>'
                   f'<span class="gcount">{len(items)} idea{"s" if len(items) != 1 else ""}</span></div>')
        out.append('<div class="split2">' + "".join(render_fn(i) for i in items) + '</div>')
    return "".join(out)


def _overall_summary_block(scan):
    s = scan.get("overall_summary")
    if not s:
        return ""
    pts = "".join(f'<li><span class="gchip">{e(p.get("group",""))}</span><span>{p.get("text","")}</span></li>'
                  for p in s.get("points", []))
    return (
        '<div class="summary-box">'
        f'<div class="sh">{e(s.get("headline",""))}</div>'
        f'<div class="stance">{e(s.get("stance",""))}</div>'
        f'<ul class="sumpts">{pts}</ul></div>')


def _page_ideas(scan):
    meta = scan.get("ivol_meta", {})
    fable = e(scan["client"].get("display_name", "Fable"))
    lhs = [_icon_legend()]
    lhs.append(_h("What we're suggesting", "the whole book, in one screen"))
    lhs.append(_overall_summary_block(scan))
    lhs.append(
        '<div class="method-box">'
        '<div class="mb-t">The universe — where these ideas come from</div>'
        '<p>The desk draws from <b>two universes</b>, both defined and screened upstream:</p>'
        '<ul>'
        f'<li><b>Enhancements</b> — universe is the <b>{len(scan.get("positions", []))} positions the client '
        'holds</b> (the Portfolio book). The Book Scanner turns each into a structure idea.</li>'
        '<li><b>New Adds</b> — universe is everything <i>outside</i> the book that clears an upstream screen: the '
        '<b>Earnings screener</b> ($10bn+ cap, US/Korea, Tech/Financials/Industrials/Utilities) and the '
        '<b>macro book</b>, plus the <b>Trade Ideas RSI screener</b> (~140-name cross-asset universe). Only names '
        'that fit this client&rsquo;s mandate and patterns are carried through.</li>'
        '</ul></div>')
    lhs.append(_product_shelf())
    lhs.append(_positioning_method())
    lhs.append(_loss_recovery_block(scan))
    lhs.append(_h("New adds", "desk ideas mapped to this client"))
    lhs.append(f'<p style="font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin:0 0 .4rem">'
               f'New exposures drawn from the Earnings screener and the macro book, filtered to the patterns in '
               f'{fable}&rsquo;s book &mdash; AI &amp; semis, enterprise software, large-cap quality, energy &amp; gold '
               f'hedges, duration; comfortable with structures. Each idea is tagged with its product type and '
               f'objective. Tenor floors: equity structured products &ge; 3m, OTC &ge; 1m, rates structured products &ge; 2y.</p>')
    lhs.append(_group_block(scan.get("new_adds_grouped", []), _render_new_add))
    lhs.append(_h("Enhancing the existing book", "structures on positions the client already holds"))
    lhs.append('<p style="font-size:12.5px;color:var(--ink-soft);line-height:1.6;margin:0 0 .4rem">'
               'Structures on positions the client already holds &mdash; the detailed why, the technical and RSI '
               'reads, how we arrived at the conviction score, and how each one helps the overall portfolio. '
               'Click any idea to expand.</p>')
    lhs.append(_group_block(scan.get("enhance_grouped", []), _render_enhance))
    lhs.append(
        '<div class="asof" style="margin-top:1.6rem">'
        'Live conviction /11 = setup &middot; pricing &middot; catalyst &middot; client fit (/8) + technical '
        'analysis (0&ndash;2: moving averages + Bollinger + Fibonacci) + RSI check (0&ndash;1, absolute 30/70), '
        'recomputed every refresh. '
        'New Adds enter post-catalyst where the Earnings desk says HOLD, so nothing here contradicts the brief or '
        'the per-name house views. '
        f'{e(meta.get("source", meta.get("honesty","")))} '
        'Issuer credit: every note is senior unsecured paper &mdash; cap any single issuer at 20% of the structure book. '
        'Demo book, not investment advice.</div>')
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
        "trades.html":   ("Trade Ideas", "Trade Ideas + Live Book", _page_trades(brief, trades)),
    }
    for fname, (active, title, lhs) in pages.items():
        htmldoc = _shell(fname, title, regime, note, lhs, brief)
        with open(os.path.join(HERE, fname), "w", encoding="utf-8") as f:
            f.write(htmldoc)

    # client book module — two extra tabs, only when a scan is supplied
    if scan:
        for fname, title, lhs_html, mast in (
            ("portfolio.html", "Fable / Portfolio", _page_portfolio(scan), _portfolio_masthead(scan)),
            ("ideas.html", "Derivatives Desk", _page_ideas(scan), _ideas_masthead(scan)),
        ):
            htmldoc = _shell(fname, title, regime, note, lhs_html, brief, masthead_html=mast)
            with open(os.path.join(HERE, fname), "w", encoding="utf-8") as f:
                f.write(htmldoc)

    # iframe fragments
    enr = brief.get("trade_enrichments", {})
    rsi = brief.get("rsi_data", {})
    frags = {
        "consensus.html":   ("The Consensus · Bid / Offer", brief.get("consensus", "")),
        "talking.html":     ("Talking Points Today", _client_ammo_body(brief.get("client_ammo", []))),
        "correlation.html": ("Correlation Regime", brief.get("correlation_regime", "")),
        "volskew.html":     ("Vol & Skew", brief.get("vol_skew", "")),
        "sectorrv.html":    ("Sector & RV", brief.get("sector_rv", "")),
        "positioning.html": ("Positioning & Flows", brief.get("positioning", "")),
        "book.html":        ("Live Book", _book_accordion(trades, enrichments=enr, rsi_data=rsi)),
    }
    for fname, (title, body) in frags.items():
        with open(os.path.join(FRAG_DIR, fname), "w", encoding="utf-8") as f:
            f.write(_frag_doc(title, body))

    book.log(f"shark format written: {', '.join(pages)} + frag/*")
