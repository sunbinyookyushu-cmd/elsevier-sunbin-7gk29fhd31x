# -*- coding: utf-8 -*-
"""Simple two-step resilience - oil shock regression.

Step 1 (per airport): D12 ln seats_it = c_i + beta_i D12 ln P_(t-3) + e_it   (OLS, Newey-West L = 12)
         beta_i = the airport's oil beta (how much its seat growth moves with jet fuel prices). Also a reduced-form
         beta on the Kaenzig and BH 12-month shock sums. Airports with >= 120 monthly observations in the window.
Step 2 (cross-section of airports): beta_i = a + b R_i (+ controls) + u_i, SE clustered by country.
         R_i = resilience index (z-score); b > 0: resilient airports cut seats less when fuel prices rise.
Windows and indices: pre2008 index (built from 1996-2007) with betas from 2008-2019 (predetermined);
full-sample index with betas from 1997-2019; raw (unshrunk) versions of both.
The common (world) response is in every beta, so it cancels across airports; this is the two-step analogue of the
interaction model with year-month FE in 31_resilience_fuel.py.
Output: _res_resil_simple.csv, resil_oil_betas.csv
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from _prep_airport import panel

am = panel()
R = pd.read_csv("resilience_airport.csv")
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
gw = g.pivot_table(index="Airport", columns="Year", values="GACI")
rows, betas = [], []
for win, (a, b) in {"2008-2019": (2008, 2019), "1997-2019": (1997, 2019)}.items():
    d = am[(am.year >= a) & (am.year <= b)].dropna(subset=["d12_ln_seats", "d12_lnjet_l3"])
    for ap, x in d.groupby("airport_iata"):
        if len(x) < 120:
            continue
        rec = dict(window=win, airport_iata=ap, iso3=x.iso3.iloc[0], region=x.Region_96.iloc[0], n_months=len(x))
        for nm, v in [("beta_price", "d12_lnjet_l3"), ("beta_kz", "kz_s12_l3"), ("beta_bh", "bh_neg_s12_l3")]:
            xx = x.dropna(subset=[v])
            o = sm.OLS(xx.d12_ln_seats, sm.add_constant(xx[v])).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
            rec[nm], rec[nm + "_se"] = o.params[v], o.bse[v]
        betas.append(rec)
B = pd.DataFrame(betas).merge(R, on="airport_iata", how="left")
B["lnG96"] = np.log(B.airport_iata.map(gw[1996]))
B["lnG07"] = np.log(B.airport_iata.map(gw[2007]))
B.to_csv("resil_oil_betas.csv", index=False)

SPECS = [("2008-2019", "R_pre2008", "resilience built 1996-2007 (EB-shrunk, paper definition)", "lnG07"),
         ("2008-2019", "R_raw_pre2008", "resilience built 1996-2007, before shrinkage", "lnG07"),
         ("1997-2019", "R_full", "full-sample resilience (8 crises, overlaps the fuel episodes)", "lnG96"),
         ("1997-2019", "R_raw_full", "full-sample resilience, before shrinkage", "lnG96")]
for win, rv, lab, gctl in SPECS:
    d = B[(B.window == win)].dropna(subset=[rv, gctl]).copy()
    # trim extreme betas (top/bottom 1%) to keep a few tiny airports from dominating
    for yv in ["beta_price", "beta_kz", "beta_bh"]:
        lo, hi = d[yv].quantile([0.01, 0.99])
        d = d[(d[yv] >= lo) & (d[yv] <= hi)] if yv == "beta_price" else d
    d["Rz"] = (d[rv] - d[rv].mean()) / d[rv].std()
    d["Gz"] = (d[gctl] - d[gctl].mean()) / d[gctl].std()
    cl = {"cov_type": "cluster", "cov_kwds": {"groups": pd.factorize(d.iso3)[0]}}
    for yv, ylab in [("beta_price", "oil beta (D12 ln P)"), ("beta_kz", "Kaenzig shock beta"), ("beta_bh", "BH shock beta")]:
        for spec, f in [("(1) resilience only", f"{yv} ~ Rz"), ("(2) + GACI", f"{yv} ~ Rz + Gz"),
                        ("(3) + GACI + region FE", f"{yv} ~ Rz + Gz + C(region)")]:
            m = smf.ols(f, d).fit(**cl)
            rows.append(dict(window=win, resilience=rv, resilience_label=lab, outcome=ylab, spec=spec, b=m.params["Rz"],
                             se=m.bse["Rz"], p=m.pvalues["Rz"], b_gaci=m.params.get("Gz", np.nan), se_gaci=m.bse.get("Gz", np.nan),
                             p_gaci=m.pvalues.get("Gz", np.nan), n=int(m.nobs), n_countries=d.iso3.nunique(),
                             mean_beta=d[yv].mean(), sd_beta=d[yv].std(), r2=m.rsquared))
out = pd.DataFrame(rows)
out.to_csv("_res_resil_simple.csv", index=False)
pd.set_option("display.width", 230)
print(out[out.outcome == "oil beta (D12 ln P)"][["window", "resilience", "spec", "b", "se", "p", "b_gaci", "p_gaci", "n", "mean_beta", "sd_beta"]].round(4).to_string(index=False))
print(out[out.outcome != "oil beta (D12 ln P)"][["resilience", "outcome", "spec", "b", "se", "p", "n"]].round(4).to_string(index=False))
