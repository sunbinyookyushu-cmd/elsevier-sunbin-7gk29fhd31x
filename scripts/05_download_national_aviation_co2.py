"""National aviation CO2 series for descriptive validation (NOT the main outcome; see docs/data_collection.md).

Sources (all currently BLOCKED by the session network policy; run locally):
  * EDGAR v8/v2024 GHG: sector 1.A.3.a (domestic aviation) + international aviation bunkers, by country-year 1970-2023.
    https://edgar.jrc.ec.europa.eu/dataset_ghg2024  (download the IPCC-2006 sector xlsx)
  * Our World in Data: 'Per capita CO2 emissions from aviation' and country aviation totals (from Lee et al. / ICCT / Graver).
    https://ourworldindata.org/grapher/co2-emissions-aviation.csv
  * UNFCCC CRF tables (Annex I): 1.A.3.a and international bunkers memo items, 1990-2022.
  * UK DfT / EEA: national aviation emissions used for UK APD evaluations.
This script just records URLs and target paths; add urllib downloads once hosts are allowed.
"""
URLS = {
 "owid_aviation_co2": "https://ourworldindata.org/grapher/co2-emissions-aviation.csv",
 "edgar_ghg_2024_landing": "https://edgar.jrc.ec.europa.eu/dataset_ghg2024",
}
if __name__ == "__main__":
    for k,v in URLS.items(): print(k, v)
