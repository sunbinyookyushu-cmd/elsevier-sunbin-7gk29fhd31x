# -*- coding: utf-8 -*-
"""Country x month IV with a continuous fuel price (user question 2026-10-02: "IV로 연속변수로 추정?").
  D12 ln S_ct = a_c + b D12 ln P_(c,t-3) + e,   P instrumented by an oil supply shock (12-month sum, lag 3)
P = (i) world real jet price (Gulf Coast, CPI-deflated) or (ii) local real jet price = world USD price x exchange
rate / local CPI (local_fx_monthly.csv from 41; no observed local jet prices, full pass-through assumed).
Instruments: Kaenzig (2021) news shock, Baumeister-Hamilton (2019) supply shock x -1. Country FE only: the shock is
common to all countries, so month FE would absorb it. 1997-2019; SE country cluster + Newey-West 12 (_est "dk"),
first-stage F under the same variance.
Data: country_month.csv (70_country_level.py). Output: _res_country_iv.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd
from _est import fit

cm = pd.read_csv("country_month.csv", usecols=["iso3", "year", "month", "t", "y_total", "y_domestic", "y_international",
                                                "d12_lnjet_l3", "kz_s12_l3", "bh_neg_s12_l3"])
L = pd.read_csv("local_fx_monthly.csv", usecols=["iso3", "ym", "lnP_loc"])
L["year"], L["month"] = L.ym.str[:4].astype(int), L.ym.str[5:7].astype(int)
L["t"] = L.year * 12 + L.month
for k, v in {"m12": 12, "l3": 3, "l15": 15}.items():
    s = L[["iso3", "t", "lnP_loc"]].copy()
    s["t"] += v
    L = L.merge(s.rename(columns={"lnP_loc": "lnP_" + k}), on=["iso3", "t"], how="left")
L["d12_lnPloc_l3"] = L.lnP_l3 - L.lnP_l15
cm = cm.merge(L[["iso3", "t", "d12_lnPloc_l3"]], on=["iso3", "t"], how="left")
d = cm[(cm.year >= 1997) & (cm.year <= 2019)].copy()

X = {"world real jet price": "d12_lnjet_l3", "local real jet price (FX-adjusted)": "d12_lnPloc_l3"}
Z = {"Kaenzig": "kz_s12_l3", "BH supply": "bh_neg_s12_l3"}
rows = []
for xl, x in X.items():
    for yk in ["total", "domestic", "international"]:
        y = "y_" + yk
        s = d.dropna(subset=[y, x, "kz_s12_l3", "bh_neg_s12_l3"])
        o = fit(s, y, exog=[x], fes=["iso3"], vc=("dk", "iso3", "t", 12), return_fs=False)
        rows.append(dict(price=xl, outcome=yk, method="OLS", b=o["coef"][x], se=o["se"][x], p=o["p"][x], F=np.nan,
                         n=o["n"], countries=s.iso3.nunique()))
        for zl, z in Z.items():
            o = fit(s, y, endog=[x], instr=[z], fes=["iso3"], vc=("dk", "iso3", "t", 12))
            r = fit(s, y, exog=[z], fes=["iso3"], vc=("dk", "iso3", "t", 12), return_fs=False)
            rows.append(dict(price=xl, outcome=yk, method=f"2SLS ({zl})", b=o["coef"][x], se=o["se"][x], p=o["p"][x],
                             F=o["fs"][x]["F"], first_stage=o["fs"][x]["pi"][z], reduced_form=r["coef"][z],
                             reduced_form_p=r["p"][z], n=o["n"], countries=s.iso3.nunique()))
out = pd.DataFrame(rows)
out.to_csv("_res_country_iv.csv", index=False)
pd.set_option("display.width", 220)
print(out.round(4).to_string(index=False))
