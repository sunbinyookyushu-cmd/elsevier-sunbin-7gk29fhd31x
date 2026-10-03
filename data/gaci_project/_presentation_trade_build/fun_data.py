# -*- coding: utf-8 -*-
"""Data for the added 'why aviation' and ranking slides (2026-09-29 pass 3).
Inputs: ext2024 airport panel (GACI1996_2024_new_panel_data.csv) and the country panel
used by the manuscript (gaci_panel_hetero.csv, ln_gaci_cwm).  Writes fun_data.json and
prints every number used on a slide."""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, '..', 'ext2024')
out = {}

ap = pd.read_csv(os.path.join(EXT, 'GACI1996_2024_new_panel_data.csv'), encoding='utf-8-sig')
oa = pd.read_csv(os.path.join(EXT, 'ourairports.csv'),
                 usecols=['iata_code', 'iso_country', 'type', 'municipality', 'name'],
                 keep_default_na=False, na_values=[''])
oa = oa[oa['iata_code'].notna() & (oa['iata_code'] != '')]
pref = {'large_airport': 0, 'medium_airport': 1, 'small_airport': 2}
oa = oa.assign(p=oa['type'].map(pref).fillna(3)).sort_values('p').drop_duplicates('iata_code')
CITY = dict(zip(oa['iata_code'], oa['municipality']))
ISO2 = dict(zip(oa['iata_code'], oa['iso_country']))

YEARS = sorted(ap.Year.unique())
ap['rank'] = ap.groupby('Year')['GACI'].rank(ascending=False, method='first').astype(int)
R = ap.pivot(index='Airport', columns='Year', values='rank')

# ---------------------------------------------------------------- 1. number one, year by year
no1 = ap[ap['rank'] == 1].sort_values('Year')[['Year', 'Airport', 'GACI']]
out['no1'] = [[int(r.Year), r.Airport, round(float(r.GACI), 3)] for r in no1.itertuples()]
print('#1 by year:', [(y, a) for y, a, _ in out['no1']])
runs = []
for y, a, _ in out['no1']:
    if runs and runs[-1][0] == a and runs[-1][2] == y - 1:
        runs[-1][2] = y
    else:
        runs.append([a, y, y])
out['no1_runs'] = runs
print('runs:', runs)

# ---------------------------------------------------------------- 2. top 10 in 2024 with 1996 rank
top = ap[ap.Year == 2024].nsmallest(10, 'rank')
rows = []
for r in top.itertuples():
    r96 = R.loc[r.Airport, 1996]
    rows.append(dict(ap=r.Airport, city=CITY.get(r.Airport, ''), iso2=ISO2.get(r.Airport, ''),
                     r24=int(r.rank), r96=None if pd.isna(r96) else int(r96), gaci=round(float(r.GACI), 2)))
out['top10_2024'] = rows
for x in rows:
    print('top10', x)
# how many of the 1996 top 20 are still top 20 in 2024
t96 = set(R.index[R[1996] <= 20]); t24 = set(R.index[R[2024] <= 20])
out['top20_kept'] = len(t96 & t24)
print('1996 top-20 still top-20 in 2024:', len(t96 & t24), sorted(t96 & t24))

# ---------------------------------------------------------------- 3. Asian hub race
ASIA = ['ICN', 'HND', 'NRT', 'KIX', 'PVG', 'PEK', 'CAN', 'HKG', 'TPE', 'SIN', 'BKK', 'KUL']
race = {}
for a in ASIA:
    race[a] = [None if pd.isna(R.loc[a, y]) else int(R.loc[a, y]) for y in YEARS] if a in R.index else None
out['asia_years'] = [int(y) for y in YEARS]
out['asia_race'] = race
for a in ASIA:
    s = race[a]
    print('race %s 1996=%s 2005=%s 2019=%s 2020=%s 2024=%s best=%s' % (
        a, s[0], s[9], s[23], s[24], s[28], min(v for v in s if v)))

# ---------------------------------------------------------------- 4. network churn
pres = {y: set(ap.loc[ap.Year == y, 'Airport']) for y in YEARS}
churn = []
for y0, y1 in zip(YEARS[:-1], YEARS[1:]):
    churn.append([int(y1), len(pres[y1] - pres[y0]), len(pres[y0] - pres[y1]), len(pres[y1])])
out['churn'] = churn
ever = set().union(*pres.values())
always = set.intersection(*pres.values())
out['ever'] = len(ever); out['always'] = len(always)
print('churn (year, new, lost, total):', churn)
print('airports ever in network %d, in all 29 years %d' % (len(ever), len(always)))
print('mean new per yr %.0f, mean lost per yr %.0f' % (np.mean([c[1] for c in churn]), np.mean([c[2] for c in churn])))

# rank mobility: share of airports (present both years) whose rank moved by more than 100 places
both = R[[1996, 2024]].dropna()
out['rank_moved_gt100_share'] = round(float(((both[2024] - both[1996]).abs() > 100).mean()), 3)
print('present 1996 & 2024: %d; moved >100 places: %.1f%%' % (len(both), 100 * out['rank_moved_gt100_share']))

# ---------------------------------------------------------------- 5. world seats, the 2020 shock
seats = ap.groupby('Year')['TotalCapacity'].sum()
out['seats_idx'] = [round(float(100 * v / seats.loc[2019]), 1) for v in seats]   # 2019 = 100
out['seats_2020_drop'] = round(float(100 * (seats.loc[2020] / seats.loc[2019] - 1)), 1)
out['seats_2024_vs_2019'] = round(float(100 * (seats.loc[2024] / seats.loc[2019] - 1)), 1)
out['seats_2024_vs_1996'] = round(float(seats.loc[2024] / seats.loc[1996]), 2)
print('seats 2020 vs 2019 %.1f%%, 2024 vs 2019 %.1f%%, 2024/1996 x%.2f' % (
    out['seats_2020_drop'], out['seats_2024_vs_2019'], out['seats_2024_vs_1996']))
print('seats idx (2019=100):', dict(zip(YEARS, out['seats_idx'])))

# ---------------------------------------------------------------- 6. countries: hub quality rank climbers / fallers
p = pd.read_csv(os.path.join(EXT, 'gaci_panel_hetero.csv'))
p['ln_gaci_cwm'] = pd.to_numeric(p['ln_gaci_cwm'], errors='coerce')
cw = p.pivot_table(index='c', columns='y', values='ln_gaci_cwm')
cb = cw[[1996, 2024]].dropna()
rk = cb.rank(ascending=False, method='first').astype(int)
rk['chg'] = rk[1996] - rk[2024]
rk['dln'] = cb[2024] - cb[1996]
out['country_n'] = int(len(rk))
out['climbers'] = [[c, int(r[1996]), int(r[2024]), round(float(r['dln']), 3)] for c, r in rk.sort_values('chg', ascending=False).head(8).iterrows()]
out['fallers'] = [[c, int(r[1996]), int(r[2024]), round(float(r['dln']), 3)] for c, r in rk.sort_values('chg').head(6).iterrows()]
out['dln_country'] = {c: round(float(v), 4) for c, v in rk['dln'].items()}
print('countries in both years:', len(rk))
print('climbers:', out['climbers'])
print('fallers:', out['fallers'])
print('share with higher hub quality in 2024: %.1f%%' % (100 * (rk['dln'] > 0).mean()))
out['share_up'] = round(float((rk['dln'] > 0).mean()), 3)

json.dump(out, open(os.path.join(HERE, 'fun_data.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('wrote fun_data.json')
