* 03_leakage.do  Net-of-leakage checks for the seat and CO2 effects (companion to 01_main.do), rewritten 2026-10-03
* Four tests on the existing stacks. Every regression includes the country controls lngdp lnpop; SE clustered by country.
* Fully inline: no programs, loops, locals or scalars, so any block (from its "use" line) can be selected and run alone.
*   A. Baseline (Table 4 col 1) with adjacent-country airports removed from the control group
*   B. Spillover: adjacent-country hubs (w0 >= 1m seats) and non-hubs as the "treated" group, true treated dropped
*   C. Bloc level: treated country + adjacent countries + border ring summed into one unit per event; DiD and SDID
*   D. Re-routing signature at adjacent-country hubs (annual stack): stage length, CO2 per flight, destinations
* Event codes (stack_month.dta, verified in events.dta): 0 NLD 2008, 1 IRL 2009, 2 DEU 2011, 3 AUT 2011, 4 NOR 2016,
*   5 SWE 2018, 6 GBR 2007, 7 DNK 1998, 8 MLT 2005. Event 0 (NLD) is excluded from every block (stk != 0), as in 01_main.do.
* Adjacency (land or short sea border) is written out per block as nbr = 1. IRL 2009: its only neighbour GBR was taxed in 2007
*   and is already outside the control pool, so nbr covers only GBR border-ring airports.
* The sample condition of 01_main.do applies: eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat | border | ctrl_eur).
clear all
set more off
set linesize 200
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper"
cap log close
log using "03_leakage_run.log", replace text
cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which esttab
if _rc ssc install estout
cap which sdid
if _rc ssc install sdid
estimates clear

* =====================================================================================
* A. Baseline with adjacent-country airports removed from the controls (monthly stack, first tax year)
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen byte nbr = 0
replace nbr = 1 if stk == 0 & inlist(iso3, "DEU", "BEL")
replace nbr = 1 if stk == 1 & inlist(iso3, "GBR")
replace nbr = 1 if stk == 2 & inlist(iso3, "NLD", "BEL", "LUX", "FRA", "CHE", "AUT", "CZE", "POL", "DNK")
replace nbr = 1 if stk == 3 & inlist(iso3, "DEU", "CHE", "ITA", "SVN", "HUN", "SVK", "CZE")
replace nbr = 1 if stk == 4 & inlist(iso3, "SWE", "DNK", "FIN")
replace nbr = 1 if stk == 5 & inlist(iso3, "NOR", "DNK", "FIN")
replace nbr = 1 if stk == 6 & inlist(iso3, "IRL", "FRA", "NLD", "BEL")
replace nbr = 1 if stk == 7 & inlist(iso3, "DEU", "SWE", "NOR")
replace nbr = 1 if stk == 8 & inlist(iso3, "ITA")
replace nbr = 0 if treat == 1
gen tp = treat * post1
gen bp = border * post1
gen hub = (w0 >= 1000000)
gen nbr_hub = nbr * hub * (border == 0)
gen nbr_nonhub = nbr * (1 - hub) * (border == 0)
gen nhp = nbr_hub * post1
gen nnp = nbr_nonhub * post1
* A0 reference: Table 4 col 1 and Table 2 col 1 as in 01_main.do
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo A0_co2
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo A0_seats
* A1 drop non-border airports of adjacent countries (border ring kept as its own group)
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | (ctrl_eur == 1 & nbr == 0)), absorb(fe_u fe_t) vce(cluster iso3n)
eststo A1_co2
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | (ctrl_eur == 1 & nbr == 0)), absorb(fe_u fe_t) vce(cluster iso3n)
eststo A1_seats
* A2 drop every adjacent-country airport, border ring included
reghdfe ln_co2 tp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | (ctrl_eur == 1 & nbr == 0 & border == 0)), absorb(fe_u fe_t) vce(cluster iso3n)
eststo A2_co2
reghdfe ln_seats tp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | (ctrl_eur == 1 & nbr == 0 & border == 0)), absorb(fe_u fe_t) vce(cluster iso3n)
eststo A2_seats
esttab A0_co2 A1_co2 A2_co2 A0_seats A1_seats A2_seats using "L_A_controls.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust, labels("Observations" "Countries")) title("Leakage A: baseline with adjacent-country airports removed from the controls (A0 all, A1 non-border adjacent dropped, A2 all adjacent dropped)")
esttab A0_co2 A1_co2 A2_co2 A0_seats A1_seats A2_seats, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust)

* =====================================================================================
* B. Spillover to adjacent countries: hubs (w0 >= 1m) and non-hubs beyond the 300 km ring, true treated airports dropped
*    Positive nhp = traffic or emissions moved to foreign hubs (diversion or re-routing)
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen byte nbr = 0
replace nbr = 1 if stk == 0 & inlist(iso3, "DEU", "BEL")
replace nbr = 1 if stk == 1 & inlist(iso3, "GBR")
replace nbr = 1 if stk == 2 & inlist(iso3, "NLD", "BEL", "LUX", "FRA", "CHE", "AUT", "CZE", "POL", "DNK")
replace nbr = 1 if stk == 3 & inlist(iso3, "DEU", "CHE", "ITA", "SVN", "HUN", "SVK", "CZE")
replace nbr = 1 if stk == 4 & inlist(iso3, "SWE", "DNK", "FIN")
replace nbr = 1 if stk == 5 & inlist(iso3, "NOR", "DNK", "FIN")
replace nbr = 1 if stk == 6 & inlist(iso3, "IRL", "FRA", "NLD", "BEL")
replace nbr = 1 if stk == 7 & inlist(iso3, "DEU", "SWE", "NOR")
replace nbr = 1 if stk == 8 & inlist(iso3, "ITA")
replace nbr = 0 if treat == 1
gen bp = border * post1
gen hub = (w0 >= 1000000)
gen nbr_hub = nbr * hub * (border == 0)
gen nbr_nonhub = nbr * (1 - hub) * (border == 0)
gen nhp = nbr_hub * post1
gen nnp = nbr_nonhub * post1
gen NH_pre36_25 = nbr_hub * pre36_25
gen NH_pre24_13 = nbr_hub * pre24_13
gen NH_post1 = nbr_hub * post1
gen NH_post2 = nbr_hub * post2
gen NN_pre36_25 = nbr_nonhub * pre36_25
gen NN_pre24_13 = nbr_nonhub * pre24_13
gen NN_post1 = nbr_nonhub * post1
gen NN_post2 = nbr_nonhub * post2
reghdfe ln_co2 nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo B1_co2
reghdfe ln_seats nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo B2_seats
reghdfe ln_fl nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo B3_fl
reghdfe ln_gauge nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo B4_gauge
* event-time version (pre-trend check on the spillover itself), both post years
reghdfe ln_co2 NH_pre36_25 NH_pre24_13 NH_post1 NH_post2 NN_pre36_25 NN_pre24_13 NN_post1 NN_post2 bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo B5_es_co2
reghdfe ln_seats NH_pre36_25 NH_pre24_13 NH_post1 NH_post2 NN_pre36_25 NN_pre24_13 NN_post1 NN_post2 bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo B6_es_seats
esttab B1_co2 B2_seats B3_fl B4_gauge B5_es_co2 B6_es_seats using "L_B_spillover.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp NH_pre36_25 NH_pre24_13 NH_post1 NH_post2 NN_post1 NN_post2) stats(N N_clust, labels("Observations" "Countries")) title("Leakage B: spillover to adjacent-country hubs (w0 >= 1m) and non-hubs")
esttab B1_co2 B2_seats B3_fl B4_gauge B5_es_co2 B6_es_seats, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp NH_pre36_25 NH_pre24_13 NH_post1 NH_post2 NN_post1 NN_post2) stats(N N_clust)

* =====================================================================================
* C. Bloc level: treated country + adjacent countries + border ring summed into one unit per event
*    Units: bloc (unit 1) and every other European control country (unit = iso3n + 1000). Time: fe_t (month x event).
*    Controls lngdp lnpop enter as seat-weighted unit means. Leakage inside the bloc is internalised: a negative bloc
*    effect is a net reduction. The collapsed file bloc_month.dta is saved so the SDID blocks below run alone.
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen byte nbr = 0
replace nbr = 1 if stk == 0 & inlist(iso3, "DEU", "BEL")
replace nbr = 1 if stk == 1 & inlist(iso3, "GBR")
replace nbr = 1 if stk == 2 & inlist(iso3, "NLD", "BEL", "LUX", "FRA", "CHE", "AUT", "CZE", "POL", "DNK")
replace nbr = 1 if stk == 3 & inlist(iso3, "DEU", "CHE", "ITA", "SVN", "HUN", "SVK", "CZE")
replace nbr = 1 if stk == 4 & inlist(iso3, "SWE", "DNK", "FIN")
replace nbr = 1 if stk == 5 & inlist(iso3, "NOR", "DNK", "FIN")
replace nbr = 1 if stk == 6 & inlist(iso3, "IRL", "FRA", "NLD", "BEL")
replace nbr = 1 if stk == 7 & inlist(iso3, "DEU", "SWE", "NOR")
replace nbr = 1 if stk == 8 & inlist(iso3, "ITA")
replace nbr = 0 if treat == 1
keep if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | nbr == 1 | border == 1 | ctrl_eur == 1)
gen double co2_lvl = exp(ln_co2)
gen double seats_lvl = exp(ln_seats)
gen bloc = (treat == 1 | nbr == 1 | border == 1)
gen unit = cond(bloc == 1, 1, iso3n + 1000)
collapse (sum) co2_lvl seats_lvl (mean) post1 t (mean) lngdp lnpop [aw = seats_lvl], by(stk unit fe_t)
gen ln_co2_u = ln(co2_lvl)
gen ln_seats_u = ln(seats_lvl)
gen treat_post = (unit == 1) * post1
egen uid = group(stk unit)
save "bloc_month.dta", replace
* C1 pooled DiD, unit x event and month x event FE, SE clustered by unit
reghdfe ln_co2_u treat_post lngdp lnpop, absorb(uid fe_t) vce(cluster unit)
eststo C1_bloc_co2
reghdfe ln_seats_u treat_post lngdp lnpop, absorb(uid fe_t) vce(cluster unit)
eststo C2_bloc_seats
esttab C1_bloc_co2 C2_bloc_seats using "L_C_bloc_did.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(treat_post) stats(N N_clust, labels("Observations" "Units")) title("Leakage C: bloc-level DiD, treated + adjacent countries + border ring as one unit")
esttab C1_bloc_co2 C2_bloc_seats, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(treat_post) stats(N N_clust)
* C3 SDID per event on the bloc series (placebo inference over donor units); time = consecutive month index within the event
*    (fe_t ids are not chronological, which sdid rejects). Unbalanced events are reported as errors and skipped.
di _n "==== bloc SDID IRL 2009: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 1
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID IRL 2009: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 1
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID DEU 2011: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 2
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID DEU 2011: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 2
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID AUT 2011: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 3
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID AUT 2011: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 3
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID NOR 2016: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 4
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID NOR 2016: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 4
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID SWE 2018: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 5
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID SWE 2018: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 5
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID GBR 2007: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 6
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID GBR 2007: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 6
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID DNK 1998: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 7
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID DNK 1998: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 7
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID MLT 2005: ln CO2 ===="
use "bloc_month.dta", clear
keep if stk == 8
drop if missing(ln_co2_u)
egen period = group(t)
cap noisily sdid ln_co2_u unit period treat_post, vce(placebo) reps(200) seed(1)
di _n "==== bloc SDID MLT 2005: ln seats ===="
use "bloc_month.dta", clear
keep if stk == 8
drop if missing(ln_seats_u)
egen period = group(t)
cap noisily sdid ln_seats_u unit period treat_post, vce(placebo) reps(200) seed(1)

* =====================================================================================
* D. Re-routing signature at adjacent-country hubs (annual stack, years E-3..E): stage length, CO2 per flight, destinations, CO2
*    If long-haul moves to foreign hubs, their mean stage and CO2 per flight rise after the tax; at treated airports stage falls
* =====================================================================================
use "stack_year.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen byte nbr = 0
replace nbr = 1 if stk == 0 & inlist(iso3, "DEU", "BEL")
replace nbr = 1 if stk == 1 & inlist(iso3, "GBR")
replace nbr = 1 if stk == 2 & inlist(iso3, "NLD", "BEL", "LUX", "FRA", "CHE", "AUT", "CZE", "POL", "DNK")
replace nbr = 1 if stk == 3 & inlist(iso3, "DEU", "CHE", "ITA", "SVN", "HUN", "SVK", "CZE")
replace nbr = 1 if stk == 4 & inlist(iso3, "SWE", "DNK", "FIN")
replace nbr = 1 if stk == 5 & inlist(iso3, "NOR", "DNK", "FIN")
replace nbr = 1 if stk == 6 & inlist(iso3, "IRL", "FRA", "NLD", "BEL")
replace nbr = 1 if stk == 7 & inlist(iso3, "DEU", "SWE", "NOR")
replace nbr = 1 if stk == 8 & inlist(iso3, "ITA")
replace nbr = 0 if treat == 1
gen hub = (w0 >= 1000000)
gen nhp = nbr * hub * (border == 0) * post1
gen nnp = nbr * (1 - hub) * (border == 0) * post1
gen bp = border * post1
gen tp = treat * post1
reghdfe ln_stage nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo D1_stage
reghdfe ln_co2_per_fl nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo D2_co2pf
reghdfe ln_deg nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo D3_deg
reghdfe ln_gaci nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo D4_gaci
reghdfe ln_co2 nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo D5_co2
* treated side for comparison: stage and CO2 per flight at treated airports
reghdfe ln_stage tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo D6_treat_stage
reghdfe ln_co2_per_fl tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo D7_treat_co2pf
esttab D1_stage D2_co2pf D3_deg D4_gaci D5_co2 D6_treat_stage D7_treat_co2pf using "L_D_rerouting.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp tp) stats(N N_clust, labels("Observations" "Countries")) title("Leakage D: stage length, CO2 per flight, destinations and GACI at adjacent-country hubs; treated side for comparison")
esttab D1_stage D2_co2pf D3_deg D4_gaci D5_co2 D6_treat_stage D7_treat_co2pf, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp tp) stats(N N_clust)
log close
