# Aviation taxes, air connectivity (GACI) and CO2 — data collection

Working repository for the project *"Does aviation tax cut carbon, or just move it? Route-level evidence and
the connectivity cost of abatement"* (target: Energy Economics). This repo holds the public reference data,
the tax event table, the fuel-burn/CO2 model, and ready-to-run download scripts. The proprietary OAG
schedule data and the GACI construction code are **not** here (GACI panel is included as data).

See `docs/data_collection.md` for the inventory, what is done, what is blocked, and how to run.

```
data/raw/gaci/         GACI airport-year panel 1996–2024 (Yoo et al.; Cheung, Wong & Zhang 2020 method)
data/raw/airports/     OurAirports, OpenFlights, mledoze/countries reference tables
data/raw/taxes/        Aviation ticket tax event tables by country group (+ docs/taxes_*.md narratives)
data/raw/emissions/    FEAT reduced-order fuel-burn coefficients (Seymour et al. 2020)
data/processed/        airport→country map, GACI with country, capitals, band distances, CO2 lookup
scripts/               numbered pipeline scripts (01–07) + geo_utils
```
