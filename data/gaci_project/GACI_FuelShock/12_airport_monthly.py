# -*- coding: utf-8 -*-
"""Airport x month estimates: jet-fuel price x 1996 network position.

Baseline (12-month differences, 1997-01 to 2019-12, airports with a 1996 GACI position):
  D12 ln y_it = a_i + d_t + b (D12 ln P_{t-3} x H_i) + e_it
  P = real US Gulf Coast jet fuel (2019 $), lagged 3 months (schedules are set ahead);
  H_i = z-score of the airport's 1996 GACI; a_i absorbs airport-specific growth trends,
  d_t (year-month) absorbs the common response and seasonality of growth.
Instruments: rolling 12-month sums of the Kaenzig news shock / sign-flipped BH supply shock,
  lagged 3 months, times H_i (= D12 of the cumulated shock at t-3).
Variance: primary = country cluster + Newey-West over months, L=12 (Thompson 2011);
  also reported: country cluster; two-way (country, year).
Output: _res_airport.csv, _res_airport_lp.csv, _res_airport_bins.csv, _hubgap_series.csv
"""
import sys
import numpy as np
import pandas as pd
from _est import fit

ONLY = sys.argv[1].split(",") if len(sys.argv) > 1 else None     # e.g. "A3" re-runs one block and merges
def RUN(block):
    return ONLY is None or block in ONLY

am = pd.read_parquet("airport_month.parquet")
b = pd.read_csv("airport_base.csv")
b = b[b.GACI_96.notna() & (b.seats_96 > 0)].copy()
def zc(v):
    return (b[v] - b[v].mean()) / b[v].std()
b["H_g"] = zc("GACI_96")
b["Hub10"] = (b.GACI_96 >= b.GACI_96.quantile(0.9)).astype(float)
b["ln_betw96"] = np.log1p(b.NorBetweenness_96)
b["H_b"] = zc("ln_betw96")
b["ln_seats96"] = np.log(b.seats_96)
b["ln_stage96"] = np.log(b.stage_96)
b["ln_gauge96"] = np.log(b.gauge_96)
for v in ["ln_seats96", "intl_share_96", "ln_stage96", "ln_gauge96", "lnpc_c96", "oilrent_c96", "ln_airma96"]:
    b["z_" + v] = zc(v)
b["dec"] = pd.qcut(b.GACI_96.rank(method="first"), 10, labels=False) + 1
b["cont"] = b.Region_96.str[:2]
keep = ["airport_iata", "H_g", "Hub10", "H_b", "dec", "cont", "Region_96", "seats_96", "n_months_9619"] + [c for c in b.columns if c.startswith("z_")]
am = am[am.airport_iata.isin(b.airport_iata)].merge(b[keep], on="airport_iata", how="left")
am = am[am.iso3.notna()].copy()

OUT = ["ln_seats", "ln_flights", "ln_skm", "ln_co2", "ln_gauge", "ln_stage", "ln_int", "intl_share",
       "ln_seats_dom", "ln_seats_intl"]
lag = am[["airport_iata", "t"] + OUT].copy()
lag["t"] = lag.t + 12
am = am.merge(lag, on=["airport_iata", "t"], how="left", suffixes=("", "_m12"))
for v in OUT:
    am["d12_" + v] = am[v] - am[v + "_m12"]

f = pd.read_csv("fuel_monthly.csv")
f["year"] = f.ym.str[:4].astype(int)
f["month"] = f.ym.str[5:7].astype(int)
for s_ in ["kz", "bh_neg", "kz_pre"]:
    for L_ in [0, 9, 12]:
        f[f"{s_}_s12_l{L_}"] = f[s_ + "_s12"].shift(L_)
    f[f"{s_}_cum_l3"] = f[s_ + "_cum"].shift(3)
fcols = [c for c in f.columns if c.startswith(("d12_", "kz", "bh_neg", "lnjet", "lnbrent", "lncrack"))]
am = am.merge(f[["year", "month"] + fcols], on=["year", "month"], how="left")
am["reg_ym"] = am.Region_96 + "_" + am.ym
am["iso_ym"] = am.iso3 + "_" + am.ym

MAIN = am[(am.year >= 1997) & (am.year <= 2019)].copy()
print("baseline sample: rows with D12 ln seats %s, airports %d, countries %d"
      % (f"{MAIN.d12_ln_seats.notna().sum():,}", MAIN.loc[MAIN.d12_ln_seats.notna(), 'airport_iata'].nunique(),
         MAIN.loc[MAIN.d12_ln_seats.notna(), 'iso3'].nunique()))

VC = ("dk", "iso3", "t", 12)
ALT = [("cl", "iso3"), ("cl2", "iso3", "year")]
PR, SH = "d12_lnjet_l3", {"KZ": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
FE = ("airport_iata", "ym")
rows = []

def rec(tab, panel, col, y, H, est, shock, price, spec, sample, r, terms, endog, note="", n_air=None):
    for term in terms:
        if term not in r["coef"]:
            continue
        rows.append(dict(table=tab, panel=panel, col=col, outcome=y, position=H, estimator=est, shock=shock or "",
                         price=price, spec=spec, sample=sample, term=term, b=r["coef"][term], se=r["se"][term],
                         p=r["p"][term], se_cl=r["alt"][0]["se"][term], p_cl=r["alt"][0]["p"][term],
                         se_2w=r["alt"][1]["se"][term], p_2w=r["alt"][1]["p"][term], n=r["n"], G=r["G"],
                         n_air=n_air, F=r["fs"].get("x", {}).get("F", np.nan) if endog else np.nan,
                         F_cl=r["alt"][0]["F"].get("x", np.nan) if endog else np.nan,
                         F_2w=r["alt"][1]["F"].get("x", np.nan) if endog else np.nan,
                         r2w=r["r2_within"], ymean=r["ymean"], note=note))

def run(tab, panel, col, y, H, est, d, price=PR, shock=None, extra=(), extra_exog=(), fes=FE, sample="1997-2019",
        spec="D12", note="", weights=None, vc=VC, alt=ALT):
    cols = list(dict.fromkeys([y, price, H, "airport_iata", "iso3", "t", "year", "ym"] + list(fes) + list(extra) + list(extra_exog)
                              + ([shock] if shock else []) + ([weights] if weights else [])))
    d = d[cols].dropna().copy()
    d["x"] = d[price] * d[H]
    ctrl = []
    for X in extra:
        d["x_" + X] = d[price] * d[X]
        ctrl.append("x_" + X)
    endog, instr, exog = [], [], list(extra_exog)
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
    r = fit(d, y, exog=exog, endog=endog, instr=instr, fes=list(fes), vc=vc, vc_alt=alt, weights=weights)
    rec(tab, panel, col, y, H, est, shock, price, spec, sample, r, ["x"] + ctrl + list(extra_exog), endog, note,
        d.airport_iata.nunique())
    return r

# ---- A1 main ----
for H in (["H_g", "Hub10", "H_b"] if RUN("A1") else []):
    for y in ["d12_ln_seats", "d12_ln_flights", "d12_ln_skm", "d12_ln_co2"]:
        run("A1", H, "OLS", y, H, "OLS", MAIN)
        for k, s in SH.items():
            run("A1", H, "2SLS-" + k, y, H, "2SLS", MAIN, shock=s)
            run("A1", H, "RF-" + k, y, H, "RF", MAIN, shock=s)
    print("A1", H, "done")

# ---- A2 margins ----
for y in (["d12_ln_gauge", "d12_ln_stage", "d12_ln_int", "d12_intl_share", "d12_ln_seats_dom", "d12_ln_seats_intl"] if RUN("A2") else []):
    run("A2", "H_g", "OLS", y, "H_g", "OLS", MAIN)
    for k, s in SH.items():
        run("A2", "H_g", "2SLS-" + k, y, "H_g", "2SLS", MAIN, shock=s)
print("A2 done")

# ---- A3 horse race ----
allx = ["z_ln_seats96", "z_intl_share_96", "z_ln_stage96", "z_ln_gauge96", "z_lnpc_c96", "z_oilrent_c96"]
HS = MAIN.dropna(subset=allx)
sets = {"(1) position": [], "(2) + size": ["z_ln_seats96"], "(3) + intl, stage": ["z_intl_share_96", "z_ln_stage96"],
        "(4) + gauge": ["z_ln_gauge96"], "(5) + income, oil rents": ["z_lnpc_c96", "z_oilrent_c96"], "(6) all": allx}
aptx = ["z_ln_seats96", "z_intl_share_96", "z_ln_stage96", "z_ln_gauge96"]   # country-level terms are absorbed by country x month FE
for y in (["d12_ln_seats", "d12_ln_co2"] if RUN("A3") else []):
    for lab, ex in sets.items():
        run("A3", y, lab, y, "H_g", "OLS", HS, extra=ex, note="common sample")
        run("A3", y, lab, y, "H_g", "2SLS", HS, shock=SH["BH"], extra=ex, note="common sample; BH")
        run("A3", y, lab, y, "H_g", "2SLS", HS, shock=SH["KZ"], extra=ex, note="common sample; KZ")
    for k_, s_ in [("OLS", None), ("BH", SH["BH"]), ("KZ", SH["KZ"])]:
        run("A3", y, "(7) airport-level + country x month FE", y, "H_g", "OLS" if s_ is None else "2SLS", HS, shock=s_,
            extra=aptx, fes=("airport_iata", "iso_ym"), note="common sample; within-country" + ("" if s_ is None else "; " + k_))
print("A3 done")

# ---- A4 dose: deciles of 1996 GACI (bottom decile = reference) ----
bins = []
for y in (["d12_ln_seats", "d12_ln_co2"] if RUN("A4") else []):
    d = MAIN[[y, PR, "dec", "airport_iata", "iso3", "t", "year", "ym"]].dropna().copy()
    ex = []
    for k in range(2, 11):
        d[f"x_d{k}"] = d[PR] * (d.dec == k)
        ex.append(f"x_d{k}")
    r = fit(d, y, exog=ex, fes=list(FE), vc=VC, vc_alt=ALT)
    for k in range(2, 11):
        bins.append(dict(outcome=y, decile=k, b=r["coef"][f"x_d{k}"], se=r["se"][f"x_d{k}"], p=r["p"][f"x_d{k}"],
                         se_cl=r["alt"][0]["se"][f"x_d{k}"], n=r["n"]))
if RUN("A4"):
    pd.DataFrame(bins).to_csv("_res_airport_bins.csv", index=False)
print("A4 done")

# ---- A5 robustness (d12 ln seats, H_g) ----
y = "d12_ln_seats"
if RUN("A5"):
    MAIN["pos"] = MAIN[PR].clip(lower=0)
    MAIN["neg"] = MAIN[PR].clip(upper=0)
    MAIN["w96"] = MAIN.seats_96
    FULL = am[(am.year >= 1997)].copy()
    for est, s, col in [("OLS", None, "OLS"), ("2SLS", SH["KZ"], "2SLS-KZ"), ("2SLS", SH["BH"], "2SLS-BH")]:
        for L in [0, 1, 6, 9, 12]:
            run("A5", f"price lag {L}", col, y, "H_g", est, MAIN, price=f"d12_lnjet_l{L}" if L else "d12_lnjet",
                shock=s.replace("_l3", f"_l{L}") if s else None)
        run("A5", "Brent", col, y, "H_g", est, MAIN, price="d12_lnbrent_l3", shock=s)
        run("A5", "nominal price", col, y, "H_g", est, MAIN, price="d12_lnjet_nom_l3", shock=s)
        run("A5", "balanced airports", col, y, "H_g", est, MAIN[MAIN.n_months_9619 == 288], shock=s)
        run("A5", "seat-weighted (1996)", col, y, "H_g", est, MAIN, shock=s, weights="w96")
        run("A5", "incl. 2020-2024", col, y, "H_g", est, FULL, shock=s, sample="1997-2024")
        run("A5", "1997-2008", col, y, "H_g", est, MAIN[MAIN.year <= 2008], shock=s, sample="1997-2008")
        run("A5", "2009-2019", col, y, "H_g", est, MAIN[MAIN.year >= 2009], shock=s, sample="2009-2019")
        run("A5", "excl. USA", col, y, "H_g", est, MAIN[MAIN.iso3 != "USA"], shock=s)
        run("A5", "excl. Middle East", col, y, "H_g", est, MAIN[MAIN.cont != "ME"], shock=s)
        run("A5", "region x month FE", col, y, "H_g", est, MAIN, shock=s, fes=("airport_iata", "reg_ym"))
        run("A5", "country x month FE", col, y, "H_g", est, MAIN, shock=s, fes=("airport_iata", "iso_ym"))
        run("A5", "trim |D12| > 1", col, y, "H_g", est, MAIN[MAIN[y].abs() <= 1], shock=s)
        run("A5", "SE: DK L=24", col, y, "H_g", est, MAIN, shock=s, vc=("dk", "iso3", "t", 24))
        run("A5", "SE: airport cluster + DK L=12", col, y, "H_g", est, MAIN, shock=s, vc=("dk", "airport_iata", "t", 12))
    run("A5", "Kaenzig pre-Covid vintage", "2SLS-KZ", y, "H_g", "2SLS", MAIN, shock="kz_pre_s12_l3")
    run("A5", "crack spread", "OLS", y, "H_g", "OLS", MAIN, price="d12_lncrack_l3")
    run("A5", "Brent + crack", "OLS", y, "H_g", "OLS", MAIN.assign(xc=MAIN.d12_lncrack_l3 * MAIN.H_g), price="d12_lnbrent_l3",
        extra_exog=["xc"])
    # asymmetry: rises vs falls
    d = MAIN[[y, "pos", "neg", "H_g", "airport_iata", "iso3", "t", "year", "ym"]].dropna().copy()
    d["x_pos"], d["x_neg"] = d.pos * d.H_g, d.neg * d.H_g
    r = fit(d, y, exog=["x_pos", "x_neg"], fes=list(FE), vc=VC, vc_alt=ALT)
    rec("A5", "asymmetry", "OLS", y, "H_g", "OLS", None, PR, "D12", "1997-2019", r, ["x_pos", "x_neg"], [],
        "x_pos: price rises; x_neg: price falls", d.airport_iata.nunique())
    # levels specification with airport x calendar-month FE and H x trend
    LV = MAIN.copy()
    LV["apt_m"] = LV.airport_iata + "_" + LV.month.astype(str)
    LV["H_tr"] = LV.H_g * LV.t
    for est, s, col in [("OLS", None, "OLS"), ("2SLS", "kz_cum_l3", "2SLS-KZ"), ("2SLS", "bh_neg_cum_l3", "2SLS-BH")]:
        run("A5", "levels + H x trend", col, "ln_seats", "H_g", est, LV, price="lnjet_l3", shock=s, extra_exog=["H_tr"],
            fes=("apt_m", "ym"), spec="levels")
    print("A5 done")

res = pd.DataFrame(rows)
if ONLY is not None:
    old_ = pd.read_csv("_res_airport.csv")
    res = pd.concat([old_[~old_.table.isin(ONLY)], res], ignore_index=True)
res.to_csv("_res_airport.csv", index=False)

# ---- hub-spoke gap series: monthly cross-sectional slope of D12 ln seats on H_g (for figures) ----
g = []
for t_, d in (MAIN.dropna(subset=["d12_ln_seats"]).groupby("ym") if ONLY is None else []):
    X = np.column_stack([np.ones(len(d)), d.H_g])
    bb = np.linalg.lstsq(X, d.d12_ln_seats.to_numpy(), rcond=None)[0]
    g.append(dict(ym=t_, slope=bb[1], d12_lnjet_l3=d[PR].iloc[0], kz_s12_l3=d[SH["KZ"]].iloc[0], bh_s12_l3=d[SH["BH"]].iloc[0]))
if ONLY is None:
    pd.DataFrame(g).to_csv("_hubgap_series.csv", index=False)

m = res[res.table == "A1"]
print(m[~m.col.str.startswith("RF")][["position", "outcome", "col", "b", "se", "p", "p_cl", "F", "n"]].round(4).to_string(index=False))
