"""
v3: AIR ONLY.  Does air connectivity make an economy cleaner, and through which channel?
Full sample 1996-2023 (sea is a control / robustness only).
  A  main: y ~ air + lnpop (+lnpc) | c + y ; exact decomposition ln CO2/GDP = ln energy/GDP + ln CO2/energy
  B  robustness to sea controls: + ln_sea_ma (geo, full sample); + ln_lsci (2006+)
  C  dynamics: long differences (5-, 10-year) ; distributed lag (air, air_t-5)
  D  Gelbach channel decomposition on the full sample (income | composition | openness | urbanisation)
  E  heterogeneity by 1996 income tercile ; by region
  F  IV: tourism_int, feyrer_int separately and jointly
  G  placebo-ish: aviation's own CO2 share; pre-period (1996-2005) vs post (2006-2023)
"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib
warnings.filterwarnings("ignore")
here = pathlib.Path(__file__).resolve().parent
d = pd.read_csv(here/"clean_open_panel.csv")
d = d.sort_values(["c","y"]).reset_index(drop=True)
def L(x): return np.log(x.where(x > 0))
# OWID aviation share check uses GACI_CO2 airport emissions? skip; use owid-co2 'co2' only.
res=[]; lines=[]
def say(s=""): print(s); lines.append(s)
def fit(y, rhs, dd, iv=None):
    fml = f"{y} ~ {rhs} | c + y" + (f" | air ~ {iv}" if iv else "")
    m = pf.feols(fml, data=dd, vcov={"CRV1":"c"}); return m.tidy(), m
f3=lambda t,k: f"{t.loc[k,'Estimate']:+.3f}({t.loc[k,'Std. Error']:.3f})" if k in t.index else "   .   "
def stars(t,k):
    z=abs(t.loc[k,'Estimate']/t.loc[k,'Std. Error']); return "***" if z>2.576 else "**" if z>1.96 else "*" if z>1.645 else ""
OUT=["ln_ci","ln_ei","ln_ce","ln_co2pc","ln_eint","renew_sh","elec_coal_sh","ln_so2gdp","ln_noxgdp","ln_so2pc","ln_pm25w","cement_sh","ln_gtfp_co2"]
LAB={"ln_ci":"ln CO2/GDP","ln_ei":"ln energy/GDP","ln_ce":"ln CO2/energy","ln_co2pc":"ln CO2 pc","ln_eint":"ln energy int. (WDI)","renew_sh":"renewable share pp","elec_coal_sh":"coal electricity pp","ln_so2gdp":"ln SO2/GDP","ln_noxgdp":"ln NOx/GDP","ln_so2pc":"ln SO2 pc","ln_pm25w":"ln PM2.5","cement_sh":"cement CO2 share","ln_gtfp_co2":"ln GTFP"}
say("=== A  AIR ONLY, 1996-2023, country + year FE, clustered by country.  air = ln GACI_cwm ===")
say(f"{'outcome':22s} | {'air (+lnpop)':>16s} | {'air (+lnpop+lnpc)':>18s} | {'lnpc':>14s} |    N   C")
for y in OUT:
    s=d.dropna(subset=[y,"air","lnpop","lnpc"])
    t1,m1=fit(y,"air + lnpop",s); t2,m2=fit(y,"air + lnpop + lnpc",s)
    say(f"{LAB[y]:22s} | {f3(t1,'air')+stars(t1,'air'):>16s} | {f3(t2,'air')+stars(t2,'air'):>18s} | {f3(t2,'lnpc'):>14s} | {m2._N:5d} {s.c.nunique():3d}")
    res.append({"block":"A","outcome":y,"b_air":t1.loc["air","Estimate"],"se_air":t1.loc["air","Std. Error"],"b_air_inc":t2.loc["air","Estimate"],"se_air_inc":t2.loc["air","Std. Error"],"n":m2._N})
s=d.dropna(subset=["air"]).copy(); r=pf.feols("air ~ 1 | c + y", data=s, fixef_rm="none"); sd_w=r.resid().std()
say(f"within-country SD of air = {sd_w:.3f}; between SD = {d.groupby('c').air.mean().std():.3f}; 1 within-SD of air on ln CO2/GDP = {res[0]['b_air']*sd_w*100:+.1f}% ")
say("exact decomposition (same sample): ln CO2/GDP = ln energy/GDP + ln CO2/energy")
s=d.dropna(subset=["ln_ci","ln_ei","ln_ce","air","lnpop","lnpc"])
for y in ["ln_ci","ln_ei","ln_ce"]:
    t,_=fit(y,"air + lnpop + lnpc",s); say(f"   {LAB[y]:16s} {f3(t,'air')}{stars(t,'air')}")
say()
say("=== B  robustness to sea controls (air coefficient, +lnpop +lnpc) ===")
say(f"{'outcome':22s} | {'none 96-23':>14s} {'+geo seaMA 96-23':>17s} | {'none 06-23':>14s} {'+LSCI 06-23':>14s}")
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp","ln_noxgdp","renew_sh"]:
    s=d.dropna(subset=[y,"air","lnpop","lnpc","ln_sea_ma"]); t1,_=fit(y,"air + lnpop + lnpc",s); t2,_=fit(y,"air + ln_sea_ma + lnpop + lnpc",s)
    s6=d[d.y>=2006].dropna(subset=[y,"air","lnpop","lnpc","ln_lsci"]); t3,_=fit(y,"air + lnpop + lnpc",s6); t4,_=fit(y,"air + ln_lsci + lnpop + lnpc",s6)
    say(f"{LAB[y]:22s} | {f3(t1,'air'):>14s} {f3(t2,'air'):>17s} | {f3(t3,'air'):>14s} {f3(t4,'air'):>14s}")
say()
say("=== C  dynamics ===")
for k in [5,10]:
    dd=d.set_index(["c","y"]); cols=["ln_ci","ln_ei","ln_ce","ln_so2gdp","air","lnpop","lnpc"]
    lag=dd[cols].groupby(level=0).shift(k); ld=(dd[cols]-lag).add_prefix("d"); ld=ld.reset_index().dropna()
    say(f"  {k}-year long differences, year FE, clustered by country:")
    for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp"]:
        m=pf.feols(f"d{y} ~ dair + dlnpop + dlnpc | y", data=ld, vcov={"CRV1":"c"}); t=m.tidy()
        say(f"     {LAB[y]:16s} d air {f3(t,'dair')}{stars(t,'dair')}   N={m._N}")
dd=d.copy(); dd["air_l5"]=dd.groupby("c").air.shift(5)
say("  distributed lag: y ~ air + air_{t-5} + lnpop + lnpc | c + y")
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp"]:
    s=dd.dropna(subset=[y,"air","air_l5","lnpop","lnpc"]); t,m=fit(y,"air + air_l5 + lnpop + lnpc",s)
    say(f"     {LAB[y]:16s} air {f3(t,'air')}{stars(t,'air')}  air_t-5 {f3(t,'air_l5')}{stars(t,'air_l5')}  sum {t.loc['air','Estimate']+t.loc['air_l5','Estimate']:+.3f}  N={m._N}")
say()
say("=== D  Gelbach decomposition of the air coefficient (base: air + lnpop), 1996-2023 ===")
groups={"income":["lnpc"],"composition":["manuf_sh","serv_sh","agr_sh"],"openness":["trade_gdp_wdi","fdi_in_gdp"],"urbanisation":["urban_sh"]}
meds=sum(groups.values(),[])
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp","ln_noxgdp","renew_sh"]:
    s=d.dropna(subset=[y,"air","lnpop"]+meds).copy()
    tb,_=fit(y,"air + lnpop",s); tf,mf=fit(y,"air + lnpop + "+" + ".join(meds),s)
    bb,bf=tb.loc["air","Estimate"],tf.loc["air","Estimate"]; parts=[]
    for gn,vs in groups.items():
        dsum=sum(pf.feols(f"{v} ~ air + lnpop | c + y",data=s).tidy().loc["air","Estimate"]*tf.loc[v,"Estimate"] for v in vs); parts.append(f"{gn} {dsum:+.3f} ({100*dsum/(bb) if bb!=0 else 0:+.0f}%)")
    say(f"{LAB[y]:18s} base {bb:+.3f}({tb.loc['air','Std. Error']:.3f}) -> full {bf:+.3f}({tf.loc['air','Std. Error']:.3f}) | " + " | ".join(parts) + f" | residual {bf/bb*100:+.0f}%  N={mf._N}")
say()
say("=== E  heterogeneity (air coef, +lnpop +lnpc) ===")
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp","renew_sh"]:
    parts=[]
    for ter in ["low","mid","high"]:
        s=d[d.inc_ter==ter].dropna(subset=[y,"air","lnpop","lnpc"]); t,_=fit(y,"air + lnpop + lnpc",s); parts.append(f"{ter} {f3(t,'air')}{stars(t,'air')}")
    say(f"{LAB[y]:18s} " + " | ".join(parts))
d["region"]=d.reg.str[:2]
say("  by region code (first 2 chars of reg):")
for y in ["ln_ci","ln_so2gdp"]:
    parts=[]
    for rg,s in d.dropna(subset=[y,"air","lnpop","lnpc"]).groupby("region"):
        if s.c.nunique()<8: continue
        t,_=fit(y,"air + lnpop + lnpc",s); parts.append(f"{rg}({s.c.nunique()}) {f3(t,'air')}{stars(t,'air')}")
    say(f"{LAB[y]:18s} " + " | ".join(parts))
say()
say("=== F  IV (+lnpop +lnpc), 1996-2023 ===")
s0=d.dropna(subset=["air","lnpop","lnpc","tourism_int","feyrer_int"])
fs=pf.feols("air ~ tourism_int + feyrer_int + lnpop + lnpc | c + y", data=s0, vcov={"CRV1":"c"}).tidy()
say("first stage: " + "; ".join(f"{k} {fs.loc[k,'Estimate']:+.4f} (t={fs.loc[k,'Estimate']/fs.loc[k,'Std. Error']:.1f})" for k in ["tourism_int","feyrer_int"]))
say(f"{'outcome':18s} | {'OLS':>14s} | {'IV tourism':>14s} {'IV Feyrer':>14s} {'IV both':>14s} | Sargan p")
from scipy.stats import chi2
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp","ln_noxgdp","renew_sh"]:
    s=s0.dropna(subset=[y]).copy(); to,_=fit(y,"air + lnpop + lnpc",s)
    ta,_=fit(y,"lnpop + lnpc",s,iv="tourism_int"); tb,_=fit(y,"lnpop + lnpc",s,iv="feyrer_int"); tc,mc=fit(y,"lnpop + lnpc",s,iv="tourism_int + feyrer_int")
    mr=pf.feols(f"{y} ~ lnpop + lnpc | c + y | air ~ tourism_int + feyrer_int", data=s, fixef_rm="none"); s["u2"]=mr.resid(); s=s.dropna(subset=["u2"])
    mj=pf.feols("u2 ~ tourism_int + feyrer_int + lnpop + lnpc | c + y", data=s); pj=1-chi2.cdf(mj._N*mj._r2_within,1)
    say(f"{LAB[y]:18s} | {f3(to,'air'):>14s} | {f3(ta,'air'):>14s} {f3(tb,'air'):>14s} {f3(tc,'air'):>14s} | {pj:.3f}")
say()
say("=== G  sub-periods (air coef, +lnpop +lnpc) ===")
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp"]:
    parts=[]
    for a,b in [(1996,2005),(2006,2014),(2015,2023)]:
        s=d[d.y.between(a,b)].dropna(subset=[y,"air","lnpop","lnpc"]); t,_=fit(y,"air + lnpop + lnpc",s); parts.append(f"{a}-{b} {f3(t,'air')}{stars(t,'air')}")
    say(f"{LAB[y]:18s} " + " | ".join(parts))
pd.DataFrame(res).to_csv(here/"_res_v3_air.csv",index=False); open(here/"_out_v3_air.txt","w").write("\n".join(lines))
