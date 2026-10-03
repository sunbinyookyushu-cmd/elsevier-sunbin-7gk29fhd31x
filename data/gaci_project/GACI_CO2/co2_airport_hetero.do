*==============================================================================
* co2_airport_hetero.do   (LZ comment 2, 2026-09-03)
* Airport-level heterogeneity, within-country design:
*   reghdfe y ln_gaci, absorb(apid cyr) vce(cluster apid)   [airport FE + country x year FE]
* Groups (1996 baseline):
*   hub_nat  = country's largest airport by 1996 seat-km
*   top5 / top1 = global top 5 / 1 percent by 1996 seat-km
*   skm3     = baseline seat-km tercile;  gac3 = baseline GACI tercile
*   orient   = baseline international share of seat-km: 0 / (0, .5] / > .5
*   mreg     = macro region (from Region code);  inc3 = host-country income tercile
* Topology-only regressors (eigenvector, closeness, betweenness) as a safeguard
* against the capacity component embedded in airport GACI.
* Export: _airport_hetero.csv (panel grp outc b se p nn nap)
*==============================================================================
clear all
set more off
set varabbrev off
set linesize 255
version 14
cd "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2"

* ---- host-country income tercile (earliest lnpc, as in co2_feyrer_hetero.do) ----
import delimited "../gaci_panel_combined.csv", clear varnames(1) encoding("utf-8")
keep c y lnpc
destring y lnpc, replace force
sort c y
bysort c (y): gen byte first_pc = sum(!missing(lnpc)) == 1 & !missing(lnpc)
keep if first_pc
keep c lnpc
rename lnpc lnpc0
xtile inc3 = lnpc0, nq(3)
rename c iso3
tempfile inc
save `inc'

* ---- topology components from the GACI construction panel ----
import delimited "../GACI1996_2024_new_panel_data.csv", clear varnames(1) encoding("utf-8")
capture rename ïyear year
capture rename v1 year
rename airport airport_iata
keep year airport_iata degree totalcapacity eigen norclose norbetweenness
destring year degree totalcapacity eigen norclose norbetweenness, replace force
duplicates drop airport_iata year, force
gen ln_eig = ln(eigen) if eigen > 0
gen ln_close = ln(norclose) if norclose > 0
gen ln_betw = ln(norbetweenness) if norbetweenness > 0
gen ln_deg = ln(degree) if degree > 0
gen ln_capg = ln(totalcapacity) if totalcapacity > 0
tempfile topo
save `topo'

* ---- airport panel ----
import delimited "airport_co2_panel.csv", clear varnames(1) encoding("utf-8")
ds airport_iata iso3 region, not
destring `r(varlist)', replace force
merge 1:1 airport_iata year using `topo', keep(1 3) nogenerate
merge m:1 iso3 using `inc', keep(1 3) nogenerate
encode airport_iata, gen(apid)
encode iso3, gen(cid)
egen cyr = group(cid year)
sort apid year

* ---- baseline (1996, else earliest year with traffic) characteristics ----
gen byte hastraffic = dep_seat_km > 0 & !missing(dep_seat_km)
bysort apid (year): gen byte firstt = sum(hastraffic) == 1 & hastraffic
gen skm0_ = dep_seat_km if firstt
gen gac0_ = gaci if firstt
gen int0_ = intl_share_skm if firstt
bysort apid: egen skm0 = max(skm0_)
bysort apid: egen gac0 = max(gac0_)
bysort apid: egen int0 = max(int0_)
drop skm0_ gac0_ int0_ firstt
* national largest airport
bysort cid: egen skm0max = max(skm0)
gen byte hub_nat = skm0 == skm0max & !missing(skm0)
* global top shares
preserve
bysort apid: keep if _n == 1
keep apid skm0 gac0 int0
xtile skm3 = skm0 if skm0 > 0, nq(3)
xtile gac3 = gac0, nq(3)
gen byte top5 = 0
gen byte top1 = 0
_pctile skm0 if skm0 > 0, p(95 99)
replace top5 = skm0 >= r(r1) & !missing(skm0)
replace top1 = skm0 >= r(r2) & !missing(skm0)
gen byte orient = 0 if int0 == 0
replace orient = 1 if int0 > 0 & int0 <= .5
replace orient = 2 if int0 > .5 & !missing(int0)
keep apid skm3 gac3 top5 top1 orient
tempfile grp
save `grp'
restore
merge m:1 apid using `grp', nogenerate
gen mreg = substr(region, 1, 2)

capture which reghdfe
if _rc {
    ssc install ftools, replace
    ssc install reghdfe, replace
}

tempname R
postfile `R' str12 panel str16 grp str16 outc double(b se p) long(nn nap) using "_aph_tmp", replace
global RH `R'

program define runcell
    args panel grp yv xv cond
    quietly count if (`cond') & !missing(`yv', `xv')
    if r(N) < 200 {
        di as err "SKIP `panel' `grp' `yv': N = " r(N)
        exit
    }
    capture noisily reghdfe `yv' `xv' if `cond', absorb(apid cyr) vce(cluster apid)
    if _rc exit
    local bb = _b[`xv']
    local sse = _se[`xv']
    local pp = 2*normal(-abs(`bb'/`sse'))
    di "APH [`panel'] `grp' `yv' on `xv': b = " %8.3f `bb' " (se " %7.3f `sse' ")  N = " %8.0f e(N) "  airports = " %6.0f e(N_clust)
    post $RH ("`panel'") ("`grp'") ("`yv'") (`bb') (`sse') (`pp') (e(N)) (e(N_clust))
end

foreach yv in ln_co2 ln_skm ln_intensity intl_share_skm {
    runcell ALL all `yv' ln_gaci "1==1"
    * hub status
    runcell HUB nat_hub `yv' ln_gaci "hub_nat==1"
    runcell HUB non_hub `yv' ln_gaci "hub_nat==0"
    runcell HUB top5 `yv' ln_gaci "top5==1"
    runcell HUB not_top5 `yv' ln_gaci "top5==0"
    runcell HUB top1 `yv' ln_gaci "top1==1"
    runcell HUB not_top1 `yv' ln_gaci "top1==0"
    * baseline connectivity
    foreach g in 1 2 3 {
        runcell GAC gac`g' `yv' ln_gaci "gac3==`g'"
        runcell SKM skm`g' `yv' ln_gaci "skm3==`g'"
        runcell INC inc`g' `yv' ln_gaci "inc3==`g'"
    }
    * orientation
    runcell ORI domestic_only `yv' ln_gaci "orient==0"
    runcell ORI mixed `yv' ln_gaci "orient==1"
    runcell ORI international `yv' ln_gaci "orient==2"
    * region
    foreach r in EU AS AF LA ME NA SW {
        runcell REG `r' `yv' ln_gaci `"mreg=="`r'""'
    }
    * topology-only regressors, full sample
    runcell TOPO eig `yv' ln_eig "1==1"
    runcell TOPO close `yv' ln_close "1==1"
    runcell TOPO betw `yv' ln_betw "1==1"
    runcell TOPO deg `yv' ln_deg "1==1"
}

* pooled interaction tests (ln CO2): hub x ln_gaci
gen g_x_hub = ln_gaci * hub_nat
gen g_x_top5 = ln_gaci * top5
reghdfe ln_co2 ln_gaci g_x_hub, absorb(apid cyr) vce(cluster apid)
post $RH ("INT") ("hub_x_gaci") ("ln_co2") (_b[g_x_hub]) (_se[g_x_hub]) (2*normal(-abs(_b[g_x_hub]/_se[g_x_hub]))) (e(N)) (e(N_clust))
di "INT hub x gaci (ln_co2): " %8.3f _b[g_x_hub] " (se " %7.3f _se[g_x_hub] ")"
reghdfe ln_co2 ln_gaci g_x_top5, absorb(apid cyr) vce(cluster apid)
post $RH ("INT") ("top5_x_gaci") ("ln_co2") (_b[g_x_top5]) (_se[g_x_top5]) (2*normal(-abs(_b[g_x_top5]/_se[g_x_top5]))) (e(N)) (e(N_clust))
di "INT top5 x gaci (ln_co2): " %8.3f _b[g_x_top5] " (se " %7.3f _se[g_x_top5] ")"
reghdfe ln_intensity ln_gaci g_x_hub, absorb(apid cyr) vce(cluster apid)
post $RH ("INT") ("hub_x_gaci") ("ln_intensity") (_b[g_x_hub]) (_se[g_x_hub]) (2*normal(-abs(_b[g_x_hub]/_se[g_x_hub]))) (e(N)) (e(N_clust))

* group sizes (for the note)
tab hub_nat if year == 2023
tab top5 if year == 2023
tab orient if year == 2023

postclose `R'
preserve
use "_aph_tmp", clear
list, clean noobs
export delimited "_airport_hetero.csv", replace
restore
erase "_aph_tmp.dta"

* export baseline groups for the concentration script
keep airport_iata iso3 year hub_nat top5 top1 skm3 gac3 inc3 orient mreg skm0 gac0
bysort airport_iata: keep if _n == 1
drop year
export delimited "_airport_groups.csv", replace

di _n "DONE_AIRPORT_HETERO"
