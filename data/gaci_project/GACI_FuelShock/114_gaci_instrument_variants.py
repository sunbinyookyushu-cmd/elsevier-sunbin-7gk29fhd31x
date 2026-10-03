# -*- coding: utf-8 -*-
"""Strengthen the connectivity instrument (user 2026-10-03): variants of the leave-own-country-out geography x foreign
network growth instrument, first-stage F for ln GACI and ln destinations on the mediation stacks (112), then the
two-instrument mediation with the strongest variant.
Variants (all exclude airports of the same country; d_ij >= 50 km; 1996 masses S_j):
  v1  ln sum S_j g_jt / d_ij                    (113 baseline)
  v2  ln sum S_j g_jt / d_ij^2                   (steeper decay)
  v3  ln sum_{d<=1000km} S_j g_jt / d_ij          (ring 1,000 km)
  v4  ln sum_{d<=2500km} S_j g_jt / d_ij          (ring 2,500 km, Europe-wide)
  v5  sum S_j GACI_jt / d_ij / sum S_j / d_ij     (proximity-weighted mean foreign GACI, level)
  v6  sum S_j Degree_jt / d_ij / sum S_j / d_ij   (proximity-weighted mean foreign destinations)
  v7  v1 excluding also the border group's countries of the stack... approximated by excluding all countries within
      300 km of airport i (neighbour countries), to separate from cross-border demand
Output: _res_gaci_instrument_variants.csv (first stages and mediation with the best variant)
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
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "dep_seats", "GACI", "Degree", "latitude_deg", "longitude_deg"])
hp = hp[hp.year.between(1996, 2019)]
A = hp.groupby("airport_iata").agg(iso3=("iso3", "first"), lat=("latitude_deg", "first"), lon=("longitude_deg", "first")).dropna()
W = hp.pivot_table(index="airport_iata", columns="year", values="dep_seats").reindex(A.index)
GA = hp.pivot_table(index="airport_iata", columns="year", values="GACI").reindex(A.index)
DG = hp.pivot_table(index="airport_iata", columns="year", values="Degree").reindex(A.index)
m = A[(W[1996].fillna(0) > 0)].index
Gm = (W.loc[m].div(W.loc[m, 1996], axis=0)).fillna(0).clip(upper=20).to_numpy(np.float32)
GAm, DGm = GA.loc[m].fillna(0).to_numpy(np.float32), DG.loc[m].fillna(0).to_numpy(np.float32)
S = W.loc[m, 1996].to_numpy(np.float32)
la, lo = np.radians(A.lat.to_numpy()), np.radians(A.lon.to_numpy())
lm, om = np.radians(A.loc[m].lat.to_numpy()), np.radians(A.loc[m].lon.to_numpy())
ci, cm = A.iso3.to_numpy(), A.loc[m].iso3.to_numpy()
# neighbour countries within 300 km of each airport (for v7)
Y = pd.read_stata("stata_tax/tax_mediation.dta").rename(columns={"airport": "airport_iata"})
need = set(Y.airport_iata)
idx = [i for i, a in enumerate(A.index) if a in need]
V = {k: np.full((len(idx), Gm.shape[1]), np.nan, np.float32) for k in ["v1", "v2", "v3", "v4", "v5", "v6", "v7"]}
for r, i in enumerate(idx):
    d = 2 * 6371 * np.arcsin(np.sqrt(np.sin((lm - la[i]) / 2) ** 2 + np.cos(la[i]) * np.cos(lm) * np.sin((om - lo[i]) / 2) ** 2))
    dd = np.maximum(d, 50.0)
    own = cm == ci[i]
    w1 = np.where(own, 0, S / dd); w2 = np.where(own, 0, S / dd ** 2)
    w3 = np.where(own | (d > 1000), 0, S / dd); w4 = np.where(own | (d > 2500), 0, S / dd)
    nbc = set(cm[(d <= 300) & ~own]); w7 = np.where(own | np.isin(cm, list(nbc)), 0, S / dd)
    V["v1"][r] = np.log(w1 @ Gm + 1e-9); V["v2"][r] = np.log(w2 @ Gm + 1e-9)
    V["v3"][r] = np.log(w3 @ Gm + 1e-9) if w3.sum() > 0 else np.nan; V["v4"][r] = np.log(w4 @ Gm + 1e-9) if w4.sum() > 0 else np.nan
    V["v5"][r] = (w1 @ GAm) / w1.sum(); V["v6"][r] = np.log((w1 @ DGm) / w1.sum() + 1e-9); V["v7"][r] = np.log(w7 @ Gm + 1e-9) if w7.sum() > 0 else np.nan
Z = pd.concat([pd.DataFrame(V[k], index=A.index[idx], columns=W.columns).stack().rename(k) for k in V], axis=1).reset_index()
Z.columns = ["airport_iata", "year"] + list(V)
Y = Y.merge(Z, on=["airport_iata", "year"], how="left")
Y["fe_u"], Y["fe_t"] = Y.fe_u.astype(int).astype(str), Y.fe_t.astype(int).astype(str)
rows = []
for k in V:
    d = Y.dropna(subset=[k, "ln_gaci", "ln_deg", "ln_co2"])
    for M in ["ln_gaci", "ln_deg"]:
        o = fit(d, "ln_co2", endog=[M], instr=[k], exog=["tp", "bp"], fes=["fe_u", "fe_t"], vc=("cl", "iso3"))
        rows.append(dict(variant=k, mediator=M, KP_F=o["fs"][M]["F"], pi_first=o["fs"][M]["pi"][k], b_M=o["coef"][M], se_M=o["se"][M],
                         direct_tp=o["coef"]["tp"], se_tp=o["se"]["tp"], n=o["n"]))
    print(k, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_gaci_instrument_variants.csv", index=False)
pd.set_option("display.width", 200)
print(R.round(4).to_string(index=False))
