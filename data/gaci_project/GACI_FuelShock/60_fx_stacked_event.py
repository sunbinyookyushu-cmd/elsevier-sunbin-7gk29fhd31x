# -*- coding: utf-8 -*-
"""Country-specific ('regional') fuel cost shocks from the exchange rate: stacked event study.
User decision 2026-10-02: staggered DiD on regional oil shocks; first check whether seats respond at all.

Episodes (local_fx_monthly.csv from 41_local_currency.py):
  hit_ct = D12 ln real exchange rate >= 0.20 and D12 ln real local-currency jet price >= 0.20 (log points; D12 is
           taken against the same calendar month a year earlier, so gaps in the FX series do not shift it)
  onset  = first month of a run of hit months; a new episode needs >= 24 months since the previous run ended.
Events used (criteria agreed 2026-10-02): onset 2001-2019; world real jet price D12 within +-0.10 at onset;
GDP per capita did not fall in the onset or the next year (GACI_CO2 panel; missing = not flagged); peak D12 ln q < 2
(drops exchange-rate unification jumps); NGA 2016 dropped (2016 recession, GDP missing in the panel).
Stack s (one per event): airports of the treated country + control airports in countries with FX data in >= 45 of
the 49 window months and no hit month in [onset-24, onset+24]. Event time e = t - onset, -24..+24.
  ln y_ist = a_{i x calendar month x s} + d_{t x s} + sum_k b_k 1[e in k] treated_is + u_ist
  bins k: [-24,-19] [-18,-13] | reference [-12,-1] | [0,5] [6,11] [12,17] [18,24]
  The 12-month reference window lets the airport x calendar-month FE absorb each airport's seasonality.
SE clustered by country; treated countries are few, so p-values are read with care. By-event estimates have one
treated country each and are reported with airport-clustered SE for reference only.
Sample: estimation panel of _prep_airport.panel() (1996 GACI and seats > 0; Sep-2008 interpolated).
Outcomes: ln domestic seats (main), ln total seats, ln international seats.
Output: fx_episodes.csv (all episodes with flags), _res_fx_event.csv (pooled bins), _res_fx_event_byevent.csv
"""
import io
import sys

import numpy as np
import pandas as pd
import pyfixest as pf
from _prep_airport import panel

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
TH, W, MIN_FX = 0.20, 24, 45

# ---- episodes ----
L = pd.read_csv("local_fx_monthly.csv", usecols=["iso3", "ym", "lnq", "lnP_loc", "lnjet"])
L["t"] = (L.ym.str[:4].astype(int) - 1996) * 12 + L.ym.str[5:7].astype(int) - 1
lag = L[["iso3", "t", "lnq", "lnP_loc", "lnjet"]].copy()
lag["t"] += 12
L = L.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
L["d12q"] = L.lnq - L.lnq_m12
L["d12P"] = L.lnP_loc - L.lnP_loc_m12
L["d12w"] = L.lnjet - L.lnjet_m12
L["hit"] = (L.d12q >= TH) & (L.d12P >= TH)
L = L.sort_values(["iso3", "t"]).reset_index(drop=True)


def ym(t):
    return f"{1996 + t // 12}-{t % 12 + 1:02d}"


rows = []
for c, g in L[L.hit].groupby("iso3"):
    ts = g.t.to_numpy()
    starts = [0] + [k for k in range(1, len(ts)) if ts[k] != ts[k - 1] + 1]
    ends = starts[1:] + [len(ts)]
    last_end = -10 ** 6
    for s0, e0 in zip(starts, ends):
        t_on, t_off = int(ts[s0]), int(ts[e0 - 1])
        if t_on - last_end >= W:
            seg = g.iloc[s0:e0]
            rows.append(dict(iso3=c, t0=t_on, onset=ym(t_on), months=t_off - t_on + 1, peak_dep=seg.d12q.max(),
                             peak_local_fuel=seg.d12P.max(), world_at_onset=seg.d12w.iloc[0]))
        last_end = t_off
E = pd.DataFrame(rows)
E["onset_year"] = E.onset.str[:4].astype(int)
cp = pd.read_csv(r"..\GACI_CO2\gaci_co2_panel.csv", usecols=["c", "y", "lnpc"]).sort_values(["c", "y"])
cp["g"] = cp.groupby("c").lnpc.diff()
gro = cp.set_index(["c", "y"]).g
E["gdp_g_onset"] = [gro.get((c, y), np.nan) for c, y in zip(E.iso3, E.onset_year)]
E["gdp_g_next"] = [gro.get((c, y + 1), np.nan) for c, y in zip(E.iso3, E.onset_year)]
E["recession"] = (E.gdp_g_onset < 0) | (E.gdp_g_next < 0)
E["used"] = ((E.onset_year >= 2001) & (E.onset_year <= 2019) & (E.world_at_onset.abs() <= 0.10) & ~E.recession
             & (E.peak_dep < 2) & ~((E.iso3 == "NGA") & (E.onset_year == 2016)))

P = panel()[["airport_iata", "iso3", "t", "month", "ln_seats", "ln_seats_dom", "ln_seats_intl"]]
nair = P.groupby("iso3").airport_iata.nunique()
E["panel_airports"] = E.iso3.map(nair).fillna(0).astype(int)
E.to_csv("fx_episodes.csv", index=False)
EV = E[E.used & (E.panel_airports > 0)].sort_values("t0").reset_index(drop=True)
print(f"episodes {len(E)} in {E.iso3.nunique()} countries; events used {len(EV)} "
      f"({int(E.used.sum())} pass the criteria, {int((E.used & (E.panel_airports == 0)).sum())} without panel airports)")

# ---- stacks ----
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
    info.append(dict(event=f"{ev.iso3} {ev.onset}", treated_airports=d[d.treated == 1].airport_iata.nunique(),
                     control_countries=len(ctrl), control_airports=d[d.treated == 0].airport_iata.nunique()))
S = pd.concat(stacks, ignore_index=True)
info = pd.DataFrame(info)
pd.set_option("display.width", 220)
tab = EV[["iso3", "onset", "months", "peak_dep", "peak_local_fuel", "world_at_onset", "gdp_g_onset", "gdp_g_next"]].round(3)
print(pd.concat([tab, info.drop(columns="event")], axis=1).to_string(index=False))

BINS = [(-24, -19, "pre_24_19"), (-18, -13, "pre_18_13"), (0, 5, "post_0_5"), (6, 11, "post_6_11"),
        (12, 17, "post_12_17"), (18, 24, "post_18_24")]
for a, b, nm in BINS:
    S[nm] = ((S.e >= a) & (S.e <= b) & (S.treated == 1)).astype(np.int8)
S["fe_am"] = S.airport_iata + "_" + S.month.astype(str) + "_" + S.stk.astype(str)
S["fe_t"] = S.t.astype(str) + "_" + S.stk.astype(str)
RHS = " + ".join(nm for *_, nm in BINS)
OUTS = {"ln_seats_dom": "domestic seats", "ln_seats": "total seats", "ln_seats_intl": "international seats"}

if "--skip-pooled" not in sys.argv:              # the pooled models take ~5 min each
    res = []
    for y, lab in OUTS.items():
        d = S.dropna(subset=[y])
        m = pf.feols(f"{y} ~ {RHS} | fe_am + fe_t", data=d, vcov={"CRV1": "iso3"})
        td = m.tidy()
        for a, b, nm in BINS:
            res.append(dict(outcome=lab, bin=f"[{a},{b}]", b=td.loc[nm, "Estimate"], se=td.loc[nm, "Std. Error"],
                            p=td.loc[nm, "Pr(>|t|)"], n=int(m._N), treated_airports=d[d.treated == 1].airport_iata.nunique(),
                            treated_countries=d[d.treated == 1].iso3.nunique(), clusters=d.iso3.nunique()))
    R = pd.DataFrame(res)
    R.to_csv("_res_fx_event.csv", index=False)
    print("\nPooled stacked event study (reference = 12 months before onset; log points):")
    print(R.round(4).to_string(index=False), flush=True)

# ---- by event ----
by = []
for k, ev in EV.iterrows():
    for y in ["ln_seats_dom", "ln_seats"]:
        d = S[(S.stk == k)].dropna(subset=[y]).copy()
        if d[d.treated == 1].airport_iata.nunique() == 0:
            continue
        d["pre"] = ((d.e <= -13) & (d.treated == 1)).astype(np.int8)
        d["post1"] = ((d.e >= 0) & (d.e <= 11) & (d.treated == 1)).astype(np.int8)
        d["post2"] = ((d.e >= 12) & (d.treated == 1)).astype(np.int8)
        m = pf.feols(f"{y} ~ pre + post1 + post2 | fe_am + fe_t", data=d, vcov={"CRV1": "airport_iata"})
        td = m.tidy().reindex(["pre", "post1", "post2"])      # 'pre' drops when treated airports start after e = -13
        by.append(dict(event=f"{ev.iso3} {ev.onset}", outcome=OUTS[y], treated_airports=d[d.treated == 1].airport_iata.nunique(),
                       local_fuel_peak=round(ev.peak_local_fuel, 2), pre=td.loc["pre", "Estimate"],
                       post_0_11=td.loc["post1", "Estimate"], se_airport=td.loc["post1", "Std. Error"],
                       post_12_24=td.loc["post2", "Estimate"]))
B = pd.DataFrame(by)
B.to_csv("_res_fx_event_byevent.csv", index=False)
print("\nBy event (one treated country each; airport-clustered SE for reference only):")
print(B.round(3).to_string(index=False))
