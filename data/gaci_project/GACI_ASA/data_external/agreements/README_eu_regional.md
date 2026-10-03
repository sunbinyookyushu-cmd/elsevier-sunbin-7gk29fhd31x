# EU and regional/multilateral air transport liberalisation agreements, 1990-2024

Companion file: `eu_regional_agreements.csv` (310 rows; one row per agreement x partner country / member state).
Compiled 2026-10-03 from web-search snippets only (WebFetch and direct HTTPS were blocked in the build
environment, and the search budget was exhausted before every date could be confirmed). **No date was
invented**: a blank date cell means the date was not confirmed by a retrieved source. Where the compiler
has a recollected date that could not be verified, it is written in `notes` as `UNVERIFIED recollection: ...`
so it can be checked against EUR-Lex before use. The `confidence` column is `high` (date read directly from
an official/primary snippet), `medium` (date confirmed in part, e.g. month/year, or from a secondary
summary of a primary table), or `low` (partner confirmed, date not).

## Column conventions

| column | meaning |
|---|---|
| `agreement` | agreement name; `- member state` suffix marks per-EU-member rows (EU-US only) |
| `bloc_or_party_a` | EU, ASEAN, AU, LACAC, MALIAT parties, Japan, Korea, Australia... |
| `party_b_country`, `party_b_iso3` | partner (or, in block C, the state entering the single market; in EU-US member rows, USA) |
| `agreement_type` | comprehensive_open_skies, common_aviation_area, comprehensive_euromed, horizontal_nationality_clause, internal_liberalisation_package, single_market_membership, regional_multilateral_ASA, plurilateral_open_skies, bilateral_open_skies(_MoU), ... |
| `date_signed` | signature (for ASEAN/CLAC/MALIAT rows: signature or accession deposit) |
| `date_provisional` | start of provisional application (EU practice: usually from signature or first day of month after notifications) |
| `date_in_force` | formal entry into force; **for ASEAN MAAS/MAFLPAS rows this is the member's own ratification date**; for block C it is the single-market entry date |
| `source_quote` | verbatim or near-verbatim snippet supporting the dates |

## Block summary (confirmed = at least one of signed / in-force populated)

| block | rows | signed date present | provisional date present | in-force date present | high / medium / low |
|---|---|---|---|---|---|
| A. EU comprehensive agreements | 66 | 63 | 34 | 20 | 37 / 12 / 17 |
| B. EU horizontal agreements | 51 | 9 | 0 | 5 | 7 / 7 / 37 |
| C. Internal packages + enlargement | 32 | 3 | 0 | 32 | 30 / 2 / 0 |
| D. Regional multilateral / open-skies programmes | 161 | 95 | 0 | 73 | 42 / 87 / 32 |

### A. EU comprehensive ("neighbourhood" and "horizontal-plus") agreements - key dates confirmed

| agreement | signed | provisional | in force | status note |
|---|---|---|---|---|
| EU-US ATA (1st stage) | 2007-04-30 (25 & 30 Apr) | 2008-03-30 | - | still provisionally applied as far as sources show |
| EU-US 2nd-stage Protocol | 2010-06-24 | 2010-06-24 | - | Decision 2010/465/EU |
| EU-Canada | 2009-12-17 (17-18 Dec) | 2009-12-17 | 2019-04-15 | Canada records 2019-05-16 |
| EU-Morocco Euro-Med | 2006-12-12 | 2006-12-12 | 2018-01-22 | Decision 2006/959/EC |
| ECAA (W. Balkans + NO/IS) | 2006-06-09 | (per party, blank) | 2017-12-01 | 9 partner rows |
| EU-Georgia CAA | 2010-12-02 | blank | 2020-08-02 | |
| EU-Jordan Euro-Med | 2010-12-15 | blank | 2020-08-02 | OJ L 430, 18.12.2020 |
| EU-Moldova CAA | 2012-06-26 | blank | 2020-08-02 | Decision (EU) 2020/951 |
| EU-Israel Euro-Med | 2013-06-10 | 2013-06-10 (administrative implementation) | 2020-08-02 | |
| EU-Ukraine CAA | 2021-10-12 | blank (applied provisionally; start not confirmed) | - | Ukraine ratified 2022-02-17 |
| EU-Qatar ATA | 2021-10-18 | 2021-10-18 | - | MS ratifications ongoing (FI 2025-01-14) |
| EU-Armenia CAA | 2021-11-15 | blank (administrative application Jan 2023) | - | NL treaty DB shows 2023-03-16 |
| EU-ASEAN CATA | 2022-10-17 | blank | - | 10 ASEAN member rows, ratifications blank |
| EU-Tunisia Euro-Med | blank | - | - | initialled 2017-12-11; signing authorised 2021-06-28; signature not confirmed |
| EU-Switzerland | 1999-06-21 | - | 2002-06-01 | |
| EEA (NO, IS; LI) | 1992-05-02 | - | 1994-01-01 (LI 1995-05-01) | |
| EU-UK TCA Title I | 2020-12-30 | 2021-01-01 | 2021-05-01 | |

EU-US member-state rows (27 = EU membership at signature, incl. UK, excl. Croatia) flag prior US open-skies
bilaterals with dates from the ICAO/US DOT list: NL 1992-10-14, FI 1995-03-24, BE 1995-03-01 (prov.),
DK & SE 1995-04-26, LU 1995-06-06, AT 1995-06-14, DE 1996-02-29 (prov.), RO 1998-07-15, IT 1998-11-11 (prov.),
PT 1999-12-22, MT 2000-10-12, PL 2001-05-31, FR 2001-10-19. CZ and SK are believed to have had open skies
(1996, 2001) but were not confirmed; UK/IE/ES/GR/HU/CY/SI/EE/LV/LT/BG had none in the retrieved lists.

### B. Horizontal agreements - confirmed signature dates
Chile 2005-10-06; Lebanon 2006-07-07; Singapore 2006-06-09; Australia 2008-04-29 (also EIF); Mexico 2010-12-15;
Brazil 2011-07-14 (conflicting 2010 date in one EP summary); Cabo Verde 2011-03-23; China 2019-05 (day 20 unverified);
Bangladesh 2024-06-07. Entry-into-force only: Georgia and Moldova horizontals 2008-02-25; Kyrgyz Rep. 2008-04-28
(signed 2007); Viet Nam 2011-05-31. Partner list (41 countries + WAEMU's 8 members) assembled from the Commission
"Horizontal Agreements" page, the Commission 2006 annual report and Transportstyrelsen's list of agreements in force.
All other signature dates are blank with an UNVERIFIED recollection in `notes`.

### C. Internal liberalisation and enlargement
First package adopted Dec 1987 (applied 1988-01-01), second package 1990 (applied 1990-11-01), third package
Regs 2407/92-2409/92 applied 1993-01-01, full cabotage 1997-04-01. Single-market entry: EU-12 1993-01-01;
AT/FI/SE 1995-01-01 (already in EEA aviation market from 1994-01-01); 10 states 2004-05-01; BG/RO 2007-01-01;
HR 2013-07-01. EEA (Norway, Iceland) 1994-01-01, Liechtenstein 1995-05-01; Switzerland 2002-06-01 (block A).

### D. Regional multilateral agreements
- **ASEAN MAAS** signed 2009-05-20 (Manila), EIF 2009-11-23; per-member ratification 2009-07-23 (SG) ... 2011-11-29 (ID). Protocols 5/6 (capital cities) EIF 2009-12-22; ID ratified 2014-05-30, SG 2016-03-11.
- **ASEAN MAFLPAS** signed 2010-11-12 (Bandar Seri Begawan), EIF 2011-06-30; last ratifications ID and LA 2016-04-07 (= effective ASEAN Open Skies / ASAM). VN date not retrieved.
- **MAFLAFS** (cargo) signed 2009-05-20; ratification table not retrieved.
- **ASEAN-China ATA** signed 2010-11-12 (9 members), China 2010-11-19, Thailand 2011-01-13; China ratified 2011-08-09.
- **MALIAT** adopted 2001-05-01 (Kona), EIF 2001-12-21; accessions Peru 2001-12-21 (withdrew 2005-01-15), Samoa 2002-07-04 (withdrew 2019-03-09), Tonga 2003-09-19, Cook Islands 2006-03-08, Mongolia 2007-08-22.
- **Yamoussoukro Decision** 1999-11-14; OAU endorsement 2000-07-12; EIF contested (2000-08-12 vs "binding 2002") - left blank. **SAATM** launched 2018-01-28 with 23 states (listed); CAR, Chad, Gambia joined May 2018; 38 members by 2024 (others not identified).
- **Andean Community Decision 582** May 2004 (day 4 unverified), 5 member rows.
- **LACAC/CLAC Multilateral Open Skies** signed 2010-11-04 (Punta Cana), EIF 2019-04-06 after Brazil's deposit (2019-03-07); Panama 2013-01-15, Uruguay 2017-12-15; CL/GT/HN/PY/DO provisional application.
- **Australia-NZ**: SAM 1996-11-01; Open Skies signed 2002-08-08, EIF 2003-08-25.
- **Japan open skies** (MLIT table, snippet-derived): US 2010-10-25, KR 2010-12-22, SG 2011-01-19, ..., CN 2012-08-08, ..., MM 2013-10-24; 28 partner rows.
- **Korea open skies**: US 1998, JP 2007, CN 2006 (Shandong/Hainan), TH 2006, MY 2007, VN 2008, MM/KH 2010, LA 2011, PY 2012, PH 2017, SG/BN 2019 (years only); 23 further partners listed in a 2010 status report without dates (many cargo-only).

## Legal logic: the 2002 "open skies" judgments and the horizontal agreements

On 5 November 2002 the Court of Justice ruled in Cases C-466/98 (UK), C-467/98 (Denmark), C-468/98 (Sweden),
C-469/98 (Finland), C-471/98 (Belgium), C-472/98 (Luxembourg), C-475/98 (Austria) and C-476/98 (Germany) that
(i) the nationality (ownership-and-control) clauses in member states' bilateral air services agreements with the
United States discriminated against airlines of other member states and so infringed the right of establishment
(then Art. 43 EC, now Art. 49 TFEU), and (ii) the Community had exclusive external competence over certain
matters (intra-Community fares of non-Community carriers, computer reservation systems, and areas covered by the
third package), so the member states could not legislate on them bilaterally.

Consequences that matter for identification:

1. Every bilateral of every member state with every third country containing a standard nationality clause
   became legally defective at the same moment, irrespective of traffic on the route. The Commission (COM(2002)
   649, COM(2003) 94) and the Council (June 2003 conclusions, Regulation (EC) No 847/2004 of 29 April 2004 on the
   negotiation and implementation of air service agreements) set up a two-track remedy: (a) **horizontal agreements**
   negotiated by the Commission under the "horizontal mandate" that replace, in one instrument, the nationality clause
   in all member-state bilaterals with a given third country by a "Community/EU carrier" designation clause (plus
   fuel-taxation, pricing and competition compatibility clauses) **without adding traffic rights**; and (b)
   member-state-by-member-state amendments under Reg. 847/2004.
2. The horizontal agreements therefore (i) do not change capacity, frequency, route or pricing provisions, (ii) are
   signed in a sequence driven by the Commission's negotiating queue and partners' legal/administrative readiness,
   and (iii) apply to all member states simultaneously whatever their bilateral traffic with the partner. Their timing
   is thus plausibly exogenous to route-level demand between any individual member state and the partner. The treatment
   they deliver is the designation freedom: any EU carrier established in a member state can be designated under that
   member state's bilateral (the key channel for low-cost and multi-base carriers), which is the variable of interest
   for a panel on airline entry/competition rather than market access per se.
3. The **comprehensive ("horizontal-plus"/neighbourhood) agreements** go further (market access, regulatory
   convergence) and their negotiation is partly demand-driven (US, Canada, Qatar, Morocco), so they are better treated
   as endogenous policy events; their *entry-into-force* dates, however, are mostly determined by the slowest national
   ratification (e.g. the cluster of 2020-08-02 EIFs for Georgia, Jordan, Moldova and Israel results from a single
   batch of Council conclusion decisions on 26 June 2020 and the final deposit on 2 July 2020) and are therefore not
   informative about demand; use `date_provisional` as the economic treatment date for EU agreements.
4. The internal packages and enlargement dates (block C) are set by treaty calendar and accession negotiations
   spanning all sectors, again plausibly exogenous to aviation demand on specific routes.

## Count of agreements by year (first dated event of each distinct agreement; signature, else entry into force)

| year | distinct agreements | row-level events (agreement x partner) |
|---|---|---|
| 1987 | 1 | 1 |
| 1990 | 1 | 1 |
| 1992 | 2 | 4 |
| 1993 | 1 | 12 |
| 1995 | 1 | 3 |
| 1996 | 1 | 1 |
| 1997 | 1 | 1 |
| 1999 | 2 | 2 |
| 2001 | 1 | 6 |
| 2002 | 1 | 2 |
| 2003 | 0 | 1 |
| 2004 | 2 | 15 |
| 2005 | 1 | 1 |
| 2006 | 2 | 13 |
| 2007 | 3 | 31 |
| 2008 | 0 | 4 |
| 2009 | 4 | 22 |
| 2010 | 7 | 35 |
| 2011 | 0 | 13 |
| 2012 | 1 | 12 |
| 2013 | 2 | 5 |
| 2015 | 0 | 2 |
| 2018 | 1 | 23 |
| 2019 | 0 | 1 |
| 2020 | 1 | 1 |
| 2021 | 3 | 3 |
| 2022 | 2 | 11 |
| 2024 | 0 | 1 |

(Horizontal agreements whose signature date is blank - about 40 partners, 2005-2020 - are excluded from this table;
once verified they will add mostly to 2006-2010.)

## Main uncertainties (to resolve before using as treatment dates)
1. **Horizontal agreement signature dates**: only 9 of ~49 partners confirmed; the rest are recollections flagged
   UNVERIFIED. Primary check: EUR-Lex Council decisions "on the signature and provisional application of the Agreement
   between the European Community and [X] on certain aspects of air services" (CELEX 2200xA...), or the Commission
   "Status of aviation relations by country" pages.
2. **Provisional application start dates** for Georgia, Jordan, Moldova, Ukraine, Armenia, ECAA parties, EU-ASEAN CATA:
   decisions authorising provisional application exist, but the operative start date (first day of month after exchange
   of notes) was not retrieved.
3. **EU-US ATA formal entry into force**: not confirmed; treated as provisionally applied since 2008-03-30.
4. **EU-Tunisia**: signature not confirmed (only Council authorisation 2021-06-28).
5. **Yamoussoukro Decision EIF** (2000-08-12 vs 2002) and **SAATM** later joiners (only 28 of 38 identified).
6. **US open-skies status of CZ, SK, HU, SI** before 2007.
7. **Japan/Korea dates** are from secondary summaries of ministry tables (Japan: day-level, medium; Korea: year-level).
8. ASEAN Protocol 5/6 Thailand and Viet Nam dates may be transposed in the snippet; Viet Nam MAFLPAS date missing.

## Sources (URLs as retrieved)
- EP Legislative Observatory (OEIL) summaries: EU-US https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1479639 ; Protocol 2010 ...?id=1687537 ; EU-Canada ...?id=1583129 ; EU-Morocco ...?id=1521570 ; EU-Georgia ...?id=1584838 ; EU-Jordan ...?id=1622436 ; EU-Moldova ...?id=1622429 ; EU-Israel ...?id=1622448 ; EU-Tunisia ...?id=1657396 ; Brazil ...?id=1127283 ; Mexico ...?id=1174489 ; Vietnam ...?id=1153370
- EUR-Lex: Decision (EU) 2018/145 (ECAA conclusion); Decision (EU) 2020/951 (Moldova); 2020/952 (Israel); 2020/899 (Jordan protocol); 2021/1404 (Tunisia signing); 2021/1897 (Ukraine); 2021/2102 (Armenia); 2010/417/EC (Canada); 2006/959/EC (Morocco); summary "Agreements on air services" https://eur-lex.europa.eu/EN/legal-content/summary/agreements-on-air-services.html
- European Commission, Mobility and Transport: ECAA page; Switzerland page; Israel page; Georgia page; Republic of Moldova page; Singapore page; Kyrgyz Republic page; Australia page; Brazil page; Cape Verde page; UEMOA page; Horizontal Agreements page https://transport.ec.europa.eu/transport-modes/air/international-aviation/external-aviation-policy/horizontal-agreements_en ; news 2019-05-24 (China), 2018-10-17 (Korea initialling), 2021-11-15 (Armenia), 2022-10-17 (ASEAN); press release IP/24/3143 (Bangladesh)
- Transportstyrelsen (Swedish Transport Agency) "EU agreements" list https://www.transportstyrelsen.se/en/aviation/Air-operators/Air-services-agreements/EU-agreements/ and Qatar/Ukraine/Jordan sub-pages
- Dutch Treaty Database (verdragenbank.overheid.nl) entries 012463 (Jordan), 012755 (Israel), 013673 (Qatar), 013681 (Armenia), 013028 (Ukraine)
- Court of Justice press release CP02/89 (5 Nov 2002) https://curia.europa.eu/en/actu/communiques/cp02/aff/cp0289en.htm ; Mondaq note 6 Jan 2003
- ICAO Compendium "List partners OSA US" https://www.icao.int/sites/default/files/sp-files/sustainability/Documents/Compendium_FairCompetition/List%20partners%20OSA%20US.pdf ; US State Dept Open Skies Partners https://www.state.gov/division-for-transportation-affairs/open-skies-partners
- OECD DAF/COMP(2014)22 (EU packages); Eurostat glossary "EU enlargements"
- ASEAN Secretariat, Ratification Status of Air Transport Agreements (27 Feb 2025) https://asean.org/wp-content/uploads/2025/03/Ratification-Status-of-Air-Transport-Agreements_27-Feb-2025rev-1.pdf ; CIL-NUS treaty database pages for MAAS, MAFLPAS, MAFLAFS, ASEAN-China ATA protocols
- NZ MFAT treaty pages (MALIAT and Protocol); US DOT MALIAT page
- African Union press releases (SAATM launch, 4th Ministerial Working Group May 2018, ICAO Assembly statement); Wikipedia "Yamoussoukro Decision"
- LACAC/CLAC Multilateral Open Skies page https://clac-lacac.org/multilateral-open-skies-agreement-2/?lang=en ; UNTS I-57687; ICAO Compendium "RegionalAgreements.pdf" (Andean Decision 582)
- ICAO Trans-Tasman case study https://www.icao.int/sites/default/files/sp-files/sustainability/Documents/TransTasmanMarket_En.PDF
- MLIT Japan open-skies table https://www.mlit.go.jp/koku/content/001881829.pdf ; JCAB "Updates on Japan's international aviation policy" (2011)
- APEC (2011) "Air transport in Korea and Northeast Asia"; knaviation.net (Korea-Singapore/Brunei 2019); Korea Times (2012 Paraguay); White House statement 9 June 1998 (US-Korea)
- Herbert Smith Freehills / Norton Rose Fulbright notes on EU-UK TCA aviation title (Dec 2020)
