*==============================================================================
* co2_spill_bands.do   (LZ comment 3, 2026-09-03)
* Formal spillover analysis.
*   A  first-order neighbour effect with own GACI controlled
*      (own exogenous control; hybrid RF control; joint IV under W variants with
*       Sanderson-Windmeijer conditional F)
*   B  distance decay: bands entered jointly and singly; kernel grid; far band alone
*   C  regional: within vs out-of-region (UN sub-region; aviation bloc);
*      region-by-year FE; heterogeneity by receiving region and international share
*   D  mechanisms of the neighbour effect (own-vs-neighbour table), incl. domestic CO2
*   E  standard-error variants (cluster sub-region; two-way)
* Inputs: gaci_panel_combined.csv, co2_country_year.csv, spillover_vars.csv,
*         spillover_bands.csv
* Export: _spill_bands.csv (panel item var b se p kpf swf nn)
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
import delimited "spillover_vars.csv", clear varnames(1) encoding("utf-8")
tempfile sv
save `sv'
import delimited "spillover_bands.csv", clear varnames(1) encoding("utf-8")
ds c subregion unregion bloc, not
destring `r(varlist)', replace force
tempfile sb
save `sb'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
merge 1:1 c y using `sv', keep(1 3) nogenerate
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
encode unregion, gen(urid)
egen sry = group(srid y)
* baseline international share tercile (earliest observed)
bysort isocode (y): gen byte first_i = sum(!missing(intl_share)) == 1 & !missing(intl_share)
gen i0_ = intl_share if first_i
bysort isocode (i0_): gen intl0 = i0_[1]
drop i0_ first_i
preserve
bysort isocode: keep if _n == 1
xtile int3 = intl0, nq(3)
keep isocode int3
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

tempname R
postfile `R' str10 panel str32 item str16 var double(b se p kpf swf) long(nn) using "_spill_tmp", replace
global RH `R'

program define postone
    * post coefficient on `v' from the last estimation, with optional swf
    args panel item v kpf swf
    local bb = _b[`v']
    local sse = _se[`v']
    local pp = 2*normal(-abs(`bb'/`sse'))
    di "SPL [`panel'] `item' `v': b = " %9.3f `bb' " (se " %8.3f `sse' ")  KP F = " %7.1f `kpf' "  SWF = " %7.1f `swf' "  N = " %7.0f e(N)
    post $RH ("`panel'") ("`item'") ("`v'") (`bb') (`sse') (`pp') (`kpf') (`swf') (e(N))
end

* =====================================================================
* A) first-order effect with own GACI controlled
* =====================================================================
di _n "===== A) own-controlled ====="
* A1 own as exogenous control (reference column)
ivreghdfe ln_co2_tot ln_gaci_cwm lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv), absorb(isocode y) robust
postone A own_exog_control nbr_g_inv e(widstat) .
postone A own_exog_control ln_gaci_cwm e(widstat) .
* A2 hybrid: own shifter in reduced form (current manuscript specification)
ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv), absorb(isocode y) robust
postone A hybrid_rf_control nbr_g_inv e(widstat) .
postone A hybrid_rf_control feyrer_int e(widstat) .
* A3.. joint IV under alternative W (with SW conditional F)
foreach W in inv contig knn5 b1 k500 k1000 {
    capture noisily ivreghdfe ln_co2_tot lnpop ln_sea_ma has_contig (ln_gaci_cwm nbr_g_`W' = feyrer_int nbr_f_`W'), absorb(isocode y) robust ffirst
    if _rc == 0 {
        local sw_own = .
        local sw_nbr = .
        capture matrix FS = e(first)
        if _rc == 0 {
            local rn : rownames FS
            local cn : colnames FS
            local ri = 0
            local k = 1
            foreach r of local rn {
                if "`r'" == "SWF" local ri = `k'
                local k = `k' + 1
            }
            if `ri' > 0 {
                local sw_own = FS[`ri', 1]
                local sw_nbr = FS[`ri', 2]
            }
        }
        postone A joint_`W' ln_gaci_cwm e(widstat) `sw_own'
        postone A joint_`W' nbr_g_`W' e(widstat) `sw_nbr'
    }
    else di as err "JOINT IV FAILED for W = `W'"
}
* A4 single-endogenous neighbour effect under each W, hybrid control (for comparability)
foreach W in inv contig knn5 b1 k500 k1000 {
    capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_contig (nbr_g_`W' = nbr_f_`W'), absorb(isocode y) robust
    if _rc == 0 postone A single_`W' nbr_g_`W' e(widstat) .
}

* =====================================================================
* B) distance decay
* =====================================================================
di _n "===== B) distance bands ====="
* bands jointly (own shifter RF-controlled; band-presence flags as controls)
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_b1 has_b2 has_b3 has_b4 has_b5 (nbr_g_b1 nbr_g_b2 nbr_g_b3 nbr_g_b4 nbr_g_b5 = nbr_f_b1 nbr_f_b2 nbr_f_b3 nbr_f_b4 nbr_f_b5), absorb(isocode y) robust
if _rc == 0 {
    foreach b in b1 b2 b3 b4 b5 {
        postone B bands_joint nbr_g_`b' e(widstat) .
    }
}
* contiguity plus bands
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_contig has_b1 has_b2 has_b3 has_b4 has_b5 (nbr_g_contig nbr_g_b1 nbr_g_b2 nbr_g_b3 nbr_g_b4 nbr_g_b5 = nbr_f_contig nbr_f_b1 nbr_f_b2 nbr_f_b3 nbr_f_b4 nbr_f_b5), absorb(isocode y) robust
if _rc == 0 {
    foreach b in contig b1 b2 b3 b4 b5 {
        postone B bands_joint_contig nbr_g_`b' e(widstat) .
    }
}
* each band alone
foreach b in contig b1 b2 b3 b4 b5 {
    capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_`b' (nbr_g_`b' = nbr_f_`b'), absorb(isocode y) robust
    if _rc == 0 postone B band_single nbr_g_`b' e(widstat) .
}
* kernel grid
foreach lam in 250 500 1000 2000 5000 {
    capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_k`lam' = nbr_f_k`lam'), absorb(isocode y) robust
    if _rc == 0 {
        postone B kernel nbr_g_k`lam' e(widstat) .
        di "KERNEL lambda=`lam': rmse = " %8.4f e(rmse)
        post $RH ("B") ("kernel_rmse") ("k`lam'") (e(rmse)) (.) (.) (e(widstat)) (.) (e(N))
    }
}

* =====================================================================
* C) regional spillovers
* =====================================================================
di _n "===== C) regional ====="
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_inreg (nbr_g_inreg nbr_g_outreg = nbr_f_inreg nbr_f_outreg), absorb(isocode y) robust
if _rc == 0 {
    postone C subregion_inout nbr_g_inreg e(widstat) .
    postone C subregion_inout nbr_g_outreg e(widstat) .
}
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_inbloc (nbr_g_inbloc nbr_g_outbloc = nbr_f_inbloc nbr_f_outbloc), absorb(isocode y) robust
if _rc == 0 {
    postone C bloc_inout nbr_g_inbloc e(widstat) .
    postone C bloc_inout nbr_g_outbloc e(widstat) .
}
* region-by-year fixed effects (UN sub-region x year)
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv), absorb(isocode sry) robust
if _rc == 0 postone C regionXyear_inv nbr_g_inv e(widstat) .
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_contig (nbr_g_contig = nbr_f_contig), absorb(isocode sry) robust
if _rc == 0 postone C regionXyear_contig nbr_g_contig e(widstat) .
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma has_b1 has_b2 has_b3 has_b4 has_b5 (nbr_g_b1 nbr_g_b2 nbr_g_b3 nbr_g_b4 nbr_g_b5 = nbr_f_b1 nbr_f_b2 nbr_f_b3 nbr_f_b4 nbr_f_b5), absorb(isocode sry) robust
if _rc == 0 {
    foreach b in b1 b2 b3 b4 b5 {
        postone C regionXyear_bands nbr_g_`b' e(widstat) .
    }
}
capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_k500 = nbr_f_k500), absorb(isocode sry) robust
if _rc == 0 postone C regionXyear_k500 nbr_g_k500 e(widstat) .
* heterogeneity by receiving region (UN region) and by baseline international share
levelsof unregion, local(regs)
foreach r of local regs {
    capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv) if unregion == "`r'", absorb(isocode y) robust
    if _rc == 0 postone C het_`r' nbr_g_inv e(widstat) .
}
foreach g in 1 2 3 {
    capture noisily ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv) if int3 == `g', absorb(isocode y) robust
    if _rc == 0 postone C het_intl`g' nbr_g_inv e(widstat) .
}

* =====================================================================
* D) mechanisms of the neighbour effect (own vs neighbour table)
* =====================================================================
di _n "===== D) neighbour mechanisms ====="
foreach yv in ln_co2_tot ln_co2_intl ln_co2_dom ln_skm ln_flights ln_gauge ln_stage ln_intensity intl_share {
    capture noisily ivreghdfe `yv' feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv), absorb(isocode y) robust
    if _rc == 0 postone D mech_`yv' nbr_g_inv e(widstat) .
}

* =====================================================================
* E) standard errors
* =====================================================================
di _n "===== E) SE variants ====="
ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv), absorb(isocode y) cluster(isocode)
postone E cluster_country nbr_g_inv e(widstat) .
ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv), absorb(isocode y) cluster(srid)
postone E cluster_subregion nbr_g_inv e(widstat) .
ivreghdfe ln_co2_tot feyrer_int lnpop ln_sea_ma (nbr_g_inv = nbr_f_inv), absorb(isocode y) cluster(isocode y)
postone E cluster_twoway nbr_g_inv e(widstat) .

postclose `R'
preserve
use "_spill_tmp", clear
list, clean noobs
export delimited "_spill_bands.csv", replace
restore
erase "_spill_tmp.dta"

di _n "DONE_SPILL_BANDS"
