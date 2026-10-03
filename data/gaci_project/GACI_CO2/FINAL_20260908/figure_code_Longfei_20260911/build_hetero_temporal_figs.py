# -*- coding: utf-8 -*-
"""Coefficient plots for the CO2 workbook: heterogeneity (4 panels) and
temporal split. Point estimate +- 95% CI, single accent hue, filled = p<0.05."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"],
                     "font.size": 11, "axes.linewidth": 0.8})
ACC = "#1F4E79"
GRAY = "#9AA0A6"

# ---------------- heterogeneity ----------------
h = pd.read_csv(os.path.join(HERE, "_feyrer_hetero.csv"))
h = h[~h["grp"].str.startswith("interact")]
h = h[~h["grp"].isin(["MiddleEast", "NorthAm"])]  # unidentified (KPF<2)
glab = {"inc_low": "Low income", "inc_mid": "Middle income", "inc_high": "High income",
        "con_low": "Low connectivity", "con_mid": "Middle connectivity", "con_high": "High connectivity",
        "Europe": "Europe", "AsiaPacific": "Asia-Pacific", "Africa": "Africa", "LatAm": "Latin America"}
panels = [("A_income", "A. Total CO2 by baseline income"),
          ("B_conn", "B. Total CO2 by baseline connectivity"),
          ("C_region", "C. Total CO2 by region"),
          ("D_intens", "D. Intensity by baseline income")]
fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.5))
for ax, (pk, title) in zip(axes.ravel(), panels):
    d = h[h["panel"] == pk].reset_index(drop=True)
    labels = [glab.get(g, g) for g in d["grp"]]
    ypos = range(len(d))[::-1]
    for i, (yy, b, se, p) in enumerate(zip(ypos, d["b"], d["se"], d["p"])):
        lo, hi = b - 1.96 * se, b + 1.96 * se
        ax.plot([lo, hi], [yy, yy], color=ACC, lw=1.6, solid_capstyle="round", zorder=2)
        ax.plot(b, yy, "o", ms=7, mfc=(ACC if p < .05 else "white"), mec=ACC, mew=1.4, zorder=3)
        ax.annotate(f"{b:.2f}", (b, yy), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=9, color="#333333")
    ax.axvline(0, color=GRAY, lw=0.9, ls="--", zorder=1)
    ax.set_yticks(list(ypos))
    ax.set_yticklabels(labels)
    ax.set_title(title, fontsize=11.5, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
axes[1, 0].set_xlabel("2SLS coefficient on ln GACI (Feyrer IV)")
axes[1, 1].set_xlabel("2SLS coefficient on ln GACI (Feyrer IV)")
fig.suptitle("Heterogeneity of the connectivity elasticity (filled = p<0.05, bars = 95% CI)",
             fontsize=12.5, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(os.path.join(HERE, "_unused_hetero_from_old_script.png"), dpi=200)
plt.close(fig)
print("saved CO2_hetero_coefplot.png")

# ---------------- temporal ----------------
# panels: full sample / crisis-free split (1996-2007, 2010-2023 excl 2020-21)
# / unrestricted 2010-2023 (gray, weak first stage) for reference
t_old = pd.read_csv(os.path.join(HERE, "_temporal_co2_cl.csv"))
t_pre8 = pd.read_csv(os.path.join(HERE, "_temporal_pre2008_cl.csv"))
t_xc = pd.read_csv(os.path.join(HERE, "_temporal_excovid_cl.csv"))
rows = []
for _, r in t_old[t_old["period"] == "full"].iterrows():
    rows.append({"period": "full", "outc": r["outc"], "b": r["b"], "se": r["se"],
                 "p": r["p"], "kpf": r["kpf"]})
for _, r in t_pre8[t_pre8["samp"] == "1996-2007"].iterrows():
    rows.append({"period": "1996-2007", "outc": r["outc"], "b": r["b"], "se": r["se"],
                 "p": r["p"], "kpf": r["kpf"]})
for _, r in t_xc[t_xc["samp"] == "2010-2023_exCOVID"].iterrows():
    rows.append({"period": "2010-2023xc", "outc": r["outc"], "b": r["b"], "se": r["se"],
                 "p": r["p"], "kpf": r["kpf"]})
for _, r in t_old[t_old["period"] == "2010-2023"].iterrows():
    rows.append({"period": "2010-2023un", "outc": r["outc"], "b": r["b"], "se": r["se"],
                 "p": r["p"], "kpf": r["kpf"]})
t = pd.DataFrame(rows)
olab = {"ln_co2_tot": "Total CO2", "ln_co2_intl": "Intl CO2",
        "ln_skm": "Seat-km", "ln_intensity": "Intensity"}
periods = ["full", "1996-2007", "2010-2023xc", "2010-2023un"]
outs = ["ln_co2_tot", "ln_co2_intl", "ln_skm", "ln_intensity"]
fig, ax = plt.subplots(figsize=(9.5, 5.2))
gap = 1.0
xw = 0.26
xticks, xticklab = [], []
x0 = 0.0
for oi, o in enumerate(outs):
    for pi, per in enumerate(periods):
        d = t[(t["outc"] == o) & (t["period"] == per)].iloc[0]
        x = x0 + pi * xw
        lo, hi = d["b"] - 1.96 * d["se"], d["b"] + 1.96 * d["se"]
        weak = d["kpf"] < 10
        col = GRAY if weak else ACC
        ax.plot([x, x], [lo, hi], color=col, lw=1.6, solid_capstyle="round", zorder=2)
        ax.plot(x, d["b"], "o", ms=7, mfc=(col if d["p"] < .05 else "white"),
                mec=col, mew=1.4, zorder=3)
    xticks.append(x0 + 1.5 * xw)
    xticklab.append(olab[o])
    x0 += 4 * xw + gap
ax.axhline(0, color=GRAY, lw=0.9, ls="--", zorder=1)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklab)
ax.set_ylabel("2SLS coefficient on ln GACI (Feyrer IV)")
ax.set_title("Temporal split: within each outcome, dots = full 1996-2023 / 1996-2007 / 2010-2023 excl. 2020-21\n"
             "/ 2010-2023 unrestricted (left to right). Gray = weak first stage (KP F = 3.2, COVID-contaminated); country-clustered 95% CIs.",
             fontsize=11, loc="left")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "CO2_temporal_coefplot.png"), dpi=200)
plt.close(fig)
print("saved CO2_temporal_coefplot.png")
