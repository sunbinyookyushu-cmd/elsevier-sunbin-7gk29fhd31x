# -*- coding: utf-8 -*-
"""49_tex_tables.py : LaTeX table fragments for the v3 draft, in the trade-paper format (booktabs, threeparttable,
   coefficient row with \\sym stars and s.e. row). Output: draft_v3_20260928/tables/*.tex (each a full table environment)."""
import os, numpy as np, pandas as pd
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
OUT = os.path.join(D, "draft_v3_20260928", "tables"); os.makedirs(OUT, exist_ok=True)
RD = dict(keep_default_na=False, na_values=["", "."])
def st(p):
    if pd.isna(p): return ""
    return "\\sym{***}" if p < .01 else "\\sym{**}" if p < .05 else "\\sym{*}" if p < .1 else ""
def cs(b, p, d=3): return "--" if pd.isna(b) else f"{b:.{d}f}{st(p)}"
def ss(se, d=3): return "" if pd.isna(se) else f"({se:.{d}f})"
def n(x): return f"{int(x):,}".replace(",", "{,}")
def esc(s): return str(s).replace("%", "\\%").replace("&", "\\&")
def g(df, **kw):
    x = df
    for k, v in kw.items(): x = x[x[k] == v]
    return x.iloc[0] if len(x) else None
WIDE = {"tab_mech_A", "tab_mech_B", "tab_mech_D", "tab_mech_E", "tab_a_stage", "tab_a_aggregate", "tab_a_stagedefs", "tab_a_spill", "tab_a_components", "tab_a_mediators"}
WIDE.add("tab_a_stagedefs2")
TALL = {"tab_growth_ineq", "tab_a_stagedefs", "tab_a_stagedefs2", "tab_a_spill", "tab_a_components"}
def table(name, caption, label, colspec, header_rows, body_rows, notes, size="\\small"):
    """Wide tables are scaled to the text width with \\resizebox (graphicx); tall tables float on their own page."""
    place = "p" if name in TALL else "H"; wide = name in WIDE
    L = [f"\\begin{{table}}[{place}]", "\\centering", f"\\caption{{{caption}}}", f"\\label{{{label}}}"]
    if wide:  # scale the tabular to the text width; notes in a text-width minipage (threeparttable would measure the unscaled tabular)
        L += ["\\begin{minipage}{\\linewidth}", "\\centering", "\\resizebox{\\linewidth}{!}{%", f"\\begin{{tabular}}{{{colspec}}}", "\\toprule"]
        L += header_rows + ["\\midrule"] + body_rows + ["\\bottomrule", "\\end{tabular}}", "\\par\\vspace{3pt}\\begin{flushleft}\\footnotesize " + notes + "\\end{flushleft}", "\\end{minipage}", "\\end{table}"]
    else:
        L += ["\\begin{threeparttable}", size, f"\\begin{{tabular}}{{{colspec}}}", "\\toprule"]
        L += header_rows + ["\\midrule"] + body_rows + ["\\bottomrule", "\\end{tabular}", "\\begin{tablenotes}\\small", "\\item " + notes, "\\end{tablenotes}", "\\end{threeparttable}", "\\end{table}"]
    open(os.path.join(OUT, name + ".tex"), "w", encoding="utf-8").write("\n".join(L) + "\n")
def coef_rows(label, cells, d=3):
    """cells: list of (b,se,p) or None -> two tabular rows."""
    r1 = label + " & " + " & ".join(cs(c.b, c.p, d) if c is not None else "" for c in cells) + " \\\\"
    r2 = " & " + " & ".join(ss(c.se, d) if c is not None else "" for c in cells) + " \\\\"
    return [r1, r2]
NOTE_BASE = "Country-year panel, 1996--2023. All regressions include country and year fixed effects and log population. 2SLS instruments ln GACI with the Feyrer interaction $Z_{ct}=a_t\\times\\ln \\mathrm{MA}^{air}_{c,1996}$. Standard errors clustered by country in parentheses. \\sym{*}~$p<0.10$, \\sym{**}~$p<0.05$, \\sym{***}~$p<0.01$."

# ================= T1 summary statistics =================
s = pd.read_csv("_sumstats.csv"); s = s[~s.Variable.str.contains("Tourism")]
rows = [f"{esc(r.Variable)} & {n(r.N)} & {r.Mean:.3f} & {r.SD:.3f} & {r['Within SD']:.3f} & {r.Min:.3f} & {r.Max:.3f} \\\\" for _, r in s.iterrows()]
table("tab_sumstat", "Summary statistics, estimation sample (166 economies, 1996--2023).", "tab:sumstat", "lrrrrrr",
      ["Variable & N & Mean & SD & Within SD & Min & Max \\\\"], rows,
      "Within SD is the standard deviation after removing country means. SWIID Gini coefficients in points (0--100); WID income shares as fractions of pretax national income (equal-split adults); GACI in index units; the Feyrer instrument is $a_t\\times\\ln\\mathrm{MA}^{air}_{c,1996}$.")

# ================= T2 headline =================
m = pd.read_csv("_main_results_cl.csv", **RD); m = m[m.iv == "feyrer_int"]
rows = []
for tr, lab in [("ln_gaci_max", "Panel A. Hub connectivity, $\\ln\\mathrm{GACI}_{max}$ (headline)"), ("ln_gaci_cwm", "Panel B. Hub quality, $\\ln\\mathrm{GACI}_{cwm}$"), ("ln_gaci_sum", "Panel C. Total connectivity, $\\ln\\mathrm{GACI}_{sum}$")]:
    x = m[m.treat == tr]; fs = g(x, model="FS")
    rows.append(f"\\multicolumn{{3}}{{l}}{{\\emph{{{lab}}}}}\\\\")
    rows.append(f"First stage: instrument coef. & \\multicolumn{{2}}{{l}}{{{cs(fs.b, fs.p)}\\ \\ {ss(fs.se)},\\ \\ KP $F={fs.kpf:.1f}$}} \\\\")
    rows += coef_rows("OLS", [g(x, outcome="ln_gini_mkt", model="OLS"), g(x, outcome="ln_gini_disp", model="OLS")])
    rows += coef_rows("2SLS", [g(x, outcome="ln_gini_mkt", model="IVcl"), g(x, outcome="ln_gini_disp", model="IVcl")])
    rows.append("\\addlinespace")
N0 = int(g(m, treat="ln_gaci_max", outcome="ln_gini_mkt", model="IVcl").N)
rows += ["\\midrule", "Country, Year FE & Yes & Yes \\\\", f"Observations & {n(N0)} & {n(N0)} \\\\"]
table("tab_main", "Main results: OLS, first stage, and 2SLS, by connectivity measure.", "tab:main", "lcc",
      [" & Market-income Gini & Disposable-income Gini \\\\", " & $\\ln G^{mkt}$ & $\\ln G^{disp}$ \\\\"], rows,
      "Each panel instruments its connectivity measure with the Feyrer interaction. The first-stage row regresses the connectivity measure on the instrument with log population and two-way fixed effects; KP $F$ is the Kleibergen--Paap $rk$ Wald statistic with country-clustered errors. " + NOTE_BASE)

# ================= T3 incidence =================
gic = pd.read_csv("_gic_dose_results.csv", **RD); gcwm = pd.read_csv("_gic_cwm_results.csv", **RD)
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01", "b50", "m40", "all"]
LAB = {"d1": "p0--10", "d2": "p10--20", "d3": "p20--30", "d4": "p30--40", "d5": "p40--50", "d6": "p50--60", "d7": "p60--70", "d8": "p70--80", "d9": "p80--90", "d10": "p90--100", "t1": "Top 1\\%", "t01": "Top 0.1\\%", "b50": "Bottom 50\\%", "m40": "Middle 40\\%", "all": "All adults (mean income)"}
rows = ["\\multicolumn{5}{l}{\\emph{Panel A. Elasticity to $\\ln\\mathrm{GACI}_{max}$, 2SLS}}\\\\"]
for k in G:
    a = g(gic, block="gic", outcome="ln_apt_" + k, spec="IV"); sh = g(gic, block="gic_share", outcome="ln_spt_" + k, spec="IV")
    if a is None: continue
    rows.append(f"{LAB[k]} & {cs(a.b, a.p)} & {ss(a.se)} & {cs(sh.b, sh.p) if sh is not None else '--'} & {ss(sh.se) if sh is not None else ''} \\\\")
rows += ["\\addlinespace", "\\multicolumn{5}{l}{\\emph{Panel B. Differences between groups (difference outcomes)}}\\\\"]
gp = pd.concat([gic[(gic.block == "gic_gap") & (gic.spec == "IV")], gcwm[(gcwm.block == "gic_gap_max") & (gcwm.spec == "IV")]])
for o, l in [("ln_apt_d10_b50", "p90--100 minus bottom 50\\%"), ("ln_apt_top_bot", "Top half (p50--100) minus bottom half (p0--50)"), ("ln_apt_d10_d1", "p90--100 minus p0--10"), ("ln_apt_t1_d10", "Top 1\\% minus p90--100")]:
    x = g(gp, outcome=o)
    if x is not None: rows.append(f"{l} & {cs(x.b, x.p)} & {ss(x.se)} & & \\\\")
kp = g(gic, block="gic", outcome="ln_apt_d10", spec="IV")
rows += ["\\midrule", f"First-stage KP $F$ & \\multicolumn{{2}}{{c}}{{{kp.kpf:.1f}}} & \\multicolumn{{2}}{{c}}{{{kp.kpf:.1f}}} \\\\", f"Observations & \\multicolumn{{2}}{{c}}{{{n(kp.N)}}} & \\multicolumn{{2}}{{c}}{{{n(kp.N)}}} \\\\"]
table("tab_incidence", "Incidence of hub connectivity across the income distribution (2SLS, Feyrer instrument).", "tab:incidence", "lcccc",
      [" & \\multicolumn{2}{c}{Average income of the group} & \\multicolumn{2}{c}{Income share of the group} \\\\", "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}", "WID group & Coef. & (s.e.) & Coef. & (s.e.) \\\\"], rows,
      "Each cell is a separate regression. Income is the log average pretax national income of the group (WID, equal-split adults); the share is the log income share, computed as log group income minus log mean income so that all groups use the same sample. Panel B regresses the difference of two group outcomes, which gives the exact difference of the two elasticities with its standard error. " + NOTE_BASE)

# ================= T4 growth and inequality by hub size =================
d4 = pd.read_csv("_median_gdp_results.csv", **RD)
O4 = [("ln_gdppc", "ln GDP p.c."), ("ln_apt_all", "ln mean income"), ("ln_gini_mkt", "ln market Gini"), ("ln_gini_disp", "ln disp. Gini")]
rows = []
for plab, items in [("Panel A. Median split", [("med_below", "Below median (smaller hubs)"), ("med_above", "Above median (larger hubs)")]), ("Panel B. Terciles", [("ter_low", "Low"), ("ter_mid", "Middle"), ("ter_high", "High")]), ("Reference", [("full", "Full sample")])]:
    rows.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{plab}}}}}\\\\")
    for key, lab in items:
        iv = [g(d4, group=key, outcome=o, model="IV") for o, _ in O4]; x = g(d4, group=key, outcome="ln_gini_mkt", model="IV")
        rows.append(f"{lab}: 2SLS & " + " & ".join(cs(c.b, c.p) for c in iv) + f" & {x.kpf:.1f} \\\\")
        rows.append(" & " + " & ".join(ss(c.se) for c in iv) + f" & N = {n(x.N)} \\\\")
        ol = [g(d4, group=key, outcome=o, model="OLS") for o, _ in O4]
        rows.append("\\quad OLS & " + " & ".join(cs(c.b, c.p) for c in ol) + " & \\\\")
        rows.append(" & " + " & ".join(ss(c.se) for c in ol) + " & \\\\")
    rows.append("\\addlinespace")
table("tab_growth_ineq", "Growth and inequality by baseline hub size (countries grouped on $\\mathrm{GACI}_{max}$ in 1996).", "tab:growth_ineq", "lcccccc",
      [" & " + " & ".join(l for _, l in O4) + " & KP $F$ / N \\\\"], rows,
      "Countries are grouped on their earliest observed $\\mathrm{GACI}_{max}$ (1996 for most). GDP per capita from the World Development Indicators (constant 2015 US dollars); mean income is WID pretax national income per equal-split adult. " + NOTE_BASE, size="\\footnotesize")

# ================= T5 mechanism (5 panels) =================
mech = pd.read_csv("_mech_results.csv", **RD); comp = pd.read_csv("_components_results.csv", **RD); alt = pd.read_csv("_alt_measures_results.csv")
med = pd.read_csv("_median_splits_results.csv", **RD); stg = pd.read_csv("_gic_bysample_results.csv", **RD); sp = pd.read_csv("_spill_results.csv", **RD)
class R: pass
def mk(row): r = R(); r.b, r.se, r.p, r.kpf, r.N = row.iv_b, row.iv_se, row.iv_p, row.kpf, row.N; return r
# Panel A
A = {"base": g(mech, block="A", item="baseline", outcome="ln_gini_mkt", term="ln_gaci_max"), "hs_max": g(mech, block="A", item="hub_ctrl_sum", outcome="ln_gini_mkt", term="ln_gaci_max"), "hs_sum": g(mech, block="A", item="hub_ctrl_sum", outcome="ln_gini_mkt", term="ln_gaci_sum"),
     "hr_max": g(mech, block="A", item="hub_ctrl_rest", outcome="ln_gini_mkt", term="ln_gaci_max"), "hr_rest": g(mech, block="A", item="hub_ctrl_rest", outcome="ln_gini_mkt", term="ln_gaci_rest"),
     "eig": g(comp, block="C", item="topo_iv_cap_ctrl_eig", outcome="ln_gini_mkt", term="ln_hub_eig"), "eig_cap": g(comp, block="C", item="topo_iv_cap_ctrl_eig", outcome="ln_gini_mkt", term="ln_hub_cap"),
     "cap": g(comp, block="C", item="cap_iv_topo_ctrl_betw", outcome="ln_gini_mkt", term="ln_hub_cap"), "cap_betw": g(comp, block="C", item="cap_iv_topo_ctrl_betw", outcome="ln_gini_mkt", term="ln_hub_betw"),
     "hhi": g(mech, block="A", item="ols_hhi", outcome="ln_gini_mkt", term="ln_hhi")}
rowsA = ["\\multicolumn{7}{l}{\\emph{Panel A. Which connectivity? Dependent variable: ln market Gini}}\\\\", " & (1) & (2) & (3) & (4) & (5) & (6) \\\\", " & Baseline & Hub + network & Hub + secondary & Core integration & Capacity + transit & Concentration (OLS) \\\\", "\\midrule"]
rowsA += coef_rows("$\\ln\\mathrm{GACI}_{max}$ (hub), instrumented", [A["base"], A["hs_max"], A["hr_max"], None, None, None])
rowsA += coef_rows("$\\ln\\mathrm{GACI}_{sum}$ (whole network), control", [None, A["hs_sum"], None, None, None, None])
rowsA += coef_rows("ln GACI of secondary airports, control", [None, None, A["hr_rest"], None, None, None])
rowsA += coef_rows("ln hub eigenvector centrality, instrumented", [None, None, None, A["eig"], None, None])
rowsA += coef_rows("ln hub seat capacity", [None, None, None, A["eig_cap"], A["cap"], None])
rowsA += coef_rows("ln hub flow betweenness, control", [None, None, None, None, A["cap_betw"], None])
rowsA += coef_rows("ln Herfindahl of airport shares (with $\\ln\\mathrm{GACI}_{sum}$)", [None, None, None, None, None, A["hhi"]])
rowsA.append("KP $F$ & " + " & ".join(f"{A[k].kpf:.1f}" if A[k] is not None and not pd.isna(A[k].kpf) else "" for k in ["base", "hs_max", "hr_max", "eig", "cap", "hhi"]) + " \\\\")
rowsA.append("Observations & " + " & ".join(n(A[k].N) for k in ["base", "hs_max", "hr_max", "eig", "cap", "hhi"]) + " \\\\")
table("tab_mech_A", "Mechanism (I): which connectivity carries the effect?", "tab:mech_A", "lcccccc", [], rowsA,
      "Column (4) instruments the hub's eigenvector centrality and controls for its seat capacity; column (5) instruments seat capacity and controls for flow betweenness; column (6) is OLS. " + NOTE_BASE)
# Panel B
B = [g(gic, block="gic", outcome="ln_apt_all", spec="IV"), g(gic, block="gic", outcome="ln_apt_d7", spec="IV"), g(gic, block="gic", outcome="ln_apt_d10", spec="IV"), g(gic, block="gic", outcome="ln_apt_b50", spec="IV"), g(gic, block="gic_share", outcome="ln_spt_b50", spec="IV"), mk(alt[alt.outcome == "ln_p50_p10"].iloc[0]), mk(alt[alt.outcome == "ln_p90_p50"].iloc[0])]
rowsB = [" & Mean income & p60--70 & p90--100 & Bottom-50 income & Bottom-50 share & p50/p10 & p90/p50 \\\\", "\\midrule"] + coef_rows("$\\ln\\mathrm{GACI}_{max}$, instrumented", B)
rowsB.append("KP $F$ & " + " & ".join(f"{c.kpf:.1f}" for c in B) + " \\\\"); rowsB.append("Observations & " + " & ".join(n(c.N) for c in B) + " \\\\")
table("tab_mech_B", "Mechanism (II): who gains? Group incomes and ratios (2SLS).", "tab:mech_B", "lccccccc", [], rowsB,
      "Outcomes in logs: average pretax income of the group, its income share (identity-based), and ratios of decile mean incomes. " + NOTE_BASE)
# Panel C
C_cp = g(mech, block="C", item="ln_gdppc", outcome="ln_gini_mkt", term="ln_gaci_max"); C_b = g(mech, block="C", item="ln_gdppc", outcome="ln_gini_mkt", term="ln_gdppc"); C_a = g(mech, block="B", item="apath", outcome="ln_gdppc")
rowsC = [" & ln market Gini \\\\", "\\midrule"] + coef_rows("$\\ln\\mathrm{GACI}_{max}$, instrumented (direct effect $c'$)", [C_cp]) + coef_rows("ln GDP per capita, control ($b$)", [C_b]) + coef_rows("Memo: hub $\\rightarrow$ ln GDP per capita, 2SLS ($a$)", [C_a])
rowsC += [f"KP $F$ & {C_cp.kpf:.1f} \\\\", f"Observations & {n(C_cp.N)} \\\\"]
table("tab_mech_C", "Mechanism (III): not a growth effect.", "tab:mech_C", "lc", [], rowsC,
      "GDP per capita is itself an outcome of connectivity ($a$-path), so it is not a valid control in the baseline; holding it fixed isolates the distributional effect from the growth effect. Other candidate mediators are reported in Appendix Table~\\ref{tab:a_mediators}. " + NOTE_BASE)
# Panel D
Dd = [g(med, var="urban", group="above", outcome="ln_gini_mkt"), g(med, var="urban", group="below", outcome="ln_gini_mkt"), g(mech, block="E", item="tour_rcpt_exp_1", outcome="ln_gini_mkt"), g(stg, sample="con_low", outcome="ln_gini_mkt"), g(stg, sample="con_mid", outcome="ln_gini_mkt"), g(med, var="trade_gdp", group="above", outcome="ln_gini_mkt"), g(sp, panel="A", item="joint_contig", var="ln_gaci_max", outcome="ln_gini_mkt")]
nb = g(sp, panel="A", item="joint_contig", var="nbr_g_contig", outcome="ln_gini_mkt")
rowsD = [" & Urban. above & Urban. below & Non-tourism & Thin networks & Take-off hubs & Open economies & Own + neighbours \\\\", "\\midrule"] + coef_rows("$\\ln\\mathrm{GACI}_{max}$, instrumented", Dd) + coef_rows("Neighbours' ln GACI (contiguity), instrumented", [None] * 6 + [nb])
rowsD.append("KP $F$ & " + " & ".join(f"{c.kpf:.1f}" for c in Dd) + " \\\\"); rowsD.append("Observations & " + " & ".join(n(c.N) for c in Dd) + " \\\\")
table("tab_mech_D", "Mechanism (IV): where is the effect found? Split samples and neighbours (ln market Gini).", "tab:mech_D", "lccccccc", [], rowsD,
      "Splits at the median of the earliest observed value (urbanisation, trade to GDP, tourism receipts as a share of exports) or at terciles of $\\mathrm{GACI}_{max}$ in 1996 (thin networks: lowest tercile; take-off hubs: middle tercile). The last column instruments own connectivity with the own shifter and the leave-out mean of contiguous neighbours' ln GACI with their shifters. " + NOTE_BASE)
# Panel E
E = [g(mech, block="A", item="baseline", outcome="ln_gini_disp", term="ln_gaci_max"), g(mech, block="D", item="redistribution", outcome="wedge_pts"), g(mech, block="D", item="redistribution", outcome="ln_wedge_ratio"), g(mech, block="D", item="redistribution", outcome="tax_gdp")]
rowsE = [" & ln disposable Gini & Market $-$ disposable Gini (points) & ln(market/disposable Gini) & Tax revenue, \\% GDP \\\\", "\\midrule"] + coef_rows("$\\ln\\mathrm{GACI}_{max}$, instrumented", E)
rowsE.append("KP $F$ & " + " & ".join(f"{c.kpf:.1f}" for c in E) + " \\\\"); rowsE.append("Observations & " + " & ".join(n(c.N) for c in E) + " \\\\")
table("tab_mech_E", "Mechanism (V): is the effect offset by redistribution?", "tab:mech_E", "lcccc", [], rowsE,
      "The wedge is the redistribution achieved by taxes and transfers; a negative coefficient means less redistribution. " + NOTE_BASE)

# ================= T6 robustness =================
rob = pd.read_csv("_robust_results_cl.csv", **RD); diag = pd.read_csv("_diag_results_cl.csv", **RD); grid = pd.read_csv("_gic_spec_grid.csv", **RD)
rows = ["\\multicolumn{5}{l}{\\emph{Panel A. Baseline}}\\\\"]
x = m[m.treat == "ln_gaci_max"]; b0 = g(x, outcome="ln_gini_mkt", model="IVcl"); d0 = g(x, outcome="ln_gini_disp", model="IVcl")
rows += coef_rows("2SLS, Feyrer instrument (Table~\\ref{tab:main})", [b0, d0]); rows[-2] = rows[-2].replace(" \\\\", f" & {g(x, model='FS').kpf:.1f} & {n(b0.N)} \\\\")
rows.append("\\multicolumn{5}{l}{\\emph{Panel B. Sample}}\\\\")
def rr(label, block, spec):
    a = g(rob, block=block, spec=spec, outcome="ln_gini_mkt"); b = g(rob, block=block, spec=spec, outcome="ln_gini_disp"); out = coef_rows(label, [a, b])
    out[0] = out[0].replace(" \\\\", f" & {a.kpf:.1f} & {n(a.N)} \\\\"); return out
for spec, lab in [("drop_top10_hubs", "Excluding the ten largest hub economies"), ("pre2020", "1996--2019"), ("drop_crises", "Excluding 2008--09 and 2020--21")]: rows += rr(lab, "sample", spec)

rows.append(r"\multicolumn{5}{l}{\emph{Panel C. Exposure trends}}\\")

dg = diag[(diag.block == "pooled") & (diag.spec == "feyrer_int")]
for term, lab in [("exposure_trends", "Baseline exposures $\\times$ aviation index")]:
    a = g(dg, term=term, outcome="ln_gini_mkt"); b = g(dg, term=term, outcome="ln_gini_disp"); out = coef_rows(lab, [a, b]); out[0] = out[0].replace(" \\\\", f" & {a.kpf:.1f} & {n(a.N)} \\\\"); rows += out
rows.append("\\multicolumn{5}{l}{\\emph{Panel D. Inference (same point estimates as the baseline)}}\\\\")
base = grid[(grid.treat == "ln_gaci_max") & (grid.ctrl == "pop") & (grid.fe == "c+y")]
for se, lab in [("cluster_c", "Clustered by country"), ("twoway_cy", "Two-way clustered (country, year)"), ("conley_1000", "Conley spatial HAC, 1{,}000 km"), ("conley_2000", "Conley spatial HAC, 2{,}000 km")]:
    a = g(base, se=se, outcome="ln_gini_mkt"); b = g(base, se=se, outcome="ln_gini_disp")
    ra = R(); ra.b, ra.se, ra.p = a.b, a.se_v, a.p; rb = R(); rb.b, rb.se, rb.p = b.b, b.se_v, b.p
    out = coef_rows(lab, [ra, rb]); out[0] = out[0].replace(" \\\\", f" & {a.F:.1f} & {n(a.N)} \\\\"); rows += out
table("tab_robust", "Robustness of the headline estimate: sample, fixed effects and inference (2SLS, Feyrer instrument).", "tab:robust", "lcccc",
      [" & ln market Gini & ln disposable Gini & KP $F$ & N \\\\"], rows,
      "Panel D re-estimates the baseline with alternative variance estimators; Conley standard errors use a Bartlett kernel in great-circle distance between country centroids with the stated cutoff and allow arbitrary within-country serial correlation. Baseline exposures are ln GDP per capita, the market Gini, ln land area, absolute latitude and ln sea market access in the base year, each interacted with the aviation index. " + NOTE_BASE)

# ================= T7 measures =================
rm = pd.read_csv("_robust_measures_results.csv", **RD)
O7 = [("ln_gini_mkt", "SWIID market Gini"), ("ln_gini_disp", "SWIID disp. Gini"), ("ln_gini_pre_wid", "WID Gini"), ("ln_palma", "Palma ratio"), ("ln_p90_p10", "p90/p10"), ("ln_abs_gap", "Absolute gap")]
rows = []
for tr, lab in [("ln_gaci_max", "Panel A. Hub connectivity, $\\ln\\mathrm{GACI}_{max}$"), ("ln_gaci_cwm", "Panel B. Hub quality, $\\ln\\mathrm{GACI}_{cwm}$"), ("ln_gaci_sum", "Panel C. Total connectivity, $\\ln\\mathrm{GACI}_{sum}$")]:
    rows.append(f"\\multicolumn{{7}}{{l}}{{\\emph{{{lab}}}}}\\\\")
    for model, ml in [("OLS", "OLS"), ("IV", "2SLS")]:
        rows += coef_rows(ml, [g(rm, treat=tr, outcome=o, model=model) for o, _ in O7])
    rows.append("KP $F$ (2SLS) & " + " & ".join(f"{g(rm, treat=tr, outcome=o, model='IV').kpf:.1f}" for o, _ in O7) + " \\\\")
    rows.append("Observations & " + " & ".join(n(g(rm, treat=tr, outcome=o, model='IV').N) for o, _ in O7) + " \\\\"); rows.append("\\addlinespace")
table("tab_measures", "Robustness to the connectivity measure and to the inequality measure.", "tab:measures", "lcccccc",
      [" & " + " & ".join(l for _, l in O7) + " \\\\"], rows,
      "Outcomes in logs. SWIID Gini indices are household-equivalised survey-based series \\citep{Solt_2020}. WID measures are computed from the pretax national income shares of ten deciles (equal-split adults): the WID Gini is the DINA Gini; Palma $=$ top-10 share / bottom-40 share; p90/p10 is the ratio of top- to bottom-decile mean income; the absolute gap is the top-10 minus bottom-50 average income in constant local prices. " + NOTE_BASE)

# ================= Appendix tables =================
# A1 incidence by stage
SAMP = [("full", "Full sample"), ("con_low", "Low"), ("con_mid", "Middle"), ("con_high", "High"), ("era_1996_2007", "1996--2007"), ("era_2010_2023x", "2010--23 ex. 2020--21"), ("inc_low", "Low"), ("inc_mid", "Middle"), ("inc_high", "High")]
ROWS = [("ln_gini_mkt", "ln market Gini"), ("ln_apt_all", "Mean income"), ("ln_apt_b50", "Income, bottom 50\\%"), ("ln_apt_d10", "Income, top 10\\%"), ("ln_spt_b50", "Share, bottom 50\\%"), ("ln_spt_d10", "Share, top 10\\%"), ("ln_apt_top_bot", "Top half minus bottom half")]
rows = []
for o, lab in ROWS: rows += coef_rows(lab, [g(stg, sample=s_, outcome=o) for s_, _ in SAMP])
rows.append("KP $F$ & " + " & ".join(f"{g(stg, sample=s_, outcome='ln_gini_mkt').kpf:.1f}" for s_, _ in SAMP) + " \\\\")
rows.append("Observations & " + " & ".join(n(g(stg, sample=s_, outcome='ln_gini_mkt').N) for s_, _ in SAMP) + " \\\\")
table("tab_a_stage", "Incidence by development stage: connectivity terciles, eras and GDP terciles (2SLS elasticities to $\\ln\\mathrm{GACI}_{max}$).", "tab:a_stage", "lccccccccc",
      [" & & \\multicolumn{3}{c}{Baseline connectivity tercile} & \\multicolumn{2}{c}{Era} & \\multicolumn{3}{c}{Baseline GDP p.c. tercile} \\\\", "\\cmidrule(lr){3-5}\\cmidrule(lr){6-7}\\cmidrule(lr){8-10}", " & " + " & ".join(l for _, l in SAMP) + " \\\\"], rows,
      "Terciles on each country's earliest observed value. The high connectivity tercile and the low GDP tercile have no first stage (KP $F<1$) and are shown for completeness. " + NOTE_BASE, size="\\footnotesize")
# A2 stacked tests
stk = pd.read_csv("_gic_stacked_results.csv", **RD); s2 = stk[stk.block != "stacked"]
rows = []
for param, lab, is_test in [("eq_d1_d10", "Joint test: equal elasticity across the ten deciles ($p$)", True), ("d10_minus_d1", "p90--100 minus p0--10", False), ("top50_minus_bot50", "Top half minus bottom half", False), ("t1_minus_d10", "Top 1\\% minus p90--100", False), ("slope_per_decile", "Linear trend: change in elasticity per decile", False), ("level_at_median", "Linear trend: elasticity at the median decile", False)]:
    cells = [g(s2, param=param, spec=sp_) for sp_ in ["OLS", "IV"]]
    if is_test: rows.append(f"{lab} & " + " & ".join(f"{c.p:.3f}" if c is not None else "" for c in cells) + " \\\\")
    else: rows += coef_rows(lab, cells)
table("tab_a_stacked", "Stacked-system tests of equal group elasticities.", "tab:a_stacked", "lcc", [" & OLS & 2SLS, Feyrer \\\\"], rows,
      "All twelve WID groups stacked in one system (country $\\times$ group $\\times$ year) with group $\\times$ ln GACI, group $\\times$ log population, country $\\times$ group and year $\\times$ group fixed effects; each group's ln GACI is instrumented by group $\\times$ $Z$. The linear-trend rows replace the group interactions by ln GACI and ln GACI $\\times$ (decile rank $-5.5$) over the ten deciles. Per-equation KP $F$ = 10.5. Standard errors clustered by country.")
# A3 lags
ld = pd.read_csv("_longdiff_results_cl.csv", **RD); lg = ld[ld.block == "lag"]
rows = []
for k in range(0, 11):
    a = g(lg, outcome="ln_gini_mkt", spec=f"k{k}"); b = g(lg, outcome="ln_gini_disp", spec=f"k{k}"); out = coef_rows(str(k), [a, b]); out[0] = out[0].replace(" \\\\", f" & {a.kpf:.1f} & {n(a.N)} \\\\"); rows += out
table("tab_a_lags", "Lagged connectivity (2SLS, Feyrer instrument).", "tab:a_lags", "lcccc", ["Lag of $\\ln\\mathrm{GACI}_{max}$ (years) & ln market Gini & ln disposable Gini & KP $F$ & N \\\\"], rows,
      "Each row instruments the $k$-year lag of ln GACI with the $k$-year lag of $Z$. " + NOTE_BASE)
# A4 aggregate
agc = pd.read_csv("_aggregate_curve_bycontinent.csv", index_col=0, keep_default_na=False)
NAME = {"AF": "Africa", "AS": "Asia-Pacific", "EU": "Europe", "LA": "Latin America", "ME": "Middle East", "NA": "North America", "SW": "Oceania", "ALL (unweighted)": "All (unweighted)", "WORLD (pop-weighted)": "World (population-weighted)"}
rows = [f"{NAME.get(i, i)} & {int(r['n'])} & {r['mean_dln_gaci']:.2f} & {r['implied_pct_inc_b50']:.1f} & {r['actual_pct_inc_b50']:.1f} & {r['implied_pct_inc_d10']:.1f} & {r['actual_pct_inc_d10']:.1f} & {r['implied_dshare_pts_b50']:.2f} & {r['actual_dshare_pts_b50']:.2f} & {r['implied_dgini_pts']:.2f} & {r['actual_dgini_pts']:.2f} \\\\" for i, r in agc.iterrows()]
table("tab_a_aggregate", "Implied incidence of observed hub-connectivity growth, 1996 to latest year.", "tab:a_aggregate", "lrrrrrrrrrr",
      [" & & & \\multicolumn{2}{c}{Bottom-50 income, \\%} & \\multicolumn{2}{c}{Top-10 income, \\%} & \\multicolumn{2}{c}{Bottom-50 share, pts} & \\multicolumn{2}{c}{Market Gini, pts} \\\\", "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}\\cmidrule(lr){8-9}\\cmidrule(lr){10-11}", "Region & N & $\\Delta\\ln\\mathrm{GACI}$ & Implied & Actual & Implied & Actual & Implied & Actual & Implied & Actual \\\\"], rows,
      "Implied $=$ each country's change in $\\ln\\mathrm{GACI}_{max}$ between its first and last year with complete data ($\\geq 15$ years apart; 138 countries) multiplied by the 2SLS elasticity of Table~\\ref{tab:incidence} (income, in percent) or converted to share points using the share elasticity and the initial share; the Gini uses the elasticity of Table~\\ref{tab:main}. Actual $=$ observed change over the same window. Continent rows are unweighted country means.", size="\\footnotesize")
# A5 regions and baseline Gini
het = pd.read_csv("_hetero_co2form_results.csv", **RD)
HO = [("ln_gini_mkt", "ln market Gini"), ("ln_gini_disp", "ln disp. Gini"), ("ln_apt_top_bot", "Top half minus bottom half"), ("ln_spt_b50", "Bottom-50 share")]
rows = []
for pan, plab, items in [("E_region", "Panel A. Macro region", [("Europe", "Europe"), ("Asia", "Asia-Pacific"), ("Africa", "Africa"), ("LatAm", "Latin America"), ("MiddleEast", "Middle East")]), ("C_gini", "Panel B. Baseline market-Gini tercile", [("gini_low", "Low"), ("gini_mid", "Middle"), ("gini_high", "High")])]:
    rows.append(f"\\multicolumn{{7}}{{l}}{{\\emph{{{plab}}}}}\\\\")
    for key, lab in items:
        cells = [g(het, panel=pan, group=key, outcome=o) for o, _ in HO]; x = g(het, panel=pan, group=key, outcome="ln_gini_mkt")
        out = coef_rows(lab, cells); out[0] = out[0].replace(" \\\\", f" & {x.kpf:.1f} & {n(x.N)} \\\\"); rows += out
table("tab_a_regions", "Heterogeneity by macro region and by baseline inequality (2SLS on subsamples).", "tab:a_regions", "lcccccc", [" & " + " & ".join(l for _, l in HO) + " & KP $F$ & N \\\\"], rows,
      "Split-sample 2SLS. Regional first stages are weak outside Europe and Africa. " + NOTE_BASE, size="\\footnotesize")
# A6 stage definitions
sd = pd.read_csv("_stage_defs_results.csv", **RD)
DEFS = [("g_max96_t3", "$\\mathrm{GACI}_{max}$ in 1996, terciles (baseline)", {"1_low": "Low", "2_mid": "Middle", "3_high": "High"}), ("g_max96_q4", "$\\mathrm{GACI}_{max}$ in 1996, quartiles", {"1_q1": "Q1", "2_q2": "Q2", "3_q3": "Q3", "4_q4": "Q4"}), ("g_max96_med", "$\\mathrm{GACI}_{max}$ in 1996, median split", {"1_below": "Below", "2_above": "Above"}),
        ("g_max9600_t3", "$\\mathrm{GACI}_{max}$, mean 1996--2000, terciles", {"1_low": "Low", "2_mid": "Middle", "3_high": "High"}), ("g_maxall_t3", "$\\mathrm{GACI}_{max}$, full-period mean, terciles", {"1_low": "Low", "2_mid": "Middle", "3_high": "High"}), ("g_cwm96_t3", "$\\mathrm{GACI}_{cwm}$ in 1996, terciles", {"1_low": "Low", "2_mid": "Middle", "3_high": "High"}),
        ("g_sum96_t3", "$\\mathrm{GACI}_{sum}$ in 1996, terciles", {"1_low": "Low", "2_mid": "Middle", "3_high": "High"}), ("g_share96_t3", "Top-airport share of national GACI, 1996, terciles", {"1_low": "Low", "2_mid": "Middle", "3_high": "High"}), ("g_max96_wcont", "$\\mathrm{GACI}_{max}$ in 1996, terciles within continent", {"1_low": "Low", "2_mid": "Middle", "3_high": "High"})]
SO6 = [("ln_gini_mkt", "ln market Gini"), ("ln_apt_all", "Mean income"), ("ln_apt_top_bot", "Top half minus bottom half"), ("ln_spt_b50", "Bottom-50 share"), ("ln_spt_d10", "Top-10 share")]
for part, (nm, lb, cap, defs) in enumerate([("tab_a_stagedefs", "tab:a_stagedefs", "Development-stage split under alternative definitions of baseline hub size, $\\mathrm{GACI}_{max}$ (2SLS elasticities to $\\ln\\mathrm{GACI}_{max}$).", DEFS[:5]),
                                            ("tab_a_stagedefs2", "tab:a_stagedefs2", "Development-stage split under alternative baseline connectivity measures (2SLS elasticities to $\\ln\\mathrm{GACI}_{max}$).", DEFS[5:])]):
    rows = []
    for dv, lab, groups in defs:
        rows.append(f"\\multicolumn{{8}}{{l}}{{\\emph{{{lab}}}}}\\\\")
        for gk, gl in groups.items():
            cells = [g(sd, defn=dv, group=gk, outcome=o) for o, _ in SO6]; x = g(sd, defn=dv, group=gk, outcome="ln_gini_mkt")
            if x is None: continue
            out = coef_rows("\\quad " + gl, cells); out[0] = out[0].replace(" \\\\", f" & {x.kpf:.1f} & {n(x.N)} \\\\"); rows += out
    table(nm, cap, lb, "lccccccc", [" & " + " & ".join(l for _, l in SO6) + " & KP $F$ & N \\\\"], rows,
          "Groups are formed over countries on the stated baseline variable. The instrument has power only in groups with small-to-moderate baseline hubs; wherever it has power the distributional pattern is the same. " + NOTE_BASE, size="\\footnotesize")
# A7 spillovers (selected full set)
SO7 = [("ln_gini_mkt", "ln market Gini"), ("ln_gini_disp", "ln disp. Gini"), ("ln_apt_top_bot", "Top half minus bottom half")]
ITEMS = [("Panel A. Own connectivity controlled", [("A", "own_exog_control", "nbr_g_inv", "Own ln GACI exogenous; neighbours (inverse distance)"), ("A", "hybrid_rf_control", "nbr_g_inv", "Own shifter in reduced form; neighbours (inverse distance)"),
          ("A", "joint_contig", "ln_gaci_max", "Joint 2SLS, contiguity: own ln GACI"), ("A", "joint_contig", "nbr_g_contig", "\\quad neighbours' ln GACI"), ("A", "joint_b1", "ln_gaci_max", "Joint 2SLS, within 500 km: own ln GACI"), ("A", "joint_b1", "nbr_g_b1", "\\quad neighbours' ln GACI"), ("A", "joint_knn5", "ln_gaci_max", "Joint 2SLS, five nearest: own ln GACI"), ("A", "joint_knn5", "nbr_g_knn5", "\\quad neighbours' ln GACI"),
          ("A", "single_contig", "nbr_g_contig", "Neighbours only (hybrid), contiguity"), ("A", "single_b1", "nbr_g_b1", "Neighbours only (hybrid), within 500 km")]),
         ("Panel B. Distance decay (own shifter in reduced form)", [("B", "band_single", "nbr_g_b2", "500--1{,}000 km"), ("B", "band_single", "nbr_g_b3", "1{,}000--2{,}000 km"), ("B", "band_single", "nbr_g_b4", "2{,}000--5{,}000 km"), ("B", "kernel", "nbr_g_k500", "Kernel $\\exp(-d/500\\,\\mathrm{km})$"), ("B", "kernel", "nbr_g_k1000", "Kernel $\\exp(-d/1{,}000\\,\\mathrm{km})$"), ("B", "kernel", "nbr_g_k2000", "Kernel $\\exp(-d/2{,}000\\,\\mathrm{km})$")])]
rows = []
for plab, items in ITEMS:
    rows.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{plab}}}}}\\\\")
    for pan, item, var, lab in items:
        cells = [g(sp, panel=pan, item=item, var=var, outcome=o) for o, _ in SO7]; x = g(sp, panel=pan, item=item, var=var, outcome="ln_gini_mkt")
        if x is None: continue
        out = coef_rows(lab, cells); out[0] = out[0].replace(" \\\\", f" & {x.kpf:.1f} & {n(x.N)} \\\\"); rows += out
table("tab_a_spill", "Spillovers from neighbours' connectivity.", "tab:a_spill", "lccccc", [" & " + " & ".join(l for _, l in SO7) + " & KP $F$ & N \\\\"], rows,
      "Neighbour exposure is the leave-out weighted mean of other countries' ln GACI (capacity-weighted mean) under the stated weights, instrumented by the identically weighted mean of their Feyrer shifters; presence flags for neighbours are included. Wide-radius exposures average over most of a country's continent and are therefore less informative about neighbour-specific spillovers than the contiguity and 500 km definitions." + NOTE_BASE, size="\\footnotesize")
# A8 components
COMP = [("gaci", "GACI (composite)"), ("cap", "Seat capacity"), ("deg", "Number of connections"), ("eig", "Eigenvector centrality"), ("close", "Closeness"), ("betw", "Flow betweenness"), ("regimp", "Regional importance")]
O8 = [("ln_gini_mkt", "ln market Gini"), ("ln_gini_disp", "ln disp. Gini"), ("ln_spt_b50", "Bottom-50 share"), ("ln_apt_top_bot", "Top half minus bottom half")]
rows = ["\\multicolumn{8}{l}{\\emph{Panel A. One hub component at a time, instrumented}}\\\\"]
for k, lab in COMP:
    cells = [g(comp, block="B", item="iv_single", outcome=o, term="ln_hub_" + k) for o, _ in O8]; fs = g(comp, block="A", outcome="ln_hub_" + k); x = cells[0]
    out = coef_rows(lab, cells + [fs]); out[0] = out[0].replace(" \\\\", f" & {x.kpf:.1f} & {n(x.N)} \\\\"); rows += out
rows.append("\\multicolumn{8}{l}{\\emph{Panel B. Horse races on ln market Gini (component instrumented, another as control)}}\\\\")
for item, lab in [("topo_iv_cap_ctrl_eig", "Eigenvector (IV) with seat capacity"), ("cap_iv_topo_ctrl_betw", "Seat capacity (IV) with betweenness"), ("cap_iv_topo_ctrl_close", "Seat capacity (IV) with closeness"), ("cap_iv_topo_ctrl_deg", "Seat capacity (IV) with degree"), ("topo_iv_cap_ctrl_deg", "Degree (IV) with seat capacity"), ("topo_iv_cap_ctrl_betw", "Betweenness (IV) with seat capacity")]:
    x = comp[(comp.block == "C") & (comp["item"] == item) & (comp.outcome == "ln_gini_mkt")]
    if not len(x): continue
    a, b = x.iloc[0], x.iloc[1]
    rows.append(f"{lab} & {cs(a.b, a.p)} {ss(a.se)} & {cs(b.b, b.p)} {ss(b.se)} & \\multicolumn{{3}}{{l}}{{instrumented / control}} & {a.kpf:.1f} & {n(a.N)} \\\\")
table("tab_a_components", "Components of hub connectivity.", "tab:a_components", "lcccccrr", [" & " + " & ".join(l for _, l in O8) + " & First stage & KP $F$ & N \\\\"], rows,
      "Hub $=$ the airport with the highest GACI in the country-year; components from the airport-level GACI panel. A single instrument moves every component (first-stage column), so one-at-a-time estimates are not separately identified; Panel B reports the pairwise horse races. " + NOTE_BASE, size="\\footnotesize")
# A9 mediators (macro channels + mech)
macro = pd.read_csv("_macro_channels_results.csv", **RD)
MEDS = [("mech", "ln_tour_arr", "ln international tourist arrivals"), ("mech", "emp_ind", "Employment in industry, \\%"), ("mech", "emp_agr", "Employment in agriculture, \\%"), ("mech", "emp_srv", "Employment in services, \\%"), ("mech", "urban", "Urban population, \\%"), ("mech", "trade_gdp", "Trade, \\% of GDP"), ("mech", "fdi_gdp", "FDI inflows, \\% of GDP"), ("mech", "wage_emp", "Wage and salaried workers, \\%"), ("mech", "unemp", "Unemployment rate, \\%"), ("mech", "ln_gdppc", "ln GDP per capita"),
        ("macro", "sh_diff", "Differentiated-goods share of trade"), ("macro", "ln_tr_diff", "ln differentiated-goods trade"), ("macro", "ln_tr_hivw", "ln high value-to-weight trade"), ("macro", "ln_nflow", "ln number of export partners"), ("macro", "ln_largest_city", "ln largest-city share of urban population"), ("macro", "labsh", "Labour share of income (PWT)"), ("macro", "ln_priv_credit", "ln private credit, \\% of GDP"), ("macro", "resource_rents", "Natural resource rents, \\% of GDP")]
rows = []
for src, mv, lab in MEDS:
    df = mech if src == "mech" else macro; blkA, blkB = ("B", "C") if src == "mech" else ("A", "B")
    a = g(df, block=blkA, item="apath", outcome=mv); cp = g(df, block=blkB, item=mv, outcome="ln_gini_mkt", term="ln_gaci_max"); bm = g(df, block=blkB, item=mv, outcome="ln_gini_mkt", term=mv)
    if a is None or cp is None: continue
    dd = 4 if abs(bm.b) < 0.05 else 3
    rows.append(f"{lab} & {cs(a.b, a.p, 2)} {ss(a.se, 2)} & {cs(cp.b, cp.p)} {ss(cp.se)} & {cs(bm.b, bm.p, dd)} {ss(bm.se, dd)} & {cp.kpf:.1f} & {n(cp.N)} \\\\")
table("tab_a_mediators", "Candidate mediators: does the hub move them, and do they transmit the effect? (ln market Gini)", "tab:a_mediators", "lccccc",
      ["Mediator & $a$: hub $\\rightarrow$ mediator (2SLS) & $c'$: hub with mediator held fixed & $b$: mediator & KP $F$ & N \\\\"], rows,
      "$a$ is the 2SLS effect of $\\ln\\mathrm{GACI}_{max}$ on the mediator; $c'$ and $b$ come from the outcome equation with the mediator as a control and the hub instrumented. Mediators from the World Development Indicators, BACI (Rauch classification and unit values), and the Penn World Table. " + NOTE_BASE, size="\\footnotesize")
print("tables written:", sorted(os.listdir(OUT)))
