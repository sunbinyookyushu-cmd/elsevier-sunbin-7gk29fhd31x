# -*- coding: utf-8 -*-
"""
22_build_placebo_outcomes.py   (LZ comment 4, 2026-09-03)
Builds the inputs for the exclusion-restriction diagnostics:
  (1) non-aviation placebo outcomes (OWID fossil CO2 by fuel; EDGAR 2024 GHG by sector)
  (2) alternative global-cycle series interacted with 1996 air market access
      (world GDP, Brent oil, world exports; world flights / seat-km / GACI sum /
      fuel-efficiency index from our own data)
  (3) placebo instrument: a_t x ln sea market access 1996
  (4) decay-exponent variants of the 1996 air market access (theta 0.5, 1.5)
  (5) development-channel covariates (urban share, FDI/GDP, tourist arrivals,
      trade/GDP)
Output: placebo_covariates.csv keyed (c, y); world_series.csv keyed y.
"""
import os, sys, json
import numpy as np
import pandas as pd
import pycountry

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(HERE, "data_external")
UP = os.path.join(HERE, "..")

fey = pd.read_csv(os.path.join(UP, "gaci_panel_feyrer.csv"), usecols=["c", "y", "a_t", "ln_air_ma", "ln_sea_ma", "feyrer_int"])
base = fey[fey.y == 1996][["c", "ln_air_ma", "ln_sea_ma"]].rename(columns={"ln_air_ma": "ln_air96", "ln_sea_ma": "ln_sea96"})
at = fey.groupby("y")["a_t"].first()

# ---------------- world series ----------------
def wb_wld(ind):
    j = json.load(open(os.path.join(EXT, f"wb_WLD_{ind}.json")))
    return pd.Series({r["year"]: r["value"] for r in j})
gdp_w = wb_wld("NY.GDP.MKTP.KD"); exp_w = wb_wld("NE.EXP.GNFS.KD")
br = pd.read_csv(os.path.join(EXT, "brent_annual.csv")); br["y"] = pd.to_datetime(br.iloc[:, 0]).dt.year
oil = pd.to_numeric(br.set_index("y")["DCOILBRENTEU"], errors="coerce")
co2 = pd.read_csv(os.path.join(HERE, "co2_country_year.csv"))
wy = co2.groupby("year").agg(fl=("n_dep_flights", "sum"), skm=("dep_seat_km", "sum"), co2=("co2_bunker", "sum"))
wy["eff"] = -np.log(wy["co2"] / wy["skm"])  # higher = more fuel-efficient
graw = pd.read_csv(os.path.join(UP, "GACI1996_2024_new_panel_data.csv"), encoding="utf-8-sig", usecols=["Year", "GACI"])
gsum = graw.groupby("Year")["GACI"].sum()
years = list(range(1996, 2024))
ws = pd.DataFrame(index=years)
ws["a_t"] = at.reindex(years)
def mm(s):
    s = s.reindex(years).astype(float)
    return (s - s.min()) / (s.max() - s.min())
ws["g_gdp"] = mm(gdp_w); ws["g_oil"] = mm(oil); ws["g_trade"] = mm(exp_w)
ws["g_fl"] = mm(wy["fl"]); ws["g_skm"] = mm(wy["skm"]); ws["g_eff"] = mm(wy["eff"]); ws["g_gaci"] = mm(gsum)
ws.index.name = "y"
ws.to_csv(os.path.join(HERE, "world_series.csv"))
print("world series corr with a_t:\n", ws.corr()["a_t"].round(3).to_string())

# ---------------- theta variants of 1996 air MA ----------------
ALIAS = {"Russia": "RUS", "Iran": "IRN", "Venezuela": "VEN", "Bolivia": "BOL", "Tanzania": "TZA", "Syria": "SYR",
         "Laos": "LAO", "Vietnam": "VNM", "South Korea": "KOR", "North Korea": "PRK", "Moldova": "MDA",
         "Democratic Republic of the Congo": "COD", "Republic of the Congo": "COG", "Ivory Coast": "CIV",
         "Cape Verde": "CPV", "Brunei": "BRN", "Micronesia": "FSM", "Macedonia": "MKD", "Czech Republic": "CZE",
         "Burma": "MMR", "East Timor": "TLS", "Palestine": "PSE", "Taiwan": "TWN", "Hong Kong": "HKG", "Macau": "MAC",
         "Turkey": "TUR", "United States": "USA", "United Kingdom": "GBR"}
def to_iso3(name, cache={}):
    if name in cache: return cache[name]
    iso = ALIAS.get(name)
    if iso is None:
        try: iso = pycountry.countries.lookup(name).alpha_3
        except LookupError:
            try: iso = pycountry.countries.search_fuzzy(name)[0].alpha_3
            except LookupError: iso = None
    cache[name] = iso; return iso
ap = pd.read_csv(os.path.join(UP, "airport_coords_merged.csv")); ap["c"] = ap["country"].astype(str).map(to_iso3)
cent = ap.dropna(subset=["c"]).groupby("c")[["lat", "lon"]].mean()
pop = json.load(open(os.path.join(UP, "wb_pop.json")))
pop96 = {k.split("|")[0]: float(v) for k, v in pop.items() if k.split("|")[1] == "1996"}
cs = [c for c in cent.index if c in pop96]
lat = np.radians(cent.loc[cs, "lat"].values); lon = np.radians(cent.loc[cs, "lon"].values)
h = np.sin((lat[:, None] - lat[None, :]) / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin((lon[:, None] - lon[None, :]) / 2) ** 2
D = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(h, 0, 1))); np.fill_diagonal(D, np.inf)
P = np.array([pop96[c] for c in cs])
th = pd.DataFrame({"c": cs})
for theta in [0.5, 1.0, 1.5]:
    W = D ** (-theta); np.fill_diagonal(W, 0.0)
    th[f"ln_air96_th{int(theta*10):02d}"] = np.log(W @ P)
print("theta variants corr with ln_air96 (canonical):")
chk = base.merge(th, on="c"); print(chk.drop(columns="c").corr()["ln_air96"].round(3).to_string())

# ---------------- OWID placebo outcomes ----------------
ow = pd.read_csv(os.path.join(EXT, "owid-co2-data.csv"), usecols=["iso_code", "year", "co2", "coal_co2", "oil_co2", "gas_co2", "cement_co2"])
ow = ow.dropna(subset=["iso_code"]).rename(columns={"iso_code": "c", "year": "y"})
ow = ow[(ow.y >= 1996) & (ow.y <= 2023)]
avi = co2[["iso3", "year", "co2_bunker", "co2_bunker_intl"]].rename(columns={"iso3": "c", "year": "y"})
ow = ow.merge(avi, on=["c", "y"], how="left")
ow["co2_mt"] = ow["co2"]; ow["av_mt"] = ow["co2_bunker"] / 1e9; ow["avdom_mt"] = (ow["co2_bunker"] - ow["co2_bunker_intl"]) / 1e9  # co2_bunker is in kg
# OWID/GCP territorial CO2 excludes international bunkers, so subtract DOMESTIC aviation only
ow["ln_co2_exav"] = np.log((ow["co2_mt"] - ow["avdom_mt"].fillna(0)).where(lambda s: s > 0))
ow["ln_coal"] = np.log(ow["coal_co2"].where(ow["coal_co2"] > 0))
ow["ln_gas"] = np.log(ow["gas_co2"].where(ow["gas_co2"] > 0))
ow["ln_cement"] = np.log(ow["cement_co2"].where(ow["cement_co2"] > 0))
ow["ln_oil_exav"] = np.log((ow["oil_co2"] - ow["avdom_mt"].fillna(0)).where(lambda s: s > 0))
ow["ln_co2_all"] = np.log(ow["co2_mt"].where(ow["co2_mt"] > 0))
owk = ow[["c", "y", "ln_co2_exav", "ln_co2_all", "ln_coal", "ln_gas", "ln_cement", "ln_oil_exav"]]

# ---------------- EDGAR sector outcomes ----------------
ed = pd.read_excel(os.path.join(EXT, "EDGAR_booklet.xlsx"), sheet_name="GHG_by_sector_and_country")
print("EDGAR columns:", ed.columns.tolist()[:6])
if "Substance" in ed.columns:
    print("substances:", ed["Substance"].dropna().unique().tolist())
    ed = ed[ed["Substance"].astype(str).str.upper() == "CO2"]
ed = ed.dropna(subset=["Sector"])
print("sectors:", sorted(ed["Sector"].astype(str).unique()))
ycols = [c for c in ed.columns if isinstance(c, (int, np.integer)) and 1996 <= c <= 2023]
edl = ed.melt(id_vars=["EDGAR Country Code", "Sector"], value_vars=ycols, var_name="y", value_name="v")
edl = edl.rename(columns={"EDGAR Country Code": "c"})
piv = edl.pivot_table(index=["c", "y"], columns="Sector", values="v", aggfunc="sum").reset_index()
piv.columns = [str(x) for x in piv.columns]
def lncol(df, name, newname):
    if name in df.columns:
        df[newname] = np.log(df[name].where(df[name] > 0))
lncol(piv, "Power Industry", "ln_ed_power"); lncol(piv, "Buildings", "ln_ed_build")
lncol(piv, "Industrial Combustion", "ln_ed_indcomb"); lncol(piv, "Transport", "ln_ed_transp")
lncol(piv, "Agriculture", "ln_ed_agri"); lncol(piv, "Waste", "ln_ed_waste")
piv["y"] = piv["y"].astype(int)
piv = piv.merge(ow[["c", "y", "avdom_mt"]], on=["c", "y"], how="left")
if "Transport" in piv.columns:
    piv["ln_ed_transp_exav"] = np.log((piv["Transport"] - piv["avdom_mt"].fillna(0)).where(lambda s: s > 0))
edk = piv[["c", "y"] + [k for k in piv.columns if k.startswith("ln_ed_")]]

# ---------------- WB covariates ----------------
def wb_all(ind, name):
    j = json.load(open(os.path.join(EXT, f"wb_{ind}.json")))
    d = pd.DataFrame(j).rename(columns={"iso3": "c", "year": "y", "value": name})
    return d[(d.y >= 1996) & (d.y <= 2023) & (d.c.str.len() == 3)]
cov = wb_all("SP.URB.TOTL.IN.ZS", "urban")
for ind, nm in [("BX.KLT.DINV.WD.GD.ZS", "fdi"), ("ST.INT.ARVL", "arrivals"), ("NE.TRD.GNFS.ZS", "trade_gdp"), ("NY.GDP.MKTP.KD", "gdp_kd")]:
    cov = cov.merge(wb_all(ind, nm), on=["c", "y"], how="outer")
cov["ln_arrivals"] = np.log(cov["arrivals"].where(cov["arrivals"] > 0))
cov["ln_gdp_kd"] = np.log(cov["gdp_kd"].where(cov["gdp_kd"] > 0))

# ---------------- assemble ----------------
grid = fey[["c", "y"]].drop_duplicates()
out = grid.merge(base, on="c", how="left").merge(th, on="c", how="left")
out = out.merge(ws.reset_index(), on="y", how="left")
for g in ["g_gdp", "g_oil", "g_trade", "g_fl", "g_skm", "g_eff", "g_gaci"]:
    out[f"fey_{g[2:]}"] = out[g] * out["ln_air96"]
out["fey_sea"] = out["a_t"] * out["ln_sea96"]
out["fey_th05"] = out["a_t"] * out["ln_air96_th05"]
out["fey_th15"] = out["a_t"] * out["ln_air96_th15"]
out["fey_th10chk"] = out["a_t"] * out["ln_air96_th10"]
out = out.merge(owk, on=["c", "y"], how="left").merge(edk, on=["c", "y"], how="left").merge(cov[["c", "y", "urban", "fdi", "ln_arrivals", "trade_gdp", "ln_gdp_kd"]], on=["c", "y"], how="left")
out.to_csv(os.path.join(HERE, "placebo_covariates.csv"), index=False)
print("saved placebo_covariates.csv", out.shape)
print(out.drop(columns=["c"]).describe().T[["count", "mean"]].round(3).to_string())
print("DONE_22")
