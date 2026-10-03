# Aviation ticket taxes, the EU ETS and hub relocation: literature and methods review

Prepared 2026-10-02 for the GACI aviation-tax / carbon-pricing paper (target: Energy Economics). Question: did national ticket taxes and the EU ETS move airport hub functions (betweenness, eigenvector centrality) and seats away from taxed airports, to neighbouring countries' airports or to non-EU hubs (Istanbul, Gulf)?

Companion files:
- `literature_methods_table.csv`: one row per study (all fields below; UTF-8 with BOM).
- `lit_notes/strand1A_NL_DE_AT_crossborder.md`, `strand1B_UK_IE_SE_NO_FR_panel.md`, `strand2_EU_ETS.md`, `strand3_hubs_centrality.md`, `strand4_methods.md`: long-form extraction notes, sources and access paths.

## 0. How this was compiled

- Coverage: 35 core empirical studies (section 3), 18 secondary or peripheral studies (section 4), 24 methods papers plus 2 applied exemplars from energy economics (section 5).
- Every academic citation was checked with the refcheck MCP (Crossref, Semantic Scholar, arXiv) and Crossref metadata; reports were checked on the publisher's page (KiM, Bundestag, IHS, SEO, CE Delft). Online-first vs issue years are noted where they differ.
- Status codes: VERIFIED = methods and results read in full text; PARTIAL = abstract (sometimes plus a publisher preview) only. Fields not read are marked "not read". No number, date or design was filled in from memory.
- Search limits: the session's WebSearch quota was exhausted, so candidates came from refcheck, OpenAlex, Crossref, Semantic Scholar, repositories (UB, Cranfield CERES, DLR elib, UCL, Strathprints, LSE, MIT, PolyU, PMC, DiVA) and the browser for SSRN, ScienceDirect and Springer pages. SSRN PDFs, Wiley full texts, HAL, SLU and Doria were behind bot checks.
- Quotation policy: headline numbers are exact and cite their table or section; the authors' wording is paraphrased.
- Spot checks: the compiler re-read key numbers in the downloaded texts for Fageda and Teixido (2022), Fageda and Oesingmann (2025, TR-A), Bernardo et al. (2024), Helmers and van der Werf (2025), KiM (2011), BT-Drs. 17/10225, Gurr and Moser (2017), IHS (2012), SEO (2009), Mayor and Tol (2007), Dray and Doyme (2019), Piltz et al. (2018), Suau-Sanchez et al. (2016), Wozny (2024), Cengiz et al. (2019), Abadie et al. (2010) and Dechezlepretre et al. (2023). All matched.

## 1. Synthesis

1. **Standard designs.** Ticket-tax evidence moved from ministry-commissioned accounting and simulation studies (KiM 2011; Infras 2012; IHS 2012; SEO 2009; CE Delft 2019) to three econometric templates: airport-level synthetic control for one country (Borbely 2019), airport-level event studies or dynamic panels (Helmers and van der Werf 2025; Falk and Hagsten 2019), and route- or itinerary-level DiD across countries (Bernardo, Fageda and Teixido 2024 with Callaway-Sant'Anna and entropy balancing; Wozny 2024 with a continuous tax rate and Danish and Finnish controls; Collet, Quirion and Taconet 2023, abstract only). EU ETS evidence uses route DiD (Fageda and Teixido 2022), a continuous EUA price x "connects at an EEA hub" design (Fageda and Oesingmann 2025, TR-A), route synthetic control (Kang et al. 2022), PSM-DID (Zhang et al. 2026, Energy Economics), a proxy SVAR with Kaenzig surprises (Albert et al. 2025) and a country-panel DiD (Zhang and Wang 2024). Only Bernardo et al. (2024) use a heterogeneity-robust staggered estimator; none of the tax or ETS papers read uses Sun-Abraham, Borusyak-Jaravel-Spiess, de Chaisemartin-D'Haultfoeuille, weighted stacking or synthetic DiD.

2. **Typical effect sizes.** Ticket taxes, first year: German airports -7% to -11% (Helmers and van der Werf, five estimators), Germany plus Austria -9% then -5% (Falk and Hagsten, abstract), about -2% or 4 million passengers a year in airport-by-airport synthetic controls (Borbely), and up to 2.0 million passengers or about 1.1% in the ministry evaluation (Infras); Schiphol OD -6.9% (KiM 2011); Sweden -9.1% with pass-through of USD 0.95 per USD 1 (Wozny). Per euro: about -1% of flights (Bernardo et al., TWFE) or of traffic (Collet et al., abstract); -0.2% of boarding passengers at the 10% level (Gurr and Moser). Effects concentrate in low-cost carriers (LCC flights -12.2%, network carriers -1.1% n.s.; Bernardo et al.) and fade: 99% of specifications significant for 2011, 38% for 2012, 0% for 2013 (Helmers and van der Werf). EU ETS: CO2 -4.7% on intra-EEA routes, -9.8% with non-EEA-only controls (Fageda and Teixido); connecting passengers via EEA hubs -0.041 per unit of square-root EUA price, visible only from 2018 when prices rose (Fageda and Oesingmann).

3. **Displacement to neighbouring airports is real but modest, and was handled in three ways.** (i) Buffer exclusion of nearby foreign airports from controls: about 150 km or two hours' drive (Bernardo et al.; Falk and Hagsten per citing papers), 350 km (Helmers and van der Werf). (ii) Neighbours as a second treated group: Borbely's 13 border airports (mostly gained; Eindhoven, Amsterdam and Basel significant at 5% and Luxembourg at 10% in placebo tests), Infras's 200 km clusters plus a "hubs by air" channel, KiM's named airports. (iii) Control-group sensitivity: switching to non-EEA-only controls doubles the ETS estimate (Fageda and Teixido), direct evidence that contaminated controls bias toward zero; Wozny drops treated-to-control itineraries and swaps in more distant controls. Magnitudes: about 1.2 million Dutch defections in one year (KiM Table 5.2) and 0.75 million German passengers abroad (Infras Table 35). Nobody uses distance rings with separate parallel-trends checks (Butts 2023) or network-based exposure.

4. **Hub function at taxed airports looks insulated; relocation to non-EU hubs is documented only for the ETS and only on the demand side.** All national taxes studied exempt transfer passengers, and taxed hubs held up or gained (Borbely: Frankfurt n.s., Munich, Duesseldorf, Tegel gained; Falk and Hagsten: hubs unaffected; KiM: Schiphol transfers kept rising). Air-side rerouting of German origin passengers to Heathrow, CDG and Amsterdam was about 400,000 in 2011 (Infras). For the ETS, Fageda and Oesingmann (2025) find that intercontinental connecting passengers via EEA hubs fall with the EUA price relative to those via non-ETS hubs (Gulf, Istanbul, Asia, North America): -0.038 where both hub types compete vs -0.060 where they do not. The only number for hub switching under carbon pricing otherwise comes from simulation: at USD 300/t, transfers via UK hubs -0.64 million vs +0.31 million via non-UK hubs (Dray and Doyme 2019); Wei and Kallbekken (2024) note that Commission assessments mention hub switching without quantifying it.

5. **Network centrality has never been the outcome of a tax or ETS evaluation.** Causal designs with centrality outcomes exist only for airline mergers: Khordagui (2025, SSRN) applies synthetic DiD per merger to degree, closeness, eigenvector and betweenness (weighted and unweighted); betweenness moves most and is volatile (Northwest-Delta long run -27.6%). Ciliberto, Cook and Williams (2019) find near-zero effects with within-airport windows and unweighted topology. Metric blueprints exist: Allroggen et al. (2015) GHCI from time-feasible one-stop routings; Suau-Sanchez et al. (2016) flow betweenness from MIDT; Logothetis and Miyoshi (2018) and O'Connell and Escofet Bueno (2018) connection-quality indices with MCT and detour limits.

6. **The Gulf and Istanbul trend is a first-order confounder.** EEA hubs' share of Eastern US to South Asia connections fell from 52.9% to 22.4% and the Middle East's rose from 32.4% to 62.3% between 2012 and 2016 (Piltz et al.); Dubai's share of one-stop connectivity from South and South-East Asia rose from 1.2% to 7.6% between 2000 and 2012 (Allroggen et al.); Turkish Airlines' effective connections rose from 19,230 (2007) to 103,368 (2014) (Logothetis and Miyoshi). An EEA x EUA-price design that does not absorb this secular trend will attribute it to the ETS.

7. **Inference is the weakest part of the literature.** Route-level papers cluster by route (Fageda and Teixido; Bernardo et al.; Fageda and Oesingmann) or city pair (Wozny, with country-pair robustness), although treatment varies by country or bloc and the EUA price is a single time series; numbers of clusters are rarely reported. Country clustering appears in Helmers and van der Werf (27 countries) and Gurr and Moser (61 destination countries). Synthetic-control papers use placebo permutation (Borbely; a Norwegian thesis with 12 donors cannot get p below about 0.08); Khordagui uses block bootstrap plus 1,000 random placebo assignments; Albert et al. report 68% bands. No aviation paper read uses Conley-Taber, Ferman-Pinto, wild cluster bootstrap or randomization inference at the country level.

8. **Timing and anticipation matter at monthly frequency.** Germany taxed bookings from 1 Sep 2010 for departures from 1 Jan 2011; Austria started 1 Apr 2011; Sweden was decided 22 Nov 2017 and started 1 Apr 2018; the Dutch tax ran 1 Jul 2008 to 1 Jul 2009. Sources conflict on Norway (1 Jun 2016 in a thesis vs "January 2016" in Bernardo et al. Table 1) and UK APD (1 Nov 1994 in Seetaram et al. vs 1998 in Bernardo et al. Table 1), so code dates from legal texts. For the ETS, 2012 is ambiguous (stop-the-clock), 2013 is the first clean year, Croatia joins 2014, Swiss hubs 2020, and 2024 brings the first free-allocation cut and the outermost-region scope change (Directive (EU) 2023/958).

9. **Implications for our design** (compiler's recommendations, not claims of the papers): (a) staggered tax DiD with Callaway-Sant'Anna or imputation on airport-month seats and airport-year centrality, never-treated airports far from taxed borders as controls, and de Chaisemartin-D'Haultfoeuille for on/off taxes and rate changes; synthetic DiD for each single-country event; (b) border-ring airports and non-EU hubs (Istanbul, Dubai, Doha, Abu Dhabi) estimated as separate exposed groups, never as controls; (c) for the ETS, replace "EEA x EUA" by an exposure dose (pre-period share of ETS-covered seats x EUA price) with region-by-year effects for Gulf and Istanbul trends, a Kaenzig-surprise instrument or check, and price-regime nonlinearity; (d) outcomes seat-weighted and unweighted, in logs or ranks, annual for betweenness, split by LCC vs network carrier and by distance band; (e) country-level clustering plus wild cluster bootstrap, randomization inference over countries and dates, and Conley-Taber or Ferman-Pinto intervals.

10. **Contribution.** The paper would be the first ex-post evaluation to use airport network centrality as the outcome for either instrument, the first to put ticket taxes and the ETS in one global airport network (6,387 airports), and the first to measure relocation to non-EU hubs on the supply side for all markets rather than for two intercontinental O-D regions (Fageda and Oesingmann) or one carrier group (Zhang et al. 2026). It must cite and differentiate Fageda and Teixido (2022, JEEM) and Zhang et al. (2026, Energy Economics). Expectations from the literature: little or positive effect at taxed hubs, losses at LCC and secondary airports, short-lived tax effects, and ETS effects only in the high-price years after 2018, which overlap COVID and the Gulf and Istanbul expansion.

## 2. Design checklist derived from the review (recommendations)

| Design element | What the literature did | What we should do |
|---|---|---|
| Treatment unit and timing | Country-level tax adoption, annual (Bernardo et al.; Helmers); ETS 2013 binary (Fageda and Teixido) | Monthly seats with legal implementation dates; anticipation window for booking-based taxes (DE Sep-Dec 2010); annual centrality with transition years flagged |
| Reversible taxes | Dropped (NL 2008-09, IE, MT in Bernardo et al.) | Keep them with de Chaisemartin-D'Haultfoeuille (M05) as extra identifying variation; drop from the absorbing CS sample |
| Dose | Tax in EUR (Gurr and Moser; Wozny; Bernardo et al. Table A4); sqrt EUA price (Fageda and Oesingmann) | Tax EUR per passenger by distance band; ETS exposure = pre-period ETS-covered seat share x EUA price; test price regimes |
| Controls | Untaxed countries; buffers of 150 km or 350 km | Far-away untaxed airports; matching on pre-period level and growth (as in Dechezlepretre et al. 2023) |
| Spillovers | Border airports as 2nd treated group (Borbely); market split by hub competition (Fageda and Oesingmann) | Distance rings (0-150, 150-350 km) and a non-EU hub group, each with own estimate and pre-trend test (Butts 2023) |
| Outcomes | Passengers, flights, seats, CO2; centrality only in merger papers | Seats (LCC vs network, distance bands); betweenness and eigenvector (weighted and unweighted, logs or ranks); time-feasible hub index; share of feasible one-stop capacity via EEA vs IST vs Gulf hubs |
| Estimators | TWFE, CS, SCM, SDID (mergers), PSM-DID, SVAR, PPML | CS and BJS imputation (main), Sun-Abraham event studies, weighted stacked DiD, SDID per country, dCDH for on/off and continuous; Goodman-Bacon diagnostic |
| Inference | Route clusters; some country clusters; SCM placebos | Country clusters + boottest WCR; randomization inference over countries and dates; Conley-Taber, Ferman-Pinto; HonestDiD sensitivity |
| Confounders | Crisis 2008-09 (NL, IE), flight shame (SE), COVID | Region-by-year FE for Gulf/Istanbul; drop or separately model 2020-21; airport-specific trends as robustness |

## 3. Main table: core empirical studies (35)

| ID | Study | Policy, period | Unit, data, frequency | Design | Displacement handling | Inference | Headline (numbers) | Hub / centrality | Status |
|---|---|---|---|---|---|---|---|---|---|
| T01 | Gordijn, H.; Kolkman, J. (2011) | NL tax, Jul 2008-Jul 2009 | Schiphol and named foreign airports; monthly/annual; IATA, MIDT, survey | Descriptive accounting vs IATA European growth; trend extrapolation | Foreign airports estimated as outcomes | None | Schiphol OD -6.9% (about 1.9m); about 1.2m defections abroad (DUS 450k, Weeze 275k, BRU 175k) | Transfer kept rising; no centrality | VERIFIED |
| T02 | Bundesregierung (2012); Annex III by Peter, M.; Bertschmann-Aeppli, D.; Zandonella, R.; Maibach, M. (Infras) (2012) | DE tax, 2011 | German clusters, foreign airports within 200 km, hubs; annual; Destatis, Eurostat | Descriptive + elasticity simulation + factor analysis | Displacement as outcome (border, hubs by land, hubs by air) | None | Up to 2.0m passengers (about 1.1%); 750k abroad (200k border, 150k hubs by land, 400k hubs by air) | Yes: LHR, CDG, AMS gained German-origin traffic | VERIFIED |
| T03 | Schoenpflug, K.; Paterson, I.; Sellner, R. (2012) | AT tax, Apr 2011 | National; annual | GDP-elasticity simulation | Travel cost only | None | About -30,000 passengers (middle scenario); 2014: no tax-caused fall | Transit at Linz collapsed | VERIFIED |
| T04 | Gurr, P.; Moser, M. (2017) | DE tax bands, 2010-16 | 61 destination countries from German airports; annual | OLS, destination and year FE, tax-rate dose | No foreign controls (on purpose) | Country clusters (61) | -0.2% per euro (10% level); later rate changes n.s. | No | VERIFIED |
| T05 | Falk, M.; Hagsten, E. (2019) | DE+AT, 2011 | 310 airports, 30 countries; 2008-16 | Dynamic panel DiD | Secondhand: 2-hour band | Not read | -9% then -5%; LCC airports drive it; hubs unaffected | LCC vs hub split | PARTIAL |
| T06 | Borbely, D. (2019) | DE, 2011 | Airport; annual 2003-15; Eurostat | Synthetic control per airport | 13 border airports as 2nd treated group, out of donors | Placebo RMSPE p-values | About -2% (4m/yr) at German airports; border airports mostly gained (EIN, AMS, BSL p<0.05; LUX p=0.057); FRA n.s. | Hub vs regional split | VERIFIED |
| T07 | Bernardo, V.; Fageda, X.; Teixido, J. (2024) | DE/AT 2011, NO 2016, SE 2018 | Airline-route; annual 2007-19; RDC | CS staggered DiD + entropy balancing; TWFE | Drop control airports within about 150 km; drop reversal countries | Route clusters | LCC flights -12.2%; network -1.1% n.s.; all -4.2%; about -1% per euro | Network carriers do not respond | VERIFIED |
| T08 | Helmers, V.; van der Werf, E. (2025) | DE, 2011 | Airport; annual 2005-19; Eurostat | Event study, 5 estimators, specification curve | Exclude foreign airports within 350 km | Country clusters (27) | 2011: -7% to -11%; fades by 2013 | Transfer shares FRA 53.7%, MUC 38% | VERIFIED |
| T09 | Zijlstra, T.; 't Hoen, A. (2026) | NL 2021, 2023 increase | 5 Dutch + 12 border airports; survey | Descriptive | Border airports as outcome | None | NL -3.4%, border -5.5% (2019 to 2025); 13% of Dutch adults fly from abroad, stable | Most German residents at AMS are transfers | VERIFIED |
| T10 | Wozny, F. (2024) | SE, Apr 2018 | Itinerary; monthly; Sabre MI | Continuous-tax DiD vs DK, FI | Drop SE-DK/FI itineraries; spec curve with NL/LV/EE/LT | City-pair (country-pair robustness) | Pass-through 0.95; passengers -9.1%; elasticity -0.86 | Return-flow spillovers | VERIFIED |
| T11 | Strale, J. (2021) | SE, Apr 2018 | Passengers; prices | Synthetic control + IV | Abstract: no leakage | Not read | Price elasticity -0.76 | Not read | PARTIAL |
| T12 | Collet, C.; Quirion, P.; Taconet, N. (2023) | Taxes + HSR, Europe 2001-19 | Route | DiD | Not read | Not read | -1% traffic per euro; taxes = 3% of EU aviation CO2 | Not read | PARTIAL |
| T13 | Oesingmann, K. (2022) | ETS + DE/AT taxes | Country pairs | PPML gravity | Not read | Not read | ETS n.s.; taxes negative; intensity < dummy | No | PARTIAL |
| T14 | Seetaram, N.; Song, H.; Page, S.J. (2014) | UK APD, 1994-2010 | 10 destinations; quarterly | ARDL per destination | None | Diagnostics only | APD significant for 5 of 10; elasticities below 1 | No | VERIFIED |
| T15 | Mayor, K.; Tol, R.S.J. (2007) | UK APD scenarios | Tourism flows, model | Simulation | None | None | APD doubling: -163,000 arrivals (0.4%) in 2010 | No | VERIFIED |
| T16 | Veldhuis, J.; Zuidberg, J. (2009) | IE ATT, 2009 | Irish airports, OAG seats | Scenario model | Capacity redeployment narrative | None | -870k to -1.33m passengers/yr; Irish capacity -16.1% (Sep 2009) | Verbal only | VERIFIED |
| T17 | CE Delft (Schroten, A. et al.) with SEO Amsterdam Economics (2019) | EU taxes, 2015 base | Country; IATA, Eurostat | Partial-equilibrium simulation | Airport choice not modelled | None | Abolishing all EU aviation taxes: +4% passengers | Stated limitation | VERIFIED |
| E01 | Fageda, X.; Teixido, J.J. (2022) | ETS from 2013 | Airline-route; quarterly 2010-16; RDC | DiD + entropy balancing + event study | Non-EEA-only controls as robustness | Route clusters | CO2 -4.7%; -9.8% with non-EEA-only controls; LCC -11% | No | VERIFIED |
| E02 | Fageda, X.; Oesingmann, K. (2025) | ETS 2013-2023 | One-stop itinerary; annual; Sabre MIDT | sqrt(EUA price) x EEA-hub itinerary; high-dim FE | Hub-competition vs no-competition split | Route clusters | -0.041; -0.038 (hub competition) vs -0.060; visible from 2018 | Yes: connecting pax shift to non-EEA hubs | VERIFIED |
| E03 | Fageda, X.; Oesingmann, K. (2025) | ETS 2013, tourism | City pair; annual 2010-22; Sabre | DiD + entropy balancing | EEA-only / non-EEA-only controls | Route clusters | Passengers -0.0265 n.s.; non-stop CO2 -0.0745 | No | VERIFIED |
| E04 | Albert, J.-F.; Gomez-Fernandez, N.; Boto-Garcia, D. (2025) | ETS policy shocks | EU, monthly 2005-19 | Proxy SVAR (Kaenzig instrument) | None | 68% bootstrap bands | Air HICP +5%; domestic pax up to -1.2%; extra-EU n.s. | No | VERIFIED |
| E05 | Kang, Y.; Liao, S.; Jiang, C.; D'Alfonso, T. (2022) | ETS 2012 | Carrier-route; annual 2007-17; OAG | Synthetic control | Not read | Not read | Seats down more than 20% at peak; LCC and short haul larger | Hub vs non-hub routes | PARTIAL |
| E06 | Zhang, R.; Shen, H.; Luo, L.; Zhao, Y. (2026) | ETS, Chinese airlines | Route; quarterly 2011-19; OAG | PSM-DID | Leakage to own domestic routes | Not read | -12.25% ETS routes; +3.61% domestic | No | PARTIAL |
| E07 | Zhang, Y.; Wang, K. (2024) | ETS 2013 | Country; 60 countries 2000-19 | Panel DiD | Not read | Not read | -690 kt total, -401 kt domestic CO2; international n.s. | No | PARTIAL |
| E08 | Dray, L.; Doyme, K. (2019) | UK carbon price (hypothetical) | City pairs; 2015 | Simulation (AIM) | Leakage as outcome | Ranges | USD 300/t: transfers via UK hubs -0.64m, via non-UK hubs +0.31m | Yes | VERIFIED |
| E09 | Wei, T.; Kallbekken, S. (2024) | Fit for 55 | AIM + CGE; 2015-50 | Simulation | Itinerary choice internal | None | Aviation leakage small/negative; intra-EU RPK -13% by 2050 | Hub switching unquantified | VERIFIED |
| E10 | Scheelhaase, J.; Grimme, W.; Maertens, S. (2024) | 2023 ETS reform | Legal texts | Descriptive | n/a | n/a | Free allocation -25% (2024), -50% (2025), none from 2026 | n/a | VERIFIED |
| H01 | Khordagui, N. (2025) | US mergers | Airport-quarter; DB1B | Synthetic DiD per merger | Drop later-treated controls | Block bootstrap + 1,000 placebos | NW-DL long run: betweenness -27.6%, eigenvector -5.2% | Centrality is the outcome | VERIFIED |
| H02 | Ciliberto, F.; Cook, E.E.; Williams, J.W. (2019) | US mergers | Airport-month; T-100 | Before-after windows, airport FE + trends | No controls | Not stated | Near zero, n.s. | Centrality is the outcome | VERIFIED |
| H03 | Bernardo, V.; Fageda, X. (2017) | Morocco-EU open skies | Airport pair; annual; RDC | Route DiD | Other North African countries as controls | Route clusters | Seats +24%; odds of service 1.5 to 3.5x | No | VERIFIED |
| H04 | Allroggen, F.; Wittman, M.D.; Malina, R. (2015) | Index (GCI/GHCI) | Airport-year; OAG 1990-2012 | Index construction | n/a | n/a | Dubai share of S/SE Asia one-stop connectivity 1.2% to 7.6% (2000-12) | Hub centrality metric | VERIFIED |
| H05 | Suau-Sanchez, P.; Voltes-Dorta, A.; Rodriguez-Deniz, H. (2016) | UK hubs, May 2013 | MIDT | Descriptive | n/a | None | Dubai 39.5% of regional UK to Asia-Pacific connections | Flow betweenness | VERIFIED |
| H06 | Piltz, C.; Voltes-Dorta, A.; Suau-Sanchez, P. (2018) | EU vs Gulf hubs, 2012-16 | MIDT + OAG | Descriptive | n/a | None | East US-South Asia: EEA 52.9% to 22.4%, Middle East 32.4% to 62.3% | Hub shares | VERIFIED |
| H07 | O'Connell, J.F.; Escofet Bueno, O. (2018) | Gulf vs EU hubs, 2014 | OAG, one day | Connectivity ratio | n/a | None | EY 2.31, QR 2.17, AF 1.44, BA 1.13 | Wave quality | VERIFIED |
| H08 | Logothetis, M.; Miyoshi, C. (2018) | TK vs EK | OAG snapshots | Hub connectivity index | n/a | None | 2014: TK 103,368 vs EK 29,507 effective connections | Hub index | VERIFIED |

### 3.1 Study cards (all extracted fields)

**T01. Gordijn, H.; Kolkman, J. (2011).** Effects of the Air Passenger Tax: Behavioral responses of passengers, airlines and airports. *KiM Netherlands Institute for Transport Policy Analysis (report, February 2011)*. https://english.kimnet.nl/documents/2011/02/10/effects-of-the-air-passenger-tax-behavioral-responses-of-passengers-airlines-and-airports. Check: KiM publication page and PDF title page (no DOI).
- Status: VERIFIED
- Read: Full PDF: summary, ch. 2, ch. 4, sec. 5.2, 5.4
- Policy: Dutch air passenger tax: EUR 11.25 (EU and within 2,500 km) / EUR 45.00 (other); transfer passengers and freight exempt
- Countries: Netherlands; foreign airports in Germany and Belgium
- Period: Tax in force 1 Jul 2008 to 1 Jul 2009 (rate set to zero); data about 2000-2010
- Data: Schiphol OD passengers vs European IATA airline growth; Dutch passengers at Duesseldorf 2000-2009 (DLR); Sabre MIDT by point of sale; Brussels Airport passenger breakdown; survey of 3,000 people; interviews; system dynamics model
- Unit: Airport (Schiphol and named foreign airports)
- Frequency: Monthly (Schiphol Jan 2007-Sep 2010) and annual
- Outcomes: OD passengers; passengers by departure airport; stated behaviour
- Identification: Descriptive accounting, no regression: Schiphol OD growth minus IATA European growth (adjusted for a 0.9 pp pre-tax shortfall); Duesseldorf 2000-07 linear trend extrapolated; survey shares allocate defections across foreign airports
- Control group: European IATA airline growth as yardstick
- Displacement: Foreign airports (Duesseldorf, Weeze, Brussels, Charleroi, Muenster/Osnabrueck) estimated as separate outcomes
- Timing and anticipation: Five periods from pre-tax (Jan 2007-Jun 2008) to summer 2010; overlaps the financial crisis; no formal anticipation window
- Inference: None
- Headline: Schiphol OD -6.9% on average Jul 2008-Jun 2009, about 1.9 million fewer passengers on a base of 27.4 million (sec. 5.4, p. 60); further -1.6% Jul-Oct 2009 (about 0.96 million). Table 5.2 defections (thousands): Duesseldorf 450, Weeze 275, Brussels 175, Charleroi 75, Muenster/Osnabrueck 50, other 220, total 1,245. Survey: 14% changed behaviour, half of them used a foreign airport
- Transfer, hub, centrality: Qualitative: untaxed transfer passengers at Schiphol kept rising while OD passengers fell. No centrality
- Lesson for our design: Hub centrality can stay flat while OD demand leaks to border airports; the 2008-09 tax is reversible and overlaps the crisis; Dutch use of Duesseldorf was already trending up, so leakage outcomes need pre-trend controls

**T02. Bundesregierung (2012); Annex III by Peter, M.; Bertschmann-Aeppli, D.; Zandonella, R.; Maibach, M. (Infras) (2012).** Bericht an den Deutschen Bundestag ueber die Auswirkungen der Einfuehrung des Luftverkehrsteuergesetzes (annex: Auswirkungen der Einfuehrung der Luftverkehrsteuer auf die Unternehmen des Luftverkehrssektors in Deutschland: Ex-Post-Analyse nach einem Jahr). *Deutscher Bundestag Drucksache 17/10225 (29.06.2012); Infras final report for the Federal Ministry of Finance, Zurich, 25 June 2012*. https://dserver.bundestag.de/btd/17/102/1710225.pdf. Check: Bundestag document server PDF incl. Infras imprint.
- Status: VERIFIED
- Read: Ministry report ch. C; Infras Z.1, 5.1.1-5.1.4, 5.3, 5.4
- Policy: German Luftverkehrsteuer (departure tax by distance band)
- Countries: Germany; foreign airports within 200 km; European hubs
- Period: Data 2005-2011; evaluation of 2011
- Data: Destatis Fachserie 8 Reihe 6.1 (German airports); Eurostat 2005-2010 plus ACI growth for 2011 (foreign airports); passengers from Germany to large European hubs; prices, kerosene, GDP; airline survey and interviews
- Unit: Airport clusters; hubs
- Frequency: Annual
- Outcomes: Passengers, flights, passengers per flight
- Identification: Three approaches combined: descriptive comparison of German vs foreign cluster growth; price-elasticity simulation; factor analysis projecting 2011 from corrected 2010 with GDP and price changes (residual = tax effect)
- Control group: Foreign airports within 200 km of a German airport, grouped in West, South and East clusters (e.g. Groningen, Maastricht, Eindhoven, Liege, Luxembourg, Strasbourg, Metz; Basel, Zurich, Innsbruck, Salzburg; Prague, Szczecin)
- Displacement: Displacement is an outcome in three channels: border airports by land, nearby hubs by land, European hubs by air. Caveat: Vienna sits in the hub comparison group although Austria was taxed in 2011
- Timing and anticipation: Law passed 28 Oct 2010, in force 15 Dec 2010; applies to bookings from 1 Sep 2010 for departures from 1 Jan 2011; no anticipation adjustment
- Inference: None (ranges only)
- Headline: 1.4 to 2.2 million passengers changed behaviour in 2011, 0.5 to 1.0 million displaced abroad (sec. 5.4). Table 35: border airports 200,000 (0-400,000); nearby hubs by land 150,000 (100,000-200,000); European hubs by air 400,000 (370,000-450,000); total 750,000 (470,000-1,050,000). Ministry summary: dampening up to 2.0 million passengers (about 1.1%) while nominal traffic still grew 4.8%. Border displacement only in the West cluster
- Transfer, hub, centrality: Yes: growth of passengers flying from Germany to each hub compared with total German growth and with the hub's own growth; displacement found for Heathrow, CDG and Amsterdam, not Madrid. Through tickets are taxed to the final destination; only split tickets avoid the tax
- Lesson for our design: Two-benchmark template for hub leakage (traffic to hub vs national growth vs hub growth); in German monthly seats treat Sep-Dec 2010 as a possible anticipation window

**T03. Schoenpflug, K.; Paterson, I.; Sellner, R. (2012).** Evaluierung der Flugabgabe. *Institut fuer Hoehere Studien (IHS) Projektbericht, September 2012, for the Austrian Ministry of Finance (update 2014)*. https://irihs.ihs.ac.at/id/eprint/3023/1/IHSPR6541149.pdf ; update http://irihs.ihs.ac.at/2887/1/IHSPR6541150.pdf. Check: IHS repository and OpenAlex.
- Status: VERIFIED (2012); PARTIAL (2014 update, executive summary)
- Read: 2012: executive summary, sec. 2.3, 4.4, 5.1, 5.3; 2014: executive summary
- Policy: Austrian Flugabgabe, EUR 8 to 35 (EUR 7 to 35 from 2013)
- Countries: Austria
- Period: Tax from 1 Apr 2011; data 2004-2011 (update to 2013)
- Data: Austrian airport passengers excluding transfer and transit; Eurostat HICP air fares; kerosene prices; GDP; travel times and costs to foreign airports within 50 and 100 km
- Unit: National / airport aggregate
- Frequency: Annual
- Outcomes: Passengers
- Identification: Simulation: expected 2011 growth = GDP growth (4.91%) x income elasticity (1.0, 1.5, 1.9), kerosene adjusted, vs actual growth corrected for the 2010 ash cloud and 2011 Arab Spring (about 300,000 passengers each); second simulation with price elasticities
- Control group: None
- Displacement: Cross-border substitution assessed only through travel cost and time; costs judged mostly larger than the tax saving
- Timing and anticipation: Authors note annual data understate effects because the tax started in Q2 2011 and flights are booked months ahead
- Inference: None (scenarios)
- Headline: Middle scenario about 30,000 fewer passengers (executive summary); sec. 5.3 gives 18,000 to 28,000 depending on method. 2014 update: no signs of a tax-induced fall
- Transfer, hub, centrality: Partly: base excludes transfer and transit; tax-exempt transit at Linz collapsed (as reported). No centrality
- Lesson for our design: Date Austria to April 2011 in monthly data; Vienna was itself treated in 2011 so it cannot be a control

**T04. Gurr, P.; Moser, M. (2017).** Beeinflusst die Luftverkehrsteuer Passagieraufkommen? Ergebnisse einer Paneldatenanalyse. *Zeitschrift fuer Verkehrswissenschaft*, 88(3), 181-193. http://z-f-v.de/fileadmin/archiv/hefte---2017_1_2_3/2017-3/ZfV_2017_Heft-3_01_Gurr_Moser-Luftverkehrssteuer_Panelanalyse.pdf. Check: Journal archive PDF (not in Crossref; refcheck not found); volume and pages match citing papers.
- Status: VERIFIED
- Read: Sec. 4-5, Tables 3-4
- Policy: German Luftverkehrsteuer (rate by destination band)
- Countries: Germany; 61 destination countries
- Period: 2010-2016
- Data: Destatis monthly boarding passengers from German main airports by final destination, summed to years; GDP, exchange-rate-adjusted relative prices, political stability index
- Unit: Destination country (from German main airports)
- Frequency: Annual (balanced panel N = 427)
- Outcomes: Log boarding passengers
- Identification: OLS of log passengers on the tax rate of the destination band (zero before 2011) with destination-country and year fixed effects
- Control group: No foreign control group; identification from tax-band variation across destinations and over time
- Displacement: Foreign controls avoided on purpose: footnote 20 argues neighbouring countries' airports would absorb diverted passengers and overstate the effect
- Timing and anticipation: Introduction effect (2010-11) separated from change effect (2011-16); later rate changes tied to a revenue target and possibly endogenous
- Inference: SE clustered by destination country (61 clusters)
- Headline: Table 3 model 3: -0.00200 (SE 0.00104), significant at 10%, about -0.2% passengers per euro of tax. Table 4: introduction effect -0.00198 (SE 0.00103), N = 122; change effect 0.0176 (SE 0.0137), not significant, N = 366
- Transfer, hub, centrality: No
- Lesson for our design: Distance-band tax rates give dose variation within the taxed country without relying on contaminated foreign controls

**T05. Falk, M.; Hagsten, E. (2019).** Short-run impact of the flight departure tax on air travel. *International Journal of Tourism Research*, 21(1), 37-44 (online 2018). DOI 10.1002/jtr.2239. Check: refcheck verified (Crossref online year 2018).
- Status: PARTIAL
- Read: Abstract only (Wiley); full text blocked
- Policy: German and Austrian departure taxes (2011)
- Countries: 30 European countries, 310 airports
- Period: 2008-2016
- Data: not read
- Unit: Airport
- Frequency: not read
- Outcomes: Passengers
- Identification: Dynamic panel difference-in-differences (abstract); exact specification not read
- Control group: Untaxed European airports (secondhand, as described by Borbely 2019 and Bernardo et al. 2024)
- Displacement: Secondhand only: two-hour driving band around taxed borders; no significant border effect reported by citing papers
- Timing and anticipation: not read
- Inference: not read
- Headline: Passengers -9% in the year of introduction and -5% in the following year (abstract); decline driven by airports used mainly by low-cost carriers; hubs not affected
- Transfer, hub, centrality: Split low-cost airports vs hubs; no centrality
- Lesson for our design: Pooled airport DiD finds hubs unaffected and LCC airports hit; allow effects to differ by airport role

**T06. Borbely, D. (2019).** A case study on Germany's aviation tax using the synthetic control approach. *Transportation Research Part A: Policy and Practice*, 126, 377-395. DOI 10.1016/j.tra.2019.06.017. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: Author accepted manuscript (Strathprints 69132): sec. 2-6, Table 1, appendix Table 2; per-airport effects only in Fig. 4
- Policy: German Luftverkehrsteuer
- Countries: Germany; 13 bordering foreign airports; untaxed EEA donors
- Period: 2003-2015 (8 pre-periods); treatment 2011
- Data: Eurostat annual passengers per airport (includes arriving and transfer passengers); NUTS2 purchasing power; lagged passengers; airfare inflation
- Unit: Airport
- Frequency: Annual
- Outcomes: Passengers
- Identification: Synthetic control (Abadie et al. 2010), one model per treated airport
- Control group: Donors from untaxed countries of similar airport size; two donor sets (surrounding countries vs wider EEA), better pre-fit kept; Austria excluded
- Displacement: 21 German airports plus 13 bordering foreign airports within about two hours' drive (150 km) treated as a second treated group and kept out of donor pools: Amsterdam, Basel, Billund, Brussels, Charleroi, Eindhoven, Luxembourg, Maastricht, Metz, Prague, Rotterdam, Szczecin, Zurich
- Timing and anticipation: 2011; no anticipation discussion
- Inference: Placebo permutation: p-value = share of donor placebos with larger post/pre RMSPE ratio; pre-fit errors above 5% flagged
- Headline: About 4 million passengers a year lost across German airports, roughly 2% (sec. 4). Table 1 RMSPE ratio / p: Eindhoven 169.09 / 0.000; Amsterdam 22.13 / 0.000; Basel 10.36 / 0.038; Luxembourg 11.71 / 0.057; Munich 24.56 / 0.000; Frankfurt p = 0.818. Bordering airports mostly gained; regional German airports lost; Berlin-Tegel, Duesseldorf, Frankfurt, Munich gained
- Transfer, hub, centrality: Results grouped by hub, regional, bordering and LCC airports; transfer traffic cited as reason hubs held up. No centrality
- Lesson for our design: Treat nearby foreign airports as a second treated group excluded from controls; airport-specific effects can have opposite signs at hubs and regional airports; placebo inference template for single-country events

**T07. Bernardo, V.; Fageda, X.; Teixido, J. (2024).** Flight ticket taxes in Europe: Environmental and economic impact. *Transportation Research Part A: Policy and Practice*, 179, 103892. DOI 10.1016/j.tra.2023.103892. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: Open access: sec. 1-3, Tables 1-6, figure captions (sec. 4 partly; appendix not read)
- Policy: National ticket taxes; identified from Germany and Austria (2011), Norway (2016), Sweden (2018)
- Countries: EEA plus UK
- Period: 2007-2019
- Data: RDC Aviation Apex-Schedules and Apex-Fares (fares 2013-2019, 15,238 pairs); Eurocontrol Small Emitters Tool for CO2; NUTS3 income and population; route HHI; OAG MIDT 2016 transfer shares (Fig. 1)
- Unit: Airline x route (61,964 airline-route pairs)
- Frequency: Monthly collapsed to annual
- Outcomes: Log flights, log CO2, fares
- Identification: TWFE (airline-route and year FE) and Callaway-Sant'Anna staggered DiD (doubly robust) with entropy balancing on 2008-2010 covariates; event study (Fig. 5); quarterly estimates (Table 3)
- Control group: Routes untaxed at both ends; UK, France, Italy (older taxes) kept as controls (dropped in Table A2); Ireland, Netherlands and Malta dropped because their taxes were reversed
- Displacement: SUTVA check (Table 4): drop control airports within about two hours' drive (usually under 150 km) of a taxing border
- Timing and anticipation: Annual coding; flat pre-trends, effect builds gradually; anticipation not discussed in parts read
- Inference: SE clustered by route; number of clusters not reported; no bootstrap
- Headline: Table 2 col. 4 (CS, LCC sample, N = 27,116): ln flights -0.122 (SE 0.024), ln emissions -0.140 (SE 0.024); TWFE cols 1-3 flights -0.090, -0.085, -0.162. Table 4 (SUTVA sample) flights -0.125 (SE 0.025). Table 5: LCC -0.122, network airlines -0.011 (SE 0.020, n.s.), all airlines -0.042 (SE 0.012). About 1% fewer flights per euro of tax (TWFE, text)
- Transfer, hub, centrality: Indirect: network carriers do not respond because transfers are exempt; transfer shares shown for Lufthansa, KLM, Austrian, SAS. No centrality
- Lesson for our design: Closest analogue to our staggered design: CS estimator, drop reversal countries (or model them), buffer robustness; expect effects through LCC route withdrawal rather than network carriers

**T08. Helmers, V.; van der Werf, E. (2025).** Did the German aviation tax have a lasting effect on passenger numbers?. *Transportation Research Part D: Transport and Environment*, 140, 104570. DOI 10.1016/j.trd.2024.104570. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: Open access full article
- Policy: German Luftverkehrsteuer
- Countries: Germany vs EU airports in untaxed countries
- Period: 2005-2019
- Data: Eurostat annual departing passengers per airport; GDP per capita; accommodation price index; terrorism dummy
- Unit: Airport (basic sample 289 airports, 26 hubs, 27 countries)
- Frequency: Annual
- Outcomes: Log departing passengers
- Identification: Event study with year-specific treatment dummies 2011-2019 and pre-dummies 2006-2009 (2010 reference); five estimators: static TWFE, pooled OLS with lagged DV, dynamic FE, Arellano-Bond, QML; specification curve over 175 specifications
- Control group: EU airports in countries without a tax; Austria, France, Ireland, Italy, Netherlands and UK excluded
- Displacement: Non-German airports within 350 km of the German border excluded from the main analysis; re-enter as an additional treated group in robustness
- Timing and anticipation: Tax announced a few months ahead; pre-dummies significant only in some models (dynamic FE 2006-07; QML 2006)
- Inference: SE clustered by country (27 countries in basic sample); robust SE where the estimator requires
- Headline: Table 2, 2011 effect across the five estimators: -0.100, -0.068, -0.113, -0.100, -0.109 (about -7% to -11%); non-hub airports -9% to -13% (Table 3). Specification curve (Table 5): 99% of specifications significant for 2011, 38% for 2012, 0% for 2013
- Transfer, hub, centrality: Measurement issue only: 2019 transfer shares 38% at Munich and 53.7% at Frankfurt mix taxed and untaxed passengers. No centrality
- Lesson for our design: Use a wide buffer (350 km) and year-by-year effects; the effect fades after about two years; country clustering with few countries is fragile

**T09. Zijlstra, T.; 't Hoen, A. (2026).** Vliegen vanuit het buurland: Leidt de vliegbelasting tot ander uitwijkgedrag?. *KiM Notitie (March 2026)*. https://www.kimnet.nl/documenten/2026/03/24/vliegen-vanuit-het-buurland (printed DOI 10.82230/KiM.MB2531, not checked in Crossref). Check: KiM publication page and PDF.
- Status: VERIFIED
- Read: Summary, ch. 1, sec. 2.3, 5.1, Appendix A
- Policy: Dutch flight tax reintroduced 2021 (EUR 7.85), raised 2023 (EUR 26.43); distance bands planned from 2027; Schiphol charges +13% in 2024
- Countries: Netherlands; 12 nearby foreign airports
- Period: 2017-19 vs 2023-25 (survey 2004-2024)
- Data: Passenger totals at 5 Dutch and 12 border airports (2019 vs 2025); Schiphol passenger survey 2004-2024 (1,140,663 respondents, transfer removed); airport-provided resident shares; licence-plate counts; earlier KiM surveys
- Unit: Airport; survey respondents
- Frequency: Annual
- Outcomes: Passengers; share of Dutch residents departing abroad
- Identification: Descriptive only
- Control group: Informal comparison with 12 border airports; reverse flow of neighbours using Dutch airports tracked
- Displacement: Border airports treated as the outcome of interest
- Timing and anticipation: COVID confounds 2021
- Inference: None
- Headline: Dutch airports 81.2 million (2019) to 78.4 million (2025), -3.4%; foreign border airports 80.6 million to 76.2 million, -5.5%; about 13% of Dutch adults depart from abroad, stable in 2013, 2016 and 2024 (sec. 5.1)
- Transfer, hub, centrality: Measurement point: of about 1.7 million German-resident departing passengers at Schiphol in 2024, about 1.2 million were transfer passengers and about 190,000 (11%) arrived overland
- Lesson for our design: The 2023 Dutch rate increase is a cleaner event than the 2021 reintroduction; hub totals mix transfer and resident leakage, so measure leakage at border airports or in LCC seats

**T10. Wozny, F. (2024).** Tax Incidence in Heterogeneous Markets: The Pass-through of Air Passenger Taxes on Airfares. *IZA Discussion Paper 16783 (February 2024)*. DOI 10.2139/ssrn.4717696 (SSRN version); IZA DP 16783. Check: refcheck verified (SSRN record); IZA PDF title page.
- Status: VERIFIED
- Read: IZA PDF read by the compiler: abstract, sec. 1, 3, 5.2, spillover and robustness passages, conclusion
- Policy: Swedish air passenger tax (SFS 2017:1200), three distance zones
- Countries: Sweden vs Denmark and Finland (robustness: Netherlands, Latvia, Estonia, Lithuania)
- Period: Tax decided 22 Nov 2017, in force 1 Apr 2018; schedule data 2015-2019; post period to Dec 2019
- Data: Sabre Market Intelligence (validated GDS bookings aggregated monthly; fares, passengers); Sabre schedule data for departures and seats per flight
- Unit: Itinerary (origin-destination airport pair x airline x booking class); 257,550 itinerary-month observations, 42,773 itineraries (balanced)
- Frequency: Monthly
- Outcomes: Airfares, passengers, RPK, departures, seats
- Identification: DiD with a continuous tax-rate treatment (USD) for departures from Sweden vs departures from Denmark and Finland; event studies; specification curve
- Control group: Itineraries departing Denmark and Finland (Norway excluded because it had its own tax)
- Displacement: Itineraries between treated and control countries dropped; specification curve randomly excludes NUTS-3 regions and randomly swaps in Netherlands, Latvia, Estonia, Lithuania (nearest untaxed countries without a direct border) for Denmark and Finland; return-itinerary spillovers estimated
- Timing and anticipation: Pre-trends similar, including months just before the reform; author concludes no anticipation
- Inference: SE clustered by city pair; robustness with country-pair clustering (Table A8)
- Headline: USD 1 of tax raises fares by USD 0.95 (conclusion); incidence 0.366 in monopoly vs 1.02 in non-monopoly markets; passengers -9.1% on average (conclusion; 9.2% in the introduction); economy-class elasticity -0.86; RPK from Sweden -6.96 billion in 2019 and -4.93 billion on return itineraries; fewer departures and seats (magnitude not extracted)
- Transfer, hub, centrality: No centrality; inbound return-flow spillovers analysed
- Lesson for our design: Monthly continuous-tax DiD with near-neighbour controls is feasible; but Copenhagen and Helsinki are controls here, whereas in our design they are leakage candidates and belong in an exposed group

**T11. Strale, J. (2021).** The Effects of the Swedish Aviation Tax on the Demand and Price of International Air Travel. *Working Paper 2021:02, Department of Economics, SLU (also Paper II of the 2022 SLU PhD thesis 'Travel demand and environmental policy')*. https://research.slu.se/en/publications/the-effects-of-the-swedish-aviation-tax-on-the-demand-and-price-o/. Check: SLU research portal record.
- Status: PARTIAL
- Read: Abstract and thesis summary (PDF behind bot check)
- Policy: Swedish aviation tax
- Countries: Sweden
- Period: Tax from April 2018; sample period not read
- Data: International air passengers from Sweden; web-scraped route-level prices; other sources not read
- Unit: not read
- Frequency: not read
- Outcomes: Passengers; prices
- Identification: Synthetic control for passengers and prices; IV for the price elasticity
- Control group: Donor pool not read
- Displacement: Abstract reports no leakage to neighbouring countries; method not read
- Timing and anticipation: Passenger effect grows over time while price effect fades; 'Greta Thunberg' effect tested, no direct evidence
- Inference: not read
- Headline: Price elasticity -0.76; price effects explain the first three quarters; later growing gap interpreted as a symbol effect (abstract)
- Transfer, hub, centrality: not read
- Lesson for our design: Swedish tax overlaps the flight-shame period; Oslo is not a valid control (Norway taxed from 2016)

**T12. Collet, C.; Quirion, P.; Taconet, N. (2023).** Air Passenger Taxes and High Speed Railways Decrease CO2 Emissions from Aviation: Evidence from Europe. *SSRN working paper (posted 4 Jul 2023, 27 pp.)*. DOI 10.2139/ssrn.4499806. Check: Crossref and SSRN page.
- Status: PARTIAL
- Read: SSRN abstract page (PDF not accessible)
- Policy: National passenger taxes and HSR openings
- Countries: Europe
- Period: 2001-2019
- Data: not read
- Unit: Route
- Frequency: not read
- Outcomes: Air traffic; CO2 equivalent
- Identification: Difference-in-differences at the route level (abstract)
- Control group: not read
- Displacement: not read
- Timing and anticipation: not read
- Inference: not read
- Headline: A 1 euro increase in passenger taxes reduces air traffic by 1%; 1 km of HSR reduces traffic by 0.24% on the main competing air route; over 2001-2019 taxes equal a 3% reduction in European aviation CO2, HSR openings over 50 km 0.4% (abstract)
- Transfer, hub, centrality: not read
- Lesson for our design: Tax-in-euros dose specification gives about -1% per euro, consistent with Bernardo et al.; worth obtaining the full text (closest multi-country tax panel besides Bernardo et al.)

**T13. Oesingmann, K. (2022).** The effect of the European Emissions Trading System (EU ETS) on aviation demand: An empirical comparison with the impact of ticket taxes. *Energy Policy*, 160, 112657. DOI 10.1016/j.enpol.2021.112657. Check: refcheck verified; Crossref.
- Status: PARTIAL
- Read: Abstract, highlights, introduction and section snippets (paywalled)
- Policy: EU ETS (intra-EEA flights) and the German and Austrian ticket taxes
- Countries: EEA country pairs
- Period: not read
- Data: not read
- Unit: Country pair
- Frequency: not read
- Outcomes: Passenger flows
- Identification: Structural gravity estimated by PPML with fixed effects; policy dummies and policy-specific intensity variables
- Control group: not read
- Displacement: not read
- Timing and anticipation: not read
- Inference: not read
- Headline: No significant EU ETS effect on intra-EEA passengers; Austrian and German taxes have robust negative effects; intensity variables give smaller effects than dummies (abstract and highlights; coefficients not read)
- Transfer, hub, centrality: Not possible with country-pair data
- Lesson for our design: Report both dummy and intensity codings; estimate taxes and ETS jointly

**T14. Seetaram, N.; Song, H.; Page, S.J. (2014).** Air Passenger Duty and Outbound Tourism Demand from the United Kingdom. *Journal of Travel Research*, 53(4), 476-487 (online 2013). DOI 10.1177/0047287513500389. Check: refcheck verified; Crossref.
- Status: VERIFIED (text; Tables 3-4 missing in preprint)
- Read: Bournemouth eprint, June 2013 preprint
- Policy: UK Air Passenger Duty and its changes (1994 start, 1997 doubling, 2001 reform, 2007 doubling, 2009 distance bands)
- Countries: UK outbound to 10 destinations (about 58% of outbound travel)
- Period: 1994Q4-2010Q4
- Data: ONS UK resident departures (all modes); HMRC APD rates; IMF GDP, CPI, exchange rates
- Unit: Destination country
- Frequency: Quarterly
- Outcomes: Outbound visits
- Identification: ARDL bounds test (Pesaran, Shin and Smith 2001) per destination, logs, AIC lags, event dummies (9/11, SARS, 2008 crisis, 1995 strikes)
- Control group: None
- Displacement: None; authors note displacement unresolved
- Timing and anticipation: Tax changes enter through the APD series
- Inference: Time-series diagnostics only; several destination models fail one or two tests
- Headline: APD coefficient negative and significant (5% or 10%) for 5 of 10 destinations; all absolute tax elasticities below 1; income elasticities 0.36 to 4.11; price elasticities -0.05 to -2.02 (abstract, sec. 4.2)
- Transfer, hub, centrality: No
- Lesson for our design: National time series cannot separate APD changes from macro shocks; use APD rate changes as intensity shocks in a panel with untaxed comparison airports

**T15. Mayor, K.; Tol, R.S.J. (2007).** The impact of the UK aviation tax on carbon dioxide emissions and visitor numbers. *Transport Policy*, 14(6), 507-513. DOI 10.1016/j.tranpol.2007.07.002. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: ESRI Working Paper 187 (states it was published as the Transport Policy article)
- Policy: UK APD scenarios: original APD, February 2007 doubling, abolition, 'green air miles', revenue-equal emissions tax
- Countries: UK; 207 countries in model
- Period: Results for 2010
- Data: Hamburg Tourism Model v1.3 calibrated to 1995 data (WTO, Euromonitor); travel cost linear in distance
- Unit: Country (tourism flows)
- Frequency: Comparative statics
- Outcomes: Tourist arrivals and departures; CO2
- Identification: Simulation; destination-choice airfare elasticity -1.50 + 0.14 ln y (-0.45 for UK travellers)
- Control group: None
- Displacement: Destination shifts by distance band; no airport choice
- Timing and anticipation: Not applicable
- Inference: None (sensitivity runs)
- Headline: Doubling APD cuts UK arrivals by about 163,000 in 2010 (0.4%) (sec. 3.2); abolition adds about 169,000; emissions rise slightly under base assumptions
- Transfer, hub, centrality: No
- Lesson for our design: Flat or banded taxes shift the distance mix of trips; distance bands should enter treatment intensity

**T16. Veldhuis, J.; Zuidberg, J. (2009).** The Implications of the Irish Air Travel Tax. *SEO-rapport 2009-77, SEO Economic Research, Amsterdam (commissioned by Aer Lingus, Ryanair, CityJet; not peer reviewed)*. https://www.seo.nl/wp-content/uploads/2020/04/2009-77_The_Implications_of_the_Irish_Air_Travel_Tax.pdf. Check: SEO publication page and UvA-DARE record.
- Status: VERIFIED
- Read: Full report
- Policy: Irish Air Travel Tax from 30 Mar 2009: EUR 10 (over 300 km from Dublin), EUR 2 (within 300 km); transfer and transit exempt
- Countries: Ireland
- Period: Base 2008; capacity through summer and September 2009
- Data: Confidential airline traffic and yield data; OAG seats by Irish airport (2008, Sep 2009); airport charges; tourism spending
- Unit: Airport; airline
- Frequency: Monthly snapshots
- Outcomes: Departing passengers; seat capacity
- Identification: Scenario model: full pass-through with elasticities (-1 leisure, -0.3 business, Ryanair -0.5 to -1.5); observed capacity cuts with 50-95% absorption
- Control group: None (contrast with Ryanair network-wide growth)
- Displacement: Attributes capacity redeployment to untaxed EU bases; notes Aer Lingus growth at Gatwick; recession not controlled
- Timing and anticipation: First months after introduction
- Inference: None
- Headline: Table 4.2: -870,000 departing passengers a year (full pass-through scenario); Table 5.2: -1,331,000 a year from capacity cuts as of summer 2009; Irish departing capacity -16.1% year on year in Sep 2009 while Ryanair network passengers rose almost 17%; Dublin, Shannon, Cork capacity -16% to -20%
- Transfer, hub, centrality: Connectivity discussed only verbally
- Lesson for our design: Main margin is LCC base reallocation across countries, which OAG seats observe directly; Irish tax gives introduction (2009), cut (2011) and abolition (2014) events, but 2009 coincides with the recession

**T17. CE Delft (Schroten, A. et al.) with SEO Amsterdam Economics (2019).** Taxes in the Field of Aviation and their impact. *Final report for the European Commission, DG MOVE (June 2019); ISBN 978-92-76-08132-6*. DOI 10.2832/913591 (EU Publications Office; not a Crossref DOI); https://cedelft.eu/wp-content/uploads/sites/2/2021/03/CE_Delft_7M16_taxes_in_the_field_of_aviation_and_their_impact.pdf. Check: PDF title page; DOI resolves to op.europa.eu (per strand agent).
- Status: VERIFIED (executive summary and modelling chapter)
- Read: Sec. 1, 3.1-3.4; country chapters skimmed
- Policy: Inventory of EU28 aviation taxes; ex-ante abolition/introduction of ticket taxes, VAT, kerosene excise
- Countries: EU28 and selected non-EU
- Period: Base year 2015
- Data: IATA Ticket Tax Box Service; IATA airport charges; PaxIS; Eurostat passengers (transfer subtracted); Eurostat kerosene sales
- Unit: Country
- Frequency: Static
- Outcomes: Passengers, fares, revenue
- Identification: Partial-equilibrium simulation with Intervistas (2007) elasticities (-1.23 domestic, -1.12 European, -0.8 intercontinental); full pass-through
- Control group: None
- Displacement: Airport choice not modelled; sec. 3.4.2-3.4.3 note impacts are overestimated where many transfer passengers use a country's hubs
- Timing and anticipation: Static
- Inference: None
- Headline: Weighted average EU aviation tax EUR 11 per ticket; abolishing all EU aviation taxes would raise passengers by 4%; ending the kerosene exemption raises ticket prices by 10% and cuts demand by 11% (executive summary, p. 11)
- Transfer, hub, centrality: Stated limitation (transfer traffic, airport choice)
- Lesson for our design: The official EU benchmark ignores airport choice and transfer traffic, the margin our centrality outcome measures

**E01. Fageda, X.; Teixido, J.J. (2022).** Pricing carbon in the aviation sector: Evidence from the European emissions trading system. *Journal of Environmental Economics and Management*, 111, 102591. DOI 10.1016/j.jeem.2021.102591. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: Open access PDF (UB repository): sec. 1-5, Tables 1-6; key numbers re-checked by the compiler
- Policy: EU ETS for aviation (intra-EEA scope after stop-the-clock)
- Countries: 44 European countries (EEA plus non-EEA Europe incl. Russia, Turkey, Switzerland, Ukraine)
- Period: 2010-2016
- Data: RDC Aviation capstats; Eurocontrol Small Emitters Tool for CO2; UN/Eurostat population; GDP per capita; monopoly dummy
- Unit: Airline x route (airport pair); 402,589 regression observations
- Frequency: Quarterly
- Outcomes: Log CO2, log flights; route exit (LPM)
- Identification: DiD with route-airline, year and quarter FE; entropy balancing on pre-2013 covariates; year-by-year event study (base 2010)
- Control group: Routes with at least one non-EEA European endpoint; North Africa and Middle East excluded (Arab Spring); Israel excluded (2013 open skies)
- Displacement: SUTVA section names demand displacement to control destinations and network airlines shifting connecting traffic; remedies: non-EEA-only controls (Table 4), Ryanair-only treated group, departure-tax dummies for Germany, Austria, Ireland
- Timing and anticipation: Treatment from 2013 (stop-the-clock, Decision 377/2013); 2012 ambiguous and dropped in robustness; Croatia from 2014; effects significant from 2014
- Inference: SE clustered by route (route-airline clustering virtually identical); number of clusters not reported; no bootstrap
- Headline: Table 2: emissions -9.2% without reweighting, -0.047 (SE 0.018) with entropy balancing; flights -0.049 (SE 0.018); short haul -0.107 (SE 0.050); Table 3: network airlines -0.020 (n.s.), low-cost -0.110 (SE 0.022); Table 4 (non-EEA-only controls): emissions -0.098 (SE 0.027), short haul -0.169 (SE 0.059); route exit probability +0.022 (Table 6); German departure tax -0.053 (SE 0.021) (Table 5 col. 1)
- Transfer, hub, centrality: No hub analysis; hub-and-spoke appears as mechanism and SUTVA threat
- Lesson for our design: Control-group choice doubles the estimate: nearby non-EEA hubs must be a separate spillover-exposed group, not controls

**E02. Fageda, X.; Oesingmann, K. (2025).** Intercontinental air travel in the era of carbon pricing: demand and hub shifts. *Transportation Research Part A: Policy and Practice*, 200, 104658. DOI 10.1016/j.tra.2025.104658. Check: refcheck partial_match 0.9 (no discrepancies); Crossref.
- Status: VERIFIED
- Read: Open access PDF (UB repository): sec. 1-6, Tables 1-7; key numbers re-checked by the compiler
- Policy: EU ETS on the intra-EEA first leg of one-stop itineraries
- Countries: EEA, UK and Swiss origins to North America and Asia
- Period: 2010-2023 (main sample excludes 2020-21)
- Data: Sabre MIDT O-D passengers by origin, connecting airport, destination, operating airline; leg frequencies and non-stop availability; hand-coded joint ventures; daily EUA prices (Investing.com) averaged to years
- Unit: One-stop itinerary (origin x connecting airport x destination x airline); 1,835,052 observations
- Frequency: Annual
- Outcomes: Log passengers
- Identification: Continuous treatment: yearly EUA price (square-root transformed, read as elasticity) x itinerary connecting at an EU ETS hub; FE: origin-airport x year, destination-airport x year, route, airline x year; event study (base 2012); dummy version (Table A3)
- Control group: Itineraries connecting at non-ETS hubs (Gulf, Istanbul, Asian and North American hubs)
- Displacement: Spillover is the object: markets split into hub competition (both hub types present) vs no hub competition
- Timing and anticipation: Treatment year 2013 (2012 untreated because free allocation exceeded verified emissions); Swiss hubs from 2020; event study shows no clear effect before 2018
- Inference: SE clustered by route; number of clusters not reported
- Headline: Table 3: -0.041 (SE 0.002), Asia -0.051, North America -0.032; 2010-2019 only -0.027 (Table 4). Table 5: hub competition -0.038 vs no hub competition -0.060 (Asia -0.0544 vs -0.0664; North America -0.0241 vs -0.0592). Dummy version (Table 7): -0.114, JV interaction +0.106. Authors: effect relevant only when prices are high (sec. 5)
- Transfer, hub, centrality: Yes: connecting passengers by hub; carbon leakage to non-EEA hubs. No centrality measure
- Lesson for our design: Closest template for our ETS design; but the common EUA series means any EEA-specific shock correlated with the price (2018 onward, Brexit, COVID, 2022) loads on the coefficient; test price nonlinearity

**E03. Fageda, X.; Oesingmann, K. (2025).** The impact of carbon pricing on tourist destinations: Shifts in demand, supply and emissions in the European aviation market. *Economics of Transportation*, 42, 100414. DOI 10.1016/j.ecotra.2025.100414. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: Open access PDF (UB repository): sec. 1-6.1, Tables 1-3
- Policy: EU ETS (2013 treatment)
- Countries: 635 EEA/UK origin cities to 114 tourist destinations (68 treated; 46 controls in Turkey, North Africa, Middle East, Cape Verde, outermost regions, Turkish Cyprus)
- Period: 2010-2022
- Data: Sabre O-D passengers incl. connecting; RDC supply; Eurocontrol SET for CO2
- Unit: City pair
- Frequency: Annual
- Outcomes: Passengers, supply, CO2
- Identification: DiD with route and year FE; entropy balancing on income and origin population; event study (base 2012)
- Control group: Untaxed tourist destinations outside the ETS scope
- Displacement: Robustness with EEA-only or non-EEA-only controls; authors flag possible leakage to nearby non-EEA destinations
- Timing and anticipation: Treatment 2013; outermost-region exemption restricted from 2024
- Inference: SE clustered by route; route counts reported
- Headline: Passengers, matched (Table 2 col. 2): -0.0265 (SE 0.0231, n.s.); unmatched (col. 5): +0.110; ln CO2 on non-stop routes (Table 3 col. 4): -0.0745 (SE 0.0328)
- Transfer, hub, centrality: No
- Lesson for our design: Use the 2024 outermost-region scope change; analyse seats and passengers separately

**E04. Albert, J.-F.; Gomez-Fernandez, N.; Boto-Garcia, D. (2025).** Up in the air: How do carbon policy shocks affect air travel?. *Transport Policy*, 168, 54-68. DOI 10.1016/j.tranpol.2025.04.003. Check: refcheck partial_match 0.9; Crossref.
- Status: VERIFIED (sec. 1-5.2, Table 2; flights subsection and conclusion cut off)
- Read: ScienceDirect open page
- Policy: EU ETS carbon policy shocks
- Countries: EU aggregate; Germany, UK, France, Italy, Spain
- Period: 2005-2019
- Data: Eurostat passengers carried and flights (domestic, intra-EU, extra-EU); HICP, HICP air, industrial production, Brent, GHG, yields; X-13 seasonal adjustment
- Unit: EU / country aggregate
- Frequency: Monthly
- Outcomes: Passengers, flights, air fares (HICP air)
- Identification: Proxy SVAR instrumented with the Kaenzig (2023) carbon policy surprise series, 2 lags; shock normalised to a 1% rise in HICP energy
- Control group: None (time series); authors critique binary DiD for SUTVA problems and for ignoring variation in allowance costs
- Displacement: None
- Timing and anticipation: Sample starts 2005 to capture anticipation; subsamples 2007-19 and 2012-19
- Inference: 68% bands from 10,000 bootstrap replications
- Headline: HICP air +5% or more on impact (significant for 10 months); domestic passengers down up to 1.2% (significant 15 months); intra-EU passengers fall in months 5-10; extra-EU passengers no significant response; Germany domestic peak about -4%; UK no response
- Transfer, hub, centrality: No
- Lesson for our design: Kaenzig surprises can serve as an external instrument for the EUA price in an EEA-exposure x price design; report 90/95% bands

**E05. Kang, Y.; Liao, S.; Jiang, C.; D'Alfonso, T. (2022).** Synthetic control methods for policy analysis: Evaluating the effect of the European Emission Trading System on aviation supply. *Transportation Research Part A: Policy and Practice*, 162, 236-252. DOI 10.1016/j.tra.2022.05.015. Check: refcheck partial_match 0.9; Crossref.
- Status: PARTIAL
- Read: Abstract, introduction, snippets (repository copy blocked)
- Policy: EU ETS
- Countries: 48 countries (31 regulated)
- Period: 2007-2017; treatment year 2012
- Data: OAG
- Unit: Carrier x route (315,193 routes; 793,188 observations)
- Frequency: Annual
- Outcomes: Seat capacity; aircraft size
- Identification: Route-level synthetic control with a modified weighting justification and stochastic approximation
- Control group: not read
- Displacement: not read
- Timing and anticipation: Treatment 2012
- Inference: not read
- Headline: Seat capacity falls by more than 20% at peak; no effect on aircraft size; larger effects for LCC and regional airlines, short haul, spoke-spoke and monopoly routes (abstract)
- Transfer, hub, centrality: Hub vs non-hub routes only
- Lesson for our design: Synthetic control on OAG seats is accepted for the ETS; expect heterogeneity by hub status

**E06. Zhang, R.; Shen, H.; Luo, L.; Zhao, Y. (2026).** International unilateral climate policies and carbon leakage: Evidence from airline routes. *Energy Economics*, 157, 109279. DOI 10.1016/j.eneco.2026.109279. Check: refcheck partial_match 0.9; Crossref.
- Status: PARTIAL
- Read: Abstract, highlights, introduction, snippets
- Policy: EU ETS applied to Chinese airlines' routes in ETS jurisdiction
- Countries: China-EU routes vs Chinese domestic routes
- Period: 2011Q1-2019Q4
- Data: OAG (multi-stop excluded)
- Unit: Route
- Frequency: Quarterly
- Outcomes: CO2, frequency, passengers
- Identification: PSM-DID
- Control group: not read
- Displacement: Leakage measured as reallocation to the same airlines' domestic routes
- Timing and anticipation: not read
- Inference: not read
- Headline: -12.25% on regulated routes and +3.61% on domestic routes; channels frequency and passengers; leakage stronger for non-alliance airlines and non-monopoly routes (abstract)
- Transfer, hub, centrality: None seen
- Lesson for our design: Published in our target journal: leakage framed as within-carrier capacity reallocation; we must cite and differentiate (airport network vs carrier routes)

**E07. Zhang, Y.; Wang, K. (2024).** Mitigation effect of the European Union emission trading system on aviation emissions. *Transportation Research Part D: Transport and Environment*, 130, 104186. DOI 10.1016/j.trd.2024.104186. Check: refcheck partial_match 0.9; Crossref.
- Status: PARTIAL
- Read: Abstract
- Policy: EU ETS (2013 regime)
- Countries: 60 countries
- Period: 2000-2019
- Data: not read
- Unit: Country
- Frequency: Annual
- Outcomes: Aviation CO2 (total, domestic, international)
- Identification: National panel DiD
- Control group: not read
- Displacement: not read
- Timing and anticipation: 2013 regime as quasi-experiment
- Inference: not read
- Headline: -690 kt total aviation CO2 and -401 kt domestic; no effect on international CO2 (abstract)
- Transfer, hub, centrality: No
- Lesson for our design: Country-level aggregates hide network reallocation

**E08. Dray, L.; Doyme, K. (2019).** Carbon leakage in aviation policy. *Climate Policy*, 19(10), 1284-1296. DOI 10.1080/14693062.2019.1668745. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: UCL accepted manuscript; Table 2 re-checked by the compiler
- Policy: Hypothetical UK-only carbon price on departing flights (USD 15-300/tCO2), biofuel mandates (5-40%), landing charges
- Countries: UK in the 2015 global system
- Period: Static 2015
- Data: AIM model with Sabre 2017 demand, schedules, routing, fares; 878 cities; 20,000 city pairs touching the UK
- Unit: City pair / itinerary
- Frequency: Static
- Outcomes: Passengers by routing (incl. transfers via UK and non-UK hubs); CO2 leakage
- Identification: Simulation; multinomial logit itinerary choice (fare, time, frequency, legs, airport size); price elasticity -0.2 to -0.8; pass-through 0/50/100%
- Control group: Not applicable
- Displacement: Leakage = CO2 change outside policy area / change inside, three scope definitions
- Timing and anticipation: Static
- Inference: Ranges over parameters
- Headline: At USD 300/tCO2, elasticity -0.2, full pass-through (Table 2): international-to-international transfers via UK hubs -0.64 million a year (base 8.7 million), via non-UK hubs +0.31 million (base 37.4 million); carbon-pricing leakage ranges +50% to -150% (abstract)
- Transfer, hub, centrality: Yes: only study found that links carbon pricing to transfer passengers switching to foreign hubs (simulation)
- Lesson for our design: Testable prediction: hub switching is concentrated in international-to-international transfers and is smaller than demand suppression

**E09. Wei, T.; Kallbekken, S. (2024).** Carbon leakage from aviation under the European Union Fit for 55 policies. *Transportation Research Part D: Transport and Environment*, 132, 104269. DOI 10.1016/j.trd.2024.104269. Check: refcheck verified; Crossref.
- Status: VERIFIED (sec. 1-4.3)
- Read: ScienceDirect open page
- Policy: ReFuelEU, Energy Taxation Directive, end of free allocation (2026)
- Countries: EU and rest of world
- Period: 2015-2050
- Data: AIM (878 cities, 1,169 airports, 40,265 segments) and GRACE CGE (GTAP v10); assumed EUA path EUR 130 (2030), 175 (2035), 315 (2050)
- Unit: Segments; regions
- Frequency: Scenario years
- Outcomes: Fares, RPK, CO2 leakage
- Identification: Linked simulation (sectoral plus CGE)
- Control group: Not applicable
- Displacement: Itinerary choice inside AIM; hub output not reported
- Timing and anticipation: Scenario
- Inference: None
- Headline: Intra-EU fares +15% and RPK -13% by 2050; EU-to-rest-of-world RPK -3%; aviation leakage small and negative (RPK component -3% in 2025 to -0.5% in 2050); GRACE economy-wide leakage about 33%, aviation outside the EU about 10% falling to about 5% by 2050
- Transfer, hub, centrality: Introduction notes Commission assessments mention 'hub switching' without quantifying it
- Lesson for our design: Our ex-post centrality evidence tests the hub-switching channel that simulations leave unquantified

**E10. Scheelhaase, J.; Grimme, W.; Maertens, S. (2024).** EU trilogue results for the aviation sector: key issues and expected impacts. *Transportation Research Procedia*, 78, 206-214. DOI 10.1016/j.trpro.2024.02.027. Check: refcheck partial_match 0.9; Crossref; Directive (EU) 2023/958 checked on EUR-Lex.
- Status: VERIFIED
- Read: DLR elib PDF; EUR-Lex full text of Directive (EU) 2023/958
- Policy: 2023 ETS aviation reform (Directive (EU) 2023/958), ReFuelEU
- Countries: EEA
- Period: 2024-2030 rules
- Data: Legal texts
- Unit: Not applicable
- Frequency: Not applicable
- Outcomes: Rule changes
- Identification: Descriptive policy analysis
- Control group: Not applicable
- Displacement: Not applicable
- Timing and anticipation: Free allocation cut 25% (2024), 50% (2025), none from 2026; extra-EEA derogation to 31 Dec 2026 with possible 2027 extension; outermost-region flights covered except domestic
- Inference: None
- Headline: Linear reduction factor 4.3% (2024-27) and 4.4% (2028-30); 20 million SAF allowances; non-CO2 MRV from 2025; SAF mandate 2% (2025) to 70% (2050) with a 90% refuelling obligation (Table 1)
- Transfer, hub, centrality: Secondhand only (grey literature: Oxera 2022, SEO and NLR 2022), not verified
- Lesson for our design: Our data see only the 2024 step of the reform; since free allowances carry the same opportunity cost (argument in Fageda and Teixido 2022), use a price-based treatment rather than a reform dummy

**H01. Khordagui, N. (2025).** Airline Mergers and Airport Connectivity. *SSRN working paper (version 1 Sep 2025, 58 pp.; not peer reviewed)*. DOI 10.2139/ssrn.5480222. Check: refcheck verified (Crossref).
- Status: VERIFIED
- Read: Full PDF: sec. 1-7, Tables 1, 2, 4, 5, 13
- Policy: Five US airline mergers (2005, 2008, 2010, 2011, 2013)
- Countries: US domestic network
- Period: 2000-2019
- Data: DB1B Coupon (10% ticket sample); county population; real weekly wage; FAA hub size
- Unit: Airport (29,027 airport-quarters)
- Frequency: Quarterly
- Outcomes: Degree, closeness, eigenvector, betweenness centrality, unweighted and passenger-weighted (directed network, largest connected component; no time-feasibility or MCT screen)
- Identification: Synthetic DiD (Arkhangelsky et al. 2021) with airport and year-quarter effects, estimated merger by merger; 8 pre-quarters, short run 8 and long run 20 quarters; merger quarter dropped
- Control group: Airports where neither merging airline had over 10% passenger share; controls that later exceed 10% are dropped
- Displacement: No discussion of network spillovers onto controls seen
- Timing and anticipation: One date per merger; announcement and single-code dates marked in plots
- Inference: Block bootstrap; placebo variance when treated group is small; placebo test with 1,000 random assignments
- Headline: Northwest-Delta long run (Table 13, % of treated pre-merger mean): degree -7.33%, closeness -0.82%, eigenvector -5.21%, betweenness -27.62%, weighted betweenness -20.84% (text sec. 5.2.2 says 28.84%). Continental-United long run (Table 4): closeness +1.10%, weighted eigenvector +4.00%. America West-US Airways: no significant long-run effects
- Transfer, hub, centrality: Yes, centrality as outcome; no taxes or carbon pricing
- Lesson for our design: Best causal template for centrality outcomes: presence-based treatment, drop later-treated controls, effects as % of pre-mean, weighted and unweighted side by side, permutation placebo; betweenness is volatile, so use logs or ranks and annual data

**H02. Ciliberto, F.; Cook, E.E.; Williams, J.W. (2019).** Network Structure and Consolidation in the U.S. Airline Industry, 1990-2015. *Review of Industrial Organization*, 54(1), 3-36 (online 2018). DOI 10.1007/s11151-018-9635-y. Check: refcheck verified; Crossref.
- Status: VERIFIED
- Read: Springer HTML: sec. 2.2, 3, 5, 6, Table 8 note
- Policy: Five US mergers plus codeshare agreements
- Countries: US domestic network
- Period: 1990-2015
- Data: BTS T-100 Domestic Segment; national any-carrier network; GDP, jet fuel price, MSA income and population
- Unit: Airport (190 airports; 53,324 airport-months)
- Frequency: Monthly
- Outcomes: Unweighted degree, closeness, betweenness (standardised); 'lies on a shortest path' dummy
- Identification: Before-after windows around each event with airport-by-merger FE, airport-specific linear trends, quarter dummies; pooled and merger by merger
- Control group: None (within-airport identification)
- Displacement: National-network measures by construction
- Timing and anticipation: Completion month; appendix uses announcement and single-code months
- Inference: Stars only; SE type and clustering not stated in parts read
- Headline: Pooled merger effect (Table 8): degree -0.00493 SD, closeness -0.0024 SD, betweenness -0.00121 SD, all insignificant; Delta-Northwest raised closeness by about 0.0588 SD; US Airways-America West lowered degree by about 0.0389 SD
- Transfer, hub, centrality: Yes (topology); no taxes
- Lesson for our design: Without a control group and with unweighted any-carrier topology, effects are near zero; use seat weights, a real control group, and the extensive-margin 'is between' indicator

**H03. Bernardo, V.; Fageda, X. (2017).** The effects of the Morocco-European Union open skies agreement: A difference-in-differences analysis. *Transportation Research Part E: Logistics and Transportation Review*, 98, 24-41. DOI 10.1016/j.tre.2016.11.009. Check: refcheck partial_match; Crossref.
- Status: VERIFIED
- Read: Accepted manuscript (UB repository)
- Policy: EU-Morocco open skies agreement (signed December 2006)
- Countries: North Africa to EU-15, Norway, Switzerland
- Period: 2003-2010
- Data: RDC Aviation capstats seats
- Unit: Airport pair (191 existing routes, 1,501 obs.; 3,895 potential routes, 31,160 obs.)
- Frequency: Annual
- Outcomes: Seats; whether a route is served
- Identification: Route-level DiD with route FE (preferred) or pooled; pre-trend evidence; matching robustness; IV for HHI
- Control group: Routes from other North African countries to the same European countries
- Displacement: No discussion of diversion between Morocco and control countries seen
- Timing and anticipation: Single date
- Inference: Robust SE clustered by route (pooled model with AR(1))
- Headline: Seats on treated routes about 24% higher than on control routes (route FE, Table 4); odds of a route being served 1.5 to 3.5 times higher (Table 5)
- Transfer, hub, centrality: No
- Lesson for our design: Route-level DiD template from the same research group; neighbouring countries are where displaced traffic goes, so treat them as an exposure group

**H04. Allroggen, F.; Wittman, M.D.; Malina, R. (2015).** How air transport connects the world: A new metric of air connectivity and its evolution between 1990 and 2012. *Transportation Research Part E: Logistics and Transportation Review*, 80, 184-201. DOI 10.1016/j.tre.2015.06.001. Check: refcheck verified; Crossref.
- Status: VERIFIED (working-paper version)
- Read: MIT ICAT Report ICAT-2015-01 (March 2015); published version not read
- Policy: None (index construction)
- Countries: World
- Period: 1990-2012
- Data: OAG schedules (December loads 1990-1998, January loads 1999-2012); LandScan population; GDP per capita; DB1B Q2-2011 detour percentiles
- Unit: Airport
- Frequency: Annual
- Outcomes: Global Connectivity Index (GCI) and Global Hub Centrality Index (GHCI)
- Identification: Index: sum over nonstop and one-stop routings of directness x days operated x destination quality; one-stop needs layover of at least 30 min and same airline or codeshare; directness zero beyond the 95th percentile detour; GHCI sums one-stop routings transferring at the airport; destination-invariant variant reported
- Control group: Not applicable
- Displacement: Not applicable
- Timing and anticipation: Annual
- Inference: None
- Headline: Global one-stop connectivity grew about 3.5 times faster than nonstop; Asian hub centrality more than quintupled 2000-2012, with UAE and Qatar airports 14.7% and Turkish airports 8.6% of Asian GHCI growth; Dubai's share of one-stop connectivity from South and South-East Asian origins rose from 1.2% (rank 18) in 2000 to 7.6% (rank 2) in 2012 (Table 7)
- Transfer, hub, centrality: Yes (hub centrality metric); no taxes
- Lesson for our design: Blueprint for a time-feasible airport-year hub centrality from OAG; use the destination-invariant variant so GDP shocks do not load into the outcome

**H05. Suau-Sanchez, P.; Voltes-Dorta, A.; Rodriguez-Deniz, H. (2016).** The role of London airports in providing connectivity for the UK: regional dependence on foreign hubs. *Journal of Transport Geography*, 50, 94-104 (online 2014). DOI 10.1016/j.jtrangeo.2014.11.008. Check: refcheck partial_match; Crossref.
- Status: VERIFIED
- Read: Accepted manuscript (Cranfield CERES); Table 6 re-checked by the compiler
- Policy: None (APD mentioned only as a policy option, footnote 14)
- Countries: UK and European network
- Period: May 2013 (destinations 2004-2013)
- Data: OAG Traffic Analyser MIDT bookings (adjusted for LCC direct sales), itineraries with up to two connections: 489,573 itineraries, 66.9 million passengers, 2,158 airports
- Unit: Airport; market
- Frequency: Single month
- Outcomes: Flow betweenness (connecting passengers at i over passengers not originating or terminating at i); share of all connecting passengers; connecting rate
- Identification: Descriptive cross-section
- Control group: None
- Displacement: None
- Timing and anticipation: Single month
- Inference: None
- Headline: UK-international markets: Dubai handles 10.0% of connecting passengers, Amsterdam 9.9%, Heathrow 8.1% (Table 4); regional UK to Asia-Pacific: Dubai 39.5% (Table 6); non-UK hubs handle 63-85% of long-haul transfer passengers (sec. 3.2); destinations served 2004-2013: Istanbul +105.3%, Dubai +58.3%, Heathrow -6.9% (Table 2)
- Transfer, hub, centrality: Yes (flow betweenness)
- Lesson for our design: Regional demand already leaks to Amsterdam, Dubai and Istanbul; OAG betweenness is the supply-side proxy for this MIDT flow betweenness

**H06. Piltz, C.; Voltes-Dorta, A.; Suau-Sanchez, P. (2018).** A comparative analysis of hub connections of European and Asian airports against Middle Eastern hubs in intercontinental markets. *Journal of Air Transport Management*, 66, 1-12. DOI 10.1016/j.jairtraman.2017.09.006. Check: refcheck partial_match; Crossref.
- Status: VERIFIED
- Read: Accepted manuscript (Cranfield CERES); Table 5 re-checked by the compiler
- Policy: None
- Countries: Eastern US to South Asia and to South East Asia
- Period: June 2012 vs June 2016
- Data: MIDT average weeks (June 2012, June 2016); OAG schedules first week of June 2016 (697,411 departures); OAG Connections Analyser MCTs
- Unit: Hub x market
- Frequency: Two snapshots
- Outcomes: Each hub's share of connecting passengers in a market; connection quality (MCT, maximum connecting time 1 hour above best weekly connection)
- Identification: Descriptive two-period comparison; authors state no counterfactual to separate new demand from diversion
- Control group: None
- Displacement: None
- Timing and anticipation: 2012 vs 2016
- Inference: None
- Headline: Eastern US-South Asia: EEA hubs' share of connections 52.9% to 22.4%, Middle East 32.4% to 62.3%, non-EEA Europe 2.5% to 3.7% (Table 5); Eastern US-South East Asia: Middle East 4.8% to 20.8%, EEA 12.5% to 3.6%
- Transfer, hub, centrality: Yes; no taxes
- Lesson for our design: Measure relocation as the market-level share of one-stop flows (or feasible one-stop seats) via EEA hubs, Istanbul and Gulf hubs; split Europe into EEA and non-EEA

**H07. O'Connell, J.F.; Escofet Bueno, O. (2018).** A study into the hub performance Emirates, Etihad Airways and Qatar Airways and their competitive position against the major European hubbing airlines. *Journal of Air Transport Management*, 69, 257-268. DOI 10.1016/j.jairtraman.2016.11.006. Check: refcheck partial_match; Crossref.
- Status: VERIFIED
- Read: Accepted manuscript (Cranfield CERES)
- Policy: None
- Countries: EK, EY, QR vs LH, KL, AF, BA
- Period: Thursday 12 June 2014
- Data: OAG schedules: over 3,700 flights, 295 airports, over 280,000 indirect airport pairs; same-airline connections only
- Unit: Airline hub
- Frequency: One day
- Outcomes: Danesi weighted connectivity ratio (time score with MCT and 240-min intercontinental maximum; detour score up to 1.50) vs random schedule
- Identification: Descriptive
- Control group: None
- Displacement: None
- Timing and anticipation: One day
- Inference: None
- Headline: Weighted connectivity ratio: Etihad 2.31 (1,555.75 weighted connections vs 672.36 under a random schedule), Qatar 2.17, Air France 1.44, BA 1.13 (sec. 4.1, Table 3)
- Transfer, hub, centrality: Yes (wave quality); no taxes
- Lesson for our design: Hub function also reflects schedule coordination; time-feasible, detour-limited connection counts capture what topology misses

**H08. Logothetis, M.; Miyoshi, C. (2018).** Network performance and competitive impact of the single hub: A case study on Turkish Airlines and Emirates. *Journal of Air Transport Management*, 69, 215-223. DOI 10.1016/j.jairtraman.2016.10.003. Check: refcheck partial_match; Crossref.
- Status: VERIFIED
- Read: Accepted manuscript (Cranfield CERES)
- Policy: None
- Countries: Turkish Airlines at Istanbul Ataturk; Emirates at Dubai
- Period: July 2007, 2014, 2016 (TK); 2008, 2014, 2016 (EK)
- Data: OAG schedules; OAG MCT; maximum connecting time 3 x MCT
- Unit: Airline hub
- Frequency: Snapshots
- Outcomes: Hub connectivity performance index (connections weighted by routing, time, seats, widebody, frequency); hub efficiency = HCPI / viable connections
- Identification: Descriptive
- Control group: None
- Displacement: None
- Timing and anticipation: Snapshots
- Inference: None
- Headline: 2014: Turkish 103,368 effective weekly connections vs Emirates 29,507; hub efficiency Turkish 68.6% vs Emirates 76.7%; Turkish grew from 19,230 (2007) to 103,368 (2014) effective connections (sec. 4.1, 4.3)
- Transfer, hub, centrality: Yes; no taxes
- Lesson for our design: Istanbul's scale rests on high-frequency short-haul feed, Gulf hubs on long-haul quality: test displacement to Istanbul and to the Gulf separately

## 4. Secondary studies (peripheral, ex-ante, or abstract only)

| ID | Study | Venue | Status | Design | Headline | Note for our design |
|---|---|---|---|---|---|---|
| C01 | Lorner, J.; Jedvik, S. (2026). Flying under the radar? A synthetic control study on the Norwegian aviation tax's effect on international departing passengers from Oslo's airport | Bachelor thesis, Department of Economics, Uppsala University (DiVA urn:nbn:se:uu:diva-594338); https://uu.diva-portal.org/smash/get/diva2:2087414/FULLTEXT01.pdf | VERIFIED (low weight, student thesis) | Synthetic control on Oslo Gardermoen, quarterly 2010Q1-2019Q4, 12 donor capitals (Tallinn 0.252, Helsinki 0.189, Copenhagen 0.185, Brussels 0.147, Warsaw 0.141, Bern 0.086); tax NOK 80 from 1 June 2016, transfers exempt | Average gap -76,547 international departing passengers (about 0.27%), not significant; in-space placebo p = 0.333 | Single-airport SCM with about 12 donors cannot reach p below about 0.08; Copenhagen is a donor although it is the obvious leakage destination |
| C02 | Warras, E. (2020). Do the aviation taxes in Norway and Sweden decrease passenger numbers | Thesis (Doria repository, handle 10024/177518; degree level not confirmed); https://www.doria.fi/handle/10024/177518 | PARTIAL (abstract) | Dynamic DiD on 129 airports, 2011-2019 | No significant effect on total passengers; domestic travel falls by over 10% from Swedish airports with LCC presence and by 24% in Norway (abstract) | Separate domestic, intra-European and long-haul seats |
| C03 | Forsyth, P.; Dwyer, L.; Spurr, R.; Pham, T. (2014). The impacts of Australia's departure tax: Tourism versus the economy? | Tourism Management 40, 126-136; 10.1016/j.tourman.2013.05.011 | PARTIAL | Ex-ante CGE; Passenger Movement Charge AUD 47 to 55 from 1 July 2012; elasticities -0.5 and -1.0 | Tourism loses, economy gains (GNI, welfare) because foreign visitors pay part of the tax (abstract; numbers not read) | Remote market with no nearby untaxed airports: displacement depends on proximity to untaxed hubs |
| C04 | Liu, S.; Wan, Y.; Ha, H.-K.; Yoshida, Y.; Zhang, A. (2019). Impact of high-speed rail network development on airport traffic and traffic distribution: Evidence from China and Japan | Transportation Research Part A: Policy and Practice 127, 115-135; 10.1016/j.tra.2019.07.015 | VERIFIED | Airport FE panel, 46 Chinese and 16 Japanese airports, 2007-2015; HSR degree and harmonic centrality as continuous treatment interacted with air-HSR link dummy | China, total passengers (Table 5): net HSR degree-centrality effect -0.028 (SE 0.012) without air-HSR link, +0.041 (SE 0.020) with link; international with link +0.048 (SE 0.007) | Centrality used as treatment, not outcome; same shock can raise hub and lower non-hub traffic, so include hub-status interactions |
| C05 | Sun, X.; Wandelt, S.; Zhang, A. (2020). How did COVID-19 impact air transportation? A first peek through the lens of complex networks | Journal of Air Transport Management 89, 101928; 10.1016/j.jairtraman.2020.101928 | VERIFIED | Descriptive daily networks (Flightradar24, 2,751 airports, 16 Dec 2019 to 15 May 2020); degree, betweenness, assortativity | Average airport degree fell from about 6 to 3; served OD pairs from about 80,000 to about 20,000 within about two weeks (sec. 2.1); betweenness swung by up to an order of magnitude within a week | Unweighted high-frequency betweenness is unstable; use annual seat-weighted measures and treat 2020-21 separately |
| C06 | Tolcha, T.D.; Tchouamou Njoya, E.; Brathen, S.; Holmgren, J. (2021). Effects of African aviation liberalisation on economic freedom, air connectivity and related economic consequences | Transport Policy 110, 204-214; 10.1016/j.tranpol.2021.06.002 | VERIFIED | PLS-SEM, 52 African countries, 2011-2019 | Path liberalisation to connectivity 0.914 (p = 0.000), adjusted R2 0.83 (Table 2) | Cautionary: treatment index partly built from network outputs; never build treatment intensity from network outcomes |
| C07 | Scheelhaase, J.; Grimme, W.; Schaefer, M. (2010). The inclusion of aviation into the EU emission trading scheme: Impacts on competition between European and non-European network airlines | Transportation Research Part D 15(1), 14-25; 10.1016/j.trd.2009.07.003 | PARTIAL | Ex-ante cost model under full scope, Lufthansa vs Continental, EUR 20/t | About 60% of Lufthansa's long-haul passengers are transfer passengers; Continental gets a larger free share and an advantage on long haul (abstract) | Early statement of the competitive-distortion hypothesis for EU vs non-EU hub carriers |
| C08 | Albers, S.; Buehne, J.-A.; Peters, H. (2009). Will the EU-ETS instigate airline network reconfigurations? | Journal of Air Transport Management 15(1), 1-6; 10.1016/j.jairtraman.2008.09.013 | PARTIAL | OAG-based route cost simulation at EUR 20/t | EUR 9-27 per route, judged too small alone to trigger network reconfiguration; Newark-Delhi via Frankfurt costs EUR 26.79 more per passenger (abstract and preview) | Ex-ante hub-relocation argument; low prices imply small effects, consistent with effects appearing only after 2018 |
| C09 | Malina, R.; McConnachie, D.; Winchester, N.; Wollersheim, C.; Paltsev, S.; Waitz, I.A. (2012). The impact of the European Union Emissions Trading Scheme on US aviation | Journal of Air Transport Management 19, 36-41; 10.1016/j.jairtraman.2011.12.004 | PARTIAL | Ex-ante cost simulation 2012-2020 | Small effects; windfall gains, US carriers would buy only about a third of their allowances (abstract) | Background for full-scope (2012) period |
| C10 | Anger, A. (2010). Including aviation in the European emissions trading scheme: Impacts on the industry, CO2 emissions and macroeconomic activity in the EU | Journal of Air Transport Management 16(2), 100-105; 10.1016/j.jairtraman.2009.10.009 | PARTIAL | E3ME macro simulation | Small macro effects; aviation CO2 down up to 7.4%, mainly through supply (abstract) | Background |
| C11 | Meleo, L.; Nava, C.R.; Pozzi, C. (2016). Aviation and the costs of the European Emission Trading Scheme: The case of Italy | Energy Policy 88, 138-147; 10.1016/j.enpol.2015.10.008 | PARTIAL | Accounting of direct ETS costs of Italian airlines 2012-14 plus scenarios 2015-16 | Not causal; cost figures not extracted | Background on actual compliance costs |
| C12 | Derigs, U.; Illing, S. (2013). Does EU ETS instigate Air Cargo network reconfiguration? A model-based analysis | European Journal of Operational Research 225(3), 518-527; 10.1016/j.ejor.2012.10.016 | PARTIAL | Cargo network optimisation under ETS scenarios | Numbers not read | Background (cargo) |
| C13 | Scheelhaase, J.; Maertens, S.; Grimme, W.; Jung, M. (2018). EU ETS versus CORSIA: A critical assessment of two approaches to limit air transport's CO2 emissions by market-based measures | Journal of Air Transport Management 67, 55-62; 10.1016/j.jairtraman.2017.11.007 | PARTIAL | Policy assessment | Recommends keeping the reduced scope plus CORSIA (abstract) | Background on scope |
| C14 | Vespermann, J.; Wald, A.; Gleich, R. (2008). Aviation growth in the Middle East: impacts on incumbent players and potential strategic reactions | Journal of Transport Geography 16(6), 388-394; 10.1016/j.jtrangeo.2008.04.009 | PARTIAL | Descriptive/strategic | Gulf carriers aim to redirect Europe/Americas-Asia flows; in some markets they are disadvantaged on flight time (abstract) | Background on Gulf hub competition |
| C15 | Grimme, W. (2011). The growth of Arabian airlines from a German perspective: A study of the impacts of new air services to Asia | Journal of Air Transport Management 17(6), 333-338; 10.1016/j.jairtraman.2011.02.002 | PARTIAL | Descriptive, German statistics for Duesseldorf and Hamburg to Asia | Emirates entry stimulated demand; incumbent hubs did not lose transfer passengers (abstract) | A fall in an EU hub's centrality need not mean passengers moved |
| C16 | O'Connell, J.F. (2011). The rise of the Arabian Gulf carriers: An insight into the business model of Emirates Airline | Journal of Air Transport Management 17(6), 339-346; 10.1016/j.jairtraman.2011.02.003 | PARTIAL | Business-model case study | Not applicable | Background |
| C17 | Redondi, R.; Malighetti, P.; Paleari, S. (2011). Hub competition and travel times in the world-wide airport network | Journal of Transport Geography 19(6), 1260-1271; 10.1016/j.jtrangeo.2010.11.010 | PARTIAL | Minimum travel times, 232 airports, 2008 | European hubs have a geographic advantage; hubs on different continents compete for the same OD markets (abstract) | Supports a global network (not Europe-only) as the outcome space |
| C18 | Burghouwt, G.; Redondi, R. (2013). Connectivity in Air Transport Networks: An Assessment of Models and Applications | Journal of Transport Economics and Policy 47(1), 35-53; 10.3828/jtep.2013.47.1.35 | PARTIAL | Comparison of eight connectivity models | Size-based measures overstate the centrality of large airports (abstract) | Report weighted and unweighted centrality; justify the chosen measure |

## 5. Methods: what each paper solves, when to use it, and the software

Package availability was checked on 2026-10-02 against the SSC archive and CRAN. Abstract-level reading unless stated.

| ID | Paper | Problem solved | When to use it here | Stata / R |
|---|---|---|---|---|
| M01 | Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. Journal of Econometrics 225(2), 254-277. 10.1016/j.jeconom.2021.03.014 | TWFE DiD with staggered timing is a weighted average of all 2x2 DiDs, including already-treated units as controls; biased when effects change over time | Diagnostic for any TWFE that pools DE/AT 2011, NO 2016, SE 2018, FR 2020 | Stata bacondecomp (SSC); R bacondecomp (CRAN) |
| M02 | Callaway, B.; Sant'Anna, P.H.C. (2021). Difference-in-Differences with multiple time periods. Journal of Econometrics 225(2), 200-230. 10.1016/j.jeconom.2020.12.001 | Group-time ATTs with staggered adoption and conditional parallel trends; OR, IPW and doubly robust estimands; aggregation; bootstrap for simultaneous inference | Main estimator for binary staggered tax adoption with never-treated or not-yet-treated airports (precedent: Bernardo et al. 2024); reversible taxes need separate handling | Stata csdid, drdid (SSC); R did (CRAN) |
| M03 | Sun, L.; Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. Journal of Econometrics 225(2), 175-199. 10.1016/j.jeconom.2020.09.006 | Lead/lag coefficients in TWFE event studies are contaminated by other periods' effects; interaction-weighted estimator | Event-study plots for ticket taxes, robustness to M02/M07 | Stata eventstudyinteract (SSC); R fixest sunab() (CRAN) |
| M04 | de Chaisemartin, C.; D'Haultfoeuille, X. (2020). Two-Way Fixed Effects Estimators with Heterogeneous Treatment Effects. American Economic Review 110(9), 2964-2996. 10.1257/aer.20181169 | TWFE weights on group-period ATEs can be negative; alternative estimator allowing switching in and out | Quantify negative weights in our TWFE | Stata did_multiplegt, did_multiplegt_old (SSC); R DIDmultiplegt (CRAN) |
| M05 | de Chaisemartin, C.; D'Haultfoeuille, X. (2026 (issue); WP 2020-22). Difference-in-Differences Estimators of Intertemporal Treatment Effects. Review of Economics and Statistics 108(4), 863-880. 10.1162/rest_a_01414 | Event-study estimators for non-binary, non-absorbing treatments with lagged effects; TWFE and local-projection versions can be biased | Best fit for ticket taxes as they happened: on/off (NL 2008-09, IE 2009-14, MT), rate changes (DE, UK APD), tax in EUR per passenger | Stata did_multiplegt_dyn (SSC); R DIDmultiplegtDYN (CRAN) |
| M06 | de Chaisemartin, C.; D'Haultfoeuille, X.; Pasquier, F.; Sow, D.; Vazquez-Bare, G. (2022-2026 (WP)). Difference-in-Differences Estimators for Treatments Continuously Distributed at Every Period (earlier: DiD for Continuous Treatments and Instruments with Stayers). arXiv 2201.06898 v7 (July 2026); SSRN. 10.2139/ssrn.4011782 | Continuous treatments (taxes, prices) with switchers and stayers; slopes identified comparing switchers and stayers with the same baseline treatment; doubly robust estimators; IV extension; gasoline-tax application | Continuous tax levels; ETS exposure dose with non-EEA stayers at zero | Stata did_multiplegt_stat (SSC); related no-stayer design: did_had (SSC), DIDHAD (CRAN) |
| M07 | Borusyak, K.; Jaravel, X.; Spiess, J. (2024). Revisiting Event-Study Designs: Robust and Efficient Estimation. Review of Economic Studies 91(6), 3253-3285. 10.1093/restud/rdae007 | Efficient imputation estimator under heterogeneous effects; tests of identifying assumptions; time-varying controls, triple differences, some non-binary treatments | Many never-treated airports worldwide and monthly seats make imputation efficient; triple difference by route type or distance band | Stata did_imputation (SSC); R didimputation (CRAN); Gardner two-stage did2s (SSC, CRAN) |
| M08 | Wooldridge, J.M. (2025). Two-way fixed effects, the two-way mundlak regression, and difference-in-differences estimators. Empirical Economics 69(5), 2545-2587. 10.1007/s00181-025-02807-z | Extended TWFE (cohort x period interactions) equals pooled OLS with cohort and period dummies and an imputation estimator; allows heterogeneity and cohort trends | Regression-based alternative; easy to add controls and Poisson for seat counts | Stata jwdid (SSC); R etwfe (CRAN) |
| M09 | Cengiz, D.; Dube, A.; Lindner, A.; Zipperer, B. (2019). The Effect of Minimum Wages on Low-Wage Jobs. Quarterly Journal of Economics 134(3), 1405-1454. 10.1093/qje/qjz014 | Stacked event-by-event datasets with clean controls (no policy change within the event window) avoid negative weighting; state clustering; Ferman-Pinto intervals for single events | One stack per tax event; clean controls = airports in countries with no tax change in the window; natural place to drop border airports | Stata stackedev (SSC) |
| M10 | Wing, C.; Freedman, S.M.; Hollingsworth, A. (2024). Stacked Difference-in-Differences. NBER Working Paper 32054. 10.3386/w32054 | Basic stacked estimator applies different implicit weights to treated and control trends and is biased; corrective weights identify a trimmed aggregate ATT | Use their weights whenever we stack tax events; balanced event window | R and Stata example code on GitHub (hollina/stacked-did-weights); no SSC command |
| M11 | Abadie, A.; Diamond, A.; Hainmueller, J. (2010). Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program. Journal of the American Statistical Association 105(490), 493-505. 10.1198/jasa.2009.ap08746 | Synthetic control for one treated aggregate unit; donor pool excludes units with similar interventions; placebo permutation inference | Single-country events (NL, SE, NO) at country or airport level (precedent: Borbely 2019; Kang et al. 2022) | Stata synth, allsynth (SSC); R Synth, tidysynth, scpi (CRAN) |
| M12 | Arkhangelsky, D.; Athey, S.; Hirshberg, D.A.; Imbens, G.W.; Wager, S. (2021). Synthetic Difference-in-Differences. American Economic Review 111(12), 4088-4118. 10.1257/aer.20190159 | Combines DiD and synthetic control ideas; robust with latent unit x time factors | Single-country taxes on airport panels; staggered version in Stata (precedent for centrality outcomes: Khordagui 2025) | Stata sdid, sdid_event (SSC); R synthdid (GitHub, not on CRAN) |
| M13 | Conley, T.G.; Taber, C.R. (2011). Inference with 'Difference in Differences' with a Small Number of Policy Changes. Review of Economics and Statistics 93(1), 113-125. 10.1162/REST_a_00049 | Inference when few groups change policy, using the distribution of control-group residuals; CI by test inversion | Six to ten taxed countries clustered by country | Stata do files and Matlab code on C. Taber's website (users.ssc.wisc.edu/~ctaber/DD/diffdiff.html); no SSC command |
| M14 | Cameron, A.C.; Gelbach, J.B.; Miller, D.L. (2008). Bootstrap-Based Improvements for Inference with Clustered Errors. Review of Economics and Statistics 90(3), 414-427. 10.1162/rest.90.3.414 | With few (5 to 30) clusters standard tests over-reject; wild cluster bootstrap-t restores size | Country clustering within Europe (about 30 countries) | Stata boottest (SSC) |
| M15 | MacKinnon, J.G.; Webb, M.D. (2017). Wild Bootstrap Inference for Wildly Different Cluster Sizes. Journal of Applied Econometrics 32(2), 233-254 (online 2016). 10.1002/jae.2508 | Unbalanced clusters break the rule of 42; wild cluster bootstrap helps but fails when few clusters are treated | Warns that country-clustered WCB alone will not rescue few-treated designs | Stata boottest (SSC) |
| M16 | MacKinnon, J.G.; Webb, M.D. (2018). The wild bootstrap for few (treated) clusters. Econometrics Journal 21(2), 114-135. 10.1111/ectj.12107 | Subcluster wild bootstrap (ordinary wild bootstrap as limit) for few treated clusters; requires similar cluster sizes, unlikely in DiD | One of several inference checks | Stata boottest (SSC) |
| M17 | Ferman, B.; Pinto, C. (2019). Inference in Differences-in-Differences with Few Treated Groups and Heteroskedasticity. Review of Economics and Statistics 101(3), 452-467. 10.1162/rest_a_00759 | Group-size heteroskedasticity invalidates few-treated methods; corrected procedure | Treated countries differ greatly in size; pair with Conley-Taber | No package verified |
| M18 | MacKinnon, J.G.; Webb, M.D. (2020). Randomization inference for difference-in-differences with few treated clusters. Journal of Econometrics 218(2), 435-450. 10.1016/j.jeconom.2020.04.024 | With few treated clusters CRVE over-rejects and WCB variants mis-size; RI on t-statistics performs better than RI on coefficients | Permute tax adoption across countries and dates | Stata ritest (SSC, general permutation tests); country-level permutation coded by user |
| M19 | Roodman, D.; Nielsen, M.O.; MacKinnon, J.G.; Webb, M.D. (2019). Fast and wild: Bootstrap inference in Stata using boottest. Stata Journal 19(1), 4-60. 10.1177/1536867X19830877 | Fast wild (cluster) bootstrap after regress, areg, reghdfe, ivregress, ivreg2 and ML commands; multiway clustering; test inversion | Default inference add-on for every regression table | Stata boottest (SSC); R fwildclusterboot removed from CRAN (checked 2026-10-02) |
| M20 | MacKinnon, J.G.; Nielsen, M.O.; Webb, M.D. (2023). Cluster-robust inference: A guide to empirical practice. Journal of Econometrics 232(2), 272-299. 10.1016/j.jeconom.2022.04.001 | Practical guide to clustering level and inference choice | Choosing airport vs country vs route clustering; leverage diagnostics | Stata summclust (SSC) |
| M21 | Callaway, B.; Goodman-Bacon, A.; Sant'Anna, P.H.C. (2024 (WP)). Difference-in-differences with a Continuous Treatment. NBER Working Paper 32117; arXiv 2107.02637 v8 (Dec 2025). 10.3386/w32117 | ATT-type dose parameters identified under generalized parallel trends, but comparing doses needs stronger assumptions (selection bias); TWFE dose estimands hard to interpret | Our EEA x EUA price design is a continuous-dose TWFE; prefer an exposure dose with an untreated group and report dose-response caveats | R contdid (CRAN 0.1.1); companion AEA P&P 2024 (10.1257/pandp.20241047) |
| M22 | Butts, K. (2023 (WP)). Difference-in-Differences Estimation with Spatial Spillovers. arXiv 2105.03737 v3 (10 June 2023). arXiv:2105.03737 | Spillovers bias DiD through contaminated controls and through treated units' exposure to close units; distance rings x treatment estimate spillovers, valid if each ring has parallel trends with far-away controls; imputation for staggered timing | Template for displacement: rings of foreign airports around taxed countries and a 'network ring' of non-EU hubs estimated as separate outcomes, far-away airports as controls | Rings built by user; imputation via did2s (SSC, CRAN) |
| M23 | Rambachan, A.; Roth, J. (2023). A More Credible Approach to Parallel Trends. Review of Economic Studies 90(5), 2555-2591. 10.1093/restud/rdad018 | Robust inference when parallel trends may fail; bounds post-period violations relative to pre-trends; sensitivity analysis | Report breakdown values for centrality effects given LCC growth trends | R HonestDiD (CRAN); Stata honestdid (SSC) |
| M24 | Roth, J.; Sant'Anna, P.H.C.; Bilinski, A.; Poe, J. (2023). What's trending in difference-in-differences? A synthesis of the recent econometrics literature. Journal of Econometrics 235(2), 2218-2244. 10.1016/j.jeconom.2023.03.008 | Practitioner synthesis: staggered timing, parallel-trends violations, inference | Citation for the estimator menu | Not applicable |

Applied exemplars from energy and environmental economics:

- **X01. Andersson, J.J. (2019).** Carbon Taxes and CO2 Emissions: Sweden as a Case Study. *American Economic Journal: Economic Policy* 11(4), 1-30. DOI 10.1257/pol.20170144. Status: PARTIAL. Design: Synthetic control from comparable OECD countries. Headline: Transport CO2 declined almost 11%, largest share due to the carbon tax; carbon-tax elasticity of gasoline demand three times the price elasticity (abstract). Lesson: Energy Economics audiences accept SCM for a single-country price instrument; tax responses can exceed price-elasticity simulations
- **X02. Dechezlepretre, A.; Nachtigall, D.; Venmans, F. (2023).** The joint impact of the European Union emissions trading system on carbon emissions and economic performance. *Journal of Environmental Economics and Management* 118, 102758. DOI 10.1016/j.jeem.2022.102758. Status: VERIFIED. Design: Matching on inclusion criteria (exact on country and NACE3; Mahalanobis on pre-ETS emissions level and growth; caliper 0.3; with replacement) plus Poisson DiD with installation and year FE and country and sector trends; 240 matched pairs. Headline: Emissions about -10% between 2005 and 2012 (abstract); Table 5 ETS x Post -0.10 to -0.11 (SE 0.06); robustness range 6% to 13%; effect driven by the largest installations. Lesson: Analogue for matching EEA airports to non-EEA or low-exposure airports on pre-period level and growth, clustering at matched-set level

### 5.1 What the applied aviation papers actually used

| Method | Used by (papers read) |
|---|---|
| TWFE DiD | Fageda and Teixido 2022; Bernardo et al. 2024 (comparison); Fageda and Oesingmann 2025 (both); Gurr and Moser 2017; Helmers and van der Werf 2025 (static); Bernardo and Fageda 2017 |
| Callaway-Sant'Anna | Bernardo et al. 2024 |
| Entropy balancing | Fageda and Teixido 2022; Bernardo et al. 2024; Fageda and Oesingmann 2025 (Economics of Transportation) |
| Synthetic control | Borbely 2019; Kang et al. 2022; Strale 2021; Lorner and Jedvik 2026; (energy: Andersson 2019) |
| Synthetic DiD | Khordagui 2025 (mergers, centrality outcomes) |
| Dynamic panel, Arellano-Bond, QML | Helmers and van der Werf 2025; Falk and Hagsten 2019 |
| Specification curve | Helmers and van der Werf 2025; Wozny 2024 |
| Continuous dose (tax or price) | Fageda and Oesingmann 2025 (EUA price); Wozny 2024 (tax rate); Gurr and Moser 2017 (tax rate); Bernardo et al. 2024 (tax in euros, Table A4, from text); Collet et al. 2023 (per euro) |
| Matching / PSM-DID | Zhang et al. 2026; (energy: Dechezlepretre et al. 2023) |
| Proxy SVAR | Albert et al. 2025 |
| Gravity PPML | Oesingmann 2022 |
| Sun-Abraham, BJS imputation, dCDH, weighted stacking, continuous-treatment DiD (CGBS), HonestDiD | None found in the aviation tax or ETS papers read |
| Inference: route or city-pair clusters | Fageda and Teixido 2022; Bernardo et al. 2024; Fageda and Oesingmann 2025; Bernardo and Fageda 2017; Wozny 2024 |
| Inference: country clusters | Helmers and van der Werf 2025 (27); Gurr and Moser 2017 (61 destination countries); Wozny 2024 (country-pair robustness) |
| Inference: placebo / permutation / bootstrap | Borbely 2019; Lorner and Jedvik 2026; Khordagui 2025; Albert et al. 2025 (68% bands) |
| Conley-Taber, Ferman-Pinto, wild cluster bootstrap, randomization inference | None in aviation papers read (Ferman-Pinto used by Cengiz et al. 2019) |

## 6. Treatment dates as reported in the sources read (verify against legal texts before coding)

| Policy | Date or change as reported | Source | Conflict |
|---|---|---|---|
| Netherlands ticket tax | In force 1 Jul 2008; rate set to zero 1 Jul 2009 (formal abolition 1 Jan 2010 in summary, December 2009 in a footnote); EUR 11.25 / 45.00 | KiM 2011 | Internal date inconsistency on abolition |
| Netherlands reintroduction | 2021 at EUR 7.85; 2023 raised to EUR 26.43; distance bands planned from 2027 | KiM 2026 | |
| Germany Luftverkehrsteuer | Passed 28 Oct 2010; in force 15 Dec 2010; bookings from 1 Sep 2010 for departures from 1 Jan 2011 | BT-Drs. 17/10225 | |
| Austria Flugabgabe | 1 Apr 2011, EUR 8 to 35; EUR 7 to 35 from 2013 | IHS 2012 | |
| Sweden | Decided 22 Nov 2017 (SFS 2017:1200); in force 1 Apr 2018 | Wozny 2024 | |
| Norway | 1 Jun 2016, NOK 80; destination-based from 2019 (NOK 75 / 200) | Lorner and Jedvik 2026 | Bernardo et al. Table 1: "January 2016" |
| Ireland Air Travel Tax | 30 Mar 2009 (EUR 10 / EUR 2); cut to EUR 3 in Mar 2011; abolished Apr 2014 | SEO 2009; Bernardo et al. Table 1 | |
| UK APD | 1 Nov 1994; doubled 1997; reformed 2001; doubled Feb 2007; four distance bands from 2009 | Seetaram et al. 2014; Mayor and Tol 2007 | Bernardo et al. Table 1: 1998 |
| Malta | 2001 to Nov 2008 | Bernardo et al. Table 1 | |
| Portugal | Jul 2021 | Bernardo et al. Table 1 | |
| France | 1999 / 2006 (older taxes) | Bernardo et al. Table 1 | 2020 eco-contribution: no ex-post study found |
| EU ETS aviation | 2012 full scope ambiguous; stop-the-clock (Decision 377/2013); 2013 first treated year; Croatia 2014; Swiss link 2020 | Fageda and Teixido 2022; Fageda and Oesingmann 2025 | 2012 treated as untreated by F&O (free allocation above verified emissions) |
| EU ETS reform | Directive (EU) 2023/958: free allocation cut 25% (2024), 50% (2025), full auctioning from 2026; extra-EEA derogation to 31 Dec 2026; outermost-region flights covered from 2024 except domestic | Scheelhaase et al. 2024; EUR-Lex check (strand 2) | F&O cite 2023/959 (general ETS revision) instead |

## 7. Dropped, corrected or unread leads

Corrections to the original leads:
- "DLR and/or Intraplan evaluation for the Finance Ministry": the ministry's 2012 ex-post evaluation was by **Infras** (entry T02). Intraplan worked for the airline association BDL (seen only as summarised in BT-Drs. 17/10225 and IHS 2012). DLR appears as ex-ante analyst (Berster et al. 2010) and data supplier to KiM (Grimme and Maertens 2010); neither was read.
- "CE Delft (2018), A study on aviation ticket taxes": exists but is a legal and design review (state aid, transfer exemptions) without elasticities or ex-post evaluation; not entered. The CE Delft and SEO (2019) report for DG MOVE was used instead (T17).
- Falk and Hagsten: correct citation is IJTR 21(1), 37-44, 2019 (online 2018). Ciliberto et al.: RIO 54(1), 2019 (online 2018). Seetaram et al.: JTR 53(4), 2014 (online 2013). MacKinnon and Webb: JAE 32(2), 2017 (online 2016).
- de Chaisemartin and D'Haultfoeuille "intertemporal" is now REStat 108(4), 863-880 (Crossref issue year 2026). The "continuous treatments with stayers" paper is retitled "DiD Estimators for Treatments Continuously Distributed at Every Period" (arXiv v7, July 2026), still a working paper.

Excluded by rule:
- Maertens, Grimme, Scheelhaase, Jung (2019), Sustainability: MDPI, excluded.

Not found (searched with refcheck, OpenAlex, Crossref; WebSearch unavailable):
- Trafikanalys evaluation of the Swedish tax (trafa.se search did not render) and TOI evaluation of the Norwegian tax.
- Ex-post studies of Northern Ireland's 2012 long-haul APD cut vs Dublin, Scottish APD devolution, France's 2020 eco-contribution, Italy's municipal surcharge, and Denmark's 2007 abolition.
- Any ex-post paper on the 2021 Dutch reintroduction other than KiM (2026).
- Fageda (or co-authors) on Gulf carriers or carbon leakage via hubs beyond F&O (2025); EU-US Open Skies or Brexit with a connectivity outcome; HSR with airport centrality as outcome; ticket taxes with hub connectivity as outcome.
- DLR (Grimme, Maertens et al.) academic paper quantifying transfer-passenger leakage to non-EU hubs: none found outside MDPI; Scheelhaase et al. (2024) cite grey literature only.
- Santonja, Teixido and Zaklan (2023) pass-through working paper; Oesingmann and Fageda (2024) "airfares +18%" (cited by Albert et al.); Fichert et al. (2014): not located.

Exist but not read (worth obtaining manually):
- Collet, Quirion and Taconet (2023) SSRN 4499806 full text (only abstract read; T12).
- Falk and Hagsten (2019) full text; Oesingmann (2022) full text; Kang et al. (2022) full text; Zhang et al. (2026, Energy Economics) full text.
- Fageda and Teixido (2025), Environmental and Resource Economics, DOI 10.1007/s10640-025-01047-0 (technology channel; PDF link returned HTML).
- De Jong (2022) SSRN 4206318 (fleet channel); Boto-Garcia et al. (2024), Annals of Tourism Research 108, 103813 (panel local projections; highlights only).
- SEO, Lieshout, Boonekamp and Zuidberg (2018), ex-ante study for the Dutch reintroduction; Beimann and Lueg-Arndt (2012); Steverink and van Daalen (2011); Fors and Ljung (2019, Lund student paper); Sharapova (2020); Kopsch (2016) / SOU 2016:83.
- Malighetti, Paleari and Redondi (2008), JATM 14(2), 53-65 (existence confirmed); Mueller (2021) RTE 94, 101127; Wang, Bonilla and Banister (2015) JTG; Mueller and Aravazhi (2020) TRD.
- Grey literature cited secondhand only and not verified: Oxera (2022) "EU hubs lose 4% of transfer passengers by 2030 and 9% by 2050"; SEO and NLR (2022) "leakage about 1% of 2035 baseline emissions"; European Commission impact assessments; Intraplan (2012) "at least 5 million passengers lost". Do not cite these numbers without reading the originals.

Methods leads dropped:
- Abadie (2021, JEL 59(2), 391-425): abstract only, not entered as a row (cited in strand4 notes).
- Leroutier (2022, JEEM 111, 102580): HAL copy blocked by a bot check; not entered.
- Clarke (2017) spillover DiD working paper and Berg and Streitz spillover note: not verified; Butts (2023) used instead.
