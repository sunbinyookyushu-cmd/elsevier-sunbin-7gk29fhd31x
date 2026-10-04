"""
Aggregate EDGAR 0.1-degree gridded CO2 (and GHS-POP population) to airport catchments.
RUN LOCALLY after downloading (see README). Needs: pip install xarray netCDF4 scipy pandas numpy

Inputs
  --edgar_dir   folder with EDGAR annual netCDF files, one per year (and per sector if you downloaded sectors), e.g.
                v8.0_FT2022_GHG_CO2_2005_TOTALS_emi.nc, v8.0_FT2022_GHG_CO2_2005_ENE_emi.nc, ...
                Both *_emi.nc (t / cell / yr) and *_flx.nc (kg m-2 s-1) are handled.
  --airports    airport_country_map.csv (Airport, lat, lon, iso_country) from the repo  (data/processed/)
  --gaci        GACI1996_2024_panel.csv  (to restrict to airports that are in GACI)
  --pop_dir     optional: GHS-POP GeoTIFF/netCDF per epoch (1990, 1995, ..., 2025) already resampled to 0.1 deg,
                or any gridded population netCDF with lat/lon dims; interpolated linearly between epochs.
Catchment definition (both written):
  ring50  : grid cells whose centre is within 50 km of the airport AND the airport is the nearest GACI airport (no overlap)
  ring100 : same with 100 km
Output: airport_catchment_co2.csv  columns: Airport, year, sector, radius_km, co2_t, n_cells, pop (if available)
"""
import argparse, re, glob, numpy as np, pandas as pd, xarray as xr
from scipy.spatial import cKDTree
ap = argparse.ArgumentParser()
ap.add_argument("--edgar_dir", required=True); ap.add_argument("--airports", required=True); ap.add_argument("--gaci", required=True)
ap.add_argument("--pop_dir", default=None); ap.add_argument("--out", default="airport_catchment_co2.csv")
a = ap.parse_args()

apt = pd.read_csv(a.airports, keep_default_na=False, na_values=[""]).dropna(subset=["lat","lon"])
gaci_apts = set(pd.read_csv(a.gaci, usecols=["Airport"]).Airport.unique())
apt = apt[apt.Airport.isin(gaci_apts)].reset_index(drop=True)
print(len(apt), "GACI airports with coordinates")

def xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)])
R = 6371.0
tree = cKDTree(xyz(apt.lat.values, apt.lon.values))

files = sorted(glob.glob(f"{a.edgar_dir}/*.nc"))
assert files, "no .nc files found"
rows = []; cell_assign = None
for f in files:
    m = re.search(r"(19|20)\d{2}", f.split("/")[-1]); year = int(m.group(0)) if m else None
    sec = re.search(r"_(\d{4})_([A-Za-z_]+?)_(emi|flx)\.nc$", f.split("/")[-1]); sector = sec.group(2) if sec else "TOTALS"
    ds = xr.open_dataset(f); var = [v for v in ds.data_vars if ds[v].ndim >= 2][0]; da = ds[var].squeeze()
    latn = [c for c in da.dims if "lat" in c.lower()][0]; lonn = [c for c in da.dims if "lon" in c.lower()][0]
    lat = da[latn].values; lon = da[lonn].values; lon180 = np.where(lon > 180, lon - 360, lon)
    vals = da.values.astype("float64")
    units = str(da.attrs.get("units", "")).lower()
    if "kg" in units and "m-2" in units and "s-1" in units:    # flux -> tonnes per cell per year
        dlat = abs(float(lat[1]-lat[0])); dlon = abs(float(lon[1]-lon[0]))
        area = (R*1000)**2 * np.radians(dlon) * (np.sin(np.radians(lat + dlat/2)) - np.sin(np.radians(lat - dlat/2)))  # m2 per lat row
        vals = vals * area[:, None] * 365.25*86400 / 1000.0
    if cell_assign is None:   # assign every grid cell to nearest GACI airport once (same grid for all files)
        LAT, LON = np.meshgrid(lat, lon180, indexing="ij")
        dist, idx = tree.query(xyz(LAT.ravel(), LON.ravel()), k=1)
        km = 2*R*np.arcsin(np.minimum(1.0, dist/2))
        cell_assign = {"idx": idx.reshape(LAT.shape), "km": km.reshape(LAT.shape)}
        print("grid", LAT.shape, "assigned")
    for rad in (50, 100):
        mask = cell_assign["km"] <= rad
        s = pd.DataFrame({"ai": cell_assign["idx"][mask], "co2": vals[mask]}).groupby("ai").agg(co2_t=("co2","sum"), n_cells=("co2","size"))
        s["Airport"] = apt.Airport.values[s.index]; s["year"] = year; s["sector"] = sector; s["radius_km"] = rad
        rows.append(s.reset_index(drop=True))
    print(f, year, sector, "ok")
out = pd.concat(rows)
if a.pop_dir:
    pfiles = sorted(glob.glob(f"{a.pop_dir}/*.nc")); prow = []
    for f in pfiles:
        yr = int(re.search(r"(19|20)\d{2}", f.split("/")[-1]).group(0)); ds = xr.open_dataset(f); var = list(ds.data_vars)[0]; da = ds[var].squeeze()
        da = da.interp({[c for c in da.dims if "lat" in c.lower()][0]: lat, [c for c in da.dims if "lon" in c.lower()][0]: lon180}, method="nearest")
        v = da.values.astype("float64")
        for rad in (50, 100):
            mask = cell_assign["km"] <= rad
            s = pd.DataFrame({"ai": cell_assign["idx"][mask], "pop": v[mask]}).groupby("ai")["pop"].sum()
            prow.append(pd.DataFrame({"Airport": apt.Airport.values[s.index], "year": yr, "radius_km": rad, "pop": s.values}))
    P = pd.concat(prow)
    # linear interpolation between epochs
    full = []
    for (ap_, rad), g in P.groupby(["Airport","radius_km"]):
        yrs = np.arange(1996, 2025); full.append(pd.DataFrame({"Airport": ap_, "radius_km": rad, "year": yrs, "pop": np.interp(yrs, g.year.values, g["pop"].values)}))
    out = out.merge(pd.concat(full), on=["Airport","radius_km","year"], how="left")
out.to_csv(a.out, index=False); print("written", a.out, out.shape)
