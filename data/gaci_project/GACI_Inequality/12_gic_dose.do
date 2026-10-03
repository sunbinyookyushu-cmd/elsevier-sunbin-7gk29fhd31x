* 12_gic_dose.do : (A) growth-incidence curve of hub connectivity across WID income groups
*                  (B) within-country regional dispersion of GRP per capita (DOSE v2.9)
* Same specification as 01_main (ln GACI_max, ln pop, country + year FE), Feyrer IV, country-clustered SE.
capture log close _all
log using "12_gic_dose_run.log", replace text
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
gen cont = substr(reg,1,2)
encode cont, gen(contid)
set varabbrev off

tempname fh
file open `fh' using "_gic_dose_results.csv", write replace
file write `fh' "block,outcome,spec,b,se,p,kpf,N" _n

* ---------------- A. growth incidence: average income by group ----------------
local GRP "d1 d2 d3 d4 d5 d6 d7 d8 d9 d10 t1 t01 b50 m40 all"
foreach pre in ln_apt ln_adi {
    foreach g of local GRP {
        local yv `pre'_`g'
        capture confirm variable `yv'
        if _rc continue
        quietly reghdfe `yv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*ttail(e(df_r), abs(`b'/`se'))
        local nn = e(N)
        file write `fh' "gic,`yv',OLS,`b',`se',`p',.,`nn'" _n
        quietly ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "gic,`yv',IV,`b',`se',`p',`kp',`nn'" _n
        quietly ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode contid#y) cluster(isocode)
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "gic,`yv',IV_contyear,`b',`se',`p',`kp',`nn'" _n
        quietly ivreghdfe `yv' lnpop (ln_gaci_max = tourism_int), absorb(isocode y) cluster(isocode)
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "gic,`yv',IV_tourism,`b',`se',`p',`kp',`nn'" _n
    }
}
* income shares (log), pretax: use the identity ln share_g = ln apt_g - ln apt_all + const so that the
* sample equals the level regressions (WID rounds the bottom-decile share to 0 in 271 country-years)
foreach g of local GRP {
    if "`g'"=="all" continue
    local yv ln_spt_`g'
    capture confirm variable ln_apt_`g'
    if _rc continue
    capture drop `yv'
    gen `yv' = ln_apt_`g' - ln_apt_all
    quietly ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "gic_share,`yv',IV,`b',`se',`p',`kp',`nn'" _n
    quietly reghdfe `yv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "gic_share,`yv',OLS,`b',`se',`p',.,`nn'" _n
}
* joint test: equal elasticity across deciles (2SLS, SUR-free version: pairwise d10 - d1 via difference outcome)
gen ln_apt_d10_d1 = ln_apt_d10 - ln_apt_d1
gen ln_apt_d10_b50 = ln_apt_d10 - ln_apt_b50
gen ln_apt_t1_d10 = ln_apt_t1 - ln_apt_d10
foreach yv in ln_apt_d10_d1 ln_apt_d10_b50 ln_apt_t1_d10 {
    quietly ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "gic_gap,`yv',IV,`b',`se',`p',`kp',`nn'" _n
    quietly reghdfe `yv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "gic_gap,`yv',OLS,`b',`se',`p',.,`nn'" _n
}

* ---------------- B. DOSE regional dispersion ----------------
foreach yv in ln_theil_reg ln_gini_reg ln_cv_reg ln_share_topreg ln_ratio_topreg theil_reg gini_reg {
    quietly reghdfe `yv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "dose,`yv',OLS,`b',`se',`p',.,`nn'" _n
    quietly ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "dose,`yv',IV,`b',`se',`p',`kp',`nn'" _n
    quietly ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode contid#y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "dose,`yv',IV_contyear,`b',`se',`p',`kp',`nn'" _n
    quietly ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if stable_reg==1, absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "dose,`yv',IV_stable,`b',`se',`p',`kp',`nn'" _n
    quietly ivreghdfe `yv' lnpop (ln_gaci_max = tourism_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "dose,`yv',IV_tourism,`b',`se',`p',`kp',`nn'" _n
}
* market Gini on the DOSE sample, for comparability
quietly ivreghdfe ln_gini_mkt lnpop (ln_gaci_max = feyrer_int) if !missing(ln_theil_reg), absorb(isocode y) cluster(isocode)
local b = _b[ln_gaci_max]
local se = _se[ln_gaci_max]
local p = 2*normal(-abs(`b'/`se'))
local kp = e(widstat)
local nn = e(N)
file write `fh' "dose,ln_gini_mkt_dosesample,IV,`b',`se',`p',`kp',`nn'" _n
* does regional dispersion carry the Gini association? (suppressor/mediator check, same logic as tab_mech)
quietly ivreghdfe ln_gini_mkt lnpop ln_theil_reg (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
local b = _b[ln_gaci_max]
local se = _se[ln_gaci_max]
local p = 2*normal(-abs(`b'/`se'))
local kp = e(widstat)
local nn = e(N)
file write `fh' "dose,ln_gini_mkt_ctrl_theil,IV,`b',`se',`p',`kp',`nn'" _n
local b = _b[ln_theil_reg]
local se = _se[ln_theil_reg]
local p = 2*normal(-abs(`b'/`se'))
file write `fh' "dose,theil_coef_in_gini_eq,IV,`b',`se',`p',.,`nn'" _n
file close `fh'
log close
