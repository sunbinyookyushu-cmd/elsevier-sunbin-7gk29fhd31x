# -*- coding: utf-8 -*-
"""Robustness of the 2022-spike result with pre-Covid resilience (31_resilience_fuel.py, RS5).
Checks: (a) drop mainland China (city lockdowns in 2022, e.g. Shanghai Apr-Jun; PVG/PEK have low resilience),
(b) drop China, Hong Kong, Macau, Taiwan, (c) placebo spike inside the pre-period (2021-07..2021-12 vs 2021-01..06),
(d) continuous ln P(t-3) x resilience within 2021-01..2024-06, (e) components of resilience.
All with airport (x calendar month) FE + country x month FE, GACI 2019 x period as control where stated.
Output: _res_resil_events_rob.csv, _res_resil_es_rob.csv"""
import numpy as np
import pandas as pd
from _est import fit

am = pd.read_parquet("airport_month.parquet")
am = am[am.iso3.notna()].copy()
R = pd.read_csv("resilience_airport.csv")
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
g19 = g[g.Year == 2019].set_index("Airport").GACI
f = pd.read_csv("fuel_monthly.csv")
ev = am[(am.ym >= "2021-01") & (am.ym <= "2024-06")].merge(R, on="airport_iata", how="inner")
ev = ev[ev.R_pre2020.notna()].copy()
r19 = am[am.year == 2019][["airport_iata", "month", "ln_seats", "ln_seats_dom"]]
ev = ev.merge(r19, on=["airport_iata", "month"], how="left", suffixes=("", "_19"))
ev["rec"] = ev.ln_seats - ev.ln_seats_19
ev["rec_dom"] = ev.ln_seats_dom - ev.ln_seats_dom_19
ev["iso_ym"] = ev.iso3 + "_" + ev.ym
ev = ev.merge(f[["ym", "lnjet_l3"]], on="ym", how="left")
ev["gl"] = np.log(ev.airport_iata.map(g19))

def z(d, v):
    c = d.drop_duplicates("airport_iata")[v]
    return (d[v] - c.mean()) / c.std()

SP = (ev.ym >= "2022-03") & (ev.ym <= "2022-12")
AF = ev.ym >= "2023-01"
rows, es = [], []

def run(label, d, y, mod="R_pre2020", gaci=True, periods=None):
    d = d.dropna(subset=[y, mod, "gl"]).copy()
    d["Rz"] = z(d, mod)
    d["Gz"] = z(d, "gl")
    per = periods or {"spike": ((d.ym >= "2022-03") & (d.ym <= "2022-12")), "after": (d.ym >= "2023-01")}
    ex = []
    for k, m in per.items():
        d["x_" + k] = d.Rz * m
        ex.append("x_" + k)
        if gaci:
            d["g_" + k] = d.Gz * m
            ex.append("g_" + k)
    r = fit(d, y, exog=ex, fes=["airport_iata", "iso_ym"], vc=("dk", "iso3", "t", 6), vc_alt=[("cl", "iso3")])
    for k in per:
        rows.append(dict(check=label, outcome=y, moderator=mod, gaci_control=gaci, term=k, b=r["coef"]["x_" + k],
                         se=r["se"]["x_" + k], p=r["p"]["x_" + k], se_cl=r["alt"][0]["se"]["x_" + k], n=r["n"],
                         n_air=d.airport_iata.nunique()))

CHN = ev.iso3 == "CHN"
GCH = ev.iso3.isin(["CHN", "HKG", "MAC", "TWN"])
for y in ["rec", "rec_dom"]:
    for gc in [False, True]:
        run("baseline", ev, y, gaci=gc)
        run("excl. mainland China", ev[~CHN], y, gaci=gc)
        run("excl. China, HK, Macau, Taiwan", ev[~GCH], y, gaci=gc)
    pre = ev[ev.ym <= "2022-02"]
    run("placebo: 2021-07..12 vs 2021-01..06 (pre-period only)", pre, y, gaci=True,
        periods={"placebo": (pre.ym >= "2021-07")})
    for comp in ["depth_pre2020", "speed_pre2020", "adapt_pre2020"]:
        run("component: " + comp.split("_")[0], ev[~CHN], y, mod=comp, gaci=True)
# continuous price within the window
for y in ["rec", "rec_dom"]:
    for lab, d in [("baseline", ev), ("excl. mainland China", ev[~CHN])]:
        d = d.dropna(subset=[y, "R_pre2020", "gl", "lnjet_l3"]).copy()
        d["Rz"] = z(d, "R_pre2020")
        d["Gz"] = z(d, "gl")
        d["xp"] = d.lnjet_l3 * d.Rz
        d["gp"] = d.lnjet_l3 * d.Gz
        r = fit(d, y, exog=["xp", "gp"], fes=["airport_iata", "iso_ym"], vc=("dk", "iso3", "t", 6), vc_alt=[("cl", "iso3")])
        rows.append(dict(check="continuous ln P(t-3) x R, " + lab, outcome=y, moderator="R_pre2020", gaci_control=True, term="lnP x R",
                         b=r["coef"]["xp"], se=r["se"]["xp"], p=r["p"]["xp"], se_cl=r["alt"][0]["se"]["xp"], n=r["n"],
                         n_air=d.airport_iata.nunique()))
# event study, excl. mainland China, with GACI x month control
d = ev[~CHN].dropna(subset=["rec", "R_pre2020", "gl"]).copy()
d["Rz"] = z(d, "R_pre2020")
d["Gz"] = z(d, "gl")
months = sorted(d.ym.unique())
ex = []
for m_ in months:
    if m_ == "2022-02":
        continue
    d["e_" + m_] = d.Rz * (d.ym == m_)
    d["g_" + m_] = d.Gz * (d.ym == m_)
    ex += ["e_" + m_]
part = ["g_" + m_ for m_ in months if m_ != "2022-02"]
r = fit(d, "rec", exog=ex, fes=["airport_iata", "iso_ym"], vc=("dk", "iso3", "t", 6), vc_alt=[("cl", "iso3")], partial=part)
for m_ in months:
    es.append(dict(ym=m_, b=r["coef"].get("e_" + m_, 0.0), se=r["se"].get("e_" + m_, 0.0), p=r["p"].get("e_" + m_, np.nan)))
pd.DataFrame(rows).to_csv("_res_resil_events_rob.csv", index=False)
pd.DataFrame(es).to_csv("_res_resil_es_rob.csv", index=False)
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).round(4).to_string(index=False))
print(" ".join(f"{x['ym'][2:]}:{x['b']:+.3f}{'*' if x['p'] < .1 else ''}" for x in es))
