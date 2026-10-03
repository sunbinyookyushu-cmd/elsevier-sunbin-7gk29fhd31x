*------------------------------------------------------------------------------*
* 08: Is air openness clean openness?  Managi et al. (2009) design with air vs sea connectivity
*   Inputs: $PROC/clean_open_panel.dta (c y ln_gaci_cwm ln_lsci ln_sea_ma lnpc lnpop tourism_int feyrer_int
*           ln_ci ln_ei ln_ce ln_so2pc ln_pm25 manuf_sh services_sh dirty_sh trade_share)
*------------------------------------------------------------------------------*
use "$PROC/clean_open_panel.dta", clear
egen cid = group(c)
* (1) OLS FE, (2) + income, (3) 2SLS air instrumented (tourism_int feyrer_int), sea instrumented by sea market access
foreach y in ln_ci ln_ei ln_ce ln_so2pc ln_pm25 dirty_sh {
    reghdfe   `y' ln_gaci_cwm ln_lsci lnpop,       absorb(cid y) vce(robust)
    reghdfe   `y' ln_gaci_cwm ln_lsci lnpop lnpc,  absorb(cid y) vce(robust)
    ivreghdfe `y' (ln_gaci_cwm ln_lsci = tourism_int feyrer_int ln_sea_ma) lnpop lnpc, absorb(cid y) robust first
}
* (4) composition channel: Gelbach decomposition of the air coefficient (ssc install b1x2)
reghdfe ln_ci ln_gaci_cwm ln_lsci lnpop lnpc, absorb(cid y) vce(robust)
b1x2 ln_ci, x1all(ln_gaci_cwm ln_lsci lnpop lnpc) x2all(manuf_sh dirty_sh services_sh trade_share) x1only(ln_gaci_cwm) ///
     x2delta(manuf_sh dirty_sh services_sh trade_share) absorb(cid y)
* (5) heterogeneity by baseline income tercile; (6) dynamic: xtabond2 with lagged outcome (Managi short vs long run)
