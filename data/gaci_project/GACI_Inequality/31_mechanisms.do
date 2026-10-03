* 31_mechanisms.do : testable mechanisms with our own panel (2SLS Feyrer, ln pop, country + year FE, cluster country).
*  A. Which connectivity: hub (GACI_max) vs the rest of the network (secondary airports), and concentration.
*  B. a-paths: does connectivity move candidate mediators? (2SLS, mediator as outcome)
*  C. IV decomposition for distributional outcomes: y on ln GACI_max (instrumented) + mediator (as control);
*     reports c' (direct) and b (mediator), indirect = a x b.
*  D. Redistribution response: market-minus-disposable Gini wedge, tax revenue.
*  E. Heterogeneity consistent with channels: baseline international seat share, tourism receipts share (median splits).
* Inputs: ineq_panel_ext.csv, _wdi_mech.csv (WDI API 2026-09-28), _co2_mech.csv (from ../GACI_CO2/co2_country_year.csv)
* Output: _mech_results.csv (block, item, outcome, term, b, se, p, kpf, N)
capture log close _all
log using "31_mechanisms_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "_wdi_mech.csv", clear varnames(1) encoding("utf-8")
tempfile wdi
save `wdi'
import delimited "_co2_mech.csv", clear varnames(1) encoding("utf-8")
tempfile co2
save `co2'
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `wdi', keep(1 3) nogenerate
merge 1:1 c y using `co2', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
capture drop ln_spt_b50
gen ln_spt_b50 = ln_apt_b50 - ln_apt_all
capture drop ln_spt_d10
gen ln_spt_d10 = ln_apt_d10 - ln_apt_all
gen ln_tour_arr = ln(tour_arrivals) if tour_arrivals > 0
gen gaci_rest = gaci_sum - gaci_max
gen ln_gaci_rest = ln(gaci_rest) if gaci_rest > 0
gen wedge_pts = gini_mkt - gini_disp
gen ln_wedge_ratio = ln(gini_mkt) - ln(gini_disp)

tempname fh
file open `fh' using "_mech_results.csv", write replace
file write `fh' "block,item,outcome,term,b,se,p,kpf,N" _n
capture program drop wr
program define wr
    args fh blk item yv term kp
    local b = _b[`term']
    local se = _se[`term']
    local p = 2*normal(-abs(`b'/`se'))
    file write `fh' "`blk',`item',`yv',`term',`b',`se',`p',`kp',`=e(N)'" _n
end

* ---------------- A. hub vs rest of network ----------------
foreach yv in ln_gini_mkt ln_gini_disp ln_spt_b50 ln_apt_top_bot {
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 wr `fh' A baseline `yv' ln_gaci_max `=e(widstat)'
    capture noisily ivreghdfe `yv' lnpop ln_gaci_rest (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        wr `fh' A hub_ctrl_rest `yv' ln_gaci_max `=e(widstat)'
        wr `fh' A hub_ctrl_rest `yv' ln_gaci_rest `=e(widstat)'
    }
    capture noisily ivreghdfe `yv' lnpop ln_gaci_sum (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        wr `fh' A hub_ctrl_sum `yv' ln_gaci_max `=e(widstat)'
        wr `fh' A hub_ctrl_sum `yv' ln_gaci_sum `=e(widstat)'
    }
    capture noisily ivreghdfe `yv' lnpop ln_gaci_max (ln_gaci_rest = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        wr `fh' A rest_iv_ctrl_hub `yv' ln_gaci_rest `=e(widstat)'
        wr `fh' A rest_iv_ctrl_hub `yv' ln_gaci_max `=e(widstat)'
    }
    quietly reghdfe `yv' ln_share_max ln_gaci_sum lnpop, absorb(isocode y) vce(cluster isocode)
    wr `fh' A ols_share_max `yv' ln_share_max .
    wr `fh' A ols_share_max `yv' ln_gaci_sum .
    quietly reghdfe `yv' ln_hhi ln_gaci_sum lnpop, absorb(isocode y) vce(cluster isocode)
    wr `fh' A ols_hhi `yv' ln_hhi .
}

* ---------------- B. a-paths ----------------
local MED "ln_tour_arr tour_rcpt_exp srv_va manf_va wage_emp self_emp lf_advanced ter_enr2 unemp_adv intl_seat_share ln_seatkm emp_srv emp_ind emp_agr urban trade_gdp fdi_gdp tax_gdp ln_gdppc unemp"
foreach mv of local MED {
    capture confirm variable `mv'
    if _rc continue
    capture noisily ivreghdfe `mv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 wr `fh' B apath `mv' ln_gaci_max `=e(widstat)'
    quietly reghdfe `mv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    wr `fh' B apath_ols `mv' ln_gaci_max .
}

* ---------------- C. IV decomposition for distributional outcomes ----------------
foreach yv in ln_gini_mkt ln_spt_b50 ln_apt_top_bot ln_spt_d10 {
    foreach mv of local MED {
        capture confirm variable `mv'
        if _rc continue
        capture noisily ivreghdfe `yv' lnpop `mv' (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            wr `fh' C `mv' `yv' ln_gaci_max `=e(widstat)'
            wr `fh' C `mv' `yv' `mv' `=e(widstat)'
        }
    }
}

* ---------------- D. redistribution response ----------------
foreach yv in wedge_pts ln_wedge_ratio tax_gdp {
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 wr `fh' D redistribution `yv' ln_gaci_max `=e(widstat)'
    quietly reghdfe `yv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    wr `fh' D redistribution_ols `yv' ln_gaci_max .
}

* ---------------- E. heterogeneity by channel proxies (baseline median) ----------------
foreach v in intl_seat_share tour_rcpt_exp srv_va wage_emp {
    bysort isocode (y): gen byte f_ = sum(!missing(`v')) == 1 & !missing(`v')
    gen t_ = `v' if f_
    bysort isocode (t_): gen b_`v' = t_[1]
    drop f_ t_
}
preserve
bysort isocode: keep if _n == 1
foreach v in intl_seat_share tour_rcpt_exp srv_va wage_emp {
    xtile m_`v' = b_`v', nq(2)
}
keep isocode m_*
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate
foreach v in intl_seat_share tour_rcpt_exp srv_va wage_emp {
    foreach yv in ln_gini_mkt ln_spt_b50 ln_apt_top_bot ln_spt_d10 {
        foreach g in 1 2 {
            capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if m_`v' == `g', absorb(isocode y) cluster(isocode)
            if _rc == 0 wr `fh' E `v'_`g' `yv' ln_gaci_max `=e(widstat)'
        }
    }
}
file close `fh'
log close _all
