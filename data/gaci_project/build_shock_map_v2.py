# -*- coding: utf-8 -*-
"""COVID shock map: implied goods-trade-flow loss from the 2019->2020 connectivity
   collapse, by country. TOTAL connectivity (GACI sum), sum intensity elasticity 0.659.
   loss_c = goods_value_c,2019 x (1 - exp(beta x dlnGACI_c)),  >0 = loss. Shared style."""
import json
import numpy as np, pandas as pd
from matplotlib.colors import PowerNorm
import _mapstyle as ms

B = 0.659
p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp'] = np.exp(p['lngdp'])
p['mshr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['gv'] = p['mshr'] / 100.0 * p['gdp']
d = (p[p.y == 2020].set_index('c')['lnG'] - p[p.y == 2019].set_index('c')['lnG']).rename('d')
gv19 = p[p.y == 2019].set_index('c')['gv'].rename('gv')
df = pd.concat([d, gv19], axis=1).dropna(subset=['d']).reset_index()
df['loss_bn'] = (df['gv'].fillna(0) * (1 - np.exp(B * df['d']))) / 1e9   # >0 = loss
df['loss_pos'] = df['loss_bn'].clip(lower=0)                            # gains -> 0 (white)

w = ms.load_world(df)
vmax = float(df['loss_pos'].max())
norm = PowerNorm(gamma=0.45, vmin=0, vmax=vmax)   # expand small losses, compress the few big hubs

ms.render(w, 'loss_pos', 'Reds', norm,
          'Implied goods-trade-flow loss, US\\$ billion',
          'GACI_shock_map.png',
          ticks=[0, 10, 50, 100, 200], tickfmt=lambda x, _: f'{x:,.0f}')
print('max loss:', round(vmax, 0))
print('top 8 losses:', df.nlargest(8, 'loss_bn')[['c', 'loss_bn']].round(0).values.tolist())
