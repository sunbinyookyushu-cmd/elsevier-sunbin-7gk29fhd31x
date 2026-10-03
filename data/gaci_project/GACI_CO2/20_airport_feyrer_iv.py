# -*- coding: utf-8 -*-
"""
20_airport_feyrer_iv.py   (LZ comment 2, identification pilot, 2026-09-03)
Airport-level Feyrer-type shifter:
   airMA_a,1996 = sum over foreign countries j of pop_j,1996 / d(airport a, centroid j)
   z_a,t        = a_t x ln airMA_a,1996        (a_t = world seat-capacity index, as country IV)
Within country x year fixed effects, z varies across airports of the same country
only through their location relative to foreign population. Size-by-cycle stress
variables: a_t x ln seat-km_a,1996 and a_t x ln GACI_a,1996 (must not kill z).
Output: airport_feyrer_panel.csv (airport_iata, year, iso3, z_air, z_cap96, z_gaci96, ln_airma96)
"""
import os, sys, json
import numpy as np
import pandas as pd
import pycountry

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); UP = os.path.join(HERE, "..")
ALIAS = {"Russia": "RUS", "Iran": "IRN", "Venezuela": "VEN", "Bolivia": "BOL", "Tanzania": "TZA", "Syria": "SYR", "Laos": "LAO", "Vietnam": "VNM",
         "South Korea": "KOR", "North Korea": "PRK", "Moldova": "MDA", "Democratic Republic of the Congo": "COD", "Republic of the Congo": "COG",
         "Ivory Coast": "CIV", "Cape Verde": "CPV", "Brunei": "BRN", "Micronesia": "FSM", "Macedonia": "MKD", "Czech Republic": "CZE", "Burma": "MMR",
         "East Timor": "TLS", "Palestine": "PSE", "Taiwan": "TWN", "Hong Kong": "HKG", "Macau": "MAC", "Turkey": "TUR", "United States": "USA", "United Kingdom": "GBR", "Swaziland": "SWZ", "Eswatini": "SWZ"}
def to_iso3(name, cache={}):
    if name in cache: return cache[name]
    iso = ALIAS.get(name)
    if iso is None:
        try: iso = pycountry.countries.lookup(name).alpha_3
        except LookupError:
            try: iso = pycountry.countries.search_fuzzy(name)[0].alpha_3
            except LookupError: iso = None
    cache[name] = iso; return iso

ap = pd.read_csv(os.path.join(UP, "airport_coords_merged.csv")); ap["c"] = ap["country"].astype(str).map(to_iso3)
cent = ap.dropna(subset=["c"]).groupby("c")[["lat", "lon"]].mean()
pop = json.load(open(os.path.join(UP, "wb_pop.json")))
pop96 = {k.split("|")[0]: float(v) for k, v in pop.items() if k.split("|")[1] == "1996"}
cs = [c for c in cent.index if c in pop96]
clat = np.radians(cent.loc[cs, "lat"].values); clon = np.radians(cent.loc[cs, "lon"].values); P = np.array([pop96[c] for c in cs])

panel = pd.read_csv(os.path.join(HERE, "airport_co2_panel.csv"))
apc = ap.drop_duplicates("Airport").set_index("Airport")[["lat", "lon"]]
base = panel[panel.year == 1996][["airport_iata", "iso3", "dep_seat_km", "GACI"]].copy()
base = base.merge(apc, left_on="airport_iata", right_index=True, how="left").dropna(subset=["lat", "lon"])
alat = np.radians(base["lat"].values); alon = np.radians(base["lon"].values)
h = np.sin((alat[:, None] - clat[None, :]) / 2) ** 2 + np.cos(alat[:, None]) * np.cos(clat[None, :]) * np.sin((alon[:, None] - clon[None, :]) / 2) ** 2
D = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
own = np.array([[c == iso for c in cs] for iso in base["iso3"].values])  # leave own country out
W = np.where(own, 0.0, 1.0 / np.maximum(D, 50.0))
base["ln_airma96"] = np.log(W @ P)
base["ln_skm96"] = np.log(base["dep_seat_km"].where(base["dep_seat_km"] > 0))
base["ln_gaci96"] = np.log(base["GACI"].where(base["GACI"] > 0))
print("airports with 1996 base:", len(base), "| within-country sd of ln_airma96:", round(base.groupby("iso3")["ln_airma96"].std().mean(), 3))

fey = pd.read_csv(os.path.join(UP, "gaci_panel_feyrer.csv"), usecols=["y", "a_t"]).drop_duplicates("y").set_index("y")["a_t"]
out = panel[["airport_iata", "year", "iso3"]].merge(base[["airport_iata", "ln_airma96", "ln_skm96", "ln_gaci96"]], on="airport_iata", how="inner")
out["a_t"] = out["year"].map(fey)
out["z_air"] = out["a_t"] * out["ln_airma96"]
out["z_cap96"] = out["a_t"] * out["ln_skm96"]
out["z_gaci96"] = out["a_t"] * out["ln_gaci96"]
out.to_csv(os.path.join(HERE, "airport_feyrer_panel.csv"), index=False)
print("saved airport_feyrer_panel.csv", out.shape)
print("DONE_20")
