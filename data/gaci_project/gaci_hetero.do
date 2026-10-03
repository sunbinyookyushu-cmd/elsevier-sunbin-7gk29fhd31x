*==============================================================================
* gaci_hetero.do  --  Heterogeneity of the GACI -> trade-openness IV effect
*   Base spec : ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y
*               (ln_gaci_cwm = lnz), vce(robust)
*   Method    : (A) split-sample IV + estat firststage per subgroup
*               (B) interaction IV (instrument the interaction too) -> tests if the
*                   slope differs across the moderator; estat firststage (S-W F)
*   Moderators: income (lnpc), country size (lnpop), period (pre/post 2010),
*               connectivity level (lng = hub vs non-hub)
*   SE        : robust, NOT clustered  (analyst choice 2026-06-17)
*==============================================================================
clear all
set more off
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel.csv", clear varnames(1) encoding("utf-8")

ds c reg, not
destring `r(varlist)', replace force
encode c,   gen(isocode)
encode reg, gen(regcode)
xtset isocode y
gen trade_intensity = ln_tradevol - lngdp

* ---- moderators (median splits, computed once) ----
summarize lnpc,  detail
gen hi_inc  = (lnpc  > r(p50)) if !missing(lnpc)        // 1 = high income
summarize lnpop, detail
gen lg_size = (lnpop > r(p50)) if !missing(lnpop)       // 1 = large country
gen late    = (y >= 2010)                               // 1 = 2010-2023
summarize lng,   detail
gen hub     = (lng  > r(p50)) if !missing(lng)          // 1 = high connectivity

label define yn 0 "low" 1 "high"
label values hi_inc lg_size hub yn

*==============================================================================
* A) SPLIT-SAMPLE IV  (headline spec run separately within each subgroup)
*    each block: 2SLS coefficient on ln_gaci_cwm + estat firststage (weak-id F)
*==============================================================================
eststo clear

di _n "##################### A1. by INCOME #####################"
foreach g in 0 1 {
    di _n "==== income = `g'  (0=low,1=high) ===="
    ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y ///
        (ln_gaci_cwm = lnz) if hi_inc==`g', vce(robust)
    estimates store INC`g'
    estat firststage
}

di _n "##################### A2. by COUNTRY SIZE #####################"
foreach g in 0 1 {
    di _n "==== size = `g'  (0=small,1=large) ===="
    ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y ///
        (ln_gaci_cwm = lnz) if lg_size==`g', vce(robust)
    estimates store SIZE`g'
    estat firststage
}

di _n "##################### A3. by PERIOD #####################"
foreach g in 0 1 {
    di _n "==== late = `g'  (0=1996-2009,1=2010-2023) ===="
    ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y ///
        (ln_gaci_cwm = lnz) if late==`g', vce(robust)
    estimates store PER`g'
    estat firststage
}

di _n "##################### A4. by CONNECTIVITY LEVEL #####################"
foreach g in 0 1 {
    di _n "==== hub = `g'  (0=low,1=high GACI_sum) ===="
    ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y ///
        (ln_gaci_cwm = lnz) if hub==`g', vce(robust)
    estimates store HUB`g'
    estat firststage
}

di _n "==== SPLIT-SAMPLE SUMMARY (coef on ln_gaci_cwm by subgroup) ===="
estimates table INC0 INC1 SIZE0 SIZE1 PER0 PER1 HUB0 HUB1, ///
    keep(ln_gaci_cwm) b(%9.4f) se(%9.4f) stats(N) ///
    title("Split-sample IV: openness effect of hub quality across subgroups")

*==============================================================================
* B) INTERACTION IV  (pooled; instrument BOTH the level and the interaction)
*    endogenous = ln_gaci_cwm , ln_gaci_cwm#moderator
*    instruments = lnz        , lnz#moderator
*    coef on the interaction term = heterogeneity test.  estat firststage = S-W F.
*==============================================================================
di _n "##################### B. INTERACTION IV #####################"

* --- B1 income ---
gen cwm_hi = ln_gaci_cwm*hi_inc
gen lnz_hi = lnz*hi_inc
di _n "==== B1 effect x income (cwm_hi = differential slope) ===="
ivregress 2sls trade_intensity lnpop deg_mean i.hi_inc i.regcode i.y ///
    (ln_gaci_cwm cwm_hi = lnz lnz_hi), vce(robust) first
estimates store IX_inc
estat firststage, all

* --- B2 size ---
gen cwm_lg = ln_gaci_cwm*lg_size
gen lnz_lg = lnz*lg_size
di _n "==== B2 effect x size ===="
ivregress 2sls trade_intensity lnpop deg_mean i.lg_size i.regcode i.y ///
    (ln_gaci_cwm cwm_lg = lnz lnz_lg), vce(robust) first
estimates store IX_size
estat firststage, all

* --- B3 period ---
gen cwm_lt = ln_gaci_cwm*late
gen lnz_lt = lnz*late
di _n "==== B3 effect x period (post-2010) ===="
ivregress 2sls trade_intensity lnpop deg_mean i.late i.regcode i.y ///
    (ln_gaci_cwm cwm_lt = lnz lnz_lt), vce(robust) first
estimates store IX_late
estat firststage, all

di _n "==== INTERACTION SUMMARY (differential slopes) ===="
estimates table IX_inc IX_size IX_late, ///
    keep(ln_gaci_cwm cwm_hi cwm_lg cwm_lt) b(%9.4f) se(%9.4f) stats(N) ///
    title("Interaction IV: differential openness effect (interaction = heterogeneity)")
