# -*- coding: utf-8 -*-
"""Build COMPARE_2023_vs_2024.md from _reest_*.json and _aggregates_compare.json."""
import json
A = json.load(open('_reest_A_paper.json')); B = json.load(open('_reest_B_rebuilt23.json')); C = json.load(open('_reest_C_ext24.json'))
G = json.load(open('_aggregates_compare.json'))
def s(v): return f"{v[0]:.3f} ({v[1]:.3f}){'***' if v[2] < .01 else '**' if v[2] < .05 else '*' if v[2] < .10 else ''}"
L = []; w = L.append
w("# GACI: 1996-2023 (paper) vs 1996-2024 (extended) re-estimation, 2026-09-02\n")
w("Python re-estimation (two-way FE 2SLS, HC1 robust). Column A reproduces every published number to 3 dp (SEs about 2% below ivreghdfe because of the FE dof adjustment). Stata do-files with paths pointed at this folder are in `do_ext2024/` for the authoritative rerun.\n")
w("Samples: **A** = paper panel (4,643 obs, 184 countries). **B** = rebuilt panel, y<=2023 (4,661; +16 land-backfilled rows BEL/LUX/SDN 1996-2011). **C** = rebuilt panel 1996-2024 (4,816; 185 countries; +155 country-years in 2024; heritage endowment as of 2024, which changes BIH/BRA/CHN/FRA/GBR only; a frozen-2023 endowment gives 1.208 (0.582), identical).\n")
w("Data changes needed for 2024: WDI land area carried forward (no 2024 value published), UNWTO 2024 arrivals ratio 0.99 of 2019 added to the tourism shifter, BACI 2024 processed. Trade data for 2024 cover 155 countries (166 in 2023).\n")
w("## Table 1 main (IV)\n\n| outcome | A paper | B rebuilt<=2023 | C 1996-2024 |\n|---|---|---|---|")
for yv, lab in [("g_int", "cwm: openness"), ("g_vol", "cwm: volume"), ("g_gdp", "cwm: GDP")]:
    w(f"| {lab} | {s(A['T1_main']['ln_gaci_cwm']['iv_'+yv]['ln_gaci_cwm'])} | {s(B['T1_main']['ln_gaci_cwm']['iv_'+yv]['ln_gaci_cwm'])} | {s(C['T1_main']['ln_gaci_cwm']['iv_'+yv]['ln_gaci_cwm'])} |")
w(f"| cwm KP F / N | {A['T1_main']['ln_gaci_cwm']['iv_g_int']['F']:.1f} / {A['T1_main']['ln_gaci_cwm']['iv_g_int']['N']} | {B['T1_main']['ln_gaci_cwm']['iv_g_int']['F']:.1f} / {B['T1_main']['ln_gaci_cwm']['iv_g_int']['N']} | {C['T1_main']['ln_gaci_cwm']['iv_g_int']['F']:.1f} / {C['T1_main']['ln_gaci_cwm']['iv_g_int']['N']} |")
for yv, lab in [("g_int", "sum: openness"), ("g_vol", "sum: volume"), ("g_gdp", "sum: GDP")]:
    w(f"| {lab} | {s(A['T1_main']['lnG']['iv_'+yv]['lnG'])} | {s(B['T1_main']['lnG']['iv_'+yv]['lnG'])} | {s(C['T1_main']['lnG']['iv_'+yv]['lnG'])} |")
w(f"| sum KP F | {A['T1_main']['lnG']['iv_g_int']['F']:.1f} | {B['T1_main']['lnG']['iv_g_int']['F']:.1f} | {C['T1_main']['lnG']['iv_g_int']['F']:.1f} |")
for yv, lab in [("g_int", "max: openness"), ("g_vol", "max: volume"), ("g_gdp", "max: GDP")]:
    w(f"| {lab} | {s(A['T1_main']['ln_gaci_max']['iv_'+yv]['ln_gaci_max'])} | {s(B['T1_main']['ln_gaci_max']['iv_'+yv]['ln_gaci_max'])} | {s(C['T1_main']['ln_gaci_max']['iv_'+yv]['ln_gaci_max'])} |")
w("\n## Table 2 heterogeneity (interaction IV; main at mean / x moderator)\n\n| spec | A | C |\n|---|---|---|")
for k in A['T2_het']:
    if k.endswith('_rem'): continue
    a = A['T2_het'][k]; c = C['T2_het'][k]; m = [x for x in a if x.startswith('cwm_')][0]
    w(f"| {k} | {s(a['ln_gaci_cwm'])} / {s(a[m])}, SW-F {a['F']:.1f} | {s(c['ln_gaci_cwm'])} / {s(c[m])}, SW-F {c['F']:.1f} |")
w("\n## Table 3 temporal (x post-2010)\n\n| outcome | A main / x post | C main / x post |\n|---|---|---|")
for yv in ["g_int", "g_vol", "g_gdp"]:
    a = A['T3_temporal']['int_'+yv]; c = C['T3_temporal']['int_'+yv]
    w(f"| {yv} | {s(a['ln_gaci_cwm'])} / {s(a['cwm_post'])} | {s(c['ln_gaci_cwm'])} / {s(c['cwm_post'])} |")
w(f"| first-stage F pre / post 2010 | {A['T3_temporal']['pre_g_int']['F']:.2f} / {A['T3_temporal']['post_g_int']['F']:.1f} | {C['T3_temporal']['pre_g_int']['F']:.2f} / {C['T3_temporal']['post_g_int']['F']:.1f} |")
w("\n## Table 4 mechanism outcomes (full sample / drop 2020-21)\n\n| outcome | A full | C full | A drop | C drop |\n|---|---|---|---|---|")
for yv in ["r_vw", "sh_hivw", "r_bec", "sh_bec", "xr_vw", "xsh_hivw", "lntot"]:
    w(f"| {yv} | {s(A['T4_mech'][yv+'_sfull']['ln_gaci_cwm'])} | {s(C['T4_mech'][yv+'_sfull']['ln_gaci_cwm'])} | {s(A['T4_mech'][yv+'_sdrop']['ln_gaci_cwm'])} | {s(C['T4_mech'][yv+'_sdrop']['ln_gaci_cwm'])} |")
w(f"| KP F | {A['T4_mech']['r_vw_sfull']['F']:.1f} | {C['T4_mech']['r_vw_sfull']['F']:.1f} | {A['T4_mech']['r_vw_sdrop']['F']:.1f} | {C['T4_mech']['r_vw_sdrop']['F']:.1f} |")
w("\n## Table 5 mediation, openness, full sample (6 columns)\n\n| column | A | C |\n|---|---|---|")
for k, lab in [("total", "(1) total"), ("M1out", "(2) M1 = ln(interm/consum) as outcome"), ("plusM1", "(3) + M1"), ("M2out", "(4) M2 = ln(hiVW/loVW) as outcome"), ("plusM2", "(5) + M2"), ("plusBoth", "(6) + both")]:
    w(f"| {lab} | {s(A['T5_mediation'][f'g_int_{k}_sfull']['ln_gaci_cwm'])} | {s(C['T5_mediation'][f'g_int_{k}_sfull']['ln_gaci_cwm'])} |")
w("\n## Table 6 controls sensitivity (openness)\n\n| controls | A | C |\n|---|---|---|")
for k in A['T6_controls']:
    w(f"| {k} | {s(A['T6_controls'][k]['ln_gaci_cwm'])} F {A['T6_controls'][k]['F']:.1f} | {s(C['T6_controls'][k]['ln_gaci_cwm'])} F {C['T6_controls'][k]['F']:.1f} |")
w("\n## Table 7 validity battery (openness / volume)\n\n| test | A | C |\n|---|---|---|")
for k in A['T7_validity']:
    if not (k.endswith('g_int') or k.endswith('g_vol')): continue
    a = A['T7_validity'][k]; c = C['T7_validity'][k]
    ja = f", J p={a['J'][2]:.3f}" if 'J' in a else ""; jc = f", J p={c['J'][2]:.3f}" if 'J' in c else ""
    w(f"| {k} | {s(a['ln_gaci_cwm'])} F {a['F']:.1f}{ja} | {s(c['ln_gaci_cwm'])} F {c['F']:.1f}{jc} |")
w("\n## Table 8 plausibly exogenous (lower bounds at gamma = 10/20/30% of RF; f*)\n\n| outcome | A | C |\n|---|---|---|")
for yv in ["g_int", "g_vol", "g_gdp"]:
    a = A['T8_conley'][yv]; c = C['T8_conley'][yv]
    w(f"| {yv} | lb {a['lb10']:.3f} / {a['lb20']:.3f} / {a['lb30']:.3f}, f* {a['fstar']:.2f} | lb {c['lb10']:.3f} / {c['lb20']:.3f} / {c['lb30']:.3f}, f* {c['fstar']:.2f} |")
w("\n## Reduced form by quintile (RF coefficient of tourism_int on openness)\n\n| moderator | A q1..q5 | C q1..q5 |\n|---|---|---|")
for m in ["inc", "con"]:
    w(f"| {m} | " + ", ".join(f"{A['T9_rf_quintile'][m][f'q{i}'][0]:.3f}" for i in range(1, 6)) + " | " + ", ".join(f"{C['T9_rf_quintile'][m][f'q{i}'][0]:.3f}" for i in range(1, 6)) + " |")
w("\n## Aggregate contribution (openness channel)\n\n| | paper 2023 (beta 1.302) | ext 2024 (beta 1.208) | ext 2024 (beta 1.302) |\n|---|---|---|---|")
for key, lab, fmt in [("gain_T", "attributable trade, $T", "{:.2f}"), ("pct_trade", "% of world trade", "{:.1f}"), ("pct_gdp", "% of world GDP", "{:.1f}"), ("world_trade_T", "world goods trade, $T", "{:.1f}"), ("open_now", "world openness now, %", "{:.1f}"), ("open_cf", "counterfactual openness, %", "{:.1f}"), ("chn_share", "China share of gain, %", "{:.0f}")]:
    w(f"| {lab} | {fmt.format(G['paper23'][key])} | {fmt.format(G['ext24'][key])} | {fmt.format(G['ext24_oldbeta'][key])} |")
w("\nNote: the 2024 aggregate is larger despite the smaller elasticity because hub quality kept recovering in 2024 (larger 1996-2024 change in ln GACI_cwm) and the base moves to 2024 trade levels.\n")
open('COMPARE_2023_vs_2024.md', 'w', encoding='utf-8').write("\n".join(L)); print("written", len(L), "lines")
