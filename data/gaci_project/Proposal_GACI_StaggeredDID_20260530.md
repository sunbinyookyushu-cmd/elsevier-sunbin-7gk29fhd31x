# Heterogeneous Shock Effects on Global Airport Resilience
## A Staggered Difference-in-Differences Approach (1996–2024)

**Date:** 2026-05-30
**Lead:** Sunbin Yoo (Managi Lab)
**Data:** GACI 1996–2024 panel (5,428 airports × 29 years × 7 metrics)

---

## 1. Motivation

Connectivity and resilience are inversely distributed across urban infrastructure: in our previous work on the Tokyo Metropolitan area (under review at *Nature Cities*), the neighborhoods with the highest railway accessibility — wealthier, younger, more central — were systematically the *least* resilient to disruption. The inversion implies a stark policy trade-off: maximising connectivity concentrates fragility.

The present project asks whether the **same inversion holds in the global aviation network observed under multiple real shocks**, and — equally importantly — how *heterogeneous* the impacts of different shock types are across airports of different sizes, regions, and hub functions. We use a lab-extended version of the Global Airport Connectivity Index (Cheung, Wong & Zhang, 2020) covering 1996–2024 (5,428 airports × 29 years) together with five clean external shocks (9/11, SARS, GFC, Ebola, COVID-19).

The closest precedents leave the gap we occupy. Wandelt, Zhang & Sun (2025, *TR-D*) build a simulation-based Global Airport Resilience Index (GARI), but cover only 2023, use hypothetical airport closures, and collapse resilience to a scalar. Janić (2022) formalises the resilience/robustness/vulnerability vocabulary but applies it to two airports (LHR, JFK) under one shock (COVID). Neither tests the inversion hypothesis on observed shocks at global scale, neither retains a multi-dimensional resilience representation, and neither exploits staggered policy variation as a source of causal identification.

We deliberately set aside the GACI → GDP translation as a *direct* estimand. The relationship between aviation connectivity and economic output is well established in the existing literature (Cheung et al., 2020 and references therein), and a direct cross-sectional regression faces severe reverse-causality concerns — global cities anchor dense aviation networks because they are large economies, and they are large economies in part because they anchor dense aviation networks. We instead estimate the effect of *shocks* on *airport resilience* directly, and report GDP implications only as back-of-envelope products of our Λ estimates with externally-estimated GACI–GDP elasticities (see §5).

## 2. Research Questions

**RQ1 — Inversion across shocks.** Does the connectivity–resilience inversion hold consistently — i.e. do high-pre-GACI hubs suffer larger cumulative GACI losses (Λ) — across health, financial, and geopolitical shocks?

**RQ2 — Policy as treatment (COVID).** How do the staggered country-level lockdown timing and stringency causally affect each component of the airport-level resilience triangle (R, T, M, Λ)?

**RQ3 — Centrality-component fragility.** Which of the five sub-components of GACI (Degree, Eigen, NorClose, NorBetweenness, RegionalImportance) is the most fragile, and does the answer change by shock type? We pre-register the hypothesis that *eigenvector centrality* is the most fragile component because, by construction, it depends on neighbours' importance and therefore collapses when neighbouring hubs collapse.

**RQ4 — Borrowed centrality.** Which airports' GACI *rises* during a shock by absorbing diverted traffic from neighbouring hubs (substitution), and which are dragged down by neighbours' losses (spillover)? We expect the sign of the network spillover term to flip across shock types — substitution dominates regionally confined shocks (9/11, SARS, Russia 2022), spillover dominates globally synchronised shocks (COVID, GFC).

## 3. The Resilience Triangle: R, T, M, Λ

For each airport *i* and each shock *s* we compute a four-tuple, following the resilience-triangle lineage from disaster engineering (Bruneau et al., 2003; Cimellaro et al., 2010) and transport resilience (Reggiani et al., 2015; Janić, 2022).

| Symbol | Name | What it asks | Better when… |
|---|---|---|---|
| **R** | Robustness | How much was kept at the worst moment? | R closer to 1 |
| **T** | Rapidity | How fast did the airport bounce back? | T closer to 0 |
| **M** | Memory | Did it return to its old normal? | M closer to 1 |
| **Λ** | Triangle area | What was the cumulative loss in GACI-years? | Λ closer to 0 |

**Worked example: LAX × COVID-19.** With LAX's GACI series 2017–2024 (3.375, 3.332, 3.318, **2.351**, 2.394, **3.023**, 3.108, 3.257):

- Pre-shock baseline = mean(2017–19) = **3.342**
- Trough = **2.351** at 2020; 90% recovery threshold = 3.008; recovery year = first year ≥ 3.008 after the trough = **2022**
- **R** = 2.351 / 3.342 = **0.703** (kept 70% at the dip)
- **T** = 2022 − 2020 = **2 years**
- **M** = 3.257 / 3.342 = **0.975** (97.5% of pre-shock by 2024)
- **Λ** = (3.342 − 2.351) + (3.342 − 2.394) = **1.939 GACI·yr**

We keep the four-tuple as a *vector* (per Reggiani et al., 2015) rather than collapse it to a scalar (as in Janić, 2022): two airports with the same scalar can hide a deep-fast-bounce profile versus a shallow-slow-bounce profile — entirely different policy problems.

The same four-tuple is computed *separately* for each of the five sub-components of GACI, producing component-level fragility profiles (Λ^Degree, Λ^Eigen, Λ^Close, Λ^Between, Λ^RegImp) that enable RQ3.

## 4. Empirical Strategy: A Two-Step Design

### 4.1 Step 1 — Construct the resilience triangle

For airport *i* and shock *s* with pre-window [t_s−3, t_s−1] and post-window [t_s, t_s+2]:

```
pre        = mean(GACI_i over [t_s−3, t_s−1])
trough     = min(GACI_i over [t_s, t_s+2])
threshold  = 0.90 × pre                (90% main; 80% / 95% sensitivity)
t_rec      = first year t > t_trough with GACI_i(t) ≥ threshold
                                        (right-censored at 2024 if not reached)
R_i,s      = trough / pre
T_i,s      = t_rec − t_s
M_i,s      = GACI_i(2024) / pre
Λ_i,s      = Σ over years t in [t_s, t_rec] of max(0, pre − GACI_i(t))
```

This yields a panel of 5,428 airports × 5 clean shocks × 5 centrality components × 4 metrics = approximately **543,000 cells**, plus a separate "riser DB" (airports with R > 1 for any shock × component, expected ~10–20% of cells) that feeds RQ4.

### 4.2 Step 2 — Identify causal effects with staggered / intensity DID

The 4-tuple is the *outcome* of a second-stage regression in which the treatment is the pre-shock-determined intensity of exposure to the shock — making the treatment mechanically exogenous to the post-shock resilience response.

**COVID-19 as the staggered design.** COVID is the cleanest staggered policy experiment because country-level lockdown start dates and stringency varied substantially across January–April 2020. We use the Oxford COVID-19 Government Response Tracker (OxCGRT; Hale et al., 2021) stringency index, mapped from country-day to airport-day.

$$Y_{i}^{\text{COVID}} = \beta_1 \cdot \text{LockdownStringency}_i + \beta_2 \cdot \text{LockdownDuration}_i + X_i'\gamma + \alpha_{r(i)} + \varepsilon_i$$

where Y is one of (R, T, M, Λ); α_{r(i)} is a region fixed effect; and X_i contains pre-shock airport controls (size, hub type, route-mix concentration). β is estimated separately for each of the four outcomes, yielding four distinct policy-margin coefficients: β_R (how much depth lockdown causes), β_T (how much recovery delay), β_M (how much permanent shortfall), β_Λ (total GACI·yr cost).

**Other shocks as intensity DID.** For 9/11, SARS, GFC, and Ebola the treatment is the pre-shock share of the airport's routes connecting it to the shock-source region:

$$Y_{i}^{s} = \beta^s \cdot \text{Exposure}_{i,\text{pre}(s)} + X_i'\gamma + \alpha_{r(i)} + \varepsilon_i$$

| Shock | Pre-shock exposure measure |
|---|---|
| 9/11 (2001) | Share of routes to/from US + transatlantic corridor |
| SARS (2003) | Share of routes to/from China, Hong Kong, Singapore |
| GFC (2008) | Share of routes to/from global financial hubs (LHR, JFK, HKG, SIN, FRA) |
| Ebola (2014) | Share of routes to/from West Africa |

Because Exposure_i is fixed at the pre-shock year and the shock is exogenous to any single airport's economy, β^s identifies the average treatment effect of exposure on the relevant resilience component.

**Estimator choice.** For the COVID staggered design we use the Callaway–Sant'Anna (2021) and Sun–Abraham (2021) estimators so that cohort-specific dynamic effects are recovered without the negative-weighting pathology of two-way fixed effects under heterogeneous treatment effects (de Chaisemartin & D'Haultfœuille, 2020). The event-study coefficients β_τ in fact *map back* into the resilience triangle: β_0 ≈ −(1 − R), the τ at which β_τ returns to 0 corresponds to T, the long-run β corresponds to −(1 − M), and ∫β_τ dτ ≈ −Λ. Reporting both the cross-sectional regression on (R, T, M, Λ) and the event-study coefficients on yearly GACI gives the reader the same content in two complementary forms.

**Standard errors.** Because (R, T, M, Λ) are *generated* from a first-stage computation on noisy GACI series, the naive second-stage standard errors are downward biased. We report two-step nonparametric bootstrap (1,000 replications, resampling airports) standard errors as the main inference, with airport-clustered analytical standard errors as a robustness check.

### 4.3 Heterogeneous treatment effects

The 4-tuple regressions are estimated separately for cells defined by:

- **Pre-shock GACI quintile** — direct test of the inversion hypothesis (RQ1). β^s monotonically larger across quintiles ⇒ inversion confirmed.
- **Hub type** — passenger, cargo, geo-bypass, tourism. We expect cargo hubs (MEM/ANC/LEJ) and geo-bypass hubs (DOH/IST) to appear as *risers* (R > 1) under specific shock types; tourism-dependent airports to show the slowest T under COVID.
- **Region** — eight UN regions.
- **Country governance / income** — Worldwide Governance Indicators and World Bank income classification.

The HTE results are presented as a *shock × airport-characteristic heatmap*, displaying β^s by cell — the single headline figure summarising the heterogeneity that motivates the project.

### 4.4 Substitution and spillover (RQ4)

Network-level effects are identified by augmenting the second-stage regression with a pre-shock-weighted spillover term measuring exposure to *other* airports' losses:

$$Y_i^s = \beta^s \cdot \text{Exposure}_{i,\text{pre}(s)} + \theta^s \cdot \sum_{j \neq i} w_{ij,\text{pre}(s)} \cdot (1 - R_{j,s}) + X_i'\gamma + \varepsilon_i$$

where w_{ij,pre(s)} is the pre-shock route weight from i to j. θ^s > 0 indicates *substitution* (i absorbs traffic from collapsing neighbours, raising R_i — borrowed centrality); θ^s < 0 indicates *spillover* (i is dragged down by neighbours' losses). The sign of θ^s is expected to flip across shock types. The riser-DB cases (DOH and IST in 9/11; MEM, ANC and LEJ in COVID; DOH and IST again in the Russia 2022 case study) serve as canonical examples.

### 4.5 GARI as a second outcome — panel extension

We apply Wandelt, Zhang & Sun's (2025) GARI formula to our 1996–2024 data to construct an *annual* GARI panel, extending what is currently a 2023 snapshot. The same staggered / intensity DID design is then run with GARI as the outcome alongside (R, T, M, Λ). This is a methodological contribution on its own: it places GARI alongside GACI as a panel measure of network resilience and, in doing so, lets us speak directly to the Wandelt–Zhang research line rather than past it.

### 4.6 Clean shock list

| Shock | Year | Pre-window | Type |
|---|---|---|---|
| 9/11 | 2001 | 1998–2000 | Geopolitical / security |
| SARS | 2003 | 2000–2002 | Health |
| Global Financial Crisis | 2008–09 | 2005–2007 | Financial |
| Ebola | 2014 | 2011–2013 | Health / regional |
| COVID-19 | 2020 | 2017–2019 | Health |

H1N1 (2009), the Eyjafjallajökull ash cloud (2010), the Arab Spring (2011), and Russia 2014 are dropped from the main panel because their pre-windows overlap with prior shocks. **Russia 2022 is retained as a qualitative substitution case study for RQ4** — the canonical observed borrowed-centrality event, with IST and DOH absorbing trans-Siberian detour traffic.

### 4.7 Right-censored T

Airports that fail to reach the 90% threshold by 2024 are right-censored. We complement the linear regression on T with a Cox proportional-hazards model on time-to-recovery, with the same right-hand-side variables. A binary "recovered by 2024" outcome is reported as additional robustness.

## 5. From Resilience to GDP — Implication, Not Estimand

We do *not* estimate the GACI → GDP relationship directly, for two reasons. First, the relationship is well-established in prior work (Cheung et al., 2020 and references therein), so re-estimating it adds little. Second, a direct cross-sectional regression faces severe reverse-causality concerns: high-GDP cities anchor dense aviation networks, and dense aviation networks anchor high-GDP cities. Any naive estimate confounds both directions.

Instead, we report **implied GDP losses** by combining our directly-estimated Λ with externally-estimated GACI–GDP elasticities η taken from the existing literature:

$$\widehat{\text{GDP loss}}_{i,s} = \eta \cdot \Lambda_{i,s} \cdot \text{GDP}_{i,\text{pre}(s)}$$

This separates *our* contribution (the resilience profile and its policy determinants) from *prior* contributions (the connectivity–GDP elasticity). Policymakers obtain the implied magnitude without us re-litigating an already-resolved coefficient.

## 6. Expected Contributions

**Conceptual.** First test of the connectivity–resilience inversion at *global* scale across *multiple observed* shocks. A positive verdict supports the broader claim that the efficiency–resilience trade-off is a structural property of network globalisation rather than a parochial feature of any single city's infrastructure.

**Methodological.** (i) First operationalisation of the resilience triangle as an *observed* multi-year panel rather than a simulated snapshot. (ii) First use of staggered policy variation (COVID lockdown stringency) and pre-shock exposure intensity to identify *causal* effects on each component of the resilience triangle. (iii) First panel extension of the Wandelt, Zhang & Sun (2025) GARI from its 2023 snapshot to an annual 1996–2024 series.

**Empirical.** Differential fragility quantified by shock type, centrality component, hub type, and region; substitution and spillover decomposed across all five clean shocks; cohort-specific dynamics of resilience recovery estimated with modern staggered-DID estimators.

**Policy.** Direct identification of which airport types are most vulnerable to which shock types — the input needed for shock-specific resilience investment. Implied GDP exposure provided through back-of-envelope multiplication with established elasticities.

## 7. Data, Timeline, Target Journals

**Internal data (available now).** GACI 1996–2024 panel; airport metadata (region, country, hub type); route-level network used for spillover weights.

**External data (~2–3 weeks).** Oxford OxCGRT (COVID stringency, country-day); FAA / ICAO archives (US airspace closure dates around 9/11); WHO PHEIC notifications (SARS, Ebola, COVID); World Bank GDP and Worldwide Governance Indicators; World Bank income classification; OECD Functional Urban Area definitions for multi-airport metro robustness checks.

**Timeline.** Week 1–3: compute (R, T, M, Λ) for the full 543,000-cell panel; construct annual GARI panel; merge OxCGRT and exposure variables. Week 4–7: estimate Callaway–Sant'Anna staggered DID for COVID; intensity DID for other shocks; bootstrap standard errors; HTE by quintile / hub-type / region. Week 8–10: spillover/substitution decomposition (RQ4); robustness checks (95% and 80% thresholds, FUA aggregation, Cox PH for T). Week 11–14: first draft. Total ~14 weeks to submission.

**Target journals.** *Nature Communications* (first choice — global system × equity × resilience scope); *Nature Cities* (same venue as the Tokyo paper); *PNAS*; *Transportation Research Part D / A / E* as disciplinary fallback.

## 8. Key References

- Bruneau, M., Chang, S.E., Eguchi, R.T., Lee, G.C., O'Rourke, T.D., Reinhorn, A.M., Shinozuka, M., Tierney, K., Wallace, W.A., von Winterfeldt, D. (2003). A framework to quantitatively assess and enhance the seismic resilience of communities. *Earthquake Spectra*, 19(4), 733–752.
- Callaway, B., Sant'Anna, P.H.C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.
- Cheung, T.K.Y., Wong, C.W.H., Zhang, A. (2020). The evolution of aviation network: Global airport connectivity index 2006–2016. *Transportation Research Part E*, 133, 101826.
- Cimellaro, G.P., Reinhorn, A.M., Bruneau, M. (2010). Framework for analytical quantification of disaster resilience. *Engineering Structures*, 32(11), 3639–3649.
- de Chaisemartin, C., D'Haultfœuille, X. (2020). Two-way fixed effects estimators with heterogeneous treatment effects. *American Economic Review*, 110(9), 2964–2996.
- Hale, T., Angrist, N., Goldszmidt, R., Kira, B., Petherick, A., Phillips, T., Webster, S., Cameron-Blake, E., Hallas, L., Majumdar, S., Tatlow, H. (2021). A global panel database of pandemic policies (Oxford COVID-19 Government Response Tracker). *Nature Human Behaviour*, 5, 529–538.
- Janić, M. (2022). Analysis and modelling of airport resilience, robustness, and vulnerability: impact of COVID-19 pandemic disease. *The Aeronautical Journal*, 126(1304), 1924–1953.
- Reggiani, A., Nijkamp, P., Lanzi, D. (2015). Transport resilience and vulnerability: the role of connectivity. *Transportation Research Part A*, 81, 4–15.
- Sun, L., Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *Journal of Econometrics*, 225(2), 175–199.
- Wandelt, S., Zhang, A., Sun, X. (2025). Global Airport Resilience Index: Towards a comprehensive understanding of air transportation resilience. *Transportation Research Part D*, 138, 104522.
- Our previous work (under review at *Nature Cities*, 2026). Inequality in railway accessibility and resilience across the Tokyo Metropolitan area.
