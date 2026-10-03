# -*- coding: utf-8 -*-
"""Local projections: dynamic hub-spoke response to an oil supply shock (airport x month, 1997-2019).

  ln y_(i,t+h) - ln y_(i,t-1) = a_i + d_t + b_h (s_t x H_i) + e,   h = 0..24
  s_t = Kaenzig news shock or sign-flipped BH supply shock, scaled to one standard deviation
  (1997-2019); H_i = z-score of 1996 GACI. Only t + h <= 2019-12 is used (no Covid months).
Price response for scaling: ln P_(t+h) - ln P_(t-1) = c + g_h s_t (time series, Newey-West L = h+1).
Implied differential elasticity at horizon h = b_h / g_h.
Variance for b_h: country cluster + Newey-West over months, L = max(h+1, 6).
Output: _res_lp.csv
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from _est import fit

am = pd.read_parquet("airport_month.parquet", columns=["airport_iata", "iso3", "t", "year", "ym", "ln_seats", "ln_co2"])
b = pd.read_csv("airport_base.csv")
b = b[b.GACI_96.notna() & (b.seats_96 > 0)]
b["H_g"] = (b.GACI_96 - b.GACI_96.mean()) / b.GACI_96.std()
am = am[am.iso3.notna()].merge(b[["airport_iata", "H_g"]], on="airport_iata", how="inner")
f = pd.read_csv("fuel_monthly.csv")
f["t"] = (f.ym.str[:4].astype(int) - 1996) * 12 + f.ym.str[5:7].astype(int) - 1
sd = f[(f.year >= 1997) & (f.year <= 2019)][["kz", "bh_neg"]].std()
f["s_kz"] = f.kz / sd.kz
f["s_bh"] = f.bh_neg / sd.bh_neg
am = am.merge(f[["t", "s_kz", "s_bh"]], on="t", how="left")
wide = {v: am.pivot_table(index="airport_iata", columns="t", values=v) for v in ["ln_seats", "ln_co2"]}
T_END = (2019 - 1996) * 12 + 11

rows = []
ts = f.set_index("t")
for h in range(0, 25):
    for y in ["ln_seats", "ln_co2"]:
        W = wide[y]
        lead = W.shift(-h, axis=1)
        prev = W.shift(1, axis=1)
        dy = (lead - prev).stack().rename("dy").reset_index()
        d = am[["airport_iata", "iso3", "t", "ym", "H_g", "s_kz", "s_bh"]].merge(dy, on=["airport_iata", "t"], how="inner")
        d = d[(d.t >= 12) & (d.t + h <= T_END)]
        for s in ["s_kz", "s_bh"]:
            d["x"] = d[s] * d.H_g
            r = fit(d, "dy", exog=["x"], fes=["airport_iata", "ym"], vc=("dk", "iso3", "t", max(h + 1, 6)), vc_alt=[("cl", "iso3")])
            # aggregate price response
            p = ts.lnjet.shift(-h) - ts.lnjet.shift(1)
            q = pd.DataFrame({"dp": p, "s": ts[s]}).loc[12:T_END - h].dropna()
            o = sm.OLS(q.dp, sm.add_constant(q.s)).fit(cov_type="HAC", cov_kwds={"maxlags": h + 1})
            rows.append(dict(h=h, outcome=y, shock=s, b=r["coef"]["x"], se=r["se"]["x"], p=r["p"]["x"],
                             se_cl=r["alt"][0]["se"]["x"], n=r["n"], g_price=o.params["s"], se_price=o.bse["s"],
                             implied_elast=r["coef"]["x"] / o.params["s"]))
    print("h", h, "done")
res = pd.DataFrame(rows)
res.to_csv("_res_lp.csv", index=False)
print(res[res.outcome == "ln_seats"].round(4).to_string(index=False))
