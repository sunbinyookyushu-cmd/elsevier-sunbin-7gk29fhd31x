* 09: airport-catchment CO2 and GACI.  Input: airport_catchment_panel.dta (built from airport_catchment_co2.csv + GACI panel)
use airport_catchment_panel.dta, clear
egen aid = group(Airport); egen cy = group(iso_country year); xtset aid year
gen ln_gaci = ln(gaci); gen ln_pop = ln(pop)
foreach s in TOTnoAV ENE IND TRO RCO {
    gen ln_co2_`s' = ln(co2_`s')
    reghdfe ln_co2_`s' ln_gaci ln_pop, absorb(aid cy) vce(cluster aid)                      // airport + country x year FE
    ivreghdfe ln_co2_`s' (ln_gaci = heritage_x_tour feyrer_air) ln_pop, absorb(aid cy) cluster(aid) first
}
* long differences
foreach k in 5 10 {
    foreach s in TOTnoAV ENE IND { gen d`k'_`s' = ln_co2_`s' - L`k'.ln_co2_`s' }
    gen d`k'_gaci = ln_gaci - L`k'.ln_gaci; gen d`k'_pop = ln_pop - L`k'.ln_pop
    foreach s in TOTnoAV ENE IND { reghdfe d`k'_`s' d`k'_gaci d`k'_pop, absorb(cy) vce(cluster aid) }
}
