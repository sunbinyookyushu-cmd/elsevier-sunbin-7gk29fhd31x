# -*- coding: utf-8 -*-
import os, re, shutil, io

BS = chr(92)  # backslash

SRC = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
OUT = os.path.join(SRC, "Overleaf_Inequality_20260918")
os.makedirs(OUT, exist_ok=True)


def rd(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


tex = rd(os.path.join(SRC, "main_inequality_v2.tex"))
bib = rd(os.path.join(SRC, "refs_inequality.bib")).strip()
appendix = rd(os.path.join(SRC, "appendix_inequality_v2.tex"))

# ---------- 1. inline tables (escaping stray % which LaTeX reads as a comment) ----------
TABLES = ["tab_sumstat", "tab_main", "tab_hetero", "tab_conc", "tab_tails", "tab_mech",
          "tab_contribution", "tab_diag", "tab_horizon", "tab_openskies", "tab_robust",
          "tab_growth", "tab_growth_decomp"]
APPX_TABLES = ["tabA_levels", "tabA_absred", "tabA_tails_other", "tabA_tails_inc3",
               "tabA_inc3_split", "tabA_leads", "tabA_rf_cont", "tabA_es_conn",
               "tabA_es_ineq", "tabA_os_feyrer", "tabA_country", "tabA_covid",
               "tabA_continent", "tabA_altdv", "tabA_longdiff_full",
               "tabA_fs_cont", "tabA_loo_contyear", "tabA_rfq",
               "tabA_growth_diag", "tabA_growth_horizon", "tabA_growth_longdiff",
               "tabA_growth_hetero", "tabA_growth_condgdp", "tabA_growth_total"]
n_tab = 0


def inline(text, subdir, names):
    global n_tab
    for nm in names:
        t = rd(os.path.join(SRC, subdir, nm + ".tex")).rstrip()
        t = re.sub(r"(?<!" + BS + BS + r")%", BS + BS + r"%", t)
        token = BS + "input{" + subdir + "/" + nm + "}"
        if token in text:
            text = text.replace(token, t)
            n_tab += 1
        else:
            print("WARNING: token not found:", nm)
    return text


tex = inline(tex, "tables", TABLES)
appendix = inline(appendix, "tables_appendix", APPX_TABLES)

# ---------- 2. split preamble / body ----------
body = tex.split(BS + "begin{document}", 1)[1]
body = BS + "section{Introduction}" + body.split(BS + "section{Introduction}", 1)[1]
for junk in [BS + "bibliographystyle{elsarticle-harv}",
             BS + "bibliography{refs_inequality}",
             BS + "end{document}"]:
    body = body.replace(junk, "")
body = body.rstrip()

abstract = tex.split(BS + "begin{abstract}", 1)[1].split(BS + "end{abstract}", 1)[0].strip()

# ---------- 3. new self-contained preamble, matching the GACI-trade Overleaf project ----------
HEAD = r"""%=======================================================================
%  Growth for Whom? Airport Connectivity and the Distribution of National Income
%  Target: Transportation Research Part A: Policy and Practice (Elsevier)
%  SELF-CONTAINED: bibliography embedded via filecontents; all tables inline.
%  Upload this .tex plus the figures:
%     fig_horizon.png   fig_rf_quintile.png   fig_map_base_gacimax.png   fig_map_implied_gini.png
%  Compile: pdflatex -> bibtex -> pdflatex x2
%  Built 2026-09-18 from main_inequality_v2.tex + appendix_inequality_v2.tex (polished draft v2),
%  formatted to match the companion GACI-trade Overleaf project.
%=======================================================================
\begin{filecontents*}[overwrite]{GACI_Inequality_refs.bib}
__BIB__
\end{filecontents*}

\documentclass[review,3p,times,authoryear]{elsarticle}

\usepackage{lineno,hyperref}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{threeparttable}
\usepackage{multirow}
\usepackage{url}
\usepackage{float}

% --- Reference-list formatting (TRA / Elsevier Harvard): DOIs as https://doi.org/... links,
%     no "doi:" / "URL:" prefixes, URLs in text font (Guide for Authors sample style).
\urlstyle{same}
\providecommand{\DOIprefix}{}\renewcommand{\DOIprefix}{}
\providecommand{\URLprefix}{}\renewcommand{\URLprefix}{}
\providecommand{\doi}[1]{}\renewcommand{\doi}[1]{\href{https://doi.org/#1}{\nolinkurl{https://doi.org/#1}}}

% --- Figure/table captions: elsarticle sets captions in \footnotesize; use \small with a bold label.
\makeatletter
\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip\small
  \sbox\@tempboxa{\textbf{#1.} #2}%
  \ifdim \wd\@tempboxa >\hsize
    \textbf{#1.} #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}
\makeatother
\journal{Transportation Research Part A: Policy and Practice}

\newcommand{\sym}[1]{\ensuremath{^{#1}}}

\begin{document}

\begin{frontmatter}

\title{Growth for Whom? Airport Connectivity and the Distribution of National Income}

\author[a]{Sunbin Yoo\corref{cor1}}
\ead{[email]}
\cortext[cor1]{Corresponding author.}
\author[a]{[Co-author]}
\address[a]{[Affiliation]}

\begin{abstract}
__ABSTRACT__
\end{abstract}

\begin{keyword}
Air connectivity \sep income inequality \sep Gini coefficient \sep
shift-share instrument \sep hub concentration \sep redistribution
\end{keyword}

\end{frontmatter}

\linenumbers

"""

TAIL = r"""

\bibliographystyle{elsarticle-harv}
\bibliography{GACI_Inequality_refs}

\end{document}
"""

out = HEAD.replace("__BIB__", bib).replace("__ABSTRACT__", abstract) + body + "\n\n" + appendix.strip() + TAIL

with io.open(os.path.join(OUT, "main.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write(out)

for fig in ["fig_horizon.png", "fig_rf_quintile.png", "fig_map_base_gacimax.png", "fig_map_implied_gini.png"]:
    shutil.copy2(os.path.join(SRC, fig), os.path.join(OUT, fig))
with io.open(os.path.join(OUT, "GACI_Inequality_refs.bib"), "w", encoding="utf-8", newline="\n") as f:
    f.write(bib + "\n")

print("tables inlined :", n_tab)
print("main.tex chars :", len(out))
print("leftover input :", out.count(BS + "input{"))
print("out dir        :", OUT)
