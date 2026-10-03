# -*- coding: utf-8 -*-
"""
reestimate_all.py -- Python re-estimation of every regression table in the TRA manuscript,
for three samples, so the 1996-2023 (paper) and 1996-2024 (extended) results can be compared.

  A  paper     : original panels in ../ (gaci_panel_3iv / combined / mechanism / measures), 1996-2023
  B  rebuilt23 : ext2024 panels restricted to y<=2023 (adds 16 land-backfilled rows: BEL/LUX/SDN 1996-2011)
  C  ext24     : ext2024 panels, 1996-2024 (adds 155 country-years for 2024; endowments as of 2024)

Specs follow the do-files 1:1: country + year FE (absorb), robust (HC1) SEs, lnpop control,
treatment ln_gaci_cwm, instrument tourism_int = tour_shift x ln(1+natural/mixed heritage stock).
Point estimates/SEs via pyfixest (validated: reproduces Table 1 exactly). KP F, Hansen J, SW F
computed on two-way-demeaned data with numpy.
Output: _reest_<label>.json  (+ printed summary)
"""
import sys, json, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import pyfixest as pf

label, pdir, ymax = sys.argv[1], sys.argv[2], int(sys.argv[3])

# ------------------------------------------------------------------ data
def load(name):
    d = pd.read_csv(f"{pdir}/{name}")
    d = d[d.y <= ymax].copy()
    d["g_int"] = d["merch_intensity"]; d["g_vol"] = d["merch_intensity"] + d["lngdp"]; d["g_gdp"] = d["lngdp"]
    d["g_shr"] = d["merch_share"]
    return d
M = load("gaci_panel_3iv.csv")
CB = load("gaci_panel_combined.csv")
ME = load("gaci_panel_mechanism.csv")
MS = load("gaci_panel_measures.csv")
MS["ln_gaci_sum"] = MS["lnG"]
# mechanism outcomes (gaci_mechanism.do)
ME["r_vw"] = ME.ln_tr_hivw - ME.ln_tr_lovw; ME["sh_hivw"] = ME.tr_hivw / ME.tr_total * 100
ME["r_bec"] = ME.ln_tr_interm - ME.ln_tr_consum; ME["sh_bec"] = ME.tr_interm / (ME.tr_interm + ME.tr_consum) * 100
ME["xr_vw"] = ME.ln_x_hivw3 - ME.ln_x_lovw3; ME["xsh_hivw"] = ME.x_hivw3 / (ME.x_hivw3 + ME.x_lovw3) * 100
ME["lntot"] = ME.ln_tr_total
# moderators (gaci_hetero_table.do): 1996 baseline, centred at the row mean
for d in (M,):
    b = d[d.y == 1996].groupby("c")[["lnpc", "ln_gaci_cwm"]].max()
    d["base_lnpc"] = d.c.map(b.lnpc); d["base_cwm"] = d.c.map(b.ln_gaci_cwm)
    d["inc_c"] = d.base_lnpc - d.base_lnpc.mean(); d["con_c"] = d.base_cwm - d.base_cwm.mean()
    d["rem_c"] = d.ln_remote - d.ln_remote.mean()
    d["post"] = (d.y >= 2010).astype(int)
    for tag, mod in [("inc", "inc_c"), ("con", "con_c"), ("rem", "rem_c"), ("post", "post")]:
        d[f"cwm_{tag}"] = d.ln_gaci_cwm * d[mod]; d[f"z_{tag}"] = d.tourism_int * d[mod]

# ------------------------------------------------------------------ helpers
def demean(df, cols, tol=1e-11, maxit=500):
    X = df[cols].astype(float).to_numpy().copy()
    gc = df["c"].to_numpy(); gy = df["y"].to_numpy()
    for _ in range(maxit):
        X0 = X.copy()
        for g in (gc, gy):
            m = pd.DataFrame(X).groupby(g).transform("mean").to_numpy(); X = X - m
        if np.abs(X - X0).max() < tol: break
    return X

def robust_cov(X, u, adj=True):
    XtXi = np.linalg.inv(X.T @ X); V = XtXi @ (X * (u**2)[:, None]).T @ X @ XtXi
    n, k = X.shape
    return V * (n / (n - k) if adj else 1.0)

def kp_F(df, endog, insts, exog):
    """1 endog: robust Wald F of excluded instruments in the first stage (= KP rk Wald F).
       2 endog: Sanderson-Windmeijer conditional F for the first endogenous variable."""
    cols = list(dict.fromkeys(endog + insts + exog)); sub = df.dropna(subset=cols)
    Z = demean(sub, cols); idx = {c: i for i, c in enumerate(cols)}
    zi = [idx[c] for c in insts]; xi = [idx[c] for c in exog]
    L = len(insts)
    if len(endog) == 1:
        Xf = Z[:, zi + xi]; yv = Z[:, idx[endog[0]]]
        b = np.linalg.lstsq(Xf, yv, rcond=None)[0]; V = robust_cov(Xf, yv - Xf @ b)
        W = b[:L] @ np.linalg.inv(V[:L, :L]) @ b[:L]
        return W / L
    # SW conditional F for endog[0]: partial the other endogenous variables' first-stage fitted values out
    y1 = Z[:, idx[endog[0]]]; others = Z[:, [idx[e] for e in endog[1:]]]
    Xall = Z[:, zi + xi]
    fit_o = Xall @ np.linalg.lstsq(Xall, others, rcond=None)[0]
    R = np.column_stack([fit_o, Z[:, xi]]) if xi else fit_o
    y1t = y1 - R @ np.linalg.lstsq(R, y1, rcond=None)[0]
    b = np.linalg.lstsq(Xall, y1t, rcond=None)[0]; V = robust_cov(Xall, y1t - Xall @ b)
    W = b[:L] @ np.linalg.inv(V[:L, :L]) @ b[:L]
    return W / (L - len(endog) + 1)

def hansen_J(df, y, endog, insts, exog):
    cols = list(dict.fromkeys([y] + endog + insts + exog)); sub = df.dropna(subset=cols)
    Zd = demean(sub, cols); idx = {c: i for i, c in enumerate(cols)}
    yv = Zd[:, idx[y]]; X = Zd[:, [idx[c] for c in endog + exog]]; Zm = Zd[:, [idx[c] for c in insts + exog]]
    P = Zm @ np.linalg.solve(Zm.T @ Zm, Zm.T @ X)
    b = np.linalg.solve(P.T @ X, P.T @ yv); u = yv - X @ b
    n = len(u); g = Zm.T @ u / n; S = (Zm * (u**2)[:, None]).T @ Zm / n
    J = n * g @ np.linalg.solve(S, g); dfj = len(insts) - len(endog)
    from scipy.stats import chi2
    return float(J), int(dfj), float(chi2.sf(J, dfj)) if dfj > 0 else None

def iv(df, y, endog, insts, exog=("lnpop",), extra=None, sample=None):
    """Manual 2SLS on two-way-demeaned data (country + year FE), HC1 robust SE with n/(n-k) adjustment.
       Validated against pyfixest/ivreghdfe for the single-endogenous case (identical to 3 dp)."""
    exog = list(exog) + (list(extra) if extra else [])
    d = df if sample is None else df[sample(df)]
    cols = list(dict.fromkeys([y] + endog + insts + exog)); d = d.dropna(subset=cols)
    Zd = demean(d, cols); idx = {c: i for i, c in enumerate(cols)}
    yv = Zd[:, idx[y]]; X = Zd[:, [idx[c] for c in endog + exog]]; Zm = Zd[:, [idx[c] for c in insts + exog]]
    Xh = Zm @ np.linalg.solve(Zm.T @ Zm, Zm.T @ X)
    b = np.linalg.solve(Xh.T @ X, Xh.T @ yv); u = yv - X @ b
    V = robust_cov(Xh, u); se = np.sqrt(np.diag(V)); n = len(u)
    from scipy.stats import t as tdist
    out = {"N": int(n), "F": float(kp_F(d, endog, insts, exog))}
    for j, e in enumerate(endog):
        out[e] = [float(b[j]), float(se[j]), float(2 * tdist.sf(abs(b[j] / se[j]), n - X.shape[1]))]
    if len(insts) > len(endog):
        J, dfj, pJ = hansen_J(d, y, endog, insts, exog); out["J"] = [J, dfj, pJ]
    return out

def ols(df, y, xs, exog=("lnpop",), sample=None):
    d = df if sample is None else df[sample(df)]
    d = d.dropna(subset=[y] + xs + list(exog))
    m = pf.feols(f"{y} ~ {' + '.join(xs + list(exog))} | c + y", data=d, vcov="hetero")
    return {"N": int(m._N), **{x: [float(m.coef()[x]), float(m.se()[x]), float(m.pvalue()[x])] for x in xs}}

R = {"label": label, "ymax": ymax, "rows_main": int(len(M)), "countries": int(M.c.nunique()),
     "years": [int(M.y.min()), int(M.y.max())]}

# ------------------------------------------------------------------ Table 1: main (cwm, sum) + measures (max)
T1 = {}
for tr, src in [("ln_gaci_cwm", M), ("lnG", M), ("ln_gaci_max", MS)]:
    T1[tr] = {"first": ols(src, tr, ["tourism_int"])}
    for yv in ["g_int", "g_vol", "g_gdp"]:
        T1[tr][f"ols_{yv}"] = ols(src, yv, [tr]); T1[tr][f"iv_{yv}"] = iv(src, yv, [tr], ["tourism_int"])
R["T1_main"] = T1

# ------------------------------------------------------------------ Table 2: heterogeneity (interaction IV)
T2 = {}
for tag in ["inc", "con", "rem"]:
    for yv in ["g_int", "g_vol", "g_gdp"]:
        T2[f"{yv}_{tag}"] = iv(M, yv, ["ln_gaci_cwm", f"cwm_{tag}"], ["tourism_int", f"z_{tag}"])
R["T2_het"] = T2

# ------------------------------------------------------------------ Table 3: temporal (post-2010)
T3 = {}
for yv in ["g_int", "g_vol", "g_gdp"]:
    T3[f"int_{yv}"] = iv(M, yv, ["ln_gaci_cwm", "cwm_post"], ["tourism_int", "z_post"])
    T3[f"pre_{yv}"] = iv(M, yv, ["ln_gaci_cwm"], ["tourism_int"], sample=lambda d: d.y < 2010)
    T3[f"post_{yv}"] = iv(M, yv, ["ln_gaci_cwm"], ["tourism_int"], sample=lambda d: d.y >= 2010)
R["T3_temporal"] = T3

# ------------------------------------------------------------------ Table 4: mechanism (composition) + Table 5 (mediation, 6 columns)
T4 = {}
for s, f in [("sfull", None), ("sdrop", lambda d: ~d.y.isin([2020, 2021]))]:
    for yv in ["r_vw", "sh_hivw", "r_bec", "sh_bec", "xr_vw", "xsh_hivw", "lntot"]:
        T4[f"{yv}_{s}"] = iv(ME, yv, ["ln_gaci_cwm"], ["tourism_int"], sample=f)
R["T4_mech"] = T4
ok = ME.dropna(subset=["g_int", "g_vol", "r_bec", "r_vw", "lnpop", "ln_gaci_cwm", "tourism_int"])
T5 = {}
for s, f in [("sfull", None), ("sdrop", lambda d: ~d.y.isin([2020, 2021]))]:
    for yv in ["g_int", "g_vol"]:
        T5[f"{yv}_total_{s}"] = iv(ok, yv, ["ln_gaci_cwm"], ["tourism_int"], sample=f)
        T5[f"{yv}_M1out_{s}"] = iv(ok, "r_bec", ["ln_gaci_cwm"], ["tourism_int"], sample=f)
        T5[f"{yv}_plusM1_{s}"] = iv(ok, yv, ["ln_gaci_cwm"], ["tourism_int"], extra=["r_bec"], sample=f)
        T5[f"{yv}_M2out_{s}"] = iv(ok, "r_vw", ["ln_gaci_cwm"], ["tourism_int"], sample=f)
        T5[f"{yv}_plusM2_{s}"] = iv(ok, yv, ["ln_gaci_cwm"], ["tourism_int"], extra=["r_vw"], sample=f)
        T5[f"{yv}_plusBoth_{s}"] = iv(ok, yv, ["ln_gaci_cwm"], ["tourism_int"], extra=["r_bec", "r_vw"], sample=f)
R["T5_mediation"] = T5

# ------------------------------------------------------------------ Table 6: controls sensitivity
T6 = {}
for tag, ex in [("none", []), ("lnpop", ["lnpop"]), ("lngdp", ["lngdp"]), ("pop_gdp", ["lnpop", "lngdp"]), ("pop_pc", ["lnpop", "lnpc"])]:
    T6[tag] = iv(ME, "g_int", ["ln_gaci_cwm"], ["tourism_int"], exog=ex)
R["T6_controls"] = T6

# ------------------------------------------------------------------ Table 7: validity battery A-D
T7 = {}
for yv in ["g_int", "g_vol", "g_shr", "lnpc", "lngdp"]:
    T7[f"A_natmix_{yv}"] = iv(M, yv, ["ln_gaci_cwm"], ["z_nat", "z_mix"])
    T7[f"B_nat_{yv}"] = iv(M, yv, ["ln_gaci_cwm"], ["z_nat"])
    T7[f"B_three_{yv}"] = iv(M, yv, ["ln_gaci_cwm"], ["z_nat", "z_mix", "z_cult"])
    T7[f"C_tour_{yv}"] = iv(CB, yv, ["ln_gaci_cwm"], ["tourism_int"], extra=["ln_sea_ma"])
    T7[f"C_feyr_{yv}"] = iv(CB, yv, ["ln_gaci_cwm"], ["feyrer_int"], extra=["ln_sea_ma"])
    T7[f"C_both_{yv}"] = iv(CB, yv, ["ln_gaci_cwm"], ["tourism_int", "feyrer_int"], extra=["ln_sea_ma"])
    T7[f"C_both19_{yv}"] = iv(CB, yv, ["ln_gaci_cwm"], ["tourism_int", "feyrer_int"], extra=["ln_sea_ma"], sample=lambda d: d.y <= 2019)
R["T7_validity"] = T7

# ------------------------------------------------------------------ Table 8: plausibly exogenous (Conley union of CIs)
T8 = {}
for yv in ["g_int", "g_vol", "g_gdp"]:
    d = M.dropna(subset=[yv, "lnpop", "ln_gaci_cwm", "tourism_int"]).copy()
    rf = ols(d, yv, ["tourism_int"])["tourism_int"]; base = iv(d, yv, ["ln_gaci_cwm"], ["tourism_int"])
    ub0 = base["ln_gaci_cwm"][0] + 1.959964 * base["ln_gaci_cwm"][1]
    row = {"rf": rf, "iv": base["ln_gaci_cwm"], "N": base["N"], "ub0": ub0}
    def lb_at(f):
        d["ytil"] = d[yv] - f * rf[0] * d["tourism_int"]
        r = iv(d, "ytil", ["ln_gaci_cwm"], ["tourism_int"])["ln_gaci_cwm"]; return r[0] - 1.959964 * r[1]
    for f in (0.10, 0.20, 0.30): row[f"lb{int(f*100)}"] = lb_at(f)
    fstar, f = 0.0, 0.0
    if base["ln_gaci_cwm"][0] - 1.959964 * base["ln_gaci_cwm"][1] > 0:
        while f < 2.0:
            f = round(f + 0.01, 2)
            if lb_at(f) <= 0: fstar = f; break
    row["fstar"] = fstar; T8[yv] = row
R["T8_conley"] = T8

# ------------------------------------------------------------------ Table 9: flexible reduced form by quintile
T9 = {}
d = M.dropna(subset=["g_int", "lnpop", "tourism_int"]).copy()
for mod, var in [("inc", "base_lnpc"), ("con", "base_cwm"), ("rem", "ln_remote")]:
    dd = d.dropna(subset=[var]).copy()
    dd["q"] = pd.qcut(dd[var].rank(method="first"), 5, labels=False) + 1
    for k in range(1, 6): dd[f"zq{k}"] = dd.tourism_int * (dd.q == k)
    m = pf.feols("g_int ~ " + " + ".join(f"zq{k}" for k in range(1, 6)) + " + lnpop | c + y", data=dd, vcov="hetero")
    T9[mod] = {"N": int(m._N), **{f"q{k}": [float(m.coef()[f"zq{k}"]), float(m.se()[f"zq{k}"])] for k in range(1, 6)}}
R["T9_rf_quintile"] = T9

json.dump(R, open(f"_reest_{label}.json", "w"), indent=1)

# ------------------------------------------------------------------ brief print
def s(v): return f"{v[0]:7.3f} ({v[1]:.3f})" + ("***" if v[2] < .01 else "**" if v[2] < .05 else "*" if v[2] < .10 else "   ")
print(f"\n===== {label}: {R['years']} rows={R['rows_main']} countries={R['countries']}")
print("T1 cwm  first-stage b/se:", s(T1['ln_gaci_cwm']['first']['tourism_int']), " N", T1['ln_gaci_cwm']['first']['N'])
for yv in ["g_int", "g_vol", "g_gdp"]:
    r = T1["ln_gaci_cwm"][f"iv_{yv}"]; print(f"T1 cwm IV {yv:6s}", s(r["ln_gaci_cwm"]), f"F={r['F']:.1f} N={r['N']}", " | OLS", s(T1["ln_gaci_cwm"][f"ols_{yv}"]["ln_gaci_cwm"]))
for yv in ["g_int", "g_vol", "g_gdp"]:
    r = T1["lnG"][f"iv_{yv}"]; print(f"T1 sum IV {yv:6s}", s(r["lnG"]), f"F={r['F']:.1f}")
for k, r in T2.items():
    if k.endswith("_rem"): continue
    print(f"T2 {k:10s} main", s(r["ln_gaci_cwm"]), " x mod", s(r[[c for c in r if c.startswith('cwm_')][0]]), f"SW-F={r['F']:.1f} N={r['N']}")
for yv in ["g_int", "g_vol", "g_gdp"]:
    r = T3[f"int_{yv}"]; print(f"T3 int {yv:6s} main", s(r["ln_gaci_cwm"]), " x post", s(r["cwm_post"]), f"SW-F={r['F']:.1f}", f"| pre-F={T3[f'pre_{yv}']['F']:.2f} post-F={T3[f'post_{yv}']['F']:.1f}")
for k, r in T4.items(): print(f"T4 {k:16s}", s(r["ln_gaci_cwm"]), f"F={r['F']:.1f} N={r['N']}")
for k, r in T5.items():
    if k.startswith("g_int") and k.endswith("sfull"): print(f"T5 {k:22s}", s(r["ln_gaci_cwm"]), f"N={r['N']}")
for k, r in T6.items(): print(f"T6 {k:8s}", s(r["ln_gaci_cwm"]), f"F={r['F']:.1f}")
for k, r in T7.items():
    if k.split("_")[-1] in ("g_int", "g_vol"):
        print(f"T7 {k:18s}", s(r["ln_gaci_cwm"]), f"F={r['F']:.1f}", (f"J p={r['J'][2]:.3f}" if "J" in r else ""), f"N={r['N']}")
for k, r in T8.items(): print(f"T8 {k:6s} IV", s(r["iv"]), f"lb10={r['lb10']:.3f} lb20={r['lb20']:.3f} lb30={r['lb30']:.3f} f*={r['fstar']:.2f}")
for k, r in T9.items(): print(f"T9 {k}", " ".join(f"q{i}={r[f'q{i}'][0]:.3f}({r[f'q{i}'][1]:.3f})" for i in range(1, 6)))
