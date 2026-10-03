# -*- coding: utf-8 -*-
"""Which airports are resilient to oil supply shocks? (definitions approved by the user 2026-10-02)

Sample: airports with scheduled seats in 2007 and a 2007 GACI value; response window 2008-2019.
Shocks: Kaenzig (2021) news shock and Baumeister-Hamilton (2019) supply shock (x -1), 12-month sums lagged 3 months,
        scaled to 1 SD over 2008-2019 (monthly series).
Outcomes:
  (1) seats        D12 ln seats_it (both months > 0), monthly
  (2) service loss L_it = 1[seats_(i,t-12) > 0 and seats_it = 0], monthly, at-risk months only (seats_(t-12) > 0);
                   months with no record count as 0 seats
  (3) destinations D ln Degree_iy (GACI panel, annual), shock = December value of the 12-month sum lagged 3
                   (i.e. Oct y-1 .. Sep y)
Traits (2007 values unless noted; z-scores across sample airports):
  connectivity ln GACI; network position ln(1 + normalized betweenness); size ln seats; isolation ln km to the nearest
  other airport with 2007 service (OurAirports coordinates); stage length ln seat-km/seat; fuel intensity
  ln CO2/seat-km; gauge ln seats/flight; international seat share; destinations ln Degree; growth ln seats 2007/2002;
  resilience index R_pre2008 (1996-2007, single-trait spec only, many airports unscored);
  country traits ln GDP pc 2007 and oil rents % GDP 2007 (FE version A only; absorbed by country x month FE).
Model: Y_it = sum_k g_k (S_t x X_ik) + airport FE + [A: month FE | B: country x month FE] + e
  g_k per 1 SD trait and 1 SD shock. seats: + = smaller cut; service loss: - = less likely to lose service;
  destinations: + = keeps more destinations.
Specs: single trait (B; country traits in A), all airport traits jointly (A with country traits, B).
SE: country cluster + Newey-West over time (_est "dk"; L = 12 months, 2 years for the annual outcome).
Output: _res_airport_profile.csv, airport_traits_2007.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import json
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from _est import fit

# ---------------- airport-month grid ----------------
V = ["dep_seats", "n_dep_flights", "dep_seat_km", "co2_dep", "dep_seats_intl"]
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month"] + V).to_pandas()
am = am[am.iso3.notna() & (am.year >= 2002) & (am.year <= 2019)]
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv", usecols=["Year", "Airport", "Degree", "NorBetweenness", "GACI"])
s07 = am[am.year == 2007].groupby(["airport_iata", "iso3"], as_index=False)[V].sum()
s07 = s07[s07.dep_seats > 0]
g07 = g[g.Year == 2007].rename(columns={"Airport": "airport_iata"})
T = s07.merge(g07[["airport_iata", "GACI", "Degree", "NorBetweenness"]], on="airport_iata", how="inner")
T = T[T.GACI > 0]
s02 = am[am.year == 2002].groupby("airport_iata").dep_seats.sum()

# isolation: km to nearest other 2007-served airport
oa = pd.read_csv(r"data_external\india_atf_vat\sources\ourairports_airports_20261002.csv",
                 usecols=["iata_code", "latitude_deg", "longitude_deg", "type"], keep_default_na=False, na_values=[""])
oa = oa.dropna(subset=["iata_code"])
rank = {"large_airport": 0, "medium_airport": 1, "small_airport": 2}
oa["r"] = oa["type"].map(rank).fillna(3)
oa = oa.sort_values("r").drop_duplicates("iata_code")
T = T.merge(oa[["iata_code", "latitude_deg", "longitude_deg"]].rename(columns={"iata_code": "airport_iata"}),
            on="airport_iata", how="left")
c = T.dropna(subset=["latitude_deg"])
la, lo = np.radians(c.latitude_deg.to_numpy()), np.radians(c.longitude_deg.to_numpy())
near = np.empty(len(c))
for i in range(len(c)):
    d = 2 * 6371 * np.arcsin(np.sqrt(np.sin((la - la[i]) / 2) ** 2 + np.cos(la[i]) * np.cos(la) * np.sin((lo - lo[i]) / 2) ** 2))
    d[i] = np.inf
    near[i] = d.min()
T["near_km"] = T.airport_iata.map(dict(zip(c.airport_iata, near)))

# country traits
cp = pd.read_csv(r"..\GACI_CO2\gaci_co2_panel.csv", usecols=["c", "y", "lnpc"])
T["lnpc07"] = T.iso3.map(cp[cp.y == 2007].set_index("c").lnpc)
wb = json.load(open(r"data_external\wb_oilrents.json", encoding="utf-8"))
recs = wb[1] if isinstance(wb, list) and len(wb) > 1 and isinstance(wb[1], list) else wb
orr = pd.DataFrame([{"iso3": r.get("countryiso3code"), "y": int(r["date"]), "v": r["value"]} for r in recs
                    if r.get("value") is not None and str(r.get("date", "")).isdigit()])
orr = orr[orr.iso3.str.len() == 3].drop_duplicates(["iso3", "y"])
T["oilrent07"] = T.iso3.map(orr[orr.y == 2007].set_index("iso3").v)
R = pd.read_csv("resilience_airport.csv", usecols=["airport_iata", "R_pre2008"])
T = T.merge(R, on="airport_iata", how="left")

lg = lambda s: np.log(s.where(s > 0))
raw = {
    "connectivity (ln GACI)": lg(T.GACI),
    "network position (ln betweenness)": np.log1p(T.NorBetweenness),
    "size (ln seats)": lg(T.dep_seats),
    "isolation (ln km to nearest airport)": lg(T.near_km),
    "stage length": lg(T.dep_seat_km) - lg(T.dep_seats),
    "fuel intensity (CO2 per seat-km)": lg(T.co2_dep) - lg(T.dep_seat_km),
    "gauge (seats per flight)": lg(T.dep_seats) - lg(T.n_dep_flights),
    "international share": T.dep_seats_intl / T.dep_seats,
    "destinations (ln degree)": lg(T.Degree),
    "growth 2002-2007": lg(T.dep_seats) - lg(T.airport_iata.map(s02)),
    "resilience index (pre-2008)": T.R_pre2008,
    "country income (ln GDP pc)": T.lnpc07,
    "country oil rents (% GDP)": T.oilrent07,
}
TR = {k: f"x{i}" for i, k in enumerate(raw)}
for k, s in raw.items():
    T[TR[k]] = (s - s.mean()) / s.std()
AIR = [k for k in raw if not k.startswith(("country", "resilience"))]
CTRY = [k for k in raw if k.startswith("country")]
T.to_csv("airport_traits_2007.csv", index=False)
print("sample airports:", len(T), "countries:", T.iso3.nunique())
print(T[[TR[k] for k in AIR]].notna().sum().rename(index={v: k for k, v in TR.items()}).to_string(), flush=True)

# ---------------- shocks ----------------
f = pd.read_csv("fuel_monthly.csv", usecols=["year", "month", "kz_s12_l3", "bh_neg_s12_l3"])
w = f[(f.year >= 2008) & (f.year <= 2019)]
SH = {"Kaenzig": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
for s in SH.values():
    f["S_" + s] = f[s] / w[s].std()

# monthly grid 2007-01 .. 2019-12 for sample airports
ids = T[["airport_iata", "iso3"]]
grid = pd.MultiIndex.from_product([ids.airport_iata, range(2007, 2020), range(1, 13)], names=["airport_iata", "year", "month"]).to_frame(index=False)
grid = grid.merge(ids, on="airport_iata").merge(am.groupby(["airport_iata", "year", "month"], as_index=False).dep_seats.sum(),
                                                 on=["airport_iata", "year", "month"], how="left")
grid["dep_seats"] = grid.dep_seats.fillna(0)
grid["t"] = grid.year * 12 + grid.month
lag = grid[["airport_iata", "t", "dep_seats"]].copy()
lag["t"] += 12
grid = grid.merge(lag, on=["airport_iata", "t"], how="left", suffixes=("", "_m12"))
grid = grid[grid.year >= 2008].copy()
grid["y_seats"] = np.log(grid.dep_seats.where(grid.dep_seats > 0)) - np.log(grid.dep_seats_m12.where(grid.dep_seats_m12 > 0))
grid["y_loss"] = np.where(grid.dep_seats_m12 > 0, (grid.dep_seats == 0).astype(float), np.nan)
grid = grid.merge(f[["year", "month"] + ["S_" + s for s in SH.values()]], on=["year", "month"], how="left")
grid = grid.merge(T[["airport_iata"] + list(TR.values())], on="airport_iata", how="left")
grid["cm"] = grid.iso3 + "_" + grid.t.astype(str)
print("monthly rows", len(grid), "service-loss rate", round(grid.y_loss.mean(), 4), flush=True)

# annual destinations
ga = g.rename(columns={"Airport": "airport_iata"})
ga = ga[ga.airport_iata.isin(T.airport_iata) & (ga.Year >= 2007) & (ga.Year <= 2019)].sort_values(["airport_iata", "Year"])
ga["lnD"] = np.log(ga.Degree.where(ga.Degree > 0))
ga["y_dest"] = ga.groupby("airport_iata").lnD.diff()
ga.loc[ga.groupby("airport_iata").Year.diff() != 1, "y_dest"] = np.nan
ga = ga[ga.Year >= 2008].rename(columns={"Year": "year"})
dec = f[f.month == 12][["year"] + ["S_" + s for s in SH.values()]]
ga = ga.merge(dec, on="year", how="left").merge(T[["airport_iata", "iso3"] + list(TR.values())], on="airport_iata", how="left")
ga["t"] = ga.year
ga["cy"] = ga.iso3 + "_" + ga.year.astype(str)

# ---------------- estimation ----------------
OUT = [("seats", grid, "y_seats", "t", "cm", 12), ("service loss", grid, "y_loss", "t", "cm", 12),
       ("destinations (annual)", ga, "y_dest", "t", "cy", 2)]
rows = []
for olab, D, y, tcol, ctfe, L in OUT:
    for slab, s in SH.items():
        S = "S_" + s

        def run(traits, fe, spec):
            d = D.dropna(subset=[y, S] + [TR[k] for k in traits]).copy()
            xs = []
            for k in traits:
                d["i_" + TR[k]] = d[S] * d[TR[k]]
                xs.append("i_" + TR[k])
            fes = ["airport_iata", tcol] if fe == "A" else ["airport_iata", ctfe]
            o = fit(d, y, exog=xs, fes=fes, vc=("dk", "iso3", tcol, L), return_fs=False)
            for k in traits:
                v = "i_" + TR[k]
                rows.append(dict(outcome=olab, shock=slab, fe=fe, spec=spec, trait=k, b=o["coef"][v], se=o["se"][v],
                                 p=o["p"][v], n=o["n"], airports=d.airport_iata.nunique(), ymean=o["ymean"]))

        for k in AIR + ["resilience index (pre-2008)"]:
            run([k], "B", "single")
        for k in CTRY:
            run([k], "A", "single")
        run(AIR + CTRY, "A", "joint")
        run(AIR, "B", "joint")
        print(olab, slab, "done", flush=True)
out = pd.DataFrame(rows)
out.to_csv("_res_airport_profile.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 500)
print(out.round(4).to_string(index=False))
