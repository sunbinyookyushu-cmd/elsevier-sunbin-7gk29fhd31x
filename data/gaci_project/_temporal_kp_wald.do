* Temporal interaction 2SLS: joint KP rk Wald F for tab:temporal
* Spec = test_temporal_sum.py (validated vs published 0.377***):
* outcome on (ln_gaci_cwm, ln_gaci_cwm x post2010) instrumented by
* (tourism_int, tourism_int x post2010), + lnpop, country & year FE, robust SE.
clear all
set more off
cap which ivreghdfe
di "ivreghdfe rc = " _rc
cap which ivreg2
di "ivreg2 rc = " _rc
cap which reghdfe
di "reghdfe rc = " _rc

import delimited "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\gaci_panel_3iv.csv", clear case(preserve)

foreach v in y ln_gaci_cwm lnG merch_intensity lngdp tourism_int lnpop {
    cap confirm numeric variable `v'
    if _rc destring `v', replace force
}
gen g_int = merch_intensity
gen g_vol = merch_intensity + lngdp
gen g_gdp = lngdp
gen post = (y >= 2010)
gen tr_post = ln_gaci_cwm * post
gen z_post  = tourism_int * post
egen cid = group(c)

* sample identical to the published run (includes lnG in the dropna set)
drop if missing(ln_gaci_cwm, lnG, tourism_int, lnpop, merch_intensity, lngdp)

foreach o in g_int g_vol g_gdp {
    di _n "==== OUTCOME: `o' ===="
    ivreghdfe `o' lnpop (ln_gaci_cwm tr_post = tourism_int z_post), absorb(cid y) robust
    di "KP rk Wald F = " e(widstat) "   N = " e(N)
}
