# -*- coding: utf-8 -*-
"""Summary stats, base GACI map, and global trade/GDP aggregates (sections 1,6,7).
Counterfactual logic: an observed change d=Dln(GACI) shifts ln(outcome) by beta*d, i.e.
outcome scales by exp(beta*d). Gain attributable to GACI growth = level*(1-exp(-beta*d));
loss from a shock (d<0) = pre-level*(1-exp(beta*d)). Partial-equilibrium, illustrative."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import geopandas as gpd

# IV betas (Table 1 Panel A, MAIN treatment = ln_gaci_cwm hub quality, tourism-heritage IV, FULL sample 1996-2023)
# Identity (cwm): B_VOL = B_INT + B_GDP  ->  2.303 = 1.302 + 1.001.  Counterfactuals use B_INT (intensity channel).
TCOL  = 'ln_gaci_cwm'   # treatment column driving the LONG-RUN counterfactual (hub quality, main var)
B_VOL = 2.126   # ln goods trade volume  (intensity + scale)
B_INT = 1.208   # ln(goods/GDP) openness (intensity channel; headline)
B_GDP = 0.919   # ln GDP total           (scale channel)
B_PC  = 0.582   # ln GDP per capita
# Abrupt 1-year SHOCK losses use TOTAL connectivity (sum) instead of hub-quality mean: cwm is too
# volatile year-to-year (hub quality collapses sharply in a single shock year), which makes the convex
# loss explode and overstates one-year shock costs. The sum measure tracks links lost more stably.
SCOL  = 'lnG'   ; B_INT_SUM = 0.635 ; B_GDP_SUM = 0.483   # sum-based intensity/scale elasticities

p = pd.read_csv('gaci_panel.csv')
merch = json.load(open('merch_trade.json'))
p['gdp']       = np.exp(p['lngdp'])
p['merch_shr'] = [merch.get(f"{c}|{y}") for c, y in zip(p['c'], p['y'])]
p['merch_shr'] = pd.to_numeric(p['merch_shr'], errors='coerce')
p['goods_val'] = p['merch_shr'] / 100.0 * p['gdp']

def lng_at(year):
    s = p[p.y == year].set_index('c')[TCOL]   # hub quality (main treatment)
    return s
def val_at(col, year):
    return p[p.y == year].set_index('c')[col]

# ---------- (1) summary statistics ----------
samp = p[(p.y >= 1996) & (p.y <= 2024)]
def stat(col, lab, src=None):
    x = (src if src is not None else samp)[col].dropna()
    return dict(var=lab, n=int(x.shape[0]), mean=x.mean(), sd=x.std(), p50=x.median(), mn=x.min(), mx=x.max())
SUM = [
    stat('lnG', 'ln GACI (connectivity sum)'),
    stat('ln_gaci_cwm', 'ln hub quality (cap-wtd-mean GACI)'),
    stat('n_air', 'number of airports'),
    stat('merch_shr', 'goods trade (% GDP)'),
    stat('lnpc', 'ln GDP per capita'),
    stat('lngdp', 'ln GDP (total)'),
    stat('unesco_cum_nat', 'natural/mixed UNESCO sites (cum.)'),
    stat('lnpop', 'ln population'),
]
pd.DataFrame(SUM).to_csv('_sumstats.csv', index=False)

# ---------- full-period change in connectivity (1996 -> 2023) ----------
ENDYR = 2024
g = p[(p.y >= 1996) & (p.y <= ENDYR)].dropna(subset=[TCOL]).sort_values('y')
dG = (g.groupby('c').last()[TCOL] - g.groupby('c').first()[TCOL]).rename('dG')   # 1996->2023, hub quality

# bases at end year
gv19 = val_at('goods_val', ENDYR)
gdp19 = val_at('gdp', ENDYR)
base = pd.concat([dG, gv19.rename('gv'), gdp19.rename('gdp')], axis=1).dropna(subset=['dG'])

def attrib_gain(level, d, beta):
    return (level * (1 - np.exp(-beta * d))).sum()

# ---------- (7) 20-year global gains from connectivity growth ----------
# Headline trade gain uses the INTENSITY (openness) elasticity B_INT, isolating the pure
# trade-intensity channel. By the identity ln(goods)=ln(goods/GDP)+ln(GDP), B_VOL = B_INT + B_GDP,
# so the volume gain folds in the GDP-scale channel; we report it only as a combined upper bound.
gain_trade  = attrib_gain(base['gv'].fillna(0), base['dG'], B_INT)     # USD goods trade, intensity channel (headline)
gain_tradev = attrib_gain(base['gv'].fillna(0), base['dG'], B_VOL)     # USD goods trade, intensity+scale (upper bound)
gain_gdp    = attrib_gain(base['gdp'].fillna(0), base['dG'], B_GDP)    # USD GDP, scale channel
tot_trade19 = base['gv'].sum(); tot_gdp19 = base['gdp'].sum()
w = base['gv'].fillna(0)
open_logpts = np.average((B_INT * base['dG']), weights=w)
GAIN = dict(gain_trade_usd=gain_trade, gain_tradevol_usd=gain_tradev,
            tot_trade19=tot_trade19, tot_gdp19=tot_gdp19,
            gain_trade_pct=100*gain_trade/tot_trade19,             # % of world goods trade
            gain_trade_pct_gdp=100*gain_trade/tot_gdp19,           # % of world GDP (= openness gain in pp of GDP)
            gain_tradevol_pct=100*gain_tradev/tot_trade19,
            gain_gdp_usd=gain_gdp, gain_gdp_pct=100*gain_gdp/tot_gdp19,
            world_open_now=100*tot_trade19/tot_gdp19,              # world goods openness now, % of GDP
            world_open_cf=100*(tot_trade19-gain_trade)/tot_gdp19,  # counterfactual openness without connectivity growth
            open_logpts=open_logpts, open_pct=100*(np.exp(open_logpts)-1), n=int(base.shape[0]))

# ---------- (6) shock losses: COVID (2019->2020) and Russia (2021->2022) ----------
def shock_loss(y0, y1, betav, betag, base_year, tcol=SCOL):
    d = (p[p.y == y1].set_index('c')[tcol] - p[p.y == y0].set_index('c')[tcol]).rename('d')   # connectivity change over shock
    gv = val_at('goods_val', base_year).rename('gv')
    gd = val_at('gdp', base_year).rename('gd')
    m = pd.concat([d, gv, gd], axis=1).dropna(subset=['d'])
    tl_v = m['gv'].fillna(0) * (1 - np.exp(betav * m['d']))            # >0 = loss
    gl_v = m['gd'].fillna(0) * (1 - np.exp(betag * m['d']))
    los = m['d'] < 0                                                   # connectivity-losing countries
    rus_t = float(tl_v.get('RUS', np.nan)); rus_g = float(gl_v.get('RUS', np.nan))
    return dict(med_dG=m['d'].median(), n_drop=int(los.sum()), n=int(m.shape[0]),
                trade_loss=tl_v.sum(), gdp_loss=gl_v.sum(),
                trade_loss_losers=tl_v[los].sum(), gdp_loss_losers=gl_v[los].sum(),
                tot_trade=float(m['gv'].sum()), tot_gdp=float(m['gd'].sum()),
                rus_trade_loss=rus_t, rus_gdp_loss=rus_g)
COVID  = shock_loss(2019, 2020, B_INT_SUM, B_GDP_SUM, 2019)   # sum-based intensity channel; gross 1-yr flow disruption
RUSSIA = shock_loss(2021, 2022, B_INT_SUM, B_GDP_SUM, 2021)   # war year (localised; recovery confounds net)

json.dump({'gain': GAIN, 'covid': COVID, 'russia': RUSSIA,
           'betas': dict(vol=B_VOL, intensity=B_INT, gdp=B_GDP, pc=B_PC)},
          open('_aggregates.json', 'w'), indent=2)

# ---------- base GACI level map (2019 ln GACI sum) ----------
g19 = val_at('lnG', 2024).rename('lnG19').reset_index()
gj = json.load(open('_world.geojson'))
w = gpd.GeoDataFrame.from_features(gj['features'])
def iso(r):
    for k in ['ISO_A3', 'ISO_A3_EH', 'ADM0_A3']:
        v = r.get(k)
        if isinstance(v, str) and v not in ('-99', ''):
            return v
    return None
w['iso3'] = w.apply(iso, axis=1)
w = w[w['NAME'] != 'Antarctica'].merge(g19, left_on='iso3', right_on='c', how='left')
fig, ax = plt.subplots(figsize=(15, 7.5))
w.plot(column='lnG19', ax=ax, cmap='viridis', legend=True, missing_kwds={'color': '#e6e6e6'},
       edgecolor='white', linewidth=0.2,
       legend_kwds={'label': 'ln(GACI sum), 2024', 'shrink': 0.6, 'orientation': 'horizontal', 'pad': 0.01, 'aspect': 40})
ax.set_title('Global air connectivity (GACI) by country, 2024', fontsize=14, fontweight='bold')
ax.axis('off'); plt.tight_layout(); plt.savefig('GACI_base_map.png', dpi=150, bbox_inches='tight')

print('=== SUMMARY STATS ==='); print(pd.DataFrame(SUM).to_string(index=False))
print('\n=== (7) GLOBAL GAINS (1996-2023) ===')
print('Goods trade attributable to GACI: $%.2f trillion  (%.1f%% of 2023 goods trade $%.1ftn)'
      % (GAIN['gain_trade_usd']/1e12, GAIN['gain_trade_pct'], GAIN['tot_trade19']/1e12))
print('GDP attributable to GACI:         $%.2f trillion  (%.1f%% of 2023 GDP $%.1ftn)'
      % (GAIN['gain_gdp_usd']/1e12, GAIN['gain_gdp_pct'], GAIN['tot_gdp19']/1e12))
print('Trade-weighted openness rise:     %.3f log pts (%.1f%%)' % (GAIN['open_logpts'], GAIN['open_pct']))
print('\n=== (6) SHOCK TRADE LOSSES ===')
print('COVID 2019->2020 (global): trade loss $%.2f tn, GDP loss $%.2f tn (median dlnGACI %.3f, %d/%d fell)'
      % (COVID['trade_loss']/1e12, COVID['gdp_loss']/1e12, COVID['med_dG'], COVID['n_drop'], COVID['n']))
print('Russia 2021->2022 NET (confounded by recovery): trade $%.2f tn (median dlnGACI %.3f, only %d/%d fell)'
      % (RUSSIA['trade_loss']/1e12, RUSSIA['med_dG'], RUSSIA['n_drop'], RUSSIA['n']))
print('Russia: loss among connectivity-LOSING countries: trade $%.2f tn, GDP $%.2f tn'
      % (RUSSIA['trade_loss_losers']/1e12, RUSSIA['gdp_loss_losers']/1e12))
print('Russia: Russia-specific loss: trade $%.0f bn, GDP $%.0f bn'
      % (RUSSIA['rus_trade_loss']/1e9, RUSSIA['rus_gdp_loss']/1e9))
print('\nwrote _sumstats.csv, _aggregates.json, GACI_base_map.png')
