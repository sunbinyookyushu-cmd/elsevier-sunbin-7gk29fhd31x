# 10_assemble.py : collect all result CSVs -> results xlsx + LaTeX table fragments (tables/*.tex)
import pandas as pd, numpy as np, os
os.makedirs("tables", exist_ok=True)
# NOTE: "NA" is the North America continent code. Without keep_default_na=False
# pandas turns it into NaN, which silently drops North America from the
# continent tables below. RD holds the read options used for every result CSV.
NA = ["."]
RD = dict(keep_default_na=False, na_values=["", "."])
def st(p):
    if pd.isna(p): return ""
    return "\\sym{***}" if p < .01 else "\\sym{**}" if p < .05 else "\\sym{*}" if p < .1 else ""
def cell(b, se, p, d=3):
    if pd.isna(b): return "--"
    return f"{b:.{d}f}{st(p)} ({se:.{d}f})" if not pd.isna(se) else f"{b:.{d}f}{st(p)}"
def bse(b, se, p, d=3):
    return (f"{b:.{d}f}{st(p)}", f"({se:.{d}f})")

main = pd.read_csv("_main_results.csv", **RD)
het = pd.read_csv("_hetero_results.csv", **RD)
conc = pd.read_csv("_conc_mech_results.csv", **RD)
ld = pd.read_csv("_longdiff_results.csv", **RD)
rob = pd.read_csv("_robust_results.csv", **RD)
tails = pd.read_csv("_tails_results.csv", **RD)
diag = pd.read_csv("_diag_results.csv", **RD)
osk = pd.read_csv("_openskies_results.csv", **RD)
gdp = pd.read_csv("_gdp_results.csv", **RD)
sums = pd.read_csv("_sumstats.csv")
contrib = pd.read_csv("_contribution_bycontinent.csv", index_col=0)
contrib_c = pd.read_csv("_contribution_bycountry.csv", index_col=0)
# "NA" is the North America continent code, not a missing value: pandas reads it as
# NaN by default, which silently dropped CAN and USA from the groupby below.
contrib_c["cont"] = contrib_c["cont"].fillna("NA")

with pd.ExcelWriter("Inequality_results_20260916.xlsx") as xw:
    sums.to_excel(xw, "T1_sumstats", index=False)
    main.to_excel(xw, "T2_main", index=False)
    het.to_excel(xw, "T3_heterogeneity", index=False)
    conc.to_excel(xw, "T4_conc_mechanism", index=False)
    tails.to_excel(xw, "T5_tails", index=False)
    ld.to_excel(xw, "T6_horizon_longdiff", index=False)
    contrib.to_excel(xw, "T7_contribution_cont")
    contrib_c.to_excel(xw, "T7_contribution_country")
    rob.to_excel(xw, "T8_robustness", index=False)
    diag.to_excel(xw, "T9_iv_diagnostics", index=False)
    osk.to_excel(xw, "T10_openskies", index=False)
    gdp.to_excel(xw, "T11_growth_gdp", index=False)

# ---------- T1 sumstats ----------
L = ["\\begin{tabular}{lrrrrrr}", "\\toprule", "Variable & N & Mean & SD & Within SD & Min & Max \\\\", "\\midrule"]
for _, r in sums.iterrows():
    L.append(f"{str(r.Variable).replace(chr(37), chr(92)+chr(37))} & {int(r.N):,} & {r.Mean:.3f} & {r.SD:.3f} & {r['Within SD']:.3f} & {r.Min:.3f} & {r.Max:.3f} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_sumstat.tex", "w").write("\n".join(L))

# ---------- T2 main: panels by measure; cols mkt, disp; rows FS, OLS, 2SLS Feyrer, 2SLS tourism ----------
labs = {"ln_gaci_max": "Panel A. Hub connectivity, $\\ln\\mathrm{GACI}_{max}$ (headline)",
        "ln_gaci_cwm": "Panel B. Hub quality, $\\ln\\mathrm{GACI}_{cwm}$",
        "ln_gaci_sum": "Panel C. Total connectivity, $\\ln\\mathrm{GACI}_{sum}$"}
L = ["\\begin{tabular}{lcc}", "\\toprule", " & Market-income Gini & Disposable-income Gini \\\\", " & $\\ln G^{mkt}$ & $\\ln G^{disp}$ \\\\", "\\midrule"]
for tr, lab in labs.items():
    L.append(f"\\multicolumn{{3}}{{l}}{{\\emph{{{lab}}}}}\\\\")
    for ivv, ivlab in [("feyrer_int", "Feyrer"), ("tourism_int", "Tourism-heritage")]:
        fs = main[(main.iv == ivv) & (main.treat == tr) & (main.model == "FS")].iloc[0]
        L.append(f"First stage, {ivlab} instrument & \\multicolumn{{2}}{{l}}{{{fs.b:.3f}{st(fs.p)}\\ \\ ({fs.se:.3f}),\\ \\ KP $F={fs.kpf:.1f}$}} \\\\")
    row = []
    for yv in ["ln_gini_mkt", "ln_gini_disp"]:
        o = main[(main.iv == "feyrer_int") & (main.treat == tr) & (main.outcome == yv) & (main.model == "OLS")].iloc[0]
        row.append(f"{o.b:.3f}{st(o.p)} ({o.se:.3f})")
    L.append("OLS & " + " & ".join(row) + " \\\\")
    for ivv, ivlab in [("feyrer_int", "2SLS, Feyrer IV"), ("tourism_int", "2SLS, tourism IV")]:
        row = []; row2 = []
        for yv in ["ln_gini_mkt", "ln_gini_disp"]:
            o = main[(main.iv == ivv) & (main.treat == tr) & (main.outcome == yv) & (main.model == "IV")].iloc[0]
            oc = main[(main.iv == ivv) & (main.treat == tr) & (main.outcome == yv) & (main.model == "IVcl")].iloc[0]
            row.append(f"{o.b:.3f}{st(o.p)} ({o.se:.3f})"); row2.append(f"[{oc.se:.3f}]{st(oc.p)}")
        L.append(f"{ivlab} & " + " & ".join(row) + " \\\\")
        L.append(" & " + " & ".join(row2) + " \\\\")
    L.append("\\addlinespace")
n = int(main[(main.model == "OLS")].N.iloc[0])
L += ["\\midrule", "Country, Year FE & Yes & Yes \\\\", f"Observations & {n:,} & {n:,} \\\\", "\\bottomrule", "\\end{tabular}"]
open("tables/tab_main.tex", "w").write("\n".join(L))

# ---------- T3 heterogeneity (max, Feyrer) ----------
def hrow(block, term, yv):
    r = het[(het.block == block) & (het.treat == "ln_gaci_max") & (het.outcome == yv) & (het.term == term)]
    return r.iloc[0] if len(r) else None
L = ["\\begin{tabular}{lcc}", "\\toprule", " & $\\ln G^{mkt}$ & $\\ln G^{disp}$ \\\\", "\\midrule",
     "\\multicolumn{3}{l}{\\emph{Panel A. Baseline GDP per capita tercile (interaction IV)}}\\\\"]
for term, lab in [("ln_gaci_max", "Low tercile (base)"), ("mid_total", "Middle tercile (total)"), ("high_total", "High tercile (total)"), ("ln_gaci_max_mid", "Interaction: middle"), ("ln_gaci_max_high", "Interaction: high")]:
    L.append(f"{lab} & " + " & ".join(cell(*hrow('inc3', term, yv)[['b', 'se', 'p']]) for yv in ["ln_gini_mkt", "ln_gini_disp"]) + " \\\\")
L.append("\\addlinespace\\multicolumn{3}{l}{\\emph{Panel B. Baseline market-Gini tercile (interaction IV)}}\\\\")
for term, lab in [("ln_gaci_max", "Low tercile (base)"), ("g2_total", "Middle tercile (total)"), ("g3_total", "High tercile (total)"), ("ln_gaci_max_g2", "Interaction: middle"), ("ln_gaci_max_g3", "Interaction: high")]:
    L.append(f"{lab} & " + " & ".join(cell(*hrow('gini3', term, yv)[['b', 'se', 'p']]) for yv in ["ln_gini_mkt", "ln_gini_disp"]) + " \\\\")
L.append("\\addlinespace\\multicolumn{3}{l}{\\emph{Panel C. Temporal: post-2010 interaction}}\\\\")
for term, lab in [("ln_gaci_max", "Pre-2010 (base)"), ("post_total", "Post-2010 (total)"), ("ln_gaci_max_post", "Interaction: post-2010")]:
    L.append(f"{lab} & " + " & ".join(cell(*hrow('post2010', term, yv)[['b', 'se', 'p']]) for yv in ["ln_gini_mkt", "ln_gini_disp"]) + " \\\\")
L.append("\\addlinespace\\multicolumn{3}{l}{\\emph{Panel D. By continent (separate 2SLS; KP $F$ in brackets)}}\\\\")
cn = {"AF": "Africa", "AS": "Asia", "EU": "Europe", "LA": "Latin America", "ME": "Middle East", "NA": "North America", "SW": "Oceania"}
for cc, lab in cn.items():
    cells = []
    for yv in ["ln_gini_mkt", "ln_gini_disp"]:
        r = hrow('continent', cc, yv)
        cells.append(cell(r.b, r.se, r.p) + f" [{r.kpf:.1f}]" if r is not None else "--")
    L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_hetero.tex", "w").write("\n".join(L))

# ---------- T4 concentration ----------
def crow(term, model, yv):
    r = conc[(conc.block == "conc") & (conc.outcome == yv) & (conc.term == term) & (conc.model == model)]
    return r.iloc[0] if len(r) else None
L = ["\\begin{tabular}{lcc}", "\\toprule", " & $\\ln G^{mkt}$ & $\\ln G^{disp}$ \\\\", "\\midrule",
     "\\multicolumn{3}{l}{\\emph{Panel A. OLS, network concentration holding total connectivity fixed}}\\\\"]
for term, model, lab in [("ln_share_max", "OLS_withsum", "ln top-airport share of national GACI"), ("ln_gaci_sum", "OLS_withsum", "\\quad ln total connectivity (sum)"),
                         ("ln_hhi", "OLS_hhi", "ln Herfindahl of airport GACI shares"), ("ln_gaci_sum", "OLS_hhi", "\\quad ln total connectivity (sum)"),
                         ("ln_gaci_max", "OLS_max_mean", "ln GACI max (with mean)"), ("ln_gaci_mean", "OLS_max_mean", "\\quad ln GACI mean")]:
    L.append(f"{lab} & " + " & ".join(cell(*crow(term, model, yv)[['b', 'se', 'p']]) for yv in ["ln_gini_mkt", "ln_gini_disp"]) + " \\\\")
L.append("\\addlinespace\\multicolumn{3}{l}{\\emph{Panel B. 2SLS, hub connectivity instrumented, total connectivity as control}}\\\\")
for term, lab in [("ln_gaci_max", "ln GACI max (instrumented, Feyrer)"), ("ln_gaci_sum", "\\quad ln total connectivity (sum)")]:
    L.append(f"{lab} & " + " & ".join(cell(*crow(term, 'IV_max_ctrl_sum', yv)[['b', 'se', 'p']]) for yv in ["ln_gini_mkt", "ln_gini_disp"]) + " \\\\")
r = crow("ln_gaci_max", "IV_max_ctrl_sum", "ln_gini_mkt"); L.append(f"KP $F$ & {r.kpf:.1f} & {r.kpf:.1f} \\\\")
L.append("\\addlinespace\\multicolumn{3}{l}{\\emph{Panel C. 2SLS, interaction with concentrated baseline system (top-airport share $>0.5$)}}\\\\")
for term, lab in [("ln_gaci_max", "Distributed systems (base)"), ("conc_total", "Concentrated systems (total)"), ("ln_gaci_max_conc", "Interaction: concentrated")]:
    L.append(f"{lab} & " + " & ".join(cell(*crow(term, 'IV_x_conc', yv)[['b', 'se', 'p']]) for yv in ["ln_gini_mkt", "ln_gini_disp"]) + " \\\\")
L += ["\\midrule", f"Observations & {int(r.N):,} & {int(r.N):,} \\\\", "\\bottomrule", "\\end{tabular}"]
open("tables/tab_conc.tex", "w").write("\n".join(L))

# ---------- T5 tails (WID) ----------
tl = {"ln_top10_wid": "Top 10\\% share (pretax)", "ln_top1_wid": "Top 1\\% share (pretax)", "ln_bot50_wid": "Bottom 50\\% share (pretax)", "ratio_t10_b50": "ln(top 10\\% / bottom 50\\%)",
      "ln_gini_pre_wid": "Gini, pretax (WID)", "ln_gini_post_wid": "Gini, post-tax (WID)", "ln_top10_post_wid": "Top 10\\% share (post-tax)", "ln_bot50_post_wid": "Bottom 50\\% share (post-tax)"}
L = ["\\begin{tabular}{lccc}", "\\toprule", "Outcome (log) & OLS & 2SLS (robust SE) & 2SLS (clustered SE) \\\\", "\\midrule"]
for yv, lab in tl.items():
    cells = []
    for model in ["OLS", "IV", "IVcl"]:
        r = tails[(tails.block == "tails") & (tails.outcome == yv) & (tails.treat == "ln_gaci_max") & (tails.model == model)].iloc[0]
        cells.append(cell(r.b, r.se, r.p))
    L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
L.append("\\addlinespace\\multicolumn{4}{l}{\\emph{Redistribution wedge (levels)}}\\\\")
for yv, lab in [("wedge_top10", "Top 10\\% share, pretax $-$ post-tax"), ("wedge_gini", "Gini, pretax $-$ post-tax (WID)"), ("wedge_swiid", "Gini, market $-$ disposable (SWIID, points)")]:
    cells = []
    for model in ["OLS", "IV", "IVcl"]:
        r = tails[(tails.block == "wedge") & (tails.outcome == yv) & (tails.model == model)].iloc[0]
        cells.append(cell(r.b, r.se, r.p))
    L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
r = tails[(tails.block == "tails") & (tails.model == "IV") & (tails.treat == "ln_gaci_max")].iloc[0]
L += ["\\midrule", f"KP $F$ (2SLS) & & {r.kpf:.1f} & \\\\", f"Observations & {int(r.N):,} & {int(r.N):,} & {int(r.N):,} \\\\", "\\bottomrule", "\\end{tabular}"]
open("tables/tab_tails.tex", "w").write("\n".join(L))

# ---------- T6 mechanism ----------
ml = {"ln_gdppc": "ln GDP per capita", "emp_agr": "Agricultural employment share (\\%)", "emp_ind": "Industrial employment share (\\%)", "emp_srv": "Service employment share (\\%)",
      "urban": "Urban population share (\\%)", "primacy": "Population in largest city (\\%)", "unemp": "Unemployment rate (\\%)", "trade_gdp": "Trade (\\% GDP)", "fdi_gdp": "FDI inflow (\\% GDP)", "tax_gdp": "Tax revenue (\\% GDP)", "ter_enr": "Tertiary enrolment (\\%)"}
L = ["\\begin{tabular}{lcccccc}", "\\toprule", "Candidate $M$ & $a$: $M$ on conn. & KP $F$ & $c$ & $c'$ & $b$: $M$ in Gini eq. & $c-c'$ \\\\", "\\midrule"]
for m_, lab in ml.items():
    a = conc[(conc.block == "mech_a") & (conc.outcome == m_)].iloc[0]
    c0 = conc[(conc.block == "mech_c") & (conc.outcome == f"ln_gini_mkt_{m_}") & (conc.term == "c")].iloc[0]
    cp = conc[(conc.block == "mech_c") & (conc.outcome == f"ln_gini_mkt_{m_}") & (conc.term == "cprime")].iloc[0]
    bm = conc[(conc.block == "mech_c") & (conc.outcome == f"ln_gini_mkt_{m_}") & (conc.term == "b_mediator")].iloc[0]
    L.append(f"{lab} & {cell(a.b, a.se, a.p, 2)} & {a.kpf:.0f} & {c0.b:.3f} & {cell(cp.b, cp.se, cp.p)} & {cell(bm.b, bm.se, bm.p, 4)} & {c0.b - cp.b:+.3f} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_mech.tex", "w").write("\n".join(L))

# ---------- T7 contribution ----------
L = ["\\begin{tabular}{lrrrrr}", "\\toprule", "Region & Countries & Mean $\\Delta\\ln\\mathrm{GACI}_{max}$ & Implied $\\Delta$Gini, OLS (pts) & Implied $\\Delta$Gini, 2SLS (pts) & Actual $\\Delta$Gini (pts) \\\\", "\\midrule"]
b_ols = main[(main.iv == "feyrer_int") & (main.treat == "ln_gaci_max") & (main.outcome == "ln_gini_mkt") & (main.model == "OLS")].b.iloc[0]
b_iv = main[(main.iv == "feyrer_int") & (main.treat == "ln_gaci_max") & (main.outcome == "ln_gini_mkt") & (main.model == "IV")].b.iloc[0]
cc = contrib_c.copy()
cc["ols_pts"] = cc.gini0 * (np.exp(b_ols * cc.dln_gaci) - 1); cc["iv_pts"] = cc.gini0 * (np.exp(b_iv * cc.dln_gaci) - 1)
names = {"AF": "Africa", "AS": "Asia", "EU": "Europe", "LA": "Latin America", "ME": "Middle East", "NA": "North America", "SW": "Oceania"}
for k, g in cc.groupby("cont"):
    L.append(f"{names.get(k, k)} & {len(g)} & {g.dln_gaci.mean():.3f} & {g.ols_pts.mean():.2f} & {g.iv_pts.mean():.2f} & {g.actual_pts.mean():.2f} \\\\")
L.append(f"\\midrule All & {len(cc)} & {cc.dln_gaci.mean():.3f} & {cc.ols_pts.mean():.2f} & {cc.iv_pts.mean():.2f} & {cc.actual_pts.mean():.2f} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_contribution.tex", "w").write("\n".join(L))
cc.round(3).to_csv("_contribution_bycountry.csv")

# ---------- T8 robustness ----------
rl = [("controls", "ctrl1", "Baseline (ln population)"), ("controls", "ctrl2", "+ ln GDP per capita"), ("controls", "ctrl3", "+ urban share"), ("controls", "ctrl4", "+ tertiary enrolment"),
      ("controls", "ctrl5", "+ trade/GDP"), ("controls", "ctrl6", "+ tax/GDP"), ("controls", "ctrl7", "+ ln sea market access"), ("controls", "ctrl8", "+ GDP pc, urban, tertiary, trade"),
      ("overid", "feyrer_tourism", "Both instruments (Hansen $J$ $p$ in col. 4)"), ("overid", "tourism_only", "Tourism instrument only"),
      ("se", "cluster_country", "SE clustered by country"), ("se", "cluster_cont_year", "SE two-way clustered continent, year"), ("se", "driscoll_kraay3", "Driscoll--Kraay SE (3 lags)"),
      ("sample", "drop_top10_hubs", "Drop ten leading hub economies"), ("sample", "pre2020", "1996--2019 only"), ("sample", "drop_crises", "Drop 2008--09 and 2020--21"),
      ("fe", "cont_x_year", "Continent $\\times$ year FE"), ("fe", "country_trends", "Country-specific linear trends")]
L = ["\\begin{tabular}{lcccc}", "\\toprule", "Specification & $\\ln G^{mkt}$ & $\\ln G^{disp}$ & KP $F$ / Hansen $p$ & N \\\\", "\\midrule"]
for blk, spec, lab in rl:
    a = rob[(rob.block == blk) & (rob.spec == spec) & (rob.outcome == "ln_gini_mkt")].iloc[0]
    d_ = rob[(rob.block == blk) & (rob.spec == spec) & (rob.outcome == "ln_gini_disp")].iloc[0]
    extra = f"{a.kpf:.1f}" + (f" / {a.hansenp:.2f}" if not pd.isna(a.hansenp) else "")
    L.append(f"{lab} & {cell(a.b, a.se, a.p)} & {cell(d_.b, d_.se, d_.p)} & {extra} & {int(a.N):,} \\\\")
L.append("\\addlinespace\\multicolumn{5}{l}{\\emph{Leave-one-continent-out (country and year FE)}}\\\\")
for cc_, lab in names.items():
    a = rob[(rob.block == "loo_cont") & (rob.spec == f"drop_{cc_}") & (rob.outcome == "ln_gini_mkt")]
    d_ = rob[(rob.block == "loo_cont") & (rob.spec == f"drop_{cc_}") & (rob.outcome == "ln_gini_disp")]
    if len(a): L.append(f"Drop {lab} & {cell(*a.iloc[0][['b', 'se', 'p']])} & {cell(*d_.iloc[0][['b', 'se', 'p']]) if len(d_) else '--'} & {a.iloc[0].kpf:.1f} & {int(a.iloc[0].N):,} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_robust.tex", "w").write("\n".join(L))

# ---------- T9 IV diagnostics ----------
L = ["\\begin{tabular}{lcccc}", "\\toprule", "Specification & Instrument & $\\ln G^{mkt}$ & $\\ln G^{disp}$ & KP $F$ \\\\", "\\midrule"]
dl = [("cont_x_year", "Continent $\\times$ year FE"), ("cont_x_year_dropLA", "Continent $\\times$ year FE, drop Latin America"), ("exposure_trends", "+ baseline exposures $\\times$ aviation index"),
      ("exposure_trends_contyear", "+ exposures $\\times$ index, continent $\\times$ year FE"), ("inc3_gini3_x_year", "Income tercile and Gini tercile $\\times$ year FE"), ("kitchen_sink", "All of the above")]
for spec, lab in dl:
    for ivv, ivlab in [("feyrer_int", "Feyrer"), ("tourism_int", "Tourism")]:
        a = diag[(diag.block == "pooled") & (diag.spec == ivv) & (diag.term == spec) & (diag.outcome == "ln_gini_mkt")].iloc[0]
        d_ = diag[(diag.block == "pooled") & (diag.spec == ivv) & (diag.term == spec) & (diag.outcome == "ln_gini_disp")].iloc[0]
        L.append(f"{lab if ivv == 'feyrer_int' else ''} & {ivlab} & {cell(a.b, a.se, a.p)} & {cell(d_.b, d_.se, d_.p)} & {a.kpf:.1f} \\\\")
a = diag[(diag.block == "pooled") & (diag.spec == "both") & (diag.term == "contyear_exposure_J") & (diag.outcome == "ln_gini_mkt")].iloc[0]
d_ = diag[(diag.block == "pooled") & (diag.spec == "both") & (diag.term == "contyear_exposure_J") & (diag.outcome == "ln_gini_disp")].iloc[0]
ja = diag[(diag.block == "pooled") & (diag.spec == "both") & (diag.term == "hansen_p") & (diag.outcome == "ln_gini_mkt")].b.iloc[0]
jd = diag[(diag.block == "pooled") & (diag.spec == "both") & (diag.term == "hansen_p") & (diag.outcome == "ln_gini_disp")].b.iloc[0]
L.append(f"Exposures $\\times$ index, continent $\\times$ year FE & Both & {cell(a.b, a.se, a.p)} & {cell(d_.b, d_.se, d_.p)} & {a.kpf:.1f} \\\\")
L.append(f"\\quad Hansen $J$ $p$-value & & {ja:.2f} & {jd:.2f} & \\\\")
oa = diag[(diag.block == "pooled") & (diag.spec == "OLS") & (diag.term == "kitchen_sink_FE") & (diag.outcome == "ln_gini_mkt")].iloc[0]
od = diag[(diag.block == "pooled") & (diag.spec == "OLS") & (diag.term == "kitchen_sink_FE") & (diag.outcome == "ln_gini_disp")].iloc[0]
L.append(f"OLS with all interacted FE & -- & {cell(oa.b, oa.se, oa.p)} & {cell(od.b, od.se, od.p)} & \\\\")
L.append("\\addlinespace\\multicolumn{5}{l}{\\emph{First stage by continent (coefficient on instrument, KP $F$)}}\\\\")
for cc_, lab in names.items():
    cells = []
    for ivv in ["feyrer_int", "tourism_int"]:
        r = diag[(diag.block == "fs_cont") & (diag.spec == ivv) & (diag.term == cc_)]
        cells.append(f"{r.iloc[0].b:.3f}{st(r.iloc[0].p)} [{r.iloc[0].kpf:.1f}]" if len(r) else "--")
    L.append(f"{lab} & Feyrer / Tourism & {cells[0]} & {cells[1]} & \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_diag.tex", "w").write("\n".join(L))

# ---------- T10 horizon + long differences ----------
L = ["\\begin{tabular}{lcccc}", "\\toprule", "Specification & $\\ln G^{mkt}$ & $\\ln G^{disp}$ & KP $F$ & N \\\\", "\\midrule",
     "\\multicolumn{5}{l}{\\emph{Panel A. Lagged connectivity, 2SLS (instrument lagged equally)}}\\\\"]
for k in [0, 1, 2, 3, 5, 7, 10]:
    a = ld[(ld.block == "lag") & (ld.spec == f"k{k}") & (ld.outcome == "ln_gini_mkt")].iloc[0]
    d_ = ld[(ld.block == "lag") & (ld.spec == f"k{k}") & (ld.outcome == "ln_gini_disp")].iloc[0]
    L.append(f"Lag {k} & {cell(a.b, a.se, a.p)} & {cell(d_.b, d_.se, d_.p)} & {a.kpf:.1f} & {int(a.N):,} \\\\")
L.append("\\addlinespace\\multicolumn{5}{l}{\\emph{Panel B. Long differences, cross-section with continent FE}}\\\\")
for pair in ["1996_2019", "2000_2019", "2005_2019", "2010_2019"]:
    for blk, lab in [("LD_OLS", "OLS"), ("LD_IV", "2SLS Feyrer"), ("LD_IVtour", "2SLS tourism")]:
        a = ld[(ld.block == blk) & (ld.spec == pair) & (ld.outcome == "ln_gini_mkt")].iloc[0]
        d_ = ld[(ld.block == blk) & (ld.spec == pair) & (ld.outcome == "ln_gini_disp")].iloc[0]
        kp = f"{a.kpf:.2f}" if not pd.isna(a.kpf) else ""
        L.append(f"{pair.replace('_', '--')}, {lab} & {cell(a.b, a.se, a.p)} & {cell(d_.b, d_.se, d_.p)} & {kp} & {int(a.N):,} \\\\")
for blk, lab in [("D5_OLS", "Stacked 5-year differences, OLS"), ("D5_IVtour", "Stacked 5-year differences, 2SLS tourism")]:
    a = ld[(ld.block == blk) & (ld.outcome == "ln_gini_mkt")].iloc[0]; d_ = ld[(ld.block == blk) & (ld.outcome == "ln_gini_disp")].iloc[0]
    kp = f"{a.kpf:.2f}" if not pd.isna(a.kpf) else ""
    L.append(f"{lab} & {cell(a.b, a.se, a.p)} & {cell(d_.b, d_.se, d_.p)} & {kp} & {int(a.N):,} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_horizon.tex", "w").write("\n".join(L))

# ---------- T11 open skies ----------
L = ["\\begin{tabular}{lcccc}", "\\toprule", "Outcome & DiD, country and year FE & DiD, continent $\\times$ year FE & Pre-trend joint $F$ ($p$) & N \\\\", "\\midrule"]
ol = {"ln_gaci_max": "ln GACI max", "ln_gaci_cwm": "ln GACI cwm", "ln_gaci_sum": "ln GACI sum", "ln_gini_mkt": "ln Gini, market", "ln_gini_disp": "ln Gini, disposable", "ln_bot50_wid": "ln bottom 50\\% share", "ln_top10_wid": "ln top 10\\% share"}
for yv, lab in ol.items():
    a = osk[(osk.block == "did") & (osk.outcome == yv)].iloc[0]; c_ = osk[(osk.block == "did_contyear") & (osk.outcome == yv)].iloc[0]
    f = osk[(osk.block == "es_pretrend_F") & (osk.outcome == yv)].iloc[0]
    L.append(f"{lab} & {cell(a.b, a.se, a.p)} & {cell(c_.b, c_.se, c_.p)} & {f.b:.2f} ({f.p:.2f}) & {int(a.N):,} \\\\")
L.append("\\addlinespace\\multicolumn{5}{l}{\\emph{Open Skies as instrument for ln GACI max (2SLS, clustered SE)}}\\\\")
for yv in ["ln_gini_mkt", "ln_gini_disp", "ln_bot50_wid", "ln_top10_wid"]:
    a = osk[(osk.block == "iv_os") & (osk.outcome == yv)]
    c_ = osk[(osk.block == "iv_os_contyear") & (osk.outcome == yv)]
    if len(a): L.append(f"{ol[yv]} & {cell(*a.iloc[0][['b', 'se', 'p']])} [KP $F$ {a.iloc[0].kpf:.1f}] & {cell(*c_.iloc[0][['b', 'se', 'p']]) if len(c_) else '--'} & & {int(a.iloc[0].N):,} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_openskies.tex", "w").write("\n".join(L))
print("assembled:", sorted(os.listdir("tables")))

# ================================================================== T12-T16 growth (GDP) tables
# Growth outcomes reported beside the distribution results. Specifications are the twins of
# the inequality tables: same panel, same instruments, same fixed effects, same samples.
GYL = [("ln_gdppc", "GDP per capita"), ("ln_avg_all_wid", "Average income"),
       ("ln_avg_top10_wid", "Top 10\\% average"), ("ln_avg_bot50_wid", "Bottom 50\\% average"),
       ("ln_ratio_avg", "Top/bottom gap")]


def g(block, outcome, spec, iv=None, treat=None):
    q = (gdp.block == block) & (gdp.outcome == outcome) & (gdp.spec == spec)
    if iv is not None: q &= (gdp.iv == iv)
    if treat is not None: q &= (gdp.treat == treat)
    r = gdp[q]
    return r.iloc[0] if len(r) else None


# ---------- T12 growth main ----------
L = ["\\begin{tabular}{lccccc}", "\\toprule",
     " & " + " & ".join(lab for _, lab in GYL) + " \\\\",
     " & $\\ln y$ & $\\ln \\bar{y}$ & $\\ln \\bar{y}^{t10}$ & $\\ln \\bar{y}^{b50}$ & $\\ln(\\bar{y}^{t10}/\\bar{y}^{b50})$ \\\\",
     "\\midrule"]
for tr, lab in labs.items():
    L.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{lab}}}}}\\\\")
    row = [cell(*g("main", yv, "OLS", "feyrer_int", tr)[["b", "se", "p"]]) for yv, _ in GYL]
    L.append("OLS & " + " & ".join(row) + " \\\\")
    for ivv, ivlab in [("feyrer_int", "2SLS, Feyrer IV"), ("tourism_int", "2SLS, tourism IV")]:
        row, row2 = [], []
        for yv, _ in GYL:
            o = g("main", yv, "IV", ivv, tr)
            oc = g("main", yv, "IVcl", ivv, tr)
            row.append(cell(o.b, o.se, o.p))
            row2.append(f"[{oc.se:.3f}]{st(oc.p)}")
        L.append(f"{ivlab} & " + " & ".join(row) + " \\\\")
        L.append(" & " + " & ".join(row2) + " \\\\")
    fr = [f"{g('main', yv, 'IV', 'feyrer_int', tr).kpf:.0f}; {g('main', yv, 'IV', 'tourism_int', tr).kpf:.0f}" for yv, _ in GYL]
    L.append("First-stage KP $F$ (Feyrer; tourism) & " + " & ".join(fr) + " \\\\")
    L.append("\\addlinespace")
L.append("\\multicolumn{6}{l}{\\emph{Panel D. Both instruments, $\\ln\\mathrm{GACI}_{max}$ (over-identified)}}\\\\")
row = [cell(*g("overid", yv, "feyrer_tourism")[["b", "se", "p"]]) for yv, _ in GYL]
L.append("2SLS, Feyrer and tourism & " + " & ".join(row) + " \\\\")
L.append("Hansen $J$ ($p$) & " + " & ".join(f"{g('overid', yv, 'feyrer_tourism').hansenp:.3f}" for yv, _ in GYL) + " \\\\")
L.append("\\midrule")
L.append("Country, Year FE & " + " & ".join(["Yes"] * 5) + " \\\\")
L.append("Observations & " + " & ".join(f"{int(g('main', yv, 'OLS', 'feyrer_int', 'ln_gaci_max').N):,}" for yv, _ in GYL) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables/tab_growth.tex", "w").write("\n".join(L))

# ---------- T13 growth incidence decomposition ----------
# ln(group average income) = ln(average income of all adults) + ln(group income share x scaling),
# so the level term is common to both groups and the share term carries the distribution.
def tl(outcome, model):
    r = tails[(tails.block == "tails") & (tails.treat == "ln_gaci_max") & (tails.outcome == outcome) & (tails.model == model)]
    return r.iloc[0] if len(r) else None


def mn(outcome, model):
    r = main[(main.iv == "feyrer_int") & (main.treat == "ln_gaci_max") & (main.outcome == outcome) & (main.model == model)]
    return r.iloc[0] if len(r) else None


L = ["\\begin{tabular}{lccc}", "\\toprule",
     " & Top 10\\% & Bottom 50\\% & Gap \\\\", "\\midrule"]
for model, plab in [("OLS", "Panel A. OLS"), ("IV", "Panel B. 2SLS, Feyrer instrument")]:
    L.append(f"\\multicolumn{{4}}{{l}}{{\\emph{{{plab}}}}}\\\\")
    a = g("main", "ln_avg_all_wid", model, "feyrer_int", "ln_gaci_max")
    L.append("(1) Average income, all adults & " + " & ".join([cell(a.b, a.se, a.p)] * 2) + " & -- \\\\")
    t10, b50, gap = tl("ln_top10_wid", model), tl("ln_bot50_wid", model), tl("ratio_t10_b50", model)
    L.append("(2) Group income share & " + " & ".join(cell(x.b, x.se, x.p) for x in [t10, b50, gap]) + " \\\\")
    st10 = g("main", "ln_avg_top10_wid", model, "feyrer_int", "ln_gaci_max")
    sb50 = g("main", "ln_avg_bot50_wid", model, "feyrer_int", "ln_gaci_max")
    sgap = g("main", "ln_ratio_avg", model, "feyrer_int", "ln_gaci_max")
    L.append("(3) Group average income $=(1)+(2)$ & " + " & ".join(cell(x.b, x.se, x.p) for x in [st10, sb50, sgap]) + " \\\\")
    gm = mn("ln_gini_mkt", model)
    L.append("Memo: market-income Gini & \\multicolumn{3}{c}{" + cell(gm.b, gm.se, gm.p) + "} \\\\")
    L.append("\\addlinespace")
L += ["\\midrule", "Country, Year FE & Yes & Yes & Yes \\\\",
      f"Observations & {int(st10.N):,} & {int(sb50.N):,} & {int(sgap.N):,} \\\\",
      "\\bottomrule", "\\end{tabular}"]
open("tables/tab_growth_decomp.tex", "w").write("\n".join(L))

# ---------- A. growth identification diagnostics ----------
GDL = [("ln_gdppc", "GDP per capita"), ("ln_avg_top10_wid", "Top 10\\% average"),
       ("ln_avg_bot50_wid", "Bottom 50\\% average"), ("ln_ratio_avg", "Top/bottom gap")]
L = ["\\begin{tabular}{lcccc}", "\\toprule", " & " + " & ".join(lab for _, lab in GDL) + " \\\\", "\\midrule"]
for ivv, ivlab in [("feyrer_int", "Feyrer instrument"), ("tourism_int", "Tourism-heritage instrument")]:
    L.append(f"\\multicolumn{{5}}{{l}}{{\\emph{{Panel. {ivlab}}}}}\\\\")
    for sp, slab in [("cont_x_year", "Continent $\\times$ year FE"),
                     ("cont_x_year_dropLA", "Continent $\\times$ year FE, drop Latin America"),
                     ("exposure_trend", "Baseline exposure $\\times$ global shifter"),
                     ("kitchen_sink", "Both, plus sea access and trade exposure")]:
        L.append(f"{slab} & " + " & ".join(cell(*g("diag", yv, sp, ivv)[["b", "se", "p"]]) for yv, _ in GDL) + " \\\\")
    L.append("First-stage KP $F$ & " + " & ".join(f"{g('diag', yv, 'cont_x_year', ivv).kpf:.1f}" for yv, _ in GDL) + " \\\\")
    L.append("\\addlinespace")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables_appendix/tabA_growth_diag.tex", "w").write("\n".join(L))

# ---------- A. growth horizon and leads ----------
L = ["\\begin{tabular}{lcccc}", "\\toprule", " & " + " & ".join(lab for _, lab in GDL) + " \\\\", "\\midrule",
     "\\multicolumn{5}{l}{\\emph{Panel A. Connectivity lagged $k$ years (2SLS, Feyrer instrument)}}\\\\"]
for k in range(11):
    L.append(f"$k={k}$ & " + " & ".join(cell(*g("lag", yv, f"k{k}")[["b", "se", "p"]]) for yv, _ in GDL) + " \\\\")
L.append("\\addlinespace\\multicolumn{5}{l}{\\emph{Panel B. Placebo, connectivity led $f$ years}}\\\\")
for k in range(1, 6):
    L.append(f"$f={k}$ & " + " & ".join(cell(*g("lead", yv, f"f{k}")[["b", "se", "p"]]) for yv, _ in GDL) + " \\\\")
L += ["\\midrule", "Country, Year FE & Yes & Yes & Yes & Yes \\\\", "\\bottomrule", "\\end{tabular}"]
open("tables_appendix/tabA_growth_horizon.tex", "w").write("\n".join(L))

# ---------- A. growth long differences ----------
L = ["\\begin{tabular}{lccccc}", "\\toprule", " & " + " & ".join(lab for _, lab in GDL) + " & KP $F$ \\\\", "\\midrule"]
for blk, blab in [("LD_OLS", "OLS"), ("LD_IV", "2SLS, Feyrer"), ("LD_IVtour", "2SLS, tourism")]:
    L.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{Panel. Long differences, {blab}}}}}\\\\")
    for pair in ["1996_2019", "1996_2023", "2000_2019", "2005_2019", "2010_2019"]:
        r0 = g(blk, "ln_gdppc", pair)
        kp = "--" if pd.isna(r0.kpf) else f"{r0.kpf:.1f}"
        L.append(f"{pair.replace('_', '--')} & " + " & ".join(cell(*g(blk, yv, pair)[["b", "se", "p"]]) for yv, _ in GDL) + f" & {kp} \\\\")
    L.append("\\addlinespace")
for blk, blab in [("D5_OLS", "Stacked 5-year differences, OLS"), ("D5_IV", "Stacked 5-year differences, 2SLS Feyrer")]:
    r0 = g(blk, "ln_gdppc", "stacked5")
    kp = "--" if pd.isna(r0.kpf) else f"{r0.kpf:.1f}"
    L.append(f"{blab} & " + " & ".join(cell(*g(blk, yv, "stacked5")[["b", "se", "p"]]) for yv, _ in GDL) + f" & {kp} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables_appendix/tabA_growth_longdiff.tex", "w").write("\n".join(L))

# ---------- A. growth heterogeneity and controls ----------
GHL = [("ln_gdppc", "GDP per capita"), ("ln_avg_top10_wid", "Top 10\\% average"), ("ln_avg_bot50_wid", "Bottom 50\\% average")]


def gh(block, outcome, treat):
    r = gdp[(gdp.block == block) & (gdp.outcome == outcome) & (gdp.treat == treat)]
    return r.iloc[0] if len(r) else None


L = ["\\begin{tabular}{lccc}", "\\toprule", " & " + " & ".join(lab for _, lab in GHL) + " \\\\", "\\midrule",
     "\\multicolumn{4}{l}{\\emph{Panel A. Baseline GDP per capita tercile (interaction IV)}}\\\\"]
for term, lab in [("ln_gaci_max", "Low tercile (base)"), ("mid_total", "Middle tercile (total)"),
                  ("high_total", "High tercile (total)"), ("ln_gaci_max_mid", "Interaction: middle"),
                  ("ln_gaci_max_high", "Interaction: high")]:
    L.append(f"{lab} & " + " & ".join(cell(*gh("inc3", yv, term)[["b", "se", "p"]]) for yv, _ in GHL) + " \\\\")
L.append("\\addlinespace\\multicolumn{4}{l}{\\emph{Panel B. Before and after 2010 (interaction IV)}}\\\\")
for term, lab in [("ln_gaci_max", "Pre-2010 (base)"), ("post_total", "Post-2010 (total)"), ("ln_gaci_max_post", "Interaction: post-2010")]:
    L.append(f"{lab} & " + " & ".join(cell(*gh("post2010", yv, term)[["b", "se", "p"]]) for yv, _ in GHL) + " \\\\")
L.append("\\addlinespace\\multicolumn{4}{l}{\\emph{Panel C. Separate 2SLS by continent}}\\\\")
cn2 = {"AF": "Africa", "AS": "Asia", "EU": "Europe", "LA": "Latin America", "ME": "Middle East", "NA": "North America", "SW": "Oceania"}
for cc, clab in cn2.items():
    rr = g("continent", "ln_gdppc", cc)
    if rr is None: continue
    L.append(f"{clab} ($N={int(rr.N):,}$) & " + " & ".join(cell(*g("continent", yv, cc)[["b", "se", "p"]]) for yv, _ in GHL) + " \\\\")
L.append("\\addlinespace\\multicolumn{4}{l}{\\emph{Panel D. Control sensitivity, 2SLS Feyrer, $\\ln\\mathrm{GACI}_{max}$}}\\\\")
ctl = {"ctrl1": "No controls beyond population", "ctrl2": "Plus urbanisation", "ctrl3": "Plus tertiary enrolment",
       "ctrl4": "Plus trade openness", "ctrl5": "Plus tax revenue share", "ctrl6": "Plus sea market access",
       "ctrl7": "Plus urbanisation, enrolment and openness"}
for sp, slab in ctl.items():
    a = g("controls", "ln_gdppc", sp)
    b = g("controls", "ln_avg_bot50_wid", sp)
    L.append(f"{slab} & {cell(a.b, a.se, a.p)} & -- & {cell(b.b, b.se, b.p)} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open("tables_appendix/tabA_growth_hetero.tex", "w").write("\n".join(L))

# ---------- A. inequality conditional on measured income ----------
L = ["\\begin{tabular}{lcc}", "\\toprule", " & $\\ln G^{mkt}$ & $\\ln G^{disp}$ \\\\", "\\midrule"]
for term, lab in [("ln_gaci_max", "$\\ln\\mathrm{GACI}_{max}$ (instrumented)"), ("ln_gdppc", "$\\ln$ GDP per capita")]:
    L.append(f"{lab} & " + " & ".join(cell(*gdp[(gdp.block == 'joint') & (gdp.outcome == yv) & (gdp.treat == term)].iloc[0][["b", "se", "p"]]) for yv in ["ln_gini_mkt", "ln_gini_disp"]) + " \\\\")
jn = gdp[(gdp.block == "joint") & (gdp.outcome == "ln_gini_mkt") & (gdp.treat == "ln_gaci_max")].iloc[0]
L += ["\\midrule", "Country, Year FE & Yes & Yes \\\\", f"First-stage KP $F$ & {jn.kpf:.1f} & {jn.kpf:.1f} \\\\",
      f"Observations & {int(jn.N):,} & {int(jn.N):,} \\\\", "\\bottomrule", "\\end{tabular}"]
open("tables_appendix/tabA_growth_condgdp.tex", "w").write("\n".join(L))
# ---------- A. total GDP as an outcome ----------
L = ["\\begin{tabular}{lccc}", "\\toprule",
     " & $\\ln\\mathrm{GACI}_{max}$ & $\\ln\\mathrm{GACI}_{cwm}$ & $\\ln\\mathrm{GACI}_{sum}$ \\\\", "\\midrule"]
TRS = ["ln_gaci_max", "ln_gaci_cwm", "ln_gaci_sum"]
L.append("OLS & " + " & ".join(cell(*g("main", "lngdp", "OLS", "feyrer_int", tr)[["b", "se", "p"]]) for tr in TRS) + " \\\\")
for ivv, ivlab in [("feyrer_int", "2SLS, Feyrer IV"), ("tourism_int", "2SLS, tourism IV")]:
    L.append(f"{ivlab} & " + " & ".join(cell(*g("main", "lngdp", "IV", ivv, tr)[["b", "se", "p"]]) for tr in TRS) + " \\\\")
    L.append(" & " + " & ".join(f"[{g('main', 'lngdp', 'IVcl', ivv, tr).se:.3f}]{st(g('main', 'lngdp', 'IVcl', ivv, tr).p)}" for tr in TRS) + " \\\\")
    L.append(f"First-stage KP $F$, {ivlab.split(',')[1].strip()} & " + " & ".join(f"{g('main', 'lngdp', 'IV', ivv, tr).kpf:.1f}" for tr in TRS) + " \\\\")
og = g("overid", "lngdp", "feyrer_tourism")
L.append("2SLS, both instruments & " + cell(og.b, og.se, og.p) + " & -- & -- \\\\")
L.append(f"Hansen $J$ ($p$) & {og.hansenp:.3f} & -- & -- \\\\")
L += ["\\midrule", "Country, Year FE & Yes & Yes & Yes \\\\",
      f"Observations & " + " & ".join([f"{int(g('main', 'lngdp', 'OLS', 'feyrer_int', 'ln_gaci_max').N):,}"] * 3) + " \\\\",
      "\\bottomrule", "\\end{tabular}"]
open("tables_appendix/tabA_growth_total.tex", "w").write("\n".join(L))
print("total GDP table written")
print("growth tables written")
