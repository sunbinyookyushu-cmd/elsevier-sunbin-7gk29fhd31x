# -*- coding: utf-8 -*-
"""Airport x year hub panel for the aviation-tax / EU ETS hub-relocation design (user 2026-10-02: "한번 해 보자").

hub_panel.csv: airport x year 1996-2024 with GACI and its components (Degree, Eigen, NorClose, NorBetweenness,
  RegionalImportance, TotalCapacity) from GACI1996_2024_new_panel_data.csv, annual departing seats (international /
  domestic) from airport_month_sep08fix.parquet, iso3, coordinates (OurAirports), EEA membership flag.
crossborder_pairs.csv: every pair of airports in different countries within 300 km of each other (great-circle),
  for the cross-border leakage design (passengers driving to a foreign airport to avoid a national ticket tax).
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv").rename(columns={"Airport": "airport_iata", "Year": "year"})
am = pq.read_table("airport_month_sep08fix.parquet",
                   columns=["airport_iata", "iso3", "year", "dep_seats", "dep_seats_intl", "dep_seats_dom", "n_dep_flights"]).to_pandas()
a2c = am.dropna(subset=["iso3"]).drop_duplicates("airport_iata").set_index("airport_iata").iso3
sy = am.groupby(["airport_iata", "year"], as_index=False)[["dep_seats", "dep_seats_intl", "dep_seats_dom", "n_dep_flights"]].sum()
P = g.merge(sy, on=["airport_iata", "year"], how="outer")
P["iso3"] = P.airport_iata.map(a2c)
oa = pd.read_csv(r"data_external\india_atf_vat\sources\ourairports_airports_20261002.csv",
                 usecols=["iata_code", "latitude_deg", "longitude_deg", "type", "iso_country"], keep_default_na=False, na_values=[""])
oa = oa.dropna(subset=["iata_code"])
oa["r"] = oa["type"].map({"large_airport": 0, "medium_airport": 1, "small_airport": 2}).fillna(3)
oa = oa.sort_values("r").drop_duplicates("iata_code").rename(columns={"iata_code": "airport_iata"})
P = P.merge(oa[["airport_iata", "latitude_deg", "longitude_deg"]], on="airport_iata", how="left")
EEA = {"AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU",
       "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE", "ISL", "LIE", "NOR"}
P["eea"] = P.iso3.isin(EEA).astype(int)   # current EEA (EU27 + ISL, LIE, NOR); GBR treated separately (EU ETS until 2020)
P = P.sort_values(["airport_iata", "year"])
P.to_csv("hub_panel.csv", index=False)
print("hub_panel:", P.shape, "airports", P.airport_iata.nunique(), "years", P.year.min(), P.year.max())
print("GACI component columns:", [c for c in g.columns if c not in ("airport_iata", "year")])

# cross-border pairs within 300 km among airports that ever had seats
A = P.dropna(subset=["latitude_deg", "iso3"]).groupby("airport_iata").agg(iso3=("iso3", "first"), lat=("latitude_deg", "first"),
                                                                        lon=("longitude_deg", "first"), seats=("dep_seats", "max"))
A = A[A.seats > 0]
la, lo, ci = np.radians(A.lat.to_numpy()), np.radians(A.lon.to_numpy()), A.iso3.to_numpy()
ids = A.index.to_numpy()
rows = []
for i in range(len(A)):
    d = 2 * 6371 * np.arcsin(np.sqrt(np.sin((la - la[i]) / 2) ** 2 + np.cos(la[i]) * np.cos(la) * np.sin((lo - lo[i]) / 2) ** 2))
    j = np.where((d <= 300) & (ci != ci[i]))[0]
    for k in j:
        rows.append((ids[i], ci[i], ids[k], ci[k], round(float(d[k]), 1)))
C = pd.DataFrame(rows, columns=["airport", "iso3", "neighbour", "neighbour_iso3", "km"])
C.to_csv("crossborder_pairs.csv", index=False)
print("cross-border pairs within 300 km:", len(C), "airports with a foreign neighbour:", C.airport.nunique())
print(C[C.iso3.isin(["NLD", "DEU", "SWE", "NOR", "AUT"])].groupby("iso3").neighbour.nunique().to_string())
