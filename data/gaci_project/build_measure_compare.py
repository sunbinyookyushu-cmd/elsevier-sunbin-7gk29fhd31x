# -*- coding: utf-8 -*-
"""Main IV under alternative connectivity measures: hub quality (cwm) vs total
connectivity (sum). Parses MAINP lines from gaci_tourism_main.log and emits a
side-by-side comparison table -> _measure_compare_table.tex.
MAINP|treat|yv|b|robSE|robP|cluSE|cluP|F|olsB|olsP|N
"""
import re

SD = {'lng': 1.354, 'ln_gaci_cwm': 0.322}   # treatment SDs (from summary stats)
OUT = [('g_vol', 'Goods volume, $\\ln$'),
       ('g_int', 'Goods openness, $\\ln(g/Y)$'),
       ('g_shr', 'Goods trade (\\% GDP)'),
       ('lnpc',  'GDP per capita, $\\ln$'),
       ('lngdp', 'GDP, $\\ln$')]

def stars(p):
    p = float(p)
    return '***' if p < .01 else '**' if p < .05 else '*' if p < .10 else ''

rec = {}
for ln in open('gaci_tourism_main.log', encoding='utf-8', errors='replace'):
    if ln.startswith('MAINP|'):
        f = ln.strip().split('|')
        rec[(f[1], f[2])] = f      # (treat, outcome) -> fields

def cell(treat, out):
    f = rec[(treat, out)]
    b, se, p, F = float(f[3]), float(f[4]), float(f[5]), float(f[9-1+1])
    return b, se, p

def fmt(treat, out, dec=3):
    b, se, p = cell(treat, out)
    d = 2 if out == 'g_shr' else dec
    return '%.*f%s & (%.*f)' % (d, b, stars(p), d, se)

BS = '\\\\'
L = []
L += [r'\begin{table}[t]', r'\centering',
      r'\caption{Main IV estimates under alternative connectivity measures.}',
      r'\label{tab:measure}', r'\begin{threeparttable}', r'\small',
      r'\begin{tabular}{lcccccc}', r'\toprule',
      r' & Volume & Openness & Share & GDP p.c. & GDP & KP $F$ ' + BS,
      r'\midrule',
      r'\multicolumn{7}{l}{\emph{Panel A. Hub quality, $\ln\mathrm{GACI}_{cwm}$ (headline)}}' + BS]

def panel(treat):
    Fval = float(rec[(treat, 'g_vol')][8])
    cells = []
    for o, _ in OUT:
        b, se, p = cell(treat, o)
        d = 2 if o == 'g_shr' else 3
        cells.append('%.*f%s' % (d, b, stars(p)))
    se_cells = []
    for o, _ in OUT:
        b, se, p = cell(treat, o)
        d = 2 if o == 'g_shr' else 3
        se_cells.append('(%.*f)' % (d, se))
    row1 = 'IV (2SLS) & ' + ' & '.join(cells) + ' & %.1f %s' % (Fval, BS)
    row2 = ' & ' + ' & '.join(se_cells) + ' & ' + BS
    # OLS row
    ols = []
    for o, _ in OUT:
        f = rec[(treat, o)]
        ob, op = float(f[9]), float(f[10])
        d = 2 if o == 'g_shr' else 3
        ols.append('%.*f%s' % (d, ob, stars(op)))
    row0 = 'OLS & ' + ' & '.join(ols) + ' & --- ' + BS
    return [row0, row1, row2]

L += panel('ln_gaci_cwm')
L += [r'\addlinespace',
      r'\multicolumn{7}{l}{\emph{Panel B. Total connectivity, $\ln\mathrm{GACI}_{sum}$}}' + BS]
L += panel('lng')
L += [r'\midrule',
      r'\multicolumn{7}{l}{\emph{Implied 1996--2023 aggregate goods-trade gain (intensity channel)}}' + BS,
      r'Hub quality (cwm) & \multicolumn{6}{l}{\$7.86 trillion ($\approx$17\% of 2023 world goods trade)} ' + BS,
      r'Total conn.\ (sum) & \multicolumn{6}{l}{\$7.60 trillion ($\approx$16\% of 2023 world goods trade)} ' + BS,
      r'\bottomrule', r'\end{tabular}',
      r'\begin{tablenotes}\footnotesize',
      (r'\item Country and year FE; population control; robust SE in parentheses. '
       r'Each panel uses a different national connectivity summary. The two measures '
       r'are on different scales, so the raw elasticities are not directly comparable; '
       r'what is robust is the \emph{qualitative pattern} (volume and openness positive '
       r'and significant, income outcomes imprecise), the exact decomposition '
       r'$\beta_{vol}=\beta_{int}+\beta_{gdp}$ (which holds in both panels), and the '
       r'implied aggregate counterfactual, which differs by only about 3\% across '
       r'measures. The cwm measure is preferred for the headline because its first '
       r'stage is stronger ($F=18.0$ vs.\ $9.7$). '
       r'\sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.'),
      r'\end{tablenotes}', r'\end{threeparttable}', r'\end{table}']

open('_measure_compare_table.tex', 'w', encoding='utf-8').write('\n'.join(L))
print('\n'.join(L))
