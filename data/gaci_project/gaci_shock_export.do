clear all
set more off
set linesize 255
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI"
import delimited "gaci_panel_tourism_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
encode c, gen(isocode)
xtset isocode y
gen covid=inrange(y,2020,2021)
gen russia=(y>=2022)
gen gaci_c=lng*covid
gen gaci_r=lng*russia
gen z=tourism_int
gen z_c=tourism_int*covid
gen z_r=tourism_int*russia
capture program drop _emit
program define _emit
    args mdl v F
    di "SHOCKP|`mdl'|`v'|" _b[`v'] "|" _se[`v'] "|" 2*ttail(e(df_r),abs(_b[`v']/_se[`v'])) "|`F'|" e(N)
end
reghdfe merch_intensity lng gaci_c gaci_r lnpop, absorb(isocode y) vce(robust)
foreach v in lng gaci_c gaci_r {
    _emit OLS `v' .
}
ivreghdfe merch_intensity lnpop (lng gaci_c = z z_c), absorb(isocode y) robust
local F=e(widstat)
foreach v in lng gaci_c {
    _emit IVcovid `v' `F'
}
ivreghdfe merch_intensity lnpop (lng gaci_r = z z_r), absorb(isocode y) robust
local F=e(widstat)
foreach v in lng gaci_r {
    _emit IVrussia `v' `F'
}
ivreghdfe merch_intensity lnpop (lng gaci_c gaci_r = z z_c z_r), absorb(isocode y) robust
local F=e(widstat)
foreach v in lng gaci_c gaci_r {
    _emit IVboth `v' `F'
}
ivreghdfe merch_intensity lnpop (lng = z) if y<=2019, absorb(isocode y) robust
_emit pre2020 lng `=e(widstat)'
ivreghdfe merch_intensity lnpop (lng = z) if y>=2020, absorb(isocode y) robust
_emit shock2023 lng `=e(widstat)'
di "DONE_SHOCK_EXPORT"
