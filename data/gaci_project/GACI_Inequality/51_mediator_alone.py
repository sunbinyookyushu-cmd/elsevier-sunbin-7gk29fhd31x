# -*- coding: utf-8 -*-
"""51_mediator_alone.py : market Gini on each mediator WITHOUT the hub as a control (user question 2026-09-28).
   (1) OLS: ln Gini_mkt ~ M + ln pop | country + year, cluster country
   (2) 2SLS: M instrumented by the Feyrer interaction (valid only if the hub acts on the Gini solely through M;
       this is the 'total effect of the mediator' that the no-hub specification implicitly assumes)
   For reference, the hub-controlled b-path (M with ln GACI_max instrumented) is reproduced.
   Output: _mediator_alone_results.csv"""
import os, numpy as np, pandas as pd, pyfixest as pf
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
p = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "ln_gini_mkt", "ln_gaci_max", "lnpop", "feyrer_int", "ln_gdppc", "emp_ind", "emp_agr", "urban", "trade_gdp"])
m = pd.read_csv("_macro_channels.csv"); w = pd.read_csv("_wdi_mech.csv")
p = p.merge(m[["c", "y", "ln_tr_hivw", "ln_tr_diff", "sh_diff", "ln_nflow"]], on=["c", "y"], how="left").merge(w[["c", "y", "tour_arrivals"]], on=["c", "y"], how="left")
p["ln_tour"] = np.log(p.tour_arrivals.where(p.tour_arrivals > 0))
MED = [("ln_gdppc", "ln GDP per capita"), ("ln_tr_hivw", "ln high value-to-weight trade"), ("ln_tr_diff", "ln differentiated-goods trade"), ("sh_diff", "Differentiated-goods share of trade"),
       ("ln_nflow", "ln number of export partners"), ("ln_tour", "ln international tourist arrivals"), ("emp_ind", "Employment in industry, %"), ("emp_agr", "Employment in agriculture, %"), ("urban", "Urban population, %"), ("trade_gdp", "Trade, % of GDP")]
rows = []
for v, lab in MED:
    d = p.dropna(subset=["ln_gini_mkt", v, "lnpop", "feyrer_int", "ln_gaci_max"]).copy()
    if d.c.nunique() < 30: continue
    ols = pf.feols(f"ln_gini_mkt ~ {v} + lnpop | c + y", d, vcov={"CRV1": "c"})
    iv = pf.feols(f"ln_gini_mkt ~ lnpop | c + y | {v} ~ feyrer_int", d, vcov={"CRV1": "c"})
    fs = pf.feols(f"{v} ~ feyrer_int + lnpop | c + y", d, vcov={"CRV1": "c"})
    ctl = pf.feols(f"ln_gini_mkt ~ {v} + lnpop | c + y | ln_gaci_max ~ feyrer_int", d, vcov={"CRV1": "c"})
    kpf = (fs.coef()["feyrer_int"] / fs.se()["feyrer_int"]) ** 2
    rows.append(dict(mediator=lab, N=len(d), ols_b=ols.coef()[v], ols_se=ols.se()[v], ols_p=ols.pvalue()[v], iv_b=iv.coef()[v], iv_se=iv.se()[v], iv_p=iv.pvalue()[v], iv_kpf=kpf,
                     ctl_b=ctl.coef()[v], ctl_se=ctl.se()[v], ctl_p=ctl.pvalue()[v], ctl_hub=ctl.coef()["ln_gaci_max"], ctl_hub_se=ctl.se()["ln_gaci_max"]))
r = pd.DataFrame(rows); r.to_csv("_mediator_alone_results.csv", index=False)
pd.set_option("display.width", 220)
print(r.assign(**{k: r[k].round(4) for k in r.columns if k not in ("mediator", "N")}).to_string(index=False))
