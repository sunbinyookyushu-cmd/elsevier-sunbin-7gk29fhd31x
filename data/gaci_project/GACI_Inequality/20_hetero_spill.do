* 20_hetero_spill.do : heterogeneity and spillover analyses in the form of the CO2 paper, applied to inequality.
* Specification: ln pop, country + year FE, Feyrer IV, country-clustered SE. No behavioural controls.
* Heterogeneity (block H): split-sample 2SLS by baseline income tercile, baseline connectivity tercile,
*   baseline market-Gini tercile; pooled top-tercile interaction; temporal split; macro region.
* Spillover (block S): neighbour exposure from ../GACI_CO2/spillover_bands.csv (leave-out means of other
*   countries' ln GACI_cwm, nbr_g_*, and of their Feyrer shifters, nbr_f_*): own-controlled, joint IV under
*   alternative W, distance bands, kernel grid, within/outside sub-region and aviation bloc, sub-region x year FE.
* Outputs: _hetero_co2form_results.csv, _spill_results.csv
capture log close _all
log using "20_hetero_spill_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "../GACI_CO2/spillover_bands.csv", clear varnames(1) encoding("utf-8")
ds c subregion unregion bloc, not
destring `r(varlist)', replace force
tempfile sb
save `sb'
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `sb', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
gen cont = substr(reg,1,2)
encode cont, gen(contid)
foreach k in EU AS AF LA ME {
    gen byte is_`k' = cont == "`k'"
}
encode subregion, gen(srid)
egen sry = group(srid y)
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
capture drop ln_spt_b50
gen ln_spt_b50 = ln_apt_b50 - ln_apt_all

* ---- baseline groupings (earliest observed value per country) ----
bysort isocode (y): gen byte first_pc = sum(!missing(lnpc)) == 1 & !missing(lnpc)
gen pc0_ = lnpc if first_pc
bysort isocode (pc0_): gen lnpc0 = pc0_[1]
drop pc0_ first_pc
bysort isocode (y): gen byte first_g = sum(!missing(gaci_max)) == 1 & !missing(gaci_max)
gen g0_ = gaci_max if first_g
bysort isocode (g0_): gen gaci0 = g0_[1]
drop g0_ first_g
bysort isocode (y): gen byte first_q = sum(!missing(gini_mkt)) == 1 & !missing(gini_mkt)
gen q0_ = gini_mkt if first_q
bysort isocode (q0_): gen gini0 = q0_[1]
drop q0_ first_q
preserve
bysort isocode: keep if _n == 1
xtile inc3 = lnpc0, nq(3)
xtile con3 = gaci0, nq(3)
xtile gin3 = gini0, nq(3)
keep isocode inc3 con3 gin3
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

tempname H
file open `H' using "_hetero_co2form_results.csv", write replace
file write `H' "panel,group,outcome,b,se,p,kpf,N,Nc" _n

capture program drop runcell
program define runcell
    args fh panel grp yv cond
    quietly count if `cond' & !missing(`yv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 60 {
        di as err "SKIP `panel' `grp' `yv': N = " r(N)
        exit
    }
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if `cond', absorb(isocode y) cluster(isocode)
    if _rc exit
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    quietly levelsof isocode if e(sample), local(cc)
    local nc : word count `cc'
    file write `fh' "`panel',`grp',`yv',`b',`se',`p',`=e(widstat)',`=e(N)',`nc'" _n
end

foreach yv in ln_gini_mkt ln_gini_disp ln_apt_top_bot ln_apt_d10 ln_spt_b50 {
    * A) baseline income terciles
    runcell `H' "A_income" "inc_low" `yv' "inc3 == 1"
    runcell `H' "A_income" "inc_mid" `yv' "inc3 == 2"
    runcell `H' "A_income" "inc_high" `yv' "inc3 == 3"
    capture drop hi_ ma_x_ iv_x_
    gen byte hi_ = inc3 == 3 if !missing(inc3)
    gen ma_x_ = ln_gaci_max * hi_
    gen iv_x_ = feyrer_int * hi_
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max ma_x_ = feyrer_int iv_x_), absorb(isocode y) cluster(isocode)
    if _rc == 0 file write `H' "A_income,interact_top_x_gaci,`yv',`=_b[ma_x_]',`=_se[ma_x_]',`=2*normal(-abs(_b[ma_x_]/_se[ma_x_]))',`=e(widstat)',`=e(N)',." _n
    * B) baseline connectivity terciles
    runcell `H' "B_conn" "con_low" `yv' "con3 == 1"
    runcell `H' "B_conn" "con_mid" `yv' "con3 == 2"
    runcell `H' "B_conn" "con_high" `yv' "con3 == 3"
    capture drop hi_ ma_x_ iv_x_
    gen byte hi_ = con3 == 3 if !missing(con3)
    gen ma_x_ = ln_gaci_max * hi_
    gen iv_x_ = feyrer_int * hi_
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max ma_x_ = feyrer_int iv_x_), absorb(isocode y) cluster(isocode)
    if _rc == 0 file write `H' "B_conn,interact_top_x_gaci,`yv',`=_b[ma_x_]',`=_se[ma_x_]',`=2*normal(-abs(_b[ma_x_]/_se[ma_x_]))',`=e(widstat)',`=e(N)',." _n
    * C) baseline market-Gini terciles
    runcell `H' "C_gini" "gini_low" `yv' "gin3 == 1"
    runcell `H' "C_gini" "gini_mid" `yv' "gin3 == 2"
    runcell `H' "C_gini" "gini_high" `yv' "gin3 == 3"
    capture drop hi_ ma_x_ iv_x_
    gen byte hi_ = gin3 == 3 if !missing(gin3)
    gen ma_x_ = ln_gaci_max * hi_
    gen iv_x_ = feyrer_int * hi_
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max ma_x_ = feyrer_int iv_x_), absorb(isocode y) cluster(isocode)
    if _rc == 0 file write `H' "C_gini,interact_top_x_gaci,`yv',`=_b[ma_x_]',`=_se[ma_x_]',`=2*normal(-abs(_b[ma_x_]/_se[ma_x_]))',`=e(widstat)',`=e(N)',." _n
    * D) temporal split
    runcell `H' "D_time" "full" `yv' "1"
    runcell `H' "D_time" "1996_2007" `yv' "y <= 2007"
    runcell `H' "D_time" "2010_2023_ex2020_21" `yv' "y >= 2010 & !inlist(y, 2020, 2021)"
    runcell `H' "D_time" "2010_2023" `yv' "y >= 2010"
    runcell `H' "D_time" "excl_2020_2023" `yv' "y <= 2019"
    * E) macro regions
    runcell `H' "E_region" "Europe" `yv' "is_EU == 1"
    runcell `H' "E_region" "Asia" `yv' "is_AS == 1"
    runcell `H' "E_region" "Africa" `yv' "is_AF == 1"
    runcell `H' "E_region" "LatAm" `yv' "is_LA == 1"
    runcell `H' "E_region" "MiddleEast" `yv' "is_ME == 1"
    runcell `H' "E_region" "excl_Europe" `yv' "is_EU == 0"
    runcell `H' "E_region" "excl_LatAm" `yv' "is_LA == 0"
}
file close `H'

* =====================================================================
* Spillovers
* =====================================================================
tempname S
file open `S' using "_spill_results.csv", write replace
file write `S' "panel,item,var,outcome,b,se,p,kpf,N" _n
capture program drop postone
program define postone
    args fh panel item v yv
    local bb = _b[`v']
    local sse = _se[`v']
    local pp = 2*normal(-abs(`bb'/`sse'))
    file write `fh' "`panel',`item',`v',`yv',`bb',`sse',`pp',`=e(widstat)',`=e(N)'" _n
end

foreach yv in ln_gini_mkt ln_gini_disp ln_apt_top_bot {
    * A1 own as exogenous control, neighbour instrumented (inverse distance)
    capture noisily ivreghdfe `yv' ln_gaci_max lnpop (nbr_g_inv = nbr_f_inv), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        postone `S' A own_exog_control nbr_g_inv `yv'
        postone `S' A own_exog_control ln_gaci_max `yv'
    }
    * A2 hybrid: own shifter in reduced form
    capture noisily ivreghdfe `yv' feyrer_int lnpop (nbr_g_inv = nbr_f_inv), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        postone `S' A hybrid_rf_control nbr_g_inv `yv'
        postone `S' A hybrid_rf_control feyrer_int `yv'
    }
    * A3 joint IV under alternative W (own instrumented by own shifter, neighbour by neighbours' shifters)
    foreach W in inv contig knn5 b1 k500 k1000 {
        capture noisily ivreghdfe `yv' lnpop has_contig (ln_gaci_max nbr_g_`W' = feyrer_int nbr_f_`W'), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            postone `S' A joint_`W' ln_gaci_max `yv'
            postone `S' A joint_`W' nbr_g_`W' `yv'
        }
    }
    * A4 single-endogenous neighbour effect under each W, hybrid control
    foreach W in inv contig knn5 b1 k500 k1000 {
        capture noisily ivreghdfe `yv' feyrer_int lnpop has_contig (nbr_g_`W' = nbr_f_`W'), absorb(isocode y) cluster(isocode)
        if _rc == 0 postone `S' A single_`W' nbr_g_`W' `yv'
    }
    * B distance bands jointly and singly; kernel grid
    capture noisily ivreghdfe `yv' feyrer_int lnpop has_b1 has_b2 has_b3 has_b4 has_b5 (nbr_g_b1 nbr_g_b2 nbr_g_b3 nbr_g_b4 nbr_g_b5 = nbr_f_b1 nbr_f_b2 nbr_f_b3 nbr_f_b4 nbr_f_b5), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        foreach b in b1 b2 b3 b4 b5 {
            postone `S' B bands_joint nbr_g_`b' `yv'
        }
    }
    foreach b in contig b1 b2 b3 b4 b5 {
        capture noisily ivreghdfe `yv' feyrer_int lnpop has_`b' (nbr_g_`b' = nbr_f_`b'), absorb(isocode y) cluster(isocode)
        if _rc == 0 postone `S' B band_single nbr_g_`b' `yv'
    }
    foreach lam in 250 500 1000 2000 5000 {
        capture noisily ivreghdfe `yv' feyrer_int lnpop (nbr_g_k`lam' = nbr_f_k`lam'), absorb(isocode y) cluster(isocode)
        if _rc == 0 postone `S' B kernel nbr_g_k`lam' `yv'
    }
    * C regional: within vs outside sub-region / bloc; sub-region x year FE with contiguity
    capture noisily ivreghdfe `yv' feyrer_int lnpop has_inreg (nbr_g_inreg nbr_g_outreg = nbr_f_inreg nbr_f_outreg), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        postone `S' C subregion_inout nbr_g_inreg `yv'
        postone `S' C subregion_inout nbr_g_outreg `yv'
    }
    capture noisily ivreghdfe `yv' feyrer_int lnpop has_inbloc (nbr_g_inbloc nbr_g_outbloc = nbr_f_inbloc nbr_f_outbloc), absorb(isocode y) cluster(isocode)
    if _rc == 0 {
        postone `S' C bloc_inout nbr_g_inbloc `yv'
        postone `S' C bloc_inout nbr_g_outbloc `yv'
    }
    capture noisily ivreghdfe `yv' lnpop has_contig (ln_gaci_max nbr_g_contig = feyrer_int nbr_f_contig), absorb(isocode sry) cluster(isocode)
    if _rc == 0 {
        postone `S' C contig_joint_subregXyear ln_gaci_max `yv'
        postone `S' C contig_joint_subregXyear nbr_g_contig `yv'
    }
    capture noisily ivreghdfe `yv' feyrer_int lnpop has_contig (nbr_g_contig = nbr_f_contig), absorb(isocode sry) cluster(isocode)
    if _rc == 0 postone `S' C contig_hybrid_subregXyear nbr_g_contig `yv'
}
file close `S'
log close _all
