# -*- coding: utf-8 -*-
"""4.1 continuous treatment + IV for the EU ETS (user decision 2026-10-02: Feyrer-style geography x Kaenzig carbon
policy surprises).

  D12 ln S_it = a_i + d_t + b_A (D12 lnEUA_(t-3) x G_i x Area_i x ETS_t) + b_R (D12 lnEUA_(t-3) x Rec_i x (1-Area_i) x ETS_t) + e
  instruments: KZc_(t-3, 12m) x G_i x Area_i x ETS_t and KZc x Rec_i x (1-Area_i) x ETS_t
  G_i   = geography-predicted share of airport i's market inside the ETS area (96: 1996 masses, distance^-1)
  Rec_i = same index for airports OUTSIDE the area (closeness to the area's mass: candidate receivers, e.g. IST, ZRH)
  EUA   = monthly mean EU allowance price (SendeCO2, EUR), 12-month log change, lag 3
  KZc   = Kaenzig (AER forthcoming, doi 10.1257/aer.20230448) monthly carbon policy surprise, 12-month sum, lag 3
          (carbonPolicyShocks.xlsx, 114 events 2005-2019)
  ETS_t = 1 when the lagged month is 2012-01 or later (aviation obligations); 2009-04..2011-12 serves as a placebo
          (the carbon price did not cost airlines anything before 2012)
  b_A < 0: airports more exposed to covered routes lose seats when the carbon price rises; b_R > 0: airports outside
  the area but close to it gain (relocation).
Specs: reduced form, IV, IV + region x month FE, placebo before 2012, exposure theta = 2, fuel-weighted exposure
(G x distance to area destinations / 1000 km). Sample: airports with seats in 2007; 2009-04..2019-12.
SE: country cluster + Newey-West 12 (_est "dk"); first-stage F under the same variance.
Output: _res_ets_iv.csv
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
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "dep_seats_intl"]).to_pandas()
am = am[am.iso3.notna() & am.year.between(2007, 2019)].copy()
keep = am[(am.year == 2007)].groupby("airport_iata").dep_seats.sum()
am = am[am.airport_iata.isin(keep[keep > 0].index)]
am["t"] = am.year * 12 + am.month
for v, s in [("ln_s", "dep_seats"), ("ln_i", "dep_seats_intl")]:
    am[v] = np.log(am[s].where(am[s] > 0))
lag = am[["airport_iata", "t", "ln_s", "ln_i"]].copy()
lag["t"] += 12
am = am.merge(lag, on=["airport_iata", "t"], how="left", suffixes=("", "_m12"))
am["y_s"], am["y_i"] = am.ln_s - am.ln_s_m12, am.ln_i - am.ln_i_m12

geo = pd.read_csv("geo_ets_exposure.csv")
reg = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "Region"]).dropna().drop_duplicates("airport_iata")
am = am.merge(geo[["airport_iata", "ets_area", "geo_share_t1", "geo_share_t2", "geo_skm", "rec_index"]], on="airport_iata", how="left")
am = am.merge(reg, on="airport_iata", how="left")
am["rec_index"] = am.rec_index.fillna(0)

e = pd.read_csv(r"data_external\aviation_taxes\EUA_monthly_sendeco2_2008_2025.csv")
e["t"] = e.month.str[:4].astype(int) * 12 + e.month.str[5:7].astype(int)
e = e.set_index("t").sort_index()
k = pd.read_excel(r"data_external\carbon_policy_shocks\carbonPolicyShocks.xlsx", sheet_name="Monthly")
k["t"] = k.Date.str[:4].astype(int) * 12 + k.Date.str[5:].astype(int)
k = k.set_index("t").sort_index()
f = pd.DataFrame(index=range(2005 * 12 + 1, 2020 * 12 + 13))
f["lnEUA"] = np.log(e.eua_mean_eur)
f["dEUA"] = f.lnEUA.shift(3) - f.lnEUA.shift(15)
f["KZc"] = k.Surprise.reindex(f.index).fillna(0).rolling(12, min_periods=12).sum().shift(3)
f["ETS"] = ((f.index - 3) >= 2012 * 12 + 1).astype(int)
tt = f.loc[2009 * 12 + 4: 2019 * 12 + 12]
print("first stage (time series) corr(dEUA, KZc):", round(tt[["dEUA", "KZc"]].corr().iloc[0, 1], 3),
      " ETS period:", round(tt[tt.ETS == 1][["dEUA", "KZc"]].corr().iloc[0, 1], 3), flush=True)
am = am.merge(f[["dEUA", "KZc", "ETS"]], left_on="t", right_index=True, how="left")
d0 = am[am.t.between(2009 * 12 + 4, 2019 * 12 + 12)].dropna(subset=["dEUA", "KZc", "geo_share_t1"]).copy()
d0["area"] = d0.ets_area.astype(int)
d0["reg_t"] = d0.Region.astype(str) + "_" + d0.t.astype(str)


def make(d, G, window):
    d = d.copy()
    d["xA"] = d.dEUA * d[G] * d.area * window
    d["xR"] = d.dEUA * d.rec_index * (1 - d.area) * window
    d["zA"] = d.KZc * d[G] * d.area * window
    d["zR"] = d.KZc * d.rec_index * (1 - d.area) * window
    return d


rows = []


def run(spec, d, y, fes, iv=True):
    s = d.dropna(subset=[y])
    if iv:
        o = fit(s, y, endog=["xA", "xR"], instr=["zA", "zR"], fes=fes, vc=("dk", "iso3", "t", 12))
        for v, lab in [("xA", "carbon cost x exposure (area airports)"), ("xR", "carbon cost x closeness (outside area)")]:
            rows.append(dict(spec=spec, outcome=y, term=lab, b=o["coef"][v], se=o["se"][v], p=o["p"][v], F=o["fs"][v]["F"],
                             n=o["n"], airports=s.airport_iata.nunique()))
    else:
        o = fit(s, y, exog=["zA", "zR"], fes=fes, vc=("dk", "iso3", "t", 12), return_fs=False)
        for v, lab in [("zA", "carbon surprise x exposure (area)"), ("zR", "carbon surprise x closeness (outside)")]:
            rows.append(dict(spec=spec, outcome=y, term=lab, b=o["coef"][v], se=o["se"][v], p=o["p"][v], F=np.nan,
                             n=o["n"], airports=s.airport_iata.nunique()))


ets = d0.ETS
for y in ["y_s", "y_i"]:
    D = make(d0, "geo_share_t1", ets)
    run("reduced form, 2012-2019 ETS window", D, y, ["airport_iata", "t"], iv=False)
    run("IV", D, y, ["airport_iata", "t"])
    run("IV + region x month FE", D, y, ["airport_iata", "reg_t"])
    run("IV, exposure theta = 2", make(d0, "geo_share_t2", ets), y, ["airport_iata", "t"])
    d0["geo_fuel"] = d0.geo_share_t1 * d0.geo_skm / 1000
    run("IV, fuel-weighted exposure", make(d0, "geo_fuel", ets), y, ["airport_iata", "t"])
    pre = d0[d0.ETS == 0]
    run("placebo: reduced form 2009-04..2012-03 (no aviation in ETS)", make(pre, "geo_share_t1", 1), y, ["airport_iata", "t"], iv=False)
    print(y, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_ets_iv.csv", index=False)
pd.set_option("display.width", 230)
print(R.round(4).to_string(index=False))
