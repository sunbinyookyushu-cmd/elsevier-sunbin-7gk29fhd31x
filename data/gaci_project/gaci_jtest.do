*==============================================================================
* gaci_jtest.do  --  Overidentification (Hansen/Sargan J) test with BOTH instruments
*   instruments : lnz (leave-out market access) + ln_unesco_nat (natural heritage)
*   logic       : 2 instruments, 1 endogenous -> overidentified -> J test of joint
*                 exclusion validity.  Shown for treatment = lng and = ln_gaci_cwm,
*                 both robust(no cluster) [Sargan] and cluster(isocode) [Hansen J].
*   read-with   : the two JUST-identified betas (lnz-only vs UNESCO-only) are printed
*                 first; if they disagree, J rejects (at least one exclusion fails).
*   FE          : region + year (absorb regcode y)
*==============================================================================
clear all
set more off
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
encode reg, gen(regcode)
xtset isocode y
gen trade_intensity = ln_tradevol - lngdp
replace ln_unesco = ln(1 + unesco_cum)
gen ln_unesco_nat = ln(1 + unesco_cum_nat)

*==============================================================================
* TREATMENT = GACI_sum (lng)   [the strong-instrument case]
*==============================================================================
di _n "################ TREATMENT = lng (GACI_sum) ################"

di _n "==== L0a just-identified: IV = lnz only ===="
ivreghdfe trade_intensity lnpop deg_mean (lng = lnz), absorb(regcode y) cluster(isocode)
di _n "==== L0b just-identified: IV = UNESCO natural only ===="
ivreghdfe trade_intensity lnpop deg_mean (lng = ln_unesco_nat), absorb(regcode y) cluster(isocode)

di _n "==== L1 OVERID both, NO cluster (robust) -> Sargan/Hansen J ===="
ivreghdfe trade_intensity lnpop deg_mean (lng = lnz ln_unesco_nat), absorb(regcode y) first
di _n "==== L2 OVERID both, CLUSTER(isocode) -> Hansen J ===="
ivreghdfe trade_intensity lnpop deg_mean (lng = lnz ln_unesco_nat), absorb(regcode y) cluster(isocode) first

*==============================================================================
* TREATMENT = capacity-wtd-mean GACI (ln_gaci_cwm)   [hub quality]
*==============================================================================
di _n "################ TREATMENT = ln_gaci_cwm (hub quality) ################"

di _n "==== C0a just-identified: IV = lnz only ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = lnz), absorb(regcode y) cluster(isocode)
di _n "==== C0b just-identified: IV = UNESCO natural only ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = ln_unesco_nat), absorb(regcode y) cluster(isocode)

di _n "==== C1 OVERID both, NO cluster (robust) -> Sargan/Hansen J ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = lnz ln_unesco_nat), absorb(regcode y) first
di _n "==== C2 OVERID both, CLUSTER(isocode) -> Hansen J ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = lnz ln_unesco_nat), absorb(regcode y) cluster(isocode) first

*==============================================================================
* Same J test via ivregress + estat overid (cross-check, robust no-cluster)
*==============================================================================
di _n "==== X ivregress cross-check (lng), estat overid ===="
ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y (lng = lnz ln_unesco_nat), vce(robust)
estat overid
