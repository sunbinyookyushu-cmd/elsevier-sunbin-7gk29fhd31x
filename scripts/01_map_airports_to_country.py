"""Map GACI airport IATA codes to ISO country, coordinates, and names.

Sources: OurAirports (primary), OpenFlights (fallback). Output:
  data/processed/airport_country_map.csv  (one row per IATA code in GACI panel)
  data/processed/gaci_with_country.csv    (GACI panel + iso_country, lat, lon)
"""
import pandas as pd, numpy as np, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
gaci = pd.read_csv(root/"data/raw/gaci/GACI1996_2024_panel.csv", encoding="utf-8-sig")
oa = pd.read_csv(root/"data/raw/airports/ourairports_airports.csv", low_memory=False, keep_default_na=False, na_values=[""])  # "NA" = Namibia
of = pd.read_csv(root/"data/raw/airports/openflights_airports.dat", header=None,
                 names=["of_id","name","city","country","iata","icao","lat","lon","alt","tz","dst","tzdb","type","source"],
                 na_values=["\\N"])
codes = pd.DataFrame({"Airport": sorted(gaci.Airport.unique())})

# OurAirports: prefer scheduled_service=yes and larger types when IATA duplicated
rank = {"large_airport":0,"medium_airport":1,"small_airport":2,"seaplane_base":3,"heliport":4,"closed":5,"balloonport":6}
oa = oa[oa.iata_code.notna()].copy()
oa["r"] = oa.type.map(rank).fillna(9) + np.where(oa.scheduled_service=="yes",0,0.5)
oa = oa.sort_values("r").drop_duplicates("iata_code")
m = codes.merge(oa[["iata_code","name","municipality","iso_country","iso_region","latitude_deg","longitude_deg","type","icao_code"]],
                left_on="Airport", right_on="iata_code", how="left").drop(columns="iata_code")
m = m.rename(columns={"latitude_deg":"lat","longitude_deg":"lon","type":"oa_type","icao_code":"icao"})
m["source"] = m.iso_country.notna().map({True: "ourairports", False: None})

# Fallback: OpenFlights (country name -> ISO via OurAirports countries table)
cty = pd.read_csv(root/"data/raw/airports/ourairports_countries.csv", keep_default_na=False, na_values=[""])[["code","name"]].rename(columns={"code":"iso","name":"cname"})
of = of[of.iata.notna()].drop_duplicates("iata").merge(cty, left_on="country", right_on="cname", how="left")
fix = {"United States":"US","United Kingdom":"GB","Russia":"RU","South Korea":"KR","North Korea":"KP","Iran":"IR","Syria":"SY",
       "Laos":"LA","Vietnam":"VN","Taiwan":"TW","Czech Republic":"CZ","Macau":"MO","Hong Kong":"HK","Congo (Kinshasa)":"CD",
       "Congo (Brazzaville)":"CG","Cote d'Ivoire":"CI","Burma":"MM","Tanzania":"TZ","Bolivia":"BO","Venezuela":"VE","Moldova":"MD",
       "Brunei":"BN","Cape Verde":"CV","Micronesia":"FM","Macedonia":"MK","Swaziland":"SZ","East Timor":"TL","Netherlands Antilles":"AN",
       "Virgin Islands":"VI","British Virgin Islands":"VG","Saint Vincent and the Grenadines":"VC","Saint Kitts and Nevis":"KN",
       "Saint Lucia":"LC","Antigua and Barbuda":"AG","Trinidad and Tobago":"TT","Falkland Islands":"FK","Reunion":"RE",
       "Wallis and Futuna":"WF","Western Sahara":"EH","Palestine":"PS","Vatican City":"VA","Sao Tome and Principe":"ST",
       "Johnston Atoll":"UM","Midway Islands":"UM","Wake Island":"UM","Myanmar":"MM","Svalbard":"SJ","Cocos (Keeling) Islands":"CC",
       "Saint Pierre and Miquelon":"PM","Saint Helena":"SH","South Georgia and the Islands":"GS","Turks and Caicos Islands":"TC",
       "Northern Mariana Islands":"MP","Guinea-Bissau":"GW","Faroe Islands":"FO","Christmas Island":"CX","Norfolk Island":"NF",
       "French Polynesia":"PF","New Caledonia":"NC","Isle of Man":"IM","Guernsey":"GG","Jersey":"JE","Gibraltar":"GI","Bermuda":"BM",
       "Cayman Islands":"KY","Aruba":"AW","Curacao":"CW","Sint Maarten":"SX","Greenland":"GL","Puerto Rico":"PR","Guam":"GU",
       "American Samoa":"AS","Anguilla":"AI","Montserrat":"MS","Mayotte":"YT","Martinique":"MQ","Guadeloupe":"GP","French Guiana":"GF",
       "Cook Islands":"CK","Niue":"NU","Tokelau":"TK","Kosovo":"XK","Eswatini":"SZ","North Macedonia":"MK","Czechia":"CZ"}
of["iso"] = of["iso"].fillna(of.country.map(fix))
need = m.iso_country.isna()
f = m.loc[need, ["Airport"]].merge(of[["iata","name","city","iso","lat","lon","icao"]], left_on="Airport", right_on="iata", how="left")
m.loc[need, ["name","municipality","iso_country","lat","lon","icao"]] = f[["name","city","iso","lat","lon","icao"]].values
m.loc[need & m.iso_country.notna(), "source"] = "openflights"

# Manual overrides: metro codes, retired codes, codes absent from both sources
manual = {"SEL":("KR",37.5583,126.7906,"Seoul (metro code; Gimpo)"), "MLH":("FR",47.5896,7.5299,"Mulhouse (EuroAirport, FR side of BSL)"),
          "BAK":("AZ",40.4675,50.0467,"Baku (metro code)"), "ZGC":("CN",36.5152,103.6203,"Lanzhou (retired code)"),
          "TIS":("AU",-10.5864,142.2900,"Thursday Island / Horn Island"), "JRS":("IL",31.8647,35.2192,"Jerusalem Atarot (closed 2001)"),
          "CAS":("MA",33.3675,-7.5899,"Casablanca (metro code)"), "HHA":("CN",28.1892,113.2196,"Changsha Huanghua (retired code)"),
          "YDI":("CA",55.9000,-60.9000,"Davis Inlet"), "UCA":("US",43.1451,-75.3839,"Utica Oneida County"),
          "TSO":("GB",49.9456,-6.3314,"Tresco Heliport"), "PLB":("US",44.6872,-73.5247,"Plattsburgh Clinton County (old)"),
          "JCA":("FR",43.5528,7.0217,"Cannes Croisette Heliport"), "PUM":("ID",-4.1800,121.6180,"Pomala"),
          "QNS":("BR",-30.0331,-51.2300,"Porto Alegre bus/metro code"), "SZD":("GB",53.3942,-1.3886,"Sheffield City (closed 2008)"),
          "XHQ":("BR",-22.7556,-43.4517,"Rio metro code"), "SGS":("PH",6.0586,125.0962,"Sanga-Sanga")}
for k,(iso,lat,lon,nm) in manual.items():
    i = m.Airport==k
    if i.any() and m.loc[i,"iso_country"].isna().all():
        m.loc[i,["iso_country","lat","lon","name","source"]] = [iso,lat,lon,nm,"manual"]
m.to_csv(root/"data/processed/airport_country_map.csv", index=False)
out = gaci.merge(m[["Airport","iso_country","lat","lon","name"]], on="Airport", how="left")
out.to_csv(root/"data/processed/gaci_with_country.csv", index=False)

# Report
n = len(m); matched = m.iso_country.notna().sum()
print(f"GACI airports: {n}; matched: {matched} ({matched/n:.1%}); ourairports {(m.source=='ourairports').sum()}, openflights {(m.source=='openflights').sum()}, manual {(m.source=='manual').sum()}")
obs = len(out); print(f"GACI airport-years: {obs}; with country: {out.iso_country.notna().sum()} ({out.iso_country.notna().mean():.1%})")
cap = out.groupby(out.iso_country.notna()).TotalCapacity.sum(); print("Share of seat capacity matched:", round(cap.get(True,0)/cap.sum(),4))
un = out[out.iso_country.isna()].groupby("Airport").agg(years=("Year","nunique"), cap=("TotalCapacity","sum")).sort_values("cap", ascending=False)
print("\nUnmatched airports (top 25 by capacity):"); print(un.head(25).to_string())
print("\nCountries:", out.iso_country.nunique(), "| top 10 by 2024 capacity:")
print(out[out.Year==2024].groupby("iso_country").TotalCapacity.sum().nlargest(10).round(0).to_string())
