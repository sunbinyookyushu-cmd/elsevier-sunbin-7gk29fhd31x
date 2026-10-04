"""v3b: does the air-only result survive income-tercile x year and region x year FE?  (full sample 1996-2023, +lnpop +lnpc)"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib
warnings.filterwarnings("ignore"); here=pathlib.Path(__file__).resolve().parent
d=pd.read_csv(here/"clean_open_panel.csv"); d["region"]=d.reg.str[:2]; d["ty"]=d.inc_ter+"_"+d.y.astype(str); d["ry"]=d.region+"_"+d.y.astype(str)
d["lnpc2"]=d.lnpc**2
f3=lambda t,k: f"{t.loc[k,'Estimate']:+.3f}({t.loc[k,'Std. Error']:.3f})"
def st(t,k):
    z=abs(t.loc[k,'Estimate']/t.loc[k,'Std. Error']); return "***" if z>2.576 else "**" if z>1.96 else "*" if z>1.645 else " "
LAB={"ln_ci":"ln CO2/GDP","ln_ei":"ln energy/GDP","ln_ce":"ln CO2/energy","ln_so2gdp":"ln SO2/GDP","ln_noxgdp":"ln NOx/GDP","renew_sh":"renew pp","ln_co2pc":"ln CO2 pc"}
lines=[]
def say(s): print(s); lines.append(s)
say(f"{'outcome':14s} | {'c+y':>16s} | {'+lnpc^2':>16s} | {'ter x y':>16s} | {'region x y':>16s} | {'ter x y + reg x y':>18s} | {'country trends':>16s}")
for y in LAB:
    s=d.dropna(subset=[y,"air","lnpop","lnpc"]).copy()
    specs=[("air + lnpop + lnpc | c + y",{}),("air + lnpop + lnpc + lnpc2 | c + y",{}),("air + lnpop + lnpc | c + ty",{}),("air + lnpop + lnpc | c + ry",{}),("air + lnpop + lnpc | c + ty + ry",{}),("air + lnpop + lnpc | c[y] + y",{})]
    out=[]
    for fml,_ in specs:
        try: t=pf.feols(f"{y} ~ {fml}", data=s, vcov={"CRV1":"c"}).tidy(); out.append(f3(t,'air')+st(t,'air'))
        except Exception as e: out.append("err")
    say(f"{LAB[y]:14s} | " + " | ".join(f"{o:>16s}" for o in out))
say("\n10-year long differences with region x year FE:")
dd=d.set_index(["c","y"]); cols=["ln_ci","ln_ei","ln_ce","ln_so2gdp","ln_noxgdp","air","lnpop","lnpc"]
ld=(dd[cols]-dd[cols].groupby(level=0).shift(10)).add_prefix("d").reset_index().dropna(); ld["region"]=ld.c.map(d.groupby("c").region.first()); ld["ry"]=ld.region+"_"+ld.y.astype(str)
for y in ["ln_ci","ln_ei","ln_ce","ln_so2gdp","ln_noxgdp"]:
    t1=pf.feols(f"d{y} ~ dair + dlnpop + dlnpc | y", data=ld, vcov={"CRV1":"c"}).tidy(); t2=pf.feols(f"d{y} ~ dair + dlnpop + dlnpc | ry", data=ld, vcov={"CRV1":"c"}).tidy()
    say(f"   {LAB[y]:14s} year FE {f3(t1,'dair')}{st(t1,'dair')}   region x year FE {f3(t2,'dair')}{st(t2,'dair')}")
open(here/"_out_v3b_fe.txt","w").write("\n".join(lines))
