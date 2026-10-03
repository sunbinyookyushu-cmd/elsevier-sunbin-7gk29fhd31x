# -*- coding: utf-8 -*-
"""Synthetic difference-in-differences per tax event (user decision 2026-10-02, option A), Arkhangelsky, Athey, Hirshberg,
Imbens & Wager (2021, AER). Country x month panel of ln departing seats (all airports of the country), de-seasonalised
with country x calendar-month means over the pre-announcement window.
  Treated unit: the taxing country. Donors: coded European countries with no coded tax event within [A-36, E+23]
  (Italy excluded). Pre period [A-36, A-1]; announcement-to-effective months dropped (donut); post [E, E+11].
  Unit weights: argmin ||w0 + Y_pre_donors w - Y_pre_treated||^2 + zeta^2 T_pre ||w||^2, w on the simplex,
  zeta = (N_tr T_post)^(1/4) sigma, sigma = sd of first differences of donor pre outcomes (paper's rule).
  Time weights: argmin ||l0 + Y_pre l - mean Y_post||^2 over donors, l on the simplex.
  tau_sdid = (Ybar_tr_post - sum_t l_t Y_tr_t) - sum_j w_j (Ybar_j_post - sum_t l_t Y_j_t).
  Also plain synthetic control (no intercept, no time weights) and plain DiD (equal weights).
  Inference: placebo (each donor in turn treated, actual treated dropped); p = share of |tau_placebo| >= |tau|.
  Pre-fit RMSE and the weighted pre-trend gap over [A-36,A-13] vs [A-12,A-1] reported.
Output: _res_tax_sdid.csv, _res_tax_sdid_weights.csv
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
CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["iso3", "year", "month", "dep_seats"]).to_pandas()
am = am[am.iso3.isin(CODED) & (am.year <= 2019)]
cm = am.groupby(["iso3", "year", "month"], as_index=False).dep_seats.sum()
cm["t"] = cm.year * 12 + cm.month
cm["y"] = np.log(cm.dep_seats)


def simplex_min(A, b, ridge=0.0, intercept=True):
    """min_w ||w0 + A w - b||^2 + ridge ||w||^2, w >= 0, sum w = 1 (w0 free if intercept)"""
    n = A.shape[1]

    def f(x):
        w, w0 = x[:n], (x[n] if intercept else 0.0)
        r = w0 + A @ w - b
        return r @ r + ridge * (w @ w)

    x0 = np.r_[np.ones(n) / n, [0.0]] if intercept else np.ones(n) / n
    cons = [{"type": "eq", "fun": lambda x: x[:n].sum() - 1}]
    bnds = [(0, 1)] * n + ([(None, None)] if intercept else [])
    r = minimize(f, x0, method="SLSQP", bounds=bnds, constraints=cons, options={"maxiter": 500, "ftol": 1e-12})
    return r.x[:n], (r.x[n] if intercept else 0.0)


def sdid(Y, tr, pre_idx, post_idx):
    """Y: DataFrame units x time (de-seasonalised ln seats); returns dict with sdid, sc, did, weights, pre-trend gap"""
    don = [u for u in Y.index if u != tr]
    Yp, Yq = Y.loc[don, pre_idx].to_numpy(), Y.loc[don, post_idx].to_numpy()
    yt_p, yt_q = Y.loc[tr, pre_idx].to_numpy(), Y.loc[tr, post_idx].to_numpy()
    T0, T1 = len(pre_idx), len(post_idx)
    sigma = np.diff(Yp, axis=1).std()
    zeta = (1 * T1) ** 0.25 * sigma
    w, _ = simplex_min(Yp.T, yt_p, ridge=zeta ** 2 * T0, intercept=True)
    lam, _ = simplex_min(Yp, Yq.mean(axis=1), ridge=0.0, intercept=True)
    tau = (yt_q.mean() - yt_p @ lam) - (w @ (Yq.mean(axis=1) - Yp @ lam))
    wsc, _ = simplex_min(Yp.T, yt_p, ridge=0.0, intercept=False)
    sc = (yt_q.mean() - yt_p.mean()) - (wsc @ Yq.mean(axis=1) - wsc @ Yp.mean(axis=1))
    did = (yt_q.mean() - yt_p.mean()) - (Yq.mean() - Yp.mean())
    gap = Y.loc[tr, pre_idx].to_numpy() - w @ Yp
    early, late = gap[: max(T0 - 12, 1)].mean(), gap[-12:].mean()
    return dict(sdid=tau, sc=sc, did=did, rmse_pre=np.sqrt((gap ** 2).mean()), pretrend_gap=late - early,
                weights=pd.Series(w, index=don), lam=lam)


rows, wrows = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    don = sorted((CODED - {"ITA", ev.iso3}) - busy)
    d = cm[cm.iso3.isin(don + [ev.iso3]) & (cm.t >= lo) & (cm.t <= hi)].copy()
    full = d.groupby("iso3").t.nunique()
    keep = full[full == full.max()].index
    d = d[d.iso3.isin(keep)]
    if ev.iso3 not in keep:
        print(ev.iso3, "treated series incomplete; skipped")
        continue
    pre_m = d[d.t < ev.tA]
    seas = pre_m.groupby(["iso3", "month"]).y.mean().rename("s")
    d = d.merge(seas, left_on=["iso3", "month"], right_index=True, how="left")
    d["yd"] = d.y - d.s
    Y = d.pivot(index="iso3", columns="t", values="yd")
    pre_idx = [t for t in Y.columns if t < ev.tA]
    post_idx = [t for t in Y.columns if t >= ev.tE]
    Y = Y.dropna(subset=pre_idx + post_idx)
    res = sdid(Y, ev.iso3, pre_idx, post_idx)
    plac = []
    for u in [x for x in Y.index if x != ev.iso3]:
        Yu = Y.drop(index=ev.iso3)
        plac.append(sdid(Yu, u, pre_idx, post_idx)["sdid"])
    plac = np.array(plac)
    p = (np.abs(plac) >= abs(res["sdid"])).mean()
    rows.append(dict(event=f"{ev.iso3} {ev.eff}", donors=len(Y) - 1, sdid=res["sdid"], p_placebo=p, placebo_sd=plac.std(),
                     sc=res["sc"], did=res["did"], rmse_pre=res["rmse_pre"], pretrend_gap=res["pretrend_gap"],
                     top_donors=", ".join(f"{i} {v:.2f}" for i, v in res["weights"].sort_values(ascending=False).head(4).items())))
    for i, v in res["weights"].items():
        wrows.append(dict(event=f"{ev.iso3} {ev.eff}", donor=i, weight=v))
    print(ev.iso3, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_tax_sdid.csv", index=False)
pd.DataFrame(wrows).to_csv("_res_tax_sdid_weights.csv", index=False)
pd.set_option("display.width", 230)
print(R.round(4).to_string(index=False))
clean = R[R.event.str[:3].isin(["NLD", "DEU", "SWE", "NOR", "AUT", "IRL", "DNK", "GBR"])]
print("\nmean SDID (8 events ex MLT): %.4f ; weighted by donors n/a" % clean.sdid.mean())
