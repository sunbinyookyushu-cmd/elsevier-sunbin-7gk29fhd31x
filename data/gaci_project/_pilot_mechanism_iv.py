# -*- coding: utf-8 -*-
"""
_pilot_mechanism_iv.py -- quick python 2SLS pilot on the mechanism splits,
same spec as gaci_mechanism.do (country+year FE, tourism_int IV, lnpop),
robust (HC1) SEs. Direction check ONLY; Stata run is authoritative.
"""
import numpy as np
import pandas as pd

d = pd.read_csv("gaci_panel_mechanism.csv")

def demean_2way(df, cols, ci="c", yi="y", iters=25):
    X = df[cols].astype(float).copy()
    for _ in range(iters):
        X = X - X.groupby(df[ci]).transform("mean")
        X = X - X.groupby(df[yi]).transform("mean")
    return X

def iv2sls(df, yv, treat="ln_gaci_cwm", inst="tourism_int", ctrl="lnpop"):
    sub = df[["c", "y", yv, treat, inst, ctrl]].dropna()
    if len(sub) < 500:
        return None
    Z = demean_2way(sub, [yv, treat, inst, ctrl])
    yt, tr, iv, ct = (Z[c].values for c in [yv, treat, inst, ctrl])
    X1 = np.column_stack([iv, ct])                       # first stage
    b1 = np.linalg.lstsq(X1, tr, rcond=None)[0]
    e1 = tr - X1 @ b1
    XtXi = np.linalg.inv(X1.T @ X1)
    V1 = XtXi @ (X1 * (e1**2)[:, None]).T @ X1 @ XtXi    # HC1-ish
    F = (b1[0]**2) / V1[0, 0]
    trhat = X1 @ b1
    X2 = np.column_stack([trhat, ct])                    # second stage
    b2 = np.linalg.lstsq(X2, yt, rcond=None)[0]
    resid = yt - np.column_stack([tr, ct]) @ b2          # structural resid
    X2tX2i = np.linalg.inv(X2.T @ X2)
    V2 = X2tX2i @ (X2 * (resid**2)[:, None]).T @ X2 @ X2tX2i
    se = np.sqrt(V2[0, 0])
    return b2[0], se, F, len(sub)

PANELS = [
    ("A Rauch (volume)", ["ln_tr_total", "ln_tr_diff", "ln_tr_ref", "ln_tr_homog"]),
    ("B V/W (volume)",   ["ln_tr_hivw", "ln_tr_lovw"]),
    ("C BEC (volume)",   ["ln_tr_interm", "ln_tr_consum", "ln_tr_capital"]),
    ("D margins",        ["ln_nprod", "ln_nflow"]),
    ("E Rauch liberal",  ["ln_tr_diff_lib", "ln_tr_ref_lib", "ln_tr_homog_lib"]),
]
print(f"{'outcome':<18}{'beta':>9}{'se':>8}{'t':>7}{'KP~F':>8}{'N':>7}")
for title, cols in PANELS:
    print("-" * 57 + f"  {title}")
    for yv in cols:
        r = iv2sls(d, yv)
        if r is None:
            print(f"{yv:<18}  (insufficient N)"); continue
        b, se, F, n = r
        print(f"{yv:<18}{b:>9.3f}{se:>8.3f}{b/se:>7.2f}{F:>8.1f}{n:>7}")
# intensity versions of the headline splits
print("-" * 57 + "  A' Rauch (intensity, minus lnGDP)")
for yv in ["ln_tr_diff", "ln_tr_ref", "ln_tr_homog"]:
    d[yv + "_int"] = d[yv] - d["lngdp"]
    r = iv2sls(d, yv + "_int")
    if r:
        b, se, F, n = r
        print(f"{yv+'_int':<18}{b:>9.3f}{se:>8.3f}{b/se:>7.2f}{F:>8.1f}{n:>7}")
