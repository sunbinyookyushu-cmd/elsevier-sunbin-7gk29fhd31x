*==============================================================================
* gaci_tables_export.do  --  emit machine-readable result lines for the Word tables
*   TAB1 = main OLS vs IV (robust + clustered SE), 3 outcomes x 2 treatments
*   TAB2 = heterogeneity (split-sample, robust SE), 3 outcomes x subgroups
*   spec: country+year FE, IV = feyrer_int, control ln_sea_ma (+lngdp for volume)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel_feyrer.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
gen trade_intensity = ln_tradevol - lngdp

* moderators (time-invariant)
gen adv_base = adv_int / a_t
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
* TAB1: main (loop over outcome x treatment). extra control lngdp for ln_tradevol.
*------------------------------------------------------------------------------
capture program drop _t1
program define _t1
    args yv treat extra
    quietly {
        reghdfe `yv' `treat' lnpop ln_sea_ma `extra', absorb(isocode y) vce(robust)
        local ob = _b[`treat']
        local op = 2*ttail(e(df_r), abs(_b[`treat']/_se[`treat']))
        ivreghdfe `yv' lnpop ln_sea_ma `extra' (`treat' = feyrer_int), absorb(isocode y) robust
        local b  = _b[`treat']
        local sr = _se[`treat']
        local pr = 2*ttail(e(df_r), abs(`b'/`sr'))
        local F  = e(widstat)
        local N  = e(N)
        ivreghdfe `yv' lnpop ln_sea_ma `extra' (`treat' = feyrer_int), absorb(isocode y) cluster(isocode)
        local sc = _se[`treat']
        local pc = 2*ttail(e(df_r), abs(_b[`treat']/`sc'))
    }
    noisily di "TAB1|`yv'|`treat'|`b'|`sr'|`pr'|`sc'|`pc'|`F'|`ob'|`op'|`N'"
end
_t1 trade_share     lng         ""
_t1 trade_intensity lng         ""
_t1 ln_tradevol     lng         "lngdp"
_t1 trade_share     ln_gaci_cwm ""
_t1 trade_intensity ln_gaci_cwm ""
_t1 ln_tradevol     ln_gaci_cwm "lngdp"

*------------------------------------------------------------------------------
* TAB2: heterogeneity (robust), 3 outcomes per subgroup
*------------------------------------------------------------------------------
capture program drop _t2
program define _t2
    args lbl cond
    foreach yv in trade_share trade_intensity ln_tradevol {
        local extra ""
        if "`yv'" == "ln_tradevol" local extra "lngdp"
        capture noisily quietly ivreghdfe `yv' lnpop ln_sea_ma `extra' (lng = feyrer_int) if `cond', absorb(isocode y) robust
        if _rc == 0 {
            noisily di "TAB2|`lbl'|`yv'|" _b[lng] "|" _se[lng] "|" 2*ttail(e(df_r), abs(_b[lng]/_se[lng])) "|" e(widstat) "|" e(N)
        }
    }
end
_t2 adv_LOW    "hi_adv==0"
_t2 adv_HIGH   "hi_adv==1"
_t2 coastal    "lockd==0"
_t2 landlocked "lockd==1"
_t2 inc_LOW    "hi_inc==0"
_t2 inc_HIGH   "hi_inc==1"
_t2 size_SMALL "lg_size==0"
_t2 size_LARGE "lg_size==1"
levelsof contc, local(lvls)
foreach L of local lvls {
    local nm : label (contc) `L'
    _t2 cont_`nm' "contc==`L'"
}
di "EXPORT_DONE"
