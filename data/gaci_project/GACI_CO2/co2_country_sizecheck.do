*==============================================================================
* co2_country_sizecheck.do
* Fairness check: apply the size-x-cycle test that killed the airport heritage
* IV to the COUNTRY tourism instrument. If tourism_int only proxies "big
* aviation country x global cycle", controlling a_t x baseline size should
* kill the first stage. Baselines (1996): ln total seat capacity, ln GDP,
* ln number of airports. Then: does the headline 2SLS (intl CO2) survive?
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "gaci_co2_panel.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

* 1996 baselines
gen tmp = ln(cap_sum) if y==1996
bysort isocode: egen lncap96 = max(tmp)
drop tmp
gen tmp = lngdp if y==1996
bysort isocode: egen lngdp96 = max(tmp)
drop tmp
gen tmp = ln(n_air) if y==1996
bysort isocode: egen lnnair96 = max(tmp)
drop tmp

gen at_lncap = tour_shift * lncap96
gen at_lngdp = tour_shift * lngdp96
gen at_lnnair = tour_shift * lnnair96

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

* ---- first stage under size-x-cycle controls ----
reghdfe ln_gaci_cwm tourism_int lnpop, absorb(isocode y) vce(robust)
test tourism_int
di "CTRY FS baseline:                 pi = " %8.4f _b[tourism_int] " (se " %7.4f _se[tourism_int] ")  F = " %7.1f r(F) "  N = " %8.0f e(N)

reghdfe ln_gaci_cwm tourism_int lnpop at_lncap, absorb(isocode y) vce(robust)
test tourism_int
di "CTRY FS + a_t x ln(cap96):        pi = " %8.4f _b[tourism_int] " (se " %7.4f _se[tourism_int] ")  F = " %7.1f r(F) "  N = " %8.0f e(N)

reghdfe ln_gaci_cwm tourism_int lnpop at_lncap at_lngdp, absorb(isocode y) vce(robust)
test tourism_int
di "CTRY FS + cap96 + gdp96 cycles:   pi = " %8.4f _b[tourism_int] " (se " %7.4f _se[tourism_int] ")  F = " %7.1f r(F) "  N = " %8.0f e(N)

reghdfe ln_gaci_cwm tourism_int lnpop at_lncap at_lngdp at_lnnair, absorb(isocode y) vce(robust)
test tourism_int
di "CTRY FS + all three size cycles:  pi = " %8.4f _b[tourism_int] " (se " %7.4f _se[tourism_int] ")  F = " %7.1f r(F) "  N = " %8.0f e(N)

* ---- headline 2SLS under the toughest control set ----
ivreghdfe ln_co2_bunker_intl lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
di "CTRY 2SLS intl baseline:          b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat)

ivreghdfe ln_co2_bunker_intl lnpop at_lncap at_lngdp at_lnnair (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
di "CTRY 2SLS intl + size cycles:     b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat)

* trade outcome for symmetry (openness + volume)
gen g_vol = merch_intensity + lngdp
ivreghdfe g_vol lnpop at_lncap at_lngdp at_lnnair (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
di "CTRY 2SLS trade volume + cycles:  b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat)

di _n "DONE_SIZECHECK"
