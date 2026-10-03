# -*- coding: utf-8 -*-
"""Make every string literal inside R(...) calls raw, except the ones that need a real newline escape."""
import pathlib, re
p = pathlib.Path("build_tex_2024.py"); L = p.read_text(encoding="utf-8").split("\n"); n = 0
BSN = "\\" + "n"   # literal backslash-n as it appears in the source
for i, l in enumerate(L):
    if not (l.startswith("R(") or re.match(r"^\s+r?\"", l)):
        continue
    if BSN in l or "\\\\caption" in l:
        continue   # keep the newline-carrying literals as normal strings
    new = re.sub(r'(?<=, )"', 'r"', l)          # second argument on the same line
    new = re.sub(r'^R\("', 'R(r"', new)         # first argument
    if new != l: n += 1
    L[i] = new
p.write_text("\n".join(L), encoding="utf-8", newline="\n"); print("lines changed:", n)
