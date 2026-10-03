*==============================================================================
* co2_yifu_suite.do   (Yifu comments 1 and 4, 2026-09-03)
*   A  functional form: log-log (reference), semi-log (ln CO2 on GACI level),
*      level-level (CO2 Mt on GACI level), lin-log (CO2 Mt on ln GACI);
*      semi-log split by baseline-connectivity tercile
*   B  continuous heterogeneity by baseline connectivity: quintile splits
*      (log-log and semi-log) and pooled flexible interactions of ln GACI with
*      centred log baseline GACI (linear, quadratic), instruments interacted
*      identically; coefficient covariances posted for delta-method curves
*   C  sample moments for implied elasticities
* Spec: ivreghdfe y lnpop ln_sea_ma (x = z), absorb(isocode y) robust
* Export: _yifu_suite.csv (panel item var b se p kpf nn v12 v22 v13 v23 v33)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl dep_seat_km
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

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen co2_mt = co2_bunker/1e9
gen gaci = gaci_cwmean
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm

* baseline connectivity (earliest observed), centred log
bysort isocode (y): gen byte first_g = sum(!missing(gaci_cwmean)) == 1 & !missing(gaci_cwmean)
gen g0_ = gaci_cwmean if first_g
bysort isocode (g0_): gen gaci0 = g0_[1]
drop g0_ first_g
gen lg0 = ln(gaci0)
preserve
bysort isocode: keep if _n == 1
xtile con3 = gaci0, nq(3)
xtile con5 = gaci0, nq(5)
summarize lg0
local m0 = r(mean)
keep isocode con3 con5
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate
gen dev = lg0 - `m0'
gen dev2 = dev^2
gen x_dev = ln_gaci_cwm * dev
gen x_dev2 = ln_gaci_cwm * dev2
gen z_dev = feyrer_int * dev
gen z_dev2 = feyrer_int * dev2
gen g_dev = gaci * dev
gen zg_dev = feyrer_int * dev

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

tempname R
postfile `R' str10 panel str24 item str14 var double(b se p kpf) long(nn) double(v12 v22 v13 v23 v33) using "_yifu_tmp", replace
global RH `R'
program define postone
    args panel item v kpf
    local bb = _b[`v']
    local sse = _se[`v']
    local pp = 2*normal(-abs(`bb'/`sse'))
    di "YIFU [`panel'] `item' `v': b = " %10.4f `bb' " (se " %9.4f `sse' ")  KP F = " %7.1f `kpf' "  N = " %7.0f e(N)
    post $RH ("`panel'") ("`item'") ("`v'") (`bb') (`sse') (`pp') (`kpf') (e(N)) (.) (.) (.) (.) (.)
end

* =====================================================================
* C) sample moments (posted as rows; b = value)
* =====================================================================
gen byte insamp = !missing(ln_co2_tot, ln_gaci_cwm, feyrer_int, lnpop, ln_sea_ma)
foreach v in gaci co2_mt ln_gaci_cwm gaci0 lg0 {
    quietly summarize `v' if insamp, detail
    post $RH ("C") ("moment_`v'") ("mean") (r(mean)) (r(sd)) (.) (.) (r(N)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90))
    di "MOMENT `v': mean " %9.4f r(mean) "  p10 " %9.4f r(p10) "  p50 " %9.4f r(p50) "  p90 " %9.4f r(p90)
}
quietly summarize dev if insamp, detail
post $RH ("C") ("moment_dev") ("mean") (r(mean)) (r(sd)) (.) (.) (r(N)) (r(p10)) (r(p25)) (r(p50)) (r(p75)) (r(p90))
di "centre lg0 mean = " %8.4f `m0'
post $RH ("C") ("centre_lg0") ("m0") (`m0') (.) (.) (.) (.) (.) (.) (.) (.) (.)

* =====================================================================
* A) functional forms
* =====================================================================
di _n "===== A) functional forms ====="
ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
postone A loglog ln_gaci_cwm e(widstat)
ivreghdfe ln_co2_tot lnpop ln_sea_ma (gaci = feyrer_int), absorb(isocode y) robust
postone A semilog gaci e(widstat)
ivreghdfe co2_mt lnpop ln_sea_ma (gaci = feyrer_int), absorb(isocode y) robust
postone A levellevel gaci e(widstat)
ivreghdfe co2_mt lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
postone A linlog ln_gaci_cwm e(widstat)
* OLS counterparts
reghdfe ln_co2_tot ln_gaci_cwm lnpop ln_sea_ma, absorb(isocode y) vce(robust)
postone A ols_loglog ln_gaci_cwm .
reghdfe ln_co2_tot gaci lnpop ln_sea_ma, absorb(isocode y) vce(robust)
postone A ols_semilog gaci .
reghdfe co2_mt gaci lnpop ln_sea_ma, absorb(isocode y) vce(robust)
postone A ols_levellevel gaci .
* semi-log and log-log by baseline-connectivity tercile
foreach g in 1 2 3 {
    capture noisily ivreghdfe ln_co2_tot lnpop ln_sea_ma (gaci = feyrer_int) if con3 == `g', absorb(isocode y) robust
    if _rc == 0 postone A semilog_con`g' gaci e(widstat)
    capture noisily ivreghdfe co2_mt lnpop ln_sea_ma (gaci = feyrer_int) if con3 == `g', absorb(isocode y) robust
    if _rc == 0 postone A level_con`g' gaci e(widstat)
    quietly summarize gaci if con3 == `g' & insamp
    post $RH ("A") ("meangaci_con`g'") ("mean") (r(mean)) (r(sd)) (.) (.) (r(N)) (.) (.) (.) (.) (.)
    quietly summarize co2_mt if con3 == `g' & insamp
    post $RH ("A") ("meanco2_con`g'") ("mean") (r(mean)) (r(sd)) (.) (.) (r(N)) (.) (.) (.) (.) (.)
}

* =====================================================================
* B) continuous heterogeneity by baseline connectivity
* =====================================================================
di _n "===== B) quintiles ====="
foreach q in 1 2 3 4 5 {
    capture noisily ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if con5 == `q', absorb(isocode y) robust
    if _rc == 0 postone B q`q'_loglog ln_gaci_cwm e(widstat)
    capture noisily ivreghdfe ln_co2_tot lnpop ln_sea_ma (gaci = feyrer_int) if con5 == `q', absorb(isocode y) robust
    if _rc == 0 postone B q`q'_semilog gaci e(widstat)
    quietly summarize gaci0 if con5 == `q' & insamp
    post $RH ("B") ("q`q'_gaci0") ("mean") (r(mean)) (r(sd)) (.) (.) (r(N)) (r(min)) (.) (.) (.) (r(max))
    quietly summarize gaci if con5 == `q' & insamp
    post $RH ("B") ("q`q'_gaci") ("mean") (r(mean)) (r(sd)) (.) (.) (r(N)) (.) (.) (.) (.) (.)
}
di _n "===== B) flexible interactions ====="
* linear interaction, log-log
ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm x_dev = feyrer_int z_dev), absorb(isocode y) robust
matrix V = e(V)
local v11 = V[1,1]
local v12 = V[1,2]
local v22 = V[2,2]
di "INT-LIN: b1 = " %8.4f _b[ln_gaci_cwm] " (se " %7.4f _se[ln_gaci_cwm] ")  b2 = " %8.4f _b[x_dev] " (se " %7.4f _se[x_dev] ")  KP F = " %7.1f e(widstat)
post $RH ("B") ("int_lin") ("ln_gaci_cwm") (_b[ln_gaci_cwm]) (_se[ln_gaci_cwm]) (2*normal(-abs(_b[ln_gaci_cwm]/_se[ln_gaci_cwm]))) (e(widstat)) (e(N)) (`v12') (`v22') (.) (.) (.)
post $RH ("B") ("int_lin") ("x_dev") (_b[x_dev]) (_se[x_dev]) (2*normal(-abs(_b[x_dev]/_se[x_dev]))) (e(widstat)) (e(N)) (`v12') (`v22') (.) (.) (.)
* quadratic interaction, log-log
ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm x_dev x_dev2 = feyrer_int z_dev z_dev2), absorb(isocode y) robust
matrix V = e(V)
local v12 = V[1,2]
local v22 = V[2,2]
local v13 = V[1,3]
local v23 = V[2,3]
local v33 = V[3,3]
di "INT-QUAD: b1 = " %8.4f _b[ln_gaci_cwm] "  b2 = " %8.4f _b[x_dev] "  b3 = " %8.4f _b[x_dev2] "  KP F = " %7.1f e(widstat)
post $RH ("B") ("int_quad") ("ln_gaci_cwm") (_b[ln_gaci_cwm]) (_se[ln_gaci_cwm]) (2*normal(-abs(_b[ln_gaci_cwm]/_se[ln_gaci_cwm]))) (e(widstat)) (e(N)) (`v12') (`v22') (`v13') (`v23') (`v33')
post $RH ("B") ("int_quad") ("x_dev") (_b[x_dev]) (_se[x_dev]) (2*normal(-abs(_b[x_dev]/_se[x_dev]))) (e(widstat)) (e(N)) (`v12') (`v22') (`v13') (`v23') (`v33')
post $RH ("B") ("int_quad") ("x_dev2") (_b[x_dev2]) (_se[x_dev2]) (2*normal(-abs(_b[x_dev2]/_se[x_dev2]))) (e(widstat)) (e(N)) (`v12') (`v22') (`v13') (`v23') (`v33')
* linear interaction, semi-log
ivreghdfe ln_co2_tot lnpop ln_sea_ma (gaci g_dev = feyrer_int zg_dev), absorb(isocode y) robust
matrix V = e(V)
local v12 = V[1,2]
local v22 = V[2,2]
di "INT-LIN semilog: b1 = " %8.4f _b[gaci] " (se " %7.4f _se[gaci] ")  b2 = " %8.4f _b[g_dev] " (se " %7.4f _se[g_dev] ")  KP F = " %7.1f e(widstat)
post $RH ("B") ("int_lin_semilog") ("gaci") (_b[gaci]) (_se[gaci]) (2*normal(-abs(_b[gaci]/_se[gaci]))) (e(widstat)) (e(N)) (`v12') (`v22') (.) (.) (.)
post $RH ("B") ("int_lin_semilog") ("g_dev") (_b[g_dev]) (_se[g_dev]) (2*normal(-abs(_b[g_dev]/_se[g_dev]))) (e(widstat)) (e(N)) (`v12') (`v22') (.) (.) (.)
* first-stage strength of the interacted instruments
reghdfe ln_gaci_cwm feyrer_int z_dev lnpop ln_sea_ma, absorb(isocode y) vce(robust)
test feyrer_int z_dev
di "FS joint F (own eq, linear interaction) = " %7.1f r(F)
post $RH ("B") ("fs_int_lin") ("F") (r(F)) (.) (.) (.) (e(N)) (.) (.) (.) (.) (.)

postclose `R'
preserve
use "_yifu_tmp", clear
list panel item var b se p kpf nn, clean noobs
export delimited "_yifu_suite.csv", replace
restore
erase "_yifu_tmp.dta"
di _n "DONE_YIFU_SUITE"
