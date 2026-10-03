# -*- coding: utf-8 -*-
"""
build_measures_panel.py -- add ln_gaci_max to the main IV panel so we can
compare the three country-level connectivity aggregations from the working
paper (Manuscript_GACI and Economic Development.pdf):

  GACI_sum   = sum of airport GACI in a country-year   -> lnG  (already in panel)
  GACI_max   = max airport GACI in a country-year      -> ln_gaci_max  (BUILT HERE)
  GACI_wmean = seat-capacity-weighted mean GACI        -> ln_gaci_cwm (already in panel)

All three are put on the log scale. Country->ISO3 mapping reuses the exact
logic in build_gaci_panel.py so the max lines up 1:1 with the existing rows.

  in : GACI1996_2024_new_panel_data.csv, ourairports.csv, iso2to3.json,
       gaci_panel_3iv.csv
  out: gaci_panel_measures.csv
"""
import csv, json, collections
import numpy as np
csv.field_size_limit(10**7)

# ---- IATA -> ISO3 (same as build_gaci_panel.py) ----
ap_iso2 = {}
for r in csv.DictReader(open('ourairports.csv', encoding='utf-8', errors='replace')):
    ia = (r.get('iata_code') or '').strip()
    if len(ia) == 3:
        ap_iso2[ia] = r.get('iso_country', '').strip()
iso2to3 = json.load(open('iso2to3.json'))

def iso3_of(airport):
    return iso2to3.get(ap_iso2.get(airport, ''), '')

# ---- max airport GACI per country-year ----
gmax = collections.defaultdict(float)
for r in csv.DictReader(open('GACI1996_2024_new_panel_data.csv',
                              encoding='utf-8', errors='replace')):
    a = r['Airport'].strip()
    c = iso3_of(a)
    if not c:
        continue
    try:
        y = int(list(r.values())[0]); g = float(r['GACI'])
    except Exception:
        continue
    if g > gmax[(c, y)]:
        gmax[(c, y)] = g

# ---- merge onto main panel ----
rows = list(csv.DictReader(open('gaci_panel_3iv.csv', encoding='utf-8')))
fields = list(rows[0].keys())
if 'ln_gaci_max' not in fields:
    fields = fields + ['gaci_max', 'ln_gaci_max']

n_match = 0
for r in rows:
    key = (r['c'], int(float(r['y'])))
    gm = gmax.get(key)
    if gm and gm > 0:
        r['gaci_max'] = gm
        r['ln_gaci_max'] = np.log(gm)
        n_match += 1
    else:
        r['gaci_max'] = ''
        r['ln_gaci_max'] = ''

with open('gaci_panel_measures.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)

print('rows=%d  matched gaci_max=%d (%.1f%%)'
      % (len(rows), n_match, 100.0*n_match/len(rows)))
# quick sanity: max should be >= mean, and log(max) vs existing measures
import statistics as st
lm = [float(r['ln_gaci_max']) for r in rows if r['ln_gaci_max'] != '']
lc = [float(r['ln_gaci_cwm']) for r in rows if r['ln_gaci_cwm'] not in ('', None)]
print('ln_gaci_max  mean=%.3f sd=%.3f min=%.3f max=%.3f'
      % (st.mean(lm), st.pstdev(lm), min(lm), max(lm)))
print('ln_gaci_cwm  mean=%.3f sd=%.3f' % (st.mean(lc), st.pstdev(lc)))
