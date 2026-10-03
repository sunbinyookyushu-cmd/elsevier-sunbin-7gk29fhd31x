# Spatial Heterogeneity of Shocks in Global Air Connectivity and Resilience

**Date:** 2026-05-15
**Lead:** Sunbin Yoo (Managi Lab)
**Data:** GACI 1996–2024 panel (5,428 airports × 29 years × 7 metrics) + country/city GDP series

---

## Motivation

When a global shock disrupts air transport, the economic cost is not evenly distributed across countries — some economies translate aviation disruption into large GDP losses while others absorb the same GACI shock with little damage. The paper documents this spatial heterogeneity, shock by shock, and asks where in the world a unit of aviation disruption hurts the most. The question generalises the connectivity–resilience inversion identified in our previous work (under review at *Nature Cities*) from one city to the global aviation system, and asks whether the inversion appears in GDP space as well.

**The main question.** *Does the GACI → GDP conversion rate vary across countries after a shock?* Which countries pay the highest economic cost for a unit of aviation disruption?

---

## Main Analysis

### Specification (1) — Pooled

$$\text{GDP}_{i,e} = \alpha \cdot \text{GACI}_{i,e} \cdot \text{event}_e + \varepsilon_{i,e}$$

- *i* = city / airport, *e* = shock event
- α = conversion rate between GACI and GDP during shock events

### Specification (2) — Country-heterogeneous

$$\text{GDP}_{i,e} = \sum_C \alpha_C \cdot \mathbf{1}[\text{country}_i = C] \cdot \text{GACI}_{i,e} \cdot \text{event}_e + \varepsilon_{i,e}$$

- α_C = country-specific conversion rate

Plotting α_C as a world choropleth — one panel per shock — is the **main figure**: it visualises which countries pay the highest economic cost for a unit of aviation disruption after each shock.

### Implied GDP loss

For each airport-city pair *i* in each shock *e*:

$$\widehat{\text{GDP loss}}_{i,e} = \hat{\alpha}_C \cdot \text{GACI}_{i,e} \cdot \text{event}_e$$

Reported per event so that the actual GDP loss attributable to GACI disruption can be read off event by event.

### Inversion test: are high-GACI airports more sensitive?

$$\text{GDP}_{i,e} = \alpha \cdot \text{GACI}_{i,e} \cdot \text{event}_e + \beta \cdot \text{GACI}_{i,\text{pre}} \cdot \text{GACI}_{i,e} \cdot \text{event}_e + \varepsilon_{i,e}$$

- β > 0: higher pre-shock GACI ↔ larger GDP loss per unit of GACI
- β = 0: uniform conversion across hub sizes
- β < 0: higher-GACI airports' economies absorb the shock more easily

---

## Additional Analysis: Resilience as Mediator

We define airport resilience following the resilience-triangle lineage (Bruneau et al., 2003; Cimellaro et al., 2010; Janić, 2022) applied to GACI dynamics around each shock. The resilience measure is computed from the GACI series and captures the depth, speed, and persistence of the post-shock dip.

### Specification (3)

$$\text{Resilience}_{i,e} = \alpha_C \cdot \text{GACI}_{i,e} \cdot \text{event}_e + \varepsilon$$

### Specification (4)

$$\text{GDP}_{i,e} = \beta \cdot \text{Resilience}_{i,e} \cdot \text{event}_e + \varepsilon$$

### Specification (5)

$$\text{GDP}_{i,e} = \sum_C \beta_C \cdot \mathbf{1}[\text{country}_i = C] \cdot \text{Resilience}_{i,e} \cdot \text{event}_e + \varepsilon$$

---

## Clean Shock List

| Shock | Year | Pre-window | Type |
|---|---|---|---|
| 9/11 | 2001 | 1998–2000 | Geopolitical / security |
| SARS | 2003 | 2000–2002 | Health |
| Global Financial Crisis | 2008–09 | 2005–2007 | Financial |
| Ebola | 2014 | 2011–2013 | Health / regional |
| COVID-19 | 2020 | 2017–2019 | Health |

Pre-shock baselines are the three-year mean over the pre-window.

---

## Key References

- Bruneau, M. et al. (2003). A framework to quantitatively assess and enhance the seismic resilience of communities. *Earthquake Spectra*, 19(4), 733–752.
- Cheung, T.K.Y., Wong, C.W.H., Zhang, A. (2020). The evolution of aviation network: Global airport connectivity index 2006–2016. *Transportation Research Part E*, 133, 101826.
- Cimellaro, G.P., Reinhorn, A.M., Bruneau, M. (2010). Framework for analytical quantification of disaster resilience. *Engineering Structures*, 32(11), 3639–3649.
- Janić, M. (2022). Analysis and modelling of airport resilience, robustness, and vulnerability: impact of COVID-19 pandemic disease. *The Aeronautical Journal*, 126(1304), 1924–1953.
- Wandelt, S., Zhang, A., Sun, X. (2024). Global Airport Resilience Index: Towards a comprehensive understanding of air transportation resilience. *Transportation Research Part D*, 138, 104796.
