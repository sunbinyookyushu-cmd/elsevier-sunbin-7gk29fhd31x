# -*- coding: utf-8 -*-
"""45_maps_incidence.py : world maps of the GACI-induced distributional change, 1996 to latest year, in the
   shared GACI map style (../_mapstyle.py: Times, Robinson, right-hand legend).
     fig_map_induced_gini_2sls.png  : implied change in the market Gini (points) = Gini0 x (exp(0.495 x dln GACI_max) - 1)
     fig_map_induced_b50share.png   : implied change in the bottom-50% pretax income share (points of national income)
                                      = share0 x 100 x (exp(-0.774 x dln GACI_max) - 1)
     fig_map_hub_growth.png         : the driver, change in ln GACI_max over the country's window
   Inputs: _aggregate_curve_bycountry.csv (21_aggregate_curve.py). Countries with >= 15 years of data."""
import os, sys, numpy as np, pandas as pd
from matplotlib.colors import TwoSlopeNorm, Normalize
HERE = os.path.dirname(os.path.abspath(__file__)); GACI = os.path.dirname(HERE)
sys.path.insert(0, GACI); os.chdir(GACI)
import _mapstyle as ms
a = pd.read_csv(os.path.join(HERE, "_aggregate_curve_bycountry.csv"))
a = a.rename(columns={"implied_dgini_pts": "gini_pts", "implied_dshare_pts_b50": "b50_pts", "dln_gaci": "dlng"})
print(a[["gini_pts", "b50_pts", "dlng"]].describe().round(2).to_string())
# 1. induced Gini change (2SLS), points; diverging, symmetric around 0, clipped at the 95th pct for legibility
d = a[["c", "gini_pts"]].rename(columns={"gini_pts": "val"}); lim = float(np.nanpercentile(np.abs(d.val), 95))
w = ms.load_world(d)
ms.render(w, "val", "RdBu_r", TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim), "Implied change in market Gini, 1996–2023 (pts)",
          os.path.join(HERE, "fig_map_induced_gini_2sls.png"), signed=True)
# 2. induced change in bottom-50 share, points of national income
d = a[["c", "b50_pts"]].rename(columns={"b50_pts": "val"}); lim = float(np.nanpercentile(np.abs(d.val), 95))
w = ms.load_world(d)
ms.render(w, "val", "RdBu", TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim), "Implied change in bottom-50% share, 1996–2023 (pts)",
          os.path.join(HERE, "fig_map_induced_b50share.png"), signed=True)
# 3. the driver: hub growth
d = a[["c", "dlng"]].rename(columns={"dlng": "val"}); lim = float(np.nanpercentile(np.abs(d.val), 97))
w = ms.load_world(d)
ms.render(w, "val", "PuOr_r", TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim), "Change in ln hub connectivity (GACI$_{max}$), 1996–2023",
          os.path.join(HERE, "fig_map_hub_growth.png"), signed=True)
print("saved 3 maps")
