# Literature found so far: EU ETS aviation, ticket taxes, hub leakage, centrality

Compiled 2026-10-02. Scope was cut back mid-task: a separate deep methods review will follow, so this file only lists what was already found and checked. No MDPI journals.

**Existence check.** Every DOI below was confirmed on Crossref with the refcheck MCP (`verify_reference`). "partial_match" verdicts were caused only by missing author lists in the query; title, DOI and journal matched.

**Status labels**
- **VERIFIED**: someone read the method and results text (open PDF or accepted manuscript).
- **PARTIAL**: abstract only.
- **EXISTS**: existence confirmed, content not read; do not cite content.

**Where numbers come from.** Headline numbers marked (abstract) or (text) were read from that source. "No number read" means none was read. I re-read Fageda and Oesingmann (2025, TRA) myself. The other entries come from two search agents who read the sources.

---

## A. Hub leakage and carbon pricing (closest to our question)

| # | Citation | DOI | Status | Policy, design, unit | Headline | Hub / centrality? |
|---|---|---|---|---|---|---|
| 1 | Fageda, X., Oesingmann, K. (2025). Intercontinental air travel in the era of carbon pricing: demand and hub shifts. *Transportation Research Part A* 200, 104658. | 10.1016/j.tra.2025.104658 | VERIFIED (I read the UB repository PDF) | **Policy:** EU ETS allowance price. **Design:** ln(passengers) on the square-root allowance price for one-stop routings via ETS hubs; controls are routings via non-ETS hubs (Gulf/Middle East, Asia, North America). Origin-year, destination-year, route and airline-year FE, plus an event study. **Data:** Sabre MIDT, origin x hub x destination x airline x year, 2010-2023 excluding 2020-21; Europe to Asia and North America. | (text) "A one-hundred percent increase in the allowance price has led to a 4 % decrease in passenger numbers on routes transferring via an ETS hub." Table 3 col 1 coefficient 0.041 (0.002) in absolute value. Table 5: 0.038 for the hub-competition subsample and 0.060 for the no-competition subsample, absolute values; the minus signs were lost in PDF text extraction. Event study: "The ETS does not seem to have had any clear effect before 2018." Fig. 5: to Asia, 16% of passengers connect at an ETS hub, 23% at Gulf/Middle East hubs and 7% at non-ETS European hubs. | **Yes, hub passenger shifts** ("hub carbon leakage"). **No** centrality measure. Istanbul is not shown separately. |
| 2 | Dray, L., Doyme, K. (2019). Carbon leakage in aviation policy. *Climate Policy* 19(10), 1284-1296. | 10.1080/14693062.2019.1668745 | VERIFIED | **Policy:** simulated UK-only carbon price, biofuel and landing-charge policies. **Design:** AIM global aviation model with logit itinerary choice. | (abstract) leakage "of between +50 and −150%". (text) transfer passengers switching from UK to non-UK hubs give "around 100% positive leakage". | **Yes**, transfer-hub switching, in simulation only. |
| 3 | Wei, T., Kallbekken, S. (2024). Carbon leakage from aviation under the European Union Fit for 55 policies. *Transportation Research Part D* 132, 104269. | 10.1016/j.trd.2024.104269 | PARTIAL | **Design:** aviation sector model plus CGE. | (abstract) "limited and negative carbon leakage" in the sector model, "high and positive leakage" in the CGE model. No number read. | Not visible from the abstract. |
| 4 | Albers, S., Bühne, J.-A., Peters, H. (2009). Will the EU-ETS instigate airline network reconfigurations? *Journal of Air Transport Management* 15(1), 1-6. | 10.1016/j.jairtraman.2008.09.013 | PARTIAL | **Design:** route cost simulation. | (abstract) at EUR 20/t, cost increases "between €9 and €27 per route", "not high enough to instigate major route reconfigurations". | **Yes**, network reconfiguration, in simulation. |
| 5 | Derigs, U., Illing, S. (2013). Does EU ETS instigate Air Cargo network reconfiguration? A model-based analysis. *European Journal of Operational Research* 225(3), 518-527. | 10.1016/j.ejor.2012.10.016 | PARTIAL | **Design:** cargo network optimisation. | No number read. | **Yes**, cargo network, in simulation. |
| 6 | Redondi, R., Gudmundsson, S.V. (2016). Congestion spill effects of Heathrow and Frankfurt airports on connection traffic in European and Gulf hub airports. *Transportation Research Part A* 92, 287-297. | 10.1016/j.tra.2016.06.011 | PARTIAL | **Shock:** capacity limits, not a tax. **Design:** fixed-effects spill models. **Data:** 9 European and Gulf hubs, 1997-2013. | (abstract) Heathrow spills "strengthen competing hub airports of major alliance groups and to a lesser degree one Gulf hub". No number read. | **Yes**, transfer traffic toward the Gulf. |

**Exists, content not read (check before citing)**
- Scheelhaase, J., Grimme, W., Schaefer, M. (2010). The inclusion of aviation into the EU emission trading scheme: Impacts on competition between European and non-European network airlines. *Transportation Research Part D* 15(1), 14-25. DOI 10.1016/j.trd.2009.07.003. Directly relevant by title.
- Grosche, T., Klophaus, R., Seredyński, A. (2017). Competition for long-haul connecting traffic among airports in Europe and the Middle East. *Journal of Air Transport Management* 64, 3-14. DOI 10.1016/j.jairtraman.2017.06.019.
- Fageda, X., Oesingmann, K. (2024). Is There Carbon Leakage in the European Emissions Trading System? Evidence from Passenger Shifts in the Aviation Market. **Working paper**, SSRN, DOI 10.2139/ssrn.4900468. This looks like the precursor of #1.

## B. EU ETS effects on aviation (no hub outcome)

| # | Citation | DOI | Status | Policy, design, unit | Headline | Hub / centrality? |
|---|---|---|---|---|---|---|
| 7 | Fageda, X., Teixidó, J.J. (2022). Pricing carbon in the aviation sector: Evidence from the European emissions trading system. *Journal of Environmental Economics and Management* 111, 102591. | 10.1016/j.jeem.2021.102591 | VERIFIED | **Policy:** 2013 intra-EEA scope. **Design:** DiD with entropy balancing; treated = intra-EEA routes, control = routes with a non-EEA endpoint. **Data:** 58,239 airline-route pairs, quarterly 2010-2016. | (abstract) emissions down "4.7% in the regulated routes". Table 2: -0.047 (0.018). With only non-EEA-to-non-EEA controls, the effect is "−9.8%". | No. Connection shifts are discussed as a SUTVA threat only. |
| 8 | Fageda, X., Teixidó, J.J. (2025). Technology Diffusion in Carbon Markets: Evidence from Aviation. *Environmental and Resource Economics* 88(12), 3949-3984. | 10.1007/s10640-025-01047-0 | VERIFIED | **Design:** DiD, route level. **Outcomes:** emission intensity, aircraft, winglets. | (text) emission intensity down "2–4% per year". | No. |
| 9 | Kang, Y., Liao, S., Jiang, C., D'Alfonso, T. (2022). Synthetic control methods for policy analysis: Evaluating the effect of the European Emission Trading System on aviation supply. *Transportation Research Part A* 162, 236-252. | 10.1016/j.tra.2022.05.015 | PARTIAL | **Design:** modified synthetic control. **Data:** airline-route seats, frequency, aircraft size. | (abstract) seat capacity cut "reaching above 20% at its peak"; largest effects on "spoke–spoke markets". | Partly: hub versus non-hub route split, no centrality outcome. |
| 10 | Oesingmann, K. (2022). The effect of the European Emissions Trading System (EU ETS) on aviation demand: An empirical comparison with the impact of ticket taxes. *Energy Policy* 160, 112657. | 10.1016/j.enpol.2021.112657 | PARTIAL | **Design:** PPML gravity on country-pair passengers. **Policies:** ETS plus the German and Austrian ticket taxes. | (abstract) no significant ETS effect; ticket taxes give "statistically significant and robust demand reductions". No number read. | No. |
| 11 | Fageda, X., Oesingmann, K. (2025). The impact of carbon pricing on tourist destinations: Shifts in demand, supply and emissions in the European aviation market. *Economics of Transportation* 42, 100414. | 10.1016/j.ecotra.2025.100414 | VERIFIED | **Design:** DiD on an entropy-balanced sample. **Data:** routes from Europe to tourist destinations, 2010-2022; Turkey is among the non-EEA destinations. | (text) emissions "about −7 %" on non-stop routes; passengers "around −1 %/−2 %", never significant. | No. |
| 12 | Anger, A. (2010). Including aviation in the European emissions trading scheme: Impacts on the industry, CO2 emissions and macroeconomic activity in the EU. *Journal of Air Transport Management* 16(2), 100-105. | 10.1016/j.jairtraman.2009.10.009 | PARTIAL | Ex ante E3ME simulation. | (abstract) CO2 down "up to 7.4%". | No. |
| 13 | Vespermann, J., Wald, A. (2011). Much Ado about Nothing? An analysis of economic impacts and ecologic effects of the EU-emission trading scheme in the aviation industry. *Transportation Research Part A* 45(10), 1066-1076. | 10.1016/j.tra.2010.03.005 | PARTIAL | Ex ante simulation. | (abstract) "only low competition distortions". No number read. | No. |
| 14 | Zhang, Y., Wang, K. (2024). Mitigation effect of the European Union emission trading system on aviation emissions. *Transportation Research Part D* 130, 104186. | 10.1016/j.trd.2024.104186 | EXISTS | Not read. | No number read. | Unknown. |

## C. National ticket and passenger taxes

| # | Citation | DOI | Status | Policy, design, unit | Headline | Hub / transfer / leakage? |
|---|---|---|---|---|---|---|
| 15 | Bernardo, V., Fageda, X., Teixidó, J. (2024). Flight ticket taxes in Europe: Environmental and economic impact. *Transportation Research Part A* 179, 103892. | 10.1016/j.tra.2023.103892 | VERIFIED | **Policies:** Germany, Austria, Norway, Sweden. **Design:** staggered DiD (Callaway-Sant'Anna) with entropy balancing. **Data:** 61,964 airline-route pairs, 2007-2019. | (abstract) flights per airline-route down 12% and CO2 down 14% for low-cost airlines. (text) whole-market effect "about 4%"; network airlines not significant, "as connecting passengers are exempt". | Transfer exemption is central to the design; border-airport leakage tests show "virtually the same" results. |
| 16 | Helmers, V., van der Werf, E. (2025). Did the German aviation tax have a lasting effect on passenger numbers? *Transportation Research Part D* 140, 104570. | 10.1016/j.trd.2024.104570 | VERIFIED | **Policy:** Germany 2011. **Design:** event-study panel with 5 estimators and 175 specifications. **Data:** 289 airports. | (abstract) "6–11% reduction" in departing passengers in the first two years; no significant effect in 2013 across specifications. | Hubs re-estimated separately because transfer passengers are untaxed (Frankfurt 53.7% transfer share). |
| 17 | Borbely, D. (2019). A case study on Germany's aviation tax using the synthetic control approach. *Transportation Research Part A* 126, 377-395. | 10.1016/j.tra.2019.06.017 | VERIFIED (accepted manuscript) | **Design:** synthetic control per airport. **Data:** Eurostat airport passengers, 2003-2015. | (text) about 4 million passengers lost per year, "roughly 2%". Hubs show small negative or positive effects. | Leakage to foreign border airports: yes. Transfer traffic: discussed, not measured. |
| 18 | Falk, M., Hagsten, E. (2019). Short-run impact of the flight departure tax on air travel. *International Journal of Tourism Research* 21(1), 37-44. | 10.1002/jtr.2239 | PARTIAL | **Policies:** Germany and Austria 2011. **Design:** dynamic panel DiD. **Data:** 310 airports. | (abstract) passengers down "9% in the year of introduction and 5% in the subsequent year"; "regular hubs are not affected". | Hub versus low-cost airport split only. |
| 19 | Wozny, F. (2024). Tax Incidence in Heterogeneous Markets: The Pass-through of Air Passenger Taxes on Airfares. **Working paper**, IZA DP 16783. | 10.2139/ssrn.4717696 | VERIFIED (WP) | **Policy:** Sweden 2018. **Design:** DiD against Denmark and Finland. **Data:** Sabre itineraries, 2015-2019. | (text) fares up 5.7%, passengers down 9.1%, elasticity -1.59. | Transfer exemption noted; hub shifts not tested. |
| 20 | Stråle, J. (2021). The Effects of the Swedish Aviation Tax on the Demand and Price of International Air Travel. **Working paper**, SLU Dept. of Economics WP 2021:02. | none (refcheck not found; PDF read on the SLU repository) | VERIFIED (WP) | **Design:** synthetic control, quarterly. | (text) effect rises from 4.4% to about 11%; (abstract) "no 'leakage effect'". | Tested border leakage: none found. |
| 21 | Seetaram, N., Song, H., Page, S.J. (2014). Air Passenger Duty and Outbound Tourism Demand from the United Kingdom. *Journal of Travel Research* 53(4), 476-487. | 10.1177/0047287513500389 | VERIFIED (accepted manuscript) | **Policy:** UK APD. **Design:** ARDL by destination, 1994-2010. | (text) APD negative and significant in 5 of 10 destinations; tax elasticities below one in absolute value. Destination numbers not read (table is an image). | No. |
| 22 | Mayor, K., Tol, R.S.J. (2007). The impact of the UK aviation tax on carbon dioxide emissions and visitor numbers. *Transport Policy* 14(6), 507-513. | 10.1016/j.tranpol.2007.07.002 | PARTIAL | Simulation (Hamburg tourism model). | (abstract) APD doubling slightly increases CO2. No number read. | No. |
| 23 | Seetaram, N., Song, H., Ye, S., Page, S. (2018). Estimating willingness to pay air passenger duty. *Annals of Tourism Research* 72, 85-97. | 10.1016/j.annals.2018.07.001 | PARTIAL | Stated preference. | No number read. | No. |
| 24 | Gordijn, H., Kolkman, J. (2011). *Effects of the Air Passenger Tax.* KiM Netherlands Institute for Transport Policy Analysis, ISBN 978-90-8902-086-4. **Grey literature.** | none | VERIFIED (report) | **Policy:** Netherlands 2008-09. **Design:** descriptive, survey, bookings. | (summary) about 2 million fewer Schiphol passengers; about 1 million Dutch passengers moved to foreign airports. Transfer passengers, untaxed, "continued to increase". | Yes: leakage to Düsseldorf, Weeze and Brussels. Transfer traffic described only. |
| 25 | Bilotkach, V., Polk, A. (2013). Market Power of Airports: A Case Study for Amsterdam Airport Schiphol. *Competition and Regulation in Network Industries* 14(4), 320-337. | 10.1177/178359171301400401 | PARTIAL | Uses the Dutch tax as a natural experiment. | No number read. | Possibly origin-destination versus transfer markets; not confirmed. |
| 26 | Markham, F., Young, M., Reis, A., Higham, J. (2018). Does carbon pricing reduce air travel? Evidence from the Australian 'Clean Energy Future' policy. *Journal of Transport Geography* 70, 206-214. | 10.1016/j.jtrangeo.2018.06.008 | PARTIAL | Time series, domestic Australia. | (abstract) no evidence of a reduction. | No. |
| 27 | Brons, M., Pels, E., Nijkamp, P., Rietveld, P. (2002). Price elasticities of demand for passenger air travel: a meta-analysis. *Journal of Air Transport Management* 8(3), 165-175. | 10.1016/S0969-6997(01)00050-3 | VERIFIED (discussion-paper version) | Meta-analysis of 37 studies. | (DP text) mean price elasticity -1.146. | No. |
| 28 | Larsson, J., Elofsson, A., Sterner, T., Åkerman, J. (2019). International and national climate policies for aviation: a review. *Climate Policy*. | 10.1080/14693062.2018.1562871 | PARTIAL | Qualitative review. | No pooled number. | No. |
| 29 | Bernardo, V., Fageda, X., Labandeira, X., Teixidó, J.J. (2026). Aligning the Aviation Industry with Global Climate Goals: The Role of Pricing Mechanisms. *Review of Environmental Economics and Policy* 20(2), 216-239. | 10.1086/742030 | EXISTS | Review. | Not read. | Unknown. |

## D. Network centrality or connectivity as a policy outcome (not taxes)

| # | Citation | DOI | Status | Shock and design | Headline | Centrality? |
|---|---|---|---|---|---|---|
| 30 | Spence, T.B., Choi, Y. (2025). Unpacking the digital divide: Heterogeneous effects of open sky agreements on air transport network centrality amid internet regulation constraints. *Transport Policy* 168, 207-219. | 10.1016/j.tranpol.2025.04.016 | PARTIAL | US open skies agreements; country panel. | (abstract) "a significant positive effect on network centrality over time". No number read. | **Yes**, centrality is the outcome. |
| 31 | Morandi, V., Malighetti, P., Paleari, S., Redondi, R. (2014). EU-US Open Skies Agreement: What Is Changed in the North Transatlantic Skies? *Transportation Journal* 53(3), 305-329. | 10.5325/transportationj.53.3.0305 | PARTIAL | Before/after comparison. | (abstract) direct connections fell, indirect competition rose. No number read. | Yes, connecting-market competition. |
| 32 | Martín-Domingo, L., Ersöz, C., Martin, J.C. (2026). Changes in Russian air connectivity in response to airspace restrictions. *Asian Geographer* 43(2), 131-153. | 10.1080/10225706.2026.2660101 | PARTIAL | 2022 airspace sanctions; descriptive OAG analysis. | (abstract) international capacity down 41% at first, then "only a 4% overall decrease"; Istanbul and Dubai benefited. | Yes, connectivity (descriptive). |
| 33 | Suau-Sanchez, P., Voltes-Dorta, A., Rodríguez-Déniz, H. (2017). Benchmarking Worldwide Airport Connectivity with Demand Data: Global Hub Competition, New Players, and the Hidden Potential of Self-connectivity. In *The Economics of Airport Operations* (Emerald), 387-423. **Book chapter.** | 10.1108/s2212-160920170000006015 | PARTIAL | MIDT 2012-2015; connectivity indices. | (abstract) European hubs "have lost traffic in global markets" to Middle East carriers. Descriptive. | Yes, connectivity indices. |

## Flagged or dropped

- **Gurr and Moser (2017)**, *Zeitschrift für Verkehrswissenschaft*. Not found by refcheck; known only secondhand. Do not cite.
- **Koopmans and Lieshout (2016)**, *JATM* 53, 1-11, DOI 10.1016/j.jairtraman.2015.12.013. Exists. Whether it studies the Dutch tax is unconfirmed.
- **Collet, Quirion and Taconet (2023)**, SSRN working paper, DOI 10.2139/ssrn.4499806. Exists, not read.
- **Transport & Environment (2026)** briefing on recent ticket taxes. NGO grey literature, not peer reviewed.
- **No peer-reviewed empirical study was found** for:
  - the Northern Ireland or Scotland APD changes;
  - the Italian municipal surcharge, the French solidarity tax or Belgium;
  - the 2021 Dutch reintroduction.

---

## Gap for our paper

Only one paper estimates hub-function relocation caused by EU carbon pricing: Fageda and Oesingmann (2025, TRA, #1). It finds that passengers connecting at ETS hubs fall about 4% when the allowance price doubles, with part of the loss going to routings via non-ETS hubs. It has four limits:
- Its unit is origin-hub-destination passenger flows for 2010-2023.
- It shows effects only from 2018.
- It does not measure network centrality.
- It does not separate Istanbul from the Gulf hubs or include national ticket taxes.

Other hub-leakage evidence is simulation only: Dray and Doyme 2019, Wei and Kallbekken 2024, Albers et al. 2009, and Derigs and Illing 2013.

The ticket-tax papers measure leakage only as substitution to nearby EU border airports. Because transfer passengers are exempt, they treat hubs as unaffected; none tests a shift of transfer traffic to Istanbul or the Gulf.

Network centrality appears as a policy outcome only for open skies, capacity spills and airspace sanctions.

**No study found here uses airport betweenness or eigenvector centrality (or a GACI-type index) of European versus Istanbul and Gulf hubs as the outcome of EU ETS scope changes, allowance prices or ticket taxes over a long panel such as 1996-2024.**

The policy relevance is new. The Commission's 17 July 2026 proposal (COM(2026) 616) explicitly targets "hub leakage" by covering departing flights to non-EEA airports within 5,000 km of Frankfurt from 2029. Istanbul, Doha, Dubai and Abu Dhabi all fall inside that band (see `data_sources.md`, section 4).
