# Strand 1A: Netherlands 2008-09 (and 2021) tax, German 2011 Luftverkehrsteuer, Austrian 2011 Flugabgabe, cross-border leakage

Compiled 2026-10-02. Nine studies. Every number below was read in the source at the location given. Numbers are transcribed exactly; wording is paraphrased rather than quoted at length (copyright constraint), so each "headline" field gives the exact figure plus table/section/page. Items marked "secondary" were read in another paper, not in the original.

Status key: VERIFIED = I read the method and results sections in full text. PARTIAL = abstract or summary only.

---

## 1. Gordijn and Kolkman (2011), KiM: Dutch air passenger tax 2008-09

1. **Citation.** Gordijn, H. and Kolkman, J. (2011). *Effects of the Air Passenger Tax: Behavioral responses of passengers, airlines and airports.* KiM Netherlands Institute for Transport Policy Analysis, Ministry of Infrastructure and the Environment, February 2011. No DOI. Dutch edition: *Effecten van de vliegbelasting: gedragsreacties van reizigers, luchtvaartmaatschappijen en luchthavens.* Verified on the publisher page (KiM, dated 10-02-2011) and the PDF title page (authors and date).
   - Page: https://english.kimnet.nl/documents/2011/02/10/effects-of-the-air-passenger-tax-behavioral-responses-of-passengers-airlines-and-airports
   - PDF: https://english.kimnet.nl/site/binaries/site-content/collections/documents/2011/02/10/effects-of-the-air-passenger-tax-behavioral-responses-of-passengers-airlines-and-airports/effects-of-the-air-passenger-tax.pdf
2. **Access.** VERIFIED. I read the full PDF (88 pp.): summary, sec. 1.3 (approach), ch. 2 (history), ch. 4, sec. 5.2 (leakage to Dusseldorf, Brussels, Weeze, Charleroi) and sec. 5.4 (Schiphol estimate).
3. **Policy, country, period.** Netherlands vliegbelasting, levied from 1 July 2008. Set to zero from 1 July 2009, then abolished (the summary says conditionally from 1 January 2010; a footnote says abolished in December 2009). Rates: EUR 11.25 for EU destinations and others within 2,500 km, EUR 45.00 otherwise. Transfer passengers and freight were exempt. Data run from about 2000 to 2010. The report also looks ahead to the German 2011 tax.
4. **Data.**
   - Schiphol Group monthly year-on-year growth in origin-destination (OD) passengers vs. passenger growth of European IATA airlines, Jan 2007 to Sep 2010 (Figs 5.14 to 5.16).
   - Annual departing Dutch passengers at Dusseldorf, 2000-2009, from DLR (Grimme and Maertens 2010).
   - Sabre MIDT ticket data by point of sale (NL vs DE) for Dusseldorf to the US and Asia. MIDT data for Brussels.
   - Brussels Airport OD/transfer and residence breakdown (Witlox and Derudder 2010).
   - KiM airport-choice survey of 3,000 people (2010); sector interviews; media analysis; a TU Delft/KiM System Dynamics simulation.
   - Outcomes: OD passengers, Dutch passengers at foreign airports, tickets by point of sale.
5. **Identification.** Descriptive ex-post accounting. There is no regression. Three steps:
   - (i) Schiphol OD growth minus European IATA airline growth. This gap is first shifted by Schiphol's average pre-tax shortfall of 0.9 percentage points (over the 18 months before the tax) and then averaged over five sub-periods.
   - (ii) Linear extrapolation of Dutch passengers at Dusseldorf from their 2000-2007 trend (+35,700 per year) to 2008-2009. The gap from that trend is read as the tax effect.
   - (iii) Survey answers used to share total defection across foreign airports.
6. **Control group and displacement.** The yardstick for Schiphol is European IATA airline growth. For Dusseldorf the counterfactual is its own pre-trend. Foreign airports (Dusseldorf, Weeze, Brussels, Charleroi) are treated as separate outcomes, not as controls. Munster/Osnabruck was not analysed because volumes were low.
7. **Timing and anticipation.** Five periods: pre-tax (Jan 2007 to Jun 2008), tax (Jul 2008 to Jun 2009), late summer after zero-rating (Jul to Oct 2009), winter 2009/10, and summer 2010. The tax coincides with the 2008-09 financial crisis, which the authors stress. There is no formal anticipation window. For Germany, the report notes that some companies already priced the tax from October 2010 into January 2011 flights (summary).
8. **Inference.** None (no standard errors).
9. **Headline.**
   - Schiphol OD effect: averages -6.9% for Jul 2008 to Jun 2009, about 1.9 million fewer OD passengers on a base of 27.4 million (sec. 5.4, p. 60, Fig. 5.16).
   - A further -1.6% in Jul to Oct 2009 (8.5% cumulative), about 0.96 million fewer passengers (p. 60).
   - Extra Dutch passengers at foreign airports (rough estimate, thousands, Table 5.2, p. 61): Dusseldorf 450, Weeze/NRN 275, Brussels 175, Charleroi 75, Munster/Osnabruck 50, other 220, total 1,245. The summary rounds this to about 1 million.
   - Dusseldorf alone: 420,000 to 470,000 extra Dutch passengers, counting both directions (sec. 5.2.1).
   - Survey: 14% said the tax changed their behaviour. Half of these cancelled or switched to car or train; the other half used a foreign airport.
10. **Transfer/hub/connectivity.** Yes, qualitatively. After July 2008, Schiphol departing passengers fell while untaxed transfer passengers kept increasing (summary, p. 8). The estimate uses OD traffic only. The ex-ante government study (Significance et al. 2007, ACCM/AEOLUS model) chose the tax variant judged least damaging to Schiphol's hub function (sec. 2.2). No centrality measure.
11. **Lesson for our design.** A transfer-exempt departure tax can cut OD traffic at a hub while transfer flows keep growing, so seat-based centrality at Schiphol may not move even when OD demand leaks. The NL 2008-09 episode is an on-off treatment overlapping the crisis. It should be modelled as its own reversible event with monthly seats, or kept out of the absorbing staggered sample. Dutch use of Dusseldorf was already trending up before the tax, so leakage outcomes need pre-trend controls.

---

## 2. Infras (Peter et al. 2012) for the German Finance Ministry, in Bundestag Drucksache 17/10225

1. **Citation.**
   - Bundesregierung (2012). *Bericht an den Deutschen Bundestag über die Auswirkungen der Einführung des Luftverkehrsteuergesetzes auf den Luftverkehrssektor und die Entwicklung der Steuereinnahmen aus der Luftverkehrsteuer.* Deutscher Bundestag, Drucksache 17/10225, 29.06.2012. Submitted by the BMF under §19(4) LuftVStG.
   - Annex III: Peter, M., Bertschmann-Aeppli, D., Zandonella, R. and Maibach, M. (Infras) (2012). *Auswirkungen der Einführung der Luftverkehrsteuer auf die Unternehmen des Luftverkehrssektors in Deutschland: Ex-Post-Analyse nach einem Jahr.* Schlussbericht, Zürich, 25 June 2012. Commissioned by the BMF.
   - URL: https://dserver.bundestag.de/btd/17/102/1710225.pdf
   - Verified on the Bundestag document server: 228-page PDF, title page, and the Infras imprint page with its suggested citation.
2. **Access.** VERIFIED. I read:
   - BMF report ch. C on passenger development, the industry (Intraplan) claims and leakage by channel.
   - Infras summary Z.1; sec. 5.1 (displacement, 5.1.1 to 5.1.4); sec. 5.3 (factor-analysis method); sec. 5.4 (overview).
3. **Policy, country, period.** German Luftverkehrsteuer from 1 January 2011. Data 2005-2011.
4. **Data.**
   - German airports: Destatis Fachserie 8 Reihe 6.1 (passengers adjusted for domestic boarders).
   - Foreign airports: Eurostat passengers 2005-2010, with 2011 built from ACI 2010-11 growth applied to Eurostat 2010 levels.
   - Passengers flying from Germany to large European hubs; price indices; kerosene prices; GDP; online survey and interviews with airlines.
   - Annual. Outcomes: passengers, flights, passengers per flight.
5. **Identification.** Three approaches, combined into one overall assessment:
   - (i) Displacement analysis: descriptive comparison of 2011 growth of German vs foreign airport clusters against 2005-2010 trends.
   - (ii) Price-elasticity simulation.
   - (iii) A "Faktoranalyse": 2011 passengers are projected from 2010, after correcting both years for the 2010 volcanic-ash closure and for Africa flows (Arab Spring), using GDP and price/kerosene changes. The residual between this projection and the corrected actual figure is the tax effect.
   - A national comparison was also made with Western European comparison countries (DK, NO, SE, FI, NL, BE, LU, FR, CH).
6. **Control group and displacement.**
   - A foreign airport counts as an alternative if it is within 200 km of a German airport (Table 17).
   - Clusters (Table 18):
     - West: German Bremen, Weeze, Dusseldorf, Cologne/Bonn, Saarbrucken and Karlsruhe/Baden-Baden vs foreign Groningen, Maastricht, Eindhoven, Liege, Luxembourg, Strasbourg and Metz.
     - South: German Karlsruhe, Friedrichshafen and Munich vs foreign Basel, Zurich, Innsbruck and Salzburg.
     - East: German Dresden and Berlin vs foreign Prague and Szczecin.
   - Displacement is measured as its own outcome through three channels:
     - border airports reached by land;
     - nearby hubs reached by land (Brussels, Zurich and Vienna vs Munich, Dusseldorf and Berlin-Tegel; Amsterdam vs Frankfurt);
     - large European hubs reached by air (London Heathrow, Paris CDG, Madrid, Amsterdam).
   - Caveats noted by Infras: Vienna sits in the comparison hub group although Austria taxed from 2011, so Brussels is shown separately. Heathrow is kept despite the UK APD rise, on the argument that only the 2010-11 change in APD matters.
7. **Timing and anticipation.** The law was passed on 28 Oct 2010 and entered into force on 15 Dec 2010. It applies to bookings made from 1 Sep 2010 for departures from 1 Jan 2011 (Infras Z.1). The analysis compares 2011 with 2005-2010 and has no anticipation adjustment.
8. **Inference.** None. Results are given as ranges.
9. **Headline.**
   - Infras: 1.4 to 2.2 million passengers changed behaviour in 2011 (rounded to 2 million), of which about 0.5 to 1.0 million were displaced abroad (sec. 5.4).
   - Displacement (Table 35):
     - border airports 200,000 (range 0 to 400,000);
     - nearby hubs by land 150,000 (100,000 to 200,000);
     - European hubs by air 400,000 (370,000 to 450,000);
     - total 750,000 (470,000 to 1,050,000).
   - Signs of displacement to border airports appear only in the West cluster, not South or East. By land, displacement to a smaller hub shows up at most for Brussels, not for Vienna, Zurich or Amsterdam (sec. 5.1.4).
   - BMF report summary: demand dampened by up to 2.0 million passengers (about 1.1%). Of these, about 0.75 million went to foreign border airports or foreign hubs and about 1.25 million switched mode or did not travel. Nominal passenger volume still rose by about 9 million (4.8%) from 2010 to 2011.
   - CO2 from German aviation fell by 0.38 Mt (Infras sec. 5.6.2).
10. **Transfer/hub/connectivity.** Yes, explicitly.
    - Re-routing via foreign hubs by air is tested by comparing 2010-11 growth in passengers flying from Germany to each hub with (a) total German air-traffic growth and (b) the hub's own growth. Growth above both is read as displacement. It is found for Heathrow, CDG and Amsterdam, not Madrid (sec. 5.1.3).
    - On a through ticket, the tax is due on the final destination even when the connection is abroad. Only separately booked tickets avoid it, saving EUR 17 (medium haul) or EUR 37 (long haul).
    - The BMF report reproduces an Intraplan table: Frankfurt plus Munich grew +7.4% in 2010-11 vs +8.9% for Amsterdam, Brussels and Zurich (Table 13).
    - No centrality measure.
11. **Lesson for our design.**
    - This is a ready template for measuring hub-function leakage: compare flows from the taxed country to foreign hubs against two benchmarks.
    - Because the tax follows the final destination of through tickets, passenger-side diversion to foreign hubs is limited. Any loss of hub centrality is more likely to come through airline supply decisions.
    - For German monthly seats, treat Sep to Dec 2010 as a possible anticipation window.

---

## 3. IHS Vienna (Schönpflug, Paterson and Sellner 2012; update 2014): Austrian Flugabgabe

1. **Citation.**
   - Schönpflug, K., Paterson, I. and Sellner, R. (with Schwarzbauer, W. and Hochmuth, B.) (2012). *Evaluierung der Flugabgabe.* Projektbericht, Institut für Höhere Studien (IHS), Wien, September 2012. Study commissioned by the Austrian BMF. https://irihs.ihs.ac.at/id/eprint/3023/1/IHSPR6541149.pdf
   - Update: Schönpflug, K., Paterson, I. and Sellner, R. (2014). *Evaluierung der Flugabgabe: Update zur IHS Studie 2012.* http://irihs.ihs.ac.at/2887/1/IHSPR6541150.pdf
   - Verified in the IHS institutional repository (both PDFs) and in OpenAlex.
2. **Access.** 2012 report VERIFIED: I read the executive summary, sec. 2.3 (German evaluations), 4.4 (alternative foreign airports), 5.1 and 5.3 (simulations). 2014 update PARTIAL: executive summary only.
3. **Policy, country, period.** Austrian Flugabgabe from 1 April 2011, EUR 8 (short haul) to EUR 35 (long haul). From 1 Jan 2013 the range is EUR 7 to 35 (2014 update). Data 2004-2011 (2012 report) and up to 2013 (update).
4. **Data.**
   - Austrian airports' arriving plus departing passengers in 2010-2011, with transfer and transit passengers removed. Airport-level trends 2004-2011.
   - Eurostat HICP for air passenger transport, kerosene prices, Eurostat nominal GDP, comparisons with European airports in 2011.
   - Travel time and cost to alternative airports within 50 and 100 km radii. Annual.
5. **Identification.** Simulation, no econometric control group.
   - Expected 2011 growth = nominal GDP growth (4.91%) times an income elasticity of 1.0, 1.5 or 1.9, adjusted for kerosene pass-through.
   - This is compared with actual 2011 growth after correcting for special effects (volcanic ash 2010 and Arab Spring 2011, about 300,000 passengers each).
   - A second simulation uses price elasticities. The gap between expected and actual growth is read as the tax effect.
6. **Control group and displacement.** No control group. Cross-border substitution is assessed only through travel time and cost to foreign alternatives (for example Bratislava for Vienna). The authors conclude that the added travel and time costs mostly do not match the tax savings (sec. 4.4).
7. **Timing and anticipation.** The tax started on 1 April 2011. The authors note that annual data probably understate the effect, because Q1 was untaxed and many Q2/Q3 flights were booked before the start. Quarterly data were not yet available (sec. 5.3).
8. **Inference.** None. Low, middle and high scenarios.
9. **Headline.**
   - Middle scenario: about 30,000 fewer passengers, within the forecast band (executive summary).
   - Sec. 5.3 gives 18,000 to 28,000 depending on the method.
   - 2014 update: no signs of a fall in passengers attributable to the tax. Weak economic growth is named as the main driver.
   - Secondary (the IHS summary of German studies):
     - Intraplan (for the airline association BDL) claimed losses of at least 2.5% of demand, or at least 5 million airport-counted passengers, in 2011. About one third of the lost trips went to foreign airports.
     - TU Chemnitz (for NGOs) found no evidence, attributing declines at border airports to their small size and low-cost profile.
10. **Transfer/hub/connectivity.** Partly. The base excludes transfer and transit passengers. The report notes that tax-exempt transit traffic at Linz collapsed. No centrality measure.
11. **Lesson for our design.** The Austrian tax started mid-year, so annual airport data blur the treatment date. Monthly OAG seats allow dating from April 2011. Vienna was itself treated in 2011, so it cannot be an untreated control or a clean "receiving hub" for German leakage in 2011.

---

## 4. Gurr and Moser (2017), Zeitschrift für Verkehrswissenschaft: German tax panel

1. **Citation.** Gurr, P. and Moser, M. (2017). Beeinflusst die Luftverkehrsteuer Passagieraufkommen? Ergebnisse einer Paneldatenanalyse. *Zeitschrift für Verkehrswissenschaft* 88(3), 181-193. No DOI found.
   - PDF from the journal archive: http://z-f-v.de/fileadmin/archiv/hefte---2017_1_2_3/2017-3/ZfV_2017_Heft-3_01_Gurr_Moser-Luftverkehrssteuer_Panelanalyse.pdf
   - Verified on the journal archive PDF (13 pages, numbered from 181). Volume, issue and pages match the reference list of Helmers and van der Werf (2025).
   - refcheck could not match it (not in Crossref or Semantic Scholar; it returned an unrelated paper).
2. **Access.** VERIFIED. I read sec. 4 (strategy, data), sec. 5 and Tables 3 and 4.
3. **Policy, country, period.** Germany, 2010-2016.
4. **Data.**
   - Destatis Fachserie Luftverkehr: monthly passengers boarding at German main airports, by last known final-destination airport. Summed to years and aggregated to destination country.
   - 61 destination countries (34 in tax band 1, 7 in band 2, 20 others); balanced panel, 427 observations.
   - Controls from the World Bank: GDP, exchange-rate-adjusted CPI, political stability index.
5. **Identification.** Panel OLS. The log of annual boarding passengers to country i is regressed on the tax rate for flights to country i (0 before 2011), the controls, destination-country fixed effects and year fixed effects (preferred model 3). Variation comes from the distance bands and from changes over time. The authors say this gives strong indications, not definitive causal identification.
6. **Control group and displacement.** No foreign control group. Footnote 20 explains why: French (or any neighbouring) airports would absorb diverted passengers and overstate the effect, while distant countries are not comparable. Identification is therefore within German outbound traffic, across destination bands.
7. **Timing and anticipation.** The tax variable is 0 in 2010. Results are split into an introduction effect (2010-11) and a change effect (2011-16). Footnote 19 notes that later rate changes were tied to a EUR 1 billion revenue target and may therefore be endogenous.
8. **Inference.** Standard errors clustered by destination country (61 clusters). Pesaran and Friedman tests for cross-sectional dependence.
9. **Headline.**
   - Table 3, model 3: tax coefficient -0.00200 (SE 0.00104), significant at 10%. One euro more tax goes with 0.2% fewer boarding passengers.
   - Table 4: introduction effect -0.00198 (SE 0.00103, significant at 10%), N = 122. Change effect 0.0176 (SE 0.0137, not significant), N = 366.
10. **Transfer/hub/connectivity.** No. Transfer passengers are not separated in what I read. No centrality.
11. **Lesson for our design.** A dose design within the taxed country, using its distance bands, avoids foreign controls contaminated by diversion. The band structure of the DE and AT taxes could give route-level treatment intensity to complement cross-country DiD.

---

## 5. Falk and Hagsten (2019), International Journal of Tourism Research: Germany and Austria

1. **Citation.** Falk, M. and Hagsten, E. (2019). Short-run impact of the flight departure tax on air travel. *International Journal of Tourism Research* 21(1), 37-44. DOI 10.1002/jtr.2239. First published online 3 Oct 2018. refcheck: verified, with a year flag (Crossref records 2018, the online year; the issue is Jan/Feb 2019).
2. **Access.** PARTIAL, abstract only. The Wiley full text and PDF were not accessible (https://onlinelibrary.wiley.com/doi/abs/10.1002/jtr.2239). Semantic Scholar lists a "bronze" PDF link, but it did not open.
3. **Policy, country, period.** German and Austrian taxes introduced in 2011; 2008-2016 (abstract).
4. **Data.** 310 airports in 30 European countries, 2008-2016. Outcome: number of flight passengers (abstract). Source and frequency: not read.
5. **Identification.** Dynamic panel difference-in-differences (abstract). Exact specification not read. Secondary: Helmers and van der Werf say they used a QML dynamic panel estimator.
6. **Control group and displacement.** Not read. Secondary (Borbely 2019, secs. 1 and 5): untaxed European airports as controls, bordering airports pooled, and no significant effect on bordering airports.
7. **Timing and anticipation.** Not read.
8. **Inference.** Not read.
9. **Headline (abstract).** Passengers fell by 9% in the year of introduction and 5% in the following year. The fall is driven mainly by airports mostly used by low-cost airlines; regular hubs are not affected.
10. **Transfer/hub/connectivity.** Airport-type split, LCC airports vs hubs (abstract). Transfer handling and centrality: not read.
11. **Lesson for our design.** A pooled DiD on airport totals found no border effect, while airport-specific SCM (Borbely) did. Effects differ by airport role, so our design should allow heterogeneity by role (hub, LCC base, border airport).

---

## 6. Borbely (2019), Transportation Research Part A: German tax, synthetic control

1. **Citation.** Borbely, D. (2019). A case study on Germany's aviation tax using the synthetic control approach. *Transportation Research Part A: Policy and Practice* 126, 377-395. DOI 10.1016/j.tra.2019.06.017. refcheck: verified. A 2018 working-paper version is at https://strathprints.strath.ac.uk/68463/.
2. **Access.** VERIFIED via the author accepted manuscript: https://strathprints.strath.ac.uk/69132/1/Borbely_TRPA2019_A_case_study_on_Germanys_aviation_tax_using_the_synthetic.pdf. I read secs. 2 to 6, Table 1 and appendix Table 2. Per-airport effect sizes (Fig. 4) are only graphical and could not be read as numbers.
3. **Policy, country, period.** German tax from 1 Jan 2011. Annual data 2003-2015: eight pre-periods (2003-2010) and post-period 2011-2015.
4. **Data.**
   - Eurostat annual passengers per airport, 2003-2015. These include departing, arriving and transfer passengers, which the author flags as a limitation (fn. 11).
   - Covariates: NUTS2 purchasing power per capita, lagged passengers, national flight-ticket price inflation (all Eurostat). First differences.
5. **Identification.** Synthetic control (Abadie et al. 2010), with a separate model for each treated airport (Stata synth).
6. **Control group and displacement.**
   - Treated units: 21 German airports and 13 "bordering" foreign airports within about two hours' drive, a 150 km circle (Amsterdam, Basel, Billund, Brussels, Charleroi, Eindhoven, Luxembourg, Maastricht, Metz, Prague, Rotterdam, Szczecin, Zurich).
   - Spillover is thus estimated as its own outcome, and bordering airports are kept out of the donor pools.
   - Donors: airports in countries with no aviation-tax change, of similar size (pre-period maximum passengers within a factor of 2).
   - Two donor sets: A = countries around Germany, B = the wider EEA. The preferred set is the one with the better pre-fit.
   - Austrian airports are excluded from donors (taxed in 2011) and not analysed. Dutch airports are kept as bordering treated units despite the NL 2008-09 tax.
   - The donor lists include London Heathrow (for example a 0.606 weight in the Frankfurt synthetic, appendix Table 2), although the UK APD changed during the sample.
7. **Timing and anticipation.** Treatment in 2011. No anticipation discussion.
8. **Inference.**
   - Placebo-in-space: the p-value is the share of donor placebos whose post/pre RMSPE ratio exceeds the treated airport's.
   - A model is flagged as ill-fitting if its pre-period RMSPE exceeds 5% of 2010 passengers.
   - Robustness: estimates compared across donor sets A and B.
9. **Headline.**
   - Summing over German airports: about 4 million passengers lost per year vs. the counterfactual, roughly 2% of annual passengers (sec. 4).
   - Most bordering airports gained. Most regional (largely LCC) German airports lost. Berlin-Tegel, Dusseldorf, Frankfurt and Munich gained relative to their synthetics; Hamburg shows a small loss.
   - Table 1 (RMSPE ratio, p-value):
     - Eindhoven 169.09 (p = 0.000), Amsterdam 22.13 (p = 0.000), Basel 10.36 (p = 0.038), Luxembourg 11.71 (p = 0.057).
     - Brussels, Charleroi and Zurich: not significant.
     - Munich 24.56 (p = 0.000), Frankfurt p = 0.818.
10. **Transfer/hub/connectivity.** Airport groups: hub, regional, bordering, low-cost. A higher share of untaxed transfer passengers is listed as one reason hubs held up. No centrality measure.
11. **Lesson for our design.** Treat nearby foreign airports as a second treated group (the spillover outcome) and drop them from controls. Airport-specific estimates reveal sign heterogeneity (hubs up, regional airports down) that pooled estimates hide. RMSPE placebo inference is a template for the few-treated-units case, for example single-country events.

---

## 7. Bernardo, Fageda and Teixidó (2024), Transportation Research Part A: DE, AT, NO, SE staggered DiD

1. **Citation.** Bernardo, V., Fageda, X. and Teixidó, J. (2024). Flight ticket taxes in Europe: Environmental and economic impact. *Transportation Research Part A: Policy and Practice* 179, 103892. DOI 10.1016/j.tra.2023.103892. Open access (CC BY-NC). refcheck: verified. SSRN working paper: 10.2139/ssrn.4124321.
2. **Access.** VERIFIED. I read secs. 1 to 3 and Tables 1 to 6 at https://www.sciencedirect.com/science/article/pii/S0965856423003129. The pass-through section was only skimmed.
3. **Policy, country, period.** Taxes in Germany (2011), Austria (2011), Norway (2016) and Sweden (2018) identify the effect. Supply data 2007-2019.
4. **Data.**
   - RDC Aviation Apex Schedules: monthly airline-route (city-pair) seats, flights, aircraft and distance, collapsed to annual; 61,964 route-airline pairs.
   - CO2 from the Eurocontrol Small Emitter Tool.
   - Fares from Apex Fares, 2013-2019.
   - NUTS3 population and income.
   - Outcomes: ln flights, ln CO2.
5. **Identification.**
   - Staggered DiD. Treated: airline-routes with an endpoint in a taxing country.
   - Main estimator: Callaway and Sant'Anna, doubly robust, with entropy balancing on 2008-2010 covariates. TWFE shown for comparison.
   - Equation (1a, 1b): log outcome on a tax dummy, covariates, airline-route fixed effects and year fixed effects.
   - Event study (Fig. 5); quarterly estimates (Table 3).
6. **Control group and displacement.**
   - Controls: routes with no tax at either end. The UK, France and Italy (taxes from the 1990s) stay in the control group; Appendix Table A2 drops them.
   - Ireland, the Netherlands and Malta are dropped because their taxes were abolished in-sample, which breaks the irreversibility assumption.
   - SUTVA check (Table 4): flights from control-group airports less than about two hours' drive (normally under 150 km) from a treated border are removed. Result: -0.125 (SE 0.025), virtually unchanged.
7. **Timing and anticipation.** Annual treatment year by country. Parallel pre-trends shown with the CS event study (Fig. 5). The effect builds up gradually after introduction. Anticipation is not discussed in what I read.
8. **Inference.** Standard errors clustered at the route level. The number of clusters is not reported in what I read.
9. **Headline (Table 2, col. 4, CS estimator, low-cost airlines).**
   - ln flights -0.122 (SE 0.024); ln emissions -0.140 (SE 0.024).
   - TWFE without covariates: -0.090 and -0.127.
   - By airline type (Table 5): network airlines -0.011 (SE 0.020, not significant); all airlines -0.042 (SE 0.012).
   - Semi-elasticity: one more euro of tax gives about 1% fewer flights per airline-route (Appendix Table A4, TWFE).
10. **Transfer/hub/connectivity.** Yes, indirectly. Network carriers serve as the group expected not to respond, because connecting passengers are exempt. Fig. 1 reports 2016 transfer shares from OAG MIDT for Lufthansa (five largest German airports), KLM (AMS), Austrian (VIE) and SAS (STO, OSL). No centrality measure.
11. **Lesson for our design.** This is the closest existing analogue to our planned staggered DiD. It shows:
    - drop reversible-treatment countries (or model them separately);
    - keep long-taxed countries as controls;
    - check robustness by excluding control airports near treated borders.

    It also predicts little network-carrier response, so hub centrality effects, if any, should run through low-cost route withdrawal at secondary airports.

---

## 8. Helmers and van der Werf (2025), Transportation Research Part D: German tax, lasting effects

1. **Citation.** Helmers, V. and van der Werf, E. (2025). Did the German aviation tax have a lasting effect on passenger numbers? *Transportation Research Part D: Transport and Environment* 140, 104570. DOI 10.1016/j.trd.2024.104570. Open access. refcheck: verified. SSRN version 2024: 10.2139/ssrn.4892451.
2. **Access.** VERIFIED. I read the full article (secs. 1 to 7, Tables 1 to 5) at https://www.sciencedirect.com/science/article/pii/S1361920924005273.
3. **Policy, country, period.** German tax from 1 Jan 2011. Data 2005-2019, with effects estimated for 2011-2019.
4. **Data.**
   - Eurostat annual departing passengers per airport: 365 airports in 31 countries.
   - Basic estimation sample: 289 airports (26 hubs) in 27 countries. Only airports with no missing data in 2009-2012 are kept, and airports with major idiosyncratic changes are removed (6 German, 13 control).
   - Covariates: GDP per capita, HICP accommodation, a terrorism dummy. Kerosene price and transport HICP are used only in the specification curve analysis (SCA), as fare proxies.
5. **Identification.**
   - Event-study panel with year-specific treatment dummies (2011-2019), pre-dummies for 2006-2009 and 2010 as the reference year.
   - Five estimators: static TWFE (eq. 1), pooled OLS with a lagged dependent variable (eq. 2), dynamic TWFE, Arellano-Bond, and Kripfganz QML (eq. 3).
   - Specification curve analysis over 175 combinations (5 estimators x 5 covariate sets x 7 sample choices).
6. **Control group and displacement.**
   - Controls: airports in EU countries without a passenger tax.
   - Excluded from main controls: Austria, France, Ireland, Italy, the Netherlands and the UK (own taxes or tax changes).
   - Non-German airports within 350 km of the German border are excluded from the main analysis, as a guard against spillover.
   - In the SCA, neighbouring airports re-enter as an additional treated group (with a dummy), and the taxed countries are added back.
   - Hubs are defined by three criteria (official hub of a non-LCC airline, regular flights outside Europe/North Africa, or the main international airport of a country). Results are shown with and without hubs.
7. **Timing and anticipation.** Reference year 2010. The tax was announced a few months ahead (sec. 7). No pre-period exclusion. Pre-dummies are significant only for the dynamic TWFE (2006, 2007) and for QML in the full sample (2006).
8. **Inference.** Standard errors clustered at country level where the estimator allows, robust otherwise. The basic sample covers 27 countries; a separate cluster count is not reported.
9. **Headline.**
   - Table 2 (all airports), Treated 2011: -0.100 static TWFE, -0.068 POLS+LDV, -0.113 dynamic TWFE, -0.100 Arellano-Bond, -0.109 QML (all significant). Summarised as a 7% to 11% reduction in 2011 (sec. 5.2).
   - Table 3 (non-hub airports), 2011: -0.089 to -0.134, i.e. -9% to -13%.
   - SCA (Table 5): 99% of specifications significant for 2011 (all airports, -6.3% to -13.5%), 38% for 2012, 0% for 2013. Effects are strong in the first two years and ambiguous afterwards.
10. **Transfer/hub/connectivity.** Yes, as a measurement issue. Hub data mix taxed OD passengers with untaxed transfer passengers (Munich 38% and Frankfurt 53.7% transfer in 2019, from airport sources), so results are shown excluding hubs. No centrality measure.
11. **Lesson for our design.**
    - Their spillover buffer is wide (350 km).
    - Use an event-study form with year-specific effects; the effect fades after two years.
    - Estimator choice drives long-run estimates, so report a specification curve, or at least static vs. dynamic bracketing.
    - Country-level clustering in a small set of countries is a weak point; we should consider wild-cluster bootstrap or permutation inference.

---

## 9. Zijlstra and 't Hoen (2026), KiM note: Dutch tax reintroduced 2021 and raised 2023

1. **Citation.** Zijlstra, T. and 't Hoen, A. (2026). *Vliegen vanuit het buurland: Leidt de vliegbelasting tot ander uitwijkgedrag?* KiM Notitie, Kennisinstituut voor Mobiliteitsbeleid, March 2026 (published 24-03-2026). DOI as printed: https://doi.org/10.82230/KiM.MB2531 (not checked in Crossref).
   - Page: https://www.kimnet.nl/documenten/2026/03/24/vliegen-vanuit-het-buurland
   - PDF: https://www.kimnet.nl/site/binaries/site-content/collections/documents/2026/03/24/vliegen-vanuit-het-buurland/kim-notitie-vliegen-vanuit-het-buurland-def.pdf
   - Verified on the KiM publication page and the PDF title page.
2. **Access.** VERIFIED. I read the summary, ch. 1, sec. 2.3, sec. 5.1 and Appendix A (method). 44 pp.
3. **Policy, country, period.**
   - Dutch vliegbelasting reintroduced in 2021 at EUR 7.85 flat and raised to EUR 26.43 in 2023 (Table 1.1).
   - Distance-based from 2027: EUR 29.40, 47.24 and 70.86.
   - Also rising airport charges (Schiphol +13% in 2024).
   - Data 2004-2025.
4. **Data.**
   - Passenger totals at 5 Dutch airports and 12 nearby foreign airports (Belgium and the German border region), 2019 vs 2025.
   - Schiphol Routes and Profile Monitor: a CAPI intercept survey, 2004-2024, OD passengers only, 1,140,663 respondents (about 55,000 a year).
   - Airport-provided shares of neighbouring-country residents, licence-plate counts at Rotterdam, earlier KiM surveys of Dutch adults, press reports.
5. **Identification.** Descriptive statistics only.
6. **Control group and displacement.** An informal comparison of Dutch airport totals with the 12 border airports. The reverse flow (Belgian and German residents at Dutch airports) is also tracked.
7. **Timing and anticipation.** Compares pre-COVID 2017-2019 with 2023-2025. COVID overlaps the 2021 reintroduction. No formal anticipation handling.
8. **Inference.** None.
9. **Headline (sec. 5.1).**
   - Dutch airports: 81.2 million passengers (2019) to 78.4 million (2025), -3.4%. The 12 foreign border airports: 80.6 million to 76.2 million, -5.5%.
   - The share of Dutch adults departing from a foreign airport is about 13% in 2013, 2016 and 2024. More than 85% of trips by Dutch residents start at a Dutch airport.
   - Groningen and Maastricht declined, linked to supply cuts.
10. **Transfer/hub/connectivity.** Yes, as a measurement issue (Appendix A). Of about 1.7 million German-resident departing passengers at Schiphol in 2024, about 1.2 million were transfer passengers, about 250,000 were visitors returning home, and about 190,000 had come overland. Only the last group, 11%, is cross-border airport choice. Transfer passengers are removed. No centrality measure.
11. **Lesson for our design.** Raw totals show no mass leakage after the 2021 reintroduction or the 2023 increase. The 2021 date is confounded by COVID, so the 2023 rate increase may be the cleaner Dutch event in monthly seat data. Airport totals at hubs mix transfer flows with resident leakage, so leakage is better read at non-hub border airports or in low-cost seat capacity.

---

## Cross-cutting points for our design (from the nine studies)

- **Spillover handling.** Two practices recur:
  - drop foreign airports near the taxed border from controls (Helmers and van der Werf: 350 km; Bernardo et al.: about 150 km or two hours' drive);
  - treat those airports as a separate treated outcome (Borbely: 13 bordering airports; Infras: West/South/East clusters within 200 km).
  - Gurr and Moser avoid foreign controls altogether by using variation across destination bands inside Germany.
- **Transfer exemption.** All three taxes exempt transfer passengers. The evidence (KiM 2011 Schiphol transfer growth; Borbely hubs gaining; Falk and Hagsten hubs unaffected; Bernardo et al. network carriers -0.011 not significant) points to small or positive effects on hubs and negative effects at LCC and regional airports. The only direct test of leakage of hub function to foreign hubs is Infras sec. 5.1.3: 400,000 passengers by air to LHR, CDG and AMS in 2011, using a two-benchmark growth comparison.
- **Timing.**
  - NL: 1 Jul 2008 to 1 Jul 2009 (reversible), reintroduced 2021, raised 2023.
  - DE: bookings from 1 Sep 2010, departures from 1 Jan 2011.
  - AT: 1 Apr 2011.
  - Monthly OAG seats allow anticipation windows; annual data blur the Austrian start.
- **Inference.** Existing work clusters by country (Helmers and van der Werf) or route (Bernardo et al.), or uses SCM placebo p-values (Borbely). No study used wild-bootstrap or randomization inference at the country level, which our few-treated-countries setting needs.
- **Network centrality.** None of the nine studies uses network centrality or connectivity as an outcome. That gap is ours to fill.

---

## Other relevant items seen but not extracted

- Wozny, F. (2024). Tax Incidence in Heterogeneous Markets: The Pass-through of Air Passenger Taxes on Airfares. IZA DP 16783 (also SSRN 10.2139/ssrn.4717696). Abstract read: the Swedish tax, with Denmark and Finland as controls, using worldwide booking data. Belongs to the Nordic strand.
- Lieshout, R., Boonekamp, T. and Zuidberg, J. (2018). *Effecten van een nationale vliegbelasting.* SEO Amsterdam Economics, ex-ante study for the 2021 Dutch tax (OpenAlex record, UvA-DARE). Not read.
- Intraplan Consult (2012), study for BDL, and Thießen et al. (2012), TU Chemnitz study for BUND and other NGOs. Known only through summaries in BT-Drs. 17/10225 and IHS (2012). Not read in the original.
- Berster, P. et al. (2010). The impacts of the planned air passenger duty in Germany. Infraday conference, TU Berlin. DLR ex-ante, cited by Borbely. Not read.
- Grimme, W. and Maertens, S. (2010), DLR data input cited in KiM (2011). Not read.
- Fichert et al. (2014), cited by Gurr and Moser for a 1.2% to 2.8% demand decline. Not located.

## Dropped or corrected leads

- **"DLR and/or Intraplan evaluation of the German Luftverkehrsteuer for the Federal Finance Ministry (around 2012)": not as described.**
  - The BMF's commissioned evaluation was by Infras, Zurich (Peter et al. 2012), annexed to BT-Drs. 17/10225 (entry 2).
  - Intraplan's 2012 study was commissioned by the airline association BDL, not the BMF, and I did not obtain the original.
  - DLR's role I could confirm only as ex-ante analysis (Berster et al. 2010) and as a data supplier to KiM (Grimme and Maertens 2010). I found no DLR ex-post evaluation for the BMF.
- **Falk and Hagsten "(2019?)": kept, year corrected.** The article is vol. 21(1) 2019, pp. 37-44, first online 3 Oct 2018 (Crossref year 2018). The lead's guess of Germany and Austria is correct. Full text was not accessible, so the entry is PARTIAL.
- **Borbely (2019) TRA: confirmed** (vol. 126, pp. 377-395).
- **Gordijn and Kolkman (2011) KiM: confirmed.**
- **Academic ex-post papers on the 2021 Dutch reintroduction: none found** in the time available. The only ex-post evidence found is the KiM (2026) descriptive note (entry 9). CE Delft and SEO ex-ante studies exist but were not read.
- **Beimann and Lueg-Arndt (2012)**, a comment on the BMF report (EconStor hdl 10419/69940): blocked by EconStor's bot check, not read.
- **Steverink and van Daalen (2011)**, *The Dutch Taxation on Airline Tickets* (TU Delft repository; Borbely describes it as mostly theoretical): not read.
- **Mayor and Tol (2010)** on the Dutch tax and tourism, cited by Borbely: not verified.
