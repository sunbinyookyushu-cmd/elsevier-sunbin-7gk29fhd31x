# Strand 2: EU ETS and aviation (carbon leakage, EU vs non-EU hub competition, 2023 reform)

Compiled 2026-10-02 for the GACI aviation-tax / EU ETS paper (target: Energy Economics).

How to read these notes
- VERIFIED = I read the method and results sections (full text). PARTIAL = abstract plus whatever the publisher preview showed (introduction and section snippets); fields I did not see are marked "not read".
- Citations were checked with the refcheck tool (Crossref / Semantic Scholar). "partial_match 0.9" from refcheck means a Crossref-only match with no discrepancies (title, authors, volume, DOI all agree); it is not a mismatch.
- Quotation policy: to stay within quotation limits I report coefficients with their table and column location instead of verbatim sentences. There is one short verbatim quote in the whole file (entry 2). Every number below was read in the source; nothing is interpolated.
- Full texts were read from: University of Barcelona repository (diposit.ub.edu), DLR elib, UCL Discovery, ScienceDirect open-access pages (opened in the browser), EUR-Lex. Closed Elsevier papers were read only as far as the public preview goes (no institutional sign-in was used).

---

## Core studies

### 1. Fageda, X. and Teixido, J.J. (2022). Pricing carbon in the aviation sector: Evidence from the European emissions trading system. Journal of Environmental Economics and Management 111, 102591. DOI 10.1016/j.jeem.2021.102591
- Verification: refcheck "verified" (confidence 1.0; Crossref, Semantic Scholar). Published version is open access (CC BY-NC-ND).
- Access: VERIFIED. Read the full published PDF via the UB repository record http://hdl.handle.net/2445/181707 (bitstream https://diposit.ub.edu/bitstreams/2ef0d7b8-6736-495e-8f51-31e9b9856293/download). Sections 1 to 5 and Tables 1 to 6 read.
- Policy, region, period: aviation in the EU ETS; 44 European countries (EEA plus European non-EEA countries incl. Russia, Turkey, Switzerland, Ukraine, Balkans, Caucasus); quarterly 2010 to 2016.
- Data: RDC Aviation (capstats) schedules: seats, frequencies, aircraft type, distance, operating airline. Unit: airline-route (airport pair) by quarter; 58,239 airline-route pairs, 558,694 obs, regression sample 402,589 after dropping pairs with under one weekly flight. CO2 estimated with Eurocontrol Small Emitters Tool. Outcomes: ln CO2 emissions, ln flights; route exit (LPM) in Section 5. Controls: urban population (UN, Eurostat NUTS3), country GDP per capita (World Bank), monopoly dummy.
- Identification: DiD (route-airline FE, year FE, quarter FE) with entropy balancing (Hainmueller) of control routes on pre-2013 covariates (distance, income, population, HHI, mean CO2, LCC and network shares). Year-by-year "augmented" event study (Autor-style leads/lags), base year 2010, 99% CIs.
- Treated and control: treated = intra-EEA routes (both endpoints in EEA). Control = routes with at least one endpoint in a non-EEA European country. North Africa and Middle East excluded (Arab spring), Israel excluded (2013 open skies). Spillovers handled explicitly in Section 4.3 (SUTVA): the authors name two channels relevant to us, demand displacement from treated to control destinations and network airlines shifting connecting traffic within hub-and-spoke systems to control routes. Remedies: (a) control group restricted to routes with both endpoints outside the EEA (Table 4); (b) treated group restricted to Ryanair, which operates no control routes (Table 5 col 4); (c) departure-tax dummies for Germany, Austria, Ireland as covariates (Table 5).
- Timing and anticipation: treatment from 2013 (stop-the-clock, Decision 377/2013, retroactively limited 2012 scope to intra-EEA). 2012 treated as ambiguous; robustness drops 2012 (Table 2 cols 3 and 6). Croatia treated from 2014. No pre-trends in the event study; effects significant from 2014.
- Inference: heteroskedasticity-robust SEs clustered at the route level (footnote 20: identical when clustered at route-airline). Number of clusters not reported in what I read. No bootstrap.
- Headline estimates: Table 2 col 2 (entropy balanced, full sample) EU ETS on ln emissions = -0.047 (SE 0.018), on ln flights = -0.049 (0.018). Short-haul under 1,000 km without islands or with HSR, Table 2 col 5: -0.107 (0.050) emissions, -0.089 (0.033) flights. By airline type, Table 3 cols 2 and 5: network -0.020 (0.020) not significant, low-cost -0.110 (0.022). With non-EEA-only control routes, Table 4: -0.098 (0.027) full sample, -0.169 (0.059) short haul, i.e. larger than the baseline. Exit probability +0.022 (Table 6 col 1). Germany departure tax coefficient -0.053 (0.021) in Table 5 col 1.
- Transfer/hub/centrality: no network or centrality outcome. Hub-and-spoke appears only as a mechanism and as the SUTVA threat (connecting traffic shifted to control routes).
- Lesson for our design: the control-group choice moves the estimate by a factor of two (Table 4 vs Table 2), which is what one expects if EEA-to-non-EEA routes absorb displaced traffic. In an airport-level EEA vs non-EEA x EUA-price design, nearby non-EEA hubs (Istanbul, Zurich, post-2020 London) are the potential beneficiaries, so they must be modelled as a spillover-exposed group, not pooled into the control group. Their binary 2013 treatment also means our continuous EUA-price design is new relative to this benchmark.

### 2. Fageda, X. and Oesingmann, K. (2025). Intercontinental air travel in the era of carbon pricing: demand and hub shifts. Transportation Research Part A 200, 104658. DOI 10.1016/j.tra.2025.104658
- Verification: refcheck partial_match 0.9 (Crossref only, no discrepancies; authors Fageda and Oesingmann confirmed). Open access CC BY-NC-ND.
- Access: VERIFIED. Read the full published PDF from the UB repository (https://hdl.handle.net/2445/225755; bitstream https://diposit.ub.edu/server/api/core/bitstreams/6a5485f0-1f2e-414e-81c8-bb328a53158a/content). Sections 1 to 6, Tables 1 to 7 read; appendix tables A2 to A4 only as described in the text.
- Policy, region, period: EU ETS aviation, one-stop itineraries from EEA (plus UK, Switzerland) origins to North America and Central, South, East and Southeast Asia; annual 2010 to 2023 (main sample excludes 2020 and 2021).
- Data: Sabre Market Intelligence MIDT, annual O-D passengers by origin airport, connecting airport, destination airport and operating airline (over 2 million obs; 1,835,052 in the main regression). Leg frequencies and non-stop availability from Sabre; joint-venture coding from airline information. EUA price: daily prices from Investing.com averaged to years.
- Identification: DiD with continuous treatment intensity. Treated = itineraries whose connecting airport is in an EU ETS country (incl. UK, Switzerland), because the first (intra-EEA) leg is regulated. Treatment variable = yearly average EUA price (square-root transformed; the authors interpret the coefficient as an elasticity, and Table A2 with the untransformed price is said to give minimal differences). Fixed effects: origin-airport x year, destination-airport x year, route (origin-hub-destination) and airline x year. Also an event study with a treated-route dummy interacted with years (base year 2012), and a binary-dummy version (Table A3).
- Treated and control: controls are itineraries connecting at non-EU ETS hubs (Gulf, Istanbul, Asian and North American hubs). Spillover is the object of study: the sample is split into O-D markets served through both EEA and non-EEA hubs ("hub competition", indirect effect including hub leakage) and markets served only through one type ("no hub competition", direct effect).
- Timing and anticipation: treatment year 2013; 2012 not treated because 2012 free allocation exceeded verified aviation emissions (EEA 2023 cited). Swiss hubs treated from 2020 (ETS link). Event study shows no clear effect before 2018 and significant reductions from 2018, when EUA prices rose.
- Inference: robust SEs clustered by route (origin-hub-destination). Number of clusters not reported. No bootstrap.
- Headline estimates: Table 3 col 1, EU ETS (price) on ln passengers = -0.041 (0.002); Asia -0.051 (0.004); North America -0.032 (0.003). Table 4, 2010-2019 only: -0.027 (0.004). Table 5: hub-competition markets -0.038 (0.002) vs no-hub-competition markets -0.060 (0.012); for North America -0.0241 vs -0.0592; for Asia -0.0544 vs -0.0664. Table 7 (binary treatment): EU ETS dummy -0.114, JV interaction +0.106 (transatlantic joint ventures dilute the effect). Descriptive (Fig. 5): of passengers from Europe to Asia, 42% fly non-stop, 35% connect in the Gulf/Middle East or Asia, 16% connect at an ETS hub. Verbatim, Section 5: "this effect only seems to be relevant when such prices are high."
- Transfer/hub/centrality: yes, directly. Outcome is connecting passengers by hub; they document hub carbon leakage toward non-EEA hubs, strongest for Europe-Asia. No network centrality measure.
- Lesson for our design: this is the closest template for the continuous EUA-price DiD. Two cautions: (i) because the price is a common time series, identification comes from treated vs control hubs across high- and low-price years, so any EEA-specific shock correlated with the EUA price (2018 onward recovery, Brexit, COVID, 2022) loads onto the coefficient; their origin-year and destination-year FE help but there is no EEA x year control by construction. (ii) The effect appears only above roughly 2018 price levels, so we should test for nonlinearity (price bins or a post-2018 interaction) rather than impose a linear dose-response. Their hub-competition split maps directly onto our centrality outcome: EEA hubs whose O-D markets overlap with Gulf/Istanbul hubs should lose betweenness most.

### 3. Zhang, R., Shen, H., Luo, L. and Zhao, Y. (2026). International unilateral climate policies and carbon leakage: Evidence from airline routes. Energy Economics 157, 109279. DOI 10.1016/j.eneco.2026.109279
- Verification: refcheck partial_match 0.9 (Crossref, no discrepancies).
- Access: PARTIAL. Read abstract, highlights, full introduction and section snippets on ScienceDirect (https://www.sciencedirect.com/science/article/abs/pii/S0140988326001581). Methods and results tables not read (paywalled).
- Policy, region, period: EU ETS aviation; Chinese airlines' international routes within EU ETS jurisdiction vs their domestic routes in China; quarterly 2011Q1 to 2019Q4.
- Data: OAG route-level data (schedules) for all Chinese civil aviation companies; multi-stop itineraries excluded. Outcomes: CO2 emissions, flight frequency, passenger volume. Further sources not read.
- Identification: propensity-score-matched DiD (PSM-DID); mechanism and cross-sectional heterogeneity tests.
- Treated and control: treated = Chinese airlines' routes subject to the EU ETS; leakage tested on the same airlines' domestic routes. Exact control construction not read. Descriptive snippet: only 0.2% of matched international observations are EU-ETS-exposed routes in the post period.
- Timing: introduction describes 2012 inclusion and stop-the-clock; the exact treatment date coded is not read.
- Inference: not read.
- Headline (from the introduction): EU ETS lowers emissions on regulated routes by 12.25% and raises emissions on the airlines' Chinese domestic routes by 3.61%; channel is frequency and passengers; leakage stronger for non-alliance airlines and non-monopoly routes.
- Transfer/hub/centrality: no hub or transfer analysis seen; leakage operates through within-airline capacity reallocation to unregulated markets.
- Lesson: an Energy Economics precedent for estimating leakage as capacity reallocation by exposed carriers. With OAG carrier-level seats we can test whether carriers with high intra-EEA exposure move seats to non-EEA airports, a cleaner leakage channel than aggregate airport counts. The very small treated share flagged in their descriptives is a warning about how thin treated cells can be.

### 4. Kang, Y., Liao, S., Jiang, C. and D'Alfonso, T. (2022). Synthetic control methods for policy analysis: Evaluating the effect of the European Emission Trading System on aviation supply. Transportation Research Part A 162, 236-252. DOI 10.1016/j.tra.2022.05.015
- Verification: refcheck partial_match 0.9 (Crossref, no discrepancies).
- Access: PARTIAL. Read abstract, full introduction and section snippets on ScienceDirect (https://www.sciencedirect.com/science/article/abs/pii/S0965856422001367). The Sapienza repository (https://hdl.handle.net/11573/1663290) lists an open-access copy of the published PDF, but the file download was blocked by the repository's bot protection, so methods and result tables were not read.
- Policy, region, period: EU ETS aviation; annual 2007 to 2017 (5 pre and 5 post years); 315,193 routes in 48 countries, 31 regulated.
- Data: OAG, annual carrier-route level, 793,188 airline-route observations; seats, frequency, aircraft size.
- Identification: synthetic control per affected route (Abadie et al. 2010) with two modifications: weights justified by an unbiasedness argument suitable for few pre-periods, and a stochastic approximation scheme to make 53,566 nested optimisations feasible.
- Treated and control: affected vs unaffected routes; heterogeneity by low-cost/regional/full-service, short vs medium/long haul, hub vs non-hub endpoints, monopoly vs not. Spillover handling not read.
- Timing: aviation inclusion in 2012 (5 pre-periods to 2011). Anticipation handling not read.
- Inference: not read.
- Headline (abstract): seat capacity reduction above 20% at its peak; no substantial effect on average aircraft size; larger effects for low-cost and regional airlines, short-haul routes, spoke-spoke markets and monopoly routes.
- Transfer/hub/centrality: distinguishes routes to/from hubs vs non-hub (spoke-spoke) markets; no centrality measure.
- Lesson: synthetic control is a usable robustness check for hub-level case studies (for example one EEA hub's betweenness vs a donor pool of non-EEA hubs), and the larger spoke-spoke effect suggests heterogeneity by airport hub status in our design.

### 5. Albert, J.-F., Gomez-Fernandez, N. and Boto-Garcia, D. (2025). Up in the air: How do carbon policy shocks affect air travel? Transport Policy 168, 54-68. DOI 10.1016/j.tranpol.2025.04.003
- Verification: refcheck partial_match 0.9 (Crossref, no discrepancies). Open access.
- Access: VERIFIED. Read Sections 1 to 5.2 and Table 2 on ScienceDirect (https://www.sciencedirect.com/science/article/pii/S0967070X25001398). The flights subsection after 5.2 and the conclusions were cut off in my extraction.
- Policy, region, period: EU ETS carbon price shocks; EU aggregate plus Germany, UK, France, Italy, Spain and a pooled rest-of-EU; monthly January 2005 to December 2019.
- Data: Eurostat monthly passengers carried and commercial flights, split into domestic, intra-EU and extra-EU; HICP, HICP energy, HICP air passenger transport, industrial production, Brent, GHG, 2-year yield. Seasonally adjusted (X-13); outliers replaced.
- Identification: proxy SVAR (external instrument) using the Känzig (2023) high-frequency carbon policy surprise series; 2 lags, levels; shock normalised to raise HICP energy by 1% on impact.
- Treated and control: no control group; the authors argue that binary DiD with non-EEA control routes risks SUTVA violations and ignores variation in allowance costs. Extra-EU flows serve as a quasi-comparison.
- Timing: sample starts 2005 to capture anticipation of aviation inclusion; robustness on 2007-2019 and 2012-2019 subsamples, 6 lags.
- Inference: 68% bands from 10,000 bootstrap replications.
- Headline (Section 5.1): HICP air rises by more than 5% on impact (significant for 10 months); domestic passengers fall by up to 1.2% (significant for 15 months); intra-EU passengers fall similarly between months 5 and 10; extra-EU passengers show no significant response. Table 2: Germany domestic peak about -4% at 3 months; UK no significant response in any segment.
- Transfer/hub/centrality: no.
- Lesson: the Känzig surprise series is a ready instrument for the EUA price in our continuous-treatment DiD (instrument EEA x EUA price with EEA x surprise), which addresses the concern that EUA prices co-move with the EU business cycle. Our monthly OAG seats make a panel local-projection version feasible. Note their 68% bands: we should report conventional 90/95% inference.

### 6. Fageda, X. and Oesingmann, K. (2025). The impact of carbon pricing on tourist destinations: Shifts in demand, supply and emissions in the European aviation market. Economics of Transportation 42, 100414. DOI 10.1016/j.ecotra.2025.100414
- Verification: refcheck "verified" (0.9, Crossref). Open access CC BY.
- Access: VERIFIED. Read the published PDF from the UB repository (https://hdl.handle.net/2445/225757; bitstream c6a2c6db-6148-4c00-9ce9-da982337b275), Sections 1 to 6.1 and Tables 1 to 3.
- Policy, region, period: EU ETS aviation; 635 EEA (plus UK) origin cities to 114 tourist destinations (68 EEA treated; 46 control in Turkey, North Africa, Middle East, Cape Verde, Albania, Montenegro, plus the Canary Islands, Azores, Madeira and Turkish Cyprus); annual 2010 to 2022.
- Data: Sabre passengers (O-D, includes connecting passengers), RDC Aviation supply (seats, flights, aircraft), Eurocontrol SET for CO2; city-pair (multi-airport cities merged) by year. Main sample 22,056 obs (routes above 12,000 passengers per year); full sample 207,861; non-stop subsample 46,040.
- Identification: DiD with route FE and year FE, entropy balancing on origin and destination income and origin population (2010-2012 means); year-by-year event study (base 2012, 95% CI). Controls include Google Trends destination searches, exchange rate, political stability.
- Treated and control: treated = intra-EEA city pairs; controls = EEA origin to non-EEA destinations and to EU outermost regions (exempt until end-2023). Robustness restricts controls to EEA-only or non-EEA-only destinations. Authors note nearby non-EEA destinations may gain from the policy (leakage), which could overstate the emission effect.
- Timing: treatment 2013. They note that from 2024 the outermost-region exemption was restricted to domestic flights (outside their sample period).
- Inference: robust SEs clustered by route; number of routes reported (for example 3,020 routes in Table 2 col 2).
- Headline: passengers, Table 2 col 2 (matched): -0.0265 (0.0231), not significant; unmatched col 5: +0.110 (0.0163). ln CO2 on non-stop routes, Table 3 col 4: -0.0745 (0.0328), about -7%; level effects between -176.9 and -1,545 tonnes per route-year in matched specifications.
- Transfer/hub/centrality: passengers include connecting itineraries, but no hub analysis.
- Lesson: (i) the 2024 change in outermost-region coverage (Canary Islands, Madeira, Azores) is a clean within-EEA scope change we can exploit with 2024 monthly seats; (ii) supply falls while passengers do not, so seats and passengers must be analysed separately; (iii) entropy balancing on destination income matters a lot for EEA vs non-EEA comparisons (sign flips between matched and unmatched samples).

### 7. Oesingmann, K. (2022). The effect of the European Emissions Trading System (EU ETS) on aviation demand: An empirical comparison with the impact of ticket taxes. Energy Policy 160, 112657. DOI 10.1016/j.enpol.2021.112657
- Verification: refcheck "verified" (1.0).
- Access: PARTIAL. Read abstract, highlights, introduction and section snippets on ScienceDirect (https://www.sciencedirect.com/science/article/abs/pii/S030142152100522X).
- Policy, region, period: EU ETS and the Austrian and German air passenger taxes; intra-EEA country pairs. Period not read.
- Data: country-pair passenger flows (source not read).
- Identification: structural gravity model estimated by PPML with fixed effects; EU ETS and ticket taxes entered as dummies and alternatively as policy-specific variables.
- Treated and control: country pairs; details not read.
- Timing, inference: not read.
- Headline (abstract and highlights): no statistically significant effect of the EU ETS on intra-EEA passenger flows; the ticket taxes give significant, robust demand reductions on affected country pairs; replacing dummies with passenger- and route-specific policy variables reduces estimated impacts. Secondhand (cited by Fageda and Oesingmann 2025, EcoTra, Section 3.2, not verified by me in the source): the German and Austrian tax reduced intra-EEA demand by 4 to 12% depending on dummy vs actual-price specification.
- Transfer/hub/centrality: no.
- Lesson: in the same data, a binary policy dummy and a cost-based intensity give different magnitudes; we should report both the EEA x post-2013 dummy and the EEA x EUA-price version, and run the ticket taxes and the ETS in one model so neither absorbs the other.

### 8. Dray, L. and Doyme, K. (2019). Carbon leakage in aviation policy. Climate Policy 19(10), 1284-1296. DOI 10.1080/14693062.2019.1668745
- Verification: refcheck "verified" (1.0).
- Access: VERIFIED (accepted manuscript). Read the full author accepted manuscript from UCL Discovery (https://discovery.ucl.ac.uk/10081643/1/DrayEtAl-CarbonLeakage-ClimatePolicy-Accepted.pdf): methods, policy scope section, Table 2 and results.
- Policy, region, period: hypothetical UK-only policies applied to the 2015 global system: carbon price on UK departing flights (15 to 300 USD/tCO2), biofuel mandates (5 to 40%), environmental landing charges.
- Data: AIM model inputs; 20,000 city pairs with a UK origin or destination or a top-nine itinerary routed through the UK; city-pair demand from AIM base-year fits to Sabre data; multinomial logit itinerary choice estimated on Sabre (2017) data (fare, travel time, frequency, number of legs, airport size).
- Identification: simulation (global aviation systems model AIM), not econometric.
- Treated and control: not applicable; leakage defined under three emissions-attribution scopes (departing flights, fuel uptake, arriving plus departing flights).
- Timing: static 2015 system.
- Inference: scenario ranges over uncertain parameters (price elasticity, pass-through, fleet swaps).
- Headline: carbon-pricing leakage between +50% and -150% depending on scope and parameters (abstract). In the 300 USD test case with -0.2 elasticity and full pass-through, international-to-international transfer passengers moving from UK hubs to non-UK hubs is the second-largest CO2 change (positive leakage), but it is outweighed by reduced UK origin-destination demand; leakage on a departing-flights basis is about -60%, and about -115% with elasticity -0.8.
- Transfer/hub/centrality: yes. Hub switching of transfer passengers is modelled explicitly through itinerary choice.
- Lesson: provides the mechanism and sign ambiguity that our hub-centrality outcome can adjudicate empirically: a unilateral price on departing flights should reduce the hub function (betweenness, transfer share) of the taxed airports even if total emissions fall. It also shows that results depend on whether a policy covers departing or all flights, which matters for coding the EU ETS (intra-EEA, both directions) vs departure-based ticket taxes.

### 9. Wei, T. and Kallbekken, S. (2024). Carbon leakage from aviation under the European Union Fit for 55 policies. Transportation Research Part D 132, 104269. DOI 10.1016/j.trd.2024.104269
- Verification: refcheck "verified" (0.9, Crossref). Open access.
- Access: VERIFIED. Read Sections 1 to 4.3 on ScienceDirect (https://www.sciencedirect.com/science/article/pii/S1361920924002268); conclusions cut off in my extraction.
- Policy, region, period: Fit for 55 aviation package (ReFuelEU SAF mandate, Energy Taxation Directive kerosene tax, EU ETS revision ending free allocation from 2026), simulated 2015 to 2050 for the EU region (EEA plus Switzerland and UK).
- Data: AIM base year 2015 (878 cities, 1,169 airports, 40,265 flight segments, about 95% of global RPK); GRACE CGE calibrated to GTAP v10 (2014), four regions. Assumed EUA path 130 EUR/t (2030), 175 (2035), 315 (2050) taken from SEO and NLR (2022).
- Identification: simulation, sectoral model plus CGE.
- Treated and control: not applicable. CORSIA prices applied to non-EU CORSIA regions in both scenarios. Tankering not modelled.
- Timing: policy scenarios phased in per legislation; free allocation ends 2026.
- Inference: alternative scenarios (no CORSIA price, five times CORSIA price, biofuel A or B only).
- Headline (Section 4): AIM gives intra-EU ticket prices +15% and intra-EU RPK -13% by 2050, EU-to-rest-of-world RPK -3%; aviation leakage negative and small (RPK component from -3% in 2025 to -0.5% in 2050). GRACE gives positive economy-wide leakage of about 33%, about 10% within aviation outside the EU, falling to about 5% by 2050, driven by lower world refined-oil prices.
- Transfer/hub/centrality: AIM contains itinerary choice; the paper notes EU impact assessments discuss hub switching without quantifying it. No hub-level output reported.
- Lesson: the main ex-ante leakage study for the 2023 reform predicts small aviation-sector leakage; our ex-post hub-centrality evidence for 2013-2024 can be framed as a test of that prediction at the pre-reform price levels, and of the hub-switching channel the simulations leave unquantified.

### 10. Scheelhaase, J., Grimme, W. and Maertens, S. (2024). EU trilogue results for the aviation sector: key issues and expected impacts. Transportation Research Procedia 78, 206-214. DOI 10.1016/j.trpro.2024.02.027
- Verification: refcheck partial_match 0.9 (Crossref, no discrepancies). Open access (EWGT 2023 proceedings).
- Access: VERIFIED. Read the full paper from DLR elib (https://elib.dlr.de/202979/1/EWGT_2023_Printversion.pdf).
- Policy, region, period: December 2022 ETS trilogue and April 2023 ReFuelEU trilogue, EEA.
- Data: none (policy analysis and literature review).
- Identification: descriptive.
- Content verified (Section 3, Table 1): cap reduction 4.3% per year 2024-2027 and 4.4% 2028-2030 (from 2.2%); free allocation cut by 25% in 2024 and 50% in 2025, none from 2026; 20 million allowances (2024-2030) to support SAF use; non-CO2 MRV from 2025; scope stays intra-EEA plus EEA-to-Switzerland and EEA-to-UK, with possible extension from 2027 if the Commission judges CORSIA insufficient in a 2026 evaluation; outermost-region flights covered except domestic flights to and from them; SAF mandate 2% (2025) rising to 70% (2050) with a 90% refuelling obligation against tankering.
- Leakage discussion (Section 4, secondhand, grey literature not read by me): Oxera (2022, for ACI Europe) projects EU hubs losing 4% of transfer passengers by 2030 and 9% by 2050 to non-EU hubs; SEO and NLR (2022) put leakage at about 1% of 2035 baseline emissions. They also expect tourist flows to shift from Greece, Spain, Cyprus to Egypt, Turkey, Tunisia, Morocco, and transfer traffic to national hubs on outermost-region routes.
- Transfer/hub/centrality: discussed qualitatively (transfer passengers, hub switching).
- Lesson: gives the exact reform dates for coding. Our data end in 2024, so only the first step (2024: 25% of free allocation auctioned, and the 2024 scope change for outermost regions) is observed; the 2026 full auctioning is out of sample. Because free allowances carry the same opportunity cost (argued in Fageda and Teixido 2022, Section 2.2), the reform should matter for marginal cost mainly through the EUA price and scope, which favours a price-based treatment over a reform dummy.

Primary-source check of the reform (EUR-Lex, read in full text): Directive (EU) 2023/958 of 10 May 2023 amending Directive 2003/87/EC as regards aviation's contribution to the Union's economy-wide emission reduction target and the appropriate implementation of a global market-based measure, OJ L 130, 16.5.2023, p. 115-133 (https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023L0958). Article 1(3) amends Article 3d(1): in 2024 and 2025, 15% of aviation allowances plus 25% (2024) and 50% (2025) of the remaining 85% are auctioned; from 1 January 2026 the entire quantity that would have been allocated free is auctioned. Recital 30: extra-EEA derogation extended to emissions until 31 December 2026; CORSIA review by 1 July 2026; possible application to departing flights from 2027. Article 3c(8): domestic flights to and from outermost regions derogated until 31 December 2030. Note: Fageda and Oesingmann (2025, TR-A) cite Directive (EU) 2023/959, which is the general ETS revision; the aviation-specific act is 2023/958.

---

## Secondary entries (leads checked at abstract level)

### 11. Zhang, Y. and Wang, K. (2024). Mitigation effect of the European Union emission trading system on aviation emissions. Transportation Research Part D 130, 104186. DOI 10.1016/j.trd.2024.104186
- Verification: refcheck partial_match 0.9 (Crossref). Access: PARTIAL (abstract, introduction, snippets; https://www.sciencedirect.com/science/article/abs/pii/S1361920924001433).
- 60 countries, 2000 to 2019, national panel DiD treating the 2013 stop-the-clock regime as the quasi-experiment; mediation and heterogeneity tests. Snippet of baseline results: EU ETS lowers total aviation CO2 by 690 thousand tonnes and domestic aviation CO2 by 401 thousand tonnes in treated countries; no detectable effect on international aviation CO2. Data sources, clustering not read. No hub analysis.
- Lesson: country-level aggregation hides the intra-EEA vs extra-EEA split; airport-level outcomes are needed.

### 12. Scheelhaase, J., Grimme, W. and Schaefer, M. (2010). The inclusion of aviation into the EU emission trading scheme: Impacts on competition between European and non-European network airlines. Transportation Research Part D 15(1), 14-25. DOI 10.1016/j.trd.2009.07.003
- Verification: refcheck "verified" (1.0). Access: PARTIAL (abstract and section snippets; https://www.sciencedirect.com/science/article/abs/pii/S1361920909000844).
- Ex-ante cost model under the original full-scope design (all flights to and from EU airports from 2012), Lufthansa vs Continental, 20 EUR/t, EUROCONTROL BADA fuel data. Snippets: about 60% of Lufthansa long-haul passengers are transfer passengers; Continental would receive a higher share of free allowances and gain a competitive advantage on long-haul markets.
- Lesson: the hub-feeder exposure of EEA network carriers is the economic reason to expect hub-function losses; useful for motivation, not for identification.

### 13. Albers, S., Buhne, J.-A. and Peters, H. (2009). Will the EU-ETS instigate airline network reconfigurations? Journal of Air Transport Management 15(1), 1-6. DOI 10.1016/j.jairtraman.2008.09.013
- Verification: refcheck "verified" (1.0). Access: PARTIAL (abstract, introduction and snippets; https://www.sciencedirect.com/science/article/abs/pii/S0969699708001348).
- Route-based simulation using OAG schedules and aircraft emission data with secondary price elasticities, 20 EUR/t, under the proposed full-scope design. Abstract: cost increases of 9 to 27 EUR per route, judged too small on their own to trigger major route reconfiguration. Snippets: Newark-Delhi via Frankfurt costs 26.79 EUR per passenger trip extra; discusses artificial stopovers and the threatened Lufthansa hub move to Zurich.
- Lesson: early statement of the hub-relocation hypothesis we test ex post, at prices far below 2018-2024 levels.

### 14. Malina, R., McConnachie, D., Winchester, N., Wollersheim, C., Paltsev, S. and Waitz, I.A. (2012). The impact of the European Union Emissions Trading Scheme on US aviation. Journal of Air Transport Management 19, 36-41. DOI 10.1016/j.jairtraman.2011.12.004
- Verification: refcheck partial_match 0.79 (I supplied only the first author; Crossref lists all six authors, no other discrepancy). Access: PARTIAL (abstract only).
- Ex-ante 2012-2020 under full scope: small effects on US airlines; windfall gains because US carriers would buy only about a third of required allowances; profits rise with full pass-through of opportunity costs. Method details not read.

### 15. Anger, A. (2010). Including aviation in the European emissions trading scheme: Impacts on the industry, CO2 emissions and macroeconomic activity in the EU. Journal of Air Transport Management 16(2), 100-105. DOI 10.1016/j.jairtraman.2009.10.009
- Verification: refcheck "verified" (1.0). Access: PARTIAL (abstract). E3ME dynamic simulation; small output and macro effects; aviation CO2 down by up to 7.4%, mainly through supply-side response.

### 16. Meleo, L., Nava, C.R. and Pozzi, C. (2016). Aviation and the costs of the European Emission Trading Scheme: The case of Italy. Energy Policy 88, 138-147. DOI 10.1016/j.enpol.2015.10.008
- Verification: refcheck "verified" (1.0). Access: PARTIAL (abstract). Calculates direct EU ETS costs of Italian airlines 2012-2014 and forecasts 2015-2016 under low, medium and high permit-price and pass-through scenarios. Accounting exercise, no causal design.

### 17. Derigs, U. and Illing, S. (2013). Does EU ETS instigate Air Cargo network reconfiguration? A model-based analysis. European Journal of Operational Research 225(3), 518-527. DOI 10.1016/j.ejor.2012.10.016
- Verification: refcheck "verified" (1.0). Access: PARTIAL (abstract). Network-design optimisation for cargo airlines under ETS cost scenarios (full scope assumed). Relevant only as the cargo analogue of route reconfiguration.

### 18. Scheelhaase, J., Maertens, S., Grimme, W. and Jung, M. (2018). EU ETS versus CORSIA: A critical assessment of two approaches to limit air transport's CO2 emissions by market-based measures. Journal of Air Transport Management 67, 55-62. DOI 10.1016/j.jairtraman.2017.11.007
- Verification: refcheck "verified" (0.99). Access: PARTIAL (abstract). Qualitative comparison; recommends keeping the reduced (intra-EEA) scope beyond 2020 with CORSIA for international flights. Background for why extra-EEA legs stay untreated in our sample.

---

## Cross-cutting lessons for our EEA vs non-EEA x EUA-price design
1. Exposure. All causal papers define treatment at the route or itinerary level (intra-EEA legs). For an airport panel, the natural intensity is the pre-period share of an airport's seats on intra-EEA legs (from OAG) times the EUA price, which gives cross-sectional dose variation inside the EEA and avoids resting identification only on the EEA vs non-EEA contrast. (This is our construction, not one used in the papers.)
2. Spillover-exposed group. Fageda and Teixido (2022, Table 4) and Fageda and Oesingmann (2025 TR-A, Table 5) both show that where substitution to non-regulated routes or hubs is possible, the estimated gap changes size. Non-EEA hubs that compete for EEA transfer traffic (Istanbul, Gulf hubs, Zurich before 2020, London after Brexit) should be a separate group whose gain is the leakage estimate, with distant non-EEA airports as controls.
3. Price endogeneity and nonlinearity. Albert et al. (2025) instrument carbon prices with Känzig surprises; Fageda and Oesingmann (2025) find effects only after 2018. We should (a) instrument EEA x EUA price with EEA x Känzig surprises, and (b) allow price bins or a high-price-regime interaction.
4. Timing to code: 2008 directive (anticipation window), 2012 nominal full-scope year (ambiguous; both Fageda papers treat 2013 as first year), 2013 stop-the-clock scope, Croatia 2014, Swiss link 2020, UK out of EU ETS from 2021 (EEA-to-UK flights stay covered), 2024 first free-allocation cut and outermost-region scope change, 2026 full auctioning (outside our data).
5. Inference. Every route-level paper read clusters at the route level (thousands of clusters) and none reports the number of clusters. In our design the price variation is a single common time series and treatment is a bloc-level status, so route- or airport-level clustering will overstate precision; we should cluster at country level and use wild cluster bootstrap or randomisation inference over the time series. (Our recommendation, not a claim made in these papers.)
6. Outcomes. Supply (flights, seats) responds more than passengers in Fageda and Teixido (2022), Fageda and Oesingmann (2025 EcoTra) and Albert et al. (2025). Network centrality built from seats will pick up supply responses first.
7. Ticket taxes in the same model. Fageda and Teixido (2022) include German, Austrian and Irish tax dummies; Oesingmann (2022) estimates taxes and ETS jointly. Our staggered tax DiD and ETS intensity design should be estimated jointly so each controls for the other.

---

## Dropped leads (and why)
- Maertens et al. (2019), Sustainability: MDPI journal, excluded by instruction.
- Santonja, A., Teixido, J. and Zaklan, A. (2023), Carbon cost pass-through in European aviation: cited as a working paper by Fageda and Oesingmann (2025, TR-A) and Albert et al. (2025); refcheck search found no DOI or published record, and I could not locate a readable copy. Not included.
- Oesingmann and Fageda (2024), airfares on EU ETS routes about 18% higher: cited by Albert et al. (2025); I did not locate or verify the source. Not included.
- De Jong, G. (2022), Emission pricing and capital replacement: evidence from aircraft fleet renewal, SSRN 4206318 / Tinbergen Institute working paper TI 2022-060/VIII: existence confirmed via OpenAlex, not read (working paper, fleet channel rather than hub channel). Candidate for strand 4 if needed.
- Fageda and Teixido, Technology diffusion in carbon markets: evidence from aviation, Environmental and Resource Economics (2025), DOI 10.1007/s10640-025-01047-0: confirmed via OpenAlex as open access, but the Springer PDF link returned an HTML page and I did not read it. Fleet/technology channel, lower priority.
- Boto-Garcia, D., Albert, J.F. and Gomez-Fernandez, N. (2024), Carbon price shocks and tourism demand, Annals of Tourism Research 108, 103813 (refcheck partial_match 0.9): only highlights read (panel local projections, transitory drop in arrivals); tourism outcome, so not given a full entry. Useful as a panel local-projection template for monthly data.
- Grey literature (SEO Amsterdam Economics and NLR 2022; Oxera 2022 for ACI Europe; European Commission impact assessments): not read. Their numbers above are reported secondhand from Scheelhaase et al. (2024) and Wei and Kallbekken (2024) and are marked as such. Academic sources were sufficient, so I did not chase them.
- Kang et al. (2022) full text: open-access PDF exists in the Sapienza repository but the download was blocked by bot protection; entry kept as PARTIAL.
