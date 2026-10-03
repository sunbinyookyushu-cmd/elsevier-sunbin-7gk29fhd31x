# -*- coding: utf-8 -*-
"""Event designs around three jet-fuel episodes (airport x month).

  2022 spike : pre 2021-01..2022-02 | spike 2022-03..2022-12 | after 2023-01..2024-06 ; position = GACI 2019
  2014 crash : pre 2013-01..2014-09 | transition 2014-10..2014-12 | low 2015-01..2016-12 ; position = GACI 2013
  2008 spike : pre 2006-01..2007-09 | spike 2007-10..2008-09 | crash+GFC 2008-10..2009-12 ; position = GACI 2007
Outcome: ln seats, and for 2022 also the recovery ratio ln seats_t - ln seats_(same month 2019).
  y_it = a_(i x calendar month) + d_(country x month) + sum_k b_k (H_i x Period_k) [+ intl_i x month] + e
Country x month FE absorb national demand, COVID rules and border reopening; within-country hubs
are compared with spokes. H_i = z-score of the airport's GACI in the base year (airports with
traffic in the base year). Event-study version: H_i x month dummies; with airport x calendar-month
FE the reference is the full 12-month window ending in the last pre month (each coefficient is then
relative to the same calendar month of that window); for the recovery ratio (airport FE) it is the
last pre month.
Variance: country cluster + Newey-West over months, L=6.
Output: _res_events.csv, _res_eventstudy.csv
"""
import numpy as np
import pandas as pd
from _est import fit

am = pd.read_parquet("airport_month.parquet")
am = am[am.iso3.notna()].copy()
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
f = pd.read_csv("fuel_monthly.csv")
f["t"] = (f.ym.str[:4].astype(int) - 1996) * 12 + f.ym.str[5:7].astype(int) - 1

EV = {
    "2022 spike": dict(base=2019, start="2021-01", end="2024-06", ref="2022-02",
                       periods={"spike (2022-03..12)": ("2022-03", "2022-12"), "after (2023-01..2024-06)": ("2023-01", "2024-06")}),
    "2014 crash": dict(base=2013, start="2013-01", end="2016-12", ref="2014-09",
                       periods={"transition (2014-10..12)": ("2014-10", "2014-12"), "low (2015-01..2016-12)": ("2015-01", "2016-12")}),
    "2008 spike": dict(base=2007, start="2006-01", end="2009-12", ref="2007-09",
                       periods={"spike (2007-10..2008-09)": ("2007-10", "2008-09"), "crash+GFC (2008-10..2009-12)": ("2008-10", "2009-12")}),
}
VC = ("dk", "iso3", "t", 6)
ALT = [("cl", "iso3"), ("cl2", "iso3", "t")]
rows, es = [], []

for ev, spec in EV.items():
    by = spec["base"]
    pos = g[g.Year == by].set_index("Airport").GACI
    yb = am[am.year == by].groupby("airport_iata").agg(seats_b=("dep_seats", "sum"), intl_b=("dep_seats_intl", "sum"))
    yb["intl_share_b"] = yb.intl_b / yb.seats_b
    base = yb[yb.seats_b > 0].join(pos.rename("gaci_b"), how="inner")
    base["H"] = (base.gaci_b - base.gaci_b.mean()) / base.gaci_b.std()
    d = am[(am.ym >= spec["start"]) & (am.ym <= spec["end"])].merge(base[["H", "intl_share_b"]], left_on="airport_iata",
                                                                     right_index=True, how="inner")
    d["apt_m"] = d.airport_iata + "_" + d.month.astype(str)
    d["iso_ym"] = d.iso3 + "_" + d.ym
    if ev == "2022 spike":
        r19 = am[am.year == 2019][["airport_iata", "month", "ln_seats", "ln_seats_dom", "ln_seats_intl"]]
        d = d.merge(r19, on=["airport_iata", "month"], how="left", suffixes=("", "_19"))
        d["rec"] = d.ln_seats - d.ln_seats_19
        d["rec_dom"] = d.ln_seats_dom - d.ln_seats_dom_19
    ex = []
    for lab, (a, b) in spec["periods"].items():
        nm = "x_" + str(len(ex))
        d[nm] = d.H * ((d.ym >= a) & (d.ym <= b))
        ex.append(nm)
    # intl share x month interactions (absorb differential reopening / long-haul seasonality)
    d["intl_ym"] = d.ym
    outs = ["ln_seats", "ln_seats_dom", "ln_seats_intl"] + (["rec", "rec_dom"] if ev == "2022 spike" else [])
    for y in outs:
        for fe_lab, fes, extra in [("apt x cal-month + country x month", ["apt_m", "iso_ym"], []),
                                   ("+ intl share(base) x month", ["apt_m", "iso_ym"], "intl"),
                                   ("apt x cal-month + month (no country FE)", ["apt_m", "ym"], [])]:
            dd = d.dropna(subset=[y, "H"]).copy()
            exog, part = list(ex), []
            if extra == "intl":
                dm = pd.get_dummies(dd.ym, prefix="im", drop_first=True).astype(float)
                dm = dm.mul(dd.intl_share_b.fillna(0).to_numpy(), axis=0)
                dd = pd.concat([dd, dm], axis=1)
                part = list(dm.columns)
            fes_ = fes if y not in ("rec", "rec_dom") else [("airport_iata" if fe == "apt_m" else fe) for fe in fes]
            r = fit(dd, y, exog=exog, fes=fes_, vc=VC, vc_alt=ALT, partial=part)
            for k, lab in enumerate(spec["periods"]):
                nm = ex[k]
                rows.append(dict(event=ev, outcome=y, fe=fe_lab, period=lab, b=r["coef"][nm], se=r["se"][nm], p=r["p"][nm],
                                 se_cl=r["alt"][0]["se"][nm], p_cl=r["alt"][0]["p"][nm], se_2w=r["alt"][1]["se"][nm],
                                 p_2w=r["alt"][1]["p"][nm], n=r["n"], G=r["G"], n_air=dd.airport_iata.nunique(),
                                 ymean=r["ymean"]))
        # continuous price version inside the window: ln P_(t-3) x H
        dd = d.dropna(subset=[y, "H"]).merge(f[["ym", "lnjet_l3"]], on="ym", how="left")
        dd["xp"] = dd.lnjet_l3 * dd.H
        fes_ = ["apt_m", "iso_ym"] if y not in ("rec", "rec_dom") else ["airport_iata", "iso_ym"]
        r = fit(dd, y, exog=["xp"], fes=fes_, vc=VC, vc_alt=ALT)
        rows.append(dict(event=ev, outcome=y, fe="apt x cal-month + country x month", period="continuous: ln P(t-3) x H",
                         b=r["coef"]["xp"], se=r["se"]["xp"], p=r["p"]["xp"], se_cl=r["alt"][0]["se"]["xp"],
                         p_cl=r["alt"][0]["p"]["xp"], se_2w=r["alt"][1]["se"]["xp"], p_2w=r["alt"][1]["p"]["xp"],
                         n=r["n"], G=r["G"], n_air=dd.airport_iata.nunique(), ymean=r["ymean"]))
    # event study, ln seats (and rec for 2022)
    for y in ["ln_seats"] + (["rec", "ln_seats_dom"] if ev == "2022 spike" else []):
        dd = d.dropna(subset=[y, "H"]).copy()
        months = sorted(dd.ym.unique())
        refy = pd.period_range(end=spec["ref"], periods=12, freq="M").astype(str).tolist()
        refset = set(refy) if y != "rec" else {spec["ref"]}
        exs = []
        for m_ in months:
            if m_ in refset:
                continue
            nm = "e_" + m_.replace("-", "_")
            dd[nm] = dd.H * (dd.ym == m_)
            exs.append(nm)
        fes_ = ["apt_m", "iso_ym"] if y not in ("rec",) else ["airport_iata", "iso_ym"]
        r = fit(dd, y, exog=exs, fes=fes_, vc=VC, vc_alt=ALT)
        for m_ in months:
            nm = "e_" + m_.replace("-", "_")
            es.append(dict(event=ev, outcome=y, ym=m_, b=r["coef"].get(nm, 0.0), se=r["se"].get(nm, 0.0),
                           p=r["p"].get(nm, np.nan), se_cl=r["alt"][0]["se"].get(nm, 0.0),
                           ref=(refy[0] + ".." + refy[-1]) if y != "rec" else spec["ref"]))
    print(ev, "done")

res = pd.DataFrame(rows)
res.to_csv("_res_events.csv", index=False)
pd.DataFrame(es).to_csv("_res_eventstudy.csv", index=False)
pd.set_option("display.width", 250)
print(res[res.fe == "apt x cal-month + country x month"][["event", "outcome", "period", "b", "se", "p", "p_cl", "n", "n_air"]].round(4).to_string(index=False))
