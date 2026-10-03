# GACI x Inequality -- Overleaf package (2026-09-18, growth block added 2026-09-19)

Source: `GACI_Inequality/main_inequality_v2.tex` + `appendix_inequality_v2.tex`
(polished 2026-09-18; v1 files kept unchanged for comparison).
Format copied from the companion GACI-trade Overleaf project
(`GACI/TRA_rev20260902_ext2024/main.tex`).

## Upload to Overleaf
New Project -> Upload Project -> `GACI_Inequality_Overleaf_20260918.zip`.
Main document: `main.tex`. Compiler: pdfLaTeX (pdflatex -> bibtex -> pdflatex x2).

## Files
- `main.tex` -- self-contained: elsarticle `[review,3p,times,authoryear]`,
  bibliography embedded via `filecontents*`, all 37 tables inline.
- `fig_horizon.png`, `fig_rf_quintile.png`, `fig_map_base_gacimax.png`,
  `fig_map_implied_gini.png` -- the four figures (maps built by `11_maps.py` in the
  shared `_mapstyle.py` style of the trade paper; `fig_map_actual_gini.png` is an
  unused alternative kept in `GACI_Inequality/`).
- `GACI_Inequality_refs.bib` -- standalone copy of the same bibliography.

## Contents
Body: 13 tables, 4 figures (2 maps). The growth block (`Growth and its incidence`,
after the main results) adds Table `tab:growth` (GDP per capita and group average
incomes, same specifications as the main table) and Table `tab:growth_decomp`
(level and share components of each group's income gain).
Appendix A Additional estimates (7 tables): Gini in points; absolute redistribution;
distributional shares for hub quality and total connectivity; separate 2SLS by
baseline income tercile; distributional shares by income tercile; continent-specific
2SLS for both measures; survey-based World Bank outcomes.
Appendix B Timing and instrument diagnostics (9 tables): leads; reduced form by
continent; Open Skies event study (connectivity and inequality outcomes);
over-identified 2SLS with Open Skies plus Feyrer; complete long-difference battery;
first stage by continent with SE; leave-one-continent-out under continent x year FE;
reduced form by baseline quintile.
Appendix Growth outcomes (6 tables): identification diagnostics; lags and leads;
long and stacked differences; heterogeneity and control sensitivity; inequality
conditional on measured income per head; total GDP as an outcome.
Appendix C Country-level quantities (2 tables): implied contribution for all 103
countries; 2019-2020 connectivity change for all 115 countries.
Plus a `Data and code availability` section.

## Coverage check
Every estimate produced by scripts 01-08 now appears in `main.tex`:
1,108 coefficient/standard-error pairs matched (767 before the growth block, 341 added) (coefficient and its SE within 140
characters of each other), 1,143 estimates matched on the loose check. 0 unmatched.
Each appendix table has a one-paragraph interpretation before it.

## Changes from main_inequality_v1.tex
1. `article` -> `elsarticle [review,3p,times,authoryear]`; `\journal{Transportation Research Part A}`.
2. `\maketitle` + abstract -> `\begin{frontmatter}` with `\author`/`\ead`/`\address`
   and a `\begin{keyword}` block. `\linenumbers` on.
3. Elsevier Harvard reference formatting and the `\@makecaption` override, both from the trade paper.
4. All `\input{...}` inlined (37 tables) -- no subdirectories needed.
5. Appendix added (24 tables + interpretation); 9 cross-references added in the body.
6. 2026-09-19: growth outcomes added from `09_gdp.do` (GDP per capita, total GDP,
   WID average incomes overall and by group, top-to-bottom ratio), 341 new estimates
   in `_gdp_results.csv` and sheet `T11_growth_gdp` of the results workbook.

## Bugs fixed while assembling (all in `10_assemble.py`; backups kept)
- `"NA"` is the North America continent code, but `pd.read_csv` read it as a missing
  value. Consequences, all now fixed by `keep_default_na=False, na_values=["", "."]`:
  * `tab_contribution.tex` had no North America row and the regional counts summed to
    101 against an `All` row of 103.
  * `tab_diag.tex` printed `--` for the North America first stage.
  * `tab_hetero.tex` Panel D omitted North America (the continent list was also
    hardcoded to six entries; `"NA"` added).
- `tab_sumstat.tex`: `10%` and `50%` were unescaped, so LaTeX read the rest of those
  two rows as a comment and dropped them. The assembler now escapes `%`.
- Backups: `_bak_10_assemble_preNAfix.py`, `_bak_tables_preNAfix/`,
  `_bak_main_inequality_v1_preappendix.tex`. Re-running `10_assemble.py` reproduces
  every other table byte-for-byte; only these four changed.

## Not done
- Compilation was not verified locally: the MiKTeX install on this PC is broken
  (missing `formats.ini` and the `miktex-config-2.9` package). Static checks only
  (environment balance, column counts, citations, refs, figures, math mode).
- `\ead{[email]}`, `[Co-author]`, `[Affiliation]` are still placeholders.
- 9 references; no literature-review section; no discussion section. Deferred on
  purpose: this pass was results only.
