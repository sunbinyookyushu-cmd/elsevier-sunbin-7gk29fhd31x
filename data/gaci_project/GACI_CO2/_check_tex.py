# -*- coding: utf-8 -*-
"""Static LaTeX sanity checks for the assembled manuscript (no compiler available locally)."""
import re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
BS = chr(92)
path = sys.argv[1]
s = open(path, encoding="utf-8").read()
s = re.sub(r"(?<!" + BS + BS + ")%.*", "", s)
b = re.findall(BS + BS + r"begin" + BS + r"{(" + BS + r"w+" + BS + r"*?)" + BS + r"}", s)
e = re.findall(BS + BS + r"end" + BS + r"{(" + BS + r"w+" + BS + r"*?)" + BS + r"}", s)
cb, ce = Counter(b), Counter(e)
print("env mismatch:", {k: (cb[k], ce[k]) for k in set(cb) | set(ce) if cb[k] != ce[k]})
print("brace balance:", s.count("{") - s.count("}"))
bad = 0
pat = BS + BS + r"begin" + BS + r"{tabular" + BS + r"}" + BS + r"{([^}]*)" + BS + r"}(.*?)" + BS + BS + r"end" + BS + r"{tabular" + BS + r"}"
for m in re.finditer(pat, s, re.S):
    ncol = len(re.findall(r"[lcr]", m.group(1)))
    for row in m.group(2).split(BS + BS + BS + BS):
        row = row.strip()
        if not row or row.startswith(BS + "toprule") or row.startswith(BS + "midrule") or row.startswith(BS + "bottomrule") or row.startswith(BS + "cmidrule"):
            continue
        row2 = re.sub(BS + BS + r"(top|mid|bottom)rule", "", row).strip()
        if not row2:
            continue
        if BS + "multicolumn" in row2:
            span = sum(int(x) for x in re.findall(BS + BS + r"multicolumn" + BS + r"{(" + BS + r"d+)" + BS + r"}", row2))
            nmc = len(re.findall(BS + BS + r"multicolumn", row2))
            cells = row2.count("&") + 1
            if cells - nmc + span != ncol:
                bad += 1; print("  multicolumn row:", cells - nmc + span, "vs", ncol, ":", row2[:70].replace(chr(10), " "))
            continue
        if row2.count("&") + 1 != ncol:
            bad += 1; print("  row cols", row2.count("&") + 1, "vs", ncol, ":", row2[:70].replace(chr(10), " "))
print("tabular rows with wrong column count:", bad)
print("unmatched $ (odd count lines):", sum(1 for ln in s.splitlines() if ln.count("$") % 2 == 1))
