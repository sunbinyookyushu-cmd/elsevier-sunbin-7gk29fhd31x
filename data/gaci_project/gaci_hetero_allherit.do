*==============================================================================
* gaci_hetero_allherit.do  --  heterogeneity (interaction IV) with the STRONGER
*   ALL-heritage instrument (tourism_all = tour_shift x ln(1+ ALL UNESCO sites)).
*   Re-tests every moderator we tried, to see if the stronger 1st stage rescues ID.
*   treatment ln_gaci_cwm ; instrument tourism_all ; country+year FE ; robust SE.
*   emits HETA|moderator|outcome|term|b|se|p|KP_F|N    (term = main / inter)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_hetero_allherit.log", replace text
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

* ---- moderators, mean-centered (1996 baseline where time-varying) ----
quietly summarize ln_remote
gen double rem_c = ln_remote - r(mean)
gen tmp = lnpc if y==1996
bysort isocode: egen base_lnpc = max(tmp)
quietly summarize base_lnpc
gen double inc_c = base_lnpc - r(mean)
drop tmp
gen tmp = lnpop if y==1996
bysort isocode: egen base_lnpop = max(tmp)
quietly summarize base_lnpop
gen double pop_c = base_lnpop - r(mean)
drop tmp
quietly summarize lnland
gen double land_c = lnland - r(mean)
gen tmp = lngdp if y==1996
bysort isocode: egen base_lngdp = max(tmp)
quietly summarize base_lngdp
gen double gdp_c = base_lngdp - r(mean)
drop tmp
gen tmp = ln_gaci_cwm if y==1996
bysort isocode: egen base_cwm = max(tmp)
quietly summarize base_cwm
gen double cwm0_c = base_cwm - r(mean)
drop tmp

capture program drop _hx
program define _hx
    args modvar modname
    foreach yv in g_int g_vol g_shr lnpc lngdp {
        capture drop cwm_m z_m
        gen double cwm_m = ln_gaci_cwm * `modvar'
        gen double z_m   = tourism_all  * `modvar'
        capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm cwm_m = tourism_all z_m), absorb(isocode y) robust
        if _rc==0 {
            local F=e(widstat)
            local bm=_b[ln_gaci_cwm]
            local sm=_se[ln_gaci_cwm]
            local pm=2*ttail(e(df_r),abs(`bm'/`sm'))
            local bi=_b[cwm_m]
            local si=_se[cwm_m]
            local pi=2*ttail(e(df_r),abs(`bi'/`si'))
            noisily di "HETA|`modname'|`yv'|main|`bm'|`sm'|`pm'|`F'|" e(N)
            noisily di "HETA|`modname'|`yv'|inter|`bi'|`si'|`pi'|`F'|" e(N)
        }
        else noisily di "HETA|`modname'|`yv'|FAIL|.|.|.|.|."
        capture drop cwm_m z_m
    }
end

di _n "############ remoteness ############"
_hx rem_c remote
di _n "############ income (1996 GDPpc) ############"
_hx inc_c income
di _n "############ population (1996) ############"
_hx pop_c population
di _n "############ land area ############"
_hx land_c land
di _n "############ GDP total (1996) ############"
_hx gdp_c gdptot
di _n "############ baseline connectivity (1996 cwm) ############"
_hx cwm0_c baseconn
di "DONE_HETA"
log close
