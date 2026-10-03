# -*- coding: utf-8 -*-
"""Extract high-speed rail ways (with geometry) and nearby stations from OpenStreetMap via Overpass.

Per country (ISO 3166-1 area; mainland China in bbox tiles):
  ways  : railway in {rail, construction} and highspeed=yes  -> tags + geometry
  nodes : all railway in {station, halt} nodes of the area -> tags + coords (filtered to 300 m of the ways later)
Raw JSON saved to data_external/osm/<CC or CN tile>_<ways|stations>.json; extraction time in _extract_log.txt.
Countries = every country with an in-operation section in UIC 2018/2022, plus DE/AT/CH neighbours already listed.
"""
import json
import os
import time
import requests

OUT = "data_external/osm/"
os.makedirs(OUT, exist_ok=True)
H = {"User-Agent": "research (mailto:sunbinyoo.kyushu@gmail.com)"}
EPS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter",
       "https://overpass.kumi.systems/api/interpreter"]
CC = ["JP", "KR", "TW", "ES", "FR", "DE", "IT", "TR", "GB", "BE", "NL", "AT", "CH", "SE", "FI", "DK", "PL",
      "SA", "MA", "RS", "US"]
# mainland China in tiles (lon_min, lat_min, lon_max, lat_max)
# tiles cover lon 73-135.1 x lat 18-53.6 without gaps; they also catch TW/KR/HK ways, which 03_assign_dates.py
# assigns to the country files first (CN tiles only add ways not already in a country file)
CN_TILES = {"CN_W": (73, 18, 104, 53.6), "CN_C1": (104, 18, 112, 35), "CN_C2": (104, 35, 112, 53.6),
            "CN_E1": (112, 18, 123, 28), "CN_E2": (112, 28, 123, 35), "CN_E3": (112, 35, 135.1, 53.6)}

# ways and stations are fetched separately (an "around" filter on thousands of ways times out);
# stations are the country's railway=station/halt nodes, filtered to 300 m of the ways in 03_assign_dates.py
def q_area(cc, what):
    sel = ('way(area.a)[railway~"^(rail|construction)$"][highspeed=yes]; out tags geom;' if what == "ways"
           else 'node(area.a)[railway~"^(station|halt)$"]; out body;')
    return f'[out:json][timeout:900];area["ISO3166-1"="{cc}"][admin_level=2]->.a;{sel}'

def q_bbox(b, what):
    s, w, n, e = b[1], b[0], b[3], b[2]
    sel = (f'way({s},{w},{n},{e})[railway~"^(rail|construction)$"][highspeed=yes]; out tags geom;' if what == "ways"
           else f'node({s},{w},{n},{e})[railway~"^(station|halt)$"]; out body;')
    return "[out:json][timeout:900];" + sel

def run(name, q):
    fn = OUT + name + ".json"
    if os.path.exists(fn) and os.path.getsize(fn) > 1000:
        print(name, "cached")
        return
    for k in range(6):
        ep = EPS[k % len(EPS)]
        try:
            r = requests.post(ep, data={"data": q}, headers=H, timeout=1000)
            if r.status_code != 200 or not r.text.lstrip().startswith("{"):
                raise RuntimeError(f"HTTP {r.status_code}: " + " ".join(r.text.split())[:160])
            j = r.json()
            if not j.get("elements"):
                # some mirrors lack the area index and silently return nothing
                raise RuntimeError("empty result (area index missing on this server?)")
            json.dump(j, open(fn, "w", encoding="utf-8"))
            print(f"{name}: elements {len(j['elements']):,} ({ep.split('/')[2]})", flush=True)
            return
        except Exception as e:
            print(f"{name}: attempt {k + 1} failed on {ep.split('/')[2]}: {str(e)[:200]}", flush=True)
            time.sleep(60)
    print(name, "FAILED", flush=True)

for cc in CC:
    for what in ("ways", "stations"):
        run(f"{cc}_{what}", q_area(cc, what))
        time.sleep(10)
for nm, b in CN_TILES.items():
    for what in ("ways", "stations"):
        run(f"{nm}_{what}", q_bbox(b, what))
        time.sleep(10)
open(OUT + "_extract_log.txt", "a").write("extracted " + time.strftime("%Y-%m-%d %H:%M") + "\n")
print("done")
