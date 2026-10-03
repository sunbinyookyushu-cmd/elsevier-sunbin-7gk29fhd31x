# GACI_ASA — Do air service agreements raise or lower aviation CO2?

Second paper on the tax-paper data: treatment = bilateral/multilateral air service liberalisation between the origin
country and the destination country; outcomes = seats, flights, direct share, stage length, CO2, CO2 per seat-km at the
origin airport x destination country x year level, plus the network position (GACI, betweenness, eigenvector) of the
airports on both sides.

## Design (copied from the literature, see lit/asa_literature_review.md)
Dyadic staggered DiD in the gravity form of Micco & Serebrisky (2006) / Winston & Yan (2015):

    ln y_{o,d,t} = beta * Open_{c(o),d,t} + alpha_{o,d} + lambda_{o,t} + mu_{d,t} + e

  o = origin airport, d = destination country, t = year; Open = 1 once an open-skies / comprehensive agreement between
  the origin country and d is in force (provisional application counts). Origin-airport x year FE absorb national and
  airport shocks; destination x year FE absorb destination demand; pair FE absorb distance and history.
  Event studies around entry into force; not-yet-treated controls; EU horizontal agreements (forced by the 2002 ECJ
  judgments) as the plausibly exogenous-timing subsample; ALI (WTO QUASAR) as continuous intensity where available.
  Staggered-robust estimators (Callaway-Sant'Anna / Borusyak-Jaravel-Spiess) as robustness.

## Folders
- data_external/agreements/   us_open_skies_partners.csv, eu_regional_agreements.csv (+ READMEs) -> build_asa_panel.py -> asa_pair_year.csv
- lit/                        asa_literature_methods_table.csv, asa_literature_review.md
- stata/07_asa_did.do         estimation template (needs the OAG origin-airport x destination-country x year file)

## Data still needed
- data/raw/oag/seats_co2_by_origin_destcountry_year.csv (same request as the tax paper's band design)
