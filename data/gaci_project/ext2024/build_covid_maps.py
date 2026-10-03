# -*- coding: utf-8 -*-
"""3-panel COVID-19 (2019->2020) connectivity-shock trade-effect map, one panel per
measure (cwm/max/sum), same style as GACI_contrib_trade_3panel. Red = trade gained,
blue = trade lost during the collapse. Reads _covid_bycountry.csv."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from matplotlib.ticker import FuncFormatter
import geopandas as gpd

INK, NODATA, BORD = '#1f1f1f', '#ededed', '#b3b8bd'
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'], 'mathtext.fontset': 'stix'})
MEAS = {  # cwm / max / sum, matching Table 1 order
    'cwm': 'Panel A.  Hub quality, GACI$_{\\mathrm{cwm}}$ (headline)',
    'max': 'Panel B.  Maximum hub, GACI$_{\\mathrm{max}}$',
    'sum': 'Panel C.  Total connectivity, GACI$_{\\mathrm{sum}}$',
}

bc = pd.read_csv('_covid_bycountry.csv')
# signed trade change (US$ bn): gain>0 red, loss<0 blue  (= -loss)
for m in MEAS:
    bc[f'chg_{m}'] = -bc[f'tloss_{m}'] / 1e9

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
Wm = W.merge(bc, left_on='iso3', right_on='c', how='left')
import _mapstyle as ms
Wm = ms.unify_china(Wm, [c for c in bc.columns if c != 'c'])

cols = [f'chg_{m}' for m in MEAS]
vals = pd.concat([Wm[c] for c in cols]).replace([np.inf, -np.inf], np.nan).dropna()
vmax = np.nanpercentile(np.abs(vals), 99.5)
norm = SymLogNorm(linthresh=1.0, vmin=-vmax, vmax=vmax, base=10)
fmt = lambda x, _: ('0' if abs(x) < 1e-9 else f'{x:+,.0f}')

fig, axes = plt.subplots(3, 1, figsize=(13, 15.5))
for ax, (m, title) in zip(axes, MEAS.items()):
    Wm['_plt'] = Wm[f'chg_{m}']
    Wm.plot(column='_plt', ax=ax, cmap='RdBu_r', norm=norm,
            missing_kwds={'color': NODATA, 'edgecolor': BORD, 'linewidth': 0.15},
            edgecolor=BORD, linewidth=0.15)
    minx, miny, maxx, maxy = W.total_bounds; xr = maxx - minx
    ax.set_xlim(minx + 0.05*xr, maxx); ax.set_ylim(miny, maxy); ax.axis('off')
    ax.set_title(title, fontsize=19, color=INK, pad=4, loc='left')
sm = plt.cm.ScalarMappable(cmap='RdBu_r', norm=norm); sm.set_array([])
cax = fig.add_axes([0.90, 0.20, 0.018, 0.60])
cb = fig.colorbar(sm, cax=cax, orientation='vertical')
cb.set_ticks([-1000, -100, -10, 0, 10, 100, 1000])
cb.ax.yaxis.set_major_formatter(FuncFormatter(fmt))
cb.set_label('COVID-19 (2019$\\rightarrow$2020) trade effect (US\\$ bn; blue = trade lost)',
             fontsize=17, color=INK, labelpad=16, rotation=270, va='bottom')
cb.outline.set_edgecolor(BORD); cb.outline.set_linewidth(0.5)
cb.ax.tick_params(labelsize=14, color=BORD, labelcolor=INK)
plt.subplots_adjust(left=0.0, right=0.88, top=0.98, bottom=0.02, hspace=0.08)
plt.savefig('GACI_covid_shock_3panel.png', dpi=170, bbox_inches='tight', facecolor='white')
plt.close(fig); print('wrote GACI_covid_shock_3panel.png')
