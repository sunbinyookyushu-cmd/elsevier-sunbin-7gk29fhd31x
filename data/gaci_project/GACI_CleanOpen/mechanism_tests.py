"""Mechanism tests for the air -> cleaner economy result (base spec: c + y FE, lnpop, lnpc, lnpc^2, clustered by country).
 1 technique: SO2 emission factors by fuel (CEDS SO2 by fuel / OWID CO2 by fuel), process SO2, coal scale
 2 absorptive capacity: air x human-capital tercile (PWT hc 1996)
 3 economy type: air x (services share / merchandise trade share / hc above median, 1996)
Output: _out_mechanism.txt"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib; warnings.filterwarnings("ignore")
here=pathlib.Path(__file__).resolve().parent
d=pd.read_csv(here/"clean_open_panel.csv").drop(columns=["coal_co2"],errors="ignore")
o=pd.read_csv(here.parent/"GACI_CO2/data_external/owid-co2-data.csv",low_memory=False).rename(columns={"iso_code":"c","year":"y"})
iso=o.dropna(subset=["c"]).drop_duplicates("country").set_index("country").c
o=o[["c","y","coal_co2","oil_co2","gas_co2"]]
ce=pd.read_csv(here/"data_external/ceds_2022_emissions_by_fuel_owid.csv"); ce["c"]=ce.Entity.map(iso); ce=ce.dropna(subset=["c"]).rename(columns={"Year":"y"})
ce["coal_so2"]=ce[["hard_coal_so2","brown_coal_so2","coal_coke_so2"]].sum(axis=1); ce["oil_so2"]=ce[["heavy_oil_so2","light_oil_so2","diesel_oil_so2"]].sum(axis=1)
ce=ce[["c","y","coal_so2","oil_so2","natural_gas_so2","process_so2","biomass_so2"]]
p=pd.read_csv(here/"pwt_country_year.csv")[["c","y","hc"]]
d=d.merge(o,on=["c","y"],how="left").merge(ce,on=["c","y"],how="left").merge(p,on=["c","y"],how="left")
L=lambda x: np.log(x.where(x>0))
d["ln_so2_coal_ef"]=L(d.coal_so2/d.coal_co2); d["ln_so2_oil_ef"]=L(d.oil_so2/d.oil_co2); d["ln_so2_fossil_ef"]=L((d.coal_so2+d.oil_so2+d.natural_gas_so2)/(d.coal_co2+d.oil_co2+d.gas_co2))
d["ln_so2_process"]=L(d.process_so2); d["so2_coal_sh"]=d.coal_so2/d.so2_total; d["lnpc2"]=d.lnpc**2; d["ln_coal_co2"]=L(d.coal_co2); d["ln_so2_coal"]=L(d.coal_so2)
lines=[]
def say(s): print(s); lines.append(s)
f3=lambda t,k: f"{t.loc[k,'Estimate']:+.3f}({t.loc[k,'Std. Error']:.3f})"
def st(t,k):
    z=abs(t.loc[k,'Estimate']/t.loc[k,'Std. Error']); return "***" if z>2.576 else "**" if z>1.96 else "*" if z>1.645 else " "
def fit(y,rhs,s): return pf.feols(f"{y} ~ {rhs} | c + y",data=s,vcov={"CRV1":"c"}).tidy()
say("MECHANISM 1: technique (emission factors). base spec c+y, lnpop, lnpc, lnpc2; air = ln GACI_cwm")
for y,lab in [("ln_so2gdp","ln SO2/GDP (total)"),("ln_so2_coal","ln coal SO2 (level)"),("ln_coal_co2","ln coal CO2 (coal use scale)"),("ln_so2_coal_ef","ln SO2 per coal CO2 (coal emission factor)"),("ln_so2_oil_ef","ln SO2 per oil CO2 (oil emission factor)"),("ln_so2_fossil_ef","ln SO2 per fossil CO2 (all fuels)"),("ln_so2_process","ln process SO2 (smelters, refineries)"),("so2_coal_sh","coal share of SO2")]:
    s=d.dropna(subset=[y,"air","lnpop","lnpc"]); t=fit(y,"air + lnpop + lnpc + lnpc2",s); say(f"  {lab:46s} {f3(t,'air')}{st(t,'air')}  N={len(s)}")
say("\nMECHANISM 2: absorptive capacity. air x human-capital tercile (PWT hc, 1996), base spec")
d["hc96"]=d.c.map(d[d.y==1996].set_index("c").hc); d["hc_ter"]=pd.qcut(d.hc96,3,labels=["lowHC","midHC","highHC"]).astype(str)
for y in ["ln_so2gdp","ln_so2_coal_ef","renew_sh","ln_ci"]:
    parts=[]
    for h in ["lowHC","midHC","highHC"]:
        s=d[d.hc_ter==h].dropna(subset=[y,"air","lnpop","lnpc"]); t=fit(y,"air + lnpop + lnpc + lnpc2",s); parts.append(f"{h} {f3(t,'air')}{st(t,'air')}")
    say(f"  {y:16s} " + " | ".join(parts))
say("\nMECHANISM 3: economy-type interactions (1996 characteristic above median), base spec")
d["serv96"]=d.c.map(d[d.y==1996].set_index("c").serv_sh); d["merch96"]=d.c.map(d[d.y==1996].set_index("c").merch_share)
for nm,v in [("services share 1996 high","serv96"),("merch. trade share 1996 high","merch96"),("human capital 1996 high","hc96")]:
    d["hi"]=(d[v]>d.groupby("c")[v].first().median()).astype(float); d["air_hi"]=d.air*d.hi
    for y in ["ln_so2gdp","renew_sh","ln_ci"]:
        s=d.dropna(subset=[y,"air","lnpop","lnpc",v]); t=fit(y,"air + air_hi + lnpop + lnpc + lnpc2",s)
        say(f"  {nm:30s} {y:10s} air {f3(t,'air')}{st(t,'air')}  air x high {f3(t,'air_hi')}{st(t,'air_hi')}")
open(here/"_out_mechanism.txt","w").write("\n".join(lines))
