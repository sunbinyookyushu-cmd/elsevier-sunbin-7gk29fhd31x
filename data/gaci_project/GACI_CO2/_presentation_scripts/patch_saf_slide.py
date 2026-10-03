# -*- coding: utf-8 -*-
"""Patch the SAF slide of GACI_CO2_presentation.pptx IN PLACE (2026-09-02).

Replaces the 'LIVE DEMO' box + QR code + artifact URL with a plain, static
version: the levels figure CO2_saf_levels.png (what the simulator showed) on the
left, and on the right a 'how it is computed' box plus a native (editable)
table of the scenario numbers. Everything else on the slide, and every other
slide, is untouched. A timestamped backup of the pptx is written first.
The same slide layout is mirrored in build_co2_deck.py (slide 33 block) so a
full rebuild would give the same result.
"""
import os, shutil, datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
CO2 = os.path.join(GACI, "GACI_CO2")
PPTX = os.path.join(GACI, "GACI_CO2_presentation.pptx")
FIG = os.path.join(CO2, "CO2_saf_levels.png")

NAVY = RGBColor(0x23, 0x2A, 0x55); GOLD = RGBColor(0xE2, 0xA8, 0x5A)
INK = RGBColor(0x1E, 0x1E, 0x24); GRAY = RGBColor(0x6E, 0x6E, 0x6E)
GREEN = RGBColor(0x2E, 0x7D, 0x5B); NAVY_T = RGBColor(0xE9, 0xEB, 0xF4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF); RED = RGBColor(0xB0, 0x41, 0x3E)


def setp(p, text, size, bold=False, color=INK, font="Calibri", align=None,
         italic=False):
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    r.font.name = font; r.font.color.rgb = color
    if align is not None:
        p.alignment = align
    return r


def rect(s, x, y, w, h, fill, rounded=False, radius=None):
    shp = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    shp.line.fill.background(); shp.shadow.inherit = False
    if rounded and radius is not None:
        shp.adjustments[0] = radius
    return shp


def saf_right_panel(s, x=7.45, y=1.95, w=5.15):
    """'How it is computed' box + native table. Shared with build_co2_deck.py."""
    box = rect(s, x, y, w, 2.04, NAVY_T, rounded=True, radius=0.08)
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.20); tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.12); tf.margin_bottom = Inches(0.08)
    setp(tf.paragraphs[0], "HOW THE SCENARIO IS COMPUTED", 11, True, NAVY)
    p = tf.add_paragraph(); p.space_before = Pt(3); p.space_after = Pt(4)
    setp(p, "E(s, r)  =  838 Mt  \u00d7  [ 1 \u2212 s \u00d7 r ]", 16, True, INK,
         "Cambria")
    lines = [
        ("838 Mt", " = world aviation CO2 in 2023 (bunker convention); "
                   "2023 scheduled traffic held fixed, fuel backed out at "
                   "3.15 kg CO2 per kg Jet A."),
        ("s", " = SAF blend share on the ReFuelEU path: 2% (2025), 6% (2030), "
              "20% (2035), 34% (2040), 42% (2045), 70% (2050)."),
        ("r", " = life-cycle CO2 saving of SAF vs fossil Jet A: 50 / 65 / 80% "
              "(literature range)."),
        ("g per $", " = E(s, r) \u00f7 attributed trade ($7.8 tn): "
                    "21 g/$ in 2023, 9\u201314 g/$ on the 2050 path."),
    ]
    for k, v in lines:
        p = tf.add_paragraph(); p.space_after = Pt(2)
        setp(p, k, 10.5, True, NAVY); setp(p, v, 10.5, False, INK)

    rows = [
        ("Mt CO2 per year", "SAF blend", "r = 50%", "r = 65%", "r = 80%"),
        ("2023 actual", "0%", "838", "838", "838"),
        ("2035 mandate", "20%", "754", "729", "704"),
        ("2050 mandate", "70%", "545", "457", "369"),
        ("CO2 saved in 2050", "", "293 Mt", "381 Mt", "469 Mt"),
        ("\u2026 as % of the 356 Mt", "", "82%", "107%", "132%"),
    ]
    ty = y + 2.12
    rh = 0.235
    tbl = s.shapes.add_table(len(rows), 5, Inches(x), Inches(ty), Inches(w),
                             Inches(rh * len(rows))).table
    tbl.columns[0].width = Inches(1.65)
    for j in range(1, 5):
        tbl.columns[j].width = Inches((w - 1.65) / 4)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(rh)
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = Inches(0.06); c.margin_right = Inches(0.06)
            c.margin_top = Inches(0.0); c.margin_bottom = Inches(0.0)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            if i == 0:
                c.fill.fore_color.rgb = NAVY
            elif i >= 4:
                c.fill.fore_color.rgb = RGBColor(0xE6, 0xF2, 0xEC)
            else:
                c.fill.fore_color.rgb = WHITE if i % 2 else NAVY_T
            tf = c.text_frame; tf.word_wrap = False
            p = tf.paragraphs[0]
            col = WHITE if i == 0 else (GREEN if i >= 4 and j >= 2 else INK)
            bold = (i == 0) or (j == 0) or (i >= 4 and j >= 2)
            setp(p, val, 9.5, bold, col,
                 align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
    return box, tbl


CAPTION = ("World aviation CO2 along the ReFuelEU blending path, 2023 traffic "
           "held fixed: 838 Mt \u2192 704\u2013754 Mt at the 2035 mandate \u2192 "
           "369\u2013545 Mt at the 2050 mandate. Green line: the 2023 level minus "
           "the 356 Mt attributed to post-1996 connectivity growth (elasticity 5.67).")

if __name__ == "__main__":
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    bak = PPTX.replace(".pptx", f"_backup_{stamp}_preSAFpatch.pptx")
    shutil.copy2(PPTX, bak)
    print("backup:", bak)
    prs = Presentation(PPTX)
    target = None
    for idx, s in enumerate(prs.slides, 1):
        if any(sh.has_text_frame and "LIVE DEMO" in sh.text_frame.text
               for sh in s.shapes):
            target = (idx, s); break
    assert target, "SAF slide with LIVE DEMO box not found (already patched?)"
    idx, s = target
    print("patching slide", idx)
    # remove demo box, QR picture, URL text, old figure
    kill = []
    for sh in s.shapes:
        t = sh.text_frame.text if sh.has_text_frame else ""
        if "LIVE DEMO" in t or "claude.ai/code/artifact" in t:
            kill.append(sh)
        elif sh.shape_type == 13:   # pictures: the old figure and the QR
            kill.append(sh)
    for sh in kill:
        sh._element.getparent().remove(sh._element)
    print("removed", len(kill), "shapes")
    # new figure, same box as the old one (same 8.6x5.2 aspect)
    s.shapes.add_picture(FIG, Inches(0.55), Inches(1.90), Inches(6.28),
                         Inches(3.80))
    # caption text
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.startswith("ReFuelEU-style"):
            tf = sh.text_frame
            p = tf.paragraphs[0]
            for r in list(p.runs)[1:]:
                r._r.getparent().remove(r._r)
            p.runs[0].text = CAPTION
            sh.top = Inches(5.84); sh.left = Inches(0.55); sh.width = Inches(12.2)
    saf_right_panel(s)
    prs.save(PPTX)
    print("saved", PPTX)
