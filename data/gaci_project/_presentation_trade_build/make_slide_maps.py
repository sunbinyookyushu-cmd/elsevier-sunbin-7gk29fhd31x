# -*- coding: utf-8 -*-
"""Slide-optimised maps for the GACI x trade conference deck (1996-2024 data, ext2024).

Every map is drawn here from the ext2024 data files; no existing PNG is reused.
Data-prep conventions follow ext2024/_mapstyle.py (ISO lookup, Antarctica removed,
Taiwan polygon shown with mainland-China values, Robinson projection).

Outputs (assets/):
  title_airports_2024.png            full-bleed title background, airports sized by GACI
  map_hubquality_2024.png            hub quality GACI_cwm (level), estimation-sample panel
  map_hubquality_2024_fullnetwork.png  same definition computed from all 2024 airports
  map_totalconn_2024.png             ln GACI_sum (the variable of the manuscript base map)
  map_contrib_trade_2024.png         attributable 2024 goods trade, cwm, openness beta=1.208
  map_covid_2019_2020.png            implied goods-trade change 2019->2020, cwm
"""
import json
import pathlib

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm, Normalize, FuncNorm, to_rgb
from matplotlib.ticker import FuncFormatter, FixedLocator

HERE = pathlib.Path(__file__).resolve().parent
EXT = HERE.parent / 'ext2024'
OUT = HERE / 'assets'
OUT.mkdir(parents=True, exist_ok=True)

# palette
INK, BRASS, TEXT, MUTED = '#1F3A32', '#B8862F', '#22211F', '#76716A'
RULE, TINT, SAGE, SLATE = '#D9D5CC', '#F3F1EC', '#7F9A8E', '#3F5A66'
NODATA = '#EAE7E1'
LAND_DARK = '#2A4A40'
MARK_EDGE = '#8C877F'

plt.rcParams.update({'font.family': 'Calibri', 'axes.unicode_minus': True})
ROBIN = '+proj=robin'
MINUS = '−'


# ---------------------------------------------------------------- data helpers
def _iso(r):
    for k in ['ISO_A3', 'ISO_A3_EH', 'ADM0_A3']:
        v = r.get(k)
        if isinstance(v, str) and v not in ('-99', ''):
            return v
    return None


def world():
    gj = json.load(open(EXT / '_world.geojson', encoding='utf-8'))
    w = gpd.GeoDataFrame.from_features(gj['features']).set_crs(4326)
    w['iso3'] = w.apply(_iso, axis=1)
    return w[w['NAME'] != 'Antarctica'].copy()


def unify_china(w, col='val'):
    """Display convention of the paper maps: Taiwan polygon shown with mainland values."""
    chn = w.loc[w['iso3'] == 'CHN', col]
    if len(chn):
        w.loc[w['iso3'] == 'TWN', col] = chn.iloc[0]
    return w


def airports(year=2024):
    ap = pd.read_csv(EXT / 'GACI1996_2024_new_panel_data.csv', encoding='utf-8-sig')
    ap = ap[ap['Year'] == year].copy()
    co = pd.read_csv(EXT / 'airport_coords_merged.csv')
    oa = pd.read_csv(EXT / 'ourairports.csv', usecols=['iata_code', 'iso_country', 'type'],
                     keep_default_na=False, na_values=[''])
    oa = oa[oa['iata_code'].notna() & (oa['iata_code'] != '')]
    pref = {'large_airport': 0, 'medium_airport': 1, 'small_airport': 2}
    oa = oa.assign(p=oa['type'].map(pref).fillna(3)).sort_values('p').drop_duplicates('iata_code')
    i23 = json.load(open(EXT / 'iso2to3.json'))
    i23['TW'] = 'TWN'   # iso2to3.json has no entry for Taiwan; its airports keep their own code
    ap['iso3'] = ap['Airport'].map(dict(zip(oa['iata_code'], oa['iso_country']))).map(i23)
    # main airports of Kyrgyzstan (Bishkek) and Moldova (Chisinau, legacy code) have no
    # iata_code match in ourairports.csv; assign them by airport code
    ap.loc[ap['Airport'] == 'FRU', 'iso3'] = 'KGZ'
    ap.loc[ap['Airport'] == 'KIV', 'iso3'] = 'MDA'
    return ap.merge(co[['Airport', 'lat', 'lon']], on='Airport', how='left')


AP = airports(2024)
_wv = world().geometry.make_valid().buffer(0)
COAST = gpd.GeoSeries([_wv.union_all()], crs=4326).boundary.to_crs(ROBIN)


def marker_points(iso_list):
    """Largest-capacity airport of each economy: marker position for economies that have
       no polygon in the 1:110m world file (Singapore, Hong Kong, Bahrain, Malta, ...)."""
    a = AP.dropna(subset=['iso3', 'lat', 'lon'])
    a = a[a['iso3'].isin(iso_list)].sort_values('TotalCapacity', ascending=False)
    a = a.drop_duplicates('iso3')
    g = gpd.GeoDataFrame(a[['iso3']], geometry=gpd.points_from_xy(a['lon'], a['lat']), crs=4326)
    return g.to_crs(ROBIN)


def signed_log_norm(vmin, vmax, lin=1.0):
    f = lambda v: np.sign(v) * np.log10(1 + np.abs(v) / lin)
    finv = lambda t: np.sign(t) * (10 ** np.abs(t) - 1) * lin
    return FuncNorm((f, finv), vmin=vmin, vmax=vmax), f


def fmt_signed(x, _):
    if abs(x) < 1e-9:
        return '0'
    s = f'{abs(x):,.0f}'
    return (MINUS + s) if x < 0 else s



def fit_limits(ax, x0, x1, y0, y1, aspect_ratio, anchor='top'):
    """Set limits with equal data aspect that exactly fill an axes of width/height = aspect_ratio."""
    w, h = x1 - x0, y1 - y0
    if w / h > aspect_ratio:            # too wide: add height
        extra = w / aspect_ratio - h
        if anchor == 'top':
            y0 -= extra
        else:
            y0 -= extra / 2; y1 += extra / 2
    else:                               # too tall: add width both sides
        extra = h * aspect_ratio - w
        x0 -= extra / 2; x1 += extra / 2
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    ax.set_aspect('equal', adjustable='box')

# ---------------------------------------------------------------- choropleth
def choropleth(vals, cmap, norm, ticks, fmt, label, outfile, cb_box=(0.545, 0.075, 0.31, 0.030),
               unify=False):
    """vals: DataFrame [iso3, val]. Taiwan keeps its own value (or no data) unless unify=True."""
    w = world().merge(vals, on='iso3', how='left')
    if unify:
        w = unify_china(w)
    w = w.to_crs(ROBIN)

    fig = plt.figure(figsize=(11.8, 5.4))
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_facecolor('white')

    w[w['val'].isna()].plot(ax=ax, color=NODATA, edgecolor='white', linewidth=0.3)
    w[w['val'].notna()].plot(ax=ax, column='val', cmap=cmap, norm=norm,
                             edgecolor='white', linewidth=0.3)
    # thin outer coastline so pale fills stay readable against the white page
    COAST.plot(ax=ax, color=RULE, linewidth=0.4)

    # economies without a polygon at this resolution -> markers at their main airport
    absent = sorted(set(vals.loc[vals['val'].notna(), 'iso3']) - set(w['iso3'].dropna()))
    mk = marker_points(absent).merge(vals, on='iso3')
    if len(mk):
        ax.scatter(mk.geometry.x, mk.geometry.y, c=mk['val'], cmap=cmap, norm=norm, s=16,
                   edgecolors=MARK_EDGE, linewidths=0.35, zorder=5)

    minx, miny, maxx, maxy = w.total_bounds
    xr = maxx - minx
    yr = maxy - miny
    fit_limits(ax, minx + 0.035 * xr, maxx + 0.01 * xr, miny - 0.10 * yr, maxy + 0.025 * yr,
               11.8 / 5.4, anchor='top')        # room under the map for the legend
    ax.axis('off')

    cax = fig.add_axes(list(cb_box))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cb = fig.colorbar(sm, cax=cax, orientation='horizontal')
    cb.ax.xaxis.set_major_locator(FixedLocator(ticks))
    cb.ax.xaxis.set_major_formatter(FuncFormatter(fmt))
    cb.ax.xaxis.set_minor_locator(FixedLocator([]))
    cb.set_label(label, fontsize=13, color=TEXT, labelpad=6)
    cb.ax.xaxis.set_label_position('top')
    cb.outline.set_edgecolor(RULE)
    cb.outline.set_linewidth(0.6)
    cb.ax.tick_params(labelsize=12, color=MUTED, labelcolor=TEXT, width=0.6, length=3)

    fig.savefig(OUT / outfile, dpi=300, facecolor='white')
    plt.close(fig)
    print('wrote', outfile, '| markers for', len(mk), 'economies without polygons')
    return w, mk


def seq_cmap():
    # pale sage start instead of pure TINT so the lowest countries do not vanish on white
    return LinearSegmentedColormap.from_list('hub', ['#E3E8E1', SAGE, INK])


# ---------------------------------------------------------------- 1. title map
def title_map():
    w = world().to_crs(ROBIN)
    a = AP.copy()
    n_all = len(a)
    a = a.dropna(subset=['lat', 'lon'])
    n_nocoord = n_all - len(a)
    pts = gpd.GeoSeries(gpd.points_from_xy(a['lon'], a['lat']), crs=4326).to_crs(ROBIN)
    a['x'], a['y'] = pts.x.values, pts.y.values
    a = a.sort_values('GACI')
    g0, g1 = a['GACI'].min(), a['GACI'].max()
    u = (a['GACI'] - g0) / (g1 - g0)
    a['s'] = 0.6 + 110 * u ** 2.0

    fig = plt.figure(figsize=(13.333, 7.5))
    fig.patch.set_facecolor(INK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(INK)
    w.plot(ax=ax, color=LAND_DARK, edgecolor='#305247', linewidth=0.25)

    top = a.nlargest(40, 'GACI')
    for mult, alpha in [(14, 0.035), (7, 0.06), (3.2, 0.10)]:
        ax.scatter(top['x'], top['y'], s=top['s'] * mult, color='#E2B866', alpha=alpha,
                   linewidths=0, zorder=3)
    ax.scatter(a['x'], a['y'], s=a['s'], color=BRASS, alpha=0.78, linewidths=0, zorder=4)
    ax.scatter(top['x'], top['y'], s=top['s'] * 0.9, color='#E8C27A', alpha=0.95,
               linewidths=0, zorder=5)

    minx, miny, maxx, maxy = w.total_bounds
    xr = maxx - minx
    fit_limits(ax, minx + 0.03 * xr, maxx - 0.005 * xr, miny, maxy, 13.333 / 7.5, anchor='center')
    ax.axis('off')

    # left-to-right darkening so the title can sit over the left side
    xs = np.linspace(0, 1, 1200)
    t = np.clip((xs - 0.26) / (0.62 - 0.26), 0, 1)
    alpha = 0.86 * (1 - (3 * t ** 2 - 2 * t ** 3))
    arr = np.zeros((4, xs.size, 4))
    arr[..., :3] = to_rgb(INK)
    arr[..., 3] = alpha
    ov = fig.add_axes([0, 0, 1, 1])
    ov.imshow(arr, extent=[0, 1, 0, 1], aspect='auto', interpolation='bilinear')
    ov.set_xlim(0, 1); ov.set_ylim(0, 1); ov.axis('off')

    fig.savefig(OUT / 'title_airports_2024.png', dpi=200, facecolor=INK)
    plt.close(fig)
    print(f'title map: {len(a)} airports plotted, {n_nocoord} without coordinates '
          f'({", ".join(AP.loc[AP["lat"].isna(), "Airport"])})')


# ---------------------------------------------------------------- 2. hub quality
def hub_maps():
    p = pd.read_csv(EXT / 'gaci_panel.csv')
    q = p[p['y'] == 2024]
    cm = seq_cmap()

    v = q[['c', 'gaci_cwmean']].rename(columns={'c': 'iso3', 'gaci_cwmean': 'val'}).dropna()
    norm = LogNorm(vmin=0.55, vmax=3.2)
    ticks = [0.6, 0.8, 1.0, 1.5, 2.0, 3.0]
    fmt = lambda x, _: f'{x:g}'
    if 'hubpanel' in RUN:
        choropleth(v, cm, norm, ticks, fmt, 'Hub quality (GACI, capacity-weighted mean), 2024',
                   'map_hubquality_2024.png', unify=True)
    print(f'  panel cwm 2024: {len(v)} economies; range {v.val.min():.2f}-{v.val.max():.2f}')

    # same definition computed from the full 2024 airport network (all economies with service)
    a = AP.dropna(subset=['iso3'])
    f = (a.assign(wG=a['TotalCapacity'] * a['GACI']).groupby('iso3')
          .agg(wG=('wG', 'sum'), cap=('TotalCapacity', 'sum')).reset_index())
    f['val'] = f['wG'] / f['cap']
    f = f[['iso3', 'val']]
    chk = v.merge(f, on='iso3', suffixes=('_panel', '_full'))
    print(f'  full-network cwm: {len(f)} economies; corr with panel = '
          f'{np.corrcoef(chk.val_panel, chk.val_full)[0,1]:.4f}; '
          f'max abs diff = {np.abs(chk.val_panel - chk.val_full).max():.3f}')
    print('  full-network CHN =', round(float(f.loc[f.iso3 == 'CHN', 'val'].iloc[0]), 4),
          '| TWN =', round(float(f.loc[f.iso3 == 'TWN', 'val'].iloc[0]), 4))
    if 'hubfull' in RUN:
        choropleth(f, cm, LogNorm(vmin=0.55, vmax=max(3.2, f.val.max())), ticks, fmt,
                   'Hub quality (GACI, capacity-weighted mean), 2024',
                   'map_hubquality_2024_fullnetwork.png')

    # manuscript base-map variable: ln GACI_sum
    s = q[['c', 'lnG']].rename(columns={'c': 'iso3', 'lnG': 'val'}).dropna()
    if 'totalconn' in RUN:
        choropleth(s, cm, Normalize(vmin=float(s.val.min()), vmax=float(s.val.max())),
                   [0, 1, 2, 3, 4, 5, 6], lambda x, _: f'{x:.0f}',
                   'Total connectivity, ln(GACI sum), 2024', 'map_totalconn_2024.png', unify=True)


# ---------------------------------------------------------------- 3. contribution
def contrib_map():
    c = pd.read_csv(EXT / '_contrib_bycountry.csv')
    v = c[['c', 'gain_cwm']].rename(columns={'c': 'iso3'})
    v['val'] = v['gain_cwm'] / 1e9
    v.loc[v['gain_cwm'] == 0, 'val'] = np.nan   # exact zero = no 2024 trade value -> shown as no data
    print(f'  contrib: {(c.gain_cwm == 0).sum()} economies with exactly zero (no 2024 trade) shown as no data')
    v = v[['iso3', 'val']]
    vmin, vmax = -300.0, 3000.0
    norm, f = signed_log_norm(vmin, vmax)
    z0 = (0 - f(vmin)) / (f(vmax) - f(vmin))
    stops = [(0.0, SLATE), (z0 * 0.55, '#8FA2AB'), (z0 * 0.93, '#D5DEE2'), (z0, '#F7F6F2'),
             (z0 + (1 - z0) * 0.10, '#F1E4C8'), (z0 + (1 - z0) * 0.62, BRASS), (1.0, '#5E4212')]
    cm = LinearSegmentedColormap.from_list('contrib', stops)
    choropleth(v, cm, norm, [-100, -10, 0, 10, 100, 1000], fmt_signed,
               'Attributable 2024 goods trade (US$ billion)', 'map_contrib_trade_2024.png')
    tot = c['gain_cwm'].sum() / 1e12
    top = c.sort_values('gain_cwm', ascending=False).head(8)
    print(f'  world sum = ${tot:.2f}T; negative countries = {(c.gain_cwm < 0).sum()} '
          f'(falling cwm: {(c.dln_cwm < 0).sum()}, of which zero-trade in 2024: '
          f'{((c.dln_cwm < 0) & (c.gain_cwm == 0)).sum()})')
    print('  top 8:', ', '.join(f'{r.c} {r.gain_cwm/1e9:,.0f}' for r in top.itertuples()))
    lo = c.sort_values('gain_cwm').head(3)
    print('  largest losses:', ', '.join(f'{r.c} {r.gain_cwm/1e9:,.0f}' for r in lo.itertuples()))


# ---------------------------------------------------------------- 4. COVID
def covid_map():
    b = pd.read_csv(EXT / '_covid_bycountry.csv')
    v = b[['c', 'tloss_cwm']].rename(columns={'c': 'iso3'})
    v['val'] = -v['tloss_cwm'] / 1e9          # negative = trade lost
    v.loc[v['tloss_cwm'] == 0, 'val'] = np.nan  # exact zero = no trade value -> shown as no data
    print(f'  covid: {(b.tloss_cwm == 0).sum()} economies with exactly zero shown as no data')
    v = v[['iso3', 'val']]
    vmin, vmax = -1200.0, 10.0
    norm, f = signed_log_norm(vmin, vmax)
    z0 = (0 - f(vmin)) / (f(vmax) - f(vmin))
    stops = [(0.0, '#2E4651'), (z0 * 0.30, SLATE), (z0 * 0.65, '#8FA2AB'), (z0 * 0.95, '#D5DEE2'),
             (z0, '#F7F6F2'), (1.0, '#E2C58E')]
    cm = LinearSegmentedColormap.from_list('covid', stops)
    choropleth(v, cm, norm, [-1000, -100, -10, 0, 10], fmt_signed,
               'Implied goods-trade change, 2019→2020 (US$ billion)', 'map_covid_2019_2020.png')
    ok = b['dln_cwm'].notna()
    print(f'  world total loss = ${b.tloss_cwm.sum()/1e12:.2f}T; fell in {(b.dln_cwm < 0).sum()} of '
          f'{ok.sum()}; median dln = {b.dln_cwm.median():.3f}; gains: {(b.tloss_cwm < 0).sum()} '
          f'(max {(-b.tloss_cwm).max()/1e9:.1f} bn)')
    top = b.sort_values('tloss_cwm', ascending=False).head(8)
    print('  top 8 losers:', ', '.join(f'{r.c} {r.tloss_cwm/1e9:,.0f}' for r in top.itertuples()))


ALL = ['title', 'hubpanel', 'hubfull', 'totalconn', 'contrib', 'covid']
RUN = ALL

if __name__ == '__main__':
    import sys
    RUN = sys.argv[1:] or ALL          # e.g.  python make_slide_maps.py hubfull contrib covid
    if 'title' in RUN:
        title_map()
    if {'hubpanel', 'hubfull', 'totalconn'} & set(RUN):
        hub_maps()
    if 'contrib' in RUN:
        contrib_map()
    if 'covid' in RUN:
        covid_map()
