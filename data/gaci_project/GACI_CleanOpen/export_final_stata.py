"""Final Stata dataset for replication: panel_v4 + the derived dummies used in the tables, with variable labels.
Output: replication/gaci_cleanopen_final.dta (Stata 14) and replication/gaci_cleanopen_final.csv"""
import pandas as pd, numpy as np, pathlib, pyreadstat
here=pathlib.Path(__file__).resolve().parent; R=here/"replication"; R.mkdir(exist_ok=True)
d=pd.read_csv(here/"panel_v4.csv")
d["trend"]=d.y-1996
keep={"c":"ISO3 country code","y":"year","in_unified":"=1: estimation sample (ln GACI, controls, SO2/NOx/CO2/energy intensities, instrument observed)",
"air":"ln GACI, seat-weighted country mean of airport GACI","gaci_cwmean":"GACI seat-weighted country mean (level)","gaci_mean":"GACI unweighted country mean (level; ME instrument)",
"feyrer_int":"Feyrer-type air market access (instrument)","tourism_int":"UNESCO natural+mixed heritage x world arrivals (weak instrument)","ln_sea_ma":"ln geographic sea market access","ln_lsci":"ln UNCTAD LSCI annual mean (2006-)",
"lnpc":"ln GDP per capita, constant 2015 US$ (WDI)","lnpc2":"lnpc squared","lnpop":"ln population (WDI)","lngdp":"ln GDP = lnpc + lnpop","lnkl":"ln capital/employment (PWT 11)","lnkl2":"lnkl squared",
"so2_total":"SO2 emissions, t (CEDS v_2025_03_18)","nox_total":"NOx emissions, t (CEDS v_2025_03_18)","so2_total_v22":"SO2 emissions, t (CEDS 2022 release via OWID; to 2019)","co2":"fossil CO2, Mt (OWID/GCP)","primary_energy_consumption":"primary energy, TWh (OWID/EI)",
"ln_so2gdp":"ln SO2/GDP","ln_so2pc":"ln SO2 per capita","ln_noxgdp":"ln NOx/GDP","ln_ci":"ln CO2/GDP","ln_co2pc":"ln CO2 per capita","ln_ei":"ln energy/GDP","ln_ce":"ln CO2/energy","ln_so2co2":"ln SO2/CO2","ln_noxco2":"ln NOx/CO2","ln_co2":"ln CO2","ln_so2gdp_v22":"ln SO2/GDP, CEDS 2022 release",
"renew_sh":"renewable share of final energy, % (WDI, to 2021)","renewables_share_elec":"renewables share of electricity, % (OWID/Ember-EI)",
"ln_coal_cons":"ln coal consumption TWh (EI)","ln_so2_coal_cons":"ln SO2 from coal / coal TWh","ln_so2_oil_cons":"ln SO2 from oil / oil TWh","ln_so2_coal_ef":"ln SO2 from coal / coal CO2","ln_so2_oil_ef":"ln SO2 from oil / oil CO2","ln_so2_fossil_ef":"ln SO2 fossil / fossil CO2","ln_so2_process":"ln process SO2 (smelting, refining)","so2_coal_sh":"coal share of SO2",
"manuf_sh":"manufacturing VA % GDP (WDI)","serv_sh":"services VA % GDP","agr_sh":"agriculture VA % GDP","trade_gdp_wdi":"trade % GDP (WDI)","fdi_in_gdp":"FDI inflows % GDP","urban_sh":"urban population %",
"region":"GACI macro-region (AF AS EU LA ME NA SW)","continent":"UN continent","subregion":"UN subregion","inc_ter":"1996 income tercile (low/mid/high)","goods_econ":"=1 merchandise trade/GDP 1996 above median","air_goods":"air x goods_econ","trend":"year - 1996","landlocked":"landlocked (0/1)"}
out=d[list(keep)].copy()
for c in out.columns:
    if out[c].dtype==object: out[c]=out[c].fillna("")
pyreadstat.write_dta(out,str(R/"gaci_cleanopen_final.dta"),version=14,column_labels=list(keep.values()))
out.to_csv(R/"gaci_cleanopen_final.csv",index=False); print("written", out.shape, "->", R)
