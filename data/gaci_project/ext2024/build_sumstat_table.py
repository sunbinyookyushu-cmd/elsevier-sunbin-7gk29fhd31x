# -*- coding: utf-8 -*-
"""Build the summary-statistics LaTeX table on the estimation sample -> _sumstat_table.tex"""
import pandas as pd, numpy as np

df = pd.read_csv('gaci_panel_3iv.csv')
num = lambda c: pd.to_numeric(df[c], errors='coerce')
df['g_vol'] = num('merch_intensity') + num('lngdp')

BS = '\\\\'   # row terminator
groups = [
 ('Connectivity', [
   (r'Hub quality, $\ln\mathrm{GACI}_{cwm}$ (cap.-wtd.\ mean)', 'ln_gaci_cwm'),
   (r'Total connectivity, $\ln\mathrm{GACI}_{sum}$', 'lnG'),
   (r'Number of airports', 'n_air')]),
 ('Trade outcomes', [
   (r'Goods-trade volume, $\ln$', 'g_vol'),
   (r'Goods openness, $\ln(\text{goods}/\text{GDP})$', 'merch_intensity'),
   (r'Goods trade (\% of GDP)', 'merch_share')]),
 ('Income', [
   (r'GDP per capita, $\ln$', 'lnpc'),
   (r'GDP, $\ln$ (total)', 'lngdp')]),
 ('Instrument and heritage', [
   (r'Tourism-heritage instrument', 'tourism_int'),
   (r'Natural + mixed UNESCO sites (cum.)', 'nat_endow')]),
 ('Controls', [
   (r'Population, $\ln$', 'lnpop'),
   (r'Land area, $\ln$', 'lnland'),
   (r'Remoteness, $\ln$ sea distance', 'ln_remote')]),
]

def row(lbl, col):
    s = num(col).dropna()
    return '%s & %d & %.2f & %.2f & %.2f & %.2f & %.2f %s' % (
        lbl, len(s), s.mean(), s.std(), s.min(), s.median(), s.max(), BS)

L = []
L += [r'\begin{table}[t]', r'\centering',
      r'\caption{Summary statistics, estimation sample (184 countries, 1996--2023).}',
      r'\label{tab:sumstat}', r'\begin{threeparttable}', r'\small',
      r'\begin{tabular}{lrrrrrr}', r'\toprule',
      r'Variable & $N$ & Mean & SD & Min & Median & Max ' + BS, r'\midrule']
for g, items in groups:
    L.append(r'\multicolumn{7}{l}{\emph{%s}}%s' % (g, BS))
    for lbl, col in items:
        L.append(row(lbl, col))
    L.append(r'\addlinespace')
L[-1] = r'\bottomrule'
L += [r'\end{tabular}', r'\begin{tablenotes}\footnotesize',
      (r'\item Estimation sample: 184 countries over 1996--2023 (4{,}643 country-year '
       r'observations; remoteness available for 4{,}635). GACI = Global Air Connectivity '
       r'Index. Hub quality is the capacity-weighted mean of airport-level GACI within a '
       r'country; total connectivity is the country sum. The tourism-heritage instrument is '
       r'global tourism demand (min--max scaled to $[0,1]$) interacted with the fixed '
       r'natural-plus-mixed heritage endowment. Goods trade is merchandise trade (WDI); '
       r'services and tourism are excluded by construction.'),
      r'\end{tablenotes}', r'\end{threeparttable}', r'\end{table}']

out = '\n'.join(L)
open('_sumstat_table.tex', 'w', encoding='utf-8').write(out)
print(out)
