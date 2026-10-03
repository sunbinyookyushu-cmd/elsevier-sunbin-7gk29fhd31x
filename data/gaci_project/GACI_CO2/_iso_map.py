# -*- coding: utf-8 -*-
"""
_iso_map.py   (2026-09-08)  shared airport -> ISO3 assignment for 01 and 06.
Order of precedence:
  1. manual PATCH (closed airports, metro codes, known gaps)
  2. OurAirports iso_country (ISO2) -> ISO3 via iso2to3.json, completed with pycountry
     for ISO2 codes the json lacks (TW, RE, GP, MQ, GF, YT, JE, GG, CK, EH, BQ, ...)
  3. fallback: country name in airport_coords_merged.csv (OAG) -> ISO3 (alias table + pycountry)
Territories keep their own ISO3 (consistent with the GACI country panel, which carries
ASM, GUM, CYM, ... as separate units). Unassigned codes are returned as None and reported.
"""
import json, os
import pandas as pd
import pycountry

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"

PATCH = {"TXL": "DEU", "SXF": "DEU", "THF": "DEU", "SEL": "KOR",
         "ISG": "JPN", "KKJ": "JPN", "MLH": "FRA", "REP": "KHM", "TSE": "KAZ"}

ALIAS = {
    "Russia": "RUS", "Iran": "IRN", "Venezuela": "VEN", "Bolivia": "BOL", "Tanzania": "TZA",
    "Syria": "SYR", "Laos": "LAO", "Vietnam": "VNM", "South Korea": "KOR", "North Korea": "PRK",
    "Moldova": "MDA", "Democratic Republic of the Congo": "COD", "Congo (Kinshasa)": "COD",
    "Congo (Brazzaville)": "COG", "Republic of the Congo": "COG", "Ivory Coast": "CIV",
    "Cote d'Ivoire": "CIV", "Cape Verde": "CPV", "Brunei": "BRN", "Micronesia": "FSM",
    "Macedonia": "MKD", "North Macedonia": "MKD", "Czech Republic": "CZE", "Burma": "MMR",
    "Myanmar": "MMR", "East Timor": "TLS", "Palestine": "PSE", "Taiwan": "TWN", "Hong Kong": "HKG",
    "Macau": "MAC", "Turkey": "TUR", "United States": "USA", "United Kingdom": "GBR",
    "Swaziland": "SWZ", "Eswatini": "SWZ", "Reunion": "REU", "Netherlands Antilles": "ANT",
    "Western Sahara": "ESH", "Kyrgyzstan": "KGZ", "Cook Islands": "COK", "Kosovo": "XKX",
    "Vatican City": "VAT", "Saint Martin": "MAF", "Sint Maarten": "SXM", "Curacao": "CUW",
    "Bonaire": "BES", "Saint Barthelemy": "BLM", "Falkland Islands": "FLK", "Virgin Islands": "VIR",
    "U.S. Virgin Islands": "VIR", "British Virgin Islands": "VGB", "Wallis and Futuna": "WLF",
    "Saint Pierre and Miquelon": "SPM", "Norfolk Island": "NFK", "Christmas Island": "CXR",
    "Cocos (Keeling) Islands": "CCK", "Niue": "NIU", "Saint Helena": "SHN", "Montserrat": "MSR",
    "Anguilla": "AIA", "Isle of Man": "IMN", "Guernsey": "GGY", "Jersey": "JEY", "Mayotte": "MYT",
    "French Guiana": "GUF", "Guadeloupe": "GLP", "Martinique": "MTQ", "Aland Islands": "ALA",
}

def _name_to_iso3(name, cache={}):
    if name in cache:
        return cache[name]
    iso = ALIAS.get(name)
    if iso is None and isinstance(name, str) and name.strip():
        try:
            iso = pycountry.countries.lookup(name).alpha_3
        except LookupError:
            try:
                iso = pycountry.countries.search_fuzzy(name)[0].alpha_3
            except LookupError:
                iso = None
    cache[name] = iso
    return iso

def build():
    oa = pd.read_csv(os.path.join(GACI, "ourairports.csv"),
                     usecols=["type", "iso_country", "iata_code"], dtype=str, keep_default_na=False)
    oa = oa[oa.iata_code.str.len() == 3]
    rank = {"large_airport": 0, "medium_airport": 1, "small_airport": 2, "seaplane_base": 3,
            "heliport": 4, "closed": 5, "balloonport": 6}
    oa["rk"] = oa["type"].map(rank).fillna(9)
    oa = oa.sort_values(["iata_code", "rk"]).drop_duplicates("iata_code")
    iata2iso2 = dict(zip(oa.iata_code, oa.iso_country))
    iso2to3 = json.load(open(os.path.join(GACI, "iso2to3.json")))
    iso2to3 = dict(iso2to3)
    iso2to3.setdefault("XK", "XKX")
    for c in pycountry.countries:
        iso2to3.setdefault(c.alpha_2, c.alpha_3)
    co = pd.read_csv(os.path.join(GACI, "airport_coords_merged.csv"), usecols=["Airport", "country"], dtype=str)
    co = co.dropna(subset=["Airport"]).drop_duplicates("Airport")
    iata2name = dict(zip(co.Airport, co.country))
    stats = {"patch": 0, "ourairports": 0, "coords_name": 0, "none": 0}
    cache = {}
    def to_iso3(iata):
        if iata in cache:
            return cache[iata]
        if iata in PATCH:
            iso = PATCH[iata]; stats["patch"] += 1
        else:
            iso2 = iata2iso2.get(iata)
            iso = iso2to3.get(iso2) if iso2 else None
            if iso is not None and iso2 not in ("ZZ", "AQ"):
                stats["ourairports"] += 1
            else:
                iso = _name_to_iso3(iata2name.get(iata))
                if iso is not None:
                    stats["coords_name"] += 1
                else:
                    stats["none"] += 1
        cache[iata] = iso
        return iso
    return to_iso3, stats

if __name__ == "__main__":
    f, st = build()
    for a in ["TPE", "FRU", "KIV", "RUN", "PTP", "BON", "MTS", "SHO", "LAX", "PRN", "HKG", "AXA", "JER"]:
        print(a, f(a))
    print(st)
