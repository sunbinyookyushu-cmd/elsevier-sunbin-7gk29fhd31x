# -*- coding: utf-8 -*-
"""Copy the paper's Stata do-files into do_ext2024/ with cd/import paths pointed at the ext2024 folder (CRLF preserved)."""
import pathlib
names = ("gaci_main_table gaci_hetero_table gaci_temporal_table gaci_mechanism gaci_mediation gaci_controls "
         "gaci_natmix_overid gaci_3iv gaci_combined_iv gaci_temporal gaci_rf_nonlinear gaci_conley "
         "gaci_measures_table gaci_tourism_hetero_iv").split()
BS = "\\"
pairs = [('2026/GACI"', '2026/GACI/ext2024"'),
         ('2026' + BS + 'GACI' + BS, '2026' + BS + 'GACI' + BS + 'ext2024' + BS),
         ('2026' + BS + 'GACI"', '2026' + BS + 'GACI' + BS + 'ext2024"')]
pathlib.Path("do_ext2024").mkdir(exist_ok=True)
n = 0
for nm in names:
    b = pathlib.Path(f"../{nm}.do").read_bytes(); b2 = b
    for old, new in pairs:
        b2 = b2.replace(old.encode(), new.encode())
    pathlib.Path(f"do_ext2024/{nm}.do").write_bytes(b2); n += (b2 != b)
    if b2 == b: print("NO PATH FOUND in", nm)
print("repointed", n, "of", len(names), "| CRLF:", all(b"\r\n" in pathlib.Path(f"do_ext2024/{x}.do").read_bytes() for x in names))
