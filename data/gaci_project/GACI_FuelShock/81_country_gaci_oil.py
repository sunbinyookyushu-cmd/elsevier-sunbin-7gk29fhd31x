# -*- coding: utf-8 -*-
"""Country level: are countries with higher connectivity (GACI) or resilience more robust to oil price shocks?
(user 2026-10-02). Country x month, 2008-2019, moderators measured in 2007.

Data: country_month.csv (70_country_level.py): D12 ln seats (total / domestic / international), shocks, R_c
      (2007-seat-weighted pre-2008 airport resilience). Country GACI = ln GACI_cwm 2007 from country_year.csv (the
      trade-paper measure); controls ln GDP pc 2007 and oil rents 1996 (z).
(a) Interaction (month FE absorb the common shock):
    D12 ln S_ct = a_c + d_t + g (S_(t-3) x M_c) [+ controls x S] + e        reduced form, S = Kaenzig or BH (1 SD)
    and IV: D12 ln Jet_(t-3) x M_c instrumented by S_(t-3) x M_c.
    M = GACI or resilience (z). g > 0: higher-M countries cut seats less.
(b) Elasticity by tercile of M (no month FE, so the level of each group's response is identified):
    D12 ln S_ct = a_c + sum_k b_k (D12 ln Jet_(t-3) x 1[M_c in tercile k]) + e, instrumented by S x tercile dummies.
    b_k = seat elasticity to the jet fuel price in tercile k.
SE: country cluster + Newey-West 12 (_est "dk").
Output: _res_country_gaci_oil.csv
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
cy = pd.read_csv("country_year.csv", usecols=["c", "y", "ln_gaci_cwm", "lnpc", "oilrent96"])
c07 = cy[cy.y == 2007].set_index("c")
cm["G"] = cm.iso3.map(c07.ln_gaci_cwm)
cm["Inc"] = cm.iso3.map(c07.lnpc)
cm["Oil"] = cm.iso3.map(cy.drop_duplicates("c").set_index("c").oilrent96)
cm["R"] = cm.R_c
d = cm[(cm.year >= 2008) & (cm.year <= 2019)].copy()
base = d.drop_duplicates("iso3")
for v in ["G", "R", "Inc", "Oil"]:
    d[v] = (d[v] - base[v].mean()) / base[v].std()
SH = {"Kaenzig": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
for s in SH.values():
    d["S_" + s] = d[s] / d.drop_duplicates("t")[s].std()
print("countries with G:", base.G.notna().sum(), " with R:", base.R.notna().sum(), " corr(G,R) =",
      round(base[["G", "R"]].corr().iloc[0, 1], 2), " corr(G,Inc) =", round(base[["G", "Inc"]].corr().iloc[0, 1], 2), flush=True)

OUT = {"y_total": "total seats", "y_domestic": "domestic seats", "y_international": "international seats"}
x = "d12_lnjet_l3"
rows = []
for yv, ylab in OUT.items():
    for M in ["G", "R"]:
        for slab, s in SH.items():
            S = "S_" + s
            for spec, ctr in [("alone", []), ("+ income, oil rents", ["Inc", "Oil"])]:
                dd = d.dropna(subset=[yv, S, x, M] + ctr).copy()
                dd["zM"] = dd[S] * dd[M]
                dd["xM"] = dd[x] * dd[M]
                cx, cz = [], []
                for k in ctr:
                    dd["z" + k] = dd[S] * dd[k]
                    cz.append("z" + k)
                o = fit(dd, yv, exog=["zM"] + cz, fes=["iso3", "t"], vc=("dk", "iso3", "t", 12), return_fs=False)
                rows.append(dict(part="(a) reduced form", outcome=ylab, moderator=M, shock=slab, spec=spec, term="shock x M",
                                 b=o["coef"]["zM"], se=o["se"]["zM"], p=o["p"]["zM"], F=np.nan, n=o["n"], countries=dd.iso3.nunique()))
                o = fit(dd, yv, endog=["xM"], instr=["zM"], exog=cz, fes=["iso3", "t"], vc=("dk", "iso3", "t", 12))
                rows.append(dict(part="(a) IV", outcome=ylab, moderator=M, shock=slab, spec=spec, term="jet price x M",
                                 b=o["coef"]["xM"], se=o["se"]["xM"], p=o["p"]["xM"], F=o["fs"]["xM"]["F"], n=o["n"],
                                 countries=dd.iso3.nunique()))
            # (b) tercile elasticities
            dd = d.dropna(subset=[yv, S, x, M]).copy()
            q = pd.qcut(dd.drop_duplicates("iso3").set_index("iso3")[M], 3, labels=["low", "mid", "high"])
            dd["q"] = dd.iso3.map(q)
            en, ins = [], []
            for k in ["low", "mid", "high"]:
                dd["x_" + k] = dd[x] * (dd.q == k)
                dd["z_" + k] = dd[S] * (dd.q == k)
                en.append("x_" + k)
                ins.append("z_" + k)
            o = fit(dd, yv, endog=en, instr=ins, fes=["iso3"], vc=("dk", "iso3", "t", 12))
            for k in ["low", "mid", "high"]:
                rows.append(dict(part="(b) tercile elasticity IV", outcome=ylab, moderator=M, shock=slab, spec=k + " tercile",
                                 term="jet price", b=o["coef"]["x_" + k], se=o["se"]["x_" + k], p=o["p"]["x_" + k],
                                 F=o["fs"]["x_" + k]["F"], n=o["n"], countries=int((dd.drop_duplicates("iso3").q == k).sum())))
R = pd.DataFrame(rows)
R.to_csv("_res_country_gaci_oil.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 300)
print(R.round(4).to_string(index=False))
