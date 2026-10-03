# -*- coding: utf-8 -*-
"""Figure: implied connectivity elasticity of trade openness by baseline-income and
   baseline-connectivity QUARTILE, from the interaction-IV estimates (Table het).
   ME(m) = b_main + b_inter * m ; delta-method 95% CI using the reported SEs and the
   reproduced main<->interaction correlation. Times New Roman, paper style."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
INK = '#1f1f1f'

# ---- estimates straight from Table het / the Stata log (openness = g_int) ----
EST = {
    'income':   dict(b_main=1.254132, se_main=0.717470, b_int=-0.242952, se_int=0.122311, corr=-0.866),
    'baseconn': dict(b_main=2.259651, se_main=1.161177, b_int=-1.481524, se_int=0.622443, corr=-0.797),
}

# ---- data: baseline (1996) moderators, mean-centered as in the do-file ----
p = pd.read_csv('gaci_panel_hetero.csv')
for col in p.columns:
    if col not in ('c', 'reg'):
        p[col] = pd.to_numeric(p[col], errors='coerce')
p['g_int'] = p['merch_intensity']

def baseline(var):
    b96 = p[p.y == 1996].set_index('c')[var]
    return p['c'].map(b96)
p['base_lnpc'] = baseline('lnpc')
p['base_cwm']  = baseline('ln_gaci_cwm')
p['inc_c']  = p['base_lnpc'] - p['base_lnpc'].mean()
p['cwm0_c'] = p['base_cwm']  - p['base_cwm'].mean()

def sample_country_vals(modvar):
    """country-level centred moderator over the estimation sample (non-missing key vars)."""
    d = p.copy()
    d['cwm_m'] = d['ln_gaci_cwm'] * d[modvar]
    d['z_m']   = d['tourism_int'] * d[modvar]
    d = d.dropna(subset=['g_int', 'lnpop', 'ln_gaci_cwm', 'cwm_m', 'tourism_int', 'z_m'])
    return d.groupby('c')[modvar].first().dropna()

def me_ci(est, m):
    b = est['b_main'] + est['b_int'] * m
    var = est['se_main']**2 + m**2 * est['se_int']**2 + 2*m*est['corr']*est['se_main']*est['se_int']
    half = 1.96 * np.sqrt(var)
    return b, b - half, b + half

PANELS = [
    ('inc_c',  'income',   'Baseline income quartile\n(1996 GDP per capita)'),
    ('cwm0_c', 'baseconn', 'Baseline connectivity quartile\n(1996 hub quality)'),
]

fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, (modvar, key, xlabel) in zip(axes, PANELS):
    vals = sample_country_vals(modvar)
    q = pd.qcut(vals, 4, labels=[1, 2, 3, 4])
    mq = vals.groupby(q, observed=True).mean()            # representative centred value per quartile
    xs = [1, 2, 3, 4]
    pts = [me_ci(EST[key], mq[k]) for k in xs]
    b   = [t[0] for t in pts]; lo = [t[1] for t in pts]; hi = [t[2] for t in pts]
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#e6e6e6', lw=0.7, zorder=0)
    ax.axhline(0, color='#b0b0b0', lw=0.8, ls=(0, (4, 3)), zorder=1)
    ax.errorbar(xs, b, yerr=[np.array(b)-np.array(lo), np.array(hi)-np.array(b)],
                fmt='o', ms=7, color='#1f4e79', ecolor='#1f4e79',
                elinewidth=1.4, capsize=5, capthick=1.4, zorder=3)
    for x, val in zip(xs, b):
        ax.annotate(f'{val:.2f}', (x, val), textcoords='offset points',
                    xytext=(11, 0), ha='left', va='center',
                    fontsize=12, color=INK, zorder=4)
    ax.set_xticks(xs)
    ax.set_xticklabels(['Q1\n(lowest)', 'Q2', 'Q3', 'Q4\n(highest)'], fontsize=12)
    ax.set_xlim(0.5, 4.5)
    ax.set_xlabel(xlabel, fontsize=13, color=INK, labelpad=8)
    ax.tick_params(labelsize=12, colors=INK, length=4, width=0.7)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color('#888888')

axes[0].set_ylabel('Implied elasticity of trade openness\nwith respect to air connectivity',
                   fontsize=13, color=INK)
fig.subplots_adjust(left=0.10, right=0.985, top=0.97, bottom=0.18, wspace=0.07)
fig.savefig('GACI_hetero_quartile.png', dpi=200, bbox_inches='tight', facecolor='white')
print('wrote GACI_hetero_quartile.png')
for modvar, key, _ in PANELS:
    vals = sample_country_vals(modvar)
    q = pd.qcut(vals, 4, labels=[1, 2, 3, 4]); mq = vals.groupby(q, observed=True).mean()
    print(key, [f"Q{k}: {me_ci(EST[key], mq[k])[0]:+.2f}" for k in [1, 2, 3, 4]])
