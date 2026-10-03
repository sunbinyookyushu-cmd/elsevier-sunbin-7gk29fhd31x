# Strand 1B: UK APD, Irish ATT, Sweden, Norway, France, Italy, Denmark, Australia, and cross-country ticket-tax panels

Compiled 2026-10-02 for the GACI ticket-tax / EU ETS hub-displacement paper (target: Energy Economics).

Conventions used in this file
- VERIFIED = I read the method and results sections myself (URL given). PARTIAL = abstract, highlights or summary only; unread fields are marked "not read".
- Numbers, table numbers and page numbers are copied exactly from the source. Sentences are paraphrased (not quoted) to keep verbatim reproduction of copyrighted text to a minimum; where a number is reported the location is given so it can be checked.
- Search context: the WebSearch budget for this session was exhausted before this strand started, so discovery used refcheck (Crossref / Semantic Scholar), the OpenAlex and Crossref APIs, HAL, publisher pages and repository pages. Sites behind bot checks (SSRN, Wiley full text, research.slu.se files, doria.fi, mediaTUM) were not bypassed.
- Coverage overlap: German and Austrian taxes (Borbely 2019, Helmers and van der Werf 2025, Falk and Hagsten 2019, Wozny 2024) and the Dutch 2008 tax belong mainly to the other strand; Falk and Hagsten is listed here only because it is a 30-country airport panel that later papers use for the displacement buffer.

---

## 1. Bernardo, Fageda and Teixido (2024), cross-country staggered DiD, airline-route level

1. Citation: Bernardo, V., Fageda, X., Teixido, J. (2024). Flight ticket taxes in Europe: Environmental and economic impact. Transportation Research Part A: Policy and Practice 179, 103892. DOI 10.1016/j.tra.2023.103892. Open access (CC BY-NC). Verified: refcheck verdict "verified" (Crossref), no discrepancies. Earlier version: SSRN 10.2139/ssrn.4124321 (2022).
2. Access: VERIFIED. Read full text (Sections 1-3, Tables 1-6, Figs 1-6 captions) at https://www.sciencedirect.com/science/article/pii/S0965856423003129 . Section 4 (pass-through) only partly read; appendix tables not read.
3. Policy, countries, period: national ticket taxes in Europe. Identification comes from Germany (Jan 2011), Austria (Jan 2011), Norway (2016) and Sweden (Apr 2018), the taxes observed with a pre-period and not abolished in-sample. Sample 2007-2019 (2019 cutoff to avoid COVID). Their Table 1 also dates Italy 1993, UK APD 1998 (sic, APD began Nov 1994 per Seetaram et al.), France 1999/2006, Malta 2001 to Nov 2008, Netherlands Jul 2008 to Jul 2009 and 2021, Ireland Mar 2009 to Apr 2014 (EUR 10, cut to EUR 3 in Mar 2011), Portugal Jul 2021, Norway "January 2016".
4. Data: RDC Aviation Apex-Schedules (seats, frequencies, aircraft type, distance) and Apex-Fares; CO2 from Eurocontrol Small Emitter Tool. Unit = airline x route, route = city pair (multi-airport cities merged). Monthly data for 61,964 airline-route pairs in EEA + UK, 2007-2019, collapsed to annual for supply and emissions; fares for 15,238 airline-route pairs 2013-2019. Outcomes: ln(flights), ln(CO2), fares (quantile pass-through). Covariates: population-weighted O-D income and population (Eurostat NUTS3), route HHI. OAG MIDT 2016 used descriptively for transfer shares of network carriers (Fig. 1).
5. Identification: staggered DiD. TWFE with airline-route and year FE (Eq. 1a/1b, dummy TAX_it), plus Callaway and Sant'Anna (2021) ATT with doubly robust estimator (Sant'Anna and Zhao 2020) and entropy balancing (Hainmueller 2012) on 2008-2010 covariates (distance, income, population, HHI, flights). Main sample = low-cost carriers (connecting passengers are exempt from almost all taxes). Semi-elasticity version with tax amount in euros (Table A4, TWFE): about 1% fewer flights per extra euro (appendix, not read directly; reported in Section 3 text).
6. Control group and displacement: treated = airline-routes with an endpoint in a taxing country (tax applies to departures only, both directions assumed affected). Control = routes with no tax at either endpoint. UK, France and Italy (taxes since the 1990s) are kept in the control group in the main estimates (excluded in Table A2); Ireland, Netherlands and Malta are dropped because their taxes were abolished (estimator assumes irreversible treatment). Displacement: SUTVA check (Table 4) drops control airports within about two hours' drive (normally under 150 km) of a taxing country's border, following Borbely (2019) and Falk and Hagsten (2019); mainly removes airports near German and Austrian borders.
7. Timing and anticipation: annual treatment dummy; event study (Fig. 5) shows flat pre-trends and an effect that builds gradually over years; quarterly CS estimates (Table 3, Fig. 6) show slower build-up in Q1. Anticipation not modelled in the parts I read.
8. Inference: robust SE clustered at route level in every table; number of clusters not reported in the parts read; no wild bootstrap or permutation test seen. Note: treatment varies at country level (4 treated countries) but clustering is by route.
9. Headline (Table 2, col 4, CS estimator, LCC sample, N = 27,116): ln(Flights) -0.122*** (0.024); ln(Emissions) -0.140*** (0.024). TWFE cols 1-3: flights -0.090, -0.085, -0.162; emissions -0.127, -0.121, -0.194. By carrier type (Table 5, CS): low-cost -0.122***, network -0.011 (0.020, not significant), all airlines -0.042*** (0.012). SUTVA sample (Table 4): flights -0.125*** (0.025), emissions -0.143*** (0.025). Heterogeneity (Table 6): competitive routes (HHI < 0.47) -0.172***; monopoly routes -0.109***; airlines with route share < 24.6% -0.227***. Pass-through medians 20% to 56% (Section 1 summary).
10. Transfer / hub: yes, indirectly. Fig. 1 (OAG traffic analyser 2016) shows high transfer shares for Lufthansa, KLM, Austrian, SAS; network carriers show no response because transfer passengers are exempt. No airport centrality or connectivity measure.
11. Lesson: the frontier design (CS + entropy balancing at route level) finds the tax bites on LCC point-to-point capacity, not on network carriers at hubs; our hub-centrality outcome may therefore respond weakly at primary hubs and more at LCC-heavy secondary airports, so split OAG seats by carrier type and use the abolitions they discarded (IE 2014, NL 2009, MT 2008) with an on/off estimator; also replace the crude 150 km SUTVA buffer with explicit network-level reallocation.

---

## 2. Oesingmann (2022), country-pair gravity (PPML), EU ETS plus DE/AT ticket taxes

1. Citation: Oesingmann, K. (2022). The effect of the European Emissions Trading System (EU ETS) on aviation demand: An empirical comparison with the impact of ticket taxes. Energy Policy 160, 112657. DOI 10.1016/j.enpol.2021.112657. Verified: refcheck "verified" (Crossref).
2. Access: PARTIAL. Read highlights, abstract, introduction and section snippets at https://www.sciencedirect.com/science/article/abs/pii/S030142152100522X (paywalled; no OA copy found; DLR elib and mediaTUM records have no full text or are bot-protected).
3. Policy, countries, period: EU ETS for aviation (from 2012) on intra-EEA flows, controlling for the Austrian and German air transport taxes. Period: not read.
4. Data: country-pair air passenger flows (source not read); regressors mentioned in the snippet include GDP, temperature differences, colonial ties, common language, EEA membership, cost developments.
5. Identification: structural gravity estimated by PPML with fixed effects; ETS dummy and tax variables; the paper discusses how fixed effects should be adapted to aviation. Exact FE structure: not read.
6. Control group / displacement: implicit (non-ETS and non-taxed pairs); displacement handling not read.
7. Timing / anticipation: not read.
8. Inference: not read.
9. Headline (abstract and highlights, no coefficients read): ETS has no statistically significant effect on intra-EEA passenger flows; ticket taxes give significant and robust demand reductions on affected country pairs; replacing policy dummies with passenger- and route-specific variables reduces the estimated policy impacts (highlight 3). Coefficients: not read.
10. Transfer / hub: not read (country-pair data cannot see hubs).
11. Lesson: the only Energy-Policy-level evidence comparing ETS and ticket taxes in one model; it signals that dummy vs intensity coding changes the magnitude, which supports our continuous-treatment design for the ETS (cost per passenger) rather than a 2012 dummy; country-pair gravity cannot see hub rerouting, which is our gap.

---

## 3. Falk and Hagsten (2019), 310-airport, 30-country dynamic panel DiD (DE/AT taxes)

1. Citation: Falk, M., Hagsten, E. (2019). Short-run impact of the flight departure tax on air travel. International Journal of Tourism Research 21(1), 37-44. DOI 10.1002/jtr.2239. First published online 3 Oct 2018 (refcheck flags year 2018 vs issue year 2019; same article). Verified: refcheck "verified"; Wiley abstract page.
2. Access: PARTIAL. Abstract only at https://onlinelibrary.wiley.com/doi/abs/10.1002/jtr.2239 (full text blocked).
3. Policy, countries, period: German and Austrian departure taxes introduced 2011; 310 airports in 30 European countries; 2008-2016.
4. Data: airport-level passenger numbers (source not read), annual.
5. Identification: dynamic panel difference-in-differences (exact specification not read).
6. Control group / displacement: non-taxed European airports. Per Bernardo et al. (2024, Section 3) Falk and Hagsten treat airports within about two hours' drive of the taxing country as potentially affected and find no relevant border effects (secondhand; not read in the original).
7. Timing: year-of-introduction and following-year effects reported; anticipation not read.
8. Inference: not read.
9. Headline (abstract): passengers fall by 9% in the year of introduction and 5% in the following year; the reduction is driven by airports mainly served by low-cost airlines, while regular hubs are not affected.
10. Transfer / hub: yes, a split between LCC-dominated airports and hubs (hubs unaffected). No network centrality.
11. Lesson: airport-level panels across 30 countries are feasible and show hubs are insulated; our airport x year centrality panel extends this to network position, and their two-hour border buffer is the convention reviewers will expect us to improve on.

---

## 4. Mayor and Tol (2007), UK APD doubling, global tourism simulation

1. Citation: Mayor, K., Tol, R.S.J. (2007). The impact of the UK aviation tax on carbon dioxide emissions and visitor numbers. Transport Policy 14(6), 507-513. DOI 10.1016/j.tranpol.2007.07.002. Verified: refcheck "verified" (Crossref, Semantic Scholar), no discrepancies.
2. Access: VERIFIED (working-paper version). Read the full ESRI Working Paper No. 187 (April 2007), which states it was subsequently published as the Transport Policy article: https://www.esri.ie/pubs/WP187.pdf
3. Policy, country, period: UK Air Passenger Duty; scenarios = original APD 2001-2007, doubled APD from February 2007, abolition, the Conservative "green air miles" proposal, and a revenue-equivalent emissions tax. Results shown for 2010.
4. Data: Hamburg Tourism Model version 1.3 (domestic and international tourists from 207 countries; WTO 2003 and Euromonitor 2002 data; behaviour estimated for 1995). Travel cost assumed linear in distance using Heathrow data. Outcomes: tourist arrivals by destination, CO2 from tourist air travel. Tourism only (no business, no domestic air).
5. Identification: simulation. Airfare elasticity of destination choice -1.50 + 0.14 ln y (y = origin income per capita), which gives -0.45 for UK travellers (Section 2). Weighted APD used: GBP 5.50 EU/EEA and GBP 22.00 other (Section 3.1, footnote 2).
6. Control / displacement: no control group. Displacement is across destinations (near to far) and is reported by distance band (Fig. 2); no airport choice, so no leakage to foreign airports is possible in the model.
7. Timing: comparative statics for 2010; no anticipation.
8. Inference: none (deterministic); sensitivity with price elasticity -0.58 and -0.68 and with domestic/international substitution (Section 4, Fig. 4).
9. Headline (Section 3.2, WP pp. 5-6): doubling APD reduces international arrivals in the UK by about 163,000 in 2010, a 0.4% reduction; abolition raises arrivals by about 169,000 per year; under base assumptions doubling slightly raises emissions because a flat per-passenger tax raises near destinations' relative price; the sign reverses if domestic and foreign holidays are close substitutes.
10. Transfer / hub: no.
11. Lesson: a flat or banded per-passenger tax shifts the distance mix of trips, so route-length heterogeneity (APD distance bands from 2009) should enter our treatment intensity, and passenger counts alone can miss composition shifts that matter for network centrality.

---

## 5. Seetaram, Song and Page (2014), UK APD, destination-level ARDL time series

1. Citation: Seetaram, N., Song, H., Page, S.J. (2014). Air passenger duty and outbound tourism demand from the United Kingdom. Journal of Travel Research 53(4), 476-487. DOI 10.1177/0047287513500389. Online 2013 (refcheck flags 2013 vs 2014; same article). Verified: refcheck "verified".
2. Access: VERIFIED for text, tables missing. Read the full accepted preprint (June 2013) at http://eprints.bournemouth.ac.uk/22553/1/Air%20Passenger%20Duty%20and%20UK%20Tourism_revise%20June2013.pdf . The preprint says "Insert Table 3/4 here", so destination-specific coefficients were not available to me.
3. Policy, country, period: UK APD from 1 Nov 1994; quarterly 1994Q4-2010Q4. APD history in Section 2: GBP 5 (UK/EU) and GBP 10 (other) in 1994, doubled three years later, class split and reform in 2001, doubled in 2007, four distance bands from 2009.
4. Data: ONS Quarterly Overseas Travel and Tourism (UK resident departures, all transport modes) to 10 destinations (France, Germany, Spain, Italy, Greece, Turkey, Egypt, US, Hong Kong, Australia; about 58% of UK outbound); APD reduced rates from HMRC; GDP, CPI, exchange rates from IMF.
5. Identification: single-equation ARDL per destination with bounds test (Pesaran, Shin and Smith 2001), log-log, lag length by AIC, general-to-specific, seasonal and event dummies (9/11, SARS, 2008 crisis, 1995 French strikes). APD enters as a log level regressor.
6. Control / displacement: none; the authors note that departures include non-air modes and that geographical displacement is unresolved (Section 5).
7. Timing: tax changes enter through the APD series; anticipation not addressed.
8. Inference: time-series diagnostics only (LM serial correlation, RESET, heteroskedasticity); several destination models fail one or two tests (France, Spain, Italy, Greece).
9. Headline (abstract and Section 4.2, text): APD coefficient negative and significant (5% or 10%) for 5 of 10 destinations; all absolute tax elasticities below 1; income elasticities 0.36 to 4.11; own-price elasticities -0.05 to -2.02 (Table 4, not seen).
10. Transfer / hub: no.
11. Lesson: national time series cannot separate APD changes from macro shocks; the UK's repeated APD changes (1994, 1997, 2001, 2007, 2009 bands, later NI and Scottish carve-outs) are better used as intensity shocks in a panel with untaxed comparison airports.

---

## 6. Veldhuis and Zuidberg (2009), Irish Air Travel Tax, airline-commissioned scenario study (SEO)

1. Citation: Veldhuis, J., Zuidberg, J. (2009). The Implications of the Irish Air Travel Tax. SEO-rapport 2009-77, SEO Economic Research (Amsterdam Aviation Economics), Amsterdam, November 2009. ISBN 978-90-6733-530-0. Commissioned by Aer Lingus, Ryanair and CityJet. Verified: SEO publication page and UvA-DARE record (dare.uva.nl/record/1/319575); report, not peer reviewed.
2. Access: VERIFIED. Read full report: https://www.seo.nl/wp-content/uploads/2020/04/2009-77_The_Implications_of_the_Irish_Air_Travel_Tax.pdf
3. Policy, country, period: Irish ATT from 30 March 2009, EUR 10 per departing passenger to airports more than 300 km from Dublin, EUR 2 within 300 km (domestic plus Cardiff, Glasgow, Prestwick, Liverpool, Manchester, Blackpool, Isle of Man); transit and transfer exempt. Base year 2008, observed capacity to summer and September 2009.
4. Data: confidential airline data (passengers, yields by 10 O-D regions), OAG departing seats 2008 by airport (Dublin, Shannon, Cork, others; Table 3.1), OAG September 2009 capacity, 2009 airport charges (Dublin, Cork, Shannon), Irish Tourist Industry Confederation spend data.
5. Identification: scenario model, not econometric. Scenario 1 = full pass-through with elasticities -1 (leisure) and -0.3 (business), sensitivity -0.5 to -1.5 for Ryanair. Scenario 2 = observed capacity cuts since the tax plus 50-95% tax absorption.
6. Control / displacement: no control group. Attributes Irish capacity cuts to the tax by contrasting Ryanair's network-wide traffic growth (+17% in September 2009) with Irish departing capacity (-16.1%), i.e. capacity redeployed to untaxed EU bases; also notes Aer Lingus growth at London Gatwick. Recession not separately controlled.
7. Timing: first months after introduction; anticipation not considered.
8. Inference: none.
9. Headline: Table 4.2, demand loss of 870,000 departing passengers per year (three airlines, full pass-through). Table 5.2, demand loss of 1,331,000 departing passengers per year from capacity cuts as of summer 2009. Section 5.1: Irish departing capacity -16.1% (Sept 2009 vs Sept 2008), Dublin, Shannon and Cork down 16% to 20%; Ryanair winter capacity about 20% lower; planned 75% cut of Ryanair presence at Shannon.
10. Transfer / hub: connectivity discussed qualitatively (Section 5.3); transfer exemption noted; no network measure.
11. Lesson: the main margin for LCCs is base and seat reallocation across countries, which our airport x month OAG seats can test directly; the Irish ATT (2009 introduction, 2011 cut to EUR 3, 2014 abolition) is a three-step on/off treatment, but the 2009 recession must be absorbed by untaxed comparison airports (UK regions, other EU) rather than asserted away as here.

---

## 7. Strale (2021), Swedish aviation tax, synthetic control plus IV price elasticity

1. Citation: Strale, J. (2021). The Effects of the Swedish Aviation Tax on the Demand and Price of International Air Travel. Working Paper Series 2021:02, Department of Economics, Swedish University of Agricultural Sciences (SLU), Uppsala. No DOI. Author spelling: Jonathan Stråle. Verified: SLU research portal record; also Paper II of his SLU doctoral thesis "Travel demand and environmental policy" (2022, ISBN 978-91-7760-923-0). Not peer reviewed as far as I could find.
2. Access: PARTIAL. Read the abstract at https://research.slu.se/en/publications/the-effects-of-the-swedish-aviation-tax-on-the-demand-and-price-o/ and the thesis summary; the PDF (research.slu.se/files/19142715/fulltext.pdf) sits behind a bot check and was not opened.
3. Policy, country, period: Swedish aviation tax (from 1 April 2018); period not read.
4. Data: international air passengers from Sweden; web-scraped route-level price data; other sources not read.
5. Identification: synthetic control for passengers and prices; IV estimation of the price elasticity to handle price-quantity simultaneity. Donor pool not read.
6. Control / displacement: tests for leakage to neighbouring countries and finds none (abstract). How leakage was measured: not read.
7. Timing: effects on passengers grow over time after introduction while price effects start high and fade (abstract). Also tests a "Greta Thunberg" effect and finds no direct evidence.
8. Inference: not read.
9. Headline (abstract): price elasticity of international air travel from Sweden -0.76; with the tax's price effect this explains the fall in international travel in the first three quarters, and the later growing gap is read as a "symbol" effect. Secondhand from Lorner and Jedvik (2026, Section 3): about 4% initially, rising to about 10% (not checked in the original).
10. Transfer / hub: not read.
11. Lesson: the Swedish tax coincides with the 2018-2019 "flight shame" period, so country-level effects mix price and norm channels; an explicit leakage test toward Copenhagen and Oslo is the comparison our network design can do better, but Oslo is itself taxed from 2016 and so cannot be a clean control for Sweden.

---

## 8. Lorner and Jedvik (2026), Norwegian 2016 tax, synthetic control on Oslo Gardermoen (bachelor thesis)

1. Citation: Lorner, J., Jedvik, S. (2026). Flying under the radar? A synthetic control study on the Norwegian aviation tax's effect on international departing passengers from Oslo's airport. Examensarbete C (bachelor-level thesis), Department of Economics, Uppsala University, spring term 2026; supervisor Torben Mideksa. DiVA urn:nbn:se:uu:diva-594338. Verified: DiVA record and PDF title page. Student thesis, not peer reviewed; low weight.
2. Access: VERIFIED. Read data, method, results and robustness sections: https://uu.diva-portal.org/smash/get/diva2:2087414/FULLTEXT01.pdf
3. Policy, country, period: Norwegian Flypassasjeravgift, NOK 80 per departing passenger, effective 1 June 2016 (transfer and transit exempt); destination split from 2019 (NOK 75 Europe, NOK 200 outside); quarterly 2010Q1-2019Q4.
4. Data: Eurostat passengers carried (departures) to international destinations by capital-city airport; predictors GDP per capita PPP (OECD), HICP passenger transport by air (Eurostat), urban population share (OWID, linearly interpolated), lagged outcomes; 520 observations.
5. Identification: synthetic control (Abadie). Donor pool of 12 capitals (Brussels, Prague, Copenhagen, Tallinn, Helsinki, Budapest, Riga, Vilnius, Warsaw, Bratislava, Ljubljana, Bern); excluded capitals with an aviation tax in the period, island capitals, high-tourism capitals (Madrid) and capitals with missing data.
6. Control / displacement: Table 2 weights: Tallinn 0.252, Helsinki 0.189, Copenhagen 0.185, Brussels 0.147, Warsaw 0.141, Bern 0.086. Copenhagen, a plausible recipient of diverted Norwegian traffic, carries 18.5% of the weight, so leakage would bias the gap toward a larger negative effect; the authors argue Norway's geography limits cross-border avoidance but do not test it.
7. Timing and anticipation: in-time placebos at 2013Q3 and 2014Q3 (before public debate) show no divergence (Section 7.1).
8. Inference: in-space placebo with donors whose pre-RMSPE is within 25% of Oslo's; RMSPE-ratio permutation p-value 0.333 (Section 7.3); leave-one-out dropping Tallinn, Helsinki, Copenhagen (Section 7.2).
9. Headline (Section 6, pp. 23-24): average post-treatment gap of -76,547 international departing passengers, about 0.27% of post-period departures, not statistically significant (p = 0.333).
10. Transfer / hub: no; passengers carried include transfer passengers at Gardermoen, who are tax-exempt, which dilutes the treatment.
11. Lesson: with about 12 donors the smallest attainable permutation p-value is about 0.08, so single-airport synthetic controls are underpowered; donor pools must exclude airports that can absorb displaced traffic, which is exactly the network spillover our design should model rather than assume away.

---

## 9. Warras (2020), Norway 2016 and Sweden 2018 taxes, airport-level dynamic DiD (thesis)

1. Citation: Warras, E. (2020). Do the aviation taxes in Norway and Sweden decrease passenger numbers. Thesis deposited in Doria (Finnish national repository), handle 10024/177518. OpenAlex classes it as a dissertation from University of Helsinki; degree level and exact institution not confirmed by me. Not peer reviewed; low weight.
2. Access: PARTIAL. Abstract via OpenAlex record for https://www.doria.fi/handle/10024/177518 ; the Doria page and PDF are behind a bot check and were not opened.
3. Policy, countries, period: Norwegian tax (2016) and Swedish tax (2018); 2011-2019.
4. Data: 129 airports; passenger numbers; source and frequency not read.
5. Identification: dynamic difference-in-differences (specification not read).
6. Control / displacement: control airports not read; low-cost airports analysed separately.
7. Timing: not read.
8. Inference: not read.
9. Headline (abstract): no significant effect on total passengers in either country, and none at low-cost airports; for domestic travel, Swedish domestic travel from airports with low-cost presence falls by over 10%, and Norwegian domestic travel falls by 24%.
10. Transfer / hub: no.
11. Lesson: the only multi-airport DiD found for the two Nordic taxes; its domestic-only effect is consistent with international demand being able to divert or being less price sensitive, so separating domestic, intra-Europe and long-haul seats in our OAG data matters.

---

## 10. Forsyth, Dwyer, Spurr and Pham (2014), Australia's Passenger Movement Charge, CGE

1. Citation: Forsyth, P., Dwyer, L., Spurr, R., Pham, T. (2014). The impacts of Australia's departure tax: Tourism versus the economy? Tourism Management 40, 126-136. DOI 10.1016/j.tourman.2013.05.011. Verified: refcheck "verified" (Crossref, Semantic Scholar), no discrepancies.
2. Access: PARTIAL. Read highlights, abstract, introduction and section snippets at https://www.sciencedirect.com/science/article/abs/pii/S0261517713001179 (paywalled; Griffith repository record had no accessible file).
3. Policy, country, period: increase of Australia's Passenger Movement Charge from AUD 47 to AUD 55 (+17%) from 1 July 2012.
4. Data: national tourism flows and expenditure (inbound, outbound, domestic); snippet cites 2010-11 PMC revenue of AUD 615.47 million and 5.5 million inbound tourists.
5. Identification: ex-ante computable general equilibrium model (model name not confirmed in what I read), with assumed price elasticities of -0.5 and -1.0 (Table 1 per snippet).
6. Control / displacement: not applicable; substitution from outbound to domestic tourism is modelled; no alternative foreign airports.
7. Timing: not applicable.
8. Inference: none.
9. Headline (abstract): the tourism industry loses while the Australian economy gains (GNI and welfare), mainly because part of the tax is paid by foreign visitors. Numerical results: not read.
10. Transfer / hub: no.
11. Lesson: for a remote market without nearby untaxed airports the tax is largely exported to foreigners and causes little diversion, a useful contrast case when we argue that displacement in Europe depends on proximity to untaxed hubs.

---

## 11. CE Delft with SEO (2019), Taxes in the field of aviation and their impact (EU DG MOVE)

1. Citation: CE Delft (Schroten, A., Nelissen, D., Aalberts-Bakker, J., Faber, J., van der Veen, R., Vergeer, R.) with SEO Amsterdam Economics (2019). Taxes in the Field of Aviation and their impact. Final report, European Commission, Directorate-General for Mobility and Transport, June 2019. ISBN 978-92-76-08132-6, DOI 10.2832/913591. Verified: DOI resolves to the EU Publications Office (op.europa.eu); title page of PDF; author list from the CE Delft publication page.
2. Access: VERIFIED for the executive summary and the modelling chapter (Sections 1, 3.1-3.4); country chapters only skimmed. PDF: https://cedelft.eu/wp-content/uploads/sites/2/2021/03/CE_Delft_7M16_taxes_in_the_field_of_aviation_and_their_impact.pdf
3. Policy, countries, period: inventory of aviation taxes in EU28 and selected non-EU countries; ex-ante modelling of introducing or abolishing ticket taxes, VAT and kerosene excise per Member State; base year 2015.
4. Data: IATA Ticket Tax Box Service, IATA airport charges, PaxIS ticket and revenue data, Eurostat passengers (transfer passengers subtracted where known), Eurostat kerosene sales.
5. Identification: partial-equilibrium simulation; price elasticities from Intervistas (2007): -1.23 domestic, -1.12 European, -0.8 intercontinental (economy), business class less elastic using Brons et al.; taxes assumed fully passed on; fiscal revenue assumed recycled.
6. Control / displacement: none modelled at airport level. The report states that ticket and fuel tax impacts are overestimated where many international transfer passengers use a country's airports as a hub (Section 3.4.2-3.4.3), and its introduction notes past taxes produced substantial substitution to foreign airports, but the model has no airport choice.
7. Timing: static.
8. Inference: none.
9. Headline (Executive summary, p. 11): the weighted average aviation tax in the EU is EUR 11 per ticket; abolishing all EU aviation taxes would raise passengers by 4%; removing the kerosene excise exemption would raise average ticket prices by 10% and cut passenger demand by 11%.
10. Transfer / hub: yes, as a stated limitation (transfer passengers excluded from the demand base; hub countries overestimated).
11. Lesson: the official EU benchmark assumes no airport choice and flags hub transfer traffic as its blind spot, which is precisely the margin our network-centrality outcome measures.

---

## Cross-study lessons for our design (short)

- Exemption of transfer passengers is near universal (Bernardo et al. Table 1 text; SEO Irish ATT; Norway; CE Delft), and both airport-level (Falk and Hagsten) and route-level (Bernardo et al.) evidence finds hubs and network carriers unaffected. A null at primary hubs is the prior; effects should show at LCC-heavy secondary airports and in O-D seat capacity.
- Displacement has only been handled by dropping control airports within about 150 km or two hours of a taxing border, or by single-airport synthetic controls. No study models reallocation through the network or to non-EU hubs (Istanbul, Gulf). This is the open gap.
- Reversals are discarded in the best study (IE, NL, MT); they are identifying variation for us (IE introduction 2009, cut 2011, abolition 2014; NL 2008-2009; MT to 2008; DK abolition 2007 not covered by any study I found).
- Inference practice is weak relative to the treatment level: route-level clustering with four treated countries (Bernardo et al.), time-series diagnostics (Seetaram et al.), permutation with about 12 donors (Lorner and Jedvik). Country-level wild cluster bootstrap or randomization inference over adoption dates is needed.
- Treatment dates disagree across sources (Norway: January 2016 in Bernardo et al. Table 1 vs 1 June 2016 in Lorner and Jedvik; UK APD 1998 in Bernardo et al. Table 1 vs 1 Nov 1994 in Seetaram et al.). Code dates from legal sources.
- Confounders coincide with several taxes: Irish ATT with the 2009 recession, UK APD doubling (Feb 2007) with the run-up to the crisis, Swedish tax with "flight shame". Untaxed comparison airports must share these shocks.

---

## Dropped leads and items not entered

- Collet, C., Quirion, P., Taconet, N. (2023). Air passenger taxes and high speed railways decrease CO2 emissions from aviation: Evidence from Europe. SSRN 10.2139/ssrn.4499806. Existence confirmed (Crossref, posted content 2023; no journal version found in Crossref). Not read: SSRN shows a bot check; no abstract in Crossref, OpenAlex or Semantic Scholar; no HAL copy. Highly relevant cross-country panel, worth obtaining manually.
- CE Delft (2018). A study on aviation ticket taxes (December 2018, for the Netherlands). Read: it is a legal and design review (State aid cases on the Irish and Dutch taxes, transfer exemptions), with no elasticity estimates or ex-post evaluation. Not an empirical study, so not entered. Useful background only: it documents the Irish ATT design (EUR 10 / EUR 2 with the 300 km Dublin rule, transfer exemption) and its reduction to zero in 2014. https://cedelft.eu/wp-content/uploads/sites/2/2021/03/CE_Delft_7L14_A_study_on_aviation_ticket_taxes_DEF.pdf
- Trafikanalys evaluation of the Swedish 2018 tax: could not locate (trafa.se search results do not render to the fetch tools; web search unavailable). Unverified, not entered.
- TOI (Norway) evaluation of the 2016 passenger tax: nothing found in Crossref, OpenAlex or refcheck. Not entered.
- Northern Ireland long-haul APD cut (2012) vs Dublin, and Scottish APD devolution: no academic or official ex-post empirical study found. CE Delft (2019) cites an ex-ante Scottish Government (2017) study of halving APD; not read.
- France 2020 eco-contribution, Italy municipal surcharge, Denmark abolition (2007): no ex-post empirical study found in Crossref, OpenAlex or refcheck.
- Seetaram, N., Song, H., Ye, S., Page, S. (2018). Estimating willingness to pay air passenger duty. Annals of Tourism Research 72, 85-97, DOI 10.1016/j.annals.2018.07.001. Exists; abstract read. Contingent valuation of UK travellers, not a policy evaluation; low relevance to our design, not entered.
- Fors, S., Ljung, B. (2019). Evaluating the Impacts of the Swedish Aviation Tax. Lund University student paper (event study on airline stock returns and passengers). Abstract seen via OpenAlex only; student paper; not entered.
- Sharapova, E. (2020) thesis on the Swedish tax and passenger behaviour, and Kopsch (2016) / SOU 2016:83 "En svensk flygskatt" (ex-ante inquiry): titles only; not read.
- Gordijn, H., Kolkman, J. (2011). Effects of the Air Passenger Tax. KiM Netherlands Institute for Transport Policy Analysis. Dutch 2008 tax (cited by Lorner and Jedvik as finding about half the drop was cross-border substitution); belongs to the Dutch/German strand; not read.
- German-tax studies (Borbely 2019 TR-A; Helmers and van der Werf 2025 TR-D; Wozny 2024 SSRN; Grimme et al. DLR): other strand.
- Year discrepancies flagged by refcheck (same articles, online vs issue year): Seetaram et al. online 2013, issue 2014; Falk and Hagsten online 2018, issue 2019.
