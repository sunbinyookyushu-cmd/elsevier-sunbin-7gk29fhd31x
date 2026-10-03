# -*- coding: utf-8 -*-
"""
12_build_spillover.py
Neighbour-connectivity spillover variables for the CO2 paper.
Country centroids = mean lat/lon of the country's airports (activity centroid,
../airport_coords_merged.csv). W = inverse haversine distance, row-normalised
over countries present in the panel that year.
Outputs spillover_vars.csv: c, y, nbr_lngaci (distance-weighted avg of other
countries' ln GACI cwm), nbr_feyrer (same for the Feyrer instrument).
"""
import os
import sys

import numpy as np
import pandas as pd
import pycountry

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

ALIAS = {
    "Russia": "RUS", "Iran": "IRN", "Venezuela": "VEN", "Bolivia": "BOL",
    "Tanzania": "TZA", "Syria": "SYR", "Laos": "LAO", "Vietnam": "VNM",
    "South Korea": "KOR", "North Korea": "PRK", "Moldova": "MDA",
    "Democratic Republic of the Congo": "COD", "Congo (Kinshasa)": "COD",
    "Congo (Brazzaville)": "COG", "Republic of the Congo": "COG",
    "Ivory Coast": "CIV", "Cote d'Ivoire": "CIV", "Cape Verde": "CPV",
    "Brunei": "BRN", "Micronesia": "FSM", "Macedonia": "MKD",
    "North Macedonia": "MKD", "Czech Republic": "CZE", "Burma": "MMR",
    "Myanmar": "MMR", "East Timor": "TLS", "Palestine": "PSE",
    "Taiwan": "TWN", "Hong Kong": "HKG", "Macau": "MAC",
    "Turkey": "TUR", "United States": "USA", "United Kingdom": "GBR",
}

def to_iso3(name, cache={}):
    if name in cache:
        return cache[name]
    iso = ALIAS.get(name)
    if iso is None:
        try:
            iso = pycountry.countries.lookup(name).alpha_3
        except LookupError:
            try:
                iso = pycountry.countries.search_fuzzy(name)[0].alpha_3
            except LookupError:
                iso = None
    cache[name] = iso
    return iso

ap = pd.read_csv(os.path.join(HERE, "..", "airport_coords_merged.csv"))
ap["c"] = ap["country"].astype(str).map(to_iso3)
cent = ap.dropna(subset=["c"]).groupby("c")[["lat", "lon"]].mean()

panel = pd.read_csv(os.path.join(HERE, "..", "gaci_panel_combined.csv"),
                    usecols=["c", "y", "ln_gaci_cwm", "feyrer_int"])
panel = panel[panel["c"].isin(cent.index)].copy()
countries = sorted(panel["c"].unique())
print("countries with centroid + panel:", len(countries))

lat = np.radians(cent.loc[countries, "lat"].values)
lon = np.radians(cent.loc[countries, "lon"].values)
dlat = lat[:, None] - lat[None, :]
dlon = lon[:, None] - lon[None, :]
h = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
dist = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
np.fill_diagonal(dist, np.inf)
W = 1.0 / np.maximum(dist, 100.0)  # floor 100km to avoid microstate blowups
np.fill_diagonal(W, 0.0)

idx = {c: i for i, c in enumerate(countries)}
out = []
for y, g in panel.groupby("y"):
    g = g.set_index("c")
    v_g = np.full(len(countries), np.nan)
    v_f = np.full(len(countries), np.nan)
    for c in g.index:
        v_g[idx[c]] = g.loc[c, "ln_gaci_cwm"]
        v_f[idx[c]] = g.loc[c, "feyrer_int"]
    ok = ~np.isnan(v_g)
    Wy = W[:, ok]
    rs = Wy.sum(axis=1, keepdims=True)
    Wn = np.divide(Wy, rs, out=np.zeros_like(Wy), where=rs > 0)
    nbr_g = Wn @ v_g[ok]
    okf = ~np.isnan(v_f)
    Wyf = W[:, okf]
    rsf = Wyf.sum(axis=1, keepdims=True)
    Wnf = np.divide(Wyf, rsf, out=np.zeros_like(Wyf), where=rsf > 0)
    nbr_f = Wnf @ v_f[okf]
    for c in g.index:
        out.append({"c": c, "y": y, "nbr_lngaci": nbr_g[idx[c]], "nbr_feyrer": nbr_f[idx[c]]})

res = pd.DataFrame(out)
res.to_csv(os.path.join(HERE, "spillover_vars.csv"), index=False)
print("saved spillover_vars.csv", res.shape)
print(res.describe().round(3).to_string())
print("\ncorr(nbr_lngaci, nbr_feyrer):",
      round(res[["nbr_lngaci", "nbr_feyrer"]].corr().iloc[0, 1], 3))
