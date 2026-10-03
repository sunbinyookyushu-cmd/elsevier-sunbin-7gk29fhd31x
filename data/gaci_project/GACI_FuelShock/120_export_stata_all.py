# -*- coding: utf-8 -*-
"""Build every dataset for the Stata do-files of the ticket-tax paper (user 2026-10-03).
Rules asked for: country ln GDP and ln population as controls in every regression; do-files fully inline (no loops, no
macros, one command per line) so any block can be re-run on its own. This script only prepares data; all estimation
is in stata_paper/01_main.do and stata_paper/02_events_mediation.do (written by 121_write_do_files.py).

Datasets (stata_paper/):
  stack_month.dta   airport x month stacks, 19 events (8 Europe with verified announcement dates + donut, 11 outside
                    Europe at effective date), pre [A-36,A-1], post [E,E+23]; treated / border 50-300 km / control;
                    outcomes ln seats, ln CO2, ln CO2 per seat-km, ln flights, ln seats per flight; dose (EUR per
                    departing passenger at the airport's pre-year distance band); size terciles; controls lngdp lnpop
                    (country-year, WDI via GACI_CO2 panel); flags zone (EUR/ROW), ctrl_never (never-taxed Europe),
                    region; fixed-effect ids fe_u (airport x calendar month x event), fe_t (month x event), fe_rt.
  stack_eff.dta     effective-date stacks +-36 months, 9 European events incl. NLD (window robustness).
  stack_loss.dta    service-loss grid (at-risk airport-months, months with no departure = 0 seats), 8 European events.
  stack_year.dta    airport x year stacks, 19 events, years E-3..E+1: ln GACI, destinations, eigenvector, betweenness,
                    ln CO2 and its exact decomposition (destinations, flights per destination, CO2 per flight, gauge,
                    stage, intensity), controls, size, fe_u (airport x event), fe_t (year x event).
  sdid_month.dta    country x month de-seasonalised ln seats / ln CO2 per event (balanced, donut dropped) for sdid.
  sdid_year.dta     country x year seat-weighted mean ln GACI per event for sdid.
  events.dta        event list.
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import os
import warnings

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

warnings.filterwarnings("ignore")
OUT = "stata_paper"
os.makedirs(OUT, exist_ok=True)
EV = pd.DataFrame([
    (0, "NLD", "2008-07-01", "2007-02-01", "EUR"), (1, "IRL", "2009-03-30", "2008-10-01", "EUR"), (2, "DEU", "2011-01-01", "2010-06-01", "EUR"),
    (3, "AUT", "2011-04-01", "2010-10-01", "EUR"), (4, "NOR", "2016-06-01", "2015-12-01", "EUR"), (5, "SWE", "2018-04-01", "2017-06-01", "EUR"),
    (6, "GBR", "2007-02-01", "2006-12-01", "EUR"), (7, "DNK", "1998-01-01", "1997-05-01", "EUR"), (8, "MLT", "2005-08-01", "2004-11-01", "EUR"),
    (9, "AUS", "2001-07-01", "2001-07-01", "ROW"), (10, "AUS", "2008-07-01", "2008-07-01", "ROW"), (11, "AUS", "2012-07-01", "2012-07-01", "ROW"),
    (12, "CAN", "2002-04-01", "2002-04-01", "ROW"), (13, "CAN", "2010-04-01", "2010-04-01", "ROW"), (14, "JPN", "2019-01-07", "2019-01-01", "ROW"),
    (15, "KOR", "2004-07-01", "2004-07-01", "ROW"), (16, "SGP", "2009-10-01", "2009-10-01", "ROW"), (17, "SGP", "2018-07-01", "2018-07-01", "ROW"),
    (18, "NZL", "2016-01-01", "2016-01-01", "ROW"), (19, "ARE", "2010-05-27", "2010-05-01", "ROW")], columns=["stk", "iso3", "eff", "ann", "zone"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
EV["E"] = np.where(pd.to_datetime(EV.eff).dt.month <= 6, pd.to_datetime(EV.eff).dt.year, pd.to_datetime(EV.eff).dt.year + 1)
EV["pre_year"] = (EV.tA - 13) // 12
# EUR per departing passenger, by distance band of the airport's pre-year mean stage length (km)
BANDS = {"DEU": [(2500, 8), (6000, 25), (1e9, 45)], "AUT": [(2500, 8), (6000, 20), (1e9, 35)], "NLD": [(2500, 11.25), (1e9, 45)],
         "IRL": [(300, 2), (1e9, 10)], "SWE": [(2500, 6.2), (6000, 25.8), (1e9, 41.2)], "NOR": [(1e9, 8.6)], "GBR": [(2500, 7.4), (1e9, 29.6)],
         "DNK": [(1e9, 10.1)], "MLT": [(1e9, 23.3)], "AUS": [(1e9, 5.0)], "CAN": [(1e9, 5.5)], "JPN": [(1e9, 8.0)], "KOR": [(1e9, 7.0)],
         "SGP": [(1e9, 6.0)], "NZL": [(1e9, 10.0)], "ARE": [(1e9, 6.0)]}
EUR = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN", "HRV", "MLT"}
ROW = {"AUS", "CAN", "CHN", "IND", "JPN", "KOR", "NZL", "QAT", "SGP", "THA", "TUR", "ARE", "USA"}
NEVER = {"BEL", "CHE", "ESP", "FIN", "HRV", "HUN", "LUX", "PRT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"), pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.event_type != "none_in_period"].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
cy = pd.read_csv("country_year.csv", usecols=["c", "y", "lngdp", "lnpop"]).rename(columns={"c": "iso3", "y": "year"})
raw = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "n_dep_flights", "dep_seat_km", "co2_dep"]).to_pandas()
raw = raw[raw.iso3.notna() & (raw.year <= 2019)].copy()
raw["t"] = raw.year * 12 + raw.month
am = raw[raw.dep_seats > 0].copy()
am["ln_seats"] = np.log(am.dep_seats)
am["ln_co2"] = np.log(am.co2_dep.where(am.co2_dep > 0))
am["ln_int"] = np.log((am.co2_dep / am.dep_seat_km).where(am.co2_dep > 0))
am["ln_fl"] = np.log(am.n_dep_flights.where(am.n_dep_flights > 0))
am["ln_gauge"] = am.ln_seats - am.ln_fl
ya = am.groupby(["airport_iata", "year"], as_index=False).agg(iso3=("iso3", "first"), seats=("dep_seats", "sum"), fl=("n_dep_flights", "sum"), skm=("dep_seat_km", "sum"), co2=("co2_dep", "sum"))
ya["stage"] = ya.skm / ya.seats
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "GACI", "Degree", "Eigen", "NorBetweenness", "Region"])
reg = hp.dropna(subset=["Region"]).drop_duplicates("airport_iata").set_index("airport_iata").Region
yy = ya.merge(hp.drop(columns="Region"), on=["airport_iata", "year"], how="left")
yy = yy[(yy.seats > 0) & (yy.co2 > 0) & (yy.fl > 0)].copy()
yy["ln_gaci"] = np.log(yy.GACI.where(yy.GACI > 0))
yy["ln_deg"] = np.log(yy.Degree.where(yy.Degree > 0))
yy["ln_eigen"] = np.log(yy.Eigen.where(yy.Eigen > 0))
yy["ln_betw"] = np.log1p(yy.NorBetweenness.fillna(0) * 1e4)
yy["ln_co2"] = np.log(yy.co2)
yy["ln_fl_per_dest"] = np.log(yy.fl) - yy.ln_deg
yy["ln_co2_per_fl"] = np.log(yy.co2 / yy.fl)
yy["ln_gauge"], yy["ln_stage"], yy["ln_int"] = np.log(yy.seats / yy.fl), np.log(yy.skm / yy.seats), np.log(yy.co2 / yy.skm)
cb = pd.read_csv("crossborder_pairs.csv")
iso_codes = {c: i + 1 for i, c in enumerate(sorted(set(am.iso3)))}
ALLC = EUR | ROW


def airport_sets(ev, pool):
    lo, hi = ev.tA - 36, ev.tE + 23
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(am[am.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (pool - {ev.iso3}) - busy
    s0 = ya[ya.year == ev.pre_year].set_index("airport_iata") if (ya.year == ev.pre_year).any() else ya[ya.year == ya.year.min()].set_index("airport_iata")
    tq = pd.qcut(s0.seats.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
    return busy, tre, nb, ctrl, s0, tq


def tag(d, ev, nb, s0, tq):
    km = d.airport_iata.map(nb)
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
    d = d[d.grp != "B50"].copy()
    d["treat"] = (d.grp == "T").astype(np.int8)
    d["border"] = (d.grp == "B").astype(np.int8)
    d["w0"] = d.airport_iata.map(s0.seats).fillna(0)
    d["stage0"] = d.airport_iata.map(s0.stage)
    sz = d.airport_iata.map(tq).astype(object)
    for s in ["small", "mid", "large"]:
        d[f"sz_{s}"] = ((sz == s) & (d.treat == 1)).astype(np.int8)
    d["dose"] = np.where(d.treat == 1, [next(v for lim, v in BANDS[ev.iso3] if s <= lim) if pd.notna(s) else np.nan for s in d.stage0], 0.0)
    d["stk"], d["zone"] = ev.stk, ev.zone
    d["ctrl_never"] = d.iso3.isin(NEVER).astype(np.int8)
    d["region"] = d.airport_iata.map(reg).fillna("NA")
    return d


# ---------------- monthly stacks (announcement timing, donut) ----------------
ms, ls = [], []
for _, ev in EV.iterrows():
    busy, tre, nb, ctrl, s0, tq = airport_sets(ev, ALLC)
    lo, hi = ev.tA - 36, ev.tE + 23
    d = am[(am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(nb.index)) & (am.t >= lo) & (am.t <= hi)].copy()
    d = tag(d, ev, nb, s0, tq)
    d["relA"], d["relE"] = d.t - ev.tA, d.t - ev.tE
    d["donut"] = ((d.t >= ev.tA) & (d.t < ev.tE)).astype(np.int8)
    d["post1"], d["post2"] = d.relE.between(0, 11).astype(np.int8), d.relE.between(12, 23).astype(np.int8)
    d["pre36_25"], d["pre24_13"] = d.relA.between(-36, -25).astype(np.int8), d.relA.between(-24, -13).astype(np.int8)
    ms.append(d)
    if ev.zone == "EUR" and ev.iso3 != "NLD":
        units = set(d.airport_iata)
        gr = pd.MultiIndex.from_product([sorted(units), range(lo - 12, ev.tE + 12)], names=["airport_iata", "t"]).to_frame(index=False)
        gr = gr.merge(raw[["airport_iata", "t", "dep_seats"]], on=["airport_iata", "t"], how="left").fillna({"dep_seats": 0})
        lag = gr.copy()
        lag["t"] += 12
        gr = gr.merge(lag.rename(columns={"dep_seats": "seats_m12"}), on=["airport_iata", "t"], how="left")
        gr = gr[(gr.t >= lo) & (gr.seats_m12 > 0) & ~((gr.t >= ev.tA) & (gr.t < ev.tE))].copy()
        gr["loss"] = (gr.dep_seats == 0).astype(np.int8)
        gr["iso3"] = gr.airport_iata.map(d.drop_duplicates("airport_iata").set_index("airport_iata").iso3)
        gr["year"], gr["month"] = (gr.t - 1) // 12, (gr.t - 1) % 12 + 1
        gr = tag(gr, ev, nb, s0, tq)
        gr["post1"] = gr.t.between(ev.tE, ev.tE + 11).astype(np.int8)
        ls.append(gr)
    print(ev.iso3, ev.eff, "stack:", d.airport_iata.nunique(), "airports", flush=True)
M = pd.concat(ms, ignore_index=True)
L = pd.concat(ls, ignore_index=True)
# ---------------- effective-date stacks, 9 European events ----------------
es = []
for _, ev in EV[EV.zone == "EUR"].iterrows():
    busy, tre, nb, ctrl, s0, tq = airport_sets(ev, EUR)
    d = am[(am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(nb.index)) & (am.t >= ev.tE - 36) & (am.t <= ev.tE + 35)].copy()
    d = tag(d, ev, nb, s0, tq)
    d["relE"] = d.t - ev.tE
    d["post"] = (d.relE >= 0).astype(np.int8)
    es.append(d)
EF = pd.concat(es, ignore_index=True)
# ---------------- annual stacks ----------------
ys = []
for _, ev in EV.iterrows():
    busy, tre, nb, ctrl, s0, tq = airport_sets(ev, ALLC)
    d = yy[(yy.iso3.isin(ctrl | {ev.iso3}) | yy.airport_iata.isin(nb.index)) & (yy.year >= ev.E - 3) & (yy.year <= ev.E + 1)].copy()
    d = tag(d, ev, nb, s0, tq)
    d["k"] = d.year - ev.E
    d["post"] = (d.k >= 0).astype(np.int8)
    d["post1"], d["post2"] = (d.k == 0).astype(np.int8), (d.k == 1).astype(np.int8)
    ys.append(d)
YA = pd.concat(ys, ignore_index=True)


def finish(D, monthly, fe_month=True):
    D = D.merge(cy, on=["iso3", "year"], how="left")
    D["iso3n"] = D.iso3.map(iso_codes).astype(np.int16)
    if monthly:
        D["fe_u"] = pd.factorize(D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str))[0] + 1
        D["fe_t"] = pd.factorize(D.t.astype(str) + "_" + D.stk.astype(str))[0] + 1
        D["fe_rt"] = pd.factorize(D.region + "_" + D.t.astype(str) + "_" + D.stk.astype(str))[0] + 1
    else:
        D["fe_u"] = pd.factorize(D.airport_iata + "_" + D.stk.astype(str))[0] + 1
        D["fe_t"] = pd.factorize(D.year.astype(str) + "_" + D.stk.astype(str))[0] + 1
        D["fe_rt"] = pd.factorize(D.region + "_" + D.year.astype(str) + "_" + D.stk.astype(str))[0] + 1
    D["eur"] = (D.zone == "EUR").astype(np.int8)
    return D.rename(columns={"airport_iata": "airport"})


keep_m = ["airport", "iso3", "iso3n", "stk", "eur", "zone", "region", "year", "month", "t", "relA", "relE", "donut", "treat", "border", "post1", "post2", "pre36_25", "pre24_13",
          "sz_small", "sz_mid", "sz_large", "dose", "w0", "lngdp", "lnpop", "ctrl_never", "ln_seats", "ln_co2", "ln_int", "ln_fl", "ln_gauge", "fe_u", "fe_t", "fe_rt"]
finish(M, True)[keep_m].to_stata(os.path.join(OUT, "stack_month.dta"), write_index=False, version=118)
finish(EF, True)[["airport", "iso3", "iso3n", "stk", "year", "month", "t", "relE", "post", "treat", "border", "sz_small", "sz_mid", "sz_large", "w0", "lngdp", "lnpop",
                  "ln_seats", "ln_co2", "ln_int", "fe_u", "fe_t"]].to_stata(os.path.join(OUT, "stack_eff.dta"), write_index=False, version=118)
finish(L, True)[["airport", "iso3", "iso3n", "stk", "year", "month", "t", "treat", "border", "post1", "sz_small", "sz_mid", "sz_large", "lngdp", "lnpop", "loss", "fe_u", "fe_t"]].to_stata(
    os.path.join(OUT, "stack_loss.dta"), write_index=False, version=118)
keep_y = ["airport", "iso3", "iso3n", "stk", "eur", "zone", "region", "year", "k", "post", "post1", "post2", "treat", "border", "sz_small", "sz_mid", "sz_large", "dose", "w0", "lngdp", "lnpop",
          "ctrl_never", "ln_gaci", "ln_deg", "ln_eigen", "ln_betw", "ln_co2", "ln_fl_per_dest", "ln_co2_per_fl", "ln_gauge", "ln_stage", "ln_int", "fe_u", "fe_t", "fe_rt"]
finish(YA, False)[keep_y].to_stata(os.path.join(OUT, "stack_year.dta"), write_index=False, version=118)
# ---------------- SDID panels (country level) ----------------
cmth = am[am.iso3.isin(ALLC)].groupby(["iso3", "year", "month", "t"], as_index=False).agg(seats=("dep_seats", "sum"), co2=("co2_dep", "sum"))
cmth["y_seats"], cmth["y_co2"] = np.log(cmth.seats), np.log(cmth.co2.where(cmth.co2 > 0))
sd = []
for _, ev in EV.iterrows():
    pool = EUR if ev.zone == "EUR" else ALLC
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    don = sorted((pool - {ev.iso3}) - busy)
    d = cmth[cmth.iso3.isin(don + [ev.iso3]) & (cmth.t >= lo) & (cmth.t <= hi) & ~((cmth.t >= ev.tA) & (cmth.t < ev.tE))].copy()
    full = d.groupby("iso3").t.nunique()
    d = d[d.iso3.isin(full[full == full.max()].index)]
    if ev.iso3 not in set(d.iso3):
        continue
    for v in ["y_seats", "y_co2"]:
        seas = d[d.t < ev.tA].groupby(["iso3", "month"])[v].mean().rename("s")
        d = d.merge(seas, left_on=["iso3", "month"], right_index=True, how="left")
        d[v] = d[v] - d.s
        d = d.drop(columns="s")
    d["treat_post"] = ((d.iso3 == ev.iso3) & (d.t >= ev.tE)).astype(np.int8)
    d["treated"] = (d.iso3 == ev.iso3).astype(np.int8)
    d["stk"] = ev.stk
    d["period"] = d.groupby("stk").t.rank(method="dense").astype(int)      # consecutive period index (donut removed)
    sd.append(d)
SD = pd.concat(sd, ignore_index=True)
SD["iso3n"] = SD.iso3.map(iso_codes).astype(np.int16)
SD[["stk", "iso3", "iso3n", "t", "period", "treated", "treat_post", "y_seats", "y_co2"]].to_stata(os.path.join(OUT, "sdid_month.dta"), write_index=False, version=118)
gy = yy[yy.iso3.isin(ALLC)].copy()
gy["w"] = gy.seats
gw = gy.dropna(subset=["ln_gaci"]).groupby(["iso3", "year"]).apply(lambda x: np.average(x.ln_gaci, weights=x.w)).rename("y_gaci").reset_index()
sy = []
for _, ev in EV.iterrows():
    pool = EUR if ev.zone == "EUR" else ALLC
    lo, hi = ev.tA - 36, ev.tE + 23
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    don = sorted((pool - {ev.iso3}) - busy)
    yrs = [y for y in range(ev.E - 6, ev.E + 2) if 1996 <= y <= 2019]
    if ev.E + 1 > 2019 or len([y for y in yrs if y < ev.E]) < 3:
        continue
    d = gw[gw.iso3.isin(don + [ev.iso3]) & gw.year.isin(yrs)].copy()
    full = d.groupby("iso3").year.nunique()
    d = d[d.iso3.isin(full[full == len(yrs)].index)]
    if ev.iso3 not in set(d.iso3):
        continue
    d["treat_post"] = ((d.iso3 == ev.iso3) & (d.year >= ev.E)).astype(np.int8)
    d["treated"] = (d.iso3 == ev.iso3).astype(np.int8)
    d["stk"] = ev.stk
    sy.append(d)
SY = pd.concat(sy, ignore_index=True)
SY["iso3n"] = SY.iso3.map(iso_codes).astype(np.int16)
SY[["stk", "iso3", "iso3n", "year", "treated", "treat_post", "y_gaci"]].to_stata(os.path.join(OUT, "sdid_year.dta"), write_index=False, version=118)
EV[["stk", "iso3", "eff", "ann", "zone", "tE", "tA", "E"]].to_stata(os.path.join(OUT, "events.dta"), write_index=False, version=118)
print("month", M.shape, "| eff", EF.shape, "| loss", L.shape, "| year", YA.shape, "| sdid month", SD.shape, "| sdid year", SY.shape)
print("country controls coverage (month):", round(finish(M, True).lngdp.notna().mean(), 3))
