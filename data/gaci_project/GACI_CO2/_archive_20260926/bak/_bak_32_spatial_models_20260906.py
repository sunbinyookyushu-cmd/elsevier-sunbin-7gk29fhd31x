# -*- coding: utf-8 -*-
"""
32_spatial_models.py   (Junya / Longfei request, 2026-09-06)
Standard spatial econometric models for the connectivity-CO2 elasticity:
  SLX, SAR, SEM, SDM (and SDEM) with country and year fixed effects,
  (A) maximum likelihood on the within-transformed data (non-instrumented),
  (B) generalised spatial 2SLS with the Feyrer shifter as the excluded
      instrument for own connectivity (Kelejian-Prucha style: W y instrumented
      by W Z, W^2 Z, W X, W^2 X; spatial error by KP GMM + Cochrane-Orcutt).
W: contiguity (Natural Earth 50m, land border) as headline; inverse distance
   (aviation-activity centroids, 100 km floor) as the alternative. Row-normalised
   within each year over the countries in the estimation sample that year.
Sample and variables replicate co2_spill_bands_cl.do (N = 4,623).
Outputs: _spatial_models.csv, _tex_spatial.tex
"""
import os, sys, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import pycountry
from scipy import optimize, sparse
from scipy.sparse.linalg import spsolve

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260906)

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

# ---------------------------------------------------------------- panel
gp = pd.read_csv(os.path.join(HERE, "..", "gaci_panel_combined.csv"),
                 usecols=["c", "y", "ln_gaci_cwm", "feyrer_int", "lnpop", "ln_sea_ma"])
co2 = pd.read_csv(os.path.join(HERE, "co2_country_year.csv"),
                  usecols=["iso3", "year", "co2_bunker", "co2_bunker_intl", "dep_seat_km"])
co2 = co2.rename(columns={"iso3": "c", "year": "y"})
df = gp.merge(co2, on=["c", "y"], how="left")
df["ln_co2_tot"] = np.log(df["co2_bunker"].where(df["co2_bunker"] > 0))
df["ln_co2_intl"] = np.log(df["co2_bunker_intl"].where(df["co2_bunker_intl"] > 0))
df["ln_skm"] = np.log(df["dep_seat_km"].where(df["dep_seat_km"] > 0))
df["ln_intensity"] = df["ln_co2_tot"] - df["ln_skm"]

ap = pd.read_csv(os.path.join(HERE, "..", "airport_coords_merged.csv"))
ap["c"] = ap["country"].astype(str).map(to_iso3)
cent = ap.dropna(subset=["c"]).groupby("c")[["lat", "lon"]].mean()
df = df[df["c"].isin(cent.index)].copy()
df = df.dropna(subset=["ln_co2_tot", "ln_gaci_cwm", "feyrer_int", "lnpop", "ln_sea_ma"]).copy()
df = df.sort_values(["y", "c"]).reset_index(drop=True)
print("sample N =", len(df), "countries =", df["c"].nunique())

countries = sorted(df["c"].unique())
n = len(countries)
idx = {c: i for i, c in enumerate(countries)}
lat = np.radians(cent.loc[countries, "lat"].values)
lon = np.radians(cent.loc[countries, "lon"].values)
dlat = lat[:, None] - lat[None, :]
dlon = lon[:, None] - lon[None, :]
h = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
D = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
np.fill_diagonal(D, np.inf)
ne = gpd.read_file(os.path.join(HERE, "data_external", "ne_50m_admin_0.geojson"))
ne["iso"] = ne["ISO_A3_EH"].where(ne["ISO_A3_EH"] != "-99", ne["ADM0_A3"])
ne = ne[ne["iso"].isin(countries)].dissolve(by="iso")
ne["geometry"] = ne.geometry.buffer(0)
C = np.zeros((n, n))
isos = list(ne.index)
sindex = ne.sindex
for a in isos:
    ga = ne.loc[a, "geometry"]
    for j in sindex.query(ga, predicate="intersects"):
        b = isos[j]
        if b != a:
            C[idx[a], idx[b]] = 1.0
            C[idx[b], idx[a]] = 1.0
Winv = 1.0 / np.maximum(D, 100.0)
np.fill_diagonal(Winv, 0.0)
print("countries with a land neighbour:", int((C.sum(1) > 0).sum()), "of", n)

def build_block_W(Wfull):
    """Block-diagonal sparse W over the stacked sample (sorted by y, c),
    row-normalised within year over countries present that year."""
    blocks = []
    for y, g in df.groupby("y", sort=True):
        ii = [idx[c] for c in g["c"]]
        Wt = Wfull[np.ix_(ii, ii)].copy()
        rs = Wt.sum(1, keepdims=True)
        Wt = np.divide(Wt, rs, out=np.zeros_like(Wt), where=rs > 0)
        blocks.append(sparse.csr_matrix(Wt))
    return sparse.block_diag(blocks, format="csr")

# ---------------------------------------------------------------- helpers
cid = df["c"].map(idx).values
yid = pd.factorize(df["y"])[0]
clus = cid

def demean(M):
    """Two-way (country, year) within transformation, alternating projections."""
    M = np.array(M, dtype=float, copy=True)
    one_d = M.ndim == 1
    if one_d:
        M = M[:, None]
    for _ in range(200):
        old = M.copy()
        for ids in (cid, yid):
            k = ids.max() + 1
            cnt = np.bincount(ids, minlength=k)
            for j in range(M.shape[1]):
                s = np.bincount(ids, weights=M[:, j], minlength=k)
                M[:, j] -= (s / cnt)[ids]
        if np.abs(M - old).max() < 1e-10:
            break
    return M[:, 0] if one_d else M

def ols(y, X):
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return b, y - X @ b

def cluster_vcov(Xw, u, bread_inv, cl):
    """Sandwich with cluster sums of Xw_i*u_i (Xw = 'score' regressors)."""
    S = Xw * u[:, None]
    G = cl.max() + 1
    meat = np.zeros((Xw.shape[1], Xw.shape[1]))
    agg = np.zeros((G, Xw.shape[1]))
    np.add.at(agg, cl, S)
    meat = agg.T @ agg
    nobs, k = Xw.shape
    adj = G / (G - 1) * (nobs - 1) / (nobs - k)
    return adj * bread_inv @ meat @ bread_inv

def robust_vcov(Xw, u, bread_inv):
    S = Xw * u[:, None]
    nobs, k = Xw.shape
    return nobs / (nobs - k) * bread_inv @ (S.T @ S) @ bread_inv

def tsls(y, Xend, Xex, H, cl):
    """2SLS: y on [Xend, Xex], instruments [H, Xex] (all already demeaned).
    Returns b, se_cluster, se_robust, names order = endog then exog, plus
    Sanderson-Windmeijer conditional F (cluster-robust) for each endogenous."""
    X = np.column_stack([Xend, Xex]) if Xex.shape[1] else Xend
    Z = np.column_stack([H, Xex]) if Xex.shape[1] else H
    PZ = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
    bread_inv = np.linalg.inv(PZ.T @ X)
    b = bread_inv @ PZ.T @ y
    u = y - X @ b
    Vc = cluster_vcov(PZ, u, bread_inv, cl)
    Vr = robust_vcov(PZ, u, bread_inv)
    # SW conditional F for each endogenous regressor (cluster-robust Wald / L)
    swf = []
    ke = Xend.shape[1]
    L = H.shape[1]
    for j in range(ke):
        others = np.delete(Xend, j, axis=1)
        if others.shape[1]:
            oth_hat = Z @ np.linalg.solve(Z.T @ Z, Z.T @ others)
            R = np.column_stack([oth_hat, Xex]) if Xex.shape[1] else oth_hat
            _, xt = ols(Xend[:, j], R)
        else:
            xt = Xend[:, j] - (Xex @ ols(Xend[:, j], Xex)[0] if Xex.shape[1] else 0)
        g, ug = ols(xt, Z)
        bi = np.linalg.inv(Z.T @ Z)
        Vg = cluster_vcov(Z, ug, bi, cl)
        gH = g[:L]
        VH = Vg[:L, :L]
        wald = gH @ np.linalg.solve(VH, gH)
        swf.append(wald / L * L / (L - ke + 1))
    return b, np.sqrt(np.diag(Vc)), np.sqrt(np.diag(Vr)), u, swf

def kp_lambda(u, W):
    """Kelejian-Prucha (1999) GMM for the spatial error parameter."""
    Wu = W @ u
    WWu = W @ Wu
    N = len(u)
    trWW = (W.multiply(W)).sum()  # tr(W'W) = sum of squares
    def moments(p):
        lam, s2 = p
        e = u - lam * Wu
        We = Wu - lam * WWu
        m1 = e @ e / N - s2
        m2 = We @ We / N - s2 * trWW / N
        m3 = e @ We / N
        return np.array([m1, m2, m3])
    sol = optimize.least_squares(moments, x0=[0.0, u @ u / N], bounds=([-0.99, 1e-8], [0.99, np.inf]))
    return sol.x[0]

def dense_blocks(W, blocks_n):
    out=[]; start=0
    for nb in blocks_n:
        out.append(W[start:start + nb, start:start + nb].toarray()); start += nb
    return out
_WB = {}
def get_blocks(W, blocks_n):
    key = id(W)
    if key not in _WB:
        _WB[key] = dense_blocks(W, blocks_n)
    return _WB[key]

def effects_sdm(rho, beta, theta, W, blocks_n, ndraw=0, V=None):
    """Average direct/indirect/total effects of ln GACI for y = rho W y + beta G + theta W G.
    Computed per year block and averaged (weighted by block size)."""
    WB = get_blocks(W, blocks_n)
    def one(r, b, t):
        d_sum = 0.0; tot_sum = 0.0; cnt = 0
        for Wt in WB:
            nb = Wt.shape[0]
            S = np.linalg.solve(np.eye(nb) - r * Wt, b * np.eye(nb) + t * Wt)
            d_sum += np.trace(S); tot_sum += S.sum(); cnt += nb
        d = d_sum / cnt; tot = tot_sum / cnt
        return d, tot - d, tot
    est = one(rho, beta, theta)
    if ndraw and V is not None:
        draws = rng.multivariate_normal([rho, beta, theta], V, size=ndraw)
        draws[:, 0] = np.clip(draws[:, 0], -0.98, 0.98)
        sims = np.array([one(*dr) for dr in draws])
        return est, sims.std(0)
    return est, (np.nan, np.nan, np.nan)

def num_hessian(f, x, eps=1e-4):
    k = len(x); Hm = np.zeros((k, k))
    for i in range(k):
        for j in range(i, k):
            xpp = x.copy(); xpp[i] += eps; xpp[j] += eps
            xpm = x.copy(); xpm[i] += eps; xpm[j] -= eps
            xmp = x.copy(); xmp[i] -= eps; xmp[j] += eps
            xmm = x.copy(); xmm[i] -= eps; xmm[j] -= eps
            Hm[i, j] = Hm[j, i] = (f(xpp) - f(xpm) - f(xmp) + f(xmm)) / (4 * eps * eps)
    return Hm

def logdet_blocks(rho, W, blocks_n):
    ld = 0.0
    for Wt in get_blocks(W, blocks_n):
        sign, l = np.linalg.slogdet(np.eye(Wt.shape[0]) - rho * Wt)
        ld += l
    return ld

def ml_spatial(y, X, W, blocks_n, kind):
    """ML for SAR ('sar') or SEM ('sem') on within-transformed data.
    Returns dict with rho/lambda, beta, se (from numerical Hessian)."""
    N = len(y); k = X.shape[1]
    Wy = W @ y; WX = W @ X
    def negll(p):
        r = p[0]; b = p[1:1 + k]; ls2 = p[1 + k]
        s2 = np.exp(ls2)
        if kind == "sar":
            e = y - r * Wy - X @ b
        else:
            e = (y - r * Wy) - (X - r * WX) @ b
        return -(logdet_blocks(r, W, blocks_n) - N / 2 * np.log(2 * np.pi * s2) - e @ e / (2 * s2))
    def conc(r):
        if kind == "sar":
            b, e = ols(y - r * Wy, X)
        else:
            b, e = ols(y - r * Wy, X - r * WX)
        s2 = e @ e / N
        return -(logdet_blocks(r, W, blocks_n) - N / 2 * np.log(2 * np.pi * s2) - N / 2), b, s2
    res = optimize.minimize_scalar(lambda r: conc(r)[0], bounds=(-0.95, 0.95), method="bounded")
    r = res.x; _, b, s2 = conc(r)
    p = np.concatenate([[r], b, [np.log(s2)]])
    Hm = num_hessian(negll, p, eps=1e-4)
    V = np.linalg.inv(Hm)
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    return {"rho": r, "b": b, "se_rho": se[0], "se_b": se[1:1 + k], "V": V, "s2": s2}

# ---------------------------------------------------------------- run
OUTCOMES = {"ln_co2_tot": "Bunker CO2", "ln_co2_intl": "Intl. CO2", "ln_intensity": "Intensity"}
WMATS = {"contig": ("Contiguity (land border)", C), "inv": ("Inverse distance", Winv)}
rows = []
def add(w, outc, model, est, term, b, se_cl, se_rob=np.nan, extra=None):
    r = {"W": w, "outcome": outc, "model": model, "estimator": est, "term": term,
         "b": b, "se_cl": se_cl, "se_rob": se_rob, "N": len(df)}
    if extra: r.update(extra)
    rows.append(r)

blocks_n = [len(g) for _, g in df.groupby("y", sort=True)]
G_raw = df["ln_gaci_cwm"].values
Z_raw = df["feyrer_int"].values
X_raw = df[["lnpop", "ln_sea_ma"]].values

for wkey, (wname, Wfull) in WMATS.items():
    W = build_block_W(Wfull)
    WG_raw = W @ G_raw; WZ_raw = W @ Z_raw; WWZ_raw = W @ WZ_raw
    WX_raw = W @ X_raw; WWX_raw = W @ WX_raw
    G = demean(G_raw); Z = demean(Z_raw); X = demean(X_raw)
    WG = demean(WG_raw); WZ = demean(WZ_raw); WWZ = demean(WWZ_raw)
    WX = demean(WX_raw); WWX = demean(WWX_raw)
    for ykey, yname in OUTCOMES.items():
        y_raw = df[ykey].values.astype(float)
        ok = ~np.isnan(y_raw)
        if not ok.all():
            # ln_co2_intl has one missing value in the Stata sample too; impute by within mean for W y only
            y_raw = np.where(ok, y_raw, np.nanmean(y_raw))
        Wy_raw = W @ y_raw; WWy_raw = W @ Wy_raw
        y = demean(y_raw); Wy = demean(Wy_raw)
        print(f"\n===== W={wkey}  outcome={ykey}")
        # ---------- Panel A: non-instrumented (OLS / ML) ----------
        # OLS-FE
        Xa = np.column_stack([G, X]); b, u = ols(y, Xa)
        bi = np.linalg.inv(Xa.T @ Xa)
        sec = np.sqrt(np.diag(cluster_vcov(Xa, u, bi, clus))); ser = np.sqrt(np.diag(robust_vcov(Xa, u, bi)))
        add(wkey, ykey, "OLS", "FE", "beta", b[0], sec[0], ser[0])
        # SLX
        Xa = np.column_stack([G, WG, X]); b, u = ols(y, Xa)
        bi = np.linalg.inv(Xa.T @ Xa)
        sec = np.sqrt(np.diag(cluster_vcov(Xa, u, bi, clus))); ser = np.sqrt(np.diag(robust_vcov(Xa, u, bi)))
        add(wkey, ykey, "SLX", "FE", "beta", b[0], sec[0], ser[0])
        add(wkey, ykey, "SLX", "FE", "theta", b[1], sec[1], ser[1])
        # SAR (ML)
        Xa = np.column_stack([G, X]); m = ml_spatial(y, Xa, W, blocks_n, "sar")
        add(wkey, ykey, "SAR", "ML", "rho", m["rho"], m["se_rho"])
        add(wkey, ykey, "SAR", "ML", "beta", m["b"][0], m["se_b"][0])
        V3 = np.zeros((3, 3)); V3[0, 0] = m["V"][0, 0]; V3[1, 1] = m["V"][1, 1]; V3[0, 1] = V3[1, 0] = m["V"][0, 1]
        (d, ind, tot), (sd, sind, stot) = effects_sdm(m["rho"], m["b"][0], 0.0, W, blocks_n, 100, V3)
        add(wkey, ykey, "SAR", "ML", "direct", d, sd); add(wkey, ykey, "SAR", "ML", "indirect", ind, sind); add(wkey, ykey, "SAR", "ML", "total", tot, stot)
        # SEM (ML)
        m = ml_spatial(y, Xa, W, blocks_n, "sem")
        add(wkey, ykey, "SEM", "ML", "lambda", m["rho"], m["se_rho"])
        add(wkey, ykey, "SEM", "ML", "beta", m["b"][0], m["se_b"][0])
        # SDM (ML)
        Xa = np.column_stack([G, WG, X]); m = ml_spatial(y, Xa, W, blocks_n, "sar")
        add(wkey, ykey, "SDM", "ML", "rho", m["rho"], m["se_rho"])
        add(wkey, ykey, "SDM", "ML", "beta", m["b"][0], m["se_b"][0])
        add(wkey, ykey, "SDM", "ML", "theta", m["b"][1], m["se_b"][1])
        V3 = m["V"][:3, :3]
        (d, ind, tot), (sd, sind, stot) = effects_sdm(m["rho"], m["b"][0], m["b"][1], W, blocks_n, 100, V3)
        add(wkey, ykey, "SDM", "ML", "direct", d, sd); add(wkey, ykey, "SDM", "ML", "indirect", ind, sind); add(wkey, ykey, "SDM", "ML", "total", tot, stot)
        # SDEM (ML): SLX regressors with spatial error
        m = ml_spatial(y, Xa, W, blocks_n, "sem")
        add(wkey, ykey, "SDEM", "ML", "lambda", m["rho"], m["se_rho"])
        add(wkey, ykey, "SDEM", "ML", "beta", m["b"][0], m["se_b"][0])
        add(wkey, ykey, "SDEM", "ML", "theta", m["b"][1], m["se_b"][1])
        print("  panel A done")

        # ---------- Panel B: instrumented (Feyrer shifter) ----------
        # 2SLS baseline
        b, sc, sr, u, swf = tsls(y, G[:, None], X, Z[:, None], clus)
        add(wkey, ykey, "2SLS", "IV", "beta", b[0], sc[0], sr[0], {"swf_beta": swf[0]})
        print(f"  2SLS beta {b[0]:.3f} ({sc[0]:.3f}) F {swf[0]:.1f}")
        # SLX-IV: G and WG instrumented by Z, WZ
        Xend = np.column_stack([G, WG]); H = np.column_stack([Z, WZ])
        b, sc, sr, u, swf = tsls(y, Xend, X, H, clus)
        add(wkey, ykey, "SLX", "IV", "beta", b[0], sc[0], sr[0], {"swf_beta": swf[0], "swf_theta": swf[1]})
        add(wkey, ykey, "SLX", "IV", "theta", b[1], sc[1], sr[1])
        print(f"  SLX-IV beta {b[0]:.3f} ({sc[0]:.3f}) theta {b[1]:.3f} ({sc[1]:.3f}) SW F {swf[0]:.1f}/{swf[1]:.1f}")
        # SAR-IV (GS2SLS): Wy, G endogenous; instruments Z, WZ, W2Z, WX, W2X
        Xend = np.column_stack([Wy, G]); H = np.column_stack([Z, WZ, WWZ, WX, WWX])
        b, sc, sr, u, swf = tsls(y, Xend, X, H, clus)
        add(wkey, ykey, "SAR", "IV", "rho", b[0], sc[0], sr[0], {"swf_rho": swf[0]})
        add(wkey, ykey, "SAR", "IV", "beta", b[1], sc[1], sr[1], {"swf_beta": swf[1]})
        # effects with cluster vcov for (rho, beta)
        Xf = np.column_stack([Xend, X]); Zf = np.column_stack([H, X])
        PZ = Zf @ np.linalg.solve(Zf.T @ Zf, Zf.T @ Xf); bi = np.linalg.inv(PZ.T @ Xf)
        Vc = cluster_vcov(PZ, u, bi, clus)
        V3 = np.zeros((3, 3)); V3[:2, :2] = Vc[:2, :2]
        (d, ind, tot), (sd, sind, stot) = effects_sdm(b[0], b[1], 0.0, W, blocks_n, 100, V3)
        add(wkey, ykey, "SAR", "IV", "direct", d, sd); add(wkey, ykey, "SAR", "IV", "indirect", ind, sind); add(wkey, ykey, "SAR", "IV", "total", tot, stot)
        print(f"  SAR-IV rho {b[0]:.3f} ({sc[0]:.3f}) beta {b[1]:.3f} ({sc[1]:.3f}) total {tot:.3f}")
        # SDM-IV: Wy, G, WG endogenous; instruments Z, WZ, W2Z, WX, W2X
        Xend = np.column_stack([Wy, G, WG]); H = np.column_stack([Z, WZ, WWZ, WX, WWX])
        b, sc, sr, u, swf = tsls(y, Xend, X, H, clus)
        add(wkey, ykey, "SDM", "IV", "rho", b[0], sc[0], sr[0], {"swf_rho": swf[0]})
        add(wkey, ykey, "SDM", "IV", "beta", b[1], sc[1], sr[1], {"swf_beta": swf[1]})
        add(wkey, ykey, "SDM", "IV", "theta", b[2], sc[2], sr[2], {"swf_theta": swf[2]})
        Xf = np.column_stack([Xend, X]); Zf = np.column_stack([H, X])
        PZ = Zf @ np.linalg.solve(Zf.T @ Zf, Zf.T @ Xf); bi = np.linalg.inv(PZ.T @ Xf)
        Vc = cluster_vcov(PZ, u, bi, clus)
        (d, ind, tot), (sd, sind, stot) = effects_sdm(b[0], b[1], b[2], W, blocks_n, 100, Vc[:3, :3])
        add(wkey, ykey, "SDM", "IV", "direct", d, sd); add(wkey, ykey, "SDM", "IV", "indirect", ind, sind); add(wkey, ykey, "SDM", "IV", "total", tot, stot)
        print(f"  SDM-IV rho {b[0]:.3f} ({sc[0]:.3f}) beta {b[1]:.3f} ({sc[1]:.3f}) theta {b[2]:.3f} ({sc[2]:.3f}) direct {d:.2f} indirect {ind:.2f} total {tot:.2f}")
        # SEM-IV: 2SLS residuals -> KP lambda -> Cochrane-Orcutt -> 2SLS
        b0, _, _, u0, _ = tsls(y, G[:, None], X, Z[:, None], clus)
        lam = kp_lambda(u0, W)
        ys = y - lam * Wy; Gs = G - lam * WG; Xs = X - lam * WX
        b, sc, sr, u, swf = tsls(ys, Gs[:, None], Xs, np.column_stack([Z, WZ]), clus)
        add(wkey, ykey, "SEM", "IV", "lambda", lam, np.nan)
        add(wkey, ykey, "SEM", "IV", "beta", b[0], sc[0], sr[0], {"swf_beta": swf[0]})
        print(f"  SEM-IV lambda {lam:.3f} beta {b[0]:.3f} ({sc[0]:.3f})")
        # SDEM-IV: SLX-IV residuals -> lambda -> transform
        Xend = np.column_stack([G, WG]); H = np.column_stack([Z, WZ])
        b0, _, _, u0, _ = tsls(y, Xend, X, H, clus)
        lam = kp_lambda(u0, W)
        WWG = demean(W @ WG_raw)
        ys = y - lam * Wy; Xends = np.column_stack([G - lam * WG, WG - lam * WWG]); Xs = X - lam * WX
        b, sc, sr, u, swf = tsls(ys, Xends, Xs, np.column_stack([Z, WZ, WWZ]), clus)
        add(wkey, ykey, "SDEM", "IV", "lambda", lam, np.nan)
        add(wkey, ykey, "SDEM", "IV", "beta", b[0], sc[0], sr[0], {"swf_beta": swf[0]})
        add(wkey, ykey, "SDEM", "IV", "theta", b[1], sc[1], sr[1], {"swf_theta": swf[1]})
        print(f"  SDEM-IV lambda {lam:.3f} beta {b[0]:.3f} ({sc[0]:.3f}) theta {b[1]:.3f} ({sc[1]:.3f})")

res = pd.DataFrame(rows)
res.to_csv(os.path.join(HERE, "_spatial_models.csv"), index=False)
print("\nsaved _spatial_models.csv", res.shape)
