# -*- coding: utf-8 -*-
"""14_fig_gic_descriptive.py : descriptive growth-by-group curves (Piketty-Saez-Zucman style), split by
   how much the country's hub connectivity grew over the sample.
   For each country: annualised log change of average pretax income of each WID group (WID aptinc 992j,
   constant local prices) between the first and last year with complete data (span >= 15 years), and the
   annualised log change of GACI_max over the same window. Countries are split into terciles of GACI growth.
   Panel (a): mean annualised income growth by group, low vs high GACI-growth tercile (middle in light grey).
   Panel (b): high-minus-low difference by group with 95% CI (two-sample, country-level).
   Input: ineq_panel_ext.csv. Output: fig_gic_descriptive.png / .pdf, _gic_descriptive.csv"""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = os.path.dirname(os.path.abspath(__file__))
GROUPS = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01"]
LAB = ["p0–10", "p10–20", "p20–30", "p30–40", "p40–50", "p50–60", "p60–70", "p70–80", "p80–90", "p90–100", "Top 1%", "Top 0.1%"]
MIN_SPAN = 15
C_LOW, C_MID, C_HIGH = "#4D4D4D", "#BDBDBD", "#1F5F8B"

cols = ["ln_apt_%s" % g for g in GROUPS]
d = pd.read_csv(os.path.join(D, "ineq_panel_ext.csv"), low_memory=False)
d = d.dropna(subset=["gini_mkt", "ln_gaci_max"] + cols)[["c", "y", "ln_gaci_max"] + cols].sort_values(["c", "y"])

rows = []
for c, g in d.groupby("c"):
    f, l = g.iloc[0], g.iloc[-1]
    span = int(l.y - f.y)
    if span < MIN_SPAN:
        continue
    r = {"c": c, "y0": int(f.y), "y1": int(l.y), "span": span,
         "dg": 100 * (l.ln_gaci_max - f.ln_gaci_max) / span}
    for k in GROUPS:
        r[k] = 100 * (l["ln_apt_" + k] - f["ln_apt_" + k]) / span
    rows.append(r)
X = pd.DataFrame(rows)
X["terc"] = pd.qcut(X.dg, 3, labels=["low", "mid", "high"])
print("countries", len(X), "| span median", X.span.median(), "| GACI growth by tercile (%/yr):")
print(X.groupby("terc", observed=True).dg.agg(["mean", "min", "max", "count"]).round(2))

summ = []
for k, lab in zip(GROUPS, LAB):
    lo, mi, hi = (X.loc[X.terc == t, k] for t in ["low", "mid", "high"])
    diff = hi.mean() - lo.mean()
    se = np.sqrt(hi.var(ddof=1) / len(hi) + lo.var(ddof=1) / len(lo))
    summ.append({"group": k, "label": lab, "low_mean": lo.mean(), "mid_mean": mi.mean(), "high_mean": hi.mean(),
                 "diff_high_low": diff, "se_diff": se, "n_low": len(lo), "n_mid": len(mi), "n_high": len(hi)})
S = pd.DataFrame(summ)
S.to_csv(os.path.join(D, "_gic_descriptive.csv"), index=False)
X.to_csv(os.path.join(D, "_gic_descriptive_countries.csv"), index=False)
print(S[["label", "low_mean", "high_mean", "diff_high_low", "se_diff"]].round(2).to_string(index=False))

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#E6E6E6", "grid.linewidth": 0.6, "axes.axisbelow": True})
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
xs = np.arange(len(GROUPS))

ax = axes[0]
ax.plot(xs, S.mid_mean, color=C_MID, lw=1.4, marker="o", ms=3.5, zorder=2)
ax.plot(xs, S.low_mean, color=C_LOW, lw=2, marker="s", ms=4.5, zorder=3)
ax.plot(xs, S.high_mean, color=C_HIGH, lw=2, marker="o", ms=4.5, zorder=4)
ax.text(xs[-1] + 0.15, S.high_mean.iloc[-1], "High GACI growth\n(n=%d)" % S.n_high[0], color=C_HIGH, va="center", fontsize=8)
ax.text(xs[-1] + 0.15, S.low_mean.iloc[-1], "Low GACI growth\n(n=%d)" % S.n_low[0], color=C_LOW, va="center", fontsize=8)
ax.text(xs[-1] + 0.15, S.mid_mean.iloc[-1], "Middle", color="#8A8A8A", va="center", fontsize=8)
ax.set_xlim(-0.5, len(GROUPS) + 1.6)
ax.set_title("(a) Annualised real income growth by group, %d–%d" % (int(X.y0.median()), int(X.y1.median())), loc="left", fontsize=9.5)
ax.set_ylabel("Mean growth of average pretax income (% per year)")

ax = axes[1]
ax.axhline(0, color="#8A8A8A", lw=0.8, zorder=1)
ax.errorbar(xs, S.diff_high_low, yerr=1.96 * S.se_diff, fmt="o", color=C_HIGH, ms=4.5, lw=1.2, capsize=2.5, zorder=3)
ax.set_title("(b) High minus low GACI-growth tercile (95% CI)", loc="left", fontsize=9.5)
ax.set_ylabel("Difference in growth (pp per year)")
ax.set_xlim(-0.5, len(GROUPS) - 0.5)

for ax in axes:
    ax.set_xticks(xs)
    ax.set_xticklabels(LAB, rotation=45, ha="right", fontsize=8)
    ax.axvline(9.5, color="#BDBDBD", lw=0.8, ls=":", zorder=1)
fig.text(0.01, -0.02,
         "Note: one observation per country (first to last year with complete WID and GACI data, span >= %d years). "
         "Terciles by annualised change in ln GACI$_{max}$. WID pretax national income, equal-split adults, constant local prices. "
         "Deciles left of the dotted line; top fractiles right." % MIN_SPAN, fontsize=7, color="#555555", ha="left")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(D, "fig_gic_descriptive." + ext), dpi=300, bbox_inches="tight")
print("saved fig_gic_descriptive.png/pdf")
