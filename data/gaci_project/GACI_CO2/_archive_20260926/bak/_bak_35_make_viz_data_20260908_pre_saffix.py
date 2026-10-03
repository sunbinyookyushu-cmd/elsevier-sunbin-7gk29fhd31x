# -*- coding: utf-8 -*-
"""
35_make_viz_data_20260908.py   (2026-09-08)
Visualization-ready workbook for the 2026-09-06 candidate manuscript
(FINAL_20260906/main_co2_nature_20260906.tex, country-clustered SE).
One sheet per display (main Tables 1-4, Figs 1-3, Extended Data tables and
figures), each in tidy long format with labels, 95% CI and significance flags,
plus country-level map data (2023) and the country-year panel for time series.
Output: CO2_visualization_data_20260908.xlsx (GACI_CO2 root and FINAL_20260906/)
"""
import os, sys, math, shutil
import numpy as np
import pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
GACI = os.path.dirname(HERE)
OUT = os.path.join(HERE, "CO2_visualization_data_20260908.xlsx")
rd = lambda fn: pd.read_csv(os.path.join(HERE, fn))

def pval(b, se):
    return 2 * (1 - norm.cdf(np.abs(np.asarray(b, float) / np.asarray(se, float))))
def stars(p):
    return np.where(p < .01, "***", np.where(p < .05, "**", np.where(p < .10, "*", "")))
def add_ci(df, b="b", se="se", p="p"):
    df = df.copy()
    if p not in df or df[p].isna().all():
        df[p] = pval(df[b], df[se])
    df["ci_lo"] = df[b] - 1.96 * df[se]
    df["ci_hi"] = df[b] + 1.96 * df[se]
    df["stars"] = stars(df[p].fillna(1.0))
    df["sig05"] = (df[p] < .05).astype(int)
    return df

try:
    import pycountry
    def cname(iso3):
        extra = {"XKX": "Kosovo", "TWN": "Taiwan", "KOR": "Korea, Republic of", "RUS": "Russia",
                 "IRN": "Iran", "SYR": "Syria", "LAO": "Laos", "VNM": "Viet Nam", "BOL": "Bolivia",
                 "VEN": "Venezuela", "TZA": "Tanzania", "COD": "Congo, Dem. Rep.", "COG": "Congo, Rep.",
                 "PRK": "Korea, DPR", "MDA": "Moldova", "CZE": "Czechia", "TUR": "Turkey", "USA": "United States",
                 "GBR": "United Kingdom", "ARE": "United Arab Emirates", "FSM": "Micronesia", "BRN": "Brunei",
                 "CIV": "Cote d'Ivoire", "MKD": "North Macedonia", "SWZ": "Eswatini", "CPV": "Cabo Verde"}
        if iso3 in extra: return extra[iso3]
        c = pycountry.countries.get(alpha_3=iso3)
        return c.name if c else iso3
except Exception:
    cname = lambda x: x

OUTC = {"ln_co2_tot": "Bunker CO2 (total)", "ln_co2_intl": "International CO2", "ln_skm": "Seat-km",
        "ln_intensity": "CO2 per seat-km", "ln_co2_lto": "Territorial (LTO) CO2", "ln_co2_5050": "50/50 CO2",
        "ln_flights": "Flights", "ln_gauge": "Seats per flight (gauge)", "ln_stage": "Km per flight (stage length)",
        "ln_co2": "Bunker CO2 (total)", "lto_share": "LTO share of CO2", "intl_share": "International share of seat-km"}
sheets = {}   # name -> (df, readme row)
def put(name, df, display, plot, source):
    sheets[name] = (df, {"sheet": name, "manuscript_display": display, "what_to_plot": plot, "source": source, "rows": len(df)})

# ============================================================ Table 1 (+ ED Table 2, SI Table 3)
a = rd("_allest_results_cl.csv"); m6 = rd("_measures6_cl.csv")
EST = {"OLS": ("A", "OLS", "ln GACI (cwm)"), "FeyrerIV": ("B", "2SLS, Feyrer instrument", "ln GACI (cwm)"),
       "HeritageIV": ("SI", "2SLS, tourism-heritage instrument", "ln GACI (cwm)"),
       "AccidentIV": ("SI", "2SLS, accident instrument (ASN)", "ln GACI (cwm)"),
       "Fey+AccOverID": ("SI", "2SLS, Feyrer + accident (overidentified)", "ln GACI (cwm)")}
MEAS = {"lng": ("C", "2SLS, GACI sum", "ln GACI (sum)"), "ln_gaci_max": ("D", "2SLS, GACI max", "ln GACI (max)"),
        "ln_gaci_mean": ("E", "2SLS, GACI mean", "ln GACI (mean)")}
rows = []
for _, r in a.iterrows():
    pn, lab, reg = EST[r.est]
    rows.append(dict(panel=pn, estimator=lab, regressor=reg, outcome=r.outc, outcome_label=OUTC[r.outc], b=r.b, se=r.se, p=r.p, kp_f=r.kpf, hansen_p=r.jp, N=r.nn))
for _, r in m6.iterrows():
    pn, lab, reg = MEAS[r.meas]
    rows.append(dict(panel=pn, estimator=lab, regressor=reg, outcome=r.outc, outcome_label=OUTC[r.outc], b=r.b, se=r.se, p=r.p, kp_f=r.kpf, hansen_p=np.nan, N=r.nn))
t1 = add_ci(pd.DataFrame(rows))
t1["in_main_table1"] = ((t1.panel.isin(list("ABCDE"))) & t1.outcome.isin(["ln_co2_tot", "ln_co2_intl", "ln_skm", "ln_intensity"])).astype(int)
t1["display"] = np.where(t1.in_main_table1 == 1, "Table 1", np.where(t1.panel == "SI", "SI Table 3 / Supp.", "ED Table 2 (allocation rules)"))
t1 = t1.sort_values(["panel", "outcome"], key=lambda s: s.map({k: i for i, k in enumerate(list("ABCDE") + ["SI"])}) if s.name == "panel" else s.map({k: i for i, k in enumerate(OUTC)}))
put("T1_main", t1, "Table 1 (Panels A-E); ED Table 2 (LTO, 50/50); SI Table 3 (other IVs)",
    "Coefficient plot by outcome x estimator (b, ci_lo, ci_hi); dashed line at 1 = unit elasticity", "_allest_results_cl.csv, _measures6_cl.csv (co2_allestimators_cl.do, co2_extensions_cl.do)")

# ============================================================ Table 2 decomposition + ED Fig 2 waterfall
mech = rd("_feyrer_mechanism_cl.csv").set_index("outc")
tot = mech.loc["ln_co2_tot", "b"]
comp = [("ln_flights", "Flights (frequency)", "Scale", 1), ("ln_gauge", "Seats per flight (aircraft gauge)", "Scale", 2),
        ("ln_stage", "Km per flight (stage length)", "Scale", 3), ("ln_skm", "Subtotal: scale (seat-km)", "Subtotal", 4),
        ("ln_intensity", "CO2 per seat-km (carbon intensity)", "Efficiency", 5), ("ln_co2_tot", "Total CO2", "Total", 6),
        ("lto_share", "LTO share of CO2 (memo, pp)", "Composition (memo)", 7), ("intl_share", "International share of seat-km (memo, pp)", "Composition (memo)", 8)]
rows = []
cum = 0.0
for k, lab, grp, o in comp:
    r = mech.loc[k]
    d = dict(order=o, component=k, label=lab, group=grp, b=r.b, se=r.se, kp_f=r.kpf, N=r.nn,
             share_of_total_pct=(100 * r.b / tot if grp in ("Scale", "Subtotal", "Efficiency", "Total") else np.nan))
    if grp in ("Scale", "Efficiency"):
        d["waterfall_start"] = cum; cum += r.b; d["waterfall_end"] = cum
    elif grp in ("Subtotal", "Total"):
        d["waterfall_start"] = 0.0; d["waterfall_end"] = r.b
    rows.append(d)
t2 = add_ci(pd.DataFrame(rows))
put("T2_decomp", t2, "Table 2; ED Fig 2 (waterfall)", "Waterfall: bars from waterfall_start to waterfall_end for Scale/Efficiency rows, Total as final bar; error bars 1.96*se",
    "_feyrer_mechanism_cl.csv (co2_feyrer_mechanism_cl.do)")

# ============================================================ Fig 1 heterogeneity (+ ED Table 3)
h = rd("_feyrer_hetero_tot_cl.csv").rename(columns={"KPF": "kp_f"})
PAN = {"A_income": "A. Total CO2 by baseline income", "B_conn": "B. Total CO2 by baseline connectivity",
       "C_region": "C. Total CO2 by region", "D_intens": "D. Intensity by baseline income"}
GL = {"inc_low": "Low income", "inc_mid": "Middle income", "inc_high": "High income", "interact_hi": "Interaction: high tercile x ln GACI (pooled)",
      "con_low": "Low connectivity", "con_mid": "Middle connectivity", "con_high": "High connectivity",
      "Europe": "Europe", "AsiaPacific": "Asia-Pacific", "Africa": "Africa", "LatAm": "Latin America", "MiddleEast": "Middle East", "NorthAm": "North America"}
h["panel_label"] = h.panel.map(PAN); h["group_label"] = h.grp.map(GL)
h["in_figure"] = (~h.grp.str.startswith("interact") & ~h.grp.isin(["MiddleEast", "NorthAm"])).astype(int)
h["note"] = np.where(h.grp.isin(["MiddleEast", "NorthAm"]), "unidentified (omitted from figure)", np.where(h.grp.str.startswith("interact"), "pooled interaction term (ED Table 3 only)", ""))
h = add_ci(h)
h["order_in_panel"] = h.groupby("panel").cumcount() + 1
put("F1_hetero", h[["panel", "panel_label", "order_in_panel", "grp", "group_label", "b", "se", "p", "ci_lo", "ci_hi", "stars", "sig05", "kp_f", "N", "Nc", "in_figure", "note"]],
    "Fig 1 (four-panel coefficient plot); ED Table 3", "Dot-and-whisker per panel; filled marker if sig05 = 1; vertical line at 0",
    "_feyrer_hetero_tot_cl.csv (co2_feyrer_hetero_tot_cl.do)")

# ============================================================ Table 3 spatial (+ ED Table 10)
sp = rd("_spatial_models.csv")
TERM = {"beta": "ln GACI (own)", "theta": "W ln GACI (neighbours)", "rho": "W ln CO2 (spatial lag, rho)", "lambda": "W u (spatial error, lambda)",
        "direct": "Direct effect", "indirect": "Indirect effect", "total": "Total effect"}
MODEL_ORDER = {"OLS": 1, "2SLS": 1, "SLX": 2, "SAR": 3, "SEM": 4, "SDM": 5, "SDEM": 6}
sp["panel"] = np.where(sp.estimator == "IV", "B. Own connectivity instrumented (spatial 2SLS)", "A. Connectivity exogenous (OLS / ML)")
sp["term_label"] = sp.term.map(TERM); sp["column"] = sp.model.map(MODEL_ORDER)
sp["W_label"] = sp.W.map({"contig": "Land contiguity (row-normalised)", "inv": "Inverse distance, all countries"})
sp["outcome_label"] = sp.outcome.map(OUTC)
sp = sp.rename(columns={"se_cl": "se"})
sp = add_ci(sp)
sp["se_note"] = np.where(sp.estimator == "ML", "Hessian s.e. (not clustered)", np.where(sp.term.isin(["lambda"]) & sp.se.isna(), "moments estimator, no s.e.", "clustered by country"))
cols = ["W", "W_label", "outcome", "outcome_label", "panel", "column", "model", "estimator", "term", "term_label", "b", "se", "se_rob", "p", "ci_lo", "ci_hi", "stars", "sig05", "N", "swf_beta", "swf_theta", "se_note"]
t3 = sp[(sp.W == "contig") & (sp.outcome == "ln_co2_tot")].sort_values(["panel", "column"])[cols]
put("T3_spatial", t3, "Table 3 (SLX/SAR/SEM/SDM/SDEM, contiguity W, bunker CO2)",
    "Grouped coefficient plot: own beta / neighbour theta / rho / lambda by model, Panel A vs B; or direct-indirect-total stacked bars", "_spatial_models.csv (32_spatial_models.py, 33_spatial_table.py)")
put("EDT10_spatial_ext", sp.sort_values(["W", "outcome", "panel", "column"])[cols], "ED Table 10 (inverse-distance W; international CO2 and intensity outcomes)",
    "Same as T3 for alternative W and outcomes (inverse-distance SAR-IV rho ~1 is a known blow-up)", "_spatial_models.csv")

# ============================================================ Country map data 2023 (Fig 2, Table 4, ED Figs 4-6)
cy = rd("co2_country_year.csv")
c23 = cy[cy.year == 2023].copy()
c23["bunker_mt_2023"] = c23.co2_bunker / 1e9; c23["lto_mt_2023"] = c23.co2_lto / 1e9; c23["co2_5050_mt_2023"] = c23.co2_5050 / 1e9
c23["bunker_intl_mt_2023"] = c23.co2_bunker_intl / 1e9
c23["share_bunker_pct"] = 100 * c23.co2_bunker / c23.co2_bunker.sum(); c23["share_lto_pct"] = 100 * c23.co2_lto / c23.co2_lto.sum()
c23["mismatch_pp"] = c23.share_bunker_pct - c23.share_lto_pct
c23["log10_bunker_mt"] = np.log10(c23.bunker_mt_2023.clip(lower=1e-3))
c23["flights_2023"] = c23.n_dep_flights; c23["seat_km_bn_2023"] = c23.dep_seat_km / 1e9
c23["intl_share_skm_2023"] = c23.dep_seat_km_intl / c23.dep_seat_km
c23["kg_co2_per_1000skm_2023"] = c23.co2_bunker / c23.dep_seat_km * 1000
att = rd("_attribution_scc.csv").rename(columns={"c": "iso3"})
att["att_tot_mt"] = att.att_tot_t / 1e6; att["att_intl_mt"] = att.att_intl_t / 1e6; att["e_tot_mt_attr_base"] = att.e_tot_t / 1e6
att["att_share_pct"] = 100 * att.att_tot_t / att.e_tot_t
for k in ["51", "185", "190"]:
    att[f"scc{k}_bn_usd"] = att[f"val_tot_scc{k}_usd"] / 1e9
att["asinh_att_mt_s2"] = np.arcsinh(att.att_tot_mt / 2.0)
gp = pd.read_csv(os.path.join(HERE, "gaci_co2_panel.csv"), usecols=["c", "y", "reg", "gaci_cwmean", "lnpc", "lnpop"])
g96 = gp[gp.y == 1996][["c", "gaci_cwmean", "reg"]].rename(columns={"c": "iso3", "gaci_cwmean": "gaci_cwm_1996"})
g23 = gp[gp.y == 2023][["c", "gaci_cwmean", "lnpc", "lnpop"]].rename(columns={"c": "iso3", "gaci_cwmean": "gaci_cwm_2023", "lnpc": "ln_gdp_pc_2023", "lnpop": "ln_pop_2023"})
mp = c23[["iso3", "bunker_mt_2023", "log10_bunker_mt", "bunker_intl_mt_2023", "lto_mt_2023", "co2_5050_mt_2023", "share_bunker_pct", "share_lto_pct", "mismatch_pp",
          "flights_2023", "seat_km_bn_2023", "intl_share_skm_2023", "kg_co2_per_1000skm_2023"]]
mp = mp.merge(att[["iso3", "dln_cwm", "att_tot_mt", "att_intl_mt", "att_share_pct", "scc51_bn_usd", "scc185_bn_usd", "scc190_bn_usd", "asinh_att_mt_s2"]], on="iso3", how="outer")
mp = mp.merge(g96, on="iso3", how="left").merge(g23, on="iso3", how="left")
mp = mp.rename(columns={"dln_cwm": "dln_gaci_1996_2023", "reg": "region_code"})
mp.insert(1, "country", mp.iso3.map(cname))
mp["in_attribution_sample"] = mp.att_tot_mt.notna().astype(int)
mp["rank_attributed"] = mp.att_tot_mt.rank(ascending=False)
mp = mp.sort_values("att_tot_mt", ascending=False)
put("MAP_country_2023", mp, "Fig 2 (attributed map: att_tot_mt, asinh scale); ED Fig 4 (bars); ED Fig 5 (levels: log10_bunker_mt); ED Fig 6 (mismatch_pp); Table 4",
    "Choropleths keyed on iso3; Fig 2 uses att_tot_mt with diverging RdBu_r on asinh(att/2), white = 0; ED Fig 5 YlGnBu on log10; ED Fig 6 RdBu_r on mismatch_pp",
    "_attribution_scc.csv (14_attribution_scc.py), co2_country_year.csv (01_build_co2_panel.py), gaci_co2_panel.csv")

# Table 4
top = att.sort_values("att_tot_mt", ascending=False).head(10)
deu = att[att.iso3 == "DEU"]
t4 = pd.concat([top, deu])
t4 = t4[["iso3", "dln_cwm", "att_tot_mt", "att_intl_mt", "scc51_bn_usd", "scc185_bn_usd", "scc190_bn_usd"]].rename(columns={"dln_cwm": "dln_gaci_1996_2023"})
t4.insert(1, "country", t4.iso3.map(cname))
world = dict(iso3="WLD", country="World (184 countries)", dln_gaci_1996_2023=np.nan, att_tot_mt=att.att_tot_mt.sum(), att_intl_mt=att.att_intl_mt.sum(),
             scc51_bn_usd=att.scc51_bn_usd.sum(), scc185_bn_usd=att.scc185_bn_usd.sum(), scc190_bn_usd=att.scc190_bn_usd.sum())
t4 = pd.concat([t4, pd.DataFrame([world])], ignore_index=True)
t4["world_share_of_attributed_pct"] = 100 * t4.att_tot_mt / att.att_tot_mt.sum()
put("T4_scc", t4, "Table 4 (top 10 + Germany + World)", "Bar chart of att_tot_mt or SCC values; world row = 42.5% of 2023 emissions (838 Mt)", "_attribution_scc.csv")

# ============================================================ Fig 3 SAF growth
BASE, ATTR = 838.0, 356.4
BETA = {"mature": 3.005, "full": 5.669}; GROWTH = {"central": 0.0074, "low": 0.0045}
PATH = {2023: 0.00, 2025: 0.02, 2030: 0.06, 2035: 0.20, 2040: 0.34, 2045: 0.42, 2050: 0.70}
MIL = sorted(PATH)
blend = lambda y: float(np.interp(y, MIL, [PATH[m] for m in MIL]))
rows = []
for bn, beta in BETA.items():
    for gn, g in GROWTH.items():
        for r in [0.0, 0.5, 0.65, 0.8]:
            for y in range(2023, 2051):
                rows.append(dict(beta_case=bn, beta=beta, growth_case=gn, dln_gaci_per_yr=g, co2_growth_pct_yr=100 * (math.exp(beta * g) - 1),
                                 scenario=("no SAF" if r == 0 else f"SAF, life-cycle saving r = {int(100*r)}%"), lca_saving_r=r, year=y, blend_share=blend(y),
                                 milestone=int(y in PATH), co2_Mt=BASE * math.exp(beta * g * (y - 2023)) * (1 - blend(y) * r),
                                 co2_Mt_fixed_2023_traffic=BASE * (1 - blend(y) * r), ref_2023_level=BASE, ref_2023_minus_attributed=BASE - ATTR))
saf = pd.DataFrame(rows)
saf["in_figure"] = ((saf.beta_case == "mature")).astype(int)
put("F3_saf", saf, "Fig 3 (two panels: central and low growth; mature beta 3.005)",
    "Lines: co2_Mt by year per scenario (no SAF dashed grey; r=50/65/80 solid); dotted red = co2_Mt_fixed_2023_traffic for r=65%; horizontal refs 838 and 482 Mt; x ticks at milestones with blend_share",
    "_saf_growth_scenarios.csv logic (31_saf_growth.py), recomputed annually")

# ============================================================ ED Fig 1 / ED Table 1 temporal
t_old = rd("_temporal_co2_cl.csv"); t_p8 = rd("_temporal_pre2008_cl.csv"); t_xc = rd("_temporal_excovid_cl.csv")
rows = []
for _, r in t_old[t_old.period == "full"].iterrows(): rows.append(dict(period="1996-2023 (full)", order=1, **r[["outc", "b", "se", "p", "kpf", "nn"]].to_dict()))
for _, r in t_p8[t_p8.samp == "1996-2007"].iterrows(): rows.append(dict(period="1996-2007 (network expansion)", order=2, **r[["outc", "b", "se", "p", "kpf", "nn"]].to_dict()))
for _, r in t_xc[t_xc.samp == "2010-2023_exCOVID"].iterrows(): rows.append(dict(period="2010-2023 excl. 2020-21 (mature)", order=3, **r[["outc", "b", "se", "p", "kpf", "nn"]].to_dict()))
for _, r in t_old[t_old.period == "2010-2023"].iterrows(): rows.append(dict(period="2010-2023 unrestricted (weak FS)", order=4, **r[["outc", "b", "se", "p", "kpf", "nn"]].to_dict()))
tp = pd.DataFrame(rows).rename(columns={"kpf": "kp_f", "nn": "N"})
tp["outcome_label"] = tp.outc.map(OUTC); tp["weak_first_stage"] = (tp.kp_f < 10).astype(int)
tp = add_ci(tp)
extra = pd.concat([t_p8.assign(src="pre2008 file"), t_xc.assign(src="excovid file")]).rename(columns={"samp": "period", "kpf": "kp_f", "nn": "N"})
extra["outcome_label"] = extra.outc.map(OUTC); extra = add_ci(extra)
put("EDF1_temporal", tp.sort_values(["outc", "order"], key=lambda s: s.map({k: i for i, k in enumerate(OUTC)}) if s.name == "outc" else s),
    "ED Fig 1; ED Table 1", "Dot-and-whisker grouped by outcome, 4 periods each (grey if weak_first_stage = 1)", "_temporal_co2_cl.csv, _temporal_pre2008_cl.csv, _temporal_excovid_cl.csv")
put("EDT1_temporal_all", extra[["src", "period", "outc", "outcome_label", "b", "se", "p", "ci_lo", "ci_hi", "stars", "kp_f", "N"]], "ED Table 1 (all sub-periods)", "Reference", "as above")

# ============================================================ ED Table 4 mediation
md = rd("_mediation_co2_cl.csv"); mi = rd("_mediation_imai.csv")
md["mediator_label"] = md.med.map({"ln_flights": "Flights", "ln_skm": "Seat-km", "intl_share": "International share of seat-km"})
mi["mediator_label"] = mi.med.map({"ln_flights": "Flights", "ln_skm": "Seat-km", "intl_share": "International share of seat-km"})
put("EDT4_mediation", pd.concat([md, mi], ignore_index=True), "ED Table 4", "Stacked bar: acme vs direct (cprime / ade) by mediator; prop = share mediated", "_mediation_co2_cl.csv, _mediation_imai.csv")

# ============================================================ ED Table 5 decomposition heterogeneity
dh = rd("_decomp_hetero_cl.csv").rename(columns={"kpf": "kp_f", "nn": "N"})
dh["outcome_label"] = dh.outc.map(OUTC)
dh["group_label"] = dh.grp.map({"all": "All", "inc_low": "Low income", "inc_mid": "Middle income", "inc_high": "High income"}).fillna(dh.grp)
dh["segment_label"] = dh.seg.map({"tot": "All departures", "intl": "International", "dom": "Domestic"}).fillna(dh.seg)
dh = add_ci(dh)
put("EDT5_decomp_hetero", dh, "ED Table 5", "Small multiples: component elasticities by income tercile and by intl/domestic segment", "_decomp_hetero_cl.csv (co2_decomp_hetero_cl.do)")

# ============================================================ ED Table 6 airport hetero
ah = rd("_airport_hetero.csv").rename(columns={"nn": "N_airport_years", "nap": "N_airports"})
ah["outcome_label"] = ah.outc.map({"ln_co2": "Bunker CO2", "ln_intensity": "CO2 per seat-km", "intl_share_skm": "International share of seat-km", "ln_skm": "Seat-km"}).fillna(ah.outc)
ah = add_ci(ah)
put("EDT6_airport_hetero", ah, "ED Table 6", "Coefficient plot by airport group (top5 vs not_top5 etc.)", "_airport_hetero.csv (co2_airport_hetero.do)")

# ============================================================ ED Table 7 / ED Fig 8 airport concentration (recomputed airport-level attribution)
p = pd.read_csv(os.path.join(HERE, "airport_co2_panel.csv"))
grp = rd("_airport_groups.csv"); het = rd("_airport_hetero.csv"); mech_r = rd("_feyrer_mechanism.csv").set_index("outc")
B_COUNTRY = float(mech_r.loc["ln_co2_tot", "b"]); B_AIRPORT = float(het[(het.panel == "ALL") & (het.outc == "ln_co2")]["b"].iloc[0])
b_top5 = float(het[(het.panel == "HUB") & (het.grp == "top5") & (het.outc == "ln_co2")]["b"].iloc[0])
b_not5 = float(het[(het.panel == "HUB") & (het.grp == "not_top5") & (het.outc == "ln_co2")]["b"].iloc[0])
p = p.sort_values(["airport_iata", "year"])
g96a = p[p.year == 1996][["airport_iata", "ln_gaci"]].rename(columns={"ln_gaci": "lg96"})
gfirst = p.dropna(subset=["ln_gaci"]).groupby("airport_iata").first()[["ln_gaci", "year"]].rename(columns={"ln_gaci": "lgfirst", "year": "yfirst"})
g23a = p[p.year == 2023][["airport_iata", "iso3", "Region", "ln_gaci", "GACI", "co2_bunker", "dep_seat_km", "intl_share_skm", "ln_intensity"]].rename(columns={"ln_gaci": "lg23"})
d = g23a.merge(g96a, on="airport_iata", how="left").merge(gfirst, on="airport_iata", how="left").merge(grp[["airport_iata", "top5", "top1", "hub_nat"]], on="airport_iata", how="left")
d["iso3"] = d["iso3"].fillna("TWN"); d["lg0"] = d["lg96"].fillna(d["lgfirst"])
d = d[(d.co2_bunker > 0) & d.lg23.notna() & d.lg0.notna()].copy()
d["dln_gaci"] = d.lg23 - d.lg0; d["co2_mt_2023"] = d.co2_bunker / 1e9
d["att_country_b_mt"] = d.co2_mt_2023 * (1 - np.exp(-B_COUNTRY * d.dln_gaci))
d["att_airport_b_mt"] = d.co2_mt_2023 * (1 - np.exp(-B_AIRPORT * d.dln_gaci))
d["att_group_b_mt"] = d.co2_mt_2023 * (1 - np.exp(-np.where(d.top5 == 1, b_top5, b_not5) * d.dln_gaci))
d["kg_co2_per_1000skm"] = d.co2_bunker / d.dep_seat_km * 1000
d["share_of_world_attributed_pct"] = 100 * d.att_country_b_mt / d.att_country_b_mt.clip(lower=0).sum()
d["rank_attributed"] = d.att_country_b_mt.rank(ascending=False)
d["country"] = d.iso3.map(cname)
ap = d.sort_values("att_country_b_mt", ascending=False)[["airport_iata", "iso3", "country", "Region", "top5", "top1", "hub_nat", "GACI", "lg0", "yfirst", "lg23", "dln_gaci", "co2_mt_2023", "dep_seat_km", "intl_share_skm", "kg_co2_per_1000skm",
                                                          "att_country_b_mt", "att_airport_b_mt", "att_group_b_mt", "share_of_world_attributed_pct", "rank_attributed"]]
put("AIRPORT_2023", ap, "ED Fig 8B (top 20 = first 20 rows); ED Table 7 inputs; airport-point maps", "Point map / bubble map keyed on IATA (needs coordinates from OAG/OpenFlights); top-20 horizontal bars, blue if top5 = 1", "airport_co2_panel.csv + _airport_groups.csv, recomputed as in 19_airport_concentration.py")
# Lorenz points (1% grid)
lor = []
grid = np.linspace(0, 1, 201)
for nm, col in [("Emissions 2023", "co2_mt_2023"), ("Attributed (country b)", "att_country_b_mt"), ("Attributed (airport b)", "att_airport_b_mt"), ("Attributed (hub/non-hub b)", "att_group_b_mt")]:
    s = np.sort(d[col].clip(lower=0).values); n = len(s); cum = np.concatenate([[0], np.cumsum(s) / s.sum()])
    xx = np.arange(n + 1) / n
    for gx in grid:
        lor.append(dict(measure=nm, cum_share_airports=gx, cum_share_mt=float(np.interp(gx, xx, cum))))
put("EDF8_lorenz", pd.DataFrame(lor), "ED Fig 8A (Lorenz curves)", "Line per measure: cum_share_mt vs cum_share_airports; diagonal = equality", "recomputed from AIRPORT_2023")
put("EDT7_airport_conc", rd("_airport_concentration.csv"), "ED Table 7", "Bar: top1/top5/top10/top25 shares and Gini by measure", "_airport_concentration.csv")

# ============================================================ ED Fig 7 efficiency curve
eb = rd("_airport_efficiency_bins.csv").rename(columns={"ln_gaci": "ln_gaci_bin_mean", "kg": "median_kg_co2_per_1000skm", "intl": "intl_share_skm", "n": "n_airports"})
eb.insert(0, "ventile", range(1, len(eb) + 1)); eb["gaci_bin_mean"] = np.exp(eb.ln_gaci_bin_mean)
put("EDF7_efficiency_curve", eb, "ED Fig 7 (2023 airport ventiles)", "Panel 1: median kg CO2/1000 seat-km vs ventile (or ln GACI); panel 2: international share", "_airport_efficiency_bins.csv (build_efficiency_curve_fig.py)")

# ============================================================ ED Fig 9 RF quintile (tourism shifter)
rq = rd("_co2_rf_quintile_intl.csv").rename(columns={"nn": "N", "bin": "quintile"})
rq["panel_label"] = rq["mod"].map({"inc": "Baseline income quintile (1996 GDP per capita)", "con": "Baseline connectivity quintile (1996 hub quality)", "rem": "Remoteness quintile (mean sea distance)"})
rq = add_ci(rq)
put("EDF9_rf_quintile", rq, "ED Fig 9", "Three panels: b with 95% CI by quintile; outcome = ln international CO2, tourism-heritage shifter", "_co2_rf_quintile_intl.csv (co2_rf_quintile.do)")

# ============================================================ ED Tables 8-9 / ED Fig 10 spillovers
sb = rd("_spill_bands_cl.csv").rename(columns={"kpf": "kp_f", "swf": "sw_f", "nn": "N"})
VL = {"nbr_g_contig": "Contiguous countries", "nbr_g_b1": "0-500 km", "nbr_g_b2": "500-1,000 km", "nbr_g_b3": "1,000-2,000 km", "nbr_g_b4": "2,000-5,000 km", "nbr_g_b5": "Beyond 5,000 km",
      "nbr_g_k250": "Kernel 250 km", "nbr_g_k500": "Kernel 500 km", "nbr_g_k1000": "Kernel 1,000 km", "nbr_g_k2000": "Kernel 2,000 km", "nbr_g_k5000": "Kernel 5,000 km",
      "ln_gaci_cwm": "Own ln GACI", "nbr_g_inv": "Neighbour ln GACI (inverse distance)", "nbr_g_knn5": "Neighbour ln GACI (5 nearest)", "feyrer_int": "Own Feyrer shifter (RF control)"}
sb["var_label"] = sb["var"].map(VL).fillna(sb["var"])
sb = add_ci(sb)
put("EDT8_9_spillover", sb, "ED Table 8 (Panel A items), ED Table 9 (Panels B-C)", "Reference; ED Fig 10 subset in next sheet", "_spill_bands_cl.csv (co2_spill_bands_cl.do)")
dec = sb[(sb.panel == "B") & (sb.item.isin(["band_single", "kernel"]))].copy()
dec["fig_panel"] = np.where(dec.item == "band_single", "A. One distance band at a time", "B. Continuous kernel")
dec["x_order"] = dec["var"].map({k: i for i, k in enumerate(VL)})
put("EDF10_spill_decay", dec.sort_values(["fig_panel", "x_order"])[["fig_panel", "x_order", "var", "var_label", "b", "se", "p", "ci_lo", "ci_hi", "sig05", "kp_f", "N"]],
    "ED Fig 10", "Dot-and-whisker: coefficient on neighbour ln GACI by band (A) and kernel scale (B)", "_spill_bands_cl.csv")
ps = rd("_spill_placebo_summary.csv").rename(columns={"Unnamed: 0": "W"})
pi = rd("_spill_placebo_perm.csv"); pw = rd("_spill_placebo_perm_W.csv")
draws = pd.concat([pd.DataFrame(dict(W="invdist_rf", draw=pi.draw, t=pi.rf_t, b=pi.rf_b, t_actual=pi.rft_actual)),
                   pw.merge(ps[["W", "t_actual"]], on="W", how="left")[["W", "draw", "t", "b", "t_actual"]]], ignore_index=True)
draws["W_label"] = draws.W.map({"invdist_rf": "Inverse distance (reduced form)", "contig": "Contiguity (joint 2SLS, neighbour coef.)", "knn5": "Five nearest (joint 2SLS, neighbour coef.)"})
put("EDF11_spill_placebo", draws, "ED Fig 11 (histograms of permuted t; vertical line at t_actual); ED Table 9 Panel C", "Histogram per W_label of t with t_actual marked", "_spill_placebo_perm.csv, _spill_placebo_perm_W.csv")
put("EDT9_placebo_summary", ps, "ED Table 9 Panel C", "Reference", "_spill_placebo_summary.csv")

# ============================================================ ED Table 11 / ED Fig 12 exclusion + placebo RF
ex = rd("_exclusion_suite_cl.csv").rename(columns={"f": "kp_f", "nn": "N"})
AL = {"ln_co2_tot": "Aviation CO2 (total, our series)", "ln_co2_intl": "Aviation CO2 (international)", "ln_co2_exav": "Territorial fossil CO2 excl. domestic aviation (GCP/OWID)",
      "ln_oil_exav": "Oil CO2 excl. domestic aviation (OWID)", "ln_ed_transp_exav": "Transport CO2 excl. domestic aviation (EDGAR)", "ln_ed_power": "Power industry CO2 (EDGAR)",
      "ln_ed_build": "Buildings CO2 (EDGAR)", "ln_ed_indcomb": "Industrial combustion CO2 (EDGAR)", "ln_coal": "Coal CO2 (OWID)", "ln_gas": "Gas CO2 (OWID)", "ln_cement": "Cement CO2 (OWID)", "ln_ed_agri": "Agriculture CO2 (EDGAR)"}
ex["item_label"] = ex.item.map(AL).fillna(ex.item)
ex = add_ci(ex)
put("EDT11_exclusion", ex, "ED Table 11 (Panels A-B), SI Table 1 (Panels G-I)", "Reference", "_exclusion_suite_cl.csv (co2_exclusion_suite_cl.do)")
prf = ex[(ex.panel == "A") & (ex.stat == "RF") & ex.item.isin(AL)].copy()
prf["order"] = prf.item.map({k: i for i, k in enumerate(AL)}); prf["is_aviation"] = prf.item.isin(["ln_co2_tot", "ln_co2_intl"]).astype(int)
put("EDF12_placebo_rf", prf.sort_values("order")[["order", "item", "item_label", "is_aviation", "b", "se", "p", "ci_lo", "ci_hi", "sig05", "N"]],
    "ED Fig 12", "Horizontal bars of reduced-form b with 95% CI; blue if is_aviation = 1, grey otherwise", "_exclusion_suite_cl.csv")

# ============================================================ ED Tables 12-13 / ED Fig 3 functional form + gradient
y = rd("_yifu_suite_cl.csv")
yy = y.copy(); yy["N"] = yy.nn; yy = add_ci(yy)
put("EDT12_13_funcform", yy, "ED Table 12 (Panel A items), ED Table 13 (Panel B items), Panel C = moments", "Reference", "_yifu_suite_cl.csv (co2_yifu_suite_cl.do)")
def g(panel, item, var=None):
    r = y[(y.panel == panel) & (y.item == item)]
    if var is not None: r = r[r["var"] == var]
    return r.iloc[0] if len(r) else None
m0 = g("C", "centre_lg0").b; lg0 = g("C", "moment_lg0")
qrows = []
for k in range(1, 6):
    r = g("B", f"q{k}_loglog"); s = g("B", f"q{k}_semilog"); g0 = g("B", f"q{k}_gaci0"); gg = g("B", f"q{k}_gaci")
    qrows.append(dict(series="Quintile split-sample 2SLS", quintile=k, baseline_gaci_mean=g0.b, baseline_gaci_min=g0.v12, baseline_gaci_max=g0.v33, b=r.b, se=r.se, p=r.p, kp_f=r.kpf, N=r.nn,
                      identified=int(r.kpf >= 5), semilog_b=s.b, semilog_se=s.se, semilog_implied_elasticity=s.b * gg.b))
q = add_ci(pd.DataFrame(qrows))
b1 = g("B", "int_lin", "ln_gaci_cwm"); b2 = g("B", "int_lin", "x_dev")
q1 = g("B", "int_quad", "ln_gaci_cwm"); q2 = g("B", "int_quad", "x_dev"); q3 = g("B", "int_quad", "x_dev2")
Vq = np.array([[q1.se ** 2, q1.v12, q1.v13], [q1.v12, q1.v22, q1.v23], [q1.v13, q1.v23, q1.v33]])
crv = []
for x in np.linspace(lg0.v12 - 0.1, lg0.v33 + 0.1, 100):
    dd = x - m0
    bl = b1.b + b2.b * dd; sl = math.sqrt(max(b1.se ** 2 + 2 * dd * b1.v12 + dd * dd * b1.v22, 0))
    xv = np.array([1, dd, dd * dd]); bq = float(xv @ np.array([q1.b, q2.b, q3.b])); sq = float(math.sqrt(max(xv @ Vq @ xv, 0)))
    crv.append(dict(series="Linear interaction (fitted)", ln_baseline_gaci=x, baseline_gaci=math.exp(x), b=bl, se=sl, ci_lo=bl - 1.96 * sl, ci_hi=bl + 1.96 * sl))
    crv.append(dict(series="Quadratic interaction (fitted)", ln_baseline_gaci=x, baseline_gaci=math.exp(x), b=bq, se=sq, ci_lo=bq - 1.96 * sq, ci_hi=bq + 1.96 * sq))
grad = pd.concat([q, pd.DataFrame(crv)], ignore_index=True)
put("EDF3_gradient", grad, "ED Fig 3; ED Table 13", "x = baseline_gaci (or quintile baseline_gaci_mean); quintile points with CI (skip identified = 0), fitted linear dashed, quadratic with band; refs at 0 and 1",
    "_yifu_suite_cl.csv, fitted curves recomputed as in 29_yifu_gradient_attribution.py")

# ============================================================ ED Table 14 attribution sensitivity
asn = rd("_attribution_sensitivity.csv"); ahc = rd("_attribution_hetero.csv")
if "c" in ahc.columns: ahc.insert(1, "country", ahc.c.map(cname))
put("EDT14_attr_sens", asn, "ED Table 14", "Bar: attributed_mt by rule", "_attribution_sensitivity.csv (29_yifu_gradient_attribution.py)")
put("EDT14_attr_country", ahc, "ED Table 14 (country-level under each rule)", "Alternative map layers", "_attribution_hetero.csv")

# ============================================================ Panel and world series
keep = ["c", "y", "reg", "gaci_cwmean", "gaci_mean", "gaci_max", "ln_gaci_cwm", "n_air", "n_dep_flights", "dep_seats", "dep_seat_km", "dep_seat_km_intl", "co2_bunker", "co2_bunker_intl", "co2_lto", "co2_5050", "lnpop", "lnpc", "lnZ"]
pn = pd.read_csv(os.path.join(HERE, "gaci_co2_panel.csv"), usecols=[k for k in keep if k in gp.columns or True])
pn = pn[[k for k in keep if k in pn.columns]].rename(columns={"c": "iso3", "y": "year", "reg": "region_code", "n_air": "n_airports", "lnZ": "ln_feyrer_instrument"})
pn.insert(1, "country", pn.iso3.map(cname))
for k in ["co2_bunker", "co2_bunker_intl", "co2_lto", "co2_5050"]:
    pn[k.replace("co2_", "") + "_mt"] = pn[k] / 1e9
pn["seat_km_bn"] = pn.dep_seat_km / 1e9; pn["intl_share_skm"] = pn.dep_seat_km_intl / pn.dep_seat_km
pn["kg_co2_per_1000skm"] = pn.co2_bunker / pn.dep_seat_km * 1000
pn = pn.drop(columns=["co2_bunker", "co2_bunker_intl", "co2_lto", "co2_5050", "dep_seat_km", "dep_seat_km_intl"]).sort_values(["iso3", "year"])
put("PANEL_country_year", pn, "Estimation panel (Table 1 sample, 1996-2023)", "Time series per country: bunker_mt, gaci_cwmean, kg_co2_per_1000skm; scatter dln GACI vs dln CO2", "gaci_co2_panel.csv (03_merge_gaci.py)")
ws = cy.groupby("year").agg(bunker_mt=("co2_bunker", lambda s: s.sum() / 1e9), bunker_intl_mt=("co2_bunker_intl", lambda s: s.sum() / 1e9), lto_mt=("co2_lto", lambda s: s.sum() / 1e9),
                            flights_mn=("n_dep_flights", lambda s: s.sum() / 1e6), seat_km_bn=("dep_seat_km", lambda s: s.sum() / 1e9), seat_km_intl_bn=("dep_seat_km_intl", lambda s: s.sum() / 1e9), n_countries=("iso3", "nunique")).reset_index()
ws["kg_co2_per_1000skm"] = ws.bunker_mt * 1e9 / (ws.seat_km_bn * 1e9) * 1000
ws["intl_share_skm"] = ws.seat_km_intl_bn / ws.seat_km_bn
gw = gp.groupby("y").agg(gaci_cwm_mean_across_countries=("gaci_cwmean", "mean"), gaci_cwm_median=("gaci_cwmean", "median")).reset_index().rename(columns={"y": "year"})
ws = ws.merge(gw, on="year", how="left")
put("WORLD_series", ws, "Context (Methods; SAF base 838 Mt in 2023)", "World aviation CO2 and traffic 1996-2023; intensity decline; mean connectivity", "co2_country_year.csv, gaci_co2_panel.csv")

# ============================================================ write
order = ["README", "T1_main", "T2_decomp", "F1_hetero", "T3_spatial", "MAP_country_2023", "T4_scc", "F3_saf",
         "EDF1_temporal", "EDT1_temporal_all", "EDF3_gradient", "EDT12_13_funcform", "EDT4_mediation", "EDT5_decomp_hetero", "EDT6_airport_hetero",
         "EDT7_airport_conc", "EDF8_lorenz", "AIRPORT_2023", "EDF7_efficiency_curve", "EDF9_rf_quintile",
         "EDT8_9_spillover", "EDF10_spill_decay", "EDF11_spill_placebo", "EDT9_placebo_summary", "EDT10_spatial_ext",
         "EDT11_exclusion", "EDF12_placebo_rf", "EDT14_attr_sens", "EDT14_attr_country", "PANEL_country_year", "WORLD_series"]
readme = pd.DataFrame([sheets[k][1] for k in order if k in sheets])
hdr = pd.DataFrame([{"sheet": "NOTE", "manuscript_display": "Manuscript: FINAL_20260906/main_co2_nature_20260906.tex (candidate of 6 Sep 2026). Standard errors clustered by country throughout (ML spatial models: Hessian s.e.).",
                     "what_to_plot": "Columns: b = coefficient, se, p, ci_lo/ci_hi = 95% CI, stars, sig05 = p<0.05 flag. Emissions in Mt CO2 (bunker convention unless stated). GACI = capacity-weighted mean unless stated.",
                     "source": "Built by 35_make_viz_data_20260908.py", "rows": np.nan}])
readme = pd.concat([hdr, readme], ignore_index=True)
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    readme.to_excel(xw, sheet_name="README", index=False)
    for k in order:
        if k == "README": continue
        sheets[k][0].to_excel(xw, sheet_name=k[:31], index=False)
    for ws_ in xw.book.worksheets:
        ws_.freeze_panes = "A2"
        for c in ws_[1]:
            c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F4E79"); c.alignment = Alignment(vertical="center")
        for i, col in enumerate(ws_.columns, 1):
            vals = [str(c.value) for c in list(col)[:200] if c.value is not None]
            w = min(max([len(v) for v in vals] + [8]) + 2, 60 if ws_.title == "README" else 28)
            ws_.column_dimensions[get_column_letter(i)].width = w
        if ws_.title == "README":
            for row in ws_.iter_rows(min_row=2):
                for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
print("wrote", OUT)
for _, r in readme.iterrows():
    print(f"  {str(r.sheet):24s} {'' if pd.isna(r.rows) else int(r.rows):>6} {str(r.manuscript_display)[:70]}")
shutil.copy(OUT, os.path.join(HERE, "FINAL_20260906", os.path.basename(OUT)))
print("copied to FINAL_20260906/")
print("DONE_35")
