# sumstat_co2.py (2026-09-25). Summary statistics for the GACI-CO2 paper, estimation sample of Table 1 (N = 4,634).
# Merge mirrors co2_exclusion_suite_cl.do / co2_feyrer_mechanism_cl.do.
import numpy as np
import pandas as pd

G = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI"
H = G + r"\GACI_CO2"

co2 = pd.read_csv(H + r"\co2_country_year.csv").rename(columns={"iso3": "c", "year": "y"})
g = pd.read_csv(G + r"\gaci_panel_combined.csv")
plc = pd.read_csv(H + r"\placebo_covariates.csv")
mea = pd.read_csv(G + r"\gaci_panel_measures.csv", usecols=["c", "y", "ln_gaci_max"])
spb = pd.read_csv(H + r"\spillover_bands.csv", usecols=["c", "y", "has_contig", "nbr_g_contig", "nbr_f_contig"])

d = g.merge(co2, on=["c", "y"], how="left").merge(plc, on=["c", "y"], how="left", suffixes=("", "_p"))
d = d.merge(mea, on=["c", "y"], how="left").merge(spb, on=["c", "y"], how="left")

d["ln_co2_tot"] = np.log(d.co2_bunker.where(d.co2_bunker > 0))
s = d[d[["ln_co2_tot", "ln_gaci_cwm", "feyrer_int", "lnpop", "ln_sea_ma"]].notna().all(axis=1)].copy()
n_c = s.groupby("c").y.transform("size"); print("singletons:", s.loc[n_c == 1, ["c","y"]].values.tolist()); s = s[n_c > 1].copy()
print("estimation sample:", len(s), "countries:", s.c.nunique(), "years:", s.y.min(), s.y.max())

pos = lambda x: x.where(x > 0)
s["co2_mt"] = s.co2_bunker / 1e9
s["co2_intl_mt"] = s.co2_bunker_intl / 1e9
s["co2_dom_mt"] = pos(s.co2_bunker - s.co2_bunker_intl) / 1e9
s["co2_lto_mt"] = s.co2_lto / 1e9
s["co2_5050_mt"] = s.co2_5050 / 1e9
s["skm_bn"] = s.dep_seat_km / 1e9
s["flights_k"] = s.n_dep_flights / 1e3
s["gauge"] = s.dep_seats / s.n_dep_flights.where(s.n_dep_flights > 0)
s["stage"] = s.dep_seat_km / s.dep_seats.where(s.dep_seats > 0)
s["intensity_g"] = 1000 * s.co2_bunker / s.dep_seat_km.where(s.dep_seat_km > 0)
s["lto_share"] = s.co2_lto / s.co2_bunker
s["intl_share"] = (s.dep_seat_km_intl / s.dep_seat_km.where(s.dep_seat_km > 0)).clip(upper=1)
s["gdp_bn"] = np.exp(s.lngdp) / 1e9
s["arrivals_m"] = np.exp(s.ln_arrivals) / 1e6
s["pop_m"] = np.exp(s.lnpop) / 1e6
# WDI returns 0 (not missing) for Venezuela trade/GDP 1991-2011; treat as missing
print("trade_gdp == 0 obs:", int((s.trade_gdp == 0).sum()))
s["trade_gdp"] = s.trade_gdp.where(s.trade_gdp > 0)

rows = [
    ("A", "Aviation outcomes", None, None),
    ("A", "Aviation CO$_2$, bunker convention (Mt)", "co2_mt", 2),
    ("A", "International aviation CO$_2$ (Mt)", "co2_intl_mt", 2),
    ("A", "Domestic aviation CO$_2$ (Mt)", "co2_dom_mt", 2),
    ("A", "Aviation CO$_2$, territorial LTO rule (Mt)", "co2_lto_mt", 2),
    ("A", "Aviation CO$_2$, 50/50 rule (Mt)", "co2_5050_mt", 2),
    ("A", "Departing seat-km (billion)", "skm_bn", 2),
    ("A", "Departing flights (thousand)", "flights_k", 1),
    ("A", "Seats per flight", "gauge", 1),
    ("A", "Km per seat (average stage length)", "stage", 0),
    ("A", "CO$_2$ per seat-km (g)", "intensity_g", 1),
    ("A", "LTO share of CO$_2$", "lto_share", 3),
    ("A", "International share of seat-km", "intl_share", 3),
    ("B", "Connectivity (log GACI)", None, None),
    ("B", "ln GACI, capacity-weighted mean (headline)", "ln_gaci_cwm", 3),
    ("B", "ln GACI, sum", "lnG", 3),
    ("B", "ln GACI, maximum", "ln_gaci_max", 3),
    ("B", "ln GACI, unweighted mean", "ln_gaci_mean", 3),
    ("C", "Instrument and baseline controls", None, None),
    ("C", "Instrument $Z_{ct}=a_t\\times\\ln \\mathrm{airMA}_{c,1996}$", "feyrer_int", 3),
    ("C", "World aviation index $a_t$ (0--1)", "a_t", 3),
    ("C", "ln air market access, 1996", "ln_air96", 3),
    ("C", "ln sea market access", "ln_sea_ma", 3),
    ("C", "Population (million)", "pop_m", 2),
    ("D", "Development controls", None, None),
    ("D", "GDP (billion current US\\$)", "gdp_bn", 1),
    ("D", "Trade (\\% of GDP)", "trade_gdp", 1),
    ("D", "Urban population (\\% of total)", "urban", 1),
    ("D", "FDI net inflows (\\% of GDP)", "fdi", 1),
    ("D", "International tourist arrivals (million)", "arrivals_m", 2),
    ("E", "Non-aviation placebo outcomes (log Mt CO$_2$)", None, None),
    ("E", "Territorial fossil CO$_2$ excl.\\ domestic aviation (GCP/OWID)", "ln_co2_exav", 3),
    ("E", "Oil CO$_2$ excl.\\ domestic aviation (OWID)", "ln_oil_exav", 3),
    ("E", "Transport CO$_2$ excl.\\ domestic aviation (EDGAR)", "ln_ed_transp_exav", 3),
    ("E", "Power industry CO$_2$ (EDGAR)", "ln_ed_power", 3),
    ("E", "Buildings CO$_2$ (EDGAR)", "ln_ed_build", 3),
    ("E", "Industrial combustion CO$_2$ (EDGAR)", "ln_ed_indcomb", 3),
    ("E", "Coal CO$_2$ (OWID)", "ln_coal", 3),
    ("E", "Gas CO$_2$ (OWID)", "ln_gas", 3),
    ("E", "Cement CO$_2$ (OWID)", "ln_cement", 3),
    ("E", "Agriculture CO$_2$ (EDGAR)", "ln_ed_agri", 3),
    ("F", "Spatial exposures (row-normalised land contiguity)", None, None),
    ("F", "Neighbours' ln GACI, $W\\ln\\mathrm{GACI}$", "nbr_g_contig", 3),
    ("F", "Neighbours' instrument, $WZ$", "nbr_f_contig", 3),
    ("F", "Has a land neighbour (0/1)", "has_contig", 3),
]

def fmt(x, k):
    if 0 < abs(x) < 0.5 * 10 ** (-k):
        return "$<$" + ("1" if k == 0 else "0." + "0" * (k - 1) + "1")
    if k == 0:
        return f"{x:,.0f}"
    return f"{x:,.{k}f}".replace("-", "$-$")

out = []
letters = iter("ABCDEF")
for p, lab, v, k in rows:
    if v is None:
        out.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{Panel {next(letters)}. {lab}}}}} \\\\")
        continue
    x = s[v].replace([np.inf, -np.inf], np.nan)
    if v == "nbr_g_contig" or v == "nbr_f_contig":
        x = x.where(s.has_contig == 1)
    x = x.dropna()
    out.append(f"  {lab} & {len(x):,} & {fmt(x.mean(), k)} & {fmt(x.std(), k)} & {fmt(x.min(), k)} & {fmt(x.max(), k)} \\\\")
    print(f"{v:22s} N={len(x):5d} mean={x.mean():12.4f} sd={x.std():12.4f} min={x.min():12.4f} max={x.max():12.4f}")

open(H + r"\Junya_comments_20260925\sumstat_rows.tex", "w", encoding="utf-8").write("\n".join(out) + "\n")
