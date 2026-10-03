# -*- coding: utf-8 -*-
"""Control-group choice and parallel trends (user 2026-10-03): three control sets, same stacks and FE as the main tables.
  (a) Europe, coded 20 countries with no tax event in the window (current)
  (b) Europe, countries with no national ticket tax at any time 1996-2019 (BEL, CHE, ESP, FIN, HRV, HUN, LUX, PRT)
  (c) World: all 33 coded countries (Europe + AUS, CAN, CHN, IND, JPN, KOR, NZL, QAT, SGP, THA, TUR, ARE, USA) with no coded
      event in the window (their own events, coded from taxes_nordic_rest.csv, make them 'busy' in those windows)
Outcomes: seats and CO2 (monthly, event-time bins [A-36,A-25] [A-24,A-13] ref [A-12,A-1] post [E,E+11]); GACI (annual,
k = -3, -2, ref -1, 0, +1). 8 events ex NLD. Border 50-300 km own group; 50 km dropped. SE country clusters.
Output: _res_tax_controls.csv
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
EUR = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN", "HRV", "MLT"}
ROW = {"AUS", "CAN", "CHN", "IND", "JPN", "KOR", "NZL", "QAT", "SGP", "THA", "TUR", "ARE", "USA"}
NEVER = {"BEL", "CHE", "ESP", "FIN", "HRV", "HUN", "LUX", "PRT"}
SETS = {"(a) Europe, no event in window": EUR - {"ITA"}, "(b) Europe, never taxed 1996-2019": NEVER, "(c) World, no event in window": (EUR - {"ITA"}) | ROW}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"), pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.event_type != "none_in_period"].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "co2_dep"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019) & (am.dep_seats > 0)].copy()
am["t"] = am.year * 12 + am.month
am["ln_seats"], am["ln_co2"] = np.log(am.dep_seats), np.log(am.co2_dep.where(am.co2_dep > 0))
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI"])
hp = hp[(hp.year <= 2019) & (hp.GACI > 0) & hp.iso3.notna()].copy()
hp["ln_gaci"] = np.log(hp.GACI)
cb = pd.read_csv("crossborder_pairs.csv")
rows = []


def est(cs, D, y, rhs, terms, unit):
    d = D.dropna(subset=[y])
    m = pf.feols(f"{y} ~ {rhs} | fe_u + fe_t", data=d, vcov={"CRV1": "iso3"})
    t = m.tidy()
    for term in terms:
        if term in t.index:
            rows.append(dict(controls=cs, outcome=y, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"], p=t.loc[term, "Pr(>|t|)"],
                             n=int(m._N), clusters=d.iso3.nunique(), control_airports=d[d.grp == "C"].airport_iata.nunique()))


for cs, pool in SETS.items():
    ms, ys = [], []
    for k, ev in EV.iterrows():
        lo, hi = ev.tA - 36, ev.tE + 11
        busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
        tre = set(am[am.iso3 == ev.iso3].airport_iata)
        nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
        ctrl = (pool - {ev.iso3}) - busy
        d = am[(am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(nb.index)) & (am.t >= lo) & (am.t <= hi) & ~((am.t >= ev.tA) & (am.t < ev.tE))].copy()
        km = d.airport_iata.map(nb)
        d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
        d = d[d.grp != "B50"]
        d["stk"], d["relA"], d["relE"] = k, d.t - ev.tA, d.t - ev.tE
        ms.append(d)
        y = hp[(hp.iso3.isin(ctrl | {ev.iso3}) | hp.airport_iata.isin(nb.index)) & (hp.year >= ev.E - 3) & (hp.year <= ev.E + 1)].copy()
        kmy = y.airport_iata.map(nb)
        y["grp"] = np.where(y.iso3 == ev.iso3, "T", np.where(kmy <= 50, "B50", np.where(kmy <= 300, "B", "C")))
        y = y[y.grp != "B50"]
        y["stk"], y["k"] = k, y.year - ev.E
        ys.append(y)
    M, Y = pd.concat(ms, ignore_index=True), pd.concat(ys, ignore_index=True)
    M["fe_u"], M["fe_t"] = M.airport_iata + "_" + M.month.astype(str) + "_" + M.stk.astype(str), M.t.astype(str) + "_" + M.stk.astype(str)
    Y["fe_u"], Y["fe_t"] = Y.airport_iata + "_" + Y.stk.astype(str), Y.year.astype(str) + "_" + Y.stk.astype(str)
    for nm, f in [("pre36_25", lambda x: x.relA.between(-36, -25)), ("pre24_13", lambda x: x.relA.between(-24, -13)), ("post0_11", lambda x: x.relE.between(0, 11))]:
        M["T_" + nm] = ((M.grp == "T") & f(M)).astype(np.int8)
        M["B_" + nm] = ((M.grp == "B") & f(M)).astype(np.int8)
    mt = ["T_pre36_25", "T_pre24_13", "T_post0_11"]
    for y in ["ln_seats", "ln_co2"]:
        est(cs, M, y, " + ".join(mt + ["B_pre36_25", "B_pre24_13", "B_post0_11"]), mt, "airport-month")
    for kk in [-3, -2, 0, 1]:
        Y[f"T_k{kk}".replace("-", "m")] = ((Y.grp == "T") & (Y.k == kk)).astype(np.int8)
        Y[f"B_k{kk}".replace("-", "m")] = ((Y.grp == "B") & (Y.k == kk)).astype(np.int8)
    yt = ["T_km3", "T_km2", "T_k0", "T_k1"]
    est(cs, Y, "ln_gaci", " + ".join(yt + ["B_km3", "B_km2", "B_k0", "B_k1"]), yt, "airport-year")
    print(cs, "done; control countries used:", sorted(set(M[M.grp == "C"].iso3)), flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_tax_controls.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 100)
print(R.round(4).to_string(index=False))
