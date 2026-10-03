# -*- coding: utf-8 -*-
"""Cumulative (1996-2023) attributable goods trade vs cumulative world trade and GDP,
   intensity channel beta=0.659. Numerator AND denominator both summed over country-years,
   so the time units match (unlike a single-year gain divided by a multi-year GDP sum)."""
import json
import numpy as np, pandas as pd

B_INT = 0.659
p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp']       = np.exp(p['lngdp'])
p['merch_shr'] = pd.to_numeric([merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']

samp = p[(p.y >= 1996) & (p.y <= 2023)].dropna(subset=['lnG']).copy()
# base = each country's first available ln GACI in window (matches the level-counterfactual base)
base = samp.sort_values('y').groupby('c')['lnG'].first().rename('lnG0')
samp = samp.merge(base, on='c')
samp['d']      = samp['lnG'] - samp['lnG0']                       # connectivity growth since base, by year
samp['attrib'] = samp['goods_val'].fillna(0) * (1 - np.exp(-B_INT * samp['d']))

cum_attrib = samp['attrib'].sum()
cum_trade  = samp['goods_val'].sum()
cum_gdp    = samp['gdp'].sum()

# single-year 2023 (for contrast, = report headline)
y23 = samp[samp.y == 2023]
sy_attrib = y23['attrib'].sum(); sy_trade = y23['goods_val'].sum(); sy_gdp = y23['gdp'].sum()

print("=== SINGLE-YEAR 2023 (report headline) ===")
print("attributable goods trade   : $%.2ftn" % (sy_attrib/1e12))
print("  %% of 2023 world goods trade: %.1f%%  (of $%.1ftn)" % (100*sy_attrib/sy_trade, sy_trade/1e12))
print("  %% of 2023 world GDP        : %.1f%%  (of $%.1ftn)" % (100*sy_attrib/sy_gdp, sy_gdp/1e12))

print("\n=== CUMULATIVE 1996-2023 (numerator and denominator both summed over years) ===")
print("cumulative attributable goods trade : $%.1ftn   (GACI-induced trade summed across all country-years)" % (cum_attrib/1e12))
print("cumulative world goods trade        : $%.1ftn" % (cum_trade/1e12))
print("cumulative world GDP                : $%.1ftn" % (cum_gdp/1e12))
print("  -> %% of cumulative world goods trade : %.1f%%" % (100*cum_attrib/cum_trade))
print("  -> %% of cumulative world GDP         : %.2f%%" % (100*cum_attrib/cum_gdp))

print("\n=== (for reference only - INCOHERENT mismatched units) ===")
print("single-year 2023 gain $%.1ftn / cumulative GDP $%.0ftn = %.2f%%  <- do NOT use (numerator 1yr, denom 28yr)"
      % (sy_attrib/1e12, cum_gdp/1e12, 100*sy_attrib/cum_gdp))
