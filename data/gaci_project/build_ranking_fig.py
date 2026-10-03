# -*- coding: utf-8 -*-
"""
GACI rankings figure, two panels (2023, the last estimation year):
  (a) top-15 airports by airport-level GACI
  (b) top-15 countries by hub quality GACI_cwm
Output: GACI_rankings_2023.png / .pdf (300 dpi)
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.linewidth": 0.8,
})

YEAR = 2023
NAVY = "#1f3d63"
N = 15

# ---------------- (a) airports
ap = pd.read_csv("GACI1996_2024_new_panel_data.csv")
top_ap = (ap[ap["Year"] == YEAR]
          .nlargest(N, "GACI")[["Airport", "GACI"]]
          .iloc[::-1])
r96 = (ap[ap["Year"] == 1996]
       .sort_values("GACI", ascending=False)
       .reset_index()["Airport"])
rank96 = {a: i + 1 for i, a in enumerate(r96)}

# ---------------- (b) countries
co = pd.read_csv("gaci_panel_tourism_ext.csv")
top_co = (co[co["y"] == YEAR]
          .nlargest(N, "gaci_cwmean")[["c", "gaci_cwmean"]]
          .iloc[::-1])
NAME = {"USA": "United States", "CHN": "China", "ARE": "United Arab Emirates",
        "GBR": "United Kingdom", "DEU": "Germany", "FRA": "France",
        "JPN": "Japan", "KOR": "South Korea", "SGP": "Singapore",
        "NLD": "Netherlands", "ESP": "Spain", "TUR": "Turkey",
        "QAT": "Qatar", "HKG": "Hong Kong SAR", "ITA": "Italy",
        "IND": "India", "CAN": "Canada", "THA": "Thailand",
        "AUS": "Australia", "MEX": "Mexico", "IDN": "Indonesia",
        "RUS": "Russia", "BRA": "Brazil", "CHE": "Switzerland",
        "MAC": "Macao SAR", "TWN": "Taiwan", "IRL": "Ireland",
        "ETH": "Ethiopia", "PAN": "Panama", "MYS": "Malaysia",
        "SAU": "Saudi Arabia", "EGY": "Egypt", "GRC": "Greece",
        "PRT": "Portugal", "AUT": "Austria", "BEL": "Belgium",
        "DNK": "Denmark", "NOR": "Norway", "SWE": "Sweden",
        "FIN": "Finland", "NZL": "New Zealand", "PHL": "Philippines",
        "VNM": "Vietnam", "ZAF": "South Africa", "MAR": "Morocco",
        "KEN": "Kenya", "COL": "Colombia", "CHL": "Chile",
        "ARG": "Argentina", "PER": "Peru", "DOM": "Dominican Republic",
        "CUB": "Cuba", "JAM": "Jamaica", "ISL": "Iceland",
        "LUX": "Luxembourg", "MDV": "Maldives", "MUS": "Mauritius",
        "FJI": "Fiji", "BHR": "Bahrain", "KWT": "Kuwait", "OMN": "Oman",
        "JOR": "Jordan", "LBN": "Lebanon", "ISR": "Israel", "CZE": "Czechia",
        "POL": "Poland", "HUN": "Hungary", "ROU": "Romania"}
print("country top-15:", top_co["c"].tolist())
missing = [c for c in top_co["c"] if c not in NAME]
if missing:
    print("!! missing names:", missing)

fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.6, 5.4))

for ax, data, labels, title, xlab in [
    (axA, top_ap["GACI"], top_ap["Airport"],
     f"(a) Top {N} airports, {YEAR}", "Airport-level GACI"),
    (axB, top_co["gaci_cwmean"], [NAME.get(c, c) for c in top_co["c"]],
     f"(b) Top {N} countries, {YEAR}",
     "Hub quality, $\\mathrm{GACI}_{cwm}$"),
]:
    bars = ax.barh(range(len(data)), data, height=0.62, color=NAVY, zorder=3)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(labels, fontsize=10)
    for i, v in enumerate(data):
        ax.text(v + max(data) * 0.012, i, f"{v:.2f}", va="center",
                fontsize=9, color="#444444", zorder=4)
    ax.set_xlim(0, max(data) * 1.12)
    ax.set_xlabel(xlab)
    ax.set_title(title, fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#e6e6e6", lw=0.6, zorder=0)
    ax.tick_params(axis="y", length=0)

# 1996 rank annotation for airports (grey, inside bar right end)
for i, (a, v) in enumerate(zip(top_ap["Airport"], top_ap["GACI"])):
    r = rank96.get(a)
    txt = f"'96: #{r}" if r and r <= 200 else "'96: n/a"
    axA.text(v - 0.03, i, txt, va="center", ha="right",
             fontsize=8, color="#dce4ee", zorder=5)

plt.subplots_adjust(left=0.07, right=0.985, wspace=0.42, bottom=0.11, top=0.93)
fig.savefig("GACI_rankings_2023.png", dpi=300, bbox_inches="tight")
fig.savefig("GACI_rankings_2023.pdf", bbox_inches="tight")
print("saved GACI_rankings_2023.png / .pdf")
print(top_ap.iloc[::-1].to_string(index=False))
