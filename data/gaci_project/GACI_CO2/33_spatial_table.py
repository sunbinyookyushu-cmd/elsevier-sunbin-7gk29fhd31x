# -*- coding: utf-8 -*-
"""
33_spatial_table.py   (2026-09-06)
Builds LaTeX fragments from _spatial_models.csv (32_spatial_models.py):
  tab:spatial      main text: bunker CO2, contiguity W, ML panel + IV panel
  tab:spatial_ext  Extended Data: inverse-distance W (bunker CO2) and
                   contiguity W for international CO2 and intensity (IV panel)
  tab:alloc        Extended Data: allocation rules (bunker / LTO / 50-50),
                   OLS and 2SLS by aggregation (from _allest_results_cl.csv,
                   _measures6_cl.csv)   [Junya: LTO and 50/50 to the appendix]
Output: _tex_spatial.tex
"""
import os, sys
import numpy as np
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
BS = chr(92)

res = pd.read_csv(os.path.join(HERE, "_spatial_models.csv"))

def stars(b, se):
    if not np.isfinite(se) or se <= 0:
        return ""
    z = abs(b / se)
    return "$^{***}$" if z > 2.576 else "$^{**}$" if z > 1.96 else "$^{*}$" if z > 1.645 else ""

def cell(b, se, dec=2):
    if not np.isfinite(b):
        return "--"
    if not np.isfinite(se):
        return f"{b:.{dec}f}"
    return f"{b:.{dec}f}{stars(b, se)} ({se:.{dec}f})"

def cell2(b, se, dec=2):
    """coefficient and s.e. on two rows (narrow columns)"""
    if not np.isfinite(b):
        return "--", ""
    if not np.isfinite(se):
        return f"{b:.{dec}f}", ""
    return f"{b:.{dec}f}{stars(b, se)}", f"({se:.{dec}f})"

def get(W, outc, model, est, term):
    r = res[(res.W == W) & (res.outcome == outc) & (res.model == model) & (res.estimator == est) & (res.term == term)]
    if len(r) == 0:
        return np.nan, np.nan, {}
    r = r.iloc[0]
    return float(r.b), float(r.se_cl), r.to_dict()

TERMS = [("beta", "ln GACI (own)"),
         ("theta", "W ln GACI (neighbours)"),
         ("rho", "W ln CO$_2$ (spatial lag, $\\rho$)"),
         ("lambda", "W $u$ (spatial error, $\\lambda$)"),
         ("direct", "Direct effect"),
         ("indirect", "Indirect effect"),
         ("total", "Total effect")]

def panel(W, outc, est, models, label_map):
    lines = []
    for term, tname in TERMS:
        vals = []; ses = []
        for m in models:
            e2 = est if est == "IV" else ("FE" if m in ("OLS", "SLX") else "ML")
            b, se, _ = get(W, outc, m, e2, term)
            v, s2 = cell2(b, se)
            vals.append(v); ses.append(s2)
        if all(v == "--" for v in vals):
            continue
        lines.append("  " + tname + " & " + " & ".join(vals) + " " + BS + BS)
        if any(ses):
            lines.append("   & " + " & ".join(ses) + " " + BS + BS)
    # first-stage F row (IV only)
    if est == "IV":
        vals = []
        for m in models:
            _, _, d = get(W, outc, m, "IV", "beta")
            f = d.get("swf_beta", np.nan)
            vals.append(f"{f:.1f}" if np.isfinite(f) else "--")
        lines.append("  First-stage $F$, own connectivity & " + " & ".join(vals) + " " + BS + BS)
    return lines

N = int(res["N"].iloc[0])
MODELS_A = ["OLS", "SLX", "SAR", "SEM", "SDM", "SDEM"]
MODELS_B = ["2SLS", "SLX", "SAR", "SEM", "SDM", "SDEM"]
HEAD_A = ["OLS-FE", "SLX", "SAR", "SEM", "SDM", "SDEM"]
HEAD_B = ["2SLS", "SLX-IV", "SAR-IV", "SEM-IV", "SDM-IV", "SDEM-IV"]

out = []
# ------------------------------------------------------------- tab:spatial
out.append("% ===== tab:spatial =====")
out.append(BS + "begin{table}[htbp]")
out.append(BS + "centering")
out.append(BS + "begin{threeparttable}")
out.append(BS + "caption{Spatial models of the connectivity elasticity: SLX, SAR, SEM and SDM}")
out.append(BS + "label{tab:spatial}")
out.append(BS + "footnotesize")
out.append(BS + "begin{tabular}{lcccccc}")
out.append(BS + "toprule")
out.append(" & " + " & ".join(HEAD_A) + " " + BS + BS)
out.append(" & (1) & (2) & (3) & (4) & (5) & (6) " + BS + BS)
out.append(BS + "midrule")
out.append(BS + "multicolumn{7}{l}{" + BS + "textit{Panel A. Connectivity treated as exogenous (OLS; ML for the spatial models)}} " + BS + BS)
out += panel("contig", "ln_co2_tot", "ML", MODELS_A, None)
out.append(BS + "midrule")
out.append(" & " + " & ".join(HEAD_B) + " " + BS + BS)
out.append(BS + "midrule")
out.append(BS + "multicolumn{7}{l}{" + BS + "textit{Panel B. Own connectivity instrumented (generalised spatial 2SLS)}} " + BS + BS)
out += panel("contig", "ln_co2_tot", "IV", MODELS_B, None)
out.append("  $N$ & " + " & ".join([f"{N:,}"] * 6) + " " + BS + BS)
out.append(BS + "bottomrule")
out.append(BS + "end{tabular}")
out.append(BS + "begin{tablenotes}[flushleft]")
out.append(BS + "footnotesize")
out.append(BS + "item Notes: Outcome is log bunker CO$_2$; country-year panel, 1996--2023, with country and year fixed effects, log population and log sea market access. W is the row-normalised land-contiguity matrix (Natural Earth boundaries; 39 sample countries have no land neighbour and receive a zero row), applied within each year. SLX adds the neighbours' average log GACI; SAR adds the neighbours' average log CO$_2$; SEM allows a spatially autoregressive error; SDM combines the spatial lag with the neighbours' connectivity; SDEM combines SLX with the spatial error. Panel A includes country and year fixed effects and estimates the spatial-lag and spatial-error models by maximum likelihood on the within-transformed data (log-determinant summed over the yearly blocks), with conventional standard errors from the Hessian (not clustered). Panel B instruments own connectivity with the Feyrer shifter, neighbours' connectivity with the identically weighted shifter, and the spatial lag of the outcome with the spatial lags of the instruments and of the exogenous controls (first and second order), in the manner of Kelejian and Prucha; the spatial-error parameter is estimated by their moments estimator from the 2SLS residuals (no standard error is reported for it) and the equation re-estimated on the transformed variables. Direct, indirect and total effects are the averages of the diagonal, off-diagonal row sums and row sums of $(I-\\rho W)^{-1}(\\beta I + \\theta W)$ over the yearly blocks; their standard errors are from 100 draws of the coefficient vector. First-stage $F$ is the Sanderson--Windmeijer conditional statistic for own connectivity. Standard errors clustered by country in parentheses (Panel B). $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.")
out.append(BS + "end{tablenotes}")
out.append(BS + "end{threeparttable}")
out.append(BS + "end{table}")
out.append("")

# --------------------------------------------------------- tab:spatial_ext
out.append("% ===== tab:spatial_ext =====")
out.append(BS + "begin{table}[htbp]")
out.append(BS + "centering")
out.append(BS + "begin{threeparttable}")
out.append(BS + "caption{Extended Data Table X: Spatial models under alternative weights and outcomes}")
out.append(BS + "label{tab:spatial_ext}")
out.append(BS + "scriptsize")
out.append(BS + "begin{tabular}{lcccccc}")
out.append(BS + "toprule")
out.append(" & " + " & ".join(HEAD_B) + " " + BS + BS)
out.append(BS + "midrule")
for (W, outc, title) in [("inv", "ln_co2_tot", "Panel A. Inverse-distance W (all countries, 100 km floor); log bunker CO$_2$"),
                         ("contig", "ln_co2_intl", "Panel B. Contiguity W; log international CO$_2$"),
                         ("contig", "ln_intensity", "Panel C. Contiguity W; log CO$_2$ per seat-km"),
                         ("inv", "ln_co2_intl", "Panel D. Inverse-distance W; log international CO$_2$"),
                         ("inv", "ln_intensity", "Panel E. Inverse-distance W; log CO$_2$ per seat-km")]:
    if len(res[(res.W == W) & (res.outcome == outc)]) == 0:
        continue
    out.append(BS + "multicolumn{7}{l}{" + BS + "textit{" + title + "}} " + BS + BS)
    out += panel(W, outc, "IV", MODELS_B, None)
    out.append(BS + "midrule")
out[-1] = BS + "bottomrule"
out.append(BS + "end{tabular}")
out.append(BS + "begin{tablenotes}[flushleft]")
out.append(BS + "scriptsize")
out.append("\\item Notes: Instrumented specifications as in Table~\\ref{tab:spatial}, Panel B, with the stated weight matrix and outcome; $N$ = " + f"{N:,}" + ". Under the inverse-distance weighting the own and neighbour shifters are nearly collinear within country, so the own-connectivity first stage is weak and the estimates are reported for completeness. Standard errors clustered by country in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.")
out.append(BS + "end{tablenotes}")
out.append(BS + "end{threeparttable}")
out.append(BS + "end{table}")
out.append("")

# --------------------------------------------------------------- tab:alloc
alle = pd.read_csv(os.path.join(HERE, "_allest_results_cl.csv"))
m6 = pd.read_csv(os.path.join(HERE, "_measures6_cl.csv"))
def a(est, outc):
    r = alle[(alle.est == est) & (alle.outc == outc)].iloc[0]
    return float(r.b), float(r.se), float(r.kpf) if np.isfinite(r.kpf) else np.nan, int(r.nn)
def m(meas, outc):
    r = m6[(m6.meas == meas) & (m6.outc == outc)].iloc[0]
    return float(r.b), float(r.se), float(r.kpf), int(r.nn)
OUTC = ["ln_co2_tot", "ln_co2_lto", "ln_co2_5050"]
out.append("% ===== tab:alloc =====")
out.append(BS + "begin{table}[htbp]")
out.append(BS + "centering")
out.append(BS + "begin{threeparttable}")
out.append(BS + "caption{Extended Data Table X: Allocation of emissions to countries: bunker, territorial (LTO) and 50/50 rules}")
out.append(BS + "label{tab:alloc}")
out.append(BS + "footnotesize")
out.append(BS + "begin{tabular}{lccc}")
out.append(BS + "toprule")
out.append(" & Bunker CO$_2$ & LTO CO$_2$ & 50/50 CO$_2$ " + BS + BS)
out.append(" & (1) & (2) & (3) " + BS + BS)
out.append(BS + "midrule")
rows_spec = [("Panel A. OLS", lambda o: a("OLS", o), "ln GACI (cwm)", False),
             ("Panel B. 2SLS, Feyrer instrument, capacity-weighted mean", lambda o: a("FeyrerIV", o), "ln GACI (cwm)", True),
             ("Panel C. 2SLS, GACI sum", lambda o: m("lng", o), "ln GACI (sum)", True),
             ("Panel D. 2SLS, GACI max", lambda o: m("ln_gaci_max", o), "ln GACI (max)", True),
             ("Panel E. 2SLS, GACI mean", lambda o: m("ln_gaci_mean", o), "ln GACI (mean)", True)]
for title, fn, vname, hasF in rows_spec:
    out.append(BS + "multicolumn{4}{l}{" + BS + "textit{" + title + "}} " + BS + BS)
    vals = [fn(o) for o in OUTC]
    out.append("  " + vname + " & " + " & ".join(f"{b:.3f}{stars(b, se)}" for b, se, f, n in vals) + " " + BS + BS)
    out.append("   & " + " & ".join(f"({se:.3f})" for b, se, f, n in vals) + " " + BS + BS)
    if hasF:
        out.append("  KP $F$ & " + " & ".join(f"{f:.1f}" for b, se, f, n in vals) + " " + BS + BS)
    out.append("  $N$ & " + " & ".join(f"{n:,}" for b, se, f, n in vals) + " " + BS + BS)
    out.append(BS + "midrule")
out[-1] = BS + "bottomrule"
out.append(BS + "end{tabular}")
out.append(BS + "begin{tablenotes}[flushleft]")
out.append(BS + "footnotesize")
out.append("\\item Notes: Specifications as in Table~\\ref{tab:main}. Column (1) repeats the headline bunker measure (all cruise plus departure-side LTO assigned to the departure country); column (2) uses landing-and-take-off emissions only (territorial rule); column (3) splits cruise emissions equally between the endpoint countries. The three rules give elasticities within 0.3 of one another under every aggregation of airport connectivity. Standard errors clustered by country in parentheses; the Kleibergen--Paap $F$ is cluster-robust. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.")
out.append(BS + "end{tablenotes}")
out.append(BS + "end{threeparttable}")
out.append(BS + "end{table}")

txt = "\n".join(out) + "\n"
open(os.path.join(HERE, "_tex_spatial.tex"), "w", encoding="utf-8").write(txt)
print("saved _tex_spatial.tex", len(txt))
# quick console summary
print(res[(res.W == "contig") & (res.outcome == "ln_co2_tot")][["model", "estimator", "term", "b", "se_cl", "se_rob"]].round(3).to_string())
