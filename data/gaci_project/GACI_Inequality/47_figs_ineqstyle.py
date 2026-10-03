# -*- coding: utf-8 -*-
"""47_figs_ineqstyle.py : paper figures in the inequality paper's own style (_ineqstyle.py).
   Fig1_incidence.png     a) elasticity of group income, b) of group share (2SLS; filled = p<0.10)
   Fig2_heterogeneity.png a) baseline connectivity tercile, b) baseline GDP tercile, c) region, d) era  (ln market Gini, 2SLS)
   Fig3_attribution.png   a) top/bottom countries by implied Gini change (bars), b) map of implied Gini change, c) map of implied bottom-50 share change
   Fig4_descriptive.png   a) growth by group for low/middle/high connectivity-growth terciles, b) high-minus-low difference
   Inputs: _gic_dose_results.csv, _gic_bysample_results.csv, _hetero_co2form_results.csv, _aggregate_curve_bycountry.csv, _gic_descriptive.csv"""
import os, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, FuncNorm, Normalize
import _ineqstyle as lz
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D); lz.setup()
RD = dict(keep_default_na=False, na_values=["", "."])
gic = pd.read_csv("_gic_dose_results.csv", **RD); stg = pd.read_csv("_gic_bysample_results.csv", **RD); het = pd.read_csv("_hetero_co2form_results.csv", **RD)
agg = pd.read_csv("_aggregate_curve_bycountry.csv"); des = pd.read_csv("_gic_descriptive.csv", **RD)
G = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "t1", "t01"]
LAB = ["p0–10", "p10–20", "p20–30", "p30–40", "p40–50", "p50–60", "p60–70", "p70–80", "p80–90", "p90–100", "Top 1%", "Top 0.1%"]
def pull(block, prefix, spec="IV"):
    x = gic[(gic.block == block) & (gic.spec == spec)].set_index("outcome").reindex([prefix + g for g in G]); return x.b.values, x.se.values, x.p.values

# ================= Figure 1: incidence =================
fig, axes = plt.subplots(1, 2, figsize=(15, 6.2)); xs = np.arange(len(G))
for ax, (block, prefix, title, ylab, letter) in zip(axes, [("gic", "ln_apt_", "Income of the group", "Elasticity to ln GACI", "a"), ("gic_share", "ln_spt_", "Income share of the group", "Elasticity to ln GACI", "b")]):
    b, se, p = pull(block, prefix); lz.zero_line(ax)
    if letter == "a":
        m = gic[(gic.block == "gic") & (gic.spec == "IV") & (gic.outcome == "ln_apt_all")].b.iloc[0]
        ax.axhline(m, color=lz.AMBER, lw=1.4, ls=(0, (4, 3)), zorder=1); ax.text(0.99, 0.965, "dashed: mean income, %.2f" % m, transform=ax.transAxes, color=lz.AMBER, ha="right", va="top", fontsize=11.5)
    lz.coef_points(ax, xs, b, se, p, labels=True, label_fmt="%.2f")
    ax.set_xticks(xs); ax.set_xticklabels(LAB, rotation=45, ha="right"); ax.set_ylabel(ylab); ax.axvline(9.5, color="#c9ced4", lw=0.9, ls=":", zorder=1); ax.set_title(title, loc="left")
    lz.panel_letter(ax, letter, x=-0.075, y=1.03)
axes[0].set_ylim(-4.5, 5.5); axes[1].set_ylim(-5.5, 2.5)
fig.tight_layout(w_pad=3); fig.savefig("Fig1_incidence_v2.png", dpi=300, bbox_inches="tight"); fig.savefig("Fig1_incidence_v2.pdf", bbox_inches="tight"); plt.close(fig)

# ================= Figure 2: heterogeneity dot plots =================
def hrow(ax, items, title, letter, xlim=(-1.5, 2.5)):
    ys = np.arange(len(items))[::-1]; b = [i[1] for i in items]; se = [i[2] for i in items]; p = [i[3] for i in items]
    lz.zero_line(ax, "h"); lz.coef_points(ax, ys, b, se, p, orient="h", label_fmt="%.2f", label_offset=10)
    ax.set_yticks(ys); ax.set_yticklabels([i[0] for i in items]); ax.set_xlim(*xlim); ax.set_ylim(-0.7, len(items) - 0.3); ax.set_xlabel("Elasticity of market Gini to ln GACI"); lz.panel_letter(ax, letter, x=-0.42, y=1.03); ax.set_title(title, loc="left")
def g_st(s, o="ln_gini_mkt"):
    x = stg[(stg["sample"] == s) & (stg.outcome == o)].iloc[0]; return x.b, x.se, x.p, x.kpf
def g_het(pan, grp, o="ln_gini_mkt"):
    x = het[(het.panel == pan) & (het.group == grp) & (het.outcome == o)].iloc[0]; return x.b, x.se, x.p, x.kpf
fig, axes = plt.subplots(1, 4, figsize=(20, 5.4))
con = [("Low", *g_st("con_low")[:3]), ("Middle", *g_st("con_mid")[:3]), ("High", *g_st("con_high")[:3])]
gdp = [("Low", *g_st("inc_low")[:3]), ("Middle", *g_st("inc_mid")[:3]), ("High", *g_st("inc_high")[:3])]
reg = [("Europe", *g_het("E_region", "Europe")[:3]), ("Asia-Pacific", *g_het("E_region", "Asia")[:3]), ("Africa", *g_het("E_region", "Africa")[:3]), ("Latin America", *g_het("E_region", "LatAm")[:3])]
era = [("1996–2007", *g_st("era_1996_2007")[:3]), ("2010–2023", *g_st("era_2010_2023x")[:3]), ("Full sample", *g_st("full")[:3])]
hrow(axes[0], con, "Baseline connectivity", "a", (-1.5, 3.5)); hrow(axes[1], gdp, "Baseline GDP per capita", "b", (-1.5, 3.5)); hrow(axes[2], reg, "Region", "c", (-1.5, 3.5)); hrow(axes[3], era, "Period", "d", (-1.5, 3.5))
for ax, note in zip(axes, [f"KP F: {g_st('con_low')[3]:.0f} / {g_st('con_mid')[3]:.0f} / {g_st('con_high')[3]:.1f}", f"KP F: {g_st('inc_low')[3]:.1f} / {g_st('inc_mid')[3]:.1f} / {g_st('inc_high')[3]:.0f}", f"KP F: {g_het('E_region','Europe')[3]:.0f} / {g_het('E_region','Asia')[3]:.0f} / {g_het('E_region','Africa')[3]:.0f} / {g_het('E_region','LatAm')[3]:.1f}", f"KP F: {g_st('era_1996_2007')[3]:.0f} / {g_st('era_2010_2023x')[3]:.0f} / {g_st('full')[3]:.0f}"]):
    ax.text(0.98, 0.03, note, transform=ax.transAxes, ha="right", va="bottom", fontsize=10.5, color=lz.SLATE)
fig.tight_layout(w_pad=2.5); fig.savefig("Fig2_heterogeneity_v2.png", dpi=300, bbox_inches="tight"); fig.savefig("Fig2_heterogeneity_v2.pdf", bbox_inches="tight"); plt.close(fig)

# ================= Figure 3: attribution (bars + maps) =================
a = agg.copy(); a["gini_pts"] = a["implied_dgini_pts"]; a["b50_pts"] = a["implied_dshare_pts_b50"]
NAMES = {"CHN": "China", "SYR": "Syria", "GUM": "Guam", "MAC": "Macao", "PRI": "Puerto Rico", "BHS": "Bahamas", "BRB": "Barbados", "MDV": "Maldives", "SYC": "Seychelles", "CPV": "Cabo Verde", "TLS": "Timor-Leste", "BTN": "Bhutan", "TJK": "Tajikistan", "TKM": "Turkmenistan", "MDA": "Moldova", "XKX": "Kosovo", "GIN": "Guinea", "MLI": "Mali", "BFA": "Burkina Faso", "NER": "Niger", "TCD": "Chad", "BEN": "Benin", "TGO": "Togo", "SLE": "Sierra Leone", "LBR": "Liberia", "GMB": "Gambia", "GNB": "Guinea-Bissau", "MRT": "Mauritania", "COD": "DR Congo", "COG": "Congo", "GAB": "Gabon", "GNQ": "Eq. Guinea", "CAF": "Central African Rep.", "BDI": "Burundi", "ETH": "Ethiopia", "ERI": "Eritrea", "DJI": "Djibouti", "SOM": "Somalia", "LSO": "Lesotho", "SWZ": "Eswatini", "COM": "Comoros", "HTI": "Haiti", "CUB": "Cuba", "BLZ": "Belize", "GUY": "Guyana", "SUR": "Suriname", "AFG": "Afghanistan", "YEM": "Yemen", "WSM": "Samoa", "TON": "Tonga", "VUT": "Vanuatu", "SLB": "Solomon Is.", "KIR": "Kiribati", "FSM": "Micronesia", "MHL": "Marshall Is.", "PLW": "Palau", "NRU": "Nauru", "MNP": "N. Mariana Is.", "ASM": "American Samoa", "PYF": "French Polynesia", "NCL": "New Caledonia", "GRL": "Greenland", "FRO": "Faroe Is.", "BMU": "Bermuda", "CYM": "Cayman Is.", "ABW": "Aruba", "CUW": "Curaçao", "ATG": "Antigua and Barbuda", "LCA": "St Lucia", "VCT": "St Vincent", "GRD": "Grenada", "DMA": "Dominica", "KNA": "St Kitts and Nevis", "MNG": "Mongolia", "PRK": "North Korea", "IND": "India", "TUR": "Turkey", "KOR": "Korea", "VNM": "Vietnam", "POL": "Poland", "ESP": "Spain", "PRT": "Portugal", "NOR": "Norway", "IRL": "Ireland", "ISL": "Iceland", "EGY": "Egypt", "MAR": "Morocco", "ETH": "Ethiopia", "COL": "Colombia", "PER": "Peru", "RUS": "Russia", "AUS": "Australia", "USA": "United States", "VEN": "Venezuela", "ZWE": "Zimbabwe", "JPN": "Japan", "DEU": "Germany", "GBR": "United Kingdom", "IDN": "Indonesia", "MEX": "Mexico", "BRA": "Brazil", "THA": "Thailand", "ARE": "United Arab Emirates", "QAT": "Qatar", "SGP": "Singapore", "MYS": "Malaysia", "PHL": "Philippines", "KAZ": "Kazakhstan", "ROU": "Romania", "HUN": "Hungary", "CZE": "Czechia", "GRC": "Greece", "ITA": "Italy", "FRA": "France", "NLD": "Netherlands", "CAN": "Canada", "NZL": "New Zealand", "ZAF": "South Africa", "NGA": "Nigeria", "KEN": "Kenya", "TZA": "Tanzania", "PAK": "Pakistan", "BGD": "Bangladesh", "LKA": "Sri Lanka", "GEO": "Georgia", "ARM": "Armenia", "ALB": "Albania", "MKD": "North Macedonia", "SRB": "Serbia", "BGR": "Bulgaria", "UKR": "Ukraine", "BLR": "Belarus", "LTU": "Lithuania", "LVA": "Latvia", "EST": "Estonia", "SVK": "Slovakia", "SVN": "Slovenia", "HRV": "Croatia", "BIH": "Bosnia and Herz.", "MNE": "Montenegro", "CHL": "Chile", "ARG": "Argentina", "URY": "Uruguay", "PRY": "Paraguay", "BOL": "Bolivia", "ECU": "Ecuador", "GTM": "Guatemala", "HND": "Honduras", "NIC": "Nicaragua", "SLV": "El Salvador", "DOM": "Dominican Rep.", "JAM": "Jamaica", "TTO": "Trinidad and Tobago", "PAN": "Panama", "CRI": "Costa Rica", "SAU": "Saudi Arabia", "OMN": "Oman", "KWT": "Kuwait", "BHR": "Bahrain", "JOR": "Jordan", "LBN": "Lebanon", "ISR": "Israel", "IRN": "Iran", "IRQ": "Iraq", "AZE": "Azerbaijan", "UZB": "Uzbekistan", "KGZ": "Kyrgyzstan", "MNG": "Mongolia", "NPL": "Nepal", "KHM": "Cambodia", "LAO": "Laos", "MMR": "Myanmar", "PNG": "Papua New Guinea", "FJI": "Fiji", "MUS": "Mauritius", "MDG": "Madagascar", "MOZ": "Mozambique", "ZMB": "Zambia", "MWI": "Malawi", "UGA": "Uganda", "RWA": "Rwanda", "GHA": "Ghana", "CIV": "Côte d'Ivoire", "SEN": "Senegal", "CMR": "Cameroon", "AGO": "Angola", "NAM": "Namibia", "BWA": "Botswana", "TUN": "Tunisia", "DZA": "Algeria", "LBY": "Libya", "SDN": "Sudan", "SWE": "Sweden", "FIN": "Finland", "DNK": "Denmark", "AUT": "Austria", "CHE": "Switzerland", "BEL": "Belgium", "LUX": "Luxembourg", "CYP": "Cyprus", "MLT": "Malta", "HKG": "Hong Kong", "TWN": "Taiwan"}
top = a.sort_values("gini_pts", ascending=False); show = pd.concat([top.head(12), top.tail(6)])
fig = plt.figure(figsize=(20, 11)); gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.5], height_ratios=[1, 1], hspace=0.16, wspace=0.05)
ax = fig.add_subplot(gs[:, 0]); ys = np.arange(len(show))[::-1]
for y, (_, r) in zip(ys, show.iterrows()):
    lz.lollipop(ax, y, r.gini_pts)
ax.set_yticks(ys); ax.set_yticklabels([NAMES.get(c, c) for c in show.c]); ax.set_xlim(min(-8, show.gini_pts.min() - 3), show.gini_pts.max() + 5); ax.set_ylim(-0.8, len(show) - 0.2)
ax.axvline(0, color="#666666", lw=1); ax.set_xlabel("Implied change in market Gini, 1996–2023 (points)"); ax.grid(axis="y", visible=False); lz.panel_letter(ax, "a", x=-0.26, y=1.02)
w = lz.world_map(a[["c", "gini_pts", "b50_pts"]])
ax2 = fig.add_subplot(gs[0, 1]); lo, hi = float(np.nanpercentile(a.gini_pts, 3)), float(np.nanpercentile(a.gini_pts, 97))
lz.draw_map(ax2, w, "gini_pts", lz.mono_cmap(lz.TEAL), Normalize(vmin=lo, vmax=hi), title="Implied change in market Gini, 1996–2023 (points)", fig=fig, cbar_ticks=[t for t in [-5, 0, 5, 10, 15] if lo <= t <= hi]); lz.panel_letter(ax2, "b", x=-0.04, y=1.0)
ax3 = fig.add_subplot(gs[1, 1]); lo2, hi2 = float(np.nanpercentile(a.b50_pts, 3)), float(np.nanpercentile(a.b50_pts, 97))
# bottom-50 share: losses are the story, so darker = larger loss (reverse the scale)
lz.draw_map(ax3, w, "b50_pts", lz.mono_cmap(lz.AMBER).reversed(), Normalize(vmin=lo2, vmax=hi2), title="Implied change in bottom-50% income share, 1996–2023 (points of national income)", fig=fig, cbar_ticks=[t for t in [-6, -4, -2, 0, 2] if lo2 <= t <= hi2]); lz.panel_letter(ax3, "c", x=-0.04, y=1.0)
fig.savefig("Fig3_attribution_v2.png", dpi=250, bbox_inches="tight"); fig.savefig("Fig3_attribution_v2.pdf", bbox_inches="tight"); plt.close(fig)

# ================= Figure 4: descriptive growth =================
fig, axes = plt.subplots(1, 2, figsize=(15, 6)); xs = np.arange(len(des))
ax = axes[0]
for col, lab, c, mk in [("low_mean", "Low connectivity growth", lz.AMBER, "s"), ("mid_mean", "Middle", lz.SLATE, "^"), ("high_mean", "High connectivity growth", lz.TEAL, "D")]:
    ax.plot(xs, des[col], color=c, lw=2.2, marker=mk, ms=7, label=lab, zorder=3)
    ax.annotate(lab, (xs[-1], des[col].iloc[-1]), xytext=(8, 0), textcoords="offset points", ha="left", va="center", fontsize=11.5, color=c)
ax.set_xlim(-0.5, len(des) + 3.2); ax.set_xticks(xs); ax.set_xticklabels(des.label, rotation=45, ha="right"); ax.set_ylabel("Real income growth, % per year"); ax.axvline(9.5, color="#c9ced4", lw=0.9, ls=":"); ax.set_title("Growth by income group, 1996–2023", loc="left"); lz.panel_letter(ax, "a", x=-0.075, y=1.03)
ax = axes[1]; lz.zero_line(ax); lz.coef_points(ax, xs, des.diff_high_low.values, des.se_diff.values, 2 * (1 - __import__("scipy").stats.norm.cdf(np.abs(des.diff_high_low.values / des.se_diff.values))), labels=False)
ax.set_xticks(xs); ax.set_xticklabels(des.label, rotation=45, ha="right"); ax.set_ylabel("High minus low, pp per year"); ax.set_title("High minus low tercile", loc="left"); ax.axvline(9.5, color="#c9ced4", lw=0.9, ls=":"); lz.panel_letter(ax, "b", x=-0.075, y=1.03)
fig.tight_layout(w_pad=3); fig.savefig("Fig4_descriptive_v2.png", dpi=300, bbox_inches="tight"); fig.savefig("Fig4_descriptive_v2.pdf", bbox_inches="tight"); plt.close(fig)
print("saved Fig1-4")
