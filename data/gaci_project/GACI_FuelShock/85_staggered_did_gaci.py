# -*- coding: utf-8 -*-
"""Staggered (stacked) DiD on airport connectivity (user 2026-10-02: "(나)로 해봐").
Country-specific shocks at different dates; does the shocked country's network shift toward its hubs?

Events
  FX: country-specific fuel-cost spikes from the exchange rate (fx_episodes.csv, the 14 events of 60/62/76;
      hit month = D12 real depreciation >= .20 and D12 local real jet price >= .20).
  GPR: country-specific geopolitical shocks (gpr_events.csv from 79, 30 events, own z > 2.5).
Annual stacks: effective event year E (onset Jan-Jun -> onset year, else next year), years E-3..E+3, outcome years
  <= 2019 (Covid). Controls: countries with no hit month within +-36 months of onset (FX: FX data in >= 66 of the 73
  window months; GPR: the 44 GPR countries). Hub_is = z-score of ln GACI in E-1 (pre-event); Size_is = z ln seats E-1.
Outcome ln GACI_iy (GACI1996_2024_new_panel_data.csv).
  (1) average:  ln GACI = a_(i x s) + d_(y x s) + b Treat x Post                       (country-level relative change)
  (2) hubs:     ln GACI = a_(i x s) + d_(country x y x s) + l Post x Hub + g Treat x Post x Hub
  (3) (2) + Post x Size + Treat x Post x Size
  (4) event study of (2): g_k for k = -3, -2, 0, 1, 2, 3 (ref -1)
  g > 0: within the shocked country, better-connected airports gain relative connectivity after the shock.
SE clustered by country.
Output: _res_staggered_gaci.csv
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
K = 3

# ---------- monthly hit tables (t = year*12 + month) ----------
L = pd.read_csv("local_fx_monthly.csv", usecols=["iso3", "ym", "lnq", "lnP_loc"])
L["t"] = L.ym.str[:4].astype(int) * 12 + L.ym.str[5:7].astype(int)
lag = L[["iso3", "t", "lnq", "lnP_loc"]].copy()
lag["t"] += 12
L = L.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
L["d12q"] = L.lnq - L.lnq_m12
L["hit"] = (L.d12q >= 0.20) & ((L.lnP_loc - L.lnP_loc_m12) >= 0.20)
fx_cov = L.dropna(subset=["d12q"])[["iso3", "t"]]
fx_hit = L[L.hit][["iso3", "t"]]

g = pd.read_excel("data_external/data_gpr_export.xls")
g["ym"] = pd.to_datetime(g.month).dt.to_period("M")
g = g[(g.ym >= pd.Period("1990-01", "M")) & (g.ym <= pd.Period("2019-12", "M"))].copy()
cols = [c for c in g.columns if str(c).startswith("GPRC_")]
G = g.melt(id_vars=["ym"], value_vars=cols, var_name="c", value_name="v")
G["iso3"] = G.c.str[5:]
G = G.dropna(subset=["v"])
G["lv"] = np.log(G.v.where(G.v > 0))
G["z"] = G.groupby("iso3").lv.transform(lambda s: (s - s.mean()) / s.std())
G["t"] = G.ym.dt.year * 12 + G.ym.dt.month
gpr_hit = G[G.z > 2.5][["iso3", "t"]]
GPRC = set(G.iso3)

# ---------- events ----------
fx = pd.read_csv("fx_episodes.csv")
fx = fx[fx.used & (fx.panel_airports > 0)].copy()
fx["t0"] = fx.onset.str[:4].astype(int) * 12 + fx.onset.str[5:7].astype(int)
ge = pd.read_csv("gpr_events.csv")
EV = {"FX fuel-cost spikes": fx[["iso3", "onset", "t0"]].reset_index(drop=True),
      "geopolitical shocks": ge[["iso3", "onset", "t0"]].reset_index(drop=True)}

# ---------- airport data ----------
gp = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv", usecols=["Year", "Airport", "GACI"]).rename(
    columns={"Airport": "airport_iata", "Year": "y"})
gp = gp[gp.GACI > 0]
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "dep_seats"]).to_pandas()
a2c = am.dropna(subset=["iso3"]).drop_duplicates("airport_iata").set_index("airport_iata").iso3
seats_y = am.groupby(["airport_iata", "year"]).dep_seats.sum()
gp["iso3"] = gp.airport_iata.map(a2c)
gp = gp.dropna(subset=["iso3"])
gp["lnG"] = np.log(gp.GACI)
lnG = gp.set_index(["airport_iata", "y"]).lnG

rows = []
for src, E in EV.items():
    E = E.copy()
    E["mon"] = (E.t0 - 1) % 12 + 1
    E["yr"] = (E.t0 - 1) // 12
    E["E"] = np.where(E.mon <= 6, E.yr, E.yr + 1)
    stacks = []
    for k, ev in E.iterrows():
        lo, hi = ev.t0 - 36, ev.t0 + 36
        hits = fx_hit if src.startswith("FX") else gpr_hit
        bad = set(hits[(hits.t >= lo) & (hits.t <= hi)].iso3)
        if src.startswith("FX"):
            cov = fx_cov[(fx_cov.t >= lo) & (fx_cov.t <= hi)].groupby("iso3").size()
            pool = set(cov[cov >= 66].index)
        else:
            pool = GPRC
        ctrl = (pool - bad) - {ev.iso3}
        d = gp[gp.iso3.isin(ctrl | {ev.iso3}) & (gp.y >= ev.E - K) & (gp.y <= min(ev.E + K, 2019))].copy()
        d["stk"], d["treat"], d["k"] = k, (d.iso3 == ev.iso3).astype(np.int8), d.y - ev.E
        keys = list(zip(d.airport_iata, [ev.E - 1] * len(d)))
        d["hub"] = lnG.reindex(keys).to_numpy()
        d["size"] = np.log(pd.Series(seats_y.reindex(keys).to_numpy()).where(lambda s: s > 0)).to_numpy()
        stacks.append(d)
    S = pd.concat(stacks, ignore_index=True).dropna(subset=["hub", "size"])
    for v in ["hub", "size"]:
        u = S.drop_duplicates(["airport_iata", "stk"])[v]
        S[v] = (S[v] - u.mean()) / u.std()
    S["post"] = (S.k >= 0).astype(np.int8)
    S["tp"] = S.treat * S.post
    S["pH"], S["tpH"], S["pS"], S["tpS"] = S.post * S.hub, S.tp * S.hub, S.post * S["size"], S.tp * S["size"]
    S["fe_i"] = S.airport_iata + "_" + S.stk.astype(str)
    S["fe_y"] = S.y.astype(str) + "_" + S.stk.astype(str)
    S["fe_cy"] = S.iso3 + "_" + S.y.astype(str) + "_" + S.stk.astype(str)
    ntr = S[S.treat == 1].iso3.nunique()
    specs = [("(1) average Treat x Post", "lnG ~ tp | fe_i + fe_y", ["tp"]),
             ("(2) Treat x Post x Hub", "lnG ~ pH + tpH | fe_i + fe_cy", ["tpH", "pH"]),
             ("(3) + size", "lnG ~ pH + tpH + pS + tpS | fe_i + fe_cy", ["tpH", "tpS", "pH", "pS"])]
    for lab, f, terms in specs:
        m = pf.feols(f, data=S, vcov={"CRV1": "iso3"})
        td = m.tidy()
        for t in terms:
            rows.append(dict(events=src, spec=lab, term=t, b=td.loc[t, "Estimate"], se=td.loc[t, "Std. Error"],
                             p=td.loc[t, "Pr(>|t|)"], n=int(m._N), treated_countries=ntr, events_n=S[S.treat == 1].stk.nunique(),
                             clusters=S.iso3.nunique()))
    names = []
    for kk in [-3, -2, 0, 1, 2, 3]:
        nm = f"k{kk}".replace("-", "m")
        S["H_" + nm] = ((S.k == kk) & (S.treat == 1)) * S.hub
        S["C_" + nm] = (S.k == kk) * S.hub
        names.append(nm)
    m = pf.feols("lnG ~ " + " + ".join(["H_" + n for n in names] + ["C_" + n for n in names]) + " | fe_i + fe_cy",
                 data=S, vcov={"CRV1": "iso3"})
    td = m.tidy()
    for nm in names:
        rows.append(dict(events=src, spec="(4) event study Treat x Hub", term=nm, b=td.loc["H_" + nm, "Estimate"],
                         se=td.loc["H_" + nm, "Std. Error"], p=td.loc["H_" + nm, "Pr(>|t|)"], n=int(m._N),
                         treated_countries=ntr, events_n=S[S.treat == 1].stk.nunique(), clusters=S.iso3.nunique()))
    print(src, "done: stacks", S.stk.nunique(), "treated airports", S[S.treat == 1].airport_iata.nunique(), flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_staggered_gaci.csv", index=False)
pd.set_option("display.width", 220)
print(R.round(4).to_string(index=False))
