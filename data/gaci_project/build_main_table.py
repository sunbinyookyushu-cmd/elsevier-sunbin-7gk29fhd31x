# -*- coding: utf-8 -*-
"""Main results table the way the layout is envisioned:
outcomes {openness, volume, GDP} x treatments {cwm, sum} x {OLS, first stage, 2SLS},
robust SE.  OLS/2SLS from gaci_tourism_main.log (MAINP), first stage computed here.
-> _main_table.tex
"""
import pandas as pd, numpy as np, statsmodels.api as sm

# ---------- 1. OLS + 2SLS (robust) from the log ----------
rec = {}
for ln in open('gaci_tourism_main.log', encoding='utf-8', errors='replace'):
    if ln.startswith('MAINP|'):
        f = ln.strip().split('|')
        rec[(f[1], f[2])] = dict(b=float(f[3]), se=float(f[4]), p=float(f[5]),
                                 olsb=float(f[9]), olsp=float(f[10]))
def st(p): p=float(p); return '***' if p<.01 else '**' if p<.05 else '*' if p<.10 else ''

# ---------- 2. first stage (robust), computed ----------
df = pd.read_csv('gaci_panel_3iv.csv')
for c in ['y','ln_gaci_cwm','lnG','tourism_int','lnpop']:
    df[c]=pd.to_numeric(df[c],errors='coerce')
df=df.dropna(subset=['ln_gaci_cwm','lnG','tourism_int','lnpop']).copy()
def demean2(d,cols,it=30):
    d=d.copy()
    for _ in range(it):
        for g in ('c','y'):
            d[cols]=d[cols]-d.groupby(g)[cols].transform('mean')
    return d
FS={}
for logname, col in [('ln_gaci_cwm','ln_gaci_cwm'), ('lng','lnG')]:   # log key -> CSV column
    cols=[col,'tourism_int','lnpop']; dd=demean2(df,cols)
    m=sm.OLS(dd[col],sm.add_constant(dd[['tourism_int','lnpop']])).fit(cov_type='HC1')
    b=m.params['tourism_int']; se=m.bse['tourism_int']
    FS[logname]=dict(b=b,se=se,F=(b/se)**2)

OUT=[('g_int','Openness'),('g_vol','Volume'),('lngdp','GDP')]
BS='\\\\'
def cells(treat,kind):  # kind in {'ols','iv'}
    out=[]
    for o,_ in OUT:
        r=rec[(treat,o)]
        if kind=='ols': out.append('%.3f%s'%(r['olsb'],st(r['olsp'])))
        else:           out.append('%.3f%s'%(r['b'],st(r['p'])))
    return out
def se_cells(treat):
    return ['(%.3f)'%rec[(treat,o)]['se'] for o,_ in OUT]

def panel(treat,title):
    fs=FS[treat]
    P=[r'\multicolumn{4}{l}{\emph{%s}}'%title+BS]
    # First stage (dep. var = the connectivity measure)
    P.append(r'First stage: instrument coef. & \multicolumn{3}{l}{%.3f%s\ \ (%.3f),\ \ KP $F=%.1f$} %s'
             %(fs['b'], '***' if fs['F']>6.635 else '', fs['se'], fs['F'], BS))
    P.append('OLS & '+' & '.join(cells(treat,'ols'))+' '+BS)
    P.append('2SLS & '+' & '.join(cells(treat,'iv'))+' '+BS)
    P.append(' & '+' & '.join(se_cells(treat))+' '+BS)
    return P

L=[r'\begin{table}[t]',r'\centering',
   r'\caption{Main results: OLS, first stage, and 2SLS, by connectivity measure (robust SE).}',
   r'\label{tab:main}',r'\begin{threeparttable}',r'\small',
   r'\begin{tabular}{lccc}',r'\toprule',
   r' & Goods openness & Goods volume & GDP '+BS,
   r' & $\ln(g/Y)$ & $\ln g$ & $\ln Y$ '+BS,r'\midrule']
L+=panel('ln_gaci_cwm',r'Panel A. Hub quality, $\ln\mathrm{GACI}_{cwm}$ (headline)')
L+=[r'\addlinespace']
L+=panel('lng',r'Panel B. Total connectivity, $\ln\mathrm{GACI}_{sum}$')
L+=[r'\midrule',
    r'Country, Year FE & Yes & Yes & Yes '+BS,
    r'Observations & 4{,}643 & 4{,}643 & 4{,}643 '+BS,
    r'\bottomrule',r'\end{tabular}',
    r'\begin{tablenotes}\footnotesize',
    (r'\item Robust (heteroskedasticity-consistent) SE in parentheses. Each panel '
     r'instruments its connectivity measure with the tourism-heritage instrument '
     r'(global tourism demand $\times$ fixed natural+mixed heritage). The first-stage '
     r'row regresses the connectivity measure on the instrument (with population and '
     r'two-way FE); KP $F$ is the first-stage Kleibergen--Paap statistic. Goods volume '
     r'$=$ openness $+$ GDP by the identity $\ln g=\ln(g/Y)+\ln Y$. Connectivity raises '
     r'goods openness and volume in both panels; the income (GDP) effect is positive '
     r'but imprecise. \sym{*}~$p<0.10$, \sym{**}~$p<0.05$, \sym{***}~$p<0.01$.'),
    r'\end{tablenotes}',r'\end{threeparttable}',r'\end{table}']
open('_main_table.tex','w',encoding='utf-8').write('\n'.join(L))
print('\n'.join(L))
print('\n--- first stage check ---')
for t in FS: print(t, 'coef=%.4f se=%.4f F=%.2f'%(FS[t]['b'],FS[t]['se'],FS[t]['F']))
