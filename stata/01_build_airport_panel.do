*------------------------------------------------------------------------------*
* 01: GACI airport-year panel (1996–2024) with country codes
*------------------------------------------------------------------------------*
import delimited "$PROC/gaci_with_country.csv", clear varnames(1) encoding(utf8) case(preserve)
rename (Airport Year Region TotalCapacity) (airport year region seats)
drop if missing(iso_country)
egen aid = group(airport)
egen rid = group(region)
gen ln_seats = ln(seats)
gen ln_gaci  = ln(GACI)
gen ln_deg   = ln(Degree)
label var seats    "Scheduled seats (annual)"
label var GACI     "Global Air Connectivity Index"
label var ln_seats "ln seats"
label var ln_gaci  "ln GACI"
* Analysis sample: airports with sustained service (>= 20 of 29 years) and >= 50k seats in some year
bys aid: gen nyears = _N
bys aid: egen maxseats = max(seats)
gen insample = nyears >= 20 & maxseats >= 50000
xtset aid year
compress
save "$PROC/airport_panel.dta", replace
