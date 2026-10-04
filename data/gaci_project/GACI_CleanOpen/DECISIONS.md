# DECISIONS.md — data and sample decisions in GACI_CleanOpen

Rule (from the author, 2026-10-04): no sample, period or variable-definition choice is made by the assistant without
recording it here and getting it confirmed. Status: **confirmed** (author decided), **applied, confirm** (assistant applied
a default needed to carry out an author decision; author to confirm or change), **pending** (not applied).

| # | decision | choice applied | status | where |
|---|---|---|---|---|
| 1 | Estimation sample rule | country-years with air, ln pop, ln pc, ln SO2/GDP, ln NOx/GDP, ln CO2/GDP, ln E/GDP, ln CO2/E and the Feyrer instrument observed | applied, confirm | build_panel_v4.py `CORE` |
| 2 | End year | 2023 (author: "2023년까지 늘릴 수 있으면 늘려보자") | confirmed | panel_v4 |
| 3 | SO2/NOx source | CEDS v_2025_03_18 (author download) for the whole period; the 2022 mirror kept as `*_v22` for a robustness column | applied, confirm | build_ceds2025.py |
| 4 | Renewable share | removed from the sample rule (WDI EG.FEC.RNEW.ZS ends 2021); reported to 2021; renewables share of electricity (OWID/Ember-EI) added to 2023 | applied, confirm | T1 |
| 5 | COVID years 2020–2021 | included (year FE); excluding them reported in Appendix A1 | applied, confirm | A1 |
| 6 | Denominators | WDI GDP per capita (constant 2015 US$) × WDI population for all intensities, so log identities hold exactly | applied (after coauthor comment 2-2), confirm | build_panel_v4.py |
| 7 | Base specification | country + year FE, ln pop, ln pc, (ln pc)^2, SE clustered by country | confirmed | all tables |
| 8 | Income terciles | 1996 ln GDP pc terciles | applied, confirm | T4 |
| 9 | Goods vs service economy | merchandise trade/GDP in 1996 above the cross-country median | applied, confirm | T4 |
| 10 | Gelbach mediators | manuf, services, agric. shares; trade/GDP, FDI/GDP; urban share | applied, confirm | T3 |
| 11 | Tourism instrument | dropped from single-instrument IV (first-stage F < 1); kept in the over-identified model of T5 | applied, confirm | T5 |
| 12 | Tercile-level IV | not reported (first-stage F < 1 in low/mid terciles) | applied, confirm | T4 |
| 13 | Region definitions for FE checks | GACI 7 macro-regions; UN 5 continents; UN 22 subregions; region linear trends | applied, confirm | A1 |
| 14 | Fuel grouping (CEDS) | coal = hard + brown + coke; oil = heavy + light + diesel | applied, confirm | build_ceds2025.py |
| 15 | Fuel-consumption emission factors | Energy Institute coal/oil consumption (TWh), 77 countries | applied, confirm | T2 |
| 16 | Global aggregate / map window | countries with ≥15 years in the sample; first-to-last-year change; linear extrapolation of the T1 elasticity | applied, confirm | make_map.py |
| 17 | Logs of zero emissions | zeros set to missing before logs | applied, confirm | build_panel_v4.py `L()` |
| 18 | Earlier 2019 cut-off (superseded) | came from the CEDS 2022 mirror and from putting SO2/NOx in the sample rule; was not asked | superseded by #2 | — |
| 19 | GTFP construction (secondary, not in tables) | global Malmquist–Luenberger, CRS, countries with ≥20 years | pending (not used in current tables) | gtfp_ml.py |
