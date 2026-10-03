# -*- coding: utf-8 -*-
"""Country-level version of the stacked event study in 60_fx_stacked_event.py (user request 2026-10-02).
Identical events, control rule, window, bins, reference period and clustering; the only change is the unit:
seats summed to country x month (country_month.csv from 70_country_level.py, all airports of the country,
Sep-2008 interpolated), so every country counts once.
  ln y_cst = a_{c x calendar month x s} + d_{t x s} + sum_k b_k 1[e in k] treated_cs + u_cst
Output: _res_fx_event_country.csv (pooled bins, with the airport-level estimates from _res_fx_event.csv alongside),
_res_fx_event_country_byevent.csv (point estimates only: one treated country per event)
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
TH, W, MIN_FX = 0.20, 24, 45

# ---- hit months (same as 60) ----
L = pd.read_csv("local_fx_monthly.csv", usecols=["iso3", "ym", "lnq", "lnP_loc"])
L["t"] = (L.ym.str[:4].astype(int) - 1996) * 12 + L.ym.str[5:7].astype(int) - 1
lag = L[["iso3", "t", "lnq", "lnP_loc"]].copy()
lag["t"] += 12
L = L.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
L["d12q"] = L.lnq - L.lnq_m12
L["hit"] = (L.d12q >= TH) & ((L.lnP_loc - L.lnP_loc_m12) >= TH)

E = pd.read_csv("fx_episodes.csv")
EV = E[E.used & (E.panel_airports > 0)].sort_values("t0").reset_index(drop=True)     # the same 14 events as 60

# ---- country x month seats ----
P = pd.read_csv("country_month.csv", usecols=["iso3", "year", "month", "ln_total", "ln_domestic", "ln_international"])
P["t"] = (P.year - 1996) * 12 + P.month - 1

stacks, info = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.t0 - W, ev.t0 + W
    inwin = L[(L.t >= lo) & (L.t <= hi)]
    cov = inwin.dropna(subset=["d12q"]).groupby("iso3").size()
    anyhit = inwin.groupby("iso3").hit.any()
    ctrl = set(cov[cov >= MIN_FX].index) - set(anyhit[anyhit].index) - {ev.iso3}
    d = P[(P.t >= lo) & (P.t <= hi) & P.iso3.isin(ctrl | {ev.iso3})].copy()
    d["stk"] = k
    d["treated"] = (d.iso3 == ev.iso3).astype(np.int8)
    d["e"] = d.t - ev.t0
    stacks.append(d)
    info.append(dict(event=f"{ev.iso3} {ev.onset}", control_countries=d[d.treated == 0].iso3.nunique()))
S = pd.concat(stacks, ignore_index=True)
print(pd.DataFrame(info).to_string(index=False))

BINS = [(-24, -19, "pre_24_19"), (-18, -13, "pre_18_13"), (0, 5, "post_0_5"), (6, 11, "post_6_11"),
        (12, 17, "post_12_17"), (18, 24, "post_18_24")]
for a, b, nm in BINS:
    S[nm] = ((S.e >= a) & (S.e <= b) & (S.treated == 1)).astype(np.int8)
S["fe_cm"] = S.iso3 + "_" + S.month.astype(str) + "_" + S.stk.astype(str)
S["fe_t"] = S.t.astype(str) + "_" + S.stk.astype(str)
RHS = " + ".join(nm for *_, nm in BINS)
OUTS = {"ln_domestic": "domestic seats", "ln_total": "total seats", "ln_international": "international seats"}

air = pd.read_csv("_res_fx_event.csv")
res = []
for y, lab in OUTS.items():
    d = S.dropna(subset=[y])
    m = pf.feols(f"{y} ~ {RHS} | fe_cm + fe_t", data=d, vcov={"CRV1": "iso3"})
    td = m.tidy()
    tr = d[d.treated == 1]
    for a, b, nm in BINS:
        ar = air[(air.outcome == lab) & (air.bin == f"[{a},{b}]")]
        res.append(dict(outcome=lab, bin=f"[{a},{b}]", b=td.loc[nm, "Estimate"], se=td.loc[nm, "Std. Error"],
                        p=td.loc[nm, "Pr(>|t|)"], n=int(m._N), treated_events=tr.stk.nunique(),
                        treated_countries=tr.iso3.nunique(), clusters=d.iso3.nunique(),
                        airport_level_b=ar.b.iloc[0] if len(ar) else np.nan, airport_level_p=ar.p.iloc[0] if len(ar) else np.nan))
R = pd.DataFrame(res)
R.to_csv("_res_fx_event_country.csv", index=False)
pd.set_option("display.width", 220)
print("\nPooled stacked event study, country x month (reference = 12 months before onset; log points):")
print(R.round(4).to_string(index=False), flush=True)

# ---- by event (point estimates; one treated country, so no usable SE) ----
by = []
for k, ev in EV.iterrows():
    for y in ["ln_domestic", "ln_total"]:
        d = S[(S.stk == k)].dropna(subset=[y]).copy()
        if d[d.treated == 1].empty:
            continue
        d["pre"] = ((d.e <= -13) & (d.treated == 1)).astype(np.int8)
        d["post1"] = ((d.e >= 0) & (d.e <= 11) & (d.treated == 1)).astype(np.int8)
        d["post2"] = ((d.e >= 12) & (d.treated == 1)).astype(np.int8)
        m = pf.feols(f"{y} ~ pre + post1 + post2 | fe_cm + fe_t", data=d, vcov="iid")
        td = m.tidy().reindex(["pre", "post1", "post2"])
        by.append(dict(event=f"{ev.iso3} {ev.onset}", outcome=OUTS[y], local_fuel_peak=round(ev.peak_local_fuel, 2),
                       pre=td.loc["pre", "Estimate"], post_0_11=td.loc["post1", "Estimate"],
                       post_12_24=td.loc["post2", "Estimate"]))
B = pd.DataFrame(by)
B.to_csv("_res_fx_event_country_byevent.csv", index=False)
print("\nBy event (point estimates, one treated country each):")
print(B.round(3).to_string(index=False))
