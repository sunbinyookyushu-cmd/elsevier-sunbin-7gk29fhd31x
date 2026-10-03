# -*- coding: utf-8 -*-
"""13_fig_gic.py : growth-incidence curve of hub connectivity.
   Panel (a): elasticity of average pretax income of each WID group to ln GACI_max (OLS and 2SLS Feyrer,
              country-clustered 95% CI). Panel (b): elasticity of the group's income share.
   Input: _gic_dose_results.csv (12_gic_dose.do). Output: fig_gic.png / fig_gic.pdf"""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(D, "_gic_dose_results.csv"), keep_default_na=False, na_values=["", "."])
GROUPS = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01"]
LAB = ["p0–10", "p10–20", "p20–30", "p30–40", "p40–50", "p50–60", "p60–70", "p70–80", "p80–90", "p90–100", "Top 1%", "Top 0.1%"]
C_OLS, C_IV = "#4D4D4D", "#1F5F8B"      # neutral ink for OLS, one accent hue for 2SLS

def pull(block, prefix, spec):
    x = d[(d.block == block) & (d.spec == spec)].set_index("outcome")
    idx = ["%s_%s" % (prefix, g) for g in GROUPS]
    x = x.reindex(idx)
    return x.b.values, x.se.values

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#E6E6E6", "grid.linewidth": 0.6, "axes.axisbelow": True})
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
xs = np.arange(len(GROUPS)); off = 0.18
for ax, (block, prefix, title, ylab) in zip(axes, [
        ("gic", "ln_apt", "(a) Average pretax income of the group", "Elasticity to ln GACI$_{max}$"),
        ("gic_share", "ln_spt", "(b) Income share of the group", "Elasticity to ln GACI$_{max}$")]):
    for spec, col, lab, sh, mk in [("OLS", C_OLS, "OLS", -off, "s"), ("IV", C_IV, "2SLS, Feyrer IV", off, "o")]:
        b, se = pull(block, prefix, spec)
        ax.errorbar(xs + sh, b, yerr=1.96 * se, fmt=mk, ms=4.5, color=col, ecolor=col, elinewidth=1.1, capsize=0, label=lab, zorder=3)
    ax.axhline(0, color="#808080", lw=0.8, zorder=1)
    ax.axvline(9.5, color="#BFBFBF", lw=0.8, ls=":", zorder=1)
    ax.set_xticks(xs); ax.set_xticklabels(LAB, rotation=45, ha="right")
    ax.set_title(title, loc="left", fontsize=9.5)
    ax.set_ylabel(ylab)
    ax.grid(axis="x", visible=False)
# panel a: clip the two imprecise bottom deciles so the curve is legible; note the range in the caption
axes[0].set_ylim(-3.5, 4.5)
axes[1].set_ylim(-5.5, 2.0)
axes[0].legend(frameon=False, loc="lower right")
# reference line: elasticity of the country-wide average income (2SLS), so groups above it gain more than average
ball = d[(d.block == "gic") & (d.spec == "IV") & (d.outcome == "ln_apt_all")].b.iloc[0]
axes[0].axhline(ball, color=C_IV, lw=0.9, ls="--", zorder=2)
axes[0].annotate("mean income, 2SLS = %.2f" % ball, (0.0, ball), xytext=(2, 4), textcoords="offset points", fontsize=7.5, color=C_IV, ha="left")
# direct labels on the two ends of the 2SLS curve in panel (a)
b, se = pull("gic", "ln_apt", "IV")
for i, dy in [(3, -14), (9, 6)]:
    axes[0].annotate("%.2f" % b[i], (i + off, b[i]), xytext=(-4, dy), textcoords="offset points", fontsize=8, color=C_IV, ha="center")
fig.tight_layout(w_pad=2.0)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(D, "fig_gic." + ext), dpi=300 if ext == "png" else None, bbox_inches="tight")
print("saved fig_gic.png / .pdf")
# figure-caption numbers
ols_b, ols_se = pull("gic", "ln_apt", "OLS"); iv_b, iv_se = pull("gic", "ln_apt", "IV")
for g, ob, os_, ib, is_ in zip(GROUPS, ols_b, ols_se, iv_b, iv_se):
    print("%-4s OLS %6.3f (%.3f)   2SLS %6.3f (%.3f)" % (g, ob, os_, ib, is_))
