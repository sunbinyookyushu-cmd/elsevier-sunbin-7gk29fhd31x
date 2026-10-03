# The Carbon Footprint of Air Connectivity
## Network Position and the Carbon Cost of Global Aviation, 1996–2023

**Date:** 2026-08-09
**Lead:** Sunbin Yoo (Managi Lab)
**Companion paper:** *Global Air Connectivity and Trade Openness, 1996–2023* (GACI–trade manuscript, TR-A submission)
**Data:** GACI country panel (184 countries × 1996–2023, `gaci_panel.csv`) + EDGAR aviation CO₂ (to be constructed)

---

## 1. Motivation

Our companion paper establishes the **benefit side** of global air connectivity: instrumented by heritage-driven tourism demand, a 1% improvement in national hub quality raises goods-trade volume by 2.3%, and two decades of connectivity growth account for roughly \$7.8 trillion of 2023 goods trade. This project quantifies the **cost side of the same ledger**: the carbon emitted to produce that connectivity.

The question is *not* whether flying emits CO₂ — it trivially does. The question is whether **connectivity is carbon-efficient**. GACI measures a country's *network position* (centrality, reach, hub standing), not its traffic volume: two countries with identical seat-kilometres can occupy very different positions in the world network. Whether a unit of network position costs more or less than a unit of emissions — and whether the answer depends on *how* connectivity is built (hub concentration versus airport proliferation) — is an open empirical question with direct policy content. Governments subsidise routes and build airports to buy connectivity; no one has priced that purchase in carbon.

Three features make this a low-cost, high-payoff companion study:

1. **The entire empirical apparatus already exists.** Panel, instrument, fixed-effects structure, heterogeneity moderators, COVID shock module, and counterfactual code carry over from the trade paper; only the outcome variable is new.
2. **The identification concern is weaker, not stronger.** Reverse causality from a country's aviation emissions to its network position is implausible; the IV serves as reinforcement rather than rescue, and OLS/2SLS are reported side by side.
3. **The policy translation is immediate.** An estimated connectivity–CO₂ elasticity converts directly into (i) the implicit abatement cost of connectivity cuts (COVID 2020), and (ii) the SAF blending trajectory required to offset projected connectivity growth (ReFuelEU / CORSIA scenarios).

## 2. Research Questions

**RQ0 (headline).** What is the carbon price of air connectivity — the elasticity of national aviation CO₂ with respect to network position — and does network *structure* change that price?

**RQ1 — Efficiency.** Is the CO₂–connectivity elasticity below or above unity? β < 1 means network-position gains outrun emissions (hub-and-spoke consolidation creates connections faster than flights); β > 1 means the pursuit of connectivity amplifies emissions.

**RQ2 — Structure.** Which growth path is carbon-cheaper per unit of connectivity: hub-quality deepening (GACI_cwm, GACI_max) or airport-system expansion (GACI_sum)? This takes the hub-and-spoke versus point-to-point decarbonisation debate to a global country panel.

**RQ3 — Distribution and timing.** Who faces the highest carbon price of connectivity — by baseline income, baseline connectivity, remoteness — and did the price fall after 2010 (fleet renewal, load-factor gains, Gulf/Asian hub expansion)?

## 3. Hypotheses

| | Hypothesis | Test |
|---|---|---|
| **H1** | Connectivity causally raises aviation CO₂, with elasticity **different from 1** (direction left open ex ante; β < 1 ⇒ carbon-efficient network growth, β > 1 ⇒ carbon-amplifying) | Main 2SLS; Wald test H₀: β = 1 |
| **H2** | Hub-quality growth (cwm/max) carries a **lower** CO₂ elasticity than airport-proliferation growth (sum): hub-and-spoke is the low-carbon path to connectivity | Cross-panel comparison of β across the three GACI measures (stacked regression / SUR for SE of the difference) |
| **H3** | The carbon price of connectivity **fell after 2010** (fleet and load-factor efficiency era) | Post-2010 interaction |
| **H4** | Poorer, more remote, less-connected countries obtain **more connectivity per tonne of CO₂** — so uniform aviation-carbon regulation (CORSIA-type) is regressive | Interaction-IV with baseline income, baseline connectivity, remoteness; cross-read with the trade paper's openness elasticities |

*Note on H1:* the hypothesis is registered as β ≠ 1 with the direction left open. Either sign sustains the paper — β < 1 is a network-efficiency finding, β > 1 is a carbon-amplification finding.

## 4. Data

### 4.1 Carried over from the companion paper (complete)

| Variable | Role | Source |
|---|---|---|
| ln GACI_cwm / GACI_max / GACI_sum | Treatment (3 measures) | `gaci_panel.csv` |
| tourism_int = global tourist arrivals (min–max) × ln(1 + natural+mixed UNESCO sites) | **Instrument (fixed, as decided — identical to trade paper, Eq. 7)** | `gaci_panel.csv` |
| ln population; country FE; year FE | Controls | `gaci_panel.csv` |
| Baseline income, baseline connectivity (1996), ln mean sea distance (CERDI) | Moderators | `gaci_panel_hetero.csv` |
| Number of airports with scheduled service | Volume-control robustness | `gaci_panel.csv` |

### 4.2 New outcome: country-year aviation CO₂ (the one construction task)

Two-tier construction from EDGAR:

- **(a) Domestic aviation** (IPCC 1.A.3.a): EDGAR country-year time series, used as reported.
- **(b) International aviation**: excluded from EDGAR national totals by bunker-fuel convention — but GACI is predominantly *international* connectivity, so this tier is essential. Construction: overlay the **EDGAR gridded (0.1°) aviation LTO (landing/take-off) sector** on our existing airport coordinates (`airport_coords_merged.csv`), aggregate grid cells around airports to the country level. LTO emissions occur physically at the airport, so country attribution is defensible, and the treatment (airport-level GACI aggregated to country) and outcome share the same aggregation unit. **This constructed series is itself a data contribution.**
- **Cross-validation / fallback:** IEA "international aviation bunkers" country series (fuel-sold basis) and Climate Watch aviation bunkers. If the EDGAR grid route fails, the bunker route is a measurement substitution, not a design change.

### 4.3 Pre-construction verification checklist (do not finalise design before checking)

1. EDGAR latest release: does it separate aviation into LTO / CDS / CRS sectors, and at which resolution and frequency?
2. Coverage 1996–2023 for both country series and gridmaps (EDGAR historically starts 1970; confirm the current end year).
3. Units: confirm tonnes **CO₂**, not tonnes carbon (avoid the ODIAC ×44/12 trap).
4. Country coverage overlap with the 184-country estimation sample; report any attrition and re-run the trade-paper first stage on the matched sample before interpreting.
5. All SAF / policy figures in §7 (ReFuelEU trajectory, CORSIA baselines, SAF production volumes) to be reference-checked before drafting.

## 5. Empirical Strategy

### 5.1 Main specification (trade-paper Eqs. 1 & 7, outcome swapped)

Second stage:

> ln CO₂ᵃⁱʳ_it = β · ln GACI_it + γ · ln pop_it + α_i + δ_t + ε_it

First stage (instrument as decided — tourism–heritage shift-share):

> ln GACI_it = π₁ · tourism_int_it + π₂ · ln pop_it + μ_i + λ_t + ν_it

Reporting format replicates the trade paper's Table 2: three panels (cwm / max / sum), each with OLS, first stage (KP F), and 2SLS rows; heteroskedasticity-robust SEs.

- **H1 test:** Wald test of β = 1 in the 2SLS row of each panel.
- **H2 test:** stacked regression across measures with interacted treatment, or SUR, to put a standard error on β_cwm − β_sum.

### 5.2 Identification discussion (the genuinely new writing)

With a CO₂ outcome the exclusion-restriction conversation changes:

- **Concern:** heritage-driven tourist flights emit CO₂ *directly*, not only through measured network position. **Defence (i):** tourism-induced flights *are* network connections; the channel is subsumed in GACI under a reduced-form reading ("the carbon footprint of exogenous connectivity"). **Defence (ii) — volume-versus-position robustness:** add airport count (held variable) and, where available, seat/frequency proxies to the second stage. If β survives volume controls, the effect is network-structural; if it collapses onto volume, the paper honestly reports that connectivity's carbon cost is a traffic phenomenon. Both readings are publishable; the design distinguishes them.
- **Reverse causality** (emissions → network position) is implausible, so OLS and 2SLS are presented as co-equal evidence with the IV as reinforcement.
- Carry over the trade paper's falsification suite unchanged: pre-period placebo, alternative instruments (air/sea distance), over-identification tests.

### 5.3 Heterogeneity and timing (trade-paper Eq. 8 structure)

Interaction-IV with the three mean-centred moderators (baseline income, baseline connectivity, remoteness), both terms instrumented; post-2010 interaction for H3. Quartile figure replicated with CO₂ elasticities. Cross-reading H4 with the trade paper's heterogeneity yields the distribution of **"dollars of connectivity-induced trade per tonne of CO₂"** across country groups — the equity headline.

### 5.4 COVID module: the implicit abatement cost of connectivity cuts

The 2019–2020 collapse (connectivity fell in 140 of 177 countries) delivers observed aviation-CO₂ reductions alongside the companion paper's \$1.8 trillion trade disruption. Combining the two yields the **implicit cost per tonne of CO₂ abated by cutting connectivity** — expected to be orders of magnitude above any carbon price, which is the empirical case for technology (SAF) over demand suppression. One headline number, one paragraph, already-built shock code.

## 6. SAF Scenario Section (policy translation — explicitly *not* causal estimation)

SAF adoption (≈0.1–0.3% of jet fuel through 2023; verify) is too small and too recent for panel identification; any DiD on mandate adoption would be underpowered and invite misreading. Instead, SAF enters as the concluding policy section that converts β̂ into forward-looking statements:

1. **Projection:** β̂ × projected connectivity growth → aviation CO₂ paths to 2030/2050.
2. **Offset trajectory:** overlay ReFuelEU blending mandates (2% in 2025 → 6% in 2030 → 70% in 2050) and CORSIA scenarios → the year at which the SAF roadmap offsets connectivity-driven emission growth, and the blending share required to hold emissions flat.
3. **Geographic mismatch (links to H4):** SAF supply concentrates at advanced-economy hubs while marginal emission growth concentrates in low-income/remote countries with the highest connectivity payoffs → distributional critique of uniform blending mandates.
4. **COVID cross-check:** the SAF volume equivalent to the 2020 demand-suppression abatement — demand cuts versus fuel switching in one comparison.

All mandate trajectories and SAF production figures reference-checked before drafting (§4.3, item 5).

## 7. Planned Tables and Figures

| Item | Content | Reuse of existing code |
|---|---|---|
| Table 1 | Summary statistics (+ aviation CO₂ rows) | ~90% (`build_sumstat_table.py`) |
| Table 2 | Main results: OLS / first stage / 2SLS × 3 GACI measures + β=1 Wald | ~95% (`gaci_main_table.do`) |
| Table 3 | Heterogeneity interaction-IV (income / baseline conn. / remoteness) | ~95% (`gaci_hetero_table.do`) |
| Table 4 | Temporal heterogeneity (post-2010) | ~95% (`gaci_temporal_table.do`) |
| Table 5 | Robustness: volume controls, alternative CO₂ measures (bunker series), over-ID, placebo | ~50% (new columns) |
| Fig 1 | Aviation CO₂ map, 2023 | map pipeline reuse (`build_gaci_map_v2.py`) |
| Fig 2 | Carbon intensity of connectivity (CO₂/GACI), by continent, 1996–2023 | trend pipeline reuse |
| Fig 3 | CO₂ elasticity by income & connectivity quartile | ~95% (`build_hetero_quartile_fig.py`) |
| Fig 4 | SAF scenario paths: projected emissions vs. ReFuelEU/CORSIA offset trajectories | new |

## 8. Contributions

1. **First global, causal connectivity–emissions elasticity.** Existing literature relates traffic volumes to emissions descriptively or at route level; no study prices *network position* in carbon, at global scale, with an identification strategy.
2. **Network structure as a decarbonisation lever.** The three-measure comparison turns the hub-and-spoke versus point-to-point debate into an estimable question on a 184-country panel.
3. **The distributional ledger of aviation carbon policy.** Connectivity benefits and carbon costs are geographically mismatched; combined with the companion paper, the framework prices both sides and shows where uniform carbon regulation of aviation is regressive (CORSIA, blending mandates).

## 9. Target Journals and Risks

**Target:** Transportation Research Part D (first choice — natural division of labour with the TR-A trade paper); Journal of Air Transport Management (second).

| Risk | Mitigation |
|---|---|
| EDGAR international-aviation attribution differs from expectation | Fall back to IEA/Climate Watch bunker series (measurement change, not design change) |
| First stage weakens on the CO₂-matched sample (EDGAR coverage < 184 countries) | Verify sample overlap first (§4.3 item 4); report matched-sample first stage before any 2SLS |
| "Obvious result" referee critique | The paper tests β = 1 and structure differences, not whether flying emits; state in the introduction: *"we test whether connectivity is carbon-efficient, not whether aviation emits"* |
| LTO-only international measure misses cruise emissions | Frame as territorial/airport-attributable emissions (consistent with LTO-based airport regulation); bunker-series robustness captures total fuel sold |

## 10. Workplan

1. **EDGAR specification check** (§4.3 items 1–4) — go/no-go gate for the grid construction route.
2. Construct country-year aviation CO₂ (two-tier); descriptive Fig 1–2; sample-overlap report.
3. Pilot regression: Table 2 skeleton (OLS + 2SLS, cwm only) on matched sample.
4. Full Tables 2–4; H1/H2 tests.
5. Robustness (Table 5) + COVID module.
6. SAF scenario section (after reference-checking all policy figures).
7. Draft manuscript on the companion paper's LaTeX skeleton.
