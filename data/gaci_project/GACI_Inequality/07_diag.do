capture log close _all
log using "07_diag_run.log", replace text
do "_prep.doh"
* exposure x trend controls (shift-share validity checks)
gen at_basepc = a_t*basepc
gen at_basegini = a_t*basegini
gen at_lnland = a_t*lnland
gen at_abslat = a_t*abslat
gen at_seama = a_t*ln_sea_ma
bysort isocode (y): gen basetrade = trade_share[1]
gen at_basetrade = a_t*basetrade
tempname fh
file open `fh' using "_diag_results.csv", write replace
file write `fh' "block,outcome,spec,term,b,se,p,kpf,N" _n
* A. per-continent first stage and reduced form, both IVs
levelsof cont, local(cl)
foreach ivv in feyrer_int tourism_int {
    foreach cc of local cl {
        capture reghdfe ln_gaci_max `ivv' lnpop if cont=="`cc'", absorb(isocode y) vce(robust)
        if _rc==0 {
            local b = _b[`ivv']
            local se = _se[`ivv']
            local p = 2*ttail(e(df_r), abs(`b'/`se'))
            local nn = e(N)
            test `ivv'
            local F = r(F)
            file write `fh' "fs_cont,ln_gaci_max,`ivv',`cc',`b',`se',`p',`F',`nn'" _n
            reghdfe ln_gini_mkt `ivv' lnpop if cont=="`cc'", absorb(isocode y) vce(robust)
            local b = _b[`ivv']
            local se = _se[`ivv']
            local p = 2*ttail(e(df_r), abs(`b'/`se'))
            local nn = e(N)
            file write `fh' "rf_cont,ln_gini_mkt,`ivv',`cc',`b',`se',`p',.,`nn'" _n
        }
    }
}
* B. pooled variants
foreach yv in ln_gini_mkt ln_gini_disp {
    foreach ivv in feyrer_int tourism_int {
        * B1. continent x year FE
        ivreghdfe `yv' lnpop (ln_gaci_max = `ivv'), absorb(isocode contid#y) robust
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "pooled,`yv',`ivv',cont_x_year,`b',`se',`p',`kp',`nn'" _n
        * B2. continent x year FE, drop LA
        ivreghdfe `yv' lnpop (ln_gaci_max = `ivv') if cont!="LA", absorb(isocode contid#y) robust
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "pooled,`yv',`ivv',cont_x_year_dropLA,`b',`se',`p',`kp',`nn'" _n
        * B3. exposure x trend controls
        ivreghdfe `yv' lnpop at_basepc at_basegini at_lnland at_abslat (ln_gaci_max = `ivv'), absorb(isocode y) robust
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "pooled,`yv',`ivv',exposure_trends,`b',`se',`p',`kp',`nn'" _n
        ivreghdfe `yv' lnpop at_basepc at_basegini at_lnland at_abslat at_seama at_basetrade (ln_gaci_max = `ivv'), absorb(isocode contid#y) robust
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "pooled,`yv',`ivv',exposure_trends_contyear,`b',`se',`p',`kp',`nn'" _n
        * B4. income-tercile x year FE and baseline-gini tercile x year FE
        ivreghdfe `yv' lnpop (ln_gaci_max = `ivv'), absorb(isocode inc3#y gini3#y) robust
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "pooled,`yv',`ivv',inc3_gini3_x_year,`b',`se',`p',`kp',`nn'" _n
        * B5. all of the above
        ivreghdfe `yv' lnpop at_basepc at_basegini at_lnland at_abslat at_seama (ln_gaci_max = `ivv'), absorb(isocode contid#y inc3#y gini3#y) robust
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "pooled,`yv',`ivv',kitchen_sink,`b',`se',`p',`kp',`nn'" _n
        * B6. OLS counterparts
        reghdfe `yv' ln_gaci_max lnpop, absorb(isocode contid#y inc3#y gini3#y) vce(robust)
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*ttail(e(df_r), abs(`b'/`se'))
        local nn = e(N)
        file write `fh' "pooled,`yv',OLS,kitchen_sink_FE,`b',`se',`p',.,`nn'" _n
    }
    * B7. both IVs, continent x year FE + exposure trends, Hansen J
    ivreghdfe `yv' lnpop at_basepc at_basegini at_lnland at_abslat at_seama (ln_gaci_max = feyrer_int tourism_int), absorb(isocode contid#y) robust
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    local jp = e(jp)
    file write `fh' "pooled,`yv',both,contyear_exposure_J,`b',`se',`p',`kp',`nn'" _n
    file write `fh' "pooled,`yv',both,hansen_p,`jp',.,.,.,`nn'" _n
    * B8. drop each continent under continent x year FE (feyrer)
    foreach cc of local cl {
        ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if cont!="`cc'", absorb(isocode contid#y) robust
        local b = _b[ln_gaci_max]
        local se = _se[ln_gaci_max]
        local p = 2*normal(-abs(`b'/`se'))
        local kp = e(widstat)
        local nn = e(N)
        file write `fh' "loo_contyear,`yv',feyrer_int,drop_`cc',`b',`se',`p',`kp',`nn'" _n
    }
}
file close `fh'
log close
