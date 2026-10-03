# GACI_CO2_presentation.pptx rebuild kit (2026-09-01, updated 2026-09-02)

- `build_co2_deck.py` : generates a 61-slide `GACI\GACI_CO2_presentation.pptx` with python-pptx.
  Paths are now self-contained (MEDIA -> `media_from_gaci_pptx\` here). Run it FROM this folder
  (it imports `patch_saf_slide.py`). CAUTION: the shipped deck is the user-upgraded 62-slide
  version (extra full-bleed rank chart at slide 33); a full rebuild drops that slide, so prefer
  in-place patches (see below) unless you intend a from-scratch rebuild.
- `media_from_gaci_pptx\` : images extracted from GACI_presentation.pptx (pipeline, formulas, maps...).
- `patch_saf_slide.py` (2026-09-02) : in-place patch of the SAF slide (slide 57 of the 62-slide deck).
  Replaced the QR code / "LIVE DEMO" simulator box with a plain static version: levels figure
  `GACI_CO2\CO2_saf_levels.png` (made by `GACI_CO2\17_saf_levels_fig.py`) on the left, and a
  "how the scenario is computed" box (E(s,r) = 838 Mt x [1 - s x r]) plus a native editable table
  (2023/2035/2050 x r = 50/65/80%, CO2 saved, % of the 356 Mt bought back) on the right.
  Writes a timestamped backup before saving; asserts the LIVE DEMO box exists, so it runs once.
  `build_co2_deck.py` imports `saf_right_panel` / `CAPTION` from it, so rebuild and patch match.
  Backup of the pre-patch deck: `GACI\GACI_CO2_presentation_backup_20260902_1317_preSAFpatch.pptx`.
- `saf_simulator.html`, `saf_qr.png` : the retired interactive SAF Buy-Back Simulator
  (artifact https://claude.ai/code/artifact/138b2cc7-2e31-4bba-a55b-81da58da6146) and its QR.
  No longer referenced by the deck or the script; kept for the record.
- Render check used PowerPoint COM: open pptx, `Slides(n).Export(png, "PNG", 2400, 1350)`.
- `make_speech_script.py` : generates `GACI\GACI_CO2_presentation_script.docx`, the slide-by-slide
  English speaking script (62 slides / ~55-57 min, pacing table + 45-min skip list, stage
  directions in grey italics). Edit the SLIDES list and rerun. Slide 57 text rewritten 2026-09-02
  (formula walk-through + table, no QR/simulator mention).

## 2026-09-03: regression + ranking slides (`add_regression_slides.py`)
- In-place insertion of 8 slides into the 62-slide deck -> 70 slides; ALL footers renumbered to
  'i / 70' (actual slide index). Backup: `GACI\GACI_CO2_presentation_backup_20260903_*_preRegSlides.pptx`.
- New slides (final numbering): 16 CO2 top-15 emitters 2023 (Korea 15th highlighted) | 35 airport GACI
  top 15 + Korean airports (ICN 24th) | 39 country ranking: hub quality (cwm, the regressor) vs GACI sum
  (Korea 19th vs 44th) | 43 MODEL: equation (1) + variables + why-OLS-fails (KAIST-deck style) |
  46 ESTIMATION: 2SLS step by step with first stage pi=0.128 (0.010), KP F 153.6, RF 0.726, beta 5.669 |
  50 Table 1 main (OLS / 2SLS / sum-max-mean, 6 outcomes) | 56 Table 2 heterogeneity + temporal |
  59 Table 3 spillovers (Panel A + margins).
- Numbers from co2_tables_20260826.tex; first stage / RF re-run in pyfixest (2SLS identical).
- Tables are native (editable). `endsz()` sets a:endParaRPr size so empty cells do not inflate rows.
- Asserts the deck is unpatched (no 'ESTIMATING EQUATION' kicker): to rerun, restore the backup first.
- NOT updated: `GACI_CO2_presentation_script.docx` (speech script still 62-slide numbering).
- `add_arithmetic_slide.py` (2026-09-03, later): +1 slide -> 71. Slide 61 'How much did GACI rise, and how
  much CO2 is that?' right after the 06 divider: 3-step flow (GACI median +8% / emissions-weighted +21%,
  43 of 184 fell; x beta 5.67 with counterfactual formula; world CO2 457 -> 838 Mt, +356 Mt attributed =
  42.5% of 2023 = ~94% of the net increase) + country table (Korea 0.88->1.79 +104%, CO2 7.1->14.4 +103%,
  attributed 14.1 Mt 98%; CHN/ARE/TUR/IND/JPN/USA/GBR/DEU; World row) + 'Read with care' caveats
  (marginal elasticity extrapolated, saturation to 100% for big movers, negative rows). Imports helpers
  from add_regression_slides.py. Backup `..._preArith.pptx`. PDF re-exported.
