*==============================================================================
* gaci_mediation.do
* IV-MEDIATION (manual 3-step, Dippel-Ferrara-Heblich 2020 SJ logic):
*   how much of the connectivity -> trade effect flows through the
*   composition mediators?
*     M1 = r_bec = ln(intermediates/consumption)   [GVC channel]
*     M2 = r_vw  = ln(high/low value-to-weight)    [belly-cargo channel]
*   Steps per outcome Y in {openness g_int, volume g_vol}:
*     (1) TOTAL   : 2SLS Y on T (T = ln_gaci_cwm, Z = tourism_int)
*     (2) ON MED  : 2SLS M on T                    (effect on mediator)
*     (3) DIRECT  : 2SLS Y on T + M as control     (M NOT instrumented; the
*                   DFH single-IV assumption: T-Y and M-Y confounders align)
*     mediated share = 1 - beta_direct/beta_total
*   Joint (both mediators) done HERE; single-mediator official CIs in
*   gaci_mediation_dfh.do (ivmediate command).
*   Samples: FULL 1996-2023 = MAIN (same as headline Table 1) and
*            robustness dropping 2020-21 only (acute pandemic years, when
*            the tourism instrument and composition move jointly).
*   PILOT (python, same spec): FULL openness total 1.302 (= headline) ->
*   both mediators 23.6% mediated (bec 16.6, vw 4.3).
* Spec: ivreghdfe, country+year FE, lnpop control, robust SE (house style).
* Input : gaci_panel_mechanism.csv
* Output: gaci_mediation.log + _mediation_results.rtf/.csv
*==============================================================================
clear all
set more off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/ext2024"
capture log close _all
log using "gaci_mediation_run.log", replace text

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

* ---- common estimation samples (fair share comparisons) ----
gen byte obsok  = !missing(g_int, g_vol, r_bec, r_vw, ///
                  ln_gaci_cwm, tourism_int, lnpop)
gen byte sfull  = obsok                             // MAIN: full 1996-2023
gen byte sdrop  = obsok & !inlist(y, 2020, 2021)    // robustness: drop acute
count if sfull
count if sdrop

* ---- packages ----
capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}
capture which esttab
if _rc {
    ssc install estout, replace
}

eststo clear
local tr ln_gaci_cwm

* =====================================================================
* step (2): effect of T on each mediator, both samples
* =====================================================================
foreach s in sfull sdrop {
    foreach m in r_bec r_vw {
        ivreghdfe `m' lnpop (`tr' = tourism_int) if `s', absorb(isocode y) robust
        eststo med_`m'_`s'
        estadd scalar KPF = e(widstat)
    }
}

* =====================================================================
* steps (1)+(3) per outcome x sample; collect mediated shares
* =====================================================================
foreach s in sfull sdrop {
    foreach yv in g_int g_vol {

        * (1) total effect
        ivreghdfe `yv' lnpop (`tr' = tourism_int) if `s', absorb(isocode y) robust
        eststo tot_`yv'_`s'
        estadd scalar KPF = e(widstat)
        scalar bt_`yv'_`s' = _b[`tr']

        * (3) direct effects: mediator(s) as controls, T still instrumented
        ivreghdfe `yv' lnpop r_bec (`tr' = tourism_int) if `s', absorb(isocode y) robust
        eststo d1_`yv'_`s'
        estadd scalar KPF = e(widstat)
        scalar b1_`yv'_`s' = _b[`tr']
        estadd scalar MSHARE = 100*(1 - b1_`yv'_`s'/bt_`yv'_`s')

        ivreghdfe `yv' lnpop r_vw (`tr' = tourism_int) if `s', absorb(isocode y) robust
        eststo d2_`yv'_`s'
        estadd scalar KPF = e(widstat)
        scalar b2_`yv'_`s' = _b[`tr']
        estadd scalar MSHARE = 100*(1 - b2_`yv'_`s'/bt_`yv'_`s')

        ivreghdfe `yv' lnpop r_bec r_vw (`tr' = tourism_int) if `s', absorb(isocode y) robust
        eststo d3_`yv'_`s'
        estadd scalar KPF = e(widstat)
        scalar b3_`yv'_`s' = _b[`tr']
        estadd scalar MSHARE = 100*(1 - b3_`yv'_`s'/bt_`yv'_`s')
    }
}

* =====================================================================
* TABLES
* =====================================================================
local opt b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) nonum ///
          coeflabels(`tr' "Hub quality (cwm)" r_bec "M: ln(Int/Cons)" ///
                     r_vw "M: ln(Hi/Lo VW)") ///
          stats(MSHARE KPF N, fmt(%9.1f %9.1f %9.0g) ///
          labels("Mediated share (%)" "First-stage KP F" "Observations"))

di _n "========== STEP 2: EFFECT OF CONNECTIVITY ON MEDIATORS =========="
esttab med_r_bec_sfull med_r_vw_sfull med_r_bec_sdrop med_r_vw_sdrop, ///
       keep(`tr') mtitles("bec FULL" "vw FULL" "bec drop2021" "vw drop2021") `opt'

foreach s in sfull sdrop {
    local slab = cond("`s'"=="sfull", "FULL 1996-2023 (MAIN)", "drop 2020-21 (acute pandemic)")

    di _n "========== MEDIATION, Y = OPENNESS ln(g/Y), `slab' =========="
    di      "  cols: total / direct|M=bec / direct|M=vw / direct|both"
    esttab tot_g_int_`s' d1_g_int_`s' d2_g_int_`s' d3_g_int_`s', ///
           keep(`tr' r_bec r_vw) mtitles("Total" "M:bec" "M:vw" "M:both") `opt'

    di _n "========== MEDIATION, Y = VOLUME ln(g), `slab' =========="
    esttab tot_g_vol_`s' d1_g_vol_`s' d2_g_vol_`s' d3_g_vol_`s', ///
           keep(`tr' r_bec r_vw) mtitles("Total" "M:bec" "M:vw" "M:both") `opt'
}

di _n "========== MEDIATED SHARES (point estimates) =========="
foreach s in sfull sdrop {
    foreach yv in g_int g_vol {
        di "`s' `yv': total=" %6.3f bt_`yv'_`s' ///
           "  bec " %5.1f 100*(1-b1_`yv'_`s'/bt_`yv'_`s') "%" ///
           "  vw "  %5.1f 100*(1-b2_`yv'_`s'/bt_`yv'_`s') "%" ///
           "  both " %5.1f 100*(1-b3_`yv'_`s'/bt_`yv'_`s') "%"
    }
}

* ---------- RTF + CSV ----------
esttab tot_g_int_sfull d1_g_int_sfull d2_g_int_sfull d3_g_int_sfull ///
       tot_g_int_sdrop d1_g_int_sdrop d2_g_int_sdrop d3_g_int_sdrop ///
       using "_mediation_results.rtf", replace ///
       b(%9.3f) se(%9.3f) star(* 0.10 ** 0.05 *** 0.01) label nonum ///
       keep(`tr' r_bec r_vw) ///
       coeflabels(`tr' "Hub quality (cwm)" r_bec "M: ln(Int/Cons)" ///
                  r_vw "M: ln(Hi/Lo VW)") ///
       mtitles("Total" "M:bec" "M:vw" "M:both" "Total" "M:bec" "M:vw" "M:both") ///
       stats(MSHARE KPF N, fmt(%9.1f %9.1f %9.0g) ///
       labels("Mediated share (%)" "First-stage KP F" "N")) ///
       title("IV mediation, Y = openness. Cols 1-4 FULL 1996-2023 (main), 5-8 drop 2020-21.")

esttab tot_g_int_sfull d1_g_int_sfull d2_g_int_sfull d3_g_int_sfull ///
       tot_g_vol_sfull d1_g_vol_sfull d2_g_vol_sfull d3_g_vol_sfull ///
       tot_g_int_sdrop d1_g_int_sdrop d2_g_int_sdrop d3_g_int_sdrop ///
       tot_g_vol_sdrop d1_g_vol_sdrop d2_g_vol_sdrop d3_g_vol_sdrop ///
       med_r_bec_sfull med_r_vw_sfull ///
       using "_mediation_results.csv", replace ///
       b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
       keep(`tr' r_bec r_vw) stats(MSHARE KPF N) plain

di _n "DONE_MEDIATION"
log close
