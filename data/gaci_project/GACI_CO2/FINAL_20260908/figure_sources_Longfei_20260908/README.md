# Figure sources (8 September 2026)

Two required figures (Fig. 1 and Fig. 2) and five optional Extended Data figures (ED Fig. 1, 2, 3, 5, 6). One sheet per figure, except that the three country maps share one sheet in `figure_sources_20260908.xlsx`; the README sheet gives the manuscript caption and plotting instructions. `current_drafts/` holds the present matplotlib versions for layout reference; `ne_50m_admin_0.geojson` is the boundary file for the maps.

## Fig. 1 (REQUIRED) - sheet `Fig1_hetero`

Caption: Heterogeneity of the connectivity elasticity (2SLS, Feyrer instrument; total bunker CO2 in panels A-C, CO2 per seat-km in panel D). Filled markers denote p<0.05; bars are 95 percent confidence intervals. The Middle East and North America are omitted as unidentified.

Plot: Four dot-and-whisker panels (panel / panel_label; order_in_panel gives the row order). x = b with ci_lo-ci_hi; filled marker if sig05 = 1, hollow otherwise; vertical dashed line at 1 (proportional growth) and at 0. Panels A-C share the total-CO2 axis; panel D (intensity) has its own axis.

Draft: `current_drafts/CO2_hetero_coefplot.png`

## Fig. 2 (REQUIRED) - sheet `Maps_country_2023`

Caption: Aviation CO2 attributed to post-1996 connectivity growth, 2023 (Mt). White denotes zero; the attribution applies the Feyrer-instrument elasticity to each country's connectivity change.

Plot: World choropleth keyed on iso3 (ISO_A3 in the geojson). Colour = att_tot_mt with a diverging scale centred at zero (asinh_att_mt_s2 is a ready-made asinh transform for the colour scale; label the colour bar in Mt). Countries with in_attribution_sample = 0 or att_tot_mt = 0 in white. att_share_pct is the country's own attributed share (for hover/labels).

Draft: `current_drafts/CO2_map_attributed_2023.png`

## Extended Data Fig. 5 (optional) - sheet `Maps_country_2023`

Caption: Aviation CO2 levels under the bunker convention, 2023.

Plot: Choropleth of bunker_mt_2023 on a log scale (log10_bunker_mt provided); same boundary file as Fig. 2.

Draft: `current_drafts/CO2_map_levels_2023.png`

## Extended Data Fig. 6 (optional) - sheet `Maps_country_2023`

Caption: Attribution mismatch, 2023: bunker-attributed share minus physical LTO share (percentage points). Positive values indicate long-haul, cruise-heavy networks; negative values indicate short-haul, domestically oriented networks.

Plot: Diverging choropleth of mismatch_pp = share_bunker_pct minus share_lto_pct (percentage points of the world total), centred at zero: positive where booked (bunker) share exceeds the physical LTO share (long-haul hubs), negative where short-haul domestic flying dominates.

Draft: `current_drafts/CO2_map_mismatch_2023.png`

## Extended Data Fig. 1 (optional) - sheet `ED1_temporal`

Caption: Temporal split of the connectivity elasticity. Within each outcome, markers show the full sample, the network-expansion era (1996-2007), the mature-network era (2010-2023 excluding the COVID-19 years 2020-2021), and the unrestricted 2010-2023 sample from left to right; gray denotes the unrestricted later sample, whose first stage (KP F = 3.2) is contaminated by the COVID collapse. Bars are 95 percent confidence intervals with standard errors clustered by country.

Plot: Dot-and-whisker grouped by outcome_label, one marker per period in the given order; grey marker if weak_first_stage = 1; line at 1.

Draft: `current_drafts/CO2_temporal_coefplot.png`

## Extended Data Fig. 2 (optional) - sheet `ED2_waterfall`

Caption: Decomposition of the CO2 elasticity on the accounting identity. Each bar is the 2SLS elasticity of the component with respect to connectivity (Feyrer instrument; 95 percent confidence intervals); the components add exactly to the total. Scale is the sum of the first three bars.

Plot: Waterfall in the given order: bars from waterfall_start to waterfall_end (scale components, then intensity, then total); share_of_total_pct as bar labels.

Draft: `current_drafts/CO2_decomp_waterfall.png`

## Extended Data Fig. 3 (optional) - sheet `ED3_gradient`

Caption: The elasticity along the baseline-connectivity distribution. Quintile split-sample 2SLS estimates (points, 95 percent confidence intervals; the fourth quintile is unidentified and omitted) and the fitted elasticity from pooled specifications that interact log GACI with centred log baseline GACI (linear, dashed; quadratic with 95 percent band). Horizontal lines mark zero and one.

Plot: Quintile points (series = quintile) with ci_lo-ci_hi at baseline_gaci_mean, plus fitted curves (series = linear / quadratic) over baseline_gaci; unidentified quintile shown hollow/grey.

Draft: `current_drafts/CO2_gradient_baseline.png`
