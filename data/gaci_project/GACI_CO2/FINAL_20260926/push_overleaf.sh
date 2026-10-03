#!/usr/bin/env bash
# Push the 2026-09-26 completed version to the Overleaf project "GACI CO2" through Overleaf's git bridge
# and remove the files the completed version no longer uses.
# Run in Git Bash, or from Claude Code with:  ! bash "<this file>"
# Git asks for credentials once: username = git, password = your Overleaf git authentication token
# (Overleaf > Account settings > Git integration > Generate token).
#
# The project held 23 files in the download of 2026-09-26 07:14 (Downloads/GACI_CO2 (2).zip):
#   main_co2_nature_20260908.tex, main_co2_20260826.tex, co2_tables_20260826.tex, refs_co2.bib and 19 PNGs.
# After this script it holds 9 files:
#   main_co2_nature_20260908.tex  <- the completed text, kept under the existing name so the main-document
#                                    setting and the coauthors' comments and history stay attached
#                                    (rename to main_co2_nature_20260926.tex in Overleaf if you like)
#   refs_co2.bib, Figure1.png, Figure2_ab.png, CO2_SAF.png, ED_Fig1.png, ED_Fig2.png, ED_Fig3.png, ED_Fig4.png
set -e
FINAL="C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/GACI_CO2/FINAL_20260926"
SRC="$FINAL/overleaf_20260926"
WORK="$FINAL/overleaf_git"
PROJECT="https://git.overleaf.com/6a8ea9bfb81c1dc24c7aa7d0"

if [ ! -d "$WORK/.git" ]; then
  git clone "$PROJECT" "$WORK"
else
  git -C "$WORK" pull --rebase
fi
cd "$WORK"
echo "Files in the Overleaf project before the update:"; git ls-files

# 1. completed text under the existing main-document name, bibliography and the seven figures
cp "$SRC/main_co2_nature_20260926.tex" "$WORK/main_co2_nature_20260908.tex"
cp "$SRC/refs_co2.bib" "$WORK/"
for f in Figure1.png Figure2_ab.png CO2_SAF.png ED_Fig1.png ED_Fig2.png ED_Fig3.png ED_Fig4.png; do
  cp "$SRC/$f" "$WORK/"
done

# 2. superseded files, listed by name from the 2026-09-26 download
for f in main_co2_20260826.tex co2_tables_20260826.tex \
         CO2_airport_concentration.png CO2_attribution_bars.png CO2_decomp_waterfall.png \
         CO2_efficiency_curve.png CO2_gradient_baseline.png CO2_hetero_coefplot.png \
         CO2_map_attributed_2023.png CO2_map_carbonprice.png CO2_map_dlngaci.png \
         CO2_map_levels_2023.png CO2_map_mismatch_2023.png CO2_placebo_rf.png \
         CO2_rf_quintile.png CO2_saf_growth.png CO2_saf_scenarios.png \
         CO2_spill_decay.png CO2_spill_placebo.png CO2_temporal_coefplot.png; do
  if [ -f "$f" ]; then git rm -q "$f"; echo "removed $f"; fi
done

git add main_co2_nature_20260908.tex refs_co2.bib Figure1.png Figure2_ab.png CO2_SAF.png ED_Fig1.png ED_Fig2.png ED_Fig3.png ED_Fig4.png
git -c user.name="Sunbin Yoo" -c user.email="sunbinyoo.kyushu@gmail.com" commit -m "Completed version 2026-09-26: Junya comments, Longfei figures, Ray SAF figure, abstract 200 words, Methods 3,000 words, Supplementary Notes 2-3; superseded files removed"
git push
echo
echo "Pushed. Open Overleaf and Recompile; the main document setting is unchanged."
echo "Files now in the project:"; git ls-files
