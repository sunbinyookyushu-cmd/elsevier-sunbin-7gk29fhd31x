# -*- coding: utf-8 -*-
"""Write the two Stata do-files for the ticket-tax paper (user 2026-10-03). Every regression is written out in full:
no loops, no macros, no locals, one command per line, so any block can be selected and run on its own. Every
regression includes the country controls lngdp and lnpop (country-year). CRLF line endings; no block comments.
  stata_paper/01_main.do              Tables 2-5, 7-9: seats, CO2, network position, event time, robustness, mechanism, Gelbach, global
  stata_paper/02_events_mediation.do  Table 6 (SDID by event), HonestDiD, IV mediation
Data from 120_export_stata_all.py. Outputs: rtf tables and logs in stata_paper/.
"""
import os

OUT = "stata_paper"
os.makedirs(OUT, exist_ok=True)
CD = r'cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper"'
HEAD = """clear all
set more off
set linesize 200
{cd}
cap log close
log using "{log}", replace text
cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which esttab
if _rc ssc install estout
estimates clear
"""
MAIN = "eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1)"                 # 8 European events, Netherlands separate, anticipation months dropped
Y1 = MAIN + " & post2 == 0"                             # first post year only
C = "lngdp lnpop"
R = lambda y, x, cond, name, w="", fe="fe_u fe_t": f"reghdfe {y} {x} {C}{w}, absorb({fe}) vce(cluster iso3n)\neststo {name}\n" if not cond else f"reghdfe {y} {x} {C} if {cond}{w}, absorb({fe}) vce(cluster iso3n)\neststo {name}\n"
ESTTAB = lambda models, file, title, keep: f'esttab {models} using "{file}", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep({keep}) stats(N N_clust, labels("Observations" "Countries")) title("{title}")\nesttab {models}, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep({keep}) stats(N N_clust)\n'

d1 = HEAD.format(cd=CD, log="01_main_run.log")
d1 += """
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
"""
d1 += R("ln_seats", "tp bp", Y1, "s_all")
d1 += R("ln_seats", "tp bp", Y1 + " & w0 > 0", "s_wt", w=" [aw = w0]")
d1 += R("ln_seats", "tp_small tp_mid tp_large bp", Y1, "s_size")
d1 += R("ln_seats", "tp_small tp_mid tp_large bp", Y1 + " & w0 > 0", "s_size_wt", w=" [aw = w0]")
d1 += R("ln_seats", "dose_post bp", Y1, "s_dose")
d1 += R("ln_seats", "tp dose_post bp", Y1, "s_dose2")
d1 += ESTTAB("s_all s_wt s_size s_size_wt s_dose s_dose2", "T2_seats.rtf", "Table 2 Seats", "tp bp tp_small tp_mid tp_large dose_post")
d1 += """
* =====================================================================================
* Table 4  CO2 (departing flights), CO2 per seat-km, first tax year; same specification as Table 2
* =====================================================================================
"""
d1 += R("ln_co2", "tp bp", Y1, "c_all")
d1 += R("ln_co2", "tp bp", Y1 + " & w0 > 0", "c_wt", w=" [aw = w0]")
d1 += R("ln_co2", "tp_small tp_mid tp_large bp", Y1, "c_size")
d1 += R("ln_co2", "tp_small tp_mid tp_large bp", Y1 + " & w0 > 0", "c_size_wt", w=" [aw = w0]")
d1 += R("ln_co2", "dose_post bp", Y1, "c_dose")
d1 += R("ln_int", "tp bp", Y1, "i_all")
d1 += R("ln_int", "tp bp", Y1 + " & w0 > 0", "i_wt", w=" [aw = w0]")
d1 += R("ln_int", "tp_small tp_mid tp_large bp", Y1, "i_size")
d1 += ESTTAB("c_all c_wt c_size c_size_wt c_dose i_all i_wt i_size", "T4_co2.rtf", "Table 4 CO2 and intensity", "tp bp tp_small tp_mid tp_large dose_post")
d1 += """
* =====================================================================================
* Table 5 / Appendix A1  Event-time coefficients, monthly: pre [A-36,A-25], [A-24,A-13], reference [A-12,A-1], post year 1, year 2
* =====================================================================================
"""
d1 += R("ln_seats", "T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2", MAIN, "es_seats")
d1 += R("ln_co2", "T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2", MAIN, "es_co2")
d1 += R("ln_int", "T_pre36_25 T_pre24_13 T_post1 T_post2 B_pre36_25 B_pre24_13 B_post1 B_post2", MAIN, "es_int")
d1 += ESTTAB("es_seats es_co2 es_int", "T5_eventtime_month.rtf", "Event time, monthly outcomes", "T_pre36_25 T_pre24_13 T_post1 T_post2 B_post1")
d1 += """
* =====================================================================================
* Appendix A2  Robustness of the seat and CO2 effects
*   (i) never-taxed European controls only; (ii) all coded countries as controls with region x month x event FE; (iii) drop recession-year events (IRL 2009)
*   (iv) effective-date windows +-12 .. +-36 (stack_eff.dta, 9 events incl. NLD)
* =====================================================================================
"""
d1 += R("ln_seats", "tp bp", Y1 + " & (treat == 1 | border == 1 | ctrl_never == 1)", "r_never_s")
d1 += R("ln_co2", "tp bp", Y1 + " & (treat == 1 | border == 1 | ctrl_never == 1)", "r_never_c")
d1 += R("ln_seats", "tp bp", "eur == 1 & stk != 0 & donut == 0 & post2 == 0", "r_world_s", fe="fe_u fe_rt")
d1 += R("ln_co2", "tp bp", "eur == 1 & stk != 0 & donut == 0 & post2 == 0", "r_world_c", fe="fe_u fe_rt")
d1 += R("ln_seats", "tp bp", Y1 + " & stk != 1", "r_noirl_s")
d1 += R("ln_co2", "tp bp", Y1 + " & stk != 1", "r_noirl_c")
d1 += ESTTAB("r_never_s r_never_c r_world_s r_world_c r_noirl_s r_noirl_c", "A2_robust_controls.rtf", "Robustness: control groups and events", "tp bp")
d1 += """
use "stack_eff.dta", clear
gen tp = treat * post
gen bp = border * post
"""
d1 += R("ln_seats", "tp bp", "relE >= -12 & relE <= 11", "w12_s")
d1 += R("ln_seats", "tp bp", "relE >= -18 & relE <= 17", "w18_s")
d1 += R("ln_seats", "tp bp", "relE >= -24 & relE <= 23", "w24_s")
d1 += R("ln_seats", "tp bp", "relE >= -36 & relE <= 35", "w36_s")
d1 += R("ln_co2", "tp bp", "relE >= -12 & relE <= 11", "w12_c")
d1 += R("ln_co2", "tp bp", "relE >= -18 & relE <= 17", "w18_c")
d1 += R("ln_co2", "tp bp", "relE >= -24 & relE <= 23", "w24_c")
d1 += R("ln_co2", "tp bp", "relE >= -36 & relE <= 35", "w36_c")
d1 += ESTTAB("w12_s w18_s w24_s w36_s w12_c w18_c w24_c w36_c", "A2_robust_windows.rtf", "Robustness: effective-date windows", "tp bp")
d1 += """
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
"""
MY = "eur == 1 & stk != 0 & k <= 0 & (treat == 1 | border == 1 | ctrl_eur == 1)"
for y, tag in [("ln_gaci", "g"), ("ln_deg", "d"), ("ln_eigen", "e"), ("ln_betw", "b")]:
    d1 += R(y, "tp bp", MY, f"n_{tag}_all")
    d1 += R(y, "tp bp", MY + " & w0 > 0", f"n_{tag}_wt", w=" [aw = w0]")
    d1 += R(y, "tp bp", MY + " & (hub == 1 | treat == 0)", f"n_{tag}_hub")
    d1 += R(y, "tp_small tp_mid tp_large bp", MY, f"n_{tag}_size")
d1 += ESTTAB("n_g_all n_g_wt n_g_hub n_g_size n_d_all n_d_wt n_d_hub n_d_size", "T3_network_gaci_deg.rtf", "Table 3 Network position: GACI and destinations", "tp bp tp_small tp_mid tp_large")
d1 += ESTTAB("n_e_all n_e_wt n_e_hub n_e_size n_b_all n_b_wt n_b_hub n_b_size", "T3_network_eigen_betw.rtf", "Table 3 Network position: eigenvector and betweenness", "tp bp tp_small tp_mid tp_large")
d1 += """
* Table 5 Panel B  Event time, annual GACI: k = -3, -2 (reference -1), 0, +1
"""
d1 += R("ln_gaci", "T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1", "eur == 1 & stk != 0 & (treat == 1 | border == 1 | ctrl_eur == 1)", "es_gaci")
d1 += R("ln_deg", "T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1", "eur == 1 & stk != 0 & (treat == 1 | border == 1 | ctrl_eur == 1)", "es_deg")
d1 += ESTTAB("es_gaci es_deg", "T5_eventtime_year.rtf", "Event time, annual GACI and destinations", "T_km3 T_km2 T_k0 T_k1")
d1 += """
* =====================================================================================
* Table 7  Mechanism. Panel A: exact decomposition ln CO2 = ln destinations + ln(flights per destination) + ln(CO2 per flight)
* (coefficients add up); per-flight CO2 = gauge x stage x intensity. Annual stacks, years E-3..E
* =====================================================================================
"""
for y, tag in [("ln_co2", "m_co2"), ("ln_deg", "m_deg"), ("ln_fl_per_dest", "m_fpd"), ("ln_co2_per_fl", "m_cpf"), ("ln_gauge", "m_gau"), ("ln_stage", "m_stg"), ("ln_int", "m_int")]:
    d1 += R(y, "tp bp", MY, f"{tag}_all")
    d1 += R(y, "tp_small tp_mid tp_large bp", MY, f"{tag}_size")
d1 += ESTTAB("m_co2_all m_deg_all m_fpd_all m_cpf_all m_gau_all m_stg_all m_int_all", "T7_decomposition_all.rtf", "Table 7A Decomposition, all treated", "tp bp")
d1 += ESTTAB("m_co2_size m_deg_size m_fpd_size m_cpf_size m_gau_size m_stg_size m_int_size", "T7_decomposition_size.rtf", "Table 7A Decomposition, by size", "tp_small tp_mid tp_large bp")
d1 += """
* Table 8  Gelbach decomposition: CO2 effect with and without the network variables as controls (descriptive channel share)
"""
d1 += R("ln_co2", "tp_small tp_mid tp_large bp", MY, "gel_0")
d1 += R("ln_co2", "tp_small tp_mid tp_large bp ln_deg", MY, "gel_deg")
d1 += R("ln_co2", "tp_small tp_mid tp_large bp ln_gaci", MY, "gel_gaci")
d1 += R("ln_co2", "tp_small tp_mid tp_large bp ln_deg ln_gaci", MY, "gel_both")
d1 += R("ln_int", "tp_small tp_mid tp_large bp", MY, "geli_0")
d1 += R("ln_int", "tp_small tp_mid tp_large bp ln_gaci", MY, "geli_gaci")
d1 += ESTTAB("gel_0 gel_deg gel_gaci gel_both geli_0 geli_gaci", "T8_gelbach.rtf", "Table 8 Gelbach: CO2 with network controls", "tp_small tp_mid tp_large ln_deg ln_gaci")
d1 += """
* Within-airport elasticities of CO2 outcomes to ln GACI, all stack airport-years (descriptive)
"""
d1 += R("ln_co2", "ln_gaci", "", "el_co2")
d1 += R("ln_int", "ln_gaci", "", "el_int")
d1 += R("ln_deg", "ln_gaci", "", "el_deg")
d1 += R("ln_gauge", "ln_gaci", "", "el_gau")
d1 += R("ln_stage", "ln_gaci", "", "el_stg")
d1 += ESTTAB("el_co2 el_int el_deg el_gau el_stg", "T8_elasticities.rtf", "Table 8A Elasticities to ln GACI", "ln_gaci")
d1 += """
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
"""
d1 += R("ln_fl", "tp_small tp_mid tp_large bp", Y1, "mm_fl")
d1 += R("ln_gauge", "tp_small tp_mid tp_large bp", Y1, "mm_gau")
d1 += """use "stack_loss.dta", clear
gen tp = treat * post1
gen bp = border * post1
gen tp_small = sz_small * post1
gen tp_mid = sz_mid * post1
gen tp_large = sz_large * post1
"""
d1 += R("loss", "tp_small tp_mid tp_large bp", "", "mm_loss")
d1 += ESTTAB("mm_fl mm_gau mm_loss", "T7_margins.rtf", "Table 7B Monthly margins", "tp_small tp_mid tp_large bp")
d1 += """
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
"""
GL = "stk != 0 & donut == 0 & post2 == 0"
d1 += R("ln_seats", "T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1", GL, "g_all_s", fe="fe_u fe_rt")
d1 += R("ln_seats", "T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1", GL + " & eur == 1", "g_eur_s", fe="fe_u fe_rt")
d1 += R("ln_seats", "T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1", GL + " & eur == 0", "g_row_s", fe="fe_u fe_rt")
d1 += R("ln_co2", "T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1", GL, "g_all_c", fe="fe_u fe_rt")
d1 += R("ln_co2", "T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1", GL + " & eur == 1", "g_eur_c", fe="fe_u fe_rt")
d1 += R("ln_co2", "T_pre36_25 T_pre24_13 T_post1 B_pre36_25 B_pre24_13 B_post1", GL + " & eur == 0", "g_row_c", fe="fe_u fe_rt")
d1 += ESTTAB("g_all_s g_eur_s g_row_s g_all_c g_eur_c g_row_c", "T9_global_month.rtf", "Table 9 Global events, monthly", "T_pre36_25 T_pre24_13 T_post1 B_post1")
d1 += """use "stack_year.dta", clear
gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
gen T_km3 = treat * (k == -3)
gen T_km2 = treat * (k == -2)
gen T_k0 = treat * (k == 0)
gen T_k1 = treat * (k == 1)
gen B_km3 = border * (k == -3)
gen B_km2 = border * (k == -2)
gen B_k0 = border * (k == 0)
gen B_k1 = border * (k == 1)
"""
d1 += R("ln_gaci", "T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1", "stk != 0", "g_all_g", fe="fe_u fe_rt")
d1 += R("ln_gaci", "T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1", "stk != 0 & eur == 1", "g_eur_g", fe="fe_u fe_rt")
d1 += R("ln_gaci", "T_km3 T_km2 T_k0 T_k1 B_km3 B_km2 B_k0 B_k1", "stk != 0 & eur == 0", "g_row_g", fe="fe_u fe_rt")
d1 += ESTTAB("g_all_g g_eur_g g_row_g", "T9_global_gaci.rtf", "Table 9 Global events, GACI", "T_km3 T_km2 T_k0 T_k1")
d1 += "log close\n"

# ------------------------------------------------------------------ 02: events (SDID), HonestDiD, mediation
d2 = HEAD.format(cd=CD, log="02_events_mediation_run.log")
d2 += """cap which sdid
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
"""
EVL = [(0, "NLD 2008"), (1, "IRL 2009"), (2, "DEU 2011"), (3, "AUT 2011"), (4, "NOR 2016"), (5, "SWE 2018"), (6, "GBR 2007"), (7, "DNK 1998"), (8, "MLT 2005")]
for k, lab in EVL:
    for y in ["y_seats", "y_co2"]:
        d2 += f'di _n "==== SDID {lab}: {y} ===="\n'
        d2 += f"preserve\nkeep if stk == {k}\ndrop if missing({y})\nsdid {y} iso3n period treat_post, vce(placebo) reps(200) seed(1)\nrestore\n"
d2 += """
use "sdid_year.dta", clear
"""
for k, lab in EVL:
    d2 += f'di _n "==== SDID {lab}: seat-weighted country GACI ===="\n'
    d2 += f"preserve\nkeep if stk == {k}\ncap noisily sdid y_gaci iso3n year treat_post, vce(placebo) reps(200) seed(1)\nrestore\n"
d2 += """
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
"""
for name, txt in [("01_main.do", d1), ("02_events_mediation.do", d2)]:
    assert "/*" not in txt and "///" not in txt and "`" not in txt.replace("`m'", "")
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(txt.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    print(name, "lines:", txt.count("\n"))
