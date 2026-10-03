# -*- coding: utf-8 -*-
"""Airport-level analysis menu.

(A) Hub attribution-mismatch table, 2023: top airports by attributed (bunker)
    emissions, with attributed-minus-physical-LTO world-share gap.
(B) Build airport-year panel (emissions x airport GACI x ISO3) for Stata
    within-country regressions -> airport_co2_panel.csv.
(C) Efficiency curve: CO2 per seat-km vs GACI (airport-year binscatter data).
"""
import json
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
HERE = GACI + r"\GACI_CO2"
RAW = HERE + r"\data_from_fangyu\delivery_20260818\airport_month_emissions.csv"

# ---- airport-year emissions ------------------------------------------------
d = pd.read_csv(RAW, dtype={"airport_iata": str, "dom_intl": str,
                            "year": np.int16, "month": np.int8})
d = d[~((d.year == 2024) & (d.month == 7))]

num = ["n_dep_flights", "dep_seats", "dep_seat_km",
       "dep_co2_taxi_out_kg", "dep_co2_takeoff_kg", "dep_co2_climbout_kg",
       "dep_co2_cruise_kg", "arr_co2_approach_kg", "arr_co2_taxi_in_kg"]
intl = (d[d.dom_intl == "International"]
        .groupby(["airport_iata", "year"], as_index=False)
        .agg(intl_seat_km=("dep_seat_km", "sum"),
             intl_cruise=("dep_co2_cruise_kg", "sum")))
a = d.groupby(["airport_iata", "year"], as_index=False)[num].sum()
a = a.merge(intl, on=["airport_iata", "year"], how="left").fillna(
    {"intl_seat_km": 0.0, "intl_cruise": 0.0})
a["co2_lto"] = (a.dep_co2_taxi_out_kg + a.dep_co2_takeoff_kg
                + a.dep_co2_climbout_kg + a.arr_co2_approach_kg
                + a.arr_co2_taxi_in_kg)
a["co2_bunker"] = a.co2_lto + a.dep_co2_cruise_kg
a["intl_share_skm"] = np.where(a.dep_seat_km > 0, a.intl_seat_km / a.dep_seat_km, np.nan)
a["intensity"] = np.where(a.dep_seat_km > 0, a.co2_bunker / a.dep_seat_km, np.nan)

# ---- ISO3 (09-08: shared _iso_map, same as 01) ----------------------------
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _iso_map import build as _build_iso
_to_iso3, _iso_stats = _build_iso()
a["iso3"] = a.airport_iata.map(_to_iso3)
print("airport ISO3 assignment sources:", _iso_stats, "| unassigned airports:", int(a.loc[a.iso3.isna(), "airport_iata"].nunique()))

# ---- merge airport GACI ----------------------------------------------------
g = pd.read_csv(GACI + r"\GACI1996_2024_new_panel_data.csv",
                usecols=["Year", "Airport", "Region", "GACI", "TotalCapacity"])
g = g.rename(columns={"Year": "year", "Airport": "airport_iata"})
m = g.merge(a, on=["airport_iata", "year"], how="left")
print(f"GACI airport-years {len(g):,}; with emissions "
      f"{m.co2_bunker.notna().sum():,} ({100*m.co2_bunker.notna().mean():.2f}%)")

p = m[m.co2_bunker.notna() & (m.year <= 2023)].copy()
p["ln_gaci"] = np.log(p.GACI)
p["ln_co2"] = np.log(p.co2_bunker.clip(lower=1))
p["ln_skm"] = np.where(p.dep_seat_km > 0, np.log(p.dep_seat_km), np.nan)
p["ln_intensity"] = p.ln_co2 - p.ln_skm
cols = ["airport_iata", "year", "iso3", "Region", "GACI", "ln_gaci",
        "co2_bunker", "co2_lto", "ln_co2", "ln_skm", "ln_intensity",
        "intl_share_skm", "n_dep_flights", "dep_seat_km"]
p[cols].to_csv(HERE + r"\airport_co2_panel.csv", index=False)
print(f"wrote airport_co2_panel.csv: {len(p):,} airport-years, "
      f"{p.airport_iata.nunique():,} airports, {p.iso3.nunique()} countries")

# ---- (A) hub mismatch table, 2023 -----------------------------------------
t = p[p.year == 2023].copy()
t["sh_bunker"] = 100 * t.co2_bunker / t.co2_bunker.sum()
t["sh_lto"] = 100 * t.co2_lto / t.co2_lto.sum()
t["gap_pp"] = t.sh_bunker - t.sh_lto
top = t.nlargest(15, "co2_bunker")[
    ["airport_iata", "iso3", "GACI", "co2_bunker", "sh_bunker", "sh_lto",
     "gap_pp", "intl_share_skm", "intensity" if "intensity" in t else "ln_intensity"]]
top["Mt"] = (top.co2_bunker / 1e9).round(1)
print("\n(A) Top-15 airports 2023, attributed (bunker) emissions:")
print(top[["airport_iata", "iso3", "Mt", "sh_bunker", "sh_lto", "gap_pp",
           "intl_share_skm"]].round(2).to_string(index=False))
gp = t.nlargest(10, "gap_pp")[["airport_iata", "iso3", "gap_pp"]]
gn = t.nsmallest(10, "gap_pp")[["airport_iata", "iso3", "gap_pp"]]
print("\nlargest positive attribution gap (pp):",
      [(r.airport_iata, round(r.gap_pp, 2)) for r in gp.itertuples()])
print("largest negative attribution gap (pp):",
      [(r.airport_iata, round(r.gap_pp, 2)) for r in gn.itertuples()])

# ---- (C) efficiency curve data: GACI ventile bins, 2023 --------------------
t2 = t[t.dep_seat_km > 0].copy()
t2["kg_per_1000skm"] = 1000 * t2.co2_bunker / t2.dep_seat_km
q = pd.qcut(t2.ln_gaci, 20, labels=False)
eff = t2.groupby(q).agg(ln_gaci=("ln_gaci", "mean"),
                        kg=("kg_per_1000skm", "median"),
                        intl=("intl_share_skm", "mean"),
                        n=("ln_gaci", "size"))
print("\n(C) CO2 per 1,000 seat-km (median, kg) by GACI ventile, 2023:")
print(eff.round(3).to_string())
eff.to_csv(HERE + r"\_airport_efficiency_bins.csv", index=False)
