# -*- coding: utf-8 -*-
"""Maps for the inequality paper, in the shared GACI map style (../_mapstyle.py).

  fig_map_implied_gini.png : GACI-induced change in the market Gini, 1996-2023,
                             OLS coefficient (0.061) applied to each country's
                             change in ln GACI_max  (= ols_pts in _contribution_bycountry.csv)
  fig_map_base_gacimax.png : hub connectivity, ln GACI_max, 2023 (base map, as in the trade paper)
  fig_map_actual_gini.png  : observed change in the market Gini over the same window (option)
"""
import os, sys
import numpy as np, pandas as pd
from matplotlib.colors import Normalize, TwoSlopeNorm

HERE = os.path.dirname(os.path.abspath(__file__))
GACI = os.path.dirname(HERE)
sys.path.insert(0, GACI)
os.chdir(GACI)                      # _mapstyle reads _world.geojson from the GACI folder
import _mapstyle as ms

cb = pd.read_csv(os.path.join(HERE, "_contribution_bycountry.csv"), keep_default_na=False)
for col in ["dln_gaci", "ols_pts", "iv_pts", "actual_pts", "gini0", "gini1"]:
    cb[col] = pd.to_numeric(cb[col], errors="coerce")

# ---- 1. implied change in market Gini (OLS), points -------------------------
d = cb[["c", "ols_pts"]].rename(columns={"ols_pts": "val"})
V = float(np.nanmax(np.abs(d["val"])))
norm = TwoSlopeNorm(vmin=-V, vcenter=0.0, vmax=V)
w = ms.load_world(d)
ms.render(w, "val", "RdBu_r", norm,
          "Implied change in market Gini, 1996--2023 (points, OLS)",
          os.path.join(HERE, "fig_map_implied_gini.png"),
          ticks=[-2, -1, 0, 1, 2], signed=True,
          tickfmt=lambda x, _: "0" if x == 0 else f"{x:+.0f}")
print("implied: range %.2f to %.2f, n=%d" % (d.val.min(), d.val.max(), d.val.notna().sum()))
print("  top:", cb.nlargest(6, "ols_pts")[["c", "ols_pts"]].round(2).values.tolist())

# ---- 2. base map: hub connectivity 2023 ---------------------------------------
p = pd.read_csv(os.path.join(HERE, "ineq_panel.csv"), usecols=["c", "y", "ln_gaci_max"])
b = p[p.y == 2023][["c", "ln_gaci_max"]].dropna().rename(columns={"ln_gaci_max": "val"})
norm2 = Normalize(vmin=float(b.val.min()), vmax=float(b.val.max()))
w2 = ms.load_world(b)
ms.render(w2, "val", "viridis", norm2,
          "Hub connectivity, $\\ln(\\mathrm{GACI}_{\\mathrm{max}})$, 2023",
          os.path.join(HERE, "fig_map_base_gacimax.png"),
          tickfmt=lambda x, _: f"{x:.1f}")
print("base: range %.2f to %.2f, n=%d" % (b.val.min(), b.val.max(), len(b)))

# ---- 3. option: observed change in market Gini over the same window -----------
a = cb[["c", "actual_pts"]].rename(columns={"actual_pts": "val"})
Va = float(np.nanmax(np.abs(a["val"])))
norm3 = TwoSlopeNorm(vmin=-Va, vcenter=0.0, vmax=Va)
w3 = ms.load_world(a)
ms.render(w3, "val", "RdBu_r", norm3,
          "Observed change in market Gini, 1996--2023 (points)",
          os.path.join(HERE, "fig_map_actual_gini.png"),
          signed=True, tickfmt=lambda x, _: "0" if x == 0 else f"{x:+.0f}")
print("actual: range %.1f to %.1f" % (a.val.min(), a.val.max()))
