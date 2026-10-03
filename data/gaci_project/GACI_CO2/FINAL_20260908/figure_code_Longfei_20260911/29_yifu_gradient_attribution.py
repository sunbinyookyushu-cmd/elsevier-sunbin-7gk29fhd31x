# -*- coding: utf-8 -*-
# NOTE (package copy, 11 Sep 2026): only the path lines were changed so the
# script finds its inputs in this flat folder. The figure code is untouched.
"""
29_yifu_gradient_attribution.py   (Yifu comments 1, 3, 4; 2026-09-03)
From _yifu_suite.csv, _feyrer_hetero_tot.csv, _attribution_scc.csv, _asn_iv_results.csv:
  - tab:funcform (ED): functional forms with implied elasticities at sample means;
                       semi-log and level by baseline tercile
  - tab:gradient (ED): quintile elasticities and flexible-interaction implied
                       elasticities at baseline percentiles
  - fig CO2_gradient_baseline.png: quintile points + continuous curve
  - heterogeneity-adjusted attribution: tercile-specific (connectivity, income),
    continuous-interaction, and semi-log elasticities -> _attribution_hetero.csv,
    tab:attr_sens (ED)
  - tab:accident_iv (SI) from the existing ASN pilot
Writes _tex_yifu.tex
"""
import os, math, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8")
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

y = pd.read_csv(os.path.join(HERE, "_yifu_suite" + SUF + ".csv"))
def g(panel, item, var=None):
    r = y[(y.panel == panel) & (y.item == item)]
    if var is not None:
        r = r[r["var"] == var]
    return r.iloc[0] if len(r) else None
mom = {k: g("C", f"moment_{k}") for k in ["gaci", "co2_mt", "ln_gaci_cwm", "gaci0", "lg0"]}
m_gaci, m_co2 = mom["gaci"].b, mom["co2_mt"].b
m0 = g("C", "centre_lg0").b
print(f"means: gaci {m_gaci:.3f}, co2 {m_co2:.3f} Mt; centre lg0 {m0:.3f}")

# ---------------- functional forms ----------------
ll = g("A", "loglog"); sl = g("A", "semilog"); lv = g("A", "levellevel"); lg = g("A", "linlog")
oll = g("A", "ols_loglog"); osl = g("A", "ols_semilog"); olv = g("A", "ols_levellevel")
rows = []
rows.append(("Log CO$_2$ on log GACI (reference)", ll, oll, ll.b, "elasticity"))
rows.append(("Log CO$_2$ on GACI level (semi-log)", sl, osl, sl.b * m_gaci, f"$\\beta \\times$ mean GACI ({m_gaci:.2f})"))
rows.append(("CO$_2$ (Mt) on GACI level (level-level)", lv, olv, lv.b * m_gaci / m_co2, f"$\\beta \\times$ mean GACI / mean CO$_2$ ({m_co2:.2f} Mt)"))
rows.append(("CO$_2$ (Mt) on log GACI (lin-log)", lg, None, lg.b / m_co2, "$\\beta$ / mean CO$_2$"))
L = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Extended Data Table: Functional form of the connectivity--emissions relationship}", r"\label{tab:funcform}", r"\footnotesize",
     r"\begin{tabular}{lcccc}", r"\toprule", r" & 2SLS & OLS & Implied elasticity at sample means & KP $F$ \\", r"\midrule",
     r"\multicolumn{5}{l}{\textit{Panel A. Full sample}} \\"]
for lbl, r2, ro, imp, how in rows:
    L.append(f"  {lbl} & {c(r2.b, r2.se, r2.p, 3)} & {c(ro.b, ro.se, ro.p, 3) if ro is not None else '--'} & {imp:.2f} ({how}) & {r2.kpf:.1f} \\\\")
L.append(r"\midrule")
L.append(r"\multicolumn{5}{l}{\textit{Panel B. Semi-log and level specifications by baseline-connectivity tercile}} \\")
L.append(r" & Semi-log $\beta$ & Level $\beta$ (Mt per unit) & Implied elasticities (semi-log; level) & KP $F$ \\")
for t, lbl in [(1, "Low baseline connectivity"), (2, "Middle"), (3, "High")]:
    s = g("A", f"semilog_con{t}"); l = g("A", f"level_con{t}"); mg = g("A", f"meangaci_con{t}").b; mc = g("A", f"meanco2_con{t}").b
    L.append(f"  {lbl} & {c(s.b, s.se, s.p, 3)} & {c(l.b, l.se, l.p, 3)} & {s.b * mg:.2f}; {l.b * mg / mc:.2f} (mean GACI {mg:.2f}, mean CO$_2$ {mc:.2f} Mt) & {s.kpf:.1f} \\\\")
L += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Specification as in Table~\ref{tab:main}, column 1, with the connectivity regressor and the outcome transformed as stated; the instrument is the Feyrer interaction throughout. GACI (capacity-weighted mean) has a sample mean of " + f"{m_gaci:.2f}" + r" and ranges from 0.56 to 2.57 at baseline; a one-unit change is therefore roughly a doubling for a typical country. Implied elasticities evaluate the semi-log and level slopes at sample means. " + SENOTE_C + " in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_ff = "\n".join(L)

# ---------------- gradient: quintiles + continuous ----------------
q = []
for k in range(1, 6):
    r = g("B", f"q{k}_loglog"); s = g("B", f"q{k}_semilog"); g0 = g("B", f"q{k}_gaci0"); gg = g("B", f"q{k}_gaci")
    q.append(dict(q=k, b=r.b, se=r.se, p=r.p, kpf=r.kpf, n=r.nn, sb=s.b, sse=s.se, sp=s.p, skpf=s.kpf, g0=g0.b, g0min=g0.v12, g0max=g0.v33, gmean=gg.b, simp=s.b * gg.b))
q = pd.DataFrame(q)
b1 = g("B", "int_lin", "ln_gaci_cwm"); b2 = g("B", "int_lin", "x_dev")
v11, v12, v22 = b1.se ** 2, b1.v12, b1.v22
q1 = g("B", "int_quad", "ln_gaci_cwm"); q2 = g("B", "int_quad", "x_dev"); q3 = g("B", "int_quad", "x_dev2")
Vq = np.array([[q1.se ** 2, q1.v12, q1.v13], [q1.v12, q1.v22, q1.v23], [q1.v13, q1.v23, q1.v33]])
def beta_lin(lg0):
    d = lg0 - m0; b = b1.b + b2.b * d; se = math.sqrt(max(v11 + 2 * d * v12 + d * d * v22, 0)); return b, se
def beta_quad(lg0):
    d = lg0 - m0; x = np.array([1, d, d * d]); b = float(x @ np.array([q1.b, q2.b, q3.b])); se = float(math.sqrt(max(x @ Vq @ x, 0))); return b, se
pcts = {"p10": mom["lg0"].v12, "p25": mom["lg0"].v22, "p50": mom["lg0"].v13, "p75": mom["lg0"].v23, "p90": mom["lg0"].v33}
G = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Extended Data Table: The elasticity along the baseline-connectivity distribution}", r"\label{tab:gradient}", r"\footnotesize",
     r"\begin{tabular}{lcccccc}", r"\toprule",
     r"\multicolumn{7}{l}{\textit{Panel A. Split-sample 2SLS by quintile of 1996 connectivity}} \\",
     r"Quintile & Baseline GACI (range) & Log-log elasticity & KP $F$ & Semi-log slope & Implied elasticity & $N$ \\", r"\midrule"]
for _, r in q.iterrows():
    G.append(f"  {int(r.q)} & {r.g0:.2f} ({r.g0min:.2f}--{r.g0max:.2f}) & {c(r.b, r.se, r.p)} & {r.kpf:.1f} & {c(r.sb, r.sse, r.sp)} & {r.simp:.2f} & {int(r.n):,} \\\\")
G.append(r"\midrule")
G.append(r"\multicolumn{7}{l}{\textit{Panel B. Pooled 2SLS with log GACI interacted with centred log baseline GACI (instruments interacted identically)}} \\")
G.append(r" & \multicolumn{2}{c}{Linear interaction} & \multicolumn{2}{c}{Quadratic interaction} & & \\")
G.append(f"  ln GACI & \\multicolumn{{2}}{{c}}{{{c(b1.b, b1.se, b1.p)}}} & \\multicolumn{{2}}{{c}}{{{c(q1.b, q1.se, q1.p)}}} & & \\\\")
G.append(f"  ln GACI $\\times$ (ln baseline GACI $-$ mean) & \\multicolumn{{2}}{{c}}{{{c(b2.b, b2.se, b2.p)}}} & \\multicolumn{{2}}{{c}}{{{c(q2.b, q2.se, q2.p)}}} & & \\\\")
G.append(f"  ln GACI $\\times$ (ln baseline GACI $-$ mean)$^2$ & \\multicolumn{{2}}{{c}}{{--}} & \\multicolumn{{2}}{{c}}{{{c(q3.b, q3.se, q3.p)}}} & & \\\\")
G.append(f"  KP $F$; $N$ & \\multicolumn{{2}}{{c}}{{{b1.kpf:.1f}; {int(b1.nn):,}}} & \\multicolumn{{2}}{{c}}{{{q1.kpf:.1f}; {int(q1.nn):,}}} & & \\\\")
G.append(r"\midrule")
G.append(r"\multicolumn{7}{l}{\textit{Panel C. Implied elasticity at percentiles of baseline connectivity (delta-method s.e.)}} \\")
G.append(r" & p10 & p25 & p50 & p75 & p90 & \\")
for nm, fn in [("Linear", beta_lin), ("Quadratic", beta_quad)]:
    cells = []
    for k in ["p10", "p25", "p50", "p75", "p90"]:
        b, se = fn(pcts[k]); cells.append(f"{b:.2f} ({se:.2f})")
    G.append(f"  {nm} & " + " & ".join(cells) + r" & \\")
G.append("  Baseline GACI at percentile & " + " & ".join(f"{math.exp(pcts[k]):.2f}" for k in ["p10", "p25", "p50", "p75", "p90"]) + r" & \\")
G += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Baseline connectivity is the earliest observed capacity-weighted GACI of each country. Panel A estimates Table~\ref{tab:main}, column 1, within quintiles; the implied elasticity of the semi-log specification is the slope times the quintile's mean GACI. Panel B interacts log GACI with the centred log baseline value (mean " + f"{m0:.2f}" + r"), instrumenting each term with the Feyrer interaction times the same centred value; Panel C evaluates the fitted elasticity at percentiles of the baseline distribution. " + SENOTE_C + " in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_gr = "\n".join(G)

# figure
fig, ax = plt.subplots(figsize=(8.2, 4.6))
xs = np.linspace(mom["lg0"].v12 - 0.1, mom["lg0"].v33 + 0.1, 100)
bl = np.array([beta_lin(x) for x in xs]); bq = np.array([beta_quad(x) for x in xs])
ax.fill_between(np.exp(xs), bq[:, 0] - 1.96 * bq[:, 1], bq[:, 0] + 1.96 * bq[:, 1], color=ACC, alpha=0.12, lw=0)
ax.plot(np.exp(xs), bq[:, 0], color=ACC, lw=2, label="Quadratic interaction (95% band)")
ax.plot(np.exp(xs), bl[:, 0], color=ACC, lw=1.4, ls="--", label="Linear interaction")
for _, r in q.iterrows():
    if r.kpf < 5:
        ax.annotate(f"Q{int(r.q)}: unidentified (KP F = {r.kpf:.1f})", (r.g0, 0.4), ha="center", fontsize=8.5, color=GRAY)
        continue
    ax.errorbar(r.g0, r.b, yerr=1.96 * r.se, fmt="o", color=NEG, mfc=(NEG if r.p < .05 else "white"), mec=NEG, ms=7, capsize=3, elinewidth=1.2, label="Quintile split (filled = p<0.05)" if r.q == 1 else None)
    ax.annotate(f"Q{int(r.q)}", (r.g0, r.b), textcoords="offset points", xytext=(8, 4), fontsize=9, color=INK)
ax.axhline(0, color=GRAY, lw=0.9, ls="--"); ax.axhline(1, color=GRAY, lw=0.7, ls=":")
ax.set_xlabel("Baseline connectivity (capacity-weighted GACI, 1996)"); ax.set_ylabel("Elasticity of CO$_2$ to connectivity (2SLS)")
ax.set_title("The elasticity declines with network maturity", loc="left", fontsize=11.5)
ax.legend(frameon=False, fontsize=9, loc="upper right"); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "CO2_gradient_baseline.png"), dpi=200); plt.close(fig)
print("saved CO2_gradient_baseline.png")

# ---------------- heterogeneity-adjusted attribution ----------------
att = pd.read_csv(os.path.join(HERE, "_attribution_scc.csv"))
gp = pd.read_csv(os.path.join(HERE, "gaci_panel_combined.csv"), usecols=["c", "y", "gaci_cwmean", "lnpc"])
g0 = gp.dropna(subset=["gaci_cwmean"]).sort_values(["c", "y"]).groupby("c").first()["gaci_cwmean"].rename("gaci0")
pc0 = gp.dropna(subset=["lnpc"]).sort_values(["c", "y"]).groupby("c").first()["lnpc"].rename("lnpc0")
g23 = gp[gp.y == 2023].set_index("c")["gaci_cwmean"].rename("gaci23")
att = att.merge(g0, left_on="c", right_index=True, how="left").merge(pc0, left_on="c", right_index=True, how="left").merge(g23, left_on="c", right_index=True, how="left")
att["con3"] = pd.qcut(att["gaci0"], 3, labels=[1, 2, 3]).astype(float)
att["inc3"] = pd.qcut(att["lnpc0"], 3, labels=[1, 2, 3]).astype(float)
het = pd.read_csv(os.path.join(HERE, "_feyrer_hetero_tot" + SUF + ".csv"))
bcon = {k: float(het[(het.panel == "B_conn") & (het.grp == f"con_{n}")]["b"].iloc[0]) for k, n in [(1, "low"), (2, "mid"), (3, "high")]}
binc = {k: float(het[(het.panel == "A_income") & (het.grp == f"inc_{n}")]["b"].iloc[0]) for k, n in [(1, "low"), (2, "mid"), (3, "high")]}
B0 = ll.b
att["b_common"] = B0
att["b_con3"] = att["con3"].map(bcon)
att["b_inc3"] = att["inc3"].map(binc)
att["b_lin"] = [max(beta_lin(math.log(v))[0], 0.0) if pd.notna(v) else np.nan for v in att["gaci0"]]
att["b_quad"] = [max(beta_quad(math.log(v))[0], 0.0) if pd.notna(v) else np.nan for v in att["gaci0"]]
att["dgaci"] = att["gaci23"] - att["gaci0"]
res = []
tot_e = att["e_tot_t"].sum()
for nm, col in [(f"Common elasticity ({B0:.2f})", "b_common"), ("Baseline-connectivity terciles (8.46 / 5.07 / 4.05)", "b_con3"), ("Baseline-income terciles (10.40 / 6.14 / 1.83)", "b_inc3"),
                ("Continuous, linear interaction", "b_lin"), ("Continuous, quadratic interaction", "b_quad")]:
    share = 1 - np.exp(-att[col] * att["dln_cwm"])
    a = (share * att["e_tot_t"]).sum()
    res.append(dict(rule=nm, attributed_mt=a / 1e6, share_pct=100 * a / tot_e, n=int(att[col].notna().sum())))
# semi-log rule: share = 1 - exp(-b_semilog * (GACI_2023 - GACI_0))
share = 1 - np.exp(-sl.b * att["dgaci"])
a = (share * att["e_tot_t"]).sum()
res.append(dict(rule=f"Semi-log slope ({sl.b:.2f} per GACI unit) on the absolute change", attributed_mt=a / 1e6, share_pct=100 * a / tot_e, n=int(att["dgaci"].notna().sum())))
res = pd.DataFrame(res)
print(res.round(2).to_string())
att.to_csv(os.path.join(HERE, "_attribution_hetero.csv"), index=False)
res.to_csv(os.path.join(HERE, "_attribution_sensitivity.csv"), index=False)
# top-country comparison
top = att.sort_values("att_tot_t", ascending=False).head(8)
A = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Extended Data Table: Sensitivity of the 2023 attribution to heterogeneous elasticities}", r"\label{tab:attr_sens}", r"\footnotesize",
     r"\begin{tabular}{lcc}", r"\toprule", r"Elasticity rule & Attributed 2023 CO$_2$ (Mt) & Share of 2023 emissions (\%) \\", r"\midrule"]
for _, r in res.iterrows():
    A.append(f"  {r.rule} & {r.attributed_mt:.1f} & {r.share_pct:.1f} \\\\")
A.append(r"\midrule")
A.append(r"\multicolumn{3}{l}{\textit{Largest contributors under the common and the continuous (quadratic) rule, Mt}} \\")
for _, r in top.iterrows():
    a_c = r.att_tot_t / 1e6; a_q = (1 - math.exp(-r.b_quad * r.dln_cwm)) * r.e_tot_t / 1e6
    A.append(f"  {r.c} (baseline GACI {r.gaci0:.2f}) & {a_c:.1f} & {a_q:.1f} \\\\")
A += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Attributed share $= 1-\exp(-\beta_c\,\Delta\ln\mathrm{GACI}_c)$ applied to 2023 bunker emissions, with $\beta_c$ assigned by the stated rule; terciles use the split-sample estimates of Extended Data Table~\ref{tab:hetero} (the top connectivity tercile is weakly identified), and the continuous rules use the fitted elasticity of Extended Data Table~\ref{tab:gradient} at each country's baseline, truncated at zero. The semi-log rule applies the slope to the absolute change in GACI. World 2023 emissions in the 184-country sample: " + f"{tot_e/1e6:.0f}" + r" Mt.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_att = "\n".join(A)

# ---------------- accident IV (existing pilot) ----------------
asn = pd.read_csv(os.path.join(HERE, "_asn_iv_results.csv"))
def ga(stage, z, outc):
    r = asn[(asn.stage == stage) & (asn.z == z) & (asn.outc == outc)]; return r.iloc[0] if len(r) else None
S = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}", r"\caption{Supplementary Table: Aviation-accident instrument (Aviation Safety Network), pilot}", r"\label{tab:accident_iv}", r"\footnotesize",
     r"\begin{tabular}{lcccc}", r"\toprule", r" & Bunker CO$_2$ & Intl.\ CO$_2$ & Intensity & KP $F$ \\", r"\midrule"]
for z, lbl in [("L.n_fatal", "Lagged fatal accidents"), ("L.ash_deaths", "Lagged accident deaths"), ("L.d_fatal", "Lagged any-fatal-accident indicator")]:
    rr = [ga("IV_asn", z, o) for o in ["ln_co2_tot", "ln_co2_intl", "ln_intensity"]]
    S.append(f"  2SLS, {lbl} & " + " & ".join(c(r.b, r.se, r.p) for r in rr) + f" & {rr[0].kpf:.1f} \\\\")
for z, lbl in [("fey+L.n_fatal", "Feyrer and lagged fatal accidents jointly"), ("fey+L.ash_deaths", "Feyrer and lagged accident deaths jointly")]:
    rr = [ga("OVERID", z, o) for o in ["ln_co2_tot", "ln_co2_intl", "ln_intensity"]]
    S.append(f"  {lbl} & " + " & ".join(c(r.b, r.se, r.p) for r in rr) + f" & {rr[0].kpf:.1f} \\\\")
    S.append(f"  \\quad Hansen $J$ $p$-value & {rr[0].jp:.2f} & {rr[1].jp:.2f} & {rr[2].jp:.2f} & \\\\")
S += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}[flushleft]", r"\footnotesize",
      r"\item Notes: Country-year accident counts and deaths from the Aviation Safety Network, lagged one year, as instruments for log GACI; specification otherwise as in Table~\ref{tab:main}. The accident instruments are weak (first-stage $F$ of 1 to 4) and are not used on their own; the joint specification with the Feyrer instrument is reported for the overidentification test. " + SENOTE_C + " in parentheses. $^{***}$, $^{**}$, $^{*}$: significance at 1, 5, and 10 percent.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex_asn = "\n".join(S)

with open(os.path.join(HERE, "_tex_yifu" + SUF + ".tex"), "w", encoding="utf-8") as f:
    f.write("% ===== tab:funcform =====\n" + tex_ff + "\n\n% ===== tab:gradient =====\n" + tex_gr + "\n\n% ===== tab:attr_sens =====\n" + tex_att + "\n\n% ===== tab:accident_iv =====\n" + tex_asn + "\n")
print("wrote _tex_yifu.tex")
print("implied: semilog %.2f, level %.2f; lin at p10/p50/p90: %s" % (sl.b * m_gaci, lv.b * m_gaci / m_co2, [round(beta_lin(pcts[k])[0], 2) for k in ["p10", "p50", "p90"]]))
print("DONE_29")
