"""Merge the per-country-group tax tables into one master table with validation.
Input : data/raw/taxes/taxes_*.csv (schema in docs/data_collection.md)
Output: data/processed/aviation_taxes_master.csv ; prints a coverage summary (country x years in force)."""
import pandas as pd, pathlib, glob
root = pathlib.Path(__file__).resolve().parents[1]
COLS = "country_iso,country,instrument,valid_from,valid_to,band_id,band_definition,distance_rule_km,class,rate,currency,unit,exemptions,legal_basis,source_url,confidence,notes".split(",")
frames = []
for f in sorted(glob.glob(str(root/"data/raw/taxes/taxes_*.csv"))):
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    missing = [c for c in COLS if c not in d.columns]
    if missing: print("!! missing columns in", f, missing)
    for c in COLS:
        if c not in d.columns: d[c] = ""
    d = d[COLS]; d["source_file"] = pathlib.Path(f).name; frames.append(d)
m = pd.concat(frames, ignore_index=True)
m["valid_from_dt"] = pd.to_datetime(m.valid_from, errors="coerce"); m["valid_to_dt"] = pd.to_datetime(m.valid_to.replace("", None), errors="coerce")
m["rate_num"] = pd.to_numeric(m.rate, errors="coerce")
import re as _re
def upper_km(txt):
    """Upper distance bound of a band in km: '<=2500 ...' -> 2500; '>2500 and <=6000' -> 6000; '>6000' -> 99999; 'any'/'' -> NaN."""
    t = str(txt).lower().replace(",", "")
    le = _re.findall(r"<=\s*(\d+)", t); gt = _re.findall(r">\s*(\d+)", t)
    if le: return float(le[-1])
    if gt: return 99999.0
    return float("nan")
m["band_upper_km"] = m.distance_rule_km.map(upper_km)
# Treatment classification: national per-passenger TICKET TAXES (fiscal/environmental) = main treatment.
# Airport/municipal development charges (IT addizionale comunale, GR spatosimo), departure taxes abolished
# before the window (MT), and 'none' placeholder rows are kept in the table but flagged include_main = 0.
def classify(r):
    ins = r.instrument.lower()
    if ins.startswith("none") or r.rate == "" : return 0
    if r.country_iso in ("IT","GR","MT"): return 0
    return 1
m["include_main"] = m.apply(classify, axis=1)
bad = m[m.valid_from_dt.isna() | (m.rate_num.isna() & (m.rate!=""))]
if len(bad): print("!! rows with unparseable dates/rates:\n", bad[["country_iso","instrument","valid_from","valid_to","band_id","class","rate"]].to_string())
m = m.sort_values(["country_iso","valid_from_dt","band_id","class"]).drop(columns=["valid_from_dt","valid_to_dt","rate_num"])
m = m[COLS[:8]+["band_upper_km"]+COLS[8:]+["include_main","source_file"]]
m.to_csv(root/"data/processed/aviation_taxes_master.csv", index=False)
print(len(m), "rows;", m.country_iso.nunique(), "countries;", m.groupby("country_iso").size().to_dict())
print("confidence:", m.confidence.value_counts().to_dict())
# years in force per country (economy/all rows)
e = m[m["class"].isin(["economy","all"])].copy()
e["y0"] = pd.to_datetime(e.valid_from).dt.year; e["y1"] = pd.to_datetime(e.valid_to.replace("", "2024-12-31")).dt.year
cov = e.groupby("country_iso").apply(lambda g: f"{g.y0.min()}–{g.y1.max()}")
print(cov.to_string())
