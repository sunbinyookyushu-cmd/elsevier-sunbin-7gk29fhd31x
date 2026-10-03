# -*- coding: utf-8 -*-
"""Margins of adjustment to fuel prices, country x month (user 2026-10-02: outcomes other than seats).
Seats did not respond (71). Exact log decomposition of fuel use:
  ln CO2 = ln flights + ln gauge (seats/flight) + ln stage (seat-km/seat) + ln intensity (CO2/seat-km)
so the coefficients of the four margins add up to the CO2 coefficient (same sample). Plus the extensive margin:
number of airports with scheduled departures in the country.
Same estimator as 71: D12 ln Y_ct = a_c + b D12 ln P_(t-3) + e, world real jet price instrumented by the Kaenzig or BH
supply shock (12-month sum, lag 3), country FE, SE country cluster + Newey-West 12, 1997-2019.
Data: airport_month_sep08fix.parquet summed by country (all airports). Departures may include cargo flights
(Fangyu's August file), which enter flights and gauge but not seats.
Output: _res_country_margins.csv, country_month_margins.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from _est import fit

V = ["n_dep_flights", "dep_seats", "dep_seat_km", "co2_dep", "n_dep_flights_dom", "dep_seats_dom", "dep_seat_km_dom"]
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month"] + V).to_pandas()
am = am[am.iso3.notna()]
am["active"] = (am.dep_seats > 0).astype(int)
am["active_dom"] = (am.dep_seats_dom > 0).astype(int)
cm = am.groupby(["iso3", "year", "month"], as_index=False)[V + ["active", "active_dom"]].sum()
cm["t"] = cm.year * 12 + cm.month
lg = lambda s: np.log(s.where(s > 0))
Y = {
    "CO2 (fuel burned)": lg(cm.co2_dep),
    "flights": lg(cm.n_dep_flights),
    "gauge (seats per flight)": lg(cm.dep_seats) - lg(cm.n_dep_flights),
    "stage length (km per seat)": lg(cm.dep_seat_km) - lg(cm.dep_seats),
    "CO2 per seat-km": lg(cm.co2_dep) - lg(cm.dep_seat_km),
    "seats": lg(cm.dep_seats),
    "seat-km": lg(cm.dep_seat_km),
    "airports with service": lg(cm.active),
    "domestic flights": lg(cm.n_dep_flights_dom),
    "domestic gauge": lg(cm.dep_seats_dom) - lg(cm.n_dep_flights_dom),
    "domestic stage length": lg(cm.dep_seat_km_dom) - lg(cm.dep_seats_dom),
    "airports with domestic service": lg(cm.active_dom),
}
names = {k: f"y{i}" for i, k in enumerate(Y)}
for k, s in Y.items():
    cm["ln_" + names[k]] = s
lag = cm[["iso3", "t"] + ["ln_" + v for v in names.values()]].copy()
lag["t"] += 12
cm = cm.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
for v in names.values():
    cm[v] = cm["ln_" + v] - cm["ln_" + v + "_m12"]
f = pd.read_csv("fuel_monthly.csv", usecols=["year", "month", "d12_lnjet_l3", "kz_s12_l3", "bh_neg_s12_l3"])
cm = cm.merge(f, on=["year", "month"], how="left")
cm.to_csv("country_month_margins.csv", index=False)

d = cm[(cm.year >= 1997) & (cm.year <= 2019)]
core = [names[k] for k in ["CO2 (fuel burned)", "flights", "gauge (seats per flight)", "stage length (km per seat)", "CO2 per seat-km"]]
common = d.dropna(subset=core + ["d12_lnjet_l3", "kz_s12_l3", "bh_neg_s12_l3"])      # same sample -> margins add up
x = "d12_lnjet_l3"
rows = []
for k, v in names.items():
    s = common if v in core else d.dropna(subset=[v, x, "kz_s12_l3", "bh_neg_s12_l3"])
    o = fit(s, v, exog=[x], fes=["iso3"], vc=("dk", "iso3", "t", 12), return_fs=False)
    rec = dict(outcome=k, n=o["n"], countries=s.iso3.nunique(), ols_b=o["coef"][x], ols_p=o["p"][x])
    for zl, z in {"kz": "kz_s12_l3", "bh": "bh_neg_s12_l3"}.items():
        o = fit(s, v, endog=[x], instr=[z], fes=["iso3"], vc=("dk", "iso3", "t", 12))
        rec.update({f"{zl}_b": o["coef"][x], f"{zl}_se": o["se"][x], f"{zl}_p": o["p"][x], f"{zl}_F": o["fs"][x]["F"]})
    rows.append(rec)
out = pd.DataFrame(rows)
out.to_csv("_res_country_margins.csv", index=False)
pd.set_option("display.width", 220)
print(out.round(4).to_string(index=False))
c = out.set_index("outcome")
for zl in ["kz", "bh"]:
    parts = c.loc[["flights", "gauge (seats per flight)", "stage length (km per seat)", "CO2 per seat-km"], f"{zl}_b"].sum()
    print(f"check {zl}: sum of four margins {parts:.5f} vs CO2 {c.loc['CO2 (fuel burned)', f'{zl}_b']:.5f}")
