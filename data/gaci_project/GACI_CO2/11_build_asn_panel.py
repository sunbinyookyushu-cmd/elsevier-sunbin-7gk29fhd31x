# -*- coding: utf-8 -*-
"""
11_build_asn_panel.py
Build country-year accident panel from ASN (Aviation Safety Network) wikibase
scrape: ASN_1996_raw.csv ... ASN_2024_raw.csv (from Downloads\ASN_data.zip).
Output: asn_country_year.csv with iso3 c, y and accident measures.
"""
import glob
import os
import re
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ASN_DIR = r"C:\Users\sunbi\AppData\Local\Temp\claude\C--Users-sunbi\95af7b89-074d-4528-b679-eb4bac771e4e\scratchpad\asn"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asn_country_year.csv")

import pycountry

ALIAS = {
    "Russia": "RUS", "Iran": "IRN", "Venezuela": "VEN", "Bolivia": "BOL",
    "Tanzania": "TZA", "Syria": "SYR", "Laos": "LAO", "Vietnam": "VNM",
    "South Korea": "KOR", "North Korea": "PRK", "Moldova": "MDA",
    "Democratic Republic of the Congo": "COD", "DR Congo": "COD",
    "Congo (Democratic Republic)": "COD", "Republic of the Congo": "COG",
    "Congo": "COG", "Ivory Coast": "CIV", "Cote d'Ivoire": "CIV",
    "Cape Verde": "CPV", "Brunei": "BRN", "Micronesia": "FSM",
    "Macedonia": "MKD", "North Macedonia": "MKD", "Czech Republic": "CZE",
    "Czechia": "CZE", "Slovak Republic": "SVK", "Burma": "MMR",
    "Myanmar": "MMR", "East Timor": "TLS", "Timor-Leste": "TLS",
    "Palestine": "PSE", "Palestinian Territory": "PSE", "Taiwan": "TWN",
    "Hong Kong": "HKG", "Macau": "MAC", "Macao": "MAC",
    "U.S. Virgin Islands": "VIR", "US Virgin Islands": "VIR",
    "British Virgin Islands": "VGB", "Falkland Islands": "FLK",
    "Netherlands Antilles": "ANT", "Curacao": "CUW", "Sint Maarten": "SXM",
    "Bonaire, Sint Eustatius and Saba": "BES", "Reunion": "REU",
    "Saint Kitts and Nevis": "KNA", "Saint Vincent and the Grenadines": "VCT",
    "Saint Lucia": "LCA", "Trinidad and Tobago": "TTO", "The Gambia": "GMB",
    "Gambia": "GMB", "Swaziland": "SWZ", "Eswatini": "SWZ",
    "Vatican City": "VAT", "Kosovo": "XKX", "Turkey": "TUR", "Türkiye": "TUR",
    "United States of America": "USA", "USA": "USA",
    "United Kingdom": "GBR", "U.K.": "GBR",
}

def to_iso3(name, cache={}):
    if name in cache:
        return cache[name]
    iso = None
    n = name.strip()
    if n in ALIAS:
        iso = ALIAS[n]
    else:
        try:
            iso = pycountry.countries.lookup(n).alpha_3
        except LookupError:
            try:
                m = pycountry.countries.search_fuzzy(n)
                iso = m[0].alpha_3 if m else None
            except LookupError:
                iso = None
    cache[name] = iso
    return iso

def parse_fat(s):
    m = re.search(r"Fatalities:\s*(\d+)", str(s))
    return int(m.group(1)) if m else 0

rows = []
unmapped = {}
for f in sorted(glob.glob(os.path.join(ASN_DIR, "ASN_*_raw.csv"))):
    year = int(re.search(r"ASN_(\d{4})_raw", f).group(1))
    d = pd.read_csv(f, encoding="utf-8-sig", keep_default_na=False)
    d["y"] = year
    # country = text after final " - " in Location
    d["country_raw"] = (d["Location"].astype(str).str.rsplit(" - ", n=1).str[-1]
                        .str.strip().str.lstrip("- ").str.strip()
                        .str.replace(r"^St\.", "Saint", regex=True))
    d["fat"] = d["Fatalities"].map(parse_fat)
    d["cat"] = d["Category"].astype(str)
    d["nature"] = d["Nature"].astype(str)
    rows.append(d[["y", "country_raw", "fat", "cat", "nature"]])

a = pd.concat(rows, ignore_index=True)
print("total events:", len(a))

# drop unlocatable (ocean, unknown)
bad_loc = a["country_raw"].str.contains(
    r"Ocean|Sea$|^Sea |Gulf|unknown|Unknown|^-$|^$|Atlantic|Pacific|Caribbean|Mediterranean|Channel|International",
    regex=True)
print("dropped no-country events:", int(bad_loc.sum()))
a = a[~bad_loc].copy()

a["c"] = a["country_raw"].map(to_iso3)
un = a[a["c"].isna()]["country_raw"].value_counts()
if len(un):
    print("UNMAPPED country names (dropped):")
    print(un.head(30).to_string())
a = a.dropna(subset=["c"])

# classify
a["accident"] = (a["cat"] == "Accident").astype(int)
a["fatal_acc"] = ((a["cat"] == "Accident") & (a["fat"] > 0)).astype(int)
a["major_acc"] = ((a["cat"] == "Accident") & (a["fat"] >= 30)).astype(int)
a["deaths"] = a["fat"] * (a["cat"] == "Accident")
com = a["nature"].str.contains("Passenger|Cargo", regex=True, na=False)
a["com_fatal"] = (com & (a["cat"] == "Accident") & (a["fat"] > 0)).astype(int)
a["com_deaths"] = a["fat"] * ((a["cat"] == "Accident") & com)

g = (a.groupby(["c", "y"])
       .agg(n_events=("accident", "size"),
            n_acc=("accident", "sum"),
            n_fatal=("fatal_acc", "sum"),
            n_major=("major_acc", "sum"),
            deaths=("deaths", "sum"),
            n_com_fatal=("com_fatal", "sum"),
            com_deaths=("com_deaths", "sum"))
       .reset_index())

# balance to full country-year grid of the GACI panel so zeros are real zeros
panel = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gaci_co2_panel.csv"),
                    usecols=["c", "y"])
grid = panel.drop_duplicates()
out = grid.merge(g, on=["c", "y"], how="left").fillna(0)
for col in out.columns[2:]:
    out[col] = out[col].astype(int)

out.to_csv(OUT, index=False)
print("saved:", OUT, out.shape)
print("\nmatched into GACI grid: nonzero country-years =", int((out["n_acc"] > 0).sum()),
      "of", len(out))
print("\nTop countries by total deaths:")
print(out.groupby("c")["deaths"].sum().sort_values(ascending=False).head(10).to_string())
print("\nWorld totals by year (accidents / fatal / major / deaths):")
print(out.groupby("y")[["n_acc", "n_fatal", "n_major", "deaths"]].sum().to_string())
