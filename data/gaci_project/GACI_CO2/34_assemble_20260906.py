# -*- coding: utf-8 -*-
"""
34_assemble_20260906.py   (2026-09-06)
Candidate manuscript = 09-03 country-clustered template (5-layer prose)
  + coauthor edits from Downloads/main_co2_nature_20260826 (2).tex
      (JL: Discussion rewrite, heterogeneity paragraph softening;
       Chunan/Fangyu: Methods emissions / allocation / validation / GACI)
  + Junya: LTO and 50/50 CO2 columns moved to Extended Data (tab:alloc),
           spatial models SLX / SAR / SEM / SDM (+SDEM) added (tab:spatial),
           old spillover table moved to Extended Data
  + Ray/Lisa: SAF scenarios coupled to connectivity growth (31_saf_growth.py)
  + display selection: main = T1 main, T2 decomp, T3 spatial, T4 scc,
       F1 hetero, F2 airport concentration, F3 attributed map, F4 mismatch,
       F5 SAF; everything else Extended Data / Supplementary.
Output: co2_overleaf_20260906/main_co2_nature_20260906.tex (+ figures, zip)
"""
import os, re, shutil, sys, zipfile
import numpy as np
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
BS = chr(92)
OUTDIR = os.path.join(HERE, "co2_overleaf_20260906")
os.makedirs(OUTDIR, exist_ok=True)
TPL = open(os.path.join(HERE, "main_co2_nature_20260903_cl_template.tex"), encoding="utf-8").read()
CO = open(r"C:\Users\sunbi\Downloads\main_co2_nature_20260826 (2).tex", encoding="utf-8").read()
OLD = open(os.path.join(HERE, "co2_overleaf_20260826", "main_co2_nature_20260826.tex"), encoding="utf-8").read()
SP = pd.read_csv(os.path.join(HERE, "_spatial_models.csv"))

def table_by_label(src, label):
    i = src.find(BS + "label{%s}" % label); assert i >= 0, label
    s = src.rfind(BS + "begin{table}", 0, i)
    e = src.find(BS + "end{table}", i) + len(BS + "end{table}")
    return src[s:e]
def figure_by_label(src, label):
    i = src.find(BS + "label{%s}" % label); assert i >= 0, label
    s = src.rfind(BS + "begin{figure}", 0, i)
    e = src.find(BS + "end{figure}", i) + len(BS + "end{figure}")
    return src[s:e]
def fragment(fn, label):
    return table_by_label(open(os.path.join(HERE, fn), encoding="utf-8").read(), label)
def between(src, start, end):
    i = src.find(start); assert i >= 0, start[:40]
    j = src.find(end, i + len(start)); assert j >= 0, end[:40]
    return src[i:j]
def sp(W, outc, model, est, term):
    r = SP[(SP.W == W) & (SP.outcome == outc) & (SP.model == model) & (SP.estimator == est) & (SP.term == term)]
    assert len(r), (W, outc, model, est, term)
    return float(r.iloc[0].b), float(r.iloc[0].se_cl)
def f2(x): return f"{x:.2f}"
def neg(x): return ("$-$" + f"{abs(x):.2f}") if x < 0 else f"{x:.2f}"

out = TPL

# ------------------------------------------------------------- header comment
hdr_end = out.find(BS + "documentclass")
out = ("% main_co2_nature_20260906.tex  (candidate, 2026-09-06)\n"
       "% Built by 34_assemble_20260906.py from the 09-03 country-clustered template,\n"
       "% the coauthor-edited 08-26 copy (Downloads/main_co2_nature_20260826 (2).tex:\n"
       "% JL Discussion + heterogeneity wording; Chunan/Fangyu Methods), Junya's\n"
       "% requests (spatial SLX/SAR/SEM/SDM table; LTO and 50/50 to the appendix),\n"
       "% and the growth-coupled SAF projection (31_saf_growth.py).\n"
       "% Inference: standard errors clustered by country throughout (09-03 decision).\n"
       "% Main displays: Tables 1-4 (main, decomposition, spatial, SCC) and Figs 1-5\n"
       "% (heterogeneity, airport concentration, attributed map, mismatch map, SAF).\n"
       "% Extended Data: tables 1-14, figures 1-11; Supplementary tables 1-3.\n"
       "% [TODO cite] markers remain; compile on Overleaf (local MiKTeX broken).\n") + out[hdr_end:]
out = out.replace(BS + "date{Nature-format draft, 3 September 2026}", BS + "date{Nature-format draft, candidate of 6 September 2026}")

# ------------------------------------------------------------- abstract
b_slx, se_slx = sp("contig", "ln_co2_tot", "SLX", "IV", "theta")
b_sdm_t, se_sdm_t = sp("contig", "ln_co2_tot", "SDM", "IV", "theta")
b_sdem_t, se_sdem_t = sp("contig", "ln_co2_tot", "SDEM", "IV", "theta")
rho_sar, se_rho_sar = sp("contig", "ln_co2_tot", "SAR", "IV", "rho")
rho_sdm, se_rho_sdm = sp("contig", "ln_co2_tot", "SDM", "IV", "rho")
lam_sem, _ = sp("contig", "ln_co2_tot", "SEM", "IV", "lambda")
lam_sdem, _ = sp("contig", "ln_co2_tot", "SDEM", "IV", "lambda")
b_sar, se_sar = sp("contig", "ln_co2_tot", "SAR", "IV", "beta")
b_sem, se_sem = sp("contig", "ln_co2_tot", "SEM", "IV", "beta")
b_sdm, se_sdm = sp("contig", "ln_co2_tot", "SDM", "IV", "beta")
b_slx_own, se_slx_own = sp("contig", "ln_co2_tot", "SLX", "IV", "beta")
b_sdem_own, se_sdem_own = sp("contig", "ln_co2_tot", "SDEM", "IV", "beta")
d_sdm, sd_sdm = sp("contig", "ln_co2_tot", "SDM", "IV", "direct")
i_sdm, si_sdm = sp("contig", "ln_co2_tot", "SDM", "IV", "indirect")
t_sdm, st_sdm = sp("contig", "ln_co2_tot", "SDM", "IV", "total")
t_sar, st_sar = sp("contig", "ln_co2_tot", "SAR", "IV", "total")
lo_t, hi_t = sorted([b_sdm_t, b_slx, b_sdem_t])[0], sorted([b_sdm_t, b_slx, b_sdem_t])[-1]
own_lo, own_hi = min(b_slx_own, b_sdem_own), max(b_slx_own, b_sdem_own)

old_abs = ("Emissions also respond to the\nconnectivity of contiguous neighbours, with an elasticity of 1.9 when own and\nneighbour connectivity are jointly instrumented.")
assert old_abs in out
new_abs = ("Emissions also respond to the\nconnectivity of contiguous neighbours: across spatial lag, error and Durbin\nspecifications the neighbour elasticity is "
           + f"{lo_t:.1f} to {hi_t:.1f}" + ", the spatial lag of\nemissions itself is negligible, and the total effect of a network-wide\nconnectivity gain is "
           + f"{t_sdm:.1f}" + ", the same as the single-equation elasticity.")
out = out.replace(old_abs, new_abs)

# ------------------------------------------------------------- Results 1: allocation sentence, column reference
old = ("The estimate is insensitive to how emissions are\nassigned to countries, ranging from 5.62 under a 50/50 split of cruise\nemissions to 5.92 under the territorial rule, and it is stable across\naggregations of airport connectivity to the country level\n(Table~\\ref{tab:main}, Panels C--E).")
assert old in out
out = out.replace(old, ("The estimate is stable across aggregations of airport connectivity\nto the country level (Table~\\ref{tab:main}, Panels C--E) and insensitive\nto how emissions are assigned to countries, ranging from 5.62 under a 50/50\nsplit of cruise emissions to 5.92 under the territorial rule (Extended Data\nTable~\\ref{tab:alloc})."))
out = out.replace("Table~\\ref{tab:main}, column 6)", "Table~\\ref{tab:main}, column 4)")

# Table 1: drop LTO and 50/50 columns
t1 = fragment("_tex_main_cl.tex", "tab:main")
lines = []
for ln in t1.split("\n"):
    if ln.strip().startswith(BS + "begin{tabular}"):
        ln = ln.replace("{lcccccc}", "{lccccc}").replace("{lccccc}", "{lcccc}")
    elif "multicolumn{7}" in ln:
        ln = ln.replace("multicolumn{7}", "multicolumn{5}")
    elif "&" in ln and BS + "item" not in ln:
        parts = ln.split("&")
        if len(parts) == 7:
            parts = [parts[0], parts[1], parts[4], parts[5], parts[6]]
            ln = "&".join(parts)
    lines.append(ln)
t1 = "\n".join(lines)
t1 = t1.replace(" & (1) & (4) & (5) & (6) ", " & (1) & (2) & (3) & (4) ")
t1 = t1.replace("total aviation CO$_2$ under the bunker convention (all cruise plus departure-side LTO assigned to the departure country), landing-and-take-off CO$_2$ only, CO$_2$ with cruise split 50/50 between endpoint countries, bunker CO$_2$ from international flights,",
                "total aviation CO$_2$ under the bunker convention (all cruise plus departure-side LTO assigned to the departure country), bunker CO$_2$ from international flights,")
t1 = t1.replace("Heteroskedasticity-robust results are in Supplementary Table~\\ref{tab:exclusion2}.",
                "The territorial (LTO) and 50/50 allocation rules are in Extended Data Table~\\ref{tab:alloc}; heteroskedasticity-robust results are in Supplementary Table~\\ref{tab:exclusion2}.")
assert "LTO" not in t1.split(BS + "begin{tablenotes}")[0], "LTO column not removed"
out = out.replace("%%TAB_MAIN%%", t1)

# ------------------------------------------------------------- airport section: effcurve and conc table to ED
# (09-06, Sunbin) the whole airport subsection moves to Extended Data; a condensed
# paragraph goes into the attribution section instead.
s = out.find(BS + "subsection*{Airport-level evidence: the response is systemic, and its")
e = out.find(BS + "subsection*{Where the elasticity comes from: frequency, not aircraft size")
assert 0 < s < e
out = out[:s] + out[e:]
old = ("The airport concentration results add\na practical corollary: an instrument that covered the top five percent of\nairports by attributed emissions, some 190 nodes, would cover 85 percent\nof the connectivity-driven total, and one covering the top ten percent\nwould cover 94 percent.")
assert old in out
out = out.replace(old, r"""The country estimates are not an artefact of national aggregation.
In an airport panel with airport and country-by-year fixed effects, so
that airports are compared with other airports of the same country in the
same year, a one percent increase in an airport's connectivity is
associated with 3.72 percent more CO$_2$, a 0.49 percent decline in
CO$_2$ per seat-km and a 0.33 point higher international share; the
elasticity is 2.0 to 2.1 at the airports in the 1996 global top five
percent and 3.8 to 4.0 elsewhere, so the response is systemic rather than
hub-driven (Extended Data Table~\ref{tab:airport_het} and Extended Data
Fig.~\ref{fig:effcurve}; these estimates are descriptive, as no valid
airport-level instrument is available, Methods). The emissions the
response generates are nonetheless concentrated: applying the elasticity
to each airport's connectivity change attributes 345 Mt across airports,
of which the top five percent of airports, some 190 nodes led by Dubai,
Doha, Shanghai Pudong, Istanbul and Incheon, hold 84.5 percent against
77.6 percent of emissions themselves (Extended Data
Fig.~\ref{fig:airportconc} and Extended Data Table~\ref{tab:airport_conc}),
so an instrument covering those nodes would cover 85 percent of the
connectivity-driven total.""")

# ------------------------------------------------------------- decomposition: waterfall to ED
fig_wf = figure_by_label(out, "fig:waterfall")
out = out.replace(fig_wf + "\n", "")
out = out.replace("Table~\\ref{tab:decomp} and\nFig.~\\ref{fig:waterfall} report", "Table~\\ref{tab:decomp} and Extended Data\nFig.~\\ref{fig:waterfall} report")
assert "Extended Data\nFig.~\\ref{fig:waterfall}" in out
out = out.replace("%%TAB_DECOMP%%", fragment("_tex_decomp_cl.tex", "tab:decomp"))

# ------------------------------------------------------------- heterogeneity: JL softening; gradient figure to ED
old = "and Europe is a zero ($-0.61$, s.e.\\ 1.73)."
assert old in out
out = out.replace(old, "while the estimate for Europe is small and statistically\nindistinguishable from zero ($-0.61$, s.e.\\ 1.73).")
old = ("The headline elasticity therefore describes\nthe network's extensive margin; for mature networks, connectivity growth is\napproximately carbon-neutral at the margin, for the reason the\ndecomposition makes explicit.")
assert old in out
out = out.replace(old, ("The headline elasticity is therefore driven primarily by\ncountries with lower baseline income and connectivity, while the effects\nare smaller and less precisely estimated in mature networks, for the\nreason the decomposition makes explicit."))
fig_gr = figure_by_label(out, "fig:gradient")
out = out.replace(fig_gr + "\n", "")
out = out.replace("distribution (Fig.~\\ref{fig:gradient} and Extended Data", "distribution (Extended Data Fig.~\\ref{fig:gradient} and Extended Data")

# ------------------------------------------------------------- spillover section -> spatial models
s = out.find(BS + "subsection*{Emissions respond to contiguous neighbours' connectivity}")
e = out.find("%%TAB_SPILL%%") + len("%%TAB_SPILL%%")
assert s > 0 and e > s
frac_lo = i_sdm / d_sdm
frac_hi = b_slx / b_slx_own
spatial_text = r"""\subsection*{Emissions respond to neighbours' connectivity, not to
neighbours' emissions}
Emissions do not respond only to a country's own network. Because
connectivity is a property of the network, a country's emissions may
depend on the connectivity of its neighbours, on their emissions, or on
spatially correlated shocks, and these channels correspond to different
models. Table~\ref{tab:spatial} nests them within the standard spatial
family (Methods): the spatial lag of connectivity (SLX), the spatial lag of
the outcome (SAR), a spatially autoregressive error (SEM), and their
combinations (the spatial Durbin model, SDM, and the spatial Durbin error
model, SDEM). Neighbours are the contiguous countries, the only definition
under which the spillover survives clustering by country and a permutation
placebo that relabels countries at random in the weight matrix (Extended
Data Tables~\ref{tab:spillover} and \ref{tab:spill_ext}; Extended Data
Figs.~\ref{fig:spilldecay} and \ref{fig:spillplacebo}); inverse-distance
weights over all countries are reported for completeness (Extended Data
Table~\ref{tab:spatial_ext}). Panel A treats connectivity as exogenous;
Panel B instruments own connectivity with the Feyrer shifter, neighbours'
connectivity with the identically weighted shifter, and the spatial lag of
emissions with the spatial lags of the instruments and controls.

Three results follow. First, the spillover runs through neighbours'
connectivity rather than through neighbours' emissions or common shocks.
The coefficient on the spatial lag of CO$_2$ is """ + f"{neg(rho_sar)} (s.e.\\ {f2(se_rho_sar)})" + r""" in
the SAR and """ + f"{neg(rho_sdm)} (s.e.\\ {f2(se_rho_sdm)})" + r""" in the SDM, and the spatial-error
parameter is """ + f"{f2(min(lam_sem, lam_sdem))} to {f2(max(lam_sem, lam_sdem))}" + r""", whereas the neighbours' connectivity term is
""" + f"{f2(b_slx)} (s.e.\\ {f2(se_slx)})" + r""" in the SLX, """ + f"{f2(b_sdm_t)} (s.e.\\ {f2(se_sdm_t)})" + r""" in the SDM and
""" + f"{f2(b_sdem_t)} (s.e.\\ {f2(se_sdem_t)})" + r""" in the SDEM. Second, the own elasticity is robust to
the spatial specification: it is """ + f"{f2(b_sar)}" + r""" under the spatial lag, """ + f"{f2(b_sem)}" + r""" under
the spatial error and """ + f"{f2(d_sdm)}" + r""" as the direct effect of the SDM, against 5.67
in Table~\ref{tab:main}, and """ + f"{f2(own_lo)} to {f2(own_hi)}" + r""" when the neighbours' term is entered,
which absorbs the part of the own response that moves with neighbours'
growth. Third, the total effect of a network-wide increase in
connectivity, direct plus indirect, is """ + f"{f2(t_sdm)} (s.e.\\ {f2(st_sdm)})" + r""" in the SDM, the
same as the single-equation elasticity; its indirect component,
""" + f"{f2(i_sdm)} (s.e.\\ {f2(si_sdm)})" + r""", is the cross-border part. The margins of the
neighbour response are in Extended Data Table~\ref{tab:spillover}, Panel
B: a neighbour's connectivity gain raises own seat-kilometres by 2.56
percent (s.e.\ 0.69) through longer and more international flying and
lowers emissions per seat-km by 0.63 percent (s.e.\ 0.23), the signature
of traffic feeding a regional hub, whereas the own response works through
frequency. National estimates therefore understate the network-wide
emissions effect of connectivity growth by between about
""" + f"{int(round(100 * frac_lo / 5) * 5)} and {int(round(100 * frac_hi / 5) * 5)}" + r""" percent of the own effect, depending on whether the SDM
indirect effect or the SLX neighbour elasticity is used, and the emissions
accrue across borders.

%%TAB_SPATIAL%%"""
out = out[:s] + spatial_text + out[e:]
out = out.replace("%%TAB_SPATIAL%%", fragment("_tex_spatial.tex", "tab:spatial"))

# ------------------------------------------------------------- attribution: bars and levels to ED
out = out.replace("%%TAB_SCC%%", table_by_label(OLD, "tab:scc"))
for lab in ["fig:bars", "fig:levels", "fig:mismatch"]:
    fg = figure_by_label(out, lab)
    out = out.replace(fg + "\n", "")
out = out.replace("(Table~\\ref{tab:scc} and Fig.~\\ref{fig:bars})", "(Table~\\ref{tab:scc} and Extended Data Fig.~\\ref{fig:bars})")
out = out.replace("(Figs.~\\ref{fig:levels} and \\ref{fig:mismatch})", "(Extended Data Figs.~\\ref{fig:levels} and \\ref{fig:mismatch})")
assert "Extended Data Fig.~\\ref{fig:bars}" in out and "Extended Data Figs.~\\ref{fig:levels}" in out
# (Sunbin 09-06) mismatch sentence without country names
old = ("the\nbunker-attributed share of world emissions exceeds the physical\nlanding-and-take-off share by 1.4 percentage points for the United States\nand the United Arab Emirates, while China's attributed share falls short by\n3.5 points, a gap that is positive at every international mega-hub and\nnegative at large domestically oriented hubs")
assert old in out
out = out.replace(old, ("the\nbunker-attributed share of world emissions exceeds the physical\nlanding-and-take-off share by up to 1.4 percentage points in countries\nwith large international hubs and falls short by up to 3.5 points in\ncountries with large domestically oriented networks, a gap that is\npositive at every international mega-hub and negative at large domestic\nhubs"))

# ------------------------------------------------------------- SAF: growth-coupled projection
s = out.find(BS + "subsection*{Only fuel switching materially lowers the level}")
e = out.find(BS + "subsection*{Attribution and fuel-switching scenarios [Ray and Lisa]}")
saf_text = r"""\subsection*{Only fuel switching materially lowers the level}
Since the efficiency margin offsets seven percent of the scale margin, the
level of emissions can be materially lowered only by changing the fuel
burned. We project world aviation CO$_2$ to 2050 by combining continued
connectivity growth with ReFuelEU-style blending paths
(Fig.~\ref{fig:saf}; Methods). Connectivity is assumed to grow at its
2010--2019 pace (0.74 log points per year on average across countries;
0.45 in a low case) and is converted to emissions with the mature-network
elasticity of 3.0, which already embeds the efficiency margin; the
blending share follows the ReFuelEU milestones from 2 percent in 2025 to
70 percent in 2050, with life-cycle savings of 50, 65 and 80 percent.
Without fuel switching, emissions reach 1{,}528 Mt in 2050 (1{,}207 Mt in
the low-growth case), 1.8 times the 2023 level of 838 Mt. The full
blending path with a 65 percent saving returns 2050 emissions to the 2023
level (833 Mt), and only the 80 percent saving takes them below it (672
Mt); no path reaches the 482 Mt that would remain after removing the
emissions attributed to the past generation of connectivity growth.
Holding 2023 traffic fixed, as in a pure accounting exercise, would
understate 2050 emissions under the same blending paths by 300 to 450 Mt.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.98\textwidth]{CO2_saf_growth.png}
\caption{\textbf{World aviation CO$_2$ to 2050 under continued connectivity growth and ReFuelEU-style SAF blending.} Left, connectivity growth at its 2010--2019 pace; right, a low-growth case. Solid lines apply life-cycle savings of 50, 65 and 80 percent along the ReFuelEU blending milestones (shares on the axis); the dashed grey line is the no-SAF path, the dotted red line the 65 percent path with 2023 traffic held fixed, and the horizontal lines mark the 2023 level (838 Mt) and the level net of the emissions attributed to 1996--2023 connectivity growth (482 Mt). Traffic growth is converted to emissions with the mature-network elasticity (3.0).}
\label{fig:saf}
\end{figure}

"""
out = out[:s] + saf_text + out[e:]
old = ("Fuel-switching scenarios back fuel out of emissions\nat 3.15 kg CO$_2$ per kg and apply ReFuelEU-style blending shares (2 to 70\npercent over 2025--2050) with life-cycle savings of 50, 65, and 80 percent,\nholding 2023 traffic fixed; the calculations are partial-equilibrium\naccounting.")
assert old in out
out = out.replace(old, (r"""Fuel-switching scenarios project world emissions as
$E(t) = E_{2023}\,\exp[\beta g (t-2023)]\,(1 - s_t r)$, where $g$ is the
average annual change in log connectivity across countries over
2010--2019 (0.0074; 0.0045 in the low case), $\beta$ the mature-network
elasticity (3.0; Extended Data Table~\ref{tab:temporal}, Panel C), $s_t$
the ReFuelEU blending share interpolated between the 2025--2050 milestones
(2 to 70 percent) and $r$ the life-cycle saving of sustainable aviation
fuel (50, 65 and 80 percent). Because $\beta$ is a reduced-form emissions
elasticity it already contains the efficiency margin, so no separate
intensity trend is applied; ReFuelEU is used as a benchmark blending path
rather than as a forecast of global mandates, and the calculations are
partial-equilibrium accounting."""))

# ------------------------------------------------------------- Discussion: JL version (with one spatial clause)
s = out.find(BS + "section*{Discussion [Jinwoo]}")
e = out.find("%=======================================================================\n" + BS + "section*{Methods}")
# JL's five-implication Discussion lives only in the docx (the (2) tex still has the 08-26 Discussion)
from docx import Document
_d = Document(r"C:\Users\sunbi\Downloads\GACI_CO2_editable_JL.docx")
_ps = [q.text.strip() for q in _d.paragraphs if q.text.strip()]
_i = _ps.index("Discussion [Jinwoo]"); _j = _ps.index("Methods", _i)
_paras = _ps[_i + 1:_j]
def _tex(t):
    t = t.replace("CO" + chr(8322), "CO$_2$").replace("CO2", "CO$_2$").replace("%", " percent").replace("&", BS + "&")
    t = t.replace("[aviation decarbonisation literature]", "[TODO cite: aviation decarbonisation pathways]")
    t = t.replace("[recent GACI paper]", "[TODO cite: companion GACI paper]").replace("[official ICAO source]", "[TODO cite: ICAO CORSIA]")
    t = t.replace(chr(8217), "'").replace(chr(8216), "`").replace(chr(8211), "--")
    return t
jl = BS + "section*{Discussion [Jinwoo]}\n%=======================================================================\n" + "\n\n".join(_tex(q) for q in _paras) + "\n\n"
old = ("A one percent increase in contiguous neighbours' connectivity raises own-country aviation CO$_2$ by about 2 percent, mainly through international traffic. The effect follows land borders rather than a smooth distance gradient, indicating a regional network externality rather than a global spillover.")
assert old in jl, jl[:3000]
jl = jl.replace(old, ("A one percent increase in contiguous neighbours' connectivity raises own-country aviation CO$_2$ by about 2 percent, mainly through international traffic. The effect follows land borders rather than a smooth distance gradient, indicating a regional network externality rather than a global spillover, and it operates through neighbours' connectivity rather than through neighbours' emissions: spatial lag and spatial error models leave the own elasticity and the total effect unchanged."))
out = out[:s] + jl + out[e:]

# ------------------------------------------------------------- Methods: Chunan/Fangyu sections from the coauthor copy
s = out.find(BS + "subsection*{Emissions data [Chunan and Fangyu]}")
e = out.find(BS + "subsection*{Estimation [Junya]}")
cf = between(CO, BS + "subsection*{Flight-level aviation CO$_2$ emissions}", BS + "subsection*{Instruments and validity [Junya]}")
cf = cf.replace(BS + "subsection*{Flight-level aviation CO$_2$ emissions}", BS + "subsection*{Flight-level aviation CO$_2$ emissions [Chunan and Fangyu]}")
cf = cf.replace(BS + "subsection*{Allocation of emissions to countries}", BS + "subsection*{Allocation of emissions to countries [Chunan and Fangyu]}")
cf = cf.replace(BS + "subsection*{Validation of the emissions inventory}", BS + "subsection*{Validation of the emissions inventory [Chunan and Fangyu]}")
cf = cf.replace(BS + "subsection*{Global Air Connectivity Index}", BS + "subsection*{Global Air Connectivity Index [Chunan and Fangyu]}")
cf = cf.replace("[htbp]", "[htbp]")
# sample sentence retained from the 09-03 version
cf = cf.rstrip() + "\n\nThe estimation sample covers 184 countries over 1996--2023, $N$ = 4{,}634 country-years; 6{,}356 airports carry emissions in the inventory, of which 5{,}354 are nodes of the connectivity network, the remainder accounting for 0.1 percent of departure emissions.\n\n"
out = out[:s] + cf + out[e:]

# ------------------------------------------------------------- Methods: spatial models subsection after Spillover design
anchor = BS + "subsection*{Mediation [Junya]}"
spatial_methods = r"""\subsection*{Spatial models [Junya]}
The spatial specifications in Table~\ref{tab:spatial} extend
equation~\ref{eq:main} with, respectively, the neighbours' average log
connectivity $W \ln \mathrm{GACI}_{ct}$ (SLX), the neighbours' average log
emissions $\rho\, W \ln \mathrm{CO_2}_{ct}$ (SAR), a spatially
autoregressive disturbance $u_{ct} = \lambda W u_{ct} + \varepsilon_{ct}$
(SEM), the spatial lag together with the neighbours' connectivity (SDM),
and the neighbours' connectivity together with the spatial error (SDEM).
$W$ is the row-normalised land-contiguity matrix, applied within each year
to the countries in the sample that year, so that the stacked matrix is
block-diagonal by year; countries without a land neighbour have a zero row.
Panel A estimates the models with country and year fixed effects on the
within-transformed data, by least squares for SLX and by maximum
likelihood for the spatial-lag and spatial-error models, with the
log-determinant summed over the yearly blocks. Panel B instruments own
connectivity with the Feyrer shifter, neighbours' connectivity with the
identically weighted average of the shifter, and the spatial lag of the
outcome with the first and second spatial lags of the shifter and of the
exogenous controls, following Kelejian and Prucha's generalised spatial
two-stage least squares; the spatial-error parameter is estimated by their
moments estimator from the 2SLS residuals, after which the equation is
re-estimated on the spatially filtered variables. Direct, indirect and
total effects of connectivity are the averages, over the yearly blocks, of
the diagonal, the off-diagonal row sums and the row sums of $(I-\rho
W)^{-1}(\beta I + \theta W)$, with standard errors from 100 draws of the
coefficient vector from its estimated covariance. Standard errors are
clustered by country in Panel B. Extended Data
Table~\ref{tab:spatial_ext} repeats Panel B with inverse-distance weights
and for international CO$_2$ and carbon intensity.

"""
out = out.replace(anchor, spatial_methods + anchor)

# ------------------------------------------------------------- Extended Data: tables and figures
ed_tables = [("%%TAB_TEMPORAL%%", fragment("_tex_main_cl.tex", "tab:temporal")),
             ("%%TAB_ALLOC%%", fragment("_tex_spatial.tex", "tab:alloc")),
             ("%%TAB_HETERO%%", fragment("_tex_hetero_tot_cl.tex", "tab:hetero")),
             ("%%TAB_MEDIATION%%", fragment("_tex_main_cl.tex", "tab:mediation")),
             ("%%TAB_DECOMP_HETERO%%", fragment("_tex_decomp_cl.tex", "tab:decomp_hetero")),
             ("%%TAB_AIRPORT_HET%%", fragment("_tex_airport.tex", "tab:airport_het")),
             ("%%TAB_AIRPORT_CONC%%", fragment("_tex_airport_conc.tex", "tab:airport_conc")),
             ("%%TAB_SPILLOVER%%", fragment("_tex_spill_cl.tex", "tab:spillover")),
             ("%%TAB_SPILL_EXT%%", fragment("_tex_spill_cl.tex", "tab:spill_ext")),
             ("%%TAB_SPATIAL_EXT%%", fragment("_tex_spatial.tex", "tab:spatial_ext")),
             ("%%TAB_EXCL%%", fragment("_tex_exclusion_cl.tex", "tab:exclusion")),
             ("%%TAB_FUNCFORM%%", fragment("_tex_yifu_cl.tex", "tab:funcform")),
             ("%%TAB_GRADIENT%%", fragment("_tex_yifu_cl.tex", "tab:gradient")),
             ("%%TAB_ATTR_SENS%%", fragment("_tex_yifu_cl.tex", "tab:attr_sens"))]
# rebuild the ED table block in the chosen order
s = out.find("%%TAB_TEMPORAL%%")
e = out.find("%%TAB_ATTR_SENS%%") + len("%%TAB_ATTR_SENS%%")
ed_block = "\n\n".join(m for m, _ in ed_tables)
out = out[:s] + ed_block + out[e:]
for m, frag in ed_tables:
    assert m in out, m
    out = out.replace(m, frag)
# ED figures: rebuild block (order of first citation in the text)
s = out.find(BS + "begin{figure}", out.find(BS + "section*{Extended Data}"))
e = out.find(BS + "clearpage\n" + BS + "section*{Supplementary Tables}")
ed_fig_src = out[s:e]
def edfig(label, src=None):
    return figure_by_label(src if src is not None else ed_fig_src, label)
figs_main_moved = {}
for lab in ["fig:effcurve", "fig:waterfall", "fig:gradient", "fig:bars", "fig:levels", "fig:airportconc", "fig:mismatch"]:
    figs_main_moved[lab] = figure_by_label(TPL, lab)
ed_figs = [edfig("fig:temporal"), figs_main_moved["fig:waterfall"], figs_main_moved["fig:gradient"],
           figs_main_moved["fig:bars"], figs_main_moved["fig:levels"], figs_main_moved["fig:mismatch"], figs_main_moved["fig:effcurve"],
           figs_main_moved["fig:airportconc"],
           edfig("fig:rfquintile"), edfig("fig:spilldecay"), edfig("fig:spillplacebo"), edfig("fig:placeborf")]
out = out[:s] + "\n\n".join(ed_figs) + "\n\n" + out[e:]
# strip any leftover comment block about the carbon-price map
out = re.sub(r"% Carbon-intensity-of-trade-gains map retained.*?\n(?=" + re.escape(BS) + r"clearpage)", "", out, flags=re.S)

# renumber ED captions in order of appearance; strip old prefixes; add prefixes to moved captions
ed_start = out.find(BS + "section*{Extended Data}")
si_start = out.find(BS + "section*{Supplementary Tables}")
ed = out[ed_start:si_start]
def strip_prefix(cap):
    cap = re.sub(r"^Extended Data Table( \d+| X)?: ", "", cap)
    cap = re.sub(r"^Extended Data Fig\.\\ (\d+): ", "", cap)
    return cap
tcount = 0; fcount = 0
def recap(m):
    global tcount, fcount
    env, body = m.group(1), m.group(2)
    cap_i = body.find(BS + "caption{")
    # find the matching brace of \caption{...}
    j = cap_i + len(BS + "caption{"); depth = 1; k = j
    while depth:
        if body[k] == "{": depth += 1
        elif body[k] == "}": depth -= 1
        k += 1
    cap = body[j:k - 1]
    cap = strip_prefix(cap)
    if cap.startswith(BS + "textbf{"):
        # main-style bold caption: keep bold, put the prefix in front
        pass
    if env == "table":
        tcount += 1; new = f"Extended Data Table {tcount}: " + cap
    else:
        fcount += 1; new = f"Extended Data Fig.\\ {fcount}: " + cap
    return BS + "begin{" + env + "}" + body[:j] + new + body[k - 1:] + BS + "end{" + env + "}"
ed = re.sub(re.escape(BS) + r"begin\{(table|figure)\}(.*?)" + re.escape(BS) + r"end\{\1\}", recap, ed, flags=re.S)
out = out[:ed_start] + ed + out[si_start:]
print("ED tables:", tcount, "| ED figures:", fcount)
# supplementary numbering already in fragments (1-3)
out = out.replace("%%TAB_EXCL2%%", fragment("_tex_exclusion_cl.tex", "tab:exclusion2"))
out = out.replace("%%TAB_AIRPORT_IV%%", fragment("_tex_airport.tex", "tab:airport_iv"))
out = out.replace("%%TAB_ACCIDENT%%", fragment("_tex_yifu_cl.tex", "tab:accident_iv"))
for a, b in [("Supplementary Table: Alternative instrument constructions", "Supplementary Table 1: Alternative instrument constructions"),
             ("Supplementary Table: Airport-level identification pilot", "Supplementary Table 2: Airport-level identification pilot"),
             ("Supplementary Table: Aviation-accident instrument", "Supplementary Table 3: Aviation-accident instrument")]:
    out = out.replace(a, b)
# floats: [htbp] -> [H] for drafting readability (as in the 08-27 user copy)
out = out.replace("[htbp]", "[H]")

INLINE_ED = False  # 09-06 later: Sunbin wants main text = main displays only; ED/SI collected at the end
if INLINE_ED:
    # ------------------------------------------------------------- inline ED/SI displays at first citation (Sunbin 09-06)
    # Every Extended Data / Supplementary table and figure is moved to just after the
    # paragraph in which it is first cited; the collecting sections are removed.
    ed_start = out.find(BS + "section*{Extended Data}")
    tail = out[ed_start:]
    main = out[:ed_start]
    floats = []
    for m in re.finditer(re.escape(BS) + r"begin\{(table|figure)\}.*?" + re.escape(BS) + r"end\{\1\}", tail, flags=re.S):
        blk = m.group(0)
        lab = re.search(re.escape(BS) + r"label\{([^}]+)\}", blk).group(1)
        floats.append((lab, blk))
    # sort by position of first citation in main (so insertion order is stable)
    def first_cite(lab):
        m = re.search(re.escape(BS) + r"ref\{" + re.escape(lab) + r"\}", main)
        return m.start() if m else len(main)
    # insertion point = end of the paragraph containing the first citation, then past
    # any floats already sitting after that paragraph (so main-text displays stay first)
    def para_end(pos):
        p = main.find("\n\n", pos)
        return len(main) if p < 0 else p
    groups = {}
    for lab, blk in floats:
        pos = first_cite(lab)
        assert pos < len(main), "uncited ED item " + lab
        groups.setdefault(para_end(pos), []).append((pos, lab, blk))
    def next_main_float_end(q):
        """If a main-text display (caption without ED/SI prefix) follows within the same
        subsection, return the position just after it, else q."""
        n = len(main)
        for tok in (BS + "subsection*{", BS + "section*{"):
            k = main.find(tok, q)
            if k >= 0:
                n = min(n, k)
        best = q
        for m in re.finditer(re.escape(BS) + r"begin\{(table|figure)\}", main[q:n]):
            st = q + m.start()
            endtok = BS + "end{" + m.group(1) + "}"
            en = main.find(endtok, st) + len(endtok)
            cap = main[st:en]
            if "caption{Extended Data" not in cap and "caption{Supplementary" not in cap:
                best = max(best, en)
        return best
    for p in sorted(groups, reverse=True):  # from the back so offsets stay valid
        q = next_main_float_end(p)
        while True:
            m = re.match(r"\s*" + re.escape(BS) + r"begin\{(table|figure)\}", main[q:])
            if not m:
                break
            endtok = BS + "end{" + m.group(1) + "}"
            q = main.find(endtok, q) + len(endtok)
        items = sorted(groups[p])
        ins = "\n\n" + "\n\n".join(blk for _, _, blk in items) + "\n"
        main = main[:q] + ins + main[q:]
    out = main + "\n" + BS + "end{document}\n"
    out = out.replace("\n\n\n\n", "\n\n").replace("\n\n\n", "\n\n")
    print("inlined ED/SI displays:", len(floats))

# renumber ED / SI captions by order of appearance
cnt = {"Extended Data Table": 0, "Extended Data Fig." + BS + " ": 0, "Supplementary Table": 0}
def renum(m):
    key = m.group(1)
    cnt[key] += 1
    return key + ("" if key.endswith(" ") else " ") + str(cnt[key]) + ":"
out = re.sub(r"(Extended Data Table|Extended Data Fig\." + re.escape(BS) + r" |Supplementary Table) ?\d+:", renum, out)
print("renumbered:", cnt)

# ------------------------------------------------------------- wide tables: shrink to text width (adjustbox)
# \resizebox (graphicx) that shrinks only when the tabular is wider than the text
# width; the adjustbox environment form broke inside threeparttable (09-06).
# threeparttable hooks \begin{tabular} to measure it, so a box around the tabular
# alone breaks the group structure; instead move caption+label out and put the
# resizebox around the whole threeparttable (tabular + notes scale together).
def _wrap_tpt(m):
    cap, lab, body = m.group(1), m.group(2), m.group(3)
    return (cap + "\n" + lab + "\n" + BS + "resizebox{" + BS + "ifdim" + BS + "width>" + BS + "textwidth " + BS + "textwidth" + BS + "else" + BS + "width" + BS + "fi}{!}{%\n"
            + BS + "begin{threeparttable}" + body + BS + "end{threeparttable}}")
pat = (re.escape(BS) + r"begin\{threeparttable\}\n(" + re.escape(BS) + r"caption\{.*?\})\n(" + re.escape(BS) + r"label\{[^}]+\})\n(.*?)" + re.escape(BS) + r"end\{threeparttable\}")
out, nwrap = re.subn(pat, _wrap_tpt, out, flags=re.S)
assert nwrap == out.count(BS + "begin{threeparttable}"), (nwrap, out.count(BS + "begin{threeparttable}"))
# (panel-title p{} trick removed 09-06: p-columns inside the resizebox broke every table)

# ------------------------------------------------------------- checks
left = re.findall(r"%%TAB_[A-Z_]+%%", out); assert not left, left
labels = re.findall(BS + BS + r"label\{([^}]+)\}", out)
refs = set(re.findall(BS + BS + r"ref\{([^}]+)\}", out))
missing = sorted(r for r in refs if r not in labels)
dups = sorted(set(l for l in labels if labels.count(l) > 1))
unref = sorted(l for l in labels if l not in refs and not l.startswith("eq:"))
print("labels", len(labels), "| missing refs:", missing, "| duplicate labels:", dups, "| unreferenced:", unref)
body = re.sub(r"%.*", "", out)
print("em-dash:", body.count(chr(8212)), "| emph:", len(re.findall(BS + BS + r"emph\{", body)), "| braces:", body.count("{") - body.count("}"))
# main display count
main_part = body[:body.find(BS + "section*{Discussion")]
print("main tables:", len(re.findall(BS + BS + r"begin\{table\}", main_part)), "| main figures:", len(re.findall(BS + BS + r"begin\{figure\}", main_part)))
# tabular column consistency
for m in re.finditer(re.escape(BS) + r"begin\{tabular\}\{([^}]+)\}(.*?)" + re.escape(BS) + r"end\{tabular\}", out, flags=re.S):
    ncol = len(re.findall(r"[lcr]", m.group(1)))
    for ln in m.group(2).split(BS + BS):
        if "&" in ln and "multicolumn" not in ln and "cmidrule" not in ln:
            k = ln.count("&") + 1
            if k != ncol:
                print("  column mismatch:", ncol, k, ln.strip()[:70])
pre = re.sub(BS + BS + r"begin\{table\}.*?" + BS + BS + r"end\{table\}", " ", body.split(BS + "section*{Methods}")[0], flags=re.S)
pre = re.sub(BS + BS + r"begin\{figure\}.*?" + BS + BS + r"end\{figure\}", " ", pre, flags=re.S)
pre = re.sub(BS + BS + r"[a-zA-Z]+\*?", " ", pre)
print("approx words before Methods (excl. displays):", len(pre.split()))

outtex = os.path.join(OUTDIR, "main_co2_nature_20260906.tex")
open(outtex, "w", encoding="utf-8").write(out)
figs = sorted(set(re.findall(BS + BS + r"includegraphics\[[^\]]*\]\{([^}]+)\}", out)))
missfig = []
for f in figs:
    src = os.path.join(HERE, f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(OUTDIR, f))
    else:
        missfig.append(f)
print("figures copied:", len(figs) - len(missfig), "| missing:", missfig)
zp = os.path.join(HERE, "co2_overleaf_20260906.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in os.listdir(OUTDIR):
        z.write(os.path.join(OUTDIR, fn), fn)
print("wrote", outtex, "and", zp)
