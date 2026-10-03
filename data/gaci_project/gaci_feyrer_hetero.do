*==============================================================================
* gaci_feyrer_hetero.do  --  Heterogeneity (SPLIT-SAMPLE) of the Feyrer-IV trade effect
*   spec      : ivreghdfe <outcome> lnpop ln_sea_ma (lng = feyrer_int), absorb(isocode y) robust
*   outcomes  : trade_share (% openness) | trade_intensity ln(trade/GDP) | ln_tradevol(+lngdp)
*   moderators (TIME-INVARIANT -> country FE keeps the within-group IV valid):
*     1) aviation advantage adv_base=ln(air/sea_1996)  + landlocked dummy
*     2) development : baseline (earliest-year) ln per-capita GDP
*     3) country size: baseline (earliest-year) ln population
*     4) region      : continent (AF/AS/EU/LA/ME/NA/SW)
*   each cell prints a RESULT line: beta(lng) / SE / p-value / KP first-stage F / N
*   (KP first-stage F = e(widstat) = weak-identification statistic under FE+robust)
*==============================================================================
clear all
set more off
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel_feyrer.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
gen trade_intensity = ln_tradevol - lngdp

* ---- moderators (time-invariant) ----
gen adv_base = adv_int / a_t                       // ln(air/sea_1996), constant within country
bysort isocode (y): gen first_lnpc  = lnpc[1]
bysort isocode (y): gen first_lnpop = lnpop[1]
gen cont = substr(reg,1,2)
encode cont, gen(contc)

summarize adv_base,    detail
gen hi_adv  = (adv_base    > r(p50)) if !missing(adv_base)
summarize first_lnpc,  detail
gen hi_inc  = (first_lnpc  > r(p50)) if !missing(first_lnpc)
summarize first_lnpop, detail
gen lg_size = (first_lnpop > r(p50)) if !missing(first_lnpop)

gen lockd = 0
foreach iso in AFG AND ARM AUT AZE BLR BTN BOL BWA BFA BDI CAF TCD CZE SWZ ETH ///
               HUN KAZ KGZ LAO LSO LIE LUX MWI MLI MDA MNG NPL NER MKD PRY RWA ///
               SMR SRB SVK SSD CHE TJK TKM UGA UZB ZMB ZWE {
    replace lockd = 1 if c == "`iso'"
}

*------------------------------------------------------------------------------
* program: run all 3 outcomes within one subgroup, emit RESULT lines (with p-value)
*------------------------------------------------------------------------------
capture program drop _hcell
program define _hcell
    args lbl cond
    foreach yv in trade_share trade_intensity ln_tradevol {
        local extra ""
        if "`yv'" == "ln_tradevol" local extra "lngdp"
        capture noisily ivreghdfe `yv' lnpop ln_sea_ma `extra' (lng = feyrer_int) ///
            if `cond', absorb(isocode y) robust
        if _rc == 0 {
            local b  = _b[lng]
            local se = _se[lng]
            local p  = 2*ttail(e(df_r), abs(`b'/`se'))
            local F  = e(widstat)
            di as txt "RESULT | " %-16s "`yv'" " | " %-12s "`lbl'" " | b=" as res %9.4f `b' ///
               as txt " se=" as res %9.4f `se' as txt " p=" as res %6.4f `p' ///
               as txt " | KP-firstF=" as res %8.2f `F' as txt " N=" as res e(N)
        }
        else di as err "RESULT | `yv' | `lbl' | FAILED rc=" _rc
    }
end

di _n "############### 1) AVIATION ADVANTAGE (adv_base median split) ###############"
_hcell "adv_LOW"  "hi_adv==0"
_hcell "adv_HIGH" "hi_adv==1"
di _n "############### 1b) LANDLOCKED ###############"
_hcell "coastal"    "lockd==0"
_hcell "landlocked" "lockd==1"
di _n "############### 2) DEVELOPMENT (baseline pc-GDP split) ###############"
_hcell "inc_LOW"  "hi_inc==0"
_hcell "inc_HIGH" "hi_inc==1"
di _n "############### 3) COUNTRY SIZE (baseline pop split) ###############"
_hcell "size_SMALL" "lg_size==0"
_hcell "size_LARGE" "lg_size==1"
di _n "############### 4) REGION / CONTINENT ###############"
levelsof contc, local(lvls)
foreach L of local lvls {
    local nm : label (contc) `L'
    _hcell "cont_`nm'" "contc==`L'"
}

di _n "############### DONE -- grep ^RESULT for the full table ###############"
