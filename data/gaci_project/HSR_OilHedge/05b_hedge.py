# -*- coding: utf-8 -*-
"""B. HSR as an oil-shock hedge: does an airport's fuel-price elasticity of seats change after an HSR station opens
within R km? (airport x month, 12-month differences, 1997-2019)

  D12 ln y_it = a_i + d_(country x month) + b1 (D12 ln P_(t-3) x post_it) + b2 (D12 ln P_(t-3) x ever_i) + b3 post_it + e
b1 < 0: after HSR arrives, the airport cuts more seats when jet fuel gets dearer (travellers shift to electric rail).
Country x month FE absorb the common price response within each country. OLS and 2SLS (Kaenzig / BH 12-month shock
sums, lag 3, x post and x ever). Variance: country cluster + Newey-West over months (L = 12; _est.py), country cluster
in brackets. Split-sample version: ever-treated airports only (their own pre vs post).
Output: _res_hsr_hedge.csv
"""
import gc
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, r"..\GACI_FuelShock")
from _est import fit

COLS = ["airport_iata", "iso3", "t", "year", "ym", "iso_ym", "d12_ln_seats", "d12_ln_seats_dom", "d12_ln_seats_intl",
        "d12_ln_co2", "d12_lnjet_l3", "kz_s12_l3", "bh_neg_s12_l3"]
am = pd.read_parquet(r"..\GACI_FuelShock\_main_panel.parquet", columns=COLS)
am = am[(am.year >= 1997) & (am.year <= 2019)].copy()
for c in COLS[6:]:
    am[c] = am[c].astype("float32")
hs = pd.read_csv("data/airport_hsr.csv", usecols=["airport_iata", "hsr_date_30", "hsr_date_50", "hsr_date_100"],
                 parse_dates=["hsr_date_30", "hsr_date_50", "hsr_date_100"])
am = am.merge(hs, on="airport_iata", how="left")
am["date"] = pd.to_datetime(am.ym + "-01")
VC = ("dk", "iso3", "t", 12)
ALT = [("cl", "iso3")]
PR = "d12_lnjet_l3"
SH = {"KZ": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
HQ = ["CHN", "JPN", "KOR", "TWN", "FRA", "HKG", "MAC"]
rows = []

for R in (50, 30, 100):
    hd = am[f"hsr_date_{R}"]
    d = am.assign(ever=hd.notna().astype("float32"), post=(hd.notna() & (am.date >= hd)).astype("float32"))
    d = d[~(hd.notna() & (hd.dt.year < 1997))]
    for y in ["d12_ln_seats_dom", "d12_ln_seats", "d12_ln_seats_intl", "d12_ln_co2"]:
        for smp in ["all", "ever-treated only", "China", "excl. China", "high-quality dates (CN JP KR TW FR)"]:
            if R != 50 and not (y == "d12_ln_seats_dom" and smp == "all"):
                continue
            msk = {"all": d.index == d.index, "ever-treated only": d.ever == 1, "China": d.iso3 == "CHN",
                   "excl. China": d.iso3 != "CHN", "high-quality dates (CN JP KR TW FR)": d.iso3.isin(HQ)}[smp]
            dd = d.loc[msk, ["airport_iata", "iso3", "t", "iso_ym", y, PR, "post", "ever"] + list(SH.values())].dropna(subset=[y, PR]).copy()
            if dd.loc[dd.ever == 1, "airport_iata"].nunique() < 5:
                continue
            dd["xp"] = dd[PR] * dd.post
            dd["xe"] = dd[PR] * dd.ever
            ex = ["xp", "post"] + (["xe"] if smp != "ever-treated only" else [])
            # a single-country sample has one country cluster (G/(G-1) undefined): cluster by airport there
            one = dd.iso3.nunique() < 10
            VCs = ("dk", "airport_iata", "t", 12) if one else VC
            ALTs = [("cl", "airport_iata")] if one else ALT
            r = fit(dd, y, exog=ex, fes=["airport_iata", "iso_ym"], vc=VCs, vc_alt=ALTs)
            ntr = int(dd.loc[dd.ever == 1, "airport_iata"].nunique())
            rows.append(dict(radius=R, outcome=y, sample=smp, estimator="OLS", cluster="airport" if one else "country", b=r["coef"]["xp"], se=r["se"]["xp"],
                             p=r["p"]["xp"], se_cl=r["alt"][0]["se"]["xp"], p_cl=r["alt"][0]["p"]["xp"],
                             b_ever=r["coef"].get("xe", np.nan), se_ever=r["se"].get("xe", np.nan),
                             b_post=r["coef"]["post"], se_post=r["se"]["post"], n=r["n"], n_treated=ntr, F=np.nan))
            for k, s in SH.items():
                de = dd.dropna(subset=[s]).copy()
                de["zp"] = de[s] * de.post
                de["ze"] = de[s] * de.ever
                en, iv = (["xp", "xe"], ["zp", "ze"]) if smp != "ever-treated only" else (["xp"], ["zp"])
                r = fit(de, y, endog=en, instr=iv, exog=["post"], fes=["airport_iata", "iso_ym"], vc=VCs, vc_alt=ALTs)
                rows.append(dict(radius=R, outcome=y, sample=smp, estimator="2SLS-" + k, cluster="airport" if one else "country", b=r["coef"]["xp"], se=r["se"]["xp"],
                                 p=r["p"]["xp"], se_cl=r["alt"][0]["se"]["xp"], p_cl=r["alt"][0]["p"]["xp"],
                                 b_ever=r["coef"].get("xe", np.nan), se_ever=r["se"].get("xe", np.nan),
                                 b_post=r["coef"]["post"], se_post=r["se"]["post"], n=r["n"], n_treated=ntr,
                                 F=r["fs"].get("xp", {}).get("F", np.nan)))
                del de
            del dd
            gc.collect()
        print("R", R, y, "done", flush=True)
    pd.DataFrame(rows).to_csv("_res_hsr_hedge.csv", index=False)      # save as we go

res = pd.DataFrame(rows)
res.to_csv("_res_hsr_hedge.csv", index=False)
pd.set_option("display.width", 230)
print(res[["radius", "outcome", "sample", "estimator", "b", "se", "p", "p_cl", "b_ever", "b_post", "F", "n", "n_treated"]].round(4).to_string(index=False))
