# -*- coding: utf-8 -*-
"""Aviation ticket taxes: stacked DiD, first pass (user 2026-10-02: "한번 해 보자").
Design 1 = transfer-exempt national departure taxes in Europe (expected channel: departing passengers drive to
foreign border airports; hubs protected by the transfer exemption). Events coded from
data_external/aviation_taxes/taxes_west_europe.csv and taxes_nordic_rest.csv (effective dates from legal texts):
  increases: NLD 2008-07-01 intro, IRL 2009-03-30 intro, DEU 2011-01-01 intro, AUT 2011-04-01 intro,
             NOR 2016-06-01 intro, SWE 2018-04-01 intro, GBR 2007-02-01 doubling, DNK 1998-01-01 domestic added,
             MLT 2005-08-01 doubling
  cuts:      NLD 2009-07-01 rate zero, DNK 2007-01-01 abolition, MLT 2008-11-01 abolition, IRL 2014-04-01 abolition,
             ISL 2011-05-18 abolition, AUT 2018-01-01 halved, NOR 2002-04-01 abolition
Stack per event: months t0-12 .. t0+11 (1996-2019 only). Treated = airports of the event country. Border = airports of
other countries within 150 km of a treated airport (crossborder_pairs.csv), estimated as their own group, never controls.
Controls = airports of the other researched European countries (21 coded countries) with no coded tax event within
the window; Italy excluded throughout (surcharge taxes transfers, several undated changes); airports in uncoded
countries (e.g. POL, CZE) are not used.
(A) monthly ln seats: ln S_ist = a_(i x cal.month x s) + d_(t x s) + b_T (Treat x Post) + b_B (Border x Post) + e
(B) annual relative connectivity ln GACI and ln Eigen: years E-2..E+2 (E = onset year if Jan-Jun, else next year),
    FE airport x stack and year x stack.
Also by event (treated and border coefficients). SE clustered by country (few clusters: read p-values with care).
Output: tax_events_design1.csv, _res_tax_did.csv
"""
import platform


def _no_wmi(*a, **k):
    raise OSError("WMI disabled")


platform._wmi_query = _no_wmi  # the WMI query in platform.machine() crashes Python 3.12 on this PC (0x8007000e)
import io
import sys
import warnings

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyfixest as pf

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
EV = pd.DataFrame([
    ("NLD", "2008-07-01", "increase", "intro EUR 11.25/45"), ("IRL", "2009-03-30", "increase", "intro EUR 2/10"),
    ("DEU", "2011-01-01", "increase", "intro EUR 8/25/45"), ("AUT", "2011-04-01", "increase", "intro EUR 8/20/35"),
    ("NOR", "2016-06-01", "increase", "intro NOK 80"), ("SWE", "2018-04-01", "increase", "intro SEK 60/250/400"),
    ("GBR", "2007-02-01", "increase", "APD doubled"), ("DNK", "1998-01-01", "increase", "domestic added, DKK 75"),
    ("MLT", "2005-08-01", "increase", "Lm10 -> Lm20"),
    ("NLD", "2009-07-01", "cut", "rate set to zero"), ("DNK", "2007-01-01", "cut", "abolished"),
    ("MLT", "2008-11-01", "cut", "abolished"), ("IRL", "2014-04-01", "cut", "abolished"),
    ("ISL", "2011-05-18", "cut", "abolished"), ("AUT", "2018-01-01", "cut", "halved"), ("NOR", "2002-04-01", "cut", "abolished"),
], columns=["iso3", "date", "kind", "what"])
d0 = pd.to_datetime(EV.date)
EV["t0"] = d0.dt.year * 12 + d0.dt.month
EV["E"] = np.where(d0.dt.month <= 6, d0.dt.year, d0.dt.year + 1)
EV.to_csv("tax_events_design1.csv", index=False)

CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & T.effective_date.notna() & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])

am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats"]).to_pandas()
am = am[am.iso3.isin(CODED - {"ITA"}) | am.iso3.notna()]
am = am[(am.year <= 2019) & (am.dep_seats > 0)]
am["t"] = am.year * 12 + am.month
am["ln_seats"] = np.log(am.dep_seats)
cb = pd.read_csv("crossborder_pairs.csv")
cb = cb[cb.km <= 150]
hp = pd.read_csv("hub_panel.csv", usecols=["airport_iata", "year", "iso3", "GACI", "Eigen"])
hp = hp[(hp.year <= 2019) & (hp.GACI > 0)]
hp["ln_gaci"] = np.log(hp.GACI)
hp["ln_eigen"] = np.log(hp.Eigen.where(hp.Eigen > 0))

ms, ys = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.t0 - 12, ev.t0 + 11
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)            # any coded event in or just before the window
    treated_air = set(am[am.iso3 == ev.iso3].airport_iata)
    border_air = set(cb[cb.airport.isin(treated_air)].neighbour)
    ctrl_c = (CODED - {"ITA", ev.iso3}) - busy
    d = am[(am.t >= lo) & (am.t <= hi) & (am.iso3.isin(ctrl_c | {ev.iso3}) | am.airport_iata.isin(border_air))].copy()
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(d.airport_iata.isin(border_air), "B", "C"))
    d["stk"], d["post"] = k, (d.t >= ev.t0).astype(np.int8)
    ms.append(d)
    y = hp[(hp.year >= ev.E - 2) & (hp.year <= ev.E + 2) & (hp.iso3.isin(ctrl_c | {ev.iso3}) | hp.airport_iata.isin(border_air))].copy()
    y["grp"] = np.where(y.iso3 == ev.iso3, "T", np.where(y.airport_iata.isin(border_air), "B", "C"))
    y["stk"], y["post"] = k, (y.year >= ev.E).astype(np.int8)
    ys.append(y)
    print(f"{ev.iso3} {ev.date} {ev.kind}: control countries {len(ctrl_c)}, treated airports {len(treated_air & set(d.airport_iata))}, "
          f"border airports {d[d.grp == 'B'].airport_iata.nunique()}", flush=True)
M = pd.concat(ms, ignore_index=True)
Y = pd.concat(ys, ignore_index=True)
for D in (M, Y):
    D["tp"] = ((D.grp == "T") & (D.post == 1)).astype(np.int8)
    D["bp"] = ((D.grp == "B") & (D.post == 1)).astype(np.int8)
M["fe_u"] = M.airport_iata + "_" + M.month.astype(str) + "_" + M.stk.astype(str)
M["fe_t"] = M.t.astype(str) + "_" + M.stk.astype(str)
Y["fe_u"] = Y.airport_iata + "_" + Y.stk.astype(str)
Y["fe_t"] = Y.year.astype(str) + "_" + Y.stk.astype(str)

rows = []
for kind in ["increase", "cut"]:
    ks = set(EV[EV.kind == kind].index)
    for lab, D, yv in [("ln seats (monthly)", M, "ln_seats"), ("ln GACI (annual)", Y, "ln_gaci"), ("ln eigenvector (annual)", Y, "ln_eigen")]:
        dd = D[D.stk.isin(ks)].dropna(subset=[yv])
        m = pf.feols(f"{yv} ~ tp + bp | fe_u + fe_t", data=dd, vcov={"CRV1": "iso3"})
        t = m.tidy()
        for term in ["tp", "bp"]:
            rows.append(dict(kind=kind, outcome=lab, event="pooled", term="taxed country" if term == "tp" else "border airports",
                             b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"], p=t.loc[term, "Pr(>|t|)"], n=int(m._N),
                             clusters=dd.iso3.nunique()))
        if yv == "ln_seats":
            for k in sorted(ks):
                dk = dd[dd.stk == k]
                try:
                    m = pf.feols(f"{yv} ~ tp + bp | fe_u + fe_t", data=dk, vcov={"CRV1": "airport_iata"})
                    t = m.tidy()
                    for term in ["tp", "bp"]:
                        if term in t.index:
                            rows.append(dict(kind=kind, outcome=lab, event=f"{EV.loc[k, 'iso3']} {EV.loc[k, 'date']} ({EV.loc[k, 'what']})",
                                             term="taxed country" if term == "tp" else "border airports", b=t.loc[term, "Estimate"],
                                             se=t.loc[term, "Std. Error"], p=t.loc[term, "Pr(>|t|)"], n=int(m._N),
                                             clusters=dk.airport_iata.nunique()))
                except Exception as ex:
                    print("event", k, "failed:", ex)
R = pd.DataFrame(rows)
R.to_csv("_res_tax_did.csv", index=False)
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 200)
print(R.round(4).to_string(index=False))
