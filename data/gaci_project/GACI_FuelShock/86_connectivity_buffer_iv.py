# -*- coding: utf-8 -*-
"""Does air connectivity make economies less exposed to oil and geopolitical shocks? Trade-paper design
(user 2026-10-02: "설명변수를 연결성으로 되돌리기(무역식) ... 한번 해볼까").

Panel and IV exactly as the GACI trade paper (GACI/ext2024/gaci_panel_3iv.csv, 185 countries, 1996-2024):
  baseline:  Y_cy = a_c + d_y + b lnGACI_cy + lnPop_cy + e,   lnGACI instrumented by tourism_int (heritage Bartik)
  here:      Y_cy = a_c + d_y + b G_cy + g (G_cy x S_cy) [+ h S_cy] + lnPop_cy [+ S x Inc96 + S x Oil96] + e
             endogenous G and G x S, instruments tourism_int and tourism_int x S (G, tourism_int centred).
  Y: trade openness g_int = ln(goods trade / GDP) (main outcome of the trade paper), ln trade volume g_vol, ln GDP.
  S: (oil) annual sum of Kaenzig news shocks or sign-flipped BH supply shocks, z-scored over 1996-2024 (common to all
     countries: only g identified, h absorbed by year FE);
     (geopolitical) country GPR, annual mean ln GPRC z-scored within country (42 countries in the panel; h identified).
  g > 0: when the shock hits, more connected countries keep more trade / output.
  Samples: full 1996-2024 (trade-paper main) and without 2020-21.
  SE: robust (trade-paper convention) and clustered by country (reported alongside).
Output: _res_connectivity_buffer_iv.csv
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
d = pd.read_csv(r"..\ext2024\gaci_panel_3iv.csv")
d["g_int"], d["g_vol"], d["g_gdp"] = d.merch_intensity, d.merch_intensity + d.lngdp, d.lngdp
d["G"] = d.ln_gaci_cwm - d.ln_gaci_cwm.mean()
d["Z"] = d.tourism_int - d.tourism_int.mean()
d["rid"] = np.arange(len(d))
base = pd.read_csv("country_year.csv", usecols=["c", "lnpc96", "oilrent96"]).drop_duplicates("c").set_index("c")
for v, src in [("Inc", "lnpc96"), ("Oil", "oilrent96")]:
    s = d.c.map(base[src])
    d[v] = (s - s.mean()) / s.std()

fa = pd.read_csv("fuel_annual.csv", usecols=["year", "kz", "bh_neg"]).set_index("year")
w = fa.loc[1996:2024]
for s in ["kz", "bh_neg"]:
    d["S_" + s] = d.y.map((fa[s] - w[s].mean()) / w[s].std())
g = pd.read_excel("data_external/data_gpr_export.xls")
g["year"] = pd.to_datetime(g.month).dt.year
g = g[(g.year >= 1990) & (g.year <= 2024)]
cols = [k for k in g.columns if str(k).startswith("GPRC_")]
ga = g.groupby("year")[cols].mean().reset_index().melt(id_vars="year", var_name="k", value_name="v")
ga["c"] = ga.k.str[5:]
ga["lv"] = np.log(ga.v.where(ga.v > 0))
ga["S_gpr"] = ga.groupby("c").lv.transform(lambda s: (s - s.mean()) / s.std())
d = d.merge(ga[["c", "year", "S_gpr"]].rename(columns={"year": "y"}), on=["c", "y"], how="left")

OUT = {"g_int": "trade openness", "g_vol": "ln trade volume", "g_gdp": "ln GDP"}
SH = {"oil, Kaenzig": ("S_kz", False), "oil, BH": ("S_bh_neg", False), "geopolitical (country GPR)": ("S_gpr", True)}
rows = []
for samp, keep in [("full 1996-2024", d.y.between(1996, 2024)), ("without 2020-21", d.y.between(1996, 2024) & ~d.y.isin([2020, 2021]))]:
    D0 = d[keep]
    for yv, ylab in OUT.items():
        o = fit(D0.dropna(subset=[yv, "G", "Z", "lnpop"]), yv, endog=["G"], instr=["Z"], exog=["lnpop"], fes=["c", "y"],
                vc=("cl", "rid"), vc_alt=[("cl", "c")])
        rows.append(dict(sample=samp, outcome=ylab, shock="none (trade-paper baseline)", spec="baseline", term="lnGACI",
                         b=o["coef"]["G"], se_rob=o["se"]["G"], p_rob=o["p"]["G"], se_cl=o["alt"][0]["se"]["G"],
                         p_cl=o["alt"][0]["p"]["G"], F=o["fs"]["G"]["F"], n=o["n"]))
        for slab, (s, has_main) in SH.items():
            for spec, ctr in [("IV", []), ("IV + S x income, S x oil rents", ["Inc", "Oil"])]:
                D = D0.dropna(subset=[yv, "G", "Z", "lnpop", s] + ctr).copy()
                D["GS"], D["ZS"] = D.G * D[s], D.Z * D[s]
                ex = ["lnpop"] + ([s] if has_main else [])
                for k in ctr:
                    D["c_" + k] = D[s] * D[k]
                    ex.append("c_" + k)
                o = fit(D, yv, endog=["G", "GS"], instr=["Z", "ZS"], exog=ex, fes=["c", "y"], vc=("cl", "rid"), vc_alt=[("cl", "c")])
                terms = [("lnGACI", "G"), ("lnGACI x shock", "GS")] + ([("shock", s)] if has_main else [])
                for tl, tv in terms:
                    rows.append(dict(sample=samp, outcome=ylab, shock=slab, spec=spec, term=tl, b=o["coef"][tv],
                                     se_rob=o["se"][tv], p_rob=o["p"][tv], se_cl=o["alt"][0]["se"][tv], p_cl=o["alt"][0]["p"][tv],
                                     F=o["fs"].get(tv, {}).get("F", np.nan), n=o["n"], countries=D.c.nunique()))
R = pd.DataFrame(rows)
R.to_csv("_res_connectivity_buffer_iv.csv", index=False)
pd.set_option("display.width", 240)
pd.set_option("display.max_rows", 300)
print(R.round(4).to_string(index=False))
