*==============================================================================
* co2_temporal_excovid.do
* 2SLS by subperiod with COVID years (2020-2021) excluded
* outcomes: ln_co2_tot, ln_co2_intl, ln_skm, ln_intensity
* samples: full exCOVID / 1996-2009 / 2010-2023 exCOVID /
*          2010-2023 exCOVID+exGFCtail(=same) / 2006-2023 exCOVID /
*          2010-2019 (clean pre-COVID later half)
* -> _temporal_excovid.csv
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
keep iso3 year co2_bunker co2_bunker_intl dep_seat_km
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

local cond1 "y != 2020 & y != 2021"
local lab1  "full_exCOVID"
local cond2 "y < 2010"
local lab2  "1996-2009"
local cond3 "y >= 2010 & y != 2020 & y != 2021"
local lab3  "2010-2023_exCOVID"
local cond4 "y >= 2010 & y <= 2019"
local lab4  "2010-2019"
local cond5 "y >= 2006 & y != 2020 & y != 2021"
local lab5  "2006-2023_exCOVID"
local cond6 "y >= 2012 & y != 2020 & y != 2021"
local lab6  "2012-2023_exCOVID"

tempname T
postfile `T' str24 samp str16 outc double(b se p kpf) long(nn) using "_txc_tmp", replace
foreach yv in ln_co2_tot ln_co2_intl ln_skm ln_intensity {
    forvalues i = 1/6 {
        quietly ivreghdfe `yv' lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int) if `cond`i'', absorb(isocode y) robust
        local bb = _b[ln_gaci_cwm]
        local ss = _se[ln_gaci_cwm]
        di "XC `lab`i'' `yv': b=" %7.3f `bb' " se=" %6.3f `ss' " F=" %7.1f e(widstat) " N=" e(N)
        post `T' ("`lab`i''") ("`yv'") (`bb') (`ss') (2*normal(-abs(`bb'/`ss'))) (e(widstat)) (e(N))
    }
}
postclose `T'
preserve
use "_txc_tmp", clear
export delimited "_temporal_excovid.csv", replace
restore
erase "_txc_tmp.dta"

di "EXCOVID TEMPORAL DONE"
