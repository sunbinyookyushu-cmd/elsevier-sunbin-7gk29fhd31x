# -*- coding: utf-8 -*-
r"""
36_apply_comments_20260908.py   (2026-09-08)
Base = Downloads/main_co2_nature_20260906 (1).tex (user copy carrying the new
Chunan/Fangyu Methods). Applies:
  1. user comment: Table 1 intensity column removed (intensity is in Table 2)
  2. user comment: Extended Data Table 1 Panels D-E (unrestricted split) removed
  3. Main section replaced by Yifu's rewrite (Downloads/Main_YO_Sep7.docx),
     citations as natbib author-year \citep/\citet with refs_co2.bib
Output: FINAL_20260908/main_co2_nature_20260908.tex, co2_overleaf_20260908/ (+zip),
copies to Downloads.
"""
import os, re, shutil, zipfile, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, "FINAL_20260908")
SRC = os.path.join(FIN, "_orig_Downloads_main_co2_nature_20260906_1.tex")
OUT = os.path.join(FIN, "main_co2_nature_20260908.tex")
BS = chr(92)
s = open(SRC, encoding="utf-8").read().replace("\r\n", "\n")

def block(src, label, env="table"):
    i = src.find(BS + "label{%s}" % label); assert i >= 0, label
    a = src.rfind(BS + "begin{%s}" % env, 0, i); b = src.find(BS + "end{%s}" % env, i) + len(BS + "end{%s}" % env)
    return a, b

# ---------------------------------------------------------------- 1. Table 1: drop Intensity column
a, b = block(s, "tab:main"); t = s[a:b]
out = []
for l in t.split("\n"):
    if l.startswith(BS + "begin{tabular}{lcccc}"):
        l = BS + "begin{tabular}{lccc}"
    elif l.startswith(BS + "multicolumn{5}{l}"):
        l = l.replace(BS + "multicolumn{5}{l}", BS + "multicolumn{4}{l}")
    elif l.strip().endswith(BS + BS) and l.count("&") == 4 and not l.startswith(BS + "multicolumn"):
        l = l.rsplit("&", 1)[0].rstrip() + " " + BS + BS
    out.append(l)
t2 = "\n".join(out)
old = "scheduled departing seat-kilometres, and CO$_2$ per seat-km."
assert old in t2
t2 = t2.replace(old, "and scheduled departing seat-kilometres; the elasticity of CO$_2$ per seat-km is reported in Table~" + BS + "ref{tab:decomp}.")
assert "Intensity" not in t2 and "-0.399" not in t2 and "(0.297)" not in t2, "intensity column still present"
s = s[:a] + t2 + s[b:]
old = "efficiency term is imprecise once errors are clustered (s.e." + BS + " 0.30;\nTable~" + BS + "ref{tab:main}, column 4)."
assert old in s, "prose ref to column 4 not found"
s = s.replace(old, "efficiency term is imprecise once errors are clustered (s.e." + BS + " 0.30;\nTable~" + BS + "ref{tab:decomp}).")
cm = " <- BECAUSE THERE IS INTENSITY ALREADY, WE CAN DELETE TABLE 1 INTENSITY VALUE. "
assert cm in s
s = s.replace(cm, "")

# ---------------------------------------------------------------- 2. ED Table 1: drop Panels D-E
a, b = block(s, "tab:temporal"); t = s[a:b]
i = t.find(BS + "midrule\n" + BS + "multicolumn{5}{l}{" + BS + "textit{Panel D. Unrestricted split")
j = t.find(BS + "bottomrule", i); assert i > 0 and j > i
t2 = t[:i] + t[j:]
oldn = "Panels D and E report the unrestricted split for reference; the weak first stage in Panel E (KP $F$ = 3.2) is driven by the COVID years, whose exclusion in Panel C restores $F$ to 10.7."
assert oldn in t2
t2 = t2.replace(oldn, "The unrestricted 2010--2023 split (not shown) has a weak first stage (KP $F$ = 3.2), driven by the COVID years, whose exclusion in Panel C restores $F$ to 10.7; its estimates appear in grey in Extended Data Fig.~" + BS + "ref{fig:temporal}.")
assert "<<D, E DELETE" not in t2 and "Panel E" not in t2
s = s[:a] + t2 + s[b:]

# (09-08 revert: validation table left exactly as in the user's tex)

# ---------------------------------------------------------------- 4. Main section from Yifu (Main_YO_Sep7.docx)
MAIN = r"""%=======================================================================
\section*{Main}
%=======================================================================
Air connectivity has become an important part of economic and transport
policy. Governments expand airport capacity, support new routes and
negotiate air-service agreements to improve access to the global air
network \citep{fageda2018,piermartini2013}. A large body of literature
links better connectivity to trade, tourism, investment, and regional
development \citep{lenaerts2021,zhang2020}, making network expansion
particularly important for countries with limited global access. However,
the climate implications of air connectivity development are less clear.
Aviation remains difficult to decarbonize because large-scale
electrification is not expected in the near term, while continued growth
in air travel can offset gains from more efficient aircraft and
lower-carbon fuels \citep{bergero2023,sacchi2023}. As countries continue
to expand their air networks, a basic question emerges: what happens to
carbon emissions when air connectivity improves?

The answer depends on how connectivity changes aviation activity. On the
one hand, better connections can open new destinations and induce trips
that would otherwise not occur \citep{koo2017,piermartini2013}. On the
other hand, they can also change how those trips are served. Changes in
network structure can alter flight frequency, aircraft size, and routing,
with potentially offsetting effects on operating and environmental
efficiency \citep{brueckner2004,pels2021}. These changes can work in
opposite directions. More aviation activity raises total emissions, while
greater efficiency lowers the emissions associated with each unit of
travel. Evidence from other transport settings shows that induced demand
can offset some of the environmental gains from improved efficiency
\citep{hymel2010,ou2024}. The net carbon effect of connectivity is
therefore an empirical question. So is the source of that effect: whether
emissions change because airlines operate more flights, use different
aircraft, fly different distances, or provide transport more efficiently.

Existing research has not resolved this question. Studies of air
connectivity have focused mainly on its economic benefits, linking better
access to trade, tourism, productivity and regional development
\citep{lenaerts2021,zhang2020}, while research on aviation
decarbonization has focused on travel demand, aircraft and operational
efficiency, and lower-carbon fuels \citep{bergero2023,dray2022}. Much
less is known about how the development of the air network itself shapes
aviation activity and emissions. Estimating this effect is difficult
because causality can run in both directions. For example, while airlines
add routes and flights in response to growing demand, better connections
can also generate additional travel \citep{koo2017,pitfield2010}. Income,
trade, and tourism can further affect both network expansion and aviation
activity \citep{vandevijver2014}. These sources of endogeneity can bias
estimates based on observed changes in connectivity. Therefore,
identifying the average causal effect of connectivity requires variation
that is not driven by local travel demand. This gap in causal evidence on
the carbon effects of air connectivity motivates our study.

However, the average effect alone provides an incomplete picture of the
carbon consequences of air connectivity. First, the carbon effect may
change as air networks develop. New connections can generate substantial
new activity in countries with sparse networks, while the same increase in
connectivity may have a smaller effect once networks are well developed.
Therefore, the carbon effect of connectivity may depend on the stage of
network development. Second, the effects may extend beyond the country
where connectivity expands. Air transport operates as an international
network, so greater connectivity in one country can change aviation
activity in neighboring countries. Emissions associated with network
growth may also be concentrated in particular airports rather than spread
evenly across the network. These differences matter for understanding
when and where the carbon consequences of network expansion are greatest.

In this study, we address three questions. First, how does air
connectivity affect aviation CO$_2$, and through which changes in
aviation activity and efficiency? Second, how does the effect change as
air networks develop? Third, how are the carbon effects of connectivity
distributed across the air network, and do they extend across national
borders? We answer these questions using a global panel of air
connectivity and flight-stage-resolved CO$_2$ emissions from more than
6{,}000 airports between 1996 and 2023. To address endogeneity, we use a
shift-share instrumental-variable design based on countries'
predetermined exposure to global aviation expansion.

Our results reveal a large positive effect of air connectivity on
aviation CO$_2$, particularly during the ``take-off'' stages of network
development. Our main estimate indicates that a 1\% increase in
connectivity increases aviation CO$_2$ by about 5.7\%, driven primarily
by a roughly 7\% increase in flight frequency. Aircraft size, flight
distance, and carbon intensity decline slightly, but these changes are
not statistically significant. The effect on emissions is largest in
countries with lower initial income and connectivity and declines as
networks mature. The effects also extend across national borders, while
emissions associated with network growth are concentrated in a small
share of airports. These findings show that network expansion increases
aviation emissions mainly by generating additional flying, while
accompanying efficiency gains are too small to offset this growth.
Therefore, accounting for network-driven growth in aviation activity is
important for assessing pathways to aviation decarbonization.

"""
i = s.find("%=======================================================================\n" + BS + "section*{Main [Yifu]}")
j = s.find("%=======================================================================\n" + BS + "section*{Results [Sunbin]}")
assert 0 < i < j
old_main = s[i:j]
open(os.path.join(FIN, "_old_main_section_20260906.tex"), "w", encoding="utf-8").write(old_main)
s = s[:i] + MAIN + s[j:]

# natbib + bibliography
s = s.replace(BS + "usepackage{amsmath,graphicx,booktabs,threeparttable,float}",
              BS + "usepackage{amsmath,graphicx,booktabs,threeparttable,float}\n" + BS + "usepackage[authoryear,round]{natbib}")
assert BS + "bibliography{" not in s
s = s.replace(BS + "end{document}", BS + "bibliographystyle{apalike}\n" + BS + "bibliography{refs_co2}\n" + BS + "end{document}")

# ---------------------------------------------------------------- header + date
hdr_end = s.find(BS + "documentclass")
s = ("% main_co2_nature_20260908.tex  (candidate, 2026-09-08)\n"
     "% Built by 36_apply_comments_20260908.py from Downloads/main_co2_nature_20260906 (1).tex\n"
     "% (user copy with the new Chunan/Fangyu Methods: flight-level emissions, allocation,\n"
     "% validation incl. BTS 3.84%/+0.76%, GACI) with the 09-08 changes:\n"
     "%   - Main section replaced by Yifu's rewrite (Main_YO_Sep7.docx); natbib author-year,\n"
     "%     refs_co2.bib (14 entries); old Main kept in FINAL_20260908/_old_main_section_20260906.tex\n"
     "%   - Table 1: intensity column removed (reported in Table 2); prose reference updated\n"
     "%   - Extended Data Table 1: Panels D-E (unrestricted split) removed; note rewritten\n"
     "% Inference: standard errors clustered by country throughout (09-03 decision).\n"
     "% Main displays: Tables 1-4 (main, decomposition, spatial, SCC) and Figs 1-3\n"
     "% (heterogeneity, attributed map, SAF). Extended Data: tables 1-14, figures 1-12;\n"
     "% Supplementary tables 1-3. [TODO cite] markers remain outside Main; compile on Overleaf.\n") + s[hdr_end:]
s = s.replace(BS + "date{Nature-format draft, candidate of 6 September 2026}", BS + "date{Nature-format draft, candidate of 8 September 2026}")
open(OUT, "w", encoding="utf-8", newline="\n").write(s)

# ---------------------------------------------------------------- checks
labels = set(re.findall(r"\\label\{([^}]+)\}", s)); refs = set(re.findall(r"\\ref\{([^}]+)\}", s))
print("dangling refs:", sorted(refs - labels))
print("duplicate labels:", [l for l in labels if s.count("\\label{%s}" % l) > 1])
cites = set(k for grp in re.findall(r"\\cite[pt]?\{([^}]+)\}", s) for k in grp.split(","))
bibkeys = set(re.findall(r"@\w+\{([^,]+),", open(os.path.join(FIN, "refs_co2.bib"), encoding="utf-8").read()))
print("cite keys missing from bib:", sorted(cites - bibkeys), "| unused bib keys:", sorted(bibkeys - cites))
figs = sorted(set(re.findall(r"includegraphics\[[^\]]*\]\{([^}]+)\}", s)))
print("figures:", figs)
print("leftover comment markers:", [l[:80] for l in s.split("\n") if "<-" in l or "<<" in l])
print("table env balance", s.count("\\begin{table}"), s.count("\\end{table}"), "| TODO cite:", s.count("[TODO"))
print("lines", s.count("\n"), "| words approx", len(re.sub(r"\\[a-zA-Z]+|[{}$&%]", " ", s).split()))

# ---------------------------------------------------------------- overleaf folder + zip + copies
OV = os.path.join(FIN, "co2_overleaf_20260908"); os.makedirs(OV, exist_ok=True)
SRCFIG = os.path.join(HERE, "co2_overleaf_20260906")
missing = []
for f in figs:
    p = os.path.join(SRCFIG, f)
    if not os.path.exists(p): p = os.path.join(HERE, f)
    if os.path.exists(p): shutil.copy(p, os.path.join(OV, f))
    else: missing.append(f)
print("missing figure files:", missing)
shutil.copy(OUT, os.path.join(OV, os.path.basename(OUT)))
shutil.copy(os.path.join(FIN, "refs_co2.bib"), os.path.join(OV, "refs_co2.bib"))
zp = os.path.join(FIN, "co2_overleaf_20260908.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(OV)):
        z.write(os.path.join(OV, f), f)
print("zip:", zp, os.path.getsize(zp) // 1024, "KB;", len(os.listdir(OV)), "files")
DL = r"C:\Users\sunbi\Downloads"
shutil.copy(OUT, os.path.join(DL, os.path.basename(OUT)))
shutil.copy(os.path.join(FIN, "refs_co2.bib"), os.path.join(DL, "refs_co2.bib"))
shutil.copy(zp, os.path.join(DL, os.path.basename(zp)))
viz = os.path.join(HERE, "CO2_visualization_data_20260908.xlsx")
if os.path.exists(viz):
    shutil.copy(viz, os.path.join(FIN, os.path.basename(viz)))
print("copied tex/bib/zip to Downloads; DONE_36")
