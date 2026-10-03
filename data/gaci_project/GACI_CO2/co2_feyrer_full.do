*==============================================================================
* co2_feyrer_full.do
* FULL RESULTS SUITE under the Feyrer air/sea IV (feyrer_int; ln_sea_ma
* always controlled). Mirrors the tourism-IV suite for comparison.
*   A) main outcomes: total/LTO/50-50/intl CO2, seat-km, intensity + trade
*      openness and volume (internal consistency for the carbon price)
*   B) H2 measures (cwm / sum / max), outcome = intl CO2
*   C) H3 temporal split (intl CO2, trade volume)
*   D) Conley UCI bounds (intl, total, intensity)
*   E) RF quintile heterogeneity (intl CO2, shifter = feyrer_int)
* Exports: _feyrer_main_results.csv, _feyrer_conley.csv, _feyrer_rf_quintile.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

* ---- build merged dataset ----
import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl co2_lto co2_5050 dep_seat_km
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "../gaci_panel_measures.csv", clear varnames(1) encoding("utf-8")
keep c y ln_gaci_max
tempfile mx
save `mx'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `mx', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_co2_lto = ln(co2_lto) if co2_lto > 0
gen ln_co2_5050 = ln(co2_5050) if co2_5050 > 0
gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm
gen g_int = merch_intensity
gen g_vol = merch_intensity + lngdp

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}
capture which esttab
if _rc {
    ssc install estout, replace
}

* =====================================================================
* A) MAIN outcomes
* =====================================================================
eststo clear
foreach yv in ln_co2_tot ln_co2_lto ln_co2_5050 ln_co2_intl ln_skm ln_intensity g_int g_vol {
    ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    eststo f_`yv'
    estadd scalar KPF = e(widstat)
    test ln_gaci_cwm = 1
    estadd scalar Wald1p = r(p)
    di "MAIN `yv': b = " %9.3f _b[ln_gaci_cwm] " (se " %8.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat) "  Wald p(b=1) = " %6.3f r(p) "  N = " %8.0f e(N)
}
esttab f_* using "_feyrer_main_results.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) stats(KPF Wald1p N) plain

* =====================================================================
* B) H2 measures, outcome = intl CO2
* =====================================================================
foreach tr in ln_gaci_cwm lng ln_gaci_max {
    ivreghdfe ln_co2_intl lnpop ln_sea_ma (`tr' = feyrer_int), absorb(isocode y) robust
    test `tr' = 1
    di "H2 `tr': b = " %9.3f _b[`tr'] " (se " %8.3f _se[`tr'] ")  KP F = " %7.1f e(widstat) "  Wald p(b=1) = " %6.3f r(p)
}

* =====================================================================
* C) H3 temporal split
* =====================================================================
foreach yv in ln_co2_intl g_vol {
    ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y < 2010, absorb(isocode y) robust
    di "H3 `yv' pre-2010:  b = " %9.3f _b[ln_gaci_cwm] " (se " %8.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat)
    ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y >= 2010, absorb(isocode y) robust
    di "H3 `yv' post-2010: b = " %9.3f _b[ln_gaci_cwm] " (se " %8.3f _se[ln_gaci_cwm] ")  KP F = " %7.1f e(widstat)
}

* =====================================================================
* D) Conley UCI (gamma = direct effect of feyrer_int, [0, gmax])
* =====================================================================
tempname R
postfile `R' str16 outc double(betaiv seiv rfcoef lb10 lb20 lb30 ub0 fstar nn) using "_fey_conley_tmp", replace
foreach yv in ln_co2_intl ln_co2_tot ln_intensity {
    reghdfe `yv' feyrer_int lnpop ln_sea_ma, absorb(isocode y) vce(robust)
    local rfc = _b[feyrer_int]
    ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    local biv = _b[ln_gaci_cwm]
    local siv = _se[ln_gaci_cwm]
    local nn = e(N)
    local ub0 = `biv' + 1.959964*`siv'
    foreach f in 10 20 30 {
        local g = (`f'/100)*`rfc'
        capture drop ytil
        gen ytil = `yv' - `g'*feyrer_int
        quietly ivreghdfe ytil lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
        local lb`f' = _b[ln_gaci_cwm] - 1.959964*_se[ln_gaci_cwm]
        drop ytil
    }
    local sgn = 1
    if `biv' < 0 {
        local sgn = -1
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
            gen ytil = `yv' - `g'*feyrer_int
            quietly ivreghdfe ytil lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
            local lbf = `sgn'*(_b[ln_gaci_cwm] - `sgn'*1.959964*_se[ln_gaci_cwm])
            drop ytil
            if `lbf' > 0 {
                local fstar = `f'
            }
            else {
                local go = 0
            }
        }
    }
    di "CONLEY `yv': b = " %8.3f `biv' "  UCI30 lb = " %8.3f `lb30' "  f* = " %5.2f `fstar'
    post `R' ("`yv'") (`biv') (`siv') (`rfc') (`lb10') (`lb20') (`lb30') (`ub0') (`fstar') (`nn')
}
postclose `R'
preserve
use "_fey_conley_tmp", clear
list, clean
export delimited "_feyrer_conley.csv", replace
restore
erase "_fey_conley_tmp.dta"

* =====================================================================
* E) RF quintile heterogeneity (shifter = feyrer_int, outcome = intl CO2)
* =====================================================================
gen tmp = lnpc if y==1996
bysort isocode: egen base_lnpc = max(tmp)
drop tmp
gen tmp = ln_gaci_cwm if y==1996
bysort isocode: egen base_cwm = max(tmp)
drop tmp
gen byte insamp = !missing(ln_co2_intl) & !missing(lnpop) & !missing(feyrer_int)
preserve
keep if insamp
collapse (first) base_lnpc base_cwm ln_remote, by(isocode)
xtile q_inc = base_lnpc, nq(5)
xtile q_con = base_cwm, nq(5)
xtile q_rem = ln_remote, nq(5)
tempfile qq
save `qq'
restore
merge m:1 isocode using `qq', nogenerate keepusing(q_inc q_con q_rem)

tempname Q
postfile `Q' str8 mod byte bin double(b se) long(nn) using "_fey_rf_tmp", replace
foreach m in inc con rem {
    reghdfe ln_co2_intl ibn.q_`m'#c.feyrer_int lnpop ln_sea_ma, absorb(isocode y) vce(robust)
    local nn = e(N)
    forvalues k = 1/5 {
        local bb = _b[`k'.q_`m'#c.feyrer_int]
        local sse = _se[`k'.q_`m'#c.feyrer_int]
        di "RFQ `m' Q`k': b = " %9.4f `bb' "  se = " %9.4f `sse'
        post `Q' ("`m'") (`k') (`bb') (`sse') (`nn')
    }
}
postclose `Q'
preserve
use "_fey_rf_tmp", clear
export delimited "_feyrer_rf_quintile.csv", replace
restore
erase "_fey_rf_tmp.dta"

di _n "DONE_FEYRER_FULL"
