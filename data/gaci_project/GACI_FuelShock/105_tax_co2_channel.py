# -*- coding: utf-8 -*-
"""Tax -> network -> CO2 (user 2026-10-02: "세금 --> gaci --> co2??").
Exact annual decomposition per airport:  ln CO2 = ln destinations + ln(flights / destination) + ln(CO2 / flight),
so the tax effect on CO2 splits into a NETWORK margin (routes dropped), a FREQUENCY margin (flights per remaining route)
and an AIRCRAFT/DISTANCE margin (CO2 per flight = gauge x stage x intensity). Coefficients add up by construction.
Also Gelbach-style check: how much of the CO2 effect is absorbed when the change in ln destinations (and ln GACI)
is added as a control (descriptive channel share, no exclusion restriction claimed).
Annual stacks as in 102 (years E-3..E, airport x event and year x event FE), 8 events ex NLD, by size tercile.
Output: _res_tax_co2_channel.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import io
import sys
import warnings

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyfixest as pf

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
EV = pd.DataFrame([("IRL", "2009-03-30", "2008-10-01"), ("DEU", "2011-01-01", "2010-06-01"), ("AUT", "2011-04-01", "2010-10-01"),
                   ("NOR", "2016-06-01", "2015-12-01"), ("SWE", "2018-04-01", "2017-06-01"), ("GBR", "2007-02-01", "2006-12-01"),
                   ("DNK", "1998-01-01", "1997-05-01"), ("MLT", "2005-08-01", "2004-11-01")], columns=["iso3", "eff", "ann"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
EV["E"] = np.where(pd.to_datetime(EV.eff).dt.month <= 6, pd.to_datetime(EV.eff).dt.year, pd.to_datetime(EV.eff).dt.year + 1)
EV["pre_year"] = (EV.tA - 13) // 12
CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "dep_seats", "n_dep_flights", "dep_seat_km", "co2_dep"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019)]
ya = am.groupby(["airport_iata", "year"], as_index=False).agg(iso3=("iso3", "first"), seats=("dep_seats", "sum"), fl=("n_dep_flights", "sum"),
                                                              skm=("dep_seat_km", "sum"), co2=("co2_dep", "sum"))
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "GACI", "Degree"])
ya = ya.merge(hp, on=["airport_iata", "year"], how="left")
ya = ya[(ya.seats > 0) & (ya.co2 > 0) & (ya.fl > 0) & (ya.Degree > 0)].copy()
ya["ln_co2"], ya["ln_deg"] = np.log(ya.co2), np.log(ya.Degree)
ya["ln_fl_per_dest"] = np.log(ya.fl / ya.Degree)
ya["ln_co2_per_fl"] = np.log(ya.co2 / ya.fl)
ya["ln_gauge"], ya["ln_stage"], ya["ln_int"] = np.log(ya.seats / ya.fl), np.log(ya.skm / ya.seats), np.log(ya.co2 / ya.skm)
ya["ln_gaci"] = np.log(ya.GACI.where(ya.GACI > 0))
cb = pd.read_csv("crossborder_pairs.csv")
ys = []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(ya[ya.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (CODED - {"ITA", ev.iso3}) - busy
    b0 = ya[ya.year == ev.pre_year].set_index("airport_iata")
    d = ya[(ya.iso3.isin(ctrl | {ev.iso3}) | ya.airport_iata.isin(nb.index)) & (ya.year >= ev.E - 3) & (ya.year <= ev.E)].copy()
    km = d.airport_iata.map(nb)
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
    d = d[d.grp != "B50"]
    tsz = pd.qcut(b0.seats.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
    d["size"] = d.airport_iata.map(tsz).astype(object).where(d.grp == "T", "ctrl")
    d["post"], d["stk"] = (d.year >= ev.E).astype(np.int8), k
    ys.append(d)
Y = pd.concat(ys, ignore_index=True)
Y["fe_u"], Y["fe_t"] = Y.airport_iata + "_" + Y.stk.astype(str), Y.year.astype(str) + "_" + Y.stk.astype(str)
Y["tp"], Y["bp"] = ((Y.grp == "T") & (Y.post == 1)).astype(np.int8), ((Y.grp == "B") & (Y.post == 1)).astype(np.int8)
for s in ["small", "mid", "large"]:
    Y[f"tp_{s}"] = ((Y["size"] == s) & (Y.post == 1)).astype(np.int8)
rows = []


def est(table, y, rhs, terms, D=Y):
    d = D.dropna(subset=[y])
    m = pf.feols(f"{y} ~ {rhs} | fe_u + fe_t", data=d, vcov={"CRV1": "iso3"})
    t = m.tidy()
    for term in terms:
        if term in t.index:
            rows.append(dict(table=table, outcome=y, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"],
                             p=t.loc[term, "Pr(>|t|)"], n=int(m._N), clusters=d.iso3.nunique()))


SZ = ["tp_small", "tp_mid", "tp_large", "bp"]
for y in ["ln_co2", "ln_deg", "ln_fl_per_dest", "ln_co2_per_fl", "ln_gauge", "ln_stage", "ln_int"]:
    est("decomposition, all treated", y, "tp + bp", ["tp", "bp"])
    est("decomposition, by size", y, " + ".join(SZ), SZ)
print("decomposition done", flush=True)
# Gelbach-style: CO2 effect with and without the network variables as controls
est("channel: CO2 baseline", "ln_co2", " + ".join(SZ), SZ)
est("channel: CO2 | ln destinations", "ln_co2", " + ".join(SZ) + " + ln_deg", SZ + ["ln_deg"])
est("channel: CO2 | ln destinations + ln GACI", "ln_co2", " + ".join(SZ) + " + ln_deg + ln_gaci", SZ + ["ln_deg", "ln_gaci"])
R = pd.DataFrame(rows)
R.to_csv("_res_tax_co2_channel.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
d = R[R.table == "decomposition, by size"].pivot(index="outcome", columns="term", values="b")
print("\ncheck: ln_deg + ln_fl_per_dest + ln_co2_per_fl vs ln_co2 (by size):")
print((d.loc[["ln_deg", "ln_fl_per_dest", "ln_co2_per_fl"]].sum() - d.loc["ln_co2"]).round(5).to_string())
