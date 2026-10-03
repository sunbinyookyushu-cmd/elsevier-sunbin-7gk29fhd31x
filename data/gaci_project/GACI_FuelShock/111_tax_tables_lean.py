# -*- coding: utf-8 -*-
"""Lean tables for the ticket-tax paper (user 2026-10-02: keep only what is needed, Gendron-Carrier et al. 2022 style).
Main: T1 events, T2 main effects (seats, CO2, GACI, destinations x all / size / seat-weighted), T3 parallel trends
(seats and GACI event-time coefficients), T4 mechanism (CO2 decomposition + frequency / gauge / service loss),
T5 connectivity and emissions (GACI elasticities + Gelbach), T6 SDID by event (seats, GACI), T7 abatement accounting.
Appendix: A1 robustness (windows, crisis events, donut, trends), A2 cross-border leakage rings.
Numbers only from the _res_*.csv files. Output draft_tax_lean_20261002/ (tables_tax.tex, main_tables.tex/.pdf, README.md).
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import glob
import os
import subprocess

import numpy as np
import pandas as pd

OUT = "draft_tax_lean_20261002"
os.makedirs(OUT, exist_ok=True)
F = {k: pd.read_csv(f) for k, f in [("size", "_res_tax_by_size.csv"), ("co2", "_res_tax_co2.csv"), ("jeem", "_res_tax_jeem.csv"),
                                    ("gpre", "_res_tax_gaci_pretrend.csv"), ("mech", "_res_tax_mechanisms.csv"), ("chan", "_res_tax_co2_channel.csv"),
                                    ("gint", "_res_gaci_intensity.csv"), ("sdid", "_res_tax_sdid.csv"), ("gsdid", "_res_tax_gaci_sdid.csv"),
                                    ("ab", "_res_tax_co2_abatement.csv"), ("cb", "_res_tax_costbenefit.csv"), ("chk", "_res_tax_checks.csv"),
                                    ("pre", "_res_tax_pretrend.csv"), ("main", "_res_tax_main.csv")]}


def st(p):
    return "" if pd.isna(p) else "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def b(r, d=3):
    return f"{r.b:.{d}f}".replace("-", "$-$") + st(r.p)


def s(r, d=3):
    return f"({r.se:.{d}f})"


def n(x):
    return f"{int(x):,}".replace(",", "{,}")


def get(df, **kw):
    m = df
    for k, v in kw.items():
        m = m[m[k] == v]
    assert len(m) == 1, (kw, len(m))
    return m.iloc[0]


TEX = []


def table(label, caption, body, notes, sideways=False):
    if label in ("tab:events", "tab:seats", "tab:network", "tab:emissions", "tab:mechanism", "tab:gaci_co2"):    # wider than the text block: scale to the line width,
        TEX.append(f"\\begin{{table}}[!htbp]\\centering\n\\footnotesize\n\\captionsetup{{labelfont = bf, textfont = it, justification = centering}}\n"  # notes in a minipage (threeparttable measures the unscaled width)
                   f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\resizebox{{\\linewidth}}{{!}}{{%\n{body}%\n}}\n\\vspace{{0.35em}}\n"
                   f"\\begin{{minipage}}{{0.97\\linewidth}}\\footnotesize\n\\textit{{Notes:}} {notes}\n\\end{{minipage}}\n\\end{{table}}\n")
        return
    if sideways:
        TEX.append(f"\\begin{{sidewaystable}}[!htbp]\\centering\n\\footnotesize\n\\captionsetup{{labelfont = bf, textfont = it, justification = centering}}\n"
                   f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\resizebox{{\\linewidth}}{{!}}{{%\n{body}%\n}}\n\\vspace{{0.35em}}\n"
                   f"\\begin{{minipage}}{{0.97\\linewidth}}\\footnotesize\n\\textit{{Notes:}} {notes}\n\\end{{minipage}}\n\\end{{sidewaystable}}\n")
    else:
        TEX.append(f"\\begin{{table}}[!htbp]\\centering\n\\footnotesize\n\\captionsetup{{labelfont = bf, textfont = it, justification = centering}}\n"
                   f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\begin{{threeparttable}}\n{body}\n\\begin{{tablenotes}}\\footnotesize\n\\item Notes: {notes}\n"
                   f"\\end{{tablenotes}}\n\\end{{threeparttable}}\n\\end{{table}}\n")


STARS = "*, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels."
# ------------------------------------------------------------ T1 events
EV = [("Denmark", "Passenger tax extended to domestic flights", "1997-05-06", "1998-01-01", "DKK 75 ($\\approx$ 10)"),
      ("Malta", "Departure tax doubled", "2004-11-24", "2005-08-01", "Lm 10 increase ($\\approx$ 23)"),
      ("United Kingdom", "Air Passenger Duty doubled", "2006-12-06", "2007-02-01", "GBP 5 / 20 increase ($\\approx$ 7 / 30)"),
      ("Netherlands", "Ticket tax (repealed July 2009)", "2007-02-07", "2008-07-01", "11.25 / 45"),
      ("Ireland", "Air Travel Tax (repealed April 2014)", "2008-10-14", "2009-03-30", "2 / 10"),
      ("Germany", "Luftverkehrsteuer", "2010-06-07", "2011-01-01", "8 / 25 / 45"),
      ("Austria", "Flugabgabe", "2010-10-23", "2011-04-01", "8 / 20 / 35"),
      ("Norway", "Flypassasjeravgift", "2015-12-14", "2016-06-01", "NOK 80 ($\\approx$ 9)"),
      ("Sweden", "Flygskatt", "2017-06-08", "2018-04-01", "SEK 60 / 250 / 400 ($\\approx$ 6 / 26 / 41)")]
body = "\\begin{tabular}{lllll}\n\\toprule\nCountry & Tax & Announced & Effective & EUR per departing passenger \\\\\n\\midrule\n"
for r in EV:
    body += " & ".join(r) + " \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:events", "National Air Passenger Taxes, 1998--2018", body,
      "Announcement is the first public government decision (coalition agreement, cabinet or budget statement, parliamentary vote), read from primary sources; effective is the first taxed departure date. Rates are statutory amounts at introduction by distance band (or the increase, for the UK, Denmark and Malta), converted at event-month exchange rates. All nine taxes exempt connecting passengers on a single ticket, so hub transfer traffic is untaxed. Control airports are those of the other coded European countries (Austria, Belgium, Croatia, Denmark, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Luxembourg, Malta, Netherlands, Norway, Portugal, Spain, Sweden, Switzerland, United Kingdom) with no tax event of their own within three years before the announcement and two years after the effective date; Italy is excluded because its surcharge taxes transfer passengers. The Netherlands enters the pooled estimates of Table~\\ref{tab:seats} only through the robustness windows (Appendix Table~\\ref{tab:robust}) because its tax lasted twelve months. Sources: national legal gazettes and budget documents.")

# ------------------------------------------------------------ T2-T4: one table per headline outcome
S, C, CK, G = F["size"], F["co2"], F["chk"], F["gpre"]
Jp = F["jeem"][(F["jeem"].table == "parallel trends") & (F["jeem"].spec == "pooled 8 events")].set_index("term")
ga = G[(G.table == "A event study, all treated") & (G.outcome == "ln_gaci")].set_index("term")
gs = G[(G.table == "A event study, by size") & (G.outcome == "ln_gaci")].set_index("term")
HEAD = "\\begin{tabular}{lcccccc}\n\\toprule\n & (1) & (2) & (3) & (4) & (5) & (6) \\\\\n & All airports & All, seat-weighted & Hubs only & Small & Mid & Large \\\\\n\\midrule\n"


def block(lab, u, w, h, sz):
    out = f"{lab} & {b(u)} & {b(w) if w is not None else '--'} & {b(h) if h is not None else '--'} & " + " & ".join(b(x) for x in sz) + " \\\\\n"
    out += f" & {s(u)} & {s(w) if w is not None else ''} & {s(h) if h is not None else ''} & " + " & ".join(s(x) for x in sz) + " \\\\\n"
    return out


# T2 seats
u = get(S, table="2 seats, unweighted (reference)", term="tp"); w = get(S, table="2 seats, seat-weighted", term="tp")
sz = [get(S, table="1 seats by size tercile", term=t) for t in ["tp_small", "tp_mid", "tp_large"]]
body = HEAD + block("Taxed country $\\times$ post", u, w, None, sz)
bp = get(S, table="2 seats, unweighted (reference)", term="bp")
bpw = get(S, table="2 seats, seat-weighted", term="bp"); bps = get(S, table="1 seats by size tercile", term="bp")
body += f"Foreign airports 50--300 km $\\times$ post & {b(bp)} & {b(bpw)} & -- & \\multicolumn{{3}}{{c}}{{{b(bps)}}} \\\\\n"
body += f" & {s(bp)} & {s(bpw)} & & \\multicolumn{{3}}{{c}}{{{s(bps)}}} \\\\\n\\addlinespace\n"
body += f"Pre-trend: taxed $\\times$ [A$-$24, A$-$13] & {b(Jp.loc['pre [A-24,A-13]'])} {s(Jp.loc['pre [A-24,A-13]'])} & & & & & \\\\\n"
body += f"\\addlinespace\n$N$ & {n(u.n)} & {n(w.n)} & & \\multicolumn{{3}}{{c}}{{{n(sz[0].n)}}} \\\\\nCountries & {int(u.clusters)} & {int(w.clusters)} & & \\multicolumn{{3}}{{c}}{{{int(sz[0].clusters)}}} \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:seats", "Ticket Taxes and Scheduled Seats in the First Year", body,
      "Dependent variable $\\ln$(monthly departing seats). Stacked difference-in-differences over the eight tax increases of Table~\\ref{tab:events} (Netherlands excluded): treated airports are those of the taxing country, controls the airports of the coded European countries without a tax event in the window; foreign airports within 50--300 km of a treated airport form their own group and those within 50 km are dropped. Pre-period: 36 months before the announcement; post-period: first twelve months from the effective date; months between announcement and effective date dropped. Fixed effects: airport-by-calendar-month-by-event and month-by-event. Column (2) weights by seats in the year before the announcement and so measures the effect on national totals. Size terciles are defined within each treated country by pre-announcement seats (median 30 thousand, 168 thousand and 2.0 million seats; the top tercile carries 94\\% of treated seats). The pre-trend row is the coefficient on the second pre-announcement year relative to the first (full event-time coefficients in Appendix Table~\\ref{tab:eventtime}). Standard errors clustered by country in parentheses. " + STARS)

# T3 network position
rows3 = []
for y, lab in [("ln_gaci", "$\\ln$ GACI (connectivity index)"), ("ln_deg", "$\\ln$ destinations"), ("ln_eigen", "$\\ln$ eigenvector centrality"), ("ln_betw", "$\\ln$ betweenness centrality")]:
    u = get(S, table="3 connectivity, all treated", outcome=y, term="tp")
    w = get(CK, table="T9 connectivity", spec="seat-weighted", outcome=y, term="tp") if y != "ln_deg" else None
    h = get(CK, table="T9 connectivity", spec="hubs (pre-year seats >= 1m)", outcome=y, term="tp") if y != "ln_deg" else None
    sz = [get(S, table="3 connectivity by size tercile", outcome=y, term=t) for t in ["tp_small", "tp_mid", "tp_large"]]
    rows3.append((lab, u, w, h, sz))
body = HEAD + "".join(block(*r) for r in rows3)
bp = get(S, table="3 connectivity, all treated", outcome="ln_gaci", term="bp")
body += f"\\addlinespace\nForeign airports 50--300 km $\\times$ post, $\\ln$ GACI & {b(bp)} {s(bp)} & & & & & \\\\\n"
body += f"Pre-trend, $\\ln$ GACI: taxed $\\times$ [$E-2$] & {b(ga.loc['T_km2'])} {s(ga.loc['T_km2'])} & & & {b(gs.loc['small_km2'])} {s(gs.loc['small_km2'])} & {b(gs.loc['mid_km2'])} {s(gs.loc['mid_km2'])} & {b(gs.loc['large_km2'])} {s(gs.loc['large_km2'])} \\\\\n"
body += f"\\addlinespace\n$N$ (airport-years) & {n(rows3[0][1].n)} & {n(rows3[0][2].n)} & {n(rows3[0][3].n)} & \\multicolumn{{3}}{{c}}{{{n(rows3[0][4][0].n)}}} \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:network", "Ticket Taxes and the Network Position of Taxed Airports", body,
      "Annual outcomes from the GACI panel: the Global Airport Connectivity Index (normalised each year, so coefficients are changes in relative network position), the number of destinations, eigenvector centrality and $\\ln(1+10^{4}\\times$normalised betweenness$)$. Columns (1) and (4)--(6): stacks of the three calendar years before the announcement and the first effective year, airport-by-event and year-by-event fixed effects, eight events. Columns (2)--(3): effective-date stacks of two years before and after, nine events; hubs are airports with at least one million seats in the pre-year. Size terciles as in Table~\\ref{tab:seats}. The pre-trend row reports the coefficient two years before the effective year relative to the year before (full event-time coefficients in Appendix Table~\\ref{tab:eventtime}). Standard errors clustered by country in parentheses. " + STARS)

# T4 emissions
rows4 = []
for y, lab in [("ln_co2", "$\\ln$ CO$_2$ (departing flights)"), ("ln_co2_seat", "$\\ln$ CO$_2$ per seat"), ("ln_int", "$\\ln$ CO$_2$ per seat-kilometre")]:
    u = get(C, table="A all treated, unweighted", outcome=y, term="tp"); w = get(C, table="A all treated, seat-weighted", outcome=y, term="tp")
    sz = [get(C, table="A by size tercile", outcome=y, term=t) for t in ["tp_small", "tp_mid", "tp_large"]]
    rows4.append((lab, u, w, None, sz))
body = HEAD.replace("Hubs only", "--") + "".join(block(*r) for r in rows4)
bp = get(C, table="A all treated, unweighted", outcome="ln_co2", term="bp"); bpw = get(C, table="A all treated, seat-weighted", outcome="ln_co2", term="bp")
body += f"\\addlinespace\nForeign airports 50--300 km $\\times$ post, $\\ln$ CO$_2$ & {b(bp)} {s(bp)} & {b(bpw)} {s(bpw)} & & & & \\\\\n"
body += f"\\addlinespace\n$N$ & {n(rows4[0][1].n)} & {n(rows4[0][2].n)} & & \\multicolumn{{3}}{{c}}{{{n(rows4[0][4][0].n)}}} \\\\\nCountries & {int(rows4[0][1].clusters)} & {int(rows4[0][2].clusters)} & & \\multicolumn{{3}}{{c}}{{{int(rows4[0][4][0].clusters)}}} \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:emissions", "Ticket Taxes and Aviation CO$_2$ in the First Year", body,
      "Monthly departing-flight CO$_2$ (LTO plus cruise) from the emissions panel; specification, sample, weights and size terciles as in Table~\\ref{tab:seats}. CO$_2$ per seat-kilometre is the fuel intensity of the remaining flights. Column (3) is left empty because the hub definition of Table~\\ref{tab:network} applies to the annual panel. Standard errors clustered by country in parentheses. " + STARS)

# ------------------------------------------------------------ T3 parallel trends
J = F["jeem"][(F["jeem"].table == "parallel trends") & (F["jeem"].spec == "pooled 8 events")].set_index("term")
G = F["gpre"]
ga = G[(G.table == "A event study, all treated") & (G.outcome == "ln_gaci")].set_index("term")
gs = G[(G.table == "A event study, by size") & (G.outcome == "ln_gaci")].set_index("term")
body = "\\begin{tabular}{lcccc}\n\\toprule\n & \\multicolumn{2}{c}{Before} & \\multicolumn{2}{c}{After} \\\\\n\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
body += "\\multicolumn{5}{l}{\\textit{Panel A. Seats, monthly (bins of twelve months; reference: the year before the announcement)}} \\\\\n & [A$-$36, A$-$25] & [A$-$24, A$-$13] & [E, E$+$11] & [E$+$12, E$+$23] \\\\\n"
body += "All treated airports & " + " & ".join(b(J.loc[t]) for t in ["pre [A-36,A-25]", "pre [A-24,A-13]", "post yr 1", "post yr 2"]) + " \\\\\n & " + " & ".join(s(J.loc[t]) for t in ["pre [A-36,A-25]", "pre [A-24,A-13]", "post yr 1", "post yr 2"]) + " \\\\\n\\addlinespace\n"
body += "\\multicolumn{5}{l}{\\textit{Panel B. Connectivity (GACI), annual (reference: the year before the effective year)}} \\\\\n & $E-3$ & $E-2$ & $E$ & $E+1$ \\\\\n"
body += "All treated airports & " + " & ".join(b(ga.loc[t]) for t in ["T_km3", "T_km2", "T_k0", "T_k1"]) + " \\\\\n & " + " & ".join(s(ga.loc[t]) for t in ["T_km3", "T_km2", "T_k0", "T_k1"]) + " \\\\\n"
for sz, lab in [("small", "Small"), ("mid", "Mid"), ("large", "Large")]:
    body += f"{lab} & " + " & ".join(b(gs.loc[f"{sz}_{t}"]) for t in ["km3", "km2", "k0", "k1"]) + " \\\\\n & " + " & ".join(s(gs.loc[f"{sz}_{t}"]) for t in ["km3", "km2", "k0", "k1"]) + " \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:eventtime", "Event-Time Coefficients: No Pre-Trends before the Tax", body,
      "Specification of Tables~\\ref{tab:seats} and \\ref{tab:network} with event-time bins instead of a single post indicator. Panel A: $\\ln$(seats), pooled eight events, bins of twelve calendar months so that seasonality cannot enter, reference bin the twelve months before the announcement (A); post bins count from the effective date (E). Panel B: $\\ln$(GACI), annual, reference the year before the effective year. Border airports enter as a separate group (not shown). Standard errors clustered by country (33). " + STARS)

# ------------------------------------------------------------ T4 mechanism
CH, M4 = F["chan"], F["mech"]
body = "\\begin{tabular}{lcccc}\n\\toprule\n & All treated & Small & Mid & Large \\\\\n\\midrule\n\\multicolumn{5}{l}{\\textit{Panel A. Exact decomposition of annual CO$_2$: $\\ln\\text{CO}_2 = \\ln\\text{destinations} + \\ln(\\text{flights per destination}) + \\ln(\\text{CO}_2\\text{ per flight})$}} \\\\\n"
for y, lab in [("ln_co2", "$\\ln$ CO$_2$ (total)"), ("ln_deg", "\\quad $\\ln$ destinations (network margin)"), ("ln_fl_per_dest", "\\quad $\\ln$ flights per destination (frequency margin)"), ("ln_co2_per_fl", "\\quad $\\ln$ CO$_2$ per flight (aircraft and distance margin)")]:
    a = get(CH, table="decomposition, all treated", outcome=y, term="tp")
    z = [get(CH, table="decomposition, by size", outcome=y, term=t) for t in ["tp_small", "tp_mid", "tp_large"]]
    body += f"{lab} & {b(a)} & " + " & ".join(b(x) for x in z) + f" \\\\\n & {s(a)} & " + " & ".join(s(x) for x in z) + " \\\\\n"
body += "\\addlinespace\n\\multicolumn{5}{l}{\\textit{Panel B. Monthly margins}} \\\\\n"
for lab, tab, y in [("$\\ln$ flights", "M4 flights by size", "ln_fl"), ("$\\ln$ seats per flight", "M4 seats per flight by size", "ln_gauge"),
                    ("Service loss (0/1, at-risk months)", "M4 service loss by size (at-risk months, LPM)", "loss")]:
    z = [get(M4, table=tab, term=t) for t in ["tp_small", "tp_mid", "tp_large"]]
    body += f"{lab} & -- & " + " & ".join(b(x) for x in z) + " \\\\\n & & " + " & ".join(s(x) for x in z) + " \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:mechanism", "How Emissions Fall: Route Exit, Not Fewer or Smaller Flights", body,
      "Panel A: the three components add up to total CO$_2$ by construction (annual stacks of Table~\\ref{tab:seats}, three pre-years and the effective year; destinations from the GACI panel). Panel B: monthly stacks of Table~\\ref{tab:seats}; service loss is a linear probability model on airport-months with scheduled departures twelve months earlier (months with no departure count as zero seats). Standard errors clustered by country. " + STARS)

# ------------------------------------------------------------ T5 GACI and emissions
GI = F["gint"]
el = GI[GI.table == "1 within-airport elasticity to ln GACI"]
body = "\\begin{tabular}{lcccccc}\n\\toprule\n\\multicolumn{7}{l}{\\textit{Panel A. Within-airport elasticities to $\\ln$ GACI, all airports 1996--2019}} \\\\\n & $\\ln$ CO$_2$ & $\\ln$ destinations & $\\ln$ seats per flight & $\\ln$ stage length & $\\ln$ CO$_2$ per seat-km & $\\ln$ CO$_2$ per seat \\\\\n\\midrule\n"
for sp, lab in [("airport + year FE", "Airport and year FE"), ("airport + country x year FE", "Airport and country-by-year FE")]:
    z = [get(el, spec=sp, outcome=y) for y in ["ln_co2", "ln_deg", "ln_gauge", "ln_stage", "ln_int", "ln_co2_seat"]]
    body += f"{lab} & " + " & ".join(b(x) for x in z) + " \\\\\n & " + " & ".join(s(x) for x in z) + " \\\\\n"
body += f"$N$ & \\multicolumn{{6}}{{c}}{{{n(z[0].n)}}} \\\\\n\\addlinespace\n\\multicolumn{{7}}{{l}}{{\\textit{{Panel B. Decomposition of the tax effect: direct effect holding GACI fixed, and the part running through GACI}}}} \\\\\n"
body += " & \\multicolumn{3}{c}{$\\ln$ CO$_2$ (total)} & \\multicolumn{3}{c}{$\\ln$ CO$_2$ per seat-km} \\\\\n\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}\n & Total & Direct & Via GACI & Total & Direct & Via GACI \\\\\n"
for sz in ["small", "mid", "large"]:
    vals = []
    for tab in ["2 Gelbach: total CO2", "2 Gelbach: CO2 per seat-km"]:
        t_ = get(GI, table=tab, spec=sz, term="total tax effect")
        d_ = get(GI, table=tab, spec=sz, term="direct (GACI held fixed)")
        i_ = get(GI, table=tab, spec=sz, term="indirect via GACI = (tax->GACI) x (GACI->Y)")
        vals += [b(t_), b(d_), f"{i_.b:.3f}".replace("-", "$-$")]
    body += f"{sz.capitalize()} airports & " + " & ".join(vals) + " \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:gaci_co2", "Connectivity and Emissions: More Connected Airports Emit More in Total but Less per Seat-Kilometre", body,
      "Panel A: coefficients of $\\ln$ GACI in airport-year regressions with the stated fixed effects; descriptive within-airport associations, not causal effects. Panel B: Gelbach (2016) decomposition on the annual tax stacks of Table~\\ref{tab:mechanism}: the total tax coefficient by size tercile, the coefficient when $\\ln$ GACI is added as a control (direct), and the difference, which equals the tax effect on $\\ln$ GACI times the conditional coefficient of $\\ln$ GACI (3.40 for total CO$_2$, $-$0.63 for CO$_2$ per seat-km). The decomposition is an accounting identity and assumes GACI is the only omitted channel; it is not an instrumental-variables mediation estimate. Standard errors clustered by country. " + STARS)

# ------------------------------------------------------------ T6 SDID
SD, GS = F["sdid"], F["gsdid"]
body = "\\begin{tabular}{lrcccc}\n\\toprule\n & & \\multicolumn{2}{c}{National seats} & \\multicolumn{2}{c}{Mean GACI (seat-weighted)} \\\\\n\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\nEvent & Donors & SDID & Placebo $p$ & SDID & Placebo $p$ \\\\\n\\midrule\n"
for _, r in SD.iterrows():
    g = GS[(GS.event == r.event) & (GS.outcome == "seat-weighted country GACI")]
    gv = f"{g.iloc[0].sdid:.3f}".replace("-", "$-$") + f" & {g.iloc[0].p_placebo:.2f}" if len(g) else "-- & --"
    body += f"{r.event} & {int(r.donors)} & {r.sdid:.3f} & {r.p_placebo:.2f} & {gv} \\\\\n".replace("& -0", "& $-$0")
body += "\\bottomrule\n\\end{tabular}"
table("tab:sdid", "Synthetic Difference-in-Differences by Event: National Totals Barely Move", body,
      "Country-level synthetic difference-in-differences (Arkhangelsky et al.\\ 2021): unit and time weights on the simplex with the paper's ridge penalty. Seats: country-by-month $\\ln$(seats) de-seasonalised with pre-announcement country-by-calendar-month means, 36 pre-months, first twelve effective months, anticipation months dropped. GACI: seat-weighted country mean of $\\ln$ GACI, annual, six pre-years, effective year and the next (Denmark has too few pre-years). Donors: coded European countries without a tax event in the window. Placebo $p$: share of donors whose own estimate, treating that donor with the actual treated country removed, is at least as large in absolute value. Malta has two airports.")

# ------------------------------------------------------------ T7 abatement
AB, CB = F["ab"], F["cb"]
body = "\\begin{tabular}{lrrrrrr}\n\\toprule\n & Airports & CO$_2$ avoided (kt) & Revenue (m EUR) & EUR per t CO$_2$ & GACI lost (index units) & Destinations lost \\\\\n\\midrule\n"
for _, r in AB.iterrows():
    body += f"{r['size'].capitalize()} airports & {int(r.airports)} & {r.co2_avoided_kt:,.0f} & {r.revenue_mEUR:,.0f} & {r.eur_per_t:,.0f} & {r.gaci_lost:.2f} & {r.destinations_lost:,.0f} \\\\\n".replace(",", "{,}")
tot = AB.sum(numeric_only=True)
body += f"\\midrule\nAll treated airports & {int(tot.airports)} & {tot.co2_avoided_kt:,.0f} & {tot.revenue_mEUR:,.0f} & {tot.revenue_mEUR*1e6/(tot.co2_avoided_kt*1e3):,.0f} & {tot.gaci_lost:.2f} & {tot.destinations_lost:,.0f} \\\\\n".replace(",", "{,}")
body += "\\bottomrule\n\\end{tabular}"
table("tab:abatement", "First-Year Accounting: Emissions Avoided, Revenue Raised and Connectivity Lost, by Airport Size", body,
      "Each row applies the size tercile's first-year coefficients (CO$_2$ from Table~\\ref{tab:emissions}; GACI and destinations from the annual stacks) to the pooled treated airports' pre-announcement-year CO$_2$, GACI and destinations. Revenue is the statutory tax at the airport's distance band times remaining passengers, assuming a load factor of 0.80. The large-airport coefficients are not statistically different from zero, so the large-airport and total rows are point estimates with wide uncertainty; the small- and mid-airport rows rest on precisely estimated coefficients. EUR per tonne compares revenue with avoided emissions and is not a welfare measure.", sideways=True)

# ------------------------------------------------------------ A1 robustness
CK, PR, MN = F["chk"], F["pre"], F["main"]
rows = [(f"Effective-date window $\\pm${w[2:4]} months, nine events", get(CK, table="T6 windows", spec=w, term="tp")) for w in ["+-12 months", "+-18 months", "+-24 months", "+-36 months"]]
rows += [("Without the recession-year events (Netherlands 2008, Ireland 2009)", get(CK, table="T8 clean events", spec="increases without NLD 2008, IRL 2009", term="tp")),
         ("Announcement donut, two pre-years", get(PR, spec="S2 announcement donut | single DiD", term="tp")),
         ("Donut, airport-specific pre-trends removed", get(PR, spec="S3 donut + airport pre-trends removed | single DiD", term="tp")),
         ("Donut, three pre-years, verified announcement dates (main)", get(MN, table="MAIN", term="T_p"))]
body = "\\begin{tabular}{lcrr}\n\\toprule\nSpecification & Taxed $\\times$ post & $N$ & Countries \\\\\n\\midrule\n"
for lab, r in rows:
    body += f"{lab} & {b(r)} {s(r)} & {n(r.n)} & {int(r.clusters)} \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:robust", "Robustness of the First-Year Seat Effect (Equal Airport Weights)", body,
      "Treated-by-post coefficient of $\\ln$(seats) from separate stacked regressions with the fixed effects of Table~\\ref{tab:seats}. Window rows use the effective date with symmetric windows. Donut rows drop the months between announcement and effective date; the pre-trend row removes each airport's linear trend fitted on the 24 months before the announcement. The first four donut rows were estimated with the announcement dates as coded before verification (Austria 2011-01, Malta 2004-12); the main row uses the verified dates. Standard errors clustered by country. " + STARS)

# ------------------------------------------------------------ A2 leakage
m1 = MN[MN.table == "MAIN"].set_index("term")
m2 = MN[MN.table == "BORDER TYPE"].set_index("term")
body = "\\begin{tabular}{lcc}\n\\toprule\n & (1) Distance rings & (2) Border airport type \\\\\n\\midrule\n"
body += f"Taxed country $\\times$ post & {b(m1.loc['T_p'])} {s(m1.loc['T_p'])} & {b(m2.loc['T_p'])} {s(m2.loc['T_p'])} \\\\\n"
for t, lab in [("B50_p", "Foreign airports 0--50 km $\\times$ post"), ("B150_p", "Foreign airports 50--150 km $\\times$ post"), ("B300_p", "Foreign airports 150--300 km $\\times$ post")]:
    body += f"{lab} & {b(m1.loc[t])} {s(m1.loc[t])} & {(b(m2.loc[t]) + ' ' + s(m2.loc[t])) if t in m2.index else ''} \\\\\n"
for t, lab in [("Bh_p", "Foreign hubs ($\\geq$ 5 million seats) within 150 km $\\times$ post"), ("Bs_p", "Foreign secondary airports within 150 km $\\times$ post")]:
    body += f"{lab} & & {b(m2.loc[t])} {s(m2.loc[t])} \\\\\n"
body += f"\\addlinespace\n$N$ & {n(m1.loc['T_p'].n)} & {n(m2.loc['T_p'].n)} \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:leakage", "Cross-Border Leakage: Seats at Foreign Airports near the Taxed Country", body,
      "Specification of Table~\\ref{tab:seats}, column (1), with the border group split by great-circle distance to the nearest treated airport, or by size within 150 km. The 0--50 km ring holds few airports and shows pre-trends in the event study, so it is excluded elsewhere. The Dutch tax of 2008, analysed separately, is the one case with measurable leakage: seats at foreign airports within 150 km rose 16\\% while the tax was in force (results available in the replication files). Standard errors clustered by country. " + STARS)

# ------------------------------------------------------------ write and compile
open(os.path.join(OUT, "tables_tax.tex"), "w", encoding="utf-8").write(
    "% ---- Ticket-tax paper, lean table set (generated by 111_tax_tables_lean.py; do not edit by hand) ----\n\n" + "\n".join([TEX[i] for i in (0, 1, 2, 3, 5, 6, 7, 8)])
    + "\n\\clearpage\n\\appendix\n\\setcounter{table}{0}\n\\renewcommand{\\thetable}{A\\arabic{table}}\n\n" + "\n".join([TEX[i] for i in (4, 9, 10)]))
open(os.path.join(OUT, "main_tables.tex"), "w", encoding="utf-8").write(r"""% Ticket taxes and the air network: lean table set (7 main + 2 appendix), compiled for checking.
% Generated by GACI_FuelShock/111_tax_tables_lean.py from the _res_*.csv files; re-run 111, do not edit tables_tax.tex by hand.
\documentclass[11pt]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath,booktabs,threeparttable,rotating,makecell,caption,graphicx}
\begin{document}
\input{tables_tax}
\end{document}
""")
tex = sorted(glob.glob(r"C:\Users\sunbi\AppData\Local\Temp\claude\C--Users-sunbi\*\scratchpad\*\TinyTeX\bin\windows\pdflatex.exe"))
if tex:
    for _ in range(2):
        r = subprocess.run([tex[-1], "-interaction=nonstopmode", "-halt-on-error", "main_tables.tex"], cwd=OUT, capture_output=True, text=True)
    log = open(os.path.join(OUT, "main_tables.log"), encoding="utf-8", errors="ignore").read()
    print("pdflatex exit", r.returncode, "| errors:", log.count("! "), "| overfull:", log.count("Overfull"), "|", log.rsplit("Output written on", 1)[-1][:60])
print("written:", OUT)
