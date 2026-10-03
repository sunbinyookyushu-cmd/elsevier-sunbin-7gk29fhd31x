clear all
set more off
set linesize 200
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper"
cap log close
log using "02_events_mediation_run.log", replace text
cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which esttab
if _rc ssc install estout
estimates clear
cap which sdid
if _rc ssc install sdid
cap which honestdid
if _rc net install honestdid, from("https://raw.githubusercontent.com/mcaceresb/stata-honestdid/main") replace
cap which ivreghdfe
if _rc ssc install ivreghdfe
cap which ivmediate
if _rc ssc install ivmediate
cap which weakiv
if _rc ssc install weakiv

* =====================================================================================
* Table 6  Synthetic difference-in-differences by event (Arkhangelsky et al. 2021), country level
* sdid_month.dta: country x period (donut removed), de-seasonalised ln seats / ln CO2; treat_post = treated country after E
* placebo inference over donors. One block per event and outcome.
* =====================================================================================
use "sdid_month.dta", clear
di _n "==== SDID NLD 2008: y_seats ===="
preserve
keep if stk == 0
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID NLD 2008: y_co2 ===="
preserve
keep if stk == 0
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID IRL 2009: y_seats ===="
preserve
keep if stk == 1
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID IRL 2009: y_co2 ===="
preserve
keep if stk == 1
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID DEU 2011: y_seats ===="
preserve
keep if stk == 2
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID DEU 2011: y_co2 ===="
preserve
keep if stk == 2
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID AUT 2011: y_seats ===="
preserve
keep if stk == 3
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID AUT 2011: y_co2 ===="
preserve
keep if stk == 3
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID NOR 2016: y_seats ===="
preserve
keep if stk == 4
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID NOR 2016: y_co2 ===="
preserve
keep if stk == 4
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID SWE 2018: y_seats ===="
preserve
keep if stk == 5
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID SWE 2018: y_co2 ===="
preserve
keep if stk == 5
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID GBR 2007: y_seats ===="
preserve
keep if stk == 6
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID GBR 2007: y_co2 ===="
preserve
keep if stk == 6
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID DNK 1998: y_seats ===="
preserve
keep if stk == 7
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID DNK 1998: y_co2 ===="
preserve
keep if stk == 7
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID MLT 2005: y_seats ===="
preserve
keep if stk == 8
drop if missing(y_seats)
sdid y_seats iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID MLT 2005: y_co2 ===="
preserve
keep if stk == 8
drop if missing(y_co2)
sdid y_co2 iso3n period treat_post, vce(placebo) reps(200) seed(1)
restore

use "sdid_year.dta", clear
di _n "==== SDID NLD 2008: seat-weighted country GACI ===="
preserve
keep if stk == 0
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID IRL 2009: seat-weighted country GACI ===="
preserve
keep if stk == 1
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID DEU 2011: seat-weighted country GACI ===="
preserve
keep if stk == 2
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID AUT 2011: seat-weighted country GACI ===="
preserve
keep if stk == 3
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID NOR 2016: seat-weighted country GACI ===="
preserve
keep if stk == 4
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID SWE 2018: seat-weighted country GACI ===="
preserve
keep if stk == 5
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID GBR 2007: seat-weighted country GACI ===="
preserve
keep if stk == 6
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID DNK 1998: seat-weighted country GACI ===="
preserve
keep if stk == 7
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore
di _n "==== SDID MLT 2005: seat-weighted country GACI ===="
preserve
keep if stk == 8
cap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)
restore

* =====================================================================================
* HonestDiD (Rambachan and Roth 2023) on the monthly event-time regression of Table 5 (seats and CO2), with controls
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen T_pre36_25 = treat * pre36_25
gen T_pre24_13 = treat * pre24_13
gen T_post1 = treat * post1
gen T_post2 = treat * post2
gen B_pre36_25 = border * pre36_25
gen B_pre24_13 = border * pre24_13
gen B_post1 = border * post1
gen B_post2 = border * post2
reghdfe ln_seats T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2 lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
honestdid, pre(1/2) post(3/4) mvec(0(0.5)2) delta(rm)
honestdid, pre(1/2) post(3/4) mvec(0(0.01)0.05)
reghdfe ln_co2 T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2 lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
honestdid, pre(1/2) post(3/4) mvec(0(0.5)2) delta(rm)
honestdid, pre(1/2) post(3/4) mvec(0(0.01)0.05)

* =====================================================================================
* Appendix D  IV mediation: tax -> network -> CO2 (annual stacks, years E-3..E, 8 European events), with controls
*   ivmediate: treatment = dose_post (EUR x post), instrument = tp, mediator = ln destinations / ln GACI
*   2SLS: CO2 on the mediator instrumented by tp (M -> Y link under exclusion); weakiv for Anderson-Rubin sets
* =====================================================================================
use "stack_year.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
keep if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1)
gen tp = treat * post1
gen bp = border * post1
gen dose_post = dose * post1
ivmediate ln_co2 bp lngdp lnpop i.fe_t, mediator(ln_deg) treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
ivmediate ln_co2 bp lngdp lnpop i.fe_t, mediator(ln_gaci) treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
ivmediate ln_int bp lngdp lnpop i.fe_t, mediator(ln_deg) treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
ivreghdfe ln_co2 bp lngdp lnpop (ln_deg = tp), absorb(fe_u fe_t) cluster(iso3n) first
cap noisily weakiv, level(95)
ivreghdfe ln_co2 bp lngdp lnpop (ln_gaci = tp), absorb(fe_u fe_t) cluster(iso3n) first
cap noisily weakiv, level(95)
reghdfe ln_co2 tp bp lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
reghdfe ln_deg tp bp lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
reghdfe ln_co2 tp bp ln_deg lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
reghdfe ln_gaci tp bp lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
reghdfe ln_co2 tp bp ln_gaci lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
log close
