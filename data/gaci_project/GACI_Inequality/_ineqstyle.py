# -*- coding: utf-8 -*-
"""Own figure identity for the inequality paper (distinct from the CO2 paper figures).
   Arial; open axes with a faint horizontal grid; diamond markers with a thick 90% bar and a thin 95% bar;
   teal for significant positive, amber for significant negative, light slate for insignificant; panel labels
   as bold letters inside the axes; lollipop charts instead of gradient bars; Equal Earth maps without graticule,
   soft no-data grey, vertical colour bar, BrBG/PuOr palettes."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
TEAL, AMBER, SLATE, INK = "#137C7C", "#D9822B", "#9AA5B1", "#222222"
GRID, NODATA, BORD = "#E4E7EB", "#DADDE1", "#8A94A0"

def setup():
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"], "font.size": 12.5,
                         "axes.labelsize": 14, "axes.titlesize": 14.5, "xtick.labelsize": 12.5, "ytick.labelsize": 12.5, "legend.fontsize": 11.5,
                         "axes.linewidth": 0.9, "axes.edgecolor": "#444444", "xtick.direction": "out", "ytick.direction": "out",
                         "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
                         "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold", "svg.fonttype": "none"})

def panel_letter(ax, letter, x=0.012, y=0.975):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=19, fontweight="bold", ha="left", va="bottom", color=INK)

def coef_points(ax, x, b, se, p, orient="v", label_fmt="%.2f", label_offset=9, sig=0.10, labels=True, size=8.5):
    """Diamond point, thick 90% CI, thin 95% CI. Teal if significant positive, amber if significant negative, slate otherwise."""
    for xi, bi, si, pi in zip(x, b, se, p):
        if np.isnan(bi): continue
        s = pi < sig; col = (TEAL if bi >= 0 else AMBER) if s else SLATE; z = 3
        lo95, hi95 = bi - 1.96 * si, bi + 1.96 * si; lo90, hi90 = bi - 1.645 * si, bi + 1.645 * si
        if orient == "v":
            ax.plot([xi, xi], [lo95, hi95], color=col, lw=1.1, solid_capstyle="round", zorder=z); ax.plot([xi, xi], [lo90, hi90], color=col, lw=3.2, solid_capstyle="butt", zorder=z)
            ax.plot(xi, bi, marker="D", ms=size, color=col, mfc="white" if not s else col, mec=col, mew=1.5, zorder=z + 1)
            if labels: ax.annotate(label_fmt % bi, (xi, hi95), xytext=(0, label_offset), textcoords="offset points", ha="center", va="bottom", fontsize=11, color=INK)
        else:
            ax.plot([lo95, hi95], [xi, xi], color=col, lw=1.1, solid_capstyle="round", zorder=z); ax.plot([lo90, hi90], [xi, xi], color=col, lw=3.2, solid_capstyle="butt", zorder=z)
            ax.plot(bi, xi, marker="D", ms=size, color=col, mfc="white" if not s else col, mec=col, mew=1.5, zorder=z + 1)
            if labels: ax.annotate(label_fmt % bi, (bi, xi), xytext=(0, label_offset), textcoords="offset points", ha="center", va="bottom", fontsize=11, color=INK)

def zero_line(ax, orient="v"):
    (ax.axhline if orient == "v" else ax.axvline)(0, color="#666666", lw=1.0, zorder=1)

def lollipop(ax, y, value, color=None, label=True, fmt="%+.1f"):
    col = color or (TEAL if value >= 0 else AMBER)
    ax.plot([0, value], [y, y], color=col, lw=2.2, solid_capstyle="round", zorder=2); ax.plot(value, y, "o", ms=9, color=col, zorder=3)
    if label: ax.text(value + (0.5 if value >= 0 else -0.5), y, fmt % value, ha="left" if value >= 0 else "right", va="center", fontsize=11, color=INK)

def mono_cmap(color, light="#F4F6F8", name="mono"):
    """Single-hue sequential colour map: near-white to the given colour."""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list(name, [light, color])

# ---------------- maps ----------------
def world_map(df, key="c", geojson="../_world.geojson", crs="+proj=eqearth"):
    import geopandas as gpd
    gj = json.load(open(geojson)); w = gpd.GeoDataFrame.from_features(gj["features"]).set_crs(4326)
    def iso(r):
        for k in ["ISO_A3", "ISO_A3_EH", "ADM0_A3"]:
            v = r.get(k)
            if isinstance(v, str) and v not in ("-99", ""): return v
        return None
    w["iso3"] = w.apply(iso, axis=1); w = w[w["NAME"] != "Antarctica"]
    w = w.merge(df, left_on="iso3", right_on=key, how="left")
    tw = w.iso3 == "TWN"; ch = w[w.iso3 == "CHN"]
    if tw.any() and len(ch):
        for c in [c for c in df.columns if c != key]: w.loc[tw, c] = ch.iloc[0][c]
    return w.to_crs(crs)

def draw_map(ax, w, column, cmap, norm, title=None, fig=None, cbar_label=None, cbar_ticks=None, cbar=True):
    ax.set_axis_off(); ax.grid(False)
    w.plot(column=column, ax=ax, cmap=cmap, norm=norm, edgecolor="white", linewidth=0.35, missing_kwds={"facecolor": NODATA, "edgecolor": "white", "linewidth": 0.35}, zorder=2)
    if title: ax.set_title(title, fontsize=14, pad=8, loc="left")
    if cbar and fig is not None:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
        cb = fig.colorbar(sm, ax=ax, orientation="vertical", fraction=0.025, pad=0.01, aspect=28)
        if cbar_ticks is not None: cb.set_ticks(cbar_ticks)
        if cbar_label: cb.set_label(cbar_label, fontsize=12)
        cb.ax.tick_params(labelsize=11); cb.outline.set_visible(False)
        return cb
