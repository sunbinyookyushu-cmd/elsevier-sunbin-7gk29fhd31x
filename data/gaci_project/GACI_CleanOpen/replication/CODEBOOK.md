# panel_v4 — codebook (country-year, ISO3 `c`, year `y`, 1996–2024)

Built by `build_panel_v4.py`. All GDP/population denominators from WDI so that log identities hold exactly:
`lngdp = lnpc + lnpop`; `ln_so2gdp = ln_ei + ln_ce + ln_so2co2`; Kaya `ln_co2 = lnpop + lnpc + ln_ei + ln_ce`.
`in_unified = 1` marks the estimation sample used in all tables (173 countries, 1996–2019: all Table-1 outcomes and the instrument observed).

| variable | definition | source |
|---|---|---|
| air, ln_gaci_cwm | log of seat-weighted mean airport GACI (country) | GACI panel (OAG-based; index values only) |
| gaci_cwmean, gaci_mean | seat-weighted / unweighted country mean of airport GACI (levels) | GACI panel |
| reg, region | GACI macro-region code (AF, AS, EU, LA, ME, NA, SW) | GACI panel |
| continent, subregion, landlocked | UN continent (5), UN subregion (22), landlocked dummy | mledoze/countries |
| tourism_int | UNESCO natural+mixed heritage sites × world tourist arrivals (instrument, weak here) | GACI trade paper |
| feyrer_int | Feyrer-type air market access: geography × world air-traffic growth (main instrument) | GACI trade paper |
| ln_sea_ma | geography-based sea market access | GACI trade paper |
| ln_lsci | log annual mean UNCTAD Liner Shipping Connectivity Index (2006–) | UNCTADstat |
| gdppc_2015usd, pop_wdi | GDP per capita (constant 2015 US$), population | WDI NY.GDP.PCAP.KD, SP.POP.TOTL |
| lnpc, lnpop, lngdp, lnpc2 | logs; lngdp = lnpc + lnpop; lnpc2 = lnpc^2 | derived |
| co2, coal_co2, oil_co2, gas_co2, cement_co2 | fossil CO2, Mt, by fuel | OWID / Global Carbon Project |
| primary_energy_consumption, coal_consumption, oil_consumption, gas_consumption | TWh | OWID / Energy Institute (fuel detail: 77 countries) |
| renew_sh | renewable energy consumption, % of final energy | WDI EG.FEC.RNEW.ZS |
| renewables_share_energy, low_carbon_share_energy | % of primary energy | OWID / EI |
| so2_total, nox_total | national SO2, NOx emissions, tonnes (to 2019) | CEDS v2022 via OWID |
| coal_so2, oil_so2, natural_gas_so2, process_so2, biomass_so2 | SO2 by fuel/process, tonnes | CEDS v2022 via OWID |
| ln_so2, ln_nox, ln_co2, ln_energy | logs of totals | derived |
| ln_so2gdp, ln_so2pc, ln_noxgdp, ln_noxpc | SO2, NOx per GDP / per capita (logs) | derived |
| ln_ci, ln_co2pc, ln_ei, ln_ce | ln CO2/GDP, ln CO2 pc, ln energy/GDP, ln CO2/energy | derived |
| ln_so2co2, ln_noxco2, ln_so2energy | sulphur (NOx) intensity of carbon; SO2 per energy | derived |
| ln_coal_cons, ln_oil_cons, ln_coal_co2 | logs of coal/oil use (TWh) and coal CO2 | derived |
| ln_so2_coal_cons, ln_so2_oil_cons | SO2 from coal (oil) per TWh of coal (oil) consumed | derived (CEDS / EI) |
| ln_so2_coal_ef, ln_so2_oil_ef, ln_so2_fossil_ef | SO2 from a fuel per CO2 from the same fuel | derived (CEDS / OWID) |
| ln_so2_process, so2_coal_sh | process SO2 (log); coal share of SO2 | derived |
| manuf_sh, ind_sh, serv_sh, agr_sh | value added shares, % GDP | WDI |
| hitech_x_sh, manuf_x_sh | high-tech % of manufactured exports; manufactures % of merchandise exports | WDI |
| trade_gdp_wdi, fdi_in_gdp, urban_sh | trade % GDP, FDI inflows % GDP, urban % | WDI |
| trade_share, merch_share | trade/GDP and merchandise trade/GDP from the GACI panel | GACI trade paper |
| energy_pc_kgoe, energy_int_mj, elec_coal_sh, pm25_wdi | WDI energy/pollution series | WDI |
| rnna, emp, hc, lnkl, lnkl2 | capital stock, employment, human capital; ln K/L and square | PWT 11.0 |
| inc96, inc_ter | 1996 ln GDP pc; income tercile (low/mid/high) | derived |
| merch96, serv96, goods_econ, air_goods | 1996 merchandise-trade share, services share; goods-economy dummy (> median); interaction | derived |

Files: `panel_v4.csv`, `panel_v4.dta` (Stata 14). Scripts: `build_panel_v4.py`, `tables_v4.py` (all tables), `make_figures.py`, `make_map.py`.
Note on sharing: GACI values are a derived index; the underlying OAG schedules are proprietary and are not included.
