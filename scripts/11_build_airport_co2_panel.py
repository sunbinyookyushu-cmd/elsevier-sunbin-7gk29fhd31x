"""Airport-year CO2 panel: merge bottom-up schedule emissions (data/raw/external/airport_year_emissions.csv,
aggregated from airport-month, departures-based to avoid double counting cruise) with the GACI panel + country.
Output: data/processed/airport_panel_co2.csv  (one row per airport-year)
  co2_t        departure CO2, all phases, tonnes (dom + intl)
  co2_dom_t / co2_intl_t
  co2_lto_t    taxi-out + take-off + climb-out (airport-local emissions) ; co2_cruise_t
  seats_dep, flights_dep, seat_km, stage_km (= seat_km/seats), co2_per_seat_kg, co2_per_skm_g, n_months (max over dom/intl)
"""
import pandas as pd, numpy as np, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
e = pd.read_csv(root/"data/raw/external/airport_year_emissions.csv")
e["co2_lto_kg"] = e.dep_co2_taxi_out_kg + e.dep_co2_takeoff_kg + e.dep_co2_climbout_kg
w = e.pivot_table(index=["airport_iata","year"], columns="dom_intl",
                  values=["dep_co2_t","dep_seats","dep_seat_km","n_dep_flights","co2_lto_kg","dep_co2_cruise_kg","n_months"], aggfunc="sum")
w.columns = [f"{a}_{b}" for a,b in w.columns]; w = w.reset_index().fillna(0)
out = pd.DataFrame({"Airport": w.airport_iata, "Year": w.year,
    "co2_t": w.dep_co2_t_Domestic + w.dep_co2_t_International,
    "co2_dom_t": w.dep_co2_t_Domestic, "co2_intl_t": w.dep_co2_t_International,
    "co2_lto_t": (w.co2_lto_kg_Domestic + w.co2_lto_kg_International)/1000,
    "co2_cruise_t": (w.dep_co2_cruise_kg_Domestic + w.dep_co2_cruise_kg_International)/1000,
    "seats_dep": w.dep_seats_Domestic + w.dep_seats_International,
    "seats_intl_dep": w.dep_seats_International,
    "flights_dep": w.n_dep_flights_Domestic + w.n_dep_flights_International,
    "seat_km": w.dep_seat_km_Domestic + w.dep_seat_km_International,
    "n_months": w[["n_months_Domestic","n_months_International"]].max(axis=1)})
out["stage_km"] = out.seat_km/out.seats_dep.replace(0,np.nan)
out["co2_per_seat_kg"] = out.co2_t*1000/out.seats_dep.replace(0,np.nan)
out["co2_per_skm_g"] = out.co2_t*1e6/out.seat_km.replace(0,np.nan)
g = pd.read_csv(root/"data/processed/gaci_with_country.csv")
p = g.merge(out, on=["Airport","Year"], how="left")
p.to_csv(root/"data/processed/airport_panel_co2.csv", index=False)
print("GACI airport-years:", len(p), "| with CO2:", p.co2_t.notna().sum(), f"({p.co2_t.notna().mean():.1%})")
print("months covered per year (median):", out.groupby("Year").n_months.median().loc[[1996,2010,2019,2023,2024]].to_dict())
print("TotalCapacity / seats_dep median by year:", (p.TotalCapacity/p.seats_dep).groupby(p.Year).median().loc[[1996,2010,2019,2024]].round(3).to_dict())
print(p[p.Year==2019].nlargest(8,"co2_t")[["Airport","iso_country","co2_t","seats_dep","stage_km","co2_per_seat_kg","GACI"]].round(1).to_string(index=False))
