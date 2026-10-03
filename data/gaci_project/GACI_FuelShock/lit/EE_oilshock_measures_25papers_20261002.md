# Energy Economics oil-shock papers (25, 2023–2026): how oil price fluctuation is measured and identified

Source: user's ScienceDirect export `Downloads/ScienceDirect_articles_02Oct2026_08-08-20.098.zip` (25 PDFs). Read on 2026-10-02 by four agents from the full text (front matter, data, method, results). Fields not in the text were left as "not stated" by the agents.

## 1. Oil price measure (independent variable) by type

| Type | n | Papers |
|---|---|---|
| Ready (2018) daily decomposition (supply / demand / risk from oil futures, oil-producer stock index, VIX innovations) | 9 | 04, 05, 07, 09, 15, 16, 17, 22, 24 |
| Raw oil price (Brent / WTI / WDI), log or % change, often split into rises and falls | 5 | 02, 03, 06, 18, 23 |
| Baumeister & Hamilton (2019) structural shocks | 4 | 01, 12 (own BH-style estimation), 14, 21 (+17 secondary) |
| Kilian (2009)-type SVAR decomposition | 3 | 10 (observed proxies relabelled), 11, 13 |
| Expected / perceived oil price | 2 | 08 (Baumeister-Kilian 2016 expectations), 25 (perceived shock from Consensus forecasts, sign-restricted FAVAR) |
| Oil price uncertainty (OVX, GARCH SD, implied vol) | 2 | 19, 20 |
| Känzig (2021) | 0 | only in the appendix of 17 |

No paper uses an oil shock as an instrument for a price (16 mentions a referee request), local projections, Driscoll-Kraay SEs, or a shock x pre-determined unit characteristic.

## 2. Paper list

| # | Citation | Dependent variable | Oil measure | Method | Heterogeneity |
|---|---|---|---|---|---|
| 01 | Li (2025) EE 145:108440, doi:10.1016/j.eneco.2025.108440 | US investor sentiment | BH (2019) series, +/- partial sums | NARDL | none |
| 02 | Bruna & Van Tran (2023) EE 128:107130, doi:10.1016/j.eneco.2023.107130 | EUR/USD | Brent quarterly yoy %, asymmetry dummy | sign-restricted BVAR | none |
| 03 | Tan & Uprasen (2023) EE 126:107033, doi:10.1016/j.eneco.2023.107033 | income inequality, 8 ASEAN | WDI real crude price + GARCH vol, +/- | panel NARDL (PMG), country FE | exporter/importer (sample average) |
| 04 | Sevillano et al. (2024) EE 131:107398, doi:10.1016/j.eneco.2024.107398 | 11 US sector returns/vol | Ready | TVP-VAR connectedness, wavelets | by sector, descriptive; fn 7 says Ready shocks are "influenced by stock markets rather than being external variables" |
| 05 | Al-Fayoumi, Bouri & Abuzayed (2023) EE 126:106930, doi:10.1016/j.eneco.2023.106930 | GCC sector returns/vol | Ready | TVP-VAR + quantile VAR connectedness | sectors, COVID phases |
| 06 | Lin, Xiao & Chai (2023) EE 124:106779, doi:10.1016/j.eneco.2023.106779 | output, CPI, rate, FX (US, CN, EA, JP) | WTI/Brent log change; Mork and Hamilton net-increase | TVP-VAR-SV, Cholesky | per economy |
| 07 | Zhao et al. (2023) EE 126:106921, doi:10.1016/j.eneco.2023.106921 | EUR/USD volatility risk | Ready | GARCH, VAR FEVD, LSTM | pre/post conflict |
| 08 | Lam & Ojede (2025) EE 148:108653, doi:10.1016/j.eneco.2025.108653 | 4 African exchange rates | Baumeister-Kilian (2016) 3-12m oil price expectations | adaptive-learning RLS | per country |
| 09 | Lu et al. (2024) EE 134:107580, doi:10.1016/j.eneco.2024.107580 | DJSI World extremes | Ready | GEV tail dependence | up/down tails |
| 10 | Yang, Dong, Du & Du (2023) EE 127:107099, doi:10.1016/j.eneco.2023.107099 | inflation CN/US/EU | GPR + oil production, world IP, real WTI | TVP-SV-VAR recursive | 3 economies |
| 11 | Benk & Gillman (2023) EE 126:106878, doi:10.1016/j.eneco.2023.106878 | real oil price; US GDP, CPI | Kilian (2009) + money + expectations shocks | recursive SVAR; shocks as predetermined regressors | none |
| 12 | Liu, Tian, Zhao & Liu (2026) EE 159:109403, doi:10.1016/j.eneco.2026.109403 | China inflation tail risk | BH-style 4-component Bayesian SVAR | Bayesian SVAR, quantile IaR | none |
| 13 | Kumar & Mallick (2024) EE 129:107152, doi:10.1016/j.eneco.2023.107152 | real oil price | Kilian-type SVAR + GPR | Cholesky vs max-FEV; TVP-VAR | pre/post 2008 |
| 14 | Iania, Lyrio & Nersisyan (2024) EE 139:107940, doi:10.1016/j.eneco.2024.107940 | bond risk premia, 15 countries | BH (2019) 4 shocks, block-exogenous | affine term structure per country | exporter / importer groups |
| 15 | Chatziantoniou et al. (2023) EE 120:106627, doi:10.1016/j.eneco.2023.106627 | 8 USD exchange rates | Ready | TVP-VAR connectedness | exporters vs importers |
| 16 | Brahmana & Aslam (2026) EE 162:109565, doi:10.1016/j.eneco.2026.109565 | private equity / unicorn returns | Ready | VAR, Markov switching | per index; fn 1 referee asked for oil shocks as instrument + mediator |
| 17 | Polat, Cunado, Cepni & Gupta (2025) EE 141:108128, doi:10.1016/j.eneco.2024.108128 | 50 US state stock/muni returns, connectedness | Ready daily; BH monthly; Känzig in appendix | state-by-state OLS, Diebold-Yilmaz | per state |
| 18 | Ben Cheikh, Ben Zaied & Mattoussi (2023) EE 128:107128, doi:10.1016/j.eneco.2023.107128 | euro-area inflation | Brent log change | LVSTR with GPR regime | GPR state; EPU/MPU alternatives |
| 19 | Elder & Payne (2024) EE 131:107338, doi:10.1016/j.eneco.2024.107338 | US unemployment by gender/age | oil price uncertainty (GARCH-in-mean SD, implied vol, SWARCH) | recursive SVAR | per group; gap as outcome; sample ends 2019:12 |
| 20 | Shahbaz et al. (2024) EE 136:107732, doi:10.1016/j.eneco.2024.107732 | metal volatility | OVX (oil price uncertainty) | TVP-VAR connectedness, quantile regression | none |
| 21 | Hu, Yu & Zhong (2023) EE 125:106890, doi:10.1016/j.eneco.2023.106890 | US firm green patents | BH (2019) demand and supply shocks, annual averages; Ready robustness | firm-FE panel, no year FE, firm-clustered SE | shock x firm traits (median splits by year, not pre-determined); "Oil User" SIC group includes air transport (SIC 45) |
| 22 | Tiwari et al. (2025) EE 141:108101, doi:10.1016/j.eneco.2024.108101 | 8 EM stock indices | Ready (then log-differenced) | TVP-VAR R2 connectedness, quantile causality | none |
| 23 | Considine et al. (2023) EE 127:106934, doi:10.1016/j.eneco.2023.106934 | inflation, oil output, critical minerals (36 countries) | log real Brent, GIRF 1 SD | GVAR, oil weakly exogenous | per country |
| 24 | Yang, Geng & Liang (2024) EE 139:107910, doi:10.1016/j.eneco.2024.107910 | implied-volatility indices, 9 countries | Ready | Diebold-Yilmaz spillovers | per country/regime |
| 25 | An, Sheng & Zheng (2023) EE 126:106950, doi:10.1016/j.eneco.2023.106950 | inflation expectations, 84 economies | perceived oil shock (sign restrictions on forecasts) | Bayesian FAVAR | advanced vs emerging |

## 3. Implications for the GACI fuel-shock paper (target: Energy Economics)

- Our design (Känzig and BH as instruments for the Gulf Coast jet price; country/airport x month panel; shock x pre-determined resilience; DK SEs) is more design-based than all 25. Closest analogue: #21 (BH shocks in a unit-FE panel with shock x unit traits; we improve on it with month FE, pre-determined moderator, cross-sectionally robust SEs).
- Most common robustness requests in this set: alternative shock series (Kilian-type, raw price, Ready), WTI vs Brent (for us: Gulf Coast vs Singapore/Rotterdam jet), pre/post 2008 and excluding 2008-09, rises vs falls, longer horizons, alternative outcome and moderator definitions, global-demand contamination check (#25), mechanism/mediation (#16).
- Ready shocks: avoid as instrument (#04 fn 7: not external); state sign convention and BH component explicitly (#21 did not).
- Real-sector quantity outcomes are absent from this set (finance 14, macro 8, innovation 1, oil market 2): air service is a distinctive outcome for EE.
