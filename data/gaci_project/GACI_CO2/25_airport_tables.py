# -*- coding: utf-8 -*-
"""
25_airport_tables.py   (LZ comment 2, 2026-09-03)
From _airport_hetero.csv and _airport_feyrer.csv:
  - tab:airport_het  ED table: within-country airport elasticities by group, four outcomes
  - tab:airport_iv   SI table: airport-level Feyrer shifter pilot (fails the first stage)
Writes _tex_airport.tex
"""
import os, math
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
def star(p):
    return "$^{***}$" if p < .01 else ("$^{**}$" if p < .05 else ("$^{*}$" if p < .1 else ""))
def c(b, se, p, nd=2):
    return f"{b:.{nd}f}{star(p)} ({se:.{nd}f})"
h = pd.read_csv(os.path.join(HERE, "_airport_hetero.csv"))
def get(panel, grp, outc):
    r = h[(h.panel == panel) & (h.grp == grp) & (h.outc == outc)]
    return r.iloc[0] if len(r) else None
outs = ["ln_co2", "ln_skm", "ln_intensity", "intl_share_skm"]
heads = ["log CO$_2$", "log seat-km", "log CO$_2$/seat-km", "Intl.\\ share"]
blocks = [
    ("All airports", "ALL", [("all", "All")]),
    ("Panel A. Hub status (global rank by 1996 seat-km)", "HUB", [("top1", "Top 1 percent"), ("not_top1", "Others"), ("top5", "Top 5 percent"), ("not_top5", "Others")]),
    ("Panel B. Baseline connectivity tercile (1996 GACI)", "GAC", [("gac1", "Low"), ("gac2", "Middle"), ("gac3", "High")]),
    ("Panel C. Baseline traffic tercile (1996 seat-km)", "SKM", [("skm1", "Low"), ("skm2", "Middle"), ("skm3", "High")]),
    ("Panel D. Orientation (baseline international share of seat-km)", "ORI", [("domestic_only", "Domestic only"), ("mixed", "Below one half"), ("international", "Above one half")]),
    ("Panel E. Host-country income tercile", "INC", [("inc1", "Low"), ("inc2", "Middle"), ("inc3", "High")]),
    ("Panel F. Region", "REG", [("EU", "Europe"), ("AS", "Asia"), ("SW", "Oceania and South-West Pacific"), ("AF", "Africa"), ("LA", "Latin America"), ("ME", "Middle East"), ("NA", "North America")]),
    ("Panel G. Topology-only regressors (log eigenvector, closeness, betweenness, degree)", "TOPO", [("eig", "Eigenvector centrality"), ("close", "Closeness"), ("betw", "Betweenness"), ("deg", "Degree")]),
]
L = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}",
     r"\caption{Extended Data Table: Airport-level elasticities within countries, by airport group}", r"\label{tab:airport_het}", r"\scriptsize",
     r"\begin{tabular}{l" + "c" * 4 + r"cc}", r"\toprule", " & " + " & ".join(heads) + r" & Airport-years & Airports \\", r"\midrule"]
for title, panel, grps in blocks:
    L.append(r"\multicolumn{7}{l}{\textit{" + title + r"}} \\")
    for g, lbl in grps:
        cells = []
        r0 = None
        for o in outs:
            r = get(panel, g, o)
            if r is None:
                cells.append("--"); continue
            nd = 3 if (panel == "TOPO" and g in ("eig", "betw", "deg")) else 2
            cells.append(c(r.b, r.se, r.p, nd)); r0 = r if r0 is None else r0
        L.append(f"  {lbl} & " + " & ".join(cells) + (f" & {int(r0.nn):,} & {int(r0.nap):,} \\\\" if r0 is not None else r" & -- & -- \\"))
ih = h[(h.panel == "INT") & (h.grp == "hub_x_gaci") & (h.outc == "ln_co2")].iloc[0]
it = h[(h.panel == "INT") & (h.grp == "top5_x_gaci") & (h.outc == "ln_co2")].iloc[0]
L += [r"\midrule", r"\multicolumn{7}{l}{\textit{Pooled interaction on log CO$_2$}} \\",
      f"  Country's largest airport $\\times$ log GACI & {c(ih.b, ih.se, ih.p)} & & & & {int(ih.nn):,} & {int(ih.nap):,} \\\\",
      f"  Global top 5 percent $\\times$ log GACI & {c(it.b, it.se, it.p)} & & & & {int(it.nn):,} & {int(it.nap):,} \\\\",
      r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}\scriptsize",
      r"\item Each cell is the coefficient on log airport GACI (or on the topology component in Panel G) from a regression with airport and country-by-year fixed effects on the indicated subsample; standard errors clustered by airport. Country-by-year effects absorb every national shock, so the elasticities compare airports of the same country in the same year. The subsample of each country's largest airport is not separately estimable under country-by-year effects (one airport per country-year) and enters only through the interaction. Airport GACI embeds a capacity term; Panel G uses the topology-only components of the index. $^{***}$ $p<0.01$, $^{**}$ $p<0.05$, $^{*}$ $p<0.1$.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex1 = "\n".join(L)

f = pd.read_csv(os.path.join(HERE, "_airport_feyrer.csv"))
def gf(item, outc):
    r = f[(f.item == item) & (f.outc == outc)]; return r.iloc[0] if len(r) else None
S = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}",
     r"\caption{Supplementary Table: Airport-level identification pilot with an airport Feyrer shifter}", r"\label{tab:airport_iv}", r"\scriptsize",
     r"\begin{tabular}{lccc}", r"\toprule", r" & Coefficient & Partial / KP $F$ & $N$ \\", r"\midrule",
     r"\multicolumn{4}{l}{\textit{First stage: log airport GACI on $a_t \times$ log airport air market access 1996}} \\"]
for k, lbl in [("fs_baseline", "Baseline"), ("fs_plus_cap96", "\\quad plus $a_t \\times$ log 1996 seat-km"), ("fs_plus_both", "\\quad plus $a_t \\times$ log 1996 GACI")]:
    r = gf(k, "ln_gaci"); S.append(f"  {lbl} & {c(r.b, r.se, r.p, 3)} & {r.kpf:.1f} & {int(r.nn):,} \\\\")
S.append(r"\midrule"); S.append(r"\multicolumn{4}{l}{\textit{2SLS (baseline instrument)}} \\")
for o, lbl in zip(outs, ["log CO$_2$", "log seat-km", "log CO$_2$/seat-km", "International share"]):
    r = gf("iv_baseline", o); S.append(f"  {lbl} & {c(r.b, r.se, r.p)} & {r.kpf:.1f} & {int(r.nn):,} \\\\")
S += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}\scriptsize",
      r"\item Airport air market access is the population-weighted inverse distance from the airport to all foreign countries' aviation centroids in 1996 (own country excluded); $a_t$ is the world seat-capacity index of the country instrument. Airport and country-by-year fixed effects, standard errors clustered by airport. Within a country the shifter varies only through airports' relative location (mean within-country standard deviation of the log 1996 access term 0.04), and it has no first stage; the pilot is therefore not used and airport-level estimates are reported as within-country descriptive evidence.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
tex2 = "\n".join(S)
with open(os.path.join(HERE, "_tex_airport.tex"), "w", encoding="utf-8") as fh:
    fh.write("% ===== tab:airport_het =====\n" + tex1 + "\n\n% ===== tab:airport_iv =====\n" + tex2 + "\n")
print("wrote _tex_airport.tex")
print("DONE_25")
