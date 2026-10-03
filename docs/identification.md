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

## Treatment geography (Li, Liu, Purevjav & Yang 2019, JEEM analogue)

| Li et al. | here |
|---|---|
| monitors ≤ 2 km of a new station | airports in a taxing country |
| 2–20 km buffer, dropped | untaxed airports 150–300 km from a taxing country, dropped |
| monitors > 20 km | untaxed airports > 300 km from any taxing country |
| staggered-rollout control | only ever-taxing countries (not-yet-treated) |
| number of new stations (dose) | per-passenger rate in EUR; implicit €/tCO2 |
| days since opening, quadratic | years since introduction, quadratic |
| continuous density + historical-plan IV | **GACI as density** → CO2, instrumented by the heritage-tourism shift-share (`stata/05_gaci_density_iv.do`) |
| Table 9: density change × IV coefficient | tax-induced ΔGACI (axis 2) × β_IV (axis 1) = implied CO2; cross-check with the direct DiD on ln CO2 |
| health benefit vs construction cost | CO2 avoided × SCC vs connectivity loss × trade elasticity (2.1) |

## Axis 1: GACI as the continuous network density

    ln CO2_it = β · ln GACI_it + γ · ln pop_ct + α_i + δ_t + ε_it ,   IV: tourism_int_ct = D̄_t × ln(1 + H_c)

GACI plays the role of Li et al.'s subway density: a continuous, whole-network position measure at each
location. The instrument is the trade paper's heritage-tourism shift-share; exclusion is easier here than
for trade because heritage-driven tourism moves aviation CO2 only by moving flights. Country×year or
region×year FE and the decomposition by GACI component (degree, betweenness, eigenvector) identify which
network dimension carries the carbon.

## Outcome: bottom-up airport-year CO2

Departure-based CO2 by phase (taxi-out, take-off, climb-out, cruise), domestic/international, 1996–2023
(2024 partial), built from the same schedules as GACI. International departures sum to 244–590 Mt per year
versus 308–633 Mt in EDGAR international aviation, i.e. 80–95% (EDGAR includes freighters and
non-scheduled traffic). Decomposition: ln CO2 = ln seats + ln stage length + ln CO2/seat-km.

## Why this is enough

Two equations, two fixed-effects structures, one leakage term. No IV, no structural model. The CO2
outcome is built from schedules (not fuel sales), so tankering and inventory accounting do not enter.
