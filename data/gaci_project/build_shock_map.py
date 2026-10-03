# -*- coding: utf-8 -*-
"""COVID shock map: implied goods-trade-flow loss from the 2019->2020 connectivity
   collapse, by country. Uses TOTAL connectivity (GACI sum) and the sum intensity
   elasticity 0.659 (hub-quality mean is too volatile for a one-year shock).
   loss_c = goods_value_c,2019 x (1 - exp(beta x dlnGACI_c,2019->2020)),  d<0 => loss."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import geopandas as gpd

B = 0.659   # sum intensity elasticity
p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp'] = np.exp(p['lngdp'])
p['mshr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['gv'] = p['mshr'] / 100.0 * p['gdp']
d = (p[p.y == 2020].set_index('c')['lnG'] - p[p.y == 2019].set_index('c')['lnG']).rename('d')
gv19 = p[p.y == 2019].set_index('c')['gv'].rename('gv')
df = pd.concat([d, gv19], axis=1).dropna(subset=['d']).reset_index()
df['loss_bn'] = (df['gv'].fillna(0) * (1 - np.exp(B * df['d']))) / 1e9   # >0 = loss

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

vmax = np.nanpercentile(np.abs(df['loss_bn']), 95)
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
fig, ax = plt.subplots(figsize=(16, 8.5))
w.plot(column='loss_bn', ax=ax, cmap='Reds', norm=plt.Normalize(0, vmax), legend=True,
       missing_kwds={'color': '#e6e6e6'}, edgecolor='white', linewidth=0.2,
       legend_kwds={'label': 'Implied goods-trade-flow loss, US$ billion (colour capped at 95th pct)',
                    'shrink': 0.55, 'orientation': 'horizontal', 'pad': 0.02, 'aspect': 45})
ax.set_title('COVID-19 (2019->2020): implied goods-trade loss from the air-connectivity collapse',
             fontsize=14, fontweight='bold')
ax.axis('off'); plt.tight_layout()
plt.savefig('GACI_shock_map.png', dpi=150, bbox_inches='tight')
print('wrote GACI_shock_map.png')
print('top 8 losses:', df.nlargest(8, 'loss_bn')[['c', 'loss_bn']].round(0).values.tolist())
