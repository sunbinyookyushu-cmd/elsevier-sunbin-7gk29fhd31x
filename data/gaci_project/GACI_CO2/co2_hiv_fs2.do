*==============================================================================
* co2_hiv_firststage.do
* PILOT: first stage of the airport-level heritage-proximity instrument.
*   z_jt = a_t (global tourism cycle) x fixed natural+mixed-site exposure of
*   airport j (n100 / n200 / inverse-distance within 300km).
*   Spec 1: airport FE + year FE           (cross-country + within variation)
*   Spec 2: airport FE + country x year FE (within-country only, demanding)
*   SE clustered by airport; F = cluster-robust F on the instrument.
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "airport_hiv_panel2.csv", clear varnames(1) encoding("utf-8")
ds airport_iata iso3 region, not
destring `r(varlist)', replace force
encode airport_iata, gen(apid)
encode iso3, gen(cid)
egen cyr = group(cid year)

capture which reghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
}

foreach z in z_gw z_n200 {
    reghdfe ln_gaci `z', absorb(apid year) vce(cluster apid)
    test `z'
    local f1 = r(F)
    local b1 = _b[`z']
    local s1 = _se[`z']
    local n1 = e(N)
    reghdfe ln_gaci `z', absorb(apid cyr) vce(cluster apid)
    test `z'
    di "FS `z': ap+yr  b = " %9.4f `b1' " (se " %8.4f `s1' ")  F = " %8.1f `f1' " N = " %9.0f `n1'
    di "FS `z': ap+cxy b = " %9.4f _b[`z'] " (se " %8.4f _se[`z'] ")  F = " %8.1f r(F) " N = " %9.0f e(N)
}

* horse race: all three (collinearity check)
reghdfe ln_gaci z_gw z_n200, absorb(apid cyr) vce(cluster apid)
test z_gw z_n200
di "JOINT (ap+cxy): F = " %8.1f r(F)

di _n "DONE_HIV_FS"
