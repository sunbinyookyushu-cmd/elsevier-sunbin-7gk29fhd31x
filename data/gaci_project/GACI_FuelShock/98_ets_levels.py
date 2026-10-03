# -*- coding: utf-8 -*-
"""EU ETS, levels design (user decision 2026-10-02: options A + D).
A: carbon price LEVEL x exposure (as in Fageda & Oesingmann 2025), instrumented by the cumulated Kaenzig carbon policy
   surprise (level of the policy stance) x exposure.
     ln S_it = a_(i x cal.month) + d_t + b_A (P_(t-3) x G_i x Area_i x ETS_t) + b_R (P_(t-3) x Rec_i x (1-Area_i) x ETS_t) + e
     P = EUA monthly mean in EUR 10s; instruments: CumKZ_(t-3) x same exposures (CumKZ = cumulated monthly surprise
     since 2005). Exposures from 96 (geography-predicted, 1996 masses).
   Specs: OLS, IV, IV + region x month FE, IV + exposure-specific linear trends (G x Area x t, Rec x (1-Area) x t),
   placebo 2008-01..2011-12 (aviation outside the ETS; OLS/RF with the same interactions).
D: annual connectivity (hub relocation): ln GACI, ln eigenvector, ln betweenness, 2008-2019, airport FE + year FE
   (or region x year FE); same regressors with annual means; all airports with seats in 2007, and hubs (>= 5 million
   seats in 2007).
SE: country cluster + Newey-West (12 months / 2 years) (_est "dk"); first-stage F under the same variance.
Output: _res_ets_levels.csv
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
e = e.set_index("t").sort_index()
k = pd.read_excel(r"data_external\carbon_policy_shocks\carbonPolicyShocks.xlsx", sheet_name="Monthly")
k["t"] = k.Date.str[:4].astype(int) * 12 + k.Date.str[5:].astype(int)
k = k.set_index("t").sort_index()
f = pd.DataFrame(index=range(2005 * 12 + 1, 2019 * 12 + 13))
f["P"] = e.eua_mean_eur.reindex(f.index) / 10
f["CumKZ"] = k.Surprise.reindex(f.index).fillna(0).cumsum()
f["P_l3"], f["Z_l3"] = f.P.shift(3), f.CumKZ.shift(3)
f["ETS"] = ((f.index - 3) >= 2012 * 12 + 1).astype(int)
f["year"] = (f.index - 1) // 12
fy = f.groupby("year")[["P", "CumKZ"]].mean()
fy["ETS"] = (fy.index >= 2012).astype(int)
x = f.dropna()
print("time series corr(P, CumKZ) 2008-2019:", round(x[["P_l3", "Z_l3"]].corr().iloc[0, 1], 3),
      "| annual:", round(fy.loc[2008:2019][["P", "CumKZ"]].corr().iloc[0, 1], 3), flush=True)

rows = []


def build(d, P, Z, win, G="geo_share_t1"):
    d = d.copy()
    d["xA"], d["xR"] = d[P] * d[G] * d.area * win, d[P] * d.rec_index * (1 - d.area) * win
    d["zA"], d["zR"] = d[Z] * d[G] * d.area * win, d[Z] * d.rec_index * (1 - d.area) * win
    d["trA"], d["trR"] = d[G] * d.area * d.tlin, d.rec_index * (1 - d.area) * d.tlin
    return d


def run(part, spec, d, y, fes, how, L, trend=False):
    s = d.dropna(subset=[y])
    ex = ["trA", "trR"] if trend else []
    if how == "ols":
        o = fit(s, y, exog=["xA", "xR"] + ex, fes=fes, vc=("dk", "iso3", "tt", L), return_fs=False)
        vs, F = ["xA", "xR"], {}
    elif how == "rf":
        o = fit(s, y, exog=["zA", "zR"] + ex, fes=fes, vc=("dk", "iso3", "tt", L), return_fs=False)
        vs, F = ["zA", "zR"], {}
    else:
        o = fit(s, y, endog=["xA", "xR"], instr=["zA", "zR"], exog=ex, fes=fes, vc=("dk", "iso3", "tt", L))
        vs, F = ["xA", "xR"], o["fs"]
    for v in vs:
        rows.append(dict(part=part, spec=spec, outcome=y, term=("area exposure" if v.endswith("A") else "outside, closeness"),
                         b=o["coef"][v], se=o["se"][v], p=o["p"][v], F=F.get(v, {}).get("F", np.nan), n=o["n"],
                         airports=s.airport_iata.nunique()))


# ---------------- A: monthly seats ----------------
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats"]).to_pandas()
am = am[am.iso3.notna() & am.year.between(2008, 2019) & (am.dep_seats > 0)].copy()
k07 = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "year", "dep_seats"]).to_pandas()
k07 = k07[k07.year == 2007].groupby("airport_iata").dep_seats.sum()
am = am[am.airport_iata.isin(k07[k07 > 0].index)]
am["t"] = am.year * 12 + am.month
am["tt"] = am.t
am["ln_s"] = np.log(am.dep_seats)
am = am.merge(geo[["airport_iata", "ets_area", "geo_share_t1", "rec_index"]], on="airport_iata").merge(reg, on="airport_iata", how="left")
am["rec_index"] = am.rec_index.fillna(0)
am["area"] = am.ets_area.astype(int)
am = am.merge(f[["P_l3", "Z_l3", "ETS"]], left_on="t", right_index=True, how="left")
am["tlin"] = (am.t - 2008 * 12) / 12
am["fe_u"] = am.airport_iata + "_" + am.month.astype(str)
am["reg_t"] = am.Region.astype(str) + "_" + am.t.astype(str)
A = build(am[am.t >= 2008 * 12 + 4], "P_l3", "Z_l3", am[am.t >= 2008 * 12 + 4].ETS)
run("A monthly seats", "OLS", A, "ln_s", ["fe_u", "t"], "ols", 12)
run("A monthly seats", "IV", A, "ln_s", ["fe_u", "t"], "iv", 12)
run("A monthly seats", "IV + region x month FE", A, "ln_s", ["fe_u", "reg_t"], "iv", 12)
run("A monthly seats", "IV + exposure trends", A, "ln_s", ["fe_u", "t"], "iv", 12, trend=True)
pre = am[(am.t >= 2008 * 12 + 4) & (am.t <= 2011 * 12 + 12)]
P0 = build(pre, "P_l3", "Z_l3", 1)
run("A monthly seats", "placebo 2008-2011 OLS (aviation not in ETS)", P0, "ln_s", ["fe_u", "t"], "ols", 12)
run("A monthly seats", "placebo 2008-2011 reduced form", P0, "ln_s", ["fe_u", "t"], "rf", 12)
print("A done", flush=True)

# ---------------- D: annual connectivity ----------------
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI", "Eigen", "NorBetweenness", "Region"])
hp = hp[hp.year.between(2008, 2019) & (hp.GACI > 0) & hp.airport_iata.isin(k07[k07 > 0].index)].copy()
hp["ln_gaci"] = np.log(hp.GACI)
hp["ln_eigen"] = np.log(hp.Eigen.where(hp.Eigen > 0))
hp["ln_betw"] = np.log1p(hp.NorBetweenness * 1e4)
hp = hp.merge(geo[["airport_iata", "ets_area", "geo_share_t1", "rec_index"]], on="airport_iata")
hp["rec_index"] = hp.rec_index.fillna(0)
hp["area"] = hp.ets_area.astype(int)
hp = hp.merge(fy.rename(columns={"P": "Py", "CumKZ": "Zy", "ETS": "ETSy"}), left_on="year", right_index=True, how="left")
hp["tt"], hp["tlin"] = hp.year, hp.year - 2008
hp["reg_y"] = hp.Region.astype(str) + "_" + hp.year.astype(str)
hp["hub"] = hp.airport_iata.map(k07).fillna(0) >= 5e6
for samp, H in [("all airports", hp), ("hubs (>= 5m seats 2007)", hp[hp.hub])]:
    Dd = build(H, "Py", "Zy", H.ETSy)
    for y in ["ln_gaci", "ln_eigen", "ln_betw"]:
        run("D annual connectivity", f"{samp} | OLS", Dd, y, ["airport_iata", "year"], "ols", 2)
        run("D annual connectivity", f"{samp} | IV", Dd, y, ["airport_iata", "year"], "iv", 2)
        run("D annual connectivity", f"{samp} | IV + region x year FE", Dd, y, ["airport_iata", "reg_y"], "iv", 2)
        run("D annual connectivity", f"{samp} | IV + exposure trends", Dd, y, ["airport_iata", "year"], "iv", 2, trend=True)
print("D done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_ets_levels.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 300)
print(R.round(4).to_string(index=False))
