# -*- coding: utf-8 -*-
"""One-coefficient DiD on the exchange-rate fuel-cost episodes, country level (user 2026-10-02: no event-time bins).
Same stacks as 75 (14 events, control rule, country x month seats from country_month_margins.csv):
  ln y_cst = a_{c x calendar month x s} + d_{t x s} + b (treated_cs x post_st) + u,  post = months since onset >= 0
Windows: (a) -24..+24, (b) -24..+48 (months after 2019-12 dropped). SE clustered by country.
Output: _res_did_simple.csv
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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
Y = {"y4": "CO2 per seat-km", "y2": "gauge (seats per flight)", "y0": "CO2", "y5": "seats"}
cm = pd.read_csv("country_month_margins.csv", usecols=["iso3", "year", "month"] + ["ln_" + k for k in Y])
L_ = pd.read_csv("local_fx_monthly.csv", usecols=["iso3", "ym", "lnq", "lnP_loc"])
L_["t"] = (L_.ym.str[:4].astype(int) - 1996) * 12 + L_.ym.str[5:7].astype(int) - 1
lag = L_[["iso3", "t", "lnq", "lnP_loc"]].copy()
lag["t"] += 12
L_ = L_.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
L_["d12q"] = L_.lnq - L_.lnq_m12
L_["hit"] = (L_.d12q >= 0.20) & ((L_.lnP_loc - L_.lnP_loc_m12) >= 0.20)
E = pd.read_csv("fx_episodes.csv")
EV = E[E.used & (E.panel_airports > 0)].sort_values("t0").reset_index(drop=True)
P = cm.copy()
P["t"] = (P.year - 1996) * 12 + P.month - 1
T_END = (2019 - 1996) * 12 + 11

rows = []
for wl, (pre, post, minfx) in {"(a) -24..+24": (24, 24, 45), "(b) -24..+48": (24, 48, 67)}.items():
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
    S["tp"] = ((S.e >= 0) & (S.treated == 1)).astype(np.int8)
    S["fe_cm"] = S.iso3 + "_" + S.month.astype(str) + "_" + S.stk.astype(str)
    S["fe_t"] = S.t.astype(str) + "_" + S.stk.astype(str)
    for v, lab in Y.items():
        dd = S.dropna(subset=["ln_" + v])
        m = pf.feols(f"ln_{v} ~ tp | fe_cm + fe_t", data=dd, vcov={"CRV1": "iso3"})
        td = m.tidy()
        rows.append(dict(window=wl, outcome=lab, b=td.loc["tp", "Estimate"], se=td.loc["tp", "Std. Error"],
                         p=td.loc["tp", "Pr(>|t|)"], n=int(m._N), treated=dd[dd.treated == 1].iso3.nunique(),
                         clusters=dd.iso3.nunique()))
R = pd.DataFrame(rows)
R.to_csv("_res_did_simple.csv", index=False)
pd.set_option("display.width", 200)
print(R.round(4).to_string(index=False))
