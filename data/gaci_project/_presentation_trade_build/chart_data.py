# -*- coding: utf-8 -*-
"""Chart data for the GACI trade conference deck (2024 manuscript version).
All inputs come from GACI/ext2024 (the data behind TRA_rev20260902_ext2024/main.tex).
Writes chart_data.json next to this script; every number is printed for checking."""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, '..', 'ext2024')
out = {}

# ---------------------------------------------------------------- airport level
ap = pd.read_csv(os.path.join(EXT, 'GACI1996_2024_new_panel_data.csv'), encoding='utf-8-sig')
IND = ['Degree', 'NorBetweenness', 'NorClose', 'Eigen', 'RegionalImportance']
LAB = ['Degree', 'Flow betweenness', 'Closeness', 'Eigenvector', 'Regional importance']

n_by_year = ap.groupby('Year')['Airport'].nunique()
out['airports_per_year'] = {int(k): int(v) for k, v in n_by_year.items()}
print('airports per year: min %d max %d' % (n_by_year.min(), n_by_year.max()))

# year-by-year PCA, same recipe as ext2024/build_method_fig_v2.py (z-score within year)
load_rows, ve = [], {}
for y, g in ap.groupby('Year'):
    X = g[IND].to_numpy(float)
    Z = (X - X.mean(0)) / X.std(0)
    C = np.cov(Z, rowvar=False)
    w, v = np.linalg.eigh(C)
    pc1 = v[:, -1]
    if pc1.sum() < 0:
        pc1 = -pc1
    load_rows.append([int(y)] + list(pc1))
    ve[int(y)] = float(w[-1] / w.sum())
L = pd.DataFrame(load_rows, columns=['Year'] + LAB).set_index('Year')
out['pca_loadings'] = {lab: [round(float(x), 4) for x in L[lab]] for lab in LAB}
out['pca_years'] = [int(y) for y in L.index]
out['pca_ve'] = [round(ve[y], 4) for y in L.index]
print('mean loadings', L.mean().round(3).to_dict())
print('sd loadings', L.std().round(3).to_dict())
print('VE range %.3f-%.3f' % (min(ve.values()), max(ve.values())))

# rank correlations among the five indicators, 2024
g24 = ap[ap.Year == 2024]
rc = g24[IND].rank().corr()
rc.index = LAB; rc.columns = LAB
out['rankcorr_2024'] = rc.round(2).values.tolist()
off = rc.values[np.triu_indices(5, 1)]
print('2024 rank corr range %.2f-%.2f' % (off.min(), off.max()))

# seat concentration: share of airports that carry half of all seats
for y in (1996, 2024):
    s = ap[ap.Year == y]['TotalCapacity'].sort_values(ascending=False).to_numpy()
    k = int(np.searchsorted(np.cumsum(s) / s.sum(), 0.5) + 1)
    out[f'half_seats_{y}'] = dict(n_airports=k, n_total=int(len(s)), share=round(k / len(s), 4))
    print(y, 'airports carrying half of seats:', k, 'of', len(s), '= %.1f%%' % (100 * k / len(s)))

# face validity: GACI vs seat capacity, 2024 (top airports labelled)
fv = g24[['Airport', 'GACI', 'TotalCapacity']].dropna()
out['gaci_capacity_corr_2024'] = round(float(np.corrcoef(fv.GACI, np.log(fv.TotalCapacity))[0, 1]), 3)
out['top15_2024'] = fv.sort_values('GACI', ascending=False).head(15)[['Airport', 'GACI']].round(3).values.tolist()
print('top15 2024', out['top15_2024'][:8])

# ---------------------------------------------------------------- country panel
p = pd.read_csv(os.path.join(EXT, 'gaci_panel_hetero.csv'))
for col in p.columns:
    if col not in ('c', 'reg'):
        p[col] = pd.to_numeric(p[col], errors='coerce')
d = p.dropna(subset=['merch_intensity', 'ln_gaci_cwm', 'tourism_int', 'lnpop']).copy()
# drop singletons (Stata drops them)
d = d[d.groupby('c')['y'].transform('size') > 1].copy()
print('first-stage N =', len(d))


def twoway_demean(df, cols, tol=1e-10, maxit=5000):
    r = df[cols].astype(float).copy()
    for _ in range(maxit):
        old = r.copy()
        r = r - r.groupby(df['c']).transform('mean')
        r = r - r.groupby(df['y']).transform('mean')
        if (r - old).abs().to_numpy().max() < tol:
            break
    return r


R = twoway_demean(d, ['ln_gaci_cwm', 'tourism_int', 'lnpop'])
P = R['lnpop'].to_numpy()


def resid_on_pop(v):
    b = (P @ v) / (P @ P)
    return v - b * P


xr = resid_on_pop(R['ln_gaci_cwm'].to_numpy())
zr = resid_on_pop(R['tourism_int'].to_numpy())
slope = float((zr @ xr) / (zr @ zr))
print('first-stage slope (FWL) = %.4f' % slope)
bins = pd.qcut(zr, 20, labels=False, duplicates='drop')
bs = pd.DataFrame({'z': zr, 'x': xr, 'b': bins}).groupby('b').mean()
out['firststage'] = dict(slope=round(slope, 4), n=int(len(d)),
                         bx=[round(float(v), 5) for v in bs.z],
                         by=[round(float(v), 5) for v in bs.x],
                         zmin=round(float(np.percentile(zr, 2)), 4), zmax=round(float(np.percentile(zr, 98)), 4))

# global tourism shift (min-max scaled world arrivals), from the panel
ts = p.groupby('y')['tour_shift'].first().dropna()
out['tour_shift'] = {int(k): round(float(v), 4) for k, v in ts.items()}
print('tour_shift', {k: round(v, 2) for k, v in out['tour_shift'].items() if k in (1996, 2010, 2019, 2020, 2024)})

# heterogeneity by quartile (same recipe as ext2024/build_hetero_quartile_fig.py)
EST = {
    'income':   dict(b_main=1.138607, se_main=0.643988, b_int=-0.214013, se_int=0.108323, corr=-0.858),
    'baseconn': dict(b_main=2.014492, se_main=0.986082, b_int=-1.334897, se_int=0.523936, corr=-0.781),
}
h = p.copy()
h['g_int'] = h['merch_intensity']
for var, new in (('lnpc', 'base_lnpc'), ('ln_gaci_cwm', 'base_cwm')):
    b96 = h[h.y == 1996].set_index('c')[var]
    h[new] = h['c'].map(b96)
h['inc_c'] = h['base_lnpc'] - h['base_lnpc'].mean()
h['cwm0_c'] = h['base_cwm'] - h['base_cwm'].mean()


def sample_vals(mod):
    q = h.copy()
    q['cwm_m'] = q['ln_gaci_cwm'] * q[mod]
    q['z_m'] = q['tourism_int'] * q[mod]
    q = q.dropna(subset=['g_int', 'lnpop', 'ln_gaci_cwm', 'cwm_m', 'tourism_int', 'z_m'])
    return q.groupby('c')[mod].first().dropna()


het = {}
for mod, key in (('inc_c', 'income'), ('cwm0_c', 'baseconn')):
    vals = sample_vals(mod)
    qq = pd.qcut(vals, 4, labels=[1, 2, 3, 4])
    mq = vals.groupby(qq, observed=True).mean()
    e = EST[key]
    rows = []
    for k in (1, 2, 3, 4):
        m = mq[k]
        b = e['b_main'] + e['b_int'] * m
        var = e['se_main']**2 + m**2 * e['se_int']**2 + 2 * m * e['corr'] * e['se_main'] * e['se_int']
        rows.append([round(float(b), 3), round(float(1.96 * np.sqrt(var)), 3)])
    het[key] = rows
    print(key, rows)
out['het_quartile'] = het

# ---------------------------------------------------------------- aggregates
ct = pd.read_csv(os.path.join(EXT, 'GACI_continent_trend.csv'))
out['continent'] = {c: ct[ct.continent == c].sort_values('y')[['y', 'eff']].round(3).values.tolist()
                    for c in ct.continent.unique()}
print('continent 2024', {c: v[-1] for c, v in out['continent'].items()})

cb = pd.read_csv(os.path.join(EXT, '_contrib_bycountry.csv'))
print('world gain_cwm = %.2f tn' % (cb.gain_cwm.sum() / 1e12), ' negatives:', int((cb.gain_cwm < 0).sum()), 'of', len(cb))
top = cb.sort_values('gain_cwm', ascending=False).head(10)
out['contrib_top10'] = [[r.c, round(r.gain_cwm / 1e9, 1)] for r in top.itertuples()]
print('top10', out['contrib_top10'])

rb = json.load(open(os.path.join(EXT, '_rank_bump_data.json'), encoding='utf-8'))
out['rank_bump'] = rb

json.dump(out, open(os.path.join(HERE, 'chart_data.json'), 'w'), indent=1)
print('wrote chart_data.json')

# ---------------------------------------------------------------- motivation: world seats vs world goods trade
seats = ap.groupby('Year')['TotalCapacity'].sum()
tv = p.dropna(subset=['ln_tradevol']).copy()
full = tv.groupby('c')['y'].nunique()
bal = full[full == 29].index
tb = tv[tv.c.isin(bal)].groupby('y')['ln_tradevol'].apply(lambda s: np.exp(s).sum())
out['motiv'] = dict(years=[int(y) for y in seats.index],
                    seats_idx=[round(float(100 * v / seats.iloc[0]), 1) for v in seats],
                    trade_idx=[round(float(100 * tb.loc[y] / tb.iloc[0]), 1) for y in seats.index],
                    n_bal=int(len(bal)))
print('motiv: balanced countries', len(bal), 'seats 2024 idx', out['motiv']['seats_idx'][-1], 'trade 2024 idx', out['motiv']['trade_idx'][-1],
      'seats 2020', out['motiv']['seats_idx'][24])
json.dump(out, open(os.path.join(HERE, 'chart_data.json'), 'w'), indent=1)
