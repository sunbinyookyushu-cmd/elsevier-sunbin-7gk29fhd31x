# -*- coding: utf-8 -*-
"""Country GACI x oil shocks using the whole GACI period (user 2026-10-02: "가시 자체는 1996-2024 인데 왜 이렇게 돌렸어?").
81 used GACI 2007 and 2008-2019 (copied from the resilience design). Here:
  A  lagged GACI (ln GACI_cwm in year y-1, updated every year), 1997-2019
  B  lagged GACI, 1997-2024 without 2020-2021 (acute pandemic; same rule as the trade paper)
  C  GACI 1996 fixed, 1997-2019
  D  GACI 1996 fixed, 1997-2024 without 2020-2021
Country GACI data end in 2023 and seats in 2024-06, so lagged GACI covers every outcome month.
Models as in 81: (a) reduced form and IV interaction with country + month FE (controls: ln GDP pc and oil rents of the
same timing, x shock); (b) IV elasticity by GACI tercile (fixed versions C, D only; country FE).
z-scores over the estimation sample. SE country cluster + Newey-West 12.
Output: _res_country_gaci_oil_full.csv
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
cm = pd.read_csv("country_month.csv")
cy = pd.read_csv("country_year.csv", usecols=["c", "y", "ln_gaci_cwm", "lnpc", "oilrent96"]).sort_values(["c", "y"])
lagd = cy[["c", "y", "ln_gaci_cwm", "lnpc"]].copy()
lagd["y"] += 1
cm = cm.merge(lagd.rename(columns={"c": "iso3", "y": "year", "ln_gaci_cwm": "G_lag", "lnpc": "Inc_lag"}), on=["iso3", "year"], how="left")
c96 = cy[cy.y == 1996].set_index("c")
cm["G_96"] = cm.iso3.map(c96.ln_gaci_cwm)
cm["Inc_96"] = cm.iso3.map(c96.lnpc)
cm["Oil"] = cm.iso3.map(cy.drop_duplicates("c").set_index("c").oilrent96)
SH = {"Kaenzig": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
x = "d12_lnjet_l3"
VERS = {"A lagged GACI, 1997-2019": ("G_lag", "Inc_lag", 2019),
        "B lagged GACI, 1997-2024 excl. 2020-21": ("G_lag", "Inc_lag", 2024),
        "C GACI 1996, 1997-2019": ("G_96", "Inc_96", 2019),
        "D GACI 1996, 1997-2024 excl. 2020-21": ("G_96", "Inc_96", 2024)}
OUT = {"y_total": "total seats", "y_domestic": "domestic seats", "y_international": "international seats"}
rows = []
for vl, (gv, iv, yend) in VERS.items():
    d = cm[(cm.year >= 1997) & (cm.year <= yend) & ~cm.year.isin([2020, 2021])].copy()
    for v, src in [("G", gv), ("Inc", iv), ("Oilz", "Oil")]:
        d[v] = (d[src] - d[src].mean()) / d[src].std()
    for s in SH.values():
        d["S_" + s] = d[s] / d.drop_duplicates("t")[s].std()
    for yv, ylab in OUT.items():
        for slab, s in SH.items():
            S = "S_" + s
            for spec, ctr in [("alone", []), ("+ income, oil rents", ["Inc", "Oilz"])]:
                dd = d.dropna(subset=[yv, S, x, "G"] + ctr).copy()
                dd["zG"], dd["xG"] = dd[S] * dd.G, dd[x] * dd.G
                cz = []
                for k in ctr:
                    dd["z" + k] = dd[S] * dd[k]
                    cz.append("z" + k)
                o = fit(dd, yv, exog=["zG"] + cz, fes=["iso3", "t"], vc=("dk", "iso3", "t", 12), return_fs=False)
                rows.append(dict(version=vl, part="(a) reduced form", outcome=ylab, shock=slab, spec=spec, b=o["coef"]["zG"],
                                 se=o["se"]["zG"], p=o["p"]["zG"], F=np.nan, n=o["n"], countries=dd.iso3.nunique()))
                o = fit(dd, yv, endog=["xG"], instr=["zG"], exog=cz, fes=["iso3", "t"], vc=("dk", "iso3", "t", 12))
                rows.append(dict(version=vl, part="(a) IV jet x GACI", outcome=ylab, shock=slab, spec=spec, b=o["coef"]["xG"],
                                 se=o["se"]["xG"], p=o["p"]["xG"], F=o["fs"]["xG"]["F"], n=o["n"], countries=dd.iso3.nunique()))
            if gv == "G_96":
                dd = d.dropna(subset=[yv, S, x, "G"]).copy()
                q = pd.qcut(dd.drop_duplicates("iso3").set_index("iso3").G, 3, labels=["low", "mid", "high"])
                dd["q"] = dd.iso3.map(q)
                en, ins = [], []
                for k in ["low", "mid", "high"]:
                    dd["x_" + k], dd["z_" + k] = dd[x] * (dd.q == k), dd[S] * (dd.q == k)
                    en.append("x_" + k)
                    ins.append("z_" + k)
                o = fit(dd, yv, endog=en, instr=ins, fes=["iso3"], vc=("dk", "iso3", "t", 12))
                for k in ["low", "mid", "high"]:
                    rows.append(dict(version=vl, part="(b) tercile elasticity IV", outcome=ylab, shock=slab, spec=k + " tercile",
                                     b=o["coef"]["x_" + k], se=o["se"]["x_" + k], p=o["p"]["x_" + k], F=o["fs"]["x_" + k]["F"],
                                     n=o["n"], countries=int((dd.drop_duplicates("iso3").q == k).sum())))
    print(vl, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_country_gaci_oil_full.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 400)
print(R.round(4).to_string(index=False))
