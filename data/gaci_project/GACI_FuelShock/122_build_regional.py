# -*- coding: utf-8 -*-
"""Build the regional (NUTS2) datasets for stata_paper/04_regional_benefits.do (user 2026-10-03, HANDOFF_aviation_tax.md).
All data preparation is done here so that the do-file stays fully inline (no programs, loops, locals).

Inputs
  stata_paper/stack_month.dta, stack_year.dta, events.dta   (from 120_export_stata_all.py)
  hub_panel.csv                                             airport coordinates (latitude_deg, longitude_deg)
  country_year.csv                                          lngdp lnpop (country x year)
  data_external/eurostat/NUTS_LB_2021_4326_LEVL_2.geojson    GISCO NUTS2 label points (2021)
  data_external/eurostat/tour_occ_nin2.tsv                  nights at tourist accommodation, NUTS2, ANNUAL, DOM / FOR / TOTAL (no monthly NUTS2 table exists)
  data_external/eurostat/tour_occ_nim.tsv                   nights at tourist accommodation, COUNTRY, monthly, DOM / FOR / TOTAL
  data_external/eurostat/lfst_r_lfe2en2.tsv                 employment by NACE, NUTS2, annual (2008-), TOTAL and G-I
  data_external/eurostat/nama_10r_2gdp.tsv                  GDP per head (EUR_HAB), NUTS2, annual (2000-)
Outputs (stata_paper/)
  reg_expo.dta    stk x nuts2: catchment seats, small / mid / large exposure, border flag
  reg_month.dta   stk x nuts2 x month: catchment seats and CO2 (regional connectivity), calendar flags, FE ids
  nat_month.dta   stk x country x month: nights (dom, for, tot) for the treated and control countries, calendar flags, FE ids
  reg_year.dta    stk x nuts2 x year: nights (annual NUTS2), employment (total, G-I), GDP per head, catchment GACI and destinations
  bc_inputs.dta   stk: treated-airport CO2 (tonnes) and seats in the first tax year, seat-weighted dose, revenue base
Parameters: catchment radius 100 km, distance decay 50 km (weight exp(-d/50)).
Size classes for ALL stack airports use the treated country's tercile cut-offs of pre-year seats (w0), so that control
regions have a non-degenerate small-airport exposure (the triple difference needs it).
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi
import json
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
OUT = "stata_paper"
EXT = os.path.join("data_external", "eurostat")
RADIUS, DECAY = 100.0, 50.0
EUR = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT", "ESP", "GRC", "HUN", "HRV", "MLT"}
ISO2 = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "CH": "CHE", "CY": "CYP", "CZ": "CZE", "DE": "DEU", "DK": "DNK", "EE": "EST", "EL": "GRC", "ES": "ESP",
        "FI": "FIN", "FR": "FRA", "HR": "HRV", "HU": "HUN", "IE": "IRL", "IS": "ISL", "IT": "ITA", "LI": "LIE", "LT": "LTU", "LU": "LUX", "LV": "LVA",
        "MT": "MLT", "NL": "NLD", "NO": "NOR", "PL": "POL", "PT": "PRT", "RO": "ROU", "SE": "SWE", "SI": "SVN", "SK": "SVK", "UK": "GBR", "TR": "TUR",
        "RS": "SRB", "ME": "MNE", "MK": "MKD", "AL": "ALB"}

# ---------------- airports and NUTS2 label points ----------------
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "latitude_deg", "longitude_deg"]).dropna().drop_duplicates("airport_iata")
hp.columns = ["airport", "lat", "lon"]
gj = json.load(open(os.path.join(EXT, "NUTS_LB_2021_4326_LEVL_2.geojson"), encoding="utf-8"))
nuts = pd.DataFrame([(f["properties"]["NUTS_ID"], f["properties"]["CNTR_CODE"], f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0])
                     for f in gj["features"]], columns=["nuts2", "cntr", "rlat", "rlon"])
nuts["iso3"] = nuts.cntr.map(ISO2)
nuts = nuts.dropna(subset=["iso3"])

# ---------------- stacks ----------------
cols_m = ["airport", "iso3", "stk", "eur", "year", "month", "t", "treat", "border", "w0", "sz_small", "sz_mid", "sz_large", "dose",
          "post1", "post2", "pre36_25", "pre24_13", "donut", "ln_seats", "ln_co2"]
sm = pd.read_stata(os.path.join(OUT, "stack_month.dta"), columns=cols_m)
sm = sm[sm.eur == 1].copy()
sy = pd.read_stata(os.path.join(OUT, "stack_year.dta"), columns=["airport", "iso3", "stk", "eur", "year", "k", "post1", "treat", "border", "w0", "ln_gaci", "ln_deg"])
sy = sy[sy.eur == 1].copy()
ev = pd.read_stata(os.path.join(OUT, "events.dta"))
ev = ev[ev.zone == "EUR"]
cy = pd.read_csv("country_year.csv", usecols=["c", "y", "lngdp", "lnpop"]).rename(columns={"c": "iso3", "y": "year"})

apc = sm.groupby(["stk", "airport", "iso3"], as_index=False).agg(w0=("w0", "max"), treat=("treat", "max"), border=("border", "max"),
                                                                  sz_small=("sz_small", "max"), sz_mid=("sz_mid", "max"), sz_large=("sz_large", "max"))
# size class for every airport from the treated country's tercile cut-offs
apc["small_all"] = apc["mid_all"] = apc["large_all"] = 0
for k, g in apc.groupby("stk"):
    tr = g[(g.treat == 1) & (g.w0 > 0)].w0
    q1, q2 = tr.quantile(1 / 3), tr.quantile(2 / 3)
    idx = g.index[g.w0 > 0]
    apc.loc[idx, "small_all"] = (apc.loc[idx, "w0"] <= q1).astype(int)
    apc.loc[idx, "mid_all"] = ((apc.loc[idx, "w0"] > q1) & (apc.loc[idx, "w0"] <= q2)).astype(int)
    apc.loc[idx, "large_all"] = (apc.loc[idx, "w0"] > q2).astype(int)
    # check against the stack's own treated terciles
    chk = g[g.treat == 1]
    agree = ((chk.sz_small == apc.loc[chk.index, "small_all"]) & (chk.sz_large == apc.loc[chk.index, "large_all"])).mean()
    print(f"stk {k}: treated terciles cut at {q1:,.0f} / {q2:,.0f} seats; agreement with stack sz_* = {agree:.2f}")

# ---------------- catchment pairs (haversine) ----------------
ap = hp[hp.airport.isin(apc.airport.unique())].reset_index(drop=True)
print("stack airports", apc.airport.nunique(), "| with coordinates", len(ap))
la1, lo1 = np.radians(nuts.rlat.values)[:, None], np.radians(nuts.rlon.values)[:, None]
la2, lo2 = np.radians(ap.lat.values)[None, :], np.radians(ap.lon.values)[None, :]
a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
dkm = 2 * 6371.0 * np.arcsin(np.sqrt(a))
ii, jj = np.where(dkm <= RADIUS)
pairs = pd.DataFrame({"nuts2": nuts.nuts2.values[ii], "airport": ap.airport.values[jj], "dkm": dkm[ii, jj]})
pairs["wdist"] = np.exp(-pairs.dkm / DECAY)
print("catchment pairs", len(pairs), "| regions with >=1 airport", pairs.nuts2.nunique(), "of", len(nuts))

# ---------------- exposure per event x region ----------------
ex = apc.merge(pairs, on="airport")
ex["ww"] = ex.wdist * ex.w0
for s in ["small", "mid", "large"]:
    ex[f"ww_{s}"] = ex.ww * ex[f"{s}_all"]
ex["ww_b"] = ex.ww * ex.border
ex["ww_t"] = ex.ww * ex.treat
expo = ex.groupby(["stk", "nuts2"], as_index=False).agg(catch_seats=("ww", "sum"), ww_small=("ww_small", "sum"), ww_mid=("ww_mid", "sum"), ww_large=("ww_large", "sum"),
                                                        ww_b=("ww_b", "sum"), ww_t=("ww_t", "sum"), border_any=("border", "max"), n_ap=("airport", "nunique"))
expo = expo[expo.catch_seats > 0].copy()
for s in ["small", "mid", "large"]:
    expo[f"expo_{s}"] = expo[f"ww_{s}"] / expo.catch_seats
expo["border_share"] = expo.ww_b / expo.catch_seats
expo["border_r"] = expo.border_any.astype(int)
expo["treat_share"] = expo.ww_t / expo.catch_seats
expo = expo.merge(nuts[["nuts2", "iso3"]], on="nuts2")

# ---------------- regional connectivity ----------------
smc = sm[["stk", "airport", "t", "ln_seats", "ln_co2"]].copy()
smc["seats"], smc["co2"] = np.exp(smc.ln_seats), np.exp(smc.ln_co2)
cm = smc.merge(pairs[["nuts2", "airport", "wdist"]], on="airport")
cm["ws"], cm["wc"] = cm.wdist * cm.seats, cm.wdist * cm.co2.fillna(0)
conn_m = cm.groupby(["stk", "nuts2", "t"], as_index=False).agg(ws=("ws", "sum"), wc=("wc", "sum"))
conn_m["ln_conn_seats"] = np.log(conn_m.ws.where(conn_m.ws > 0))
conn_m["ln_conn_co2"] = np.log(conn_m.wc.where(conn_m.wc > 0))
syc = sy[["stk", "airport", "year", "w0", "ln_gaci", "ln_deg"]].dropna(subset=["ln_gaci"]).copy()
syc["gaci"], syc["deg"] = np.exp(syc.ln_gaci), np.exp(syc.ln_deg)
cyv = syc.merge(pairs[["nuts2", "airport", "wdist"]], on="airport")
cyv["wk"] = cyv.wdist * cyv.w0
cyv["g"], cyv["d"] = cyv.wk * cyv.gaci, cyv.wk * cyv.deg
conn_y = cyv.groupby(["stk", "nuts2", "year"], as_index=False).agg(g=("g", "sum"), d=("d", "sum"), wk=("wk", "sum"))
conn_y = conn_y[conn_y.wk > 0]
conn_y["ln_conn_gaci"] = np.log(conn_y.g / conn_y.wk)
conn_y["ln_conn_deg"] = np.log(conn_y.d / conn_y.wk)

# ---------------- Eurostat ----------------


def eurostat(name, keys):
    d = pd.read_csv(os.path.join(EXT, name + ".tsv"), sep="\t", dtype=str)
    kcol = d.columns[0]
    kk = d[kcol].str.split(",", expand=True)
    kk.columns = keys
    d = pd.concat([kk, d.drop(columns=kcol)], axis=1)
    d = d.melt(id_vars=keys, var_name="period", value_name="raw")
    d["period"] = d.period.str.strip()
    d["val"] = pd.to_numeric(d.raw.str.strip().str.split(" ").str[0].replace(":", np.nan), errors="coerce")
    return d.drop(columns="raw")


# annual NUTS2 nights (tour_occ_nin2); monthly nights exist only at country level (tour_occ_nim)
tour = eurostat("tour_occ_nin2", ["freq", "c_resid", "unit", "nace_r2", "geo"])
tour = tour[(tour.unit == "NR") & (tour.nace_r2 == "I551-I553") & (tour.geo.str.len() == 4) & tour.c_resid.isin(["DOM", "FOR", "TOTAL"])]
tour["year"] = tour.period.astype(int)
tour = tour.pivot_table(index=["geo", "year"], columns="c_resid", values="val", aggfunc="first").reset_index()
tour.columns = ["nuts2", "year", "nights_dom", "nights_for", "nights_tot"]
nat = eurostat("tour_occ_nim", ["freq", "c_resid", "unit", "nace_r2", "geo"])
nat = nat[(nat.unit == "NR") & (nat.nace_r2 == "I551-I553") & (nat.geo.str.len() == 2) & nat.c_resid.isin(["DOM", "FOR", "TOTAL"])].copy()
nat["t"] = nat.period.str[:4].astype(int) * 12 + nat.period.str[5:7].astype(int)
nat = nat.pivot_table(index=["geo", "t"], columns="c_resid", values="val", aggfunc="first").reset_index()
nat.columns = ["geo", "t", "nights_dom", "nights_for", "nights_tot"]
nat["iso3"] = nat.geo.map(ISO2)
nat = nat.dropna(subset=["iso3"]).drop(columns="geo")
emp = eurostat("lfst_r_lfe2en2", ["freq", "nace_r2", "age", "sex", "unit", "geo"])
emp = emp[(emp.age == "Y15-64") & (emp.sex == "T") & (emp.unit == "THS_PER") & (emp.geo.str.len() == 4) & emp.nace_r2.isin(["TOTAL", "G-I"])]
emp["year"] = emp.period.astype(int)
emp = emp.pivot_table(index=["geo", "year"], columns="nace_r2", values="val", aggfunc="first").reset_index()
emp.columns = ["nuts2", "year", "emp_GI", "emp_tot"]
gdp = eurostat("nama_10r_2gdp", ["freq", "unit", "geo"])
gdp = gdp[(gdp.unit == "EUR_HAB") & (gdp.geo.str.len() == 4)].copy()
gdp["year"] = gdp.period.astype(int)
gdp = gdp[["geo", "year", "val"]].rename(columns={"geo": "nuts2", "val": "gdp_pc"})
print("Eurostat NUTS2 codes matched to GISCO 2021: nights", tour.nuts2.isin(nuts.nuts2).mean().round(3), "| employment", emp.nuts2.isin(nuts.nuts2).mean().round(3),
      "| gdp", gdp.nuts2.isin(nuts.nuts2).mean().round(3))

# ---------------- calendar and country roles per event ----------------
cal = sm.groupby(["stk", "t"], as_index=False).agg(year=("year", "first"), month=("month", "first"), post1=("post1", "max"), post2=("post2", "max"),
                                                   pre36_25=("pre36_25", "max"), pre24_13=("pre24_13", "max"), donut=("donut", "max"))
roles = []
for k, g in sm.groupby("stk"):
    tiso = g[g.treat == 1].iso3.iloc[0]
    ctrl = sorted(set(g[(g.treat == 0) & (g.border == 0)].iso3) & EUR)
    roles.append((k, tiso, ctrl))
    print(f"stk {k} treated {tiso}; control countries {len(ctrl)}: {' '.join(ctrl)}")
caly = sy.groupby(["stk", "year"], as_index=False).agg(k=("k", "first"), post1=("post1", "max"))


def add_fe(D, monthly):
    D = D.merge(cy, on=["iso3", "year"], how="left")
    D["nuts2n"] = pd.factorize(D.nuts2)[0] + 1
    if monthly:
        D["fe_r"] = pd.factorize(D.stk.astype(str) + "_" + D.nuts2 + "_" + D.month.astype(str))[0] + 1
        D["fe_ct"] = pd.factorize(D.stk.astype(str) + "_" + D.iso3 + "_" + D.t.astype(str))[0] + 1
        D["ym"] = (D.year - 1960) * 12 + D.month - 1
    else:
        D["fe_ry"] = pd.factorize(D.stk.astype(str) + "_" + D.nuts2)[0] + 1
        D["fe_cy"] = pd.factorize(D.stk.astype(str) + "_" + D.iso3 + "_" + D.year.astype(str))[0] + 1
    return D


# ---------------- monthly regional panel ----------------
pm, py_, nm_ = [], [], []
for k, tiso, ctrl in roles:
    reg = expo[(expo.stk == k) & expo.iso3.isin(ctrl + [tiso])].copy()
    reg["treat_c"] = (reg.iso3 == tiso).astype(int)
    c = cal[cal.stk == k].drop(columns="stk")
    d = reg.merge(c, how="cross")
    d = d.merge(conn_m[conn_m.stk == k].drop(columns="stk"), on=["nuts2", "t"], how="left")
    pm.append(d)
    cn = pd.DataFrame({"iso3": ctrl + [tiso]})
    cn["stk"] = k
    cn["treat_c"] = (cn.iso3 == tiso).astype(int)
    cn = cn.merge(c, how="cross").merge(nat, on=["iso3", "t"], how="left")
    nm_.append(cn)
    yv = caly[caly.stk == k].drop(columns="stk")
    dy = reg.merge(yv, how="cross")
    dy = dy.merge(conn_y[conn_y.stk == k].drop(columns="stk"), on=["nuts2", "year"], how="left")
    py_.append(dy)
PM = pd.concat(pm, ignore_index=True)
PM = add_fe(PM, True)
NM = pd.concat(nm_, ignore_index=True)
NM = NM.merge(cy, on=["iso3", "year"], how="left")
NM["iso3n"] = pd.factorize(NM.iso3)[0] + 1
NM["fe_cm"] = pd.factorize(NM.stk.astype(str) + "_" + NM.iso3 + "_" + NM.month.astype(str))[0] + 1
NM["fe_t"] = pd.factorize(NM.stk.astype(str) + "_" + NM.t.astype(str))[0] + 1
NM["ym"] = (NM.year - 1960) * 12 + NM.month - 1
for v in ["nights_dom", "nights_for", "nights_tot"]:
    NM["ln_" + v] = np.log(NM[v].where(NM[v] > 0))
PY = pd.concat(py_, ignore_index=True)
PY = PY.merge(tour, on=["nuts2", "year"], how="left").merge(emp, on=["nuts2", "year"], how="left").merge(gdp, on=["nuts2", "year"], how="left")
PY = add_fe(PY, False)
for v in ["nights_dom", "nights_for", "nights_tot", "emp_GI", "emp_tot", "gdp_pc"]:
    PY["ln_" + v] = np.log(PY[v].where(PY[v] > 0))

# ---------------- benefit / cost inputs: treated airports, first tax year ----------------
tr = sm[(sm.treat == 1) & (sm.post1 == 1) & (sm.donut == 0)].copy()
tr["seats"], tr["co2_kg"] = np.exp(tr.ln_seats), np.exp(tr.ln_co2)
bc = tr.groupby("stk", as_index=False).agg(iso3=("iso3", "first"), co2_post_t=("co2_kg", lambda x: x.sum() / 1000.0), seats_post=("seats", "sum"),
                                           rev_base=("dose", lambda x: (x * tr.loc[x.index, "seats"]).sum()), n_airports=("airport", "nunique"))
bc["dose_w"] = bc.rev_base / bc.seats_post
bc = bc.merge(ev[["stk", "eff", "ann"]], on="stk")

# ---------------- diagnostics and output ----------------
print("\nmonthly panel", PM.shape, "| annual panel", PY.shape)
diag = PM[PM.treat_c == 1].groupby("stk").agg(iso3=("iso3", "first"), regions=("nuts2", "nunique"), conn_cov=("ln_conn_seats", lambda x: x.notna().mean()),
                                              expo_small_mean=("expo_small", "mean"), expo_small_sd=("expo_small", "std"))
print("treated-country regions, monthly connectivity coverage and exposure:\n", diag.round(3).to_string())
dn = NM.groupby(["stk", "treat_c"]).agg(n_c=("iso3", "nunique"), for_cov=("ln_nights_for", lambda x: x.notna().mean()), dom_cov=("ln_nights_dom", lambda x: x.notna().mean()))
print("national monthly nights coverage (treat_c 1 = treated country):\n", dn.round(3).to_string())
diag2 = PY[PY.treat_c == 1].groupby("stk").agg(nights=("ln_nights_for", lambda x: x.notna().mean()), emp=("ln_emp_GI", lambda x: x.notna().mean()), gdp=("ln_gdp_pc", lambda x: x.notna().mean()))
print("treated-country regions, annual coverage:\n", diag2.round(3).to_string())
print("control regions per event:\n", PM[PM.treat_c == 0].groupby("stk").nuts2.nunique().to_string())
print("\nbenefit inputs:\n", bc.round(1).to_string())
keep_e = ["stk", "nuts2", "iso3", "catch_seats", "n_ap", "expo_small", "expo_mid", "expo_large", "border_r", "border_share", "treat_share"]
expo[keep_e].to_stata(os.path.join(OUT, "reg_expo.dta"), write_index=False, version=118)
keep_m = ["stk", "nuts2", "nuts2n", "iso3", "treat_c", "border_r", "border_share", "year", "month", "t", "ym", "post1", "post2", "pre36_25", "pre24_13", "donut",
          "expo_small", "expo_mid", "expo_large", "catch_seats", "n_ap", "ln_conn_seats", "ln_conn_co2", "lngdp", "lnpop", "fe_r", "fe_ct"]
NM[["stk", "iso3", "iso3n", "treat_c", "year", "month", "t", "ym", "post1", "post2", "pre36_25", "pre24_13", "donut", "nights_dom", "nights_for", "nights_tot",
    "ln_nights_dom", "ln_nights_for", "ln_nights_tot", "lngdp", "lnpop", "fe_cm", "fe_t"]].to_stata(os.path.join(OUT, "nat_month.dta"), write_index=False, version=118)
PM[keep_m].to_stata(os.path.join(OUT, "reg_month.dta"), write_index=False, version=118)
keep_y = ["stk", "nuts2", "nuts2n", "iso3", "treat_c", "border_r", "border_share", "year", "k", "post1", "expo_small", "expo_mid", "expo_large", "catch_seats", "n_ap",
          "nights_dom", "nights_for", "nights_tot", "emp_GI", "emp_tot", "gdp_pc", "ln_nights_dom", "ln_nights_for", "ln_nights_tot", "ln_emp_GI", "ln_emp_tot", "ln_gdp_pc",
          "ln_conn_gaci", "ln_conn_deg", "lngdp", "lnpop", "fe_ry", "fe_cy"]
PY[keep_y].to_stata(os.path.join(OUT, "reg_year.dta"), write_index=False, version=118)
bc.to_stata(os.path.join(OUT, "bc_inputs.dta"), write_index=False, version=118)
pairs.to_csv(os.path.join(OUT, "catch_pairs.csv"), index=False)
print("written: reg_expo.dta reg_month.dta nat_month.dta reg_year.dta bc_inputs.dta catch_pairs.csv")
