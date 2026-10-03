import re, subprocess, sys, pathlib
from PIL import Image
S = pathlib.Path(r"C:\Users\sunbi\AppData\Local\Temp\claude\C--Users-sunbi\03959d37-389d-4dc3-a843-df1ca5e7fcc3\scratchpad")
G = pathlib.Path(r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI")
src = (G / "_design_rankbump" / "FigureOnly.dc.html").read_text(encoding="utf-8")
h = src.replace('<script src="./support.js"></script>', '')
h = h.replace('<x-dc>', '').replace('</x-dc>', '')
h = h.replace('<helmet>', '').replace('</helmet>', '')
# drop the baked-in grey footnote (duplicates the LaTeX caption)
h2, n = re.subn(r'<div style="border-top: 1px solid #e7e2d8; margin-top: 26px;.*?</div>\s*', '', h, flags=re.S)
assert n == 1, n
# white background instead of off-white panel
h2 = h2.replace('#fbfaf7', '#ffffff')
h2 = h2.replace('padding: 48px 56px 40px 56px', 'padding: 40px 56px 24px 56px')
out_html = S / "rankbump_fig.html"
out_html.write_text(h2, encoding="utf-8")
png = S / "rankbump_raw.png"
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
       "--force-device-scale-factor=3", "--window-size=1660,900", "--virtual-time-budget=15000",
       f"--screenshot={png}", out_html.as_uri()]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
print("chrome rc", r.returncode, r.stderr[-400:])
im = Image.open(png).convert("RGB")
print("raw", im.size)
# trim white margins
bg = Image.new("RGB", im.size, (255, 255, 255))
from PIL import ImageChops
bbox = ImageChops.difference(im, bg).getbbox()
print("bbox", bbox)
pad = 36
box = (max(bbox[0]-pad,0), max(bbox[1]-pad,0), min(bbox[2]+pad, im.width), min(bbox[3]+pad, im.height))
im.crop(box).save(S / "GACI_rank_bump_rev.png", dpi=(300,300))
print("final", Image.open(S / "GACI_rank_bump_rev.png").size)
