# -*- coding: utf-8 -*-
"""Base map: global air connectivity (ln GACI sum) by country, 2023. Shared style."""
import numpy as np, pandas as pd
from matplotlib.colors import Normalize
import _mapstyle as ms

p = pd.read_csv('gaci_panel.csv')
g = p[p.y == 2023][['c', 'lnG']].dropna(subset=['lnG']).rename(columns={'lnG': 'val'})

w = ms.load_world(g)
vmin, vmax = float(g['val'].min()), float(g['val'].max())
norm = Normalize(vmin=vmin, vmax=vmax)

ms.render(w, 'val', 'viridis', norm,
          'Air connectivity, $\\ln(\\mathrm{GACI}_{\\mathrm{sum}})$, 2023',
          'GACI_base_map.png',
          tickfmt=lambda x, _: f'{x:.0f}')
print('range:', round(vmin, 2), round(vmax, 2))
