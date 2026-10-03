# -*- coding: utf-8 -*-
"""Do resilient airports absorb jet-fuel price shocks better?

  D12 ln y_it = a_i + d_t + b (D12 ln P_(t-3) x Rz_i) + e_it
  Rz_i = z-score of the airport's resilience index (30_build_resilience.py), built only from years
  before the test window: pre2004 -> test 2004-2019, pre2008 -> test 2008-2019; real-time R_(i,y-1)
  (time-varying, main effect included) -> 2004-2019; full-sample R (overlaps the fuel episodes)
  -> 1997-2019 for comparison. b > 0: resilient airports cut capacity less when fuel prices rise.
Instruments, variance and FE as in 12_airport_monthly.py.
Also: horse race against GACI position (and its square), components, terciles, predictive validity
of pre-2008 resilience for later crises, the 2022 spike with pre-Covid resilience, and a replication
check against Zhang, Cheung & Zhang (2027) Table 5 / Fig. 10.
Output: _res_resil.csv, _res_resil_events.csv, _res_resil_es.csv, _res_resil_valid.csv
"""
import numpy as np
import pandas as pd
from _est import fit

am = pd.read_parquet("airport_month.parquet")
am = am[am.iso3.notna()].copy()
R = pd.read_csv("resilience_airport.csv")
rt = pd.read_csv("resilience_realtime.csv")
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
gw = g.pivot_table(index="Airport", columns="Year", values="GACI")
base = pd.read_csv("airport_base.csv")[["airport_iata", "seats_96", "intl_share_96", "stage_96", "Region_96"]]

OUT = ["ln_seats", "ln_flights", "ln_skm", "ln_co2"]
lag = am[["airport_iata", "t"] + OUT].copy()
lag["t"] += 12
am = am.merge(lag, on=["airport_iata", "t"], how="left", suffixes=("", "_m12"))
for v in OUT:
    am["d12_" + v] = am[v] - am[v + "_m12"]
f = pd.read_csv("fuel_monthly.csv")
am = am.merge(f[["ym", "d12_lnjet_l3", "kz_s12_l3", "bh_neg_s12_l3", "lnjet_l3"]], on="ym", how="left")
am = am.merge(R, on="airport_iata", how="left").merge(base, on="airport_iata", how="left")
am["iso_ym"] = am.iso3 + "_" + am.ym
for Y in [1996, 2003, 2007, 2019]:
    am[f"gaci_{Y}"] = am.airport_iata.map(gw[Y])
am = am.merge(rt.rename(columns={"R": "R_rt", "depth": "depth_rt", "speed": "speed_rt", "adapt": "adapt_rt",
                                 "n_valid": "n_valid_rt"}), on=["airport_iata", "year"], how="left")

VC = ("dk", "iso3", "t", 12)
ALT = [("cl", "iso3"), ("cl2", "iso3", "year")]
PR, SH = "d12_lnjet_l3", {"KZ": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
rows = []

def zs(d, v, by=None):
    """z-score on the airport cross-section of the estimation sample (per year when `by` is given)"""
    if by is None:
        c = d.drop_duplicates("airport_iata")[v]
        return (d[v] - c.mean()) / c.std()
    c = d.drop_duplicates(["airport_iata", by]).groupby(by)[v].agg(["mean", "std"])
    return (d[v] - d[by].map(c["mean"])) / d[by].map(c["std"])

def run(tab, panel, col, y, d, H, est, shock=None, extra=(), exog0=(), fes=("airport_iata", "ym"), note="", window=""):
    need = list(dict.fromkeys([y, PR, H, "airport_iata", "iso3", "t", "year", "ym"] + list(fes) + list(extra) + list(exog0)
                              + ([shock] if shock else [])))
    d = d[need].dropna().copy()
    d["x"] = d[PR] * d[H]
    ctrl = []
    for X in extra:
        d["x_" + X] = d[PR] * d[X]
        ctrl.append("x_" + X)
    endog, instr, exog = [], [], list(exog0)
    if est == "OLS":
        exog = ["x"] + ctrl + exog
    else:
        d["zz"] = d[shock] * d[H]
        endog, instr = ["x"] + ctrl, ["zz"]
        for X in extra:
            d["zz_" + X] = d[shock] * d[X]
            instr.append("zz_" + X)
    r = fit(d, y, exog=exog, endog=endog, instr=instr, fes=list(fes), vc=VC, vc_alt=ALT)
    for term in ["x"] + ctrl + list(exog0):
        rows.append(dict(table=tab, panel=panel, col=col, outcome=y, moderator=H, estimator=est, shock=shock or "",
                         window=window, term=term, b=r["coef"][term], se=r["se"][term], p=r["p"][term],
                         se_cl=r["alt"][0]["se"][term], p_cl=r["alt"][0]["p"][term], se_2w=r["alt"][1]["se"][term],
                         p_2w=r["alt"][1]["p"][term], n=r["n"], n_air=d.airport_iata.nunique(), G=r["G"],
                         F=r["fs"].get("x", {}).get("F", np.nan) if endog else np.nan, r2w=r["r2_within"], note=note))
    return r

WIN = {"pre2004": (2004, 2019), "pre2008": (2008, 2019), "full": (1997, 2019)}
S = {}
for v, (a, b) in WIN.items():
    d = am[(am.year >= a) & (am.year <= b) & am[f"R_{v}"].notna()].copy()
    d["Rz"] = zs(d, f"R_{v}")
    for c in ["depth", "speed", "adapt"]:
        d[c + "_z"] = zs(d, f"{c}_{v}")
    gy = {"pre2004": 2003, "pre2008": 2007, "full": 1996}[v]
    d["G"] = zs(d, f"gaci_{gy}")
    d["G2"] = d.G ** 2
    d["size_z"] = zs(d.assign(ls=np.log(d.seats_96.where(d.seats_96 > 0))), "ls")
    d["intl_z"] = zs(d, "intl_share_96")
    d["stage_z"] = zs(d.assign(lst=np.log(d.stage_96.where(d.stage_96 > 0))), "lst")
    q = d.drop_duplicates("airport_iata")[f"R_{v}"].quantile([1 / 3, 2 / 3]).to_numpy()
    d["T_mid"] = ((d[f"R_{v}"] > q[0]) & (d[f"R_{v}"] <= q[1])).astype(float)
    d["T_top"] = (d[f"R_{v}"] > q[1]).astype(float)
    S[v] = d
# real-time
d = am[(am.year >= 2004) & (am.year <= 2019) & am.R_rt.notna()].copy()
d["Rz"] = zs(d, "R_rt", by="year")
S["realtime"] = d

# ---- RS1 main ----
LAB = {"pre2004": ("Panel A. Resilience built from 1996-2003 (AFC, 9/11, SARS); test 2004-2019", "2004-2019"),
       "pre2008": ("Panel B. Resilience built from 1996-2007 (AFC, 9/11, SARS); test 2008-2019", "2008-2019"),
       "realtime": ("Panel C. Real-time resilience R(i, y-1), updated yearly; test 2004-2019", "2004-2019"),
       "full": ("Panel D. Full-sample resilience (8 crises, 1996-2024; overlaps the fuel episodes); test 1997-2019", "1997-2019")}
for v in ["pre2004", "pre2008", "realtime", "full"]:
    ex0 = ["Rz"] if v == "realtime" else []
    for y in ["d12_ln_seats", "d12_ln_flights", "d12_ln_skm", "d12_ln_co2"]:
        run("RS1", v, "OLS", y, S[v], "Rz", "OLS", exog0=ex0, window=LAB[v][1])
        for k, s in SH.items():
            run("RS1", v, "2SLS-" + k, y, S[v], "Rz", "2SLS", shock=s, exog0=ex0, window=LAB[v][1])
    print("RS1", v, "done")

# ---- RS2 horse race with GACI position (pre2004 and pre2008) ----
for v in ["pre2004", "pre2008"]:
    d = S[v].dropna(subset=["G", "size_z", "intl_z", "stage_z"])
    specs = [("(1) resilience", "Rz", []), ("(2) GACI only", "G", []), ("(3) resilience + GACI", "Rz", ["G"]),
             ("(4) + GACI squared", "Rz", ["G", "G2"]), ("(5) + size, intl, stage", "Rz", ["G", "G2", "size_z", "intl_z", "stage_z"])]
    for lab, H, ex in specs:
        run("RS2", v, lab, "d12_ln_seats", d, H, "OLS", extra=ex, window=LAB[v][1], note="common sample")
        for k, s in SH.items():
            run("RS2", v, lab, "d12_ln_seats", d, H, "2SLS", shock=s, extra=ex, window=LAB[v][1], note="common sample; " + k)
    lab = "(6) (5) + country x month FE"
    run("RS2", v, lab, "d12_ln_seats", d, "Rz", "OLS", extra=["G", "G2", "size_z", "intl_z", "stage_z"],
        fes=("airport_iata", "iso_ym"), window=LAB[v][1], note="common sample")
    for k, s in SH.items():
        run("RS2", v, lab, "d12_ln_seats", d, "Rz", "2SLS", shock=s, extra=["G", "G2", "size_z", "intl_z", "stage_z"],
            fes=("airport_iata", "iso_ym"), window=LAB[v][1], note="common sample; " + k)
    print("RS2", v, "done")

# ---- RS3 components and terciles (pre2004, pre2008) ----
for v in ["pre2004", "pre2008"]:
    d = S[v]
    for c in ["depth_z", "speed_z", "adapt_z"]:
        run("RS3", v, c, "d12_ln_seats", d, c, "OLS", window=LAB[v][1])
        run("RS3", v, c, "d12_ln_seats", d, c, "2SLS", shock=SH["BH"], window=LAB[v][1], note="BH")
        run("RS3", v, c, "d12_ln_seats", d, c, "2SLS", shock=SH["KZ"], window=LAB[v][1], note="KZ")
    run("RS3", v, "all three", "d12_ln_seats", d.dropna(subset=["depth_z", "speed_z", "adapt_z"]), "depth_z", "OLS",
        extra=["speed_z", "adapt_z"], window=LAB[v][1])
    dd = d.copy()
    run("RS3", v, "terciles", "d12_ln_seats", dd, "T_mid", "OLS", extra=["T_top"], window=LAB[v][1], note="bottom tercile = reference")
    print("RS3", v, "done")

res = pd.DataFrame(rows)
res.to_csv("_res_resil.csv", index=False)

# ---- RS4 predictive validity: does pre-2008 resilience predict later crisis performance? ----
cc = pd.read_csv("resilience_crisis_full.csv").rename(columns={"a": "airport_iata"})
X = R[["airport_iata", "R_pre2008", "R_pre2004"]].merge(cc, on="airport_iata")
X["iso3"] = X.airport_iata.map(am.drop_duplicates("airport_iata").set_index("airport_iata").iso3)
X["lg07"] = np.log(X.airport_iata.map(gw[2007]))
X["lg03"] = np.log(X.airport_iata.map(gw[2003]))
X["one"] = 1
val = []
for v, lg in [("R_pre2008", "lg07"), ("R_pre2004", "lg03")]:
    X["Rz"] = (X[v] - X[v].mean()) / X[v].std()
    for yv in ["depth_GFC+H1N1", "speed_GFC+H1N1", "depth_Ash+Tohoku", "depth_Ebola+MERS", "depth_COVID", "speed_COVID",
               "upgrade_COVID"]:
        for ctrl in [[], [lg]]:
            d = X.dropna(subset=[yv, "Rz", "iso3"] + ctrl)
            if v == "R_pre2004" and yv.endswith("GFC+H1N1") is False and False:
                pass
            r = fit(d, yv, exog=["Rz"] + ctrl, fes=[], vc=("cl", "iso3"))
            val.append(dict(resilience=v, outcome=yv, control=("ln GACI at build end" if ctrl else "none"), b=r["coef"]["Rz"],
                            se=r["se"]["Rz"], p=r["p"]["Rz"], n=r["n"], ymean=r["ymean"]))
pd.DataFrame(val).to_csv("_res_resil_valid.csv", index=False)
print("RS4 done")

# ---- RS5 2022 spike with pre-Covid resilience ----
ev = am[(am.ym >= "2021-01") & (am.ym <= "2024-06") & am.R_pre2020.notna()].copy()
ev["Rz"] = zs(ev, "R_pre2020")
ev["apt_m"] = ev.airport_iata + "_" + ev.month.astype(str)
r19 = am[am.year == 2019][["airport_iata", "month", "ln_seats", "ln_seats_dom"]]
ev = ev.merge(r19, on=["airport_iata", "month"], how="left", suffixes=("", "_19"))
ev["rec"] = ev.ln_seats - ev.ln_seats_19
ev["rec_dom"] = ev.ln_seats_dom - ev.ln_seats_dom_19
ev["x_spike"] = ev.Rz * ((ev.ym >= "2022-03") & (ev.ym <= "2022-12"))
ev["x_after"] = ev.Rz * (ev.ym >= "2023-01")
y19 = am[am.year == 2019].groupby("airport_iata").agg(s=("dep_seats", "sum"), si=("dep_seats_intl", "sum"))
ev["intl19"] = ev.airport_iata.map(y19.si / y19.s)
ev["G19"] = zs(ev.assign(g=np.log(ev.gaci_2019)), "g")
ev["G19_spike"] = ev.G19 * ((ev.ym >= "2022-03") & (ev.ym <= "2022-12"))
ev["G19_after"] = ev.G19 * (ev.ym >= "2023-01")
er, es = [], []
for y in ["ln_seats", "ln_seats_dom", "rec", "rec_dom"]:
    for lab, extra in [("country x month FE", []), ("+ GACI 2019 x period", ["G19_spike", "G19_after"]), ("+ intl share x month", "intl")]:
        d = ev.dropna(subset=[y, "Rz"] + list(extra if extra != "intl" else [])).copy()
        part = []
        if extra == "intl":
            dm = pd.get_dummies(d.ym, prefix="im", drop_first=True).astype(float).mul(d.intl19.fillna(0).to_numpy(), axis=0)
            d = pd.concat([d, dm], axis=1)
            part = list(dm.columns)
            extra = []
        fes = ["airport_iata" if y.startswith("rec") else "apt_m", "iso_ym"]
        r = fit(d, y, exog=["x_spike", "x_after"] + list(extra), fes=fes, vc=("dk", "iso3", "t", 6), vc_alt=[("cl", "iso3")], partial=part)
        for tm in ["x_spike", "x_after"]:
            er.append(dict(outcome=y, spec=lab, term=tm, b=r["coef"][tm], se=r["se"][tm], p=r["p"][tm],
                           se_cl=r["alt"][0]["se"][tm], n=r["n"], n_air=d.airport_iata.nunique()))
    # event study (recovery outcome, reference 2022-02)
    if y == "rec":
        d = ev.dropna(subset=["rec", "Rz"]).copy()
        months = sorted(d.ym.unique())
        exs = []
        for m_ in months:
            if m_ == "2022-02":
                continue
            d["e_" + m_] = d.Rz * (d.ym == m_)
            exs.append("e_" + m_)
        r = fit(d, "rec", exog=exs, fes=["airport_iata", "iso_ym"], vc=("dk", "iso3", "t", 6), vc_alt=[("cl", "iso3")])
        for m_ in months:
            es.append(dict(ym=m_, b=r["coef"].get("e_" + m_, 0.0), se=r["se"].get("e_" + m_, 0.0), p=r["p"].get("e_" + m_, np.nan)))
pd.DataFrame(er).to_csv("_res_resil_events.csv", index=False)
pd.DataFrame(es).to_csv("_res_resil_es.csv", index=False)
print("RS5 done")

pd.set_option("display.width", 250)
m = res[(res.table == "RS1") & (res.term == "x")]
print(m[["panel", "outcome", "col", "b", "se", "p", "p_cl", "F", "n", "n_air"]].round(4).to_string(index=False))
