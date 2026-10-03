# -*- coding: utf-8 -*-
"""Extend global tourism demand to 2020-2023 (UNWTO recovery ratios vs 2019) and
rebuild the tourism-IV panel for 1996-2023 (captures the COVID collapse + Russia years)."""
import json, numpy as np, pandas as pd
tour = {int(k): float(v) for k, v in json.load(open('world_tourism.json')).items()}   # 1996-2019 (World Bank ST.INT.ARVL, world)
v19 = tour[2019]
# UNWTO international tourist arrivals, ratio to 2019 peak (well-documented COVID path):
#   2020 -72% , 2021 -69% , 2022 -34% , 2023 -12%
ratio = {2020: 0.278, 2021: 0.311, 2022: 0.657, 2023: 0.887, 2024: 0.99}
for y, r in ratio.items():
    tour[y] = r * v19
json.dump({str(k): v for k, v in sorted(tour.items())}, open('world_tourism_ext.json', 'w'))

p = pd.read_csv('gaci_panel.csv')                  # 1996-2023, has unesco_cum_nat, lng, controls
merch = json.load(open('merch_trade.json'))
tv = pd.Series(tour); lo, hi = tv.min(), tv.max()
shift = {y: (v - lo) / (hi - lo) for y, v in tour.items()}
endow = p.groupby('c')['unesco_cum_nat'].max().to_dict()
p['tour_shift']  = p['y'].map(shift)
p['nat_endow']   = p['c'].map(endow)
p['merch_share'] = [merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])]
p = p[p['tour_shift'].notna() & p['merch_share'].notna()].copy()
p['merch_share']     = p['merch_share'].astype(float)
p['merch_intensity'] = np.log(p['merch_share'] / 100.0)
p['tourism_int']     = p['tour_shift'] * np.log1p(p['nat_endow'])
p['tourism_cum']     = p['tour_shift'] * np.log1p(p['unesco_cum_nat'])
p.to_csv('gaci_panel_tourism_ext.csv', index=False, encoding='utf-8')
print('wrote gaci_panel_tourism_ext.csv rows=%d years %d-%d countries=%d'
      % (len(p), p['y'].min(), p['y'].max(), p['c'].nunique()))
print('tour_shift (normalised):')
for y in [1996,2000,2010,2019,2020,2021,2022,2023,2024]:
    print('  %d: %.3f' % (y, shift[y]))
