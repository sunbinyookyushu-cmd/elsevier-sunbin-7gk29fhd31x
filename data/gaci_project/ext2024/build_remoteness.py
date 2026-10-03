# -*- coding: utf-8 -*-
"""Build a country-level REMOTENESS moderator from CERDI sea distances and merge
   it into the analysis panel -> gaci_panel_hetero.csv (for the interaction-IV hetero).
   remoteness_i = UNWEIGHTED mean sea distance to all analysis-sample countries
   (pure geography; GDP-weighting inverted the ranking via mass-proximity). ln_remote = ln(that).
   Time-invariant & exogenous. NOTE: a few landlocked countries (e.g. KAZ) carry CERDI
   road-to-port routing artifacts; minor among 183 countries."""
import numpy as np, pandas as pd

cer = pd.read_stata('CERDI_seadistance.dta')[['iso1', 'iso2', 'seadistance']].dropna(subset=['seadistance'])
pan = pd.read_csv('gaci_panel_tourism_ext.csv')
isos = set(pan['c'].unique())

cer = cer[(cer['iso1'] != cer['iso2']) & (cer['iso2'].isin(isos))]   # partners = analysis countries
g = cer.groupby('iso1')['seadistance'].mean()                        # unweighted mean distance
rem = g.rename('remote_km').to_frame()
rem = rem[rem.index.isin(isos)]
rem['ln_remote'] = np.log(rem['remote_km'])
rem.index.name = 'c'

# sanity check
print('countries with remoteness:', rem.shape[0])
print('\n=== MOST remote (should be Pacific/islands/Southern) ===')
print(rem.sort_values('remote_km', ascending=False).head(10)['remote_km'].round(0).to_string())
print('\n=== LEAST remote (should be Europe/Mediterranean hubs) ===')
print(rem.sort_values('remote_km').head(10)['remote_km'].round(0).to_string())

# merge into panel and save augmented file
out = pan.merge(rem[['ln_remote']], left_on='c', right_index=True, how='left')
matched = out['ln_remote'].notna().groupby(out['c']).first().sum()
print('\npanel countries:', pan['c'].nunique(), ' matched remoteness:', int(matched))
print('UNMATCHED panel ISO:', sorted(set(pan['c']) - set(rem.index))[:30])
out.to_csv('gaci_panel_hetero.csv', index=False)
print('\nwrote gaci_panel_hetero.csv  (panel + ln_remote)')
