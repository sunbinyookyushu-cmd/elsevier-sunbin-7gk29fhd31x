# -*- coding: utf-8 -*-
"""Country-level version of the oil-shock analysis (user request 2026-10-02: "just estimate it at country level").
Same equations as the airport analysis, with seats summed to country x month.

Data: airport_month_sep08fix.parquet (Sep-2008 gap interpolated), all airports of a country summed; outcome
D12 ln seats (total, domestic, international departing seats); months with zero seats dropped (log undefined).
Shocks as in 37: D12 ln real jet price (lag 3), Kaenzig news shock 12-month sum (lag 3), BH supply shock (x -1)
12-month sum (lag 3).

A. Average response, 1997-2019: D12 ln S_ct = a_c + b Shock_(t-3) + e; country FE, SE country cluster +
   Newey-West 12 over months (_est.py "dk").
B. Resilience, two-step (country analogue of 37/38): per country 2008-2019 beta_c (HAC 12, >= 120 months),
   then beta_c = a + g R_c (+ ln GACI_c + region FE), robust SE; betas trimmed 1/99 pct as in 38.
   R_c = 2007-seat-weighted mean of the airport pre-2008 resilience index (resilience_airport.csv, built from
   1996-2007); GACI_c = 2007-seat-weighted mean airport GACI 2007; region = region of the country's largest airport.
C. Same as B in one panel regression: D12 ln S_ct = a_c + d_t + g (Kaenzig_(t-3) x R_c) + e, 2008-2019.
Output: _res_country_level.csv, country_betas.csv, country_month.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import statsmodels.api as sm
import statsmodels.formula.api as smf
from _est import fit

OUT = {"total": "dep_seats", "domestic": "dep_seats_dom", "international": "dep_seats_intl"}
SHOCKS = {"jet fuel price (D12 ln, real)": "d12_lnjet_l3", "Kaenzig oil supply news shock": "kz_s12_l3",
          "BH oil supply shock": "bh_neg_s12_l3"}

# ---- country x month panel ----
am = pq.read_table("airport_month_sep08fix.parquet",
                   columns=["airport_iata", "iso3", "year", "month"] + list(OUT.values())).to_pandas()
am = am[am.iso3.notna()]
cm = am.groupby(["iso3", "year", "month"], as_index=False)[list(OUT.values())].sum()
cm["t"] = cm.year * 12 + cm.month
for k, v in OUT.items():
    cm["ln_" + k] = np.log(cm[v].where(cm[v] > 0))
lag = cm[["iso3", "t"] + ["ln_" + k for k in OUT]].copy()
lag["t"] += 12
cm = cm.merge(lag, on=["iso3", "t"], how="left", suffixes=("", "_m12"))
for k in OUT:
    cm["y_" + k] = cm["ln_" + k] - cm["ln_" + k + "_m12"]
f = pd.read_csv("fuel_monthly.csv")
cm = cm.merge(f[["year", "month"] + list(SHOCKS.values())], on=["year", "month"], how="left")
cm["ym"] = cm.t

# ---- country traits (measured up to 2007) ----
R = pd.read_csv("resilience_airport.csv")[["airport_iata", "R_pre2008"]]
g = pd.read_csv(r"..\GACI1996_2024_new_panel_data.csv")
g07 = g[g.Year == 2007][["Airport", "GACI", "Region"]].rename(columns={"Airport": "airport_iata"})
s07 = am[am.year == 2007].groupby(["airport_iata", "iso3"], as_index=False).dep_seats.sum()
s07 = s07.merge(R, on="airport_iata", how="left").merge(g07, on="airport_iata", how="left")
rows = []
for c, x in s07.groupby("iso3"):
    xr, xg = x.dropna(subset=["R_pre2008"]), x.dropna(subset=["GACI"])
    rows.append(dict(iso3=c, seats07=x.dep_seats.sum(),
                     R_c=np.average(xr.R_pre2008, weights=xr.dep_seats) if xr.dep_seats.sum() > 0 else np.nan,
                     R_cover=xr.dep_seats.sum() / x.dep_seats.sum() if x.dep_seats.sum() > 0 else np.nan,
                     lnG_c=np.log(np.average(xg.GACI, weights=xg.dep_seats)) if xg.dep_seats.sum() > 0 else np.nan,
                     region=x.sort_values("dep_seats").Region.dropna().iloc[-1] if x.Region.notna().any() else np.nan))
CT = pd.DataFrame(rows)
cm = cm.merge(CT, on="iso3", how="left")
cm.to_csv("country_month.csv", index=False)

res = []
sd = {v: cm.drop_duplicates("t").query("1997 <= year <= 2019")[v].std() for v in SHOCKS.values()}

# ---- A. average response ----
a = cm[(cm.year >= 1997) & (cm.year <= 2019)]
for slab, s in SHOCKS.items():
    for k in OUT:
        o = fit(a, "y_" + k, exog=[s], fes=["iso3"], vc=("dk", "iso3", "t", 12), return_fs=False)
        res.append(dict(part="A average response 1997-2019", outcome=k, shock=slab, term="shock", b=o["coef"][s],
                        se=o["se"][s], p=o["p"][s], n=o["n"], countries=a.dropna(subset=["y_" + k, s]).iso3.nunique(),
                        sd_shock=sd[s], effect_1sd=o["coef"][s] * sd[s]))

# ---- B. two-step resilience ----
w = cm[(cm.year >= 2008) & (cm.year <= 2019)]
betas = []
for c, x in w.groupby("iso3"):
    for k in OUT:
        xx = x.dropna(subset=["y_" + k])
        if len(xx) < 120:
            continue
        rec = dict(iso3=c, outcome=k, n_months=len(xx))
        for slab, s in SHOCKS.items():
            o = sm.OLS(xx["y_" + k], sm.add_constant(xx[s])).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
            rec[s], rec[s + "_se"] = o.params[s], o.bse[s]
        betas.append(rec)
B = pd.DataFrame(betas).merge(CT, on="iso3", how="left")
B.to_csv("country_betas.csv", index=False)
for k in OUT:
    for slab, s in SHOCKS.items():
        d = B[(B.outcome == k)].dropna(subset=[s, "R_c", "lnG_c", "region"]).copy()
        lo, hi = d[s].quantile([0.01, 0.99])
        d = d[(d[s] >= lo) & (d[s] <= hi)]
        d["Rz"] = (d.R_c - d.R_c.mean()) / d.R_c.std()
        d["Gz"] = (d.lnG_c - d.lnG_c.mean()) / d.lnG_c.std()
        for spec, rhs in [("(1) resilience only", "Rz"), ("(2) + GACI + region FE", "Rz + Gz + C(region)")]:
            m = smf.ols(f"{s} ~ {rhs}", d).fit(cov_type="HC1")
            res.append(dict(part="B two-step 2008-2019", outcome=k, shock=slab, term="resilience", spec=spec,
                            b=m.params["Rz"], se=m.bse["Rz"], p=m.pvalues["Rz"], n=int(m.nobs), countries=int(m.nobs),
                            mean_beta=d[s].mean(), sd_shock=sd[s], effect_1sd=m.params["Rz"] * sd[s]))

# ---- C. panel interaction ----
Rs = CT.dropna(subset=["R_c"])
w = w.drop(columns=["Rz"], errors="ignore").merge(
    Rs.assign(Rz=(Rs.R_c - Rs.R_c.mean()) / Rs.R_c.std())[["iso3", "Rz"]], on="iso3", how="inner")
for slab, s in SHOCKS.items():
    w["x_" + s] = w[s] * w.Rz
    for k in OUT:
        o = fit(w, "y_" + k, exog=["x_" + s], fes=["iso3", "ym"], vc=("dk", "iso3", "t", 12), return_fs=False,
                vc_alt=[("cl", "iso3")])
        res.append(dict(part="C panel 2008-2019 (country + month FE)", outcome=k, shock=slab, term="shock x resilience",
                        b=o["coef"]["x_" + s], se=o["se"]["x_" + s], p=o["p"]["x_" + s], n=o["n"],
                        countries=w.dropna(subset=["y_" + k]).iso3.nunique(), se_country_cl=o["alt"][0]["se"]["x_" + s],
                        p_country_cl=o["alt"][0]["p"]["x_" + s], sd_shock=sd[s], effect_1sd=o["coef"]["x_" + s] * sd[s]))

out = pd.DataFrame(res)
out.to_csv("_res_country_level.csv", index=False)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 20)
print(out[["part", "outcome", "shock", "spec", "b", "se", "p", "n", "countries", "effect_1sd"]].round(4).to_string(index=False))
print("\nR_c coverage (share of 2007 seats at airports with a pre-2008 score):", CT.R_cover.describe().round(3).to_dict())
print("countries with R_c:", CT.R_c.notna().sum(), " with region:", CT.region.notna().sum())
