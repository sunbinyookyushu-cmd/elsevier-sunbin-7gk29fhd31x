*------------------------------------------------------------------------------*
* 07: Air service agreements and CO2 — dyadic staggered DiD (origin airport x destination country x year)
*
*   ln y_odt = beta * Open_{c(o)dt} + alpha_od + lambda_ot + mu_dt + e_odt
*
*   Inputs: $RAW/oag/seats_co2_by_origin_destcountry_year.csv  (origin_iata dest_iso year n_flights seats seat_km co2_kg)
*           $ASA/asa_pair_year.csv  (o_iso d_iso year open_any open_us open_eu open_regional ali first_year)
*------------------------------------------------------------------------------*
import delimited "$RAW/oag/seats_co2_by_origin_destcountry_year.csv", clear varnames(1)
drop if year == 2024
rename dest_iso d_iso
merge m:1 origin_iata using "$PROC/airport_country_map.dta", keep(3) nogen keepusing(iso_country)
rename iso_country o_iso
drop if o_iso == d_iso                                            // international pairs only
preserve
    import delimited "$ASA/asa_pair_year.csv", clear varnames(1)
    tempfile asa
    save `asa'
restore
merge m:1 o_iso d_iso year using `asa', keep(1 3) nogen
foreach v in open_any open_us open_eu open_regional {
    replace `v' = 0 if missing(`v')
}
gen ln_co2   = ln(co2_kg/1000)
gen ln_seats = ln(seats)
gen ln_fl    = ln(n_flights)
gen ln_skm   = ln(seat_km)
gen ln_stage = ln(seat_km/seats)
gen ln_int   = ln(co2_kg*1000/seat_km)
egen od = group(origin_iata d_iso)
egen ot = group(origin_iata year)
egen dt = group(d_iso year)
keep if seats >= 1000

*--- Main: static DiD, all agreement types ---------------------------------------------------------
eststo clear
foreach y in ln_seats ln_fl ln_skm ln_stage ln_co2 ln_int {
    eststo a_`y': reghdfe `y' open_any, absorb(od ot dt) vce(cluster o_iso)
}
esttab a_* using "$OUT/table_asa_main.csv", replace se b(4) star(* 0.10 ** 0.05 *** 0.01) keep(open_any)

*--- By agreement type -----------------------------------------------------------------------------
foreach y in ln_seats ln_co2 ln_int {
    reghdfe `y' open_us open_eu open_regional, absorb(od ot dt) vce(cluster o_iso)
}

*--- Event study around entry into force (binned -5..+8, ref -1) -------------------------------------
gen et = year - first_year
replace et = -5 if et < -5 & !missing(et)
replace et =  8 if et >  8 & !missing(et)
forvalues k = 5(-1)2 {
    gen ev_m`k' = (et == -`k')
}
forvalues k = 0/8 {
    gen ev_p`k' = (et == `k')
}
reghdfe ln_co2 ev_m5 ev_m4 ev_m3 ev_m2 ev_p0-ev_p8, absorb(od ot dt) vce(cluster o_iso)
coefplot, keep(ev_*) vertical yline(0) xline(4.5, lpattern(dash)) ytitle("Effect on ln CO2") xtitle("Years since agreement in force")
graph export "$OUT/fig_asa_event_co2.pdf", replace

*--- Plausibly exogenous timing: EU horizontal agreements after the 2002 ECJ judgments -----------------
reghdfe ln_co2 open_eu if o_iso_in_eu == 1, absorb(od ot dt) vce(cluster d_iso)

*--- Staggered-robust estimators (ssc install csdid / did_imputation) -----------------------------
*   did_imputation ln_co2 od year first_year, fe(od ot dt) cluster(o_iso) autosample

*--- Network position of the origin airport (annual, airport level) -----------------------------------
*   exposure_ot = share of o's baseline seats to destinations whose agreement enters into force by t
*   reghdfe ln_gaci exposure, absorb(airport iso_country#year) vce(cluster iso_country)
