# -*- coding: utf-8 -*-
"""Feyrer-style geography-predicted EU ETS exposure for every airport (user decision 2026-10-02: 4.1 = continuous
treatment instrumented by geography x Kaenzig carbon policy surprises; no route data needed).

Actual exposure (share of an airport's seats on ETS-covered routes) responds to the ETS itself, so it is predicted from
geography and pre-determined masses only:
  geo_share_i(theta) = sum_{j in ETS area, j != i} S_j d_ij^-theta / sum_{j != i} S_j d_ij^-theta
  S_j = departing seats of airport j in 1996 (pre-determined, 16 years before the 2012 inclusion);
  d_ij great-circle km (floor 50 km); theta = 1 (main) and 2.
ETS aviation scope 2013-2023 = flights between airports inside the area (intra-EEA, Reg. 421/2014 and 2017/2392):
  EU member states + Iceland, Norway, Liechtenstein; UK inside until 2020; Croatia from 2014 (EU accession 2013).
  For airports outside the area, covered seats are ~0 after 2013, so exposure enters only for area airports;
  a second index measures how close a NON-area airport is to the area's mass (candidate receivers of hub traffic,
  e.g. IST, Gulf hubs):  rec_i = sum_{j in area} S_j d_ij^-1 / sum_j S_j d_ij^-1 for i outside the area.
Also: geo_skm_i = mean great-circle distance to area destinations weighted by S_j d_ij^-1 (fuel per covered seat
  rises with distance, so carbon cost per covered seat scales with it).
Output: geo_ets_exposure.csv (airport, iso3, ets_area, geo_share_t1, geo_share_t2, geo_skm, rec_index, seats_1996)
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd

hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "dep_seats", "latitude_deg", "longitude_deg"])
a = hp.groupby("airport_iata").agg(iso3=("iso3", "first"), lat=("latitude_deg", "first"), lon=("longitude_deg", "first")).dropna()
s96 = hp[hp.year == 1996].set_index("airport_iata").dep_seats
a["seats_1996"] = a.index.map(s96).fillna(0)
AREA = {"AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU",
        "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE", "ISL", "LIE", "NOR", "GBR"}
a["ets_area"] = a.iso3.isin(AREA).astype(int)
m = a[a.seats_1996 > 0]                                     # masses
la, lo = np.radians(a.lat.to_numpy()), np.radians(a.lon.to_numpy())
lm, om = np.radians(m.lat.to_numpy()), np.radians(m.lon.to_numpy())
S = m.seats_1996.to_numpy()
inA = m.ets_area.to_numpy() == 1
ids_m = m.index.to_numpy()
res = {k: np.full(len(a), np.nan) for k in ["geo_share_t1", "geo_share_t2", "geo_skm", "rec_index"]}
for i, ap in enumerate(a.index):
    d = 2 * 6371 * np.arcsin(np.sqrt(np.sin((lm - la[i]) / 2) ** 2 + np.cos(la[i]) * np.cos(lm) * np.sin((om - lo[i]) / 2) ** 2))
    d = np.maximum(d, 50.0)
    w1 = S / d
    w1[ids_m == ap] = 0
    w2 = S / d ** 2
    w2[ids_m == ap] = 0
    res["geo_share_t1"][i] = w1[inA].sum() / w1.sum()
    res["geo_share_t2"][i] = w2[inA].sum() / w2.sum()
    res["geo_skm"][i] = (w1[inA] * d[inA]).sum() / w1[inA].sum()
    res["rec_index"][i] = res["geo_share_t1"][i]
for k, v in res.items():
    a[k] = v
a.loc[a.ets_area == 1, "rec_index"] = np.nan                # receivers index only for airports outside the area
a.index.name = "airport_iata"
a.reset_index().to_csv("geo_ets_exposure.csv", index=False)
pd.set_option("display.width", 200)
print(a.groupby("ets_area")[["geo_share_t1", "geo_share_t2", "geo_skm"]].describe().T.round(3).to_string())
show = ["FRA", "CDG", "AMS", "LHR", "MUC", "FCO", "MAD", "HEL", "IST", "DXB", "DOH", "AUH", "SVO", "ZRH", "JFK", "SIN"]
print(a.loc[[x for x in show if x in a.index], ["iso3", "ets_area", "geo_share_t1", "geo_share_t2", "geo_skm", "rec_index"]].round(3).to_string())
