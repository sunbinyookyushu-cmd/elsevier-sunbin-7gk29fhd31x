# -*- coding: utf-8 -*-
"""21_aggregate_curve.py : aggregate (back-of-envelope) incidence of observed hub-connectivity growth, 1996-latest.
   For each country: dln GACI_max over its window x group elasticity (2SLS Feyrer, country-clustered, from
   _gic_dose_results.csv) = implied log change of the group's average income / of its income share.
   Compared with the actual change over the same window. Aggregated by continent (unweighted country means,
   as in _contribution_bycontinent.csv) and for the world (population-weighted, latest population).
   Outputs: _aggregate_curve_bycountry.csv, _aggregate_curve_bycontinent.csv, _aggregate_curve_world.csv"""
import os, numpy as np, pandas as pd
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
RD = dict(keep_default_na=False, na_values=["", "."])
g = pd.read_csv("_gic_dose_results.csv", **RD)
d = pd.read_csv("ineq_panel_ext.csv", low_memory=False)
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "b50", "m40", "all"]
beta_inc = {k: g[(g.block == "gic") & (g.outcome == "ln_apt_" + k) & (g.spec == "IV")].b.iloc[0] for k in G}
beta_sh = {k: g[(g.block == "gic_share") & (g.outcome == "ln_spt_" + k) & (g.spec == "IV")].b.iloc[0] for k in G if k != "all"}
beta_gini = 0.495  # headline 2SLS, ln market Gini (Table 1)
cols = ["ln_apt_" + k for k in G] + ["spt_b50", "spt_d10", "spt_t1", "gini_mkt", "ln_gaci_max", "lnpop"]
s = d.dropna(subset=["gini_mkt", "ln_gaci_max"] + ["ln_apt_" + k for k in G]).sort_values(["c", "y"])
rows = []
for c, x in s.groupby("c"):
    f, l = x.iloc[0], x.iloc[-1]
    if l.y - f.y < 15: continue
    r = {"c": c, "cont": str(f.reg)[:2], "y0": int(f.y), "y1": int(l.y), "dln_gaci": l.ln_gaci_max - f.ln_gaci_max, "pop1": np.exp(l.lnpop)}
    for k in G:
        r["actual_dln_inc_" + k] = l["ln_apt_" + k] - f["ln_apt_" + k]
        r["implied_dln_inc_" + k] = beta_inc[k] * r["dln_gaci"]
    for k in ["b50", "d10", "t1"]:
        r["share0_" + k] = f["spt_" + k]; r["share1_" + k] = l["spt_" + k]
        r["implied_dshare_pts_" + k] = f["spt_" + k] * 100 * (np.exp(beta_sh[k] * r["dln_gaci"]) - 1)
        r["actual_dshare_pts_" + k] = (l["spt_" + k] - f["spt_" + k]) * 100
    r["gini0"] = f.gini_mkt; r["implied_dgini_pts"] = f.gini_mkt * (np.exp(beta_gini * r["dln_gaci"]) - 1); r["actual_dgini_pts"] = l.gini_mkt - f.gini_mkt
    rows.append(r)
X = pd.DataFrame(rows)
X.to_csv("_aggregate_curve_bycountry.csv", index=False)

def summarise(df, w=None):
    out = {"n": len(df), "mean_dln_gaci": np.average(df.dln_gaci, weights=w)}
    for k in G:
        out["implied_pct_inc_" + k] = 100 * np.average(df["implied_dln_inc_" + k], weights=w)
        out["actual_pct_inc_" + k] = 100 * np.average(df["actual_dln_inc_" + k], weights=w)
    for k in ["b50", "d10", "t1"]:
        out["implied_dshare_pts_" + k] = np.average(df["implied_dshare_pts_" + k], weights=w)
        out["actual_dshare_pts_" + k] = np.average(df["actual_dshare_pts_" + k], weights=w)
    out["implied_dgini_pts"] = np.average(df.implied_dgini_pts, weights=w); out["actual_dgini_pts"] = np.average(df.actual_dgini_pts, weights=w)
    return out
C = pd.DataFrame({c: summarise(x) for c, x in X.groupby("cont")}).T
C.loc["ALL (unweighted)"] = summarise(X); C.loc["WORLD (pop-weighted)"] = summarise(X, X.pop1)
C.to_csv("_aggregate_curve_bycontinent.csv")
pd.set_option("display.width", 220)
show = ["n", "mean_dln_gaci", "implied_pct_inc_b50", "actual_pct_inc_b50", "implied_pct_inc_d10", "actual_pct_inc_d10", "implied_pct_inc_all", "actual_pct_inc_all",
        "implied_dshare_pts_b50", "actual_dshare_pts_b50", "implied_dshare_pts_d10", "actual_dshare_pts_d10", "implied_dgini_pts", "actual_dgini_pts"]
print(C[show].round(2).to_string())
print("\nelasticities used: income", {k: round(v, 2) for k, v in beta_inc.items()}, "\nshare", {k: round(v, 2) for k, v in beta_sh.items()})
