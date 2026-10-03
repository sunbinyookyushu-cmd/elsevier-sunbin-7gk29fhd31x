# -*- coding: utf-8 -*-
"""23_make_pub_tables_xlsx.py : publication table set for the inequality paper, journal layout
   (coefficient row with stars, SE row in parentheses below, panels, notes). Times New Roman.
   Main text: Tables 1-8. Appendix: A1-A7. Everything except Table 2 (OLS + 2SLS) is 2SLS with the Feyrer
   instrument, ln population, country + year FE, country-clustered SE. No tourism instrument anywhere.
   Output: Tables_for_paper_20260928.xlsx"""
import os, numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
RD = dict(keep_default_na=False, na_values=["", "."])
main = pd.read_csv("_main_results_cl.csv", **RD); tails = pd.read_csv("_tails_results_cl.csv", **RD)
rob = pd.read_csv("_robust_results_cl.csv", **RD); diag = pd.read_csv("_diag_results_cl.csv", **RD)
ld = pd.read_csv("_longdiff_results_cl.csv", **RD); gdp = pd.read_csv("_gdp_results_cl.csv", **RD)
sums = pd.read_csv("_sumstats.csv")
gmax = pd.read_csv("_gic_dose_results.csv", **RD); gcwm = pd.read_csv("_gic_cwm_results.csv", **RD)
stk = pd.read_csv("_gic_stacked_results.csv", **RD); grid = pd.read_csv("_gic_spec_grid.csv", **RD)
het = pd.read_csv("_hetero_co2form_results.csv", **RD); sp = pd.read_csv("_spill_results.csv", **RD)
agc = pd.read_csv("_aggregate_curve_bycontinent.csv", index_col=0); des = pd.read_csv("_gic_descriptive.csv", **RD)

FN = "Times New Roman"
F_T = Font(name=FN, bold=True, size=11); F_H = Font(name=FN, bold=True, size=10); F_B = Font(name=FN, size=10)
F_I = Font(name=FN, italic=True, size=10); F_N = Font(name=FN, size=9)
TOP = Side(style="medium"); THIN = Side(style="thin")
def st(p):
    if pd.isna(p): return ""
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""
def cs(b, p, d=3): return "--" if pd.isna(b) else f"{b:.{d}f}{st(p)}"
def ss(se, d=3): return "" if pd.isna(se) else f"({se:.{d}f})"

wb = Workbook(); wb.remove(wb.active)
class Tab:
    def __init__(self, name, title):
        self.ws = wb.create_sheet(name); self.r = 1
        self.put(1, title, F_T); self.r = 3
    def put(self, c, v, font=F_B, align="center", fmt=None):
        if isinstance(v, (np.integer,)): v = int(v)
        if isinstance(v, (np.floating,)): v = float(v)
        x = self.ws.cell(row=self.r, column=c, value=v); x.font = font; x.alignment = Alignment(horizontal=align, vertical="center", wrap_text=(c == 1))
        if fmt: x.number_format = fmt
        return x
    def header(self, cols, first=""):
        self.put(1, first, F_H, "left")
        for j, c in enumerate(cols, 2): self.put(j, c, F_H)
        for j in range(1, len(cols) + 2):
            self.ws.cell(row=self.r, column=j).border = Border(top=TOP, bottom=THIN)
        self.ncol = len(cols) + 1; self.r += 1
    def panel(self, label):
        self.put(1, label, F_I, "left"); self.r += 1
    def row2(self, label, cells, extra=None):
        """cells: list of (b, se, p) or None; writes coef row then se row. extra: dict col->value on coef row."""
        self.put(1, label, F_B, "left")
        for j, c in enumerate(cells, 2):
            if c is None: self.put(j, "--"); continue
            self.put(j, cs(c[0], c[2]))
        if extra:
            for j, v in extra.items(): self.put(j, v, F_B, "center", fmt="#,##0" if isinstance(v, int) else "0.0")
        self.r += 1
        for j, c in enumerate(cells, 2):
            if c is not None: self.put(j, ss(c[1]))
        self.r += 1
    def row1(self, label, vals, fmt=None):
        self.put(1, label, F_B, "left")
        for j, v in enumerate(vals, 2): self.put(j, v, F_B, "center", fmt=fmt if isinstance(v, (int, float, np.floating, np.integer)) else None)
        self.r += 1
    def close(self, notes, widths=None):
        for j in range(1, self.ncol + 1): self.ws.cell(row=self.r - 1, column=j).border = Border(bottom=TOP)
        self.r += 1
        for n in notes:
            self.put(1, n, F_N, "left"); self.r += 1
        w = widths or [46] + [16] * (self.ncol - 1)
        for j, v in enumerate(w, 1): self.ws.column_dimensions[get_column_letter(j)].width = v

def pick(df, **kw):
    x = df
    for k, v in kw.items(): x = x[x[k] == v]
    return None if len(x) == 0 else (x.b.iloc[0], x.se.iloc[0], x.p.iloc[0])
def kp(df, **kw):
    x = df
    for k, v in kw.items(): x = x[x[k] == v]
    return None if len(x) == 0 else (float(x.kpf.iloc[0]), int(x.N.iloc[0]))

G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01", "b50", "m40", "all"]
LAB = {"d1": "p0-10", "d2": "p10-20", "d3": "p20-30", "d4": "p30-40", "d5": "p40-50", "d6": "p50-60", "d7": "p60-70", "d8": "p70-80", "d9": "p80-90",
       "d10": "p90-100", "t1": "Top 1%", "t01": "Top 0.1%", "b50": "Bottom 50%", "m40": "Middle 40%", "all": "All adults (mean income)"}
NOTE_SPEC = "Country-year panel, 1996-2023. All regressions include country and year fixed effects and log population. 2SLS instruments ln GACI with the Feyrer interaction Z_ct = a_t x ln MA_c,1996 (a_t = world seat-capacity index, MA = population-weighted air market access in 1996). Standard errors clustered by country in parentheses. *** p<0.01, ** p<0.05, * p<0.1."

# ================= Table 1 summary statistics =================
t = Tab("Table1_sumstats", "Table 1. Summary statistics")
t.header(["N", "Mean", "SD", "Within SD", "Min", "Max"], "Variable")
for _, r in sums.iterrows():
    if "Tourism" in r.Variable: continue
    t.row1(r.Variable, [int(r.N), r.Mean, r.SD, r["Within SD"], r.Min, r.Max], fmt="0.000")
    t.ws.cell(row=t.r - 1, column=2).number_format = "#,##0"
t.close(["Notes: SWIID Gini indices in points (0-100); WID shares as fractions of pretax national income; GACI in index units. Within SD is the standard deviation after removing country means."])

# ================= Table 2 headline =================
t = Tab("Table2_headline", "Table 2. Hub connectivity and income inequality")
t.header(["ln Market Gini", "ln Disposable Gini", "First stage", "KP F", "N"], "")
m = main[main.iv == "feyrer_int"]
for tr, lab in [("ln_gaci_max", "Panel A. Hub connectivity, ln GACI_max (headline)"), ("ln_gaci_cwm", "Panel B. Hub quality, ln GACI_cwm (capacity-weighted mean)"), ("ln_gaci_sum", "Panel C. Total connectivity, ln GACI_sum")]:
    t.panel(lab); x = m[m.treat == tr]; fs = x[x.model == "FS"].iloc[0]
    t.row2("OLS", [pick(x, outcome="ln_gini_mkt", model="OLS"), pick(x, outcome="ln_gini_disp", model="OLS"), None], {6: int(x[x.model == "OLS"].N.iloc[0])})
    t.row2("2SLS, Feyrer instrument", [pick(x, outcome="ln_gini_mkt", model="IVcl"), pick(x, outcome="ln_gini_disp", model="IVcl"), (fs.b, fs.se, fs.p)], {5: float(fs.kpf), 6: int(x[x.model == "IVcl"].N.iloc[0])})
t.close(["Notes: " + NOTE_SPEC, "First stage reports the coefficient on Z in the regression of ln GACI on Z and log population; KP F is the Kleibergen-Paap rk Wald F statistic."])

# ================= Table 3 distribution (WID) =================
t = Tab("Table3_distribution", "Table 3. Which part of the distribution moves: WID income shares")
cols = [("ln_bot50_wid", "Bottom 50% share"), ("ln_top10_wid", "Top 10% share"), ("ln_top1_wid", "Top 1% share"), ("ratio_t10_b50", "Top 10% / Bottom 50%"), ("ln_gini_pre_wid", "Pretax Gini (WID)"), ("ln_gini_post_wid", "Post-tax Gini (WID)"), ("ln_bot50_post_wid", "Bottom 50% post-tax share")]
t.header([c for _, c in cols] + ["N"], "Outcome (logs)")
x = tails[(tails.block == "tails") & (tails.treat == "ln_gaci_max")]
t.row2("OLS", [pick(x, outcome=o, model="OLS") for o, _ in cols], {len(cols) + 2: int(x[x.model == "OLS"].N.iloc[0])})
t.row2("2SLS, Feyrer instrument", [pick(x, outcome=o, model="IVcl") for o, _ in cols], {len(cols) + 2: int(x[x.model == "IVcl"].N.iloc[0])})
t.row1("KP F (2SLS)", [round(float(x[x.model == "IVcl"].kpf.iloc[0]), 1)] + [""] * len(cols))
t.close(["Notes: " + NOTE_SPEC, "Outcomes are WID distributional national accounts series (pretax national income, equal-split adults; post-tax national income for the last two columns), in logs."], widths=[30] + [15] * 8)

# ================= Table 4 incidence curve (max) =================
def curve_table(name, title, df, treat_lab, gapblock="gic_gap", extra=None):
    t = Tab(name, title)
    t.header(["Average income of the group", "Income share of the group", "KP F", "N"], "WID group")
    t.panel("Panel A. Elasticity to " + treat_lab + " (2SLS)")
    for g in G:
        a = pick(df, block="gic", outcome="ln_apt_" + g, spec="IV"); s = pick(df, block="gic_share", outcome="ln_spt_" + g, spec="IV")
        if a is None: continue
        k = kp(df, block="gic", outcome="ln_apt_" + g, spec="IV")
        t.row2(LAB[g], [a, s], {4: k[0], 5: k[1]})
    t.panel("Panel B. Differences between groups")
    gp = df[(df.block == gapblock) & (df.spec == "IV")]
    if extra is not None: gp = pd.concat([gp, extra])
    for o, l in [("ln_apt_d10_b50", "p90-100 minus Bottom 50%"), ("ln_apt_d10_d1", "p90-100 minus p0-10"), ("ln_apt_t1_d10", "Top 1% minus p90-100"), ("ln_apt_top_bot", "Top half (p50-100) minus bottom half (p0-50)")]:
        c = pick(gp, outcome=o)
        if c is None: continue
        k = kp(gp, outcome=o); t.row2(l, [c, None], {4: k[0], 5: k[1]})
    t.close(["Notes: " + NOTE_SPEC, "Each cell is a separate regression. Income = ln average pretax national income of the group (WID aptinc, equal-split adults); share = ln income share, computed as ln group income minus ln mean income so that all groups use the same sample. Panel B regresses the difference of two group outcomes, which yields the exact difference of the two elasticities with its standard error."],
            widths=[46, 24, 24, 10, 10])
curve_table("Table4_incidence", "Table 4. Incidence of hub connectivity across the income distribution", gmax, "ln GACI_max", extra=gcwm[(gcwm.block == "gic_gap_max") & (gcwm.spec == "IV")])

# ================= Table 5 heterogeneity =================
HO = [("ln_gini_mkt", "ln Market Gini"), ("ln_gini_disp", "ln Disposable Gini"), ("ln_apt_top_bot", "Top half minus bottom half"), ("ln_spt_b50", "Bottom 50% share")]
def het_table(name, title, panels, note_extra=""):
    t = Tab(name, title)
    t.header([l for _, l in HO] + ["KP F", "N", "Countries"], "Sample")
    for pan, plab, items in panels:
        t.panel(plab)
        for key, lab in items:
            cells = [pick(het, panel=pan, group=key, outcome=o) for o, _ in HO]
            x = het[(het.panel == pan) & (het.group == key) & (het.outcome == "ln_gini_mkt")]
            ex = {}
            if len(x):
                ex = {len(HO) + 2: float(x.kpf.iloc[0]), len(HO) + 3: int(x.N.iloc[0])}
                if not pd.isna(x.Nc.iloc[0]): ex[len(HO) + 4] = int(x.Nc.iloc[0])
            t.row2(lab, cells, ex)
    t.close(["Notes: " + NOTE_SPEC, "Split-sample 2SLS. Terciles are formed on the earliest observed value per country. 'Interaction' rows report the coefficient on (top tercile x ln GACI) in a pooled regression where both ln GACI and the interaction are instrumented. KP F and N refer to the market-Gini column." + note_extra],
            widths=[44, 18, 18, 22, 18, 8, 8, 10])
het_table("Table5_heterogeneity", "Table 5. Heterogeneity by development stage and period", [
    ("A_income", "Panel A. Baseline income per capita tercile", [("inc_low", "Low"), ("inc_mid", "Middle"), ("inc_high", "High"), ("interact_top_x_gaci", "Interaction: top tercile x ln GACI")]),
    ("B_conn", "Panel B. Baseline connectivity tercile", [("con_low", "Low"), ("con_mid", "Middle"), ("con_high", "High"), ("interact_top_x_gaci", "Interaction: top tercile x ln GACI")]),
    ("D_time", "Panel C. Period", [("full", "Full sample, 1996-2023"), ("1996_2007", "Network-expansion era, 1996-2007"), ("2010_2023_ex2020_21", "Mature-network era, 2010-2023 (excl. 2020-21)"), ("excl_2020_2023", "Pre-pandemic, 1996-2019")])])

# ================= Table 6 robustness and inference =================
t = Tab("Table6_robustness", "Table 6. Robustness of the headline estimate and inference")
t.header(["ln Market Gini", "ln Disposable Gini", "KP F", "N"], "")
rb = rob[rob.block.isin(["sample", "loo_cont", "fe"])]
def rrow(label, block, spec):
    a = pick(rb, block=block, spec=spec, outcome="ln_gini_mkt"); b = pick(rb, block=block, spec=spec, outcome="ln_gini_disp")
    x = rb[(rb.block == block) & (rb.spec == spec) & (rb.outcome == "ln_gini_mkt")]
    t.row2(label, [a, b], {4: float(x.kpf.iloc[0]), 5: int(x.N.iloc[0])} if len(x) else None)
t.panel("Panel A. Baseline")
x = m[(m.treat == "ln_gaci_max")]
t.row2("2SLS, Feyrer instrument (Table 2, Panel A)", [pick(x, outcome="ln_gini_mkt", model="IVcl"), pick(x, outcome="ln_gini_disp", model="IVcl")], {4: float(x[x.model == "FS"].kpf.iloc[0]), 5: int(x[x.model == "IVcl"].N.iloc[0])})
t.panel("Panel B. Sample")
for spec, lab in [("drop_top10_hubs", "Excluding the ten largest hub countries"), ("pre2020", "1996-2019"), ("drop_crises", "Excluding crisis years (2008-09, 2020-21)")]: rrow(lab, "sample", spec)
for spec, lab in [("drop_AF", "Excluding Africa"), ("drop_AS", "Excluding Asia"), ("drop_EU", "Excluding Europe"), ("drop_LA", "Excluding Latin America"), ("drop_ME", "Excluding Middle East"), ("drop_NA", "Excluding North America"), ("drop_SW", "Excluding Oceania")]: rrow(lab, "loo_cont", spec)
t.panel("Panel C. Fixed effects")
rrow("Country and continent x year fixed effects", "fe", "cont_x_year"); rrow("Country-specific linear trends", "fe", "country_trends")
dg = diag[(diag.block == "pooled") & (diag.spec == "feyrer_int")]
for term, lab in [("subreg_x_year", "Country and UN sub-region x year fixed effects"), ("exposure_trends", "Baseline-exposure x linear trend control")]:
    a = pick(dg, term=term, outcome="ln_gini_mkt"); b = pick(dg, term=term, outcome="ln_gini_disp"); x = dg[(dg.term == term) & (dg.outcome == "ln_gini_mkt")]
    t.row2(lab, [a, b], {4: float(x.kpf.iloc[0]), 5: int(x.N.iloc[0])} if len(x) else None)
t.panel("Panel D. Inference (same point estimates as the baseline)")
base = grid[(grid.treat == "ln_gaci_max") & (grid.ctrl == "pop") & (grid.fe == "c+y")]
for se, lab in [("cluster_c", "Clustered by country"), ("twoway_cy", "Two-way clustered (country, year)"), ("conley_1000", "Conley spatial HAC, 1,000 km"), ("conley_2000", "Conley spatial HAC, 2,000 km")]:
    a = base[(base.se == se) & (base.outcome == "ln_gini_mkt")].iloc[0]; b = base[(base.se == se) & (base.outcome == "ln_gini_disp")].iloc[0]
    t.row2(lab, [(a.b, a.se_v, a.p), (b.b, b.se_v, b.p)], {4: float(a.F), 5: int(a.N)})
t.close(["Notes: " + NOTE_SPEC, "Panel D re-estimates the baseline with alternative variance estimators; Conley standard errors use a Bartlett kernel in great-circle distance between country centroids with the stated cutoff and allow arbitrary within-country serial correlation. Continent x year, sub-region x year and country-trend specifications have weak first stages (KP F below 4) and are reported for transparency."],
        widths=[52, 18, 18, 8, 8])

# ================= Table 7 spillovers =================
SO = [("ln_gini_mkt", "ln Market Gini"), ("ln_gini_disp", "ln Disposable Gini"), ("ln_apt_top_bot", "Top half minus bottom half")]
def spill_table(name, title, rows, note):
    t = Tab(name, title)
    t.header([l for _, l in SO] + ["KP F", "N"], "Specification / coefficient")
    for plab, items in rows:
        t.panel(plab)
        for pan, item, var, lab in items:
            cells = [pick(sp, panel=pan, item=item, var=var, outcome=o) for o, _ in SO]
            x = sp[(sp.panel == pan) & (sp["item"] == item) & (sp["var"] == var) & (sp.outcome == "ln_gini_mkt")]
            t.row2(lab, cells, {len(SO) + 2: float(x.kpf.iloc[0]), len(SO) + 3: int(x.N.iloc[0])} if len(x) else None)
    t.close(["Notes: " + NOTE_SPEC, note], widths=[60, 18, 18, 22, 8, 8])
spill_table("Table7_spillovers", "Table 7. Spillovers from neighbours' connectivity", [
    ("Panel A. Own and neighbour connectivity instrumented jointly", [
        ("A", "joint_contig", "ln_gaci_max", "Contiguous neighbours: own ln GACI"), ("A", "joint_contig", "nbr_g_contig", "   neighbours' ln GACI (leave-out mean)"),
        ("A", "joint_b1", "ln_gaci_max", "Neighbours within 500 km: own ln GACI"), ("A", "joint_b1", "nbr_g_b1", "   neighbours' ln GACI (leave-out mean)"),
        ("A", "joint_knn5", "ln_gaci_max", "Five nearest countries: own ln GACI"), ("A", "joint_knn5", "nbr_g_knn5", "   neighbours' ln GACI (leave-out mean)")]),
    ("Panel B. Neighbour exposure alone, own shifter controlled in reduced form", [
        ("A", "single_contig", "nbr_g_contig", "Contiguous neighbours"), ("A", "single_b1", "nbr_g_b1", "Within 500 km"),
        ("B", "kernel", "nbr_g_k500", "Kernel exp(-d/500 km)"), ("B", "kernel", "nbr_g_k1000", "Kernel exp(-d/1,000 km)"), ("B", "kernel", "nbr_g_k2000", "Kernel exp(-d/2,000 km)"),
        ("A", "single_inv", "nbr_g_inv", "Inverse distance, all countries")]),
    ("Panel C. Sub-region x year fixed effects", [
        ("C", "contig_joint_subregXyear", "ln_gaci_max", "Contiguous, joint 2SLS: own ln GACI"), ("C", "contig_joint_subregXyear", "nbr_g_contig", "   neighbours' ln GACI"),
        ("C", "contig_hybrid_subregXyear", "nbr_g_contig", "Contiguous, own shifter in reduced form: neighbours' ln GACI")])],
    "Neighbour exposure is the leave-out weighted mean of other countries' ln GACI (capacity-weighted mean) under the stated weights, instrumented by the identically weighted mean of their Feyrer shifters; flags for the presence of neighbours are included. Wide-radius exposures (inverse distance, kernels above 1,000 km) are close to continent-level trends and should be read with that in mind.")

# ================= Table 8 aggregate =================
t = Tab("Table8_aggregate", "Table 8. Implied incidence of observed connectivity growth, 1996 to latest year")
t.header(["Countries", "Mean change in ln GACI", "Bottom 50% income: implied %", "actual %", "p90-100 income: implied %", "actual %", "Bottom 50% share: implied pts", "actual pts", "Top 10% share: implied pts", "actual pts", "Market Gini: implied pts", "actual pts"], "Region")
NAME = {"AF": "Africa", "AS": "Asia-Pacific", "EU": "Europe", "LA": "Latin America", "ME": "Middle East", "NA": "North America", "SW": "Oceania"}
keys = ["n", "mean_dln_gaci", "implied_pct_inc_b50", "actual_pct_inc_b50", "implied_pct_inc_d10", "actual_pct_inc_d10", "implied_dshare_pts_b50", "actual_dshare_pts_b50", "implied_dshare_pts_d10", "actual_dshare_pts_d10", "implied_dgini_pts", "actual_dgini_pts"]
for idx, row in agc.iterrows():
    vals = [int(row["n"])] + [round(float(row[k]), 2) for k in keys[1:]]
    t.row1(NAME.get(idx, idx), vals, fmt="0.00"); t.ws.cell(row=t.r - 1, column=2).number_format = "#,##0"
t.close(["Notes: Implied = each country's change in ln GACI_max between its first and last year with complete data (>= 15 years apart; 138 countries) multiplied by the 2SLS elasticity of Table 4 (income, in percent) or converted to share points using the share elasticity and the initial share; Gini uses the Table 2 elasticity. Actual = observed change over the same window. Continent rows are unweighted country means; WORLD weights by latest population."],
        widths=[22, 10] + [14] * 11)

# ================= Appendix =================
curve_table("A1_incidence_cwm", "Table A1. Incidence across the income distribution, hub quality (ln GACI_cwm)", gcwm, "ln GACI_cwm")
het_table("A2_heterogeneity_regions", "Table A2. Heterogeneity by macro region and by baseline inequality", [
    ("E_region", "Panel A. Macro region", [("Europe", "Europe"), ("Asia", "Asia-Pacific"), ("Africa", "Africa"), ("LatAm", "Latin America"), ("MiddleEast", "Middle East"), ("excl_Europe", "Excluding Europe"), ("excl_LatAm", "Excluding Latin America")]),
    ("C_gini", "Panel B. Baseline market-Gini tercile", [("gini_low", "Low"), ("gini_mid", "Middle"), ("gini_high", "High"), ("interact_top_x_gaci", "Interaction: top tercile x ln GACI")])],
    " Regional first stages are weak outside Europe and Africa.")

t = Tab("A3_stacked_tests", "Table A3. Are the group elasticities different? Stacked-system tests")
t.header(["OLS", "2SLS, Feyrer", "2SLS, continent x year FE", "N"], "")
s2 = stk[stk.block != "stacked"]
for param, lab, is_test in [("eq_d1_d10", "Joint test: equal elasticity across the ten deciles (statistic; p)", True), ("d10_minus_d1", "p90-100 minus p0-10", False), ("top50_minus_bot50", "Top half minus bottom half", False), ("t1_minus_d10", "Top 1% minus p90-100", False), ("slope_per_decile", "Linear trend: change in elasticity per decile", False), ("level_at_median", "Linear trend: elasticity at the median decile", False)]:
    cells = []
    for spec in ["OLS", "IV", "IV_contyear"]:
        x = s2[(s2.param == param) & (s2.spec == spec)]
        if not len(x): cells.append(None); continue
        x = x.iloc[0]
        cells.append((x.b, x.se, x.p) if not is_test else (x.b, np.nan, np.nan))
    nn = s2[(s2.param == param) & (s2.spec == "IV")]
    if is_test:
        t.put(1, lab, F_B, "left")
        for j, spec in enumerate(["OLS", "IV", "IV_contyear"], 2):
            x = s2[(s2.param == param) & (s2.spec == spec)]
            if len(x): t.put(j, (f"F = {x.b.iloc[0]:.2f}; p = {x.p.iloc[0]:.3f}") if spec == "OLS" else f"p = {x.p.iloc[0]:.3f}")
        t.put(5, int(nn.N.iloc[0]), fmt="#,##0"); t.r += 1
    else:
        t.row2(lab, cells, {5: int(nn.N.iloc[0])} if len(nn) else None)
t.close(["Notes: All twelve WID groups stacked in one system (country x group x year) with group x ln GACI, group x log population, country x group and year x group fixed effects; each group's ln GACI is instrumented by group x Z. Standard errors clustered by country. The linear-trend rows replace the group interactions by ln GACI and ln GACI x (decile rank - 5.5) over the ten deciles. Per-equation KP F = 10.5 (Feyrer), 2.3 (continent x year); the cluster-robust rank statistic of the 12-endogenous system is degenerate and not reported."],
        widths=[58, 22, 22, 22, 8])

t = Tab("A4_descriptive_growth", "Table A4. Annualised growth of group income by tercile of connectivity growth (descriptive)")
t.header(["Low GACI-growth tercile", "Middle tercile", "High GACI-growth tercile", "High minus low (pp per year)", "s.e."], "WID group")
for _, r in des.iterrows():
    p = 2 * (1 - __import__("scipy").stats.norm.cdf(abs(r.diff_high_low / r.se_diff)))
    t.row1(r.label, [round(r.low_mean, 2), round(r.mid_mean, 2), round(r.high_mean, 2), f"{r.diff_high_low:.2f}{st(p)}", f"({r.se_diff:.2f})"], fmt="0.00")
t.close(["Notes: One observation per country: annualised log change of the group's average pretax income (WID, constant local prices) between the first and last year with complete data (>= 15 years apart; 138 countries). Terciles by annualised change in ln GACI_max (means -0.17, 0.58 and 1.44 percent per year). Two-sample standard errors across countries."],
        widths=[20, 20, 16, 22, 24, 10])

t = Tab("A5_lags", "Table A5. Lagged connectivity (2SLS, Feyrer instrument)")
t.header(["ln Market Gini", "ln Disposable Gini", "KP F", "N"], "Lag of ln GACI_max (years)")
lg = ld[ld.block == "lag"]
for k in range(0, 11):
    a = pick(lg, outcome="ln_gini_mkt", spec=f"k{k}"); b = pick(lg, outcome="ln_gini_disp", spec=f"k{k}"); x = lg[(lg.outcome == "ln_gini_mkt") & (lg.spec == f"k{k}")]
    t.row2(str(k), [a, b], {4: float(x.kpf.iloc[0]), 5: int(x.N.iloc[0])} if len(x) else None)
t.close(["Notes: " + NOTE_SPEC + " Each row instruments the k-year lag of ln GACI with the k-year lag of Z."], widths=[30, 18, 18, 8, 8])

t = Tab("A6_growth_levels", "Table A6. Connectivity, average incomes and GDP per capita (2SLS, Feyrer instrument)")
gm = gdp[(gdp.block == "main") & (gdp.iv == "feyrer_int") & (gdp.spec == "IVcl")]
outs = [("ln_gdppc", "ln GDP per capita"), ("ln_avg_all_wid", "ln mean income (WID)"), ("ln_avg_bot50_wid", "ln average income, bottom 50%"), ("ln_avg_top10_wid", "ln average income, top 10%"), ("ln_ratio_avg", "ln (top 10% / bottom 50%)")]
t.header([l for _, l in outs] + ["KP F", "N"], "Treatment (2SLS, Feyrer instrument)")
for tr, lab in [("ln_gaci_max", "ln GACI_max (hub connectivity)"), ("ln_gaci_cwm", "ln GACI_cwm (hub quality)"), ("ln_gaci_sum", "ln GACI_sum (total connectivity)")]:
    cells = [pick(gm, outcome=o, treat=tr) for o, _ in outs]
    x = gm[(gm.treat == tr) & (gm.outcome == "ln_gdppc")]
    t.row2(lab, cells, {len(outs) + 2: float(x.kpf.iloc[0]), len(outs) + 3: int(x.N.iloc[0])} if len(x) else None)
t.close(["Notes: " + NOTE_SPEC + " GDP per capita from the World Development Indicators (constant 2015 USD); average incomes from WID pretax national income per equal-split adult."], widths=[34, 18, 20, 24, 22, 22, 8, 8])

spill_table("A7_spillovers_full", "Table A7. Spillovers: full set of exposures", [
    ("Panel A. Own connectivity controlled", [("A", "own_exog_control", "nbr_g_inv", "Own ln GACI exogenous; neighbours (inverse distance)"), ("A", "own_exog_control", "ln_gaci_max", "   own ln GACI"),
        ("A", "hybrid_rf_control", "nbr_g_inv", "Own shifter in reduced form; neighbours (inverse distance)"), ("A", "hybrid_rf_control", "feyrer_int", "   own shifter")] +
        [("A", f"joint_{w}", v, l) for w in ["inv", "contig", "knn5", "b1", "k500", "k1000"] for v, l in [("ln_gaci_max", f"Joint 2SLS, {w}: own ln GACI"), (f"nbr_g_{w}", f"   neighbours' ln GACI")]] +
        [("A", f"single_{w}", f"nbr_g_{w}", f"Neighbours only (hybrid), {w}") for w in ["inv", "contig", "knn5", "b1", "k500", "k1000"]]),
    ("Panel B. Distance decay", [("B", "bands_joint", f"nbr_g_b{i}", f"Bands jointly: {l}") for i, l in zip(range(1, 6), ["<500 km", "500-1,000 km", "1,000-2,000 km", "2,000-5,000 km", ">5,000 km"])] +
        [("B", "band_single", v, f"Band alone: {l}") for v, l in [("nbr_g_contig", "contiguous"), ("nbr_g_b1", "<500 km"), ("nbr_g_b2", "500-1,000 km"), ("nbr_g_b3", "1,000-2,000 km"), ("nbr_g_b4", "2,000-5,000 km"), ("nbr_g_b5", ">5,000 km")]] +
        [("B", "kernel", f"nbr_g_k{l}", f"Kernel exp(-d/{l} km)") for l in [250, 500, 1000, 2000, 5000]]),
    ("Panel C. Regional", [("C", "subregion_inout", "nbr_g_inreg", "Within UN sub-region"), ("C", "subregion_inout", "nbr_g_outreg", "   outside sub-region"), ("C", "bloc_inout", "nbr_g_inbloc", "Within aviation bloc"), ("C", "bloc_inout", "nbr_g_outbloc", "   outside bloc"),
        ("C", "contig_joint_subregXyear", "ln_gaci_max", "Contiguous, joint, sub-region x year FE: own"), ("C", "contig_joint_subregXyear", "nbr_g_contig", "   neighbours"), ("C", "contig_hybrid_subregXyear", "nbr_g_contig", "Contiguous, hybrid, sub-region x year FE: neighbours")])],
    "Exposures as in Table 7; the joint distance-band specification is unidentified (KP F = 0) and is shown only for completeness.")

# ================= Contents =================
ws = wb.create_sheet("Contents", 0)
rows = [("Main text", F_H), ("Table 1  Summary statistics", F_B), ("Table 2  Hub connectivity and income inequality (headline; OLS and 2SLS)", F_B), ("Table 3  Which part of the distribution moves: WID income shares", F_B),
        ("Table 4  Incidence of hub connectivity across the income distribution (GACI_max)", F_B), ("Table 5  Heterogeneity by development stage and period", F_B), ("Table 6  Robustness of the headline estimate and inference", F_B),
        ("Table 7  Spillovers from neighbours' connectivity", F_B), ("Table 8  Implied incidence of observed connectivity growth", F_B), ("", F_B), ("Appendix", F_H),
        ("A1  Incidence curve with hub quality (GACI_cwm)", F_B), ("A2  Heterogeneity by macro region and baseline inequality", F_B), ("A3  Stacked-system tests of equal elasticities", F_B), ("A4  Descriptive growth by group and connectivity-growth tercile", F_B),
        ("A5  Lagged connectivity", F_B), ("A6  Average incomes and GDP per capita", F_B), ("A7  Spillovers: full set of exposures", F_B), ("", F_B),
        ("All estimates: 2SLS with the Feyrer instrument, log population, country and year fixed effects, standard errors clustered by country (Table 2 also reports OLS). The tourism-heritage instrument and the leads panel are not used. Built 2026-09-28 by 23_make_pub_tables_xlsx.py from the *_cl.csv and GIC result files.", F_N)]
for i, (v, f) in enumerate(rows, 1):
    x = ws.cell(row=i, column=1, value=v); x.font = f
ws.column_dimensions["A"].width = 120
out = "Tables_for_paper_20260928.xlsx"; wb.save(out); print("saved", out, wb.sheetnames)
