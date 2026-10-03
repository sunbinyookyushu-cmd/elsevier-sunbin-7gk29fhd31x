# -*- coding: utf-8 -*-
# NOTE (package copy, 11 Sep 2026): only the path lines were changed so the
# script finds its inputs in this flat folder. The figure code is untouched.
"""Rebuild CO2_map_attributed_2023.png from _attribution_scc.csv (Feyrer
beta 5.669 series, replacing the tourism-beta series the map used before).
Same style as 10_extra_maps.py panel A: signed asinh scale, 0 = white.
Run with cwd = GACI folder (needs _world.geojson, _mapstyle.py)."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib.colors import FuncNorm

GACI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GACI)
import _mapstyle as ms

d = pd.read_csv(os.path.join(GACI, "_attribution_scc.csv"))
d["att_mt"] = d.att_tot_t / 1e6

w = ms.load_world(d[["c", "att_mt"]])
s = 2.0  # asinh scale (Mt); China +87.7 vs median ~0.1
fwd = lambda x: np.arcsinh(np.asarray(x, dtype=float) / s)
inv = lambda x: s * np.sinh(np.asarray(x, dtype=float))
w["att_t"] = fwd(w.att_mt)
lim = float(np.nanmax(np.abs(w.att_t)))
norm = FuncNorm((lambda x: x, lambda x: x), vmin=-lim, vmax=lim)
tickvals = [-16, -4, 0, 4, 16, 88]
ms.render(w, "att_t", "RdBu_r", norm,
          "CO$_2$ attributable to 1996-2023 connectivity growth (Mt)",
          os.path.join(GACI, "CO2_map_attributed_2023.png"),
          ticks=fwd(tickvals),
          tickfmt=lambda x, _: f"{inv([x])[0]:+,.0f}" if abs(inv([x])[0]) > 0.5 else "0")
print("map rebuilt")
top = d.nlargest(6, "att_mt")[["c", "att_mt"]]
print("largest:", [(r.c, round(r.att_mt, 1)) for r in top.itertuples()])
