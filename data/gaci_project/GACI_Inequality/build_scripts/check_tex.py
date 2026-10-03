# -*- coding: utf-8 -*-
"""Static sanity checks on the assembled Overleaf main.tex."""
import io, os, re, collections

BS = chr(92)
D = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality\Overleaf_Inequality_20260918"
tex = io.open(os.path.join(D, "main.tex"), encoding="utf-8").read()
bib = io.open(os.path.join(D, "GACI_Inequality_refs.bib"), encoding="utf-8").read()

problems = []

# strip comment lines for structural checks
lines = tex.split("\n")


def strip_comment(ln):
    out, i = [], 0
    while i < len(ln):
        c = ln[i]
        if c == BS and i + 1 < len(ln):
            out.append(ln[i:i + 2]); i += 2; continue
        if c == "%":
            break
        out.append(c); i += 1
    return "".join(out)


code = "\n".join(strip_comment(l) for l in lines)

# 1. environment balance
stack = []
for m in re.finditer(BS + BS + r"(begin|end)\{([^}]+)\}", code):
    kind, env = m.group(1), m.group(2)
    if kind == "begin":
        stack.append((env, m.start()))
    else:
        if not stack:
            problems.append("unmatched \\end{%s}" % env)
        elif stack[-1][0] != env:
            problems.append("mismatch: \\begin{%s} ... \\end{%s}" % (stack[-1][0], env))
            stack.pop()
        else:
            stack.pop()
for env, pos in stack:
    problems.append("unclosed \\begin{%s} at char %d" % (env, pos))

# 2. tabular column counts
ncols_of = {"l": 1, "c": 1, "r": 1}
def brace_group(s, i):
    """s[i] == '{' -> return (content, index after closing brace), brace-balanced."""
    assert s[i] == "{"
    depth, j = 0, i
    while j < len(s):
        if s[j] == BS:
            j += 2; continue
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced")


for m in re.finditer(BS + BS + r"begin\{tabular\}", code):
    spec, after = brace_group(code, m.end())
    end = code.find(BS + "end{tabular}", after)
    bodytxt = code[after:end]
    # drop @{...} / p{...} / >{...} inserts before counting column letters
    bare, k = "", 0
    while k < len(spec):
        if spec[k] in "@>!<" and k + 1 < len(spec) and spec[k + 1] == "{":
            _, k = brace_group(spec, k + 1); continue
        if spec[k] == "{":
            _, k = brace_group(spec, k); continue
        bare += spec[k]; k += 1
    ncol = sum(1 for ch in bare if ch in "lcr")
    for rawrow in bodytxt.split(BS + BS):
        row = rawrow.strip()
        if not row or row.startswith(BS + "toprule") or row.startswith(BS + "midrule"):
            pass
        # count & not escaped, not inside \multicolumn span accounting
        amps = len(re.findall(r"(?<!" + BS + BS + r")&", row))
        spans = [int(x) for x in re.findall(BS + BS + r"multicolumn\{(\d+)\}", row)]
        cells = amps + 1 + sum(s - 1 for s in spans)
        stripped = re.sub(BS + BS + r"(toprule|midrule|bottomrule|addlinespace)", "", row).strip()
        if not stripped:
            continue
        if cells > ncol:
            problems.append("tabular{%s} (%d cols): row has %d cells -> %s" % (spec, ncol, cells, row[:70]))

# 3. citations resolve
keys = set(re.findall(r"@\w+\{([^,]+),", bib))
cited = set()
for m in re.finditer(BS + BS + r"cite[a-z]*\{([^}]*)\}", code):
    for k in m.group(1).split(","):
        cited.add(k.strip())
missing = sorted(cited - keys)
if missing:
    problems.append("citations with no bib entry: %s" % missing)

# 4. refs resolve
labels = set(re.findall(BS + BS + r"label\{([^}]*)\}", code))
refs = set()
for m in re.finditer(BS + BS + r"ref\{([^}]*)\}", code):
    refs.add(m.group(1))
badrefs = sorted(refs - labels)
if badrefs:
    problems.append("\\ref with no \\label: %s" % badrefs)

# 5. graphics present
for m in re.finditer(BS + BS + r"includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", code):
    f = m.group(1)
    if not os.path.exists(os.path.join(D, f)):
        problems.append("missing figure file: %s" % f)

# 6. stray % outside comments in table rows (would swallow a row)
for i, ln in enumerate(lines, 1):
    if "&" in ln and re.search(r"(?<!" + BS + BS + r")%", ln):
        problems.append("line %d: unescaped %% inside a table row -> %s" % (i, ln[:70]))

# 7. em-dash check (user rule) and math-mode $ balance
if chr(8212) in tex:
    problems.append("em-dash present in text")
if code.count("$") % 2:
    problems.append("odd number of $ (unbalanced math mode)")

print("cited keys        :", len(cited), " bib entries:", len(keys))
print("labels/refs       :", len(labels), "/", len(refs))
print("tables (tabular)  :", len(re.findall(BS + BS + r"begin\{tabular\}", code)))
print("figures           :", len(re.findall(BS + BS + r"includegraphics", code)))
print()
if problems:
    print("PROBLEMS (%d):" % len(problems))
    for p in problems:
        print("  -", p)
else:
    print("No structural problems found.")
