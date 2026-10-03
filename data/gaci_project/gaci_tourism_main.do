*==============================================================================
* gaci_tourism_main.do  --  FULL main results, tourism-heritage IV
*   instrument : tourism_int = (world tourism demand_t) x ln(1+natural heritage endowment)
*   treatments : lng (GACI sum) ; ln_gaci_cwm (hub quality)   [two panels]
*   outcomes   : g_vol  ln goods trade volume
*                g_int  ln(goods trade/GDP)  (goods openness)
*                g_shr  goods trade % GDP
*                lnpc   ln GDP per capita    (income)
*                lngdp  ln GDP (total)
*   FE country+year ; robust + clustered SE ; OLS benchmark ; KP first-stage F ; 1996-2019
*   emits MAINP| lines (pipe-delimited) for the Word builder.
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

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

capture program drop _m
program define _m
    args treat yv
    quietly {
        reghdfe `yv' `treat' lnpop, absorb(isocode y) vce(robust)
        local ob = _b[`treat']
        local op = 2*ttail(e(df_r), abs(_b[`treat']/_se[`treat']))
        ivreghdfe `yv' lnpop (`treat' = tourism_int), absorb(isocode y) robust
        local b  = _b[`treat']
        local sr = _se[`treat']
        local pr = 2*ttail(e(df_r), abs(`b'/`sr'))
        local F  = e(widstat)
        local N  = e(N)
        ivreghdfe `yv' lnpop (`treat' = tourism_int), absorb(isocode y) cluster(isocode)
        local sc = _se[`treat']
        local pc = 2*ttail(e(df_r), abs(_b[`treat']/`sc'))
    }
    noisily di "MAINP|`treat'|`yv'|`b'|`sr'|`pr'|`sc'|`pc'|`F'|`ob'|`op'|`N'"
end

* ln_gaci_cwm (hub quality) is the MAIN treatment -> emit first (Panel A); lng = secondary
foreach tr in ln_gaci_cwm lng {
    foreach yv in g_vol g_int g_shr lnpc lngdp {
        _m `tr' `yv'
    }
}
di "DONE_MAIN"
