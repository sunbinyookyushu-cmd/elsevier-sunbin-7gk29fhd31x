# -*- coding: utf-8 -*-
"""
18_decomp_table_fig.py   (LZ comment 1, 2026-09-03)
Layer 2 displays from _feyrer_mechanism.csv and _decomp_hetero.csv:
  - tab:decomp   main-text table, identity decomposition with scale/efficiency subtotals
  - fig CO2_decomp_waterfall.png   waterfall 0 -> +flights -> gauge -> stage -> intensity = total
  - tab:decomp_hetero  ED table: decomposition by income tercile, connectivity tercile,
                       and by segment (international / domestic)
  - CO2_hetero_coefplot.png regenerated from _feyrer_hetero_tot.csv (total CO2 outcome)
Writes tex fragments to _tex_decomp.tex
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

plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"], "font.size": 11, "axes.linewidth": 0.8})
ACC, GRAY, NEG, INK = "#1F4E79", "#9AA0A6", "#B5651D", "#1f1f1f"

def star(p):
    return "$^{***}$" if p < .01 else ("$^{**}$" if p < .05 else ("$^{*}$" if p < .1 else ""))
def pv(b, se):
    return math.erfc(abs(b / se) / 2 ** 0.5)

m = pd.read_csv(os.path.join(HERE, "_feyrer_mechanism" + SUF + ".csv")).set_index("outc")
tot = m.loc["ln_co2_tot", "b"]
comp = [("ln_flights", "Flights (frequency)"), ("ln_gauge", "Seats per flight (aircraft gauge)"),
        ("ln_stage", "Km per flight (average stage length)"), ("ln_intensity", "CO$_2$ per seat-km (carbon intensity)")]
rows = []
def row(lbl, b, se, share, bold=False):
    p = pv(b, se)
    l = f"\\textbf{{{lbl}}}" if bold else lbl
    return f"  {l} & {b:+.3f}{star(p)} & ({se:.3f}) & {share:+.0f} \\\\"
L = []
L.append(r"\begin{table}[htbp]")
L.append(r"\centering")
L.append(r"\begin{threeparttable}")
L.append(r"\caption{Decomposition of the CO$_2$ elasticity on the accounting identity}")
L.append(r"\label{tab:decomp}")
L.append(r"\footnotesize")
L.append(r"\begin{tabular}{lccc}")
L.append(r"\toprule")
L.append(r" & Elasticity to GACI & s.e. & Share of total (\%) \\")
L.append(r"\midrule")
L.append(r"\multicolumn{4}{l}{\textit{Scale components}} \\")
for k, lbl in comp[:3]:
    L.append(row(lbl, m.loc[k, "b"], m.loc[k, "se"], 100 * m.loc[k, "b"] / tot))
L.append(row("Subtotal: scale (seat-km)", m.loc["ln_skm", "b"], m.loc["ln_skm", "se"], 100 * m.loc["ln_skm", "b"] / tot, bold=True))
L.append(r"\multicolumn{4}{l}{\textit{Efficiency component}} \\")
k, lbl = comp[3]
L.append(row(lbl, m.loc[k, "b"], m.loc[k, "se"], 100 * m.loc[k, "b"] / tot))
L.append(r"\midrule")
L.append(row("Total CO$_2$ (equals Table~\\ref{tab:main}, column 1)", tot, m.loc["ln_co2_tot", "se"], 100, bold=True))
L.append(r"\midrule")
L.append(r"\multicolumn{4}{l}{\textit{Composition margins (memo)}} \\")
L.append(row("LTO share of CO$_2$", m.loc["lto_share", "b"], m.loc["lto_share", "se"], float("nan")).replace("& +nan \\\\", "& -- \\\\"))
L.append(row("International share of seat-km", m.loc["intl_share", "b"], m.loc["intl_share", "se"], float("nan")).replace("& +nan \\\\", "& -- \\\\"))
L.append(r"\bottomrule")
L.append(r"\end{tabular}")
L.append(r"\begin{tablenotes}\footnotesize")
L.append(r"\item Each row is a separate 2SLS regression of the log component on log GACI (capacity-weighted mean), instrumented by the Feyrer interaction, with log population and log sea market access, country and year fixed effects, and " + SENOTE + "; identical sample of "
         f"{int(m.loc['ln_co2_tot','nn']):,} country-years, first-stage Kleibergen-Paap $F$ = {m.loc['ln_co2_tot','kpf']:.1f}. "
         r"Because CO$_2$ = flights $\times$ seats per flight $\times$ km per flight $\times$ CO$_2$ per seat-km, the log elasticities add exactly to the total. Load factor is constant by construction (scheduled capacity) and cancels. Shares are component elasticity divided by the total. $^{***}$ $p<0.01$, $^{**}$ $p<0.05$, $^{*}$ $p<0.1$.")
L.append(r"\end{tablenotes}")
L.append(r"\end{threeparttable}")
L.append(r"\end{table}")
tex_main = "\n".join(L)

# ---------------- waterfall ----------------
steps = [("Flights", m.loc["ln_flights", "b"], m.loc["ln_flights", "se"]),
         ("Seats per\nflight", m.loc["ln_gauge", "b"], m.loc["ln_gauge", "se"]),
         ("Km per\nflight", m.loc["ln_stage", "b"], m.loc["ln_stage", "se"]),
         ("CO$_2$ per\nseat-km", m.loc["ln_intensity", "b"], m.loc["ln_intensity", "se"])]
fig, ax = plt.subplots(figsize=(8.2, 4.6))
cum = 0.0
xs = list(range(len(steps) + 1))
for i, (lbl, b, se) in enumerate(steps):
    bottom = cum if b >= 0 else cum + b
    ax.bar(i, abs(b), bottom=bottom, width=0.62, color=(ACC if b >= 0 else NEG), edgecolor="white", linewidth=0.8, zorder=3)
    ax.errorbar(i, cum + b, yerr=1.96 * se, fmt="none", ecolor=INK, elinewidth=1.0, capsize=3, zorder=4)
    ax.annotate(f"{b:+.2f}", (i, max(cum, cum + b) + 0.25 + 1.96 * se * (b >= 0)), ha="center", va="bottom", fontsize=10.5, color=INK)
    newcum = cum + b
    ax.plot([i + 0.31, i + 1 - 0.31], [newcum, newcum], color=GRAY, lw=0.9, ls="--", zorder=2)
    cum = newcum
ax.bar(len(steps), tot, width=0.62, color="#555555", edgecolor="white", linewidth=0.8, zorder=3)
ax.errorbar(len(steps), tot, yerr=1.96 * m.loc["ln_co2_tot", "se"], fmt="none", ecolor=INK, elinewidth=1.0, capsize=3, zorder=4)
ax.annotate(f"{tot:.2f}", (len(steps), tot + 0.25 + 1.96 * m.loc["ln_co2_tot", "se"]), ha="center", va="bottom", fontsize=10.5, color=INK, fontweight="bold")
ax.set_xticks(xs)
ax.set_xticklabels([s[0] for s in steps] + ["Total CO$_2$"])
ax.axhline(0, color=INK, lw=0.8)
ax.set_ylabel("Elasticity to GACI (2SLS, Feyrer IV)")
ax.set_ylim(-1.2, 9.8)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#e6e6e6", lw=0.7, zorder=0)
ax.text(0.99, 0.97, "Scale (seat-km): %+.2f    Efficiency: %+.2f" % (m.loc["ln_skm", "b"], m.loc["ln_intensity", "b"]),
        transform=ax.transAxes, va="top", ha="right", fontsize=10.5, color=INK)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "CO2_decomp_waterfall.png"), dpi=220)
plt.close(fig)
print("saved CO2_decomp_waterfall.png")

# ---------------- ED table: decomposition heterogeneity ----------------
d = pd.read_csv(os.path.join(HERE, "_decomp_hetero" + SUF + ".csv"))
def cell(b, se, p):
    return f"{b:+.2f}{star(p)} ({se:.2f})"
comps = ["ln_co2", "ln_flights", "ln_gauge", "ln_stage", "ln_intensity"]
heads = ["Total CO$_2$", "Flights", "Seats/flight", "Km/flight", "CO$_2$/seat-km"]
blocks = [("Panel A. Baseline income tercile (total CO$_2$ identity)", "A_income", [("inc_low", "Low income"), ("inc_mid", "Middle income"), ("inc_high", "High income")]),
          ("Panel B. Baseline connectivity tercile", "B_conn", [("con_low", "Low connectivity"), ("con_mid", "Middle connectivity"), ("con_high", "High connectivity")]),
          ("Panel C. Segment identities", "C_segment", [("all|intl", "International traffic, all countries"), ("all|dom", "Domestic traffic, all countries"),
                                                          ("inc_low|intl", "International, low income"), ("inc_high|intl", "International, high income")])]
E = []
E.append(r"\begin{table}[htbp]")
E.append(r"\centering")
E.append(r"\begin{threeparttable}")
E.append(r"\caption{Extended Data Table: Decomposition of the CO$_2$ elasticity by group and segment}")
E.append(r"\label{tab:decomp_hetero}")
E.append(r"\scriptsize")
E.append(r"\begin{tabular}{l" + "c" * 5 + "cc}")
E.append(r"\toprule")
E.append(" & " + " & ".join(heads) + r" & KP $F$ & $N$ \\")
E.append(r"\midrule")
for title, blk, grps in blocks:
    E.append(r"\multicolumn{8}{l}{\textit{" + title + r"}} \\")
    for key, lbl in grps:
        if "|" in key:
            g, seg = key.split("|")
        else:
            g, seg = key, "tot"
        sub = d[(d.block == blk) & (d.grp == g) & (d.seg == seg)].set_index("outc")
        if len(sub) == 0:
            continue
        cells = [cell(sub.loc[c, "b"], sub.loc[c, "se"], sub.loc[c, "p"]) for c in comps]
        E.append(f"  {lbl} & " + " & ".join(cells) + f" & {sub.loc['ln_co2','kpf']:.1f} & {int(sub.loc['ln_co2','nn']):,} \\\\")
E.append(r"\bottomrule")
E.append(r"\end{tabular}")
E.append(r"\begin{tablenotes}\scriptsize")
E.append(r"\item 2SLS elasticities to log GACI (Feyrer instrument; controls and fixed effects as in Table~\ref{tab:decomp}), estimated on the common sample of each block so that the four components sum to the total within each row. Panel C applies the identity separately to international and domestic departures; domestic rows exclude country-years without domestic traffic. The high-connectivity tercile has a weak first stage ($F$ = 1.8) and is reported for completeness only. " + SENOTE_C + " in parentheses. $^{***}$ $p<0.01$, $^{**}$ $p<0.05$, $^{*}$ $p<0.1$.")
E.append(r"\end{tablenotes}")
E.append(r"\end{threeparttable}")
E.append(r"\end{table}")
tex_ed = "\n".join(E)

with open(os.path.join(HERE, "_tex_decomp" + SUF + ".tex"), "w", encoding="utf-8") as f:
    f.write("% ===== tab:decomp (main text) =====\n" + tex_main + "\n\n% ===== tab:decomp_hetero (ED) =====\n" + tex_ed + "\n")
print("wrote _tex_decomp.tex")

# ---------------- hetero coefplot from total-CO2 results ----------------
h = pd.read_csv(os.path.join(HERE, "_feyrer_hetero_tot" + SUF + ".csv"))
h = h[~h["grp"].str.startswith("interact")]
h = h[~h["grp"].isin(["MiddleEast", "NorthAm"])]
glab = {"inc_low": "Low income", "inc_mid": "Middle income", "inc_high": "High income",
        "con_low": "Low connectivity", "con_mid": "Middle connectivity", "con_high": "High connectivity",
        "Europe": "Europe", "AsiaPacific": "Asia-Pacific", "Africa": "Africa", "LatAm": "Latin America"}
panels = [("A_income", "A. Total CO2 by baseline income"), ("B_conn", "B. Total CO2 by baseline connectivity"),
          ("C_region", "C. Total CO2 by region"), ("D_intens", "D. Intensity by baseline income")]
fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.5))
for ax, (pk, title) in zip(axes.ravel(), panels):
    dd = h[h["panel"] == pk].reset_index(drop=True)
    labels = [glab.get(g, g) for g in dd["grp"]]
    ypos = list(range(len(dd)))[::-1]
    for yy, b, se, p in zip(ypos, dd["b"], dd["se"], dd["p"]):
        lo, hi = b - 1.96 * se, b + 1.96 * se
        ax.plot([lo, hi], [yy, yy], color=ACC, lw=1.6, solid_capstyle="round", zorder=2)
        ax.plot(b, yy, "o", ms=7, mfc=(ACC if p < .05 else "white"), mec=ACC, mew=1.4, zorder=3)
        ax.annotate(f"{b:.2f}", (b, yy), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color="#333333")
    ax.axvline(0, color=GRAY, lw=0.9, ls="--", zorder=1)
    ax.set_yticks(ypos); ax.set_yticklabels(labels)
    ax.set_title(title, fontsize=11.5, loc="left")
    ax.spines[["top", "right"]].set_visible(False); ax.tick_params(axis="y", length=0)
axes[1, 0].set_xlabel("2SLS coefficient on ln GACI (Feyrer IV)")
axes[1, 1].set_xlabel("2SLS coefficient on ln GACI (Feyrer IV)")
fig.suptitle("Heterogeneity of the connectivity elasticity (filled = p<0.05, bars = 95% CI)", fontsize=12.5, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(os.path.join(HERE, "CO2_hetero_coefplot.png"), dpi=200)
plt.close(fig)
print("saved CO2_hetero_coefplot.png (total CO2)")
print("DONE_18")
