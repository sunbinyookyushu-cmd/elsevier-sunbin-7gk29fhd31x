"""Python replica of stata/03_airport_did.do (pyfixest) — checks that data + pipeline give sensible numbers.

Design (Li, Liu, Purevjav & Yang 2019 JEEM analogue):
  treated  : airports in a country with a ticket tax in force in year t
  spill150 : UNTAXED airports within 150 km of a taxing country's commercial airport   (leakage group)
  buffer   : UNTAXED airports 150-300 km from a taxing country  -> DROPPED (treatment misclassification zone)
  control  : untaxed airports > 300 km from any taxing country in year t
  y_at = b*Tax_ct + s*Spill150_at + alpha_a + lambda_{region x year} + e ; cluster: country
Also: continuous "neighbour tax pressure" (distance-decay sum of foreign rates), event study, dynamics,
not-yet-treated control, and a back-of-envelope CO2 / cost-benefit block (EDGAR intensity).
"""
import pandas as pd, numpy as np, pathlib, pyfixest as pf, warnings
warnings.filterwarnings("ignore")
root = pathlib.Path(__file__).resolve().parents[1]
g = pd.read_csv(root/"data/processed/gaci_with_country.csv").dropna(subset=["iso_country"])
tax = pd.read_csv(root/"data/processed/aviation_taxes_master.csv", dtype=str, keep_default_na=False)
fx = pd.read_csv(root/"stata/fx_eur.csv")

# ---- country-year tax panel (mirrors 02_build_tax_panel.do) ----
t = tax[tax["class"].isin(["economy","all"]) & (tax.rate!="") & (tax.valid_from!="") & (tax.include_main=="1")].copy()
t["rate"] = pd.to_numeric(t.rate, errors="coerce"); t = t[t.rate>0]
t["vfrom"] = pd.to_datetime(t.valid_from); t["vto"] = pd.to_datetime(t.valid_to.replace("", "2024-12-31"))
t["dkm"] = pd.to_numeric(t.band_upper_km, errors="coerce")
rows = []
for _, r in t.iterrows():
    for y in range(r.vfrom.year, min(r.vto.year, 2024)+1):
        s = max(r.vfrom, pd.Timestamp(y,1,1)); e = min(r.vto, pd.Timestamp(y,12,31))
        months = min(12, (e - s).days/30.44 + 1/30.44)
        if months <= 0: continue
        rows.append({"iso_country": r.country_iso, "year": y, "months": months, "rate": r.rate, "cur": r.currency, "dkm": r.dkm})
ty = pd.DataFrame(rows).merge(fx, on=["cur","year"], how="left"); ty["fx"] = ty.fx.fillna(1.0)
ty["rate_eur"] = ty.rate*ty.fx*ty.months/12
dmin = ty.groupby(["iso_country","year"]).dkm.transform("min")
short = ty[(ty.dkm==dmin)|ty.dkm.isna()].groupby(["iso_country","year"]).rate_eur.sum().rename("tax_short_eur")
anym = ty.groupby(["iso_country","year"]).months.max().rename("months_any")
cy = pd.concat([anym, short], axis=1).reset_index()
cy["tax_any"] = (cy.months_any>=6).astype(int)
first = cy[cy.tax_any==1].groupby("iso_country").year.min().rename("first_tax")
ever = set(first.index)
print("Tax-years by country:", cy[cy.tax_any==1].groupby("iso_country").year.agg(["min","max","count"]).to_dict("index"))

# ---- airport panel ----
g = g.rename(columns={"Airport":"airport","Year":"year","Region":"region","TotalCapacity":"seats"})
g = g[g.lat.between(30,72) & g.lon.between(-30,60)]
g["nyears"] = g.groupby("airport").year.transform("nunique"); g["maxseats"] = g.groupby("airport").seats.transform("max")
g = g[(g.nyears>=20)&(g.maxseats>=50000)].copy()
g = g.merge(cy[["iso_country","year","tax_any","tax_short_eur"]], on=["iso_country","year"], how="left").fillna({"tax_any":0,"tax_short_eur":0})
g = g.merge(first, on="iso_country", how="left")
g["ever_treated"] = g.iso_country.isin(ever).astype(int)

# ---- distance to nearest taxing country (by year) + neighbour tax pressure ----
nd = pd.read_csv(root/"data/processed/airport_nearest_foreign_country_km.csv").rename(columns={"Airport":"airport"})
tx = cy[["iso_country","year","tax_any","tax_short_eur"]].rename(columns={"iso_country":"foreign_iso","tax_any":"f_tax","tax_short_eur":"f_rate"})
ndy = nd.merge(tx, on="foreign_iso")                      # airport x foreign taxing country x year
ndy = ndy[ndy.f_tax==1]
mind = ndy.groupby(["airport","year"]).km.min().rename("km_to_taxed")
press = ndy.assign(p=lambda d: d.f_rate/np.maximum(d.km,50)**2*1e4).groupby(["airport","year"]).p.sum().rename("nbr_tax_pressure")
g = g.merge(mind, on=["airport","year"], how="left").merge(press, on=["airport","year"], how="left")
g["nbr_tax_pressure"] = g.nbr_tax_pressure.fillna(0)
g["spill150"] = ((g.tax_any==0) & (g.km_to_taxed<=150)).astype(int)
g["buffer"]   = ((g.tax_any==0) & (g.km_to_taxed>150) & (g.km_to_taxed<=300)).astype(int)
g["ln_seats"] = np.log(g.seats); g["ln_gaci"] = np.log(g.GACI); g["ln_deg"] = np.log(g.Degree)
g["ry"] = g.region + "_" + g.year.astype(str)
g["et"] = (g.year - g.first_tax).clip(-5, 8)
g["yrs_since"] = np.where(g.tax_any==1, (g.year - g.first_tax).clip(0, None), 0)
base = g[g.buffer==0].copy()
print(f"sample: {base.airport.nunique()} airports, {len(base)} airport-years | treated {int(base.tax_any.sum())}, spill150 {int(base.spill150.sum())}, buffer dropped {int(g.buffer.sum())}")

def run(label, fml, data):
    m = pf.feols(fml, data=data, vcov={"CRV1":"iso_country"})
    print(f"\n[{label}]  N={m._N}"); print(m.tidy()[["Estimate","Std. Error","Pr(>|t|)"]].round(3).to_string())
    return m

for y in ["ln_seats","ln_deg","ln_gaci"]:
    run(f"{y}: binary + spill150, buffer dropped", f"{y} ~ tax_any + spill150 | airport + ry", base)
run("ln_seats: dose (EUR, shortest band) + neighbour tax pressure", "ln_seats ~ tax_short_eur + nbr_tax_pressure | airport + ry", base)
run("ln_seats: not-yet-treated control only (ever-treated countries)", "ln_seats ~ tax_any + spill150 | airport + ry", base[base.ever_treated==1])
run("ln_seats: seats-weighted", "ln_seats ~ tax_any + spill150 | airport + ry", base.assign(w=base.groupby("airport").seats.transform("first")), ) if False else None
run("ln_seats: excl. 2020-2022", "ln_seats ~ tax_any + spill150 | airport + ry", base[~base.year.between(2020,2022)])
run("ln_seats: dynamics (years since tax, quadratic)", "ln_seats ~ tax_any + yrs_since + I(yrs_since**2) + spill150 | airport + ry", base)
es = base.copy(); es["et"] = es.et.fillna(-1).astype(int)
m = run("event study, ln seats", "ln_seats ~ i(et, ref=-1) + spill150 | airport + ry", es)

# ---- back-of-envelope CO2 / cost-benefit (Li et al. Table 14 analogue) ----
b_tax = pf.feols("ln_seats ~ tax_any + spill150 | airport + ry", data=base, vcov={"CRV1":"iso_country"}).coef()
inten = pd.read_csv(root/"data/processed/edgar_intl_aviation_intensity.csv").set_index("year").t_per_seat
treated_seats = base[base.tax_any==1].groupby("year").seats.sum()
spill_seats = base[base.spill150==1].groupby("year").seats.sum()
cf_treated = treated_seats/np.exp(b_tax["tax_any"]) - treated_seats           # counterfactual-minus-actual seats (>0 = seats removed by tax)
cf_spill   = spill_seats/np.exp(b_tax["spill150"]) - spill_seats
abated_t = (cf_treated*inten.reindex(cf_treated.index)).sum(); leaked_t = -(cf_spill*inten.reindex(cf_spill.index)).sum()
print(f"\n[implied CO2] b_tax={b_tax['tax_any']:.3f}, b_spill={b_tax['spill150']:.3f}")
print(f"  seats removed in taxed airports (cum. 1996-2024): {cf_treated.sum()/1e6:,.0f} m ; implied CO2 avoided: {abated_t/1e6:,.1f} MtCO2e")
print(f"  seats added in spill airports: {-cf_spill.sum()/1e6:,.0f} m ; implied CO2 leaked: {leaked_t/1e6:,.1f} MtCO2e ; net: {(abated_t-leaked_t)/1e6:,.1f} MtCO2e")
for scc in (100, 200):
    print(f"  value at SCC {scc} EUR/t: gross {abated_t*scc/1e9:,.1f} bn EUR, net {(abated_t-leaked_t)*scc/1e9:,.1f} bn EUR")
print("  NOTE: intensity = EDGAR *international* aviation GHG / all scheduled seats -> lower bound; assumes unchanged stage length & load factor.")
