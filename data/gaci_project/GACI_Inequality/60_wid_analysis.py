# -*- coding: utf-8 -*-
"""60_wid_analysis.py : WID-main design (decision 2026-09-28). Full WID sample (all country-years with WID decile incomes),
   treatment ln GACI_max (also cwm, sum), Feyrer instrument, country + year FE, ln pop, country-clustered SE.
   Produces every number for the v4 manuscript in one long file: _wid_results.csv
   Blocks: sumstat | main | incidence | growth_stage | hub_network | channels | splits | redistribution | robust | measures |
           lags | stagedefs | spill | components | swiid_subsample | aggregate (by country / continent / world)
   Outcomes (logs): group incomes ln_apt_* (WID deciles, top1, top0.1, b50, m40, all) and derived b30 / mid40 / top30;
   group shares ln_spt_* (identity: ln share = ln group income - ln mean income + ln group size); gaps as difference outcomes."""
import os, warnings, numpy as np, pandas as pd, pyfixest as pf
from scipy import stats
warnings.filterwarnings("ignore")
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
RD = dict(keep_default_na=False, na_values=["", ".", "NA"])

# ---------------------------------------------------------------- panel
p = pd.read_csv("ineq_panel.csv", low_memory=False)
e = pd.read_csv("ineq_panel_ext.csv", low_memory=False)
keep_e = ["c", "y"] + [c for c in e.columns if (c.startswith("spt_") or c.startswith("ln_apt_") or c.startswith("ln_spt_")) and c not in p.columns]
p = p.merge(e[keep_e], on=["c", "y"], how="left")
for f, cols in [("_macro_channels.csv", ["ln_tr_hivw", "ln_tr_diff", "ln_nflow"]), ("_wdi_mech.csv", ["tour_arrivals", "tour_rcpt_exp"]), ("_airport_gini.csv", ["ap_gini", "n_air"]),
                ("_hub_components.csv", ["hub_eig", "hub_cap", "hub_deg", "hub_close", "hub_betw", "hub_regimp", "rest_deg", "rest_cap"]), ("../GACI_CO2/spillover_bands.csv", ["nbr_g_contig", "nbr_f_contig", "has_contig", "nbr_g_b1", "nbr_f_b1"])]:
    x = pd.read_csv(f, **RD, low_memory=False); x = x[["c", "y"] + [k for k in cols if k in x.columns]]
    for k in x.columns:
        if k not in ("c", "y"): x[k] = pd.to_numeric(x[k], errors="coerce")
    p = p.merge(x, on=["c", "y"], how="left", suffixes=("", "_dup"))
p = p.loc[:, ~p.columns.str.endswith("_dup")]
num = [c for c in p.columns if c not in ("c", "reg")]
for c in num: p[c] = pd.to_numeric(p[c], errors="coerce")
p["ln_tour"] = np.log(p.tour_arrivals.where(p.tour_arrivals > 0))
p["cont"] = p.reg.astype(str).str[:2]
# derived groups
S = lambda *ds: sum(p["spt_" + d] for d in ds)
p["spt_b30"] = S("d1", "d2", "d3"); p["spt_mid40"] = S("d4", "d5", "d6", "d7"); p["spt_top30"] = S("d8", "d9", "d10"); p["spt_tophalf"] = S("d6", "d7", "d8", "d9", "d10")
for g, sz in [("b30", 0.3), ("mid40", 0.4), ("top30", 0.3), ("tophalf", 0.5)]:
    p["ln_apt_" + g] = np.log(p["spt_" + g] / sz) + p.ln_apt_all; p["ln_spt_" + g] = np.log(p["spt_" + g])
p["gap_top30_b30"] = p.ln_apt_top30 - p.ln_apt_b30; p["gap_d10_b50"] = p.ln_apt_d10 - p.ln_apt_b50; p["gap_t1_d10"] = p.ln_apt_t1 - p.ln_apt_d10; p["gap_tophalf_bothalf"] = p.ln_apt_tophalf - p.ln_apt_b50
p["ln_palma"] = np.log(p.spt_d10 / S("d1", "d2", "d3", "d4")); gap = np.exp(p.ln_apt_d10) - np.exp(p.ln_apt_b50); p["ln_absgap"] = np.log(gap.where(gap > 0))
p["gap_d5_d1"] = p.ln_apt_d5 - p.ln_apt_d1
# 2026-10-01: all WID group shares by the identity ln share = ln group income - ln mean income + ln group size, so that every
# share regression uses the full sample (the recorded shares of the bottom two deciles are rounded to zero in 272 / 57 country-years)
for g_, sz in [("d1", .1), ("d2", .1), ("d3", .1), ("d4", .1), ("d5", .1), ("d6", .1), ("d7", .1), ("d8", .1), ("d9", .1), ("d10", .1), ("t1", .01), ("t01", .001), ("b50", .5), ("m40", .4)]:
    p["ln_spt_" + g_] = p["ln_apt_" + g_] - p.ln_apt_all + np.log(sz)
p["post_minus_pre_b50"] = p.ln_bot50_post_wid - p.ln_bot50_wid; p["post_minus_pre_t10"] = p.ln_top10_post_wid - p.ln_top10_wid
p["ln_gaci_rest"] = np.log((p.gaci_sum - p.gaci_max).where(lambda s: s > 0))
for k in ["hub_eig", "hub_cap", "hub_deg", "hub_close", "hub_regimp", "rest_cap"]: p["ln_" + k] = np.log(p[k].where(p[k] > 0))
p["nbr_g"] = p.nbr_g_contig; p["nbr_f"] = p.nbr_f_contig
# estimation sample
CORE = ["ln_apt_all", "spt_d1", "spt_d10", "ln_gaci_max", "lnpop", "feyrer_int"]
p = p.dropna(subset=CORE).copy(); p = p[(p.y >= 1996) & (p.y <= 2023)]
print("WID sample:", len(p), "country-years,", p.c.nunique(), "countries")
# baselines (earliest observed) and splits
b0 = p.sort_values("y").groupby("c").first()
base = pd.DataFrame({"g0": b0.ln_gaci_max, "urb0": b0.urban, "tour0": b0.tour_rcpt_exp, "apg0": b0.ap_gini, "trade0": b0.trade_gdp, "gdp0": b0.ln_gdppc, "land0": b0.lnland, "lat0": b0.abslat, "sea0": b0.ln_sea_ma, "b30sh0": np.log(b0.spt_b30)})
for v in ["g0", "urb0", "tour0", "apg0", "trade0", "gdp0"]:
    base[v + "_hi"] = (base[v] > base[v].median()).astype(float).where(base[v].notna())
base["g0_ter"] = pd.qcut(base.g0, 3, labels=["low", "mid", "high"]); base["g0_q"] = pd.qcut(base.g0, 4, labels=["q1", "q2", "q3", "q4"]); base["gdp0_ter"] = pd.qcut(base.gdp0, 3, labels=["low", "mid", "high"])
p = p.merge(base, left_on="c", right_index=True, how="left")
for v in ["gdp0", "b30sh0", "land0", "lat0", "sea0"]: p[v + "_x_a"] = p[v] * p.a_t
for k in range(1, 11): p[f"L{k}_g"] = p.groupby("c").ln_gaci_max.shift(k); p[f"L{k}_z"] = p.groupby("c").feyrer_int.shift(k)
p = p.sort_values(["c", "y"]).reset_index(drop=True)

# ---------------------------------------------------------------- estimators
rows = []
def kpF(fs, z):
    if isinstance(z, str): return (fs.coef()[z] / fs.se()[z]) ** 2
    idx = [list(fs.coef().index).index(k) for k in z]; b = fs.coef()[z].values; V = fs._vcov[np.ix_(idx, idx)]; return float(b @ np.linalg.solve(V, b) / len(z))
def est(d, o, x="ln_gaci_max", z="feyrer_int", ctrl=None, vcov=None, block="", panel="", spec="", sample="", label=None, keep=None, rf=True):
    """2SLS of o on x (instrumented by z) with controls; records x (and controls if keep) rows. rf: reduced-form p of z on o."""
    ctrl = ctrl or []; need = [o, x, "lnpop"] + ctrl + ([z] if isinstance(z, str) else z); d = d.dropna(subset=need)
    if d.c.nunique() < 15: return None
    vc = vcov or {"CRV1": "c"}; rhs = " + ".join(["lnpop"] + ctrl); zz = z if isinstance(z, str) else " + ".join(z)
    fs = pf.feols(f"{x} ~ {zz} + {rhs} | c + y", d, vcov=vc); iv = pf.feols(f"{o} ~ {rhs} | c + y | {x} ~ {zz}", d, vcov=vc)
    F = kpF(fs, z); rfp = np.nan
    if rf and isinstance(z, str): rfp = pf.feols(f"{o} ~ {z} + {rhs} | c + y", d, vcov=vc).pvalue()[z]
    out = dict(block=block, panel=panel, spec=spec, sample=sample, outcome=o, term=label or x, b=iv.coef()[x], se=iv.se()[x], p=iv.pvalue()[x], kpf=F, N=len(d), n_c=d.c.nunique(), rf_p=rfp, fs_b=fs.coef()[z] if isinstance(z, str) else np.nan, fs_se=fs.se()[z] if isinstance(z, str) else np.nan)
    rows.append(out)
    for k in (keep or []): rows.append(dict(block=block, panel=panel, spec=spec, sample=sample, outcome=o, term=k, b=iv.coef()[k], se=iv.se()[k], p=iv.pvalue()[k], kpf=F, N=len(d), n_c=d.c.nunique(), rf_p=np.nan, fs_b=np.nan, fs_se=np.nan))
    return iv
def ols(d, o, x="ln_gaci_max", ctrl=None, block="", panel="", spec="", sample="", label=None, keep=None):
    ctrl = ctrl or []; d = d.dropna(subset=[o, x, "lnpop"] + ctrl); rhs = " + ".join([x, "lnpop"] + ctrl)
    f = pf.feols(f"{o} ~ {rhs} | c + y", d, vcov={"CRV1": "c"})
    rows.append(dict(block=block, panel=panel, spec=spec, sample=sample, outcome=o, term=label or x, b=f.coef()[x], se=f.se()[x], p=f.pvalue()[x], kpf=np.nan, N=len(d), n_c=d.c.nunique(), rf_p=np.nan, fs_b=np.nan, fs_se=np.nan))
    for k in (keep or []): rows.append(dict(block=block, panel=panel, spec=spec, sample=sample, outcome=o, term=k, b=f.coef()[k], se=f.se()[k], p=f.pvalue()[k], kpf=np.nan, N=len(d), n_c=d.c.nunique(), rf_p=np.nan, fs_b=np.nan, fs_se=np.nan))

# Conley (spatial HAC, Bartlett in great-circle distance, all time lags within the cutoff) for the 2SLS coefficient
co = pd.read_csv("_panel_coords.csv", usecols=["c", "lat", "lon"]).drop_duplicates("c").set_index("c")
def conley_se(d, o, x="ln_gaci_max", z="feyrer_int", cutoff_km=1000.0):
    d = d.dropna(subset=[o, x, "lnpop", z]); d = d[d.c.isin(co.index)]; d = d[d.groupby("c").c.transform("size") > 1]
    r = lambda v: pf.feols(f"{v} ~ lnpop | c + y", d).resid()
    y, X, Z = r(o), r(x), r(z); Xh = Z * (Z @ X) / (Z @ Z); b = (Xh @ y) / (Xh @ X); u = y - X * b
    lat = np.radians(co.loc[d.c, "lat"].values); lon = np.radians(co.loc[d.c, "lon"].values)
    dl = lat[:, None] - lat[None, :]; dn = lon[:, None] - lon[None, :]
    h = np.sin(dl / 2) ** 2 + np.cos(lat)[:, None] * np.cos(lat)[None, :] * np.sin(dn / 2) ** 2; dist = 6371.0 * 2 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
    K = np.clip(1 - dist / cutoff_km, 0, None); cc = d.c.to_numpy(dtype=object); same = (cc[:, None] == cc[None, :]); K[same] = 1.0
    g = Xh * u; meat = g @ K @ g; se = np.sqrt(meat) / abs(Xh @ X); return b, se, 2 * (1 - stats.norm.cdf(abs(b / se))), len(d)

# ---------------------------------------------------------------- 0. summary statistics
# 2026-10-02 (user): levels instead of logs, shares in percent, no instrument row
for g_ in ["top30", "mid40", "b30", "b50", "d10"]: p["pct_" + g_] = 100 * p["spt_" + g_]
p["pop_m"] = np.exp(p.lnpop) / 1e6; p["gdppc_k"] = np.exp(p.ln_gdppc) / 1e3
sv = [("pct_top30", "Top 30% share of pretax income, %"), ("pct_mid40", "Middle 40% (p30--70) share, %"), ("pct_b30", "Bottom 30% share, %"), ("pct_b50", "Bottom 50% share, %"), ("pct_d10", "Top 10% share, %"),
      ("gaci_max", "Hub connectivity, GACI max"), ("gaci_cwmean", "Hub quality, GACI cwm"), ("gaci_sum", "Total connectivity, GACI sum"), ("ap_gini", "Gini of GACI across a country's airports"), ("pop_m", "Population, millions"), ("gdppc_k", "GDP per capita, thousand constant 2015 US dollars")]
ss = []
for v, lab in sv:
    s = p[v].dropna(); w = (p[v] - p.groupby("c")[v].transform("mean")).dropna()
    ss.append(dict(var=lab, N=len(s), mean=s.mean(), sd=s.std(), within=w.std(), min=s.min(), max=s.max()))
pd.DataFrame(ss).to_csv("_wid_sumstat.csv", index=False)

# ---------------------------------------------------------------- 1. main table
MAINO = ["ln_apt_all", "ln_apt_top30", "ln_apt_b30", "ln_spt_b30", "gap_top30_b30"]
for x, lab in [("ln_gaci_max", "max"), ("ln_gaci_cwm", "cwm"), ("ln_gaci_sum", "sum")]:
    for o in MAINO:
        est(p, o, x=x, block="main", panel=lab, spec="2SLS"); ols(p, o, x=x, block="main", panel=lab, spec="OLS")

# ---------------------------------------------------------------- 2. incidence
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01", "b50", "m40", "b30", "mid40", "top30", "all"]
for g in G:
    est(p, "ln_apt_" + g, block="incidence", panel="income", spec="2SLS"); ols(p, "ln_apt_" + g, block="incidence", panel="income", spec="OLS")
    if g != "all": est(p, "ln_spt_" + g, block="incidence", panel="share", spec="2SLS"); ols(p, "ln_spt_" + g, block="incidence", panel="share", spec="OLS")
for o in ["gap_top30_b30", "gap_tophalf_bothalf", "gap_d10_b50", "gap_t1_d10"]: est(p, o, block="incidence", panel="diff", spec="2SLS")

# ---------------------------------------------------------------- 3. growth and incidence by baseline hub size
GO = ["ln_gdppc", "ln_apt_all", "ln_apt_b30", "ln_spt_b30", "gap_top30_b30"]
for grp, col, vals in [("median", "g0_hi", [(0.0, "below"), (1.0, "above")]), ("tercile", "g0_ter", [("low", "low"), ("mid", "mid"), ("high", "high")]), ("quartile", "g0_q", [("q1", "q1"), ("q2", "q2"), ("q3", "q3"), ("q4", "q4")])]:
    for val, nm in vals:
        d = p[p[col] == val]
        for o in GO: est(d, o, block="growth_stage", panel=grp, spec="2SLS", sample=nm); ols(d, o, block="growth_stage", panel=grp, spec="OLS", sample=nm)
for o in GO: est(p, o, block="growth_stage", panel="full", spec="2SLS", sample="full"); ols(p, o, block="growth_stage", panel="full", spec="OLS", sample="full")

# ---------------------------------------------------------------- 4. hub vs network
for o in ["ln_spt_b30", "gap_top30_b30", "ln_apt_b30", "ln_apt_all"]:
    est(p, o, block="hub_network", spec="baseline")
    est(p, o, ctrl=["ln_gaci_sum"], keep=["ln_gaci_sum"], block="hub_network", spec="hub_ctrl_sum")
    est(p, o, ctrl=["ln_gaci_rest"], keep=["ln_gaci_rest"], block="hub_network", spec="hub_ctrl_rest")
    est(p, o, x="ln_hub_eig", ctrl=["ln_hub_cap"], keep=["ln_hub_cap"], block="hub_network", spec="eig_iv_ctrl_cap", label="ln_hub_eig")
    ols(p, o, x="ln_hhi", ctrl=["ln_gaci_sum"], keep=["ln_gaci_sum"], block="hub_network", spec="ols_hhi", label="ln_hhi")
    ols(p, o, x="ln_share_max", ctrl=["ln_gaci_sum"], keep=["ln_gaci_sum"], block="hub_network", spec="ols_share_max", label="ln_share_max")

# ---------------------------------------------------------------- 5. channel decomposition (mediator instrumented, no hub)
MED = [("ln_gdppc", "ln GDP per capita"), ("ln_tr_diff", "ln differentiated-goods trade"), ("ln_tr_hivw", "ln high value-to-weight trade"), ("ln_tour", "ln international tourist arrivals"), ("emp_ind", "Employment in industry, %"), ("ln_nflow", "ln number of export partners"), ("trade_gdp", "Trade, % of GDP"), ("urban", "Urban population, %")]
CO = ["ln_apt_all", "ln_apt_top30", "ln_apt_mid40", "ln_apt_b30", "ln_spt_top30", "ln_spt_mid40", "ln_spt_b30", "gap_top30_b30"]
for m, lab in MED:
    est(p, m, block="channels", panel="apath", spec="2SLS", label="ln_gaci_max")           # a: GACI_max -> M
    for o in CO: est(p, o, x=m, block="channels", panel="theta", spec="2SLS", label=m)      # theta: o on M-hat (legacy rescaling)
for o in CO: est(p, o, block="channels", panel="reference", spec="2SLS")
# 2026-10-01 decomposition (Gelbach-type, user decision): total = direct (hub, channel held fixed) + indirect (a x theta_M)
# 'total' is re-estimated on the channel's sample so that direct + indirect = total exactly; 'direct' keeps the channel coefficient (term = M)
for m, lab in MED:
    dm = p.dropna(subset=[m])
    for o in CO:
        est(dm, o, block="channels", panel="decomp", spec="total", sample=m)
        est(dm, o, ctrl=[m], keep=[m], block="channels", panel="decomp", spec="direct", sample=m)
MED5 = [m for m, _ in MED[:5]]; d5 = p.dropna(subset=MED5)
for o in CO:
    est(d5, o, block="channels", panel="decomp", spec="total", sample="all5")
    est(d5, o, ctrl=MED5, keep=MED5, block="channels", panel="decomp", spec="direct", sample="all5")

# ---------------------------------------------------------------- 6. splits (where)
SO = ["ln_spt_b30", "ln_apt_b30", "ln_apt_all", "gap_top30_b30"]
for lab, col in [("airport_concentration", "apg0_hi"), ("urbanisation", "urb0_hi"), ("tourism_dependence", "tour0_hi"), ("trade_openness", "trade0_hi"), ("baseline_income", "gdp0_hi")]:
    for val, nm in [(1.0, "above"), (0.0, "below")]:
        for o in SO: est(p[p[col] == val], o, block="splits", panel=lab, spec="2SLS", sample=nm)
for nm, cond in [("1996-2007", (p.y <= 2007)), ("2010-2023", (p.y >= 2010) & ~p.y.isin([2020, 2021])), ("1996-2019", (p.y <= 2019))]:
    for o in SO: est(p[cond], o, block="splits", panel="era", spec="2SLS", sample=nm)
# spillover: own + contiguous neighbours jointly (own shifter, neighbours' shifter)
d = p.dropna(subset=["nbr_g", "nbr_f", "has_contig"])
for o in SO:
    try:
        dd = d.dropna(subset=[o]); dd = dd[dd.groupby("c").c.transform("size") > 1]
        r_ = lambda v: pf.feols(f"{v} ~ lnpop + has_contig | c + y", dd).resid()
        y = r_(o); X = np.column_stack([r_("ln_gaci_max"), r_("nbr_g")]); Z = np.column_stack([r_("feyrer_int"), r_("nbr_f")])
        Pz = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X); b = np.linalg.solve(Pz.T @ X, Pz.T @ y); u = y - X @ b; A = np.linalg.inv(Pz.T @ X)
        cl = dd.c.to_numpy(dtype=object); Gc = len(np.unique(cl)); meat = sum(np.outer(Pz[cl == g].T @ u[cl == g], Pz[cl == g].T @ u[cl == g]) for g in np.unique(cl)); V = A @ meat @ A.T * Gc / (Gc - 1)
        for i, k in enumerate(["ln_gaci_max", "nbr_g"]):
            se = np.sqrt(V[i, i]); rows.append(dict(block="spill", panel="joint_contig", spec="2SLS", sample="", outcome=o, term=k, b=b[i], se=se, p=2 * (1 - stats.t.cdf(abs(b[i] / se), Gc - 1)), kpf=np.nan, N=len(dd), n_c=Gc, rf_p=np.nan, fs_b=np.nan, fs_se=np.nan))
    except Exception as ex: print("spill skip", o, ex)

# ---------------------------------------------------------------- 7. redistribution (WID pretax vs post-tax)
for o in ["ln_bot50_wid", "ln_bot50_post_wid", "post_minus_pre_b50", "ln_top10_wid", "ln_top10_post_wid", "post_minus_pre_t10"]: est(p, o, block="redistribution", spec="2SLS"); ols(p, o, block="redistribution", spec="OLS")

# ---------------------------------------------------------------- 8. robustness
RO = ["ln_spt_b30", "gap_top30_b30", "ln_apt_all"]
top10 = p.groupby("c").gaci_max.mean().nlargest(10).index
for nm, d in [("baseline", p), ("drop_top10_hubs", p[~p.c.isin(top10)]), ("pre2020", p[p.y <= 2019]), ("drop_crises", p[~p.y.isin([2008, 2009, 2020, 2021])])]:
    for o in RO: est(d, o, block="robust", panel="sample", spec=nm)
for o in RO: est(p, o, ctrl=["gdp0_x_a", "b30sh0_x_a", "land0_x_a", "lat0_x_a", "sea0_x_a"], block="robust", panel="exposure", spec="exposure_trends")
# 2026-10-02 exclusion-restriction checks (Feyrer-style): one competing exposure x shifter at a time
for o in RO:
    est(p, o, ctrl=["sea0_x_a"], block="robust", panel="exclusion", spec="sea_ma_x_a")
    est(p, o, ctrl=["gdp0_x_a"], block="robust", panel="exclusion", spec="gdp0_x_a")
    est(p, o, ctrl=["land0_x_a"], block="robust", panel="exclusion", spec="land0_x_a")
for o in RO:
    est(p, o, vcov={"CRV1": "c"}, block="robust", panel="inference", spec="cluster_country"); est(p, o, vcov={"CRV1": "c+y"}, block="robust", panel="inference", spec="twoway_country_year")
    for cut in [1000.0, 2000.0]:
        b, se, pv, n = conley_se(p, o, cutoff_km=cut); rows.append(dict(block="robust", panel="inference", spec=f"conley_{int(cut)}", sample="", outcome=o, term="ln_gaci_max", b=b, se=se, p=pv, kpf=np.nan, N=n, n_c=np.nan, rf_p=np.nan, fs_b=np.nan, fs_se=np.nan))
# ---------------------------------------------------------------- 9. measures
for x, lab in [("ln_gaci_max", "max"), ("ln_gaci_cwm", "cwm"), ("ln_gaci_sum", "sum")]:
    for o in ["ln_spt_b30", "ln_spt_b50", "gap_top30_b30", "gap_d10_b50", "ln_palma", "ln_absgap", "ln_gini_pre_wid", "ln_spt_d10", "ln_spt_t1"]:
        est(p, o, x=x, block="measures", panel=lab, spec="2SLS"); ols(p, o, x=x, block="measures", panel=lab, spec="OLS")
# ---------------------------------------------------------------- 10. lags
for k in range(0, 11):
    for o in RO: est(p, o, x="ln_gaci_max" if k == 0 else f"L{k}_g", z="feyrer_int" if k == 0 else f"L{k}_z", block="lags", spec=str(k), label="ln_gaci_max")
# ---------------------------------------------------------------- 11. stage definitions (baseline GDP terciles, era already; add GDP tercile)
for val in ["low", "mid", "high"]:
    for o in GO: est(p[p.gdp0_ter == val], o, block="stagedefs", panel="gdp_tercile", spec="2SLS", sample=val)
# ---------------------------------------------------------------- 12. components one at a time
for x in ["ln_hub_eig", "ln_hub_cap", "ln_hub_deg", "ln_hub_close", "ln_hub_regimp"]:
    for o in ["ln_spt_b30", "gap_top30_b30", "ln_apt_all"]: est(p, o, x=x, block="components", spec="2SLS", label=x)
# ---------------------------------------------------------------- 13. SWIID subsample (survey-based Gini available)
sw = p.dropna(subset=["ln_gini_mkt"])
for o in ["ln_gini_mkt", "ln_gini_disp", "ln_apt_all", "ln_apt_top30", "ln_apt_b30", "ln_spt_b30", "ln_apt_b50", "ln_spt_b50", "gap_top30_b30", "gap_tophalf_bothalf"]:
    est(sw, o, block="swiid_subsample", spec="2SLS"); ols(sw, o, block="swiid_subsample", spec="OLS")
for g in ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "b50", "all"]:
    est(sw, "ln_apt_" + g, block="swiid_subsample", panel="income", spec="2SLS")
    if g != "all": est(sw, "ln_spt_" + g, block="swiid_subsample", panel="share", spec="2SLS")

R = pd.DataFrame(rows); R.to_csv("_wid_results.csv", index=False)
# ---------------------------------------------------------------- 14. aggregate: implied change in bottom-30 share, 1996 -> last
g = R[(R.block == "main") & (R.panel == "max") & (R.spec == "2SLS")].set_index("outcome")
el_b30sh, el_all, el_b30, el_top30 = g.loc["ln_spt_b30", "b"], g.loc["ln_apt_all", "b"], g.loc["ln_apt_b30", "b"], g.loc["ln_apt_top30", "b"]
first = p.sort_values("y").groupby("c").first(); last = p.sort_values("y").groupby("c").last()
ag = pd.DataFrame({"cont": first.cont, "y0": first.y, "y1": last.y, "pop1": np.exp(last.lnpop), "dln": last.ln_gaci_max - first.ln_gaci_max, "sh0": first.spt_b30, "sh1": last.spt_b30, "all0": first.ln_apt_all, "all1": last.ln_apt_all, "b30_0": first.ln_apt_b30, "b30_1": last.ln_apt_b30})
ag = ag[(ag.y1 - ag.y0) >= 15].copy()
ag["implied_b30sh_pts"] = 100 * ag.sh0 * (np.exp(el_b30sh * ag.dln) - 1); ag["actual_b30sh_pts"] = 100 * (ag.sh1 - ag.sh0)
ag["implied_all_pct"] = 100 * (np.exp(el_all * ag.dln) - 1); ag["actual_all_pct"] = 100 * (np.exp(ag.all1 - ag.all0) - 1)
ag["implied_b30_pct"] = 100 * (np.exp(el_b30 * ag.dln) - 1); ag["actual_b30_pct"] = 100 * (np.exp(ag.b30_1 - ag.b30_0) - 1); ag["implied_top30_pct"] = 100 * (np.exp(el_top30 * ag.dln) - 1)
ag.reset_index().to_csv("_wid_aggregate_bycountry.csv", index=False)
cols = ["dln", "implied_all_pct", "actual_all_pct", "implied_top30_pct", "implied_b30_pct", "actual_b30_pct", "implied_b30sh_pts", "actual_b30sh_pts"]
byc = ag.groupby("cont")[cols].mean(); byc["n"] = ag.groupby("cont").size(); byc.loc["ALL (unweighted)"] = ag[cols].mean().tolist() + [len(ag)]
wm = lambda v: np.average(ag[v], weights=ag.pop1); byc.loc["WORLD (pop-weighted)"] = [wm(v) for v in cols] + [len(ag)]
byc.to_csv("_wid_aggregate_bycontinent.csv")
print("results rows:", len(R)); print(R.groupby("block").size().to_dict())
print(byc.round(2).to_string())
