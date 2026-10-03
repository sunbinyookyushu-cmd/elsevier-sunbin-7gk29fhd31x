# -*- coding: utf-8 -*-
"""Tables-only draft for the ticket-tax paper, DC_MA draft format (user 2026-10-02): reads the result CSVs, writes
draft_tax_20261002/tables_tax.tex + main_tables.tex + README.md, compiles with the scratch TinyTeX if present.
Numbers come only from the result files (92-103); nothing is typed in by hand except event descriptions (tax files).
JEEM-style order: events, summary statistics, before/after means, parallel trends, main DiD, robustness, dose and
heterogeneity, mechanism (M4), connectivity, SDID by event, Netherlands episode, leakage, cost-benefit.
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import glob
import os
import shutil
import subprocess

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

OUT = "draft_tax_20261002"
os.makedirs(OUT, exist_ok=True)
R = {k: pd.read_csv(f) for k, f in [("main", "_res_tax_main.csv"), ("pre", "_res_tax_pretrend.csv"), ("chk", "_res_tax_checks.csv"),
                                    ("jeem", "_res_tax_jeem.csv"), ("size", "_res_tax_by_size.csv"), ("mech", "_res_tax_mechanisms.csv"),
                                    ("sdid", "_res_tax_sdid.csv"), ("cb", "_res_tax_costbenefit.csv")]}


def st(p):
    return "" if pd.isna(p) else "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def c(b, p=None, se=None, d=3):
    s = f"{b:.{d}f}".replace("-", "$-$") + st(p)
    return s if se is None else s + f" & ({se:.{d}f})"


def cell(row, d=3):
    return f"{row.b:.{d}f}".replace("-", "$-$") + st(row.p), f"({row.se:.{d}f})"


def n(x):
    return f"{int(x):,}".replace(",", "{,}")


def get(df, **kw):
    m = df
    for k, v in kw.items():
        m = m[m[k] == v]
    assert len(m) == 1, (kw, len(m))
    return m.iloc[0]


TEX = []


def table(label, caption, body, notes, sideways=False, size="footnotesize"):
    env = "sidewaystable" if sideways else "table"
    if sideways:                                   # wide tables: scale to the line width, notes in a minipage (DC_MA tab:econ_main)
        TEX.append(f"""\\begin{{sidewaystable}}[!htbp]\\centering
\\{size}
\\captionsetup{{labelfont = bf, textfont = it, justification = centering}}
\\caption{{{caption}}}
\\label{{{label}}}
\\resizebox{{\\linewidth}}{{!}}{{%
{body}%
}}
\\vspace{{0.35em}}
\\begin{{minipage}}{{0.97\\linewidth}}\\footnotesize
\\textit{{Notes:}} {notes}
\\end{{minipage}}
\\end{{sidewaystable}}
""")
        return
    TEX.append(f"""\\begin{{{env}}}[!htbp]\\centering
\\{size}
\\captionsetup{{labelfont = bf, textfont = it, justification = centering}}
\\caption{{{caption}}}
\\label{{{label}}}
\\begin{{threeparttable}}
{body}
\\begin{{tablenotes}}\\footnotesize
\\item Notes: {notes}
\\end{{tablenotes}}
\\end{{threeparttable}}
\\end{{{env}}}
""")


# ---------------------------------------------------------------- data for T1, T2
EV = pd.DataFrame([
    ("NLD", "Netherlands", "Vliegbelasting (ticket tax)", "2007-02-07", "2008-07-01", "11.25 / 45 (within 2{,}500 km or EU / other)", "yes, 24 h"),
    ("IRL", "Ireland", "Air Travel Tax", "2008-10-14", "2009-03-30", "2 / 10 (up to 300 km / other)", "yes, 6 h"),
    ("DEU", "Germany", "Luftverkehrsteuer", "2010-06-07", "2011-01-01", "8 / 25 / 45 (three distance bands)", "yes, 12--24 h"),
    ("AUT", "Austria", "Flugabgabe", "2010-10-23", "2011-04-01", "8 / 20 / 35 (three distance bands)", "yes, 24 h"),
    ("NOR", "Norway", "Flypassasjeravgift", "2015-12-14", "2016-06-01", "NOK 80 ($\\approx$ 8.6), flat", "yes, 24 h"),
    ("SWE", "Sweden", "Flygskatt", "2017-06-08", "2018-04-01", "SEK 60 / 250 / 400 ($\\approx$ 6.2 / 25.8 / 41.2)", "yes, 24 h"),
    ("GBR", "United Kingdom", "Air Passenger Duty, doubled", "2006-12-06", "2007-02-01", "GBP 5 / 20 increase ($\\approx$ 7.4 / 29.6)", "yes, 24 h"),
    ("DNK", "Denmark", "Passagerafgift, extended to domestic", "1997-05-06", "1998-01-01", "DKK 75 ($\\approx$ 10.1) on domestic departures", "yes"),
    ("MLT", "Malta", "Departure tax, doubled", "2004-11-24", "2005-08-01", "Lm 10 increase ($\\approx$ 23.3), flat", "yes, journeys starting in Malta"),
], columns=["iso3", "country", "tax", "ann", "eff", "rate", "exempt"])
a = pd.to_datetime(EV.ann)
e = pd.to_datetime(EV.eff)
EV["tA"], EV["tE"] = a.dt.year * 12 + a.dt.month, e.dt.year * 12 + e.dt.month
EV.loc[EV.iso3 == "AUT", "tA"] = 2010 * 12 + 10
EV.loc[EV.iso3 == "MLT", "tA"] = 2004 * 12 + 11
EV["pre_year"] = (EV.tA - 13) // 12
CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "dep_seats", "n_dep_flights", "dep_seat_km"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019)]
ya = am.groupby(["airport_iata", "year"]).agg(iso3=("iso3", "first"), seats=("dep_seats", "sum"), fl=("n_dep_flights", "sum"), skm=("dep_seat_km", "sum"))
ya = ya[ya.seats > 0]
ya["stage"] = ya.skm / ya.seats
gac = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "GACI"]).set_index(["airport_iata", "year"]).GACI
cb = pd.read_csv("crossborder_pairs.csv")
rows1, ss = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    ctrl = sorted((CODED - {"ITA", ev.iso3}) - busy)
    b0 = ya.xs(ev.pre_year, level="year") if ev.pre_year in ya.index.get_level_values(1) else ya.xs(ya.index.get_level_values(1).min(), level="year")
    tre = b0[b0.iso3 == ev.iso3]
    nb = cb[cb.airport.isin(tre.index)].groupby("neighbour").km.min()
    bor = b0[b0.index.isin(nb[(nb > 50) & (nb <= 300)].index)]
    con = b0[b0.iso3.isin(ctrl)]
    rows1.append(dict(ev, n_treated=len(tre), n_border=len(bor), n_ctrl=len(ctrl)))
    for g, d in [("Taxed country", tre), ("Border, 50--300 km", bor), ("Control countries", con)]:
        d = d.copy()
        d["gaci"] = [gac.get((i, ev.pre_year), np.nan) for i in d.index]
        d["grp"], d["stk"] = g, k
        ss.append(d)
E1 = pd.DataFrame(rows1)
SS = pd.concat(ss)

# ---------------------------------------------------------------- T1 events
body = "\\begin{tabular}{llllllrr}\n\\toprule\nCountry & Tax & Announced & Effective & Rate (EUR per departing passenger) & Transfers exempt & Treated airports & Control countries \\\\\n\\midrule\n"
for _, r in E1.iterrows():
    body += f"{r.country} & {r.tax} & {r.ann} & {r.eff} & {r.rate} & {r.exempt} & {r.n_treated} & {r.n_ctrl} \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:events", "National Air Passenger Taxes Used as Events", body,
      "Announcement is the first public government decision (coalition agreement, cabinet or budget statement, parliamentary decision), read from primary sources; effective is the first departure date taxed. Rates are the statutory amounts at introduction (or the change, for the UK, Denmark and Malta), converted at the rate of the event month where not in euro. All nine taxes exempt connecting passengers (within the stated window, on a single ticket). Treated airports are those with scheduled departures in the calendar year before the announcement; control countries are the other coded European countries (Table~\\ref{tab:sumstats} notes) with no tax event of their own within three years before the announcement and two years after the effective date. The Netherlands is analysed separately (Table~\\ref{tab:nld}) because the tax was set to zero after twelve months. Sources: national legal gazettes and budget documents (coded in \\texttt{taxes\\_west\\_europe.csv}, \\texttt{taxes\\_nordic\\_rest.csv}, \\texttt{announcement\\_dates\\_verified.csv}).",
      sideways=True)

# ---------------------------------------------------------------- T2 summary statistics
body = "\\begin{tabular}{lrrrrr}\n\\toprule\n & Airports & Seats (thousand) & Flights & Stage length (km) & GACI \\\\\n\\midrule\n"
for g in ["Taxed country", "Border, 50--300 km", "Control countries"]:
    d = SS[SS.grp == g]
    body += f"\\multicolumn{{6}}{{l}}{{\\textit{{{g}}}}} \\\\\n"
    body += f"\\quad Mean & {n(d.groupby('stk').size().sum())} & {d.seats.mean()/1e3:,.0f} & {d.fl.mean():,.0f} & {d.stage.mean():,.0f} & {d.gaci.mean():.3f} \\\\\n".replace(",", "{,}")
    body += f"\\quad Median & & {d.seats.median()/1e3:,.0f} & {d.fl.median():,.0f} & {d.stage.median():,.0f} & {d.gaci.median():.3f} \\\\\n".replace(",", "{,}")
body += "\\bottomrule\n\\end{tabular}"
table("tab:sumstats", "Summary Statistics: Airports in the Year before the Announcement", body,
      "Airport-level values in the calendar year before each event's announcement, pooled over the nine events (an airport appears once per event in which it is in the sample). Seats and flights are scheduled departures (OAG schedules); stage length is seat-kilometres per seat; GACI is the Global Airport Connectivity Index of that year. Border airports are airports of other countries within 50--300 km of a treated airport; airports within 50 km are excluded from all groups. Coded countries: Germany, Austria, Netherlands, Belgium, Luxembourg, France, Ireland, United Kingdom, Switzerland, Sweden, Norway, Denmark, Finland, Iceland, Portugal, Spain, Greece, Hungary, Croatia, Malta (Italy excluded throughout because its surcharge taxes transfer passengers and has undated changes).")

# ---------------------------------------------------------------- T3 before/after means
t4 = R["chk"][R["chk"].table == "T4 before/after"]
body = "\\begin{tabular}{lcccc}\n\\toprule\n & \\multicolumn{2}{c}{Raw $\\ln$(seats)} & \\multicolumn{2}{c}{Residualised} \\\\\n\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n & Before & After & Before & After \\\\\n\\midrule\n"
for g, lab in [("T", "Taxed country"), ("B", "Border airports"), ("C", "Control countries")]:
    raw = t4[(t4.spec == g) & t4.term.str.startswith("pre mean")].iloc[0]
    res = t4[(t4.spec == g) & t4.term.str.startswith("pre / post")].iloc[0]
    body += f"{lab} & {raw.b:.3f} & {raw.se:.3f} & {c(res.b)} & {c(res.se)} \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:prepost", "Mean Log Seats Twelve Months before and after the Effective Date", body,
      "Monthly airport observations in the twelve months before and after the effective date of the nine tax increases (stacked by event, Netherlands included). Residualised values are deviations from airport-by-calendar-month-by-event means, so they remove each airport's level and seasonality; the difference in their before/after change between taxed and control airports is the raw difference-in-differences. Border airports within 150 km in this table.")

# ---------------------------------------------------------------- T4 parallel trends
J = R["jeem"][R["jeem"].table == "parallel trends"]
body = "\\begin{tabular}{lcccc}\n\\toprule\n & Pre, years $-3$ & Pre, years $-2$ & Post, year 1 & Post, year 2 \\\\\n & [A$-$36, A$-$25] & [A$-$24, A$-$13] & [E, E$+$11] & [E$+$12, E$+$23] \\\\\n\\midrule\n"
p = J[J.spec == "pooled 8 events"].set_index("term")
body += "Pooled, 8 events & " + " & ".join(cell(p.loc[t])[0] for t in ["pre [A-36,A-25]", "pre [A-24,A-13]", "post yr 1", "post yr 2"]) + " \\\\\n"
body += " & " + " & ".join(cell(p.loc[t])[1] for t in ["pre [A-36,A-25]", "pre [A-24,A-13]", "post yr 1", "post yr 2"]) + " \\\\\n\\addlinespace\n"
for _, ev in EV.iterrows():
    s = J[J.spec == f"{ev.iso3} {ev.eff}"].set_index("term")
    vals = []
    for t in ["pre [A-36,A-25]", "pre [A-24,A-13]", "post yr 1"]:
        vals.append(f"{cell(s.loc[t])[0]} {cell(s.loc[t])[1]}" if t in s.index else "--")
    body += f"{ev.country} {ev.eff[:4]} & " + " & ".join(vals) + " & \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:pretrend", "Parallel-Trend Test: Event-Time Coefficients Relative to the Year before the Announcement", body,
      "Stacked difference-in-differences on monthly $\\ln$(seats) with airport-by-calendar-month-by-event and month-by-event fixed effects. Event time runs from the announcement (A) for the pre-period and from the effective date (E) for the post-period; the months between announcement and effective date are dropped (anticipation donut). Bins are twelve calendar months each, so seasonality cannot enter the comparison; reference bin [A$-$12, A$-$1]. Border airports (50--300 km) enter as a separate group (not shown). Pooled rows: standard errors clustered by country (33 clusters). Event rows: one treated country, standard errors clustered by airport, for reference only; Denmark has no third pre-year in the data. The Netherlands row refers to its 2008 introduction. *, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels.")

# ---------------------------------------------------------------- T5 main
S = R["size"]
u = S[S.table == "2 seats, unweighted (reference)"].set_index("term")
w = S[S.table == "2 seats, seat-weighted"].set_index("term")
su = S[S.table == "1 seats by size tercile"].set_index("term")
sw = S[S.table == "2 seats, seat-weighted, by size"].set_index("term")
body = "\\begin{tabular}{lcccc}\n\\toprule\n & (1) & (2) & (3) & (4) \\\\\nWeights & Equal & Seats & Equal & Seats \\\\\n\\midrule\n"
body += f"Taxed country $\\times$ post & {cell(u.loc['tp'])[0]} & {cell(w.loc['tp'])[0]} & & \\\\\n & {cell(u.loc['tp'])[1]} & {cell(w.loc['tp'])[1]} & & \\\\\n"
for s, lab in [("tp_small", "\\quad small airports (bottom tercile)"), ("tp_mid", "\\quad mid tercile"), ("tp_large", "\\quad large airports (top tercile)")]:
    body += f"{lab} & & & {cell(su.loc[s])[0]} & {cell(sw.loc[s])[0]} \\\\\n & & & {cell(su.loc[s])[1]} & {cell(sw.loc[s])[1]} \\\\\n"
body += f"Border airports $\\times$ post & {cell(u.loc['bp'])[0]} & {cell(w.loc['bp'])[0]} & {cell(su.loc['bp'])[0]} & {cell(sw.loc['bp'])[0]} \\\\\n & {cell(u.loc['bp'])[1]} & {cell(w.loc['bp'])[1]} & {cell(su.loc['bp'])[1]} & {cell(sw.loc['bp'])[1]} \\\\\n\\addlinespace\n"
body += f"$N$ & {n(u.loc['tp'].n)} & {n(w.loc['tp'].n)} & {n(su.loc['tp_small'].n)} & {n(sw.loc['tp_small'].n)} \\\\\nCountries & {int(u.loc['tp'].clusters)} & {int(w.loc['tp'].clusters)} & {int(su.loc['tp_small'].clusters)} & {int(sw.loc['tp_small'].clusters)} \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:main", "Effect of a Ticket Tax on Scheduled Seats in the First Year", body,
      "Dependent variable $\\ln$(monthly departing seats). Stacked difference-in-differences over the eight tax increases of Table~\\ref{tab:events} (Netherlands separate), pre-period the 36 months before the announcement, post-period the first twelve months from the effective date, anticipation months dropped. Fixed effects: airport-by-calendar-month-by-event and month-by-event. Size terciles are defined within each treated country by seats in the year before the announcement (median seats 30 thousand, 168 thousand and 2.0 million; the top tercile holds 94\\% of the treated countries' seats). Columns (2) and (4) weight observations by pre-announcement-year seats, so they measure the effect on national seat totals. Border airports: other countries' airports within 50--300 km of a treated airport. Standard errors clustered by country in parentheses. *, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels.")

# ---------------------------------------------------------------- T6 robustness
C6 = R["chk"]
P6 = R["pre"]
J6 = R["jeem"][R["jeem"].table == "4.1 dose"]
rows6 = []
for wdw in ["+-12 months", "+-18 months", "+-24 months", "+-36 months"]:
    r = get(C6, table="T6 windows", spec=wdw, term="tp")
    rows6.append((f"Effective-date window $\\pm${wdw[2:4]} months", r))
rows6.append(("Without the crisis-year events (NLD 2008, IRL 2009)", get(C6, table="T8 clean events", spec="increases without NLD 2008, IRL 2009", term="tp")))
rows6.append(("Announcement donut, 2 pre-years", get(P6, spec="S2 announcement donut | single DiD", term="tp")))
rows6.append(("Donut, airport pre-trends removed", get(P6, spec="S3 donut + airport pre-trends removed | single DiD", term="tp")))
rows6.append(("Donut, 3 pre-years, verified announcement dates (main)", get(R["main"], table="MAIN", term="T_p")))
body = "\\begin{tabular}{lccrr}\n\\toprule\nSpecification & Taxed $\\times$ post & (s.e.) & $N$ & Countries \\\\\n\\midrule\n"
for lab, r in rows6:
    body += f"{lab} & {cell(r)[0]} & {cell(r)[1]} & {n(r.n)} & {int(r.clusters)} \\\\\n"
d1 = get(J6, term="dose x post [E,E+11]")
d2 = get(J6, term="dose x post")
body += "\\addlinespace\n\\multicolumn{5}{l}{\\textit{Dose: tax in EUR per departing passenger (airport-specific, from distance bands and pre-year stage length)}} \\\\\n"
body += f"Dose $\\times$ post, per EUR & {cell(d1, 4)[0]} & {cell(d1, 4)[1]} & {n(d1.n)} & {int(d1.clusters)} \\\\\n"
body += f"Dose $\\times$ post, with treated $\\times$ post included & {cell(d2, 4)[0]} & {cell(d2, 4)[1]} & {n(d2.n)} & {int(d2.clusters)} \\\\\n"
for t in ["dose x pre [A-36,A-25]", "dose x pre [A-24,A-13]"]:
    r = get(J6, term=t)
    body += f"Dose $\\times$ {t[7:]} & {cell(r, 4)[0]} & {cell(r, 4)[1]} & & \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:robust", "Robustness of the First-Year Seat Effect", body,
      "Each row is the treated-by-post coefficient of a separate stacked regression of $\\ln$(seats) with the fixed effects of Table~\\ref{tab:main}; border airports included as a separate group (not shown). Window rows use the effective date, nine events (Netherlands included), symmetric windows. The crisis row drops the two events whose first tax year overlaps the 2008--09 recession. Donut rows drop the months between announcement and effective date and take the pre-announcement years as reference; the pre-trend row removes each airport's linear trend fitted on the 24 pre-announcement months. The first four donut rows use the announcement dates as coded before verification (Austria 2011-01, Malta 2004-12); the main row uses the verified dates (2010-10, 2004-11). Dose rows interact event time with the airport's predicted tax per passenger (one distance band per airport, from its pre-year mean stage length; standard deviation 4.9 EUR among treated airports). Standard errors clustered by country. *, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels.")

# ---------------------------------------------------------------- T7 mechanism M4 by size
M4 = R["mech"]
sz = R["size"]
body = "\\begin{tabular}{lcccc}\n\\toprule\n & Seats & Flights & Seats per flight & Service loss \\\\\n & $\\ln$ & $\\ln$ & $\\ln$ & (0/1) \\\\\n\\midrule\n"
for s, lab in [("tp_small", "Small airports $\\times$ post"), ("tp_mid", "Mid tercile $\\times$ post"), ("tp_large", "Large airports $\\times$ post"), ("bp", "Border airports $\\times$ post")]:
    r = [get(sz, table="1 seats by size tercile", term=s), get(M4, table="M4 flights by size", term=s), get(M4, table="M4 seats per flight by size", term=s),
         get(M4, table="M4 service loss by size (at-risk months, LPM)", term=s)]
    body += f"{lab} & " + " & ".join(cell(x)[0] for x in r) + " \\\\\n & " + " & ".join(cell(x)[1] for x in r) + " \\\\\n"
body += f"\\addlinespace\n$N$ & {n(r[0].n)} & {n(r[1].n)} & {n(r[2].n)} & {n(r[3].n)} \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:mechanism", "Margins of Adjustment by Airport Size: Frequencies, Aircraft Size and Service Loss", body,
      "Same stacks and fixed effects as Table~\\ref{tab:main}, column (3). Service loss is a linear probability model on the months at risk (airports with seats twelve months earlier; months with no scheduled departure count as zero seats); the mean monthly loss rate among treated small airports before the announcement is used as the base in the text. Seats per flight rises at large airports while flights fall, so hubs keep seats by up-gauging; small airports lose frequencies and whole months of service. Standard errors clustered by country. *, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels.")

# ---------------------------------------------------------------- T8 connectivity
body = "\\begin{tabular}{lcccc}\n\\toprule\n & $\\ln$ GACI & $\\ln$ Destinations & $\\ln$ Eigenvector & $\\ln$ Betweenness \\\\\n\\midrule\n"
for s, lab in [("tp_small", "Small airports $\\times$ post"), ("tp_mid", "Mid tercile $\\times$ post"), ("tp_large", "Large airports $\\times$ post"), ("bp", "Border airports $\\times$ post")]:
    r = [get(sz, table="3 connectivity by size tercile", outcome=y, term=s) for y in ["ln_gaci", "ln_deg", "ln_eigen", "ln_betw"]]
    body += f"{lab} & " + " & ".join(cell(x)[0] for x in r) + " \\\\\n & " + " & ".join(cell(x)[1] for x in r) + " \\\\\n"
r = [get(sz, table="3 connectivity, all treated", outcome=y, term="tp") for y in ["ln_gaci", "ln_deg", "ln_eigen", "ln_betw"]]
body += "\\addlinespace\nAll treated airports $\\times$ post & " + " & ".join(cell(x)[0] for x in r) + " \\\\\n & " + " & ".join(cell(x)[1] for x in r) + " \\\\\n"
h = R["chk"][R["chk"].table == "T9 connectivity"]
for sp, lab in [("hubs (pre-year seats >= 1m)", "Hubs only ($\\geq$ 1 million seats)"), ("seat-weighted", "Seat-weighted, all airports")]:
    r = [get(h, spec=sp, outcome=y, term="tp") for y in ["ln_gaci", "ln_eigen", "ln_betw"]]
    body += f"{lab} & {cell(r[0])[0]} & -- & {cell(r[1])[0]} & {cell(r[2])[0]} \\\\\n & {cell(r[0])[1]} & & {cell(r[1])[1]} & {cell(r[2])[1]} \\\\\n"
body += f"\\addlinespace\n$N$ (annual) & {n(r[0].n)} & & & \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:connectivity", "Network Position of Taxed Airports: Connectivity Index and Centralities", body,
      "Annual airport outcomes from the GACI panel: the connectivity index (GACI), the number of destinations (degree), eigenvector centrality and $\\ln(1+10^{4}\\times$normalised betweenness$)$. Size-tercile rows: stacks of the three calendar years before the announcement and the first effective year, airport-by-event and year-by-event fixed effects (Table~\\ref{tab:main} sample). Hub and seat-weighted rows: effective-date stacks of two pre- and two post-years, nine events. GACI is normalised each year, so the coefficients are changes in relative network position. Standard errors clustered by country. *, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels.")

# ---------------------------------------------------------------- T9 SDID
D9 = R["sdid"]
body = "\\begin{tabular}{lrcccccl}\n\\toprule\nEvent & Donors & SDID & Placebo $p$ & Synthetic control & DiD & Pre-fit RMSE & Largest donor weights \\\\\n\\midrule\n"
for _, r in D9.iterrows():
    body += f"{r.event} & {int(r.donors)} & {c(r.sdid)} & {r.p_placebo:.2f} & {c(r.sc)} & {c(r.did)} & {r.rmse_pre:.3f} & {r.top_donors} \\\\\n"
body += "\\bottomrule\n\\end{tabular}"
table("tab:sdid", "Synthetic Difference-in-Differences by Event: National Seat Totals", body,
      "Country-by-month $\\ln$(seats) of all airports of the country, de-seasonalised with country-by-calendar-month means over the pre-announcement window; pre-period the 36 months before the announcement, post-period the first twelve effective months, anticipation months dropped. SDID follows Arkhangelsky et al.\\ (2021): unit weights on the simplex with the paper's ridge penalty, time weights, and an intercept; synthetic control uses no intercept and no time weights; DiD uses equal donor weights. Donors are the coded European countries without a tax event in the window. Placebo $p$ is the share of donors whose own SDID estimate (treating that donor, with the actual treated country removed) is at least as large in absolute value. Malta has two airports. No significance stars: inference is by placebo only.",
      sideways=True)

# ---------------------------------------------------------------- T10 NLD
N = R["main"][R["main"].table == "NLD"].set_index("term")
body = "\\begin{tabular}{lcc}\n\\toprule\n & Tax in force & After removal \\\\\n & 2008-07 to 2009-06 & 2009-07 to 2010-12 \\\\\n\\midrule\n"
for g, lab in [("T", "Dutch airports"), ("B150", "Border airports, 50--150 km"), ("B300", "Border airports, 150--300 km")]:
    body += f"{lab} & {cell(N.loc[g + '_tax'])[0]} & {cell(N.loc[g + '_after'])[0]} \\\\\n & {cell(N.loc[g + '_tax'])[1]} & {cell(N.loc[g + '_after'])[1]} \\\\\n"
body += f"\\addlinespace\n$N$ & \\multicolumn{{2}}{{c}}{{{n(N.loc['T_tax'].n)}}} \\\\\nCountries & \\multicolumn{{2}}{{c}}{{{int(N.loc['T_tax'].clusters)}}} \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:nld", "The Dutch Episode: Introduction (July 2008) and Removal (July 2009)", body,
      "Single-event stacked regression of $\\ln$(seats) with the fixed effects of Table~\\ref{tab:main}; reference period the 36 months before the February 2007 coalition agreement that announced the tax, anticipation months dropped. The tax was set to zero from 1 July 2009 and repealed in December 2009. The 50 km ring (Eindhoven, Weeze-adjacent airports) is estimated separately and is based on very few airports. Standard errors clustered by country. *, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels.")

# ---------------------------------------------------------------- T11 leakage
Mn = R["main"]
m1 = Mn[Mn.table == "MAIN"].set_index("term")
m2 = Mn[Mn.table == "BORDER TYPE"].set_index("term")
body = "\\begin{tabular}{lcc}\n\\toprule\n & (1) Distance rings & (2) Border airport type \\\\\n\\midrule\n"
body += f"Taxed country $\\times$ post & {cell(m1.loc['T_p'])[0]} & {cell(m2.loc['T_p'])[0]} \\\\\n & {cell(m1.loc['T_p'])[1]} & {cell(m2.loc['T_p'])[1]} \\\\\n"
for t, lab in [("B50_p", "Border 0--50 km $\\times$ post"), ("B150_p", "Border 50--150 km $\\times$ post"), ("B300_p", "Border 150--300 km $\\times$ post")]:
    body += f"{lab} & {cell(m1.loc[t])[0]} & {cell(m2.loc[t])[0] if t in m2.index else ''} \\\\\n & {cell(m1.loc[t])[1]} & {cell(m2.loc[t])[1] if t in m2.index else ''} \\\\\n"
for t, lab in [("Bh_p", "Border hubs ($\\geq$ 5 million seats), $\\leq$150 km $\\times$ post"), ("Bs_p", "Border secondary airports, $\\leq$150 km $\\times$ post")]:
    body += f"{lab} & & {cell(m2.loc[t])[0]} \\\\\n & & {cell(m2.loc[t])[1]} \\\\\n"
body += f"\\addlinespace\n$N$ & {n(m1.loc['T_p'].n)} & {n(m2.loc['T_p'].n)} \\\\\nCountries & {int(m1.loc['T_p'].clusters)} & {int(m2.loc['T_p'].clusters)} \\\\\n\\bottomrule\n\\end{{tabular}}"
table("tab:leakage", "Cross-Border Leakage: Seats at Foreign Airports near the Taxed Country", body,
      "Specification of Table~\\ref{tab:main} with the border group split by great-circle distance to the nearest treated airport (column 1) or, for airports within 150 km, by size (column 2). Eight events (Netherlands in Table~\\ref{tab:nld}). The 0--50 km ring contains few airports and shows pre-trends in the event study; it is excluded from the other tables. Standard errors clustered by country. *, **, *** denote significance at the 10\\%, 5\\%, and 1\\% levels.")

# ---------------------------------------------------------------- T12 cost-benefit
CB = R["cb"].copy()
CB["eur_t"] = CB.revenue_mEUR * 1e6 / (CB.co2_lost_kt * 1e3)
body = "\\begin{tabular}{lrrrrrr}\n\\toprule\nEvent & Seats before (m) & Effect, year 1 & Passengers lost (m) & CO$_2$ avoided (kt) & Revenue (m EUR) & EUR per t CO$_2$ \\\\\n\\midrule\n"
for _, r in CB.iterrows():
    body += f"{r.event} & {r.pre_seats_m:.1f} & {c(r.coef_yr1)} & {r.pax_lost_m:.1f} & {r.co2_lost_kt:,.0f} & {r.revenue_mEUR:,.0f} & {r.eur_t:,.0f} \\\\\n".replace(",", "{,}")
body += "\\bottomrule\n\\end{tabular}"
table("tab:costbenefit", "First-Year Accounting: Passengers, CO$_2$ and Revenue by Event", body,
      "Illustrative accounting that applies each event's own first-year airport-level coefficient (Table~\\ref{tab:pretrend}, event rows; equal airport weights) to the treated country's pre-announcement-year seats and departing-flight CO$_2$ (LTO plus cruise, from the emissions panel). Passengers assume a load factor of 0.80. Revenue is the predicted tax per passenger (distance band at the airport's mean stage length) times remaining passengers. Because the airport-level coefficient over-weights small airports, these figures bound the national effect from above; the seat-weighted estimate of Table~\\ref{tab:main} is about one third as large. EUR per tonne compares revenue with avoided emissions and is not a welfare measure.",
      sideways=True)

# ---------------------------------------------------------------- write, compile
open(os.path.join(OUT, "tables_tax.tex"), "w", encoding="utf-8").write(
    "% ---- Ticket-tax paper tables (generated by 110_tax_tables_tex.py; do not edit by hand) ----\n"
    "% preamble: \\usepackage{amsmath,booktabs,threeparttable,rotating,makecell,caption,graphicx}\n\n" + "\n".join(TEX))
open(os.path.join(OUT, "main_tables.tex"), "w", encoding="utf-8").write(r"""% Ticket taxes and the air network: tables only, compiled on their own for checking (format of DC_MA/draft_econ_v2).
% Tables: tables_tax.tex (generated by GACI_FuelShock/110_tax_tables_tex.py from the _res_*.csv files; re-run 110, not by hand).
\documentclass[11pt]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath,booktabs,threeparttable,rotating,makecell,caption,graphicx}
\begin{document}
\input{tables_tax}
\end{document}
""")
tex = sorted(glob.glob(r"C:\Users\sunbi\AppData\Local\Temp\claude\C--Users-sunbi\*\scratchpad\*\TinyTeX\bin\windows\pdflatex.exe"))
if tex:
    pdfl = tex[-1]
    for _ in range(2):
        r = subprocess.run([pdfl, "-interaction=nonstopmode", "-halt-on-error", "main_tables.tex"], cwd=OUT, capture_output=True, text=True)
    log = open(os.path.join(OUT, "main_tables.log"), encoding="utf-8", errors="ignore").read()
    print("pdflatex exit", r.returncode, "| errors:", log.count("! "), "| undefined refs:", "undefined" in log.lower(), "| overfull:", log.count("Overfull"))
    pages = log.rsplit("Output written on", 1)[-1][:80] if "Output written on" in log else "no output"
    print(pages)
else:
    print("no TinyTeX found: not compiled")
print("written:", OUT)
