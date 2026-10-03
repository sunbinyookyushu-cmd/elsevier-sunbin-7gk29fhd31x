*==============================================================================
* gaci_main_table.do
* MAIN RESULTS: OLS, first stage, 2SLS for outcomes {openness, volume, GDP}
*   under two connectivity measures: ln_gaci_cwm (hub quality) and lng (sum).
*   Robust SE throughout. Country + year FE. Instrument = tourism_int.
* Output: on-screen esttab + _main_results.rtf  (also _main_results.csv)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_main_table.log", replace text

import delimited "gaci_panel_3iv.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

* ---- outcomes ----
gen g_int = merch_intensity              // goods openness  ln(g/Y)
gen g_vol = merch_intensity + lngdp      // goods volume     ln g
gen g_gdp = lngdp                        // GDP (total)      ln Y

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

* =====================================================================
* loop over the two connectivity measures
*   treat = ln_gaci_cwm  (Panel A, headline) ; lng (Panel B, sum)
* =====================================================================
foreach tr in ln_gaci_cwm lng {

    * ---------- FIRST STAGE: treat on the instrument ----------
    reghdfe `tr' tourism_int lnpop, absorb(isocode y) vce(robust)
    eststo fs_`tr'
    * first-stage F on the excluded instrument
    test tourism_int
    estadd scalar Fstat = r(F)
    estadd local meas "`tr'"

    * ---------- per-outcome OLS and 2SLS ----------
    foreach yv in g_int g_vol g_gdp {

        * OLS
        reghdfe `yv' `tr' lnpop, absorb(isocode y) vce(robust)
        eststo ols_`tr'_`yv'

        * 2SLS (robust)
        ivreghdfe `yv' lnpop (`tr' = tourism_int), absorb(isocode y) robust
        eststo iv_`tr'_`yv'
        estadd scalar KPF = e(widstat)
    }
}

* =====================================================================
* TABLES
*   For each panel: 6 columns = OLS(open,vol,gdp) + 2SLS(open,vol,gdp)
*   keep only the treatment coefficient; show stars, robust SE, F.
* =====================================================================
local opt b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
          nonum mtitles("OLS:Open" "OLS:Vol" "OLS:GDP" "IV:Open" "IV:Vol" "IV:GDP") ///
          coeflabels(ln_gaci_cwm "Hub quality (cwm)" lng "Total conn. (sum)") ///
          stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "Observations"))

di _n "================= PANEL A: HUB QUALITY (cwm) ================="
esttab ols_ln_gaci_cwm_g_int ols_ln_gaci_cwm_g_vol ols_ln_gaci_cwm_g_gdp ///
       iv_ln_gaci_cwm_g_int  iv_ln_gaci_cwm_g_vol  iv_ln_gaci_cwm_g_gdp, ///
       keep(ln_gaci_cwm) `opt'

di _n "================= PANEL B: TOTAL CONNECTIVITY (sum) ================="
esttab ols_lng_g_int ols_lng_g_vol ols_lng_g_gdp ///
       iv_lng_g_int  iv_lng_g_vol  iv_lng_g_gdp, ///
       keep(lng) `opt'

di _n "================= FIRST-STAGE COEFFICIENTS (instrument) ================="
esttab fs_ln_gaci_cwm fs_lng, keep(tourism_int) ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum ///
       mtitles("FS: cwm" "FS: sum") ///
       coeflabels(tourism_int "Instrument (tourism\_int)") ///
       stats(Fstat N, fmt(%9.2f %9.0g) labels("First-stage F" "Observations"))

* ---------- write RTF + CSV versions ----------
esttab ols_ln_gaci_cwm_g_int ols_ln_gaci_cwm_g_vol ols_ln_gaci_cwm_g_gdp ///
       iv_ln_gaci_cwm_g_int  iv_ln_gaci_cwm_g_vol  iv_ln_gaci_cwm_g_gdp  ///
       ols_lng_g_int ols_lng_g_vol ols_lng_g_gdp ///
       iv_lng_g_int  iv_lng_g_vol  iv_lng_g_gdp ///
       using "_main_results.rtf", replace ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       label nonum stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "N")) ///
       title("Main results: OLS and 2SLS, by connectivity measure (robust SE)")

esttab ols_ln_gaci_cwm_g_int ols_ln_gaci_cwm_g_vol ols_ln_gaci_cwm_g_gdp ///
       iv_ln_gaci_cwm_g_int  iv_ln_gaci_cwm_g_vol  iv_ln_gaci_cwm_g_gdp  ///
       ols_lng_g_int ols_lng_g_vol ols_lng_g_gdp ///
       iv_lng_g_int  iv_lng_g_vol  iv_lng_g_gdp ///
       using "_main_results.csv", replace ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       stats(KPF N) plain

di _n "DONE_MAIN_TABLE"
log close
