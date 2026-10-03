# -*- coding: utf-8 -*-
"""Build GACI_FuelShock_results_20260929.xlsx from the result CSVs (tables in paper layout,
figure data with native Excel charts, raw result sheets). Text for README / Design sheets is in
_xlsx_text.py so that it can be edited without touching the table code."""
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, ScatterChart, BarChart, Reference, Series
from _xlsx_text import README, DESIGN, DECISIONS


from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties

def style_chart(ch, ci=True, skip=None, colors=("137C7C", "8C8C8C", "8C8C8C")):
    """visible axes, straight lines, coefficient solid teal, CI bounds grey dashed, legend at bottom"""
    for ax in (ch.x_axis, ch.y_axis):
        ax.delete = False
    ch.x_axis.tickLblPos = "low"
    ch.legend.position = "t"
    if skip:
        ch.x_axis.tickLblSkip = skip
        ch.x_axis.tickMarkSkip = skip
    for i, s_ in enumerate(ch.series):
        s_.smooth = False
        s_.marker.symbol = "none"
        col = colors[i] if i < len(colors) else "8C8C8C"
        s_.graphicalProperties.line.solidFill = col
        s_.graphicalProperties.line.width = 22000 if i == 0 or not ci else 12700
        if ci and i > 0:
            s_.graphicalProperties.line.dashStyle = "dash"

OUTF = "GACI_FuelShock_results_20260929.xlsx"
FONT = "Times New Roman"
thin, thick = Side(style="thin"), Side(style="medium")

def st(p):
    if p is None or not np.isfinite(p):
        return ""
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""

def W(ws, r, c, v, bold=False, italic=False, align="center", size=10, wrap=False):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = Font(name=FONT, size=size, bold=bold, italic=italic)
    cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    return cell

def rule(ws, r, c1, c2, side="top", s=thin):
    for c in range(c1, c2 + 1):
        cell = ws.cell(row=r, column=c)
        b = cell.border
        cell.border = Border(top=s if side == "top" else b.top, bottom=s if side == "bottom" else b.bottom,
                             left=b.left, right=b.right)

def fc(b, p, d=4):
    return "" if b is None or not np.isfinite(b) else f"{b:.{d}f}{st(p)}"

def fs(se, d=4, br="()"):
    return "" if se is None or not np.isfinite(se) else f"{br[0]}{se:.{d}f}{br[1]}"

def fn(n):
    return "" if n is None or not np.isfinite(n) else f"{int(n):,}"

def ff(F):
    return "" if F is None or not np.isfinite(F) else (f"{F:,.1f}" if F < 1e5 else f"{F:.2e}")

def notes(ws, r, ncol, text):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    c = W(ws, r, 1, text, italic=False, align="left", size=9, wrap=True)
    ws.row_dimensions[r].height = max(30, 13 * (len(text) // (12 * ncol) + 2))
    return r + 2

def title(ws, r, ncol, text):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    W(ws, r, 1, text, italic=True, align="center", size=11)
    return r + 1

LAB = {
    "d_ln_seats": "Δ ln seats", "d_ln_flights": "Δ ln departures", "d_ln_skm": "Δ ln seat-km", "d_ln_co2": "Δ ln CO2",
    "d_ln_gaci_cwm": "Δ ln GACI cwm", "d_ln_gaci_max": "Δ ln GACI max", "d_ln_gauge": "Δ ln seats per departure",
    "d_ln_stage": "Δ ln stage length", "d_ln_int": "Δ ln CO2 per seat-km", "d_intl_share": "Δ intl. seat share",
    "d_ln_seats_intl": "Δ ln intl. seats", "d_ln_seats_dom": "Δ ln domestic seats", "d_ln_hhi": "Δ ln airport HHI",
    "d_top_share": "Δ top-airport seat share", "d_ln_napt": "Δ ln active airports",
    "d12_ln_seats": "Δ12 ln seats", "d12_ln_flights": "Δ12 ln departures", "d12_ln_skm": "Δ12 ln seat-km",
    "d12_ln_co2": "Δ12 ln CO2", "d12_ln_gauge": "Δ12 ln seats per departure", "d12_ln_stage": "Δ12 ln stage length",
    "d12_ln_int": "Δ12 ln CO2 per seat-km", "d12_intl_share": "Δ12 intl. seat share",
    "d12_ln_seats_dom": "Δ12 ln domestic seats", "d12_ln_seats_intl": "Δ12 ln intl. seats",
    "ln_seats": "ln seats", "ln_seats_dom": "ln domestic seats", "ln_seats_intl": "ln intl. seats",
    "rec": "ln seats − ln seats (same month 2019)", "rec_dom": "ln dom. seats − ln dom. seats (same month 2019)",
}
POS = {"H_g": "GACI 1996 (z)", "Hub10": "Top-decile GACI 1996 (hub = 1)", "H_b": "ln(1+betweenness) 1996 (z)",
       "H_cwm": "GACI cwm 1996 (z)", "H_betw": "ln(1+mean betweenness) 1996 (z)", "H_max": "GACI max 1996 (z)"}
EST = {"OLS": "OLS", "2SLS-KZ": "2SLS (Känzig)", "2SLS-BH": "2SLS (BH)"}

rc = pd.read_csv("_res_country.csv")
ra = pd.read_csv("_res_airport.csv")
rb = pd.read_csv("_res_airport_bins.csv")
rev = pd.read_csv("_res_events.csv")
res_ = pd.read_csv("_res_eventstudy.csv")
rlp = pd.read_csv("_res_lp.csv")
rfs = pd.read_csv("_res_first_stage.csv")
ss = pd.read_csv("_sumstats.csv")
hg = pd.read_csv("_hubgap_series.csv")

def pick(df, **kw):
    m = df
    for k, v in kw.items():
        m = m[m[k] == v]
    return m.iloc[0] if len(m) else None

wb = Workbook()

# ---------------- README / Decisions / Design ----------------
def text_sheet(name, blocks, width=120):
    ws = wb.create_sheet(name)
    ws.column_dimensions["A"].width = width
    r = 1
    for kind, txt in blocks:
        c = ws.cell(row=r, column=1, value=txt)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if kind == "h1":
            c.font = Font(name="맑은 고딕", size=14, bold=True)
        elif kind == "h2":
            c.font = Font(name="맑은 고딕", size=11, bold=True)
            r += 0
        else:
            c.font = Font(name="맑은 고딕", size=10)
            ws.row_dimensions[r].height = max(15, 15 * (len(txt) // 95 + txt.count("\n") + 1))
        r += 1
    return ws

wb.remove(wb.active)
text_sheet("README", README)
text_sheet("결정필요_표본정의", DECISIONS)
text_sheet("연구설계", DESIGN)

# ---------------- generic wide table ----------------
def wide_table(ws, r, ttl, blocks, ests, panels, df, keyname, extra_rows, note, termname="Δ ln P(jet) × position",
               terms=("x",), term_labels=None):
    ncol = 1 + len(blocks) * len(ests)
    r = title(ws, r, ncol, ttl)
    rule(ws, r, 1, ncol, "top", thick)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=ncol)
    W(ws, r, 2, "Dependent variable")
    r += 1
    for j, (o, lab) in enumerate(blocks):
        c0 = 2 + j * len(ests)
        ws.merge_cells(start_row=r, start_column=c0, end_row=r, end_column=c0 + len(ests) - 1)
        W(ws, r, c0, lab)
        rule(ws, r, c0, c0 + len(ests) - 1, "bottom", thin)
    r += 1
    for j in range(len(blocks)):
        for k, (e, elab) in enumerate(ests):
            W(ws, r, 2 + j * len(ests) + k, elab)
    r += 1
    for c in range(2, ncol + 1):
        W(ws, r, c, f"({c - 1})")
    rule(ws, r, 1, ncol, "bottom", thin)
    r += 1
    for pk, plab in panels:
        W(ws, r, 1, plab, italic=True, align="left")
        r += 1
        for ti, term in enumerate(terms):
            tl = term_labels[ti] if term_labels else termname
            W(ws, r, 1, tl, align="left")
            W(ws, r + 1, 1, "", align="left")
            W(ws, r + 2, 1, "", align="left")
            for j, (o, _) in enumerate(blocks):
                for k, (e, _) in enumerate(ests):
                    x = pick(df, **{keyname: pk, "outcome": o, "col": e, "term": term})
                    c = 2 + j * len(ests) + k
                    if x is None:
                        continue
                    W(ws, r, c, fc(x.b, x.p))
                    W(ws, r + 1, c, fs(x.se))
                    W(ws, r + 2, c, fs(x.se_cl, br="[]"), size=9)
            r += 3
        for lab, fnc in extra_rows:
            W(ws, r, 1, lab, align="left")
            for j, (o, _) in enumerate(blocks):
                for k, (e, _) in enumerate(ests):
                    x = pick(df, **{keyname: pk, "outcome": o, "col": e, "term": terms[0]})
                    if x is not None:
                        W(ws, r, 2 + j * len(ests) + k, fnc(x, e))
            r += 1
    rule(ws, r - 1, 1, ncol, "bottom", thick)
    ws.column_dimensions["A"].width = 38
    for c in range(2, ncol + 1):
        ws.column_dimensions[get_column_letter(c)].width = 13
    return notes(ws, r, ncol, note)

NOTE_DK = ("SE in parentheses: clustered by country and Newey-West over time (Thompson 2011; {L}), floored at the larger "
           "one-way component; stars (* p<0.1, ** p<0.05, *** p<0.01) refer to these. SE in brackets: country cluster only. "
           "KP F = Kleibergen-Paap Wald F of the excluded instrument under each variance estimator.")

# ---------------- T1 summary statistics ----------------
ws = wb.create_sheet("T1_요약통계")
r = title(ws, 1, 8, "Table 1. Summary statistics")
rule(ws, r, 1, 8, "top", thick)
for j, h in enumerate(["Variable", "Unit", "N", "Mean", "SD", "P10", "Median", "P90"]):
    W(ws, r, j + 1, h, align="left" if j == 0 else "center")
rule(ws, r, 1, 8, "bottom", thin)
r += 1
for pnl, g in ss.groupby("panel", sort=False):
    W(ws, r, 1, pnl, italic=True, align="left")
    r += 1
    for x in g.itertuples():
        W(ws, r, 1, x.variable, align="left")
        W(ws, r, 2, "" if pd.isna(x.unit) else x.unit)
        W(ws, r, 3, fn(x.n))
        for j, v in enumerate([x.mean, x.sd, x.p10, x.median, x.p90]):
            W(ws, r, 4 + j, "" if pd.isna(v) else f"{v:,.3f}")
        r += 1
rule(ws, r - 1, 1, 8, "bottom", thick)
ws.column_dimensions["A"].width = 52
notes(ws, r, 8, "Airports: all airports with a 1996 GACI value and positive departing seats in 1996 (OAG schedules). "
      "Countries: countries with a 1996 GACI value. Top-decile airports: GACI 1996 at or above the 90th percentile. "
      "Jet fuel: EIA US Gulf Coast kerosene-type jet fuel spot price, deflated by US CPI-U to 2019 dollars. "
      "Kaenzig (2021) oil supply news shock and Baumeister-Hamilton (2019) oil supply shock (sign flipped so that a "
      "positive value raises the oil price). Panel E: time-series correlations used by the first stage.")

# ---------------- T2 country main ----------------
ws = wb.create_sheet("T2_국가_본분석")
blocks = [(o, LAB[o]) for o in ["d_ln_seats", "d_ln_flights", "d_ln_skm", "d_ln_co2", "d_ln_gaci_cwm"]]
ests = [(e, EST[e]) for e in ["OLS", "2SLS-KZ", "2SLS-BH"]]
C1 = rc[rc.table == "C1"]
extra = [("Observations", lambda x, e: fn(x.n)), ("Countries", lambda x, e: fn(x.n_c)),
         ("KP F (country + year HAC)", lambda x, e: ff(x.F) if e != "OLS" else ""),
         ("KP F (country cluster)", lambda x, e: ff(x.F_cl) if e != "OLS" else "")]
wide_table(ws, 1, "Table 2. Jet fuel prices and 1996 network position: country × year, 1997–2019 (first differences)",
           blocks, ests, [("H_cwm", "Panel A. Position = GACI cwm 1996 (z)"), ("H_betw", "Panel B. Position = ln(1+mean betweenness) 1996 (z)"),
                          ("H_max", "Panel C. Position = GACI max 1996 (z)")], C1, "panel", extra,
           "Notes: Δ y_ct = a_c + d_t + b (Δ ln P_t × H_c) + e_ct. P = annual mean real jet fuel price (2019 $). H_c = 1996 position, "
           "standardized across the 150 countries with a 1996 GACI value. Country FE absorb country-specific growth trends; year FE "
           "absorb the common response to the price. 2SLS: Δ ln P_t × H_c instrumented by ΔK_t × H_c, where K_t is the annual mean of the "
           "cumulated monthly Känzig (2021) oil supply news shock or of the cumulated Baumeister-Hamilton (2019) supply shock (× −1). "
           + NOTE_DK.format(L="L = 2 years"))

# ---------------- T3 airport main ----------------
ws = wb.create_sheet("T3_공항_본분석")
blocks = [(o, LAB[o]) for o in ["d12_ln_seats", "d12_ln_flights", "d12_ln_skm", "d12_ln_co2"]]
A1 = ra[ra.table == "A1"]
extra = [("Observations", lambda x, e: fn(x.n)), ("Airports", lambda x, e: fn(x.n_air)),
         ("Countries (clusters)", lambda x, e: fn(x.G) if False else ""),
         ("KP F (country + month HAC)", lambda x, e: ff(x.F) if e != "OLS" else ""),
         ("KP F (country cluster)", lambda x, e: ff(x.F_cl) if e != "OLS" else "")]
extra = [e_ for e_ in extra if e_[0] != "Countries (clusters)"]
r = wide_table(ws, 1, "Table 3. Jet fuel prices and 1996 network position: airport × month, 1997–2019 (12-month differences)",
               blocks, ests, [("H_g", "Panel A. Position = GACI 1996 (z)"), ("Hub10", "Panel B. Position = top-decile GACI 1996 (hub = 1)"),
                              ("H_b", "Panel C. Position = ln(1+betweenness) 1996 (z)")], A1, "panel", extra,
               "Notes: Δ12 ln y_it = a_i + d_t + b (Δ12 ln P_(t−3) × H_i) + e_it. P = real US Gulf Coast jet fuel price (2019 $), lagged three "
               "months. Airports with a 1996 GACI value and positive 1996 seats; Δ12 requires positive seats in both months. Airport FE absorb "
               "airport-specific growth trends; year-month FE absorb the common response and the seasonality of growth. 2SLS instruments: "
               "12-month sums of the Känzig news shock or of the BH supply shock (× −1), lagged three months, × H_i. "
               + NOTE_DK.format(L="L = 12 months"))
# Panel D: carbon-price back-of-envelope
dlnP = np.log((1.88 + 0.957) / 1.88)
W(ws, r, 1, "Panel D. Implied hub–spoke gap in seat growth from a USD 100/t CO2 price (top-decile hubs vs other airports)", italic=True, align="left")
r += 1
rule(ws, r, 1, 4, "top", thin)
for j, h in enumerate(["Estimator", "Coefficient (Panel B, Δ12 ln seats)", "Δ ln P", "Implied gap, % [90% CI]"]):
    W(ws, r, j + 1, h)
r += 1
for e in ["OLS", "2SLS-KZ", "2SLS-BH"]:
    x = pick(A1, panel="Hub10", outcome="d12_ln_seats", col=e, term="x")
    g = lambda v: 100 * (np.exp(v * dlnP) - 1)
    W(ws, r, 1, EST[e])
    W(ws, r, 2, fc(x.b, x.p))
    W(ws, r, 3, f"{dlnP:.3f}")
    W(ws, r, 4, f"{g(x.b):.2f} [{g(x.b - 1.645 * x.se):.2f}, {g(x.b + 1.645 * x.se):.2f}]")
    r += 1
rule(ws, r - 1, 1, 4, "bottom", thick)
notes(ws, r, 8, "Panel D: USD 100 per tonne CO2 × 9.57 kg CO2 per gallon of jet fuel (3.16 kg CO2/kg × 3.03 kg/gal) = USD 0.957 per gallon, "
      "added to the 2019 average real price of USD 1.88 per gallon: Δ ln P = %.3f. The time FE absorb the common response, so only the "
      "hub–spoke difference is identified; the level effect on all airports is not." % dlnP)

# ---------------- T4 margins (long) ----------------
ws = wb.create_sheet("T4_경로_마진")
def long_table(ws, r, ttl, rows_spec, df, key, ests, note, extra_cols=True, lab_col="Dependent variable"):
    ncol = 1 + len(ests) + (3 if extra_cols else 0)
    r = title(ws, r, ncol, ttl)
    rule(ws, r, 1, ncol, "top", thick)
    W(ws, r, 1, lab_col, align="left")
    for k, (e, el) in enumerate(ests):
        W(ws, r, 2 + k, el)
    if extra_cols:
        for k, h in enumerate(["Observations", "KP F (Känzig)", "KP F (BH)"]):
            W(ws, r, 2 + len(ests) + k, h)
    rule(ws, r, 1, ncol, "bottom", thin)
    r += 1
    for item in rows_spec:
        if item[0] == "panel":
            W(ws, r, 1, item[1], italic=True, align="left")
            r += 1
            continue
        lab, sel = item
        W(ws, r, 1, lab, align="left")
        xs = {}
        for k, (e, _) in enumerate(ests):
            x = pick(df, **sel, col=e)
            xs[e] = x
            if x is None:
                continue
            W(ws, r, 2 + k, fc(x.b, x.p))
            W(ws, r + 1, 2 + k, fs(x.se))
            W(ws, r + 2, 2 + k, fs(x.se_cl, br="[]"), size=9)
        if extra_cols:
            x0 = next((v for v in xs.values() if v is not None), None)
            if x0 is not None:
                W(ws, r, 2 + len(ests), fn(x0.n))
                W(ws, r, 3 + len(ests), ff(xs.get("2SLS-KZ").F) if xs.get("2SLS-KZ") is not None else "")
                W(ws, r, 4 + len(ests), ff(xs.get("2SLS-BH").F) if xs.get("2SLS-BH") is not None else "")
        r += 3
    rule(ws, r - 1, 1, ncol, "bottom", thick)
    ws.column_dimensions["A"].width = 44
    for c in range(2, ncol + 1):
        ws.column_dimensions[get_column_letter(c)].width = 15
    return notes(ws, r, ncol, note)

A2, C2 = ra[ra.table == "A2"], rc[rc.table == "C2"]
spec = [("panel", "Panel A. Airport × month, 1997–2019; position = GACI 1996 (z)")]
spec += [(LAB[o], dict(outcome=o, term="x")) for o in ["d12_ln_gauge", "d12_ln_stage", "d12_ln_int", "d12_intl_share", "d12_ln_seats_dom", "d12_ln_seats_intl"]]
r = long_table(ws, 1, "Table 4. Margins of adjustment: aircraft size, stage length, fuel intensity, segments and network structure",
               spec, A2, None, ests, "Panel A: specification of Table 3 (Δ12, airport and year-month FE). " + NOTE_DK.format(L="L = 12 months"))
spec = [("panel", "Panel B. Country × year, 1997–2019; position = GACI cwm 1996 (z)")]
spec += [(LAB[o], dict(outcome=o, term="x")) for o in ["d_ln_gauge", "d_ln_stage", "d_ln_int", "d_intl_share", "d_ln_seats_intl",
                                                     "d_ln_seats_dom", "d_ln_hhi", "d_top_share", "d_ln_napt", "d_ln_gaci_max"]]
long_table(ws, r, "", spec, C2, None, ests, "Panel B: specification of Table 2 (first differences, country and year FE). HHI and top-airport "
           "share: concentration of departing seats across the country's airports. " + NOTE_DK.format(L="L = 2 years"))

# ---------------- T5 horse race ----------------
ws = wb.create_sheet("T5_경쟁회귀")
TL = {"x": "Δ ln P × position (GACI)", "x_z_ln_seats96": "Δ ln P × ln seats 1996 (z)", "x_z_intl_share_96": "Δ ln P × intl. share 1996 (z)",
      "x_z_ln_stage96": "Δ ln P × ln stage length 1996 (z)", "x_z_ln_gauge96": "Δ ln P × ln seats/departure 1996 (z)",
      "x_z_lnpc_c96": "Δ ln P × ln GDP pc 1996 (z)", "x_z_oilrent_c96": "Δ ln P × oil rents 1996–98 (z)",
      "x_z_intl_share96": "Δ ln P × intl. share 1996 (z)", "x_z_lnpc96": "Δ ln P × ln GDP pc 1996 (z)",
      "x_z_lnpop96": "Δ ln P × ln population 1996 (z)", "x_z_oilrent96": "Δ ln P × oil rents 1996–98 (z)"}
def horse(ws, r, ttl, df, outcome, note_sfx, panels):
    cols = list(dict.fromkeys(df[df.outcome == outcome].col))
    ncol = 1 + len(cols)
    r = title(ws, r, ncol, ttl)
    rule(ws, r, 1, ncol, "top", thick)
    W(ws, r, 1, "")
    for k, c in enumerate(cols):
        W(ws, r, 2 + k, c, wrap=True)
    ws.row_dimensions[r].height = 30
    rule(ws, r, 1, ncol, "bottom", thin)
    r += 1
    for plab, est, notesel in panels:
        W(ws, r, 1, plab, italic=True, align="left")
        r += 1
        d = df[(df.outcome == outcome) & (df.estimator == est) & (df.note.str.contains(notesel, regex=False))]
        terms = list(dict.fromkeys(d.term))
        for term in terms:
            W(ws, r, 1, TL.get(term, term), align="left")
            for k, c in enumerate(cols):
                x = pick(d, col=c, term=term)
                if x is None:
                    continue
                W(ws, r, 2 + k, fc(x.b, x.p))
                W(ws, r + 1, 2 + k, fs(x.se))
            r += 2
        W(ws, r, 1, "Observations", align="left")
        for k, c in enumerate(cols):
            x = pick(d, col=c, term="x")
            if x is not None:
                W(ws, r, 2 + k, fn(x.n))
        r += 1
        if est == "2SLS":
            W(ws, r, 1, "SW F, position term (HAC)", align="left")
            for k, c in enumerate(cols):
                x = pick(d, col=c, term="x")
                if x is not None:
                    W(ws, r, 2 + k, ff(x.F))
            r += 1
    rule(ws, r - 1, 1, ncol, "bottom", thick)
    ws.column_dimensions["A"].width = 40
    for c in range(2, ncol + 1):
        ws.column_dimensions[get_column_letter(c)].width = 15
    return notes(ws, r, ncol, note_sfx)

A3 = ra[ra.table == "A3"]
r = horse(ws, 1, "Table 5. Position versus other 1996 characteristics: airport × month, Δ12 ln seats", A3, "d12_ln_seats",
          "Common sample of airports with all 1996 characteristics. Every characteristic enters as Δ12 ln P(t−3) × X_i (z-scores). "
          "2SLS: each interaction instrumented by the shock × X_i (Sanderson-Windmeijer F for the position term). Column (7) replaces "
          "year-month FE by country × year-month FE; country-level characteristics are then absorbed and dropped. " + NOTE_DK.format(L="L = 12 months").split(" SE in brackets")[0] + ".",
          [("Panel A. OLS", "OLS", "common sample"), ("Panel B. 2SLS (BH)", "2SLS", "BH"), ("Panel C. 2SLS (Känzig)", "2SLS", "KZ")])
r = horse(ws, r, "Table 5 (cont.). Airport × month, Δ12 ln CO2", A3, "d12_ln_co2", "As above, outcome Δ12 ln CO2.",
          [("Panel D. OLS", "OLS", "common sample"), ("Panel E. 2SLS (BH)", "2SLS", "BH"), ("Panel F. 2SLS (Känzig)", "2SLS", "KZ")])
C3 = rc[rc.table == "C3"]
horse(ws, r, "Table 5 (cont.). Country × year, Δ ln seats", C3, "d_ln_seats",
      "Country × year, first differences, country and year FE; common sample of countries with all 1996 characteristics. " + NOTE_DK.format(L="L = 2 years").split(" SE in brackets")[0] + ".",
      [("Panel G. OLS", "OLS", "common sample"), ("Panel H. 2SLS (BH)", "2SLS", "BH")])

# ---------------- T6 events ----------------
ws = wb.create_sheet("T6_사건연구")
FEL = {"apt x cal-month + country x month": "Country × month FE", "+ intl share(base) x month": "+ intl. share × month",
       "apt x cal-month + month (no country FE)": "Month FE only"}
r = 1
for ev, outs in [("2022 spike", ["ln_seats", "ln_seats_dom", "ln_seats_intl", "rec", "rec_dom"]),
                 ("2014 crash", ["ln_seats", "ln_seats_dom", "ln_seats_intl"]),
                 ("2008 spike", ["ln_seats", "ln_seats_dom", "ln_seats_intl"])]:
    d = rev[rev.event == ev]
    fes_ = list(FEL)
    ncol = 1 + len(outs) * len(fes_)
    r = title(ws, r, ncol, f"Table 6{'abc'[['2022 spike', '2014 crash', '2008 spike'].index(ev)]}. {ev}: hub–spoke differences in seats (airport × month)")
    rule(ws, r, 1, ncol, "top", thick)
    for j, o in enumerate(outs):
        c0 = 2 + j * len(fes_)
        ws.merge_cells(start_row=r, start_column=c0, end_row=r, end_column=c0 + len(fes_) - 1)
        W(ws, r, c0, LAB[o], wrap=True)
        rule(ws, r, c0, c0 + len(fes_) - 1, "bottom", thin)
    ws.row_dimensions[r].height = 30
    r += 1
    for j in range(len(outs)):
        for k, fe in enumerate(fes_):
            W(ws, r, 2 + j * len(fes_) + k, FEL[fe], wrap=True, size=9)
    ws.row_dimensions[r].height = 28
    rule(ws, r, 1, ncol, "bottom", thin)
    r += 1
    periods = list(dict.fromkeys(d.period))
    for pr in periods:
        W(ws, r, 1, ("ln P(t−3) × position (within window)" if pr.startswith("continuous") else "Position × " + pr), align="left")
        for j, o in enumerate(outs):
            for k, fe in enumerate(fes_):
                x = pick(d, outcome=o, fe=fe, period=pr)
                if x is None:
                    continue
                c = 2 + j * len(fes_) + k
                W(ws, r, c, fc(x.b, x.p))
                W(ws, r + 1, c, fs(x.se))
                W(ws, r + 2, c, fs(x.se_cl, br="[]"), size=9)
        r += 3
    for lab, f_ in [("Observations", lambda x: fn(x.n)), ("Airports", lambda x: fn(x.n_air))]:
        W(ws, r, 1, lab, align="left")
        for j, o in enumerate(outs):
            for k, fe in enumerate(fes_):
                x = pick(d, outcome=o, fe=fe, period=periods[0])
                if x is not None:
                    W(ws, r, 2 + j * len(fes_) + k, f_(x))
        r += 1
    rule(ws, r - 1, 1, ncol, "bottom", thick)
    r += 1
ws.column_dimensions["A"].width = 42
for c in range(2, 17):
    ws.column_dimensions[get_column_letter(c)].width = 12
notes(ws, r, 16, "y_it = a_(i × calendar month) + d_(country × month) + Σ_k b_k (H_i × Period_k) + e_it. Position H_i = z-score of the airport's GACI in "
      "the base year (2019 for 2022, 2013 for 2014, 2007 for 2008); airports with traffic in the base year. Reference = pre-period "
      "(2021-01..2022-02; 2013-01..2014-09; 2006-01..2007-09). Recovery outcomes (rec) use airport FE instead of airport × calendar-month FE. "
      "'+ intl. share × month': base-year international seat share × year-month dummies (partialled out). 'Continuous' rows: ln P(t−3) × H_i "
      "within the window. SE in parentheses: country cluster + Newey-West over months (L = 6); brackets: country cluster. Monthly "
      "event-study coefficients are in sheet Fig_사건연구: for 2022 the hub–spoke gap already widens from early 2021, before the price spike, "
      "and keeps widening in 2023–2024 when prices fall.")

# ---------------- T7 local projections ----------------
ws = wb.create_sheet("T7_국소투영")
ncol = 11
r = title(ws, 1, ncol, "Table 7. Local projections: response of the hub–spoke gap to a one-SD oil supply shock (airport × month, 1997–2019)")
rule(ws, r, 1, ncol, "top", thick)
hdr = ["Horizon h (months)", "Känzig: ln seats", "Känzig: ln CO2", "Känzig: price response", "Känzig: implied elasticity (seats)",
       "BH: ln seats", "BH: ln CO2", "BH: price response", "BH: implied elasticity (seats)", "N (seats, Känzig)", ""]
for j, h in enumerate(hdr[:10]):
    W(ws, r, j + 1, h, wrap=True)
ws.row_dimensions[r].height = 42
rule(ws, r, 1, ncol, "bottom", thin)
r += 1
for h in [0, 1, 2, 3, 6, 9, 12, 15, 18, 21, 24]:
    W(ws, r, 1, str(h))
    for k, s in enumerate(["s_kz", "s_bh"]):
        xs = pick(rlp, h=h, outcome="ln_seats", shock=s)
        xc = pick(rlp, h=h, outcome="ln_co2", shock=s)
        c0 = 2 + 4 * k
        W(ws, r, c0, fc(xs.b, xs.p))
        W(ws, r + 1, c0, fs(xs.se))
        W(ws, r, c0 + 1, fc(xc.b, xc.p))
        W(ws, r + 1, c0 + 1, fs(xc.se))
        pz = 2 * (1 - __import__("scipy").stats.norm.cdf(abs(xs.g_price / xs.se_price)))
        W(ws, r, c0 + 2, fc(xs.g_price, pz))
        W(ws, r + 1, c0 + 2, fs(xs.se_price))
        W(ws, r, c0 + 3, f"{xs.implied_elast:.4f}")
    W(ws, r, 10, fn(pick(rlp, h=h, outcome="ln_seats", shock="s_kz").n))
    r += 2
rule(ws, r - 1, 1, ncol, "bottom", thick)
ws.column_dimensions["A"].width = 18
for c in range(2, 12):
    ws.column_dimensions[get_column_letter(c)].width = 14
notes(ws, r, ncol, "ln y_(i,t+h) − ln y_(i,t−1) = a_i + d_t + b_h (s_t × H_i) + e; s_t = shock scaled to one SD over 1997–2019; H_i = GACI 1996 (z). "
      "Only t + h ≤ 2019-12. Price response: ln P_(t+h) − ln P_(t−1) on s_t (time series, Newey-West L = h+1). Implied elasticity = b_h / price "
      "response (differential elasticity of seats per SD of GACI). SE: country cluster + Newey-West over months (L = max(h+1, 6)).")

# ---------------- T8 robustness ----------------
ws = wb.create_sheet("T8_강건성")
A5, C5 = ra[ra.table == "A5"], rc[rc.table == "C5"]
spec = [("panel", "Panel A. Airport × month, Δ12 ln seats, position = GACI 1996 (z)"), ("Baseline (Table 3, col. 1–3)", dict(table="A1", panel="H_g", outcome="d12_ln_seats", term="x"))]
for pnl in list(dict.fromkeys(A5.panel)):
    terms = list(dict.fromkeys(A5[A5.panel == pnl].term))
    for t_ in terms:
        lab = pnl if len(terms) == 1 else f"{pnl}: {t_}"
        spec.append((lab, dict(panel=pnl, term=t_)))
r = long_table(ws, 1, "Table 8. Robustness", spec, pd.concat([A1, A5]), None, ests,
               "Panel A: each row changes one element of the Table 3 specification. Price lag L: Δ12 ln P(t−L) with the shock sums lagged L months. "
               "Crack spread: ln(jet/Brent per gallon). Levels: ln seats on ln P(t−3) × H with airport × calendar-month FE, year-month FE and H × linear "
               "trend (instruments: cumulated shocks). Asymmetry: price rises and falls entered separately. SE rows: see Table 3 unless the row "
               "states another variance estimator.", lab_col="Specification")
spec = [("panel", "Panel B. Country × year, Δ ln seats, position = GACI cwm 1996 (z)"), ("Baseline (Table 2, col. 1–3)", dict(table="C1", panel="H_cwm", outcome="d_ln_seats", term="x"))]
for pnl in list(dict.fromkeys(C5.panel)):
    terms = list(dict.fromkeys(C5[C5.panel == pnl].term))
    for t_ in terms:
        spec.append((pnl if len(terms) == 1 else f"{pnl}: {t_}", dict(panel=pnl, term=t_)))
long_table(ws, r, "", spec, pd.concat([C1, C5]), None, ests, "Panel B: each row changes one element of the Table 2 specification.", lab_col="Specification")

# ---------------- A1 first stage ----------------
ws = wb.create_sheet("A1_1단계")
ncol = 9
r = title(ws, 1, ncol, "Table A1. First stages: (Δ ln P × H) on (shock × H)")
rule(ws, r, 1, ncol, "top", thick)
for j, h in enumerate(["Level", "Position", "Instrument", "π", "SE (HAC)", "KP F (HAC)", "KP F (country cluster)", "KP F (two-way)", "Observations"]):
    W(ws, r, j + 1, h, wrap=True)
rule(ws, r, 1, ncol, "bottom", thin)
r += 1
SHL = {"kz_s12_l3": "Känzig, 12-month sum (t−3)", "bh_neg_s12_l3": "BH × (−1), 12-month sum (t−3)",
       "d_kz_cum": "Känzig, Δ annual mean of cumulated shock", "d_bh_neg_cum": "BH × (−1), Δ annual mean of cumulated shock"}
for (lev, H, s), g in rfs.groupby(["level", "position", "shock"], sort=False):
    g = g.reset_index(drop=True)
    W(ws, r, 1, lev)
    W(ws, r, 2, POS.get(H, H))
    W(ws, r, 3, SHL.get(s, s))
    W(ws, r, 4, fc(g.pi[0], g.p[0]))
    W(ws, r, 5, fs(g.se[0]))
    W(ws, r, 6, ff(g.F[0]))
    W(ws, r, 7, ff(g.F[1]))
    W(ws, r, 8, ff(g.F[2]))
    W(ws, r, 9, fn(g.n[0]))
    r += 1
rule(ws, r - 1, 1, ncol, "bottom", thick)
for c, wdt in zip("ABCDEFGHI", [14, 30, 40, 12, 12, 12, 16, 14, 14]):
    ws.column_dimensions[c].width = wdt
notes(ws, r, ncol, "With a single aggregate shock, country-cluster first-stage F statistics treat each unit as an independent replication of one "
      "time series and are therefore very large; the HAC and two-way versions account for the common time component and are the relevant "
      "measures of instrument strength here. Two-way = country and year (airports) or country and year (countries).")

# ---------------- A2 dose ----------------
ws = wb.create_sheet("A2_분위별")
ncol = 6
r = title(ws, 1, ncol, "Table A2. Differential response by 1996 GACI decile (airports) and tercile (countries), OLS")
rule(ws, r, 1, ncol, "top", thick)
for j, h in enumerate(["Group (reference = bottom)", "Δ12 ln seats", "", "Δ12 ln CO2", "", ""]):
    W(ws, r, j + 1, h)
rule(ws, r, 1, ncol, "bottom", thin)
r += 1
W(ws, r, 1, "Panel A. Airports: Δ12 ln P(t−3) × decile dummy", italic=True, align="left")
r += 1
for k in range(2, 11):
    W(ws, r, 1, f"Decile {k}", align="left")
    for j, o in enumerate(["d12_ln_seats", "d12_ln_co2"]):
        x = pick(rb, outcome=o, decile=k)
        W(ws, r, 2 + 2 * j, fc(x.b, x.p))
        W(ws, r, 3 + 2 * j, fs(x.se))
    r += 1
W(ws, r, 1, "Panel B. Countries: Δ ln P × tercile dummy (GACI cwm 1996)", italic=True, align="left")
r += 1
C4 = rc[rc.table == "C4"]
for t_, lab in [("x_mid", "Middle tercile"), ("x_top", "Top tercile")]:
    W(ws, r, 1, lab, align="left")
    for j, o in enumerate(["d_ln_seats", "d_ln_co2"]):
        x = pick(C4, outcome=o, term=t_)
        W(ws, r, 2 + 2 * j, fc(x.b, x.p))
        W(ws, r, 3 + 2 * j, fs(x.se))
    r += 1
rule(ws, r - 1, 1, ncol, "bottom", thick)
ws.column_dimensions["A"].width = 44
notes(ws, r, ncol, "Specifications of Tables 3 and 2 with the continuous position replaced by group dummies; SE: country cluster + Newey-West over time.")

# ---------------- A3 position IV ----------------
ws = wb.create_sheet("A3_위치도구변수")
ncol = 7
r = title(ws, 1, ncol, "Table A3. Position instrumented by 1996 air market access (country × year)")
rule(ws, r, 1, ncol, "top", thick)
for j, h in enumerate(["Outcome", "2SLS", "SE (HAC)", "SE (country cl.)", "KP F (HAC)", "KP F (country cl.)", "Observations"]):
    W(ws, r, j + 1, h)
rule(ws, r, 1, ncol, "bottom", thin)
r += 1
for x in rc[rc.table == "C6"].itertuples():
    W(ws, r, 1, LAB[x.outcome])
    W(ws, r, 2, fc(x.b, x.p))
    W(ws, r, 3, fs(x.se))
    W(ws, r, 4, fs(x.se_cl, br="[]"))
    W(ws, r, 5, ff(x.F))
    W(ws, r, 6, ff(x.F_cl))
    W(ws, r, 7, fn(x.n))
    note6 = x.note
    r += 1
rule(ws, r - 1, 1, ncol, "bottom", thick)
ws.column_dimensions["A"].width = 20
b_ = pd.read_csv("airport_base.csv")
b_ = b_[b_.GACI_96.notna() & (b_.seats_96 > 0)]
notes(ws, r, ncol, "Δ ln P × GACI cwm 1996 (z) instrumented by Δ ln P × ln air market access 1996 (z) (Feyrer 2019 ingredient, build_feyrer_iv.py). "
      + note6 + "; at the airport level corr(GACI 1996, ln airMA 1996) = %.2f, so no airport-level version is estimated." % b_[["GACI_96", "ln_airma96"]].corr().iloc[0, 1])

# ---------------- figure data with native charts ----------------
ws = wb.create_sheet("Fig_허브격차시계열")
hg2 = hg.copy()
hg2["slope_ma12"] = hg2.slope.rolling(12, min_periods=6).mean()
cols = ["ym", "slope", "slope_ma12", "d12_lnjet_l3"]
for j, c in enumerate(["Year-month", "Monthly slope of Δ12 ln seats on GACI 1996 (z)", "12-month moving average", "Δ12 ln jet fuel price (t−3)"]):
    W(ws, 1, j + 1, c, wrap=True)
for i, x in enumerate(hg2[cols].itertuples(index=False)):
    for j, v in enumerate(x):
        ws.cell(row=2 + i, column=j + 1, value=(v if j == 0 else float(v) if pd.notna(v) else None))
n = len(hg2)
ch = LineChart()
ch.title = "Hub–spoke seat-growth gap and jet fuel price changes, 1997–2019"
ch.y_axis.title = "Slope (Δ12 ln seats per SD of GACI 1996)"
ch.x_axis.title = "Year-month"
ch.add_data(Reference(ws, min_col=3, min_row=1, max_row=n + 1), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=n + 1))
ch2 = LineChart()
ch2.add_data(Reference(ws, min_col=4, min_row=1, max_row=n + 1), titles_from_data=True)
ch2.y_axis.axId = 200
ch2.y_axis.title = "Δ12 ln jet fuel price"
ch2.y_axis.crosses = "max"
style_chart(ch, ci=False, skip=24, colors=("137C7C",))
style_chart(ch2, ci=False, colors=("D9822B",))
ch2.y_axis.delete = False
ch2.y_axis.majorGridlines = None
ch.x_axis.title = None
ch += ch2
ch.height, ch.width = 9, 22
ws.add_chart(ch, "F2")
ws.column_dimensions["B"].width = 18

ws = wb.create_sheet("Fig_사건연구")
r0 = 1
for k, (ev, o) in enumerate([("2022 spike", "rec"), ("2022 spike", "ln_seats_dom"), ("2014 crash", "ln_seats"), ("2008 spike", "ln_seats")]):
    d = res_[(res_.event == ev) & (res_.outcome == o)].copy()
    c0 = 1 + 5 * k
    W(ws, 1, c0, f"{ev}: {LAB[o]}", bold=True, align="left")
    for j, h in enumerate(["Year-month", "Coefficient", "Lower 95%", "Upper 95%"]):
        W(ws, 2, c0 + j, h)
    for i, x in enumerate(d.itertuples()):
        ws.cell(row=3 + i, column=c0, value=x.ym)
        ws.cell(row=3 + i, column=c0 + 1, value=float(x.b))
        ws.cell(row=3 + i, column=c0 + 2, value=float(x.b - 1.96 * x.se))
        ws.cell(row=3 + i, column=c0 + 3, value=float(x.b + 1.96 * x.se))
    ch = LineChart()
    ch.title = f"{ev}: position × month ({LAB[o]}); reference {d.ref.iloc[0]}"
    ch.add_data(Reference(ws, min_col=c0 + 1, max_col=c0 + 3, min_row=2, max_row=2 + len(d)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=c0, min_row=3, max_row=2 + len(d)))
    style_chart(ch, ci=True, skip=6)
    ch.height, ch.width = 8, 18
    ws.add_chart(ch, f"{get_column_letter(22)}{2 + 17 * k}")

ws = wb.create_sheet("Fig_분위_LP")
W(ws, 1, 1, "Airport GACI 1996 decile (reference = 1): Δ12 ln seats", bold=True, align="left")
for j, h in enumerate(["Decile", "Coefficient", "Lower 95%", "Upper 95%"]):
    W(ws, 2, 1 + j, h)
d = rb[rb.outcome == "d12_ln_seats"]
for i, x in enumerate(d.itertuples()):
    ws.cell(row=3 + i, column=1, value=int(x.decile))
    ws.cell(row=3 + i, column=2, value=float(x.b))
    ws.cell(row=3 + i, column=3, value=float(x.b - 1.96 * x.se))
    ws.cell(row=3 + i, column=4, value=float(x.b + 1.96 * x.se))
ch = LineChart()
ch.title = "Differential elasticity of seats by 1996 GACI decile"
ch.add_data(Reference(ws, min_col=2, max_col=4, min_row=2, max_row=2 + len(d)), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=3, max_row=2 + len(d)))
style_chart(ch, ci=True)
ch.height, ch.width = 8, 16
ws.add_chart(ch, "K2")
W(ws, 1, 6, "Local projections, ln seats (per 1-SD shock)", bold=True, align="left")
for j, h in enumerate(["h", "Känzig", "Lower 95%", "Upper 95%", "BH", "Lower 95% ", "Upper 95% "]):
    W(ws, 2, 6 + j, h)
for i, h in enumerate(range(25)):
    a = pick(rlp, h=h, outcome="ln_seats", shock="s_kz")
    b2 = pick(rlp, h=h, outcome="ln_seats", shock="s_bh")
    vals = [h, a.b, a.b - 1.96 * a.se, a.b + 1.96 * a.se, b2.b, b2.b - 1.96 * b2.se, b2.b + 1.96 * b2.se]
    for j, v in enumerate(vals):
        ws.cell(row=3 + i, column=6 + j, value=float(v))
ch = LineChart()
ch.title = "Local projections: position × shock, ln seats"
ch.add_data(Reference(ws, min_col=7, max_col=12, min_row=2, max_row=27), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=6, min_row=3, max_row=27))
style_chart(ch, ci=True, skip=3, colors=("137C7C", "8C8C8C", "8C8C8C", "D9822B", "E3B57F", "E3B57F"))
for i_ in (4, 5):
    ch.series[i_].graphicalProperties.line.dashStyle = "dash"
ch.series[3].graphicalProperties.line.dashStyle = "solid"
ch.series[3].graphicalProperties.line.width = 22000
ch.height, ch.width = 8, 16
ws.add_chart(ch, "K20")

# ---------------- raw ----------------
for nm, df in [("raw_country", rc), ("raw_airport", ra), ("raw_events", rev), ("raw_eventstudy", res_), ("raw_lp", rlp),
               ("raw_first_stage", rfs), ("raw_bins", rb), ("raw_sumstats", ss)]:
    ws = wb.create_sheet(nm)
    ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append([None if (isinstance(v, float) and not np.isfinite(v)) else v for v in row])

wb.save(OUTF)
print("saved", OUTF, [s.title for s in wb.worksheets])
