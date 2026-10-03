# -*- coding: utf-8 -*-
"""Reproduce the interaction-IV (g_int / trade openness) for income and baseline-connectivity
   moderators, to (a) validate point estimates vs the Stata log and (b) recover the
   main<->interaction correlation for delta-method quartile CIs."""
import numpy as np, pandas as pd

p = pd.read_csv('gaci_panel_hetero.csv')
for col in p.columns:
    if col not in ('c', 'reg'):
        p[col] = pd.to_numeric(p[col], errors='coerce')

p['g_int'] = p['merch_intensity']
p['g_vol'] = p['merch_intensity'] + p['lngdp']

# moderators, mean-centered exactly as the do-file (summarize over all obs)
def baseline(df, var):
    b96 = df[df.y == 1996].set_index('c')[var]
    return df['c'].map(b96)

p['base_lnpc'] = baseline(p, 'lnpc')
p['inc_c']  = p['base_lnpc'] - p['base_lnpc'].mean()
p['base_cwm'] = baseline(p, 'ln_gaci_cwm')
p['cwm0_c'] = p['base_cwm'] - p['base_cwm'].mean()
p['rem_c']  = p['ln_remote'] - p['ln_remote'].mean()


def twoway_resid(df, cols):
    """Partial out country FE, year FE, lnpop (FWL) from each column."""
    C = pd.get_dummies(df['c'], drop_first=True).astype(float).values
    Y = pd.get_dummies(df['y'], drop_first=True).astype(float).values
    W = np.column_stack([np.ones(len(df)), df['lnpop'].values, C, Y])
    Q, _ = np.linalg.qr(W)
    out = {}
    for k in cols:
        v = df[k].values.astype(float)
        out[k] = v - Q @ (Q.T @ v)
    return out


def iv2sls(df, modvar):
    df = df.copy()
    df['cwm_m'] = df['ln_gaci_cwm'] * df[modvar]
    df['z_m']   = df['tourism_int'] * df[modvar]
    need = ['g_int', 'lnpop', 'ln_gaci_cwm', 'cwm_m', 'tourism_int', 'z_m', 'c', 'y']
    d = df.dropna(subset=need).copy()
    r = twoway_resid(d, ['g_int', 'ln_gaci_cwm', 'cwm_m', 'tourism_int', 'z_m'])
    y = r['g_int']
    X = np.column_stack([r['ln_gaci_cwm'], r['cwm_m']])
    Z = np.column_stack([r['tourism_int'], r['z_m']])
    n = len(y)
    ZtZ_inv = np.linalg.inv(Z.T @ Z)
    Xhat = Z @ (ZtZ_inv @ (Z.T @ X))
    A = np.linalg.inv(Xhat.T @ X)
    beta = A @ (Xhat.T @ y)
    e = y - X @ beta
    # robust (HC1-style) sandwich
    meat = (Xhat * (e**2)[:, None]).T @ Xhat
    k = 2 + 1 + (d['c'].nunique() - 1) + (d['y'].nunique() - 1)  # params incl. absorbed FE
    V = A @ meat @ A.T * n / (n - k)
    se = np.sqrt(np.diag(V))
    corr = V[0, 1] / (se[0] * se[1])
    return dict(n=n, b_main=beta[0], b_int=beta[1], se_main=se[0], se_int=se[1], corr=corr)


for name, mv in [('income', 'inc_c'), ('baseconn', 'cwm0_c'), ('remote', 'rem_c')]:
    res = iv2sls(p, mv)
    print(f"{name:9s} N={res['n']:5d}  main={res['b_main']:+.4f} ({res['se_main']:.4f})  "
          f"inter={res['b_int']:+.4f} ({res['se_int']:.4f})  corr(main,inter)={res['corr']:+.3f}")
