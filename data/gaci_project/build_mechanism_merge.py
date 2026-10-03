# -*- coding: utf-8 -*-
"""
build_mechanism_merge.py -- merge BACI mechanism outcomes into the main
IV panel. One CSV out; the do-file imports it directly (no Stata merge).

  gaci_panel_3iv.csv          main panel (c, y, ln_gaci_cwm, tourism_int, ...)
+ baci_mechanism_panel.csv    BACI splits (ln_tr_* and tr_* levels)
+ baci_mechanism_extra.csv    tercile + export-side variants
= gaci_panel_mechanism.csv
"""
import pandas as pd

main = pd.read_csv("gaci_panel_3iv.csv")
mech = pd.read_csv("baci_mechanism_panel.csv")
extra = pd.read_csv("baci_mechanism_extra.csv")

keep_m = [c for c in mech.columns
          if c.startswith(("ln_", "tr_")) or c in ("c", "y")]
keep_e = [c for c in extra.columns if c not in ("i_num",)]

out = (main.merge(mech[keep_m], on=["c", "y"], how="left", validate="1:1")
           .merge(extra[keep_e], on=["c", "y"], how="left", validate="1:1"))

matched = out["ln_tr_total"].notna().mean()
print(f"panel rows={len(out):,}  BACI matched={matched:.1%}")
assert matched > 0.95, "BACI merge coverage below 95% -- check ISO3 mapping"

out.to_csv("gaci_panel_mechanism.csv", index=False)
print("wrote gaci_panel_mechanism.csv  cols=%d" % out.shape[1])
