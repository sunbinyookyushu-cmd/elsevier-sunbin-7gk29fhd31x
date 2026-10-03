# Air service agreements, liberalisation and air transport outcomes: literature and methods review

Companion to `asa_literature_methods_table.csv` (44 entries: 25 VERIFIED, 15 PARTIAL, 4 EXISTS).
Verification was done from publisher / RePEc / repository search snippets only (full texts not fetched).
Cells marked "not read" in the table mean the value was not visible in any snippet; nothing was inferred.

Two corrections to the brief, both confirmed from RePEc records:

* Piermartini & Rousova (2013) appears in *AEJ: Economic Policy* 5(3), 287-319 under the title
  **"The Sky Is Not Flat: How Discriminatory Is the Access to International Air Services?"**. The title
  "Liberalization of Air Transport Services and Passenger Traffic" is the WTO Staff Working Paper
  ERSD-2008-06 version.
* Cristea, Hillberry & Mattoo (2015) "Open Skies over the Middle East" is in **The World Economy** 38(11),
  1650-1681 (earlier: World Bank PRWP 6937, 2014), not World Trade Review.

---

## (a) Designs used and typical effect sizes

### Design families

| Family | Representative papers | Unit | Treatment | Comments |
|---|---|---|---|---|
| Dyadic gravity, cross-section with treatment intensity | Piermartini & Rousova 2013 (A03); Cristea, Hillberry & Mattoo 2015 (A04); Zhang & Findlay 2014 (A29) | country pair (or city pair) | WTO/QUASAR Air Liberalization Index (ALI, 0-50) or own restrictiveness index; individual ASA provisions | Identifies from cross-pair variation in liberalisation level; reverse causality (liberal ASAs where traffic is large) is the main threat |
| Dyadic gravity panel / DiD with agreement-in-force dummy | Micco & Serebrisky 2006 (A01); Oum, Wang & Yan 2019 (A33); Clougherty, Dresner & Oum 2001 (A11); Yamaguchi 2008 (A34); Surovitskikh & Lubbe 2015 (A31, ALI in panel); Cristea, Abate & Benitez 2025 (A32, partial vs full liberalisation) | country pair x year | OSA / liberalised bilateral in force from its application date | The closest analogues to a staggered dyadic DiD; FE structures mostly "not read" from snippets, but reduced-form gravity DiD is stated explicitly in A33 |
| Route-level DiD around a single agreement | Bernardo & Fageda 2017 (A21, EU-Morocco); Abate 2016 (A30, intra-Africa); Bilotkach et al. 2021 (A22, ASEAN; FE + PSM-DiD + distance matching) | airport pair (route) x period, or city x year | Route/city falls under the new agreement after entry into force | Separate equations for intensive margin (seats on existing routes) and extensive margin (new route opened) in A21 - a useful template |
| Natural experiment on routing | Soderlund 2023 (A05) | country pair x year | Reduction in flight distance from Soviet airspace opening | Exogenous geopolitical shock to routing; DiD with continuous intensity |
| Structural / simulation | Winston & Yan 2015 (A02); Gillen, Harris & Oum 2002 (A09); Adler et al. 2014 (A14); Cristea, Hummels & Roberson 2017 (A35); Mayor & Tol 2008 (B01) | route / market | counterfactual regime | Deliver welfare numbers; not reduced-form causal estimates |
| Before-after descriptive | Morandi et al. 2014 (A24); Malighetti et al. 2012 (A25); Burghouwt & de Wit 2015 (A17); Dobruszkes 2006/2009/2013 (A18-A20); InterVISTAS 2006 (A13) | routes, airports, markets | pre vs post | No control group; useful for mechanisms (hub concentration, LCC route creation) |
| Ticket-level panel with emissions | Fontagne, Mitaritonna, Orefice & Santoni 2026 (B02) | country pair x year (ticket data aggregated) | ASA in force / liberalisation level | Only ex-post ASA -> CO2 estimate found |

### Typical effect sizes (as visible in abstracts/snippets)

* **Traffic.** ALI from 25th to 75th percentile: about +30% bilateral passengers (A03). Multilateralising
  OSAs: about +5% world traffic; EEA-type agreements: about +10%; multiple designation alone: about +0.5% (A03).
  InterVISTAS (A13): post-liberalisation growth typically 12-35% and a simulated +63% for 320 restricted pairs
  (consultancy figures, no counterfactual). Cristea et al. (A04): higher traffic driven mainly by more city pairs
  served (extensive margin) rather than more passengers per route.
* **Seats / frequency.** EU-Morocco OSA: +20-40% seats on pre-existing routes plus more new routes (A21).
  Intra-African liberalised routes: up to +40% departure frequency (A30). ASEAN OSA: more LCC/FSC services to
  and from the region but fewer FSC flights within it; net negative effect on number of airlines (A22).
* **Costs / fares.** US OSAs cut air freight costs about 9% and raised the air share of imports about 7%, with no
  effect for low-income partners (A01). Winston & Yan: at least USD 4 bn/yr traveller gains from US OSAs (A02).
  Abate (A30) finds no fare reduction in Africa; Cristea, Abate & Benitez (A32) find lower fares for both partial
  and full liberalisation (2011-19).
* **Network / hubs.** After EU-US Open Skies the number of direct transatlantic connections and served airport
  pairs fell while indirect (connecting) competition rose (A24); Open-Skies-related capacity expansion on
  US-Europe routes was entirely by immunised carriers between their hubs (A27). Dresner & Oum (A10) document
  diversion of Canada-bound traffic through US hubs under liberal US bilaterals.
* **Trade via routing.** Shorter flight routes from Soviet airspace opening raised trade proportionally to the
  distance reduction; business travel cost accounts for about 85% of distance-related trade friction (A05).
* **Emissions.** After an ASA: average itinerary distance -1.4 to -1.6%, legs -3 to -4%, CO2 per passenger about
  -3.9%; total emissions rise because induced demand outweighs the per-passenger saving; full liberalisation of all
  pairs would cut emissions per passenger 2.3% (B02).

---

## (b) How timing endogeneity of agreements was handled

* **Country-pair fixed effects (Baier-Bergstrand logic).** The trade-agreement literature (D01) shows that pair FE,
  which absorb time-invariant unobservables that drive both selection into an agreement and the outcome, change
  estimated effects by a factor of about five, and that lagged agreement terms are needed for phase-in. Among the
  ASA papers, the panel studies (A01, A11, A31, A33, A34, A32) use within-pair variation in the agreement dummy, but
  the exact FE sets were not visible in snippets; none of the snippets mentions leads for anticipation or
  pre-trend tests, so these should be treated as "not read" rather than absent.
* **Cross-sectional ALI studies (A03, A04, A29)** rely on exogeneity of the liberalisation level conditional on gravity
  controls and country effects. A03 motivates causality by showing provision-specific effects and non-linearity (a
  minimum liberalisation threshold), but cannot rule out that high-traffic pairs negotiate liberal ASAs.
* **Matching.** Bilotkach et al. (A22) complement FE with propensity-score and distance matching of ASEAN cities to
  non-ASEAN controls.
* **Natural experiments.** Soderlund (A05) uses an airspace-opening shock that was not chosen by the trading
  partners; Morocco (A21) and ASEAN (A22) exploit single, externally negotiated multilateral events with
  route-level controls.
* **Structural models (A02, A09, A14, A35)** sidestep timing by simulating counterfactual regimes rather than
  estimating treatment effects on timing.
* **Endogenous binary treatment estimators** (Egger et al. 2011, D02) are available in the trade literature but no ASA
  paper found uses them.
* **Pitfield (A26)** is an explicit methodological discussion of the counterfactual problem for the EU-US OSA.
* **Staggered-adoption estimators (D04-D06)** were not mentioned in any ASA paper snippet found; this is a clear
  methodological opening.

---

## (c) Data sources for agreement dates used by these papers

| Source | Content | Used by | Access |
|---|---|---|---|
| **ICAO World's Air Services Agreements (WASA) database** (Doc 9511) | >2,500 summaries and >1,900 full texts of registered bilaterals; analytical tool coding up to ~90 provisions (scope, traffic rights, capacity, tariffs); routes exchanged | Basis of QUASAR; A03, A04 (via QUASAR/WASA) | https://www.icao.int/sustainability/Pages/WASA.aspx ; https://data.icao.int/WASA/ |
| **WTO QUASAR (Quantitative Air Services Agreements Review)** and the **Air Liberalization Index** (0-50; 7 features: grant of rights, capacity, designation, withholding/ownership, pricing, statistics, cooperative arrangements) | Built from WASA plus IATA information; categorises ~2,300-2,500 bilaterals circa 2005 | A03, A04, A31, A29 (own index inspired by ALI) | WTO Secretariat documents; see WTO ERSD-2008-06 (A03 WP) and ICAO ATConf/6 IP.017 |
| **US DOT "Open Skies Agreements Currently Being Applied"** | List of US open-skies partners with application dates (incl. MALIAT signatories) | A01, A02, A27, A34, A35 (US OSA dates) | https://www.transportation.gov/policy/aviation-policy/open-skies-agreements-being-applied |
| **US State Department (EB) Open Skies Partners list** (e.g., 19 Aug 2013 version) | Partner, in-force/provisional application date, all-cargo/7th-freedom flag | Same US studies | Copy archived by ICAO: https://www.icao.int/sites/default/files/sp-files/sustainability/Documents/Compendium_FairCompetition/List%20partners%20OSA%20US.pdf |
| **EU documents** | EU-US Air Transport Agreement (signed 2007, applied 30 Mar 2008); EU-Canada Agreement (signed 17-18 Dec 2009, provisionally applied); EU-Morocco (Dec 2006); horizontal agreements following the 5 Nov 2002 ECJ "open skies" judgments (Community clause replacing nationality clauses) | A12, A21, A24, A20 | https://transport.ec.europa.eu/transport-modes/air/international-aviation/external-aviation-policy/horizontal-agreements_en ; European Parliament Legislative Observatory summaries |
| **Ticket / schedule data** | Winston & Yan, Whalen, Brueckner et al.: US DOT DB1B/O&D; Fontagne et al.: airline ticket data 2012-2019; Bernardo & Fageda, Burghouwt & de Wit, Cheung et al.: schedule seat data (OAG-type) | - | commercial |

Gaps found in the search: no empirical evaluation of the **EU-Canada** agreement's traffic effects, and no
econometric study of the **EU horizontal agreements** (post-2002 ECJ judgments) as a treatment, were located.
Both are candidate treatment events for a staggered design because their dates are documented in EU records.

---

## (d) The gap on CO2 and network centrality

**Does an ASA -> CO2 study exist?** Yes, two, of different kinds:

1. **Mayor & Tol (2008, JATM 14(1), 1-7, B01)** - an *ex-ante simulation* of the EU-US Open Skies agreement's
   effect on international travel and CO2 using a tourism-flow model. It is not an ex-post causal estimate.
2. **Fontagne, Mitaritonna, Orefice & Santoni (2026, CEPII WP 2026-04, B02)** - the *first ex-post* estimate.
   Using ticket data 2012-2019 matched to ASAs in force, they find that ASAs shorten itineraries (-1.4 to -1.6%
   distance) and reduce stopovers (-3 to -4% legs), cutting CO2 per passenger about 3.9%, while total emissions
   rise through induced demand. It is a working paper (no DOI yet); exact FE/DiD structure was not visible.

What is **not** covered by either:

* No study uses **airport-level** outcomes (seats or CO2 by airport x destination-country x year); both CO2 papers
  work at country-pair level.
* No study links ASAs to an **airport network-centrality index**. The GACI (Cheung, Wong & Zhang 2020, C01) is a
  descriptive metric paper without a policy treatment. The hub evidence that exists is route-level and
  descriptive (Morandi et al. 2014; Whalen 2007; Dresner & Oum 1998), pointing to *hub concentration* after some
  agreements and *route creation / de-hubbing* after others (Morocco, EU LCC expansion) - i.e. the sign of the
  centrality effect is an open empirical question.
* No study decomposes the CO2 effect into **detour (routing)**, **hub bypass (legs)**, **aircraft/stage-length mix**
  and **induced demand** at the airport level; B02 does this only at country-pair level and only for the first two.
* No study applies **heterogeneity-robust staggered estimators** (D04-D06) to ASA adoption.

---

## (e) Design checklist for a paper with airport x destination-country x year seats/CO2 and GACI as outcomes

1. **Treatment definition.** Date of *application* (provisional or in force), not signature, from WASA/QUASAR,
   US DOT list, EU documents. Code (i) a binary liberal-ASA dummy and (ii) an ALI-type intensity; record
   amendments so a pair can move up the ladder (treat as separate events or use the continuous index).
   Multilateral blocs (EU internal market, EU-US, ASEAN SAM, MALIAT, Yamoussoukro/SAATM) should be coded at the
   airport-country level by membership date.
2. **Panel and FE for dyadic outcomes (seats, CO2 by airport i -> destination country d, year t).**
   Baseline: airport-x-destination FE (absorbs selection into agreements, A01/D01 logic) + airport-x-year FE +
   destination-country-x-year FE (gravity multilateral-resistance analogues). Note that the ASA is signed at the
   *country* level: the airport-year FE absorbs the home country's common year shocks, so identification comes
   from the destination-specific timing within airport. Cluster at the country-pair level (the level at which
   treatment is assigned); report two-way clustering (home country, destination country) as robustness.
3. **Estimator.** Use PPML (D03) for seats/CO2 with zeros and heteroskedasticity; for heterogeneity-robust
   dynamics use Callaway-Sant'Anna (D04) with not-yet-treated controls, Sun-Abraham (D05) interaction-weighted
   event study, and Borusyak-Jaravel-Spiess (D06) imputation, which handles high-dimensional FE naturally.
   Report the TWFE estimate alongside and a Goodman-Bacon-type weight diagnostic (not in table; add if used).
4. **Event-study window and anticipation.** Include at least 3-5 leads (negotiation and signature typically
   precede application by 1-3 years, cf. Baier-Bergstrand lags for phase-in) and 5+ lags; bin endpoints.
   Test pre-trends with the D05/D06 estimators, not with contaminated TWFE leads.
5. **Extensive vs intensive margin.** Following Cristea et al. (A04) and Bernardo & Fageda (A21): estimate (i)
   probability that airport i serves destination d (route existence), (ii) seats conditional on service, and
   (iii) CO2 per seat / per passenger. The CO2 total-vs-per-passenger divergence in B02 means the paper should
   report both.
6. **Mechanism decomposition for CO2.** Decompose airport-destination CO2 change into: stage length (detour
   reduction, A05/B02), number of legs / hub bypass (B02, A24), aircraft size and load factor, and frequency
   (A30, A14). Use great-circle vs actual routing distance where available to isolate the detour channel.
7. **Network centrality outcome (GACI).** GACI is airport x year, so the treatment must be aggregated: e.g.
   share of the airport's destination countries (or seats) covered by a liberal ASA, or number of new liberal
   ASAs of the home country in year t. Use airport FE + year FE (+ region-year), staggered/continuous-intensity
   estimators, and leave-one-out construction of GACI so the treated pair's own seats do not mechanically move
   the index. Because competitors' agreements shift centrality (A27 hub-to-hub concentration), model spillovers
   explicitly (e.g. exposure of rival hubs in the same country) rather than assuming SUTVA.
8. **Controls / confounders.** Alliance antitrust immunity and JV approvals (A27, A28), LCC entry (A17-A19),
   airport slot constraints (A14), HSR competition (A14), fuel prices, and bilateral trade/visa changes; all vary
   by pair-year and are correlated with ASA timing.
9. **Endogeneity of timing.** Beyond pair FE: (i) report heterogeneity by partner income (A01 found no effect for
   low-income partners), (ii) placebo with signature-but-not-applied agreements, (iii) matching of treated to
   untreated destinations on pre-period traffic growth (A22), (iv) if feasible, use externally driven events
   (2002 ECJ judgments forcing EU horizontal agreements; ASEAN SAM deadline; Soviet-airspace-type shocks) as
   quasi-exogenous timing.
10. **Data provenance statement.** List agreement sources (WASA/QUASAR version and date, US DOT list date, EU
    documents), schedule/ticket vendor, emissions method (fuel-burn model by aircraft type and stage length), and
    GACI construction (C01 definition: degree, closeness, eigenvector + volumetric indicators).

---

## (f) Sources

Core ASA / liberalisation studies

* Micco & Serebrisky (2006) JIE 70(1): https://repositorio.uchile.cl/handle/2250/128587
* Winston & Yan (2015) AEJ:EP 7(2): https://ideas.repec.org/a/aea/aejpol/v7y2015i2p370-414.html
* Piermartini & Rousova (2013) AEJ:EP 5(3): https://ideas.repec.org/a/aea/aejpol/v5y2013i3p287-319.html ; WP ERSD-2008-06: https://ideas.repec.org/r/zbw/wtowps/ersd200806.html
* Cristea, Hillberry & Mattoo (2015) World Economy 38(11): https://ideas.repec.org/a/bla/worlde/v38y2015i11p1650-1681.html ; WB PRWP 6937: https://documents.worldbank.org/en/publication/documents-reports/documentdetail/973041468299065196
* Soderlund (2023) JIE 145: https://ideas.repec.org/a/eee/inecon/v145y2023ics0022199623000983.html ; https://www.sciencedirect.com/science/article/pii/S0022199623000983
* Fu, Oum & Zhang (2010) Transportation Journal 49(4): https://ideas.repec.org/a/wly/transj/v49y2010i4p24-41.html ; ITF DP version: https://www.itf-oecd.org/sites/default/files/docs/09fp04_0.pdf
* Fu & Oum (2014) Advances in Airline Economics 4: https://ideas.repec.org/h/eme/aiaezz/s2212-160920140000004000.html
* Gillen, Harris & Oum (2002) TR-E 38(3-4): https://ideas.repec.org/a/eee/transe/v38y2002i3-4p155-174.html
* Dresner & Oum (1998) JTEP 32(3): https://trid.trb.org/View/504354
* Clougherty, Dresner & Oum (2001) Transport Policy 8(3): https://ideas.repec.org/a/eee/trapol/v8y2001i3p219-230.html
* Button (2009) JATM 15(2): https://ideas.repec.org/a/eee/jaitra/v15y2009i2p59-71.html
* InterVISTAS-ga2 (2006): https://www.iata.org/en/iata-repository/publications/economic-reports/the-economic-impacts-of-air-service-liberalization---intervistas ; https://www.icao.int/Meetings/AMC/MA/2006/dubai2006/economicliberalization_intervista.pdf
* Adler, Fu, Oum & Yu (2014) TR-A 62: https://cris.huji.ac.il/en/publications/air-transport-liberalization-and-airport-slot-allocation-the-case/
* Fu, Oum, Chen & Lei (2015) Transport Policy 43: https://ideas.repec.org/a/eee/trapol/v43y2015icp61-75.html
* Zhang & Zhang (2002) JATM 8(5): https://ideas.repec.org/a/eee/jaitra/v8y2002i5p275-287.html
* Burghouwt & de Wit (2015) Transport Policy 43: https://trid.trb.org/view/1368100
* Dobruszkes (2006) JTG 14: https://ideas.repec.org/p/ulb/ulbeco/2013-135954.html ; Dobruszkes (2009) JTG 17(6): https://ideas.repec.org/a/eee/jotrge/v17y2009i6p423-432.html ; Dobruszkes & Mondou (2013) JATM 29: https://ideas.repec.org/a/eee/jaitra/v29y2013icp23-34.html
* Bernardo & Fageda (2017) TR-E 98: https://ideas.repec.org/a/eee/transe/v98y2017icp24-41.html ; https://diposit.ub.edu/dspace/handle/2445/119872
* Bilotkach et al. (2021) Transport Policy 110: https://ideas.repec.org/a/eee/trapol/v110y2021icp368-378.html
* Sazali (2025) PhD Leeds: https://etheses.whiterose.ac.uk/id/eprint/38665/
* Morandi, Malighetti, Paleari & Redondi (2014) Transportation Journal 53(3): https://ideas.repec.org/a/wly/transj/v53y2014i3p305-329.html
* Malighetti et al. (2012) Economia e Politica Industriale: https://ideas.repec.org/a/fan/polipo/vhtml10.3280-poli2012-004004.html
* Pitfield (2009) JATM 15(6): https://dspace.lboro.ac.uk/dspace-jspui/handle/2134/10985
* Whalen (2007) RIO 30(1): https://ideas.repec.org/a/kap/revind/v30y2007i1p39-61.html
* Brueckner, Lee & Singer (2011) JCLE 7(3): https://ideas.repec.org/a/oup/jcomle/v7y2011i3p573-602..html
* Zhang & Findlay (2014) JATM 34: https://ideas.repec.org/a/eee/jaitra/v34y2014icp42-48.html
* Abate (2016) TR-A 92: https://ideas.repec.org/a/eee/transa/v92y2016icp326-337.html
* Surovitskikh & Lubbe (2015) JATM 42: https://ideas.repec.org/a/eee/jaitra/v42y2015icp159-166.html
* Cristea, Abate & Benitez (2025) Economics of Transportation 42: https://ideas.repec.org/a/eee/ecotra/v42y2025ics2212012225000206.html
* Oum, Wang & Yan (2019) Transport Policy 74: https://ideas.repec.org/a/eee/trapol/v74y2019icp1-14.html
* Yamaguchi (2008) TR-E 44(4): https://ideas.repec.org/a/eee/transe/v44y2008i4p653-663.html
* Cristea, Hummels & Roberson (2017) WP: https://pages.uoregon.edu/cristea/Research_files/osa.pdf

ASA -> CO2

* Mayor & Tol (2008) JATM 14(1): https://research.vu.nl/en/publications/the-impact-of-the-eu-us-open-skies-agreement-on-international-tra-2/ ; https://www.esri.ie/publications/the-impact-of-the-eu-us-open-skies-agreement-on-international-travel-and-carbon-0
* Fontagne, Mitaritonna, Orefice & Santoni (2026) CEPII WP 2026-04: https://www.cepii.fr/CEPII/en/publications/wp/abstract.asp?NoDoc=15039 ; PDF: https://www.cepii.fr/PDF_PUB/wp/2026/wp2026-04.pdf ; RePEc: https://ideas.repec.org/p/cii/cepidt/2026-04.html ; VoxEU: https://cepr.org/voxeu/columns/air-service-liberalisation-and-carbon-dioxide-emissions

Connectivity metric

* Cheung, Wong & Zhang (2020) TR-E 133: https://ideas.repec.org/a/eee/transe/v133y2020ics1366554519301243.html

Methods

* Baier & Bergstrand (2007) JIE 71(1): https://ideas.repec.org/p/fip/fedawp/2005-03.html
* Egger, Larch, Staub & Winkelmann (2011) AEJ:EP 3(3): https://www.aeaweb.org/articles/pdf/doi/10.1257/pol.3.3.113
* Santos Silva & Tenreyro (2006) REStat 88(4): https://eprints.lse.ac.uk/2510/
* Callaway & Sant'Anna (2021) J. Econometrics 225(2): https://cran.r-project.org/web/packages/did/citation.html
* Sun & Abraham (2021) J. Econometrics 225(2): https://arxiv.org/abs/1804.05785
* Borusyak, Jaravel & Spiess (2024) REStud 91(6): https://ideas.repec.org/p/ehl/lserod/123781.html

Agreement-date data sources

* ICAO WASA: https://www.icao.int/sustainability/Pages/WASA.aspx ; https://data.icao.int/WASA/AboutWASA/WASAExplanatoryNotes
* WTO QUASAR / ALI: WTO ERSD-2008-06 (above); ICAO ATConf/6 IP.017: https://www.icao.int:443/Meetings/atconf6/Documents/WorkingPapers/ATConf.6.IP.017.2.en.pdf
* US DOT open skies list: https://www.transportation.gov/policy/aviation-policy/open-skies-agreements-being-applied
* US State Dept partner list (2013 copy): https://www.icao.int/sites/default/files/sp-files/sustainability/Documents/Compendium_FairCompetition/List%20partners%20OSA%20US.pdf
* EU horizontal agreements: https://transport.ec.europa.eu/transport-modes/air/international-aviation/external-aviation-policy/horizontal-agreements_en
* EU-Canada agreement summary: https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1545693
