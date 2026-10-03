*==============================================================================
* co2_iv_choice.do  (2026-09-03)  Which instrument? Same diagnostics for
*   A  feyrer_int = a_t x ln airMA96 (sea MA controlled)      [current]
*   B  adv_int    = a_t x ln(airMA96 / seaMA96)                [air advantage]
*   C  feyrer_int with fey_sea (a_t x ln seaMA96) as control   [air net of sea]
* Diagnostics (all cluster(isocode)): first stage, 2SLS on CO2 / seat-km /
* intensity, placebo outcomes (total ex-aviation, coal, cement), horse race
* with world GDP x geography, zero-first-stage RF (top connectivity tercile),
* overid with lagged fatal accidents, controls path end-point.
* Export: _iv_choice.csv (iv item outc b se p f nn)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker dep_seat_km
rename iso3 c
rename year y
tempfile co2
save `co2'
import delimited "placebo_covariates.csv", clear varnames(1) encoding("utf-8")
ds c, not
destring `r(varlist)', replace force
tempfile plc
save `plc'
import delimited "../gaci_panel_feyrer.csv", clear varnames(1) encoding("utf-8")
keep c y adv_int a_t
destring y adv_int a_t, replace force
tempfile adv
save `adv'
import delimited "asn_country_year.csv", clear varnames(1) encoding("utf-8")
keep c y n_fatal
tempfile asn
save `asn'
import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `plc', keep(1 3) nogenerate
merge 1:1 c y using `adv', keep(1 3) nogenerate
merge 1:1 c y using `asn', keep(1 3) nogenerate
encode c, gen(isocode)
sort isocode y
xtset isocode y
gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm
capture gen fey_gdp_sea = g_gdp * ln_sea96
bysort isocode (y): gen byte first_g = sum(!missing(gaci_cwmean)) == 1 & !missing(gaci_cwmean)
gen g0_ = gaci_cwmean if first_g
bysort isocode (g0_): gen gaci0 = g0_[1]
drop g0_ first_g
preserve
bysort isocode: keep if _n == 1
xtile con3 = gaci0, nq(3)
keep isocode con3
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate
capture gen lag_fatal = L.n_fatal

tempname R
postfile `R' str4 iv str24 item str18 outc double(b se p f) long(nn) using "_ivc_tmp", replace
global RH `R'
program define pst
    args iv item outc v f
    local bb = _b[`v']
    local sse = _se[`v']
    post $RH ("`iv'") ("`item'") ("`outc'") (`bb') (`sse') (2*normal(-abs(`bb'/`sse'))) (`f') (e(N))
    di "IVC [`iv'] `item' `outc': b = " %9.3f `bb' " (se " %8.3f `sse' ")  F = " %7.1f `f' "  N = " %6.0f e(N)
end

foreach IV in A B C {
    if "`IV'" == "A" {
        local z "feyrer_int"
        local ctl "lnpop ln_sea_ma"
    }
    if "`IV'" == "B" {
        local z "adv_int"
        local ctl "lnpop ln_sea_ma"
    }
    if "`IV'" == "C" {
        local z "feyrer_int"
        local ctl "lnpop ln_sea_ma fey_sea"
    }
    di _n "=============== IV `IV': z = `z' ; controls = `ctl' ==============="
    * first stage
    reghdfe ln_gaci_cwm `z' `ctl', absorb(isocode y) vce(cluster isocode)
    test `z'
    pst `IV' firststage ln_gaci_cwm `z' r(F)
    * 2SLS main outcomes
    foreach yv in ln_co2_tot ln_skm ln_intensity {
        ivreghdfe `yv' `ctl' (ln_gaci_cwm = `z'), absorb(isocode y) cluster(isocode)
        pst `IV' iv `yv' ln_gaci_cwm e(widstat)
    }
    * placebo outcomes (reduced form)
    foreach yv in ln_co2_exav ln_coal ln_cement ln_ed_power ln_ed_transp_exav {
        capture noisily reghdfe `yv' `z' `ctl', absorb(isocode y) vce(cluster isocode)
        if _rc == 0 pst `IV' rf_placebo `yv' `z' .
    }
    reghdfe ln_co2_tot `z' `ctl', absorb(isocode y) vce(cluster isocode)
    pst `IV' rf_aviation ln_co2_tot `z' .
    * horse race: world GDP x own geography of the instrument
    if "`IV'" == "B" {
        capture gen adv_gdp = g_gdp * (ln_air96 - ln_sea96)
        reghdfe ln_gaci_cwm `z' adv_gdp `ctl', absorb(isocode y) vce(cluster isocode)
        test `z'
        pst `IV' fs_plus_gdpcycle ln_gaci_cwm `z' r(F)
        capture noisily ivreghdfe ln_co2_tot `ctl' adv_gdp (ln_gaci_cwm = `z'), absorb(isocode y) cluster(isocode)
        if _rc == 0 pst `IV' iv_plus_gdpcycle ln_co2_tot ln_gaci_cwm e(widstat)
        reghdfe ln_gaci_cwm `z' fey_oil `ctl', absorb(isocode y) vce(cluster isocode)
        test `z'
        pst `IV' fs_plus_oilcycle ln_gaci_cwm `z' r(F)
    }
    else {
        reghdfe ln_gaci_cwm `z' fey_gdp `ctl', absorb(isocode y) vce(cluster isocode)
        test `z'
        pst `IV' fs_plus_gdpcycle ln_gaci_cwm `z' r(F)
        capture noisily ivreghdfe ln_co2_tot `ctl' fey_gdp (ln_gaci_cwm = `z'), absorb(isocode y) cluster(isocode)
        if _rc == 0 pst `IV' iv_plus_gdpcycle ln_co2_tot ln_gaci_cwm e(widstat)
        reghdfe ln_gaci_cwm `z' fey_oil `ctl', absorb(isocode y) vce(cluster isocode)
        test `z'
        pst `IV' fs_plus_oilcycle ln_gaci_cwm `z' r(F)
    }
    * world GDP x SEA geography as a general-growth control (for A and B)
    capture noisily ivreghdfe ln_co2_tot `ctl' fey_gdp_sea (ln_gaci_cwm = `z'), absorb(isocode y) cluster(isocode)
    if _rc == 0 pst `IV' iv_plus_gdp_x_sea ln_co2_tot ln_gaci_cwm e(widstat)
    * zero first stage: top tercile
    reghdfe ln_gaci_cwm `z' `ctl' if con3 == 3, absorb(isocode y) vce(cluster isocode)
    test `z'
    pst `IV' zfs_firststage_top ln_gaci_cwm `z' r(F)
    reghdfe ln_co2_tot `z' `ctl' if con3 == 3, absorb(isocode y) vce(cluster isocode)
    pst `IV' zfs_rf_top ln_co2_tot `z' .
    * overid with lagged fatal accidents
    capture noisily ivreghdfe ln_co2_tot `ctl' (ln_gaci_cwm = `z' lag_fatal), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        pst `IV' overid_accident ln_co2_tot ln_gaci_cwm e(widstat)
        post $RH ("`IV'") ("hansen_p_accident") ("ln_co2_tot") (e(j)) (.) (e(jp)) (.) (e(N))
        di "IVC [`IV'] Hansen J with accidents = " %6.2f e(j) "  p = " %5.3f e(jp)
    }
    * controls end-point
    capture noisily ivreghdfe ln_co2_tot `ctl' lngdp trade_gdp urban fdi (ln_gaci_cwm = `z'), absorb(isocode y) cluster(isocode)
    if _rc == 0 pst `IV' iv_with_controls ln_co2_tot ln_gaci_cwm e(widstat)
    * post-2010 excluding COVID
    capture noisily ivreghdfe ln_co2_tot `ctl' (ln_gaci_cwm = `z') if y >= 2010 & !inlist(y, 2020, 2021), absorb(isocode y) cluster(isocode)
    if _rc == 0 pst `IV' iv_post2010_excovid ln_co2_tot ln_gaci_cwm e(widstat)
}
* correlation of the two instruments within country
quietly reghdfe adv_int feyrer_int, absorb(isocode y)
di "within R2 of adv_int on feyrer_int = " %6.3f e(r2_within)
post $RH ("AB") ("within_r2") ("adv_on_fey") (e(r2_within)) (.) (.) (.) (e(N))

postclose `R'
preserve
use "_ivc_tmp", clear
list, clean noobs
export delimited "_iv_choice.csv", replace
restore
erase "_ivc_tmp.dta"
di _n "DONE_IV_CHOICE"
