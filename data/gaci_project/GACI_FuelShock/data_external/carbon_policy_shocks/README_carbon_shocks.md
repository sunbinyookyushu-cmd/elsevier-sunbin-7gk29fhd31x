# Carbon policy surprises and shocks (Kaenzig; Bauer, Kaenzig and Rudebusch)

Downloaded 2026-10-02. All data files are unmodified copies of the originals.
Only the two repository README.md files were renamed (both are called README.md upstream), content unchanged.

## 1. Citations (verified)

**Main paper (AER, forthcoming)**
Kaenzig, Diego R. "The Unequal Economic Consequences of Carbon Pricing." *American Economic Review*, forthcoming. DOI: 10.1257/aer.20230448.
- Source for the DOI: AEA forthcoming list and article page (https://www.aeaweb.org/articles?id=10.1257/aer.20230448), status "Forthcoming", no volume, issue or pages yet.
- Check on 2026-10-02: this DOI is NOT yet registered. Crossref (api.crossref.org/works/10.1257/aer.20230448) and doi.org both return 404. Cite it as "forthcoming" and re-check before submission.
- The GitHub README (repo pushed 2026-05-05) still says "Conditionally accepted at American Economic Review" and uses the shorter title "The Unequal Consequences of Carbon Pricing". Kaenzig's website says "Forthcoming at American Economic Review". The AEA page uses the full title above.

**Working paper (Crossref verified, refcheck match)**
Kaenzig, Diego R. 2023. "The Unequal Economic Consequences of Carbon Pricing." NBER Working Paper 31221, issued May 2023, revised September 2025. DOI: 10.3386/w31221.
Also on SSRN: DOI 10.2139/ssrn.4440716 (Crossref).

**Updated surprise series 2005 to 2024 (Crossref verified, refcheck "verified")**
Bauer, Michael D., Diego R. Kaenzig, and Glenn D. Rudebusch. 2026. "Carbon Pricing and Inflation Expectations." *The Econometrics Journal*, published online 4 August 2026. DOI: 10.1093/ectj/utag023. (Volume, issue and pages not yet in Crossref.)
Earlier version: CEPR Discussion Paper 21355 (from the repo README; not checked in Crossref). The repo README still says "Conditionally accepted at The Econometrics Journal".

## 2. Files in this folder

| File | Source URL | GitHub commit (date) | Content |
|---|---|---|---|
| `carbonPolicyShocks.xlsx` | https://raw.githubusercontent.com/dkaenzig/carbonpolicyshocks/main/carbonPolicyShocks.xlsx | d8b2fe5 (2025-06-02, "Updated shocks") | AER version. Sheets `Daily`, `Monthly`, `Info` |
| `legacy/carbonPolicyShocks_legacy.xlsx` | https://raw.githubusercontent.com/dkaenzig/carbonpolicyshocks/main/legacy/carbonPolicyShocks_legacy.xlsx | 18e3e3d (2025-06-02) | Earlier (April 2023) version. Sheets `Baseline`, `Pct`, `Info` |
| `dataCPS.xlsx` | https://raw.githubusercontent.com/dkaenzig/carbonpolicyshocks/main/dataCPS.xlsx | a245da5 (2026-03-07) | Monthly data for the baseline VAR, 1999M01 to 2019M12 |
| `carbon-policy-surprises.xlsx` | https://raw.githubusercontent.com/dkaenzig/carbon-policy-surprises-update/main/carbon-policy-surprises.xlsx | 3d7c44a (2026-05-05) | Bauer, Kaenzig, Rudebusch (BKR) updated daily series 2005 to 2024. Sheets `Data`, `Info` |
| `Kaenzig 2025 - The unequal economic consequences of carbon pricing.pdf` | https://github.com/dkaenzig/carbonpolicyshocks (repo file) | | Paper, version dated June 2025, 120 pages incl. appendix (Table A.1 event list) |
| `bkr_carbon_pricing.pdf` | https://dkaenzig.github.io/diegokaenzig.com/Papers/bkr_carbon_pricing.pdf | | BKR paper, version dated March 30, 2026 (Appendix Table A.1 lists the 2020 to 2024 events) |
| `README_carbonpolicyshocks_repo.md` | https://raw.githubusercontent.com/dkaenzig/carbonpolicyshocks/main/README.md | | Original README.md of repo 1 (renamed) |
| `README_carbon-policy-surprises-update_repo.md` | https://raw.githubusercontent.com/dkaenzig/carbon-policy-surprises-update/main/README.md | | Original README.md of repo 2 (renamed) |

Repositories: https://github.com/dkaenzig/carbonpolicyshocks and https://github.com/dkaenzig/carbon-policy-surprises-update (both linked from Kaenzig's research page and, for the first, from the NBER page). License: CC BY 4.0 (both READMEs).

Not obtained: an AEA/openICPSR replication package (openICPSR search returned HTTP 403; the AER article page lists no replication link) and the NBER data appendix (data.nber.org/data-appendix/w31221 returned HTTP 403). Whether these contain anything beyond the GitHub files is unknown.

### Rows and coverage (checked in Python)

**`carbonPolicyShocks.xlsx`** (AER version)
- `Daily`: 114 rows, columns `Date`, `Surprise`. One row per retained event day, 2005-06-20 to 2019-11-08. No zeros, no missing values.
- `Monthly`: 246 rows, columns `Date` (string like `1999M07`), `Surprise`, `Shock`. Covers 1999M07 to 2019M12. `Surprise` is 0 before 2005 and in months without events (78 non-zero months, first 2005M06, last 2019M11). `Monthly Surprise` equals the sum of `Daily Surprise` within the month (max difference 0.0). `Shock` is non-missing in every month.
- Events per year in `Daily`: 2005: 3, 2006: 5, 2007: 10, 2008: 1, 2009: 3, 2010: 7, 2011: 11, 2012: 10, 2013: 15, 2014: 14, 2015: 4, 2016: 5, 2017: 9, 2018: 7, 2019: 10.

**`legacy/carbonPolicyShocks_legacy.xlsx`** (April 2023 version)
- `Baseline` and `Pct`: 252 rows each, 1999M01 to 2019M12, columns `Date`, `Surprise`, `Shock`. Missing for 1999M01 to 1999M06. First non-zero surprise 2005M05 (this version still includes the 2005-05-25 event that the AER version excludes).
- Correlation with the AER version (monthly): Surprise 0.68, Shock 0.80.

**`dataCPS.xlsx`**: 252 rows, 1999M01 to 2019M12, columns `EKESCPENF_SA`, `GHGTotal_IP`, `EKCPHARMF_SA`, `EKIPTOTG`, `EMECB2Y`, `EKESUNEMO`, `DJSTO50`, `DCOILBRENTEU`. The README says the file holds HICP energy, GHG emissions, HICP headline, industrial production, two-year rate, unemployment rate, EUROSTOXX50 and Brent. The column-to-variable mapping is not documented; it appears to follow that order (my reading of the codes, not stated).

**`carbon-policy-surprises.xlsx`** (BKR update)
- `Data`: 5,217 daily rows (trading days), 2005-01-03 to 2024-12-31. Columns `date`, `ets_price`, `elec_price`, `event_day`, `event_desc`, `cp_surprise_base`, `cp_surprise_pct`.
- 171 event days (`event_day` = 1), 2005-05-25 to 2024-07-31. Surprises are 0 on all non-event days, never missing.
- `ets_price` is missing for 2005-01-03 to 2005-04-21 (79 rows); `elec_price` is never missing.
- Events per year: 2005: 4, 2006: 5, 2007: 10, 2008: 1, 2009: 3, 2010: 7, 2011: 13, 2012: 11, 2013: 15, 2014: 16, 2015: 4, 2016: 7, 2017: 9, 2018: 8, 2019: 14, 2020: 12, 2021: 10, 2022: 6, 2023: 13, 2024: 3. No events after 2024-07-31.
- Six event days have a surprise of exactly 0 (settlement price unchanged): 2006-12-14, 2007-03-26, 2007-04-30, 2007-05-04, 2012-06-05, 2012-07-13.

## 3. What the series measure

### Kaenzig (AER version), `carbonPolicyShocks.xlsx`

Definition (paper, Section 2.2, Eq. 1): "I construct the carbon policy surprise series as the change in the EUA futures price on the day of a regulatory event relative to the last trading day before the event. Because carbon prices were near zero at the end of the first phase, I express the EUA price change in euros, normalized by the prevailing wholesale electricity price on the day prior to the event":
CPSurprise_d = (F_d - F_{d-1}) / P^elec_{d-1}.

- Not a principal component. It is a single price change on each event day (daily window, settlement prices).
- Contract: "price data for the December contract from the ICE"; "I focus on the front contract (the nearest expiry)".
- Electricity price: appendix footnote 5: "To mitigate the influence of extreme observations in the wholesale electricity price, I use an average of the price over the last 5 trading days before the event."
- Refined series: the file's daily `Surprise` is described in the Info sheet as "purged from macro, financial and oil market news". The paper's baseline is "the residual from the predictive regression (2), controlling for the full information set", which also includes heating degree days (climatic); it "closely tracks the raw series, with a correlation coefficient of 0.90". The Info sheet wording omits the climatic variables; I take the file to be the paper's baseline refined series, but the exact predictor set behind the file is not stated in the file.
- Units: not stated in the file or README. Magnitudes (max 0.97, min -1.19) match BKR's series, which is in percent, and the paper speaks of "events implying a change in electricity prices of nearly 1.5 percent". So the values appear to be in percent of the electricity price (inferred, not stated).
- Events: "I identify 126 regulatory events between 2005 and 2019" (supply of allowances: cap, free allocation, auctioning, international credits). 12 were dropped after a Factiva narrative check for confounding news (oil market, sovereign debt crisis, Brexit), "leaving 114 events". I parsed Appendix Table A.1: 126 events, 12 flagged, and the 114 kept dates match the `Daily` sheet exactly. Excluded dates: 2005-05-25, 2011-11-14, 2011-11-25, 2012-05-23, 2014-03-28, 2014-11-04, 2016-01-15, 2016-06-23, 2018-12-05, 2019-02-15, 2019-04-23, 2019-06-12.
- `Monthly Surprise`: "aggregated by summing over daily surprises"; months without events are zero; before 2005 "I censor missing values in the surprise series to zero, following the approach in Noh (2019)".
- `Monthly Shock`: "Carbon policy shock, identified using the external instruments VAR using the surprise series as an instrument for the energy price residual." Computed as CPShock_t = s1' Sigma^{-1} u_t from an 8-variable monthly VAR (HICP energy, GHG emissions, HICP, industrial production, unemployment, two-year rate, stock index, real Brent), 6 lags, in levels, 1999M01 to 2019M12, constant plus a dummy for 2011M07 to 2012M03. The impact vector is scaled so that the shock has a unit positive effect on HICP energy (s_{1,1} = 1). Units/scale of the `Shock` series itself are not documented (sd in the file is 0.67). Monthly correlation of Surprise and Shock in the file: 0.21 (0.24 for 2005M01 onward).
- Instrument strength in the paper's VAR: robust F = 16.85 for the baseline refined surprise.

### BKR update, `carbon-policy-surprises.xlsx`

Definition (BKR, Eq. 1): cps_t = 100 * (f_t - f_{t-1}) / p^elec_{t-1}, where f is "the settlement (end-of-day) price of the front-quarter EUA futures contract", and "We multiply the scaled surprise by 100 to measure cps_t in percent". Footnote 3: "the electricity price is divided by 0.38 tCO2/mwh" to put it in the same units as the carbon price.

- `cp_surprise_base`: README: "Carbon policy surprise, measured as the EUR change relative to wholesale electricity price". Units: percent. I reproduced it exactly (correlation 1.0000, max abs difference below 0.0001) as 100 * (ets_price_d - ets_price_{d-1}) / elec_price_{d-1} using the file's own columns. So (a) it uses the previous trading day's electricity price, not a 5-day average, and (b) the `elec_price` column already appears to be in EUR per tCO2-equivalent, i.e. EUR/MWh divided by 0.38 (inferred from the exact reproduction plus footnote 3; not stated in the file).
- `cp_surprise_pct`: README: "measured as the log change in ETS price". Reproduced exactly as 100 * (ln ets_price_d - ln ets_price_{d-1}). Note: BKR Appendix Figure B.3 describes the alternative as a simple percent change; the file uses log change.
- `ets_price`: "EU ETS price, measured based on the front futures contract" (EUR/tCO2). `elec_price`: "EU wholesale electricity price, measured as a weighted average over major European markets". Data vendor not stated.
- Not purged and not screened: the base series is the raw price change (exact reproduction from prices), and the file keeps all 12 events that Kaenzig excluded as confounded. There is no confounding flag in the file. BKR's own robustness check drops ECB announcement days and 2019-04-23 (Figure B.6), but those dates are not marked in the file.
- Events: "For the period from 2008 to 2019, we use the events described in Känzig (2023) (see Table A.1 therein). We supplement these dates with a new set of 45 EU ETS regulatory events from January 2020 to December 2024 ... This yields a total of 152 regulatory events from 2008 to 2024." Baseline sample in BKR: 2013 to 2024, 117 events. The file also contains the 19 Phase I events of 2005 to 2007. My counts from the file match: 152 events 2008 to 2024 and 117 events 2013 to 2024.
- Comparison with Kaenzig: on Kaenzig's 114 event days, correlation of BKR `cp_surprise_base` with Kaenzig's refined daily `Surprise` is 0.897. Monthly sums, 2005 to 2019: correlation 0.67.

### Sign convention (both series)

Positive value = the EUA futures price rose on the event day relative to the previous trading day (by construction of Eq. 1). The paper describes a shock that raises energy prices as "restrictive" / "tightening the carbon pricing regime", and the VAR shock is normalized to raise HICP energy. So positive = tighter carbon policy / higher carbon price; negative = looser.

## 4. Aggregation

- Daily to monthly (as the author does): sum the daily surprises within each calendar month; months with no event are 0. If you need 2005 to 2024 from the BKR file: group `cp_surprise_base` by year-month and sum. This gives 240 months (2005-01 to 2024-12), of which 113 contain at least one event and 43 contain more than one.
- Monthly to annual or quarterly: the paper states this only for the VAR shock: "I aggregate the shock CPShock_t by summing over the respective months before running the local projections." For the surprise series, summing is the natural analogue, but the paper does not state an annual aggregation of the surprise.
- Annual sums of BKR `cp_surprise_base` (percent): 2005 1.78, 2006 -0.87, 2007 -0.31, 2008 -0.17, 2009 -0.71, 2010 0.53, 2011 -1.12, 2012 -1.64, 2013 -0.73, 2014 -1.41, 2015 0.20, 2016 -1.02, 2017 -0.51, 2018 -1.32, 2019 2.23, 2020 3.58, 2021 2.65, 2022 -0.50, 2023 -0.30, 2024 -0.26.
- BKR use the series at the event (daily) level in event-study regressions; I did not find a monthly aggregation in BKR.

## 5. Caveats

1. No single published series covers 2005 to 2024 with Kaenzig's AER construction. The AER series (refined, 12 confounded events dropped, 5-day average electricity price, December ICE contract) stops at 2019-11-08 (daily) and 2019M12 (monthly). The 2020 to 2024 extension exists only as the BKR raw series (not purged, confounded events kept, previous-day electricity price, front-quarter contract). Splicing the two creates a construction break at 2020. Using the BKR series for the whole 2005 to 2024 period is internally consistent but is not the AER baseline.
2. The VAR-based monthly `Shock` exists only for 1999M07 to 2019M12. No VAR shock for 2020 to 2024 is published in these repositories.
3. Event list mismatches in the BKR file: BKR Appendix Table A.1 lists 2020-05-18 ("Revised 2020 UK aviation auction calendar"), but the file has `event_day` = 0 and surprise 0 on that date. The file flags 2019-12-12 ("The start of auctioning for the Innovation Fund slightly postponed ...") as an event, which is in neither Kaenzig's Table A.1 nor BKR's Table A.1. The totals (45 new, 152 for 2008 to 2024) still match because of this swap. Reason unknown.
4. Normalization by electricity prices: during the 2021 to 2023 energy crisis `elec_price` was very high (for example about 732 on the 2021-12-15 event day, 1,054 on 2022-07-28, 928 on 2022-12-09, against roughly 55 to 240 on event days from 2005 to 2020), so a given EUR move in the carbon price produces a smaller surprise in those years. BKR note the series is heteroskedastic with larger surprises after 2019.
5. Phase I prices collapsed toward zero in 2007 (front futures 0.10 EUR on 2007-11-07), so `cp_surprise_pct` takes extreme values there (for example +35.7 on 2007-11-07, -43.5 on 2013-04-16). Kaenzig drops the late-2007 events when using the percentage version.
6. Market Stability Reserve: operational January 2019 (paper, p. 8). From 2017 on, several events are MSR or auction-volume announcements and periodic data updates (surplus indicator, international credit use, New Entrants' Reserve status). Kaenzig shows robustness to excluding "data updates which affect the supply of allowances indirectly, e.g. by triggering the market stability reserve". The file has no event-type column; types are only in the two Table A.1s.
7. Aviation-specific events (relevant for an airport panel; my observation, not from the papers): 11 event descriptions mention aviation, airlines or aircraft (2011-09-26, 2012-11-16, 2013-02-28, 2013-03-25, 2013-09-26, 2014-06-04, 2020-09-09, 2022-12-09, 2023-01-18, 2023-10-31, 2023-11-16). These could affect aviation through channels other than the EUA price, so a robustness check that drops them may be worth running.
8. The surprise is a single EU-wide time series; most months are zero (127 of 240 months in the BKR file). Kaenzig treats it as a noisy proxy and uses it as an instrument for a VAR residual, not as the shock itself.
9. Unknowns: exact predictor set used for the file's refined daily series (Info sheet says macro, financial and oil; paper baseline also includes heating degree days); units of the monthly `Shock`; the data vendor for the BKR electricity price; whether an AEA replication package with additional files exists.
