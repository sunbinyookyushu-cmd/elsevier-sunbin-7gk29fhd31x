# -*- coding: utf-8 -*-
"""Ticket-tax DiD, main specification after the user's decisions (2026-10-02):
  - event time from the announcement A with a donut (months A..E-1 dropped), annual bins, THREE pre-years:
    pre [A-36,A-25], [A-24,A-13], reference [A-12,A-1]; post [E,E+11] (main), [E+12,E+23] (appendix)
  - main single DiD = first post year [E,E+11] against [A-36,A-1]
  - NLD 2008: intro (2008-07) and rate zero (2009-07) estimated as one episode: tax year and the 18 months after removal
  - border rings 0-50, 50-150, 150-300 km (each its own group, never controls); border airports split into hubs
    (pre-year seats >= 5 million) and secondary airports
  - exports the stacked data and a Stata do-file for exact HonestDiD intervals (stata_tax/)
Announcement dates as in 94 (AUT, GBR unverified; IRL, MLT month approximations) until the verification agent reports.
SE country clusters; WCR wild bootstrap (Webb, 999) for the main coefficient.
Output: _res_tax_main.csv, stata_tax/tax_es_stack.dta, stata_tax/tax_honestdid.do
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import io
import os
import sys
import warnings

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyfixest as pf
from pyfixest.estimation import demean as _pf_demean

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
rng = np.random.default_rng(20261002)
EV = pd.DataFrame([("NLD", "2008-07-01", "2007-02-01"), ("IRL", "2009-03-30", "2008-10-01"), ("DEU", "2011-01-01", "2010-06-01"),
                   ("AUT", "2011-04-01", "2010-10-01"), ("NOR", "2016-06-01", "2015-12-01"), ("SWE", "2018-04-01", "2017-06-01"),
                   ("GBR", "2007-02-01", "2006-12-01"), ("DNK", "1998-01-01", "1997-05-01"), ("MLT", "2005-08-01", "2004-11-01")],
# announcement dates verified from primary sources 2026-10-02 (announcement_dates_verified.csv)
                  columns=["iso3", "eff", "ann"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
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


def build(E, extra_lo=0):
    out = []
    for k, ev in E.iterrows():
        lo, hi = ev.tA - 36 - extra_lo, ev.tE + 23
        busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
        tre = set(am[am.iso3 == ev.iso3].airport_iata)
        nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
        ctrl = (CODED - {"ITA", ev.iso3}) - busy
        d = am[(am.t >= lo) & (am.t <= hi) & (am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(nb.index))].copy()
        km = d.airport_iata.map(nb)
        d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 150, "B150", np.where(km <= 300, "B300", "C"))))
        pre_y = (ev.tA - 13) // 12
        big = d.airport_iata.map(ys.xs(pre_y, level="year") if pre_y in ys.index.get_level_values(1) else pd.Series(dtype=float)).fillna(0) >= 5e6
        d["bhub"] = (d.grp.isin(["B50", "B150"]) & big).astype(np.int8)
        d["stk"], d["relA"], d["relE"] = k, d.t - ev.tA, d.t - ev.tE
        d = d[~((d.t >= ev.tA) & (d.t < ev.tE))]                                       # donut
        out.append(d)
    D = pd.concat(out, ignore_index=True)
    D["fe_u"] = D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str)
    D["fe_t"] = D.t.astype(str) + "_" + D.stk.astype(str)
    return D


def wild_p(Dd, y, test, others, reps=999):
    Dd = Dd.dropna(subset=[y, test] + others).reset_index(drop=True)
    codes = np.column_stack([pd.factorize(Dd[f])[0] for f in ["fe_u", "fe_t"]]).astype(np.uint64)
    A, _ = _pf_demean(Dd[[y, test] + others].to_numpy(float), codes, np.ones(len(Dd)))
    yd, X = A[:, 0], A[:, 1:]
    g = pd.factorize(Dd.iso3)[0]
    G = g.max() + 1

    def tstat(yv):
        XtX = np.linalg.inv(X.T @ X)
        b = XtX @ X.T @ yv
        u = yv - X @ b
        S = np.zeros((G, X.shape[1]))
        np.add.at(S, g, X * u[:, None])
        return b[0] / np.sqrt((XtX @ (S.T @ S) @ XtX)[0, 0] * G / (G - 1))

    t0 = tstat(yd)
    Xo = X[:, 1:]
    fit_r = Xo @ np.linalg.lstsq(Xo, yd, rcond=None)[0]
    ur = yd - fit_r
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    cnt = 0
    for _ in range(reps):
        v, _ = _pf_demean((ur * webb[rng.integers(0, 6, G)][g])[:, None], codes, np.ones(len(Dd)))
        cnt += abs(tstat(fit_r + v[:, 0])) >= abs(t0)
    return (cnt + 1) / (reps + 1)


rows = []


def est(table, spec, D, rhs, terms, wild=None):
    m = pf.feols(f"ln_seats ~ {rhs} | fe_u + fe_t", data=D, vcov={"CRV1": "iso3"})
    t = m.tidy()
    for term in terms:
        if term in t.index:
            r = dict(table=table, spec=spec, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"],
                     p=t.loc[term, "Pr(>|t|)"], n=int(m._N), clusters=D.iso3.nunique())
            if wild and term in wild:
                r["p_wild"] = wild_p(D, "ln_seats", term, [x for x in rhs.split(" + ") if x != term])
            rows.append(r)


inc = EV[EV.iso3 != "NLD"].reset_index(drop=True)          # NLD analysed separately (tax removed after 12 months)
D = build(inc)
G = ["T", "B50", "B150", "B300"]
bins = {"pre36_25": lambda x: x.relA.between(-36, -25), "pre24_13": lambda x: x.relA.between(-24, -13),
        "post0_11": lambda x: x.relE.between(0, 11), "post12_23": lambda x: x.relE.between(12, 23)}
for g in G:
    for b, f in bins.items():
        D[f"{g}_{b}"] = ((D.grp == g) & f(D)).astype(np.int8)
es_terms = [f"{g}_{b}" for g in G for b in bins]
est("ES", "8 events (ex NLD), donut, annual bins", D, " + ".join(es_terms), es_terms)
print("ES done", flush=True)

# main single DiD: first post year vs pre-announcement (drop second post year)
D1 = D[~D.relE.between(12, 23)].copy()
for g in G:
    D1[f"{g}_p"] = ((D1.grp == g) & D1.relE.between(0, 11)).astype(np.int8)
est("MAIN", "first post year vs [A-36,A-1]", D1, " + ".join(f"{g}_p" for g in G), [f"{g}_p" for g in G], wild=["T_p"])
# border hubs vs secondary (rings <=150)
D1["Bh_p"] = ((D1.grp.isin(["B50", "B150"])) & (D1.bhub == 1) & D1.relE.between(0, 11)).astype(np.int8)
D1["Bs_p"] = ((D1.grp.isin(["B50", "B150"])) & (D1.bhub == 0) & D1.relE.between(0, 11)).astype(np.int8)
est("BORDER TYPE", "border <=150 km: hubs vs secondary", D1, "T_p + Bh_p + Bs_p + B300_p", ["T_p", "Bh_p", "Bs_p", "B300_p"])
print("MAIN done", flush=True)

# NLD episode: tax year [2008-07, 2009-06] and after removal [2009-07, 2010-12], vs [A-36, A-1]
nl = EV[EV.iso3 == "NLD"].reset_index(drop=True)
N = build(nl)
N = N[N.t <= 2010 * 12 + 12]
tax = N.t.between(2008 * 12 + 7, 2009 * 12 + 6)
aft = N.t.between(2009 * 12 + 7, 2010 * 12 + 12)
for g in G:
    N[f"{g}_tax"] = ((N.grp == g) & tax).astype(np.int8)
    N[f"{g}_after"] = ((N.grp == g) & aft).astype(np.int8)
nt = [f"{g}_{p}" for g in G for p in ["tax", "after"]]
est("NLD", "tax year and 18 months after removal", N, " + ".join(nt), nt)
print("NLD done", flush=True)

R = pd.DataFrame(rows)
R.to_csv("_res_tax_main.csv", index=False)

# ---------- Stata export for HonestDiD ----------
os.makedirs("stata_tax", exist_ok=True)
X = D[["ln_seats", "iso3"] + es_terms].copy()
X["fe_u"] = pd.factorize(D.fe_u)[0] + 1
X["fe_t"] = pd.factorize(D.fe_t)[0] + 1
X["iso3n"] = pd.factorize(D.iso3)[0] + 1
X.to_stata("stata_tax/tax_es_stack.dta", write_index=False, version=118)
do = r"""* =====================================================================
* Ticket taxes: event study and HonestDiD (Rambachan and Roth 2023)
* Data: tax_es_stack.dta from 95_tax_main.py (8 events, NLD analysed separately)
* Event time from the announcement with a donut; annual bins:
*   pre  T_pre36_25 (A-36..A-25), T_pre24_13 (A-24..A-13); reference A-12..A-1
*   post T_post0_11 (E..E+11), T_post12_23 (E+12..E+23)
* Border rings B50, B150, B300 enter as separate groups.
* FE airport x calendar month x stack and month x stack; SE by country.
* Needs reghdfe, ftools, honestdid (installed below if missing).
* =====================================================================
clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_tax"
cap log close
log using "tax_honestdid_run.log", replace text
cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which honestdid
if _rc net install honestdid, from("https://raw.githubusercontent.com/mcaceresb/stata-honestdid/main") replace
use "tax_es_stack.dta", clear
reghdfe ln_seats T_pre36_25 T_pre24_13 T_post0_11 T_post12_23 B50_pre36_25 B50_pre24_13 B50_post0_11 B50_post12_23 B150_pre36_25 B150_pre24_13 B150_post0_11 B150_post12_23 B300_pre36_25 B300_pre24_13 B300_post0_11 B300_post12_23, absorb(fe_u fe_t) vce(cluster iso3n)
* relative magnitudes: post-period violations up to Mbar times the largest pre-period violation
honestdid, pre(1/2) post(3/4) mvec(0(0.5)2) delta(rm)
* smoothness: deviations from a linear pre-trend bounded by M (log points per year)
honestdid, pre(1/2) post(3/4) mvec(0(0.01)0.05)
log close
"""
with open("stata_tax/tax_honestdid.do", "wb") as fh:
    fh.write(do.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
