capture log close _all
log using "08_openskies_run.log", replace text
do "_prep.doh"
* Open Skies staggered adoption: drop always-treated (applied before 1997)
drop if os_year<=1996 & !missing(os_year)
gen treated = !missing(os_year)
* event-time dummies, window -6..+10 with binned endpoints, omit t=-1
gen evt = os_evt
replace evt = -6 if evt < -6 & !missing(evt)
replace evt = 10 if evt > 10 & !missing(evt)
forvalues k = 6(-1)2 {
    gen ev_m`k' = (evt==-`k')
}
forvalues k = 0/10 {
    gen ev_p`k' = (evt==`k')
}
tempname fh
file open `fh' using "_openskies_results.csv", write replace
file write `fh' "block,outcome,term,b,se,p,kpf,N" _n
foreach yv in ln_gaci_max ln_gaci_cwm ln_gaci_sum ln_gini_mkt ln_gini_disp ln_bot50_wid ln_top10_wid {
    * A. TWFE DiD
    reghdfe `yv' post_os lnpop, absorb(isocode y) cluster(isocode)
    local b = _b[post_os]
    local se = _se[post_os]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "did,`yv',post_os,`b',`se',`p',.,`nn'" _n
    reghdfe `yv' post_os lnpop, absorb(isocode contid#y) cluster(isocode)
    local b = _b[post_os]
    local se = _se[post_os]
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    local nn = e(N)
    file write `fh' "did_contyear,`yv',post_os,`b',`se',`p',.,`nn'" _n
    * B. event study (TWFE)
    reghdfe `yv' ev_m6 ev_m5 ev_m4 ev_m3 ev_m2 ev_p0-ev_p10 lnpop, absorb(isocode y) cluster(isocode)
    local nn = e(N)
    foreach t in ev_m6 ev_m5 ev_m4 ev_m3 ev_m2 ev_p0 ev_p1 ev_p2 ev_p3 ev_p4 ev_p5 ev_p6 ev_p7 ev_p8 ev_p9 ev_p10 {
        local b = _b[`t']
        local se = _se[`t']
        local p = 2*ttail(e(df_r), abs(`b'/`se'))
        file write `fh' "es,`yv',`t',`b',`se',`p',.,`nn'" _n
    }
    test ev_m6 ev_m5 ev_m4 ev_m3 ev_m2
    file write `fh' "es_pretrend_F,`yv',joint_pre,`r(F)',.,`r(p)',.,`nn'" _n
}
* C. Open Skies as instrument for connectivity
foreach yv in ln_gini_mkt ln_gini_disp ln_bot50_wid ln_top10_wid {
    ivreghdfe `yv' lnpop (ln_gaci_max = post_os), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "iv_os,`yv',ln_gaci_max,`b',`se',`p',`kp',`nn'" _n
    ivreghdfe `yv' lnpop (ln_gaci_max = post_os), absorb(isocode contid#y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local nn = e(N)
    file write `fh' "iv_os_contyear,`yv',ln_gaci_max,`b',`se',`p',`kp',`nn'" _n
    ivreghdfe `yv' lnpop (ln_gaci_max = post_os feyrer_int), absorb(isocode y) cluster(isocode)
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    local kp = e(widstat)
    local jp = e(jp)
    local nn = e(N)
    file write `fh' "iv_os_feyrer,`yv',ln_gaci_max,`b',`se',`p',`kp',`nn'" _n
    file write `fh' "iv_os_feyrer,`yv',hansen_p,`jp',.,.,.,`nn'" _n
}
* D. Callaway-Sant'Anna if available
capture which csdid
if _rc==0 {
    gen gvar = os_year
    replace gvar = 0 if missing(gvar)
    foreach yv in ln_gaci_max ln_gini_mkt ln_gini_disp {
        capture noisily csdid `yv' lnpop, ivar(isocode) time(y) gvar(gvar) method(dripw) notyet
        if _rc==0 {
            capture noisily estat simple
            if _rc==0 {
                matrix b = r(b)
                matrix V = r(V)
                local bb = b[1,1]
                local ss = sqrt(V[1,1])
                local p = 2*normal(-abs(`bb'/`ss'))
                file write `fh' "csdid_simple,`yv',att,`bb',`ss',`p',.,`e(N)'" _n
            }
        }
    }
}
file close `fh'
log close
