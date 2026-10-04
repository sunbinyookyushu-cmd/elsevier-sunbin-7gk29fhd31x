"""
Is air openness clean openness?  v2: true sea connectivity (UNCTAD LSCI), WDI composition mediators, Green TFP.
air = ln GACI_cwm ; sea = ln LSCI (annual mean of quarters), window 2006-2023 (LSCI starts 2006Q1).
Blocks
  A  OLS / +income / 2SLS(tourism_int, feyrer_int)  for intensity, pollution, energy-structure and GTFP outcomes
  A' same outcomes 1996-2023 with sea = geography-based sea market access (comparability with v1)
  B  within-country SD scaling of air vs sea
  C  exact Gelbach (2016) decomposition of the air coefficient: income | composition (manuf/serv/agr shares) | openness (trade, FDI) | urbanisation
  D  two-IV agreement: just-identified with each instrument, over-identified, Sargan J
  E  heterogeneity by 1996 income tercile
Outputs: _res_v2.csv, _out_v2.txt
"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib
warnings.filterwarnings("ignore")
here = pathlib.Path(__file__).resolve().parent
g = pd.read_csv(here.parent/"gaci_panel_combined.csv")
o = pd.read_csv(here.parent/"GACI_CO2/data_external/owid-co2-data.csv", low_memory=False).rename(columns={"iso_code":"c","year":"y"})
o = o[["c","y","co2","co2_per_capita","co2_per_gdp","energy_per_gdp","co2_per_unit_energy","coal_co2","cement_co2"]]
d = g.merge(o, on=["c","y"], how="inner"); d = d[d.y.between(1996,2023)].copy()
def L(x): return np.log(x.where(x > 0))
d["ln_ci"]=L(d.co2_per_gdp); d["ln_ei"]=L(d.energy_per_gdp); d["ln_ce"]=L(d.co2_per_unit_energy); d["ln_co2pc"]=L(d.co2_per_capita)
d["cement_sh"]=d.cement_co2/d.co2
pol = pd.read_csv(here/"pollution_country_year.csv").rename(columns={"iso3":"c","year":"y"})
d = d.merge(pol, on=["c","y"], how="left"); d["gdp"]=np.exp(d.lngdp); d["pop"]=np.exp(d.lnpop)
d["ln_so2gdp"]=L(d.so2_total/d.gdp); d["ln_noxgdp"]=L(d.nox_total/d.gdp); d["ln_so2pc"]=L(d.so2_total/d["pop"])
ls = pd.read_csv(here/"lsci_country_year.csv"); wd = pd.read_csv(here/"wdi_country_year.csv")
d = d.merge(ls[["c","y","ln_lsci"]], on=["c","y"], how="left").merge(wd, on=["c","y"], how="left")
try:
    gt = pd.read_csv(here/"gtfp_country_year.csv"); d = d.merge(gt[["c","y","ln_gtfp_co2","ln_gtfp_co2so2","ln_tfp_dea","ln_geff_co2","ln_eff_tfp"]], on=["c","y"], how="left"); HAVE_GTFP=True
except FileNotFoundError: HAVE_GTFP=False
d["ln_pm25w"]=L(d.pm25_wdi); d["ln_eint"]=L(d.energy_int_mj); d["ln_gdppc_w"]=L(d.gdppc_2015usd)
d["air"]=d.ln_gaci_cwm
base = d[d.y==1996].set_index("c").lnpc; d["inc96"]=d.c.map(base); d["inc_ter"]=pd.qcut(d.inc96, 3, labels=["low","mid","high"])
res=[]; lines=[]
def say(s=""): print(s); lines.append(s)
def fit(y, rhs, dd, iv=None, label="", sample=""):
    fml = f"{y} ~ {rhs} | c + y" + (f" | air ~ {iv}" if iv else "")
    m = pf.feols(fml, data=dd, vcov={"CRV1":"c"}); t = m.tidy()
    row = {"outcome":y,"spec":label,"sample":sample,"n":m._N,"n_c":dd.c.nunique()}
    for k in ["air","sea","lnpc"]:
        if k in t.index: row[f"b_{k}"]=t.loc[k,"Estimate"]; row[f"se_{k}"]=t.loc[k,"Std. Error"]
    res.append(row); return t, m
f3=lambda t,k: f"{t.loc[k,'Estimate']:+.3f}({t.loc[k,'Std. Error']:.3f})" if k in t.index else "   .   "
OUT = ["ln_ci","ln_ei","ln_ce","ln_co2pc","ln_eint","renew_sh","elec_coal_sh","cement_sh","ln_so2gdp","ln_noxgdp","ln_pm25w"] + (["ln_gtfp_co2","ln_gtfp_co2so2","ln_tfp_dea","ln_geff_co2"] if HAVE_GTFP else [])

def blockA(dd, seavar, title, sample):
    dd = dd.copy(); dd["sea"] = dd[seavar]
    say(f"=== A {title}: country + year FE, country-clustered SE ===")
    say(f"{'outcome':14s} | {'OLS air':>14s} {'OLS sea':>14s} | {'+lnpc air':>14s} {'+lnpc sea':>14s} | {'2SLS air':>14s} {'2SLS sea':>14s} |    N  (C)")
    for y in OUT:
        s = dd.dropna(subset=[y,"air","sea","lnpop","lnpc","tourism_int","feyrer_int"])
        if len(s) < 200: continue
        t1,_=fit(y,"air + sea + lnpop",s,label="ols",sample=sample); t2,_=fit(y,"air + sea + lnpop + lnpc",s,label="ols_inc",sample=sample)
        t3,m3=fit(y,"sea + lnpop + lnpc",s,iv="tourism_int + feyrer_int",label="iv_inc",sample=sample)
        say(f"{y:14s} | {f3(t1,'air'):>14s} {f3(t1,'sea'):>14s} | {f3(t2,'air'):>14s} {f3(t2,'sea'):>14s} | {f3(t3,'air'):>14s} {f3(t3,'sea'):>14s} | {m3._N:5d} ({s.c.nunique()})")
    fs = pf.feols("air ~ tourism_int + feyrer_int + sea + lnpop + lnpc | c + y", data=dd.dropna(subset=["air","sea","lnpop","lnpc","tourism_int","feyrer_int"]), vcov={"CRV1":"c"})
    tt = fs.tidy(); say("first stage (clustered t): " + "; ".join(f"{k} {tt.loc[k,'Estimate']:+.4f} (t={tt.loc[k,'Estimate']/tt.loc[k,'Std. Error']:.1f})" for k in ["tourism_int","feyrer_int"]))
    # within-country SD of air and sea after two-way demeaning
    s = dd.dropna(subset=["air","sea"]).copy()
    for v in ["air","sea"]:
        r = pf.feols(f"{v} ~ 1 | c + y", data=s, fixef_rm="none"); s[f"{v}_w"] = r.resid()
    say(f"B within SD (two-way demeaned): air {s.air_w.std():.3f}, sea {s.sea_w.std():.3f}  -> multiply air coef by {s.air_w.std():.3f} and sea coef by {s.sea_w.std():.3f} for 1-within-SD effects"); say()

dL = d[d.y>=2006].dropna(subset=["ln_lsci"])
blockA(dL, "ln_lsci", "2006-2023, air = ln GACI_cwm, sea = ln LSCI", "lsci06")
blockA(d,  "ln_sea_ma", "1996-2023, air = ln GACI_cwm, sea = ln sea market access (v1 measure)", "sema96")
blockA(d[d.y>=2006], "ln_sea_ma", "2006-2023, sea = ln sea market access (same window as LSCI)", "sema06")

# ---- C: exact Gelbach decomposition of the air coefficient (LSCI sample) ----
say("=== C Gelbach (2016) decomposition of the OLS air coefficient, 2006-2023, sea = ln LSCI ===")
groups = {"income (lnpc)":["lnpc"], "composition (manuf, serv, agr % GDP)":["manuf_sh","serv_sh","agr_sh"], "openness (trade, FDI % GDP)":["trade_gdp_wdi","fdi_in_gdp"], "urbanisation":["urban_sh"]}
meds = sum(groups.values(), [])
for y in ["ln_ci","ln_ei","ln_ce","ln_co2pc","ln_so2gdp","ln_noxgdp"] + (["ln_gtfp_co2"] if HAVE_GTFP else []):
    s = dL.dropna(subset=[y,"air","ln_lsci","lnpop"]+meds).copy(); s["sea"]=s.ln_lsci
    tb,_ = fit(y,"air + sea + lnpop",s,label="gel_base",sample="lsci06"); tf,mf = fit(y,"air + sea + lnpop + "+" + ".join(meds),s,label="gel_full",sample="lsci06")
    bb, bf = tb.loc["air","Estimate"], tf.loc["air","Estimate"]
    parts=[]; tot=0
    for gname, vs in groups.items():
        dsum=0
        for v in vs:
            ta = pf.feols(f"{v} ~ air + sea + lnpop | c + y", data=s, vcov={"CRV1":"c"}).tidy()
            dsum += ta.loc["air","Estimate"]*tf.loc[v,"Estimate"]
        tot+=dsum; parts.append(f"{gname} {dsum:+.3f}")
    say(f"{y:10s} base {bb:+.3f}({tb.loc['air','Std. Error']:.3f}) -> full {bf:+.3f}({tf.loc['air','Std. Error']:.3f}); explained {bb-bf:+.3f} = " + " | ".join(parts) + f"   [check sum {tot:+.3f}]  N={mf._N}")
    res.append({"outcome":y,"spec":"gelbach","sample":"lsci06","n":mf._N,"b_base":bb,"b_full":bf,**{f"d_{k.split()[0]}":None for k in groups}})
say()
# ---- D: two-IV agreement ----
say("=== D instrument-by-instrument 2SLS (+lnpc, sea=ln LSCI, 2006-2023) and Sargan J for the over-identified model ===")
say(f"{'outcome':10s} | {'tourism IV':>14s} {'Feyrer IV':>14s} {'both':>14s} | Sargan J p")
for y in ["ln_ci","ln_ei","ln_ce","ln_co2pc","ln_so2gdp","ln_noxgdp","ln_pm25w"] + (["ln_gtfp_co2"] if HAVE_GTFP else []):
    s = dL.dropna(subset=[y,"air","ln_lsci","lnpop","lnpc","tourism_int","feyrer_int"]).copy(); s["sea"]=s.ln_lsci
    ta,_=fit(y,"sea + lnpop + lnpc",s,iv="tourism_int",label="iv_tour",sample="lsci06"); tb,_=fit(y,"sea + lnpop + lnpc",s,iv="feyrer_int",label="iv_feyrer",sample="lsci06"); tc,mc=fit(y,"sea + lnpop + lnpc",s,iv="tourism_int + feyrer_int",label="iv_both",sample="lsci06")
    # Sargan: regress 2SLS residual on instruments + exog within FE; J = N * R2
    try:
        mr = pf.feols(f"{y} ~ sea + lnpop + lnpc | c + y | air ~ tourism_int + feyrer_int", data=s, fixef_rm="none")
        s = s.copy(); s["u2"] = mr.resid(); s = s.dropna(subset=["u2"])
        mj = pf.feols("u2 ~ tourism_int + feyrer_int + sea + lnpop + lnpc | c + y", data=s)
        from scipy.stats import chi2
        J = mj._N * mj._r2_within; pj = 1-chi2.cdf(J, 1)
    except Exception: pj=np.nan
    say(f"{y:10s} | {f3(ta,'air'):>14s} {f3(tb,'air'):>14s} {f3(tc,'air'):>14s} | {pj:.3f}")
say()
# ---- E: heterogeneity ----
say("=== E heterogeneity by 1996 income tercile (OLS + lnpc, sea=ln LSCI, 2006-2023): air coefficient ===")
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp","ln_noxgdp","ln_pm25w"] + (["ln_gtfp_co2"] if HAVE_GTFP else []):
    parts=[]
    for ter in ["low","mid","high"]:
        s=dL[dL.inc_ter==ter].dropna(subset=[y,"air","ln_lsci","lnpop","lnpc"]).copy(); s["sea"]=s.ln_lsci
        if len(s)<100: parts.append(f"{ter} ."); continue
        t,_=fit(y,"air + sea + lnpop + lnpc",s,label=f"ols_inc_{ter}",sample="lsci06"); parts.append(f"{ter} {f3(t,'air')} / sea {f3(t,'sea')}")
    say(f"{y:10s} " + " | ".join(parts))
pd.DataFrame(res).to_csv(here/"_res_v2.csv", index=False); open(here/"_out_v2.txt","w").write("\n".join(lines))
