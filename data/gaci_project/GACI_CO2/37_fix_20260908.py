# -*- coding: utf-8 -*-
r"""
37_fix_20260908.py   (2026-09-08)  accuracy fixes on FINAL_20260908/main_co2_nature_20260908.tex
 1. Table 3 / ED Table 10 replaced by the rerun spatial fragments (32/33: Eswatini restored,
    singleton dropped, N = 4,634); spatial prose (abstract, Results, Discussion) regenerated
    from _spatial_models.csv.
 2. ED Tables 8-9 replaced by the rerun spillover fragments (21 -> Stata -> 24); spillover
    prose numbers regenerated from _spill_supp.csv / _spill_placebo_summary.csv.
 3. SAF growth-rate unit (0.0074 log points = 0.74 percent per year).
 4. SI Table 1 Panel C robust row: true heteroskedasticity-robust s.e. (0.41) and KP F (153.6).
 5. ED Table 5 note F = 0.2 (was 1.8); ED Fig 10 caption (beyond-5,000 km coefficient is imprecise,
    not significant); ED Fig 1 caption (KP F = 3.2, clustered); ED Fig 9 caption (robust CIs).
 6. Land-neighbour count unified to the Natural Earth count used by every W (39).
 7. Attribution shares on one denominator (world 2023 = 838 Mt) in ED Table 14, Results, Discussion.
 8. Methods: stress-test F on the 4,121 sample; tourism-IV p-values; mismatch sentence and ED Fig 6
    caption (stage length, not international orientation); 'below' -> Methods; wording fixes.
"""
import os, re, shutil, sys
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, "FINAL_20260908")
TEX = os.path.join(FIN, "main_co2_nature_20260908.tex")
BS = chr(92)
shutil.copy(TEX, os.path.join(FIN, "_bak_main_co2_nature_20260908_prefix.tex"))
s = open(TEX, encoding="utf-8").read()
nrep = 0
def rep(old, new, count=1):
    global s, nrep
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new); nrep += 1
def table_by_label(src, label):
    i = src.find(BS + "label{%s}" % label); assert i >= 0, label
    a = src.rfind(BS + "begin{table}", 0, i); b = src.find(BS + "end{table}", i) + len(BS + "end{table}")
    return a, b
def swap_table(label, fragsrc):
    global s
    a, b = table_by_label(s, label); fa, fb = table_by_label(fragsrc, label)
    frag = fragsrc[fa:fb]
    # keep the Extended Data numbering caption prefix of the manuscript if the fragment lacks it
    mcap = re.search(r"\\caption\{([^}]*)\}", s[a:b]).group(1); fcap = re.search(r"\\caption\{([^}]*)\}", frag).group(1)
    if mcap.startswith("Extended Data Table") and not fcap.startswith("Extended Data Table"):
        frag = frag.replace(BS + "caption{" + fcap + "}", BS + "caption{" + mcap + "}")
    # manuscript uses [H] + resizebox wrapper; reuse the manuscript's wrapper lines if fragment differs
    s = s[:a] + frag + s[b:]
    print("swapped", label)
f2 = lambda x: f"{x:.2f}"
def neg(x): return ("$-$" + f"{abs(x):.2f}") if x < 0 else f"{x:.2f}"

# ------------------------------------------------------------------ 1. spatial
SP = pd.read_csv(os.path.join(HERE, "_spatial_models.csv"))
def sp(model, est, term, W="contig", outc="ln_co2_tot"):
    r = SP[(SP.W == W) & (SP.outcome == outc) & (SP.model == model) & (SP.estimator == est) & (SP.term == term)]
    assert len(r), (model, est, term); return float(r.iloc[0].b), float(r.iloc[0].se_cl)
frag = open(os.path.join(HERE, "_tex_spatial.tex"), encoding="utf-8").read()
swap_table("tab:spatial", frag); swap_table("tab:spatial_ext", frag)
N_sp = int(SP[(SP.W == "contig") & (SP.outcome == "ln_co2_tot")].N.iloc[0])
b2, se2 = sp("2SLS", "IV", "beta"); bslx, seslx = sp("SLX", "IV", "beta"); tslx, setslx = sp("SLX", "IV", "theta")
bsar, _ = sp("SAR", "IV", "beta"); rsar, sersar = sp("SAR", "IV", "rho"); bsem, _ = sp("SEM", "IV", "beta"); lsem, _ = sp("SEM", "IV", "lambda")
bsdm, _ = sp("SDM", "IV", "beta"); tsdm, setsdm = sp("SDM", "IV", "theta"); rsdm, sersdm = sp("SDM", "IV", "rho")
dsdm, _ = sp("SDM", "IV", "direct"); isdm, seisdm = sp("SDM", "IV", "indirect"); totsdm, setot = sp("SDM", "IV", "total")
bsdem, _ = sp("SDEM", "IV", "beta"); tsdem, setsdem = sp("SDEM", "IV", "theta"); lsdem, _ = sp("SDEM", "IV", "lambda")
lo_l, hi_l = sorted([lsem, lsdem]); th_lo, th_hi = min(tslx, tsdm, tsdem), max(tslx, tsdm, tsdem)
own_lo, own_hi = sorted([bslx, bsdem])
und_lo, und_hi = sorted([100 * isdm / dsdm, 100 * tslx / bslx])
print(f"spatial: 2SLS {b2:.2f} ({se2:.2f}) N {N_sp}; SLX {bslx:.2f}/{tslx:.2f}; SAR b {bsar:.2f} rho {rsar:.2f} ({sersar:.2f}); SEM {bsem:.2f} lam {lsem:.2f}; "
      f"SDM b {bsdm:.2f} th {tsdm:.2f} ({setsdm:.2f}) rho {rsdm:.2f} ({sersdm:.2f}) direct {dsdm:.2f} indirect {isdm:.2f} ({seisdm:.2f}) total {totsdm:.2f} ({setot:.2f}); "
      f"SDEM {bsdem:.2f} th {tsdem:.2f} ({setsdem:.2f}) lam {lsdem:.2f}; understate {und_lo:.0f}-{und_hi:.0f}%")
rep("The coefficient on the spatial lag of CO$_2$ is 0.03 (s.e.\\ 0.04) in\nthe SAR and $-$0.02 (s.e.\\ 0.02) in the SDM, and the spatial-error\nparameter is 0.10 to 0.14, whereas the neighbours' connectivity term is\n1.92 (s.e.\\ 0.69) in the SLX, 1.30 (s.e.\\ 0.67) in the SDM and\n2.23 (s.e.\\ 0.67) in the SDEM.",
    f"The coefficient on the spatial lag of CO$_2$ is {neg(rsar)} (s.e.\\ {f2(sersar)}) in\nthe SAR and {neg(rsdm)} (s.e.\\ {f2(sersdm)}) in the SDM, and the spatial-error\nparameter is {f2(lo_l)} to {f2(hi_l)}, whereas the neighbours' connectivity term is\n{f2(tslx)} (s.e.\\ {f2(setslx)}) in the SLX, {f2(tsdm)} (s.e.\\ {f2(setsdm)}) in the SDM and\n{f2(tsdem)} (s.e.\\ {f2(setsdem)}) in the SDEM.")
rep("it is 5.72 under the spatial lag, 5.02 under\nthe spatial error and 4.94 as the direct effect of the SDM, against 5.67\nin Table~\\ref{tab:main}, and 3.16 to 3.49 when the neighbours' term is entered,",
    f"it is {f2(bsar)} under the spatial lag, {f2(bsem)} under\nthe spatial error and {f2(dsdm)} as the direct effect of the SDM, against 5.67\nin Table~\\ref{{tab:main}}, and {f2(own_lo)} to {f2(own_hi)} when the neighbours' term is entered,")
rep("direct plus indirect, is 5.88 (s.e.\\ 0.93) in the SDM, the\nsame as the single-equation elasticity; its indirect component,\n0.94 (s.e.\\ 0.45), is the cross-border part.",
    f"direct plus indirect, is {f2(totsdm)} (s.e.\\ {f2(setot)}) in the SDM, the\nsame as the single-equation elasticity; its indirect component,\n{f2(isdm)} (s.e.\\ {f2(seisdm)}), is the cross-border part.")
rep("20 and 55 percent of the own effect", f"{round(und_lo / 5) * 5:.0f} and {round(und_hi / 5) * 5:.0f} percent of the own effect")
rep("the neighbour elasticity is 1.3 to 2.2, the spatial lag of\nemissions itself is negligible, and the total effect of a network-wide\nconnectivity gain is 5.9, the same as the single-equation elasticity.",
    f"the neighbour elasticity is {th_lo:.1f} to {th_hi:.1f}, the spatial lag of\nemissions itself is negligible, and the total effect of a network-wide\nconnectivity gain is {totsdm:.1f}, the same as the single-equation elasticity.")
rep("percent (s.e.\\ 0.69) through longer and more international flying and\nlowers emissions per seat-km by 0.63 percent (s.e.\\ 0.23), the signature",
    "percent (s.e.\\ 0.69) through more international flying and\nlowers emissions per seat-km by 0.63 percent (s.e.\\ 0.23), the signature")  # numbers patched below from _spill_supp

# ------------------------------------------------------------------ 2. spillover
frag2 = open(os.path.join(HERE, "_tex_spill_cl.tex"), encoding="utf-8").read()
swap_table("tab:spillover", frag2); swap_table("tab:spill_ext", frag2)
supp = pd.read_csv(os.path.join(HERE, "_spill_supp.csv"))
def su(item, var):
    r = supp[(supp.item == item) & (supp["var"] == var)]; assert len(r), (item, var); return float(r.iloc[0].b), float(r.iloc[0].se)
skm_b, skm_se = su("ln_skm_country", "nbr_g_contig"); int_b, int_se = su("ln_intensity_country", "nbr_g_contig")
nb_b, nb_se = su("contig_country", "nbr_g_contig"); own_b, own_se = su("contig_country", "ln_gaci_cwm")
sb = pd.read_csv(os.path.join(HERE, "_spill_bands_cl.csv"))
single = sb[(sb.panel == "B") & (sb.item == "band_single") & (sb["var"] == "nbr_g_contig")].iloc[0]
b5 = sb[(sb.panel == "B") & (sb.item == "band_single") & (sb["var"] == "nbr_g_b5")].iloc[0]
summ = pd.read_csv(os.path.join(HERE, "_spill_placebo_summary.csv"), index_col=0)
print(f"spill: joint contig own {own_b:.2f} ({own_se:.2f}) nbr {nb_b:.2f} ({nb_se:.2f}); single {single.b:.2f} ({single.se:.2f}); skm {skm_b:.2f} ({skm_se:.2f}); "
      f"intensity {int_b:.2f} ({int_se:.2f}); b5 {b5.b:.2f} ({b5.se:.2f}) p {b5.p:.2f}; perm p contig {summ.loc['contig','p_perm_t']:.3f} knn5 {summ.loc['knn5','p_perm_t']:.3f}")
rep("B: a neighbour's connectivity gain raises own seat-kilometres by 2.56\npercent (s.e.\\ 0.69) through more international flying and\nlowers emissions per seat-km by 0.63 percent (s.e.\\ 0.23), the signature",
    f"B: a neighbour's connectivity gain raises own seat-kilometres by {f2(skm_b)}\npercent (s.e.\\ {f2(skm_se)}) through more international flying and\nlowers emissions per seat-km by {f2(abs(int_b))} percent (s.e.\\ {f2(int_se)}), the signature")
about = round((nb_b + single.b) / 2)
rep("raises own-country aviation CO$_2$ by about 2 percent, mainly through international traffic.",
    f"raises own-country aviation CO$_2$ by about {about} percent, mainly through international traffic.")
b5txt = ("the significantly negative coefficient beyond 5{,}000 km" if b5.p < .05 else "the negative but imprecise coefficient beyond 5{,}000 km")
rep("The absence of a smooth decline and the significantly negative coefficient beyond 5{,}000 km indicate that wide exposures track global trends rather than a spatial spillover.",
    f"The absence of a smooth decline and {b5txt} indicate that wide exposures track global trends rather than a spatial spillover.")

# ------------------------------------------------------------------ 2b. exclusion suite (full-sample baseline geography, 22 fix)
frag3 = open(os.path.join(HERE, "_tex_exclusion_cl.tex"), encoding="utf-8").read()
swap_table("tab:exclusion", frag3); swap_table("tab:exclusion2", frag3)
exc = pd.read_csv(os.path.join(HERE, "_exclusion_suite_cl.csv"))
def ex_(panel, item, stat):
    r = exc[(exc.panel == panel) & (exc.item == item) & (exc.stat == stat)]; assert len(r), (panel, item, stat); return r.iloc[0]
sea = ex_("C", "sea_with_air", "RF"); air = ex_("C", "air_with_sea", "RF"); airF = ex_("C", "air_with_sea", "IV")
alt = exc[(exc.panel == "F") & (exc.stat == "IV") & (exc.item != "feyrer_int")].b
print(f"exclusion: sea RF {sea.b:.2f} ({sea.se:.2f}); air RF {air.b:.2f} ({air.se:.2f}); air-with-sea F {airF.f:.1f}; alt shifters {alt.min():.2f}-{alt.max():.2f}; N {int(sea.nn)}")
rep("access and both interactions are entered, the sea term has a reduced form\nof 0.08 (s.e.\\ 0.30) while the air term retains 0.64 (s.e.\\ 0.22).",
    f"access and both interactions are entered, the sea term has a reduced form\nof {neg(sea.b)} (s.e.\\ {f2(sea.se)}) while the air term retains {f2(air.b)} (s.e.\\ {f2(air.se)}).")
rep("and distance-decay exponents (5.8 to 6.1)", f"and distance-decay exponents ({alt.min():.1f} to {alt.max():.1f})")
ADV_F = float(os.environ.get("ADV_F", "nan"))
rep("cycle and the air interaction with the sea interaction as a control, have\nno usable first stage ($F$ of 1.0 and 3.0).",
    f"cycle and the air interaction with the sea interaction as a control, have\nweak first stages (country-clustered $F$ of {ADV_F:.1f} and {airF.f:.1f}).")
rep("(Extended Data Table~\\ref{tab:exclusion}, Panels A, C and D;", "(Extended Data Table~\\ref{tab:exclusion}, Panels A, C and D;")  # unchanged anchor check
# Table 4 note: attribution window for late entrants
rep("to each country's 1996--2023 change in log connectivity: attributed share",
    "to each country's 1996--2023 change in log connectivity (the first and last years in which the country is observed, for the 34 countries entering after 1996 and the 18 whose series end before 2023): attributed share")

# ------------------------------------------------------------------ 3. SAF unit
rep("2010--2019 pace (0.74 log points per year on average across countries;\n0.45 in a low case)",
    "2010--2019 pace (0.0074 log points, or 0.74 percent, per year on average across\ncountries; 0.45 percent in a low case)")

# ------------------------------------------------------------------ 4. SI Table 1 robust row
ex = pd.read_csv(os.path.join(HERE, "_exclusion_suite.csv")); r = ex[(ex.panel == "I") & (ex.item == "robust")].iloc[0]
rep("  Heteroskedasticity-robust & 5.67$^{***}$ & (1.12) & 18.4 & 4,634 \\\\",
    f"  Heteroskedasticity-robust & {r.b:.2f}$^{{***}}$ & ({r.se:.2f}) & {r.f:.1f} & {int(r.nn):,} \\\\")

# ------------------------------------------------------------------ 5. captions / notes
rep("The high-connectivity tercile has a weak first stage ($F$ = 1.8)", "The high-connectivity tercile has a weak first stage ($F$ = 0.2)")
rep("gray denotes the unrestricted later sample, whose first stage (KP $F=7$) is contaminated by the COVID collapse.",
    "gray denotes the unrestricted later sample, whose first stage (KP $F$ = 3.2) is contaminated by the COVID collapse. Bars are 95 percent confidence intervals with standard errors clustered by country.")
rep("Reduced-form quintile slopes under the tourism shifter: effects are concentrated in low-income, low-connectivity quintiles.",
    "Reduced-form quintile slopes under the tourism shifter (heteroskedasticity-robust 95 percent confidence intervals): effects are concentrated in low-income, low-connectivity quintiles.")

# ------------------------------------------------------------------ 6. land-neighbour count
n_no = 39
for old in ["an indicator for countries with no neighbour under the definition (31 countries have no land neighbour)",
            "land contiguity from\nNatural Earth administrative boundaries (31 sample countries have no land\nneighbour and receive a zero exposure with an indicator)"]:
    if old in s: rep(old, old.replace("31", str(n_no)))
assert "31 countries have no land" not in s and "31 sample countries" not in s

# ------------------------------------------------------------------ 7. attribution denominator (world 838 Mt)
att = pd.read_csv(os.path.join(HERE, "_attribution_sensitivity.csv")); W = 838.0
a, b = table_by_label(s, "tab:attr_sens"); t = s[a:b]
for _, r in att.iterrows():
    old = f"& {r.attributed_mt:.1f} & {r.share_pct:.1f} \\\\"
    assert t.count(old) == 1, old
    t = t.replace(old, f"& {r.attributed_mt:.1f} & {100 * r.attributed_mt / W:.1f} \\\\")
t = t.replace("World 2023 emissions in the 184-country sample: 832 Mt.", "Shares are of world 2023 aviation CO$_2$ (838 Mt; the 184-country sample holds 832 Mt).")
s = s[:a] + t + s[b:]
lo = 100 * att.attributed_mt.drop(0).min() / W; hi = 100 * att.attributed_mt.drop(0).max() / W
rep("totals between 294 and 353 Mt, or 35 to 43 percent of 2023 emissions,", f"totals between 294 and 353 Mt, or {lo:.0f} to {hi:.0f} percent of 2023 emissions,")
rep("the 35--43 percent attribution range", f"the {lo:.0f}--{hi:.0f} percent attribution range")

# ------------------------------------------------------------------ 8. wording / logic
rep("The primary instrument survives (heteroskedasticity-robust $F$ declines\nonly from 120.1 to 105.8);",
    "The primary instrument survives (on the 4,121-observation sample of the\nstress test, the heteroskedasticity-robust $F$ declines only from 120.1 to\n105.8);")
rep("under it, total emissions do not respond, but\ninternational emissions rise by 3.16 percent and emissions per seat-km by\n1.23 percent (Methods).",
    "under it, total emissions do not respond, while\ninternational emissions rise by 3.16 percent ($p$ = 0.05) and emissions per\nseat-km by 1.23 percent ($p$ = 0.07) (Methods).")
rep("bunker-attributed share of world emissions exceeds the physical\nlanding-and-take-off share by up to 1.4 percentage points in countries\nwith large international hubs and falls short by up to 3.5 points in\ncountries with large domestically oriented networks, a gap that is\npositive at every international mega-hub and negative at large domestic\nhubs (Extended Data Figs.~\\ref{fig:levels} and \\ref{fig:mismatch}).",
    "bunker-attributed share of world emissions exceeds the physical\nlanding-and-take-off share by up to 1.4 percentage points where average\nstage lengths are long, at the Gulf hubs and in the United States, and\nfalls short by up to 3.5 points where networks are dominated by\nshort-haul domestic flying, most of all in China (Extended Data\nFigs.~\\ref{fig:levels} and \\ref{fig:mismatch}).")
rep("Positive values indicate international hub countries; negative values indicate domestically oriented networks.",
    "Positive values indicate long-haul, cruise-heavy networks; negative values indicate short-haul, domestically oriented networks.")
rep("tercile has no first stage ($F = 0.2$), a fact we use below as a\ndiagnostic.", "tercile has no first stage ($F = 0.2$), a fact we use as a diagnostic of\nthe exclusion restriction (Methods).")
rep("Kleibergen-Paap $F$ = 18.4", "Kleibergen--Paap $F$ = 18.4")

open(TEX, "w", encoding="utf-8", newline="\n").write(s)
print("replacements:", nrep)
labels = set(re.findall(r"\\label\{([^}]+)\}", s)); refs = set(re.findall(r"\\ref\{([^}]+)\}", s))
print("dangling refs:", sorted(refs - labels), "| dup labels:", [l for l in labels if s.count("\\label{%s}" % l) > 1])
print("table balance", s.count("\\begin{table}"), s.count("\\end{table}"))
print("DONE_37")
