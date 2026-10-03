# -*- coding: utf-8 -*-
"""Figure: flexible (quintile-bin) reduced-form effect of the tourism instrument
   on trade openness, by baseline income, baseline connectivity and remoteness.
   Reads _rf_nonlinear.csv written by gaci_rf_nonlinear.do. Paper style."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
INK = '#1f1f1f'

r = pd.read_csv('_rf_nonlinear.csv')

PANELS = [
    ('inc', 'Baseline income quintile\n(1996 GDP per capita)'),
    ('con', 'Baseline connectivity quintile\n(1996 hub quality)'),
    ('rem', 'Remoteness quintile\n(mean sea distance)'),
]

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), sharey=True)
for ax, (key, xlabel) in zip(axes, PANELS):
    d = r[r['mod'] == key].sort_values('bin')
    xs = d['bin'].to_numpy()
    b = d['b'].to_numpy()
    half = 1.96 * d['se'].to_numpy()
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#e6e6e6', lw=0.7, zorder=0)
    ax.axhline(0, color='#b0b0b0', lw=0.8, ls=(0, (4, 3)), zorder=1)
    ax.errorbar(xs, b, yerr=half, fmt='o', ms=7, color='#1f4e79', ecolor='#1f4e79',
                elinewidth=1.4, capsize=5, capthick=1.4, zorder=3)
    for x, val in zip(xs, b):
        ax.annotate(f'{val:.2f}', (x, val), textcoords='offset points',
                    xytext=(10, 0), ha='left', va='center',
                    fontsize=11, color=INK, zorder=4)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(['Q1\n(lowest)', 'Q2', 'Q3', 'Q4', 'Q5\n(highest)'], fontsize=11)
    ax.set_xlim(0.5, 5.7)
    ax.set_xlabel(xlabel, fontsize=12.5, color=INK, labelpad=8)
    ax.tick_params(labelsize=11, colors=INK, length=4, width=0.7)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color('#888888')

axes[0].set_ylabel('Reduced-form effect of the\ntourism instrument on trade openness',
                   fontsize=12.5, color=INK)
fig.subplots_adjust(left=0.075, right=0.99, top=0.97, bottom=0.20, wspace=0.06)
fig.savefig('GACI_rf_quintile.png', dpi=200, bbox_inches='tight', facecolor='white')
print('wrote GACI_rf_quintile.png')
for key, _ in PANELS:
    d = r[r['mod'] == key].sort_values('bin')
    print(key, [f"Q{int(k)}: {v:+.3f}" for k, v in zip(d['bin'], d['b'])])
