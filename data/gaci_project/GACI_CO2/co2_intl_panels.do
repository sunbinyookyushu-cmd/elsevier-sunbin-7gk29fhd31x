*==============================================================================
* co2_intl_panels.do
* Supplement: H2 measure comparison and H3 temporal split for the HEADLINE
* outcome ln_co2_bunker_intl (international emissions, fuel-uplift allocation).
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

import delimited "gaci_co2_panel.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y

foreach tr in ln_gaci_cwm lng ln_gaci_max {
    ivreghdfe ln_co2_bunker_intl lnpop (`tr' = tourism_int), absorb(isocode y) robust
    local kpf = e(widstat)
    test `tr' = 1
    di "H2 intl `tr': b = " %9.3f _b[`tr'] " (se " %9.3f _se[`tr'] ")  KP F = " %6.1f `kpf' "  Wald p(b=1) = " %6.3f r(p)
}

ivreghdfe ln_co2_bunker_intl lnpop (ln_gaci_cwm = tourism_int) if y < 2010, absorb(isocode y) robust
di "H3 intl pre-2010:  b = " %9.3f _b[ln_gaci_cwm] " (se " %9.3f _se[ln_gaci_cwm] ")  KP F = " %6.1f e(widstat)
ivreghdfe ln_co2_bunker_intl lnpop (ln_gaci_cwm = tourism_int) if y >= 2010, absorb(isocode y) robust
di "H3 intl post-2010: b = " %9.3f _b[ln_gaci_cwm] " (se " %9.3f _se[ln_gaci_cwm] ")  KP F = " %6.1f e(widstat)

di _n "DONE_INTL_PANELS"
