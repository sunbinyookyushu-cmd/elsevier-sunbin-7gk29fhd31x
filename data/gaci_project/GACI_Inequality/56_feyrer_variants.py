# -*- coding: utf-8 -*-
"""56_feyrer_variants.py : first-stage strength of Feyrer-type instruments (user, 2026-09-28).
   Instruments (from ../build_feyrer_iv.py, merged from ../gaci_panel_feyrer.csv):
     A  feyrer_int = a_t x ln MA^air_1996                       (current headline)
     B  adv_int    = a_t x [ln MA^air_1996 - ln MA^sea_1996]     (Feyrer's air-vs-sea advantage)
     C  ln_feyrer  = ln[a_t MA^air_ct + (1-a_t) MA^sea_ct]       (Feyrer's effective market access, time-varying)
     D  A + B jointly
   For each: first-stage KP F and 2SLS on ln market Gini, ln disp. Gini, bottom-50 share; full sample and the
   baseline airport-concentration split of 54_airport_gini.py. Country + year FE, ln pop, cluster country.
   Output: _feyrer_variants_results.csv"""
import os, numpy as np, pandas as pd, pyfixest as pf
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gini_disp", "ln_gaci_max", "lnpop", "feyrer_int"])
f = pd.read_csv("../gaci_panel_feyrer.csv", usecols=["c", "y", "adv_int", "ln_feyrer"])
e = pd.read_csv("ineq_panel_ext.csv", usecols=["c", "y", "ln_spt_b50"]); g = pd.read_csv("_airport_gini.csv")
p = p.merge(f, on=["c", "y"], how="left").merge(e, on=["c", "y"], how="left").merge(g[["c", "y", "ap_gini"]], on=["c", "y"], how="left")
base = p.sort_values("y").groupby("c").first()[["ap_gini"]].rename(columns={"ap_gini": "ap_gini0"}); p = p.merge(base, on="c", how="left")
med = p.groupby("c").ap_gini0.first().median(); p["half"] = np.where(p.ap_gini0.isna(), "", np.where(p.ap_gini0 <= med, "dispersed", "concentrated"))
print("corr(feyrer_int, adv_int) within country:", round(p.assign(a=p.feyrer_int - p.groupby("c").feyrer_int.transform("mean"), b=p.adv_int - p.groupby("c").adv_int.transform("mean"))[["a", "b"]].corr().iloc[0, 1], 3))
IVS = {"A feyrer_int (a_t x ln MA_air96)": ["feyrer_int"], "B adv_int (a_t x [ln MA_air96 - ln MA_sea96])": ["adv_int"], "C ln_feyrer (effective MA, time-varying)": ["ln_feyrer"], "D A + B": ["feyrer_int", "adv_int"]}
rows = []
def F_of(fs, zs):
    if len(zs) == 1: return (fs.coef()[zs[0]] / fs.se()[zs[0]]) ** 2
    idx = [list(fs.coef().index).index(z) for z in zs]; b = fs.coef()[zs].values; V = fs._vcov[np.ix_(idx, idx)]; return float(b @ np.linalg.solve(V, b) / len(zs))
for lab, zs in IVS.items():
    for samp in ["full", "concentrated", "dispersed"]:
        for o in ["ln_gini_mkt", "ln_gini_disp", "ln_spt_b50"]:
            d = p if samp == "full" else p[p.half == samp]
            d = d.dropna(subset=[o, "ln_gaci_max", "lnpop"] + zs)
            fs = pf.feols("ln_gaci_max ~ " + " + ".join(zs) + " + lnpop | c + y", d, vcov={"CRV1": "c"})
            iv = pf.feols(f"{o} ~ lnpop | c + y | ln_gaci_max ~ " + " + ".join(zs), d, vcov={"CRV1": "c"})
            rows.append(dict(iv=lab, sample=samp, outcome=o, fs_b=" ; ".join("%.3f (%.3f)" % (fs.coef()[z], fs.se()[z]) for z in zs), F=F_of(fs, zs), b=iv.coef()["ln_gaci_max"], se=iv.se()["ln_gaci_max"], p=iv.pvalue()["ln_gaci_max"], N=len(d), n_c=d.c.nunique()))
r = pd.DataFrame(rows); r.to_csv("_feyrer_variants_results.csv", index=False)
pd.set_option("display.width", 240); pd.set_option("display.max_colwidth", 60)
print(r.assign(F=r.F.round(1), b=r.b.round(3), se=r.se.round(3), p=r.p.round(3)).to_string(index=False))
