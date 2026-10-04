"""v4 panel (rev. 2026-10-04: CEDS v_2025_03_18 to 2023; sample rule without renewables): ALL denominators from one source so that log identities hold exactly.
  GDP  = WDI GDP per capita (constant 2015 US$) x WDI population   -> lngdp = lnpc + lnpop by construction
  CO2  = OWID (Global Carbon Project) Mt ; energy = OWID/EI primary energy TWh ; coal/oil/gas consumption TWh (EI, 77 countries)
  SO2, NOx = CEDS 2022 (OWID mirror) t ; SO2 by fuel (CEDS) ; CO2 by fuel (OWID)
  GACI, instruments, region codes = gaci_panel_combined
Identities (exact in logs): ln SO2/GDP = ln SO2pc - lnpc ; ln SO2/GDP = ln E/GDP + ln CO2/E + ln SO2/CO2 ; Kaya: ln CO2 = lnpop + lnpc + ln E/GDP + ln CO2/E
Output: panel_v4.csv (+ stata/panel_v4.dta)"""
import pandas as pd, numpy as np, pathlib, pyreadstat
here=pathlib.Path(__file__).resolve().parent
g=pd.read_csv(here.parent/"gaci_panel_combined.csv")[["c","y","reg","ln_gaci_cwm","gaci_cwmean","gaci_mean","tourism_int","feyrer_int","ln_sea_ma","trade_share","merch_share"]]
w=pd.read_csv(here/"wdi_country_year.csv")
o=pd.read_csv(here.parent/"GACI_CO2/data_external/owid-co2-data.csv",low_memory=False).rename(columns={"iso_code":"c","year":"y"})
iso=o.dropna(subset=["c"]).drop_duplicates("country").set_index("country").c
o=o[["c","y","co2","coal_co2","oil_co2","gas_co2","cement_co2"]]
e=pd.read_csv(here/"data_external/owid-energy-data.csv",low_memory=False).rename(columns={"iso_code":"c","year":"y"})[["c","y","primary_energy_consumption","coal_consumption","oil_consumption","gas_consumption","renewables_share_energy","low_carbon_share_energy","renewables_share_elec"]]
ce22=pd.read_csv(here/"data_external/ceds_2022_emissions_by_fuel_owid.csv"); ce22["c"]=ce22.Entity.map(iso); ce22=ce22.dropna(subset=["c"]).rename(columns={"Year":"y"})
ce22["so2_total_v22"]=ce22[[x for x in ce22.columns if x.endswith("_so2")]].sum(axis=1); ce22["nox_total_v22"]=ce22[[x for x in ce22.columns if x.endswith("_nox")]].sum(axis=1); ce22=ce22[["c","y","so2_total_v22","nox_total_v22"]]
ce=pd.read_csv(here/"ceds2025_country_year.csv")   # CEDS v_2025_03_18 (user download), tonnes, 1990-2023: main SO2/NOx source
ce=ce[["c","y","so2_total","nox_total","coal_so2","oil_so2","natural_gas_so2","process_so2","biomass_so2","coal_nox","oil_nox"]].merge(ce22,on=["c","y"],how="outer")
p=pd.read_csv(here/"pwt_country_year.csv")[["c","y","rnna","emp","hc"]]
ls=pd.read_csv(here/"lsci_country_year.csv")[["c","y","ln_lsci"]]
ml=pd.read_json(here.parents[2]/"data/raw/airports/mledoze_countries.json"); geo=pd.DataFrame({"c":ml.cca3,"continent":ml.region,"subregion":ml.subregion,"landlocked":ml.landlocked.astype(int)})
d=g.merge(w,on=["c","y"],how="left").merge(o,on=["c","y"],how="left").merge(e,on=["c","y"],how="left").merge(ce,on=["c","y"],how="left").merge(p,on=["c","y"],how="left").merge(ls,on=["c","y"],how="left").merge(geo,on="c",how="left")
d=d[d.y.between(1996,2024)].copy()
L=lambda x: np.log(x.where(x>0))
d["air"]=d.ln_gaci_cwm; d["lnpc"]=L(d.gdppc_2015usd); d["lnpop"]=L(d.pop_wdi); d["lngdp"]=d.lnpc+d.lnpop; d["lnpc2"]=d.lnpc**2
d["ln_so2"]=L(d.so2_total); d["ln_nox"]=L(d.nox_total); d["ln_co2"]=L(d.co2); d["ln_energy"]=L(d.primary_energy_consumption)
d["ln_so2gdp_v22"]=L(d.so2_total_v22)-d.lngdp; d["ln_noxgdp_v22"]=L(d.nox_total_v22)-d.lngdp; d["ln_so2gdp"]=d.ln_so2-d.lngdp; d["ln_so2pc"]=d.ln_so2-d.lnpop; d["ln_noxgdp"]=d.ln_nox-d.lngdp; d["ln_noxpc"]=d.ln_nox-d.lnpop
d["ln_ci"]=d.ln_co2-d.lngdp; d["ln_co2pc"]=d.ln_co2-d.lnpop; d["ln_ei"]=d.ln_energy-d.lngdp; d["ln_ce"]=d.ln_co2-d.ln_energy
d["ln_so2co2"]=d.ln_so2-d.ln_co2; d["ln_so2energy"]=d.ln_so2-d.ln_energy; d["ln_noxco2"]=d.ln_nox-d.ln_co2
d["ln_coal_cons"]=L(d.coal_consumption); d["ln_oil_cons"]=L(d.oil_consumption); d["ln_coal_co2"]=L(d.coal_co2)
d["ln_so2_coal_cons"]=L(d.coal_so2)-d.ln_coal_cons; d["ln_so2_oil_cons"]=L(d.oil_so2)-d.ln_oil_cons
d["ln_so2_coal_ef"]=L(d.coal_so2)-L(d.coal_co2); d["ln_so2_oil_ef"]=L(d.oil_so2)-L(d.oil_co2); d["ln_so2_fossil_ef"]=L(d.coal_so2+d.oil_so2+d.natural_gas_so2)-L(d.coal_co2+d.oil_co2+d.gas_co2)
d["ln_so2_process"]=L(d.process_so2); d["so2_coal_sh"]=d.coal_so2/d.so2_total
d["lnkl"]=L(d.rnna/d.emp); d["lnkl2"]=d.lnkl**2
d["region"]=d.reg.str[:2]
base=d[d.y==1996].set_index("c").lnpc; d["inc96"]=d.c.map(base); d["inc_ter"]=pd.qcut(d.inc96,3,labels=["low","mid","high"]).astype(str)
d["merch96"]=d.c.map(d[d.y==1996].set_index("c").merch_share); d["serv96"]=d.c.map(d[d.y==1996].set_index("c").serv_sh)
d["goods_econ"]=(d.merch96>d.groupby("c").merch96.first().median()).astype(float); d["air_goods"]=d.air*d.goods_econ
CORE=["air","lnpop","lnpc","ln_so2gdp","ln_noxgdp","ln_ci","ln_ei","ln_ce","feyrer_int"]   # DECISION 2026-10-04: renew_sh removed from the rule (WDI ends 2021); CEDS v2025 extends SO2/NOx to 2023
d["in_unified"]=d[CORE].notna().all(axis=1).astype(int)
u=d[d.in_unified==1]; print("unified v4:", len(u), "obs", u.c.nunique(), "countries", u.y.min(), "-", u.y.max())
print("identity check: max |lngdp-lnpc-lnpop| =", float(np.nanmax(np.abs(d.lngdp-d.lnpc-d.lnpop))), "; max |ln_so2gdp-(ln_ei+ln_ce+ln_so2co2)| =", float(np.nanmax(np.abs(d.ln_so2gdp-(d.ln_ei+d.ln_ce+d.ln_so2co2)))))
d.to_csv(here/"panel_v4.csv",index=False)
out=d.copy()
for c in out.columns:
    if out[c].dtype==object: out[c]=out[c].fillna("")
pyreadstat.write_dta(out,str(here/"stata/panel_v4.dta"),version=14); print("written panel_v4.csv / stata/panel_v4.dta", d.shape)
