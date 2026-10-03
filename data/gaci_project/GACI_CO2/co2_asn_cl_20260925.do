*==============================================================================
* co2_asn_cl_20260925.do
* Accident-IV pilot (Supplementary Table tab:accident_iv) re-estimated with
* standard errors CLUSTERED BY COUNTRY. The original co2_measures_asn.do used
* robust (heteroskedasticity-only) errors although the table note says
* clustered. After the tourism-heritage IV is dropped (Junya comment, 9/25),
* this is the only overidentification test, so it must match the paper's
* inference (country clustering throughout, 09-03 decision).
* Output: _asn_iv_results_cl.csv  (same layout as _asn_iv_results.csv)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"
log using "co2_asn_cl_20260925_run.log", replace text

* ---- build merged dataset (same as co2_measures_asn.do) ----
import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl co2_lto co2_5050 dep_seat_km
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "asn_country_year.csv", clear varnames(1) encoding("utf-8")
tempfile asn
save `asn'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `asn', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm

gen ash_deaths = asinh(deaths)
gen ash_com_deaths = asinh(com_deaths)
gen byte d_major = n_major > 0
gen byte d_fatal = n_fatal > 0

tempname R
postfile `R' str12 stage str16 z str16 outc double(b se p kpf jp) long(nn) using "_asn_tmp_cl", replace

* ---- B1: first stage, lagged accident measures (cluster-robust partial F) ----
foreach z in ash_deaths ash_com_deaths n_fatal n_major d_major d_fatal {
    quietly reghdfe ln_gaci_cwm L.`z' lnpop ln_sea_ma, absorb(isocode y) vce(cluster isocode)
    local bb = _b[L.`z']
    local ss = _se[L.`z']
    local pp = 2*normal(-abs(`bb'/`ss'))
    quietly test L.`z'
    local ff = r(F)
    di "FS L.`z': b = " %9.4f `bb' " (se " %8.4f `ss' ")  partial F = " %7.1f `ff' "  N = " %8.0f e(N)
    post `R' ("FS_lag") ("L.`z'") ("ln_gaci_cwm") (`bb') (`ss') (`pp') (`ff') (.) (e(N))
}

* ---- B2: 2SLS, lagged accident IV alone ----
foreach z in ash_deaths n_fatal d_fatal {
    foreach yv in ln_co2_tot ln_co2_intl ln_intensity {
        capture noisily quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = L.`z'), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            local bb = _b[ln_gaci_cwm]
            local ss = _se[ln_gaci_cwm]
            local pp = 2*normal(-abs(`bb'/`ss'))
            di "IV L.`z' -> `yv': b = " %9.3f `bb' " (se " %8.3f `ss' ")  KP F = " %7.1f e(widstat) "  N = " %8.0f e(N)
            post `R' ("IV_asn") ("L.`z'") ("`yv'") (`bb') (`ss') (`pp') (e(widstat)) (.) (e(N))
        }
    }
}

* ---- B3: over-ID, Feyrer + lagged accident IV jointly (cluster-robust Hansen J) ----
foreach z in ash_deaths n_fatal {
    foreach yv in ln_co2_tot ln_co2_intl ln_intensity {
        capture noisily quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int L.`z'), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            local bb = _b[ln_gaci_cwm]
            local ss = _se[ln_gaci_cwm]
            local pp = 2*normal(-abs(`bb'/`ss'))
            local jp = e(jp)
            di "OVERID feyrer+L.`z' -> `yv': b = " %9.3f `bb' " (se " %8.3f `ss' ")  KP F = " %7.1f e(widstat) "  Hansen J p = " %6.3f `jp' "  N = " %8.0f e(N)
            post `R' ("OVERID") ("fey+L.`z'") ("`yv'") (`bb') (`ss') (`pp') (e(widstat)) (`jp') (e(N))
        }
    }
}

postclose `R'
use "_asn_tmp_cl", clear
list, clean
export delimited "_asn_iv_results_cl.csv", replace
erase "_asn_tmp_cl.dta"

di _n "DONE_ASN_CL"
log close
