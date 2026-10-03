# Air passenger ticket taxes: Germany, Austria, Netherlands

Companion narrative to `data/raw/taxes/taxes_DE_AT_NL.csv`. Compiled 2026-10-03 from legislative texts (gesetze-im-internet.de, RIS, officielebekendmakingen.nl), national tax authorities (Zoll, BMF Austria, Belastingdienst), government press releases and Destatis statistics. WebFetch was unavailable, so every figure was confirmed from search snippets of the cited sources; where a value could only be corroborated indirectly the CSV `confidence` is set to `medium` and a note is given. All three taxes are levied **per departing passenger, independent of travel class**, so `class = all` throughout (Austria's EUR 30 ultra-short-haul rate is coded `higher`).

---

## 1. Germany: Luftverkehrsteuer (LuftVStG)

### 1.1 Timeline

| Period | Band 1 (Annex 1) | Band 2 (Annex 2) | Band 3 (other) | Instrument |
|---|---|---|---|---|
| 2011-01-01 to 2011-12-31 | 8.00 | 25.00 | 45.00 | LuftVStG s.11(1), Art. 1 Haushaltsbegleitgesetz 2011 (BGBl. I 2010 S. 1885) |
| 2012-01-01 to 2012-12-31 | 7.50 | 23.43 | 42.18 | LuftVStAbsenkV 2012 (ETS offset) |
| 2013-01-01 to 2015-12-31 | 7.50 | 23.43 | 42.18 | Act of 5 Dec 2012 amending s.11(1); LuftVStFestV 2014, 2015 |
| 2016 | 7.38 | 23.05 | 41.49 | LuftVStFestV 2016 |
| 2017 | 7.47 | 23.32 | 41.99 | LuftVStAbsenkV 2017 |
| 2018 | 7.46 | 23.31 | 41.97 | LuftVStAbsenkV 2018 |
| 2019 | 7.38 | 23.05 | 41.49 | LuftVStAbsenkV 2019 (27 Nov 2018) |
| 2020-01-01 to 2020-03-31 | 7.37 | 23.01 | 41.43 | LuftVStAbsenkV 2020, first version (29 Nov 2019) |
| 2020-04-01 to 2020-12-31 | 12.90 | 32.67 | 58.82 | Statute raised to 13.03/33.01/59.43 (Act of 12 Dec 2019, BGBl. I S. 2492); applied via LuftVStAbsenkV 2020, second version (2 Apr 2020) |
| 2021 | 12.88 | 32.62 | 58.73 | LuftVStAbsenkV 2021 |
| 2022 | 12.77 | 32.35 | 58.23 | LuftVStAbsenkV 2022 |
| 2023 | 12.73 | 32.25 | 58.06 | LuftVStAbsenkV 2023 |
| 2024-01-01 to 2024-04-30 | 12.48 | 31.61 | 56.91 | LuftVStAbsenkV 2024 |
| 2024-05-01 to 2026-06-30 | 15.53 | 39.34 | 70.83 | Zweites Haushaltsfinanzierungsgesetz 2024 (BGBl. 2024 I Nr. 107, 27 Mar 2024) |
| 2026-07-01 onwards | 13.03 | 33.01 | 59.43 | Zweites Gesetz zur Aenderung des LuftVStG, 18 Jun 2026 (BGBl. 2026 I Nr. 182) |

Key design feature: the statute (s.11(1)) carries nominal rates, and s.11(2) obliged the Finance Ministry to lower the *applied* rates by ordinance each year so that ticket-tax revenue plus aviation EU-ETS auction revenue stayed at roughly EUR 1 billion. That is why applied rates in 2012-2024 sit a few cents to a few euros below the statutory 8/25/45 (2011), 7.50/23.43/42.18 (2013 statute) and 13.03/33.01/59.43 (from Apr 2020). The 2024 budget act rewrote s.11(2): from 2025 a reduction ordinance is issued only if prior-year revenue exceeds EUR 2.33 billion. No ordinance was issued for 2025 or 2026, so the statutory 15.53/39.34/70.83 applied unchanged until the July 2026 cut.

The 2011 rates were constitutionally upheld by the Bundesverfassungsgericht (judgment of 5 Nov 2014, 1 BvF 3/11).

### 1.2 Band definitions

Rates attach to the **country of the destination airport** (not to the actual route flown) via two country annexes to s.11:

* **Annex 1 (band 1)** - countries whose largest commercial airport is within about 2,500 km of Frankfurt am Main. The legislative logic is: Germany itself (domestic flights), all EU member states, EU candidate countries, EFTA states, plus third countries within that distance. The current list includes Albania, Algeria, Andorra, Belgium, Bosnia and Herzegovina, Bulgaria, Denmark, Germany, Estonia, Finland, France, Greece, Ireland, Iceland, Italy, Kosovo, Croatia, Latvia, Libya, Liechtenstein, Lithuania, Luxembourg, Malta, Morocco, Moldova, Monaco, Montenegro, Netherlands, North Macedonia, Norway, Austria, Poland, Portugal, Romania, Russian Federation, San Marino, Sweden, Switzerland, Serbia, Slovakia, Slovenia, Spain, Czech Republic, Turkey, Tunisia, Ukraine, Hungary, Vatican City, United Kingdom, Belarus and Cyprus.
* **Annex 2 (band 2)** - countries not in Annex 1 whose largest commercial airport is within about 6,000 km of Frankfurt. Current list: Afghanistan, Egypt, Equatorial Guinea, Armenia, Azerbaijan, Ethiopia, Bahrain, Benin, Burkina Faso, Cote d'Ivoire, Djibouti, Eritrea, Gabon, Gambia, Georgia, Ghana, Guinea, Guinea-Bissau, Iraq, Iran, Israel, Yemen, Jordan, Cameroon, Cape Verde, Kazakhstan, Qatar, Kyrgyzstan, Kuwait, Lebanon, Liberia, Mali, Mauritania, Niger, Nigeria, Oman, Pakistan, Palestinian territories, Sao Tome and Principe, Saudi Arabia, Senegal, Sierra Leone, Sudan, South Sudan, Syria, Tajikistan, Togo, Chad, Turkmenistan, Uganda, Uzbekistan, United Arab Emirates and Central African Republic. South Sudan was added with effect from 1 Apr 2020 (Act of 12 Dec 2019).
* **Band 3** - every other country (more than ~6,000 km), e.g. Americas, East and South-East Asia, Southern Africa, Oceania.

Both annexes were amended again by the Act of 18 Jun 2026; the substance of that amendment could not be verified from snippets (likely housekeeping of country names).

### 1.3 Exemptions and special treatment

* **Children**: passengers under two years of age without their own seat are exempt (s.5).
* **Transfer / transit**: the tax attaches to the legal transaction entitling to a departure from a German airport. A passenger who starts abroad and connects in Germany is not taxed on the onward departure provided the stopover is not a "Zwischenlandung" under s.2 no.5, i.e. the interruption is at most 12 hours when the onward destination is in an Annex 1 country and at most 24 hours otherwise. Domestic-origin itineraries with a connection within these windows are taxed once, at the rate of the final destination. Longer stopovers split the journey into separately taxable departures.
* **Domestic flights**: Germany is in Annex 1, so domestic departures pay the band 1 rate. Flights to and from German, Danish and Dutch North Sea islands without a tide-independent road or rail link are exempt where the island is origin or destination.
* Other exemptions (s.5): crew, flights for sovereign purposes (military, police, customs), medical flights, and aircraft below a weight threshold used for private purposes.
* No class differentiation; no indexation.

---

## 2. Austria: Flugabgabe (FlugAbgG)

### 2.1 Timeline

| Period | Short (Annex 1) | Medium (Annex 2) | Long (other) | Instrument |
|---|---|---|---|---|
| 2011-04-01 to 2012-12-31 | 8.00 | 20.00 | 35.00 | FlugAbgG, Art. 48 Budgetbegleitgesetz 2011 (BGBl. I Nr. 111/2010) |
| 2013-01-01 to 2017-12-31 | 7.00 | 15.00 | 35.00 | Abgabenaenderungsgesetz 2012 (BGBl. I Nr. 112/2012) |
| 2018-01-01 to 2020-08-31 | 3.50 | 7.50 | 17.50 | BGBl. I Nr. 44/2017 (halving) |
| 2020-09-01 onwards | 12.00 flat; 30.00 if airport-to-airport distance < 350 km | | | Konjunkturstaerkungsgesetz 2020 (BGBl. I Nr. 96/2020) |

The Act entered into force on 1 Jan 2011 but the levy only arose for departures after 31 Mar 2011 (and for legal transactions concluded after 31 Dec 2010). The 2013 cut was explicitly motivated by competitiveness vis-a-vis Germany and neighbouring airports; the long-haul rate was left at 35 because it was already below the German 42.18. The 2018 halving (decided March 2017) applied to departures after 31 Dec 2017. The 2020 reform, part of the eco-social agenda packaged into the COVID-era Konjunkturstaerkungsgesetz, abolished the three distance classes and introduced a flat EUR 12 with a punitive EUR 30 for ultra-short routes, applying to departures after 31 Aug 2020. The rate is not indexed and remained EUR 12 / EUR 30 through 2026; the debate in 2025-26 was about cutting it, not raising it.

### 2.2 Band definitions

2011-Aug 2020: the rate depended on the country or territory of the **destination airport (Zielflugplatz)**:

* **Annex 1 - Kurzstrecke**: countries and territories whose largest airport lies within roughly 2,500 km of Vienna-Schwechat. Partial list from the statute: Egypt, North Macedonia, Armenia, Moldova, Albania, Montenegro, Algeria, Monaco, Andorra, Netherlands, Belgium, Norway, Bosnia and Herzegovina, Austria (domestic), Bulgaria, Palestinian territories, Denmark, Poland, Finland, Portugal, Estonia, Romania, Russian Federation, plus the remaining European states, Turkey, Israel, Libya, Tunisia, Morocco, Georgia, Azerbaijan, Lebanon, Syria, Jordan, Iraq, Cyprus, Malta, Ukraine, Belarus (list reconstructed from partial snippets; treat the full membership as medium confidence).
* **Annex 2 - Mittelstrecke**: countries not in Annex 1 whose largest airport is within about 6,000 km of Vienna-Schwechat: Gulf states (Bahrain, Qatar, Kuwait, Oman, UAE, Saudi Arabia, Yemen), Iran, Afghanistan, Pakistan, Central Asian republics, and West, Central and East African states (e.g. DR Congo). The 6,000 km logic is reported by the Wikipedia article "Luftverkehrabgabe"; the statutory annex itself is a closed list.
* **Langstrecke**: everything else.

Both annexes were modified by BGBl. I Nr. 112/2012 (2013). From 1 Sep 2020 the destination-country annexes no longer drive the rate; only the **great-circle distance between the Austrian departure airport and the destination airport** matters (below 350 km => EUR 30, otherwise EUR 12). BGBl. I Nr. 96/2020 still amended Annex 1, suggesting the annex survives for other purposes (e.g. reporting); this was not verified.

### 2.3 Exemptions and special treatment (s.3 FlugAbgG)

* Children under two years without their own seat.
* Flight crew, including crew positioning flights.
* Training flights and parachute-jump flights.
* Flights exclusively for military, medical or humanitarian purposes.
* **Transit and transfer passengers** after a scheduled stopover at a domestic airport of less than 24 hours.
* Departures after an unscheduled landing.
* Aircraft with maximum take-off weight up to and including 2,000 kg.
* State aircraft (Art. 3 Chicago Convention).
* **Domestic flights** are taxable (Austria is in Annex 1; since Sep 2020 most domestic city pairs are under 350 km and pay EUR 30).
* No class differentiation; no indexation.

---

## 3. Netherlands: Vliegbelasting

### 3.1 First tax, 2008-2009

Introduced by the Belastingplan 2008 (Wet van 20 december 2007, Stb. 2007, 562) as Hoofdstuk VII of the Wet belastingen op milieugrondslag, effective **1 Jul 2008**:

* **EUR 11.25** per passenger when the destination is in an EU member state **or** at most 2,500 km (flight distance) from the departure airport;
* **EUR 45.00** for all other destinations.

Collected from the airport operator, who passed it on to airlines. Exempt: transfer passengers (passengers using the Dutch airport only to connect), children under two, and aircraft with MTOW up to 8,616 kg (outside the "vliegtuig" definition). Because of traffic leakage to Dusseldorf, Weeze and Brussels during the 2008-09 crisis, the Fiscaal stimuleringspakket (Wet van 1 juli 2009, Stb. 2009, 280; KB Stb. 2009, 281) set both rates to **zero from 1 Jul 2009**; the chapter was then repealed by the Belastingplan 2010 (wetsvoorstel 32132) with effect from 1 Jan 2010.

### 3.2 Second tax, 2021 onwards (flat rate)

Wet vliegbelasting (Stb. 2020, 549), amended by the novelle of 16 Dec 2020 (Stb. 2020, 550) which removed the planned cargo-aircraft component, entered into force on **1 Jan 2021** (Besluit Stb. 2020, 552). The rate is flat per departing passenger, indexed annually by a fixed price-development formula:

| Year | Rate (EUR) | Note |
|---|---|---|
| 2021 | 7.845 | base EUR 7.45 indexed |
| 2022 | 7.947 | |
| 2023 | 26.43 | Belastingplan 2023: +EUR 17.95 |
| 2024 | 29.05 | aircraft threshold cut from 8,616 kg to 4,000 kg MTOW from 1 Jul 2024 (Stb. 2024, 196) |
| 2025 | 29.40 | |
| 2026 | 30.25 | applies to all 2026 departures even if ticketed earlier |

Exemptions: transfer passengers (overstappers) are exempt; children under two are not counted as passengers; domestic flights are taxable like any other departure (there are hardly any). No class differentiation.

### 3.3 Differentiated tax from 2027 (enacted)

Wet differentiatie vliegbelasting (Wet van 17 december 2025, Stb. 2025, 446; Eerste Kamer 16 Dec 2025) replaces the flat rate from **1 Jan 2027** with three categories based on the **passenger's final destination**, assigned through closed country lists built on great-circle distance from Amsterdam to the capital of the destination state:

* **Bijlage A** (capital approx. <= 2,000 km; plus all EU member states, EU outermost regions within 3,500 km, and the Caribbean Netherlands): **EUR 29.40**
* **Bijlage B** (capital approx. 2,000-5,500 km; Tunisia and Algeria placed here deliberately so that all North African destinations are taxed alike): **EUR 47.24**
* **Category C** (not in A or B; capital approx. > 5,500 km): **EUR 70.86**

Amounts are at 2025 price level and will be indexed for 2027. Expected extra revenue EUR 257 million; average tax about EUR 38.51. Transfer exemption continues. Recorded in the CSV with `confidence = medium` because the law is not yet in force at compilation date and the indexed 2027 amounts are not yet published.

---

## 4. Confirmed vs. uncertain

Confirmed from primary or official sources: all German statutory and applied rates 2011-2026 (every ordinance located on gesetze-im-internet.de / juris / Haufe, cross-checked with Destatis), the German annex logic and lists, the 12h/24h transfer rule and s.5 exemptions; all four Austrian rate regimes with BGBl numbers and the s.3 exemption list; both Dutch tax episodes with Staatsblad citations, the 2008 band definition, every flat rate 2021-2026, the 2024 weight-threshold change and the 2027 differentiated amounts.

Uncertain or only indirectly confirmed:
* Germany 2013: rates confirmed (Destatis), but the amending act of 5 Dec 2012 and its BGBl page were seen only in a snippet; 2017 and 2018 ordinances confirmed via Destatis and umwelt-online rather than the gesetze-im-internet page.
* Germany: content of the June 2026 amendment to Annexes 1 and 2 not verified.
* Austria: the explicit 2,500 km / 6,000 km thresholds for Annex 1/2 come from secondary sources (Wikipedia, BMF handbook snippets); the full country membership of the Austrian annexes was only partially visible, so the CSV describes the annexes by logic plus partial list. Whether Annex 1 retained a function after Sep 2020 is unverified.
* Netherlands 2008: the 8,616 kg aircraft threshold is confirmed for the 2021 law and described as the original definition; its presence in the 2008 text is inferred.
* Netherlands 2027: indexed 2027 amounts and full Bijlage A/B lists not yet published in the sources reached.

---

## 5. Sources

Germany
* LuftVStG consolidated text and annexes: https://www.gesetze-im-internet.de/luftvstg/BJNR188510010.html ; https://www.gesetze-im-internet.de/luftvstg/__11.html ; https://www.gesetze-im-internet.de/luftvstg/anlage_1.html ; https://www.gesetze-im-internet.de/luftvstg/anlage_2.html ; https://www.gesetze-im-internet.de/luftvstg/__2.html ; https://www.gesetze-im-internet.de/luftvstg/__5.html
* Zoll tax-rate page: https://zoll.de/EN/Businesses/Aviation-tax/Taxation-principles/Tax-rates/tax-rates_node.html
* LuftVStAbsenkV 2012: https://www.gesetze-im-internet.de/luftvstabsenkv_2012/BJNR273200011.html
* LuftVStFestV 2014 / 2015 / 2016: https://www.gesetze-im-internet.de/luftvstfestv_2014/BJNR438300013.html ; https://www.gesetze-im-internet.de/luftvstfestv_2015/BJNR182200014.html ; https://www.gesetze-im-internet.de/luftvstfestv_2016/BJNR197800015.html
* LuftVStAbsenkV 2019: https://www.gesetze-im-internet.de/luftvstabsenkv_2019/BJNR224400018.html
* LuftVStAbsenkV 2020 (Jan-Mar): https://www.haufe.de/id/norm/luftverkehrsteuer-absenkungsverordnung-2020-bis-31032020-1-steuersaetze-2020-HI13563622_p1.html ; (Apr-Dec): https://www.gesetze-im-internet.de/luftvstabsenkv_2020_2/BJNR076200020.html
* LuftVStAbsenkV 2021 / 2022 / 2023 / 2024: https://www.gesetze-im-internet.de/luftvstabsenkv_2021/BJNR276200020.html ; https://www.gesetze-im-internet.de/luftvstabsenkv_2022/BJNR506700021.html ; https://www.gesetze-im-internet.de/luftvstabsenkv_2023/BJNR206200022.html ; https://www.umwelt-online.de/recht/allgemei/steuer/luftvstabsenkv24.htm
* Act of 12 Dec 2019 (BGBl. I S. 2492): https://umwelt-online.de/recht/allgemei/steuer/z19_2492.htm ; Bundesregierung explainer: https://www.bundesregierung.de/breg-de/themen/klimaschutz/luftverkehrsteuer-1681874
* Zweites Haushaltsfinanzierungsgesetz 2024: https://www.bundesregierung.de/breg-de/service/gesetzesvorhaben/haushaltsfinanzierungsgesetz-2252042 ; https://umwelt-online.de/recht/allgemei/steuer/z24_0107.htm
* 2026 reduction: https://www.bundesregierung.de/breg-de/aktuelles/senkung-luftverkehrsteuer-2418542 ; https://www.umwelt-online.de/recht/allgemei/steuer/z26_0182.htm ; https://www.bundesfinanzministerium.de/Content/DE/Pressemitteilungen/Finanzpolitik/2026/04/2026-04-01-senkung-der-luftverkehrsteuer.html ; BR-Drs. 196/26: https://dserver.bundestag.de/brd/2026/0196-26.pdf
* Destatis Luftverkehrsteuer statistics (rate tables 2011-2021): https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/DEHeft_derivate_00071354/2140960217004_akt_24062022.pdf
* BVerfG 1 BvF 3/11: https://www.haufe.de/id/entscheidung/bverfg-urteil-vom-05112014-1-bvf-311-HI7399340.html

Austria
* FlugAbgG consolidated (RIS): https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20007051 ; s.5: https://www.ris.bka.gv.at/Dokumente/Bundesnormen/NOR40225646/NOR40225646.html ; s.3: https://www.ris.bka.gv.at/Dokumente/Bundesnormen/NOR40225648/NOR40225648.html
* BGBl. I Nr. 111/2010 (Budgetbegleitgesetz 2011): https://www.ris.bka.gv.at/Dokumente/Erv/ERV_2010_1_111/ERV_2010_1_111.pdf
* BGBl. I Nr. 96/2020 (KonStG 2020): https://ris.bka.gv.at/eli/bgbl/I/2020/96 ; BMF summary: https://www.bmf.gv.at/rechtsnews/steuern-rechtsnews/neue-gesetze/2020/konstg-2020.html
* BGBl. I Nr. 44/2017: https://www.bmf.gv.at/rechtsnews/steuern-rechtsnews/archiv-gesetze-und-verordnungen/2017/flugabgabegesetz.html
* Flugabgaberichtlinien (Findok): https://findok.bmf.gv.at/findok/resources/pdf/0b995a40-959d-42fd-a4b8-016a78917b6a/74910.1.X.X.pdf ; BMF Handbuch Flugabgabe: https://www.bmf.gv.at/dam/jcr:e62e5137-e516-40e1-b669-2fbe49bb8682/BMF_Handbuch_Flugabgabe_Luftfahrzeughalter.pdf
* USP overview: https://www.usp.gv.at/themen/steuern-finanzen/weitere-steuern-und-abgaben/flugabgabe.html
* Parliamentary answer on 2013 cut: https://www.parlament.gv.at/dokument/XXIV/AB/15071/fname_321815.pdf
* Wikipedia (secondary, annex logic): https://de.wikipedia.org/wiki/Luftverkehrabgabe

Netherlands
* Belastingdienst vliegbelasting page: https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/overige_belastingen/belastingen_op_milieugrondslag/vliegbelasting
* Rijksoverheid overview: https://www.rijksoverheid.nl/onderwerpen/luchtvaart/belasting-op-luchtvaart
* 2008-09 tax, abolition memorandum (kst 32132-3): https://zoek.officielebekendmakingen.nl/kst-32132-3.html ; zero-rate notice: https://zoek.officielebekendmakingen.nl/stcrt-2009-10309.html ; Stb. 2009, 281: https://zoek.officielebekendmakingen.nl/stb-2009-281.html ; evaluation annex: https://zoek.officielebekendmakingen.nl/blg-865793.pdf
* Wet vliegbelasting entry into force (Stb. 2020, 552): https://zoek.officielebekendmakingen.nl/stb-2020-552.pdf ; https://www.taxence.nl/nieuws/wet-vliegbelasting-treedt-in-werking-per-1-januari-2021/
* Weight threshold 2024 (Stb. 2024, 196): https://zoek.officielebekendmakingen.nl/stb-2024-196.pdf
* Wet differentiatie vliegbelasting (Stb. 2025, 446): https://zoek.officielebekendmakingen.nl/stb-2025-446.html ; dossier 36815: https://www.eerstekamer.nl/wetsvoorstel/36815_wet_differentiatie ; nader rapport: https://www.rijksoverheid.nl/binaries/rijksoverheid/documenten/kamerstukken/2025/09/16/nader-rapport-wetsvoorstel-wet-differentiatie-tarief-vliegbelasting/Nader-rapport-inzake-het-wetsvoorstel-Wet-differentiatie-vliegbelasting.pdf
* CE Delft (2024) Belastingen en heffingen in de luchtvaart: https://cedelft.eu/wp-content/uploads/sites/2/2025/01/CE_Delft_240248_Belastingen-en-heffingen-in-de-luchtvaart_def.pdf

Cross-country
* CE Delft (2019) Taxes in the Field of Aviation and their impact: https://cedelft.eu/publications/taxes-in-the-field-of-aviation-and-their-impact/
