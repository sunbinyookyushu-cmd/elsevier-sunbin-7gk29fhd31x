# -*- coding: utf-8 -*-
"""Diagnostic: country-level decomposition of the 1996->2023 attributable-gain
counterfactual, to locate where the implausibly large aggregate comes from."""
import json
import numpy as np, pandas as pd

B_VOL, B_GDP = 1.166, 0.507
p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp']       = np.exp(p['lngdp'])
p['merch_shr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']

ENDYR = 2023
g = p[(p.y >= 1996) & (p.y <= ENDYR)].dropna(subset=['lnG']).sort_values('y')
dG = (g.groupby('c').last()['lnG'] - g.groupby('c').first()['lnG']).rename('dG')
gv = p[p.y == ENDYR].set_index('c')['goods_val'].rename('gv')
gd = p[p.y == ENDYR].set_index('c')['gdp'].rename('gd')
b = pd.concat([dG, gv, gd], axis=1).dropna(subset=['dG'])

b['share_attr']  = 1 - np.exp(-B_VOL * b['dG'])          # fraction of own goods trade "caused" by connectivity
b['gain_usd']    = b['gv'].fillna(0) * b['share_attr']
b['gain_gdp']    = b['gd'].fillna(0) * (1 - np.exp(-B_GDP * b['dG']))

tot = b['gain_usd'].sum(); tot_gdp = b['gain_gdp'].sum()
print("=== AGGREGATE (replicates report) ===")
print("trade gain $%.2ftn | GDP gain $%.2ftn | n=%d" % (tot/1e12, tot_gdp/1e12, b.shape[0]))

print("\n=== TOP 15 CONTRIBUTORS TO THE TRADE AGGREGATE ===")
print("%-5s %8s %10s %12s %8s" % ("ISO","dlnGACI","attr_share","gain_$bn","%of_agg"))
top = b.sort_values('gain_usd', ascending=False).head(15)
for c, r in top.iterrows():
    print("%-5s %8.3f %9.0f%% %12.0f %7.1f%%" %
          (c, r['dG'], 100*r['share_attr'], r['gain_usd']/1e9, 100*r['gain_usd']/tot))

print("\nTop 5 share of aggregate:  %.0f%%" % (100*top['gain_usd'].head(5).sum()/tot))
print("Top 10 share of aggregate: %.0f%%" % (100*top['gain_usd'].head(10).sum()/tot))

print("\n=== IMPLAUSIBILITY CHECK: how many countries attribute too much of their OWN trade? ===")
for thr in [0.50, 0.75, 0.90]:
    sub = b[b['share_attr'] > thr]
    print("share_attr > %2.0f%%: %3d countries, holding $%.2ftn of 2023 trade (%.0f%% of the aggregate gain)"
          % (100*thr, sub.shape[0], sub['gv'].sum()/1e12, 100*sub['gain_usd'].sum()/tot))
print("median country attr_share: %.0f%% | mean: %.0f%%" % (100*b['share_attr'].median(), 100*b['share_attr'].mean()))

print("\n=== SENSITIVITY: aggregate under alternative, more conservative constructions ===")
# (a) linearized (first-order) instead of convex exponential: gain ~ beta*dG*level
lin = (B_VOL * b['dG'].clip(lower=0) * b['gv'].fillna(0)).sum()
# (b) cap per-country attributable share at 30%
cap = (b['gv'].fillna(0) * b['share_attr'].clip(upper=0.30)).sum()
# (c) use OLS elasticity 0.83 instead of IV 1.166
ols = (b['gv'].fillna(0) * (1 - np.exp(-0.83 * b['dG']))).sum()
# (d) drop China
noChina = b.drop(index='CHN', errors='ignore')['gain_usd'].sum()
print("exponential IV (current):    $%.2ftn" % (tot/1e12))
print("linearized beta*dG*level:    $%.2ftn" % (lin/1e12))
print("cap own-share at 30%%:        $%.2ftn" % (cap/1e12))
print("OLS elasticity 0.83:         $%.2ftn" % (ols/1e12))
print("current minus China:         $%.2ftn" % (noChina/1e12))
b.sort_values('gain_usd', ascending=False).to_csv('_diag_country.csv')
print("\nwrote _diag_country.csv")
