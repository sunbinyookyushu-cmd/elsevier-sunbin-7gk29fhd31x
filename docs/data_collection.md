# Data collection — inventory and status

Project: aviation ticket taxes → route-level CO2 and network connectivity (GACI), Europe-anchored,
1996–2024. Identification: within-origin-airport variation across distance bands of per-passenger taxes
(origin×year and destination×year fixed effects), plus cross-border leakage to untaxed neighbours.

## 1. What is in the repo now

| Dataset | Path | Status | Notes |
|---|---|---|---|
| GACI airport-year panel 1996–2024 | `data/raw/gaci/GACI1996_2024_panel.csv` | done | 101,049 airport-years, 5,428 airports, 17 OAG regions; Degree, TotalCapacity (seats), Eigen, NorClose, NorBetweenness, RegionalImportance, GACI |
| Airport → ISO country, lat/lon | `data/processed/airport_country_map.csv` | done | OurAirports (5,269), OpenFlights fallback (71), manual (18). 98.7% of airports, 99.8% of airport-years, ~100% of seat capacity. Namibia "NA" code handled. |
| GACI with country | `data/processed/gaci_with_country.csv` | done | input for country aggregation (cwm / max / sum as in the trade paper) |
| Country reference table | `data/processed/country_capitals.csv` | done | ISO2/3, capital + coordinates (245/250), centroid, borders, region |
| Tax-band reference distances | `data/processed/band_reference_distances.csv` | done | London/Frankfurt/Vienna/Stockholm/Oslo/Paris/Amsterdam/Brussels/… → every capital, km & miles; UK APD bands 2009–15, 2015–23, 2023– reproduced; DE 2,500/6,000 km rule |
| Fuel-burn / CO2 model | `scripts/02_fuel_burn_model.py`, `data/processed/co2_per_flight_lookup.csv` | done | FEAT reduced-order model (Seymour et al. 2020), 133 ICAO types + IATA alias table for OAG codes; CO2 = 3.16 × fuel; detour +5% +40 km (parameters) |
| Aviation tax event tables | `data/raw/taxes/taxes_*.csv` → `data/processed/aviation_taxes_master.csv` (391 rows, 17 countries, `include_main` flag; narratives in `docs/taxes_*.md`) | done (verify low/medium cells) | compiled from WebSearch snippets of official sources; every row carries a confidence flag and source URL — **verify high-stakes cells against the primary legal texts before estimation** |

## 2. What is blocked by the session network policy (scripts are ready)

The cloud session can reach GitHub (raw/clone) and PyPI only. These hosts returned 403 from the egress
proxy; allow them in the environment's network settings (Custom → Allowed domains) or run the scripts locally:

| Source | Host(s) to allow | Script | Use |
|---|---|---|---|
| Eurostat avia_par_XX (route-level passengers, flights; 1993–) | `ec.europa.eu` | `scripts/03_download_eurostat_avia_par.py` | load factor and passengers per route; "CO2 per passenger" outcome |
| Climate TRACE airport emissions 2015– | `api.climatetrace.org`, `downloads.climatetrace.org` | `scripts/04_download_climatetrace.py` | validate bottom-up airport-year CO2 |
| EDGAR / OWID national aviation CO2 | `edgar.jrc.ec.europa.eu`, `ourworldindata.org`, `nyc3.digitaloceanspaces.com` | `scripts/05_download_national_aviation_co2.py` | descriptive only (fuel-sold basis) |
| Official tax pages (HMRC gov.uk, BMF, Skatteverket, Legifrance, CE Delft) | `www.gov.uk`, `www.legislation.gov.uk`, `www.bundesfinanzministerium.de`, `www.skatteverket.se`, `www.legifrance.gouv.fr`, `cedelft.eu` | — | primary-source verification of the tax table |
| EEA EMEP/EEA guidebook aviation annex | `www.eea.europa.eu` | — | alternative emission factors (robustness) |

## 3. Not obtainable here (proprietary)

* **OAG schedule segments** (route × carrier × aircraft × year: frequencies, seats, aircraft type). Needed for
  the route-level CO2 outcome and for recomputing GACI. The user holds this (GACI was built from it).
  Required fields per segment-year: origin IATA, destination IATA, aircraft IATA/ICAO code, departures, seats,
  (optionally ASKs, carrier, domestic/international flag).

## 4. How the pieces fit (pipeline sketch)

1. `01_map_airports_to_country.py` → airport→country; `06_country_capitals.py` → capitals; `07_band_reference_distances.py` → bands.
2. OAG segments + `geo_utils.haversine_km` (airport coordinates from the map) → great-circle km per route.
3. `02_fuel_burn_model.co2_kg(aircraft_code, gc_km) × departures` → route-year CO2; sum to airport-year; compare with Climate TRACE 2015–.
4. Tax tables × band distances → per-passenger tax on each route-year; ÷ (CO2 per passenger, using seats × load factor from Eurostat) → implicit €/tCO2.
5. Estimation: route FE + origin×year FE + destination×year FE; event studies around 2009/2015/2023 (UK), 2011/2020 (DE), 2008/2009 (NL), 2018/2025 (SE); border-leakage ring around taxed airports; heterogeneity by GACI of untaxed substitutes within 200 km.

## 5. Known caveats to carry into the paper

* GACI is standardised within year (relative network position); report seats (absolute) alongside GACI.
* 850 small airports appear ≤3 years; restrict DiD samples to airports with sustained service or a seat floor.
* FEAT reduced model over-predicts fuel on very short sectors for long-haul types (<500 km); irrelevant for taxed long-haul bands but flag in the appendix.
* Tax tables assembled from secondary snippets where primary pages were unreachable; confidence flags in the CSV.
