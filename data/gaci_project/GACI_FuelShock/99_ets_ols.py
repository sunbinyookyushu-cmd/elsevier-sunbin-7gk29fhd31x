# -*- coding: utf-8 -*-
"""EU ETS without an instrument (fallback C + D, 2026-10-02): Kaenzig-based IVs had first-stage F < 5 (97: ~4 in changes;
98: ~0.3 in levels). Following Fageda & Oesingmann (2025), the EUA price is treated as exogenous to aviation (aviation is
a small part of ETS allowance demand); common shocks absorbed by month / region x month FE.
  ln S_it = a_(i x cal.month) + FE_t + b_A (P_(t-3) x G_i x Area_i x ETS_t) + b_R (P_(t-3) x Rec_i x (1-Area_i) x ETS_t) + e
  P = EUA monthly mean (EUR 10s); G, Rec from 96. Specs: month FE; region x month FE; + exposure-specific linear trends;
  placebo 2008-2011 (aviation outside the ETS) with the same interactions (ETS_t replaced by 1).
D: annual ln GACI / ln eigenvector / ln betweenness, airport FE + year FE or region x year FE (+ trends), all airports and
   hubs (>= 5 million seats 2007), 2008-2019; placebo 2008-2011.
SE: country cluster + Newey-West (12 months / 2 years).
Output: _res_ets_ols.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import warnings

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from _est import fit

warnings.filterwarnings("ignore")
geo = pd.read_csv("geo_ets_exposure.csv")
reg = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "Region"]).dropna().drop_duplicates("airport_iata")
e = pd.read_csv(r"data_external\aviation_taxes\EUA_monthly_sendeco2_2008_2025.csv")
e["t"] = e.month.str[:4].astype(int) * 12 + e.month.str[5:7].astype(int)
P = (e.set_index("t").eua_mean_eur / 10).sort_index()
Py = e.assign(year=e.month.str[:4].astype(int)).groupby("year").eua_mean_eur.mean() / 10

am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats"]).to_pandas()
k07 = am[am.year == 2007].groupby("airport_iata").dep_seats.sum()
am = am[am.iso3.notna() & am.year.between(2008, 2019) & (am.dep_seats > 0) & am.airport_iata.isin(k07[k07 > 0].index)].copy()
am["t"] = am.year * 12 + am.month
am["tt"] = am.t
am["ln_s"] = np.log(am.dep_seats)
am = am.merge(geo[["airport_iata", "ets_area", "geo_share_t1", "rec_index"]], on="airport_iata").merge(reg, on="airport_iata", how="left")
am["rec_index"] = am.rec_index.fillna(0)
am["area"] = am.ets_area.astype(int)
am["P"] = (am.t - 3).map(P)
am["ETS"] = ((am.t - 3) >= 2012 * 12 + 1).astype(int)
am["tlin"] = (am.t - 2008 * 12) / 12
am["fe_u"] = am.airport_iata + "_" + am.month.astype(str)
am["reg_t"] = am.Region.astype(str) + "_" + am.t.astype(str)
am = am.dropna(subset=["P"])

rows = []


def run(part, spec, d, y, fes, win, L, trend=False):
    d = d.copy()
    d["xA"], d["xR"] = d.Pv * d.geo_share_t1 * d.area * win, d.Pv * d.rec_index * (1 - d.area) * win
    ex = ["xA", "xR"]
    if trend:
        d["trA"], d["trR"] = d.geo_share_t1 * d.area * d.tlin, d.rec_index * (1 - d.area) * d.tlin
        ex += ["trA", "trR"]
    s = d.dropna(subset=[y])
    o = fit(s, y, exog=ex, fes=fes, vc=("dk", "iso3", "tt", L), return_fs=False)
    for v, lab in [("xA", "carbon price x exposure (area)"), ("xR", "carbon price x closeness (outside)")]:
        rows.append(dict(part=part, spec=spec, outcome=y, term=lab, b=o["coef"][v], se=o["se"][v], p=o["p"][v], n=o["n"],
                         airports=s.airport_iata.nunique()))


am["Pv"] = am.P
run("C monthly seats", "month FE", am, "ln_s", ["fe_u", "t"], am.ETS, 12)
run("C monthly seats", "region x month FE", am, "ln_s", ["fe_u", "reg_t"], am.ETS, 12)
run("C monthly seats", "region x month FE + exposure trends", am, "ln_s", ["fe_u", "reg_t"], am.ETS, 12, trend=True)
pre = am[am.t <= 2011 * 12 + 12]
run("C monthly seats", "placebo 2008-2011, region x month FE", pre, "ln_s", ["fe_u", "reg_t"], 1, 12)
print("C done", flush=True)

hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI", "Eigen", "NorBetweenness", "Region"])
hp = hp[hp.year.between(2008, 2019) & (hp.GACI > 0) & hp.airport_iata.isin(k07[k07 > 0].index)].copy()
hp["ln_gaci"] = np.log(hp.GACI)
hp["ln_eigen"] = np.log(hp.Eigen.where(hp.Eigen > 0))
hp["ln_betw"] = np.log1p(hp.NorBetweenness * 1e4)
hp = hp.merge(geo[["airport_iata", "ets_area", "geo_share_t1", "rec_index"]], on="airport_iata")
hp["rec_index"] = hp.rec_index.fillna(0)
hp["area"] = hp.ets_area.astype(int)
hp["Pv"] = hp.year.map(Py)
hp["ETS"] = (hp.year >= 2012).astype(int)
hp["tt"], hp["tlin"] = hp.year, hp.year - 2008
hp["reg_y"] = hp.Region.astype(str) + "_" + hp.year.astype(str)
hp["hub"] = hp.airport_iata.map(k07).fillna(0) >= 5e6
for samp, H in [("all airports", hp), ("hubs (>= 5m seats 2007)", hp[hp.hub])]:
    for y in ["ln_gaci", "ln_eigen", "ln_betw"]:
        run("D annual connectivity", f"{samp} | year FE", H, y, ["airport_iata", "year"], H.ETS, 2)
        run("D annual connectivity", f"{samp} | region x year FE", H, y, ["airport_iata", "reg_y"], H.ETS, 2)
        run("D annual connectivity", f"{samp} | region x year FE + trends", H, y, ["airport_iata", "reg_y"], H.ETS, 2, trend=True)
print("D done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_ets_ols.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 300)
print(R.round(4).to_string(index=False))
