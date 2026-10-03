# -*- coding: utf-8 -*-
"""Alternative fuel-shock designs, airport x month, 12-month differences, 1997-2019
(airport + year-month FE; country cluster + Newey-West over months, L = 12).

Section 1. Who is exposed (price x 1996 exposure):
  D1  fuel burn per seat (kg CO2 per departing seat), CO2 per seat-km (fleet efficiency), stage length,
      each alone and jointly with GACI; outcomes seats, CO2, CO2 per seat-km, seats per departure.
Section 2. What kind of oil price movement (moderator = GACI 1996 and fuel burn per seat):
  D2  Baumeister-Hamilton decomposition: supply, economic activity, oil consumption demand, oil inventory
      demand shocks (12-month sums, lag 3) x H, jointly (reduced form); price-equivalent scaling from the
      time-series regression of D12 ln P on the four sums.
  D3  persistent vs transitory: (a) D12 of the 12-month-ahead expected WTI price (Baumeister 2022) vs D12 of
      the spot premium over it; (b) D12 of the 12-month trailing mean of ln jet vs D12 of the deviation from it;
      (c) Kaenzig news shock vs BH supply shock (reduced form, jointly).
  D4  crude vs jet-specific: D12 ln Brent and D12 ln crack spread (jet / Brent) jointly.
  D5  asymmetry (rises vs falls) and regime (real jet price above / below USD 2.5 per gallon, t-3).
Output: _res_designs.csv, _res_designs_ts.csv
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from _est import fit
from _prep_airport import panel, fuel_monthly

am = panel()
M = am[(am.year >= 1997) & (am.year <= 2019)].copy()
VC = ("dk", "iso3", "t", 12)
ALT = [("cl", "iso3"), ("cl2", "iso3", "year")]
PR, SH = "d12_lnjet_l3", {"KZ": "kz_s12_l3", "BH": "bh_neg_s12_l3"}
FE = ["airport_iata", "ym"]
rows = []
ONLY = sys.argv[1].split(",") if len(sys.argv) > 1 else None      # e.g. "D1j" re-runs one block and merges
RUN = lambda b: ONLY is None or b in ONLY

def add(tab, panel_, col, y, est, r, terms, labels=None, note="", H=""):
    for i, t_ in enumerate(terms):
        if t_ not in r["coef"]:
            continue
        rows.append(dict(table=tab, panel=panel_, col=col, outcome=y, estimator=est, moderator=H, term=t_,
                         label=(labels[i] if labels else t_), b=r["coef"][t_], se=r["se"][t_], p=r["p"][t_],
                         se_cl=r["alt"][0]["se"][t_], p_cl=r["alt"][0]["p"][t_], n=r["n"],
                         F=r["fs"].get(terms[0], {}).get("F", np.nan) if r.get("fs") else np.nan, note=note))

def inter(d, pairs):
    """pairs: list of (name, shock_col, moderator_col) -> creates product columns"""
    for nm, s, h in pairs:
        d[nm] = d[s] * d[h]
    return [p[0] for p in pairs]

# ================= Section 1: exposure =================
EXPO = [("z_fuelseat", "Fuel burn per seat 1996 (z)"), ("z_int", "CO2 per seat-km 1996 (z)"), ("z_stage", "Stage length 1996 (z)")]
for y in ["d12_ln_seats", "d12_ln_co2", "d12_ln_int", "d12_ln_gauge"]:
    for H, lab in (EXPO if RUN("D1") else []):
        d = M.dropna(subset=[y, PR, H]).copy()
        d["x"] = d[PR] * d[H]
        r = fit(d, y, exog=["x"], fes=FE, vc=VC, vc_alt=ALT)
        add("D1", H, "OLS", y, "OLS", r, ["x"], [lab], H=H)
        for k, s in SH.items():
            d["zz"] = d[s] * d[H]
            r = fit(d.dropna(subset=[s]), y, endog=["x"], instr=["zz"], fes=FE, vc=VC, vc_alt=ALT)
            add("D1", H, "2SLS-" + k, y, "2SLS", r, ["x"], [lab], H=H)
    # joint: fuel/seat + GACI; all three + GACI; + country x month FE
    # ln(fuel/seat) = ln(CO2 per seat-km) + ln(stage) exactly, so the three cannot enter together:
    # "efficiency + stage + GACI" splits fuel/seat into its two parts
    for col, Hs, fes in ([] if not RUN("D1j") else [("fuel/seat + GACI", ["z_fuelseat", "H_g"], FE),
                         ("efficiency + stage + GACI (fuel/seat split)", ["z_int", "z_stage", "H_g"], FE),
                         ("fuel/seat + GACI, country x month FE", ["z_fuelseat", "H_g"], ["airport_iata", "iso_ym"]),
                         ("fuel/seat + size + intl + GACI", ["z_fuelseat", "z_size", "z_intl", "H_g"], FE)]):
        d = M.dropna(subset=[y, PR] + Hs).copy()
        xs = inter(d, [("x_" + h, PR, h) for h in Hs])
        r = fit(d, y, exog=xs, fes=fes, vc=VC, vc_alt=ALT)
        add("D1j", col, "OLS", y, "OLS", r, xs)
        for k, s in SH.items():
            dd = d.dropna(subset=[s]).copy()
            zs = inter(dd, [("z_" + h, s, h) for h in Hs])
            r = fit(dd, y, endog=xs, instr=zs, fes=fes, vc=VC, vc_alt=ALT)
            add("D1j", col, "2SLS-" + k, y, "2SLS", r, xs)
    print("D1", y, "done")

# ================= Section 2: kind of oil price movement =================
if not RUN("S2"):
    res = pd.DataFrame(rows)
    old_ = pd.read_csv("_res_designs.csv")
    drop = [t for t in ["D1", "D1j"] if RUN(t)]
    res = pd.concat([old_[~old_.table.isin(drop)], res], ignore_index=True)
    res.to_csv("_res_designs.csv", index=False)
    print(res[res.table.isin(drop)][["table", "panel", "col", "outcome", "label", "b", "se", "p"]].round(4).to_string(index=False))
    sys.exit(0)
f = fuel_monthly()
fm = f[(f.year >= 1997) & (f.year <= 2019)].copy()
ts = []
def tsreg(yv, xs, lab):
    q = fm[[yv] + xs].dropna()
    o = sm.OLS(q[yv], sm.add_constant(q[xs])).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    for x in xs:
        ts.append(dict(design=lab, dep=yv, term=x, b=o.params[x], se=o.bse[x], p=o.pvalues[x], sd_x=q[x].std(), n=int(o.nobs), r2=o.rsquared))
    return o

BHS = [("bh_neg_s12_l3", "Supply (BH, x -1)"), ("bh_act_s12_l3", "Economic activity (BH)"),
       ("bh_cons_s12_l3", "Oil consumption demand (BH)"), ("bh_inv_s12_l3", "Oil inventory demand (BH)")]
tsreg("d12_lnjet_l3", [b for b, _ in BHS], "D2 BH decomposition")
sd = {b: fm[b].std() for b, _ in BHS}
for H in ["H_g", "z_fuelseat"]:
    for y in ["d12_ln_seats", "d12_ln_co2"]:
        d = M.dropna(subset=[y, H] + [b for b, _ in BHS]).copy()
        xs = []
        for b_, _ in BHS:
            d["x_" + b_] = d[b_] / sd[b_] * d[H]
            xs.append("x_" + b_)
        r = fit(d, y, exog=xs, fes=FE, vc=VC, vc_alt=ALT)
        add("D2", H, "RF, per 1 SD of each 12-month shock sum", y, "RF", r, xs, [l for _, l in BHS], H=H)
    print("D2", H, "done")

# persistent vs transitory
tsreg("d12_lnjet_l3", ["d12_ln_e12_l3", "d12_ln_trans_l3"], "D3a expectations")
tsreg("d12_lnjet_l3", ["d12_lnjet_ma12_l3", "d12_lnjet_dev_l3"], "D3b moving average")
tsreg("d12_lnjet_l3", ["kz_s12_l3", "bh_neg_s12_l3"], "D3c KZ vs BH")
for H in ["H_g", "z_fuelseat"]:
    for y in ["d12_ln_seats", "d12_ln_co2"]:
        for lab, comps, labs in [("(a) expected vs spot premium", ["d12_ln_e12_l3", "d12_ln_trans_l3"],
                                  ["D12 ln expected WTI, 12 months ahead (persistent)", "D12 (ln spot WTI - ln expected) (transitory)"]),
                                 ("(b) 12-month mean vs deviation", ["d12_lnjet_ma12_l3", "d12_lnjet_dev_l3"],
                                  ["D12 of 12-month trailing mean of ln jet (persistent)", "D12 of deviation from trailing mean (transitory)"]),
                                 ("(c) Kaenzig news vs BH supply (RF, per 1 SD)", ["kz_s12_l3", "bh_neg_s12_l3"],
                                  ["Kaenzig news shock, 12-month sum (per SD)", "BH supply shock x -1, 12-month sum (per SD)"])]:
            d = M.dropna(subset=[y, H] + comps).copy()
            xs = []
            for c_ in comps:
                scale = fm[c_].std() if lab.startswith("(c)") else 1.0
                d["x_" + c_] = d[c_] / scale * d[H]
                xs.append("x_" + c_)
            r = fit(d, y, exog=xs, fes=FE, vc=VC, vc_alt=ALT)
            add("D3", H, lab, y, "OLS" if not lab.startswith("(c)") else "RF", r, xs, labs, H=H)
    print("D3", H, "done")

# crude vs jet-specific; asymmetry; regime
for H in ["H_g", "z_fuelseat"]:
    for y in ["d12_ln_seats", "d12_ln_co2"]:
        d = M.dropna(subset=[y, H, "d12_lnbrent_l3", "d12_lncrack_l3"]).copy()
        xs = inter(d, [("x_brent", "d12_lnbrent_l3", H), ("x_crack", "d12_lncrack_l3", H)])
        r = fit(d, y, exog=xs, fes=FE, vc=VC, vc_alt=ALT)
        add("D4", H, "crude vs jet-specific", y, "OLS", r, xs, ["D12 ln Brent x H", "D12 ln crack spread x H"], H=H)
        d = M.dropna(subset=[y, H, PR, "jet_real_l3"]).copy()
        d["x_up"], d["x_dn"] = d[PR].clip(lower=0) * d[H], d[PR].clip(upper=0) * d[H]
        r = fit(d, y, exog=["x_up", "x_dn"], fes=FE, vc=VC, vc_alt=ALT)
        add("D5", H, "asymmetry", y, "OLS", r, ["x_up", "x_dn"], ["price rises x H", "price falls x H"], H=H)
        hi = (d.jet_real_l3 > 2.5).astype(float)
        d["x_hi"], d["x_lo"] = d[PR] * d[H] * hi, d[PR] * d[H] * (1 - hi)
        r = fit(d, y, exog=["x_hi", "x_lo"], fes=FE, vc=VC, vc_alt=ALT)
        add("D5", H, "regime", y, "OLS", r, ["x_hi", "x_lo"], ["D12 ln P x H, real jet > USD 2.5 (t-3)", "D12 ln P x H, real jet <= USD 2.5"], H=H)
    print("D4-5", H, "done")

res = pd.DataFrame(rows)
res.to_csv("_res_designs.csv", index=False)
pd.DataFrame(ts).to_csv("_res_designs_ts.csv", index=False)
pd.set_option("display.width", 260)
print(res[["table", "panel", "col", "outcome", "label", "b", "se", "p", "F", "n"]].round(4).to_string(index=False))
print(pd.DataFrame(ts).round(4).to_string(index=False))
