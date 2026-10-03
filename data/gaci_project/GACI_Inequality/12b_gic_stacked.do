* 12b_gic_stacked.do : stacked (pooled) version of the group-specific income regressions
* One system: ln(avg pretax income of group g)_{ct} on group x ln GACI_max, group x ln pop,
* country#group FE, year#group FE, country-clustered SE. Feyrer IV = group x (a_t x ln MA_1996).
* Adds (i) joint Wald test that decile elasticities are equal, (ii) top-minus-bottom contrast,
* (iii) linear-rank trend of the elasticity across deciles.
capture log close _all
log using "12b_gic_stacked_run.log", replace text
clear all
set more off
set linesize 255
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
keep if !missing(gini_mkt)
gen cont = substr(reg,1,2)
encode cont, gen(contid)
set varabbrev off
keep isocode y contid ln_gaci_max lnpop feyrer_int tourism_int ln_apt_d1 ln_apt_d2 ln_apt_d3 ln_apt_d4 ln_apt_d5 ln_apt_d6 ln_apt_d7 ln_apt_d8 ln_apt_d9 ln_apt_d10 ln_apt_t1 ln_apt_t01
forvalues g = 1/10 {
    rename ln_apt_d`g' ln_apt`g'
}
rename ln_apt_t1 ln_apt11
rename ln_apt_t01 ln_apt12
reshape long ln_apt, i(isocode y) j(grp)
drop if missing(ln_apt) | missing(ln_gaci_max) | missing(feyrer_int) | missing(lnpop)
egen cg = group(isocode grp)
egen yg = group(y grp)
egen ygc = group(y grp contid)
forvalues g = 1/12 {
    gen x`g' = ln_gaci_max * (grp == `g')
    gen z`g' = feyrer_int * (grp == `g')
    gen w`g' = tourism_int * (grp == `g')
    gen p`g' = lnpop * (grp == `g')
}
global XL ""
global ZL ""
global WL ""
global PL ""
global PL10 ""
forvalues g = 1/12 {
    global XL "$XL x`g'"
    global ZL "$ZL z`g'"
    global WL "$WL w`g'"
    global PL "$PL p`g'"
    if `g' <= 10 global PL10 "$PL10 p`g'"
}
* centred decile rank for the trend specification (deciles only)
gen rankc = grp - 5.5
gen xr = ln_gaci_max * rankc
gen zr = feyrer_int * rankc
gen wr = tourism_int * rankc

tempname fh
file open `fh' using "_gic_stacked_results.csv", write replace
file write `fh' "block,spec,param,b,se,p,kpf,N" _n

* ---------- A. OLS stacked ----------
reghdfe ln_apt $XL $PL, absorb(cg yg) vce(cluster isocode)
local nn = e(N)
forvalues g = 1/12 {
    local b = _b[x`g']
    local se = _se[x`g']
    local p = 2*ttail(e(df_r), abs(`b'/`se'))
    file write `fh' "stacked,OLS,x`g',`b',`se',`p',.,`nn'" _n
}
test x1=x2=x3=x4=x5=x6=x7=x8=x9=x10
file write `fh' "test,OLS,eq_d1_d10,`r(F)',.,`r(p)',.,`nn'" _n
test x1=x2=x3=x4=x5=x6=x7=x8=x9=x10=x11=x12
file write `fh' "test,OLS,eq_all12,`r(F)',.,`r(p)',.,`nn'" _n
lincom x10 - x1
file write `fh' "contrast,OLS,d10_minus_d1,`r(estimate)',`r(se)',`r(p)',.,`nn'" _n
lincom (x6+x7+x8+x9+x10)/5 - (x1+x2+x3+x4+x5)/5
file write `fh' "contrast,OLS,top50_minus_bot50,`r(estimate)',`r(se)',`r(p)',.,`nn'" _n
lincom x11 - x10
file write `fh' "contrast,OLS,t1_minus_d10,`r(estimate)',`r(se)',`r(p)',.,`nn'" _n

* ---------- B. 2SLS stacked, Feyrer IV ----------
ivreghdfe ln_apt $PL ($XL = $ZL), absorb(cg yg) cluster(isocode)
local nn = e(N)
local kp = e(widstat)
forvalues g = 1/12 {
    local b = _b[x`g']
    local se = _se[x`g']
    local p = 2*normal(-abs(`b'/`se'))
    file write `fh' "stacked,IV,x`g',`b',`se',`p',`kp',`nn'" _n
}
test x1=x2=x3=x4=x5=x6=x7=x8=x9=x10
file write `fh' "test,IV,eq_d1_d10,`r(chi2)',.,`r(p)',`kp',`nn'" _n
test x1=x2=x3=x4=x5=x6=x7=x8=x9=x10=x11=x12
file write `fh' "test,IV,eq_all12,`r(chi2)',.,`r(p)',`kp',`nn'" _n
lincom x10 - x1
file write `fh' "contrast,IV,d10_minus_d1,`r(estimate)',`r(se)',`r(p)',`kp',`nn'" _n
lincom (x6+x7+x8+x9+x10)/5 - (x1+x2+x3+x4+x5)/5
file write `fh' "contrast,IV,top50_minus_bot50,`r(estimate)',`r(se)',`r(p)',`kp',`nn'" _n
lincom x11 - x10
file write `fh' "contrast,IV,t1_minus_d10,`r(estimate)',`r(se)',`r(p)',`kp',`nn'" _n

* ---------- C. 2SLS stacked, continent x year x group FE ----------
ivreghdfe ln_apt $PL ($XL = $ZL), absorb(cg ygc) cluster(isocode)
local nn = e(N)
local kp = e(widstat)
forvalues g = 1/12 {
    local b = _b[x`g']
    local se = _se[x`g']
    local p = 2*normal(-abs(`b'/`se'))
    file write `fh' "stacked,IV_contyear,x`g',`b',`se',`p',`kp',`nn'" _n
}
test x1=x2=x3=x4=x5=x6=x7=x8=x9=x10
file write `fh' "test,IV_contyear,eq_d1_d10,`r(chi2)',.,`r(p)',`kp',`nn'" _n
lincom x10 - x1
file write `fh' "contrast,IV_contyear,d10_minus_d1,`r(estimate)',`r(se)',`r(p)',`kp',`nn'" _n
lincom (x6+x7+x8+x9+x10)/5 - (x1+x2+x3+x4+x5)/5
file write `fh' "contrast,IV_contyear,top50_minus_bot50,`r(estimate)',`r(se)',`r(p)',`kp',`nn'" _n

* ---------- D. 2SLS stacked, tourism IV ----------
ivreghdfe ln_apt $PL ($XL = $WL), absorb(cg yg) cluster(isocode)
local nn = e(N)
local kp = e(widstat)
forvalues g = 1/12 {
    local b = _b[x`g']
    local se = _se[x`g']
    local p = 2*normal(-abs(`b'/`se'))
    file write `fh' "stacked,IV_tourism,x`g',`b',`se',`p',`kp',`nn'" _n
}
test x1=x2=x3=x4=x5=x6=x7=x8=x9=x10
file write `fh' "test,IV_tourism,eq_d1_d10,`r(chi2)',.,`r(p)',`kp',`nn'" _n
lincom x10 - x1
file write `fh' "contrast,IV_tourism,d10_minus_d1,`r(estimate)',`r(se)',`r(p)',`kp',`nn'" _n

* ---------- E. linear trend across deciles (deciles only) ----------
preserve
keep if grp <= 10
reghdfe ln_apt ln_gaci_max xr $PL10, absorb(cg yg) vce(cluster isocode)
local nn = e(N)
local b = _b[ln_gaci_max]
local se = _se[ln_gaci_max]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
file write `fh' "trend,OLS,level_at_median,`b',`se',`p',.,`nn'" _n
local b = _b[xr]
local se = _se[xr]
local p = 2*ttail(e(df_r), abs(`b'/`se'))
file write `fh' "trend,OLS,slope_per_decile,`b',`se',`p',.,`nn'" _n
ivreghdfe ln_apt $PL10 (ln_gaci_max xr = feyrer_int zr), absorb(cg yg) cluster(isocode)
local nn = e(N)
local kp = e(widstat)
local b = _b[ln_gaci_max]
local se = _se[ln_gaci_max]
local p = 2*normal(-abs(`b'/`se'))
file write `fh' "trend,IV,level_at_median,`b',`se',`p',`kp',`nn'" _n
local b = _b[xr]
local se = _se[xr]
local p = 2*normal(-abs(`b'/`se'))
file write `fh' "trend,IV,slope_per_decile,`b',`se',`p',`kp',`nn'" _n
ivreghdfe ln_apt $PL10 (ln_gaci_max xr = feyrer_int zr), absorb(cg ygc) cluster(isocode)
local nn = e(N)
local kp = e(widstat)
local b = _b[ln_gaci_max]
local se = _se[ln_gaci_max]
local p = 2*normal(-abs(`b'/`se'))
file write `fh' "trend,IV_contyear,level_at_median,`b',`se',`p',`kp',`nn'" _n
local b = _b[xr]
local se = _se[xr]
local p = 2*normal(-abs(`b'/`se'))
file write `fh' "trend,IV_contyear,slope_per_decile,`b',`se',`p',`kp',`nn'" _n
ivreghdfe ln_apt $PL10 (ln_gaci_max xr = tourism_int wr), absorb(cg yg) cluster(isocode)
local nn = e(N)
local kp = e(widstat)
local b = _b[ln_gaci_max]
local se = _se[ln_gaci_max]
local p = 2*normal(-abs(`b'/`se'))
file write `fh' "trend,IV_tourism,level_at_median,`b',`se',`p',`kp',`nn'" _n
local b = _b[xr]
local se = _se[xr]
local p = 2*normal(-abs(`b'/`se'))
file write `fh' "trend,IV_tourism,slope_per_decile,`b',`se',`p',`kp',`nn'" _n
restore

file close `fh'
log close _all
