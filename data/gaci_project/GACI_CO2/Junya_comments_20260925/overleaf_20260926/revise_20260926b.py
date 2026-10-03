# -*- coding: utf-8 -*-
"""Second pass 2026-09-26: Junya's Overleaf comment (airport regressions out), 986/848 clause,
TODO cites, natbib citations in Methods, plausibly-exogenous sentence out, validation table to
Extended Data, Extended Data reordered by first citation, plain-style prose edits."""
import re, pathlib
D = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2\Junya_comments_20260925\overleaf_20260926")
P = D / "main_co2_nature_20260926.tex"
t = P.read_bytes().decode("utf-8")
log = []

def rep(old, new, label, count=1):
    global t
    n = t.count(old)
    assert n == count, f"{label}: found {n}, expected {count}\n{old[:120]}"
    t = t.replace(old, new)
    log.append(f"OK  {label}")

def whole_env(label, env="table"):
    i = t.index("\\label{" + label + "}")
    b = t.rfind("\\begin{" + env + "}", 0, i)
    e = t.index("\\end{" + env + "}", i) + len("\\end{" + env + "}")
    # swallow one trailing newline pair
    return t[b:e]

# ---------------------------------------------------------------- A. airport regressions out
s = t.index("\\subsection*{Airport-Level Analysis and Identification Challenges}")
e = t.index("\\subsection*{Mediation analysis}")
airport_block = t[s:e]
assert "Finally, we conduct a concentration analysis" in airport_block
t = t[:s] + t[e:]
log.append("OK  Methods airport subsection removed")

rep("total because the elasticity is applied to the same emissions base. \n",
    "total because the elasticity is applied to the same emissions base. We then rank airports by attributed emissions and compare the cumulative shares held by the top 1, 5, 10 and 25 percent of airports with their shares of actual 2023 emissions (Extended Data Table~\\ref{tab:airport_conc} and Extended Data Fig.~\\ref{fig:airportconc}).\n",
    "concentration sentence moved into Attribution")

old_res = """Within countries and years, a one percent increase in an airport's
connectivity is associated with 3.8 percent more CO$_2$ (Extended Data
Table~\\ref{tab:airport_het}; this estimate is descriptive, Methods). The
emissions the response generates are concentrated: the top five percent of
airports, some 192 nodes led by Dubai, Doha, Shanghai Pudong, Istanbul and
Incheon, hold 85 percent of the 346 Mt attributed across airports, against
78 percent of emissions themselves (Extended Data
Fig.~\\ref{fig:airportconc} and Extended Data
Table~\\ref{tab:airport_conc}). An instrument covering those nodes would
cover 85 percent of the connectivity-driven total."""
new_res = """Across airports, the emissions the response generates are more
concentrated than emissions themselves. The top five percent of airports,
some 192 nodes led by Dubai, Doha, Shanghai Pudong, Istanbul and Incheon,
hold 85 percent of the 346 Mt attributed across airports, against 78
percent of 2023 emissions (Extended Data Fig.~\\ref{fig:airportconc} and
Extended Data Table~\\ref{tab:airport_conc}). An instrument covering those
nodes would cover 85 percent of the connectivity-driven total."""
rep(old_res, new_res, "Results airport paragraph")

rep("Airport estimates are descriptive; the attribution", "The airport attribution is descriptive; the country attribution", "Discussion limitation wording")

blk = whole_env("tab:airport_het"); rep(blk + "\n\n", "", "ED Table airport_het removed")
blk = whole_env("tab:airport_iv"); rep(blk + "\n\n", "", "Supp Table airport_iv removed")

rep("""  Attributed (country b) & 45.9 & 84.6 & 94.2 & 99.3 & 0.945 \\\\
  Attributed (airport b) & 46.8 & 85.3 & 94.6 & 99.4 & 0.947 \\\\
  Attributed (hub/non-hub b) & 44.9 & 82.7 & 93.2 & 99.3 & 0.941 \\\\
""", """  Attributed to 1996--2023 connectivity growth & 45.9 & 84.6 & 94.2 & 99.3 & 0.945 \\\\
""", "ED Table airport_conc rows")
rep("with $\\beta$ from the country 2SLS (5.35), the airport within-country regression (3.76), or the hub-specific airport estimates (2.11 for the global top 5 percent by 1996 capacity, 4.08 otherwise).",
    "with $\\beta$ the country-level 2SLS elasticity (5.35).", "ED Table airport_conc note")

# ---------------------------------------------------------------- B. 986 vs 848
rep("1.8 times the 2023 level of 986~Mt, compared with",
    "1.8 times the 2023 level of 986~Mt (848~Mt of direct combustion emissions plus upstream fuel-supply emissions), compared with",
    "986/848 clause")

# ---------------------------------------------------------------- C. TODO cites
rep("Earlier work finds that connectivity yields its largest economic gains in low-income, remote and weakly connected economies [TODO cite: companion GACI paper]. Marginal economic benefits and carbon consequences may therefore be greatest in the same places.",
    "The economic gains from connectivity are also expected to be largest in weakly connected economies \\citep{lenaerts2021,zhang2020}, so marginal economic benefits and carbon consequences may be greatest in the same places.",
    "TODO cite companion paper")
rep("rather than the regional causal incidence of network expansion [TODO cite: ICAO CORSIA].",
    "rather than the regional causal incidence of network expansion \\citep{icao2018corsia}.", "TODO cite CORSIA")

# ---------------------------------------------------------------- D. natbib citations in Methods
rep("Guidebook (EEA, 2023)", "Guidebook \\citep{eea2023}", "cite EEA")
rep("following Avogadro and Redondi (2024)", "following \\citet{avogadro2024}", "cite Avogadro")
rep("(IATA, 2018, 2019, 2024; Clarke et al., 2022)", "\\citep{iata2018,iata2019,iata2024,clarke2022}", "cite IATA/OECD")
rep("Quadros et al. (2022) report", "\\citet{quadros2022} report", "cite Quadros")
rep("following Cheung et al. (2020)", "following \\citet{cheung2020}", "cite Cheung", count=2)
rep("proposed by Imai, Keele, and Yamamoto (2010)", "proposed by \\citet{imai2010}", "cite Imai Methods")
rep("implements the algorithm of Imai, Keele and Yamamoto (2010)", "implements the algorithm of \\citet{imai2010}", "cite Imai table note")
rep("Following Kelejian and Prucha's generalized spatial two-stage least squares (GS2SLS) approach,",
    "Following the generalised spatial two-stage least squares (GS2SLS) approach of \\citet{kelejian1998},", "cite Kelejian-Prucha")

# ---------------------------------------------------------------- E. plausibly-exogenous sentence out
rep("Furthermore, plausibly-exogenous bounds indicate that a direct effect of the instrument would need to account for 85 percent of the reduced form (42 percent for intensity) to overturn our baseline results.\n",
    "", "plausibly-exogenous sentence removed")

# ---------------------------------------------------------------- F. validation table -> Extended Data (booktabs)
old_tab = whole_env("tab:validation_benchmarks")
rep(old_tab + "\n\n", "", "validation table cut from Methods")
rep("(Table~\\ref{tab:validation_benchmarks})", "(Extended Data Table~\\ref{tab:validation_benchmarks})", "validation ref")
new_tab = r"""\begin{table}[H]
\centering
\resizebox{\ifdim\width>\textwidth \textwidth\else\width\fi}{!}{%
\begin{threeparttable}
\caption{External validation of the flight-level emissions inventory}
\label{tab:validation_benchmarks}
\footnotesize
\begin{tabular}{lllcc}
\toprule
Benchmark & Comparison & Period & WAPE & Aggregate bias \\
\midrule
  IATA & Global CO$_2$ emissions & 2004--2023 & 3.04\% & $-$1.98\% \\
  OECD & Global CO$_2$ emissions & 2013--2023 & 3.58\% & $+$3.40\% \\
  BTS & U.S. carrier fuel consumption & 1996--2023 & 3.84\% & $+$0.76\% \\
\bottomrule
\end{tabular}
\begin{tablenotes}[flushleft]
\footnotesize
\item Notes: WAPE is $\sum_t |\widehat{E}_t-E_t^B|/\sum_t E_t^B$ and aggregate bias is $\sum_t(\widehat{E}_t-E_t^B)/\sum_t E_t^B$, where $\widehat{E}_t$ is our estimate and $E_t^B$ the benchmark; positive bias means our estimate exceeds the benchmark. Benchmarks: IATA industry statistics \citep{iata2018,iata2019,iata2024}, the OECD flight-level inventory \citep{clarke2022} and carrier-reported fuel consumption from the U.S. Bureau of Transportation Statistics (Methods).
\end{tablenotes}
\end{threeparttable}}
\end{table}"""

# ---------------------------------------------------------------- H. prose edits
rep("By\nregion it ranges from 5.1 in Asia--Pacific and 4.5 in Africa to 2.9 in\nLatin America and zero in Europe.",
    "By\nregion it is 5.1 in Asia--Pacific and 4.5 in Africa, and not\ndistinguishable from zero in Europe and Latin America.", "region sentence")
rep("We empirically validate the exclusion restriction using three direct tests, all of which pass (",
    "Three direct tests are consistent with the exclusion restriction (", "exclusion tests wording")
rep("firmly rejecting a general development channel", "rejecting a general development channel", "firmly")
rep("while the air term retains a strong 0.82", "while the air term retains 0.82", "strong")
rep("is negligible at 0.09 (s.e.\\ 0.19), contrasting sharply with 1.97 and 0.41 in the lower terciles.",
    "is 0.09 (s.e.\\ 0.19), against 1.97 and 0.41 in the lower terciles.", "sharply")
rep("\\subsection*{Spatial Econometric Specifications and Spillover Effects}",
    "\\subsection*{Spatial econometric specifications and spillover effects}", "spatial heading case")
rep("\\subsection*{Decomposition of the emissions}", "\\subsection*{Decomposition of the emissions elasticity}", "decomp heading")
n = t.count("neighbor"); t = t.replace("neighbor", "neighbour"); log.append(f"OK  neighbor->neighbour ({n})")
n = t.count("utilizing"); t = t.replace("utilizing", "using"); log.append(f"OK  utilizing->using ({n})")
rep("\\caption{Temporal split of the connectivity elasticity. Within each outcome",
    "\\caption{\\textbf{Temporal split of the connectivity elasticity.} Within each outcome", "fig temporal bold lead")
rep("\\caption{Spatial profile of the spillover. A,", "\\caption{\\textbf{Spatial profile of the spillover.} A,", "fig spilldecay bold lead")
rep("\\caption{Permutation placebo for the spillover. Distributions", "\\caption{\\textbf{Permutation placebo for the spillover.} Distributions", "fig spillplacebo bold lead")
rep("\\caption{Reduced forms of the Feyrer instrument on aviation CO$_2$ (blue) and on non-aviation emission series (grey)",
    "\\caption{\\textbf{Placebo reduced forms on non-aviation emissions.} Reduced forms of the Feyrer instrument on aviation CO$_2$ (blue) and on non-aviation emission series (grey)", "fig placeborf bold lead")

# ---------------------------------------------------------------- G. reorder Extended Data by first citation
ed_hdr_end = t.index("\\renewcommand{\\figurename}{Extended Data Fig.}\n") + len("\\renewcommand{\\figurename}{Extended Data Fig.}\n")
ed_end = t.index("\\clearpage\n\\section*{Supplementary Note 1")
ed_seg = t[ed_hdr_end:ed_end]
blocks = re.findall(r"\\begin\{(table|figure)\}\[H\].*?\\end\{\1\}", ed_seg, flags=re.S)
blocks = [m.group(0) for m in re.finditer(r"\\begin\{(table|figure)\}\[H\].*?\\end\{\1\}", ed_seg, flags=re.S)]
blocks.append(new_tab)
bylabel = {}
for b in blocks:
    lab = re.search(r"\\label\{([^}]+)\}", b).group(1)
    bylabel[lab] = b
body = t[:ed_hdr_end]
first = {}
for m in re.finditer(r"\\ref\{((?:tab|fig):[^}]+)\}", body):
    first.setdefault(m.group(1), m.start())
cited = [l for l, _ in sorted(first.items(), key=lambda x: x[1]) if l in bylabel]
assert set(cited) == set(bylabel), (set(bylabel) - set(cited))
tabs = [l for l in cited if l.startswith("tab:")]
figs = [l for l in cited if l.startswith("fig:")]
new_seg = "\n" + "\n\n".join(bylabel[l] for l in tabs + figs) + "\n\n"
t = t[:ed_hdr_end] + new_seg + t[ed_end:]
log.append("OK  ED reordered: tables " + ", ".join(x[4:] for x in tabs))
log.append("OK  ED reordered: figures " + ", ".join(x[4:] for x in figs))

# ---------------------------------------------------------------- I. header comment
rep("% main_co2_nature_20260908.tex  (candidate, 2026-09-08)\n",
    "% main_co2_nature_20260926.tex  (2026-09-26: Junya Estimation comments applied; airport regressions removed per\n%   Junya's Overleaf comment; validation table moved to Extended Data; Extended Data ordered by first citation)\n% --- history ---\n% main_co2_nature_20260908.tex  (candidate, 2026-09-08)\n", "header comment")

P.write_bytes(t.encode("utf-8"))
print("\n".join(log))

# ---------------------------------------------------------------- bib additions
B = D / "refs_co2.bib"
bib = B.read_text(encoding="utf-8")
add = r"""
@article{cheung2020,
  author  = {Cheung, Tommy K. Y. and Wong, Collin W. H. and Zhang, Anming},
  title   = {The evolution of aviation network: Global airport connectivity index 2006--2016},
  journal = {Transportation Research Part E: Logistics and Transportation Review},
  volume  = {133},
  pages   = {101826},
  year    = {2020},
  doi     = {10.1016/j.tre.2019.101826}
}
@article{imai2010,
  author  = {Imai, Kosuke and Keele, Luke and Yamamoto, Teppei},
  title   = {Identification, inference and sensitivity analysis for causal mediation effects},
  journal = {Statistical Science},
  volume  = {25},
  number  = {1},
  pages   = {51--71},
  year    = {2010},
  doi     = {10.1214/10-STS321}
}
@article{kelejian1998,
  author  = {Kelejian, Harry H. and Prucha, Ingmar R.},
  title   = {A generalized spatial two-stage least squares procedure for estimating a spatial autoregressive model with autoregressive disturbances},
  journal = {The Journal of Real Estate Finance and Economics},
  volume  = {17},
  number  = {1},
  pages   = {99--121},
  year    = {1998},
  doi     = {10.1023/A:1007707430416}
}
@article{quadros2022,
  author  = {Quadros, Fl{\'a}vio D. A. and Snellen, Mirjam and Sun, Junzi and Dedoussi, Irene C.},
  title   = {Global civil aviation emissions estimates for 2017--2020 using {ADS-B} data},
  journal = {Journal of Aircraft},
  volume  = {59},
  number  = {6},
  pages   = {1394--1405},
  year    = {2022},
  doi     = {10.2514/1.C036763}
}
@article{avogadro2024,
  author  = {Avogadro, Nicol{\`o} and Redondi, Renato},
  title   = {Pathways toward sustainable aviation: Analyzing emissions from air operations in {Europe} to support policy initiatives},
  journal = {Transportation Research Part A: Policy and Practice},
  volume  = {186},
  pages   = {104121},
  year    = {2024},
  doi     = {10.1016/j.tra.2024.104121}
}
@techreport{clarke2022,
  author      = {Clarke, Daniel and Flachenecker, Florian and Guidetti, Emmanuelle and Pionnier, Pierre-Alain},
  title       = {{CO$_2$} emissions from air transport: A near-real-time global database for policy analysis},
  institution = {Organisation for Economic Co-operation and Development},
  type        = {OECD Statistics Working Papers},
  number      = {2022/04},
  address     = {Paris},
  year        = {2022},
  doi         = {10.1787/ecc9f16b-en}
}
@techreport{eea2023,
  author      = {{European Environment Agency}},
  title       = {{EMEP/EEA} air pollutant emission inventory guidebook 2023},
  institution = {European Environment Agency},
  type        = {EEA Report},
  number      = {06/2023},
  address     = {Copenhagen},
  year        = {2023}
}
@misc{iata2018,
  author       = {{International Air Transport Association}},
  title        = {Industry statistics fact sheet, December 2018},
  howpublished = {IATA Economics, Montr{\'e}al},
  year         = {2018}
}
@misc{iata2019,
  author       = {{International Air Transport Association}},
  title        = {Industry statistics fact sheet, December 2019},
  howpublished = {IATA Economics, Montr{\'e}al},
  year         = {2019}
}
@misc{iata2024,
  author       = {{International Air Transport Association}},
  title        = {Industry statistics fact sheet, December 2024},
  howpublished = {IATA Economics, Montr{\'e}al},
  year         = {2024}
}
@techreport{icao2018corsia,
  author      = {{International Civil Aviation Organization}},
  title       = {Annex 16 to the {Convention on International Civil Aviation}, Environmental Protection, Volume {IV}: Carbon Offsetting and Reduction Scheme for International Aviation ({CORSIA})},
  institution = {International Civil Aviation Organization},
  address     = {Montr{\'e}al},
  edition     = {First},
  year        = {2018}
}
"""
for k in ["cheung2020", "imai2010", "kelejian1998", "quadros2022", "avogadro2024", "clarke2022", "eea2023", "iata2018", "iata2019", "iata2024", "icao2018corsia"]:
    assert "@" in add and ("{" + k + ",") in add
if "cheung2020" not in bib:
    bib = bib.rstrip("\n") + "\n" + add
    B.write_text(bib, encoding="utf-8", newline="\n")
    print("bib: 11 entries appended")
