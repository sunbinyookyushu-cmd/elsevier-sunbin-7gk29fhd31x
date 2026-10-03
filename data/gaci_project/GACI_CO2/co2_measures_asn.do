*==============================================================================
* co2_measures_asn.do
* A) H2 measure robustness under Feyrer IV: cwm / sum (lng) / max, across the
*    four key outcomes (total CO2, intl CO2, seat-km, intensity)
*    -> _feyrer_measures.csv
* B) ASN accident-IV pilot: country-year accident shocks as instrument for
*    ln_gaci_cwm. First stage, 2SLS, and over-ID jointly with feyrer_int.
*    -> _asn_iv_results.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

* ---- build merged dataset (same as co2_feyrer_full.do) ----
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

import delimited "asn_country_year.csv", clear varnames(1) encoding("utf-8")
tempfile asn
save `asn'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `mx', keep(1 3) nogenerate
merge 1:1 c y using `asn', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm

* =====================================================================
* A) measures: cwm / sum / max x 4 outcomes
* =====================================================================
tempname M
postfile `M' str16 meas str16 outc double(b se p kpf) long(nn) using "_meas_tmp", replace
foreach tr in ln_gaci_cwm lng ln_gaci_max {
    foreach yv in ln_co2_tot ln_co2_intl ln_skm ln_intensity {
        quietly ivreghdfe `yv' lnpop ln_sea_ma (`tr' = feyrer_int), absorb(isocode y) robust
        local bb = _b[`tr']
        local ss = _se[`tr']
        local pp = 2*normal(-abs(`bb'/`ss'))
        di "MEAS `tr' `yv': b = " %9.3f `bb' " (se " %8.3f `ss' ")  KP F = " %7.1f e(widstat) "  N = " %8.0f e(N)
        post `M' ("`tr'") ("`yv'") (`bb') (`ss') (`pp') (e(widstat)) (e(N))
    }
}
postclose `M'
preserve
use "_meas_tmp", clear
export delimited "_feyrer_measures.csv", replace
restore
erase "_meas_tmp.dta"

* =====================================================================
* B) ASN accident IV
* =====================================================================
gen ash_deaths = asinh(deaths)
gen ash_com_deaths = asinh(com_deaths)
gen byte d_major = n_major > 0
gen byte d_fatal = n_fatal > 0

tempname R
postfile `R' str12 stage str16 z str16 outc double(b se p kpf jp) long(nn) using "_asn_tmp", replace

* ---- B1: first stage, lagged accident measures ----
foreach z in ash_deaths ash_com_deaths n_fatal n_major d_major d_fatal {
    quietly reghdfe ln_gaci_cwm L.`z' lnpop ln_sea_ma, absorb(isocode y) vce(robust)
    local bb = _b[L.`z']
    local ss = _se[L.`z']
    local pp = 2*normal(-abs(`bb'/`ss'))
    quietly test L.`z'
    local ff = r(F)
    di "FS L.`z': b = " %9.4f `bb' " (se " %8.4f `ss' ")  partial F = " %7.1f `ff' "  N = " %8.0f e(N)
    post `R' ("FS_lag") ("L.`z'") ("ln_gaci_cwm") (`bb') (`ss') (`pp') (`ff') (.) (e(N))
}
* contemporaneous, for comparison (endogeneity check: sign should differ)
foreach z in ash_deaths n_fatal {
    quietly reghdfe ln_gaci_cwm `z' lnpop ln_sea_ma, absorb(isocode y) vce(robust)
    local bb = _b[`z']
    local ss = _se[`z']
    local pp = 2*normal(-abs(`bb'/`ss'))
    quietly test `z'
    local ff = r(F)
    di "FS contemp `z': b = " %9.4f `bb' " (se " %8.4f `ss' ")  partial F = " %7.1f `ff'
    post `R' ("FS_contemp") ("`z'") ("ln_gaci_cwm") (`bb') (`ss') (`pp') (`ff') (.) (e(N))
}

* ---- B2: 2SLS with the strongest lagged accident IV(s), just-identified ----
foreach z in ash_deaths n_fatal d_fatal {
    foreach yv in ln_co2_tot ln_co2_intl ln_intensity {
        capture noisily quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = L.`z'), absorb(isocode y) robust
        if _rc == 0 {
            local bb = _b[ln_gaci_cwm]
            local ss = _se[ln_gaci_cwm]
            local pp = 2*normal(-abs(`bb'/`ss'))
            di "IV L.`z' -> `yv': b = " %9.3f `bb' " (se " %8.3f `ss' ")  KP F = " %7.1f e(widstat)
            post `R' ("IV_asn") ("L.`z'") ("`yv'") (`bb') (`ss') (`pp') (e(widstat)) (.) (e(N))
        }
    }
}

* ---- B3: over-ID, feyrer_int + lagged accident IV jointly (Hansen J) ----
foreach z in ash_deaths n_fatal {
    foreach yv in ln_co2_tot ln_co2_intl ln_intensity {
        capture noisily quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int L.`z'), absorb(isocode y) robust
        if _rc == 0 {
            local bb = _b[ln_gaci_cwm]
            local ss = _se[ln_gaci_cwm]
            local pp = 2*normal(-abs(`bb'/`ss'))
            local jp = e(jp)
            di "OVERID feyrer+L.`z' -> `yv': b = " %9.3f `bb' "  KP F = " %7.1f e(widstat) "  Hansen J p = " %6.3f `jp'
            post `R' ("OVERID") ("fey+L.`z'") ("`yv'") (`bb') (`ss') (`pp') (e(widstat)) (`jp') (e(N))
        }
    }
}

postclose `R'
preserve
use "_asn_tmp", clear
list, clean
export delimited "_asn_iv_results.csv", replace
restore
erase "_asn_tmp.dta"

di _n "DONE_MEASURES_ASN"
