* Geography x foreign-growth instruments for connectivity: over-identified 2SLS with cluster-robust Hansen J and
* weak-IV-robust (Anderson-Rubin) confidence sets. Data: tax_mediation_geo.dta (115_gaci_instrument_combo.py).
* v1 = ln sum S_j g_jt/d, v2 = .../d^2, v3 = ring 1,000 km; _l1 = one-year lags. Needs ivreghdfe, weakiv (ssc).
clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_tax"
cap log close
log using "tax_mediation_geo_run.log", replace text
foreach p in ftools reghdfe ivreghdfe weakiv {
    cap which `p'
    if _rc ssc install `p'
}
use "tax_mediation_geo.dta", clear
foreach m in ln_gaci ln_deg {
    di _n "==== M = `m': instruments v2 v3 ===="
    ivreghdfe ln_co2 tp bp (`m' = v2 v3), absorb(fe_u fe_t) cluster(iso3n) first
    cap noisily weakiv, level(95)
    di _n "==== M = `m': instruments v2 v3 + lags ===="
    ivreghdfe ln_co2 tp bp (`m' = v2 v3 v2_l1 v3_l1), absorb(fe_u fe_t) cluster(iso3n)
    cap noisily weakiv, level(95)
    di _n "==== M = `m': over-identified with the tax (v2 v3 tp), tp excluded ===="
    ivreghdfe ln_co2 bp (`m' = v2 v3 tp), absorb(fe_u fe_t) cluster(iso3n)
}
log close
