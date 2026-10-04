"""Figures for the coauthor document: GACI explained + the main result visually.
 fig2: ln GACI_cwm over time for six countries (relative, within-year standardised index)
 fig3: binned scatter (FWL residuals) of ln SO2/GDP and ln SO2 per oil CO2 on ln GACI, unified sample
 fig4: schematic of scale / composition / technique and which table tests which"""
import pandas as pd, numpy as np, pyfixest as pf, warnings, pathlib, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
warnings.filterwarnings("ignore"); here=pathlib.Path(__file__).resolve().parent; F=here/"figures"
plt.rcParams.update({"font.family":"DejaVu Serif","font.size":10,"axes.spines.top":False,"axes.spines.right":False,"axes.linewidth":0.8,"axes.edgecolor":"#52514e","xtick.color":"#52514e","ytick.color":"#52514e","axes.labelcolor":"#0b0b0b","axes.grid":True,"grid.color":"#e6e5e0","grid.linewidth":0.6})
PAL=["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#4a3aa7"]
d=pd.read_csv(here/"panel_v4.csv")
# ---------- fig2 ----------
sel=[("CHN","China"),("ARE","UAE"),("TUR","Türkiye"),("ETH","Ethiopia"),("DEU","Germany"),("USA","United States")]
fig,ax=plt.subplots(figsize=(7.2,3.9),dpi=200)
for (c,lab),col in zip(sel,PAL):
    s=d[(d.c==c)&(d.y<=2019)].sort_values("y"); ax.plot(s.y,s.air,color=col,lw=2,label=lab); ax.text(s.y.iloc[-1]+0.3,s.air.iloc[-1],lab,color="#0b0b0b",fontsize=9,va="center")
ax.set_xlim(1996,2023); ax.set_xlabel("Year"); ax.set_ylabel("ln GACI (seat-weighted country mean)"); ax.set_title("Country air connectivity is a relative, within-year position",loc="left",fontsize=11,color="#0b0b0b")
ax.legend(frameon=False,fontsize=7.5,ncol=6,loc="upper left",bbox_to_anchor=(0,-0.16),handlelength=1.5); ax.grid(axis="x",visible=False); fig.tight_layout(); fig.savefig(F/"fig2_gaci_countries.png"); plt.close(fig)
# ---------- fig3 ----------
d=d[d.in_unified==1].copy()
fig,axes=plt.subplots(1,2,figsize=(7.6,3.6),dpi=200)
for ax,(y,title) in zip(axes,[("ln_so2gdp","(a) ln SO2 / GDP"),("ln_so2co2","(b) ln SO2 / CO2 (sulphur intensity of carbon)")]):
    s=d.dropna(subset=[y]).copy()
    ry=pf.feols(f"{y} ~ lnpop + lnpc + lnpc2 | c + y",data=s,fixef_rm="none").resid(); rx=pf.feols("air ~ lnpop + lnpc + lnpc2 | c + y",data=s,fixef_rm="none").resid()
    m=pf.feols(f"{y} ~ air + lnpop + lnpc + lnpc2 | c + y",data=s,vcov={"CRV1":"c"}).tidy(); b,se=m.loc["air","Estimate"],m.loc["air","Std. Error"]
    q=pd.qcut(rx,25,labels=False,duplicates="drop"); bx=pd.Series(rx).groupby(q).mean(); by=pd.Series(ry).groupby(q).mean()
    ax.scatter(bx,by,s=28,color=PAL[0],edgecolor="white",linewidth=0.8,zorder=3); xs=np.linspace(rx.min(),rx.max(),10); ax.plot(xs,b*xs,color=PAL[1],lw=2)
    ax.set_title(title,loc="left",fontsize=10,color="#0b0b0b"); ax.set_xlabel("ln GACI residual (country, year FE; controls)"); ax.set_ylabel("outcome residual")
    ax.text(0.03,0.06,f"slope = {b:.2f} (SE {se:.2f})\nN = {len(s):,}, {s.c.nunique()} countries",transform=ax.transAxes,fontsize=8.5,color="#52514e")
fig.suptitle("Within-country relation between air connectivity and SO2, unified sample, 173 countries 1996–2019 (25 bins)",x=0.01,ha="left",fontsize=10.5,color="#0b0b0b"); fig.tight_layout(); fig.savefig(F/"fig3_binscatter_so2.png"); plt.close(fig)
# ---------- fig4 schematic ----------
fig,ax=plt.subplots(figsize=(10.5,4.2),dpi=200); ax.axis("off"); ax.set_xlim(0,13.6); ax.set_ylim(0,6)
def box(x,y,w,h,text,fc="#f3f2ee",ec="#52514e",fs=9,bold=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.12",fc=fc,ec=ec,lw=0.9)); ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,color="#0b0b0b",fontweight="bold" if bold else "normal",linespacing=1.3)
def arrow(x0,y0,x1,y1,col="#52514e"): ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle="-|>",mutation_scale=12,lw=1.1,color=col))
box(0.2,2.3,2.3,1.4,"Air connectivity\n(ln GACI)",fc="#e3eefb",ec=PAL[0],bold=True,fs=10)
box(3.4,4.3,3.0,1.2,"Scale\nIs more fuel burned?",fc="#fbeae3",ec=PAL[1]); box(3.4,2.4,3.0,1.2,"Composition\nDo dirtier or cleaner\nindustries grow?",fc="#fbeae3",ec=PAL[1]); box(3.4,0.5,3.0,1.2,"Technique\nLess SO2 per unit of fuel?",fc="#e2f5ee",ec=PAL[2],bold=True)
for yy in (4.9,3.0,1.1): arrow(2.5,3.0,3.4,yy)
box(7.0,4.3,6.4,1.2,"Table 1b/2: energy/GDP −0.19 n.s., coal use +0.25 n.s.\n→ no scale effect",fs=8.5); box(7.0,2.4,6.4,1.2,"Table 3: industry shares explain < 10% of the coefficient\nTable 2: process SO2 (smelters) unchanged\n→ no composition effect",fs=8); box(7.0,0.5,6.4,1.2,"Table 1b: SO2/CO2 −0.82*** carries 80% of SO2/GDP −1.02***\nTable 2: SO2 per unit oil −0.9**, per coal CO2 −1.2***\n→ technique effect",fs=8,fc="#e2f5ee",ec=PAL[2])
for yy in (4.9,3.0,1.1): arrow(6.4,yy,7.0,yy)
ax.text(0.2,5.7,"How the tables map onto the scale–composition–technique decomposition (Antweiler, Copeland & Taylor 2001)",fontsize=10.5,color="#0b0b0b",fontweight="bold")
ax.text(0.2,0.05,"Table 4 adds where: the effect appears in goods-producing economies, not in service economies.   Table 5: IV (Feyrer air market access) confirms the sign.",fontsize=8.5,color="#52514e")
fig.savefig(F/"fig4_mechanism_map.png",bbox_inches="tight"); plt.close(fig)
print("figures written:", sorted(p.name for p in F.iterdir()))
