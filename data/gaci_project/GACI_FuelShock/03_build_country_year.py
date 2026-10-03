# -*- coding: utf-8 -*-
"""Country x year panel (1996-2023) for the fuel-shock x network-position study.

Base: ../GACI_CO2/gaci_co2_panel.csv (184 countries; GACI measures, OAG seats, flights, seat-km,
CO2 in the bunker convention). Added here:
  - within-country concentration of departing seats across airports (HHI, top-airport share,
    number of active airports) from airport_month.parquet
  - 1996 baseline position and characteristics (GACI cwm, GACI max, betweenness, degree,
    international seat share, stage length, oil rents, GDP pc, population, air market access)
Output: country_year.csv
"""
import json
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
cp = pd.read_csv(GACI + r"\GACI_CO2\gaci_co2_panel.csv")
fe = pd.read_csv(GACI + r"\gaci_panel_feyrer.csv", usecols=["c", "y", "ln_air_ma", "ln_sea_ma"])
cp = cp.merge(fe, on=["c", "y"], how="left")

am = pd.read_parquet("airport_month.parquet", columns=["airport_iata", "iso3", "year", "dep_seats"])
ay = am[am.year <= 2023].groupby(["iso3", "year", "airport_iata"]).dep_seats.sum().reset_index()
ay = ay[ay.dep_seats > 0]
ay["sh"] = ay.dep_seats / ay.groupby(["iso3", "year"]).dep_seats.transform("sum")
conc = ay.groupby(["iso3", "year"]).agg(hhi=("sh", lambda s: (s ** 2).sum()), top_share=("sh", "max"),
                                         n_apt=("sh", "size")).reset_index().rename(columns={"iso3": "c", "year": "y"})
cp = cp.merge(conc, on=["c", "y"], how="left")

cp["cont"] = cp.reg.str[:2]
cp["ln_seats"] = np.log(cp.dep_seats.where(cp.dep_seats > 0))
cp["ln_flights"] = np.log(cp.n_dep_flights.where(cp.n_dep_flights > 0))
cp["ln_skm"] = np.log(cp.dep_seat_km.where(cp.dep_seat_km > 0))
cp["ln_co2"] = np.log(cp.co2_bunker.where(cp.co2_bunker > 0))
cp["ln_gauge"] = cp.ln_seats - cp.ln_flights
cp["ln_stage"] = cp.ln_skm - cp.ln_seats
cp["ln_int"] = cp.ln_co2 - cp.ln_skm
cp["intl_share"] = cp.dep_seats_intl / cp.dep_seats
cp["ln_seats_intl"] = np.log(cp.dep_seats_intl.where(cp.dep_seats_intl > 0))
cp["ln_seats_dom"] = np.log((cp.dep_seats - cp.dep_seats_intl).where(cp.dep_seats - cp.dep_seats_intl > 0))
cp["ln_hhi"] = np.log(cp.hhi)
cp["ln_napt"] = np.log(cp.n_apt)
cp["ln_betw"] = np.log1p(cp.betw_mean)
cp["ln_betw_sum"] = np.log1p(cp.betw_sum)

wb = json.load(open("data_external/wb_oilrents.json"))[1]
oil = pd.DataFrame([(r["countryiso3code"], int(r["date"]), r["value"]) for r in wb if r["value"] is not None],
                   columns=["c", "y", "oilrent"])
oil96 = oil[(oil.y >= 1996) & (oil.y <= 1998)].groupby("c").oilrent.mean().rename("oilrent96")

b = cp[cp.y == 1996].set_index("c")
base = pd.DataFrame({
    "gaci_cwm96": b.gaci_cwmean, "gaci_max96": b.gaci_max, "ln_gaci_cwm96": b.ln_gaci_cwm,
    "ln_gaci_max96": b.ln_gaci_max, "ln_betw96": b.ln_betw, "ln_betw_sum96": b.ln_betw_sum,
    "deg_mean96": b.deg_mean, "eig_mean96": b.eig_mean, "ln_cap96": b.lnCap,
    "ln_seats96": b.ln_seats, "intl_share96": b.intl_share, "ln_stage96": b.ln_stage,
    "ln_gauge96": b.ln_gauge, "hhi96": b.hhi, "lnpc96": b.lnpc, "lnpop96": b.lnpop,
    "ln_airma96": b.ln_air_ma, "ln_seama96": b.ln_sea_ma}).join(oil96)
cp = cp.merge(base, left_on="c", right_index=True, how="left")
cp = cp.merge(pd.read_csv("fuel_annual.csv"), left_on="y", right_on="year", how="left")
cp.to_csv("country_year.csv", index=False)
print("country_year rows %d, countries %d, years %d-%d; countries with 1996 GACI %d"
      % (len(cp), cp.c.nunique(), cp.y.min(), cp.y.max(), base.gaci_cwm96.notna().sum()))
