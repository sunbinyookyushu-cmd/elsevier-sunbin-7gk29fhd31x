# -*- coding: utf-8 -*-
"""
28_make_results_xlsx.py   (2026-09-03)
Collect the new result CSVs (LZ comment implementation) into one workbook,
CO2_results_summary_20260903_LZ.xlsx, with a README sheet mapping each sheet to
its script, manuscript display and one-line finding. The 08-26 final workbook is
left untouched.
"""
import os, sys
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "CO2_results_summary_20260903_LZ.xlsx")

sheets = [
    ("L2_decomp_main", "_feyrer_mechanism.csv", "co2_feyrer_mechanism.do / 18_decomp_table_fig.py", "Table decomp, Fig waterfall",
     "CO2 5.67 = flights 6.98 + gauge -0.30 (ns) + stage -0.60 + intensity -0.40; scale 6.07 (107%), efficiency offsets 7%"),
    ("L2_decomp_hetero", "_decomp_hetero.csv", "co2_decomp_hetero.do", "ED Table 4",
     "Low income 10.40 (all scale margins expand); middle 6.14; high 1.83 (flights up, gauge and stage down); intl 5.69 vs domestic -0.64 ns"),
    ("L3_hetero_totalCO2", "_feyrer_hetero_tot.csv", "co2_feyrer_hetero_tot.do", "ED Table 2, Fig hetero",
     "CORRECTED to total CO2 (08-26 numbers were international CO2): 10.40 / 6.14 / 1.83 (p=.06); Africa 6.36, Asia-Pacific 5.33, LatAm 2.92, Europe -0.61 ns"),
    ("L1_airport_hetero", "_airport_hetero.csv", "co2_airport_hetero.do", "ED Table 5",
     "Within-country elasticity 3.72; top-5% hubs 2.11 vs others 4.05 (interaction -2.56): systemic, not hub-driven; topology-only components agree"),
    ("L1_airport_concentration", "_airport_concentration.csv", "19_airport_concentration.py", "Table airport_conc, Fig airportconc",
     "Attributed emissions more concentrated than emissions: top 1% 45.8% vs 41.0%, top 5% 84.5% vs 77.6%, Gini .945 vs .916; led by new hubs (DXB, DOH, PVG, IST, ICN)"),
    ("L1_airport_top20", "_airport_top20.csv", "19_airport_concentration.py", "Fig airportconc B", "Top 20 airports by attributed Mt"),
    ("L1_airport_IV_pilot", "_airport_feyrer.csv", "20_airport_feyrer_iv.py / co2_airport_feyrer.do", "SI Table 2",
     "Airport Feyrer shifter has no first stage within countries (F 0.4-0.7): airport results stay descriptive"),
    ("L4_spill_bands", "_spill_bands.csv", "21_build_spillover_bands.py / co2_spill_bands.do", "Table spillover A, ED Table 6, ED Fig 4",
     "Joint IV contiguity: own 3.48 / neighbour 1.93 (SW F 66/124); no smooth distance decay; far band (>5000 km) negative; inverse-distance 7.45 fragile"),
    ("L4_spill_clustered", "_spill_supp.csv", "co2_spill_supp.do", "Table spillover A-B (bracketed s.e.)",
     "Contiguity joint IV with country clustering: own se 1.29 (t 2.7), neighbour se 0.69 (t 2.8); neighbour margins: seat-km 2.56, flights 1.22, stage 1.04, intensity -0.63"),
    ("L4_spill_cluster_AR", "_spill_cluster_ar.csv", "co2_spill_cluster_ar.do", "Table spillover A (middle block)",
     "Country-clustered: contiguity single-endogenous 2.05 (0.61), F 175, AR [0.9, 3.2]; with sub-region x year FE 2.07 (0.83); joint contig AR [0.1, 3.1]; knn5 and 500 km AR sets include zero"),
    ("L4_placebo_invdist", "_spill_placebo_perm.csv", "21_build_spillover_bands.py", "ED Table 6 C, ED Fig 5",
     "Inverse-distance RF t 3.81; permutation p 0.146"),
    ("L4_placebo_W_summary", "_spill_placebo_summary.csv", "21b_perm_contig.py", "ED Table 6 C, ED Fig 5", "Permutation p for contiguity and knn5 joint-IV neighbour coefficient"),
    ("L4_placebo_W_draws", "_spill_placebo_perm_W.csv", "21b_perm_contig.py", "ED Fig 5", "All permutation draws"),
    ("M_exclusion_suite", "_exclusion_suite.csv", "22_build_placebo_outcomes.py / co2_exclusion_suite.do", "ED Table 7, SI Table 1, ED Fig 6",
     "Total non-aviation CO2 RF 0.05 ns (aviation 0.73); sector series shift both ways; GDP/trade cycles collinear with a_t; air beats sea geography (RF .64 vs .08); zero-FS RF .10; controls 4.7-4.9; alt shifters 5.8-6.1; cluster se 1.12"),
    ("CL_main_temporal", "_allest_results_cl.csv", "co2_allestimators_cl.do", "Table 1 (clustered canonical)", "Country-clustered Table 1: 5.67 (1.12), KP F 18.4; intensity -0.40 (0.30) ns"),
    ("CL_measures6", "_measures6_cl.csv", "co2_extensions_cl.do", "Table 1 Panels C-E (clustered)", "GACI sum/max/mean panels, clustered"),
    ("CL_temporal", "_temporal_co2_cl.csv", "co2_extensions_cl.do", "ED Table 1 (clustered)", "1996-2007 5.61 (1.10) F 25; 2010-2023 exCOVID 3.01 (1.19) F 11; unrestricted post F 3.2"),
    ("CL_temporal_pre2008", "_temporal_pre2008_cl.csv", "co2_temporal_pre2008_cl.do", "ED Table 1 B", "clustered"),
    ("CL_temporal_excovid", "_temporal_excovid_cl.csv", "co2_temporal_excovid_cl.do", "ED Table 1 C", "clustered"),
    ("CL_mechanism", "_feyrer_mechanism_cl.csv", "co2_feyrer_mechanism_cl.do", "Table 2 (clustered)", "flights 6.98 (1.38); gauge/stage/intensity ns under clustering"),
    ("CL_decomp_hetero", "_decomp_hetero_cl.csv", "co2_decomp_hetero_cl.do", "ED Table 4 (clustered)", "within-tercile first stages weak (F 1.7-5.7)"),
    ("CL_hetero_totalCO2", "_feyrer_hetero_tot_cl.csv", "co2_feyrer_hetero_tot_cl.do", "ED Table 2 (clustered)", "10.40 (2.80)/6.14 (2.12)/1.83 (2.42); split F 2-16"),
    ("CL_exclusion_suite", "_exclusion_suite_cl.csv", "co2_exclusion_suite_cl.do", "ED Table 7, SI Table 1 (clustered)", "coal/cement remain significant; others ns; sea placebo air F 3.0; Hansen J 4.1 p .04; controls F 9.6-12"),
    ("CL_spill_bands", "_spill_bands_cl.csv", "co2_spill_bands_cl.do", "Table 4, ED Table 6 (clustered)", "joint contig own 3.48 (1.29)/nbr 1.93 (0.69); single contig 2.05 (0.61) F 175; far band -7.0 (6.4) ns"),
    ("CL_yifu_suite", "_yifu_suite_cl.csv", "co2_yifu_suite_cl.do", "ED Tables 8-9 (clustered)", "semi-log 4.09 (1.01); quintiles 8.5 (1.7)/8.5 (2.9)/3.3 (2.3)/unid./4.1 (2.5); interaction -3.99 (1.00) F 9"),
    ("CL_mediation", "_mediation_co2_cl.csv", "co2_extensions_cl.do", "ED Table 3 A (clustered)", "clustered Sobel"),
    ("M_world_series", "world_series.csv", "22_build_placebo_outcomes.py", "Methods", "Min-max scaled world cycles used in the horse race"),
    ("Y_funcform_gradient", "_yifu_suite.csv", "co2_yifu_suite.do", "ED Tables 8-9, Fig gradient",
     "Semi-log 4.09/unit (elasticity 4.44 at mean), level 4.25 Mt/unit; tercile semi-log 10.3/4.6/1.1; quintiles 8.5/8.5/3.3/(unid.)/4.1; continuous p10 7.1, p50 6.0, p90 4.1"),
    ("Y_attribution_sens", "_attribution_sensitivity.csv", "29_yifu_gradient_attribution.py", "ED Table 10",
     "Attribution 294-356 Mt (35-43%) across elasticity rules; common 5.67 is the upper end"),
    ("Y_attribution_country", "_attribution_hetero.csv", "29_yifu_gradient_attribution.py", "ED Table 10", "Country-level elasticities under each rule"),
    ("Y_accident_iv", "_asn_iv_results.csv", "co2_measures_asn.do", "SI Table 3", "ASN accident IV weak (F 1-4), 2SLS 6.2 (2.4); Hansen p 0.70/0.95 with Feyrer; joint 5.4"),
]
readme = []
with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    for name, fn, script, display, finding in sheets:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            readme.append({"sheet": name, "source_csv": fn, "script": script, "manuscript_display": display, "finding": finding, "status": "MISSING"})
            continue
        df = pd.read_csv(p)
        df.to_excel(xw, sheet_name=name[:31], index=False)
        readme.append({"sheet": name, "source_csv": fn, "script": script, "manuscript_display": display, "finding": finding, "status": f"{len(df)} rows"})
    pd.DataFrame(readme).to_excel(xw, sheet_name="README", index=False)
    # move README first
    wb = xw.book
    wb.move_sheet("README", offset=-(len(wb.sheetnames) - 1))
print("wrote", OUT)
for r in readme:
    print(f"  {r['sheet']:26s} {r['status']}")
print("DONE_28")
