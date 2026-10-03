*==============================================================================
* co2_airport_feyrer.do   (LZ comment 2, identification pilot, 2026-09-03)
* Airport-level 2SLS with the airport Feyrer shifter z_air = a_t x ln airMA_a,1996
* under airport FE + country x year FE (cluster airport).
*   (1) first stage, (2) 2SLS on ln CO2 / ln seat-km / ln intensity / intl share,
*   (3) size-by-cycle stress: add a_t x ln seat-km_1996 and a_t x ln GACI_1996,
*   (4) reduced forms.
* Decision rule (pre-registered in the response plan): the pilot is adopted only if
* the first stage survives (3) with KP F above 10.
* Export: _airport_feyrer.csv (item outc b se p kpf nn)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "airport_feyrer_panel.csv", clear varnames(1) encoding("utf-8")
ds airport_iata iso3, not
destring `r(varlist)', replace force
tempfile z
save `z'
import delimited "airport_co2_panel.csv", clear varnames(1) encoding("utf-8")
ds airport_iata iso3 region, not
destring `r(varlist)', replace force
merge 1:1 airport_iata year using `z', keep(3) nogenerate
encode airport_iata, gen(apid)
encode iso3, gen(cid)
egen cyr = group(cid year)

capture which ivreghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
    ssc install ivreghdfe, replace
}

tempname R
postfile `R' str24 item str16 outc double(b se p kpf) long(nn) using "_apf_tmp", replace

* first stages
reghdfe ln_gaci z_air, absorb(apid cyr) vce(cluster apid)
test z_air
di "AFS baseline: pi = " %8.4f _b[z_air] " (se " %7.4f _se[z_air] ")  F = " %8.1f r(F) "  N = " %8.0f e(N)
post `R' ("fs_baseline") ("ln_gaci") (_b[z_air]) (_se[z_air]) (2*normal(-abs(_b[z_air]/_se[z_air]))) (r(F)) (e(N))
reghdfe ln_gaci z_air z_cap96, absorb(apid cyr) vce(cluster apid)
test z_air
di "AFS + a_t x ln skm96: pi = " %8.4f _b[z_air] " (se " %7.4f _se[z_air] ")  F = " %8.1f r(F)
post `R' ("fs_plus_cap96") ("ln_gaci") (_b[z_air]) (_se[z_air]) (2*normal(-abs(_b[z_air]/_se[z_air]))) (r(F)) (e(N))
reghdfe ln_gaci z_air z_cap96 z_gaci96, absorb(apid cyr) vce(cluster apid)
test z_air
di "AFS + both size cycles: pi = " %8.4f _b[z_air] " (se " %7.4f _se[z_air] ")  F = " %8.1f r(F)
post `R' ("fs_plus_both") ("ln_gaci") (_b[z_air]) (_se[z_air]) (2*normal(-abs(_b[z_air]/_se[z_air]))) (r(F)) (e(N))

* 2SLS and reduced forms
foreach yv in ln_co2 ln_skm ln_intensity intl_share_skm {
    capture noisily ivreghdfe `yv' (ln_gaci = z_air), absorb(apid cyr) cluster(apid)
    if _rc == 0 {
        di "AIV baseline `yv': b = " %8.3f _b[ln_gaci] " (se " %7.3f _se[ln_gaci] ")  KP F = " %8.1f e(widstat) "  N = " %8.0f e(N)
        post `R' ("iv_baseline") ("`yv'") (_b[ln_gaci]) (_se[ln_gaci]) (2*normal(-abs(_b[ln_gaci]/_se[ln_gaci]))) (e(widstat)) (e(N))
    }
    capture noisily ivreghdfe `yv' z_cap96 z_gaci96 (ln_gaci = z_air), absorb(apid cyr) cluster(apid)
    if _rc == 0 {
        di "AIV stressed `yv': b = " %8.3f _b[ln_gaci] " (se " %7.3f _se[ln_gaci] ")  KP F = " %8.1f e(widstat)
        post `R' ("iv_stressed") ("`yv'") (_b[ln_gaci]) (_se[ln_gaci]) (2*normal(-abs(_b[ln_gaci]/_se[ln_gaci]))) (e(widstat)) (e(N))
    }
    reghdfe `yv' z_air, absorb(apid cyr) vce(cluster apid)
    post `R' ("rf_baseline") ("`yv'") (_b[z_air]) (_se[z_air]) (2*normal(-abs(_b[z_air]/_se[z_air]))) (.) (e(N))
    reghdfe `yv' ln_gaci, absorb(apid cyr) vce(cluster apid)
    post `R' ("ols") ("`yv'") (_b[ln_gaci]) (_se[ln_gaci]) (2*normal(-abs(_b[ln_gaci]/_se[ln_gaci]))) (.) (e(N))
}

postclose `R'
preserve
use "_apf_tmp", clear
list, clean noobs
export delimited "_airport_feyrer.csv", replace
restore
erase "_apf_tmp.dta"
di _n "DONE_AIRPORT_FEYRER"
