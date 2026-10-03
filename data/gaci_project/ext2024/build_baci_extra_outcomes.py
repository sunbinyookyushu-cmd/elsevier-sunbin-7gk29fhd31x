# -*- coding: utf-8 -*-
"""
build_baci_extra_outcomes.py -- additional mechanism outcome variants from
the pass-1 cache (no re-read of raw BACI):
  - unit-value TERCILES: tr_hivw3 (top tercile $/kg) vs tr_lovw3 (bottom),
    middle tercile dropped -> sharper value/weight contrast
  - EXPORT-only category values: xr_interm, xr_consum, xr_hivw, xr_lovw
Appends columns to baci_mechanism_panel.csv -> baci_mechanism_extra.csv
(c, y + new tr/ln columns). Merge with build_mechanism_merge.py afterwards.
"""
import os, glob, collections
import numpy as np
import pandas as pd

RAW   = r"C:\Users\sunbi\GACI_baci_raw"
BDIR  = os.path.join(RAW, "BACI_HS92_V202601")
CACHE = os.path.join(RAW, "cache_cy_hs6")
HERE  = os.path.dirname(os.path.abspath(__file__))
YEARS = range(1996, 2025)

# ---- concordance: HS92 -> BEC group (reuse logic from build_baci_mechanism) ----
un = pd.read_excel(os.path.join(RAW, "UN_HS_SITC_BEC_correlations.xlsx"),
                   dtype=str).rename(columns=lambda s: s.strip())
un = un[["HS92", "BEC4"]].dropna(subset=["HS92"]).drop_duplicates("HS92")
un["HS92"] = un["HS92"].str.zfill(6)
INTERM = {"111", "121", "21", "22", "31", "322", "42", "53"}
CONSUM = {"112", "122", "51", "522", "61", "62", "63"}
bec = {}
for h, b4 in zip(un["HS92"], un["BEC4"].fillna("")):
    bec[h] = "interm" if b4 in INTERM else ("consum" if b4 in CONSUM else "other")

# ---- pooled unit values -> tercile classification ----
uv_v = collections.defaultdict(float); uv_q = collections.defaultdict(float)
for y in YEARS:
    f = os.path.join(CACHE, f"exp_{y}.csv")
    d = pd.read_csv(f, dtype={"k": str})
    d = d[d["q"] > 0]
    for k, v, q in zip(d["k"].str.zfill(6), d["v"], d["q"]):
        uv_v[k] += v; uv_q[k] += q
uv = pd.Series({k: uv_v[k]/uv_q[k] for k in uv_v if uv_q[k] > 0})
t1, t2 = uv.quantile([1/3, 2/3])
hi3 = set(uv[uv >= t2].index); lo3 = set(uv[uv <= t1].index)
print(f"unit-value terciles: cuts {t1:.2f} / {t2:.2f} $/kg; "
      f"top={len(hi3)} bottom={len(lo3)} products")

rows = []
for y in YEARS:
    fe = os.path.join(CACHE, f"exp_{y}.csv"); fi = os.path.join(CACHE, f"imp_{y}.csv")
    agg = collections.defaultdict(lambda: collections.defaultdict(float))
    for side, f in (("x", fe), ("m", fi)):
        d = pd.read_csv(f, dtype={"k": str})
        d["k"] = d["k"].str.zfill(6)
        d["vw3"] = np.where(d["k"].isin(hi3), "hivw3",
                   np.where(d["k"].isin(lo3), "lovw3", "mid"))
        d["bg"] = d["k"].map(bec)
        for c, sub in d.groupby("c"):
            a = agg[c]
            for g, vv in sub.groupby("vw3")["v"].sum().items():
                a[f"{side}_{g}"] += vv
            if side == "x":
                for g, vv in sub.groupby("bg")["v"].sum().items():
                    a[f"x_{g}"] += vv
                a["x_total"] += sub["v"].sum()
    for c, a in agg.items():
        rows.append({"i_num": c, "y": y, **a})
    print(f"{y} done ({len(agg)} countries)", flush=True)

pan = pd.DataFrame(rows).fillna(0.0)
cc = glob.glob(os.path.join(BDIR, "country_codes_V*.csv"))
cmap = pd.read_csv(cc[0])
pan["c"] = pan["i_num"].map(dict(zip(cmap["country_code"], cmap["country_iso3"])))

out = pan[["c", "y"]].copy()
out["tr_hivw3"] = pan.get("x_hivw3", 0.0) + pan.get("m_hivw3", 0.0)
out["tr_lovw3"] = pan.get("x_lovw3", 0.0) + pan.get("m_lovw3", 0.0)
for col in ["x_hivw3", "x_lovw3", "x_interm", "x_consum", "x_total"]:
    out[col] = pan.get(col, 0.0)
for col in ["tr_hivw3", "tr_lovw3", "x_hivw3", "x_lovw3",
            "x_interm", "x_consum", "x_total"]:
    with np.errstate(divide="ignore"):
        out["ln_" + col] = np.where(out[col] > 0, np.log(out[col]*1000.0), np.nan)
out = out.dropna(subset=["c"])
out.to_csv(os.path.join(HERE, "baci_mechanism_extra.csv"), index=False)
print(f"WROTE baci_mechanism_extra.csv: {len(out):,} rows")
