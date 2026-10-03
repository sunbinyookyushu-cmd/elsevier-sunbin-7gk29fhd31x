# -*- coding: utf-8 -*-
"""Local-currency jet fuel prices: country-specific fuel cost variation from real exchange rates.

  ln q_ct   = ln e_ct + ln CPI_US,t - ln CPI_c,t     (e: local currency per USD, BIS monthly averages;
                                                      CPI_c: WDI annual CPI interpolated log-linearly between
                                                      mid-year values; CPI_US: monthly CPI-U)
  ln P^loc_ct = ln P_t (real USD jet price) + ln q_ct  (real local-currency jet price)
Designs (airport x month, D12 differences, lag 3, 1997-2019):
  L1  D12 ln y on D12 ln P^loc with airport + year-month FE: the USD price is absorbed, so the coefficient comes
      from real exchange-rate movements (which also move travel demand; reported for completeness).
  L2  D12 ln q_c x fuel burn per seat_i (and x GACI_i) with airport + country x year-month FE, controlling
      D12 ln P_t x exposure: within a country and month, do fuel-intensive airports cut more when the local
      real cost of fuel rises? Country-level demand effects of the exchange rate are absorbed.
  L3  L2 for domestic seats only; L2 excluding large real-rate swings (|D12 ln q| > 0.5).
Output: _res_localfx.csv, local_fx_monthly.csv
"""
import json
import numpy as np
import pandas as pd
import pycountry
from _est import fit
from _prep_airport import panel

bis = pd.read_csv("data_external/BIS_WS_XRU_monthly_avg.csv")
def a2to3(a):
    try:
        return pycountry.countries.get(alpha_2=a).alpha_3
    except Exception:
        return {"XK": "XKX"}.get(a)
bis["iso3"] = bis.iso2.map(a2to3)
bis = bis.dropna(subset=["iso3"])
bis = bis[bis.iso2 != "XM"]
fx = bis[["iso3", "t", "v"]].rename(columns={"t": "ym", "v": "e"})

wb = json.load(open("data_external/wb_cpi.json"))[1]
cpi = pd.DataFrame([(r["countryiso3code"], int(r["date"]), r["value"]) for r in wb if r["value"] is not None],
                   columns=["iso3", "year", "cpi"])
cpi = cpi[cpi.iso3.str.len() == 3]
months = pd.period_range("1994-01", "2024-12", freq="M")
rows = []
for c, g in cpi.groupby("iso3"):
    g = g.sort_values("year")
    x = (g.year - 1994) * 12 + 6.0                     # mid-year
    tt = np.arange(len(months))
    v = np.interp(tt, x.to_numpy(), np.log(g.cpi.to_numpy()), left=np.nan, right=np.nan)
    rows.append(pd.DataFrame({"iso3": c, "ym": months.astype(str), "lncpi_c": v}))
cpim = pd.concat(rows)
f = pd.read_csv("fuel_monthly.csv")[["ym", "cpi", "lnjet"]]
L = fx.merge(cpim, on=["iso3", "ym"], how="inner").merge(f, on="ym", how="inner")
L["lnq"] = np.log(L.e) + np.log(L.cpi) - L.lncpi_c
L["lnP_loc"] = L.lnjet + L.lnq
L = L.sort_values(["iso3", "ym"])
for v in ["lnq", "lnP_loc"]:
    L[v + "_l3"] = L.groupby("iso3")[v].shift(3)
    L["d12_" + v + "_l3"] = L[v + "_l3"] - L.groupby("iso3")[v + "_l3"].shift(12)
L.to_csv("local_fx_monthly.csv", index=False)
print("local FX panel: countries %d; months %s..%s" % (L.iso3.nunique(), L.ym.min(), L.ym.max()))

am = panel()
M = am[(am.year >= 1997) & (am.year <= 2019)].merge(L[["iso3", "ym", "d12_lnq_l3", "d12_lnP_loc_l3"]], on=["iso3", "ym"], how="left")
print("airport-months with local price: %s of %s; airports %d; countries %d"
      % (f"{M.d12_lnq_l3.notna().sum():,}", f"{len(M):,}", M.loc[M.d12_lnq_l3.notna(), 'airport_iata'].nunique(),
         M.loc[M.d12_lnq_l3.notna(), 'iso3'].nunique()))
VC = ("dk", "iso3", "t", 12)
ALT = [("cl", "iso3"), ("cl2", "iso3", "year")]
res = []
def rec(design, col, y, r, terms, labels, d, note=""):
    for t_, l_ in zip(terms, labels):
        res.append(dict(design=design, col=col, outcome=y, term=t_, label=l_, b=r["coef"][t_], se=r["se"][t_], p=r["p"][t_],
                        se_cl=r["alt"][0]["se"][t_], p_cl=r["alt"][0]["p"][t_], n=r["n"], n_air=d.airport_iata.nunique(),
                        n_c=d.iso3.nunique(), note=note))

for y in ["d12_ln_seats", "d12_ln_co2", "d12_ln_seats_dom", "d12_ln_seats_intl"]:
    d = M.dropna(subset=[y, "d12_lnP_loc_l3"]).copy()
    r = fit(d, y, exog=["d12_lnP_loc_l3"], fes=["airport_iata", "ym"], vc=VC, vc_alt=ALT)
    rec("L1 local real price, airport + month FE", "all countries", y, r, ["d12_lnP_loc_l3"], ["D12 ln local real jet price (t-3)"], d)
    for H, hl in [("z_fuelseat", "fuel burn per seat 1996 (z)"), ("H_g", "GACI 1996 (z)")]:
        for lab, dd in [("all countries", d), ("excl. |D12 ln q| > 0.5", d[d.d12_lnq_l3.abs() <= 0.5])]:
            dd = dd.dropna(subset=[H]).copy()
            dd["x_q"] = dd.d12_lnq_l3 * dd[H]
            dd["x_p"] = dd.d12_lnjet_l3 * dd[H]
            r = fit(dd, y, exog=["x_q", "x_p"], fes=["airport_iata", "iso_ym"], vc=VC, vc_alt=ALT)
            rec("L2 real exchange rate x exposure, airport + country x month FE", lab + "; exposure = " + hl, y, r,
                ["x_q", "x_p"], ["D12 ln real exchange rate (t-3) x exposure", "D12 ln USD jet price (t-3) x exposure"], dd)
    print(y, "done")
out = pd.DataFrame(res)
out.to_csv("_res_localfx.csv", index=False)
pd.set_option("display.width", 250)
print(out[["design", "col", "outcome", "label", "b", "se", "p", "p_cl", "n", "n_c"]].round(4).to_string(index=False))
