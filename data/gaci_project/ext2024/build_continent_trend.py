# -*- coding: utf-8 -*-
"""Task 4: implied GACI effect on TRADE INTENSITY (goods openness) by CONTINENT, 1996-2024.
   Main treatment = hub quality ln_gaci_cwm; intensity-channel elasticity beta_int_cwm = 1.302
   (Table 1 Panel B, ln(goods/GDP) on ln_gaci_cwm).
   implied openness gain since 1996 for country c, year t:
       eff_{c,t} = 100 * ( exp( beta * (cwm_{c,t} - cwm_{c,1996}) ) - 1 )   [percent]
   aggregated to a continent as the goods-trade-weighted mean across its countries each year."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

BETA = 1.208   # ln(goods/GDP) on ln_gaci_cwm, full-sample IV (Table 1 Panel B, intensity channel)

p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp']       = np.exp(p['lngdp'])
p['merch_shr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']
p['cont']      = p['reg'].astype(str).str[:2]
p = p[(p.y >= 1996) & (p.y <= 2024)].dropna(subset=['ln_gaci_cwm']).copy()

# baseline (first available, 1996 where present) hub quality per country
base = p.sort_values('y').groupby('c')['ln_gaci_cwm'].first().rename('cwm0')
p = p.merge(base, on='c')
p['d_cwm'] = p['ln_gaci_cwm'] - p['cwm0']
p['eff']   = 100.0 * (np.exp(BETA * p['d_cwm']) - 1.0)        # implied % openness gain vs 1996

CONT = {'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'LA': 'Latin America',
        'ME': 'Middle East', 'NA': 'North America', 'SW': 'Pacific/Oceania'}

def wmean(g):
    w = g['goods_val'].fillna(0.0)
    if w.sum() <= 0: return g['eff'].mean()
    return np.average(g['eff'], weights=w)

trend = (p.groupby(['cont', 'y']).apply(wmean).rename('eff').reset_index())
trend = trend[trend['cont'].isin(CONT)]

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
INK = '#1f1f1f'
fig, ax = plt.subplots(figsize=(11, 6.2))
colors = plt.cm.tab10(np.linspace(0, 1, len(CONT)))
order = ['AS', 'ME', 'EU', 'LA', 'AF', 'NA', 'SW']
for i, k in enumerate(order):
    s = trend[trend['cont'] == k].sort_values('y')
    if s.empty: continue
    ax.plot(s['y'], s['eff'], marker='o', ms=4, lw=2.0, color=colors[i], label=CONT[k])
ax.axhline(0, color='#9a9a9a', lw=0.8)
ax.set_xlabel('Year', fontsize=14, color=INK)
ax.set_ylabel('Implied gain in goods-trade openness vs. 1996 (%)', fontsize=14, color=INK)
ax.legend(loc='upper left', fontsize=12.5, ncol=2, frameon=False, handlelength=1.8,
          columnspacing=1.2, labelspacing=0.4)
ax.set_xlim(1996, 2025)
ax.grid(True, color='#ececec', lw=0.7); ax.set_axisbelow(True)
ax.tick_params(labelsize=12.5, colors=INK, length=4, width=0.7)
for sp in ['top', 'right']:
    ax.spines[sp].set_visible(False)
for sp in ['left', 'bottom']:
    ax.spines[sp].set_color('#888888')
plt.tight_layout(); plt.savefig('GACI_continent_trend.png', dpi=200, bbox_inches='tight', facecolor='white')

print("=== 2023 endpoint: implied goods-openness gain since 1996 (trade-weighted %, by continent) ===")
e23 = trend[trend['y'] == 2024].set_index('cont')['eff'].sort_values(ascending=False)
for k, v in e23.items():
    print("  %-16s %+6.1f%%" % (CONT.get(k, k), v))
trend.assign(continent=trend['cont'].map(CONT)).to_csv('GACI_continent_trend.csv', index=False)
print("\nwrote GACI_continent_trend.png, GACI_continent_trend.csv  (beta_int_cwm = %.3f)" % BETA)
