# -*- coding: utf-8 -*-
"""Does the inverse-U of Zhang et al. (2027) survive without the shrinkage-induced crisis-count component?
R (shrunk), raw R, and n_valid on GACI 2024 + square; and with n_valid dummies. Output: _res_resil_invU.csv"""
import numpy as np, pandas as pd, statsmodels.api as sm
R = pd.read_csv("resilience_airport.csv").set_index("airport_iata")
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
g24 = g[g.Year == 2024].set_index("Airport").GACI
q = R.join(g24.rename("g24"))
q = q[q.R_full.notna() & (q.n_years_full >= 5) & q.g24.notna()]
rows = []
for y, ctrl in [("R_full", False), ("R_raw_full", False), ("n_valid_full", False), ("R_full", True), ("R_raw_full", True),
                ("depth_full", False), ("speed_full", False), ("adapt_full", False)]:
    X = np.column_stack([q.g24, q.g24 ** 2])
    if ctrl:
        X = np.column_stack([X, pd.get_dummies(q.n_valid_full, drop_first=True).astype(float).to_numpy()])
    d = pd.DataFrame(X).assign(y=q[y].to_numpy()).dropna()
    o = sm.OLS(d.y.to_numpy(), sm.add_constant(d.drop(columns="y").to_numpy())).fit(cov_type="HC1")
    a1, a2 = o.params[1], o.params[2]
    rows.append(dict(outcome=y, n_valid_dummies=ctrl, a1=a1, se1=o.bse[1], a2=a2, se2=o.bse[2], p2=o.pvalues[2],
                     peak=-a1 / (2 * a2), n=int(o.nobs)))
out = pd.DataFrame(rows)
out.to_csv("_res_resil_invU.csv", index=False)
print(out.round(4).to_string(index=False))
