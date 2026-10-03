# -*- coding: utf-8 -*-
"""
build_tourism_iv.py  --  Tourism-demand x UNESCO-heritage instrument for connectivity,
with a GOODS-only (merchandise) trade outcome (services/tourism excluded).

Instrument logic (clean exclusion for a GOODS-trade outcome):
  UNESCO natural/mixed heritage does NOT directly cause goods trade; it draws leisure
  air travel, hence connectivity. Goods trade is reached ONLY through connectivity
  (belly-hold cargo, business links). Time variation from the global tourism boom.

  tour_shift_t   = world international tourist arrivals (ST.INT.ARVL), min-max to [0,1]
  nat_endow_c    = country's total natural+mixed UNESCO sites (fixed endowment)
  tourism_int_ct = tour_shift_t * ln(1 + nat_endow_c)          [Bartik: shift x endowment]
  tourism_cum_ct = tour_shift_t * ln(1 + unesco_cum_nat_ct)    [shift x time-varying stock]

Outcome (goods only):
  merch_share     = merchandise trade % GDP   (TG.VAL.TOTL.GD.ZS, services EXCLUDED)
  merch_intensity = ln(merch_share/100) = ln(goods trade / GDP) = goods openness

Inputs : gaci_panel.csv, world_tourism.json, merch_trade.json
Output : gaci_panel_tourism.csv   (sample restricted to 1996-2019 = tourism-shift years)
"""
import json
import numpy as np, pandas as pd

p = pd.read_csv('gaci_panel.csv')
tour = {int(k): float(v) for k, v in json.load(open('world_tourism.json')).items()}
merch = json.load(open('merch_trade.json'))            # "ISO3|year" -> merch % GDP

# global tourism shift, min-max to [0,1]
tv = pd.Series(tour); lo, hi = tv.min(), tv.max()
shift = {y: (v - lo) / (hi - lo) for y, v in tour.items()}

# fixed natural+mixed heritage endowment per country (max cumulative over sample)
endow = p.groupby('c')['unesco_cum_nat'].max().to_dict()

p['tour_shift']     = p['y'].map(shift)
p['nat_endow']      = p['c'].map(endow)
p['merch_share']    = [merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])]

p = p[p['tour_shift'].notna() & p['merch_share'].notna()].copy()   # 1996-2019, goods available
p['merch_share']    = p['merch_share'].astype(float)
p['merch_intensity']= np.log(p['merch_share'] / 100.0)
p['tourism_int']    = p['tour_shift'] * np.log1p(p['nat_endow'])
p['tourism_cum']    = p['tour_shift'] * np.log1p(p['unesco_cum_nat'])
p['ln_nat_endow']   = np.log1p(p['nat_endow'])

p.to_csv('gaci_panel_tourism.csv', index=False, encoding='utf-8')
print('wrote gaci_panel_tourism.csv  rows=%d  countries=%d  years %d-%d'
      % (len(p), p['c'].nunique(), p['y'].min(), p['y'].max()))
print('tour_shift: %.3f (%d) -> %.3f (%d)' % (shift[1996], 1996, shift[2019], 2019))
print('countries with >=1 natural/mixed site: %d / %d'
      % ((p.groupby('c')['nat_endow'].max() > 0).sum(), p['c'].nunique()))
print('merch_intensity mean=%.3f  vs  (services-incl) trade_intensity proxy n/a' % p['merch_intensity'].mean())
