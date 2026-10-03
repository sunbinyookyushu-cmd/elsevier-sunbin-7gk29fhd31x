# -*- coding: utf-8 -*-
"""
build_measures_maps.py
Maps of the country-level contribution of aviation-connectivity growth (1996->2023)
to goods trade and GDP, for all THREE connectivity measures (sum / max / cwm).

Outputs:
  GACI_contrib_trade_3panel.png  -- per-country attributable GOODS-TRADE gain (USD bn),
                                    intensity channel, 3 panels (sum/max/cwm), shared log scale
  GACI_contrib_gdp_3panel.png    -- per-country attributable GDP gain (USD bn),
                                    scale channel, 3 panels, shared log scale
  GACI_contrib_bars.png          -- grouped bars: world aggregate $tn by measure & channel
  GACI_dln_3panel.png            -- per-country Dln(GACI) 1996->2023 by measure (diverging)
"""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, TwoSlopeNorm, SymLogNorm
from matplotlib.ticker import FuncFormatter
import geopandas as gpd

INK, NODATA, BORD = '#1f1f1f', '#ededed', '#b3b8bd'
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})

ENDYR, STARTYR = 2023, 1996
MEAS = {   # order matches manuscript Table 1: A=cwm (headline), B=max, C=sum
    'cwm': dict(col='ln_gaci_cwm', b_int=1.302, b_vol=2.303, b_gdp=1.001, title='Panel A.  Hub quality, GACI$_{\\mathrm{cwm}}$ (headline)'),
    'max': dict(col='ln_gaci_max', b_int=0.966, b_vol=1.709, b_gdp=0.743, title='Panel B.  Maximum hub, GACI$_{\\mathrm{max}}$'),
    'sum': dict(col='lnG',         b_int=0.659, b_vol=1.166, b_gdp=0.507, title='Panel C.  Total connectivity, GACI$_{\\mathrm{sum}}$'),
}

# ---------- data ----------
p = pd.read_csv('gaci_panel_measures.csv')
p['gdp']       = np.exp(p['lngdp'])
p['goods_val'] = p['merch_share'] / 100.0 * p['gdp']
end = p[p.y == ENDYR].set_index('c')
gv23, gdp23 = end['goods_val'], end['gdp']

def dln(col):
    g = p[(p.y >= STARTYR) & (p.y <= ENDYR)].dropna(subset=[col]).sort_values('y')
    return (g.groupby('c').last()[col] - g.groupby('c').first()[col]).rename('d')

frames = {}
for name, cfg in MEAS.items():
    d = dln(cfg['col'])
    df = pd.concat([gv23.rename('gv'), gdp23.rename('gdp'), d], axis=1).dropna(subset=['d'])
    df[f'dln_{name}']       = df['d']
    df[f'tgain_{name}']     = df['gv'].fillna(0)  * (1 - np.exp(-cfg['b_int'] * df['d']))   # trade, intensity
    df[f'ggain_{name}']     = df['gdp'].fillna(0) * (1 - np.exp(-cfg['b_gdp'] * df['d']))   # GDP, scale
    frames[name] = df[[f'dln_{name}', f'tgain_{name}', f'ggain_{name}']]
allc = pd.concat(frames.values(), axis=1)
allc.index.name = 'c'
allc = allc.reset_index()

# ---------- geometry ----------
gj = json.load(open('_world.geojson'))
W = gpd.GeoDataFrame.from_features(gj['features']).set_crs(4326)
def iso(r):
    for k in ['ISO_A3', 'ISO_A3_EH', 'ADM0_A3']:
        v = r.get(k)
        if isinstance(v, str) and v not in ('-99', ''):
            return v
    return None
W['iso3'] = W.apply(iso, axis=1)
W = W[W['NAME'] != 'Antarctica'].to_crs('+proj=robin')
Wm = W.merge(allc, left_on='iso3', right_on='c', how='left')
import _mapstyle as ms
Wm = ms.unify_china(Wm, [c for c in allc.columns if c != 'c'])

def frame_ax(ax):
    minx, miny, maxx, maxy = W.total_bounds
    xr = maxx - minx
    ax.set_xlim(minx + 0.05 * xr, maxx); ax.set_ylim(miny, maxy); ax.axis('off')

# ================= FIG 1: trade gain, 3 panels, shared log scale =================
def panel_fig(cols, prefix, cmap, label, outfile, unit=1e9, mode='symlog'):
    # mode: 'symlog' (diverging log, signed USD gains) | 'linear' (diverging linear, e.g. Dln)
    vals = (pd.concat([Wm[c] for c in cols]) / unit).replace([np.inf, -np.inf], np.nan).dropna()
    if mode == 'linear':
        vmax = np.nanpercentile(np.abs(vals), 98)
        norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
        fmt = lambda x, _: ('0' if abs(x) < 1e-9 else f'{x:+.1f}')
    else:  # symlog diverging: red = positive gain, blue = negative (connectivity fell)
        vmax = np.nanpercentile(np.abs(vals), 99.5)
        norm = SymLogNorm(linthresh=1.0, vmin=-vmax, vmax=vmax, base=10)
        fmt = lambda x, _: ('0' if abs(x) < 1e-9 else f'{x:+,.0f}')
    fig, axes = plt.subplots(3, 1, figsize=(13, 15.5))
    for ax, (name, cfg) in zip(axes, MEAS.items()):
        col = f'{prefix}_{name}'
        plotcol = '_plt'
        Wm[plotcol] = Wm[col] / unit
        Wm.plot(column=plotcol, ax=ax, cmap=cmap, norm=norm,
                missing_kwds={'color': NODATA, 'edgecolor': BORD, 'linewidth': 0.15},
                edgecolor=BORD, linewidth=0.15)
        frame_ax(ax)
        ax.set_title(cfg['title'], fontsize=19, color=INK, pad=4, loc='left')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
    cax = fig.add_axes([0.90, 0.20, 0.018, 0.60])
    cb = fig.colorbar(sm, cax=cax, orientation='vertical')
    if mode == 'symlog':
        cb.set_ticks([-1000, -100, -10, 0, 10, 100, 1000])
    cb.ax.yaxis.set_major_formatter(FuncFormatter(fmt))
    cb.set_label(label, fontsize=17, color=INK, labelpad=16, rotation=270, va='bottom')
    cb.outline.set_edgecolor(BORD); cb.outline.set_linewidth(0.5)
    cb.ax.tick_params(labelsize=14, color=BORD, labelcolor=INK)
    plt.subplots_adjust(left=0.0, right=0.88, top=0.98, bottom=0.02, hspace=0.08)
    plt.savefig(outfile, dpi=170, bbox_inches='tight', facecolor='white')
    plt.close(fig); print('wrote', outfile)

panel_fig([f'tgain_{m}' for m in MEAS], 'tgain', 'RdBu_r',
          'Attributable goods-trade gain, 1996$\\rightarrow$2023 (US\\$ bn, intensity channel)',
          'GACI_contrib_trade_3panel.png', mode='symlog')
panel_fig([f'ggain_{m}' for m in MEAS], 'ggain', 'PuOr_r',
          'Attributable GDP gain, 1996$\\rightarrow$2023 (US\\$ bn, scale channel)',
          'GACI_contrib_gdp_3panel.png', mode='symlog')
panel_fig([f'dln_{m}' for m in MEAS], 'dln', 'RdBu_r',
          '$\\Delta\\ln$ GACI, 1996$\\rightarrow$2023', 'GACI_dln_3panel.png',
          unit=1, mode='linear')

# ================= FIG: aggregate bars =================
tab = pd.read_csv('_measures_contribution.csv').set_index('measure')
labels = ['cwm', 'max', 'sum']   # match manuscript Table 1 panel order
trade_int = [tab.loc[m, 'trade_int_usd']/1e12 for m in labels]
trade_vol = [tab.loc[m, 'trade_vol_usd']/1e12 for m in labels]
gdp_A     = [tab.loc[m, 'gdpA_scale_usd']/1e12 for m in labels]
x = np.arange(len(labels)); wbar = 0.26
fig, ax = plt.subplots(figsize=(9, 5.6))
b1 = ax.bar(x - wbar, trade_int, wbar, label='Trade, intensity (headline)', color='#d1495b')
b2 = ax.bar(x,        trade_vol, wbar, label='Trade, volume (upper bound)', color='#edae49')
b3 = ax.bar(x + wbar, gdp_A,     wbar, label='GDP, scale (direct $\\beta_{GDP}$)', color='#00798c')
for bars in (b1, b2, b3):
    for r in bars:
        ax.annotate(f'{r.get_height():.1f}', (r.get_x()+r.get_width()/2, r.get_height()),
                    ha='center', va='bottom', fontsize=11, color=INK)
ax.set_xticks(x); ax.set_xticklabels(['GACI$_{cwm}$', 'GACI$_{max}$', 'GACI$_{sum}$'], fontsize=14)
ax.set_ylabel('World aggregate contribution, 2023 (US\\$ trillion)', fontsize=13, color=INK)
ax.set_title('Contribution of aviation-connectivity growth 1996$\\rightarrow$2023, by measure and channel',
             fontsize=13.5, color=INK)
ax.legend(fontsize=11, frameon=False, loc='upper center', ncol=3, bbox_to_anchor=(0.5, -0.09))
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(labelsize=12, colors=INK); ax.set_ylim(0, max(trade_vol)*1.18)
plt.tight_layout(); plt.savefig('GACI_contrib_bars.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close(fig); print('wrote GACI_contrib_bars.png')
