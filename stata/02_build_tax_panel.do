*------------------------------------------------------------------------------*
* 02: Country-year aviation ticket tax treatment
* Input : data/processed/aviation_taxes_master.csv (one row per period x band x class, see docs/taxes_*.md)
* Output: data/processed/tax_country_year.dta with
*   tax_any      = 1 if a per-passenger ticket tax was in force for >= 6 months of year t
*   tax_start    = first full year of taxation (for event time)
*   tax_short_eur= economy per-pax rate on the shortest/intra-European band, EUR, year-weighted
*   tax_long_eur = economy per-pax rate on the longest band, EUR, year-weighted
*------------------------------------------------------------------------------*
import delimited "$PROC/aviation_taxes_master.csv", clear varnames(1) encoding(utf8) stringcols(_all)
keep if inlist(class, "economy", "all")
gen double vfrom = date(valid_from, "YMD")
gen double vto   = date(valid_to,   "YMD")
replace vto = date("2024-12-31", "YMD") if missing(vto)
destring rate, replace force
drop if missing(rate)
* --- FX to EUR (approximate ECB annual averages in stata/fx_eur.csv; EUR per unit of local currency) ----
preserve
    import delimited "$ROOT/stata/fx_eur.csv", clear varnames(1)
    tempfile fx
    save `fx'
restore
* expand each rate row into the calendar years it covers; weight by months in force in that year
gen y0 = year(vfrom)
gen y1 = year(vto)
gen nyrs = y1 - y0 + 1
expand nyrs
bys country_iso instrument band_id class vfrom: gen year = y0 + _n - 1
gen double start = max(vfrom, mdy(1,1,year))
gen double stop  = min(vto,   mdy(12,31,year))
gen months = (stop - start + 1) / 30.44
replace months = 12 if months > 12
rename currency cur
merge m:1 cur year using `fx', keep(1 3) nogen
gen rate_eur = rate * fx * months / 12
destring distance_rule_km, gen(dkm) force
bys country_iso year: egen dmin = min(dkm)
bys country_iso year: egen dmax = max(dkm)
gen is_short = (dkm == dmin) | missing(dkm)
gen is_long  = (dkm == dmax) | missing(dkm)
tempfile base short long
preserve
    collapse (max) months_any = months, by(country_iso year)
    save `base'
restore
preserve
    keep if is_short
    collapse (sum) tax_short_eur = rate_eur, by(country_iso year)
    save `short'
restore
keep if is_long
collapse (sum) tax_long_eur = rate_eur, by(country_iso year)
merge 1:1 country_iso year using `short', nogen
merge 1:1 country_iso year using `base',  nogen
gen tax_any = months_any >= 6
rename country_iso iso_country
bys iso_country (year): gen tax_start = year if tax_any & (_n == 1 | !tax_any[_n-1])
bys iso_country: egen first_tax = min(tax_start)
drop tax_start
label var tax_any       "Ticket tax in force (>= 6 months)"
label var tax_short_eur "Economy per-pax tax, shortest band (EUR, year-weighted)"
label var tax_long_eur  "Economy per-pax tax, longest band (EUR, year-weighted)"
save "$PROC/tax_country_year.dta", replace
