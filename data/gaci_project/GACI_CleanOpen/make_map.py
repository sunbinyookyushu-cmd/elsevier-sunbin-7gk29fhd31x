"""Global aggregate exercise + world map.
 (a) change in ln GACI (first to last year in the unified sample, >=15 years apart)
 (b) observed change in ln SO2/GDP over the same window
 Aggregate: counterfactual SO2 had connectivity stayed at its initial level, using the Table 1 elasticity (with 95% band).
Outputs: figures/fig5_map_gaci_so2.png, global_aggregate_so2.csv, global_aggregate_summary.txt"""
import json, pandas as pd, numpy as np, geopandas as gpd, matplotlib, pathlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap
here=pathlib.Path(__file__).resolve().parent; F=here/"figures"
plt.rcParams.update({"font.family":"DejaVu Serif","font.size":10})
d=pd.read_csv(here/"clean_open_panel.csv")
CORE=["air","lnpop","lnpc","ln_so2gdp","ln_noxgdp","renew_sh","ln_ci","ln_ei","ln_ce","tourism_int","feyrer_int"]; d=d.dropna(subset=CORE)
B,SE=-0.935,0.381
g=d.sort_values("y").groupby("c"); first=g.first(); last=g.last(); ok=(last.y-first.y)>=15
ch=pd.DataFrame({"y0":first.y,"y1":last.y,"d_air":last.air-first.air,"d_so2gdp":last.ln_so2gdp-first.ln_so2gdp,"so2_0":first.so2_total,"so2_1":last.so2_total,"reg":last.reg.str[:2]})[ok]
lines=[]
def say(s): print(s); lines.append(s)
for lab,b in [("point",B),("lower (b-1.96se)",B+1.96*SE),("upper (b+1.96se)",B-1.96*SE)]:
    cf=ch.so2_1*np.exp(-b*ch.d_air); av=(cf-ch.so2_1).sum()
    say(f"{lab:18s} elasticity {b:+.3f}: SO2 avoided in final year {av/1e3:,.0f} kt = {100*av/ch.so2_1.sum():.1f}% of final-year SO2 = {100*av/(ch.so2_0.sum()-ch.so2_1.sum()):.1f}% of the observed decline")
say(f"countries {len(ch)}; mean d ln GACI {ch.d_air.mean():+.3f} (sd {ch.d_air.std():.3f}); world SO2 (sample) {ch.so2_0.sum()/1e3:,.0f} -> {ch.so2_1.sum()/1e3:,.0f} kt ({100*(ch.so2_1.sum()/ch.so2_0.sum()-1):+.1f}%)")
ch["impl_pct_so2int"]=100*(np.exp(B*ch.d_air)-1); ch["so2_avoided_kt"]=(ch.so2_1*np.exp(-B*ch.d_air)-ch.so2_1)/1e3
reg=ch.groupby("reg").agg(countries=("d_air","size"),mean_d_lnGACI=("d_air","mean"),implied_pct_SO2_intensity=("impl_pct_so2int","mean"),SO2_avoided_kt=("so2_avoided_kt","sum")).round(2)
say("\nby region:\n"+reg.to_string())
say("\nlargest implied contributions (kt avoided): "+", ".join(f"{c} {v:,.0f}" for c,v in ch.so2_avoided_kt.sort_values(ascending=False).head(8).items()))
ch.round(4).to_csv(here/"global_aggregate_so2.csv"); open(here/"global_aggregate_summary.txt","w").write("\n".join(lines))
# ---- map ----
gj=json.load(open(here.parent/"GACI_CO2/data_external/ne_50m_admin_0.geojson")); w=gpd.GeoDataFrame.from_features(gj["features"]).set_crs(4326)
def iso(r):
    for k in ["ISO_A3","ISO_A3_EH","ADM0_A3"]:
        v=r.get(k)
        if isinstance(v,str) and v not in ("-99",""): return v
w["iso3"]=w.apply(iso,axis=1); w=w[w["NAME"]!="Antarctica"].merge(ch.reset_index().rename(columns={"c":"iso3"}),on="iso3",how="left").to_crs("+proj=robin")
blue_red=LinearSegmentedColormap.from_list("br",["#0d366b","#2a78d6","#9ec5f4","#f0efec","#f3a59a","#e34948","#7a1f1e"])
fig,axes=plt.subplots(2,1,figsize=(9,8.6),dpi=200)
for ax,(col,title,cm,lim,lab) in zip(axes,[("d_air","(a) Change in ln GACI, first to last sample year (1996 → 2019)",blue_red.reversed(),0.6,"Δ ln GACI"),("d_so2gdp","(b) Observed change in ln SO2/GDP over the same window",blue_red,2.0,"Δ ln SO2/GDP")]):
    norm=TwoSlopeNorm(vmin=-lim,vcenter=0,vmax=lim)
    w.plot(column=col,ax=ax,cmap=cm,norm=norm,missing_kwds={"color":"#ededed","edgecolor":"#b3b8bd","linewidth":0.2},edgecolor="#ffffff",linewidth=0.25)
    ax.axis("off"); ax.set_title(title,loc="left",fontsize=10.5,color="#0b0b0b")
    sm=plt.cm.ScalarMappable(cmap=cm,norm=norm); sm.set_array([]); cb=fig.colorbar(sm,ax=ax,orientation="vertical",shrink=0.7,pad=0.01,extend="both"); cb.set_label(lab,fontsize=9); cb.ax.tick_params(labelsize=8)
fig.text(0.01,0.005,"Grey: outside the unified sample. Panel (a): red = became more central in the world air network. Panel (b): blue = SO2 intensity fell. Sample: 141 countries with ≥15 years.",fontsize=8,color="#52514e")
fig.tight_layout(); fig.savefig(F/"fig5_map_gaci_so2.png",bbox_inches="tight"); plt.close(fig); print("map written")
