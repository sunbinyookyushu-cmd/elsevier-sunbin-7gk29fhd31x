*==============================================================================*
* Is air connectivity clean connectivity?  -- full replication of Tables 1-5 and Appendix A1-A3
* Data : gaci_cleanopen_final.dta  (built by export_final_stata.py; see CODEBOOK.md and DECISIONS.md)
* Needs: ssc install reghdfe ftools ivreg2 ivreghdfe ranktest estout b1x2   (run once)
* Run  : cd to this folder, then  do replicate_tables.do   -> tables in out/*.rtf, full log in out/replicate_tables.log
* Base : y = b ln GACI + ln pop + ln pc + (ln pc)^2 + country FE + year FE, SE clustered by country
* IV   : ln GACI instrumented by Feyrer-type air market access (feyrer_int)
*==============================================================================*
clear all
set more off
cap mkdir out
cap log close _all
log using "out/replicate_tables.log", replace text
use "gaci_cleanopen_final.dta", clear
keep if in_unified == 1                      // DECISION #1-#5 (DECISIONS.md)
egen cid = group(c)
xtset cid y
egen ry = group(region y)
egen cy = group(continent y)
egen sy = group(subregion y)
egen ty = group(inc_ter y)
egen regid = group(region)                  // numeric region id for region-specific trends
local X   "lnpop lnpc lnpc2"
local Y1  "ln_so2gdp ln_so2pc ln_noxgdp renew_sh renewables_share_elec ln_ci ln_co2pc ln_ei ln_ce"
local Yd  "ln_so2gdp ln_ei ln_ce ln_so2co2 ln_noxgdp ln_noxco2 ln_co2"
local Y2  "ln_coal_cons ln_so2_coal_cons ln_so2_oil_cons ln_so2_coal_ef ln_so2_oil_ef ln_so2_fossil_ef ln_so2_process so2_coal_sh"
local Y3  "ln_so2gdp ln_noxgdp renew_sh ln_ci ln_ei"
local Y4  "ln_so2gdp ln_noxgdp renew_sh ln_ci"

* ---- quick checks against the Python run (tables/_all_tables.txt) ----
*   unified sample: 4,516 obs (4,515 after singleton drop), 176 countries; within-SD of ln GACI = 0.075
*   T1 Panel A ln SO2/GDP: b(air) = -0.705 (SE 0.316);  Panel B 2SLS: -4.939 (2.037), KP F about 11-12
*   T1b identity: -0.705 = -0.152 + -0.019 + -0.535
count
qui tab cid
di as txt "countries: " r(r)
* within-country SD of ln GACI (for the 1-SD rows)
qui reghdfe air, absorb(cid y) resid(r_air)
qui sum r_air
di as txt "within-country SD of ln GACI = " %5.3f r(sd)

*---------------------------------------------------------------- T1 / T1b / T2 : Panel A OLS, Panel B 2SLS
foreach T in 1 1b 2 {
    if "`T'"=="1"  local YY "`Y1'"
    if "`T'"=="1b" local YY "`Yd'"
    if "`T'"=="2"  local YY "`Y2'"
    eststo clear
    foreach y of local YY {
        eststo A_`y': reghdfe `y' air `X', absorb(cid y) vce(cluster cid)
        eststo B_`y': ivreghdfe `y' (air = feyrer_int) `X', absorb(cid y) cluster(cid)
        estadd scalar KPF = e(widstat) : B_`y'
    }
    esttab A_* using "out/T`T'_panelA.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air lnpc lnpc2) stats(N N_clust, labels("N" "Countries")) title("Table `T' Panel A: OLS")
    esttab B_* using "out/T`T'_panelB.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air) stats(N KPF, labels("N" "KP first-stage F")) title("Table `T' Panel B: 2SLS")
}
* adding-up check for T1b (OLS): b(ln_so2gdp) = b(ln_ei)+b(ln_ce)+b(ln_so2co2)
foreach y in ln_so2gdp ln_ei ln_ce ln_so2co2 { qui reghdfe `y' air `X', absorb(cid y) vce(cluster cid); scalar b_`y' = _b[air] }
di as txt "T1b identity: " %6.3f b_ln_so2gdp " = " %6.3f b_ln_ei " + " %6.3f b_ln_ce " + " %6.3f b_ln_so2co2 "  (sum = " %6.3f b_ln_ei+b_ln_ce+b_ln_so2co2 ")"

*---------------------------------------------------------------- T3 : Gelbach decomposition (Panel A via b1x2; Panel B manual 2SLS)
local MED "manuf_sh serv_sh agr_sh trade_gdp_wdi fdi_in_gdp urban_sh"
foreach y of local Y3 {
    preserve
    keep if !missing(`y', air, lnpop, lnpc, feyrer_int, manuf_sh, serv_sh, agr_sh, trade_gdp_wdi, fdi_in_gdp, urban_sh)
    * Panel A
    b1x2 `y', x1all(air `X') x2all(`MED') x1only(air) ///
        x2delta(g1 = manuf_sh serv_sh agr_sh : g2 = trade_gdp_wdi fdi_in_gdp : g3 = urban_sh) absorb(cid y) cluster(cid)
    * Panel B: 2SLS base, 2SLS full, 2SLS auxiliaries -> delta_k = Gamma_k * gamma_k
    qui ivreghdfe `y' (air = feyrer_int) `X', absorb(cid y) cluster(cid)
    scalar bB = _b[air]
    qui ivreghdfe `y' (air = feyrer_int) `X' `MED', absorb(cid y) cluster(cid)
    scalar bF = _b[air]
    scalar tot = 0
    foreach m of local MED {
        scalar g_`m' = _b[`m']
        qui ivreghdfe `m' (air = feyrer_int) `X', absorb(cid y) cluster(cid)
        scalar d_`m' = _b[air]*g_`m'
        scalar tot = tot + d_`m'
    }
    di as txt "`y' IV Gelbach: base " %6.3f bB " full " %6.3f bF " explained " %6.3f bB-bF " = composition " %6.3f d_manuf_sh+d_serv_sh+d_agr_sh ///
        " + openness " %6.3f d_trade_gdp_wdi+d_fdi_in_gdp " + urban " %6.3f d_urban_sh "  [sum " %6.3f tot "]"
    restore
}

*---------------------------------------------------------------- T4 : heterogeneity
eststo clear
foreach y of local Y4 {
    eststo h_`y': reghdfe `y' air air_goods `X', absorb(cid y) vce(cluster cid)
    foreach t in low mid high {
        qui reghdfe `y' air `X' if inc_ter=="`t'", absorb(cid y) vce(cluster cid)
        di as txt "`y' tercile `t': " %6.3f _b[air] " (" %5.3f _se[air] ")"
    }
    * Panel B: split-sample IV
    qui ivreghdfe `y' (air = feyrer_int) `X' if goods_econ==1, absorb(cid y) cluster(cid)
    di as txt "`y' IV goods economies: " %6.3f _b[air] " (" %5.3f _se[air] ")  KP F " %4.1f e(widstat)
    qui ivreghdfe `y' (air = feyrer_int) `X' if goods_econ==0, absorb(cid y) cluster(cid)
    di as txt "`y' IV service economies: " %6.3f _b[air] " (" %5.3f _se[air] ")  KP F " %4.1f e(widstat)
}
esttab h_* using "out/T4_panelA.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air air_goods) stats(N N_clust)
* (Stata alternative with interaction IV, not possible in pyfixest):
* ivreghdfe ln_so2gdp (air air_goods = feyrer_int c.feyrer_int#c.goods_econ) `X', absorb(cid y) cluster(cid)

*---------------------------------------------------------------- T5 : IV diagnostics
eststo clear
foreach y of local Y4 {
    eststo o_`y':  reghdfe `y' air `X', absorb(cid y) vce(cluster cid)
    eststo rf_`y': reghdfe `y' feyrer_int `X', absorb(cid y) vce(cluster cid)
    eststo f_`y':  ivreghdfe `y' (air = feyrer_int) `X', absorb(cid y) cluster(cid)
    estadd scalar KPF = e(widstat) : f_`y'
    eststo me_`y': ivreghdfe `y' (air = gaci_mean) `X', absorb(cid y) cluster(cid)
    estadd scalar KPF = e(widstat) : me_`y'
    eststo b_`y':  ivreghdfe `y' (air = tourism_int feyrer_int) `X', absorb(cid y) cluster(cid)
    estadd scalar KPF = e(widstat) : b_`y'
    estadd scalar Jp  = e(jp)      : b_`y'
}
esttab o_* rf_* f_* me_* b_* using "out/T5.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air feyrer_int) stats(N KPF Jp, labels("N" "KP F" "Hansen J p"))

*---------------------------------------------------------------- A1 : robustness (SO2/GDP and CO2/GDP)
foreach y in ln_so2gdp ln_ci {
    eststo clear
    eststo r1:  reghdfe `y' air `X',                      absorb(cid y)  vce(cluster cid)
    eststo r2:  reghdfe `y' air `X' lnkl lnkl2,           absorb(cid y)  vce(cluster cid)
    eststo r3:  reghdfe `y' air `X' ln_sea_ma,            absorb(cid y)  vce(cluster cid)
    eststo r4:  reghdfe `y' air `X' ln_lsci if y>=2006,   absorb(cid y)  vce(cluster cid)
    eststo r5:  reghdfe `y' air `X',                      absorb(cid ry) vce(cluster cid)
    eststo r6:  reghdfe `y' air `X',                      absorb(cid cy) vce(cluster cid)
    eststo r7:  reghdfe `y' air `X',                      absorb(cid sy) vce(cluster cid)
    eststo r8:  reghdfe `y' air `X',                      absorb(cid y regid#c.trend) vce(cluster cid)
    eststo r9:  reghdfe `y' air `X',                      absorb(cid ty) vce(cluster cid)
    eststo r10: reghdfe `y' air `X' if !inlist(y,2020,2021), absorb(cid y) vce(cluster cid)
    eststo r11: reghdfe `y' air `X' if y<=2009,           absorb(cid y)  vce(cluster cid)
    eststo r12: reghdfe `y' air `X' if y>=2010,           absorb(cid y)  vce(cluster cid)
    eststo r13: reghdfe `y' air `X' if y<=2019,           absorb(cid y)  vce(cluster cid)
    if "`y'"=="ln_so2gdp" eststo r14: reghdfe ln_so2gdp_v22 air `X', absorb(cid y) vce(cluster cid)
    esttab r* using "out/A1_`y'.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air) stats(N N_clust) ///
        mtitles("base" "+K/L" "+sea MA" "+LSCI 06-" "region x yr" "continent x yr" "subregion x yr" "region trends" "tercile x yr" "excl 2020-21" "1996-2009" "2010-2023" "1996-2019" "CEDS2022")
}

*---------------------------------------------------------------- A2 : alternative aggregates
foreach y in ln_so2gdp ln_ci {
    foreach x in air gaci_cwmean gaci_mean {
        qui reghdfe `y' `x' `X', absorb(cid y) vce(cluster cid)
        di as txt "A2 `y' on `x': " %6.3f _b[`x'] " (" %5.3f _se[`x'] ")"
    }
}

*---------------------------------------------------------------- A3 : IV dropping one region
foreach r in AF AS EU LA ME SW {
    qui ivreghdfe ln_so2gdp (air = feyrer_int) `X' if region!="`r'", absorb(cid y) cluster(cid)
    di as txt "A3 drop `r': " %6.3f _b[air] " (" %5.3f _se[air] ")  KP F " %4.1f e(widstat) "  N " e(N)
}
cap log close _all
