*==============================================================================
* gaci_3iv_pairs.do  --  PAIRWISE over-ID J tests to pinpoint which heritage type
*   breaks the exclusion restriction.
*   z_nat / z_mix / z_cult  (= tour_shift x ln(1+count) by category)
*   pairs (2 instruments each -> 1 over-id df -> Hansen J):
*     nat+mix   : do natural & mixed AGREE? (J pass => main instrument is internally valid)
*     nat+cult  : do natural & cultural agree? (J reject => cultural is the violator)
*     mix+cult  : completeness
*     all three : reference
*   country+year FE ; robust SE.
*   emits IV3P|pair|outcome|b|se|p|KP_F|HansenJ|Jdf|J_p|N
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_3iv_pairs.log", replace text
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

capture program drop _jp
program define _jp
    syntax, yv(string) insts(string) tag(string)
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm = `insts'), absorb(isocode y) robust
    if _rc==0 {
        local b=_b[ln_gaci_cwm]
        local se=_se[ln_gaci_cwm]
        local p=2*ttail(e(df_r),abs(`b'/`se'))
        local Jp=.
        if !missing(e(j)) & e(jdf)>0  local Jp=chi2tail(e(jdf),e(j))
        noisily di "IV3P|`tag'|`yv'|`b'|`se'|`p'|" e(widstat) "|" e(j) "|" e(jdf) "|`Jp'|" e(N)
    }
    else noisily di "IV3P|`tag'|`yv'|FAIL|.|.|.|.|.|.|."
end

di _n "############ pairwise over-ID J tests ############"
foreach yv in g_int g_vol g_shr lnpc lngdp {
    _jp, yv(`yv') insts(z_nat z_mix)        tag(natmix)
    _jp, yv(`yv') insts(z_nat z_cult)       tag(natcult)
    _jp, yv(`yv') insts(z_mix z_cult)       tag(mixcult)
    _jp, yv(`yv') insts(z_nat z_mix z_cult) tag(three)
}
di "DONE_PAIRS"
log close
