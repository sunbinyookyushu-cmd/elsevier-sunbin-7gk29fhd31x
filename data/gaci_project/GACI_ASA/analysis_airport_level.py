"""Airport-level ASA design that runs on existing data (no route/pair data needed).

Idea (Li et al. 2019 within-city logic): national agreement exposure Exp_ct hits airports in proportion to their
predetermined international orientation. With COUNTRY x YEAR FE, the national timing of agreements (and every national
shock) is absorbed; beta comes from within-country differences between airports that were more vs less international
before liberalisation.

    ln y_at = beta * (Exp_ct x s_a) + alpha_a + delta_ct + e_at          (dose design)
    s_a  = airport's international share of departing seats, mean 1996-1998 (predetermined)
    Exp_ct = share of world international seats (1996 weights) in partner countries with an agreement in force with c
Outcomes: international seats, flights, seat-km, CO2, stage length, CO2 per seat-km (departures); GACI, degree,
eigenvector, betweenness (annual). SE clustered by country. Also: dose by agreement type; hub (top airport) interaction;
Europe-only sample; placebo with domestic outcomes (an agreement should not move domestic flying).
Output: _res_asa_airport.csv, _out_airport_level.txt
"""
import pandas as pd, numpy as np, pathlib, pyfixest as pf, warnings
warnings.filterwarnings("ignore")
here = pathlib.Path(__file__).resolve().parent; root = here.parents[2]
e = pd.read_csv(root/"data/raw/external/airport_year_emissions.csv"); e = e[e.year <= 2023]
m = pd.read_csv(root/"data/processed/airport_country_map.csv")[["Airport","iso_country","lat","lon"]].rename(columns={"Airport":"airport_iata","iso_country":"iso"})
e = e.merge(m, on="airport_iata", how="inner")
e["kind"] = np.where(e.dom_intl=="International","intl","dom")
w = e.pivot_table(index=["airport_iata","iso","year"], columns="kind", values=["dep_seats","n_dep_flights","dep_seat_km","dep_co2_t"], aggfunc="sum").fillna(0)
w.columns = [f"{v}_{k}" for v,k in w.columns]; A = w.reset_index()
g = pd.read_csv(root/"data/processed/gaci_with_country.csv")[["Airport","Year","GACI","Degree","Eigen","NorBetweenness","Region"]].rename(columns={"Airport":"airport_iata","Year":"year"})
A = A.merge(g, on=["airport_iata","year"], how="left")
# predetermined international share (1996-98) and hub flag (largest airport of the country by 1996-98 seats)
base = A[A.year.between(1996,1998)].groupby(["airport_iata","iso"]).agg(s_intl=("dep_seats_intl","sum"), s_all=("dep_seats_intl","sum")).reset_index()
tot = A[A.year.between(1996,1998)].groupby("airport_iata").apply(lambda d: (d.dep_seats_intl+d.dep_seats_dom).sum()).rename("s_tot").reset_index()
base = base.merge(tot, on="airport_iata"); base["intl_share0"] = base.s_intl/base.s_tot.replace(0,np.nan)
base["hub0"] = (base.groupby("iso").s_tot.transform("max") == base.s_tot).astype(int)
A = A.merge(base[["airport_iata","intl_share0","hub0","s_tot"]], on="airport_iata", how="inner")
A = A[A.s_tot >= 50000*3]                                   # airports with >= 50k seats/yr in the base period
# country exposure
P = pd.read_csv(here/"asa_pair_year.csv"); Y = pd.read_csv(here/"country_year_outcomes.csv")
wt = Y[Y.year==1996].set_index("iso_country").intl_seats; wt = (wt/wt.sum()).rename("w").reset_index().rename(columns={"iso_country":"d_iso"})
E = P.merge(wt, on="d_iso", how="left").fillna({"w":0})
for k in ["any","us","eu","bloc","bil"]: E[f"exp_{k}"] = E[f"open_{k}"]*E.w
X = E.groupby(["o_iso","year"])[[f"exp_{k}" for k in ["any","us","eu","bloc","bil"]]].sum().reset_index().rename(columns={"o_iso":"iso"})
A = A.merge(X, on=["iso","year"], how="left").fillna({f"exp_{k}":0 for k in ["any","us","eu","bloc","bil"]})
for k in ["any","us","eu","bloc","bil"]: A[f"dose_{k}"] = A[f"exp_{k}"]*A.intl_share0
A["dose_hub"] = A.exp_any*A.hub0
A["cy"] = A.iso + "_" + A.year.astype(str)
def L(x): return np.log(x.where(x > 0))
A["ln_seats_i"]=L(A.dep_seats_intl); A["ln_fl_i"]=L(A.n_dep_flights_intl); A["ln_skm_i"]=L(A.dep_seat_km_intl); A["ln_co2_i"]=L(A.dep_co2_t_intl)
A["ln_stage_i"]=L(A.dep_seat_km_intl/A.dep_seats_intl.replace(0,np.nan)); A["ln_int_i"]=L(A.dep_co2_t_intl*1e6/A.dep_seat_km_intl.replace(0,np.nan))
A["ln_seats_d"]=L(A.dep_seats_dom); A["ln_co2_d"]=L(A.dep_co2_t_dom)
A["ln_gaci"]=L(A.GACI); A["ln_deg"]=L(A.Degree); A["ln_eig"]=L(A.Eigen); A["ln_betw"]=L(A.NorBetweenness)
print(f"airports {A.airport_iata.nunique()}, countries {A.iso.nunique()}, airport-years {len(A)} | intl_share0: mean {A.drop_duplicates('airport_iata').intl_share0.mean():.2f} sd {A.drop_duplicates('airport_iata').intl_share0.std():.2f} | exp_any 2019: mean {A[A.year==2019].exp_any.mean():.2f}")
res=[]; lines=[]
def run(label, fml, d, terms):
    mdl = pf.feols(fml, data=d, vcov={"CRV1":"iso"}); t = mdl.tidy()
    out=[]
    for term in terms:
        if term in t.index:
            r=t.loc[term]; res.append({"block":label,"term":term,"b":r["Estimate"],"se":r["Std. Error"],"p":r["Pr(>|t|)"],"n":mdl._N}); out.append(f"{term} {r['Estimate']:+.3f} ({r['Std. Error']:.3f}) p={r['Pr(>|t|)']:.2f}")
    s=f"{label:48s} " + " | ".join(out) + f"  N={mdl._N}"; print(s); lines.append(s)
OUT_I = ["ln_seats_i","ln_fl_i","ln_skm_i","ln_co2_i","ln_stage_i","ln_int_i"]; OUT_N = ["ln_gaci","ln_deg","ln_eig","ln_betw"]
print("\n=== 1. Dose = national exposure x predetermined intl share; airport FE + country x year FE (beta = effect of exposure 0->1 for a fully international airport) ===")
for y in OUT_I+OUT_N: run(f"1 {y}", f"{y} ~ dose_any | airport_iata + cy", A.dropna(subset=[y]), ["dose_any"])
A["yr"]=A.year.astype(int)
print("\n=== 1b. SAME + intl_share0 x year dummies (absorbs the secular convergence of domestic airports into international flying) ===")
for y in OUT_I+OUT_N+["ln_seats_d","ln_co2_d"]: run(f"1b {y}", f"{y} ~ dose_any + i(yr, intl_share0, ref=1996) | airport_iata + cy", A.dropna(subset=[y]), ["dose_any"])
print("\n=== 2. By agreement type ===")
for y in ["ln_co2_i","ln_seats_i","ln_stage_i","ln_int_i","ln_gaci","ln_deg"]: run(f"2 {y}", f"{y} ~ dose_us + dose_eu + dose_bloc + dose_bil | airport_iata + cy", A.dropna(subset=[y]), ["dose_us","dose_eu","dose_bloc","dose_bil"])
print("\n=== 3. Hub vs non-hub: exposure x hub (largest airport) with country x year FE ===")
for y in ["ln_co2_i","ln_seats_i","ln_gaci","ln_betw","ln_eig"]: run(f"3 {y}", f"{y} ~ dose_any + dose_hub | airport_iata + cy", A.dropna(subset=[y]), ["dose_any","dose_hub"])
print("\n=== 4. Placebo: DOMESTIC outcomes should not respond ===")
for y in ["ln_seats_d","ln_co2_d"]: run(f"4 {y}", f"{y} ~ dose_any | airport_iata + cy", A.dropna(subset=[y]), ["dose_any"])
print("\n=== 5. Europe-only sample (EU1/EU2 regions) ===")
Eu = A[A.Region.isin(["EU1","EU2"])]
for y in ["ln_co2_i","ln_seats_i","ln_stage_i","ln_int_i","ln_gaci","ln_deg"]: run(f"5 {y}", f"{y} ~ dose_any | airport_iata + cy", Eu.dropna(subset=[y]), ["dose_any"])
print("\n=== 6. Elasticity form: dose scaled by its SD among airports (effect of a 1-SD dose change) ===")
sd = A.dose_any.std(); print(f"SD(dose_any) = {sd:.3f}  -> multiply column-1 betas by {sd:.3f}")
pd.DataFrame(res).to_csv(here/"_res_asa_airport.csv", index=False); open(here/"_out_airport_level.txt","w").write("\n".join(lines))
