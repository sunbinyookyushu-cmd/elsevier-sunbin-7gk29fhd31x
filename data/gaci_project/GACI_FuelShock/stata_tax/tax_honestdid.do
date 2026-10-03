* =====================================================================
* Ticket taxes: event study and HonestDiD (Rambachan and Roth 2023)
* Data: tax_es_stack.dta from 95_tax_main.py (8 events, NLD analysed separately)
* Event time from the announcement with a donut; annual bins:
*   pre  T_pre36_25 (A-36..A-25), T_pre24_13 (A-24..A-13); reference A-12..A-1
*   post T_post0_11 (E..E+11), T_post12_23 (E+12..E+23)
* Border rings B50, B150, B300 enter as separate groups.
* FE airport x calendar month x stack and month x stack; SE by country.
* Needs reghdfe, ftools, honestdid (installed below if missing).
* =====================================================================
clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_tax"
cap log close
log using "tax_honestdid_run.log", replace text
cap which reghdfe
if _rc ssc install reghdfe
cap which ftools
if _rc ssc install ftools
cap which honestdid
if _rc net install honestdid, from("https://raw.githubusercontent.com/mcaceresb/stata-honestdid/main") replace
use "tax_es_stack.dta", clear
reghdfe ln_seats T_pre36_25 T_pre24_13 T_post0_11 T_post12_23 B50_pre36_25 B50_pre24_13 B50_post0_11 B50_post12_23 B150_pre36_25 B150_pre24_13 B150_post0_11 B150_post12_23 B300_pre36_25 B300_pre24_13 B300_post0_11 B300_post12_23, absorb(fe_u fe_t) vce(cluster iso3n)
* relative magnitudes: post-period violations up to Mbar times the largest pre-period violation
honestdid, pre(1/2) post(3/4) mvec(0(0.5)2) delta(rm)
* smoothness: deviations from a linear pre-trend bounded by M (log points per year)
honestdid, pre(1/2) post(3/4) mvec(0(0.01)0.05)
log close
