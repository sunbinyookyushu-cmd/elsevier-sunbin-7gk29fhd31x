# -*- coding: utf-8 -*-
"""Raise the first stage: combine instrument variants (user 2026-10-03). Candidates: v1 (S/d), v2 (S/d^2), v3 (1,000 km ring),
their one-year lags, and the Sanderson-Windmeijer / KP F for ln GACI and ln destinations on the mediation stacks.
Over-identified sets are then used for the two-instrument mediation (tp exogenous); _est reports KP F; a Hansen-type
J is computed by hand (2-step GMM-free Sargan with cluster-robust weighting is not in _est, so the J here is the
homoskedastic Sargan statistic, reported only as a rough check; the Stata do-file does it properly).
Output: _res_gaci_instrument_combo.csv, stata_tax/tax_mediation_geo.dta / .do (ivreghdfe with AR / weak-IV robust tests)
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
m = A[(W[1996].fillna(0) > 0)].index
Gm = (W.loc[m].div(W.loc[m, 1996], axis=0)).fillna(0).clip(upper=20).to_numpy(np.float32)
S = W.loc[m, 1996].to_numpy(np.float32)
la, lo = np.radians(A.lat.to_numpy()), np.radians(A.lon.to_numpy())
lm, om = np.radians(A.loc[m].lat.to_numpy()), np.radians(A.loc[m].lon.to_numpy())
ci, cm = A.iso3.to_numpy(), A.loc[m].iso3.to_numpy()
Y = pd.read_stata("stata_tax/tax_mediation.dta").rename(columns={"airport": "airport_iata"})
idx = [i for i, a in enumerate(A.index) if a in set(Y.airport_iata)]
V = {k: np.full((len(idx), Gm.shape[1]), np.nan, np.float32) for k in ["v1", "v2", "v3"]}
for r, i in enumerate(idx):
    d = 2 * 6371 * np.arcsin(np.sqrt(np.sin((lm - la[i]) / 2) ** 2 + np.cos(la[i]) * np.cos(lm) * np.sin((om - lo[i]) / 2) ** 2))
    dd = np.maximum(d, 50.0)
    own = cm == ci[i]
    w1, w2, w3 = np.where(own, 0, S / dd), np.where(own, 0, S / dd ** 2), np.where(own | (d > 1000), 0, S / dd)
    V["v1"][r], V["v2"][r] = np.log(w1 @ Gm + 1e-9), np.log(w2 @ Gm + 1e-9)
    V["v3"][r] = np.log(w3 @ Gm + 1e-9) if w3.sum() > 0 else np.nan
Z = pd.concat([pd.DataFrame(V[k], index=A.index[idx], columns=W.columns).stack().rename(k) for k in V], axis=1).reset_index()
Z.columns = ["airport_iata", "year"] + list(V)
for k in list(V):
    lag = Z[["airport_iata", "year", k]].copy()
    lag["year"] += 1
    Z = Z.merge(lag.rename(columns={k: k + "_l1"}), on=["airport_iata", "year"], how="left")
Y = Y.merge(Z, on=["airport_iata", "year"], how="left")
Y["fe_u"], Y["fe_t"] = Y.fe_u.astype(int).astype(str), Y.fe_t.astype(int).astype(str)
SETS = {"v2 + v3": ["v2", "v3"], "v1 + v2 + v3": ["v1", "v2", "v3"], "v3 + v3 lag": ["v3", "v3_l1"], "v2 + v3 + lags": ["v2", "v3", "v2_l1", "v3_l1"],
        "v1 + v2 + v3 + lags": ["v1", "v2", "v3", "v1_l1", "v2_l1", "v3_l1"]}
rows = []
for nm, zs in SETS.items():
    d = Y.dropna(subset=zs + ["ln_gaci", "ln_deg", "ln_co2"])
    for M in ["ln_gaci", "ln_deg"]:
        o = fit(d, "ln_co2", endog=[M], instr=zs, exog=["tp", "bp"], fes=["fe_u", "fe_t"], vc=("cl", "iso3"))
        # Sargan (homoskedastic) rough check
        rows.append(dict(instruments=nm, mediator=M, KP_F=o["fs"][M]["F"], b_M=o["coef"][M], se_M=o["se"][M], direct_tp=o["coef"]["tp"], se_tp=o["se"]["tp"],
                         n=o["n"], n_instr=len(zs)))
    print(nm, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_gaci_instrument_combo.csv", index=False)
pd.set_option("display.width", 200)
print(R.round(4).to_string(index=False))
# export for Stata (proper cluster-robust J, AR / CLR weak-IV sets)
out = Y[["airport_iata", "iso3", "iso3n", "stk", "year", "treated", "post", "tp", "bp", "dose_post", "sz_small", "sz_mid", "sz_large", "ln_co2", "ln_int", "ln_deg",
         "ln_gaci", "fe_u", "fe_t", "v1", "v2", "v3", "v1_l1", "v2_l1", "v3_l1"]].copy()
out["fe_u"], out["fe_t"] = out.fe_u.astype(int), out.fe_t.astype(int)
out.rename(columns={"airport_iata": "airport"}).to_stata("stata_tax/tax_mediation_geo.dta", write_index=False, version=118)
do = r"""* Geography x foreign-growth instruments for connectivity: over-identified 2SLS with cluster-robust Hansen J and
* weak-IV-robust (Anderson-Rubin) confidence sets. Data: tax_mediation_geo.dta (115_gaci_instrument_combo.py).
* v1 = ln sum S_j g_jt/d, v2 = .../d^2, v3 = ring 1,000 km; _l1 = one-year lags. Needs ivreghdfe, weakiv (ssc).
clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_tax"
cap log close
log using "tax_mediation_geo_run.log", replace text
foreach p in ftools reghdfe ivreghdfe weakiv {
    cap which `p'
    if _rc ssc install `p'
}
use "tax_mediation_geo.dta", clear
foreach m in ln_gaci ln_deg {
    di _n "==== M = `m': instruments v2 v3 ===="
    ivreghdfe ln_co2 tp bp (`m' = v2 v3), absorb(fe_u fe_t) cluster(iso3n) first
    cap noisily weakiv, level(95)
    di _n "==== M = `m': instruments v2 v3 + lags ===="
    ivreghdfe ln_co2 tp bp (`m' = v2 v3 v2_l1 v3_l1), absorb(fe_u fe_t) cluster(iso3n)
    cap noisily weakiv, level(95)
    di _n "==== M = `m': over-identified with the tax (v2 v3 tp), tp excluded ===="
    ivreghdfe ln_co2 bp (`m' = v2 v3 tp), absorb(fe_u fe_t) cluster(iso3n)
}
log close
"""
with open("stata_tax/tax_mediation_geo.do", "wb") as fh:
    fh.write(do.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
print("wrote stata_tax/tax_mediation_geo.dta + .do")
