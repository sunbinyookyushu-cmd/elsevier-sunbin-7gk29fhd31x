# -*- coding: utf-8 -*-
"""Country x year (as in the GACI trade paper): does air connectivity buffer economies against oil and geopolitical
shocks? (user 2026-10-02: "컨트리레벨 에그리게이트 해서 추정 가능? trade 때처럼")

Panel: country_year.csv (03_build_country_year.py; GACI_CO2 panel + fuel series), 1997-2019 (pre-Covid).
Outcomes (first differences): trade openness (trade_share, pp of GDP), ln trade volume, ln GDP, ln GDP per capita.
Moderator: H = z-score of ln GACI_cwm 1996 (pre-determined); controls interacted with the same shock: oil rents 1996
           and ln GDP pc 1996 (z), so H is not "rich" or "oil exporter".
(O) oil:  d Y_cy = a_c + d_y + g (S_y x H_c) + th (S_y x Oil_c) + k (S_y x Inc_c) + e
          S_y = annual change in the cumulated Kaenzig news shock or sign-flipped BH supply shock (as in 11),
          scaled to 1 SD; common shock, so only the interactions are identified.
(G) geopolitical, 44 GPR countries: d Y_cy = a_c + d_y + b GPR_cy + g (GPR_cy x H_c) + controls x GPR + e
          GPR_cy = annual mean ln GPRC, z-scored within country (own history 1990-2019), contemporaneous and lag 1.
g > 0: better-connected economies lose less (or gain more) when the shock hits.
SE: country cluster + Newey-West over years (L = 2) (_est "dk").
Output: _res_country_econ_buffer.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import warnings

import numpy as np
import pandas as pd
from _est import fit

warnings.filterwarnings("ignore")
c = pd.read_csv("country_year.csv").sort_values(["c", "y"])
c = c[c.ln_gaci_cwm96.notna()].copy()
for v in ["trade_share", "ln_tradevol", "lngdp", "lnpc"]:
    c["d_" + v] = c.groupby("c")[v].diff()
    c.loc[c.groupby("c").y.diff() != 1, "d_" + v] = np.nan
base = c.drop_duplicates("c")
z = lambda v: (c[v] - base[v].mean()) / base[v].std()
c["H"] = z("ln_gaci_cwm96")
c["Oil"] = z("oilrent96")
c["Inc"] = z("lnpc96")
d = c[(c.y >= 1997) & (c.y <= 2019)].copy()
for s in ["d_kz_cum", "d_bh_neg_cum"]:
    d["S_" + s] = d[s] / d.drop_duplicates("y")[s].std()

# GPR annual, 44 countries
g = pd.read_excel("data_external/data_gpr_export.xls")
g["year"] = pd.to_datetime(g.month).dt.year
g = g[(g.year >= 1990) & (g.year <= 2019)]
cols = [k for k in g.columns if str(k).startswith("GPRC_")]
ga = g.groupby("year")[cols].mean().reset_index().melt(id_vars="year", var_name="k", value_name="v")
ga["c"] = ga.k.str[5:]
ga["lv"] = np.log(ga.v.where(ga.v > 0))
ga["gpr"] = ga.groupby("c").lv.transform(lambda s: (s - s.mean()) / s.std())
ga = ga.sort_values(["c", "year"])
ga["gpr_l1"] = ga.groupby("c").gpr.shift(1)
d = d.merge(ga[["c", "year", "gpr", "gpr_l1"]].rename(columns={"year": "y"}), on=["c", "y"], how="left")

OUT = {"d_trade_share": "trade openness (pp)", "d_ln_tradevol": "ln trade volume", "d_lngdp": "ln GDP", "d_lnpc": "ln GDP pc"}
rows = []
for yv, ylab in OUT.items():
    for slab, s in [("Kaenzig", "S_d_kz_cum"), ("BH", "S_d_bh_neg_cum")]:
        for spec, mods in [("H only", ["H"]), ("H + oil + income", ["H", "Oil", "Inc"])]:
            dd = d.dropna(subset=[yv, s] + mods).copy()
            xs = []
            for m in mods:
                dd["x_" + m] = dd[s] * dd[m]
                xs.append("x_" + m)
            o = fit(dd, yv, exog=xs, fes=["c", "y"], vc=("dk", "c", "y", 2), return_fs=False)
            rows.append(dict(shock=slab, outcome=ylab, spec=spec, term="shock x GACI", b=o["coef"]["x_H"], se=o["se"]["x_H"],
                             p=o["p"]["x_H"], n=o["n"], countries=dd.c.nunique()))
    for lab, gv in [("GPR (t)", "gpr"), ("GPR (t-1)", "gpr_l1")]:
        for spec, mods in [("H only", ["H"]), ("H + oil + income", ["H", "Oil", "Inc"])]:
            dd = d.dropna(subset=[yv, gv] + mods).copy()
            xs = [gv]
            for m in mods:
                dd["x_" + m] = dd[gv] * dd[m]
                xs.append("x_" + m)
            o = fit(dd, yv, exog=xs, fes=["c", "y"], vc=("dk", "c", "y", 2), return_fs=False)
            for term, v in [("GPR main effect", gv), ("GPR x GACI", "x_H")]:
                rows.append(dict(shock=lab, outcome=ylab, spec=spec, term=term, b=o["coef"][v], se=o["se"][v],
                                 p=o["p"][v], n=o["n"], countries=dd.c.nunique()))
R = pd.DataFrame(rows)
R.to_csv("_res_country_econ_buffer.csv", index=False)
pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
