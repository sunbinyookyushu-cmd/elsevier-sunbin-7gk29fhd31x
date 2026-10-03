# Data sources: EU ETS aviation, carbon prices, aviation taxes

Checked on 2026-10-02. "Read" means I opened the page or file in this session. "Not verified" means I could not open it (blocked or JavaScript-only) and nothing about it below should be cited without checking.

Legal timeline: see `eu_ets_aviation_timeline.csv` (21 dated events with acts, quotes and URLs).

---

## 1. EU allowance (EUA) price

### 1a. Downloaded: SendeCO2 daily EUA price, 2008-2025 (free CSV)

| Item | Detail |
|---|---|
| Files in this folder | `EUA_daily_sendeco2_2008_2025.csv` (date, eua_eur, cer_eur; 4,590 trading days, 2008-01-02 to 2025-12-31); `EUA_monthly_sendeco2_2008_2025.csv` (month, mean/min/max/last, n_days; 216 months); raw per-year files in `raw_sendeco2/`; builder script `build_eua_price_files.py` |
| Source page | https://www.sendeco2.com/es/precios-co2 |
| Per-year CSV | `https://www.sendeco2.com/site_sendeco/service/download-csv.php?year=YYYY` (2008 to 2026 available) |
| Format | Semicolon-separated, `Fecha;EUA;CER;SPREAD`, date dd-mm-yyyy, EUR per tonne |
| Access | Free, no login. The site's legal note (https://www.sendeco2.com/es/nota-legal, section 2.1 VII) forbids reproducing or exploiting the content for commercial purposes. Academic use with citation should be fine, but do not post the raw files in a public replication package without checking. |
| Caveat | The page does not say which contract the daily "EUA" price is (spot or December futures, which exchange). |
| Validation (my computation) | On days with an EEX primary auction (2012-2025, EUA contracts only), SendeCO2 vs EEX clearing price: 2,563 matched days, correlation 0.9996, median absolute difference EUR 0.25, 95th percentile EUR 1.83. |
| Gap | No 2005-2007 (Phase 1) prices. For a 1996-2024 hub panel this matters only as a placebo; aviation obligations start in 2012. |

Annual mean of the daily SendeCO2 EUA price (EUR/t, computed from the file): 2008 21.95, 2009 13.05, 2010 14.32, 2011 12.87, 2012 7.32, 2013 4.46, 2014 5.96, 2015 7.67, 2016 5.36, 2017 5.83, 2018 15.89, 2019 24.80, 2020 24.69, 2021 53.18, 2022 80.90, 2023 83.58, 2024 65.21, 2025 73.90.

### 1b. Downloaded: EEX primary-market auction results, 2012-2025 (includes aviation allowances, EUAA)

| Item | Detail |
|---|---|
| Files in this folder | `EEX_emission_spot_primary_auction_report_2012_2025.zip` (784 KB, one xls/xlsx per year, as published); `EEX_auction_prices_2012_2025.csv` (2,841 auctions: date, auction name, contract code, volume, status, clearing price, `is_euaa` flag) |
| Source page | https://www.eex.com/en/markets/environmentals/eu-ets1-eu-ets2-auctions/eu-ets1-auctions |
| Direct file | https://www.eex.com/fileadmin/EEX/Downloads/Markets/Environmentals/EUA_Emission_Spot_Primary_Market_Auction_Report/Archive_Reports/emission-spot-primary-market-auction-report-2012-2025-data.zip |
| Contracts | T2PA (EUA phase 2), T3PA (EUA phase 3 and later), EAA2/EAA3 (aviation allowances, EUAA). 82 EUAA auctions found, 2012 to 2024. |
| Use | Primary-market clearing prices only (auction days, not every trading day). Good for an official, citable price and for EUAA prices. |

### 1c. Other free price sources (not downloaded)

- **ICAP Allowance Price Explorer**, https://icapcarbonaction.com/en/ets-prices. Terms page (read): https://icapcarbonaction.com/en/terms-use-and-documentation-notes-allowance-price-explorer. For the EU ETS: "EUA spot price up to 2018 provided by the EEX Group . From 2019, end-of-day and weekly average data is provided by Intercontinental Exchange . EEX data is not available for download. End-of-day ICE Data is only visible in the tool's graph-format. Weekly average ICE Data is available for download and with a 6-month lag". Reuse needs ICAP's prior written permission.
- **World Bank Carbon Pricing Dashboard**, https://carbonpricingdashboard.worldbank.org/ . Annual price per instrument (EU ETS included). Data file used by a third-party mirror: https://carbonpricingdashboard.worldbank.org/sites/default/files/data-latest.xlsx . The site returned HTTP 403 to automated requests in this session, so download it by hand in a browser. Licence CC BY 4.0 (World Bank data catalog, https://datacatalog.worldbank.org/search/dataset/0042051/carbon-pricing-dashboard). A DataHub mirror (https://datahub.io/climate-and-environment/carbon-pricing) describes annual prices 1990-2024, "Data as of April 1, 2024". I did not check the price-date convention in the World Bank file itself.
- **OECD Net Effective Carbon Rates** also reports the ETS permit price by country and sector for 2018, 2021 and 2023 (see section 3b).
- **Ember** (https://ember-energy.org/data/european-electricity-prices-and-costs/) uses the EU ETS front-December contract from Montel for its carbon cost series. I did not confirm that the carbon price itself can be downloaded.
- Paid or institutional: ICE/EEX end-of-day data, Refinitiv Datastream, Bloomberg (use these if a referee asks for the exact front-December futures series from 2005).

---

## 2. Verified emissions by aircraft operator (Union Registry, formerly EUTL)

### 2a. Commission "Verified emissions" and "Compliance data" files (operator level)

| Item | Detail |
|---|---|
| Page | https://climate.ec.europa.eu/eu-action/carbon-markets/eu-emissions-trading-system-eu-ets/union-registry_en (redirects to `/areas-action/...`) |
| Files | One xlsx (xls before 2015) per reporting year. Latest: "Verified Emissions for 2025" (posted 09/04/2026). For 2024: https://climate.ec.europa.eu/document/download/385daec1-0970-44ab-917d-f500658e72aa_en?filename=verified_emissions_2024_en.xlsx (6.9 MB). Compliance files: e.g. https://climate.ec.europa.eu/document/download/b80300cf-7608-405d-969e-8b016687640e_en?filename=compliance_2024_code_en.xlsx. Older years and the 2008-2012 file are linked on the same page. |
| Coverage | Each verified-emissions file carries history back to 2008: `VERIFIED_EMISSIONS_2008` to `_2024`, `ALLOCATION_*`, and from 2020 `CH_ALLOCATION_*` / `CH_VERIFIED_EMISSIONS_*` (Swiss ETS part). A separate sheet covers operators administered by Switzerland (with CRCO number). |
| Aviation rows | `MAIN_ACTIVITY_TYPE_CODE == 10`. The 2024 file has 1,499 aircraft-operator rows (largest administering states: GB 323, FR 277, DE 205, IT 109, IE 100). |
| Operator identifiers | `REGISTRY_CODE` = administering Member State. For aircraft operators the column headed `IDENTIFIER_IN_REG` holds the operator name and the column headed `INSTALLATION_NAME` holds the Eurocontrol CRCO identification number (I checked: Lufthansa 1776, KLM 1640, Qatar Airways 21912, Turkish Airlines 2758, Etihad 29929, Pegasus 10690 match the CRCO numbers in the official operator list). `INSTALLATION_IDENTIFIER` is the registry account id. Codes: -1 = blank, "Excluded" = out of scope that year. |
| Airport or route | **Not included.** Only operator, administering state, allocation and verified emissions. Emissions cover only the flights in scope each year (from 2013: intra-EEA, then also departures to CH and UK). Non-EU carriers appear for their in-scope flights only (Emirates, Qatar, Turkish are administered by Germany). |
| Official operator list (CRCO number, operator name, state of the operator, grouped by administering state) | Commission Regulation (EU) 2026/784 of 26 March 2026 amending Regulation (EC) No 748/2009: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202600784 |
| Notes in the file (read) | "2013 data are not directly comparable to 2012 data given the extended scope of the EU ETS in phase III"; GB-administered accounts still marked OPEN are former UK accounts "excluded from the EU ETS since Brexit". |

### 2b. EEA EU ETS data viewer (aggregated)

- Viewer: https://www.eea.europa.eu/en/analysis/maps-and-charts/emissions-trading-viewer-1-dashboards
- Full dataset: https://www.eea.europa.eu/en/datahub/datahubitem-view/98f04097-26de-4fca-86c4-63834818c0c0
- Aggregated by country (administering state), activity type and year: verified emissions, allocated allowances, surrendered units. Aviation is activity type 10. Quote: "The ETS1 information 1. Total allocated allowances , 1.2 Correction to freely allocated allowances (not reflected in EUTL) , 1.3 Allowances auctioned or sold are only available at national level. The data can be split between aviation (activity type 10) and stationary installations".
- No operator, airport or route detail.

**Implication for the design:** EUTL data cannot measure airport exposure. Airport-level treatment intensity has to be built from schedules (seats or flights on in-scope routes, e.g. from OAG/Cirium or your GACI route data) times the EUA price and the in-scope share defined by the timeline file.

---

## 3. Aviation taxes, fuel taxes and charges

### 3a. ICAO

- I could not open icao.int taxation pages in this session (HTTP 403 for automated downloads, 404 for the old page paths). So the edition, year and content of **ICAO Doc 8632** (ICAO's policies on taxation in international air transport) and the existence of any ICAO country-by-country tax database are **not verified** here. Check the current ICAO taxation pages manually.
- What I did read from ICAO: Assembly Resolution A42-22 on CORSIA (phases, baselines, volunteering States by year), used in the timeline (E08, E16).

### 3b. OECD (read through the OECD SDMX API, which is open; oecd.org web pages were blocked)

- **Net Effective Carbon Rates (NECR)**, dataflow `OECD.CTP.TPS,DSD_NECR@DF_NECRS` version 1.1. 86 reference areas, including all 27 EU members, Turkey (TUR), the UK, Norway, Iceland and Switzerland; no UAE or Qatar. Years available: 2018, 2021, 2023. Sectors: ROAD, OFFROAD, INDUSTRY, AGRIFISH, RESCOM, ELEC and totals. **There is no separate aviation sector**; jet kerosene appears as emissions source `KERO`, and aviation sits inside `OFFROAD` (off-road transport). Measures include `FUETAX` (fuel excise), `CARBTAX`, `MPERPRI` (ETS permit price), `AVPERPRI` (permit price adjusted for free allocation), `NETECR`, `SUBSID`, `TAXBCO` (tax base, kt CO2). Units EUR or national currency per tCO2; price base V (current) or Q (constant).
  - Example query (CSV): `https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_NECR@DF_NECRS,1.1/DEU+NLD+TUR.OFFROAD.KERO........?format=csv`
  - Values read for OFFROAD x KERO, EUR/tCO2, current prices: DEU fuel excise 0 in 2018, 2021, 2023; DEU ETS permit price 5.95 (2018), 51.93 (2021), 81.09 (2023); NLD the same pattern (0.47, 51.93, 81.09); TUR fuel excise 0 and permit price 0 in all three years.
  - Not verified: how NECR treats international aviation bunker fuel (methodology pages blocked). Check before using it for international flights.
- **Net Effective Energy Rates (NEER)**, dataflow `OECD.CTP.TPS,DSD_NEER@DF_NEERS` (same structure, per GJ). Not queried.
- **Taxing Energy Use** (older OECD vintages) and **Effective Carbon Rates** web pages: blocked; not verified whether pre-2018 vintages are in the SDMX API.
- **OECD PINE** (policy instruments for the environment; may list national air passenger taxes): https://pinedatabase.oecd.org/ redirects to a Shiny app (https://oecd-main.shinyapps.io/pinedatabase/); contents not inspected.

### 3c. EU sources

- **Energy Taxation Directive 2003/96/EC**, Article 14 (read, https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32003L0096). Commercial jet fuel is exempt by EU law: "Member States shall exempt the following from taxation ... (b) energy products supplied for use as fuel for the purpose of air navigation other than in private pleasure-flying." Article 14(2): "Member States may limit the scope of the exemptions provided for in paragraph 1(b) and (c) to international and intra-Community transport." So any jet fuel excise in the EU is at most domestic, and ticket taxes are the main national instrument.
- **Taxes in Europe Database (TEDB)**, https://ec.europa.eu/taxation_customs/tedb/ (JavaScript app; not inspected). It may record national air passenger taxes; check by hand.
- **Commission ETS review package of 17 July 2026**: proposal COM(2026) 616 (read; see timeline E20, it explicitly cites "hub leakage"); impact assessment SWD(2026) 616, https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A52026SC0616 ; support study on ETS aviation, https://op.europa.eu/en/publication-detail/-/publication/632c2f70-ae51-11f1-b9e5-01aa75ed71a1/language-en . The impact assessment and study were not read; they likely contain the Commission's own hub-leakage analysis and are worth reading for the paper's motivation.

### 3d. National ticket taxes

I found no single verified, harmonised database of national air passenger tax rates by year in this session. Rates and dates for the Netherlands (2008-09, 2021-), Germany (2011-), Austria (2011-), Sweden (2018-), Norway, France, Italy and UK APD should be coded from national legislation or official tax authority pages, and cross-checked against the policy descriptions in the papers listed in `literature_aviation_tax_ets.md`. Note that the Dutch, German and Swedish taxes exempt transfer passengers (reported in the KiM report, Helmers and van der Werf 2025, and Bernardo et al. 2024), which matters for any hub-centrality outcome.

---

## 4. Distances relevant to the 2026 proposal (my computation)

The proposal would cover departing flights to non-EEA aerodromes within 5,000 km of Frankfurt from 2029. Great-circle distances from FRA (OurAirports coordinates, https://davidmegginson.github.io/ourairports-data/airports.csv): IST 1,837 km, SAW 1,901 km, CAI 2,922 km, DOH 4,588 km, DXB 4,845 km, DWC 4,859 km, AUH 4,862 km, MCT 5,179 km. All main competitor hubs (Istanbul, Doha, Dubai, Abu Dhabi) fall inside the proposed 5,000 km band.
