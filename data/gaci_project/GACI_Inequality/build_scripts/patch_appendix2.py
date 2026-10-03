# -*- coding: utf-8 -*-
"""Insert the second batch of appendix tables (with interpretation) into appendix_inequality.tex."""
import io, sys

P = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality\appendix_inequality.tex"
t = io.open(P, encoding="utf-8").read()

# ---- goes at the end of Appendix A, before the Appendix B header -------------
A_ADD = r"""
Table~\ref{tab:a_continent} reports the continent-specific 2SLS estimates of Table~\ref{tab:hetero} for both hub connectivity and hub quality, and adds North America. The two measures agree within every continent: the estimate is positive and significant in Asia ($0.48$ for hub connectivity and $0.86$ for hub quality), negative and significant in Africa ($-0.21$ and $-0.25$), and not distinguishable from zero elsewhere. The North American, Middle Eastern and Oceanian estimates rest on first stages with $F$ below $2$ and carry no information.

\begin{table}[H]\centering\caption{Continent-specific 2SLS, both connectivity measures (Feyrer instrument).}\label{tab:a_continent}
\begin{threeparttable}\small\input{tables_appendix/tabA_continent}
\begin{tablenotes}\footnotesize\item Robust SE in parentheses. Country and year fixed effects and log population within each continent sample. North America comprises Canada, Greenland and the United States. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_altdv} replaces the model-based SWIID series with the survey-based World Bank Poverty and Inequality Platform series, which is observed only in survey years and gives 1,877 country-years. The outcomes are in points rather than logs, so the coefficients are not comparable in size with Table~\ref{tab:main}, but the signs are the same in both OLS and 2SLS: the Gini and the top-decile share rise with hub connectivity and the bottom-quintile share falls. The 2SLS coefficients are large for the same reason they are large in the main table, and the bottom-quintile coefficient is the only one that is not significant in OLS.

\begin{table}[H]\centering\caption{Survey-based inequality measures (World Bank Poverty and Inequality Platform).}\label{tab:a_altdv}
\begin{threeparttable}\small\input{tables_appendix/tabA_altdv}
\begin{tablenotes}\footnotesize\item Outcomes in points. Country and year fixed effects and log population. Robust SE in parentheses. The sample is the survey years for which the World Bank reports a distribution. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

"""

# ---- goes at the end of Appendix B, before the Appendix C header -------------
B_ADD = r"""
Table~\ref{tab:a_longdiff} reports the complete long-difference battery: five windows, four estimators and the stacked five-year differences. No 2SLS specification in the table has a first-stage $F$ above $3$, and the point estimates range from $-21$ to $39$ with standard errors to match. The OLS coefficients are between $-0.04$ and $0.07$ and none is significant. The 1996--2023 window, which adds the pandemic years to the 1996--2019 window used in Section~\ref{sec:horizon}, changes the OLS coefficient from $0.066$ to $0.037$ and leaves the conclusion unchanged. The instruments predict the level of connectivity within countries but not its medium-run change.

\begin{table}[H]\centering\caption{Long differences and stacked differences, complete battery.}\label{tab:a_longdiff}
\begin{threeparttable}\small\input{tables_appendix/tabA_longdiff_full}
\begin{tablenotes}\footnotesize\item Cross-sections of changes with continent fixed effects and robust SE; the stacked five-year differences use year and continent effects and country-clustered SE. The both-instrument rows use the Feyrer and tourism instruments jointly. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_fscont} reports the first stage estimated separately within each continent, with standard errors, which Table~\ref{tab:diag} reports without. The Feyrer instrument is a strong predictor within Africa, Asia, Europe and Latin America, with the sign reversal discussed in Section~\ref{sec:diag}, and is uninformative within North America, the Middle East and Oceania. The tourism instrument is the mirror image: it is strong within Latin America, Oceania and North America and weak within Africa and Europe. No continent has a strong first stage for both instruments, so the over-identification test in Table~\ref{tab:robust} draws its power from between-continent variation.

\begin{table}[H]\centering\caption{First stage estimated separately by continent.}\label{tab:a_fscont}
\begin{threeparttable}\small\input{tables_appendix/tabA_fs_cont}
\begin{tablenotes}\footnotesize\item Coefficient of the instrument on $\ln\mathrm{GACI}_{max}$ with country and year fixed effects and log population; robust SE in parentheses. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_loocy} drops one continent at a time under continent by year fixed effects, which is the specification preferred in Section~\ref{sec:diag}. The market-Gini estimate stays between $0.27$ and $1.06$ and is significant in six of the seven cases; the exception is dropping Asia, where the first stage collapses to $F=1.4$. Dropping Europe raises the estimate to $1.06$ on a first stage of $F=4.7$. The disposable-Gini estimate is significant only when Europe or Latin America is dropped, which is the same fragility reported in Section~\ref{sec:diag}.

\begin{table}[H]\centering\caption{Leave-one-continent-out under continent by year fixed effects (Feyrer instrument).}\label{tab:a_loocy}
\begin{threeparttable}\small\input{tables_appendix/tabA_loo_contyear}
\begin{tablenotes}\footnotesize\item Robust SE in parentheses. Country and continent by year fixed effects and log population. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_rfq} reports the coefficients plotted in Figure~\ref{fig:rfq}. The reduced form is positive and significant in the second, fourth and fifth quintiles of baseline inequality and not distinguishable from zero in the first and third. By baseline income it is positive and significant in the first four quintiles and zero in the richest. The association is therefore not driven by the richest or by the most unequal economies.

\begin{table}[H]\centering\caption{Reduced form of the Feyrer instrument on the market Gini, by baseline quintile.}\label{tab:a_rfq}
\begin{threeparttable}\small\input{tables_appendix/tabA_rfq}
\begin{tablenotes}\footnotesize\item Country and year fixed effects and log population within each quintile; robust SE in parentheses. Quintiles are fixed at each country's first observed year. These are the coefficients plotted in Figure~\ref{fig:rfq}. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

"""

ANCHOR_B = "%=======================================================================\n\\section{Timing and instrument diagnostics}"
ANCHOR_C = "%=======================================================================\n\\section{Country-level quantities}"

for anchor, block in [(ANCHOR_B, A_ADD), (ANCHOR_C, B_ADD)]:
    if t.count(anchor) != 1:
        print("anchor problem:", anchor[:60], t.count(anchor)); sys.exit(1)
    t = t.replace(anchor, block.rstrip() + "\n\n" + anchor, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("appendix extended with 6 tables")
