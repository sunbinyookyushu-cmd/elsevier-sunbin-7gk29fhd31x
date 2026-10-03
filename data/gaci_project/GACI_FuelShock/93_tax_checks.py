# -*- coding: utf-8 -*-
"""Checks on the first-pass ticket-tax DiD (92), organised like Li, Liu, Purevjav & Yang (2019, JEEM 96:213-235):
  T4  before/after means (raw and residualised), treated / border / control       (their Table 5 / Fig. 4)
  T5  event study, quarterly bins t0-12..t0+11 and half-year bins t0-24..t0+23      (their Table 6 / Fig. 5)
  T6  varying windows +-12, 18, 24, 36 months                                         (their Table 11)
  T7  dose: Treat x Post x tax change in EUR per departing short-haul passenger      (their continuous measure)
  T8  excluding events that coincide with other shocks (NLD 2008 and IRL 2009 = financial crisis;
      cuts: AUT 2018 = airberlin/Niki collapse, NOR 2002 = after 9/11)
  T9  connectivity for hubs only (pre-year seats >= 1 million) and seat-weighted: ln GACI, ln eigenvector, ln betweenness
  T10 Design 2: taxes that also charge transfer passengers (ITA 2008-11 approx. and 2013-07 surcharge rises, NOR 1998-04
      seat tax) and the French 2016-01 transfer exemption (a cut for transfers): connectivity of the country's hubs
  Inference: country-clustered SE plus wild cluster restricted bootstrap p-values (Webb weights, 999 draws) for the
  pooled treated coefficients.
Output: _res_tax_checks.csv
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

# ---------------- events ----------------
# dEUR: change in the tax per departing short-haul economy passenger, in EUR (approximate conversion at the event date;
# NOK 80 ~ EUR 8.6, SEK 60 ~ EUR 6.2, GBP 5 ~ EUR 7.4, DKK 75 ~ EUR 10.1 (domestic), Lm10 ~ EUR 23.3)
EV1 = pd.DataFrame([
    ("NLD", "2008-07-01", "increase", 11.25, 1), ("IRL", "2009-03-30", "increase", 2.0, 1), ("DEU", "2011-01-01", "increase", 8.0, 0),
    ("AUT", "2011-04-01", "increase", 8.0, 0), ("NOR", "2016-06-01", "increase", 8.6, 0), ("SWE", "2018-04-01", "increase", 6.2, 0),
    ("GBR", "2007-02-01", "increase", 7.4, 0), ("DNK", "1998-01-01", "increase", 10.1, 0), ("MLT", "2005-08-01", "increase", 23.3, 0),
    ("NLD", "2009-07-01", "cut", -11.25, 0), ("DNK", "2007-01-01", "cut", -5.0, 0), ("MLT", "2008-11-01", "cut", -23.3, 0),
    ("IRL", "2014-04-01", "cut", -3.0, 0), ("ISL", "2011-05-18", "cut", np.nan, 0), ("AUT", "2018-01-01", "cut", -3.5, 1),
    ("NOR", "2002-04-01", "cut", np.nan, 1)], columns=["iso3", "date", "kind", "dEUR", "confounded"])
EV2 = pd.DataFrame([("ITA", "2008-11-01", "transfer-taxed increase"), ("ITA", "2013-07-01", "transfer-taxed increase"),
                    ("NOR", "1998-04-01", "transfer-taxed increase"), ("FRA", "2016-01-01", "transfer exemption (cut)")],
                   columns=["iso3", "date", "kind"])
for E in (EV1, EV2):
    dd = pd.to_datetime(E.date)
    E["t0"], E["E"] = dd.dt.year * 12 + dd.dt.month, np.where(dd.dt.month <= 6, dd.dt.year, dd.dt.year + 1)

CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])

am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "dep_seats_intl"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019) & (am.dep_seats > 0)].copy()
am["t"] = am.year * 12 + am.month
am["ln_seats"] = np.log(am.dep_seats)
am["ln_intl"] = np.log(am.dep_seats_intl.where(am.dep_seats_intl > 0))
cb = pd.read_csv("crossborder_pairs.csv")
cb = cb[cb.km <= 150]
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI", "Eigen", "NorBetweenness", "dep_seats"])
hp = hp[(hp.year <= 2019) & (hp.GACI > 0)].copy()
hp["ln_gaci"] = np.log(hp.GACI)
hp["ln_eigen"] = np.log(hp.Eigen.where(hp.Eigen > 0))
hp["ln_betw"] = np.log1p(hp.NorBetweenness * 1e4)
pre_seats = hp.set_index(["airport_iata", "year"]).dep_seats


def stacks(E, W_pre, W_post, annual=False, exclude_ita=True, ywin=2):
    out = []
    for k, ev in E.iterrows():
        lo, hi = ev.t0 - W_pre, ev.t0 + W_post
        busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
        tre = set(am[am.iso3 == ev.iso3].airport_iata)
        bor = set(cb[cb.airport.isin(tre)].neighbour)
        ctrl = (CODED - ({"ITA"} if exclude_ita else set()) - {ev.iso3}) - busy
        if annual:
            d = hp[(hp.year >= ev.E - ywin) & (hp.year <= ev.E + ywin) & (hp.iso3.isin(ctrl | {ev.iso3}) | hp.airport_iata.isin(bor))].copy()
            d["post"] = (d.year >= ev.E).astype(np.int8)
            d["rel"] = d.year - ev.E
            d["w"] = d.airport_iata.map(pre_seats.xs(ev.E - 1, level="year")).fillna(0)
        else:
            d = am[(am.t >= lo) & (am.t <= hi) & (am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(bor))].copy()
            d["post"] = (d.t >= ev.t0).astype(np.int8)
            d["rel"] = d.t - ev.t0
        d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(d.airport_iata.isin(bor), "B", "C"))
        d["stk"] = k
        out.append(d)
    D = pd.concat(out, ignore_index=True)
    D["tp"] = ((D.grp == "T") & (D.post == 1)).astype(np.int8)
    D["bp"] = ((D.grp == "B") & (D.post == 1)).astype(np.int8)
    if annual:
        D["fe_u"], D["fe_t"] = D.airport_iata + "_" + D.stk.astype(str), D.year.astype(str) + "_" + D.stk.astype(str)
    else:
        D["fe_u"] = D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str)
        D["fe_t"] = D.t.astype(str) + "_" + D.stk.astype(str)
    return D


def wild_p(D, y, test, others, fes=("fe_u", "fe_t"), cl="iso3", reps=999):
    """wild cluster restricted bootstrap (WCR, Webb 6-point weights) p-value for H0: b_test = 0"""
    D = D.dropna(subset=[y, test] + others).reset_index(drop=True)
    codes = np.column_stack([pd.factorize(D[f])[0] for f in fes]).astype(np.uint64)
    A, _ = _pf_demean(D[[y, test] + others].to_numpy(float), codes, np.ones(len(D)))
    yd, X = A[:, 0], A[:, 1:]
    g = pd.factorize(D[cl])[0]
    G = g.max() + 1

    def tstat(yv):
        XtX = np.linalg.inv(X.T @ X)
        b = XtX @ X.T @ yv
        u = yv - X @ b
        S = np.zeros((G, X.shape[1]))
        np.add.at(S, g, X * u[:, None])
        V = XtX @ (S.T @ S) @ XtX * G / (G - 1)
        return b[0] / np.sqrt(V[0, 0])

    t0 = tstat(yd)
    Xo = X[:, 1:]
    br = np.linalg.lstsq(Xo, yd, rcond=None)[0] if Xo.shape[1] else np.zeros(0)
    fit_r = Xo @ br if Xo.shape[1] else np.zeros(len(yd))
    ur = yd - fit_r
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    cnt = 0
    for _ in range(reps):
        w = webb[rng.integers(0, 6, G)][g]
        v, _ = _pf_demean((ur * w)[:, None], codes, np.ones(len(D)))
        cnt += abs(tstat(fit_r + v[:, 0])) >= abs(t0)
    return (cnt + 1) / (reps + 1)


rows = []


def add(table, spec, D, y, rhs, terms, weights=None, cl="iso3", wild=None):
    m = pf.feols(f"{y} ~ {rhs} | fe_u + fe_t", data=D.dropna(subset=[y]), vcov={"CRV1": cl}, weights=weights)
    t = m.tidy()
    for term in terms:
        if term not in t.index:
            continue
        r = dict(table=table, spec=spec, outcome=y, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"],
                 p=t.loc[term, "Pr(>|t|)"], n=int(m._N), clusters=D[cl].nunique())
        if wild and term in wild:
            others = [x.strip() for x in rhs.split("+") if x.strip() != term]
            r["p_wild"] = wild_p(D, y, term, others)
        rows.append(r)


inc = EV1[EV1.kind == "increase"].reset_index(drop=True)
cut = EV1[EV1.kind == "cut"].reset_index(drop=True)
M12 = stacks(inc, 12, 11)

# ---- T4 before/after means ----
for g_ in ["T", "B", "C"]:
    x = M12[M12.grp == g_]
    resid = x.ln_seats - x.groupby("fe_u").ln_seats.transform("mean")
    rows.append(dict(table="T4 before/after", spec=g_, outcome="ln seats", term="pre mean / post mean (raw)",
                     b=x[x.post == 0].ln_seats.mean(), se=x[x.post == 1].ln_seats.mean(), n=len(x)))
    rows.append(dict(table="T4 before/after", spec=g_, outcome="ln seats", term="pre / post residual (airport x cal-month FE)",
                     b=resid[x.post == 0].mean(), se=resid[x.post == 1].mean(), n=len(x)))
print("T4 done", flush=True)

# ---- T5 event study ----
for lab, D, bins in [("quarterly, -12..+11", M12, [(-12, -10), (-9, -7), (-6, -4), (0, 2), (3, 5), (6, 8), (9, 11)]),
                     ("half-year, -24..+23", stacks(inc, 24, 23), [(-24, -19), (-18, -13), (-12, -7), (0, 5), (6, 11), (12, 17), (18, 23)])]:
    names = []
    for a, b in bins:
        for gg in ["T", "B"]:
            nm = f"{gg}_{a}_{b}".replace("-", "m")
            D[nm] = ((D.grp == gg) & (D.rel >= a) & (D.rel <= b)).astype(np.int8)
            names.append(nm)
    add("T5 event study", lab, D, "ln_seats", " + ".join(names), names)
print("T5 done", flush=True)

# ---- T6 windows ----
for w in [12, 18, 24, 36]:   # +-6 is not identified: each airport x calendar-month x stack cell has one observation
    D = M12 if w == 12 else stacks(inc, w, w - 1)
    add("T6 windows", f"+-{w} months", D, "ln_seats", "tp + bp", ["tp", "bp"], wild=["tp"] if w == 12 else None)
print("T6 done", flush=True)

# ---- T7 dose ----
D = M12.copy()
D["dEUR"] = D.stk.map(inc.dEUR)
D["tpE"], D["bpE"] = D.tp * D.dEUR, D.bp * D.dEUR
add("T7 dose", "per EUR of tax", D, "ln_seats", "tpE + bpE", ["tpE", "bpE"])
print("T7 done", flush=True)

# ---- T8 excluding confounded events, and cuts ----
clean = inc[inc.confounded == 0].reset_index(drop=True)
add("T8 clean events", "increases without NLD 2008, IRL 2009", stacks(clean, 12, 11), "ln_seats", "tp + bp", ["tp", "bp"], wild=["tp"])
add("T8 clean events", "cuts, all", stacks(cut, 12, 11), "ln_seats", "tp + bp", ["tp", "bp"])
add("T8 clean events", "cuts without AUT 2018, NOR 2002", stacks(cut[cut.confounded == 0].reset_index(drop=True), 12, 11),
    "ln_seats", "tp + bp", ["tp", "bp"])
print("T8 done", flush=True)

# ---- T9 connectivity: all, hubs only, seat-weighted ----
A = stacks(inc, 12, 11, annual=True)
for y in ["ln_gaci", "ln_eigen", "ln_betw"]:
    add("T9 connectivity", "all airports", A, y, "tp + bp", ["tp", "bp"], wild=["tp"] if y == "ln_gaci" else None)
    add("T9 connectivity", "hubs (pre-year seats >= 1m)", A[A.w >= 1e6], y, "tp + bp", ["tp", "bp"])
    add("T9 connectivity", "seat-weighted", A[A.w > 0], y, "tp + bp", ["tp", "bp"], weights="w")
print("T9 done", flush=True)

# ---- T10 Design 2: transfer-taxed events (Italy treated, so not excluded) ----
for k, ev in EV2.iterrows():
    one = EV2.loc[[k]].reset_index(drop=True)
    A2 = stacks(one, 12, 11, annual=True, exclude_ita=False)
    A2["hub"] = (A2.w >= 5e6).astype(np.int8)
    A2["tph"] = A2.tp * A2.hub
    for y in ["ln_gaci", "ln_eigen", "ln_betw"]:
        add("T10 transfer-taxed", f"{ev.iso3} {ev.date} {ev.kind}", A2, y, "tp + tph + bp", ["tp", "tph"])
    M2 = stacks(one, 12, 11, exclude_ita=False)
    M2["hub"] = M2.airport_iata.map(pre_seats.xs(ev.E - 1, level="year")).fillna(0).ge(5e6).astype(np.int8)
    M2["tph"] = M2.tp * M2.hub
    add("T10 transfer-taxed", f"{ev.iso3} {ev.date} {ev.kind}", M2, "ln_intl", "tp + tph + bp", ["tp", "tph"], cl="airport_iata")
print("T10 done", flush=True)

R = pd.DataFrame(rows)
R.to_csv("_res_tax_checks.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 300)
print(R.round(4).to_string(index=False))
