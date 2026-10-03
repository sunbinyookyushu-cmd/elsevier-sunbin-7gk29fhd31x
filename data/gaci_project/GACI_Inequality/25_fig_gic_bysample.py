# -*- coding: utf-8 -*-
"""25_fig_gic_bysample.py : incidence curve by development stage.
   (a) by baseline-connectivity tercile: low (precisely zero) vs middle (the effect); high omitted (unidentified, KP F < 1).
   (b) by era: 1996-2007 network expansion vs 2010-2023 mature network (excl. 2020-21).
   Each point: 2SLS elasticity of the group's average income to ln GACI_max, 95% CI (country-clustered);
   dashed line = mean-income elasticity of the same subsample. Input: _gic_bysample_results.csv. Output: fig_gic_bysample.png/.pdf"""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
D = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(D, "_gic_bysample_results.csv"), keep_default_na=False, na_values=["", "."])
GROUPS = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1"]
LAB = ["p0–10", "p10–20", "p20–30", "p30–40", "p40–50", "p50–60", "p60–70", "p70–80", "p80–90", "p90–100", "Top 1%"]
C1, C2 = "#4D4D4D", "#1F5F8B"
def pull(smp, prefix="ln_apt_"):
    x = d[d["sample"] == smp].set_index("outcome").reindex([prefix + g for g in GROUPS])
    return x.b.values, x.se.values
def meanel(smp):
    x = d[(d["sample"] == smp) & (d.outcome == "ln_apt_all")]
    return (x.b.iloc[0], x.kpf.iloc[0], int(x.N.iloc[0])) if len(x) else (np.nan, np.nan, 0)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#E6E6E6", "grid.linewidth": 0.6, "axes.axisbelow": True})
fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.7), sharey=True)
xs = np.arange(len(GROUPS)); off = 0.18
PANELS = [("(a) By baseline connectivity", [("con_low", "Low tercile", C1, "s"), ("con_mid", "Middle tercile", C2, "o")]),
          ("(b) By era", [("era_2010_2023x", "2010–2023 (excl. 2020–21)", C1, "s"), ("era_1996_2007", "1996–2007", C2, "o")]),
          ("(c) By baseline GDP per capita", [("inc_mid", "Middle tercile", C1, "s"), ("inc_high", "High tercile", C2, "o")])]
for ax, (title, series) in zip(axes, PANELS):
    for smp, lab, col, mk in series:
        b, se = pull(smp); m, F, N = meanel(smp)
        sh = -off if col == C1 else off
        ax.errorbar(xs + sh, b, yerr=1.96 * se, fmt=mk, ms=4.5, color=col, ecolor=col, elinewidth=1.1, capsize=0, zorder=3, label="%s (KP F = %.1f, N = %s)" % (lab, F, format(N, ",")))
        if not np.isnan(m): ax.axhline(m, color=col, lw=0.9, ls="--", zorder=2)
    ax.axhline(0, color="#808080", lw=0.8, zorder=1); ax.axvline(9.5, color="#BFBFBF", lw=0.8, ls=":", zorder=1)
    ax.set_xticks(xs); ax.set_xticklabels(LAB, rotation=45, ha="right"); ax.set_title(title, loc="left", fontsize=9.5); ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left", fontsize=7.5)
axes[0].set_ylabel("Elasticity of group income to ln GACI$_{max}$ (2SLS)"); axes[0].set_ylim(-4, 6)
fig.text(0.01, -0.03, "Note: 2SLS with the Feyrer instrument, ln population, country and year FE; 95% CI clustered by country. Dashed lines: elasticity of mean income in the same subsample. "
         "The top connectivity tercile and the low income tercile are omitted (KP F < 1). Bottom two deciles are imprecise in every subsample.", fontsize=7, color="#555555", ha="left")
fig.tight_layout(w_pad=2.0)
for ext in ("png", "pdf"): fig.savefig(os.path.join(D, "fig_gic_bysample." + ext), dpi=300, bbox_inches="tight")
print("saved fig_gic_bysample.png/pdf")
for smp in ["full", "con_low", "con_mid", "con_high", "era_1996_2007", "era_2010_2023x", "con_mid_era1", "inc_low", "inc_mid", "inc_high", "gdp_low", "gdp_mid", "gdp_high"]:
    m, F, N = meanel(smp); tb = d[(d["sample"] == smp) & (d.outcome == "ln_apt_top_bot")]; b5 = d[(d["sample"] == smp) & (d.outcome == "ln_spt_b50")]; gi = d[(d["sample"] == smp) & (d.outcome == "ln_gini_mkt")]
    f = lambda x: "%.2f (%.2f) p=%.2f" % (x.b.iloc[0], x.se.iloc[0], x.p.iloc[0]) if len(x) else "--"
    print("%-16s F=%5.1f N=%5d | Gini %s | mean %.2f | top-bot %s | b50 share %s" % (smp, F, N, f(gi), m, f(tb), f(b5)))
