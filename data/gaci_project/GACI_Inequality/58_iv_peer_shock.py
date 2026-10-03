# -*- coding: utf-8 -*-
"""58_iv_peer_shock.py : Autor-Dorn-Hanson-type 'same shock, other recipients' instrument for own ln GACI_max (user, 2026-09-28).
   Peer groups are defined on the 1996 starting position, not on geography:
     P1  leave-out mean of ln GACI_max over countries in the same 1996 GACI_max decile
     P2  same, 1996 tercile
     P3  same 1996 decile AND a different continent (removes regional common shocks)
     P4  same 1996 decile, different continent, weighted by similarity in 1996 ln GACI_max (kernel in the baseline gap)
   For each: first stage KP F and 2SLS on ln market Gini, ln disp. Gini, bottom-50 share; full sample and the
   baseline airport-concentration split. Country + year FE, ln pop, cluster country. Output: _iv_peer_shock_results.csv"""
import os, numpy as np, pandas as pd, pyfixest as pf
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gini_disp", "ln_gaci_max", "lnpop", "feyrer_int", "reg"])
e = pd.read_csv("ineq_panel_ext.csv", usecols=["c", "y", "ln_spt_b50"]); g = pd.read_csv("_airport_gini.csv")
p = p.merge(e, on=["c", "y"], how="left").merge(g[["c", "y", "ap_gini"]], on=["c", "y"], how="left")
p["cont"] = p.reg.astype(str).str[:2]
base = p.sort_values("y").groupby("c").first()[["ln_gaci_max", "ap_gini", "cont"]].rename(columns={"ln_gaci_max": "g0", "ap_gini": "ap_gini0", "cont": "cont0"})
base["dec"] = pd.qcut(base.g0, 10, labels=False); base["ter"] = pd.qcut(base.g0, 3, labels=False)
p = p.merge(base[["g0", "dec", "ter", "ap_gini0", "cont0"]], on="c", how="left")
med = base.ap_gini0.median(); p["half"] = np.where(p.ap_gini0.isna(), "", np.where(p.ap_gini0 <= med, "dispersed", "concentrated"))
# peer instruments: leave-out means within (year, group)
wide = p.pivot(index="c", columns="y", values="ln_gaci_max")            # country x year
info = base.loc[wide.index]
def peer_mean(mask_fn, weight_fn=None):
    out = pd.DataFrame(index=wide.index, columns=wide.columns, dtype=float)
    for c in wide.index:
        m = mask_fn(c) & (wide.index != c)
        if m.sum() == 0: continue
        W = np.ones(m.sum()) if weight_fn is None else weight_fn(c, m)
        sub = wide[m]; num = (sub.T * W).T.sum(axis=0, min_count=1); den = (sub.notna().T * W).T.sum(axis=0)
        out.loc[c] = num / den.replace(0, np.nan)
    return out.stack().rename("v").reset_index().rename(columns={"level_1": "y"})
P = {}
P["P1 same 1996 decile"] = peer_mean(lambda c: (info.dec == info.loc[c, "dec"]).values)
P["P2 same 1996 tercile"] = peer_mean(lambda c: (info.ter == info.loc[c, "ter"]).values)
P["P3 same decile, other continent"] = peer_mean(lambda c: ((info.dec == info.loc[c, "dec"]) & (info.cont0 != info.loc[c, "cont0"])).values)
P["P4 other continent, similarity-weighted"] = peer_mean(lambda c: (info.cont0 != info.loc[c, "cont0"]).values, lambda c, m: np.exp(-np.abs(info.g0[m].values - info.loc[c, "g0"]) / 0.15))
for k, v in P.items(): p = p.merge(v.rename(columns={"v": k}), on=["c", "y"], how="left")
rows = []
for k in P:
    for samp in ["full", "concentrated", "dispersed"]:
        d = p if samp == "full" else p[p.half == samp]
        for o in ["ln_gini_mkt", "ln_gini_disp", "ln_spt_b50"]:
            dd = d.dropna(subset=[o, "ln_gaci_max", "lnpop", k]).rename(columns={k: "Z"})
            fs = pf.feols("ln_gaci_max ~ Z + lnpop | c + y", dd, vcov={"CRV1": "c"}); iv = pf.feols(f"{o} ~ lnpop | c + y | ln_gaci_max ~ Z", dd, vcov={"CRV1": "c"})
            rows.append(dict(instrument=k, sample=samp, outcome=o, fs_b=fs.coef()["Z"], fs_se=fs.se()["Z"], F=(fs.coef()["Z"] / fs.se()["Z"]) ** 2, b=iv.coef()["ln_gaci_max"], se=iv.se()["ln_gaci_max"], p=iv.pvalue()["ln_gaci_max"], N=len(dd), n_c=dd.c.nunique()))
r = pd.DataFrame(rows); r.to_csv("_iv_peer_shock_results.csv", index=False)
pd.set_option("display.width", 240); print(r.assign(fs_b=r.fs_b.round(3), fs_se=r.fs_se.round(3), F=r.F.round(1), b=r.b.round(3), se=r.se.round(3), p=r.p.round(3)).to_string(index=False))
