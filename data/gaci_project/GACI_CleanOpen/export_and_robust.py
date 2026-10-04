"""Robustness: is the larger air coefficient under LSCI due to the measure or the (coastal) sample?  + export Stata panel."""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib, pyreadstat
warnings.filterwarnings("ignore")
exec(open(pathlib.Path(__file__).resolve().parent/"analysis_v2_lsci.py").read().split("res=[]; lines=[]")[0])   # reuse data build
d["ln_lsci_sea"]=d.ln_lsci; d["ln_sea_ma_geo"]=d.ln_sea_ma
def b(y, rhs, s):
    t=pf.feols(f"{y} ~ {rhs} | c + y", data=s, vcov={"CRV1":"c"}).tidy(); return f"{t.loc['air','Estimate']:+.3f}({t.loc['air','Std. Error']:.3f})", len(s)
print("air coefficient (+lnpop +lnpc), 2006-2023 | sample: LSCI(coastal) vs all | sea control: LSCI / geo MA / none")
print(f"{'outcome':12s} | {'LSCI smp, LSCI':>16s} {'LSCI smp, geoMA':>16s} {'LSCI smp, none':>16s} | {'all, geoMA':>16s} {'all, none':>16s}")
for y in ["ln_ci","ln_ei","ln_ce","ln_co2pc","ln_so2gdp","ln_noxgdp","renew_sh"]:
    sL=d[(d.y>=2006)].dropna(subset=[y,"air","ln_lsci","ln_sea_ma","lnpop","lnpc"]); sA=d[(d.y>=2006)].dropna(subset=[y,"air","ln_sea_ma","lnpop","lnpc"])
    a1,n1=b(y,"air + ln_lsci + lnpop + lnpc",sL); a2,_=b(y,"air + ln_sea_ma + lnpop + lnpc",sL); a3,_=b(y,"air + lnpop + lnpc",sL); a4,n4=b(y,"air + ln_sea_ma + lnpop + lnpc",sA); a5,_=b(y,"air + lnpop + lnpc",sA)
    print(f"{y:12s} | {a1:>16s} {a2:>16s} {a3:>16s} | {a4:>16s} {a5:>16s}   N={n1}/{n4}")
# landlocked flag for the paper
ml=pd.read_json(here.parents[2]/"data/raw/airports/mledoze_countries.json"); ll=dict(zip(ml.cca3, ml.landlocked.astype(int))); d["landlocked"]=d.c.map(ll)
print("\nLSCI sample landlocked share:", d[d.y>=2006].dropna(subset=["ln_lsci"]).groupby("c").landlocked.first().mean().round(3), " full sample:", d.groupby("c").landlocked.first().mean().round(3))
# export
keep=["c","y","reg","air","ln_gaci_cwm","ln_gaci_mean","gaci_cwmean","ln_lsci","ln_sea_ma","ln_air_ma","lngdp","lnpc","lnpop","trade_share","merch_share","tourism_int","feyrer_int","landlocked","inc96",
      "co2","co2_per_capita","co2_per_gdp","energy_per_gdp","co2_per_unit_energy","coal_co2","cement_co2","ln_ci","ln_ei","ln_ce","ln_co2pc","cement_sh",
      "so2_total","nox_total","pm25_exposure","ln_so2gdp","ln_noxgdp","ln_so2pc","pm25_wdi","ln_pm25w",
      "manuf_sh","ind_sh","serv_sh","agr_sh","hitech_x_sh","manuf_x_sh","energy_pc_kgoe","energy_int_mj","ln_eint","elec_coal_sh","renew_sh","gdppc_2015usd","urban_sh","fdi_in_gdp","trade_gdp_wdi"] + (["ln_gtfp_co2","ln_gtfp_co2so2","ln_tfp_dea","ln_geff_co2","ln_eff_tfp"] if HAVE_GTFP else [])
out=d[keep].copy(); out["inc_ter"]=d.inc_ter.astype(str)
for c in out.columns:
    if out[c].dtype==object: out[c]=out[c].fillna("")
pyreadstat.write_dta(out, str(here/"stata/clean_open_panel.dta"), version=14)
out.to_csv(here/"clean_open_panel.csv", index=False)
print("exported", out.shape, "->", here/"stata/clean_open_panel.dta")
