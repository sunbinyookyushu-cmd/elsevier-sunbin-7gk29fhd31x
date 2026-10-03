# -*- coding: utf-8 -*-
"""Cross-validate our country-year aviation CO2 (bunker allocation) against the
OWID/ICCT country series (Graver et al.; departure-based, so bunker is the
comparable measure). Reports level ratios, log-log correlation, and the
largest divergences."""
import numpy as np
import pandas as pd

HERE = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2"
ours = pd.read_csv(HERE + r"\co2_country_year.csv")
owid = pd.read_csv(HERE + r"\_owid_aviation.csv")
owid = owid[owid.code.notna() & (owid.code.str.len() == 3)]
owid = owid.rename(columns={"code": "iso3", "total_annual_emissions": "owid_t"})

m = ours.merge(owid[["iso3", "year", "owid_t"]], on=["iso3", "year"], how="inner")
m["ours_t"] = m.co2_bunker / 1000.0  # kg -> tonnes
m = m[(m.ours_t > 0) & (m.owid_t > 0)]
print(f"overlap: {len(m):,} country-years, {m.iso3.nunique()} countries, "
      f"years {m.year.min()}-{m.year.max()}")

for yr in sorted(m.year.unique()):
    s = m[m.year == yr]
    r = np.corrcoef(np.log(s.ours_t), np.log(s.owid_t))[0, 1]
    print(f"{yr}: N={len(s):3d}  global ratio ours/OWID = "
          f"{s.ours_t.sum()/s.owid_t.sum():.3f}  log-log corr = {r:.3f}")

s = m[m.year == 2019].copy()
s["ratio"] = s.ours_t / s.owid_t
big = s[s.owid_t > 1e6].sort_values("ratio")  # countries > 1 Mt
print("\n2019, countries > 1 Mt: ratio ours/OWID")
print("lowest 5:")
print(big[["iso3", "ratio"]].head(5).to_string(index=False))
print("highest 5:")
print(big[["iso3", "ratio"]].tail(5).to_string(index=False))
print(f"\nmedian ratio (>1Mt countries): {big.ratio.median():.3f}")
