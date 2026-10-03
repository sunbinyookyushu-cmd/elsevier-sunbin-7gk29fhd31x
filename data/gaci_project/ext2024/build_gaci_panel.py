# -*- coding: utf-8 -*-
"""
build_gaci_panel.py  --  ONE script that builds the single master dataset gaci_panel.csv
from raw inputs. Replaces the older fragmented build scripts.

Raw inputs (all in this folder):
  GACI1996_2024_new_panel_data.csv  airport-year centralities (Year,Airport,Region,Degree,
                                    TotalCapacity,Eigen,NorClose,NorBetweenness,RegionalImportance,GACI)
  airport_coords_merged.csv         Airport,lat,lon  (OpenFlights+OurAirports, 98.4% of panel)
  ourairports.csv                   IATA -> iso_country (ISO2)
  iso2to3.json                      ISO2 -> ISO3 (World Bank)
  wb_pop.json                       "ISO3|year" -> population (WDI SP.POP.TOTL)
  wdi_covariates.json               "name|ISO3|year" -> trade_pct_gdp, gdp_usd, gdppc_kd, land_km2
  uh_csv.csv                        UNESCO World Heritage list (data.unesco.org whc001 export)

Output: gaci_panel.csv  (country-year; one row per country-year)
"""
import csv, json, collections
import numpy as np
csv.field_size_limit(10**7)
THETA = 2.0  # distance decay for market-access instrument

# ---------- geography ----------
ap, lat, lon = [], [], []
for r in csv.DictReader(open('airport_coords_merged.csv', encoding='utf-8')):
    ap.append(r['Airport']); lat.append(float(r['lat'])); lon.append(float(r['lon']))
ap = np.array(ap); n = len(ap); latd = np.array(lat)
latr = np.radians(lat); lonr = np.radians(lon); R = 6371.0; la = latr[:, None]
a = np.sin((latr[None, :]-la)/2)**2 + np.cos(la)*np.cos(latr[None, :])*np.sin((lonr[None, :]-lonr[:, None])/2)**2
D = 2*R*np.arcsin(np.sqrt(np.clip(a, 0, 1))); np.fill_diagonal(D, 0)

ap_iso2 = {}
for r in csv.DictReader(open('ourairports.csv', encoding='utf-8', errors='replace')):
    ia = (r.get('iata_code') or '').strip()
    if len(ia) == 3: ap_iso2[ia] = r.get('iso_country', '').strip()
iso2to3 = json.load(open('iso2to3.json'))
ISO3 = np.array([iso2to3.get(ap_iso2.get(a, ''), '') for a in ap])
apidx = {a: i for i, a in enumerate(ap)}

pop = {}
for k, v in json.load(open('wb_pop.json')).items():
    c, y = k.split('|'); pop[(c, int(y))] = v
wdi = {}
for k, v in json.load(open('wdi_covariates.json')).items():
    nm, c, y = k.split('|'); wdi[(nm, c, int(y))] = v
def gg(nm, c, y): return wdi.get((nm, c, y))
# EXT2024: land area is quasi time-invariant; carry forward the latest available WDI value
_land = {}
for (nm_, c_, y_), v_ in wdi.items():
    if nm_ == 'land_km2' and v_ not in (None, '', 0): _land.setdefault(c_, {})[y_] = v_
def gland(c, y):
    d = _land.get(c)
    if not d: return None
    if y in d: return d[y]
    prev = [yy for yy in d if yy <= y]
    return d[max(prev)] if prev else d[min(d)]


# ---------- predicted GACI (market-access instrument lnZ), country-year ----------
# Frankel-Romer / market-access IV: own-country population MUST be excluded
# (leave-one-out) so the instrument is determined ONLY by FOREIGN population / dist^2.
# The OLD version left out only the self-airport (matrix diagonal) but still leaked
# own-country population through OTHER domestic airports -- which get a huge 1/D^2 weight
# at short distance -> lnZ ended up driven mostly by own population (endogenous, and
# collinear with the lnpop control). Mask ALL same-country pairs to fix this.
with np.errstate(divide='ignore'):
    Wd = np.where(D > 0, D**(-THETA), 0.0)
same = (ISO3[:, None] == ISO3[None, :])      # True for same-country airport pairs
Wd_lo = np.where(same, 0.0, Wd)              # leave-out: drop ALL own-country pairs
predG = {}       # leave-out (proper Frankel-Romer): foreign population only -> lnZ
predG_own = {}   # old version (own-country population leaks in) -> lnZ_own, comparison only
for y in range(1996, 2025):
    m = np.array([pop.get((ISO3[i], y), 0.0) for i in range(n)])
    MA = Wd_lo @ m; MA_own = Wd @ m
    o = collections.defaultdict(float); o_own = collections.defaultdict(float)
    for i in range(n):
        if ISO3[i]:
            o[ISO3[i]] += MA[i]; o_own[ISO3[i]] += MA_own[i]
    predG[y] = o; predG_own[y] = o_own

# ---------- actual connectivity aggregates, country-year ----------
COMP = ['Degree', 'TotalCapacity', 'Eigen', 'NorClose', 'NorBetweenness', 'RegionalImportance']
short = {'Degree': 'deg', 'TotalCapacity': 'cap', 'Eigen': 'eig', 'NorClose': 'close',
         'NorBetweenness': 'betw', 'RegionalImportance': 'regimp'}
aggG = collections.defaultdict(float); aggCap = collections.defaultdict(float)
comp_sum = {k: collections.defaultdict(float) for k in COMP}
cap_x_gaci = collections.defaultdict(float)            # for capacity-weighted-mean GACI
nair = collections.defaultdict(int)
cregion = collections.defaultdict(collections.Counter); clat = collections.defaultdict(list)
for r in csv.DictReader(open('GACI1996_2024_new_panel_data.csv', encoding='utf-8', errors='replace')):
    a = r['Airport'].strip()
    if a not in apidx or not ISO3[apidx[a]]:
        continue
    c = ISO3[apidx[a]]; i = apidx[a]
    try:
        y = int(list(r.values())[0]); g = float(r['GACI']); cap = float(r['TotalCapacity'])
    except Exception:
        continue
    aggG[(c, y)] += g; aggCap[(c, y)] += cap; cap_x_gaci[(c, y)] += cap*g; nair[(c, y)] += 1
    for k in COMP: comp_sum[k][(c, y)] += float(r[k])
    cregion[c][r['Region']] += 1; clat[c].append(abs(latd[i]))
creg = {c: cnt.most_common(1)[0][0] for c, cnt in cregion.items()}
cabslat = {c: float(np.mean(v)) for c, v in clat.items()}

# ---------- UNESCO cumulative counts ----------
byc = collections.defaultdict(list); byc_nat = collections.defaultdict(list)
for r in csv.DictReader(open('uh_csv.csv', encoding='utf-8-sig', errors='replace')):
    try: yr = int(str(r['date_inscribed'])[:4])
    except Exception: continue
    cat = r.get('category', '')
    for i2 in (r.get('iso_codes', '') or '').replace(';', ',').split(','):
        i3 = iso2to3.get(i2.strip().upper())
        if not i3: continue
        byc[i3].append(yr)
        if cat in ('Natural', 'Mixed'): byc_nat[i3].append(yr)
def cum(d, c, y): return sum(1 for yy in d.get(c, []) if yy <= y)

# ---------- assemble ----------
def L(x): return np.log(x) if (x is not None and x > 0) else ''
recs = []
for (c, y), G in aggG.items():
    tp = gg('trade_pct_gdp', c, y); gdp = gg('gdp_usd', c, y)
    pc = gg('gdppc_kd', c, y); land = gland(c, y)
    P = pop.get((c, y)); z = predG[y].get(c); z_own = predG_own[y].get(c)
    if None in (tp, gdp, pc, land, P) or G <= 0 or tp <= 0 or not z or z <= 0:
        continue
    na = nair[(c, y)]; capt = aggCap[(c, y)]
    cwm = cap_x_gaci[(c, y)]/capt if capt > 0 else None
    rec = dict(
        c=c, y=y, reg=creg.get(c, 'NA'),
        trade_share=tp, ln_tradevol=np.log(tp/100*gdp), lngdp=np.log(gdp),
        lnG=np.log(G), ln_gaci_cwm=L(cwm), ln_gaci_mean=np.log(G/na), lnCap=np.log(capt),
        gaci_cwmean=(cwm if cwm else ''), gaci_mean=G/na,
        ln_unesco=L(cum(byc, c, y)), unesco_cum=cum(byc, c, y), unesco_cum_nat=cum(byc_nat, c, y),
        lnZ=np.log(z), lnZ_own=(np.log(z_own) if (z_own and z_own > 0) else ''),
        lnpc=np.log(pc), lnpop=np.log(P), lnland=np.log(land), abslat=cabslat.get(c, 30.0), n_air=na)
    for k, s in short.items():
        tot = comp_sum[k][(c, y)]
        rec[s+'_sum'] = tot; rec[s+'_mean'] = tot/na if na else 0.0
    recs.append(rec)

order = (['c', 'y', 'reg', 'trade_share', 'ln_tradevol', 'lngdp',
          'lnG', 'ln_gaci_cwm', 'ln_gaci_mean', 'lnCap', 'gaci_cwmean', 'gaci_mean',
          'ln_unesco', 'unesco_cum', 'unesco_cum_nat', 'lnZ', 'lnZ_own',
          'lnpc', 'lnpop', 'lnland', 'abslat', 'n_air',
          'deg_sum', 'deg_mean', 'eig_sum', 'eig_mean', 'close_sum', 'close_mean',
          'betw_sum', 'betw_mean', 'regimp_sum', 'regimp_mean', 'cap_sum', 'cap_mean'])
with open('gaci_panel.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=order); w.writeheader()
    for r in recs: w.writerow({k: r.get(k, '') for k in order})
print('wrote gaci_panel.csv  rows=%d  countries=%d  cols=%d'
      % (len(recs), len(set(r['c'] for r in recs)), len(order)))
