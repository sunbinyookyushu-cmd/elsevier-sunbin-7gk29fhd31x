"""Per-passenger economy ticket tax payable on a departure from origin country o to destination country d
in year t (EUR, year-weighted by months in force): data/processed/tax_by_origin_dest_year.csv

Band logic per tax (see docs/taxes_*.md). Distances are reference-city -> destination CAPITAL great-circle
(data/processed/band_reference_distances.csv). Statutory annexes (DE/AT/SE/NO/DK) list countries; the distance
rule reproduces them up to a handful of border cases, which the route-level design drops via a +-200 km buffer.
Territorial bands (EEA / EU / 'Europe') use membership-by-year tables below.
"""
import pandas as pd, numpy as np, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
tax = pd.read_csv(root/"data/processed/aviation_taxes_master.csv", dtype=str, keep_default_na=False)
dist = pd.read_csv(root/"data/processed/band_reference_distances.csv")
caps = pd.read_csv(root/"data/processed/country_capitals.csv")
fx = pd.read_csv(root/"stata/fx_eur.csv")
DEST = caps.iso2.dropna().unique().tolist()

EU15 = set("AT BE DE DK ES FI FR GB GR IE IT LU NL PT SE".split())
EU04 = EU15 | set("CY CZ EE HU LT LV MT PL SI SK".split()); EU07 = EU04 | {"BG","RO"}; EU13 = EU07 | {"HR"}
def eu(y):  s = EU15 if y < 2004 else EU04 if y < 2007 else EU07 if y < 2013 else EU13;  return s - ({"GB"} if y >= 2021 else set())
def eea(y): return eu(y) | {"NO","IS","LI"}
EUROPE = set("AL AD AT BA BE BG BY CH CY CZ DE DK EE ES FI FR GB GR HR HU IE IS IT LI LT LU LV MC MD ME MK MT NL NO PL PT RO RS RU SE SI SK SM TR UA VA XK GI FO GL".split())

def km(o, d):
    r = dist[(dist.ref_iso2==o)&(dist.dest_iso2==d)]
    return float(r.dist_km.iloc[0]) if len(r) else np.nan
def miles(o, d): return km(o,d)/1.609344

def band_of(o, d, y, row):
    """Return True if destination d falls in this tax row's band (row = master table row)."""
    b = row.band_id.strip().lower(); up = row.band_upper_km; up = float(up) if up not in ("", "nan") else np.nan
    if o == "GB":
        if b in ("eea",): return d in eea(y) or d == "GB"
        if b in ("non-eea",): return not (d in eea(y) or d == "GB")
        if b == "domestic": return d == "GB"
        if b.startswith("ni-"): return False                      # Northern Ireland carve-out handled separately
        mi = miles(o, d)
        if np.isnan(mi): return False
        if y < 2015 or (y == 2015 and False):
            pass
        if b == "a": return mi <= 2000 and (d != "GB" or y < 2023)
        if b == "b":
            if y >= 2023: return 2000 < mi <= 5500
            if y >= 2015: return mi > 2000
            return 2000 < mi <= 4000
        if b == "c": return mi > 5500 if y >= 2023 else 4000 < mi <= 6000
        if b == "d": return mi > 6000
        return False
    if o == "FR":
        if b in ("eu","european","europe","européenne"):
            return d in eea(y) or d in ("CH","FR","GB","MC","AD") or (y >= 2025 and km("FR", d) <= 1000)
        if b in ("other",): return not (d in eea(y) or d in ("CH","FR","GB","MC","AD"))
        if b in ("intermediate","intermédiaire"): return (not (d in eea(y) or d in ("CH","FR","GB","MC","AD") or km("FR",d) <= 1000)) and km("FR", d) <= 5500
        if b in ("distant","lointaine"): return km("FR", d) > 5500
        return False
    if o == "NL":
        if b == "1": return d in eu(y) or km("NL", d) <= 2500
        if b == "2": return not (d in eu(y) or km("NL", d) <= 2500)
        if b == "flat": return True
        return False
    if o == "IE":
        if b == "b1": return km("IE", d) <= 300
        if b == "b2": return km("IE", d) > 300
        if b in ("flat","all"): return True
        return False
    if o == "BE":
        if b == "b1": return km("BE", d) < 500
        if b == "b2": return km("BE", d) >= 500 and (d in eea(y) or d in ("GB","CH"))
        if b == "b3": return km("BE", d) >= 500 and not (d in eea(y) or d in ("GB","CH"))
        return False
    if o == "NO":
        if b == "flat": return True
        if b == "b1": return d in EUROPE
        if b == "b2": return d not in EUROPE
        return False
    if o == "DK":
        if b == "intl": return d != "DK"
        if b == "all": return True
        if b == "b1": return d in EUROPE
        if b == "b2": return d not in EUROPE and km("DK", d) <= 6000
        if b == "b3": return d not in EUROPE and km("DK", d) > 6000
        return False
    if o == "SE":
        if b == "b1": return d in EUROPE
        if b == "b2": return d not in EUROPE and km("SE", d) <= 6000
        if b == "b3": return d not in EUROPE and km("SE", d) > 6000
        if b == "all": return True
        return False
    if o == "AT":
        if b == "flat": return True
        if b == "under350": return False                           # airport-pair rule; not representable at country level
        if b == "short": return km("AT", d) <= 2500
        if b == "medium": return 2500 < km("AT", d) <= 6000
        if b == "long": return km("AT", d) > 6000
        return False
    if o == "DE":
        k = km("DE", d)
        if b == "1": return k <= 2500
        if b == "2": return 2500 < k <= 6000
        if b == "3": return k > 6000
        return False
    if o == "PT": return b in ("all","flat")
    return False

t = tax[(tax.include_main=="1") & tax["class"].isin(["economy","all"]) & (tax.rate!="") & (tax.valid_from!="")].copy()
t["rate"] = pd.to_numeric(t.rate, errors="coerce"); t = t[t.rate.notna()]
t["vfrom"] = pd.to_datetime(t.valid_from); t["vto"] = pd.to_datetime(t.valid_to.replace("", "2024-12-31"))
rows = []
for _, r in t.iterrows():
    o = r.country_iso
    for y in range(max(1996, r.vfrom.year), min(r.vto.year, 2024)+1):
        s = max(r.vfrom, pd.Timestamp(y,1,1)); e = min(r.vto, pd.Timestamp(y,12,31))
        months = min(12, (e - s).days/30.44 + 1/30.44)
        if months <= 0: continue
        f = fx[(fx.cur==r.currency)&(fx.year==y)].fx
        f = float(f.iloc[0]) if len(f) else 1.0
        for d in DEST:
            if band_of(o, d, y, r):
                rows.append((o, d, y, r.rate*f*months/12, r.band_id, r.instrument))
out = pd.DataFrame(rows, columns=["o_iso","d_iso","year","tau_eur","band_id","instrument"])
# several instruments/periods within a year sum (e.g. FR TSBA uprating mid-year); keep the main band id
agg = out.groupby(["o_iso","d_iso","year"], as_index=False).agg(tau_eur=("tau_eur","sum"), band_id=("band_id","first"))
agg.to_csv(root/"data/processed/tax_by_origin_dest_year.csv", index=False)
print(len(agg), "origin x destination x year rows;", agg.o_iso.nunique(), "taxing origins")
chk = agg[agg.d_iso.isin(["ES","US","IN","JP","AU","DE","GB","TR"]) & agg.year.isin([2010,2012,2016,2019,2023])]
print(chk.pivot_table(index=["o_iso","year"], columns="d_iso", values="tau_eur").round(1).to_string())
