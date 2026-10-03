# -*- coding: utf-8 -*-
"""Airport-level heritage-proximity instrument (pilot).

Exposure_j = natural+mixed UNESCO sites near airport j (fixed endowment, as in
the trade paper's country instrument), three variants:
  n100  : count of sites within 100 km
  n200  : count within 200 km
  invd  : sum over sites within 300 km of 1/max(d,10km)  (distance-weighted)
Instrument z_jt = tour_shift_t x Exposure_j  (same global tourism cycle
shifter a_t as the country IV).
Output: airport_hiv_panel.csv = airport_co2_panel + exposures + instruments.
"""
import numpy as np
import pandas as pd

GACI = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
HERE = GACI + r"\GACI_CO2"

# ---- UNESCO natural + mixed sites -----------------------------------------
uh = pd.read_csv(GACI + r"\uh_csv.csv",
                 usecols=["category", "coordinates", "date_inscribed"])
uh = uh[uh.category.isin(["Natural", "Mixed"])].copy()
cc = uh.coordinates.str.split("|", expand=True)
uh["slat"] = pd.to_numeric(cc[0], errors="coerce")
uh["slon"] = pd.to_numeric(cc[1], errors="coerce")
uh = uh.dropna(subset=["slat", "slon"])
print(f"natural+mixed sites with coordinates: {len(uh)}")

# ---- airports --------------------------------------------------------------
ap = pd.read_csv(GACI + r"\airport_coords_merged.csv")  # Airport, lat, lon
ap = ap.dropna(subset=["lat", "lon"]).copy()
print(f"airports with coordinates: {len(ap)}")

# ---- haversine distance matrix (airports x sites), km ----------------------
R = 6371.0
la = np.radians(ap.lat.to_numpy())[:, None]
lo = np.radians(ap.lon.to_numpy())[:, None]
sa = np.radians(uh.slat.to_numpy())[None, :]
so = np.radians(uh.slon.to_numpy())[None, :]
dlat = sa - la
dlon = so - lo
h = np.sin(dlat / 2) ** 2 + np.cos(la) * np.cos(sa) * np.sin(dlon / 2) ** 2
dist = 2 * R * np.arcsin(np.sqrt(np.clip(h, 0, 1)))

ap["exp_n100"] = (dist <= 100).sum(axis=1)
ap["exp_n200"] = (dist <= 200).sum(axis=1)
w = np.where(dist <= 300, 1.0 / np.maximum(dist, 10.0), 0.0)
ap["exp_invd"] = w.sum(axis=1)
print("exposure summary:")
print(ap[["exp_n100", "exp_n200", "exp_invd"]].describe().loc[["mean", "50%", "max"]].round(3))
print(f"airports with n200>0: {(ap.exp_n200 > 0).mean():.1%}")

# ---- global tourism shifter a_t -------------------------------------------
g = pd.read_csv(GACI + r"\gaci_panel_3iv.csv", usecols=["y", "tour_shift"])
ts = g.groupby("y")["tour_shift"].agg(["mean", "std"])
assert (ts["std"].fillna(0) < 1e-9).all(), "tour_shift varies within year!"
shift = ts["mean"]
print(f"tour_shift: {shift.loc[1996]:.3f} (1996) -> {shift.loc[2023]:.3f} (2023)")

# ---- merge into the airport panel -----------------------------------------
p = pd.read_csv(HERE + r"\airport_co2_panel.csv")
p = p.merge(ap[["Airport", "exp_n100", "exp_n200", "exp_invd"]],
            left_on="airport_iata", right_on="Airport", how="left").drop(columns=["Airport"])
p["a_t"] = p.year.map(shift)
for v in ["n100", "n200", "invd"]:
    p[f"z_{v}"] = p["a_t"] * p[f"exp_{v}"]
print(f"panel rows {len(p):,}; exposure matched "
      f"{p.exp_n200.notna().sum():,} ({100 * p.exp_n200.notna().mean():.2f}%)")
p.to_csv(HERE + r"\airport_hiv_panel.csv", index=False)
print("wrote airport_hiv_panel.csv")
