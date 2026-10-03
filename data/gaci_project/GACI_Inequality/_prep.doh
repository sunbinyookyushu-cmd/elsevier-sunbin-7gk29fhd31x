clear all
set more off
set linesize 255
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "ineq_panel.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
gen cont = substr(reg,1,2)
encode cont, gen(contid)
* baseline (first observed year) income and inequality terciles, fixed per country
bysort isocode (y): gen basepc = lnpc[1]
bysort isocode (y): gen basegini = gini_mkt[1]
bysort isocode (y): gen baseshare = share_max[1]
bysort isocode (y): gen firsty = y[1]
preserve
bysort isocode: keep if _n==1
xtile inc3 = basepc, nq(3)
xtile gini3 = basegini, nq(3)
gen conc2 = (baseshare > 0.5)
keep isocode inc3 gini3 conc2
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogen
gen post2010 = (y>=2010)
gen midinc = (inc3==2)
gen highinc = (inc3==3)
foreach v in ln_gaci_max ln_gaci_cwm ln_gaci_sum feyrer_int tourism_int {
    gen `v'_mid = `v'*midinc
    gen `v'_high = `v'*highinc
    gen `v'_post = `v'*post2010
    gen `v'_conc = `v'*conc2
    gen `v'_g2 = `v'*(gini3==2)
    gen `v'_g3 = `v'*(gini3==3)
}
gen tophub = inlist(c,"DEU","USA","FRA","NLD","GBR") | inlist(c,"CHN","CAN","SGP","ARE","THA")
sort isocode y
xtset isocode y
