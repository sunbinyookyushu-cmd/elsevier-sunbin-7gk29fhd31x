# -*- coding: utf-8 -*-
"""build_tex_2024.py -- rewrite TRA_rev20260902/main.tex to the 1996-2024 sample (Stata-confirmed numbers).
Every replacement asserts its expected match count; whitespace inside `old` matches any whitespace/newlines."""
import re, pathlib
G = pathlib.Path(__file__).parent.parent
SRC = G / "TRA_rev20260902" / "main.tex"; OUT = G / "TRA_rev20260902_ext2024" / "main.tex"
OUT.parent.mkdir(exist_ok=True)
t = SRC.read_text(encoding="utf-8")
log = []
def R(old, new, count=1):
    global t
    pat = re.compile(r"\s+".join(re.escape(p) for p in old.split()))
    n = len(pat.findall(t)); assert n == count, (f"expected {count}, found {n}: {old[:90]}")
    t = pat.sub(lambda m: new, t); log.append((old[:60], n))

# ---------------- header / title / abstract ------------------------------------------------------
R(r"%  Global Air Connectivity and Trade Openness, 1996-2023", r"%  Global Air Connectivity and Trade Openness, 1996-2024")
R(r"1996-2023 unified, Fig.2 re-rendered", "1996-2023 unified, Fig.2 re-rendered\n%  Rev 2026-09-02b: sample extended to 1996-2024 (Stata-confirmed), all tables/figures/aggregates updated")
R(r"\title{Global Air Connectivity and Trade Openness, 1996--2023}", r"\title{Global Air Connectivity and Trade Openness, 1996--2024}")
R(r"using a panel of 184 countries over 1996--2023.", r"using a panel of 185 countries over 1996--2024.")
R(r"yields a goods-trade-volume elasticity of $2.30$, which decomposes exactly into a trade-openness elasticity of $1.30$ and a GDP-scale elasticity of $1.00$.",
  r"yields a goods-trade-volume elasticity of $2.13$, which decomposes exactly into a trade-openness elasticity of $1.21$ and a GDP-scale elasticity of $0.92$.")
R(r"connectivity shifts the trade mix toward high value-to-weight goods and, more tentatively, intermediate goods, the margins on which air transport operates,",
  r"connectivity shifts the trade mix toward high value-to-weight goods and intermediate goods, the margins on which air transport operates,")

# ---------------- introduction / literature -------------------------------------------------------
R(r"for each year from 1996 to 2023, covering between 3{,}171 and 3{,}833 active airports per year, and aggregate the airport-level scores into a country-year panel of 184 countries.",
  r"for each year from 1996 to 2024, covering between 3{,}171 and 3{,}863 active airports per year, and aggregate the airport-level scores into a country-year panel of 185 countries.")
R(r"During 1996--2023, the number of active airports connected to the global aviation network increased from 3{,}171 to 3{,}833.",
  r"During 1996--2024, the number of active airports connected to the global aviation network increased from 3{,}171 to 3{,}863.")
R(r"(between 3{,}171 and 3{,}833 airports per year over the sample period)", r"(between 3{,}171 and 3{,}863 airports per year over the sample period)")
R(r"indicators in our 1996--2023 panel yields", r"indicators in our 1996--2024 panel yields")

# ---------------- Figure 2 caption (2024 endpoint) -------------------------------------------------
old_cap = t[t.index(r"\caption{Rank trajectories implied by the index, 1996--2023."):t.index(r"\label{fig:gaci_rankings}")]
new_cap = r"""\caption{Rank trajectories implied by the index, 1996--2024. Panel (a):
airport-level GACI rank, for the fifteen highest-ranked airports of 2024;
panel (b): country-level hub quality ($\mathrm{GACI}_{cwm}$) rank, for the
fifteen highest-ranked countries of 2024. Country ranks are computed from
the full airport network (all economies with scheduled service), so data
availability in the estimation sample plays no role. Ranks beyond 20 are
drawn on a compressed scale below the dashed divider. Highlighted
trajectories mark entrants from outside the top 20 in 1996, with the number
of places gained shown next to the 2024 label; Shanghai Pudong (PVG) and
Incheon (ICN), both dashed, did not operate in 1996 and enter at their first
available cross-section (2000 and 2005). The rise of Gulf, Turkish, and East
Asian hubs (Dubai, Istanbul, Shanghai, Beijing, Guangzhou, Incheon; the
United Arab Emirates, Qatar, Turkey, Korea, Saudi Arabia) concentrates after
2010, consistent with the temporal placement of the identifying variation
documented in Section~\ref{sec:temporal}.}
"""
t = t.replace(old_cap, new_cap)

# ---------------- data section ---------------------------------------------------------------------
R(r"1996--2019; extended to 2020--2023 with UNWTO figures", r"1996--2019; extended to 2020--2024 with UNWTO figures")
old_sample = t[t.index(r"\paragraph{\textbf{Sample}} An unbalanced panel of 184 countries"):t.index("so the regressions use 4{,}642 observations.") + len("so the regressions use 4{,}642 observations.")]
new_sample = (r"\paragraph{\textbf{Sample}} An unbalanced panel of 185 countries observed annually from 1996 to 2024, with 4{,}816 of the $185\times29=5{,}365$ possible country-year observations. 131 of the 185 countries are observed in all 29"
 "\nyears. The gaps arise almost entirely from missing WDI merchandise-trade or\nGDP entries, concentrated in small island economies and conflict-affected\nstates, with a residual handful of country-years in which no scheduled air\nservice operated (for example, Iraq in 1996--2004); coverage in 2024, the most\nrecent WDI release, is thinner (155 countries). Two countries (Moldova and New\nCaledonia) enter with a single observation, which the country fixed effect\nabsorbs, so the regressions use 4{,}814 observations.")
t = t.replace(old_sample, new_sample)
R(r"the most heritage-rich holds eighteen.", r"the most heritage-rich holds nineteen.")
R(r"maps the 2023 cross-section of the index", r"maps the 2024 cross-section of the index")
R(r"\caption{Summary statistics, estimation sample (184 countries, 1996--2023).}", r"\caption{Summary statistics, estimation sample (185 countries, 1996--2024).}")
old_rows = t[t.index(r"\multicolumn{7}{l}{\emph{Connectivity}}\\"):t.index(r"Remoteness, mean sea distance (km) & 4635 & 10{,}800 & 1{,}815 & 7{,}811 & 10{,}592 & 15{,}297 \\") + len(r"Remoteness, mean sea distance (km) & 4635 & 10{,}800 & 1{,}815 & 7{,}811 & 10{,}592 & 15{,}297 \\")]
new_rows = r"""\multicolumn{7}{l}{\emph{Connectivity}}\\
Hub quality, $\mathrm{GACI}_{cwm}$ (cap.-wtd.\ mean index) & 4816 & 1.09 & 0.40 & 0.53 & 0.99 & 3.13 \\
Total connectivity, $\mathrm{GACI}_{sum}$ (index) & 4816 & 14.36 & 41.96 & 0.55 & 4.07 & 510.04 \\
Number of airports & 4816 & 19.40 & 52.74 & 1.00 & 5.00 & 614.00 \\
\addlinespace
\multicolumn{7}{l}{\emph{Trade outcomes}}\\
Goods-trade volume (billion USD) & 4816 & 169.2 & 477.1 & 0.04 & 16.9 & 6{,}250.9 \\
Goods trade (\% of GDP) & 4816 & 65.90 & 43.89 & 7.81 & 55.60 & 420.68 \\
\addlinespace
\multicolumn{7}{l}{\emph{Income}}\\
GDP per capita (USD) & 4816 & 14{,}091 & 19{,}306 & 227 & 5{,}072 & 122{,}118 \\
GDP (billion USD) & 4816 & 384.1 & 1{,}626.7 & 0.06 & 29.2 & 28{,}751.0 \\
\addlinespace
\multicolumn{7}{l}{\emph{Instrument and heritage}}\\
Tourism-heritage instrument & 4816 & 0.43 & 0.48 & 0.00 & 0.36 & 3.00 \\
Natural + mixed UNESCO sites (cum.) & 4816 & 1.38 & 2.35 & 0.00 & 1.00 & 19.00 \\
\addlinespace
\multicolumn{7}{l}{\emph{Controls}}\\
Population (million) & 4816 & 39.57 & 145.01 & 0.01 & 8.46 & 1{,}450.94 \\
Land area (thousand km$^2$) & 4816 & 748.1 & 1{,}963.6 & 0.02 & 155.4 & 16{,}388.5 \\
Remoteness, mean sea distance (km) & 4808 & 10{,}778 & 1{,}830 & 7{,}773 & 10{,}586 & 15{,}320 \\"""
t = t.replace(old_rows, new_rows)
R(r"\caption{Air connectivity (GACI) levels, 2023. Yellow = highly connected", r"\caption{Air connectivity (GACI) levels, 2024. Yellow = highly connected")
R(r"the aggregate contribution of GACI to trade over the period 1996--2023.", r"the aggregate contribution of GACI to trade over the period 1996--2024.")

# ---------------- main results text ---------------------------------------------------------------
R(r"the expected positive sign ($0.032$, $p<0.01$), and the Kleibergen--Paap statistic ($F=18.0$) sits comfortably",
  r"the expected positive sign ($0.034$, $p<0.01$), and the Kleibergen--Paap statistic ($F=21.9$) sits comfortably")
R(r"raises trade volume by about $2.3\%$ ($p<0.01$).", r"raises trade volume by about $2.1\%$ ($p<0.01$).")
R(r"rises by about $1.3\%$ ($p<0.05$), and GDP rises by about $1.0\%$, although", r"rises by about $1.2\%$ ($p<0.05$), and GDP rises by about $0.9\%$, although")
R(r"enters the first stage at $0.044$ ($p<0.01$) with a Kleibergen--Paap statistic of $27.4$, the highest",
  r"enters the first stage at $0.046$ ($p<0.01$) with a Kleibergen--Paap statistic of $33.0$, the highest")
R(r"trade volume rising by about $1.7\%$ ($p<0.01$) and openness by about $1.0\%$ ($p<0.05$)",
  r"trade volume rising by about $1.6\%$ ($p<0.01$) and openness by about $0.9\%$ ($p<0.05$)")
R(r"first stage is the weakest of the three ($F=9.7$)", r"first stage is the weakest of the three ($F=11.0$)")
# Table 1
R(r"First stage: instrument coef. & \multicolumn{3}{l}{0.032\sym{***}\ \ (0.007),\ \ KP $F=18.0$} \\", r"First stage: instrument coef. & \multicolumn{3}{l}{0.034\sym{***}\ \ (0.007),\ \ KP $F=21.9$} \\")
R(r"OLS & 0.157\sym{***} & 1.144\sym{***} & 0.987\sym{***} \\", r"OLS & 0.167\sym{***} & 1.141\sym{***} & 0.975\sym{***} \\")
R(r"1.302\sym{**} & 2.303\sym{***} & 1.001 \\", r"1.208\sym{**} & 2.126\sym{***} & 0.919 \\", count=2)   # Table 1 + Conley
R(r"& (0.662) & (0.776) & (0.680) \\", r"& (0.593) & (0.703) & (0.624) \\", count=2)
R(r"\multicolumn{3}{l}{0.044\sym{***}\ \ (0.008),\ \ KP $F=27.4$} \\", r"\multicolumn{3}{l}{0.046\sym{***}\ \ (0.008),\ \ KP $F=33.0$} \\")
R(r"OLS & 0.103\sym{**} & 1.083\sym{***} & 0.980\sym{***} \\", r"OLS & 0.112\sym{***} & 1.075\sym{***} & 0.963\sym{***} \\")
R(r"2SLS & 0.966\sym{**} & 1.709\sym{***} & 0.743 \\", r"2SLS & 0.897\sym{**} & 1.580\sym{***} & 0.683 \\")
R(r"& (0.469) & (0.548) & (0.507) \\", r"& (0.423) & (0.503) & (0.467) \\")
R(r"\multicolumn{3}{l}{0.064\sym{***}\ \ (0.020),\ \ KP $F=9.7$} \\", r"\multicolumn{3}{l}{0.065\sym{***}\ \ (0.020),\ \ KP $F=11.0$} \\")
R(r"OLS & -0.027 & 0.237\sym{***} & 0.264\sym{***} \\", r"OLS & -0.025 & 0.239\sym{***} & 0.263\sym{***} \\")
R(r"2SLS & 0.659\sym{*} & 1.166\sym{***} & 0.507 \\", r"2SLS & 0.635\sym{*} & 1.119\sym{***} & 0.483 \\")
R(r"& (0.365) & (0.432) & (0.341) \\", r"& (0.342) & (0.404) & (0.323) \\")
R(r"Observations & 4{,}642 & 4{,}642 & 4{,}642 \\", r"Observations & 4{,}814 & 4{,}814 & 4{,}814 \\", count=3)  # main, temporal, conley
R(r"Observations & 4{,}642 & 4{,}642 & 4{,}642 & 4{,}642 & 4{,}642 \\", r"Observations & 4{,}814 & 4{,}814 & 4{,}814 & 4{,}814 & 4{,}814 \\")

# ---------------- heterogeneity --------------------------------------------------------------------
R(r"interacted first stages are weaker (KP $F\approx5$--$9$), so we read", r"interacted first stages are weaker (KP $F\approx6$--$11$), so we read")
R(r"strong (KP $F=18.0$, Table~\ref{tab:main}); what the weaker", r"strong (KP $F=21.9$, Table~\ref{tab:main}); what the weaker")
R(r"$\ln\mathrm{GACI}_{cwm}$ (at mean) & 1.254\sym{*} & 2.260\sym{*} & 1.391\sym{**} \\", r"$\ln\mathrm{GACI}_{cwm}$ (at mean)   & 1.139\sym{*}  & 2.014\sym{**} & 1.300\sym{**} \\")
R(r"& (0.717) & (1.161) & (0.693) \\", r"                         & (0.644)       & (0.986)       & (0.623) \\")
R(r"$\times$ moderator & $-0.243$\sym{**} & $-1.482$\sym{**} & $-1.241$\sym{*} \\", r"$\times$ moderator       & $-0.214$\sym{**} & $-1.335$\sym{**} & $-1.137$\sym{*} \\")
R(r"& (0.122) & (0.622) & (0.673) \\", r"                         & (0.108)       & (0.524)       & (0.587) \\")
R(r"$\ln\mathrm{GACI}_{cwm}$ (at mean) & 1.959\sym{***} & 6.093\sym{***} & 2.394\sym{***} \\", r"$\ln\mathrm{GACI}_{cwm}$ (at mean)   & 1.718\sym{**} & 5.584\sym{***} & 2.214\sym{***} \\")
R(r"& (0.732) & (1.742) & (0.825) \\", r"                         & (0.675)       & (1.436)       & (0.749) \\")
R(r"$\times$ moderator & $-1.108$\sym{***} & $-6.060$\sym{***} & $-1.234$ \\", r"$\times$ moderator       & $-1.095$\sym{***} & $-5.852$\sym{***} & $-1.068$ \\")
R(r"& (0.131) & (1.046) & (0.815) \\", r"                         & (0.117)       & (0.863)       & (0.733) \\")
R(r"$\ln\mathrm{GACI}_{cwm}$ (at mean) & 0.705 & 3.834\sym{***} & 1.003 \\", r"$\ln\mathrm{GACI}_{cwm}$ (at mean)   & 0.580         & 3.570\sym{***} & 0.914 \\")
R(r"& (0.759) & (1.133) & (0.708) \\", r"                         & (0.706)       & (0.972)       & (0.650) \\")
R(r"$\times$ moderator & $-0.865$\sym{***} & $-4.579$\sym{***} & 0.007 \\", r"$\times$ moderator       & $-0.881$\sym{***} & $-4.517$\sym{***} & 0.070 \\")
R(r"& (0.119) & (0.677) & (0.755) \\", r"                         & (0.109)       & (0.573)       & (0.702) \\")
R(r"First-stage KP $F$ & 8.07 & 4.96 & 9.21 \\", r"First-stage KP $F$       & 9.69          & 6.34          & 11.03 \\")
R(r"Observations & 4{,}121 & 4{,}121 & 4{,}635 \\", r"Observations             & 4{,}284       & 4{,}284       & 4{,}806 \\")
R(r"less-connected economies; KP $F$ is modest ($\approx5$--$9$), so the gradient is", r"less-connected economies; KP $F$ is modest ($\approx6$--$11$), so the gradient is")
R(r"income and connectivity moderators require observation in 1996 (4{,}121), and sea distance is unavailable for a handful of economies (4{,}635).",
  r"income and connectivity moderators require observation in 1996 (4{,}284), and sea distance is unavailable for a handful of economies (4{,}806).")
R(r"from about $1.7$ to $0.8$ across income quartiles and from about $2.7$ to $1.7$ across connectivity quartiles",
  r"from about $1.5$ to $0.7$ across income quartiles and from about $2.4$ to $1.5$ across connectivity quartiles")

# ---------------- temporal -------------------------------------------------------------------------
R(r"of the 1996--2023 sample (Table~\ref{tab:temporal}).", r"of the 1996--2024 sample (Table~\ref{tab:temporal}).")
R(r"strength as the interacted specifications above (KP $F=6.2$).", r"strength as the interacted specifications above (KP $F=7.3$).")
R(r"first-stage KP $F$ at $0.29$ before 2010 and $27.7$ afterwards", r"first-stage KP $F$ at $0.34$ before 2010 and $31.6$ afterwards")
R(r"throughout ($F<5$) and the post-2010 interaction for volume positive and significant at the 1~percent level throughout ($0.24$--$0.54$).",
  r"throughout ($F<4$) and the post-2010 interaction for volume positive and significant throughout ($0.23$--$0.54$; at the 1~percent level in every split year up to 2012 and at the 5~percent level in 2013).")
R(r"$\ln\mathrm{GACI}_{cwm}$ (pre-2010) & 1.247 & 0.496 & $-0.751$ \\", r"$\ln\mathrm{GACI}_{cwm}$ (pre-2010) & 1.140   & 0.390   & $-0.750$ \\")
R(r"& (0.771) & (0.877) & (0.983) \\", r"                        & (0.698) & (0.819) & (0.908) \\")
R(r"$\times$ post-2010 & 0.012 & 0.377\sym{***} & 0.366\sym{***} \\", r"$\times$ post-2010      & 0.014   & 0.373\sym{***} & 0.359\sym{***} \\")
R(r"& (0.076) & (0.088) & (0.091) \\", r"                        & (0.076) & (0.089) & (0.091) \\")
R(r"First-stage KP $F$ & 6.22 & 6.22 & 6.22 \\", r"First-stage KP $F$      & 7.27 & 7.27 & 7.27 \\")
R(r"instrument is essentially irrelevant before 2010 (KP $F=0.29$) and strong afterwards ($F=27.7$), so identification",
  r"instrument is essentially irrelevant before 2010 (KP $F=0.34$) and strong afterwards ($F=31.6$), so identification")

# ---------------- mechanism ------------------------------------------------------------------------
R(r"a rise in hub quality shifts trade toward high value-to-weight goods (column (4): $1.71$, $p<0.05$), directly supporting \textbf{Hypothesis~2}, and the shift toward intermediate goods points the same way (column (2): $1.12$, s.e.\ $0.69$), consistent in sign with \textbf{Hypothesis~3} but not statistically significant at conventional levels.",
  r"a rise in hub quality shifts trade toward high value-to-weight goods (column (4): $1.87$, $p<0.01$), directly supporting \textbf{Hypothesis~2}, and toward intermediate goods (column (2): $1.48$, $p<0.05$), supporting \textbf{Hypothesis~3}.")
R(r"The connectivity coefficient falls from $1.27$ in column (1) to $1.09$ when the intermediates ratio enters (column (3)) and to $1.00$, no longer statistically distinguishable from zero, when both ratios enter (column (6)).",
  r"The connectivity coefficient falls from $1.18$ in column (1) to $0.94$, no longer statistically distinguishable from zero, when the intermediates ratio enters (column (3)), and to $0.83$ when both ratios enter (column (6)).")
R(r"(column (6): $0.173$, $p<0.01$ and $0.047$, $p<0.05$)", r"(column (6): $0.171$, $p<0.01$ and $0.052$, $p<0.01$)")
R(r"\textbf{Hypothesis~3} receives qualified support: the shift toward intermediates is imprecisely estimated in the first step, but the intermediates ratio is the single strongest absorber of the openness effect in the second, which is the pattern the value-chain channel requires.",
  r"\textbf{Hypothesis~3} is likewise supported: the shift toward intermediates is significant in the first step, and the intermediates ratio is the single strongest absorber of the openness effect in the second, which is the pattern the value-chain channel requires.")
R(r"\caption{Mechanism: connectivity, trade composition, and openness, 2SLS, 1996--2023.}", "\\caption{Mechanism: connectivity, trade composition, and openness, 2SLS,\n1996--2024.}")
R(r"$\ln\mathrm{GACI}_{cwm}$ & 1.268\sym{*} & 1.116 & 1.086\sym{*} & 1.714\sym{**} & 1.247\sym{*} & 0.996 \\", r"$\ln\mathrm{GACI}_{cwm}$ & 1.176\sym{**} & 1.483\sym{**} & 0.939 & 1.868\sym{***} & 1.144\sym{*} & 0.825 \\")
R(r"& (0.656) & (0.693) & (0.638) & (0.753) & (0.668) & (0.649) \\", r" & (0.588) & (0.653) & (0.571) & (0.716) & (0.599) & (0.583) \\")
R(r"ln(Interm./Consum.) & & & 0.163\sym{***} & & & 0.173\sym{***} \\", r"ln(Interm./Consum.) &  &  & 0.160\sym{***} &  &  & 0.171\sym{***} \\")
R(r"ln(High/Low VW) & & & & & 0.012 & 0.047\sym{**} \\", r"ln(High/Low VW) &  &  &  &  & 0.017 & 0.052\sym{***} \\")
R(r"& & & & & (0.021) & (0.020) \\", r" &  &  &  &  & (0.021) & (0.019) \\")
R(r"First-stage KP $F$ & 18.1 & 18.1 & 17.7 & 18.1 & 17.5 & 16.9 \\", r"First-stage KP $F$ & 22.1 & 22.1 & 21.2 & 22.1 & 21.1 & 19.9 \\")
R(r"Observations & 4{,}614 & 4{,}614 & 4{,}614 & 4{,}614 & 4{,}614 & 4{,}614 \\", r"Observations & 4{,}785 & 4{,}785 & 4{,}785 & 4{,}785 & 4{,}785 & 4{,}785 \\")

# ---------------- aggregate ------------------------------------------------------------------------
R(r"\subsection{Aggregate contribution of connectivity growth, 1996--2023}", r"\subsection{Aggregate contribution of connectivity growth, 1996--2024}")
R(r"it lets the contribution of two decades of global aviation connectivity growth be compared", r"it lets the contribution of nearly three decades of global aviation connectivity growth be compared")
R(r"how much of its 2023 trade is attributable to that country's own 1996--2023 rise in hub quality", r"how much of its 2024 trade is attributable to that country's own 1996--2024 rise in hub quality")
R(r"with $\beta=1.302$, so the implied gain", r"with $\beta=1.208$, so the implied gain")
R(r"about \textbf{\$7.8 trillion} of 2023 trade, roughly \textbf{17\%} of 2023 world trade (\$47 trillion) and \textbf{7.4\%} of 2023 world GDP, equivalently raising world trade openness by about 7.4 percentage points of GDP.",
  r"about \textbf{\$10 trillion} of 2024 trade, roughly \textbf{21\%} of 2024 world trade (\$47 trillion) and \textbf{9.2\%} of 2024 world GDP, equivalently raising world trade openness by about 9.2 percentage points of GDP.")
R(r"($\beta\in[0.00,\,2.60]$) to the same calculation yields an attributable-trade range of \$0.03--12.4 trillion. The volume-channel counterpart ($\beta\in[0.78,\,3.82]$) is \$5.1--14.9 trillion. Across the three connectivity measures the point estimate spans \$6.8--7.8 trillion on the openness channel",
  r"($\beta\in[0.05,\,2.37]$) to the same calculation yields an attributable-trade range of \$0.5--15.9 trillion. The volume-channel counterpart ($\beta\in[0.75,\,3.50]$) is \$6.7--19.4 trillion. Across the three connectivity measures the point estimate spans \$8.0--10.0 trillion on the openness channel")
R(r"shows these gains accrue most to the Middle East (Gulf hubs) and Asia (China), which pull away from the rest after 2005.",
  r"shows these gains accrue most to Asia (China) and the Middle East (Gulf hubs), which pull away from the rest after 2005.")
R(r"channel, $\beta=1.302$).}", r"channel, $\beta=1.208$).}")
R(r"the openness channel attributes \$6.8--7.8 trillion of 2023 goods trade (14.5--16.5\% of the world total), and the volume channel \$10.2--11.5 trillion (21.6--24.6\%), regardless of measure.",
  r"the openness channel attributes \$8.0--10.0 trillion of 2024 goods trade (17.2--21.4\% of the world total), and the volume channel \$10.4--14.9 trillion (22.3--32.0\%), regardless of measure.")
R(r"implies a further \$9.8--13.2 trillion.", r"implies a further \$13.8--17.4 trillion.")
R(r"which alone accounts for roughly \$2.1 trillion of 2023 trade on the headline measure, followed by Korea, the United Arab Emirates, Japan, and Turkey.",
  r"which alone accounts for roughly \$2.7 trillion of 2024 trade on the headline measure, followed by Korea, the United Arab Emirates, Japan, and the United States.")
R(r"Third, the totals are net figures: 42 to 60 of the 184 countries, depending on the measure, experienced falling connectivity over the period",
  r"Third, the totals are net figures: 18 to 34 of the 185 countries, depending on the measure, experienced falling connectivity over the period")
R(r"\caption{Aggregate contribution of aviation-connectivity growth, 1996--2023, under three connectivity measures.}", "\\caption{Aggregate contribution of aviation-connectivity growth, 1996--2024, under\nthree connectivity measures.}")
R(r"$\mathrm{GACI}_{cwm}$ (headline) & 1.302 & 7.8\ (16.5) & 2.303 & 11.5\ (24.6) & 1.001 & 13.2\ (12.6) \\", r"$\mathrm{GACI}_{cwm}$ (headline) & 1.208 & 10.0\ (21.4) & 2.126 & 14.9\ (32.0) & 0.919 & 17.4\ (16.1) \\")
R(r"$\mathrm{GACI}_{max}$ & 0.966 & 6.8\ (14.5) & 1.709 & 10.2\ (21.6) & 0.743 & \phantom{0}9.8\ (\phantom{0}9.4) \\", r"$\mathrm{GACI}_{max}$ & 0.897 & \phantom{0}8.9\ (19.0) & 1.580 & 13.3\ (28.6) & 0.683 & 14.1\ (13.0) \\")
R(r"$\mathrm{GACI}_{sum}$ & 0.659 & 7.5\ (16.0) & 1.166 & 10.5\ (22.4) & 0.507 & 13.0\ (12.5) \\", r"$\mathrm{GACI}_{sum}$ & 0.635 & \phantom{0}8.0\ (17.2) & 1.119 & 10.4\ (22.3) & 0.483 & 13.8\ (12.8) \\")
R(r"$\sum_i \text{level}_i(2023)\times[1-\exp(-\beta\,\Delta\ln\mathrm{GACI}_i)]$, where", r"$\sum_i \text{level}_i(2024)\times[1-\exp(-\beta\,\Delta\ln\mathrm{GACI}_i)]$, where")
R(r"country's 1996--2023 change in that measure.", r"country's 1996--2024 change in that measure.")
R(r"World bases are 2023 goods trade (\$46.9~trillion) and GDP (\$104.6~trillion);", r"World bases are 2024 goods trade (\$46.6~trillion) and GDP (\$108.2~trillion);")
R(r"1996--2023 (openness channel), under the three connectivity measures. Red denotes", r"1996--2024 (openness channel), under the three connectivity measures. Red denotes")
R(r"a sizeable minority of countries (42--60 of 184, depending on the measure) saw connectivity fall", r"a minority of countries (18--34 of 185, depending on the measure) saw connectivity fall")

# ---------------- COVID ----------------------------------------------------------------------------
R(r"implying a one-year goods-trade disruption of about \$7.5 trillion, roughly 20\% of 2019 world trade; the maximum-hub measure implies \$6.7 trillion (18\%), and total connectivity \$1.8 trillion (4.8\%).",
  r"implying a one-year goods-trade disruption of about \$7.1 trillion, roughly 19\% of 2019 world trade; the maximum-hub measure implies \$6.3 trillion (17\%), and total connectivity \$1.7 trillion (4.6\%).")
R(r"smallest openness elasticity ($0.659$ against $1.302$ for hub quality)", r"smallest openness elasticity ($0.635$ against $1.208$ for hub quality)")
R(r"ranges from \$2.5 trillion (total connectivity) to \$13.2 trillion (hub quality), about 3 to 15\% of 2019 world GDP",
  r"ranges from \$2.4 trillion (total connectivity) to \$12.3 trillion (hub quality), about 3 to 14\% of 2019 world GDP")
R(r"producing implied trade disruption of \$1.8--7.5 trillion across", r"producing implied trade disruption of \$1.7--7.1 trillion across")

# ---------------- synthesis / discussion / conclusion ----------------------------------------------
R(r"volume with an elasticity of $2.30$ and trade openness with an elasticity of $1.30$ (Table~\ref{tab:main})",
  r"volume with an elasticity of $2.13$ and trade openness with an elasticity of $1.21$ (Table~\ref{tab:main})")
R(r"\textbf{Hypothesis~3}, that connectivity raises intermediate-goods trade relative to final consumption goods, receives partial support: the estimated shift toward intermediates is positive but not statistically significant at conventional levels, yet the intermediates ratio is the strongest single absorber of the openness effect, a pattern consistent with, though not conclusive for, the value-chain channel.",
  r"\textbf{Hypothesis~3}, that connectivity raises intermediate-goods trade relative to final consumption goods, is supported: connectivity shifts the trade mix toward intermediate goods (Table~\ref{tab:mechanism}, column (2)), and the intermediates ratio is the strongest single absorber of the openness effect, the pattern the value-chain channel requires.")
R(r"connectivity tilts the trade mix toward high value-to-weight goods and, with less precision, intermediate goods, and this shift carries the openness effect.",
  r"connectivity tilts the trade mix toward high value-to-weight goods and intermediate goods, and this shift carries the openness effect.")
R(r"implies an elasticity of trade openness of $1.30$, and the positive relationship", r"implies an elasticity of trade openness of $1.21$, and the positive relationship")
R(r"Evidence for the global-value-chain channel is more tentative. The estimated shift toward intermediate goods is positive but not statistically significant at conventional levels. In addition, the reduction",
  r"The global-value-chain channel is also supported: connectivity shifts the trade mix toward intermediate goods, although this estimate is less precise than the unit-value margin. In addition, the reduction")
R(r"attributes approximately \$7.8 trillion of 2023 goods trade to changes in hub quality since 1996,", r"attributes approximately \$10 trillion of 2024 goods trade to changes in hub quality since 1996,")
R(r"we estimate a goods-volume elasticity of $2.30$ (an openness elasticity of $1.30$ plus a GDP-scale elasticity of $1.00$) that",
  r"we estimate a goods-volume elasticity of $2.13$ (an openness elasticity of $1.21$ plus a GDP-scale elasticity of $0.92$) that")
R(r"toward high value-to-weight and, more tentatively, intermediate goods, and this compositional shift carries the openness effect.",
  r"toward high value-to-weight and intermediate goods, and this compositional shift carries the openness effect.")
R(r"under-connected economies, and two decades of connectivity growth account for on the order of \$7.8 trillion of 2023 goods trade.",
  r"under-connected economies, and nearly three decades of connectivity growth account for on the order of \$10 trillion of 2024 goods trade.")

# ---------------- appendix: controls, battery, Conley, RF ------------------------------------------
R(r"$1.66$ with no controls, $1.30$ with population (the baseline), $1.71$ with GDP, $1.64$ with both, and $1.43$ with population and GDP per capita, always significant at the 5 per cent level, with the first stage strong throughout (KP $F=15.1$--$20.9$).",
  r"$1.52$ with no controls, $1.21$ with population (the baseline), $1.54$ with GDP, $1.51$ with both, and $1.34$ with population and GDP per capita, always significant at the 5 per cent level, with the first stage strong throughout (KP $F=18.9$--$24.5$).")
R(r"$\ln\mathrm{GACI}_{cwm}$ & 1.663\sym{**} & 1.302\sym{**} & 1.706\sym{**} & 1.642\sym{**} & 1.430\sym{**} \\", r"$\ln\mathrm{GACI}_{cwm}$ & 1.516\sym{**} & 1.208\sym{**} & 1.540\sym{**} & 1.505\sym{**} & 1.340\sym{**} \\")
R(r"& (0.775) & (0.662) & (0.688) & (0.686) & (0.704) \\", r" & (0.675) & (0.593) & (0.601) & (0.609) & (0.645) \\")
R(r"First-stage KP $F$ & 15.1 & 18.0 & 19.1 & 18.9 & 20.9 \\", r"First-stage KP $F$ & 18.9 & 21.9 & 23.9 & 23.2 & 24.5 \\")
R(r"elasticity is essentially unchanged ($2.18$, $p<0.01$). The first stage is weaker than in the baseline model (KP $F=8.5$),",
  r"elasticity remains positive and precisely estimated ($1.90$, $p<0.01$). The first stage is weaker than in the baseline model (KP $F=10.5$),")
R(r"Hansen $J$ to rejection for the volume outcome ($p=0.004$) and collapses", r"Hansen $J$ to rejection for the volume outcome ($p=0.008$) and collapses")
R(r"Used alone it delivers a volume elasticity of $2.26$ ($p<0.01$); combined with the tourism-heritage instrument, the two instruments deliver statistically indistinguishable estimates on the volume channel ($\hat\beta=2.25$, Hansen $J$ $p=0.95$).",
  r"Used alone it delivers a volume elasticity of $2.30$ ($p<0.01$); combined with the tourism-heritage instrument, the two instruments deliver statistically indistinguishable estimates on the volume channel ($\hat\beta=2.26$, Hansen $J$ $p=0.69$).")
R(r"relevance before 2010 (KP $F=0.3$) and is strong afterwards ($F=27.7$);", r"relevance before 2010 (KP $F=0.3$) and is strong afterwards ($F=31.6$);")
R(r"for direct effects up to 36 per cent of the reduced form, and even at $\gamma_{\max}$ equal to 30 per cent the interval is $[0.14, 3.83]$. The openness estimate has no such slack, but this is a mechanical consequence of its baseline precision rather than new information about exclusion: its unperturbed 95 per cent interval, $[0.00, 2.60]$, already touches zero, so any positive $\gamma$ moves the lower bound below zero.",
  r"for direct effects up to 36 per cent of the reduced form, and even at $\gamma_{\max}$ equal to 30 per cent the interval is $[0.14, 3.50]$. The openness estimate has far less slack: its lower bound stays positive only for direct effects up to 4 per cent of the reduced form. This is a mechanical consequence of its baseline precision rather than new information about exclusion, since its unperturbed 95 per cent interval, $[0.05, 2.37]$, barely clears zero.")
R(r"(A) Over-ID, nat+mix & $z_{\text{nat}},z_{\text{mix}}$ & 2.178\sym{***} & 8.5 & 0.78 & 4{,}642 \\", r"(A) Over-ID, nat+mix      & $z_{\text{nat}},z_{\text{mix}}$ & 1.900\sym{***} & 10.5 & 0.73 & 4{,}814 \\")
R(r"(B) Add cultural & $+\,z_{\text{cult}}$ & 0.394 & 19.8 & 0.004 & 4{,}642 \\", r"(B) Add cultural          & $+\,z_{\text{cult}}$            & 0.371          & 24.0 & 0.008 & 4{,}814 \\")
R(r"(C) Air/sea distance only & Feyrer-type & 2.257\sym{***} & 153.6 & --- & 4{,}634 \\", r"(C) Air/sea distance only & Feyrer-type                     & 2.304\sym{***} & 160.7 & --- & 4{,}806 \\")
R(r"\quad combined & tourism $+$ Feyrer & 2.249\sym{***} & 97.2 & 0.95 & 4{,}634 \\", r"\quad combined            & tourism $+$ Feyrer              & 2.256\sym{***} & 103.9 & 0.69 & 4{,}806 \\")
R(r"(D) Pre-2010 & tourism-heritage & --- & 0.3 & --- & 2{,}218 \\", r"(D) Pre-2010              & tourism-heritage                & ---            & 0.3 & --- & 2{,}234 \\")
R(r"\quad Post-2010 & tourism-heritage & --- & 27.7 & --- & 2{,}423 \\", r"\quad Post-2010           & tourism-heritage                & ---            & 31.6 & --- & 2{,}579 \\")
R(r"Reduced form $\hat\delta$ & 0.042 & 0.075 & 0.033 \\", r"Reduced form $\hat\delta$       & 0.041         & 0.073          & 0.031 \\")
R(r"UCI, $\gamma_{\max}=10\%$ of RF & $[-0.09,\,2.60]$ & $[0.58,\,3.83]$ & $[-0.44,\,2.33]$ \\", r"UCI, $\gamma_{\max}=10\%$ of RF & $[-0.05,\,2.37]$ & $[0.55,\,3.50]$ & $[-0.41,\,2.14]$ \\")
R(r"UCI, $\gamma_{\max}=20\%$ of RF & $[-0.19,\,2.60]$ & $[0.36,\,3.83]$ & $[-0.56,\,2.33]$ \\", r"UCI, $\gamma_{\max}=20\%$ of RF & $[-0.15,\,2.37]$ & $[0.35,\,3.50]$ & $[-0.51,\,2.14]$ \\")
R(r"UCI, $\gamma_{\max}=30\%$ of RF & $[-0.30,\,2.60]$ & $[0.14,\,3.83]$ & $[-0.67,\,2.33]$ \\", r"UCI, $\gamma_{\max}=30\%$ of RF & $[-0.25,\,2.37]$ & $[0.14,\,3.50]$ & $[-0.61,\,2.14]$ \\")
R(r"Breakdown share $f^{*}$ & 0.00 & 0.36 & --- \\", r"Breakdown share $f^{*}$         & 0.04          & 0.36           & --- \\")
R(r"For openness, $f^{*}=0$ reflects that the unperturbed interval already touches zero; for GDP the baseline estimate is not significant, so no breakdown share is defined.",
  r"For openness, the small $f^{*}$ reflects that the unperturbed interval barely clears zero; for GDP the baseline estimate is not significant, so no breakdown share is defined.")
R(r"from $0.229$ (SE $0.062$) in the bottom quintile to $0.014$ (SE $0.019$) in the top,", r"from $0.234$ (SE $0.058$) in the bottom quintile to $0.016$ (SE $0.018$) in the top,")

# ---------------- appendix: country table ----------------------------------------------------------
R(r"the implied effect of its 1996--2023 connectivity growth on each outcome", r"the implied effect of its 1996--2024 connectivity growth on each outcome")
R(r"\caption{Country-level implied effects of air-connectivity growth, 1996--2023.}", r"\caption{Country-level implied effects of air-connectivity growth, 1996--2024.}")
ctab = (G / "ext2024" / "_country_estimates_table.tex").read_text(encoding="utf-8")
new_body = ctab[ctab.index(r"\multicolumn{6}{l}{\emph{Largest implied trade gains (top 25)}}\\"):ctab.index(r"World total & --- & --- & --- & --- & 10656 \\") + len(r"World total & --- & --- & --- & --- & 10656 \\")]
old_body = t[t.index(r"\multicolumn{6}{l}{\emph{Largest implied trade gains (top 25)}}\\"):t.index(r"World total & --- & --- & --- & --- & 7858 \\") + len(r"World total & --- & --- & --- & --- & 7858 \\")]
t = t.replace(old_body, new_body)
R(r"$\beta_{int}=1.302\,(0.662)$, volume $\beta_{vol}=2.303\,(0.776)$, GDP $\beta_{gdp}=1.001\,(0.680)$)", r"$\beta_{int}=1.208\,(0.593)$, volume $\beta_{vol}=2.126\,(0.703)$, GDP $\beta_{gdp}=0.919\,(0.624)$)")
R(r"World total is summed over all 184 countries; negative", r"World total is summed over all 185 countries; negative")

OUT.write_text(t, encoding="utf-8", newline="\n")
print("written", OUT, "replacements:", len(log))
left = [l[:110] for l in t.splitlines() if ("2023" in l and not l.startswith("@") and "_2023" not in l)]
print("remaining 2023 lines:"); [print("  ", l) for l in left]
left = [l[:110] for l in t.splitlines() if re.search(r"\b184\b", l) and not l.startswith("@")]
print("remaining 184 lines:"); [print("  ", l) for l in left]
for pat in ["1.302", "2.303", "1.001", "7.8 trillion", "4{,}642", "4{,}643", "0.659", "1.166", "0.966", "1.709"]:
    print(pat, "->", sum(1 for l in t.splitlines() if pat in l and not l.startswith("@")))
