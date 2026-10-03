# -*- coding: utf-8 -*-
"""Replication check of the full-sample resilience index against Zhang, Cheung & Zhang (2027, TR-E):
Table 5 summary statistics and the inverse-U of Fig. 10 (R on GACI 2024 and its square, airports with
>= 5 observed years). Major hub (Section 5.1.1): >= 5 years with GACI >= 2.0, or top 200 in 2024, or
1996-2024 mean GACI in the top decile. Output: _res_resil_replication.csv"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

R = pd.read_csv("resilience_airport.csv").set_index("airport_iata")
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
gw = g.pivot_table(index="Airport", columns="Year", values="GACI")
hub = ((gw >= 2.0).sum(axis=1) >= 5) | (gw[2024].rank(ascending=False) <= 200) | (gw.mean(axis=1) >= gw.mean(axis=1).quantile(0.9))
d = R[["R_full", "n_valid_full", "n_years_full"]].join(hub.rename("hub")).join(gw[2024].rename("g24"))
d = d[d.R_full.notna()]
PAPER = {"All": (4058, .623, .084, .51, .616, .734), "Hub": (536, .674, .066, .582, .689, .748),
         "Non-hub": (3522, .616, .083, .499, .604, .728), "<3 crises": (2137, .564, .055, .479, .576, .626),
         ">=3 crises": (1921, .689, .057, .611, .69, .765), "<10 years": (431, .515, .06, .442, .509, .597),
         ">=10 years": (3627, .636, .076, .548, .63, .739)}
grp = {"All": d.index == d.index, "Hub": d.hub, "Non-hub": ~d.hub, "<3 crises": d.n_valid_full < 3,
       ">=3 crises": d.n_valid_full >= 3, "<10 years": d.n_years_full < 10, ">=10 years": d.n_years_full >= 10}
rows = []
for k, m in grp.items():
    s = d.loc[m, "R_full"]
    p = PAPER[k]
    rows.append(dict(section="Table 5", group=k, N=len(s), mean=s.mean(), sd=s.std(), p10=s.quantile(.1), p50=s.median(),
                     p90=s.quantile(.9), N_paper=p[0], mean_paper=p[1], sd_paper=p[2], p10_paper=p[3], p50_paper=p[4], p90_paper=p[5]))
q = d[(d.n_years_full >= 5) & d.g24.notna()]
X = sm.add_constant(np.column_stack([q.g24, q.g24 ** 2]))
o = sm.OLS(q.R_full.to_numpy(), X).fit(cov_type="HC1")
a1, a2 = o.params[1], o.params[2]
peak = -a1 / (2 * a2)
# delta-method SE of the peak
gr = np.array([0, -1 / (2 * a2), a1 / (2 * a2 ** 2)])
se_peak = float(np.sqrt(gr @ o.cov_params() @ gr))
rows.append(dict(section="Fig. 10 inverse-U", group="GACI 2024", N=len(q), mean=a1, sd=o.bse[1], p10=np.nan, p50=np.nan, p90=np.nan,
                 N_paper=3404, mean_paper=np.nan, sd_paper=np.nan))
rows.append(dict(section="Fig. 10 inverse-U", group="GACI 2024 squared", N=len(q), mean=a2, sd=o.bse[2], N_paper=3404))
rows.append(dict(section="Fig. 10 inverse-U", group="Peak (GACI)", N=len(q), mean=peak, sd=se_peak, N_paper=3404, mean_paper=1.85))
out = pd.DataFrame(rows)
out.to_csv("_res_resil_replication.csv", index=False)
print(out.round(3).to_string(index=False))
