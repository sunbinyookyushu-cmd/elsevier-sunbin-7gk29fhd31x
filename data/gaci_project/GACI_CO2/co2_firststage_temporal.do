*==============================================================================
* co2_firststage_temporal.do
* First stage by subperiod + year-specific first-stage slopes
* A) reghdfe ln_gaci_cwm feyrer_int lnpop ln_sea_ma, absorb(isocode y) robust
*    samples: full / 1996-2005 / 2006-2023 / 2006-2023 exGFC /
*             1996-2009 / 2010-2023 / 2010-2023 ex-COVID(drop 2020-21)
*    -> _fs_subperiod.csv  (b, se, t, partial F, N)
* B) year-specific slopes: c.feyrer_int#i.y (base 1996) + FE
*    -> _fs_byyear.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
set seed 20260826
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

* ---- build merged dataset (identical to co2_extensions.do) ----
import delimited "co2_country_year.csv", clear varnames(1) encoding("utf-8")
keep iso3 year co2_bunker dep_seat_km
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
* keep estimation sample aligned with the 2SLS (outcome non-missing)
keep if !missing(ln_co2_tot, ln_gaci_cwm, feyrer_int, lnpop, ln_sea_ma)

* =====================================================================
* A) subperiod first stages
* =====================================================================
tempname S
postfile `S' str24 samp double(b se t pF) long(nn) using "_fs_tmp", replace

local cond1 "1"
local lab1  "full_1996-2023"
local cond2 "y < 2006"
local lab2  "1996-2005"
local cond3 "y >= 2006"
local lab3  "2006-2023"
local cond4 "y >= 2006 & y != 2008 & y != 2009"
local lab4  "2006-2023_exGFC"
local cond5 "y < 2010"
local lab5  "1996-2009"
local cond6 "y >= 2010"
local lab6  "2010-2023"
local cond7 "y >= 2010 & y != 2020 & y != 2021"
local lab7  "2010-2023_exCOVID"

forvalues i = 1/7 {
    quietly reghdfe ln_gaci_cwm feyrer_int lnpop ln_sea_ma if `cond`i'', absorb(isocode y) vce(robust)
    local bb = _b[feyrer_int]
    local ss = _se[feyrer_int]
    quietly test feyrer_int
    di "FS `lab`i'': b=" %8.4f `bb' " se=" %7.4f `ss' " t=" %6.2f `bb'/`ss' " F=" %8.1f r(F) " N=" e(N)
    post `S' ("`lab`i''") (`bb') (`ss') (`bb'/`ss') (r(F)) (e(N))
}
postclose `S'
preserve
use "_fs_tmp", clear
export delimited "_fs_subperiod.csv", replace
restore
erase "_fs_tmp.dta"

* =====================================================================
* B) year-specific first-stage slopes (base year 1996)
* =====================================================================
quietly reghdfe ln_gaci_cwm c.feyrer_int#ib1996.y lnpop ln_sea_ma, absorb(isocode y) vce(robust)
tempname Y
postfile `Y' int y double(b se) using "_fsy_tmp", replace
forvalues t = 1996/2023 {
    if `t' == 1996 {
        post `Y' (1996) (0) (0)
    }
    else {
        capture local bb = _b[c.feyrer_int#`t'.y]
        capture local ss = _se[c.feyrer_int#`t'.y]
        di "FSYEAR `t': b_rel1996=" %8.4f `bb' " se=" %7.4f `ss'
        post `Y' (`t') (`bb') (`ss')
    }
}
postclose `Y'
preserve
use "_fsy_tmp", clear
export delimited "_fs_byyear.csv", replace
restore
erase "_fsy_tmp.dta"

di "FS TEMPORAL DONE"
