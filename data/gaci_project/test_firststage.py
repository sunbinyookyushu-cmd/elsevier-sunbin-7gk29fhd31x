# -*- coding: utf-8 -*-
"""First-stage strength test: regress connectivity (cwm and sum) on the
tourism-heritage instrument with two-way (country+year) FE, across samples.
First-stage F on the excluded instrument = (coef/cluster-SE)^2 (one instrument).
"""
import pandas as pd, numpy as np
import statsmodels.api as sm

df = pd.read_csv('gaci_panel_3iv.csv')
for c in ['y', 'ln_gaci_cwm', 'lnG', 'tourism_int', 'lnpop']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df = df.dropna(subset=['ln_gaci_cwm', 'lnG', 'tourism_int', 'lnpop']).copy()

def demean2(d, cols, ent='c', tim='y', it=30):
    d = d.copy()
    for c in cols:
        d[c] = d[c].astype(float)
    for _ in range(it):
        for g in (ent, tim):
            d[cols] = d[cols] - d.groupby(g)[cols].transform('mean')
    return d

def fstage(d, treat, sample_label):
    cols = [treat, 'tourism_int', 'lnpop']
    dd = demean2(d, cols)
    X = sm.add_constant(dd[['tourism_int', 'lnpop']])
    y = dd[treat]
    mr = sm.OLS(y, X).fit(cov_type='HC1')                         # robust
    mc = sm.OLS(y, X).fit(cov_type='cluster',
                          cov_kwds={'groups': d['c'].values})     # cluster by country
    Fr = (mr.params['tourism_int'] / mr.bse['tourism_int']) ** 2
    Fc = (mc.params['tourism_int'] / mc.bse['tourism_int']) ** 2
    print('  %-22s | n=%4d | b=%7.3f | F robust=%6.2f | F cluster=%6.2f' %
          (sample_label, len(d), mr.params['tourism_int'], Fr, Fc))
    return Fr, Fc

for treat, name in [('ln_gaci_cwm', 'HUB QUALITY (cwm)'), ('lnG', 'TOTAL CONNECTIVITY (sum)')]:
    print('#### first stage:', name, '####')
    fstage(df, treat, 'full 1996-2023')
    fstage(df[df.y <= 2019], treat, 'pre-COVID 1996-2019')
    fstage(df[~df.y.isin([2020, 2021])], treat, 'excl. 2020-21')
    fstage(df[df.y >= 2010], treat, 'post-2010 2010-2023')
    print()
