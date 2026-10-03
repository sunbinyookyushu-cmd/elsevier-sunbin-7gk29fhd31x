# -*- coding: utf-8 -*-
"""Slope-chart poster, light editorial, enlarged type. Two artboards:
  Main.dc.html        with headline block
  FigureOnly.dc.html  no title: legend + panels + caption (journal figure)"""
import json, html

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
data = json.load(open(GACI + r"\_rank_bump_data.json", encoding="utf-8"))
for e in data["countries"]:
    if e["label"] == "IL":
        e["label"] = "Israel"

BG, GRID = "#fbfaf7", "#e7e2d8"
INK, SEC, MUT = "#20242b", "#4c5560", "#8a919b"
ACC = "#D55E00"
SLATE, SLATE_LAB = "#7f99b3", "#5b6673"

W, H = 762, 700
XL, XR = 224, 538
TOP, TB = 46, 508
DIV = TB + 16
CB = 668
ROW = (TB - TOP) / 19.0


def yr_rank(r):
    if r is None:
        return CB - 4
    if r <= 20:
        return TOP + (r - 1) * ROW
    return DIV + 14 + (min(r, 110) - 21) / 89.0 * (CB - DIV - 22)


def dodge(items, key, mingap=22.0):
    items = sorted(items, key=key)
    ys = [key(i) for i in items]
    for k in range(1, len(ys)):
        if ys[k] - ys[k - 1] < mingap:
            ys[k] = ys[k - 1] + mingap
    return {id(i): yy for i, yy in zip(items, ys)}


def svg_panel(entries, title):
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'style="display: block; overflow: visible" role="img" aria-label="{html.escape(title)}">']
    s.append(f'<text x="{XL}" y="26" text-anchor="middle" font-size="22" font-weight="700" '
             f'letter-spacing="2" fill="{SEC}" class="ff-s">1996</text>')
    s.append(f'<text x="{XR}" y="26" text-anchor="middle" font-size="22" font-weight="700" '
             f'letter-spacing="2" fill="{ACC}" class="ff-s">2023</text>')
    for xx in (XL, XR):
        s.append(f'<line x1="{xx}" y1="{TOP-8}" x2="{xx}" y2="{CB}" stroke="{GRID}" stroke-width="1"></line>')
    s.append(f'<line x1="{XL-64}" y1="{DIV}" x2="{XR+64}" y2="{DIV}" stroke="{GRID}" '
             f'stroke-width="1" stroke-dasharray="5 5"></line>')
    s.append(f'<text x="{XR+64}" y="{DIV+16}" text-anchor="end" font-size="13" fill="{MUT}" '
             f'font-style="italic" class="ff-s">below top 20 (compressed scale)</text>')

    ents = []
    for e in entries:
        r96 = e["r96"]
        alt = None
        if r96 is None:
            alt = [r for y, r in e["series"] if r is not None][0]
        ents.append(dict(e=e, r96=r96, alt=alt,
                         yl=yr_rank(r96) if r96 is not None else yr_rank(None),
                         yr=yr_rank(e["r23"])))
    dl = dodge(ents, lambda i: i["yl"])
    dr = dodge(ents, lambda i: i["yr"])

    for i in sorted(ents, key=lambda i: (i["e"]["riser"], )):
        e = i["e"]
        riser = e["riser"]
        col = ACC if riser else SLATE
        wd = 3.4 if riser else 1.5
        y1, y2 = i["yl"], i["yr"]
        dash = ' stroke-dasharray="7 6"' if i["r96"] is None else ""
        cx1, cx2 = XL + (XR - XL) * 0.42, XL + (XR - XL) * 0.58
        s.append(f'<g class="sr {"srA" if riser else "srC"}">')
        s.append(f'<path d="M {XL} {y1:.1f} C {cx1:.1f} {y1:.1f}, {cx2:.1f} {y2:.1f}, {XR} {y2:.1f}" '
                 f'fill="none" stroke="{col}" stroke-width="{wd}" stroke-linecap="round"{dash} class="ln"></path>')
        for xx, yy in ((XL, y1), (XR, y2)):
            s.append(f'<circle cx="{xx}" cy="{yy:.1f}" r="{5 if riser else 3.4}" fill="{col}" '
                     f'stroke="{BG}" stroke-width="1.8"></circle>')
        name = html.escape(e["label"])
        ly = dl[id(i)]
        ltxt = f'{name} \u00b7 #{i["alt"]} in \u201900' if i["r96"] is None else f'{name} \u00b7 #{i["r96"]}'
        lf = f'font-weight="700" fill="{ACC}"' if riser else f'font-weight="400" fill="{SLATE_LAB}"'
        s.append(f'<text x="{XL-14}" y="{ly+4:.1f}" text-anchor="end" font-size="17" {lf} class="lb ff-s">{ltxt}</text>')
        ry = dr[id(i)]
        if riser:
            gain = f' <tspan font-size="14" font-weight="500" opacity="0.85">\u25b2{(i["r96"] or i["alt"]) - e["r23"]}</tspan>'
            s.append(f'<text x="{XR+14}" y="{ry+5:.1f}" font-size="18" font-weight="700" fill="{ACC}" '
                     f'class="lb ff-s">#{e["r23"]} {name}{gain}</text>')
        else:
            s.append(f'<text x="{XR+14}" y="{ry+5:.1f}" font-size="17" font-weight="400" fill="{SLATE_LAB}" '
                     f'class="lb ff-s">#{e["r23"]} {name}</text>')
        s.append('</g>')
    s.append('</svg>')
    return "\n".join(s)


CAPTION = ("Only the 1996 and 2023 cross-sections are shown; ranks beyond 20 sit on a compressed scale "
           "below the divider, and Shanghai Pudong enters the network in 2000 (dashed). Country ranks are "
           "computed from the full airport network, so estimation-sample availability plays no role. The "
           "ascent of the Gulf and Turkish hubs concentrates after 2010, consistent with the temporal "
           "placement of the identifying variation (Section 5.2).")

LEGEND = f"""<div style="display: flex; flex-direction: column; gap: 9px; flex-shrink: 0; padding-bottom: 8px">
      <div style="display: flex; align-items: center; gap: 9px">
        <svg width="30" height="12" viewBox="0 0 30 12" style="display: block"><line x1="1" y1="10" x2="29" y2="2" stroke="{ACC}" stroke-width="3.2" stroke-linecap="round"></line></svg>
        <span class="ff-s" style="font-size: 15.5px; color: {SEC}; font-weight: 600">Entrant from outside the top 20</span>
      </div>
      <div style="display: flex; align-items: center; gap: 9px">
        <svg width="30" height="12" viewBox="0 0 30 12" style="display: block"><line x1="1" y1="6" x2="29" y2="6" stroke="{SLATE}" stroke-width="1.6" stroke-linecap="round"></line></svg>
        <span class="ff-s" style="font-size: 15.5px; color: {SEC}; font-weight: 400">Incumbent, 1996 top 20</span>
      </div>
    </div>"""


def build(with_title):
    if with_title:
        header = f"""
  <div class="ff-s" style="font-size: 13px; letter-spacing: 0.22em; color: {ACC}; text-transform: uppercase; font-weight: 600">Figure 2 &middot; Global Air Connectivity Index</div>
  <div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 48px; margin-top: 14px">
    <div style="max-width: 980px">
      <div style="font-size: 52px; line-height: 1.05; font-weight: 600; color: {INK}; letter-spacing: -0.012em">Twenty-seven years,<br>one reordered sky</div>
      <div style="font-size: 20px; color: {SEC}; margin-top: 16px">Istanbul climbs ninety-six places, Dubai eighty-nine, the Emirates take the top country seat: the hubs that lead in 2023 were barely on the map in 1996.</div>
    </div>
    {LEGEND}
  </div>"""
    else:
        header = f"""
  <div style="display: flex; justify-content: flex-end">
    {LEGEND}
  </div>"""
    pa = svg_panel(data["airports"], "Airport GACI rank, 1996 versus 2023")
    pb = svg_panel(data["countries"], "Country hub-quality rank, 1996 versus 2023")
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600&family=Archivo:wght@400;500;600;700&display=swap">
  <style>
    body {{ margin: 0; background: {BG}; font-family: 'Newsreader', Georgia, 'Times New Roman', serif; }}
    a {{ color: {ACC}; }} a:hover {{ opacity: 0.8; }}
    .ff-s {{ font-family: 'Archivo', 'Segoe UI', Arial, sans-serif; }}
    svg text.ff-s {{ font-family: 'Archivo', 'Segoe UI', Arial, sans-serif; }}
    .sr .ln {{ transition: stroke-width 130ms ease; }}
    .srA:hover .ln {{ stroke-width: 4.6px; }}
    .srC:hover .ln {{ stroke-width: 2.6px; }}
    .srC:hover .lb {{ font-weight: 600; }}
  </style>
</helmet>
<div style="width: 1660px; background: {BG}; padding: 48px 56px 40px 56px; box-sizing: border-box">{header}
  <div style="display: flex; gap: 20px; margin-top: 30px">
    <div style="flex: 1 1 0">
      <div class="ff-s" style="font-size: 16px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: {SEC}; margin-bottom: 8px">(a) Airports &middot; GACI rank</div>
      {pa}
    </div>
    <div style="flex: 1 1 0">
      <div class="ff-s" style="font-size: 16px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: {SEC}; margin-bottom: 8px">(b) Countries &middot; hub quality (GACI<span style="vertical-align: sub; font-size: 10px">cwm</span>) rank</div>
      {pb}
    </div>
  </div>
  <div style="border-top: 1px solid {GRID}; margin-top: 26px; padding-top: 14px; font-size: 16px; line-height: 1.6; color: {MUT}; max-width: 1420px">{CAPTION}</div>
</div>
</x-dc>
</body>
</html>
"""


base = GACI + r"\_design_rankbump"
open(base + r"\Main.dc.html", "w", encoding="utf-8").write(build(True))
open(base + r"\FigureOnly.dc.html", "w", encoding="utf-8").write(build(False))
print("wrote Main.dc.html + FigureOnly.dc.html")

cv = {"artboards": [
        {"file": "Main.dc.html", "x": 0, "y": 0, "w": 1660, "h": 1160, "title": "With title", "print": "fixed"},
        {"file": "FigureOnly.dc.html", "x": 0, "y": 1300, "w": 1660, "h": 980, "title": "Figure only", "print": "fixed"},
      ],
      "launch": {"view": "canvas"}}
open(base + r"\canvas.json", "w", encoding="utf-8").write(json.dumps(cv, indent=1))
print("wrote canvas.json")
