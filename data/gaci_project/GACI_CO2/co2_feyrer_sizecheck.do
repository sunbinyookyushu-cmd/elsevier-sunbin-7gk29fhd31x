*==============================================================================
* co2_feyrer_sizecheck.do
* Same size-x-cycle stress test on the INDEPENDENT Feyrer-type air/sea IV
* (feyrer_int = a_t x ln air market access 1996). If this survives, the trade
* volume result keeps one identification leg under the toughest critique.
* Data: gaci_panel_combined.csv (has feyrer_int, ln_sea_ma).
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"

import delimited "gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen g_vol = merch_intensity + lngdp
gen tmp = ln(cap_sum) if y==1996
bysort isocode: egen lncap96 = max(tmp)
drop tmp
gen tmp = lngdp if y==1996
bysort isocode: egen lngdp96 = max(tmp)
drop tmp
gen tmp = lnpop if y==1996
bysort isocode: egen lnpop96 = max(tmp)
drop tmp

gen at_lngdp = tour_shift * lngdp96
gen at_lnpop = tour_shift * lnpop96
gen at_lncap = tour_shift * lncap96
gen byte s96 = !missing(lngdp96, lnpop96, lncap96)

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

reghdfe ln_gaci_cwm feyrer_int lnpop ln_sea_ma if s96, absorb(isocode y) vce(robust)
test feyrer_int
di "FEY FS baseline:              pi = " %8.4f _b[feyrer_int] "  F = " %8.1f r(F) "  N = " %8.0f e(N)

reghdfe ln_gaci_cwm feyrer_int lnpop ln_sea_ma at_lnpop at_lngdp if s96, absorb(isocode y) vce(robust)
test feyrer_int
di "FEY FS + pop/gdp cycles:      pi = " %8.4f _b[feyrer_int] "  F = " %8.1f r(F)

reghdfe ln_gaci_cwm feyrer_int lnpop ln_sea_ma at_lnpop at_lngdp at_lncap if s96, absorb(isocode y) vce(robust)
test feyrer_int
di "FEY FS + all size cycles:     pi = " %8.4f _b[feyrer_int] "  F = " %8.1f r(F)

ivreghdfe g_vol lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if s96, absorb(isocode y) robust
di "FEY 2SLS vol baseline:        b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %8.1f e(widstat)

ivreghdfe g_vol lnpop ln_sea_ma at_lnpop at_lngdp (ln_gaci_cwm = feyrer_int) if s96, absorb(isocode y) robust
di "FEY 2SLS vol + pop/gdp:       b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %8.1f e(widstat)

ivreghdfe g_vol lnpop ln_sea_ma at_lnpop at_lngdp at_lncap (ln_gaci_cwm = feyrer_int) if s96, absorb(isocode y) robust
di "FEY 2SLS vol + all cycles:    b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %8.1f e(widstat)

di _n "DONE_FEYCHECK"
