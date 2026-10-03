# -*- coding: utf-8 -*-
"""Generate appendix tables for the GACI-inequality paper from the result CSVs."""
import csv, io, os, collections

BS = chr(92)
SRC = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
OUTDIR = os.path.join(SRC, "tables_appendix")
os.makedirs(OUTDIR, exist_ok=True)


def load(name):
    return list(csv.DictReader(io.open(os.path.join(SRC, name), encoding="utf-8-sig")))


def f(x, d=3):
    if x is None or x == "" or x == ".":
        return ""
    return ("%." + str(d) + "f") % float(x)


def stars(p):
    if p in (None, "", "."):
        return ""
    p = float(p)
    if p < 0.01:
        return BS + "sym{***}"
    if p < 0.05:
        return BS + "sym{**}"
    if p < 0.10:
        return BS + "sym{*}"
    return ""


def cell(b, se, p, d=3, brack=False):
    """coefficient with stars and (SE) or [SE]."""
    if b in (None, "", "."):
        return ""
    o, c = ("[", "]") if brack else ("(", ")")
    s = f(b, d) + stars(p)
    if se not in (None, "", "."):
        s += " " + o + f(se, d) + c
    return s


def write(name, txt):
    with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt.rstrip() + "\n")
    print("  wrote", name)


TREAT_LAB = {"ln_gaci_max": r"Hub connectivity, $\ln\mathrm{GACI}_{max}$",
             "ln_gaci_cwm": r"Hub quality, $\ln\mathrm{GACI}_{cwm}$",
             "ln_gaci_sum": r"Total connectivity, $\ln\mathrm{GACI}_{sum}$"}
TREAT_ORDER = ["ln_gaci_max", "ln_gaci_cwm", "ln_gaci_sum"]

# =====================================================================
# A.1  Gini in points (levels)  +  A.2 absolute redistribution
# =====================================================================
main = load("_main_results.csv")
idx = {(r["iv"], r["treat"], r["outcome"], r["model"]): r for r in main}

rows = [r"\begin{tabular}{lcc}", r"\toprule",
        r" & Market Gini & Disposable Gini " + BS + BS,
        r" & (points) & (points) " + BS + BS, r"\midrule"]
for i, t in enumerate(TREAT_ORDER):
    rows.append(r"\multicolumn{3}{l}{\emph{Panel %s. %s}}%s" % ("ABC"[i], TREAT_LAB[t], BS + BS))
    r_ols_m = idx[("feyrer_int", t, "gini_mkt", "OLS")]
    r_ols_d = idx[("feyrer_int", t, "gini_disp", "OLS")]
    rows.append("OLS & %s & %s %s" % (cell(r_ols_m["b"], r_ols_m["se"], r_ols_m["p"]),
                                      cell(r_ols_d["b"], r_ols_d["se"], r_ols_d["p"]), BS + BS))
    for iv, lab in [("feyrer_int", "2SLS, Feyrer IV"), ("tourism_int", "2SLS, tourism IV")]:
        m, d = idx[(iv, t, "gini_mkt", "IV")], idx[(iv, t, "gini_disp", "IV")]
        mc, dc = idx[(iv, t, "gini_mkt", "IVcl")], idx[(iv, t, "gini_disp", "IVcl")]
        rows.append("%s & %s & %s %s" % (lab, cell(m["b"], m["se"], m["p"]),
                                         cell(d["b"], d["se"], d["p"]), BS + BS))
        rows.append(" & %s & %s %s" % (cell("", mc["se"], mc["p"]) or "[%s]%s" % (f(mc["se"]), stars(mc["p"])),
                                       "[%s]%s" % (f(dc["se"]), stars(dc["p"])), BS + BS))
    if i < 2:
        rows.append(r"\addlinespace")
rows += [r"\midrule", "Country, Year FE & Yes & Yes " + BS + BS,
         "Observations & 3,735 & 3,735 " + BS + BS,
         r"\bottomrule", r"\end{tabular}"]
write("tabA_levels.tex", "\n".join(rows))

# --- A.2 absolute redistribution
rows = [r"\begin{tabular}{lccc}", r"\toprule",
        r"Connectivity measure & OLS & 2SLS, Feyrer IV & 2SLS, tourism IV " + BS + BS,
        r"\midrule"]
for t in TREAT_ORDER:
    o = idx[("feyrer_int", t, "abs_red", "OLS")]
    fv, fc = idx[("feyrer_int", t, "abs_red", "IV")], idx[("feyrer_int", t, "abs_red", "IVcl")]
    tv, tc = idx[("tourism_int", t, "abs_red", "IV")], idx[("tourism_int", t, "abs_red", "IVcl")]
    rows.append("%s & %s & %s & %s %s" % (TREAT_LAB[t], cell(o["b"], o["se"], o["p"]),
                                          cell(fv["b"], fv["se"], fv["p"]),
                                          cell(tv["b"], tv["se"], tv["p"]), BS + BS))
    rows.append(" & & [%s]%s & [%s]%s %s" % (f(fc["se"]), stars(fc["p"]),
                                             f(tc["se"]), stars(tc["p"]), BS + BS))
rows += [r"\midrule", "Observations & 1,898 & 1,898 & 1,898 " + BS + BS,
         r"\bottomrule", r"\end{tabular}"]
write("tabA_absred.tex", "\n".join(rows))

# =====================================================================
# A.3  Distributional shares for hub quality and total connectivity
# =====================================================================
tails = load("_tails_results.csv")
OUT_LAB = [("ln_top10_wid", r"Top 10\% share (pretax)"),
           ("ln_top1_wid", r"Top 1\% share (pretax)"),
           ("ln_bot50_wid", r"Bottom 50\% share (pretax)"),
           ("ratio_t10_b50", r"ln(top 10\% / bottom 50\%)"),
           ("ln_gini_pre_wid", r"Gini, pretax (WID)"),
           ("ln_gini_post_wid", r"Gini, post-tax (WID)"),
           ("ln_top10_post_wid", r"Top 10\% share (post-tax)"),
           ("ln_bot50_post_wid", r"Bottom 50\% share (post-tax)"),
           ("top10_wid", r"Top 10\% share, levels"),
           ("top1_wid", r"Top 1\% share, levels"),
           ("bot50_wid", r"Bottom 50\% share, levels")]
ti = {(r["treat"], r["outcome"], r["model"]): r for r in tails if r["block"] == "tails"}
rows = [r"\begin{tabular}{lccc}", r"\toprule",
        r"Outcome & OLS & 2SLS (robust SE) & 2SLS (clustered SE) " + BS + BS, r"\midrule"]
for i, t in enumerate(["ln_gaci_cwm", "ln_gaci_sum"]):
    rows.append(r"\multicolumn{4}{l}{\emph{Panel %s. %s}}%s" % ("AB"[i], TREAT_LAB[t], BS + BS))
    for key, lab in OUT_LAB:
        o, v, c = ti.get((t, key, "OLS")), ti.get((t, key, "IV")), ti.get((t, key, "IVcl"))
        if not o:
            continue
        rows.append("%s & %s & %s & %s %s" % (lab, cell(o["b"], o["se"], o["p"]),
                                              cell(v["b"], v["se"], v["p"]),
                                              cell(c["b"], c["se"], c["p"]), BS + BS))
    kp = ti[(t, "ln_top10_wid", "IV")]["kpf"]
    rows.append(r"KP $F$ (2SLS) & & %s & %s" % (f(kp, 1), BS + BS))
    if i == 0:
        rows.append(r"\addlinespace")
rows += [r"\midrule", "Observations & 3,714 & 3,714 & 3,714 " + BS + BS,
         r"\bottomrule", r"\end{tabular}"]
write("tabA_tails_other.tex", "\n".join(rows))

# --- A.4 tails by baseline income tercile
t3 = [r for r in tails if r["block"] == "tails_inc3"]
t3i = {(r["outcome"], r["treat"]): r for r in t3}
TERMS = [("ln_gaci_max", "Low-income tercile (base)"),
         ("ln_gaci_max_mid", r"\quad Interaction: middle"),
         ("ln_gaci_max_high", r"\quad Interaction: high"),
         ("mid_total", "Middle tercile (total)"),
         ("high_total", "High tercile (total)")]
rows = [r"\begin{tabular}{lcc}", r"\toprule",
        r" & $\ln$ top 10\% share & $\ln$ bottom 50\% share " + BS + BS, r"\midrule"]
for term, lab in TERMS:
    a, b = t3i.get(("ln_top10_wid", term)), t3i.get(("ln_bot50_wid", term))
    rows.append("%s & %s & %s %s" % (lab, cell(a["b"], a["se"], a["p"]),
                                     cell(b["b"], b["se"], b["p"]), BS + BS))
rows += [r"\midrule",
         "KP $F$ & %s & %s %s" % (f(t3i[("ln_top10_wid", "ln_gaci_max")]["kpf"], 1),
                                  f(t3i[("ln_bot50_wid", "ln_gaci_max")]["kpf"], 1), BS + BS),
         "Observations & 3,714 & 3,714 " + BS + BS, r"\bottomrule", r"\end{tabular}"]
write("tabA_tails_inc3.tex", "\n".join(rows))

# =====================================================================
# A.5  separate 2SLS by baseline income tercile
# =====================================================================
het = load("_hetero_results.csv")
sp = {(r["treat"], r["outcome"], r["term"]): r for r in het if r["block"] == "inc3_split"}
QLAB = {"q1": "Low tercile", "q2": "Middle tercile", "q3": "High tercile"}
rows = [r"\begin{tabular}{lcccc}", r"\toprule",
        r"Baseline GDP per capita & $\ln G^{mkt}$ & $\ln G^{disp}$ & KP $F$ & N " + BS + BS,
        r"\midrule"]
for i, t in enumerate(["ln_gaci_max", "ln_gaci_cwm"]):
    rows.append(r"\multicolumn{5}{l}{\emph{Panel %s. %s}}%s" % ("AB"[i], TREAT_LAB[t], BS + BS))
    for q in ["q1", "q2", "q3"]:
        m, d = sp[(t, "ln_gini_mkt", q)], sp[(t, "ln_gini_disp", q)]
        rows.append("%s & %s & %s & %s & %s %s" % (
            QLAB[q], cell(m["b"], m["se"], m["p"]), cell(d["b"], d["se"], d["p"]),
            f(m["kpf"], 1), "{:,}".format(int(m["N"])), BS + BS))
    if i == 0:
        rows.append(r"\addlinespace")
rows += [r"\bottomrule", r"\end{tabular}"]
write("tabA_inc3_split.tex", "\n".join(rows))

# =====================================================================
# A.6  leads of connectivity
# =====================================================================
ld = load("_longdiff_results.csv")
lead = {(r["outcome"], r["spec"]): r for r in ld if r["block"] == "lead"}
lc = {(r["outcome"], r["spec"]): r for r in ld if r["block"] == "lead_cond"}
rows = [r"\begin{tabular}{lcccc}", r"\toprule",
        r"Specification & $\ln G^{mkt}$ & $\ln G^{disp}$ & KP $F$ & N " + BS + BS, r"\midrule",
        r"\multicolumn{5}{l}{\emph{Panel A. Connectivity led $k$ years (instrument led equally)}}" + BS + BS]
for k in range(1, 6):
    m, d = lead[("ln_gini_mkt", "f%d" % k)], lead[("ln_gini_disp", "f%d" % k)]
    rows.append("Lead %d & %s & %s & %s & %s %s" % (
        k, cell(m["b"], m["se"], m["p"]), cell(d["b"], d["se"], d["p"]),
        f(m["kpf"], 1), "{:,}".format(int(m["N"])), BS + BS))
rows.append(r"\addlinespace\multicolumn{5}{l}{\emph{Panel B. Current and three-year-ahead connectivity, jointly instrumented}}" + BS + BS)
for spec, lab in [("t_given_f3", "Current connectivity"), ("f3_given_t", "Connectivity led 3 years")]:
    m, d = lc[("ln_gini_mkt", spec)], lc[("ln_gini_disp", spec)]
    rows.append("%s & %s & %s & %s & %s %s" % (
        lab, cell(m["b"], m["se"], m["p"]), cell(d["b"], d["se"], d["p"]),
        f(m["kpf"], 2), "{:,}".format(int(m["N"])), BS + BS))
rows += [r"\bottomrule", r"\end{tabular}"]
write("tabA_leads.tex", "\n".join(rows))

# =====================================================================
# A.7  reduced form by continent
# =====================================================================
diag = load("_diag_results.csv")
rf = {(r["spec"], r["term"]): r for r in diag if r["block"] == "rf_cont"}
CONT = [("AF", "Africa"), ("AS", "Asia"), ("EU", "Europe"), ("LA", "Latin America"),
        ("ME", "Middle East"), ("NA", "North America"), ("SW", "Oceania")]
rows = [r"\begin{tabular}{lccc}", r"\toprule",
        r"Continent & Feyrer instrument & Tourism instrument & N " + BS + BS, r"\midrule"]
for code, lab in CONT:
    a, b = rf.get(("feyrer_int", code)), rf.get(("tourism_int", code))
    rows.append("%s & %s & %s & %s %s" % (lab, cell(a["b"], a["se"], a["p"], 4),
                                          cell(b["b"], b["se"], b["p"], 4),
                                          "{:,}".format(int(a["N"])), BS + BS))
rows += [r"\bottomrule", r"\end{tabular}"]
write("tabA_rf_cont.tex", "\n".join(rows))

# =====================================================================
# A.8  Open Skies event study (two tables)
# =====================================================================
os_r = load("_openskies_results.csv")
es = {(r["outcome"], r["term"]): r for r in os_r if r["block"] == "es"}
EV = ["ev_m6", "ev_m5", "ev_m4", "ev_m3", "ev_m2"] + ["ev_p%d" % k for k in range(0, 11)]


def evlab(t):
    return ("$-%s$" % t[4:]) if t.startswith("ev_m") else t[4:]


def es_table(outs, header):
    rows = [r"\begin{tabular}{l" + "c" * len(outs) + "}", r"\toprule",
            "Event time & " + " & ".join(header) + " " + BS + BS, r"\midrule"]
    for t in EV:
        cells = []
        for o in outs:
            r = es.get((o, t))
            cells.append(cell(r["b"], r["se"], r["p"]) if r else "")
        rows.append("%s & %s %s" % (evlab(t), " & ".join(cells), BS + BS))
        if t == "ev_m2":
            rows.append(r"\addlinespace")
    rows += [r"\midrule",
             "Observations & " + " & ".join("{:,}".format(int(es[(o, "ev_p0")]["N"])) for o in outs) + " " + BS + BS,
             r"\bottomrule", r"\end{tabular}"]
    return "\n".join(rows)


write("tabA_es_conn.tex", es_table(["ln_gaci_max", "ln_gaci_cwm", "ln_gaci_sum"],
                                   [r"$\ln\mathrm{GACI}_{max}$", r"$\ln\mathrm{GACI}_{cwm}$", r"$\ln\mathrm{GACI}_{sum}$"]))
write("tabA_es_ineq.tex", es_table(["ln_gini_mkt", "ln_gini_disp", "ln_bot50_wid", "ln_top10_wid"],
                                   [r"$\ln G^{mkt}$", r"$\ln G^{disp}$", r"$\ln$ bottom 50\%", r"$\ln$ top 10\%"]))

# =====================================================================
# A.9  Open Skies + Feyrer over-identified 2SLS
# =====================================================================
ivf = {(r["outcome"], r["term"]): r for r in os_r if r["block"] == "iv_os_feyrer"}
OUT2 = [("ln_gini_mkt", r"$\ln G^{mkt}$"), ("ln_gini_disp", r"$\ln G^{disp}$"),
        ("ln_bot50_wid", r"$\ln$ bottom 50\% share"), ("ln_top10_wid", r"$\ln$ top 10\% share")]
rows = [r"\begin{tabular}{lccc}", r"\toprule",
        r"Outcome & $\ln\mathrm{GACI}_{max}$ & KP $F$ & Hansen $J$ $p$ " + BS + BS, r"\midrule"]
for k, lab in OUT2:
    b, h = ivf[(k, "ln_gaci_max")], ivf[(k, "hansen_p")]
    rows.append("%s & %s & %s & %s %s" % (lab, cell(b["b"], b["se"], b["p"]),
                                          f(b["kpf"], 1), f(h["b"], 2), BS + BS))
rows += [r"\midrule", "Observations & 3,389 / 3,368 & & " + BS + BS,
         r"\bottomrule", r"\end{tabular}"]
write("tabA_os_feyrer.tex", "\n".join(rows))

# =====================================================================
# A.10  country-level implied contribution (all 103)
# =====================================================================
cb = load("_contribution_bycountry.csv")
for r in cb:                      # "NA" (North America) was read as missing upstream
    if not r["cont"]:
        r["cont"] = "NA"
cb.sort(key=lambda r: -float(r["dln_gaci"]))
rows = [r"\begin{tabular}{llrrrrrr}", r"\toprule",
        r"Country & Cont. & Years & $\Delta\ln\mathrm{GACI}_{max}$ & Gini$_0$ & Gini$_1$ & Actual $\Delta$ & Implied $\Delta$ (OLS / 2SLS) " + BS + BS,
        r"\midrule"]
for r in cb:
    rows.append("%s & %s & %s--%s & %s & %s & %s & %s & %s / %s %s" % (
        r["c"], r["cont"], r["y0"], r["y1"], f(r["dln_gaci"], 3),
        f(r["gini0"], 1), f(r["gini1"], 1), f(r["actual_pts"], 2),
        f(r["ols_pts"], 2), f(r["iv_pts"], 2), BS + BS))
rows += [r"\bottomrule", r"\end{tabular}"]
write("tabA_country.tex", "\n".join(rows))

# =====================================================================
# A.11  COVID-19 connectivity shock by country (all 115, two columns)
# =====================================================================
cv = load("_covid_shock_bycountry.csv")
cv.sort(key=lambda r: float(r["dln"]))
half = (len(cv) + 1) // 2
left, right = cv[:half], cv[half:]
rows = [r"\begin{tabular}{lrrr@{\hskip 2em}lrrr}", r"\toprule",
        r"Country & 2019 & 2020 & $\Delta\ln$ & Country & 2019 & 2020 & $\Delta\ln$ " + BS + BS,
        r"\midrule"]
for i in range(half):
    a = left[i]
    b = right[i] if i < len(right) else None
    la = "%s & %s & %s & %s" % (a["c"], f(a["2019"], 2), f(a["2020"], 2), f(a["dln"], 3))
    lb = ("%s & %s & %s & %s" % (b["c"], f(b["2019"], 2), f(b["2020"], 2), f(b["dln"], 3))) if b else " & & & "
    rows.append(la + " & " + lb + " " + BS + BS)
rows += [r"\bottomrule", r"\end{tabular}"]
write("tabA_covid.tex", "\n".join(rows))

print("\nAppendix tables written to:", OUTDIR)
