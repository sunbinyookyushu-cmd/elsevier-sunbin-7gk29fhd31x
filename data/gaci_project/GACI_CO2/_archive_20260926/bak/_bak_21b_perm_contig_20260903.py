# -*- coding: utf-8 -*-
"""
21b_perm_contig.py   (2026-09-03)
Permutation placebo for the contiguity- and knn5-based spillover specifications:
relabel countries at random (permute rows/cols of W), rebuild the neighbour
exposures, re-estimate the joint-IV specification
   ln_co2 ~ lnpop + ln_sea_ma + has_contig | c + y | (ln_gaci, nbr_g) ~ (feyrer_int, nbr_f)
and record the neighbour coefficient, its t, and the reduced-form t. 500 draws.
Output: _spill_placebo_perm_W.csv, CO2_spill_placebo.png
"""
import os, sys, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import pycountry
import pyfixest as pf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"], "font.size": 11})
ACC, GRAY, INK = "#1F4E79", "#9AA0A6", "#1f1f1f"

sb = pd.read_csv(os.path.join(HERE, "spillover_bands.csv"))
panel = pd.read_csv(os.path.join(HERE, "..", "gaci_panel_combined.csv"), usecols=["c", "y", "ln_gaci_cwm", "feyrer_int", "lnpop", "ln_sea_ma"])
co2 = pd.read_csv(os.path.join(HERE, "co2_country_year.csv"), usecols=["iso3", "year", "co2_bunker"]).rename(columns={"iso3": "c", "year": "y"})
co2["ln_co2_tot"] = np.log(co2["co2_bunker"].where(co2["co2_bunker"] > 0))
base = panel.merge(co2[["c", "y", "ln_co2_tot"]], on=["c", "y"]).merge(sb[["c", "y", "has_contig", "nbr_g_contig", "nbr_f_contig", "nbr_g_knn5", "nbr_f_knn5"]], on=["c", "y"])
base = base.dropna(subset=["ln_co2_tot", "ln_gaci_cwm", "feyrer_int", "lnpop", "ln_sea_ma"]).copy()
countries = sorted(base["c"].unique()); n = len(countries); idx = {c: i for i, c in enumerate(countries)}

# rebuild W matrices exactly as in 21 (contiguity from Natural Earth; knn5 from centroids)
ALIAS = {"Russia": "RUS", "Iran": "IRN", "Venezuela": "VEN", "Bolivia": "BOL", "Tanzania": "TZA", "Syria": "SYR", "Laos": "LAO", "Vietnam": "VNM",
         "South Korea": "KOR", "North Korea": "PRK", "Moldova": "MDA", "Democratic Republic of the Congo": "COD", "Republic of the Congo": "COG",
         "Ivory Coast": "CIV", "Cape Verde": "CPV", "Brunei": "BRN", "Micronesia": "FSM", "Macedonia": "MKD", "Czech Republic": "CZE", "Burma": "MMR",
         "East Timor": "TLS", "Palestine": "PSE", "Taiwan": "TWN", "Hong Kong": "HKG", "Macau": "MAC", "Turkey": "TUR", "United States": "USA", "United Kingdom": "GBR"}
def to_iso3(name, cache={}):
    if name in cache: return cache[name]
    iso = ALIAS.get(name)
    if iso is None:
        try: iso = pycountry.countries.lookup(name).alpha_3
        except LookupError:
            try: iso = pycountry.countries.search_fuzzy(name)[0].alpha_3
            except LookupError: iso = None
    cache[name] = iso; return iso
ap = pd.read_csv(os.path.join(HERE, "..", "airport_coords_merged.csv")); ap["c"] = ap["country"].astype(str).map(to_iso3)
cent = ap.dropna(subset=["c"]).groupby("c")[["lat", "lon"]].mean().reindex(countries)
lat = np.radians(cent["lat"].values); lon = np.radians(cent["lon"].values)
h = np.sin((lat[:, None] - lat[None, :]) / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin((lon[:, None] - lon[None, :]) / 2) ** 2
D = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(h, 0, 1))); np.fill_diagonal(D, np.inf)
ne = gpd.read_file(os.path.join(HERE, "data_external", "ne_50m_admin_0.geojson"))
ne["iso"] = ne["ISO_A3_EH"].where(ne["ISO_A3_EH"] != "-99", ne["ADM0_A3"])
ne = ne[ne["iso"].isin(countries)].dissolve(by="iso"); ne["geometry"] = ne.geometry.buffer(0)
C = np.zeros((n, n)); isos = list(ne.index); sidx = ne.sindex
for a in isos:
    for j in sidx.query(ne.loc[a, "geometry"], predicate="intersects"):
        b = isos[j]
        if b != a: C[idx[a], idx[b]] = 1.0; C[idx[b], idx[a]] = 1.0
K = np.zeros((n, n))
for i in range(n):
    K[i, np.argsort(D[i])[:5]] = 1.0
mats = {"contig": C, "knn5": K}

def rownorm(W):
    rs = W.sum(axis=1, keepdims=True); return np.divide(W, rs, out=np.zeros_like(W), where=rs > 0)
def exposures(W, v):
    ok = ~np.isnan(v); Wy = rownorm(W[:, ok]); out = Wy @ v[ok]; out[W[:, ok].sum(axis=1) == 0] = np.nan; return out
pan_by_y = {y: g.set_index("c") for y, g in base.groupby("y")}
def build(W):
    recs = []
    for y, g in pan_by_y.items():
        vg = np.full(n, np.nan); vf = np.full(n, np.nan)
        for c in g.index:
            vg[idx[c]] = g.loc[c, "ln_gaci_cwm"]; vf[idx[c]] = g.loc[c, "feyrer_int"]
        eg = exposures(W, vg); ef = exposures(W, vf)
        for c in g.index:
            recs.append((c, y, eg[idx[c]], ef[idx[c]]))
    d = pd.DataFrame(recs, columns=["c", "y", "pg", "pfv"])
    d["hasw"] = d["pg"].notna().astype(int); d["pg"] = d["pg"].fillna(0.0); d["pfv"] = d["pfv"].fillna(0.0)
    return d

def fe_resid(dd, cols):
    out = {}
    for col in cols:
        out[col] = np.asarray(pf.feols(f"{col} ~ 1 | c + y", data=dd).resid())
    return out
def est(dd):
    # joint 2SLS with two endogenous regressors after two-way FE residualisation; robust SE
    dd = dd.dropna(subset=["ln_co2_tot", "ln_gaci_cwm", "pg", "feyrer_int", "pfv", "lnpop", "ln_sea_ma", "hasw"]).copy()
    R = fe_resid(dd, ["ln_co2_tot", "ln_gaci_cwm", "pg", "feyrer_int", "pfv", "lnpop", "ln_sea_ma", "hasw"])
    y = R["ln_co2_tot"]
    ctrl = [R["lnpop"], R["ln_sea_ma"]]
    if dd["hasw"].nunique() > 1:
        ctrl.append(R["hasw"])
    X = np.column_stack([R["ln_gaci_cwm"], R["pg"]] + ctrl)
    Z = np.column_stack([R["feyrer_int"], R["pfv"]] + ctrl)
    Xh = Z @ np.linalg.lstsq(Z, X, rcond=None)[0]
    XtX = Xh.T @ Xh
    beta = np.linalg.solve(XtX, Xh.T @ y)
    e = y - X @ beta
    meat = (Xh * e[:, None]).T @ (Xh * e[:, None])
    V = np.linalg.solve(XtX, np.linalg.solve(XtX, meat).T)
    b, t = beta[1], beta[1] / np.sqrt(V[1, 1])
    fml = "ln_co2_tot ~ pfv + feyrer_int + lnpop + ln_sea_ma" + (" + hasw" if dd["hasw"].nunique() > 1 else "") + " | c + y"
    r = pf.feols(fml, data=dd, vcov="hetero")
    return float(b), float(t), float(r.coef()["pfv"]), float(r.tstat()["pfv"])

rng = np.random.default_rng(20260903)
NPERM = 500
allres = []
summary = {}
for nm, W in mats.items():
    d0 = build(W); dd = base.merge(d0, on=["c", "y"])
    b0, t0, rb0, rt0 = est(dd)
    print(f"{nm}: actual joint-IV nbr b = {b0:.3f} (t {t0:.2f}); RF b = {rb0:.3f} (t {rt0:.2f})")
    for k in range(NPERM):
        perm = rng.permutation(n); Wp = W[perm, :][:, perm]
        dp = build(Wp); dq = base.merge(dp, on=["c", "y"])
        try:
            b, t, rb, rt = est(dq)
        except Exception:
            b, t, rb, rt = np.nan, np.nan, np.nan, np.nan
        allres.append({"W": nm, "draw": k, "b": b, "t": t, "rf_b": rb, "rf_t": rt})
        if k % 100 == 0: print(nm, "perm", k)
    r = pd.DataFrame([x for x in allres if x["W"] == nm])
    p_t = float((r["t"].abs() >= abs(t0)).mean()); p_rt = float((r["rf_t"].abs() >= abs(rt0)).mean()); p_b = float((r["b"].abs() >= abs(b0)).mean())
    summary[nm] = dict(b_actual=b0, t_actual=t0, rf_b_actual=rb0, rf_t_actual=rt0, p_perm_t=p_t, p_perm_rf_t=p_rt, p_perm_b=p_b,
                       perm_t_sd=float(r["t"].std()), perm_b_sd=float(r["b"].std()), n_ok=int(r["b"].notna().sum()))
    print(f"{nm}: permutation p (|t|) = {p_t:.3f}; p (|RF t|) = {p_rt:.3f}; p (|b|) = {p_b:.3f}; sd(t_perm) = {r['t'].std():.2f}")
pd.DataFrame(allres).to_csv(os.path.join(HERE, "_spill_placebo_perm_W.csv"), index=False)
pd.DataFrame(summary).T.to_csv(os.path.join(HERE, "_spill_placebo_summary.csv"))

# figure: distributions of permuted t with actual
res = pd.DataFrame(allres)
inv = pd.read_csv(os.path.join(HERE, "_spill_placebo_perm.csv"))
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
panels = [("Inverse distance (reduced form)", inv["rf_t"].dropna(), float(inv["rft_actual"].iloc[0])),
          ("Contiguity (joint IV)", res[res.W == "contig"]["t"].dropna(), summary["contig"]["t_actual"]),
          ("Five nearest (joint IV)", res[res.W == "knn5"]["t"].dropna(), summary["knn5"]["t_actual"])]
for ax, (ttl, s, act) in zip(axes, panels):
    ax.hist(s, bins=30, color=GRAY, edgecolor="white", linewidth=0.5)
    ax.axvline(act, color=ACC, lw=2)
    p = float((s.abs() >= abs(act)).mean())
    ax.set_title(ttl, fontsize=11, loc="left")
    ax.text(0.02, 0.95, f"actual t = {act:.2f}\npermutation p = {p:.3f}", transform=ax.transAxes, va="top", fontsize=9.5, color=INK)
    ax.set_xlabel("t-statistic on neighbour term, permuted W"); ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("Draws (500)")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "CO2_spill_placebo.png"), dpi=200); plt.close(fig)
print("saved CO2_spill_placebo.png")
print("DONE_21b")
