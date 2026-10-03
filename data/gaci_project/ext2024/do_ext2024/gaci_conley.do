*==============================================================================
* gaci_conley.do
* Conley, Hansen & Rossi (2012) plausibly-exogenous UCI bounds, tourism IV.
*   gamma = direct effect of tourism_int on the outcome (exclusion violation).
*   Prior support gamma in [0, gmax]: the candidate violation channels
*   (induced surface travel, direct tourism demand) all RAISE trade, so the
*   conservative direction is gamma >= 0.
*   UCI = union over the gamma grid of 95% CIs from 2SLS of (y - gamma*Z).
*   Because beta(gamma) is monotone in gamma, the union endpoints are the
*   lower bound at gamma = gmax and the upper bound at gamma = 0.
*   Benchmarks: gmax = {10,20,30}% of the reduced-form coefficient.
*   Breakdown f* = largest gamma/RF (grid 0.01) with CI lower bound still > 0.
* Treatment = ln_gaci_cwm (headline). Country+year FE, robust SE.
* Output: gaci_conley.log + _conley_results.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/ext2024"
* batch mode (/e) writes gaci_conley.log automatically

import delimited "gaci_panel_3iv.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen g_int = merch_intensity
gen g_vol = merch_intensity + lngdp
gen g_gdp = lngdp

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

tempname R
postfile `R' str8 outc double(betaiv seiv rfcoef rfse lb10 ub10 lb20 ub20 lb30 ub30 fstar nn) using "_conley_tmp", replace

foreach yv in g_int g_vol g_gdp {
    di _n "==================== OUTCOME: `yv' ===================="

    * ---- reduced form ----
    reghdfe `yv' tourism_int lnpop, absorb(isocode y) vce(robust)
    local rfc = _b[tourism_int]
    local rfs = _se[tourism_int]

    * ---- baseline 2SLS (gamma = 0) ----
    ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
    local biv = _b[ln_gaci_cwm]
    local siv = _se[ln_gaci_cwm]
    local nn = e(N)
    local ub0 = `biv' + 1.959964*`siv'

    * ---- UCI bounds at benchmark gmax = f% of the reduced form ----
    foreach f in 10 20 30 {
        local g = (`f'/100)*`rfc'
        capture drop ytil
        gen ytil = `yv' - `g'*tourism_int
        quietly ivreghdfe ytil lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
        local lb`f' = _b[ln_gaci_cwm] - 1.959964*_se[ln_gaci_cwm]
        local ub`f' = `ub0'
        drop ytil
        di "  gmax = `f'% of RF: UCI = [" %9.3f `lb`f'' ", " %9.3f `ub`f'' "]"
    }

    * ---- breakdown fraction f* ----
    local fstar = 0
    local f = 0
    local go = 1
    while `go' {
        local f = `f' + 0.01
        if `f' > 2.001 {
            local go = 0
        }
        else {
            local g = `f'*`rfc'
            capture drop ytil
            gen ytil = `yv' - `g'*tourism_int
            quietly ivreghdfe ytil lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
            local lbf = _b[ln_gaci_cwm] - 1.959964*_se[ln_gaci_cwm]
            drop ytil
            if `lbf' > 0 {
                local fstar = `f'
            }
            else {
                local go = 0
            }
        }
    }
    di "  breakdown fraction f* = " %6.2f `fstar'

    post `R' ("`yv'") (`biv') (`siv') (`rfc') (`rfs') (`lb10') (`ub10') (`lb20') (`ub20') (`lb30') (`ub30') (`fstar') (`nn')
}

postclose `R'
use "_conley_tmp", clear
list, clean
export delimited "_conley_results.csv", replace
erase "_conley_tmp.dta"
di _n "DONE_CONLEY"
