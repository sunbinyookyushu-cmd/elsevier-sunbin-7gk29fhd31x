# -*- coding: utf-8 -*-
"""Check _est.fit against pyfixest on the country-year panel (OLS, 2SLS, weights, two-way FE)."""
import numpy as np
import pandas as pd
import pyfixest as pf
from _est import fit

c = pd.read_csv("country_year.csv")
c = c[(c.y <= 2019) & c.gaci_cwm96.notna()].copy()
c["H"] = (c.gaci_cwm96 - c.gaci_cwm96.mean()) / c.gaci_cwm96.std()
c = c.sort_values(["c", "y"])
c["dy"] = c.groupby("c").ln_seats.diff()
c["x"] = c.d_lnjet * c.H
c["z"] = c.d_kz_cum * c.H
c["wt"] = np.exp(c.ln_seats96)
d = c.dropna(subset=["dy", "x", "z", "wt"]).copy()

m = pf.feols("dy ~ x | c + y", data=d, vcov={"CRV1": "c"})
r = fit(d, "dy", exog=["x"], fes=["c", "y"], vc=("cl", "c"))
print("OLS   pyfixest b %.6f se %.6f | _est b %.6f se %.6f" % (m.coef()["x"], m.se()["x"], r["coef"]["x"], r["se"]["x"]))
m = pf.feols("dy ~ 1 | c + y | x ~ z", data=d, vcov={"CRV1": "c"})
r = fit(d, "dy", endog=["x"], instr=["z"], fes=["c", "y"], vc=("cl", "c"))
fs = pf.feols("x ~ z | c + y", data=d, vcov={"CRV1": "c"})
print("2SLS  pyfixest b %.6f se %.6f | _est b %.6f se %.6f" % (m.coef()["x"], m.se()["x"], r["coef"]["x"], r["se"]["x"]))
print("FS F  pyfixest t^2 %.3f | _est KP F %.3f" % ((fs.coef()["z"] / fs.se()["z"]) ** 2, r["fs"]["x"]["F"]))
m = pf.feols("dy ~ x | c + y", data=d, vcov={"CRV1": "c"}, weights="wt")
r = fit(d, "dy", exog=["x"], fes=["c", "y"], vc=("cl", "c"), weights="wt")
print("WLS   pyfixest b %.6f se %.6f | _est b %.6f se %.6f" % (m.coef()["x"], m.se()["x"], r["coef"]["x"], r["se"]["x"]))
m = pf.feols("dy ~ x | c + y", data=d, vcov={"CRV1": "c+y"})
r = fit(d, "dy", exog=["x"], fes=["c", "y"], vc=("cl2", "c", "y"))
print("2way  pyfixest b %.6f se %.6f | _est b %.6f se %.6f" % (m.coef()["x"], m.se()["x"], r["coef"]["x"], r["se"]["x"]))

# single aggregate shock: first stage and 2SLS under the three variance options
for vc in [("cl", "c"), ("cl2", "c", "y"), ("dk", "c", "y", 2)]:
    r = fit(d, "dy", endog=["x"], instr=["z"], fes=["c", "y"], vc=vc)
    print(vc, "2SLS b %.4f se %.4f  FS F %.1f" % (r["coef"]["x"], r["se"]["x"], r["fs"]["x"]["F"]))
# DK with L=0 must equal two-way (c, y) up to the small-sample factor
a = fit(d, "dy", exog=["x"], fes=["c", "y"], vc=("dk", "c", "y", 0))
b = fit(d, "dy", exog=["x"], fes=["c", "y"], vc=("cl2", "c", "y"))
print("dk L=0 se %.6f vs cl2 se %.6f" % (a["se"]["x"], b["se"]["x"]))
