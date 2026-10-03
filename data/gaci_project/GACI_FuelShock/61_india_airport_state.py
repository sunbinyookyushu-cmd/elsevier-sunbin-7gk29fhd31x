# -*- coding: utf-8 -*-
"""Indian airports in the OAG airport-month file -> state/UT, for the state ATF VAT design (user decision 2026-10-02).

State from OurAirports iso_region (data_external/india_atf_vat/sources/ourairports_airports_20261002.csv), with legacy
ISO 3166-2:IN codes mapped to current names. VAT jurisdiction can differ from today's state before a reorganisation:
  Telangana airports were in Andhra Pradesh until 2014-06-02; Ladakh (Leh, Kargil) was in Jammu & Kashmir until
  2019-10-31; Uttarakhand, Chhattisgarh and Jharkhand were split from UP, MP and Bihar in Nov 2000;
  Dadra & Nagar Haveli and Daman & Diu merged in Jan 2020.
These are recorded in `vat_state_before` / `vat_state_change` so the VAT panel can be assigned by date.
Output: data_external/india_atf_vat/india_airport_state_map.csv
"""
import io
import sys

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
D = "data_external/india_atf_vat/"
oa = pd.read_csv(D + "sources/ourairports_airports_20261002.csv", keep_default_na=False, na_values=[""])
oa = oa[(oa.iso_country == "IN") & oa.iata_code.notna()]
STATE = {"IN-AN": "Andaman & Nicobar Islands", "IN-AP": "Andhra Pradesh", "IN-AR": "Arunachal Pradesh", "IN-AS": "Assam",
         "IN-BR": "Bihar", "IN-CH": "Chandigarh", "IN-CT": "Chhattisgarh", "IN-CG": "Chhattisgarh",
         "IN-DD": "Dadra & Nagar Haveli and Daman & Diu", "IN-DN": "Dadra & Nagar Haveli and Daman & Diu",
         "IN-DH": "Dadra & Nagar Haveli and Daman & Diu", "IN-DL": "Delhi", "IN-GA": "Goa", "IN-GJ": "Gujarat",
         "IN-HP": "Himachal Pradesh", "IN-HR": "Haryana", "IN-JH": "Jharkhand", "IN-JK": "Jammu & Kashmir",
         "IN-KA": "Karnataka", "IN-KL": "Kerala", "IN-LA": "Ladakh", "IN-LD": "Lakshadweep", "IN-MH": "Maharashtra",
         "IN-MM": "Maharashtra",                                     # OurAirports uses IN-MM for Maharashtra
         "IN-ML": "Meghalaya", "IN-MN": "Manipur", "IN-MP": "Madhya Pradesh", "IN-MZ": "Mizoram", "IN-NL": "Nagaland",
         "IN-OR": "Odisha", "IN-OD": "Odisha", "IN-PB": "Punjab", "IN-PY": "Puducherry", "IN-RJ": "Rajasthan",
         "IN-SK": "Sikkim", "IN-TG": "Telangana", "IN-TS": "Telangana", "IN-TN": "Tamil Nadu", "IN-TR": "Tripura",
         "IN-UP": "Uttar Pradesh", "IN-UT": "Uttarakhand", "IN-UK": "Uttarakhand", "IN-UL": "Uttarakhand",
         "IN-WB": "West Bengal"}
oa["state"] = oa.iso_region.map(STATE)
m = oa.drop_duplicates("iata_code").set_index("iata_code")[["name", "municipality", "iso_region", "state", "type",
                                                             "latitude_deg", "longitude_deg"]]

am = pd.read_parquet("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "dep_seats", "dep_seats_dom"])
am = am[am.iso3 == "IND"]
s = am.groupby("airport_iata").agg(first_year=("year", "min"), last_year=("year", "max"))
for y in [1996, 2005, 2015, 2019]:
    s[f"seats_{y}"] = am[am.year == y].groupby("airport_iata").dep_seats.sum()
s["dom_share_2019"] = am[am.year == 2019].groupby("airport_iata").dep_seats_dom.sum() / s.seats_2019
b = pd.read_csv("airport_base.csv", usecols=["airport_iata", "GACI_96", "seats_96"]).set_index("airport_iata")
s["in_estimation_panel"] = (b.reindex(s.index).GACI_96.notna() & (b.reindex(s.index).seats_96 > 0)).astype(int)
out = s.join(m, how="left")
out["vat_state_before"] = np.where(out.state == "Telangana", "Andhra Pradesh",
                          np.where(out.state == "Ladakh", "Jammu & Kashmir", ""))
out["vat_state_change"] = np.where(out.state == "Telangana", "2014-06-02",
                          np.where(out.state == "Ladakh", "2019-10-31", ""))
out = out.reset_index().rename(columns={"index": "airport_iata"}).sort_values("seats_2019", ascending=False)
out.to_csv(D + "india_airport_state_map.csv", index=False)
print(f"Indian airports in the OAG file: {len(out)} | matched to a state: {int(out.state.notna().sum())} | "
      f"in estimation panel: {int(out.in_estimation_panel.sum())}")
print("unmatched:", out[out.state.isna()].airport_iata.tolist())
print("\nairports per state (estimation panel / all):")
g = out.groupby("state").agg(all=("airport_iata", "size"), panel=("in_estimation_panel", "sum"),
                             seats_2019_m=("seats_2019", lambda x: round(x.sum() / 1e6, 1)))
print(g.sort_values("seats_2019_m", ascending=False).to_string())
