# -*- coding: utf-8 -*-
import io, os
SRC = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
p = os.path.join(SRC, "appendix_inequality_v2.tex")
s = io.open(p, encoding="utf-8").read()

new = r"""Table~\ref{tab:a_growth_total} reports total GDP rather than GDP per capita as the outcome, with log population entered as a control throughout. The estimates exceed the per capita estimates by between $0.07$ and $0.20$ across the three connectivity measures, which is the population term, and the pattern across instruments is unchanged: the Feyrer estimates are positive and significant, the tourism estimates are not distinguishable from zero. Among the level outcomes, total GDP is the only one for which the Hansen test does not reject ($p=0.13$).

\begin{table}[H]\centering\caption{Total GDP as an outcome.}\label{tab:a_growth_total}
\begin{threeparttable}\small\input{tables_appendix/tabA_growth_total}
\begin{tablenotes}\footnotesize\item Outcome is log GDP in constant 2015 US dollars. Log population and country and year fixed effects throughout. Robust SE in parentheses, country-clustered SE in brackets with the corresponding significance level. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

"""

anchor = "\\section*{Data and code availability}"
assert s.count(anchor) == 1, s.count(anchor)
if "tab:a_growth_total" not in s:
    s = s.replace(anchor, new + anchor)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("appendix patched, chars:", len(s))
else:
    print("already present")
