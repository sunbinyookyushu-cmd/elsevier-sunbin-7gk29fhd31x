# -*- coding: utf-8 -*-
"""Did ticket taxes cut aviation CO2, and where in the network? (user 2026-10-02)
Stacks as in 102 (8 events ex NLD, announcement donut, pre [A-36,A-1], post [E,E+11], border 50-300 km own group).
  A outcomes: ln CO2 (departing flights, LTO + cruise), ln CO2 per seat, ln CO2 per seat-km (fuel intensity),
    ln stage length; by size tercile, unweighted, and seat-weighted (national totals); border group.
  B connectivity as moderator: Treat x Post x pre-year GACI tercile (within treated country) for ln CO2 and ln seats;
    and Treat x Post x (GACI residual on ln seats) = connectivity beyond size.
  C abatement in connectivity units: for each size tercile, CO2 avoided (coefficient x pre-year CO2) per unit of
    connectivity lost (coefficient x pre-year GACI sum, and destinations lost), plus revenue per tonne (dose x pax).
SE country clusters. Output: _res_tax_co2.csv, _res_tax_co2_abatement.csv
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
BANDS = {"DEU": [(2500, 8), (6000, 25), (1e9, 45)], "AUT": [(2500, 8), (6000, 20), (1e9, 35)], "IRL": [(300, 2), (1e9, 10)],
         "SWE": [(2500, 6.2), (6000, 25.8), (1e9, 41.2)], "NOR": [(1e9, 8.6)], "GBR": [(2500, 7.4), (1e9, 29.6)], "DNK": [(1e9, 10.1)], "MLT": [(1e9, 23.3)]}
CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "dep_seat_km", "co2_dep"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019) & (am.dep_seats > 0) & (am.co2_dep > 0)].copy()
am["t"] = am.year * 12 + am.month
am["ln_seats"], am["ln_co2"] = np.log(am.dep_seats), np.log(am.co2_dep)
am["ln_co2_seat"] = am.ln_co2 - am.ln_seats
am["ln_int"] = np.log(am.co2_dep / am.dep_seat_km)
am["ln_stage"] = np.log(am.dep_seat_km / am.dep_seats)
ya = am.groupby(["airport_iata", "year"]).agg(seats=("dep_seats", "sum"), co2=("co2_dep", "sum"), skm=("dep_seat_km", "sum"))
ya["stage"] = ya.skm / ya.seats
gac = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "GACI", "Degree"]).set_index(["airport_iata", "year"])
cb = pd.read_csv("crossborder_pairs.csv")
ms = []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(am[am.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (CODED - {"ITA", ev.iso3}) - busy
    b0 = ya.xs(ev.pre_year, level="year") if ev.pre_year in ya.index.get_level_values(1) else ya.xs(ya.index.get_level_values(1).min(), level="year")
    d = am[(am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(nb.index)) & (am.t >= lo) & (am.t <= hi) & ~((am.t >= ev.tA) & (am.t < ev.tE))].copy()
    km = d.airport_iata.map(nb)
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
    d = d[d.grp != "B50"]
    d["w0"] = d.airport_iata.map(b0.seats).fillna(0)
    d["co20"] = d.airport_iata.map(b0.co2).fillna(0)
    d["stage0"] = d.airport_iata.map(b0.stage)
    g0 = gac.xs(ev.pre_year, level="year") if ev.pre_year in gac.index.get_level_values(1) else gac.xs(gac.index.get_level_values(1).min(), level="year")
    d["gaci0"], d["deg0"] = d.airport_iata.map(g0.GACI), d.airport_iata.map(g0.Degree)
    tsz = pd.qcut(b0.seats.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
    gt = g0.GACI.reindex(list(tre)).dropna()
    tgq = pd.qcut(gt, 3, labels=["lowG", "midG", "highG"]) if len(gt) >= 6 else pd.Series(dtype=object)
    d["size"] = d.airport_iata.map(tsz).astype(object).where(d.grp == "T", "ctrl")
    d["gq"] = d.airport_iata.map(tgq).astype(object).where(d.grp == "T", "ctrl")
    d["dose"] = [next(v for lim, v in BANDS[ev.iso3] if s <= lim) if pd.notna(s) else np.nan for s in d.stage0]
    d["post"], d["stk"] = (d.t >= ev.tE).astype(np.int8), k
    ms.append(d)
M = pd.concat(ms, ignore_index=True)
M["fe_u"] = M.airport_iata + "_" + M.month.astype(str) + "_" + M.stk.astype(str)
M["fe_t"] = M.t.astype(str) + "_" + M.stk.astype(str)
M["tp"], M["bp"] = ((M.grp == "T") & (M.post == 1)).astype(np.int8), ((M.grp == "B") & (M.post == 1)).astype(np.int8)
for s in ["small", "mid", "large"]:
    M[f"tp_{s}"] = ((M["size"] == s) & (M.post == 1)).astype(np.int8)
for g in ["lowG", "midG", "highG"]:
    M[f"tp_{g}"] = ((M.gq == g) & (M.post == 1)).astype(np.int8)
# connectivity beyond size: residual of ln GACI on ln seats among treated airports (pre-year), centred
tr = M[M.grp == "T"].drop_duplicates(["airport_iata", "stk"]).dropna(subset=["gaci0", "w0"])
tr = tr[tr.w0 > 0]
X = np.column_stack([np.ones(len(tr)), np.log(tr.w0)])
beta = np.linalg.lstsq(X, np.log(tr.gaci0), rcond=None)[0]
resid = np.log(tr.gaci0) - X @ beta
M["gres"] = M.set_index(["airport_iata", "stk"]).index.map(dict(zip(zip(tr.airport_iata, tr.stk), resid))).to_numpy()
M["tp_gres"] = M.tp * M.gres.fillna(0)
M["lnw0"] = np.log(M.w0.where(M.w0 > 0))
M["tp_lnw0"] = M.tp * (M.lnw0 - tr.w0.pipe(np.log).mean())
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
GQ = ["tp_lowG", "tp_midG", "tp_highG", "bp"]
for y in ["ln_co2", "ln_co2_seat", "ln_int", "ln_stage", "ln_seats"]:
    est("A all treated, unweighted", M, y, "tp + bp", ["tp", "bp"])
    est("A all treated, seat-weighted", M[M.w0 > 0], y, "tp + bp", ["tp", "bp"], weights="w0")
    est("A by size tercile", M, y, " + ".join(SZ), SZ)
    print(y, "A done", flush=True)
for y in ["ln_co2", "ln_seats"]:
    est("B by pre-year GACI tercile", M, y, " + ".join(GQ), GQ)
    est("B GACI beyond size (residual)", M.dropna(subset=["lnw0"]), y, "tp + tp_lnw0 + tp_gres + bp", ["tp", "tp_lnw0", "tp_gres"])
    print(y, "B done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_tax_co2.csv", index=False)
# ---- C abatement in connectivity units (first year), by size tercile, pooled over events ----
S = pd.read_csv("_res_tax_by_size.csv")
ab = []
base = M[M.grp == "T"].drop_duplicates(["airport_iata", "stk"])
for s in ["small", "mid", "large"]:
    b = base[base["size"] == s]
    bc = R[(R.table == "A by size tercile") & (R.outcome == "ln_co2") & (R.term == f"tp_{s}")].iloc[0]
    bg = S[(S.table == "3 connectivity by size tercile") & (S.outcome == "ln_gaci") & (S.term == f"tp_{s}")].iloc[0]
    bd = S[(S.table == "3 connectivity by size tercile") & (S.outcome == "ln_deg") & (S.term == f"tp_{s}")].iloc[0]
    co2_av = -(np.exp(bc.b) - 1) * b.co20.sum() / 1000           # tonnes
    gaci_lost = -(np.exp(bg.b) - 1) * b.gaci0.sum()
    deg_lost = -(np.exp(bd.b) - 1) * b.deg0.sum()
    rev = (b.dose.fillna(0) * b.w0 * 0.8 * np.exp(bc.b)).sum()
    ab.append(dict(size=s, airports=len(b), co2_coef=bc.b, co2_avoided_kt=co2_av / 1000, gaci_coef=bg.b, gaci_lost=gaci_lost,
                   destinations_lost=deg_lost, revenue_mEUR=rev / 1e6, eur_per_t=rev / co2_av if co2_av > 0 else np.nan,
                   gaci_per_kt=gaci_lost / (co2_av / 1000) if co2_av > 0 else np.nan,
                   destinations_per_kt=deg_lost / (co2_av / 1000) if co2_av > 0 else np.nan))
AB = pd.DataFrame(ab)
AB.to_csv("_res_tax_co2_abatement.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
print("\nAbatement accounting, first tax year, pooled treated airports (load factor 0.80):")
print(AB.round(3).to_string(index=False))
