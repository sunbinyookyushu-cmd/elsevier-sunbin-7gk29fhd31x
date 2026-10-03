*==============================================================================
* gaci_tourism_hetero_iv.do  --  CREATIVE heterogeneity via INTERACTION IV
*   (replaces weakly-identified split-sample IV; full-sample first stage is kept,
*    so the Kleibergen-Paap F stays high instead of collapsing per subsample)
*   treatment   : ln_gaci_cwm (hub quality)            [MAIN VARIABLE]
*   instrument  : tourism_int (tourism shift x heritage)
*   moderators  : (1) remoteness  = ln mean sea distance (CERDI), time-invariant geography
*                 (2) income      = baseline (1996) ln GDP per capita
*   spec: ivreghdfe y lnpop (cwm  cwm#mod = z  z#mod), absorb(country year) robust
*         moderators are MEAN-CENTERED -> 'main' coef = effect at the average country;
*         'inter' coef = how the connectivity effect shifts per unit of the moderator.
*   outcomes (g_int = trade openness = MAIN, first): g_int g_vol g_shr lnpc lngdp
*   emits: HET3|moderator|outcome|term|b|se|p|KP_F|N      (term = main / inter)
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/ext2024"
capture log close _all
log using "gaci_tourism_hetero_iv_run.log", replace text
import delimited "gaci_panel_hetero.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

* goods outcomes
gen g_int = merch_intensity                       // ln(goods/GDP)  = trade openness (MAIN)
gen g_shr = merch_share                           // goods % GDP
gen g_vol = merch_intensity + lngdp               // ln(goods trade value)

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

*------------------------------------------------------------------------------
* moderators, mean-centered
*------------------------------------------------------------------------------
* (1) remoteness: time-invariant ln mean sea distance (CERDI)
quietly summarize ln_remote
gen double rem_c = ln_remote - r(mean)
* (2) baseline income: 1996 ln GDP per capita (exogenous to later trade)
gen tmp = lnpc if y==1996
bysort isocode: egen base_lnpc = max(tmp)
quietly summarize base_lnpc
gen double inc_c = base_lnpc - r(mean)
drop tmp
* (3) population / market size: baseline 1996 ln population
gen tmp = lnpop if y==1996
bysort isocode: egen base_lnpop = max(tmp)
quietly summarize base_lnpop
gen double pop_c = base_lnpop - r(mean)
drop tmp
* (4) land area (time-invariant geography)
quietly summarize lnland
gen double land_c = lnland - r(mean)
* (5) GDP total / economic size: baseline 1996 ln GDP
gen tmp = lngdp if y==1996
bysort isocode: egen base_lngdp = max(tmp)
quietly summarize base_lngdp
gen double gdp_c = base_lngdp - r(mean)
drop tmp
* (6) baseline connectivity level: 1996 ln_gaci_cwm
gen tmp = ln_gaci_cwm if y==1996
bysort isocode: egen base_cwm = max(tmp)
quietly summarize base_cwm
gen double cwm0_c = base_cwm - r(mean)
drop tmp
* baseline (1996) TRADE levels for new subsample splits
gen tmp = g_vol if y==1996
bysort isocode: egen base_gvol = max(tmp)
drop tmp
gen tmp = g_int if y==1996
bysort isocode: egen base_gint = max(tmp)
drop tmp

capture program drop _hx
program define _hx
    args modvar modname
    foreach yv in g_int g_vol g_shr lnpc lngdp {
        capture drop cwm_m z_m
        gen double cwm_m = ln_gaci_cwm * `modvar'
        gen double z_m   = tourism_int * `modvar'
        capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm cwm_m = tourism_int z_m), absorb(isocode y) robust
        if _rc==0 {
            local F = e(widstat)
            local N = e(N)
            local bm = _b[ln_gaci_cwm]
            local sm = _se[ln_gaci_cwm]
            local pm = 2*ttail(e(df_r), abs(`bm'/`sm'))
            local bi = _b[cwm_m]
            local si = _se[cwm_m]
            local pi = 2*ttail(e(df_r), abs(`bi'/`si'))
            noisily di "HET3|`modname'|`yv'|main|`bm'|`sm'|`pm'|`F'|`N'"
            noisily di "HET3|`modname'|`yv'|inter|`bi'|`si'|`pi'|`F'|`N'"
        }
        else noisily di "HET3|`modname'|`yv'|FAIL|.|.|.|.|."
        capture drop cwm_m z_m
    }
end

di _n "############ moderator = remoteness (CERDI sea distance, ln) ############"
_hx rem_c remote
di _n "############ moderator = baseline income (1996 ln GDP per capita) ############"
_hx inc_c income
di _n "############ moderator = population (1996 ln population) ############"
_hx pop_c population
di _n "############ moderator = land area (ln land, geography) ############"
_hx land_c land
di _n "############ moderator = GDP total (1996 ln GDP, economic size) ############"
_hx gdp_c gdptot
di _n "############ moderator = baseline connectivity (1996 ln_gaci_cwm) ############"
_hx cwm0_c baseconn

*------------------------------------------------------------------------------
* SUBSAMPLE split (binary, at median) -- for comparison. Use this instead of the
* interaction ONLY if BOTH halves keep KP first-stage F >= ~10; otherwise it is
* weakly identified (as the earlier region/GDP splits were) and interaction IV wins.
*------------------------------------------------------------------------------
capture program drop _hs
program define _hs
    args splitvar splitname
    quietly summarize `splitvar', detail
    local md = r(p50)
    foreach half in lo hi {
        if "`half'"=="lo" local cond "`splitvar' <  `md'"
        else              local cond "`splitvar' >= `md'"
        foreach yv in g_int g_vol g_shr lnpc lngdp {
            capture noisily ivreghdfe `yv' lnpop (ln_gaci_cwm = tourism_int) if (`cond') & !missing(`splitvar'), absorb(isocode y) robust
            if _rc==0 {
                local b=_b[ln_gaci_cwm]
                local se=_se[ln_gaci_cwm]
                local p=2*ttail(e(df_r),abs(`b'/`se'))
                noisily di "HET4|`splitname'|`half'|`yv'|`b'|`se'|`p'|" e(widstat) "|" e(N)
            }
            else noisily di "HET4|`splitname'|`half'|`yv'|FAIL|.|.|.|."
        }
    }
end
di _n "############ SUBSAMPLE split: remoteness (median) ############"
_hs ln_remote remote
di _n "############ SUBSAMPLE split: baseline income (median) ############"
_hs base_lnpc income
di _n "############ SUBSAMPLE split: baseline GDP total (median) ############"
_hs base_lngdp gdpbase
di _n "############ SUBSAMPLE split: baseline trade VOLUME (median) ############"
_hs base_gvol volbase
di _n "############ SUBSAMPLE split: baseline trade OPENNESS (median) ############"
_hs base_gint openbase
di "DONE_HETIV"
log close
