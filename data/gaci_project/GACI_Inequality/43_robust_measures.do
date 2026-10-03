* 43_robust_measures.do : robustness to the connectivity measure (max / cwm / sum) and to the inequality measure.
* Outcomes: ln SWIID market Gini, ln SWIID disposable Gini, ln WID pretax Gini, ln Palma (top10/bottom40, WID),
*           ln p90/p10 (WID decile means), ln absolute gap top10 vs bottom50 (WID, constant local prices), ln p50/p10.
* OLS and 2SLS Feyrer; ln pop, country + year FE, cluster country. Output: _robust_measures_results.csv
capture log close _all
log using "43_robust_measures_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "_alt_measures_panel.csv", clear varnames(1) encoding("utf-8")
keep c y palma p90_p10 p50_p10 abs_gap_t10_b50
ds c, not
destring `r(varlist)', replace force
tempfile alt
save `alt'
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `alt', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
gen ln_palma = ln(palma)
gen ln_p90_p10 = ln(p90_p10)
gen ln_p50_p10 = ln(p50_p10)
gen ln_abs_gap = ln(abs_gap_t10_b50) if abs_gap_t10_b50 > 0
tempname fh
file open `fh' using "_robust_measures_results.csv", write replace
file write `fh' "treat,outcome,model,b,se,p,kpf,N" _n
foreach tr in ln_gaci_max ln_gaci_cwm ln_gaci_sum {
    foreach yv in ln_gini_mkt ln_gini_disp ln_gini_pre_wid ln_palma ln_p90_p10 ln_p50_p10 ln_abs_gap {
        capture confirm variable `yv'
        if _rc continue
        quietly reghdfe `yv' `tr' lnpop, absorb(isocode y) vce(cluster isocode)
        file write `fh' "`tr',`yv',OLS,`=_b[`tr']',`=_se[`tr']',`=2*ttail(e(df_r), abs(_b[`tr']/_se[`tr']))',.,`=e(N)'" _n
        capture noisily ivreghdfe `yv' lnpop (`tr' = feyrer_int), absorb(isocode y) cluster(isocode)
        if _rc == 0 file write `fh' "`tr',`yv',IV,`=_b[`tr']',`=_se[`tr']',`=2*normal(-abs(_b[`tr']/_se[`tr']))',`=e(widstat)',`=e(N)'" _n
    }
}
file close `fh'
log close _all
