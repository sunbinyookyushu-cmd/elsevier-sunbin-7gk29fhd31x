* 27_stage_defs.do : robustness of the development-stage split to its definition.
* For each definition of low / middle / high, split-sample 2SLS (Feyrer IV, ln pop, country + year FE, cluster country)
* of ln market Gini, mean income, top-half minus bottom-half, bottom-50 share, top-10 share.
* Definitions: base year (1996 / 1996-2000 mean / full-period mean), measure (GACI_max / cwm / sum / top-airport share /
* 1996 air market access), cut (terciles / quartiles / median / within-continent terciles).
* Output: _stage_defs_results.csv (defn, group, outcome, b, se, p, kpf, N, Nc)
capture log close _all
log using "27_stage_defs_run.log", replace text
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
gen cont = substr(reg,1,2)
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
capture drop ln_spt_b50
gen ln_spt_b50 = ln_apt_b50 - ln_apt_all
capture drop ln_spt_d10
gen ln_spt_d10 = ln_apt_d10 - ln_apt_all

* ---- country-level bases ----
foreach v in gaci_max gaci_cwmean gaci_sum share_max ln_air_ma {
    bysort isocode (y): gen byte f_ = sum(!missing(`v')) == 1 & !missing(`v')
    gen t_ = `v' if f_
    bysort isocode (t_): gen `v'_96 = t_[1]
    drop f_ t_
    egen `v'_all = mean(`v'), by(isocode)
    gen t2_ = `v' if y <= 2000
    egen `v'_9600 = mean(t2_), by(isocode)
    drop t2_
}
preserve
bysort isocode: keep if _n == 1
xtile g_max96_t3 = gaci_max_96, nq(3)
xtile g_max9600_t3 = gaci_max_9600, nq(3)
xtile g_maxall_t3 = gaci_max_all, nq(3)
xtile g_cwm96_t3 = gaci_cwmean_96, nq(3)
xtile g_sum96_t3 = gaci_sum_96, nq(3)
xtile g_share96_t3 = share_max_96, nq(3)
xtile g_airma96_t3 = ln_air_ma_96, nq(3)
xtile g_max96_q4 = gaci_max_96, nq(4)
xtile g_max96_med = gaci_max_96, nq(2)
gen g_max96_wcont = .
levelsof cont, local(CC)
foreach k of local CC {
    capture drop tmp_
    quietly count if cont == "`k'"
    if r(N) >= 9 {
        xtile tmp_ = gaci_max_96 if cont == "`k'", nq(3)
        replace g_max96_wcont = tmp_ if cont == "`k'"
    }
}
capture drop tmp_
keep isocode g_*
tempfile grp
save `grp'
restore
merge m:1 isocode using `grp', nogenerate

tempname fh
file open `fh' using "_stage_defs_results.csv", write replace
file write `fh' "defn,group,outcome,b,se,p,kpf,N,Nc" _n
capture program drop runone
program define runone
    args fh defn grp yv cond
    quietly count if `cond' & !missing(`yv', ln_gaci_max, feyrer_int, lnpop)
    if r(N) < 60 exit
    capture noisily ivreghdfe `yv' lnpop (ln_gaci_max = feyrer_int) if `cond', absorb(isocode y) cluster(isocode)
    if _rc exit
    local b = _b[ln_gaci_max]
    local se = _se[ln_gaci_max]
    local p = 2*normal(-abs(`b'/`se'))
    quietly levelsof isocode if e(sample), local(cc)
    local nc : word count `cc'
    file write `fh' "`defn',`grp',`yv',`b',`se',`p',`=e(widstat)',`=e(N)',`nc'" _n
end
local OUTS "ln_gini_mkt ln_apt_all ln_apt_top_bot ln_spt_b50 ln_spt_d10"
foreach yv of local OUTS {
    foreach dv in g_max96_t3 g_max9600_t3 g_maxall_t3 g_cwm96_t3 g_sum96_t3 g_share96_t3 g_airma96_t3 g_max96_wcont {
        runone `fh' "`dv'" "1_low" `yv' "`dv' == 1"
        runone `fh' "`dv'" "2_mid" `yv' "`dv' == 2"
        runone `fh' "`dv'" "3_high" `yv' "`dv' == 3"
    }
    runone `fh' "g_max96_q4" "1_q1" `yv' "g_max96_q4 == 1"
    runone `fh' "g_max96_q4" "2_q2" `yv' "g_max96_q4 == 2"
    runone `fh' "g_max96_q4" "3_q3" `yv' "g_max96_q4 == 3"
    runone `fh' "g_max96_q4" "4_q4" `yv' "g_max96_q4 == 4"
    runone `fh' "g_max96_med" "1_below" `yv' "g_max96_med == 1"
    runone `fh' "g_max96_med" "2_above" `yv' "g_max96_med == 2"
}
file close `fh'
log close _all
