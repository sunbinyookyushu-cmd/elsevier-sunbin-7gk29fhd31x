# -*- coding: utf-8 -*-
import pathlib
BS = "\\"
p = pathlib.Path("build_tex_2024.py"); s = p.read_text(encoding="utf-8")
old = ' r"' + BS + 'nyears. The gaps'
assert s.count(old) == 1, s.count(old)
s = s.replace(old, ' "' + BS + 'nyears. The gaps'); p.write_text(s, encoding="utf-8", newline="\n"); print("tex builder fixed")
g = pathlib.Path("_design_rankbump/gen_slope_dc_2024.py"); L = g.read_text(encoding="utf-8").split("\n")
hit = 0
for i, l in enumerate(L):
    if "ltxt = " in l and "u201900" in l:
        L[i] = l.replace(BS + "u201900'", BS + "u2019{str(i[\"alty\"])[2:]}'"); hit += 1; print("label line:", L[i].strip()[:130])
assert hit == 1
g.write_text("\n".join(L), encoding="utf-8", newline="\n")
