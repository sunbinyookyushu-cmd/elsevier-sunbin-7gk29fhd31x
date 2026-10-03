"""Distance from each taxing country's reference point to every destination country's capital.

Why: European ticket taxes define bands either explicitly by capital-city distance (UK APD: London to the
destination's capital; 2,000 / 4,000 / 6,000 miles; 5,500 miles ultra-long-haul from 2023) or by country
annexes that were drawn up from distance to the taxing country (DE: Frankfurt; AT: Vienna; SE: Stockholm;
NO: Oslo; FR: Paris; NL 2008: 2,500 km rule; BE: 500 km rule). The table lets us (i) reproduce the UK bands
exactly, (ii) check the annex lists the tax agents compile, and (iii) build a continuous 'distance from
taxing country' variable for RD-style checks at band thresholds.
Output: data/processed/band_reference_distances.csv  (ref_country x dest_country, km, miles)
"""
import pandas as pd, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from geo_utils import haversine_km, km_to_miles
root = pathlib.Path(__file__).resolve().parents[1]
cap = pd.read_csv(root/"data/processed/country_capitals.csv")
REF = {"GB":("London",51.5074,-0.1278), "DE":("Frankfurt",50.1109,8.6821), "AT":("Vienna",48.2082,16.3738),
       "SE":("Stockholm",59.3293,18.0686), "NO":("Oslo",59.9139,10.7522), "FR":("Paris",48.8566,2.3522),
       "NL":("Amsterdam",52.3676,4.9041), "BE":("Brussels",50.8503,4.3517), "DK":("Copenhagen",55.6761,12.5683),
       "PT":("Lisbon",38.7223,-9.1393), "IE":("Dublin",53.3498,-6.2603), "IT":("Rome",41.9028,12.4964)}
rows = []
for ref,(city,la,lo) in REF.items():
    d = haversine_km(la, lo, cap.ref_lat, cap.ref_lon)
    rows.append(pd.DataFrame({"ref_iso2":ref,"ref_city":city,"dest_iso2":cap.iso2,"dest_country":cap.country,"dest_capital":cap.capital,
                              "dist_km":d.round(1),"dist_miles":km_to_miles(d).round(1)}))
out = pd.concat(rows)
# UK APD bands (statute miles, London -> destination capital)
def apd_band_2009(mi):  # 1 Nov 2009 - 31 Mar 2015
    return "A" if mi<=2000 else "B" if mi<=4000 else "C" if mi<=6000 else "D"
def apd_band_2015(mi):  # 1 Apr 2015 - 31 Mar 2023
    return "A" if mi<=2000 else "B"
def apd_band_2023(mi, dest):  # from 1 Apr 2023: domestic / A / B (<=5,500) / C (>5,500)
    return "DOM" if dest=="GB" else "A" if mi<=2000 else "B" if mi<=5500 else "C"
uk = out.ref_iso2=="GB"
out.loc[uk,"uk_apd_band_2009_2015"] = out.loc[uk,"dist_miles"].map(apd_band_2009)
out.loc[uk,"uk_apd_band_2015_2023"] = out.loc[uk,"dist_miles"].map(apd_band_2015)
out.loc[uk,"uk_apd_band_2023_"] = [apd_band_2023(m,d) for m,d in zip(out.loc[uk,"dist_miles"], out.loc[uk,"dest_iso2"])]
# Germany: statutory classes are by annex lists; the drafting rule was ~<=2,500 km / <=6,000 km from Frankfurt
de = out.ref_iso2=="DE"
out.loc[de,"de_class_rule"] = pd.cut(out.loc[de,"dist_km"], [0,2500,6000,99999], labels=["1","2","3"]).astype(str)
out.to_csv(root/"data/processed/band_reference_distances.csv", index=False)
print(out.groupby("ref_iso2").size().to_dict())
print(out[(out.ref_iso2=="GB")&(out.dest_iso2.isin(["US","AE","IN","CN","JP","AU","SG","EG","TR","CA","BR","ZA","TH","HK","AR"]))][["dest_country","dist_miles","uk_apd_band_2009_2015","uk_apd_band_2015_2023","uk_apd_band_2023_"]].sort_values("dist_miles").to_string(index=False))
