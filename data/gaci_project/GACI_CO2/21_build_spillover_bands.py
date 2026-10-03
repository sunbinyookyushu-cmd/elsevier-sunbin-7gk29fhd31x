# -*- coding: utf-8 -*-
"""
21_build_spillover_bands.py   (LZ comment 3, 2026-09-03)
Extends 12_build_spillover.py with:
  - contiguity exposure (Natural Earth 50m admin-0 polygons, touches)
  - distance bands: <500, 500-1000, 1000-2000, 2000-5000, >5000 km (leave-out means)
  - continuous kernel exp(-d/lambda), lambda in {250,500,1000,2000,5000} km
  - k-nearest (k=5) exposure
  - within-region vs out-of-region (UN sub-region; aviation bloc)
  - permutation placebo: 500 random row permutations of the inverse-distance W,
    IV coefficient distribution (pyfixest), saved to _spill_placebo_perm.csv
Each exposure X is built for ln_gaci_cwm (nbr_g_X) and feyrer_int (nbr_f_X).
Output: spillover_bands.csv (c, y, exposures, subregion, bloc, has_contig, has_bloc)
"""
import os, sys, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import pycountry

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ALIAS = {
    "Russia": "RUS", "Iran": "IRN", "Venezuela": "VEN", "Bolivia": "BOL",
    "Tanzania": "TZA", "Syria": "SYR", "Laos": "LAO", "Vietnam": "VNM",
    "South Korea": "KOR", "North Korea": "PRK", "Moldova": "MDA",
    "Democratic Republic of the Congo": "COD", "Congo (Kinshasa)": "COD",
    "Congo (Brazzaville)": "COG", "Republic of the Congo": "COG",
    "Ivory Coast": "CIV", "Cote d'Ivoire": "CIV", "Cape Verde": "CPV",
    "Brunei": "BRN", "Micronesia": "FSM", "Macedonia": "MKD",
    "North Macedonia": "MKD", "Czech Republic": "CZE", "Burma": "MMR",
    "Myanmar": "MMR", "East Timor": "TLS", "Palestine": "PSE",
    "Taiwan": "TWN", "Hong Kong": "HKG", "Macau": "MAC",
    "Turkey": "TUR", "United States": "USA", "United Kingdom": "GBR",
    "Swaziland": "SWZ", "Eswatini": "SWZ",  # 09-08 fix
}
def to_iso3(name, cache={}):
    if name in cache:
        return cache[name]
    iso = ALIAS.get(name)
    if iso is None:
        try:
            iso = pycountry.countries.lookup(name).alpha_3
        except LookupError:
            try:
                iso = pycountry.countries.search_fuzzy(name)[0].alpha_3
            except LookupError:
                iso = None
    cache[name] = iso
    return iso

# ---------------- centroids and panel ----------------
ap = pd.read_csv(os.path.join(HERE, "..", "airport_coords_merged.csv"))
ap["c"] = ap["country"].astype(str).map(to_iso3)
cent = ap.dropna(subset=["c"]).groupby("c")[["lat", "lon"]].mean()
panel = pd.read_csv(os.path.join(HERE, "..", "gaci_panel_combined.csv"),
                    usecols=["c", "y", "ln_gaci_cwm", "feyrer_int", "lnpop", "ln_sea_ma", "reg"])
panel = panel[panel["c"].isin(cent.index)].copy()
countries = sorted(panel["c"].unique())
n = len(countries)
idx = {c: i for i, c in enumerate(countries)}
print("countries:", n)

lat = np.radians(cent.loc[countries, "lat"].values)
lon = np.radians(cent.loc[countries, "lon"].values)
dlat = lat[:, None] - lat[None, :]
dlon = lon[:, None] - lon[None, :]
h = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
D = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
np.fill_diagonal(D, np.inf)

# ---------------- contiguity from Natural Earth ----------------
ne = gpd.read_file(os.path.join(HERE, "data_external", "ne_50m_admin_0.geojson"))
ne["iso"] = ne["ISO_A3_EH"].where(ne["ISO_A3_EH"] != "-99", ne["ADM0_A3"])
ne = ne[ne["iso"].isin(countries)].dissolve(by="iso")
ne["geometry"] = ne.geometry.buffer(0)
C = np.zeros((n, n), dtype=bool)
isos = list(ne.index)
sindex = ne.sindex
for a in isos:
    ga = ne.loc[a, "geometry"]
    for j in sindex.query(ga, predicate="intersects"):
        b = isos[j]
        if b != a:
            C[idx[a], idx[b]] = True
            C[idx[b], idx[a]] = True
has_contig = C.any(axis=1)
print("countries with a land neighbour:", has_contig.sum(), "of", n)
subreg = ne["SUBREGION"].to_dict()
unreg = ne["REGION_UN"].to_dict()

# ---------------- aviation blocs ----------------
BLOCS = {
    "EU_EEA": "AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE NOR ISL CHE GBR".split(),
    "ASEAN": "BRN KHM IDN LAO MYS MMR PHL SGP THA VNM".split(),
    "GCC": "BHR KWT OMN QAT SAU ARE".split(),
    "MERCOSUR": "ARG BRA PRY URY BOL".split(),
    "NORTH_AMERICA": "USA CAN MEX".split(),
    "ECOWAS": "BEN BFA CPV CIV GMB GHA GIN GNB LBR MLI NER NGA SEN SLE TGO".split(),
    "EAC_SADC": "KEN TZA UGA RWA BDI ZAF BWA NAM ZWE ZMB MWI MOZ AGO LSO SWZ MDG MUS SYC COD".split(),
    "CIS": "RUS BLR KAZ KGZ TJK UZB ARM AZE MDA TKM".split(),
    "ANDEAN_CA": "COL ECU PER CHL PAN CRI GTM HND SLV NIC DOM".split(),
    "SOUTH_ASIA": "IND PAK BGD LKA NPL BTN MDV".split(),
    "OCEANIA": "AUS NZL FJI PNG".split(),
}
bloc = {}
for b, lst in BLOCS.items():
    for c in lst:
        bloc[c] = b

# ---------------- weight matrices ----------------
def rownorm(W):
    rs = W.sum(axis=1, keepdims=True)
    return np.divide(W, rs, out=np.zeros_like(W), where=rs > 0)

Winv = 1.0 / np.maximum(D, 100.0); np.fill_diagonal(Winv, 0.0)
mats = {"inv": Winv, "contig": C.astype(float)}
bands = [("b1", 0, 500), ("b2", 500, 1000), ("b3", 1000, 2000), ("b4", 2000, 5000), ("b5", 5000, 1e9)]
for nm, lo, hi in bands:
    mats[nm] = ((D > lo) & (D <= hi)).astype(float)
for lam in [250, 500, 1000, 2000, 5000]:
    K = np.exp(-D / lam); np.fill_diagonal(K, 0.0)
    mats[f"k{lam}"] = K
# k nearest 5
knn = np.zeros((n, n))
for i in range(n):
    nn5 = np.argsort(D[i])[:5]
    knn[i, nn5] = 1.0
mats["knn5"] = knn
# region in/out (UN subregion) and bloc in/out
sr = np.array([subreg.get(c, "NA") for c in countries])
same_sr = (sr[:, None] == sr[None, :]) & (sr[:, None] != "NA")
np.fill_diagonal(same_sr, False)
mats["inreg"] = same_sr.astype(float)
mats["outreg"] = (~same_sr).astype(float) * Winv  # distance-weighted outside region
np.fill_diagonal(mats["outreg"], 0.0)
bl = np.array([bloc.get(c, "NA") for c in countries])
same_bl = (bl[:, None] == bl[None, :]) & (bl[:, None] != "NA")
np.fill_diagonal(same_bl, False)
mats["inbloc"] = same_bl.astype(float)
mats["outbloc"] = (~same_bl).astype(float) * Winv
np.fill_diagonal(mats["outbloc"], 0.0)

def exposures(W, v):
    ok = ~np.isnan(v)
    Wy = rownorm(W[:, ok])
    out = Wy @ v[ok]
    out[(W[:, ok].sum(axis=1) == 0)] = np.nan
    return out

rows = []
for y, g in panel.groupby("y"):
    g = g.set_index("c")
    vg = np.full(n, np.nan); vf = np.full(n, np.nan)
    for c in g.index:
        vg[idx[c]] = g.loc[c, "ln_gaci_cwm"]; vf[idx[c]] = g.loc[c, "feyrer_int"]
    ex = {}
    for nm, W in mats.items():
        ex[f"nbr_g_{nm}"] = exposures(W, vg)
        ex[f"nbr_f_{nm}"] = exposures(W, vf)
    for c in g.index:
        i = idx[c]
        r = {"c": c, "y": y, "subregion": subreg.get(c, ""), "unregion": unreg.get(c, ""),
             "bloc": bloc.get(c, "NONE"), "has_contig": int(has_contig[i]), "has_bloc": int(c in bloc)}
        for k, v in ex.items():
            r[k] = v[i]
        rows.append(r)
res = pd.DataFrame(rows)
# exposures undefined (no neighbour in band) -> 0 with the has_* flags for contig/bloc; bands: 0 too, flagged
for nm in ["contig", "inreg", "inbloc"] + [b[0] for b in bands]:
    for p in ["g", "f"]:
        col = f"nbr_{p}_{nm}"
        res[f"has_{nm}"] = res[col].notna().astype(int)
        res[col] = res[col].fillna(0.0)
res.to_csv(os.path.join(HERE, "spillover_bands.csv"), index=False)
print("saved spillover_bands.csv", res.shape)
print(res.filter(like="nbr_g_").describe().T[["count", "mean", "std"]].round(3).to_string())

# ---------------- permutation placebo (IV with permuted W rows) ----------------
try:
    import pyfixest as pf
    co2 = pd.read_csv(os.path.join(HERE, "co2_country_year.csv"), usecols=["iso3", "year", "co2_bunker"])
    co2 = co2.rename(columns={"iso3": "c", "year": "y"})
    co2["ln_co2_tot"] = np.log(co2["co2_bunker"].where(co2["co2_bunker"] > 0))
    base = panel.merge(co2[["c", "y", "ln_co2_tot"]], on=["c", "y"], how="left")
    base = base.merge(res[["c", "y", "nbr_g_inv", "nbr_f_inv"]], on=["c", "y"], how="left")
    base = base.dropna(subset=["ln_co2_tot", "nbr_g_inv", "nbr_f_inv", "feyrer_int", "lnpop", "ln_sea_ma"]).copy()
    fit = pf.feols("ln_co2_tot ~ feyrer_int + lnpop + ln_sea_ma | c + y | nbr_g_inv ~ nbr_f_inv", data=base, vcov="hetero")
    b_act = float(fit.coef()["nbr_g_inv"]); print("actual IV nbr coef (pyfixest):", round(b_act, 3))
    rf = pf.feols("ln_co2_tot ~ nbr_f_inv + feyrer_int + lnpop + ln_sea_ma | c + y", data=base, vcov="hetero")
    rf_act = float(rf.coef()["nbr_f_inv"]); rft_act = float(rf.tstat()["nbr_f_inv"])
    fs = pf.feols("nbr_g_inv ~ nbr_f_inv + feyrer_int + lnpop + ln_sea_ma | c + y", data=base, vcov="hetero")
    fst_act = float(fs.tstat()["nbr_f_inv"])
    print("actual RF nbr coef %.3f (t %.2f); FS t %.2f" % (rf_act, rft_act, fst_act))
    rng = np.random.default_rng(20260903)
    draws = []
    NPERM = 500
    yrs = sorted(base["y"].unique())
    pan_by_y = {y: g.set_index("c") for y, g in panel.groupby("y")}
    for d in range(NPERM):
        perm = rng.permutation(n)
        Wp = Winv[perm, :][:, perm]  # relabel countries: destroys the true geography, keeps W structure
        recs = []
        for y in yrs:
            g = pan_by_y[y]
            vg = np.full(n, np.nan); vf = np.full(n, np.nan)
            for c in g.index:
                vg[idx[c]] = g.loc[c, "ln_gaci_cwm"]; vf[idx[c]] = g.loc[c, "feyrer_int"]
            eg = exposures(Wp, vg); ef = exposures(Wp, vf)
            for c in g.index:
                recs.append((c, y, eg[idx[c]], ef[idx[c]]))
        pr = pd.DataFrame(recs, columns=["c", "y", "pg", "pfv"])
        dd = base.merge(pr, on=["c", "y"], how="left").dropna(subset=["pg", "pfv"])
        try:
            f = pf.feols("ln_co2_tot ~ feyrer_int + lnpop + ln_sea_ma | c + y | pg ~ pfv", data=dd, vcov="hetero")
            r = pf.feols("ln_co2_tot ~ pfv + feyrer_int + lnpop + ln_sea_ma | c + y", data=dd, vcov="hetero")
            q = pf.feols("pg ~ pfv + feyrer_int + lnpop + ln_sea_ma | c + y", data=dd, vcov="hetero")
            draws.append({"draw": d, "b": float(f.coef()["pg"]), "se": float(f.se()["pg"]),
                          "rf_b": float(r.coef()["pfv"]), "rf_t": float(r.tstat()["pfv"]), "fs_t": float(q.tstat()["pfv"])})
        except Exception as e:
            draws.append({"draw": d, "b": np.nan, "se": np.nan, "rf_b": np.nan, "rf_t": np.nan, "fs_t": np.nan})
        if d % 100 == 0:
            print("perm", d)
    pdraws = pd.DataFrame(draws)
    pdraws.attrs["b_actual"] = b_act
    pdraws["b_actual"] = b_act; pdraws["rf_actual"] = rf_act; pdraws["rft_actual"] = rft_act; pdraws["fst_actual"] = fst_act
    pdraws.to_csv(os.path.join(HERE, "_spill_placebo_perm.csv"), index=False)
    bb = pdraws["rf_t"].dropna()
    print("placebo RF t: mean %.3f sd %.3f  share |t_perm| >= |t_actual| (%.2f): %.3f" % (bb.mean(), bb.std(), abs(rft_act), (bb.abs() >= abs(rft_act)).mean()))
    rb = pdraws["rf_b"].dropna()
    print("placebo RF b: mean %.3f sd %.3f  share |b_perm| >= |b_actual| (%.3f): %.3f" % (rb.mean(), rb.std(), abs(rf_act), (rb.abs() >= abs(rf_act)).mean()))
    print("placebo FS t: mean |t| %.2f  share |t| >= 1.96: %.3f  (actual %.2f)" % (pdraws["fs_t"].abs().mean(), (pdraws["fs_t"].abs() >= 1.96).mean(), fst_act))
except Exception as e:
    print("PERMUTATION PLACEBO FAILED:", e)
print("DONE_21")
