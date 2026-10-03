"""Country-year outcome panel for the ASA analysis (runs on data already in the repo).
Sources: data/raw/external/airport_year_emissions.csv (dom/intl departures, seats, seat-km, CO2 by phase),
         data/processed/gaci_with_country.csv (airport GACI + components), airport_country_map (ISO2).
Output : data/gaci_project/GACI_ASA/country_year_outcomes.csv
  intl_seats, intl_flights, intl_skm, intl_co2_t, intl_stage_km, intl_co2_per_skm_g, dom_* equivalents,
  gaci_cwm (seat-weighted mean), gaci_max, gaci_sum, deg_sum, betw_sum, eig_max, n_airports; 1996-2023 (2024 partial dropped)
"""
import pandas as pd, numpy as np, pathlib
root = pathlib.Path(__file__).resolve().parents[3]
e = pd.read_csv(root/"data/raw/external/airport_year_emissions.csv")
m = pd.read_csv(root/"data/processed/airport_country_map.csv")[["Airport","iso_country"]].rename(columns={"Airport":"airport_iata"})
e = e.merge(m, on="airport_iata", how="inner"); e = e[e.year <= 2023]
e["kind"] = np.where(e.dom_intl=="International","intl","dom")
agg = e.groupby(["iso_country","year","kind"]).agg(seats=("dep_seats","sum"), flights=("n_dep_flights","sum"), skm=("dep_seat_km","sum"), co2_t=("dep_co2_t","sum")).unstack("kind")
agg.columns = [f"{k}_{v}" for v,k in agg.columns]; agg = agg.fillna(0).reset_index()
for k in ["intl","dom"]:
    agg[f"{k}_stage_km"] = agg[f"{k}_skm"]/agg[f"{k}_seats"].replace(0,np.nan)
    agg[f"{k}_co2_per_skm_g"] = agg[f"{k}_co2_t"]*1e6/agg[f"{k}_skm"].replace(0,np.nan)
g = pd.read_csv(root/"data/processed/gaci_with_country.csv").dropna(subset=["iso_country"])
g = g[g.Year <= 2023]
net = g.groupby(["iso_country","Year"]).apply(lambda d: pd.Series({
    "gaci_cwm": np.average(d.GACI, weights=d.TotalCapacity) if d.TotalCapacity.sum()>0 else np.nan,
    "gaci_max": d.GACI.max(), "gaci_sum": d.GACI.sum(), "deg_sum": d.Degree.sum(), "deg_max": d.Degree.max(),
    "betw_sum": d.NorBetweenness.sum(), "eig_max": d.Eigen.max(), "n_airports": len(d), "seats_gaci": d.TotalCapacity.sum()})).reset_index().rename(columns={"Year":"year"})
out = agg.merge(net, on=["iso_country","year"], how="outer")
out.to_csv(root/"data/gaci_project/GACI_ASA/country_year_outcomes.csv", index=False)
print(out.shape, "countries:", out.iso_country.nunique(), "years:", out.year.min(), out.year.max())
print(out[out.iso_country.isin(["KR","DE","AE","US"]) & out.year.isin([1996,2008,2019,2023])][["iso_country","year","intl_seats","intl_co2_t","intl_stage_km","intl_co2_per_skm_g","gaci_cwm","deg_sum"]].round(1).to_string(index=False))
