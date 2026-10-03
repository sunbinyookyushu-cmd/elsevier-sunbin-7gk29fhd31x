# -*- coding: utf-8 -*-
"""26_add_stage_and_charts_xlsx.py : add to Tables_for_paper_20260928.xlsx
   (1) Table 5b: incidence by development stage (compact: Gini, mean income, bottom-50 income, top-decile income,
       bottom-50 share, top-half minus bottom-half; columns = connectivity terciles and eras);
   (2) sheet Fig_data with the plotted numbers and NATIVE Excel scatter charts with 95% CI error bars:
       Figure A (full-sample curve: income and share), Figure B (by connectivity tercile), Figure C (by era);
   (3) sheet Fig_png with the matplotlib PNGs embedded (fig_gic, fig_gic_bysample, fig_gic_descriptive)."""
import os, numpy as np, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart.error_bar import ErrorBars
from openpyxl.chart.data_source import NumDataSource, NumRef
from openpyxl.chart.marker import Marker
from openpyxl.drawing.image import Image as XLImage
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
RD = dict(keep_default_na=False, na_values=["", "."])
bs = pd.read_csv("_gic_bysample_results.csv", **RD); gmax = pd.read_csv("_gic_dose_results.csv", **RD)
FN = "Times New Roman"
F_T = Font(name=FN, bold=True, size=11); F_H = Font(name=FN, bold=True, size=10); F_B = Font(name=FN, size=10); F_I = Font(name=FN, italic=True, size=10); F_N = Font(name=FN, size=9)
TOP = Side(style="medium"); THIN = Side(style="thin")
def st(p): return "" if pd.isna(p) else "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""
wb = load_workbook("Tables_for_paper_20260928.xlsx")
for n in ["Table5b_stage", "Fig_data", "Fig_png"]:
    if n in wb.sheetnames: wb.remove(wb[n])

# ---------------- Table 5b ----------------
ws = wb.create_sheet("Table5b_stage", wb.sheetnames.index("Table5_heterogeneity") + 1)
ws["A1"] = "Table 5b. Incidence by development stage: where the curve tilts"; ws["A1"].font = F_T
SAMP = [("full", "Full sample"), ("con_low", "Low"), ("con_mid", "Middle"), ("con_high", "High"), ("era_1996_2007", "1996–2007"), ("era_2010_2023x", "2010–2023 (excl. 2020–21)"), ("con_mid_era1", "Middle tercile, 1996–2007"),
        ("inc_low", "Low"), ("inc_mid", "Middle"), ("inc_high", "High")]
r = 3
ws.cell(row=r, column=1, value="").font = F_H; ws.cell(row=r, column=2, value="").font = F_H
ws.cell(row=r, column=3, value="Baseline-connectivity tercile").font = F_H; ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
ws.cell(row=r, column=6, value="Era").font = F_H; ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=7)
ws.cell(row=r, column=8, value="Take-off").font = F_H
ws.cell(row=r, column=9, value="Baseline GDP per capita tercile").font = F_H; ws.merge_cells(start_row=r, start_column=9, end_row=r, end_column=11)
for c in range(1, 12): ws.cell(row=r, column=c).alignment = Alignment(horizontal="center")
r += 1
ws.cell(row=r, column=1, value="Outcome (2SLS elasticity to ln GACI_max)").font = F_H
for j, (_, lab) in enumerate(SAMP, 2):
    x = ws.cell(row=r, column=j, value=lab); x.font = F_H; x.alignment = Alignment(horizontal="center", wrap_text=True)
for c in range(1, 12): ws.cell(row=r, column=c).border = Border(top=TOP, bottom=THIN)
ROWS = [("ln_gini_mkt", "ln Market Gini"), ("ln_gini_disp", "ln Disposable Gini"), ("ln_apt_all", "Mean income"), ("ln_apt_b50", "Average income, bottom 50%"), ("ln_apt_d10", "Average income, top 10%"),
        ("ln_spt_b50", "Income share, bottom 50%"), ("ln_spt_d10", "Income share, top 10%"), ("ln_apt_top_bot", "Top half minus bottom half")]
for o, lab in ROWS:
    r += 1; ws.cell(row=r, column=1, value=lab).font = F_B
    for j, (smp, _) in enumerate(SAMP, 2):
        x = bs[(bs["sample"] == smp) & (bs.outcome == o)]
        if len(x):
            ws.cell(row=r, column=j, value=f"{x.b.iloc[0]:.3f}{st(x.p.iloc[0])}").font = F_B; ws.cell(row=r, column=j).alignment = Alignment(horizontal="center")
            ws.cell(row=r + 1, column=j, value=f"({x.se.iloc[0]:.3f})").font = F_B; ws.cell(row=r + 1, column=j).alignment = Alignment(horizontal="center")
        else:
            ws.cell(row=r, column=j, value="--").font = F_B; ws.cell(row=r, column=j).alignment = Alignment(horizontal="center")
    r += 1
r += 1; ws.cell(row=r, column=1, value="First-stage KP F").font = F_B
for j, (smp, _) in enumerate(SAMP, 2):
    x = bs[(bs["sample"] == smp) & (bs.outcome == "ln_gini_mkt")]
    if len(x): c = ws.cell(row=r, column=j, value=float(x.kpf.iloc[0])); c.number_format = "0.0"; c.font = F_B; c.alignment = Alignment(horizontal="center")
r += 1; ws.cell(row=r, column=1, value="Observations").font = F_B
for j, (smp, _) in enumerate(SAMP, 2):
    x = bs[(bs["sample"] == smp) & (bs.outcome == "ln_gini_mkt")]
    if len(x): c = ws.cell(row=r, column=j, value=int(x.N.iloc[0])); c.number_format = "#,##0"; c.font = F_B; c.alignment = Alignment(horizontal="center")
r += 1; ws.cell(row=r, column=1, value="Countries").font = F_B
for j, (smp, _) in enumerate(SAMP, 2):
    x = bs[(bs["sample"] == smp) & (bs.outcome == "ln_gini_mkt")]
    if len(x): c = ws.cell(row=r, column=j, value=int(x.Nc.iloc[0])); c.number_format = "#,##0"; c.font = F_B; c.alignment = Alignment(horizontal="center")
for c in range(1, 12): ws.cell(row=r, column=c).border = Border(bottom=TOP)
r += 2
for n in ["Notes: Split-sample 2SLS with the Feyrer instrument, ln population, country and year fixed effects; standard errors clustered by country in parentheses. *** p<0.01, ** p<0.05, * p<0.1.",
          "Terciles are formed on each country's earliest observed value (GACI_max; GDP per capita). Shares use the identity ln share = ln group income − ln mean income. The high connectivity tercile and the low GDP tercile have no first stage (KP F < 1) and are shown for completeness only.",
          "Source: _gic_bysample_results.csv (24_gic_bysample.do)."]:
    ws.cell(row=r, column=1, value=n).font = F_N; r += 1
ws.column_dimensions["A"].width = 40
for j in range(2, 12): ws.column_dimensions[get_column_letter(j)].width = 15

# ---------------- Fig_data + native charts ----------------
ws = wb.create_sheet("Fig_data")
ws["A1"] = "Data behind the incidence figures (2SLS Feyrer, country-clustered). Charts on this sheet are native Excel charts and can be edited."; ws["A1"].font = F_N
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01"]
LAB = ["p0-10", "p10-20", "p20-30", "p30-40", "p40-50", "p50-60", "p60-70", "p70-80", "p80-90", "p90-100", "Top 1%", "Top 0.1%"]
def block(row0, title, cols):
    """cols: list of (header, series_b, series_se). Writes rank, label, then for each series b, lo, hi, half-width."""
    ws.cell(row=row0, column=1, value=title).font = F_H
    hdr = ["rank", "group"]
    for h, _, _ in cols: hdr += [h + " b", h + " ci95"]
    for j, h in enumerate(hdr, 1): ws.cell(row=row0 + 1, column=j, value=h).font = F_H
    for i in range(len(G)):
        ws.cell(row=row0 + 2 + i, column=1, value=i + 1); ws.cell(row=row0 + 2 + i, column=2, value=LAB[i])
        for k, (_, b, se) in enumerate(cols):
            v = None if np.isnan(b[i]) else float(b[i]); w = None if np.isnan(se[i]) else float(1.96 * se[i])
            ws.cell(row=row0 + 2 + i, column=3 + 2 * k, value=v).number_format = "0.000"
            ws.cell(row=row0 + 2 + i, column=4 + 2 * k, value=w).number_format = "0.000"
    return row0 + 2, row0 + 1 + len(G)
def pull(df, smp_col, smp, prefix):
    x = df[df[smp_col] == smp].set_index("outcome").reindex([prefix + g for g in G]) if smp_col else df.set_index("outcome").reindex([prefix + g for g in G])
    return x.b.values.astype(float), x.se.values.astype(float)
def chart(title, ytitle, rows, cols, anchor, series_spec, width=18, height=9):
    ch = ScatterChart(); ch.title = title; ch.style = 2; ch.height = height; ch.width = width
    ch.x_axis.title = "WID group (1 = p0-10 ... 10 = p90-100, 11 = top 1%, 12 = top 0.1%)"; ch.y_axis.title = ytitle
    ch.x_axis.scaling.min = 0.5; ch.x_axis.scaling.max = 12.5; ch.x_axis.majorUnit = 1
    ch.x_axis.delete = False; ch.y_axis.delete = False
    r0, r1 = rows
    xref = Reference(ws, min_col=1, min_row=r0, max_row=r1)
    for (label, bcol, color) in series_spec:
        yref = Reference(ws, min_col=bcol, min_row=r0, max_row=r1)
        s = Series(yref, xref, title=label)
        s.marker = Marker(symbol="circle", size=6); s.marker.graphicalProperties.solidFill = color; s.marker.graphicalProperties.line.solidFill = color
        s.graphicalProperties.line.noFill = True
        col_letter = get_column_letter(bcol + 1)
        ref = f"'Fig_data'!${col_letter}${r0}:${col_letter}${r1}"
        s.errBars = ErrorBars(errDir="y", errValType="cust", plus=NumDataSource(numRef=NumRef(f=ref)), minus=NumDataSource(numRef=NumRef(f=ref)), noEndCap=False)
        ch.series.append(s)
    ws.add_chart(ch, anchor)

# Figure A: full-sample income and share (Table 4)
bI, sI = pull(gmax[(gmax.block == "gic") & (gmax.spec == "IV")], None, None, "ln_apt_"); bS, sS = pull(gmax[(gmax.block == "gic_share") & (gmax.spec == "IV")], None, None, "ln_spt_")
bO, sO = pull(gmax[(gmax.block == "gic") & (gmax.spec == "OLS")], None, None, "ln_apt_")
rA = block(3, "A. Full sample: elasticity of group income and share (Table 4)", [("2SLS income", bI, sI), ("OLS income", bO, sO), ("2SLS share", bS, sS)])
chart("Figure A. Incidence of hub connectivity: group income (2SLS vs OLS)", "Elasticity to ln GACI_max", rA, 3, "K3", [("2SLS, Feyrer IV", 3, "1F5F8B"), ("OLS", 5, "4D4D4D")])
chart("Figure A'. Income share of the group (2SLS)", "Elasticity of share to ln GACI_max", rA, 3, "K23", [("2SLS, Feyrer IV", 7, "1F5F8B")])
# Figure B: by connectivity tercile
bL, sL = pull(bs, "sample", "con_low", "ln_apt_"); bM, sM = pull(bs, "sample", "con_mid", "ln_apt_")
rB = block(rA[1] + 3, "B. By baseline-connectivity tercile: group income", [("Low tercile", bL, sL), ("Middle tercile", bM, sM)])
chart("Figure B. By baseline connectivity: low tercile (flat) vs middle tercile (tilted)", "Elasticity of group income to ln GACI_max", rB, 3, "K43", [("Low tercile", 3, "4D4D4D"), ("Middle tercile", 5, "1F5F8B")])
# Figure C: by era
bE1, sE1 = pull(bs, "sample", "era_1996_2007", "ln_apt_"); bE2, sE2 = pull(bs, "sample", "era_2010_2023x", "ln_apt_")
rC = block(rB[1] + 3, "C. By era: group income", [("1996-2007", bE1, sE1), ("2010-2023 excl. 2020-21", bE2, sE2)])
chart("Figure C. By era: network expansion 1996-2007 vs mature network 2010-2023", "Elasticity of group income to ln GACI_max", rC, 3, "K63", [("1996-2007", 3, "1F5F8B"), ("2010-2023 (excl. 2020-21)", 5, "4D4D4D")])
# Figure D: by baseline income tercile
bIm, sIm = pull(bs, "sample", "inc_mid", "ln_apt_"); bIh, sIh = pull(bs, "sample", "inc_high", "ln_apt_")
rD = block(rC[1] + 3, "D. By baseline GDP per capita tercile: group income", [("Middle tercile", bIm, sIm), ("High tercile", bIh, sIh)])
chart("Figure D. By baseline GDP per capita: middle vs high tercile (low tercile unidentified)", "Elasticity of group income to ln GACI_max", rD, 3, "K83", [("Middle tercile", 3, "4D4D4D"), ("High tercile", 5, "1F5F8B")])
for j, w in enumerate([8, 12, 14, 12, 14, 12, 14, 12], 1): ws.column_dimensions[get_column_letter(j)].width = w

# ---------------- Fig_png ----------------
ws = wb.create_sheet("Fig_png")
ws["A1"] = "Matplotlib figures (project scripts 13, 25, 14). Vector versions: fig_gic.pdf, fig_gic_bysample.pdf, fig_gic_descriptive.pdf."; ws["A1"].font = F_N
row = 3
for f, cap in [("fig_gic.png", "Figure 1. Incidence of hub connectivity across the income distribution (13_fig_gic.py)"),
               ("fig_gic_bysample.png", "Figure 2. Incidence by development stage (25_fig_gic_bysample.py)"),
               ("fig_gic_descriptive.png", "Figure 3. Descriptive growth by group and connectivity-growth tercile (14_fig_gic_descriptive.py)")]:
    if not os.path.exists(f): continue
    ws.cell(row=row, column=1, value=cap).font = F_H
    img = XLImage(f); scale = 900 / img.width; img.width = 900; img.height = int(img.height * scale)
    ws.add_image(img, f"A{row + 1}"); row += int(img.height / 20) + 4
wb.save("Tables_for_paper_20260928.xlsx"); print("saved", wb.sheetnames)
