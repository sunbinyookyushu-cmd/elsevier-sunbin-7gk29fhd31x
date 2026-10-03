# -*- coding: utf-8 -*-
"""Mechanical fixes found in the 2026-09-26 final read-through."""
import pathlib
D = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2\Junya_comments_20260925\overleaf_20260926")
P = D / "main_co2_nature_20260926.tex"
t = P.read_bytes().decode("utf-8")
log = []
def rep(old, new, label, count=1):
    global t
    n = t.count(old)
    assert n == count, f"{label}: found {n}, expected {count}"
    t = t.replace(old, new)
    log.append(f"OK  {label}")

# 1 date line
rep(r"\date{Nature-format draft, candidate of 8 September 2026}",
    r"\date{Nature-format draft, 26 September 2026}", "date line")

# 2 owner tags in section headers
rep(r"\section*{Discussion [Jinwoo]}", r"\section*{Discussion}", "Discussion header tag")
rep(r"\subsection*{Estimation [Junya]}", r"\subsection*{Estimation}", "Estimation tag")
rep(r"\subsection*{Instruments and validity [Junya]}", r"\subsection*{Instruments and validity}", "Instruments tag")
rep(r"\subsection*{Spatial Econometric Specifications and Spillover Effects [Junya]}",
    r"\subsection*{Spatial Econometric Specifications and Spillover Effects}", "Spatial tag")
rep(r"\subsection*{Mediation analysis [Junya]}", r"\subsection*{Mediation analysis}", "Mediation tag")
rep(r"\subsection*{Attribution and fuel-switching scenarios [Ray and Lisa]}",
    r"\subsection*{Attribution and fuel-switching scenarios}", "Attribution tag")

# 3 Discussion spacing
rep("CO$_2$ by 5.35 percent.Changes in aircraft gauge", "CO$_2$ by 5.35 percent. Changes in aircraft gauge", "missing space")
rep("rather than the addition of a single route.  A one percent", "rather than the addition of a single route. A one percent", "double space 1")
rep("are not individually significant.  The 0.29 percent", "are not individually significant. The 0.29 percent", "double space 2")
rep("common regional shocks.  The social-cost estimate", "common regional shocks. The social-cost estimate", "double space 3")
rep(r"under its 2\% Ramsey approach \citep{epa2023}.  For the fuel-switching", r"under its 2\% Ramsey approach \citep{epa2023}. For the fuel-switching", "double space SAF")

# 4 Discussion TODO cite 1: same claim and sources as in Main
rep("we identify network development as an important source [TODO cite: aviation decarbonisation pathways].",
    r"we identify network development as an important source \citep{bergero2023,dray2022}.", "TODO cite decarbonisation")

# 5 Table 1 note: instrument wording now follows eq:feyrer
rep("Panels B--E instrument log GACI with the Feyrer interaction of world aviation technology and 1996 air-versus-sea geography (Methods).",
    r"Panels B--E instrument log GACI with the Feyrer interaction of the world aviation index and log 1996 air market access, with log sea market access as a control (Methods, equation~\ref{eq:feyrer}).", "Table 1 note IV wording")

P.write_bytes(t.encode("utf-8"))
print("\n".join(log))
