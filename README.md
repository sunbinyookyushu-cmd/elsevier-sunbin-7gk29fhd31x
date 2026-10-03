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

## Note (2026-10-03)
The session scaffold in `scripts/`, `stata/` and `data/processed/` (annual airport DiD, tax master table, FEAT fuel
model) predates the upload of the full project folder `data/gaci_project/`. The ticket-tax paper lives in
`data/gaci_project/GACI_FuelShock/` (stacked monthly DiD, SDID, HonestDiD, Stata package in `stata_paper/`), and the
main-text draft is in `GACI_FuelShock/draft_tax_lean_20261002/`. Still useful from the scaffold:
`data/processed/aviation_taxes_master.csv` (17 countries, rates to 2026), `tax_by_origin_dest_year.csv` (band logic by
destination country) and `band_reference_distances.csv`; the annual binary DiD is superseded (see
`output/robustness_co2_binary_did.txt` for why).
