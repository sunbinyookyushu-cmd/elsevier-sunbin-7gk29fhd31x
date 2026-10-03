# -*- coding: utf-8 -*-
"""Raw oil price regressions, country x month (user 2026-10-02: "did we regress on the oil price itself?").
Most Energy Economics oil papers use the raw price (Brent / WTI) as the regressor; we compare three raw series:
US Gulf Coast jet fuel (used so far), Brent, WTI, all real (US CPI, 2019 $), D12 ln, lag 3.
  D12 ln Y_ct = a_c + b D12 ln P_(t-3) + e     (OLS; country FE; SE country cluster + Newey-West 12; 1997-2019)
Same outcomes as 72 (country_month_margins.csv). No instrument: b mixes supply-driven and demand-driven price moves.
Output: _res_raw_price_ols.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd
from _est import fit

Y = {"y5": "seats", "y1": "flights", "y2": "gauge (seats per flight)", "y3": "stage length", "y4": "CO2 per seat-km", "y0": "CO2"}
cm = pd.read_csv("country_month_margins.csv", usecols=["iso3", "year", "month", "t"] + list(Y))
f = pd.read_csv("fuel_monthly.csv", usecols=["year", "month", "lnjet", "lnbrent", "cpi"])
w = pd.read_csv("data_external/MCOILWTICO.csv")
w["year"] = pd.to_datetime(w.observation_date).dt.year
w["month"] = pd.to_datetime(w.observation_date).dt.month
f = f.merge(w[["year", "month", "MCOILWTICO"]], on=["year", "month"], how="left")
cpi19 = f[f.year == 2019].cpi.mean()
f["lnwti"] = np.log(f.MCOILWTICO * cpi19 / f.cpi)
f = f.sort_values(["year", "month"]).reset_index(drop=True)
P = {"jet fuel (Gulf Coast)": "lnjet", "Brent": "lnbrent", "WTI": "lnwti"}
for v in P.values():
    f["x_" + v] = f[v].shift(3) - f[v].shift(15)
cm = cm.merge(f[["year", "month"] + ["x_" + v for v in P.values()]], on=["year", "month"], how="left")
d = cm[(cm.year >= 1997) & (cm.year <= 2019)]
rows = []
for yv, ylab in Y.items():
    for pl, pv in P.items():
        x = "x_" + pv
        s = d.dropna(subset=[yv, x])
        o = fit(s, yv, exog=[x], fes=["iso3"], vc=("dk", "iso3", "t", 12), return_fs=False)
        rows.append(dict(outcome=ylab, price=pl, b=o["coef"][x], se=o["se"][x], p=o["p"][x], n=o["n"],
                         countries=s.iso3.nunique()))
out = pd.DataFrame(rows)
out.to_csv("_res_raw_price_ols.csv", index=False)
pd.set_option("display.width", 200)
print(out.round(4).to_string(index=False))
print("corr of D12 ln series 1997-2019:")
ff = f[(f.year >= 1997) & (f.year <= 2019)][["x_" + v for v in P.values()]]
print(ff.corr().round(3).to_string())
