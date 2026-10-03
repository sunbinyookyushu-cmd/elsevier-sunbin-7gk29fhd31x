*==============================================================================
* gaci_analysis.do   --  SINGLE master analysis file
* Air connectivity (GACI) -> trade, IV/2SLS.  Uses ONE dataset: gaci_panel.csv
*==============================================================================
* CODEBOOK (gaci_panel.csv, 4,714 country-year, 187 countries, 1996-2023)
* ---- id ----
*   c reg = ISO3 country / sub-region ;  y = year
* ---- outcomes ----
*   ln_tradevol  ln(trade volume, USD)
*   trade_share  trade openness = trade % GDP
*   lngdp        ln(GDP, USD)        [used to build trade_intensity = ln_tradevol-lngdp]
* ---- treatments (air connectivity), all ENDOGENOUS ----
*   lng          ln(GACI_sum)            total connectivity (scales with size)
*   ln_gaci_cwm  ln(capacity-weighted-mean GACI)   hub QUALITY, size-neutral
*   ln_gaci_mean ln(simple-mean GACI)
*   lncap        ln(total seat capacity)
* ---- instruments ----
*   ln_unesco    ln(cumulative UNESCO World Heritage sites)  [tourism channel; missing if 0]
*   unesco_cum   level count ; unesco_cum_nat = natural/mixed only
*   lnz          ln(predicted GACI = geographic market access, pop/dist^2)  [Frankel-Romer]
* ---- controls ----
*   lnpc lnpop lnland abslat n_air
* ---- GACI components (country sum & mean): deg_/eig_/close_/betw_/regimp_/cap_ ----
*
* KEY FACTS (updated 2026-06-17, leave-out lnZ):
*  - lnz is now a PROPER Frankel-Romer leave-out instrument: foreign pop / dist^2 with the
*    OWN country fully excluded.  (lnz_own = old version that leaked own-country population
*    through domestic airports; kept ONLY for comparison.)
*  - Geographic IV (lnz) is strong in LEVELS / region+year FE (first-stage F ~ 21 for lng),
*    but COLLAPSES under COUNTRY FE (F < 1): market access has ~no within-country variation.
*    => headline uses REGION+year FE (absorb regcode y), NOT country FE.
*  - For treatment = capacity-weighted-mean GACI (ln_gaci_cwm = hub QUALITY, size-neutral),
*    lnz survives country FE a bit better (clustered F ~ 3) but still weak; region+year is
*    the usable spec.  Headline treatment = ln_gaci_cwm, instrument = lnz.
*  - NB deg_mean is ITSELF an endogenous connectivity component (collinear with GACI).
*    Including it as a control conditions on a collinear mediator -> always report the
*    with-deg_mean and without-deg_mean specs as a robustness pair.
*  - UNESCO natural-heritage (ln_unesco_nat) kept as an alternative-exclusion robustness IV.
*==============================================================================

clear all
set more off
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel.csv", clear varnames(1) encoding("utf-8")

* numeric (blanks -> missing) for ALL columns EXCEPT string IDs c, reg
ds c reg, not
destring `r(varlist)', replace force
encode c,   gen(isocode)
encode reg, gen(regcode)
xtset isocode y

gen trade_intensity = ln_tradevol - lngdp     // = ln(trade/GDP) = openness

* UNESCO instrument: KEEP all country-years (0 sites -> ln(1)=0), avoids selecting on
* having heritage and keeps the 0->1 extensive margin (73 countries, 1,031 rows).
* (Originally ln_unesco = ln(cum), which set 0-site rows to missing and dropped them.
*  To reproduce the drop-zeros version as robustness: use ln(unesco_cum) instead.)
replace ln_unesco = ln(1 + unesco_cum)
gen ln_unesco_nat = ln(1 + unesco_cum_nat)   // NATURAL+MIXED heritage = clean tourism IV

label var lng          "ln GACI_sum (connectivity, endog)"
label var ln_gaci_cwm  "ln capacity-wtd-mean GACI (hub quality, endog)"
label var ln_unesco    "ln cumulative UNESCO sites (IV)"
label var lnz          "ln predicted GACI / market access (IV)"
label var trade_intensity "ln(trade/GDP) = openness"

capture which ivreg2
if _rc {
    capture ssc install ranktest, replace
    capture ssc install ivreg2, replace
}
capture which ivreghdfe
if _rc {
    capture ssc install ftools, replace
    capture ssc install reghdfe, replace
    capture ssc install ivreghdfe, replace
}

*------------------------------------------------------------------------------
* 1) FIRST-STAGE STRENGTH: leave-out market access (lnz), levels vs country FE
*    (run as reduced-form-style readout; full first stage is in the IV models below)
*------------------------------------------------------------------------------
di _n "==== 1a lnz -> ln_gaci_cwm, REGION+year FE (headline FE) ===="
reghdfe ln_gaci_cwm lnz lnpop deg_mean, absorb(regcode y) cluster(isocode)
test lnz
di _n "==== 1b lnz -> ln_gaci_cwm, COUNTRY+year FE (expect weak) ===="
reghdfe ln_gaci_cwm lnz lnpop deg_mean, absorb(isocode y) cluster(isocode)
test lnz
di _n "==== 1c old leaky lnz_own -> ln_gaci_cwm, COUNTRY+year FE (collapses) ===="
reghdfe ln_gaci_cwm lnz_own lnpop deg_mean, absorb(isocode y) cluster(isocode)
test lnz_own

*==============================================================================
* HEADLINE: hub-quality connectivity -> trade openness, IV = leave-out market access
*   outcome    = trade_intensity = ln(trade/GDP) = openness
*   treatment  = ln_gaci_cwm (capacity-weighted-mean GACI; size-neutral hub QUALITY)
*   instrument = lnz (leave-out Frankel-Romer market access; FOREIGN pop / dist^2)
*   FE         = region + year  (absorb regcode y) -- country FE kills this geographic IV
*   first-stage F printed via 'first'.
*   SE: robust, NOT clustered (analyst choice 2026-06-17). NB country-clustered SE shrinks
*       the first-stage F sharply (panel serial correlation); add cluster(isocode) to any
*       model below to reproduce the clustered robustness version.
*==============================================================================
di _n "==== M1 HEADLINE: trade_intensity (ln_gaci_cwm = lnz), absorb(regcode y) ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = lnz), absorb(regcode y) cluster(isocode) first

di _n "==== M2 + geographic controls (lnpc lnland abslat) ===="
ivreghdfe trade_intensity lnpop lnpc lnland abslat deg_mean (ln_gaci_cwm = lnz), absorb(regcode y) cluster(isocode) first

di _n "==== M3 robustness: DROP deg_mean (it is endogenous connectivity) ===="
ivreghdfe trade_intensity lnpop (ln_gaci_cwm = lnz), absorb(regcode y) cluster(isocode) first

di _n "==== M4 outcome = ln_tradevol (+lngdp control) ===="
ivreghdfe ln_tradevol lngdp lnpop deg_mean (ln_gaci_cwm = lnz), absorb(regcode y) cluster(isocode) first

di _n "==== M5 outcome = trade_share (%) ===="
ivreghdfe trade_share lnpop deg_mean (ln_gaci_cwm = lnz), absorb(regcode y) cluster(isocode) first

di _n "==== M6 treatment = GACI_sum (lng) instead of hub quality ===="
ivreghdfe trade_intensity lnpop deg_mean (lng = lnz), absorb(regcode y) cluster(isocode) first

di _n "==== M7 robustness IV = natural+mixed UNESCO heritage ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = ln_unesco_nat), absorb(regcode y) cluster(isocode) first

di _n "==== M8 sanity: COUNTRY+year FE (expect weak-IV / sign flip) ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = lnz), absorb(isocode y) cluster(isocode) first

di _n "==== M9 OLS benchmark (no IV) ===="
reghdfe trade_intensity ln_gaci_cwm lnpop deg_mean, absorb(regcode y) cluster(isocode)

*------------------------------------------------------------------------------
* 2) Overidentification: lnz + UNESCO together -> Hansen J tests joint exclusion
*------------------------------------------------------------------------------
di _n "==== M10 two instruments (lnz + natural UNESCO), Hansen J ===="
ivreghdfe trade_intensity lnpop deg_mean (ln_gaci_cwm = lnz ln_unesco_nat), absorb(regcode y) cluster(isocode) first
