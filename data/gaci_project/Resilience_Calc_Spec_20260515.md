# Resilience Calculation Spec — For Co-author Review

**Project:** Connectivity–Resilience Inequality in the Global Aviation Network (1996–2024)
**Date:** 2026-05-15
**Status:** Spec drafted, requesting co-author confirmation before computation begins.

---

## 1. Resilience Triangle — Per Airport × Per Shock

For each airport *i* and each shock *s*, we compute a four-tuple, following the established resilience-triangle lineage (Bruneau et al., 2003; Cimellaro et al., 2010; Reggiani et al., 2015; Janić, 2022):

| Symbol | Name | Formula | Source |
|---|---|---|---|
| **R**ᵢₛ | Robustness | GACI(trough) / GACI(pre) | Bruneau et al. (2003); Janić (2022) |
| **T**ᵢₛ | Rapidity | t_recovery − t_shock | Bruneau et al. (2003); Cimellaro et al. (2010) |
| **M**ᵢₛ | Memory | GACI(2024) / GACI(pre) | Extends Cimellaro et al. (2010) "permanent loss" |
| **Λ**ᵢₛ | Triangle area | Σ max(0, GACI_pre − GACI_t) over [t_s, t_rec] | Cimellaro et al. (2010, Eq. 5) discretised |

The vector representation (rather than the scalar collapse in Janić, 2022) follows the recommendation of Reggiani et al. (2015) for transport-network resilience.

The same four-tuple is also computed **separately for each of the 5 sub-components** of GACI (Degree, Eigen, NorClose, NorBetweenness, RegionalImportance) to enable RQ3 (which centrality type is the source of fragility). The GACI definition and its 5-component decomposition come from Cheung, Wong & Zhang (2020).

---

## 2. Five Design Choices — Locked

| # | Choice | Decision | Rationale / Reference |
|---|---|---|---|
| 1 | Pre-shock baseline | **`mean(GACI in [t_s−3, t_s−1])`** (3-yr mean) | Noise smoothing, consistent with the 3-year averaging convention in transport-resilience studies (Reggiani et al., 2015). |
| 2 | Recovery threshold | **90% of pre** (main), 80% (sensitivity) | 90% follows the practical recovery convention used in Cimellaro et al. (2010, §3.2); 95% (Bruneau et al., 2003 original) reported as upper-bound sensitivity. |
| 3 | Trough detection | **Airport-specific** `min(GACI_i in [t_s, t_s+2])` | Shock propagation speed varies by region. Heterogeneous-trough approach used in Janić (2022). |
| 4 | Risers (R > 1, Λ < 0) | **Separate 5th category** | Substitution beneficiaries (DOH, MEM, IST) are conceptually distinct; analysed under RQ4. Borrowed-centrality framing extends Wandelt et al. (2024). |
| 5 | Overlapping shocks | **Clean shocks only** | Pre-window must be free of prior-shock contamination, otherwise resilience triangles are mis-anchored. |

---

## 3. Clean Shock List

Five shocks with uncontaminated pre-windows:

| Shock | Year | Pre-window | Type |
|---|---|---|---|
| 9/11 | 2001 | 1998–2000 | Geopolitical / security |
| SARS | 2003 | 2000–2002 | Health |
| Global Financial Crisis | 2008–09 | 2005–2007 | Financial |
| Ebola | 2014 | 2011–2013 | Health / regional |
| COVID-19 | 2020 | 2017–2019 | Health |

**Dropped from main analysis (overlap with prior shock):** H1N1 2009 (within GFC), Eyjafjallajökull ash 2010 (GFC tail), Arab Spring 2011 (GFC tail), Russia 2014 (Ebola-overlap region), Russia 2022 (within COVID recovery).

**Russia 2022 is retained as a qualitative case study for RQ4** (canonical substitution / borrowed-centrality example: IST and DOH absorbing trans-Siberian detour traffic).

---

## 4. Worked Example — LAX × COVID-19

| Year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| GACI | 3.375 | 3.332 | 3.318 | 2.351 | 2.394 | 3.023 | 3.108 | 3.257 |

Calculation:

- Pre = mean(3.375, 3.332, 3.318) = **3.342**
- Trough = min(2020–22) = **2.351** (at 2020)
- 90% threshold = 0.9 × 3.342 = 3.008
- Recovery year = first year GACI ≥ 3.008 after 2020 → **2022** (3.023)
- **R = 0.703** (kept 70% of pre at trough)
- **T = 2** years
- **M = 0.975** (97.5% of pre by 2024)
- **Λ = (3.342 − 2.351) + (3.342 − 2.394) = 1.939** GACI·yr

LAX summary: "lost 30%, recovered to 90% in 2 years, near-full normalisation by 2024" — robust profile.

---

## 5. Pipeline Output Shape

The full panel after computation:

- 5,428 airports × 5 clean shocks × 5 centrality components × 4 metrics (R, T, M, Λ)
- = approximately **543,000 cells**, plus airport-level metadata (region, country, hub-type, etc.)
- Plus a separate **riser DB** (airports with R > 1 for any shock × component, ~10–20% of cells expected)

---

## 6. Pending Questions for Co-authors

1. **Russia 2022 inclusion in main panel.** Currently dropped due to COVID overlap, retained only as qualitative case for RQ4. Is the COVID-pre-window contamination (mean of 2019, 2020, 2021) bad enough to justify exclusion, or should we proceed with a *DiD-style* design (treated = Trans-Siberian-dependent EU–AS routes, control = unaffected, using 2019 as clean baseline)? The DiD route would preserve a *true* multi-shock test.

2. **Recovery threshold sensitivity.** 90% main / 80% sensitivity — should we also report 95% as a third sensitivity to align with Bruneau (2003) original convention?

3. **Memory M definition.** Currently GACI(2024) / GACI(pre). For shocks where recovery completed before 2024 (e.g., SARS, recovered by 2005), is the 2024-anchored M still meaningful, or should M be defined at t_rec + 5 (i.e., "5 years past recovery")?

4. **Cross-component aggregation.** When we have 5 component-level (R, T, M, Λ), should we (a) report each separately throughout, or (b) construct a composite resilience index by weighting the 5 components inversely to their pre-shock GACI loadings (parallel to how Cheung et al. 2020 built GACI itself)?

5. **Eigenvector–GACI collinearity.** Eigenvector centrality is mechanically inside the GACI formula. When regressing Λ^GACI on the 5 components, this risks pure collinearity. Do we orthogonalise (Gram–Schmidt) before regression, or use Shapley variance-decomposition only?

---

## 7. Next Step (After Co-author Sign-off)

1. Implement shock-window detection per airport in Python (4 days)
2. Compute (R, T, M, Λ) for the full 5,428 × 5 × 5 panel (2 days)
3. Generate per-shock quadrant world maps + Lorenz curves (3 days)
4. Run meta-regression and SAR estimation in R (5 days)
5. First-draft Results section (2 weeks)

Total: ~5 weeks from go-ahead to first Results draft.

---

## 8. Key References

**Resilience-triangle formulation.**

- Bruneau, M., Chang, S.E., Eguchi, R.T., Lee, G.C., O'Rourke, T.D., Reinhorn, A.M., Shinozuka, M., Tierney, K., Wallace, W.A., von Winterfeldt, D. (2003). A framework to quantitatively assess and enhance the seismic resilience of communities. *Earthquake Spectra*, 19(4), 733–752.
- Cimellaro, G.P., Reinhorn, A.M., Bruneau, M. (2010). Framework for analytical quantification of disaster resilience. *Engineering Structures*, 32(11), 3639–3649.
- Reggiani, A., Nijkamp, P., Lanzi, D. (2015). Transport resilience and vulnerability: the role of connectivity. *Transportation Research Part A*, 81, 4–15.
- Janić, M. (2022). Analysis and modelling of airport resilience, robustness, and vulnerability: impact of COVID-19 pandemic disease. *The Aeronautical Journal*, 126(1304), 1924–1953.

**Aviation-network connectivity and resilience.**

- Cheung, T.K.Y., Wong, C.W.H., Zhang, A. (2020). The evolution of aviation network: Global airport connectivity index 2006–2016. *Transportation Research Part E*, 133, 101826.
- Wandelt, S., Zhang, A., Sun, X. (2024). Global Airport Resilience Index: Towards a comprehensive understanding of air transportation resilience. *Transportation Research Part D*, 138, 104796.

**Connectivity–resilience inversion in urban infrastructure.**

- Our previous work (under review at *Nature Cities*, 2026). Inequality in railway accessibility and resilience across the Tokyo Metropolitan area.
