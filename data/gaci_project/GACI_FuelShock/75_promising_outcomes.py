# -*- coding: utf-8 -*-
"""Three candidate outcomes (user 2026-10-02): CO2 per seat-km, gauge (seats per flight), CO2. Country x month.

1. Continuous IV with longer lags (71/72 used lag 3 only):
   D12 ln Y_ct = a_c + b D12 ln P_(t-L) + e,  P = world real jet price, instrumented by the Kaenzig or BH supply
   shock 12-month sum lagged L; L = 3, 12, 24, 36. Country FE, SE country cluster + Newey-West 12, 1997-2019.
2. Stacked DiD on the exchange-rate fuel-cost episodes (62, country level), same 14 events and control rule.
   (a) window -24..+24, bins as 60/62.
   (b) window -24..+48 (effects in the LPs appear after 2-4 years); controls: FX data in >= 67 of 73 months and no
       hit month in the window; post bins [0,11] [12,23] [24,35] [36,48]; months after 2019-12 dropped (Covid), so
       late events contribute only early post bins.
   ln y_cst = a_{c x calendar month x s} + d_{t x s} + sum_k b_k 1[e in k] treated_cs + u; reference [-12,-1];
   SE clustered by country.
Data: country_month_margins.csv (72). Output: _res_promising_iv.csv, _res_promising_did.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import io
import sys

import numpy as np
import pandas as pd
import pyfixest as pf
from _est import fit

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
pd.set_option("display.width", 220)
Y = {"y4": "CO2 per seat-km", "y2": "gauge (seats per flight)", "y0": "CO2"}
cm = pd.read_csv("country_month_margins.csv", usecols=["iso3", "year", "month", "t"] + list(Y) + ["ln_" + k for k in Y])

# ---- 1. IV with lags ----
f = pd.read_csv("fuel_monthly.csv", usecols=["year", "month", "d12_lnjet", "kz_s12", "bh_neg_s12"])
f["t"] = f.year * 12 + f.month
f = f.set_index("t").sort_index()
LAGS = [3, 12, 24, 36]
for L in LAGS:
    cm[f"x{L}"] = cm.t.map(f.d12_lnjet.shift(L))
    cm[f"kz{L}"] = cm.t.map(f.kz_s12.shift(L))
    cm[f"bh{L}"] = cm.t.map(f.bh_neg_s12.shift(L))
d = cm[(cm.year >= 1997) & (cm.year <= 2019)]
rows = []
for v, lab in Y.items():
    for L in LAGS:
        x = f"x{L}"
        s = d.dropna(subset=[v, x, f"kz{L}", f"bh{L}"])
        rec = dict(outcome=lab, lag=L, n=len(s), countries=s.iso3.nunique())
        for zl in ["kz", "bh"]:
            o = fit(s, v, endog=[x], instr=[f"{zl}{L}"], fes=["iso3"], vc=("dk", "iso3", "t", 12))
            rec.update({f"{zl}_b": o["coef"][x], f"{zl}_se": o["se"][x], f"{zl}_p": o["p"][x], f"{zl}_F": o["fs"][x]["F"]})
        rows.append(rec)
IV = pd.DataFrame(rows)
IV.to_csv("_res_promising_iv.csv", index=False)
print("1. Continuous IV, D12 ln Y on D12 ln jet price lagged L:")
print(IV.round(4).to_string(index=False), flush=True)

# ---- 2. stacked DiD ----
L_ = pd.read_csv("local_fx_monthly.csv", usecols=["iso3", "ym", "lnq", "lnP_loc"])
L_["t"] = (L_.ym.str[:4].astype(int) - 1996) * 12 + L_.ym.str[5:7].astype(int) - 1
lag = L_[["iso3", "t", "lnq", "lnP_loc"]].copy()
lag["t"] += 12
L_ = L_.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
L_["d12q"] = L_.lnq - L_.lnq_m12
L_["hit"] = (L_.d12q >= 0.20) & ((L_.lnP_loc - L_.lnP_loc_m12) >= 0.20)
E = pd.read_csv("fx_episodes.csv")
EV = E[E.used & (E.panel_airports > 0)].sort_values("t0").reset_index(drop=True)
P = cm[["iso3", "year", "month"] + ["ln_" + k for k in Y]].copy()
P["t"] = (P.year - 1996) * 12 + P.month - 1
T_END = (2019 - 1996) * 12 + 11

WINDOWS = {
    "(a) -24..+24": (24, 24, 45, [(-24, -19), (-18, -13), (0, 5), (6, 11), (12, 17), (18, 24)]),
    "(b) -24..+48": (24, 48, 67, [(-24, -19), (-18, -13), (0, 11), (12, 23), (24, 35), (36, 48)]),
}
rows = []
for wl, (pre, post, minfx, bins) in WINDOWS.items():
    stacks = []
    for k, ev in EV.iterrows():
        lo, hi = ev.t0 - pre, ev.t0 + post
        inwin = L_[(L_.t >= lo) & (L_.t <= hi)]
        cov = inwin.dropna(subset=["d12q"]).groupby("iso3").size()
        anyhit = inwin.groupby("iso3").hit.any()
        ctrl = set(cov[cov >= minfx].index) - set(anyhit[anyhit].index) - {ev.iso3}
        dd = P[(P.t >= lo) & (P.t <= min(hi, T_END)) & P.iso3.isin(ctrl | {ev.iso3})].copy()
        dd["stk"], dd["treated"], dd["e"] = k, (dd.iso3 == ev.iso3).astype(np.int8), dd.t - ev.t0
        stacks.append(dd)
    S = pd.concat(stacks, ignore_index=True)
    names = []
    for a, b in bins:
        nm = f"b_{a}_{b}".replace("-", "m")
        S[nm] = ((S.e >= a) & (S.e <= b) & (S.treated == 1)).astype(np.int8)
        names.append((nm, f"[{a},{b}]"))
    S["fe_cm"] = S.iso3 + "_" + S.month.astype(str) + "_" + S.stk.astype(str)
    S["fe_t"] = S.t.astype(str) + "_" + S.stk.astype(str)
    rhs = " + ".join(n for n, _ in names)
    for v, lab in Y.items():
        dd = S.dropna(subset=["ln_" + v])
        m = pf.feols(f"ln_{v} ~ {rhs} | fe_cm + fe_t", data=dd, vcov={"CRV1": "iso3"})
        td = m.tidy()
        for nm, bl in names:
            rows.append(dict(window=wl, outcome=lab, bin=bl, b=td.loc[nm, "Estimate"], se=td.loc[nm, "Std. Error"],
                             p=td.loc[nm, "Pr(>|t|)"], n=int(m._N), treated=dd[dd.treated == 1].iso3.nunique(),
                             clusters=dd.iso3.nunique()))
    print(wl, "done", flush=True)
DID = pd.DataFrame(rows)
DID.to_csv("_res_promising_did.csv", index=False)
print("\n2. Stacked DiD, country x month (reference [-12,-1]):")
print(DID.round(4).to_string(index=False))
