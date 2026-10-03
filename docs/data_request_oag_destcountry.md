# Data request: seats and CO2 by origin airport × destination country × year

Needed for the clean axis-2 design (`stata/06_band_did.do`). Same source and method as
`airport_month_emissions.csv`, but keep the **destination country** dimension and drop the month.

File: `data/raw/oag/seats_co2_by_origin_destcountry_year.csv` (expected 2–5 million rows, ~100 MB; if over
100 MB, gzip it or split by decade: `..._1996_2009.csv`, `..._2010_2024.csv`).

| column | definition |
|---|---|
| origin_iata | departure airport IATA |
| dest_iso | ISO-2 of the **destination airport's country** (domestic rows have dest_iso = origin country) |
| year | calendar year |
| n_flights | scheduled departures |
| seats | departing seats |
| seat_km | seats × great-circle km |
| co2_kg | departure CO2, all phases (taxi-out + take-off + climb-out + cruise), kg |

Optional but useful: `co2_lto_kg` (taxi-out + take-off + climb-out only) and `n_months` (coverage check).

Why destination *country* and not route: every European ticket tax sets its band by destination country
(statutory annexes) or by capital-city distance, so the tax payable is constant within (origin country,
destination country, year). The country level therefore carries all the identifying variation while
keeping the file small.
