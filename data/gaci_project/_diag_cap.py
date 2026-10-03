# -*- coding: utf-8 -*-
"""sum + openness (beta_int=0.659) counterfactual, with two disciplining devices:
   (A) cap per-country attributed share at c  (sweep)
   (B) winsorize the treatment change d_sum at a percentile (support restriction)."""
import json
import numpy as np, pandas as pd

B = 0.659  # openness, sum spec
p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp']       = np.exp(p['lngdp'])
p['merch_shr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']

ENDYR = 2023
g = p[(p.y >= 1996) & (p.y <= ENDYR)].dropna(subset=['lnG']).sort_values('y')
dG = (g.groupby('c').last()['lnG'] - g.groupby('c').first()['lnG']).rename('d')
gv = p[p.y == ENDYR].set_index('c')['goods_val'].rename('gv')
b = pd.concat([dG, gv], axis=1).dropna(subset=['d'])
tot = b['gv'].sum()

def agg(d, cap=None):
    s = 1 - np.exp(-B * d)
    if cap is not None: s = np.minimum(s, cap)
    return (b['gv'].fillna(0) * s).sum()

base_share = 1 - np.exp(-B * b['d'])
print("=== UNCAPPED (sum + openness) ===")
print("aggregate $%.2ftn (%.0f%% of $%.1ftn) | CHN share %.0f%% | >50%%: %d countries"
      % (agg(b['d'])/1e12, 100*agg(b['d'])/tot, tot/1e12, 100*base_share['CHN'], (base_share>0.5).sum()))

print("\n=== (A) CAP per-country attributed share ===")
print("%6s %12s %8s %10s" % ("cap","aggregate","%trade","#binding"))
for cap in [0.50, 0.40, 0.35, 0.30, 0.25, 0.20]:
    a = agg(b['d'], cap)
    nb = int((base_share > cap).sum())
    print("%5.0f%% %10.2ftn %7.0f%% %10d" % (100*cap, a/1e12, 100*a/tot, nb))
print("anchor note: IATA ~35%% of world trade BY VALUE moves by air (<1%% by volume)")

print("\n=== (B) WINSORIZE d_sum at a percentile (out-of-support extrapolation) ===")
print("%8s %10s %12s %8s" % ("pctile","d_cutoff","aggregate","%trade"))
for q in [1.00, 0.99, 0.95, 0.90]:
    cut = b['d'].quantile(q)
    dw = b['d'].clip(upper=cut)
    a = agg(dw)
    print("%7.0f%% %10.3f %10.2ftn %7.0f%%" % (100*q, cut, a/1e12, 100*a/tot))

print("\n=== how much each device removes, vs the China problem ===")
print("China d_sum=%.3f sits at the %.0fth pctile of the d distribution"
      % (b.loc['CHN','d'], 100*(b['d'] < b.loc['CHN','d']).mean()))
