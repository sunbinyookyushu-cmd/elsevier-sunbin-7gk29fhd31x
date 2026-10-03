# -*- coding: utf-8 -*-
"""Summary statistics for the fuel-shock study. Output: _sumstats.csv"""
import numpy as np
import pandas as pd

rows = []
def add(panel, var, s, unit=""):
    s = pd.Series(s).dropna()
    rows.append(dict(panel=panel, variable=var, unit=unit, n=len(s), mean=s.mean(), sd=s.std(), p10=s.quantile(.1),
                     median=s.median(), p90=s.quantile(.9)))

# A. airports (baseline cross-section, 1996)
b = pd.read_csv("airport_base.csv")
b = b[b.GACI_96.notna() & (b.seats_96 > 0)]
add("A. Airports, 1996", "GACI 1996", b.GACI_96)
add("A. Airports, 1996", "Degree 1996", b.Degree_96)
add("A. Airports, 1996", "ln(1+betweenness) 1996", np.log1p(b.NorBetweenness_96))
add("A. Airports, 1996", "Departing seats 1996 (million)", b.seats_96 / 1e6)
add("A. Airports, 1996", "International seat share 1996", b.intl_share_96)
add("A. Airports, 1996", "Seat-weighted stage length 1996", b.stage_96, "km")
add("A. Airports, 1996", "Seats per departure 1996", b.gauge_96)
add("A. Airports, 1996", "CO2 per seat-km 1996", b.int_96 * 1000, "g")
hub = b[b.GACI_96 >= b.GACI_96.quantile(.9)]
spk = b[b.GACI_96 < b.GACI_96.quantile(.9)]
for nm, s in [("International seat share 1996", "intl_share_96"), ("Seat-weighted stage length 1996", "stage_96"),
              ("Seats per departure 1996", "gauge_96")]:
    add("A2. Top-decile GACI airports (hubs)", nm, hub[s])
    add("A3. Other airports", nm, spk[s])

# B. airport-month growth, 1997-2019
am = pd.read_parquet("airport_month.parquet", columns=["airport_iata", "t", "year", "ln_seats", "ln_co2", "ln_gauge", "ln_stage"])
am = am[am.airport_iata.isin(b.airport_iata)]
lag = am.copy()
lag["t"] += 12
am = am.merge(lag[["airport_iata", "t", "ln_seats", "ln_co2"]], on=["airport_iata", "t"], suffixes=("", "_m12"))
am = am[(am.year >= 1997) & (am.year <= 2019)]
add("B. Airport-months 1997-2019", "D12 ln seats", am.ln_seats - am.ln_seats_m12)
add("B. Airport-months 1997-2019", "D12 ln CO2", am.ln_co2 - am.ln_co2_m12)

# C. countries
c = pd.read_csv("country_year.csv")
c96 = c[(c.y == 1996) & c.gaci_cwm96.notna()]
add("C. Countries, 1996", "GACI cwm 1996", c96.gaci_cwm96)
add("C. Countries, 1996", "GACI max 1996", c96.gaci_max96)
add("C. Countries, 1996", "ln(1+mean betweenness) 1996", c96.ln_betw96)
add("C. Countries, 1996", "International seat share 1996", c96.intl_share96)
add("C. Countries, 1996", "Airport seat HHI 1996", c96.hhi96)
add("C. Countries, 1996", "Oil rents 1996-98 (% GDP)", c96.oilrent96)
cc = c[c.gaci_cwm96.notna() & (c.y >= 1997) & (c.y <= 2019)].sort_values(["c", "y"])
add("C. Country-years 1997-2019", "D ln seats", cc.groupby("c").ln_seats.diff())

# D. fuel series
f = pd.read_csv("fuel_monthly.csv")
fm = f[(f.year >= 1997) & (f.year <= 2019)]
add("D. Monthly series 1997-2019", "Jet fuel, US Gulf Coast (2019 $/gal)", fm.jet_real)
add("D. Monthly series 1997-2019", "D12 ln jet fuel (real)", fm.d12_lnjet)
add("D. Monthly series 1997-2019", "Kaenzig news shock (monthly)", fm.kz)
add("D. Monthly series 1997-2019", "BH supply shock x (-1) (monthly)", fm.bh_neg)
add("D. Monthly series 1997-2019", "Kaenzig shock, 12-month sum", fm.kz_s12)
add("D. Monthly series 1997-2019", "BH shock x (-1), 12-month sum", fm.bh_neg_s12)
ts = pd.DataFrame([dict(panel="E. Time-series first stage 1997-2019", variable=v, unit="corr",
                        n=fm[[x, z]].dropna().shape[0], mean=fm[[x, z]].corr().iloc[0, 1], sd=np.nan, p10=np.nan,
                        median=np.nan, p90=np.nan)
                   for v, x, z in [("corr(D12 ln P(t-3), Kaenzig 12m sum (t-3))", "d12_lnjet_l3", "kz_s12_l3"),
                                   ("corr(D12 ln P(t-3), BH 12m sum (t-3))", "d12_lnjet_l3", "bh_neg_s12_l3"),
                                   ("corr(D12 ln jet, D12 ln Brent)", "d12_lnjet", "d12_lnbrent")]])
out = pd.concat([pd.DataFrame(rows), ts], ignore_index=True)
out.to_csv("_sumstats.csv", index=False)
print(out.round(3).to_string(index=False))
