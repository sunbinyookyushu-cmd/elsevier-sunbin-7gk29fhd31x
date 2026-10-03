# -*- coding: utf-8 -*-
"""Feyrer-style instrument for an airport's connectivity (user 2026-10-03): geography x FOREIGN network growth,
leave-own-country-out, so it is unrelated to the taxing country's own policy and demand.
  Z_it = ln sum_{j: country(j) != country(i)} [ S_j(1996) x (seats_jt / seats_j1996) ] / d_ij      (d_ij >= 50 km)
       = log of the proximity-weighted size of the foreign network reachable from i, driven only by foreign growth.
Then, on the annual tax stacks of 112 (8 European events, years E-3..E, airport x event + year x event FE):
  first stage      ln GACI_it on Z_it (+ tp, bp)
  2SLS (two tools) ln CO2 = b_T tp + b_M ln GACI + bp,  ln GACI instrumented by Z  -> direct b_T, indirect pi x b_M
  over-identified   ln GACI instrumented by Z and tp (exclusion for tp testable by Hansen J)
  plus the same for ln destinations as mediator and ln CO2/seat-km as outcome.
SE country cluster (_est "cl"). Output: gaci_instrument.csv, _res_gaci_instrument.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import warnings

import numpy as np
import pandas as pd
from _est import fit

warnings.filterwarnings("ignore")
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "dep_seats", "latitude_deg", "longitude_deg"])
hp = hp[hp.year.between(1996, 2019)]
A = hp.groupby("airport_iata").agg(iso3=("iso3", "first"), lat=("latitude_deg", "first"), lon=("longitude_deg", "first")).dropna()
W = hp.pivot_table(index="airport_iata", columns="year", values="dep_seats").reindex(A.index)
m = A[(W[1996].fillna(0) > 0)].index                     # masses: airports with 1996 seats
Gm = (W.loc[m].div(W.loc[m, 1996], axis=0)).fillna(0).clip(upper=20).to_numpy(np.float32)   # growth factor, capped at 20x
S = W.loc[m, 1996].to_numpy(np.float32)
la, lo = np.radians(A.lat.to_numpy()), np.radians(A.lon.to_numpy())
lm, om = np.radians(A.loc[m].lat.to_numpy()), np.radians(A.loc[m].lon.to_numpy())
ci, cm = A.iso3.to_numpy(), A.loc[m].iso3.to_numpy()
Z = np.empty((len(A), Gm.shape[1]), np.float32)
for i in range(len(A)):
    d = 2 * 6371 * np.arcsin(np.sqrt(np.sin((lm - la[i]) / 2) ** 2 + np.cos(la[i]) * np.cos(lm) * np.sin((om - lo[i]) / 2) ** 2))
    w = S / np.maximum(d, 50.0)
    w[cm == ci[i]] = 0.0
    Z[i] = np.log(w @ Gm + 1e-9)
Zdf = pd.DataFrame(Z, index=A.index, columns=W.columns).stack().rename("z_geo").reset_index().rename(columns={"level_1": "year"})
Zdf.columns = ["airport_iata", "year", "z_geo"]
Zdf.to_csv("gaci_instrument.csv", index=False)
print("instrument built:", Zdf.shape, flush=True)

Y = pd.read_stata("stata_tax/tax_mediation.dta")
Y = Y.rename(columns={"airport": "airport_iata"}).merge(Zdf, on=["airport_iata", "year"], how="left")
Y["fe_u"], Y["fe_t"] = Y.fe_u.astype(int).astype(str), Y.fe_t.astype(int).astype(str)
rows = []


def add(part, spec, o, terms, F=None):
    for v, lab in terms:
        rows.append(dict(part=part, spec=spec, term=lab, b=o["coef"][v], se=o["se"][v], p=o["p"][v], F=(o["fs"].get(v, {}).get("F") if o.get("fs") else None),
                         n=o["n"], note=F))


d = Y.dropna(subset=["z_geo", "ln_gaci", "ln_co2"])
for M, lab in [("ln_gaci", "GACI"), ("ln_deg", "destinations")]:
    o = fit(d, M, exog=["z_geo", "tp", "bp"], fes=["fe_u", "fe_t"], vc=("cl", "iso3"), return_fs=False)
    add("first stage", f"M = {lab}", o, [("z_geo", "Z geo x foreign growth"), ("tp", "treated x post")])
    pi = o["coef"]["tp"]
    for yv, ylab in [("ln_co2", "CO2"), ("ln_int", "CO2 per seat-km")]:
        o2 = fit(d, yv, endog=[M], instr=["z_geo"], exog=["tp", "bp"], fes=["fe_u", "fe_t"], vc=("cl", "iso3"))
        add("2SLS, M instrumented by Z, tp exogenous", f"Y = {ylab}, M = {lab}", o2, [(M, f"ln {lab} (b_M)"), ("tp", "treated x post (direct)")],
            F=f"KP F {o2['fs'][M]['F']:.1f}; indirect = pi x b_M = {pi * o2['coef'][M]:.4f}")
        o3 = fit(d, yv, endog=[M], instr=["z_geo", "tp"], exog=["bp"], fes=["fe_u", "fe_t"], vc=("cl", "iso3"))
        add("2SLS, M instrumented by Z and tp (over-identified)", f"Y = {ylab}, M = {lab}", o3, [(M, f"ln {lab} (b_M)")], F=f"KP F {o3['fs'][M]['F']:.1f}")
    print(lab, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_gaci_instrument.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_colwidth", 70)
print(R.round(4).to_string(index=False))
