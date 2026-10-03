# -*- coding: utf-8 -*-
"""Merge the country-year CO2 panel with the GACI estimation panel
(gaci_panel_measures.csv: all three connectivity aggregations + tourism IV).
Annual analysis sample = 1996-2023 (2024 is a half year). Outcomes in logs."""
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
HERE = GACI + r"\GACI_CO2"

co2 = pd.read_csv(HERE + r"\co2_country_year.csv")
co2 = co2[co2.year <= 2023].copy()

g = pd.read_csv(GACI + r"\gaci_panel_measures.csv")

m = g.merge(co2, left_on=["c", "y"], right_on=["iso3", "year"], how="left")
print(f"GACI rows {len(g):,}; with CO2 match {m.iso3.notna().sum():,} "
      f"({100*m.iso3.notna().mean():.2f}%)")
miss = m[m.iso3.isna()].groupby("c").size().sort_values(ascending=False)
print("countries with unmatched years:", dict(miss.head(8)))

for v in ["co2_bunker", "co2_lto", "co2_5050", "co2_bunker_intl"]:
    m["ln_" + v] = np.where(m[v] > 0, np.log(m[v]), np.nan)
m["ln_seatkm"] = np.where(m.dep_seat_km > 0, np.log(m.dep_seat_km), np.nan)
m["ln_flights"] = np.where(m.n_dep_flights > 0, np.log(m.n_dep_flights), np.nan)

out = HERE + r"\gaci_co2_panel.csv"
m.drop(columns=["iso3", "year"]).to_csv(out, index=False)
print(f"wrote {out}: {len(m):,} rows, ln_co2_bunker non-missing "
      f"{m.ln_co2_bunker.notna().sum():,}")
