*==============================================================================
* gaci_combined_iv.do  --  OVER-IDENTIFIED IV: combine the two instruments
*   treatment  : ln_gaci_cwm (hub quality)
*   instruments: tourism_int (tourism-heritage Bartik)  +  feyrer_int (air/sea geography)
*   control    : ln_sea_ma (maritime channel, for the Feyrer exclusion); + lnpop
*   FE         : country + year ; robust SE
*   For each outcome, 4 specs: tourism-only | feyrer-only | BOTH (over-ID + Hansen J) |
*                              BOTH on 1996-2019 (pre-COVID, stronger instrument).
*   emits: COMB|spec|outcome|b|se|p|KP_F|HansenJ|J_p|N     (spec = tour/feyr/both/both19)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/ext2024"
capture log close _all
log using "gaci_combined_iv_run.log", replace text
import delimited "gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen g_int = merch_intensity                 // ln(goods/GDP)  = openness (MAIN)
gen g_shr = merch_share
gen g_vol = merch_intensity + lngdp

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

capture program drop _ci
program define _ci
    syntax, yv(string) insts(string) tag(string) sample(string)
    capture noisily ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = `insts') if `sample', absorb(isocode y) robust
    if _rc==0 {
        local b  = _b[ln_gaci_cwm]
        local se = _se[ln_gaci_cwm]
        local p  = 2*ttail(e(df_r), abs(`b'/`se'))
        local Jp = .
        if !missing(e(j)) & e(jdf)>0  local Jp = chi2tail(e(jdf), e(j))
        noisily di "COMB|`tag'|`yv'|`b'|`se'|`p'|" e(widstat) "|" e(j) "|`Jp'|" e(N)
    }
    else noisily di "COMB|`tag'|`yv'|FAIL|.|.|.|.|.|."
end

foreach yv in g_int g_vol g_shr lnpc lngdp {
    _ci, yv(`yv') insts(tourism_int)             tag(tour)   sample(1==1)
    _ci, yv(`yv') insts(feyrer_int)              tag(feyr)   sample(1==1)
    _ci, yv(`yv') insts(tourism_int feyrer_int)  tag(both)   sample(1==1)
    _ci, yv(`yv') insts(tourism_int feyrer_int)  tag(both19) sample(y<=2019)
}
di "DONE_COMBINED"
log close
