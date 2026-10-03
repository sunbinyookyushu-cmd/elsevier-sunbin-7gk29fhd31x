# Connectivity–Resilience Inequality in the Global Aviation Network
## A Multi-Shock, Multi-Component, Co-Evolutionary Panel Analysis (1996–2024)

**Draft date:** 2026-05-15
**Lead:** Sunbin Yoo (Managi Lab)
**Data:** GACI 1996–2024 panel (5,428 airports × 29 years × 7 metrics)

---

## 1. Motivation

One of the most consequential recent findings in urban infrastructure-equity research is that **connectivity and resilience are inversely distributed**. Our previous work (under review at *Nature Cities*) shows that, across the Tokyo Metropolitan area, railway accessibility (number of facilities reachable in a given travel time) and post-earthquake resilience (the share of accessibility retained under a disruption scenario) move in *opposite directions* across socio-spatial groups: high-income, highly-educated, younger urban-core neighborhoods enjoy the highest accessibility but the lowest resilience, while older, suburban, and peri-urban communities show the reverse. The inversion implies a stark trade-off — pursuing efficiency and equity together comes at the cost of resilience.

This proposal asks whether the same inversion holds in a **global system observed under multiple real shocks**, rather than a single city under a single simulated shock. The test bed is an in-lab extension of the **Global Airport Connectivity Index (GACI)** of Cheung, Wong & Zhang (2020, *TR-E*) to a 1996–2024 panel of 5,428 airports (101,049 airport-year observations). Moving from cities to airports gives us simultaneously a **29-year time series, ~10 observed shocks, and 5 distinct centrality components**.

The closest precedents are Wandelt, Zhang & Sun (2024, *TR-D*), who construct a **Global Airport Resilience Index (GARI)** that is (i) *simulation*-based, (ii) limited to a single year (2023), and (iii) collapses resilience to a scalar; and Janić (2022, *Aeronautical Journal*), who formalises the resilience/robustness/vulnerability vocabulary but applies it to only two airports (LHR, JFK) under a single shock (COVID). The present project occupies the gap they leave open: a **global panel, multiple observed shocks, and a multi-dimensional resilience triangle defined on five centrality components**, while building directly on the inversion concept established by our previous work in the urban-rail setting.

## 2. Research Questions

The project is organised around four conceptual levers that go beyond what a single-city, single-shock design can reach.

**RQ1 (Co-evolution).** How have *connectivity inequality* (Gini on GACI) and *resilience inequality* (Gini on Λ) co-evolved across the global airport network between 1996 and 2024? Do the two inequalities move together as mega-hubs rise, or diverge?

**RQ2 (Multi-shock robustness).** Does the inversion documented in our previous work (high-connectivity ↔ low-resilience) hold consistently across shock types — health, financial, geopolitical, natural — or is it confined to certain shock classes?

**RQ3 (Centrality-type fragility mapping).** Which of the five sub-components of GACI (Degree, Eigen, NorClose, NorBetweenness, RegionalImportance) is most strongly tied to resilience loss Λ? This is the first cross-shock attempt to quantify *"which kind of connectivity is the source of fragility."*

**RQ4 (Borrowed centrality / network substitution).** Which airports' GACI actually *rises* during a shock, and is that rise (i) own growth, or (ii) absorbed traffic from collapsing neighboring hubs? Does the sign of substitution-vs-spillover flip across shock types?

## 3. Conceptual Framework — Resilience Triangle on a Five-Component Centrality

For every airport i and every shock s we construct a four-tuple following the established resilience-triangle lineage in engineering and transport-systems research (Bruneau et al., 2003; Cimellaro, Reinhorn & Bruneau, 2010; Reggiani, Nijkamp & Lanzi, 2015; Janić, 2022):

- **R**ᵢₛ (Robustness) = GACIᵢ,trough(s) / GACIᵢ,pre(s) — the share retained at the trough. Follows Bruneau et al. (2003) and Janić (2022) for transport infrastructure.
- **T**ᵢₛ (Rapidity) = years elapsed until GACI returns to 90% of pre-shock level. Standard rapidity definition in Bruneau et al. (2003); Cimellaro et al. (2010) discuss threshold choice.
- **M**ᵢₛ (Memory) = post-recovery new normal / pre-shock normal — whether the airport settles in a new equilibrium. Extends the "permanent loss" concept of Cimellaro et al. (2010, Eq. 5).
- **Λ**ᵢₛ (Triangle area) = ∫[GACIᵢ,pre − GACIᵢ,t] dt — cumulative resilience loss. Direct application of Bruneau et al. (2003) and Cimellaro et al. (2010) "loss-of-resilience" integral to a discrete annual GACI time series.

The tuple (R, T, M, Λ) thus operationalises the **classical resilience triangle** as defined in Bruneau et al. (2003) and formalised analytically by Cimellaro et al. (2010), now applied to airport-level GACI dynamics. Janić (2022) collapsed R × (1/T) into a single scalar; we deliberately retain the **vector representation** so that depth, speed and permanence of disruption can each be examined separately — an approach also recommended in Reggiani et al. (2015) for transport-network resilience.

The decisive conceptual move is to compute the four-tuple **not only for GACI but for each of its five sub-components separately**, producing (Λ^Degree, Λ^Eigen, Λ^Close, Λ^Between, Λ^RegImp) per airport-shock. This lets us draw *fragility profiles* by centrality type.

**Pre-registered hypothesis (RQ3).** Eigenvector centrality should be the most fragile component, because by definition it is proportional to neighbors' importance — when adjacent hubs collapse, the focal airport's eigen-score collapses with them. Degree is the most robust component, because it counts direct ties only; an airport keeps its degree if its own routes survive. Normalized betweenness can paradoxically *increase* during shocks at substitution hubs that take over diverted traffic. Closeness and RegionalImportance should lie in between.

## 4. Methods per RQ

### 4.1 RQ1 — Co-evolution of two inequalities

For each year t we compute Gini^GACI_t over the cross-section of 5,428 airports. For each shock s we compute Gini^Λ_s; between shocks we either carry forward the most recent Λ or use a five-year rolling window. The two series are then subjected to:

- Cross-correlation function (lead–lag structure)
- Granger causality (does rising connectivity concentration *predict* later resilience divergence?)
- Bai–Perron multiple structural-break tests on each series, 1996–2024
- Regression: Gini^Λ_s ~ Gini^GACI_{s−k} + period dummies

### 4.2 RQ2 — Multi-shock robustness

**Shock window definition (locked spec, 2026-05-15).** Pre-shock baseline = `mean(GACI in [t_s − 3, t_s − 1])`, following the 3-year averaging convention used in transport-resilience studies to smooth annual noise (Reggiani et al., 2015). Trough = airport-specific `min(GACI_i in [t_s, t_s + 2])`, allowing heterogeneous shock-propagation speed across regions. Recovery end = first year that GACI ≥ 90% of pre-shock level (90% as main spec, with 80% and 95% as sensitivity); the 90% threshold follows the practical recovery convention used in Cimellaro et al. (2010, §3.2).

**Clean-shock list (main panel, 5 events).** To eliminate pre-window contamination from prior shocks, we restrict the main resilience-triangle panel to shocks whose 3-year pre-window is free of any prior major aviation disruption:

| Shock | Year | Pre-window | Primary region | Type |
|---|---|---|---|---|
| 9/11 | 2001 | 1998–2000 | NA1 | Geopolitical / security |
| SARS | 2003 | 2000–2002 | AS1, AS2 | Health |
| Global Financial Crisis | 2008–09 | 2005–2007 | EU1, NA1, global | Financial |
| Ebola | 2014 | 2011–2013 | AF3, AF4 | Health / regional |
| COVID-19 | 2020 | 2017–2019 | Global | Health |

**Excluded from main panel (overlap with prior shock):** H1N1 2009 (within GFC), Eyjafjallajökull ash 2010, Arab Spring 2011, and Russia sanctions 2014 (all within GFC tail); Russia airspace closure 2022 (within COVID recovery). The Russia 2022 case is **retained as a qualitative case study for RQ4** because it is the canonical observed substitution event: trans-Siberian-detour traffic absorbed by IST and DOH.

For each shock we obtain a 5,428-airport × (R, T, M, Λ) meta-database and classify airports into four quadrants on the (pre-shock GACI, Λ) plane, with axes crossed at their medians:

- Q1: high-GACI, high-resilience (frontier)
- Q2: high-GACI, low-resilience — the *mega-hub fragility* quadrant (the aviation analogue of the urban-core advantaged neighbourhoods identified in our previous work)
- Q3: low-GACI, high-resilience (peripheral safe-havens)
- Q4: low-GACI, low-resilience (doubly disadvantaged)

A pooled meta-regression then quantifies the inversion strength and its shock-type heterogeneity:

Λᵢₛ = α + β · GACIᵢ,pre + Σ γₛ · ShockTypeₛ + δ · GACIᵢ,pre × ShockTypeₛ + Xᵢβ + εᵢₛ

The inversion prediction is β > 0; interaction terms test whether the inversion is uniform across shock classes.

### 4.3 RQ3 — Centrality-type fragility decomposition

The four-tuple is computed *separately* for each of the five components, yielding fragility profiles. Analyses include:

- **Component-wise inequality.** How each component's Gini shifts during shocks — which component's distribution is most reactive to disruption.
- **Cross-component correlation.** How strongly Λ^Eigen co-moves with the other components' Λs, testing whether eigen-collapse is the synchronising signal.
- **Predictive regression.** Λ^GACIᵢₛ = Σₖ θₖ · Componentᵢ,pre^k + Xᵢβ + ε, with the pre-registered ordering θ_Eigen > θ_Degree.
- **Shapley decomposition.** Variance of Λ^GACI attributed to each component's contribution.
- **Heatmap visualisation.** An (airport × component) Λ matrix per shock, making fragility profiles visible at a glance.

### 4.4 RQ4 — Borrowed centrality / network substitution

**Risers.** Airports with ΔGACIᵢ > 0 during a shock are flagged as "risers." Pre-registered candidate categories:

- *Cargo specialists*: MEM, ANC, LEJ, HKG-cargo (the COVID-era cargo surge)
- *Geo-bypass hubs*: DOH (US-traffic detour after 9/11), IST (Russian-airspace detour 2022), KUL (regional substitution)
- *Regional safe-havens*: hubs adjacent to but unaffected by a region-specific shock

**Decomposition of riser dynamics.**

ΔGACIᵢ = αᵢ,own + Σⱼ≠ᵢ wᵢⱼ · L̃ⱼ + εᵢ

where wᵢⱼ is the pre-shock route weight (shared flights or alliance overlap between i and j), and L̃ⱼ = −ΔGACIⱼ is neighbor j's loss.

**Spatial autoregressive (SAR) model.**

ΔGACIᵢ = ρ · Σⱼ wᵢⱼ ΔGACIⱼ + Xᵢβ + ε

- ρ < 0 indicates *substitution* (neighbor's loss is the focal airport's gain)
- ρ > 0 indicates *spillover* (neighbor's loss propagates as the focal airport's loss)

**Hypothesis.** ρ flips sign by shock type — *substitution* (ρ < 0) for spatially confined shocks (SARS, Ebola, Russia 2022) and *spillover* (ρ > 0) for globally synchronised shocks (COVID, GFC). The Russia-2022 airspace closure should be the textbook substitution case, with IST and DOH absorbing Trans-Siberian detour traffic.

## 5. Expected Contributions

**Conceptual.** The project tests whether the connectivity–resilience inversion identified in our previous work — established for one city under a simulated shock — extends to the *global* aviation system observed across *multiple real* shocks. A positive verdict allows the broader claim that *the efficiency–resilience trade-off is not a parochial feature of urban infrastructure but a by-product of network globalisation itself*. A negative or shock-conditional verdict is equally informative: it would identify the conditions under which the inversion appears.

**Methodological.** It is, to our knowledge, the first attempt to operationalise the resilience triangle as (i) an *observed* response rather than a simulated one, (ii) a *multi-year panel* rather than a snapshot, and (iii) a *five-component vector* rather than a scalar. The framework transfers directly to other globally observed networks: trade, power, finance.

**Empirical.** Differential fragility sources by shock type — e.g., *health shocks → eigen-dependence, financial shocks → volume-dependence, geopolitical shocks → regional-importance dependence* — are quantified for the first time. The SAR estimation of borrowed centrality identifies the sign-flip conditions between substitution and spillover.

**Policy.** The systemic-risk cost of mega-hub concentration is quantified at the level of passenger and economic exposure. The country/city covariates (GDP, tourism, business, logistics, governance) that produce *frontier-positioned* airports (high efficiency and high resilience) are identified — directly relevant for developing-country aviation policy.

## 6. Data, Pipeline, Timeline

**Internal data (available now).** `GACI1996_2024_new_panel_data.csv` (5,428 airports × 29 years × 7 metrics = 101,049 airport-year observations, no missing values).

**External covariates (2–3 weeks to assemble).** GDP per capita, GDP growth, Logistics Performance Index (from 2007), and Worldwide Governance Indicators from the World Bank; tourism receipts and arrivals from UNWTO; airport-level cargo and international shares from IATA / ICAO; FDI flows and business-services GDP shares from OECD; shock metadata (origin date, type, affected regions) compiled in-house.

**Pipeline.**

1. (Python) Detect shock windows; compute (R, T, M, Λ) per airport × component × shock — 5,428 × 5 × 10 ≈ 271,400 cells.
2. (Python) Annual Gini series + shock-wise quadrant classification.
3. (R) Covariate PCA / EFA → four latent factors (business hub-ness, tourism dependence, logistics readiness, governance capacity).
4. (R) Meta-regression and Spatial AR via the `spdep` package.
5. (Python / QGIS) Visualisation: per-shock world maps of quadrants (10 panels), per-shock Lorenz curves, centrality-component heatmaps, efficiency–resilience Pareto frontier scatter.

**Timeline.**

- **Week 1–4 (RQ1, RQ3):** CSV-only stage; primary conceptual findings produced.
- **Week 5–8 (RQ2, RQ4):** After external covariates are merged; quadrant maps and SAR estimation completed.
- **Week 9–12 (Draft):** Methods and Results first draft.
- **Total: 12 weeks (3 months)** to a submission-ready manuscript.

**Target-journal ranking.**

1. **Nature Communications** — global system × equity × resilience, scope-exact fit.
2. **Nature Cities** — same venue as our previous work, attractive if the city-airport bridge is emphasised.
3. **Nature Sustainability** — if the climate-shock framing is foregrounded.
4. **PNAS** — if the methodological backbone is the headline.
5. **Transportation Research Part D / A / E** — disciplinary fallback (Wandelt 2024 is in TR-D).

## 7. Open Questions for Co-authors

1. Do we report the resilience triangle as a full (R, T, M) 3-D object, or simplify to (Λ, T) two dimensions for the main figures?
2. For covariate dimension reduction, PCA (interpretable) or EFA (latent-factor hypotheses testable)?
3. Is the 90% recovery threshold (with 80% / 95% as sensitivity) appropriate, or should we anchor on a different definition (e.g., 1-sigma return-to-trend)?
4. For the SAR weights wᵢⱼ, which specification is the main one — pre-shock route share, alliance overlap, or continental adjacency?
5. RQ3 has a collinearity risk because eigenvector centrality is mechanically inside the GACI formula. Do we orthogonalise the components before regression, or use Shapley-style variance decomposition only?

## 8. Key References

**Resilience-triangle formulation.**

- Bruneau, M., Chang, S.E., Eguchi, R.T., Lee, G.C., O'Rourke, T.D., Reinhorn, A.M., Shinozuka, M., Tierney, K., Wallace, W.A., von Winterfeldt, D. (2003). A framework to quantitatively assess and enhance the seismic resilience of communities. *Earthquake Spectra*, 19(4), 733–752. — Origin of the (R, T, Λ) resilience triangle.
- Cimellaro, G.P., Reinhorn, A.M., Bruneau, M. (2010). Framework for analytical quantification of disaster resilience. *Engineering Structures*, 32(11), 3639–3649. — Analytical formalisation of the Λ integral and recovery-threshold convention.
- Reggiani, A., Nijkamp, P., Lanzi, D. (2015). Transport resilience and vulnerability: the role of connectivity. *Transportation Research Part A*, 81, 4–15. — Recommends vector representation of resilience for transport networks.
- Janić, M. (2022). Analysis and modelling of airport resilience, robustness, and vulnerability: impact of COVID-19 pandemic disease. *The Aeronautical Journal*, 126(1304), 1924–1953. — Airport-level application of R/robustness/vulnerability.

**Aviation-network connectivity and resilience.**

- Cheung, T.K.Y., Wong, C.W.H., Zhang, A. (2020). The evolution of aviation network: Global airport connectivity index 2006–2016. *Transportation Research Part E*, 133, 101826. — Source of GACI.
- Wandelt, S., Zhang, A., Sun, X. (2024). Global Airport Resilience Index: Towards a comprehensive understanding of air transportation resilience. *Transportation Research Part D*, 138, 104796. — Simulation-based scalar resilience benchmark.

**Connectivity–resilience inversion in urban infrastructure.**

- Our previous work, under review at *Nature Cities* (2026). Inequality in railway accessibility and resilience across the Tokyo Metropolitan area.
