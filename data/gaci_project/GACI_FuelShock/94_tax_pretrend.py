# -*- coding: utf-8 -*-
"""Pre-trend treatment for the ticket-tax DiD (user 2026-10-02: announcement dates, donut, country/airport trends,
HonestDiD sensitivity). The 93 event study showed seats falling 6-12 months before the effective date.

Announcement dates (first public decision; from the coded tax files, notes say which are unverified):
  NLD 2007-02 (coalition agreement), IRL 2008-10 (Budget 2009, month only), DEU 2010-06 (cabinet savings package; tickets
  taxed from 2010-09), AUT 2011-01 (law in force; earlier budget announcement not verified -> conservative),
  NOR 2015-12 (Storting decision 14 Dec 2015), SWE 2017-06 (2017-06-08), GBR 2006-12 (Pre-Budget Report, not verified),
  DNK 1997-05 (bill tabled 6 May 1997), MLT 2004-12 (Budget 2005, month approximate).
S1 effective-date event study with ANNUAL bins (each bin holds every calendar month once): [E-24,E-13] vs ref [E-12,E-1].
S2 donut on the announcement: months between announcement A and effective date E dropped; reference = [A-12,A-1];
   pre-trend bin [A-24,A-13]; post bins [E,E+11], [E+12,E+23]; single DiD = post vs pre-announcement.
S3 S2 after removing each airport's own linear trend estimated on [A-24,A-1] (with airport x calendar-month means), i.e.
   pre-announcement trends extrapolated (country- and airport-specific trends).
S4 HonestDiD-style relative-magnitudes bound on S2/S3: post-period bias allowed up to M x |pre-trend coefficient|;
   conservative CI = b_post -/+ (M |b_pre| + 1.96 se_post); breakdown M* where the CI first includes 0.
   (Exact Rambachan-Roth intervals need the honestdid package in Stata/R; this is the conservative envelope.)
Treated, border (<=150 km) and control groups as in 92/93; controls have no coded event within [A-36, E+23].
SE country clusters; WCR wild bootstrap (Webb, 999) for the single DiD coefficients.
Output: _res_tax_pretrend.csv
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
from pyfixest.estimation import demean as _pf_demean

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
rng = np.random.default_rng(20261002)
EV = pd.DataFrame([("NLD", "2008-07-01", "2007-02-01", 1), ("IRL", "2009-03-30", "2008-10-01", 0), ("DEU", "2011-01-01", "2010-06-01", 1),
                   ("AUT", "2011-04-01", "2011-01-01", 0), ("NOR", "2016-06-01", "2015-12-01", 1), ("SWE", "2018-04-01", "2017-06-01", 1),
                   ("GBR", "2007-02-01", "2006-12-01", 0), ("DNK", "1998-01-01", "1997-05-01", 1), ("MLT", "2005-08-01", "2004-12-01", 0)],
                  columns=["iso3", "eff", "ann", "ann_verified"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
EV["lead_months"] = EV.tE - EV.tA

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
cb = pd.read_csv("crossborder_pairs.csv")
cb = cb[cb.km <= 150]

out = []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 24, ev.tE + 23
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(am[am.iso3 == ev.iso3].airport_iata)
    bor = set(cb[cb.airport.isin(tre)].neighbour)
    ctrl = (CODED - {"ITA", ev.iso3}) - busy
    d = am[(am.t >= min(lo, ev.tE - 24)) & (am.t <= hi) & (am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(bor))].copy()
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(d.airport_iata.isin(bor), "B", "C"))
    d["stk"], d["relE"], d["relA"] = k, d.t - ev.tE, d.t - ev.tA
    d["donut"] = ((d.t >= ev.tA) & (d.t < ev.tE)).astype(np.int8)
    out.append(d)
    print(f"{ev.iso3} eff {ev.eff} ann {ev.ann} lead {ev.lead_months} m; controls {len(ctrl)}", flush=True)
D = pd.concat(out, ignore_index=True)
D["fe_u"] = D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str)
D["fe_t"] = D.t.astype(str) + "_" + D.stk.astype(str)


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
    fit_r = Xo @ np.linalg.lstsq(Xo, yd, rcond=None)[0] if Xo.shape[1] else np.zeros(len(yd))
    ur = yd - fit_r
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    cnt = 0
    for _ in range(reps):
        v, _ = _pf_demean((ur * webb[rng.integers(0, 6, G)][g])[:, None], codes, np.ones(len(Dd)))
        cnt += abs(tstat(fit_r + v[:, 0])) >= abs(t0)
    return (cnt + 1) / (reps + 1)


rows = []


def run(spec, Dd, y, bins, single=True):
    names = []
    for lab, cond in bins:
        for gg in ["T", "B"]:
            nm = f"{gg}_{lab}"
            Dd[nm] = ((Dd.grp == gg) & cond(Dd)).astype(np.int8)
            names.append(nm)
    m = pf.feols(f"{y} ~ {' + '.join(names)} | fe_u + fe_t", data=Dd, vcov={"CRV1": "iso3"})
    t = m.tidy()
    for nm in names:
        if nm in t.index:
            rows.append(dict(spec=spec, term=nm, b=t.loc[nm, "Estimate"], se=t.loc[nm, "Std. Error"], p=t.loc[nm, "Pr(>|t|)"],
                             n=int(m._N), clusters=Dd.iso3.nunique()))
    if single:
        Dd["tp"] = ((Dd.grp == "T") & Dd.postflag).astype(np.int8)
        Dd["bp"] = ((Dd.grp == "B") & Dd.postflag).astype(np.int8)
        m = pf.feols(f"{y} ~ tp + bp | fe_u + fe_t", data=Dd, vcov={"CRV1": "iso3"})
        t = m.tidy()
        for nm in ["tp", "bp"]:
            r = dict(spec=spec + " | single DiD", term=nm, b=t.loc[nm, "Estimate"], se=t.loc[nm, "Std. Error"],
                     p=t.loc[nm, "Pr(>|t|)"], n=int(m._N), clusters=Dd.iso3.nunique())
            if nm == "tp":
                r["p_wild"] = wild_p(Dd, y, "tp", ["bp"])
            rows.append(r)


# S1: effective date, annual bins, window [E-24, E+23]
S1 = D[(D.relE >= -24) & (D.relE <= 23)].copy()
S1["postflag"] = S1.relE >= 0
run("S1 effective date, annual bins", S1, "ln_seats",
    [("pre_E24_13", lambda x: x.relE.between(-24, -13)), ("post_0_11", lambda x: x.relE.between(0, 11)),
     ("post_12_23", lambda x: x.relE.between(12, 23))])
print("S1 done", flush=True)

# S2: announcement donut
S2 = D[(D.relA >= -24) & (D.donut == 0) & (D.relE <= 23)].copy()
S2["postflag"] = S2.relE >= 0
run("S2 announcement donut", S2, "ln_seats",
    [("pre_A24_13", lambda x: x.relA.between(-24, -13)), ("post_0_11", lambda x: x.relE.between(0, 11)),
     ("post_12_23", lambda x: x.relE.between(12, 23))])
print("S2 done", flush=True)

# S3: S2 after removing each airport's pre-announcement linear trend
S3 = S2.copy()
pre = S3[S3.relA.between(-24, -1)].copy()
pre["tc"] = pre.t - pre.groupby(["airport_iata", "stk"]).t.transform("mean")
pre["ym"] = pre.ln_seats - pre.groupby("fe_u").ln_seats.transform("mean")
pre["tm"] = pre.t - pre.groupby("fe_u").t.transform("mean")
gg = pre.groupby(["airport_iata", "stk"])
slope = (gg.apply(lambda x: (x.tm * x.ym).sum() / (x.tm ** 2).sum() if (x.tm ** 2).sum() > 0 and len(x) >= 12 else np.nan)).rename("slope")
S3 = S3.merge(slope.reset_index(), on=["airport_iata", "stk"], how="left").dropna(subset=["slope"])
S3["y_dt"] = S3.ln_seats - S3.slope * S3.t
S3["postflag"] = S3.relE >= 0
run("S3 donut + airport pre-trends removed", S3, "y_dt",
    [("pre_A24_13", lambda x: x.relA.between(-24, -13)), ("post_0_11", lambda x: x.relE.between(0, 11)),
     ("post_12_23", lambda x: x.relE.between(12, 23))])
print("S3 done", flush=True)

R = pd.DataFrame(rows)
# S4: relative-magnitudes envelope
for spec in ["S2 announcement donut", "S3 donut + airport pre-trends removed"]:
    r = R[R.spec == spec].set_index("term")
    bpre = abs(r.loc["T_pre_A24_13", "b"])
    for post in ["T_post_0_11", "T_post_12_23"]:
        b, se = r.loc[post, "b"], r.loc[post, "se"]
        Mstar = max((abs(b) - 1.96 * se) / bpre, 0) if bpre > 0 else np.inf
        for M in [0, 0.5, 1, 2]:
            half = M * bpre + 1.96 * se
            R = pd.concat([R, pd.DataFrame([dict(spec=f"S4 sensitivity on {spec}", term=f"{post} M={M}", b=b, se=se,
                                                 ci_lo=b - half, ci_hi=b + half, breakdown_M=Mstar)])], ignore_index=True)
R.to_csv("_res_tax_pretrend.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 200)
print(EV[["iso3", "eff", "ann", "lead_months", "ann_verified"]].to_string(index=False))
print(R.round(4).to_string(index=False))
