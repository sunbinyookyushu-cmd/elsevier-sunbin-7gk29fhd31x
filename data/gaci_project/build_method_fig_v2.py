# -*- coding: utf-8 -*-
"""
GACI construction figure, two panels:
  (a) toy network schematic (redrawn, adapted from Cheung et al. 2020 Fig. 1)
  (b) year-by-year PC1 loadings + variance explained, 1996-2024
Output: GACI_method_construction.png / .pdf  (300 dpi)
Panel (b) numbers must match main tex Setup section
(loadings ~ 0.49/0.43/0.39/0.43/0.48, VE 63-77%, pooled 74%).
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.linewidth": 0.8,
})

# ---------------------------------------------------------------- panel (b) data
df = pd.read_csv("GACI1996_2024_new_panel_data.csv")
IND = ["Degree", "NorBetweenness", "NorClose", "Eigen", "RegionalImportance"]
LAB = ["Degree", "Flow betweenness", "Closeness", "Eigenvector", "Regional importance"]

years = sorted(df["Year"].unique())
loads = {k: [] for k in IND}
ve = []
for y in years:
    X = df.loc[df["Year"] == y, IND].to_numpy(dtype=float)
    Z = (X - X.mean(0)) / X.std(0)
    C = np.corrcoef(Z, rowvar=False)
    w, V = np.linalg.eigh(C)
    pc1 = V[:, -1]
    if pc1.sum() < 0:
        pc1 = -pc1
    for k, v in zip(IND, pc1):
        loads[k].append(v)
    ve.append(w[-1] / w.sum())

mean_loads = {k: np.mean(v) for k, v in loads.items()}
sd_loads = {k: np.std(v) for k, v in loads.items()}
print("mean loadings:", {k: round(v, 3) for k, v in mean_loads.items()})
print("sd loadings  :", {k: round(v, 3) for k, v in sd_loads.items()})
print("VE range     :", round(min(ve), 3), "-", round(max(ve), 3))

# ---------------------------------------------------------------- figure
fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.2, 5.2),
                               gridspec_kw={"width_ratios": [1.0, 1.15]})

# ================= (a) toy network schematic =================
axA.set_xlim(0, 10)
axA.set_ylim(0, 7)
axA.set_aspect("equal")
axA.axis("off")

NAVY = "#1f3d63"
HUB = "#a41f2f"
LINK = "#9db8d2"

nodes = {
    "LHR": (1.0, 5.9), "FRA": (2.6, 4.9), "HKG": (5.0, 3.5),
    "SIN": (6.7, 2.5), "SYD": (8.2, 1.6), "PER": (9.4, 3.4),
    "DXB": (4.4, 6.2),
}
# direct links: (from, to, seat-capacity weight -> line width)
links = [("LHR", "FRA", 3.0), ("FRA", "HKG", 5.0), ("DXB", "HKG", 3.5),
         ("HKG", "SIN", 5.5), ("SIN", "SYD", 3.0), ("SYD", "PER", 2.0),
         ("HKG", "PER", 2.5)]
for a, b, w in links:
    xa, ya = nodes[a]
    xb, yb = nodes[b]
    axA.plot([xa, xb], [ya, yb], color=LINK, lw=w, zorder=1,
             solid_capstyle="round")

# through-flow (dashed) paths converging on the hub
for (x0, y0), rad in [((0.4, 3.2), 0.25), ((1.4, 1.0), -0.2), ((2.8, 0.6), -0.15)]:
    axA.add_patch(FancyArrowPatch((x0, y0), nodes["HKG"],
                                  connectionstyle=f"arc3,rad={rad}",
                                  arrowstyle="-|>", mutation_scale=11,
                                  color=NAVY, lw=1.1, linestyle=(0, (4, 3)),
                                  zorder=2))
for (x1, y1), rad in [((9.1, 5.9), 0.2), ((9.6, 4.9), -0.1)]:
    axA.add_patch(FancyArrowPatch(nodes["HKG"], (x1, y1),
                                  connectionstyle=f"arc3,rad={rad}",
                                  arrowstyle="-|>", mutation_scale=11,
                                  color=NAVY, lw=1.1, linestyle=(0, (4, 3)),
                                  zorder=2))

for name, (x, y) in nodes.items():
    hub = name == "HKG"
    axA.add_patch(Circle((x, y), 0.34 if hub else 0.26,
                         facecolor=HUB if hub else NAVY,
                         edgecolor="white", lw=1.2, zorder=3))
    dy = 0.62 if name in ("HKG", "SYD", "SIN") else -0.62
    axA.text(x, y - dy, name, ha="center",
             va="center", fontsize=10.5, color="#222222", zorder=4)

axA.text(3.55, 4.35, r"$w_{ij}$", fontsize=11, color="#43608a", style="italic")
axA.text(5.0, -0.75,
         "Nodes: airports.  Edge width: link intensity $w_{ij}$ (seat capacity).\n"
         "Dashed: indirect flows routed through the hub (flow betweenness).",
         ha="center", va="top", fontsize=9.5, color="#444444", clip_on=False)
axA.set_title("(a) Airport network and link intensities", fontsize=12)

# ================= (b) yearly PC1 loadings =================
# fixed categorical order, adjacency chosen to keep CVD-safe neighbours
COL = {"Degree": "#0072B2", "Flow betweenness": "#E69F00",
       "Closeness": "#009E73", "Eigenvector": "#56B4E9",
       "Regional importance": "#CC79A7"}

for k, lab in zip(IND, LAB):
    axB.plot(years, loads[k], color=COL[lab], lw=2.0, zorder=3,
             label=lab)

axB.plot(years, ve, color="#8a8a8a", lw=1.6, ls=(0, (5, 3)), zorder=2,
         label="Share of variance explained by PC1")
axB.legend(loc="center left", bbox_to_anchor=(0.02, 0.52), frameon=False,
           fontsize=9.5, handlelength=2.2, labelspacing=0.45)

axB.set_xlim(1996, 2024)
axB.set_ylim(0.30, 0.85)
axB.set_xlabel("Year")
axB.set_ylabel("First-principal-component loading / variance share")
axB.spines[["top", "right"]].set_visible(False)
axB.grid(axis="y", color="#e6e6e6", lw=0.6, zorder=0)
axB.set_title("(b) Year-by-year PCA weights, 1996–2024", fontsize=12)

plt.subplots_adjust(left=0.02, right=0.98, wspace=0.10, bottom=0.12, top=0.92)
fig.savefig("GACI_method_construction.png", dpi=300, bbox_inches="tight")
fig.savefig("GACI_method_construction.pdf", bbox_inches="tight")
print("saved GACI_method_construction.png / .pdf")
