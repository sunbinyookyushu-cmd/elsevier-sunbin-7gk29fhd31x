# -*- coding: utf-8 -*-
"""61_tex_tables_wid.py : LaTeX table fragments for the WID-main manuscript (draft_v4_wid_20260928/tables/*.tex)
   from _wid_results.csv, _wid_sumstat.csv, _wid_aggregate_bycontinent.csv (60_wid_analysis.py)."""
import os, numpy as np, pandas as pd
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
OUT = os.path.join(D, "draft_v4_wid_20260928", "tables"); os.makedirs(OUT, exist_ok=True)
R = pd.read_csv("_wid_results.csv"); R["sample"] = R["sample"].fillna(""); R["panel"] = R["panel"].fillna("")
def st(p): return "" if pd.isna(p) else "\\sym{***}" if p < .01 else "\\sym{**}" if p < .05 else "\\sym{*}" if p < .1 else ""
def cs(b, p, d=3): return "" if pd.isna(b) else f"{(0.0 if abs(b) < 0.5 * 10 ** (-d) else b):.{d}f}{st(p)}"
def ss(se, d=3): return "" if pd.isna(se) else f"({se:.{d}f})"
def n(x): return "" if pd.isna(x) else f"{int(x):,}".replace(",", "{,}")
def g(**kw):
    m = R
    for k, v in kw.items(): m = m[m[k] == v]
    return m.iloc[0] if len(m) else None
def coef_rows(label, cells, d=3):
    return [label + " & " + " & ".join(cs(c.b, c.p, d) if c is not None else "" for c in cells) + " \\\\", " & " + " & ".join(ss(c.se, d) if c is not None else "" for c in cells) + " \\\\"]
WIDE = {"tab_main", "tab_growth_stage", "tab_channels", "tab_splits", "tab_sumstat", "tab_a_stagedefs", "tab_a_aggregate", "tab_robust"}
TALL = {"tab_incidence", "tab_growth_stage", "tab_a_swiid", "tab_robust", "tab_hub_network", "tab_channels"}
def table(name, caption, label, colspec, header_rows, body_rows, notes, size="\\small"):
    place = "p" if name in TALL else "H"; wide = name in WIDE
    L = [f"\\begin{{table}}[{place}]", "\\centering", f"\\caption{{{caption}}}", f"\\label{{{label}}}"]
    if wide:
        L += ["\\begin{minipage}{\\linewidth}", "\\centering", "\\resizebox{\\linewidth}{!}{%", f"\\begin{{tabular}}{{{colspec}}}", "\\toprule"] + header_rows + ["\\midrule"] + body_rows + ["\\bottomrule", "\\end{tabular}}", "\\par\\vspace{3pt}\\begin{flushleft}\\footnotesize " + notes + "\\end{flushleft}", "\\end{minipage}", "\\end{table}"]
    else:
        L += ["\\begin{threeparttable}", size, f"\\begin{{tabular}}{{{colspec}}}", "\\toprule"] + header_rows + ["\\midrule"] + body_rows + ["\\bottomrule", "\\end{tabular}", "\\begin{tablenotes}\\small", "\\item " + notes, "\\end{tablenotes}", "\\end{threeparttable}", "\\end{table}"]
    open(os.path.join(OUT, name + ".tex"), "w", encoding="utf-8").write("\n".join(L) + "\n")
NOTE = "Country-year panel of 178 economies, 1996--2023. All regressions include country and year fixed effects and log population. 2SLS instruments $\\ln\\mathrm{GACI}_{max}$ with the Feyrer interaction $Z_{ct}=a_t\\times\\ln\\mathrm{MA}^{air}_{c,1996}$; KP $F$ is the Kleibergen--Paap $rk$ Wald statistic. Group incomes are the log average pretax national income of the group (WID, equal-split adults); shares are log income shares, computed as log group income minus log mean income so that all groups use the same sample. Standard errors clustered by country in parentheses. \\sym{*}~$p<0.10$, \\sym{**}~$p<0.05$, \\sym{***}~$p<0.01$."
NOTE_SHORT = "Specification as in Table~\\ref{tab:main}: country and year fixed effects, log population, $\\ln\\mathrm{GACI}_{max}$ instrumented by the Feyrer interaction; standard errors clustered by country in parentheses. \\sym{*}~$p<0.10$, \\sym{**}~$p<0.05$, \\sym{***}~$p<0.01$."
OL = {"ln_apt_all": "Mean income", "ln_apt_top30": "Top-30\\% income", "ln_apt_mid40": "Middle-40\\% income", "ln_apt_b30": "Bottom-30\\% income", "ln_spt_b30": "Bottom-30\\% share", "ln_spt_top30": "Top-30\\% share", "ln_spt_mid40": "Middle-40\\% share", "gap_top30_b30": "Top-30 minus bottom-30 income", "ln_gdppc": "ln GDP per capita"}

# ================= T1 summary statistics
s = pd.read_csv("_wid_sumstat.csv")
rows = [f"{r['var'].replace('%', chr(92) + '%')} & {n(r.N)} & {r['mean']:.3f} & {r.sd:.3f} & {r.within:.3f} & {r['min']:.3f} & {r['max']:.3f} \\\\" for _, r in s.iterrows()]
table("tab_sumstat", "Summary statistics, estimation sample (178 economies, 1996--2023).", "tab:sumstat", "lrrrrrr", ["Variable & N & Mean & SD & Within SD & Min & Max \\\\"], rows,
      "Within SD is the standard deviation after removing country means. Shares in percent of pretax national income (WID, equal-split adults); the WID group incomes that serve as outcomes are in constant local currency per adult and enter the regressions in logs, so their levels are not comparable across countries and are not tabulated. GACI in index units; the airport Gini is computed over the airports of each country-year (countries with at least two airports).")

# ================= T2 main
MO = ["ln_apt_all", "ln_apt_top30", "ln_apt_b30", "ln_spt_b30", "gap_top30_b30"]
rows = []
for pan, plab, x in [("max", "Panel A. Hub connectivity, $\\ln\\mathrm{GACI}_{max}$ (headline)", "ln_gaci_max"), ("cwm", "Panel B. Hub quality, $\\ln\\mathrm{GACI}_{cwm}$", "ln_gaci_cwm"), ("sum", "Panel C. Total connectivity, $\\ln\\mathrm{GACI}_{sum}$", "ln_gaci_sum")]:
    a = g(block="main", panel=pan, spec="2SLS", outcome="ln_apt_all")
    rows.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{plab}}}}}\\\\")
    rows.append(f"First stage: instrument coef. & \\multicolumn{{5}}{{l}}{{{a.fs_b:.3f}{st(2*(1-__import__('scipy').stats.norm.cdf(abs(a.fs_b/a.fs_se))))}\\ \\ ({a.fs_se:.3f}),\\ \\ KP $F={a.kpf:.1f}$}} \\\\")
    rows += coef_rows("OLS", [g(block="main", panel=pan, spec="OLS", outcome=o) for o in MO]); rows += coef_rows("2SLS", [g(block="main", panel=pan, spec="2SLS", outcome=o) for o in MO]); rows.append("\\addlinespace")
rows += ["\\midrule", "Country, Year FE & Yes & Yes & Yes & Yes & Yes \\\\", f"Observations & {n(a.N)} & {n(a.N)} & {n(a.N)} & {n(a.N)} & {n(a.N)} \\\\"]
table("tab_main", "Main results: OLS, first stage, and 2SLS, by connectivity measure.", "tab:main", "lccccc", [" & Mean income & Top-30\\% income & Bottom-30\\% income & Bottom-30\\% share & Top-30 minus bottom-30 \\\\", " & $\\ln y$ & $\\ln y_{70-100}$ & $\\ln y_{0-30}$ & $\\ln s_{0-30}$ & $\\ln y_{70-100}-\\ln y_{0-30}$ \\\\"], rows,
      "Each panel instruments its connectivity measure with the Feyrer interaction. The first-stage row regresses the connectivity measure on the instrument with log population and two-way fixed effects. The last column is a difference outcome and gives the exact difference of the two elasticities with its standard error. " + NOTE)

# ================= T3 incidence
G = [("d1", "p0--10"), ("d2", "p10--20"), ("d3", "p20--30"), ("d4", "p30--40"), ("d5", "p40--50"), ("d6", "p50--60"), ("d7", "p60--70"), ("d8", "p70--80"), ("d9", "p80--90"), ("d10", "p90--100"), ("t1", "Top 1\\%"), ("t01", "Top 0.1\\%"), ("b30", "Bottom 30\\%"), ("mid40", "Middle 40\\% (p30--70)"), ("top30", "Top 30\\%"), ("b50", "Bottom 50\\%"), ("all", "All adults (mean income)")]
rows = ["\\multicolumn{5}{l}{\\emph{Panel A. Elasticity to $\\ln\\mathrm{GACI}_{max}$, 2SLS}}\\\\"]
for k, lab in G:
    a = g(block="incidence", panel="income", spec="2SLS", outcome="ln_apt_" + k); b = g(block="incidence", panel="share", spec="2SLS", outcome="ln_spt_" + k) if k != "all" else None
    rows.append(f"{lab} & {cs(a.b, a.p)} & {ss(a.se)} & " + (f"{cs(b.b, b.p)} & {ss(b.se)}" if b is not None else "-- & ") + " \\\\")
rows += ["\\addlinespace", "\\multicolumn{5}{l}{\\emph{Panel B. Differences between groups (difference outcomes)}}\\\\"]
for o, lab in [("gap_top30_b30", "Top 30\\% minus bottom 30\\%"), ("gap_tophalf_bothalf", "Top half minus bottom half"), ("gap_d10_b50", "p90--100 minus bottom 50\\%"), ("gap_t1_d10", "Top 1\\% minus p90--100")]:
    a = g(block="incidence", panel="diff", spec="2SLS", outcome=o); rows.append(f"{lab} & {cs(a.b, a.p)} & {ss(a.se)} & & \\\\")
a = g(block="incidence", panel="income", spec="2SLS", outcome="ln_apt_all")
rows += ["\\midrule", f"First-stage KP $F$ & \\multicolumn{{2}}{{c}}{{{a.kpf:.1f}}} & \\multicolumn{{2}}{{c}}{{{a.kpf:.1f}}} \\\\", f"Observations & \\multicolumn{{2}}{{c}}{{{n(a.N)}}} & \\multicolumn{{2}}{{c}}{{{n(a.N)}}} \\\\"]
table("tab_incidence", "Incidence of hub connectivity across the income distribution (2SLS, Feyrer instrument).", "tab:incidence", "lcccc", [" & \\multicolumn{2}{c}{Average income of the group} & \\multicolumn{2}{c}{Income share of the group} \\\\", "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}", "WID group & Coef. & (s.e.) & Coef. & (s.e.) \\\\"], rows,
      "Each cell is a separate regression on the same sample; the average income of the bottom two deciles is undefined (non-positive) in 3 and 1 country-years, so those rows use 4{,}534 and 4{,}536 observations. Panel B regresses the difference of two group outcomes on instrumented connectivity. " + NOTE)

# ================= T4 growth and incidence by baseline hub size
GO = ["ln_gdppc", "ln_apt_all", "ln_apt_b30", "ln_spt_b30", "gap_top30_b30"]
rows = []
def stage_rows(pan, items):
    out = []
    for val, lab in items:
        a = g(block="growth_stage", panel=pan, spec="2SLS", sample=val, outcome="ln_gdppc")
        r2 = coef_rows(lab + ": 2SLS", [g(block="growth_stage", panel=pan, spec="2SLS", sample=val, outcome=o) for o in GO]); r2[0] = r2[0].replace(" \\\\", f" & {a.kpf:.1f} \\\\"); r2[1] = r2[1].replace(" \\\\", f" & N = {n(a.N)} \\\\"); out += r2
        out += coef_rows("\\quad OLS", [g(block="growth_stage", panel=pan, spec="OLS", sample=val, outcome=o) for o in GO])
    return out
rows.append("\\multicolumn{7}{l}{\\emph{Panel A. Median split on $\\mathrm{GACI}_{max}$ in 1996}}\\\\"); rows += stage_rows("median", [("below", "Below median (smaller hubs)"), ("above", "Above median (larger hubs)")])
rows.append("\\addlinespace\\multicolumn{7}{l}{\\emph{Panel B. Terciles}}\\\\"); rows += stage_rows("tercile", [("low", "Low"), ("mid", "Middle"), ("high", "High")])
rows.append("\\addlinespace\\multicolumn{7}{l}{\\emph{Reference}}\\\\"); rows += stage_rows("full", [("full", "Full sample")])
table("tab_growth_stage", "Growth and its incidence by baseline hub size (countries grouped on $\\mathrm{GACI}_{max}$ in 1996).", "tab:growth_stage", "lcccccc", [" & ln GDP p.c. & Mean income & Bottom-30\\% income & Bottom-30\\% share & Top-30 minus bottom-30 & KP $F$ / N \\\\"], rows,
      "Countries are grouped on their earliest observed $\\mathrm{GACI}_{max}$ (1996 for most). GDP per capita from the World Development Indicators (constant 2015 US dollars). The instrument has no power among the largest hubs (upper half, top tercile), which are shown for completeness. " + NOTE, size="\\footnotesize")

# ================= T5 hub vs network
rows = []
for o in ["ln_spt_b30", "gap_top30_b30", "ln_apt_all"]:
    rows.append(f"\\multicolumn{{4}}{{l}}{{\\emph{{Dependent variable: {OL[o]}}}}}\\\\")
    b0 = g(block="hub_network", spec="baseline", outcome=o); b1 = g(block="hub_network", spec="hub_ctrl_sum", outcome=o, term="ln_gaci_max"); c1 = g(block="hub_network", spec="hub_ctrl_sum", outcome=o, term="ln_gaci_sum")
    b3 = g(block="hub_network", spec="eig_iv_ctrl_cap", outcome=o, term="ln_hub_eig"); c3 = g(block="hub_network", spec="eig_iv_ctrl_cap", outcome=o, term="ln_hub_cap")
    rows += coef_rows("$\\ln\\mathrm{GACI}_{max}$ (hub), instrumented", [b0, b1, None]); rows += coef_rows("$\\ln\\mathrm{GACI}_{sum}$ (whole network), control", [None, c1, None])
    rows += coef_rows("ln hub eigenvector centrality, instrumented", [None, None, b3]); rows += coef_rows("ln hub seat capacity, control", [None, None, c3])
    rows.append(f"KP $F$ & {b0.kpf:.1f} & {b1.kpf:.1f} & {b3.kpf:.1f} \\\\"); rows.append(f"Observations & {n(b0.N)} & {n(b1.N)} & {n(b3.N)} \\\\"); rows.append("\\addlinespace")
table("tab_hub_network", "Mechanism (I): which connectivity carries the effect?", "tab:hub_network", "lccc", [" & (1) & (2) & (3) \\\\", " & Baseline & Hub + network & Core integration \\\\"], rows,
      "Column (2) adds total connectivity as a control; column (3) instruments the hub's eigenvector centrality (integration with the global core) and controls for its seat capacity. " + NOTE_SHORT, size="\\footnotesize")

# ================= T6 channels
MED = [("ln_gdppc", "ln GDP per capita"), ("ln_tr_diff", "ln differentiated-goods trade"), ("ln_tr_hivw", "ln high value-to-weight trade"), ("ln_tour", "ln international tourist arrivals"), ("emp_ind", "Employment in industry, \\%")]
rows = []
for o, plab in [("ln_spt_b30", "Panel A. Bottom-30\\% share"), ("ln_apt_b30", "Panel B. Bottom-30\\% income"), ("ln_apt_all", "Panel C. Mean income")]:
    rows.append(f"\\multicolumn{{8}}{{l}}{{\\emph{{{plab}}}}}\\\\")
    for m, lab in MED:
        a = g(block="channels", panel="apath", outcome=m); tot = g(block="channels", panel="decomp", spec="total", sample=m, outcome=o)
        dire = g(block="channels", panel="decomp", spec="direct", sample=m, outcome=o, term="ln_gaci_max"); th = g(block="channels", panel="decomp", spec="direct", sample=m, outcome=o, term=m)
        da = 2 if m == "emp_ind" else 3
        rows += [f"{lab} & {cs(a.b, a.p, da)} {ss(a.se, da)} & {cs(th.b, th.p)} {ss(th.se)} & {a.b * th.b:.3f} & {cs(dire.b, dire.p)} {ss(dire.se)} & {cs(tot.b, tot.p)} {ss(tot.se)} & {dire.kpf:.1f} & {n(dire.N)} \\\\"]
    tot = g(block="channels", panel="decomp", spec="total", sample="all5", outcome=o); dire = g(block="channels", panel="decomp", spec="direct", sample="all5", outcome=o, term="ln_gaci_max")
    rows += [f"All five channels jointly & & & {tot.b - dire.b:.3f} & {cs(dire.b, dire.p)} {ss(dire.se)} & {cs(tot.b, tot.p)} {ss(tot.se)} & {dire.kpf:.1f} & {n(dire.N)} \\\\"]
    if o != "ln_apt_all": rows.append("\\addlinespace")
table("tab_channels", "Mechanism (III): is the exclusion of the bottom carried by the growth channels? Decomposition of the hub effect.", "tab:channels", "lccccccr",
      ["Channel $M$ & $a$: $\\mathrm{GACI}_{max}\\rightarrow M$ & $\\theta$: $M\\rightarrow$ outcome & Indirect $a\\theta$ & Direct (hub) & Total & KP $F$ & N \\\\"], rows,
      "Each row decomposes the 2SLS effect of $\\ln\\mathrm{GACI}_{max}$ on the outcome into the part transmitted by channel $M$ and the direct effect that remains with $M$ held fixed: Total $=$ Direct $+$ Indirect, where $a$ is the 2SLS effect of instrumented connectivity on $M$, $\\theta$ is the coefficient on $M$ when it is added to the second stage, and the total is re-estimated on the channel's sample so that the identity holds exactly. The joint row holds all five channels fixed; its indirect column is the sum of the five indirect effects (total minus direct). Because the channels are themselves outcomes of connectivity, the decomposition is a Gelbach-type accounting under the assumption that the channel coefficient is not confounded, and is reported as descriptive. KP $F$ refers to the direct regression. Channels from the World Development Indicators and BACI. " + NOTE, size="\\footnotesize")

# ================= T7 splits
rows = []
SP = [("airport_concentration", "Airport network concentrated (above median)", "above"), ("airport_concentration", "Airport network dispersed (below median)", "below"), ("urbanisation", "Urbanisation above median", "above"), ("urbanisation", "Urbanisation below median", "below"),
      ("baseline_income", "Baseline GDP per capita above median", "above"), ("baseline_income", "Baseline GDP per capita below median", "below"), ("tourism_dependence", "Tourism-dependent (above median)", "above"), ("tourism_dependence", "Not tourism-dependent (below median)", "below"), ("era", "1996--2007", "1996-2007"), ("era", "2010--2023 excluding 2020--21", "2010-2023")]
for pan, lab, smp in SP:
    cells = [g(block="splits", panel=pan, sample=smp, outcome=o) for o in ["ln_spt_b30", "ln_apt_b30", "ln_apt_all", "gap_top30_b30"]]
    r = coef_rows(lab, cells); r[0] = r[0].replace(" \\\\", f" & {cells[0].kpf:.1f} & {cells[0].rf_p:.3f} & {n(cells[0].N)} \\\\"); rows += r
# spillover
a = g(block="spill", outcome="ln_spt_b30", term="ln_gaci_max"); b = g(block="spill", outcome="ln_spt_b30", term="nbr_g")
rows += ["\\addlinespace", "\\multicolumn{8}{l}{\\emph{Own and contiguous neighbours' connectivity, jointly instrumented (bottom-30\\% share)}}\\\\"]
rows += coef_rows("Own $\\ln\\mathrm{GACI}_{max}$", [a, g(block="spill", outcome="ln_apt_b30", term="ln_gaci_max"), g(block="spill", outcome="ln_apt_all", term="ln_gaci_max"), g(block="spill", outcome="gap_top30_b30", term="ln_gaci_max")])
rows += coef_rows("Neighbours' ln GACI (contiguity, leave-out mean)", [b, g(block="spill", outcome="ln_apt_b30", term="nbr_g"), g(block="spill", outcome="ln_apt_all", term="nbr_g"), g(block="spill", outcome="gap_top30_b30", term="nbr_g")])
table("tab_splits", "Mechanism (IV): where is the effect found? Split samples (2SLS, Feyrer instrument).", "tab:splits", "lcccccrr",
      [" & Bottom-30\\% share & Bottom-30\\% income & Mean income & Top-30 minus bottom-30 & KP $F$ & RF $p$ & N \\\\"], rows,
      "Splits at the median of each country's earliest observed value: the Gini of GACI across its airports (network concentration), urbanisation, GDP per capita, and tourism receipts as a share of exports. RF $p$ is the $p$-value of the instrument in the reduced form for the bottom-30\\% share, which does not depend on first-stage strength. The last two rows instrument own connectivity with the own shifter and the leave-out mean of contiguous neighbours' ln GACI with their shifters. " + NOTE, size="\\footnotesize")

# ================= T8 redistribution
rows = []
for o, lab in [("ln_bot50_wid", "Bottom-50\\% share, pretax"), ("ln_bot50_post_wid", "Bottom-50\\% share, post-tax"), ("post_minus_pre_b50", "Post-tax minus pretax, bottom 50\\%"), ("ln_top10_wid", "Top-10\\% share, pretax"), ("ln_top10_post_wid", "Top-10\\% share, post-tax"), ("post_minus_pre_t10", "Post-tax minus pretax, top 10\\%")]:
    a = g(block="redistribution", spec="2SLS", outcome=o); b = g(block="redistribution", spec="OLS", outcome=o)
    rows.append(f"{lab} & {cs(b.b, b.p)} & {ss(b.se)} & {cs(a.b, a.p)} & {ss(a.se)} \\\\")
a = g(block="redistribution", spec="2SLS", outcome="ln_bot50_wid"); rows += ["\\midrule", f"KP $F$ & & & \\multicolumn{{2}}{{c}}{{{a.kpf:.1f}}} \\\\", f"Observations & \\multicolumn{{2}}{{c}}{{{n(a.N)}}} & \\multicolumn{{2}}{{c}}{{{n(a.N)}}} \\\\"]
table("tab_redistribution", "Mechanism (V): is the effect offset by redistribution? Pretax and post-tax income shares (WID).", "tab:redistribution", "lcccc", [" & \\multicolumn{2}{c}{OLS} & \\multicolumn{2}{c}{2SLS} \\\\", "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}", " & Coef. & (s.e.) & Coef. & (s.e.) \\\\"], rows,
      "Post-tax national income shares from the WID distributional national accounts (after all taxes and transfers). The difference rows are difference outcomes: a negative coefficient for the bottom 50\\% means that taxes and transfers redistribute less toward the bottom half after connectivity rises. " + NOTE)

# ================= T9 robustness
RO = ["ln_spt_b30", "gap_top30_b30", "ln_apt_all"]
rows = ["\\multicolumn{5}{l}{\\emph{Panel A. Baseline}}\\\\"]
def rrow(lab, cells, showF=True):
    return [lab + " & " + " & ".join(f"{cs(c.b, c.p)} {ss(c.se)}" for c in cells) + (f" & {cells[0].kpf:.1f}" if showF and pd.notna(cells[0].kpf) else " & ") + f" & {n(cells[0].N)} \\\\"]
rows += rrow("2SLS, Feyrer instrument (Table~\\ref{tab:main})", [g(block="robust", panel="sample", spec="baseline", outcome=o) for o in RO])
rows.append("\\multicolumn{5}{l}{\\emph{Panel B. Sample}}\\\\")
for spec, lab in [("drop_top10_hubs", "Excluding the ten largest hub economies"), ("pre2020", "1996--2019"), ("drop_crises", "Excluding 2008--09 and 2020--21")]: rows += rrow(lab, [g(block="robust", panel="sample", spec=spec, outcome=o) for o in RO])
rows.append("\\multicolumn{5}{l}{\\emph{Panel C. Exclusion restriction: competing exposure $\\times$ shifter as control}}\\\\")
for spec, lab in [("sea_ma_x_a", "$\\ln\\mathrm{MA}^{sea}_{c,1996}\\times a_t$ (maritime market access)"), ("gdp0_x_a", "Baseline ln GDP per capita $\\times a_t$"), ("land0_x_a", "ln land area $\\times a_t$")]: rows += rrow(lab, [g(block="robust", panel="exclusion", spec=spec, outcome=o) for o in RO])
rows.append("\\multicolumn{5}{l}{\\emph{Panel D. Inference}}\\\\")
for spec, lab in [("cluster_country", "Clustered by country"), ("twoway_country_year", "Two-way clustered (country, year)"), ("conley_1000", "Conley spatial HAC, 1{,}000 km"), ("conley_2000", "Conley spatial HAC, 2{,}000 km")]: rows += rrow(lab, [g(block="robust", panel="inference", spec=spec, outcome=o) for o in RO], showF=(spec == "cluster_country"))
rows.append("\\multicolumn{6}{l}{\\emph{Panel E. Alternative distributional measures, 2SLS (coefficient in the first column)}}\\\\")
for o, lab in [("ln_spt_b50", "Bottom-50\\% share"), ("ln_palma", "Palma ratio (top 10 / bottom 40)"), ("ln_gini_pre_wid", "WID Gini"), ("ln_spt_d10", "Top-10\\% share"), ("ln_absgap", "Absolute gap, top 10 minus bottom 50")]:
    a = g(block="measures", panel="max", spec="2SLS", outcome=o); rows += [f"{lab} & {cs(a.b, a.p)} {ss(a.se)} & & & & {n(a.N)} \\\\"]
table("tab_robust", "Robustness of the headline estimates: sample, exclusion restriction, inference and alternative measures (2SLS, Feyrer instrument).", "tab:robust", "lcccrr", [" & Bottom-30\\% share & Top-30 minus bottom-30 & Mean income & KP $F$ & N \\\\"], rows,
      "Panel C adds, one at a time, a competing baseline exposure interacted with the aviation shifter $a_t$ (Section~\\ref{sec:strategy}); $\\mathrm{MA}^{sea}$ is Equation~\\eqref{eq:ma} computed with CERDI port-to-port sea distances. Panel D varies the variance estimator. The two-way clustered row keeps the baseline point estimates; the Conley rows are re-estimated on the 4{,}334 country-years of the 165 economies with centroid coordinates, so their point estimates differ slightly. Conley standard errors use a Bartlett kernel in great-circle distance between country centroids and allow arbitrary within-country serial correlation. Panel E replaces the bottom-30\\% share by other summaries of the same WID distribution: Palma $=$ top-10 share / bottom-40 share; the absolute gap is the top-10 minus bottom-50 average income in constant local prices; the WID Gini is the DINA Gini. " + NOTE_SHORT)

# ================= appendix
# A1 quartiles and GDP terciles (heterogeneity, not robustness)
rows = ["\\multicolumn{7}{l}{\\emph{Panel A. Quartiles of $\\mathrm{GACI}_{max}$ in 1996}}\\\\"]; rows += stage_rows("quartile", [("q1", "Q1 (smallest)"), ("q2", "Q2"), ("q3", "Q3"), ("q4", "Q4 (largest)")])
rows.append("\\addlinespace\\multicolumn{7}{l}{\\emph{Panel B. Terciles of baseline GDP per capita}}\\\\")
for val, lab in [("low", "Low"), ("mid", "Middle"), ("high", "High")]:
    a = g(block="stagedefs", panel="gdp_tercile", sample=val, outcome="ln_gdppc"); r = coef_rows(lab + ": 2SLS", [g(block="stagedefs", panel="gdp_tercile", sample=val, outcome=o) for o in GO]); r[0] = r[0].replace(" \\\\", f" & {a.kpf:.1f} \\\\"); r[1] = r[1].replace(" \\\\", f" & N = {n(a.N)} \\\\"); rows += r
table("tab_a_stagedefs", "Growth and its incidence under alternative baseline groupings (2SLS).", "tab:a_stagedefs", "lcccccc", [" & ln GDP p.c. & Mean income & Bottom-30\\% income & Bottom-30\\% share & Top-30 minus bottom-30 & KP $F$ / N \\\\"], rows,
      "Groups are formed over countries on the stated baseline variable. The instrument has no power in the two largest quartiles, shown for completeness. " + NOTE, size="\\footnotesize")
# A3 SWIID subsample
rows = ["\\multicolumn{3}{l}{\\emph{Panel A. Survey-based Gini coefficients (SWIID)}}\\\\"]
for o, lab in [("ln_gini_mkt", "ln market-income Gini"), ("ln_gini_disp", "ln disposable-income Gini")]:
    a = g(block="swiid_subsample", spec="2SLS", outcome=o); b = g(block="swiid_subsample", spec="OLS", outcome=o); rows.append(f"{lab} & {cs(b.b, b.p)} {ss(b.se)} & {cs(a.b, a.p)} {ss(a.se)} \\\\")
rows += ["\\addlinespace", "\\multicolumn{3}{l}{\\emph{Panel B. WID outcomes on the same subsample}}\\\\"]
for o, lab in [("ln_apt_all", "Mean income"), ("ln_apt_top30", "Top-30\\% income"), ("ln_apt_b30", "Bottom-30\\% income"), ("ln_spt_b30", "Bottom-30\\% share"), ("ln_apt_b50", "Bottom-50\\% income"), ("ln_spt_b50", "Bottom-50\\% share"), ("gap_top30_b30", "Top-30 minus bottom-30"), ("gap_tophalf_bothalf", "Top half minus bottom half")]:
    a = g(block="swiid_subsample", spec="2SLS", outcome=o); b = g(block="swiid_subsample", spec="OLS", outcome=o); rows.append(f"{lab} & {cs(b.b, b.p)} {ss(b.se)} & {cs(a.b, a.p)} {ss(a.se)} \\\\")
rows += ["\\addlinespace", "\\multicolumn{3}{l}{\\emph{Panel C. Decile incomes and shares, 2SLS}}\\\\"]
for k, lab in G[:11] + [("b50", "Bottom 50\\%"), ("all", "All adults")]:
    a = g(block="swiid_subsample", panel="income", spec="2SLS", outcome="ln_apt_" + k); b = g(block="swiid_subsample", panel="share", spec="2SLS", outcome="ln_spt_" + k) if k != "all" else None
    if a is None: continue
    rows.append(f"{lab}: income {cs(a.b, a.p)} {ss(a.se)}" + (f"; share {cs(b.b, b.p)} {ss(b.se)}" if b is not None else "") + " & & \\\\")
a = g(block="swiid_subsample", spec="2SLS", outcome="ln_gini_mkt"); rows += ["\\midrule", f"KP $F$ & & {a.kpf:.1f} \\\\", f"Observations & {n(a.N)} & {n(a.N)} \\\\"]
table("tab_a_swiid", "The subsample with survey-based Gini coefficients (166 economies, 3{,}716 country-years).", "tab:a_swiid", "lcc", [" & OLS & 2SLS \\\\"], rows,
      "The Standardized World Income Inequality Database \\citep{Solt_2020} provides market- and disposable-income Gini coefficients for 166 of the 178 economies. Panel A uses them as outcomes; Panels B and C re-estimate the WID outcomes on the same subsample. " + NOTE)
# A4 aggregate
agc = pd.read_csv("_wid_aggregate_bycontinent.csv", index_col=0, keep_default_na=False)
NAME = {"AF": "Africa", "AS": "Asia-Pacific", "EU": "Europe", "LA": "Latin America", "ME": "Middle East", "NA": "North America", "SW": "Oceania", "ALL (unweighted)": "All (unweighted)", "WORLD (pop-weighted)": "World (population-weighted)"}
rows = [f"{NAME.get(i, i)} & {int(r['n'])} & {r['dln']:.2f} & {r['implied_all_pct']:.1f} & {r['actual_all_pct']:.1f} & {r['implied_top30_pct']:.1f} & {r['implied_b30_pct']:.1f} & {r['actual_b30_pct']:.1f} & {r['implied_b30sh_pts']:.2f} & {r['actual_b30sh_pts']:.2f} \\\\" for i, r in agc.iterrows()]
table("tab_a_aggregate", "Implied incidence of observed hub-connectivity growth, first to last year (1996--2023).", "tab:a_aggregate", "lrrrrrrrrr",
      [" & & & \\multicolumn{2}{c}{Mean income, \\%} & Top-30 income, \\% & \\multicolumn{2}{c}{Bottom-30 income, \\%} & \\multicolumn{2}{c}{Bottom-30 share, pts} \\\\", "\\cmidrule(lr){4-5}\\cmidrule(lr){6-6}\\cmidrule(lr){7-8}\\cmidrule(lr){9-10}", "Region & N & $\\Delta\\ln\\mathrm{GACI}$ & Implied & Actual & Implied & Implied & Actual & Implied & Actual \\\\"], rows,
      "Implied $=$ each country's change in $\\ln\\mathrm{GACI}_{max}$ between its first and last year with data ($\\geq 15$ years apart; 162 countries) multiplied by the 2SLS elasticities of Table~\\ref{tab:main} (incomes in percent; the share converted to points using the initial share). Actual $=$ observed change over the same window. Continent rows are unweighted country means.", size="\\footnotesize")
print("tables written:", sorted(os.listdir(OUT)))
