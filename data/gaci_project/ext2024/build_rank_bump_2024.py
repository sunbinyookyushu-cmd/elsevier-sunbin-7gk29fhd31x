# -*- coding: utf-8 -*-
"""Rank-bump data for the 2024 endpoint (_rank_bump_data.json, same schema as the 2023 file: r23 = end-year rank),
then a patched copy of the design generator (gen_slope_dc.py) -> _design_rankbump/FigureOnly.dc.html, then a
headless-Chrome render without the baked-in footnote -> GACI_rank_bump_rev.png (white background, 3x)."""
import json, re, pathlib, subprocess, sys
import pandas as pd
from PIL import Image, ImageChops
E = pathlib.Path(__file__).parent; G = E.parent
sys.path.insert(0, str(G))
YEARS = [1996, 2000, 2005, 2010, 2015, 2020, 2024]; END = 2024; TOPN = 15; SHOW = 20
src = (G / "build_ranking_fig_v2.py").read_text(encoding="utf-8")
ISO2NAME = eval(re.search(r"ISO2NAME = (\{.*?\})\n", src, re.S).group(1))
ISO2NAME.update({"IL": "Israel", "AE": "UAE"})

ap = pd.read_csv(E / "GACI1996_2024_new_panel_data.csv")
oa = pd.read_csv(E / "ourairports.csv", usecols=["iata_code", "iso_country", "type"]).dropna(subset=["iata_code"])
pref = {"large_airport": 0, "medium_airport": 1, "small_airport": 2}
oa["p"] = oa["type"].map(pref).fillna(3); oa = oa.sort_values("p").drop_duplicates("iata_code")
iso = dict(zip(oa["iata_code"], oa["iso_country"])); ap["cty"] = ap["Airport"].map(iso)
grp = (ap.dropna(subset=["cty"]).assign(wG=lambda d: d["TotalCapacity"] * d["GACI"])
         .groupby(["Year", "cty"], as_index=False).agg(wG=("wG", "sum"), cap=("TotalCapacity", "sum")))
grp["cwm"] = grp["wG"] / grp["cap"]
def ranks(df, idcol, vcol):
    return {y: {a: i + 1 for i, a in enumerate(df[df["Year"] == y].sort_values(vcol, ascending=False)[idcol])} for y in YEARS}
rk_ap = ranks(ap, "Airport", "GACI"); rk_co = ranks(grp, "cty", "cwm")
def entries(rk, labfun):
    top = sorted(rk[END], key=rk[END].get)[:TOPN]; out = []
    for e in top:
        r96 = rk[1996].get(e); series = [[y, rk[y].get(e)] for y in YEARS]
        out.append({"label": labfun(e), "r23": rk[END][e], "r96": r96, "riser": (r96 is None) or (r96 > SHOW), "series": series})
    return out
data = {"airports": entries(rk_ap, lambda a: a), "countries": entries(rk_co, lambda c: ISO2NAME.get(c, c))}
json.dump(data, open(E / "_rank_bump_data.json", "w", encoding="utf-8"), indent=1)
print("airports:", [(e["label"], e["r96"], e["r23"]) for e in data["airports"]])
print("countries:", [(e["label"], e["r96"], e["r23"]) for e in data["countries"]])
first_year = {e["label"]: next((y for y, r in e["series"] if r is not None), None) for e in data["airports"] if e["r96"] is None}
print("airports absent in 1996 -> first year in network:", first_year)

# patched generator
gen = (G / "_design_rankbump" / "gen_slope_dc.py").read_text(encoding="utf-8")
gen = re.sub(r'GACI = r"[^"]*"', lambda m: 'GACI = r"%s"' % str(E), gen).replace("2023", "2024").replace("Twenty-seven years", "Twenty-eight years")

(E / "_design_rankbump").mkdir(exist_ok=True)
(E / "_design_rankbump" / "gen_slope_dc_2024.py").write_text(gen, encoding="utf-8", newline="\n")
print("generator writes to:", re.findall(r'open\([^)]*\)', gen)[:4])
