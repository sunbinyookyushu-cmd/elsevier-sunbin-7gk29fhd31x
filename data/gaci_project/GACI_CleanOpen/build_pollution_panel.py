"""Country-year local-pollution outcomes from OWID mirrors of CEDS (2022 release) and World Bank PM2.5 exposure.
CEDS: emissions by fuel for SO2, NOx, CO, OC, BC, NMVOC, NH3 (tonnes); summed over fuels/process -> national totals.
Entity names mapped to ISO3 with the OWID co2 file's country/iso_code pairs. Output: pollution_country_year.csv"""
import pandas as pd, numpy as np, pathlib, re
here = pathlib.Path(__file__).resolve().parent
c = pd.read_csv(here/"data_external/ceds_2022_emissions_by_fuel_owid.csv")
iso = pd.read_csv(here.parent/"GACI_CO2/data_external/owid-co2-data.csv", usecols=["country","iso_code"]).dropna().drop_duplicates()
iso = dict(zip(iso.country, iso.iso_code))
pols = sorted({re.sub(r"^(biomass|brown_coal|coal_coke|diesel_oil|hard_coal|heavy_oil|light_oil|natural_gas|process)_","",x) for x in c.columns if "_" in x})
for p in pols: c[f"{p}_total"] = c[[x for x in c.columns if x.endswith("_"+p) and not x.endswith("_total")]].sum(axis=1)
c["iso3"] = c.Entity.map(iso); c = c[c.iso3.notna() & (c.Year >= 1990)]
out = c[["iso3","Year"]+[f"{p}_total" for p in pols]].rename(columns={"Year":"year"})
pm = pd.read_csv(here/"data_external/pm25-exposure-world-bank.csv"); pm["iso3"]=pm.Entity.map(iso); pm = pm[pm.iso3.notna()].rename(columns={"Year":"year"})[["iso3","year","pm25_exposure"]]
out = out.merge(pm, on=["iso3","year"], how="outer")
out.to_csv(here/"pollution_country_year.csv", index=False)
print("pollutants:", pols); print(out.shape, "countries", out.iso3.nunique(), "years", out.year.min(), out.year.max())
print(out[out.iso3.isin(["KOR","DEU","CHN","IND"]) & out.year.isin([1996,2010,2019])][["iso3","year","so2_total","nox_total","pm25_exposure"]].round(0).to_string(index=False))
