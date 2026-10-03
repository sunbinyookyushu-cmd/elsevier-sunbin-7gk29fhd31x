* 24_gic_bysample.do : incidence curve by development stage.
* Group-specific 2SLS (Feyrer IV, ln pop, country + year FE, country-clustered SE) on subsamples:
*   baseline-connectivity terciles (earliest observed GACI_max), network-expansion era 1996-2007,
*   mature era 2010-2023 excluding 2020-21. Plus Gini, mean income and the top-half minus bottom-half contrast.
* Output: _gic_bysample_results.csv (sample, outcome, b, se, p, kpf, N, Nc)
capture log close _all
log using "24_gic_bysample_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
local GRP "d1 d2 d3 d4 d5 d6 d7 d8 d9 d10 t1 b50 m40"
foreach g of local GRP {
    capture drop ln_spt_`g'
    gen ln_spt_`g' = ln_apt_`g' - ln_apt_all
}
bysort isocode (y): gen byte first_g = sum(!missing(gaci_max)) == 1 & !missing(gaci_max)
gen g0_ = gaci_max if first_g
bysort isocode (g0_): gen gaci0 = g0_[1]
drop g0_ first_g
bysort isocode (y): gen byte first_pc = sum(!missing(lnpc)) == 1 & !missing(lnpc)
gen pc0_ = lnpc if first_pc
bysort isocode (pc0_): gen lnpc0 = pc0_[1]
drop pc0_ first_pc
bysort isocode (y): gen byte first_gd = sum(!missing(ln_gdppc)) == 1 & !missing(ln_gdppc)
gen gd0_ = ln_gdppc if first_gd
bysort isocode (gd0_): gen gdppc0 = gd0_[1]
drop gd0_ first_gd
preserve
bysort isocode: keep if _n == 1
xtile con3 = gaci0, nq(3)
xtile inc3 = lnpc0, nq(3)
xtile gdp3 = gdppc0, nq(3)
keep isocode con3 inc3 gdp3
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

tempname fh
file open `fh' using "_gic_bysample_results.csv", write replace
file write `fh' "sample,outcome,b,se,p,kpf,N,Nc" _n
capture program drop runone
program define runone
    args fh smp yv cond
    quietly count if `cond' & !missing(`yv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 60 exit
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if `cond', absorb(isocode y) cluster(isocode)
    if _rc exit
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    quietly levelsof isocode if e(sample), local(cc)
    local nc : word count `cc'
    file write `fh' "`smp',`yv',`b',`se',`p',`=e(widstat)',`=e(N)',`nc'" _n
end
local OUTS "ln_gini_mkt ln_gini_disp ln_apt_all ln_apt_top_bot"
foreach g of local GRP {
    local OUTS "`OUTS' ln_apt_`g' ln_spt_`g'"
}
foreach yv of local OUTS {
    runone `fh' "full" `yv' "1"
    runone `fh' "con_low" `yv' "con3 == 1"
    runone `fh' "con_mid" `yv' "con3 == 2"
    runone `fh' "con_high" `yv' "con3 == 3"
    runone `fh' "con_lowmid" `yv' "con3 <= 2"
    runone `fh' "era_1996_2007" `yv' "y <= 2007"
    runone `fh' "era_2010_2023x" `yv' "y >= 2010 & !inlist(y, 2020, 2021)"
    runone `fh' "con_mid_era1" `yv' "con3 == 2 & y <= 2007"
    runone `fh' "inc_low" `yv' "inc3 == 1"
    runone `fh' "inc_mid" `yv' "inc3 == 2"
    runone `fh' "inc_high" `yv' "inc3 == 3"
    runone `fh' "gdp_low" `yv' "gdp3 == 1"
    runone `fh' "gdp_mid" `yv' "gdp3 == 2"
    runone `fh' "gdp_high" `yv' "gdp3 == 3"
}
file close `fh'
log close _all
