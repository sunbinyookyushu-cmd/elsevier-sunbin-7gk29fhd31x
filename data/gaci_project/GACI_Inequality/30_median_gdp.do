* 30_median_gdp.do : growth and inequality together, countries split by baseline hub size (GACI_max in 1996).
* Median split and terciles. Outcomes: ln GDP per capita (WDI), ln GDP, ln mean income (WID), ln market Gini,
* ln disposable Gini. 2SLS Feyrer IV, ln pop, country + year FE, cluster country.
* Output: _median_gdp_results.csv (group, outcome, b, se, p, kpf, N, Nc)
capture log close _all
log using "30_median_gdp_run.log", replace text
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
bysort isocode (y): gen byte f_ = sum(!missing(gaci_max)) == 1 & !missing(gaci_max)
gen t_ = gaci_max if f_
bysort isocode (t_): gen gaci0 = t_[1]
drop f_ t_
preserve
bysort isocode: keep if _n == 1
xtile med2 = gaci0, nq(2)
xtile ter3 = gaci0, nq(3)
xtile qua4 = gaci0, nq(4)
keep isocode med2 ter3 qua4
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

tempname fh
file open `fh' using "_median_gdp_results.csv", write replace
file write `fh' "group,outcome,model,b,se,p,kpf,N,Nc" _n
capture program drop runone
program define runone
    args fh grp yv cond
    quietly count if `cond' & !missing(`yv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 60 exit
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if `cond', absorb(isocode y) cluster(isocode)
    if _rc exit
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    quietly levelsof isocode if e(sample), local(cc)
    local nc : word count `cc'
    file write `fh' "`grp',`yv',IV,`b',`se',`p',`=e(widstat)',`=e(N)',`nc'" _n
    quietly reghdfe `yv' ln_gaci_max lnpop if `cond', absorb(isocode y) vce(cluster isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    file write `fh' "`grp',`yv',OLS,`b',`se',`p',.,`=e(N)',`nc'" _n
end
foreach yv in ln_gdppc lngdp ln_apt_all ln_gini_mkt ln_gini_disp {
    runone `fh' "full" `yv' "1"
    runone `fh' "med_below" `yv' "med2 == 1"
    runone `fh' "med_above" `yv' "med2 == 2"
    runone `fh' "ter_low" `yv' "ter3 == 1"
    runone `fh' "ter_mid" `yv' "ter3 == 2"
    runone `fh' "ter_high" `yv' "ter3 == 3"
    runone `fh' "q1" `yv' "qua4 == 1"
    runone `fh' "q2" `yv' "qua4 == 2"
    runone `fh' "q3" `yv' "qua4 == 3"
    runone `fh' "q4" `yv' "qua4 == 4"
}
file close `fh'
log close _all
