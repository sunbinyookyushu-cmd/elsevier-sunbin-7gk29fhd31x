# -*- coding: utf-8 -*-
"""Geopolitical shocks: stacked DiD (user 2026-10-02: "staggered DiD 가능? ... 시트? 노선? 둘다 돌려봐").

Shock data: Caldara & Iacoviello (2022, AER) country-specific geopolitical risk index GPRC (44 countries, monthly),
data_external/data_gpr_export.xls (downloaded 2026-10-02 from matteoiacoviello.com).
Event: z = (ln GPRC - own 1990-2019 mean) / own SD; onset = first month with z > 2.5 and no z > 2.5 month in the
previous 24 months; dropped if the world GPR spikes the same month (world z > 2: global events such as 9/11, Iraq 2003);
onsets 2000-01..2017-12.
Stack s (one per event): airports of the treated country + airports of GPR countries with no z > 2.5 month in
[onset-24, onset+24]. Moderators measured the calendar year before onset: GACI (ln) and size (ln seats), z-scored.

(A) seats, monthly, window -24..+24 months, ln seats (months with seats > 0):
  (1) ln S_ist = b (Treat x Post) + a_{i x cal.month x s} + d_{t x s} + e
  (2) ... + g (Treat x Post x GACI) + th (Treat x Post x Size) + l (Post x GACI) + k (Post x Size)
  (3) event study by treated-airport GACI half (median within the treated country), bins as in 60/62.
(B) routes, annual, ln Degree (GACI panel), years -2..+2 around the effective onset year (onset year if the onset month
  is Jan-Jun, else the next year); FE airport x stack and year x stack; same (1)-(3) with years -2, 0, 1, 2 (ref -1).
SE clustered by country.
Output: gpr_events.csv, _res_gpr_did.csv, _res_gpr_es.csv
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

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
TH, W = 2.5, 24

# ---------------- events ----------------
g = pd.read_excel("data_external/data_gpr_export.xls")
g["ym"] = pd.to_datetime(g.month).dt.to_period("M")
g = g[(g.ym >= pd.Period("1990-01", "M")) & (g.ym <= pd.Period("2019-12", "M"))].copy()
cols = [c for c in g.columns if str(c).startswith("GPRC_")]
L = g.melt(id_vars=["ym", "GPR"], value_vars=cols, var_name="c", value_name="v")
L["iso3"] = L.c.str[5:]
L = L.dropna(subset=["v"]).sort_values(["iso3", "ym"]).reset_index(drop=True)
L["lv"] = np.log(L.v.where(L.v > 0))
L["z"] = L.groupby("iso3").lv.transform(lambda s: (s - s.mean()) / s.std())
L["t"] = L.ym.dt.year * 12 + L.ym.dt.month
wl = np.log(g.set_index("ym").GPR)
wz = (wl - wl.mean()) / wl.std()
ev = []
for c, x in L.groupby("iso3"):
    x = x.reset_index(drop=True)
    last = -10 ** 6
    for i in np.where(x.z > TH)[0]:
        if x.t[i] - last > W:
            ev.append(dict(iso3=c, onset=str(x.ym[i]), t0=int(x.t[i]), z=x.z[i], world_z=wz.get(x.ym[i], np.nan)))
        last = x.t[i]
E = pd.DataFrame(ev)
E = E[(E.onset >= "2000-01") & (E.onset <= "2017-12") & ~(E.world_z > 2)].sort_values("t0").reset_index(drop=True)
E["year0"] = E.t0 // 12 - (E.t0 % 12 == 0)
E["month0"] = (E.t0 - 1) % 12 + 1
E["year0"] = (E.t0 - 1) // 12
E["y_eff"] = np.where(E.month0 <= 6, E.year0, E.year0 + 1)
E.to_csv("gpr_events.csv", index=False)
print(f"events used: {len(E)} in {E.iso3.nunique()} countries", flush=True)
GPRC = set(L.iso3)
hitm = L[L.z > TH][["iso3", "t"]]

# ---------------- data ----------------
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats"]).to_pandas()
am = am[am.iso3.isin(GPRC) & (am.dep_seats > 0)]
am["t"] = am.year * 12 + am.month
am["ln_seats"] = np.log(am.dep_seats)
ann_seats = am.groupby(["airport_iata", "year"]).dep_seats.sum()
gp = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv", usecols=["Year", "Airport", "Degree", "GACI"]).rename(
    columns={"Airport": "airport_iata", "Year": "year"})
gaci = gp.set_index(["airport_iata", "year"]).GACI
a2c = am.drop_duplicates("airport_iata").set_index("airport_iata").iso3
gp["iso3"] = gp.airport_iata.map(a2c)
gp = gp[gp.iso3.isin(GPRC) & (gp.Degree > 0)]
gp["ln_deg"] = np.log(gp.Degree)


def controls(ev):
    lo, hi = ev.t0 - W, ev.t0 + W
    bad = set(hitm[(hitm.t >= lo) & (hitm.t <= hi)].iso3)
    return (GPRC - bad) - {ev.iso3}


def moderators(d, ev):
    yb = ev.year0 - 1
    keys = list(zip(d.airport_iata, [yb] * len(d)))
    d["G"] = np.log(pd.Series(gaci.reindex(keys).to_numpy(), index=d.index).where(lambda s: s > 0))
    d["Sz"] = np.log(pd.Series(ann_seats.reindex(keys).to_numpy(), index=d.index).where(lambda s: s > 0))
    return d


ms, ys = [], []
for k, ev in E.iterrows():
    ctrl = controls(ev)
    d = am[am.iso3.isin(ctrl | {ev.iso3}) & (am.t >= ev.t0 - W) & (am.t <= ev.t0 + W)].copy()
    d["stk"], d["treat"], d["e"] = k, (d.iso3 == ev.iso3).astype(np.int8), d.t - ev.t0
    ms.append(moderators(d, ev))
    y = gp[gp.iso3.isin(ctrl | {ev.iso3}) & (gp.year >= ev.y_eff - 2) & (gp.year <= ev.y_eff + 2)].copy()
    y["stk"], y["treat"], y["e"] = k, (y.iso3 == ev.iso3).astype(np.int8), y.year - ev.y_eff
    ys.append(moderators(y, ev))
M = pd.concat(ms, ignore_index=True)
Y = pd.concat(ys, ignore_index=True)
print("monthly rows", len(M), "annual rows", len(Y), flush=True)

res, es = [], []
for lab, D, yv, tvar, fe_unit in [("seats (monthly)", M, "ln_seats", "t", "cm"), ("routes (annual)", Y, "ln_deg", "year", "u")]:
    D = D.copy()
    D["post"] = (D.e >= 0).astype(np.int8)
    D["tp"] = D.treat * D.post
    for v in ["G", "Sz"]:
        u = D.drop_duplicates(["airport_iata", "stk"])[v]
        D[v] = (D[v] - u.mean()) / u.std()
    D["tpG"], D["tpS"], D["pG"], D["pS"] = D.tp * D.G, D.tp * D.Sz, D.post * D.G, D.post * D.Sz
    if fe_unit == "cm":
        D["fe_u"] = D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str)
    else:
        D["fe_u"] = D.airport_iata + "_" + D.stk.astype(str)
    D["fe_t"] = D[tvar].astype(str) + "_" + D.stk.astype(str)
    Dm = D.dropna(subset=["G", "Sz"])
    specs = [("(1) average", D, "tp"), ("(1') average, moderator sample", Dm, "tp"),
             ("(2) x GACI and size", Dm, "tp + tpG + tpS + pG + pS")]
    for sl, dd, rhs in specs:
        m = pf.feols(f"{yv} ~ {rhs} | fe_u + fe_t", data=dd, vcov={"CRV1": "iso3"})
        td = m.tidy()
        for term in td.index:
            res.append(dict(outcome=lab, spec=sl, term=term, b=td.loc[term, "Estimate"], se=td.loc[term, "Std. Error"],
                            p=td.loc[term, "Pr(>|t|)"], n=int(m._N), treated_countries=dd[dd.treat == 1].iso3.nunique(),
                            events=dd[dd.treat == 1].stk.nunique(), clusters=dd.iso3.nunique()))
    # event study by GACI half (median among treated airports of the stack)
    med = Dm[Dm.treat == 1].drop_duplicates(["airport_iata", "stk"]).groupby("stk").G.median()
    Dm = Dm.copy()
    Dm["hi"] = (Dm.G > Dm.stk.map(med)).astype(np.int8)
    bins = [(-24, -19), (-18, -13), (0, 5), (6, 11), (12, 17), (18, 24)] if fe_unit == "cm" else [(-2, -2), (0, 0), (1, 1), (2, 2)]
    names = []
    for a, b in bins:
        for grp, gv in [("hi", 1), ("lo", 0)]:
            nm = f"{grp}_{a}_{b}".replace("-", "m")
            Dm[nm] = ((Dm.e >= a) & (Dm.e <= b) & (Dm.treat == 1) & (Dm.hi == gv)).astype(np.int8)
            names.append((nm, grp, f"[{a},{b}]"))
    m = pf.feols(f"{yv} ~ {' + '.join(n for n, _, _ in names)} | fe_u + fe_t", data=Dm, vcov={"CRV1": "iso3"})
    td = m.tidy()
    for nm, grp, bl in names:
        es.append(dict(outcome=lab, group="high GACI" if grp == "hi" else "low GACI", bin=bl, b=td.loc[nm, "Estimate"],
                       se=td.loc[nm, "Std. Error"], p=td.loc[nm, "Pr(>|t|)"]))
    print(lab, "done", flush=True)

R = pd.DataFrame(res)
R.to_csv("_res_gpr_did.csv", index=False)
S = pd.DataFrame(es)
S.to_csv("_res_gpr_es.csv", index=False)
pd.set_option("display.width", 220)
print(E[["iso3", "onset", "z", "world_z"]].round(2).to_string(index=False))
print(R.round(4).to_string(index=False))
print(S.round(4).to_string(index=False))
