"""Build the (o_iso, d_iso, year) liberalisation panel from the agreement tables, 1990-2024.
Inputs : data_external/agreements/us_open_skies_partners.csv, eu_regional_agreements.csv (agent-compiled, ISO3 codes)
Output : asa_pair_year.csv  with open_us open_eu open_regional open_any first_year (symmetric pairs, ISO2)
Rules  : treatment starts in the first FULL year after entry into force / provisional application (if in force on or
         before 1 July, that year counts). Signature-only rows (no in-force date) use date_signed + 1 year, flagged.
"""
import pandas as pd, numpy as np, pathlib, itertools
here = pathlib.Path(__file__).resolve().parent
caps = pd.read_csv(here.parents[2]/"data/processed/country_capitals.csv")[["iso2","iso3"]].dropna()
iso3to2 = dict(zip(caps.iso3, caps.iso2))
EU_ACCESSION = {**{c:1995 for c in "AT BE DE DK ES FI FR GB GR IE IT LU NL PT SE".split()}, **{c:2004 for c in "CY CZ EE HU LT LV MT PL SI SK".split()}, "BG":2007,"RO":2007,"HR":2013}
def start_year(d_force, d_prov, d_sign):
    for d in (d_force, d_prov):
        d = pd.to_datetime(d, errors="coerce")
        if pd.notna(d): return d.year if d.month <= 7 else d.year + 1, "in_force"
    d = pd.to_datetime(d_sign, errors="coerce")
    if pd.notna(d): return d.year + 1, "signed_only"
    return None, "no_date"
rows = []
# --- US bilateral open skies ---
us = pd.read_csv(here/"data_external/agreements/us_open_skies_partners.csv", dtype=str, keep_default_na=False)
for _, r in us.iterrows():
    p = iso3to2.get(r.partner_iso3.strip().upper())
    if not p or "open skies" not in r.agreement_type.lower(): continue
    y, how = start_year(r.date_in_force, r.provisional_application, r.date_signed)
    if y: rows.append(("US", p, y, "open_us", how))
# --- EU and regional agreements ---
eu = pd.read_csv(here/"data_external/agreements/eu_regional_agreements.csv", dtype=str, keep_default_na=False)
for _, r in eu.iterrows():
    y, how = start_year(r.date_in_force, r.date_provisional, r.date_signed)
    p = iso3to2.get(r.party_b_iso3.strip().upper())
    if not y or not p: continue
    a = r.bloc_or_party_a.strip().upper()
    if a in ("EU","EUROPEAN UNION","EC"):
        for m, acc in EU_ACCESSION.items():                      # every member in the EU at that time
            if acc <= y and m != p: rows.append((m, p, max(y, acc), "open_eu", how))
    elif a in ("ASEAN","MALIAT","SAATM","CLAC","ANZ") or "regional" in r.agreement_type.lower():
        rows.append((a, p, y, "open_regional_member", how))      # member accession rows; pairs formed below
    else:
        a2 = iso3to2.get(a, a if len(a)==2 else None)
        if a2: rows.append((a2, p, y, "open_regional", how))
df = pd.DataFrame(rows, columns=["a","b","year","kind","how"])
# regional blocs: all member pairs liberalised from max(accession years)
mem = df[df.kind=="open_regional_member"]
pairs = []
for bloc, g in mem.groupby("a"):
    acc = g.groupby("b").year.min()
    for x, z in itertools.combinations(acc.index, 2): pairs.append((x, z, max(acc[x], acc[z]), "open_regional", "bloc"))
df = pd.concat([df[df.kind!="open_regional_member"], pd.DataFrame(pairs, columns=df.columns)], ignore_index=True)
# symmetric pair-year panel
sym = pd.concat([df, df.rename(columns={"a":"b","b":"a"})], ignore_index=True)
first = sym.groupby(["a","b","kind"]).year.min().reset_index()
years = range(1990, 2025)
panel = first.assign(key=1).merge(pd.DataFrame({"year":list(years),"key":1}), on="key").drop(columns="key")
panel["on"] = (panel.year_y >= panel.year_x).astype(int)
wide = panel.pivot_table(index=["a","b","year_y"], columns="kind", values="on", aggfunc="max").fillna(0).reset_index().rename(columns={"a":"o_iso","b":"d_iso","year_y":"year"})
for k in ["open_us","open_eu","open_regional"]:
    if k not in wide: wide[k] = 0
wide["open_any"] = wide[["open_us","open_eu","open_regional"]].max(axis=1)
fy = sym.groupby(["a","b"]).year.min().rename("first_year").reset_index().rename(columns={"a":"o_iso","b":"d_iso"})
wide = wide.merge(fy, on=["o_iso","d_iso"], how="left")
wide.to_csv(here/"asa_pair_year.csv", index=False)
print("pair-years:", len(wide), "| pairs:", wide.groupby(["o_iso","d_iso"]).ngroups, "| first years by kind:")
print(first.groupby("kind").year.describe()[["count","min","50%","max"]].to_string())
print("date basis:", df.how.value_counts().to_dict())
