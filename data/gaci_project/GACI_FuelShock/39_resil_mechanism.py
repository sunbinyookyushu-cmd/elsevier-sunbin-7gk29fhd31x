# -*- coding: utf-8 -*-
"""Mechanisms behind the clean result (38): airports with higher 1996-2007 resilience cut seats less after
supply-driven oil price rises (Kaenzig news shocks) in 2008-2019.

A. Margins of adjustment. For each airport, Kaenzig betas (2008-2019, 12-month sums lagged 3 months, HAC) of
   D12 ln departures, seats per departure (gauge), seat-weighted stage length, CO2 per seat-km, CO2, domestic seats,
   international seats. Each beta is regressed on resilience (z) + ln GACI 2007 + growth 1996-2007 + region FE.
   If resilient airports keep seats by flying fewer, larger aircraft, the departures beta falls and the gauge beta
   rises with resilience; if by trimming fuel per seat-km, the intensity beta falls.
B. Structure. The seats beta regressed on resilience plus 2007 characteristics (fuel per seat-km, gauge, stage length,
   destinations, international share, size, country income): does the resilience coefficient shrink?
Betas trimmed at the 1st/99th percentile per outcome; SE clustered by country.
Output: _res_resil_mech_margins.csv, _res_resil_mech_structure.csv, resil_kz_betas_margins.csv
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from _prep_airport import panel

OUTS = {"d12_ln_seats": "seats", "d12_ln_flights": "departures", "d12_ln_gauge": "seats per departure",
        "d12_ln_stage": "stage length", "d12_ln_int": "CO2 per seat-km", "d12_ln_co2": "CO2",
        "d12_ln_seats_dom": "domestic seats", "d12_ln_seats_intl": "international seats"}
am = panel()
A = am[(am.year >= 2008) & (am.year <= 2019)]
rows = []
for ap, x in A.groupby("airport_iata"):
    rec = dict(airport_iata=ap, iso3=x.iso3.iloc[0], region=x.Region_96.iloc[0])
    for y in OUTS:
        xx = x.dropna(subset=[y, "kz_s12_l3"])
        if len(xx) < 120:
            rec["b_" + y] = np.nan
            continue
        o = sm.OLS(xx[y], sm.add_constant(xx.kz_s12_l3)).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
        rec["b_" + y] = o.params["kz_s12_l3"]
    rows.append(rec)
K = pd.DataFrame(rows)
R = pd.read_csv("resilience_airport.csv")
K = K.merge(R[["airport_iata", "R_pre2008", "n_valid_pre2008"]], on="airport_iata", how="left")
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
gw = g.pivot_table(index="Airport", columns="Year", values="GACI")
cap = g.pivot_table(index="Airport", columns="Year", values="TotalCapacity")
deg = g.pivot_table(index="Airport", columns="Year", values="Degree")
K["lnG07"] = np.log(K.airport_iata.map(gw[2007]))
K["g9607"] = np.log(K.airport_iata.map(cap[2007]) / K.airport_iata.map(cap[1996]))
K["ln_deg07"] = np.log(K.airport_iata.map(deg[2007]))
# 2007 airport characteristics from the monthly file
m07 = pd.read_parquet("airport_month.parquet", columns=["airport_iata", "year", "dep_seats", "dep_seat_km", "co2_dep",
                                                        "n_dep_flights", "dep_seats_intl"])
m07 = m07[m07.year == 2007].groupby("airport_iata")[["dep_seats", "dep_seat_km", "co2_dep", "n_dep_flights", "dep_seats_intl"]].sum()
m07 = m07[(m07.dep_seats > 0) & (m07.dep_seat_km > 0) & (m07.n_dep_flights > 0)]
ch = pd.DataFrame({"ln_int07": np.log(m07.co2_dep / m07.dep_seat_km), "ln_gauge07": np.log(m07.dep_seats / m07.n_dep_flights),
                   "ln_stage07": np.log(m07.dep_seat_km / m07.dep_seats), "intl07": m07.dep_seats_intl / m07.dep_seats,
                   "ln_seats07": np.log(m07.dep_seats)})
K = K.join(ch, on="airport_iata")
cp = pd.read_csv(r"..\GACI_CO2\gaci_co2_panel.csv", usecols=["c", "y", "lnpc"])
K["lnpc07"] = K.iso3.map(cp[cp.y == 2007].set_index("c").lnpc)
K = K.replace([np.inf, -np.inf], np.nan)
K.to_csv("resil_kz_betas_margins.csv", index=False)

z = lambda s: (s - s.mean()) / s.std()
res = []
base = K.dropna(subset=["R_pre2008", "lnG07", "g9607", "b_d12_ln_seats"]).copy()
for y, lab in OUTS.items():
    d = base.dropna(subset=["b_" + y]).copy()
    lo, hi = d["b_" + y].quantile([0.01, 0.99])
    d = d[(d["b_" + y] >= lo) & (d["b_" + y] <= hi)]
    d["zR"], d["zG"], d["zg"] = z(d.R_pre2008), z(d.lnG07), z(d.g9607)
    m = smf.ols(f"Q('b_{y}') ~ zR + zG + zg + C(region)", d).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.iso3)[0]})
    res.append(dict(outcome=lab, b=m.params["zR"], se=m.bse["zR"], p=m.pvalues["zR"], n=int(m.nobs),
                    mean_beta=d["b_" + y].mean(), share_negative=(d["b_" + y] < 0).mean()))
M = pd.DataFrame(res)
M.to_csv("_res_resil_mech_margins.csv", index=False)

# B. structure
d = base.dropna(subset=["ln_int07", "ln_gauge07", "ln_stage07", "intl07", "ln_seats07", "ln_deg07", "lnpc07"]).copy()
lo, hi = d.b_d12_ln_seats.quantile([0.01, 0.99])
d = d[(d.b_d12_ln_seats >= lo) & (d.b_d12_ln_seats <= hi)]
for c in ["R_pre2008", "lnG07", "g9607", "ln_int07", "ln_gauge07", "ln_stage07", "intl07", "ln_seats07", "ln_deg07", "lnpc07"]:
    d["z_" + c] = z(d[c])
cl = {"cov_type": "cluster", "cov_kwds": {"groups": pd.factorize(d.iso3)[0]}}
st = []
for lab, extra in [("resilience only", ""), ("+ fuel per seat-km 2007", " + z_ln_int07"), ("+ gauge 2007", " + z_ln_gauge07"),
                   ("+ stage length 2007", " + z_ln_stage07"), ("+ destinations 2007", " + z_ln_deg07"),
                   ("+ intl share 2007", " + z_intl07"), ("+ size 2007", " + z_ln_seats07"), ("+ country income 2007", " + z_lnpc07"),
                   ("+ all", " + z_ln_int07 + z_ln_gauge07 + z_ln_stage07 + z_ln_deg07 + z_intl07 + z_ln_seats07 + z_lnpc07")]:
    m = smf.ols(f"b_d12_ln_seats ~ z_R_pre2008 + z_lnG07 + z_g9607{extra} + C(region)", d).fit(**cl)
    row = dict(spec=lab, b_R=m.params["z_R_pre2008"], se_R=m.bse["z_R_pre2008"], p_R=m.pvalues["z_R_pre2008"], n=int(m.nobs))
    for k in m.params.index:
        if k.startswith("z_") and k not in ("z_R_pre2008", "z_lnG07", "z_g9607"):
            row[k[2:]] = f"{m.params[k]:+.4f} (p {m.pvalues[k]:.3f})"
    st.append(row)
S = pd.DataFrame(st)
S.to_csv("_res_resil_mech_structure.csv", index=False)
pd.set_option("display.width", 250)
print(M.round(4).to_string(index=False))
print()
print(S.round(4).to_string(index=False))
