# -*- coding: utf-8 -*-
"""Export the geopolitical-shock stacks of 79_gpr_stacked.py to Stata (user 2026-10-02: "스태타 do파일로 제공 가능?").
Same event rule, controls, windows and moderators as 79 (construction copied, regressions left to Stata).
Usage: python 79b_export_gpr_stata.py [threshold]  (default 2.5; e.g. 3.0 writes files with suffix _z30)
Output folder stata_gpr/: gpr_stack_seats{suffix}.dta (monthly), gpr_stack_routes{suffix}.dta (annual), gpr_events{suffix}.dta,
then run gpr_stacked.do in Stata.
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import os
import sys
import warnings

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

warnings.filterwarnings("ignore")
TH = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5
W = 24
SUF = "" if TH == 2.5 else f"_z{int(round(TH * 10))}"
OUT = "stata_gpr"
os.makedirs(OUT, exist_ok=True)

# ---------------- events (as in 79) ----------------
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
E["month0"] = (E.t0 - 1) % 12 + 1
E["year0"] = (E.t0 - 1) // 12
E["y_eff"] = np.where(E.month0 <= 6, E.year0, E.year0 + 1)
E["stk"] = E.index
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
    bad = set(hitm[(hitm.t >= ev.t0 - W) & (hitm.t <= ev.t0 + W)].iso3)
    return (GPRC - bad) - {ev.iso3}


def moderators(d, ev):
    keys = list(zip(d.airport_iata, [ev.year0 - 1] * len(d)))
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

iso_codes = {c: i + 1 for i, c in enumerate(sorted(GPRC))}


def finish(D, monthly):
    D = D.copy()
    D["post"] = (D.e >= 0).astype(np.int8)
    D["tp"] = (D.treat * D.post).astype(np.int8)
    for v in ["G", "Sz"]:
        u = D.drop_duplicates(["airport_iata", "stk"])[v]
        D[v] = (D[v] - u.mean()) / u.std()
    D["tpG"], D["tpS"], D["pG"], D["pS"] = D.tp * D.G, D.tp * D.Sz, D.post * D.G, D.post * D.Sz
    if monthly:
        D["fe_u"] = pd.factorize(D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str))[0] + 1
        D["fe_t"] = pd.factorize(D.t.astype(str) + "_" + D.stk.astype(str))[0] + 1
        bins = [(-24, -19), (-18, -13), (0, 5), (6, 11), (12, 17), (18, 24)]
    else:
        D["fe_u"] = pd.factorize(D.airport_iata + "_" + D.stk.astype(str))[0] + 1
        D["fe_t"] = pd.factorize(D.year.astype(str) + "_" + D.stk.astype(str))[0] + 1
        bins = [(-2, -2), (0, 0), (1, 1), (2, 2)]
    hasm = D.G.notna() & D.Sz.notna()
    med = D[hasm & (D.treat == 1)].drop_duplicates(["airport_iata", "stk"]).groupby("stk").G.median()
    D["hi"] = np.where(hasm, (D.G > D.stk.map(med)).astype(float), np.nan)
    for a, b in bins:
        for grp, gv in [("hi", 1), ("lo", 0)]:
            nm = f"{grp}_{a}_{b}".replace("-", "m")
            D[nm] = ((D.e >= a) & (D.e <= b) & (D.treat == 1) & (D.hi == gv)).astype(np.int8)
    D["iso3n"] = D.iso3.map(iso_codes).astype(np.int16)
    D["airport_n"] = (pd.factorize(D.airport_iata)[0] + 1).astype(np.int32)
    D = D.rename(columns={"airport_iata": "airport"})
    keep = ["airport", "airport_n", "iso3", "iso3n", "stk", "treat", "e", "post", "tp", "G", "Sz", "tpG", "tpS", "pG", "pS", "hi", "fe_u", "fe_t"]
    keep += [c for c in D.columns if c.startswith(("hi_", "lo_"))]
    keep += (["t", "year", "month", "ln_seats"] if monthly else ["year", "ln_deg"])
    D = D[keep]
    for c in ["G", "Sz", "tpG", "tpS", "pG", "pS", "hi"] + (["ln_seats"] if monthly else ["ln_deg"]):
        D[c] = D[c].astype(np.float32)
    D["e"] = D.e.astype(np.int16)
    D["stk"] = D.stk.astype(np.int16)
    return D


M = finish(pd.concat(ms, ignore_index=True), True)
Y = finish(pd.concat(ys, ignore_index=True), False)
M.to_stata(os.path.join(OUT, f"gpr_stack_seats{SUF}.dta"), write_index=False, version=118)
Y.to_stata(os.path.join(OUT, f"gpr_stack_routes{SUF}.dta"), write_index=False, version=118)
E[["stk", "iso3", "onset", "t0", "year0", "month0", "y_eff", "z", "world_z"]].to_stata(
    os.path.join(OUT, f"gpr_events{SUF}.dta"), write_index=False, version=118)
print("seats rows", len(M), "routes rows", len(Y), "events", len(E))
print("treated airports (seats):", M[M.treat == 1].airport.nunique(), " control airports:", M[M.treat == 0].airport.nunique())
