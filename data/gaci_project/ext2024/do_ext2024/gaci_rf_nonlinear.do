*==============================================================================
* gaci_rf_nonlinear.do
* Flexible (quintile-bin) REDUCED-FORM heterogeneity of the instrument effect
* on trade openness, by baseline income, baseline connectivity, remoteness.
*   Spec: reghdfe g_int ibn.q#c.tourism_int lnpop, absorb(isocode y) robust
*   Bins are country-level quintiles over the estimation sample, so the bin
*   main effects are absorbed by the country FE. Reduced form only: no weak-
*   instrument issue, read as the shape of the gradient.
* Output: gaci_rf_nonlinear.log + _rf_nonlinear.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/ext2024"
* batch mode (/e) writes gaci_rf_nonlinear.log automatically

import delimited "gaci_panel_3iv.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen g_int = merch_intensity

capture which reghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
}

* ---- baseline (1996) moderators ----
gen tmp = lnpc if y==1996
bysort isocode: egen base_lnpc = max(tmp)
drop tmp
gen tmp = ln_gaci_cwm if y==1996
bysort isocode: egen base_cwm = max(tmp)
drop tmp

* ---- country-level quintiles over the estimation sample ----
gen byte insamp = !missing(g_int) & !missing(lnpop) & !missing(tourism_int)
preserve
keep if insamp
collapse (first) base_lnpc base_cwm ln_remote, by(isocode)
xtile q_inc = base_lnpc, nq(5)
xtile q_con = base_cwm, nq(5)
xtile q_rem = ln_remote, nq(5)
tempfile qq
save `qq'
restore
merge m:1 isocode using `qq', nogen keepusing(q_inc q_con q_rem)

tempname R
postfile `R' str8 mod byte bin double(b se) long(nn) using "_rf_tmp", replace

foreach m in inc con rem {
    di _n "==================== MODERATOR: `m' ===================="
    reghdfe g_int ibn.q_`m'#c.tourism_int lnpop, absorb(isocode y) vce(robust)
    local nn = e(N)
    forvalues k = 1/5 {
        local bb = _b[`k'.q_`m'#c.tourism_int]
        local sse = _se[`k'.q_`m'#c.tourism_int]
        di "  Q`k': b = " %9.4f `bb' "  se = " %9.4f `sse'
        post `R' ("`m'") (`k') (`bb') (`sse') (`nn')
    }
}

postclose `R'
use "_rf_tmp", clear
list, clean
export delimited "_rf_nonlinear.csv", replace
erase "_rf_tmp.dta"
di _n "DONE_RF_NONLINEAR"
