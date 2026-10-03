# -*- coding: utf-8 -*-
"""Monthly and annual fuel-price and oil-shock series for the fuel-shock x network-position study.

Sources (data_external/):
  MJFUELUSGULF.csv  EIA US Gulf Coast kerosene-type jet fuel spot, $/gal, monthly (FRED)
  MCOILBRENTEU.csv  Brent spot, $/bbl, monthly (FRED)
  CPIAUCSL.csv      US CPI-U, SA (FRED) -> real 2019 dollars
  Kaenzig_oilSupplyNewsShocks_2025M12.xlsx   Kaenzig (2021 AER) oil supply news shock, monthly
  BaumeisterHamilton2019_oil_supply_shocks.xlsx  BH (2019 AER) structural oil supply shock, monthly

Outputs:
  fuel_monthly.csv  ym (YYYY-MM), year, month, prices, logs, lags, 12-month differences, shocks
  fuel_annual.csv   calendar-year averages / sums
Sign convention: Kaenzig news shock > 0 raises the oil price. BH supply shock > 0 is a supply
INCREASE (lowers the price), so it is multiplied by -1 here ("bh_neg") so that both instruments
push the price up.
"""
import numpy as np
import pandas as pd

X = "data_external/"

def fred(f, col):
    d = pd.read_csv(X + f)
    d["ym"] = pd.to_datetime(d.observation_date).dt.to_period("M")
    return d.set_index("ym")[col].rename(col)

jet = fred("MJFUELUSGULF.csv", "MJFUELUSGULF")
brent = fred("MCOILBRENTEU.csv", "MCOILBRENTEU")
cpi = fred("CPIAUCSL.csv", "CPIAUCSL")

k = pd.read_excel(X + "Kaenzig_oilSupplyNewsShocks_2025M12.xlsx", sheet_name="Monthly")
k["ym"] = pd.PeriodIndex(k["Date"].str.replace("M", "-"), freq="M")
k = k.set_index("ym")
kp = pd.read_excel(X + "Kaenzig_oilSupplyNewsShocks_2025M12.xlsx", sheet_name="Monthly (pre-Covid)")
kp["ym"] = pd.PeriodIndex(kp["Date"].str.replace("M", "-"), freq="M")
kp = kp.set_index("ym")

bh = pd.read_excel(X + "BaumeisterHamilton2019_oil_supply_shocks.xlsx", header=None).iloc[2:, :2]
bh.columns = ["date", "bh"]
bh = bh.dropna()
bh["ym"] = pd.to_datetime(bh.date).dt.to_period("M")
bh = bh.set_index("ym")["bh"].astype(float)

idx = pd.period_range("1975-01", "2026-08", freq="M")
m = pd.DataFrame(index=idx)
m["jet_nom"] = jet
m["brent_nom"] = brent
m["cpi"] = cpi
m["kz"] = k["Oil supply news shock"]
m["kz_pre"] = kp["Oil supply news shock"]
m["kz_surprise"] = k["Oil supply surprise series"]
m["bh_neg"] = -bh

cpi19 = m.loc["2019-01":"2019-12", "cpi"].mean()
m["jet_real"] = m.jet_nom * cpi19 / m.cpi
m["brent_real"] = m.brent_nom * cpi19 / m.cpi
m["brent_gal_real"] = m.brent_real / 42.0
m["lnjet"] = np.log(m.jet_real)
m["lnbrent"] = np.log(m.brent_real)
m["lnjet_nom"] = np.log(m.jet_nom)
m["lncrack"] = m.lnjet - np.log(m.brent_gal_real)     # jet-specific (refining) component

# cumulated shocks (level analogues of the log price) and rolling 12-month sums
for s in ["kz", "kz_pre", "bh_neg"]:
    m[s + "_cum"] = m[s].fillna(0).cumsum().where(m[s].notna() | (m.index < m[s].first_valid_index()))
    m[s + "_s12"] = m[s].rolling(12, min_periods=12).sum()

# trailing averages and lags of the log price
for v in ["lnjet", "lnbrent", "lncrack", "lnjet_nom"]:
    m[v + "_ma6"] = m[v].shift(1).rolling(6, min_periods=6).mean()
    for L in [1, 3, 6, 9, 12]:
        m[f"{v}_l{L}"] = m[v].shift(L)
# 12-month differences
for v in list(m.columns):
    if v.startswith(("lnjet", "lnbrent", "lncrack")) or v.endswith("_cum"):
        m["d12_" + v] = m[v] - m[v].shift(12)
# rolling 12-month sums of shocks, lagged (instrument for d12 of a lagged price)
for s in ["kz", "kz_pre", "bh_neg"]:
    for L in [1, 3, 6]:
        m[f"{s}_s12_l{L}"] = m[s + "_s12"].shift(L)

m = m.reset_index().rename(columns={"index": "ym"})
m["year"] = m.ym.dt.year
m["month"] = m.ym.dt.month
m["ym"] = m.ym.astype(str)
m = m[(m.year >= 1990)]
m.to_csv("fuel_monthly.csv", index=False)

# ---- annual ----
a = m.groupby("year").agg(jet_real=("jet_real", "mean"), jet_nom=("jet_nom", "mean"),
                          brent_real=("brent_real", "mean"), kz=("kz", "sum"),
                          kz_pre=("kz_pre", "sum"), bh_neg=("bh_neg", "sum"),
                          nm=("jet_real", "count")).reset_index()
a["lnjet"] = np.log(a.jet_real)
a["lnbrent"] = np.log(a.brent_real)
a["lnjet_nom"] = np.log(a.jet_nom)
a["lncrack"] = a.lnjet - np.log(a.brent_real / 42)
# annual analogue of the cumulated shock = calendar-year MEAN of the monthly cumulated series,
# so that its first difference lines up with the difference of annual-average log prices
cumavg = m.groupby("year")[["kz_cum", "kz_pre_cum", "bh_neg_cum"]].mean().reset_index()
a = a.merge(cumavg, on="year", how="left")
a["lnjet_l1"] = a.lnjet.shift(1)
a["kz_l1"] = a.kz.shift(1)
a["bh_neg_l1"] = a.bh_neg.shift(1)
for v in ["lnjet", "lnbrent", "lncrack", "kz_cum", "kz_pre_cum", "bh_neg_cum"]:
    a["d_" + v] = a[v].diff()
a.to_csv("fuel_annual.csv", index=False)

# ---- quick first-stage diagnostics (time series) ----
mm = m[(m.year >= 1997) & (m.year <= 2019)].dropna(subset=["d12_lnjet", "kz_s12", "bh_neg_s12"])
print("monthly 1997-2019: corr(d12 lnjet, kz_s12) = %.3f; corr(d12 lnjet, bh_neg_s12) = %.3f"
      % (mm.d12_lnjet.corr(mm.kz_s12), mm.d12_lnjet.corr(mm.bh_neg_s12)))
aa = a[(a.year >= 1997) & (a.year <= 2019)]
print("annual 1997-2019: corr(d lnjet, d kz_cum) = %.3f; corr(d lnjet, d bh_neg_cum) = %.3f; corr(lnjet, kz_cum) = %.3f; corr(lnjet, bh_neg_cum) = %.3f"
      % (aa.d_lnjet.corr(aa.d_kz_cum), aa.d_lnjet.corr(aa.d_bh_neg_cum), aa.lnjet.corr(aa.kz_cum), aa.lnjet.corr(aa.bh_neg_cum)))
print(a[(a.year >= 1996) & (a.year <= 2024)][["year", "jet_nom", "jet_real", "brent_real", "kz", "bh_neg"]].round(2).to_string(index=False))
