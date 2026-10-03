# -*- coding: utf-8 -*-
"""GACI: parallel-trend table and SDID by event (user 2026-10-02).
A Event study on annual ln GACI (and ln destinations): airport x event and year x event FE; event years relative to the
  effective year E: -3, -2 (reference -1), 0, +1; 8 events ex NLD (NLD separately); all treated and by size tercile;
  border 50-300 km own group. Pre-year taken as the calendar year before the announcement for terciles.
B SDID per event on the COUNTRY mean of ln GACI (seat-weighted mean over the country's airports, so hubs dominate) and
  on the unweighted mean (every airport counts once), annual 1996-2019: pre years E-6..E-1, post E and E+1; donors =
  coded European countries with no tax event in [A-36 m, E+23 m]; placebo p over donors.
Output: _res_tax_gaci_pretrend.csv, _res_tax_gaci_sdid.csv
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
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI", "Degree", "dep_seats"])
hp = hp[(hp.year <= 2019) & (hp.GACI > 0) & hp.iso3.notna()].copy()
hp["ln_gaci"], hp["ln_deg"] = np.log(hp.GACI), np.log(hp.Degree.where(hp.Degree > 0))
seats_y = hp.set_index(["airport_iata", "year"]).dep_seats
cb = pd.read_csv("crossborder_pairs.csv")
rows = []


def est(table, D, y, rhs, terms):
    d = D.dropna(subset=[y])
    m = pf.feols(f"{y} ~ {rhs} | fe_u + fe_t", data=d, vcov={"CRV1": "iso3"})
    t = m.tidy()
    for term in terms:
        if term in t.index:
            rows.append(dict(table=table, outcome=y, term=term, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"],
                             p=t.loc[term, "Pr(>|t|)"], n=int(m._N), clusters=d.iso3.nunique()))


def stacks(E):
    out = []
    for k, ev in E.iterrows():
        lo, hi = ev.tA - 36, ev.tE + 23
        busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
        tre = set(hp[hp.iso3 == ev.iso3].airport_iata)
        nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
        ctrl = (CODED - {"ITA", ev.iso3}) - busy
        d = hp[(hp.iso3.isin(ctrl | {ev.iso3}) | hp.airport_iata.isin(nb.index)) & (hp.year >= ev.E - 3) & (hp.year <= ev.E + 1)].copy()
        km = d.airport_iata.map(nb)
        d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
        d = d[d.grp != "B50"]
        s0 = seats_y.xs(ev.pre_year, level="year") if ev.pre_year in seats_y.index.get_level_values(1) else seats_y.xs(seats_y.index.get_level_values(1).min(), level="year")
        tq = pd.qcut(s0.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
        d["size"] = d.airport_iata.map(tq).astype(object).where(d.grp == "T", "ctrl")
        d["k"], d["stk"] = d.year - ev.E, k
        out.append(d)
    D = pd.concat(out, ignore_index=True)
    D["fe_u"], D["fe_t"] = D.airport_iata + "_" + D.stk.astype(str), D.year.astype(str) + "_" + D.stk.astype(str)
    return D


D = stacks(EV[EV.iso3 != "NLD"].reset_index(drop=True))
KS = [-3, -2, 0, 1]
names = []
for kk in KS:
    nm = f"T_k{kk}".replace("-", "m")
    D[nm] = ((D.grp == "T") & (D.k == kk)).astype(np.int8)
    names.append(nm)
    for s in ["small", "mid", "large"]:
        D[f"{s}_k{kk}".replace("-", "m")] = ((D["size"] == s) & (D.k == kk)).astype(np.int8)
    D[f"B_k{kk}".replace("-", "m")] = ((D.grp == "B") & (D.k == kk)).astype(np.int8)
bn = [f"B_k{kk}".replace("-", "m") for kk in KS]
for y in ["ln_gaci", "ln_deg"]:
    est("A event study, all treated", D, y, " + ".join(names + bn), names + bn)
    sn = [f"{s}_k{kk}".replace("-", "m") for s in ["small", "mid", "large"] for kk in KS]
    est("A event study, by size", D, y, " + ".join(sn + bn), sn)
print("A done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_tax_gaci_pretrend.csv", index=False)


# ---------------- B: SDID on country GACI ----------------
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
    return (yt_q.mean() - yt_p @ lam) - (w @ (Yq.mean(axis=1) - Yp @ lam)), w, don


hpc = hp[hp.iso3.isin(CODED)].copy()
hpc["w"] = hpc.dep_seats.fillna(0)
cw = hpc.groupby(["iso3", "year"]).apply(lambda x: np.average(x.ln_gaci, weights=x.w) if x.w.sum() > 0 else np.nan).rename("gw")
cu = hpc.groupby(["iso3", "year"]).ln_gaci.mean().rename("gu")
C = pd.concat([cw, cu], axis=1).reset_index()
srows = []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 23
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    don = sorted((CODED - {"ITA", ev.iso3}) - busy)
    pre_idx, post_idx = [y for y in range(ev.E - 6, ev.E) if y >= 1996], [ev.E, ev.E + 1]
    if post_idx[-1] > 2019 or len(pre_idx) < 3:
        continue
    for col, lab in [("gw", "seat-weighted country GACI"), ("gu", "unweighted country GACI")]:
        Y = C[C.iso3.isin(don + [ev.iso3])].pivot(index="iso3", columns="year", values=col).reindex(columns=pre_idx + post_idx).dropna()
        if ev.iso3 not in Y.index or len(Y) < 6:
            continue
        tau, w, dn = sdid(Y, ev.iso3, pre_idx, post_idx)
        plac = np.array([sdid(Y.drop(index=ev.iso3), u, pre_idx, post_idx)[0] for u in Y.index if u != ev.iso3])
        top = ", ".join(f"{d} {v:.2f}" for d, v in sorted(zip(dn, w), key=lambda z: -z[1])[:3])
        srows.append(dict(event=f"{ev.iso3} {ev.eff}", outcome=lab, donors=len(Y) - 1, sdid=tau, p_placebo=(np.abs(plac) >= abs(tau)).mean(),
                          placebo_sd=plac.std(), top_donors=top))
    print(ev.iso3, "SDID done", flush=True)
S = pd.DataFrame(srows)
S.to_csv("_res_tax_gaci_sdid.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
print(S.round(4).to_string(index=False))
