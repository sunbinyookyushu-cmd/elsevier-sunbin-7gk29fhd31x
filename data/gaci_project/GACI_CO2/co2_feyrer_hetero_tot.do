*==============================================================================
* co2_feyrer_hetero_tot.do (2026-09-03: outcome = TOTAL CO2, corrects intl-outcome mislabel)
* GROUP HETEROGENEITY of the headline elasticity (Feyrer IV, ln_sea_ma
* controlled), split-sample 2SLS + pooled interaction tests.
*   A) baseline income terciles (earliest observed lnpc per country)
*   B) baseline connectivity terciles (earliest observed gaci_cwmean)
*   C) macro regions (Europe / Asia-Pacific / Africa / LatAm / MiddleEast / NorthAm)
*   D) intensity outcome (ln CO2 per seat-km) across income terciles
* Spec mirrors co2_feyrer_full.do part A:
*   ivreghdfe y lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
* Exports: _feyrer_hetero_tot.csv (long: panel, group, b, se, p, KPF, N, Ncountries)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

* ---- build merged dataset (identical to co2_feyrer_full.do) ----
import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker co2_bunker_intl co2_lto co2_5050 dep_seat_km
rename iso3 c
rename year y
tempfile co2
save `co2'

import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `co2', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y

gen ln_co2_tot = ln(co2_bunker) if co2_bunker > 0
gen ln_skm = ln(dep_seat_km) if dep_seat_km > 0
gen ln_intensity = ln_co2_tot - ln_skm

* ---- time-invariant grouping variables ----
* baseline income: earliest observed lnpc per country
bysort isocode (y): gen byte first_pc = sum(!missing(lnpc)) == 1 & !missing(lnpc)
gen lnpc0_ = lnpc if first_pc
bysort isocode (lnpc0_): gen lnpc0 = lnpc0_[1]
drop lnpc0_ first_pc

* baseline connectivity: earliest observed gaci_cwmean per country
bysort isocode (y): gen byte first_g = sum(!missing(gaci_cwmean)) == 1 & !missing(gaci_cwmean)
gen g0_ = gaci_cwmean if first_g
bysort isocode (g0_): gen gaci0 = g0_[1]
drop g0_ first_g

* terciles over countries (one obs per country)
preserve
bysort isocode: keep if _n == 1
xtile inc3 = lnpc0, nq(3)
xtile con3 = gaci0, nq(3)
keep isocode inc3 con3
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

* macro regions
gen mreg = ""
replace mreg = "Europe" if inlist(reg, "EU1", "EU2")
replace mreg = "AsiaPacific" if inlist(reg, "AS1", "AS2", "AS3", "AS4", "SW1")
replace mreg = "Africa" if inlist(reg, "AF1", "AF2", "AF3", "AF4")
replace mreg = "LatAm" if inlist(reg, "LA1", "LA2", "LA3", "LA4")
replace mreg = "MiddleEast" if reg == "ME1"
replace mreg = "NorthAm" if reg == "NA1"

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

* ---- results accumulator ----
tempname H
postfile `H' str12 panel str16 grp b se p KPF N Nc using "_feyrer_hetero_tot_post.dta", replace

capture program drop runcell
program define runcell
    args H panel grp yv cond
    quietly count if `cond' & !missing(`yv', ln_gaci_cwm, feyrer_int, lnpop, ln_sea_ma)
    if r(N) < 60 {
        di as err "SKIP `panel' `grp': N = " r(N)
        exit
    }
    capture noisily ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if `cond', absorb(isocode y) robust
    if _rc exit
    local b = _b[ln_gaci_cwm]
    local se = _se[ln_gaci_cwm]
    local p = 2 * normal(-abs(`b'/`se'))
    quietly levelsof isocode if e(sample), local(cc)
    local nc : word count `cc'
    post `H' ("`panel'") ("`grp'") (`b') (`se') (`p') (e(widstat)) (e(N)) (`nc')
    di "HET [`panel'] `grp': b = " %8.3f `b' " (se " %7.3f `se' ")  KP F = " %7.1f e(widstat) "  N = " %7.0f e(N) "  countries = " `nc'
end

* =====================================================================
* A) income terciles, outcome = intl CO2
* =====================================================================
di _n "===== A) baseline income terciles (ln_co2_tot) ====="
runcell `H' "A_income" "inc_low" ln_co2_tot "inc3 == 1"
runcell `H' "A_income" "inc_mid" ln_co2_tot "inc3 == 2"
runcell `H' "A_income" "inc_high" ln_co2_tot "inc3 == 3"

* pooled interaction test: top tercile vs rest
gen byte hi_inc = inc3 == 3 if !missing(inc3)
gen ma_x_hiinc = ln_gaci_cwm * hi_inc
gen iv_x_hiinc = feyrer_int * hi_inc
ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm ma_x_hiinc = feyrer_int iv_x_hiinc), absorb(isocode y) robust
local bi = _b[ma_x_hiinc]
local si = _se[ma_x_hiinc]
post `H' ("A_income") ("interact_hi") (`bi') (`si') (2*normal(-abs(`bi'/`si'))) (e(widstat)) (e(N)) (.)
di "INTERACTION income-high x MA: b = " %8.3f `bi' " (se " %7.3f `si' ")  KP F = " %7.1f e(widstat)

* =====================================================================
* B) baseline connectivity terciles, outcome = intl CO2
* =====================================================================
di _n "===== B) baseline connectivity terciles (ln_co2_tot) ====="
runcell `H' "B_conn" "con_low" ln_co2_tot "con3 == 1"
runcell `H' "B_conn" "con_mid" ln_co2_tot "con3 == 2"
runcell `H' "B_conn" "con_high" ln_co2_tot "con3 == 3"

gen byte hi_con = con3 == 3 if !missing(con3)
gen ma_x_hicon = ln_gaci_cwm * hi_con
gen iv_x_hicon = feyrer_int * hi_con
ivreghdfe ln_co2_tot lnpop ln_sea_ma (ln_gaci_cwm ma_x_hicon = feyrer_int iv_x_hicon), absorb(isocode y) robust
local bi = _b[ma_x_hicon]
local si = _se[ma_x_hicon]
post `H' ("B_conn") ("interact_hi") (`bi') (`si') (2*normal(-abs(`bi'/`si'))) (e(widstat)) (e(N)) (.)
di "INTERACTION conn-high x MA: b = " %8.3f `bi' " (se " %7.3f `si' ")  KP F = " %7.1f e(widstat)

* =====================================================================
* C) macro regions, outcome = intl CO2
* =====================================================================
di _n "===== C) macro regions (ln_co2_tot) ====="
foreach r in Europe AsiaPacific Africa LatAm MiddleEast NorthAm {
    runcell `H' "C_region" "`r'" ln_co2_tot `"mreg == "`r'""'
}

* =====================================================================
* D) intensity outcome across income terciles
* =====================================================================
di _n "===== D) baseline income terciles (ln_intensity) ====="
runcell `H' "D_intens" "inc_low" ln_intensity "inc3 == 1"
runcell `H' "D_intens" "inc_mid" ln_intensity "inc3 == 2"
runcell `H' "D_intens" "inc_high" ln_intensity "inc3 == 3"

postclose `H'
use "_feyrer_hetero_tot_post.dta", clear
export delimited "_feyrer_hetero_tot.csv", replace
erase "_feyrer_hetero_tot_post.dta"
list, clean noobs
