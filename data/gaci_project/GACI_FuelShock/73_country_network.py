# -*- coding: utf-8 -*-
"""B. Network redistribution within a country when fuel prices rise (user choice 2026-10-02).
Total seats do not respond (71, 72); do seats move between airports? Country x month:
  HHI       = sum_i (seat share of airport i)^2 x 100 (all departing seats; domestic version on domestic seats)
  top share = seat share (x 100) of the country's main airport, fixed in advance = largest airport in the
              first calendar year the country appears (1996 for almost all), so the identity cannot switch.
Months with fewer than 2 airports with seats are dropped (HHI = 100 by construction).
Same estimator as 71/72 on 12-month level changes: D12 Y_ct = a_c + b D12 ln P_(t-3) + e, world real jet price
instrumented by the Kaenzig or BH supply shock, country FE, SE country cluster + Newey-West 12, 1997-2019.
b > 0: seats concentrate in the main airport when fuel gets dearer.
Output: _res_country_network.csv, country_month_network.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from _est import fit

am = pq.read_table("airport_month_sep08fix.parquet",
                   columns=["airport_iata", "iso3", "year", "month", "dep_seats", "dep_seats_dom"]).to_pandas()
am = am[am.iso3.notna()]
first = am.groupby("iso3").year.min()
y1 = am[am.year == am.iso3.map(first)].groupby(["iso3", "airport_iata"]).dep_seats.sum().reset_index()
main = y1.sort_values("dep_seats").groupby("iso3").airport_iata.last()


def conc(col, tag):
    x = am[am[col] > 0][["iso3", "year", "month", "airport_iata", col]].copy()
    x["S"] = x.groupby(["iso3", "year", "month"])[col].transform("sum")
    x["sh2"] = (x[col] / x.S) ** 2
    x["main"] = (x.airport_iata == x.iso3.map(main)) * x[col] / x.S
    g = x.groupby(["iso3", "year", "month"]).agg(hhi=("sh2", "sum"), top=("main", "sum"), n=(col, "size")).reset_index()
    g = g[g.n >= 2]
    return g.rename(columns={"hhi": "hhi_" + tag, "top": "top_" + tag, "n": "n_" + tag})


cm = conc("dep_seats", "all").merge(conc("dep_seats_dom", "dom"), on=["iso3", "year", "month"], how="outer")
for v in ["hhi_all", "top_all", "hhi_dom", "top_dom"]:
    cm[v] *= 100
cm["t"] = cm.year * 12 + cm.month
lag = cm[["iso3", "t", "hhi_all", "top_all", "hhi_dom", "top_dom"]].copy()
lag["t"] += 12
cm = cm.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
for v in ["hhi_all", "top_all", "hhi_dom", "top_dom"]:
    cm["d12_" + v] = cm[v] - cm[v + "_m12"]
f = pd.read_csv("fuel_monthly.csv", usecols=["year", "month", "d12_lnjet_l3", "kz_s12_l3", "bh_neg_s12_l3"])
cm = cm.merge(f, on=["year", "month"], how="left")
cm.to_csv("country_month_network.csv", index=False)

d = cm[(cm.year >= 1997) & (cm.year <= 2019)]
x = "d12_lnjet_l3"
OUT = {"d12_top_all": "main-airport seat share (pp)", "d12_hhi_all": "airport HHI (x100)",
       "d12_top_dom": "main-airport share of domestic seats (pp)", "d12_hhi_dom": "domestic airport HHI (x100)"}
rows = []
for v, lab in OUT.items():
    s = d.dropna(subset=[v, x, "kz_s12_l3", "bh_neg_s12_l3"])
    o = fit(s, v, exog=[x], fes=["iso3"], vc=("dk", "iso3", "t", 12), return_fs=False)
    rec = dict(outcome=lab, n=o["n"], countries=s.iso3.nunique(), mean_level=s[v.replace("d12_", "")].mean(),
               ols_b=o["coef"][x], ols_p=o["p"][x])
    for zl, z in {"kz": "kz_s12_l3", "bh": "bh_neg_s12_l3"}.items():
        o = fit(s, v, endog=[x], instr=[z], fes=["iso3"], vc=("dk", "iso3", "t", 12))
        rec.update({f"{zl}_b": o["coef"][x], f"{zl}_se": o["se"][x], f"{zl}_p": o["p"][x], f"{zl}_F": o["fs"][x]["F"]})
    rows.append(rec)
out = pd.DataFrame(rows)
out.to_csv("_res_country_network.csv", index=False)
pd.set_option("display.width", 220)
print(out.round(4).to_string(index=False))
