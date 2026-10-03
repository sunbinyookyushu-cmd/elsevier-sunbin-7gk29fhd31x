# -*- coding: utf-8 -*-
"""_est.py  OLS / 2SLS with high-dimensional fixed effects, several endogenous regressors,
optional weights, and three kinds of cluster-robust inference.

Fixed effects are partialled out with pyfixest's numba demeaning (alternating projections).
Small-sample factor as in reghdfe / pyfixest (ssc 'nonnested'): G/(G-1) * (N-1)/(N-K), where K
counts the regressors plus the levels of every fixed effect that is not nested in the cluster
variable.

Variance options (argument `vc`):
  ("cl", c)            one-way cluster on c
  ("cl2", c1, c2)      two-way cluster, Cameron-Gelbach-Miller (2011): V1 + V2 - V12, all terms
                       scaled by Gmin/(Gmin-1) as in pyfixest
  ("dk", c, t, L)      cluster on c plus Newey-West (Bartlett, L lags) over the common time index t,
                       minus the c x t intersection (Thompson 2011, J. Financ. Econ.). This is the
                       relevant option here: the regressor is a single aggregate price series times a
                       fixed exposure, so residuals share a common, serially correlated time component.
  For "cl2" and "dk" each variance is floored at the larger one-way component (c alone, or t alone),
  which only binds when the subtraction of the intersection term makes the sum too small.
p-values use t(G - 1) with G = number of clusters (for "cl2"/"dk": min of the two dimensions).
First-stage strength: with one endogenous regressor, Kleibergen-Paap Wald F under the same vc
(= squared robust t of the excluded instrument when there is one instrument); with several,
Sanderson-Windmeijer F per endogenous regressor.
Checked against pyfixest in 10_validate_est.py.
"""
import numpy as np
import pandas as pd
from scipy import stats
from pyfixest.estimation import demean as _pf_demean


def _codes(df, fes):
    return np.column_stack([pd.factorize(df[f])[0] for f in fes]).astype(np.uint64)


def _nested(df, fe, cl):
    return df.groupby(fe, observed=True)[cl].nunique().max() == 1


def _sums(Xs, g):
    return pd.DataFrame(Xs).groupby(g, sort=True).sum()


def _meat(Xs, g):
    S = _sums(Xs, g).to_numpy()
    return S.T @ S


def _psd(V):
    w, Q = np.linalg.eigh((V + V.T) / 2)
    return Q @ np.diag(np.clip(w, 0, None)) @ Q.T if (w < 0).any() else V


def _floor(V, parts):
    """conservative floor: each variance at least as large as the largest one-way component
    (guards against the negative / near-zero sums that the subtraction can produce with few periods)"""
    d = np.diag(V).copy()
    m = np.max(np.column_stack([np.diag(P) for P in parts]), axis=1)
    if (d < m).any():
        s_new = np.sqrt(np.maximum(d, m))
        s_old = np.sqrt(np.where(d > 0, d, 1.0))
        R = V / np.outer(s_old, s_old)
        R[np.ix_(d <= 0, d <= 0)] = 0
        np.fill_diagonal(R, 1.0)
        V = R * np.outer(s_new, s_new)
    return V


def _vcov(Xh, u, bread, vc, D, n, k):
    """D: DataFrame holding the cluster / time columns (aligned with rows). returns V, G"""
    Xs = Xh * u[:, None]
    adj = (n - 1) / (n - k)
    kind = vc[0]
    if kind == "cl":
        g = D[vc[1]].to_numpy()
        G = pd.Series(g).nunique()
        return bread @ _meat(Xs, g) @ bread * G / (G - 1) * adj, G
    if kind == "cl2":
        g1, g2 = D[vc[1]].to_numpy(), D[vc[2]].to_numpy()
        g12 = pd.Series(g1).astype(str).to_numpy() + "|" + pd.Series(g2).astype(str).to_numpy()
        G = min(pd.Series(g1).nunique(), pd.Series(g2).nunique())
        M1, M2 = _meat(Xs, g1), _meat(Xs, g2)
        V = _psd(bread @ (M1 + M2 - _meat(Xs, g12)) @ bread * G / (G - 1) * adj)
        return _floor(V, [bread @ M1 @ bread * G / (G - 1) * adj, bread @ M2 @ bread * G / (G - 1) * adj]), G
    if kind == "dk":
        g, t, L = D[vc[1]].to_numpy(), D[vc[2]].to_numpy(), vc[3]
        gt = pd.Series(g).astype(str).to_numpy() + "|" + pd.Series(t).astype(str).to_numpy()
        St = _sums(Xs, t)
        tt = St.index.to_numpy()
        S = St.to_numpy()
        pos = {v: i for i, v in enumerate(tt)}
        Om = S.T @ S
        for l in range(1, L + 1):
            wgt = 1 - l / (L + 1)
            idx = [(pos[v], pos[v - l]) for v in tt if (v - l) in pos]
            if not idx:
                continue
            a, b = np.array(idx).T
            C = S[a].T @ S[b]
            Om += wgt * (C + C.T)
        Gc, Gt = pd.Series(g).nunique(), len(tt)
        G = min(Gc, Gt)
        Mc = _meat(Xs, g)
        V = _psd(bread @ (Mc + Om - _meat(Xs, gt)) @ bread * G / (G - 1) * adj)
        return _floor(V, [bread @ Mc @ bread * G / (G - 1) * adj, bread @ Om @ bread * G / (G - 1) * adj]), G
    raise ValueError(kind)


def fit(df, y, exog=(), endog=(), instr=(), fes=(), vc=("cl", "iso3"), weights=None, return_fs=True,
        vc_alt=(), partial=()):
    """vc: primary variance option; vc_alt: further options, reported in out['alt'][i] (se, p, G, F).
    partial: exogenous controls partialled out (Frisch-Waugh) after the fixed effects; not reported,
    counted in K. Keeps the variance matrix small when there are many controls."""
    exog, endog, instr, partial = list(exog), list(endog), list(instr), list(partial)
    cols = [y] + endog + instr + exog + partial
    vcols = [v for opt in [vc] + list(vc_alt) for v in opt[1:] if isinstance(v, str)]
    need = list(dict.fromkeys(cols + list(fes) + vcols + ([weights] if weights else [])))
    d = df.loc[df[need].notna().all(axis=1), need]
    if weights:
        d = d[d[weights] > 0]
    n = len(d)
    w = d[weights].to_numpy(float) if weights else np.ones(n)
    A = d[cols].to_numpy(float)
    if fes:
        A, ok = _pf_demean(A, _codes(d, fes), w)
        if not ok:
            raise RuntimeError("demeaning did not converge")
    else:
        A = A - np.average(A, axis=0, weights=w)
    sw = np.sqrt(w)
    A = A * sw[:, None]
    if partial:
        P = A[:, len(cols) - len(partial):]
        A = A[:, :len(cols) - len(partial)]
        Pq, _ = np.linalg.qr(P)
        A = A - Pq @ (Pq.T @ A)
    yv = A[:, 0]
    Xe = A[:, 1:1 + len(endog)]
    Zx = A[:, 1 + len(endog):1 + len(endog) + len(instr)]
    W = A[:, 1 + len(endog) + len(instr):]
    X = np.column_stack([Xe, W])
    names = endog + exog
    k_fe = sum(d[f].nunique() for f in fes if not _nested(d, f, vc[1])) - (1 if fes else 0)
    k = X.shape[1] + len(partial) + max(k_fe, 0) + (0 if fes else 1)
    if endog:
        Z = np.column_stack([Zx, W])
        Xh = Z @ np.linalg.lstsq(Z, X, rcond=None)[0]
    else:
        Xh = X
    XtX = Xh.T @ X
    if np.linalg.cond(XtX) > 1e12:
        import warnings
        warnings.warn("near-collinear regressors in fit(%s): condition number %.2e" % (y, np.linalg.cond(XtX)))
    beta = np.linalg.solve(XtX, Xh.T @ yv)
    u = yv - X @ beta
    V, G = _vcov(Xh, u, np.linalg.inv(Xh.T @ Xh), vc, d, n, k)
    se = np.sqrt(np.diag(V))
    with np.errstate(divide="ignore", invalid="ignore"):
        p = 2 * (1 - stats.t.cdf(np.abs(beta / se), G - 1))
    r2w = 1 - (u @ u) / (yv @ yv) if not endog else np.nan
    out = dict(coef=dict(zip(names, beta)), se=dict(zip(names, se)), p=dict(zip(names, p)),
               n=n, G=G, r2_within=r2w, ymean=float(np.average(d[y], weights=w)), fs={})
    if endog and return_fs:
        if W.shape[1]:
            Wq, _ = np.linalg.qr(W)
            Mw = lambda B: B - Wq @ (Wq.T @ B)
            Zp, Xp = Mw(Zx), Mw(Xe)
        else:
            Zp, Xp = Zx, Xe
        L, K1 = Zp.shape[1], Xp.shape[1]
        for j in range(K1):
            xj = Xp[:, j]
            if K1 > 1:
                Xo = np.delete(Xp, j, axis=1)
                Po = Zp @ np.linalg.lstsq(Zp, Xo, rcond=None)[0]
                e = xj - Xo @ np.linalg.solve(Po.T @ Xo, Po.T @ xj)
            else:
                e = xj
            pi = np.linalg.lstsq(Zp, e, rcond=None)[0]
            r = e - Zp @ pi
            Vp, _ = _vcov(Zp, r, np.linalg.inv(Zp.T @ Zp), vc, d, n, L + W.shape[1] + max(k_fe, 0))
            wald = float(pi @ np.linalg.pinv(Vp) @ pi)
            out["fs"][endog[j]] = dict(F=wald / (L - K1 + 1), pi=dict(zip(instr, pi)),
                                       pi_se=dict(zip(instr, np.sqrt(np.diag(Vp)))))
    out["alt"] = []
    for opt in vc_alt:
        k2 = X.shape[1] + max(sum(d[f].nunique() for f in fes if not _nested(d, f, opt[1])) - (1 if fes else 0), 0) + (0 if fes else 1)
        V2, G2 = _vcov(Xh, u, np.linalg.inv(Xh.T @ Xh), opt, d, n, k2)
        se2 = np.sqrt(np.diag(V2))
        with np.errstate(divide="ignore", invalid="ignore"):
            p2 = 2 * (1 - stats.t.cdf(np.abs(beta / se2), G2 - 1))
        a = dict(vc=opt, se=dict(zip(names, se2)), p=dict(zip(names, p2)), G=G2, F={})
        if endog and return_fs and len(endog) == 1:
            e = Xp[:, 0]
            pi = np.linalg.lstsq(Zp, e, rcond=None)[0]
            r = e - Zp @ pi
            Vp, _ = _vcov(Zp, r, np.linalg.inv(Zp.T @ Zp), opt, d, n, L + W.shape[1])
            a["F"][endog[0]] = float(pi @ np.linalg.pinv(Vp) @ pi) / L
        out["alt"].append(a)
    return out


def stars(p):
    if p is None or not np.isfinite(p):
        return ""
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
