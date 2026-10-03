# -*- coding: utf-8 -*-
"""Rescue variant: gateway-assigned heritage exposure.
Each natural/mixed site is assigned to its NEAREST GATEWAY airport within
300 km, where a gateway = airport in the global top quartile of 1996 seat
capacity (tourists enter through hubs, then travel overland).
exposure_gw_j = number of sites assigned to airport j; z_gw = a_t x exposure.
Appends to airport_hiv_panel.csv -> airport_hiv_panel2.csv."""
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
HERE = GACI + r"\GACI_CO2"

uh = pd.read_csv(GACI + r"\uh_csv.csv", usecols=["category", "coordinates"])
uh = uh[uh.category.isin(["Natural", "Mixed"])]
cc = uh.coordinates.str.split("|", expand=True)
uh = pd.DataFrame({"slat": pd.to_numeric(cc[0], errors="coerce"),
                   "slon": pd.to_numeric(cc[1], errors="coerce")}).dropna()

ap = pd.read_csv(GACI + r"\airport_coords_merged.csv").dropna(subset=["lat", "lon"])
g96 = pd.read_csv(GACI + r"\GACI1996_2024_new_panel_data.csv",
                  usecols=["Year", "Airport", "TotalCapacity"])
g96 = g96[g96.Year == 1996][["Airport", "TotalCapacity"]]
ap = ap.merge(g96, on="Airport", how="left")
cut = ap.TotalCapacity.quantile(0.75)
gw = ap[ap.TotalCapacity >= cut].reset_index(drop=True)
print(f"gateways (top-quartile 1996 capacity): {len(gw)} airports, cutoff {cut:,.0f} seats")

R = 6371.0
la = np.radians(gw.lat.to_numpy())[:, None]
lo = np.radians(gw.lon.to_numpy())[:, None]
sa = np.radians(uh.slat.to_numpy())[None, :]
so = np.radians(uh.slon.to_numpy())[None, :]
h = (np.sin((sa - la) / 2) ** 2
     + np.cos(la) * np.cos(sa) * np.sin((so - lo) / 2) ** 2)
dist = 2 * R * np.arcsin(np.sqrt(np.clip(h, 0, 1)))  # gateways x sites

nearest = dist.argmin(axis=0)
mind = dist.min(axis=0)
ok = mind <= 300
print(f"sites assigned to a gateway within 300km: {ok.sum()}/{len(uh)}")
counts = pd.Series(gw.Airport.to_numpy()[nearest[ok]]).value_counts()
print("top assigned gateways:", dict(counts.head(10)))

p = pd.read_csv(HERE + r"\airport_hiv_panel.csv")
p["exp_gw"] = p.airport_iata.map(counts).fillna(0.0)
p["z_gw"] = p.a_t * p.exp_gw
p.to_csv(HERE + r"\airport_hiv_panel2.csv", index=False)
print(f"airports with exp_gw>0: {(p[p.year==2023].exp_gw > 0).sum()}")
print("wrote airport_hiv_panel2.csv")
