"""Download SendeCO2 daily EUA price CSVs (2008-2025) and build daily + monthly EUA price files.
Also extracts EEX primary-market auction clearing prices (EUA and EUAA) from the EEX archive zip
as a cross-check for the SendeCO2 series.

Source pages (checked 2026-10-02):
  SendeCO2 price page: https://www.sendeco2.com/es/precios-co2
  per-year CSV:        https://www.sendeco2.com/site_sendeco/service/download-csv.php?year=YYYY
  EEX auction archive: https://www.eex.com/fileadmin/EEX/Downloads/Markets/Environmentals/
                       EUA_Emission_Spot_Primary_Market_Auction_Report/Archive_Reports/
                       emission-spot-primary-market-auction-report-2012-2025-data.zip
Outputs (this folder):
  raw_sendeco2/sendeco2_YYYY.csv           raw per-year files as downloaded
  EUA_daily_sendeco2_2008_2025.csv         date, eua_eur (EUR per tCO2), cer_eur
  EUA_monthly_sendeco2_2008_2025.csv       month, mean/min/max/last of daily EUA, n_days
  EEX_auction_prices_2012_2025.csv         auction date, product code, clearing price (EUR)
"""
import os, io, subprocess, zipfile
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw_sendeco2")
os.makedirs(RAW, exist_ok=True)

# 1. SendeCO2 daily files
frames = []
for y in range(2008, 2026):
    fp = os.path.join(RAW, f"sendeco2_{y}.csv")
    if not os.path.exists(fp) or os.path.getsize(fp) < 500:
        subprocess.run(["curl.exe", "-sL", "-A", "Mozilla/5.0", "-o", fp,
                        f"https://www.sendeco2.com/site_sendeco/service/download-csv.php?year={y}"], check=True)
    d = pd.read_csv(fp, sep=";", encoding="iso-8859-15", dtype=str)
    d.columns = [c.strip() for c in d.columns]
    d = d.rename(columns={"Fecha": "date", "EUA": "eua_eur", "CER": "cer_eur"})
    d["date"] = pd.to_datetime(d["date"], format="%d-%m-%Y")
    for c in ["eua_eur", "cer_eur"]:
        d[c] = pd.to_numeric(d[c].str.replace(",", ".", regex=False), errors="coerce")
    frames.append(d[["date", "eua_eur", "cer_eur"]])

daily = pd.concat(frames).sort_values("date").drop_duplicates("date")
daily = daily[daily["eua_eur"] > 0]
daily.to_csv(os.path.join(HERE, "EUA_daily_sendeco2_2008_2025.csv"), index=False, date_format="%Y-%m-%d")

monthly = (daily.set_index("date")["eua_eur"].resample("MS")
           .agg(["mean", "min", "max", "last", "count"]).reset_index())
monthly.columns = ["month", "eua_mean_eur", "eua_min_eur", "eua_max_eur", "eua_last_eur", "n_days"]
monthly = monthly[monthly["n_days"] > 0]
monthly["month"] = monthly["month"].dt.strftime("%Y-%m")
monthly.round(3).to_csv(os.path.join(HERE, "EUA_monthly_sendeco2_2008_2025.csv"), index=False)
print("daily rows", len(daily), daily["date"].min().date(), daily["date"].max().date())
print("monthly rows", len(monthly))

# 2. EEX primary auction clearing prices (cross-check, and EUAA aviation allowances)
zp = os.path.join(HERE, "EEX_emission_spot_primary_auction_report_2012_2025.zip")
rows = []
with zipfile.ZipFile(zp) as z:
    for name in sorted(z.namelist()):
        if not name.endswith((".xls", ".xlsx")):
            continue
        raw = pd.read_excel(io.BytesIO(z.read(name)), sheet_name=0, header=None)
        # find the header row containing 'Date' and 'Auction Price'
        hdr = None
        for i in range(min(15, len(raw))):
            vals = [str(v) for v in raw.iloc[i].tolist()]
            if any(v.strip().lower().startswith("date") for v in vals) and any("auction price" in v.lower() for v in vals):
                hdr = i
                break
        if hdr is None:
            print("header not found", name)
            continue
        df = raw.iloc[hdr + 1:].copy()
        df.columns = [str(c).strip() for c in raw.iloc[hdr].tolist()]
        dcol = [c for c in df.columns if c.lower().startswith("date")][0]
        pcol = [c for c in df.columns if "auction price" in c.lower()][0]
        ncol = [c for c in df.columns if c.lower() == "auction name"]
        ccol = [c for c in df.columns if c.lower() == "contract"]
        vcol = [c for c in df.columns if c.lower().startswith("auction volume")]
        scol = [c for c in df.columns if "status" in c.lower()]
        out = pd.DataFrame({
            "auction_date": pd.to_datetime(df[dcol], errors="coerce", dayfirst=True),
            "auction_name": df[ncol[0]] if ncol else None,
            "contract": df[ccol[0]] if ccol else None,
            "auction_volume_t": pd.to_numeric(df[vcol[0]], errors="coerce") if vcol else None,
            "status": df[scol[0]] if scol else None,
            "clearing_price_eur": pd.to_numeric(df[pcol], errors="coerce"),
            "source_file": os.path.basename(name),
        })
        rows.append(out.dropna(subset=["auction_date", "clearing_price_eur"]))
eex = pd.concat(rows, ignore_index=True).sort_values("auction_date").reset_index(drop=True)
# aviation allowance (EUAA) auctions: contract codes EAA2/EAA3 or 'EUAA' in the auction name
eex["is_euaa"] = (eex["contract"].astype(str).str.contains("EAA", case=False)
                  | eex["auction_name"].astype(str).str.contains("EUAA", case=False))
eex.to_csv(os.path.join(HERE, "EEX_auction_prices_2012_2025.csv"), index=False, date_format="%Y-%m-%d")
print("EEX auction rows", len(eex), eex["auction_date"].min().date(), eex["auction_date"].max().date())
print(eex["contract"].value_counts().head(15))
print("EUAA auctions by year:", eex[eex.is_euaa].groupby(eex["auction_date"].dt.year).size().to_dict())

# 3. Cross-check: SendeCO2 daily vs EEX clearing price on the same day (EUA contracts only)
m = eex.merge(daily, left_on="auction_date", right_on="date", how="inner")
m = m[~m["is_euaa"]]
if len(m):
    diff = (m["eua_eur"] - m["clearing_price_eur"])
    print("same-day matches", len(m), "corr", round(m["eua_eur"].corr(m["clearing_price_eur"]), 4),
          "median abs diff EUR", round(diff.abs().median(), 3), "p95 abs diff", round(diff.abs().quantile(0.95), 3))

