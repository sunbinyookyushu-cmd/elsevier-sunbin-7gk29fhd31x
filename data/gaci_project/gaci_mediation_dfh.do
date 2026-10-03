*==============================================================================
* gaci_mediation_dfh.do
* IV-MEDIATION via the OFFICIAL ivmediate command
*   (Dippel, Ferrara & Heblich 2020, Stata Journal 20(3) 613-626, st0611;
*    single instrument identifies BOTH treatment and mediation effects
*    under the assumption that T-Y and M-Y confounders align).
* Companion to gaci_mediation.do (manual 3-step, incl. joint mediators):
*   ivmediate takes ONE mediator at a time but delivers proper CIs for the
*   total / direct / indirect effects and the mediated share.
* Setup: Y in {openness, volume}; T = ln_gaci_cwm; Z = tourism_int;
*   M in {r_bec = ln(interm/consum), r_vw = ln(hi/lo value-weight)}.
*   FE: country via absorb(), year via i.y dummies (absorb takes 1 var).
*   Samples: FULL 1996-2023 = MAIN (same as headline Table 1) and
*            robustness dropping 2020-21 only (acute pandemic years);
*            common samples as in gaci_mediation.do.
* Input : gaci_panel_mechanism.csv
* Output: gaci_mediation_dfh.log
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
capture log close _all
log using "gaci_mediation_dfh.log", replace text

import delimited "gaci_panel_mechanism.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

* ---- outcomes and mediators ----
gen g_int = merch_intensity                       // openness  ln(g/Y)
gen g_vol = merch_intensity + lngdp               // volume    ln g
gen r_bec = ln_tr_interm - ln_tr_consum           // M1: GVC composition
gen r_vw  = ln_tr_hivw   - ln_tr_lovw             // M2: value/weight comp.

* ---- common estimation samples ----
gen byte obsok  = !missing(g_int, g_vol, r_bec, r_vw, ///
                  ln_gaci_cwm, tourism_int, lnpop)
gen byte sfull  = obsok                             // MAIN: full 1996-2023
gen byte sdrop  = obsok & !inlist(y, 2020, 2021)    // robustness: drop acute
count if sfull
count if sdrop

* ---- package ----
capture which ivmediate
if _rc {
    ssc install ivmediate, replace
}

* =====================================================================
* ivmediate: sample x Y x M grid  (full = show intermediate regressions)
* =====================================================================
foreach s in sfull sdrop {
    local slab = cond("`s'"=="sfull", "FULL 1996-2023 MAIN", "drop 2020-21 acute-pandemic")
    foreach yv in g_int g_vol {
        foreach m in r_bec r_vw {
            di _n "================================================================"
            di    " ivmediate: Y = `yv'   M = `m'   (`slab', robust)"
            di    "================================================================"
            ivmediate `yv' lnpop i.y if `s', ///
                mediator(`m') treatment(ln_gaci_cwm) instrument(tourism_int) ///
                absorb(isocode) vce(robust) full
        }
    }
}

* cluster-robust variant for the headline pair (openness x GVC mediator)
di _n "================================================================"
di    " ivmediate: Y = g_int   M = r_bec   FULL sample, vce(cluster isocode)"
di    "================================================================"
ivmediate g_int lnpop i.y if sfull, ///
    mediator(r_bec) treatment(ln_gaci_cwm) instrument(tourism_int) ///
    absorb(isocode) vce(cluster isocode) full

di _n "DONE_MEDIATION_DFH"
log close
