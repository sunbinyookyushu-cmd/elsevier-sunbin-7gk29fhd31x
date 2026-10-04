"""
Build country-year panels from user-supplied external files:
  data_external/lsci/US_LSCI.csv        UNCTAD Liner Shipping Connectivity Index (quarterly, 2006Q1-)
  data_external/wdi/wdi_data.csv        WDI DataBank export (16 series, wide years)
  data_external/pwt/pwt110.xlsx         Penn World Table 11.0
Outputs (ISO3 'c', year 'y'):
  lsci_country_year.csv   lsci (annual mean of quarters), lsci_q1 (Q1 only), ln_lsci
  wdi_country_year.csv    one column per series (short names)
  pwt_country_year.csv    rgdpo, rgdpna, rnna, rkna, emp, hc, pop, labsh, ctfp, rtfpna, avh
"""
import json, re
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
EXT  = HERE / "data_external"
ROOT = HERE.parents[2]

# ---------- M49 numeric -> ISO3 ----------
ml = pd.read_json(ROOT / "data/raw/airports/mledoze_countries.json")
m49 = {str(r.ccn3).zfill(3): r.cca3 for r in ml.itertuples() if isinstance(r.ccn3, str) and r.ccn3}
# UNCTAD uses a few legacy / aggregate codes
m49.update({"891": None, "530": None, "736": "SDN", "158": "TWN"})

# ---------- LSCI ----------
ls = pd.read_csv(EXT / "lsci/US_LSCI.csv", dtype={"Economy": str})
ls = ls.rename(columns={"Economy": "m49", "Economy Label": "econ",
                        "Index (average Q1 2023 = 100)": "lsci"})
ls["y"] = ls["Quarter"].str[:4].astype(int)
ls["q"] = ls["Quarter"].str[-2:].astype(int)
ls["c"] = ls["m49"].map(m49)
unm = ls.loc[ls["c"].isna(), ["m49", "econ"]].drop_duplicates()
print("LSCI unmapped economies:\n", unm.to_string())
ls = ls.dropna(subset=["c", "lsci"])
ann = ls.groupby(["c", "y"]).agg(lsci=("lsci", "mean"), lsci_nq=("lsci", "size")).reset_index()
q1  = ls[ls.q == 1].groupby(["c", "y"])["lsci"].mean().rename("lsci_q1").reset_index()
ann = ann.merge(q1, on=["c", "y"], how="left")
ann["ln_lsci"] = np.log(ann["lsci"])
ann.to_csv(HERE / "lsci_country_year.csv", index=False)
print("LSCI:", ann.shape, ann.y.min(), ann.y.max(), ann.c.nunique(), "countries")

# ---------- WDI ----------
short = {
 "NV.IND.MANF.ZS": "manuf_sh", "NV.IND.TOTL.ZS": "ind_sh", "NV.SRV.TOTL.ZS": "serv_sh",
 "NV.AGR.TOTL.ZS": "agr_sh", "TX.VAL.TECH.MF.ZS": "hitech_x_sh", "TX.VAL.MANF.ZS.UN": "manuf_x_sh",
 "EG.USE.PCAP.KG.OE": "energy_pc_kgoe", "EG.EGY.PRIM.PP.KD": "energy_int_mj", "EG.ELC.COAL.ZS": "elec_coal_sh",
 "EG.FEC.RNEW.ZS": "renew_sh", "EN.ATM.PM25.MC.M3": "pm25_wdi", "NY.GDP.PCAP.KD": "gdppc_2015usd",
 "SP.POP.TOTL": "pop_wdi", "SP.URB.TOTL.IN.ZS": "urban_sh", "BX.KLT.DINV.WD.GD.ZS": "fdi_in_gdp",
 "NE.TRD.GNFS.ZS": "trade_gdp_wdi"}
w = pd.read_csv(EXT / "wdi/wdi_data.csv")
w = w.dropna(subset=["Series Code"])
w = w[w["Series Code"].isin(short)]
yc = [c for c in w.columns if re.match(r"^\d{4} \[YR\d{4}\]$", c)]
long = w.melt(id_vars=["Country Code", "Series Code"], value_vars=yc, var_name="y", value_name="v")
long["y"] = long["y"].str[:4].astype(int)
long["v"] = pd.to_numeric(long["v"].replace("..", np.nan), errors="coerce")
long["var"] = long["Series Code"].map(short)
wd = long.pivot_table(index=["Country Code", "y"], columns="var", values="v").reset_index()
wd = wd.rename(columns={"Country Code": "c"})
wd = wd[wd.y >= 1990]
# drop WDI aggregates (codes not ISO3 country) using mledoze list
iso = set(ml.cca3) | {"XKX"}
wd = wd[wd.c.isin(iso)]
wd.to_csv(HERE / "wdi_country_year.csv", index=False)
print("WDI:", wd.shape, wd.c.nunique(), "countries; non-missing per var (1996-2023):")
print(wd[wd.y.between(1996, 2023)].drop(columns=["c", "y"]).notna().sum().to_string())

# ---------- PWT ----------
p = pd.read_excel(EXT / "pwt/pwt110.xlsx", sheet_name="Data")
keep = ["countrycode", "year", "rgdpo", "rgdpe", "rgdpna", "cgdpo", "rnna", "rkna", "cn", "emp", "hc", "pop",
        "avh", "labsh", "ctfp", "rtfpna", "delta"]
p = p[keep].rename(columns={"countrycode": "c", "year": "y"})
p = p[p.y >= 1990]
p.to_csv(HERE / "pwt_country_year.csv", index=False)
print("PWT:", p.shape, p.c.nunique(), "countries")
