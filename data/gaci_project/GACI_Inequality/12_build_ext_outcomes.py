# -*- coding: utf-8 -*-
"""12_build_ext_outcomes.py : two new outcome blocks merged onto ineq_panel.csv -> ineq_panel_ext.csv
   (a) WID growth-incidence groups: average pretax national income (aptinc, equal-split adults 20+)
       and income share (sptinc) for deciles p0p10..p90p100, top 1%, top 0.1%, bottom 50%, middle 40%,
       plus post-tax disposable (adiinc/sdiinc). Source: WID bulk download 2026-09-28
       (scratchpad/ext/wid_all_data.zip -> wid_pct_long.csv via extract_wid_pct.py).
   (b) DOSE v2.9 (Wenz et al. 2023, Zenodo 13773040): within-country dispersion of regional GRP per
       capita (constant 2015 LCU), population weighted: Theil-T, Gini, CV, top-region share of GRP,
       top-region GRPpc / national mean, number of regions.
"""
import os, io, numpy as np, pandas as pd, pycountry

D = os.path.dirname(os.path.abspath(__file__))
EXT = r"C:\Users\sunbi\AppData\Local\Temp\claude\C--Users-sunbi\ba65b5c1-d10e-4893-9614-ff9d9e4c7cba\scratchpad\ext"

# ---------------- (a) WID ----------------
w = pd.read_csv(os.path.join(EXT, "wid_pct_long.csv"))
fix = {"KS": "XKX", "ZZ": None}
def a3(a2):
    if a2 in fix: return fix[a2]
    try: return pycountry.countries.get(alpha_2=a2).alpha_3
    except Exception: return None
w["c"] = w.country.map(a3)
w = w[w.c.notna()].rename(columns={"year": "y"})
G = {"p0p10": "d1", "p10p20": "d2", "p20p30": "d3", "p30p40": "d4", "p40p50": "d5", "p50p60": "d6",
     "p60p70": "d7", "p70p80": "d8", "p80p90": "d9", "p90p100": "d10", "p99p100": "t1", "p99.9p100": "t01",
     "p0p50": "b50", "p50p90": "m40", "p0p100": "all"}
w = w[w.percentile.isin(G)].copy()
w["g"] = w.percentile.map(G)
def wide(var, prefix, log):
    x = w.pivot_table(index=["c", "y"], columns="g", values=var)
    x.columns = ["%s_%s" % (prefix, g) for g in x.columns]
    if log: x = np.log(x.where(x > 0))
    return x
W = pd.concat([wide("aptinc", "ln_apt", True), wide("sptinc", "ln_spt", True), wide("sptinc", "spt", False),
               wide("adiinc", "ln_adi", True), wide("sdiinc", "ln_sdi", True)], axis=1).reset_index()
print("WID wide:", W.shape, "countries", W.c.nunique())

# ---------------- (b) DOSE ----------------
d = pd.read_csv(os.path.join(EXT, "DOSE_V2.9.csv"), low_memory=False)
d = d.rename(columns={"GID_0": "c", "year": "y"})
d["ypc"] = d["grp_pc_lcu_2015"].where(d["grp_pc_lcu_2015"].notna(), d["grp_pc_usd_2015"])
d = d[(d.y >= 1990) & d.ypc.notna() & d["pop"].notna() & (d["pop"] > 0) & (d.ypc > 0)]
def disp(g):
    p = g["pop"].values.astype(float); yv = g.ypc.values.astype(float)
    ps = p / p.sum(); ybar = (ps * yv).sum(); r = yv / ybar
    theil = (ps * r * np.log(r)).sum()
    # population-weighted Gini
    o = np.argsort(yv); yv_o, ps_o = yv[o], ps[o]
    cum_p = np.cumsum(ps_o); cum_y = np.cumsum(ps_o * yv_o) / (ps_o * yv_o).sum()
    gini = 1 - np.sum((cum_y[1:] + cum_y[:-1]) * np.diff(np.concatenate([[0], cum_p]))[1:]) - cum_y[0] * cum_p[0]
    grp = p * yv; share_top = grp.max() / grp.sum()
    cv = np.sqrt((ps * (yv - ybar) ** 2).sum()) / ybar
    return pd.Series(dict(n_reg=len(g), theil_reg=theil, gini_reg=gini, cv_reg=cv, share_topreg=share_top,
                          ratio_topreg=yv.max() / ybar, structchange=int(g["StructChange"].fillna(0).astype(float).max() > 0)))
R = d.groupby(["c", "y"]).apply(disp).reset_index()
R = R[R.n_reg >= 3]
for v in ["theil_reg", "gini_reg", "cv_reg", "share_topreg", "ratio_topreg"]:
    R["ln_" + v] = np.log(R[v])
# stable region set: drop country-years whose region count differs from the country's modal count
mode = R.groupby("c").n_reg.agg(lambda s: s.mode().iloc[0]).rename("n_reg_mode")
R = R.merge(mode, on="c"); R["stable_reg"] = (R.n_reg == R.n_reg_mode).astype(int)
print("DOSE country-years:", R.shape, "countries", R.c.nunique(), "stable share", R.stable_reg.mean().round(3))

# ---------------- merge ----------------
P = pd.read_csv(os.path.join(D, "ineq_panel.csv"), keep_default_na=False, na_values=["", "."], low_memory=False)
n0 = len(P)
P = P.merge(W, on=["c", "y"], how="left").merge(R, on=["c", "y"], how="left")
assert len(P) == n0
P.to_csv(os.path.join(D, "ineq_panel_ext.csv"), index=False)
s = P[P.gini_mkt.notna()]
print("estimation sample rows", len(s))
print("  WID d1 coverage", s.ln_apt_d1.notna().sum(), " all", s.ln_apt_all.notna().sum())
print("  DOSE coverage", s.ln_theil_reg.notna().sum(), "countries", s[s.ln_theil_reg.notna()].c.nunique(),
      " stable", (s.stable_reg == 1).sum())
# consistency with existing panel variables
chk = s[["ln_avg_all_wid", "ln_apt_all", "bot50_wid", "spt_b50", "top10_wid", "spt_d10"]].dropna()
print("  check corr ln_avg_all_wid~ln_apt_all", np.corrcoef(chk.ln_avg_all_wid, chk.ln_apt_all)[0, 1].round(4),
      " bot50", np.corrcoef(chk.bot50_wid, chk.spt_b50)[0, 1].round(4), " top10", np.corrcoef(chk.top10_wid, chk.spt_d10)[0, 1].round(4))
print(s[["theil_reg", "gini_reg", "share_topreg", "ratio_topreg", "n_reg"]].describe().T.round(3))
