# -*- coding: utf-8 -*-
"""Temporal interaction (B): cwm/sum + treat#post, instrumented by
tourism_int + tourism_int#post. Two-way FE, robust (HC1) 2SLS, manual.
Validate on cwm (should match Stata: volume x post = +0.377***), then report sum.
"""
import pandas as pd, numpy as np

df = pd.read_csv('gaci_panel_3iv.csv')
for c in ['y','ln_gaci_cwm','lnG','merch_intensity','lngdp','tourism_int','lnpop']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['g_int'] = df['merch_intensity']
df['g_vol'] = df['merch_intensity'] + df['lngdp']
df['g_gdp'] = df['lngdp']
df['post']  = (df['y'] >= 2010).astype(float)

def demean2(d, cols, it=40):
    d = d.copy()
    for _ in range(it):
        for g in ('c','y'):
            d[cols] = d[cols] - d.groupby(g)[cols].transform('mean')
    return d

def tsls(d, treat, outcome):
    d = d.dropna(subset=[treat,'lnG','ln_gaci_cwm','tourism_int','lnpop',outcome]).copy()
    d['tr_post'] = d[treat] * d['post']
    d['z_post']  = d['tourism_int'] * d['post']
    cols = [outcome, treat, 'tr_post', 'lnpop', 'tourism_int', 'z_post']
    dd = demean2(d, cols)
    Y = dd[[outcome]].values
    X = dd[[treat, 'tr_post', 'lnpop']].values          # endog, endog, exog
    Z = dd[['tourism_int', 'z_post', 'lnpop']].values    # IV, IV, exog
    n, k = X.shape
    ZtZ_inv = np.linalg.inv(Z.T @ Z)
    Pz = Z @ ZtZ_inv @ Z.T
    XPzX_inv = np.linalg.inv(X.T @ Pz @ X)
    beta = XPzX_inv @ (X.T @ Pz @ Y)
    u = (Y - X @ beta).ravel()
    Xhat = Pz @ X
    n_c = d['c'].nunique(); n_t = d['y'].nunique()
    dof = n - k - (n_c - 1) - (n_t - 1)
    scale = n / dof
    meat = Xhat.T @ np.diag(u**2) @ Xhat
    V = XPzX_inv @ meat @ XPzX_inv * scale
    se = np.sqrt(np.diag(V))
    from scipy import stats
    names = [treat, treat+'#post', 'lnpop']
    res = {}
    for i,nm in enumerate(names[:2]):
        b = beta[i,0]; s = se[i]; t = b/s
        p = 2*stats.t.sf(abs(t), dof)
        res[nm] = (b, s, p)
    return res

def stars(p): return '***' if p<.01 else '**' if p<.05 else '*' if p<.10 else ''

for treat,label in [('ln_gaci_cwm','cwm (validate)'),('lnG','sum')]:
    print('####', label, '####')
    for o,olbl in [('g_int','Openness'),('g_vol','Volume'),('g_gdp','GDP')]:
        r = tsls(df, treat, o)
        lvl = r[treat]; itx = r[treat+'#post']
        print('  %-9s | %-12s level: %7.3f%-3s (%.3f) | x post: %7.3f%-3s (%.3f)'
              % (olbl, treat, lvl[0], stars(lvl[2]), lvl[1], itx[0], stars(itx[2]), itx[1]))
    print()
