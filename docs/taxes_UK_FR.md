# Air passenger ticket taxes: United Kingdom and France — source-cited history

Companion file: `data/raw/taxes/taxes_UK_FR.csv` (one row per period × band × class; `confidence` ∈ {high, medium, low}; empty `rate` = value not confirmed, see `notes`).

Method note. Research was done with web-search snippets only (page fetching was blocked), prioritising gov.uk / HMRC policy papers and the gov.uk "historic rates" table, legislation.gov.uk, the House of Commons Library briefing SN05094, Légifrance / ecologie.gouv.fr (DGAC) notices, French parliamentary answers and the WebLex tariff pages. Numbers that could not be confirmed were left blank rather than estimated. Mile→km conversions use 1 mile = 1.609 km.

---

## 1. United Kingdom — Air Passenger Duty (APD)

### 1.1 Legal basis and chargeable event
APD is an excise duty under Finance Act 1994, Part I Chapter IV (ss. 28–44, Schedules 5A and 6), chargeable on the carriage of each chargeable passenger on a flight beginning at a UK airport. The rate (s. 30) depends on (i) the destination band and (ii) the class of travel; since 2013 a third "higher" rate applies to passengers on large aircraft with few seats (private/business jets). Rates are reset annually (usually by the preceding year's Finance Act, taking effect 1 April) and HMRC publishes them in "Rates for Air Passenger Duty" and its historic-rates annex.

### 1.2 Timeline

| Effective | Structure and rates (per departing passenger) | Legal basis |
|---|---|---|
| 1 Nov 1994 | Introduced (announced Nov 1993 Budget). Flat rate by destination group: £5 UK/EEA, £10 elsewhere. No class split. | FA 1994 ss. 28–44 |
| 1 Nov 1997 | Doubled to £10 (EEA) / £20 (other). | FA 1997 s. 9 |
| 1 Apr 2001 | Reform: reduced rate for "standard class" (lowest class on the aircraft) and standard rate for any other class. EEA £5/£10; non-EEA £20/£40. Domestic return-leg exemption abolished (FA 1994 s. 31 repealed by FA 2000 s. 19). | FA 2000 ss. 18–19 |
| 1 Feb 2007 | All rates doubled (2006 Pre-Budget Report): EEA £10/£20; non-EEA £40/£80. | FA 2007 s. 12 |
| 1 Nov 2009 | Four distance bands by **capital-city distance from London**: A 0–2,000 mi (0–3,218 km), B 2,001–4,000 mi (3,219–6,436 km), C 4,001–6,000 mi (6,437–9,654 km), D >6,000 mi (>9,654 km). Reduced/standard: A £11/£22, B £45/£90, C £50/£100, D £55/£110. Standard rate = 2× reduced. | FA 2009 s. 17, Sch 5 |
| 1 Nov 2010 | A £12/£24, B £60/£120, C £75/£150, D £85/£170. Frozen through 2011-12 (Budget 2011). | FA 2009 Sch 5 |
| 1 Apr 2012 | A £13/£26, B £65/£130, C £81/£162, D £92/£184. | FA 2012 s. 190, Sch 23 |
| 1 Apr 2013 | A £13/£26, B £67/£134, C £83/£166, D £94/£188. **Higher rate introduced** (aircraft ≥20 t and <19 seats; = 2× standard): A £52, B £268, C £332, D £376. Scope extended to aircraft ≥5.7 t (de minimis previously 10 t). | FA 2012 Sch 23; FA 2013 s. 185 |
| 1 Apr 2014 | A £13/£26/£52, B £69/£138/£276, C £85/£170/£340, D £97/£194/£388. | FA 2014 |
| 1 Apr 2015 | **Bands B–D merged** into Band B (>2,000 mi). A £13/£26/£78; B £71/£142/£426. Band A higher rate raised to £78 (6× reduced). Children under 12 in lowest class exempt from 1 May 2015. | FA 2014 s. 79 |
| 1 Apr 2016 | A £13/£26/£78; B £73/£146/£438. Under-16s exempt (lowest class) from 1 Mar 2016. | FA 2015 |
| 1 Apr 2017 | A £13/£26/£78; B £75/£150/£450. | FA 2016 |
| 1 Apr 2018 | A £13/£26/£78; B £78/£156/£468. | FA 2017 |
| 1 Apr 2019 | A £13/£26/£78; B £78/£172/£515. | FA 2018 |
| 1 Apr 2020 | A £13/£26/£78; B £80/£176/£528. | FA 2019 |
| 1 Apr 2021 | A £13/£26/£78; B £82/£180/£541. | FA 2020 |
| 1 Apr 2022 | A £13/£26/£78; B £84/£185/£554. | FA 2021 |
| 1 Apr 2023 | **New Domestic band** (flights within the UK) and **new ultra-long-haul Band C** (>5,500 mi = >8,850 km); Band B becomes 2,001–5,500 mi (3,219–8,850 km). Domestic £6.50/£13/£78; A £13/£26/£78; B £87/£191/£574; C £91/£200/£601. | Finance (No. 2) Act 2023 (Bill cl. 321–322) |
| 1 Apr 2024 | Domestic £7/£14/£78; A £13/£26/£78; B £88/£194/£581; C £92/£202/£607. | FA 2024 |
| 1 Apr 2025 | Domestic £7/£14/£84; A £13/£28/£84; B £90/£216/£647; C £94/£224/£673 (standard/higher adjusted beyond RPI). | FA 2025 |
| 1 Apr 2026 | Domestic £8/£16/£142; A £15/£32/£142; B £102/£244/£1,097; C £106/£253/£1,141 (higher rate +50% real). | FA 2026 |

Format of rate triplets: reduced (economy / lowest class) / standard (any other class, or seat pitch >1.016 m = 40 in) / higher (private jets ≥20 t, <19 seats).

### 1.3 Band logic
- 1994–2009: two territorial groups — the UK plus EEA states (and territories listed in FA 1994 Sch 5A Part 1) versus everywhere else. Not distance-based.
- 2009–2015: four bands by the great-circle distance from London to the **capital city** of the destination country (Sch 5A lists each territory's band). Hence, for example, the whole of the USA sat in Band B while Russia (Moscow) sat in Band A.
- 2015–2023: two bands (A ≤2,000 mi; B >2,000 mi).
- From 2023: Domestic / A (≤2,000 mi) / B (2,001–5,500 mi) / C (>5,500 mi, "ultra-long-haul"). The Channel Islands and Isle of Man are Band A, not domestic.
- Class: "standard class travel" means the only class on the aircraft or the lowest class if there are several; a class whose seats have a pitch exceeding 40 inches (1.016 m) is not standard class and pays the standard rate.
- Connected flights: duty is assessed on the final destination of a connected journey (24-hour connection rule), so UK transfer passengers are not double-charged and the band is that of the ultimate destination.

### 1.4 Exemptions (principal)
Children under 2 without a seat; from 1 May 2015 children under 12 and from 1 Mar 2016 children under 16 in the lowest class; connected-flight passengers; crew; flights departing from Highlands and Islands airports (region with ≤12.5 persons/km²); aircraft below the de minimis weight (10 t until March 2013; 5.7 t since 1 Apr 2013); emergency, military and similar flights. (Detailed conditions: HMRC Excise Notice 550.)

### 1.5 Devolution
- **Northern Ireland.** From 1 Nov 2011 direct long-haul departures from NI (bands B–D) were charged at Band A rates. Finance Act 2012 s. 190/Sch 23 inserted FA 1994 s. 30A devolving the direct long-haul rates (not Band A) to the NI Assembly; the Air Passenger Duty (Setting of Rate) Act (Northern Ireland) 2012 set them at **£0 from 1 Jan 2013**, where they remain (gov.uk rate tables for 2025-26 and 2026-27 still show £0 for NI direct Band B/C, all three rates). F(No.2)A 2023 extended the power to the new ultra-long-haul band. Indirect long-haul, Band A and domestic departures from NI pay UK rates.
- **Scotland.** Scotland Act 2016 s. 17 devolved the tax on air passengers; the Air Departure Tax (Scotland) Act 2017 created ADT, originally intended from 1 Apr 2018 but deferred because the Highlands and Islands exemption needed state-aid (now Subsidy Control Act 2022) clearance. APD continues to apply in Scotland; the Scottish Government states ADT will start on 1 April 2027 with an extended Highlands and Islands exemption. ADT rates are not yet legislated.
- **Wales.** Not devolved (not covered here).

---

## 2. France

France levies two per-passenger ticket taxes on departures from French airports, historically coded in CGI art. 302 bis K and, since 1 Jan 2022, merged (with the airport safety/security tax and the airport equalisation levy) into the single **Taxe sur le transport aérien de passagers (TTAP)**, Code des impositions sur les biens et services (CIBS) art. L. 422-13 ff. The two components relevant here are the *tarif de l'aviation civile* (ex-TAC) and the *tarif de solidarité* (ex-TSBA).

### 2.1 Taxe de l'aviation civile (TAC) — "tarif de l'aviation civile"
Created by loi de finances pour 1999 (n° 98-1266, art. 51) with effect 1 Jan 1999 to fund the civil-aviation annex budget (BACEA) and, for part of the period, the FIATA/general budget. Two destination categories: (a) France (metropolitan incl. Corsica, and overseas departments), other EU member states, EEA states and Switzerland — from 2021 also any state less than 1,000 km from continental France (added by LF 2021 to keep the UK in the low category after Brexit); (b) all other destinations. Since 1 Mar 2025 the categories are renamed "destination européenne ou assimilée" vs "intermédiaire ou lointaine", but TAC keeps a single non-European rate. Rates are uprated each 1 April by the forecast CPI (ex-tobacco) since 2013.

Confirmed values (EU-category / other):
- 1999–2001: franc-denominated rates — **not confirmed** (left blank).
- (by 2003) €3.92 / €6.66 — inferred from LF 2004 art. 44, which replaced those amounts (start date not confirmed; medium).
- 1 Jan 2004: €4.48 / €7.60 (LF 2004 art. 44; medium).
- 1 Jan 2006: €3.92 / €7.04 (restructuring of aviation financing; medium — whether these held unchanged until March 2013 was not verified).
- 1 Apr 2013: uprated by arrêté of 22 Feb 2013 — values **not confirmed**.
- 1 Apr 2014: €4.36 / €7.85 (arrêté 25 Mar 2014; medium).
- 2015-16, 2016-17: **not confirmed**.
- 1 Apr 2017: €4.48 / €8.06 (Bulletin officiel; high).
- 2018-19, 2019-20, 2020-21: **not confirmed** (CE Delft 2019 should give the 2018-19 level).
- 1 Apr 2021: €4.63 / (other not confirmed) (Légifrance version of art. 302 bis K at 1 Apr 2021).
- 2022-23: €4.73 / €8.50; 2023-24: €4.93 / €8.87; 2024-25: €5.05 / €9.09; 2025-26: €5.14 / €9.25; 2026-27: €5.21 / €9.37 (WebLex tariff pages, DGAC notices).

Exemptions: direct-transit passengers (same aircraft/flight number), children under 2, crew; connecting passengers (arrived by air, <24 h, final airport different from origin) received 50 % relief from 1 Apr 2015 and full exemption from 1 Jan 2016 (LFR 2014). Corsica and overseas departments are inside the French/EU category; a "majoration corse" exists but belongs to the airport (safety/security) component of TTAP, not to the TAC/TSBA rates.

### 2.2 Taxe de solidarité sur les billets d'avion (TSBA, "Chirac tax") — "tarif de solidarité"
Created by loi de finances rectificative pour 2005 (n° 2005-1720, art. 22) as a "majoration" of the TAC with effect **1 Jul 2006**; rates fixed by décret n° 2006-663 of 6 Jun 2006. Revenue goes to the Fonds de solidarité pour le développement (Unitaid, IFFIm) and, since 2020, surplus to AFITF (transport infrastructure); since 1 Mar 2025 revenue is first assigned to AFITF (ceiling €271 m for 2026).

| Effective | Europe/EEA/CH economy | Europe/EEA/CH business-first | Other economy | Other business-first | Basis |
|---|---|---|---|---|---|
| 1 Jul 2006 | €1 | €10 | €4 | €40 | LFR 2005 art. 22; décret 2006-663 |
| 1 Apr 2014 | €1.13 | €11.27 | €4.51 | €45.07 | +12.7 % inflation catch-up 2006–13 (vehicle not confirmed) |
| 1 Jan 2020 | €2.63 | €20.27 | €7.51 | €63.07 | LF 2020 (n° 2019-1479): "éco-contribution" of €1.50/€9 (EU) and €3/€18 (other) added |
| 1 Mar 2025 | €7.40 (European) | €30 | €15 intermediate / €40 distant | €80 intermediate / €120 distant | LF 2025 (n° 2025-127) art. 30; CIBS L. 422-22 ff. |

Note on 2006: one parliamentary-answer snippet gives €10 for "other destinations, business"; the DGAC/press reports of décret 2006-663 and the uniform 2014 uprating (45.07 = 40 × 1.127) confirm €40.

**Distance bands since 1 Mar 2025** (CIBS, LF 2025 art. 30):
- *Destination européenne ou assimilée*: metropolitan and overseas France, EU member states, EEA states, and states whose capital's main airport lies <1,000 km from the national reference airport (Paris-CDG) — this captures the UK and Switzerland.
- *Destination intermédiaire*: neither European nor distant, i.e. capital's main airport ≤5,500 km from Paris-CDG.
- *Destination lointaine*: capital's main airport >5,500 km from Paris-CDG (new category created in 2025; previously all non-European destinations shared one rate).
- Class: "sans services additionnels" (economy/premium economy) vs "avec services additionnels" (business/first).
- **Business/private aviation** (non-commercial business aircraft): European €210 (turboprop; one press source says €220) / €420 (jet); intermediate €675 / €1,015; distant €1,025 / €2,100 per passenger.
- Since 2025 the solidarity tariff is fixed in statute (the former power to set it by arrêté was removed).

**Corsica, overseas and PSO routes.** TSBA applies to Corsica and the overseas departments as "France" (European category). In 2020 the éco-contribution component did not apply to "liaisons d'aménagement du territoire" (PSO routes serving isolated areas / territorial continuity); Corsica PSO routes nevertheless paid €2.63 before 2025. The February 2025 parliamentary compromise promised to spare Corsica, overseas and PSO routes from the 2025 increase; this was legislated as a *tarif réduit de solidarité* (restoring €2.63 / €20.27) conditional on EU state-aid clearance. The reduced tariff entered into force on **1 Jun 2026** (arrêté of 31 May 2026) for 26 domestic PSO/territorial-development routes, including the Corsica–Paris/Marseille/Nice/Lyon PSO routes; overseas routes are not yet covered because the European Commission rejected the mechanism proposed for them (minister's statement, 2026). Between 1 Mar 2025 and 31 May 2026 all these routes paid the full €7.40/€30.

**Transit.** Connecting and direct-transit passengers are outside the scope of TTAP (same rule as for TAC), as are children under 2 and crew.

### 2.3 What was confirmed vs not (France)
Confirmed: TSBA rates for 2006, 2014, 2020 and 2025 (incl. business-aviation figures and band definitions); TAC for 2004, 2006, 2014, 2017, 2021 (EU category), 2022–2027; the 2026 reduced tariff. Not confirmed: TAC franc rates 1999–2001; TAC in 2013-14, 2015-16, 2016-17, 2018-19 to 2020-21 and the 2021-22 third-country rate; the exact statutory vehicle of the 2014 TSBA uprating; the enacted article number of LF 2020 (Bill art. 20; usually cited as art. 72).

---

## 3. Sources

United Kingdom
- HMRC, "Historic rates for Air Passenger Duty" — https://www.gov.uk/guidance/rates-and-allowances-for-air-passenger-duty-historic-rates
- HMRC, "Air Passenger Duty historical rates" (APD bulletin) — https://www.gov.uk/government/statistics/air-passenger-duty-bulletin/air-passenger-duty-rates
- HMRC, "Rates for Air Passenger Duty" — https://www.gov.uk/guidance/rates-and-allowances-for-air-passenger-duty
- House of Commons Library, SN05094 "Air passenger duty: recent debates & reform" — https://commonslibrary.parliament.uk/research-briefings/sn05094/
- Finance Act 1994 s. 30 — https://www.legislation.gov.uk/ukpga/1994/9/section/30 ; Finance Act 1997 s. 9 — https://www.legislation.gov.uk/ukpga/1997/16/section/9 ; Finance Act 2000 s. 18 — https://www.legislation.gov.uk/ukpga/2000/17/section/18 ; Finance Act 2007 s. 12 — https://www.legislation.gov.uk/ukpga/2007/11/section/12 ; Finance Act 2009 s. 17 — https://www.legislation.gov.uk/ukpga/2009/10/section/17 ; Finance Act 2012 Sch 23 — https://www.legislation.gov.uk/ukpga/2012/14/schedule/23 ; Finance Act 2013 s. 185 (explanatory notes) — https://www.legislation.gov.uk/ukpga/2013/29/notes/division/1/105 ; Finance Act 2014 s. 79 — https://www.legislation.gov.uk/ukpga/2014/26/section/79 ; Finance (No. 2) Act 2023 — https://www.legislation.gov.uk/ukpga/2023/30 ; Finance (No. 2) Bill cl. 321 debate — https://www.theyworkforyou.com/pbc/2022-23/Finance_No._2_Bill/04-0_2023-05-18a.101.2
- HM Treasury/HMRC policy papers: banding reforms and rates 2023-24 — https://www.gov.uk/government/publications/air-passenger-duty-banding-reforms-from-april-2023/air-passenger-duty-banding-reforms-and-rates-from-1-april-2023-to-31-march-2024 ; rates 2020-21 — https://www.gov.uk/government/publications/air-passenger-duty-rates-from-1-april-2020-to-31-march-2021/air-passenger-duty-rates-from-1-april-2020-to-31-march-2021 ; 2021-22 — https://www.gov.uk/government/publications/changes-to-air-passenger-duty-rates-from-1-april-2021/changes-to-air-passenger-duty-rates-from-1-april-2021 ; 2022-23 — https://www.gov.uk/government/publications/air-passenger-duty-rates-from-1-april-2022-to-31-march-2023/air-passenger-duty-rates-from-1-april-2022-to-31-march-2023 ; 2024-25 — https://www.gov.uk/government/publications/changes-to-air-passenger-duty-rates-from-1-april-2024/increases-to-air-passenger-duty-rates-from-1-april-2024 ; 2025-26 — https://www.gov.uk/government/publications/changes-to-air-passenger-duty-rates-from-1-april-2025/air-passenger-duty-rates-from-1-april-2025-to-31-march-2026 ; 2026-27 — https://www.gov.uk/government/publications/changes-to-air-passenger-duty-rates-from-1-april-2026/air-passenger-duty-rates-from-1-april-2026-to-31-march-2027
- Child exemption (FA 2015 s. 57 notes) — https://www.legislation.gov.uk/ukpga/2015/11/section/57/notes
- Northern Ireland: Air Passenger Duty (Setting of Rate) Act (NI) 2012 and notes — https://www.legislation.gov.uk/nia/2012/5 ; OBR NI tax forecasts — https://obr.uk/topics/scotland-wales-and-northern-ireland/northern-ireland-tax-forecasts/
- Scotland: Air Departure Tax (Scotland) Act 2017 — https://www.legislation.gov.uk/asp/2017/2 ; Scottish Government ADT policy — https://www.gov.scot/policies/taxes/air-departure-tax/ ; SPICe briefing SB 17-70 — https://www.parliament.scot/chamber-and-committees/research-prepared-for-parliament/research-briefings/2017/10/12/sb-1770
- Wikipedia, "Air Passenger Duty" (cross-check only) — https://en.wikipedia.org/wiki/Air_Passenger_Duty

France
- Légifrance, CGI art. 302 bis K (version 1 Apr 2021) — https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006069577/LEGISCTA000006147318/2021-04-01
- Loi de finances pour 2004, art. 44 (TAC amounts) — https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000002453491
- Loi n° 2019-1479 de finances pour 2020 (éco-contribution) — https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000039683944
- Ministère de la Transition écologique / DGAC, "Taxes aéronautiques" — https://www.ecologie.gouv.fr/politiques-publiques/taxes-aeronautiques ; Notice TAC 2026 — https://www.ecologie.gouv.fr/sites/default/files/documents/Notice_TAC_FR_2026.pdf ; Notice tarif de solidarité 2026 — https://www.ecologie.gouv.fr/sites/default/files/documents/ts_notice_fr_2026.pdf ; press release on reduced tariff from 1 Jun 2026 — https://www.ecologie.gouv.fr/presse/tsba-philippe-tabarot-annonce-lentree-vigueur-1er-juin-dune-reduction-taxe-lignes-aeriennes
- Bulletin officiel MTES, TAC rates 2017-18 — https://www.bulletin-officiel.developpement-durable.gouv.fr/documents/Bulletinofficiel-0030005/met_20170017_0000_0007.pdf
- Sénat, avis PLF 2018 "Transports aériens" (TAC 2014 rates) — https://www.senat.fr/rap/a17-113-4/a17-113-43.html ; Sénat, PLF 1999 aviation civile — https://www.senat.fr/rap/l98-066325/l98-06632517.html
- WebLex, TTAP tariff pages 2022–2026 — https://www.weblex.fr/chiffres-cles/taxe-sur-le-transport-aerien-de-passagers-2022 (and -2023, -2024, -2025, -2026) ; "le tarif réduit de solidarité prend son envol" — https://www.weblex.fr/weblex-actualite/transport-aerien-le-tarif-reduit-de-solidarite-prend-son-envol
- Assemblée nationale written answers on TSBA (2006 rates; 2014 uprating) — https://questions.assemblee-nationale.fr/dyn/13/questions/QANR5L13QE15709.pdf ; https://questions.assemblee-nationale.fr/dyn/14/questions/QANR5L14QE35129.pdf ; Sénat question 14333 (2020) — https://www.senat.fr/questions/base/2020/qSEQ200214333.html
- Le Monde du Droit, LF 2025 art. 30 summary — https://www.lemondedudroit.fr/fiscal/309-fiscalite-des-entreprises/99562-taxe-en-matiere-de-deplacements-routiers-et-aeriens.html ; TAC uprating 1 Apr 2013 — https://www.lemondedudroit.fr/fiscal/309-fiscalite-des-entreprises/39372-actualisation-des-tarifs-de-la-taxe-de-laviation-civile-a-compter-du-1er-avril-2013-.html
- EBAA, FAQ TSBA 2025 (business aviation) — https://ebaa.org/app/uploads/2025/03/FAQ_TSBA-vdef.pdf
- L'Écho touristique: TSBA 2006 (DGAC) — https://www.lechotouristique.com/article/taxe-de-solidarite-sur-les-billets-d-avion-la-dgac-fait-le-point,45898 ; TSBA 2025 details — https://www.lechotouristique.com/article/la-taxe-sur-les-billets-davion-tsba-finalement-adoptee-tous-les-details ; TourMaG, 26 reduced-tariff routes — https://www.tourmag.com/Baisse-de-65-de-la-taxe-sur-les-billets-d-avion-voici-les-26-lignes-concernees-_a131979.html
- CE Delft (2019), "Taxes in the Field of Aviation and their impact", for the European Commission — https://op.europa.eu/en/publication-detail/-/publication/0b1c6cdd-88d3-11e9-9369-01aa75ed71a1 (not readable in this environment; recommended to fill the 2018-19 TAC gap)
- Wikipedia, "Solidarity tax on airplane tickets" (cross-check only) — https://en.wikipedia.org/wiki/Solidarity_tax_on_airplane_tickets
