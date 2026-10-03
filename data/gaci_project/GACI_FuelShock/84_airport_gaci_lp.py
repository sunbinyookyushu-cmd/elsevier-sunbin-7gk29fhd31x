# -*- coding: utf-8 -*-
"""Airport-level version of 83: which airports lose relative connectivity after oil supply shocks?

  lnGACI_(i,y+h) - lnGACI_(i,y-1) = a_i + [A: d_y | B: d_(country x y)] + g_h (S_y x Z_i) + th_h (S_y x Inc_c)
                                     + controls + r dlnGACI_(i,y-1) + e,     h = 0..4
  GACI: airport panel 1996-2024 (GACI1996_2024_new_panel_data.csv). Sample: airports with 1996 GACI and seats
  (airport_base.csv). Z (1996, z-scored over airports): fuel exposure = ln stage length; isolation = ln km to the
  nearest other 1996-served airport (OurAirports coordinates); international seat share; size = ln seats; initial
  connectivity = ln GACI 1996; country oil rents 1996 (version A only, absorbed by country x year FE in B).
  Inc_c = ln GDP pc 1996 of the country (A only). Controls in A: country ln GDP and ln population in y-1.
  S_y = annual sum of the monthly Kaenzig / sign-flipped BH supply shock, 1 SD (1997-2019).
  Samples: main y+h <= 2019; extended y+h <= 2024 with any of 2020-2021 in [y-1, y+h] dropped.
  SE: country cluster + Newey-West over years, L = max(h+1, 2).
Output: _res_airport_gaci_lp.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import warnings

import numpy as np
import pandas as pd
from _est import fit

warnings.filterwarnings("ignore")
b = pd.read_csv("airport_base.csv")
b = b[b.GACI_96.notna() & (b.seats_96 > 0) & b.iso3.notna()].copy()
oa = pd.read_csv(r"data_external\india_atf_vat\sources\ourairports_airports_20261002.csv",
                 usecols=["iata_code", "latitude_deg", "longitude_deg", "type"], keep_default_na=False, na_values=[""])
oa = oa.dropna(subset=["iata_code"])
oa["r"] = oa["type"].map({"large_airport": 0, "medium_airport": 1, "small_airport": 2}).fillna(3)
oa = oa.sort_values("r").drop_duplicates("iata_code")
b = b.merge(oa[["iata_code", "latitude_deg", "longitude_deg"]].rename(columns={"iata_code": "airport_iata"}), on="airport_iata", how="left")
cc = b.dropna(subset=["latitude_deg"])
la, lo = np.radians(cc.latitude_deg.to_numpy()), np.radians(cc.longitude_deg.to_numpy())
near = np.empty(len(cc))
for i in range(len(cc)):
    dd = 2 * 6371 * np.arcsin(np.sqrt(np.sin((la - la[i]) / 2) ** 2 + np.cos(la[i]) * np.cos(la) * np.sin((lo - lo[i]) / 2) ** 2))
    dd[i] = np.inf
    near[i] = dd.min()
b["near_km"] = b.airport_iata.map(dict(zip(cc.airport_iata, near)))
lg = lambda s: np.log(s.where(s > 0))
ZR = {"fuel exposure (stage length)": lg(b.stage_96), "isolation (km to nearest airport)": lg(b.near_km),
      "international share": b.intl_share_96, "size (ln seats)": lg(b.seats_96),
      "initial connectivity (GACI 1996)": lg(b.GACI_96), "country oil rents": b.oilrent_c96, "income": b.lnpc_c96}
ZK = {k: f"z{i}" for i, k in enumerate(ZR)}
for k, s in ZR.items():
    b[ZK[k]] = (s - s.mean()) / s.std()
AIR = ["fuel exposure (stage length)", "isolation (km to nearest airport)", "international share", "size (ln seats)",
       "initial connectivity (GACI 1996)"]

g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv", usecols=["Year", "Airport", "GACI"])
g = g[g.Airport.isin(b.airport_iata) & (g.GACI > 0)]
W = g.pivot_table(index="Airport", columns="Year", values="GACI")
W = np.log(W.reindex(columns=range(1996, 2025)))
fa = pd.read_csv("fuel_annual.csv", usecols=["year", "kz", "bh_neg"]).set_index("year")
sd = fa.loc[1997:2019].std()
cy = pd.read_csv("country_year.csv", usecols=["c", "y", "lngdp", "lnpop"])
cy["y"] += 1

rows = []
for h in range(0, 5):
    dy = (W.shift(-h, axis=1) - W.shift(1, axis=1)).stack().reset_index()
    dy.columns = ["airport_iata", "y", "dy"]
    dl = (W - W.shift(1, axis=1)).shift(1, axis=1).stack().reset_index()
    dl.columns = ["airport_iata", "y", "dl"]
    d = dy.merge(dl, on=["airport_iata", "y"], how="left").merge(b[["airport_iata", "iso3"] + list(ZK.values())], on="airport_iata")
    d = d.merge(cy.rename(columns={"c": "iso3", "lngdp": "lngdp_l1", "lnpop": "lnpop_l1"}), on=["iso3", "y"], how="left")
    for s in ["kz", "bh_neg"]:
        d["S_" + s] = d.y.map(fa[s] / sd[s])
    d["cy"] = d.iso3 + "_" + d.y.astype(str)
    for samp, keep in [("main (to 2019)", (d.y >= 1997) & (d.y + h <= 2019)),
                       ("extended (to 2024, 2020-21 out)", (d.y >= 1997) & (d.y + h <= 2024)
                        & ~d.y.apply(lambda y: any(t in (2020, 2021) for t in range(y - 1, y + h + 1))))]:
        d0 = d[keep]
        for slab, s in [("Kaenzig", "S_kz"), ("BH", "S_bh_neg")]:
            for fe in ["A", "B"]:
                pool = AIR + (["country oil rents"] if fe == "A" else [])
                specs = [(k, [k]) for k in pool] + [("all jointly", pool)]
                for spec, zz in specs:
                    zv = [ZK[k] for k in zz] + ([ZK["income"]] if fe == "A" else [])
                    ctl = ["lngdp_l1", "lnpop_l1"] if fe == "A" else []
                    dd = d0.dropna(subset=["dy", "dl", s] + zv + ctl).copy()
                    xs = []
                    for v in zv:
                        dd["i_" + v] = dd[s] * dd[v]
                        xs.append("i_" + v)
                    fes = ["airport_iata", "y"] if fe == "A" else ["airport_iata", "cy"]
                    o = fit(dd, "dy", exog=xs + ctl + ["dl"], fes=fes, vc=("dk", "iso3", "y", max(h + 1, 2)), return_fs=False)
                    for k in zz:
                        v = "i_" + ZK[k]
                        rows.append(dict(sample=samp, shock=slab, fe=fe, h=h, spec="all jointly" if spec == "all jointly" else "alone",
                                         Z=k, b=o["coef"][v], se=o["se"][v], p=o["p"][v], n=o["n"], airports=dd.airport_iata.nunique()))
    print("h", h, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_airport_gaci_lp.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 500)
m = R[R["sample"].str.startswith("main")]
print(m.pivot_table(index=["fe", "shock", "spec", "Z"], columns="h", values="b").round(4).to_string())
print(m.pivot_table(index=["fe", "shock", "spec", "Z"], columns="h", values="p").round(3).to_string())
e = R[R["sample"].str.startswith("extended") & (R.spec == "alone")]
print("\nextended, alone:")
print(e.pivot_table(index=["fe", "shock", "Z"], columns="h", values="b").round(4).to_string())
print(e.pivot_table(index=["fe", "shock", "Z"], columns="h", values="p").round(3).to_string())
print("n/airports (h=0, main, A):", R[(R.h == 0) & R["sample"].str.startswith("main") & (R.fe == "A")][["n", "airports"]].iloc[0].to_dict())
