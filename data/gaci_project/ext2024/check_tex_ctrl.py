# -*- coding: utf-8 -*-
"""Scan the built tex for control characters / tabs and for LaTeX macros that lost their backslash vs the 2023 version."""
import pathlib, re, collections
D = pathlib.Path(__file__).parent.parent / "TRA_rev20260902_ext2024"
t = (D / "main.tex").read_text(encoding="utf-8"); o = (D / "main_2023_version.tex").read_text(encoding="utf-8")
bad = [(i + 1, repr(l[:100])) for i, l in enumerate(t.split("\n")) if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\t]", l)]
print("control-char lines:", len(bad)); [print("  ", b) for b in bad[:20]]
# macro census: any \word appearing in old but with reduced count in new, or new bare words like 'extbf{' 'eta='
mo = collections.Counter(re.findall(r"\\[A-Za-z]+", o)); mn = collections.Counter(re.findall(r"\\[A-Za-z]+", t))
drop = {k: (mo[k], mn.get(k, 0)) for k in mo if mn.get(k, 0) < mo[k]}
print("macros with reduced count (old,new):", drop)
for pat in [r"(?<!\\)\bextbf\{", r"(?<!\\)\beta=", r"(?<!\\)\bpprox", r"(?<!\\)\bimes", r"(?<!\\)\bef\{", r"(?<!\\)\bathrm\{", r"(?<!\\)\bym\{", r"(?<!\\)\bmph\{"]:
    hits = re.findall(pat, t); print(pat, len(hits))
print("braces balanced:", t.count("{") - t.count("}"), "| begin/end table:", t.count(r"\begin{table}"), t.count(r"\end{table}"), "| figure:", t.count(r"\begin{figure}"), t.count(r"\end{figure}"))
