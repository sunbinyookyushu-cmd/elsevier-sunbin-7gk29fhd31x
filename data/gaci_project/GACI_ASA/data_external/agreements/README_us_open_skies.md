# US bilateral Open Skies partners, 1990-2024 — `us_open_skies_partners.csv`

Compiled 2026-10-03 for the GACI_ASA panel. Research constraint: web **fetching was blocked**;
every fact below was recovered from search-engine snippets of the sources listed (200 targeted
WebSearch queries). Dates that could not be read from a snippet are left **blank** and flagged in
`notes` — nothing has been inferred or invented. Rows marked `confidence=low` need manual
verification before use.

## 1. Sources (in order of authority)

| # | Source | Used for |
|---|--------|----------|
| 1 | U.S. Dept. of State, Bureau of Economic & Business Affairs, *Open Skies Partners* list, edition of **19 Aug 2013**, hosted by ICAO: `https://www.icao.int/sites/default/files/sp-files/sustainability/Documents/Compendium_FairCompetition/List%20partners%20OSA%20US.pdf` | Status (In Force / Provisional / C&R / N/A) and date for every partner 1992-2013 |
| 2 | U.S. Dept. of State, *Open Skies Partners*, edition of **14 Nov 2016**: `https://2009-2017.state.gov/documents/organization/206046.pdf` | Same, 2013-2016; filled gaps (Slovakia, Ghana, Rwanda, Benin, Senegal, Poland, Oman, Bosnia, Cook Is., Kuwait, Liberia, Georgia, Croatia, Kenya, Laos, Zambia, St Kitts, Montenegro, Macedonia, Guyana, Togo, Serbia, Seychelles, Yemen, Burundi, Curaçao) |
| 3 | State Dept. *Open Skies Partners* current page: `https://www.state.gov/division-for-transportation-affairs/open-skies-partners` (and 2021-2025 archive) | Membership list (no dates visible in snippets) |
| 4 | U.S. DOT, *Open Skies Agreements Currently Being Applied* (last updated 2026-03-03): `https://www.transportation.gov/policy/aviation-policy/open-skies-agreements-being-applied` | Current membership (incl. Sierra Leone, Guinea, St Vincent, Lebanon, Fiji, Kazakhstan…); MALIAT page |
| 5 | DOT / State press releases (transportation.gov briefing-room; state.gov; pacom.mil mirrors) | Signing dates 2007-2024 (Canada, Australia, Japan, Brazil, Colombia, Montenegro, Macedonia, St Kitts, Mongolia, UK, Bangladesh, Moldova, Angola, Fiji, DR, Nigeria EIF) |
| 6 | Treaty databases: Dutch *verdragenbank.overheid.nl* (Aruba, Neth. Antilles, Sint Maarten); UN Treaty Series (Qatar); Turkish MFA; Omani decree.om | Signature / EIF dates for those partners |
| 7 | Trade press (Flight Global, Aviation Week, ATW, FreightWaves, CAPA, ch-aviation, exyuaviation, Stabroek News, Caribbean Today, etc.) and White House fact sheets (Clinton 2000 Nigeria/Tanzania; Bush 2001 Poland) | Phase-in carve-outs, signing ceremonies, cross-checks |
| 8 | EU: European Parliament OEIL / Commission COM(2010)208-209; Pillsbury note | EU-US ATA dates (signed 25 & 30 Apr 2007; provisional application 30 Mar 2008; 2nd-stage Protocol 24 Jun 2010) |

Academic appendices (Winston & Yan 2015 AEJ:EP; Micco & Serebrisky 2006; Cristea, Hillberry & Mattoo 2015)
were searched for but their partner-date tables are **not exposed in snippets**; they were not used.
The State lists are the primary source those papers themselves rely on.

## 2. How dates were determined

The State Department list gives, for each partner, one *date* and a *status*:

* **In Force** – date the agreement entered into force (often the signature date when the
  agreement entered into force upon signature). Written to `date_in_force`.
* **Provisional** – provisionally applied from that date pending ratification. Written to
  `provisional_application`; `date_in_force` left blank unless a later EIF was found
  (e.g. Nigeria 2000→2024-05-13; Qatar 2001→2020-08-27; Armenia 2008→2009-06-16).
* **C&R** – "applied on the basis of comity and reciprocity" pending EIF (Namibia, Indonesia,
  Seychelles, Yemen, Bangladesh, Burundi, Ecuador). Treated like provisional application.
* **N/A** – status column blank on the State list (Benin, Barbados, Brazil); the date is the date
  the agreement was reached/applied.

`date_signed` is filled only when a signature date was found in a press release or treaty
database. In several cases the State-list date **precedes** the reported signature (Ghana
10/11/00 vs signed 16 Mar 2001; Poland 5/31/01 vs 18 Jun 2001; India 1/15/05 vs 14 Apr 2005;
Kenya 5/30/08 vs 18 Jun 2008; Croatia initialled 13 Mar 2008 vs signed 4 Feb 2011): the State date
is the date of initialling/first application. For panel treatment, the recommended variable is
`coalesce(date_in_force, provisional_application, date_signed)` — i.e. the first date the open
skies regime was actually applied, which is what the State list reports.

Partial dates: `YYYY` or `YYYY-MM` is used only where the snippet gave no more (Argentina 1999;
Ecuador 2021-12; Angola 2024-10) and is flagged in `notes`.

### Agreement types
* `full open skies` – standard US model text, no transition.
* `open skies with phase-in` – transition annex (Peru 1998, Italy 1998/99, Argentina 1999, Ghana
  2001, Senegal 2000, Poland 2001, France 2001, Colombia 2010, Brazil 2010/11).
* `multilateral MALIAT` – Multilateral Agreement on the Liberalization of International Air
  Transportation (signed Kona/Washington 1 May 2001, EIF 21 Dec 2001; later accessions Samoa 2002,
  Tonga 2003, Cook Islands 2006, Mongolia cargo protocol).
* `multilateral EU-US ATA` – one row per EU member state (27 at signature) plus Croatia (2013 EU
  accession) and Norway/Iceland (2011 ancillary agreement). Treatment date for states without an
  earlier bilateral = **2008-03-30** (provisional application). States with an earlier bilateral
  keep their bilateral row (with `superseded_by` = EU-US ATA) *and* get an EU-US row.

### EU member states with earlier bilateral open skies (all confirmed from State lists)
Netherlands 1992-10-14; Belgium 1995-03-01 (prov.); Finland 1995-03-24; Denmark, Sweden 1995-04-26;
Luxembourg 1995-06-06; Austria 1995-06-14; Czech Rep. 1995-12-08; Germany 1996-02-29 (prov.);
Romania 1998-07-15; Italy 1998-11-11 (prov., signed Dec 1999); Portugal 1999-12-22;
Slovakia 2000-01-07; Malta 2000-10-12; Poland 2001-05-31; France 2001-10-19.
Non-EU: Iceland, Norway 1995 (joined EU-US ATA 2011); Switzerland 1995-06-15 (still bilateral).
No earlier open skies: Bulgaria, Cyprus, Estonia, Greece, Hungary, Ireland, Latvia, Lithuania,
Slovenia, Spain, United Kingdom (Bermuda II) → treated 2008-03-30. (State's 2013 list shows these
as "Provisional 4/30/07", i.e. the signature date, not 30 Mar 2008.)

## 3. Count of new bilateral/MALIAT open skies partners by first-application year
(129 bilateral/MALIAT rows; EU-US rows excluded; year = coalesce(in-force, provisional, signed))

| Year | New partners | Year | New partners |
|------|-------------|------|-------------|
| 1992 | 1 (NLD) | 2010 | 6 |
| 1995 | 10 | 2011 | 2 |
| 1996 | 2 | 2012 | 3 |
| 1997 | 13 | 2013 | 3 |
| 1998 | 5 | 2014 | 3 |
| 1999 | 7 | 2015 | 2 |
| 2000 | 11 | 2016 | 5 |
| 2001 | 5 (+MALIAT) | 2017 | 0 (Sint Maarten signed 2017, EIF 2018) |
| 2002 | 4 | 2018 | 5 |
| 2003 | 2 | 2019 | 1 |
| 2004 | 4 | 2020 | 2 |
| 2005 | 7 | 2021 | 2 |
| 2006 | 4 | 2022 | 0 |
| 2007 | 3 | 2023 | 3 |
| 2008 | 4 (+EU-US 27 states) | 2024 | 3 |
| 2009 | 1 | 2025 | 1 (ATG, out of panel) |
| no date | 5 (Lebanon, São Tomé, Sierra Leone, Guinea, St Vincent) | | |

Rows with a full `date_in_force` (YYYY-MM-DD): **95**. Rows with provisional/C&R date only: 18.
Signed-only: 11. Year- or month-only treatment date: 2 (Argentina, Ecuador) plus Angola's signature
month. Undated: 5. Cumulative count cross-check: 50 partners by Nov 2000 (White House), 56 by
Nov 2001 (Sri Lanka), 60 by Sept 2003, 89 incl. EU in 2007, 100 = Colombia (Nov 2010),
103 = Macedonia (2011), 132 = Mongolia (Jan 2023), ">135" by Oct 2024.

## 4. Known ambiguities / caveats

1. **Argentina** – signed in Buenos Aires in 1999 with phase-in to June 2003; incoming government
   put ratification on hold Jan 2000. Exact signature and EIF dates not recovered; listed as a
   current partner by DOT. Only `date_signed=1999`.
2. **Slovakia** – State list 1/7/00 vs Slovak Spectator "finalised 22 Jan 2001"; unresolved.
3. **Korea** – State list In Force 4/23/98; some sources cite a June 1998 signing.
4. **Laos** – State list 10/3/08; ATW/FreightWaves report a signing ceremony in 2010.
5. **Kenya, Ghana, Poland, India, Croatia** – State-list date precedes press-reported signature
   (initialling vs signature); see §2.
6. **Oman** – 2001 agreement (In Force 9/16/01) and a new ATA signed Muscat 19/21 Dec 2013; both
   kept in one row with the 2013 instrument in `superseded_by`.
7. **Netherlands Antilles → Curaçao / Sint Maarten** – 1998 agreement (prov. 7/14/98, EIF
   2/16/99) dissolved with the Antilles in 2010; Curaçao date 9/26/16 (State 2016 list, status not
   visible); Sint Maarten signed 2017-07-14, EIF 2018-04-01.
8. **Brazil** – reached 2010-12-03, signed 2011-03-19, frequencies phased to Oct 2014, full open
   skies Oct 2015, Senate approval 2018-03-07, EIF 2018-05-21. `date_in_force` = 2018-05-21; for
   a treatment-effect panel the economic liberalisation date (2015-10) may be preferable.
9. **Colombia** – provisional 2010-11-11; full open skies "end of 2012" (1 Jan 2013 from general
   knowledge, not from a snippet).
10. **Qatar** – signed 2001-10-03, provisionally applied; formal EIF 2020-08-27 only.
11. **Nigeria** – provisional 2000-08-26; EIF 2024-05-13.
12. **Yemen** – on State 2016 list (C&R 12/12/12); not confirmed on current DOT list.
13. **Ecuador** – C&R since Dec 2021; signed "16 November" (year not visible, 2022 or 2023).
14. **Angola** – initialled/applied 2023-04-26; signed Luanda Oct 2024 (day not visible).
15. **Congo (Rep.)** – two signing dates reported (2018-12-04 Washington; 2021-04-19).
16. **Kazakhstan** – signed 2019-12-30, ratified by Kazakh parliament 2021-22; EIF and DOT-list
    presence not confirmed.
17. **Lebanon, São Tomé & Príncipe, Sierra Leone, Guinea, St Vincent & Grenadines** – on the DOT
    list (2026 edition) but no date found; left blank. The last three are probably 2024-2025
    agreements. São Tomé's membership itself is unconfirmed.
18. **Antigua & Barbuda** – initialled 2025-01-15 (outside panel window; kept for completeness).
19. **Norway/Iceland EU-US accession (June 2011)** and **Croatia EU-US accession protocol** – dates
    from general knowledge only (`confidence=low`); verify in OJ L 283/2011 and the 2013 protocol.
20. **Vietnam (2008)** is a cargo-only liberalisation, **not** open skies — excluded. Other large
    markets never open skies with the US in the window: China, Russia, South Africa, Saudi Arabia,
    Egypt, Philippines, Hong Kong (liberal but not open skies).
21. The EU-US ATA's formal entry into force (after all member-state ratifications) and the 2010
    Protocol's EIF are not given; the panel should use provisional application dates
    (2008-03-30 and 2010-06-24).
22. ISO3: Netherlands Antilles uses the retired code `ANT`; MALIAT row uses `MULTI`.
