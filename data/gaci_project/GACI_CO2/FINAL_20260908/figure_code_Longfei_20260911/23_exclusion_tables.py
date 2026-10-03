# -*- coding: utf-8 -*-
"""
23_exclusion_tables.py   (LZ comment 4, 2026-09-03)
From _exclusion_suite.csv:
  - tab:exclusion  (ED / Methods) five panels: A placebo outcomes, B cycle content,
                   C placebo instrument, D zero first stage, E control path
  - tab:exclusion2 (SI) alternative shifters, leads, overidentification, SE variants
  - CO2_placebo_rf.png  reduced-form comparison bar chart
Writes _tex_exclusion.tex
"""
import os, math
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SUF = os.environ.get("CLSUF", "")  # "_cl" selects country-clustered result files
SENOTE = "standard errors clustered by country" if SUF else "heteroskedasticity-robust standard errors"
SENOTE_C = "Standard errors clustered by country" if SUF else "Robust standard errors"

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"], "font.size": 11, "axes.linewidth": 0.8})
ACC, GRAY, INK, NEG = "#1F4E79", "#9AA0A6", "#1f1f1f", "#B5651D"
def star(p):
    return "" if (p is None or (isinstance(p, float) and math.isnan(p))) else ("$^{***}$" if p < .01 else ("$^{**}$" if p < .05 else ("$^{*}$" if p < .1 else "")))
def c3(b, se, p):
    return f"{b:.3f}{star(p)} ({se:.3f})"
def c2(b, se, p):
    return f"{b:.2f}{star(p)} ({se:.2f})"

d = pd.read_csv(os.path.join(HERE, "_exclusion_suite" + SUF + ".csv"))
def get(panel, item, stat):
    r = d[(d.panel == panel) & (d.item == item) & (d.stat == stat)]
    return r.iloc[0] if len(r) else None

# ---------------- Panel A rows ----------------
A = [("ln_co2_tot", "Aviation CO$_2$ (total, our series)"), ("ln_co2_intl", "Aviation CO$_2$ (international)"),
     ("ln_co2_exav", "Territorial fossil CO$_2$ excl.\\ domestic aviation (GCP/OWID)"), ("ln_oil_exav", "Oil CO$_2$ excl.\\ domestic aviation (OWID)"),
     ("ln_ed_transp_exav", "Transport CO$_2$ excl.\\ domestic aviation (EDGAR)"), ("ln_ed_power", "Power industry CO$_2$ (EDGAR)"),
     ("ln_ed_build", "Buildings CO$_2$ (EDGAR)"), ("ln_ed_indcomb", "Industrial combustion CO$_2$ (EDGAR)"),
     ("ln_coal", "Coal CO$_2$ (OWID)"), ("ln_gas", "Gas CO$_2$ (OWID)"), ("ln_cement", "Cement CO$_2$ (OWID)"), ("ln_ed_agri", "Agriculture CO$_2$ (EDGAR)")]
L = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}",
     r"\caption{Extended Data Table: Exclusion-restriction diagnostics for the Feyrer instrument}", r"\label{tab:exclusion}", r"\scriptsize",
     r"\begin{tabular}{lcccc}", r"\toprule",
     r" & Reduced form & 2SLS & KP $F$ & $N$ \\", r"\midrule",
     r"\multicolumn{5}{l}{\textit{Panel A. Outcomes: coefficient on the instrument (reduced form) and on log GACI (2SLS)}} \\"]
for k, lbl in A:
    rf = get("A", k, "RF"); iv = get("A", k, "IV")
    if rf is None: continue
    L.append(f"  {lbl} & {c3(rf.b, rf.se, rf.p)} & {c2(iv.b, iv.se, iv.p) if iv is not None else '--'} & {iv.f:.1f} & {int(rf.nn):,} \\\\")
L.append(r"\midrule")
L.append(r"\multicolumn{5}{l}{\textit{Panel B. Content of the global cycle: first stage of the aviation-technology instrument with rival cycle $\times$ geography added}} \\")
L.append(r" & First-stage $\pi$ & 2SLS & Partial $F$ & $N$ \\")
for k, lbl in [("baseline", "Aviation technology $\\times$ air geography (baseline)"), ("plus_oil", "\\quad plus oil price $\\times$ geography"),
               ("plus_gdp", "\\quad plus world GDP $\\times$ geography"), ("plus_trade", "\\quad plus world exports $\\times$ geography"), ("plus_all3", "\\quad plus all three")]:
    fs = get("B", k, "FS"); iv = get("B", k, "IV")
    L.append(f"  {lbl} & {c3(fs.b, fs.se, fs.p)} & {c2(iv.b, iv.se, iv.p)} & {fs.f:.1f} & {int(fs.nn):,} \\\\")
for k, lbl in [("own_fey_gdp", "World GDP $\\times$ geography alone"), ("own_fey_oil", "Oil price $\\times$ geography alone"), ("own_fey_trade", "World exports $\\times$ geography alone")]:
    fs = get("B", k, "FS"); rf = get("B", k, "RF")
    L.append(f"  {lbl} & {c3(fs.b, fs.se, fs.p)} & RF {c3(rf.b, rf.se, rf.p)} & {fs.f:.1f} & {int(fs.nn):,} \\\\")
L.append(r"\midrule")
L.append(r"\multicolumn{5}{l}{\textit{Panel C. Placebo instrument: aviation technology $\times$ 1996 sea market access}} \\")
L.append(r" & First-stage $\pi$ & Reduced form & Partial $F$ & $N$ \\")
fs = get("C", "sea_alone", "FS"); rf = get("C", "sea_alone", "RF")
L.append(f"  Sea-geography instrument alone & {c3(fs.b, fs.se, fs.p)} & {c3(rf.b, rf.se, rf.p)} & {fs.f:.1f} & {int(fs.nn):,} \\\\")
fs = get("C", "sea_with_air", "FS"); rf = get("C", "sea_with_air", "RF")
L.append(f"  Sea-geography instrument, air-geography instrument included & {c3(fs.b, fs.se, fs.p)} & {c3(rf.b, rf.se, rf.p)} & {fs.f:.1f} & {int(fs.nn):,} \\\\")
fs = get("C", "air_with_sea", "FS"); rf = get("C", "air_with_sea", "RF"); iv = get("C", "air_with_sea", "IV")
L.append(f"  Air-geography instrument, sea-geography instrument included & {c3(fs.b, fs.se, fs.p)} & {c3(rf.b, rf.se, rf.p)} & {fs.f:.1f} & {int(fs.nn):,} \\\\")
L.append(f"  \\quad 2SLS with the sea interaction as a control & \\multicolumn{{2}}{{c}}{{{c2(iv.b, iv.se, iv.p)}}} & {iv.f:.1f} & {int(iv.nn):,} \\\\")
L.append(r"\midrule")
L.append(r"\multicolumn{5}{l}{\textit{Panel D. Zero-first-stage test by baseline connectivity tercile}} \\")
L.append(r" & First-stage $\pi$ & Reduced form (CO$_2$) & Partial $F$ & $N$ \\")
for g, lbl in [(1, "Low baseline connectivity"), (2, "Middle"), (3, "High (instrument does not move GACI)")]:
    fs = get("D", f"con{g}", "FS"); rf = get("D", f"con{g}", "RF")
    L.append(f"  {lbl} & {c3(fs.b, fs.se, fs.p)} & {c3(rf.b, rf.se, rf.p)} & {fs.f:.1f} & {int(fs.nn):,} \\\\")
L.append(r"\midrule")
L.append(r"\multicolumn{5}{l}{\textit{Panel E. Development-channel controls added sequentially (2SLS coefficient on log GACI)}} \\")
L.append(r" & 2SLS & & KP $F$ & $N$ \\")
for k, lbl in [("c0_baseline", "Baseline (log population, log sea market access)"), ("c1_gdp", "\\quad plus log GDP"), ("c2_trade", "\\quad plus trade/GDP"),
               ("c3_urban", "\\quad plus urban share"), ("c4_fdi", "\\quad plus FDI/GDP"), ("c5_arrivals", "\\quad plus log tourist arrivals"), ("c0_commonsample", "Baseline on the common sample of the last row")]:
    iv = get("E", k, "IV")
    L.append(f"  {lbl} & {c2(iv.b, iv.se, iv.p)} & & {iv.f:.1f} & {int(iv.nn):,} \\\\")
L += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}\scriptsize",
      r"\item All regressions include country and year fixed effects, log population and log sea market access; " + SENOTE + " in parentheses. Panel A: the reduced form regresses each log outcome on the Feyrer interaction; non-aviation series are Global Carbon Project territorial CO$_2$ via Our World in Data (domestic aviation subtracted, since international bunkers are excluded from territorial totals) and EDGAR v2024 sectoral CO$_2$ (1996--2023). Panel B: rival cycles are world real GDP, the annual Brent price and world real exports, each min-max scaled like the aviation index and interacted with log 1996 air market access; the aviation index correlates 0.82, 0.53 and 0.84 with the three. Panel C: the placebo instrument replaces air market access by sea market access in the interaction. Panel D: terciles of 1996 capacity-weighted GACI. $^{***}$ $p<0.01$, $^{**}$ $p<0.05$, $^{*}$ $p<0.1$.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex1 = "\n".join(L)

# ---------------- SI table: alternative shifters, leads, J, SE ----------------
S = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}",
     r"\caption{Supplementary Table: Alternative instrument constructions, leads, overidentification and inference}", r"\label{tab:exclusion2}", r"\scriptsize",
     r"\begin{tabular}{lcccc}", r"\toprule", r" & First-stage $\pi$ & 2SLS & KP $F$ & $N$ \\", r"\midrule",
     r"\multicolumn{5}{l}{\textit{Panel A. Technology series in the interaction (all $\times$ log 1996 air market access)}} \\"]
for k, lbl in [("feyrer_int", "World seat capacity (baseline)"), ("fey_fl", "World flights"), ("fey_skm", "World seat-km"), ("fey_gaci", "World sum of GACI"), ("fey_eff", "World fuel-efficiency index (CO$_2$ per seat-km, inverted)"),
               ("fey_th10chk", "Baseline geography recomputed ($\\theta = 1$)"), ("fey_th05", "Distance decay $\\theta = 0.5$"), ("fey_th15", "Distance decay $\\theta = 1.5$")]:
    fs = get("F", k, "FS"); iv = get("F", k, "IV")
    S.append(f"  {lbl} & {c3(fs.b, fs.se, fs.p)} & {c2(iv.b, iv.se, iv.p)} & {fs.f:.1f} & {int(fs.nn):,} \\\\")
S.append(r"\midrule")
S.append(r"\multicolumn{5}{l}{\textit{Panel B. Leads of the instrument (reduced form on log CO$_2$)}} \\")
S.append(r" & Current & Lead & & $N$ \\")
for k, lbl in [("lead3", "Three-year lead"), ("lead5", "Five-year lead")]:
    cur = get("G", f"{k}_current", "RF"); ld = get("G", f"{k}_lead", "RF")
    S.append(f"  {lbl} & {c3(cur.b, cur.se, cur.p)} & {c3(ld.b, ld.se, ld.p)} & & {int(cur.nn):,} \\\\")
S.append(r"\midrule")
S.append(r"\multicolumn{5}{l}{\textit{Panel C. Overidentification and inference (2SLS on log CO$_2$)}} \\")
S.append(r" & 2SLS & s.e. & KP $F$ & $N$ \\")
iv = get("H", "feyrer_plus_tourism", "IV"); j = get("H", "hansen_j", "J")
S.append(f"  Feyrer and tourism-heritage instruments jointly & {iv.b:.2f}{star(iv.p)} & ({iv.se:.2f}) & {iv.f:.1f} & {int(iv.nn):,} \\\\")
S.append(f"  \\quad Hansen $J$ (p-value) & \\multicolumn{{2}}{{c}}{{{j.b:.2f} ({j.p:.3f})}} & & \\\\")
ta = get("H", "tourism_alone", "IV")
if ta is not None:
    S.append(f"  Tourism-heritage instrument alone & {ta.b:.2f}{star(ta.p)} & ({ta.se:.2f}) & {ta.f:.1f} & {int(ta.nn):,} \\\\")
for k, lbl in [("robust", "Heteroskedasticity-robust" + (" (baseline)" if not SUF else "")), ("cluster_country", "Clustered by country"), ("cluster_twoway", "Two-way clustered (country, year)")]:
    iv = get("I", k, "IV")
    S.append(f"  {lbl} & {iv.b:.2f}{star(iv.p)} & ({iv.se:.2f}) & {iv.f:.1f} & {int(iv.nn):,} \\\\")
S += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}\scriptsize",
      r"\item Specification as in Table~\ref{tab:main}, column 1. Panel A replaces the world seat-capacity index by other min-max scaled world aviation series, or recomputes 1996 air market access with a different distance-decay exponent. Panel B enters the instrument dated $t+3$ or $t+5$ alongside its current value; because the technology index is a smooth global trend, the lead is mechanically collinear with the current value and this test is informative only about differential trends by geography. Panel C: the tourism-heritage instrument fails the size-by-cycle stress test (Methods) and is shown for reference; the Hansen test rejects equality of the two just-identified estimates. $^{***}$ $p<0.01$, $^{**}$ $p<0.05$, $^{*}$ $p<0.1$.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex2 = "\n".join(S)
with open(os.path.join(HERE, "_tex_exclusion" + SUF + ".tex"), "w", encoding="utf-8") as f:
    f.write("% ===== tab:exclusion =====\n" + tex1 + "\n\n% ===== tab:exclusion2 =====\n" + tex2 + "\n")
print("wrote _tex_exclusion.tex")

# ---------------- figure: reduced-form comparison ----------------
rows = []
for k, lbl in A:
    rf = get("A", k, "RF")
    if rf is not None:
        rows.append((lbl.replace("\\ ", " ").replace("$_2$", "2").replace("excl.\\", "excl."), rf.b, rf.se, k.startswith("ln_co2_tot") or k == "ln_co2_intl"))
fig, ax = plt.subplots(figsize=(8.6, 5.0))
ys = list(range(len(rows)))[::-1]
for yy, (lbl, b, se, av) in zip(ys, rows):
    ax.barh(yy, b, color=(ACC if av else GRAY), height=0.66, edgecolor="white")
    ax.errorbar(b, yy, xerr=1.96 * se, fmt="none", ecolor=INK, elinewidth=1.0, capsize=2.5)
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
ax.axvline(0, color=INK, lw=0.8)
ax.set_xlabel("Reduced-form coefficient on the Feyrer instrument (log outcome), 95% CI")
ax.set_title("Reduced forms: aviation CO2 (blue) versus non-aviation emissions", loc="left", fontsize=11.5)
ax.spines[["top", "right"]].set_visible(False); ax.grid(axis="x", color="#e6e6e6", lw=0.7)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "CO2_placebo_rf.png"), dpi=200); plt.close(fig)
print("saved CO2_placebo_rf.png")
print("DONE_23")
