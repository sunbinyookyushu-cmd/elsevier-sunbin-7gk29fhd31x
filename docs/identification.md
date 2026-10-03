# Identification — the simple version

## Headline model (airport level; runs today on GACI data)

    y_at = β · Tax_c(a),t + α_a + λ_r(a),t + ε_at

* y: ln seats, ln GACI (plus Degree, Betweenness as mechanisms)
* Tax: 1 if the airport's country levies a per-passenger ticket tax in year t (binary; dose = EUR rate as robustness)
* α_a airport FE; λ_rt OAG-region × year FE (common European shocks: fuel, GFC, COVID)
* SE clustered by country. Event study with leads/lags of the first tax year (parallel pre-trends test).
* Leakage: Spill_at = 1 for untaxed airports within 300 km of a taxing country; estimated jointly so
  the control group is not contaminated and the net effect = β_tax × taxed seats + β_spill × spill seats.

Treatment events (1996–2024 window): NL 2008→2009 (abolished) → 2021; DE 2011; AT 2011; NO 2016; SE 2018;
PT 2021; BE 2022; IE 2009→2014 (abolished). UK (since 1994) and FR (TAC) are always-treated → absorbed by
airport FE; UK rate changes enter only the dose specification.

## Route-level model (needs OAG segments)

    ln CO2_ijt = β · Tax_ijt + α_ij + λ_it + μ_jt + ε_ijt

Within the same origin airport and year, routes in different distance bands face different per-passenger
taxes. Origin×year FE kills airport-level demand shocks; destination×year FE kills destination shocks.
Same equation for ln departures, ln seats, ln ASK, ln CO2/seat → scale vs aircraft-technology split.
Checks: (i) UK 2015 band merger (long-haul tax cut), (ii) 2,000-mile threshold RD for UK routes,
(iii) NL 2008 introduction and 2009 abolition (symmetry).

## Why this is enough

Two equations, two fixed-effects structures, one leakage term. No IV, no structural model. The CO2
outcome is built from schedules (not fuel sales), so tankering and inventory accounting do not enter.
