# -*- coding: utf-8 -*-
import pathlib, re, zipfile, glob, os
G = pathlib.Path(__file__).parent.parent; D = G / "TRA_rev20260902_ext2024"; os.chdir(D)
t = (D / "main.tex").read_text(encoding="utf-8")
old = "Second, the geography is stable across the three panels: the same countries shade in the same direction under all three connectivity measures, restating in map form the stability of the world totals."
pat = re.compile(r"\s+".join(re.escape(p) for p in old.split())); assert len(pat.findall(t)) == 1
new = ("Second, the geography is broadly stable across the three panels: most countries shade in the same direction under all three connectivity "
       "measures, restating in map form the stability of the world totals; the visible exceptions are the United States and Russia, whose single "
       "largest gateway lost ground on the maximum-hub measure even as their capacity-weighted hub quality rose.")
t = pat.sub(lambda m: new, t); (D / "main.tex").write_text(t, encoding="utf-8", newline="\n")
z = zipfile.ZipFile("GACI_Overleaf_ext2024.zip", "w", zipfile.ZIP_DEFLATED)
for f in ["main.tex", "GACI_TRA_refs.bib"] + sorted(glob.glob("*.png")): z.write(f)
z.close(); print("zip:", zipfile.ZipFile("GACI_Overleaf_ext2024.zip").namelist())
(D / "CHANGES_ext2024.md").write_text("""# GACI TRA manuscript, 1996-2024 version (2026-09-02)

Base: `TRA_rev20260902/main.tex` (coauthor-review fixes applied). This folder = same manuscript re-estimated on 1996-2024.
Upload `GACI_Overleaf_ext2024.zip` to Overleaf (main.tex + bib + 8 figures). `main_2023_version.tex` is the previous version for diffing.

## Data (ext2024/)
- WDI land area carried forward (no 2024 value published; it was the filter that silently dropped 2024), UNWTO 2024 arrivals ratio 0.99 of 2019 added to the tourism shifter, BACI 2024 processed.
- Panel: 185 countries, 4,816 country-years (Stata uses 4,814 after 2 singletons: Moldova, New Caledonia); 155 countries in 2024.
- Airports 3,171 (2005) to 3,863 (2024).

## Estimates (Stata ivreghdfe, robust; do-files in ext2024/do_ext2024, logs *_run.log)
- cwm: openness 1.208** (0.593), volume 2.126*** (0.703), GDP 0.919 (0.624), KP F 21.9. max: 0.897**/1.580***/0.683, F 33.0. sum: 0.635*/1.119***/0.483, F 11.0.
- Heterogeneity, temporal, controls, validity battery, Conley, RF-quintile, mechanism, mediation: all tables replaced 1:1 from Stata outputs.
- Substantive change: the intermediate/consumption composition shift is now significant (1.483**, was 1.116 ns) -> Hypothesis 3 wording upgraded from "qualified/partial support" to "supported" in mechanism text, synthesis, discussion, abstract, conclusion.
- Conley: openness f* = 0.04 (unperturbed CI [0.05, 2.37] now clears zero) -> paragraph and note rewritten.

## Aggregates (compute_aggregates.py etc., 2024 base, beta 1.208)
- Headline $10 trillion (9.95) = 21% of 2024 world trade ($46.6T) = 9.2% of world GDP ($108.4T); CI $0.5-15.9T; volume $6.7-19.4T.
- Three measures: openness $8.0-10.0T (17.2-21.4%), volume $10.4-14.9T, GDP-scale $13.8-17.4T. China $2.7T; decliners 18-34 of 185; Germany largest loss.
- COVID 2019->2020: cwm $7.1T (19%), max $6.3T (17%), sum $1.7T (4.6%); GDP $2.4-12.3T (3-14%).
- Continent 2024 endpoint: Asia +68%, Middle East +58%, Europe +20%, Africa +20%, Pacific +19%, Latin America +17%, North America +13%.

## Figures regenerated (all in ext2024/, copied here)
method construction (PCA to 2024), rank bump (2024 endpoint: DXB/IST/PVG/PEK/CAN/ICN; SGP #1 country), base map 2024, hetero quartile (Stata 2024 het estimates), continent trend, contribution 3-panel, COVID 3-panel, RF quintile.

## Not compiled locally (no TeX). Check the Overleaf log after upload.
""", encoding="utf-8")
print("done")
