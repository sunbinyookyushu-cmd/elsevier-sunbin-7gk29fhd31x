# -*- coding: utf-8 -*-
"""Mechanisms behind "small airports lose, hubs do not" (user 2026-10-02: run M1-M4 with current data).
Stacks as in 102 (8+1 events, announcement donut, pre [A-36,A-1], post [E,E+11], border 50-300 km own group).
  M2 tax relative to fare: Treat x Post x (dose / pre-year mean stage length, EUR per 1000 km) and x short-haul
     (pre-year stage < 1000 km); dose from 100 (band rate at pre-year stage length).
  M4 extensive margin by size tercile: ln flights, ln seats per flight, service-loss dummy (seats_(t-12)>0 & seats_t=0,
     months with no record = 0 seats, at-risk months), monthly; destinations already in 102.
  M3 proxies: Treat x Post x LCC-type share (pre-year share of flights with 150-200 seats... not available at flight level;
     proxy = 1[pre-year mean seats per flight in 150-200]) and x seat growth 2002-2007 (pre-boom LCC expansion), centred.
  M1 transfer-taxed events: NOR 1998-04 (per-seat tax, transfers taxed), ITA 2013-07 surcharge rise (international
     transfers taxed), PRT 2021-07 carbon tax (transfers taxed; outcome window ends 2019 -> skipped, data to 2019 here),
     plus FRA 2016-01 transfer exemption (reverse): country-level SDID of hub vs non-hub seats (hub = >= 5m seats),
     each with placebo p; compare with transfer-exempt events from 101.
SE country clusters (M2-M4); placebo inference (M1). Output: _res_tax_mechanisms.csv
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
from scipy.optimize import minimize

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
EV = pd.DataFrame([("NLD", "2008-07-01", "2007-02-01"), ("IRL", "2009-03-30", "2008-10-01"), ("DEU", "2011-01-01", "2010-06-01"),
                   ("AUT", "2011-04-01", "2010-10-01"), ("NOR", "2016-06-01", "2015-12-01"), ("SWE", "2018-04-01", "2017-06-01"),
                   ("GBR", "2007-02-01", "2006-12-01"), ("DNK", "1998-01-01", "1997-05-01"), ("MLT", "2005-08-01", "2004-11-01")],
                  columns=["iso3", "eff", "ann"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
EV["pre_year"] = (EV.tA - 13) // 12
BANDS = {"DEU": [(2500, 8), (6000, 25), (1e9, 45)], "AUT": [(2500, 8), (6000, 20), (1e9, 35)], "NLD": [(2500, 11.25), (1e9, 45)],
         "IRL": [(300, 2), (1e9, 10)], "SWE": [(2500, 6.2), (6000, 25.8), (1e9, 41.2)], "NOR": [(1e9, 8.6)],
         "GBR": [(2500, 7.4), (1e9, 29.6)], "DNK": [(1e9, 10.1)], "MLT": [(1e9, 23.3)]}
CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
raw = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "n_dep_flights",
                                                               "dep_seat_km"]).to_pandas()
raw = raw[raw.iso3.notna() & (raw.year <= 2019)].copy()
raw["t"] = raw.year * 12 + raw.month
am = raw[raw.dep_seats > 0].copy()
am["ln_seats"], am["ln_fl"] = np.log(am.dep_seats), np.log(am.n_dep_flights.where(am.n_dep_flights > 0))
am["ln_gauge"] = am.ln_seats - am.ln_fl
ya = am.groupby(["airport_iata", "year"]).agg(seats=("dep_seats", "sum"), fl=("n_dep_flights", "sum"), skm=("dep_seat_km", "sum"))
ya["stage"], ya["gauge"] = ya.skm / ya.seats, ya.seats / ya.fl
cb = pd.read_csv("crossborder_pairs.csv")
# service-loss grid for treated/control airports: built per stack below from raw (zeros kept via reindex)
rows = []


def est(table, D, y, rhs, terms, cl="iso3"):
    d = D.dropna(subset=[y])
    m = pf.feols(f"{y} ~ {rhs} | fe_u + fe_t", data=d, vcov={"CRV1": cl})
    t = m.tidy()
    for term in terms:
        if term in t.index:
            rows.append(dict(table=table, outcome=y, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"],
                             p=t.loc[term, "Pr(>|t|)"], n=int(m._N), clusters=d[cl].nunique()))


ms, ls = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(am[am.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (CODED - {"ITA", ev.iso3}) - busy
    py = ev.pre_year if ev.pre_year in ya.index.get_level_values(1) else ya.index.get_level_values(1).min()
    b0 = ya.xs(py, level="year")
    g02 = ya.xs(2002, level="year").seats if 2002 < py else None
    units = set(am[am.iso3.isin(ctrl | {ev.iso3})].airport_iata) | set(nb.index)
    d = am[am.airport_iata.isin(units) & (am.t >= lo) & (am.t <= hi) & ~((am.t >= ev.tA) & (am.t < ev.tE))].copy()
    km = d.airport_iata.map(nb)
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
    d = d[d.grp != "B50"]
    d["post"] = (d.t >= ev.tE).astype(np.int8)
    d["stk"] = k
    d["stage0"], d["gauge0"], d["seats0"] = [d.airport_iata.map(b0[c]) for c in ["stage", "gauge", "seats"]]
    d["dose"] = [next(v for lim, v in BANDS[ev.iso3] if s <= lim) if pd.notna(s) else np.nan for s in d.stage0]
    d["dose_km"] = d.dose / (d.stage0 / 1000)
    d["short0"] = (d.stage0 < 1000).astype(float)
    d["lcc0"] = d.gauge0.between(150, 200).astype(float)
    d["g0207"] = np.log(d.seats0 / d.airport_iata.map(g02)) if g02 is not None else np.nan
    tq = pd.qcut(b0.seats.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
    d["size"] = d.airport_iata.map(tq).astype(object).where(d.grp == "T", "ctrl")
    ms.append(d)
    # service loss grid: airports in units with seats in pre-year; months lo..hi
    gr = pd.MultiIndex.from_product([sorted(units & set(b0[b0.seats > 0].index)), range(lo - 12, hi + 1)], names=["airport_iata", "t"]).to_frame(index=False)
    gr = gr.merge(raw[["airport_iata", "t", "dep_seats"]], on=["airport_iata", "t"], how="left").fillna({"dep_seats": 0})
    lagv = gr[["airport_iata", "t", "dep_seats"]].copy()
    lagv["t"] += 12
    gr = gr.merge(lagv, on=["airport_iata", "t"], how="left", suffixes=("", "_m12"))
    gr = gr[(gr.t >= lo) & (gr.dep_seats_m12 > 0) & ~((gr.t >= ev.tA) & (gr.t < ev.tE))].copy()
    gr["loss"] = (gr.dep_seats == 0).astype(float)
    gr["iso3"] = gr.airport_iata.map(am.drop_duplicates("airport_iata").set_index("airport_iata").iso3)
    gr["grp"] = np.where(gr.iso3 == ev.iso3, "T", np.where(gr.airport_iata.map(nb) <= 300, "B", "C"))
    gr = gr[~(gr.airport_iata.map(nb) <= 50)]
    gr["post"], gr["stk"], gr["month"] = (gr.t >= ev.tE).astype(np.int8), k, (gr.t - 1) % 12 + 1
    gr["size"] = gr.airport_iata.map(tq).astype(object).where(gr.grp == "T", "ctrl")
    ls.append(gr)
M, L = pd.concat(ms, ignore_index=True), pd.concat(ls, ignore_index=True)
for D in (M, L):
    D["fe_u"] = D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str)
    D["fe_t"] = D.t.astype(str) + "_" + D.stk.astype(str)
    D["tp"] = ((D.grp == "T") & (D.post == 1)).astype(np.int8)
    D["bp"] = ((D.grp == "B") & (D.post == 1)).astype(np.int8)
    for s in ["small", "mid", "large"]:
        D[f"tp_{s}"] = ((D["size"] == s) & (D.post == 1)).astype(np.int8)
SZ = ["tp_small", "tp_mid", "tp_large", "bp"]
# ---- M2 ----
tr = M[M.grp == "T"].drop_duplicates(["airport_iata", "stk"])
for v in ["dose_km", "short0", "lcc0", "g0207"]:
    M[v + "_c"] = M[v] - tr[v].mean()
    M["tp_" + v] = M.tp * M[v + "_c"]
est("M2 tax per km", M, "ln_seats", "tp + tp_dose_km + bp", ["tp", "tp_dose_km"])
est("M2 short-haul (<1000 km)", M, "ln_seats", "tp + tp_short0 + bp", ["tp", "tp_short0"])
print("M2 done", flush=True)
# ---- M4 ----
est("M4 flights by size", M, "ln_fl", " + ".join(SZ), SZ)
est("M4 seats per flight by size", M, "ln_gauge", " + ".join(SZ), SZ)
est("M4 service loss by size (at-risk months, LPM)", L, "loss", " + ".join(SZ), SZ)
print("M4 done", flush=True)
# ---- M3 proxies ----
est("M3 LCC-type gauge (150-200 seats/flight)", M, "ln_seats", "tp + tp_lcc0 + bp", ["tp", "tp_lcc0"])
est("M3 seat growth 2002-07", M.dropna(subset=["g0207_c"]), "ln_seats", "tp + tp_g0207 + bp", ["tp", "tp_g0207"])
est("M3 LCC-type x size", M, "ln_seats", " + ".join(SZ) + " + tp_lcc0", SZ + ["tp_lcc0"])
print("M3 done", flush=True)


# ---- M1: transfer-taxed events, country-level SDID of hub vs non-hub seats ----
def simplex_min(A, b, ridge=0.0, intercept=True):
    n = A.shape[1]

    def f(x):
        w, w0 = x[:n], (x[n] if intercept else 0.0)
        r = w0 + A @ w - b
        return r @ r + ridge * (w @ w)

    x0 = np.r_[np.ones(n) / n, [0.0]] if intercept else np.ones(n) / n
    r = minimize(f, x0, method="SLSQP", bounds=[(0, 1)] * n + ([(None, None)] if intercept else []),
                 constraints=[{"type": "eq", "fun": lambda x: x[:n].sum() - 1}], options={"maxiter": 500, "ftol": 1e-12})
    return r.x[:n]


def sdid(Y, tr_, pre_idx, post_idx):
    don = [u for u in Y.index if u != tr_]
    Yp, Yq = Y.loc[don, pre_idx].to_numpy(), Y.loc[don, post_idx].to_numpy()
    yt_p, yt_q = Y.loc[tr_, pre_idx].to_numpy(), Y.loc[tr_, post_idx].to_numpy()
    zeta = (len(post_idx)) ** 0.25 * np.diff(Yp, axis=1).std()
    w = simplex_min(Yp.T, yt_p, ridge=zeta ** 2 * len(pre_idx))
    lam = simplex_min(Yp, Yq.mean(axis=1))
    return (yt_q.mean() - yt_p @ lam) - (w @ (Yq.mean(axis=1) - Yp @ lam))


hub_set = set(ya.xs(2007, level="year").query("seats >= 5e6").index)
raw["hub"] = raw.airport_iata.isin(hub_set)
cmh = raw[raw.iso3.isin(CODED)].groupby(["iso3", "hub", "year", "month"], as_index=False).dep_seats.sum()
cmh["t"] = cmh.year * 12 + cmh.month
M1 = pd.DataFrame([("NOR", "1998-04-01", "1998-04-01", "per-seat tax, transfers taxed (increase)"),
                   ("ITA", "2013-07-01", "2013-07-01", "surcharge +EUR 2, intl transfers taxed (increase)"),
                   ("FRA", "2016-01-01", "2016-01-01", "TAC connecting passengers exempted (cut for transfers)"),
                   ("DEU", "2011-01-01", "2010-06-01", "reference: transfer-exempt increase"),
                   ("SWE", "2018-04-01", "2017-06-01", "reference: transfer-exempt increase")], columns=["iso3", "eff", "ann", "what"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(M1[s])
    M1[c] = dd.dt.year * 12 + dd.dt.month
for k, ev in M1.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3) - {ev.iso3}
    for hub in [True, False]:
        d = cmh[(cmh.hub == hub) & (cmh.t >= lo) & (cmh.t <= hi) & (cmh.iso3.isin((CODED - busy)) | (cmh.iso3 == ev.iso3))].copy()
        if ev.iso3 != "ITA":
            d = d[d.iso3 != "ITA"]
        d = d[d.dep_seats > 0]
        d["y"] = np.log(d.dep_seats)
        full = d.groupby("iso3").t.nunique()
        d = d[d.iso3.isin(full[full == full.max()].index)]
        if ev.iso3 not in set(d.iso3):
            rows.append(dict(table="M1 transfer-taxed SDID", outcome=f"{'hub' if hub else 'non-hub'} seats", term=f"{ev.iso3} {ev.eff} {ev.what}", b=np.nan))
            continue
        seas = d[d.t < ev.tA].groupby(["iso3", "month"]).y.mean().rename("s")
        d = d.merge(seas, left_on=["iso3", "month"], right_index=True, how="left")
        d["yd"] = d.y - d.s
        Y = d.pivot(index="iso3", columns="t", values="yd").dropna()
        pre_idx, post_idx = [t for t in Y.columns if t < ev.tA], [t for t in Y.columns if t >= ev.tE]
        if ev.iso3 not in Y.index or len(Y) < 6:
            continue
        tau = sdid(Y, ev.iso3, pre_idx, post_idx)
        plac = np.array([sdid(Y.drop(index=ev.iso3), u, pre_idx, post_idx) for u in Y.index if u != ev.iso3])
        rows.append(dict(table="M1 transfer-taxed SDID", outcome=f"{'hub' if hub else 'non-hub'} seats",
                         term=f"{ev.iso3} {ev.eff} {ev.what}", b=tau, se=plac.std(), p=(np.abs(plac) >= abs(tau)).mean(), n=len(Y) - 1))
print("M1 done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_tax_mechanisms.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_colwidth", 70)
print(R.round(4).to_string(index=False))
