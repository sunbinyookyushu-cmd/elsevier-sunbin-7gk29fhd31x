"""Download Climate TRACE aviation emissions (asset = airport level, 2015-present).

Climate TRACE publishes source-level (airport) emissions for 'domestic-aviation' and 'international-aviation'
sub-sectors with annual/monthly CO2, CO2e. Two routes:
  (a) bulk package: https://downloads.climatetrace.org/v{ver}/sector_packages/transportation.zip
  (b) API: https://api.climatetrace.org/v6/assets?sectors=domestic-aviation,international-aviation&limit=...
Host required: api.climatetrace.org / downloads.climatetrace.org (currently BLOCKED by the session network
policy -> run locally or after allowing the hosts).
Output: data/raw/emissions/climatetrace_transportation.zip (unzip -> aviation CSVs with asset name, lat/lon, country, year, co2)
Use: validate the bottom-up (OAG x FEAT) airport-year CO2 for 2015-2024; expect correlation > 0.9 in logs.
"""
import pathlib, urllib.request, shutil, sys
root = pathlib.Path(__file__).resolve().parents[1]
dest = root/"data/raw/emissions/climatetrace_transportation.zip"
ver = sys.argv[1] if len(sys.argv)>1 else "6"
url = f"https://downloads.climatetrace.org/v{ver}/sector_packages/transportation.zip"
print("downloading", url)
with urllib.request.urlopen(url, timeout=600) as r, open(dest,"wb") as f: shutil.copyfileobj(r,f)
print("ok", dest.stat().st_size//2**20, "MB")
