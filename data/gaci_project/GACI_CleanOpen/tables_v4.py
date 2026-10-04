"""v4 table set on panel_v4.csv (single-source denominators; exact identities).  Base spec:
   y ~ ln GACI + ln pop + ln pc + (ln pc)^2 | country + year, SE clustered by country; Panel B = 2SLS with Feyrer air market access.
T1 main | T1b identity decompositions (SO2/GDP = E/GDP x CO2/E x SO2/CO2 ; Kaya) | T2 technique (emission factors incl. per unit fuel consumption)
T3 Gelbach A/B | T4 heterogeneity A/B | T5 IV diagnostics (reduced form, measurement-error IV, over-id) | A1a/A1b robustness incl. region definitions and 2023 extension | A2 aggregates | A3 IV dropping regions
Outputs: tables/*.tex, tables/_all_tables.txt, tables/_tables.json, tables/_coefs.csv"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib, json; warnings.filterwarnings("ignore")
from scipy.stats import chi2
here=pathlib.Path(__file__).resolve().parent; T=here/"tables"; T.mkdir(exist_ok=True)
D=pd.read_csv(here/"panel_v4.csv"); d=D[D.in_unified==1].copy()
print("UNIFIED v4:", len(d), d.c.nunique(), d.y.min(), d.y.max())
d["ty"]=d.inc_ter+"_"+d.y.astype(str); d["ry"]=d.region+"_"+d.y.astype(str); d["cy"]=d.continent.astype(str)+"_"+d.y.astype(str); d["sy"]=d.subregion.astype(str)+"_"+d.y.astype(str); d["trend"]=d.y-1996
BASE="air + lnpop + lnpc + lnpc2"; XIV="lnpop + lnpc + lnpc2"
LAB={"ln_so2gdp":"ln SO2/GDP","ln_so2pc":"ln SO2 pc","ln_noxgdp":"ln NOx/GDP","renew_sh":"Renewable share (pp)","ln_ci":"ln CO2/GDP","ln_co2pc":"ln CO2 pc","ln_ei":"ln energy/GDP","ln_ce":"ln CO2/energy","ln_so2co2":"ln SO2/CO2","ln_noxco2":"ln NOx/CO2","ln_co2":"ln CO2","ln_so2":"ln SO2",
     "ln_coal_cons":"ln coal use (TWh)","ln_so2_coal_cons":"ln SO2/coal use","ln_so2_oil_cons":"ln SO2/oil use","ln_so2_coal_ef":"ln SO2/coal CO2","ln_so2_oil_ef":"ln SO2/oil CO2","ln_so2_fossil_ef":"ln SO2/fossil CO2","ln_so2_process":"ln process SO2","so2_coal_sh":"Coal share of SO2",
     "air":"ln GACI","lnpc":"ln GDP pc","lnpc2":"(ln GDP pc)$^2$","lnpop":"ln population","air_goods":"ln GACI $\\times$ goods economy","feyrer_int":"Air market access (reduced form)"}
coefs=[]; txt=[]; TABLES=[]
def say(s=""): print(s); txt.append(s)
def fe(y,rhs,s,fe="c + y",iv=None): return pf.feols(f"{y} ~ {rhs} | {fe}"+(f" | air ~ {iv}" if iv else ""),data=s,vcov={"CRV1":"c"})
def cell(m,k):
    t=m.tidy()
    if k not in t.index: return ("","")
    b,se=t.loc[k,"Estimate"],t.loc[k,"Std. Error"]; z=abs(b/se); st="***" if z>2.576 else "**" if z>1.96 else "*" if z>1.645 else ""
    return (f"{b:.3f}{st}",f"({se:.3f})")
def fsF(s,iv="feyrer_int",rhs=XIV):
    fs=pf.feols(f"air ~ {iv} + {rhs} | c + y",data=s,vcov={"CRV1":"c"}); ks=iv.split(" + "); idx=[list(fs.coef().index).index(k) for k in ks]; b=fs.coef().values[idx]; V=fs._vcov[np.ix_(idx,idx)]; return float(b@np.linalg.solve(V,b))/len(ks)
def table(name,title,cols,panels,note=""):
    lines=[]
    for plab,pms,prows,pextra in panels:
        if plab: lines.append((f"__PANEL__{plab}",[""]*len(cols)))
        for k in prows:
            cs=[cell(m,k) for m in pms]; lines.append((LAB.get(k,k),[c[0] for c in cs])); lines.append(("",[c[1] for c in cs]))
        if pextra: lines+=pextra
        lines.append(("Observations",[f"{m._N:,}" for m in pms]))
    w=max(14,max(len(c) for c in cols)+2); say(f"\n{name}. {title}"); say(" "*28+"".join(f"{c:>{w}s}" for c in cols))
    for lab,vals in lines:
        if lab.startswith("__PANEL__"): say(f"--- {lab[9:]} ---")
        else: say(f"{lab:28s}"+"".join(f"{v:>{w}s}" for v in vals))
    tex=["\\begin{table}[htbp]\\centering\\small",f"\\caption{{{title}}}\\label{{tab:{name}}}","\\begin{tabular}{l"+"c"*len(cols)+"}","\\toprule"," & "+" & ".join(cols)+" \\\\","\\midrule"]
    for lab,vals in lines:
        if lab.startswith("__PANEL__"): tex.append("\\midrule"); tex.append(f"\\multicolumn{{{len(cols)+1}}}{{l}}{{\\textit{{{lab[9:]}}}}} \\\\"); continue
        if lab=="Observations": tex.append("\\midrule")
        tex.append(f"{lab} & "+" & ".join(vals)+" \\\\")
    tex+=["\\bottomrule","\\end{tabular}",f"\\begin{{minipage}}{{0.95\\textwidth}}\\footnotesize {note}\\end{{minipage}}","\\end{table}"]
    (T/f"{name}.tex").write_text("\n".join(tex)); TABLES.append({"name":name,"title":title,"cols":cols,"rows":[[lab,vals] for lab,vals in lines],"note":note})
    for plab,pms,prows,pextra in panels:
        for c_,m in zip(cols,pms):
            t=m.tidy()
            for k in t.index: coefs.append({"table":name,"panel":plab or "A","column":c_,"var":k,"b":t.loc[k,"Estimate"],"se":t.loc[k,"Std. Error"],"n":m._N})
NOTE_BASE="Unified sample: 173 countries, 1996--2019, country-years with all Table 1 outcomes and the instrument observed. All denominators from one source (WDI GDP in constant 2015 US\\$ = GDP per capita $\\times$ population), so log identities hold exactly. Country and year fixed effects; controls ln population, ln GDP per capita and its square. Standard errors clustered by country. *, **, *** : 10, 5, 1\\%."
NOTE_IV=" Panel B instruments ln GACI with Feyrer-type air market access (country geography $\\times$ world air-traffic growth); first-stage F is the cluster-robust F on the excluded instrument."
def AB(ys,extraA=None,extraB_fn=None,sample=None):
    msA=[];msB=[];Fs=[]
    for y in ys:
        s=(sample if sample is not None else d).dropna(subset=[y,"air","lnpop","lnpc","feyrer_int"]); msA.append(fe(y,BASE,s)); msB.append(fe(y,XIV,s,iv="feyrer_int")); Fs.append(f"{fsF(s):.1f}")
    return msA,msB,[("First-stage F (clustered)",Fs)]
sd_w=pf.feols("air ~ 1 | c + y",data=d,fixef_rm="none").resid().std()
# ---------- T1 ----------
Y1=["ln_so2gdp","ln_so2pc","ln_noxgdp","renew_sh","ln_ci","ln_co2pc","ln_ei","ln_ce"]; msA,msB,exB=AB(Y1)
exA=[("1 within-SD effect",[f"{m.tidy().loc['air','Estimate']*sd_w*(100 if y!='renew_sh' else 1):+.1f}{'%' if y!='renew_sh' else 'pp'}" for m,y in zip(msA,Y1)])]
table("T1","Air connectivity and the pollution and carbon intensity of the economy, 1996--2019",[LAB[y] for y in Y1],[("Panel A: OLS, country and year FE",msA,["air","lnpc","lnpc2"],exA),("Panel B: 2SLS, ln GACI instrumented by air market access",msB,["air"],exB)],note=NOTE_BASE+f" Within-country SD of ln GACI = {sd_w:.3f}. Because ln GDP per capita is a regressor, the ln GACI coefficient is identical for the per-GDP and per-capita versions of each outcome (ln X/GDP = ln X/pop $-$ ln GDP/pop)."+NOTE_IV)
# ---------- T1b identity decompositions ----------
Yd=["ln_so2gdp","ln_ei","ln_ce","ln_so2co2","ln_noxgdp","ln_noxco2","ln_co2"]; msA,msB,exB=AB(Yd)
def sums(ms): 
    b=lambda i: ms[i].tidy().loc["air","Estimate"]; return [("Adding-up check",[f"{b(0):+.3f} = {b(1):+.3f} {b(2):+.3f} {b(3):+.3f}" if False else "", "", "", f"sum(2--4) = {b(1)+b(2)+b(3):+.3f}", "", f"sum = {b(1)+b(2)+b(5):+.3f}", f"Kaya: {b(1)+b(2):+.3f}"])]
table("T1b","Identity decompositions: ln SO2/GDP = ln E/GDP + ln CO2/E + ln SO2/CO2, and Kaya",[LAB[y] for y in Yd],[("Panel A: OLS",msA,["air"],sums(msA)),("Panel B: 2SLS",msB,["air"],exB+sums(msB))],note=NOTE_BASE+" Columns 2--4 decompose column 1 exactly (energy intensity, carbon intensity of energy, sulphur intensity of carbon); column 6 decomposes NOx/GDP as cols 2+3+6. Kaya: ln CO2 = ln pop + ln GDP/pop + ln E/GDP + ln CO2/E; with ln pop and ln GDP/pop as controls the ln GACI coefficient on ln CO2 (col 7) equals the sum of cols 2 and 3."+NOTE_IV)
# ---------- T2 technique ----------
Y2=["ln_coal_cons","ln_so2_coal_cons","ln_so2_oil_cons","ln_so2_coal_ef","ln_so2_oil_ef","ln_so2_fossil_ef","ln_so2_process","so2_coal_sh"]; msA,msB,exB=AB(Y2)
table("T2","Technique, not scale: SO2 per unit of fuel burned",[LAB[y] for y in Y2],[("Panel A: OLS, country and year FE",msA,["air"],None),("Panel B: 2SLS",msB,["air"],exB)],note=NOTE_BASE+" SO2 per unit of fuel use: CEDS SO2 from coal (oil) divided by Energy Institute coal (oil) consumption in TWh (77 countries). SO2 per fuel CO2: CEDS SO2 from a fuel divided by OWID CO2 from the same fuel (all countries). Process SO2 = smelting and refining."+NOTE_IV)
# ---------- T3 Gelbach ----------
groups={"Composition (manuf., services, agric. \\% GDP)":["manuf_sh","serv_sh","agr_sh"],"Openness (trade, FDI \\% GDP)":["trade_gdp_wdi","fdi_in_gdp"],"Urbanisation":["urban_sh"]}; meds=sum(groups.values(),[]); Y3=["ln_so2gdp","ln_noxgdp","renew_sh","ln_ci","ln_ei"]
def gelbach(y,s,iv=None):
    rhs_b=BASE if not iv else XIV; mb=fe(y,rhs_b,s,iv=iv); mf=fe(y,rhs_b+" + "+" + ".join(meds),s,iv=iv); tb,tf=mb.tidy(),mf.tidy(); bb,bf=tb.loc["air","Estimate"],tf.loc["air","Estimate"]
    out={"Base coefficient":f"{bb:.3f} ({tb.loc['air','Std. Error']:.3f})","Full coefficient":f"{bf:.3f} ({tf.loc['air','Std. Error']:.3f})","Explained (base $-$ full)":f"{bb-bf:+.3f}"}; tot=0
    for gn,vs in groups.items():
        dsum=sum((pf.feols(f"{v} ~ {XIV} | c + y | air ~ {iv}",data=s) if iv else pf.feols(f"{v} ~ {BASE} | c + y",data=s)).tidy().loc["air","Estimate"]*tf.loc[v,"Estimate"] for v in vs); tot+=dsum; out[f"\\quad {gn}"]=f"{dsum:+.3f} ({100*dsum/bb:+.0f}\\%)"
    assert abs((bb-bf)-tot)<1e-6; out["Observations"]=f"{mf._N:,}"; return out
matA={};matB={}
for y in Y3:
    s=d.dropna(subset=[y,"air","lnpop","lnpc","feyrer_int"]+meds); matA[y]=gelbach(y,s); matB[y]=gelbach(y,s,iv="feyrer_int")
cols=[LAB[y] for y in Y3]; rws=list(matA[Y3[0]].keys())
lines=[["__PANEL__Panel A: OLS, country and year FE",[""]*len(cols)]]+[[r,[matA[y][r] for y in Y3]] for r in rws]+[["__PANEL__Panel B: 2SLS (auxiliary regressions also 2SLS)",[""]*len(cols)]]+[[r,[matB[y][r] for y in Y3]] for r in rws]
say("\nT3. Gelbach decomposition"); 
for lab,vals in lines: say(f"--- {lab[9:]} ---" if lab.startswith("__PANEL__") else f"{lab.replace(chr(92)+'quad ','  ').replace(chr(92),''):50s}"+"".join(f"{v.replace(chr(92),''):>22s}" for v in vals))
NOTE3=NOTE_BASE+" Exact Gelbach (2016) decomposition of the change in the ln GACI coefficient when the mediators are added; in Panel B all regressions are 2SLS with the same instrument so the identity holds for the IV coefficient. Sample restricted to country-years with all mediators."
tex=["\\begin{table}[htbp]\\centering\\small","\\caption{Channels: Gelbach (2016) decomposition of the ln GACI coefficient}\\label{tab:T3}","\\begin{tabular}{l"+"c"*len(cols)+"}","\\toprule"," & "+" & ".join(cols)+" \\\\","\\midrule"]
for lab,vals in lines:
    if lab.startswith("__PANEL__"): tex+=["\\midrule",f"\\multicolumn{{{len(cols)+1}}}{{l}}{{\\textit{{{lab[9:]}}}}} \\\\"]; continue
    if lab=="Observations": tex.append("\\midrule")
    tex.append(f"{lab} & "+" & ".join(vals)+" \\\\")
tex+=["\\bottomrule","\\end{tabular}","\\begin{minipage}{0.95\\textwidth}\\footnotesize "+NOTE3+"\\end{minipage}","\\end{table}"]; (T/"T3.tex").write_text("\n".join(tex))
TABLES.append({"name":"T3","title":"Channels: Gelbach (2016) decomposition of the ln GACI coefficient","cols":cols,"rows":[[lab if lab.startswith("__PANEL__") else lab.replace("\\quad ","    "),vals] for lab,vals in lines],"note":NOTE3})
# ---------- T4 heterogeneity ----------
Y4=["ln_so2gdp","ln_noxgdp","renew_sh","ln_ci"]; msA=[];exA=[];msB=[];exB=[]
for y in Y4:
    s=d.dropna(subset=[y,"air","lnpop","lnpc","merch96"]); msA.append(fe(y,"air + air_goods + lnpop + lnpc + lnpc2",s)); msB.append(fe(y,XIV,s[s.goods_econ==1],iv="feyrer_int"))
for ter in ["low","mid","high"]:
    r=[]
    for y in Y4:
        s=d[d.inc_ter==ter].dropna(subset=[y,"air","lnpop","lnpc"]); c_=cell(fe(y,BASE,s),"air"); r.append(f"{c_[0]} {c_[1]}")
    exA.append((f"ln GACI, {ter}-income tercile (separate reg.)",r))
rF=[];rS=[]
for y in Y4:
    s1=d[d.goods_econ==1].dropna(subset=[y,"air","lnpop","lnpc","merch96"]); rF.append(f"{fsF(s1):.1f}")
    s0=d[d.goods_econ==0].dropna(subset=[y,"air","lnpop","lnpc","merch96"]); c_=cell(fe(y,XIV,s0,iv="feyrer_int"),"air"); rS.append(f"{c_[0]} {c_[1]}  [F {fsF(s0):.1f}]")
exB=[("First-stage F, goods economies",rF),("ln GACI, service economies (separate IV)",rS)]
table("T4","Where does air connectivity clean? Goods-trading economies and income groups",[LAB[y] for y in Y4],[("Panel A: OLS, country and year FE",msA,["air","air_goods"],exA),("Panel B: 2SLS by subsample (model row = goods economies)",msB,["air"],exB)],note=NOTE_BASE+" Goods economy = merchandise trade share of GDP above the 1996 cross-country median. Tercile rows: separate regressions by 1996 income tercile (tercile-level IV not reported: first-stage F below 1 in low and mid terciles)."+NOTE_IV)
# ---------- T5 IV diagnostics: reduced form, ME-IV, over-identification ----------
Y5=["ln_so2gdp","ln_noxgdp","renew_sh","ln_ci"]; cols=[];ms=[];ex={"Sargan J p (both IVs)":[],"First-stage F":[]}
for y in Y5:
    s=d.dropna(subset=[y,"air","lnpop","lnpc","feyrer_int","tourism_int","gaci_mean"]).copy()
    mo=fe(y,BASE,s); mrf=fe(y,"feyrer_int + "+XIV,s); mf=fe(y,XIV,s,iv="feyrer_int"); mme=fe(y,XIV,s,iv="gaci_mean"); mb=fe(y,XIV,s,iv="tourism_int + feyrer_int")
    for lab,m,F in [("OLS",mo,""),("reduced form",mrf,""),("IV: market access",mf,f"{fsF(s):.1f}"),("IV: unweighted GACI mean (ME)",mme,f"{fsF(s,iv='gaci_mean'):.1f}"),("IV: both",mb,f"{fsF(s,iv='tourism_int + feyrer_int'):.1f}")]:
        ms.append(m); cols.append(f"{LAB[y]}: {lab}"); ex["First-stage F"].append(F)
        if lab=="IV: both":
            mr=pf.feols(f"{y} ~ {XIV} | c + y | air ~ tourism_int + feyrer_int",data=s,fixef_rm="none"); s2=s.copy(); s2["u2"]=mr.resid(); s2=s2.dropna(subset=["u2"]); mj=pf.feols(f"u2 ~ tourism_int + feyrer_int + {XIV} | c + y",data=s2); ex["Sargan J p (both IVs)"].append(f"{1-chi2.cdf(mj._N*mj._r2_within,1):.3f}")
        else: ex["Sargan J p (both IVs)"].append("")
table("T5","Instrumental-variable diagnostics",cols,[(None,ms,["air","feyrer_int"],[(k,v) for k,v in ex.items()])],note=NOTE_BASE+" Reduced form regresses the outcome directly on the instrument. The measurement-error IV instruments the seat-weighted ln GACI with the unweighted country mean of airport GACI: a classical-measurement-error correction that uses no exclusion restriction beyond independent measurement error; if the OLS coefficient is attenuated, this estimate should exceed OLS. Sargan J from the over-identified model.")
# ---------- A1 robustness ----------
for y,nm in [("ln_so2gdp","A1a"),("ln_ci","A1b")]:
    cols=[];ms=[]; s=d.dropna(subset=[y,"air","lnpop","lnpc"]); sk=s.dropna(subset=["lnkl"]); ss=s.dropna(subset=["ln_sea_ma"]); sl=s[s.y>=2006].dropna(subset=["ln_lsci"])
    specs=[("base",fe(y,BASE,s)),("+K/L",fe(y,BASE+" + lnkl + lnkl2",sk)),("+sea MA",fe(y,BASE+" + ln_sea_ma",ss)),("+LSCI 06-",fe(y,BASE+" + ln_lsci",sl)),("GACI-region$\\times$yr",fe(y,BASE,s,fe="c + ry")),("continent$\\times$yr",fe(y,BASE,s,fe="c + cy")),("subregion$\\times$yr",fe(y,BASE,s,fe="c + sy")),("region trends",fe(y,BASE+" + i(region, trend)",s)),("tercile$\\times$yr",fe(y,BASE,s,fe="c + ty")),("1996-2009",fe(y,BASE,s[s.y<=2009])),("2010-2019",fe(y,BASE,s[s.y>=2010]))]
    if y=="ln_ci":
        sx=D.dropna(subset=["ln_ci","air","lnpop","lnpc"]); specs.append(("1996-2023 (all)",fe(y,BASE,sx))); specs.append(("2010-2023",fe(y,BASE,sx[sx.y>=2010])))
    for lab,m in specs: ms.append(m); cols.append(lab)
    table(nm,f"Robustness of the ln GACI coefficient: {LAB[y]}",cols,[(None,ms,["air"],None)],note=NOTE_BASE+" K/L from PWT 11. GACI-region = the 7 macro-regions of the GACI panel (AF, AS, EU, LA, ME, NA, SW); continent = 5 UN continents; subregion = 22 UN subregions; region trends = region-specific linear trends. CO2 columns 12--13 extend the sample to 2023 (CEDS ends 2019).")
# ---------- A2 aggregates ----------
cols=[];ms=[]
for y in ["ln_so2gdp","ln_ci"]:
    for lab,x in [("ln cwm","air"),("cwm level","gaci_cwmean"),("mean level","gaci_mean")]:
        s=d.dropna(subset=[y,x,"lnpop","lnpc"]); ms.append(pf.feols(f"{y} ~ {x} + lnpop + lnpc + lnpc2 | c + y",data=s,vcov={"CRV1":"c"})); cols.append(f"{LAB[y]}: {lab}")
vals=[]
for m in ms:
    k=[i for i in m.tidy().index if i in ("air","gaci_cwmean","gaci_mean")][0]; c_=cell(m,k); vals.append(f"{c_[0]} {c_[1]}")
say("\nA2. aggregates: "+" | ".join(f"{c}: {v}" for c,v in zip(cols,vals)))
TABLES.append({"name":"A2","title":"Alternative country aggregates of airport GACI","cols":cols,"rows":[["GACI aggregate",vals],["Observations",[f"{m._N:,}" for m in ms]]],"note":NOTE_BASE})
(T/"A2.tex").write_text("% see _tables.json A2")
# ---------- A3 IV dropping one region at a time ----------
cols=[];ms=[];Fs=[]
for rg in sorted(d.region.dropna().unique()):
    s=d[d.region!=rg].dropna(subset=["ln_so2gdp","air","lnpop","lnpc","feyrer_int"]); ms.append(fe("ln_so2gdp",XIV,s,iv="feyrer_int")); cols.append(f"drop {rg}"); Fs.append(f"{fsF(s):.1f}")
table("A3","IV estimate for ln SO2/GDP dropping one GACI region at a time",cols,[(None,ms,["air"],[("First-stage F",Fs)])],note=NOTE_BASE+NOTE_IV)
pd.DataFrame(coefs).to_csv(T/"_coefs.csv",index=False); (T/"_all_tables.txt").write_text("\n".join(txt)); json.dump(TABLES,open(T/"_tables.json","w"),indent=1); print("\nwritten", sorted(p.name for p in T.iterdir()))
