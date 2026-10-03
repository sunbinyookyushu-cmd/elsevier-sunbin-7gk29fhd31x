*==============================================================================
* gaci_temporal_table.do
* TEMPORAL HETEROGENEITY: has the connectivity->trade effect changed over time?
*   (A) split at 2010:  effect in 1996-2009  vs  2010-2023  (cwm = tourism_int)
*   (B) interaction:    cwm + cwm#post  instrumented by tourism_int + tourism_int#post
*       -> "post" coefficient = how much the effect differs after 2010.
*   Treatment = ln_gaci_cwm. Country+year FE, robust SE.
*   NOTE: the instrument barely moves before 2010, so the pre-2010 first stage is
*         very weak (KP F near zero) -- this is itself the finding.
* Output: on-screen esttab + _temporal_results.rtf / .csv
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_temporal_table.log", replace text

import delimited "gaci_panel_3iv.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen g_int = merch_intensity              // openness
gen g_vol = merch_intensity + lngdp      // volume
gen g_gdp = lngdp                        // GDP
gen post  = (y>=2010)

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

* ---------- (A) pre / post 2010 split ----------
foreach yv in g_int g_vol g_gdp {
    ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int) if y<2010, ///
        absorb(isocode y) robust
    eststo pre_`yv'
    estadd scalar KPF = e(widstat)

    ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int) if y>=2010, ///
        absorb(isocode y) robust
    eststo post_`yv'
    estadd scalar KPF = e(widstat)
}

* ---------- (B) formal interaction with post-2010 ----------
gen cwm_post = ln_gaci_cwm * post
gen z_post   = tourism_int  * post
foreach yv in g_int g_vol g_gdp {
    ivreghdfe `yv' lnpop (ln_gaci_cwm cwm_post = tourism_int z_post), ///
        absorb(isocode y) robust
    eststo int_`yv'
    estadd scalar KPF = e(widstat)
}

* =====================================================================
* TABLES
* =====================================================================
local lbl coeflabels(ln_gaci_cwm "Connectivity" cwm_post "$\times$ post-2010")

di _n "================= (A) PRE 1996-2009  vs  POST 2010-2023 ================="
esttab pre_g_int post_g_int pre_g_vol post_g_vol pre_g_gdp post_g_gdp, ///
       keep(ln_gaci_cwm) `lbl' nonum ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       mtitles("Open:pre" "Open:post" "Vol:pre" "Vol:post" "GDP:pre" "GDP:post") ///
       stats(KPF N, fmt(%9.2f %9.0g) labels("KP F" "N"))

di _n "================= (B) INTERACTION cwm + cwm#post ================="
esttab int_g_int int_g_vol int_g_gdp, ///
       keep(ln_gaci_cwm cwm_post) `lbl' nonum ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       mtitles("Openness" "Volume" "GDP") ///
       stats(KPF N, fmt(%9.2f %9.0g) labels("KP F" "N"))

* ---------- write RTF + CSV ----------
esttab pre_g_int post_g_int pre_g_vol post_g_vol pre_g_gdp post_g_gdp ///
       using "_temporal_split.rtf", replace ///
       keep(ln_gaci_cwm) `lbl' nonum ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       mtitles("Open:pre" "Open:post" "Vol:pre" "Vol:post" "GDP:pre" "GDP:post") ///
       stats(KPF N, fmt(%9.2f %9.0g) labels("KP F" "N")) ///
       title("Temporal split: pre-2010 vs post-2010 (robust SE)")

esttab int_g_int int_g_vol int_g_gdp ///
       using "_temporal_interaction.rtf", replace ///
       keep(ln_gaci_cwm cwm_post) `lbl' nonum ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       mtitles("Openness" "Volume" "GDP") ///
       stats(KPF N, fmt(%9.2f %9.0g) labels("KP F" "N")) ///
       title("Temporal interaction with post-2010 (robust SE)")

esttab pre_g_int post_g_int pre_g_vol post_g_vol pre_g_gdp post_g_gdp ///
       int_g_int int_g_vol int_g_gdp ///
       using "_temporal_results.csv", replace ///
       keep(ln_gaci_cwm cwm_post) ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) stats(KPF N) plain

di _n "DONE_TEMPORAL_TABLE"
log close
