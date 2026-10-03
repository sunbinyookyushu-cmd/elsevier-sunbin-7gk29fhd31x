# -*- coding: utf-8 -*-
"""Render ext2024/_design_rankbump/FigureOnly.dc.html (2024 endpoint) to GACI_rank_bump_rev.png:
   footnote removed (duplicates the LaTeX caption), white background, 3x device scale, trimmed."""
import re, subprocess, pathlib
from PIL import Image, ImageChops
E = pathlib.Path(__file__).parent
src = (E / "_design_rankbump" / "FigureOnly.dc.html").read_text(encoding="utf-8")
h = src.replace('<script src="./support.js"></script>', '').replace('<x-dc>', '').replace('</x-dc>', '').replace('<helmet>', '').replace('</helmet>', '')
h, n = re.subn(r'<div style="border-top: 1px solid #e7e2d8; margin-top: 26px;.*?</div>\s*', '', h, flags=re.S); assert n == 1, n
h = h.replace('#fbfaf7', '#ffffff').replace('padding: 48px 56px 40px 56px', 'padding: 40px 56px 24px 56px')
out_html = E / "_design_rankbump" / "FigureOnly_standalone_nonote.html"; out_html.write_text(h, encoding="utf-8")
raw = E / "_rankbump_raw.png"
cmd = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
       "--force-device-scale-factor=3", "--window-size=1660,900", "--virtual-time-budget=15000", f"--screenshot={raw}", out_html.as_uri()]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=180); print("chrome rc", r.returncode)
im = Image.open(raw).convert("RGB"); bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox(); pad = 36
im.crop((max(bbox[0]-pad, 0), max(bbox[1]-pad, 0), min(bbox[2]+pad, im.width), min(bbox[3]+pad, im.height))).save(E / "GACI_rank_bump_rev.png", dpi=(300, 300))
print("final", Image.open(E / "GACI_rank_bump_rev.png").size)
