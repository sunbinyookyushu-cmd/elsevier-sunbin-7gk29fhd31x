# -*- coding: utf-8 -*-
"""Sign of GACI -> CO2 and the intensity channel (user 2026-10-02: "gaci->co2 마이너스 아닐까? 매개하면 플러스?").
1 Within-airport association, annual panel 1996-2019, all airports: ln CO2, ln CO2/seat, ln CO2/seat-km, ln gauge,
  ln stage on ln GACI with airport FE + year FE, and + country x year FE (descriptive elasticities).
2 Sequential-g / Gelbach decomposition on the tax stacks (annual, as 105): for Y in {ln CO2, ln CO2 per seat-km}
     total tax effect  =  effect holding ln GACI fixed (direct)  +  (tax -> ln GACI) x (ln GACI -> Y | tax)
  computed exactly from the two regressions (omitted-variable identity). This is descriptive: it assumes GACI is the
  only omitted channel correlated with the tax, not an exclusion restriction.
SE country clusters. Output: _res_gaci_intensity.csv
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
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "dep_seats", "n_dep_flights", "dep_seat_km", "co2_dep"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019)]
ya = am.groupby(["airport_iata", "year"], as_index=False).agg(iso3=("iso3", "first"), seats=("dep_seats", "sum"), fl=("n_dep_flights", "sum"),
                                                              skm=("dep_seat_km", "sum"), co2=("co2_dep", "sum"))
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "GACI", "Degree", "Region"])
ya = ya.merge(hp, on=["airport_iata", "year"], how="left")
ya = ya[(ya.seats > 0) & (ya.co2 > 0) & (ya.fl > 0) & (ya.GACI > 0)].copy()
ya["ln_gaci"], ya["ln_co2"] = np.log(ya.GACI), np.log(ya.co2)
ya["ln_co2_seat"], ya["ln_int"] = np.log(ya.co2 / ya.seats), np.log(ya.co2 / ya.skm)
ya["ln_gauge"], ya["ln_stage"], ya["ln_deg"] = np.log(ya.seats / ya.fl), np.log(ya.skm / ya.seats), np.log(ya.Degree.where(ya.Degree > 0))
ya["cy"] = ya.iso3 + "_" + ya.year.astype(str)
rows = []
for y in ["ln_co2", "ln_co2_seat", "ln_int", "ln_gauge", "ln_stage", "ln_deg"]:
    for fe, lab in [("airport_iata + year", "airport + year FE"), ("airport_iata + cy", "airport + country x year FE")]:
        m = pf.feols(f"{y} ~ ln_gaci | {fe}", data=ya, vcov={"CRV1": "iso3"})
        t = m.tidy().loc["ln_gaci"]
        rows.append(dict(table="1 within-airport elasticity to ln GACI", spec=lab, outcome=y, term="ln GACI", b=t["Estimate"], se=t["Std. Error"],
                         p=t["Pr(>|t|)"], n=int(m._N)))
print("1 done", flush=True)

# ---- 2 Gelbach on tax stacks (reuse 105 stack construction) ----
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
SZ = ["tp_small", "tp_mid", "tp_large"]


def coefs(y, rhs, D=Y):
    m = pf.feols(f"{y} ~ {rhs} | fe_u + fe_t", data=D.dropna(subset=[y]), vcov={"CRV1": "iso3"})
    return m.tidy()


rhs = " + ".join(SZ) + " + bp"
G = coefs("ln_gaci", rhs)                      # tax -> GACI
for y, ylab in [("ln_co2", "total CO2"), ("ln_int", "CO2 per seat-km"), ("ln_co2_seat", "CO2 per seat")]:
    tot = coefs(y, rhs)
    dirc = coefs(y, rhs + " + ln_gaci")
    g_y = dirc.loc["ln_gaci"]
    for s in SZ:
        total, direct = tot.loc[s, "Estimate"], dirc.loc[s, "Estimate"]
        indirect = G.loc[s, "Estimate"] * g_y["Estimate"]
        rows.append(dict(table=f"2 Gelbach: {ylab}", spec=s.replace("tp_", ""), outcome=y, term="total tax effect", b=total, se=tot.loc[s, "Std. Error"], p=tot.loc[s, "Pr(>|t|)"], n=int(len(Y))))
        rows.append(dict(table=f"2 Gelbach: {ylab}", spec=s.replace("tp_", ""), outcome=y, term="direct (GACI held fixed)", b=direct, se=dirc.loc[s, "Std. Error"], p=dirc.loc[s, "Pr(>|t|)"], n=int(len(Y))))
        rows.append(dict(table=f"2 Gelbach: {ylab}", spec=s.replace("tp_", ""), outcome=y, term="indirect via GACI = (tax->GACI) x (GACI->Y)", b=indirect,
                         se=np.nan, p=np.nan, n=int(len(Y)), note=f"tax->GACI {G.loc[s, 'Estimate']:.4f}; GACI->Y {g_y['Estimate']:.3f} (p {g_y['Pr(>|t|)']:.3f}); check total-direct {total - direct:.4f}"))
R = pd.DataFrame(rows)
R.to_csv("_res_gaci_intensity.csv", index=False)
pd.set_option("display.width", 240)
pd.set_option("display.max_colwidth", 90)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
