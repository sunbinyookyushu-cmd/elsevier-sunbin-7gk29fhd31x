*------------------------------------------------------------------------------*
* 08: Is air openness clean openness?   air = ln GACI_cwm, sea = ln UNCTAD LSCI (2006-2023)
*   Input: stata/clean_open_panel.dta  (built by export_and_robust.py; variable names match analysis_v2_lsci.py)
*   Needs: reghdfe ivreghdfe ftools b1x2 estout   (ssc install ...)
*------------------------------------------------------------------------------*
clear all
use "clean_open_panel.dta", clear
egen cid = group(c)
xtset cid y
gen air = ln_gaci_cwm
gen sea = ln_lsci
keep if y >= 2006 & !missing(sea)                      // LSCI window; coastal countries (landlocked ~0.7%)

* ---------- Table 1: intensity outcomes, OLS FE / +income / 2SLS ----------
local Y1 ln_ci ln_ei ln_ce ln_co2pc ln_eint renew_sh
eststo clear
foreach y of local Y1 {
    eststo o_`y':  reghdfe `y' air sea lnpop,        absorb(cid y) vce(cluster cid)
    eststo i_`y':  reghdfe `y' air sea lnpop lnpc,   absorb(cid y) vce(cluster cid)
    eststo v_`y':  ivreghdfe `y' (air = tourism_int feyrer_int) sea lnpop lnpc, absorb(cid y) cluster(cid) first
}
esttab o_* i_* using "t1_intensity.rtf", replace se star(* .10 ** .05 *** .01) keep(air sea lnpc) b(3) ///
    stats(N N_clust, labels("N" "Countries")) title("Air vs sea connectivity: carbon and energy intensity, 2006-2023")

* ---------- Table 2: local pollutants (CEDS ends 2019) and PM2.5 ----------
local Y2 ln_so2gdp ln_noxgdp ln_pm25w
foreach y of local Y2 {
    eststo p_`y':  reghdfe `y' air sea lnpop lnpc,   absorb(cid y) vce(cluster cid)
    eststo pv_`y': ivreghdfe `y' (air = tourism_int feyrer_int) sea lnpop lnpc, absorb(cid y) cluster(cid)
}
esttab p_* pv_* using "t2_pollution.rtf", replace se star(* .10 ** .05 *** .01) keep(air sea) b(3) ///
    stats(N N_clust widstat jp, labels("N" "Countries" "KP F" "Hansen J p"))

* ---------- Table 3: within-SD scaling (report in text) ----------
foreach v in air sea {
    reghdfe `v', absorb(cid y) resid(r_`v')
    sum r_`v'
    di "within-SD `v' = " r(sd)
}

* ---------- Table 4: Gelbach decomposition of the air coefficient ----------
* mediators: income | composition (manuf serv agr shares) | openness (trade FDI) | urbanisation
foreach y in ln_ci ln_ei ln_ce ln_so2gdp ln_noxgdp {
    preserve
    keep if !missing(`y', air, sea, lnpop, lnpc, manuf_sh, serv_sh, agr_sh, trade_gdp_wdi, fdi_in_gdp, urban_sh)
    b1x2 `y', x1all(air sea lnpop) x2all(lnpc manuf_sh serv_sh agr_sh trade_gdp_wdi fdi_in_gdp urban_sh) ///
        x1only(air) x2delta(g1 = lnpc : g2 = manuf_sh serv_sh agr_sh : g3 = trade_gdp_wdi fdi_in_gdp : g4 = urban_sh) ///
        absorb(cid y) cluster(cid)
    restore
}

* ---------- Table 5: instrument-by-instrument + over-id ----------
foreach y in ln_ci ln_ce ln_so2gdp ln_noxgdp {
    ivreghdfe `y' (air = tourism_int) sea lnpop lnpc, absorb(cid y) cluster(cid)
    ivreghdfe `y' (air = feyrer_int)  sea lnpop lnpc, absorb(cid y) cluster(cid)
    ivreghdfe `y' (air = tourism_int feyrer_int) sea lnpop lnpc, absorb(cid y) cluster(cid)
    di "Hansen J p = " e(jp)
}

* ---------- Table 6: heterogeneity by 1996 income tercile ----------
foreach y in ln_ci ln_ce ln_so2gdp {
    foreach t in low mid high {
        reghdfe `y' air sea lnpop lnpc if inc_ter == "`t'", absorb(cid y) vce(cluster cid)
    }
}

* ---------- Table 7: Green TFP (global Malmquist-Luenberger, gtfp_ml.py) ----------
foreach y in ln_gtfp_co2 ln_gtfp_co2so2 ln_tfp_dea {
    reghdfe `y' air sea lnpop lnpc, absorb(cid y) vce(cluster cid)
}

* ---------- Robustness: sample vs measure (LSCI sample with geographic sea MA / no sea control) ----------
foreach y in ln_ci ln_ce ln_so2gdp {
    reghdfe `y' air ln_sea_ma lnpop lnpc, absorb(cid y) vce(cluster cid)
    reghdfe `y' air lnpop lnpc,            absorb(cid y) vce(cluster cid)
}
* Dynamic panel (Managi short vs long run): xtabond2 `y' L.`y' air sea lnpop lnpc i.y, gmm(L.`y', lag(2 4) collapse) iv(i.y tourism_int feyrer_int) twostep robust
