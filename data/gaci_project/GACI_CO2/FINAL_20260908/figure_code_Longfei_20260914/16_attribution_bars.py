# -*- coding: utf-8 -*-
# NOTE (package copy, 11 Sep 2026): only the path lines were changed so the
# script finds its inputs in this flat folder. The figure code is untouched.
"""Bar chart of country-level CO2 attributed to 1996-2023 connectivity
growth (_attribution_scc.csv, Feyrer betas), with the social cost at the
EPA SCC ($190/t) annotated on each bar. Top 12 positive + all negatives
below -1 Mt. Times New Roman, map-palette colours (RdBu)."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"],
                     "mathtext.fontset": "stix"})

NAMES = {"CHN": "China", "USA": "United States", "ARE": "United Arab Emirates",
         "JPN": "Japan", "TUR": "Turkey", "IND": "India", "KOR": "Korea",
         "CAN": "Canada", "QAT": "Qatar", "ESP": "Spain", "SAU": "Saudi Arabia",
         "SGP": "Singapore", "BEL": "Belgium", "ITA": "Italy", "DEU": "Germany",
         "RUS": "Russia", "GUM": "Guam", "PAK": "Pakistan"}

d = pd.read_csv(os.path.join(HERE, "_attribution_scc.csv"))
d["mt"] = d.att_tot_t / 1e6
d["bn"] = d.att_tot_t * 190 / 1e9
top = d.nlargest(12, "mt")
neg = d[d.mt < -1].sort_values("mt", ascending=False)
sel = pd.concat([top, neg])
sel["name"] = sel.c.map(NAMES).fillna(sel.c)
sel = sel.iloc[::-1]  # largest at top after barh

POS, NEG = "#b2182b", "#2166ac"   # RdBu endpoints (match the maps)
fig, ax = plt.subplots(figsize=(9.5, 7.2))
bars = ax.barh(sel.name, sel.mt,
               color=[POS if v > 0 else NEG for v in sel.mt],
               edgecolor="white", linewidth=0.6, height=0.72)
ax.axvline(0, color="#1f1f1f", linewidth=0.8)

for b, mt, bn in zip(bars, sel.mt, sel.bn):
    lab = f"{mt:,.1f} Mt ({bn:+,.1f} bn USD/yr)"
    if mt > 0:
        ax.text(mt + 1.5, b.get_y() + b.get_height() / 2, lab,
                va="center", ha="left", fontsize=11.5, color="#1f1f1f")
    else:
        ax.text(mt - 1.5, b.get_y() + b.get_height() / 2, lab,
                va="center", ha="right", fontsize=11.5, color="#1f1f1f")

ax.set_xlim(-62, 130)
ax.set_xlabel("Aviation CO$_2$ attributed to 1996$-$2023 connectivity growth (Mt, 2023)",
              fontsize=13.5)
ax.tick_params(axis="y", labelsize=12.5, length=0)
ax.tick_params(axis="x", labelsize=11.5)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color("#b3b8bd")
ax.set_axisbelow(True)
ax.grid(axis="x", color="#e6e6e6", linewidth=0.7)
ax.text(0.985, 0.03,
        "Values in parentheses: social cost at the US EPA SCC of 190 USD/t\n"
        "World total: 356.4 Mt = 42.5% of 2023 aviation CO$_2$ (67.7 bn USD/yr)",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=11,
        color="#4d4d4d")
plt.tight_layout()
out = os.path.join(HERE, "CO2_attribution_bars.png")
plt.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
print("wrote", out, "| bars:", len(sel))
