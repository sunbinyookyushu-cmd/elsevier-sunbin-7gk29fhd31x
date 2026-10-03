# -*- coding: utf-8 -*-
"""Insert appendix cross-references into the body of main_inequality_v1.tex."""
import io, os, sys

SRC = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality\main_inequality_v1.tex"
t = io.open(SRC, encoding="utf-8").read()

PATCHES = [
    # 1. main results -> levels + abs_red appendix tables
    ("The three measures are on different scales, and what carries over is the common pattern: positive in OLS, larger in 2SLS, and present for both instruments.",
     "The three measures are on different scales, and what carries over is the common pattern: positive in OLS, larger in 2SLS, and present for both instruments. Table~\\ref{tab:a_levels} reports the same specifications with the Gini in points, and Table~\\ref{tab:a_absred} reports absolute redistribution as an outcome."),
    # 2. heterogeneity -> separate tercile regressions
    ("The separate regressions confirm that the low-income first stage is weak ($F=3.6$), so the U-shape rests mainly on the contrast between middle and high income.",
     "The separate regressions confirm that the low-income first stage is weak ($F=3.6$), so the U-shape rests mainly on the contrast between middle and high income (Table~\\ref{tab:a_inc3split})."),
    # 3. tails -> other measures and tercile interactions
    ("Hypothesis~2 is supported for the bottom half and the top decile, and rejected for the top percentile.",
     "Hypothesis~2 is supported for the bottom half and the top decile, and rejected for the top percentile. Table~\\ref{tab:a_tails_other} reports the same outcomes for hub quality and total connectivity, and Table~\\ref{tab:a_tails_inc3} reports them by baseline income tercile."),
    # 4. horizon -> leads
    ("A joint specification with current and three-year-ahead connectivity is uninformative because the two instruments are nearly collinear ($F=0.3$).",
     "A joint specification with current and three-year-ahead connectivity is uninformative because the two instruments are nearly collinear ($F=0.3$); Table~\\ref{tab:a_leads} reports the lead coefficients."),
    # 5. diagnostics -> reduced form by continent
    ("The pooled first stage is positive because it combines within-continent and between-continent variation.",
     "The pooled first stage is positive because it combines within-continent and between-continent variation, and the reduced form inherits the same sign pattern (Table~\\ref{tab:a_rfcont})."),
    # 6. Open Skies -> event study tables and over-identified IV
    ("As an instrument, Open Skies has $F=2.1$.",
     "The event-study coefficients are reported in Tables~\\ref{tab:a_es_conn} and \\ref{tab:a_es_ineq}. As an instrument, Open Skies has $F=2.1$; used together with the Feyrer instrument in an over-identified specification it gives a market-Gini coefficient of $0.427$ (Table~\\ref{tab:a_osfeyrer})."),
    # 7. contribution -> country table
    ("The 2SLS-implied contributions therefore exceed the observed changes for most regions and reach $22$ points for Korea and Turkey, which is not a plausible ceteris paribus quantity.",
     "The 2SLS-implied contributions therefore exceed the observed changes for most regions and reach $22$ points for Korea and Turkey, which is not a plausible ceteris paribus quantity. Table~\\ref{tab:a_country} reports the country-level detail."),
    # 8. COVID -> country table
    ("The available inequality data for 2020--2023 do not show a corresponding fall.",
     "The available inequality data for 2020--2023 do not show a corresponding fall. Table~\\ref{tab:a_covid} reports the 2019 to 2020 change for each country."),
]

fail = []
for old, new in PATCHES:
    if old not in t:
        fail.append(old[:60])
        continue
    if t.count(old) != 1:
        fail.append("NOT UNIQUE: " + old[:60])
        continue
    t = t.replace(old, new)

if fail:
    print("FAILED anchors:")
    for f in fail:
        print("  -", f)
    sys.exit(1)

io.open(SRC, "w", encoding="utf-8", newline="\n").write(t)
print("patched %d cross-references into main_inequality_v1.tex" % len(PATCHES))
