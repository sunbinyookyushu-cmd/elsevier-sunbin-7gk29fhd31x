clear all
set more off
set linesize 200
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper"
cap log close
log using "01_main_run.log", replace text
cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which esttab
if _rc ssc install estout
estimates clear

* =====================================================================================
* Table 2  Seats, first tax year. Treated x post = tp; border x post = bp; size terciles tp_small tp_mid tp_large
* Sample: 8 European tax increases (Netherlands separate), pre [A-36,A-1], post [E,E+11], anticipation months dropped
* FE: airport x calendar month x event (fe_u), month x event (fe_t). Controls: country ln GDP, ln population. SE: country
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen tp = treat * post1
gen bp = border * post1
gen tp_small = sz_small * post1
gen tp_mid = sz_mid * post1
gen tp_large = sz_large * post1
gen dose_post = dose * post1
gen T_pre36_25 = treat * pre36_25
gen T_pre24_13 = treat * pre24_13
gen T_post1 = treat * post1
gen T_post2 = treat * post2
gen B_pre36_25 = border * pre36_25
gen B_pre24_13 = border * pre24_13
gen B_post1 = border * post1
gen B_post2 = border * post2
gen hub = (w0 >= 1000000)
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo s_all
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo s_wt
reghdfe ln_seats tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo s_size
reghdfe ln_seats tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo s_size_wt
reghdfe ln_seats dose_post bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo s_dose
reghdfe ln_seats tp dose_post bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo s_dose2
esttab s_all s_wt s_size s_size_wt s_dose s_dose2 using "T2_seats.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large dose_post) stats(N N_clust, labels("Observations" "Countries")) title("Table 2 Seats")
esttab s_all s_wt s_size s_size_wt s_dose s_dose2, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large dose_post) stats(N N_clust)

* =====================================================================================
* Table 4  CO2 (departing flights), CO2 per seat-km, first tax year; same specification as Table 2
* =====================================================================================
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo c_all
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo c_wt
reghdfe ln_co2 tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo c_size
reghdfe ln_co2 tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo c_size_wt
reghdfe ln_co2 dose_post bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo c_dose
reghdfe ln_int tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo i_all
reghdfe ln_int tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo i_wt
reghdfe ln_int tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo i_size
esttab c_all c_wt c_size c_size_wt c_dose i_all i_wt i_size using "T4_co2.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large dose_post) stats(N N_clust, labels("Observations" "Countries")) title("Table 4 CO2 and intensity")
esttab c_all c_wt c_size c_size_wt c_dose i_all i_wt i_size, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large dose_post) stats(N N_clust)

* =====================================================================================
* Table 5 / Appendix A1  Event-time coefficients, monthly: pre [A-36,A-25], [A-24,A-13], reference [A-12,A-1], post year 1, year 2
* =====================================================================================
reghdfe ln_seats T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2 lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo es_seats
reghdfe ln_co2 T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2 lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo es_co2
reghdfe ln_int T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2 lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo es_int
esttab es_seats es_co2 es_int using "T5_eventtime_month.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_pre36_25 T_pre24_13 T_post1 T_post2 B_post1) stats(N N_clust, labels("Observations" "Countries")) title("Event time, monthly outcomes")
esttab es_seats es_co2 es_int, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_pre36_25 T_pre24_13 T_post1 T_post2 B_post1) stats(N N_clust)

* =====================================================================================
* Appendix A2  Robustness of the seat and CO2 effects
*   (i) never-taxed European controls only; (ii) all coded countries as controls with region x month x event FE; (iii) drop recession-year events (IRL 2009)
*   (iv) effective-date windows +-12 .. +-36 (stack_eff.dta, 9 events incl. NLD)
* =====================================================================================
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & (treat == 1 | border == 1 | ctrl_never == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo r_never_s
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & (treat == 1 | border == 1 | ctrl_never == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo r_never_c
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo r_world_s
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo r_world_c
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & stk != 1, absorb(fe_u fe_t) vce(cluster iso3n)
eststo r_noirl_s
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & stk != 1, absorb(fe_u fe_t) vce(cluster iso3n)
eststo r_noirl_c
esttab r_never_s r_never_c r_world_s r_world_c r_noirl_s r_noirl_c using "A2_robust_controls.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust, labels("Observations" "Countries")) title("Robustness: control groups and events")
esttab r_never_s r_never_c r_world_s r_world_c r_noirl_s r_noirl_c, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust)

use "stack_eff.dta", clear
gen tp = treat * post
gen bp = border * post
reghdfe ln_seats tp bp lngdp lnpop if relE >= -12 & relE <= 11, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w12_s
reghdfe ln_seats tp bp lngdp lnpop if relE >= -18 & relE <= 17, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w18_s
reghdfe ln_seats tp bp lngdp lnpop if relE >= -24 & relE <= 23, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w24_s
reghdfe ln_seats tp bp lngdp lnpop if relE >= -36 & relE <= 35, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w36_s
reghdfe ln_co2 tp bp lngdp lnpop if relE >= -12 & relE <= 11, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w12_c
reghdfe ln_co2 tp bp lngdp lnpop if relE >= -18 & relE <= 17, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w18_c
reghdfe ln_co2 tp bp lngdp lnpop if relE >= -24 & relE <= 23, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w24_c
reghdfe ln_co2 tp bp lngdp lnpop if relE >= -36 & relE <= 35, absorb(fe_u fe_t) vce(cluster iso3n)
eststo w36_c
esttab w12_s w18_s w24_s w36_s w12_c w18_c w24_c w36_c using "A2_robust_windows.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust, labels("Observations" "Countries")) title("Robustness: effective-date windows")
esttab w12_s w18_s w24_s w36_s w12_c w18_c w24_c w36_c, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust)

* =====================================================================================
* Table 3  Network position, annual: ln GACI, destinations, eigenvector, betweenness; years E-3..E (first effective year)
* FE: airport x event (fe_u), year x event (fe_t). Controls: country ln GDP, ln population
* =====================================================================================
use "stack_year.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen tp = treat * post1
gen bp = border * post1
gen tp_small = sz_small * post1
gen tp_mid = sz_mid * post1
gen tp_large = sz_large * post1
gen hub = (w0 >= 1000000)
gen T_km3 = treat * (k == -3)
gen T_km2 = treat * (k == -2)
gen T_k0 = treat * (k == 0)
gen T_k1 = treat * (k == 1)
gen B_km3 = border * (k == -3)
gen B_km2 = border * (k == -2)
gen B_k0 = border * (k == 0)
gen B_k1 = border * (k == 1)
gen dose_post = dose * post1
reghdfe ln_gaci tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_g_all
reghdfe ln_gaci tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_g_wt
reghdfe ln_gaci tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & (hub == 1 | treat == 0), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_g_hub
reghdfe ln_gaci tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_g_size
reghdfe ln_deg tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_d_all
reghdfe ln_deg tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_d_wt
reghdfe ln_deg tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & (hub == 1 | treat == 0), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_d_hub
reghdfe ln_deg tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_d_size
reghdfe ln_eigen tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_e_all
reghdfe ln_eigen tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_e_wt
reghdfe ln_eigen tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & (hub == 1 | treat == 0), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_e_hub
reghdfe ln_eigen tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_e_size
reghdfe ln_betw tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_b_all
reghdfe ln_betw tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_b_wt
reghdfe ln_betw tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & (hub == 1 | treat == 0), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_b_hub
reghdfe ln_betw tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo n_b_size
esttab n_g_all n_g_wt n_g_hub n_g_size n_d_all n_d_wt n_d_hub n_d_size using "T3_network_gaci_deg.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large) stats(N N_clust, labels("Observations" "Countries")) title("Table 3 Network position: GACI and destinations")
esttab n_g_all n_g_wt n_g_hub n_g_size n_d_all n_d_wt n_d_hub n_d_size, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large) stats(N N_clust)
esttab n_e_all n_e_wt n_e_hub n_e_size n_b_all n_b_wt n_b_hub n_b_size using "T3_network_eigen_betw.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large) stats(N N_clust, labels("Observations" "Countries")) title("Table 3 Network position: eigenvector and betweenness")
esttab n_e_all n_e_wt n_e_hub n_e_size n_b_all n_b_wt n_b_hub n_b_size, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp tp_small tp_mid tp_large) stats(N N_clust)

* Table 5 Panel B  Event time, annual GACI: k = -3, -2 (reference -1), 0, +1
reghdfe ln_gaci T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1 lngdp lnpop if eur == 1 & stk != 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo es_gaci
reghdfe ln_deg T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1 lngdp lnpop if eur == 1 & stk != 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo es_deg
esttab es_gaci es_deg using "T5_eventtime_year.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_km3 T_km2 T_k0 T_k1) stats(N N_clust, labels("Observations" "Countries")) title("Event time, annual GACI and destinations")
esttab es_gaci es_deg, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_km3 T_km2 T_k0 T_k1) stats(N N_clust)

* =====================================================================================
* Table 7  Mechanism. Panel A: exact decomposition ln CO2 = ln destinations + ln(flights per destination) + ln(CO2 per flight)
* (coefficients add up); per-flight CO2 = gauge x stage x intensity. Annual stacks, years E-3..E
* =====================================================================================
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_co2_all
reghdfe ln_co2 tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_co2_size
reghdfe ln_deg tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_deg_all
reghdfe ln_deg tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_deg_size
reghdfe ln_fl_per_dest tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_fpd_all
reghdfe ln_fl_per_dest tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_fpd_size
reghdfe ln_co2_per_fl tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_cpf_all
reghdfe ln_co2_per_fl tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_cpf_size
reghdfe ln_gauge tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_gau_all
reghdfe ln_gauge tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_gau_size
reghdfe ln_stage tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_stg_all
reghdfe ln_stage tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_stg_size
reghdfe ln_int tp bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_int_all
reghdfe ln_int tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo m_int_size
esttab m_co2_all m_deg_all m_fpd_all m_cpf_all m_gau_all m_stg_all m_int_all using "T7_decomposition_all.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust, labels("Observations" "Countries")) title("Table 7A Decomposition, all treated")
esttab m_co2_all m_deg_all m_fpd_all m_cpf_all m_gau_all m_stg_all m_int_all, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp bp) stats(N N_clust)
esttab m_co2_size m_deg_size m_fpd_size m_cpf_size m_gau_size m_stg_size m_int_size using "T7_decomposition_size.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp_small tp_mid tp_large bp) stats(N N_clust, labels("Observations" "Countries")) title("Table 7A Decomposition, by size")
esttab m_co2_size m_deg_size m_fpd_size m_cpf_size m_gau_size m_stg_size m_int_size, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp_small tp_mid tp_large bp) stats(N N_clust)

* Table 8  Gelbach decomposition: CO2 effect with and without the network variables as controls (descriptive channel share)
reghdfe ln_co2 tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo gel_0
reghdfe ln_co2 tp_small tp_mid tp_large bp ln_deg lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo gel_deg
reghdfe ln_co2 tp_small tp_mid tp_large bp ln_gaci lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo gel_gaci
reghdfe ln_co2 tp_small tp_mid tp_large bp ln_deg ln_gaci lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo gel_both
reghdfe ln_int tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo geli_0
reghdfe ln_int tp_small tp_mid tp_large bp ln_gaci lngdp lnpop if eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
eststo geli_gaci
esttab gel_0 gel_deg gel_gaci gel_both geli_0 geli_gaci using "T8_gelbach.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp_small tp_mid tp_large ln_deg ln_gaci) stats(N N_clust, labels("Observations" "Countries")) title("Table 8 Gelbach: CO2 with network controls")
esttab gel_0 gel_deg gel_gaci gel_both geli_0 geli_gaci, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp_small tp_mid tp_large ln_deg ln_gaci) stats(N N_clust)

* Within-airport elasticities of CO2 outcomes to ln GACI, all stack airport-years (descriptive)
reghdfe ln_co2 ln_gaci lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
eststo el_co2
reghdfe ln_int ln_gaci lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
eststo el_int
reghdfe ln_deg ln_gaci lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
eststo el_deg
reghdfe ln_gauge ln_gaci lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
eststo el_gau
reghdfe ln_stage ln_gaci lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
eststo el_stg
esttab el_co2 el_int el_deg el_gau el_stg using "T8_elasticities.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(ln_gaci) stats(N N_clust, labels("Observations" "Countries")) title("Table 8A Elasticities to ln GACI")
esttab el_co2 el_int el_deg el_gau el_stg, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(ln_gaci) stats(N N_clust)

* =====================================================================================
* Table 7 Panel B  Monthly margins: flights, seats per flight (stack_month) and service loss (stack_loss)
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen tp = treat * post1
gen bp = border * post1
gen tp_small = sz_small * post1
gen tp_mid = sz_mid * post1
gen tp_large = sz_large * post1
reghdfe ln_fl tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo mm_fl
reghdfe ln_gauge tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
eststo mm_gau
use "stack_loss.dta", clear
gen tp = treat * post1
gen bp = border * post1
gen tp_small = sz_small * post1
gen tp_mid = sz_mid * post1
gen tp_large = sz_large * post1
reghdfe loss tp_small tp_mid tp_large bp lngdp lnpop, absorb(fe_u fe_t) vce(cluster iso3n)
eststo mm_loss
esttab mm_fl mm_gau mm_loss using "T7_margins.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp_small tp_mid tp_large bp) stats(N N_clust, labels("Observations" "Countries")) title("Table 7B Monthly margins")
esttab mm_fl mm_gau mm_loss, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp_small tp_mid tp_large bp) stats(N N_clust)

* =====================================================================================
* Table 9  Global: all 19 events (11 outside Europe at effective date, no donut), region x month x event FE
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen tp = treat * post1
gen bp = border * post1
gen T_pre36_25 = treat * pre36_25
gen T_pre24_13 = treat * pre24_13
gen T_post1 = treat * post1
gen B_pre36_25 = border * pre36_25
gen B_pre24_13 = border * pre24_13
gen B_post1 = border * post1
reghdfe ln_seats T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1 lngdp lnpop if stk != 0 & donut == 0 & post2 == 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_all_s
reghdfe ln_seats T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1 lngdp lnpop if stk != 0 & donut == 0 & post2 == 0 & eur == 1, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_eur_s
reghdfe ln_seats T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1 lngdp lnpop if stk != 0 & donut == 0 & post2 == 0 & eur == 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_row_s
reghdfe ln_co2 T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1 lngdp lnpop if stk != 0 & donut == 0 & post2 == 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_all_c
reghdfe ln_co2 T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1 lngdp lnpop if stk != 0 & donut == 0 & post2 == 0 & eur == 1, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_eur_c
reghdfe ln_co2 T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1 lngdp lnpop if stk != 0 & donut == 0 & post2 == 0 & eur == 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_row_c
esttab g_all_s g_eur_s g_row_s g_all_c g_eur_c g_row_c using "T9_global_month.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_pre36_25 T_pre24_13 T_post1 B_post1) stats(N N_clust, labels("Observations" "Countries")) title("Table 9 Global events, monthly")
esttab g_all_s g_eur_s g_row_s g_all_c g_eur_c g_row_c, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_pre36_25 T_pre24_13 T_post1 B_post1) stats(N N_clust)
use "stack_year.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen T_km3 = treat * (k == -3)
gen T_km2 = treat * (k == -2)
gen T_k0 = treat * (k == 0)
gen T_k1 = treat * (k == 1)
gen B_km3 = border * (k == -3)
gen B_km2 = border * (k == -2)
gen B_k0 = border * (k == 0)
gen B_k1 = border * (k == 1)
reghdfe ln_gaci T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1 lngdp lnpop if stk != 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_all_g
reghdfe ln_gaci T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1 lngdp lnpop if stk != 0 & eur == 1, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_eur_g
reghdfe ln_gaci T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1 lngdp lnpop if stk != 0 & eur == 0, absorb(fe_u fe_rt) vce(cluster iso3n)
eststo g_row_g
esttab g_all_g g_eur_g g_row_g using "T9_global_gaci.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_km3 T_km2 T_k0 T_k1) stats(N N_clust, labels("Observations" "Countries")) title("Table 9 Global events, GACI")
esttab g_all_g g_eur_g g_row_g, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(T_km3 T_km2 T_k0 T_k1) stats(N N_clust)
log close
