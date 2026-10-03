*==============================================================================
* co2_country_sizecheck2.do
* Decompose the size-x-cycle stress test: economic size (GDP, pop) vs
* aviation-capacity baseline (quasi-endogenous: GACI is built from capacity,
* so a_t x ln(cap96) partials out the treatment's own persistence).
* Also: baseline FS on the restricted 1996 sample for a fair comparison, and
* the headline 2SLS under the economic-size cycles.
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

gen tmp = ln(cap_sum) if y==1996
bysort isocode: egen lncap96 = max(tmp)
drop tmp
gen tmp = lngdp if y==1996
bysort isocode: egen lngdp96 = max(tmp)
drop tmp
gen tmp = lnpop if y==1996
bysort isocode: egen lnpop96 = max(tmp)
drop tmp

gen at_lncap = tour_shift * lncap96
gen at_lngdp = tour_shift * lngdp96
gen at_lnpop = tour_shift * lnpop96

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

gen byte s96 = !missing(lncap96, lngdp96, lnpop96)

reghdfe ln_gaci_cwm tourism_int lnpop if s96, absorb(isocode y) vce(robust)
test tourism_int
di "FS2 baseline (1996 sample):   pi = " %8.4f _b[tourism_int] "  F = " %7.1f r(F) "  N = " %8.0f e(N)

reghdfe ln_gaci_cwm tourism_int lnpop at_lnpop if s96, absorb(isocode y) vce(robust)
test tourism_int
di "FS2 + a_t x ln(pop96):        pi = " %8.4f _b[tourism_int] "  F = " %7.1f r(F)

reghdfe ln_gaci_cwm tourism_int lnpop at_lngdp if s96, absorb(isocode y) vce(robust)
test tourism_int
di "FS2 + a_t x ln(gdp96):        pi = " %8.4f _b[tourism_int] "  F = " %7.1f r(F)

reghdfe ln_gaci_cwm tourism_int lnpop at_lnpop at_lngdp if s96, absorb(isocode y) vce(robust)
test tourism_int
di "FS2 + pop96 + gdp96 cycles:   pi = " %8.4f _b[tourism_int] "  F = " %7.1f r(F)

reghdfe ln_gaci_cwm tourism_int lnpop at_lncap if s96, absorb(isocode y) vce(robust)
test tourism_int
di "FS2 + a_t x ln(cap96) only:   pi = " %8.4f _b[tourism_int] "  F = " %7.1f r(F)

* headline 2SLS under economic-size cycles (the fair exclusion-style control)
ivreghdfe ln_co2_bunker_intl lnpop at_lnpop at_lngdp (ln_gaci_cwm = tourism_int) if s96, absorb(isocode y) robust
di "2SLS intl + pop/gdp cycles:   b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat)

gen g_vol = merch_intensity + lngdp
ivreghdfe g_vol lnpop at_lnpop at_lngdp (ln_gaci_cwm = tourism_int) if s96, absorb(isocode y) robust
di "2SLS volume + pop/gdp cycles: b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat)

di _n "DONE_SIZECHECK2"
