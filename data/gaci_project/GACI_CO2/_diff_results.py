# -*- coding: utf-8 -*-
"""_diff_results.py  compare result CSVs in _bak_results_pre0908/ with the current ones.
Usage: python _diff_results.py [name1.csv name2.csv ...]   (default: all common files)
Reports rows where any numeric column differs at 2 decimals (3 for small |x|<0.1)."""
import os, sys
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); BAK = os.path.join(HERE, "_bak_results_pre0908")
names = sys.argv[1:] or sorted(f for f in os.listdir(BAK) if f.endswith(".csv") and os.path.exists(os.path.join(HERE, f)))
def rd(p):
    try: return pd.read_csv(p)
    except Exception: return pd.read_csv(p, header=None)
for nm in names:
    o = rd(os.path.join(BAK, nm)); n = rd(os.path.join(HERE, nm))
    if o.shape[1] != n.shape[1] or list(o.columns) != list(n.columns):
        print(f"== {nm}: columns differ (old {o.shape}, new {n.shape})"); continue
    keys = [c for c in o.columns if o[c].dtype == object or c in ("year", "y", "bin", "quintile", "draw")]
    nums = [c for c in o.columns if c not in keys and np.issubdtype(o[c].dtype, np.number)]
    if not keys or not nums or len(o) > 5000:
        print(f"== {nm}: skipped (keys {len(keys)}, nums {len(nums)}, rows {len(o)}->{len(n)})"); continue
    m = o.merge(n, on=keys, how="outer", suffixes=("_o", "_n"), indicator=True)
    added = m[m._merge == "right_only"]; gone = m[m._merge == "left_only"]; both = m[m._merge == "both"]
    ch = []
    for c in nums:
        a, b = both[c + "_o"].astype(float), both[c + "_n"].astype(float)
        dec = np.where(np.abs(a) < 0.1, 3, 2)
        ra = np.array([round(x, int(d)) if pd.notna(x) else np.nan for x, d in zip(a, dec)]); rb = np.array([round(x, int(d)) if pd.notna(x) else np.nan for x, d in zip(b, dec)])
        diff = ~((ra == rb) | (np.isnan(ra) & np.isnan(rb)))
        for i in np.where(diff)[0]:
            ch.append((tuple(both.iloc[i][k] for k in keys), c, a.iloc[i], b.iloc[i]))
    print(f"== {nm}: rows {len(o)}->{len(n)}, added {len(added)}, removed {len(gone)}, changed cells {len(ch)}")
    for k, c, a, b in ch[:60]:
        print(f"   {k} {c}: {a:.4g} -> {b:.4g}")
    if len(ch) > 60: print(f"   ... {len(ch) - 60} more")
