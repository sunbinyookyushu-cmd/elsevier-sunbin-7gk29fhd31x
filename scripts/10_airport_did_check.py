"""Python replica of stata/03_airport_did.do (pyfixest) — a quick check that the pipeline and data produce
sensible numbers before anyone opens Stata. Headline model:
    y_at = b*Tax_ct + spill*Spill_at + alpha_a + lambda_{region x year} + e,   cluster: country
"""
import pandas as pd, numpy as np, pathlib, pyfixest as pf
root = pathlib.Path(__file__).resolve().parents[1]
g = pd.read_csv(root/"data/processed/gaci_with_country.csv").dropna(subset=["iso_country"])
tax = pd.read_csv(root/"data/processed/aviation_taxes_master.csv", dtype=str, keep_default_na=False)
fx = pd.read_csv(root/"stata/fx_eur.csv")

# ---- country-year tax panel (mirrors 02_build_tax_panel.do) ----
t = tax[tax["class"].isin(["economy","all"]) & (tax.rate!="") & (tax.valid_from!="") & (tax.include_main=="1")].copy()
t["rate"] = pd.to_numeric(t.rate, errors="coerce"); t = t[t.rate>0]  # zero-rated periods (NL Jul-Dec 2009) = not in force
t["vfrom"] = pd.to_datetime(t.valid_from); t["vto"] = pd.to_datetime(t.valid_to.replace("", "2024-12-31"))
t["dkm"] = pd.to_numeric(t.band_upper_km, errors="coerce")
rows = []
for _, r in t.iterrows():
    for y in range(r.vfrom.year, min(r.vto.year, 2024)+1):
        s = max(r.vfrom, pd.Timestamp(y,1,1)); e = min(r.vto, pd.Timestamp(y,12,31))
        months = min(12, (e - s).days/30.44 + 1/30.44)
        if months <= 0: continue
        rows.append({"iso_country": r.country_iso, "year": y, "months": months, "rate": r.rate, "cur": r.currency, "dkm": r.dkm, "band": r.band_id, "instrument": r.instrument})
ty = pd.DataFrame(rows).merge(fx, on=["cur","year"], how="left"); ty["fx"] = ty.fx.fillna(1.0)
ty["rate_eur"] = ty.rate*ty.fx*ty.months/12
dmin = ty.groupby(["iso_country","year"]).dkm.transform("min"); dmax = ty.groupby(["iso_country","year"]).dkm.transform("max")
short = ty[(ty.dkm==dmin)|ty.dkm.isna()].groupby(["iso_country","year"]).rate_eur.sum().rename("tax_short_eur")
longb = ty[(ty.dkm==dmax)|ty.dkm.isna()].groupby(["iso_country","year"]).rate_eur.sum().rename("tax_long_eur")
anym = ty.groupby(["iso_country","year"]).months.max().rename("months_any")
cy = pd.concat([anym, short, longb], axis=1).reset_index()
cy["tax_any"] = (cy.months_any>=6).astype(int)
cy = cy.sort_values(["iso_country","year"])
first = cy[cy.tax_any==1].groupby("iso_country").year.min().rename("first_tax")
print("Tax-years by country:", cy[cy.tax_any==1].groupby("iso_country").year.agg(["min","max","count"]).to_dict("index"))

# ---- airport panel ----
g = g.rename(columns={"Airport":"airport","Year":"year","Region":"region","TotalCapacity":"seats"})
g = g[g.lat.between(30,72) & g.lon.between(-30,60)]
g["nyears"] = g.groupby("airport").year.transform("nunique"); g["maxseats"] = g.groupby("airport").seats.transform("max")
g = g[(g.nyears>=20)&(g.maxseats>=50000)].copy()
g = g.merge(cy[["iso_country","year","tax_any","tax_short_eur"]], on=["iso_country","year"], how="left").fillna({"tax_any":0,"tax_short_eur":0})
g = g.merge(first, on="iso_country", how="left")
# spillover ring 300 km
nd = pd.read_csv(root/"data/processed/airport_nearest_foreign_country_km.csv").rename(columns={"Airport":"airport"})
sp = nd[nd.km<=300].merge(cy[cy.tax_any==1][["iso_country","year"]].rename(columns={"iso_country":"foreign_iso"}), on="foreign_iso")
sp = sp[["airport","year"]].drop_duplicates().assign(spill300=1)
g = g.merge(sp, on=["airport","year"], how="left").fillna({"spill300":0}); g.loc[g.tax_any==1,"spill300"]=0
g["ln_seats"] = np.log(g.seats); g["ln_gaci"] = np.log(g.GACI); g["ln_deg"] = np.log(g.Degree)
g["ry"] = g.region + "_" + g.year.astype(str)
g["et"] = (g.year - g.first_tax).clip(-5, 8)
print(f"sample: {g.airport.nunique()} airports, {len(g)} airport-years, treated airport-years {int(g.tax_any.sum())}, spill {int(g.spill300.sum())}")

# ---- regressions ----
for y in ["ln_seats","ln_gaci","ln_deg"]:
    m1 = pf.feols(f"{y} ~ tax_any + spill300 | airport + ry", data=g, vcov={"CRV1":"iso_country"})
    m2 = pf.feols(f"{y} ~ tax_short_eur + spill300 | airport + ry", data=g, vcov={"CRV1":"iso_country"})
    print(f"\n== {y} ==\n", pf.etable([m1,m2], type="df").to_string())
# event study on ln seats
es = g.copy(); es["et"] = es.et.fillna(-1).astype(int)   # never-treated -> reference bin
m = pf.feols("ln_seats ~ i(et, ref=-1) + spill300 | airport + ry", data=es, vcov={"CRV1":"iso_country"})
print("\n== event study, ln seats ==\n", m.tidy().round(3).to_string())
