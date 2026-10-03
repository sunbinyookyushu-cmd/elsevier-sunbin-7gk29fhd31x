# -*- coding: utf-8 -*-
"""JEEM-style package for the ticket-tax paper (user decision 2026-10-02, option (다)):
  4.1 continuous treatment = predicted tax per departing passenger (EUR) from each tax's distance bands and the
      airport's 2007 mean stage length (pre-determined exposure, analogue of the JEEM subway-density measure);
      heterogeneity by 2007 international seat share and hub status (transfer-exempt taxes bite less at hubs).
  Parallel-trend tables: pooled and event-by-event (announcement donut, annual bins, 3 pre-years).
  Cost-benefit: seats and CO2 lost in the first tax year vs tax revenue (load factor assumption stated).
Stacks and events as in 95 (8 events, NLD separate; border rings as own groups, 50-km ring excluded from controls).
Dose per event (EUR per departing economy passenger, change at the event; conversions at event-date rates):
  DEU 2011: 8 / 25 / 45 by band (<=2500 km, 2500-6000, >6000);  AUT 2011: 8 / 20 / 35;  NLD 2008: 11.25 (<=2500) / 45;
  IRL 2009: 2 (<=300 km) / 10;  SWE 2018: SEK 60/250/400 = 6.2 / 25.8 / 41.2 (<=2500 / <=6000 / >6000);
  NOR 2016: NOK 80 = 8.6 flat;  GBR 2007 change: GBP 5 / 20 = 7.4 / 29.6 (<=2500 proxy for EEA / other);
  DNK 1998: DKK 75 = 10.1 on DOMESTIC departures only (dose = 10.1 x 2007 domestic seat share... 1997 share used);
  MLT 2005 change: Lm10 = 23.3 flat.
  Airport dose = band rate at the airport's pre-year mean stage length (seat-km / seat). Crude: one band per airport.
Output: _res_tax_jeem.csv, tax_dose_airports.csv
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
EV = pd.DataFrame([("NLD", "2008-07-01", "2007-02-01"), ("IRL", "2009-03-30", "2008-10-01"), ("DEU", "2011-01-01", "2010-06-01"),
                   ("AUT", "2011-04-01", "2010-10-01"), ("NOR", "2016-06-01", "2015-12-01"), ("SWE", "2018-04-01", "2017-06-01"),
                   ("GBR", "2007-02-01", "2006-12-01"), ("DNK", "1998-01-01", "1997-05-01"), ("MLT", "2005-08-01", "2004-11-01")],
# announcement dates verified from primary sources 2026-10-02 (announcement_dates_verified.csv): AUT 2010-10-23, GBR 2006-12-06,
# IRL 2008-10-14, MLT 2004-11-24, DEU 2010-06-07
                  columns=["iso3", "eff", "ann"])
for c, s in [("tE", "eff"), ("tA", "ann")]:
    dd = pd.to_datetime(EV[s])
    EV[c] = dd.dt.year * 12 + dd.dt.month
EV["pre_year"] = (EV.tA - 13) // 12
BANDS = {"DEU": [(2500, 8), (6000, 25), (1e9, 45)], "AUT": [(2500, 8), (6000, 20), (1e9, 35)], "NLD": [(2500, 11.25), (1e9, 45)],
         "IRL": [(300, 2), (1e9, 10)], "SWE": [(2500, 6.2), (6000, 25.8), (1e9, 41.2)], "NOR": [(1e9, 8.6)],
         "GBR": [(2500, 7.4), (1e9, 29.6)], "DNK": [(1e9, 10.1)], "MLT": [(1e9, 23.3)]}
CODED = {"DEU", "AUT", "NLD", "BEL", "LUX", "FRA", "ITA", "IRL", "GBR", "CHE", "SWE", "NOR", "DNK", "FIN", "ISL", "PRT",
         "ESP", "GRC", "HUN", "HRV", "MLT"}
T = pd.concat([pd.read_csv(r"data_external\aviation_taxes\taxes_west_europe.csv"),
               pd.read_csv(r"data_external\aviation_taxes\taxes_nordic_rest.csv")])
T = T[T.country_iso3.isin(CODED) & (T.event_type != "none_in_period")].copy()
td = pd.to_datetime(T.effective_date, errors="coerce")
T["t"] = td.dt.year * 12 + td.dt.month
T = T.dropna(subset=["t"])
am = pq.read_table("airport_month_sep08fix.parquet", columns=["airport_iata", "iso3", "year", "month", "dep_seats", "dep_seats_dom",
                                                              "dep_seats_intl", "dep_seat_km", "co2_dep"]).to_pandas()
am = am[am.iso3.notna() & (am.year <= 2019) & (am.dep_seats > 0)].copy()
am["t"] = am.year * 12 + am.month
am["ln_seats"] = np.log(am.dep_seats)
ya = am.groupby(["airport_iata", "year"]).agg(seats=("dep_seats", "sum"), dom=("dep_seats_dom", "sum"), intl=("dep_seats_intl", "sum"),
                                               skm=("dep_seat_km", "sum"), co2=("co2_dep", "sum"))
ya["stage"] = ya.skm / ya.seats
ya["intl_share"] = ya.intl / ya.seats
ya["dom_share"] = ya.dom / ya.seats
cb = pd.read_csv("crossborder_pairs.csv")


def dose(iso3, stage, dom_share):
    r = next(v for lim, v in BANDS[iso3] if stage <= lim)
    return r * dom_share if iso3 == "DNK" else r


out, doses = [], []
for k, ev in EV.iterrows():
    lo, hi = ev.tA - 36, ev.tE + 23
    busy = set(T[(T.t >= lo - 12) & (T.t <= hi)].country_iso3)
    tre = set(am[am.iso3 == ev.iso3].airport_iata)
    nb = cb[cb.airport.isin(tre)].groupby("neighbour").km.min()
    ctrl = (CODED - {"ITA", ev.iso3}) - busy
    d = am[(am.t >= lo) & (am.t <= hi) & (am.iso3.isin(ctrl | {ev.iso3}) | am.airport_iata.isin(nb.index))].copy()
    km = d.airport_iata.map(nb)
    d["grp"] = np.where(d.iso3 == ev.iso3, "T", np.where(km <= 50, "B50", np.where(km <= 300, "B", "C")))
    py = ev.pre_year if ev.pre_year in ya.index.get_level_values(1) else ya.index.get_level_values(1).min()
    base = ya.xs(py, level="year")
    d["stage0"] = d.airport_iata.map(base.stage)
    d["intl0"] = d.airport_iata.map(base.intl_share)
    d["dom0"] = d.airport_iata.map(base.dom_share)
    d["seats0"] = d.airport_iata.map(base.seats)
    d["co20"] = d.airport_iata.map(base.co2)
    d["hub0"] = (d.seats0 >= 5e6).astype(np.int8)
    d["dose"] = np.where(d.grp == "T", [dose(ev.iso3, s, ds) if pd.notna(s) else np.nan for s, ds in zip(d.stage0, d.dom0.fillna(0))], 0.0)
    d["stk"], d["relA"], d["relE"] = k, d.t - ev.tA, d.t - ev.tE
    d = d[~((d.t >= ev.tA) & (d.t < ev.tE)) & (d.grp != "B50")]
    out.append(d)
    doses.append(d[d.grp == "T"].drop_duplicates("airport_iata")[["airport_iata", "iso3", "stage0", "intl0", "dom0", "seats0", "dose"]].assign(event=ev.iso3 + " " + ev.eff))
D = pd.concat(out, ignore_index=True)
pd.concat(doses).to_csv("tax_dose_airports.csv", index=False)
D["fe_u"] = D.airport_iata + "_" + D.month.astype(str) + "_" + D.stk.astype(str)
D["fe_t"] = D.t.astype(str) + "_" + D.stk.astype(str)
D["post1"] = D.relE.between(0, 11).astype(np.int8)
D["post2"] = D.relE.between(12, 23).astype(np.int8)
D["pre3"] = D.relA.between(-36, -25).astype(np.int8)
D["pre2"] = D.relA.between(-24, -13).astype(np.int8)
isT, isB = (D.grp == "T").astype(np.int8), (D.grp == "B").astype(np.int8)
rows = []


def est(table, spec, d, rhs, terms, cl="iso3"):
    m = pf.feols(f"ln_seats ~ {rhs} | fe_u + fe_t", data=d, vcov={"CRV1": cl})
    t = m.tidy()
    for term, lab in terms:
        if term in t.index:
            rows.append(dict(table=table, spec=spec, term=lab, b=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"],
                             p=t.loc[term, "Pr(>|t|)"], n=int(m._N), clusters=d[cl].nunique()))


# ---- 4.1 continuous dose (EUR per passenger), event-time bins; 1 SD of dose among treated airports reported ----
D1 = D[D.post2 == 0].copy()
sd_dose = D1[D1.grp == "T"].drop_duplicates(["airport_iata", "stk"]).dose.std()
D1["dose_pre3"], D1["dose_pre2"], D1["dose_post"] = D1.dose * D1.pre3, D1.dose * D1.pre2, D1.dose * D1.post1
D1["B_post"] = isB.loc[D1.index] * D1.post1
est("4.1 dose", f"EUR per passenger x event time (dose SD among treated = {sd_dose:.1f})", D1, "dose_pre3 + dose_pre2 + dose_post + B_post",
    [("dose_pre3", "dose x pre [A-36,A-25]"), ("dose_pre2", "dose x pre [A-24,A-13]"), ("dose_post", "dose x post [E,E+11]"), ("B_post", "border 50-300 km x post")])
D1["T_post"] = isT.loc[D1.index] * D1.post1
est("4.1 dose", "binary + dose (does dose add to the on/off effect?)", D1, "T_post + dose_post + B_post",
    [("T_post", "treated x post"), ("dose_post", "dose x post")])
print("4.1 done", flush=True)

# ---- heterogeneity: intl share and hub (transfer exemption) ----
D1["intl_c"] = D1.intl0 - D1[D1.grp == "T"].drop_duplicates(["airport_iata", "stk"]).intl0.mean()
D1["T_post_intl"], D1["T_post_hub"] = D1.T_post * D1.intl_c, D1.T_post * D1.hub0
est("heterogeneity", "x international share (centred)", D1.dropna(subset=["intl_c"]), "T_post + T_post_intl + B_post",
    [("T_post", "treated x post"), ("T_post_intl", "x intl share")])
est("heterogeneity", "x hub (>= 5m seats pre-year)", D1, "T_post + T_post_hub + B_post",
    [("T_post", "treated x post, non-hub"), ("T_post_hub", "x hub")])
print("heterogeneity done", flush=True)

# ---- parallel trends by event ----
D["T_pre3"], D["T_pre2"], D["T_post1"], D["T_post2"] = isT * D.pre3, isT * D.pre2, isT * D.post1, isT * D.post2
D["B_post1"] = isB * D.post1
est("parallel trends", "pooled 8 events", D, "T_pre3 + T_pre2 + T_post1 + T_post2 + B_post1",
    [("T_pre3", "pre [A-36,A-25]"), ("T_pre2", "pre [A-24,A-13]"), ("T_post1", "post yr 1"), ("T_post2", "post yr 2")])
for k, ev in EV.iterrows():
    dk = D[D.stk == k]
    est("parallel trends", f"{ev.iso3} {ev.eff}", dk, "T_pre3 + T_pre2 + T_post1 + T_post2 + B_post1",
        [("T_pre3", "pre [A-36,A-25]"), ("T_pre2", "pre [A-24,A-13]"), ("T_post1", "post yr 1")], cl="airport_iata")
print("parallel trends done", flush=True)

# ---- cost-benefit, first tax year, per event: uses the event's own post-yr-1 coefficient ----
R = pd.DataFrame(rows)
LF = 0.80   # assumed load factor (stated in notes)
cbr = []
for k, ev in EV.iterrows():
    b = R[(R.spec == f"{ev.iso3} {ev.eff}") & (R.term == "post yr 1")].b
    if b.empty:
        continue
    b = float(b.iloc[0])
    tr = D[(D.stk == k) & (D.grp == "T")].drop_duplicates("airport_iata")
    seats0, co20 = tr.seats0.sum(), tr.co20.sum()
    pax_lost = -(np.exp(b) - 1) * seats0 * LF
    co2_lost = -(np.exp(b) - 1) * co20
    rev = (tr.dose * tr.seats0 * LF * np.exp(b)).sum()
    cbr.append(dict(event=f"{ev.iso3} {ev.eff}", coef_yr1=b, pre_seats_m=seats0 / 1e6, pax_lost_m=pax_lost / 1e6, co2_lost_kt=co2_lost / 1e6,
                    revenue_mEUR=rev / 1e6, eur_per_tCO2=rev / (co2_lost / 1000) if co2_lost > 0 else np.nan,   # co2_dep is in kg mean_dose_eur=(tr.dose * tr.seats0).sum() / seats0))
CB = pd.DataFrame(cbr)
CB.to_csv("_res_tax_costbenefit.csv", index=False)
R.to_csv("_res_tax_jeem.csv", index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 300)
print(R.round(4).to_string(index=False))
print("\nCost-benefit, first tax year (load factor 0.80 assumed; CO2 = departing-flight CO2 from the panel):")
print(CB.round(3).to_string(index=False))
