*==============================================================================
* co2_extensions.do
* A) Measures x 6 outcomes under Feyrer IV: sum (lng) / max / mean
*    -> _measures6.csv   (panels C/D/E of the main sheet)
* B) Mediation, two flavours:
*    B1: IV product-of-coefficients + Sobel (treatment instrumented)
*    B2: Imai et al. (2010) causal mediation via medeff (quasi-Bayesian ACME),
*        OLS with country + year dummies
*    mediators: ln_flights, ln_skm, intl_share; outcome ln_co2_tot
*    -> _mediation_co2.csv
* C) Temporal heterogeneity: pre-2010 vs 2010+ (Feyrer IV)
*    -> _temporal_co2.csv
* D) Spatial spillovers: neighbour connectivity (inverse-distance weighted),
*    own + neighbour GACI both instrumented (own Feyrer + neighbour Feyrer)
*    -> _spillover_co2.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
set seed 20260826
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

* ---- build merged dataset ----
import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl co2_lto co2_5050 dep_seat_km n_dep_flights dep_seats dep_seat_km_intl
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "../gaci_panel_measures.csv", clear varnames(1) encoding("utf-8")
keep c y ln_gaci_max
tempfile mx
save `mx'

import delimited "spillover_vars.csv", clear varnames(1) encoding("utf-8")
tempfile sp
save `sp'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `mx', keep(1 3) nogenerate
merge 1:1 c y using `sp', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_co2_lto = ln(co2_lto) if co2_lto > 0
gen ln_co2_5050 = ln(co2_5050) if co2_5050 > 0
gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm
gen ln_flights = ln(n_dep_flights) if n_dep_flights > 0
gen intl_share = dep_seat_km_intl/dep_seat_km if dep_seat_km > 0
replace intl_share = 1 if intl_share > 1 & !missing(intl_share)
gen g_vol = merch_intensity + lngdp

* =====================================================================
* A) measures x 6 outcomes
* =====================================================================
tempname M
postfile `M' str16 meas str16 outc double(b se p kpf) long(nn) using "_m6_tmp", replace
foreach tr in lng ln_gaci_max ln_gaci_mean {
    foreach yv in ln_co2_tot ln_co2_lto ln_co2_5050 ln_co2_intl ln_skm ln_intensity {
        quietly ivreghdfe `yv' lnpop ln_sea_ma (`tr' = feyrer_int), absorb(isocode y) robust
        local bb = _b[`tr']
        local ss = _se[`tr']
        di "M6 `tr' `yv': b = " %9.3f `bb' "  KP F = " %7.1f e(widstat)
        post `M' ("`tr'") ("`yv'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    }
}
postclose `M'
preserve
use "_m6_tmp", clear
export delimited "_measures6.csv", replace
restore
erase "_m6_tmp.dta"

* =====================================================================
* B) mediation
* =====================================================================
tempname D
postfile `D' str12 method str16 med double(a sa b sb cprime scp ctot acme sobel_se sobel_p prop) using "_med_tmp", replace

* --- B1: IV product of coefficients ---
foreach mv in ln_flights ln_skm intl_share {
    quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    local ctot = _b[ln_gaci_cwm]
    quietly ivreghdfe `mv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    local aa = _b[ln_gaci_cwm]
    local sa = _se[ln_gaci_cwm]
    quietly ivreghdfe ln_co2_tot `mv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    local bb = _b[`mv']
    local sb = _se[`mv']
    local cp = _b[ln_gaci_cwm]
    local scp = _se[ln_gaci_cwm]
    local acme = `aa'*`bb'
    local sse = sqrt(`aa'^2*`sb'^2 + `bb'^2*`sa'^2)
    local sz = `acme'/`sse'
    local sp2 = 2*normal(-abs(`sz'))
    local pr = `acme'/`ctot'
    di "MED-IV `mv': a=" %7.3f `aa' " b=" %7.3f `bb' " ACME=" %7.3f `acme' " Sobel p=" %6.4f `sp2' " prop=" %6.3f `pr'
    post `D' ("IV_product") ("`mv'") (`aa') (`sa') (`bb') (`sb') (`cp') (`scp') (`ctot') (`acme') (`sse') (`sp2') (`pr')
}

* --- B2: Imai et al. (2010) medeff, OLS with country+year dummies ---
foreach mv in ln_flights ln_skm intl_share {
    capture noisily medeff (regress `mv' ln_gaci_cwm lnpop ln_sea_ma i.isocode i.y) ///
        (regress ln_co2_tot ln_gaci_cwm `mv' lnpop ln_sea_ma i.isocode i.y), ///
        treat(ln_gaci_cwm) mediate(`mv') sims(200)
    if _rc == 0 {
        local d1 = r(delta1)
        local z1 = r(zeta1)
        local tau = r(tau)
        local pr = `d1'/`tau'
        di "MED-IMAI `mv': ACME=" %7.3f `d1' " ADE=" %7.3f `z1' " total=" %7.3f `tau' " prop=" %6.3f `pr'
        post `D' ("Imai_medeff") ("`mv'") (.) (.) (.) (.) (`z1') (.) (`tau') (`d1') (.) (.) (`pr')
    }
}
postclose `D'
preserve
use "_med_tmp", clear
list, clean
export delimited "_mediation_co2.csv", replace
restore
erase "_med_tmp.dta"

* =====================================================================
* C) temporal heterogeneity
* =====================================================================
tempname T
postfile `T' str12 period str16 outc double(b se p kpf) long(nn) using "_tmp_tmp", replace
foreach yv in ln_co2_tot ln_co2_intl ln_skm ln_intensity {
    quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    local bb = _b[ln_gaci_cwm]
    local ss = _se[ln_gaci_cwm]
    post `T' ("full") ("`yv'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y < 2010, absorb(isocode y) robust
    local bb = _b[ln_gaci_cwm]
    local ss = _se[ln_gaci_cwm]
    di "TEMP pre `yv': b=" %8.3f `bb' " F=" %7.1f e(widstat)
    post `T' ("1996-2009") ("`yv'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if y >= 2010, absorb(isocode y) robust
    local bb = _b[ln_gaci_cwm]
    local ss = _se[ln_gaci_cwm]
    di "TEMP post `yv': b=" %8.3f `bb' " F=" %7.1f e(widstat)
    post `T' ("2010-2023") ("`yv'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
}
postclose `T'
preserve
use "_tmp_tmp", clear
export delimited "_temporal_co2.csv", replace
restore
erase "_tmp_tmp.dta"

* =====================================================================
* D) spatial spillovers
* =====================================================================
tempname S
postfile `S' str8 stage str16 outc str12 var double(b se p kpf) long(nn) using "_sp_tmp", replace
foreach yv in ln_co2_tot ln_co2_intl ln_intensity g_vol {
    * reduced form
    quietly reghdfe `yv' feyrer_int nbr_feyrer lnpop ln_sea_ma, absorb(isocode y) vce(robust)
    foreach v in feyrer_int nbr_feyrer {
        local bb = _b[`v']
        local ss = _se[`v']
        post `S' ("RF") ("`yv'") ("`v'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (.) (e(N))
    }
    * 2SLS, own + neighbour connectivity both endogenous
    capture noisily quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm nbr_lngaci = feyrer_int nbr_feyrer), absorb(isocode y) robust
    if _rc == 0 {
        foreach v in ln_gaci_cwm nbr_lngaci {
            local bb = _b[`v']
            local ss = _se[`v']
            di "SPILL IV `yv' `v': b=" %8.3f `bb' " se=" %8.3f `ss' " F=" %7.1f e(widstat)
            post `S' ("IV") ("`yv'") ("`v'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
        }
    }
}
postclose `S'
preserve
use "_sp_tmp", clear
list, clean
export delimited "_spillover_co2.csv", replace
restore
erase "_sp_tmp.dta"

di _n "DONE_EXTENSIONS"
