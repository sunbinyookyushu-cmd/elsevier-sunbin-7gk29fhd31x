*==============================================================================
* co2_hiv_fs3.do
* CRITICAL CHECK on the gateway heritage instrument: does z_gw survive
* size-x-cycle controls? If z_gw only proxies "big airport x aviation boom",
* controlling a_t x ln(1996 capacity) and a_t x gateway-dummy should kill it.
* Sample: airports observed in 1996 (cap96 nonmissing). FE: airport + country
* x year. Cluster by airport.
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "airport_hiv_panel3.csv", clear varnames(1) encoding("utf-8")
ds airport_iata iso3 region, not
destring `r(varlist)', replace force
encode airport_iata, gen(apid)
encode iso3, gen(cid)
egen cyr = group(cid year)
keep if !missing(ln_cap96)

gen at_lncap = a_t * ln_cap96
gen at_gwdum = a_t * gw_dum

capture which reghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
}

reghdfe ln_gaci z_gw, absorb(apid cyr) vce(cluster apid)
test z_gw
di "FS3 baseline (1996 sample):        b = " %8.4f _b[z_gw] " (se " %7.4f _se[z_gw] ")  F = " %8.1f r(F) "  N = " %9.0f e(N)

reghdfe ln_gaci z_gw at_lncap, absorb(apid cyr) vce(cluster apid)
test z_gw
di "FS3 + a_t x ln(cap96):             b = " %8.4f _b[z_gw] " (se " %7.4f _se[z_gw] ")  F = " %8.1f r(F) "  N = " %9.0f e(N)

reghdfe ln_gaci z_gw at_lncap at_gwdum, absorb(apid cyr) vce(cluster apid)
test z_gw
di "FS3 + a_t x ln(cap96) + a_t x gw:  b = " %8.4f _b[z_gw] " (se " %7.4f _se[z_gw] ")  F = " %8.1f r(F) "  N = " %9.0f e(N)

di _n "DONE_FS3"
