*==============================================================================
* gaci_3iv.do  --  three SEPARATE heritage instruments -> OVER-IDENTIFIED IV + Hansen J
*   z_nat  = tour_shift x ln(1+ natural sites)
*   z_mix  = tour_shift x ln(1+ mixed sites)
*   z_cult = tour_shift x ln(1+ cultural sites)
*   3 instruments, 1 endogenous (ln_gaci_cwm) -> 2 over-id restrictions -> Hansen J test.
*   Idea: let the DATA test whether cultural heritage is a valid instrument.
*     Hansen J p > 0.10  -> the three heritage types AGREE  -> cultural OK to include (valid).
*     Hansen J p < 0.05  -> they DISAGREE -> at least one (likely cultural) violates exclusion.
*   country+year FE ; robust SE.  emits:
*   IV3|spec|outcome|b|se|p|KP_F|HansenJ|Jdf|J_p|N      (spec = nat / three)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_3iv.log", replace text
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

capture program drop _j
program define _j
    syntax, yv(string) insts(string) tag(string)
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm = `insts'), absorb(isocode y) robust
    if _rc==0 {
        local b=_b[ln_gaci_cwm]
        local se=_se[ln_gaci_cwm]
        local p=2*ttail(e(df_r),abs(`b'/`se'))
        local Jp=.
        if !missing(e(j)) & e(jdf)>0  local Jp=chi2tail(e(jdf),e(j))
        noisily di "IV3|`tag'|`yv'|`b'|`se'|`p'|" e(widstat) "|" e(j) "|" e(jdf) "|`Jp'|" e(N)
    }
    else noisily di "IV3|`tag'|`yv'|FAIL|.|.|.|.|.|.|."
end

di _n "############ natural-only  vs  three-heritage (over-ID + Hansen J) ############"
foreach yv in g_int g_vol g_shr lnpc lngdp {
    _j, yv(`yv') insts(z_nat)              tag(nat)
    _j, yv(`yv') insts(z_nat z_mix z_cult) tag(three)
}
di "DONE_3IV"
log close
