# -*- coding: utf-8 -*-
"""Sweep the temporal split year: for each candidate split, report
(a) pre-period and post-period subsample first-stage F (robust, HC1) on tourism_int,
(b) the interaction-2SLS coefficients (level, x post) for Volume, matching
    test_temporal_sum.py's spec (cwm treat).
Goal: diagnose whether the weak pre-period first stage is specific to the 2010
split or structural.
"""
import pandas as pd, numpy as np
import statsmodels.api as sm
from scipy import stats

CSV = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\ext2024\gaci_panel_3iv.csv"
df = pd.read_csv(CSV)
for c in ['y','ln_gaci_cwm','lnG','merch_intensity','lngdp','tourism_int','lnpop']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['g_vol'] = df['merch_intensity'] + df['lngdp']
df['g_gdp'] = df['lngdp']
df['g_int'] = df['merch_intensity']

def demean2(d, cols, it=40):
    d = d.copy()
    for _ in range(it):
        for g in ('c','y'):
            d[cols] = d[cols] - d.groupby(g)[cols].transform('mean')
    return d

def sub_F(d, treat='ln_gaci_cwm'):
    d = d.dropna(subset=[treat,'tourism_int','lnpop']).copy()
    if d['y'].nunique() < 2 or len(d) < 50:
        return np.nan, len(d)
    dd = demean2(d, [treat,'tourism_int','lnpop'], it=30)
    X = sm.add_constant(dd[['tourism_int','lnpop']])
    m = sm.OLS(dd[treat], X).fit(cov_type='HC1')
    F = (m.params['tourism_int']/m.bse['tourism_int'])**2
    return F, len(d)

def tsls_itx(d, split, treat='ln_gaci_cwm', outcome='g_vol'):
    d = d.dropna(subset=[treat,'tourism_int','lnpop',outcome]).copy()
    d['post'] = (d['y'] >= split).astype(float)
    d['tr_post'] = d[treat]*d['post']
    d['z_post'] = d['tourism_int']*d['post']
    cols = [outcome, treat, 'tr_post', 'lnpop', 'tourism_int', 'z_post']
    dd = demean2(d, cols)
    Y = dd[[outcome]].values
    X = dd[[treat,'tr_post','lnpop']].values
    Z = dd[['tourism_int','z_post','lnpop']].values
    Pz = Z @ np.linalg.inv(Z.T@Z) @ Z.T
    XPzX_inv = np.linalg.inv(X.T@Pz@X)
    beta = XPzX_inv @ (X.T@Pz@Y)
    u = (Y - X@beta).ravel()
    Xhat = Pz@X
    n,k = X.shape
    dof = n - k - (d['c'].nunique()-1) - (d['y'].nunique()-1)
    V = XPzX_inv @ (Xhat.T @ np.diag(u**2) @ Xhat) @ XPzX_inv * (n/dof)
    se = np.sqrt(np.diag(V))
    out = []
    for i in range(2):
        b = beta[i,0]; s = se[i]; p = 2*stats.t.sf(abs(b/s), dof)
        out.append((b,s,p))
    return out

def st(p): return '***' if p<.01 else '**' if p<.05 else '*' if p<.10 else '   '

print('split | pre-F (n)        | post-F (n)       | Volume level      | Volume x post')
for split in range(2002, 2018):
    d = df.dropna(subset=['ln_gaci_cwm','tourism_int','lnpop']).copy()
    Fp, npre = sub_F(d[d.y < split])
    Fo, npost = sub_F(d[d.y >= split])
    (bl,sl,pl),(bx,sx,px) = tsls_itx(df, split)
    print('%d  | F=%6.2f (%5d) | F=%6.2f (%5d) | %7.3f%s (%.3f) | %7.3f%s (%.3f)'
          % (split, Fp, npre, Fo, npost, bl, st(pl), sl, bx, st(px), sx))
