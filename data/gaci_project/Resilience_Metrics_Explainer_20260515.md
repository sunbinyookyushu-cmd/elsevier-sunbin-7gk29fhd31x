# What R, T, M, Λ Measure — An Intuitive Guide

**Project:** Connectivity–Resilience Inequality in the Global Aviation Network (1996–2024)
**Date:** 2026-05-15
**Purpose:** A one-page intuitive explanation of the four resilience-triangle metrics, for co-author review.

---

## The four dimensions

For each airport *i* and each shock *s*, we compute four numbers that together describe how the airport responded to the shock. The framework comes from disaster-engineering resilience theory (Bruneau et al., 2003; Cimellaro et al., 2010) applied here to GACI dynamics.

| Symbol | Name | What it asks | Better when… |
|---|---|---|---|
| **R** | Robustness | *How much did the airport keep at the worst moment?* | R closer to 1 |
| **T** | Rapidity | *How fast did the airport bounce back?* | T closer to 0 |
| **M** | Memory | *Did the airport return to its old normal, or settle below?* | M closer to 1 |
| **Λ** | Triangle area | *What was the cumulative loss in GACI-years?* | Λ closer to 0 |

---

## Worked example: LAX × COVID-19

LAX's GACI series from 2017 through 2024:

| Year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| GACI | 3.375 | 3.332 | 3.318 | **2.351** | 2.394 | **3.023** | 3.108 | 3.257 |
|  | *pre* | *pre* | *pre* | *trough* |  | *recovery* |  | *end* |

Inputs derived from the series:

- **Pre-shock baseline** (3-year mean of 2017–19) = **3.342**
- **Trough** (min over 2020–22) = **2.351** at year **2020**
- **90% recovery threshold** = 0.90 × 3.342 = **3.008**
- **Recovery year** (first year ≥ 3.008 after the trough) = **2022** (GACI = 3.023)

The four resilience-triangle metrics:

**R (Robustness)** = 2.351 / 3.342 = **0.703**
→ At the bottom of the COVID dip, LAX retained 70% of its pre-shock GACI.

**T (Rapidity)** = 2022 − 2020 = **2 years**
→ LAX took two years to climb back within 10% of its pre-shock level.

**M (Memory)** = 3.257 / 3.342 = **0.975**
→ By 2024 LAX had recovered to 97.5% of its pre-shock GACI — close to full normalisation, with a small 2.5% permanent shortfall.

**Λ (Triangle area)** = (3.342 − 2.351) + (3.342 − 2.394) = **1.939 GACI·year**
→ The cumulative gap between pre-shock baseline and observed GACI, summed over the dip-to-recovery window. Units are GACI × years.

---

## Visual intuition

```
GACI
  ┌──────────────────────────────────────────────
3.4│  ● ─ ● ─ ● ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ●  ●  ●     ← pre-shock baseline = 3.342
   │                                  ╱
3.2│                                ●
   │                              ╱
3.0│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ╱ ─ ─ ─ ─ ─ ─ ─    ← 90% threshold = 3.008
   │                            ╱     ↑recovery
2.8│                          ╱        (2022)
   │                        ╱
2.6│                      ╱
   │                    ╱
2.4│              ●   ●
   │              ↑   2021
2.2│           trough (2.351, 2020)
   └──┬───┬───┬───┬───┬───┬───┬───┬───
     '17 '18 '19 '20 '21 '22 '23 '24
                  ↑shock onset
```

- **R** = the **vertical depth** at trough / baseline (how deep)
- **T** = the **horizontal extent** from shock to recovery year (how long)
- **M** = the **end-state height** at 2024 / baseline (how complete the recovery)
- **Λ** = the **area** between the baseline line and the dipped curve (total cost)

---

## One-line cheat sheet

- **R** = how much was *kept* at the worst point (vertical fraction)
- **T** = how *quickly* the airport came back (horizontal length)
- **M** = how *fully* it returned to normal (end-state share)
- **Λ** = the *total cost* across the dip (area, in GACI·years)

---

## Edge cases

**Risers** (R > 1, Λ < 0). Some airports actually *gain* GACI during a shock by absorbing traffic diverted from collapsing neighbors. Examples: MEM, ANC, LEJ (cargo specialists) during COVID; DOH, IST (geo-bypass hubs) during 9/11 and the 2022 Russia airspace closure. For these airports a negative Λ indicates *cumulative gain* rather than loss. They are flagged as a separate fifth category and analysed under the borrowed-centrality research question (RQ4).

**Never recovered** (T undefined). Some airports do not reach the 90% threshold within the sample. For COVID these are mostly tourism-dependent airports and Russian airports under sanctions. We treat T as right-censored at sample-end (T = 2024 − t_shock) and report Λ accumulated through 2024.

---

## Why four numbers, not one

Janić (2022) collapses resilience into a single scalar (R × 1/T). But two airports can have the same scalar score and very different stories:

- *Airport A*: deep dip but fast bounce-back (R = 0.70, T = 2) — e.g., LAX × COVID
- *Airport B*: shallow dip but slow recovery (R = 0.85, T = 4) — e.g., a regional airport

The two might have identical scalar resilience and face entirely different policy implications. Keeping (R, T, M, Λ) as a **vector** preserves the policy-relevant distinctions, following the recommendation of Reggiani, Nijkamp & Lanzi (2015) for transport-network resilience.

---

## Computation summary

For airport *i* and shock *s* with pre-window [t_s−3, t_s−1] and post-window [t_s, t_s+2]:

```
pre        = mean(GACI_i over [t_s−3, t_s−1])
trough     = min(GACI_i over [t_s, t_s+2])
threshold  = 0.90 × pre                          (90% main; 80%, 95% as sensitivity)
t_rec      = first year t > t_trough with GACI_i(t) ≥ threshold
                                                  (right-censored at 2024 if not reached)
R_i,s      = trough / pre
T_i,s      = t_rec − t_s
M_i,s      = GACI_i(2024) / pre
Λ_i,s      = Σ over years t in [t_s, t_rec] of max(0, pre − GACI_i(t))
```

The same four metrics are computed separately for each of the five sub-components of GACI (Degree, Eigen, NorClose, NorBetweenness, RegionalImportance), enabling the centrality-fragility mapping.

---

## References

- Bruneau, M., Chang, S.E., Eguchi, R.T., Lee, G.C., O'Rourke, T.D., Reinhorn, A.M., Shinozuka, M., Tierney, K., Wallace, W.A., von Winterfeldt, D. (2003). A framework to quantitatively assess and enhance the seismic resilience of communities. *Earthquake Spectra*, 19(4), 733–752.
- Cimellaro, G.P., Reinhorn, A.M., Bruneau, M. (2010). Framework for analytical quantification of disaster resilience. *Engineering Structures*, 32(11), 3639–3649.
- Reggiani, A., Nijkamp, P., Lanzi, D. (2015). Transport resilience and vulnerability: the role of connectivity. *Transportation Research Part A*, 81, 4–15.
- Janić, M. (2022). Analysis and modelling of airport resilience, robustness, and vulnerability: impact of COVID-19 pandemic disease. *The Aeronautical Journal*, 126(1304), 1924–1953.
- Cheung, T.K.Y., Wong, C.W.H., Zhang, A. (2020). The evolution of aviation network: Global airport connectivity index 2006–2016. *Transportation Research Part E*, 133, 101826.
