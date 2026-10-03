# -*- coding: utf-8 -*-
"""Is the 2022-spike result driven by resilience or by the number of valid crises (which the empirical-Bayes
shrinkage builds into the composite)? Moderators: shrunk R, raw (unshrunk) R, n_valid; and shrunk R with
n_valid x period dummies. Recovery outcome, excl. mainland China, GACI 2019 x period, airport + country x month FE.
Output: _res_resil_shrink.csv"""
import numpy as np
import pandas as pd
from _est import fit

am = pd.read_parquet("airport_month.parquet")
am = am[am.iso3.notna()].copy()
R = pd.read_csv("resilience_airport.csv")
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
g19 = g[g.Year == 2019].set_index("Airport").GACI
ev = am[(am.ym >= "2021-01") & (am.ym <= "2024-06") & (am.iso3 != "CHN")].merge(R, on="airport_iata", how="inner")
ev = ev[ev.R_pre2020.notna()].copy()
r19 = am[am.year == 2019][["airport_iata", "month", "ln_seats"]]
ev = ev.merge(r19, on=["airport_iata", "month"], how="left", suffixes=("", "_19"))
ev["rec"] = ev.ln_seats - ev.ln_seats_19
ev["iso_ym"] = ev.iso3 + "_" + ev.ym
ev["gl"] = np.log(ev.airport_iata.map(g19))
ev = ev.dropna(subset=["rec", "gl"])
def z(v):
    c = ev.drop_duplicates("airport_iata")[v]
    return (ev[v] - c.mean()) / c.std()
SP = ((ev.ym >= "2022-03") & (ev.ym <= "2022-12")).astype(float)
AF = (ev.ym >= "2023-01").astype(float)
ev["Gz"] = z("gl")
ev["n2"] = (ev.n_valid_pre2020 >= 2).astype(float)
ev["n3"] = (ev.n_valid_pre2020 >= 3).astype(float)
base = ["g_sp", "g_af"]
ev["g_sp"], ev["g_af"] = ev.Gz * SP, ev.Gz * AF
rows = []
for lab, mod, extra in [("shrunk R (baseline)", "R_pre2020", []), ("raw R (no shrinkage)", "R_raw_pre2020", []),
                        ("n valid crises (count)", "n_valid_pre2020", []),
                        ("shrunk R + n_valid dummies x period", "R_pre2020", ["n2", "n3"]),
                        ("raw R + n_valid dummies x period", "R_raw_pre2020", ["n2", "n3"])]:
    d = ev.dropna(subset=[mod]).copy()
    c = d.drop_duplicates("airport_iata")[mod]
    d["Rz"] = (d[mod] - c.mean()) / c.std()
    d["x_sp"], d["x_af"] = d.Rz * SP.loc[d.index], d.Rz * AF.loc[d.index]
    ex = ["x_sp", "x_af"] + base
    for e in extra:
        d[e + "_sp"], d[e + "_af"] = d[e] * SP.loc[d.index], d[e] * AF.loc[d.index]
        ex += [e + "_sp", e + "_af"]
    r = fit(d, "rec", exog=ex, fes=["airport_iata", "iso_ym"], vc=("dk", "iso3", "t", 6), vc_alt=[("cl", "iso3")])
    for tm, nm in [("x_sp", "spike"), ("x_af", "after")] + [(e + "_sp", e + " x spike") for e in extra]:
        rows.append(dict(moderator=lab, term=nm, b=r["coef"][tm], se=r["se"][tm], p=r["p"][tm], n=r["n"], n_air=d.airport_iata.nunique()))
out = pd.DataFrame(rows)
out.to_csv("_res_resil_shrink.csv", index=False)
print(out.round(4).to_string(index=False))
c = ev.drop_duplicates("airport_iata")
print("corr(shrunk R, n_valid) = %.2f; corr(raw R, n_valid) = %.2f; corr(shrunk, raw) = %.2f"
      % (c.R_pre2020.corr(c.n_valid_pre2020), c.R_raw_pre2020.corr(c.n_valid_pre2020), c.R_pre2020.corr(c.R_raw_pre2020)))
