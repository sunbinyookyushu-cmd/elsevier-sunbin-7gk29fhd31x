"""Is air openness clean openness?  First pass on data already in the repo.
Panel: gaci_panel_combined.csv (184 countries, 1996-2023: ln GACI_cwm, trade, GDP, pc income, pop, tourism_int, feyrer_int,
       ln_sea_ma = geography-based sea market access) x OWID CO2/energy (co2, co2_per_gdp, energy_per_gdp,
       co2_per_unit_energy, coal/oil/gas/cement CO2).
Outcomes (national, NOT aviation): ln CO2/GDP (carbon intensity of the economy), ln energy/GDP (energy intensity),
       ln CO2/energy (fuel-mix dirtiness), coal share of CO2, cement share of CO2 (heavy-industry proxy), ln CO2, ln CO2 pc.
Specs: (1) OLS FE: y ~ ln GACI + ln sea MA + ln pop | country + year
       (2) + ln income pc  (income held fixed: what remains is composition + knowledge, not scale/technique via income)
       (3) 2SLS: ln GACI instrumented by tourism_int and feyrer_int (sea MA exogenous geography x world trade)
       (4) heterogeneity by baseline (1996) income tercile
       (5) Gelbach-style: add trade_share, lnpc, merch_share sequentially and see how much of the GACI coefficient they absorb
Pending data (see README): UNCTAD LSCI (true sea connectivity, 2006-), WDI manufacturing/services shares, PM2.5, CEDS SO2,
       UNIDO pollution-intensive industry share.
Output: _res_clean_openness.csv, _out_clean_openness.txt
"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib
warnings.filterwarnings("ignore")
here = pathlib.Path(__file__).resolve().parent
g = pd.read_csv(here.parent/"gaci_panel_combined.csv")
o = pd.read_csv(here.parent/"GACI_CO2/data_external/owid-co2-data.csv", low_memory=False).rename(columns={"iso_code":"c","year":"y"})
o = o[["c","y","co2","co2_per_capita","co2_per_gdp","energy_per_gdp","co2_per_unit_energy","coal_co2","oil_co2","gas_co2","cement_co2","consumption_co2","primary_energy_consumption"]]
d = g.merge(o, on=["c","y"], how="inner"); d = d[d.y.between(1996,2023)].copy()
def L(x): return np.log(x.where(x > 0))
d["ln_ci"]=L(d.co2_per_gdp); d["ln_ei"]=L(d.energy_per_gdp); d["ln_ce"]=L(d.co2_per_unit_energy); d["ln_co2"]=L(d.co2); d["ln_co2pc"]=L(d.co2_per_capita)
d["coal_sh"]=d.coal_co2/d.co2; d["cement_sh"]=d.cement_co2/d.co2; d["ln_cement"]=L(d.cement_co2)
pol = pd.read_csv(here/"pollution_country_year.csv").rename(columns={"iso3":"c","year":"y"})
d = d.merge(pol, on=["c","y"], how="left")
d["gdp"] = np.exp(d.lngdp); d["pop"] = np.exp(d.lnpop)
d["ln_so2pc"]=L(d.so2_total/d["pop"]); d["ln_noxpc"]=L(d.nox_total/d["pop"]); d["ln_so2gdp"]=L(d.so2_total/d.gdp); d["ln_noxgdp"]=L(d.nox_total/d.gdp); d["ln_pm25"]=L(d.pm25_exposure)
d["air"]=d.ln_gaci_cwm; d["sea"]=d.ln_sea_ma
base = d[d.y==1996].set_index("c").lnpc; d["inc96"]=d.c.map(base); d["inc_ter"]=pd.qcut(d.inc96, 3, labels=["low","mid","high"])
OUT=["ln_ci","ln_ei","ln_ce","coal_sh","cement_sh","ln_co2","ln_co2pc","ln_so2pc","ln_so2gdp","ln_noxpc","ln_noxgdp","ln_pm25"]
res=[]; lines=[]
def say(s): print(s); lines.append(s)
def fit(y, rhs, dd, iv=None, label=""):
    fml = f"{y} ~ {rhs} | c + y" + (f" | air ~ {iv}" if iv else "")
    m = pf.feols(fml, data=dd, vcov={"CRV1":"c"}); t = m.tidy()
    row = {"outcome":y,"spec":label,"n":m._N}
    for k in ["air","sea","lnpc"]:
        if k in t.index: row[f"b_{k}"]=t.loc[k,"Estimate"]; row[f"se_{k}"]=t.loc[k,"Std. Error"]
    if iv:
        try: row["kp_f"] = float(m._f_stat_1st_stage) if hasattr(m,"_f_stat_1st_stage") else np.nan
        except Exception: row["kp_f"]=np.nan
    res.append(row); return t, m
say("=== (1)-(3): air = ln GACI_cwm, sea = ln sea market access; country + year FE; country-clustered SE ===")
say(f"{'outcome':10s} | {'OLS air':>14s} {'OLS sea':>14s} | {'+lnpc air':>14s} {'+lnpc sea':>14s} | {'2SLS air':>14s} {'2SLS sea':>14s} | N")
for y in OUT:
    dd = d.dropna(subset=[y,"air","sea","lnpop","lnpc","tourism_int","feyrer_int"])
    t1,_ = fit(y,"air + sea + lnpop",dd,label="ols"); t2,_ = fit(y,"air + sea + lnpop + lnpc",dd,label="ols_inc"); t3,m3 = fit(y,"sea + lnpop + lnpc",dd,iv="tourism_int + feyrer_int",label="iv_inc")
    f=lambda t,k: f"{t.loc[k,'Estimate']:+.3f}({t.loc[k,'Std. Error']:.3f})"
    say(f"{y:10s} | {f(t1,'air'):>14s} {f(t1,'sea'):>14s} | {f(t2,'air'):>14s} {f(t2,'sea'):>14s} | {f(t3,'air'):>14s} {f(t3,'sea'):>14s} | {m3._N}")
# first stage strength
fs = pf.feols("air ~ tourism_int + feyrer_int + sea + lnpop + lnpc | c + y", data=d.dropna(subset=["air","sea","lnpop","lnpc","tourism_int","feyrer_int"]), vcov="hetero")
say("\nfirst stage: " + "; ".join(f"{k} {fs.tidy().loc[k,'Estimate']:+.4f} (t={fs.tidy().loc[k,'Estimate']/fs.tidy().loc[k,'Std. Error']:.1f})" for k in ["tourism_int","feyrer_int"]) + f"; F-stat(2) ~ {fs.wald_test(R=None) if False else ''}")
say("\n=== (4) heterogeneity by 1996 income tercile (OLS + lnpc): air coefficient ===")
for y in ["ln_ci","ln_ei","ln_ce","cement_sh","ln_so2gdp","ln_noxgdp"]:
    parts=[]
    for ter in ["low","mid","high"]:
        dd=d[(d.inc_ter==ter)].dropna(subset=[y,"air","sea","lnpop","lnpc"])
        t,_=fit(y,"air + sea + lnpop + lnpc",dd,label=f"ols_inc_{ter}"); parts.append(f"{ter} {t.loc['air','Estimate']:+.3f}({t.loc['air','Std. Error']:.3f})")
    say(f"{y:10s} " + " | ".join(parts))
say("\n=== (5) Gelbach-style absorption of the air coefficient on ln CO2/GDP (OLS) ===")
dd=d.dropna(subset=["ln_ci","air","sea","lnpop","lnpc","trade_share","merch_share"])
for rhs,lab in [("air + sea + lnpop","base"),("air + sea + lnpop + lnpc","+income"),("air + sea + lnpop + lnpc + trade_share","+trade"),("air + sea + lnpop + lnpc + trade_share + merch_share","+merch share")]:
    t,_=fit("ln_ci",rhs,dd,label=f"gelbach_{lab}"); say(f"{lab:14s} air {t.loc['air','Estimate']:+.3f} ({t.loc['air','Std. Error']:.3f})   sea {t.loc['sea','Estimate']:+.3f} ({t.loc['sea','Std. Error']:.3f})")
pd.DataFrame(res).to_csv(here/"_res_clean_openness.csv", index=False); open(here/"_out_clean_openness.txt","w").write("\n".join(lines))
