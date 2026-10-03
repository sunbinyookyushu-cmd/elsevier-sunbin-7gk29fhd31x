# -*- coding: utf-8 -*-
"""Validation of the dated high-speed network.

1. Route length in operation by country and year from the dated OSM ways (way km / number of parallel tracks,
   approximated by halving double-tracked ways that come in pairs) against UIC section totals (sum of km of UIC
   sections opened by that year).
2. UIC sections that could not be matched to OSM (station names or path), by country.
3. Agreement between UIC-path dates and OSM start_date on the same ways (years).
Output: data/validation_km_by_year.csv, data/validation_unmatched.csv, data/validation_date_agreement.csv
"""
import numpy as np
import pandas as pd

W = pd.read_parquet("data/hsr_ways_dated.parquet")
U = pd.read_csv("data/uic_sections.csv", parse_dates=["date"])
U = U[U.status == "In operation"]
L = pd.read_csv("data/uic_match_log.csv", parse_dates=["date"])
CC = {"JP": "JAPAN", "KR": "SOUTH KOREA", "TW": "TAIWAN", "ES": "SPAIN", "FR": "FRANCE", "DE": "GERMANY", "IT": "ITALY",
      "TR": "TURKEY", "GB": "UNITED KINGDOM|UK", "BE": "BELGIUM", "NL": "NETHERLANDS", "AT": "AUSTRIA", "CH": "SWITZERLAND",
      "SE": "SWEDEN", "FI": "FINLAND", "DK": "DENMARK", "PL": "POLAND", "SA": "SAUDI", "MA": "MOROCCO", "RS": "SERBIA",
      "US": "USA", "CN": "CHINA"}
W = W[W.railway == "rail"].copy()
W["yr"] = pd.to_datetime(W.open_date).dt.year
rows = []
for cc, pat in CC.items():
    u = U[U.country.str.upper().str.contains(pat, regex=True)]
    # latest edition for totals (2022 when present, else 2018)
    ed = "2022" if (u.edition.astype(str) == "2022").any() else "2018"
    u = u[u.edition.astype(str) == ed]
    w = W[W.cc == cc]
    tot_way_km = w.km.sum()
    for y in range(1995, 2024):
        rows.append(dict(cc=cc, year=y, uic_km=u.loc[u.year <= y, "km"].sum(),
                         osm_dated_way_km=w.loc[w.yr <= y, "km"].sum(), osm_total_way_km=tot_way_km,
                         osm_undated_way_km=w.loc[w.yr.isna(), "km"].sum()))
V = pd.DataFrame(rows)
V["osm_route_km_approx"] = V.osm_dated_way_km / 2          # most HSR is double track mapped as two ways
V["ratio_osm_to_uic"] = V.osm_route_km_approx / V.uic_km.replace(0, np.nan)
V.to_csv("data/validation_km_by_year.csv", index=False)
un = L[~L.ok].copy()
un.to_csv("data/validation_unmatched.csv", index=False)
both = W[W.uic_date.notna() & W.osm_year_ok.notna()].copy()
both["diff"] = pd.to_datetime(both.uic_date).dt.year - both.osm_year_ok
agr = both.groupby("cc").apply(lambda g: pd.Series({"ways_both": len(g), "same_year_share": (g["diff"].abs() == 0).mean(),
                                                     "within_1y_share": (g["diff"].abs() <= 1).mean(),
                                                     "km_both": g.km.sum()})).reset_index()
agr.to_csv("data/validation_date_agreement.csv", index=False)
pd.set_option("display.width", 220)
print(V[V.year.isin([2000, 2005, 2010, 2015, 2019, 2023])].pivot_table(index="cc", columns="year", values="ratio_osm_to_uic").round(2).to_string())
print("\nUIC sections not fully matched:", len(un), "of", len(L))
print(un.groupby("cc").size().to_string())
print("\nUIC vs OSM date agreement on the same ways:")
print(agr.round(3).to_string(index=False))
