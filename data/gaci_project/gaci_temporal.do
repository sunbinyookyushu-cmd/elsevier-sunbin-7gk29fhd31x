*==============================================================================
* gaci_temporal.do  --  TEMPORAL heterogeneity: has the connectivity->trade effect
*   changed over time?  Split at the data midpoint (1996-2023 -> 2010).
*   treatment ln_gaci_cwm ; instrument tourism_int (natural+mixed) ; country+year FE.
*   (A) split:  effect in 1996-2009  vs  2010-2023   (each: cwm = tourism_int)
*   (B) interaction: cwm + cwm#post instrumented by tourism_int + tourism_int#post
*       -> 'inter' = how much the effect differs post-2010 (formal difference test)
*   NOTE: tourism_int collapses in 2020-21 (COVID), so the post-2010 first stage is
*         weaker; read the post window with that caveat.
*   emits TSPL|period|outcome|b|se|p|KP_F|N   and   TEMP|outcome|term|b|se|p|KP_F|N
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_temporal.log", replace text
import delimited "gaci_panel_tourism_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
gen g_int = merch_intensity
gen g_shr = merch_share
gen g_vol = merch_intensity + lngdp
gen post = (y>=2010)

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

* ---- (A) pre/post split ----
capture program drop _t
program define _t
    args lbl cond
    foreach yv in g_int g_vol g_shr lnpc lngdp {
        capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int) if `cond', absorb(isocode y) robust
        if _rc==0 {
            local b=_b[ln_gaci_cwm]
            local se=_se[ln_gaci_cwm]
            local p=2*ttail(e(df_r),abs(`b'/`se'))
            noisily di "TSPL|`lbl'|`yv'|`b'|`se'|`p'|" e(widstat) "|" e(N)
        }
        else noisily di "TSPL|`lbl'|`yv'|FAIL|.|.|.|."
    }
end
di _n "############ pre 1996-2009 ############"
_t pre "y<2010"
di _n "############ post 2010-2023 ############"
_t post "y>=2010"

* ---- (B) interaction (formal difference) ----
di _n "############ interaction: cwm + cwm#post ############"
foreach yv in g_int g_vol g_shr lnpc lngdp {
    capture drop cwm_p z_p
    gen double cwm_p = ln_gaci_cwm * post
    gen double z_p   = tourism_int  * post
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm cwm_p = tourism_int z_p), absorb(isocode y) robust
    if _rc==0 {
        local F=e(widstat)
        local bm=_b[ln_gaci_cwm]
        local sm=_se[ln_gaci_cwm]
        local pm=2*ttail(e(df_r),abs(`bm'/`sm'))
        local bi=_b[cwm_p]
        local si=_se[cwm_p]
        local pi=2*ttail(e(df_r),abs(`bi'/`si'))
        noisily di "TEMP|`yv'|main|`bm'|`sm'|`pm'|`F'|" e(N)
        noisily di "TEMP|`yv'|inter|`bi'|`si'|`pi'|`F'|" e(N)
    }
    else noisily di "TEMP|`yv'|FAIL|.|.|.|.|."
    capture drop cwm_p z_p
}
di "DONE_TEMPORAL"
log close
