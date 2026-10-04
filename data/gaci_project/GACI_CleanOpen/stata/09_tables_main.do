*------------------------------------------------------------------------------*
* 09: core table set, air-only.  Base: y ~ ln GACI + ln pop + ln pc + (ln pc)^2 | country + year, cluster(country)
*     mirrors tables_main.py (T1-T5, A1-A2).  Input: clean_open_panel.dta ; needs reghdfe ivreghdfe estout b1x2
*------------------------------------------------------------------------------*
clear all
use "clean_open_panel.dta", clear
egen cid = group(c)
xtset cid y
gen air   = ln_gaci_cwm
gen lnpc2 = lnpc^2
gen merch96 = merch_share if y==1996
bys cid: egen m96 = max(merch96)
qui sum m96 if y==1996, d
gen goods = m96 > r(p50)
gen air_goods = air*goods

* T1 main
eststo clear
foreach y in ln_so2gdp ln_so2pc ln_noxgdp renew_sh ln_ci ln_ei ln_ce {
    eststo t1_`y': reghdfe `y' air lnpop lnpc lnpc2, absorb(cid y) vce(cluster cid)
}
esttab t1_* using "tables/T1.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air lnpc lnpc2) stats(N N_clust, labels("N" "Countries"))

* T2 technique: build emission factors first (CEDS SO2 by fuel / OWID CO2 by fuel) -> variables ln_so2_coal_ef etc. exported from Python
*   (tables_main.py writes them into the panel on request; here we assume they exist)
capture confirm variable ln_so2_coal_ef
if !_rc {
    eststo clear
    foreach y in ln_so2gdp ln_coal_co2 ln_so2_coal_ef ln_so2_oil_ef ln_so2_fossil_ef ln_so2_process so2_coal_sh {
        eststo t2_`y': reghdfe `y' air lnpop lnpc lnpc2, absorb(cid y) vce(cluster cid)
    }
    esttab t2_* using "tables/T2.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air) stats(N N_clust)
}

* T3 Gelbach (b1x2)
foreach y in ln_so2gdp ln_noxgdp renew_sh ln_ci ln_ei {
    preserve
    keep if !missing(`y', air, lnpop, lnpc, manuf_sh, serv_sh, agr_sh, trade_gdp_wdi, fdi_in_gdp, urban_sh)
    b1x2 `y', x1all(air lnpop lnpc lnpc2) x2all(manuf_sh serv_sh agr_sh trade_gdp_wdi fdi_in_gdp urban_sh) x1only(air) ///
        x2delta(g1 = manuf_sh serv_sh agr_sh : g2 = trade_gdp_wdi fdi_in_gdp : g3 = urban_sh) absorb(cid y) cluster(cid)
    restore
}

* T4 heterogeneity
eststo clear
foreach y in ln_so2gdp ln_noxgdp renew_sh ln_ci {
    eststo t4_`y': reghdfe `y' air air_goods lnpop lnpc lnpc2, absorb(cid y) vce(cluster cid)
    foreach t in low mid high {
        reghdfe `y' air lnpop lnpc lnpc2 if inc_ter=="`t'", absorb(cid y) vce(cluster cid)
    }
}
esttab t4_* using "tables/T4.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air air_goods) stats(N N_clust)

* T5 IV
eststo clear
foreach y in ln_so2gdp ln_noxgdp renew_sh ln_ci {
    eststo iv1_`y': ivreghdfe `y' (air = tourism_int) lnpop lnpc lnpc2, absorb(cid y) cluster(cid)
    eststo iv2_`y': ivreghdfe `y' (air = feyrer_int)  lnpop lnpc lnpc2, absorb(cid y) cluster(cid)
    eststo iv3_`y': ivreghdfe `y' (air = tourism_int feyrer_int) lnpop lnpc lnpc2, absorb(cid y) cluster(cid)
}
esttab iv* using "tables/T5.rtf", replace se star(* .10 ** .05 *** .01) b(3) keep(air) stats(N widstat jp, labels("N" "KP F" "Hansen J p"))

* A1 robustness (SO2/GDP and CO2/GDP)
gen region = substr(reg,1,2)
egen ry = group(region y)
egen ty = group(inc_ter y)
foreach y in ln_so2gdp ln_ci {
    reghdfe `y' air lnpop lnpc lnpc2,                     absorb(cid y)  vce(cluster cid)
    reghdfe `y' air lnpop lnpc lnpc2 ln_sea_ma,           absorb(cid y)  vce(cluster cid)
    reghdfe `y' air lnpop lnpc lnpc2 ln_lsci if y>=2006,  absorb(cid y)  vce(cluster cid)
    reghdfe `y' air lnpop lnpc lnpc2,                     absorb(cid ry) vce(cluster cid)
    reghdfe `y' air lnpop lnpc lnpc2,                     absorb(cid ty) vce(cluster cid)
    reghdfe `y' air lnpop lnpc lnpc2 if y<=2009,          absorb(cid y)  vce(cluster cid)
    reghdfe `y' air lnpop lnpc lnpc2 if y>=2010,          absorb(cid y)  vce(cluster cid)
}
