* 34_components.do : which component of hub connectivity carries the inequality effect?
* Hub components (ln): seat capacity (cap), number of connections (deg), eigenvector centrality (eig),
* closeness (close), flow betweenness (betw), regional importance (regimp).
*  A. first stage: which component does the Feyrer instrument move?
*  B. each component as treatment (2SLS Feyrer) on ln market Gini / disposable Gini / bottom-50 share / top-bot.
*  C. horse race: component instrumented, ln hub capacity as control (topology net of scale), and vice versa.
*  D. OLS with all components jointly.
* Output: _components_results.csv (block, item, outcome, term, b, se, p, kpf, N)
capture log close _all
log using "34_components_run.log", replace text
clear all
set more off
set linesize 255
set varabbrev off
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_Inequality"
import delimited "_hub_components.csv", clear varnames(1) encoding("utf-8")
tempfile hc
save `hc'
import delimited "ineq_panel_ext.csv", clear varnames(1) encoding("utf-8")
ds c reg, not
destring `r(varlist)', replace force
merge 1:1 c y using `hc', keep(1 3) nogenerate
encode c, gen(isocode)
xtset isocode y
keep if !missing(gini_mkt)
gen ln_apt_top_bot = (ln_apt_d6 + ln_apt_d7 + ln_apt_d8 + ln_apt_d9 + ln_apt_d10)/5 - (ln_apt_d1 + ln_apt_d2 + ln_apt_d3 + ln_apt_d4 + ln_apt_d5)/5
capture drop ln_spt_b50
gen ln_spt_b50 = ln_apt_b50 - ln_apt_all
foreach k in gaci deg cap eig close betw regimp {
    gen ln_hub_`k' = ln(hub_`k') if hub_`k' > 0
}
foreach k in deg cap eig close betw {
    gen ln_rest_`k' = ln(rest_`k') if rest_`k' > 0
}
* sanity: hub_gaci should equal gaci_max
gen chk = abs(hub_gaci - gaci_max)
summarize chk

tempname fh
file open `fh' using "_components_results.csv", write replace
file write `fh' "block,item,outcome,term,b,se,p,kpf,N" _n
capture program drop wr
program define wr
    args fh blk item yv term kp
    local b = _b[`term']
    local se = _se[`term']
    local p = 2*normal(-abs(`b'/`se'))
    file write `fh' "`blk',`item',`yv',`term',`b',`se',`p',`kp',`=e(N)'" _n
end
local COMP "gaci cap deg eig close betw regimp"
* ---- A. first stages ----
foreach k of local COMP {
    quietly reghdfe ln_hub_`k' feyrer_int lnpop, absorb(isocode y) vce(cluster isocode)
    wr `fh' A firststage ln_hub_`k' feyrer_int .
}
* ---- B. each component as treatment ----
foreach yv in ln_gini_mkt ln_gini_disp ln_spt_b50 ln_apt_top_bot {
    foreach k of local COMP {
        capture noisily ivreghdfe `yv' lnpop (ln_hub_`k' = feyrer_int), absorb(isocode y) cluster(isocode)
        if _rc == 0 wr `fh' B iv_single `yv' ln_hub_`k' `=e(widstat)'
        quietly reghdfe `yv' ln_hub_`k' lnpop, absorb(isocode y) vce(cluster isocode)
        wr `fh' B ols_single `yv' ln_hub_`k' .
    }
    * ---- C. horse race: topology component instrumented, capacity as control; capacity instrumented, component as control ----
    foreach k in deg eig close betw {
        capture noisily ivreghdfe `yv' lnpop ln_hub_cap (ln_hub_`k' = feyrer_int), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            wr `fh' C topo_iv_cap_ctrl_`k' `yv' ln_hub_`k' `=e(widstat)'
            wr `fh' C topo_iv_cap_ctrl_`k' `yv' ln_hub_cap `=e(widstat)'
        }
        capture noisily ivreghdfe `yv' lnpop ln_hub_`k' (ln_hub_cap = feyrer_int), absorb(isocode y) cluster(isocode)
        if _rc == 0 {
            wr `fh' C cap_iv_topo_ctrl_`k' `yv' ln_hub_cap `=e(widstat)'
            wr `fh' C cap_iv_topo_ctrl_`k' `yv' ln_hub_`k' `=e(widstat)'
        }
    }
    * ---- D. OLS with all components jointly ----
    quietly reghdfe `yv' ln_hub_cap ln_hub_deg ln_hub_eig ln_hub_close ln_hub_betw lnpop, absorb(isocode y) vce(cluster isocode)
    foreach k in cap deg eig close betw {
        wr `fh' D ols_joint `yv' ln_hub_`k' .
    }
    * ---- E. hub component vs rest-of-network component (OLS, joint) ----
    foreach k in cap betw eig {
        quietly reghdfe `yv' ln_hub_`k' ln_rest_`k' lnpop, absorb(isocode y) vce(cluster isocode)
        wr `fh' E ols_hub_vs_rest_`k' `yv' ln_hub_`k' .
        wr `fh' E ols_hub_vs_rest_`k' `yv' ln_rest_`k' .
    }
}
file close `fh'
log close _all
