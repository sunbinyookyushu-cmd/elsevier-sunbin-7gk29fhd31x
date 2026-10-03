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

*--- Treatment geography (Li et al. 2019 analogue: treated / spillover ring / buffer dropped / control) ----
*   km_to_taxed_at = distance from airport a to the nearest commercial airport of ANY country taxing in year t
preserve
    import delimited "$PROC/airport_nearest_foreign_country_km.csv", clear varnames(1) case(preserve)
    rename (Airport iso_country) (airport own_iso)
    keep airport foreign_iso km
    rename foreign_iso iso_country
    joinby iso_country using "$PROC/tax_country_year.dta", unmatched(none)
    keep if tax_any == 1
    gen double p = tax_short_eur / max(km, 50)^2 * 1e4          // distance-decay neighbour tax pressure
    collapse (min) km_to_taxed = km (sum) nbr_tax_pressure = p, by(airport year)
    tempfile geo
    save `geo'
restore
merge 1:1 airport year using `geo', keep(1 3) nogen
replace nbr_tax_pressure = 0 if missing(nbr_tax_pressure)
gen spill150 = tax_any == 0 & km_to_taxed <= 150                        // leakage group
gen buffer   = tax_any == 0 & km_to_taxed >  150 & km_to_taxed <= 300   // misclassification zone -> dropped
label var spill150 "Untaxed airport within 150 km of a taxing country"
label var nbr_tax_pressure "Sum over taxing neighbours of rate/(km^2) x 1e4"
drop if buffer                                                          // control = untaxed airports > 300 km away
gen yrs_since = cond(tax_any == 1, max(year - first_tax, 0), 0)
bys iso_country: egen ever_treated = max(tax_any)

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
foreach y in ln_co2 ln_co2_intl ln_co2_seat ln_stage ln_seats ln_gaci ln_deg {
    eststo `y'_bin : reghdfe `y' tax_any spill150,       absorb(aid rid#year) vce(cluster iso_country)
    eststo `y'_dose: reghdfe `y' tax_short_eur nbr_tax_pressure, absorb(aid rid#year) vce(cluster iso_country)
    eststo `y'_es  : reghdfe `y' ev_m5 ev_m4 ev_m3 ev_m2 ev_p0-ev_p8 spill150, absorb(aid rid#year) vce(cluster iso_country)
}
esttab *_bin *_dose using "$OUT/table_airport_did.csv", replace se star(* 0.10 ** 0.05 *** 0.01) ///
    keep(tax_any tax_short_eur spill150 nbr_tax_pressure) b(3) label title("Airport-level DiD: ticket taxes, seats and connectivity")
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
reghdfe ln_seats tax_any spill150 [aw = seats0], absorb(aid rid#year) vce(cluster iso_country)
* (b) drop COVID years (treated countries' recovery paths differ from Southern Europe's)
reghdfe ln_seats tax_any spill150 if !inrange(year, 2020, 2022), absorb(aid rid#year) vce(cluster iso_country)
* (c) few treated clusters (~9 countries): wild-cluster bootstrap p-values   (ssc install boottest)
reghdfe ln_seats tax_any spill150, absorb(aid rid#year) vce(cluster iso_country)
boottest tax_any, reps(9999) seed(1234) nograph
* (d) staggered-DiD robust estimator (ssc install csdid / did_imputation) — treatment = first_tax, never-treated controls
*     did_imputation ln_seats aid year first_tax, fe(aid rid#year) cluster(iso_country) autosample

* (e) not-yet-treated control only (Li et al. "staggered rollout" column)
reghdfe ln_co2 tax_any spill150 if ever_treated, absorb(aid rid#year) vce(cluster iso_country)
* (f) dynamics: years since introduction, quadratic (Li et al. eq. 4 analogue)
reghdfe ln_co2 tax_any c.yrs_since c.yrs_since#c.yrs_since spill150, absorb(aid rid#year) vce(cluster iso_country)

*--- Decomposition: ln CO2 = ln seats + ln stage length + ln (CO2 per seat-km) ------------------------------
*   same regressors on each component; coefficients add up to the ln_co2 coefficient
foreach y in ln_seats ln_stage ln_co2_skm {
    reghdfe `y' tax_any spill150, absorb(aid rid#year) vce(cluster iso_country)
}

*--- Back-of-envelope: tonnes abated vs leaked, value at SCC, vs connectivity loss ------------------------
est restore ln_co2_bin
scalar b_tax = _b[tax_any]
scalar b_spill = _b[spill150]
preserve
    gen double abated = (co2_t/exp(b_tax) - co2_t) * tax_any
    gen double leaked = (co2_t - co2_t/exp(b_spill)) * spill150
    collapse (sum) abated leaked
    gen net_mt = (abated - leaked)/1e6
    gen value_bn_scc100 = net_mt * 100 / 1e3     // EUR bn at SCC = 100 EUR/t; compare with GACI loss x trade elasticity (2.1)
    list
restore

*--- Heterogeneity: hubs vs non-hubs (baseline GACI tercile, 1996 or first year) ----------------------
bys aid (year): gen gaci0 = GACI[1]
xtile hubq = gaci0, nq(3)
reghdfe ln_seats c.tax_any#i.hubq spill150, absorb(aid rid#year) vce(cluster iso_country)
