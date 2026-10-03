# -*- coding: utf-8 -*-
"""
30_main_temporal_cl.py   (2026-09-03) Country-clustered versions of Table 1
(tab:main), ED Table 1 (tab:temporal) and ED Table 3 (tab:mediation, Panel A),
mirroring 13_make_tex_tables.py but reading the *_cl.csv result files.
Writes _tex_main_cl.tex
"""
import os, math, sys
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SUF = os.environ.get("CLSUF", "_cl")
def star(p):
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return ""
    return "$^{***}$" if p < .01 else ("$^{**}$" if p < .05 else ("$^{*}$" if p < .1 else ""))
def f3(x):
    return f"{x:.3f}"
ae = pd.read_csv(os.path.join(HERE, "_allest_results" + SUF + ".csv"))
m6 = pd.read_csv(os.path.join(HERE, "_measures6" + SUF + ".csv"))
tmp = pd.read_csv(os.path.join(HERE, "_temporal_co2" + SUF + ".csv"))
tmp8 = pd.read_csv(os.path.join(HERE, "_temporal_pre2008" + SUF + ".csv"))
tmpxc = pd.read_csv(os.path.join(HERE, "_temporal_excovid" + SUF + ".csv"))
mp = pd.read_csv(os.path.join(HERE, "_mediation_co2" + SUF + ".csv"))
mi = pd.read_csv(os.path.join(HERE, "_mediation_imai.csv"))
OUTC = ["ln_co2_tot", "ln_co2_lto", "ln_co2_5050", "ln_co2_intl", "ln_skm", "ln_intensity"]
SENOTE = "Standard errors clustered by country in parentheses"

def panel_block(sub, coeflab, kpf=True):
    b = "  " + coeflab + " & " + " & ".join(f3(sub.loc[o, "b"]) + star(sub.loc[o, "p"]) for o in OUTC) + r" \\"
    s = "   & " + " & ".join(f"({f3(sub.loc[o,'se'])})" for o in OUTC) + r" \\"
    rows = [b, s]
    if kpf and "kpf" in sub.columns and sub["kpf"].notna().any():
        rows.append("  KP $F$ & " + " & ".join(f"{sub.loc[o,'kpf']:.1f}" for o in OUTC) + r" \\")
    rows.append("  $N$ & " + " & ".join(f"{int(sub.loc[o,'nn']):,}" for o in OUTC) + r" \\")
    return rows

L = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Air connectivity and aviation CO$_2$: main results}", r"\label{tab:main}", r"\footnotesize",
     r"\begin{tabular}{lcccccc}", r"\toprule",
     r" & \multicolumn{1}{c}{Bunker CO$_2$} & \multicolumn{1}{c}{LTO CO$_2$} & \multicolumn{1}{c}{50/50 CO$_2$} & \multicolumn{1}{c}{Intl.\ CO$_2$} & \multicolumn{1}{c}{Seat-km} & \multicolumn{1}{c}{Intensity} \\",
     r" & (1) & (2) & (3) & (4) & (5) & (6) \\", r"\midrule", r"\multicolumn{7}{l}{\textit{Panel A. OLS}} \\"]
L += panel_block(ae[ae["est"] == "OLS"].set_index("outc"), r"ln GACI (cwm)", kpf=False)
L.append(r"\midrule"); L.append(r"\multicolumn{7}{l}{\textit{Panel B. 2SLS, Feyrer instrument, capacity-weighted mean}} \\")
L += panel_block(ae[ae["est"] == "FeyrerIV"].set_index("outc"), r"ln GACI (cwm)")
for meas, lbl, cl in [("lng", "Panel C. 2SLS, GACI sum", "ln GACI (sum)"), ("ln_gaci_max", "Panel D. 2SLS, GACI max", "ln GACI (max)"), ("ln_gaci_mean", "Panel E. 2SLS, GACI mean", "ln GACI (mean)")]:
    L.append(r"\midrule"); L.append(r"\multicolumn{7}{l}{\textit{" + lbl + r"}} \\")
    L += panel_block(m6[m6["meas"] == meas].set_index("outc"), cl)
L += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Country-year panel, 1996--2023. All specifications include country and year fixed effects and control for log population and log sea market access. Outcomes are in logs: total aviation CO$_2$ under the bunker convention (all cruise plus departure-side LTO assigned to the departure country), landing-and-take-off CO$_2$ only, CO$_2$ with cruise split 50/50 between endpoint countries, bunker CO$_2$ from international flights, scheduled departing seat-kilometres, and CO$_2$ per seat-km. The instrument in Panels B--E interacts world aviation technology with air-versus-sea geography (Feyrer-type). " + SENOTE + r"; the Kleibergen--Paap $F$ is cluster-robust. Heteroskedasticity-robust results are in Supplementary Table~\ref{tab:exclusion2}. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_main = "\n".join(L)

TOUT = ["ln_co2_tot", "ln_co2_intl", "ln_skm", "ln_intensity"]
T = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Extended Data Table 1: Temporal split of the connectivity elasticity}", r"\label{tab:temporal}", r"\footnotesize",
     r"\begin{tabular}{lcccc}", r"\toprule",
     r" & \multicolumn{1}{c}{Bunker CO$_2$} & \multicolumn{1}{c}{Intl.\ CO$_2$} & \multicolumn{1}{c}{Seat-km} & \multicolumn{1}{c}{Intensity} \\", r" & (1) & (2) & (3) & (4) \\", r"\midrule"]
tpanels = [(tmp[tmp["period"] == "full"], "Panel A. Full sample, 1996--2023"), (tmp8[tmp8["samp"] == "1996-2007"], "Panel B. Network-expansion era, 1996--2007"),
           (tmpxc[tmpxc["samp"] == "2010-2023_exCOVID"], r"Panel C. Mature-network era, 2010--2023 (excl.\ 2020--2021)"),
           (tmp[tmp["period"] == "1996-2009"], "Panel D. Unrestricted split: 1996--2009"), (tmp[tmp["period"] == "2010-2023"], "Panel E. Unrestricted split: 2010--2023 (weak first stage)")]
for pi, (sub, lbl) in enumerate(tpanels):
    sub = sub.set_index("outc")
    T.append(r"\multicolumn{5}{l}{\textit{" + lbl + r"}} \\")
    T.append(r"  ln GACI (cwm) & " + " & ".join(f3(sub.loc[o, "b"]) + star(sub.loc[o, "p"]) for o in TOUT) + r" \\")
    T.append(r"   & " + " & ".join(f"({f3(sub.loc[o,'se'])})" for o in TOUT) + r" \\")
    T.append(r"  KP $F$ & " + " & ".join(f"{sub.loc[o,'kpf']:.1f}" for o in TOUT) + r" \\")
    T.append(r"  $N$ & " + " & ".join(f"{int(sub.loc[o,'nn']):,}" for o in TOUT) + r" \\")
    if pi < len(tpanels) - 1:
        T.append(r"\midrule")
fb = tmp8[tmp8["samp"] == "1996-2007"].set_index("outc").loc["ln_co2_tot"]; fc = tmpxc[tmpxc["samp"] == "2010-2023_exCOVID"].set_index("outc").loc["ln_co2_tot"]
fe = tmp[tmp["period"] == "2010-2023"].set_index("outc").loc["ln_co2_tot"]
T += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: 2SLS with the Feyrer instrument; specifications as in Table~\ref{tab:main}. Panels B and C split the sample at its midpoint (2010) and exclude the crisis years: Panel B ends before the global financial crisis (2008--2009) and Panel C drops the COVID-19 collapse (2020--2021). Panels D and E report the unrestricted split for reference; the weak first stage in Panel E (KP $F$ = " + f"{fe.kpf:.1f}" + r") is driven by the COVID years, whose exclusion in Panel C restores $F$ to " + f"{fc.kpf:.1f}" + r". " + SENOTE + r"; Kleibergen--Paap $F$ statistics are cluster-robust. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_temp = "\n".join(T)
print("temporal: B %.2f (%.2f) F %.1f | C %.2f (%.2f) F %.1f | E F %.1f" % (fb.b, fb.se, fb.kpf, fc.b, fc.se, fc.kpf, fe.kpf))

# mediation Panel A (clustered), Panel B unchanged (IKY, OLS scale)
for i in mp.index:
    if pd.isna(mp.loc[i, "sobel_se"]):
        a, sa, b, sb = mp.loc[i, ["a", "sa", "b", "sb"]]
        sse = math.sqrt(a * a * sb * sb + b * b * sa * sa)
        mp.loc[i, "sobel_se"] = sse; mp.loc[i, "sobel_p"] = math.erfc(abs(a * b / sse) / 2 ** 0.5)
mlab = {"ln_flights": "Flight frequency", "ln_skm": "Seat-kilometres", "intl_share": "International share"}
tot = float(mp["ctot"].iloc[0])
M = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Extended Data Table 3: Causal mediation of the connectivity effect on aviation CO$_2$}", r"\label{tab:mediation}", r"\footnotesize",
     r"\begin{tabular}{lccccc}", r"\toprule",
     r"\multicolumn{6}{l}{\textit{Panel A. Instrumental-variable product of coefficients (2SLS scale; total effect " + f"{tot:.3f}" + r")}} \\",
     r"Mediator & $a$: GACI$\rightarrow M$ & $b$: $M\rightarrow$CO$_2$ & ACME ($a\times b$) & Sobel $p$ & Share mediated \\", r"\midrule"]
for _, r in mp.iterrows():
    M.append(f"  {mlab.get(r['med'], r['med'])} & {r['a']:.3f} & {r['b']:.3f} & {r['acme']:.3f} & {r['sobel_p']:.3f} & {100*r['prop']:.1f}\\% \\\\")
M.append(r"\midrule")
itot = float(mi["tau"].mean())
M.append(r"\multicolumn{6}{l}{\textit{Panel B. Imai, Keele and Yamamoto (2010) mediation (OLS scale; total effect " + f"{itot:.3f}" + r")}} \\")
M.append(r"Mediator & ACME & Direct effect & Total effect & & Share mediated \\"); M.append(r"\midrule")
for _, r in mi.iterrows():
    M.append(f"  {mlab.get(r['med'], r['med'])} & {r['acme']:.3f} & {r['ade']:.3f} & {r['tau']:.3f} & & {100*r['prop']:.1f}\\% \\\\")
M += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Outcome is log total bunker CO$_2$; the treatment is log GACI (capacity-weighted mean). Panel A instruments the treatment with the Feyrer shifter in each equation (standard errors clustered by country) and combines the paths by the product method with delta-method (Sobel) standard errors. Panel B implements the algorithm of Imai, Keele and Yamamoto (2010) by quasi-Bayesian simulation (200 draws) on least-squares models with country and year indicator variables. Each row is a separate single-mediator analysis and the mediators overlap, so shares do not sum across rows. All models control for log population and log sea market access. Sequential ignorability of the mediator is assumed conditional on the fixed effects.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_med = "\n".join(M)
with open(os.path.join(HERE, "_tex_main" + SUF + ".tex"), "w", encoding="utf-8") as f:
    f.write("% ===== tab:main =====\n" + tex_main + "\n\n% ===== tab:temporal =====\n" + tex_temp + "\n\n% ===== tab:mediation =====\n" + tex_med + "\n")
fi = ae[ae["est"] == "FeyrerIV"].set_index("outc")
print("main: " + "; ".join(f"{o} {fi.loc[o,'b']:.3f} ({fi.loc[o,'se']:.3f}) F {fi.loc[o,'kpf']:.1f}" for o in OUTC))
print("DONE_30")
