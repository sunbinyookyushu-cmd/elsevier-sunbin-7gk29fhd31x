# -*- coding: utf-8 -*-
"""57_iv_others_growth.py : country-specific shifter instruments for own ln GACI_max (user, 2026-09-28):
   leave-out weighted means of OTHER countries' ln GACI (nbr_g_*) from ../GACI_CO2/spillover_bands.csv, under
   inverse-distance, distance-band, exponential-kernel, five-nearest and within/outside-region weights.
   Each is a shift-share with a country-specific shift (others' connectivity growth) and fixed geographic weights.
   For each candidate: first-stage KP F (alone and jointly with the Feyrer interaction) and 2SLS on ln market Gini,
   ln disp. Gini and bottom-50 share; full sample and the baseline airport-concentration split.
   Output: _iv_others_growth_results.csv"""
import os, numpy as np, pandas as pd, pyfixest as pf
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gini_disp", "ln_gaci_max", "lnpop", "feyrer_int"])
sb = pd.read_csv("../GACI_CO2/spillover_bands.csv"); e = pd.read_csv("ineq_panel_ext.csv", usecols=["c", "y", "ln_spt_b50"]); g = pd.read_csv("_airport_gini.csv")
p = p.merge(sb, on=["c", "y"], how="left").merge(e, on=["c", "y"], how="left").merge(g[["c", "y", "ap_gini"]], on=["c", "y"], how="left")
base = p.sort_values("y").groupby("c").first()[["ap_gini"]].rename(columns={"ap_gini": "ap_gini0"}); p = p.merge(base, on="c", how="left")
med = p.groupby("c").ap_gini0.first().median(); p["half"] = np.where(p.ap_gini0.isna(), "", np.where(p.ap_gini0 <= med, "dispersed", "concentrated"))
CAND = [c for c in sb.columns if c.startswith("nbr_g_")]
print("candidates:", CAND)
def F_of(fs, zs):
    if len(zs) == 1: return (fs.coef()[zs[0]] / fs.se()[zs[0]]) ** 2
    idx = [list(fs.coef().index).index(z) for z in zs]; b = fs.coef()[zs].values; V = fs._vcov[np.ix_(idx, idx)]; return float(b @ np.linalg.solve(V, b) / len(zs))
rows = []
for z in CAND:
    for zs, tag in [([z], "alone"), ([z, "feyrer_int"], "with Feyrer")]:
        for samp in ["full", "concentrated", "dispersed"]:
            d = p if samp == "full" else p[p.half == samp]
            for o in ["ln_gini_mkt", "ln_gini_disp", "ln_spt_b50"]:
                dd = d.dropna(subset=[o, "ln_gaci_max", "lnpop"] + zs)
                if dd.c.nunique() < 20 or dd[z].std() == 0: continue
                try:
                    fs = pf.feols("ln_gaci_max ~ " + " + ".join(zs) + " + lnpop | c + y", dd, vcov={"CRV1": "c"})
                    iv = pf.feols(f"{o} ~ lnpop | c + y | ln_gaci_max ~ " + " + ".join(zs), dd, vcov={"CRV1": "c"})
                except Exception as ex: print("skip", z, tag, samp, o, ex); continue
                rows.append(dict(instrument=z, spec=tag, sample=samp, outcome=o, fs_b=fs.coef()[z], fs_se=fs.se()[z], F=F_of(fs, zs), b=iv.coef()["ln_gaci_max"], se=iv.se()["ln_gaci_max"], p=iv.pvalue()["ln_gaci_max"], N=len(dd), n_c=dd.c.nunique()))
r = pd.DataFrame(rows); r.to_csv("_iv_others_growth_results.csv", index=False)
pd.set_option("display.width", 240)
s = r[(r.spec == "alone") & (r.outcome == "ln_gini_mkt")].pivot(index="instrument", columns="sample", values=["F", "b", "p"]).round(2)
print("\n=== alone, ln market Gini: F / b / p by sample ===\n", s.to_string())
s2 = r[(r.spec == "alone") & (r.sample == "full")].pivot(index="instrument", columns="outcome", values=["b", "p"]).round(3); print("\n=== alone, full sample, all outcomes ===\n", s2.to_string())
s3 = r[(r.spec == "with Feyrer") & (r.outcome == "ln_gini_mkt")].pivot(index="instrument", columns="sample", values=["F", "b", "p"]).round(2); print("\n=== with Feyrer, ln market Gini ===\n", s3.to_string())
