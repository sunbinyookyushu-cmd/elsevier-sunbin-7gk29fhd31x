# -*- coding: utf-8 -*-
"""Ticket taxes: who loses? (user 2026-10-02, items 1-3)
  1 airport size terciles (pre-announcement-year seats, terciles within the treated country) x Treat x Post
  2 seat-weighted stacked DiD (weights = pre-year seats) to reconcile the unweighted airport effect (-12%) with the
    country-total SDID (~0)
  3 connectivity (ln GACI, ln eigenvector, ln betweenness, ln degree) by size tercile, annual
Stacks as in 95/100: 8 events (NLD separate in 95), announcement donut, pre [A-36,A-1], post [E,E+11]; border rings
50-300 km as own group; 50-km ring excluded; verified announcement dates. SE country clusters.
Output: _res_tax_by_size.csv
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
EV = pd.DataFrame([("NLD", "2008-07-01", "2007-02-01"), ("IRL", "2009-03-30", "2008-10-01"), ("DEU", "2011-01-01", "2010-06-01"),
                   ("AUT", "2011-04-01", "2010-10-01"), ("NOR", "2016-06-01", "2015-12-01"), ("SWE", "2018-04-01", "2017-06-01"),
                   ("GBR", "2007-02-01", "2006-12-01"), ("DNK", "1998-01-01", "1997-05-01"), ("MLT", "2005-08-01", "2004-11-01")],
                  columns=["iso3", "eff", "ann"])
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
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019) & (am.dep_seats > 0)].copy()
am["t"] = am.year * 12 + am.month
am["ln_seats"] = np.log(am.dep_seats)
ys = am.groupby(["airport_iata", "year"]).dep_seats.sum()
cb = pd.read_csv("crossborder_pairs.csv")
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI", "Eigen", "NorBetweenness", "Degree"])
hp = hp[(hp.year <= 2019) & (hp.GACI > 0)].copy()
hp["ln_gaci"], hp["ln_deg"] = np.log(hp.GACI), np.log(hp.Degree.where(hp.Degree > 0))
hp["ln_eigen"] = np.log(hp.Eigen.where(hp.Eigen > 0))
hp["ln_betw"] = np.log1p(hp.NorBetweenness * 1e4)

ms, ys_ = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(am[am.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (CODED - {"ITA", ev.iso3}) - busy
    py = ev.pre_year if ev.pre_year in ys.index.get_level_values(1) else ys.index.get_level_values(1).min()
    s0 = ys.xs(py, level="year")
    tq = pd.qcut(s0.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
    for src, out, tcol, keepfun in [(am, ms, "t", lambda d: (d.t >= lo) & (d.t <= hi) & ~((d.t >= ev.tA) & (d.t < ev.tE))),
                                    (hp, ys_, "year", lambda d: (d.year >= ev.E - 3) & (d.year <= ev.E))]:
        d = src[(src.iso3.isin(ctrl | {ev.iso3}) | src.airport_iata.isin(nb.index))]
        d = d[keepfun(d)].copy()
        km = d.airport_iata.map(nb)
        d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
        d = d[d.grp != "B50"]
        d["w0"] = d.airport_iata.map(s0).fillna(0)
        d["size"] = d.airport_iata.map(tq).astype(object).where(d.grp == "T", "ctrl")
        d["post"] = ((d.t >= ev.tE) if tcol == "t" else (d.year >= ev.E)).astype(np.int8)
        d["stk"] = k
        out.append(d)
M, Y = pd.concat(ms, ignore_index=True), pd.concat(ys_, ignore_index=True)
M["fe_u"] = M.airport_iata + "_" + M.month.astype(str) + "_" + M.stk.astype(str)
M["fe_t"] = M.t.astype(str) + "_" + M.stk.astype(str)
Y["fe_u"] = Y.airport_iata + "_" + Y.stk.astype(str)
Y["fe_t"] = Y.year.astype(str) + "_" + Y.stk.astype(str)
for D in (M, Y):
    D["tp"] = ((D.grp == "T") & (D.post == 1)).astype(np.int8)
    D["bp"] = ((D.grp == "B") & (D.post == 1)).astype(np.int8)
    for s in ["small", "mid", "large"]:
        D[f"tp_{s}"] = ((D["size"] == s) & (D.post == 1)).astype(np.int8)
rows = []


def est(table, D, y, rhs, terms, weights=None):
    d = D.dropna(subset=[y])
    m = pf.feols(f"{y} ~ {rhs} | fe_u + fe_t", data=d, vcov={"CRV1": "iso3"}, weights=weights)
    t = m.tidy()
    for term in terms:
        if term in t.index:
            rows.append(dict(table=table, outcome=y, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"],
                             p=t.loc[term, "Pr(>|t|)"], n=int(m._N), clusters=d.iso3.nunique()))


SZ = ["tp_small", "tp_mid", "tp_large", "bp"]
est("1 seats by size tercile", M, "ln_seats", " + ".join(SZ), SZ)
est("2 seats, seat-weighted", M[M.w0 > 0], "ln_seats", "tp + bp", ["tp", "bp"], weights="w0")
est("2 seats, seat-weighted, by size", M[M.w0 > 0], "ln_seats", " + ".join(SZ), SZ, weights="w0")
est("2 seats, unweighted (reference)", M, "ln_seats", "tp + bp", ["tp", "bp"])
print("seats done", flush=True)
for y in ["ln_gaci", "ln_deg", "ln_eigen", "ln_betw"]:
    est("3 connectivity by size tercile", Y, y, " + ".join(SZ), SZ)
    est("3 connectivity, all treated", Y, y, "tp + bp", ["tp", "bp"])
print("connectivity done", flush=True)
sz = M[M.grp == "T"].drop_duplicates(["airport_iata", "stk"]).groupby("size").w0.agg(["count", "median", "sum"])
sz["share_of_seats"] = sz["sum"] / sz["sum"].sum()
R = pd.DataFrame(rows)
R.to_csv("_res_tax_by_size.csv", index=False)
pd.set_option("display.width", 220)
print(sz.round(3).to_string())
print(R.round(4).to_string(index=False))
