"""For every GACI airport: distance (km) to the nearest commercial airport in each *other* country.

Used to build the cross-border leakage variable: an untaxed airport is a 'spillover' airport in year t if a
country that taxes in t has an airport within RING km (default 300). Precomputing airport x foreign-country
minimum distances keeps the Stata side to a simple merge. Only airports with >= MIN_SEATS seats in any year
and within Europe/neighbourhood (lat 30-72, lon -30..60) are considered as potential 'source' airports.
Output: data/processed/airport_nearest_foreign_country_km.csv (Airport, iso_country, foreign_iso, km)
"""
import pandas as pd, numpy as np, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from geo_utils import haversine_km
root = pathlib.Path(__file__).resolve().parents[1]
g = pd.read_csv(root/"data/processed/gaci_with_country.csv")
MIN_SEATS, MAXKM = 100_000, 1000
ap = g.groupby(["Airport","iso_country","lat","lon"], as_index=False).TotalCapacity.max()
eu = ap[(ap.lat.between(30,72)) & (ap.lon.between(-30,60)) & (ap.TotalCapacity>=MIN_SEATS)].reset_index(drop=True)
print("European-neighbourhood commercial airports:", len(eu))
la, lo = eu.lat.values, eu.lon.values
rows = []
for i, r in eu.iterrows():
    d = haversine_km(r.lat, r.lon, la, lo)
    df = pd.DataFrame({"foreign_iso": eu.iso_country.values, "km": d})
    df = df[(df.foreign_iso != r.iso_country) & (df.km <= MAXKM)]
    m = df.groupby("foreign_iso", as_index=False).km.min()
    m.insert(0, "iso_country", r.iso_country); m.insert(0, "Airport", r.Airport)
    rows.append(m)
out = pd.concat(rows); out["km"] = out.km.round(1)
out.to_csv(root/"data/processed/airport_nearest_foreign_country_km.csv", index=False)
print(len(out), "airport x foreign-country pairs within", MAXKM, "km")
print(out[out.Airport.isin(["NRN","BSL","CRL","MMX","BRU","DUS"])].sort_values(["Airport","km"]).groupby("Airport").head(3).to_string(index=False))
