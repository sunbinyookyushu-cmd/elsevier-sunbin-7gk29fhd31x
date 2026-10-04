# GACI_CleanOpen — Is air openness clean openness?

Question. Openness arrives by two modes: aircraft move people and light, high value-to-weight goods; ships move heavy,
pollution-intensive goods. Transposing Managi, Hibiki & Tsurumi (2009, JEEM), we ask whether a country's air
connectivity (GACI) and its sea connectivity (UNCTAD LSCI) have different effects on the carbon, energy and
pollution intensity of the economy, and through which channel (income/scale, composition, technique).

Design.   ln Y_ct = b_air ln GACI_ct + b_sea ln LSCI_ct + g ln y_ct + d ln pop_ct + a_c + l_t + e_ct,   2006-2023
  Y: CO2/GDP, energy/GDP, CO2/energy, CO2 pc, primary energy intensity (WDI), renewable share, SO2/GDP and NOx/GDP (CEDS, to 2019),
     PM2.5 exposure (WDI), Green TFP (global Malmquist-Luenberger from PWT 11 + CO2 [+SO2]).
  IV for GACI: tourism_int (heritage x world arrivals) and feyrer_int (air market access), as in the GACI trade paper.
  Channel: exact Gelbach (2016) decomposition of b_air into income | composition (manuf, services, agriculture % GDP) |
  openness (trade, FDI % GDP) | urbanisation. Heterogeneity by 1996 income tercile. Country-clustered SE.

## Data (all built here)
| file | source | content |
|---|---|---|
| data_external/lsci/US_LSCI.csv | UNCTADstat (user upload, .7z) | quarterly LSCI 2006Q1-2026, M49 codes -> ISO3 via mledoze; `lsci_country_year.csv` = annual mean, ln_lsci |
| data_external/wdi/wdi_data.csv | WDI DataBank (user upload) | 16 series -> `wdi_country_year.csv` (manuf_sh ind_sh serv_sh agr_sh hitech_x_sh manuf_x_sh energy_pc_kgoe energy_int_mj elec_coal_sh renew_sh pm25_wdi gdppc_2015usd pop_wdi urban_sh fdi_in_gdp trade_gdp_wdi) |
| data_external/pwt/pwt110.xlsx | PWT 11.0 (user upload) | `pwt_country_year.csv` (rgdpna rnna emp hc ...) -> `gtfp_country_year.csv` |
| data_external/ceds_*, pm25-* | CEDS v2022 / WB via OWID mirrors | `pollution_country_year.csv` (SO2 NOx CO BC OC NMVOC NH3 1990-2019, PM2.5) |
| ../gaci_panel_combined.csv, ../GACI_CO2/data_external/owid-co2-data.csv | trade paper, OWID | GACI, income, pop, instruments; CO2/energy |
Merged analysis panel: `clean_open_panel.csv` / `stata/clean_open_panel.dta` (Stata 14 format).

Scripts: build_external_panels.py -> gtfp_ml.py (global ML DEA, ~7 min) -> analysis_v2_lsci.py (_out_v2.txt, _res_v2.csv)
-> export_and_robust.py (sample-vs-measure check, Stata export). v1 (geographic sea MA, 1996-2023): analysis_clean_openness.py.
Stata: stata/08_clean_openness.do reproduces Tables 1-7 with reghdfe/ivreghdfe/b1x2.

## Results (2006-2023, sea = ln LSCI, country + year FE, +ln pop; SE clustered by country)
Air = ln GACI_cwm. Within-country SD: air 0.065, sea 0.189 (so multiply air by 0.065, sea by 0.189 for 1-SD effects).

| outcome | OLS air | OLS sea | +lnpc air | +lnpc sea | 2SLS air | N (C) |
|---|---|---|---|---|---|---|
| ln CO2/GDP | -0.317 (0.115)*** | +0.063 (0.062) | -0.225 (0.107)** | +0.100 (0.051)* | +0.09 (0.44) | 1917 (114) |
| ln energy/GDP | -0.180 (0.086)** | +0.027 (0.061) | -0.081 (0.088) | +0.068 (0.041) | -0.25 (0.31) | 1870 (114) |
| ln CO2/energy | -0.157 (0.068)** | +0.029 (0.020) | -0.172 (0.067)** | +0.023 (0.023) | +0.48 (0.33) | 2213 (137) |
| ln CO2 pc | +0.131 (0.130) | +0.217 (0.057)*** | -0.191 (0.091)** | +0.108 (0.044)** | -0.27 (0.43) | 2377 (139) |
| ln energy intensity (WDI) | -0.282 (0.090)*** | +0.057 (0.037) | -0.074 (0.058) | +0.123 (0.032)*** | +0.03 (0.36) | 2147 (136) |
| renewable share (pp) | +4.5 (2.5)* | -2.2 (1.2)* | +10.8 (2.5)*** | -0.5 (1.1) | +1.0 (8.9) | 2146 (139) |
| ln SO2/GDP | -0.964 (0.325)*** | +0.019 (0.088) | -0.652 (0.291)** | +0.083 (0.083) | -6.19 (2.73)** | 1816 (136) |
| ln NOx/GDP | -0.416 (0.208)** | -0.052 (0.073) | -0.116 (0.167) | +0.010 (0.067) | -3.04 (1.74)* | 1816 (136) |
| ln PM2.5 | -0.049 (0.049) | +0.006 (0.016) | -0.045 (0.049) | +0.007 (0.016) | -0.19 (0.20) | 2307 (134) |
| ln GTFP (CO2 bad) | +0.016 (0.035) | -0.013 (0.013) | -0.025 (0.032) | -0.036 (0.015)** | -0.09 (0.14) | 1862 (105) |
| ln TFP (DEA, no bad) | +0.140 (0.104) | +0.168 (0.079)** | -0.155 (0.065)** | +0.006 (0.023) | +0.05 (0.22) | 1862 (105) |

Reading. Air and sea connectivity have opposite signs: air connectivity lowers carbon, energy and SO2 intensity and the
dirtiness of the fuel mix, and raises the renewable share; sea connectivity raises CO2 pc and energy intensity. Per within-SD
the two are of similar size (CO2/GDP: air -2.1%, sea +1.9%). Aviation's own CO2 is < 3% of national CO2, so the air
coefficients are not mechanical.

Gelbach decomposition of b_air (base -> full with all mediators):
  ln CO2/GDP  -0.243 -> -0.173: explained -0.070 = income -0.040 | composition -0.007 | openness -0.001 | urbanisation -0.021
  ln SO2/GDP  -0.824 -> -0.523: explained -0.300 = income -0.216 | composition -0.085 | openness -0.004 | urbanisation +0.005
  ln NOx/GDP  -0.292 -> -0.107: explained -0.185 = income -0.162 | composition -0.033 | openness +0.007 | urbanisation +0.003
  ln CO2/energy -0.131 -> -0.131: nothing explained (pure technique / fuel-mix effect)
  -> composition (industry shares) explains at most 10% of the air effect; income 15-25%; 60-100% is residual
     technique. "Air openness is clean openness" is NOT mainly a light-industry composition story.

Instruments. First stage (clustered t): tourism_int 3.8, feyrer_int 2.3. Instrument-by-instrument 2SLS:
  SO2/GDP tourism -8.1 (9.1), Feyrer -5.9 (3.0)**, both -6.2 (2.7)**, Sargan p 0.47  -> consistent, large.
  NOx/GDP both -3.0*, Sargan p 0.05. CO2/GDP: tourism +0.63 (0.39), Feyrer -2.3 (2.1), Sargan p 0.004 -> IVs disagree;
  CO2 IV estimates are not credible. Headline for CO2 stays OLS-FE; IV supports the local-pollution result.

Heterogeneity (OLS +lnpc, air coef): CO2/energy high-income -0.346 (0.096)***, low/mid ~0; SO2/GDP mid-income -0.81 (0.56);
  energy/GDP high-income +0.17 (0.11). The fuel-mix cleaning is a rich-country phenomenon.

Sample vs measure. LSCI covers coastal economies only (landlocked share 0.7% vs 20.6% in full panel). On the LSCI sample the
air coefficient on ln CO2/GDP is -0.225 with LSCI, -0.138 with geographic sea MA, -0.175 with no sea control; on the full
2006-2023 sample -0.068 / -0.134. Half of the difference to v1 is sample (coastal countries), half is measurement.

GTFP. Global Malmquist-Luenberger (Oh 2010) with K = rnna, L = emp x hc, good = rgdpna, bad = CO2 (variant: CO2+SO2),
144 countries 1995-2023; growth correlates 0.57 with PWT rtfpna growth (conventional DEA TFP: 0.95). Air connectivity has no
effect on GTFP; sea connectivity lowers it (-0.036 (0.015)** with income). GTFP is a secondary result, not the headline.

## What to say in the paper
1. Air connectivity is "clean openness": lower CO2/GDP, energy/GDP, CO2/energy, SO2/GDP; higher renewable share. Sea
   connectivity is the mirror image (CO2 pc, energy intensity up). Country+year FE, within-SD comparable.
2. Mechanism (Gelbach): not composition; mostly technique (fuel mix) plus income. Knowledge/technology diffusion story
   (face-to-face contact, FDI in services, management practices) rather than relocation of dirty industry.
3. IV: valid for local pollutants, over-identification fails for CO2 -> present as supporting evidence only.
4. Limitations: LSCI window 2006-; coastal sample; CEDS ends 2019; GACI within-country variation is small (SD 0.065).
