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
def upper_km(txt, band_id=""):
    """Upper distance bound of a band in km. '<=2500 ...' -> 2500; '>2500 and <=6000' -> 6000; '3219-6436' -> 6436;
    '>6000' -> 99999; 'Europe'/'EEA' text or band id with no number -> 2500 (intra-European proxy);
    'non-Europe'/'other'/'non-EEA' -> 99999; 'any' / flat / '' -> NaN."""
    t = str(txt).lower().replace(",", ""); b = str(band_id).lower().strip()
    rng = _re.findall(r"(\d+)\s*-\s*(\d+)", t)
    if rng: return float(rng[-1][1])
    le = _re.findall(r"<=?\s*(\d+)", t); gt = _re.findall(r">=?\s*(\d+)", t)
    if le: return float(le[-1])
    if gt: return 99999.0
    for src in (t, b):
        if "non-europe" in src or "non-eea" in src or "non-eu" in src or "outside" in src or src in ("other","others","rest","lointaine","distant"): return 99999.0
    for src in (t, b):
        if "europe" in src or "eea" in src or src in ("eu","european","européenne","eu/eea"): return 2500.0
    if b in ("intermédiaire","intermediate"): return 5500.0
    return float("nan")
m["band_upper_km"] = [upper_km(t,b) for t,b in zip(m.distance_rule_km, m.band_id)]
# Treatment classification: national per-passenger TICKET TAXES (fiscal/environmental) = main treatment.
# Airport/municipal development charges (IT addizionale comunale, GR spatosimo), departure taxes abolished
# before the window (MT), and 'none' placeholder rows are kept in the table but flagged include_main = 0.
def classify(r):
    ins = r.instrument.lower()
    if ins.startswith("none") or r.rate == "" : return 0
    if r.country_iso in ("IT","GR","MT"): return 0
    if ins.startswith("taxe de l'aviation civile") or ins.startswith("taxe de l\u2019aviation civile"): return 0  # FR TAC: DGAC funding charge replacing earlier airport charges (1999); not a new ticket tax
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
