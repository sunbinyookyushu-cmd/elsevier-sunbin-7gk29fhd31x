# -*- coding: utf-8 -*-
"""Which unstated choices reproduce Zhang et al. (2027) Table 5? (N 4058, mean .623, sd .084;
<3 crises 2137/.564; >=3 crises 1921/.689; peak of the inverse-U near GACI 1.85)"""
import numpy as np, pandas as pd
import importlib.util, sys
spec = importlib.util.spec_from_file_location("rb", "30_build_resilience.py")
src = open("30_build_resilience.py", encoding="utf-8").read().split("VERS = {")[0]
ns = {}
exec(src, ns)
W, RANK, CRISES, YEARS, theil = ns["W"], ns["RANK"], ns["CRISES"], ns["YEARS"], ns["theil"]
print("airports in GACI panel:", W.shape[0])

def build(END=2024, postnorm="pct", absent_zero=False, H=6, TAU=2.0):
    X = W.copy()
    first = X.notna().idxmax(axis=1)                       # first year observed
    if absent_zero:                                        # after entry, a missing year = no service (GACI 0)
        for y in X.columns:
            X.loc[(X[y].isna()) & (first <= y), y] = 0.0
    D, S, U = {}, {}, {}
    for name, s, e in CRISES:
        pre = X[s - 1] if s - 1 in X.columns else pd.Series(np.nan, index=X.index)
        pre = pre.where(pre > 0)
        mn = X[[y for y in range(s, min(e, END) + 1)]].min(axis=1)
        dec = (pre - mn) / pre
        b = pre.notna() & mn.notna() & (dec >= 0.01)
        D[name] = (1 - dec.clip(lower=0)).where(b)
        post = [y for y in range(e + 1, min(e + H, END) + 1)]
        if post:
            w = np.exp(-(np.array(post) - (e + 1)) / TAU)
            rec = X[post].div(pre, axis=0).clip(upper=1)
            num = (rec.fillna(0) * w).sum(axis=1); den = (rec.notna() * w).sum(axis=1)
            S[name] = (num / den).where((den > 0) & b)
        else:
            S[name] = pd.Series(np.nan, index=X.index)
        k = 5 if e + 5 <= END else (3 if e + 3 <= END else None)
        U[name] = ((X[e + k] - pre) / pre).clip(lower=0).where(pre.notna()) if k else pd.Series(np.nan, index=X.index)
    D, S, U = pd.DataFrame(D), pd.DataFrame(S), pd.DataFrame(U)
    valid = (D.notna() & S.notna()).sum(axis=1)
    slope = pd.Series([theil(YEARS.astype(float), RANK.loc[a].to_numpy(float)) for a in RANK.index], index=RANK.index)
    sn = slope.rank(pct=True)
    ub = U.mean(axis=1)
    pn = ub.rank(pct=True) if postnorm == "pct" else (ub - ub.min()) / (ub.max() - ub.min())
    ad = (0.5 * sn + 0.5 * pn).fillna(sn)
    R = (D.mean(axis=1) + S.mean(axis=1) + ad) / 3
    Rs = R.where(valid >= 3, valid / (valid + 2) * R + 2 / (valid + 2) * 0.5).where(valid > 0)
    return Rs, valid

g24 = W[2024]
nyr = W.notna().sum(axis=1)
for pnorm in ["pct", "minmax"]:
    for az in [False, True]:
        R, v = build(postnorm=pnorm, absent_zero=az)
        ok = R.notna()
        lo, hi = R[ok & (v < 3)], R[ok & (v >= 3)]
        d = pd.DataFrame({"R": R, "g": g24, "n": nyr}).dropna()
        d = d[d.n >= 5]
        c = np.polyfit(d.g, d.R, 2)
        print(f"postnorm={pnorm:6s} absent0={az!s:5s}  N={ok.sum()} mean={R.mean():.3f} sd={R.std():.3f} | "
              f"<3: {len(lo)} {lo.mean():.3f} | >=3: {len(hi)} {hi.mean():.3f} | inverse-U peak GACI={-c[1]/(2*c[0]):.2f} (a2={c[0]:.4f}, N={len(d)})")
