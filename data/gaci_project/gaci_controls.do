*==============================================================================
* gaci_controls.do  (paste-safe: no inline //, no ///, no locals)
* CONTROL SENSITIVITY (Faber-style): the 2SLS openness estimate should not
* move when the feasible time-varying controls (population, GDP, GDP pc)
* enter in different combinations. Country FE absorb all time-invariant
* geography, so these are the only controls available.
* PILOT (python, same spec): none 1.663** / lnpop 1.302** / lngdp 1.706** /
* lnpop+lngdp 1.642** / lnpop+lnpc 1.430** -- stable, always p<0.05.
* Input : gaci_panel_mechanism.csv
* Output: gaci_controls.log
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_controls.log", replace text

import delimited "gaci_panel_mechanism.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen g_int = merch_intensity
gen g_vol = merch_intensity + lngdp

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}
capture which esttab
if _rc {
    ssc install estout, replace
}

eststo clear

* ---- openness, five control sets ----
ivreghdfe g_int (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
eststo c_none
estadd scalar KPF = e(widstat)

ivreghdfe g_int lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
eststo c_pop
estadd scalar KPF = e(widstat)

ivreghdfe g_int lngdp (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
eststo c_gdp
estadd scalar KPF = e(widstat)

ivreghdfe g_int lnpop lngdp (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
eststo c_popgdp
estadd scalar KPF = e(widstat)

ivreghdfe g_int lnpop lnpc (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
eststo c_poppc
estadd scalar KPF = e(widstat)

di _n "============ CONTROL SENSITIVITY: OPENNESS ============"
esttab c_none c_pop c_gdp c_popgdp c_poppc, b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum keep(ln_gaci_cwm) coeflabels(ln_gaci_cwm "Hub quality (cwm)") mtitles("none" "lnpop" "lngdp" "pop+gdp" "pop+pc") stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "Observations"))

di _n "DONE_CONTROLS"
log close
