* =====================================================================
* Geopolitical shocks and air service: stacked DiD (GACI_FuelShock)
* Data built by 79b_export_gpr_stata.py (same rules as 79_gpr_stacked.py)
*   Shock: Caldara and Iacoviello (2022) country GPR index, 44 countries
*   Event: own z-score above 2.5, no event in the previous 24 months,
*          no world GPR spike the same month, onsets 2000-2017 (30 events)
*   Stack: treated country airports plus airports of GPR countries
*          with no event within +-24 months of the onset
*   G, Sz: ln GACI and ln seats in the year before onset (z-scores)
* Models
*   (1)  y = b tp + FE
*   (1b) same, moderator sample
*   (2)  y = b tp + g tpG + th tpS + l pG + k pS + FE
*   (3)  event study by GACI half (hi = above treated-country median)
* Seats: monthly ln seats, FE airport x calendar month x stack, month x stack
* Routes: annual ln Degree, FE airport x stack, year x stack
* SE clustered by country (iso3n)
* Needs: reghdfe, ftools, estout (installed below if missing)
* =====================================================================

clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_gpr"
cap log close
log using "gpr_stacked_run.log", replace text

cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which esttab
if _rc ssc install estout

estimates clear

* ---------------- seats (monthly) ----------------
use "gpr_stack_seats.dta", clear
describe, short
tab stk treat if e == 0

reghdfe ln_seats tp, absorb(fe_u fe_t) vce(cluster iso3n)
eststo S1
reghdfe ln_seats tp if !missing(G, Sz), absorb(fe_u fe_t) vce(cluster iso3n)
eststo S1b
reghdfe ln_seats tp tpG tpS pG pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo S2
reghdfe ln_seats hi_m24_m19 hi_m18_m13 hi_0_5 hi_6_11 hi_12_17 hi_18_24 lo_m24_m19 lo_m18_m13 lo_0_5 lo_6_11 lo_12_17 lo_18_24 if !missing(G, Sz), absorb(fe_u fe_t) vce(cluster iso3n)
eststo S3

* ---------------- routes (annual) ----------------
use "gpr_stack_routes.dta", clear
describe, short

reghdfe ln_deg tp, absorb(fe_u fe_t) vce(cluster iso3n)
eststo R1
reghdfe ln_deg tp if !missing(G, Sz), absorb(fe_u fe_t) vce(cluster iso3n)
eststo R1b
reghdfe ln_deg tp tpG tpS pG pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo R2
reghdfe ln_deg hi_m2_m2 hi_0_0 hi_1_1 hi_2_2 lo_m2_m2 lo_0_0 lo_1_1 lo_2_2 if !missing(G, Sz), absorb(fe_u fe_t) vce(cluster iso3n)
eststo R3

* ---------------- tables ----------------
esttab S1 S1b S2 R1 R1b R2, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp tpG tpS pG pS) order(tp tpG tpS pG pS) stats(N N_clust, labels("Observations" "Countries")) mtitles("Seats" "Seats" "Seats" "Routes" "Routes" "Routes")
esttab S1 S1b S2 R1 R1b R2 using "gpr_did_table.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp tpG tpS pG pS) order(tp tpG tpS pG pS) stats(N N_clust, labels("Observations" "Countries")) mtitles("Seats" "Seats" "Seats" "Routes" "Routes" "Routes")
esttab S3 R3, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) mtitles("Seats ES" "Routes ES")
esttab S3 R3 using "gpr_es_table.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) mtitles("Seats ES" "Routes ES")

log close
