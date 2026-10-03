# -*- coding: utf-8 -*-
"""
GACI ranking bump chart, two panels:
  (a) airport GACI rank trajectories, top 15 in 2023 traced back to 1996
  (b) country hub-quality (capacity-weighted mean GACI) rank trajectories,
      top 15 in 2023 -- computed from the FULL airport network
      (all countries with scheduled service, not the estimation sample)
Risers (outside top 30 in 1996, or absent) highlighted in vermillion.
Output: GACI_rank_bump.png / .pdf (300 dpi)
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.linewidth": 0.8,
})

YEARS = [1996, 2000, 2005, 2010, 2015, 2020, 2023]
TOPN = 15
SHOW = 20          # visible rank range
BAND = SHOW + 3.2  # off-scale band position for ranks > SHOW
GREY = "#a9bccf"
DARK = "#1f3d63"
ACC = "#D55E00"

ISO2NAME = {"AE": "UAE", "NL": "Netherlands", "SG": "Singapore",
            "HK": "Hong Kong", "DE": "Germany", "US": "United States",
            "TR": "Turkey", "FR": "France", "GB": "United Kingdom",
            "CH": "Switzerland", "SA": "Saudi Arabia", "IL": "Israel",
            "ET": "Ethiopia", "AT": "Austria", "IE": "Ireland",
            "QA": "Qatar", "JP": "Japan", "KR": "South Korea",
            "ES": "Spain", "IT": "Italy", "CA": "Canada", "CN": "China",
            "BE": "Belgium", "DK": "Denmark", "FI": "Finland",
            "IS": "Iceland", "LU": "Luxembourg", "PA": "Panama",
            "NZ": "New Zealand", "PT": "Portugal", "GR": "Greece",
            "TH": "Thailand", "MY": "Malaysia", "AU": "Australia",
            "KE": "Kenya", "MU": "Mauritius", "MV": "Maldives",
            "BH": "Bahrain", "KW": "Kuwait", "OM": "Oman", "JO": "Jordan",
            "TW": "Taiwan", "MO": "Macao", "CY": "Cyprus", "MT": "Malta",
            "NO": "Norway", "SE": "Sweden", "CZ": "Czechia", "PL": "Poland",
            "HU": "Hungary", "RU": "Russia", "IN": "India", "BR": "Brazil",
            "MX": "Mexico", "ZA": "South Africa", "EG": "Egypt",
            "MA": "Morocco", "LK": "Sri Lanka", "VN": "Vietnam",
            "PH": "Philippines", "ID": "Indonesia", "CO": "Colombia",
            "CL": "Chile", "PE": "Peru", "AR": "Argentina"}


def ranks_by_year(df, ycol, idcol, vcol):
    out = {}
    for y in YEARS:
        s = df[df[ycol] == y].sort_values(vcol, ascending=False)[idcol]
        out[y] = {a: i + 1 for i, a in enumerate(s)}
    return out


def draw(ax, rk, title, labfun):
    top23 = sorted(rk[2023], key=rk[2023].get)[:TOPN]
    for ent in top23:
        r23 = rk[2023][ent]
        r96 = rk[1996].get(ent)
        riser = (r96 is None) or (r96 > SHOW)
        xs, ys = [], []
        for y in YEARS:
            r = rk[y].get(ent)
            if r is None:
                continue
            xs.append(y)
            ys.append(r if r <= SHOW else BAND)
        col = ACC if riser else (DARK if r23 <= 5 else GREY)
        lw = 2.4 if riser else (2.0 if r23 <= 5 else 1.5)
        z = 4 if riser else (3 if r23 <= 5 else 2)
        ax.plot(xs, ys, color=col, lw=lw, zorder=z,
                marker="o", ms=4.5, mec="white", mew=0.8,
                solid_capstyle="round")
        note = ""
        if riser:
            note = f"  (#{r96} in '96)" if r96 is not None else "  (n/a in '96)"
        ax.text(2023.6, ys[-1], labfun(ent) + note, va="center",
                fontsize=9.3, color=ACC if riser else "#333333",
                clip_on=False)

    ax.set_ylim(BAND + 1.2, 0.2)
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xticks(YEARS)
    ax.set_xticklabels([f"'{str(y)[2:]}" for y in YEARS])
    ax.set_xlim(1995.6, 2023.8)
    ax.axhspan(SHOW + 1.4, BAND + 1.2, color="#f4f4f2", zorder=0)
    ax.text(2023.4, BAND + 0.9, f"rank > {SHOW}", fontsize=8.5,
            color="#999999", va="center", ha="right", zorder=5)
    ax.set_ylabel("Rank")
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color="#ececec", lw=0.6, zorder=0)
    ax.set_title(title, fontsize=12, pad=10)


ap = pd.read_csv("GACI1996_2024_new_panel_data.csv")

# airport -> ISO2 from OurAirports (clean iso_country for IATA codes)
oa = pd.read_csv("ourairports.csv", usecols=["iata_code", "iso_country", "type"])
oa = oa.dropna(subset=["iata_code"])
pref = {"large_airport": 0, "medium_airport": 1, "small_airport": 2}
oa["p"] = oa["type"].map(pref).fillna(3)
oa = oa.sort_values("p").drop_duplicates("iata_code")
iso = dict(zip(oa["iata_code"], oa["iso_country"]))

ap["cty"] = ap["Airport"].map(iso)
matched = ap["cty"].notna().mean()
print(f"airport->ISO2 match: {matched:.1%}")

grp = (ap.dropna(subset=["cty"])
         .assign(wG=lambda d: d["TotalCapacity"] * d["GACI"])
         .groupby(["Year", "cty"], as_index=False)
         .agg(wG=("wG", "sum"), cap=("TotalCapacity", "sum")))
grp["cwm"] = grp["wG"] / grp["cap"]

rk_ap = ranks_by_year(ap, "Year", "Airport", "GACI")
rk_co = ranks_by_year(grp, "Year", "cty", "cwm")

top15_iso = sorted(rk_co[2023], key=rk_co[2023].get)[:TOPN]
print("country top-15 (full network):", [ISO2NAME.get(c, c) for c in top15_iso])
miss = [c for c in top15_iso if c not in ISO2NAME]
if miss:
    print("!! missing names:", miss)

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.6, 6.2))
draw(axA, rk_ap, "(a) Airport GACI rank, top 15 in 2023", lambda a: a)
draw(axB, rk_co,
     "(b) Country hub quality ($\\mathrm{GACI}_{cwm}$) rank, top 15 in 2023",
     lambda c: ISO2NAME.get(c, c))

plt.subplots_adjust(left=0.055, right=0.86, wspace=0.62, bottom=0.06, top=0.92)
fig.savefig("GACI_rank_bump.png", dpi=300, bbox_inches="tight")
fig.savefig("GACI_rank_bump.pdf", bbox_inches="tight")
print("saved GACI_rank_bump.png / .pdf")
