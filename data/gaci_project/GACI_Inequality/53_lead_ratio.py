# -*- coding: utf-8 -*-
"""53_lead_ratio.py : hub lead over the national average airport, ln(GACI_max / GACI_cwm), as a third concentration measure.
   Outcomes: ln market Gini, ln disposable Gini, bottom-50 share, top-half minus bottom-half income.
   Specs: (1) OLS, ln(max/cwm) with ln GACI_sum controlled; (2) OLS without sum; (3) 2SLS, ln(max/cwm) instrumented by the
   Feyrer interaction with ln GACI_sum controlled; (4) 2SLS, ln GACI_max instrumented with ln(max/cwm) as OLS control
   (does the hub effect survive holding its lead fixed?). Country + year FE, ln pop, cluster country.
   Output: _lead_ratio_results.csv"""
import os, numpy as np, pandas as pd, pyfixest as pf
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gini_disp", "ln_gaci_max", "ln_gaci_cwm", "ln_gaci_sum", "ln_share_max", "ln_hhi", "lnpop", "feyrer_int", "n_air"])
e = pd.read_csv("ineq_panel_ext.csv", usecols=["c", "y", "ln_spt_b50", "ln_apt_top_bot"] if "ln_apt_top_bot" in pd.read_csv("ineq_panel_ext.csv", nrows=1).columns else ["c", "y", "ln_spt_b50"])
p = p.merge(e, on=["c", "y"], how="left"); p["ln_lead"] = p.ln_gaci_max - p.ln_gaci_cwm
print("ln(max/cwm): mean %.3f sd %.3f within-sd %.3f | corr with ln_share_max %.2f, ln_hhi %.2f" % (p.ln_lead.mean(), p.ln_lead.std(), (p.ln_lead - p.groupby("c").ln_lead.transform("mean")).std(), p[["ln_lead", "ln_share_max"]].corr().iloc[0, 1], p[["ln_lead", "ln_hhi"]].corr().iloc[0, 1]))
OUT = [("ln_gini_mkt", "ln market Gini"), ("ln_gini_disp", "ln disp. Gini"), ("ln_spt_b50", "Bottom-50 share")] + ([("ln_apt_top_bot", "Top half minus bottom half")] if "ln_apt_top_bot" in p.columns else [])
rows = []
def add(spec, o, olab, f, term, kpf=None):
    rows.append(dict(spec=spec, outcome=olab, term=term, b=f.coef()[term], se=f.se()[term], p=f.pvalue()[term], kpf=kpf, N=f._N))
for o, olab in OUT:
    d = p.dropna(subset=[o, "ln_lead", "ln_gaci_sum", "lnpop", "feyrer_int"])
    f = pf.feols(f"{o} ~ ln_lead + ln_gaci_sum + lnpop | c + y", d, vcov={"CRV1": "c"}); add("OLS, lead with sum", o, olab, f, "ln_lead"); add("OLS, lead with sum", o, olab, f, "ln_gaci_sum")
    f = pf.feols(f"{o} ~ ln_lead + lnpop | c + y", d, vcov={"CRV1": "c"}); add("OLS, lead alone", o, olab, f, "ln_lead")
    fs = pf.feols("ln_lead ~ feyrer_int + ln_gaci_sum + lnpop | c + y", d, vcov={"CRV1": "c"}); kpf = (fs.coef()["feyrer_int"] / fs.se()["feyrer_int"]) ** 2
    f = pf.feols(f"{o} ~ ln_gaci_sum + lnpop | c + y | ln_lead ~ feyrer_int", d, vcov={"CRV1": "c"}); add("2SLS, lead instrumented, sum control", o, olab, f, "ln_lead", kpf); add("2SLS, lead instrumented, sum control", o, olab, f, "ln_gaci_sum", kpf)
    fs = pf.feols("ln_gaci_max ~ feyrer_int + ln_lead + lnpop | c + y", d, vcov={"CRV1": "c"}); kpf = (fs.coef()["feyrer_int"] / fs.se()["feyrer_int"]) ** 2
    f = pf.feols(f"{o} ~ ln_lead + lnpop | c + y | ln_gaci_max ~ feyrer_int", d, vcov={"CRV1": "c"}); add("2SLS, max instrumented, lead control", o, olab, f, "ln_gaci_max", kpf); add("2SLS, max instrumented, lead control", o, olab, f, "ln_lead", kpf)
    fs = pf.feols("ln_lead ~ feyrer_int + lnpop | c + y", d, vcov={"CRV1": "c"}); kpf = (fs.coef()["feyrer_int"] / fs.se()["feyrer_int"]) ** 2
    add("first stage: Z -> lead (no sum)", o, olab, fs, "feyrer_int", kpf)
r = pd.DataFrame(rows); r.to_csv("_lead_ratio_results.csv", index=False)
pd.set_option("display.width", 220)
print(r.assign(b=r.b.round(4), se=r.se.round(4), p=r.p.round(3), kpf=r.kpf.round(1)).to_string(index=False))
