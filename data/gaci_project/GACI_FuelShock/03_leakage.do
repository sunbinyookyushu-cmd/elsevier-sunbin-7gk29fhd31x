* =====================================================================================
* 03_leakage.do  Net-of-leakage checks for the CO2 effect (companion to 01_main.do)
*
* Four tests, all on files that already exist in stata_paper\:
*   A. Baseline (Table 4 col 1) with adjacent-country airports removed from the control group
*      -> if the baseline is inflated by contaminated controls, the coefficient shrinks here
*   B. Spillover regression: do hubs in adjacent countries GAIN seats / CO2 after the tax?
*      -> direct test of the re-routing / non-border diversion channel
*   C. Bloc-level DiD and SDID: treated country + all adjacent countries summed into one unit
*      -> leakage inside the bloc is internalised; a negative bloc effect is a net reduction
*   D. Stage length and CO2 per flight at adjacent-country hubs (annual stack)
*      -> re-routing of long-haul via a foreign hub lengthens the hub's average stage
*
* Before running, VERIFY two things against your data:
*   1. stk codes. Taken from the sdid loop order in 02_events_mediation.do:
*      0 NLD 2008, 1 IRL 2009, 2 DEU 2011, 3 AUT 2011, 4 NOR 2016, 5 SWE 2018,
*      6 GBR 2007, 7 DNK 1998, 8 MLT 2005.   Check:  tab stk iso3 if treat == 1
*   2. Adjacency lists in the program `nbr_list` below. Edit freely.
* Variable names used (all appear in 01_main_run.log): iso3 iso3n eur stk donut treat border
*   post1 post2 pre36_25 pre24_13 ln_seats ln_co2 ln_int ln_fl lngdp lnpop fe_u fe_t fe_rt w0
*   stack_year: k ln_stage ln_co2_per_fl ln_deg
* =====================================================================================
clear all
set more off
set linesize 200
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper"
cap log close
log using "03_leakage_run.log", replace text
estimates clear

* ---------- adjacency map: nbr = 1 if the airport's country borders the treated country of its event
cap program drop nbr_list
program define nbr_list
    gen byte nbr = 0
    replace nbr = 1 if stk == 0 & inlist(iso3, "DEU", "BEL")                                        // NLD 2008
    replace nbr = 1 if stk == 1 & inlist(iso3, "GBR")                                               // IRL 2009
    replace nbr = 1 if stk == 2 & inlist(iso3, "NLD", "BEL", "LUX", "FRA", "CHE", "AUT", "CZE", "POL", "DNK")   // DEU 2011
    replace nbr = 1 if stk == 3 & inlist(iso3, "DEU", "CHE", "ITA", "SVN", "HUN", "SVK", "CZE")     // AUT 2011
    replace nbr = 1 if stk == 4 & inlist(iso3, "SWE", "DNK", "FIN")                                 // NOR 2016
    replace nbr = 1 if stk == 5 & inlist(iso3, "NOR", "DNK", "FIN")                                 // SWE 2018
    replace nbr = 1 if stk == 6 & inlist(iso3, "IRL", "FRA", "NLD", "BEL")                          // GBR 2007
    replace nbr = 1 if stk == 7 & inlist(iso3, "DEU", "SWE", "NOR")                                 // DNK 1998
    replace nbr = 1 if stk == 8 & inlist(iso3, "ITA")                                               // MLT 2005
    replace nbr = 0 if treat == 1
end

* =====================================================================================
* A. Baseline with adjacent-country airports removed from the controls (monthly stack)
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
nbr_list
gen tp = treat * post1
gen bp = border * post1
gen hub = (w0 >= 1000000)
gen nbr_hub    = nbr * hub * (border == 0)
gen nbr_nonhub = nbr * (1 - hub) * (border == 0)
gen nhp  = nbr_hub * post1
gen nnp  = nbr_nonhub * post1

local base "eur == 1 & stk != 0 & donut == 0 & post2 == 0"

* A0 reference: Table 4 col 1 as run in 01_main.do
reghdfe ln_co2 tp bp lngdp lnpop if `base' & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store A0_base
* A1 drop non-border airports of adjacent countries (keep the border ring)
reghdfe ln_co2 tp bp lngdp lnpop if `base' & (treat == 1 | border == 1 | (ctrl_eur == 1 & nbr == 0)), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store A1_noadj
* A2 drop every adjacent-country airport, border ring included
reghdfe ln_co2 tp lngdp lnpop if `base' & (treat == 1 | (ctrl_eur == 1 & nbr == 0 & border == 0)), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store A2_noadj_nobrd
* A3 same for seats
reghdfe ln_seats tp lngdp lnpop if `base' & (treat == 1 | (ctrl_eur == 1 & nbr == 0 & border == 0)), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store A3_seats
esttab A0_base A1_noadj A2_noadj_nobrd A3_seats using "L_A_controls.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust, labels("Observations" "Countries")) title("Leakage A: CO2 effect with adjacent-country airports removed from controls")
esttab A0_base A1_noadj A2_noadj_nobrd A3_seats, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust)

* =====================================================================================
* B. Spillover: adjacent-country airports as the "treated" group, true treated dropped
*    Positive nhp = traffic / emissions moved to foreign hubs (diversion or re-routing)
* =====================================================================================
reghdfe ln_co2 nhp nnp bp lngdp lnpop if `base' & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store B1_co2
reghdfe ln_seats nhp nnp bp lngdp lnpop if `base' & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store B2_seats
reghdfe ln_fl nhp nnp bp lngdp lnpop if `base' & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store B3_fl
* event-time version for the hub spillover (pre-trend check on the spillover itself)
gen NH_pre36_25 = nbr_hub * pre36_25
gen NH_pre24_13 = nbr_hub * pre24_13
gen NH_post1    = nbr_hub * post1
gen NH_post2    = nbr_hub * post2
reghdfe ln_co2 NH_pre36_25 NH_pre24_13 NH_post1 NH_post2 nnp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store B4_es
esttab B1_co2 B2_seats B3_fl B4_es using "L_B_spillover.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp NH_pre36_25 NH_pre24_13 NH_post1 NH_post2) stats(N N_clust, labels("Observations" "Countries")) title("Leakage B: spillover to adjacent-country hubs (w0 >= 1m) and non-hubs")
esttab B1_co2 B2_seats B3_fl B4_es, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp NH_pre36_25 NH_pre24_13 NH_post1 NH_post2) stats(N N_clust)

* =====================================================================================
* C. Bloc level: treated country + adjacent countries summed into one unit per event
*    Units: bloc (unit id 1) and every other European country not in the bloc. Time: fe_t within event.
* =====================================================================================
preserve
keep if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | nbr == 1 | border == 1 | ctrl_eur == 1)
gen double co2_lvl   = exp(ln_co2)
gen double seats_lvl = exp(ln_seats)
gen bloc = (treat == 1 | nbr == 1 | border == 1)
gen unit = cond(bloc == 1, 1, iso3n + 1000)
collapse (sum) co2_lvl seats_lvl (mean) post1 lngdp lnpop, by(stk unit fe_t)
gen ln_co2_u   = ln(co2_lvl)
gen ln_seats_u = ln(seats_lvl)
gen bloc = (unit == 1)
gen treat_post = bloc * post1
egen uid = group(stk unit)
* C1 pooled DiD, unit x event and month x event FE, SE clustered by unit
reghdfe ln_co2_u treat_post, absorb(uid fe_t) vce(cluster unit)
estimates store C1_bloc_co2
reghdfe ln_seats_u treat_post, absorb(uid fe_t) vce(cluster unit)
estimates store C2_bloc_seats
esttab C1_bloc_co2 C2_bloc_seats using "L_C_bloc_did.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(treat_post) stats(N N_clust, labels("Observations" "Units")) title("Leakage C: bloc-level DiD, treated + adjacent countries as one unit")
esttab C1_bloc_co2 C2_bloc_seats, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(treat_post) stats(N N_clust)
* C3 SDID per event on the bloc series (needs a balanced panel; unbalanced events are skipped with a message)
cap which sdid
if _rc ssc install sdid
levelsof stk, local(evs)
foreach e of local evs {
    di _n "==== bloc SDID, event stk = `e': ln CO2 ===="
    preserve
    keep if stk == `e'
    drop if missing(ln_co2_u)
    cap noisily sdid ln_co2_u unit fe_t treat_post, vce(placebo) reps(200) seed(1)
    restore
}
restore

* =====================================================================================
* D. Re-routing signature at adjacent-country hubs (annual stack): stage length and CO2 per flight
*    If long-haul moves to foreign hubs, their average stage and CO2 per flight rise after the tax
* =====================================================================================
use "stack_year.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
nbr_list
gen hub = (w0 >= 1000000)
gen nhp = nbr * hub * (border == 0) * post1
gen nnp = nbr * (1 - hub) * (border == 0) * post1
gen bp  = border * post1
gen tp  = treat * post1
local ys "ln_stage ln_co2_per_fl ln_deg ln_co2"
foreach y of local ys {
    reghdfe `y' nhp nnp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & treat == 0 & (nbr == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
    estimates store D_`y'
}
* and the treated side for comparison (stage falls at treated airports if long-haul is shed)
reghdfe ln_stage tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
estimates store D_treat_stage
esttab D_ln_stage D_ln_co2_per_fl D_ln_deg D_ln_co2 D_treat_stage using "L_D_rerouting.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp tp) stats(N N_clust, labels("Observations" "Countries")) title("Leakage D: stage length and CO2 per flight at adjacent-country hubs")
esttab D_ln_stage D_ln_co2_per_fl D_ln_deg D_ln_co2 D_treat_stage, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(nhp nnp bp tp) stats(N N_clust)

log close
