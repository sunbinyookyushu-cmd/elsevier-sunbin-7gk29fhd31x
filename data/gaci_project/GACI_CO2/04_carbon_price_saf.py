# -*- coding: utf-8 -*-
"""Carbon price of connectivity + SAF scenarios.

Mirrors the trade paper's partial-equilibrium counterfactual: attributable
share = 1 - exp(-beta * dln GACI_cwm 1996-2023), applied to 2023 levels.
  - emissions side: beta_intl = 3.164 (2SLS, ln intl bunker CO2; co2_main.log),
    applied to 2023 international bunker emissions; total-bunker beta = 1.162
    (not significant) reported as indicative only.
  - trade side: attributed 2023 trade gains from the trade paper
    (_contrib_bycountry.csv, gain_cwm; world total ~$7.8tn, beta = 1.302).
Carbon price = attributed CO2 / attributed trade (g CO2 per USD).

SAF scenarios: fuel = CO2 / 3.15 (Jet A factor, Fangyu 2026-08-20; piston
AvGas 3.10 share negligible). Life-cycle emissions under blending share s and
LCA reduction r:  E(s) = E * [(1-s) + s*(1-r)].
Blending path: ReFuelEU (2% 2025, 6% 2030, 20% 2035, 34% 2040, 42% 2045,
70% 2050); r in {0.5, 0.65, 0.8}.
Outputs: _carbon_price_bycountry.csv, CO2_saf_scenarios.png, console summary.
"""
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
HERE = GACI + r"\GACI_CO2"

BETA_INTL = 3.164     # 2SLS ln intl bunker CO2 on ln GACI_cwm (co2_main.log)
BETA_TOT = 1.162      # 2SLS ln total bunker CO2 (not significant; indicative)
EF = 3.15             # kg CO2 per kg Jet A

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'],
                     'mathtext.fontset': 'stix'})
INK = '#1f1f1f'

co2 = pd.read_csv(HERE + r"\co2_country_year.csv")
e23 = co2[co2.year == 2023][["iso3", "co2_bunker", "co2_bunker_intl"]].copy()

tr = pd.read_csv(GACI + r"\_contrib_bycountry.csv")  # c, dln_cwm, gain_cwm ...
m = tr.merge(e23, left_on="c", right_on="iso3", how="inner")
print(f"countries in both: {len(m)}")

# attributed 2023 emissions (tonnes)
m["att_co2_intl_t"] = (m.co2_bunker_intl / 1000.0) * (1 - np.exp(-BETA_INTL * m.dln_cwm))
m["att_co2_tot_t"] = (m.co2_bunker / 1000.0) * (1 - np.exp(-BETA_TOT * m.dln_cwm))

att_co2 = m.att_co2_intl_t.sum()
att_co2_tot = m.att_co2_tot_t.sum()
att_trade = m.gain_cwm.sum()
world_intl = (e23.co2_bunker_intl.sum() / 1000.0)
print(f"attributed intl CO2 2023: {att_co2/1e6:,.0f} Mt "
      f"({100*att_co2/world_intl:.1f}% of 2023 intl emissions)")
print(f"attributed total-bunker CO2 (indicative): {att_co2_tot/1e6:,.0f} Mt")
print(f"attributed trade (trade paper): ${att_trade/1e12:,.2f} tn")
cp = 1e6 * att_co2 / att_trade   # g per USD
print(f"CARBON PRICE OF CONNECTIVITY: {cp:.1f} g CO2 per $ of attributed trade")

m["cp_g_per_usd"] = np.where(m.gain_cwm > 0, 1e6 * m.att_co2_intl_t / m.gain_cwm, np.nan)
m[["c", "dln_cwm", "gain_cwm", "att_co2_intl_t", "att_co2_tot_t", "cp_g_per_usd"]] \
    .to_csv(HERE + r"\_carbon_price_bycountry.csv", index=False)

top = m[m.gain_cwm > 1e10].nlargest(8, "cp_g_per_usd")
bot = m[m.gain_cwm > 1e10].nsmallest(8, "cp_g_per_usd")
print("dirtiest connectivity gains (g/$, gains>$10bn):",
      [(r.c, round(r.cp_g_per_usd, 1)) for r in top.itertuples()])
print("cleanest connectivity gains (g/$):",
      [(r.c, round(r.cp_g_per_usd, 1)) for r in bot.itertuples()])

# ---- SAF scenarios ---------------------------------------------------------
PATH = {2025: 0.02, 2030: 0.06, 2035: 0.20, 2040: 0.34, 2045: 0.42, 2050: 0.70}
RS = [0.5, 0.65, 0.8]
years = sorted(PATH)
fig, ax = plt.subplots(figsize=(8.6, 5.2))
ax.set_axisbelow(True)
ax.yaxis.grid(True, color='#e6e6e6', lw=0.7)
colors = {0.5: '#8ab6d6', 0.65: '#1f4e79', 0.8: '#12314d'}
for r in RS:
    vals = [cp * ((1 - PATH[y]) + PATH[y] * (1 - r)) for y in years]
    ax.plot(years, vals, 'o-', color=colors[r], lw=1.8, ms=6,
            label=f'LCA reduction {int(100*r)}%')
ax.axhline(cp, color='#b0b0b0', lw=0.9, ls=(0, (4, 3)))
ax.annotate(f'2023 baseline: {cp:.0f} g/\\$', (years[0], cp),
            textcoords='offset points', xytext=(2, 6), fontsize=11, color=INK)
ax.set_xlabel('ReFuelEU blending milestone year', fontsize=12.5, color=INK)
ax.set_ylabel('Carbon price of connectivity\n(g CO$_2$ per \\$ of attributed trade)',
              fontsize=12.5, color=INK)
ax.legend(frameon=False, fontsize=11)
for sp in ['top', 'right']:
    ax.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(HERE + r"\CO2_saf_scenarios.png", dpi=200, facecolor='white')
print("wrote CO2_saf_scenarios.png")
for r in RS:
    v35 = cp * ((1 - PATH[2035]) + PATH[2035] * (1 - r))
    v50 = cp * ((1 - PATH[2050]) + PATH[2050] * (1 - r))
    print(f"r={r}: carbon price {cp:.1f} -> {v35:.1f} (2035 mandate) -> {v50:.1f} (2050) g/$")
