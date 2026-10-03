*------------------------------------------------------------------------------*
* 05: AXIS 1 — GACI as the continuous "network density" (Li, Liu, Purevjav & Yang 2019 analogue)
*
*   ln CO2_it = beta * ln GACI_it + gamma * ln pop_ct + alpha_i + delta_t + e_it
*
*   Li et al.: subway density at a monitor (continuous, whole-network) -> air pollution, instrumented by
*   density implied by HISTORICAL subway plans.  Here: GACI (continuous network position) -> aviation CO2,
*   instrumented by the heritage-tourism shift-share from the trade paper:
*        tourism_int_ct = Dbar_t (world tourist arrivals, min-max) x ln(1 + H_c^{nat+mix})
*   Country FE absorb the heritage endowment, year FE absorb the world cycle; only the interaction identifies.
*   Exclusion is easier than for trade: heritage-driven tourism moves aviation CO2 only by moving flights.
*
*   Level A (now): country-year, GACI_cwm/max/sum from the trade-paper panel, CO2 = sum of airport dep CO2.
*   Level B (now): airport-year, ln GACI_at instrumented by tourism_int_{c(a),t} (same shifter for all airports
*            of the country) or by tourism_int x baseline airport share of national seats.
*   Combination (Li et al. Table 9): dCO2(tax) = beta_IV x dGACI(tax, from 03_airport_did.do).
*
*   Needs: $PROC/country_panel_trade.dta  (iso_country year gaci_cwm gaci_max gaci_sum tourism_int ln_pop)
*          -> export from the trade-paper project and commit to data/processed/.
*------------------------------------------------------------------------------*
use "$PROC/airport_panel.dta", clear

*--- Level A: country-year ---------------------------------------------------------------------------
preserve
    collapse (sum) co2_t co2_intl_t seats_dep seat_km, by(iso_country year)
    merge 1:1 iso_country year using "$PROC/country_panel_trade.dta", keep(3) nogen
    gen ln_co2 = ln(co2_t)
    gen ln_co2_intl = ln(co2_intl_t)
    foreach m in cwm max sum {
        gen ln_gaci_`m' = ln(gaci_`m')
    }
    egen cid = group(iso_country)
    * OLS, first stage, 2SLS (ssc install ivreghdfe)
    reghdfe   ln_co2 ln_gaci_cwm ln_pop, absorb(cid year) vce(robust)
    reghdfe   ln_gaci_cwm tourism_int ln_pop, absorb(cid year) vce(robust)
    ivreghdfe ln_co2 (ln_gaci_cwm = tourism_int) ln_pop, absorb(cid year) robust first
    ivreghdfe ln_co2_intl (ln_gaci_cwm = tourism_int) ln_pop, absorb(cid year) robust
    * post-2010 (where the instrument has power, KP F ~ 32 in the trade paper)
    ivreghdfe ln_co2 (ln_gaci_cwm = tourism_int) ln_pop if year >= 2010, absorb(cid year) robust
    * mechanism: which network dimension carries the carbon? (components from the airport panel, cap-weighted)
restore

*--- Level B: airport-year ----------------------------------------------------------------------------
merge m:1 iso_country year using "$PROC/country_panel_trade.dta", keep(3) nogen keepusing(tourism_int ln_pop)
bys aid (year): gen share0 = seats[1]
bys iso_country year: egen natseats = total(seats)
bys iso_country (year): replace share0 = share0 / natseats[1]        // baseline share of national seats
gen z_airport = tourism_int * share0
reghdfe   ln_co2 ln_gaci ln_pop, absorb(aid rid#year) vce(cluster iso_country)
ivreghdfe ln_co2 (ln_gaci = tourism_int) ln_pop, absorb(aid year) cluster(iso_country) first
ivreghdfe ln_co2 (ln_gaci = z_airport)  ln_pop, absorb(aid rid#year) cluster(iso_country) first
* components: replace ln_gaci by ln_deg, ln(NorBetweenness), ln(Eigen) one at a time (same instrument)

*--- Regional connectivity density (optional, Li et al. density formula) ------------------------------
*   dens_at = sum_{j != a, within 500 km} GACI_jt / d_aj^2  -> build in Python from airport coordinates (scripts/08 logic)

*--- Combine with axis 2 (Li et al. Table 9) ----------------------------------------------------------
*   dln CO2_tax = beta_IV (Level A or B) x dln GACI_tax (coefficient on tax_any for ln_gaci in 03_airport_did.do)
*   report alongside the direct DiD estimate on ln_co2 from 03 as a consistency check.
