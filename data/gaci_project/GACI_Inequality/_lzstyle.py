# -*- coding: utf-8 -*-
"""Figure style following the CO2 paper figures (Longfei, 2026-09-23): Arial, bold panel letters outside the axes,
   boxed axes, filled crimson markers for significant estimates and hollow grey for insignificant, value labels,
   vertical-gradient bars, Robinson maps with graticule, hatched no-data and a horizontal colour bar."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.patches import Rectangle
RED, BLUE, GREY, INK = "#B22234", "#2E75B6", "#8C8C8C", "#1f1f1f"
LIGHTRED, LIGHTBLUE = "#F2C1C6", "#C9DBEF"

def setup():
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"], "font.size": 13,
                         "axes.labelsize": 15, "axes.titlesize": 16, "xtick.labelsize": 13, "ytick.labelsize": 13, "legend.fontsize": 12,
                         "axes.linewidth": 1.0, "xtick.direction": "out", "ytick.direction": "out", "axes.spines.top": True, "axes.spines.right": True,
                         "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold", "svg.fonttype": "none"})

def panel_letter(ax, letter, dx=-0.06, dy=1.02):
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=22, fontweight="bold", ha="left", va="bottom", color=INK)

def coef_points(ax, x, b, se, p, orient="v", label_fmt="%.2f", label_offset=8, sig=0.10, color_sig=RED, color_ns=GREY, size=9, capsize=4, lw=1.6, labels=True, neg_color=None):
    """Point estimates with 95% CI; filled if p<sig, hollow otherwise. orient 'v': x positions, values on y."""
    for xi, bi, si, pi in zip(x, b, se, p):
        if np.isnan(bi): continue
        s = pi < sig; col = (neg_color if (neg_color and bi < 0 and s) else color_sig) if s else color_ns
        mfc = col if s else "white"
        if orient == "v":
            ax.errorbar(xi, bi, yerr=1.96 * si, fmt="o", ms=size, color=col, mfc=mfc, mec=col, mew=1.6, ecolor=col, elinewidth=lw, capsize=capsize, capthick=lw, zorder=3)
            if labels: ax.annotate(label_fmt % bi, (xi, bi + 1.96 * si), xytext=(0, label_offset), textcoords="offset points", ha="center", va="bottom", fontsize=12, color=INK)
        else:
            ax.errorbar(bi, xi, xerr=1.96 * si, fmt="o", ms=size, color=col, mfc=mfc, mec=col, mew=1.6, ecolor=col, elinewidth=lw, capsize=capsize, capthick=lw, zorder=3)
            if labels: ax.annotate(label_fmt % bi, (bi, xi), xytext=(0, label_offset), textcoords="offset points", ha="center", va="bottom", fontsize=12, color=INK)

def zero_line(ax, orient="v"):
    (ax.axhline if orient == "v" else ax.axvline)(0, color=GREY, lw=1.2, ls="--", zorder=1)

def gradient_bar(ax, x, height, width=0.6, color=RED, bottom=0.0, light=None, zorder=2):
    """Vertical bar with a light-to-full colour gradient (as in the CO2 figure)."""
    light = light or (LIGHTRED if color == RED else LIGHTBLUE)
    cmap = LinearSegmentedColormap.from_list("g", [light, color])
    y0, y1 = (bottom, bottom + height) if height >= 0 else (bottom + height, bottom)
    n = 200; grad = np.linspace(0, 1, n).reshape(n, 1)
    if height < 0: grad = grad[::-1]
    ax.imshow(grad, extent=[x - width / 2, x + width / 2, y0, y1], aspect="auto", cmap=cmap, origin="lower", zorder=zorder, interpolation="bicubic")
    ax.add_patch(Rectangle((x - width / 2, y0), width, y1 - y0, fill=False, edgecolor="none"))

def hgradient_bar(ax, y, length, height=0.7, color=RED, light=None, zorder=2):
    light = light or (LIGHTRED if color == RED else LIGHTBLUE)
    cmap = LinearSegmentedColormap.from_list("g", [light, color])
    x0, x1 = (0, length) if length >= 0 else (length, 0)
    n = 200; grad = np.linspace(0, 1, n).reshape(1, n)
    if length < 0: grad = grad[:, ::-1]
    ax.imshow(grad, extent=[x0, x1, y - height / 2, y + height / 2], aspect="auto", cmap=cmap, origin="lower", zorder=zorder, interpolation="bicubic")

# ---------------- maps ----------------
def world_robinson(df, key="c", geojson="../_world.geojson"):
    import geopandas as gpd
    gj = json.load(open(geojson)); w = gpd.GeoDataFrame.from_features(gj["features"]).set_crs(4326)
    def iso(r):
        for k in ["ISO_A3", "ISO_A3_EH", "ADM0_A3"]:
            v = r.get(k)
            if isinstance(v, str) and v not in ("-99", ""): return v
        return None
    w["iso3"] = w.apply(iso, axis=1); w["is_ant"] = w["NAME"] == "Antarctica"
    w = w.merge(df, left_on="iso3", right_on=key, how="left")
    tw = w.iso3 == "TWN"; ch = w[w.iso3 == "CHN"]
    if tw.any() and len(ch):
        for c in [c for c in df.columns if c != key]: w.loc[tw, c] = ch.iloc[0][c]
    return w.to_crs("+proj=robin")

def graticule(ax, crs="+proj=robin", lons=range(-180, 181, 60), lats=range(-60, 61, 30), color="#c8c8c8", lw=0.5):
    import geopandas as gpd
    from shapely.geometry import LineString
    lines = [LineString([(lo, la) for la in np.linspace(-89.9, 89.9, 181)]) for lo in lons] + [LineString([(lo, la) for lo in np.linspace(-180, 180, 361)]) for la in lats]
    g = gpd.GeoSeries(lines, crs=4326).to_crs(crs); g.plot(ax=ax, color=color, linewidth=lw, zorder=1)
    edge = gpd.GeoSeries([LineString([(lo, la) for lo, la in [(-180, y) for y in np.linspace(-90, 90, 181)] + [(x, 90) for x in np.linspace(-180, 180, 361)] + [(180, y) for y in np.linspace(90, -90, 181)] + [(x, -90) for x in np.linspace(180, -180, 361)]])], crs=4326).to_crs(crs)
    edge.plot(ax=ax, color="#9a9a9a", linewidth=0.8, zorder=1)
    # tick-like labels
    for la in lats:
        p = gpd.GeoSeries([LineString([(-180, la), (-179, la)])], crs=4326).to_crs(crs).iloc[0].coords[0]
        ax.text(p[0] - 3e5, p[1], f"{abs(la)}°{'N' if la > 0 else 'S' if la < 0 else ''}", ha="right", va="center", fontsize=10, color=INK)
    for lo in lons:
        p = gpd.GeoSeries([LineString([(lo, -90), (lo, -89)])], crs=4326).to_crs(crs).iloc[0].coords[0]
        ax.text(p[0], p[1] - 4e5, f"{abs(lo)}°{'E' if lo > 0 else 'W' if lo < 0 else ''}", ha="center", va="top", fontsize=10, color=INK)

def draw_map(ax, w, column, cmap, norm, title=None, cbar_label=None, cbar_ticks=None, cbar_ticklabels=None, fig=None, cbar=True):
    ax.set_axis_off()
    w[w.is_ant].plot(ax=ax, facecolor="white", edgecolor="#9a9a9a", linewidth=0.4, hatch="////", zorder=2)
    body = w[~w.is_ant]
    body.plot(column=column, ax=ax, cmap=cmap, norm=norm, edgecolor="#5a6f8a", linewidth=0.35, missing_kwds={"facecolor": "white", "edgecolor": "#9a9a9a", "hatch": "////", "linewidth": 0.35}, zorder=2)
    graticule(ax)
    if title: ax.set_title(title, fontsize=15, pad=6)
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, edgecolor="none"))
    hp = Rectangle((0.02, 0.06), 0.03, 0.05, transform=ax.transAxes, facecolor="white", edgecolor="#5a6f8a", hatch="////", lw=0.6); ax.add_patch(hp)
    ax.text(0.06, 0.085, "No data", transform=ax.transAxes, fontsize=11, va="center")
    if cbar and fig is not None:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
        cb = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.05, pad=0.02, aspect=40)
        if cbar_ticks is not None: cb.set_ticks(cbar_ticks)
        if cbar_ticklabels is not None: cb.set_ticklabels(cbar_ticklabels)
        if cbar_label: cb.set_label(cbar_label, fontsize=13)
        cb.ax.tick_params(labelsize=12)
        return cb
