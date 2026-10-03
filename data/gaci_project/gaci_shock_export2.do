*==============================================================================
* gaci_shock_export2.do  --  COVID/Russia shock interaction across ALL 5 outcomes
*   model: IV with both shocks, ln_gaci_cwm + cwm#covid + cwm#russia instrumented by
*          tourism_int + its interactions. Outcomes as columns (parallel to Tables 1-2).
*   treatment = ln_gaci_cwm (hub quality)  [MAIN VARIABLE]
*   emits SHOCK2|outcome|term|b|se|p|F|N   (term = ln_gaci_cwm / gaci_c / gaci_r)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel_tourism_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
gen g_int = merch_intensity
gen g_shr = merch_share
gen g_vol = merch_intensity + lngdp
gen covid=inrange(y,2020,2021)
gen russia=(y>=2022)
gen gaci_c=ln_gaci_cwm*covid
gen gaci_r=ln_gaci_cwm*russia
gen z=tourism_int
gen z_c=tourism_int*covid
gen z_r=tourism_int*russia

capture program drop _emit
program define _emit
    args yv v F
    di "SHOCK2|`yv'|`v'|" _b[`v'] "|" _se[`v'] "|" 2*ttail(e(df_r),abs(_b[`v']/_se[`v'])) "|`F'|" e(N)
end

foreach yv in g_vol g_int g_shr lnpc lngdp {
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm gaci_c gaci_r = z z_c z_r), absorb(isocode y) robust
    if _rc==0 {
        local F=e(widstat)
        foreach v in ln_gaci_cwm gaci_c gaci_r {
            _emit `yv' `v' `F'
        }
    }
}
di "DONE_SHOCK2"
