# -*- coding: utf-8 -*-
"""A. Level effect of an HSR station opening near an airport on its seats (airport x month, 1997-2019).

Gardner (2022) two-stage DiD, implemented directly (pyfixest's did2s builds a dense matrix over the ~55k
country x month effects and exhausted memory):
  stage 1: y_it = a_i + d_(country x month) + e on untreated observations (never-treated airports and treated
           airports before their opening month); predict a_i + d for every observation
  stage 2: y_it - (a_i + d) on post_it (or on event-time dummies), all observations
Point estimates equal did2s / the imputation estimator. SE: clustered by airport and by country in stage 2, ignoring
first-stage estimation error (the usual shortcut; slightly understates uncertainty).
Airports whose first nearby station opened before 1997 are dropped (always treated in the window).
Output: _res_hsr_level.csv, _res_hsr_es.csv
"""
import gc
import numpy as np
import pandas as pd
import pyfixest as pf

COLS = ["airport_iata", "iso3", "t", "year", "ym", "iso_ym", "ln_seats", "ln_seats_dom", "ln_seats_intl"]
am = pd.read_parquet(r"..\GACI_FuelShock\airport_month.parquet", columns=["airport_iata", "iso3", "t", "year", "ym",
                                                                          "ln_seats", "ln_seats_dom", "ln_seats_intl", "ln_co2"])
base = pd.read_csv(r"..\GACI_FuelShock\airport_base.csv", usecols=["airport_iata", "GACI_96", "seats_96"])
base = base[base.GACI_96.notna() & (base.seats_96 > 0)]
am = am[am.airport_iata.isin(base.airport_iata) & am.iso3.notna() & (am.year >= 1997) & (am.year <= 2019)].copy()
am["iso_ym"] = am.iso3 + "_" + am.ym
for c in ["ln_seats", "ln_seats_dom", "ln_seats_intl", "ln_co2"]:
    am[c] = am[c].astype("float32")
hs = pd.read_csv("data/airport_hsr.csv", usecols=["airport_iata", "hsr_date_30", "hsr_date_50", "hsr_date_100"],
                 parse_dates=["hsr_date_30", "hsr_date_50", "hsr_date_100"])
am = am.merge(hs, on="airport_iata", how="left")
am["date"] = pd.to_datetime(am.ym + "-01")
HQ = ["CHN", "JPN", "KOR", "TWN", "FRA", "HKG", "MAC"]
lev, es = [], []


def gardner(d, y, second):
    """d must hold y, post, airport_iata, iso_ym, iso3 and the second-stage regressors in `second`"""
    d = d.dropna(subset=[y]).copy()
    un = d[d.post == 0]
    m1 = pf.feols(f"{y} ~ 1 | airport_iata + iso_ym", data=un)
    fe = m1.fixef()
    fa = pd.Series(fe["C(airport_iata)"])
    fc = pd.Series(fe["C(iso_ym)"])
    d["yhat"] = d.airport_iata.map(fa) + d.iso_ym.map(fc)
    d = d[d.yhat.notna()].copy()                                   # needs pre-period obs and untreated peers
    d["ytil"] = d[y] - d.yhat
    rhs = " + ".join(second)
    m2a = pf.feols(f"ytil ~ {rhs}", data=d, vcov={"CRV1": "airport_iata"})
    # one-country samples have a single country cluster: report the airport-cluster SE in both columns there
    m2c = pf.feols(f"ytil ~ {rhs}", data=d, vcov={"CRV1": "iso3"}) if d.iso3.nunique() >= 10 else m2a
    return m2a, m2c, d


for R in (50, 30, 100):
    hd = am[f"hsr_date_{R}"]
    d0 = am.assign(ever=hd.notna().astype("int8"), post=(hd.notna() & (am.date >= hd)).astype("int8"))
    d0 = d0[~(hd.notna() & (hd.dt.year < 1997))]
    for y in (["ln_seats_dom", "ln_seats", "ln_seats_intl", "ln_co2"] if R == 50 else ["ln_seats_dom"]):
        for smp, msk in [("all", None), ("China", "CHN"), ("excl. China", "exCHN"), ("high-quality dates (CN JP KR TW FR)", "HQ")]:
            if R != 50 and smp != "all":
                continue
            dd = d0 if msk is None else (d0[d0.iso3 == "CHN"] if msk == "CHN" else d0[d0.iso3 != "CHN"] if msk == "exCHN"
                                         else d0[d0.iso3.isin(HQ)])
            try:
                m2a, m2c, used = gardner(dd, y, ["post"])
                lev.append(dict(radius=R, outcome=y, sample=smp, b=m2a.coef()["post"], se_airport=m2a.se()["post"],
                                p_airport=m2a.pvalue()["post"], se_country=m2c.se()["post"], p_country=m2c.pvalue()["post"],
                                n=len(used), n_treated=int(used.loc[used.ever == 1, "airport_iata"].nunique()),
                                n_post_obs=int(used.post.sum())))
            except Exception as e:
                lev.append(dict(radius=R, outcome=y, sample=smp, note=str(e)[:150]))
            gc.collect()
        print("R", R, y, "done", flush=True)
    if R == 50:
        # event study, years relative to opening, binned at -6 / +6; reference = never treated and the year before (-1)
        for y in ["ln_seats_dom", "ln_seats", "ln_co2"]:
            dd = d0.copy()
            coh = dd[f"hsr_date_{R}"].dt.year
            rel = (dd.year - coh).clip(-6, 6)
            names = []
            for k in range(-6, 7):
                if k == -1:
                    continue
                nm = f"e_m{abs(k)}" if k < 0 else f"e_p{k}"
                dd[nm] = ((dd.ever == 1) & (rel == k)).astype("int8")
                names.append(nm)
            m2a, m2c, used = gardner(dd, y, names)
            for nm in names:
                k = -int(nm[3:]) if nm.startswith("e_m") else int(nm[3:])
                es.append(dict(outcome=y, rel_year=k, b=m2a.coef()[nm], se_airport=m2a.se()[nm], p=m2a.pvalue()[nm],
                               se_country=m2c.se()[nm]))
            es.append(dict(outcome=y, rel_year=-1, b=0.0, se_airport=0.0, p=np.nan, se_country=0.0))
            print("event study", y, "done", flush=True)
            gc.collect()

pd.DataFrame(lev).to_csv("_res_hsr_level.csv", index=False)
pd.DataFrame(es).sort_values(["outcome", "rel_year"]).to_csv("_res_hsr_es.csv", index=False)
pd.set_option("display.width", 220)
print(pd.DataFrame(lev).round(4).to_string(index=False))
print(pd.DataFrame(es).sort_values(["outcome", "rel_year"]).round(4).to_string(index=False))
