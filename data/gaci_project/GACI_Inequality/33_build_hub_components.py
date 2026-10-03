# -*- coding: utf-8 -*-
"""33_build_hub_components.py : components of the hub airport's connectivity, country-year.
   For each country-year, the hub = airport with the highest GACI. Components from the raw airport panel:
   Degree (number of connections), TotalCapacity (seats), Eigen (eigenvector centrality), NorClose (closeness),
   NorBetweenness (flow betweenness), RegionalImportance. Also the same components summed over the other airports.
   Mapping airport -> ISO3 reuses ../build_gaci_panel.py (ourairports IATA -> ISO2, iso2to3.json).
   Output: _hub_components.csv (c, y, hub_airport, hub_gaci, hub_deg, hub_cap, hub_eig, hub_close, hub_betw, hub_regimp,
           rest_deg, rest_cap, rest_eig, rest_close, rest_betw, n_air)"""
import os, csv, json, collections, numpy as np, pandas as pd
D = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D, "..")
csv.field_size_limit(10 ** 7)
ap_iso2 = {}
for r in csv.DictReader(open(os.path.join(P, "ourairports.csv"), encoding="utf-8", errors="replace")):
    ia = (r.get("iata_code") or "").strip()
    if len(ia) == 3: ap_iso2[ia] = r.get("iso_country", "").strip()
iso2to3 = json.load(open(os.path.join(P, "iso2to3.json")))
raw = pd.read_csv(os.path.join(P, "GACI1996_2024_new_panel_data.csv"), encoding="utf-8", encoding_errors="replace")
raw.columns = [c.strip().lstrip("﻿") for c in raw.columns]
raw["c"] = raw["Airport"].str.strip().map(lambda a: iso2to3.get(ap_iso2.get(a, ""), ""))
raw = raw[raw.c != ""].rename(columns={"Year": "y"})
num = ["Degree", "TotalCapacity", "Eigen", "NorClose", "NorBetweenness", "RegionalImportance", "GACI"]
for k in num: raw[k] = pd.to_numeric(raw[k], errors="coerce")
raw = raw.sort_values(["c", "y", "GACI"], ascending=[True, True, False])
hub = raw.groupby(["c", "y"]).first().reset_index()
hub = hub.rename(columns={"Airport": "hub_airport", "GACI": "hub_gaci", "Degree": "hub_deg", "TotalCapacity": "hub_cap", "Eigen": "hub_eig", "NorClose": "hub_close", "NorBetweenness": "hub_betw", "RegionalImportance": "hub_regimp"})
tot = raw.groupby(["c", "y"]).agg(n_air=("Airport", "size"), tot_deg=("Degree", "sum"), tot_cap=("TotalCapacity", "sum"), tot_eig=("Eigen", "sum"), tot_close=("NorClose", "sum"), tot_betw=("NorBetweenness", "sum")).reset_index()
out = hub[["c", "y", "hub_airport", "hub_gaci", "hub_deg", "hub_cap", "hub_eig", "hub_close", "hub_betw", "hub_regimp"]].merge(tot, on=["c", "y"])
for k in ["deg", "cap", "eig", "close", "betw"]:
    out["rest_" + k] = out["tot_" + k] - out["hub_" + k]
out = out.drop(columns=[c for c in out.columns if c.startswith("tot_")])
out.to_csv(os.path.join(D, "_hub_components.csv"), index=False)
print(out.shape); print(out.describe().T[["count", "mean", "min", "max"]].round(3).to_string())
print(out[out.c == "KOR"][["y", "hub_airport", "hub_gaci", "hub_deg", "hub_cap", "hub_eig", "hub_betw"]].iloc[[0, 5, 10, 20, -1]].to_string(index=False))
