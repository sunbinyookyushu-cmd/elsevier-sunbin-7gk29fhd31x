# -*- coding: utf-8 -*-
"""50_figs_gaci_build.py : figures describing the construction of the GACI panel and the geography of hub connectivity,
   drawn from the airport-year panel (../GACI1996_2024_new_panel_data.csv) in the paper's own style (_ineqstyle.py).
   Figure set (analogues of the descriptive figures in Cheung, Wong and Zhang 2020 TRE, redrawn from our own 1996-2023 panel):
     FigB1_gaci_construction  (a) schematic of link intensity and indirect flows through a hub
                              (b) correlation of the five indicators, all airport-years 1996-2023
                              (c) eigenvector centrality vs degree, 2023, coloured by GACI
                              (d) GACI vs seat capacity, 2023 (connectivity is not volume)
     FigB2_network_evolution  (a) airports with scheduled service, 1996-2023   (b) complementary CDF of degree, four years
                              (c) the twenty most connected airports in 2023 and their 1996 index (dumbbell)
     FigB3_maps_hubs          (a) airports in 2023, point size = GACI, twenty largest labelled   (b) country hub connectivity ln GACI_max, 2023
     FigB4_map_change         change in ln GACI_max between first and last year, by country
   Inputs: ../GACI1996_2024_new_panel_data.csv, ../airport_coords_merged.csv, ineq_panel.csv, ../_world.geojson"""
import os, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm, LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Circle
import _ineqstyle as lz
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D); lz.setup()
TEAL, AMBER, SLATE, INK = lz.TEAL, lz.AMBER, lz.SLATE, lz.INK
Y0, Y1 = 1996, 2023

a = pd.read_csv("../GACI1996_2024_new_panel_data.csv", encoding="utf-8", encoding_errors="replace")
a.columns = [c.strip().lstrip("﻿") for c in a.columns]
for k in ["Degree", "TotalCapacity", "Eigen", "NorClose", "NorBetweenness", "RegionalImportance", "GACI"]: a[k] = pd.to_numeric(a[k], errors="coerce")
a["Airport"] = a["Airport"].str.strip(); a = a[(a.Year >= Y0) & (a.Year <= Y1)]
co = pd.read_csv("../airport_coords_merged.csv"); co["Airport"] = co["Airport"].str.strip()
pan = pd.read_csv("ineq_panel.csv", usecols=["c", "y", "gaci_max"])

# ======================= Figure B1: construction =======================
fig, axs = plt.subplots(2, 2, figsize=(14.5, 11.5))
# (a) schematic
ax = axs[0, 0]; ax.set_axis_off(); ax.set_xlim(0, 10); ax.set_ylim(0, 8.6)
pos = {"LHR": (1.0, 6.9), "FRA": (2.6, 5.9), "DXB": (4.2, 7.6), "HKG": (5.0, 4.3), "SIN": (6.4, 3.1), "SYD": (7.6, 2.0), "PER": (8.9, 4.5)}
links = [("LHR", "FRA", 1.6), ("FRA", "HKG", 3.4), ("DXB", "HKG", 2.2), ("HKG", "SIN", 1.4), ("HKG", "SYD", 3.0), ("HKG", "PER", 1.6), ("SYD", "PER", 1.2), ("SIN", "SYD", 1.0)]
for u, v, w in links: ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color="#9FC9C9", lw=w * 2.2, solid_capstyle="round", zorder=1)
for k, (x, y) in pos.items():
    hub = k == "HKG"; ax.add_patch(Circle((x, y), 0.34 if hub else 0.24, facecolor=AMBER if hub else TEAL, edgecolor="white", lw=1.5, zorder=3))
    ax.text(x, y - (0.62 if hub else 0.48), k, ha="center", va="top", fontsize=12, color=INK, fontweight="bold" if hub else "normal")
ax.text(0.35, 4.35, r"$w_{ij}=\sqrt{s_i s_j\,/\,(d_i d_j)}$", fontsize=12.5, color="#2F6F6F", ha="left", va="center")
for (x0, y0, x1, y1, r) in [(0.4, 3.4, 9.3, 6.9, -0.25), (1.2, 1.2, 9.6, 5.6, 0.25), (2.2, 0.6, 8.2, 7.9, 0.15)]:
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), connectionstyle=f"arc3,rad={r}", arrowstyle="-|>", mutation_scale=12, color="#7A8794", lw=1.1, ls=(0, (4, 3)), zorder=2))
ax.text(0.1, 0.25, "Nodes: airports; the hub is in amber. Link width: link intensity $w_{ij}$ (seat capacity per connection).\nDashed arcs: origin-destination flows routed through the hub (flow betweenness).", fontsize=10.5, color="#555555", va="bottom")
ax.set_title("Airport network, link intensities and indirect flows", loc="left", pad=8); lz.panel_letter(ax, "a", x=-0.08, y=1.0)
# (b) correlation of the five indicators
ax = axs[0, 1]
ind = pd.DataFrame({"Degree (log)": np.log(a.Degree), "Seat capacity (log)": np.log(a.TotalCapacity), "Eigenvector": a.Eigen, "Closeness": a.NorClose, "Flow betweenness (log)": np.log1p(a.NorBetweenness), "Regional importance": a.RegionalImportance, "GACI": a.GACI}).replace([np.inf, -np.inf], np.nan).dropna()
C = ind.corr(); n = len(C)
im = ax.imshow(C.values, cmap=lz.mono_cmap(TEAL), vmin=0, vmax=1)
ax.set_xticks(range(n)); ax.set_yticks(range(n)); ax.set_xticklabels(C.columns, rotation=45, ha="right", fontsize=11); ax.set_yticklabels(C.columns, fontsize=11); ax.grid(False)
for i in range(n):
    for j in range(n): ax.text(j, i, "%.2f" % C.values[i, j], ha="center", va="center", fontsize=10, color="white" if C.values[i, j] > 0.6 else INK)
for s in ax.spines.values(): s.set_visible(False)
ax.set_title("Correlation of the indicators, all airport-years 1996–2023", loc="left", pad=8); lz.panel_letter(ax, "b", x=-0.32, y=1.0)
# (c) eigenvector vs degree, 2023
ax = axs[1, 0]; t = a[a.Year == Y1].dropna(subset=["Degree", "Eigen", "GACI"]); t = t[t.Degree > 0]
sc = ax.scatter(t.Degree, t.Eigen, c=t.GACI, cmap=lz.mono_cmap(TEAL), norm=Normalize(t.GACI.quantile(0.02), t.GACI.max()), s=14 + 60 * (t.GACI - t.GACI.min()) / (t.GACI.max() - t.GACI.min()), alpha=0.85, lw=0.3, edgecolors="white", zorder=3)
ax.set_xscale("log"); ax.set_xlabel("Degree (number of directly connected airports, log scale)"); ax.set_ylabel("Weighted eigenvector centrality")
for code, dx, dy in [("ATL", 6, 2), ("LAX", 6, -2), ("ORD", 6, 2), ("DFW", 6, -4), ("LHR", 6, 2), ("DXB", 6, 6), ("FRA", 6, -3), ("IST", 6, -8), ("AMS", -30, -10)]:
    r = t[t.Airport == code]
    if len(r): ax.annotate(code, (r.Degree.iloc[0], r.Eigen.iloc[0]), xytext=(dx, dy), textcoords="offset points", fontsize=9.5, color=INK)
cb = fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.02); cb.set_label("GACI, 2023"); cb.outline.set_visible(False)
ax.set_title("Eigenvector centrality and degree, 2023", loc="left", pad=8); lz.panel_letter(ax, "c", x=-0.16, y=1.0)
# (d) GACI vs seat capacity, 2023
ax = axs[1, 1]; t2 = t[t.TotalCapacity > 0]
ax.scatter(t2.TotalCapacity, t2.GACI, s=12, color=TEAL, alpha=0.45, lw=0, zorder=3)
ax.set_xscale("log"); ax.set_xlabel("Annual seat capacity (log scale)"); ax.set_ylabel("GACI, 2023")
for code, dx, dy in [("FRA", -28, 4), ("DXB", 6, 2), ("ATL", 6, -6), ("PEK", 6, 4), ("DOH", -30, -4), ("DEL", 6, 2), ("GRU", -30, -6), ("JNB", 6, -4), ("AKL", -30, 2)]:
    r = t2[t2.Airport == code]
    if len(r): ax.annotate(code, (r.TotalCapacity.iloc[0], r.GACI.iloc[0]), xytext=(dx, dy), textcoords="offset points", fontsize=9.5, color=INK)
ax.set_title("Connectivity is not volume: GACI and seat capacity, 2023", loc="left", pad=8); lz.panel_letter(ax, "d", x=-0.16, y=1.0)
fig.tight_layout(w_pad=3, h_pad=4); fig.savefig("FigB1_gaci_construction.png", dpi=300, bbox_inches="tight"); fig.savefig("FigB1_gaci_construction.pdf", bbox_inches="tight"); plt.close(fig)

# ======================= Figure B2: network evolution =======================
fig, axs = plt.subplots(1, 3, figsize=(17, 5.6), gridspec_kw={"width_ratios": [1, 1, 1.25]})
ax = axs[0]; yr = a.groupby("Year").agg(n=("Airport", "size"), links=("Degree", lambda s: s.sum() / 2), seats=("TotalCapacity", "sum"))
ax.plot(yr.index, yr.n, color=TEAL, lw=2.6, marker="o", ms=4.5); ax.set_ylabel("Airports with scheduled service"); ax.set_xlabel("Year")
ax.axvspan(2020, 2021.9, color="#F3F5F7", zorder=0); ax.text(2020.95, yr.n.min() + 0.04 * (yr.n.max() - yr.n.min()), "COVID-19", ha="center", fontsize=10, color="#8A94A0")
ax.set_title("Size of the network", loc="left", pad=8); lz.panel_letter(ax, "a", x=-0.2, y=1.02)
ax = axs[1]
for y, c in [(1996, "#BFDCDC"), (2008, "#7FBABA"), (2019, "#3F9797"), (2023, TEAL)]:
    d = np.sort(a[a.Year == y].Degree.dropna().values); d = d[d > 0]; ccdf = 1 - np.arange(len(d)) / len(d)
    ax.plot(d, ccdf, color=c, lw=2.2 if y == 2023 else 1.8, label=str(y))
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Degree $k$ (log scale)"); ax.set_ylabel("Share of airports with degree $\\geq k$"); ax.legend(frameon=False, title=None, loc="lower left")
ax.set_title("Degree distribution", loc="left", pad=8); lz.panel_letter(ax, "b", x=-0.2, y=1.02)
ax = axs[2]; top = a[a.Year == Y1].nlargest(20, "GACI")[["Airport", "GACI"]].merge(a[a.Year == Y0][["Airport", "GACI"]].rename(columns={"GACI": "g0"}), how="left")
top = top.sort_values("GACI"); ys = np.arange(len(top))
for i, r in enumerate(top.itertuples()):
    if not np.isnan(r.g0): ax.plot([r.g0, r.GACI], [i, i], color="#C9CED4", lw=2.2, zorder=1); ax.plot(r.g0, i, "o", ms=7, color=SLATE, zorder=2)
    ax.plot(r.GACI, i, "o", ms=8, color=TEAL, zorder=3)
ax.set_yticks(ys); ax.set_yticklabels(top.Airport); ax.set_xlabel("GACI"); ax.grid(axis="y", visible=False)
ax.plot([], [], "o", color=SLATE, label="1996"); ax.plot([], [], "o", color=TEAL, label="2023"); ax.legend(frameon=False, loc="lower right")
ax.set_title("The twenty most connected airports, 2023 and 1996", loc="left", pad=8); lz.panel_letter(ax, "c", x=-0.16, y=1.02)
fig.tight_layout(w_pad=3.5); fig.savefig("FigB2_network_evolution.png", dpi=300, bbox_inches="tight"); fig.savefig("FigB2_network_evolution.pdf", bbox_inches="tight"); plt.close(fig)

# ======================= Figure B3: maps of hubs =======================
import geopandas as gpd
from shapely.geometry import Point
last = pan.groupby("c").y.max(); cm = pan.merge(last.rename("ymax"), on="c"); cm = cm[cm.y == cm.ymax]
cm = cm[cm.y >= 2019]; cm["lng"] = np.log(cm.gaci_max)        # latest year 2019-2023 for each country
w = lz.world_map(cm[["c", "lng"]], key="c")
pts = a[a.Year == Y1].merge(co[["Airport", "lat", "lon"]], on="Airport", how="inner").dropna(subset=["lat", "lon", "GACI"])
gp = gpd.GeoDataFrame(pts, geometry=[Point(x, y) for x, y in zip(pts.lon, pts.lat)], crs=4326).to_crs("+proj=eqearth")
fig, axs = plt.subplots(2, 1, figsize=(14, 14.5))
ax = axs[0]; ax.set_axis_off(); ax.grid(False)
w.plot(ax=ax, facecolor="#EEF1F4", edgecolor="white", linewidth=0.35, zorder=1)
g = gp.sort_values("GACI"); s = 3 + 110 * ((g.GACI - g.GACI.min()) / (g.GACI.max() - g.GACI.min())) ** 2
ax.scatter(g.geometry.x, g.geometry.y, s=s, color=TEAL, alpha=0.55, lw=0.3, edgecolors="white", zorder=3)
LABS = {"LHR": (-34, 8), "FRA": (6, 8), "IST": (6, 2), "DXB": (8, 2), "JED": (-8, -14), "ATL": (6, -4), "ORD": (-6, 10), "DFW": (-34, -8), "LAX": (-34, -4), "SFO": (-34, 6), "DEN": (-14, 10), "MIA": (8, -6), "JFK": (8, 2), "YYZ": (4, 10), "PVG": (8, 2), "CAN": (8, -8), "SIN": (8, -2), "CDG": (2, -14), "AMS": (-2, 14), "DEL": (8, -4)}
for _, r in g[g.Airport.isin(LABS)].iterrows(): ax.annotate(r.Airport, (r.geometry.x, r.geometry.y), xytext=LABS[r.Airport], textcoords="offset points", fontsize=9.5, color=INK, zorder=4)
for v, lab, xx in [(0.5, "0.5", 0.62), (1.5, "1.5", 0.70), (2.5, "2.5", 0.79), (3.2, "3.2", 0.89)]:
    ss = 3 + 110 * ((v - g.GACI.min()) / (g.GACI.max() - g.GACI.min())) ** 2
    ax.scatter([xx], [0.06], s=ss, transform=ax.transAxes, color=TEAL, alpha=0.55, lw=0.3, edgecolors="white", zorder=5); ax.text(xx, 0.015, lab, transform=ax.transAxes, ha="center", va="top", fontsize=10, color="#555555")
ax.text(0.56, 0.06, "GACI:", transform=ax.transAxes, ha="right", va="center", fontsize=10.5, color="#555555")
ax.set_title("Airports with scheduled service in 2023, point size proportional to GACI", loc="left", fontsize=14, pad=6); lz.panel_letter(ax, "a", x=-0.03, y=0.98)
ax = axs[1]
lz.draw_map(ax, w, "lng", lz.mono_cmap(TEAL), Normalize(vmin=np.nanpercentile(w.lng, 2), vmax=np.nanmax(w.lng)), title="Hub connectivity by country, ln GACI$_{max}$, 2023", fig=fig, cbar_label="ln GACI$_{max}$")
lz.panel_letter(ax, "b", x=-0.03, y=0.98)
fig.subplots_adjust(hspace=0.06); fig.savefig("FigB3_maps_hubs.png", dpi=250, bbox_inches="tight"); fig.savefig("FigB3_maps_hubs.pdf", bbox_inches="tight"); plt.close(fig)

# ======================= Figure B4: change map =======================
first = pan.sort_values("y").groupby("c").first().rename(columns={"y": "y0", "gaci_max": "g0"}); lastv = pan.sort_values("y").groupby("c").last().rename(columns={"y": "y1", "gaci_max": "g1"})
ch = first.join(lastv); ch = ch[(ch.y1 - ch.y0) >= 15]; ch["dlng"] = np.log(ch.g1) - np.log(ch.g0); ch = ch.reset_index()
w2 = lz.world_map(ch[["c", "dlng"]], key="c")
lim = float(np.nanpercentile(np.abs(w2.dlng), 97))
div = LinearSegmentedColormap.from_list("div", [AMBER, "#F7F4EF", TEAL])
fig, ax = plt.subplots(figsize=(14, 7.2))
lz.draw_map(ax, w2, "dlng", div, TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim), title="Change in hub connectivity, ln GACI$_{max}$, first to last year (1996–2023)", fig=fig, cbar_label="Δ ln GACI$_{max}$")
fig.savefig("FigB4_map_change.png", dpi=250, bbox_inches="tight"); fig.savefig("FigB4_map_change.pdf", bbox_inches="tight"); plt.close(fig)
print("saved FigB1-B4; airports 2023 mapped:", len(gp), "of", (a.Year == Y1).sum(), "| countries in map:", w.lng.notna().sum(), "| change map:", w2.dlng.notna().sum())
