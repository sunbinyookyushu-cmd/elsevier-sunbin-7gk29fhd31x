*==============================================================================
* gaci_mechanism.do  (v4: paste-safe -- no inline //, no ///, no locals)
* MECHANISM: does connectivity tilt trade composition as the channels predict?
* Outcomes (BACI HS92, country-year, X+M unless noted):
*   r_vw     = ln(high/low unit-value trade), median split   [belly channel]
*   sh_hivw  = high unit-value share of total trade, in pp
*   r_bec    = ln(intermediates/consumption)                 [GVC channel]
*   sh_bec   = intermediates/(interm+consum) share, in pp
*   xr_vw    = EXPORT-only ln(top/bottom unit-value tercile)
*   xsh_hivw = EXPORT-only top-tercile share, in pp
*   lntot    = ln total BACI trade (coherence check)
* Samples: FULL 1996-2023 = MAIN; robustness drops 2020-21 only.
* Spec: ivreghdfe, country+year FE, treat=ln_gaci_cwm, IV=tourism_int,
*   control lnpop, robust SE (identical to gaci_main_table.do).
* Input : gaci_panel_mechanism.csv
* Output: gaci_mechanism.log + _mechanism_results.rtf/.csv
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/ext2024"
capture log close _all
log using "gaci_mechanism_run.log", replace text

import delimited "gaci_panel_mechanism.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

* ---- composition outcomes ----
gen r_vw = ln_tr_hivw - ln_tr_lovw
gen sh_hivw = tr_hivw/tr_total*100
gen r_bec = ln_tr_interm - ln_tr_consum
gen sh_bec = tr_interm/(tr_interm + tr_consum)*100
gen xr_vw = ln_x_hivw3 - ln_x_lovw3
gen xsh_hivw = x_hivw3/(x_hivw3 + x_lovw3)*100
gen lntot = ln_tr_total

* ---- samples ----
gen byte sfull = 1
gen byte sdrop = 1
replace sdrop = 0 if y == 2020
replace sdrop = 0 if y == 2021

* ---- packages ----
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

* ---- 2SLS: each outcome x (full, drop 2020-21) ----
foreach s in sfull sdrop {
    foreach yv in r_vw sh_hivw r_bec sh_bec xr_vw xsh_hivw lntot {
        ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int) if `s', absorb(isocode y) robust
        eststo `yv'_`s'
        estadd scalar KPF = e(widstat)
    }
}

* ---- tables ----
di _n "============ PANEL A: FULL SAMPLE 1996-2023 (MAIN) ============"
esttab r_vw_sfull sh_hivw_sfull r_bec_sfull sh_bec_sfull xr_vw_sfull xsh_hivw_sfull lntot_sfull, b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum keep(ln_gaci_cwm) coeflabels(ln_gaci_cwm "Hub quality (cwm)") mtitles("ln(Hi/Lo)" "HiVW sh" "ln(Int/Con)" "Int sh" "X:ln(T/B)" "X:Top sh" "ln Total") stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "Observations"))

di _n "============ PANEL B: DROP 2020-21 (acute pandemic) ============"
esttab r_vw_sdrop sh_hivw_sdrop r_bec_sdrop sh_bec_sdrop xr_vw_sdrop xsh_hivw_sdrop lntot_sdrop, b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum keep(ln_gaci_cwm) coeflabels(ln_gaci_cwm "Hub quality (cwm)") mtitles("ln(Hi/Lo)" "HiVW sh" "ln(Int/Con)" "Int sh" "X:ln(T/B)" "X:Top sh" "ln Total") stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "Observations"))

* ---- RTF + CSV ----
esttab r_vw_sfull sh_hivw_sfull r_bec_sfull sh_bec_sfull xr_vw_sfull xsh_hivw_sfull r_vw_sdrop sh_hivw_sdrop r_bec_sdrop sh_bec_sdrop xr_vw_sdrop xsh_hivw_sdrop using "_mechanism_results.rtf", replace b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) label nonum keep(ln_gaci_cwm) coeflabels(ln_gaci_cwm "Hub quality (cwm)") mtitles("ln(Hi/Lo)" "HiVW sh" "ln(Int/Con)" "Int sh" "X:ln(T/B)" "X:Top sh" "ln(Hi/Lo)" "HiVW sh" "ln(Int/Con)" "Int sh" "X:ln(T/B)" "X:Top sh") stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "N")) title("Mechanism: trade composition 2SLS. Cols 1-6 full 1996-2023 (main), 7-12 drop 2020-21.")

esttab r_vw_sfull sh_hivw_sfull r_bec_sfull sh_bec_sfull xr_vw_sfull xsh_hivw_sfull lntot_sfull r_vw_sdrop sh_hivw_sdrop r_bec_sdrop sh_bec_sdrop xr_vw_sdrop xsh_hivw_sdrop lntot_sdrop using "_mechanism_results.csv", replace b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) keep(ln_gaci_cwm) stats(KPF N) plain

di _n "DONE_MECHANISM"
log close
