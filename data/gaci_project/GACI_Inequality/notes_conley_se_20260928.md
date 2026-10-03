# Country-clustered vs Conley SE — 2026-09-28

Scripts: `15_conley_se.py` (own implementation, two-way FE 2SLS sandwich with product kernel; `_conley_se_results.csv`), `16_acreg_check.do` (acreg 1.1.0 cross-check; `_acreg_results.csv`), `_panel_coords.csv` (Natural Earth centroids + airport-mean fallback for 27 islands/city states).
Check: own cluster SE 0.198 vs Stata reghdfe 0.194 (dof convention); coefficients identical (0.495 / 0.651).

## Headline 2SLS, ln GACI_max -> ln market Gini (b = 0.495) / ln disposable Gini (b = 0.651)
| SE | market | disp |
|---|---|---|
| country cluster (Stata) | 0.194** | 0.241*** |
| Conley 1000 km, all lags uniform | 0.203** | 0.248*** |
| Conley 2000 km, all lags uniform | 0.224** | 0.267** |
| Conley 3000 km, all lags uniform | 0.250** | 0.285** |
| Conley 5000 km, all lags uniform | 0.289* | 0.322** |
| Conley 2000 km, Bartlett lag 10 (own) | 0.139*** | 0.168*** |
| acreg 2000 km, Bartlett lag 30, hac | 0.161*** | 0.201*** |
| acreg 2000 km, Bartlett lag 10, hac | 0.125*** | 0.155*** |
| acreg 1000 km, Bartlett lag 30, hac | 0.160*** | 0.200*** |

Reading: Gini residuals are highly persistent, so the temporal kernel dominates. Any Bartlett down-weighting of long lags (acreg lagcutoff, own L=10) gives SEs *below* the cluster SE; spatial correlation up to 2000–3000 km adds 15–30% on top of clustering. Decision: keep country clustering as the main SE (allows arbitrary within-country persistence, 163 clusters) and report Conley with uniform lags at 2000/3000 km as robustness; do not adopt the lag-truncated Conley SEs because they are smaller only because they assume the persistence dies out.

## Group regressions (2SLS, uniform lags)
Income: d8–d10 and top 1% stay significant at 5–10% to 2000 km, d10 and top 1% to 3000 km. Share (identity-based): d3 and bottom 50% significant to 2000–3000 km; d4/d5 lose at 2000 km.
