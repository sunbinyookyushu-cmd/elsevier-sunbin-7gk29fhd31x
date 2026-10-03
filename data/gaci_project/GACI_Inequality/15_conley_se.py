# -*- coding: utf-8 -*-
"""15_conley_se.py : country-clustered vs Conley spatial-temporal HAC standard errors.
   Model: y_ct = b ln GACI_max_ct + g ln pop_ct + a_c + d_t + e_ct, OLS and 2SLS (Feyrer IV a_t x ln MA_1996).
   Two-way FE removed by alternating projections; b, g estimated on the within-transformed data.
   Variance = (Xh'X)^-1 [sum_ij w_ij (xh_i e_i)(xh_j e_j)'] (X'Xh)^-1  with xh = fitted first stage (2SLS) or x (OLS).
   Weights w_ij = K_s(d_ij) * K_t(|t_i - t_j|):
     K_s Bartlett in great-circle distance between country centroids, cutoff D km (K_s = 1 within a country);
     K_t Bartlett in years, cutoff L (L = 'all' -> 1 for every lag, i.e. no temporal downweighting).
   D = 0 with L = 'all' and a CRV1 correction reproduces country-clustered SE (check against Stata).
   Outputs _conley_se_results.csv. Coordinates: Natural Earth centroids (../_world.geojson, ISO_A3_EH)."""
import os, numpy as np, pandas as pd, geopandas as gpd
from scipy import stats

D_ = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(D_, "ineq_panel_ext.csv"), low_memory=False)
w = gpd.read_file(os.path.join(D_, "..", "_world.geojson"))
w["iso3"] = w["ISO_A3_EH"].where(w["ISO_A3_EH"] != "-99", w["ADM0_A3"])
cen = w.dissolve(by="iso3").geometry.representative_point()
coords = pd.DataFrame({"lat": cen.y, "lon": cen.x})
# fallback for countries absent from the 1:110m map (islands, city states): mean airport coordinates, as in ../build_feyrer_iv.py
import csv, json, collections
P = os.path.join(D_, "..")
ap = {r["Airport"]: (float(r["lat"]), float(r["lon"])) for r in csv.DictReader(open(os.path.join(P, "airport_coords_merged.csv"), encoding="utf-8"))}
ap_iso2 = {}
for r in csv.DictReader(open(os.path.join(P, "ourairports.csv"), encoding="utf-8", errors="replace")):
    ia = (r.get("iata_code") or "").strip()
    if len(ia) == 3: ap_iso2[ia] = r.get("iso_country", "").strip()
iso2to3 = json.load(open(os.path.join(P, "iso2to3.json")))
cl = collections.defaultdict(list)
for a, (la, lo) in ap.items():
    i3 = iso2to3.get(ap_iso2.get(a, ""), "")
    if i3: cl[i3].append((la, lo))
miss = sorted(set(d.c) - set(coords.index))
fb = {c: (np.mean([x[0] for x in cl[c]]), np.mean([x[1] for x in cl[c]])) for c in miss if c in cl}
coords = pd.concat([coords, pd.DataFrame(fb, index=["lat", "lon"]).T])
print("centroids from airports:", sorted(fb), "| still missing:", sorted(set(miss) - set(fb)))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

def demean(M, ids1, ids2, tol=1e-11, maxit=5000):
    M = M.astype(float).copy()
    for _ in range(maxit):
        M0 = M.copy()
        for ids in (ids1, ids2):
            g = pd.DataFrame(M).groupby(ids).transform("mean").values
            M = M - g
        if np.max(np.abs(M - M0)) < tol:
            break
    return M

def fit(y, X, Z=None):
    if Z is None:
        Xh = X
    else:
        Xh = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
    A = np.linalg.inv(Xh.T @ X)
    b = A @ (Xh.T @ y)
    e = y - X @ b
    return b, e, Xh, A

def sandwich(A, Xh, e, W):
    G = Xh * e[:, None]
    M = G.T @ (W @ G)
    return A @ M @ A.T

def run(sample, yv, xv, iv, specs, label):
    s = sample.dropna(subset=[yv, xv, "lnpop", iv]).copy()
    s = s[s.c.isin(coords.index)]
    cid = s.c.astype("category").cat.codes.values
    tid = s.y.astype(int).values
    yy = demean(s[[yv]].values, cid, tid)[:, 0]
    X = demean(s[[xv, "lnpop"]].values, cid, tid)
    Z = demean(s[[iv, "lnpop"]].values, cid, tid)
    N, K = X.shape
    G = len(np.unique(cid))
    # pairwise distance in km between observations via country index
    cc = s.c.astype("category").cat.categories
    la = coords.loc[cc, "lat"].values; lo = coords.loc[cc, "lon"].values
    Dc = haversine(la[:, None], lo[:, None], la[None, :], lo[None, :])
    Dobs = Dc[cid][:, cid]
    dT = np.abs(tid[:, None] - tid[None, :])
    same_c = (cid[:, None] == cid[None, :])
    out = []
    for model in ["OLS", "2SLS"]:
        b, e, Xh, A = fit(yy, X, None if model == "OLS" else Z)
        for (Dk, L) in specs:
            if Dk == 0:
                Ks = same_c.astype(float)
            else:
                Ks = np.clip(1 - Dobs / Dk, 0, 1)
                Ks[same_c] = 1.0
            if L == "all":
                Kt = np.ones_like(dT, dtype=float)
            else:
                Kt = np.clip(1 - dT / (L + 1), 0, 1)
            Wm = Ks * Kt
            V = sandwich(A, Xh, e, Wm)
            if Dk == 0 and L == "all":
                V = V * (G / (G - 1)) * ((N - 1) / (N - K - (G - 1) - (len(np.unique(tid)) - 1)))  # CRV1 with FE dof as in reghdfe
                spec = "cluster_country"
            else:
                spec = "conley_D%s_L%s" % (Dk, L)
            se = np.sqrt(V[0, 0])
            p = 2 * (1 - stats.norm.cdf(abs(b[0] / se)))
            out.append({"block": label, "outcome": yv, "model": model, "spec": spec, "b": b[0], "se": se, "p": p, "N": N, "G": G})
    return out

SPECS = [(0, "all"), (500, "all"), (1000, "all"), (2000, "all"), (3000, "all"), (5000, "all"),
         (1000, 5), (2000, 5), (2000, 10), (3000, 10)]
base = d.dropna(subset=["gini_mkt"]).copy()
res = []
for yv in ["ln_gini_mkt", "ln_gini_disp"]:
    res += run(base, yv, "ln_gaci_max", "feyrer_int", SPECS, "headline")
    print(pd.DataFrame(res).tail(len(SPECS) * 2)[["outcome", "model", "spec", "b", "se", "p"]].round(3).to_string(index=False))

# group-specific regressions (income level and relative income = share identity), 2SLS focus
GROUPS = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01", "b50", "all"]
GSPECS = [(0, "all"), (1000, "all"), (2000, "all"), (3000, "all"), (2000, 10)]
for g in GROUPS:
    base["rel_" + g] = base["ln_apt_" + g] - base["ln_apt_all"]
    res += run(base, "ln_apt_" + g, "ln_gaci_max", "feyrer_int", GSPECS, "gic_income")
    if g != "all":
        res += run(base, "rel_" + g, "ln_gaci_max", "feyrer_int", GSPECS, "gic_share")
R = pd.DataFrame(res)
R.to_csv(os.path.join(D_, "_conley_se_results.csv"), index=False)
print("saved _conley_se_results.csv", R.shape)
