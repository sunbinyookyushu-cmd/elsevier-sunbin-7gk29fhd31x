*==============================================================================
* co2_cutoff_sweep.do
* Temporal cutoff diagnostics for the Feyrer-IV emissions elasticity
* A) Cutoff sweep 2002-2019: pre (y<c) vs post (y>=c) 2SLS, b/se/p/KP-F/N
*    variants: all years; exGFC (drop 2008 & 2009)
*    -> _cutoff_sweep.csv
* B) First-stage structural break: sup-Wald over candidate breaks
*    reghdfe ln_gaci_cwm feyrer_int + feyrer_int x 1(y>=c), test interaction
*    -> _cutoff_break_fs.csv
* C) Interacted 2SLS: elasticity difference post vs pre at each cutoff
*    two endogenous (ln_gaci_cwm, ln_gaci_cwm x post) with
*    (feyrer_int, feyrer_int x post); record interaction b/se + KP F
*    -> _cutoff_ivdiff.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
set seed 20260826
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

* ---- build merged dataset (identical to co2_extensions.do) ----
import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl co2_lto co2_5050 dep_seat_km n_dep_flights dep_seats dep_seat_km_intl
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "../gaci_panel_measures.csv", clear varnames(1) encoding("utf-8")
keep c y ln_gaci_max
tempfile mx
save `mx'

import delimited "spillover_vars.csv", clear varnames(1) encoding("utf-8")
tempfile sp
save `sp'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `mx', keep(1 3) nogenerate
merge 1:1 c y using `sp', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm

summarize y
local ymin = r(min)
local ymax = r(max)
di "YEAR RANGE: `ymin' - `ymax'"

* =====================================================================
* A) cutoff sweep, pre/post, all vs exGFC
* =====================================================================
tempname S
postfile `S' str8 variant int cut str4 side double(b se p kpf) long(nn) using "_cut_tmp", replace
forvalues c = 2002/2019 {
    quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y < `c', absorb(isocode y) robust
    local bb = _b[ln_gaci_cwm]
    local ss = _se[ln_gaci_cwm]
    di "SWEEP all  c=`c' pre : b=" %7.3f `bb' " se=" %6.3f `ss' " F=" %7.1f e(widstat) " N=" e(N)
    post `S' ("all") (`c') ("pre") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y >= `c', absorb(isocode y) robust
    local bb = _b[ln_gaci_cwm]
    local ss = _se[ln_gaci_cwm]
    di "SWEEP all  c=`c' post: b=" %7.3f `bb' " se=" %6.3f `ss' " F=" %7.1f e(widstat) " N=" e(N)
    post `S' ("all") (`c') ("post") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y < `c' & y != 2008 & y != 2009, absorb(isocode y) robust
    local bb = _b[ln_gaci_cwm]
    local ss = _se[ln_gaci_cwm]
    di "SWEEP exG  c=`c' pre : b=" %7.3f `bb' " se=" %6.3f `ss' " F=" %7.1f e(widstat) " N=" e(N)
    post `S' ("exGFC") (`c') ("pre") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y >= `c' & y != 2008 & y != 2009, absorb(isocode y) robust
    local bb = _b[ln_gaci_cwm]
    local ss = _se[ln_gaci_cwm]
    di "SWEEP exG  c=`c' post: b=" %7.3f `bb' " se=" %6.3f `ss' " F=" %7.1f e(widstat) " N=" e(N)
    post `S' ("exGFC") (`c') ("post") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
}
postclose `S'
preserve
use "_cut_tmp", clear
export delimited "_cutoff_sweep.csv", replace
restore
erase "_cut_tmp.dta"

* =====================================================================
* B) first-stage structural break: sup-Wald over candidate cutoffs
* =====================================================================
tempname B
postfile `B' int cut double(wald pval b_z b_zpost) using "_brk_tmp", replace
forvalues c = 2002/2019 {
    gen byte post_c = (y >= `c')
    gen z_post = feyrer_int * post_c
    quietly reghdfe ln_gaci_cwm feyrer_int z_post lnpop ln_sea_ma, absorb(isocode y) vce(robust)
    local bz = _b[feyrer_int]
    local bzp = _b[z_post]
    quietly test z_post
    di "BREAK c=`c': W=" %8.2f r(F) " p=" %7.5f r(p) " b_z=" %7.3f `bz' " b_zpost=" %7.3f `bzp'
    post `B' (`c') (r(F)) (r(p)) (`bz') (`bzp')
    drop post_c z_post
}
postclose `B'
preserve
use "_brk_tmp", clear
export delimited "_cutoff_break_fs.csv", replace
restore
erase "_brk_tmp.dta"

* =====================================================================
* C) interacted 2SLS: does the elasticity differ post vs pre?
* =====================================================================
tempname C
postfile `C' str8 variant int cut double(b_pre se_pre b_diff se_diff p_diff kpf) long(nn) using "_ivd_tmp", replace
forvalues c = 2002/2019 {
    gen byte post_c = (y >= `c')
    gen g_post = ln_gaci_cwm * post_c
    gen z_post = feyrer_int * post_c
    capture noisily quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm g_post = feyrer_int z_post), absorb(isocode y) robust
    if _rc == 0 {
        local b1 = _b[ln_gaci_cwm]
        local s1 = _se[ln_gaci_cwm]
        local b2 = _b[g_post]
        local s2 = _se[g_post]
        di "IVDIFF all c=`c': b_pre=" %7.3f `b1' " b_diff=" %7.3f `b2' " se_diff=" %6.3f `s2' " F=" %7.1f e(widstat)
        post `C' ("all") (`c') (`b1') (`s1') (`b2') (`s2') (2*normal(-abs(`b2'/`s2'))) (e(widstat)) (e(N))
    }
    capture noisily quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm g_post = feyrer_int z_post) if y != 2008 & y != 2009, absorb(isocode y) robust
    if _rc == 0 {
        local b1 = _b[ln_gaci_cwm]
        local s1 = _se[ln_gaci_cwm]
        local b2 = _b[g_post]
        local s2 = _se[g_post]
        di "IVDIFF exG c=`c': b_pre=" %7.3f `b1' " b_diff=" %7.3f `b2' " se_diff=" %6.3f `s2' " F=" %7.1f e(widstat)
        post `C' ("exGFC") (`c') (`b1') (`s1') (`b2') (`s2') (2*normal(-abs(`b2'/`s2'))) (e(widstat)) (e(N))
    }
    drop post_c g_post z_post
}
postclose `C'
preserve
use "_ivd_tmp", clear
export delimited "_cutoff_ivdiff.csv", replace
restore
erase "_ivd_tmp.dta"

di "CUTOFF SWEEP DONE"
