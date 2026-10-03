# -*- coding: utf-8 -*-
"""
24_spill_tables_figs.py   (LZ comment 3, 2026-09-03)
From _spill_bands.csv, _spill_supp.csv, _spill_placebo_perm.csv, _spill_placebo_summary.csv:
  - tab:spillover (main text): Panel A joint IV, own and neighbour connectivity, W variants
                               Panel B own-vs-neighbour margins (contiguity, joint IV)
  - tab:spill_ext (ED): Panel C distance profile (single bands, kernel grid)
                        Panel D regional, region-by-year FE, inference and placebo
  - CO2_spill_decay.png: band and kernel coefficient profiles
  - tab:hetero regenerated from _feyrer_hetero_tot.csv (total CO2) -> _tex_hetero_tot.tex
Writes _tex_spill.tex
"""
import os, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SUF = os.environ.get("CLSUF", "")  # "_cl" selects country-clustered result files
SENOTE = "standard errors clustered by country" if SUF else "heteroskedasticity-robust standard errors"
SENOTE_C = "Standard errors clustered by country" if SUF else "Robust standard errors"

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"], "font.size": 11, "axes.linewidth": 0.8, "mathtext.fontset": "stix"})
ACC, GRAY, INK, NEG = "#1F4E79", "#9AA0A6", "#1f1f1f", "#B5651D"
def star(p):
    return "" if (p is None or (isinstance(p, float) and math.isnan(p))) else ("$^{***}$" if p < .01 else ("$^{**}$" if p < .05 else ("$^{*}$" if p < .1 else "")))
def c(b, se, p, nd=2):
    return f"{b:.{nd}f}{star(p)} ({se:.{nd}f})"

sb = pd.read_csv(os.path.join(HERE, "_spill_bands" + SUF + ".csv"))
sp = pd.read_csv(os.path.join(HERE, "_spill_supp.csv"))  # already holds robust and country-clustered rows
def gb(panel, item, var):
    r = sb[(sb.panel == panel) & (sb.item == item) & (sb["var"] == var)]; return r.iloc[0] if len(r) else None
def gs(panel, item, var):
    r = sp[(sp.panel == panel) & (sp.item == item) & (sp["var"] == var)]; return r.iloc[0] if len(r) else None
summ = None
if os.path.exists(os.path.join(HERE, "_spill_placebo_summary.csv")):
    summ = pd.read_csv(os.path.join(HERE, "_spill_placebo_summary.csv"), index_col=0)
inv = pd.read_csv(os.path.join(HERE, "_spill_placebo_perm.csv"))
p_inv = float((inv["rf_t"].abs() >= abs(inv["rft_actual"].iloc[0])).mean())
def pperm(W):
    if summ is not None and W in summ.index:
        return float(summ.loc[W, "p_perm_t"])
    return float("nan")

# ---------------- main table ----------------
L = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}",
     r"\caption{Connectivity spillovers: own and neighbouring countries' connectivity, jointly instrumented}", r"\label{tab:spillover}", r"\footnotesize",
     r"\begin{tabular}{lccccc}", r"\toprule",
     r"\multicolumn{6}{l}{\textit{Panel A. Log bunker CO$_2$; own and neighbour connectivity both instrumented}} \\",
     r"Neighbour definition & Own ln GACI & Neighbour ln GACI & SW $F$ (own / nbr) & KP $F$ & $N$ \\", r"\midrule"]
for W, lbl in [("contig", "Contiguous countries (land border)"), ("knn5", "Five nearest countries"), ("b1", "Countries within 500 km"), ("k1000", "Kernel $\\exp(-d/1000\\,\\mathrm{km})$"), ("inv", "Inverse distance, all countries")]:
    o = gb("A", f"joint_{W}", "ln_gaci_cwm"); nb = gb("A", f"joint_{W}", f"nbr_g_{W}")
    if o is None: continue
    sw = f"{o.swf:.0f} / {nb.swf:.0f}" if not math.isnan(o.swf) else "--"
    L.append(f"  {lbl} & {c(o.b, o.se, o.p)} & {c(nb.b, nb.se, nb.p)} & {sw} & {o.kpf:.1f} & {int(o.nn):,} \\\\")
    oc = gs("JOINT", f"{W}_country", "ln_gaci_cwm"); nc = gs("JOINT", f"{W}_country", f"nbr_g_{W}")
    if oc is not None and not SUF:
        L.append(f"  \\quad s.e.\\ clustered by country & ({oc.se:.2f}) & ({nc.se:.2f}) & & & \\\\")
ar = pd.read_csv(os.path.join(HERE, "_spill_cluster_ar.csv"))
def ga(item, var):
    r = ar[(ar.item == item) & (ar["var"] == var)]; return r.iloc[0] if len(r) else None
L.append(r"\midrule")
L.append(r"\multicolumn{6}{l}{\textit{Neighbour connectivity instrumented, own shifter in reduced form; s.e.\ clustered by country; AR = Anderson--Rubin 95\% set}} \\")
L.append(r"Neighbour definition & Own shifter (RF) & Neighbour ln GACI & AR set & KP $F$ & $N$ \\")
for W, lbl in [("contig", "Contiguous countries"), ("contig_rxy", "Contiguous, sub-region $\\times$ year FE"), ("b1", "Countries within 500 km"), ("knn5", "Five nearest countries")]:
    key = f"single_{W}_isocode" if not W.endswith("_rxy") else f"single_{W.replace('_rxy','')}_isocode_rxy"
    v = f"nbr_g_{W.replace('_rxy','')}"
    r = ga(key, v)
    if r is None: continue
    a = ga(f"single_{W.replace('_rxy','')}_AR", v)
    arset = f"[{a.ar_lo:.1f}, {a.ar_hi:.1f}]" if (a is not None and not W.endswith("_rxy") and not math.isnan(a.ar_lo)) else "--"
    L.append(f"  {lbl} & controlled & {c(r.b, r.se, r.p)} & {arset} & {r.kpf:.1f} & {int(r.nn):,} \\\\")
for W, lbl in [("contig", "Contiguous, joint 2SLS (own and neighbour instrumented)"), ("b1", "Within 500 km, joint 2SLS")]:
    r = ga(f"joint_{W}_isocode", f"nbr_g_{W}"); o = ga(f"joint_{W}_isocode", "ln_gaci_cwm")
    if r is None: continue
    L.append(f"  {lbl} & own {c(o.b, o.se, o.p)} & {c(r.b, r.se, r.p)} & [{r.ar_lo:.1f}, {r.ar_hi:.1f}] & {r.kpf:.1f} (SW {r.swf_own:.1f} / {r.swf_nbr:.1f}) & {int(r.nn):,} \\\\")
h = gb("A", "hybrid_rf_control", "nbr_g_inv"); hf = gb("A", "hybrid_rf_control", "feyrer_int"); hc = gb("E", "cluster_country", "nbr_g_inv")
L.append(f"  Inverse distance, own shifter in reduced form (previous specification) & RF {c(hf.b, hf.se, hf.p)} & {c(h.b, h.se, h.p)} & -- & {h.kpf:.1f} & {int(h.nn):,} \\\\")
L.append(f"  \\quad s.e.\\ clustered by country & & ({hc.se:.2f}) & & & \\\\")
L.append(r"\midrule")
L.append(r"\multicolumn{6}{l}{\textit{Panel B. Margins of the response, contiguity definition, joint 2SLS}} \\")
L.append(r"Outcome & Own ln GACI & Neighbour ln GACI & & KP $F$ & $N$ \\")
L.append(r"\midrule")
for yv, lbl in [("ln_co2_tot", "Bunker CO$_2$"), ("ln_co2_intl", "International CO$_2$"), ("ln_co2_dom", "Domestic CO$_2$"), ("ln_skm", "Seat-km"), ("ln_flights", "Flights"),
                ("ln_gauge", "Seats per flight"), ("ln_stage", "Km per flight"), ("ln_intensity", "CO$_2$ per seat-km"), ("intl_share", "International share of seat-km")]:
    o = gs("MECH", f"{yv}_robust", "ln_gaci_cwm"); nb = gs("MECH", f"{yv}_robust", "nbr_g_contig")
    oc = gs("MECH", f"{yv}_country", "ln_gaci_cwm"); nc = gs("MECH", f"{yv}_country", "nbr_g_contig")
    if o is None: continue
    if SUF:
        L.append(f"  {lbl} & {c(oc.b, oc.se, oc.p)} & {c(nc.b, nc.se, nc.p)} & & {oc.kpf:.1f} & {int(oc.nn):,} \\\\")
    else:
        L.append(f"  {lbl} & {c(o.b, o.se, o.p)} [{oc.se:.2f}] & {c(nb.b, nb.se, nb.p)} [{nc.se:.2f}] & & {o.kpf:.1f} & {int(o.nn):,} \\\\")
L += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Neighbour connectivity is the leave-out average of other countries' log GACI (capacity-weighted mean) under the stated weighting; it is instrumented by the identically weighted average of their Feyrer shifters, and own connectivity by the own shifter. All specifications include country and year fixed effects, log population, log sea market access and an indicator for countries with no neighbour under the definition (31 countries have no land neighbour). SW $F$ is the Sanderson--Windmeijer conditional first-stage statistic for each endogenous regressor. " + ("Standard errors clustered by country in parentheses." if SUF else "Heteroskedasticity-robust standard errors in parentheses; country-clustered standard errors in brackets or on the following line.") + " The middle block of Panel A instruments neighbour connectivity only, with the own shifter as a control, and reports country-clustered standard errors and Anderson--Rubin 95 percent sets obtained by grid inversion (for the joint rows, the subset Anderson--Rubin set for the neighbour coefficient with own connectivity instrumented under each null); SW $F$ in that block is cluster-robust. The last row is the specification of the previous draft with all-country inverse-distance weights. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent" + ("" if SUF else " (robust)") + ".",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_main = "\n".join(L)

# ---------------- ED table: distance profile, regional, placebo ----------------
E = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}",
     r"\caption{Extended Data Table: Spatial structure of the connectivity spillover}", r"\label{tab:spill_ext}", r"\scriptsize",
     r"\begin{tabular}{lcccc}", r"\toprule",
     r"\multicolumn{5}{l}{\textit{Panel A. One neighbour definition at a time (neighbour connectivity instrumented; own shifter in reduced form)}} \\",
     r" & Neighbour ln GACI & KP $F$ & RMSE & $N$ \\", r"\midrule"]
for it, v, lbl in [("band_single", "nbr_g_contig", "Contiguous countries"), ("band_single", "nbr_g_b1", "0--500 km"), ("band_single", "nbr_g_b2", "500--1,000 km"), ("band_single", "nbr_g_b3", "1,000--2,000 km"),
                   ("band_single", "nbr_g_b4", "2,000--5,000 km"), ("band_single", "nbr_g_b5", "Beyond 5,000 km")]:
    r = gb("B", it, v); E.append(f"  {lbl} & {c(r.b, r.se, r.p)} & {r.kpf:.1f} & & {int(r.nn):,} \\\\")
for lam in [250, 500, 1000, 2000, 5000]:
    r = gb("B", "kernel", f"nbr_g_k{lam}"); rm = gb("B", "kernel_rmse", f"k{lam}")
    E.append(f"  Kernel $\\exp(-d/\\lambda)$, $\\lambda$ = {lam:,} km & {c(r.b, r.se, r.p)} & {r.kpf:.1f} & {rm.b:.4f} & {int(r.nn):,} \\\\")
E.append(r"\midrule")
E.append(r"\multicolumn{5}{l}{\textit{Panel B. Regional exposure and region-by-year fixed effects}} \\")
E.append(r" & Coefficient & KP $F$ & & $N$ \\")
r1 = gb("C", "bloc_inout", "nbr_g_inbloc"); r2 = gb("C", "bloc_inout", "nbr_g_outbloc")
E.append(f"  Within aviation bloc (leave-out mean) & {c(r1.b, r1.se, r1.p)} & {r1.kpf:.1f} & & {int(r1.nn):,} \\\\")
E.append(f"  Outside bloc (inverse-distance weighted), same regression & {c(r2.b, r2.se, r2.p)} & & & \\\\")
r1 = gb("C", "subregion_inout", "nbr_g_inreg"); r2 = gb("C", "subregion_inout", "nbr_g_outreg")
E.append(f"  Within UN sub-region (leave-out mean) & {c(r1.b, r1.se, r1.p)} & {r1.kpf:.1f} & & {int(r1.nn):,} \\\\")
E.append(f"  Outside sub-region, same regression & {c(r2.b, r2.se, r2.p)} & & & \\\\")
r = gs("RXY", "contig_robust", "nbr_g_contig"); rc = gs("RXY", "contig_country", "nbr_g_contig"); rs = gs("RXY", "contig_subregion", "nbr_g_contig")
E.append(f"  Contiguous, joint 2SLS, sub-region $\\times$ year FE & {c(r.b, r.se, r.p)} [{rc.se:.2f}] \\{{{rs.se:.2f}\\}} & {r.kpf:.1f} & & {int(r.nn):,} \\\\")
r = gb("C", "regionXyear_contig", "nbr_g_contig")
E.append(f"  Contiguous, own shifter in reduced form, sub-region $\\times$ year FE & {c(r.b, r.se, r.p)} & {r.kpf:.1f} & & {int(r.nn):,} \\\\")
r = gb("C", "regionXyear_k500", "nbr_g_k500")
E.append(f"  Kernel 500 km, own shifter in reduced form, sub-region $\\times$ year FE & {c(r.b, r.se, r.p)} & {r.kpf:.1f} & & {int(r.nn):,} \\\\")
r = gb("C", "regionXyear_inv", "nbr_g_inv")
E.append(f"  Inverse distance, own shifter in reduced form, sub-region $\\times$ year FE & {c(r.b, r.se, r.p)} & {r.kpf:.1f} & & {int(r.nn):,} \\\\")
E.append(r"\midrule")
E.append(r"\multicolumn{5}{l}{\textit{Panel C. Permutation placebo: countries relabelled at random in the weight matrix (500 draws)}} \\")
E.append(r" & Actual $t$ & Permutation $p$ & s.d.\ of permuted $t$ & \\")
E.append(f"  Inverse distance (reduced form on the neighbour shifter) & {inv['rft_actual'].iloc[0]:.2f} & {p_inv:.3f} & {inv['rf_t'].std():.2f} & \\\\")
if summ is not None:
    for W, lbl in [("contig", "Contiguous countries (joint 2SLS, neighbour coefficient)"), ("knn5", "Five nearest countries (joint 2SLS, neighbour coefficient)")]:
        if W in summ.index:
            E.append(f"  {lbl} & {summ.loc[W, 't_actual']:.2f} & {summ.loc[W, 'p_perm_t']:.3f} & {summ.loc[W, 'perm_t_sd']:.2f} & \\\\")
E += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\scriptsize",
      r"\item Notes: Panel A enters one neighbour exposure at a time (each instrumented by its own weighted shifter) with the own Feyrer shifter as a control; bands are leave-out means over countries whose aviation centroids fall in the stated distance range, with an indicator for empty bands. Panel B: aviation blocs are the EU/EEA single market, ASEAN, GCC, Mercosur, North America, ECOWAS, EAC/SADC, CIS, the Andean and Central American group, South Asia and Oceania; sub-regions follow the UN M49 classification. " + ("Standard errors clustered by country in parentheses (sub-region-clustered in braces where shown)." if SUF else "Robust standard errors in parentheses, country-clustered in brackets and sub-region-clustered in braces.") + " Panel C permutes country labels in the weight matrix, rebuilds the exposures and re-estimates; the $p$-value is the share of draws whose $|t|$ exceeds the actual. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent" + ("" if SUF else " (robust)") + ".",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_ed = "\n".join(E)

# ---------------- decay figure ----------------
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
ax = axes[0]
items = [("nbr_g_contig", "Contiguous"), ("nbr_g_b1", "0-500 km"), ("nbr_g_b2", "500-1,000"), ("nbr_g_b3", "1,000-2,000"), ("nbr_g_b4", "2,000-5,000"), ("nbr_g_b5", ">5,000")]
for i, (v, lbl) in enumerate(items):
    r = gb("B", "band_single", v)
    ax.errorbar(i, r.b, yerr=1.96 * r.se, fmt="o", color=ACC, mfc=(ACC if r.p < .05 else "white"), mec=ACC, ms=7, capsize=3, elinewidth=1.2)
ax.axhline(0, color=GRAY, lw=0.9, ls="--"); ax.set_xticks(range(len(items))); ax.set_xticklabels([l for _, l in items], fontsize=9.5)
ax.set_ylabel("Coefficient on neighbour ln GACI (2SLS)"); ax.set_title("A. One distance band at a time", loc="left", fontsize=11.5)
ax.spines[["top", "right"]].set_visible(False)
ax = axes[1]
lams = [250, 500, 1000, 2000, 5000]
for i, lam in enumerate(lams):
    r = gb("B", "kernel", f"nbr_g_k{lam}")
    ax.errorbar(i, r.b, yerr=1.96 * r.se, fmt="o", color=ACC, mfc=(ACC if r.p < .05 else "white"), mec=ACC, ms=7, capsize=3, elinewidth=1.2)
ax.axhline(0, color=GRAY, lw=0.9, ls="--"); ax.set_xticks(range(len(lams))); ax.set_xticklabels([f"{l:,} km" for l in lams], fontsize=9.5)
ax.set_xlabel("Kernel scale $\\lambda$ in $\\exp(-d/\\lambda)$"); ax.set_title("B. Continuous kernel, widening spatial reach", loc="left", fontsize=11.5)
ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Spatial profile of the spillover (filled = p<0.05; bars = 95% CI; own shifter controlled)", fontsize=12, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.96]); fig.savefig(os.path.join(HERE, "CO2_spill_decay.png"), dpi=200); plt.close(fig)
print("saved CO2_spill_decay.png")

with open(os.path.join(HERE, "_tex_spill" + SUF + ".tex"), "w", encoding="utf-8") as f:
    f.write("% ===== tab:spillover (main) =====\n" + tex_main + "\n\n% ===== tab:spill_ext (ED) =====\n" + tex_ed + "\n")
print("wrote _tex_spill.tex")

# ---------------- ED hetero table from total-CO2 results ----------------
h = pd.read_csv(os.path.join(HERE, "_feyrer_hetero_tot" + SUF + ".csv"))
def gh(panel, grp):
    r = h[(h.panel == panel) & (h.grp == grp)]; return r.iloc[0] if len(r) else None
H = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Extended Data Table 2: Heterogeneity of the connectivity elasticity}", r"\label{tab:hetero}", r"\footnotesize",
     r"\begin{tabular}{lcccc}", r"\toprule", r" & Coefficient & s.e. & KP $F$ & $N$ \\", r"\midrule"]
for title, panel, grps in [("Panel A. Total CO$_2$ by baseline income tercile", "A_income", [("inc_low", "Low income"), ("inc_mid", "Middle income"), ("inc_high", "High income")]),
                           ("Panel B. Total CO$_2$ by baseline connectivity tercile", "B_conn", [("con_low", "Low connectivity"), ("con_mid", "Middle connectivity"), ("con_high", "High connectivity (weak first stage)")]),
                           ("Panel C. Total CO$_2$ by region", "C_region", [("Europe", "Europe"), ("AsiaPacific", "Asia--Pacific"), ("Africa", "Africa"), ("LatAm", "Latin America")]),
                           ("Panel D. Intensity by baseline income tercile", "D_intens", [("inc_low", "Low income"), ("inc_mid", "Middle income"), ("inc_high", "High income")])]:
    H.append(r"\multicolumn{5}{l}{\textit{" + title + r"}} \\")
    for g, lbl in grps:
        r = gh(panel, g); H.append(f"  {lbl} & {r.b:.3f}{star(r.p)} & ({r.se:.3f}) & {r.KPF:.1f} & {int(r.N):,} \\\\")
    if panel == "C_region":
        H.append(r"  Middle East & \multicolumn{4}{c}{not identified (KP $F<2$)} \\")
        H.append(r"  North America & \multicolumn{4}{c}{not identified (KP $F<2$)} \\")
    if panel in ("A_income", "B_conn"):
        ri = gh(panel, "interact_hi")
        H.append(f"  \\quad Pooled interaction, top tercile $\\times$ ln GACI & {ri.b:.3f}{star(ri.p)} & ({ri.se:.3f}) & {ri.KPF:.1f} & {int(ri.N):,} \\\\")
    H.append(r"\midrule")
H = H[:-1]
H += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Split-sample 2SLS with the Feyrer instrument on log total bunker CO$_2$ (Panels A--C) and log CO$_2$ per seat-km (Panel D); terciles are formed on 1996 values. All specifications include country and year fixed effects and control for log population and log sea market access. The Middle East and North America cells have too little instrument variation for inference. " + SENOTE_C + " in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
with open(os.path.join(HERE, "_tex_hetero_tot" + SUF + ".tex"), "w", encoding="utf-8") as f:
    f.write("\n".join(H) + "\n")
print("wrote _tex_hetero_tot.tex")
print("DONE_24")
