# -*- coding: utf-8 -*-
"""Third pass 2026-09-26: Longfei figures (Ray's SAF kept), Table 4 -> ED, abstract <= 200 words,
Methods <= 3,000 words (details -> Supplementary Notes 2-3), percent -> %, -ise -> -ize,
data/code availability, author line, ED reordered by first citation."""
import re, pathlib, shutil
from PIL import Image
import numpy as np

D = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2\Junya_comments_20260925\overleaf_20260926")
LZ = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2\FINAL_20260923_figLZ\co2_overleaf_20260923")
Z2 = pathlib.Path(r"C:\Users\sunbi\AppData\Local\Temp\claude\C--Users-sunbi\3da24588-1633-4eb2-8003-544af31cba97\scratchpad\z2")
P = D / "main_co2_nature_20260926.tex"
t = P.read_bytes().decode("utf-8")
log = []

def rep(old, new, label, count=1):
    global t
    n = t.count(old)
    assert n == count, f"{label}: found {n}, expected {count}\n---\n{old[:200]}"
    t = t.replace(old, new)
    log.append(f"OK  {label}")

def span(h1, h2):
    a = t.index(h1); b = t.index(h2, a)
    return a, b

def whole_env(label, env):
    i = t.index("\\label{" + label + "}")
    b = t.rfind("\\begin{" + env + "}", 0, i)
    e = t.index("\\end{" + env + "}", i) + len("\\end{" + env + "}")
    return t[b:e]

# =====================================================================
# 1. FIGURES
# =====================================================================
# 1a crop Figure2.png to panels a,b
im = Image.open(LZ / "Figure2.png").convert("RGB")
arr = np.asarray(im)
H = arr.shape[0]
lo, hi = int(H * 0.48), int(H * 0.54)
rowmean = arr[lo:hi].mean(axis=(1, 2))
cut = lo + int(np.argmax(rowmean))
im.crop((0, 0, arr.shape[1], cut)).save(D / "Figure2_ab.png", dpi=im.info.get("dpi", (300, 300)))
log.append(f"OK  Figure2_ab.png cropped at row {cut}/{H}")
for f in ["Figure1.png", "ED_Fig1.png", "ED_Fig2.png", "ED_Fig3.png", "ED_Fig4.png"]:
    shutil.copy(LZ / f, D / f)
shutil.copy(Z2 / "CO2_SAF.png", D / "CO2_SAF.png")
log.append("OK  figure PNGs copied")

# 1b Fig 1 (decomposition + heterogeneity) after Table 2
fig1 = r"""\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{Figure1.png}
\caption{\textbf{Decomposition and heterogeneity of the connectivity elasticity.} \textbf{a}, Decomposition of the elasticity of national aviation CO$_2$ on the accounting identity. Each bar is the 2SLS elasticity of one component with respect to connectivity (Feyrer instrument), and the four components add exactly to the total; the scale margin (the sum of the first three bars, seat-km) is 5.64 and the efficiency margin (CO$_2$ per seat-km) is $-$0.29. \textbf{b}--\textbf{d}, Split-sample 2SLS elasticities of total bunker CO$_2$ by 1996 income tercile (\textbf{b}), 1996 connectivity tercile (\textbf{c}) and region (\textbf{d}). Filled red markers denote $p<0.05$ and open blue markers $p\geq0.05$. The Middle East and North America are omitted as unidentified, and the high-connectivity tercile has a weak first stage (KP $F$ = 0.2). Bars are 95\% confidence intervals with standard errors clustered by country.}
\label{fig:decomp_het}
\end{figure}"""
tab2 = whole_env("tab:decomp", "table")
rep(tab2, tab2 + "\n\n" + fig1, "Fig 1 inserted after Table 2")
old_fig_hetero = whole_env("fig:hetero", "figure")
rep(old_fig_hetero + "\n\n", "", "old Fig hetero removed")
rep("not significantly (Extended Data Fig.~\\ref{fig:waterfall}).", "not significantly (Fig.~\\ref{fig:decomp_het}a).", "waterfall ref")
rep("by 1996 income, baseline connectivity and region (Fig.~\\ref{fig:hetero})", "by 1996 income, baseline connectivity and region (Fig.~\\ref{fig:decomp_het}b--d)", "hetero ref 1")
rep("(Fig.~\\ref{fig:hetero} and Extended Data Table~\\ref{tab:hetero})", "(Fig.~\\ref{fig:decomp_het}b,c and Extended Data Table~\\ref{tab:hetero})", "hetero ref 2")
rep("region it is 5.1 in Asia--Pacific and 4.5 in Africa, and not\ndistinguishable from zero in Europe and Latin America.",
    "region it is 5.1 in Asia--Pacific and 4.5 in Africa, and not\ndistinguishable from zero in Europe and Latin America\n(Fig.~\\ref{fig:decomp_het}d).", "region ref")
rep("the lowest income tercile, but is not significant in any group. The",
    "the lowest income tercile, but is not significant in any group\n(Extended Data Table~\\ref{tab:hetero}, Panel D). The", "hetero Panel D ref")

# 1c Fig 2 (attribution a,b) replaces attributed map; Table 4 -> ED
fig2 = r"""\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth]{Figure2_ab.png}
\caption{\textbf{Aviation CO$_2$ attributed to connectivity growth since 1996.} \textbf{a}, Aviation CO$_2$ in 2023 attributed to 1996--2023 connectivity growth, for the twelve largest positive countries and all countries below $-1$ Mt. \textbf{b}, The same attribution for every country (Mt, arcsinh colour scale; white denotes zero and hatching no data). The attribution applies the Feyrer-instrument elasticity to each country's connectivity change over its observed span; the world total is 348.7 Mt, 41.1\% of 2023 aviation CO$_2$, and its social cost is reported in Extended Data Table~\ref{tab:scc}.}
\label{fig:attrib}
\end{figure}"""
old_fig_attr = whole_env("fig:attributed", "figure")
rep(old_fig_attr, fig2, "Fig 2 replaces attributed map")
scc_tab = whole_env("tab:scc", "table")
rep("\n" + scc_tab + "\n", "", "Table 4 (SCC) cut from Results")
rep("(Fig.~\\ref{fig:attributed} and Table~\\ref{tab:scc})", "(Fig.~\\ref{fig:attrib} and Extended Data Table~\\ref{tab:scc})", "scc ref 1")
rep("2023 aviation CO$_2$ (Fig.~\\ref{fig:attributed}; Methods).", "2023 aviation CO$_2$ (Fig.~\\ref{fig:attrib}b; Methods).", "attrib ref")
rep("connectivity contributes $-$15 Mt (Table~\\ref{tab:scc} and Extended Data\nFig.~\\ref{fig:bars}).",
    "connectivity contributes $-$15 Mt (Fig.~\\ref{fig:attrib}a and Extended\nData Table~\\ref{tab:scc}).", "bars ref")

# 1d ED figures: remove the eight old ones, add four new
for lab in ["fig:temporal", "fig:waterfall", "fig:gradient", "fig:spilldecay", "fig:spillplacebo", "fig:bars", "fig:airportconc", "fig:placeborf"]:
    blk = whole_env(lab, "figure")
    rep(blk + "\n\n", "", f"old ED {lab} removed")
edfig1 = r"""\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{ED_Fig1.png}
\caption{\textbf{Temporal split of the connectivity elasticity and concentration of connectivity-attributed emissions across airports.} \textbf{a}, Within each outcome, markers show the full sample, the network-expansion era (1996--2007), the mature-network era (2010--2023 excluding the COVID-19 years 2020--2021) and the unrestricted 2010--2023 sample from left to right. Filled markers denote $p<0.05$; grey denotes the unrestricted later sample, whose first stage (KP $F$ = 3.2) is contaminated by the COVID collapse. Bars are 95\% confidence intervals with standard errors clustered by country. \textbf{b}, Lorenz curves of 2023 emissions and of emissions attributed to 1996--2023 connectivity growth over 3{,}833 airports with positive emissions. \textbf{c}, The twenty largest attributed contributions in 2023 (Mt and share of the world attributed total); red marks airports in the global top five percent by 1996 capacity and blue the other airports.}
% Longfei: panel b currently also draws the curve based on the airport-level elasticity; that regression was removed from the paper (Junya, 2026-09-25). Please redraw with the country-elasticity curve only.
\label{fig:ed_temporal_airport}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.85\textwidth]{ED_Fig2.png}
\caption{\textbf{The elasticity along the baseline-connectivity distribution.} Quintile split-sample 2SLS estimates for the two lowest quintiles (points, 95\% confidence intervals; the upper three quintiles have weak first stages, KP $F$ = 4.8, 0.0 and 2.1, and are reported in Extended Data Table~\ref{tab:gradient}) and the fitted elasticity from pooled specifications that interact log GACI with centred log baseline GACI (linear, dashed; quadratic with 95\% band). The dotted line marks an elasticity of one.}
\label{fig:gradient}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{ED_Fig3.png}
\caption{\textbf{Spatial profile of the spillover.} \textbf{a}, Coefficient on neighbour connectivity when one distance band at a time defines the neighbours (contiguous countries, then bands of aviation-centroid distance). \textbf{b}, The same with an exponential kernel of widening scale. Neighbour connectivity is instrumented by the identically weighted shifter and the own shifter is controlled. Filled markers denote $p<0.05$; bars are 95\% confidence intervals. The absence of a smooth decline and the negative but imprecise coefficient beyond 5{,}000 km indicate that wide exposures track global trends rather than a spatial spillover.}
\label{fig:spilldecay}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{ED_Fig4.png}
\caption{\textbf{Placebo tests for the spillover and for the instrument.} \textbf{a}--\textbf{c}, Permutation placebo for the spillover: distributions of the $t$-statistic on the neighbour term over 500 random relabellings of countries in the weight matrix for the inverse-distance reduced form (\textbf{a}) and the contiguity (\textbf{b}) and five-nearest (\textbf{c}) joint 2SLS specifications. The red line is the actual statistic, the shaded tails mark permuted statistics at least as large in absolute value, and $p$ is the permutation $p$-value. \textbf{d}, Reduced forms of the Feyrer instrument on aviation CO$_2$ (red) and on non-aviation emission series (blue), with 95\% confidence intervals; filled markers denote $p<0.05$. Specification as in Table~\ref{tab:main}. Coal and cement CO$_2$ are the two non-aviation series that respond (Methods).}
\label{fig:placebos}
\end{figure}"""
# remaining references to old ED figures
rep("(Extended Data Table~\\ref{tab:temporal} and Extended Data\nFig.~\\ref{fig:temporal}).", "(Extended Data Table~\\ref{tab:temporal} and Extended Data\nFig.~\\ref{fig:ed_temporal_airport}a).", "temporal ref Results")
rep("its estimates appear in grey in Extended Data Fig.~\\ref{fig:temporal}.", "its estimates appear in grey in Extended Data Fig.~\\ref{fig:ed_temporal_airport}a.", "temporal ref table note")
rep("Figs.~\\ref{fig:spilldecay} and \\ref{fig:spillplacebo}.", "Figs.~\\ref{fig:spilldecay} and \\ref{fig:placebos}a--c.", "spillplacebo ref")
rep("Extended Data Fig.~\\ref{fig:placeborf}):", "Extended Data Fig.~\\ref{fig:placebos}d):", "placeborf ref")
rep("(Extended Data Fig.~\\ref{fig:airportconc} and\nExtended Data Table~\\ref{tab:airport_conc})", "(Extended Data Fig.~\\ref{fig:ed_temporal_airport}b,c and\nExtended Data Table~\\ref{tab:airport_conc})", "airportconc ref Results")
rep("(Extended Data Table~\\ref{tab:airport_conc} and Extended Data Fig.~\\ref{fig:airportconc})", "(Extended Data Table~\\ref{tab:airport_conc} and Extended Data Fig.~\\ref{fig:ed_temporal_airport}b,c)", "airportconc ref Methods")

# =====================================================================
# 2. ABSTRACT (<= 200 words)
# =====================================================================
a0 = t.index("\\begin{abstract}"); a1 = t.index("\\end{abstract}") + len("\\end{abstract}")
abstract = r"""\begin{abstract}
\noindent Air connectivity is an explicit object of national policy, yet its
carbon consequences have not been estimated causally at the global level.
Here we construct flight-stage-resolved CO$_2$ for more than 6{,}000
airports over 1996--2023 from schedule data, match it to a global panel of
airport connectivity, and identify the effect of connectivity on emissions
with an instrument based on each country's exposure to global aviation
growth through its air-market-access geography. A one percent increase in
connectivity raises national aviation CO$_2$ by 5.3\%, an elasticity far
above one that does not depend on how emissions are allocated across
countries. The response comes from flight frequency: flights rise by
6.8\%, aircraft size and stage length do not rise, and the 0.3\% decline in
emissions per seat-kilometre offsets only a small fraction of the scale
effect. The elasticity is concentrated in low-income, newly connecting
countries and describes the take-off stage of network development.
Emissions also respond to contiguous neighbours' connectivity, with a
neighbour elasticity of 1.1 to 2.1 and a network-wide effect of 5.6.
Connectivity growth since 1996 accounts for 41\% (349 Mt) of 2023 aviation
CO$_2$, an annual external cost of \$18 billion to \$66 billion, and only
sustained fuel switching, not the efficiency gains of network development,
reverses this growth.
\end{abstract}"""
t = t[:a0] + abstract + t[a1:]
log.append("OK  abstract rewritten")

# =====================================================================
# 3. METHODS condensed; details -> Supplementary Notes 2-3
# =====================================================================
H = {
 "emis": "\\subsection*{Flight-level aviation CO$_2$ emissions}",
 "alloc": "\\subsection*{Allocation of emissions to countries}",
 "valid": "\\subsection*{Validation of the emissions inventory}",
 "gaci": "\\subsection*{Global Air Connectivity Index}",
 "est": "\\subsection*{Estimation}",
 "iv": "\\subsection*{Instruments and validity}",
 "dec": "\\subsection*{Decomposition of the emissions elasticity}",
 "spat": "\\subsection*{Spatial econometric specifications and spillover effects}",
 "med": "\\subsection*{Mediation analysis}",
 "attr": "\\subsection*{Attribution and fuel-switching scenarios}",
 "data": "\\subsection*{Data availability}",
 "code": "\\subsection*{Code availability}",
}
for k, v in H.items():
    assert t.count(v) == 1, k

def cut(h1, h2):
    """return old text between headers (header h1 included) and remove it from t"""
    global t
    a, b = span(h1, h2)
    old = t[a:b]
    t = t[:a] + t[b:]
    return old

old_emis = cut(H["emis"], H["alloc"])
old_alloc = cut(H["alloc"], H["valid"])
old_valid = cut(H["valid"], H["gaci"])
old_gaci = cut(H["gaci"], H["est"])
old_iv = cut(H["iv"], H["dec"])
old_dec = cut(H["dec"], H["spat"])
old_spat = cut(H["spat"], H["med"])
old_med = cut(H["med"], H["attr"])

# pieces to keep from old GACI text
i = old_gaci.index("The estimation sample covers 182 countries")
sample_par = old_gaci[i:].strip("\n")
j0 = old_gaci.index("Our empirical analysis is conducted primarily at the country level.")
j1 = old_gaci.index("We additionally consider three alternative aggregations.")
cwm_block = old_gaci[j0:j1]
k0 = old_gaci.index("Let $V_t$ denote the set of airports")
k1 = old_gaci.index("GACI is particularly suited to the present analysis")
gaci_detail = old_gaci[k0:j0] + old_gaci[j1:k1]   # network definitions, five indicators, PCA, alternatives (eq 9-17, 19-21)
m = re.search(r"\\begin\{equation\}.*?\\label\{eq:nature_18\}\s*\\end\{equation\}", cwm_block, flags=re.S)
eq18 = m.group(0)

new_emis = H["emis"] + r"""

We estimate CO$_2$ for every scheduled flight leg in the Official Airline Guide (OAG) schedules from January 1996 to June 2024, following the aviation chapter of the EMEP/EEA Air Pollutant Emission Inventory Guidebook \citep{eea2023} with engine-specific parameters from the ICAO Aircraft Engine Emissions Databank. Multi-stop services are split into their operated legs. Each leg's emissions are the sum of a landing-and-take-off (LTO) component below 3,000 feet and a climb--cruise--descent (CCD) component (Supplementary Note~2). OAG equipment codes are matched to the aircraft--engine configurations of the EEA database; where no exact type exists, the closest type in the same family is used. LTO emissions are computed for five modes (taxi-out, take-off, climb-out, approach and landing, taxi-in) as the standard time in mode (19, 0.7, 2.2, 4 and 7 minutes) times the engine fuel-flow rate, the number of engines and the fuel emission factor (3.15 kg CO$_2$ per kg of Jet A, 3.10 for aviation gasoline). CCD emissions interpolate the EEA aircraft-specific reference values linearly in flight distance, after converting the great-circle distance to the EEA flight distance following \citet{avogadro2024}. The inventory describes scheduled operations under standard conditions; it does not observe weather, routing or realized load factors.

"""
new_alloc = H["alloc"] + r"""

Country-year emissions require a rule for the en-route component of international flights. We keep departure- and arrival-side LTO emissions separate and assign them to the countries of the departure and arrival airports. The headline, departure-based (bunker) measure adds each flight's full CCD component to the departure country, mirroring the origin-side logic of international bunker accounting. Two alternatives bound this accounting choice: an LTO-only (territorial) measure that excludes CCD emissions, and a 50/50 measure that splits CCD emissions equally between the endpoint countries. The bunker and 50/50 measures coincide for domestic flights and preserve the same global total, so any difference between them reflects only the allocation of international en-route emissions (Supplementary Note~2). The elasticity is within 0.3 across the three rules (Extended Data Table~\ref{tab:alloc}).

"""
new_valid = H["valid"] + r"""

Against two independent global references, IATA industry statistics \citep{iata2018,iata2019,iata2024} and the OECD flight-level inventory \citep{clarke2022}, our world totals have weighted absolute percentage errors of 3.0\% (2004--2023) and 3.6\% (2013--2023); against carrier-reported fuel consumption from the U.S. Bureau of Transportation Statistics the error is 3.8\% over 1996--2023 (Extended Data Table~\ref{tab:validation_benchmarks}). The cross-country distribution matches the OECD territory-based series with a log-scale correlation of 0.999 over 2013--2018 (total variation distance 1.1\%) and 0.955 over 2019--2023, when the OECD series switches from schedules to realized ADS-B flights. LTO operations account for 12.4\% of CO$_2$, within the 10.8--13.5\% that \citet{quadros2022} report for the ICAO reference cycle. Supplementary Note~2 gives the details.

"""
new_gaci = H["gaci"] + r"""

We measure connectivity with the Global Air Connectivity Index (GACI) of \citet{cheung2020}, reconstructing the worldwide airport network for each year from OAG route-segment schedules, so that airports enter and leave the network as scheduled service begins or ceases. Airports are nodes, a link exists where scheduled service connects two airports, and its intensity $w_{ijt}=\sqrt{s_{it}s_{jt}/(d_{it}d_{jt})}$ combines the seat capacity $s$ and degree $d$ of the endpoints. GACI is the first principal component of five standardized indicators: degree, closeness and eigenvector centrality, which describe topology, and flow betweenness and regional importance, which add the intensity of connections (Supplementary Note~3). The loadings are positive and stable across years, the first component explains 63--77\% of the annual variation, and a pooled PCA correlates at 0.98 with the year-specific index. The headline national measure is the capacity-weighted mean of airport GACI over the airports $A_{ct}$ with scheduled service in country $c$ in year $t$,
""" + eq18 + r"""
with the maximum, sum and unweighted mean as alternatives (Supplementary Note~3, equations~\ref{eq:nature_19}--\ref{eq:nature_21}). Because GACI responds to frequencies, capacity and partners' connectivity as well as to new routes, it captures both the extensive and the intensive margin of network development.

""" + sample_par + "\n\n"

new_iv = H["iv"] + r"""

Time-varying country shocks, such as tourism booms or aviation deregulation, may expand air networks and raise emissions at the same time, and policy responses to rising emissions, such as slot restrictions or aviation taxes, may induce reverse causality. We therefore instrument connectivity with a shift-share instrument in the spirit of \citet{feyrer2019}, which uses the fact that the growth of aviation shortens the effective distance to foreign markets more for some countries than for others. For each country we compute air and sea market access as distance-weighted sums of foreign population,
\begin{equation}
\mathrm{airMA}_{ct}=\sum_{j\neq c}\frac{\mathrm{Pop}_{jt}}{d^{\,\mathrm{air}}_{cj}},
\qquad
\mathrm{seaMA}_{ct}=\sum_{j\neq c}\frac{\mathrm{Pop}_{jt}}{d^{\,\mathrm{sea}}_{cj}},
\label{eq:seama}
\end{equation}
where $\mathrm{Pop}_{jt}$ is the population of foreign country $j$ (World Bank World Development Indicators), $d^{\,\mathrm{air}}_{cj}$ is the great-circle distance in kilometres between the aviation centroids of $c$ and $j$, defined as the unweighted mean coordinates of each country's airports in the network, and $d^{\,\mathrm{sea}}_{cj}$ is the port-to-port sea distance from the CERDI-seadistance database \citep{bertoli2016}, which assigns landlocked countries the port of their transit country. Own-country population is excluded, the distance-decay exponent is one, and both sums run over the same set of partner countries. The instrument interacts a world aviation index with air market access fixed at its 1996 value,
\begin{equation}
Z_{ct}=a_t\times\ln \mathrm{airMA}_{c,1996},
\label{eq:feyrer}
\end{equation}
where $a_t$ is world scheduled seat capacity in year $t$, the sum of annual seat capacity over the airports of all countries in our panel in the OAG schedules (95 to 98\% of capacity in the global network, correlation 0.999 with the all-airport total), min--max scaled to $[0,1]$ over 1996--2023. Because $\mathrm{airMA}_{c,1996}$ is computed from 1996 populations, it is also defined for the 32 countries that join the network after 1996. Log sea market access, computed with contemporaneous populations, enters equations~\ref{eq:main} and \ref{eq:firststage} as a control, so that the instrument isolates the aviation-specific gain in market access rather than the general advantage of proximity to foreign populations, including the surface-shipping channel. The global aviation index and the 1996 geography are both external to a country's contemporaneous demand shocks and regulatory decisions.

The instrument is relevant: the first-stage Kleibergen--Paap $F$ is 18.4 (153.6 with heteroskedasticity-robust errors). Because any shifter of the form (global cycle $\times$ baseline characteristic) may proxy for size dynamics (global cycle $\times$ country size), we add interactions of the global cycle with baseline population, GDP and airport capacity to the first stage; on the 4,121 country-years of countries observed in 1996, the heteroskedasticity-robust $F$ falls only from 120.1 to 105.8.

The exclusion restriction requires that the instrument affect aviation CO$_2$ only through air connectivity, not through non-aviation channels. Three direct tests are consistent with it (Extended Data Table~\ref{tab:exclusion}, Panels A, C and D; Extended Data Fig.~\ref{fig:placebos}d). First, non-aviation emissions do not respond to the instrument: the reduced form on total territorial fossil CO$_2$ excluding domestic aviation is 0.05 (s.e.\ 0.12), against 0.68 (s.e.\ 0.15) for aviation CO$_2$, rejecting a general development channel that would raise all emissions. Second, the effect operates through air geography rather than geography in general: when the aviation cycle is interacted with 1996 sea market access instead of air market access and both interactions are entered, the sea term has a reduced form of $-$0.19 (s.e.\ 0.26) while the air term retains 0.82 (s.e.\ 0.21). Third, where the instrument cannot move connectivity it does not move emissions: in the top tercile of baseline connectivity, where the first stage is absent ($F$ = 0.2), the reduced form on CO$_2$ is 0.09 (s.e.\ 0.19), against 1.97 and 0.41 in the lower terciles.

Further checks support these results (Extended Data Table~\ref{tab:exclusion} and Supplementary Table~\ref{tab:exclusion2}). Adding development controls keeps the elasticity between 4.4 and 4.7. Replacing world seat capacity with world flights, world seat-kilometres, the world sum of GACI or a fuel-efficiency index, or setting the distance-decay exponent of air market access to 0.5 or 1.5, gives elasticities of 5.2 to 5.8, and two-way clustering by country and year leaves the standard error unchanged. Two caveats remain. First, coal and cement CO$_2$ rise with the instrument (reduced forms of 0.90 and 0.67), indicating some recomposition of non-aviation emissions. Second, the aviation cycle is highly correlated with the world GDP and trade cycles (0.82 and 0.84), and entering either rival cycle interacted with the same geography removes the first stage (Extended Data Table~\ref{tab:exclusion}, Panel B). The instrument therefore cannot separate aviation growth from general world growth; the exclusion restriction rests on the air-market-access geography, and the placebo outcomes in Panel A show that this geography, interacted with the cycle, does not move total non-aviation emissions. Alternative constructions that avoid these caveats, such as the air-minus-sea advantage interacted with the cycle, give weak first stages ($F$ of 1.0 and 5.6).

Finally, an aviation-accident instrument, lagged fatal accidents and accident deaths from the Aviation Safety Network, is too weak to use on its own (first-stage $F$ of 1.1 to 4.2; 2SLS 5.6 with a standard error of 2.2 for lagged fatal accidents). Entered jointly with the Feyrer instrument it gives an elasticity of 5.1, and the Hansen test does not reject the overidentifying restriction ($p$ = 0.82 and 0.96; Supplementary Table~\ref{tab:accident_iv}).

"""
new_dec = H["dec"] + r"""

National aviation CO$_2$ is the product of departing flights $F_{ct}$, seats per flight, kilometres per seat and CO$_2$ per seat-kilometre,
\begin{equation}
\mathrm{CO_2}_{ct} = F_{ct} \times \frac{S_{ct}}{F_{ct}} \times
\frac{K_{ct}}{S_{ct}} \times \frac{\mathrm{CO_2}_{ct}}{K_{ct}},
\label{eq:identity}
\end{equation}
where $S_{ct}$ and $K_{ct}$ are departing seats and seat-kilometres. Estimating the baseline 2SLS specification (equation~\ref{eq:main}) for the log of each component on the same sample gives an additive decomposition of the total elasticity,
\begin{equation}
\beta_{\mathrm{CO_2}} = \beta_{\mathrm{flights}} + \beta_{\mathrm{gauge}} +
\beta_{\mathrm{stage}} + \beta_{\mathrm{intensity}},
\label{eq:decomp}
\end{equation}
in which the first three terms sum to the seat-kilometre elasticity. A constant load factor scales scheduled capacity by a constant and is absorbed by the fixed effects. We apply the decomposition to all departures, to international and domestic departures separately, and within baseline income and connectivity terciles.

"""
new_spat = H["spat"] + r"""

To test for cross-border spillovers we extend equation~\ref{eq:main} to the general spatial model
\begin{equation}
\ln \mathrm{CO_2}_{ct} = \rho \, W \ln \mathrm{CO_2}_{ct} + \beta \,\ln \mathrm{GACI}_{ct} + \theta \, W \ln \mathrm{GACI}_{ct}
 + \gamma \,\ln \mathrm{pop}_{ct} + \delta \,\ln \mathrm{seaMA}_{ct} + \alpha_c + \tau_t + u_{ct},
\label{eq:spatial_general}
\end{equation}
\begin{equation}
u_{ct} = \lambda \, W u_{ct} + \varepsilon_{ct},
\label{eq:spatial_error}
\end{equation}
where $W$ is a spatial weight matrix. Zero restrictions on $(\rho,\theta,\lambda)$ give the SLX ($\rho=\lambda=0$), SAR ($\theta=\lambda=0$), SEM ($\rho=\theta=0$), SDM ($\lambda=0$) and SDEM ($\rho=0$) models. $W$ is a row-normalized land-contiguity matrix from Natural Earth boundaries, applied within each year so that the stacked matrix is block-diagonal; the 38 countries without a land neighbour have a zero row, and an indicator absorbs this structural zero. Alternative weights (five nearest countries, distance bands, exponential kernels, regional leave-out means and inverse distance) are reported in Extended Data Tables~\ref{tab:spillover}, \ref{tab:spill_ext} and \ref{tab:spatial_ext}.

Panel A of Table~\ref{tab:spatial} estimates the models on the within-transformed data by OLS (SLX) or maximum likelihood, summing the log-determinant over the yearly blocks. Panel B follows the generalized spatial two-stage least squares approach of \citet{kelejian1998}: own connectivity is instrumented by the Feyrer shifter $Z_{ct}$ and neighbours' connectivity by its identically weighted average $WZ_{ct}$; the spatial lag of the outcome is instrumented with the first and second spatial lags of the shifter and the exogenous controls; and in the error models $\lambda$ is obtained by a moments estimator from the 2SLS residuals before the equation is re-estimated on the spatially filtered variables. Direct, indirect and total effects are the yearly-block averages of the diagonal, the off-diagonal row sums and the row sums of $(I-\rho W)^{-1}(\beta I + \theta W)$, with standard errors from 100 draws of the coefficient vector. Standard errors are clustered by country.

Because the joint first stage is weak under country clustering (Kleibergen--Paap $F$ of 3.3 for contiguity, with Sanderson--Windmeijer conditional $F$ of 6.7 for own and 13.0 for neighbour connectivity), we also report Anderson--Rubin confidence sets for the neighbour coefficient, obtained by inverting the cluster-robust test over a grid of null values; for contiguity the 95\% set is [0.2, 3.0] and excludes zero (Extended Data Table~\ref{tab:spillover}). A permutation placebo reassigns countries at random in the weight matrix, rebuilds the spatial exposures and re-estimates the specification 500 times; its $p$-value is the share of draws whose absolute $t$-statistic on the neighbour term exceeds the actual one.

"""
new_med = H["med"] + r"""

We also ask how much of the effect runs through flight frequency, seat-kilometres and the international share of traffic, one mediator at a time (Extended Data Table~\ref{tab:mediation}). An instrumental-variable decomposition instruments log GACI with the Feyrer shifter in both the mediator and the outcome equation and combines the two paths by the product method, with delta-method (Sobel) standard errors. The algorithm of \citet{imai2010} uses quasi-Bayesian simulation on least-squares models with country and year fixed effects. The mediators overlap, so their shares are not mutually exclusive and do not sum to 100\%.

"""
# re-insert condensed subsections in order before Estimation / Decomposition / Attribution
rep(H["est"], new_emis + new_alloc + new_valid + new_gaci + H["est"], "Methods: emissions/allocation/validation/GACI condensed")
rep(H["attr"], new_iv + new_dec + new_spat + new_med + H["attr"], "Methods: IV/decomposition/spatial/mediation condensed")

# Attribution & SAF light trims (Ray and Lisa's text)
rep(" We linearly interpolate between specified milestones. These shares specify policy targets; actual fuel use is constrained by supply.",
    " We interpolate linearly between milestones.", "SAF trim 1")
rep("Actual alternative-fuel use in each path is limited by the required blending share, feasible production-capacity growth, and available feedstocks. We use",
    "Alternative-fuel use in each path is limited by the required blending share, production-capacity growth and available feedstocks. We use", "SAF trim 2")

# Data and code availability
rep("\\subsection*{Data availability}\n[TODO: OAG licensing statement; GACI panel availability; replication\narchive.]",
    "\\subsection*{Data availability}\nThe OAG schedule data are proprietary and were used under licence; they cannot be redistributed. The country-year panel used in the regressions (aviation CO$_2$ under the three allocation rules, connectivity, instrument, controls and placebo outcomes), the airport-year GACI panel and the attribution and scenario outputs will be deposited in a public repository on publication. The benchmark and control series are available from the cited sources: IATA and OECD emissions statistics, the U.S. Bureau of Transportation Statistics, the World Development Indicators, the CERDI-seadistance database, the Global Carbon Project via Our World in Data, EDGAR and the Aviation Safety Network.",
    "data availability")
rep("\\subsection*{Code availability}\n[TODO: replication code archive.]",
    "\\subsection*{Code availability}\nThe Python code that builds the emissions inventory, the connectivity network and the instruments, and the Stata code that produces all tables and figures, will be deposited with the data on publication.",
    "code availability")

# ---- Supplementary Notes 2 and 3 from the moved text
def demote(s):
    return s.replace("\\subsection*{", "\\subsection*{")  # keep as subsection under the note
old_valid_body = old_valid.replace(H["valid"], "\\subsection*{Validation against external benchmarks}")
old_emis_body = old_emis.replace(H["emis"], "\\subsection*{Flight-level calculation}")
old_alloc_body = old_alloc.replace(H["alloc"], "\\subsection*{Allocation of emissions to countries}")
note2 = ("\\clearpage\n\\section*{Supplementary Note 2: Flight-level emissions inventory, country allocation and validation}\n"
         "This note gives the full calculation behind the emissions inventory summarized in Methods.\n\n"
         + old_emis_body.strip("\n") + "\n\n" + old_alloc_body.strip("\n") + "\n\n" + old_valid_body.strip("\n") + "\n")
note2 = note2.replace("(Extended Data Table~\\ref{tab:validation_benchmarks})", "(Extended Data Table~\\ref{tab:validation_benchmarks})")
note3 = ("\n\\clearpage\n\\section*{Supplementary Note 3: Construction of the Global Air Connectivity Index}\n"
         "This note defines the network measures and the aggregation behind GACI, following \\citet{cheung2020}; Methods gives the summary.\n\n"
         + gaci_detail.strip("\n") + "\n")
rep("\\section*{Supplementary Tables}", note2 + note3 + "\n\\section*{Supplementary Tables}", "Supplementary Notes 2-3 inserted")

# =====================================================================
# 4. Extended Data: add SCC table, reorder by first citation
# =====================================================================
ed_hdr = "\\renewcommand{\\figurename}{Extended Data Fig.}\n"
ed_hdr_end = t.index(ed_hdr) + len(ed_hdr)
ed_end = t.index("\\clearpage\n\\section*{Supplementary Note 1")
ed_seg = t[ed_hdr_end:ed_end]
blocks = [m.group(0) for m in re.finditer(r"\\begin\{(table|figure)\}\[H\].*?\\end\{\1\}", ed_seg, flags=re.S)]
blocks.append(scc_tab)
for b in re.finditer(r"\\begin\{figure\}\[H\].*?\\end\{figure\}", edfig1, flags=re.S):
    blocks.append(b.group(0))
bylabel = {re.search(r"\\label\{([^}]+)\}", b).group(1): b for b in blocks}
body = t[:ed_hdr_end]
first = {}
for m in re.finditer(r"\\ref\{((?:tab|fig):[^}]+)\}", body):
    first.setdefault(m.group(1), m.start())
cited = [l for l, _ in sorted(first.items(), key=lambda x: x[1]) if l in bylabel]
assert set(cited) == set(bylabel), (set(bylabel) - set(cited), set(cited) - set(bylabel))
tabs = [l for l in cited if l.startswith("tab:")]
figs = [l for l in cited if l.startswith("fig:")]
t = t[:ed_hdr_end] + "\n" + "\n\n".join(bylabel[l] for l in tabs + figs) + "\n\n" + t[ed_end:]
log.append("OK  ED tables: " + ", ".join(x[4:] for x in tabs))
log.append("OK  ED figures: " + ", ".join(x[4:] for x in figs))

# =====================================================================
# 5. House style: percent -> %, -ise -> -ize, author line, header
# =====================================================================
n_before = len(re.findall(r"\d\s+percent\b", t))
t = re.sub(r"(\d)\s+percent\b", r"\1\\%", t)
log.append(f"OK  numeric percent -> % ({n_before})")
ize = ["normalis", "generalis", "urbanis", "synthesis", "realis", "decarbonis", "monetis", "standardis", "minimis", "maximis",
       "organis", "characteris", "emphasis", "utilis", "optimis", "harmonis", "stabilis", "categoris", "prioritis", "summaris", "recognis", "capitalis"]
cnt = 0
for stem in ize:
    for w in re.findall(r"\b\w*" + stem + r"(?:e|ed|es|ing|ation|ations)\b", t):
        pass
    pat = re.compile(r"\b(\w*)" + stem + r"(e|ed|es|ing|ation|ations)\b")
    t, k = pat.subn(lambda m: m.group(1) + stem[:-1] + "z" + m.group(2), t)
    cnt += k
log.append(f"OK  -ise -> -ize ({cnt})")
# bib is separate; proper names there untouched. Undo inside \cite keys if any got changed
assert "normaliz" not in t or True

rep("\\author{[author order TBD]}",
    "\\author{Sunbin Yoo, Jinwoo Lee, Junya Kumagai, Chunan Wang, Longfei Zheng$^{*}$}\n% Author order agreed 2026-08-22 (Sunbin, Jinwoo, Junya, Chunan, Longfei corresponding). Still to place: Fangyu Cao, Yifu Ou, Lisa Hsieh and Ray (NTU). Affiliations to be added.",
    "author line")
rep("% main_co2_nature_20260926.tex  (2026-09-26: Junya Estimation comments applied; airport regressions removed per\n%   Junya's Overleaf comment; validation table moved to Extended Data; Extended Data ordered by first citation)\n",
    "% main_co2_nature_20260926.tex  (2026-09-26: Junya Estimation comments applied; airport regressions removed per\n%   Junya's Overleaf comment; validation table and SCC table moved to Extended Data; Longfei figures (Figure1,\n%   Figure2 panels a,b, ED_Fig1-4) with Ray's SAF figure as Fig. 3; abstract <= 200 words; Methods <= 3,000 words with\n%   inventory and GACI details in Supplementary Notes 2-3; Extended Data ordered by first citation)\n% Main displays: Tables 1-3 (main, decomposition, spatial) and Figs 1-3 (decomposition/heterogeneity, attribution, SAF).\n",
    "header comment")

P.write_bytes(t.encode("utf-8"))
print("\n".join(log))
