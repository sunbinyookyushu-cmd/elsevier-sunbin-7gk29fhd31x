# -*- coding: utf-8 -*-
"""Build country-year aviation CO2 panel from Fangyu's airport-month delivery.

Steps: drop the partial 2024-07 rows -> map IATA -> ISO3 (ourairports + iso2to3)
-> aggregate to country x year x dom/intl -> build three allocation measures:
  co2_lto     : LTO phases only, each phase at its own airport (territorial)
  co2_bunker  : LTO + cruise assigned to the departure airport (fuel-uplift /
                IEA bunker convention)  <- headline
  co2_5050    : LTO + half of cruise on each side
Cruise appears once on each side in the raw file, so exactly one side (or a
weighted split) is used; never both.
Outputs: co2_country_year.csv (wide, dom/intl and total), validation prints.
"""
import json
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
RAW = GACI + r"\GACI_CO2\data_from_fangyu\delivery_20260818\airport_month_emissions.csv"
OUT = GACI + r"\GACI_CO2\co2_country_year.csv"

# ---- IATA -> ISO3 crosswalk ------------------------------------------------
oa = pd.read_csv(GACI + r"\ourairports.csv",
                 usecols=["type", "iso_country", "iata_code", "scheduled_service"],
                 dtype=str, keep_default_na=False)  # 'NA' = Namibia, not NaN
oa = oa[oa.iata_code.str.len() == 3]
rank = {"large_airport": 0, "medium_airport": 1, "small_airport": 2,
        "seaplane_base": 3, "heliport": 4, "closed": 5, "balloonport": 6}
oa["rk"] = oa["type"].map(rank).fillna(9)
oa = oa.sort_values(["iata_code", "rk"]).drop_duplicates("iata_code")
iata2iso2 = dict(zip(oa.iata_code, oa.iso_country))

iso2to3 = json.load(open(GACI + r"\iso2to3.json"))

# manual patches: closed airports whose IATA was dropped from ourairports
# (Berlin Tegel/Schoenefeld/Tempelhof), metro codes, and known gaps flagged in
# the 08-18 validation (SEL/ISG/KKJ/MLH). Economies without WDI coverage are
# not patched; they are outside the GACI estimation sample, consistent with
# the trade paper.
PATCH = {"TXL": "DEU", "SXF": "DEU", "THF": "DEU", "SEL": "KOR",
         "ISG": "JPN", "KKJ": "JPN", "MLH": "FRA",
         "REP": "KHM", "TSE": "KAZ"}

def to_iso3(iata):
    if iata in PATCH:
        return PATCH[iata]
    iso2 = iata2iso2.get(iata)
    if iso2 is None:
        return None
    return iso2to3.get(iso2)

# ---- load emissions --------------------------------------------------------
num_cols = ["n_dep_flights", "dep_seats", "dep_seat_km",
            "dep_co2_taxi_out_kg", "dep_co2_takeoff_kg", "dep_co2_climbout_kg",
            "dep_co2_cruise_kg",
            "n_arr_flights", "arr_seats", "arr_seat_km",
            "arr_co2_approach_kg", "arr_co2_taxi_in_kg", "arr_co2_cruise_kg"]
d = pd.read_csv(RAW, dtype={"airport_iata": str, "dom_intl": str,
                            "year": np.int16, "month": np.int8})
n0 = len(d)

# drop the partial 2024-07 rows (Fangyu: July 2024 covers 1-3 July only)
bad = (d.year == 2024) & (d.month == 7)
print(f"rows total {n0:,}; dropping 2024-07 partial rows: {bad.sum():,}")
d = d[~bad].copy()

# ---- map to countries ------------------------------------------------------
d["iso3"] = d.airport_iata.map(to_iso3)
tot_co2 = d.dep_co2_taxi_out_kg + d.dep_co2_takeoff_kg + d.dep_co2_climbout_kg + d.dep_co2_cruise_kg
matched = d.iso3.notna()
print(f"airport codes: {d.airport_iata.nunique():,}; matched to ISO3: "
      f"{d.loc[matched, 'airport_iata'].nunique():,}")
print(f"unmatched share of rows {100*(1-matched.mean()):.2f}% | of dep flights "
      f"{100*d.loc[~matched,'n_dep_flights'].sum()/d.n_dep_flights.sum():.2f}% | of dep CO2 "
      f"{100*tot_co2[~matched].sum()/tot_co2.sum():.2f}%")
top_un = (d.loc[~matched].groupby("airport_iata")["n_dep_flights"].sum()
          .sort_values(ascending=False).head(12))
print("largest unmatched codes by flights:", dict(top_un))
d = d[matched].copy()

# ---- aggregate: country x year x dom/intl ----------------------------------
g = d.groupby(["iso3", "year", "dom_intl"], as_index=False)[num_cols].sum()

# allocation measures (kg)
g["co2_lto"] = (g.dep_co2_taxi_out_kg + g.dep_co2_takeoff_kg + g.dep_co2_climbout_kg
                + g.arr_co2_approach_kg + g.arr_co2_taxi_in_kg)
g["co2_bunker"] = g.co2_lto + g.dep_co2_cruise_kg
g["co2_5050"] = g.co2_lto + 0.5 * (g.dep_co2_cruise_kg + g.arr_co2_cruise_kg)

keep = ["n_dep_flights", "dep_seats", "dep_seat_km", "n_arr_flights",
        "dep_co2_cruise_kg", "arr_co2_cruise_kg",
        "co2_lto", "co2_bunker", "co2_5050"]

# wide: total + international-only
tot = g.groupby(["iso3", "year"], as_index=False)[keep].sum()
intl = (g[g.dom_intl == "International"]
        .groupby(["iso3", "year"], as_index=False)[keep].sum()
        .rename(columns={k: k + "_intl" for k in keep}))
w = tot.merge(intl, on=["iso3", "year"], how="left")
for k in keep:
    w[k + "_intl"] = w[k + "_intl"].fillna(0.0)
w.to_csv(OUT, index=False)
print(f"wrote {OUT}: {len(w):,} country-years, {w.iso3.nunique()} countries, "
      f"{w.year.min()}-{w.year.max()}")

# ---- validation ------------------------------------------------------------
gl = w.groupby("year")[["co2_lto", "co2_bunker", "co2_5050"]].sum() / 1e12  # Gt
print("\nGlobal totals (Gt CO2):")
print(gl.loc[[1996, 2000, 2005, 2010, 2015, 2019, 2020, 2023]].round(3))
print(f"\n2019 bunker total {gl.loc[2019,'co2_bunker']:.3f} Gt "
      f"(ICCT benchmark ~0.92 Gt commercial aviation)")
print(f"2019 LTO share {100*gl.loc[2019,'co2_lto']/gl.loc[2019,'co2_bunker']:.1f}%")
chk = w[["dep_co2_cruise_kg", "arr_co2_cruise_kg"]].sum()
print(f"global dep-cruise / arr-cruise ratio {chk[0]/chk[1]:.6f} (should be ~1)")
t19 = w[w.year == 2019].nlargest(10, "co2_bunker")[["iso3", "co2_bunker"]]
t19["Mt"] = (t19.co2_bunker / 1e9).round(1)
print("\nTop-10 countries 2019, bunker (Mt):")
print(t19[["iso3", "Mt"]].to_string(index=False))
