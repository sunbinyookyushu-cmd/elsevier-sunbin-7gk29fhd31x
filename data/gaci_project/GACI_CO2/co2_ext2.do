*==============================================================================
* co2_ext2.do
* Fix-ups after co2_extensions.do:
* B2') Imai et al. (2010) medeff with explicit dummies (factor vars not allowed)
*      -> appends method "Imai_medeff" rows into _mediation_imai.csv
* D')  Spillover hybrid spec: own GACI instrumented (Feyrer), neighbour Feyrer
*      shifter entered directly (reduced-form neighbour effect conditional on
*      own connectivity) -> _spillover_hybrid.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
set seed 20260826
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl dep_seat_km n_dep_flights dep_seat_km_intl
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "spillover_vars.csv", clear varnames(1) encoding("utf-8")
tempfile sp
save `sp'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `sp', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm
gen ln_flights = ln(n_dep_flights) if n_dep_flights > 0
gen intl_share = dep_seat_km_intl/dep_seat_km if dep_seat_km > 0
replace intl_share = 1 if intl_share > 1 & !missing(intl_share)
gen g_vol = merch_intensity + lngdp

* =====================================================================
* B2') medeff with explicit dummy variables
* =====================================================================
quietly tab isocode, gen(cd_)
quietly tab y, gen(yd_)

tempname D
postfile `D' str12 method str16 med double(acme acme_lo acme_hi ade tau prop) using "_imai_tmp", replace
foreach mv in ln_flights ln_skm intl_share {
    capture noisily medeff (regress `mv' ln_gaci_cwm lnpop ln_sea_ma cd_* yd_*) ///
        (regress ln_co2_tot ln_gaci_cwm `mv' lnpop ln_sea_ma cd_* yd_*), ///
        treat(ln_gaci_cwm) mediate(`mv') sims(200)
    if _rc == 0 {
        local d1 = r(delta1)
        local z1 = r(zeta1)
        local tau = r(tau)
        local pr = `d1'/`tau'
        capture local dlo = r(d1lo)
        capture local dhi = r(d1hi)
        if "`dlo'" == "" {
            local dlo = .
        }
        if "`dhi'" == "" {
            local dhi = .
        }
        di "IMAI `mv': ACME=" %8.4f `d1' " [" %8.4f `dlo' "," %8.4f `dhi' "]  ADE=" %8.4f `z1' "  total=" %8.4f `tau' "  prop=" %6.3f `pr'
        post `D' ("Imai_medeff") ("`mv'") (`d1') (`dlo') (`dhi') (`z1') (`tau') (`pr')
    }
    else {
        di "IMAI `mv': FAILED rc=" _rc
    }
}
postclose `D'
preserve
use "_imai_tmp", clear
list, clean
export delimited "_mediation_imai.csv", replace
restore
erase "_imai_tmp.dta"

* =====================================================================
* D') spillover hybrid: own IV + neighbour shifter as exogenous
* =====================================================================
tempname S
postfile `S' str16 outc str12 var double(b se p kpf) long(nn) using "_sph_tmp", replace
foreach yv in ln_co2_tot ln_co2_intl ln_intensity g_vol {
    quietly ivreghdfe `yv' nbr_feyrer lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    foreach v in ln_gaci_cwm nbr_feyrer {
        local bb = _b[`v']
        local ss = _se[`v']
        di "HYB `yv' `v': b=" %8.3f `bb' " se=" %8.3f `ss' " F=" %7.1f e(widstat)
        post `S' ("`yv'") ("`v'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    }
}
postclose `S'
preserve
use "_sph_tmp", clear
list, clean
export delimited "_spillover_hybrid.csv", replace
restore
erase "_sph_tmp.dta"

di _n "DONE_EXT2"
