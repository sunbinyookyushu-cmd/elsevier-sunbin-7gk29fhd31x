# -*- coding: utf-8 -*-
"""Carbon price of connectivity + SAF, Feyrer-IV edition.
Reads the 2SLS betas from _feyrer_main_results.csv (intl CO2, openness) and
recomputes the attribution with INTERNALLY CONSISTENT Feyrer elasticities:
  attributed CO2  = E_2023 x (1 - exp(-beta_co2_intl x dln GACI_cwm))
  attributed trade = T_2023 x (1 - exp(-beta_openness x dln GACI_cwm))
(dln from _contrib_bycountry.csv; T_2023 = 2023 goods trade level from the
combined panel). Reports the tourism-IV version alongside for comparison.
"""
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
HERE = GACI + r"\GACI_CO2"
EF = 3.15

# ---- parse Feyrer betas ----------------------------------------------------
raw = pd.read_csv(HERE + r"\_feyrer_main_results.csv", header=None)
hdr = raw.iloc[0].tolist()
brow = raw[raw[0] == "ln_gaci_cwm"].iloc[0].tolist()
def beta_of(col):
    j = hdr.index(col)
    return float(str(brow[j]).replace("*", "").replace('"', ""))
b_intl = beta_of("f_ln_co2_intl")
b_open = beta_of("f_g_int")
b_vol = beta_of("f_g_vol")
print(f"Feyrer betas: intl CO2 {b_intl:.3f} | openness {b_open:.3f} | volume {b_vol:.3f}")

# ---- country pieces --------------------------------------------------------
co2 = pd.read_csv(HERE + r"\co2_country_year.csv")
e23 = co2[co2.year == 2023][["iso3", "co2_bunker_intl"]].rename(columns={"iso3": "c"})

g = pd.read_csv(GACI + r"\gaci_panel_combined.csv", usecols=["c", "y", "ln_tradevol"])
t23 = g[g.y == 2023].dropna(subset=["ln_tradevol"]).copy()
t23["trade23"] = np.exp(t23.ln_tradevol)
dln = pd.read_csv(GACI + r"\_contrib_bycountry.csv")[["c", "dln_cwm", "gain_cwm"]]

m = dln.merge(e23, on="c").merge(t23[["c", "trade23"]], on="c")
print(f"countries: {len(m)}")

# trade side uses the VOLUME elasticity: under the Feyrer IV the openness
# response is null/negative (scale complier), so volume is the consistent
# trade-attribution channel.
m["att_co2_t"] = (m.co2_bunker_intl / 1000.0) * (1 - np.exp(-b_intl * m.dln_cwm))
m["att_trade"] = m.trade23 * (1 - np.exp(-b_vol * m.dln_cwm))

att_co2 = m.att_co2_t.sum()
att_trade = m.att_trade.sum()
world_intl = e23.co2_bunker_intl.sum() / 1000.0
world_trade = t23.trade23.sum()
print(f"attributed intl CO2 2023 (Feyrer): {att_co2/1e6:,.0f} Mt "
      f"({100*att_co2/world_intl:.1f}% of intl emissions)")
print(f"attributed trade 2023 (Feyrer openness): ${att_trade/1e12:,.2f} tn "
      f"({100*att_trade/world_trade:.1f}% of world trade)")
cp = 1e6 * att_co2 / att_trade
print(f"CARBON PRICE (Feyrer, both sides): {cp:.1f} g CO2 per $")

# comparison: tourism-IV edition (from 04: 166 Mt / $7.75 tn = 21.4 g/$)
print("comparison, tourism-IV edition: 166 Mt / $7.75 tn = 21.4 g/$")

m[["c", "dln_cwm", "att_co2_t", "att_trade"]].to_csv(
    HERE + r"\_carbon_price_feyrer.csv", index=False)

# ---- SAF path on the Feyrer carbon price ----------------------------------
PATH = {2025: 0.02, 2030: 0.06, 2035: 0.20, 2040: 0.34, 2045: 0.42, 2050: 0.70}
for r in (0.5, 0.65, 0.8):
    v35 = cp * ((1 - PATH[2035]) + PATH[2035] * (1 - r))
    v50 = cp * ((1 - PATH[2050]) + PATH[2050] * (1 - r))
    print(f"SAF r={r}: {cp:.1f} -> {v35:.1f} (2035) -> {v50:.1f} (2050) g/$")
