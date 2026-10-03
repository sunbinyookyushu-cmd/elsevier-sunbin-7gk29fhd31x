* 16_acreg_check.do : cross-check of 15_conley_se.py with acreg (Colella, Lalive, Sakalli & Thoenig 2019)
* Headline 2SLS, country + year FE, Bartlett kernels: spatial cutoff 2000 km, serial cutoff all years (27) and 10.
clear all
ssc install hdfe, replace
set more off
set linesize 255
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "_panel_coords.csv", clear varnames(1) encoding("utf-8")
encode c, gen(isocode)
tempname fh
file open `fh' using "_acreg_results.csv", write replace
file write `fh' "outcome,spec,b,se" _n
foreach yv in ln_gini_mkt ln_gini_disp {
    acreg `yv' lnpop (ln_gaci_max = feyrer_int), id(isocode) time(y) spatial latitude(lat) longitude(lon) dist(2000) lagcutoff(30) bartlett hac pfe1(isocode) pfe2(y)
    file write `fh' "`yv',acreg_D2000_Lall,`=_b[ln_gaci_max]',`=_se[ln_gaci_max]'" _n
    acreg `yv' lnpop (ln_gaci_max = feyrer_int), id(isocode) time(y) spatial latitude(lat) longitude(lon) dist(2000) lagcutoff(10) bartlett hac pfe1(isocode) pfe2(y)
    file write `fh' "`yv',acreg_D2000_L10,`=_b[ln_gaci_max]',`=_se[ln_gaci_max]'" _n
    acreg `yv' lnpop (ln_gaci_max = feyrer_int), id(isocode) time(y) spatial latitude(lat) longitude(lon) dist(1000) lagcutoff(30) bartlett hac pfe1(isocode) pfe2(y)
    file write `fh' "`yv',acreg_D1000_Lall,`=_b[ln_gaci_max]',`=_se[ln_gaci_max]'" _n
}
file close `fh'

