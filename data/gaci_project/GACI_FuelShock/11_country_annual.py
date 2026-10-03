# -*- coding: utf-8 -*-
"""Country x year estimates: jet-fuel price x 1996 network position.

Baseline specification (first differences, 1997-2019):
  d ln y_ct = a_c + d_t + b (d ln P_t x H_c) + e_ct
  P_t = real US Gulf Coast jet fuel (annual mean, 2019 $); H_c = z-score of the 1996 position
  a_c absorbs country-specific growth trends; d_t absorbs the common response to the price.
Instruments for d ln P_t x H_c: d K_t x H_c, with K_t the annual mean of the cumulated monthly
  Kaenzig (2021) oil supply news shock, or of the cumulated (sign-flipped) Baumeister-Hamilton
  (2019) oil supply shock.
Variance: primary = country cluster + Newey-West over years (L=2) (Thompson 2011);
  also reported: country cluster; two-way (country, year).
Output: _res_country.csv
"""
import numpy as np
import pandas as pd
from _est import fit

c = pd.read_csv("country_year.csv").sort_values(["c", "y"])
c = c[c.gaci_cwm96.notna()].copy()
base = c.drop_duplicates("c")
def z(v):
    m, s = base[v].mean(), base[v].std()
    return (c[v] - m) / s
c["H_cwm"] = z("gaci_cwm96")
c["H_max"] = z("gaci_max96")
c["H_betw"] = z("ln_betw96")
c["H_air"] = z("ln_airma96")
for v in ["lnpc96", "lnpop96", "oilrent96", "intl_share96", "ln_stage96", "ln_seats96", "ln_gauge96", "hhi96"]:
    c["z_" + v] = z(v)
tq = base.gaci_cwm96.quantile([1 / 3, 2 / 3]).to_numpy()
c["T_mid"] = ((c.gaci_cwm96 > tq[0]) & (c.gaci_cwm96 <= tq[1])).astype(float)
c["T_top"] = (c.gaci_cwm96 > tq[1]).astype(float)

OUT = ["ln_seats", "ln_flights", "ln_skm", "ln_co2", "ln_gaci_cwm", "ln_gaci_max", "ln_hhi", "top_share",
       "ln_napt", "intl_share", "ln_gauge", "ln_stage", "ln_int", "ln_seats_intl", "ln_seats_dom"]
for v in OUT:
    c["d_" + v] = c.groupby("c")[v].diff()
    c.loc[c.groupby("c").y.diff() != 1, "d_" + v] = np.nan
c["d_lnjet_l1"] = c.groupby("c").d_lnjet.shift(1)
c["d_kz_cum_l1"] = c.groupby("c").d_kz_cum.shift(1)
c["d_bh_neg_cum_l1"] = c.groupby("c").d_bh_neg_cum.shift(1)
c["trend"] = c.y - 1996
c["t"] = c.y

VC = ("dk", "c", "t", 2)
ALT = [("cl", "c"), ("cl2", "c", "t")]
rows = []

def run(tab, panel, col, y, H, est, d, price="d_lnjet", shock=None, extra=(), extra_price=(), fes=("c", "y"),
        sample="1997-2019", spec="FD", note="", weights=None):
    """extra: interaction variables X (their price interaction enters as control, instrumented in 2SLS)."""
    d = d.copy()
    d["x"] = d[price] * d[H]
    endog, instr, exog = [], [], []
    ctrl = []
    for X in extra:
        d["x_" + X] = d[price] * d[X]
        ctrl.append("x_" + X)
    exog += list(extra_price)
    if est == "OLS":
        exog = ["x"] + ctrl + exog
    elif est == "RF":
        d["x"] = d[shock] * d[H]
        for X in extra:
            d["x_" + X] = d[shock] * d[X]
        exog = ["x"] + ctrl + exog
    else:
        d["zz"] = d[shock] * d[H]
        endog, instr = ["x"] + ctrl, ["zz"]
        for X in extra:
            d["zz_" + X] = d[shock] * d[X]
            instr.append("zz_" + X)
    r = fit(d, y, exog=exog, endog=endog, instr=instr, fes=list(fes), vc=VC, vc_alt=ALT, weights=weights)
    F = r["fs"].get("x", {}).get("F", np.nan) if endog else np.nan
    for term in ["x"] + ctrl + list(extra_price):
        if term not in r["coef"]:
            continue
        rows.append(dict(table=tab, panel=panel, col=col, outcome=y, position=H, estimator=est,
                         shock=shock or "", price=price, spec=spec, sample=sample, term=term,
                         b=r["coef"][term], se=r["se"][term], p=r["p"][term],
                         se_cl=r["alt"][0]["se"][term], p_cl=r["alt"][0]["p"][term],
                         se_2w=r["alt"][1]["se"][term], p_2w=r["alt"][1]["p"][term],
                         n=r["n"], G=r["G"], n_c=d.loc[d[y].notna(), "c"].nunique(), F=F,
                         F_cl=r["alt"][0]["F"].get("x", np.nan) if endog else np.nan,
                         F_2w=r["alt"][1]["F"].get("x", np.nan) if endog else np.nan,
                         r2w=r["r2_within"], ymean=r["ymean"], note=note))

S = c[(c.y >= 1997) & (c.y <= 2019)]
SH = {"KZ": "d_kz_cum", "BH": "d_bh_neg_cum"}

# ---- C1 main: traffic and position outcomes ----
for H in ["H_cwm", "H_betw", "H_max"]:
    for y in ["d_ln_seats", "d_ln_flights", "d_ln_skm", "d_ln_co2", "d_ln_gaci_cwm"]:
        run("C1", H, "OLS", y, H, "OLS", S)
        for k, s in SH.items():
            run("C1", H, "2SLS-" + k, y, H, "2SLS", S, shock=s)
            run("C1", H, "RF-" + k, y, H, "RF", S, shock=s)

# ---- C2 margins and network structure ----
for y in ["d_ln_gauge", "d_ln_stage", "d_ln_int", "d_intl_share", "d_ln_seats_intl", "d_ln_seats_dom",
          "d_ln_hhi", "d_top_share", "d_ln_napt", "d_ln_gaci_max"]:
    run("C2", "H_cwm", "OLS", y, "H_cwm", "OLS", S)
    for k, s in SH.items():
        run("C2", "H_cwm", "2SLS-" + k, y, "H_cwm", "2SLS", S, shock=s)

# ---- C3 horse race (d ln seats, d ln CO2) ----
sets = {"(1) position": [], "(2) + size": ["z_ln_seats96"], "(3) + intl, stage": ["z_intl_share96", "z_ln_stage96"],
        "(4) + income, pop": ["z_lnpc96", "z_lnpop96"], "(5) + oil rents": ["z_oilrent96"],
        "(6) all": ["z_ln_seats96", "z_intl_share96", "z_ln_stage96", "z_lnpc96", "z_lnpop96", "z_oilrent96"]}
for y in ["d_ln_seats", "d_ln_co2"]:
    for lab, ex in sets.items():
        SS = S.dropna(subset=["z_" + v for v in ["ln_seats96", "intl_share96", "ln_stage96", "lnpc96", "lnpop96", "oilrent96"]])
        run("C3", y, lab, y, "H_cwm", "OLS", SS, extra=ex, note="common sample")
        run("C3", y, lab, y, "H_cwm", "2SLS", SS, shock="d_bh_neg_cum", extra=ex, note="common sample; BH")

# ---- C4 dose (terciles of 1996 GACI cwm) ----
for y in ["d_ln_seats", "d_ln_co2", "d_ln_gaci_cwm"]:
    d = S.copy()
    d["x_mid"] = d.d_lnjet * d.T_mid
    d["x_top"] = d.d_lnjet * d.T_top
    r = fit(d, y, exog=["x_mid", "x_top"], fes=["c", "y"], vc=VC, vc_alt=ALT)
    for term in ["x_mid", "x_top"]:
        rows.append(dict(table="C4", panel="tercile", col="OLS", outcome=y, position="tercile(gaci_cwm96)",
                         estimator="OLS", shock="", price="d_lnjet", spec="FD", sample="1997-2019", term=term,
                         b=r["coef"][term], se=r["se"][term], p=r["p"][term], se_cl=r["alt"][0]["se"][term],
                         p_cl=r["alt"][0]["p"][term], se_2w=r["alt"][1]["se"][term], p_2w=r["alt"][1]["p"][term],
                         n=r["n"], G=r["G"], n_c=d.c.nunique(), F=np.nan, F_cl=np.nan, F_2w=np.nan,
                         r2w=r["r2_within"], ymean=r["ymean"], note="bottom tercile = reference"))

# ---- C5 robustness (d ln seats, H_cwm) ----
y = "d_ln_seats"
for est, s in [("OLS", None), ("2SLS", "d_bh_neg_cum"), ("2SLS", "d_kz_cum")]:
    col = est if s is None else est + ("-BH" if "bh" in s else "-KZ")
    run("C5", "lagged price", col, y, "H_cwm", est, S, price="d_lnjet_l1", shock=(s + "_l1") if s else None)
    run("C5", "Brent", col, y, "H_cwm", est, S, price="d_lnbrent", shock=s)
    run("C5", "incl. 2020-2023", col, y, "H_cwm", est, c[(c.y >= 1997) & (c.y <= 2023)], shock=s, sample="1997-2023")
    run("C5", "1997-2008", col, y, "H_cwm", est, c[(c.y >= 1997) & (c.y <= 2008)], shock=s, sample="1997-2008")
    run("C5", "2009-2019", col, y, "H_cwm", est, c[(c.y >= 2009) & (c.y <= 2019)], shock=s, sample="2009-2019")
    run("C5", "no country FE", col, y, "H_cwm", est, S, shock=s, fes=("y",))
    run("C5", "region x year FE", col, y, "H_cwm", est, S.assign(ry=S.reg + S.y.astype(str)), shock=s, fes=("c", "ry"))
    run("C5", "seat-weighted (1996)", col, y, "H_cwm", est, S.assign(w=np.exp(S.ln_seats96)), shock=s, weights="w")
    run("C5", "excl. USA", col, y, "H_cwm", est, S[S.c != "USA"], shock=s)
    run("C5", "excl. Middle East", col, y, "H_cwm", est, S[S.cont != "ME"], shock=s)
# crack spread (jet-specific refining margin) and levels specification
run("C5", "crack spread", "OLS", y, "H_cwm", "OLS", S, price="d_lncrack")
L = S.copy()
L["H_tr"] = L.H_cwm * L.trend
for est, s, col in [("OLS", None, "OLS"), ("2SLS", "bh_neg_cum", "2SLS-BH"), ("2SLS", "kz_cum", "2SLS-KZ")]:
    run("C5", "levels + H x trend", col, "ln_seats", "H_cwm", est, L.assign(ln_seats=L.ln_seats), price="lnjet",
        shock=s, extra_price=["H_tr"], spec="levels")

# ---- C6 position instrumented by 1996 air market access (Feyrer ingredient) ----
d = S.copy()
d["x"] = d.d_lnjet * d.H_cwm
d["zz"] = d.d_lnjet * d.H_air
for y in ["d_ln_seats", "d_ln_co2"]:
    r = fit(d, y, endog=["x"], instr=["zz"], fes=["c", "y"], vc=VC, vc_alt=ALT)
    rows.append(dict(table="C6", panel="position IV", col="2SLS (P x airMA96)", outcome=y, position="H_cwm",
                     estimator="2SLS", shock="d_lnjet x z(ln airMA96)", price="d_lnjet", spec="FD", sample="1997-2019",
                     term="x", b=r["coef"]["x"], se=r["se"]["x"], p=r["p"]["x"], se_cl=r["alt"][0]["se"]["x"],
                     p_cl=r["alt"][0]["p"]["x"], se_2w=r["alt"][1]["se"]["x"], p_2w=r["alt"][1]["p"]["x"], n=r["n"],
                     G=r["G"], n_c=d.c.nunique(), F=r["fs"]["x"]["F"], F_cl=r["alt"][0]["F"]["x"], F_2w=r["alt"][1]["F"]["x"],
                     r2w=np.nan, ymean=r["ymean"], note="cross-sectional corr(H_cwm, z airMA96) = %.2f" % base[["gaci_cwm96", "ln_airma96"]].corr().iloc[0, 1]))

res = pd.DataFrame(rows)
res.to_csv("_res_country.csv", index=False)
m = res[(res.table == "C1") & (res.position == "H_cwm")]
print(m[["outcome", "col", "b", "se", "p", "se_cl", "F", "F_cl", "n"]].round(4).to_string(index=False))
