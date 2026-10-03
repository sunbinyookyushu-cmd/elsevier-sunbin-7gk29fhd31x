* 40_mediators2.do : second mediator battery, candidates that could plausibly transmit an inequality-raising effect.
*  Employment composition (ILO): shares of finance (K), professional/scientific (M), ICT (J), real estate (L), KIBS (J+K+L+M),
*  accommodation (I), transport (H), public admin (O); occupations: managers, professionals, elementary; informality rate.
*  Population flows and fiscal: net migration rate (per 1,000), transfers share of government expense.
* a-path (2SLS/OLS), IV decomposition on ln market Gini / bottom-50 share / top-10 share (c', b), plus headline on same sample.
* Output: _mediators2_results.csv (block,item,outcome,term,b,se,p,kpf,N)
capture log close _all
log using "40_mediators2_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "_med2.csv", clear varnames(1) encoding("utf-8")
tempfile m2
save `m2'
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `m2', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
capture drop ln_spt_b50
gen ln_spt_b50 = ln_apt_b50 - ln_apt_all
capture drop ln_spt_d10
gen ln_spt_d10 = ln_apt_d10 - ln_apt_all
tempname fh
file open `fh' using "_mediators2_results.csv", write replace
file write `fh' "block,item,outcome,term,b,se,p,kpf,N" _n
capture program drop wr
program define wr
    args fh blk item yv term kp
    local b = _b[`term']
    local se = _se[`term']
    local p = 2*normal(-abs(`b'/`se'))
    file write `fh' "`blk',`item',`yv',`term',`b',`se',`p',`kp',`=e(N)'" _n
end
local MED "emp_fin_sh emp_prof_sh emp_ict_sh emp_re_sh emp_kibs_sh emp_accom_sh emp_transp_sh emp_pub_sh occ_mgr_sh occ_prof_sh occ_top_sh occ_elem_sh informal_rt net_mig_rate transfers_sh_exp"
foreach mv of local MED {
    capture confirm variable `mv'
    if _rc continue
    quietly count if !missing(`mv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 150 continue
    capture noisily ivreghdfe `mv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 wr `fh' A apath `mv' ln_gaci_max `=e(widstat)'
    quietly reghdfe `mv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    wr `fh' A apath_ols `mv' ln_gaci_max .
    * headline on the same sample
    capture noisily ivreghdfe ln_gini_mkt lnpop (ln_gaci_max = feyrer_int) if !missing(`mv'), absorb(isocode y) cluster(isocode)
    if _rc == 0 wr `fh' A samplegini `mv' ln_gaci_max `=e(widstat)'
    foreach yv in ln_gini_mkt ln_spt_b50 ln_spt_d10 {
        capture noisily ivreghdfe `yv' lnpop `mv' (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            wr `fh' B `mv' `yv' ln_gaci_max `=e(widstat)'
            wr `fh' B `mv' `yv' `mv' `=e(widstat)'
        }
        quietly reghdfe `yv' `mv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
        wr `fh' B_ols `mv' `yv' `mv' .
    }
}
file close `fh'
log close _all
