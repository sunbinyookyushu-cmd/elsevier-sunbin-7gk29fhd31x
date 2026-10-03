# -*- coding: utf-8 -*-
"""Generate two artboards from _rank_bump_data.json:
  Main.dc.html          night-approach dark editorial (leading candidate)
  PrintEditorial.dc.html refined light version for print/paper use
Palette roles (validated, deliberate emphasis hierarchy + universal direct
labels): entrants (accent, glow on dark), top-5 incumbents, context."""
import json, html

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
data = json.load(open(GACI + r"\_rank_bump_data.json", encoding="utf-8"))
for e in data["countries"]:
    if e["label"] == "IL":
        e["label"] = "Israel"

YEARS = [1996, 2000, 2005, 2010, 2015, 2020, 2023]
SHOW = 20

MODES = {
    "dark": dict(
        bg="#0b1422", grid="#182742", guide="#131f36", band="#081020",
        ink="#f2ede4", sec="#b8c2cf", mut="#6f7e94",
        acc="#FF8A3D", top="#A8C0DE", ctx="#567394",
        lab_top="#dde6f2", lab_ctx="#8fa0b6", chipbg="#101d33",
        chipbd="#233650", rule="#1d2c46", glow=True,
    ),
    "light": dict(
        bg="#fbfaf7", grid="#e9e5dd", guide="#f1eee7", band="#f0ece3",
        ink="#20242b", sec="#4c5560", mut="#8a919b",
        acc="#D55E00", top="#1f3d63", ctx="#7f99b3",
        lab_top="#2c3947", lab_ctx="#5b6673", chipbg="#f4f1ea",
        chipbd="#e2dccf", rule="#e6e1d6", glow=False,
    ),
}

W, H = 760, 648
PL, PT = 42, 14
PW, PB = 470, 520
ROW = (PB - PT) / (SHOW - 1)
BT, BB = PB + 34, PB + 74
XT = BB + 34


def x(year):
    return PL + (year - 1996) / 27.0 * PW


def y(rank, j=0):
    if rank <= SHOW:
        return PT + (rank - 1) * ROW
    return BT + 10 + (j % 5) * 5


def svg_panel(entries, title, m):
    s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'style="display: block; overflow: visible" role="img" aria-label="{html.escape(title)}">']
    for yr in YEARS:  # vertical year guides
        s.append(f'<line x1="{x(yr):.1f}" y1="{PT}" x2="{x(yr):.1f}" y2="{PB}" stroke="{m["guide"]}" stroke-width="1"></line>')
    for r in (1, 5, 10, 15, 20):
        yy = y(r)
        s.append(f'<line x1="{PL}" y1="{yy:.1f}" x2="{PL+PW}" y2="{yy:.1f}" stroke="{m["grid"]}" stroke-width="1"></line>')
        s.append(f'<text x="{PL-10}" y="{yy+4:.1f}" text-anchor="end" font-size="12" fill="{m["mut"]}" class="ff-s">{r}</text>')
    s.append(f'<rect x="{PL}" y="{BT}" width="{PW}" height="{BB-BT}" rx="3" fill="{m["band"]}"></rect>')
    s.append(f'<text x="{PL+PW-8}" y="{BT+24}" text-anchor="end" font-size="11" fill="{m["mut"]}" font-style="italic" class="ff-s">rank &gt; 20</text>')
    for yr in YEARS:
        s.append(f'<text x="{x(yr):.1f}" y="{XT}" text-anchor="middle" font-size="12" fill="{m["mut"]}" class="ff-s">\u2019{str(yr)[2:]}</text>')

    def cls(e):
        return 2 if e["riser"] else (1 if e["r23"] <= 5 else 0)
    for e in sorted(entries, key=cls):
        riser = e["riser"]
        col = m["acc"] if riser else (m["top"] if e["r23"] <= 5 else m["ctx"])
        wd = 3.2 if riser else (2.2 if e["r23"] <= 5 else 1.4)
        j = e["r23"]
        pts = [(x(yr), y(r, j)) for yr, r in e["series"] if r is not None]
        pl = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        gcls = "srA glow" if (riser and m["glow"]) else ("srA" if riser else ("srB" if e["r23"] <= 5 else "srC"))
        s.append(f'<g class="sr {gcls}">')
        s.append(f'<polyline points="{pl}" fill="none" stroke="{col}" stroke-width="{wd}" '
                 f'stroke-linejoin="round" stroke-linecap="round" class="ln"></polyline>')
        for a, b in pts:
            s.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{4.4 if riser else 3.6}" fill="{col}" stroke="{m["bg"]}" stroke-width="1.6"></circle>')
        ex, ey = pts[-1]
        name = html.escape(e["label"])
        if riser:
            tail = f'#{e["r96"]} \u2192 #{e["r23"]}' if e["r96"] is not None else f'new \u2192 #{e["r23"]}'
            s.append(f'<text x="{ex+13:.1f}" y="{ey+4:.1f}" font-size="13.5" font-weight="700" fill="{m["acc"]}" class="lb ff-s">{name}'
                     f' <tspan font-size="11" font-weight="500" opacity="0.85">{tail}</tspan></text>')
        else:
            fw = "600" if e["r23"] <= 5 else "400"
            fc = m["lab_top"] if e["r23"] <= 5 else m["lab_ctx"]
            s.append(f'<text x="{ex+13:.1f}" y="{ey+4:.1f}" font-size="13" font-weight="{fw}" fill="{fc}" class="lb ff-s">{name}</text>')
        s.append('</g>')
    s.append('</svg>')
    return "\n".join(s)


def chip(m, place, move):
    return (f'<div style="display: flex; align-items: baseline; gap: 8px; padding: 8px 14px; '
            f'background: {m["chipbg"]}; border: 1px solid {m["chipbd"]}; border-radius: 999px">'
            f'<span class="ff-s" style="font-size: 13px; font-weight: 700; color: {m["ink"]}">{place}</span>'
            f'<span class="ff-s" style="font-size: 12.5px; font-weight: 600; color: {m["acc"]}">{move}</span></div>')


def legend_item(m, col, wd, label, bold=False):
    return (f'<div style="display: flex; align-items: center; gap: 8px">'
            f'<svg width="30" height="12" viewBox="0 0 30 12" style="display: block">'
            f'<line x1="1" y1="6" x2="29" y2="6" stroke="{col}" stroke-width="{wd}" stroke-linecap="round"></line>'
            f'<circle cx="15" cy="6" r="3.6" fill="{col}" stroke="{m["bg"]}" stroke-width="1.4"></circle></svg>'
            f'<span class="ff-s" style="font-size: 12.5px; color: {m["sec"]}; font-weight: {"600" if bold else "400"}">{label}</span></div>')


CAPTION = ("Country ranks are computed from the full airport network (all economies with scheduled service), "
           "so data availability in the estimation sample plays no role. Ranks beyond 20 are collapsed into the "
           "shaded band. Highlighted trajectories mark entrants from outside the top 20 in 1996. The rise of the "
           "Gulf and Turkish hubs concentrates after 2010, consistent with the temporal placement of the "
           "identifying variation (Section 5.2).")


def page(m):
    glow_css = (f'.glow .ln {{ filter: drop-shadow(0 0 7px rgba(255, 138, 61, 0.5)); }}\n'
                f'    .glow circle {{ filter: drop-shadow(0 0 5px rgba(255, 138, 61, 0.55)); }}'
                ) if m["glow"] else ""
    chips = "".join([
        chip(m, "Istanbul", "#98 \u2192 #2"), chip(m, "Dubai", "#92 \u2192 #3"),
        chip(m, "Jeddah", "#89 \u2192 #12"), chip(m, "UAE", "#21 \u2192 #1"),
        chip(m, "Qatar", "#54 \u2192 #4"), chip(m, "Ethiopia", "#86 \u2192 #14"),
    ])
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;1,6..72,500&family=Archivo:wght@400;500;600;700&display=swap">
  <style>
    body {{ margin: 0; background: {m["bg"]}; font-family: 'Newsreader', Georgia, 'Times New Roman', serif; }}
    a {{ color: {m["acc"]}; }} a:hover {{ opacity: 0.8; }}
    .ff-s {{ font-family: 'Archivo', 'Segoe UI', Arial, sans-serif; }}
    svg text.ff-s {{ font-family: 'Archivo', 'Segoe UI', Arial, sans-serif; }}
    .sr .ln {{ transition: stroke-width 130ms ease; }}
    .srA:hover .ln {{ stroke-width: 4.4px; }}
    .srB:hover .ln {{ stroke-width: 3.2px; }}
    .srC:hover .ln {{ stroke-width: 2.6px; }}
    .srC:hover .lb {{ font-weight: 600; }}
    {glow_css}
  </style>
</helmet>
<div style="width: 1660px; background: {m["bg"]}; padding: 52px 56px 40px 56px; box-sizing: border-box">
  <div class="ff-s" style="font-size: 11px; letter-spacing: 0.22em; color: {m["acc"]}; text-transform: uppercase; font-weight: 600">Figure 2 &middot; Global Air Connectivity Index &middot; 1996&ndash;2023</div>
  <div style="font-size: 44px; line-height: 1.08; font-weight: 600; color: {m["ink"]}; margin-top: 14px; letter-spacing: -0.01em">The ascent of the Gulf and Turkish hubs</div>
  <div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 40px; margin-top: 12px">
    <div style="font-size: 17px; font-style: italic; color: {m["sec"]}; max-width: 760px">Rank trajectories for the top fifteen of 2023 &mdash; highlighted lines entered from outside the top twenty in 1996.</div>
    <div style="display: flex; gap: 18px; align-items: center; flex-shrink: 0">
      {legend_item(m, m["acc"], 3.2, "Entrant since 1996", bold=True)}
      {legend_item(m, m["top"], 2.2, "Top-five incumbent")}
      {legend_item(m, m["ctx"], 1.4, "Other incumbent")}
    </div>
  </div>
  <div style="display: flex; gap: 10px; margin-top: 22px; flex-wrap: wrap">{chips}</div>
  <div style="display: flex; gap: 26px; margin-top: 30px">
    <div style="flex: 1 1 0">
      <div class="ff-s" style="font-size: 13px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {m["sec"]}; margin-bottom: 12px">(a) Airports &middot; GACI rank</div>
      {svg_panel(data["airports"], "Airport GACI rank trajectories", m)}
    </div>
    <div style="flex: 1 1 0">
      <div class="ff-s" style="font-size: 13px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {m["sec"]}; margin-bottom: 12px">(b) Countries &middot; hub quality (GACI<span style="vertical-align: sub; font-size: 10px">cwm</span>) rank</div>
      {svg_panel(data["countries"], "Country hub-quality rank trajectories", m)}
    </div>
  </div>
  <div style="border-top: 1px solid {m["rule"]}; margin-top: 24px; padding-top: 14px; font-size: 13.5px; line-height: 1.6; color: {m["mut"]}; max-width: 1420px">{CAPTION}</div>
</div>
</x-dc>
</body>
</html>
"""


base = GACI + r"\_design_rankbump"
open(base + r"\Main.dc.html", "w", encoding="utf-8").write(page(MODES["dark"]))
open(base + r"\PrintEditorial.dc.html", "w", encoding="utf-8").write(page(MODES["light"]))
print("wrote Main.dc.html + PrintEditorial.dc.html")

cv = {"artboards": [
        {"file": "Main.dc.html", "x": 0, "y": 0, "w": 1660, "h": 1120, "title": "Night approach", "print": "fixed"},
        {"file": "PrintEditorial.dc.html", "x": 0, "y": 1260, "w": 1660, "h": 1120, "title": "Print editorial", "print": "fixed"},
      ],
      "launch": {"view": "canvas"}}
open(base + r"\canvas.json", "w", encoding="utf-8").write(json.dumps(cv, indent=1))
print("wrote canvas.json")
