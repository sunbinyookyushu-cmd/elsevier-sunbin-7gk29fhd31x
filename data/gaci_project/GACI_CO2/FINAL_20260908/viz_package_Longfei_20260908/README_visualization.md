# Visualization data package (8 September 2026)

Contents

- `CO2_visualization_data_20260908.xlsx`: one sheet per manuscript display. The `README` sheet inside maps every sheet to its figure or table, says what to plot, and names the source result file.
- `current_figures/`: the PNGs currently placed in the manuscript (matplotlib drafts). They show the intended content and panel layout of each figure; the design is open.
- `manuscript_20260908.pdf`: the current compiled manuscript, so that each figure can be read against its caption and the text that cites it.
- `ne_50m_admin_0.geojson`: Natural Earth 1:50m country boundaries (ISO3 in the `ISO_A3` property) for the choropleths.

Column conventions (all estimation sheets)

- `b` coefficient, `se` standard error, `p` p-value, `ci_lo` / `ci_hi` 95 percent confidence interval, `stars` significance stars, `sig05` = 1 if p < 0.05 (use for filled versus hollow markers).
- Elasticities are percent change in the outcome per one percent change in connectivity (GACI). A dashed reference line at 1 (proportional growth) is used in the coefficient plots.
- Country identifiers are ISO3 (`iso3`); airports are IATA codes (`airport_iata`) with `lat` / `lon`.

Main-text figures

| Figure | Sheet | Plot |
|---|---|---|
| Fig. 1 Heterogeneity (four panels) | `F1_hetero` | Dot-and-whisker per panel (income tercile, connectivity tercile, region, intensity by income); filled marker if `sig05` = 1; vertical line at 1 |
| Fig. 2 Attributed emissions map, 2023 | `MAP_country_2023` (column `att_tot_mt`) | Choropleth on ISO3, diverging scale centred at zero (asinh or signed log helps; China 85.9 Mt to Germany -14.7 Mt); white = zero |
| Fig. 3 World CO2 to 2050 under SAF blending | `F3_saf` (rows with `in_figure` = 1) | Two panels (growth_case central / low); lines of `co2_Mt` by year for each `lca_saving_r` (0 = no SAF, dashed grey; 0.5 / 0.65 / 0.8 solid); dotted line = `co2_Mt_fixed_2023_traffic` for r = 0.65; horizontal references `ref_2023_level` (848 Mt) and `ref_2023_minus_attributed` (499 Mt); x ticks at milestone years with `blend_share` |

Extended Data figures

| Figure | Sheet | Plot |
|---|---|---|
| ED Fig. 1 Temporal split | `EDF1_temporal` | Dot-and-whisker grouped by outcome, one marker per period; grey if `weak_first_stage` = 1 |
| ED Fig. 2 Decomposition waterfall | `T2_decomp` | Waterfall from `waterfall_start` to `waterfall_end`: flights, seats per flight, km per flight, intensity, total |
| ED Fig. 3 Elasticity along baseline connectivity | `EDF3_gradient` | Quintile points with CIs plus fitted linear and quadratic curves (`series`) against baseline GACI |
| ED Fig. 4 Country attribution bars | `MAP_country_2023` | Horizontal bars of `att_tot_mt`, top countries and Germany |
| ED Fig. 5 Emission levels map | `MAP_country_2023` (`bunker_mt_2023`, log scale) | Choropleth |
| ED Fig. 6 Attribution mismatch map | `MAP_country_2023` (`mismatch_pp` = bunker share minus LTO share) | Diverging choropleth |
| ED Fig. 7 Airport efficiency curve | `EDF7_efficiency_curve` | Median kg CO2 per 1,000 seat-km and international share by GACI ventile |
| ED Fig. 8 Airport concentration | `EDF8_lorenz` (A), `AIRPORT_2023` first 20 rows (B) | Lorenz curves per measure with the diagonal; top-20 bars, blue if `top5` = 1 |
| ED Fig. 9 Reduced-form quintiles, tourism shifter | `EDF9_rf_quintile` | Three panels of `b` with CI by quintile |
| ED Fig. 10 Spillover spatial profile | `EDF10_spill_decay` | Dot-and-whisker by distance band (A) and kernel (B) |
| ED Fig. 11 Permutation placebo | `EDF11_spill_placebo` | Histogram of permuted `t` per `W_label` with a vertical line at `t_actual` |
| ED Fig. 12 Placebo reduced forms | `EDF12_placebo_rf` | Horizontal bars with CIs, aviation outcomes highlighted (`is_aviation` = 1) |

Tables that could also be drawn

- `T1_main`: coefficient plot by outcome and estimator (OLS versus 2SLS, four aggregations).
- `T3_spatial` and `EDT10_spatial_ext`: own beta, neighbour theta, rho and lambda by model, or stacked direct / indirect / total bars.
- `EDT4_mediation`: stacked ACME versus direct effect by mediator.
- `EDT5_decomp_hetero`, `EDT6_airport_hetero`: small-multiple coefficient plots by group.
- `EDT14_attr_sens`: attributed Mt by elasticity rule.

Context sheets

- `PANEL_country_year`: the estimation panel (184 countries, 1996 to 2023) for any time-series or scatter.
- `WORLD_series`: world aviation CO2, traffic and intensity by year.
- `AIRPORT_2023`: all 3,833 airports with positive 2023 emissions, attribution under three elasticity rules, and coordinates (7 airports lack coordinates).

Sheets marked "Reference" in the README are table inputs that do not need a figure.
