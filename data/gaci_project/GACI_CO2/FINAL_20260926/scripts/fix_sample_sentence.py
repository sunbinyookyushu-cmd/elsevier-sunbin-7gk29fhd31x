# -*- coding: utf-8 -*-
import pathlib, subprocess, zipfile, os
D = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2\Junya_comments_20260925\overleaf_20260926")
P = D / "main_co2_nature_20260926.tex"
t = P.read_bytes().decode("utf-8")

old = "The estimation sample covers 182 countries over 1996--2023, comprising 4,634 country-year observations after one singleton observation is dropped."
new = ("The estimation sample covers 182 countries over 1996--2023, comprising 4,634 country-year observations. "
       "Two of the 184 countries in the emissions panel are excluded: Cura\\c{c}ao, for which the CERDI database records no sea distance, "
       "and New Caledonia, observed in a single year.")
assert t.count(old) == 1; t = t.replace(old, new)

old2 = "For the 34 countries entering the panel after 1996 and the 18 whose series end before 2023, the change is taken between the first and last observed years."
new2 = ("The attribution covers all 184 countries in the emissions panel; for the 34 countries entering the panel after 1996 and the 18 whose series end before 2023, "
        "the change is taken between the first and last observed years.")
assert t.count(old2) == 1; t = t.replace(old2, new2)

P.write_bytes(t.encode("utf-8"))
print("sentences fixed")

# regenerate diff and zip
base = D / "_base_overleaf_download_20260926.tex"
with open(D / "diff_20260926_vs_overleaf.txt", "w", encoding="utf-8") as f:
    subprocess.run(["diff", str(base), str(P)], stdout=f)
z = zipfile.ZipFile(D / "GACI_CO2_overleaf_upload_20260926.zip", "w", zipfile.ZIP_DEFLATED)
os.chdir(D)
z.write("main_co2_nature_20260926.tex"); z.write("refs_co2.bib"); z.close()
print("zip and diff regenerated")
