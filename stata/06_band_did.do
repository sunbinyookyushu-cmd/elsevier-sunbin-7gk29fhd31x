*------------------------------------------------------------------------------*
* 06: AXIS 2 (clean version) — distance-band DiD within origin airports
*
*   ln y_odt = beta * tau_odt + alpha_od + lambda_ot + mu_dt + e_odt
*
*   o = origin airport, d = destination COUNTRY, t = year
*   tau_odt : economy per-passenger ticket tax (EUR, year-weighted) payable from o's country to d in t
*             (data/processed/tax_by_origin_dest_year.csv, scripts/12)
*   alpha_od: origin-airport x destination-country FE
*   lambda_ot: ORIGIN AIRPORT x YEAR FE  -> absorbs every national/airport shock (adoption timing, COVID, LCC boom)
*   mu_dt   : destination-country x year FE -> absorbs destination demand
*   => identified only from same-airport, same-year differences in tax across distance bands.
*   Li et al. analogue: treated (high band) vs control (low band) within the same "city"; buffer = destinations
*   within +-200 km of a band threshold are dropped (misclassification zone).
*
*   INPUT (aggregate OAG by the user, same source as airport_month_emissions):
*     data/raw/oag/seats_co2_by_origin_destcountry_year.csv
*     columns: origin_iata, dest_iso, year, n_flights, seats, seat_km, co2_kg   (departures; dom = dest_iso == own country)
*------------------------------------------------------------------------------*
import delimited "$RAW/oag/seats_co2_by_origin_destcountry_year.csv", clear varnames(1)
drop if year == 2024                                           // partial year
rename dest_iso d_iso
merge m:1 origin_iata using "$PROC/airport_country_map.dta", keep(3) nogen keepusing(iso_country)
rename iso_country o_iso
* tax payable
preserve
    import delimited "$PROC/tax_by_origin_dest_year.csv", clear varnames(1)
    tempfile tau
    save `tau'
restore
merge m:1 o_iso d_iso year using `tau', keep(1 3) nogen
replace tau_eur = 0 if missing(tau_eur)
* band-threshold buffer: distance from origin country's reference city to destination capital
preserve
    import delimited "$PROC/band_reference_distances.csv", clear varnames(1)
    rename (ref_iso2 dest_iso2) (o_iso d_iso)
    keep o_iso d_iso dist_km dist_miles
    tempfile bd
    save `bd'
restore
merge m:1 o_iso d_iso using `bd', keep(1 3) nogen
gen near_threshold = 0
replace near_threshold = 1 if o_iso == "DE" & (inrange(dist_km, 2300, 2700) | inrange(dist_km, 5800, 6200))
replace near_threshold = 1 if o_iso == "AT" & (inrange(dist_km, 2300, 2700) | inrange(dist_km, 5800, 6200))
replace near_threshold = 1 if o_iso == "GB" & (inrange(dist_miles, 1900, 2100) | inrange(dist_miles, 3900, 4100) | inrange(dist_miles, 5900, 6100) | inrange(dist_miles, 5400, 5600))
replace near_threshold = 1 if o_iso == "SE" & inrange(dist_km, 5800, 6200)
replace near_threshold = 1 if o_iso == "NL" & inrange(dist_km, 2300, 2700)
replace near_threshold = 1 if o_iso == "FR" & inrange(dist_km, 5300, 5700)
replace near_threshold = 1 if o_iso == "BE" & inrange(dist_km, 400, 600)

gen ln_co2   = ln(co2_kg/1000)
gen ln_seats = ln(seats)
gen ln_fl    = ln(n_flights)
gen ln_skm   = ln(seat_km)
gen ln_co2_skm = ln(co2_kg*1000/seat_km)                        // g CO2 per seat-km (technology)
gen ln_stage   = ln(seat_km/seats)
egen od = group(origin_iata d_iso)
egen ot = group(origin_iata year)
egen dt = group(d_iso year)
keep if inrange(seats, 1000, .)                                  // drop trivial OD-years

*--- Main (ssc install reghdfe) ---------------------------------------------------------------------
eststo clear
foreach y in ln_co2 ln_seats ln_fl ln_skm ln_co2_skm ln_stage {
    eststo m_`y': reghdfe `y' tau_eur if !near_threshold, absorb(od ot dt) vce(cluster o_iso)
}
esttab m_* using "$OUT/table_band_did.csv", replace se b(4) star(* 0.10 ** 0.05 *** 0.01) keep(tau_eur) ///
    title("Within-airport distance-band DiD: EUR 1 of per-passenger tax")
* implicit carbon price version: tau per tCO2 per seat  (tau_eur / (co2_kg/seats/1000))
gen tau_per_tco2 = tau_eur / (co2_kg/seats/1000)
reghdfe ln_co2 tau_per_tco2 if !near_threshold, absorb(od ot dt) vce(cluster o_iso)

*--- Event studies around the clean episodes (binary high-band indicator x event time) --------------------
*   UK 2015: bands C/D (>4,000 mi) lose tax relative to band B -> reverse treatment
gen uk_far = o_iso == "GB" & dist_miles > 4000
forvalues k = 2011/2019 {
    gen uk15_`k' = uk_far * (year == `k')
}
drop uk15_2014
reghdfe ln_co2 uk15_* if o_iso == "GB" & dist_miles > 2000 & inrange(year, 2011, 2019) & !near_threshold, absorb(od ot dt) vce(cluster d_iso)
*   DE 2011: band 2/3 vs band 1 destinations from German airports
gen de_long = o_iso == "DE" & dist_km > 2500
forvalues k = 2007/2015 {
    gen de11_`k' = de_long * (year == `k')
}
drop de11_2010
reghdfe ln_co2 de11_* if o_iso == "DE" & inrange(year, 2007, 2015) & !near_threshold, absorb(od ot dt) vce(cluster d_iso)
*   NL 2008 introduction / 2009 abolition: non-EU >2,500 km vs EU destinations from Dutch airports

*--- Threshold RD (UK 2,000-mile boundary, 2009-2014): local linear in distance, both sides -----------------
preserve
    keep if o_iso == "GB" & inrange(year, 2009, 2014) & inrange(dist_miles, 1000, 3000)
    gen above = dist_miles > 2000
    gen run = dist_miles - 2000
    reghdfe ln_co2 above c.run c.run#above, absorb(ot dt) vce(cluster d_iso)
restore
