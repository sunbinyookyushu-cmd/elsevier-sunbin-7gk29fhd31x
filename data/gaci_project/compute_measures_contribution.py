# -*- coding: utf-8 -*-
"""
compute_measures_contribution.py
Re-compute the aggregate USD contribution of global aviation connectivity growth
(1996->2023) to world GOODS TRADE and to GDP, using ALL THREE connectivity
measures side by side, and computing the GDP contribution several ways.

Measures (all logged, country-year):
    sum  = ln(sum of airport GACI)              -> column lnG
    max  = ln(max airport GACI)                 -> column ln_gaci_max
    cwm  = ln(seat-capacity-weighted mean GACI) -> column ln_gaci_cwm   (manuscript headline)

IV elasticities (Table: _measures_results.csv, tourism-heritage IV, full 1996-2023):
                 intensity beta_int   volume beta_vol   GDP beta_gdp   KP-F
    sum            0.659 (*)            1.166 (***)        0.507 (ns)    9.7
    max            0.966 (**)           1.709 (***)        0.743 (ns)   27.4
    cwm            1.302 (**)           2.303 (***)        1.001 (ns)   18.0

Counterfactual (partial equilibrium): a country's observed change d=Dln(GACI) over
1996->2023 scales its outcome by exp(beta*d). Gain attributable to connectivity growth
   trade gain_i = trade_i(2023) * (1 - exp(-beta * d_i)),   sum over countries.
GDP gain uses GDP levels and beta_gdp.

GDP contribution computed THREE ways per measure:
  (A) scale channel  : GDP_2023 * (1-exp(-beta_gdp * d))              [direct GDP elasticity]
  (B) via identity   : trade-volume gain minus trade-intensity gain  [the GDP-scale part of the trade-volume gain]
  (C) openness->GDP  : intensity trade gain expressed as pp of world GDP
Trade contribution computed TWO ways per measure:
  intensity channel (headline, isolates trade/GDP ratio) and volume channel (upper bound, folds in scale).

in : gaci_panel_measures.csv
out: _measures_contribution.csv  (master comparison, USD + % shares)
     _contrib_bycountry.csv       (per-country attributable trade, for maps)
"""
import numpy as np, pandas as pd

ENDYR, STARTYR = 2023, 1996
MEAS = {   # order matches manuscript Table 1: A=cwm (headline), B=max, C=sum
    #            treat col        b_int  b_vol  b_gdp   KP-F  int_sig vol_sig gdp_sig
    'cwm': dict(col='ln_gaci_cwm',  b_int=1.302, b_vol=2.303, b_gdp=1.001, kpf=18.0, s_int='**', s_vol='***', s_gdp='ns'),
    'max': dict(col='ln_gaci_max',  b_int=0.966, b_vol=1.709, b_gdp=0.743, kpf=27.4, s_int='**', s_vol='***', s_gdp='ns'),
    'sum': dict(col='lnG',          b_int=0.659, b_vol=1.166, b_gdp=0.507, kpf=9.7,  s_int='*',  s_vol='***', s_gdp='ns'),
}

p = pd.read_csv('gaci_panel_measures.csv')
p['gdp']       = np.exp(p['lngdp'])
p['goods_val'] = p['merch_share'] / 100.0 * p['gdp']       # merch_share is goods trade as % of GDP

# world bases at end year (fixed across measures so shares are comparable)
end = p[p.y == ENDYR].set_index('c')
gv23, gdp23 = end['goods_val'], end['gdp']
TOT_TRADE = gv23.dropna().sum()
TOT_GDP   = gdp23.dropna().sum()

def dln(col):
    g = p[(p.y >= STARTYR) & (p.y <= ENDYR)].dropna(subset=[col]).sort_values('y')
    return (g.groupby('c').last()[col] - g.groupby('c').first()[col]).rename('d')

def attrib(level, d, beta):
    m = pd.concat([level.rename('L'), d], axis=1).dropna(subset=['d'])
    return (m['L'].fillna(0) * (1 - np.exp(-beta * m['d']))).sum()

rows, bycountry = [], {}
for name, cfg in MEAS.items():
    d = dln(cfg['col'])
    # trade contributions
    trade_int = attrib(gv23, d, cfg['b_int'])          # headline (intensity/openness channel)
    trade_vol = attrib(gv23, d, cfg['b_vol'])          # upper bound (volume = intensity + scale)
    # GDP contributions, three ways
    gdp_A = attrib(gdp23, d, cfg['b_gdp'])             # (A) direct GDP-scale elasticity on GDP levels
    gdp_B = trade_vol - trade_int                       # (B) GDP-scale part embedded in the trade-volume gain
    gdp_C = trade_int                                   # (C) openness gain in pp of GDP == trade_int / TOT_GDP
    rows.append(dict(
        measure=name, treat=cfg['col'], KP_F=cfg['kpf'],
        b_int=cfg['b_int'], sig_int=cfg['s_int'],
        b_vol=cfg['b_vol'], sig_vol=cfg['s_vol'],
        b_gdp=cfg['b_gdp'], sig_gdp=cfg['s_gdp'],
        # --- trade in USD ---
        trade_int_usd=trade_int, trade_int_pctT=100*trade_int/TOT_TRADE, trade_int_pctY=100*trade_int/TOT_GDP,
        trade_vol_usd=trade_vol, trade_vol_pctT=100*trade_vol/TOT_TRADE, trade_vol_pctY=100*trade_vol/TOT_GDP,
        # --- GDP in USD, three ways ---
        gdpA_scale_usd=gdp_A, gdpA_pctY=100*gdp_A/TOT_GDP,
        gdpB_identity_usd=gdp_B, gdpB_pctY=100*gdp_B/TOT_GDP,
        gdpC_openness_ppGDP=100*gdp_C/TOT_GDP,
        n=int(d.dropna().shape[0]),
    ))
    # per-country attributable trade (intensity channel) for maps
    bc = pd.concat([gv23.rename('gv'), d], axis=1).dropna(subset=['d'])
    bc['dln']        = bc['d']
    bc['trade_gain'] = bc['gv'].fillna(0) * (1 - np.exp(-cfg['b_int'] * bc['d']))
    bycountry[name]  = bc[['dln', 'trade_gain']].rename(columns={'dln': f'dln_{name}', 'trade_gain': f'gain_{name}'})

tab = pd.DataFrame(rows).set_index('measure')
tab.to_csv('_measures_contribution.csv')

bc_all = pd.concat(bycountry.values(), axis=1)
bc_all.index.name = 'c'
bc_all.to_csv('_contrib_bycountry.csv')

# ---------- pretty print ----------
pd.set_option('display.width', 200, 'display.float_format', lambda v: f'{v:,.2f}')
print('=' * 78)
print(f'WORLD BASES 2023:  goods trade = ${TOT_TRADE/1e12:,.1f} tn   GDP = ${TOT_GDP/1e12:,.1f} tn')
print('=' * 78)
hdr = f"{'measure':>7} | {'b_int':>6} {'b_vol':>6} {'b_gdp':>6} {'KP-F':>5} || {'TRADE int $tn':>13} {'%wT':>5} | {'TRADE vol $tn':>13} {'%wT':>5} || {'GDP(A) $tn':>10} {'%Y':>5} | {'GDP(B) $tn':>10}"
print(hdr); print('-' * len(hdr))
for m, r in tab.iterrows():
    print(f"{m:>7} | {r.b_int:>6.3f} {r.b_vol:>6.3f} {r.b_gdp:>6.3f} {r.KP_F:>5.1f} || "
          f"{r.trade_int_usd/1e12:>13.2f} {r.trade_int_pctT:>5.1f} | "
          f"{r.trade_vol_usd/1e12:>13.2f} {r.trade_vol_pctT:>5.1f} || "
          f"{r.gdpA_scale_usd/1e12:>10.2f} {r.gdpA_pctY:>5.1f} | {r.gdpB_identity_usd/1e12:>10.2f}")
print('-' * len(hdr))
print("TRADE int = intensity/openness channel (headline).  TRADE vol = volume channel (upper bound).")
print("GDP(A) = direct GDP-scale elasticity on GDP levels.  GDP(B) = volume-minus-intensity trade gain (scale part).")
print("%wT = % of 2023 world goods trade.  %Y = % of 2023 world GDP.")
print("\nCaveat: beta_gdp is NOT statistically significant for any measure (ns);")
print("beta_int significant at 10% (sum) / 5% (max, cwm); beta_vol significant at 1% for all three.")
print("=> The trade-volume USD numbers rest on the strongest (***) coefficients.")
print('\nwrote _measures_contribution.csv, _contrib_bycountry.csv')
