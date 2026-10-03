*==============================================================================
* gaci_hetero_table.do
* HETEROGENEITY (interaction IV): does the connectivity->trade effect vary with
*   (1) baseline income, (2) baseline connectivity, (3) remoteness?
*   Spec: ivreghdfe yv lnpop (cwm  cwm#mod = tourism_int  tourism_int#mod)
*         -> "main" = effect at the moderator mean ; "inter" = how it shifts.
*   Treatment = ln_gaci_cwm (headline). Country+year FE, robust SE.
* Output: on-screen esttab by outcome + _hetero_results.rtf / .csv
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_hetero_table.log", replace text

import delimited "gaci_panel_3iv.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen g_int = merch_intensity              // openness
gen g_vol = merch_intensity + lngdp      // volume
gen g_gdp = lngdp                        // GDP

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

* ---- moderators, mean-centered (baseline 1996 where time-varying) ----
gen tmp = lnpc if y==1996
bysort isocode: egen base_lnpc = max(tmp)
quietly summarize base_lnpc
gen inc_c = base_lnpc - r(mean)
drop tmp

gen tmp = ln_gaci_cwm if y==1996
bysort isocode: egen base_cwm = max(tmp)
quietly summarize base_cwm
gen con_c = base_cwm - r(mean)
drop tmp

quietly summarize ln_remote
gen rem_c = ln_remote - r(mean)

eststo clear

* ---- one moderator: builds cwm#mod and instrument#mod, runs 3 outcomes ----
capture program drop _het
program define _het
    args mod tag
    gen cwm_`tag' = ln_gaci_cwm * `mod'
    gen z_`tag'   = tourism_int  * `mod'
    foreach yv in g_int g_vol g_gdp {
        ivreghdfe `yv' lnpop (ln_gaci_cwm cwm_`tag' = tourism_int z_`tag'), ///
            absorb(isocode y) robust
        eststo `yv'_`tag'
        estadd scalar KPF = e(widstat)
    }
end

_het inc_c inc
_het con_c con
_het rem_c rem

* =====================================================================
* TABLES  (rows: connectivity at mean + its interaction with the moderator)
* =====================================================================
local lbl coeflabels(ln_gaci_cwm "Connectivity (at mean)" ///
          cwm_inc "$\times$ baseline income" ///
          cwm_con "$\times$ baseline connectivity" ///
          cwm_rem "$\times$ remoteness")
local opt b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum `lbl' ///
          stats(KPF N, fmt(%9.2f %9.0g) labels("KP F (weak-id)" "N"))

di _n "================= OPENNESS  ln(g/Y) ================="
esttab g_int_inc g_int_con g_int_rem, ///
       keep(ln_gaci_cwm cwm_inc cwm_con cwm_rem) ///
       mtitles("Income" "Base.conn" "Remote") `opt'

di _n "================= VOLUME  ln g ================="
esttab g_vol_inc g_vol_con g_vol_rem, ///
       keep(ln_gaci_cwm cwm_inc cwm_con cwm_rem) ///
       mtitles("Income" "Base.conn" "Remote") `opt'

di _n "================= GDP  ln Y ================="
esttab g_gdp_inc g_gdp_con g_gdp_rem, ///
       keep(ln_gaci_cwm cwm_inc cwm_con cwm_rem) ///
       mtitles("Income" "Base.conn" "Remote") `opt'

* ---------- write RTF + CSV (openness & volume, the trade outcomes) ----------
esttab g_int_inc g_int_con g_int_rem g_vol_inc g_vol_con g_vol_rem ///
       using "_hetero_results.rtf", replace ///
       keep(ln_gaci_cwm cwm_inc cwm_con cwm_rem) ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum `lbl' ///
       stats(KPF N, fmt(%9.2f %9.0g) labels("KP F" "N")) ///
       mgroups("Openness" "Volume", pattern(1 0 0 1 0 0)) ///
       title("Heterogeneity: interaction IV (robust SE)")

esttab g_int_inc g_int_con g_int_rem g_vol_inc g_vol_con g_vol_rem ///
       using "_hetero_results.csv", replace ///
       keep(ln_gaci_cwm cwm_inc cwm_con cwm_rem) ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) stats(KPF N) plain

di _n "DONE_HETERO_TABLE"
log close
