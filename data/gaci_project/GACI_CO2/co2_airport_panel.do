*==============================================================================
* co2_airport_panel.do
* Airport-level panel regressions (descriptive, no IV): does an airport's
* network position track its emissions, traffic, intensity, and intl share?
*   Spec 1: airport FE + year FE
*   Spec 2: airport FE + country x year FE  (within-country identification:
*           national shocks, policy, macro absorbed)
* Outcomes: ln CO2 (bunker), ln seat-km, ln intensity, intl share of seat-km.
* SE clustered by airport.
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "airport_co2_panel.csv", clear varnames(1) encoding("utf-8")
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

foreach yv in ln_co2 ln_skm ln_intensity intl_share_skm {
    reghdfe `yv' ln_gaci, absorb(apid year) vce(cluster apid)
    local b1 = _b[ln_gaci]
    local s1 = _se[ln_gaci]
    local n1 = e(N)
    reghdfe `yv' ln_gaci, absorb(apid cyr) vce(cluster apid)
    di "AIRPORT `yv': ap+yr FE b = " %8.4f `b1' " (se " %7.4f `s1' ", N " %9.0f `n1' ")   ap+ctry-x-yr FE b = " %8.4f _b[ln_gaci] " (se " %7.4f _se[ln_gaci] ", N " %9.0f e(N) ")"
}

di _n "DONE_AIRPORT_PANEL"
