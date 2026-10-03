# -*- coding: utf-8 -*-
# NOTE (package copy, 11 Sep 2026): only the path lines were changed so the
# script finds its inputs in this flat folder. The figure code is untouched.
"""Mismatch descriptives, 2023: (A) where aviation emissions occur (bunker
allocation, Mt, log colour scale); (B) the allocation mismatch itself =
cruise attributed by fuel uplift minus cruise attributed by arrival
(dep_cruise - arr_cruise, Mt): positive = net fuel-uplift exporter (hubs).
Run with cwd = GACI folder (needs _world.geojson, _mapstyle.py there);
outputs land in GACI_CO2."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm

GACI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GACI)
import _mapstyle as ms

d = pd.read_csv(os.path.join(GACI, "co2_country_year.csv"))
d = d[d.year == 2023].copy()
d["bunker_mt"] = d.co2_bunker / 1e9
d["log_bunker"] = np.log10(d.bunker_mt.clip(lower=1e-3))
# note: dep_cruise - arr_cruise nets to ~0 by round-trip symmetry (checked);
# the substantive mismatch is attributed (bunker) share vs physical LTO share.
d["gap_pp"] = 100 * (d.co2_bunker / d.co2_bunker.sum()
                     - d.co2_lto / d.co2_lto.sum())
d["gap_mt"] = (d.dep_co2_cruise_kg - d.arr_co2_cruise_kg) / 1e9

df = d[["iso3", "bunker_mt", "log_bunker", "gap_pp", "gap_mt"]].rename(columns={"iso3": "c"})
w = ms.load_world(df)

# (A) levels, log colour scale
norm = Normalize(vmin=-2, vmax=np.log10(250))
ticks = [np.log10(v) for v in (0.01, 0.1, 1, 10, 100)]
ms.render(w, "log_bunker", "YlGnBu", norm,
          "Aviation CO$_2$, 2023 (Mt, fuel-uplift allocation)",
          os.path.join(GACI, "CO2_map_levels_2023.png"),
          ticks=ticks, tickfmt=lambda x, _: f"{10**x:g}")

# (B) allocation mismatch: attributed (bunker) share minus physical LTO share
lim = float(np.nanquantile(np.abs(w.gap_pp.dropna()), 0.995))
norm2 = TwoSlopeNorm(vmin=-lim, vcenter=0.0, vmax=lim)
ms.render(w, "gap_pp", "RdBu_r", norm2,
          "World share, attributed minus physical LTO (pp, 2023)",
          os.path.join(GACI, "CO2_map_mismatch_2023.png"),
          signed=True, tickfmt=lambda x, _: f"{x:+.1f}" if x else "0")

top = d.nlargest(8, "gap_pp")[["iso3", "gap_pp"]]
bot = d.nsmallest(8, "gap_pp")[["iso3", "gap_pp"]]
print("attribution >> physical LTO (pp):", [(r.iso3, round(r.gap_pp, 2)) for r in top.itertuples()])
print("physical LTO >> attribution (pp):", [(r.iso3, round(r.gap_pp, 2)) for r in bot.itertuples()])
print("round-trip netting check, |dep-arr cruise| max (Mt):",
      round(d.gap_mt.abs().max(), 2))
