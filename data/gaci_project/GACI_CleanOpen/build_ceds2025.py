"""Ingest CEDS v_2025_03_18 SO2 and NOx (user upload, kt): totals by country, SO2/NOx by country x fuel. -> ceds2025_country_year.csv (tonnes, ISO3, 1990-2023)"""
import pandas as pd, numpy as np, pathlib
here=pathlib.Path(__file__).resolve().parent; E=here/"data_external/ceds_2025"
def long(fn,key):
    f=pd.read_csv(fn); yc=[c for c in f.columns if c.startswith("X")]
    l=f.melt(id_vars=["country"]+([key] if key else []),value_vars=yc,var_name="y",value_name="kt"); l["y"]=l.y.str[1:].astype(int); l["c"]=l.country.str.upper(); return l[l.y>=1990]
out=None
for sp in ["SO2","NOx"]:
    tot=long(next(E.glob(f"*{sp}_CEDS_estimates_by_country_v_2025*.csv")),None); tot[f"{sp.lower()}_total"]=tot.kt*1e3; tot=tot[["c","y",f"{sp.lower()}_total"]]
    fuel=long(next(E.glob(f"*{sp}_CEDS_estimates_by_country_fuel_v_2025*.csv")),"fuel"); w=fuel.pivot_table(index=["c","y"],columns="fuel",values="kt",aggfunc="sum").reset_index()
    w.columns=["c","y"]+[f"{x}_{sp.lower()}" for x in w.columns[2:]]
    for x in w.columns[2:]: w[x]=w[x]*1e3
    w[f"coal_{sp.lower()}"]=w[[f"hard_coal_{sp.lower()}",f"brown_coal_{sp.lower()}",f"coal_coke_{sp.lower()}"]].sum(axis=1); w[f"oil_{sp.lower()}"]=w[[f"heavy_oil_{sp.lower()}",f"light_oil_{sp.lower()}",f"diesel_oil_{sp.lower()}"]].sum(axis=1)
    m=tot.merge(w,on=["c","y"],how="outer"); out=m if out is None else out.merge(m,on=["c","y"],how="outer")
out["ceds_version"]="v_2025_03_18"
out.to_csv(here/"ceds2025_country_year.csv",index=False); print(out.shape, out.c.nunique(),"countries", out.y.min(),"-",out.y.max()); print(out.columns.tolist())
