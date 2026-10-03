* 04_regional_benefits.do  Regional cost of the connectivity loss and benefit / cost accounting, rewritten 2026-10-03
* Companion to 01_main.do (same 8 European events, same stacks). Data prepared by 122_build_regional.py:
*   nat_month.dta  country x month x event: Eurostat nights (tour_occ_nim, dom / for / total), treated and control countries
*   reg_month.dta  NUTS2 x month x event: catchment seats and CO2 (airports within 100 km, weight exp(-d/50 km)), exposure
*   reg_year.dta   NUTS2 x year x event (E-3..E+1): Eurostat nights (tour_occ_nin2, annual), employment (lfst_r_lfe2en2,
*                  NACE G-I = trade, transport, accommodation and food; "I" alone is not published), GDP per head
*                  (nama_10r_2gdp), catchment GACI and destinations, exposure
*   bc_inputs.dta  event: treated-airport CO2 (tonnes) and seats in the first tax year, seat-weighted dose, revenue base
* Exposure = share of the region's catchment seats (pre-year, distance-weighted) at small airports, where small means
*   below the treated country's lower tercile of pre-year seats; defined for treated AND control regions.
* Design: region x calendar month x event FE and country x month x event FE (annual: region x event, country x year x event),
*   so the national demand effect of the tax is absorbed; identifying variation = exposure x post inside the treated country;
*   control-country regions carry the same exposure x post term (triple difference). Border-ring regions dropped.
* Every regression includes lngdp lnpop (collinear with the country x time FE and dropped by reghdfe; kept for uniformity).
* Fully inline: no programs, loops, locals. Scalars appear only inside block 7, which recomputes what it needs.
* Eurostat NUTS2 monthly nights do not exist, so the monthly nights block is national (block N); regional nights are annual.
* Parameters (block 7): load factor 0.80, carbon value 100 and 200 EUR/t, spending per foreign night 120 EUR.
clear all
set more off
set linesize 200
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper"
cap log close
log using "04_regional_benefits_run.log", replace text
cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which esttab
if _rc ssc install estout
cap which ivreghdfe
if _rc ssc install ivreghdfe
cap which ivreg2
if _rc ssc install ivreg2
cap which ranktest
if _rc ssc install ranktest
estimates clear

* =====================================================================================
* N. National monthly nights (Eurostat tour_occ_nim): treated country vs control countries, same calendar as Table 2
*    FE: country x calendar month x event (fe_cm), month x event (fe_t). SE clustered by country.
* =====================================================================================
use "nat_month.dta", clear
gen tp = treat_c * post1
gen T_pre36_25 = treat_c * pre36_25
gen T_pre24_13 = treat_c * pre24_13
gen T_post1 = treat_c * post1
gen T_post2 = treat_c * post2
reghdfe ln_nights_for tp lngdp lnpop if stk != 0 & donut == 0 & post2 == 0, absorb(fe_cm fe_t) vce(cluster iso3n)
eststo N1_for
reghdfe ln_nights_dom tp lngdp lnpop if stk != 0 & donut == 0 & post2 == 0, absorb(fe_cm fe_t) vce(cluster iso3n)
eststo N2_dom
reghdfe ln_nights_tot tp lngdp lnpop if stk != 0 & donut == 0 & post2 == 0, absorb(fe_cm fe_t) vce(cluster iso3n)
eststo N3_tot
reghdfe ln_nights_for T_pre36_25 T_pre24_13 T_post1 T_post2 lngdp lnpop if stk != 0 & donut == 0, absorb(fe_cm fe_t) vce(cluster iso3n)
eststo N4_es_for
reghdfe ln_nights_dom T_pre36_25 T_pre24_13 T_post1 T_post2 lngdp lnpop if stk != 0 & donut == 0, absorb(fe_cm fe_t) vce(cluster iso3n)
eststo N5_es_dom
reghdfe ln_nights_tot T_pre36_25 T_pre24_13 T_post1 T_post2 lngdp lnpop if stk != 0 & donut == 0, absorb(fe_cm fe_t) vce(cluster iso3n)
eststo N6_es_tot
esttab N1_for N2_dom N3_tot N4_es_for N5_es_dom N6_es_tot using "R0_national_nights.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp T_pre36_25 T_pre24_13 T_post1 T_post2) stats(N N_clust, labels("Observations" "Countries")) title("National nights at tourist accommodation (Eurostat, monthly): treated vs control countries")
esttab N1_for N2_dom N3_tot N4_es_for N5_es_dom N6_es_tot, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tp T_pre36_25 T_pre24_13 T_post1 T_post2) stats(N N_clust)

* =====================================================================================
* R1. Regional connectivity loss (monthly): catchment seats and CO2 on small-airport exposure x post, within treated country
*     FE: region x calendar month x event (fe_r), country x month x event (fe_ct). SE clustered by region.
* =====================================================================================
use "reg_month.dta", clear
gen tpx = treat_c * post1 * expo_small
gen cpx = (1 - treat_c) * post1 * expo_small
gen TX_pre36_25 = treat_c * pre36_25 * expo_small
gen TX_pre24_13 = treat_c * pre24_13 * expo_small
gen TX_post1 = treat_c * post1 * expo_small
gen TX_post2 = treat_c * post2 * expo_small
gen CX_pre36_25 = (1 - treat_c) * pre36_25 * expo_small
gen CX_pre24_13 = (1 - treat_c) * pre24_13 * expo_small
gen CX_post1 = (1 - treat_c) * post1 * expo_small
gen CX_post2 = (1 - treat_c) * post2 * expo_small
reghdfe ln_conn_seats tpx cpx lngdp lnpop if stk != 0 & donut == 0 & post2 == 0 & border_r == 0, absorb(fe_r fe_ct) vce(cluster nuts2n)
eststo M1_seats
reghdfe ln_conn_co2 tpx cpx lngdp lnpop if stk != 0 & donut == 0 & post2 == 0 & border_r == 0, absorb(fe_r fe_ct) vce(cluster nuts2n)
eststo M2_co2
reghdfe ln_conn_seats tpx cpx lngdp lnpop if stk != 0 & donut == 0 & post2 == 0 & border_r == 0 [aw = catch_seats], absorb(fe_r fe_ct) vce(cluster nuts2n)
eststo M3_seats_wt
reghdfe ln_conn_seats TX_pre36_25 TX_pre24_13 TX_post1 TX_post2 CX_pre36_25 CX_pre24_13 CX_post1 CX_post2 lngdp lnpop if stk != 0 & donut == 0 & border_r == 0, absorb(fe_r fe_ct) vce(cluster nuts2n)
eststo M4_es_seats
reghdfe ln_conn_co2 TX_pre36_25 TX_pre24_13 TX_post1 TX_post2 CX_pre36_25 CX_pre24_13 CX_post1 CX_post2 lngdp lnpop if stk != 0 & donut == 0 & border_r == 0, absorb(fe_r fe_ct) vce(cluster nuts2n)
eststo M5_es_co2
esttab M1_seats M2_co2 M3_seats_wt M4_es_seats M5_es_co2 using "R1_regional_connectivity.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx TX_pre36_25 TX_pre24_13 TX_post1 TX_post2 CX_post1) stats(N N_clust, labels("Observations" "Regions")) title("Regional connectivity (catchment seats, CO2): small-airport exposure x post, treated-country regions vs control-country regions")
esttab M1_seats M2_co2 M3_seats_wt M4_es_seats M5_es_co2, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx TX_pre36_25 TX_pre24_13 TX_post1 TX_post2 CX_post1) stats(N N_clust)

* =====================================================================================
* R2. Annual regional outcomes, years E-3..E: nights (for, dom, total), employment (G-I, total), GDP per head, catchment GACI
*     FE: region x event (fe_ry), country x year x event (fe_cy). SE clustered by region.
* =====================================================================================
use "reg_year.dta", clear
gen tpx = treat_c * post1 * expo_small
gen cpx = (1 - treat_c) * post1 * expo_small
gen TX_km3 = treat_c * (k == -3) * expo_small
gen TX_km2 = treat_c * (k == -2) * expo_small
gen TX_k0 = treat_c * (k == 0) * expo_small
gen TX_k1 = treat_c * (k == 1) * expo_small
gen CX_km3 = (1 - treat_c) * (k == -3) * expo_small
gen CX_km2 = (1 - treat_c) * (k == -2) * expo_small
gen CX_k0 = (1 - treat_c) * (k == 0) * expo_small
gen CX_k1 = (1 - treat_c) * (k == 1) * expo_small
reghdfe ln_nights_for tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y1_for
reghdfe ln_nights_dom tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y2_dom
reghdfe ln_nights_tot tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y3_tot
reghdfe ln_emp_GI tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y4_empGI
reghdfe ln_emp_tot tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y5_emptot
reghdfe ln_gdp_pc tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y6_gdp
reghdfe ln_conn_gaci tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y7_gaci
reghdfe ln_conn_deg tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo Y8_deg
esttab Y7_gaci Y8_deg Y1_for Y2_dom Y3_tot Y4_empGI Y5_emptot Y6_gdp using "R2_regional_annual.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx) stats(N N_clust, labels("Observations" "Regions")) title("Annual regional outcomes, years E-3..E: small-airport exposure x post (treated) and the same term in control countries")
esttab Y7_gaci Y8_deg Y1_for Y2_dom Y3_tot Y4_empGI Y5_emptot Y6_gdp, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx) stats(N N_clust)
* event time, k = -3, -2 (reference -1), 0, +1
reghdfe ln_conn_gaci TX_km3 TX_km2 TX_k0 TX_k1 CX_km3 CX_km2 CX_k0 CX_k1 lngdp lnpop if stk != 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo E1_gaci
reghdfe ln_nights_for TX_km3 TX_km2 TX_k0 TX_k1 CX_km3 CX_km2 CX_k0 CX_k1 lngdp lnpop if stk != 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo E2_for
reghdfe ln_nights_dom TX_km3 TX_km2 TX_k0 TX_k1 CX_km3 CX_km2 CX_k0 CX_k1 lngdp lnpop if stk != 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo E3_dom
reghdfe ln_emp_GI TX_km3 TX_km2 TX_k0 TX_k1 CX_km3 CX_km2 CX_k0 CX_k1 lngdp lnpop if stk != 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo E4_empGI
esttab E1_gaci E2_for E3_dom E4_empGI using "R3_regional_eventtime.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(TX_km3 TX_km2 TX_k0 TX_k1 CX_k0 CX_k1) stats(N N_clust, labels("Observations" "Regions")) title("Annual regional event time: exposure x k, treated country (TX) and control countries (CX)")
esttab E1_gaci E2_for E3_dom E4_empGI, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(TX_km3 TX_km2 TX_k0 TX_k1 CX_k0 CX_k1) stats(N N_clust)

* =====================================================================================
* R4. 2SLS: regional outcomes on catchment GACI (or destinations), instrumented by exposure x post in the treated country
* =====================================================================================
use "reg_year.dta", clear
gen tpx = treat_c * post1 * expo_small
gen cpx = (1 - treat_c) * post1 * expo_small
ivreghdfe ln_nights_for cpx lngdp lnpop (ln_conn_gaci = tpx) if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) cluster(nuts2n) first
eststo G1_for_gaci
ivreghdfe ln_nights_dom cpx lngdp lnpop (ln_conn_gaci = tpx) if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) cluster(nuts2n)
eststo G2_dom_gaci
ivreghdfe ln_emp_GI cpx lngdp lnpop (ln_conn_gaci = tpx) if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) cluster(nuts2n)
eststo G3_emp_gaci
ivreghdfe ln_nights_for cpx lngdp lnpop (ln_conn_deg = tpx) if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) cluster(nuts2n) first
eststo G4_for_deg
ivreghdfe ln_emp_GI cpx lngdp lnpop (ln_conn_deg = tpx) if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) cluster(nuts2n)
eststo G5_emp_deg
esttab G1_for_gaci G2_dom_gaci G3_emp_gaci G4_for_deg G5_emp_deg using "R4_regional_iv.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(ln_conn_gaci ln_conn_deg cpx) stats(N N_clust widstat, labels("Observations" "Regions" "KP F")) title("2SLS: regional nights and hospitality employment on catchment GACI / destinations, instrument = exposure x post (treated country)")
esttab G1_for_gaci G2_dom_gaci G3_emp_gaci G4_for_deg G5_emp_deg, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(ln_conn_gaci ln_conn_deg cpx) stats(N N_clust widstat)

* =====================================================================================
* R5. Predicted seat loss as the exposure measure: pred_loss = -(expo_small b_small + expo_mid b_mid + expo_large b_large)
*     with the Table 2 size-tercile coefficients (recomputed here so the block runs alone)
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen bp = border * post1
gen tp_small = sz_small * post1
gen tp_mid = sz_mid * post1
gen tp_large = sz_large * post1
reghdfe ln_seats tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_small = _b[tp_small]
scalar b_mid = _b[tp_mid]
scalar b_large = _b[tp_large]
use "reg_year.dta", clear
gen pred_loss = -(expo_small * b_small + expo_mid * b_mid + expo_large * b_large)
gen tpl = treat_c * post1 * pred_loss
gen cpl = (1 - treat_c) * post1 * pred_loss
reghdfe ln_conn_gaci tpl cpl lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo P1_gaci
reghdfe ln_nights_for tpl cpl lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo P2_for
reghdfe ln_nights_dom tpl cpl lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo P3_dom
reghdfe ln_emp_GI tpl cpl lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo P4_empGI
reghdfe ln_gdp_pc tpl cpl lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
eststo P5_gdp
esttab P1_gaci P2_for P3_dom P4_empGI P5_gdp using "R5_regional_predloss.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpl cpl) stats(N N_clust, labels("Observations" "Regions")) title("Annual regional outcomes on predicted first-year seat loss x post (log points, from Table 2 size coefficients)")
esttab P1_gaci P2_for P3_dom P4_empGI P5_gdp, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpl cpl) stats(N N_clust)

* =====================================================================================
* 7. Benefit / cost accounting, first tax year, by event and total (EUR; tonnes CO2)
*    counterfactual = observed / exp(beta); abatement = observed x (exp(-beta) - 1)
*    Inputs recomputed in this block: seat-weighted seats and CO2 effects (Table 2 col 2, Table 4 col 2), unweighted CO2
*    (Table 4 col 1), national foreign-nights effect (block N), regional hospitality-employment exposure effect (block R2)
*    Parameters: load factor 0.80, carbon value 100 and 200 EUR/t, spending per foreign night 120 EUR
* =====================================================================================
use "stack_month.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen tp = treat * post1
gen bp = border * post1
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_seats_w = _b[tp]
scalar se_seats_w = _se[tp]
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_co2_w = _b[tp]
scalar se_co2_w = _se[tp]
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & post2 == 0 & (treat == 1 | border == 1 | ctrl_eur == 1), absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_co2_u = _b[tp]
scalar se_co2_u = _se[tp]
use "nat_month.dta", clear
gen tp = treat_c * post1
reghdfe ln_nights_for tp lngdp lnpop if stk != 0 & donut == 0 & post2 == 0, absorb(fe_cm fe_t) vce(cluster iso3n)
scalar b_for = _b[tp]
scalar se_for = _se[tp]
keep if stk != 0 & treat_c == 1 & post1 == 1 & donut == 0
collapse (sum) nights_for_post = nights_for, by(stk)
gen double nights_lost = nights_for_post * (exp(-b_for) - 1)
gen double nights_lost_hi = nights_for_post * (exp(-(b_for - 1.96 * se_for)) - 1)
gen double nights_lost_lo = nights_for_post * (exp(-(b_for + 1.96 * se_for)) - 1)
save "bc_tour.dta", replace
use "reg_year.dta", clear
gen tpx = treat_c * post1 * expo_small
gen cpx = (1 - treat_c) * post1 * expo_small
reghdfe ln_emp_GI tpx cpx lngdp lnpop if stk != 0 & k <= 0 & border_r == 0, absorb(fe_ry fe_cy) vce(cluster nuts2n)
scalar b_emp = _b[tpx]
scalar se_emp = _se[tpx]
keep if stk != 0 & treat_c == 1 & k == 0 & border_r == 0
gen double jobs_lost = emp_GI * 1000 * (exp(-b_emp * expo_small) - 1)
collapse (sum) jobs_lost emp_GI_post = emp_GI, by(stk)
replace emp_GI_post = emp_GI_post * 1000
save "bc_jobs.dta", replace
use "bc_inputs.dta", clear
keep if stk != 0
merge 1:1 stk using "bc_tour.dta", nogen
merge 1:1 stk using "bc_jobs.dta", nogen
gen double t_abated = co2_post_t * (exp(-b_co2_w) - 1)
gen double t_abated_hi = co2_post_t * (exp(-(b_co2_w - 1.96 * se_co2_w)) - 1)
gen double t_abated_lo = co2_post_t * (exp(-(b_co2_w + 1.96 * se_co2_w)) - 1)
gen double t_abated_unw = co2_post_t * (exp(-b_co2_u) - 1)
gen double pax_post = seats_post * 0.80
gen double pax_lost = pax_post * (exp(-b_seats_w) - 1)
gen double revenue = rev_base * 0.80
gen double dwl = 0.5 * dose_w * pax_lost
gen double carbon_val_100 = t_abated * 100
gen double carbon_val_200 = t_abated * 200
gen double tourism_loss = nights_lost * 120
gen double tourism_loss_hi = nights_lost_hi * 120
gen double cost_total = dwl + tourism_loss
gen double cost_per_t = cost_total / t_abated
gen double cost_per_t_unw = cost_total / t_abated_unw
gen double revenue_per_t = revenue / t_abated
gen double net_100 = carbon_val_100 - cost_total
gen double net_200 = carbon_val_200 - cost_total
preserve
collapse (sum) co2_post_t seats_post t_abated t_abated_hi t_abated_lo t_abated_unw pax_post pax_lost revenue dwl carbon_val_100 carbon_val_200 nights_for_post nights_lost nights_lost_hi tourism_loss tourism_loss_hi cost_total net_100 net_200 jobs_lost emp_GI_post
gen iso3 = "ALL"
gen stk = 99
gen double cost_per_t = cost_total / t_abated
gen double cost_per_t_unw = cost_total / t_abated_unw
gen double revenue_per_t = revenue / t_abated
save "bc_total.dta", replace
restore
append using "bc_total.dta"
order stk iso3 eff dose_w n_airports co2_post_t t_abated t_abated_lo t_abated_hi t_abated_unw seats_post pax_post pax_lost revenue dwl nights_for_post nights_lost nights_lost_hi tourism_loss tourism_loss_hi cost_total cost_per_t cost_per_t_unw revenue_per_t carbon_val_100 carbon_val_200 net_100 net_200 emp_GI_post jobs_lost
format co2_post_t t_abated* seats_post pax_post pax_lost revenue dwl nights_for_post nights_lost* tourism_loss* cost_total carbon_val_* net_* emp_GI_post jobs_lost %15.0fc
format cost_per_t* revenue_per_t %9.1fc
save "benefits_by_event.dta", replace
export delimited using "benefits_by_event.csv", replace
di _n "==== Benefit / cost, first tax year (EUR; tonnes CO2); seat-weighted CO2 and seats effects ===="
list stk iso3 dose_w t_abated t_abated_hi t_abated_unw revenue dwl nights_lost tourism_loss jobs_lost cost_per_t revenue_per_t net_100, noobs abbrev(14)
di _n "Parameters: load factor 0.80, carbon value 100 EUR/t (200 in net_200), spending per foreign night 120 EUR, CO2 in tonnes (kg / 1000)"
di "Coefficients: seats weighted " b_seats_w " (se " se_seats_w "), CO2 weighted " b_co2_w " (se " se_co2_w "), CO2 unweighted " b_co2_u " (se " se_co2_u ")"
di "              national foreign nights " b_for " (se " se_for "), regional G-I employment x exposure " b_emp " (se " se_emp ")"
log close
