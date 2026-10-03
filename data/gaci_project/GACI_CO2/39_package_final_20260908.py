# -*- coding: utf-8 -*-
"""39_package_final_20260908.py  Assemble FINAL_20260908: overleaf folder (tex+bib+figures), viz xlsx,
README, results CSVs -> GACI_CO2_FINAL_20260908.zip; copies to Downloads."""
import os, re, shutil, zipfile, sys, datetime
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__)); FIN = os.path.join(HERE, "FINAL_20260908")
TEX = os.path.join(FIN, "main_co2_nature_20260908.tex"); OV = os.path.join(FIN, "co2_overleaf_20260908")
s = open(TEX, encoding="utf-8").read()
figs = sorted(set(re.findall(r"includegraphics\[[^\]]*\]\{([^}]+)\}", s)))
os.makedirs(OV, exist_ok=True)
for f in os.listdir(OV):
    try: os.remove(os.path.join(OV, f))
    except OSError: pass
missing = []
for f in figs:
    p = os.path.join(HERE, f)
    if os.path.exists(p): shutil.copy(p, os.path.join(OV, f))
    else: missing.append(f)
shutil.copy(TEX, os.path.join(OV, os.path.basename(TEX))); shutil.copy(os.path.join(FIN, "refs_co2.bib"), os.path.join(OV, "refs_co2.bib"))
print("figures:", len(figs), "missing:", missing)
RES = os.path.join(FIN, "results_csv"); os.makedirs(RES, exist_ok=True)
for f in sorted(os.listdir(HERE)):
    if f.startswith("_") and f.endswith(".csv") and not f.startswith("_bak"): shutil.copy(os.path.join(HERE, f), os.path.join(RES, f))
for f in ["co2_country_year.csv", "gaci_co2_panel.csv"]: shutil.copy(os.path.join(HERE, f), os.path.join(RES, f))
viz = os.path.join(HERE, "CO2_visualization_data_20260908.xlsx")
if os.path.exists(viz): shutil.copy(viz, os.path.join(FIN, os.path.basename(viz)))
readme = os.path.join(FIN, "README_20260908.md")
zp = os.path.join(FIN, "GACI_CO2_FINAL_20260908.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in os.listdir(OV): z.write(os.path.join(OV, f), "co2_overleaf_20260908/" + f)
    for f in os.listdir(RES): z.write(os.path.join(RES, f), "results_csv/" + f)
    for f in [os.path.basename(TEX), "refs_co2.bib", os.path.basename(viz), "README_20260908.md"]:
        p = os.path.join(FIN, f)
        if os.path.exists(p): z.write(p, f)
print("zip:", zp, os.path.getsize(zp) // 1024, "KB")
DL = r"C:\Users\sunbi\Downloads"
for f in [zp, TEX, os.path.join(FIN, "refs_co2.bib"), viz, readme]:
    if os.path.exists(f): shutil.copy(f, os.path.join(DL, os.path.basename(f)))
print("copied to Downloads; DONE_39")
