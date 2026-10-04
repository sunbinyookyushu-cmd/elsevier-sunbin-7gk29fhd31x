"""Ingest CEDS v_2025_03_18 SO2 (user upload): by country, by country x fuel. kt -> tonnes; ISO3 upper; 1990-2023.
Output: so2_ceds2025_country_year.csv ; comparison with the OWID mirror of CEDS v2022 on 1996-2019."""
import pandas as pd, numpy as np, pathlib
here=pathlib.Path(__file__).resolve().parent; E=here/"data_external/ceds_2025"
def long(fn,key):
    f=pd.read_csv(fn); yc=[c for c in f.columns if c.startswith("X")]
    l=f.melt(id_vars=["country",key] if key else ["country"],value_vars=yc,var_name="y",value_name="kt"); l["y"]=l.y.str[1:].astype(int); l["c"]=l.country.str.upper(); return l[l.y>=1990]
tot=long(next(E.glob("*by_country_v_2025*.csv")),None).rename(columns={"kt":"so2_kt_2025"})[["c","y","so2_kt_2025"]]
fuel=long(next(E.glob("*by_country_fuel_v_2025*.csv")),"fuel")
w=fuel.pivot_table(index=["c","y"],columns="fuel",values="kt",aggfunc="sum").reset_index()
w.columns=["c","y"]+[f"{x}_so2_kt25" for x in w.columns[2:]]
w["coal_so2_kt25"]=w[["hard_coal_so2_kt25","brown_coal_so2_kt25","coal_coke_so2_kt25"]].sum(axis=1); w["oil_so2_kt25"]=w[["heavy_oil_so2_kt25","light_oil_so2_kt25","diesel_oil_so2_kt25"]].sum(axis=1)
w["fuelsum_kt25"]=w[[c for c in w.columns if c.endswith("_so2_kt25") and not c.startswith(("coal_","oil_"))]].sum(axis=1)
m=tot.merge(w,on=["c","y"],how="outer")
print("countries",m.c.nunique(),"years",m.y.min(),"-",m.y.max()); print("total vs sum of fuels: max |diff| =",float((m.so2_kt_2025-m.fuelsum_kt25).abs().max()),"kt")
m["so2_total_2025"]=m.so2_kt_2025*1e3   # tonnes, same unit as OWID mirror
m.to_csv(here/"so2_ceds2025_country_year.csv",index=False)
# ---- compare with v2022 mirror ----
old=pd.read_csv(here/"panel_v4.csv")[["c","y","so2_total","coal_so2","oil_so2","process_so2","in_unified"]]
cmp=old.merge(m,on=["c","y"],how="inner").dropna(subset=["so2_total","so2_total_2025"]); cmp=cmp[cmp.so2_total>0]
cmp["dl"]=np.log(cmp.so2_total_2025)-np.log(cmp.so2_total)
print("\noverlap 1996-2019: N",len(cmp),"countries",cmp.c.nunique())
print("log(v2025/v2022): mean %.3f sd %.3f; |dl|>0.1 share %.2f; |dl|>0.5 share %.3f"%(cmp.dl.mean(),cmp.dl.std(),(cmp.dl.abs()>0.1).mean(),(cmp.dl.abs()>0.5).mean()))
print("by year (mean dl):"); print(cmp.groupby("y").dl.mean().round(3).to_string())
print("\nlargest revisions (country mean dl):"); print(cmp.groupby("c").dl.mean().sort_values().round(2).head(8).to_string()); print(cmp.groupby("c").dl.mean().sort_values().round(2).tail(8).to_string())
big=["CHN","IND","USA","RUS","DEU","TUR","KOR","IRN"]; print("\nkey countries, v2022 vs v2025 (kt), 2010 and 2019:")
for c in big:
    r=cmp[(cmp.c==c)&(cmp.y.isin([2010,2019]))]; print(c, [(int(y),round(a/1e3),round(b)) for y,a,b in zip(r.y,r.so2_total,r.so2_kt_2025)])
# ---- world totals 2019-2023 in v2025 ----
print("\nv2025 world (sum of countries) SO2 kt by year 2015-2023:"); print(m.groupby("y").so2_kt_2025.sum().loc[2015:2023].round(0).to_string())
