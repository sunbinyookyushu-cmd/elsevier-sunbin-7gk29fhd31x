"""Country-level ASA analysis that runs on current data (dyadic version waits for the OAG pair file).
 A. US open-skies DiD: partner country c treated from the first full year in force; outcomes = c's international
    seats, flights, CO2, stage length, CO2 per seat-km, GACI (cap-weighted mean, max), destinations; country FE +
    year FE, and + region x year FE; event study -5..+8; SE clustered by country. Never-/not-yet-treated controls.
 B. Liberalisation exposure index: Exp_ct = sum_p Open_cpt x w_p, w_p = partner p's share of world international
    seats in 1996 (predetermined weights), all agreement types; same FE; continuous treatment.
 C. EU-horizontal subsample placeholder (if horizontal agreements are in the EU table).
Output: _res_asa_country.csv and printed tables.
"""
import pandas as pd, numpy as np, pathlib, pyfixest as pf, warnings
warnings.filterwarnings("ignore")
here = pathlib.Path(__file__).resolve().parent
Y = pd.read_csv(here/"country_year_outcomes.csv").rename(columns={"iso_country":"iso"})
P = pd.read_csv(here/"asa_pair_year.csv")
reg = pd.read_csv(here.parents[2]/"data/processed/gaci_with_country.csv").groupby("iso_country").Region.agg(lambda s: s.mode().iloc[0]).rename("region").reset_index().rename(columns={"iso_country":"iso"})
Y = Y.merge(reg, on="iso", how="left"); Y["ry"] = Y.region.astype(str) + "_" + Y.year.astype(str)
for c, src in [("ln_seats","intl_seats"),("ln_fl","intl_flights"),("ln_co2","intl_co2_t"),("ln_stage","intl_stage_km"),("ln_int","intl_co2_per_skm_g"),("ln_gaci","gaci_cwm"),("ln_gmax","gaci_max"),("ln_deg","deg_sum")]:
    Y[c] = np.log(Y[src].where(Y[src] > 0))
# ---- A. US open skies ----
us = P[(P.o_iso=="US") & (P.open_us==1)].groupby("d_iso").year.min().rename("us_first").reset_index().rename(columns={"d_iso":"iso"})
A = Y[Y.iso!="US"].merge(us, on="iso", how="left")
A["open_us"] = ((A.year >= A.us_first) & A.us_first.notna()).astype(int)
A["et"] = (A.year - A.us_first).clip(-5, 8)
print(f"US open-skies partners in panel: {A.us_first.notna().groupby(A.iso).max().sum()} countries; treated country-years {int(A.open_us.sum())}")
res = []
def run(label, fml, d, cl="iso"):
    m = pf.feols(fml, data=d, vcov={"CRV1": cl}); t = m.tidy()
    for term in t.index:
        if term.startswith(("open","exp","et","C(")): res.append({"block":label,"term":term,"b":t.loc[term,"Estimate"],"se":t.loc[term,"Std. Error"],"p":t.loc[term,"Pr(>|t|)"],"n":m._N})
    return m
print("\n=== A. US open skies, country FE + year FE (col 1) and + region x year FE (col 2) ===")
for y in ["ln_seats","ln_fl","ln_co2","ln_stage","ln_int","ln_gaci","ln_gmax","ln_deg"]:
    d = A.dropna(subset=[y])
    m1 = run(f"A1 {y}", f"{y} ~ open_us | iso + year", d); m2 = run(f"A2 {y}", f"{y} ~ open_us | iso + ry", d)
    t1, t2 = m1.tidy().loc["open_us"], m2.tidy().loc["open_us"]
    print(f"{y:9s}  {t1['Estimate']:+.3f} ({t1['Std. Error']:.3f}) p={t1['Pr(>|t|)']:.2f}   |  {t2['Estimate']:+.3f} ({t2['Std. Error']:.3f}) p={t2['Pr(>|t|)']:.2f}   N={m1._N}")
es = A.copy(); es["et"] = es.et.fillna(-1).astype(int)
for y in ["ln_co2","ln_gaci"]:
    m = run(f"A-ES {y}", f"{y} ~ i(et, ref=-1) | iso + ry", es.dropna(subset=[y]))
    print(f"\n[event study {y}]\n", m.tidy()[["Estimate","Std. Error","Pr(>|t|)"]].round(3).to_string())
# ---- B. exposure index ----
w = Y[Y.year==1996].set_index("iso").intl_seats; w = (w/w.sum()).rename("w").reset_index().rename(columns={"iso":"d_iso"})
E = P.merge(w, on="d_iso", how="left").fillna({"w":0})
E["exp_any"] = E.open_any*E.w; E["exp_us"] = E.open_us*E.w; E["exp_eu"] = E.open_eu*E.w; E["exp_reg"] = E.open_regional*E.w
X = E.groupby(["o_iso","year"])[["exp_any","exp_us","exp_eu","exp_reg"]].sum().reset_index().rename(columns={"o_iso":"iso"})
B = Y.merge(X, on=["iso","year"], how="left").fillna({"exp_any":0,"exp_us":0,"exp_eu":0,"exp_reg":0})
print("\n=== B. exposure index (share of world intl seats covered by an agreement in force), country FE + region x year FE ===")
for y in ["ln_seats","ln_co2","ln_stage","ln_int","ln_gaci","ln_deg"]:
    d = B.dropna(subset=[y]); m = run(f"B {y}", f"{y} ~ exp_any | iso + ry", d); t = m.tidy().loc["exp_any"]
    kinds = [k for k in ["exp_us","exp_eu","exp_reg"] if d[k].abs().sum() > 0]
    m3 = run(f"B3 {y}", f"{y} ~ {' + '.join(kinds)} | iso + ry", d); t3 = m3.tidy()
    by = " ".join(f"{k[4:]} {t3.loc[k,'Estimate']:+.2f}({t3.loc[k,'Std. Error']:.2f})" for k in kinds)
    print(f"{y:9s} exp_any {t['Estimate']:+.3f} ({t['Std. Error']:.3f}) p={t['Pr(>|t|)']:.2f} | {by}  N={m._N}")
pd.DataFrame(res).to_csv(here/"_res_asa_country.csv", index=False)
