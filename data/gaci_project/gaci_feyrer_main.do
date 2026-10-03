*==============================================================================
* gaci_feyrer_main.do  --  MAIN results: OLS + IV (ivreghdfe), 3 trade outcomes
*   spec       : COUNTRY+YEAR FE (absorb isocode y), robust SE
*   treatment  : lng (GACI_sum) and ln_gaci_cwm (hub quality)
*   instrument : feyrer_int = a_t * ln(air_MA_1996)   [Feyrer air-vs-sea, survives FE]
*   control    : ln_sea_ma (maritime channel; +lngdp for the volume outcome)
*   outcomes   : trade_share (% openness) | trade_intensity ln(trade/GDP) | ln_tradevol
*   diagnostic : ivreghdfe 'first' -> Kleibergen-Paap first-stage F = e(widstat)
*   each model prints a PAPER line: IV beta / SE / p-value / KP first-stage F / OLS / N
*==============================================================================
clear all
set more off
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel_feyrer.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
encode reg, gen(regcode)
xtset isocode y
gen trade_intensity = ln_tradevol - lngdp
label var lng         "ln GACI_sum"
label var ln_gaci_cwm "ln cap-wtd-mean GACI (hub quality)"
label var feyrer_int  "Feyrer air/sea x a_t (IV)"
label var ln_sea_ma   "ln sea market access (control)"

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

*==============================================================================
* TREATMENT = lng (GACI_sum)
*==============================================================================
di _n "==================== trade_share  <-  lng ===================="
reghdfe trade_share lng lnpop ln_sea_ma, absorb(isocode y) vce(robust)
local ob = _b[lng]
local op = 2*ttail(e(df_r), abs(_b[lng]/_se[lng]))
ivreghdfe trade_share lnpop ln_sea_ma (lng = feyrer_int), absorb(isocode y) robust first
local b = _b[lng]
local se = _se[lng]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
local F = e(widstat)
local n = e(N)
di as txt "PAPER | trade_share <- lng | IVb=" %9.4f `b' " se=" %9.4f `se' " p=" %6.4f `p' " KPfirstF=" %8.2f `F' " OLSb=" %9.4f `ob' " OLSp=" %6.4f `op' " N=" `n'

di _n "==================== trade_intensity  <-  lng ===================="
reghdfe trade_intensity lng lnpop ln_sea_ma, absorb(isocode y) vce(robust)
local ob = _b[lng]
local op = 2*ttail(e(df_r), abs(_b[lng]/_se[lng]))
ivreghdfe trade_intensity lnpop ln_sea_ma (lng = feyrer_int), absorb(isocode y) robust first
local b = _b[lng]
local se = _se[lng]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
local F = e(widstat)
local n = e(N)
di as txt "PAPER | trade_intensity <- lng | IVb=" %9.4f `b' " se=" %9.4f `se' " p=" %6.4f `p' " KPfirstF=" %8.2f `F' " OLSb=" %9.4f `ob' " OLSp=" %6.4f `op' " N=" `n'

di _n "==================== ln_tradevol  <-  lng  (+lngdp) ===================="
reghdfe ln_tradevol lng lngdp lnpop ln_sea_ma, absorb(isocode y) vce(robust)
local ob = _b[lng]
local op = 2*ttail(e(df_r), abs(_b[lng]/_se[lng]))
ivreghdfe ln_tradevol lngdp lnpop ln_sea_ma (lng = feyrer_int), absorb(isocode y) robust first
local b = _b[lng]
local se = _se[lng]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
local F = e(widstat)
local n = e(N)
di as txt "PAPER | ln_tradevol <- lng | IVb=" %9.4f `b' " se=" %9.4f `se' " p=" %6.4f `p' " KPfirstF=" %8.2f `F' " OLSb=" %9.4f `ob' " OLSp=" %6.4f `op' " N=" `n'

*==============================================================================
* TREATMENT = ln_gaci_cwm (hub quality)
*==============================================================================
di _n "==================== trade_share  <-  ln_gaci_cwm ===================="
reghdfe trade_share ln_gaci_cwm lnpop ln_sea_ma, absorb(isocode y) vce(robust)
local ob = _b[ln_gaci_cwm]
local op = 2*ttail(e(df_r), abs(_b[ln_gaci_cwm]/_se[ln_gaci_cwm]))
ivreghdfe trade_share lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust first
local b = _b[ln_gaci_cwm]
local se = _se[ln_gaci_cwm]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
local F = e(widstat)
local n = e(N)
di as txt "PAPER | trade_share <- cwm | IVb=" %9.4f `b' " se=" %9.4f `se' " p=" %6.4f `p' " KPfirstF=" %8.2f `F' " OLSb=" %9.4f `ob' " OLSp=" %6.4f `op' " N=" `n'

di _n "==================== trade_intensity  <-  ln_gaci_cwm ===================="
reghdfe trade_intensity ln_gaci_cwm lnpop ln_sea_ma, absorb(isocode y) vce(robust)
local ob = _b[ln_gaci_cwm]
local op = 2*ttail(e(df_r), abs(_b[ln_gaci_cwm]/_se[ln_gaci_cwm]))
ivreghdfe trade_intensity lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust first
local b = _b[ln_gaci_cwm]
local se = _se[ln_gaci_cwm]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
local F = e(widstat)
local n = e(N)
di as txt "PAPER | trade_intensity <- cwm | IVb=" %9.4f `b' " se=" %9.4f `se' " p=" %6.4f `p' " KPfirstF=" %8.2f `F' " OLSb=" %9.4f `ob' " OLSp=" %6.4f `op' " N=" `n'

di _n "==================== ln_tradevol  <-  ln_gaci_cwm  (+lngdp) ===================="
reghdfe ln_tradevol ln_gaci_cwm lngdp lnpop ln_sea_ma, absorb(isocode y) vce(robust)
local ob = _b[ln_gaci_cwm]
local op = 2*ttail(e(df_r), abs(_b[ln_gaci_cwm]/_se[ln_gaci_cwm]))
ivreghdfe ln_tradevol lngdp lnpop ln_sea_ma (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust first
local b = _b[ln_gaci_cwm]
local se = _se[ln_gaci_cwm]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
local F = e(widstat)
local n = e(N)
di as txt "PAPER | ln_tradevol <- cwm | IVb=" %9.4f `b' " se=" %9.4f `se' " p=" %6.4f `p' " KPfirstF=" %8.2f `F' " OLSb=" %9.4f `ob' " OLSp=" %6.4f `op' " N=" `n'

di _n "################ ALL PAPER LINES (grep ^PAPER) ################"
