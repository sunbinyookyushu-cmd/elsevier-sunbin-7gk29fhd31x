*==============================================================================
* co2_main.do
* MAIN RESULTS, GACI x aviation CO2 (mirror of trade paper gaci_main_table.do).
*   Outcomes: ln CO2 bunker (headline: LTO territorial + cruise-to-departure),
*             ln CO2 LTO-only, ln CO2 50/50, ln CO2 bunker intl-only,
*             ln seat-km (traffic), ln carbon intensity (CO2/seat-km).
*   Treatments: ln_gaci_cwm (headline) ; lng (sum) and ln_gaci_max for H2.
*   H1: Wald test beta = 1 (proportionality of emissions to connectivity).
*   H3: pre/post-2010 split (instrument has no relevance pre-2010).
*   Country + year FE, robust SE, instrument = tourism_int.
* Output: batch log + _co2_main_results.csv
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "gaci_co2_panel.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen ln_intensity = ln_co2_bunker - ln_seatkm

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

* =====================================================================
* PANEL A: headline treatment ln_gaci_cwm, all outcomes, OLS + 2SLS
* =====================================================================
local outcomes ln_co2_bunker ln_co2_lto ln_co2_5050 ln_co2_bunker_intl ln_seatkm ln_intensity

reghdfe ln_gaci_cwm tourism_int lnpop, absorb(isocode y) vce(robust)
test tourism_int
di _n "FIRST STAGE (cwm): pi = " %9.4f _b[tourism_int] "  F = " %9.2f r(F)

foreach yv of local outcomes {
    reghdfe `yv' ln_gaci_cwm lnpop, absorb(isocode y) vce(robust)
    eststo ols_`yv'
    ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
    eststo iv_`yv'
    estadd scalar KPF = e(widstat)
    * H1 Wald: beta = 1
    test ln_gaci_cwm = 1
    estadd scalar Wald1p = r(p)
    di "  `yv': 2SLS b = " %9.3f _b[ln_gaci_cwm] " (se " %9.3f _se[ln_gaci_cwm] ")  H1 Wald p(b=1) = " %6.3f r(p)
}

di _n "================= PANEL A: 2SLS, treatment = ln_gaci_cwm ================="
esttab iv_ln_co2_bunker iv_ln_co2_lto iv_ln_co2_5050 iv_ln_co2_bunker_intl iv_ln_seatkm iv_ln_intensity, ///
    keep(ln_gaci_cwm) b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum ///
    mtitles("Bunker" "LTO" "5050" "BunkIntl" "SeatKm" "Intensity") ///
    stats(KPF Wald1p N, fmt(%9.1f %9.3f %9.0g) labels("KP F" "Wald p(b=1)" "N"))

di _n "================= PANEL A OLS ================="
esttab ols_ln_co2_bunker ols_ln_co2_lto ols_ln_co2_5050 ols_ln_co2_bunker_intl ols_ln_seatkm ols_ln_intensity, ///
    keep(ln_gaci_cwm) b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum ///
    mtitles("Bunker" "LTO" "5050" "BunkIntl" "SeatKm" "Intensity")

* =====================================================================
* PANEL B: H2 measure comparison, outcome = ln_co2_bunker
* =====================================================================
eststo clear
foreach tr in ln_gaci_cwm lng ln_gaci_max {
    ivreghdfe ln_co2_bunker lnpop (`tr' = tourism_int), absorb(isocode y) robust
    eststo m_`tr'
    estadd scalar KPF = e(widstat)
    test `tr' = 1
    estadd scalar Wald1p = r(p)
}
di _n "================= PANEL B: measures (H2), outcome = bunker ================="
esttab m_ln_gaci_cwm m_lng m_ln_gaci_max, ///
    b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum keep(ln_gaci_cwm lng ln_gaci_max) ///
    mtitles("cwm" "sum" "max") ///
    stats(KPF Wald1p N, fmt(%9.1f %9.3f %9.0g) labels("KP F" "Wald p(b=1)" "N"))

* =====================================================================
* PANEL C: H3 temporal split (headline)
* =====================================================================
eststo clear
ivreghdfe ln_co2_bunker lnpop (ln_gaci_cwm = tourism_int) if y < 2010, absorb(isocode y) robust
eststo t_pre
estadd scalar KPF = e(widstat)
ivreghdfe ln_co2_bunker lnpop (ln_gaci_cwm = tourism_int) if y >= 2010, absorb(isocode y) robust
eststo t_post
estadd scalar KPF = e(widstat)
di _n "================= PANEL C: temporal split ================="
esttab t_pre t_post, keep(ln_gaci_cwm) b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum ///
    mtitles("Pre2010" "Post2010") stats(KPF N, fmt(%9.1f %9.0g) labels("KP F" "N"))

* ---------- CSV export (2SLS Panel A + B) ----------
eststo clear
foreach yv of local outcomes {
    quietly ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust
    eststo x_`yv'
    estadd scalar KPF = e(widstat)
    quietly test ln_gaci_cwm = 1
    estadd scalar Wald1p = r(p)
}
esttab x_* using "_co2_main_results.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) stats(KPF Wald1p N) plain

di _n "DONE_CO2_MAIN"
