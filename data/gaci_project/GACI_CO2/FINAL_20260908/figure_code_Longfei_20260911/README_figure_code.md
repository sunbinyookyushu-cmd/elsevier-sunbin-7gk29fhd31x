# GACI x CO2 — figure code, 11 September 2026

Code behind the fifteen figures in the 8 September manuscript
(`main_co2_nature_20260908.tex`): three in the main text, twelve in Extended Data.
Everything needed to redraw them is in this one flat folder, so each script runs
where it sits:

```
cd figure_code_Longfei_20260911
set CLSUF=_cl          # Windows;  export CLSUF=_cl  on macOS/Linux
python 18_decomp_table_fig.py
```

`CLSUF=_cl` selects the country-clustered result files, which are the ones the
manuscript reports. Leaving it unset draws the heteroskedasticity-robust
variants (same layout, different confidence intervals) from the unsuffixed
files, which are also included; those are not the manuscript figures. Run on Python 3.13.5
with pandas 2.3.1, numpy 2.3.2, matplotlib 3.10.8, geopandas 1.1.2 (maps and
`21b` only) and pyfixest 0.40.1 (`21b` only).

Every figure in `figures_current/` was regenerated from this folder on
11 September and came out byte-identical to the file in the manuscript, so what
is here is exactly what produced the current versions.

## Which script draws which figure

| Display | File | Script (line of the `savefig`) | Inputs it reads |
|---|---|---|---|
| Fig. 1 | CO2_hetero_coefplot.png | `18_decomp_table_fig.py` (182) | `_feyrer_hetero_tot_cl.csv` |
| Fig. 2 | CO2_map_attributed_2023.png | `15_remake_attributed_map.py` + `_mapstyle.py` (84) | `_attribution_scc.csv`, `_world.geojson` |
| Fig. 3 | CO2_saf_growth.png | `31_saf_growth.py` (137) | `_allest_results_cl.csv`, `_temporal_excovid_cl.csv`, `_attribution_scc.csv`, `co2_country_year.csv` |
| ED 1 | CO2_temporal_coefplot.png | `build_hetero_temporal_figs.py` (105) | `_temporal_co2_cl.csv`, `_temporal_pre2008_cl.csv`, `_temporal_excovid_cl.csv` |
| ED 2 | CO2_decomp_waterfall.png | `18_decomp_table_fig.py` (105) | `_feyrer_mechanism_cl.csv` |
| ED 3 | CO2_gradient_baseline.png | `29_yifu_gradient_attribution.py` (131) | `_yifu_suite_cl.csv`, `gaci_panel_combined.csv` |
| ED 4 | CO2_attribution_bars.png | `16_attribution_bars.py` (67) | `_attribution_scc.csv` |
| ED 5 | CO2_map_levels_2023.png | `05_mismatch_maps.py` + `_mapstyle.py` (84) | `co2_country_year.csv`, `_world.geojson` |
| ED 6 | CO2_map_mismatch_2023.png | `05_mismatch_maps.py`, same run | `co2_country_year.csv`, `_world.geojson` |
| ED 7 | CO2_efficiency_curve.png | `build_efficiency_curve_fig.py` (57) | `airport_co2_panel.csv` |
| ED 8 | CO2_airport_concentration.png | `19_airport_concentration.py` (103) | `airport_co2_panel.csv`, `_airport_groups.csv`, `_attribution_scc.csv` |
| ED 9 | CO2_rf_quintile.png | `build_co2_rf_quintile_fig.py` (51) | `_co2_rf_quintile_intl.csv` |
| ED 10 | CO2_spill_decay.png | `24_spill_tables_figs.py` (162) | `_spill_bands_cl.csv`, `_spill_supp.csv` |
| ED 11 | CO2_spill_placebo.png | `21b_perm_contig.py` (153), or `fig_spill_placebo_replot.py` | `_spill_placebo_perm_W.csv`, `_spill_placebo_summary.csv`, `_spill_placebo_perm.csv` |
| ED 12 | CO2_placebo_rf.png | `23_exclusion_tables.py` (141) | `_exclusion_suite_cl.csv` |

Several of these scripts build the LaTeX tables as well as the figure; the
plotting block is the tail of each file, at the line given above.

Two things worth knowing before running them:

- `21b_perm_contig.py` draws ED Fig. 11 only after re-running 500 permutations
  of the weight matrix for two specifications, which takes about half an hour
  and needs geopandas, pycountry and pyfixest. `fig_spill_placebo_replot.py` is
  the same plotting block reading the permutation draws `21b` already saved, so
  it redraws the figure in a second. That replot file is the one thing here that
  was written for this package rather than lifted from the pipeline.
- `build_hetero_temporal_figs.py` also writes `_unused_hetero_from_old_script.png`.
  That is a superseded version of the heterogeneity panel; the manuscript's
  Fig. 1 comes from `18_decomp_table_fig.py`. Ignore the file.

## House style

All fifteen figures share one set of conventions, in case you want the new
visualizations to sit alongside them:

```python
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"],
                     "font.size": 11, "axes.linewidth": 0.8,
                     "mathtext.fontset": "stix"})
ACC, GRAY, INK, NEG = "#1F4E79", "#9AA0A6", "#1f1f1f", "#B5651D"
```

Blue `#1F4E79` carries the estimate, grey `#9AA0A6` the comparison or null
series, `#B5651D` a negative or contrasting one; near-black `#1f1f1f` for text.
Coefficient panels drop the top and right spines, put a dashed grey line at
zero, use filled markers for p < 0.05 and hollow otherwise, and carry 95 percent
confidence intervals. Panel titles are left-aligned at font size 11. Figures are
saved at dpi 200 (the waterfall at 220) on a white face.

The three maps go through `_mapstyle.py`: Robinson projection, Natural Earth
geometry from `_world.geojson`, `#ededed` for countries outside the sample,
`#b3b8bd` outlines, and a tall vertical colour bar in a reserved right-hand
strip. Levels use `YlGnBu` on a log scale; signed quantities use `RdBu_r`
centred on white at zero, with an asinh scale on the attribution map so China
does not flatten everything else. Taiwan is drawn with the mainland values so
China reads as one unit (`unify_china`).

## Folder

- `*.py` — the thirteen pipeline scripts, plus `_mapstyle.py` and the replot helper.
- `*.csv` — every result file the scripts read. Files ending `_cl` are the
  country-clustered versions the manuscript reports; the same names without the
  suffix are the robust versions.
- `co2_country_year.csv`, `airport_co2_panel.csv`, `spillover_bands.csv`,
  `gaci_panel_combined.csv`, `airport_coords_merged.csv` — the underlying panels.
- `_world.geojson`, `data_external/ne_50m_admin_0.geojson` — map geometry.
- `figures_current/` — the fifteen PNGs as they stand in the manuscript.

The only edits made to the original scripts were the path lines, so that each
one finds its inputs in this flat folder and runs on Windows, macOS or Linux; the files carry a note at the top
saying so. The plotting code is untouched. If you would rather work from the
plotted series than from the scripts, `CO2_visualization_data_20260908.xlsx`
(sent on 8 September) has one sheet per display.
