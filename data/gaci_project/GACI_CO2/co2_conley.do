*==============================================================================
* co2_conley.do
* Conley plausibly-exogenous UCI bounds for the CO2 outcome (mirror of the
* trade paper gaci_conley.do). Outcome = ln_co2_bunker, treatment = ln_gaci_cwm.
* gamma in [0, gmax] (violation channels raise both travel and emissions).
* Output: batch log + _co2_conley_results.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "gaci_co2_panel.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
gen ln_intensity = ln_co2_bunker - ln_seatkm

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

tempname R
postfile `R' str20 outc double(betaiv seiv rfcoef rfse lb10 ub10 lb20 ub20 lb30 ub30 fstar nn) using "_co2_conley_tmp", replace

foreach yv in ln_co2_bunker_intl ln_intensity ln_co2_bunker {
    di _n "==================== OUTCOME: `yv' ===================="
    reghdfe `yv' tourism_int lnpop, absorb(isocode y) vce(robust)
    local rfc = _b[tourism_int]
    local rfs = _se[tourism_int]
    ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
    local biv = _b[ln_gaci_cwm]
    local siv = _se[ln_gaci_cwm]
    local nn = e(N)
    local ub0 = `biv' + 1.959964*`siv'
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
use "_co2_conley_tmp", clear
list, clean
export delimited "_co2_conley_results.csv", replace
erase "_co2_conley_tmp.dta"
di _n "DONE_CO2_CONLEY"
