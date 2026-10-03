"""Build the symmetric (o_iso, d_iso, year) liberalisation panel 1990-2024 from the agreement tables.
Inputs : data_external/agreements/us_open_skies_partners.csv, eu_regional_agreements.csv (agent-compiled, ISO3)
Output : asa_pair_year.csv : open_us open_eu open_bloc open_bil open_horizontal open_any first_year (ISO2)
Kinds  : open_us   US bilateral open skies (and EU-US ATA via member-state rows)
         open_eu   EU comprehensive agreements (EU-US/Canada/Morocco/ECAA/Georgia/Jordan/Moldova/Israel/Ukraine/Qatar/
                   Armenia/ASEAN/Switzerland/EEA/UK): each EU member at the time x partner
         open_bloc regional multilateral: EU single market (members pairwise from entry), ASEAN MAAS/MAFLPAS, ASEAN-China,
                   MALIAT, SAATM, CLAC, Andean, Australia-NZ
         open_bil  other bilateral open skies (Japan, Korea programmes)
         open_horizontal  EU horizontal (nationality-clause) agreements: NOT traffic-rights liberalisation; kept separate
Date rule: treated from the year of entry into force / provisional application if on or before 1 July, else next year;
           signature-only rows: signature year + 1 (flagged 'signed_only').
"""
import pandas as pd, numpy as np, pathlib, itertools, re
here = pathlib.Path(__file__).resolve().parent
caps = pd.read_csv(here.parents[2]/"data/processed/country_capitals.csv")[["iso2","iso3"]].dropna()
iso3to2 = dict(zip(caps.iso3, caps.iso2)); iso3to2.update({"XKX":"XK","KOS":"XK"})
EU_ENTRY = {**{c:1993 for c in "BE DE DK ES FR GB GR IE IT LU NL PT".split()}, "AT":1995,"FI":1995,"SE":1995,
            **{c:2004 for c in "CY CZ EE HU LT LV MT PL SI SK".split()}, "BG":2007,"RO":2007,"HR":2013}
def members_eu(y): return {m for m, e in EU_ENTRY.items() if e <= y and not (m == "GB" and y >= 2021)}
def start_year(*dates):
    for i, d in enumerate(dates):
        d = pd.to_datetime(str(d).strip() or None, errors="coerce")
        if pd.notna(d):
            if i < len(dates)-1: return (d.year if d.month <= 7 else d.year+1), "in_force"
            return d.year + 1, "signed_only"
    return None, "no_date"
rows = []   # (a, b, year, kind, how)
# ---------- US bilateral ----------
us = pd.read_csv(here/"data_external/agreements/us_open_skies_partners.csv", dtype=str, keep_default_na=False)
for _, r in us.iterrows():
    p = iso3to2.get(r.partner_iso3.strip().upper())
    if not p or "open skies" not in r.agreement_type.lower() or "cargo" in r.agreement_type.lower(): continue
    y, how = start_year(r.date_in_force, r.provisional_application, r.date_signed)
    if y: rows.append(("US", p, y, "open_us", how))
# ---------- EU and regional ----------
eu = pd.read_csv(here/"data_external/agreements/eu_regional_agreements.csv", dtype=str, keep_default_na=False)
bloc_members = {}   # bloc -> {member: year}
for _, r in eu.iterrows():
    a = r.bloc_or_party_a.strip(); typ = r.agreement_type.strip().lower()
    p = iso3to2.get(r.party_b_iso3.strip().upper())
    y, how = start_year(r.date_in_force, r.date_provisional, r.date_signed)
    if not y: continue
    if a.startswith("EU member state:"):                       # EU-US ATA, one row per member
        m = iso3to2.get(r.party_b_iso3.strip().upper()) if r.party_b_iso3.strip().upper() != "USA" else None
        # party_b is USA; member from the label
        name = a.split(":")[1].strip()
        m = {"Austria":"AT","Belgium":"BE","Bulgaria":"BG","Cyprus":"CY","Czech Republic":"CZ","Germany":"DE","Denmark":"DK","Estonia":"EE","Spain":"ES","Finland":"FI","France":"FR","United Kingdom":"GB","Greece":"GR","Hungary":"HU","Ireland":"IE","Italy":"IT","Lithuania":"LT","Luxembourg":"LU","Latvia":"LV","Malta":"MT","Netherlands":"NL","Poland":"PL","Portugal":"PT","Romania":"RO","Sweden":"SE","Slovenia":"SI","Slovakia":"SK","Croatia":"HR","Norway":"NO","Iceland":"IS"}.get(name)
        if m: rows.append((m, "US", y, "open_eu", how)); rows.append((m, "US", y, "open_us", how))
        continue
    if typ == "horizontal_nationality_clause":
        if p:
            for m in members_eu(y): rows.append((m, p, y, "open_horizontal", how))
        continue
    if typ == "single_market_membership" and p:
        bloc_members.setdefault("EU_SM", {})[p] = min(y, bloc_members.get("EU_SM", {}).get(p, 9999)); continue
    if a.startswith("EU"):                                      # EU comprehensive / ECAA / EEA / euromed / bloc-to-bloc
        if not p or p == "EU": continue
        mem = members_eu(y) | ({"NO","IS"} if "Norway" in a or "EEA" in a else set())
        for m in mem:
            if m != p: rows.append((m, p, y, "open_eu", how))
        continue
    if a in ("ASEAN",) and typ == "bloc_to_country_asa" and p:  # ASEAN-China: each ASEAN member x China
        for m in ["BN","KH","ID","LA","MY","MM","PH","SG","TH","VN"]: rows.append((m, p, y, "open_bloc", how))
        continue
    if a in ("ASEAN","African Union","MALIAT parties","LACAC/CLAC","Andean Community (CAN)") and p:
        bloc_members.setdefault(a, {})[p] = min(y, bloc_members.get(a, {}).get(p, 9999)); continue
    if a in ("Japan","Korea, Republic of","Australia") and p:
        a2 = {"Japan":"JP","Korea, Republic of":"KR","Australia":"AU"}[a]
        kind = "open_bloc" if a == "Australia" else "open_bil"
        rows.append((a2, p, y, kind, how)); continue
for bloc, mem in bloc_members.items():
    for x, z in itertools.combinations(mem, 2): rows.append((x, z, max(mem[x], mem[z]), "open_bloc", "bloc"))
df = pd.DataFrame(rows, columns=["a","b","year","kind","how"])
df = df[df.a != df.b]
sym = pd.concat([df, df.rename(columns={"a":"b","b":"a"})], ignore_index=True)
first = sym.groupby(["a","b","kind"]).year.min().reset_index()
yrs = pd.DataFrame({"year": range(1990, 2025), "key": 1})
panel = first.rename(columns={"year":"y0"}).assign(key=1).merge(yrs, on="key").drop(columns="key")
panel["on"] = (panel.year >= panel.y0).astype(int)
wide = panel.pivot_table(index=["a","b","year"], columns="kind", values="on", aggfunc="max").fillna(0).reset_index().rename(columns={"a":"o_iso","b":"d_iso"})
for k in ["open_us","open_eu","open_bloc","open_bil","open_horizontal"]:
    if k not in wide: wide[k] = 0
wide["open_any"] = wide[["open_us","open_eu","open_bloc","open_bil"]].max(axis=1)
fy = sym[sym.kind != "open_horizontal"].groupby(["a","b"]).year.min().rename("first_year").reset_index().rename(columns={"a":"o_iso","b":"d_iso"})
wide = wide.merge(fy, on=["o_iso","d_iso"], how="left")
wide.to_csv(here/"asa_pair_year.csv", index=False)
print("pair-years:", len(wide), "| pairs:", wide.groupby(["o_iso","d_iso"]).ngroups)
print(first.groupby("kind").agg(pairs=("year","size"), first=("year","min"), median=("year","median"), last=("year","max")).to_string())
print("date basis:", df.how.value_counts().to_dict())
print("pairs liberalised (any) by 2000/2010/2020:", [(int(wide[(wide.year==y)&(wide.open_any==1)].shape[0]/2)) for y in (2000,2010,2020)])
