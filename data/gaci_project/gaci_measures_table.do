*==============================================================================
* gaci_measures_table.do
* Coworker (Chun-an) suggestion: compare the three country-level connectivity
* aggregations from the working paper as the explanatory variable:
*     ln_gaci_sum  = log sum of airport GACI   (= lnG, "total connectivity")
*     ln_gaci_max  = log max airport GACI      (dominant gateway hub)
*     ln_gaci_cwm  = log seat-capacity-weighted mean GACI
* Outcomes (3 only): trade openness / trade volume / GDP.
*   g_int = merch_intensity          goods openness  ln(g/Y)
*   g_vol = merch_intensity + lngdp  goods volume     ln g
*   g_gdp = lngdp                    GDP (total)      ln Y
* Same design as headline table: country + year FE, lnpop control, robust SE,
* instrument = tourism_int (tourism-demand x natural-heritage Bartik).
* Output: on-screen esttab + _measures_results.rtf / .csv
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "_measures_run.log", replace text

import delimited "gaci_panel_measures.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

* ---- rename sum measure for clarity (lnG already = log sum of GACI) ----
gen ln_gaci_sum = lng

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
* loop over the three connectivity measures
* =====================================================================
foreach tr in ln_gaci_sum ln_gaci_max ln_gaci_cwm {

    * ---------- FIRST STAGE: measure on the instrument ----------
    reghdfe `tr' tourism_int lnpop, absorb(isocode y) vce(robust)
    eststo fs_`tr'
    test tourism_int
    estadd scalar Fstat = r(F)

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
* TABLES: one panel per measure, 6 columns = OLS(open,vol,gdp)+IV(open,vol,gdp)
* =====================================================================
local opt b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
          nonum mtitles("OLS:Open" "OLS:Vol" "OLS:GDP" "IV:Open" "IV:Vol" "IV:GDP") ///
          coeflabels(ln_gaci_sum "GACI sum (log)" ln_gaci_max "GACI max (log)" ///
                     ln_gaci_cwm "GACI seat-wtd mean (log)") ///
          stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "Observations"))

di _n "================= PANEL A: GACI SUM (log) ================="
esttab ols_ln_gaci_sum_g_int ols_ln_gaci_sum_g_vol ols_ln_gaci_sum_g_gdp ///
       iv_ln_gaci_sum_g_int  iv_ln_gaci_sum_g_vol  iv_ln_gaci_sum_g_gdp, ///
       keep(ln_gaci_sum) `opt'

di _n "================= PANEL B: GACI MAX (log) ================="
esttab ols_ln_gaci_max_g_int ols_ln_gaci_max_g_vol ols_ln_gaci_max_g_gdp ///
       iv_ln_gaci_max_g_int  iv_ln_gaci_max_g_vol  iv_ln_gaci_max_g_gdp, ///
       keep(ln_gaci_max) `opt'

di _n "================= PANEL C: GACI SEAT-WEIGHTED MEAN (log) ================="
esttab ols_ln_gaci_cwm_g_int ols_ln_gaci_cwm_g_vol ols_ln_gaci_cwm_g_gdp ///
       iv_ln_gaci_cwm_g_int  iv_ln_gaci_cwm_g_vol  iv_ln_gaci_cwm_g_gdp, ///
       keep(ln_gaci_cwm) `opt'

di _n "================= FIRST-STAGE COEFFICIENTS (instrument) ================="
esttab fs_ln_gaci_sum fs_ln_gaci_max fs_ln_gaci_cwm, keep(tourism_int) ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum ///
       mtitles("FS: sum" "FS: max" "FS: cwm") ///
       coeflabels(tourism_int "Instrument (tourism\_int)") ///
       stats(Fstat N, fmt(%9.2f %9.0g) labels("First-stage F" "Observations"))

* ---------- write RTF + CSV ----------
esttab ols_ln_gaci_sum_g_int ols_ln_gaci_sum_g_vol ols_ln_gaci_sum_g_gdp ///
       iv_ln_gaci_sum_g_int  iv_ln_gaci_sum_g_vol  iv_ln_gaci_sum_g_gdp  ///
       ols_ln_gaci_max_g_int ols_ln_gaci_max_g_vol ols_ln_gaci_max_g_gdp ///
       iv_ln_gaci_max_g_int  iv_ln_gaci_max_g_vol  iv_ln_gaci_max_g_gdp  ///
       ols_ln_gaci_cwm_g_int ols_ln_gaci_cwm_g_vol ols_ln_gaci_cwm_g_gdp ///
       iv_ln_gaci_cwm_g_int  iv_ln_gaci_cwm_g_vol  iv_ln_gaci_cwm_g_gdp ///
       using "_measures_results.rtf", replace ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       label nonum stats(KPF N, fmt(%9.1f %9.0g) labels("First-stage KP F" "N")) ///
       title("Three connectivity measures x three outcomes: OLS and 2SLS (robust SE)")

esttab ols_ln_gaci_sum_g_int ols_ln_gaci_sum_g_vol ols_ln_gaci_sum_g_gdp ///
       iv_ln_gaci_sum_g_int  iv_ln_gaci_sum_g_vol  iv_ln_gaci_sum_g_gdp  ///
       ols_ln_gaci_max_g_int ols_ln_gaci_max_g_vol ols_ln_gaci_max_g_gdp ///
       iv_ln_gaci_max_g_int  iv_ln_gaci_max_g_vol  iv_ln_gaci_max_g_gdp  ///
       ols_ln_gaci_cwm_g_int ols_ln_gaci_cwm_g_vol ols_ln_gaci_cwm_g_gdp ///
       iv_ln_gaci_cwm_g_int  iv_ln_gaci_cwm_g_vol  iv_ln_gaci_cwm_g_gdp ///
       using "_measures_results.csv", replace ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) ///
       stats(KPF N) plain

di _n "DONE_MEASURES_TABLE"
log close
