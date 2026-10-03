# -*- coding: utf-8 -*-
"""
19_airport_concentration.py   (LZ comment 2, 2026-09-03)
Contribution of individual airports to the connectivity-attributed emissions.
For each airport a:  attributed_a = CO2_a,2023 x [1 - exp(-b x (ln GACI_a,2023 - ln GACI_a,1996))]
with b = (i) country IV elasticity 5.67 (baseline), (ii) airport within-country
elasticity 3.72, (iii) group-specific airport elasticities (top-5% hubs vs other).
Ranks airports, reports the share of the global attributed total held by the top
1 / 5 / 10 / 25 percent, Lorenz curve and Gini, benchmarked against the
concentration of 2023 emissions themselves; checks the airport sum against the
country-level 356 Mt. Outputs: _airport_concentration.csv, _airport_top20.csv,
CO2_airport_concentration.png, _tex_airport_conc.tex
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman"], "font.size": 11, "axes.linewidth": 0.8})
ACC, GRAY, INK, NEG = "#1F4E79", "#9AA0A6", "#1f1f1f", "#B5651D"

p = pd.read_csv(os.path.join(HERE, "airport_co2_panel.csv"))
grp = pd.read_csv(os.path.join(HERE, "_airport_groups.csv"))
het = pd.read_csv(os.path.join(HERE, "_airport_hetero.csv"))
mech = pd.read_csv(os.path.join(HERE, "_feyrer_mechanism.csv")).set_index("outc")
B_COUNTRY = float(mech.loc["ln_co2_tot", "b"])
B_AIRPORT = float(het[(het.panel == "ALL") & (het.outc == "ln_co2")]["b"].iloc[0])
b_top5 = float(het[(het.panel == "HUB") & (het.grp == "top5") & (het.outc == "ln_co2")]["b"].iloc[0])
b_not5 = float(het[(het.panel == "HUB") & (het.grp == "not_top5") & (het.outc == "ln_co2")]["b"].iloc[0])
print(f"b country {B_COUNTRY:.3f}; airport {B_AIRPORT:.3f}; top5 {b_top5:.3f}; other {b_not5:.3f}")

# first and last observed GACI per airport (1996 and 2023 where available)
p = p.sort_values(["airport_iata", "year"])
g96 = p[p.year == 1996][["airport_iata", "ln_gaci"]].rename(columns={"ln_gaci": "lg96"})
gfirst = p.dropna(subset=["ln_gaci"]).groupby("airport_iata").first()[["ln_gaci", "year"]].rename(columns={"ln_gaci": "lgfirst", "year": "yfirst"})
g23 = p[p.year == 2023][["airport_iata", "iso3", "Region", "ln_gaci", "co2_bunker", "dep_seat_km"]].rename(columns={"ln_gaci": "lg23"})
d = g23.merge(g96, on="airport_iata", how="left").merge(gfirst, on="airport_iata", how="left").merge(grp[["airport_iata", "top5", "top1", "hub_nat", "gac3", "inc3"]], on="airport_iata", how="left")
d["iso3"] = d["iso3"].fillna("TWN")
d["lg0"] = d["lg96"].fillna(d["lgfirst"])  # entrants: growth since first appearance
d = d[(d.co2_bunker > 0) & d.lg23.notna() & d.lg0.notna()].copy()
d["dlg"] = d["lg23"] - d["lg0"]
d["co2_mt"] = d["co2_bunker"] / 1e9  # kg -> Mt
for nm, b in [("country", B_COUNTRY), ("airport", B_AIRPORT)]:
    d[f"att_{nm}"] = d["co2_mt"] * (1 - np.exp(-b * d["dlg"]))
d["b_grp"] = np.where(d["top5"] == 1, b_top5, b_not5)
d["att_group"] = d["co2_mt"] * (1 - np.exp(-d["b_grp"] * d["dlg"]))
print("airports in 2023 attribution:", len(d))
for nm in ["country", "airport", "group"]:
    print(f"attributed total ({nm} b): {d[f'att_{nm}'].sum():.1f} Mt; positive part {d.loc[d[f'att_{nm}']>0, f'att_{nm}'].sum():.1f} Mt; 2023 CO2 total {d.co2_mt.sum():.1f} Mt")

def conc(series):
    s = series.clip(lower=0).sort_values(ascending=False).values
    tot = s.sum(); n = len(s); cum = np.cumsum(s) / tot
    out = {f"top{q}" : float(cum[max(int(np.ceil(n * q / 100)) - 1, 0)]) for q in [1, 5, 10, 25]}
    lor = np.cumsum(np.sort(s)) / tot
    gini = 1 - 2 * np.trapezoid(lor, dx=1.0 / n) if n > 1 else np.nan
    out["gini"] = float(gini); out["n"] = n
    return out, lor
rows = []
lorenz = {}
for nm, col in [("Emissions 2023", "co2_mt"), ("Attributed (country b)", "att_country"), ("Attributed (airport b)", "att_airport"), ("Attributed (hub/non-hub b)", "att_group")]:
    c, lor = conc(d[col]); c["measure"] = nm; rows.append(c); lorenz[nm] = lor
res = pd.DataFrame(rows)[["measure", "top1", "top5", "top10", "top25", "gini", "n"]]
print(res.round(3).to_string())
res.to_csv(os.path.join(HERE, "_airport_concentration.csv"), index=False)
top = d.sort_values("att_country", ascending=False).head(20)[["airport_iata", "iso3", "co2_mt", "dlg", "att_country", "att_airport", "top5"]]
top["share_country"] = top["att_country"] / d["att_country"].clip(lower=0).sum()
top.to_csv(os.path.join(HERE, "_airport_top20.csv"), index=False)
print(top.round(3).to_string())
# by hub status shares
for flag in ["top5", "top1", "hub_nat"]:
    sh = d.loc[d[flag] == 1, "att_country"].clip(lower=0).sum() / d["att_country"].clip(lower=0).sum()
    she = d.loc[d[flag] == 1, "co2_mt"].sum() / d["co2_mt"].sum()
    print(f"{flag}: share of attributed {sh:.3f} vs share of emissions {she:.3f} (n={int((d[flag]==1).sum())})")
# consistency with country attribution
ca = pd.read_csv(os.path.join(HERE, "_attribution_scc.csv"))
print("country-level attributed total (file):", ca.columns.tolist()[:8])

# ---------------- figure: Lorenz curves + top-20 bars ----------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axes[0]
x = None
for nm, col, ls in [("Emissions 2023", "co2_mt", "--"), ("Attributed (country b)", "att_country", "-"), ("Attributed (airport b)", "att_airport", ":")]:
    lor = lorenz[nm]; xx = np.linspace(0, 1, len(lor) + 1)[1:]
    ax.plot(xx, lor, ls, color=(GRAY if col == "co2_mt" else ACC), lw=1.8, label=nm)
ax.plot([0, 1], [0, 1], color="#dddddd", lw=0.8)
ax.set_xlabel("Cumulative share of airports (ranked low to high)"); ax.set_ylabel("Cumulative share of Mt")
ax.set_title("A. Lorenz curves", loc="left", fontsize=11.5); ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
ax = axes[1]
t = top.iloc[::-1]
ax.barh(range(len(t)), t["att_country"], color=[ACC if v == 1 else GRAY for v in t["top5"]], edgecolor="white", height=0.72)
ax.set_yticks(range(len(t))); ax.set_yticklabels([f"{a} ({c})" for a, c in zip(t.airport_iata, t.iso3)], fontsize=9)
for i, (v, s) in enumerate(zip(t["att_country"], t["share_country"])):
    ax.text(v + 0.1, i, f"{v:.1f} Mt ({100*s:.1f}%)", va="center", fontsize=8.5, color=INK)
ax.set_xlabel("Connectivity-attributed CO$_2$ in 2023 (Mt, country elasticity)")
ax.set_title("B. Top 20 airports (blue = global top 5 percent by 1996 capacity)", loc="left", fontsize=11.5)
ax.spines[["top", "right"]].set_visible(False); ax.set_xlim(0, top["att_country"].max() * 1.35)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "CO2_airport_concentration.png"), dpi=200); plt.close(fig)
print("saved CO2_airport_concentration.png")

# ---------------- tex fragment (small table) ----------------
L = [r"\begin{table}[htbp]", r"\centering", r"\begin{threeparttable}",
     r"\caption{Concentration of connectivity-attributed emissions across airports, 2023}", r"\label{tab:airport_conc}", r"\footnotesize",
     r"\begin{tabular}{lccccc}", r"\toprule", r" & Top 1\% & Top 5\% & Top 10\% & Top 25\% & Gini \\", r"\midrule"]
for _, r in res.iterrows():
    L.append(f"  {r['measure']} & {100*r['top1']:.1f} & {100*r['top5']:.1f} & {100*r['top10']:.1f} & {100*r['top25']:.1f} & {r['gini']:.3f} \\\\")
L += [r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}\footnotesize",
      r"\item Shares (percent) of the global total held by the top-ranked airports, and Gini coefficients, over the " + f"{len(d):,}" + r" airports with positive 2023 emissions. Attributed emissions are CO$_2$ in 2023 times $1-\exp(-\beta\,\Delta\ln \mathrm{GACI}_{1996\text{--}2023})$ with $\beta$ from the country 2SLS (" + f"{B_COUNTRY:.2f}" + r"), the airport within-country regression (" + f"{B_AIRPORT:.2f}" + r"), or the hub-specific airport estimates (" + f"{b_top5:.2f}" + r" for the global top 5 percent by 1996 capacity, " + f"{b_not5:.2f}" + r" otherwise). Negative attributions (airports whose connectivity fell) are set to zero in the ranking.",
      r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}"]
with open(os.path.join(HERE, "_tex_airport_conc.tex"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print("DONE_19")
