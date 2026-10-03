# -*- coding: utf-8 -*-
"""v1 vs v2 polish check: numbers, labels/refs, citations invariant; style rules on v2."""
import io, os, re, collections

D = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
BS = chr(92)


def rd(n):
    return io.open(os.path.join(D, n), encoding="utf-8").read()


def prose(t):
    # drop table floats (their content is identical \input lines anyway) and comments
    t = re.sub(BS + BS + r"begin\{table\}.*?" + BS + BS + r"end\{table\}", " ", t, flags=re.S)
    return "\n".join(l for l in t.split("\n") if not l.strip().startswith("%"))


def nums(t):
    return collections.Counter(re.findall(r"(?<![\w.])-?\d+(?:[.,]\d+)*(?![\w])", t))


def keys(t, cmd):
    out = collections.Counter()
    for m in re.finditer(BS + BS + cmd + r"\{([^}]*)\}", t):
        for k in m.group(1).split(","):
            out[k.strip()] += 1
    return out


for a, b in [("main_inequality_v1.tex", "main_inequality_v2.tex"),
             ("appendix_inequality.tex", "appendix_inequality_v2.tex")]:
    t1, t2 = rd(a), rd(b)
    p1, p2 = prose(t1), prose(t2)
    print("=" * 70)
    print("%s  ->  %s" % (a, b))
    print("words (prose): %d -> %d" % (len(p1.split()), len(p2.split())))
    n1, n2 = nums(p1), nums(p2)
    lost = {k: v for k, v in (n1 - n2).items()}
    new = {k: v for k, v in (n2 - n1).items()}
    print("numbers in v1 prose missing from v2:", lost if lost else "none")
    print("numbers new in v2 prose            :", new if new else "none")
    for cmd, lab in [("label", "labels"), ("ref", "refs"), ("cite[pt]?", "cites")]:
        k1, k2 = keys(t1, cmd), keys(t2, cmd)
        d = (k1 - k2) + (k2 - k1)
        print("%-7s v1=%d v2=%d  diff: %s" % (lab, sum(k1.values()), sum(k2.values()), dict(d) if d else "none"))
    print("input{} lines identical:", sorted(re.findall(BS + BS + r"input\{[^}]*\}", t1)) == sorted(re.findall(BS + BS + r"input\{[^}]*\}", t2)))
    # style rules on v2
    print("-- style scan v2 --")
    print("  em-dash:", t2.count(chr(8212)), "| '---' in prose:", len(re.findall(r"(?<!-)---(?!-)", p2)))
    emph = re.findall(BS + BS + r"(emph|textit|textbf)\{[^}]*\}", p2)
    print("  emph/textit/textbf in prose:", [e for e in emph] if emph else "none (hypothesis labels are inside quote blocks: %d)" % len(re.findall(BS + BS + r"textbf\{Hypothesis", t2)))
    banned = ["footprint", "surge", "bites", "wins", "loses", "pays", "not a plausible", "reveals", "at the bottom\\.",
              "mirror image", "carry no information", "the instruments fail", "it has no power", "credible",
              "unequalising", "distributional cost", "benefit rural", "fragility", "whose inequality", "in its own right",
              "roughly", "simple question", "deserve emphasis", "picture"]
    hits = {w: len(re.findall(w, p2, re.I)) for w in banned}
    hits = {k: v for k, v in hits.items() if v}
    print("  flagged words remaining:", hits if hits else "none")
