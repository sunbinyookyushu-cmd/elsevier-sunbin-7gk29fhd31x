*==============================================================================
* gaci_allheritage.do  --  robustness: heritage instrument INCLUDING cultural sites
*   tourism_int = tour_shift x ln(1+ natural+mixed)   [current/clean exclusion]
*   tourism_all = tour_shift x ln(1+ ALL UNESCO)      [incl cultural; stronger 1st stage ~59]
*   treatment ln_gaci_cwm ; country+year FE ; robust SE
*   (1) pooled main: natural vs ALL, each outcome  -> is beta stable? (informal validity check)
*   (2) income interaction IV with the stronger ALL instrument -> does heterogeneity identify?
*   emits ALLH|spec|outcome|b|se|p|KP_F|N   and   HETALL|outcome|term|b|se|p|KP_F|N
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_allheritage.log", replace text
import delimited "gaci_panel_tourism_all.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
gen g_int = merch_intensity
gen g_shr = merch_share
gen g_vol = merch_intensity + lngdp

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

* ---- (1) pooled main: natural vs ALL ----
capture program drop _m2
program define _m2
    args treat spec yv
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm = `treat'), absorb(isocode y) robust
    if _rc==0 {
        local b=_b[ln_gaci_cwm]
        local se=_se[ln_gaci_cwm]
        local p=2*ttail(e(df_r),abs(`b'/`se'))
        noisily di "ALLH|`spec'|`yv'|`b'|`se'|`p'|" e(widstat) "|" e(N)
    }
    else noisily di "ALLH|`spec'|`yv'|FAIL|.|.|.|."
end
di _n "############ POOLED MAIN: natural+mixed vs ALL heritage ############"
foreach yv in g_int g_vol g_shr lnpc lngdp {
    _m2 tourism_int natural `yv'
    _m2 tourism_all allherit `yv'
}

* ---- (2) income interaction with the ALL (stronger) instrument ----
gen tmp = lnpc if y==1996
bysort isocode: egen base_lnpc = max(tmp)
quietly summarize base_lnpc
gen double inc_c = base_lnpc - r(mean)
drop tmp
di _n "############ INCOME interaction IV, instrument = ALL heritage ############"
foreach yv in g_int g_vol g_shr lnpc lngdp {
    capture drop cwm_m z_m
    gen double cwm_m = ln_gaci_cwm * inc_c
    gen double z_m   = tourism_all  * inc_c
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm cwm_m = tourism_all z_m), absorb(isocode y) robust
    if _rc==0 {
        local F=e(widstat)
        local bm=_b[ln_gaci_cwm]
        local sm=_se[ln_gaci_cwm]
        local pm=2*ttail(e(df_r),abs(`bm'/`sm'))
        local bi=_b[cwm_m]
        local si=_se[cwm_m]
        local pi=2*ttail(e(df_r),abs(`bi'/`si'))
        noisily di "HETALL|`yv'|main|`bm'|`sm'|`pm'|`F'|" e(N)
        noisily di "HETALL|`yv'|inter|`bi'|`si'|`pi'|`F'|" e(N)
    }
    else noisily di "HETALL|`yv'|FAIL|.|.|.|.|."
    capture drop cwm_m z_m
}
di "DONE_ALLHERIT"
log close
