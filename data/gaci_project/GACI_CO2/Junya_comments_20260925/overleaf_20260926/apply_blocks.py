# -*- coding: utf-8 -*-
"""Apply paste_blocks_20260925.tex (BLOCK 1-13) to the 9/26 Overleaf download."""
import re, sys, shutil, pathlib

SCR = pathlib.Path(r"C:\Users\sunbi\AppData\Local\Temp\claude\C--Users-sunbi\3da24588-1633-4eb2-8003-544af31cba97\scratchpad")
J = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2\Junya_comments_20260925")
SRC = SCR / "z2" / "main_co2_nature_20260908.tex"
OUT = SCR / "z2" / "main_co2_nature_20260926.tex"

tex = SRC.read_text(encoding="utf-8")
blocks_raw = (J / "paste_blocks_20260925.tex").read_text(encoding="utf-8")

# ---- parse blocks: split on "% BLOCK n" headers; body = non-comment lines ----
parts = re.split(r"^% -{50,}\n% BLOCK (\d+)", blocks_raw, flags=re.M)
blocks = {}
for i in range(1, len(parts), 2):
    n = int(parts[i]); body = parts[i + 1].split(chr(10), 1)[1]
    blocks[n] = body

def payloads(n):
    """Return list of non-comment chunks (separated by comment-only runs) in block n."""
    lines = blocks[n].split("\n")
    chunks, cur = [], []
    for ln in lines:
        if ln.startswith("%"):
            if cur:
                chunks.append("\n".join(cur).strip("\n")); cur = []
        else:
            cur.append(ln)
    if cur:
        chunks.append("\n".join(cur).strip("\n"))
    return [c for c in chunks if c.strip()]

log = []
def replace_once(old_pat, new, label, regex=False):
    global tex
    if regex:
        m = list(re.finditer(old_pat, tex, flags=re.S))
        assert len(m) == 1, f"{label}: {len(m)} matches"
        tex = tex[:m[0].start()] + new + tex[m[0].end():]
    else:
        assert tex.count(old_pat) == 1, f"{label}: {tex.count(old_pat)} matches"
        tex = tex.replace(old_pat, new)
    log.append(f"OK  {label}")

def para_containing(anchor_start, anchor_end):
    """Return full paragraph (line) that starts with anchor_start and contains anchor_end."""
    for ln in tex.split("\n"):
        if ln.startswith(anchor_start) and anchor_end in ln:
            return ln
    raise AssertionError(f"paragraph not found: {anchor_start[:40]}")

def whole_table(label):
    i = tex.index("\\label{" + label + "}")
    b = tex.rfind("\\begin{table}", 0, i)
    e = tex.index("\\end{table}", i) + len("\\end{table}")
    return tex[b:e]

# BLOCK 1
p1 = payloads(1); assert len(p1) == 1
old = "The estimation sample covers 184 countries over 1996--2023, comprising 4,634 country-year observations."
replace_once(old, p1[0], "BLOCK 1 (182 countries + sumstat ref)")

# BLOCK 2
p2 = payloads(2); assert len(p2) == 2, p2
replace_once("sea market access, respectively,", p2[0], "BLOCK 2a (eq:seama ref)")
replace_once("(184 clusters)", p2[1], "BLOCK 2b (182 clusters)")

# BLOCK 3
p3 = payloads(3); assert len(p3) == 1
old = para_containing("To address this endogeneity, we instrument connectivity using a Feyrer-type shifter", "declines only slightly from 120.1 to 105.8.")
replace_once(old, p3[0], "BLOCK 3 (instrument formulas)")

# BLOCK 4
p4 = payloads(4); assert len(p4) == 1
old = para_containing("Six further checks reinforce our findings", "yielded weak first stages ($F$ of 1.0 and 5.6).")
replace_once(old, p4[0], "BLOCK 4 (further checks / caveat)")

# BLOCK 5: three lines from "Finally, we consider other potential instruments" to "post-2010 first stage."
p5 = payloads(5); assert len(p5) == 1
s = tex.index("Finally, we consider other potential instruments, but restrict their use")
e = tex.index("post-2010 first stage.", s) + len("post-2010 first stage.")
old = tex[s:e]
assert old.count("\n") <= 3, old
replace_once(old, p5[0], "BLOCK 5 (accident IV, heritage dropped)")

# BLOCK 6
p6 = payloads(6); assert len(p6) == 1
old = para_containing("We initially explored an instrumental variable strategy for this airport-level analysis.", "rather than strictly causal effects.")
replace_once(old, p6[0], "BLOCK 6 (airport IV paragraph)")

# BLOCK 7
p7 = payloads(7); assert len(p7) == 1
old = para_containing("Finally, we implement robust inference procedures", "exceeds the true empirical estimate.")
replace_once(old, p7[0], "BLOCK 7 (spatial weak-IV paragraph)")

# BLOCK 8, 9, 10: whole tables
for n, lab in [(8, "tab:spillover"), (9, "tab:exclusion2"), (10, "tab:accident_iv")]:
    p = payloads(n); assert len(p) == 1, (n, len(p))
    replace_once(whole_table(lab), p[0], f"BLOCK {n} (table {lab})")

# BLOCK 13 (a) Panel E rows
p13 = payloads(13); assert len(p13) == 3, p13
s = tex.index("Panel E. Development-channel controls added sequentially")
hdr_end = tex.index("\n", tex.index(" & 2SLS & & KP $F$ & $N$ \\\\", s)) + 1
e = tex.index("\\bottomrule", hdr_end)
old_rows = tex[hdr_end:e]
assert old_rows.count("\\\\") == 7, old_rows
tex = tex[:hdr_end] + p13[0].rstrip("\n") + "\n" + tex[e:]
log.append("OK  BLOCK 13a (Panel E rows, VEN fix)")
# (b) note
replace_once("Panel D: terciles of 1996 capacity-weighted GACI.", p13[1], "BLOCK 13b (exclusion note VEN)")
# (c) results text
replace_once("between 4.4 and 4.6 when income, trade, urbanisation,", p13[2], "BLOCK 13c (4.4-4.7 in Results)")

# BLOCK 11: sumstat table first under Supplementary Tables
p11 = payloads(11); assert len(p11) == 1
anchor = "\\section*{Supplementary Tables}\n\\setcounter{table}{0}\n\\renewcommand{\\tablename}{Supplementary Table}\n"
assert tex.count(anchor) == 1
tex = tex.replace(anchor, anchor + "\n" + p11[0] + "\n")
log.append("OK  BLOCK 11 (new Supplementary Table sumstat)")

# BLOCK 12: bib entries (they are commented in the block file; strip leading "% ")
bib_lines = [ln[2:] if ln.startswith("% ") else ln[1:] for ln in blocks[12].split("\n") if ln.startswith("%") and not ln.startswith("% -") and "refs_co2.bib" not in ln]
bib_add = "\n".join(bib_lines).strip() + "\n"
assert "@article{feyrer2019" in bib_add and "@techreport{bertoli2016" in bib_add
BIB = SCR / "z2" / "refs_co2.bib"
bib = BIB.read_text(encoding="utf-8")
if "feyrer2019" not in bib:
    bib = bib.rstrip("\n") + "\n\n" + bib_add
    BIB.write_text(bib, encoding="utf-8")
    log.append("OK  BLOCK 12 (bib: feyrer2019, bertoli2016 appended)")

OUT.write_text(tex, encoding="utf-8")
print("\n".join(log))
print("written", OUT)
