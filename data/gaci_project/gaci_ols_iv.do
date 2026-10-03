*==============================================================================
* gaci_ols_iv.do  --  OLS version + IV(2SLS) version, with estat diagnostics
*   Dataset : gaci_panel.csv   (built by build_gaci_panel.py)
*   FE      : region + year  (i.regcode i.y)   [country FE kills the geographic IV]
*   SE      : robust, NOT clustered  (analyst choice 2026-06-17)
*   Engine  : ivregress 2sls  -> estat firststage / estat endogenous / estat overid
*   Outcome : trade_intensity = ln(trade/GDP) = openness  (also ln_tradevol)
*   Treat   : ln_gaci_cwm (hub quality) and lng (GACI_sum, scale)
*   IV      : lnz (leave-out market access) ; ln_unesco_nat (natural heritage, robustness)
*==============================================================================
clear all
set more off
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel.csv", clear varnames(1) encoding("utf-8")

ds c reg, not
destring `r(varlist)', replace force
encode c,   gen(isocode)
encode reg, gen(regcode)
xtset isocode y

gen  trade_intensity = ln_tradevol - lngdp        // openness = ln(trade/GDP)
replace ln_unesco    = ln(1 + unesco_cum)
gen  ln_unesco_nat   = ln(1 + unesco_cum_nat)     // clean tourism IV (nature+mixed)

label var ln_gaci_cwm "ln cap-wtd-mean GACI (hub quality)"
label var lng         "ln GACI_sum (scale)"
label var lnz         "ln market access (leave-out IV)"
label var trade_intensity "ln(trade/GDP) openness"

*==============================================================================
* 1) OLS VERSION  (region+year FE, robust)
*==============================================================================
di _n "############################## OLS ##############################"
di _n "==== OLS-1 openness on hub quality (ln_gaci_cwm) ===="
reghdfe trade_intensity ln_gaci_cwm lnpop deg_mean, absorb(regcode y) vce(robust)
estimates store OLS_cwm
di _n "==== OLS-2 openness on GACI_sum (lng) ===="
reghdfe trade_intensity lng lnpop deg_mean, absorb(regcode y) vce(robust)
estimates store OLS_sum
di _n "==== OLS-3 trade volume on hub quality ===="
reghdfe ln_tradevol ln_gaci_cwm lngdp lnpop deg_mean, absorb(regcode y) vce(robust)
estimates store OLS_vol

*==============================================================================
* 2) IV (2SLS) VERSION  + estat diagnostics
*    estat firststage  -> weak-id F (robust) + Stock-Yogo critical values
*    estat endogenous  -> Durbin-Wu-Hausman test of treatment endogeneity
*    estat overid      -> Sargan/Wooldridge (only when overidentified)
*==============================================================================
di _n "############################## IV / 2SLS ##############################"

di _n "===== IV-1 HEADLINE: openness, (ln_gaci_cwm = lnz) ====="
ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y (ln_gaci_cwm = lnz), vce(robust) first
estimates store IV_cwm
estat firststage, all
estat endogenous

di _n "===== IV-2 treatment = GACI_sum: openness, (lng = lnz) ====="
ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y (lng = lnz), vce(robust) first
estimates store IV_sum
estat firststage, all
estat endogenous

di _n "===== IV-3 outcome = trade volume, (ln_gaci_cwm = lnz) +lngdp ====="
ivregress 2sls ln_tradevol lngdp lnpop deg_mean i.regcode i.y (ln_gaci_cwm = lnz), vce(robust) first
estimates store IV_vol
estat firststage, all
estat endogenous

di _n "===== IV-4 robustness IV = natural UNESCO, (ln_gaci_cwm = ln_unesco_nat) ====="
ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y (ln_gaci_cwm = ln_unesco_nat), vce(robust) first
estimates store IV_un
estat firststage, all
estat endogenous

di _n "===== IV-5 OVERID: openness, (ln_gaci_cwm = lnz ln_unesco_nat) ====="
ivregress 2sls trade_intensity lnpop deg_mean i.regcode i.y (ln_gaci_cwm = lnz ln_unesco_nat), vce(robust) first
estimates store IV_oid
estat firststage, all
estat overid

*==============================================================================
* 3) SUMMARY TABLE: OLS vs IV side by side (built-in estimates table)
*==============================================================================
di _n "############################## SUMMARY: OLS vs IV ##############################"
estimates table OLS_cwm OLS_sum OLS_vol IV_cwm IV_sum IV_vol IV_un IV_oid, ///
    keep(ln_gaci_cwm lng lnpop deg_mean lngdp) b(%9.4f) se(%9.4f) stats(N r2) ///
    title("OLS vs IV: GACI -> trade openness (robust SE, region+year FE)")

* optional prettier table if estout is installed:
capture which esttab
if !_rc {
    esttab OLS_cwm IV_cwm IV_sum IV_vol IV_oid using gaci_ols_iv_results.rtf, replace ///
        keep(ln_gaci_cwm lng lnpop deg_mean) se r2 nogaps ///
        mtitle("OLS cwm" "IV cwm" "IV sum" "IV vol" "IV overid") ///
        title("GACI -> trade openness: OLS vs IV")
}
