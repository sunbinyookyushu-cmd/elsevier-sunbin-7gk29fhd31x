# -*- coding: utf-8 -*-
"""
build_baci_mechanism.py -- mechanism outcomes from BACI HS92 (V202601)
for the GACI connectivity->trade paper.

Channel-specific trade outcomes, country-year, 1996-2023:
  (1) Rauch split      : differentiated (n) / reference-priced (r) / homogeneous (w)
                         [conservative baseline; liberal for robustness]
                         chain: HS92(6d) -> SITC2(4d, UN correlation) -> Rauch(1999 revised)
  (2) unit-value split : high vs low value-to-weight (pooled product median $/kg,
                         time-invariant classification)
  (3) BEC split        : intermediate / consumption / capital (UN BEC4 grouping)
  (4) extensive margin : # HS6 products exported, # export partners

Pass 1 (heavy, resumable): per-year BACI csv -> (country,HS6) aggregates cache
Pass 2 (light)           : cache + concordances -> baci_mechanism_panel.csv

Raw dir : C:/Users/sunbi/GACI_baci_raw   (zip extracted to ./BACI_HS92_V202601/)
Progress: _baci_progress.txt (this folder) -- one line per completed step.
"""
import os, sys, glob, collections, csv
import numpy as np
import pandas as pd

RAW    = r"C:\Users\sunbi\GACI_baci_raw"
BDIR   = os.path.join(RAW, "BACI_HS92_V202601")
CACHE  = os.path.join(RAW, "cache_cy_hs6")
HERE   = os.path.dirname(os.path.abspath(__file__))
PROG   = os.path.join(HERE, "_baci_progress.txt")
OUT    = os.path.join(HERE, "baci_mechanism_panel.csv")
YEARS  = range(1996, 2024)

def log(msg):
    print(msg, flush=True)
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ---------------------------------------------------------------- pass 1
def pass1():
    os.makedirs(CACHE, exist_ok=True)
    for y in YEARS:
        out_e = os.path.join(CACHE, f"exp_{y}.csv")
        out_i = os.path.join(CACHE, f"imp_{y}.csv")
        if os.path.exists(out_e) and os.path.exists(out_i):
            continue
        src = glob.glob(os.path.join(BDIR, f"BACI_HS92_Y{y}_V*.csv"))
        if not src:
            log(f"pass1 {y}: SOURCE MISSING, skipped"); continue
        df = pd.read_csv(src[0], usecols=["t", "i", "j", "k", "v", "q"],
                         dtype={"t": "int16", "i": "int32", "j": "int32",
                                "k": "str", "v": "float64"},
                         converters=None, na_values=["NA", ""], low_memory=False)
        df["q"] = pd.to_numeric(df["q"], errors="coerce")
        # exporter side: value, tonnage, and partner count per (i,k)
        e = (df.groupby(["i", "k"], sort=False)
               .agg(v=("v", "sum"), q=("q", "sum"), npart=("j", "nunique"))
               .reset_index().rename(columns={"i": "c"}))
        m = (df.groupby(["j", "k"], sort=False)
               .agg(v=("v", "sum"), q=("q", "sum"))
               .reset_index().rename(columns={"j": "c"}))
        e.to_csv(out_e, index=False); m.to_csv(out_i, index=False)
        log(f"pass1 {y}: rows={len(df):,} -> exp cells={len(e):,} imp cells={len(m):,}")

# ---------------------------------------------------------------- concordances
def load_concordances():
    # UN correlation: HS92 -> SITC2(4d), HS92 -> BEC4
    un = pd.read_excel(os.path.join(RAW, "UN_HS_SITC_BEC_correlations.xlsx"),
                       dtype=str).rename(columns=lambda s: s.strip())
    un = un[["HS92", "SITC2", "BEC4"]].dropna(subset=["HS92"]).drop_duplicates("HS92")
    un["HS92"]  = un["HS92"].str.zfill(6)
    un["sitc4"] = un["SITC2"].str.replace(".", "", regex=False).str.ljust(4, "0").str[:4]

    # Rauch (revised): sitc4 -> con/lib in {n, r, w}
    ra = pd.read_csv(os.path.join(RAW, "Rauch_classification_revised.csv"), dtype=str)
    ra["sitc4"] = ra["sitc4"].str.zfill(4)
    ra3 = (ra.assign(s3=ra["sitc4"].str[:3]).groupby("s3")["con"]
             .agg(lambda s: s.mode().iat[0]))          # 3-digit fallback
    un = un.merge(ra[["sitc4", "con", "lib"]], on="sitc4", how="left")
    miss = un["con"].isna()
    un.loc[miss, "con"] = un.loc[miss, "sitc4"].str[:3].map(ra3)
    un.loc[miss, "lib"] = un.loc[miss, "con"]

    # BEC4 -> end-use group (UN standard grouping; 321/7 unallocated -> other)
    INTERM = {"111", "121", "21", "22", "31", "322", "42", "53"}
    CONSUM = {"112", "122", "51", "522", "61", "62", "63"}
    CAPIT  = {"41", "521"}
    def bec_grp(b):
        if b in INTERM: return "interm"
        if b in CONSUM: return "consum"
        if b in CAPIT:  return "capital"
        return "other"
    un["bec_grp"] = un["BEC4"].fillna("").map(bec_grp)
    conc = un.set_index("HS92")[["con", "lib", "bec_grp"]]
    log(f"concordance: {len(conc):,} HS92 codes | rauch matched="
        f"{conc['con'].notna().mean():.1%}")
    return conc

# ---------------------------------------------------------------- pass 2
def pass2():
    conc = load_concordances()

    # pooled unit values -> time-invariant high/low value-to-weight split
    uv_v = collections.defaultdict(float); uv_q = collections.defaultdict(float)
    for y in YEARS:
        f = os.path.join(CACHE, f"exp_{y}.csv")
        if not os.path.exists(f): continue
        d = pd.read_csv(f, dtype={"k": str})
        d = d[d["q"] > 0]
        for k, v, q in zip(d["k"].str.zfill(6), d["v"], d["q"]):
            uv_v[k] += v; uv_q[k] += q
    uv = pd.Series({k: uv_v[k]/uv_q[k] for k in uv_v if uv_q[k] > 0}, name="uv")
    med = uv.median()
    vw_hi = set(uv[uv >= med].index)
    log(f"unit values: {len(uv):,} products, median={med:.2f} $1000/ton "
        f"(={med:.2f} $/kg); high-V/W products={len(vw_hi):,}")

    rows = []
    for y in YEARS:
        fe = os.path.join(CACHE, f"exp_{y}.csv"); fi = os.path.join(CACHE, f"imp_{y}.csv")
        if not (os.path.exists(fe) and os.path.exists(fi)): continue
        agg = collections.defaultdict(lambda: collections.defaultdict(float))
        ext = collections.defaultdict(lambda: [0, 0])          # nprod, npartner-sum
        for side, f in (("x", fe), ("m", fi)):
            d = pd.read_csv(f, dtype={"k": str})
            d["k"] = d["k"].str.zfill(6)
            d = d.join(conc, on="k")
            d["vwgrp"] = np.where(d["k"].isin(vw_hi), "hivw", "lovw")
            for c, sub in d.groupby("c"):
                a = agg[c]
                a[f"{side}_total"] += sub["v"].sum()
                for g, vv in sub.groupby("con")["v"].sum().items():
                    a[f"{side}_rauch_{g}"] += vv
                for g, vv in sub.groupby("lib")["v"].sum().items():
                    a[f"{side}_rauchlib_{g}"] += vv
                for g, vv in sub.groupby("bec_grp")["v"].sum().items():
                    a[f"{side}_bec_{g}"] += vv
                for g, vv in sub.groupby("vwgrp")["v"].sum().items():
                    a[f"{side}_{g}"] += vv
                if side == "x":
                    ext[c][0] = sub["k"].nunique()
                    ext[c][1] = int(sub["npart"].sum())
        for c, a in agg.items():
            r = {"i_num": c, "y": y, "nprod_exp": ext[c][0], "nflow_exp": ext[c][1]}
            r.update(a); rows.append(r)
        log(f"pass2 {y}: countries={len(agg)}")

    pan = pd.DataFrame(rows).fillna(0.0)

    # numeric UN code -> ISO3 (BACI country codes file)
    cc = glob.glob(os.path.join(BDIR, "country_codes_V*.csv"))
    cmap = pd.read_csv(cc[0])
    isocol = [c for c in cmap.columns if "iso" in c.lower() and "3" in c][0]
    numcol = [c for c in cmap.columns if "code" in c.lower()][0]
    pan["c"] = pan["i_num"].map(dict(zip(cmap[numcol], cmap[isocol])))

    # trade totals (X+M, in current $1000) and logs
    def tv(stub):
        return pan.get(f"x_{stub}", 0.0) + pan.get(f"m_{stub}", 0.0)
    outcols = {"total": "total",
               "rauch_n": "diff", "rauch_r": "ref", "rauch_w": "homog",
               "rauchlib_n": "diff_lib", "rauchlib_r": "ref_lib", "rauchlib_w": "homog_lib",
               "bec_interm": "interm", "bec_consum": "consum", "bec_capital": "capital",
               "hivw": "hivw", "lovw": "lovw"}
    keep = pan[["c", "y", "nprod_exp", "nflow_exp"]].copy()
    for stub, name in outcols.items():
        keep[f"tr_{name}"] = tv(stub)
        with np.errstate(divide="ignore"):
            keep[f"ln_tr_{name}"] = np.where(keep[f"tr_{name}"] > 0,
                                             np.log(keep[f"tr_{name}"] * 1000.0), np.nan)
    keep["ln_nprod"] = np.log(keep["nprod_exp"].clip(lower=1))
    keep["ln_nflow"] = np.log(keep["nflow_exp"].clip(lower=1))
    keep = keep.dropna(subset=["c"])
    keep.to_csv(OUT, index=False)
    log(f"WROTE {OUT}: {len(keep):,} country-years, "
        f"{keep['c'].nunique()} countries, {keep['y'].min()}-{keep['y'].max()}")

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("all", "pass1"): pass1()
    if step in ("all", "pass2"): pass2()
