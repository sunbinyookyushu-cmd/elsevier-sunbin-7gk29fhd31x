*------------------------------------------------------------------------------*
* 03: SIMPLE MODEL — airport-level difference-in-differences
*
*   y_at = beta * Tax_c(a),t + alpha_a + lambda_r(a),t + e_at           (1)
*
*   y      : ln seats, ln GACI (and GACI components)
*   Tax    : 1 if airport a's country taxes tickets in year t (>= 6 months)   [binary, headline]
*            or economy per-pax rate in EUR on the shortest band              [dose, robustness]
*   alpha_a: airport FE;  lambda_rt: OAG-region x year FE (absorbs regional demand, fuel price, COVID)
*   SE clustered by country (treatment level). Sample: European-neighbourhood airports, insample==1.
*
*   Event study: replace Tax with leads/lags of first_tax (binned at -5/+8), omit t = -1.
*   Leakage   : Spill_at = 1 if a is in an UNTAXED country and some taxing country's airport is
*               within 300 km in year t (precomputed distances, data/processed/airport_nearest_foreign_country_km.csv)
*------------------------------------------------------------------------------*
use "$PROC/airport_panel.dta", clear
merge m:1 iso_country year using "$PROC/tax_country_year.dta", keep(1 3) nogen
replace tax_any = 0 if missing(tax_any)
foreach v in tax_short_eur tax_long_eur { 
    replace `v' = 0 if missing(`v') 
}
* Europe + neighbourhood sample (same box as script 08)
keep if inrange(lat, 30, 72) & inrange(lon, -30, 60)
keep if insample

*--- Leakage ring --------------------------------------------------------------
preserve
    import delimited "$PROC/airport_nearest_foreign_country_km.csv", clear varnames(1) case(preserve)
    rename (Airport iso_country) (airport own_iso)
    keep airport foreign_iso km
    rename foreign_iso iso_country
    joinby iso_country using "$PROC/tax_country_year.dta", unmatched(none)
    keep if tax_any == 1 & km <= 300
    collapse (min) km_to_taxed = km, by(airport year)
    gen spill300 = 1
    tempfile spill
    save `spill'
restore
merge 1:1 airport year using `spill', keep(1 3) nogen
replace spill300 = 0 if missing(spill300) | tax_any == 1    // only untaxed airports can be spillover airports

*--- Event time ---------------------------------------------------------------
gen et = year - first_tax
replace et = -5 if et < -5 & !missing(et)
replace et =  8 if et >  8 & !missing(et)
forvalues k = 5(-1)2 {
    gen ev_m`k' = (et == -`k')
}
forvalues k = 0/8 {
    gen ev_p`k' = (et == `k')
}
* (omitted: et == -1; never-treated airports have all ev_* = 0)

*--- Estimation ----------------------------------------------------------------
eststo clear
foreach y in ln_seats ln_gaci ln_deg {
    eststo `y'_bin : reghdfe `y' tax_any spill300,       absorb(aid rid#year) vce(cluster iso_country)
    eststo `y'_dose: reghdfe `y' tax_short_eur spill300, absorb(aid rid#year) vce(cluster iso_country)
    eststo `y'_es  : reghdfe `y' ev_m5 ev_m4 ev_m3 ev_m2 ev_p0-ev_p8 spill300, absorb(aid rid#year) vce(cluster iso_country)
}
esttab *_bin *_dose using "$OUT/table_airport_did.csv", replace se star(* 0.10 ** 0.05 *** 0.01) ///
    keep(tax_any tax_short_eur spill300) b(3) label title("Airport-level DiD: ticket taxes, seats and connectivity")
esttab *_es using "$OUT/table_event_study.csv", replace se b(3) keep(ev_*)

*--- Event-study plot (ln seats) -----------------------------------------------
est restore ln_seats_es
coefplot, keep(ev_*) vertical yline(0) xline(4.5, lpattern(dash)) ///
    rename(ev_m5="-5" ev_m4="-4" ev_m3="-3" ev_m2="-2" ev_p0="0" ev_p1="1" ev_p2="2" ev_p3="3" ev_p4="4" ev_p5="5" ev_p6="6" ev_p7="7" ev_p8="8") ///
    ytitle("Effect on ln seats") xtitle("Years since ticket tax introduced") ciopts(recast(rcap))
graph export "$OUT/fig_event_study_seats.pdf", replace

*--- Robustness (keep it short) ------------------------------------------------
* (a) weight by baseline seats so the estimate speaks to passenger-weighted exposure
bys aid (year): gen seats0 = seats[1]
reghdfe ln_seats tax_any spill300 [aw = seats0], absorb(aid rid#year) vce(cluster iso_country)
* (b) drop COVID years (treated countries' recovery paths differ from Southern Europe's)
reghdfe ln_seats tax_any spill300 if !inrange(year, 2020, 2022), absorb(aid rid#year) vce(cluster iso_country)
* (c) few treated clusters (~9 countries): wild-cluster bootstrap p-values   (ssc install boottest)
reghdfe ln_seats tax_any spill300, absorb(aid rid#year) vce(cluster iso_country)
boottest tax_any, reps(9999) seed(1234) nograph
* (d) staggered-DiD robust estimator (ssc install csdid / did_imputation) — treatment = first_tax, never-treated controls
*     did_imputation ln_seats aid year first_tax, fe(aid rid#year) cluster(iso_country) autosample

*--- Heterogeneity: hubs vs non-hubs (baseline GACI tercile, 1996 or first year) ----------------------
bys aid (year): gen gaci0 = GACI[1]
xtile hubq = gaci0, nq(3)
reghdfe ln_seats c.tax_any#i.hubq spill300, absorb(aid rid#year) vce(cluster iso_country)
