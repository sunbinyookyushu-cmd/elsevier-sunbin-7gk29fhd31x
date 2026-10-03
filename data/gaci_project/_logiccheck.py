# -*- coding: utf-8 -*-
"""Logic checks on the cwm-aligned GACI results."""
import json, numpy as np, pandas as pd

# 1) decomposition identity  g_vol == g_int + lngdp  (per subsample, from hetero2 log)
print("=== CHECK 1: identity  beta_vol = beta_int + beta_gdp(lngdp)  per subsample ===")
res = {}
for ln in open('gaci_tourism_hetero2.log', encoding='utf-8', errors='replace'):
    ln = ln.strip()
    if ln.startswith('RES2|'):
        p = ln.split('|')
        if p[3] == 'FAIL': continue
        res[(p[2], p[1])] = (float(p[3]), float(p[6]))   # (group,outcome) -> (beta, F)
groups = sorted({g for g, o in res})
print("%-14s %9s %9s %9s %9s %8s" % ("group", "b_vol", "b_int+gdp", "diff", "F", "ok"))
for g in groups:
    if all((g, o) in res for o in ('g_vol', 'g_int', 'lngdp')):
        bv = res[(g, 'g_vol')][0]; bi = res[(g, 'g_int')][0]; bg = res[(g, 'lngdp')][0]
        diff = bv - (bi + bg)
        print("%-14s %9.3f %9.3f %9.2e %9.2f %8s" % (g, bv, bi + bg, diff, res[(g, 'g_vol')][1],
                                                     "OK" if abs(diff) < 1e-4 else "**OFF**"))

# 2) weak-identification audit (first-stage F by subsample)
print("\n=== CHECK 2: first-stage F by subsample (IV weak if F<10) ===")
Fs = sorted({(g, res[(g, 'g_int')][1]) for g in groups if (g, 'g_int') in res}, key=lambda x: x[1])
for g, F in Fs:
    flag = "  <-- WEAK (F<10)" if F < 10 else ("  <-- VERY WEAK (F<2)" if F < 2 else "")
    print("  %-14s F=%8.2f%s" % (g, F, flag))

# 3) aggregate consistency: report numbers vs recomputation
print("\n=== CHECK 3: aggregate openness identity (report json) ===")
AG = json.load(open('_aggregates.json'))['gain']
lhs = AG['world_open_now'] - AG['world_open_cf']
print("  openness now %.2f%% - cf %.2f%% = %.3f pp  vs  gain/GDP %.3f pp  -> %s"
      % (AG['world_open_now'], AG['world_open_cf'], lhs, AG['gain_trade_pct_gdp'],
         "OK" if abs(lhs - AG['gain_trade_pct_gdp']) < 0.05 else "OFF"))
print("  gain_trade %% of trade = %.2f, of GDP = %.2f, volume(int+scale) = %.2f%%"
      % (AG['gain_trade_pct'], AG['gain_trade_pct_gdp'], AG['gain_tradevol_pct']))
print("  intensity gain $%.2fT + scale $%.2fT(GDP-chan implied trade) ?= volume $%.2fT"
      % (AG['gain_trade_usd']/1e12, (AG['gain_tradevol_usd']-AG['gain_trade_usd'])/1e12, AG['gain_tradevol_usd']/1e12))
