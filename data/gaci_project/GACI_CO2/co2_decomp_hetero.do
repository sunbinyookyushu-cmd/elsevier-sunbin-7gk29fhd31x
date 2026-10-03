*==============================================================================
* co2_decomp_hetero.do   (LZ comment 1, 2026-09-03)
* Identity decomposition of the CO2 elasticity, extended:
*   (A) by baseline income tercile (split samples, common sample per block)
*   (B) by baseline connectivity tercile
*   (C) international vs domestic segment (each its own identity)
* Identity per segment S:  CO2_S = flights_S x (seats/flight)_S x (km/seat)_S
*                                   x (CO2/seat-km)_S
* Spec: ivreghdfe y lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
* Exports: _decomp_hetero.csv (block, grp, seg, outc, b, se, p, kpf, nn)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl dep_seat_km n_dep_flights dep_seats n_dep_flights_intl dep_seats_intl dep_seat_km_intl
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

* ---- segments: tot / intl / dom ----
gen co2_dom = co2_bunker - co2_bunker_intl
gen fl_dom = n_dep_flights - n_dep_flights_intl
gen st_dom = dep_seats - dep_seats_intl
gen skm_dom = dep_seat_km - dep_seat_km_intl

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_flights_tot = ln(n_dep_flights) if n_dep_flights > 0
gen ln_gauge_tot = ln(dep_seats/n_dep_flights) if n_dep_flights > 0 & dep_seats > 0
gen ln_stage_tot = ln(dep_seat_km/dep_seats) if dep_seats > 0 & dep_seat_km > 0
gen ln_intensity_tot = ln(co2_bunker/dep_seat_km) if co2_bunker > 0 & dep_seat_km > 0

gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen ln_flights_intl = ln(n_dep_flights_intl) if n_dep_flights_intl > 0
gen ln_gauge_intl = ln(dep_seats_intl/n_dep_flights_intl) if n_dep_flights_intl > 0 & dep_seats_intl > 0
gen ln_stage_intl = ln(dep_seat_km_intl/dep_seats_intl) if dep_seats_intl > 0 & dep_seat_km_intl > 0
gen ln_intensity_intl = ln(co2_bunker_intl/dep_seat_km_intl) if co2_bunker_intl > 0 & dep_seat_km_intl > 0

gen ln_co2_dom = ln(co2_dom) if co2_dom > 0
gen ln_flights_dom = ln(fl_dom) if fl_dom > 0
gen ln_gauge_dom = ln(st_dom/fl_dom) if fl_dom > 0 & st_dom > 0
gen ln_stage_dom = ln(skm_dom/st_dom) if st_dom > 0 & skm_dom > 0
gen ln_intensity_dom = ln(co2_dom/skm_dom) if co2_dom > 0 & skm_dom > 0

* ---- baseline groups (as in co2_feyrer_hetero.do) ----
bysort isocode (y): gen byte first_pc = sum(!missing(lnpc)) == 1 & !missing(lnpc)
gen lnpc0_ = lnpc if first_pc
bysort isocode (lnpc0_): gen lnpc0 = lnpc0_[1]
drop lnpc0_ first_pc
bysort isocode (y): gen byte first_g = sum(!missing(gaci_cwmean)) == 1 & !missing(gaci_cwmean)
gen g0_ = gaci_cwmean if first_g
bysort isocode (g0_): gen gaci0 = g0_[1]
drop g0_ first_g
preserve
bysort isocode: keep if _n == 1
xtile inc3 = lnpc0, nq(3)
xtile con3 = gaci0, nq(3)
keep isocode inc3 con3
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

* common samples per segment
foreach S in tot intl dom {
    gen byte ok_`S' = !missing(ln_co2_`S') & !missing(ln_flights_`S') & !missing(ln_gauge_`S') & !missing(ln_stage_`S') & !missing(ln_intensity_`S') & !missing(lnpop) & !missing(ln_sea_ma) & !missing(feyrer_int) & !missing(ln_gaci_cwm)
}

tempname M
postfile `M' str12 block str12 grp str6 seg str16 outc double(b se p kpf) long(nn) using "_decomp_tmp", replace

program define runblock
    args block grp seg cond
    foreach comp in co2 flights gauge stage intensity {
        quietly ivreghdfe ln_`comp'_`seg' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if ok_`seg' & (`cond'), absorb(isocode y) robust
        local bb = _b[ln_gaci_cwm]
        local sse = _se[ln_gaci_cwm]
        local pp = 2*normal(-abs(`bb'/`sse'))
        di "DECOMP `block' `grp' `seg' `comp': b = " %9.3f `bb' " (se " %8.3f `sse' ")  KP F = " %7.1f e(widstat) "  N = " %8.0f e(N)
        post $MH ("`block'") ("`grp'") ("`seg'") ("ln_`comp'") (`bb') (`sse') (`pp') (e(widstat)) (e(N))
    }
end
global MH `M'

* (A) income terciles, total segment
runblock A_income all tot "1==1"
runblock A_income inc_low tot "inc3==1"
runblock A_income inc_mid tot "inc3==2"
runblock A_income inc_high tot "inc3==3"
* (B) connectivity terciles, total segment
runblock B_conn con_low tot "con3==1"
runblock B_conn con_mid tot "con3==2"
runblock B_conn con_high tot "con3==3"
* (C) segments, full sample
runblock C_segment all intl "1==1"
runblock C_segment all dom "1==1"
* (C2) segments by income (low vs high) for the international segment
runblock C_segment inc_low intl "inc3==1"
runblock C_segment inc_high intl "inc3==3"

postclose `M'
preserve
use "_decomp_tmp", clear
list, clean noobs
export delimited "_decomp_hetero.csv", replace
restore
erase "_decomp_tmp.dta"

di _n "DONE_DECOMP_HETERO"
