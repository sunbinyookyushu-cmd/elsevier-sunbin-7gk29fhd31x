* =====================================================================
* Tax -> network position -> CO2: IV mediation (Dippel, Ferrara and Heblich 2020, ivmediate) and Gelbach check
* Data: tax_mediation.dta (112_export_mediation.py): annual stacks, 8 European tax increases, years E-3..E
*   Y = ln_co2 (also ln_int = CO2 per seat-km); M = ln_deg (destinations; also ln_gaci)
*   Treatment = dose_post (EUR per departing passenger x post, continuous); instrument = tp (treated x post)
*   Exogenous: bp (border x post). FE: airport x event (fe_u, absorbed), year x event (fe_t, dummies)
*   Identification needs the tax to move CO2 only through the network margin once the mediator is accounted for;
*   the exact decomposition (flights per destination and CO2 per flight do not move) is the supporting evidence.
* Needs: ivmediate (ssc), ivreghdfe, reghdfe, ftools
* =====================================================================
clear all
set more off
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_tax"
cap log close
log using "tax_mediation_run.log", replace text
foreach p in ftools reghdfe ivreghdfe ivmediate {
    cap which `p'
    if _rc ssc install `p'
}
use "tax_mediation.dta", clear
describe, short
tab stk treated if post == 1

* ---------- A. ivmediate: all treated airports ----------
foreach m in ln_deg ln_gaci {
    di _n "==== ivmediate: Y = ln_co2, M = `m' ===="
    ivmediate ln_co2 bp i.fe_t, mediator(`m') treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
    di _n "==== ivmediate: Y = ln_int (CO2 per seat-km), M = `m' ===="
    ivmediate ln_int bp i.fe_t, mediator(`m') treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
}

* ---------- B. ivmediate by size tercile (treated airports of one tercile vs all controls) ----------
foreach s in small mid large {
    preserve
    keep if treated == 0 | sz_`s' == 1
    di _n "==== ivmediate, `s' airports: Y = ln_co2, M = ln_deg ===="
    cap noisily ivmediate ln_co2 bp i.fe_t, mediator(ln_deg) treatment(dose_post) instrument(tp) absorb(fe_u) vce(cluster iso3n)
    restore
}

* ---------- C. Manual three-step (conservative, mediator as control) ----------
* total:   Y on tp;  mediator: M on tp;  direct: Y on tp and M;  indirect = total - direct (Gelbach identity)
foreach m in ln_deg ln_gaci {
    reghdfe ln_co2 tp bp, absorb(fe_u fe_t) vce(cluster iso3n)
    scalar tot_`m' = _b[tp]
    reghdfe `m' tp bp, absorb(fe_u fe_t) vce(cluster iso3n)
    scalar pi_`m' = _b[tp]
    reghdfe ln_co2 tp bp `m', absorb(fe_u fe_t) vce(cluster iso3n)
    scalar dir_`m' = _b[tp]
    scalar beta_`m' = _b[`m']
    di _n "Gelbach, M = `m': total " tot_`m' "  direct " dir_`m' "  indirect " tot_`m' - dir_`m' "  (= pi " pi_`m' " x beta " beta_`m' ")"  "  share " (tot_`m' - dir_`m') / tot_`m'
}

* ---------- D. 2SLS of CO2 on the mediator with tp as the instrument (the M -> Y link under exclusion) ----------
foreach m in ln_deg ln_gaci {
    ivreghdfe ln_co2 bp (`m' = tp), absorb(fe_u fe_t) cluster(iso3n)
    ivreghdfe ln_int bp (`m' = tp), absorb(fe_u fe_t) cluster(iso3n)
}
log close
