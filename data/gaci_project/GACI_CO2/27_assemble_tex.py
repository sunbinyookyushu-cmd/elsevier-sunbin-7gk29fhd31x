# -*- coding: utf-8 -*-
"""
27_assemble_tex.py   (2026-09-03)
Assemble main_co2_nature_20260903.tex from the template and the generated table
fragments; reuse Table 1 (tab:main), tab:scc, tab:temporal and tab:mediation from
the 08-26 canonical tex verbatim. Copies figures into co2_overleaf_20260903/.
"""
import os, re, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "co2_overleaf_20260826", "main_co2_nature_20260826.tex")
OUTDIR = os.path.join(HERE, "co2_overleaf_20260903")
os.makedirs(OUTDIR, exist_ok=True)
old = open(OLD, encoding="utf-8").read()
TPL = "main_co2_nature_20260903" + os.environ.get("CLSUF", "") + "_template.tex"
tpl = open(os.path.join(HERE, TPL), encoding="utf-8").read()
BS = chr(92)

def table_by_label(src, label):
    i = src.find(BS + "label{%s}" % label)
    assert i >= 0, label
    s = src.rfind(BS + "begin{table}", 0, i)
    e = src.find(BS + "end{table}", i) + len(BS + "end{table}")
    return src[s:e]
def fragment(fn, label):
    src = open(os.path.join(HERE, fn), encoding="utf-8").read()
    return table_by_label(src, label)

SUF = os.environ.get("CLSUF", "")  # "_cl": country-clustered fragments (_tex_*_cl.tex, _tex_main_cl.tex)
if SUF:
    OUTDIR = os.path.join(HERE, "co2_overleaf_20260903" + SUF)
    os.makedirs(OUTDIR, exist_ok=True)
    main_src = {"tab:main": fragment("_tex_main" + SUF + ".tex", "tab:main"),
                "tab:temporal": fragment("_tex_main" + SUF + ".tex", "tab:temporal"),
                "tab:mediation": fragment("_tex_main" + SUF + ".tex", "tab:mediation")}
else:
    main_src = {"tab:main": table_by_label(old, "tab:main"), "tab:temporal": table_by_label(old, "tab:temporal"), "tab:mediation": table_by_label(old, "tab:mediation")}
subs = {
    "%%TAB_MAIN%%": main_src["tab:main"],
    "%%TAB_SCC%%": table_by_label(old, "tab:scc"),
    "%%TAB_TEMPORAL%%": main_src["tab:temporal"],
    "%%TAB_MEDIATION%%": main_src["tab:mediation"],
    "%%TAB_DECOMP%%": fragment("_tex_decomp" + SUF + ".tex", "tab:decomp"),
    "%%TAB_DECOMP_HETERO%%": fragment("_tex_decomp" + SUF + ".tex", "tab:decomp_hetero"),
    "%%TAB_HETERO%%": fragment("_tex_hetero_tot" + SUF + ".tex", "tab:hetero"),
    "%%TAB_SPILL%%": fragment("_tex_spill" + SUF + ".tex", "tab:spillover"),
    "%%TAB_SPILL_EXT%%": fragment("_tex_spill" + SUF + ".tex", "tab:spill_ext"),
    "%%TAB_AIRPORT_CONC%%": fragment("_tex_airport_conc.tex", "tab:airport_conc"),
    "%%TAB_AIRPORT_HET%%": fragment("_tex_airport.tex", "tab:airport_het"),
    "%%TAB_AIRPORT_IV%%": fragment("_tex_airport.tex", "tab:airport_iv"),
    "%%TAB_EXCL%%": fragment("_tex_exclusion" + SUF + ".tex", "tab:exclusion"),
    "%%TAB_EXCL2%%": fragment("_tex_exclusion" + SUF + ".tex", "tab:exclusion2"),
    "%%TAB_FUNCFORM%%": fragment("_tex_yifu" + SUF + ".tex", "tab:funcform"),
    "%%TAB_GRADIENT%%": fragment("_tex_yifu" + SUF + ".tex", "tab:gradient"),
    "%%TAB_ATTR_SENS%%": fragment("_tex_yifu" + SUF + ".tex", "tab:attr_sens"),
    "%%TAB_ACCIDENT%%": fragment("_tex_yifu" + SUF + ".tex", "tab:accident_iv"),
}
out = tpl
for k, v in subs.items():
    assert k in out, k
    out = out.replace(k, v)
ren = [("Extended Data Table: Decomposition of the CO$_2$ elasticity by group and segment", "Extended Data Table 4: Decomposition of the CO$_2$ elasticity by group and segment"),
       ("Extended Data Table: Airport-level elasticities within countries, by airport group", "Extended Data Table 5: Airport-level elasticities within countries, by airport group"),
       ("Extended Data Table: Spatial structure of the connectivity spillover", "Extended Data Table 6: Spatial structure of the connectivity spillover"),
       ("Extended Data Table: Exclusion-restriction diagnostics for the Feyrer instrument", "Extended Data Table 7: Exclusion-restriction diagnostics for the Feyrer instrument"),
       ("Supplementary Table: Alternative instrument constructions", "Supplementary Table 1: Alternative instrument constructions"),
       ("Supplementary Table: Airport-level identification pilot", "Supplementary Table 2: Airport-level identification pilot"),
       ("Extended Data Table: Functional form of the connectivity--emissions relationship", "Extended Data Table 8: Functional form of the connectivity--emissions relationship"),
       ("Extended Data Table: The elasticity along the baseline-connectivity distribution", "Extended Data Table 9: The elasticity along the baseline-connectivity distribution"),
       ("Extended Data Table: Sensitivity of the 2023 attribution to heterogeneous elasticities", "Extended Data Table 10: Sensitivity of the 2023 attribution to heterogeneous elasticities"),
       ("Supplementary Table: Aviation-accident instrument", "Supplementary Table 3: Aviation-accident instrument")]
for a, b in ren:
    out = out.replace(a, b)
left = re.findall(r"%%TAB_[A-Z_]+%%", out)
assert not left, left
labels = re.findall(BS + BS + r"label\{([^}]+)\}", out)
refs = set(re.findall(BS + BS + r"ref\{([^}]+)\}", out))
missing = sorted(r for r in refs if r not in labels)
dups = sorted(set(l for l in labels if labels.count(l) > 1))
print("labels", len(labels), "| missing refs:", missing, "| duplicate labels:", dups)
body = re.sub(r"%.*", "", out)
print("em-dash count:", body.count(chr(8212)), "| emph in body:", len(re.findall(BS + BS + r"emph\{", body)))
figs = sorted(set(re.findall(BS + BS + r"includegraphics\[[^\]]*\]\{([^}]+)\}", out)))
outtex = os.path.join(OUTDIR, "main_co2_nature_20260903.tex")
open(outtex, "w", encoding="utf-8").write(out)
missfig = []
for f in figs:
    src = os.path.join(HERE, f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(OUTDIR, f))
    else:
        missfig.append(f)
print("figures copied:", len(figs) - len(missfig), "| missing:", missfig)
pre = body.split(BS + "section*{Methods}")[0]
pre = re.sub(BS + BS + r"begin\{table\}.*?" + BS + BS + r"end\{table\}", " ", pre, flags=re.S)
pre = re.sub(BS + BS + r"begin\{figure\}.*?" + BS + BS + r"end\{figure\}", " ", pre, flags=re.S)
pre = re.sub(BS + BS + r"[a-zA-Z]+\*?", " ", pre)
print("approx words before Methods (excl. displays):", len(pre.split()))
print("wrote", outtex)
