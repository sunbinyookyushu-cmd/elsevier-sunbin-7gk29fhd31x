# -*- coding: utf-8 -*-
"""
13_make_tex_tables.py
Overleaf-ready tables for the CO2 paper, generated from the result CSVs.
One table per results block, panels combined inside a single table (not split).
Output: co2_tables_20260826.tex (compilable standalone; each table also
usable via \\input after stripping the preamble).
"""
import math
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "co2_tables_20260826.tex")

def star(p):
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return ""
    return "$^{***}$" if p < .01 else ("$^{**}$" if p < .05 else ("$^{*}$" if p < .1 else ""))

def f3(x):
    return f"{x:.3f}"

ae = pd.read_csv(os.path.join(HERE, "_allest_results.csv"))
m6 = pd.read_csv(os.path.join(HERE, "_measures6.csv"))
spn = pd.read_csv(os.path.join(HERE, "_spillover_nbr.csv"))
spm = pd.read_csv(os.path.join(HERE, "_spillover_mech.csv"))
mp = pd.read_csv(os.path.join(HERE, "_mediation_co2.csv"))
mi = pd.read_csv(os.path.join(HERE, "_mediation_imai.csv"))
het = pd.read_csv(os.path.join(HERE, "_feyrer_hetero.csv"))
tmp = pd.read_csv(os.path.join(HERE, "_temporal_co2.csv"))

# fix Stata -x^2 Sobel gap
for i in mp.index:
    if pd.isna(mp.loc[i, "sobel_se"]):
        a, sa, b, sb = mp.loc[i, ["a", "sa", "b", "sb"]]
        sse = math.sqrt(a * a * sb * sb + b * b * sa * sa)
        mp.loc[i, "sobel_se"] = sse
        mp.loc[i, "sobel_p"] = math.erfc(abs(a * b / sse) / 2**0.5)

OUTC = ["ln_co2_tot", "ln_co2_lto", "ln_co2_5050", "ln_co2_intl", "ln_skm", "ln_intensity"]

L = []
L.append(r"""\documentclass[11pt]{article}
\usepackage[margin=2.2cm]{geometry}
\usepackage{booktabs}
\usepackage{threeparttable}
\usepackage{amsmath}
\usepackage{graphicx}
\begin{document}
""")

# ================= Table 1: main =================
def panel_block(sub, coeflab, kpf=True):
    b = "  " + coeflab + " & " + " & ".join(f3(sub.loc[o, "b"]) + star(sub.loc[o, "p"]) for o in OUTC) + r" \\"
    s = "   & " + " & ".join(f"({f3(sub.loc[o,'se'])})" for o in OUTC) + r" \\"
    rows = [b, s]
    if kpf and "kpf" in sub.columns and sub["kpf"].notna().any():
        rows.append("  KP $F$ & " + " & ".join(f"{sub.loc[o,'kpf']:.1f}" for o in OUTC) + r" \\")
    rows.append("  $N$ & " + " & ".join(f"{int(sub.loc[o,'nn']):,}" for o in OUTC) + r" \\")
    return rows

L.append(r"""\begin{table}[htbp]
\centering
\begin{threeparttable}
\caption{Air connectivity and aviation CO$_2$: main results}
\label{tab:main}
\footnotesize
\begin{tabular}{lcccccc}
\toprule
 & \multicolumn{1}{c}{Bunker CO$_2$} & \multicolumn{1}{c}{LTO CO$_2$} & \multicolumn{1}{c}{50/50 CO$_2$} & \multicolumn{1}{c}{Intl.\ CO$_2$} & \multicolumn{1}{c}{Seat-km} & \multicolumn{1}{c}{Intensity} \\
 & (1) & (2) & (3) & (4) & (5) & (6) \\
\midrule
\multicolumn{7}{l}{\textit{Panel A. OLS}} \\""")
L += panel_block(ae[ae["est"] == "OLS"].set_index("outc"), r"ln GACI (cwm)", kpf=False)
L.append(r"\midrule" + "\n" + r"\multicolumn{7}{l}{\textit{Panel B. 2SLS, Feyrer instrument, capacity-weighted mean}} \\")
L += panel_block(ae[ae["est"] == "FeyrerIV"].set_index("outc"), r"ln GACI (cwm)")
for meas, lbl, cl in [("lng", "Panel C. 2SLS, GACI sum", "ln GACI (sum)"),
                      ("ln_gaci_max", "Panel D. 2SLS, GACI max", "ln GACI (max)"),
                      ("ln_gaci_mean", "Panel E. 2SLS, GACI mean", "ln GACI (mean)")]:
    L.append(r"\midrule" + "\n" + r"\multicolumn{7}{l}{\textit{" + lbl + r"}} \\")
    L += panel_block(m6[m6["meas"] == meas].set_index("outc"), cl)
L.append(r"""\bottomrule
\end{tabular}
\begin{tablenotes}[flushleft]
\footnotesize
\item Notes: Country-year panel, 1996--2023. All specifications include country and year fixed effects and control for log population and log sea market access. Outcomes are in logs: total aviation CO$_2$ under the bunker convention (all cruise plus departure-side LTO assigned to the departure country), landing-and-take-off CO$_2$ only, CO$_2$ with cruise split 50/50 between endpoint countries, bunker CO$_2$ from international flights, scheduled departing seat-kilometres, and CO$_2$ per seat-km. The instrument in Panels B--E interacts world aviation technology with air-versus-sea geography (Feyrer-type). Robust standard errors in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.
\end{tablenotes}
\end{threeparttable}
\end{table}
""")

# ================= Table 2: spillover =================
SOUT = ["ln_co2_tot", "ln_co2_intl", "ln_intensity", "g_vol"]
nb = spn[spn["var"] == "nbr_lngaci"].set_index("outc")
ow = spn[spn["var"] == "feyrer_int"].set_index("outc")
sm = spm.set_index("outc")
MOUT = ["ln_flights", "ln_skm", "ln_gauge", "ln_stage", "intl_share"]
L.append(r"""\begin{table}[htbp]
\centering
\begin{threeparttable}
\caption{Connectivity spillovers: neighbouring countries' connectivity and own aviation outcomes}
\label{tab:spillover}
\footnotesize
\begin{tabular}{lccccc}
\toprule
\multicolumn{6}{l}{\textit{Panel A. 2SLS: neighbour connectivity instrumented}} \\
 & \multicolumn{1}{c}{Bunker CO$_2$} & \multicolumn{1}{c}{Intl.\ CO$_2$} & \multicolumn{1}{c}{Intensity} & \multicolumn{1}{c}{Trade volume} & \\
 & (1) & (2) & (3) & (4) & \\
\midrule""")
L.append(r"  ln neighbour GACI & " + " & ".join(f3(nb.loc[o, "b"]) + star(nb.loc[o, "p"]) for o in SOUT) + r" & \\")
L.append(r"   & " + " & ".join(f"({f3(nb.loc[o,'se'])})" for o in SOUT) + r" & \\")
L.append(r"  Own Feyrer shifter & " + " & ".join(f3(ow.loc[o, "b"]) + star(ow.loc[o, "p"]) for o in SOUT) + r" & \\")
L.append(r"   & " + " & ".join(f"({f3(ow.loc[o,'se'])})" for o in SOUT) + r" & \\")
L.append(r"  KP $F$ & " + " & ".join(f"{nb.loc[o,'kpf']:.1f}" for o in SOUT) + r" & \\")
L.append(r"  $N$ & " + " & ".join(f"{int(nb.loc[o,'nn']):,}" for o in SOUT) + r" & \\")
L.append(r"""\midrule
\multicolumn{6}{l}{\textit{Panel B. Margins of the own response to neighbour connectivity (same specification)}} \\
 & \multicolumn{1}{c}{Flights} & \multicolumn{1}{c}{Seat-km} & \multicolumn{1}{c}{Aircraft size} & \multicolumn{1}{c}{Stage length} & \multicolumn{1}{c}{Intl.\ share} \\
 & (1) & (2) & (3) & (4) & (5) \\
\midrule""")
L.append(r"  ln neighbour GACI & " + " & ".join(f3(sm.loc[o, "b"]) + star(sm.loc[o, "p"]) for o in MOUT) + r" \\")
L.append(r"   & " + " & ".join(f"({f3(sm.loc[o,'se'])})" for o in MOUT) + r" \\")
L.append(r"""\bottomrule
\end{tabular}
\begin{tablenotes}[flushleft]
\footnotesize
\item Notes: Neighbour connectivity is the inverse-distance-weighted average of all other countries' log GACI (capacity-weighted mean), with weights based on haversine distances between countries' aviation activity centroids. It is instrumented by the identically weighted average of other countries' Feyrer shifters; the own Feyrer shifter enters directly, so the own-connectivity effect is in reduced form. Own and neighbour connectivity cannot be jointly instrumented because the two shifters are collinear within country. All specifications include country and year fixed effects and control for log population and log sea market access. Robust standard errors in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.
\end{tablenotes}
\end{threeparttable}
\end{table}
""")

# ================= Table 3: mediation =================
med_lab = {"ln_flights": "Flight frequency", "ln_skm": "Seat-kilometres", "intl_share": "International share"}
L.append(r"""\begin{table}[htbp]
\centering
\begin{threeparttable}
\caption{Causal mediation of the connectivity effect on aviation CO$_2$}
\label{tab:mediation}
\footnotesize
\begin{tabular}{lccccc}
\toprule
\multicolumn{6}{l}{\textit{Panel A. Instrumental-variable product of coefficients (2SLS scale; total effect 5.669)}} \\
Mediator & $a$: GACI$\rightarrow M$ & $b$: $M\rightarrow$CO$_2$ & ACME ($a\times b$) & Sobel $p$ & Share mediated \\
\midrule""")
for _, r in mp.iterrows():
    L.append(f"  {med_lab[r['med']]} & {f3(r['a'])} & {f3(r['b'])} & {f3(r['acme'])} & "
             f"{r['sobel_p']:.3f} & {100*r['prop']:.1f}\\% \\\\")
L.append(r"""\midrule
\multicolumn{6}{l}{\textit{Panel B. Imai, Keele and Yamamoto (2010) mediation (OLS scale; total effect 3.582)}} \\
Mediator & ACME & Direct effect & Total effect & & Share mediated \\
\midrule""")
for _, r in mi.iterrows():
    L.append(f"  {med_lab[r['med']]} & {f3(r['acme'])} & {f3(r['ade'])} & {f3(r['tau'])} & & "
             f"{100*r['prop']:.1f}\\% \\\\")
L.append(r"""\bottomrule
\end{tabular}
\begin{tablenotes}[flushleft]
\footnotesize
\item Notes: Outcome is log total bunker CO$_2$; the treatment is log GACI (capacity-weighted mean). Panel A instruments the treatment with the Feyrer shifter in each equation and combines the paths by the product method with delta-method (Sobel) standard errors. Panel B implements the algorithm of Imai, Keele and Yamamoto (2010) by quasi-Bayesian simulation (200 draws) on least-squares models with country and year indicator variables. Each row is a separate single-mediator analysis and the mediators overlap, so shares do not sum across rows. All models control for log population and log sea market access. Sequential ignorability of the mediator is assumed conditional on the fixed effects.
\end{tablenotes}
\end{threeparttable}
\end{table}
""")

# ================= Table 4: heterogeneity =================
het = het[~het["grp"].str.startswith("interact")]
glab = {"inc_low": "Low income", "inc_mid": "Middle income", "inc_high": "High income",
        "con_low": "Low connectivity", "con_mid": "Middle connectivity", "con_high": "High connectivity",
        "Europe": "Europe", "AsiaPacific": "Asia--Pacific", "Africa": "Africa", "LatAm": "Latin America",
        "MiddleEast": "Middle East", "NorthAm": "North America"}
pan_lab = {"A_income": "Panel A. Total CO$_2$ by baseline income tercile",
           "B_conn": "Panel B. Total CO$_2$ by baseline connectivity tercile",
           "C_region": "Panel C. Total CO$_2$ by region",
           "D_intens": "Panel D. Intensity by baseline income tercile"}
L.append(r"""\begin{table}[htbp]
\centering
\begin{threeparttable}
\caption{Heterogeneity of the connectivity elasticity}
\label{tab:hetero}
\footnotesize
\begin{tabular}{lcccc}
\toprule
 & Coefficient & s.e. & KP $F$ & $N$ \\
\midrule""")
for pk in ["A_income", "B_conn", "C_region", "D_intens"]:
    L.append(r"\multicolumn{5}{l}{\textit{" + pan_lab[pk] + r"}} \\")
    for _, r in het[het["panel"] == pk].iterrows():
        if r["grp"] in ("MiddleEast", "NorthAm"):
            L.append(f"  {glab[r['grp']]} & \\multicolumn{{4}}{{c}}{{not identified (KP $F<2$)}} \\\\")
            continue
        L.append(f"  {glab[r['grp']]} & {f3(r['b'])}{star(r['p'])} & ({f3(r['se'])}) & "
                 f"{r['KPF']:.1f} & {int(r['N']):,} \\\\")
    if pk != "D_intens":
        L.append(r"\midrule")
L.append(r"""\bottomrule
\end{tabular}
\begin{tablenotes}[flushleft]
\footnotesize
\item Notes: Split-sample 2SLS with the Feyrer instrument; terciles are formed on 1996 values. All specifications include country and year fixed effects and control for log population and log sea market access. The Middle East and North America cells have too little instrument variation for inference. Robust standard errors in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.
\end{tablenotes}
\end{threeparttable}
\end{table}
""")

# ================= Table 5: temporal =================
TOUT = ["ln_co2_tot", "ln_co2_intl", "ln_skm", "ln_intensity"]
L.append(r"""\begin{table}[htbp]
\centering
\begin{threeparttable}
\caption{Temporal split of the connectivity elasticity}
\label{tab:temporal}
\footnotesize
\begin{tabular}{lcccc}
\toprule
 & \multicolumn{1}{c}{Bunker CO$_2$} & \multicolumn{1}{c}{Intl.\ CO$_2$} & \multicolumn{1}{c}{Seat-km} & \multicolumn{1}{c}{Intensity} \\
 & (1) & (2) & (3) & (4) \\
\midrule""")
tmp8 = pd.read_csv(os.path.join(HERE, "_temporal_pre2008.csv"))
tmpxc = pd.read_csv(os.path.join(HERE, "_temporal_excovid.csv"))
tpanels = [
    (tmp[tmp["period"] == "full"], "Panel A. Full sample, 1996--2023"),
    (tmp8[tmp8["samp"] == "1996-2007"], "Panel B. Network-expansion era, 1996--2007"),
    (tmpxc[tmpxc["samp"] == "2010-2023_exCOVID"],
     r"Panel C. Mature-network era, 2010--2023 (excl.\ 2020--2021)"),
    (tmp[tmp["period"] == "1996-2009"], "Panel D. Unrestricted split: 1996--2009"),
    (tmp[tmp["period"] == "2010-2023"], "Panel E. Unrestricted split: 2010--2023 (weak first stage)"),
]
for pi, (sub, lbl) in enumerate(tpanels):
    sub = sub.set_index("outc")
    L.append(r"\multicolumn{5}{l}{\textit{" + lbl + r"}} \\")
    L.append(r"  ln GACI (cwm) & " + " & ".join(f3(sub.loc[o, "b"]) + star(sub.loc[o, "p"]) for o in TOUT) + r" \\")
    L.append(r"   & " + " & ".join(f"({f3(sub.loc[o,'se'])})" for o in TOUT) + r" \\")
    L.append(r"  KP $F$ & " + " & ".join(f"{sub.loc[o,'kpf']:.1f}" for o in TOUT) + r" \\")
    L.append(r"  $N$ & " + " & ".join(f"{int(sub.loc[o,'nn']):,}" for o in TOUT) + r" \\")
    if pi < len(tpanels) - 1:
        L.append(r"\midrule")
L.append(r"""\bottomrule
\end{tabular}
\begin{tablenotes}[flushleft]
\footnotesize
\item Notes: 2SLS with the Feyrer instrument; specifications as in Table~\ref{tab:main}. Panels B and C split the sample at its midpoint (2010) and exclude the crisis years: Panel B ends before the global financial crisis (2008--2009) and Panel C drops the COVID-19 collapse (2020--2021). Both subperiods are strongly identified and the elasticity in each is above one; the pre-versus-post difference for total CO$_2$ is 2.61 ($p = 0.005$). Panels D and E report the unrestricted split for reference: the weak first stage in Panel E (KP $F = 7.0$) is driven by the COVID years, whose exclusion in Panel C restores $F$ to 36.7, so the small point estimates in Panel E reflect a contaminated first stage rather than a vanished effect. Robust standard errors in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.
\end{tablenotes}
\end{threeparttable}
\end{table}
""")

# ================= Figures =================
FIGS = [
    ("CO2_map_attributed_2023.png", "fig:attributed",
     "Aviation CO$_2$ attributed to post-1996 connectivity growth, 2023 (Mt). "
     "White denotes zero; the attribution applies the Feyrer-instrument elasticity to each country's connectivity change."),
    ("CO2_map_dlngaci.png", "fig:dlngaci",
     "Change in log air connectivity (GACI, capacity-weighted mean), 1996--2023."),
    ("CO2_map_levels_2023.png", "fig:levels",
     "Aviation CO$_2$ levels under the bunker convention, 2023."),
    ("CO2_map_mismatch_2023.png", "fig:mismatch",
     "Attribution mismatch, 2023: bunker-attributed share minus physical LTO share (percentage points). "
     "Positive values indicate international hub countries; negative values indicate domestically oriented networks."),
    ("CO2_map_carbonprice.png", "fig:carbonprice",
     "Carbon intensity of connectivity gains (g CO$_2$ per USD of trade gain; heritage-instrument pipeline)."),
    ("CO2_efficiency_curve.png", "fig:effcurve",
     "Airport-level efficiency curve, 2023: median kg CO$_2$ per 1{,}000 seat-km by connectivity ventile, "
     "with the international share of seat-km on the second panel."),
    ("CO2_hetero_coefplot.png", "fig:hetero",
     "Heterogeneity of the connectivity elasticity (2SLS, Feyrer instrument). Filled markers denote $p<0.05$; "
     "bars are 95 percent confidence intervals. The Middle East and North America are omitted as unidentified."),
    ("CO2_temporal_coefplot.png", "fig:temporal",
     "Temporal split of the connectivity elasticity. Within each outcome, markers show the full sample, "
     "the network-expansion era (1996--2007), the mature-network era (2010--2023 excluding the COVID-19 years "
     "2020--2021), and the unrestricted 2010--2023 sample from left to right; gray denotes the unrestricted "
     "later sample, whose first stage (KP $F=7$) is contaminated by the COVID collapse."),
    ("CO2_saf_scenarios.png", "fig:saf",
     "World aviation CO$_2$ under ReFuelEU-style SAF blending paths."),
    ("CO2_rf_quintile.png", "fig:rfquintile",
     "Reduced-form quintile slopes under the tourism shifter: effects are concentrated in low-income, "
     "low-connectivity quintiles."),
]
L.append(r"\clearpage")
for fn, lbl, cap in FIGS:
    L.append(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\textwidth]{""" + fn + r"""}
\caption{""" + cap + r"""}
\label{""" + lbl + r"""}
\end{figure}
""")

L.append(r"\end{document}")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("saved:", OUT)
