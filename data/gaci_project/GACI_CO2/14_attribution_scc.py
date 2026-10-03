# -*- coding: utf-8 -*-
"""Country-level attribution with the FEYRER betas + social-cost-of-carbon
valuation. Fixes the inconsistency where CO2_map_attributed_2023.png was
built from _carbon_price_bycountry.csv (tourism-IV beta 1.162 ns) while the
caption claims the Feyrer elasticity.
  attributed CO2_c = E_2023,c x (1 - exp(-beta x dln GACI_cwm,c))
  beta_tot = 5.6689, beta_intl = 5.6902 (_feyrer_main_results.csv)
SCC values (USD per t CO2, 2020 USD):
  51  = US IWG (2021) interim, 3% discount
  185 = Rennert et al. (2022, Nature), 2% near-term discount
  190 = US EPA (2023) central, 2% Ramsey
Output: _attribution_scc.csv (per country) + console world totals + top table.
"""
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
HERE = GACI + r"\GACI_CO2"

raw = pd.read_csv(HERE + r"\_feyrer_main_results.csv", header=None)
hdr = raw.iloc[0].tolist()
brow = raw[raw[0] == "ln_gaci_cwm"].iloc[0].tolist()
def beta_of(col):
    return float(str(brow[hdr.index(col)]).replace("*", "").replace('"', ""))
B_TOT = beta_of("f_ln_co2_tot")
B_INTL = beta_of("f_ln_co2_intl")
print(f"Feyrer betas: total {B_TOT:.4f} | intl {B_INTL:.4f}")

co2 = pd.read_csv(HERE + r"\co2_country_year.csv")
e23 = co2[co2.year == 2023][["iso3", "co2_bunker", "co2_bunker_intl"]] \
        .rename(columns={"iso3": "c"})
dln = pd.read_csv(GACI + r"\_contrib_bycountry.csv")[["c", "dln_cwm"]]
m = dln.merge(e23, on="c", how="inner")
print(f"countries merged: {len(m)} (dln {len(dln)}, co2-2023 {len(e23)})")

# kg -> t
m["e_tot_t"] = m.co2_bunker / 1000.0
m["e_intl_t"] = m.co2_bunker_intl / 1000.0
m["att_tot_t"] = m.e_tot_t * (1 - np.exp(-B_TOT * m.dln_cwm))
m["att_intl_t"] = m.e_intl_t * (1 - np.exp(-B_INTL * m.dln_cwm))

SCC = {"scc51": 51.0, "scc185": 185.0, "scc190": 190.0}
for k, v in SCC.items():
    m[f"val_tot_{k}_usd"] = m.att_tot_t * v

world_e = e23.co2_bunker.sum() / 1000.0          # includes countries w/o dln
world_e_m = m.e_tot_t.sum()                      # merged coverage
att = m.att_tot_t.sum()
att_i = m.att_intl_t.sum()
print(f"2023 world bunker CO2: {world_e/1e6:,.0f} Mt (merged coverage {world_e_m/1e6:,.0f} Mt)")
print(f"attributed TOTAL 2023 (Feyrer {B_TOT:.2f}): {att/1e6:,.1f} Mt "
      f"= {100*att/world_e:.1f}% of world / {100*att/world_e_m:.1f}% of merged")
print(f"attributed INTL  2023 (Feyrer {B_INTL:.2f}): {att_i/1e6:,.1f} Mt "
      f"= {100*att_i/(m.e_intl_t.sum()):.1f}% of merged intl")
pos = m[m.att_tot_t > 0].att_tot_t.sum()
print(f"  gross positive {pos/1e6:,.1f} Mt / gross negative {(att-pos)/1e6:,.1f} Mt")
for k, v in SCC.items():
    print(f"SCC ${v:.0f}/t: world attributed value = ${att*v/1e9:,.1f} bn per year "
          f"(gross positive ${pos*v/1e9:,.1f} bn)")

m = m.sort_values("att_tot_t", ascending=False)
cols = ["c", "dln_cwm", "e_tot_t", "att_tot_t", "att_intl_t"] + \
       [f"val_tot_{k}_usd" for k in SCC]
m[cols].to_csv(HERE + r"\_attribution_scc.csv", index=False)

print("\nTop 12 / bottom 3 (att Mt, $bn at SCC190):")
show = pd.concat([m.head(12), m.tail(3)])
for r in show.itertuples():
    print(f"  {r.c}: {r.att_tot_t/1e6:+7.1f} Mt  ${r.att_tot_t*190/1e9:+8.1f} bn")
