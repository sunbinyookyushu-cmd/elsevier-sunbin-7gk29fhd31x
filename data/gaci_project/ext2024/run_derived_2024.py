# -*- coding: utf-8 -*-
"""
run_derived_2024.py -- patch the paper's derived-output scripts (copied into ext2024/) to the 1996-2024
sample and the Stata-confirmed 2024 elasticities, then run them. Produces aggregates, maps, figures and
the country appendix table used to update main.tex.

Stata 2024 (ivreghdfe, robust):  cwm  int 1.208 (0.593)  vol 2.126 (0.703)  gdp 0.919 (0.624)  KP F 21.9
                                 max  int 0.897 (0.423)  vol 1.580 (0.503)  gdp 0.683 (0.467)  KP F 33.0
                                 sum  int 0.635 (0.342)  vol 1.119 (0.404)  gdp 0.483 (0.323)  KP F 11.0
"""
import re, subprocess, sys, json, pathlib, os
E = pathlib.Path(__file__).parent; os.chdir(E)
PY = sys.executable
stats = json.load(open("_ext_sample_stats.json"))

def patch(fn, subs, regex=False):
    p = E / fn; s = p.read_text(encoding="utf-8"); n_tot = 0
    for old, new in subs:
        if regex:
            s, n = re.subn(old, new, s)
        else:
            n = s.count(old); s = s.replace(old, new)
        n_tot += n
        if n == 0: print(f"  !! no match in {fn}: {old[:60]}")
    p.write_text(s, encoding="utf-8", newline="\n"); print(f"patched {fn}: {n_tot} replacements")

def run(fn, *args):
    print(f"\n>>> {fn}"); r = subprocess.run([PY, fn, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout[-2500:]);
    if r.returncode: print("STDERR:", r.stderr[-2000:])
    return r.returncode

BETA_MAP = [("1.302", "1.208"), ("2.303", "2.126"), ("1.001", "0.919"),
            ("0.662", "0.593"), ("0.776", "0.703"), ("0.680", "0.624"),
            ("0.966", "0.897"), ("1.709", "1.580"), ("0.743", "0.683"),
            ("0.659", "0.635"), ("1.166", "1.119"), ("0.507", "0.483")]

# 1) compute_aggregates.py -----------------------------------------------------------------
patch("compute_aggregates.py", [
    ("B_VOL = 2.303", "B_VOL = 2.126"), ("B_INT = 1.302", "B_INT = 1.208"), ("B_GDP = 1.001", "B_GDP = 0.919"),
    ("B_PC  = 0.514", "B_PC  = %.3f" % stats["b_pc"][0]),
    ("B_INT_SUM = 0.659 ; B_GDP_SUM = 0.507", "B_INT_SUM = 0.635 ; B_GDP_SUM = 0.483"),
    ("samp = p[(p.y >= 1996) & (p.y <= 2023)]", "samp = p[(p.y >= 1996) & (p.y <= 2024)]"),
    ("ENDYR = 2023", "ENDYR = 2024"),
    ("g19 = val_at('lnG', 2023)", "g19 = val_at('lnG', 2024)"),
    ("'ln(GACI sum), 2023'", "'ln(GACI sum), 2024'"), ("by country, 2023'", "by country, 2024'"),
])
run("compute_aggregates.py")

# 2) measures contribution + maps ----------------------------------------------------------
patch("compute_measures_contribution.py", [
    ("ENDYR, STARTYR = 2023, 1996", "ENDYR, STARTYR = 2024, 1996"),
    ("b_int=1.302, b_vol=2.303, b_gdp=1.001, kpf=18.0", "b_int=1.208, b_vol=2.126, b_gdp=0.919, kpf=21.9"),
    ("b_int=0.966, b_vol=1.709, b_gdp=0.743, kpf=27.4", "b_int=0.897, b_vol=1.580, b_gdp=0.683, kpf=33.0"),
    ("b_int=0.659, b_vol=1.166, b_gdp=0.507, kpf=9.7", "b_int=0.635, b_vol=1.119, b_gdp=0.483, kpf=11.0"),
])
run("compute_measures_contribution.py")
patch("build_measures_maps.py", [("ENDYR, STARTYR = 2023, 1996", "ENDYR, STARTYR = 2024, 1996"),
                                 ("rightarrow$2023", "rightarrow$2024"), ("contribution, 2023 (US", "contribution, 2024 (US")])
run("build_measures_maps.py")

# 3) COVID shock ---------------------------------------------------------------------------
patch("compute_covid_3measure.py", [
    ("'cwm': dict(col='ln_gaci_cwm', b_int=1.302, b_gdp=1.001)", "'cwm': dict(col='ln_gaci_cwm', b_int=1.208, b_gdp=0.919)"),
    ("'max': dict(col='ln_gaci_max', b_int=0.966, b_gdp=0.743)", "'max': dict(col='ln_gaci_max', b_int=0.897, b_gdp=0.683)"),
    ("'sum': dict(col='lnG',         b_int=0.659, b_gdp=0.507)", "'sum': dict(col='lnG',         b_int=0.635, b_gdp=0.483)"),
])
run("compute_covid_3measure.py")
run("build_covid_maps.py")

# 4) country appendix ----------------------------------------------------------------------
patch("build_country_estimates.py", [
    ("BETA = {'vol': (2.303, 0.776), 'int': (1.302, 0.662),", "BETA = {'vol': (2.126, 0.703), 'int': (1.208, 0.593),"),
    ("1996--2023", "1996--2024"), ("1996->2023", "1996->2024"),
])
patch("build_country_estimates.py", [(r"'gdp': \(1\.001, 0\.680\)", "'gdp': (0.919, 0.624)")], regex=True)
run("build_country_estimates.py")

# 5) continent trend -----------------------------------------------------------------------
patch("build_continent_trend.py", [("BETA = 1.302", "BETA = 1.208"), ("(p.y <= 2023)", "(p.y <= 2024)"),
                                   ("ax.set_xlim(1996, 2024)", "ax.set_xlim(1996, 2025)"),
                                   ("trend['y'] == 2023", "trend['y'] == 2024"), ("1996-2023", "1996-2024")])
run("build_continent_trend.py")

# 6) heterogeneity quartile figure (Stata 2024 het estimates; corr from the 2SLS V matrix) -----
patch("build_hetero_quartile_fig.py", [
    ("dict(b_main=1.254132, se_main=0.717470, b_int=-0.242952, se_int=0.122311, corr=-0.866)",
     "dict(b_main=1.138607, se_main=0.643988, b_int=-0.214013, se_int=0.108323, corr=%.3f)" % stats["corr_inc"]),
    ("dict(b_main=2.259651, se_main=1.161177, b_int=-1.481524, se_int=0.622443, corr=-0.797)",
     "dict(b_main=2.014492, se_main=0.986082, b_int=-1.334897, se_int=0.523936, corr=%.3f)" % stats["corr_con"]),
])
run("build_hetero_quartile_fig.py")

# 7) RF quintile figure, base map, method figure, CI ranges, temporal sweep -----------------
run("build_rf_quintile_fig.py")
patch("build_base_map_v2.py", [("2023", "2024")])
run("build_base_map_v2.py")
run("build_method_fig_v2.py")
patch("compute_aggregates_ci.py", BETA_MAP + [("ENDYR = 2023", "ENDYR = 2024")])
run("compute_aggregates_ci.py")
src = (E.parent / "_sweep_temporal_split.py").read_text(encoding="utf-8")
src = re.sub(r'CSV = r"[^"]*"', 'CSV = r"%s"' % str(E / "gaci_panel_3iv.csv").replace("\\", "\\\\"), src)
(E / "_sweep_temporal_split.py").write_text(src, encoding="utf-8", newline="\n")
run("_sweep_temporal_split.py")
print("\nDERIVED DONE")
