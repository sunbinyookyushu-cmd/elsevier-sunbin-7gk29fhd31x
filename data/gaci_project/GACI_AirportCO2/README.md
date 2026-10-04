# GACI_AirportCO2 — Does air connectivity make the local economy cleaner? (airport-catchment design)

Why. The country-level "clean openness" result (GACI_CleanOpen) is a between-group convergence correlation: it
vanishes with income-group x year or region x year FE. GACI is an airport-level index, so the natural unit is the
airport catchment, which allows country x year FE: compare hub and non-hub catchments inside the same country-year.

Design.   ln CO2_{a,t}^{(s)} = b ln GACI_{a,t} + g ln pop_{a,t} + alpha_a + lambda_{c(a),t} + e
  a = airport catchment (grid cells within 50/100 km whose nearest GACI airport is a), s = EDGAR sector.
  Outcomes: total CO2 excl. aviation; power (ENE); manufacturing combustion (IND); road (TRO); residential (RCO);
            CO2 per capita (GHS-POP).  Treatment: airport GACI (and raw degree / destinations / seats for robustness).
  IV (as in the tax paper axis 1): UNESCO natural heritage within 100 km x world tourist arrivals; Feyrer-type air
  market access of the airport.  Dynamics: 5/10-year long differences.  Heterogeneity: hub vs regional, income.
  Events as supporting evidence: hub closures/airline exits (Air Berlin 2017 TXL/DUS, Alitalia MXP de-hubbing 2008,
  Malev 2012 BUD, Spanair 2012 BCN, Cyprus Airways 2015 LCA, Adria 2019 LJU, flybe 2020) -> stacked DiD on catchment CO2.

Known caveat (write it in the paper). EDGAR allocates national totals to grid cells with spatial proxies: point
sources for ENE/IND (good, real location information), population for RCO and road density for TRO. For RCO/TRO a
"local effect" could partly be the proxy moving. Therefore: main outcomes = ENE + IND (point-source sectors) and total
excl. aviation; RCO/TRO as secondary; always exclude TNR_Aviation sectors (mechanical).  Second caveat: local growth
and connectivity are simultaneous -> IV and long differences matter; OLS is descriptive.

## Downloads needed (public, then run aggregate_edgar.py locally)
1. EDGAR v8.0 (or EDGAR 2024) gridded CO2, 0.1 deg, annual, netCDF, years 1996-2022:
   https://edgar.jrc.ec.europa.eu/dataset_ghg80  -> "CO2 (fossil) ... gridmaps" : TOTALS and sector files
   ENE, IND, TRO, RCO, TNR_Aviation_CDS, TNR_Aviation_CRS, TNR_Aviation_LTO (one .nc per year per sector).
   ~27 years x 8 files; each file 10-60 MB.  Do NOT upload them here; run the script and upload only the output CSV.
2. GHS-POP (JRC) population grid, epochs 1990-2025, 1 km or 30 arcsec, resampled to 0.1 deg; or Gridded Population
   of the World v4 (SEDAC, 2000/05/10/15/20).  Optional but needed for per-capita outcomes.
3. (optional) VIIRS/DMSP night lights annual composites as a local-GDP proxy.

Run:  python aggregate_edgar.py --edgar_dir <edgar folder> --airports data/processed/airport_country_map.csv
           --gaci data/raw/gaci/GACI1996_2024_panel.csv [--pop_dir <pop folder>] --out airport_catchment_co2.csv
Then upload airport_catchment_co2.csv (a few MB) and the analysis (stata/09_airport_catchment.do, Python mirror) runs here.
