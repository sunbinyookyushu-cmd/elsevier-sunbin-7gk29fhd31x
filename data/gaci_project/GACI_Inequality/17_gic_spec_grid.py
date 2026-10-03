# -*- coding: utf-8 -*-
"""17_gic_spec_grid.py : specification grid for the incidence curve, mirroring the CO2 paper's design choices.
   No behavioural controls. Varies only: treatment (GACI_max vs capacity-weighted mean), the CO2-paper design
   control ln sea MA (in/out), fixed effects (country+year; country + continent x year), and inference
   (country cluster; two-way country+year; Conley 1000/2000 km with uniform lags; Driscoll-Kraay lag 5).
   2SLS with the Feyrer instrument throughout. Outcomes: ln avg pretax income of each WID group, relative income
   (= share identity), two contrasts (p90-100 minus bottom 50; top half minus bottom half), and the two Gini series.
   Output: _gic_spec_grid.csv and a printed scorecard."""
import os, csv, json, collections, numpy as np, pandas as pd, geopandas as gpd
from scipy import stats

D_ = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D_, "..")
d = pd.read_csv(os.path.join(D_, "ineq_panel_ext.csv"), low_memory=False)
d = d.dropna(subset=["gini_mkt", "ln_gaci_max", "ln_gaci_cwm", "feyrer_int", "lnpop", "ln_sea_ma"]).copy()
d["cont"] = d.reg.str[:2]
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01", "b50", "all"]
for g in G[:-1]:
    d["rel_" + g] = d["ln_apt_" + g] - d["ln_apt_all"]
d["gap_d10_b50"] = d["ln_apt_d10"] - d["ln_apt_b50"]
d["gap_top_bot"] = d[["ln_apt_d%d" % i for i in range(6, 11)]].mean(axis=1) - d[["ln_apt_d%d" % i for i in range(1, 6)]].mean(axis=1)

# ---- coordinates (Natural Earth + airport fallback) ----
w = gpd.read_file(os.path.join(P, "_world.geojson")); w["iso3"] = w["ISO_A3_EH"].where(w["ISO_A3_EH"] != "-99", w["ADM0_A3"])
cen = w.dissolve(by="iso3").geometry.representative_point(); coords = pd.DataFrame({"lat": cen.y, "lon": cen.x})
ap = {r["Airport"]: (float(r["lat"]), float(r["lon"])) for r in csv.DictReader(open(os.path.join(P, "airport_coords_merged.csv"), encoding="utf-8"))}
ap_iso2 = {}
for r in csv.DictReader(open(os.path.join(P, "ourairports.csv"), encoding="utf-8", errors="replace")):
    ia = (r.get("iata_code") or "").strip()
    if len(ia) == 3: ap_iso2[ia] = r.get("iso_country", "").strip()
iso2to3 = json.load(open(os.path.join(P, "iso2to3.json"))); cl = collections.defaultdict(list)
for a, (la, lo) in ap.items():
    i3 = iso2to3.get(ap_iso2.get(a, ""), "")
    if i3: cl[i3].append((la, lo))
miss = sorted(set(d.c) - set(coords.index)); fb = {c: (np.mean([x[0] for x in cl[c]]), np.mean([x[1] for x in cl[c]])) for c in miss if c in cl}
coords = pd.concat([coords, pd.DataFrame(fb, index=["lat", "lon"]).T]); d = d[d.c.isin(coords.index)].copy()

def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2); dp, dl = p2 - p1, np.radians(lon2 - lon1)
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2))

def demean(M, groups, tol=1e-11, maxit=5000):
    M = M.astype(float).copy()
    for _ in range(maxit):
        M0 = M.copy()
        for ids in groups:
            M = M - pd.DataFrame(M).groupby(ids).transform("mean").values
        if np.max(np.abs(M - M0)) < tol: break
    return M

def estimate(s, yv, xv, ctrl, fe_groups, se_list):
    cid = s.c.astype("category").cat.codes.values.astype(np.int64); tid = s.y.astype(np.int64).values
    cont = s.cont.astype("category").cat.codes.values.astype(np.int64)
    groups = [cid, tid] if fe_groups == "c+y" else [cid, cont * 10000 + tid]
    yy = demean(s[[yv]].values, groups)[:, 0]
    X = demean(s[[xv] + ctrl].values, groups); Z = demean(s[["feyrer_int"] + ctrl].values, groups)
    N, K = X.shape; Gn = len(np.unique(cid)); Tn = len(np.unique(tid))
    # first-stage F (cluster) for the excluded instrument
    Pz = np.linalg.solve(Z.T @ Z, Z.T @ X[:, [0]]); u = X[:, [0]] - Z @ Pz
    Az = np.linalg.inv(Z.T @ Z); Gz = Z * u; meat = np.zeros((Z.shape[1], Z.shape[1]))
    for g in np.unique(cid):
        m = cid == g; sg = Gz[m].sum(0); meat += np.outer(sg, sg)
    Vz = Az @ meat @ Az * (Gn / (Gn - 1)); F = float(Pz[0, 0] ** 2 / Vz[0, 0])
    Xh = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X); A = np.linalg.inv(Xh.T @ X); b = A @ (Xh.T @ yy); e = yy - X @ b
    Gm = Xh * e[:, None]
    same_c = cid[:, None] == cid[None, :]; same_t = tid[:, None] == tid[None, :]
    cc = s.c.astype("category").cat.categories; la = coords.loc[cc, "lat"].values; lo = coords.loc[cc, "lon"].values
    Dc = haversine(la[:, None], lo[:, None], la[None, :], lo[None, :]); Dobs = Dc[cid][:, cid]; dT = np.abs(tid[:, None] - tid[None, :])
    out = {}
    for se in se_list:
        if se == "cluster_c":
            Wm = same_c.astype(float); adj = (Gn / (Gn - 1)) * ((N - 1) / (N - K - (Gn - 1) - (Tn - 1)))
        elif se == "twoway_cy":
            Wm = same_c.astype(float) + same_t.astype(float) - (same_c & same_t).astype(float); adj = 1.0
        elif se.startswith("conley"):
            Dk = float(se.split("_")[1]); Wm = np.clip(1 - Dobs / Dk, 0, 1); Wm[same_c] = 1.0; adj = 1.0
        elif se == "dk5":
            Wm = np.clip(1 - dT / 6.0, 0, 1); adj = 1.0
        V = A @ (Gm.T @ (Wm @ Gm)) @ A.T * adj
        sev = float(np.sqrt(V[0, 0])); out[se] = (float(b[0]), sev, float(2 * (1 - stats.norm.cdf(abs(b[0] / sev)))))
    return out, F, N

SES = ["cluster_c", "twoway_cy", "conley_1000", "conley_2000", "dk5"]
OUTS = ["ln_gini_mkt", "ln_gini_disp"] + ["ln_apt_" + g for g in G] + ["rel_" + g for g in G[:-1]] + ["gap_d10_b50", "gap_top_bot"]
rows = []
for xv in ["ln_gaci_max", "ln_gaci_cwm"]:
    for ctrl_lab, ctrl in [("pop", ["lnpop"]), ("pop+seaMA", ["lnpop", "ln_sea_ma"])]:
        for fe in ["c+y", "c+cont#y"]:
            for yv in OUTS:
                s = d.dropna(subset=[yv])
                res, F, N = estimate(s, yv, xv, ctrl, fe, SES)
                for se, (b, sev, p) in res.items():
                    rows.append({"treat": xv, "ctrl": ctrl_lab, "fe": fe, "outcome": yv, "se": se, "b": b, "se_v": sev, "p": p, "F": F, "N": N})
            print("done", xv, ctrl_lab, fe, "F=%.1f" % F, flush=True)
R = pd.DataFrame(rows); R.to_csv(os.path.join(D_, "_gic_spec_grid.csv"), index=False)

# ---- scorecard ----
def st(p): return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""
print("\nSCORECARD  (2SLS Feyrer). cols: headline mkt Gini | top groups sig (of d7-d10,t1) | bottom-half shares sig (of d1-d5,b50) | d10-b50 | tophalf-bothalf | F")
for (xv, cl_, fe, se), x in R.groupby(["treat", "ctrl", "fe", "se"], sort=False):
    x = x.set_index("outcome")
    h = x.loc["ln_gini_mkt"]; F = h.F
    top = sum(x.loc["ln_apt_" + g].p < .1 for g in ["d7", "d8", "d9", "d10", "t1"])
    bot = sum(x.loc["rel_" + g].p < .1 for g in ["d1", "d2", "d3", "d4", "d5", "b50"])
    g1 = x.loc["gap_d10_b50"]; g2 = x.loc["gap_top_bot"]
    print(f"{xv[-3:]:3s} {cl_:9s} {fe:8s} {se:11s} | {h.b:5.2f} ({h.se_v:.2f}){st(h.p):3s} | top {top}/5 | bot {bot}/6 | {g1.b:5.2f} ({g1.se_v:.2f}){st(g1.p):3s} | {g2.b:5.2f} ({g2.se_v:.2f}){st(g2.p):3s} | F={F:4.1f}")
