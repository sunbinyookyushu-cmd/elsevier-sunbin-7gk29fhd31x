# -*- coding: utf-8 -*-
# NOTE (package copy, 11 Sep 2026): only the path lines were changed so the
# script finds its inputs in this flat folder. The figure code is untouched.
"""Figure: hub efficiency curve, 2023. Median CO2 per 1,000 seat-km by GACI
   ventile, with bootstrapped 95% CI on the median and international seat-km
   share on a second axis. House style."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
INK = '#1f1f1f'
rng = np.random.default_rng(20260822)

import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = pd.read_csv(os.path.join(HERE, "airport_co2_panel.csv"))
t = p[(p.year == 2023) & (p.dep_seat_km > 0)].copy()
t["kg"] = 1000 * t.co2_bunker / t.dep_seat_km
t["q"] = pd.qcut(t.ln_gaci, 20, labels=False)

rows = []
for q, s in t.groupby("q"):
    med = s.kg.median()
    boots = [s.kg.sample(len(s), replace=True, random_state=None).median()
             for _ in range(400)]
    boots = np.array([np.median(rng.choice(s.kg.to_numpy(), len(s))) for _ in range(400)])
    rows.append(dict(q=q, gaci=s.GACI.mean(), med=med,
                     lo=np.percentile(boots, 2.5), hi=np.percentile(boots, 97.5),
                     intl=s.intl_share_skm.mean()))
e = pd.DataFrame(rows).sort_values("q")

fig, ax = plt.subplots(figsize=(8.8, 5.2))
ax.set_axisbelow(True)
ax.yaxis.grid(True, color='#e6e6e6', lw=0.7)
ax.fill_between(e.q, e.lo, e.hi, color='#1f4e79', alpha=0.15, lw=0)
ax.plot(e.q, e.med, 'o-', color='#1f4e79', lw=1.8, ms=5.5,
        label='CO$_2$ per 1,000 seat-km (median, kg)')
ax.set_xlabel('Airport connectivity (GACI) ventile, 2023', fontsize=12.5, color=INK)
ax.set_ylabel('CO$_2$ per 1,000 seat-km (kg)', fontsize=12.5, color=INK)
ax.set_xticks([0, 4, 9, 14, 19])
ax.set_xticklabels(['1\n(least\nconnected)', '5', '10', '15', '20\n(most\nconnected)'],
                   fontsize=10.5)
ax2 = ax.twinx()
ax2.plot(e.q, 100 * e.intl, 's--', color='#c0504d', lw=1.4, ms=4.5,
         label='International share of seat-km (%)')
ax2.set_ylabel('International share of seat-km (%)', fontsize=12.5, color='#c0504d')
ax2.tick_params(colors='#c0504d')
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=11, loc='upper center')
for sp in ['top']:
    ax.spines[sp].set_visible(False)
    ax2.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "CO2_efficiency_curve.png"), dpi=200, facecolor='white')
print('wrote CO2_efficiency_curve.png')
print(e[['q', 'med', 'lo', 'hi', 'intl']].round(2).to_string(index=False))
