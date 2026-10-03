# -*- coding: utf-8 -*-
"""
build_feyrer_iv.py  --  Feyrer (2019, AEJ:Applied) style AIR-vs-SEA time-varying IV.

Idea: a country's distances to world markets are FIXED, but the world transitions
from SEA to AIR transport over time (global aviation grows). Countries that AIR
shortens a lot (relative to sea) gain connectivity disproportionately as aviation
booms -> within-country time variation that SURVIVES country fixed effects.

For country c, year t, summing over foreign countries j (j != c, leave-out):
  air_ma_ct = sum_j pop_jt / d_air(c,j)^THETA      (great-circle, airport-centroids)
  sea_ma_ct = sum_j pop_jt / d_sea(c,j)^THETA      (CERDI port-to-port sea distance)
  a_t       = global aviation intensity in year t, min-max normalised to [0,1]
              (world total seat capacity; the exogenous time shifter)
  feyrer_ct = a_t*air_ma_ct + (1-a_t)*sea_ma_ct    (effective MA shifting sea->air)

Instruments produced (ln):
  ln_feyrer  = ln(feyrer_ct)                        MAIN time-varying IV
  ln_air_ma  = ln(air_ma_ct)                        pure air MA (dies under country FE)
  ln_sea_ma  = ln(sea_ma_ct)                        CONTROL: maritime geography->trade
  feyrer_int = a_t * ln(air_ma_base1996)            Bartik form (base air MA x time)
  adv_int    = a_t * ln(air_ma_base/sea_ma_base)    aviation-ADVANTAGE ratio x time

Exclusion defence: include ln_sea_ma as a CONTROL -> absorbs the direct geography->
trade (shipping/gravity) channel; the residual identifying variation in ln_feyrer is
the AVIATION-SPECIFIC gain, which plausibly reaches trade only THROUGH air connectivity.

Inputs : gaci_panel.csv, airport_coords_merged.csv, ourairports.csv, iso2to3.json,
         wb_pop.json, CERDI_seadistance.dta
Output : gaci_panel_feyrer.csv  (= gaci_panel.csv + the new IV columns)
"""
import csv, json, collections
import numpy as np, pandas as pd
csv.field_size_limit(10**7)
THETA = 1.0   # gravity distance elasticity (Feyrer ~1); try 2.0 as sensitivity

# ---------- airport -> ISO3, country centroid (mean airport lat/lon) ----------
ap_lat, ap_lon, ap_name = {}, {}, []
rows = list(csv.DictReader(open('airport_coords_merged.csv', encoding='utf-8')))
for r in rows:
    ap_lat[r['Airport']] = float(r['lat']); ap_lon[r['Airport']] = float(r['lon'])
ap_iso2 = {}
for r in csv.DictReader(open('ourairports.csv', encoding='utf-8', errors='replace')):
    ia = (r.get('iata_code') or '').strip()
    if len(ia) == 3: ap_iso2[ia] = r.get('iso_country', '').strip()
iso2to3 = json.load(open('iso2to3.json'))
clat = collections.defaultdict(list); clon = collections.defaultdict(list)
for a in ap_lat:
    iso3 = iso2to3.get(ap_iso2.get(a, ''), '')
    if iso3:
        clat[iso3].append(ap_lat[a]); clon[iso3].append(ap_lon[a])
cent = {c: (float(np.mean(clat[c])), float(np.mean(clon[c]))) for c in clat}

# ---------- population ISO3|year ----------
pop = {}
for k, v in json.load(open('wb_pop.json')).items():
    c, y = k.split('|'); pop[(c, int(y))] = float(v)

# ---------- CERDI sea distance (km), both directions ----------
cerdi = pd.read_stata('CERDI_seadistance.dta')
d_sea = {}
for a, b, s in zip(cerdi['iso1'], cerdi['iso2'], cerdi['seadistance']):
    if pd.notna(s) and s > 0:
        d_sea[(a, b)] = float(s); d_sea[(b, a)] = float(s)

# ---------- great-circle air distance between country centroids ----------
def gc(c, j):
    la1, lo1 = np.radians(cent[c]); la2, lo2 = np.radians(cent[j])
    h = np.sin((la2-la1)/2)**2 + np.cos(la1)*np.cos(la2)*np.sin((lo2-lo1)/2)**2
    return 2*6371.0*np.arcsin(np.sqrt(min(1.0, h)))

# ---------- panel countries / years + global aviation index a_t ----------
panel = pd.read_csv('gaci_panel.csv')
years = sorted(panel['y'].unique())
countries = sorted(set(panel['c'].unique()) & set(cent.keys()))
capsum_by_year = panel.groupby('y')['cap_sum'].sum()
cap = capsum_by_year.reindex(years).astype(float)
a_t = ((cap - cap.min()) / (cap.max() - cap.min())).to_dict()   # min-max -> [0,1]

# ---------- compute MAs per country-year ----------
# foreign set for c = countries j (j!=c) having centroid, pop, AND a sea distance to c
rec = {}
base_air, base_sea = {}, {}
BASE = years[0]
for c in countries:
    Js = [j for j in countries if j != c and (c, j) in d_sea and j in cent]
    if not Js:
        continue
    dair = {j: gc(c, j) for j in Js}
    dsea = {j: d_sea[(c, j)] for j in Js}
    wair = {j: dair[j]**(-THETA) if dair[j] > 0 else 0.0 for j in Js}
    wsea = {j: dsea[j]**(-THETA) if dsea[j] > 0 else 0.0 for j in Js}
    for y in years:
        air = sum(pop.get((j, y), 0.0)*wair[j] for j in Js)
        sea = sum(pop.get((j, y), 0.0)*wsea[j] for j in Js)
        if air <= 0 or sea <= 0:
            continue
        at = a_t[y]
        fey = at*air + (1-at)*sea
        rec[(c, y)] = dict(ln_air_ma=np.log(air), ln_sea_ma=np.log(sea),
                           ln_feyrer=np.log(fey), a_t=at)
        if y == BASE:
            base_air[c] = np.log(air); base_sea[c] = np.log(sea)

# interaction (Bartik) instruments use base-year (1996) geography x time index a_t
for (c, y), d in rec.items():
    if c in base_air:
        d['feyrer_int'] = a_t[y]*base_air[c]
        d['adv_int']    = a_t[y]*(base_air[c]-base_sea[c])

# ---------- merge onto gaci_panel and write ----------
newcols = ['ln_air_ma', 'ln_sea_ma', 'ln_feyrer', 'a_t', 'feyrer_int', 'adv_int']
for col in newcols:
    panel[col] = [rec.get((c, y), {}).get(col, '') for c, y in zip(panel['c'], panel['y'])]
panel.to_csv('gaci_panel_feyrer.csv', index=False, encoding='utf-8')

nz = sum(1 for c, y in zip(panel['c'], panel['y']) if (c, y) in rec)
print('wrote gaci_panel_feyrer.csv  rows=%d  with-Feyrer-IV=%d  countries=%d  THETA=%.1f'
      % (len(panel), nz, len(countries), THETA))
print('a_t range: %.3f (%d) -> %.3f (%d)' % (a_t[years[0]], years[0], a_t[years[-1]], years[-1]))
