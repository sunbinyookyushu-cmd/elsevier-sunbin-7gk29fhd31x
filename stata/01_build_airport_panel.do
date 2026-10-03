*------------------------------------------------------------------------------*
* 01: GACI airport-year panel (1996–2024) with country codes
*------------------------------------------------------------------------------*
import delimited "$PROC/airport_panel_co2.csv", clear varnames(1) encoding(utf8) case(preserve)   // GACI + country + bottom-up CO2 (scripts/11)
rename (Airport Year Region TotalCapacity) (airport year region seats)
drop if missing(iso_country)
egen aid = group(airport)
egen rid = group(region)
gen ln_seats = ln(seats)
gen ln_gaci  = ln(GACI)
gen ln_deg   = ln(Degree)
gen ln_co2      = ln(co2_t)              // departure CO2, all phases (t)
gen ln_co2_intl = ln(co2_intl_t)
gen ln_co2_dom  = ln(co2_dom_t)
gen ln_co2_seat = ln(co2_per_seat_kg)
gen ln_co2_skm  = ln(co2_per_skm_g)      // technology / efficiency margin
gen ln_stage    = ln(stage_km)           // average stage length (composition margin)
label var ln_co2 "ln CO2 (departures, t)"
drop if year == 2024 & n_months < 12     // 2024 is a partial year in the emissions file
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
