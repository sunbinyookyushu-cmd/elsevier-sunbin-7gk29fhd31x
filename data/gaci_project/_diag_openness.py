# -*- coding: utf-8 -*-
"""Re-run the 1996->2023 attributable-gain counterfactual using the
openness coefficient beta_int = 0.659 (ln(goods/GDP)) instead of volume 1.166."""
import json
import numpy as np, pandas as pd

B_VOL, B_INT = 1.166, 0.659
p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp']       = np.exp(p['lngdp'])
p['merch_shr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']

ENDYR = 2023
g = p[(p.y >= 1996) & (p.y <= ENDYR)].dropna(subset=['lnG']).sort_values('y')
dG = (g.groupby('c').last()['lnG'] - g.groupby('c').first()['lnG']).rename('dG')
gv = p[p.y == ENDYR].set_index('c')['goods_val'].rename('gv')
b = pd.concat([dG, gv], axis=1).dropna(subset=['dG'])

for name, beta in [('VOLUME 1.166', B_VOL), ('OPENNESS 0.659', B_INT)]:
    share = 1 - np.exp(-beta * b['dG'])
    gain  = (b['gv'].fillna(0) * share).sum()
    tot   = b['gv'].sum()
    print("=== beta = %s ===" % name)
    print("  aggregate trade gain : $%.2ftn  (%.0f%% of 2023 goods trade $%.1ftn)"
          % (gain/1e12, 100*gain/tot, tot/1e12))

# country decomposition under openness beta
b['share'] = 1 - np.exp(-B_INT * b['dG'])
b['gain']  = b['gv'].fillna(0) * b['share']
tot = b['gain'].sum()
print("\n=== OPENNESS beta=0.659 : TOP 10 CONTRIBUTORS ===")
print("%-5s %8s %10s %12s %8s" % ("ISO","dlnGACI","attr_share","gain_$bn","%of_agg"))
top = b.sort_values('gain', ascending=False).head(10)
for c, r in top.iterrows():
    print("%-5s %8.3f %9.0f%% %12.0f %7.1f%%"
          % (c, r['dG'], 100*r['share'], r['gain']/1e9, 100*r['gain']/tot))
print("Top 5 share: %.0f%% | Top 10 share: %.0f%%"
      % (100*top['gain'].head(5).sum()/tot, 100*top['gain'].sum()/tot))
print("CHN attr_share of own trade: %.0f%%" % (100*b.loc['CHN','share']))
n50 = (b['share'] > 0.50).sum()
print("countries attributing >50%% of own trade: %d (vs 40 under volume beta)" % n50)

# also: openness as the report frames it (trade-weighted log points)
w = b['gv'].fillna(0)
lp = np.average(B_INT * b['dG'], weights=w)
print("\ntrade-weighted openness rise: %.3f log pts (%.1f%%)" % (lp, 100*(np.exp(lp)-1)))
