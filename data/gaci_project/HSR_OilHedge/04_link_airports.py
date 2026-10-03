# -*- coding: utf-8 -*-
"""Airport HSR access dates.

For every airport in the GACI base sample (1996 GACI value, positive 1996 seats) and every radius R in {30, 50, 100} km:
  hsr_date_R   = earliest opening date of a dated high-speed station within R km of the airport
  n_hsr_R      = number of such stations (ever)
Japan: station dates from MLIT N05-20 (Shinkansen service-start year of each station, official) take precedence
over UIC/OSM; the month comes from the UIC 2018 exact date of the same line opening when the years agree.
Output: data/airport_hsr.csv
"""
import math
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree

GACI = r"..\\"
ap = pd.read_csv(GACI + "airport_coords_merged.csv").rename(columns={"Airport": "airport_iata"})
base = pd.read_csv(r"..\GACI_FuelShock\airport_base.csv")
base = base[base.GACI_96.notna() & (base.seats_96 > 0)][["airport_iata", "iso3", "GACI_96", "seats_96"]]
ap = base.merge(ap[["airport_iata", "lat", "lon"]], on="airport_iata", how="left")
print("base airports", len(base), "with coordinates", ap.lat.notna().sum())

st = pd.read_csv("data/hsr_stations_dated.csv", parse_dates=["open_date"])
st = st[st.cc != "JP"].copy()
# Japan: MLIT N05-20 Shinkansen stations (official service-start year)
j = gpd.read_file("data_external/primary/japan_MLIT_N05-20/N05-20_Station2.geojson")
j = j[j.N05_002.astype(str).str.contains("新幹線")].copy()
j["year"] = pd.to_numeric(j.N05_004, errors="coerce")
j = j.to_crs(4326)
j["lat"], j["lon"] = j.geometry.centroid.y, j.geometry.centroid.x
jst = j.groupby("N05_011").agg(lat=("lat", "mean"), lon=("lon", "mean"), year=("year", "min")).reset_index()
uic = pd.read_csv("data/uic_sections.csv", parse_dates=["date"])
ujp = uic[uic.country.str.upper().str.contains("JAPAN") & uic.date.notna()]
month_by_year = ujp.groupby(ujp.date.dt.year).date.min()               # e.g. 2015 -> 2015-03-14
jst["open_date"] = jst.year.map(lambda y: month_by_year.get(y, pd.Timestamp(int(y), 7, 1)) if pd.notna(y) else pd.NaT)
jst["cc"], jst["name"], jst["date_source"] = "JP", jst.N05_011, "MLIT N05-20 (+UIC month)"
st = pd.concat([st, jst[["cc", "name", "lat", "lon", "open_date", "date_source"]]], ignore_index=True)
st = st[st.open_date.notna()]

def xy(lat, lon):
    return np.column_stack([lat * 111.0, lon * 111.0 * np.cos(np.radians(lat))])

tree = cKDTree(xy(st.lat.to_numpy(), st.lon.to_numpy()))
A = ap.dropna(subset=["lat"]).copy()
P = xy(A.lat.to_numpy(), A.lon.to_numpy())
for R in (30, 50, 100):
    idx = tree.query_ball_point(P, r=R)
    A[f"hsr_date_{R}"] = [st.open_date.iloc[i].min() if i else pd.NaT for i in idx]
    A[f"n_hsr_{R}"] = [len(i) for i in idx]
    A[f"hsr_src_{R}"] = [st.date_source.iloc[i].iloc[st.open_date.iloc[i].argmin()] if i else "" for i in idx]
dd, ii = tree.query(P, k=1)
A["km_nearest_hsr"] = dd
A.to_csv("data/airport_hsr.csv", index=False)
for R in (30, 50, 100):
    d = A[f"hsr_date_{R}"]
    print(f"R={R}km: airports with HSR ever {d.notna().sum()}, opened 1997-2019 {((d.dt.year >= 1997) & (d.dt.year <= 2019)).sum()}, "
          f"before 1997 {(d.dt.year < 1997).sum()}")
print(A[A.hsr_date_50.notna()].groupby("iso3").hsr_date_50.agg(["size", "min", "max"]).sort_values("size", ascending=False).head(25).to_string())
