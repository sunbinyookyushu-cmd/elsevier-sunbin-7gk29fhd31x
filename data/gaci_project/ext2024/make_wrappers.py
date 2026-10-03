# -*- coding: utf-8 -*-
"""Batch-mode helpers: rename inner `log using` targets to *_run.log (batch mode auto-opens <dofile>.log and locks it)
and create wrapper do-files w_<name>.do so the batch log never collides with the do-file's own log."""
import pathlib, re
E = pathlib.Path(".")
names = ("gaci_main_table gaci_hetero_table gaci_temporal_table gaci_mechanism gaci_mediation gaci_controls "
         "gaci_natmix_overid gaci_3iv gaci_combined_iv gaci_temporal gaci_rf_nonlinear gaci_conley "
         "gaci_measures_table gaci_tourism_hetero_iv").split()
CRLF = b"\r\n"
for nm in names:
    p = E / "do_ext2024" / f"{nm}.do"; s = p.read_bytes().decode("utf-8", errors="replace")
    s = re.sub(r'log using "([^"]+?)\.log"', lambda m: f'log using "{m.group(1)}_run.log"', s)
    p.write_bytes(s.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    w = E / "do_ext2024" / f"w_{nm}.do"
    w.write_bytes((f'do "C:/Users/sunbi/managi-lab Dropbox/Sunbin Yoo/Research Box ^-^/2026/GACI/ext2024/do_ext2024/{nm}.do"\r\n').encode("utf-8"))
for f in E.glob("*.log"):
    if f.name != "_baci_run.log": f.unlink()
print("ok", len(names))
