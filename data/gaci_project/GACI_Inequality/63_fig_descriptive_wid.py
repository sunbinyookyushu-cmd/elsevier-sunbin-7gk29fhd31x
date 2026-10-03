# -*- coding: utf-8 -*-
"""63_fig_descriptive_wid.py (2026-10-01): descriptive growth-incidence figure on the WID estimation sample.
   Replaces Fig4_descriptive_v3 (48_figs_v3.py), whose country set was conditioned on SWIID availability (138 countries).
   Sample rule = the estimation sample of 60_wid_analysis.py (country-years with WID decile incomes, GACI and the instrument,
   1996-2023) with a first-to-last span of at least 15 years, i.e. the 162 countries of the aggregate accounting.
   For each country: annualised log change of the average pretax income of each WID group and of ln GACI_max between its first and
   last year; countries split into terciles of GACI growth. Output: _desc_wid.csv, draft_v4_wid_20260928/figures/FigW1_descriptive.png/.pdf"""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import stats
import _ineqstyle as lz
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D); lz.setup()
plt.rcParams.update({"axes.grid": True, "grid.color": "#ECEEF1", "grid.linewidth": 0.7, "axes.edgecolor": "#555555"})
OUT = os.path.join(D, "draft_v4_wid_20260928", "figures")
TEAL, AMBER, SLATE, BAND = lz.TEAL, lz.AMBER, lz.SLATE, "#F3F5F7"
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01"]
LAB = ["p0–10", "p10–20", "p20–30", "p30–40", "p40–50", "p50–60", "p60–70", "p70–80", "p80–90", "p90–100", "Top 1%", "Top 0.1%"]
MIN_SPAN = 15

p = pd.read_csv("ineq_panel.csv", low_memory=False); e = pd.read_csv("ineq_panel_ext.csv", low_memory=False)
keep = ["c", "y"] + [c for c in e.columns if (c.startswith("spt_") or c.startswith("ln_apt_")) and c not in p.columns]
p = p.merge(e[keep], on=["c", "y"], how="left")
for c in p.columns:
    if c not in ("c", "reg"): p[c] = pd.to_numeric(p[c], errors="coerce")
p = p.dropna(subset=["ln_apt_all", "spt_d1", "spt_d10", "ln_gaci_max", "lnpop", "feyrer_int"]); p = p[(p.y >= 1996) & (p.y <= 2023)]
cols = ["ln_apt_" + g for g in G]
d = p.dropna(subset=cols)[["c", "y", "ln_gaci_max"] + cols].sort_values(["c", "y"])
rows = []
for c, g in d.groupby("c"):
    f, l = g.iloc[0], g.iloc[-1]; span = int(l.y - f.y)
    if span < MIN_SPAN: continue
    r = {"c": c, "y0": int(f.y), "y1": int(l.y), "span": span, "dg": 100 * (l.ln_gaci_max - f.ln_gaci_max) / span}
    for k in G: r[k] = 100 * (l["ln_apt_" + k] - f["ln_apt_" + k]) / span
    rows.append(r)
X = pd.DataFrame(rows); X["terc"] = pd.qcut(X.dg, 3, labels=["low", "mid", "high"])
print("countries", len(X), "| per tercile", X.terc.value_counts().to_dict(), "| GACI growth %/yr by tercile:"); print(X.groupby("terc", observed=True).dg.agg(["mean", "min", "max"]).round(2))
summ = []
for k, lab in zip(G, LAB):
    lo, mi, hi = (X.loc[X.terc == t, k] for t in ["low", "mid", "high"]); diff = hi.mean() - lo.mean(); se = np.sqrt(hi.var(ddof=1) / len(hi) + lo.var(ddof=1) / len(lo))
    summ.append({"group": k, "label": lab, "low_mean": lo.mean(), "mid_mean": mi.mean(), "high_mean": hi.mean(), "diff_high_low": diff, "se_diff": se, "p": 2 * (1 - stats.norm.cdf(abs(diff / se))), "n_low": len(lo), "n_mid": len(mi), "n_high": len(hi)})
des = pd.DataFrame(summ); des.to_csv("_desc_wid.csv", index=False); X.to_csv("_desc_wid_countries.csv", index=False)
print(des[["label", "low_mean", "mid_mean", "high_mean", "diff_high_low", "se_diff", "p"]].round(2).to_string(index=False))

def ribbon_series(ax, xs, b, se, p, color, lw=2.4, ms=7.5, sig=0.10):
    ax.fill_between(xs, b - 1.96 * se, b + 1.96 * se, color=color, alpha=0.13, lw=0, zorder=2); ax.fill_between(xs, b - 1.645 * se, b + 1.645 * se, color=color, alpha=0.22, lw=0, zorder=2)
    ax.plot(xs, b, color=color, lw=lw, zorder=4, solid_capstyle="round")
    for xi, bi, pi in zip(xs, b, p): ax.plot(xi, bi, "o", ms=ms, mfc=color if pi < sig else "white", mec=color, mew=1.8, zorder=5)
def band30(ax, ylo, yhi):
    ax.add_patch(Rectangle((-0.5, ylo), 3.0, yhi - ylo, facecolor=BAND, edgecolor="none", zorder=0)); ax.axvline(2.5, color="#C9CED4", lw=0.9, zorder=1); ax.axvline(9.5, color="#C9CED4", lw=0.9, ls=(0, (2, 3)), zorder=1)
def finish(ax, xs, ylab, title, letter, xmax=None):
    ax.set_xticks(xs); ax.set_xticklabels(LAB, rotation=45, ha="right"); ax.set_ylabel(ylab); ax.set_title(title, loc="left", pad=10)
    ax.set_xlim(-0.5, xmax if xmax else len(xs) - 0.5); ax.grid(axis="x", visible=False); lz.panel_letter(ax, letter, x=-0.085, y=1.03)

xs = np.arange(len(des)); fig, axes = plt.subplots(1, 2, figsize=(15, 6.0))
ax = axes[0]; ylo = min(des.low_mean.min(), 0) - 0.2; yhi = des.high_mean.max() + 0.9; band30(ax, ylo, yhi)
ax.fill_between(xs, des.low_mean, des.high_mean, color=TEAL, alpha=0.08, lw=0, zorder=1)
ax.plot(xs, des.mid_mean, color=SLATE, lw=1.6, ls=(0, (4, 2)), marker="o", ms=4, zorder=3)
ax.plot(xs, des.low_mean, color=AMBER, lw=2.6, marker="o", ms=6.5, zorder=4, solid_capstyle="round"); ax.plot(xs, des.high_mean, color=TEAL, lw=2.6, marker="o", ms=6.5, zorder=4, solid_capstyle="round")
for col, lab, c in [("high_mean", "High connectivity growth", TEAL), ("mid_mean", "Middle tercile", SLATE), ("low_mean", "Low connectivity growth", AMBER)]:
    ax.annotate(lab, (xs[-1], des[col].iloc[-1]), xytext=(9, 0), textcoords="offset points", ha="left", va="center", fontsize=11.5, color=c)
ax.text(1.0, yhi - 0.05, "Bottom 30%", ha="center", va="top", fontsize=11.5, color="#6B7280"); ax.text(6.0, yhi - 0.05, "Upper 70%", ha="center", va="top", fontsize=11.5, color="#6B7280")
ax.set_ylim(ylo, yhi); finish(ax, xs, "Real income growth, % per year", "Growth of average pretax income by group, 1996–2023", "a", xmax=len(des) + 3.6)
ax = axes[1]; dd, s, pv = des.diff_high_low.values, des.se_diff.values, des.p.values
ylo, yhi = min((dd - 1.96 * s).min(), 0) - 0.2, (dd + 1.96 * s).max() + 0.4; band30(ax, ylo, yhi); lz.zero_line(ax); ribbon_series(ax, xs, dd, s, pv, TEAL)
ax.set_ylim(ylo, yhi); finish(ax, xs, "High minus low tercile, pp per year", "Growth gap between high and low connectivity growth", "b")
fig.tight_layout(w_pad=3.5); fig.savefig(os.path.join(OUT, "FigW1_descriptive.png"), dpi=300, bbox_inches="tight"); fig.savefig(os.path.join(OUT, "FigW1_descriptive.pdf"), bbox_inches="tight"); plt.close(fig)
print("saved FigW1_descriptive")
