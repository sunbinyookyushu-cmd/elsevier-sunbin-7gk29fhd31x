*==============================================================================
* gaci_tourism_hetero.do  --  Heterogeneity of the tourism-IV goods-trade effect
*   spec     : ivreghdfe <goods outcome> lnpop (lng = tourism_int), absorb(isocode y) robust
*   outcomes : merch_intensity = ln(goods trade/GDP) ; merch_share = goods % GDP
*   moderators (time-invariant): heritage endowment / income / size / continent / landlocked
*   each cell: beta(lng) / SE / p / KP first-stage F / N   (split-sample, robust)
*   NB countries with zero natural heritage have tourism_int = 0 (no identification);
*      the low-heritage cell is therefore weak by construction and flagged.
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

* ---- moderators ----
bysort isocode (y): gen first_lnpc  = lnpc[1]
bysort isocode (y): gen first_lnpop = lnpop[1]
gen cont = substr(reg,1,2)
encode cont, gen(contc)
summarize nat_endow,   detail
gen hi_her  = (nat_endow   > r(p50)) if !missing(nat_endow)
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

capture program drop _hcell
program define _hcell
    args lbl cond
    foreach yv in merch_intensity merch_share {
        capture noisily quietly ivreghdfe `yv' lnpop (lng = tourism_int) if `cond', absorb(isocode y) robust
        if _rc == 0 {
            local b  = _b[lng]
            local se = _se[lng]
            local p  = 2*ttail(e(df_r), abs(`b'/`se'))
            local F  = e(widstat)
            noisily di "REST|" %-16s "`yv'" "|" %-12s "`lbl'" "|b=" %10.4f `b' "|se=" %9.4f `se' "|p=" %6.4f `p' "|KPF=" %8.2f `F' "|N=" %5.0f e(N)
        }
        else noisily di "REST|`yv'|`lbl'|FAILED rc=" _rc
    }
end

di _n "############### 1) HERITAGE endowment (native dimension) ###############"
_hcell "her_HIGH" "hi_her==1"
_hcell "her_LOW"  "hi_her==0"
di _n "############### 2) DEVELOPMENT (baseline pc-GDP) ###############"
_hcell "inc_LOW"  "hi_inc==0"
_hcell "inc_HIGH" "hi_inc==1"
di _n "############### 3) COUNTRY SIZE (baseline pop) ###############"
_hcell "size_SMALL" "lg_size==0"
_hcell "size_LARGE" "lg_size==1"
di _n "############### 4) LANDLOCKED ###############"
_hcell "coastal"    "lockd==0"
_hcell "landlocked" "lockd==1"
di _n "############### 5) CONTINENT ###############"
levelsof contc, local(lvls)
foreach L of local lvls {
    local nm : label (contc) `L'
    _hcell "cont_`nm'" "contc==`L'"
}
di "DONE_TOURISM_HET"
