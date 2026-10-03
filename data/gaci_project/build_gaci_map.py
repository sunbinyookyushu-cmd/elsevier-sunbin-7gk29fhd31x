# -*- coding: utf-8 -*-
"""Single world map: GACI-implied goods-trade gain from connectivity growth, 1996-2023,
   on the INTENSITY (openness) channel.
   implied_c = goods_value_c,2023 x (1 - exp(-beta_int x dlnGACI_c)),  beta_int = 0.659 (full-sample IV)."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import geopandas as gpd

B_VOL = 1.302   # intensity (openness) elasticity on ln_gaci_cwm (hub quality); isolates trade-intensity channel
TCOL  = 'ln_gaci_cwm'

p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp'] = np.exp(p['lngdp'])
p['mshr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['gv'] = p['mshr'] / 100.0 * p['gdp']
pp = p[(p.y >= 1996) & (p.y <= 2023)].dropna(subset=[TCOL]).sort_values('y')
dG = (pp.groupby('c').last()[TCOL] - pp.groupby('c').first()[TCOL])
gv23 = p[p.y == 2023].set_index('c')['gv']
df = pd.DataFrame({'dG': dG, 'gv': gv23}).dropna(subset=['dG']).reset_index()
df['trade_usd'] = (df['gv'].fillna(0) * (1 - np.exp(-B_VOL * df['dG']))) / 1e9   # US$ billion

gj = json.load(open('_world.geojson'))
w = gpd.GeoDataFrame.from_features(gj['features'])
def iso(r):
    for k in ['ISO_A3', 'ISO_A3_EH', 'ADM0_A3']:
        v = r.get(k)
        if isinstance(v, str) and v not in ('-99', ''):
            return v
    return None
w['iso3'] = w.apply(iso, axis=1)
w = w[w['NAME'] != 'Antarctica'].merge(df, left_on='iso3', right_on='c', how='left')

vmax = np.nanpercentile(np.abs(df['trade_usd']), 95)   # cap so US/China do not wash out the rest
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
fig, ax = plt.subplots(figsize=(16, 8.5))
w.plot(column='trade_usd', ax=ax, cmap='RdBu_r', norm=norm, legend=True,
       missing_kwds={'color': '#e6e6e6'}, edgecolor='white', linewidth=0.2,
       legend_kwds={'label': 'Implied goods-trade gain, US$ billion (colour capped at 95th pct)',
                    'shrink': 0.55, 'orientation': 'horizontal', 'pad': 0.02, 'aspect': 45})
ax.set_title('GACI-implied goods-trade gain from air-connectivity growth, 1996-2023 (intensity channel)',
             fontsize=14, fontweight='bold')
ax.axis('off'); plt.tight_layout()
plt.savefig('GACI_implied_map.png', dpi=150, bbox_inches='tight')
print('wrote GACI_implied_map.png (single panel, implied trade volume US$)')
print('top 8:', df.nlargest(8, 'trade_usd')[['c', 'trade_usd']].round(0).values.tolist())
