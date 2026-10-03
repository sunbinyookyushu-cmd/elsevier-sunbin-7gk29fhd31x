# -*- coding: utf-8 -*-
import re, sys, os
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "FINAL_20260908/main_co2_nature_20260908.tex"), encoding="utf-8").read()
BS = chr(92)
E = re.escape(BS)
def strip(t):
    t = re.sub(E + r"begin\{(table|figure)\}.*?" + E + r"end\{\1\}", "", t, flags=re.S)
    t = re.sub(E + r"begin\{equation\}.*?" + E + r"end\{equation\}", "", t, flags=re.S)
    t = re.sub(E + r"\[.*?" + E + r"\]", "", t, flags=re.S)
    t = re.sub(r"%.*", "", t)
    t = re.sub(E + r"(cite[pt]?|ref|label)\{[^}]*\}", "", t)
    t = re.sub(E + r"[a-zA-Z]+\*?", "", t); t = re.sub(r"[{}$&]", "", t)
    return len(t.split())
def sec(a, b):
    i = s.find(a); j = s.find(b, i + 1); return s[i:j]
S = BS + "section*{"
print("abstract", strip(sec(BS + "begin{abstract}", BS + "end{abstract}")))
print("main", strip(sec(S + "Main}", S + "Results")))
print("results", strip(sec(S + "Results", S + "Discussion")))
print("discussion", strip(sec(S + "Discussion", S + "Methods")))
print("methods", strip(sec(S + "Methods", S + "Extended Data")))
print("results subsections:")
for m in re.finditer(E + r"subsection\*\{([^}]*)\}", sec(S + "Results", S + "Discussion")):
    print("  ", len(m.group(1)), "chars:", m.group(1).replace("\n", " "))
a = pd.read_csv(os.path.join(HERE, "_allest_results_cl.csv")); print(a[a.est == "HeritageIV"].round(3).to_string())
print("percent:", len(re.findall(r"\bpercent\b", s)), "| %:", s.count(BS + "%"))
for w in ["decarboni[sz]", "neighbo(?:u)?r", "kilomet(?:re|er)", "standardi[sz]", "organi[sz]", "analy[sz]"]:
    print(w, sorted(set(re.findall(w + r"\w*", s)))[:10])
