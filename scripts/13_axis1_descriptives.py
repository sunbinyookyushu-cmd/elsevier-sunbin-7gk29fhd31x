"""Section 2 + axis-1 OLS/FE pieces that run on current data.
 (a) EDGAR validation table (international departures CO2 vs EDGAR international aviation)
 (b) Li et al. Table 5 analogue: residualised ln CO2, 5 years before / after each tax introduction, treated vs control
 (c) Axis 1 OLS/FE: ln CO2 on ln GACI (country-year, cap-weighted mean; airport-year), and by GACI component
Outputs: output/tab_edgar_validation.csv, output/tab_before_after.csv, output/tab_axis1_ols.txt
"""
import pandas as pd, numpy as np, pathlib, pyfixest as pf, warnings
warnings.filterwarnings("ignore")
root = pathlib.Path(__file__).resolve().parents[1]
p = pd.read_csv(root/"data/processed/airport_panel_co2.csv").dropna(subset=["iso_country","co2_t"])
p = p[~((p.Year==2024)&(p.n_months<12))].rename(columns={"Airport":"airport","Year":"year","Region":"region","TotalCapacity":"seats"})

# (a) EDGAR validation
e = pd.read_csv(root/"data/processed/edgar_intl_aviation_intensity.csv").set_index("year")
v = pd.DataFrame({"ours_intl_dep_Mt": p.groupby("year").co2_intl_t.sum()/1e6, "ours_total_dep_Mt": p.groupby("year").co2_t.sum()/1e6, "edgar_intl_Mt": e.intl_aviation_ghg_mt})
v["ratio_intl"] = v.ours_intl_dep_Mt/v.edgar_intl_Mt
v.round(2).to_csv(root/"output/tab_edgar_validation.csv")
print("(a) ours/EDGAR intl ratio: min %.2f median %.2f max %.2f ; corr(ln) = %.3f" % (v.ratio_intl.min(), v.ratio_intl.median(), v.ratio_intl.max(), np.corrcoef(np.log(v.dropna().ours_intl_dep_Mt), np.log(v.dropna().edgar_intl_Mt))[0,1]))

# (b) before/after (Li Table 5): residualise ln CO2 on airport FE + region x year FE, compare +-5 years around first tax
tax = pd.read_csv(root/"data/processed/aviation_taxes_master.csv", dtype=str, keep_default_na=False)
first = {"NL":2008,"IE":2009,"DE":2011,"AT":2011,"NO":2016,"SE":2018,"PT":2021,"BE":2022}
eu = p[p.lat.between(30,72)&p.lon.between(-30,60)].copy(); eu["ln_co2"]=np.log(eu.co2_t.where(eu.co2_t>0)); eu=eu.dropna(subset=["ln_co2"])
eu["ry"]=eu.region+"_"+eu.year.astype(str)
m0 = pf.feols("ln_co2 ~ 1 | airport + ry", data=eu, fixef_rm="none"); eu["r"]=np.asarray(m0.resid())
never = eu[~eu.iso_country.isin(list(first)+["GB","FR","DK"])]
rows=[]
for c,y0 in first.items():
    tr = eu[eu.iso_country==c]
    for grp,d in (("treated",tr),("control",never)):
        b = d[(d.year>=y0-5)&(d.year<y0)].r.mean(); a = d[(d.year>=y0)&(d.year<y0+5)].r.mean()
        rows.append({"episode":f"{c} {y0}","group":grp,"before":b,"after":a,"diff":a-b})
ba = pd.DataFrame(rows)
dd = ba.pivot(index="episode",columns="group",values="diff"); dd["diff_in_diff"]=dd.treated-dd.control
dd.round(3).to_csv(root/"output/tab_before_after.csv"); print("(b) residualised ln CO2, +-5y, diff-in-diff by episode:\n", dd.round(3).to_string())

# (c) axis 1 OLS/FE elasticities
p["ln_co2"]=np.log(p.co2_t.where(p.co2_t>0)); p["ln_gaci"]=np.log(p.GACI); p["ln_deg"]=np.log(p.Degree)
p["ln_betw"]=np.log(p.NorBetweenness.where(p.NorBetweenness>0)); p["ln_eig"]=np.log(p.Eigen.where(p.Eigen>0)); p["ln_close"]=np.log(p.NorClose)
p["ry"]=p.region+"_"+p.year.astype(str)
out=[]
def rec(label, m, var): t=m.tidy().loc[var]; out.append(f"{label:70s} b={t['Estimate']:+.3f} se={t['Std. Error']:.3f} N={m._N}")
a = p.dropna(subset=["ln_co2","ln_gaci"])
rec("airport: ln CO2 ~ ln GACI | airport + region x year", pf.feols("ln_co2 ~ ln_gaci | airport + ry", a, vcov={"CRV1":"iso_country"}), "ln_gaci")
rec("airport: ln CO2 ~ ln GACI | airport + country x year", pf.feols("ln_co2 ~ ln_gaci | airport + iso_country^year", a, vcov={"CRV1":"iso_country"}), "ln_gaci")
for v in ["ln_deg","ln_betw","ln_eig","ln_close"]:
    d=a.dropna(subset=[v]); rec(f"airport: ln CO2 ~ {v} | airport + country x year", pf.feols(f"ln_co2 ~ {v} | airport + iso_country^year", d, vcov={"CRV1":"iso_country"}), v)
m = pf.feols("ln_co2 ~ ln_deg + ln_betw + ln_eig + ln_close | airport + iso_country^year", a.dropna(subset=["ln_betw","ln_eig"]), vcov={"CRV1":"iso_country"})
out.append("airport, all components jointly:\n"+m.tidy()[["Estimate","Std. Error"]].round(3).to_string())
# country level: cap-weighted mean GACI (trade paper headline), sum, max
c = p.groupby(["iso_country","year"]).apply(lambda d: pd.Series({"co2":d.co2_t.sum(),"co2_intl":d.co2_intl_t.sum(),"gaci_cwm":np.average(d.GACI,weights=d.seats),"gaci_sum":d.GACI.sum(),"gaci_max":d.GACI.max(),"seats":d.seats.sum()})).reset_index()
c["ln_co2"]=np.log(c.co2.where(c.co2>0)); c["ln_co2_intl"]=np.log(c.co2_intl.where(c.co2_intl>0))
for g in ["gaci_cwm","gaci_sum","gaci_max"]:
    c[f"ln_{g}"]=np.log(c[g]); d=c.dropna(subset=["ln_co2",f"ln_{g}"])
    rec(f"country: ln CO2 ~ ln {g} | country + year", pf.feols(f"ln_co2 ~ ln_{g} | iso_country + year", d, vcov={"CRV1":"iso_country"}), f"ln_{g}")
d=c.dropna(subset=["ln_co2_intl","ln_gaci_cwm"]); rec("country: ln CO2 intl ~ ln gaci_cwm | country + year", pf.feols("ln_co2_intl ~ ln_gaci_cwm | iso_country + year", d, vcov={"CRV1":"iso_country"}), "ln_gaci_cwm")
c.to_csv(root/"data/processed/country_panel_co2_gaci.csv", index=False)
txt="\n".join(out); open(root/"output/tab_axis1_ols.txt","w").write(txt); print("(c)\n"+txt)
