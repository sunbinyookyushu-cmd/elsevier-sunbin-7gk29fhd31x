* 36_wage_premia.do : direct test of the skill-biased / hub-occupation channel with ILOSTAT earnings.
* Outcomes (log ratios of average monthly earnings, employees, both sexes):
*   prem_adv_bas   advanced vs basic education      prem_adv_int  advanced vs intermediate education
*   prem_ser_agr   services vs agriculture          prem_ser_ind  services vs industry
*   prem_mkt_man   market services vs manufacturing prem_mgr_elem managers vs elementary occupations
*   prem_prof_elem professionals vs elementary      prem_prof_craft professionals vs craft workers
*   gini_earn_total Gini of monthly earnings (employees); ln_earn_total ln average earnings
* 2SLS Feyrer, ln pop, country + year FE, cluster country; OLS alongside. Unbalanced ILO coverage: report N and countries.
* Output: _wage_premia_results.csv (outcome, model, b, se, p, kpf, N, Nc)
capture log close _all
log using "36_wage_premia_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "_ilo_premia.csv", clear varnames(1) encoding("utf-8")
tempfile ilo
save `ilo'
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `ilo', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
tempname fh
file open `fh' using "_wage_premia_results.csv", write replace
file write `fh' "outcome,model,b,se,p,kpf,N,Nc" _n
foreach yv in prem_adv_bas prem_adv_int prem_ser_agr prem_ser_ind prem_mkt_man prem_mgr_elem prem_prof_elem prem_prof_craft gini_earn_total ln_earn_total {
    capture confirm variable `yv'
    if _rc continue
    quietly count if !missing(`yv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 100 continue
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        quietly levelsof isocode if e(sample), local(cc)
        local nc : word count `cc'
        file write `fh' "`yv',IV,`=_b[ln_gaci_max]',`=_se[ln_gaci_max]',`=2*normal(-abs(_b[ln_gaci_max]/_se[ln_gaci_max]))',`=e(widstat)',`=e(N)',`nc'" _n
    }
    quietly reghdfe `yv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    quietly levelsof isocode if e(sample), local(cc)
    local nc : word count `cc'
    file write `fh' "`yv',OLS,`=_b[ln_gaci_max]',`=_se[ln_gaci_max]',`=2*ttail(e(df_r), abs(_b[ln_gaci_max]/_se[ln_gaci_max]))',.,`=e(N)',`nc'" _n
    * headline Gini on the same sample, for comparability
    capture noisily ivreghdfe ln_gini_mkt lnpop (ln_gaci_max = feyrer_int) if !missing(`yv'), absorb(isocode y) cluster(isocode)
    if _rc == 0 file write `fh' "`yv'_sample_gini,IV,`=_b[ln_gaci_max]',`=_se[ln_gaci_max]',`=2*normal(-abs(_b[ln_gaci_max]/_se[ln_gaci_max]))',`=e(widstat)',`=e(N)',." _n
}
file close `fh'
log close _all
