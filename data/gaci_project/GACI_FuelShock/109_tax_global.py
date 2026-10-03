# -*- coding: utf-8 -*-
"""Global version: all coded ticket-tax increases, Europe and beyond (user 2026-10-03: "전체로 돌려봐").
Events: 8 European (verified announcement dates, donut as before) + 11 outside Europe (coded in taxes_nordic_rest.csv;
announcement dates not yet verified, so event time starts at the effective date with no donut):
  AUS PMC 2001-07-01, 2008-07-01, 2012-07-01; CAN ATSC 2002-04-01, 2010-04-01; JPN 2019-01-07; KOR 2004-07-01;
  SGP 2009-10-01, 2018-07-01 (transfers taxed); NZL 2016-01-01; ARE 2010-05-27. USA 1997 (no domestic control) and
  IND 2019 (Rs 150) excluded.
Controls: all 33 coded countries with no coded event in [A-48 m, E+11 m]; border 50-300 km own group; 50 km dropped.
Specs: (1) month x event FE; (2) region x month x event FE (region = GACI panel Region of the airport), pooled 19 events;
       Europe-only and non-Europe-only; size terciles pooled. Outcomes ln seats, ln CO2 (monthly), ln GACI (annual).
Pre-trend bins [E-36,E-25] [E-24,E-13] (or from A for European events), ref [-12,-1], post [E,E+11].
SE country clusters. Output: _res_tax_global.csv
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
EV = pd.DataFrame([("IRL", "2009-03-30", "2008-10-01", "EUR"), ("DEU", "2011-01-01", "2010-06-01", "EUR"), ("AUT", "2011-04-01", "2010-10-01", "EUR"),
                   ("NOR", "2016-06-01", "2015-12-01", "EUR"), ("SWE", "2018-04-01", "2017-06-01", "EUR"), ("GBR", "2007-02-01", "2006-12-01", "EUR"),
                   ("DNK", "1998-01-01", "1997-05-01", "EUR"), ("MLT", "2005-08-01", "2004-11-01", "EUR"),
                   ("AUS", "2001-07-01", "2001-07-01", "ROW"), ("AUS", "2008-07-01", "2008-07-01", "ROW"), ("AUS", "2012-07-01", "2012-07-01", "ROW"),
                   ("CAN", "2002-04-01", "2002-04-01", "ROW"), ("CAN", "2010-04-01", "2010-04-01", "ROW"), ("JPN", "2019-01-07", "2019-01-01", "ROW"),
                   ("KOR", "2004-07-01", "2004-07-01", "ROW"), ("SGP", "2009-10-01", "2009-10-01", "ROW"), ("SGP", "2018-07-01", "2018-07-01", "ROW"),
                   ("NZL", "2016-01-01", "2016-01-01", "ROW"), ("ARE", "2010-05-27", "2010-05-01", "ROW")], columns=["iso3", "eff", "ann", "zone"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
EV["E"] = np.where(pd.to_datetime(EV.eff).dt.month <= 6, pd.to_datetime(EV.eff).dt.year, pd.to_datetime(EV.eff).dt.year + 1)
EV["pre_year"] = (EV.tA - 13) // 12
ALL = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN", "HRV", "MLT",
       "AUS", "CAN", "CHN", "IND", "JPN", "KOR", "NZL", "QAT", "SGP", "THA", "TUR", "ARE", "USA"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"), pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.event_type != "none_in_period"].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "co2_dep"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019) & (am.dep_seats > 0)].copy()
am["t"] = am.year * 12 + am.month
am["ln_seats"], am["ln_co2"] = np.log(am.dep_seats), np.log(am.co2_dep.where(am.co2_dep > 0))
ys_ = am.groupby(["airport_iata", "year"]).dep_seats.sum()
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI", "Region"])
reg = hp.dropna(subset=["Region"]).drop_duplicates("airport_iata").set_index("airport_iata").Region
hp = hp[(hp.year <= 2019) & (hp.GACI > 0) & hp.iso3.notna()].copy()
hp["ln_gaci"] = np.log(hp.GACI)
cb = pd.read_csv("crossborder_pairs.csv")
ms, ys = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(am[am.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (ALL - {ev.iso3}) - busy
    s0 = ys_.xs(ev.pre_year, level="year") if ev.pre_year in ys_.index.get_level_values(1) else ys_.xs(ys_.index.get_level_values(1).min(), level="year")
    tq = pd.qcut(s0.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
    d = am[(am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(nb.index)) & (am.t >= lo) & (am.t <= hi) & ~((am.t >= ev.tA) & (am.t < ev.tE))].copy()
    km = d.airport_iata.map(nb)
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
    d = d[d.grp != "B50"]
    d["stk"], d["relA"], d["relE"], d["zone"] = k, d.t - ev.tA, d.t - ev.tE, ev.zone
    d["size"] = d.airport_iata.map(tq).astype(object).where(d.grp == "T", "ctrl")
    ms.append(d)
    y = hp[(hp.iso3.isin(ctrl | {ev.iso3}) | hp.airport_iata.isin(nb.index)) & (hp.year >= ev.E - 3) & (hp.year <= ev.E + 1)].copy()
    kmy = y.airport_iata.map(nb)
    y["grp"] = np.where(y.iso3 == ev.iso3, "T", np.where(kmy <= 50, "B50", np.where(kmy <= 300, "B", "C")))
    y = y[y.grp != "B50"]
    y["stk"], y["k"], y["zone"] = k, y.year - ev.E, ev.zone
    y["size"] = y.airport_iata.map(tq).astype(object).where(y.grp == "T", "ctrl")
    ys.append(y)
    print(f"{ev.iso3} {ev.eff}: treated airports {len(tre & set(d.airport_iata))}, control countries {len(ctrl)}", flush=True)
M, Y = pd.concat(ms, ignore_index=True), pd.concat(ys, ignore_index=True)
M["region"], Y["region"] = M.airport_iata.map(reg).fillna("NA"), Y.airport_iata.map(reg).fillna("NA")
M["fe_u"], M["fe_t"] = M.airport_iata + "_" + M.month.astype(str) + "_" + M.stk.astype(str), M.t.astype(str) + "_" + M.stk.astype(str)
M["fe_rt"] = M.region + "_" + M.fe_t
Y["fe_u"], Y["fe_t"] = Y.airport_iata + "_" + Y.stk.astype(str), Y.year.astype(str) + "_" + Y.stk.astype(str)
Y["fe_rt"] = Y.region + "_" + Y.fe_t
for nm, f in [("pre36_25", lambda x: x.relA.between(-36, -25)), ("pre24_13", lambda x: x.relA.between(-24, -13)), ("post0_11", lambda x: x.relE.between(0, 11))]:
    M["T_" + nm] = ((M.grp == "T") & f(M)).astype(np.int8)
    M["B_" + nm] = ((M.grp == "B") & f(M)).astype(np.int8)
    for sz in ["small", "mid", "large"]:
        M[f"{sz}_{nm}"] = ((M["size"] == sz) & f(M)).astype(np.int8)
for kk in [-3, -2, 0, 1]:
    Y[f"T_k{kk}".replace("-", "m")] = ((Y.grp == "T") & (Y.k == kk)).astype(np.int8)
    Y[f"B_k{kk}".replace("-", "m")] = ((Y.grp == "B") & (Y.k == kk)).astype(np.int8)
    for sz in ["small", "mid", "large"]:
        Y[f"{sz}_k{kk}".replace("-", "m")] = ((Y["size"] == sz) & (Y.k == kk)).astype(np.int8)
rows = []


def est(sample, fe, D, y, terms, extra):
    d = D.dropna(subset=[y])
    m = pf.feols(f"{y} ~ {' + '.join(terms + extra)} | fe_u + {fe}", data=d, vcov={"CRV1": "iso3"})
    t = m.tidy()
    for term in terms:
        if term in t.index:
            rows.append(dict(sample=sample, fe=fe, outcome=y, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"], p=t.loc[term, "Pr(>|t|)"],
                             n=int(m._N), clusters=d.iso3.nunique(), events=d[d.grp == "T"].stk.nunique()))


mt, mb = ["T_pre36_25", "T_pre24_13", "T_post0_11"], ["B_pre36_25", "B_pre24_13", "B_post0_11"]
yt, yb = ["T_km3", "T_km2", "T_k0", "T_k1"], ["B_km3", "B_km2", "B_k0", "B_k1"]
for sample, cond_m, cond_y in [("all 19 events", M.stk >= 0, Y.stk >= 0), ("Europe 8", M.zone == "EUR", Y.zone == "EUR"), ("outside Europe 11", M.zone == "ROW", Y.zone == "ROW")]:
    for fe in ["fe_t", "fe_rt"]:
        for y in ["ln_seats", "ln_co2"]:
            est(sample, fe, M[cond_m], y, mt, mb)
        est(sample, fe, Y[cond_y], "ln_gaci", yt, yb)
    print(sample, "done", flush=True)
st = [f"{sz}_{nm}" for sz in ["small", "mid", "large"] for nm in ["pre24_13", "post0_11"]]
for y in ["ln_seats", "ln_co2"]:
    est("all 19 events, by size", "fe_rt", M, y, st, mb)
sy = [f"{sz}_{k}" for sz in ["small", "mid", "large"] for k in ["km2", "k0", "k1"]]
est("all 19 events, by size", "fe_rt", Y, "ln_gaci", sy, yb)
R = pd.DataFrame(rows)
R.to_csv("_res_tax_global.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
