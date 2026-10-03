*------------------------------------------------------------------------------*
* 04: ROUTE-LEVEL MODEL (run once OAG segment data are available)
*
*   ln CO2_ijt = beta * Tax_ijt + alpha_ij + lambda_it + mu_jt + e_ijt          (2)
*
*   i = origin airport, j = destination airport, t = year
*   Tax_ijt : economy per-passenger ticket tax (EUR) payable on departure from i to j in t
*             (band depends on destination country's distance from the taxing country)
*   alpha_ij: route FE;  lambda_it: origin-airport x year FE;  mu_jt: destination-airport x year FE
*   => identification from same-airport, same-year differences in tax across distance bands.
*   Decomposition: run (2) for ln departures, ln seats, ln ASK, ln CO2, ln (CO2/seat) => scale vs technology.
*
* Expected OAG input (data/raw/oag/segments_YYYY.csv or one file): 
*   origin_iata dest_iata ac_code (IATA or ICAO) departures seats year [carrier domestic]
*------------------------------------------------------------------------------*
* --- 1. Route-year aggregation with CO2 ---------------------------------------------------------
import delimited "$RAW/oag/segments.csv", clear varnames(1)
* great-circle distance from airport coordinates
preserve
    import delimited "$PROC/airport_country_map.csv", clear varnames(1) case(preserve)
    keep Airport iso_country lat lon
    rename (Airport iso_country lat lon) (origin_iata o_iso o_lat o_lon)
    tempfile o
    save `o'
    rename (origin_iata o_iso o_lat o_lon) (dest_iata d_iso d_lat d_lon)
    tempfile d
    save `d'
restore
merge m:1 origin_iata using `o', keep(3) nogen
merge m:1 dest_iata   using `d', keep(3) nogen
geodist o_lat o_lon d_lat d_lon, gen(gc_km)           // ssc install geodist
* CO2 per flight from the FEAT lookup (type x 100-km grid); map IATA -> ICAO codes first
*   -> in production: export ac codes, run scripts/02_fuel_burn_model.py (python) to attach co2_kg, or
*      merge on (ac_icao, gc_km rounded to 100) with data/processed/co2_per_flight_lookup.csv
gen gc_km100 = max(100, round(gc_km, 100))
rename ac_code ac_icao
merge m:1 ac_icao gc_km100 using "$PROC/co2_lookup.dta", keep(1 3)   // build .dta from the csv once
gen co2_t = co2_kg * departures / 1000
collapse (sum) departures seats co2_t (first) gc_km o_iso d_iso, by(origin_iata dest_iata year)
gen ask = seats * gc_km
gen ln_co2 = ln(co2_t)
gen ln_seats = ln(seats)
gen ln_dep = ln(departures)
gen ln_ask = ln(ask)
gen ln_co2_seat = ln(co2_t / seats)

* --- 2. Tax payable on route i->j in year t --------------------------------------------------------
* band_reference_distances.csv gives, for each taxing country, the destination-country distance and
* (for UK) the statutory band; aviation_taxes_master.csv gives the rate per band x period.
* Build a (o_iso, d_iso, year) -> tax_eur table in a separate do-file (band logic is tax-specific), then:
merge m:1 o_iso d_iso year using "$PROC/route_tax_eur.dta", keep(1 3) nogen
replace tax_eur = 0 if missing(tax_eur)

* --- 3. Estimation ------------------------------------------------------------------------------
egen rid = group(origin_iata dest_iata)
egen oy  = group(origin_iata year)
egen dy  = group(dest_iata year)
eststo clear
foreach y in ln_dep ln_seats ln_ask ln_co2 ln_co2_seat {
    eststo `y': reghdfe `y' tax_eur, absorb(rid oy dy) vce(cluster o_iso)
}
esttab using "$OUT/table_route_co2.csv", replace se b(4) star(* 0.10 ** 0.05 *** 0.01) keep(tax_eur)

* --- 4. Band-threshold check (UK): routes just below vs above 2,000 miles, 2009–2014 -----------------
*   keep if o_iso=="GB" & inrange(year,2009,2014); use dist_miles of destination capital; local linear in distance
