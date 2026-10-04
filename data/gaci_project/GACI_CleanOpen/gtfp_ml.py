"""
Green TFP via Global Malmquist-Luenberger (Oh 2010, J. Productivity Analysis) directional distance functions.
Inputs : capital stock rnna (PWT 11, 2021 USD), employment emp, human-capital-adjusted labour emp*hc
Good   : real GDP rgdpna (PWT 11)
Bad    : CO2 (OWID, Mt)  [variant 2: CO2 and SO2 (CEDS kt)]
Frontier: global (all countries, all years pooled) -> no infeasibility, circular.
DDF:   D(x,y,b; g=(y,-b)) = max beta  s.t.  sum_j l_j y_j >= (1+beta) y_k,  sum_j l_j b_j = (1-beta) b_k,  sum_j l_j x_j <= x_k, l>=0  (CRS)
GML_{t,t+1} = (1+D_t)/(1+D_{t+1});  cumulative GTFP index normalised to 1 in first year; ln_gtfp = log(cum index).
Conventional TFP (no bad output): same global DEA, output-oriented Shephard distance (Farrell efficiency), GM index.
Output: gtfp_country_year.csv  (c, y, ddf_co2, ddf_co2so2, eff_tfp, gml_co2, gml_co2so2, gm_tfp, ln_gtfp_co2, ln_gtfp_co2so2, ln_tfp_dea)
"""
import numpy as np, pandas as pd, pathlib, time
from scipy.optimize import linprog
here = pathlib.Path(__file__).resolve().parent
p = pd.read_csv(here/"pwt_country_year.csv")
o = pd.read_csv(here.parent/"GACI_CO2/data_external/owid-co2-data.csv", low_memory=False).rename(columns={"iso_code":"c","year":"y"})[["c","y","co2"]]
pol = pd.read_csv(here/"pollution_country_year.csv").rename(columns={"iso3":"c","year":"y"})[["c","y","so2_total"]]
d = p.merge(o, on=["c","y"]).merge(pol, on=["c","y"], how="left")
d = d[d.y.between(1995, 2023)].dropna(subset=["rnna","emp","hc","rgdpna","co2"]).query("rnna>0 and emp>0 and rgdpna>0 and co2>0").copy()
d["lab"] = d.emp*d.hc
# balanced-ish: keep countries with >= 20 years
cnt = d.groupby("c").size(); d = d[d.c.isin(cnt[cnt>=20].index)].sort_values(["c","y"]).reset_index(drop=True)
print("DMUs:", len(d), "countries:", d.c.nunique(), "years:", d.y.min(), d.y.max())
# scale to means
X = d[["rnna","lab"]].values; X = X/X.mean(0)
Y = d[["rgdpna"]].values; Y = Y/Y.mean(0)
B1 = d[["co2"]].values; B1 = B1/B1.mean(0)
has_so2 = d.so2_total.notna().values & (d.so2_total.fillna(0).values > 0)
B2 = np.column_stack([d.co2.values/d.co2.mean(), d.so2_total.fillna(np.nan).values/np.nanmean(d.so2_total.values)])

def ddf(k, X, Y, B, idx):
    """directional distance of DMU k vs frontier formed by rows idx (global). returns beta."""
    n = len(idx); xk, yk, bk = X[k], Y[k], B[k]
    # variables: lambdas (n) + beta
    c = np.zeros(n+1); c[-1] = -1.0
    A_ub = []; b_ub = []
    for i in range(Y.shape[1]):   # -(sum l y) + beta*y_k <= -y_k
        row = np.zeros(n+1); row[:n] = -Y[idx, i]; row[-1] = yk[i]; A_ub.append(row); b_ub.append(-yk[i])
    for i in range(X.shape[1]):   # sum l x <= x_k
        row = np.zeros(n+1); row[:n] = X[idx, i]; A_ub.append(row); b_ub.append(xk[i])
    A_eq = []; b_eq = []
    for i in range(B.shape[1]):   # sum l b + beta*b_k = b_k
        row = np.zeros(n+1); row[:n] = B[idx, i]; row[-1] = bk[i]; A_eq.append(row); b_eq.append(bk[i])
    r = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                bounds=[(0, None)]*n + [(0, None)], method="highs")
    return r.x[-1] if r.status == 0 else np.nan

def farrell(k, X, Y, idx):
    """output-oriented Farrell: max phi s.t. sum l y >= phi y_k, sum l x <= x_k"""
    n = len(idx); xk, yk = X[k], Y[k]
    c = np.zeros(n+1); c[-1] = -1.0
    A_ub = []; b_ub = []
    for i in range(Y.shape[1]):
        row = np.zeros(n+1); row[:n] = -Y[idx, i]; row[-1] = yk[i]; A_ub.append(row); b_ub.append(0.0)
    for i in range(X.shape[1]):
        row = np.zeros(n+1); row[:n] = X[idx, i]; A_ub.append(row); b_ub.append(xk[i])
    r = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(0, None)]*n + [(0, None)], method="highs")
    return r.x[-1] if r.status == 0 else np.nan

t0 = time.time()
all_idx = np.arange(len(d))
so2_idx = np.where(has_so2)[0]
d["ddf_co2"] = [ddf(k, X, Y, B1, all_idx) for k in range(len(d))]
print("ddf_co2 done", round(time.time()-t0), "s")
d["eff_tfp"] = [farrell(k, X, Y, all_idx) for k in range(len(d))]
print("farrell done", round(time.time()-t0), "s")
d["ddf_co2so2"] = np.nan
d.loc[has_so2, "ddf_co2so2"] = [ddf(k, X, Y, B2, so2_idx) for k in so2_idx]
print("ddf_co2so2 done", round(time.time()-t0), "s")

# indices: global ML = (1+D_t)/(1+D_{t+1}); cumulative level relative to each country's first year
def cum_index(df, col, kind):
    out = {}
    for c, g in df.groupby("c"):
        g = g.sort_values("y")
        if kind == "ddf":
            lvl = 1.0/(1.0 + g[col].values)        # higher = closer to frontier
        else:
            lvl = 1.0/g[col].values                # Farrell efficiency 1/phi in (0,1]
        out[c] = pd.Series(lvl/lvl[0], index=g.index)
    return pd.concat(out.values())
d["gtfp_co2_lvl"] = cum_index(d, "ddf_co2", "ddf")
d["gtfp_co2so2_lvl"] = cum_index(d.dropna(subset=["ddf_co2so2"]), "ddf_co2so2", "ddf")
d["tfp_dea_lvl"] = cum_index(d, "eff_tfp", "far")
d["ln_gtfp_co2"] = np.log(d.gtfp_co2_lvl); d["ln_gtfp_co2so2"] = np.log(d.gtfp_co2so2_lvl); d["ln_tfp_dea"] = np.log(d.tfp_dea_lvl)
# also the raw (not-normalised) distance-based levels: ln(1/(1+D)) comparable across countries
d["ln_geff_co2"] = -np.log1p(d.ddf_co2); d["ln_geff_co2so2"] = -np.log1p(d.ddf_co2so2); d["ln_eff_tfp"] = -np.log(d.eff_tfp)
d["gml_co2"] = d.groupby("c").gtfp_co2_lvl.pct_change()+1
d["gm_tfp"] = d.groupby("c").tfp_dea_lvl.pct_change()+1
cols = ["c","y","ddf_co2","ddf_co2so2","eff_tfp","gml_co2","gm_tfp","ln_gtfp_co2","ln_gtfp_co2so2","ln_tfp_dea","ln_geff_co2","ln_geff_co2so2","ln_eff_tfp"]
d[cols].to_csv(here/"gtfp_country_year.csv", index=False)
print(d[cols].describe().T[["count","mean","std","min","max"]])
print("corr ln_gtfp_co2 vs PWT rtfpna growth:")
dd = d.dropna(subset=["rtfpna"]).copy()
dd["dl_tfp_pwt"] = dd.groupby("c").rtfpna.transform(lambda s: np.log(s).diff()); dd["dl_gtfp"] = dd.groupby("c").ln_gtfp_co2.diff(); dd["dl_tfpdea"] = dd.groupby("c").ln_tfp_dea.diff()
print(dd[["dl_tfp_pwt","dl_gtfp","dl_tfpdea"]].corr())
