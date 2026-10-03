*==============================================================================
* co2_spill_supp.do   (2026-09-03) clustered inference for the spillover specs
* that are the candidates for the headline (joint IV under contiguity / knn5 /
* <500 km / k1000 W; region-by-year FE variants), plus neighbour mechanisms
* under the contiguity W. Cluster: country; UN sub-region; two-way country+year.
* Export: _spill_supp.csv (panel item var b se p kpf nn)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl dep_seat_km n_dep_flights dep_seats dep_seat_km_intl
rename iso3 c
rename year y
tempfile co2
save `co2'
import delimited "spillover_bands.csv", clear varnames(1) encoding("utf-8")
ds c subregion unregion bloc, not
destring `r(varlist)', replace force
tempfile sb
save `sb'
import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `sb', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_co2_intl = ln(co2_bunker_intl) if co2_bunker_intl > 0
gen co2_dom = co2_bunker - co2_bunker_intl
gen ln_co2_dom = ln(co2_dom) if co2_dom > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm
gen ln_flights = ln(n_dep_flights) if n_dep_flights > 0
gen ln_gauge = ln(dep_seats/n_dep_flights) if n_dep_flights > 0 & dep_seats > 0
gen ln_stage = ln(dep_seat_km/dep_seats) if dep_seats > 0 & dep_seat_km > 0
gen intl_share = dep_seat_km_intl/dep_seat_km if dep_seat_km > 0
replace intl_share = 1 if intl_share > 1 & !missing(intl_share)
encode subregion, gen(srid)
egen sry = group(srid y)

tempname R
postfile `R' str12 panel str32 item str16 var double(b se p kpf) long(nn) using "_spsupp_tmp", replace
global RH `R'
program define postone
    args panel item v
    local bb = _b[`v']
    local sse = _se[`v']
    local pp = 2*normal(-abs(`bb'/`sse'))
    di "SUP [`panel'] `item' `v': b = " %9.3f `bb' " (se " %8.3f `sse' ")  KP F = " %7.1f e(widstat) "  N = " %7.0f e(N)
    post $RH ("`panel'") ("`item'") ("`v'") (`bb') (`sse') (`pp') (e(widstat)) (e(N))
end

* joint IV specs under three clusterings
foreach W in contig knn5 b1 k1000 {
    foreach cl in robust country subregion twoway {
        if "`cl'" == "robust" local vo "robust"
        if "`cl'" == "country" local vo "cluster(isocode)"
        if "`cl'" == "subregion" local vo "cluster(srid)"
        if "`cl'" == "twoway" local vo "cluster(isocode y)"
        capture noisily ivreghdfe ln_co2_tot lnpop ln_sea_ma has_contig (ln_gaci_cwm nbr_g_`W' = feyrer_int nbr_f_`W'), absorb(isocode y) `vo'
        if _rc == 0 {
            postone JOINT `W'_`cl' ln_gaci_cwm
            postone JOINT `W'_`cl' nbr_g_`W'
        }
    }
}
* region-by-year FE, contiguity, clustered
foreach cl in robust country subregion {
    if "`cl'" == "robust" local vo "robust"
    if "`cl'" == "country" local vo "cluster(isocode)"
    if "`cl'" == "subregion" local vo "cluster(srid)"
    capture noisily ivreghdfe ln_co2_tot lnpop ln_sea_ma has_contig (ln_gaci_cwm nbr_g_contig = feyrer_int nbr_f_contig), absorb(isocode sry) `vo'
    if _rc == 0 {
        postone RXY contig_`cl' ln_gaci_cwm
        postone RXY contig_`cl' nbr_g_contig
    }
}
* neighbour mechanisms under contiguity W (joint IV, own controlled), robust and country-clustered
foreach yv in ln_co2_tot ln_co2_intl ln_co2_dom ln_skm ln_flights ln_gauge ln_stage ln_intensity intl_share {
    capture noisily ivreghdfe `yv' lnpop ln_sea_ma has_contig (ln_gaci_cwm nbr_g_contig = feyrer_int nbr_f_contig), absorb(isocode y) robust
    if _rc == 0 {
        postone MECH `yv'_robust ln_gaci_cwm
        postone MECH `yv'_robust nbr_g_contig
    }
    capture noisily ivreghdfe `yv' lnpop ln_sea_ma has_contig (ln_gaci_cwm nbr_g_contig = feyrer_int nbr_f_contig), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        postone MECH `yv'_country ln_gaci_cwm
        postone MECH `yv'_country nbr_g_contig
    }
}
* first stages of the contiguity joint spec (for the text)
reghdfe ln_gaci_cwm feyrer_int nbr_f_contig lnpop ln_sea_ma has_contig, absorb(isocode y) vce(cluster isocode)
di "FS own: feyrer_int = " %8.4f _b[feyrer_int] " (se " %7.4f _se[feyrer_int] ")  nbr_f_contig = " %8.4f _b[nbr_f_contig] " (se " %7.4f _se[nbr_f_contig] ")"
post $RH ("FS") ("own_eq") ("feyrer_int") (_b[feyrer_int]) (_se[feyrer_int]) (2*normal(-abs(_b[feyrer_int]/_se[feyrer_int]))) (.) (e(N))
post $RH ("FS") ("own_eq") ("nbr_f_contig") (_b[nbr_f_contig]) (_se[nbr_f_contig]) (2*normal(-abs(_b[nbr_f_contig]/_se[nbr_f_contig]))) (.) (e(N))
reghdfe nbr_g_contig feyrer_int nbr_f_contig lnpop ln_sea_ma has_contig, absorb(isocode y) vce(cluster isocode)
di "FS nbr: feyrer_int = " %8.4f _b[feyrer_int] " (se " %7.4f _se[feyrer_int] ")  nbr_f_contig = " %8.4f _b[nbr_f_contig] " (se " %7.4f _se[nbr_f_contig] ")"
post $RH ("FS") ("nbr_eq") ("feyrer_int") (_b[feyrer_int]) (_se[feyrer_int]) (2*normal(-abs(_b[feyrer_int]/_se[feyrer_int]))) (.) (e(N))
post $RH ("FS") ("nbr_eq") ("nbr_f_contig") (_b[nbr_f_contig]) (_se[nbr_f_contig]) (2*normal(-abs(_b[nbr_f_contig]/_se[nbr_f_contig]))) (.) (e(N))
* sample facts
quietly count if has_contig == 0 & y == 2023
di "countries without a land neighbour in 2023: " r(N)

postclose `R'
preserve
use "_spsupp_tmp", clear
list, clean noobs
export delimited "_spill_supp.csv", replace
restore
erase "_spsupp_tmp.dta"
di _n "DONE_SPILL_SUPP"
