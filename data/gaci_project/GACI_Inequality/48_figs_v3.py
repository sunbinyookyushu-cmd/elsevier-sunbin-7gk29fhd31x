# -*- coding: utf-8 -*-
"""48_figs_v3.py : refined versions of the two distribution figures (paper Figures 1 and 2).
   Fig4_descriptive_v3  a) growth by income group for high/middle/low connectivity-growth terciles (gap shaded),
                        b) high-minus-low difference as a line with 90/95% ribbons
   Fig1_incidence_v3    a) 2SLS elasticity of group income, line + ribbons, mean-income reference, halves shaded,
                        b) same for group income share
   Inputs: _gic_dose_results.csv, _gic_descriptive.csv. Style: _ineqstyle.py (teal/amber/slate, Arial, open axes)."""
import os, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import stats
import _ineqstyle as lz
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D); lz.setup()
plt.rcParams.update({"axes.grid": True, "grid.color": "#ECEEF1", "grid.linewidth": 0.7, "axes.edgecolor": "#555555"})
RD = dict(keep_default_na=False, na_values=["", "."])
gic = pd.read_csv("_gic_dose_results.csv", **RD); des = pd.read_csv("_gic_descriptive.csv", **RD)
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01"]
LAB = ["p0–10", "p10–20", "p20–30", "p30–40", "p40–50", "p50–60", "p60–70", "p70–80", "p80–90", "p90–100", "Top 1%", "Top 0.1%"]
TEAL, AMBER, SLATE, INK = lz.TEAL, lz.AMBER, lz.SLATE, lz.INK
BAND = "#F3F5F7"

def pull(block, prefix, spec="IV"):
    x = gic[(gic.block == block) & (gic.spec == spec)].set_index("outcome").reindex([prefix + g for g in G]); return x.b.values, x.se.values, x.p.values

def ribbon_series(ax, xs, b, se, p, color, neg_color=None, lw=2.4, ms=7.5, sig=0.10):
    """Line through point estimates, 95% (light) and 90% (mid) ribbons, points filled when p<sig."""
    ax.fill_between(xs, b - 1.96 * se, b + 1.96 * se, color=color, alpha=0.13, lw=0, zorder=2)
    ax.fill_between(xs, b - 1.645 * se, b + 1.645 * se, color=color, alpha=0.22, lw=0, zorder=2)
    ax.plot(xs, b, color=color, lw=lw, zorder=4, solid_capstyle="round")
    for xi, bi, pi in zip(xs, b, p):
        s = pi < sig; c = (neg_color if (neg_color and bi < 0) else color) if s else color
        ax.plot(xi, bi, "o", ms=ms, mfc=c if s else "white", mec=c, mew=1.8, zorder=5)

def halves(ax, ylo, yhi, top_x=9.5, label_y=None, show_labels=True):
    """Shade the bottom half of the distribution and mark the top groups."""
    ax.add_patch(Rectangle((-0.5, ylo), 5.0, yhi - ylo, facecolor=BAND, edgecolor="none", zorder=0))
    ax.axvline(4.5, color="#C9CED4", lw=0.9, zorder=1); ax.axvline(top_x, color="#C9CED4", lw=0.9, ls=(0, (2, 3)), zorder=1)
    if show_labels:
        y = label_y if label_y is not None else yhi - 0.06 * (yhi - ylo)
        ax.text(2.0, y, "Bottom half", ha="center", va="top", fontsize=11.5, color="#6B7280")
        ax.text(7.0, y, "Top half", ha="center", va="top", fontsize=11.5, color="#6B7280")
        ax.text(10.5, y, "Top", ha="center", va="top", fontsize=11.5, color="#6B7280")

def finish(ax, xs, ylab, title, letter):
    ax.set_xticks(xs); ax.set_xticklabels(LAB, rotation=45, ha="right"); ax.set_ylabel(ylab); ax.set_title(title, loc="left", pad=10)
    ax.set_xlim(-0.5, len(xs) - 0.5); ax.grid(axis="x", visible=False); lz.panel_letter(ax, letter, x=-0.085, y=1.03)

# ================= Paper Figure 2: incidence (file Fig1_incidence_v3) =================
xs = np.arange(len(G))
fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))
# (a) group income
ax = axes[0]; b, se, p = pull("gic", "ln_apt_")
ylo, yhi = -3.2, 3.6; halves(ax, ylo, yhi)
lz.zero_line(ax)
m = gic[(gic.block == "gic") & (gic.spec == "IV") & (gic.outcome == "ln_apt_all")].b.iloc[0]
ax.axhline(m, color=AMBER, lw=1.6, ls=(0, (5, 3)), zorder=3); ax.plot([-0.25, 0.35], [2.55, 2.55], color=AMBER, lw=1.6, ls=(0, (5, 3)), zorder=6); ax.text(0.5, 2.55, "Mean income of all adults, %.2f" % m, ha="left", va="center", fontsize=11.5, color=AMBER, zorder=6)
ribbon_series(ax, xs, b, se, p, TEAL)
ax.set_ylim(ylo, yhi); finish(ax, xs, "Elasticity of group income to ln GACI", "Average income of the group", "a")
ax.text(0.5, ylo + 0.06, "bands truncated", ha="center", va="bottom", fontsize=9.5, color="#8A94A0")
# (b) group share
ax = axes[1]; b, se, p = pull("gic_share", "ln_spt_")
ylo, yhi = -3.4, 1.6; halves(ax, ylo, yhi)
lz.zero_line(ax); ribbon_series(ax, xs, b, se, p, TEAL, neg_color=AMBER)
ax.set_ylim(ylo, yhi); finish(ax, xs, "Elasticity of income share to ln GACI", "Income share of the group", "b")
ax.text(0.5, ylo + 0.05, "bands truncated", ha="center", va="bottom", fontsize=9.5, color="#8A94A0")
fig.tight_layout(w_pad=3.5); fig.savefig("Fig1_incidence_v3.png", dpi=300, bbox_inches="tight"); fig.savefig("Fig1_incidence_v3.pdf", bbox_inches="tight"); plt.close(fig)

# ================= Paper Figure 1: descriptive growth (file Fig4_descriptive_v3) =================
xs = np.arange(len(des))
fig, axes = plt.subplots(1, 2, figsize=(15, 6.0))
ax = axes[0]
ylo, yhi = 0.2, 3.75; halves(ax, ylo, yhi, show_labels=False)
ax.fill_between(xs, des.low_mean, des.high_mean, color=TEAL, alpha=0.08, lw=0, zorder=1)
ax.plot(xs, des.mid_mean, color=SLATE, lw=1.6, ls=(0, (4, 2)), marker="o", ms=4, zorder=3)
ax.plot(xs, des.low_mean, color=AMBER, lw=2.6, marker="o", ms=6.5, zorder=4, solid_capstyle="round")
ax.plot(xs, des.high_mean, color=TEAL, lw=2.6, marker="o", ms=6.5, zorder=4, solid_capstyle="round")
for col, lab, c in [("high_mean", "High connectivity growth", TEAL), ("mid_mean", "Middle tercile", SLATE), ("low_mean", "Low connectivity growth", AMBER)]:
    ax.annotate(lab, (xs[-1], des[col].iloc[-1]), xytext=(9, 0), textcoords="offset points", ha="left", va="center", fontsize=11.5, color=c)
ax.text(2.0, 3.68, "Bottom half", ha="center", va="top", fontsize=11.5, color="#6B7280"); ax.text(7.0, 3.68, "Top half", ha="center", va="top", fontsize=11.5, color="#6B7280")
ax.set_ylim(ylo, yhi); ax.set_xticks(xs); ax.set_xticklabels(des.label, rotation=45, ha="right"); ax.set_ylabel("Real income growth, % per year")
ax.set_title("Growth of average pretax income by group, 1996–2023", loc="left", pad=10); ax.set_xlim(-0.5, len(des) + 3.6); ax.grid(axis="x", visible=False); lz.panel_letter(ax, "a", x=-0.085, y=1.03)
ax = axes[1]
d, s = des.diff_high_low.values, des.se_diff.values; p = 2 * (1 - stats.norm.cdf(np.abs(d / s)))
ylo, yhi = -0.3, 4.2; halves(ax, ylo, yhi, label_y=4.05)
lz.zero_line(ax); ribbon_series(ax, xs, d, s, p, TEAL)
ax.set_ylim(ylo, yhi); finish(ax, xs, "High minus low tercile, pp per year", "Growth gap between high and low connectivity growth", "b")
fig.tight_layout(w_pad=3.5); fig.savefig("Fig4_descriptive_v3.png", dpi=300, bbox_inches="tight"); fig.savefig("Fig4_descriptive_v3.pdf", bbox_inches="tight"); plt.close(fig)
print("saved Fig1_incidence_v3, Fig4_descriptive_v3")
