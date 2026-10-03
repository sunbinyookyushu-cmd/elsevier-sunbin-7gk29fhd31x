# -*- coding: utf-8 -*-
"""44_make_final_xlsx.py : keep only the tables that go into the paper, renumber, rebuild Contents.
   Input: Tables_for_paper_20260928.xlsx (working file, untouched). Output: Tables_for_paper_FINAL_20260928.xlsx"""
import os, re
from openpyxl import load_workbook
from openpyxl.styles import Font
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
wb = load_workbook("Tables_for_paper_20260928.xlsx")
# (old sheet name, new sheet name, new title prefix)
MAIN = [("Table1_sumstats", "T1_sumstats", "Table 1."), ("Table2_headline", "T2_headline", "Table 2."), ("Table4_incidence", "T3_incidence", "Table 3."),
        ("Table5c_growth_ineq", "T4_growth_ineq_by_hub", "Table 4."), ("Table9_regression", "T5_mechanism", "Table 5."), ("Table6_robustness", "T6_robustness", "Table 6."),
        ("Table10_robust_measures", "T7_measures", "Table 7.")]
APP = [("Table5b_stage", "A1_incidence_by_stage", "Table A1."), ("A3_stacked_tests", "A2_stacked_tests", "Table A2."), ("A5_lags", "A3_lags", "Table A3."),
       ("Table8_aggregate", "A4_aggregate", "Table A4."), ("A2_heterogeneity_regions", "A5_regions_baseline_gini", "Table A5."), ("A8_stage_definitions", "A6_stage_definitions", "Table A6."),
       ("A7_spillovers_full", "A7_spillovers", "Table A7."), ("A10_hub_components", "A8_hub_components", "Table A8."), ("A12_macro_channels", "A9_mediators", "Table A9.")]
FIGS = [("Fig_data", "Fig_data"), ("Fig_png", "Fig_png")]
keep = {o for o, _, _ in MAIN + APP} | {o for o, _ in FIGS}
for n in list(wb.sheetnames):
    if n not in keep: wb.remove(wb[n])
def retitle(ws, prefix):
    v = ws["A1"].value or ""
    v = re.sub(r"^Table\s+[A-Z]?\d+[a-z]?\.\s*", "", v); ws["A1"] = f"{prefix} {v}"
order = []
for o, n, p in MAIN + APP:
    ws = wb[o]; ws.title = n; retitle(ws, p); order.append(n)
for o, n in FIGS: order.append(n)
from openpyxl.drawing.image import Image as XLImage
wm = wb.create_sheet("Maps"); wm["A1"] = "World maps (45_maps_incidence.py; shared GACI map style). Implied changes use the 2SLS elasticities of Table 2 and Table 3 applied to each country's change in ln GACI_max, 1996 to latest year (>= 15 years of data, 138 countries)."; wm["A1"].font = Font(name="Times New Roman", size=9)
row = 3
for f, cap in [("fig_map_hub_growth.png", "Map 1. Change in ln hub connectivity (GACI_max), 1996-2023"), ("fig_map_induced_gini_2sls.png", "Map 2. Implied change in the market Gini (points), 2SLS elasticity 0.495"),
               ("fig_map_induced_b50share.png", "Map 3. Implied change in the bottom-50% income share (points of national income), 2SLS share elasticity -0.774"), ("fig_map_implied_gini.png", "Map 2b. Implied change in the market Gini (points), OLS elasticity 0.061 (conservative)")]:
    if not os.path.exists(f): continue
    wm.cell(row=row, column=1, value=cap).font = Font(name="Times New Roman", bold=True, size=10)
    img = XLImage(f); sc = 1000 / img.width; img.width = 1000; img.height = int(img.height * sc); wm.add_image(img, f"A{row + 1}"); row += int(img.height / 20) + 4
order.append("Maps")
# reorder
wb._sheets = [wb[n] for n in order]
# contents
ws = wb.create_sheet("Contents", 0)
FN = "Times New Roman"; H = Font(name=FN, bold=True, size=11); B = Font(name=FN, size=10); N = Font(name=FN, size=9, italic=True)
lines = [("Growth for Whom? Hub connectivity and within-country inequality. Final table set, 2026-09-28.", H), ("", B), ("Main text", H)]
desc = {"A1_incidence_by_stage": "Incidence by development stage (connectivity terciles, eras, GDP terciles)", "A2_stacked_tests": "Stacked-system tests of equal group elasticities", "A3_lags": "Lagged connectivity",
        "A4_aggregate": "Implied incidence of observed connectivity growth (with the maps)", "A5_regions_baseline_gini": "Heterogeneity by macro region and baseline inequality", "A6_stage_definitions": "Development-stage split under alternative definitions",
        "A7_spillovers": "Spillovers from neighbours' connectivity", "A8_hub_components": "Components of hub connectivity", "A9_mediators": "Mediation: macro channels (trade composition, spatial concentration, factor shares); other mediators available on request",
        "T1_sumstats": "Summary statistics", "T2_headline": "Hub connectivity and income inequality (OLS and 2SLS; hub, hub quality, total connectivity)",
        "T3_incidence": "Incidence across the income distribution: group incomes and shares, and contrasts (2SLS)", "T4_growth_ineq_by_hub": "Growth and inequality by baseline hub size (median split, terciles, quartiles)",
        "T5_mechanism": "Mechanism: which connectivity, who gains, not a growth effect, where, not offset", "T6_robustness": "Robustness of the headline estimate: sample, fixed effects, inference",
        "T7_measures": "Robustness to the connectivity measure and to the inequality measure",
        "A1_incidence_cwm": "Incidence curve with hub quality (GACI_cwm)", "A2_incidence_by_stage": "Incidence by development stage (connectivity terciles, eras, GDP terciles)", "A3_stacked_tests": "Stacked-system tests of equal group elasticities",
        "A4_descriptive_growth": "Descriptive growth by group and connectivity-growth tercile", "A5_lags": "Lagged connectivity", "A6_growth_levels": "GDP per capita and average incomes", "A7_aggregate": "Implied incidence of observed connectivity growth",
        "A8_regions_baseline_gini": "Heterogeneity by macro region and baseline inequality", "A9_stage_definitions": "Development-stage split under alternative definitions", "A10_median_splits": "Split samples by country characteristics",
        "A11_spillovers": "Spillovers from neighbours' connectivity (full set)", "A12_hub_components": "Components of hub connectivity", "A13_wage_premia": "Wage premia (ILOSTAT): not identified",
        "A14_macro_channels": "Macro channels: spatial concentration, export composition, factor shares", "A15_mediators_employment": "Employment composition, informality, migration and transfers as mediators",
        "A16_alt_measures": "Alternative inequality and poverty measures", "A17_mechanism_full": "Mechanism, full set of specifications"}
for o, n, p in MAIN: lines.append((f"{p:<10s} {n:<28s} {desc[n]}", B))
lines += [("", B), ("Appendix", H)]
for o, n, p in APP: lines.append((f"{p:<10s} {n:<28s} {desc[n]}", B))
lines += [("", B), ("Figures", H), ("Fig_data      native Excel charts with 95% CI (full curve; by connectivity tercile; by era; by GDP tercile)", B), ("Fig_png       matplotlib figures: fig_gic, fig_gic_bysample, fig_gic_descriptive (vector PDFs in the folder)", B), ("Maps          hub growth; implied change in market Gini (2SLS and OLS); implied change in bottom-50 share", B), ("", B),
          ("All estimates: 2SLS with the Feyrer instrument, ln population, country and year fixed effects, standard errors clustered by country (Table 2 and Table 7 also report OLS). No tourism instrument, no leads panel, no behavioural controls in the baseline.", N),
          ("Cross-references inside table notes use the working-file numbering: Table 9A/C/D/E = T5 panels; Table 5b = A1; A3 = A2; A5 = A3; Table 8 = A4; A2 = A5; A8 = A6; A7 = A7; A10 = A8; A12 = A9; A9, A11, A13, A14, Table 3, Table 9 (full) are in the working file only (Tables_for_paper_20260928.xlsx).", N),
          ("Kept out of the final set (available in the working file): WID-shares table, cwm incidence curve, descriptive growth table (figure only), GDP levels, median splits by characteristics, wage premia, employment-composition mediators, alternative measures beyond T7, full mechanism table, one-page summary.", N)]
for i, (v, f) in enumerate(lines, 1): ws.cell(row=i, column=1, value=v).font = f
ws.column_dimensions["A"].width = 130
wb.save("Tables_for_paper_FINAL_20260928.xlsx"); print("saved", wb.sheetnames)
