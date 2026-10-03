*==============================================================================
* co2_spill_cluster_ar.do   (2026-09-03) Which spillover IV combinations survive
* country clustering?
*   A  single-endogenous: neighbour GACI instrumented by the neighbour shifter,
*      own shifter in reduced form, for contig / knn5 / b1 / k500 / inv,
*      cluster(isocode) and cluster(srid); with and without sub-region x year FE
*   B  joint (own + neighbour endogenous), contig / knn5 / b1: cluster(isocode)
*      with clustered SW conditional F (ivreg2 ffirst) and Anderson-Rubin
*      confidence set for the neighbour coefficient by grid inversion
*      (subset AR: own treated with its instrument in the restricted regression)
*   C  single-endogenous contig: Anderson-Rubin CI by grid, cluster(isocode)
* Export: _spill_cluster_ar.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker
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
encode subregion, gen(srid)
egen sry = group(srid y)

tempname R
postfile `R' str10 panel str32 item str16 var double(b se p kpf swf_own swf_nbr ar_lo ar_hi) long(nn) using "_spar_tmp", replace
global RH `R'
program define postone
    args panel item v kpf swo swn lo hi
    local bb = _b[`v']
    local sse = _se[`v']
    local pp = 2*normal(-abs(`bb'/`sse'))
    di "CLU [`panel'] `item' `v': b = " %8.3f `bb' " (se " %7.3f `sse' ")  KP F = " %7.1f `kpf' "  SWF own/nbr = " %6.1f `swo' " / " %6.1f `swn' "  AR = [" %6.2f `lo' ", " %6.2f `hi' "]  N = " %6.0f e(N)
    post $RH ("`panel'") ("`item'") ("`v'") (`bb') (`sse') (`pp') (`kpf') (`swo') (`swn') (`lo') (`hi') (e(N))
end

* =====================================================================
* A) single-endogenous under clustering
* =====================================================================
di _n "===== A) single-endogenous, clustered ====="
foreach W in contig knn5 b1 k500 inv {
    local hc ""
    if inlist("`W'", "contig", "b1") local hc "has_`W'"
    foreach cl in isocode srid {
        capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma `hc' (nbr_g_`W' = nbr_f_`W'), absorb(isocode y) cluster(`cl')
        if _rc == 0 postone A single_`W'_`cl' nbr_g_`W' e(widstat) . . . .
        capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma `hc' (nbr_g_`W' = nbr_f_`W'), absorb(isocode sry) cluster(`cl')
        if _rc == 0 postone A single_`W'_`cl'_rxy nbr_g_`W' e(widstat) . . . .
    }
}

* =====================================================================
* B) joint, clustered, with clustered SW F and subset AR grid for the neighbour term
* =====================================================================
di _n "===== B) joint, clustered ====="
foreach W in contig knn5 b1 {
    local hc ""
    if inlist("`W'", "contig", "b1") local hc "has_`W'"
    capture noisily ivreghdfe ln_co2_tot lnpop ln_sea_ma `hc' (ln_gaci_cwm nbr_g_`W' = feyrer_int nbr_f_`W'), absorb(isocode y) cluster(isocode) ffirst
    if _rc == 0 {
        local kp = e(widstat)
        local bn = _b[nbr_g_`W']
        local swo = .
        local swn = .
        capture matrix FS = e(first)
        if _rc == 0 {
            local rn : rownames FS
            local k = 1
            foreach r of local rn {
                if "`r'" == "SWF" {
                    local swo = FS[`k', 1]
                    local swn = FS[`k', 2]
                }
                local k = `k' + 1
            }
        }
        * subset AR for the neighbour coefficient: for each b0, y - b0*nbr_g is regressed
        * with own still instrumented; test that the excluded neighbour instrument is zero
        local lo = .
        local hi = .
        local prev = 0
        forvalues b0 = -4(0.1)12 {
            quietly gen yb = ln_co2_tot - `b0'*nbr_g_`W'
            capture quietly ivreghdfe yb lnpop ln_sea_ma `hc' nbr_f_`W' (ln_gaci_cwm = feyrer_int), absorb(isocode y) cluster(isocode)
            if _rc == 0 {
                quietly test nbr_f_`W'
                local acc = r(p) > 0.05
                if `acc' & `prev' == 0 local lo = `b0'
                if `acc' local hi = `b0'
                local prev = `acc'
            }
            drop yb
        }
        di "AR grid for `W': accepted b0 from " `lo' " to " `hi'
        quietly ivreghdfe ln_co2_tot lnpop ln_sea_ma `hc' (ln_gaci_cwm nbr_g_`W' = feyrer_int nbr_f_`W'), absorb(isocode y) cluster(isocode)
        postone B joint_`W'_isocode ln_gaci_cwm `kp' `swo' `swn' . .
        postone B joint_`W'_isocode nbr_g_`W' `kp' `swo' `swn' `lo' `hi'
    }
}

* =====================================================================
* C) single-endogenous contig and knn5: AR CI by grid, cluster(isocode)
* =====================================================================
di _n "===== C) single-endogenous AR ====="
foreach W in contig knn5 b1 {
    local hc ""
    if inlist("`W'", "contig", "b1") local hc "has_`W'"
    local lo = .
    local hi = .
    local prev = 0
    forvalues b0 = -4(0.1)12 {
        quietly gen yb = ln_co2_tot - `b0'*nbr_g_`W'
        quietly reghdfe yb nbr_f_`W' feyrer_int lnpop ln_sea_ma `hc', absorb(isocode y) vce(cluster isocode)
        quietly test nbr_f_`W'
        local acc = r(p) > 0.05
        if `acc' & `prev' == 0 local lo = `b0'
        if `acc' local hi = `b0'
        local prev = `acc'
        drop yb
    }
    quietly ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma `hc' (nbr_g_`W' = nbr_f_`W'), absorb(isocode y) cluster(isocode)
    postone C single_`W'_AR nbr_g_`W' e(widstat) . . `lo' `hi'
}

postclose `R'
preserve
use "_spar_tmp", clear
list, clean noobs
export delimited "_spill_cluster_ar.csv", replace
restore
erase "_spar_tmp.dta"
di _n "DONE_SPILL_CLUSTER_AR"
