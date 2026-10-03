# -*- coding: utf-8 -*-
"""Assign opening dates to OSM high-speed ways and stations.

Date sources, in order of priority:
  1. UIC section dates (2018 edition: exact date; 2022 edition: year -> 1 July of that year, flagged).
     Each in-operation UIC section is matched to OSM by its end (and intermediate) stations; the shortest path
     on the OSM high-speed graph between consecutive matched stations receives the section date.
  2. OSM start_date / opening_date on the way itself (only years >= 1964; upgraded conventional lines often carry
     their 19th-century date, so those are dropped). Full dates are used when tagged. In China this source comes
     first (see the note at the assignment step).
  3. For FR / GB / NL, where UIC lists lines rather than stations, UIC dates are carried to OSM ways by line name
     (data_external/primary/osm_name_crosswalk.csv; geographic rules split multi-phase lines).
Station names: English exonyms in UIC (Cologne, Turin, ...) are mapped to local names; stops in parentheses are
context and dropped; stations snap to the high-speed graph within 10 km; matched end stations keep the section date
even when no path is found.
Japan: stations take the MLIT N05-20 service-start year of their Shinkansen line (official), month from UIC.
Station opening = earliest date among dated high-speed ways within 300 m of the station node.
Outputs: data/hsr_ways_dated.parquet, data/hsr_stations_dated.csv, data/uic_match_log.csv
"""
import glob
import json
import math
import re
import unicodedata
from collections import defaultdict

import networkx as nx
import numpy as np
import pandas as pd

OSM = "data_external/osm/"
UIC = pd.read_csv("data/uic_sections.csv", parse_dates=["date"])
UIC = UIC[UIC.status == "In operation"].copy()
CMAP = {"JP": "JAPAN", "KR": "SOUTH KOREA", "TW": "TAIWAN", "ES": "SPAIN", "FR": "FRANCE", "DE": "GERMANY", "IT": "ITALY",
        "TR": "TURKEY", "GB": "UNITED KINGDOM|UK", "BE": "BELGIUM", "NL": "NETHERLANDS", "AT": "AUSTRIA", "CH": "SWITZERLAND",
        "SE": "SWEDEN", "FI": "FINLAND", "DK": "DENMARK", "PL": "POLAND", "SA": "SAUDI", "MA": "MOROCCO", "RS": "SERBIA",
        "US": "USA", "CN": "CHINA"}


def norm(s):
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"\b(railway|train|rail|station|gare|estacion|stazione|bahnhof|hbf|hauptbahnhof|high speed|av|tgv|hsr)\b", " ", s)
    s = s.replace("-", " ").replace("'", "").replace(".", " ")
    return re.sub(r"\s+", " ", s).strip()


EXO = {"cologne": "koln", "munich": "munchen", "nuremberg": "nurnberg", "turin": "torino", "milan": "milano",
       "rome": "roma", "florence": "firenze", "venice": "venezia", "naples": "napoli", "genoa": "genova",
       "padua": "padova", "seville": "sevilla", "saragossa": "zaragoza", "brussels": "bruxelles", "antwerp": "antwerpen",
       "liege": "liege", "the hague": "den haag", "lisbon": "lisboa", "vienna": "wien", "copenhagen": "kobenhavn",
       "gothenburg": "goteborg", "hanover": "hannover", "frankfurt": "frankfurt (main)", "basel": "basel sbb",
       "istanbul": "istanbul", "ankara": "ankara", "moscow": "moskva", "mecca": "makkah", "medina": "madinah",
       "tianjing": "tianjin", "xiamenb": "xiamen"}


def hav(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(min(1, h)))


def osm_year(t):
    for k in ("start_date", "opening_date"):
        v = t.get(k)
        if v:
            m = re.search(r"(1[89]\d{2}|20\d{2})", v)
            if m:
                return int(m.group(1)), v
    return None, None


def osm_date(raw, year):
    """full date when the tag gives it (YYYY-MM-DD, YYYY-MM -> 15th), else 1 July of the year"""
    if isinstance(raw, str):
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", raw)
        if m:
            try:
                return pd.Timestamp(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                pass
        m = re.search(r"(\d{4})-(\d{2})(?!-)", raw)
        if m:
            try:
                return pd.Timestamp(int(m.group(1)), int(m.group(2)), 15)
            except ValueError:
                pass
    return pd.Timestamp(int(year), 7, 1)


ways, stations = [], []
files = sorted(glob.glob(OSM + "*_ways.json"), key=lambda f: ("CN_" in f, f))     # country files before CN tiles
for fn in files:
    tag = fn.replace("\\", "/").split("/")[-1].replace("_ways.json", "")
    cc = "CN" if tag.startswith("CN_") else tag
    for e in json.load(open(fn, encoding="utf-8"))["elements"]:
        t = e.get("tags", {})
        if e["type"] != "way" or "geometry" not in e:
            continue
        g = [(p["lat"], p["lon"]) for p in e["geometry"]]
        y, raw = osm_year(t)
        ways.append(dict(cc=cc, way_id=e["id"], nodes=e.get("nodes", []), geom=g, railway=t.get("railway"),
                         name=t.get("name", ""), ref=t.get("ref", ""), maxspeed=t.get("maxspeed", ""),
                         osm_year=y, osm_date_raw=raw, usage=t.get("usage", ""),
                         km=sum(hav(g[i], g[i + 1]) for i in range(len(g) - 1))))
    sf = fn.replace("_ways.json", "_stations.json")
    if not __import__("os").path.exists(sf):
        print("no station file yet:", sf)
        continue
    for e in json.load(open(sf, encoding="utf-8"))["elements"]:
        if "lat" not in e:
            continue
        t = e.get("tags", {})
        stations.append(dict(cc=cc, node_id=e["id"], lat=e["lat"], lon=e["lon"], name=t.get("name", ""),
                             name_en=t.get("name:en", ""), name_local=t.get("name:ja", t.get("name:zh", t.get("name:ko", ""))),
                             railway=t.get("railway", "")))
W = pd.DataFrame(ways).drop_duplicates("way_id")
S = pd.DataFrame(stations).drop_duplicates("node_id")
from scipy.spatial import cKDTree
_p = [(la, lo * math.cos(math.radians(la))) for g in W.geom for (la, lo) in g]
_t = cKDTree(np.array(_p) * 111.0)
_q = np.column_stack([S.lat, S.lon * np.cos(np.radians(S.lat))]) * 111.0
SALL = S.copy()                                                  # all stations: used to locate UIC end stations
S = S[[len(i) > 0 for i in _t.query_ball_point(_q, r=0.3)]].copy()
print("ways", len(W), "stations within 300 m of a high-speed way", len(S))

# ---- graph per country from way node sequences ----
match_log, way_date, station_date = [], {}, {}
for cc, Wc in W.groupby("cc"):
    G = nx.Graph()
    node_xy = {}
    for w in Wc.itertuples():
        if w.railway != "rail":
            continue
        # node ids are not in the "out tags geom" output: connected ways share an OSM node, hence identical
        # coordinates, so rounded coordinates serve as node keys
        for k in range(len(w.geom) - 1):
            a = (round(w.geom[k][0], 7), round(w.geom[k][1], 7))
            b = (round(w.geom[k + 1][0], 7), round(w.geom[k + 1][1], 7))
            node_xy[a], node_xy[b] = w.geom[k], w.geom[k + 1]
            G.add_edge(a, b, km=hav(w.geom[k], w.geom[k + 1]), way=w.way_id)
    if G.number_of_nodes() == 0:
        continue
    ids = list(node_xy)
    xy = np.array([node_xy[i] for i in ids])
    # gaps where tracks through stations or junctions are not tagged highspeed: link dead ends to the nearest node
    # of a different way within 2 km (weight = 3 x distance)
    from scipy.spatial import cKDTree as _KD
    _xyk = np.column_stack([xy[:, 0] * 111.0, xy[:, 1] * 111.0 * np.cos(np.radians(xy[:, 0]))])
    _kd = _KD(_xyk)
    pos = {n: i for i, n in enumerate(ids)}
    dead = [n for n in G.nodes if G.degree(n) == 1]
    added = 0
    for n in dead:
        wn = next(iter(G[n].values()))["way"]
        dists, idxs = _kd.query(_xyk[pos[n]], k=12, distance_upper_bound=2.0)
        for dk, ik in zip(np.atleast_1d(dists), np.atleast_1d(idxs)):
            if not np.isfinite(dk) or ik >= len(ids):
                break
            m = ids[ik]
            if m == n or any(e["way"] == wn for e in G[m].values()):
                continue
            G.add_edge(n, m, km=3 * max(dk, 0.01), way=None)
            added += 1
            break
    Sc = SALL[SALL.cc == cc].copy()
    Sc["keys"] = [{norm(a) for a in (r.name, r.name_en, r.name_local) if norm(a)} for r in Sc.itertuples()]

    def snap(lat, lon, maxkm=10.0):
        d = np.hypot((xy[:, 0] - lat) * 111, (xy[:, 1] - lon) * 111 * math.cos(math.radians(lat)))
        i = d.argmin()
        return (ids[i], d[i]) if d[i] <= maxkm else (None, d[i])

    def _cands(k):
        exact = Sc[Sc["keys"].apply(lambda s: k in s)]
        if len(exact):
            return exact
        return Sc[Sc["keys"].apply(lambda s: any(k == x.split(" ")[0] or x.startswith(k + " ") or k.startswith(x + " ") for x in s))]

    def find_station(name):
        """among stations whose name matches (exact first, then partial; English exonyms tried too),
        take the one closest to the high-speed graph"""
        k = norm(name)
        if not k:
            return None
        for kk in [k] + ([norm(EXO[k])] if k in EXO else []):
            c = _cands(kk)
            if len(c):
                dd = [snap(r.lat, r.lon, maxkm=1e9)[1] for r in c.itertuples()]
                j = int(np.argmin(dd))
                return c.iloc[j] if dd[j] <= 10.0 else None
        return None

    pat = CMAP.get(cc, cc)
    U = UIC[UIC.country.str.upper().str.contains(pat, regex=True)]
    for u in U.itertuples():
        stops = [p.strip() for p in re.split(r"\s+-\s+|－", u.section) if p.strip()]
        stops = [p for p in stops if not (p.startswith("(") and p.endswith(")"))] or stops     # context stops in ()
        dt = u.date if pd.notna(u.date) else (pd.Timestamp(int(u.year), 7, 1) if pd.notna(u.year) else pd.NaT)
        prec = "day" if pd.notna(u.date) else "year"
        matched, path_km, ok = [], 0.0, True
        for s_ in stops:
            st = find_station(s_)
            if st is None:
                matched.append((s_, None))
                continue
            nid, dkm = snap(st.lat, st.lon)
            matched.append((s_, nid))
            if pd.notna(dt) and (st.node_id not in station_date or dt < station_date[st.node_id][0]):
                station_date[st.node_id] = (dt, "UIC endpoint")
        seq = [m[1] for m in matched if m[1] is not None]
        for a, b in zip(seq[:-1], seq[1:]):
            try:
                p = nx.shortest_path(G, a, b, weight="km")
            except Exception:
                ok = False
                continue
            for x, y in zip(p[:-1], p[1:]):
                e = G[x][y]
                wid = e["way"]
                if wid is None:
                    continue
                path_km += e["km"]
                if wid not in way_date or (pd.notna(dt) and dt < way_date[wid][0]):
                    way_date[wid] = (dt, prec, u.edition, u.section)
        match_log.append(dict(cc=cc, edition=u.edition, section=u.section, date=dt, precision=prec, uic_km=u.km,
                              stops=len(stops), stops_matched=len(seq), path_km=round(path_km, 1),
                              ok=ok and len(seq) == len(stops) and len(seq) >= 2))
    print(cc, "UIC sections", len(U), "fully matched", sum(1 for m in match_log if m["cc"] == cc and m["ok"]), flush=True)

L = pd.DataFrame(match_log)
L.to_csv("data/uic_match_log.csv", index=False)
W["uic_date"] = W.way_id.map(lambda w: way_date.get(w, (pd.NaT,))[0])
W["uic_prec"] = W.way_id.map(lambda w: way_date.get(w, (None, None))[1])
W["uic_section"] = W.way_id.map(lambda w: way_date.get(w, (None, None, None, None))[3])
W["osm_year_ok"] = W.osm_year.where(W.osm_year >= 1964)
W["open_date"] = W.uic_date
W["date_source"] = np.where(W.uic_date.notna(), "UIC", "none")
# China: OSM per-way start_date takes precedence over UIC paths. On trunk lines with well-documented opening years
# (Beijing-Guangzhou 2009/2012, Hefei-Fuzhou 2015, Hangzhou-Shenzhen 2009-2013, Guiyang-Guangzhou and Lanzhou-Xinjiang
# 2014) OSM matches and the UIC shortest paths do not: in a dense network the path between two UIC end stations runs
# over other lines. Elsewhere UIC first (JP/TW agreement > 99%).
W["osm_dt"] = [osm_date(r, y) if pd.notna(y) else pd.NaT for r, y in zip(W.osm_date_raw, W.osm_year_ok)]
cn_osm = (W.cc == "CN") & W.osm_dt.notna()
W.loc[cn_osm, "open_date"] = W.loc[cn_osm, "osm_dt"]
W.loc[cn_osm, "date_source"] = "OSM start_date (CN priority)"
fill = W.open_date.isna() & W.osm_dt.notna()
W.loc[fill, "open_date"] = W.loc[fill, "osm_dt"]
W.loc[fill, "date_source"] = "OSM start_date"
# UIC dates carried to OSM ways by line name where UIC lists lines rather than stations (FR, GB, NL)
X = pd.read_csv("data_external/primary/osm_name_crosswalk.csv", parse_dates=["date"])
W["mlat"] = W.geom.map(lambda g: float(np.mean([p[0] for p in g])))
W["mlon"] = W.geom.map(lambda g: float(np.mean([p[1] for p in g])))
for x in X.itertuples():
    m = (W.cc == x.cc) & W.name.str.contains(x.osm_name_regex, regex=True) & (W.date_source == "none")
    if isinstance(x.rule, str) and x.rule.strip():
        m &= W.eval(x.rule.replace("lat", "mlat").replace("lon", "mlon"))
    W.loc[m, "open_date"] = x.date
    W.loc[m, "date_source"] = "UIC via line name"
# parallel tracks: the path follows one track of a double-track line; an undated rail way with >= 80% of its vertices
# within 50 m of a UIC-dated way takes that date
from scipy.spatial import cKDTree as _KD2
_d = W[(W.date_source.isin(["UIC", "UIC via line name"])) & (W.railway == "rail")]
_pts, _dt = [], []
for w in _d.itertuples():
    for (la, lo) in w.geom:
        _pts.append((la * 111.0, lo * 111.0 * math.cos(math.radians(la))))
        _dt.append(w.open_date)
if _pts:
    _kd2 = _KD2(np.array(_pts))
    for i in W.index[(W.date_source == "none") & (W.railway == "rail")]:
        g = W.at[i, "geom"]
        q = np.array([(la * 111.0, lo * 111.0 * math.cos(math.radians(la))) for la, lo in g])
        dd, ii = _kd2.query(q, k=1, distance_upper_bound=0.05)
        ok = np.isfinite(dd)
        if ok.mean() >= 0.8:
            W.at[i, "open_date"] = min(_dt[j] for j in ii[ok])
            W.at[i, "date_source"] = "UIC (parallel track)"
W.drop(columns=["nodes"]).to_parquet("data/hsr_ways_dated.parquet", index=False)

# ---- stations: earliest dated rail way within 300 m ----
pts, pw = [], []
for w in W[(W.railway == "rail") & W.open_date.notna()].itertuples():
    for (la, lo) in w.geom:
        pts.append((la, lo * math.cos(math.radians(la))))
        pw.append((w.open_date, w.date_source, w.maxspeed, w.cc))
tree = cKDTree(np.array(pts) * 111.0)
rows = []
for s in S.itertuples():
    q = np.array([s.lat, s.lon * math.cos(math.radians(s.lat))]) * 111.0
    idx = tree.query_ball_point(q, r=0.3)
    if not idx:
        if s.node_id in station_date:
            rows.append(dict(cc=s.cc, node_id=s.node_id, name=s.name, name_en=s.name_en, lat=s.lat, lon=s.lon,
                             open_date=station_date[s.node_id][0], date_source=station_date[s.node_id][1]))
        continue
    best = min(idx, key=lambda i: pw[i][0])
    od, src = pw[best][0], pw[best][1]
    if s.node_id in station_date and station_date[s.node_id][0] < od:
        od, src = station_date[s.node_id]
    rows.append(dict(cc=s.cc, node_id=s.node_id, name=s.name, name_en=s.name_en, lat=s.lat, lon=s.lon,
                     open_date=od, date_source=src))
ST = pd.DataFrame(rows)
ST.to_csv("data/hsr_stations_dated.csv", index=False)
cov = S.groupby("cc").size().rename("stations_on_hsr").to_frame().join(ST.groupby("cc").size().rename("dated"))
cov["share_dated"] = cov.dated / cov.stations_on_hsr
cov.to_csv("data/station_date_coverage.csv")
print("dated stations", len(ST))
print(cov.round(2).to_string())
print(W.groupby(["cc", "date_source"]).km.sum().unstack().round(0).to_string())
