# -*- coding: utf-8 -*-
"""
compute_covid_3measure.py
COVID-19 connectivity-collapse shock (2019 -> 2020), computed for ALL THREE measures.
Mirror of the aggregate-contribution logic but over a single shock year: a country's
one-year change d = Dln(GACI) scales its 2019 trade by exp(beta*d); the implied loss
(d<0) is  loss_i = trade_i(2019) * (1 - exp(beta*d_i)),  positive = trade lost.

Measures / IV elasticities (same as _measures_contribution): order = cwm, max, sum
    cwm : b_int 1.302, b_gdp 1.001
    max : b_int 0.966, b_gdp 0.743
    sum : b_int 0.659, b_gdp 0.507   (measure the manuscript currently uses for shocks)

in : gaci_panel_measures.csv
out: _covid_3measure.csv  + _covid_bycountry.csv (per-country, for maps)
"""
import numpy as np, pandas as pd

Y0, Y1 = 2019, 2020
MEAS = {  # order matches manuscript Table 1: cwm (headline), max, sum
    'cwm': dict(col='ln_gaci_cwm', b_int=1.208, b_gdp=0.919),
    'max': dict(col='ln_gaci_max', b_int=0.897, b_gdp=0.683),
    'sum': dict(col='lnG',         b_int=0.635, b_gdp=0.483),
}

p = pd.read_csv('gaci_panel_measures.csv')
p['gdp']       = np.exp(p['lngdp'])
p['goods_val'] = p['merch_share'] / 100.0 * p['gdp']
tr19  = p[p.y == Y0].set_index('c')['goods_val']
gdp19 = p[p.y == Y0].set_index('c')['gdp']
TOT_TRADE19 = tr19.dropna().sum()
TOT_GDP19   = gdp19.dropna().sum()

rows, bycountry = [], {}
for name, cfg in MEAS.items():
    d = (p[p.y == Y1].set_index('c')[cfg['col']] - p[p.y == Y0].set_index('c')[cfg['col']]).rename('d')
    m = pd.concat([tr19.rename('tr'), gdp19.rename('gd'), d], axis=1).dropna(subset=['d'])
    tl = m['tr'].fillna(0) * (1 - np.exp(cfg['b_int'] * m['d']))   # >0 = loss (d<0)
    gl = m['gd'].fillna(0) * (1 - np.exp(cfg['b_gdp'] * m['d']))
    losers = m['d'] < 0
    rows.append(dict(
        measure=name, b_int=cfg['b_int'], b_gdp=cfg['b_gdp'],
        med_dln=m['d'].median(), n=int(m.shape[0]), n_fell=int(losers.sum()),
        trade_loss_usd=tl.sum(), trade_loss_pct=100*tl.sum()/TOT_TRADE19,
        gdp_loss_usd=gl.sum(),  gdp_loss_pct=100*gl.sum()/TOT_GDP19,
        # loss restricted to connectivity-losing countries (gross gateway disruption)
        trade_loss_losers=tl[losers].sum(), gdp_loss_losers=gl[losers].sum(),
    ))
    bc = m[['d']].copy(); bc['tloss'] = tl
    bycountry[name] = bc.rename(columns={'d': f'dln_{name}', 'tloss': f'tloss_{name}'})

tab = pd.DataFrame(rows).set_index('measure')
tab.to_csv('_covid_3measure.csv')
bc_all = pd.concat(bycountry.values(), axis=1); bc_all.index.name = 'c'
bc_all.to_csv('_covid_bycountry.csv')

print('='*70)
print(f'COVID-19 shock 2019->2020.  World 2019: trade ${TOT_TRADE19/1e12:.1f}tn  GDP ${TOT_GDP19/1e12:.1f}tn')
print('='*70)
h = f"{'measure':>7} | {'b_int':>6} | {'med dln':>8} {'n_fell/n':>9} | {'TRADE loss $tn':>14} {'%wT':>5} | {'GDP loss $tn':>12} {'%Y':>5}"
print(h); print('-'*len(h))
for m, r in tab.iterrows():
    print(f"{m:>7} | {r.b_int:>6.3f} | {r.med_dln:>8.3f} {int(r.n_fell):>4}/{int(r.n):<4} | "
          f"{r.trade_loss_usd/1e12:>14.2f} {r.trade_loss_pct:>5.1f} | {r.gdp_loss_usd/1e12:>12.2f} {r.gdp_loss_pct:>5.1f}")
print('-'*len(h))
print("Net loss (gains from countries whose connectivity ROSE are netted out).")
print("Loss among only the connectivity-LOSING countries (gross gateway disruption):")
for m, r in tab.iterrows():
    print(f"   {m}: trade ${r.trade_loss_losers/1e12:.2f}tn, GDP ${r.gdp_loss_losers/1e12:.2f}tn")
print('\nwrote _covid_3measure.csv, _covid_bycountry.csv')
