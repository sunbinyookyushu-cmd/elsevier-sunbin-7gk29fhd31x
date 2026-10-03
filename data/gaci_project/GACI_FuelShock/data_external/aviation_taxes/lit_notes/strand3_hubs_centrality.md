# Strand 3: Hub competition (Gulf, Istanbul) and centrality or connectivity as a policy outcome

Notes compiled 2026-10-02 for the Energy Economics paper on ticket taxes, EU ETS and airport hub functions.

How the search was done. The session WebSearch budget was exhausted, so candidates were found with refcheck (Crossref, Semantic Scholar), the OpenAlex API and Semantic Scholar API, then full texts were fetched from repositories (Cranfield CERES, MIT DSpace, UCL Discovery, PolyU, Universitat de Barcelona, PubMed Central) or read as open HTML in the browser (ScienceDirect open access, Springer, SSRN). Every citation below was checked with refcheck. MDPI journals were skipped.

Copyright note. Headline results are given as exact numbers with their table, section or page, in paraphrase. Only one short verbatim quote is used in this file (Wei and Kallbekken, PARTIAL list).

Status codes. VERIFIED = I read the method and results sections. PARTIAL = abstract only (or abstract plus one passage). Fields I did not read are marked "not read".

## Quick map

| # | Study | Status | Design | Outcome type |
|---|---|---|---|---|
| 1 | Khordagui (2025) SSRN | VERIFIED | Synthetic DiD, 5 US mergers | Airport degree, closeness, eigenvector, betweenness (weighted and unweighted) |
| 2 | Ciliberto, Cook, Williams (RIO, 2018 online) | VERIFIED | Event-window panel, airport-merger FE + airport trends | Degree, closeness, betweenness (unweighted) |
| 3 | Allroggen, Wittman, Malina (TRE 2015) | VERIFIED (working paper version) | Index construction, descriptive | Global Connectivity Index and Global Hub Centrality Index |
| 4 | Suau-Sanchez, Voltes-Dorta, Rodriguez-Deniz (JTG 2016) | VERIFIED | Descriptive, MIDT cross-section | Flow betweenness (connecting-passenger shares) |
| 5 | Piltz, Voltes-Dorta, Suau-Sanchez (JATM 2018) | VERIFIED | Descriptive, two MIDT waves | Share of connections by hub region |
| 6 | O'Connell and Escofet Bueno (JATM 2018) | VERIFIED | Schedule-based index | Weighted connectivity ratio (wave quality) |
| 7 | Logothetis and Miyoshi (JATM 2018) | VERIFIED | Schedule-based index | Hub connectivity performance index, hub efficiency |
| 8 | Dray and Doyme (Climate Policy 2019) | VERIFIED | Simulation (AIM model) | Transfer passengers by hub, carbon leakage |
| 9 | Tolcha et al. (Transport Policy 2021) | VERIFIED | PLS-SEM | Country connectivity (flights, routes, ASK) |
| 10 | Liu, Wan, Ha, Yoshida, Zhang (TRA 2019) | VERIFIED | Airport FE panel | Airport traffic (HSR centrality is the treatment) |
| 11 | Bernardo and Fageda (TRE 2017) | VERIFIED | Route-level DiD | Seats, route entry |
| 12 | Sun, Wandelt, Zhang (JATM 2020) | VERIFIED | Descriptive daily networks | Degree, betweenness, assortativity, communities |
| P1-P8 | Vespermann et al. 2008; Grimme 2011; O'Connell 2011; Albers et al. 2009; Redondi et al. 2011; Burghouwt and Redondi 2013; Wei and Kallbekken 2024; Malighetti et al. 2008 | PARTIAL or not read | see below | |

Main finding for the paper: I found no ex post study that links a ticket tax or the EU ETS to airport centrality or to relocation of transfer traffic to Istanbul or Gulf hubs. The closest evidence is simulation (Dray and Doyme 2019) and an ex ante cost study (Albers et al. 2009). The closest methodological template for a centrality outcome in a causal design is Khordagui (2025).

---

## A. Policy evaluations with centrality or connectivity as the outcome

### 1. Khordagui (2025), airline mergers and airport connectivity

1. Citation: Khordagui, N. (2025). Airline Mergers and Airport Connectivity. SSRN Working Paper 5480222, version dated 1 September 2025, posted 13 September 2025, 58 pages, not peer reviewed. DOI 10.2139/ssrn.5480222. Verified: refcheck "verified" (Crossref).
2. Access: VERIFIED. Full PDF read (sections 1 to 7, Tables 1, 2, 4, 5, 13). URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5480222
3. Policy and setting: five US airline mergers, America West-US Airways (2005), Northwest-Delta (2008), Continental-United (2010), AirTran-Southwest (2011), US Airways-American (2013). US domestic network, 2000-2019.
4. Data: DOT Airline Origin and Destination Survey (DB1B Coupon, 10 percent ticket sample), quarterly 2000-2019, US reporting carriers between US airports, ticketing airline. One directed network per quarter, measures computed on the largest connected component, contiguous US only. Outcomes: degree, closeness, eigenvector and betweenness centrality, each unweighted and weighted by number of passengers (weighted closeness uses the reciprocal of passengers as segment length; weighted betweenness uses passenger-weighted shortest paths). Shortest paths are counted in segments; there is no time-feasibility or minimum connecting time screen. Covariates: county population, real average weekly wage; FAA hub size category for subgroups. Table 1 has 29,027 airport-quarter observations.
5. Identification: Synthetic Difference-in-Differences (Arkhangelsky et al. 2021), two-way FE with airport and year-quarter effects plus unit and time weights. Each merger estimated separately; pre-period 8 quarters, short run 8 quarters post, long run 20 quarters post; merger quarter dropped.
6. Control group and spillovers: treated airports are those where at least one merging airline had an average passenger share above 10 percent over the 8 pre-merger quarters. Control airports that acquire more than 10 percent presence after the merger are dropped to avoid contamination (1 to 8 percent of airports, 20 percent for Continental-United). Heterogeneity by hub size (large and medium vs small and non-hub), by graph-theoretic "center" status (minimum eccentricity), and by whether one or both merging airlines served the airport. I did not see any discussion of network spillovers onto control airports, even though centralities of control airports are mechanically linked to changes at treated airports.
7. Treatment timing: single date per merger (the quarter the merger took place); plots also mark announcement and single-code dates. No staggered pooling across mergers.
8. Inference: variance by block bootstrap, placebo variance when the treated group is small; placebo test with 1,000 random treatment assignments (section 6.2). Number of clusters or blocks not stated (the Continental-United sample has 227 airports).
9. Headline: Northwest-Delta, long run (Table 13, full sample): degree -7.33 percent, closeness -0.82 percent, eigenvector -5.21 percent, betweenness -27.62 percent, weighted betweenness -20.84 percent of the treated pre-merger mean. The text in section 5.2.2 gives 28.84 percent for weighted betweenness, which conflicts with the table. Continental-United, long run (Table 4): closeness +1.10 percent, weighted eigenvector +4.00 percent. America West-US Airways: no significant long-run effects. Effects concentrate at smaller and less central airports.
10. Transfer or centrality: yes, airport centrality in passenger networks. No taxes or carbon pricing.
11. Lesson for our design: the best template for a causal design with airport centrality outcomes. Copy (i) a presence-based treatment definition, (ii) dropping later-treated controls, (iii) reporting effects as a percent of the treated pre-period mean, (iv) weighted and unweighted versions side by side, and (v) a permutation placebo. Betweenness moves by tens of percent from small bases, so use log or rank transforms and annual aggregation.

### 2. Ciliberto, Cook and Williams, network structure and consolidation in the US

1. Citation: Ciliberto, F., Cook, E.E., Williams, J.W. Network Structure and Consolidation in the U.S. Airline Industry, 1990-2015. Review of Industrial Organization 54(1), 3-36. DOI 10.1007/s11151-018-9635-y. Verified: refcheck "verified"; Crossref lists year 2018 (online first) while the lead said 2019.
2. Access: VERIFIED. Full HTML read on Springer (sections 2.2, 3, 5, 6 and the Table 8 note). URL: https://link.springer.com/article/10.1007/s11151-018-9635-y
3. Policy and setting: five mergers (US Airways-America West, Delta-Northwest, United-Continental, Southwest-AirTran, American-US Airways) and a set of codeshare agreements; US domestic network 1990-2015.
4. Data: BTS T-100 Domestic Segment; the national network is the union of all carriers' networks (a route counts if any carrier serves it); airports near an MSA; 190 airports, 53,324 airport-month observations. Outcomes: unweighted degree, closeness, betweenness, standardized to mean 0 and SD 1; betweenness also as a dummy (airport lies on at least one shortest path) and for airports always "between". Distance is the number of links.
5. Identification: before-after regression around each event using 1 year before to 1 year after (and 1 year before vs the third year after), with airport-by-merger FE, airport-specific linear trends, quarter dummies, and controls for GDP, jet fuel price, MSA income and population. Pooled across mergers and estimated merger by merger.
6. Control group and spillovers: no untreated comparison group; identification is within-airport around the event date. National-network measures by construction.
7. Treatment timing: completion month in the main text; announcement, completion and single-code month and windows that drop the interim period are in the appendix (reported as analogous).
8. Inference: significance stars only (p<0.01, 0.05, 0.1 in the Table 8 note); standard error type and clustering not stated in the text or table note I read.
9. Headline: pooled merger effect (Table 8, section 5.2) on degree -0.00493 SD, closeness -0.0024 SD, betweenness -0.00121 SD, all insignificant; individual mergers differ, for example Delta-Northwest raised closeness by about 0.0588 SD and US Airways-America West lowered degree by about 0.0389 SD.
10. Transfer or centrality: yes (topology). No taxes.
11. Lesson: an event-window design without a control group, on an unweighted any-carrier network, finds near-zero effects. Our design should use seat-weighted networks and a real control group, and should report the extensive-margin "is between" indicator as well as levels.

### 9. Tolcha, Njoya, Brathen, Holmgren (2021), African liberalisation and air connectivity

1. Citation: Tolcha, T.D., Tchouamou Njoya, E., Brathen, S., Holmgren, J. (2021). Effects of African aviation liberalisation on economic freedom, air connectivity and related economic consequences. Transport Policy 110, 204-214. DOI 10.1016/j.tranpol.2021.06.002. Verified: refcheck "partial_match" (DOI resolves, metadata matches Crossref, no discrepancies listed).
2. Access: VERIFIED (open access HTML read in full). URL: https://www.sciencedirect.com/science/article/pii/S0967070X21001773
3. Policy and setting: air transport liberalisation in 52 African countries, annual 2011-2019 (468 observations).
4. Data: connectivity indicators from SRS Analyser (flight frequency, routes, available seat kilometres); liberalisation indicators: number of foreign scheduled airlines (ICAO), number of bilateral agreements (WASA-ICAO), number of international destinations (SRS Analyser); Heritage Foundation and UNDP for other constructs. No centrality.
5. Identification: PLS structural equation model with latent variables; no fixed effects, no control group, no event timing.
6. Control group and spillovers: none.
7. Treatment timing: none (latent continuous score).
8. Inference: p-values reported for path coefficients; no clustering described.
9. Headline: standardized path from liberalisation to connectivity 0.914 (p=0.000), adjusted R2 for connectivity 0.83 (Table 2).
10. Transfer or centrality: no. No taxes.
11. Lesson (cautionary): the liberalisation score is partly built from network outputs (international destinations), so its correlation with connectivity (0.91) is partly mechanical. Never build treatment intensity from network outcomes.

### 11. Bernardo and Fageda (2017), Morocco-EU open skies

1. Citation: Bernardo, V., Fageda, X. (2017). The effects of the Morocco-European Union open skies agreement: A difference-in-differences analysis. Transportation Research Part E 98, 24-41. DOI 10.1016/j.tre.2016.11.009. Verified: refcheck "partial_match" (DOI resolves, no discrepancies).
2. Access: VERIFIED (accepted manuscript, Universitat de Barcelona repository). URL: http://hdl.handle.net/2445/119872
3. Policy and setting: EU-Morocco open skies agreement signed December 2006; routes between North Africa and EU-15 plus Norway and Switzerland, 2003-2010 (stops before the Arab Spring).
4. Data: RDC Aviation (capstats) seats at airport-pair level; 191 pre-existing routes (1,501 observations) and 3,895 potential routes (31,160 observations). Outcomes: seats on existing routes; probability that a route is served. No centrality.
5. Identification: route-level DiD (route FE preferred, pooled as alternative), pre-trend evidence, matching on common support as robustness, instrument for route HHI.
6. Control group and spillovers: routes from the other North African countries to the same European countries. I did not see a discussion of diversion between Morocco and the control countries.
7. Treatment timing: single date (OSA signature, December 2006).
8. Inference: heteroskedasticity-robust SE clustered by route (pooled model with AR(1) errors).
9. Headline: seats on treated routes about 24 percent higher than on control routes after the OSA (route FE, Table 4); odds of a route being served 1.5 to 3.5 times higher (Table 5).
10. Transfer or centrality: no. No taxes.
11. Lesson: neighbours make natural controls but are exactly where displaced traffic goes in our setting. Treat neighbouring-country airports as a separate exposure group, not as controls.

### 12. Sun, Wandelt and Zhang (2020), COVID-19 and the air network

1. Citation: Sun, X., Wandelt, S., Zhang, A. (2020). How did COVID-19 impact air transportation? A first peek through the lens of complex networks. Journal of Air Transport Management 89, 101928. DOI 10.1016/j.jairtraman.2020.101928. Verified: refcheck search result (Crossref) and PubMed Central record.
2. Access: VERIFIED (full text on PMC). URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC7486886/
3. Event and setting: COVID-19 travel bans; worldwide, daily networks 16 December 2019 to 15 May 2020.
4. Data: Flightradar24 flights of 150 airlines between 2,751 airports, one network per day (152 days); unweighted degree, betweenness, assortativity, number of communities; also a country network and domestic networks (China, Europe, US).
5. Identification: descriptive network analysis.
6. Control group and spillovers: none.
7. Treatment timing: not modelled.
8. Inference: none.
9. Headline: average airport degree fell from about six to three; served OD pairs fell from about 80,000 to about 20,000 within roughly two weeks from mid-March 2020 (section 2.1). Istanbul and Dubai dropped close to inoperative, and betweenness of individual airports fluctuated by up to an order of magnitude within a week.
10. Transfer or centrality: yes (betweenness, degree). No taxes.
11. Lesson: daily or monthly unweighted betweenness is extremely volatile when big hubs drop out, because other nodes inherit shortest paths. Use annual aggregation and seat weights, and treat 2020-2021 as a separate shock (drop or interact).

---

## B. Hub competition: Gulf and Istanbul versus European hubs

### 4. Suau-Sanchez, Voltes-Dorta, Rodriguez-Deniz (2016), UK regional dependence on foreign hubs

1. Citation: Suau-Sanchez, P., Voltes-Dorta, A., Rodriguez-Deniz, H. (2016). The role of London airports in providing connectivity for the UK: regional dependence on foreign hubs. Journal of Transport Geography 50, 94-104 (online 2014). DOI 10.1016/j.jtrangeo.2014.11.008. Verified: refcheck "partial_match" (DOI resolves, no discrepancies).
2. Access: VERIFIED (author accepted manuscript, Cranfield CERES). URL: https://dspace.lib.cranfield.ac.uk/bitstreams/63aa3026-e966-41f3-9485-8531317afdad/download
3. Setting: UK and European airport network, May 2013; context of Heathrow capacity limits and Gulf and Istanbul growth.
4. Data: OAG Traffic Analyser MIDT bookings for May 2013 (GDS data adjusted by OAG for direct low-cost sales), itineraries with up to two connections: 489,573 itineraries, 148,305 directed markets, 66.9 million passengers, 436 airlines, 2,158 airports. Indicators: OD_i (share of market passengers originating or terminating at i), C_i (connecting passengers at i over passengers not originating or terminating at i, a flow-betweenness measure following Freeman et al. 1991), C'_i (share of all connecting passengers), connecting rate.
5. Identification: descriptive cross-section.
6. Control group and spillovers: none.
7. Timing: single month.
8. Inference: none.
9. Headline: in UK-international markets Dubai handles 10.0 percent of connecting passengers, Amsterdam 9.9 percent and Heathrow 8.1 percent (Table 4); for regional UK to Asia-Pacific, Dubai's share is 39.5 percent (Table 6); non-UK hubs handle between 63 and 85 percent of transfer passengers in the long-haul markets (section 3.2). Table 2 (OAG): destinations served 2004-2013 grew 105.3 percent at Istanbul and 58.3 percent at Dubai, against -6.9 percent at Heathrow.
10. Transfer or centrality: yes, passenger flow betweenness. Taxes: the discussion lists Air Passenger Duty reform among UK options (footnote 14 notes the higher APD bands were to be abolished from April 2015), but there is no analysis of taxes and hub choice.
11. Lesson: the "decoupling" or "demand leakage" of UK regional transfer demand to Amsterdam, Dubai and Istanbul is the mechanism we test. Our OAG betweenness is supply-side; if MIDT is unavailable, document that supply-side centrality is a proxy for passenger flow betweenness.

### 5. Piltz, Voltes-Dorta, Suau-Sanchez (2018), European and Asian hubs against Middle Eastern hubs

1. Citation: Piltz, C., Voltes-Dorta, A., Suau-Sanchez, P. (2018). A comparative analysis of hub connections of European and Asian airports against Middle Eastern hubs in intercontinental markets. Journal of Air Transport Management 66, 1-12. DOI 10.1016/j.jairtraman.2017.09.006. Verified: refcheck "partial_match" (DOI resolves, no discrepancies).
2. Access: VERIFIED (author accepted manuscript, Cranfield CERES). URL: https://dspace.lib.cranfield.ac.uk/bitstreams/16760732-6c95-451e-8d28-460c9019f511/download
3. Setting: Eastern US to South Asia and to South East Asia, June 2012 vs June 2016.
4. Data: MIDT bookings (average week, OAG-adjusted) for June 2012 and June 2016; OAG schedules for the first week of June 2016 (697,411 departures) and OAG Connections Analyser minimum connecting times (about 70,000 airline-specific exceptions). Outcome: each hub's share of connecting passengers in a market (C_ik); quality of connections from a connections-building algorithm (published MCT, maximum connecting time one hour above the shortest weekly connection, bookings allocated to flights by seat capacity).
5. Identification: descriptive two-period comparison; the authors state they lack a counterfactual to separate new demand from diversion (section 3.1).
6. Control group and spillovers: none.
7. Timing: 2012 vs 2016.
8. Inference: none.
9. Headline (Table 5): Eastern US-South Asia, EEA hubs' share of connections fell from 52.9 to 22.4 percent while Middle East hubs rose from 32.4 to 62.3 percent (Heathrow 26.2 to 10.8 percent, Dubai 11.6 to 28.6 percent). Eastern US-South East Asia: Middle East 4.8 to 20.8 percent, EEA 12.5 to 3.6 percent. Istanbul (non-EEA Europe) rose 2.5 to 3.7 percent in South Asia.
10. Transfer or centrality: yes (market shares of transfer flows by hub region). No taxes.
11. Lesson: a clean way to measure relocation to non-EU hubs is the market-level share of one-stop flows (or feasible one-stop seats) routed via EEA hubs, via Istanbul and via Gulf hubs. Split Europe into EEA and non-EEA so Istanbul is identified separately.

### 6. O'Connell and Escofet Bueno (2018), hub performance of Emirates, Etihad, Qatar vs European hub carriers

1. Citation: O'Connell, J.F., Escofet Bueno, O. (2018). A study into the hub performance Emirates, Etihad Airways and Qatar Airways and their competitive position against the major European hubbing airlines. Journal of Air Transport Management 69, 257-268. DOI 10.1016/j.jairtraman.2016.11.006. Verified: refcheck "partial_match" (DOI resolves, no discrepancies).
2. Access: VERIFIED (author accepted manuscript, Cranfield CERES). URL: https://dspace.lib.cranfield.ac.uk/bitstreams/4a64f96d-0890-4e70-b727-32abc95cb34b/download
3. Setting: Gulf carriers (EK at DXB, EY at AUH, QR at DOH) vs LH, KL, AF, BA; single day, Thursday 12 June 2014.
4. Data: OAG schedules, over 3,700 nonstop flights of seven airlines, 295 airports, over 280,000 airport pairs with indirect connections; codeshares excluded, only online (same-airline) connections. Method: Danesi (2006) weighted connectivity ratio. A connection scores 1 in time if connecting time is between MCT and an intermediate threshold and 0.5 up to the maximum acceptable connecting time (240 minutes for intercontinental combinations); 1 in space if detour factor is at most 1.20 and 0.5 up to 1.50; the ratio compares weighted connections to those expected from a random schedule.
5. Identification: descriptive benchmarking.
6. Control group and spillovers: none.
7. Timing: one day.
8. Inference: none.
9. Headline (section 4.1, Table 3): weighted connectivity ratio 2.31 for Etihad (1,555.75 weighted connections against 672.36 under a random schedule), 2.17 for Qatar Airways, 1.44 for Air France, 1.13 for British Airways.
10. Transfer or centrality: yes (hub wave quality, time-feasible connections). No taxes.
11. Lesson: hub function is also temporal coordination. A schedule-based count of time-feasible, detour-limited connections per hub from OAG is a mechanism outcome that pure topology misses.

### 7. Logothetis and Miyoshi (2018), Turkish Airlines vs Emirates

1. Citation: Logothetis, M., Miyoshi, C. (2018). Network performance and competitive impact of the single hub: A case study on Turkish Airlines and Emirates. Journal of Air Transport Management 69, 215-223. DOI 10.1016/j.jairtraman.2016.10.003. Verified: refcheck "partial_match" (DOI resolves, no discrepancies).
2. Access: VERIFIED (author accepted manuscript, Cranfield CERES). URL: https://dspace.lib.cranfield.ac.uk/bitstreams/8be6a584-6951-4e68-916f-0bfe0d877579/download
3. Setting: Turkish Airlines at Istanbul Ataturk (first week of July 2007, 2014, 2016) and Emirates at Dubai (2008, 2014, 2016).
4. Data: OAG schedules for the hub; MCTs from OAG; maximum acceptable connecting time set at three times MCT. Hub Connectivity Performance Analyser: viable connections, each weighted by routing factor (zero if detour above 50 percent), time factor with time-of-day penalties, seat factor, widebody service factor, and frequency factor that accounts for direct seats in the same OD market. HCPI is the sum of quality indexes; hub efficiency is HCPI over viable connections.
5. Identification: descriptive benchmarking.
6. Control group and spillovers: none.
7. Timing: snapshots.
8. Inference: none.
9. Headline (sections 4.1 and 4.3): in 2014 Turkish offered 103,368 effective weekly connections against 29,507 for Emirates, but hub efficiency was 68.6 percent against 76.7 percent; Turkish effective connections rose from 19,230 (2007) to 103,368 (2014).
10. Transfer or centrality: yes. No taxes.
11. Lesson: Istanbul's scale comes from high-frequency short-haul European feed, while Gulf hubs specialise in long-haul quality. Report seat-weighted and unweighted centrality and test separately whether displacement from taxed EU airports goes to Istanbul (short-haul feed) or to Gulf hubs (long-haul).

---

## C. Connectivity and hub centrality metrics

### 3. Allroggen, Wittman and Malina (2015), Global Connectivity Index

1. Citation: Allroggen, F., Wittman, M.D., Malina, R. (2015). How air transport connects the world: A new metric of air connectivity and its evolution between 1990 and 2012. Transportation Research Part E 80, 184-201. DOI 10.1016/j.tre.2015.06.001. Verified: refcheck "verified".
2. Access: VERIFIED, but for the working paper version: MIT ICAT Report No. ICAT-2015-01 (March 2015), DSpace@MIT, http://hdl.handle.net/1721.1/95968. The published TRE version was not read; numbers may differ slightly.
3. Setting: all world airports, yearly 1990-2012.
4. Data and metric: OAG schedules (December loads 1990-1998, January loads 1999-2012), scheduled passenger flights, codeshare duplicates removed. GCI of an airport = sum over all nonstop and one-stop routings of directness value x frequency (days operated in the year) x destination quality. One-stop routings must have at least 30 minutes layover and be on one airline that sells connections or a codeshare. Directness value falls linearly in a perceived detour factor (layover minutes count twice flight minutes), and is zero beyond a maximum detour calibrated as the 95th percentile of US DB1B one-stop tickets (Q2 2011) by distance band, constant beyond 4,200 km. Destination quality uses LandScan population adjusted by GDP per capita with a logistic distance decay capped at 257 km. The Global Hub Centrality Index (GHCI) applies the same sum to one-stop routings that transfer at the airport (eq. 15). A destination-invariant variant is also reported.
5. Identification: index construction and growth decomposition (network vs destination effects); no causal design.
6. Control group and spillovers: none.
7. Timing: annual.
8. Inference: none.
9. Headline: global one-stop connectivity grew about 3.5 times faster than nonstop connectivity (summary); hub centrality in Asia more than quintupled 2000-2012, with airports in the UAE and Qatar accounting for 14.7 percent and Turkish airports for 8.6 percent of Asian GHCI growth (section 4, p. 41). Table 7: the share of one-stop connectivity from South and South-East Asian origins routed via Dubai rose from 1.2 percent (rank 18) in 2000 to 7.6 percent (rank 2) in 2012.
10. Transfer or centrality: yes (GHCI is a transfer-based hub centrality). No taxes.
11. Lesson: the best blueprint for a time-feasible hub centrality outcome computable from OAG for each airport-year. Use the destination-invariant variant (destination weights would load GDP shocks into the outcome) and keep its MCT, same-ticket and detour rules as robustness alternatives to plain betweenness.

---

## D. Carbon pricing, taxes and hub relocation

### 8. Dray and Doyme (2019), carbon leakage in aviation policy

1. Citation: Dray, L., Doyme, K. (2019). Carbon leakage in aviation policy. Climate Policy 19(10), 1284-1296. DOI 10.1080/14693062.2019.1668745. Verified: refcheck "verified".
2. Access: VERIFIED (accepted manuscript, UCL Discovery). URL: https://discovery.ucl.ac.uk/10081643/1/DrayEtAl-CarbonLeakage-ClimatePolicy-Accepted.pdf
3. Policy and setting: hypothetical UK-only policies applied to the 2015 system: carbon price on UK departing flights of 15-300 USD per tCO2, a 5-40 percent biofuel mandate, and bonus-malus landing charges.
4. Data and model: components of the AIM global aviation model; city-pair demand, schedules, routing and fares from Sabre (2017); 878 cities, 20,000 city pairs touching the UK; multinomial logit itinerary choice on fare, travel time, frequency, number of legs and airport size; price elasticity -0.2 to -0.8; cost pass-through at congested airports 0, 50 or 100 percent; optional fleet swapping and fuel tankering.
5. Identification: simulation (no ex post estimation).
6. Control group and spillovers: leakage is the change in CO2 outside the policy area over the change inside, under three scope definitions.
7. Timing: static 2015 counterfactual.
8. Inference: ranges across uncertain parameters.
9. Headline: in the 300 USD per tCO2 test case with elasticity -0.2 and full pass-through (Table 2), international-to-international transfer passengers via UK hubs fall by 0.64 million per year (from 8.7 million) while transfers via non-UK hubs rise by 0.31 million (from 37.4 million). Leakage for carbon pricing ranges from +50 to -150 percent depending on scope and parameters (abstract).
10. Transfer or centrality: yes. This is the only study I found that explicitly links a carbon price to transfer passengers switching from a taxed country's hubs to foreign hubs, and it is a simulation.
11. Lesson: gives a structural prediction we can test ex post: the hub-switching channel is concentrated among international-to-international transfer passengers at hub airports, and it is smaller than demand suppression for origin-destination passengers. Test effects separately for transfer-heavy hubs and for origin-destination airports.

### 10. Liu, Wan, Ha, Yoshida, Zhang (2019), HSR network centrality and airport traffic

1. Citation: Liu, S., Wan, Y., Ha, H.-K., Yoshida, Y., Zhang, A. (2019). Impact of high-speed rail network development on airport traffic and traffic distribution: Evidence from China and Japan. Transportation Research Part A 127, 115-135. DOI 10.1016/j.tra.2019.07.015. Verified: refcheck "partial_match" (DOI resolves, no discrepancies).
2. Access: VERIFIED (accepted manuscript, PolyU repository). URL: https://ira.lib.polyu.edu.hk/bitstream/10397/89949/1/a0793-n04_1724.pdf
3. Policy and setting: HSR network expansion; 46 airports in China and 16 in Japan, annual 2007-2015.
4. Data: airport passenger traffic (China: Statistical Data on Civil Aviation of China; international traffic from China's Port-of-Entry Yearbook); HSR timetables (China July edition, JR March edition). Treatment intensity: the airport city's HSR degree centrality (number of prefecture-level stations reachable without changing trains, also split by distance band) and harmonic centrality; air-HSR intermodal link dummy.
5. Identification: airport fixed-effects panel regression (Hausman test favours FE), centrality interacted with the air-HSR link dummy; controls for population, GDP per capita, LCC base, fuel price, airport competition and year shocks.
6. Control group and spillovers: none beyond FE; airport competition variable included.
7. Treatment timing: continuous, annual.
8. Inference: standard errors in parentheses; clustering not stated.
9. Headline (Table 5, China, total passengers, millions): net effect of HSR degree centrality -0.028 (SE 0.012) at airports without an air-HSR link and +0.041 (SE 0.020) with a link; for international passengers with a link +0.048 (SE 0.007).
10. Transfer or centrality: centrality is the treatment, not the outcome. No taxes.
11. Lesson: a continuous-treatment panel with network-based intensity, analogous to our continuous EU ETS exposure; it shows that the same shock can raise hub traffic and lower non-hub traffic, so hub status interactions are needed.

---

## E. PARTIAL (abstract only) or not read

P1. Vespermann, J., Wald, A., Gleich, R. (2008). Aviation growth in the Middle East: impacts on incumbent players and potential strategic reactions. Journal of Transport Geography 16(6), 388-394. DOI 10.1016/j.jtrangeo.2008.04.009. refcheck "verified". PARTIAL (ScienceDirect abstract; paywalled). Abstract: UAE and Qatar invest in fleets and airports; Middle Eastern carriers aim to redirect international flows from Europe and the Americas to Asia; incumbents in Europe and Asia will be directly affected, though for some markets Middle Eastern carriers are disadvantaged on flight time and connections. Data, design, numbers: not read.

P2. Grimme, W. (2011). The growth of Arabian airlines from a German perspective: A study of the impacts of new air services to Asia. Journal of Air Transport Management 17(6), 333-338. DOI 10.1016/j.jairtraman.2011.02.002. refcheck "partial_match" (no discrepancies). PARTIAL (ScienceDirect abstract; DLR elib states no full text available). Abstract: German air transport statistics on passenger flows from Duesseldorf and Hamburg to Asia; Emirates services stimulated demand while incumbent hubs did not lose transfer passengers; Lufthansa protected Frankfurt and Munich with capacity and faster services. Design and numbers: not read. Lesson from abstract only: Gulf entry may create demand rather than divert it, so a fall in an EU hub's centrality need not mean passengers moved.

P3. O'Connell, J.F. (2011). The rise of the Arabian Gulf carriers: An insight into the business model of Emirates Airline. Journal of Air Transport Management 17(6), 339-346. DOI 10.1016/j.jairtraman.2011.02.003. refcheck "verified". PARTIAL (abstract): Emirates' success attributed to its hub-and-spoke operation, cost structure and brand. Business-model case study; no hub relocation estimates read.

P4. Albers, S., Buhne, J.-A., Peters, H. (2009). Will the EU-ETS instigate airline network reconfigurations? Journal of Air Transport Management 15(1), 1-6. DOI 10.1016/j.jairtraman.2008.09.013. refcheck "partial_match" (no discrepancies). PARTIAL (abstract). Route-based ex ante simulation for selected airlines; at 20 EUR per tCO2 the ETS cost increase is 9 to 27 EUR per route, judged too small on its own to trigger major route reconfigurations. Relevant as the ex ante prior that ETS-driven hub relocation should be small.

P5. Redondi, R., Malighetti, P., Paleari, S. (2011). Hub competition and travel times in the world-wide airport network. Journal of Transport Geography 19(6), 1260-1271. DOI 10.1016/j.jtrangeo.2010.11.010. refcheck "partial_match" (no discrepancies). PARTIAL (abstract; Bergamo repository blocked the download). Minimum travel time between airport pairs for 232 airports with more than 3 million departing seats in 2008; hub competition measures that separate location from temporal coordination; major European airports have a geographic advantage over American and Asian hubs, and hubs on different continents compete for the same OD markets.

P6. Burghouwt, G., Redondi, R. (2013). Connectivity in air transport networks: An assessment of models and applications. Journal of Transport Economics and Policy 47(1), 35-53. DOI 10.3828/jtep.2013.47.1.35. refcheck "verified". PARTIAL (abstract via Semantic Scholar). Compares eight connectivity models on European airports; size-based measures underestimate accessibility of small airports and overestimate centrality of large airports; model choice matters at lower levels of analysis.

P7. Wei, T., Kallbekken, S. (2024). Carbon leakage from aviation under the European Union Fit for 55 policies. Transportation Research Part D 132, 104269. DOI 10.1016/j.trd.2024.104269. refcheck "verified". PARTIAL (abstract plus one passage of the open access HTML). Links the AIM sectoral model with a general equilibrium model: leakage is limited and negative in the sectoral model but high and positive once lower world kerosene prices are fed back. The introduction notes that leakage through "'hub switching', but is not quantified" in the Commission impact assessments. This supports our claim that hub relocation from EU carbon policy has not been measured.

P8. Malighetti, P., Paleari, S., Redondi, R. (2008). Connectivity of the European airport network: "Self-help hubbing" and business implications. Journal of Air Transport Management 14(2), 53-65. DOI 10.1016/j.jairtraman.2007.10.003. Existence confirmed by refcheck search (Crossref). Not read (no open copy obtained).

---

## Cross-cutting lessons for our design

1. Outcome definitions. Report three families: (a) topology centralities on the OAG network (degree, betweenness, eigenvector), each seat-weighted and unweighted (Khordagui; Ciliberto et al.); (b) a time-feasible hub centrality that counts one-stop connections through the airport within MCT and detour limits, in the spirit of the GHCI (Allroggen et al.), with destination weights switched off; (c) market-level shares of feasible one-stop capacity routed via EEA hubs, Istanbul and Gulf hubs for OD markets that start in taxed countries (Piltz et al.; Suau-Sanchez et al.).
2. Relocation to non-EU hubs. Split hubs into EEA, non-EEA Europe (Istanbul) and Middle East, as Piltz et al. do. Expect Istanbul gains to show in short-haul feed and Gulf gains in long-haul one-stop markets (Logothetis and Miyoshi).
3. Treatment and controls in a network. A tax at one hub mechanically shifts other airports' betweenness (Sun et al. show large swings when hubs drop out), so SUTVA fails. Keep neighbouring-country airports as a separate exposure group (Bernardo and Fageda use neighbours as controls, which would absorb the displacement we want to measure), and drop or separately code later-treated units (Khordagui).
4. Functional form. Betweenness changes are large in percent terms from small bases (Khordagui: -27.6 percent). Use logs with a small constant or ranks, annual aggregation, and permutation placebos.
5. Inference. Only Bernardo and Fageda (route-clustered) and Khordagui (block bootstrap plus 1,000-draw placebo) describe inference clearly; Ciliberto et al. and Liu et al. do not state clustering. With few treated countries, cluster at the country level and use a wild cluster bootstrap or randomization inference.
6. Gap statement. Ex post evidence linking ticket taxes or the EU ETS to airport centrality or to transfer relocation toward Istanbul and the Gulf is absent in what I found; the only quantification is simulation (Dray and Doyme 2019), and ex ante cost evidence suggests small ETS effects (Albers et al. 2009).

---

## Dropped leads and what I could not verify

- Fageda and co-authors on Gulf carriers or carbon leakage via transfer hubs: no such paper found in refcheck or OpenAlex searches. Fageda items found were Bernardo and Fageda (2017, included) and Fageda and Teixido-Figueras (JEEM 2021, DOI 10.1016/j.jeem.2021.102591, EU ETS effects), which I did not read and leave to the ETS strand.
- EU-US Open Skies effects on connectivity: no policy evaluation with a connectivity or centrality outcome found. Janic (2009, Journal of Airport Management) appeared in search but is about Heathrow capacity management and was not read.
- Brexit and airport connectivity: nothing relevant found in refcheck or OpenAlex.
- HSR entry with airport centrality as the outcome: none found; Liu et al. (2019) uses HSR centrality as the treatment (included as an analogue).
- Turkish Airlines or Istanbul hub studies in JATM, JTG, Transport Policy 2015-2025 beyond Logothetis and Miyoshi: none found in these tools; "Turkiye as a regional hub" (Pressacademia 2024) dropped as a low-quality outlet.
- Ticket taxes and hub connectivity or transfer relocation: refcheck query on air passenger tax, connectivity and transfer relocation returned nothing relevant. The tax strand should check this from its side.
- Secondary claims seen inside papers but not verified at source: Dresner et al. (2015) on Gulf carriers and US carriers' traffic (cited in O'Connell and Escofet Bueno); Grosche and Klophaus (2015) on European hub dominance 2009-2012 (cited in Piltz et al.); the ACI Europe 2014 connectivity report figure on EU hubs' share of indirect connections (cited in O'Connell and Escofet Bueno). Do not cite these numbers without reading the originals.
- Found but not read for time: Mueller (2021) Research in Transportation Economics 94, 101127 (COVID and European connectivity, open access); Wang, Bonilla, Banister (2015) Journal of Transport Geography (China deregulation); Mueller and Aravazhi (2020) TRD (generalized travel cost connectivity, Scandinavia); Sun et al. later COVID network papers.
- Lead "O'Connell (2011), Emirates" verified but only the abstract was available (P3). Leads Vespermann et al. (2008) and Grimme (2011) exist as described in the brief but are paywalled (P1, P2).
