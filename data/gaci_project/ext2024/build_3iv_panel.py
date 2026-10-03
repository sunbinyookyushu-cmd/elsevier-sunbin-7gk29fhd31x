# -*- coding: utf-8 -*-
"""gaci_panel_hetero.csv + UNESCO per-category endowments -> gaci_panel_3iv.csv
   nat_e/mix_e/cult_e = max cumulative count of Natural/Mixed/Cultural sites per country (time-invariant, as in the
   original 3iv panel); z_* = tour_shift x ln(1+endowment)."""
import csv, json, collections, numpy as np, pandas as pd
iso2to3 = json.load(open('iso2to3.json'))
by = {k: collections.defaultdict(list) for k in ('Natural', 'Mixed', 'Cultural')}
for r in csv.DictReader(open('uh_csv.csv', encoding='utf-8-sig', errors='replace')):
    try: yr = int(str(r['date_inscribed'])[:4])
    except Exception: continue
    cat = r.get('category', '')
    if cat not in by: continue
    for i2 in (r.get('iso_codes', '') or '').replace(';', ',').split(','):
        i3 = iso2to3.get(i2.strip().upper())
        if i3: by[cat][i3].append(yr)
p = pd.read_csv('gaci_panel_hetero.csv')
ymax = p.groupby('c')['y'].max().to_dict()
def endow(cat, c): return sum(1 for yy in by[cat].get(c, []) if yy <= ymax[c])
p['nat_e']  = p['c'].map(lambda c: endow('Natural', c))
p['mix_e']  = p['c'].map(lambda c: endow('Mixed', c))
p['cult_e'] = p['c'].map(lambda c: endow('Cultural', c))
for e in ('nat', 'mix', 'cult'):
    p['z_' + e] = p['tour_shift'] * np.log1p(p[e + '_e'])
p.to_csv('gaci_panel_3iv.csv', index=False)
print('wrote gaci_panel_3iv.csv', p.shape, 'years', p.y.min(), p.y.max())
