# -*- coding: utf-8 -*-
"""Shared map styling for the GACI paper figures.
   Times New Roman, Robinson projection, full-bleed map (left ocean trimmed),
   large vertical colour legend in a reserved right-hand strip."""
import json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import geopandas as gpd

INK    = '#1f1f1f'     # near-black text
NODATA = '#ededed'     # countries outside the sample
BORD   = '#b3b8bd'     # country outlines


def set_times():
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                         'mathtext.fontset': 'stix', 'svg.fonttype': 'none'})


def load_world(df, key_col='c'):
    """Merge a country-indexed DataFrame onto world geometry and reproject to Robinson."""
    gj = json.load(open('_world.geojson'))
    w = gpd.GeoDataFrame.from_features(gj['features']).set_crs(4326)
    def iso(r):
        for k in ['ISO_A3', 'ISO_A3_EH', 'ADM0_A3']:
            v = r.get(k)
            if isinstance(v, str) and v not in ('-99', ''):
                return v
        return None
    w['iso3'] = w.apply(iso, axis=1)
    w = w[w['NAME'] != 'Antarctica'].merge(df, left_on='iso3', right_on=key_col, how='left')
    w = unify_china(w, [c for c in df.columns if c != key_col])
    return w.to_crs('+proj=robin')


def unify_china(w, value_cols, iso_col='iso3'):
    """Country-level display convention: colour the Taiwan polygon with the
       mainland-China values so China appears as a single unit on the map."""
    tw = w[iso_col] == 'TWN'
    chn = w.loc[w[iso_col] == 'CHN']
    if tw.any() and len(chn):
        for col in value_cols:
            w.loc[tw, col] = chn.iloc[0][col]
    return w


def render(w, column, cmap, norm, label, outfile,
           ticks=None, signed=False, tickfmt=None, crop_left=0.05, dpi=200):
    set_times()
    fig, ax = plt.subplots(figsize=(16, 7.4))
    fig.patch.set_facecolor('white'); ax.set_facecolor('white')

    w.plot(column=column, ax=ax, cmap=cmap, norm=norm,
           missing_kwds={'color': NODATA, 'edgecolor': BORD, 'linewidth': 0.2},
           edgecolor=BORD, linewidth=0.2)
    ax.axis('off')

    # tight framing; trim the empty west-Pacific wedge on the left
    minx, miny, maxx, maxy = w.total_bounds
    xr = maxx - minx
    ax.set_xlim(minx + crop_left * xr, maxx)
    ax.set_ylim(miny, maxy)

    # large vertical colour legend in the reserved right-hand strip
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
    cax = fig.add_axes([0.915, 0.16, 0.020, 0.66])   # [left, bottom, width, height]
    cb = fig.colorbar(sm, cax=cax, orientation='vertical', extend='neither')
    if ticks is not None:
        cb.set_ticks(ticks)
    if tickfmt is None:
        tickfmt = (lambda x, _: '0' if x == 0 else f'{x:+,.0f}') if signed \
                  else (lambda x, _: f'{x:,.0f}')
    cb.ax.yaxis.set_major_formatter(FuncFormatter(tickfmt))
    cb.set_label(label, fontsize=18, color=INK, labelpad=14, rotation=270, va='bottom')
    cb.outline.set_edgecolor(BORD); cb.outline.set_linewidth(0.5)
    cb.ax.tick_params(labelsize=16, color=BORD, labelcolor=INK, width=0.6, length=4)

    plt.subplots_adjust(left=0.0, right=0.90, top=1.0, bottom=0.0)
    plt.savefig(outfile, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('wrote', outfile)
