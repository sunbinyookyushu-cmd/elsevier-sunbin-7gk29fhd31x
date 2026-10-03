* =====================================================================================
* 04_regional_benefits.do
* Regional cost of connectivity loss + benefit / cost accounting of the aviation taxes
* Companion to 01_main.do (same stacks, same 8 European events, same FE logic)
*
* Design. The tax is national, the connectivity loss is local. Within the treated country,
* regions whose airport catchment is dominated by small airports (the ones that lose seats,
* destinations and GACI in Tables 2-3) are compared with hub regions. Country x month x event
* FE absorb the tax's direct demand effect and all macro shocks, so the identifying variation
* is region "exposure" x post. Control-country regions carry the same exposure x post term as
* a placebo for generic small-airport trends (triple difference).
*
* Sections
*   1. Catchment weights: NUTS2 centroid -> airports within `radius' km, weight exp(-d/`decay')
*   2. Event calendar, treated / border countries, per-airport size and pre-period seats
*   3. Region exposure (small-airport seat share, predicted seat loss) and regional connectivity
*   4. Eurostat: monthly nights (tour_occ_nim), annual employment (lfst_r_lfe2en2), GDP (nama_10r_2gdp)
*   5. Monthly regional panel: foreign / domestic nights, reduced form, event time, 2SLS on connectivity
*   6. Annual regional panel: nights, employment (NACE I and total), GDP per head, 2SLS on regional GACI
*   7. Benefit / cost table by event and in total: tonnes abated (weighted spec, with CI), carbon value,
*      tax revenue, Harberger deadweight loss, foreign-night loss valued at `spend' EUR, jobs, cost per tonne
*
* Inputs you must place in stata_paper\ (headers exactly as written):
*   airports.csv          `apid',lat,lon        one row per airport, same id as in the stacks
*   nuts2_centroids.csv   nuts2,lat,lon         NUTS2 (2021 codes), label point or centroid, from GISCO
*       python one-liner:  import geopandas as g; d=g.read_file('NUTS_LB_2021_4326.geojson'); d=d[d.LEVL_CODE==2];
*                          d.assign(nuts2=d.NUTS_ID,lat=d.geometry.y,lon=d.geometry.x)[['nuts2','lat','lon']].to_csv('nuts2_centroids.csv',index=False)
*   Eurostat tables are downloaded when `dl' = 1, otherwise <code>.tsv must already be in the folder
*
* FILL IN the three locals marked <<, VERIFY the comments marked VERIFY. Everything else runs as is.
* Untested against the data: read the log once, the first error names the variable that differs.
* =====================================================================================
clear all
set more off
set linesize 200
cd "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_FuelShock\stata_paper"
cap log close
log using "04_regional_benefits_run.log", replace text

* ---------- 0. Parameters
local apid    ""           // << airport id shared by stack_month.dta, stack_year.dta, airports.csv; leave "" to auto-detect
local tvar    ""           // << calendar month variable (Stata %tm) in stack_month.dta;            leave "" to auto-detect
local yvar    ""           // << calendar year variable in stack_year.dta;                            leave "" to auto-detect
local radius  100          // catchment radius, km
local decay   50           // distance decay scale, km
local lf      0.80         // load factor: seats -> passengers
local scc     100          // carbon value, EUR / tCO2 (a 200 column is also reported)
local spend   120          // spending per foreign tourist night, EUR
local co2_t   1            // multiply exp(ln_co2) by this to get tonnes: 1 if tonnes, 0.001 if kg   VERIFY
local agegrp  "Y15-64"     // LFS age group for employment                                          VERIFY
local dl      1            // 1 download Eurostat TSVs, 0 reuse files in the folder

foreach p in reghdfe ftools estout geodist ivreghdfe ivreg2 ranktest {
    cap which `p'
    if _rc ssc install `p'
}
estimates clear
if `dl' == 1 local dlopt "download"

* ---------- auto-detect the three id / time variables when left blank (first candidate found wins)
cap program drop pick_var
program define pick_var, rclass
    syntax, file(string) cands(string) [given(string)]
    if "`given'" != "" {
        return local v "`given'"
        exit
    }
    preserve
    use in 1 using "`file'", clear
    local found ""
    foreach c of local cands {
        cap confirm variable `c'
        if _rc == 0 & "`found'" == "" local found "`c'"
    }
    restore
    if "`found'" == "" {
        di as error "none of (`cands') found in `file': set the local at the top of the file"
        error 111
    }
    return local v "`found'"
end
pick_var, file("stack_month.dta") given("`apid'") cands("iata icao apt airport airport_id ap_id apid ap code node id")
local apid "`r(v)'"
pick_var, file("stack_month.dta") given("`tvar'") cands("ym mdate month date t period tm")
local tvar "`r(v)'"
pick_var, file("stack_year.dta") given("`yvar'") cands("year y yr cal_year")
local yvar "`r(v)'"
di as text _n "using airport id = `apid', month = `tvar', year = `yvar'" _n

* ---------- programs
cap program drop mk_ctrl
program define mk_ctrl
    * never-taxed / European control countries, same list as 01_main.do (inlist takes at most 10 strings)
    gen ctrl_eur = inlist(iso3, "DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE") | inlist(iso3, "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN") | inlist(iso3, "HRV", "MLT")
end

cap program drop get_eurostat
program define get_eurostat
    * get_eurostat <code> [, download keepif(<condition on k1..kN>)]
    * returns long data: k1..kN (the dimension values in the TSV key order), period (string), val
    syntax anything(name=code), [download keepif(string)]
    if "`download'" != "" {
        copy "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/`code'?format=TSV&compressed=false" "`code'.tsv", replace
    }
    import delimited using "`code'.tsv", delimiter(tab) varnames(nonames) stringcols(_all) clear
    qui describe, varlist
    local last : word count `r(varlist)'
    forvalues j = 2/`last' {
        local h = strtrim(v`j'[1])
        local h = subinstr("`h'", "-", "_", .)
        rename v`j' t_`h'
    }
    di as text "`code' key order: " v1[1]
    drop in 1
    rename v1 key
    split key, parse(",") gen(k)
    drop key
    if `"`keepif'"' != "" keep if `keepif'
    qui ds k*
    reshape long t_, i(`r(varlist)') j(period) string
    gen double val = real(word(t_, 1))
    drop t_
end

cap program drop iso2to3
program define iso2to3
    syntax, from(name) gen(name)
    gen `gen' = ""
    local map "AT:AUT BE:BEL BG:BGR CH:CHE CY:CYP CZ:CZE DE:DEU DK:DNK EE:EST EL:GRC ES:ESP FI:FIN FR:FRA HR:HRV HU:HUN IE:IRL IS:ISL IT:ITA LI:LIE LT:LTU LU:LUX LV:LVA MT:MLT NL:NLD NO:NOR PL:POL PT:PRT RO:ROU SE:SWE SI:SVN SK:SVK UK:GBR"
    foreach p of local map {
        gettoken a b : p, parse(":")
        local b = subinstr("`b'", ":", "", .)
        replace `gen' = "`b'" if `from' == "`a'"
    }
end

* =====================================================================================
* 1. Catchment weights
* =====================================================================================
import delimited using "airports.csv", varnames(1) clear
keep `apid' lat lon
tempfile ap
save `ap'
import delimited using "nuts2_centroids.csv", varnames(1) clear
rename (lat lon) (rlat rlon)
cross using `ap'
geodist rlat rlon lat lon, gen(dkm)
keep if dkm <= `radius'
gen double wdist = exp(-dkm / `decay')
keep nuts2 `apid' dkm wdist
save "catch.dta", replace

* =====================================================================================
* 2. Event calendar, treated / border countries, airport characteristics, size coefficients
* =====================================================================================
use "stack_month.dta", clear
keep if stk != 0
cap rename `tvar' ym
format ym %tm
collapse (max) post1 post2 pre36_25 pre24_13 donut, by(stk ym)
save "cal_stk.dta", replace

use "stack_month.dta", clear
keep if stk != 0 & treat == 1
collapse (max) dose, by(stk iso3)
bysort stk: gen n = _N
qui count if n > 1
if r(N) > 0 di as error "VERIFY: more than one treated country in an event, first one kept"
bysort stk: keep if _n == 1
rename iso3 iso3_tr
keep stk iso3_tr dose
save "ev_treat.dta", replace

use "stack_month.dta", clear
keep if stk != 0
collapse (max) w0 sz_small sz_mid sz_large treat border, by(stk `apid' iso3)
save "ap_char.dta", replace

* Table 2 size-tercile seat coefficients -> predicted seat loss by region
use "stack_month.dta", clear
cap rename `tvar' ym
mk_ctrl
gen tp = treat * post1
gen bp = border * post1
gen tp_small = sz_small * post1
gen tp_mid   = sz_mid   * post1
gen tp_large = sz_large * post1
reghdfe ln_seats tp_small tp_mid tp_large bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_s = _b[tp_small]
scalar b_m = _b[tp_mid]
scalar b_l = _b[tp_large]
* weighted seat and CO2 effects for the benefit table (Table 2 col 2, Table 4 col 2)
reghdfe ln_seats tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_seats_w  = _b[tp]
scalar se_seats_w = _se[tp]
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0 & w0 > 0 [aw = w0], absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_co2_w  = _b[tp]
scalar se_co2_w = _se[tp]
reghdfe ln_co2 tp bp lngdp lnpop if eur == 1 & stk != 0 & donut == 0 & (treat == 1 | border == 1 | ctrl_eur == 1) & post2 == 0, absorb(fe_u fe_t) vce(cluster iso3n)
scalar b_co2_u  = _b[tp]
scalar se_co2_u = _se[tp]

* =====================================================================================
* 3. Region exposure and regional connectivity
* =====================================================================================
use "ap_char.dta", clear
joinby `apid' using "catch.dta"
gen double ww   = wdist * w0
gen double ww_s = ww * sz_small
gen double ww_m = ww * sz_mid
gen double ww_l = ww * sz_large
gen double ww_b = ww * border
collapse (sum) ww ww_s ww_m ww_l ww_b (max) border_r = border, by(stk nuts2)
gen expo_small = ww_s / ww
gen expo_mid   = ww_m / ww
gen expo_large = ww_l / ww
gen pred_loss  = -(expo_small * b_s + expo_mid * b_m + expo_large * b_l)   // predicted first-year seat loss, log points
rename ww catch_seats
keep stk nuts2 expo_small expo_mid expo_large pred_loss catch_seats border_r
save "reg_expo.dta", replace

* monthly: distance-weighted catchment seats and CO2
use "stack_month.dta", clear
keep if stk != 0
cap rename `tvar' ym
keep stk `apid' ym ln_seats ln_co2
gen double seats = exp(ln_seats)
gen double co2   = exp(ln_co2)
joinby `apid' using "catch.dta"
gen double ws = wdist * seats
gen double wc = wdist * co2
collapse (sum) ws wc, by(stk nuts2 ym)
gen ln_conn_seats = ln(ws)
gen ln_conn_co2   = ln(wc)
save "reg_conn_m.dta", replace

* annual: seat-weighted catchment GACI and destinations
use "stack_year.dta", clear
keep if stk != 0
cap rename `yvar' year
keep stk `apid' year k post1 ln_gaci ln_deg w0
gen double gaci = exp(ln_gaci)
gen double deg  = exp(ln_deg)
joinby `apid' using "catch.dta"
gen double wk = wdist * w0
gen double g  = wk * gaci
gen double d  = wk * deg
collapse (sum) g d wk (max) k post1, by(stk nuts2 year)
gen ln_conn_gaci = ln(g / wk)
gen ln_conn_deg  = ln(d / wk)
save "reg_conn_y.dta", replace
collapse (max) k post1, by(stk year)
save "cal_y.dta", replace

* =====================================================================================
* 4. Eurostat regional series
* =====================================================================================
* nights by NUTS2, monthly, residents / non-residents, all accommodation (I551-I553)
* VERIFY key order printed in the log: expected freq,c_resid,unit,nace_r2,geo -> k1..k5
get_eurostat tour_occ_nim, `dlopt' keepif(`"k3 == "NR" & k4 == "I551-I553" & strlen(k5) == 4"')
rename k5 nuts2
gen ym = ym(real(substr(period, 1, 4)), real(substr(period, 6, 2)))
format ym %tm
keep nuts2 k2 ym val
reshape wide val, i(nuts2 ym) j(k2) string
rename (valDOM valFOR valTOTAL) (nights_dom nights_for nights_tot)
save "tour_m.dta", replace
gen year = year(dofm(ym))
bysort nuts2 year: gen nm = _N
keep if nm == 12
collapse (sum) nights_dom nights_for nights_tot, by(nuts2 year)
save "tour_y.dta", replace

* employment by NUTS2, NACE Rev.2, annual (from 2008): total and accommodation + food (I)
* VERIFY key order: expected freq,sex,age,nace_r2,unit,geo -> k1..k6
cap noisily {
    get_eurostat lfst_r_lfe2en2, `dlopt' keepif(`"k2 == "T" & k3 == "`agegrp'" & inlist(k4, "TOTAL", "I") & strlen(k6) == 4"')
    rename k6 nuts2
    gen year = real(period)
    keep nuts2 k4 year val
    reshape wide val, i(nuts2 year) j(k4) string
    rename (valTOTAL valI) (emp_tot emp_I)       // thousands
    save "emp_y.dta", replace
}

* GDP per head by NUTS2, annual
* VERIFY key order: expected freq,unit,geo -> k1..k3
cap noisily {
    get_eurostat nama_10r_2gdp, `dlopt' keepif(`"k2 == "EUR_HAB" & strlen(k3) == 4"')
    rename k3 nuts2
    gen year = real(period)
    keep nuts2 year val
    rename val gdp_pc
    save "gdp_y.dta", replace
}

* =====================================================================================
* 5. Monthly regional panel
* =====================================================================================
use "cal_stk.dta", clear
joinby ym using "tour_m.dta"
merge m:1 stk using "ev_treat.dta", nogen keep(match)
merge m:1 stk nuts2 using "reg_expo.dta", nogen keep(match)
merge 1:1 stk nuts2 ym using "reg_conn_m.dta", nogen keep(master match)
gen iso2 = substr(nuts2, 1, 2)
iso2to3, from(iso2) gen(iso3)
gen treat_c  = (iso3 == iso3_tr)
mk_ctrl
keep if (treat_c == 1 | ctrl_eur == 1) & border_r == 0          // border-ring regions dropped
gen moy = month(dofm(ym))
egen fe_r  = group(stk nuts2 moy)        // region x calendar month x event
egen fe_ct = group(stk iso3 ym)          // country x month x event
egen nuts2n = group(nuts2)
foreach y in nights_for nights_dom nights_tot {
    gen ln_`y' = ln(`y')
}
* exposure x post, treated and control
gen tpx  = treat_c * post1 * expo_small
gen cpx  = (1 - treat_c) * post1 * expo_small
gen tpl  = treat_c * post1 * pred_loss
gen cpl  = (1 - treat_c) * post1 * pred_loss
* event time
foreach w in pre36_25 pre24_13 post1 post2 {
    gen TX_`w' = treat_c * `w' * expo_small
    gen CX_`w' = (1 - treat_c) * `w' * expo_small
}
save "panel_reg_m.dta", replace

local samp "donut == 0 & post2 == 0"
* reduced form, small-airport exposure
reghdfe ln_nights_for tpx cpx if `samp', absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R1_for
reghdfe ln_nights_dom tpx cpx if `samp', absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R2_dom
reghdfe ln_nights_tot tpx cpx if `samp', absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R3_tot
reghdfe ln_nights_for tpx cpx if `samp' [aw = catch_seats], absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R4_for_wt
* reduced form, predicted seat loss (coefficient = nights elasticity to predicted seat loss)
reghdfe ln_nights_for tpl cpl if `samp', absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R5_for_pl
reghdfe ln_nights_dom tpl cpl if `samp', absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R6_dom_pl
esttab R1_for R2_dom R3_tot R4_for_wt R5_for_pl R6_dom_pl using "R1_regional_nights.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx tpl cpl) stats(N N_clust, labels("Observations" "Regions")) title("Regional nights: exposure to small-airport connectivity loss, within treated country")
esttab R1_for R2_dom R3_tot R4_for_wt R5_for_pl R6_dom_pl, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx tpl cpl) stats(N N_clust)
estimates restore R1_for
scalar b_tpx_for  = _b[tpx]
scalar se_tpx_for = _se[tpx]

* event time
reghdfe ln_nights_for TX_pre36_25 TX_pre24_13 TX_post1 TX_post2 CX_pre36_25 CX_pre24_13 CX_post1 CX_post2 if donut == 0, absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R7_es_for
reghdfe ln_nights_dom TX_pre36_25 TX_pre24_13 TX_post1 TX_post2 CX_pre36_25 CX_pre24_13 CX_post1 CX_post2 if donut == 0, absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R8_es_dom
esttab R7_es_for R8_es_dom using "R2_regional_eventtime.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(TX_*) stats(N N_clust, labels("Observations" "Regions")) title("Regional nights, event time: exposure x window, treated country")
esttab R7_es_for R8_es_dom, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(TX_*) stats(N N_clust)

* 2SLS: nights on catchment seats, instrumented by exposure x post in the treated country
ivreghdfe ln_nights_for cpx (ln_conn_seats = tpx) if `samp', absorb(fe_r fe_ct) cluster(nuts2n) first
estimates store R9_iv_for
ivreghdfe ln_nights_dom cpx (ln_conn_seats = tpx) if `samp', absorb(fe_r fe_ct) cluster(nuts2n)
estimates store R10_iv_dom
reghdfe ln_conn_seats tpx cpx if `samp', absorb(fe_r fe_ct) vce(cluster nuts2n)
estimates store R11_fs
esttab R11_fs R9_iv_for R10_iv_dom using "R3_regional_iv.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx ln_conn_seats) stats(N N_clust widstat, labels("Observations" "Regions" "KP F")) title("Regional nights and catchment seats: first stage and 2SLS")
esttab R11_fs R9_iv_for R10_iv_dom, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx ln_conn_seats) stats(N N_clust widstat)

* =====================================================================================
* 6. Annual regional panel: nights, employment, GDP per head, regional GACI
* =====================================================================================
use "cal_y.dta", clear
joinby year using "tour_y.dta"
merge m:1 stk using "ev_treat.dta", nogen keep(match)
merge m:1 stk nuts2 using "reg_expo.dta", nogen keep(match)
merge 1:1 stk nuts2 year using "reg_conn_y.dta", nogen keep(master match)
cap merge 1:1 nuts2 year using "emp_y.dta", nogen keep(master match)
cap merge 1:1 nuts2 year using "gdp_y.dta", nogen keep(master match)
gen iso2 = substr(nuts2, 1, 2)
iso2to3, from(iso2) gen(iso3)
gen treat_c  = (iso3 == iso3_tr)
mk_ctrl
keep if (treat_c == 1 | ctrl_eur == 1) & border_r == 0
egen fe_ry = group(stk nuts2)
egen fe_cy = group(stk iso3 year)
egen nuts2n = group(nuts2)
gen tpx = treat_c * post1 * expo_small
gen cpx = (1 - treat_c) * post1 * expo_small
foreach y in nights_for nights_dom emp_tot emp_I gdp_pc {
    cap gen ln_`y' = ln(`y')
}
save "panel_reg_y.dta", replace

local sampy "k <= 0"
foreach y in ln_nights_for ln_nights_dom ln_emp_I ln_emp_tot ln_gdp_pc {
    cap noisily reghdfe `y' tpx cpx if `sampy', absorb(fe_ry fe_cy) vce(cluster nuts2n)
    if _rc == 0 estimates store Y_`y'
}
cap noisily esttab Y_* using "R4_regional_annual.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx) stats(N N_clust, labels("Observations" "Regions")) title("Annual regional outcomes: exposure x post, years E-3..E")
cap noisily esttab Y_*, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx) stats(N N_clust)
scalar b_emp_I = .
cap estimates restore Y_ln_emp_I
if _rc == 0 scalar b_emp_I = _b[tpx]

* 2SLS on regional GACI
reghdfe ln_conn_gaci tpx cpx if `sampy', absorb(fe_ry fe_cy) vce(cluster nuts2n)
estimates store G_fs
ivreghdfe ln_nights_for cpx (ln_conn_gaci = tpx) if `sampy', absorb(fe_ry fe_cy) cluster(nuts2n)
estimates store G_iv_for
cap noisily ivreghdfe ln_emp_I cpx (ln_conn_gaci = tpx) if `sampy', absorb(fe_ry fe_cy) cluster(nuts2n)
cap estimates store G_iv_emp
cap noisily esttab G_fs G_iv_for G_iv_emp using "R5_regional_gaci_iv.rtf", replace b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx ln_conn_gaci) stats(N N_clust widstat, labels("Observations" "Regions" "KP F")) title("Regional GACI: first stage and 2SLS on nights and hospitality employment")
cap noisily esttab G_fs G_iv_for G_iv_emp, b(4) se(4) star(* 0.10 ** 0.05 *** 0.01) keep(tpx cpx ln_conn_gaci) stats(N N_clust widstat)

* =====================================================================================
* 7. Benefit / cost accounting, first tax year, by event and total
*    counterfactual = observed / exp(beta); abatement = observed x (exp(-beta) - 1)
* =====================================================================================
* 7a. treated-airport aggregates in the first post year
use "stack_month.dta", clear
keep if stk != 0 & treat == 1 & post1 == 1 & donut == 0
gen double co2_lvl   = exp(ln_co2) * `co2_t'
gen double seats_lvl = exp(ln_seats)
collapse (sum) co2_post = co2_lvl seats_post = seats_lvl (first) iso3, by(stk)
merge 1:1 stk using "ev_treat.dta", nogen
tempfile agg
save `agg'

* 7b. treated-region foreign nights and hospitality jobs in the first post year, with exposure
use "panel_reg_m.dta", clear
keep if treat_c == 1 & post1 == 1 & donut == 0
gen double nights_lost = nights_for * (exp(-b_tpx_for * expo_small) - 1)
gen double nights_lost_lo = nights_for * (exp(-(b_tpx_for - 1.96 * se_tpx_for) * expo_small) - 1)
collapse (sum) nights_for_post = nights_for nights_lost nights_lost_lo, by(stk)
tempfile tour
save `tour'
cap noisily {
    use "panel_reg_y.dta", clear
    keep if treat_c == 1 & post1 == 1
    gen double jobs_lost = emp_I * 1000 * (exp(-b_emp_I * expo_small) - 1)
    collapse (sum) jobs_lost emp_I_post = emp_I, by(stk)
    tempfile jobs
    save `jobs'
}

* 7c. assemble
use `agg', clear
merge 1:1 stk using `tour', nogen
cap merge 1:1 stk using `jobs', nogen
* abatement, weighted spec (aggregate-relevant) with 95% band, and unweighted spec for reference
gen double t_abated    = co2_post * (exp(-b_co2_w) - 1)
gen double t_abated_hi = co2_post * (exp(-(b_co2_w - 1.96 * se_co2_w)) - 1)
gen double t_abated_lo = co2_post * (exp(-(b_co2_w + 1.96 * se_co2_w)) - 1)
gen double t_abated_unw = co2_post * (exp(-b_co2_u) - 1)
* passengers, revenue, deadweight loss
gen double pax_post = seats_post * `lf'
gen double pax_lost = pax_post * (exp(-b_seats_w) - 1)
gen double revenue  = dose * pax_post
gen double dwl      = 0.5 * dose * pax_lost
* values
gen double carbon_val_100 = t_abated * `scc'
gen double carbon_val_200 = t_abated * 200
gen double tourism_loss   = nights_lost * `spend'
gen double tourism_loss_lo = nights_lost_lo * `spend'
gen double cost_total     = dwl + tourism_loss
gen double cost_per_t     = cost_total / t_abated
gen double cost_per_t_hi  = cost_total / t_abated_hi
gen double revenue_per_t  = revenue / t_abated
gen double net_100        = carbon_val_100 - cost_total
gen double net_200        = carbon_val_200 - cost_total
* total row
cap confirm variable jobs_lost
if _rc gen double jobs_lost = .
preserve
collapse (sum) co2_post seats_post pax_post t_abated t_abated_hi t_abated_lo t_abated_unw pax_lost revenue dwl carbon_val_100 carbon_val_200 nights_for_post nights_lost tourism_loss cost_total net_100 net_200 jobs_lost
gen iso3 = "ALL"
gen stk = 99
gen cost_per_t    = cost_total / t_abated
gen cost_per_t_hi = cost_total / t_abated_hi
gen revenue_per_t = revenue / t_abated
tempfile tot
save `tot'
restore
append using `tot'
order stk iso3 dose co2_post t_abated t_abated_lo t_abated_hi t_abated_unw seats_post pax_lost revenue dwl nights_for_post nights_lost tourism_loss cost_total cost_per_t cost_per_t_hi revenue_per_t carbon_val_100 carbon_val_200 net_100 net_200 jobs_lost
format co2_post t_abated* seats_post pax_lost revenue dwl nights_for_post nights_lost tourism_loss cost_total carbon_val_* net_* %15.0fc
format cost_per_t* revenue_per_t %9.1fc
save "benefits_by_event.dta", replace
export delimited using "benefits_by_event.csv", replace
di _n "==== Benefit / cost, first tax year (EUR; tonnes CO2) ===="
list stk iso3 dose t_abated t_abated_hi revenue dwl nights_lost tourism_loss jobs_lost cost_per_t revenue_per_t net_100, noobs abbrev(14)
di _n "Parameters: load factor `lf', carbon value `scc' EUR/t, spending per foreign night `spend' EUR, CO2 unit factor `co2_t'"
di    "Coefficients: seats (weighted) " b_seats_w ", CO2 (weighted) " b_co2_w " (se " se_co2_w "), CO2 (unweighted) " b_co2_u ", nights x exposure " b_tpx_for " (se " se_tpx_for ")"

log close
