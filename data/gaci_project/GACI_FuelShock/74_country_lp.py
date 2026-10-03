# -*- coding: utf-8 -*-
"""C. Longer horizons: local projections of country aviation on an oil supply shock, 0-48 months (user choice
2026-10-02). Airlines plan schedules 6-12 months ahead and replace fleets over years, so the 12-month window of
71-73 may be too short.
  Y_(c,t+h) - Y_(c,t-1) = a_(c x calendar month of t) + b_h s_t + g D12 Y_(c,t-1) + e,   h = 0, 3, ..., 48
  Y = ln seats, ln flights, ln gauge, ln stage length, ln CO2 per seat-km, ln CO2 (country_month_margins.csv, 72),
      main-airport seat share and airport HHI in levels x 100 (country_month_network.csv, 73)
  s_t = monthly Kaenzig news shock or sign-flipped BH supply shock, scaled to 1 SD (1997-2019), as in 14.
Country x calendar-month FE absorb seasonality (the h+1-month change depends on the start month); no month FE,
because the shock is common. Only t + h <= 2019-12. SE country cluster + Newey-West L = max(h+1, 6).
Price response g_h: ln P_(t+h) - ln P_(t-1) on s_t (time series, Newey-West L = h+1); implied elasticity b_h / g_h.
Output: _res_country_lp.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd
import statsmodels.api as sm
from _est import fit

M = pd.read_csv("country_month_margins.csv")
N = pd.read_csv("country_month_network.csv", usecols=["iso3", "t", "top_all", "hhi_all"])
OUT = {"ln_y5": "seats", "ln_y1": "flights", "ln_y2": "gauge (seats per flight)", "ln_y3": "stage length",
       "ln_y4": "CO2 per seat-km", "ln_y0": "CO2", "top_all": "main-airport seat share (pp)", "hhi_all": "airport HHI (x100)"}
M = M[["iso3", "year", "month", "t"] + [k for k in OUT if k.startswith("ln_")]].merge(N, on=["iso3", "t"], how="left")
f = pd.read_csv("fuel_monthly.csv", usecols=["year", "month", "kz", "bh_neg", "lnjet"])
f["t"] = f.year * 12 + f.month
sd = f[(f.year >= 1997) & (f.year <= 2019)][["kz", "bh_neg"]].std()
f["s_kz"], f["s_bh"] = f.kz / sd.kz, f.bh_neg / sd.bh_neg
T0, T_END = 1997 * 12 + 1, 2019 * 12 + 12
ts = f.set_index("t").sort_index()

rows = []
for v, lab in OUT.items():
    W = M.pivot_table(index="iso3", columns="t", values=v)
    W = W.reindex(columns=range(W.columns.min(), W.columns.max() + 1))
    prev, lag12 = W.shift(1, axis=1), W.shift(13, axis=1)
    g12 = (prev - lag12).stack().rename("g12").reset_index()
    for h in range(0, 49, 3):
        dy = (W.shift(-h, axis=1) - prev).stack().rename("dy").reset_index()
        d = dy.merge(g12, on=["iso3", "t"], how="left").merge(f[["t", "month", "s_kz", "s_bh"]], on="t", how="left")
        d = d[(d.t >= T0) & (d.t + h <= T_END)].copy()
        d["cm"] = d.iso3 + "_" + d.month.astype(str)
        for s in ["s_kz", "s_bh"]:
            r = fit(d, "dy", exog=[s, "g12"], fes=["cm"], vc=("dk", "iso3", "t", max(h + 1, 6)), return_fs=False)
            p = ts.lnjet.shift(-h) - ts.lnjet.shift(1)
            q = pd.DataFrame({"dp": p, "s": ts[s]}).loc[T0:T_END - h].dropna()
            o = sm.OLS(q.dp, sm.add_constant(q.s)).fit(cov_type="HAC", cov_kwds={"maxlags": h + 1})
            rows.append(dict(outcome=lab, h=h, shock=s, b=r["coef"][s], se=r["se"][s], p=r["p"][s], n=r["n"],
                             countries=d.dropna(subset=["dy", "g12"]).iso3.nunique(), price_resp=o.params["s"],
                             price_se=o.bse["s"], implied_elast=r["coef"][s] / o.params["s"]))
    print(lab, "done", flush=True)
res = pd.DataFrame(rows)
res.to_csv("_res_country_lp.csv", index=False)
pd.set_option("display.width", 220)
show = res[res.h.isin([0, 6, 12, 18, 24, 36, 48])]
print(show.round(4).to_string(index=False))
