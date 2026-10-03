# -*- coding: utf-8 -*-
"""September 2008 gap in the OAG airport-month file (Fangyu delivery 2026-08-18).

Diagnosis (2026-10-02): world seats are -13.4% YoY in 2008-09 only (2008-10 -0.4%; one year later 2009-09 +16.9%).
93% of the 238 airports with >300k seats in Aug 2008 are at 0.86x their Aug-Oct seats per day in Sep 2008
(0.995x in Sep 2007), in every region, so about 4 days of schedules are missing from the extract.
Fix (user decision 2026-10-02): interpolate 2008-09 per airport from Aug and Oct 2008 and the airport's usual
September ratio.

  ratio_i  = median over 2005-07 and 2009-11 of seats_Sep / mean(seats_Aug, seats_Oct)   (years with all three > 0;
             airports without such a year get the median ratio over all airports)
  target_i = ratio_i x mean(seats_Aug2008, seats_Oct2008)          (needs Aug and Oct 2008 rows with seats > 0)
  Sep-2008 row with seats > 0: every value column x target_i / seats_Sep2008 (keeps the observed mix of the month:
                               dom/intl, gauge, stage length, CO2 per seat-km; only the level is restored)
  Sep-2008 row missing:        each value column = its own ratio x its Aug/Oct mean (row created)
  Airports without Aug and Oct 2008 seats, or with 0 seats in Sep 2008 (cargo-only rows): left as observed.
Derived log columns are recomputed for the changed rows as in 02_build_airport_month.py.
Smaller one-month bumps (+5-6% world seats in 2000-05, 2011-10, 2013-03) are NOT changed here.

Output: airport_month_sep08fix.parquet (airport_month.parquet is left untouched)
"""
import io
import sys

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

VAL = ["n_dep_flights", "dep_seats", "dep_seat_km", "co2_dep", "co2_bunker", "dep_seat_km_dom", "dep_seat_km_intl",
       "dep_seats_dom", "dep_seats_intl", "n_dep_flights_dom", "n_dep_flights_intl"]
REF_YEARS = [2005, 2006, 2007, 2009, 2010, 2011]
Y, M = 2008, 9

am = pd.read_parquet("airport_month.parquet")
key = ["airport_iata", "year", "month"]
x = am.set_index(key)[VAL]


def month(y, m):
    try:
        return x.xs((y, m), level=("year", "month"))
    except KeyError:
        return pd.DataFrame(columns=VAL)


# usual September ratio per airport and column
ratios = []
for y in REF_YEARS:
    a, s, o = month(y, 8), month(y, 9), month(y, 10)
    j = a.join(s, lsuffix="_a", how="inner").join(o.add_suffix("_o"), how="inner")
    r = pd.DataFrame({c: j[c] / ((j[c + "_a"] + j[c + "_o"]) / 2) for c in VAL})
    ok = (j[[c + "_a" for c in VAL]].to_numpy() > 0) & (j[VAL].to_numpy() > 0) & (j[[c + "_o" for c in VAL]].to_numpy() > 0)
    r = r.where(ok)
    r["year"] = y
    ratios.append(r)
rat = pd.concat(ratios).groupby(level=0)[VAL].median()
glob = rat.median()

a8, s8, o8 = month(Y, 8), month(Y, 9), month(Y, 10)
nb = a8.join(o8, lsuffix="_a", rsuffix="_o", how="inner")
nb = nb[(nb.dep_seats_a > 0) & (nb.dep_seats_o > 0)]
avg = pd.DataFrame({c: (nb[c + "_a"] + nb[c + "_o"]) / 2 for c in VAL})
r_i = rat.reindex(avg.index).fillna(glob)

# case 1: observed Sep-2008 row with seats > 0 -> scale the whole row to the interpolated seat level
obs = s8[s8.dep_seats > 0].index.intersection(avg.index)
target = r_i.loc[obs, "dep_seats"] * avg.loc[obs, "dep_seats"]
k = target / s8.loc[obs, "dep_seats"]
new_obs = s8.loc[obs, VAL].mul(k, axis=0)

# case 2: Sep-2008 row missing although Aug and Oct have seats -> build it column by column
miss = avg.index.difference(s8.index)
new_miss = (r_i.loc[miss, VAL] * avg.loc[miss, VAL])

# write back
fx = am.copy()
fx[VAL] = fx[VAL].astype(float)
sel = (fx.year == Y) & (fx.month == M) & fx.airport_iata.isin(obs)
fx.loc[sel, VAL] = new_obs.reindex(fx.loc[sel, "airport_iata"]).to_numpy()
if len(miss):
    tmpl = am[(am.year == Y) & (am.month == 10) & am.airport_iata.isin(miss)][["airport_iata", "iso3"]].drop_duplicates("airport_iata")
    add = tmpl.set_index("airport_iata").join(new_miss).reset_index()
    add["year"], add["month"] = np.int16(Y), np.int8(M)
    fx = pd.concat([fx, add], ignore_index=True)

ch = (fx.year == Y) & (fx.month == M)
fx.loc[ch, "ym"] = f"{Y}-{M:02d}"
fx.loc[ch, "t"] = (Y - 1996) * 12 + (M - 1)
pos = lambda v: v.where(v > 0)
fx.loc[ch, "ln_seats"] = np.log(pos(fx.loc[ch, "dep_seats"]))
fx.loc[ch, "ln_flights"] = np.log(pos(fx.loc[ch, "n_dep_flights"]))
fx.loc[ch, "ln_skm"] = np.log(pos(fx.loc[ch, "dep_seat_km"]))
fx.loc[ch, "ln_co2"] = np.log(pos(fx.loc[ch, "co2_bunker"]))
fx.loc[ch, "ln_gauge"] = fx.loc[ch, "ln_seats"] - fx.loc[ch, "ln_flights"]
fx.loc[ch, "ln_stage"] = fx.loc[ch, "ln_skm"] - fx.loc[ch, "ln_seats"]
fx.loc[ch, "ln_int"] = np.log(pos(fx.loc[ch, "co2_dep"])) - fx.loc[ch, "ln_skm"]
fx.loc[ch, "intl_share"] = fx.loc[ch, "dep_seats_intl"] / pos(fx.loc[ch, "dep_seats"])
fx.loc[ch, "ln_seats_dom"] = np.log(pos(fx.loc[ch, "dep_seats_dom"]))
fx.loc[ch, "ln_seats_intl"] = np.log(pos(fx.loc[ch, "dep_seats_intl"]))
fx = fx.sort_values(["airport_iata", "t"]).reset_index(drop=True)
fx.to_parquet("airport_month_sep08fix.parquet", index=False)

# report
left = s8.index.difference(obs)
print(f"Sep-2008 rows scaled: {len(obs):,} | rows created: {len(miss):,} | Sep-2008 rows left as observed: {len(left):,} "
      f"(no Aug+Oct seats or 0 seats)")
print("scale factor k (interpolated / observed seats): quantiles",
      k.quantile([.1, .25, .5, .75, .9]).round(3).to_dict())
print("airports using the all-airport median ratio (no reference year):", int(rat.reindex(avg.index).dep_seats.isna().sum()))
print("usual September seat ratio, all-airport median:", round(float(glob.dep_seats), 3))
w0 = am.groupby(["year", "month"]).dep_seats.sum()
w1 = fx.groupby(["year", "month"]).dep_seats.sum()
for (yy, mm) in [(2008, 8), (2008, 9), (2008, 10), (2009, 9)]:
    print(f"world seats {yy}-{mm:02d} YoY: before {100 * (w0[(yy, mm)] / w0[(yy - 1, mm)] - 1):+.1f}%  "
          f"after {100 * (w1[(yy, mm)] / w1[(yy - 1, mm)] - 1):+.1f}%")
print("rows before/after:", f"{len(am):,}", f"{len(fx):,}")
