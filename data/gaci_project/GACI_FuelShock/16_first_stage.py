# -*- coding: utf-8 -*-
"""First stages for the baseline samples (airport-month D12 spec; country-year FD spec).
  (D ln P x H) = a + d + pi (D K x H) + e, same FE as the second stage.
Reports pi and its SE, and the Kleibergen-Paap Wald F under the three variance options.
Output: _res_first_stage.csv
"""
import numpy as np
import pandas as pd
from _est import fit

rows = []
def rec(level, H, shock, r, sample, n_units):
    for i, a in enumerate([dict(vc=r["vc"], se=r["se"], p=r["p"], G=r["G"])] + r["alt"]):
        F = (r["coef"]["zz"] / a["se"]["zz"]) ** 2
        rows.append(dict(level=level, position=H, shock=shock, sample=sample, vc=str(a["vc"]), pi=r["coef"]["zz"],
                         se=a["se"]["zz"], p=a["p"]["zz"], F=F, G=a["G"], n=r["n"], n_units=n_units))

# airport-month
am = pd.read_parquet("airport_month.parquet", columns=["airport_iata", "iso3", "t", "year", "month", "ym", "ln_seats"])
b = pd.read_csv("airport_base.csv")
b = b[b.GACI_96.notna() & (b.seats_96 > 0)].copy()
b["H_g"] = (b.GACI_96 - b.GACI_96.mean()) / b.GACI_96.std()
b["Hub10"] = (b.GACI_96 >= b.GACI_96.quantile(0.9)).astype(float)
b["H_b"] = np.log1p(b.NorBetweenness_96)
b["H_b"] = (b.H_b - b.H_b.mean()) / b.H_b.std()
am = am[am.iso3.notna()].merge(b[["airport_iata", "H_g", "Hub10", "H_b"]], on="airport_iata")
lag = am[["airport_iata", "t", "ln_seats"]].copy()
lag["t"] += 12
am = am.merge(lag, on=["airport_iata", "t"], suffixes=("", "_m12"))
am["d12"] = am.ln_seats - am.ln_seats_m12
f = pd.read_csv("fuel_monthly.csv")
am = am.merge(f[["ym", "d12_lnjet_l3", "kz_s12_l3", "bh_neg_s12_l3"]], on="ym", how="left")
A = am[(am.year >= 1997) & (am.year <= 2019)].dropna(subset=["d12"]).copy()
for H in ["H_g", "Hub10", "H_b"]:
    for s in ["kz_s12_l3", "bh_neg_s12_l3"]:
        A["x"] = A.d12_lnjet_l3 * A[H]
        A["zz"] = A[s] * A[H]
        r = fit(A, "x", exog=["zz"], fes=["airport_iata", "ym"], vc=("dk", "iso3", "t", 12),
                vc_alt=[("cl", "iso3"), ("cl2", "iso3", "year")])
        r["vc"] = ("dk", "iso3", "t", 12)
        rec("airport-month", H, s, r, "1997-2019, D12 ln seats observed", A.airport_iata.nunique())

# country-year
c = pd.read_csv("country_year.csv").sort_values(["c", "y"])
c = c[c.gaci_cwm96.notna()].copy()
base = c.drop_duplicates("c")
for H, v in [("H_cwm", "gaci_cwm96"), ("H_betw", "ln_betw96"), ("H_max", "gaci_max96")]:
    c[H] = (c[v] - base[v].mean()) / base[v].std()
c["dls"] = c.groupby("c").ln_seats.diff()
c.loc[c.groupby("c").y.diff() != 1, "dls"] = np.nan
c["t"] = c.y
C = c[(c.y >= 1997) & (c.y <= 2019)].dropna(subset=["dls"]).copy()
for H in ["H_cwm", "H_betw", "H_max"]:
    for s in ["d_kz_cum", "d_bh_neg_cum"]:
        C["x"] = C.d_lnjet * C[H]
        C["zz"] = C[s] * C[H]
        r = fit(C, "x", exog=["zz"], fes=["c", "y"], vc=("dk", "c", "t", 2), vc_alt=[("cl", "c"), ("cl2", "c", "t")])
        r["vc"] = ("dk", "c", "t", 2)
        rec("country-year", H, s, r, "1997-2019, D ln seats observed", C.c.nunique())

out = pd.DataFrame(rows)
out.to_csv("_res_first_stage.csv", index=False)
print(out.round(4).to_string(index=False))
