# -*- coding: utf-8 -*-
"""Static replacement for the SAF Buy-Back Simulator (deck slide 'The only lever').

World aviation CO2 level (Mt, bunker convention, 2023 scheduled traffic held
fixed) along the ReFuelEU blending path, for three life-cycle savings r:
    E(s, r) = E_2023 * (1 - s * r),   E_2023 = 838 Mt
which is the same identity as 04_carbon_price_saf.py, E * [(1-s) + s(1-r)],
applied to the level instead of the carbon price. Reference lines: 2023 level
(838 Mt) and 2023 minus the 356 Mt attributed to post-1996 connectivity growth
(14_attribution_scc.py, Feyrer beta 5.67).
Output: CO2_saf_levels.png (+ console table used on the slide).
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = (r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
        r"\GACI_CO2")
BASE = 838.0            # Mt, world aviation CO2 2023 (bunker convention)
ATTR = 356.4            # Mt attributed to 1996-2023 connectivity growth
PATH = {2023: 0.00, 2025: 0.02, 2030: 0.06, 2035: 0.20, 2040: 0.34,
        2045: 0.42, 2050: 0.70}
RS = [0.5, 0.65, 0.8]
COL = {0.5: '#8ab6d6', 0.65: '#1f4e79', 0.8: '#12314d'}

def E(s, r):
    return BASE * (1 - s * r)

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
INK = '#1f1f1f'
years = sorted(PATH)
fig, ax = plt.subplots(figsize=(8.6, 5.2))
ax.set_axisbelow(True)
ax.yaxis.grid(True, color='#e6e6e6', lw=0.7)
for r in RS:
    vals = [E(PATH[y], r) for y in years]
    ax.plot(years, vals, 'o-', color=COL[r], lw=1.8, ms=6,
            label=f'life-cycle saving r = {int(100*r)}%')
    ax.annotate(f'{vals[-1]:.0f}', (2050, vals[-1]), textcoords='offset points',
                xytext=(7, -4), fontsize=11, color=COL[r])
ax.axhline(BASE, color='#b0413e', lw=1.1, ls=(0, (4, 3)))
ax.annotate(f'2023 level: {BASE:.0f} Mt', (2023, BASE), textcoords='offset points',
            xytext=(4, 6), fontsize=11, color='#b0413e')
ax.axhline(BASE - ATTR, color='#2e7d5b', lw=1.1, ls=(0, (4, 3)))
ax.annotate(f'2023 minus the {ATTR:.0f} Mt attributed to connectivity growth: '
            f'{BASE-ATTR:.0f} Mt', (2023, BASE - ATTR), textcoords='offset points',
            xytext=(4, 6), fontsize=11, color='#2e7d5b')
ax.set_xticks(years)
ax.set_xticklabels([f'{y}\n{int(100*PATH[y])}%' for y in years], fontsize=11)
ax.set_xlabel('ReFuelEU milestone year and SAF blend share', fontsize=12.5,
              color=INK)
ax.set_ylabel('World aviation CO$_2$ (Mt per year)\n2023 traffic held fixed',
              fontsize=12.5, color=INK)
ax.set_ylim(300, 900)
ax.set_xlim(2022, 2052.5)
ax.legend(frameon=False, fontsize=11, loc='lower left')
for sp in ['top', 'right']:
    ax.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(HERE + r"\CO2_saf_levels.png", dpi=200, facecolor='white')
print("wrote CO2_saf_levels.png")
print("year blend  r50  r65  r80")
for y in years:
    print(y, f"{int(100*PATH[y]):>3}%", *[f"{E(PATH[y], r):5.0f}" for r in RS])
print("saved in 2050 (Mt):", [round(BASE - E(0.7, r), 0) for r in RS])
print("bought back (% of 356 Mt):",
      [round(100 * (BASE - E(0.7, r)) / ATTR, 0) for r in RS])
