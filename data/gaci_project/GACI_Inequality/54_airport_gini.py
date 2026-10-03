# -*- coding: utf-8 -*-
"""54_airport_gini.py : within-country inequality of connectivity across airports (user, 2026-09-28).
   Index: Gini of airport-level GACI within each country-year (countries with >= 2 airports), plus Theil and the top-airport share.
   Uses:
     (1) descriptive: change in ln GACI_max vs change in airport-GACI Gini, first to last year  -> FigB5_airport_gini.png
     (2) regressions (ln market Gini, ln disp. Gini, bottom-50 share; country + year FE, ln pop, cluster country):
         a. 2SLS GACI_max (Feyrer) with airport-Gini as control
         b. OLS and 2SLS with GACI_max x (baseline airport-Gini, demeaned); interaction instrumented by Z x baseline airport-Gini
         c. split samples by baseline (1996) airport-Gini: below / above median, terciles
   Outputs: _airport_gini.csv (c, y, n_air, ap_gini, ap_theil, share_max), _airport_gini_results.csv"""
import os, csv, json, numpy as np, pandas as pd, pyfixest as pf
import matplotlib.pyplot as plt
import _ineqstyle as lz
D = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(D, ".."); os.chdir(D); lz.setup()
csv.field_size_limit(10 ** 7)
ap_iso2 = {}
for r in csv.DictReader(open(os.path.join(P, "ourairports.csv"), encoding="utf-8", errors="replace")):
    ia = (r.get("iata_code") or "").strip()
    if len(ia) == 3: ap_iso2[ia] = r.get("iso_country", "").strip()
iso2to3 = json.load(open(os.path.join(P, "iso2to3.json")))
raw = pd.read_csv(os.path.join(P, "GACI1996_2024_new_panel_data.csv"), encoding="utf-8", encoding_errors="replace")
raw.columns = [c.strip().lstrip("﻿") for c in raw.columns]
raw["c"] = raw["Airport"].str.strip().map(lambda a: iso2to3.get(ap_iso2.get(a, ""), "")); raw = raw[raw.c != ""].rename(columns={"Year": "y"})
raw["GACI"] = pd.to_numeric(raw["GACI"], errors="coerce"); raw = raw.dropna(subset=["GACI"]); raw = raw[(raw.y >= 1996) & (raw.y <= 2023)]

def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    if n < 2 or x.sum() <= 0: return np.nan
    return (2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n
def theil(x):
    x = np.asarray(x, float); m = x.mean()
    if len(x) < 2 or m <= 0: return np.nan
    r = x / m; r = r[r > 0]; return float(np.mean(r * np.log(r)))
g = raw.groupby(["c", "y"]).GACI.agg(n_air="size", ap_gini=gini, ap_theil=theil, share_max=lambda s: s.max() / s.sum()).reset_index()
g.to_csv("_airport_gini.csv", index=False)
print("country-years", len(g), "| with >=2 airports", (g.n_air >= 2).sum(), "| ap_gini mean %.3f sd %.3f within-sd %.3f" % (g.ap_gini.mean(), g.ap_gini.std(), (g.ap_gini - g.groupby("c").ap_gini.transform("mean")).std()))

p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gini_disp", "ln_gaci_max", "ln_gaci_sum", "lnpop", "feyrer_int", "ln_air_ma"])
e = pd.read_csv("ineq_panel_ext.csv", usecols=["c", "y", "ln_spt_b50", "ln_apt_all", "ln_apt_b50", "ln_apt_d10"])
p = p.merge(e, on=["c", "y"], how="left").merge(g, on=["c", "y"], how="left")
base = p.sort_values("y").groupby("c").first()[["ap_gini", "y"]].rename(columns={"ap_gini": "ap_gini0", "y": "y0"})
p = p.merge(base, on="c", how="left"); p["ap_gini0_dm"] = p.ap_gini0 - p.ap_gini0.mean(); p["z_x_ap0"] = p.feyrer_int * p.ap_gini0_dm; p["max_x_ap0"] = p.ln_gaci_max * p.ap_gini0_dm
med = p.groupby("c").ap_gini0.first().median(); q = p.groupby("c").ap_gini0.first().quantile([1 / 3, 2 / 3]).values
p["ap0_grp"] = np.where(p.ap_gini0 <= q[0], "low", np.where(p.ap_gini0 <= q[1], "mid", "high")); p["ap0_half"] = np.where(p.ap_gini0 <= med, "below", "above")
print("baseline airport-Gini: median %.3f, terciles %.3f / %.3f" % (med, q[0], q[1]))


def iv2(d, o, endog, inst, exog=["lnpop"]):
    """2SLS with several endogenous regressors: FE partialled out with pyfixest, then 2SLS on residuals, CRV1 by country."""
    from scipy import stats
    d = d.dropna(subset=[o] + endog + inst + exog).copy(); d = d[d.groupby("c").c.transform("size") > 1]; d = d[d.groupby("y").y.transform("size") > 1]
    def res(v): return pf.feols(f"{v} ~ " + " + ".join(exog) + " | c + y", d).resid()
    y = res(o); X = np.column_stack([res(v) for v in endog]); Z = np.column_stack([res(v) for v in inst])
    Pz = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X); b = np.linalg.solve(Pz.T @ X, Pz.T @ y); u = y - X @ b
    A = np.linalg.inv(Pz.T @ X); cl = d.c.values; G = len(np.unique(cl)); n, k = X.shape
    meat = sum(np.outer(Pz[cl == g].T @ u[cl == g], Pz[cl == g].T @ u[cl == g]) for g in np.unique(cl))
    V = A @ meat @ A.T * (G / (G - 1)) * ((n - 1) / (n - k)); se = np.sqrt(np.diag(V)); pv = 2 * (1 - stats.t.cdf(np.abs(b / se), G - 1))
    return dict(zip(endog, b)), dict(zip(endog, se)), dict(zip(endog, pv)), n

rows = []
def kp(fs, z="feyrer_int"): return (fs.coef()[z] / fs.se()[z]) ** 2
def add(spec, o, term, f, kpf=None, sample=""):
    rows.append(dict(spec=spec, outcome=o, sample=sample, term=term, b=f.coef()[term], se=f.se()[term], p=f.pvalue()[term], kpf=kpf, N=f._N))
OUT = ["ln_gini_mkt", "ln_gini_disp", "ln_spt_b50"]
for o in OUT:
    d = p.dropna(subset=[o, "ln_gaci_max", "lnpop", "feyrer_int", "ap_gini"]).copy()
    # a. control
    f = pf.feols(f"{o} ~ ap_gini + lnpop | c + y | ln_gaci_max ~ feyrer_int", d, vcov={"CRV1": "c"}); fs = pf.feols("ln_gaci_max ~ feyrer_int + ap_gini + lnpop | c + y", d, vcov={"CRV1": "c"})
    add("a. 2SLS max, airport-Gini control", o, "ln_gaci_max", f, kp(fs)); add("a. 2SLS max, airport-Gini control", o, "ap_gini", f, kp(fs))
    f = pf.feols(f"{o} ~ ln_gaci_max + ap_gini + lnpop | c + y", d, vcov={"CRV1": "c"}); add("a. OLS max, airport-Gini control", o, "ln_gaci_max", f); add("a. OLS max, airport-Gini control", o, "ap_gini", f)
    f = pf.feols(f"{o} ~ ap_gini + lnpop | c + y", d, vcov={"CRV1": "c"}); add("a. OLS airport-Gini alone", o, "ap_gini", f)
    # b. interaction with baseline airport-Gini
    d2 = p.dropna(subset=[o, "ln_gaci_max", "lnpop", "feyrer_int", "ap_gini0"]).copy()
    f = pf.feols(f"{o} ~ ln_gaci_max + max_x_ap0 + lnpop | c + y", d2, vcov={"CRV1": "c"}); add("b. OLS max x baseline airport-Gini", o, "ln_gaci_max", f); add("b. OLS max x baseline airport-Gini", o, "max_x_ap0", f)
    bb, ss, pp, nn = iv2(d2, o, ["ln_gaci_max", "max_x_ap0"], ["feyrer_int", "z_x_ap0"])
    for k in ["ln_gaci_max", "max_x_ap0"]: rows.append(dict(spec="b. 2SLS max x baseline airport-Gini", outcome=o, sample="", term=k, b=bb[k], se=ss[k], p=pp[k], kpf=None, N=nn))
    # c. splits
    for col, grps in [("ap0_half", ["below", "above"]), ("ap0_grp", ["low", "mid", "high"])]:
        for gname in grps:
            s = d2[d2[col] == gname]
            if s.c.nunique() < 15: continue
            f = pf.feols(f"{o} ~ lnpop | c + y | ln_gaci_max ~ feyrer_int", s, vcov={"CRV1": "c"}); fs = pf.feols("ln_gaci_max ~ feyrer_int + lnpop | c + y", s, vcov={"CRV1": "c"})
            add(f"c. 2SLS split by baseline airport-Gini ({col})", o, "ln_gaci_max", f, kp(fs), sample=f"{gname} (n_c={s.c.nunique()})")
r = pd.DataFrame(rows); r.to_csv("_airport_gini_results.csv", index=False)
pd.set_option("display.width", 240); print(r.assign(b=r.b.round(3), se=r.se.round(3), p=r.p.round(3), kpf=r.kpf.round(1)).to_string(index=False))

# descriptive figure: change in ln GACI_max vs change in airport-Gini, first to last year
first = p.sort_values("y").groupby("c").first(); lastv = p.sort_values("y").groupby("c").last()
ch = pd.DataFrame({"d_max": lastv.ln_gaci_max - first.ln_gaci_max, "d_apg": lastv.ap_gini - first.ap_gini, "span": lastv.y - first.y, "n_air": lastv.n_air}).dropna(); ch = ch[ch.span >= 15]
fig, axes = plt.subplots(1, 2, figsize=(14, 5.6))
ax = axes[0]; yr = p.dropna(subset=["ap_gini"]).groupby("y").agg(apg=("ap_gini", "mean"), mx=("ln_gaci_max", "mean"))
ax.plot(yr.index, yr.apg, color=lz.TEAL, lw=2.6, marker="o", ms=4.5); ax.set_ylabel("Mean Gini of GACI across a country's airports"); ax.set_xlabel("Year"); ax.set_title("Concentration of connectivity within countries", loc="left", pad=8); lz.panel_letter(ax, "a", x=-0.16, y=1.02)
ax = axes[1]; ax.scatter(ch.d_max, ch.d_apg, s=18 + 2 * np.sqrt(ch.n_air), color=lz.TEAL, alpha=0.6, lw=0.4, edgecolors="white", zorder=3)
for cc in ["TUR", "KOR", "QAT", "ARE", "USA", "CHN", "RUS", "IND", "SAU", "IRL", "NOR", "VNM", "BRA", "ETH"]:
    if cc in ch.index: ax.annotate(cc, (ch.loc[cc, "d_max"], ch.loc[cc, "d_apg"]), xytext=(5, 3), textcoords="offset points", fontsize=9.5, color=lz.INK)
b1, b0 = np.polyfit(ch.d_max, ch.d_apg, 1); xx = np.linspace(ch.d_max.min(), ch.d_max.max(), 50); ax.plot(xx, b0 + b1 * xx, color=lz.AMBER, lw=1.8, ls=(0, (5, 3)))
ax.axhline(0, color="#666666", lw=1); ax.axvline(0, color="#666666", lw=1); ax.set_xlabel("Change in ln GACI$_{max}$, first to last year"); ax.set_ylabel("Change in airport-GACI Gini")
ax.set_title("Hub growth and concentration, %d countries (slope %.2f)" % (len(ch), b1), loc="left", pad=8); lz.panel_letter(ax, "b", x=-0.16, y=1.02)
fig.tight_layout(w_pad=3); fig.savefig("FigB5_airport_gini.png", dpi=300, bbox_inches="tight"); fig.savefig("FigB5_airport_gini.pdf", bbox_inches="tight"); plt.close(fig)
print("corr(d_max, d_apg) = %.2f; share of countries with rising concentration among those with rising max: %.2f" % (ch[["d_max", "d_apg"]].corr().iloc[0, 1], (ch[ch.d_max > 0].d_apg > 0).mean()))
