# -*- coding: utf-8 -*-
"""compute_aggregates_ci.py -- 95% CI band for the $7.8tn headline counterfactual.
Replicates compute_aggregates.py's gain formula, evaluating it at beta and
beta +/- 1.96*SE (2SLS robust SEs from Table 1 Panel A). Comment 769 (T. Cheung).
"""
import json
import numpy as np, pandas as pd

TCOL = 'ln_gaci_cwm'
BETAS = {  # (beta, robust SE) from Table 1 Panel A, cwm
    'openness': (1.208, 0.593),
    'volume':   (2.126, 0.703),
}
ENDYR = 2024

p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp'] = np.exp(p['lngdp'])
p['merch_shr'] = pd.to_numeric(
    [merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']

g = p[(p.y >= 1996) & (p.y <= ENDYR)].dropna(subset=[TCOL]).sort_values('y')
dG = (g.groupby('c').last()[TCOL] - g.groupby('c').first()[TCOL]).rename('dG')
gv = p[p.y == ENDYR].set_index('c')['goods_val'].rename('gv')
base = pd.concat([dG, gv], axis=1).dropna(subset=['dG'])
tot = base['gv'].sum()

def gain(beta):
    return (base['gv'].fillna(0) * (1 - np.exp(-beta * base['dG']))).sum()

print(f"countries={base.shape[0]}  2023 world goods trade = ${tot/1e12:.1f}tn")
for name, (b, se) in BETAS.items():
    lo, hi = b - 1.96 * se, b + 1.96 * se
    g_pt, g_lo, g_hi = gain(b), gain(lo), gain(hi)
    print(f"{name}: beta={b} [{lo:.3f}, {hi:.3f}]")
    print(f"  gain point = ${g_pt/1e12:.2f}tn ({100*g_pt/tot:.1f}% of world trade)")
    print(f"  gain 95%CI = [${g_lo/1e12:.2f}tn, ${g_hi/1e12:.2f}tn]"
          f"  ([{100*g_lo/tot:.1f}%, {100*g_hi/tot:.1f}%])")
