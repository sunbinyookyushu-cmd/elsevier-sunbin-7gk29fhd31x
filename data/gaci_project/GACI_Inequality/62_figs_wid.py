# -*- coding: utf-8 -*-
"""62_figs_wid.py : figures for the WID-main manuscript (draft_v4_wid_20260928/figures), own style (_ineqstyle.py).
   FigW2_incidence     (a) 2SLS elasticity of group income by WID group, line + 90/95% ribbons, mean-income reference, bottom 30% shaded
                       (b) same for group income share
   FigW3_where         dot plots by split sample: (a) bottom-30% share, (b) bottom-30% income, (c) mean income
   FigW4_attribution   (a) countries with the largest implied changes in the bottom-30% share, (b) map of implied bottom-30% share change,
                       (c) map of implied mean-income growth
   Inputs: _wid_results.csv, _wid_aggregate_bycountry.csv"""
import os, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
import _ineqstyle as lz
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D); lz.setup()
plt.rcParams.update({"axes.grid": True, "grid.color": "#ECEEF1", "grid.linewidth": 0.7, "axes.edgecolor": "#555555"})
OUT = os.path.join(D, "draft_v4_wid_20260928", "figures"); os.makedirs(OUT, exist_ok=True)
R = pd.read_csv("_wid_results.csv"); R["sample"] = R["sample"].fillna(""); R["panel"] = R["panel"].fillna("")
TEAL, AMBER, SLATE, INK, BAND = lz.TEAL, lz.AMBER, lz.SLATE, lz.INK, "#F3F5F7"
def g(**kw):
    m = R
    for k, v in kw.items(): m = m[m[k] == v]
    return m.iloc[0]
def save(fig, name): fig.savefig(os.path.join(OUT, name + ".png"), dpi=300, bbox_inches="tight"); fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight"); plt.close(fig)

def ribbon_series(ax, xs, b, se, p, color, neg_color=None, lw=2.4, ms=7.5, sig=0.10):
    ax.fill_between(xs, b - 1.96 * se, b + 1.96 * se, color=color, alpha=0.13, lw=0, zorder=2); ax.fill_between(xs, b - 1.645 * se, b + 1.645 * se, color=color, alpha=0.22, lw=0, zorder=2)
    ax.plot(xs, b, color=color, lw=lw, zorder=4, solid_capstyle="round")
    for xi, bi, pi in zip(xs, b, p):
        s = pi < sig; c = (neg_color if (neg_color and bi < 0) else color) if s else color; ax.plot(xi, bi, "o", ms=ms, mfc=c if s else "white", mec=c, mew=1.8, zorder=5)
def bands(ax, ylo, yhi):
    ax.add_patch(Rectangle((-0.5, ylo), 3.0, yhi - ylo, facecolor=BAND, edgecolor="none", zorder=0)); ax.axvline(2.5, color="#C9CED4", lw=0.9, zorder=1); ax.axvline(9.5, color="#C9CED4", lw=0.9, ls=(0, (2, 3)), zorder=1)
    y = yhi - 0.06 * (yhi - ylo); ax.text(1.0, y, "Bottom 30%", ha="center", va="top", fontsize=11.5, color="#6B7280"); ax.text(6.0, y, "p30–100", ha="center", va="top", fontsize=11.5, color="#6B7280"); ax.text(10.5, y, "Top", ha="center", va="top", fontsize=11.5, color="#6B7280")

# ================= Figure 2: incidence =================
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01"]; LAB = ["p0–10", "p10–20", "p20–30", "p30–40", "p40–50", "p50–60", "p60–70", "p70–80", "p80–90", "p90–100", "Top 1%", "Top 0.1%"]
xs = np.arange(len(G)); fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))
for ax, (pan, pre, title, ylab, letter, ylo, yhi) in zip(axes, [("income", "ln_apt_", "Average income of the group", "Elasticity of group income to ln GACI$_{max}$", "a", -2.6, 3.4), ("share", "ln_spt_", "Income share of the group", "Elasticity of income share to ln GACI$_{max}$", "b", -3.4, 1.4)]):
    rr = [g(block="incidence", panel=pan, spec="2SLS", outcome=pre + k) for k in G]; b = np.array([r.b for r in rr]); se = np.array([r.se for r in rr]); p = np.array([r.p for r in rr])
    bands(ax, ylo, yhi); lz.zero_line(ax)
    if pan == "income":
        m = g(block="incidence", panel="income", spec="2SLS", outcome="ln_apt_all").b
        ax.axhline(m, color=AMBER, lw=1.6, ls=(0, (5, 3)), zorder=3); ax.plot([-0.25, 0.35], [2.55, 2.55], color=AMBER, lw=1.6, ls=(0, (5, 3)), zorder=6); ax.text(0.5, 2.55, "Mean income of all adults, %.2f" % m, ha="left", va="center", fontsize=11.5, color=AMBER, zorder=6)
    ribbon_series(ax, xs, b, se, p, TEAL, neg_color=AMBER if pan == "share" else None)
    ax.set_ylim(ylo, yhi); ax.set_xticks(xs); ax.set_xticklabels(LAB, rotation=45, ha="right"); ax.set_ylabel(ylab); ax.set_title(title, loc="left", pad=10); ax.set_xlim(-0.5, len(xs) - 0.5); ax.grid(axis="x", visible=False); lz.panel_letter(ax, letter, x=-0.085, y=1.03)
    ax.text(0.5, ylo + 0.05, "bands truncated", ha="center", va="bottom", fontsize=9.5, color="#8A94A0")
fig.tight_layout(w_pad=3.5); save(fig, "FigW2_incidence")

# ================= Figure 3: where =================
ROWS = [("full", "Full sample", ("growth_stage", "full", "full")), ("g_low", "Baseline hub: smallest tercile", ("growth_stage", "tercile", "low")), ("g_mid", "Baseline hub: middle tercile", ("growth_stage", "tercile", "mid")),
        ("c_hi", "Airport network concentrated", ("splits", "airport_concentration", "above")), ("c_lo", "Airport network dispersed", ("splits", "airport_concentration", "below")),
        ("u_hi", "Urbanisation above median", ("splits", "urbanisation", "above")), ("u_lo", "Urbanisation below median", ("splits", "urbanisation", "below")),
        ("y_hi", "Baseline income above median", ("splits", "baseline_income", "above")), ("y_lo", "Baseline income below median", ("splits", "baseline_income", "below")),
        ("e1", "1996–2007", ("splits", "era", "1996-2007")), ("e2", "2010–2023", ("splits", "era", "2010-2023"))]
fig, axes = plt.subplots(1, 3, figsize=(13.5, 6.6), sharey=True)
for ax, (o, title, letter, xlim) in zip(axes, [("ln_spt_b30", "Bottom-30% share", "a", (-4.2, 2.2)), ("ln_apt_b30", "Bottom-30% income", "b", (-4.2, 5.2)), ("ln_apt_all", "Mean income", "c", (-1.2, 4.2))]):
    ys = np.arange(len(ROWS))[::-1]; b, se, p = [], [], []
    for key, lab, (blk, pan, smp) in ROWS:
        r = g(block=blk, panel=pan, spec="2SLS", sample=smp, outcome=o); b.append(r.b); se.append(r.se); p.append(r.p)
    lz.zero_line(ax, orient="h"); lz.coef_points(ax, ys, np.array(b), np.array(se), np.array(p), orient="h", labels=True, label_offset=7, size=8)
    for yy in [ys[0] - 0.5, ys[2] - 0.5, ys[4] - 0.5, ys[6] - 0.5, ys[8] - 0.5]: ax.axhline(yy, color="#E4E7EB", lw=0.8)
    ax.set_yticks(ys); ax.set_yticklabels([lab for _, lab, _ in ROWS]); ax.set_xlim(*xlim); ax.set_ylim(-0.7, len(ROWS) - 0.3); ax.set_xlabel("Elasticity to ln GACI$_{max}$"); ax.set_title(title, loc="left", pad=8); ax.grid(axis="y", visible=False)
    lz.panel_letter(ax, letter, x=(-0.62 if letter == "a" else -0.1), y=1.02)
fig.tight_layout(w_pad=2.5); save(fig, "FigW3_where")

# ================= Figure 4: attribution =================
ag = pd.read_csv("_wid_aggregate_bycountry.csv"); ag = ag.rename(columns={"index": "c"}) if "index" in ag.columns else ag
if "c" not in ag.columns: ag = ag.rename(columns={ag.columns[0]: "c"})
top = pd.concat([ag.nlargest(6, "implied_b30sh_pts"), ag.nsmallest(12, "implied_b30sh_pts")]).sort_values("implied_b30sh_pts")
fig = plt.figure(figsize=(15, 13)); gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.9], height_ratios=[1, 1], wspace=0.08, hspace=0.12)
ax = fig.add_subplot(gs[:, 0]); ys = np.arange(len(top))
for i, r in enumerate(top.itertuples()): lz.lollipop(ax, i, r.implied_b30sh_pts, fmt="%+.2f")
ax.set_yticks(ys); ax.set_yticklabels(top.c); ax.axvline(0, color="#666666", lw=1); ax.set_xlabel("Implied change in bottom-30% share (points)"); ax.grid(axis="y", visible=False); ax.set_xlim(top.implied_b30sh_pts.min() * 1.35, top.implied_b30sh_pts.max() * 1.6 + 0.3); lz.panel_letter(ax, "a", x=-0.3, y=1.01)
w = lz.world_map(ag[["c", "implied_b30sh_pts", "implied_all_pct"]], key="c")
ax2 = fig.add_subplot(gs[0, 1]); lo, hi = np.nanpercentile(w.implied_b30sh_pts, 2), 0.0
lz.draw_map(ax2, w, "implied_b30sh_pts", lz.mono_cmap(AMBER).reversed(), Normalize(vmin=lo, vmax=hi), title="Implied change in bottom-30% share, 1996–2023 (points)", fig=fig); lz.panel_letter(ax2, "b", x=0.0, y=0.98)
ax3 = fig.add_subplot(gs[1, 1]); hi2 = np.nanpercentile(w.implied_all_pct, 98)
lz.draw_map(ax3, w, "implied_all_pct", lz.mono_cmap(TEAL), Normalize(vmin=min(0, np.nanmin(w.implied_all_pct)), vmax=hi2), title="Implied growth of mean income from hub connectivity, 1996–2023 (%)", fig=fig); lz.panel_letter(ax3, "c", x=0.0, y=0.98)
save(fig, "FigW4_attribution")
print("saved FigW2, FigW3, FigW4")
