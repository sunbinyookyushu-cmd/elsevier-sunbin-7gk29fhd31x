# -*- coding: utf-8 -*-
"""HSR as an oil-shock hedge for air travel: airport x month, 1997-2019.

Treatment: post_R = 1 from the month an HSR station within R km of the airport opens (R = 30 / 50 / 100 km,
04_link_airports.py). Airports whose first nearby station opened before 1997 are always treated inside the
window and are dropped from the staggered estimates (kept in a robustness row).

A. Level effect of HSR on seats (Gardner two-stage DiD, pyfixest did2s): first stage on untreated observations with
   airport + country x year-month FE; second stage post (and event time in years). SE clustered by airport.
B. Oil hedge: D12 ln y_it = a_i + d_(country x month) + b1 (D12 ln P_(t-3) x post_it) + b2 (D12 ln P_(t-3) x ever_i)
   + b3 post_it + e.  b1 = change in the airport's fuel-price elasticity after HSR opens (relative to its own
   pre-period and to airports never reached by HSR). OLS and 2SLS (Kaenzig / BH shock sums x post, x ever).
   Variance: country cluster + Newey-West over months (L = 12).
   Split-sample version: ever-treated airports only.
Output: _res_hsr_level.csv, _res_hsr_hedge.csv, _res_hsr_es.csv
"""
import sys
import numpy as np
import pandas as pd
import pyfixest as pf
sys.path.insert(0, r"..\GACI_FuelShock")
from _est import fit

am = pd.read_parquet(r"..\GACI_FuelShock\_main_panel.parquet")
lv = pd.read_parquet(r"..\GACI_FuelShock\airport_month.parquet", columns=["airport_iata", "t", "ln_seats", "ln_seats_dom", "ln_seats_intl"])
am = am.drop(columns=[c for c in ["ln_seats", "ln_seats_dom", "ln_seats_intl"] if c in am.columns]).merge(lv, on=["airport_iata", "t"], how="left")
hs = pd.read_csv("data/airport_hsr.csv", parse_dates=["hsr_date_30", "hsr_date_50", "hsr_date_100"])
M = am[(am.year >= 1997) & (am.year <= 2019)].merge(hs[["airport_iata", "hsr_date_30", "hsr_date_50", "hsr_date_100", "km_nearest_hsr"]],
                                                    on="airport_iata", how="left")
M["date"] = pd.to_datetime(M.ym + "-01")
VC = ("dk", "iso3", "t", 12)
ALT = [("cl", "iso3"), ("cl2", "iso3", "year")]
PR = "d12_lnjet_l3"
SH = {"KZ": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
lev, hed, es = [], [], []

for R in (50, 30, 100):
    d0 = M.copy()
    hd = d0[f"hsr_date_{R}"]
    d0["ever"] = hd.notna().astype(float)
    d0["post"] = (hd.notna() & (d0.date >= hd)).astype(float)
    pre97 = hd.notna() & (hd.dt.year < 1997)
    d = d0[~pre97].copy()
    d["cohort"] = hd[~pre97].dt.year
    tag = f"R{R}"
    # ---- A. level effect (Gardner did2s) ----
    for y in (["ln_seats_dom", "ln_seats", "ln_seats_intl"] if R == 50 else ["ln_seats_dom"]):
        dd = d.dropna(subset=[y]).copy()
        dd["post_b"] = dd.post.astype(bool)
        try:
            m = pf.did2s(dd, yname=y, first_stage="~ 0 | airport_iata + iso_ym", second_stage="~ post",
                         treatment="post_b", cluster="airport_iata")
            lev.append(dict(radius=R, outcome=y, sample="all", b=m.coef()["post"], se=m.se()["post"], p=m.pvalue()["post"],
                            n=len(dd), n_treated=int(dd.loc[dd.ever == 1, "airport_iata"].nunique())))
            for smp, msk in [("China", dd.iso3 == "CHN"), ("excl. China", dd.iso3 != "CHN"),
                             ("high-quality dates (CN JP KR TW FR)", dd.iso3.isin(["CHN", "JPN", "KOR", "TWN", "FRA", "HKG", "MAC"]))]:
                ds = dd[msk]
                if ds.loc[ds.ever == 1, "airport_iata"].nunique() < 5:
                    continue
                m = pf.did2s(ds, yname=y, first_stage="~ 0 | airport_iata + iso_ym", second_stage="~ post",
                             treatment="post_b", cluster="airport_iata")
                lev.append(dict(radius=R, outcome=y, sample=smp, b=m.coef()["post"], se=m.se()["post"], p=m.pvalue()["post"],
                                n=len(ds), n_treated=int(ds.loc[ds.ever == 1, "airport_iata"].nunique())))
        except Exception as e:
            lev.append(dict(radius=R, outcome=y, sample="all", b=np.nan, se=np.nan, p=np.nan, n=len(dd), note=str(e)[:120]))
        # event study (years relative to opening), R = 50 and domestic seats only
        if R == 50 and y == "ln_seats_dom":
            dd["rel"] = np.where(dd.ever == 1, (dd.year - dd.cohort).clip(-6, 6), -1000)
            dd["rel"] = dd.rel.astype(int)
            m = pf.did2s(dd, yname=y, first_stage="~ 0 | airport_iata + iso_ym", second_stage="~ i(rel, ref=-1000)",
                         treatment="post_b", cluster="airport_iata")
            for k, v in m.coef().items():
                es.append(dict(term=k, b=v, se=m.se()[k], p=m.pvalue()[k]))
    # ---- B. oil hedge ----
    for y in ["d12_ln_seats_dom", "d12_ln_seats", "d12_ln_seats_intl", "d12_ln_co2"]:
        HQ = d.iso3.isin(["CHN", "JPN", "KOR", "TWN", "FRA", "HKG", "MAC"])
        for smp, msk in [("all", d.index == d.index), ("ever-treated only", d.ever == 1), ("China", d.iso3 == "CHN"),
                         ("excl. China", d.iso3 != "CHN"), ("high-quality dates (CN JP KR TW FR)", HQ)]:
            if R != 50 and not (y == "d12_ln_seats_dom" and smp == "all"):
                continue
            dd = d[msk].dropna(subset=[y, PR]).copy()
            if dd.loc[dd.ever == 1, "airport_iata"].nunique() < 5:
                continue
            dd["xp"] = dd[PR] * dd.post
            dd["xe"] = dd[PR] * dd.ever
            ex = ["xp", "post"] + (["xe"] if smp != "ever-treated only" else [])
            r = fit(dd, y, exog=ex, fes=["airport_iata", "iso_ym"], vc=VC, vc_alt=ALT)
            hed.append(dict(radius=R, outcome=y, sample=smp, estimator="OLS", term="D12 lnP x post", b=r["coef"]["xp"],
                            se=r["se"]["xp"], p=r["p"]["xp"], se_cl=r["alt"][0]["se"]["xp"], p_cl=r["alt"][0]["p"]["xp"],
                            b_post=r["coef"]["post"], se_post=r["se"]["post"], n=r["n"],
                            n_treated=int(dd.loc[dd.ever == 1, "airport_iata"].nunique()), F=np.nan))
            for k, s in SH.items():
                de = dd.dropna(subset=[s]).copy()
                de["zp"] = de[s] * de.post
                de["ze"] = de[s] * de.ever
                en, iv = (["xp", "xe"], ["zp", "ze"]) if smp != "ever-treated only" else (["xp"], ["zp"])
                r = fit(de, y, endog=en, instr=iv, exog=["post"], fes=["airport_iata", "iso_ym"], vc=VC, vc_alt=ALT)
                hed.append(dict(radius=R, outcome=y, sample=smp, estimator="2SLS-" + k, term="D12 lnP x post", b=r["coef"]["xp"],
                                se=r["se"]["xp"], p=r["p"]["xp"], se_cl=r["alt"][0]["se"]["xp"], p_cl=r["alt"][0]["p"]["xp"],
                                b_post=r["coef"]["post"], se_post=r["se"]["post"], n=r["n"],
                                n_treated=int(de.loc[de.ever == 1, "airport_iata"].nunique()),
                                F=r["fs"].get("xp", {}).get("F", np.nan)))
    print("R", R, "done", flush=True)

pd.DataFrame(lev).to_csv("_res_hsr_level.csv", index=False)
pd.DataFrame(hed).to_csv("_res_hsr_hedge.csv", index=False)
pd.DataFrame(es).to_csv("_res_hsr_es.csv", index=False)
pd.set_option("display.width", 250)
print(pd.DataFrame(lev).round(4).to_string(index=False))
print(pd.DataFrame(hed)[["radius", "outcome", "sample", "estimator", "b", "se", "p", "p_cl", "b_post", "F", "n", "n_treated"]].round(4).to_string(index=False))
