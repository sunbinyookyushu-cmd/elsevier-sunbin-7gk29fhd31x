"""
Core table set: "Is air connectivity clean connectivity?"  (air-only, country-level, 1996-2023)
Base spec: y ~ ln GACI_cwm + ln pop + ln pc + (ln pc)^2 | country + year ; SE clustered by country.
T1 main outcomes | T2 technique (SO2 emission factors) | T3 Gelbach channels | T4 heterogeneity | T5 IV
A1 robustness (controls, sea, long differences, strict FE, sub-periods) | A2 alternative GACI aggregates
Outputs: tables/T*.tex, tables/A*.tex, tables/_all_tables.txt, tables/_coefs.csv
"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib; warnings.filterwarnings("ignore")
from scipy.stats import chi2
here=pathlib.Path(__file__).resolve().parent; T=here/"tables"
d=pd.read_csv(here/"clean_open_panel.csv").drop(columns=["coal_co2"],errors="ignore").sort_values(["c","y"])
o=pd.read_csv(here.parent/"GACI_CO2/data_external/owid-co2-data.csv",low_memory=False).rename(columns={"iso_code":"c","year":"y"})
iso=o.dropna(subset=["c"]).drop_duplicates("country").set_index("country").c; o=o[["c","y","coal_co2","oil_co2","gas_co2"]]
ce=pd.read_csv(here/"data_external/ceds_2022_emissions_by_fuel_owid.csv"); ce["c"]=ce.Entity.map(iso); ce=ce.dropna(subset=["c"]).rename(columns={"Year":"y"})
ce["coal_so2"]=ce[["hard_coal_so2","brown_coal_so2","coal_coke_so2"]].sum(axis=1); ce["oil_so2"]=ce[["heavy_oil_so2","light_oil_so2","diesel_oil_so2"]].sum(axis=1)
p=pd.read_csv(here/"pwt_country_year.csv")[["c","y","rnna","emp"]]
g=pd.read_csv(here.parent/"gaci_panel_combined.csv")[["c","y","gaci_cwmean","gaci_mean"]].rename(columns={"gaci_cwmean":"g_cwm0","gaci_mean":"g_mean0"})
d=d.merge(o,on=["c","y"],how="left").merge(ce[["c","y","coal_so2","oil_so2","natural_gas_so2","process_so2"]],on=["c","y"],how="left").merge(p,on=["c","y"],how="left").merge(g,on=["c","y"],how="left")
L=lambda x: np.log(x.where(x>0))
d["lnpc2"]=d.lnpc**2; d["lnkl"]=L(d.rnna/d.emp); d["lnkl2"]=d.lnkl**2
d["ln_so2_coal_ef"]=L(d.coal_so2/d.coal_co2); d["ln_so2_oil_ef"]=L(d.oil_so2/d.oil_co2); d["ln_so2_fossil_ef"]=L((d.coal_so2+d.oil_so2+d.natural_gas_so2)/(d.coal_co2+d.oil_co2+d.gas_co2))
d["ln_coal_co2"]=L(d.coal_co2); d["ln_so2_process"]=L(d.process_so2); d["so2_coal_sh"]=d.coal_so2/d.so2_total
d["region"]=d.reg.str[:2]; d["ty"]=d.inc_ter+"_"+d.y.astype(str); d["ry"]=d.region+"_"+d.y.astype(str)
d["merch96"]=d.c.map(d[d.y==1996].set_index("c").merch_share); d["serv96"]=d.c.map(d[d.y==1996].set_index("c").serv_sh)
d["goods_econ"]=(d.merch96>d.groupby("c").merch96.first().median()).astype(float); d["air_goods"]=d.air*d.goods_econ
# ---- unified analysis sample: country-years with all T1 outcomes, controls and both instruments (1996-2019, 149 countries) ----
CORE=["air","lnpop","lnpc","ln_so2gdp","ln_noxgdp","renew_sh","ln_ci","ln_ei","ln_ce","tourism_int","feyrer_int"]
d=d.dropna(subset=CORE).copy()
print("UNIFIED SAMPLE:", len(d), "obs,", d.c.nunique(), "countries,", d.y.min(), "-", d.y.max())
BASE="air + lnpop + lnpc + lnpc2"
LAB={"ln_so2gdp":"ln SO2/GDP","ln_so2pc":"ln SO2 pc","ln_noxgdp":"ln NOx/GDP","renew_sh":"Renewable share (pp)","ln_ci":"ln CO2/GDP","ln_ei":"ln energy/GDP","ln_ce":"ln CO2/energy","ln_co2pc":"ln CO2 pc",
     "ln_coal_co2":"ln coal CO2 (scale)","ln_so2_coal_ef":"ln SO2/coal CO2","ln_so2_oil_ef":"ln SO2/oil CO2","ln_so2_fossil_ef":"ln SO2/fossil CO2","ln_so2_process":"ln process SO2","so2_coal_sh":"Coal share of SO2",
     "air":"ln GACI","lnpc":"ln GDP pc","lnpc2":"(ln GDP pc)$^2$","lnpop":"ln population","air_goods":"ln GACI $\\times$ goods economy"}
coefs=[]; txt=[]; TABLES=[]
def say(s=""): print(s); txt.append(s)
def fe(y,rhs,s,fe="c + y",iv=None):
    m=pf.feols(f"{y} ~ {rhs} | {fe}"+(f" | air ~ {iv}" if iv else ""),data=s,vcov={"CRV1":"c"}); return m
def cell(m,k):
    t=m.tidy()
    if k not in t.index: return ("","")
    b,se=t.loc[k,"Estimate"],t.loc[k,"Std. Error"]; z=abs(b/se); st="***" if z>2.576 else "**" if z>1.96 else "*" if z>1.645 else ""
    return (f"{b:.3f}{st}",f"({se:.3f})")
def fsF(m_or_s, iv="feyrer_int", rhs="lnpop + lnpc + lnpc2"):
    """clustered first-stage F for the IV spec on sample s"""
    s=m_or_s; fs=pf.feols(f"air ~ {iv} + {rhs} | c + y",data=s,vcov={"CRV1":"c"}); ks=[k for k in fs.tidy().index if k in iv.split(" + ")]
    idx=[list(fs.coef().index).index(k) for k in ks]; b=fs.coef().values[idx]; V=fs._vcov[np.ix_(idx,idx)]; return float(b@np.linalg.solve(V,b))/len(ks)
def table(name,title,cols,rows=None,ms=None,extra=None,note="",panels=None):
    """panels: list of (panel_label, models, coef_rows, extra_rows). Single-panel call: rows/ms/extra."""
    if panels is None: panels=[(None,ms,rows,extra)]
    lines=[]
    for plab,pms,prows,pextra in panels:
        if plab: lines.append((f"__PANEL__{plab}",[""]*len(cols)))
        for k in prows:
            cs=[cell(m,k) for m in pms]; lines.append((LAB.get(k,k),[c[0] for c in cs])); lines.append(("",[c[1] for c in cs]))
        if pextra: lines+=pextra
        lines.append(("Observations",[f"{m._N:,}" for m in pms]))
    w=max(14,max(len(c) for c in cols)+2); say(f"\n{name}. {title}"); say(" "*26+"".join(f"{c:>{w}s}" for c in cols))
    for lab,vals in lines:
        if lab.startswith("__PANEL__"): say(f"--- {lab[9:]} ---")
        else: say(f"{lab:26s}"+"".join(f"{v:>{w}s}" for v in vals))
    tex=["\\begin{table}[htbp]\\centering\\small",f"\\caption{{{title}}}\\label{{tab:{name}}}","\\begin{tabular}{l"+"c"*len(cols)+"}","\\toprule"," & "+" & ".join(cols)+" \\\\","\\midrule"]
    for lab,vals in lines:
        if lab.startswith("__PANEL__"): tex.append("\\midrule"); tex.append(f"\\multicolumn{{{len(cols)+1}}}{{l}}{{\\textit{{{lab[9:]}}}}} \\\\"); continue
        if lab=="Observations": tex.append("\\midrule")
        tex.append(f"{lab} & "+" & ".join(vals)+" \\\\")
    tex+=["\\bottomrule","\\end{tabular}",f"\\begin{{minipage}}{{0.95\\textwidth}}\\footnotesize {note}\\end{{minipage}}","\\end{table}"]
    (T/f"{name}.tex").write_text("\n".join(tex))
    TABLES.append({"name":name,"title":title,"cols":cols,"rows":[[lab,vals] for lab,vals in lines],"note":note})
    for plab,pms,prows,pextra in panels:
        for c_,m in zip(cols,pms):
            t=m.tidy()
            for k in t.index: coefs.append({"table":name,"panel":plab or "A","column":c_,"var":k,"b":t.loc[k,"Estimate"],"se":t.loc[k,"Std. Error"],"n":m._N})
NOTE_IV=" Panel B instruments ln GACI with Feyrer-type air market access (country geography $\\times$ world air-traffic growth); first-stage F is the cluster-robust F on the excluded instrument."
NOTE_BASE="Unified sample: 149 countries, 1996--2019, country-years with all Table 1 outcomes and instruments observed. Country and year fixed effects; controls ln population, ln GDP per capita and its square. Standard errors clustered by country in parentheses. *, **, *** : 10, 5, 1\\%. ln GACI = log of seat-weighted mean airport GACI."
def N_c(s): return s.c.nunique()

# ---- T1 main: Panel A OLS, Panel B IV (Feyrer) ----
Y1=["ln_so2gdp","ln_so2pc","ln_noxgdp","renew_sh","ln_ci","ln_ei","ln_ce"]; msA=[]; msB=[]; Fs=[]
for y in Y1:
    s=d.dropna(subset=[y,"air","lnpop","lnpc"]); msA.append(fe(y,BASE,s)); msB.append(fe(y,"lnpop + lnpc + lnpc2",s,iv="feyrer_int")); Fs.append(f"{fsF(s):.1f}")
sd_w=pf.feols("air ~ 1 | c + y",data=d.dropna(subset=["air"]),fixef_rm="none").resid().std()
exA=[("1 within-SD effect",[f"{m.tidy().loc['air','Estimate']*sd_w*(100 if y!='renew_sh' else 1):+.1f}{'%' if y!='renew_sh' else 'pp'}" for m,y in zip(msA,Y1)])]
exB=[("First-stage F (clustered)",Fs)]
table("T1","Air connectivity and the pollution and carbon intensity of the economy, 1996--2019",[LAB[y] for y in Y1],panels=[("Panel A: OLS, country and year FE",msA,["air","lnpc","lnpc2"],exA),("Panel B: 2SLS, ln GACI instrumented by air market access",msB,["air"],exB)],note=NOTE_BASE+f" Within-country SD of ln GACI = {sd_w:.3f}. SO2 and NOx from CEDS (to 2019); renewable share from WDI; CO2 and energy from OWID/EI."+NOTE_IV)
# ---- T2 technique: Panel A OLS, Panel B IV ----
Y2=["ln_so2gdp","ln_coal_co2","ln_so2_coal_ef","ln_so2_oil_ef","ln_so2_fossil_ef","ln_so2_process","so2_coal_sh"]; msA=[]; msB=[]; Fs=[]
for y in Y2:
    s=d.dropna(subset=[y,"air","lnpop","lnpc"]); msA.append(fe(y,BASE,s)); msB.append(fe(y,"lnpop + lnpc + lnpc2",s,iv="feyrer_int")); Fs.append(f"{fsF(s):.1f}")
table("T2","Technique, not scale: SO2 emission factors by fuel",[LAB[y] for y in Y2],panels=[("Panel A: OLS, country and year FE",msA,["air"],None),("Panel B: 2SLS, ln GACI instrumented by air market access",msB,["air"],[("First-stage F (clustered)",Fs)])],note=NOTE_BASE+" Emission factor = CEDS SO2 from a fuel divided by OWID CO2 from the same fuel (CO2 proxies combustion volume; the ratio moves only with sulphur content and abatement). Process SO2 = smelting and refining."+NOTE_IV)
# ---- T3 Gelbach: Panel A OLS, Panel B 2SLS (mediator auxiliaries estimated by 2SLS with the same instrument) ----
groups={"Composition (manuf., services, agric. \\% GDP)":["manuf_sh","serv_sh","agr_sh"],"Openness (trade, FDI \\% GDP)":["trade_gdp_wdi","fdi_in_gdp"],"Urbanisation":["urban_sh"]}
meds=sum(groups.values(),[]); Y3=["ln_so2gdp","ln_noxgdp","renew_sh","ln_ci","ln_ei"]
say("\nT3. Gelbach decomposition of the ln GACI coefficient (Panel A OLS, Panel B 2SLS)"); cols=[LAB[y] for y in Y3]; rows_out=[]
def gelbach(y,s,iv=None):
    rhs_b="air + lnpop + lnpc + lnpc2" if not iv else "lnpop + lnpc + lnpc2"
    mb=fe(y,rhs_b,s,iv=iv); mf=fe(y,rhs_b+" + "+" + ".join(meds),s,iv=iv); tb,tf=mb.tidy(),mf.tidy()
    bb,bf=tb.loc["air","Estimate"],tf.loc["air","Estimate"]; out={"Base coefficient":f"{bb:.3f} ({tb.loc['air','Std. Error']:.3f})","Full coefficient":f"{bf:.3f} ({tf.loc['air','Std. Error']:.3f})","Explained (base $-$ full)":f"{bb-bf:+.3f}"}
    tot=0
    for gn,vs in groups.items():
        dsum=0
        for v in vs:
            ta=(pf.feols(f"{v} ~ lnpop + lnpc + lnpc2 | c + y | air ~ {iv}",data=s) if iv else pf.feols(f"{v} ~ air + lnpop + lnpc + lnpc2 | c + y",data=s)).tidy()
            dsum+=ta.loc["air","Estimate"]*tf.loc[v,"Estimate"]
        tot+=dsum; out[f"\\quad {gn}"]=f"{dsum:+.3f} ({100*dsum/bb:+.0f}\\%)"
    out["Observations"]=f"{mf._N:,}"; return out,bb-bf,tot
matA={}; matB={}
for y in Y3:
    s=d.dropna(subset=[y,"air","lnpop","lnpc"]+meds)
    matA[y],ex,tot=gelbach(y,s); assert abs(ex-tot)<1e-6, (y,ex,tot)
    matB[y],exB,totB=gelbach(y,s,iv="feyrer_int"); print(f"   IV identity check {y}: explained {exB:+.4f} vs sum of parts {totB:+.4f}")
rws=list(matA[Y3[0]].keys()); lines=[["__PANEL__Panel A: OLS, country and year FE",[""]*len(cols)]]+[[r,[matA[y][r] for y in Y3]] for r in rws]+[["__PANEL__Panel B: 2SLS, ln GACI instrumented by air market access (auxiliary regressions also 2SLS)",[""]*len(cols)]]+[[r,[matB[y][r] for y in Y3]] for r in rws]
tex=["\\begin{table}[htbp]\\centering\\small","\\caption{Channels: Gelbach (2016) decomposition of the ln GACI coefficient}\\label{tab:T3}","\\begin{tabular}{l"+"c"*len(Y3)+"}","\\toprule"," & "+" & ".join(cols)+" \\\\","\\midrule"]
for lab,vals in lines:
    if lab.startswith("__PANEL__"): tex.append("\\midrule"); tex.append(f"\\multicolumn{{{len(cols)+1}}}{{l}}{{\\textit{{{lab[9:]}}}}} \\\\"); say(f"--- {lab[9:]} ---"); continue
    if lab=="Observations": tex.append("\\midrule")
    tex.append(f"{lab} & "+" & ".join(vals)+" \\\\"); say(f"{lab.replace(chr(92)+'quad ','  ').replace(chr(92),''):50s}"+"".join(f"{v.replace(chr(92),''):>22s}" for v in vals))
NOTE3=NOTE_BASE+" Income is in the base specification; the decomposition allocates the change in the ln GACI coefficient to mediator groups exactly (Gelbach 2016). In Panel B the base and full models and the mediator auxiliary regressions are all 2SLS with air market access as the instrument, so the identity holds for the IV coefficient as well. Sample restricted to country-years with all mediators."
tex+=["\\bottomrule","\\end{tabular}","\\begin{minipage}{0.95\\textwidth}\\footnotesize "+NOTE3+"\\end{minipage}","\\end{table}"]
(T/"T3.tex").write_text("\n".join(tex))
TABLES.append({"name":"T3","title":"Channels: Gelbach (2016) decomposition of the ln GACI coefficient","cols":cols,"rows":[[lab if lab.startswith("__PANEL__") else lab.replace("\\quad ","    "),vals] for lab,vals in lines],"note":NOTE3})
# ---- T4 heterogeneity: Panel A OLS (interaction + terciles), Panel B split-sample IV (goods vs service economies, terciles) ----
Y4=["ln_so2gdp","ln_noxgdp","renew_sh","ln_ci"]; msA=[]; exA=[]; exB=[]
for y in Y4:
    s=d.dropna(subset=[y,"air","lnpop","lnpc","merch96"]); msA.append(fe(y,"air + air_goods + lnpop + lnpc + lnpc2",s))
for ter in ["low","mid","high"]:
    rA=[]
    for y in Y4:
        s=d[d.inc_ter==ter].dropna(subset=[y,"air","lnpop","lnpc"]); cA=cell(fe(y,BASE,s),"air"); rA.append(f"{cA[0]} {cA[1]}")
    exA.append((f"ln GACI, {ter}-income tercile (separate reg.)",rA))
msB=[]  # Panel B: goods-economy subsample IV as the model row; other subsamples as extra rows
for y in Y4:
    s=d[(d.goods_econ==1)].dropna(subset=[y,"air","lnpop","lnpc","merch96"]); msB.append(fe(y,"lnpop + lnpc + lnpc2",s,iv="feyrer_int"))
rF=[]; rS=[]
for y in Y4:
    s=d[(d.goods_econ==1)].dropna(subset=[y,"air","lnpop","lnpc","merch96"]); rF.append(f"{fsF(s):.1f}")
    s2=d[(d.goods_econ==0)].dropna(subset=[y,"air","lnpop","lnpc","merch96"]); cB=cell(fe(y,"lnpop + lnpc + lnpc2",s2,iv="feyrer_int"),"air"); rS.append(f"{cB[0]} {cB[1]}  [F {fsF(s2):.1f}]")
exB.append(("First-stage F, goods economies",rF)); exB.append(("ln GACI, service economies (separate IV)",rS))
# tercile-level IV omitted: first-stage F < 1 in the low and mid terciles (reported in _run_log)
LAB["air_goodsIV"]="ln GACI, goods economies"
table("T4","Where does air connectivity clean? Goods-trading economies and income groups",[LAB[y] for y in Y4],panels=[("Panel A: OLS, country and year FE",msA,["air","air_goods"],exA),("Panel B: 2SLS by subsample, ln GACI instrumented by air market access (model row = goods economies)",msB,["air"],exB)],note=NOTE_BASE+" Goods economy = merchandise trade share of GDP above the 1996 cross-country median. Tercile rows: ln GACI coefficient from separate regressions by 1996 income tercile. Panel B runs the IV separately in goods and service economies; bracketed F is the first-stage F of that subsample. Tercile-level IV is not reported because the instrument has no first-stage power within the low- and mid-income terciles (F below 1)."+NOTE_IV)
# ---- T5 IV ----
Y5=["ln_so2gdp","ln_noxgdp","renew_sh","ln_ci"]; cols=[]; ms=[]; ex_rows={"Sargan J p-value":[],"First-stage F (clustered)":[]}
for y in Y5:
    s=d.dropna(subset=[y,"air","lnpop","lnpc","tourism_int","feyrer_int"]).copy()
    for lab,iv in [("Feyrer","feyrer_int"),("both","tourism_int + feyrer_int")]:
        m=fe(y,"lnpop + lnpc + lnpc2",s,iv=iv); ms.append(m); cols.append(f"{LAB[y]}: {lab}")
        fs=pf.feols(f"air ~ {iv} + lnpop + lnpc + lnpc2 | c + y",data=s,vcov={"CRV1":"c"}); ks=[k for k in fs.tidy().index if k in ("tourism_int","feyrer_int")]
        b=fs.coef()[ks].values; V=fs._vcov[[list(fs.coef().index).index(k) for k in ks]][:,[list(fs.coef().index).index(k) for k in ks]]; F=float(b@np.linalg.solve(V,b))/len(ks); ex_rows["First-stage F (clustered)"].append(f"{F:.1f}")
        if lab=="both":
            mr=pf.feols(f"{y} ~ lnpop + lnpc + lnpc2 | c + y | air ~ {iv}",data=s,fixef_rm="none"); s2=s.copy(); s2["u2"]=mr.resid(); s2=s2.dropna(subset=["u2"]); mj=pf.feols("u2 ~ tourism_int + feyrer_int + lnpop + lnpc + lnpc2 | c + y",data=s2); ex_rows["Sargan J p-value"].append(f"{1-chi2.cdf(mj._N*mj._r2_within,1):.3f}")
        else: ex_rows["Sargan J p-value"].append("")
table("T5","Instrumental-variable diagnostics: single-instrument vs over-identified estimates",cols,["air"],ms,extra=[(k,v) for k,v in ex_rows.items()],note=NOTE_BASE+" ln GACI instrumented by UNESCO natural/mixed heritage sites $\\times$ world tourist arrivals (tourism) and Feyrer-type air market access (Feyrer), as in the GACI trade paper. The tourism instrument alone has no first-stage power in the unified sample (clustered F $<$ 1) and is reported only inside the over-identified model. Sargan J from the over-identified model.")
# ---- A1 robustness ----
for y,nm in [("ln_so2gdp","A1a"),("ln_ci","A1b")]:
    cols=[]; ms=[]
    s=d.dropna(subset=[y,"air","lnpop","lnpc"]); s_kl=s.dropna(subset=["lnkl","trade_share"]); s_sea=s.dropna(subset=["ln_sea_ma"]); s_l=d[d.y>=2006].dropna(subset=[y,"air","lnpop","lnpc","ln_lsci"])
    for lab,m in [("base",fe(y,BASE,s)),("+K/L, trade",fe(y,BASE+" + lnkl + lnkl2 + trade_share",s_kl)),("+sea MA",fe(y,BASE+" + ln_sea_ma",s_sea)),("+LSCI 06-",fe(y,BASE+" + ln_lsci",s_l)),("region$\\times$yr",fe(y,BASE,s,fe="c + ry")),("tercile$\\times$yr",fe(y,BASE,s,fe="c + ty")),("1996-2009",fe(y,BASE,s[s.y<=2009])),("2010-2023",fe(y,BASE,s[s.y>=2010]))]:
        ms.append(m); cols.append(lab)
    table(nm,f"Robustness of the ln GACI coefficient: {LAB[y]}",cols,["air"],ms,note=NOTE_BASE+" K/L from PWT 11 (rnna/emp). Sea MA = geography-based sea market access; LSCI = UNCTAD liner shipping connectivity (2006--). Region$\\times$year and income-tercile$\\times$year replace year effects.")
# ---- A2 alternative aggregates ----
d["g_cwm"]=d.g_cwm0; d["g_mean"]=d.g_mean0; cols=[]; ms=[]
for y in ["ln_so2gdp","ln_ci"]:
    for lab,x in [("ln cwm","air"),("cwm level","g_cwm"),("mean level","g_mean")]:
        s=d.dropna(subset=[y,x,"lnpop","lnpc"]); m=pf.feols(f"{y} ~ {x} + lnpop + lnpc + lnpc2 | c + y",data=s,vcov={"CRV1":"c"}); ms.append(m); cols.append(f"{LAB[y]}: {lab}")
say("\nA2. Alternative GACI aggregates (coefficient on the GACI variable)"); vals=[]
for m,c_ in zip(ms,cols):
    k=[i for i in m.tidy().index if i in ("air","g_cwm","g_mean")][0]; cc=cell(m,k); vals.append(f"{cc[0]} {cc[1]}"); say(f"  {c_:28s} {cc[0]} {cc[1]}  N={m._N}")
tex=["\\begin{table}[htbp]\\centering\\small","\\caption{Alternative country aggregates of airport GACI}\\label{tab:A2}","\\begin{tabular}{l"+"c"*len(cols)+"}","\\toprule"," & "+" & ".join(cols)+" \\\\","\\midrule","GACI aggregate & "+" & ".join(vals)+" \\\\","Observations & "+" & ".join(f"{m._N:,}" for m in ms)+" \\\\","\\bottomrule","\\end{tabular}","\\begin{minipage}{0.95\\textwidth}\\footnotesize "+NOTE_BASE+"\\end{minipage}","\\end{table}"]
(T/"A2.tex").write_text("\n".join(tex))
TABLES.append({"name":"A2","title":"Alternative country aggregates of airport GACI","cols":cols,"rows":[["GACI aggregate",vals],["Observations",[f"{m._N:,}" for m in ms]]],"note":NOTE_BASE})
import json; json.dump(TABLES, open(T/"_tables.json","w"), indent=1)
pd.DataFrame(coefs).to_csv(T/"_coefs.csv",index=False); (T/"_all_tables.txt").write_text("\n".join(txt)); print("\nwritten", sorted(p.name for p in T.iterdir()))
