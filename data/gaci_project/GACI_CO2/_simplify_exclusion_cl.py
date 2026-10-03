# -*- coding: utf-8 -*-
"""Simplify the exclusion-restriction presentation in the clustered template:
Methods = three core tests that pass + one sentence pointing to the remaining
checks and two caveats; Discussion limitation sentence shortened."""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "main_co2_nature_20260903_cl_template.tex")
s = open(p, encoding="utf-8").read()
BS = chr(92)
a = s.index(BS + "subsection*{Exclusion-restriction diagnostics [Junya]}")
b = s.index(BS + "subsection*{Spillover design [Junya]}")
new = r"""\subsection*{Exclusion-restriction diagnostics [Junya]}
The exclusion restriction requires that the instrument affects aviation
CO$_2$ only through air connectivity. Three tests address it directly, and
all three pass (Extended Data Table~\ref{tab:exclusion}, Panels A, C and D;
Extended Data Fig.~\ref{fig:placeborf}). First, non-aviation emissions do
not respond to the instrument: the reduced form on total territorial fossil
CO$_2$ excluding domestic aviation is 0.05 (s.e.\ 0.12) against 0.73 (s.e.\
0.16) for aviation CO$_2$, so a general development channel that would
raise all emissions is rejected. Second, the effect runs through air
geography rather than geography in general: when the aviation-technology
cycle is interacted with 1996 sea market access instead of air market
access and both interactions are entered, the sea term has a reduced form
of 0.08 (s.e.\ 0.30) while the air term retains 0.64 (s.e.\ 0.22). Third,
where the instrument cannot move connectivity it does not move emissions:
in the top tercile of baseline connectivity the first stage is absent
($F$ = 0.2) and the reduced form on CO$_2$ is 0.10 (s.e.\ 0.19), against
2.22 and 0.41 in the lower terciles.

Six further checks are reported in Extended Data Table~\ref{tab:exclusion}
and Supplementary Table~\ref{tab:exclusion2}: development-channel controls
(the elasticity stays between 4.7 and 4.9), alternative technology series
and distance-decay exponents (5.8 to 6.1), leads of the instrument
(uninformative, because the technology index is a smooth trend), the
Hansen test against the tourism-heritage instrument (rejects at 5 percent,
as expected for an instrument with different compliers that fails the
stress test), a horse race against rival global cycles, and the comparison
of heteroskedasticity-robust and clustered errors. Two of these leave
caveats that we state rather than resolve: coal and cement CO$_2$ rise
with the instrument (0.90 and 0.67), indicating some recomposition of
non-aviation emissions in countries whose air access improved, and the
aviation cycle cannot be separated statistically from world GDP and trade
cycles interacted with the same geography (time-series correlations of
0.82 and 0.84), so the aviation-specific content of the identifying
variation rests on the air-versus-sea contrast of the second test rather
than on the cycle itself. Alternative instrument constructions that would
avoid these caveats, the air-minus-sea advantage interacted with the
cycle and the air interaction with the sea interaction as a control, have
no usable first stage ($F$ of 1.0 and 3.0).

"""
s = s[:a] + new + s[b:]
old = ("The instrument's aviation-specific content\ncannot be separated statistically from world income or trade growth\ninteracted with the same geography; its validity rests on the air-versus-sea\ngeography contrast, on the absence of a response in total non-aviation\nemissions, and on the zero reduced form where the first stage is absent,\nwhile sectoral non-aviation emissions do shift in both directions\n(Methods).")
assert old in s, "discussion sentence not found"
s = s.replace(old, "The instrument passes the three\ndirect exclusion tests, but its aviation-specific content cannot be\nseparated statistically from world income and trade cycles interacted\nwith the same geography, and coal and cement emissions co-move with it\n(Methods).")
open(p, "w", encoding="utf-8").write(s)
print("simplified; methods block chars:", len(new))
