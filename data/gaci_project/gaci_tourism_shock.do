*==============================================================================
* gaci_tourism_shock.do  --  COVID & Russia-war shock interactions
*   panel    : gaci_panel_tourism_ext.csv (1996-2023, tourism demand extended to 2023)
*   shocks   : covid = 2020-2021 ; russia = 2022-2023   (year FE absorbs main dummies)
*   interest : GACI x covid , GACI x russia  -> does the connectivity-trade link change?
*   outcome  : merch_intensity = ln(goods/GDP) ; merch_share = goods % GDP
*   (a) OLS interaction (descriptive)  (b) IV interaction (tourism_int, instrument collapses
*       in COVID -> first stage likely weak; reported honestly)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel_tourism_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

gen covid  = inrange(y,2020,2021)
gen russia = (y>=2022)
gen gaci_c = lng*covid
gen gaci_r = lng*russia
gen z      = tourism_int
gen z_c    = tourism_int*covid
gen z_r    = tourism_int*russia
label var lng    "GACI (baseline, non-shock yrs)"
label var gaci_c "GACI x COVID(2020-21)"
label var gaci_r "GACI x Russia(2022-23)"

di _n "############### (a) OLS interaction (descriptive) ###############"
di _n "==== A1 goods openness ===="
reghdfe merch_intensity lng gaci_c gaci_r lnpop, absorb(isocode y) vce(robust)
lincom lng + gaci_c
lincom lng + gaci_r
di _n "==== A2 goods share % ===="
reghdfe merch_share lng gaci_c gaci_r lnpop, absorb(isocode y) vce(robust)

di _n "############### (b) IV interaction (instrument the interactions) ###############"
di _n "==== B1 goods openness, COVID only ===="
ivreghdfe merch_intensity lnpop (lng gaci_c = z z_c), absorb(isocode y) robust first
di _n "==== B2 goods openness, RUSSIA only ===="
ivreghdfe merch_intensity lnpop (lng gaci_r = z z_r), absorb(isocode y) robust first
di _n "==== B3 goods openness, BOTH shocks ===="
ivreghdfe merch_intensity lnpop (lng gaci_c gaci_r = z z_c z_r), absorb(isocode y) robust first

di _n "############### (c) split-sample IV: pre-2020 vs shock period ###############"
di _n "==== C1 pre-2020 (1996-2019) ===="
ivreghdfe merch_intensity lnpop (lng = z) if y<=2019, absorb(isocode y) robust
di _n "==== C2 2020-2023 (shock window) ===="
ivreghdfe merch_intensity lnpop (lng = z) if y>=2020, absorb(isocode y) robust
di "DONE_SHOCK"
