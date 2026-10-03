# -*- coding: utf-8 -*-
"""Parse UIC 'High Speed Lines in the World' (Details) into section tables.

Sources (data_external/primary/):
  UIC_HSL_world_2018_summary.pdf                       uic.org/IMG/pdf/20181001-high-speed-lines-in-the-world.pdf
                                                       (updated 1 Oct 2018; exact opening date YYYY.MM.DD)
  UIC_HSL_world_2022_summary_20231001_mirror_poder360.pdf  UIC 2022 edition (updated 1 Oct 2023; opening year only).
                                                       Copy hosted by poder360.com.br; the uic.org original is behind a
                                                       bot wall. PDF metadata: Adobe Acrobat, created 2023-09-11 (UIC staff).
Record per row: edition, area, country, status, section, from, to, vmax, date/year, km.
Output: data/uic_sections.csv
"""
import os
import re
import fitz
import pandas as pd

D = "data_external/primary/"
os.makedirs("data", exist_ok=True)
STAT = re.compile(r"^[1-4]\. (In operation|Under construction|Planned|Long-term planning)$")


def parse(path, edition):
    doc = fitz.open(path)
    lines = []
    for p in doc:
        lines += [l.strip() for l in p.get_text().split("\n")]
    lines = [l for l in lines if l]
    # the Details part starts after the header row ending with "(km)"
    start = next(i for i, l in enumerate(lines) if "Details" in l)
    L = lines[start:]
    rows = []
    i = 0
    while i < len(L):
        if STAT.match(L[i]) and i >= 2:
            area, country, status = L[i - 2], L[i - 1], L[i]
            j = i + 1
            sec = []
            # section text may wrap over several lines until the speed (2-3 digit number)
            while j < len(L) and not re.fullmatch(r"\d{2,3}", L[j]):
                sec.append(L[j])
                j += 1
            if j + 2 >= len(L):
                break
            vmax = L[j]
            dt = L[j + 1]
            km = L[j + 2]
            rows.append(dict(edition=edition, area=area, country=country, status=status[3:], section=" ".join(sec),
                             vmax=vmax, date_raw=dt, km_raw=km))
            i = j + 3
        else:
            i += 1
    return pd.DataFrame(rows)


a = parse(D + "UIC_HSL_world_2018_summary.pdf", "2018")
b = parse(D + "UIC_HSL_world_2022_summary_20231001_mirror_poder360.pdf", "2022")
u = pd.concat([a, b], ignore_index=True)
u["km"] = pd.to_numeric(u.km_raw.str.replace(",", "").str.replace("*", ""), errors="coerce")
u["vmax"] = pd.to_numeric(u.vmax, errors="coerce")
u["date"] = pd.to_datetime(u.date_raw.str.extract(r"(\d{4}\.\d{2}\.\d{2})")[0], format="%Y.%m.%d", errors="coerce")
u["year"] = pd.to_numeric(u.date_raw.str.extract(r"(\d{4})")[0], errors="coerce")
sp = u.section.str.replace("－", " - ").str.replace("–", " - ")
parts = sp.str.split(r"\s+-\s+", regex=True)
u["from"] = parts.str[0].str.strip()
u["to"] = parts.str[-1].str.strip()
u["n_nodes"] = parts.str.len()
u.to_csv("data/uic_sections.csv", index=False)
op = u[u.status == "In operation"]
print("rows:", len(u), "| in operation:", len(op))
print(op.groupby(["edition", "country"]).agg(n=("km", "size"), km=("km", "sum"), first=("year", "min"), last=("year", "max")).round(0).to_string())
