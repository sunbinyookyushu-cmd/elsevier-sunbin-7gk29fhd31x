# -*- coding: utf-8 -*-
"""Add six verified Nature Climate Change / Nature Cities citations (2026-09-26)."""
import pathlib, shutil, zipfile, os
D = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2\FINAL_20260926\overleaf_20260926")
P = D / "main_co2_nature_20260926.tex"
t = P.read_bytes().decode("utf-8")
log = []
def rep(old, new, label):
    global t
    n = t.count(old); assert n == 1, f"{label}: {n}\n{old}"
    t = t.replace(old, new); log.append("OK  " + label)

rep("development \\citep{lenaerts2021,zhang2020}, making network expansion",
    "development \\citep{lenaerts2021,zhang2020,amico2026}, making network expansion", "intro: Amico 2026 (Nature Cities)")
rep("trade, and tourism can further affect both network expansion and aviation\nactivity \\citep{vandevijver2014}.",
    "trade, and tourism can further affect both network expansion and aviation\nactivity \\citep{vandevijver2014,lenzen2018}.", "intro: Lenzen 2018 (NCC)")
rep("combine connectivity expansion with lower-carbon fuels, propulsion technologies and demand-side measures.",
    "combine connectivity expansion with lower-carbon fuels, propulsion technologies and demand-side measures \\citep{creutzig2018}.", "discussion 1: Creutzig 2018 (NCC)")
rep("The economic gains from connectivity are also expected to be largest in weakly connected economies \\citep{lenaerts2021,zhang2020},",
    "The economic gains from connectivity are also expected to be largest in weakly connected economies \\citep{lenaerts2021,zhang2020,amico2026},", "discussion 2: Amico 2026")
rep("It remains after accounting for neighbours' emissions and common regional shocks.",
    "It remains after accounting for neighbours' emissions and common regional shocks, which distinguishes it from the strategic interaction in emissions documented among neighbouring jurisdictions \\citep{zhuwei2024}.", "discussion 3: Zhu and Wei 2024 (Nature Cities)")
rep("The later-period elasticity is identified only after excluding the COVID-19 collapse years;",
    "The later-period elasticity is identified only after excluding the COVID-19 collapse years \\citep{lequere2020};", "discussion 5: Le Quere 2020 (NCC)")
rep("and non-CO$_2$ climate effects are excluded.",
    "and non-CO$_2$ climate effects, which account for a large part of aviation's warming, are excluded \\citep{brazzola2022}.", "discussion 5: Brazzola 2022 (NCC)")
P.write_bytes(t.encode("utf-8"))

bib = r"""
@article{brazzola2022,
  author  = {Brazzola, Nicoletta and Patt, Anthony and Wohland, Jan},
  title   = {Definitions and implications of climate-neutral aviation},
  journal = {Nature Climate Change},
  volume  = {12},
  number  = {8},
  pages   = {761--767},
  year    = {2022},
  doi     = {10.1038/s41558-022-01404-7}
}
@article{lequere2020,
  author  = {Le Qu{\'e}r{\'e}, Corinne and Jackson, Robert B. and Jones, Matthew W. and Smith, Adam J. P. and Abernethy, Sam and Andrew, Robbie M. and De-Gol, Anthony J. and Willis, David R. and Shan, Yuli and Canadell, Josep G. and Friedlingstein, Pierre and Creutzig, Felix and Peters, Glen P.},
  title   = {Temporary reduction in daily global {CO$_2$} emissions during the {COVID-19} forced confinement},
  journal = {Nature Climate Change},
  volume  = {10},
  number  = {7},
  pages   = {647--653},
  year    = {2020},
  doi     = {10.1038/s41558-020-0797-x}
}
@article{creutzig2018,
  author  = {Creutzig, Felix and Roy, Joyashree and Lamb, William F. and Azevedo, In{\^e}s M. L. and Bruine de Bruin, W{\"a}ndi and Dalkmann, Holger and Edelenbosch, Oreane Y. and Geels, Frank W. and Grubler, Arnulf and Hepburn, Cameron and Hertwich, Edgar G. and Khosla, Radhika and Mattauch, Linus and Minx, Jan C. and Ramakrishnan, Anjali and Rao, Narasimha D. and Steinberger, Julia K. and Tavoni, Massimo and {\"U}rge-Vorsatz, Diana and Weber, Elke U.},
  title   = {Towards demand-side solutions for mitigating climate change},
  journal = {Nature Climate Change},
  volume  = {8},
  number  = {4},
  pages   = {260--263},
  year    = {2018},
  doi     = {10.1038/s41558-018-0121-1}
}
@article{lenzen2018,
  author  = {Lenzen, Manfred and Sun, Ya-Yen and Faturay, Futu and Ting, Yuan-Peng and Geschke, Arne and Malik, Arunima},
  title   = {The carbon footprint of global tourism},
  journal = {Nature Climate Change},
  volume  = {8},
  number  = {6},
  pages   = {522--528},
  year    = {2018},
  doi     = {10.1038/s41558-018-0141-x}
}
@article{amico2026,
  author  = {Amico, Ambra and Duarte, Fabio and Liao, Wen-Chi and Zheng, Siqi},
  title   = {Air connectivity boosts urban attractiveness for global firms},
  journal = {Nature Cities},
  volume  = {3},
  number  = {1},
  pages   = {78--88},
  year    = {2026},
  doi     = {10.1038/s44284-025-00361-4}
}
@article{zhuwei2024,
  author  = {Zhu, Bei and Wei, Chu},
  title   = {Strategic interactions for carbon emissions in {Chinese} cities are influenced by mayors},
  journal = {Nature Cities},
  volume  = {1},
  number  = {5},
  pages   = {370--377},
  year    = {2024},
  doi     = {10.1038/s44284-024-00059-z}
}
"""
B = D / "refs_co2.bib"
s = B.read_text(encoding="utf-8")
if "brazzola2022" not in s:
    B.write_text(s.rstrip("\n") + "\n" + bib, encoding="utf-8", newline="\n"); log.append("OK  bib +6")
# sync copy and zip
J = D.parent.parent / "Junya_comments_20260925" / "overleaf_20260926"
shutil.copy(P, J / P.name); shutil.copy(B, J / B.name)
os.chdir(D)
z = zipfile.ZipFile(D.parent / "GACI_CO2_overleaf_upload_20260926.zip", "w", zipfile.ZIP_DEFLATED)
for f in ["main_co2_nature_20260926.tex", "refs_co2.bib", "Figure1.png", "Figure2_ab.png", "CO2_SAF.png", "ED_Fig1.png", "ED_Fig2.png", "ED_Fig3.png", "ED_Fig4.png"]:
    z.write(f)
z.close(); log.append("OK  zip rebuilt, copy synced")
print("\n".join(log))
