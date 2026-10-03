# -*- coding: utf-8 -*-
"""Export the annual tax stacks for IV mediation in Stata (user 2026-10-03): tax -> network (destinations / GACI) -> CO2.
Same stacks as 105 (8 European events, years E-3..E, airport x event and year x event FE, border 50-300 km group).
Variables: ln_co2, ln_int (CO2 per seat-km), ln_deg, ln_gaci, tp (treated x post), bp, dose_post (EUR per departing
passenger at the airport's pre-year distance band x post; the continuous treatment that tp instruments in ivmediate),
size tercile dummies, fe_u / fe_t integer ids, iso3n.
Output: stata_tax/tax_mediation.dta ; do-file stata_tax/tax_mediation.do
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import os
import warnings

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

warnings.filterwarnings("ignore")
EV = pd.DataFrame([("IRL", "2009-03-30", "2008-10-01"), ("DEU", "2011-01-01", "2010-06-01"), ("AUT", "2011-04-01", "2010-10-01"),
                   ("NOR", "2016-06-01", "2015-12-01"), ("SWE", "2018-04-01", "2017-06-01"), ("GBR", "2007-02-01", "2006-12-01"),
                   ("DNK", "1998-01-01", "1997-05-01"), ("MLT", "2005-08-01", "2004-11-01")], columns=["iso3", "eff", "ann"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
EV["E"] = np.where(pd.to_datetime(EV.eff).dt.month <= 6, pd.to_datetime(EV.eff).dt.year, pd.to_datetime(EV.eff).dt.year + 1)
EV["pre_year"] = (EV.tA - 13) // 12
BANDS = {"DEU": [(2500, 8), (6000, 25), (1e9, 45)], "AUT": [(2500, 8), (6000, 20), (1e9, 35)], "IRL": [(300, 2), (1e9, 10)],
         "SWE": [(2500, 6.2), (6000, 25.8), (1e9, 41.2)], "NOR": [(1e9, 8.6)], "GBR": [(2500, 7.4), (1e9, 29.6)], "DNK": [(1e9, 10.1)], "MLT": [(1e9, 23.3)]}
CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"), pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "dep_seats", "n_dep_flights", "dep_seat_km", "co2_dep"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019)]
ya = am.groupby(["airport_iata", "year"], as_index=False).agg(iso3=("iso3", "first"), seats=("dep_seats", "sum"), fl=("n_dep_flights", "sum"), skm=("dep_seat_km", "sum"), co2=("co2_dep", "sum"))
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "GACI", "Degree"])
ya = ya.merge(hp, on=["airport_iata", "year"], how="left")
ya = ya[(ya.seats > 0) & (ya.co2 > 0) & (ya.fl > 0) & (ya.Degree > 0) & (ya.GACI > 0)].copy()
ya["ln_co2"], ya["ln_deg"], ya["ln_gaci"] = np.log(ya.co2), np.log(ya.Degree), np.log(ya.GACI)
ya["ln_int"], ya["stage"] = np.log(ya.co2 / ya.skm), ya.skm / ya.seats
cb = pd.read_csv("crossborder_pairs.csv")
out = []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(ya[ya.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (CODED - {"ITA", ev.iso3}) - busy
    b0 = ya[ya.year == ev.pre_year].set_index("airport_iata")
    d = ya[(ya.iso3.isin(ctrl | {ev.iso3}) | ya.airport_iata.isin(nb.index)) & (ya.year >= ev.E - 3) & (ya.year <= ev.E)].copy()
    km = d.airport_iata.map(nb)
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
    d = d[d.grp != "B50"]
    tsz = pd.qcut(b0.seats.reindex(list(tre)).dropna(), 3, labels=["small", "mid", "large"])
    d["size"] = d.airport_iata.map(tsz).astype(object).where(d.grp == "T", "ctrl")
    d["stage0"] = d.airport_iata.map(b0.stage)
    d["dose"] = np.where(d.grp == "T", [next(v for lim, v in BANDS[ev.iso3] if s <= lim) if pd.notna(s) else np.nan for s in d.stage0], 0.0)
    d["post"], d["stk"] = (d.year >= ev.E).astype(np.int8), k
    out.append(d)
Y = pd.concat(out, ignore_index=True)
Y["tp"] = ((Y.grp == "T") & (Y.post == 1)).astype(np.int8)
Y["bp"] = ((Y.grp == "B") & (Y.post == 1)).astype(np.int8)
Y["dose_post"] = (Y.dose.fillna(0) * Y.post).astype(float)
for s in ["small", "mid", "large"]:
    Y[f"sz_{s}"] = (Y["size"] == s).astype(np.int8)
    Y[f"tp_{s}"] = (Y[f"sz_{s}"] * Y.post).astype(np.int8)
Y["fe_u"] = pd.factorize(Y.airport_iata + "_" + Y.stk.astype(str))[0] + 1
Y["fe_t"] = pd.factorize(Y.year.astype(str) + "_" + Y.stk.astype(str))[0] + 1
Y["iso3n"] = pd.factorize(Y.iso3)[0] + 1
Y["treated"] = (Y.grp == "T").astype(np.int8)
cols = ["airport_iata", "iso3", "iso3n", "stk", "year", "treated", "post", "tp", "bp", "dose_post", "sz_small", "sz_mid", "sz_large",
        "tp_small", "tp_mid", "tp_large", "ln_co2", "ln_int", "ln_deg", "ln_gaci", "fe_u", "fe_t"]
os.makedirs("stata_tax", exist_ok=True)
Y[cols].rename(columns={"airport_iata": "airport"}).to_stata("stata_tax/tax_mediation.dta", write_index=False, version=118)
print("rows", len(Y), "treated airport-years", int(Y.treated.sum()), "events", Y.stk.nunique(), "countries", Y.iso3.nunique())
do = r"""* =====================================================================
* Tax -> network position -> CO2: IV mediation (Dippel, Ferrara and Heblich 2020, ivmediate) and Gelbach check
* Data: tax_mediation.dta (112_export_mediation.py): annual stacks, 8 European tax increases, years E-3..E
*   Y = ln_co2 (also ln_int = CO2 per seat-km); M = ln_deg (destinations; also ln_gaci)
*   Treatment = dose_post (EUR per departing passenger x post, continuous); instrument = tp (treated x post)
*   Exogenous: bp (border x post). FE: airport x event (fe_u, absorbed), year x event (fe_t, dummies)
*   Identification needs the tax to move CO2 only through the network margin once the mediator is accounted for;
*   the exact decomposition (flights per destination and CO2 per flight do not move) is the supporting evidence.
* Needs: ivmediate (ssc), ivreghdfe, reghdfe, ftools
* =====================================================================
clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_tax"
cap log close
log using "tax_mediation_run.log", replace text
foreach p in ftools reghdfe ivreghdfe ivmediate {
    cap which `p'
    if _rc ssc install `p'
}
use "tax_mediation.dta", clear
describe, short
tab stk treated if post == 1

* ---------- A. ivmediate: all treated airports ----------
foreach m in ln_deg ln_gaci {
    di _n "==== ivmediate: Y = ln_co2, M = `m' ===="
    ivmediate ln_co2 bp i.fe_t, mediator(`m') treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
    di _n "==== ivmediate: Y = ln_int (CO2 per seat-km), M = `m' ===="
    ivmediate ln_int bp i.fe_t, mediator(`m') treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
}

* ---------- B. ivmediate by size tercile (treated airports of one tercile vs all controls) ----------
foreach s in small mid large {
    preserve
    keep if treated == 0 | sz_`s' == 1
    di _n "==== ivmediate, `s' airports: Y = ln_co2, M = ln_deg ===="
    cap noisily ivmediate ln_co2 bp i.fe_t, mediator(ln_deg) treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
    restore
}

* ---------- C. Manual three-step (conservative, mediator as control) ----------
* total:   Y on tp;  mediator: M on tp;  direct: Y on tp and M;  indirect = total - direct (Gelbach identity)
foreach m in ln_deg ln_gaci {
    reghdfe ln_co2 tp bp, absorb(fe_u fe_t) vce(cluster iso3n)
    scalar tot_`m' = _b[tp]
    reghdfe `m' tp bp, absorb(fe_u fe_t) vce(cluster iso3n)
    scalar pi_`m' = _b[tp]
    reghdfe ln_co2 tp bp `m', absorb(fe_u fe_t) vce(cluster iso3n)
    scalar dir_`m' = _b[tp]
    scalar beta_`m' = _b[`m']
    di _n "Gelbach, M = `m': total " tot_`m' "  direct " dir_`m' "  indirect " tot_`m' - dir_`m' "  (= pi " pi_`m' " x beta " beta_`m' ")"  "  share " (tot_`m' - dir_`m') / tot_`m'
}

* ---------- D. 2SLS of CO2 on the mediator with tp as the instrument (the M -> Y link under exclusion) ----------
foreach m in ln_deg ln_gaci {
    ivreghdfe ln_co2 bp (`m' = tp), absorb(fe_u fe_t) cluster(iso3n)
    ivreghdfe ln_int bp (`m' = tp), absorb(fe_u fe_t) cluster(iso3n)
}
log close
"""
with open("stata_tax/tax_mediation.do", "wb") as fh:
    fh.write(do.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
print("wrote stata_tax/tax_mediation.do")
