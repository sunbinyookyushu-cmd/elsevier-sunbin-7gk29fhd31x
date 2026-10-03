# -*- coding: utf-8 -*-
# Inserts the growth (GDP) results beside the distribution results in the v2 draft.
# Adds one main subsection with two tables and five appendix tables, plus cross references.
import io, os, shutil

SRC = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
MAIN = os.path.join(SRC, "main_inequality_v2.tex")
APPX = os.path.join(SRC, "appendix_inequality_v2.tex")

for f, bak in [(MAIN, "_bak_main_inequality_v2_pregrowth.tex"), (APPX, "_bak_appendix_inequality_v2_pregrowth.tex")]:
    b = os.path.join(SRC, bak)
    if not os.path.exists(b):
        shutil.copy2(f, b)


def rd(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)


tex = rd(MAIN)
app = rd(APPX)

GROWTH = r"""\subsection{Growth and its incidence}
\label{sec:growth}
Does hub connectivity also move average income, and if so, who receives the increase? This matters for reading Table~\ref{tab:main}: a rising Gini that accompanies broad income growth is a different object from a rising Gini in which the bottom half stands still. Table~\ref{tab:growth} reports the specifications of Table~\ref{tab:main} with growth outcomes, and Table~\ref{tab:growth_decomp} separates the response of each group's average income into a level term that both groups share and a share term that they do not.

Average income moves with connectivity, and by more than any distribution estimate in this paper. In OLS a one-percent increase in hub connectivity accompanies a $0.75$ percent increase in GDP per capita, and in 2SLS with the Feyrer instrument the elasticity is $1.29$. The World Inequality Database measure of average pretax income per adult, which is built from national accounts rather than from the World Development Indicators, gives $0.67$ and $1.22$ in the same specifications, so the two income sources agree on the sign and on the order of magnitude.

The increase is not shared evenly. Under the Feyrer instrument the average income of the top decile rises by $1.44$ percent per percent of connectivity, the average income of the bottom half by $0.45$ percent, and the ratio between the two by $1.00$ percent. Table~\ref{tab:growth_decomp} shows where the difference arises. Both groups carry the same level term of $1.22$. The top decile adds a share gain of $0.22$ and the bottom half subtracts a share loss of $0.77$, which is the estimate already reported in Table~\ref{tab:tails}. The bottom half therefore retains about one third of the average gain. Consider an economy whose hub connectivity rises by ten percent. Average income rises by about twelve percent, the average income of the top decile by about fourteen percent and that of the bottom half by about four percent, while the market Gini rises by about five percent of its own value, which is $2.3$ points at the sample mean of $45.6$. Growth and the rise in the Gini are two readings of one movement rather than two separate findings.

The growth estimates are less robust than the distribution estimates, and three results set the limit. First, the tourism-heritage instrument, which reproduces the market-Gini estimate of the Feyrer instrument ($0.47$ against $0.50$), gives $-0.13$ for GDP per capita and cannot be distinguished from zero; with both instruments entered together the Hansen test rejects for GDP per capita ($p=0.002$), for average income ($p<0.001$) and for the top decile ($p=0.004$), but not for the top-to-bottom ratio ($p=0.33$). Second, under continent by year fixed effects the level estimates turn negative, $-1.07$ for GDP per capita and $-1.68$ for the bottom half, while the ratio remains positive at $1.21$ and significant (Table~\ref{tab:a_growth_diag}). Third, in long differences the instrument is uninformative for growth as it is for inequality, with a first-stage $F$ below $3$ in every window (Table~\ref{tab:a_growth_ld}), and the leads are as large as the lags (Table~\ref{tab:a_growth_hzn}). What survives these checks is the incidence rather than the level, so we treat the level estimates as descriptive and the gap estimates as the result.

One feature of the construction separates the two halves of Table~\ref{tab:growth_decomp}. The Gini coefficients and the income shares are distribution statistics and do not use national income in their construction, so their co-movement with GDP per capita is an estimate rather than an identity. The group average incomes in the last three columns of Table~\ref{tab:growth} do share a national-accounts level term by construction, and that term is what row 1 of Table~\ref{tab:growth_decomp} isolates and the ratio removes.

\begin{table}[H]\centering\caption{Growth outcomes: GDP per capita and group average incomes.}\label{tab:growth}
\begin{threeparttable}\small\input{tables/tab_growth}
\begin{tablenotes}\footnotesize\item GDP per capita is World Development Indicators output in constant 2015 US dollars. Average incomes are World Inequality Database pretax national income per equal-split adult aged 20 and over, in constant local currency, so country fixed effects absorb the currency unit. Robust SE in parentheses, country-clustered SE in brackets with the corresponding significance level. Log population and country and year fixed effects throughout. Panel D enters both instruments; the Hansen row reports the over-identification test. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

\begin{table}[H]\centering\caption{Incidence of the income gain: level and share components (hub connectivity).}\label{tab:growth_decomp}
\begin{threeparttable}\small\input{tables/tab_growth_decomp}
\begin{tablenotes}\footnotesize\item The rows are an accounting identity: the log average income of a group equals the log average income of all adults plus the log of the group's income share, up to a group-specific constant that the fixed effects absorb. Row 1 is therefore common to both columns and row 2 carries the distribution. Row 2 repeats the share estimates of Table~\ref{tab:tails}. The Gini and the income shares do not use national income in their construction; the group average incomes do. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

"""

anchor = r"\subsection{Heterogeneity by development, initial inequality and period}"
assert tex.count(anchor) == 1
tex = tex.replace(anchor, GROWTH + anchor)

# cross reference from the mechanism section back to the growth table
old = r"Hub connectivity raises GDP per capita (elasticity $1.29$)"
assert tex.count(old) == 1
tex = tex.replace(old, r"Hub connectivity raises GDP per capita (elasticity $1.29$, Table~\ref{tab:growth})")

# abstract
old = ("Connectivity raises GDP per capita, industrial employment and urbanisation, "
       "each of which is associated with lower inequality, so the residual association exceeds the total.")
assert tex.count(old) == 1
new = old + (" Measured in income levels rather than shares, the same movement raises the average income of the "
             "top decile by about three times that of the bottom half, and the level estimates, unlike the ratio "
             "between the two, survive neither continent by year fixed effects nor the second instrument.")
tex = tex.replace(old, new)

# synthesis, second hypothesis paragraph
old = ("The distributional response to connectivity is a widening between the upper-middle of the distribution "
       "and the bottom half rather than an increase at the very top.")
assert tex.count(old) == 1
new = old + (" Measured in levels, the same result is an average income gain of which the bottom half retains about "
             "one third, and the ratio of top-decile to bottom-half average income is the one growth quantity that "
             "survives the continent by year and over-identification checks.")
tex = tex.replace(old, new)

wr(MAIN, tex)

APPENDIX_ADD = r"""
\section{Growth outcomes}
\label{app:growth}
Table~\ref{tab:a_growth_diag} subjects the growth estimates of Table~\ref{tab:growth} to the diagnostics that Section~\ref{sec:diag} applies to the inequality estimates. Under continent by year fixed effects the level estimates change sign, to $-1.07$ for GDP per capita and $-1.68$ for the average income of the bottom half, and dropping Latin America moves them further negative. The top-to-bottom ratio is the exception: it remains positive at $1.21$ and significant under the same fixed effects, and it also survives the exposure-trend and combined controls. Under the tourism-heritage instrument none of the level estimates is distinguishable from zero. The pattern supports reading the incidence rather than the level as the result.

\begin{table}[H]\centering\caption{Identification diagnostics for the growth outcomes.}\label{tab:a_growth_diag}
\begin{threeparttable}\small\input{tables_appendix/tabA_growth_diag}
\begin{tablenotes}\footnotesize\item Each cell is a separate 2SLS estimate of the coefficient on $\ln\mathrm{GACI}_{max}$ with log population and the stated fixed effects. Robust SE in parentheses. The exposure rows interact each country's baseline income, baseline Gini, land area and absolute latitude with the global aviation index. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_growth_hzn} reports the growth outcomes with connectivity lagged and led. The level estimates rise with the horizon, from $1.29$ at $k=0$ to $1.73$ at $k=10$ for GDP per capita and from $0.45$ to $1.93$ for the bottom half, so the gap between the two groups closes at long horizons and is near zero by $k=9$. The leads are as large as the contemporaneous estimates and the five-year lead is larger, which is the same persistence pattern that Table~\ref{tab:a_leads} reports for the Gini and which prevents a causal timing reading.

\begin{table}[H]\centering\caption{Growth outcomes with lagged and led connectivity.}\label{tab:a_growth_hzn}
\begin{threeparttable}\small\input{tables_appendix/tabA_growth_horizon}
\begin{tablenotes}\footnotesize\item Each row is a separate 2SLS estimate in which connectivity and the instrument are lagged or led by the stated number of years. Robust SE in parentheses. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_growth_ld} reports the long-difference and stacked-difference designs for the growth outcomes. The OLS long differences are positive in every window, between $0.59$ and $0.92$ for GDP per capita and between $0.21$ and $1.10$ for the bottom half, and the implied gap is positive in four of the five windows. The instrumented versions are uninformative: the first-stage $F$ is below $3$ in every window and below $1$ in four of them, which reproduces the result of Table~\ref{tab:a_longdiff} for the Gini. The stacked five-year differences behave the same way: the OLS estimates are about $0.41$ for both groups with no gap between them, while the instrumented versions rest on a first-stage $F$ of $0.001$ and return coefficients in the hundreds, which are not interpretable. We therefore report the long differences as descriptive.

\begin{table}[H]\centering\caption{Long differences and stacked differences, growth outcomes.}\label{tab:a_growth_ld}
\begin{threeparttable}\small\input{tables_appendix/tabA_growth_longdiff}
\begin{tablenotes}\footnotesize\item Long differences are cross sections of country changes between the stated years with continent fixed effects and the change in log population. KP $F$ is reported for the GDP per capita column; the instrument is the change in the Feyrer interaction. Robust SE in parentheses. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_growth_het} reports how the growth estimates vary across groups. The level response falls monotonically with baseline income, from $2.69$ in the low tercile to $0.38$ in the high tercile for GDP per capita, and the bottom-half response turns negative in the high tercile ($-0.43$) while the top-decile response stays positive ($0.56$). The response is smaller after 2010 for both groups, and the reduction is larger for the top decile. By continent the level response is positive in Africa, Asia and Latin America and negative in Europe, and the Oceania estimates rest on a first stage too weak to interpret. The control battery leaves the GDP per capita estimate between $1.26$ and $1.47$ and the bottom-half estimate between $-0.17$ and $0.60$, so the bottom-half estimate is the less stable of the two.

\begin{table}[H]\centering\caption{Growth outcomes: heterogeneity and control sensitivity.}\label{tab:a_growth_het}
\begin{threeparttable}\small\input{tables_appendix/tabA_growth_hetero}
\begin{tablenotes}\footnotesize\item Panels A and B are interaction 2SLS in which both connectivity and the instrument are interacted with fixed baseline group indicators; total rows are linear combinations. Panel C reports separate 2SLS by continent. Panel D reports the GDP per capita and bottom-half estimates under added controls. Robust SE in parentheses. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}

Table~\ref{tab:a_growth_cond} reports the inequality equation with GDP per capita entered as a control, which is the suppressor result of Section~\ref{sec:mech} in table form. Conditional on measured income per head, the hub coefficient rises from $0.50$ to $0.75$ for the market Gini and from $0.65$ to $0.97$ for the disposable Gini, and income per head itself carries a negative coefficient in both equations. The association between connectivity and inequality is therefore not an artefact of the income growth that accompanies it.

\begin{table}[H]\centering\caption{Inequality conditional on measured income per head (2SLS, Feyrer instrument).}\label{tab:a_growth_cond}
\begin{threeparttable}\small\input{tables_appendix/tabA_growth_condgdp}
\begin{tablenotes}\footnotesize\item Hub connectivity is instrumented; GDP per capita enters as an exogenous control. Robust SE in parentheses. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.\end{tablenotes}\end{threeparttable}\end{table}
"""

anchor2 = r"\section*{Data and code availability}"
assert app.count(anchor2) == 1
app = app.replace(anchor2, APPENDIX_ADD.strip() + "\n\n" + anchor2)
wr(APPX, app)

print("main chars :", len(tex))
print("appx chars :", len(app))
print("new inputs :", tex.count("tables/tab_growth"), app.count("tables_appendix/tabA_growth"))
