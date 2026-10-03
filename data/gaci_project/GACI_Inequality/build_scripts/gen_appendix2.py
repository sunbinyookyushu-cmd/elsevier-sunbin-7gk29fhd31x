# -*- coding: utf-8 -*-
"""Second batch of appendix tables: the blocks the strict coverage check found missing."""
import csv, io, os

BS = chr(92)
SRC = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
OUTDIR = os.path.join(SRC, "tables_appendix")


def load(n):
    return list(csv.DictReader(io.open(os.path.join(SRC, n), encoding="utf-8-sig")))


def f(x, d=3):
    if x in (None, "", "."):
        return ""
    return ("%." + str(d) + "f") % float(x)


def stars(p):
    if p in (None, "", "."):
        return ""
    p = float(p)
    return BS + "sym{***}" if p < .01 else BS + "sym{**}" if p < .05 else BS + "sym{*}" if p < .10 else ""


def cell(b, se, p, d=3):
    if b in (None, "", "."):
        return ""
    s = f(b, d) + stars(p)
    if se not in (None, "", "."):
        s += " (" + f(se, d) + ")"
    return s


def write(name, txt):
    io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n").write(txt.rstrip() + "\n")
    print("  wrote", name)


EOL = " " + BS + BS

# =====================================================================
# survey-based World Bank outcomes (block altdv)
# =====================================================================
rob = load("_robust_results.csv")
alt = {(r["outcome"], r["spec"]): r for r in rob if r["block"] == "altdv"}
ROWS = [("gini_wb", "Gini (World Bank PIP, points)"),
        ("top10_wb", r"Top 10\% income share (points)"),
        ("bot20_wb", r"Bottom 20\% income share (points)")]
L = [BS + "begin{tabular}{lccc}", BS + "toprule",
     "Outcome & OLS & 2SLS, Feyrer IV & N" + EOL, BS + "midrule"]
for k, lab in ROWS:
    o, v = alt[(k, "OLS")], alt[(k, "IV")]
    L.append("%s & %s & %s & %s%s" % (lab, cell(o["b"], o["se"], o["p"]),
                                      cell(v["b"], v["se"], v["p"]),
                                      "{:,}".format(int(o["N"])), EOL))
L += [BS + "bottomrule", BS + "end{tabular}"]
write("tabA_altdv.tex", "\n".join(L))

# =====================================================================
# reduced form by quintile (blocks rfq_basegini, rfq_basepc) -- table for Figure 2
# =====================================================================
rfq = {(r["block"], r["spec"]): r for r in rob if r["block"].startswith("rfq")}
L = [BS + "begin{tabular}{lcc}", BS + "toprule",
     "Quintile & By baseline market Gini & By baseline GDP per capita" + EOL, BS + "midrule"]
for q in range(1, 6):
    a, b = rfq[("rfq_basegini", "q%d" % q)], rfq[("rfq_basepc", "q%d" % q)]
    L.append("Q%d & %s & %s%s" % (q, cell(a["b"], a["se"], a["p"], 4),
                                  cell(b["b"], b["se"], b["p"], 4), EOL))
L += [BS + "bottomrule", BS + "end{tabular}"]
write("tabA_rfq.tex", "\n".join(L))

# =====================================================================
# leave-one-continent-out under continent x year FE (block loo_contyear)
# and first stage by continent with standard errors (block fs_cont)
# =====================================================================
diag = load("_diag_results.csv")
loo = {(r["outcome"], r["term"]): r for r in diag if r["block"] == "loo_contyear"}
CONT = [("AF", "Africa"), ("AS", "Asia"), ("EU", "Europe"), ("LA", "Latin America"),
        ("ME", "Middle East"), ("NA", "North America"), ("SW", "Oceania")]
L = [BS + "begin{tabular}{lccc}", BS + "toprule",
     r"Dropped continent & $\ln G^{mkt}$ & $\ln G^{disp}$ & KP $F$" + EOL, BS + "midrule"]
for code, lab in CONT:
    m, d = loo[("ln_gini_mkt", "drop_" + code)], loo[("ln_gini_disp", "drop_" + code)]
    L.append("%s & %s & %s & %s%s" % (lab, cell(m["b"], m["se"], m["p"]),
                                      cell(d["b"], d["se"], d["p"]), f(m["kpf"], 1), EOL))
L += [BS + "bottomrule", BS + "end{tabular}"]
write("tabA_loo_contyear.tex", "\n".join(L))

fs = {(r["spec"], r["term"]): r for r in diag if r["block"] == "fs_cont"}
L = [BS + "begin{tabular}{lcccc}", BS + "toprule",
     r"Continent & Feyrer instrument & KP $F$ & Tourism instrument & KP $F$" + EOL, BS + "midrule"]
for code, lab in CONT:
    a, b = fs.get(("feyrer_int", code)), fs.get(("tourism_int", code))
    if not a:
        continue
    L.append("%s & %s & %s & %s & %s%s" % (
        lab, cell(a["b"], a["se"], a["p"], 4), f(a["kpf"], 1),
        cell(b["b"], b["se"], b["p"], 4) if b else "", f(b["kpf"], 1) if b else "", EOL))
L += [BS + "bottomrule", BS + "end{tabular}"]
write("tabA_fs_cont.tex", "\n".join(L))

# =====================================================================
# continent-specific 2SLS, both connectivity measures, all seven continents
# =====================================================================
het = load("_hetero_results.csv")
con = {(r["treat"], r["outcome"], r["term"]): r for r in het if r["block"] == "continent"}
L = [BS + "begin{tabular}{lccc}", BS + "toprule",
     r"Continent & $\ln G^{mkt}$ & $\ln G^{disp}$ & KP $F$" + EOL, BS + "midrule"]
for i, t in enumerate(["ln_gaci_max", "ln_gaci_cwm"]):
    lab = r"Hub connectivity, $\ln\mathrm{GACI}_{max}$" if i == 0 else r"Hub quality, $\ln\mathrm{GACI}_{cwm}$"
    L.append(r"\multicolumn{4}{l}{\emph{Panel %s. %s}}%s" % ("AB"[i], lab, BS + BS))
    for code, cl in CONT:
        m, d = con.get((t, "ln_gini_mkt", code)), con.get((t, "ln_gini_disp", code))
        if not m:
            continue
        L.append("%s & %s & %s & %s%s" % (cl, cell(m["b"], m["se"], m["p"]),
                                          cell(d["b"], d["se"], d["p"]), f(m["kpf"], 1), EOL))
    if i == 0:
        L.append(BS + "addlinespace")
L += [BS + "bottomrule", BS + "end{tabular}"]
write("tabA_continent.tex", "\n".join(L))

# =====================================================================
# complete long-difference battery (all windows, all four estimators, stacked)
# =====================================================================
ld = load("_longdiff_results.csv")
li = {(r["block"], r["outcome"], r["spec"]): r for r in ld}
WIN = [("1996_2019", "1996--2019"), ("1996_2023", "1996--2023"), ("2000_2019", "2000--2019"),
       ("2005_2019", "2005--2019"), ("2010_2019", "2010--2019")]
EST = [("LD_OLS", "OLS"), ("LD_IV", "2SLS, Feyrer"), ("LD_IVtour", "2SLS, tourism"),
       ("LD_IVboth", "2SLS, both")]
L = [BS + "begin{tabular}{llccc}", BS + "toprule",
     r"Window & Estimator & $\ln G^{mkt}$ & $\ln G^{disp}$ & KP $F$" + EOL, BS + "midrule"]
for j, (ws, wl) in enumerate(WIN):
    for i, (blk, el) in enumerate(EST):
        m, d = li.get((blk, "ln_gini_mkt", ws)), li.get((blk, "ln_gini_disp", ws))
        if not m:
            continue
        L.append("%s & %s & %s & %s & %s%s" % (wl if i == 0 else "", el,
                                               cell(m["b"], m["se"], m["p"]),
                                               cell(d["b"], d["se"], d["p"]),
                                               f(m["kpf"], 2), EOL))
    if j < len(WIN) - 1:
        L.append(BS + "addlinespace")
L.append(r"\addlinespace\multicolumn{5}{l}{\emph{Stacked five-year differences}}" + BS + BS)
for blk, el in [("D5_OLS", "OLS"), ("D5_IV", "2SLS, Feyrer"), ("D5_IVtour", "2SLS, tourism")]:
    m, d = li.get((blk, "ln_gini_mkt", "stacked5")), li.get((blk, "ln_gini_disp", "stacked5"))
    if not m:
        continue
    L.append(" & %s & %s & %s & %s%s" % (el, cell(m["b"], m["se"], m["p"]),
                                         cell(d["b"], d["se"], d["p"]), f(m["kpf"], 2), EOL))
L += [BS + "bottomrule", BS + "end{tabular}"]
write("tabA_longdiff_full.tex", "\n".join(L))

print("\ndone ->", OUTDIR)
