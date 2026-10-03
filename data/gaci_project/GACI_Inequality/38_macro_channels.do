* 38_macro_channels.do : macro channels of the hub-inequality effect (2SLS Feyrer, ln pop, country + year FE, cluster country).
*  A. a-paths: does hub connectivity move (i) spatial concentration [top-region GRP share, Theil, largest-city share],
*     (ii) export composition [differentiated / high value-to-weight / capital-goods shares, high-tech and ICT/service exports],
*     (iii) factor and finance [labour share (PWT), private credit, investment, resource rents, remittances]?
*  B. IV decomposition on ln market Gini and bottom-50 share: c' (hub, instrumented) with the channel as control, and b.
*  C. heterogeneity: baseline median split on top-region share, differentiated-export share, labour share.
* Inputs: ineq_panel_ext.csv, _macro_channels.csv. Output: _macro_channels_results.csv (block,item,outcome,term,b,se,p,kpf,N)
capture log close _all
log using "38_macro_channels_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "_macro_channels.csv", clear varnames(1) encoding("utf-8")
tempfile mc
save `mc'
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `mc', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
capture drop ln_spt_b50
gen ln_spt_b50 = ln_apt_b50 - ln_apt_all
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
capture gen ln_labsh = ln(labsh)
capture gen ln_priv_credit = ln(priv_credit) if priv_credit > 0
capture gen ln_largest_city = ln(largest_city_sh) if largest_city_sh > 0
capture gen ln_hitech = ln(hitech_exp_sh) if hitech_exp_sh > 0
capture gen ln_ict_serv = ln(ict_serv_exp_sh) if ict_serv_exp_sh > 0
capture gen ln_serv_exp_sh = ln(serv_exp_sh) if serv_exp_sh > 0
tempname fh
file open `fh' using "_macro_channels_results.csv", write replace
file write `fh' "block,item,outcome,term,b,se,p,kpf,N" _n
capture program drop wr
program define wr
    args fh blk item yv term kp
    local b = _b[`term']
    local se = _se[`term']
    local p = 2*normal(-abs(`b'/`se'))
    file write `fh' "`blk',`item',`yv',`term',`b',`se',`p',`kp',`=e(N)'" _n
end
local CH "ln_share_topreg ln_theil_reg share_topreg ln_largest_city primacy urban sh_diff sh_homog sh_hivw sh_x_hivw3 sh_capital sh_interm ln_tr_diff ln_tr_hivw ln_nprod ln_nflow ln_hitech ln_ict_serv ln_serv_exp_sh labsh ln_labsh ln_priv_credit gfcf_gdp resource_rents remit_gdp ind_va"
* ---- A. a-paths ----
foreach mv of local CH {
    capture confirm variable `mv'
    if _rc continue
    quietly count if !missing(`mv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 100 continue
    capture noisily ivreghdfe `mv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    if _rc == 0 wr `fh' A apath `mv' ln_gaci_max `=e(widstat)'
    quietly reghdfe `mv' ln_gaci_max lnpop, absorb(isocode y) vce(cluster isocode)
    wr `fh' A apath_ols `mv' ln_gaci_max .
}
* ---- B. IV decomposition ----
foreach yv in ln_gini_mkt ln_spt_b50 ln_apt_top_bot {
    foreach mv of local CH {
        capture confirm variable `mv'
        if _rc continue
        quietly count if !missing(`mv', `yv', ln_gaci_max, feyrer_int, lnpop)
        if r(N) < 100 continue
        capture noisily ivreghdfe `yv' lnpop `mv' (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            wr `fh' B `mv' `yv' ln_gaci_max `=e(widstat)'
            wr `fh' B `mv' `yv' `mv' `=e(widstat)'
        }
    }
}
* ---- C. heterogeneity by baseline median ----
foreach v in share_topreg sh_diff labsh sh_hivw {
    capture confirm variable `v'
    if _rc continue
    bysort isocode (y): gen byte f_ = sum(!missing(`v')) == 1 & !missing(`v')
    gen t_ = `v' if f_
    bysort isocode (t_): gen b_`v' = t_[1]
    drop f_ t_
}
preserve
bysort isocode: keep if _n == 1
foreach v in share_topreg sh_diff labsh sh_hivw {
    capture confirm variable b_`v'
    if _rc continue
    xtile m_`v' = b_`v', nq(2)
}
keep isocode m_*
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate
foreach v in share_topreg sh_diff labsh sh_hivw {
    capture confirm variable m_`v'
    if _rc continue
    foreach yv in ln_gini_mkt ln_spt_b50 ln_apt_top_bot {
        foreach g in 1 2 {
            capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if m_`v' == `g', absorb(isocode y) cluster(isocode)
            if _rc == 0 wr `fh' C `v'_`g' `yv' ln_gaci_max `=e(widstat)'
        }
    }
}
file close `fh'
log close _all
