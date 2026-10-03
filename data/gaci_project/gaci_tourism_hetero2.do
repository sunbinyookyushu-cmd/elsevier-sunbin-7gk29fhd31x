*==============================================================================
* gaci_tourism_hetero2.do  --  Heterogeneity (split-sample) of the tourism-IV effect
*   instrument : tourism_int  (tourism shift x heritage endowment), country+year FE, robust
*   treatment  : ln_gaci_cwm  (hub quality = capacity-weighted-mean GACI)  [MAIN VARIABLE]
*   OUTCOMES (GOODS / merchandise trade, services & tourism excluded):
*     g_vol  = ln(goods trade value)        ("ln trade volume")
*     g_int  = ln(goods trade / GDP)        ("trade intensity")  = merch_intensity
*     g_shr  = goods trade % GDP            ("trade share")       = merch_share
*   GROUPS: 1996 GACI < / > median ; 1996 GDP < / > median ; region (continent)
*   each cell -> RESULT line: outcome | group | beta | se | p | KP first-stage F | N
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_tourism_hetero2.log", replace text
import delimited "gaci_panel_tourism_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

* goods outcomes
gen g_int = merch_intensity                       // ln(goods/GDP)
gen g_shr = merch_share                           // goods % GDP
gen g_vol = merch_intensity + lngdp               // ln(goods trade value)

* baseline (1996) splits  -- baseline hub quality (ln_gaci_cwm) to match the main treatment
gen tmp_g = ln_gaci_cwm if y==1996
gen tmp_y = lngdp       if y==1996
bysort isocode: egen base_gaci = max(tmp_g)
bysort isocode: egen base_gdp  = max(tmp_y)
bysort isocode: gen firstobs = (_n==1)
summarize base_gaci if firstobs, detail
local mg = r(p50)
summarize base_gdp  if firstobs, detail
local my = r(p50)
gen gaci_hi = (base_gaci > `mg') if !missing(base_gaci)
gen gdp_hi  = (base_gdp  > `my') if !missing(base_gdp)
gen cont = substr(reg,1,2)
encode cont, gen(contc)

capture program drop _hc
program define _hc
    args lbl cond
    foreach yv in g_vol g_int g_shr lnpc lngdp {
        capture noisily quietly ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int) if `cond', absorb(isocode y) robust
        if _rc == 0 {
            local b  = _b[ln_gaci_cwm]
            local se = _se[ln_gaci_cwm]
            local p  = 2*ttail(e(df_r), abs(`b'/`se'))
            noisily di "RES2|" "`yv'" "|" "`lbl'" "|" `b' "|" `se' "|" `p' "|" e(widstat) "|" e(N)
        }
        else noisily di "RES2|`yv'|`lbl'|FAIL|.|.|.|."
    }
end

di _n "############ pooled (all) ############"
_hc all "1==1"
di _n "############ 1996 GACI median split ############"
_hc gaci_below "gaci_hi==0"
_hc gaci_above "gaci_hi==1"
di _n "############ 1996 GDP median split ############"
_hc gdp_below "gdp_hi==0"
_hc gdp_above "gdp_hi==1"
di _n "############ regions ############"
levelsof contc, local(lvls)
foreach L of local lvls {
    local nm : label (contc) `L'
    _hc region_`nm' "contc==`L'"
}
di "DONE_HET2"
log close
