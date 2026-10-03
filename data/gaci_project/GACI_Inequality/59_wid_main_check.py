# -*- coding: utf-8 -*-
"""59_wid_main_check.py : would a WID-only design (full WID sample, no SWIID Gini) carry the paper? (user, 2026-09-28)
   Full WID sample (179 economies, ~4,537 country-years), Feyrer instrument, country + year FE, ln pop, cluster country.
   A. scalar headline candidates: bottom-30 / bottom-20 / bottom-50 shares, top-10 share, top-half minus bottom-30 income,
      top-10 minus bottom-50 income, mean income, WID Gini; pretax and post-tax where available
   B. mechanism I: GACI_max with GACI_sum controlled (hub vs network)
   C. mechanism IV: splits by urbanisation, tourism dependence, baseline airport concentration
   D. mechanism V: pretax vs post-tax bottom-50 and top-10 shares (WID redistribution)
   E. growth by baseline hub size (below / above median GACI_max 1996)
   Output: _wid_main_check.csv"""
import os, numpy as np, pandas as pd, pyfixest as pf
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gaci_max", "ln_gaci_sum", "lnpop", "feyrer_int", "ln_gdppc", "urban", "ln_gini_pre_wid", "ln_bot50_post_wid", "ln_top10_post_wid", "ln_bot50_wid", "ln_top10_wid"])
e = pd.read_csv("ineq_panel_ext.csv"); e = e[["c", "y"] + [c for c in e.columns if c.startswith("spt_") or c.startswith("ln_apt_") or c.startswith("ln_spt_")]]
w = pd.read_csv("_wdi_mech.csv", usecols=["c", "y", "tour_rcpt_exp"]); g = pd.read_csv("_airport_gini.csv")
p = p.merge(e, on=["c", "y"], how="left").merge(w, on=["c", "y"], how="left").merge(g[["c", "y", "ap_gini"]], on=["c", "y"], how="left")
p["ln_spt_b30"] = np.log(p.spt_d1 + p.spt_d2 + p.spt_d3); p["ln_spt_b20"] = np.log(p.spt_d1 + p.spt_d2)
p["ln_apt_b30"] = np.log((p.spt_d1 + p.spt_d2 + p.spt_d3) / 0.3) + p.ln_apt_all
p["ln_apt_tophalf"] = np.log((p.spt_d6 + p.spt_d7 + p.spt_d8 + p.spt_d9 + p.spt_d10) / 0.5) + p.ln_apt_all
p["top_minus_b30"] = p.ln_apt_tophalf - p.ln_apt_b30; p["d10_minus_b50"] = p.ln_apt_d10 - p.ln_apt_b50
p["post_minus_pre_b50"] = p.ln_bot50_post_wid - p.ln_bot50_wid
base = p.sort_values("y").groupby("c").first()[["ln_gaci_max", "urban", "tour_rcpt_exp", "ap_gini"]].rename(columns=lambda s: s + "0")
p = p.merge(base, on="c", how="left")
for v in ["ln_gaci_max0", "urban0", "tour_rcpt_exp0", "ap_gini0"]:
    med = base[v].median(); p[v + "_hi"] = np.where(p[v].isna(), np.nan, (p[v] > med).astype(float))
rows = []
def run(d, o, x="ln_gaci_max", ctrl="", tag="", sample="full"):
    need = [o, x, "lnpop", "feyrer_int"] + ([ctrl] if ctrl else []); d = d.dropna(subset=need)
    if d.c.nunique() < 20: return
    rhs = "lnpop" + (f" + {ctrl}" if ctrl else "")
    fs = pf.feols(f"{x} ~ feyrer_int + {rhs} | c + y", d, vcov={"CRV1": "c"}); iv = pf.feols(f"{o} ~ {rhs} | c + y | {x} ~ feyrer_int", d, vcov={"CRV1": "c"})
    r = dict(block=tag, outcome=o, sample=sample, b=iv.coef()[x], se=iv.se()[x], p=iv.pvalue()[x], F=(fs.coef()["feyrer_int"] / fs.se()["feyrer_int"]) ** 2, N=len(d), n_c=d.c.nunique())
    if ctrl: r["ctrl_b"] = iv.coef()[ctrl]; r["ctrl_se"] = iv.se()[ctrl]
    rows.append(r)
A = ["ln_spt_b20", "ln_spt_b30", "ln_spt_b50", "ln_top10_wid", "ln_spt_t1", "top_minus_b30", "d10_minus_b50", "ln_apt_b30", "ln_apt_all", "ln_gini_pre_wid", "ln_bot50_post_wid", "ln_top10_post_wid", "post_minus_pre_b50"]
for o in A: run(p, o, tag="A scalar candidates")
for o in ["ln_spt_b30", "ln_spt_b50", "top_minus_b30", "ln_apt_b30", "ln_apt_all"]: run(p, o, ctrl="ln_gaci_sum", tag="B hub with sum control")
for v, lab in [("urban0_hi", "urban"), ("tour_rcpt_exp0_hi", "tourism"), ("ap_gini0_hi", "airport concentration"), ("ln_gaci_max0_hi", "baseline hub size")]:
    for val, nm in [(1.0, "above"), (0.0, "below")]:
        for o in ["ln_spt_b30", "ln_apt_b30", "ln_apt_all", "top_minus_b30"]: run(p[p[v] == val], o, tag=f"C/E split {lab}", sample=nm)
r = pd.DataFrame(rows); r.to_csv("_wid_main_check.csv", index=False)
st = lambda pv: "***" if pv < .01 else "**" if pv < .05 else "*" if pv < .1 else ""
pd.set_option("display.width", 220)
for blk, s in r.groupby("block", sort=False):
    print("\n==", blk)
    for _, x in s.iterrows(): print(f"  {x.outcome:20s} {x['sample']:6s} b {x.b:7.3f} ({x.se:.3f}){st(x.p):3s} F {x.F:5.1f} N {x.N} n_c {x.n_c}" + (f" | sum ctrl {x.ctrl_b:6.3f} ({x.ctrl_se:.3f})" if "ctrl_b" in x and pd.notna(x.get("ctrl_b")) else ""))
