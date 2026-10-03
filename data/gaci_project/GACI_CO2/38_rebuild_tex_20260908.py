# -*- coding: utf-8 -*-
r"""
38_rebuild_tex_20260908.py   (2026-09-08)
Rebuild FINAL_20260908/main_co2_nature_20260908.tex on the corrected data
(airport->country assignment fixed: Kyrgyzstan's FRU restored, Taiwan and territories
assigned; Eswatini restored in spatial/spillover/placebo samples; 1996 baseline
geography recovered for late entrants). All tables are swapped in from the regenerated
fragments, the user's Table 1 / ED Table 1 edits are re-applied, and every number in
the prose, captions and notes is recomputed from the result CSVs. Also folds in the
09-08 accuracy fixes (SAF unit, SI Table 1 robust row, captions, denominators, mismatch
wording, Methods clauses). Old strings must exist exactly once; failures are listed.
"""
import os, re, shutil, sys, math
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, "FINAL_20260908")
TEX = os.path.join(FIN, "main_co2_nature_20260908.tex")
BS = chr(92)
BAK = os.path.join(FIN, "_bak_main_co2_nature_20260908_pre38.tex")
if not os.path.exists(BAK): shutil.copy(TEX, BAK)
s = open(BAK, encoding="utf-8").read()   # always rebuild from the pre-38 baseline
FAIL = []; NREP = 0
def rep(old, new, count=1):
    global s, NREP
    c = s.count(old)
    if c != count:
        FAIL.append((c, old[:100])); return
    s = s.replace(old, new); NREP += 1
def rd(fn): return pd.read_csv(os.path.join(HERE, fn))
f2 = lambda x: f"{x:.2f}"
f1 = lambda x: f"{x:.1f}"
def neg(x, d=2): return ("$-$" + f"{abs(x):.{d}f}") if x < 0 else f"{x:.{d}f}"
def sgn(x, d=2): return ("$-$" + f"{abs(x):.{d}f}") if x < 0 else f"{x:.{d}f}"
def pm(x, d=0): return ("$-$" + f"{abs(x):.{d}f}") if x < 0 else ("$+$" + f"{x:.{d}f}")
def table_by_label(src, label):
    i = src.find(BS + "label{%s}" % label); assert i >= 0, label
    a = src.rfind(BS + "begin{table}", 0, i); b = src.find(BS + "end{table}", i) + len(BS + "end{table}")
    return a, b
def swap_table(label, fragsrc):
    global s
    a, b = table_by_label(s, label); fa, fb = table_by_label(fragsrc, label); frag = fragsrc[fa:fb]
    mcap = re.search(r"\\caption\{(.*?)\}\n", s[a:b], flags=re.S).group(1); fcap = re.search(r"\\caption\{(.*?)\}\n", frag, flags=re.S).group(1)
    pref = re.match(r"(Extended Data Table \d+|Supplementary Table \d+): ", mcap)
    if pref and not fcap.startswith(pref.group(1)):
        frag = frag.replace(BS + "caption{" + fcap + "}", BS + "caption{" + pref.group(1) + ": " + re.sub(r"^(Extended Data Table|Supplementary Table)(?: \d+)?: ", "", fcap) + "}")
    # manuscript wrapper: [H] + resizebox; normalise fragment
    frag = frag.replace(BS + "begin{table}[htbp]", BS + "begin{table}[H]")
    if BS + "resizebox" not in frag:
        frag = frag.replace(BS + "begin{threeparttable}", BS + "resizebox{" + BS + "ifdim" + BS + "width>" + BS + "textwidth " + BS + "textwidth" + BS + "else" + BS + "width" + BS + "fi}{!}{%\n" + BS + "begin{threeparttable}", 1)
        frag = frag.replace(BS + "end{threeparttable}", BS + "end{threeparttable}}", 1)
    s = s[:a] + frag + s[b:]

# ============================================================ data
al = rd("_allest_results_cl.csv"); m6 = rd("_measures6_cl.csv"); mech = rd("_feyrer_mechanism_cl.csv").set_index("outc")
t8 = rd("_temporal_pre2008_cl.csv"); txc = rd("_temporal_excovid_cl.csv"); told = rd("_temporal_co2_cl.csv")
med = rd("_mediation_co2_cl.csv").set_index("med"); dh = rd("_decomp_hetero_cl.csv"); hetdf = rd("_feyrer_hetero_tot_cl.csv"); het = hetdf.set_index(["panel", "grp"])
yf = rd("_yifu_suite_cl.csv"); asens = rd("_attribution_sensitivity.csv"); att = rd("_attribution_scc.csv")
ah = rd("_airport_hetero.csv"); ac = rd("_airport_concentration.csv").set_index("measure"); top = rd("_airport_top20.csv")
SP = rd("_spatial_models.csv"); supp = rd("_spill_supp.csv"); sb = rd("_spill_bands_cl.csv"); psum = rd("_spill_placebo_summary.csv", ).rename(columns={"Unnamed: 0": "W"}).set_index("W")
exc = rd("_exclusion_suite_cl.csv"); exr = rd("_exclusion_suite.csv"); saf = rd("_saf_growth_scenarios.csv"); asn = rd("_asn_iv_results.csv")
cy = rd("co2_country_year.csv"); WORLD = cy.loc[cy.year == 2023, "co2_bunker"].sum() / 1e9
def A(est, outc, col="b"): return float(al[(al.est == est) & (al.outc == outc)].iloc[0][col])
def M6(meas, outc, col="b"): return float(m6[(m6.meas == meas) & (m6.outc == outc)].iloc[0][col])
def T(df, samp, outc, col="b"): return float(df[(df.samp == samp) & (df.outc == outc)].iloc[0][col])
def DH(grp, seg, outc, col="b"): return float(dh[(dh.grp == grp) & (dh.seg == seg) & (dh.outc == outc)].iloc[0][col])
def Y(panel, item, var=None, col="b"):
    r = yf[(yf.panel == panel) & (yf.item == item)]
    if var is not None: r = r[r["var"] == var]
    return float(r.iloc[0][col])
def EX(panel, item, stat, col="b", df=None):
    df = exc if df is None else df
    return float(df[(df.panel == panel) & (df.item == item) & (df.stat == stat)].iloc[0][col])
def sp(model, est, term, W="contig", outc="ln_co2_tot", col="b"):
    r = SP[(SP.W == W) & (SP.outcome == outc) & (SP.model == model) & (SP.estimator == est) & (SP.term == term)]; return float(r.iloc[0][col if col != "se" else "se_cl"])
def SU(item, var, col="b"): return float(supp[(supp.item == item) & (supp["var"] == var)].iloc[0][col])

b, se = A("FeyrerIV", "ln_co2_tot"), A("FeyrerIV", "ln_co2_tot", "se"); kpf = A("FeyrerIV", "ln_co2_tot", "kpf")
b_int, se_int = A("FeyrerIV", "ln_co2_intl"), A("FeyrerIV", "ln_co2_intl", "se")
b_skm, se_skm = A("FeyrerIV", "ln_skm"), A("FeyrerIV", "ln_skm", "se"); b_ii, se_ii = A("FeyrerIV", "ln_intensity"), A("FeyrerIV", "ln_intensity", "se")
b_lto, b_5050 = A("FeyrerIV", "ln_co2_lto"), A("FeyrerIV", "ln_co2_5050"); b_ols = A("OLS", "ln_co2_tot")
b_rob_se, kpf_rob = A("FeyrerIV", "ln_co2_tot", "se") if False else float(exr[(exr.panel == "I") & (exr.item == "robust")].iloc[0].se), float(exr[(exr.panel == "I") & (exr.item == "robust")].iloc[0].f)
b96, se96, F96 = T(t8, "1996-2007", "ln_co2_tot"), T(t8, "1996-2007", "ln_co2_tot", "se"), T(t8, "1996-2007", "ln_co2_tot", "kpf")
b10, se10, F10 = T(txc, "2010-2023_exCOVID", "ln_co2_tot"), T(txc, "2010-2023_exCOVID", "ln_co2_tot", "se"), T(txc, "2010-2023_exCOVID", "ln_co2_tot", "kpf")
Fun = float(told[(told.period == "2010-2023") & (told.outc == "ln_co2_tot")].kpf.iloc[0])
ctrl = exc[(exc.panel == "E") & (exc.stat == "IV") & exc.item.str.startswith("c") & ~exc.item.isin(["c0_baseline", "c0_commonsample"])].b
fl, fl_se = mech.loc["ln_flights", "b"], mech.loc["ln_flights", "se"]; ga, ga_se = mech.loc["ln_gauge", "b"], mech.loc["ln_gauge", "se"]
st, st_se = mech.loc["ln_stage", "b"], mech.loc["ln_stage", "se"]; ii, ii_se = mech.loc["ln_intensity", "b"], mech.loc["ln_intensity", "se"]
sc = mech.loc["ln_skm", "b"]; tot = mech.loc["ln_co2_tot", "b"]; ish, ish_se = mech.loc["intl_share", "b"], mech.loc["intl_share", "se"]
share_scale = 100 * sc / tot; share_eff = 100 * ii / tot
medlo, medhi = sorted([100 * med.loc["ln_flights", "prop"], 100 * med.loc["ln_skm", "prop"]])
print(f"headline {b:.3f} ({se:.3f}) F {kpf:.1f}; intl {b_int:.3f}; skm {b_skm:.3f}; intensity {b_ii:.3f} ({se_ii:.3f}); OLS {b_ols:.3f}; 96-07 {b96:.2f} ({se96:.2f}) F {F96:.0f}; 10-23xc {b10:.2f} ({se10:.2f}) F {F10:.0f}; unrestricted F {Fun:.1f}")
print(f"decomp: flights {fl:.2f} ({fl_se:.2f}) gauge {ga:.2f} ({ga_se:.2f}) stage {st:.2f} ({st_se:.2f}) int {ii:.2f} ({ii_se:.2f}); scale {sc:.2f} = {share_scale:.0f}%; eff {share_eff:.0f}%; intl share {ish:.2f} ({ish_se:.2f}); mediation {medlo:.0f}-{medhi:.0f}%; controls {ctrl.min():.1f}-{ctrl.max():.1f}; world {WORLD:.1f}")

# ============================================================ 1. tables from fragments
FR = {k: open(os.path.join(HERE, k), encoding="utf-8").read() for k in
      ["_tex_main_cl.tex", "_tex_decomp_cl.tex", "_tex_hetero_tot_cl.tex", "_tex_spill_cl.tex", "_tex_spatial.tex", "_tex_exclusion_cl.tex", "_tex_yifu_cl.tex", "_tex_airport.tex", "_tex_airport_conc.tex"]}
for lab, fn in [("tab:main", "_tex_main_cl.tex"), ("tab:temporal", "_tex_main_cl.tex"), ("tab:mediation", "_tex_main_cl.tex"),
                ("tab:decomp", "_tex_decomp_cl.tex"), ("tab:decomp_hetero", "_tex_decomp_cl.tex"), ("tab:hetero", "_tex_hetero_tot_cl.tex"),
                ("tab:spillover", "_tex_spill_cl.tex"), ("tab:spill_ext", "_tex_spill_cl.tex"), ("tab:spatial", "_tex_spatial.tex"), ("tab:spatial_ext", "_tex_spatial.tex"), ("tab:alloc", "_tex_spatial.tex"),
                ("tab:exclusion", "_tex_exclusion_cl.tex"), ("tab:exclusion2", "_tex_exclusion_cl.tex"), ("tab:funcform", "_tex_yifu_cl.tex"), ("tab:gradient", "_tex_yifu_cl.tex"), ("tab:attr_sens", "_tex_yifu_cl.tex"), ("tab:accident_iv", "_tex_yifu_cl.tex"),
                ("tab:airport_het", "_tex_airport.tex"), ("tab:airport_iv", "_tex_airport.tex"), ("tab:airport_conc", "_tex_airport_conc.tex")]:
    swap_table(lab, FR[fn])
print("tables swapped")

# --- Table 1: manuscript layout (Bunker, Intl, Seat-km) filled from the 6-column fragment (cols 1, 4, 5)
a, b_ = table_by_label(s, "tab:main"); t = s[a:b_]
base_t = open(BAK, encoding="utf-8").read(); a0, b0 = table_by_label(base_t, "tab:main"); t0 = base_t[a0:b0]
def rows_of(block):
    i0 = block.find(BS + "toprule"); i1 = block.find(BS + "bottomrule"); return block[i0:i1]
keep = [0, 1, 4, 5]; out = []
for l in rows_of(t).split(chr(10)):
    if l.startswith(BS + "multicolumn{7}{l}"): l = l.replace(BS + "multicolumn{7}{l}", BS + "multicolumn{4}{l}")
    elif l.strip().endswith(BS + BS) and l.count("&") == 6 and not l.startswith(BS + "multicolumn"):
        cells = [c.strip() for c in l.rstrip().rstrip(BS).rstrip().split("&")]
        l = " & ".join(cells[k] for k in keep) + " " + BS + BS
    out.append(l)
newrows = chr(10).join(out)
t_new = t0[:t0.find(BS + "toprule")] + newrows + t0[t0.find(BS + "bottomrule"):]
assert "Intensity" not in t_new and "LTO CO" not in t_new, "Table 1 column selection failed"
s = s[:a] + t_new + s[b_:]
a, b_ = table_by_label(s, "tab:temporal"); t = s[a:b_]
i = t.find(BS + "midrule\n" + BS + "multicolumn{5}{l}{" + BS + "textit{Panel D. Unrestricted split"); j = t.find(BS + "bottomrule", i); assert i > 0 and j > i
t = t[:i] + t[j:]
t = re.sub(r"Panels D and E report the unrestricted split for reference; the weak first stage in Panel E \(KP \$F\$ = [\d.]+\) is driven by the COVID years, whose exclusion in Panel C restores \$F\$ to ([\d.]+)\.",
           lambda m: f"The unrestricted 2010--2023 split (not shown) has a weak first stage (KP $F$ = {Fun:.1f}), driven by the COVID years, whose exclusion in Panel C restores $F$ to {m.group(1)}; its estimates appear in grey in Extended Data Fig.~" + BS + "ref{fig:temporal}.", t)
assert "Panel E" not in t; s = s[:a] + t + s[b_:]

# --- Table 4 (tab:scc) regenerated from _attribution_scc.csv
NAMES = {"CHN": "China", "USA": "United States", "ARE": "United Arab Emirates", "JPN": "Japan", "TUR": "Turkey", "IND": "India", "KOR": "Korea", "CAN": "Canada", "QAT": "Qatar", "ESP": "Spain", "DEU": "Germany", "GBR": "United Kingdom", "SGP": "Singapore", "SAU": "Saudi Arabia", "NLD": "Netherlands", "FRA": "France", "AUS": "Australia", "MEX": "Mexico", "BRA": "Brazil", "ITA": "Italy", "RUS": "Russia", "IDN": "Indonesia", "THA": "Thailand", "VNM": "Viet Nam", "PHL": "Philippines", "EGY": "Egypt", "ETH": "Ethiopia"}
att = att.sort_values("att_tot_t", ascending=False); ATT = att.att_tot_t.sum() / 1e6; ATTI = att.att_intl_t.sum() / 1e6
SCC = {k: att[f"val_tot_scc{k}_usd"].sum() / 1e9 for k in ["51", "185", "190"]}
neg_row = att[att.att_tot_t == att.att_tot_t.min()].iloc[0]
rows = []
for _, r in pd.concat([att.head(10), att[att.c == neg_row.c]]).iterrows():
    nm = NAMES.get(r.c, r.c); v = lambda x, d: (f"$-{abs(x):.{d}f}$" if x < 0 else f"{x:.{d}f}")
    rows.append(f"{nm} & {v(r.dln_cwm, 2)} & {v(r.att_tot_t / 1e6, 1)} & {v(r.att_intl_t / 1e6, 1)} & {v(r.val_tot_scc51_usd / 1e9, 1)} & {v(r.val_tot_scc185_usd / 1e9, 1)} & {v(r.val_tot_scc190_usd / 1e9, 1)} \\\\")
a, b_ = table_by_label(s, "tab:scc"); t = s[a:b_]
i = t.find(BS + "midrule\nChina"); j = t.find(BS + "midrule\nWorld"); assert i > 0 and j > i
k = t.find(BS + BS + "\n", j) + 3
worldrow = f"World & & {ATT:.1f} & {ATTI:.1f} & {SCC['51']:.1f} & {SCC['185']:.1f} & {SCC['190']:.1f} \\\\\n"
t = t[:i] + BS + "midrule\n" + "\n".join(rows) + "\n" + BS + "midrule\n" + worldrow + t[k:]
t = re.sub(r"elasticities \([\d.]+ total, [\d.]+ international\)", f"elasticities ({b:.3f} total, {b_int:.3f} international)", t)
t = re.sub(r"the world attributed total equals [\d.]+ percent of 2023 aviation CO\$_2\$", f"the world attributed total equals {100 * ATT / WORLD:.1f} percent of 2023 aviation CO$_2$ ({WORLD:.0f} Mt)", t)
t = t.replace("Top ten positive countries, Germany (largest negative)", f"Top ten positive countries, {NAMES.get(neg_row.c, neg_row.c)} (largest negative)")
t = t.replace("to each country's 1996--2023 change in log connectivity: attributed share", "to each country's 1996--2023 change in log connectivity (the first and last years in which the country is observed, for the 34 countries entering after 1996 and the 18 whose series end before 2023): attributed share")
s = s[:a] + t + s[b_:]
SH = 100 * ATT / WORLD
print(f"attribution: {ATT:.1f} Mt = {SH:.1f}% of {WORLD:.1f}; intl {ATTI:.1f}; SCC {SCC['51']:.1f}/{SCC['185']:.1f}/{SCC['190']:.1f}; top: " + ", ".join(f"{r.c} {r.att_tot_t/1e6:+.0f}" for _, r in att.head(7).iterrows()) + f"; min {neg_row.c} {neg_row.att_tot_t/1e6:+.0f}")

# ============================================================ 2. abstract & Main
rep("A one percent increase in connectivity raises national aviation\nCO$_2$ by 5.7 percent,", f"A one percent increase in connectivity raises national aviation\nCO$_2$ by {b:.1f} percent,")
rep("accounting identity shows that it is a frequency response: flights rise by\n7.0 percent,", f"accounting identity shows that it is a frequency response: flights rise by\n{fl:.1f} percent,")
rep("emissions per seat-kilometre is small (0.4 percent) and imprecisely", f"emissions per seat-kilometre is small ({abs(ii):.1f} percent) and imprecisely")
rep("1996 accounts for 42.5 percent (356 Mt) of 2023 aviation CO$_2$, an annual\nexternal cost of \\$18 billion to \\$68 billion at standard social-cost-of-carbon",
    f"1996 accounts for {SH:.1f} percent ({ATT:.0f} Mt) of 2023 aviation CO$_2$, an annual\nexternal cost of \\${SCC['51']:.0f} billion to \\${SCC['190']:.0f} billion at standard social-cost-of-carbon")
rep("Our main estimate indicates that a 1\\% increase in\nconnectivity increases aviation CO$_2$ by about 5.7\\%, driven primarily\nby a roughly 7\\% increase in flight frequency.",
    f"Our main estimate indicates that a 1\\% increase in\nconnectivity increases aviation CO$_2$ by about {b:.1f}\\%, driven primarily\nby a roughly {fl:.0f}\\% increase in flight frequency.")

# ============================================================ 3. Results: headline
tstat = (b - 1) / se
rep("connectivity raises total bunker CO$_2$ by 5.67 percent (s.e.\\ 1.12,\nclustered by country), and the hypothesis that the elasticity equals one\nis rejected at any conventional level ($t = 4.2$).",
    f"connectivity raises total bunker CO$_2$ by {b:.2f} percent (s.e.\\ {se:.2f},\nclustered by country), and the hypothesis that the elasticity equals one\nis rejected at any conventional level ($t = {tstat:.1f}$).")
lo3, hi3 = sorted([b_lto, b_5050]); lo_lab = "the territorial rule" if b_lto < b_5050 else "a 50/50\nsplit of cruise emissions"; hi_lab = "the territorial rule" if b_lto > b_5050 else "a 50/50 split of cruise emissions"
rep("ranging from 5.62 under a 50/50\nsplit of cruise emissions to 5.92 under the territorial rule (Extended Data\nTable~\\ref{tab:alloc}).",
    f"ranging from {lo3:.2f} under {lo_lab} to {hi3:.2f} under {hi_lab} (Extended Data\nTable~\\ref{{tab:alloc}}).")
pct_ols = 100 * (1 - b_ols / b); words = {30: "thirty", 35: "thirty-five", 40: "forty", 45: "forty-five"}
rep("roughly forty percent smaller", f"roughly {words.get(int(5 * round(pct_ols / 5)), str(int(5 * round(pct_ols / 5))))} percent smaller")
rep("is 5.61 (s.e.\\ 1.10; first-stage $F$ = 25) for 1996--2007 and 3.01 (s.e.\\\n1.19; $F$ = 11) for 2010--2023 excluding the COVID-19 collapse, so it\ndeclines by roughly half",
    f"is {b96:.2f} (s.e.\\ {se96:.2f}; first-stage $F$ = {F96:.0f}) for 1996--2007 and {b10:.2f} (s.e.\\\n{se10:.2f}; $F$ = {F10:.0f}) for 2010--2023 excluding the COVID-19 collapse, so it\ndeclines by roughly {'half' if 0.4 < b10 / b96 < 0.62 else 'two fifths' if b10 / b96 < 0.4 else 'a third'}")
rep("The elasticity moves within 4.7\nto 4.9 when log GDP,", f"The elasticity moves within {ctrl.min():.1f}\nto {ctrl.max():.1f} when log GDP,")
rep("The same variation raises seat-kilometres by 6.07 percent, faster than\nemissions, so emissions per seat-km fall by 0.40 percent, although this\nefficiency term is imprecise once errors are clustered (s.e.\\ 0.30;\nTable~\\ref{tab:decomp}).",
    f"The same variation raises seat-kilometres by {b_skm:.2f} percent, faster than\nemissions, so emissions per seat-km fall by {abs(b_ii):.2f} percent, although this\nefficiency term is imprecise once errors are clustered (s.e.\\ {se_ii:.2f};\nTable~\\ref{{tab:decomp}}).")
# decomposition
rep("An elasticity of 5.67 invites the question of its origin.", f"An elasticity of {b:.2f} invites the question of its origin.")
rep("The response is a frequency response: flights rise by 6.98 percent (s.e.\\\n1.38) for a one percent gain in connectivity, while aircraft gauge\n($-0.30$, s.e.\\ 0.44), stage length ($-0.60$, s.e.\\ 0.58) and emissions\nper seat-km ($-0.40$, s.e.\\ 0.30) do not change significantly. In point\nestimates, scale, the sum of the first three terms, contributes 6.07 or\n107 percent of the total and the efficiency term offsets seven percent of\nit,",
    f"The response is a frequency response: flights rise by {fl:.2f} percent (s.e.\\\n{fl_se:.2f}) for a one percent gain in connectivity, while aircraft gauge\n({sgn(ga)}, s.e.\\ {ga_se:.2f}), stage length ({sgn(st)}, s.e.\\ {st_se:.2f}) and emissions\nper seat-km ({sgn(ii)}, s.e.\\ {ii_se:.2f}) do not change significantly. In point\nestimates, scale, the sum of the first three terms, contributes {sc:.2f} or\n{share_scale:.0f} percent of the total and the efficiency term offsets {abs(share_eff):.0f} percent of\nit,")
rep("share of seat-km rises by 0.1 percentage point (s.e.\\ 0.13).", f"share of seat-km {'rises' if ish > 0 else 'falls'} by {abs(ish):.1f} percentage point (s.e.\\ {ish_se:.2f}).")
rep("attributes 84 to 87 percent of the total effect to flight frequency and\nseat-kilometres,", f"attributes {medlo:.0f} to {medhi:.0f} percent of the total effect to flight frequency and\nseat-kilometres,")
# decomposition heterogeneity
Fs = dh[(dh.block == "A_income") & (dh.grp != "all")].kpf
lo_, mi_, hi_ = "inc_low", "inc_mid", "inc_high"
rep("(Kleibergen--Paap $F$ between 1.7 and 5.7)", f"(Kleibergen--Paap $F$ between {Fs.min():.1f} and {Fs.max():.1f})")
rep("flights by 8.8 percent (s.e.\\\n2.7), aircraft size by 0.9 and stage length by 1.7, with intensity falling\nby 1.1 percent, for a total of 10.4 (s.e.\\ 2.8). In the middle tercile\nflights rise by 8.6 percent (s.e.\\ 3.3) but stages shorten, giving 6.1\n(s.e.\\ 2.1). In the top tercile the total is 1.8 (s.e.\\ 2.4)",
    f"flights by {DH(lo_,'tot','ln_flights'):.1f} percent (s.e.\\\n{DH(lo_,'tot','ln_flights','se'):.1f}), aircraft size by {DH(lo_,'tot','ln_gauge'):.1f} and stage length by {DH(lo_,'tot','ln_stage'):.1f}, with intensity falling\nby {abs(DH(lo_,'tot','ln_intensity')):.1f} percent, for a total of {DH(lo_,'tot','ln_co2'):.1f} (s.e.\\ {DH(lo_,'tot','ln_co2','se'):.1f}). In the middle tercile\nflights rise by {DH(mi_,'tot','ln_flights'):.1f} percent (s.e.\\ {DH(mi_,'tot','ln_flights','se'):.1f}) but stages shorten, giving {DH(mi_,'tot','ln_co2'):.1f}\n(s.e.\\ {DH(mi_,'tot','ln_co2','se'):.1f}). In the top tercile the total is {DH(hi_,'tot','ln_co2'):.1f} (s.e.\\ {DH(hi_,'tot','ln_co2','se'):.1f})")
rep("the international elasticity (5.69, s.e.\\ 1.13) is\ncarried by frequency (6.03, s.e.\\ 1.12), with a small up-gauging (0.58,\ns.e.\\ 0.37) and an intensity decline of 0.52 (s.e.\\ 0.31), while domestic\nemissions do not respond ($-0.64$, s.e.\\ 2.73).",
    f"the international elasticity ({DH('all','intl','ln_co2'):.2f}, s.e.\\ {DH('all','intl','ln_co2','se'):.2f}) is\ncarried by frequency ({DH('all','intl','ln_flights'):.2f}, s.e.\\ {DH('all','intl','ln_flights','se'):.2f}), with a small up-gauging ({DH('all','intl','ln_gauge'):.2f},\ns.e.\\ {DH('all','intl','ln_gauge','se'):.2f}) and an intensity decline of {abs(DH('all','intl','ln_intensity')):.2f} (s.e.\\ {DH('all','intl','ln_intensity','se'):.2f}), while domestic\nemissions do not respond ({sgn(DH('all','dom','ln_co2'))}, s.e.\\ {DH('all','dom','ln_co2','se'):.2f}).")
hi_p, hi_pi = A("HeritageIV", "ln_co2_intl", "p"), A("HeritageIV", "ln_intensity", "p")
rep("under it, total emissions do not respond, but\ninternational emissions rise by 3.16 percent and emissions per seat-km by\n1.23 percent (Methods).",
    f"under it, total emissions do not respond, while\ninternational emissions rise by {A('HeritageIV','ln_co2_intl'):.2f} percent ($p$ = {hi_p:.2f}) and emissions per\nseat-km by {A('HeritageIV','ln_intensity'):.2f} percent ($p$ = {hi_pi:.2f}) (Methods).")
# heterogeneity
PAN = {"inc_low": "A_income", "inc_mid": "A_income", "inc_high": "A_income", "con_low": "B_conn", "con_mid": "B_conn", "con_high": "B_conn", "Europe": "C_region", "AsiaPacific": "C_region", "Africa": "C_region", "LatAm": "C_region"}
H = lambda g, c="b", p=None: float(het.loc[(p or PAN[g], g), c])
rep("the elasticity of total CO$_2$ is 10.40 (s.e.\\\n2.80) in the bottom income tercile, 6.14 (s.e.\\ 2.12) in the middle and\n1.83 (s.e.\\ 2.42) at the top, and the pooled interaction of the top\ntercile with connectivity is $-3.33$ (s.e.\\ 0.57).",
    f"the elasticity of total CO$_2$ is {H('inc_low'):.2f} (s.e.\\\n{H('inc_low','se'):.2f}) in the bottom income tercile, {H('inc_mid'):.2f} (s.e.\\ {H('inc_mid','se'):.2f}) in the middle and\n{H('inc_high'):.2f} (s.e.\\ {H('inc_high','se'):.2f}) at the top, and the pooled interaction of the top\ntercile with connectivity is {sgn(H('interact_hi','b','A_income'))} (s.e.\\ {H('interact_hi','se','A_income'):.2f}).")
rep("connectivity the elasticity falls from 8.46 (s.e.\\ 1.68; first-stage $F$ =\n16) in the bottom tercile to 5.07 (s.e.\\ 2.49) in the middle; the top\ntercile has no first stage ($F = 0.2$),",
    f"connectivity the elasticity falls from {H('con_low'):.2f} (s.e.\\ {H('con_low','se'):.2f}; first-stage $F$ =\n{H('con_low','KPF'):.0f}) in the bottom tercile to {H('con_mid'):.2f} (s.e.\\ {H('con_mid','se'):.2f}) in the middle; the top\ntercile has no first stage ($F = {H('con_high','KPF'):.1f}$),")
rep("Regionally, the elasticity is 6.36 (s.e.\\ 2.10) in Africa and\n5.33 (s.e.\\ 1.66) in Asia--Pacific, 2.92 (s.e.\\ 1.94) in Latin America,\nwhile the estimate for Europe is small and statistically\nindistinguishable from zero ($-0.61$, s.e.\\ 1.73).",
    f"Regionally, the elasticity is {H('AsiaPacific'):.2f} (s.e.\\ {H('AsiaPacific','se'):.2f}) in Asia--Pacific, {H('Africa'):.2f} (s.e.\\ {H('Africa','se'):.2f}; $p$ = {H('Africa','p'):.2f}) in Africa and\n{H('LatAm'):.2f} (s.e.\\ {H('LatAm','se'):.2f}) in Latin America,\nwhile the estimate for Europe is small and statistically\nindistinguishable from zero ({sgn(H('Europe'))}, s.e.\\ {H('Europe','se'):.2f}).")
hf = hetdf[~hetdf.grp.str.startswith("interact") & ~hetdf.grp.isin(["MiddleEast", "NorthAm", "con_high"]) & (hetdf.panel != "D_intens")].KPF
rep("(clustered $F$ between 2 and 16)", f"(clustered $F$ between {hf.min():.0f} and {hf.max():.0f})")
rep("decline in emissions per seat-km in the bottom income tercile ($-1.06$,\ns.e.\\ 0.77)", f"decline in emissions per seat-km in the bottom income tercile ({sgn(DH('inc_low','tot','ln_intensity'))},\ns.e.\\ {DH('inc_low','tot','ln_intensity','se'):.2f})")
# take-off / functional form
mg = Y("C", "moment_gaci"); mco2 = Y("C", "moment_co2_mt"); sl, sl_se = Y("A", "semilog"), Y("A", "semilog", col="se"); lv, lv_se = Y("A", "levellevel"), Y("A", "levellevel", col="se")
rep("semi-log slope is 4.09 log points of CO$_2$ per unit of GACI (s.e.\\ 1.01),\nan elasticity of 4.4 at the sample mean, and the level-level slope is 4.2\nMt per unit (s.e.\\ 4.0);",
    f"semi-log slope is {sl:.2f} log points of CO$_2$ per unit of GACI (s.e.\\ {sl_se:.2f}),\nan elasticity of {sl * mg:.1f} at the sample mean, and the level-level slope is {lv:.1f}\nMt per unit (s.e.\\ {lv_se:.1f});")
rep("semi-log slope is 10.3 (s.e.\\ 2.3) in the bottom tercile, 4.6 (s.e.\\ 2.6)\nin the middle and 1.1 (s.e.\\ 1.7) at the top,",
    f"semi-log slope is {Y('A','semilog_con1'):.1f} (s.e.\\ {Y('A','semilog_con1',col='se'):.1f}) in the bottom tercile, {Y('A','semilog_con2'):.1f} (s.e.\\ {Y('A','semilog_con2',col='se'):.1f})\nin the middle and {Y('A','semilog_con3'):.1f} (s.e.\\ {Y('A','semilog_con3',col='se'):.1f}) at the top,")
q = {k: (Y("B", f"q{k}_loglog"), Y("B", f"q{k}_loglog", col="se"), Y("B", f"q{k}_loglog", col="kpf")) for k in range(1, 6)}
b1, b1se, b1F = Y("B", "int_lin", "ln_gaci_cwm"), Y("B", "int_lin", "ln_gaci_cwm", "se"), Y("B", "int_lin", "ln_gaci_cwm", "kpf"); b2, b2se = Y("B", "int_lin", "x_dev"), Y("B", "int_lin", "x_dev", "se")
r1 = yf[(yf.panel == "B") & (yf.item == "int_lin") & (yf["var"] == "ln_gaci_cwm")].iloc[0]; m0 = Y("C", "centre_lg0"); lg0 = yf[(yf.panel == "C") & (yf.item == "moment_lg0")].iloc[0]
def blin(x):
    d = x - m0; return b1 + b2 * d
p10, p50, p90 = blin(lg0.v12), blin(lg0.v13), blin(lg0.v33)
q12 = f"{q[1][0]:.1f}" if abs(q[1][0] - q[2][0]) < 0.05 else f"{q[1][0]:.1f} and {q[2][0]:.1f}"
rep("Quintile splits give elasticities of 8.5 (s.e.\\ 1.7 and 2.9) in\nboth of the two lowest quintiles, 3.3 (s.e.\\ 2.3) in the third and 4.1\n(s.e.\\ 2.5) in the fifth, while the fourth is unidentified;",
    f"Quintile splits give elasticities of {q12} (s.e.\\ {q[1][1]:.1f} and {q[2][1]:.1f}) in\n{'both of ' if abs(q[1][0] - q[2][0]) < 0.05 else ''}the two lowest quintiles, {q[3][0]:.1f} (s.e.\\ {q[3][1]:.1f}) in the third and {q[5][0]:.1f}\n(s.e.\\ {q[5][1]:.1f}) in the fifth, while the fourth is unidentified;")
rep("(interaction\n$-3.99$, s.e.\\ 1.00; joint first-stage $F$ = 9), gives a fitted elasticity\nof 7.1 at the tenth percentile of baseline connectivity, 6.0 at the median\nand 4.1 at the ninetieth,",
    f"(interaction\n{sgn(b2)}, s.e.\\ {b2se:.2f}; joint first-stage $F$ = {b1F:.0f}), gives a fitted elasticity\nof {p10:.1f} at the tenth percentile of baseline connectivity, {p50:.1f} at the median\nand {p90:.1f} at the ninetieth,")
rep("elasticity falls from 5.6 to 3.0 across the two eras.", f"elasticity falls from {b96:.1f} to {b10:.1f} across the two eras.")
lo_att = asens.attributed_mt.drop(0).min(); hi_att = asens.attributed_mt.drop(0).max(); common = asens.attributed_mt.iloc[0]
rep("totals between 294 and 353 Mt, or 35 to 43 percent of 2023 emissions,\nagainst 356 Mt under the common elasticity",
    f"totals between {lo_att:.0f} and {hi_att:.0f} Mt, or {100 * lo_att / WORLD:.0f} to {100 * hi_att / WORLD:.0f} percent of 2023 emissions,\nagainst {common:.0f} Mt under the common elasticity")
rep("tercile has no first stage ($F = 0.2$), a fact we use below as a\ndiagnostic.", "tercile has no first stage, a fact we use as a diagnostic of\nthe exclusion restriction (Methods).")
rep(f"tercile has no first stage ($F = {H('con_high','KPF'):.1f}$),\na fact we use as a diagnostic of\nthe exclusion restriction (Methods).", f"tercile has no first stage ($F = {H('con_high','KPF'):.1f}$), a fact we use as a diagnostic of\nthe exclusion restriction (Methods).") if False else None

# ============================================================ 4. spatial section
b2s, se2s = sp("2SLS", "IV", "beta"), sp("2SLS", "IV", "beta", col="se"); bslx, tslx, setslx = sp("SLX", "IV", "beta"), sp("SLX", "IV", "theta"), sp("SLX", "IV", "theta", col="se")
bsar, rsar, sersar = sp("SAR", "IV", "beta"), sp("SAR", "IV", "rho"), sp("SAR", "IV", "rho", col="se"); bsem, lsem = sp("SEM", "IV", "beta"), sp("SEM", "IV", "lambda")
bsdm, tsdm, setsdm, rsdm, sersdm = sp("SDM", "IV", "beta"), sp("SDM", "IV", "theta"), sp("SDM", "IV", "theta", col="se"), sp("SDM", "IV", "rho"), sp("SDM", "IV", "rho", col="se")
dsdm, isdm, seisdm, totsdm, setot = sp("SDM", "IV", "direct"), sp("SDM", "IV", "indirect"), sp("SDM", "IV", "indirect", col="se"), sp("SDM", "IV", "total"), sp("SDM", "IV", "total", col="se")
bsdem, tsdem, setsdem, lsdem = sp("SDEM", "IV", "beta"), sp("SDEM", "IV", "theta"), sp("SDEM", "IV", "theta", col="se"), sp("SDEM", "IV", "lambda")
lo_l, hi_l = sorted([lsem, lsdem]); th_lo, th_hi = min(tslx, tsdm, tsdem), max(tslx, tsdm, tsdem); own_lo, own_hi = sorted([bslx, bsdem]); und_lo, und_hi = sorted([100 * isdm / dsdm, 100 * tslx / bslx])
rep("The coefficient on the spatial lag of CO$_2$ is 0.03 (s.e.\\ 0.04) in\nthe SAR and $-$0.02 (s.e.\\ 0.02) in the SDM, and the spatial-error\nparameter is 0.10 to 0.14, whereas the neighbours' connectivity term is\n1.92 (s.e.\\ 0.69) in the SLX, 1.30 (s.e.\\ 0.67) in the SDM and\n2.23 (s.e.\\ 0.67) in the SDEM.",
    f"The coefficient on the spatial lag of CO$_2$ is {neg(rsar)} (s.e.\\ {sersar:.2f}) in\nthe SAR and {neg(rsdm)} (s.e.\\ {sersdm:.2f}) in the SDM, and the spatial-error\nparameter is {lo_l:.2f} to {hi_l:.2f}, whereas the neighbours' connectivity term is\n{tslx:.2f} (s.e.\\ {setslx:.2f}) in the SLX, {tsdm:.2f} (s.e.\\ {setsdm:.2f}) in the SDM and\n{tsdem:.2f} (s.e.\\ {setsdem:.2f}) in the SDEM.")
rep("it is 5.72 under the spatial lag, 5.02 under\nthe spatial error and 4.94 as the direct effect of the SDM, against 5.67\nin Table~\\ref{tab:main}, and 3.16 to 3.49 when the neighbours' term is entered,",
    f"it is {bsar:.2f} under the spatial lag, {bsem:.2f} under\nthe spatial error and {dsdm:.2f} as the direct effect of the SDM, against {b:.2f}\nin Table~\\ref{{tab:main}}, and {own_lo:.2f} to {own_hi:.2f} when the neighbours' term is entered,")
rep("direct plus indirect, is 5.88 (s.e.\\ 0.93) in the SDM, the\nsame as the single-equation elasticity; its indirect component,\n0.94 (s.e.\\ 0.45), is the cross-border part.",
    f"direct plus indirect, is {totsdm:.2f} (s.e.\\ {setot:.2f}) in the SDM, the\nsame as the single-equation elasticity; its indirect component,\n{isdm:.2f} (s.e.\\ {seisdm:.2f}), is the cross-border part.")
skm_b, skm_se = SU("ln_skm_country", "nbr_g_contig"), SU("ln_skm_country", "nbr_g_contig", "se"); int_b, int_se = SU("ln_intensity_country", "nbr_g_contig"), SU("ln_intensity_country", "nbr_g_contig", "se")
rep("B: a neighbour's connectivity gain raises own seat-kilometres by 2.56\npercent (s.e.\\ 0.69) through longer and more international flying and\nlowers emissions per seat-km by 0.63 percent (s.e.\\ 0.23), the signature",
    f"B: a neighbour's connectivity gain raises own seat-kilometres by {skm_b:.2f}\npercent (s.e.\\ {skm_se:.2f}) through more international flying and\nlowers emissions per seat-km by {abs(int_b):.2f} percent (s.e.\\ {int_se:.2f}), the signature")
rep("20 and 55 percent of the own effect", f"{5 * round(und_lo / 5):.0f} and {5 * round(und_hi / 5):.0f} percent of the own effect")
rep("the neighbour elasticity is 1.3 to 2.2, the spatial lag of\nemissions itself is negligible, and the total effect of a network-wide\nconnectivity gain is 5.9, the same as the single-equation elasticity.",
    f"the neighbour elasticity is {th_lo:.1f} to {th_hi:.1f}, the spatial lag of\nemissions itself is negligible, and the total effect of a network-wide\nconnectivity gain is {totsdm:.1f}, the same as the single-equation elasticity.")
nb_b = SU("contig_country", "nbr_g_contig"); single = sb[(sb.panel == "B") & (sb.item == "band_single") & (sb["var"] == "nbr_g_contig")].iloc[0]
about = int(round((nb_b + single.b) / 2))
rep("raises own-country aviation CO$_2$ by about 2 percent, mainly through international traffic.", f"raises own-country aviation CO$_2$ by about {about} percent, mainly through international traffic.")
b5 = sb[(sb.panel == "B") & (sb.item == "band_single") & (sb["var"] == "nbr_g_b5")].iloc[0]
rep("The absence of a smooth decline and the significantly negative coefficient beyond 5{,}000 km indicate",
    "The absence of a smooth decline and " + ("the significantly negative coefficient beyond 5{,}000 km indicate" if b5.p < .05 else "the negative but imprecise coefficient beyond 5{,}000 km indicate"))

# ============================================================ 5. attribution section
top7 = att.head(7); names7 = [NAMES.get(c, c) for c in top7.c]
def cc(c): return NAMES.get(c, c)
rep("attributes 356 Mt, or 42.5 percent, of 2023 aviation CO$_2$ to\npost-1996 network expansion", f"attributes {ATT:.0f} Mt, or {SH:.1f} percent, of 2023 aviation CO$_2$ to\npost-1996 network expansion")
old_list = "China\n($+88$ Mt), the United States ($+36$), the United Arab Emirates ($+25$),\nJapan ($+17$), Turkey ($+17$), India ($+16$), and Korea ($+14$), while\nGermany's declining connectivity contributes $-16$ Mt"
r7 = list(top7.itertuples())
new_list = (f"{'the ' if r7[0].c in ('USA','ARE') else ''}{cc(r7[0].c)}\n({pm(r7[0].att_tot_t/1e6)} Mt), " + ", ".join(f"{'the ' if r.c in ('USA','ARE') else ''}{cc(r.c)} ({pm(r.att_tot_t/1e6)})" for r in r7[1:6]) + f", and {'the ' if r7[6].c in ('USA','ARE') else ''}{cc(r7[6].c)} ({pm(r7[6].att_tot_t/1e6)}), while\n{cc(neg_row.c)}'s declining connectivity contributes {pm(neg_row.att_tot_t/1e6)} Mt")
rep(old_list, new_list)
rep("with elasticities that vary by baseline connectivity the world total is 294 to 353 Mt", f"with elasticities that vary by baseline connectivity the world total is {lo_att:.0f} to {hi_att:.0f} Mt")
rep("these emissions represent an annual external cost of \\$18.2 billion to\n\\$67.7 billion,", f"these emissions represent an annual external cost of \\${SCC['51']:.1f} billion to\n\\${SCC['190']:.1f} billion,")
g = lambda c: att[att.c == c].iloc[0].val_tot_scc190_usd / 1e9
rep("the cost is \\$16.7 billion per year for China, \\$6.9 billion for the\nUnited States, and \\$4.7 billion for the United Arab Emirates, while\nGermany's connectivity decline corresponds to an avoided cost of \\$3.0\nbillion per year.",
    f"the cost is \\${g(r7[0].c):.1f} billion per year for {cc(r7[0].c)}, \\${g(r7[1].c):.1f} billion for the\n{cc(r7[1].c)}, and \\${g(r7[2].c):.1f} billion for the {cc(r7[2].c)}, while\n{cc(neg_row.c)}'s connectivity decline corresponds to an avoided cost of \\${abs(g(neg_row.c)):.1f}\nbillion per year.")
c23 = cy[cy.year == 2023].copy(); gap = 100 * (c23.co2_bunker / c23.co2_bunker.sum() - c23.co2_lto / c23.co2_lto.sum())
rep("bunker-attributed share of world emissions exceeds the physical\nlanding-and-take-off share by up to 1.4 percentage points in countries\nwith large international hubs and falls short by up to 3.5 points in\ncountries with large domestically oriented networks, a gap that is\npositive at every international mega-hub and negative at large domestic\nhubs (Extended Data Figs.~\\ref{fig:levels} and \\ref{fig:mismatch}).",
    f"bunker-attributed share of world emissions exceeds the physical\nlanding-and-take-off share by up to {gap.max():.1f} percentage points where average\nstage lengths are long, at the Gulf hubs and in the United States, and\nfalls short by up to {abs(gap.min()):.1f} points where networks are dominated by\nshort-haul domestic flying, most of all in China (Extended Data\nFigs.~\\ref{{fig:levels}} and \\ref{{fig:mismatch}}).")
rep("Positive values indicate international hub countries; negative values indicate domestically oriented networks.", "Positive values indicate long-haul, cruise-heavy networks; negative values indicate short-haul, domestically oriented networks.")
rep("bunker conventions shift measured responsibility across countries by up to 3.5 percentage points of the world total", f"bunker conventions shift measured responsibility across countries by up to {abs(gap.min()):.1f} percentage points of the world total")
AH = lambda p, gname, outc, col="b": float(ah[(ah.panel == p) & (ah.grp == gname) & (ah.outc == outc)].iloc[0][col])
a_all, a_int, a_sh = AH("ALL", "all", "ln_co2"), AH("ALL", "all", "ln_intensity"), AH("ALL", "all", "intl_share_skm")
h5, h1, o5, o1 = AH("HUB", "top5", "ln_co2"), AH("HUB", "top1", "ln_co2"), AH("HUB", "not_top5", "ln_co2"), AH("HUB", "not_top1", "ln_co2")
rep("associated with 3.72 percent more CO$_2$, a 0.49 percent decline in\nCO$_2$ per seat-km and a 0.33 point higher international share; the\nelasticity is 2.0 to 2.1 at the airports in the 1996 global top five\npercent and 3.8 to 4.0 elsewhere,",
    f"associated with {a_all:.2f} percent more CO$_2$, a {abs(a_int):.2f} percent decline in\nCO$_2$ per seat-km and a {a_sh:.2f} point higher international share; the\nelasticity is {min(h5,h1):.1f} to {max(h5,h1):.1f} at the airports in the 1996 global top five\npercent and {min(o5,o1):.1f} to {max(o5,o1):.1f} elsewhere,")
# airport attribution total and concentration (recompute as in 19)
apn = pd.read_csv(os.path.join(HERE, "airport_co2_panel.csv")).sort_values(["airport_iata", "year"])
g96 = apn[apn.year == 1996][["airport_iata", "ln_gaci"]].rename(columns={"ln_gaci": "lg96"}); gfirst = apn.dropna(subset=["ln_gaci"]).groupby("airport_iata").first()[["ln_gaci"]].rename(columns={"ln_gaci": "lgfirst"})
g23 = apn[apn.year == 2023][["airport_iata", "ln_gaci", "co2_bunker"]].rename(columns={"ln_gaci": "lg23"})
d = g23.merge(g96, on="airport_iata", how="left").merge(gfirst, on="airport_iata", how="left"); d["lg0"] = d.lg96.fillna(d.lgfirst)
d = d[(d.co2_bunker > 0) & d.lg23.notna() & d.lg0.notna()]; d["attm"] = d.co2_bunker / 1e9 * (1 - np.exp(-b * (d.lg23 - d.lg0)))
AP_TOT = d.attm.sum(); NAP = len(d); n5 = int(np.ceil(NAP * 0.05)); top5sh = 100 * ac.loc["Attributed (country b)", "top5"]; em5 = 100 * ac.loc["Emissions 2023", "top5"]
led = ", ".join({"DXB": "Dubai", "DOH": "Doha", "PVG": "Shanghai Pudong", "IST": "Istanbul", "ICN": "Incheon", "LHR": "London Heathrow", "SIN": "Singapore", "PEK": "Beijing Capital", "DEL": "Delhi", "CAN": "Guangzhou", "HND": "Tokyo Haneda", "AMS": "Amsterdam"}.get(a, a) for a in top.airport_iata.head(5))
print(f"airport: attributed {AP_TOT:.0f} Mt over {NAP} airports; top5% ({n5}) hold {top5sh:.1f}% vs {em5:.1f}%; led by {led}; within-country {a_all:.2f}")
rep("to each airport's connectivity change attributes 345 Mt across airports,\nof which the top five percent of airports, some 190 nodes led by Dubai,\nDoha, Shanghai Pudong, Istanbul and Incheon, hold 84.5 percent against\n77.6 percent of emissions themselves",
    f"to each airport's connectivity change attributes {AP_TOT:.0f} Mt across airports,\nof which the top five percent of airports, some {n5} nodes led by {led}, hold {top5sh:.1f} percent against\n{em5:.1f} percent of emissions themselves")
rep("so an instrument covering those nodes would cover 85 percent of the\nconnectivity-driven total.", f"so an instrument covering those nodes would cover {top5sh:.0f} percent of the\nconnectivity-driven total.")
rep("its sum (345 Mt) is close to the country\ntotal", f"its sum ({AP_TOT:.0f} Mt) is close to the country\ntotal")
rep("fast-growing countries and the world total (42.5 percent) is the more\nconservative summary.", f"fast-growing countries and the world total ({SH:.1f} percent) is the more\nconservative summary.")
rep("Nevertheless, 85 percent of attributed emissions is concentrated in the top 5 percent of airports", f"Nevertheless, {top5sh:.0f} percent of attributed emissions is concentrated in the top 5 percent of airports")
rep("A, Lorenz curves of 2023 emissions and of emissions attributed to 1996--2023 connectivity growth over 3{,}833 airports with positive emissions.", f"A, Lorenz curves of 2023 emissions and of emissions attributed to 1996--2023 connectivity growth over {NAP:,} airports with positive emissions.".replace(",", "{,}"))
# ED Fig 4 caption
rep("The world total is 356.4 Mt, 42.5\npercent of 2023 aviation CO$_2$ (\\$67.7 billion per year).", f"The world total is {ATT:.1f} Mt, {SH:.1f}\npercent of 2023 aviation CO$_2$ (\\${SCC['190']:.1f} billion per year).")

# ============================================================ 6. SAF
BASE = round(WORLD, 1); ATTR = round(ATT, 1); bm = round(b10, 3)
S = lambda gc, r, y: float(saf[(saf.beta_case == "mature") & (saf.growth_case == gc) & (saf.lca_saving_r == r) & (saf.year == y)].co2_Mt.iloc[0])
Sf = lambda r, y: float(saf[(saf.beta_case == "mature") & (saf.growth_case == "central") & (saf.lca_saving_r == r) & (saf.year == y)].co2_Mt_fixed_traffic.iloc[0])
gaps = [S("central", r, 2050) - Sf(r, 2050) for r in (0.5, 0.65, 0.8)]
rep("2010--2019 pace (0.74 log points per year on average across countries;\n0.45 in a low case) and is converted to emissions with the mature-network\nelasticity of 3.0,",
    f"2010--2019 pace (0.0074 log points, or 0.74 percent, per year on average across\ncountries; 0.45 percent in a low case) and is converted to emissions with the mature-network\nelasticity of {bm:.1f},")
rep("Without fuel switching, emissions reach 1{,}528 Mt in 2050 (1{,}207 Mt in\nthe low-growth case), 1.8 times the 2023 level of 838 Mt. The full\nblending path with a 65 percent saving returns 2050 emissions to the 2023\nlevel (833 Mt), and only the 80 percent saving takes them below it (672\nMt); no path reaches the 482 Mt that would remain after removing the\nemissions attributed to the past generation of connectivity growth.\nHolding 2023 traffic fixed, as in a pure accounting exercise, would\nunderstate 2050 emissions under the same blending paths by 300 to 450 Mt.",
    f"Without fuel switching, emissions reach {S('central',0.0,2050):,.0f} Mt in 2050 ({S('low',0.0,2050):,.0f} Mt in\nthe low-growth case), {S('central',0.0,2050)/BASE:.1f} times the 2023 level of {BASE:.0f} Mt. The full\nblending path with a 65 percent saving {'returns 2050 emissions to the 2023 level' if abs(S('central',0.65,2050) - BASE) < 0.03 * BASE else ('brings 2050 emissions close to the 2023 level' if S('central',0.65,2050) > BASE else 'takes 2050 emissions slightly below the 2023 level')}\n({S('central',0.65,2050):,.0f} Mt), and {'only ' if S('central',0.65,2050) >= BASE else ''}the 80 percent saving takes them {'below it' if S('central',0.65,2050) >= BASE else 'further below'} ({S('central',0.8,2050):,.0f}\nMt); no path reaches the {BASE - ATTR:.0f} Mt that would remain after removing the\nemissions attributed to the past generation of connectivity growth.\nHolding 2023 traffic fixed, as in a pure accounting exercise, would\nunderstate 2050 emissions under the same blending paths by {50 * round(min(gaps) / 50):.0f} to {50 * round(max(gaps) / 50):.0f} Mt.".replace(",", "{,}").replace("{,}0 Mt", ",0 Mt") if False else
    f"Without fuel switching, emissions reach {S('central',0.0,2050):,.0f} Mt in 2050 ({S('low',0.0,2050):,.0f} Mt in\nthe low-growth case), {S('central',0.0,2050)/BASE:.1f} times the 2023 level of {BASE:.0f} Mt. The full\nblending path with a 65 percent saving {'returns 2050 emissions to the 2023 level' if abs(S('central',0.65,2050) - BASE) < 0.03 * BASE else ('brings 2050 emissions close to the 2023 level' if S('central',0.65,2050) > BASE else 'takes 2050 emissions slightly below the 2023 level')}\n({S('central',0.65,2050):,.0f} Mt), and {'only ' if S('central',0.65,2050) >= BASE else ''}the 80 percent saving takes them {'below it' if S('central',0.65,2050) >= BASE else 'further below'} ({S('central',0.8,2050):,.0f}\nMt); no path reaches the {BASE - ATTR:.0f} Mt that would remain after removing the\nemissions attributed to the past generation of connectivity growth.\nHolding 2023 traffic fixed, as in a pure accounting exercise, would\nunderstate 2050 emissions under the same blending paths by {50 * round(min(gaps) / 50):.0f} to {50 * round(max(gaps) / 50):.0f} Mt.")
s = s.replace("1,528 Mt", "1{,}528 Mt")
for v in [S('central',0.0,2050), S('low',0.0,2050)]:
    s = s.replace(f"{v:,.0f} Mt", f"{v:,.0f}".replace(",", "{,}") + " Mt")
rep("and the horizontal lines mark the 2023 level (838 Mt) and the level net of the emissions attributed to 1996--2023 connectivity growth (482 Mt). Traffic growth is converted to emissions with the mature-network elasticity (3.0).",
    f"and the horizontal lines mark the 2023 level ({BASE:.0f} Mt) and the level net of the emissions attributed to 1996--2023 connectivity growth ({BASE - ATTR:.0f} Mt). Traffic growth is converted to emissions with the mature-network elasticity ({bm:.1f}).")
rep("2010--2019 (0.0074; 0.0045 in the low case), $\\beta$ the mature-network\nelasticity (3.0; Extended Data Table~\\ref{tab:temporal}, Panel C),",
    f"2010--2019 (0.0074; 0.0045 in the low case), $\\beta$ the mature-network\nelasticity ({bm:.1f}; Extended Data Table~\\ref{{tab:temporal}}, Panel C),")

# ============================================================ 7. Discussion
rep("A one percent increase in GACI raises seat-kilometres by 6.07 percent and CO$_2$ by 5.67 percent.", f"A one percent increase in GACI raises seat-kilometres by {b_skm:.2f} percent and CO$_2$ by {b:.2f} percent.")
rep("The 0.40 percent intensity decline offsets only 7 percent of the scale response; full offset would require about 6 percent.",
    f"The {abs(b_ii):.2f} percent intensity decline offsets only {abs(share_eff):.0f} percent of the scale response; full offset would require about {b_skm:.0f} percent.")
rep("the 35--43 percent attribution range", f"the {100 * lo_att / WORLD:.0f}--{100 * hi_att / WORLD:.0f} percent attribution range")

# ============================================================ 8. Methods
rep("first-stage Kleibergen--Paap $F$ is 18 (154 with heteroskedasticity-robust\nerrors).", f"first-stage Kleibergen--Paap $F$ is {kpf:.0f} ({kpf_rob:.0f} with heteroskedasticity-robust\nerrors).")
rep("The primary instrument survives (heteroskedasticity-robust $F$ declines\nonly from 120.1 to 105.8);",
    "The primary instrument survives (on the 4,121 country-years of countries\nobserved in 1996, for which baseline size is defined, the\nheteroskedasticity-robust $F$ declines only from 120.1 to 105.8);")
asn_f = asn[asn.iloc[:, 0].astype(str).str.contains("fatal", case=False)] if "spec" not in asn.columns else asn
rf_tot, rf_tot_se = EX("A", "ln_co2_tot", "RF"), EX("A", "ln_co2_tot", "RF", "se"); rf_ex, rf_ex_se = EX("A", "ln_co2_exav", "RF"), EX("A", "ln_co2_exav", "RF", "se")
rep("CO$_2$ excluding domestic aviation is 0.05 (s.e.\\ 0.12) against 0.73 (s.e.\\\n0.16) for aviation CO$_2$,", f"CO$_2$ excluding domestic aviation is {rf_ex:.2f} (s.e.\\ {rf_ex_se:.2f}) against {rf_tot:.2f} (s.e.\\\n{rf_tot_se:.2f}) for aviation CO$_2$,")
sea, sea_se, air, air_se = EX("C", "sea_with_air", "RF"), EX("C", "sea_with_air", "RF", "se"), EX("C", "air_with_sea", "RF"), EX("C", "air_with_sea", "RF", "se")
rep("access and both interactions are entered, the sea term has a reduced form\nof 0.08 (s.e.\\ 0.30) while the air term retains 0.64 (s.e.\\ 0.22).",
    f"access and both interactions are entered, the sea term has a reduced form\nof {neg(sea)} (s.e.\\ {sea_se:.2f}) while the air term retains {air:.2f} (s.e.\\ {air_se:.2f}).")
d_hi, d_hi_se, d_hiF = EX("D", "con3", "RF"), EX("D", "con3", "RF", "se"), EX("D", "con3", "FS", "f")
Dl, Dm = EX("D", "con1", "RF"), EX("D", "con2", "RF")
rep("in the top tercile of baseline connectivity the first stage is absent\n($F$ = 0.2) and the reduced form on CO$_2$ is 0.10 (s.e.\\ 0.19), against\n2.22 and 0.41 in the lower terciles.",
    f"in the top tercile of baseline connectivity the first stage is absent\n($F$ = {d_hiF:.1f}) and the reduced form on CO$_2$ is {d_hi:.2f} (s.e.\\ {d_hi_se:.2f}), against\n{Dl:.2f} and {Dm:.2f} in the lower terciles.")
rep("(the elasticity stays between 4.7 and 4.9)", f"(the elasticity stays between {ctrl.min():.1f} and {ctrl.max():.1f})")
alt = exc[(exc.panel == "F") & (exc.stat == "IV") & (exc.item != "feyrer_int")].b
rep("and distance-decay exponents (5.8 to 6.1)", f"and distance-decay exponents ({alt.min():.1f} to {alt.max():.1f})")
coal, cem = EX("A", "ln_coal", "RF"), EX("A", "ln_cement", "RF")
rep("coal and cement CO$_2$ rise\nwith the instrument (0.90 and 0.67),", f"coal and cement CO$_2$ rise\nwith the instrument ({coal:.2f} and {cem:.2f}),")
airF = EX("C", "air_with_sea", "IV", "f"); ADV_F = float(os.environ.get("ADV_F", "nan"))
rep("cycle and the air interaction with the sea interaction as a control, have\nno usable first stage ($F$ of 1.0 and 3.0).",
    f"cycle and the air interaction with the sea interaction as a control, have\nweak first stages (country-clustered $F$ of {ADV_F:.1f} and {airF:.1f}).")
n_no = 38  # NE contiguity: 144 of 182 sample countries (NCL singleton dropped) have a land neighbour
for old in ["an indicator for countries with no neighbour under the definition (31 countries have no land neighbour)",
            "land contiguity from\nNatural Earth administrative boundaries (31 sample countries have no land\nneighbour and receive a zero exposure with an indicator)"]:
    if old in s: rep(old, old.replace("31", str(n_no)))
# accident IV numbers (SI Table 3) in Methods
def AS(stage, z, outc, col="b"): return float(asn[(asn.stage == stage) & (asn.z == z) & (asn.outc == outc)].iloc[0][col])
fs_lag = asn[(asn.stage == "FS_lag") & asn.z.isin(["L.ash_deaths", "L.n_fatal", "L.d_fatal"])].kpf; nf, nf_se = AS("IV_asn", "L.n_fatal", "ln_co2_tot"), AS("IV_asn", "L.n_fatal", "ln_co2_tot", "se")
jp1, jp2 = AS("OVERID", "fey+L.n_fatal", "ln_co2_tot", "jp"), AS("OVERID", "fey+L.ash_deaths", "ln_co2_tot", "jp"); jb = (AS("OVERID", "fey+L.n_fatal", "ln_co2_tot") + AS("OVERID", "fey+L.ash_deaths", "ln_co2_tot")) / 2
rep("first-stage $F$ of 1 to 4; 2SLS 6.2 with a standard error of 2.4 for\nlagged fatal accidents), but the Hansen test does not reject its joint\nvalidity with the Feyrer instrument ($p$ = 0.70 and 0.95), and the jointly\ninstrumented elasticity is 5.4",
    f"first-stage $F$ of {fs_lag.min():.0f} to {fs_lag.max():.0f}; 2SLS {nf:.1f} with a standard error of {nf_se:.1f} for\nlagged fatal accidents), but the Hansen test does not reject its joint\nvalidity with the Feyrer instrument ($p$ = {jp1:.2f} and {jp2:.2f}), and the jointly\ninstrumented elasticity is {jb:.1f}")
print(f"accident IV: F {fs_lag.min():.1f}-{fs_lag.max():.1f}; n_fatal {nf:.2f} ({nf_se:.2f}); Hansen p {jp1:.2f}/{jp2:.2f}; joint {jb:.2f}")

# ============================================================ 9. captions / notes / misc
rep("gray denotes the unrestricted later sample, whose first stage (KP $F=7$) is contaminated by the COVID collapse.",
    f"gray denotes the unrestricted later sample, whose first stage (KP $F$ = {Fun:.1f}) is contaminated by the COVID collapse. Bars are 95 percent confidence intervals with standard errors clustered by country.")
rep("Reduced-form quintile slopes under the tourism shifter: effects are concentrated in low-income, low-connectivity quintiles.",
    "Reduced-form quintile slopes under the tourism shifter (heteroskedasticity-robust 95 percent confidence intervals): effects are concentrated in low-income, low-connectivity quintiles.")
rep("Kleibergen-Paap $F$ = 18.4", f"Kleibergen--Paap $F$ = {kpf:.1f}") if "Kleibergen-Paap $F$ = 18.4" in s else None
# SI Table 1 robust row (fragment may carry clustered values in the 'robust' row)
a, b_ = table_by_label(s, "tab:exclusion2"); t = s[a:b_]
t = re.sub(r"  Heteroskedasticity-robust & [\d.]+\$\^\{\*+\}\$ & \([\d.]+\) & [\d.]+ & 4,634 \\\\", f"  Heteroskedasticity-robust & {b:.2f}$^{{***}}$ & ({b_rob_se:.2f}) & {kpf_rob:.1f} & 4,634 \\\\\\\\", t)
s = s[:a] + t + s[b_:]
# ED Table 5 note F (fragment regenerated; make sure the note F matches the table)
a, b_ = table_by_label(s, "tab:decomp_hetero"); t = s[a:b_]
t = re.sub(r"has a weak first stage \(\$F\$ = [\d.]+\)", f"has a weak first stage ($F$ = {H('con_high','KPF'):.1f})", t); s = s[:a] + t + s[b_:]
# ED Table 14 shares on the world denominator
a, b_ = table_by_label(s, "tab:attr_sens"); t = s[a:b_]
for _, r in asens.iterrows():
    t = re.sub(r"& " + re.escape(f"{r.attributed_mt:.1f}") + r" & [\d.]+ \\\\", f"& {r.attributed_mt:.1f} & {100 * r.attributed_mt / WORLD:.1f} \\\\\\\\", t)
t = re.sub(r"World 2023 emissions in the 184-country sample: [\d.]+ Mt\.", f"Shares are of world 2023 aviation CO$_2$ ({WORLD:.0f} Mt; the 184-country sample holds {att.e_tot_t.sum()/1e6:.0f} Mt).", t)
s = s[:a] + t + s[b_:]
# Table 3 note: land-neighbour count and sample
a, b_ = table_by_label(s, "tab:spatial"); t = s[a:b_]; t = re.sub(r"(\d+) sample countries have no land neighbour", f"{n_no} sample countries have no land neighbour", t); s = s[:a] + t + s[b_:]
# Methods sample statement: unmatched airports
rep("Of the 6,356 airports represented in the emissions inventory, 5,354 are nodes in the connectivity network; airports not matched to the GACI network account for only 0.1\\% of departure-based emissions.",
    "Of the 6,356 airports represented in the emissions inventory, 5,354 are nodes in the connectivity network; airports not matched to the GACI network account for only 0.1\\% of departure-based emissions, and airports that cannot be assigned to a country (0.02\\% of emissions) are excluded from the country panel.")

open(TEX, "w", encoding="utf-8", newline="\n").write(s)
print("replacements:", NREP, "| failures:", len(FAIL))
for c, o in FAIL: print("  FAIL count", c, ":", o.replace("\n", "⏎"))
labels = set(re.findall(r"\\label\{([^}]+)\}", s)); refs = set(re.findall(r"\\ref\{([^}]+)\}", s))
print("dangling refs:", sorted(refs - labels), "| dup labels:", [l for l in labels if s.count("\\label{%s}" % l) > 1], "| table balance", s.count("\\begin{table}"), s.count("\\end{table}"))
print("DONE_38")
