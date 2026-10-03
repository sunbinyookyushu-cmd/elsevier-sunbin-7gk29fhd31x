# -*- coding: utf-8 -*-
"""Counterfactual computed CONSISTENTLY with the hub-quality (cap-weighted-mean)
spec: treatment change = d ln_gaci_cwm, coefficient = Panel B beta (vol 2.303)."""
import json
import numpy as np, pandas as pd

# Panel B (treatment = log cap-weighted-mean GACI) coefficients
BCWM_VOL, BCWM_GDP, BCWM_INT = 2.303, 1.001, 1.302
# Panel A (sum) for comparison
BSUM_VOL = 1.166

p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp']       = np.exp(p['lngdp'])
p['merch_shr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']
p['ln_gaci_cwm'] = pd.to_numeric(p['ln_gaci_cwm'], errors='coerce')

ENDYR = 2023
def dcol(col):
    g = p[(p.y >= 1996) & (p.y <= ENDYR)].dropna(subset=[col]).sort_values('y')
    return (g.groupby('c').last()[col] - g.groupby('c').first()[col]).rename('d')

gv = p[p.y == ENDYR].set_index('c')['goods_val'].rename('gv')

print("=== mean change in treatment 1996->2023 (how fast each grew) ===")
dS = dcol('lnG'); dC = dcol('ln_gaci_cwm')
print("d ln GACI SUM : mean %.3f  median %.3f" % (dS.mean(), dS.median()))
print("d ln GACI CWM : mean %.3f  median %.3f  <- weighted mean grows much slower" % (dC.mean(), dC.median()))

print("\n=== aggregate trade gain ===")
for name, d, beta in [("SUM   spec (beta 1.166 x d_sum)", dS, BSUM_VOL),
                      ("CWM   spec (beta 2.303 x d_cwm)", dC, BCWM_VOL)]:
    b = pd.concat([d, gv], axis=1).dropna(subset=['d'])
    gain = (b['gv'].fillna(0) * (1 - np.exp(-beta * b['d']))).sum()
    tot  = b['gv'].sum()
    print("  %s : $%.2ftn  (%.0f%% of $%.1ftn, n=%d)" % (name, gain/1e12, 100*gain/tot, tot/1e12, b.shape[0]))

# CWM country decomposition
b = pd.concat([dC, gv], axis=1).dropna(subset=['d'])
b['share'] = 1 - np.exp(-BCWM_VOL * b['d'])
b['gain']  = b['gv'].fillna(0) * b['share']
tot = b['gain'].sum()
print("\n=== CWM spec : TOP 10 CONTRIBUTORS ===")
print("%-5s %8s %10s %12s %8s" % ("ISO","d_cwm","attr_share","gain_$bn","%of_agg"))
for c, r in b.sort_values('gain', ascending=False).head(10).iterrows():
    print("%-5s %8.3f %9.0f%% %12.0f %7.1f%%" % (c, r['d'], 100*r['share'], r['gain']/1e9, 100*r['gain']/tot))
print("CHN attr_share of own trade: %.0f%%" % (100*b.loc['CHN','share']) if 'CHN' in b.index else "")
print("countries attributing >50%% of own trade: %d" % (b['share'] > 0.50).sum())
