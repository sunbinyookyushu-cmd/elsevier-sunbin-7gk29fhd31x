"""Country reference table: ISO codes, capital, capital coordinates, borders, region.
Sources: mledoze/countries (names, capitals, borders), lutangar/cities.json (GeoNames-derived city coordinates).
Capital coordinates are needed to assign tax distance bands (UK APD: capital-city distance from London;
DE/SE/NO/FR bands: destination-country annexes that approximate distance from the taxing country).
Output: data/processed/country_capitals.csv
"""
import json, pandas as pd, pathlib, unicodedata
root = pathlib.Path(__file__).resolve().parents[1]
scr = pathlib.Path("/tmp/claude-0/-home-user-elsevier-sunbin-7gk29fhd31x/9250555c-d558-50dc-930d-cff0acde2e51/scratchpad/cities.json")
def norm(s): return unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode().lower().strip()
d = json.load(open(root/"data/raw/airports/mledoze_countries.json"))
cities = pd.DataFrame(json.load(open(scr)))  # name, lat, lng, country (ISO2)
cities["n"] = cities.name.map(norm)
rows = []
for c in d:
    cap = (c.get("capital") or [None])[0]
    lat = lon = None
    if cap:
        cand = cities[(cities.country==c["cca2"]) & (cities.n==norm(cap))]
        if cand.empty:  # try alternative spellings
            alts = {"Washington, D.C.":"Washington","Kingstown":"Kingstown","Sri Jayawardenepura Kotte":"Sri Jayewardenepura Kotte",
                    "Nay Pyi Taw":"Nay Pyi Taw","City of Victoria":"Victoria","Saint Helier":"Saint Helier","Saint-Denis":"Saint-Denis",
                    "Pago Pago":"Pago Pago","Tórshavn":"Torshavn","Nuku'alofa":"Nuku'alofa","Nuuk":"Nuuk","Papeetē":"Papeete","Nouméa":"Noumea",
                    "Vaduz":"Vaduz","Bern":"Bern","Kyiv":"Kyiv","Beijing":"Beijing","New Delhi":"New Delhi","Jerusalem":"Jerusalem",
                    "Rome":"Rome","Prague":"Prague","Vienna":"Vienna","Warsaw":"Warsaw","Lisbon":"Lisbon","Athens":"Athens","Moscow":"Moscow",
                    "Bucharest":"Bucharest","Copenhagen":"Copenhagen","Brussels":"Brussels","Luxembourg":"Luxembourg"}
            a = alts.get(cap, cap)
            cand = cities[(cities.country==c["cca2"]) & (cities.n.str.contains(norm(a).split(",")[0], regex=False))]
        if not cand.empty:
            lat, lon = float(cand.iloc[0].lat), float(cand.iloc[0].lng)
    rows.append({"iso2":c["cca2"],"iso3":c["cca3"],"country":c["name"]["common"],"capital":cap,"cap_lat":lat,"cap_lon":lon,
                 "centroid_lat":(c.get("latlng") or [None,None])[0],"centroid_lon":(c.get("latlng") or [None,None])[1],
                 "region":c.get("region"),"subregion":c.get("subregion"),"borders_iso3":";".join(c.get("borders",[])),
                 "landlocked":c.get("landlocked"),"independent":c.get("independent")})
df = pd.DataFrame(rows)
MANUAL = {"US":(38.8951,-77.0364),"MM":(19.7633,96.0785),"YE":(15.3694,44.1910),"TO":(-21.1393,-175.2049),"VU":(-17.7333,168.3167),
          "AG":(17.1175,-61.8456),"GD":(12.0564,-61.7485),"KI":(1.3278,172.9767),"SM":(43.9356,12.4473),"MO":(22.1987,113.5439),
          "GG":(49.4555,-2.5368),"EH":(27.1536,-13.2033),"IO":(-7.3195,72.4229),"TK":(-9.3800,-171.2200)}
for iso,(la,lo) in MANUAL.items():
    i = df.iso2==iso; df.loc[i & df.cap_lat.isna(), ["cap_lat","cap_lon"]] = [la,lo]
# fallback: centroid if capital not found
df["ref_lat"] = df.cap_lat.fillna(df.centroid_lat); df["ref_lon"] = df.cap_lon.fillna(df.centroid_lon)
df.to_csv(root/"data/processed/country_capitals.csv", index=False)
print(len(df), "countries;", df.cap_lat.notna().sum(), "capital coords found; missing:", df[df.cap_lat.isna()][["iso2","capital"]].values.tolist()[:40])
print(df[df.iso2.isin(["GB","DE","SE","FR","NL","NO","US","JP","KR","AU"])][["iso2","capital","cap_lat","cap_lon"]].to_string())
