*==============================================================================
* gaci_tourism_iv.do  --  Tourism x UNESCO-heritage instrument, GOODS-trade outcome
*   outcome    : merch_intensity = ln(goods trade / GDP)  [services/tourism EXCLUDED]
*                merch_share     = goods trade % GDP
*   treatment  : lng (GACI_sum) ; ln_gaci_cwm (hub quality)
*   instrument : tourism_int = tour_shift_t * ln(1+natural-heritage endowment)  [Bartik]
*                tourism_cum = tour_shift_t * ln(1+cumulative natural heritage)  [robustness]
*   FE         : country + year (absorb isocode y).  Sample 1996-2019.
*   Exclusion  : natural heritage -> leisure flights -> connectivity -> GOODS trade only.
*                (tourism receipts are SERVICES, removed by using merchandise trade.)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel_tourism.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
label var lng         "ln GACI_sum"
label var tourism_int "tourism shift x heritage endowment (IV)"

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

*------------------------------------------------------------------------------
* 1) FIRST-STAGE: does tourism_int predict connectivity under country+year FE?
*------------------------------------------------------------------------------
di _n "==== 1a tourism_int -> lng, country+year FE (robust) ===="
reghdfe lng tourism_int lnpop, absorb(isocode y) vce(robust)
test tourism_int
di _n "==== 1b tourism_int -> lng, country+year FE (cluster) ===="
reghdfe lng tourism_int lnpop, absorb(isocode y) cluster(isocode)
test tourism_int
di _n "==== 1c tourism_int -> ln_gaci_cwm, country+year FE (robust) ===="
reghdfe ln_gaci_cwm tourism_int lnpop, absorb(isocode y) vce(robust)
test tourism_int

*------------------------------------------------------------------------------
* 2) 2SLS: connectivity -> GOODS trade, IV = tourism_int
*------------------------------------------------------------------------------
di _n "===== M1 goods openness (merch_intensity), (lng = tourism_int), ROBUST ====="
ivreghdfe merch_intensity lnpop (lng = tourism_int), absorb(isocode y) robust first
di _n "===== M1c same, CLUSTER ====="
ivreghdfe merch_intensity lnpop (lng = tourism_int), absorb(isocode y) cluster(isocode) first

di _n "===== M2 goods share % (merch_share), (lng = tourism_int), ROBUST ====="
ivreghdfe merch_share lnpop (lng = tourism_int), absorb(isocode y) robust first

di _n "===== M3 robustness: IV = tourism_cum (time-varying stock) ====="
ivreghdfe merch_intensity lnpop (lng = tourism_cum), absorb(isocode y) robust first

di _n "===== M4 treatment = hub quality (ln_gaci_cwm = tourism_int) ====="
ivreghdfe merch_intensity lnpop (ln_gaci_cwm = tourism_int), absorb(isocode y) robust first

di _n "===== M5 OLS benchmark (goods openness on lng) ====="
reghdfe merch_intensity lng lnpop, absorb(isocode y) vce(robust)

di _n "===== M6 reduced form: goods openness on tourism_int directly ====="
reghdfe merch_intensity tourism_int lnpop, absorb(isocode y) vce(robust)
di "DONE_TOURISM"
