capture log close _all
log using "06_tails_run.log", replace text
do "_prep.doh"
tempname fh
file open `fh' using "_tails_results.csv", write replace
file write `fh' "block,outcome,treat,model,b,se,p,kpf,N" _n
* WID pretax and post-tax shares; SWIID reference
foreach yv in ln_top10_wid ln_top1_wid ln_bot50_wid ratio_t10_b50 ln_gini_pre_wid ln_gini_post_wid ln_top10_post_wid ln_bot50_post_wid top10_wid top1_wid bot50_wid {
    foreach tr in ln_gaci_max ln_gaci_cwm ln_gaci_sum {
        reghdfe `yv' `tr' lnpop, absorb(isocode y) vce(robust)
        local b = _b[`tr']
        local se = _se[`tr']
        local p = 2*ttail(e(df_r), abs(`b'/`se'))
        local nn = e(N)
        file write `fh' "tails,`yv',`tr',OLS,`b',`se',`p',.,`nn'" _n
        ivreghdfe `yv' lnpop (`tr' = feyrer_int), absorb(isocode y) robust
        local b = _b[`tr']
        local se = _se[`tr']
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "tails,`yv',`tr',IV,`b',`se',`p',`kp',`nn'" _n
        ivreghdfe `yv' lnpop (`tr' = feyrer_int), absorb(isocode y) cluster(isocode)
        local b = _b[`tr']
        local se = _se[`tr']
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "tails,`yv',`tr',IVcl,`b',`se',`p',`kp',`nn'" _n
    }
}
* redistribution wedge: post-tax minus pre-tax top10 share, and pre/post gini gap
gen wedge_top10 = top10_wid - top10_post_wid
gen wedge_gini = gini_pre_wid - gini_post_wid
gen wedge_swiid = gini_mkt - gini_disp
foreach yv in wedge_top10 wedge_gini wedge_swiid {
    reghdfe `yv' ln_gaci_max lnpop, absorb(isocode y) vce(robust)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "wedge,`yv',ln_gaci_max,OLS,`b',`se',`p',.,`nn'" _n
    ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) robust
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "wedge,`yv',ln_gaci_max,IV,`b',`se',`p',`kp',`nn'" _n
    ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "wedge,`yv',ln_gaci_max,IVcl,`b',`se',`p',`kp',`nn'" _n
}
* tails heterogeneity by baseline income tercile (interaction IV)
foreach yv in ln_top10_wid ln_bot50_wid {
    ivreghdfe `yv' lnpop (ln_gaci_max ln_gaci_max_mid ln_gaci_max_high = feyrer_int feyrer_int_mid feyrer_int_high), absorb(isocode y) robust
    local kp = e(widstat)
    local nn = e(N)
    foreach t in ln_gaci_max ln_gaci_max_mid ln_gaci_max_high {
        local b = _b[`t']
        local se = _se[`t']
        local p = 2*normal(-abs(`b'/`se'))
        file write `fh' "tails_inc3,`yv',`t',IV,`b',`se',`p',`kp',`nn'" _n
    }
    lincom ln_gaci_max + ln_gaci_max_mid
    file write `fh' "tails_inc3,`yv',mid_total,IV,`r(estimate)',`r(se)',`r(p)',.,`nn'" _n
    lincom ln_gaci_max + ln_gaci_max_high
    file write `fh' "tails_inc3,`yv',high_total,IV,`r(estimate)',`r(se)',`r(p)',.,`nn'" _n
}
file close `fh'
log close
