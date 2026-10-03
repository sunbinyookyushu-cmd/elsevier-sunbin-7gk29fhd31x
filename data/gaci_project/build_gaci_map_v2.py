# -*- coding: utf-8 -*-
"""Refined world map: GACI-implied goods-trade gain from connectivity growth, 1996-2023,
   on the INTENSITY (openness) channel. Shared style (_mapstyle), signed-log colour.
   implied_c = goods_value_c,2023 x (1 - exp(-beta_int x dlnGACI_c)),  beta_int = 1.302."""
import json
import numpy as np, pandas as pd
from matplotlib.colors import SymLogNorm
import _mapstyle as ms

B_VOL = 1.302   # intensity (openness) elasticity on ln_gaci_cwm (hub quality)
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

w = ms.load_world(df)
V = float(np.nanmax(np.abs(df['trade_usd'])))            # ~2063 (China)
norm = SymLogNorm(linthresh=25, linscale=0.5, vmin=-V, vmax=V, base=10)

ms.render(w, 'trade_usd', 'RdBu_r', norm,
          'Implied goods-trade gain, US\\$ billion  (signed-log scale)',
          'GACI_implied_map.png',
          ticks=[-400, -100, 0, 100, 400, 1600], signed=True)
print('top 8:', df.nlargest(8, 'trade_usd')[['c', 'trade_usd']].round(0).values.tolist())
