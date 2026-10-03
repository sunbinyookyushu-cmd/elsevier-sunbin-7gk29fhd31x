*==============================================================================
* co2_ext4.do
* Spillover mechanism: what margin of OWN aviation responds to NEIGHBOUR
* connectivity? (neighbour-endogenous spec of co2_ext3.do)
* outcomes: flights, seat-km, gauge, stage, intl share
* -> _spillover_mech.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker dep_seat_km n_dep_flights dep_seats dep_seat_km_intl
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "spillover_vars.csv", clear varnames(1) encoding("utf-8")
tempfile sp
save `sp'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `sp', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_flights = ln(n_dep_flights) if n_dep_flights > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_gauge = ln(dep_seats/n_dep_flights) if n_dep_flights > 0 & dep_seats > 0
gen ln_stage = ln(dep_seat_km/dep_seats) if dep_seats > 0 & dep_seat_km > 0
gen intl_share = dep_seat_km_intl/dep_seat_km if dep_seat_km > 0
replace intl_share = 1 if intl_share > 1 & !missing(intl_share)

tempname S
postfile `S' str16 outc double(b se p kpf) long(nn) using "_spm_tmp", replace
foreach yv in ln_flights ln_skm ln_gauge ln_stage intl_share {
    quietly ivreghdfe `yv' feyrer_int lnpop ln_sea_ma (nbr_lngaci = nbr_feyrer), absorb(isocode y) robust
    local bb = _b[nbr_lngaci]
    local ss = _se[nbr_lngaci]
    di "SPM `yv': b=" %8.3f `bb' " se=" %8.3f `ss' " F=" %7.1f e(widstat)
    post `S' ("`yv'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
}
postclose `S'
preserve
use "_spm_tmp", clear
list, clean
export delimited "_spillover_mech.csv", replace
restore
erase "_spm_tmp.dta"

di _n "DONE_EXT4"
