# -*- coding: utf-8 -*-
"""
_make_response_results_20260903.py
Point-by-point responses with results (after implementation on 2026-09-03):
  Response_LZ_results_20260903.docx   (Prof. Zheng, 4 comments + 5-layer structure)
  Response_Yifu_results_20260903.docx (Yifu, 4 comments)
Both end with a shared 'Open issues and fragile results' section.
"""
import os, sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

def new_doc(title, sub):
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2.0)
    p = doc.add_paragraph(); r = p.add_run(title); r.bold = True; r.font.size = Pt(15)
    p = doc.add_paragraph(sub); p.runs[0].italic = True
    return doc

def heading(doc, text):
    p = doc.add_paragraph(); r = p.add_run(text); r.bold = True; r.font.size = Pt(12.5); r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(4)

def comment_box(doc, text):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; c.paragraphs[0].text = ""
    r = c.paragraphs[0].add_run("Comment: "); r.bold = True
    first = True
    for line in text.strip().split("\n"):
        if first:
            c.paragraphs[0].add_run(line).italic = True; first = False
        else:
            p = c.add_paragraph(); p.add_run(line).italic = True; p.paragraph_format.space_after = Pt(2)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def response(doc, items, label="Response: "):
    p = doc.add_paragraph(); r = p.add_run(label); r.bold = True; r.font.color.rgb = RGBColor(0xB0, 0x6A, 0x1E)
    p.paragraph_format.space_after = Pt(2)
    for kind, txt in items:
        if kind == "p":
            q = doc.add_paragraph(txt); q.paragraph_format.space_after = Pt(4)
        elif kind == "b":
            q = doc.add_paragraph(txt, style="List Bullet"); q.paragraph_format.space_after = Pt(2)
        elif kind == "s":
            q = doc.add_paragraph(); rr = q.add_run(txt); rr.bold = True; q.paragraph_format.space_after = Pt(2)

def table(doc, headers, rows, fs=9):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(fs)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(fs)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

OPEN = [
    ("Spillover: the earlier inverse-distance estimate is not robust.", "The 7.45 elasticity of the August draft has a country-clustered standard error of 5.7 (t = 1.3) and a permutation placebo p-value of 0.15; the exposure beyond 5,000 km carries a significantly negative coefficient, so wide exposures track global trends. The manuscript now leads with the contiguity specification (own 3.48, neighbour 1.93, jointly instrumented; clustered t = 2.7 and 2.8; permutation p = 0.004). Under country clustering the joint specification has a weak first stage (Kleibergen-Paap F 3.3), but the neighbour coefficient remains bounded away from zero by the subset Anderson-Rubin set (0.1 to 3.1), and the single-endogenous contiguity specification (neighbour instrumented, own shifter controlled) is strong and stable: 2.05 (clustered s.e. 0.61, F 175, Anderson-Rubin set 0.9 to 3.2), 2.07 (s.e. 0.83) with sub-region-by-year fixed effects. Only the contiguity definition survives clustering; the five-nearest and 500 km definitions have Anderson-Rubin sets that include zero. What remains fragile is the mechanism, which attributed to neighbours depends on the weighting (gauge and higher intensity under inverse distance; flights, longer stages and lower intensity under contiguity). The own intensity coefficient also changes sign in the joint specification (+0.32). The spillover layer should be presented as a contiguity result with these caveats stated."),
    ("Exclusion restriction: passes in the aggregate, not sector by sector, and the aviation cycle is not separable from world growth.", "Total non-aviation CO2 does not respond to the instrument (reduced form 0.05 against 0.73 for aviation), and air geography beats sea geography in the placebo-instrument horse race. But coal and cement CO2 rise with the instrument (0.90 and 0.67) while power, buildings and agriculture fall, so the instrument predicts a recomposition of non-aviation emissions; and the world-GDP and world-export cycles interacted with the same geography are collinear with the aviation cycle (correlations 0.82 and 0.84), so we cannot show statistically that the identifying variation is aviation-specific rather than growth-specific. The Hansen test also rejects equality with the tourism instrument. These are reported in full in Methods; a referee may still regard them as the weakest point."),
    ("Identification is concentrated in the expansion era and in low-baseline countries.", "The unrestricted post-2010 first stage has F = 7 (36.7 after dropping 2020 to 2021), the top baseline-connectivity tercile has F = 1.8, the fourth quintile has F of 0.0, and the high-income tercile has F = 10. The elasticity for mature networks is therefore imprecise (1.83, p = 0.06 for high income) and the gradient figure has a gap at the fourth quintile. The take-off interpretation is the honest reading, and the 42.5 percent attribution is the upper end of a 35 to 43 percent range."),
    ("Correction to the August draft.", "The heterogeneity numbers in the August draft (11.43, 5.91, 0.35 by income tercile) were estimated on international CO2 but labelled as total CO2. The corrected total-CO2 estimates are 10.40, 6.14 and 1.83, and the regional pattern is unchanged (Europe is a precise zero, minus 0.61). Coauthors who cited the earlier numbers should update them."),
    ("Airport level remains descriptive.", "The airport Feyrer shifter has no first stage within countries (F 0.4 to 0.7) and the earlier heritage-proximity instrument failed the size-by-cycle test; the concentration analysis applies the country elasticity to airports, and each country's largest airport cannot be estimated separately under country-by-year fixed effects. The airport layer answers the aggregation question descriptively, not causally."),
    ("Level specifications are imprecise.", "The level-level slope (4.2 Mt per GACI unit, s.e. 2.0) and especially the top-tercile level slope (minus 27.7, not significant) are dominated by a few large emitters; the semi-log results are the informative complement to the log-log estimates."),
    ("Domestic traffic.", "Own connectivity has no effect on domestic emissions (minus 0.64, s.e. 1.14) and the neighbour effect on domestic emissions is significant only with robust errors (2.02, s.e. 0.90; clustered 2.34). The paper's statements about domestic traffic should stay cautious."),
    ("Inference convention changed to country clustering.", "All country-year tables in the canonical manuscript (co2_overleaf_20260903_cl) now use standard errors clustered by country (184 clusters); heteroskedasticity-robust results are kept only in Supplementary Table 1. Consequences: the headline elasticity is 5.67 with s.e. 1.12 (t = 5.1) and first-stage F = 18.4 rather than 154; the efficiency term (-0.40, s.e. 0.30) and the gauge and stage components are no longer individually significant, so the paper now describes the efficiency margin as small and imprecise; within-tercile and within-quintile first stages are weak (F between 2 and 16), so the heterogeneity gradient rests on the pooled interactions (-3.33, s.e. 0.57 by income; -2.33, s.e. 0.69 by connectivity) rather than on the split samples; the Hansen test against the tourism instrument now rejects only at 5 percent (J = 4.1); the sea-geography placebo still passes but the air first stage with the sea term included is weak (F = 3.0); the spillover results are unchanged because they were already reported with clustered errors."),
    ("Length and display count.", "The restructured manuscript has about 4,100 words before Methods, four main tables and nine main figures, plus ten Extended Data tables, seven Extended Data figures and three Supplementary tables. This exceeds Nature-family limits and will need cutting at submission; the local LaTeX installation is broken, so the file has not yet been compiled (Overleaf required)."),
]

def open_issues(doc):
    heading(doc, "Open issues and fragile results (shared with all coauthors)")
    for t, body in OPEN:
        p = doc.add_paragraph(); r = p.add_run(t + " "); r.bold = True; p.add_run(body); p.paragraph_format.space_after = Pt(5)

# ============================================================== LZ
doc = new_doc("Response to Prof. Zheng's comments on the empirical analyses (GACI and aviation CO2): results",
              "Prepared 3 September 2026 by Sunbin Yoo. All estimates are now in the restructured manuscript main_co2_nature_20260903.tex (co2_overleaf_20260903) and the workbook CO2_results_summary_20260903_LZ.xlsx. Comment text is quoted from Comments_GAC&CO2_LZ.docx.")
heading(doc, "Overall")
comment_box(doc, "Overall, I think the current results are already strong ... I suggest further strengthening the empirical analysis in four directions ... the empirical analysis should be organized into the following layers.")
response(doc, [("p", "All four directions have been implemented with new estimation, and the Results section is now organised in the five layers you proposed: causal effect (country and airport), mechanism (identity decomposition), heterogeneity, spillovers, policy. Two findings changed in the process and are flagged in the last section: the neighbour-connectivity result of the August draft did not survive clustered inference and a permutation placebo, and has been replaced by a contiguity specification with own and neighbour connectivity jointly instrumented; and the heterogeneity estimates of the August draft had been computed on international rather than total CO2 and are corrected.")])
table(doc, ["Request", "What was done", "Where"],
      [["1 Decompose the 5.67 elasticity", "Exact identity decomposition (flights, seats per flight, km per flight, CO2 per seat-km) on the identical sample; by income and connectivity tercile; international and domestic identities; waterfall figure", "Table 2 (tab:decomp), Fig. waterfall, ED Table 4"],
       ["2 Airport-level analysis", "Within-country elasticities by hub status, baseline connectivity, traffic, orientation, income, region; topology-only regressors; contribution concentration (top 1/5/10/25 percent, Lorenz, Gini) benchmarked against emissions; airport Feyrer-shifter pilot (fails)", "Fig. airport concentration, Table 3 (tab:airport_conc), ED Table 5, SI Table 2"],
       ["3 Formal spillover analysis", "Own and neighbour connectivity jointly instrumented under contiguity, five nearest, 500 km, kernels; distance bands and continuous decay; within versus outside sub-region and aviation bloc; sub-region-by-year fixed effects; permutation placebo; own-versus-neighbour margins; clustered inference", "Table 4 (tab:spillover), ED Table 6, ED Figs 4 and 5"],
       ["4 Exclusion restriction", "Three direct tests in Methods (non-aviation placebo, air-versus-sea geography, zero first stage), all pass; six further checks in ED/SI with two stated caveats (coal and cement co-movement; cycle collinearity); alternative instrument constructions have no first stage", "ED Table 7, SI Table 1, ED Fig. 6, Methods"],
       ["5-layer structure", "Results re-ordered; mediation moved to Extended Data; Methods gains decomposition identity, airport design, spillover design, exclusion diagnostics", "Manuscript"]])

heading(doc, "1. Decompose the CO2 elasticity")
comment_box(doc, "The most important result is that a 1% increase in GACI increases aviation CO2 by 5.67%. ... where does this very large elasticity come from? ... distinguish between scale effects and efficiency effects.")
response(doc, [
    ("p", "Because emissions are computed from scheduled flights, national CO2 equals flights x seats per flight x km per flight x CO2 per seat-km, so the log elasticities add exactly (equations 2 and 3 of Methods). Load factor is constant by construction and cancels; passenger-km cannot be separated from these data, which we state."),
])
table(doc, ["Component", "Elasticity (s.e.)", "Share of total"],
      [["Flights (frequency)", "+6.98*** (0.57)", "123%"], ["Seats per flight (gauge)", "-0.30 (0.23)", "-5%"], ["Km per flight (stage length)", "-0.60*** (0.21)", "-11%"],
       ["Scale subtotal (= seat-km elasticity)", "+6.07*** (0.44)", "107%"], ["CO2 per seat-km (intensity)", "-0.40*** (0.12)", "-7%"], ["Total CO2 (Table 1)", "+5.67*** (0.41)", "100%"]])
response(doc, [
    ("p", "The answer to 'where does 5.67 come from' is that it is a frequency response: connectivity adds flights, not larger aircraft or longer stages, and the efficiency gain offsets seven percent of the scale effect (scale exceeds efficiency by a factor of fifteen). The composition margins are small (LTO share +0.014, not significant; international share of seat-km +0.10 percentage points)."),
    ("p", "The decomposition also explains the heterogeneity. In the bottom income tercile every scale margin expands (flights +8.8, gauge +0.9, stage +1.7) and intensity falls by 1.1, total 10.4; in the middle tercile flights rise by 8.6 but stages shorten by 1.7, total 6.1; in the top tercile flights still rise (8.5) but aircraft become smaller (-3.3) and stages shorter (-4.3), so the total is 1.8 and imprecise (first-stage F = 10). Applied to international departures the identity gives 5.69 = 6.03 (flights) + 0.58 (gauge) - 0.40 (stage) - 0.52 (intensity); domestic emissions do not respond (-0.64, s.e. 1.14)."),
    ("p", "The mediation analysis (84 to 87 percent through frequency and seat-km) is retained in Extended Data as a complementary view. The fleet fuel-efficiency split (within-type versus type mix) would require an aircraft-type aggregate from Fangyu and is not included."),
], label="Findings: ")

heading(doc, "2. Airport-level analysis")
comment_box(doc, "Is the global effect driven by a small number of hub airports? ... rank airports by their estimated connectivity-induced emissions and calculate how much of the global effect is accounted for by the top 1%, 5%, 10%, etc.")
response(doc, [
    ("p", "The emissions delivery covers 6,356 airports; the analysis keeps the 5,354 that are nodes of the connectivity network (the 1,002 others hold 0.1 percent of departure CO2). Within countries, with airport and country-by-year fixed effects, a one percent increase in an airport's connectivity is associated with 3.72 percent more CO2, 4.18 percent more seat-km, 0.49 percent lower intensity and a 0.33 point higher international share."),
    ("s", "Heterogeneity (ED Table 5)"),
    ("b", "Hubs have a lower elasticity: 2.04 at the 1996 global top one percent and 2.11 at the top five percent, against 3.78 and 4.05 elsewhere; pooled interaction -2.56 (s.e. 0.20). The response is systemic, not hub-driven."),
    ("b", "By baseline connectivity tercile 4.18 / 5.85 / 2.90; by baseline traffic 5.14 / 5.24 / 3.04; domestic-only airports 4.24, mixed 2.86, highly international 4.69; by host-country income 4.10 / 4.02 / 3.39; Africa 6.03, Europe 4.45, Latin America 4.02, Asia 3.52, North America 2.59."),
    ("b", "Topology-only components reproduce the pattern (closeness 4.41 on CO2 and -0.70 on intensity; eigenvector, betweenness and degree all lower intensity), so the capacity term in airport GACI is not driving the result."),
    ("b", "Each country's largest airport cannot be estimated as a separate subsample under country-by-year effects (one airport per country-year); it enters through the interaction (-2.01)."),
    ("s", "Contribution and concentration (Table 3, Fig. airport concentration)"),
    ("b", "Applying the country elasticity to each airport's 1996-2023 connectivity change attributes 345 Mt across 3,833 airports, consistent with the 356 Mt country total."),
    ("b", "Attributed emissions are more concentrated than emissions: top one percent of airports 45.8 percent (emissions 41.0), top five percent 84.5 (77.6), top ten percent 94.1 (89.0), Gini 0.945 (0.916). The result is robust to using the airport elasticity (3.72) or hub-specific elasticities."),
    ("b", "The concentration is at the new hubs, not the incumbents: the 260 airports in the 1996 global top five percent hold 68.5 percent of the attributed total against 75.3 percent of emissions. Largest contributions: Dubai 19.4 Mt, Doha 12.3, Shanghai Pudong 11.2, Istanbul 10.3, Incheon 9.9, Heathrow 9.9, Haneda 8.7, Singapore 8.5."),
    ("b", "Policy corollary in Layer 5: an instrument covering the top five percent of airports (about 190) would cover 85 percent of connectivity-driven emissions."),
    ("s", "Identification pilot"),
    ("p", "An airport-level Feyrer shifter (a_t x log 1996 air market access of the airport, own country excluded) has no first stage within countries (F 0.4 to 0.7; within-country s.d. of the geography term 0.04), so airport results stay descriptive and the pilot is disclosed in SI Table 2. A shift-share exposure to 1996 partner airports could not be built because the delivery has no route-level data."),
], label="Findings: ")

heading(doc, "3. Formal spillover analysis")
comment_box(doc, "(a) First-order neighbour effects ... while controlling for its own GACI. (b) Distance-decay spillovers ... (c) Regional spillovers ... connect the spillover effects to the mechanisms/decomposition.")
response(doc, [
    ("p", "This is the layer where the results changed most. The August estimate (7.45, inverse-distance weights, own shifter in reduced form) has a country-clustered standard error of 5.7 and a permutation placebo p-value of 0.15, and the exposure to countries beyond 5,000 km carries a significantly negative coefficient (-7.0): wide exposures track global trends. We therefore rebuilt the analysis around definitions that allow own and neighbour connectivity to be instrumented jointly."),
    ("s", "(a) Own-controlled first-order effect (Table 4, Panel A)"),
])
table(doc, ["Neighbour definition", "Own ln GACI", "Neighbour ln GACI", "SW F own / nbr", "KP F"],
      [["Contiguous countries", "3.48*** (0.47) [1.29]", "1.93*** (0.27) [0.69]", "66 / 124", "32.7"], ["Five nearest", "1.23* (0.64) [1.84]", "3.51*** (0.66) [1.94]", "48 / 49", "23.5"],
       ["Within 500 km", "4.89*** (0.52) [1.34]", "0.62** (0.26) [0.66]", "104 / 224", "51.2"], ["Kernel 1,000 km", "-0.08 (0.66) [1.91]", "4.97*** (0.77) [2.29]", "41 / 49", "20.5"],
       ["Inverse distance, all countries", "-2.35 (1.69)", "16.18*** (3.74)", "10 / 11", "5.1"], ["Inverse distance, own shifter in RF (August)", "RF 0.25** (0.12)", "7.45*** (1.99) [5.66]", "--", "134.1"]])
response(doc, [
    ("p", "Robust s.e. in parentheses, country-clustered in brackets. The contiguity specification is the headline: own 3.48 and neighbour 1.93, both significant with clustered errors (t = 2.7 and 2.8), conditional first stages strong, permutation placebo p = 0.004 (five nearest: p = 0.010). Treating own GACI as an exogenous control instead gives 3.32 for the neighbour term but is biased because own GACI is endogenous; it is kept as a reference row."),
    ("s", "(b) Distance decay (ED Table 6, ED Fig. 4)"),
    ("p", "There is no smooth decay. One definition at a time: contiguous 2.05***, 0-500 km 0.09 (ns), 500-1,000 km -0.11 (ns), 1,000-2,000 km 2.51***, 2,000-5,000 km 3.06 (ns), beyond 5,000 km -7.00***. Kernel coefficients rise with the scale (2.2 at 250 km to 6.2 at 5,000 km) because wider kernels absorb global trends. The spillover is a land-neighbour phenomenon."),
    ("s", "(c) Regional (ED Table 6)"),
    ("p", "Within aviation blocs the leave-out exposure carries 2.35*** (outside-bloc 13.6, again the broad-exposure artefact); the UN sub-region split is weakly identified. With sub-region-by-year fixed effects, which absorb every regional trend, the contiguity effect is 1.95 (robust s.e. 0.47; sub-region-clustered 1.09), and the 500 km kernel 3.49 (s.e. 1.07). By receiving region the estimates are unstable (Asia large, Americas negative) and we do not report them as findings; by baseline international share the effect is present in the bottom and top terciles."),
    ("s", "Mechanism link (Table 4, Panel B, contiguity, jointly instrumented)"),
    ("p", "Own connectivity works through frequency (5.61) with shorter stages (-1.80) and no up-gauging; neighbours' connectivity raises own seat-km by 2.56 through more flights (1.22) on longer stages (1.04), leaves gauge unchanged, raises the international share slightly (0.07) and lowers CO2 per seat-km (-0.63). It loads on international CO2 (2.23***) rather than domestic (2.02, ns clustered). The interpretation is traffic feeding a regional hub. Note that this mechanism differs from the August draft (which found gauge and higher intensity under inverse-distance weights), and that the own intensity coefficient in the joint specification (+0.32) differs from the single-equation -0.40; both are stated in the text."),
    ("s", "Inference"),
    ("p", "Country, sub-region and two-way clustered errors are reported; Country-clustered Anderson-Rubin sets are reported for the contiguity specifications (single-endogenous 0.9 to 3.2; joint subset 0.1 to 3.1); Conley spatial HAC errors were not implemented and can be added."),
], label="Findings: ")

heading(doc, "4. Strengthen the exclusion restriction")
comment_box(doc, "Nature-series reviewers are likely to focus heavily on the exclusion restriction of IV, particularly because air connectivity is related to many dimensions of economic development.")
response(doc, [
    ("p", "The manuscript now presents the exclusion restriction in two tiers. Methods states three direct tests, all of which pass: (1) non-aviation emissions do not respond to the instrument (reduced form on total territorial fossil CO2 excluding domestic aviation 0.05, s.e. 0.12, against 0.73, s.e. 0.16, for aviation CO2); (2) the effect runs through air geography rather than geography in general (with the sea-geography interaction entered alongside, sea 0.08, s.e. 0.30, air 0.64, s.e. 0.22); (3) where the instrument cannot move connectivity it does not move emissions (top baseline-connectivity tercile: first-stage F 0.2, reduced form 0.10, s.e. 0.19, against 2.22 and 0.41 below). Six further checks are reported in ED Table 7 and SI Table 1 and summarised in one paragraph, with two caveats stated rather than resolved: coal and cement CO2 co-move with the instrument (0.90 and 0.67), and the aviation cycle cannot be separated statistically from world GDP and trade cycles interacted with the same geography (correlations 0.82 and 0.84). Alternative instrument constructions that would avoid these caveats (air-minus-sea advantage x cycle; air interaction with the sea interaction as a control) have no usable first stage (F 1.0 and 3.0), so the Feyrer interaction remains the single instrument."),
])
table(doc, ["Test", "Result", "Reading"],
      [["(1) Placebo outcomes: reduced form on non-aviation emissions", "Total territorial CO2 excl. domestic aviation 0.05 (s.e. 0.12); aviation CO2 0.73 (0.16)", "A general development channel that raises all emissions is rejected"],
       ["(2) Placebo geography: aviation cycle x sea market access", "Entered with the air interaction: sea 0.08 (0.30), air 0.64 (0.22)", "The effect runs through air geography, not geography in general"],
       ["(3) Zero first stage: top baseline-connectivity tercile", "First-stage F 0.2; reduced form on CO2 0.10 (0.19) vs 2.22 and 0.41 in the lower terciles", "Where the instrument cannot move connectivity, it does not move emissions"],
       ["Six secondary checks (ED Table 7, SI Table 1)", "Controls 4.7 to 4.9; alternative shifters 5.8 to 6.1; leads uninformative; Hansen J vs tourism IV 4.1 (p 0.04); rival cycles collinear with the aviation cycle; robust s.e. 0.41 vs clustered 1.12", "Two caveats stated: coal and cement co-move with the instrument (0.90, 0.67); the aviation cycle is not separable from world GDP and trade cycles"]])

heading(doc, "5. Five-layer structure")
response(doc, [("p", "Implemented as: Layer 1 (Table 1; airport evidence with Fig. concentration and Table 3; efficiency curve), Layer 2 (Table 2 decomposition, waterfall, ED Table 4; mediation in ED Table 3), Layer 3 (heterogeneity with corrected total-CO2 numbers; a new subsection on what the elasticity represents, following Yifu's comments), Layer 4 (Table 4 spillovers, ED Table 6, ED Figs 4-5), Layer 5 (attribution with a heterogeneity-adjusted range, SCC, mismatch, SAF, hub-coverage corollary). Methods adds the identity, the airport design and pilot, the exclusion diagnostics, and the spillover design. The draft is over Nature length and display limits and will need trimming at submission.")])
open_issues(doc)
doc.save(os.path.join(HERE, "Response_LZ_results_20260903.docx"))
print("saved Response_LZ_results_20260903.docx")

# ============================================================== Yifu
doc = new_doc("Response to Yifu's comments on the interpretation of the 5.67 elasticity: results",
              "Prepared 3 September 2026 by Sunbin Yoo. Estimates are in main_co2_nature_20260903.tex (subsection 'What the elasticity represents', ED Tables 8-10, ED Fig. gradient, SI Table 3) and in CO2_results_summary_20260903_LZ.xlsx (sheets Y_*).")
heading(doc, "1. Interpretation of the 5.67 elasticity and the low-base problem")
comment_box(doc, "I wonder whether the large elasticity mainly reflects the 'take-off' stage of aviation development ... a country moving from 1 to 2 would experience a 100% increase, while a mature network moving from 100 to 101 would see only a 1% increase ... complement the current results with semi-log and/or level specifications.")
response(doc, [("p", "We agree and now state in the abstract, Results and Discussion that the headline elasticity describes the take-off stage of network development rather than a universal constant. The functional-form check is in ED Table 8.")])
table(doc, ["Specification", "2SLS (s.e.)", "Implied elasticity at sample means", "KP F"],
      [["Log CO2 on log GACI (reference)", "5.67 (0.41)", "5.67", "153.6"], ["Log CO2 on GACI level (semi-log)", "4.09 (0.35) per unit", "4.44 (x mean GACI 1.09)", "165.6"],
       ["CO2 (Mt) on GACI level", "4.25 (1.95) Mt per unit", "1.21 (x mean GACI / mean CO2 3.81 Mt)", "165.6"], ["CO2 (Mt) on log GACI", "5.89 (2.76) Mt per log point", "1.55", "153.6"],
       ["Semi-log, low / middle / high baseline-connectivity tercile", "10.26 (0.87) / 4.59 (0.87) / 1.11 (0.57)", "7.8 / 4.5 / 1.6", "111.5 / 29.5 / 10.8"]])
response(doc, [("p", "GACI (capacity-weighted mean) has a sample mean of 1.09 and a baseline range of 0.56 to 2.57, so a one-unit change is roughly a doubling for a typical country and the semi-log slope of 4.09 log points per unit is the absolute-change analogue of the elasticity. The gradient survives the change of scale: the same absolute addition to the network raises emissions ten times more in the bottom tercile than in the top. The level-level slopes are imprecise and dominated by large emitters (the top-tercile level slope is -27.7, not significant), so we treat the semi-log results as the informative complement.")], label="Findings: ")

heading(doc, "2. IV and the post-2010 period; the accident instrument")
comment_box(doc, "The first-stage F-test is very strong before 2010 but becomes weak afterwards (KP F = 7) ... a more conservative interpretation may be that the large elasticity captures the effect ... during the network expansion/take-off stage. We could also try the aviation-accident IV.")
response(doc, [
    ("p", "The conservative interpretation is adopted. The text now says that the identifying variation is concentrated in the expansion era (first stage strong before 2010, and in the mature era only once 2020 to 2021 are excluded, F = 36.7), that the elasticity falls from 5.6 to 3.0 across the eras, and that the headline number is the emissions response during take-off, which the sample observes for most countries between 1996 and the late 2000s."),
    ("p", "The accident instrument (Aviation Safety Network country-year fatal accidents and deaths, lagged one year) had already been piloted and is now reported in SI Table 3. It is too weak to stand alone (first-stage F 1 to 4; 2SLS 6.2 with s.e. 2.4 for lagged fatal accidents, 5.6 with s.e. 3.0 for deaths), but the Hansen test does not reject its joint validity with the Feyrer instrument (p = 0.70 and 0.95) and the jointly instrumented elasticity is 5.4 (s.e. 0.42). We present it as supporting evidence, not as an independent identification strategy."),
], label="Findings: ")

heading(doc, "3. Attribution using a common elasticity")
comment_box(doc, "I am slightly concerned about applying the same 5.669 elasticity to all countries in the 2023 attribution exercise ... add a heterogeneity-adjusted attribution as a robustness check.")
response(doc, [("p", "ED Table 10 recomputes the attribution under six rules.")])
table(doc, ["Elasticity rule", "Attributed 2023 CO2 (Mt)", "Share of 2023 emissions"],
      [["Common elasticity 5.67 (headline)", "356", "42.8% (42.5% of the 838 Mt world total)"], ["Baseline-connectivity terciles 8.46 / 5.07 / 4.05", "312", "37.5%"],
       ["Baseline-income terciles 10.40 / 6.14 / 1.83", "294", "35.3%"], ["Continuous, linear interaction with baseline", "323", "38.9%"],
       ["Continuous, quadratic interaction", "314", "37.8%"], ["Semi-log slope 4.09 on the absolute change in GACI", "353", "42.5%"]])
response(doc, [("p", "Country level, largest contributors (attributed 2023 CO2, Mt) under three rules:")], label="")
table(doc, ["Country", "Baseline GACI 1996", "Common 5.67", "Connectivity-tercile rule", "Continuous (quadratic) rule"],
      [['CHN', '1.16', '87.7', '76.4', '79.3'], ['USA', '2.01', '36.4', '26.7', '25.9'], ['ARE', '1.58', '24.7', '23.1', '22.7'], ['JPN', '1.32', '17.4', '14.2', '14.1'], ['TUR', '1.21', '16.6', '15.5', '15.7'], ['IND', '1.18', '15.9', '12.9', '13.5'], ['KOR', '0.88', '14.1', '14.0', '14.1'], ['CAN', '1.48', '13.1', '10.8', '10.5'], ['DEU', '2.36', '-15.8', '-10.4', '-11.2']])
response(doc, [("p", "The headline is the upper end of a 35 to 43 percent range; the lower end is about one third of current emissions. The abstract keeps 42.5 percent but the Results and Discussion now give the range. Country ranks are stable (China, the United States and the Gulf states lead under every rule); the largest downward revisions in megatonnes are for the United States (-10), China (-8), Japan (-3) and Spain (-3), and Germany's negative attribution shrinks from -16 to -11.")], label="Findings: ")

heading(doc, "4. Continuous heterogeneity by baseline connectivity")
comment_box(doc, "present the heterogeneity by baseline connectivity more continuously rather than relying only on terciles ... whether the current low/middle/high pattern reflects a smooth decline with network maturity or is driven mainly by countries at the very bottom.")
response(doc, [
    ("p", "ED Table 9 and the new Fig. gradient give quintile splits and pooled flexible interactions. Quintiles of 1996 GACI: 8.49 (F 100), 8.49 (F 48), 3.29 (F 36), unidentified (F 0.0), 4.05 (F 12). Pooled 2SLS with log GACI interacted with centred log baseline GACI (instrument interacted identically, joint first-stage F = 76): linear interaction -3.99 (s.e. 0.39), implying 7.1 at the tenth percentile of baseline connectivity, 6.0 at the median and 4.1 at the ninetieth; the quadratic term is positive, so the fitted curve flattens at about 4 rather than continuing to zero."),
    ("p", "The pattern is therefore a step rather than a smooth slope: the two lowest quintiles, which together hold 40 percent of countries, share the high elasticity, and the decline occurs between the second and third quintiles. It is not driven only by countries at the very bottom. The gap at the fourth quintile (no instrument variation) is shown as such in the figure. In semi-log form the quintile slopes are 10.5, 9.0, 2.7, unidentified, 1.4, the same shape."),
], label="Findings: ")
open_issues(doc)
doc.save(os.path.join(HERE, "Response_Yifu_results_20260903.docx"))
print("saved Response_Yifu_results_20260903.docx")

# em-dash check
for fn in ["Response_LZ_results_20260903.docx", "Response_Yifu_results_20260903.docx"]:
    d = Document(os.path.join(HERE, fn))
    txt = "\n".join(p.text for p in d.paragraphs) + "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
    print(fn, "em-dash:", txt.count(chr(8212)), "words:", len(txt.split()))
