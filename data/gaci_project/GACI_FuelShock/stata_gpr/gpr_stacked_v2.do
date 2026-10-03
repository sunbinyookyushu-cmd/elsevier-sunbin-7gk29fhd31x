* =====================================================================
* Geopolitical shocks and air service: follow-up checks (GACI_FuelShock)
* Data: 79b_export_gpr_stata.py (2.5 = 30 events, 3.0 = 13 larger events)
* A. 30 events: GACI only and size only (collinearity check)
* B. 13 larger events (own z above 3.0, rule fixed before looking)
* C. effect of each of the 30 events, seats and routes
*    (one treated country per event, so SE clustered by airport, for reference)
* Same FE as gpr_stacked.do. Needs reghdfe, ftools, estout.
* =====================================================================

clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_gpr"
cap log close
log using "gpr_stacked_v2_run.log", replace text

cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which esttab
if _rc ssc install estout

estimates clear

* ---------------- A. 30 events, one moderator at a time ----------------
use "gpr_stack_seats.dta", clear
corr G Sz if e == 0 & treat == 1
reghdfe ln_seats tp tpG pG, absorb(fe_u fe_t) vce(cluster iso3n)
eststo A_S_G
reghdfe ln_seats tp tpS pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo A_S_S

use "gpr_stack_routes.dta", clear
reghdfe ln_deg tp tpG pG, absorb(fe_u fe_t) vce(cluster iso3n)
eststo A_R_G
reghdfe ln_deg tp tpS pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo A_R_S

esttab A_S_G A_S_S A_R_G A_R_S, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp tpG tpS pG pS) order(tp tpG tpS pG pS) stats(N N_clust, labels("Observations" "Countries")) mtitles("Seats G" "Seats size" "Routes G" "Routes size")
esttab A_S_G A_S_S A_R_G A_R_S using "gpr_v2_A_single_moderator.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp tpG tpS pG pS) order(tp tpG tpS pG pS) stats(N N_clust, labels("Observations" "Countries")) mtitles("Seats G" "Seats size" "Routes G" "Routes size")

* ---------------- B. 13 larger events (z above 3.0) ----------------
use "gpr_events_z30.dta", clear
list stk iso3 onset z, noobs

use "gpr_stack_seats_z30.dta", clear
reghdfe ln_seats tp, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_S1
reghdfe ln_seats tp tpG tpS pG pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_S2
reghdfe ln_seats tp tpG pG, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_S3
reghdfe ln_seats tp tpS pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_S4

use "gpr_stack_routes_z30.dta", clear
reghdfe ln_deg tp, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_R1
reghdfe ln_deg tp tpG tpS pG pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_R2
reghdfe ln_deg tp tpG pG, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_R3
reghdfe ln_deg tp tpS pS, absorb(fe_u fe_t) vce(cluster iso3n)
eststo B_R4

esttab B_S1 B_S2 B_S3 B_S4 B_R1 B_R2 B_R3 B_R4, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp tpG tpS pG pS) order(tp tpG tpS pG pS) stats(N N_clust, labels("Observations" "Countries")) mtitles("Seats" "Seats" "Seats G" "Seats size" "Routes" "Routes" "Routes G" "Routes size")
esttab B_S1 B_S2 B_S3 B_S4 B_R1 B_R2 B_R3 B_R4 using "gpr_v2_B_large_events.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp tpG tpS pG pS) order(tp tpG tpS pG pS) stats(N N_clust, labels("Observations" "Countries")) mtitles("Seats" "Seats" "Seats G" "Seats size" "Routes" "Routes" "Routes G" "Routes size")

* ---------------- C. each of the 30 events ----------------
* b_tp, se_tp: average effect (tp only)
* b_tp2 ... se_tpS: model with tp tpG tpS pG pS
cap postclose pfh
postfile pfh str6 outcome stk b_tp se_tp b_tp2 se_tp2 b_tpG se_tpG b_tpS se_tpS n using "gpr_byevent.dta", replace

use "gpr_stack_seats.dta", clear
forvalues k = 0/29 {
    scalar b1 = .
    scalar s1 = .
    capture quietly reghdfe ln_seats tp if stk == `k', absorb(fe_u fe_t) vce(cluster airport_n)
    if _rc == 0 {
        scalar b1 = _b[tp]
        scalar s1 = _se[tp]
    }
    capture quietly reghdfe ln_seats tp tpG tpS pG pS if stk == `k', absorb(fe_u fe_t) vce(cluster airport_n)
    if _rc == 0 {
        post pfh ("seats") (`k') (scalar(b1)) (scalar(s1)) (_b[tp]) (_se[tp]) (_b[tpG]) (_se[tpG]) (_b[tpS]) (_se[tpS]) (e(N))
    }
    else {
        post pfh ("seats") (`k') (scalar(b1)) (scalar(s1)) (.) (.) (.) (.) (.) (.) (.)
    }
}

use "gpr_stack_routes.dta", clear
forvalues k = 0/29 {
    scalar b1 = .
    scalar s1 = .
    capture quietly reghdfe ln_deg tp if stk == `k', absorb(fe_u fe_t) vce(cluster airport_n)
    if _rc == 0 {
        scalar b1 = _b[tp]
        scalar s1 = _se[tp]
    }
    capture quietly reghdfe ln_deg tp tpG tpS pG pS if stk == `k', absorb(fe_u fe_t) vce(cluster airport_n)
    if _rc == 0 {
        post pfh ("routes") (`k') (scalar(b1)) (scalar(s1)) (_b[tp]) (_se[tp]) (_b[tpG]) (_se[tpG]) (_b[tpS]) (_se[tpS]) (e(N))
    }
    else {
        post pfh ("routes") (`k') (scalar(b1)) (scalar(s1)) (.) (.) (.) (.) (.) (.) (.)
    }
}
postclose pfh

use "gpr_byevent.dta", clear
merge m:1 stk using "gpr_events.dta", keepusing(iso3 onset z) nogenerate
order outcome stk iso3 onset z
sort outcome stk
format b_* se_* %9.4f
format z %5.2f
list outcome iso3 onset b_tp se_tp b_tpG se_tpG b_tpS se_tpS n, sepby(outcome) noobs abbreviate(8)
export delimited using "gpr_byevent.csv", replace

log close
