# -*- coding: utf-8 -*-
"""Conley (spatial x temporal HAC) standard errors for the ticket-tax DiD (user 2026-10-03).
Monthly: stack_eff.dta (effective-date stacks +-36 months, 9 European events incl. NLD; the main announcement-donut
  stack_month.dta is not in the cloud copy) -> ln seats, ln CO2, ln CO2/seat-km on tp (treated x post), bp (border x post),
  FE airport x calendar month x event (fe_u) and month x event (fe_t); post window = first 12 effective months.
Annual: stack_year.dta, European events ex NLD (stk 1-8), k = -3..0 -> ln GACI, destinations, eigenvector, CO2.
Estimator: two-way demeaning (alternating projections) then OLS; SEs: (i) country cluster, (ii) HC1,
  (iii) Conley with a uniform spatial kernel within D km and a Bartlett time kernel with lag L
  (D = 300, 500, 1000 km; L = 12 months / 2 years). Repeated airport-periods across stacks are summed within the
  calendar period before forming the HAC, so the same observation appearing in two stacks is treated as perfectly
  correlated. Coordinates: ../../processed/airport_country_map.csv (session repo) or ../hub_panel.csv.
Output: _res_tax_conley.csv
"""
import numpy as np, pandas as pd, pathlib, warnings
warnings.filterwarnings("ignore")
HERE = pathlib.Path(__file__).resolve().parent
coords = pd.read_csv(HERE.parents[2]/"data/processed/airport_country_map.csv")[["Airport","lat","lon"]].rename(columns={"Airport":"airport"}).dropna()

def demean(df, cols, fes, tol=1e-9, maxit=500):
    X = df[cols].to_numpy(float).copy()
    g = [df[f].to_numpy() for f in fes]
    for _ in range(maxit):
        X0 = X.copy()
        for gi in g:
            m = pd.DataFrame(X).groupby(gi).transform("mean").to_numpy()
            X = X - m
        if np.abs(X - X0).max() < tol: break
    return X

def conley_meat(U, tcode, acode, D_km, L, K):
    """U: n x k scores (x_tilde * e); tcode: integer period; acode: airport index into K; K: N x N spatial kernel."""
    k = U.shape[1]; periods = np.sort(np.unique(tcode)); N = K.shape[0]
    Ut = {}
    for t in periods:
        m = tcode == t
        M = np.zeros((N, k)); np.add.at(M, acode[m], U[m]); Ut[t] = M
    KU = {t: K @ Ut[t] for t in periods}
    meat = np.zeros((k, k))
    for t in periods:
        for s in periods:
            lag = abs(int(t) - int(s))
            if lag > L: continue
            w = 1 - lag/(L+1)
            meat += w * Ut[t].T @ KU[s]
    return meat

def run(df, y, xs, fes, label, time_col, L, cutoffs=(300, 500, 1000)):
    d = df.dropna(subset=[y]+xs).copy()
    d = d.merge(coords, on="airport", how="inner")
    Z = demean(d, [y]+xs, fes); yt, Xt = Z[:,0], Z[:,1:]
    XtX_inv = np.linalg.inv(Xt.T @ Xt); b = XtX_inv @ Xt.T @ yt; e = yt - Xt @ b
    n, k = Xt.shape; U = Xt * e[:,None]
    rows = []
    # HC1
    V = XtX_inv @ (U.T @ U) @ XtX_inv * n/(n-k)
    rows.append(("HC1", np.sqrt(np.diag(V))))
    # country cluster
    cl = pd.factorize(d.iso3)[0]; G = cl.max()+1
    S = np.zeros((G,k)); np.add.at(S, cl, U); V = XtX_inv @ (S.T @ S) @ XtX_inv * (G/(G-1))*((n-1)/(n-k))
    rows.append((f"cluster country (G={G})", np.sqrt(np.diag(V))))
    # Conley
    ap = d.drop_duplicates("airport")[["airport","lat","lon"]].reset_index(drop=True)
    acode = pd.Series(range(len(ap)), index=ap.airport).reindex(d.airport).to_numpy()
    la, lo = np.radians(ap.lat.to_numpy()), np.radians(ap.lon.to_numpy())
    dist = 2*6371*np.arcsin(np.sqrt(np.sin((la[:,None]-la[None,:])/2)**2 + np.cos(la[:,None])*np.cos(la[None,:])*np.sin((lo[:,None]-lo[None,:])/2)**2))
    tcode = d[time_col].to_numpy().astype(int)
    for Dk in cutoffs:
        K = (dist <= Dk).astype(float)
        V = XtX_inv @ conley_meat(U, tcode, acode, Dk, L, K) @ XtX_inv
        rows.append((f"Conley {Dk} km, lag {L}", np.sqrt(np.diag(V))))
    out = []
    for name, se in rows:
        for j, x in enumerate(xs):
            out.append({"sample": label, "outcome": y, "term": x, "b": b[j], "se_type": name, "se": se[j], "n": n, "airports": len(ap)})
    return pd.DataFrame(out)

res = []
# ---- monthly (effective-date stacks) ----
M = pd.read_stata(HERE/"stata_paper/stack_eff.dta")
M = M[(M.relE >= -36) & (M.relE <= 11)].copy()          # pre 36 months, first 12 effective months
M["tp"] = M.treat*M.post; M["bp"] = M.border*M.post
for y in ["ln_seats", "ln_co2", "ln_int"]:
    res.append(run(M[M.stk != 0], y, ["tp","bp"], ["fe_u","fe_t"], "monthly, 8 events ex NLD, eff-date +-36/12", "t", 12))
res.append(run(M, "ln_seats", ["tp","bp"], ["fe_u","fe_t"], "monthly, 9 events incl NLD", "t", 12))
# by size (monthly, seats and CO2)
M["tp_small"], M["tp_mid"], M["tp_large"] = M.tp*M.sz_small, M.tp*M.sz_mid, M.tp*M.sz_large
for y in ["ln_seats","ln_co2"]:
    res.append(run(M[M.stk != 0], y, ["tp_small","tp_mid","tp_large","bp"], ["fe_u","fe_t"], "monthly by size, 8 events", "t", 12))
# ---- annual (main annual stacks) ----
Y = pd.read_stata(HERE/"stata_paper/stack_year.dta")
CODED = {"DEU","AUT","NLD","BEL","LUX","FRA","ITA","IRL","GBR","CHE","SWE","NOR","DNK","FIN","ISL","PRT","ESP","GRC","HUN","HRV","MLT"}
Y = Y[(Y.eur == 1) & (Y.stk.between(1, 8)) & (Y.k <= 0) & (Y.iso3.isin(CODED) | (Y.treat == 1) | (Y.border == 1)) & (Y.iso3 != "ITA")].copy()   # European controls only, as in 01_main.do
Y["tp"] = Y.treat*Y.post; Y["bp"] = Y.border*Y.post
for y in ["ln_gaci","ln_deg","ln_eigen","ln_co2"]:
    res.append(run(Y, y, ["tp","bp"], ["fe_u","fe_t"], "annual, 8 events, k=-3..0", "year", 2))
R = pd.concat(res, ignore_index=True)
R["t"] = R.b/R.se; R["p"] = 2*(1-__import__("scipy").stats.norm.cdf(np.abs(R.t)))
R.to_csv(HERE/"_res_tax_conley.csv", index=False)
pd.set_option("display.width", 220)
for (s, y), g in R.groupby(["sample","outcome"], sort=False):
    print(f"\n=== {s} | {y} | N={g.n.iloc[0]:,} airports={g.airports.iloc[0]}")
    piv = g[g.term.str.startswith("tp")].pivot(index="term", columns="se_type", values="se")
    bb = g[g.term.str.startswith("tp")].drop_duplicates("term").set_index("term").b
    piv.insert(0, "coef", bb); print(piv.round(4).to_string())
