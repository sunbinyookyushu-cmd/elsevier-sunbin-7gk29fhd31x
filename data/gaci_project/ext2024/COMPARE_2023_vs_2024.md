# GACI: 1996-2023 (paper) vs 1996-2024 (extended) re-estimation, 2026-09-02

Python re-estimation (two-way FE 2SLS, HC1 robust). Column A reproduces every published number to 3 dp (SEs about 2% below ivreghdfe because of the FE dof adjustment). Stata do-files with paths pointed at this folder are in `do_ext2024/` for the authoritative rerun.

Samples: **A** = paper panel (4,643 obs, 184 countries). **B** = rebuilt panel, y<=2023 (4,661; +16 land-backfilled rows BEL/LUX/SDN 1996-2011). **C** = rebuilt panel 1996-2024 (4,816; 185 countries; +155 country-years in 2024; heritage endowment as of 2024, which changes BIH/BRA/CHN/FRA/GBR only; a frozen-2023 endowment gives 1.208 (0.582), identical).

Data changes needed for 2024: WDI land area carried forward (no 2024 value published), UNWTO 2024 arrivals ratio 0.99 of 2019 added to the tourism shifter, BACI 2024 processed. Trade data for 2024 cover 155 countries (166 in 2023).

## Table 1 main (IV)

| outcome | A paper | B rebuilt<=2023 | C 1996-2024 |
|---|---|---|---|
| cwm: openness | 1.302 (0.647)** | 1.312 (0.662)** | 1.208 (0.580)** |
| cwm: volume | 2.303 (0.759)*** | 2.356 (0.776)*** | 2.126 (0.687)*** |
| cwm: GDP | 1.001 (0.665) | 1.045 (0.677) | 0.919 (0.611) |
| cwm KP F / N | 18.9 / 4643 | 18.1 / 4661 | 22.9 / 4816 |
| sum: openness | 0.659 (0.357)* | 0.636 (0.344)* | 0.635 (0.335)* |
| sum: volume | 1.166 (0.423)*** | 1.142 (0.408)*** | 1.119 (0.395)*** |
| sum: GDP | 0.507 (0.333) | 0.506 (0.327) | 0.483 (0.316) |
| sum KP F | 10.2 | 10.7 | 11.5 |
| max: openness | 0.966 (0.459)** | 0.960 (0.461)** | 0.897 (0.414)** |
| max: volume | 1.709 (0.535)*** | 1.724 (0.539)*** | 1.580 (0.492)*** |
| max: GDP | 0.743 (0.496) | 0.764 (0.499) | 0.683 (0.457) |

## Table 2 heterogeneity (interaction IV; main at mean / x moderator)

| spec | A | C |
|---|---|---|
| g_int_inc | 1.254 (0.702)* / -0.243 (0.120)**, SW-F 16.4 | 1.139 (0.630)* / -0.214 (0.106)**, SW-F 19.8 |
| g_vol_inc | 1.959 (0.716)*** / -1.108 (0.128)***, SW-F 16.4 | 1.718 (0.661)*** / -1.095 (0.114)***, SW-F 19.8 |
| g_gdp_inc | 0.705 (0.743) / -0.865 (0.117)***, SW-F 16.4 | 0.580 (0.691) / -0.881 (0.107)***, SW-F 19.8 |
| g_int_con | 2.260 (1.136)** / -1.482 (0.609)**, SW-F 9.6 | 2.014 (0.965)** / -1.335 (0.513)***, SW-F 12.3 |
| g_vol_con | 6.093 (1.704)*** / -6.060 (1.023)***, SW-F 9.6 | 5.584 (1.406)*** / -5.852 (0.844)***, SW-F 12.3 |
| g_gdp_con | 3.834 (1.108)*** / -4.579 (0.663)***, SW-F 9.6 | 3.570 (0.951)*** / -4.517 (0.561)***, SW-F 12.3 |

## Table 3 temporal (x post-2010)

| outcome | A main / x post | C main / x post |
|---|---|---|
| g_int | 1.247 (0.753)* / 0.012 (0.074) | 1.140 (0.683)* / 0.014 (0.074) |
| g_vol | 0.496 (0.857) / 0.377 (0.086)*** | 0.390 (0.801) / 0.373 (0.087)*** |
| g_gdp | -0.751 (0.961) / 0.366 (0.089)*** | -0.750 (0.887) / 0.359 (0.089)*** |
| first-stage F pre / post 2010 | 0.31 / 30.1 | 0.37 / 34.1 |

## Table 4 mechanism outcomes (full sample / drop 2020-21)

| outcome | A full | C full | A drop | C drop |
|---|---|---|---|---|
| r_vw | 1.714 (0.736)** | 1.868 (0.701)*** | 6.044 (2.198)*** | 5.488 (1.782)*** |
| sh_hivw | 29.342 (14.626)** | 35.513 (14.098)** | 125.729 (45.685)*** | 118.094 (37.888)*** |
| r_bec | 1.116 (0.677)* | 1.483 (0.639)** | 6.309 (2.233)*** | 6.083 (1.840)*** |
| sh_bec | 25.117 (13.391)* | 32.973 (12.713)*** | 125.725 (44.289)*** | 122.813 (36.805)*** |
| xr_vw | 4.038 (1.822)** | 3.659 (1.628)** | 11.767 (4.764)** | 9.408 (3.553)*** |
| xsh_hivw | 62.425 (27.310)** | 54.579 (24.178)** | 177.772 (71.175)** | 140.030 (52.719)*** |
| lntot | 0.272 (0.778) | 0.412 (0.705) | 2.971 (1.438)** | 2.685 (1.220)** |
| KP F | 19.0 | 23.1 | 9.5 | 12.8 |

## Table 5 mediation, openness, full sample (6 columns)

| column | A | C |
|---|---|---|
| (1) total | 1.268 (0.641)** | 1.176 (0.575)** |
| (2) M1 = ln(interm/consum) as outcome | 1.116 (0.677)* | 1.483 (0.639)** |
| (3) + M1 | 1.086 (0.624)* | 0.939 (0.558)* |
| (4) M2 = ln(hiVW/loVW) as outcome | 1.714 (0.736)** | 1.868 (0.701)*** |
| (5) + M2 | 1.247 (0.653)* | 1.144 (0.586)* |
| (6) + both | 0.996 (0.635) | 0.825 (0.570) |

## Table 6 controls sensitivity (openness)

| controls | A | C |
|---|---|---|
| none | 1.663 (0.757)** F 15.9 | 1.516 (0.660)** F 19.8 |
| lnpop | 1.302 (0.647)** F 18.9 | 1.208 (0.580)** F 22.9 |
| lngdp | 1.706 (0.672)** F 20.0 | 1.540 (0.588)*** F 25.0 |
| pop_gdp | 1.642 (0.671)** F 19.8 | 1.505 (0.596)** F 24.3 |
| pop_pc | 1.430 (0.688)** F 21.9 | 1.340 (0.631)** F 25.6 |

## Table 7 validity battery (openness / volume)

| test | A | C |
|---|---|---|
| A_natmix_g_int | 1.267 (0.628)** F 8.9, J p=0.514 | 1.174 (0.549)** F 10.9, J p=0.589 |
| B_nat_g_int | 1.094 (0.662)* F 16.3 | 1.027 (0.615)* F 18.7 |
| B_three_g_int | 0.454 (0.360) F 20.7, J p=0.069 | 0.500 (0.322) F 25.1, J p=0.111 |
| C_tour_g_int | 1.250 (0.614)** F 20.6 | 1.152 (0.548)** F 25.2 |
| C_feyr_g_int | -0.301 (0.229) F 160.9 | -0.235 (0.220) F 168.1 |
| C_both_g_int | -0.055 (0.212) F 101.8, J p=0.005 | 0.005 (0.202) F 108.6, J p=0.007 |
| C_both19_g_int | -0.053 (0.238) F 102.4, J p=0.000 | -0.044 (0.241) F 100.3, J p=0.000 |
| A_natmix_g_vol | 2.178 (0.705)*** F 8.9, J p=0.780 | 1.900 (0.628)*** F 10.9, J p=0.733 |
| B_nat_g_vol | 2.090 (0.790)*** F 16.3 | 2.011 (0.742)*** F 18.7 |
| B_three_g_vol | 0.394 (0.491) F 20.7, J p=0.004 | 0.371 (0.440) F 25.1, J p=0.008 |
| C_tour_g_vol | 2.206 (0.719)*** F 20.6 | 2.026 (0.649)*** F 25.2 |
| C_feyr_g_vol | 2.257 (0.299)*** F 160.9 | 2.304 (0.289)*** F 168.1 |
| C_both_g_vol | 2.249 (0.289)*** F 101.8, J p=0.945 | 2.256 (0.275)*** F 108.6, J p=0.684 |
| C_both19_g_vol | 2.728 (0.329)*** F 102.4, J p=0.000 | 2.740 (0.333)*** F 100.3, J p=0.000 |

## Table 8 plausibly exogenous (lower bounds at gamma = 10/20/30% of RF; f*)

| outcome | A | C |
|---|---|---|
| g_int | lb -0.065 / -0.166 / -0.269, f* 0.04 | lb -0.026 / -0.124 / -0.224, f* 0.08 |
| g_vol | lb 0.610 / 0.396 / 0.176, f* 0.38 | lb 0.582 / 0.379 / 0.171, f* 0.38 |
| g_gdp | lb -0.413 / -0.526 / -0.640, f* 0.00 | lb -0.380 / -0.483 / -0.587, f* 0.00 |

## Reduced form by quintile (RF coefficient of tourism_int on openness)

| moderator | A q1..q5 | C q1..q5 |
|---|---|---|
| inc | 0.179, -0.094, 0.028, 0.103, 0.020 | 0.156, -0.069, 0.030, 0.108, 0.021 |
| con | 0.229, 0.103, 0.048, 0.060, 0.011 | 0.263, 0.102, 0.021, 0.044, 0.015 |

## Aggregate contribution (openness channel)

| | paper 2023 (beta 1.302) | ext 2024 (beta 1.208) | ext 2024 (beta 1.302) |
|---|---|---|---|
| attributable trade, $T | 7.75 | 9.95 | 10.54 |
| % of world trade | 16.5 | 21.3 | 22.6 |
| % of world GDP | 7.4 | 9.2 | 9.7 |
| world goods trade, $T | 46.9 | 46.6 | 46.6 |
| world openness now, % | 44.8 | 43.0 | 43.0 |
| counterfactual openness, % | 37.4 | 33.9 | 33.3 |
| China share of gain, % | 27 | 27 | 27 |

Note: the 2024 aggregate is larger despite the smaller elasticity because hub quality kept recovering in 2024 (larger 1996-2024 change in ln GACI_cwm) and the base moves to 2024 trade levels.
