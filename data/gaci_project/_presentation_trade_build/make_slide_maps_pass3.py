# -*- coding: utf-8 -*-
"""Maps and data for the slides added on 2026-09-29 (pass 3). Drawn from ext2024 data;
no existing PNG is reused.

  assets/map_hubchange_1996_2024.png   % change in hub quality (capacity-weighted mean GACI), 1996->2024
  assets/map_krjp_about.png            small Korea-Japan map for the speaker slide (Seoul, Tokyo, Fukuoka),
                                       Natural Earth 1:50m outlines (ne_50m_admin_0_countries.geojson)
  country_change.json                  economy ranks and % change used on the country slide

Country aggregation follows ext2024/build_rank_bump_2024.py (the manuscript's rank figure):
ISO-2 country of each airport from ourairports.csv, capacity-weighted mean GACI, all airports with
scheduled service. So the ranks match the paper figure (South Korea 108 -> 12)."""
import json, pathlib
import numpy as np, pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import make_slide_maps as msm

HERE = pathlib.Path(__file__).resolve().parent
EXT = HERE.parent / 'ext2024'
OUT = HERE / 'assets'

# ---------------------------------------------------------------- country hub quality, 1996 and 2024
ap = pd.read_csv(EXT / 'GACI1996_2024_new_panel_data.csv')
oa = pd.read_csv(EXT / 'ourairports.csv', usecols=['iata_code', 'iso_country', 'type']).dropna(subset=['iata_code'])
oa['p'] = oa['type'].map({'large_airport': 0, 'medium_airport': 1, 'small_airport': 2}).fillna(3)
oa = oa.sort_values('p').drop_duplicates('iata_code')
ap['cty'] = ap['Airport'].map(dict(zip(oa['iata_code'], oa['iso_country'])))
grp = (ap.dropna(subset=['cty']).assign(wG=lambda d: d['TotalCapacity'] * d['GACI'])
         .groupby(['Year', 'cty'], as_index=False).agg(wG=('wG', 'sum'), cap=('TotalCapacity', 'sum')))
grp['cwm'] = grp['wG'] / grp['cap']
W = grp.pivot(index='cty', columns='Year', values='cwm')
R = W.rank(ascending=False, method='first')
both = W[[1996, 2024]].dropna()
chg = pd.DataFrame({'r96': R.loc[both.index, 1996].astype(int), 'r24': R.loc[both.index, 2024].astype(int),
                    'pct': 100 * (both[2024] / both[1996] - 1)})
print('economies: 1996 %d, 2024 %d, both %d; hub quality up in %.1f%%' % (
    W[1996].notna().sum(), W[2024].notna().sum(), len(both), 100 * (chg.pct > 0).mean()))
top = chg.sort_values('pct', ascending=False).head(8)
print('largest % gains:\n', top.round(1))
print('largest rank gains:\n', (chg.r96 - chg.r24).sort_values(ascending=False).head(6))
low = chg.sort_values('pct').head(6)
print('largest % falls:\n', low.round(1))
kr = [int(R.loc['KR', y]) for y in sorted(W.columns)]
json.dump(dict(n96=int(W[1996].notna().sum()), n24=int(W[2024].notna().sum()), n_both=int(len(both)),
               share_up=round(float((chg.pct > 0).mean()), 3),
               top=[[c, int(r.r96), int(r.r24), round(float(r.pct), 3)] for c, r in top.iterrows()],
               falls=[[c, int(r.r96), int(r.r24), round(float(r.pct), 3)] for c, r in low.iterrows()],
               kr_years=[int(y) for y in sorted(W.columns)], kr_rank=kr),
          open(HERE / 'country_change.json', 'w'), indent=1)
print('KR rank by year:', dict(zip(sorted(W.columns), kr)))

# ---------------------------------------------------------------- change map
i23 = json.load(open(EXT / 'iso2to3.json'))
i23['TW'] = 'TWN'
v = chg.reset_index().rename(columns={'cty': 'iso2'})
v['iso3'] = v['iso2'].map(i23)
print('unmapped iso2:', v.loc[v.iso3.isna(), 'iso2'].tolist())
v = v.dropna(subset=['iso3'])[['iso3', 'pct']].rename(columns={'pct': 'val'})
print('pct quantiles', v.val.quantile([0, .05, .25, .5, .75, .95, 1]).round(1).to_dict())
# TwoSlopeNorm puts 0 at the middle of the colour map
stops = [(0.0, msm.SLATE), (0.25, '#8FA2AB'), (0.44, '#D5DEE2'), (0.5, '#F7F6F2'),
         (0.56, '#F1E4C8'), (0.80, msm.BRASS), (1.0, '#5E4212')]
cm = LinearSegmentedColormap.from_list('chg', stops)
norm = TwoSlopeNorm(vmin=-50, vcenter=0, vmax=100)
fmt = lambda x, _: ('+%d%%' % x) if x > 0 else (('%s%d%%' % (msm.MINUS, abs(x))) if x < 0 else '0')
msm.choropleth(v, cm, norm, [-50, -25, 0, 25, 50, 100], fmt,
               'Change in hub quality, 1996 → 2024', 'map_hubchange_1996_2024.png')


# ---------------------------------------------------------------- Korea-Japan mini map (speaker slide)
def krjp_map():
    """Equirectangular with cos(lat) aspect; extent chosen so that slide coordinates are linear in lon/lat.
    Returns the extent so the slide script can place native labels on the pins."""
    ext = dict(lon0=123.0, lon1=147.0, lat0=30.0, lat1=42.6)
    k = 1 / np.cos(np.radians(36.0))
    # Natural Earth 1:50m outlines (public domain), finer than the 1:110m file used for world maps
    w = gpd.read_file(HERE / 'ne_50m_admin_0_countries.geojson')
    fig_w = 4.2
    fig_h = fig_w * (ext['lat1'] - ext['lat0']) * k / (ext['lon1'] - ext['lon0'])
    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('none')
    w.plot(ax=ax, color='#2A4A40', edgecolor='#3C6356', linewidth=0.5)
    cities = {'Seoul': (126.98, 37.57), 'Tokyo': (139.69, 35.69), 'Fukuoka': (130.40, 33.59)}
    # flight arcs between the three cities
    pairs = [('Seoul', 'Tokyo', 0.18), ('Seoul', 'Fukuoka', -0.25), ('Fukuoka', 'Tokyo', -0.22)]
    for a, b, bend in pairs:
        (x1, y1), (x2, y2) = cities[a], cities[b]
        t = np.linspace(0, 1, 60)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        cx, cy = mx - dy * bend, my + dx * bend
        xs = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
        ys = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
        ax.plot(xs, ys, color='#E2B866', lw=1.1, alpha=0.75, solid_capstyle='round')
    for name, (x, y) in cities.items():
        for s, a in ((260, 0.10), (120, 0.18)):
            ax.scatter([x], [y], s=s, color='#E2B866', alpha=a, linewidths=0, zorder=4)
        ax.scatter([x], [y], s=34, color='#E8C27A', edgecolors='#1F3A32', linewidths=0.8, zorder=5)
    ax.set_xlim(ext['lon0'], ext['lon1'])
    ax.set_ylim(ext['lat0'], ext['lat1'])
    ax.set_aspect(k)
    ax.axis('off')
    fig.savefig(OUT / 'map_krjp_about.png', dpi=300, transparent=True)
    plt.close(fig)
    # soft edges: fade the alpha channel towards all four borders so the clipped land has no hard edge
    from PIL import Image
    im = Image.open(OUT / 'map_krjp_about.png').convert('RGBA')
    a = np.asarray(im).astype(float)
    h, w_ = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w_]
    d = np.minimum.reduce([xx / (0.16 * w_), (w_ - 1 - xx) / (0.10 * w_), yy / (0.20 * h), (h - 1 - yy) / (0.12 * h)])
    fade = np.clip(d, 0, 1) ** 1.6
    a[..., 3] *= fade
    Image.fromarray(a.astype(np.uint8), 'RGBA').save(OUT / 'map_krjp_about.png')
    ext.update(cities=cities, aspect=float(k))
    json.dump(ext, open(HERE / 'krjp_extent.json', 'w'), indent=1)
    print('wrote map_krjp_about.png', round(fig_w, 2), 'x', round(fig_h, 2), 'in')


krjp_map()
