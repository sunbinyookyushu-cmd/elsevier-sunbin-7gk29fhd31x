*==============================================================================
* gaci_natmix_overid.do  --  MAIN + HETEROGENEITY with natural & mixed entered as
*   TWO SEPARATE instruments (over-identified throughout -> Hansen J at every step).
*   z_nat = tour_shift x ln(1+natural) ; z_mix = tour_shift x ln(1+mixed)
*   MAIN  : (ln_gaci_cwm = z_nat z_mix)
*   HET   : (ln_gaci_cwm  cwm#mod = z_nat z_mix  z_nat#mod z_mix#mod)   [2 endog, 4 IV]
*   country+year FE ; robust SE.
*   emits  MNM|outcome|b|se|p|KP_F|J_p|N
*          HNM|moderator|outcome|term|b|se|p|KP_F|J_p|N   (term = main / inter)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_natmix_overid.log", replace text
import delimited "gaci_panel_3iv.csv", clear varnames(1) encoding("utf-8")
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

* ---- (1) MAIN: natural+mixed as separate instruments (over-ID) ----
di _n "############ MAIN (over-ID: z_nat z_mix) ############"
foreach yv in g_int g_vol g_shr lnpc lngdp {
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm = z_nat z_mix), absorb(isocode y) robust
    if _rc==0 {
        local b=_b[ln_gaci_cwm]
        local se=_se[ln_gaci_cwm]
        local p=2*ttail(e(df_r),abs(`b'/`se'))
        local Jp=.
        if !missing(e(j)) & e(jdf)>0  local Jp=chi2tail(e(jdf),e(j))
        noisily di "MNM|`yv'|`b'|`se'|`p'|" e(widstat) "|`Jp'|" e(N)
    }
    else noisily di "MNM|`yv'|FAIL|.|.|.|.|."
}

* ---- (2) HETEROGENEITY: interaction IV with separate instruments (over-ID) ----
capture program drop _hxj
program define _hxj
    args modvar modname
    foreach yv in g_int g_vol g_shr lnpc lngdp {
        capture drop cwm_m zn_m zx_m
        gen double cwm_m = ln_gaci_cwm * `modvar'
        gen double zn_m  = z_nat * `modvar'
        gen double zx_m  = z_mix * `modvar'
        capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm cwm_m = z_nat z_mix zn_m zx_m), absorb(isocode y) robust
        if _rc==0 {
            local F=e(widstat)
            local Jp=.
            if !missing(e(j)) & e(jdf)>0  local Jp=chi2tail(e(jdf),e(j))
            local bm=_b[ln_gaci_cwm]
            local sm=_se[ln_gaci_cwm]
            local pm=2*ttail(e(df_r),abs(`bm'/`sm'))
            local bi=_b[cwm_m]
            local si=_se[cwm_m]
            local pi=2*ttail(e(df_r),abs(`bi'/`si'))
            noisily di "HNM|`modname'|`yv'|main|`bm'|`sm'|`pm'|`F'|`Jp'|" e(N)
            noisily di "HNM|`modname'|`yv'|inter|`bi'|`si'|`pi'|`F'|`Jp'|" e(N)
        }
        else noisily di "HNM|`modname'|`yv'|FAIL|.|.|.|.|.|."
        capture drop cwm_m zn_m zx_m
    }
end
di _n "############ HETEROGENEITY (over-ID interaction) ############"
_hxj inc_c   income
_hxj rem_c   remote
_hxj pop_c   population
_hxj land_c  land
_hxj gdp_c   gdptot
_hxj cwm0_c  baseconn
di "DONE_NATMIX"
log close
