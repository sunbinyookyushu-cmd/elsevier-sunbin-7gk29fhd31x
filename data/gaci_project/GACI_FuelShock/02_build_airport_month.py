# -*- coding: utf-8 -*-
"""Airport x month panel (1996-01 to 2024-06) with 1996 and 2019 network positions.

Input : ../GACI_CO2/data_from_fangyu/delivery_20260818/airport_month_emissions.csv (OAG schedules,
        Fangyu delivery 2026-08-18), ../GACI1996_2024_new_panel_data.csv (airport GACI panel),
        ../GACI_CO2/airport_feyrer_panel.csv (airport air market access 1996),
        ../GACI_CO2/gaci_co2_panel.csv (country covariates), data_external/wb_oilrents.json
Output: airport_month.parquet   one row per airport x month, total and dom/intl splits
        airport_base.csv        airport cross-section: 1996/2019 positions and 1996 characteristics

No sample restriction is applied here; restrictions are made (and reported) in the estimation scripts.
"""
import json, os, sys
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
RAW = GACI + r"\GACI_CO2\data_from_fangyu\delivery_20260818\airport_month_emissions.csv"
sys.path.insert(0, GACI + r"\GACI_CO2")
from _iso_map import build as _build_iso

to_iso3, _ = _build_iso()

d = pd.read_csv(RAW, dtype={"airport_iata": str, "dom_intl": str, "year": np.int16, "month": np.int8})
d = d[~((d.year == 2024) & (d.month == 7))]          # 2024-07 covers 1-3 July only
d["co2_dep"] = d.dep_co2_taxi_out_kg + d.dep_co2_takeoff_kg + d.dep_co2_climbout_kg + d.dep_co2_cruise_kg
d["co2_bunker"] = (d.dep_co2_taxi_out_kg + d.dep_co2_takeoff_kg + d.dep_co2_climbout_kg
                   + d.arr_co2_approach_kg + d.arr_co2_taxi_in_kg + d.dep_co2_cruise_kg)
num = ["n_dep_flights", "dep_seats", "dep_seat_km", "co2_dep", "co2_bunker"]
d["intl"] = (d.dom_intl == "International").astype(np.int8)

tot = d.groupby(["airport_iata", "year", "month"], as_index=False)[num].sum()
seg = d.groupby(["airport_iata", "year", "month", "intl"], as_index=False)[["dep_seats", "dep_seat_km", "n_dep_flights"]].sum()
seg = seg.pivot_table(index=["airport_iata", "year", "month"], columns="intl",
                      values=["dep_seats", "dep_seat_km", "n_dep_flights"], fill_value=0)
seg.columns = [f"{a}_{'intl' if b == 1 else 'dom'}" for a, b in seg.columns]
p = tot.merge(seg.reset_index(), on=["airport_iata", "year", "month"], how="left")
for c in [c for c in p.columns if c.endswith(("_intl", "_dom"))]:
    p[c] = p[c].fillna(0)

p["iso3"] = p.airport_iata.map(to_iso3)
p["ym"] = p.year.astype(str) + "-" + p.month.astype(int).map("{:02d}".format)
p["t"] = (p.year - 1996) * 12 + (p.month - 1)                  # 0 = 1996-01

# outcomes
p["ln_seats"] = np.log(p.dep_seats.where(p.dep_seats > 0))
p["ln_flights"] = np.log(p.n_dep_flights.where(p.n_dep_flights > 0))
p["ln_skm"] = np.log(p.dep_seat_km.where(p.dep_seat_km > 0))
p["ln_co2"] = np.log(p.co2_bunker.where(p.co2_bunker > 0))
p["ln_gauge"] = p.ln_seats - p.ln_flights                       # seats per departure
p["ln_stage"] = p.ln_skm - p.ln_seats                           # seat-weighted stage length (km)
p["ln_int"] = np.log(p.co2_dep.where(p.co2_dep > 0)) - p.ln_skm # kg CO2 per seat-km (fuel burn)
p["intl_share"] = p.dep_seats_intl / p.dep_seats.where(p.dep_seats > 0)
p["ln_seats_dom"] = np.log(p.dep_seats_dom.where(p.dep_seats_dom > 0))
p["ln_seats_intl"] = np.log(p.dep_seats_intl.where(p.dep_seats_intl > 0))
p = p.sort_values(["airport_iata", "t"])
p.to_parquet(os.path.join(os.path.dirname(os.path.abspath(__file__)), "airport_month.parquet"), index=False)
print("airport-month rows %s, airports %s, unmatched ISO3 airports %s"
      % (f"{len(p):,}", p.airport_iata.nunique(), p.loc[p.iso3.isna(), "airport_iata"].nunique()))

# ---- airport cross-section ----
g = pd.read_csv(GACI + r"\GACI1996_2024_new_panel_data.csv")
cols = ["GACI", "Degree", "TotalCapacity", "Eigen", "NorClose", "NorBetweenness", "RegionalImportance"]
b96 = g[g.Year == 1996].set_index("Airport")[cols + ["Region"]].add_suffix("_96")
b19 = g[g.Year == 2019].set_index("Airport")[cols].add_suffix("_19")
base = b96.join(b19, how="outer")
base.index.name = "airport_iata"

y96 = p[p.year == 1996].groupby("airport_iata")[["dep_seats", "dep_seat_km", "n_dep_flights", "dep_seats_intl", "co2_dep"]].sum()
y96 = pd.DataFrame({"seats_96": y96.dep_seats, "intl_share_96": y96.dep_seats_intl / y96.dep_seats,
                    "stage_96": y96.dep_seat_km / y96.dep_seats, "gauge_96": y96.dep_seats / y96.n_dep_flights,
                    "int_96": y96.co2_dep / y96.dep_seat_km,
                    "months_96": p[p.year == 1996].groupby("airport_iata").month.nunique()})
y19 = p[p.year == 2019].groupby("airport_iata")[["dep_seats", "dep_seats_intl", "dep_seat_km"]].sum()
y19 = pd.DataFrame({"seats_19": y19.dep_seats, "intl_share_19": y19.dep_seats_intl / y19.dep_seats,
                    "stage_19": y19.dep_seat_km / y19.dep_seats})
# months with positive seats 1996-2019 (balanced-panel flag)
n_pos = p[(p.year <= 2019) & (p.dep_seats > 0)].groupby("airport_iata").t.nunique().rename("n_months_9619")
base = base.join(y96, how="outer").join(y19, how="outer").join(n_pos, how="left")

fe = pd.read_csv(GACI + r"\GACI_CO2\airport_feyrer_panel.csv")
fe = fe[fe.year == 1996].set_index("airport_iata")[["ln_airma96"]]
base = base.join(fe, how="left")
base["iso3"] = base.index.map(to_iso3)

# country covariates, 1996
cp = pd.read_csv(GACI + r"\GACI_CO2\gaci_co2_panel.csv")
c96 = cp[cp.y == 1996].set_index("c")[["lnpc", "lnpop", "reg"]].rename(columns={"lnpc": "lnpc_c96", "lnpop": "lnpop_c96", "reg": "reg_c"})
wb = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_external", "wb_oilrents.json")))[1]
oil = pd.DataFrame([(r["countryiso3code"], int(r["date"]), r["value"]) for r in wb if r["value"] is not None],
                   columns=["c", "y", "oilrent"])
oil96 = oil[(oil.y >= 1996) & (oil.y <= 1998)].groupby("c").oilrent.mean().rename("oilrent_c96")   # 1996-98 mean, fills 1996 gaps
base = base.join(c96, on="iso3").join(oil96, on="iso3")
base.reset_index().to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "airport_base.csv"), index=False)
print("airport_base rows %d; with 1996 GACI %d; with 1996 GACI and 1996 traffic %d; with airMA96 %d"
      % (len(base), base.GACI_96.notna().sum(), (base.GACI_96.notna() & base.seats_96.notna()).sum(),
         (base.GACI_96.notna() & base.ln_airma96.notna()).sum()))
