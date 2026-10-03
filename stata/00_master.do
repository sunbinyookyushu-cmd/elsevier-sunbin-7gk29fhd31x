*==============================================================================*
* Aviation taxes, connectivity (GACI) and CO2 — master do-file
* Run from the repo root:  do stata/00_master.do
* Requires: reghdfe, ftools, estout (ssc install reghdfe ftools estout)
*==============================================================================*
clear all
set more off
version 16
global ROOT  "`c(pwd)'"
global RAW   "$ROOT/data/raw"
global PROC  "$ROOT/data/processed"
global OUT   "$ROOT/output"
cap mkdir "$OUT"

do "$ROOT/stata/01_build_airport_panel.do"     // GACI airport-year panel + country, logs
do "$ROOT/stata/02_build_tax_panel.do"         // country-year tax treatment from the tax event table
do "$ROOT/stata/03_airport_did.do"             // SIMPLE model: airport DiD + event study + border leakage
* do "$ROOT/stata/04_route_co2_template.do"    // run once OAG segment data are in place
