# -*- coding: utf-8 -*-
"""Country-level implied effects of connectivity growth (1996->2023), consistent
with the headline cwm IV elasticities, with delta-method standard errors.

NOTE: these are NOT separately estimated per-country IV coefficients (a single
country's 28-year series cannot identify the IV, since the instrument is the
common global tourism shift scaled by a fixed heritage stock). They are the
pooled IV elasticities applied to each country's observed change in hub quality,
with delta-method SEs propagated from the elasticity SEs. Cross-outcome
differences are therefore mechanical (each is beta_k * dG_i); the country
variation comes entirely from dG_i.

Outputs: _country_estimates.csv (all 184) and _country_estimates_table.tex.
"""
import pandas as pd, numpy as np

# pooled cwm IV estimates (robust SE), from gaci_tourism_main.log (MAINP ln_gaci_cwm)
BETA = {'vol': (2.303, 0.776), 'int': (1.302, 0.662),
        'pc':  (0.514, 0.475), 'gdp': (1.001, 0.680)}
B_INT, SE_INT = BETA['int']

df = pd.read_csv('gaci_panel_3iv.csv')
for c in ['y', 'ln_gaci_cwm', 'merch_intensity', 'lngdp']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['g_vol'] = df['merch_intensity'] + df['lngdp']
df = df.dropna(subset=['ln_gaci_cwm', 'g_vol'])

rows = []
for c, g in df.groupby('c'):
    g = g.sort_values('y')
    f, l = g.iloc[0], g.iloc[-1]
    dG = l['ln_gaci_cwm'] - f['ln_gaci_cwm']
    goods_last = np.exp(l['g_vol'])            # USD goods trade, last year
    rec = {'country': c, 'y0': int(f['y']), 'y1': int(l['y']), 'dlnGACI': dG,
           'goods_last_usd': goods_last}
    # implied effect on each log outcome: beta_k * dG ; SE = SE_k * |dG|
    for k, (b, se) in BETA.items():
        rec[f'eff_{k}'] = b * dG
        rec[f'se_{k}']  = se * abs(dG)
    # implied trade-gain in USD (intensity channel) + delta-method SE
    share = 1 - np.exp(-B_INT * dG)
    gain = goods_last * share
    dgain_dbeta = goods_last * dG * np.exp(-B_INT * dG)   # d gain / d beta
    rec['gain_usd'] = gain
    rec['gain_se_usd'] = abs(dgain_dbeta) * SE_INT
    rec['share_attr'] = share
    rows.append(rec)

cc = pd.DataFrame(rows).sort_values('gain_usd', ascending=False).reset_index(drop=True)
cc.to_csv('_country_estimates.csv', index=False)
TOT = cc['gain_usd'].sum()
print('countries: %d   total trade gain: $%.2fT' % (len(cc), TOT / 1e12))

# ---- LaTeX: top 25 + bottom 5 (connectivity losers) + world total ----
BS = '\\\\'
def fmt_est(b, se, dec=2):
    return '%.*f (%.*f)' % (dec, b, dec, se)
def fmt_gain(g, se):  # in $bn
    return '%.1f (%.1f)' % (g / 1e9, se / 1e9)

def line(r):
    return ' & '.join([
        r['country'],
        '%.2f' % r['dlnGACI'],
        fmt_est(r['eff_int'], r['se_int']),
        fmt_est(r['eff_vol'], r['se_vol']),
        fmt_est(r['eff_gdp'], r['se_gdp']),
        fmt_gain(r['gain_usd'], r['gain_se_usd']),
    ]) + ' ' + BS

top = cc.head(25)
bot = cc.tail(5)

L = []
L += [r'\begin{table}[t]', r'\centering',
      r'\caption{Country-level implied effects of air-connectivity growth, 1996--2023.}',
      r'\label{tab:country}', r'\begin{threeparttable}', r'\scriptsize',
      r'\begin{tabular}{lrcccr}', r'\toprule',
      (r'Country & $\Delta\ln\mathrm{GACI}_{cwm}$ & Openness & Volume & GDP '
       r'& Trade gain ' + BS),
      (r' & & $\beta_{int}\Delta G$ & $\beta_{vol}\Delta G$ & $\beta_{gdp}\Delta G$ '
       r'& (\$bn) ' + BS),
      r'\midrule',
      r'\multicolumn{6}{l}{\emph{Largest implied trade gains (top 25)}}' + BS]
for _, r in top.iterrows():
    L.append(line(r))
L += [r'\addlinespace',
      r'\multicolumn{6}{l}{\emph{Connectivity decliners (bottom 5)}}' + BS]
for _, r in bot.iterrows():
    L.append(line(r))
L += [r'\midrule',
      r'World total & --- & --- & --- & --- & %.0f ' % (TOT / 1e9) + BS,
      r'\bottomrule', r'\end{tabular}',
      r'\begin{tablenotes}\scriptsize',
      (r'\item Implied effects apply the pooled cwm IV elasticities---openness '
       r'$\beta_{int}=1.302\,(0.662)$, volume $\beta_{vol}=2.303\,(0.776)$, GDP '
       r'$\beta_{gdp}=1.001\,(0.680)$---to the change in hub quality '
       r'$\Delta\ln\mathrm{GACI}_{cwm}$ observed for each country '
       r'between its first and last sample '
       r'year. Columns 3--5 report the implied log-point effect $\beta_k\Delta G$ '
       r'with delta-method SE $\mathrm{SE}(\beta_k)\,|\Delta G|$ in parentheses. '
       r'The trade gain is $\text{goods}\times(1-e^{-\beta_{int}\Delta G})$ with '
       r'delta-method SE. These are not separately estimated per-country '
       r'regressions: a single country cannot identify the IV, so cross-country '
       r'variation comes only through $\Delta G$. World total is summed over all '
       r'184 countries; the full table is in the supplementary file '
       r'\texttt{\_country\_estimates.csv}.'),
      r'\end{tablenotes}', r'\end{threeparttable}', r'\end{table}']

open('_country_estimates_table.tex', 'w', encoding='utf-8').write('\n'.join(L))
print('wrote _country_estimates_table.tex and _country_estimates.csv')
print(cc.head(6)[['country','dlnGACI','eff_int','se_int','gain_usd','gain_se_usd']].to_string())
