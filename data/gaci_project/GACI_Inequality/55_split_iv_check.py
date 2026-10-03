# -*- coding: utf-8 -*-
"""55_split_iv_check.py : weak-IV check for the split by baseline airport-GACI concentration (54_airport_gini.py).
   For each half (below / above the 1996 median of the airport-GACI Gini) and outcome:
     - 2SLS with Feyrer only, tourism-heritage only (trade paper IV), and both (KP F, Hansen J)
     - reduced form: outcome on each instrument
     - Anderson-Rubin 90/95% confidence set for the Feyrer-only 2SLS (grid inversion, cluster-robust)
   Output: _split_iv_check.csv"""
import os, numpy as np, pandas as pd, pyfixest as pf
from scipy import stats
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gini_disp", "ln_gaci_max", "lnpop", "feyrer_int", "tourism_int"])
e = pd.read_csv("ineq_panel_ext.csv", usecols=["c", "y", "ln_spt_b50"]); g = pd.read_csv("_airport_gini.csv")
p = p.merge(e, on=["c", "y"], how="left").merge(g[["c", "y", "ap_gini"]], on=["c", "y"], how="left")
base = p.sort_values("y").groupby("c").first()[["ap_gini"]].rename(columns={"ap_gini": "ap_gini0"}); p = p.merge(base, on="c", how="left")
med = p.groupby("c").ap_gini0.first().median(); p["half"] = np.where(p.ap_gini0 <= med, "dispersed (below median)", "concentrated (above median)")
p["tourism_int"] = p.tourism_int / p.tourism_int.std()   # rescale for readability
def kpf(fs, zs):
    if len(zs) == 1: return (fs.coef()[zs[0]] / fs.se()[zs[0]]) ** 2
    return float(fs.wald_test(R=None, q=None) if False else np.nan)
def ar_set(d, o, grid):
    """Anderson-Rubin: for each beta0, regress y - beta0*x on Z (with controls, FE); keep beta0 where Z is insignificant."""
    keep90, keep95 = [], []
    for b0 in grid:
        d["_yy"] = d[o] - b0 * d.ln_gaci_max
        f = pf.feols("_yy ~ feyrer_int + lnpop | c + y", d, vcov={"CRV1": "c"}); pv = f.pvalue()["feyrer_int"]
        if pv > 0.10: keep90.append(b0)
        if pv > 0.05: keep95.append(b0)
    fmt = lambda k: ("[%.2f, %.2f]" % (min(k), max(k)) + (" (open)" if (min(k) <= grid[0] or max(k) >= grid[-1]) else "")) if k else "empty"
    return fmt(keep90), fmt(keep95)
rows = []
for o, olab in [("ln_gini_mkt", "ln market Gini"), ("ln_gini_disp", "ln disp. Gini"), ("ln_spt_b50", "Bottom-50 share")]:
    for h in ["concentrated (above median)", "dispersed (below median)"]:
        d = p[(p.half == h)].dropna(subset=[o, "ln_gaci_max", "lnpop", "feyrer_int", "tourism_int"]).copy()
        r = dict(outcome=olab, half=h, n_c=d.c.nunique(), N=len(d))
        for tag, zs in [("feyrer", ["feyrer_int"]), ("tourism", ["tourism_int"]), ("both", ["feyrer_int", "tourism_int"])]:
            f = pf.feols(f"{o} ~ lnpop | c + y | ln_gaci_max ~ " + " + ".join(zs), d, vcov={"CRV1": "c"})
            fs = pf.feols("ln_gaci_max ~ " + " + ".join(zs) + " + lnpop | c + y", d, vcov={"CRV1": "c"})
            if len(zs) == 1: F = (fs.coef()[zs[0]] / fs.se()[zs[0]]) ** 2
            else:
                b = fs.coef()[zs].values; V = fs._vcov[[list(fs.coef().index).index(z) for z in zs]][:, [list(fs.coef().index).index(z) for z in zs]]; F = float(b @ np.linalg.solve(V, b) / len(zs))
            r[f"{tag}_b"] = f.coef()["ln_gaci_max"]; r[f"{tag}_se"] = f.se()["ln_gaci_max"]; r[f"{tag}_p"] = f.pvalue()["ln_gaci_max"]; r[f"{tag}_F"] = F
            if len(zs) == 2:
                # Hansen J via 2SLS residual regression on instruments (homoskedastic approx.)
                d["_u"] = d[o].values - f.coef()["ln_gaci_max"] * d.ln_gaci_max.values
                fj = pf.feols("_u ~ feyrer_int + tourism_int + lnpop | c + y", d); r["J_p"] = float(1 - stats.chi2.cdf(fj._N * fj._r2_within, 1))
        for z in ["feyrer_int", "tourism_int"]:
            frf = pf.feols(f"{o} ~ {z} + lnpop | c + y", d, vcov={"CRV1": "c"}); r[f"rf_{z[:4]}_b"] = frf.coef()[z]; r[f"rf_{z[:4]}_p"] = frf.pvalue()[z]
        r["AR90"], r["AR95"] = ar_set(d, o, np.round(np.arange(-3, 4.01, 0.05), 2))
        rows.append(r)
res = pd.DataFrame(rows); res.to_csv("_split_iv_check.csv", index=False)
pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
cols = ["outcome", "half", "n_c", "feyrer_b", "feyrer_se", "feyrer_p", "feyrer_F", "tourism_b", "tourism_se", "tourism_p", "tourism_F", "both_b", "both_se", "both_p", "both_F", "J_p", "rf_feyr_b", "rf_feyr_p", "rf_tour_b", "rf_tour_p", "AR90", "AR95"]
print(res[cols].round(3).to_string(index=False))
