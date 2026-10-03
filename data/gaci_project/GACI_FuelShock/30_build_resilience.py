# -*- coding: utf-8 -*-
"""Airport resilience index following Zhang, Cheung & Zhang (2027, TR-E 217, 105192), built from
the annual airport GACI panel (../GACI1996_2024_new_panel_data.csv, 101,049 airport-years).

Components per airport i and crisis c (start s, end e; Table 3 of the paper):
  pre      = GACI_(i, s-1)
  Depth_ic = 1 - max(0, (pre - min_{t in [s,e]} GACI_it) / pre)      (missing if decline < 1%)
  Speed_ic = sum_{t=e+1}^{min(e+6, END)} w_t min(GACI_it/pre, 1) / sum w_t,  w_t = exp(-(t-(e+1))/2)
  U_ic     = max(0, (GACI_(i,e+k) - pre) / pre), k = 5 (k = 3 when e+5 is beyond the data end)
  Adaptability_i = 0.5 SlopeNorm_i + 0.5 PostNorm_i
     SlopeNorm = cross-airport percentile of the Theil-Sen slope of the airport's yearly GACI rank percentile
     PostNorm  = min-max scaling of mean_c U_ic to [0,1] (the paper: "scaling to the [0,1] interval"; min-max
                 reproduces its Table 5 level better than a percentile, _res_replicate_check.py)
  R_i = (Depth_i + Speed_i + Adaptability_i) / 3, component means over the crises where each is defined
  EB shrinkage: n_i = crises with pre observed, decline >= 1%, Depth and Speed defined;
     n_i = 0 -> NA; n_i in {1,2} -> n/(n+2) R + 2/(n+2) 0.5; n_i >= 3 -> R.

Versions (the data end truncates every window, so a version never uses years after END):
  full     : 8 crises, END 2024            (replication of the paper)
  pre2004  : AFC, 9/11, SARS, END 2003     (predetermined for a 2004-2019 fuel test)
  pre2008  : AFC, 9/11, SARS, END 2007     (predetermined for a 2008-2019 fuel test)
  pre2020  : 6 pre-Covid crises, END 2019  (predetermined for the 2022 spike)
  rt{Y}    : real-time, END = Y-1, crises that started by Y-1, Y = 2004..2019
Output: resilience_airport.csv (wide: one row per airport, columns per version),
        resilience_realtime.csv (airport x year), resilience_crisis_full.csv (airport x crisis components)
"""
import numpy as np
import pandas as pd
from scipy.stats import theilslopes

g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")[["Year", "Airport", "GACI"]]
g = g.rename(columns={"Year": "y", "Airport": "a"})
W = g.pivot_table(index="a", columns="y", values="GACI")          # airports x years, NaN when absent
YEARS = np.array(W.columns)
RANK = g.assign(rho=g.groupby("y").GACI.rank(pct=True)).pivot_table(index="a", columns="y", values="rho")

CRISES = [("AFC", 1997, 1998), ("9/11", 2001, 2002), ("SARS", 2003, 2003), ("GFC+H1N1", 2008, 2009),
          ("Ash+Tohoku", 2010, 2011), ("Ebola+MERS", 2014, 2015), ("COVID", 2020, 2021), ("RU airspace", 2022, 2024)]
H, TAU = 6, 2.0

def col(y):
    return W[y] if y in W.columns else pd.Series(np.nan, index=W.index)

def theil(row_y, row_v):
    m = ~np.isnan(row_v)
    x, v = row_y[m], row_v[m]
    if len(x) >= 3:
        return theilslopes(v, x)[0]
    if len(x) == 2:
        return (v[1] - v[0]) / (x[1] - x[0])
    return np.nan

def build(crises, END, keep_crisis=False):
    rows = {}
    D, S, U = {}, {}, {}
    for name, s, e in crises:
        if s - 1 > END:
            continue
        pre = col(s - 1)
        e_ = min(e, END)
        mn = W[[y for y in range(s, e_ + 1) if y in W.columns]].min(axis=1, skipna=True)
        dec = (pre - mn) / pre
        binding = pre.notna() & mn.notna() & (dec >= 0.01)
        depth = (1 - dec.clip(lower=0)).where(binding)
        post = [y for y in range(e + 1, min(e + H, END) + 1) if y in W.columns] if e <= END else []
        if post:
            wts = np.exp(-(np.array(post) - (e + 1)) / TAU)
            rec = W[post].div(pre, axis=0).clip(upper=1)
            num = (rec.fillna(0) * wts).sum(axis=1)
            den = (rec.notna() * wts).sum(axis=1)
            speed = (num / den).where((den > 0) & binding)
        else:
            speed = pd.Series(np.nan, index=W.index)
        k = 5 if e + 5 <= END else (3 if e + 3 <= END else None)
        up = ((col(e + k) - pre) / pre).clip(lower=0).where(pre.notna()) if k else pd.Series(np.nan, index=W.index)
        D[name], S[name], U[name] = depth, speed, up
    D, S, U = pd.DataFrame(D), pd.DataFrame(S), pd.DataFrame(U)
    valid = (D.notna() & S.notna()).sum(axis=1)
    yrs = YEARS[YEARS <= END]
    slope = pd.Series([theil(yrs.astype(float), RANK.loc[a, yrs].to_numpy(float)) for a in RANK.index], index=RANK.index)
    slope_n = slope.rank(pct=True)
    ub = U.mean(axis=1)
    post_n = (ub - ub.min()) / (ub.max() - ub.min())       # min-max; reproduces the paper's level best (see _res_replicate_check.py)
    adapt = (0.5 * slope_n + 0.5 * post_n).fillna(slope_n)
    depth_i, speed_i = D.mean(axis=1), S.mean(axis=1)
    R = (depth_i + speed_i + adapt) / 3
    Rs = R.where(valid >= 3, valid / (valid + 2) * R + 2 / (valid + 2) * 0.5).where(valid > 0)
    out = pd.DataFrame({"R": Rs, "R_raw": R.where(valid > 0), "depth": depth_i, "speed": speed_i, "adapt": adapt,
                        "n_valid": valid, "n_years": W[yrs].notna().sum(axis=1)})
    if keep_crisis:
        return out, D, S, U
    return out

VERS = {"full": (CRISES, 2024), "pre2004": (CRISES[:3], 2003), "pre2008": (CRISES[:3], 2007),
        "pre2020": (CRISES[:6], 2019)}
wide = []
for v, (cr, END) in VERS.items():
    if v == "full":
        o, D, S, U = build(cr, END, keep_crisis=True)
        cc = pd.concat({"depth": D, "speed": S, "upgrade": U}, axis=1)
        cc.columns = [f"{a}_{b}" for a, b in cc.columns]
        cc.to_csv("resilience_crisis_full.csv")
    else:
        o = build(cr, END)
    wide.append(o.add_suffix("_" + v))
    print(v, "airports with R:", o.R.notna().sum(), " mean %.3f sd %.3f" % (o.R.mean(), o.R.std()))
wide = pd.concat(wide, axis=1)
wide.index.name = "airport_iata"
wide.to_csv("resilience_airport.csv")

rt = []
for Y in range(2004, 2020):
    cr = [c for c in CRISES if c[1] <= Y - 1]
    o = build(cr, Y - 1)[["R", "depth", "speed", "adapt", "n_valid"]]
    o["year"] = Y
    rt.append(o.reset_index().rename(columns={"a": "airport_iata"}))
pd.concat(rt).to_csv("resilience_realtime.csv", index=False)
print("real-time versions 2004-2019 written")
