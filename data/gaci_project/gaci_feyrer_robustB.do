*==============================================================================
* gaci_feyrer_robustB.do  --  Robustness B: EXOGENOUS (Bartik) maritime control
*   Concern (co-author): contemporaneous MA_sea (ln_sea_ma) is a "bad control"
*     (endogenous, correlated with eps); since Z shares geography with sea access,
*     conditioning on an endogenous MA_sea does not purge the maritime->trade path
*     and can break the exclusion restriction.
*   Fix B: replace ln_sea_ma with an EXOGENOUS maritime Bartik control
*     sea_int = a_t * ln(sea_MA_1996)  = feyrer_int - adv_int   (no time-varying foreign pop)
*   Test: does the instrument feyrer_int still identify (KP F) and does beta survive,
*         once the maritime channel is absorbed by an exogenous control?
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

* exogenous maritime Bartik control = a_t * ln(sea_MA_1996)
gen sea_int = feyrer_int - adv_int
label var sea_int   "a_t x ln(sea MA 1996), exogenous maritime control"
label var feyrer_int "a_t x ln(air MA 1996), instrument"

di _n "==== how much independent variation? correlations ===="
pwcorr feyrer_int sea_int ln_sea_ma, obs

capture program drop _runB
program define _runB
    args lbl ctrl
    foreach yv in trade_share trade_intensity ln_tradevol {
        local extra ""
        if "`yv'" == "ln_tradevol" local extra "lngdp"
        capture noisily quietly ivreghdfe `yv' lnpop `extra' `ctrl' (lng = feyrer_int), absorb(isocode y) robust
        if _rc == 0 {
            noisily di "RESB|`lbl'|`yv'|" _b[lng] "|" _se[lng] "|" 2*ttail(e(df_r), abs(_b[lng]/_se[lng])) "|" e(widstat) "|" e(N)
        }
    }
end

di _n "######## B1: control = sea_int (EXOGENOUS Bartik) -- the fix ########"
_runB exo_seaint "sea_int"
di _n "######## B0: control = ln_sea_ma (original, possibly endogenous) ########"
_runB orig_seama "ln_sea_ma"
di _n "######## B2: control = sea_int + ln_sea_ma (both) ########"
_runB both "sea_int ln_sea_ma"
di _n "######## B3: no maritime control (reference) ########"
_runB none ""

di _n "######## also: treatment = hub quality (cwm) with sea_int ########"
foreach yv in trade_share trade_intensity ln_tradevol {
    local extra ""
    if "`yv'" == "ln_tradevol" local extra "lngdp"
    capture noisily quietly ivreghdfe `yv' lnpop `extra' sea_int (ln_gaci_cwm = feyrer_int), absorb(isocode y) robust
    if _rc == 0 {
        noisily di "RESB|exo_cwm|`yv'|" _b[ln_gaci_cwm] "|" _se[ln_gaci_cwm] "|" 2*ttail(e(df_r), abs(_b[ln_gaci_cwm]/_se[ln_gaci_cwm])) "|" e(widstat) "|" e(N)
    }
}
di "ROBUSTB_DONE"
