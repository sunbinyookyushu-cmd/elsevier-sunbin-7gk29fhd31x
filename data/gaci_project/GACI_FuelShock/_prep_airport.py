# -*- coding: utf-8 -*-
"""Shared airport x month estimation panel (same sample rules as 12_airport_monthly.py):
airports with a 1996 GACI value and positive 1996 seats, D12 outcomes, 1996 exposures (z-scores over
the airport cross-section), fuel series and shock series. Cached to _main_panel_sep08fix.parquet.
Source = airport_month_sep08fix.parquet: the 2008-09 extract gap interpolated (50_fix_sep2008.py, user decision
2026-10-02). SRC = "airport_month.parquet" reproduces the 9/29 workbooks (cache _main_panel.parquet)."""
import os
import numpy as np
import pandas as pd

SRC = "airport_month_sep08fix.parquet"
CACHE = "_main_panel_sep08fix.parquet" if SRC != "airport_month.parquet" else "_main_panel.parquet"
OUT = ["ln_seats", "ln_flights", "ln_skm", "ln_co2", "ln_gauge", "ln_stage", "ln_int", "ln_seats_dom", "ln_seats_intl"]


def fuel_monthly():
    f = pd.read_csv("fuel_monthly.csv")
    f["year"] = f.ym.str[:4].astype(int)
    f["month"] = f.ym.str[5:7].astype(int)
    idx = f.ym
    # Baumeister-Hamilton demand shocks (economic activity, oil consumption demand, oil inventory demand)
    d = pd.read_excel("data_external/BaumeisterHamilton2019_demand_shocks.xlsx", header=None).iloc[2:, :4]
    d.columns = ["date", "bh_act", "bh_cons", "bh_inv"]
    d = d.dropna(subset=["date"])
    d["ym"] = pd.to_datetime(d.date).dt.to_period("M").astype(str)
    f = f.merge(d.drop(columns="date"), on="ym", how="left")
    # Baumeister (2022) WTI price expectations (12-month ahead) and WTI spot
    e = pd.read_excel("data_external/BaumeisterKilian_WTI_price_expectations.xlsx")
    e = e.iloc[:, :5]
    e.columns = ["date", "e3", "e6", "e9", "e12"]
    e["ym"] = pd.to_datetime(e.date).dt.to_period("M").astype(str)
    f = f.merge(e.drop(columns="date"), on="ym", how="left")
    w = pd.read_csv("data_external/MCOILWTICO.csv")
    w["ym"] = pd.to_datetime(w.observation_date).dt.to_period("M").astype(str)
    f = f.merge(w[["ym", "MCOILWTICO"]], on="ym", how="left")
    f["ln_e12"] = np.log(f.e12) - np.log(f.cpi)                   # real (CPI-deflated) 12-month-ahead expected WTI
    f["ln_wti"] = np.log(f.MCOILWTICO) - np.log(f.cpi)
    f["ln_trans"] = f.ln_wti - f.ln_e12                                                              # spot premium over expected
    f["lnjet_ma12"] = f.lnjet.rolling(12, min_periods=12).mean()
    f["lnjet_dev"] = f.lnjet - f.lnjet_ma12
    for v in ["ln_e12", "ln_trans", "lnjet_ma12", "lnjet_dev"]:
        f[v + "_l3"] = f[v].shift(3)
        f["d12_" + v + "_l3"] = f[v + "_l3"] - f[v + "_l3"].shift(12)
    for s in ["bh_act", "bh_cons", "bh_inv"]:
        f[s + "_s12_l3"] = f[s].rolling(12, min_periods=12).sum().shift(3)
    f["jet_real_l3"] = f.jet_real.shift(3)
    return f


def panel(rebuild=False):
    if os.path.exists(CACHE) and not rebuild:
        return pd.read_parquet(CACHE)
    am = pd.read_parquet(SRC)
    b = pd.read_csv("airport_base.csv")
    b = b[b.GACI_96.notna() & (b.seats_96 > 0)].copy()
    lg = lambda v: np.log(v.where(v > 0))
    b["ln_betw96"] = np.log1p(b.NorBetweenness_96)
    b["fuelseat_96"] = b.int_96 * b.stage_96                     # kg CO2 per departing seat (fuel burn per seat x 3.16)
    raw = {"H_g": b.GACI_96, "H_b": b.ln_betw96, "z_fuelseat": lg(b.fuelseat_96), "z_int": lg(b.int_96),
           "z_stage": lg(b.stage_96), "z_size": lg(b.seats_96), "z_intl": b.intl_share_96, "z_gauge": lg(b.gauge_96)}
    for k, v in raw.items():
        b[k] = (v - v.mean()) / v.std()
    b["Hub10"] = (b.GACI_96 >= b.GACI_96.quantile(0.9)).astype(float)
    keep = ["airport_iata", "Region_96", "seats_96", "fuelseat_96", "int_96", "stage_96", "n_months_9619", "Hub10"] + list(raw)
    am = am[am.airport_iata.isin(b.airport_iata) & am.iso3.notna()].merge(b[keep], on="airport_iata", how="left")
    lag = am[["airport_iata", "t"] + OUT].copy()
    lag["t"] += 12
    am = am.merge(lag, on=["airport_iata", "t"], how="left", suffixes=("", "_m12"))
    for v in OUT:
        am["d12_" + v] = am[v] - am[v + "_m12"]
    am = am.drop(columns=[v + "_m12" for v in OUT])
    f = fuel_monthly()
    fc = [c for c in f.columns if c.startswith(("d12_", "kz", "bh_", "lnjet", "jet_real", "ln_"))]
    am = am.merge(f[["year", "month"] + fc], on=["year", "month"], how="left")
    am["iso_ym"] = am.iso3 + "_" + am.ym
    am["reg_ym"] = am.Region_96 + "_" + am.ym
    am = am[(am.year >= 1997)].copy()
    am.to_parquet(CACHE, index=False)
    return am
