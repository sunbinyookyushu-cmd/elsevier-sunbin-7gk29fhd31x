# -*- coding: utf-8 -*-
"""Growth-inclusive SAF scenarios (response to Ray/Lisa, 2026-09-04).

17_saf_levels_fig.py holds 2023 scheduled traffic fixed, so it is a pure
blending identity, E(s, r) = E_2023 * (1 - s*r), and it overstates what SAF
buys. This script combines the ReFuelEU blending path with continued
connectivity growth, projected with the MATURE-NETWORK elasticity:

    E(t) = E_2023 * exp(beta * g * (t - 2023)) * (1 - s_t * r)

  beta : 2SLS elasticity of ln bunker CO2 on ln GACI (cwm), 2010-2023
         excluding 2020-21 = 3.005 (SE 1.187, p = .011, KP F = 10.7,
         N = 2,065; _temporal_excovid_cl.csv, ED Table 1 Panel C).
         The full-sample estimate 5.669 is carried as a high case.
         beta is the reduced form on emissions, so the efficiency gain
         (intensity elasticity -0.979 over the same window) is ALREADY
         netted out; do not apply the seat-km elasticity (3.984) and then
         subtract efficiency again.
  g    : mean annual change in ln GACI (cwm), country mean:
         0.0074 (2010-2019, central) and 0.0045 (2010-2023, low, COVID in).
  s_t  : ReFuelEU blend share, linear between milestone years.
  r    : life-cycle saving of the SAF blend, 50 / 65 / 80 percent.

Reference levels: 838 Mt (world aviation CO2 2023, bunker convention) and
838 - 356.4 = 482 Mt (2023 minus the emissions attributed to 1996-2023
connectivity growth, 14_attribution_scc.py, Feyrer beta 5.67).

Outputs: CO2_saf_growth.png, _saf_growth_scenarios.csv, console summary.
"""
import os
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

BASE = 838.0            # Mt, world aviation CO2 2023 (bunker convention)
ATTR = 356.4            # Mt attributed to 1996-2023 connectivity growth
BETA = {'mature': 3.005, 'full': 5.669}
GROWTH = {'central': 0.0074, 'low': 0.0045}
PATH = {2023: 0.00, 2025: 0.02, 2030: 0.06, 2035: 0.20, 2040: 0.34,
        2045: 0.42, 2050: 0.70}
RS = [0.5, 0.65, 0.8]
COL = {0.5: '#8ab6d6', 0.65: '#1f4e79', 0.8: '#12314d'}

MILES = sorted(PATH)
YEARS = np.arange(2023, 2051)


def blend(y):
    """ReFuelEU blend share, linear between milestone years."""
    return float(np.interp(y, MILES, [PATH[m] for m in MILES]))


def emissions(y, r, beta, g):
    return BASE * np.exp(beta * g * (y - 2023)) * (1 - blend(y) * r)


# ---- scenario table --------------------------------------------------------
rows = []
for bname, beta in BETA.items():
    for gname, g in GROWTH.items():
        for r in RS + [0.0]:
            for y in MILES:
                rows.append({'beta_case': bname, 'beta': beta,
                             'growth_case': gname, 'dln_gaci_per_yr': g,
                             'co2_growth_pct_yr': 100 * (np.exp(beta * g) - 1),
                             'lca_saving_r': r, 'year': y,
                             'blend_share': blend(y),
                             'co2_Mt': emissions(y, r, beta, g),
                             'co2_Mt_fixed_traffic': BASE * (1 - blend(y) * r)})
sc = pd.DataFrame(rows)
sc.to_csv(os.path.join(HERE, '_saf_growth_scenarios.csv'), index=False)

# ---- figure: two growth cases, mature-network beta -------------------------
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
INK = '#1f1f1f'
fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.4), sharey=True)
beta = BETA['mature']
for ax, gname in zip(axes, ['central', 'low']):
    g = GROWTH[gname]
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#e6e6e6', lw=0.7)
    ax.plot(YEARS, [emissions(y, 0.0, beta, g) for y in YEARS],
            color='#7a7a7a', lw=1.6, ls=(0, (5, 2)), label='no SAF')
    for r in RS:
        ax.plot(YEARS, [emissions(y, r, beta, g) for y in YEARS],
                color=COL[r], lw=1.9,
                label='life-cycle saving r = %d%%' % int(100 * r))
        ax.plot(MILES, [emissions(y, r, beta, g) for y in MILES], 'o',
                color=COL[r], ms=5)
        v50 = emissions(2050, r, beta, g)
        ax.annotate('%.0f' % v50, (2050, v50), textcoords='offset points',
                    xytext=(6, -4), fontsize=10.5, color=COL[r])
    ax.plot(YEARS, [BASE * (1 - blend(y) * 0.65) for y in YEARS],
            color='#b0413e', lw=1.3, ls=(0, (1.5, 1.8)),
            label='r = 65%, 2023 traffic fixed (current draft)')
    ax.axhline(BASE, color='#b0413e', lw=0.9, ls=(0, (4, 3)), alpha=.55)
    ax.axhline(BASE - ATTR, color='#2e7d5b', lw=0.9, ls=(0, (4, 3)), alpha=.8)
    ax.set_xticks(MILES)
    ax.set_xticklabels(['%d\n%d%%' % (y, int(100 * PATH[y])) for y in MILES],
                       fontsize=10.5)
    ax.set_xlim(2022.5, 2052.5)
    ax.set_xlabel('ReFuelEU milestone year and SAF blend share', fontsize=12,
                  color=INK)
    ax.set_title('%s growth: $\\Delta$ln GACI = %.4f/yr $\\rightarrow$ '
                 '%.1f%% CO$_2$/yr'
                 % (gname, g, 100 * (np.exp(beta * g) - 1)),
                 fontsize=12, color=INK)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
axes[0].set_ylabel('World aviation CO$_2$ (Mt per year)', fontsize=12.5,
                   color=INK)
axes[0].annotate('2023 level: %.0f Mt' % BASE, (2023.2, BASE),
                 textcoords='offset points', xytext=(0, -15), fontsize=10.5,
                 color='#b0413e')
axes[0].annotate('2023 minus the %.0f Mt attributed to\nconnectivity growth: '
                 '%.0f Mt' % (ATTR, BASE - ATTR), (2023.2, BASE - ATTR),
                 textcoords='offset points', xytext=(0, 6), fontsize=10.5,
                 color='#2e7d5b')
axes[0].set_ylim(380, 1650)
axes[1].legend(frameon=False, fontsize=10.5, loc='upper left')
fig.suptitle('SAF blending with continued connectivity growth, mature-network '
             'elasticity $\\beta$ = %.3f' % beta, fontsize=13.5, color=INK,
             y=0.985)
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(os.path.join(HERE, 'CO2_saf_growth.png'), dpi=200,
            facecolor='white')
print('wrote CO2_saf_growth.png, _saf_growth_scenarios.csv')

# ---- console summary -------------------------------------------------------
for bname, beta in BETA.items():
    for gname, g in GROWTH.items():
        print('\nbeta = %.3f (%s), dlnGACI = %.4f (%s) -> %.2f%% CO2 per year'
              % (beta, bname, g, gname, 100 * (np.exp(beta * g) - 1)))
        print('  no SAF   : ' + '  '.join(
            '%d:%.0f' % (y, emissions(y, 0.0, beta, g)) for y in MILES))
        for r in RS:
            print('  r = %2d%%   : ' % int(100 * r) + '  '.join(
                '%d:%.0f' % (y, emissions(y, r, beta, g)) for y in MILES))
print('\nfixed-traffic benchmark (current draft, 17_saf_levels_fig.py):')
for r in RS:
    print('  r = %2d%%   : ' % int(100 * r) + '  '.join(
        '%d:%.0f' % (y, BASE * (1 - blend(y) * r)) for y in MILES))
b, g = BETA['mature'], GROWTH['central']
print('\n2050, mature beta, central growth: no-SAF %.0f Mt; ' % emissions(2050, 0, b, g)
      + '; '.join('r=%d%% %.0f Mt' % (int(100 * r), emissions(2050, r, b, g))
                  for r in RS))
print('2050 gap vs the %.0f Mt connectivity-free level: ' % (BASE - ATTR)
      + '; '.join('r=%d%% %+.0f Mt' % (int(100 * r),
                                       emissions(2050, r, b, g) - (BASE - ATTR))
                  for r in RS))
