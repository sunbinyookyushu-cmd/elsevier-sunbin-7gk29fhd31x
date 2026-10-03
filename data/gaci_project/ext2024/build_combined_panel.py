# -*- coding: utf-8 -*-
"""Merge the Feyrer air/sea instrument (+ sea market-access control) into the hetero panel
   so we can run an OVER-IDENTIFIED IV: ln_gaci_cwm = tourism_int + feyrer_int.
   -> gaci_panel_combined.csv"""
import numpy as np, pandas as pd

h = pd.read_csv('gaci_panel_hetero.csv')                 # tourism_int, ln_remote, moderators, cwm, outcomes
f = pd.read_csv('gaci_panel_feyrer.csv')[['c', 'y', 'feyrer_int', 'ln_sea_ma', 'ln_air_ma']]
f = f.apply(lambda s: pd.to_numeric(s, errors='coerce') if s.name not in ('c',) else s)

m = h.merge(f, on=['c', 'y'], how='left')
both = m.dropna(subset=['tourism_int', 'feyrer_int'])
print('hetero rows           :', len(h))
print('rows with BOTH instr  :', len(both), '(%.0f%%)' % (100*len(both)/len(h)))
print('countries with both   :', both['c'].nunique(), 'of', h['c'].nunique())
print('year range with both  :', int(both['y'].min()), '-', int(both['y'].max()))
print('countries MISSING feyrer:', sorted(set(h['c']) - set(both['c']))[:25])

# quick relevance peek (raw corr of each instrument with the treatment, within-ish)
for z in ['tourism_int', 'feyrer_int']:
    sub = m.dropna(subset=[z, 'ln_gaci_cwm'])
    print('corr(%s, ln_gaci_cwm) = %.3f' % (z, np.corrcoef(sub[z], sub['ln_gaci_cwm'])[0, 1]))

m.to_csv('gaci_panel_combined.csv', index=False)
print('\nwrote gaci_panel_combined.csv')
