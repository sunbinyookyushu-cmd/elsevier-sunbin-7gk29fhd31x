# Connectivity–Resilience Inequality in the Global Aviation Network
## A Multi-Shock Panel Test of the Inversion Hypothesis (1996–2024)

**Date:** 2026-05-15
**Lead:** Sunbin Yoo (Managi Lab)
**Data:** GACI 1996–2024 panel (5,428 airports × 29 years × 7 metrics)

---

## 1. Motivation

A central finding of our previous work (under review at *Nature Cities*) is that **connectivity and resilience are inversely distributed** across urban infrastructure. In the Tokyo Metropolitan area, neighborhoods with the highest railway accessibility (wealthier, more educated, younger, central) systematically have the *lowest* resilience to disruption, while peripheral and older neighborhoods show the reverse. The inversion implies a stark policy trade-off: maximising connectivity concentrates fragility.

The present project asks whether the **same inversion holds in the global aviation network observed under multiple real shocks**, rather than in a single city under a single simulated shock. We use a lab-extended version of the Global Airport Connectivity Index (Cheung, Wong & Zhang, 2020) covering 1996–2024, giving 5,428 airports across 29 years and ~10 observed shocks.

The closest precedents leave the gap we occupy. Wandelt, Zhang & Sun (2024, *TR-D*) build a simulation-based Global Airport Resilience Index but cover only 2023, use hypothetical airport closures, and collapse resilience to a scalar. Janić (2022) formalises the resilience/robustness/vulnerability vocabulary but applies it to two airports (LHR, JFK) under one shock (COVID). Neither tests the inversion hypothesis on observed shocks at global scale, and neither retains a multi-dimensional resilience representation.

## 2. Research Questions

**RQ1 — Co-evolution.** How have *connectivity inequality* (Gini on GACI) and *resilience inequality* (Gini on resilience-loss Λ) co-evolved across the global airport network between 1996 and 2024? Do the two inequalities move together as mega-hubs rise, or diverge?

**RQ2 — Multi-shock robustness of inversion.** Does the inversion identified in our previous work (high-connectivity ↔ low-resilience) hold consistently across shock types — health, financial, geopolitical — or is it confined to certain shock classes?

**RQ3 — Centrality-component fragility.** Which of the five sub-components of GACI (Degree, Eigen, NorClose, NorBetweenness, RegionalImportance) is most strongly linked to resilience loss? We pre-register the hypothesis that *eigenvector centrality* is the most fragile component, because by definition it depends on neighbors' importance and therefore collapses when neighboring hubs collapse.

**RQ4 — Borrowed centrality.** Which airports' GACI actually *rises* during a shock, and is that rise (i) own growth, or (ii) absorbed traffic from collapsing neighboring hubs? We expect the sign of the substitution–spillover effect to flip across shock types — substitution dominates regionally confined shocks, spillover dominates globally synchronised shocks.

## 3. The Resilience Triangle: What R, T, M, Λ Measure

For each airport *i* and each shock *s*, we compute four numbers that decompose the airport's response into four dimensions, following the resilience-triangle lineage in disaster-engineering (Bruneau et al., 2003; Cimellaro et al., 2010) and transport resilience (Reggiani et al., 2015; Janić, 2022).

| Symbol | Name | What it asks | Better when… |
|---|---|---|---|
| **R** | Robustness | *How much was kept at the worst moment?* | R closer to 1 |
| **T** | Rapidity | *How fast did the airport bounce back?* | T closer to 0 |
| **M** | Memory | *Did the airport return to its old normal?* | M closer to 1 |
| **Λ** | Triangle area | *What was the cumulative loss in GACI-years?* | Λ closer to 0 |

**Worked example: LAX × COVID-19.** LAX's GACI series 2017–2024:

| Year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| GACI | 3.375 | 3.332 | 3.318 | **2.351** | 2.394 | **3.023** | 3.108 | 3.257 |

From these values: pre-shock baseline = mean(2017–19) = **3.342**; trough = **2.351** at 2020; 90% recovery threshold = 3.008; recovery year = first year ≥ 3.008 after trough = **2022**.

The four metrics evaluate as:

- **R** = 2.351 / 3.342 = **0.703** — LAX retained 70% of pre-shock GACI at the dip.
- **T** = 2022 − 2020 = **2 years** — recovered within two years.
- **M** = 3.257 / 3.342 = **0.975** — back to 97.5% of pre-shock by 2024 (2.5% permanent shortfall).
- **Λ** = (3.342 − 2.351) + (3.342 − 2.394) = **1.939 GACI·year** — cumulative gap, baseline minus observed, summed over the dip-to-recovery years.

**Vector representation, not scalar.** Janić (2022) collapses these into a single number; we deliberately keep the four-tuple because two airports with the same scalar can hide very different stories (a deep-fast-bounce profile is a different policy problem from a shallow-slow-bounce profile). Reggiani et al. (2015) recommend exactly this vector representation for transport networks.

**Edge cases.** Some airports *gain* GACI during a shock by absorbing diverted traffic (cargo specialists like MEM/ANC/LEJ during COVID; geo-bypass hubs like DOH and IST during 9/11 and the Russia airspace closure). For these, R > 1 and Λ < 0, indicating cumulative *gain* rather than loss. These risers are flagged as a separate fifth analytical category and analysed under RQ4. Airports that do not reach the 90% threshold within the sample window have T treated as right-censored at 2024.

**Centrality-component triangles.** The same four-tuple is computed *separately* for each of the five sub-components of GACI, producing fragility profiles (Λ^Degree, Λ^Eigen, Λ^Close, Λ^Between, Λ^RegImp) that enable RQ3.

## 4. Empirical Strategy

### 4.1 Computational pipeline

For airport *i* and shock *s* with pre-window [t_s−3, t_s−1] and post-window [t_s, t_s+2]:

```
pre       = mean(GACI_i over [t_s−3, t_s−1])
trough    = min(GACI_i over [t_s, t_s+2])
threshold = 0.90 × pre              (90% main; 80% and 95% as sensitivity)
t_rec     = first year t > t_trough with GACI_i(t) ≥ threshold
                                     (right-censored at 2024 if not reached)

R_i,s = trough / pre
T_i,s = t_rec − t_s
M_i,s = GACI_i(2024) / pre
Λ_i,s = Σ over t in [t_s, t_rec] of max(0, pre − GACI_i(t))
```

### 4.2 Locked design choices

| Choice | Decision | Reference |
|---|---|---|
| Pre-shock baseline | 3-year mean before shock | Reggiani et al. (2015) |
| Recovery threshold | 90% main; 80% / 95% sensitivity | Cimellaro et al. (2010, §3.2) |
| Trough detection | Airport-specific min over [t_s, t_s+2] | Janić (2022) |
| Risers (R > 1) | Separate 5th category, RQ4 deep-dive | extends Wandelt et al. (2024) |
| Overlapping shocks | Main panel uses clean shocks only | this study |

### 4.3 Clean shock list (main panel)

| Shock | Year | Pre-window | Type |
|---|---|---|---|
| 9/11 | 2001 | 1998–2000 | Geopolitical / security |
| SARS | 2003 | 2000–2002 | Health |
| Global Financial Crisis | 2008–09 | 2005–2007 | Financial |
| Ebola | 2014 | 2011–2013 | Health / regional |
| COVID-19 | 2020 | 2017–2019 | Health |

Excluded from the main panel due to overlap with prior shocks: H1N1 2009, ash cloud 2010, Arab Spring 2011, Russia 2014 (all within GFC tail), and Russia 2022 (within COVID recovery). The Russia 2022 case is retained as a *qualitative case study for RQ4* because it is the canonical observed substitution event (IST and DOH absorbing trans-Siberian detour traffic).

### 4.4 Identification: airport × shock panel with two-way fixed effects

Once R/T/M/Λ are computed per airport × shock, we have a panel of 5,428 × 5 = **27,140 observations**, with the resilience metrics as outcomes. The core regression is:

$$\Lambda_{is} = \alpha + \beta \cdot \text{Treatment}_{i,\text{pre}(s)} + \gamma_i + \delta_s + X_{is}\beta + \varepsilon_{is}$$

where γ_i absorbs all time-invariant airport characteristics (geography, city size, infrastructure age) and δ_s absorbs shock-specific severity. The treatment is measured *before* each shock and varies both across airports and across shocks for the same airport.

We estimate two complementary specifications:

1. **Inversion as causal** — Treatment = log(GACI_pre). β > 0 indicates that a larger hub-state *causes* a larger cumulative loss, within-airport. This is the inversion hypothesis re-cast as a within-airport causal estimate.
2. **Borrowed centrality** — Treatment = Σⱼ wᵢⱼ × (1 − R_{j,s}), pre-shock-weighted exposure to neighbors' losses. β > 0 (on R) indicates substitution; β < 0 indicates spillover.

Together, the two specifications give (i) the causal version of the inversion hypothesis and (ii) the network-spillover test. Treatment is in both cases measured pre-shock and therefore mechanically exogenous to the shock's resilience response.

### 4.5 Covariate factor analysis

Airport-level covariates assembled from World Bank (GDP, Logistics Performance Index, Worldwide Governance Indicators), UNWTO (tourism receipts), IATA/ICAO (cargo and international share), and OECD (FDI, business-services GDP share). These are reduced via PCA into four latent factors (business hub-ness, tourism dependence, logistics readiness, governance capacity) and entered as the X_is covariates in the panel regression.

## 5. Expected Contributions

**Conceptual.** The project tests whether the connectivity–resilience inversion established in our previous work for one city under a simulated shock extends to the *global* aviation system observed across *multiple real* shocks. A positive verdict supports the broader claim that the efficiency–resilience trade-off is not a parochial urban-infrastructure phenomenon but a by-product of network globalisation itself. A shock-conditional verdict is equally informative.

**Methodological.** First operationalisation of the resilience triangle as (i) an *observed* response rather than a simulated one, (ii) a *multi-year panel* rather than a snapshot, (iii) a *five-component vector* per airport-shock rather than a scalar, and (iv) an *outcome variable in a two-way-fixed-effects panel* that yields within-airport causal estimates of the inversion. The framework transfers directly to other globally observed networks (trade, power, finance).

**Empirical.** Differential fragility sources by shock type — quantified for the first time across centrality components — and clean within-airport causal estimates of the inversion. Russia 2022 case study provides a textbook substitution example.

**Policy.** Systemic risk of mega-hub concentration is quantified at the level of passenger and economic exposure. The country/city factors (business / tourism / logistics / governance) that produce *frontier-positioned* airports (high efficiency *and* high resilience) are identified, directly relevant for developing-country aviation policy.

## 6. Data, Pipeline, Timeline

**Internal data (available now).** GACI 1996–2024 panel, 5,428 airports × 29 years × 7 metrics. No missing values.

**External covariates (~2–3 weeks).** GDP, LPI, WGI (World Bank); tourism (UNWTO); cargo and international share (IATA/ICAO); FDI, business-services GDP share (OECD); shock metadata in-house.

**Timeline.** Week 1–4: compute (R, T, M, Λ) for the full 5,428 × 5 × 5 panel and run RQ1, RQ3 (CSV-only). Week 5–8: merge covariates, fit two-way fixed-effects panel for RQ2, run SAR estimation for RQ4. Week 9–12: first draft. Total: 12 weeks to submission.

**Target journals.** Nature Communications (first choice — global system × equity × resilience scope); Nature Cities (same venue as our previous work); Nature Sustainability; PNAS; TR-D / TR-A / TR-E as disciplinary fallback.

## 7. Key References

- Bruneau, M. et al. (2003). A framework to quantitatively assess and enhance the seismic resilience of communities. *Earthquake Spectra*, 19(4), 733–752.
- Cheung, T.K.Y., Wong, C.W.H., Zhang, A. (2020). The evolution of aviation network: Global airport connectivity index 2006–2016. *Transportation Research Part E*, 133, 101826.
- Cimellaro, G.P., Reinhorn, A.M., Bruneau, M. (2010). Framework for analytical quantification of disaster resilience. *Engineering Structures*, 32(11), 3639–3649.
- Janić, M. (2022). Analysis and modelling of airport resilience, robustness, and vulnerability: impact of COVID-19 pandemic disease. *The Aeronautical Journal*, 126(1304), 1924–1953.
- Reggiani, A., Nijkamp, P., Lanzi, D. (2015). Transport resilience and vulnerability: the role of connectivity. *Transportation Research Part A*, 81, 4–15.
- Wandelt, S., Zhang, A., Sun, X. (2024). Global Airport Resilience Index: Towards a comprehensive understanding of air transportation resilience. *Transportation Research Part D*, 138, 104796.
- Our previous work (under review at *Nature Cities*, 2026). Inequality in railway accessibility and resilience across the Tokyo Metropolitan area.
