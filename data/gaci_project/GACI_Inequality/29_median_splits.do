* 29_median_splits.do : split countries at the median of a baseline characteristic (earliest observed value),
* not of the treatment. Split-sample 2SLS (Feyrer IV, ln pop, country + year FE, cluster country).
* Outcomes: ln market Gini, mean income, top-half minus bottom-half, bottom-50 share, top-10 share.
* Output: _median_splits_results.csv (var, group, outcome, b, se, p, kpf, N, Nc)
capture log close _all
log using "29_median_splits_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
capture drop ln_spt_b50
gen ln_spt_b50 = ln_apt_b50 - ln_apt_all
capture drop ln_spt_d10
gen ln_spt_d10 = ln_apt_d10 - ln_apt_all
gen top10 = spt_d10
local VARS "ln_gdppc lnpop gini_mkt top10 trade_gdp urban tax_gdp abslat ln_sea_ma ln_air_ma"
foreach v of local VARS {
    bysort isocode (y): gen byte f_ = sum(!missing(`v')) == 1 & !missing(`v')
    gen t_ = `v' if f_
    bysort isocode (t_): gen b_`v' = t_[1]
    drop f_ t_
}
preserve
bysort isocode: keep if _n == 1
foreach v of local VARS {
    xtile m_`v' = b_`v', nq(2)
}
keep isocode m_*
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

tempname fh
file open `fh' using "_median_splits_results.csv", write replace
file write `fh' "var,group,outcome,b,se,p,kpf,N,Nc" _n
capture program drop runone
program define runone
    args fh vv grp yv cond
    quietly count if `cond' & !missing(`yv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 60 exit
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if `cond', absorb(isocode y) cluster(isocode)
    if _rc exit
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    quietly levelsof isocode if e(sample), local(cc)
    local nc : word count `cc'
    file write `fh' "`vv',`grp',`yv',`b',`se',`p',`=e(widstat)',`=e(N)',`nc'" _n
end
foreach yv in ln_gini_mkt ln_apt_all ln_apt_top_bot ln_spt_b50 ln_spt_d10 {
    foreach v of local VARS {
        runone `fh' "`v'" "below" `yv' "m_`v' == 1"
        runone `fh' "`v'" "above" `yv' "m_`v' == 2"
    }
}
file close `fh'
log close _all
