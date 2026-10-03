*==============================================================================
* co2_rf_quintile.do
* Flexible (quintile-bin) reduced-form heterogeneity of the instrument effect
* on ln CO2 (bunker), by baseline income, baseline connectivity, remoteness.
* Mirror of the trade paper gaci_rf_nonlinear.do (Yifu comment 3).
* Output: batch log + _co2_rf_quintile_intl.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "gaci_co2_panel.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

capture which reghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
}

gen tmp = lnpc if y==1996
bysort isocode: egen base_lnpc = max(tmp)
drop tmp
gen tmp = ln_gaci_cwm if y==1996
bysort isocode: egen base_cwm = max(tmp)
drop tmp

gen byte insamp = !missing(ln_co2_bunker_intl) & !missing(lnpop) & !missing(tourism_int)
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
postfile `R' str8 mod byte bin double(b se) long(nn) using "_co2_rf_tmp2", replace

foreach m in inc con rem {
    di _n "==================== MODERATOR: `m' ===================="
    reghdfe ln_co2_bunker_intl ibn.q_`m'#c.tourism_int lnpop, absorb(isocode y) vce(robust)
    local nn = e(N)
    forvalues k = 1/5 {
        local bb = _b[`k'.q_`m'#c.tourism_int]
        local sse = _se[`k'.q_`m'#c.tourism_int]
        di "  Q`k': b = " %9.4f `bb' "  se = " %9.4f `sse'
        post `R' ("`m'") (`k') (`bb') (`sse') (`nn')
    }
}

postclose `R'
use "_co2_rf_tmp2", clear
list, clean
export delimited "_co2_rf_quintile_intl.csv", replace
erase "_co2_rf_tmp2.dta"
di _n "DONE_CO2_RF"
