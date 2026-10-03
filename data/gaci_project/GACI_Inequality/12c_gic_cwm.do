* 12c_gic_cwm.do : incidence curve with the capacity-weighted-mean treatment (ln GACI_cwm).
* Same specification as 12_gic_dose.do: ln pop, country + year FE, Feyrer IV, country-clustered SE.
* Outcomes: ln avg pretax income of each WID group; log share via the identity; three difference outcomes.
capture log close _all
log using "12c_gic_cwm_run.log", replace text
clear all
set more off
set linesize 255
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
set varabbrev off

tempname fh
file open `fh' using "_gic_cwm_results.csv", write replace
file write `fh' "block,outcome,spec,b,se,p,kpf,N" _n

local GRP "d1 d2 d3 d4 d5 d6 d7 d8 d9 d10 t1 t01 b50 m40 all"
foreach g of local GRP {
    local yv ln_apt_`g'
    capture confirm variable `yv'
    if _rc continue
    quietly reghdfe `yv' ln_gaci_cwm lnpop, absorb(isocode y) vce(cluster isocode)
    local b = _b[ln_gaci_cwm]
    local se = _se[ln_gaci_cwm]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "gic,`yv',OLS,`b',`se',`p',.,`nn'" _n
    quietly ivreghdfe `yv' lnpop (ln_gaci_cwm = feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_cwm]
    local se = _se[ln_gaci_cwm]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "gic,`yv',IV,`b',`se',`p',`kp',`nn'" _n
}
foreach g of local GRP {
    if "`g'"=="all" continue
    capture confirm variable ln_apt_`g'
    if _rc continue
    capture drop ln_spt_`g'
    gen ln_spt_`g' = ln_apt_`g' - ln_apt_all
    local yv ln_spt_`g'
    quietly reghdfe `yv' ln_gaci_cwm lnpop, absorb(isocode y) vce(cluster isocode)
    local b = _b[ln_gaci_cwm]
    local se = _se[ln_gaci_cwm]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "gic_share,`yv',OLS,`b',`se',`p',.,`nn'" _n
    quietly ivreghdfe `yv' lnpop (ln_gaci_cwm = feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_cwm]
    local se = _se[ln_gaci_cwm]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "gic_share,`yv',IV,`b',`se',`p',`kp',`nn'" _n
}
gen ln_apt_d10_d1 = ln_apt_d10 - ln_apt_d1
gen ln_apt_d10_b50 = ln_apt_d10 - ln_apt_b50
gen ln_apt_t1_d10 = ln_apt_t1 - ln_apt_d10
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
foreach yv in ln_apt_d10_d1 ln_apt_d10_b50 ln_apt_t1_d10 ln_apt_top_bot {
    quietly ivreghdfe `yv' lnpop (ln_gaci_cwm = feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_cwm]
    local se = _se[ln_gaci_cwm]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "gic_gap,`yv',IV,`b',`se',`p',`kp',`nn'" _n
    quietly reghdfe `yv' ln_gaci_cwm lnpop, absorb(isocode y) vce(cluster isocode)
    local b = _b[ln_gaci_cwm]
    local se = _se[ln_gaci_cwm]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "gic_gap,`yv',OLS,`b',`se',`p',.,`nn'" _n
}
* top-half minus bottom-half contrast for the headline treatment too (missing from 12_gic_dose)
quietly ivreghdfe ln_apt_top_bot lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
local b = _b[ln_gaci_max]
local se = _se[ln_gaci_max]
local p = 2*normal(-abs(`b'/`se'))
local kp = e(widstat)
local nn = e(N)
file write `fh' "gic_gap_max,ln_apt_top_bot,IV,`b',`se',`p',`kp',`nn'" _n
file close `fh'
log close _all
