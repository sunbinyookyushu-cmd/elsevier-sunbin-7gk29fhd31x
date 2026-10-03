# -*- coding: utf-8 -*-
"""Check that every estimate in the result CSVs appears in the assembled main.tex."""
import csv, io, os, collections

SRC = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
TEX = os.path.join(SRC, "Overleaf_Inequality_20260918", "main.tex")
tex = io.open(TEX, encoding="utf-8").read()

FILES = {
    "_main_results.csv": ("block?iv", "b"),
    "_hetero_results.csv": ("block", "b"),
    "_conc_mech_results.csv": ("block", "b"),
    "_longdiff_results.csv": ("block", "b"),
    "_robust_results.csv": ("block", "b"),
    "_tails_results.csv": ("block", "b"),
    "_diag_results.csv": ("block", "b"),
    "_openskies_results.csv": ("block", "b"),
    "_gdp_results.csv": ("block", "b"),
}


def present(v):
    """Is this estimate printed anywhere in the tex, at any plausible rounding?"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None                      # not a number: nothing to find
    for d in (4, 3, 2, 1, 0):
        s = ("%." + str(d) + "f") % x
        if s in tex:
            return True
        if s.startswith("-") and s[1:] in tex:   # sign may be rendered as $-$
            return True
    return False


total = miss_total = 0
report = []
for fn, (bkey, vkey) in FILES.items():
    rows = list(csv.DictReader(io.open(os.path.join(SRC, fn), encoding="utf-8-sig")))
    key = "iv" if bkey == "block?iv" else "block"
    per = collections.defaultdict(lambda: [0, 0])   # [n, n_missing]
    misses = collections.defaultdict(list)
    for r in rows:
        blk = r.get(key, "")
        p = present(r.get(vkey))
        if p is None:
            continue
        per[blk][0] += 1
        total += 1
        if not p:
            per[blk][1] += 1
            miss_total += 1
            misses[blk].append(r)
    report.append((fn, per, misses))

for fn, per, misses in report:
    print("== %s" % fn)
    for blk in sorted(per):
        n, m = per[blk]
        flag = "" if m == 0 else "   <-- %d MISSING" % m
        print("   %-18s %3d estimates, %3d missing%s" % (blk, n, m, flag))
        for r in misses[blk][:4]:
            print("        e.g. " + ", ".join("%s=%s" % (k, v) for k, v in list(r.items())[:6]))
print()
print("TOTAL: %d estimates checked, %d not found in main.tex" % (total, miss_total))
