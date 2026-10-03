# -*- coding: utf-8 -*-
"""Clean (predetermined) design: does resilience built from 1996-2007 predict how an airport's seat growth responds to
oil shocks in 2008-2019?

  beta_i (2008-2019, from 37_resil_simple_beta.py) = a + b R_i,1996-2007 + c ln GACI_2007 + d growth_1996-2007 + region FE
Everything on the right-hand side is measured before the test window, so the regressor cannot contain the outcome
(unlike the full-period index, whose adaptability part is 2004-2014 growth). Checks: crisis-count dummies (the
empirical-Bayes shrinkage makes the composite track the number of valid crises), unshrunk index, components.
Betas trimmed at the 1st/99th percentile; SE clustered by country.
Output: _res_resil_clean.csv
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

B = pd.read_csv("resil_oil_betas.csv")
d = B[B.window == "2008-2019"].dropna(subset=["R_pre2008", "R_raw_pre2008", "depth_pre2008", "speed_pre2008", "adapt_pre2008"]).copy()
for v in ["beta_price", "beta_kz", "beta_bh"]:
    lo, hi = d[v].quantile([0.01, 0.99])
    d = d[(d[v] >= lo) & (d[v] <= hi)]
cap = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv").pivot_table(index="Airport", columns="Year", values="TotalCapacity")
d["g9607"] = np.log(d.airport_iata.map(cap[2007]) / d.airport_iata.map(cap[1996]))
d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=["g9607", "lnG07"])
z = lambda s: (s - s.mean()) / s.std()
for c, n in [("R_pre2008", "R"), ("R_raw_pre2008", "Rraw"), ("depth_pre2008", "dep"), ("speed_pre2008", "spd"),
             ("adapt_pre2008", "adp"), ("g9607", "g"), ("lnG07", "G")]:
    d["z_" + n] = z(d[c])
cl = {"cov_type": "cluster", "cov_kwds": {"groups": pd.factorize(d.iso3)[0]}}
SPECS = [("(1) resilience + GACI", "z_R + z_G"), ("(2) + growth 1996-2007", "z_R + z_G + z_g"),
         ("(3) + crisis-count dummies", "z_R + z_G + z_g + C(n_valid_pre2008)"), ("(4) unshrunk index", "z_Rraw + z_G + z_g"),
         ("(5) components", "z_dep + z_spd + z_adp + z_G + z_g")]
rows = []
for y, lab in [("beta_kz", "Kaenzig supply-news shock"), ("beta_bh", "BH supply shock"), ("beta_price", "jet fuel price (supply + demand)")]:
    for sp, rhs in SPECS:
        m = smf.ols(f"{y} ~ {rhs} + C(region)", d).fit(**cl)
        for k in m.params.index:
            if k.startswith("z_") and k != "z_G":
                rows.append(dict(outcome=lab, spec=sp, term=k[2:], b=m.params[k], se=m.bse[k], p=m.pvalues[k], n=int(m.nobs),
                                 countries=d.iso3.nunique(), mean_beta=d[y].mean(), share_negative=(d[y] < 0).mean()))
out = pd.DataFrame(rows)
out.to_csv("_res_resil_clean.csv", index=False)
pd.set_option("display.width", 200)
print(out.round(4).to_string(index=False))
