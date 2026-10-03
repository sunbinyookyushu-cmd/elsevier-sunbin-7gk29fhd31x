*==============================================================================
* co2_feyrer_intl.do
* Decisive check: does the CO2 headline (ln intl bunker CO2) hold under the
* Feyrer air/sea IV, which survives all size-x-cycle stress tests?
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl co2_lto dep_seat_km
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_intensity = ln(co2_bunker) - ln(dep_seat_km) if co2_bunker > 0 & dep_seat_km > 0

gen tmp = lngdp if y==1996
bysort isocode: egen lngdp96 = max(tmp)
drop tmp
gen tmp = lnpop if y==1996
bysort isocode: egen lnpop96 = max(tmp)
drop tmp
gen at_lngdp = tour_shift * lngdp96
gen at_lnpop = tour_shift * lnpop96

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

foreach yv in ln_co2_intl ln_co2_tot ln_intensity {
    ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    di "FEYCO2 `yv' baseline:      b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %8.1f e(widstat) "  N = " %8.0f e(N)
    ivreghdfe `yv' lnpop ln_sea_ma at_lnpop at_lngdp (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    di "FEYCO2 `yv' + size cycles: b = " %8.3f _b[ln_gaci_cwm] " (se " %7.3f _se[ln_gaci_cwm] ")  KP F = " %8.1f e(widstat) "  N = " %8.0f e(N)
}

di _n "DONE_FEYCO2"
