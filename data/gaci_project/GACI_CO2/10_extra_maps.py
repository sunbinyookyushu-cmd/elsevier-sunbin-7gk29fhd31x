# -*- coding: utf-8 -*-
"""Extra attribution maps, trade-paper format (_mapstyle): (A) emissions
attributable to 1996-2023 connectivity growth (Mt, signed, asinh colour
scale); (B) connectivity growth itself (dln GACI, signed); (C) carbon-price
of connectivity-driven trade gains (g CO2 per USD, log colour scale).
Run with cwd = GACI folder (needs _world.geojson, _mapstyle.py there);
outputs land in GACI_CO2."""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm, FuncNorm

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
sys.path.insert(0, GACI)
import _mapstyle as ms

d = pd.read_csv(GACI + r"\GACI_CO2\_carbon_price_bycountry.csv")
d["att_mt"] = d.att_co2_tot_t / 1e6
d["cp_log"] = np.log10(d.cp_g_per_usd.where(d.cp_g_per_usd > 0))

w = ms.load_world(d[["c", "att_mt", "dln_cwm", "cp_log"]])

# (A) attributable emissions, signed asinh scale (China 32.9 Mt vs median ~0.03);
# colour the arcsinh transform with a TwoSlopeNorm so white sits exactly at 0
s = 0.5  # linear width around zero, Mt
fwd = lambda x: np.arcsinh(np.asarray(x, dtype=float) / s)
w["att_t"] = fwd(w.att_mt)
norm = TwoSlopeNorm(vmin=float(fwd(-3.0)), vcenter=0.0, vmax=float(fwd(35.0)))
tickvals = [-3, -1, 0, 1, 3, 10, 30]
ms.render(w, "att_t", "RdBu_r", norm,
          "CO$_2$ attributable to 1996-2023 connectivity growth (Mt)",
          GACI + r"\GACI_CO2\CO2_map_attributed_2023.png",
          ticks=[float(fwd(v)) for v in tickvals], signed=True,
          tickfmt=lambda x, _: (lambda v: f"{v:+g}" if round(v, 2) else "0")(np.sinh(x) * s))

# (B) connectivity growth, dln GACI 1996-2023
lim2 = float(np.nanquantile(np.abs(w.dln_cwm.dropna()), 0.995))
norm2 = TwoSlopeNorm(vmin=-lim2, vcenter=0.0, vmax=lim2)
ms.render(w, "dln_cwm", "RdBu_r", norm2,
          "Hub-quality growth, 1996-2023 ($\\Delta$ln GACI)",
          GACI + r"\GACI_CO2\CO2_map_dlngaci.png",
          signed=True, tickfmt=lambda x, _: f"{x:+.2f}" if x else "0")

# (C) implied carbon price of the trade gains, g CO2 per USD, log scale
norm3 = Normalize(vmin=0, vmax=np.log10(550))
ticks3 = [np.log10(v) for v in (1, 3, 10, 30, 100, 300)]
ms.render(w, "cp_log", "YlOrRd", norm3,
          "Attributed CO$_2$ per dollar of attributed trade (g/USD)",
          GACI + r"\GACI_CO2\CO2_map_carbonprice.png",
          ticks=ticks3, tickfmt=lambda x, _: f"{10**x:g}")

for col, name in [("att_mt", "attributable Mt"), ("dln_cwm", "dln GACI"),
                  ("cp_log", "log10 g/USD")]:
    v = d[col].dropna()
    print(f"{name}: n = {len(v)}, min = {v.min():.2f}, max = {v.max():.2f}")
top = d.nlargest(6, "att_mt")[["c", "att_mt"]]
print("largest attributable:", [(r.c, round(r.att_mt, 1)) for r in top.itertuples()])
