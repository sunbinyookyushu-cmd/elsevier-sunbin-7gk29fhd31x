# -*- coding: utf-8 -*-
"""Which countries lose relative connectivity after oil supply shocks? Interacted local projections, country x year
(user 2026-10-02, VAR-style dynamics on relative GACI).

  lnGACI_(c,y+h) - lnGACI_(c,y-1) = a_c + d_y + g_h (S_y x Z_c) + th_h (S_y x Inc_c)
                                     + f1 lnGDP_(c,y-1) + f2 lnPop_(c,y-1) + r dlnGACI_(c,y-1) + e,   h = 0..4
  GACI = country ln GACI_cwm (trade-paper measure, country_year.csv, 1996-2023); year FE remove the common part, so
  the outcome is relative connectivity. S_y = annual sum of the monthly Kaenzig news shock or sign-flipped BH supply
  shock, scaled to 1 SD (1997-2019). Z_c and Inc_c (ln GDP pc) are 1996 values, z-scored:
    fuel exposure = ln seat-weighted stage length 1996; remoteness = ln mean sea distance (CERDI, trade paper);
    oil rents 1996 (% GDP); international seat share 1996; initial connectivity = ln GACI_cwm 1996.
  Specs: each Z alone (with S x income and controls), all Z jointly.
  Samples: main y+h <= 2019; extended y+h <= 2023 with any year 2020-2021 in [y-1, y+h] dropped.
  SE: country cluster + Newey-West over years, L = max(h+1, 2).
Output: _res_country_gaci_lp.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import warnings

import numpy as np
import pandas as pd
from _est import fit

warnings.filterwarnings("ignore")
c = pd.read_csv("country_year.csv", usecols=["c", "y", "ln_gaci_cwm", "lngdp", "lnpop", "kz", "bh_neg", "ln_stage96",
                                             "ln_remote", "oilrent96", "intl_share96", "ln_gaci_cwm96", "lnpc96"])
c = c.sort_values(["c", "y"])
W = c.pivot_table(index="c", columns="y", values="ln_gaci_cwm")
W = W.reindex(columns=range(1996, 2024))
sh = c.drop_duplicates("y").set_index("y")[["kz", "bh_neg"]].sort_index()
sd = sh.loc[1997:2019].std()
ZS = {"fuel exposure (stage length)": "ln_stage96", "remoteness (sea distance)": "ln_remote", "oil rents": "oilrent96",
      "international share": "intl_share96", "initial connectivity (GACI 1996)": "ln_gaci_cwm96"}
base = c.groupby("c")[list(ZS.values()) + ["lnpc96"]].first()
Z = (base - base.mean()) / base.std()

rows = []
for h in range(0, 5):
    dy = (W.shift(-h, axis=1) - W.shift(1, axis=1)).stack().rename("dy").reset_index().rename(columns={"level_1": "y"})
    dy.columns = ["c", "y", "dy"]
    lagd = (W - W.shift(1, axis=1)).shift(1, axis=1).stack().rename("dl").reset_index()
    lagd.columns = ["c", "y", "dl"]
    d = dy.merge(lagd, on=["c", "y"], how="left")
    ctl = c[["c", "y", "lngdp", "lnpop"]].copy()
    ctl["y"] += 1
    d = d.merge(ctl.rename(columns={"lngdp": "lngdp_l1", "lnpop": "lnpop_l1"}), on=["c", "y"], how="left")
    d = d.merge(Z.add_prefix("z_"), left_on="c", right_index=True, how="left")
    for s in ["kz", "bh_neg"]:
        d["S_" + s] = d.y.map(sh[s] / sd[s])
    for samp, keep in [("main (to 2019)", (d.y >= 1997) & (d.y + h <= 2019)),
                       ("extended (to 2023, 2020-21 out)", (d.y >= 1997) & (d.y + h <= 2023)
                        & ~d.y.apply(lambda y: any(t in (2020, 2021) for t in range(y - 1, y + h + 1))))]:
        dd0 = d[keep]
        for slab, s in [("Kaenzig", "S_kz"), ("BH", "S_bh_neg")]:
            specs = [(k, [v]) for k, v in ZS.items()] + [("all jointly", list(ZS.values()))]
            for spec, zv in specs:
                dd = dd0.dropna(subset=["dy", "dl", "lngdp_l1", "lnpop_l1", "z_lnpc96", s] + ["z_" + v for v in zv]).copy()
                xs = []
                for v in zv + ["lnpc96"]:
                    dd["i_" + v] = dd[s] * dd["z_" + v]
                    xs.append("i_" + v)
                o = fit(dd, "dy", exog=xs + ["lngdp_l1", "lnpop_l1", "dl"], fes=["c", "y"], vc=("dk", "c", "y", max(h + 1, 2)),
                        return_fs=False)
                for v in zv:
                    rows.append(dict(sample=samp, shock=slab, h=h, spec=spec if spec == "all jointly" else "alone",
                                     Z=[k for k, vv in ZS.items() if vv == v][0], b=o["coef"]["i_" + v], se=o["se"]["i_" + v],
                                     p=o["p"]["i_" + v], b_income=o["coef"]["i_lnpc96"], p_income=o["p"]["i_lnpc96"],
                                     n=o["n"], countries=dd.c.nunique()))
    print("h", h, "done", flush=True)
R = pd.DataFrame(rows)
R.to_csv("_res_country_gaci_lp.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 500)
show = R.pivot_table(index=["sample", "shock", "spec", "Z"], columns="h", values="b").round(4)
pv = R.pivot_table(index=["sample", "shock", "spec", "Z"], columns="h", values="p").round(3)
print(show.to_string())
print(pv.to_string())
print("n/countries (h=0, main):", R[(R.h == 0) & (R["sample"].str.startswith("main"))][["n", "countries"]].iloc[0].to_dict())
