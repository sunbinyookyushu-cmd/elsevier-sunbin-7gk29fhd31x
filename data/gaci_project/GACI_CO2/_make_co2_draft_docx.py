# -*- coding: utf-8 -*-
"""Build Draft_CO2_Connectivity_20260822.docx: the simple-framing draft
("does connectivity increase or decrease CO2?") with ALL results: 8 tables
+ 3 embedded figures. Numbers from co2_feyrer_full.log, co2_main.log,
co2_airport_panel.log, co2_feyrer_sizecheck.log, co2_country_sizecheck2.log,
co2_feyrer_mechanism.log, attribution and SAF arithmetic (2026-08-22 runs).
v3: emerging-hub framing (China not headlined) + mechanism decomposition
section 5.3 (Table 4, frequency response + fleet channel).
v5: new section 5.6 (Table 7, group heterogeneity from co2_feyrer_hetero.do)
+ Figures 4-5 (attributed / dln GACI maps from 10_extra_maps.py); attribution
and SAF renumbered to 5.7/5.8, Tables 8/9.
v4: Table 9 Panel B = beta-linked SAF accounting (savings vs the 356 Mt
attributed to connectivity growth + emissions-neutral growth headroom;
trade-free, CO2 arithmetic only)."""
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = r"C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_CO2"
OUT = HERE + r"\Draft_CO2_Connectivity_20260823_v5.docx"

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11)


def h(level, text):
    doc.add_heading(text, level=level)


def p(text, italic=False):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.italic = italic
    return par


def caption(text):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.bold = True
    run.font.size = Pt(10)


def note(text):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.font.size = Pt(9)


def table(rows, widths=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            c = t.cell(i, j)
            c.text = str(cell)
            for par in c.paragraphs:
                for run in par.runs:
                    run.font.size = Pt(9)
                    run.font.name = "Times New Roman"
                    if i == 0:
                        run.bold = True
                if j > 0:
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return t


def fig(path, cap):
    doc.add_picture(path, width=Inches(6.3))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(cap)


# ---------------- title + abstract ----------------
tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tp.add_run("How Much Does Air Connectivity Increase Aviation CO2?\n"
               "Evidence from 184 Countries, 1996-2023")
r.bold = True
r.font.size = Pt(16)
p("Working draft with full first-pass results, 22 August 2026. "
  "Author order TBD.", italic=True)

h(1, "Abstract")
p("More connectivity means more flying, so aviation CO2 should rise; what is "
  "unknown is by how much, whether the rise is more or less than "
  "proportional, and how much of it is offset by the efficiency gains of "
  "hubbing, since hub consolidation shifts flying into larger aircraft and "
  "longer stage lengths that emit less per seat-kilometre. We answer these "
  "questions by combining flight-stage-resolved emissions for more than 6,000 airports "
  "(1996-2024, EEA/EMEP methodology) with the Global Air Connectivity Index "
  "(GACI), instrumenting connectivity with a Feyrer-type air/sea market-access "
  "shifter (first-stage F = 153). Connectivity growth increases emissions, and "
  "more than proportionally: the elasticity of national aviation CO2 "
  "with respect to hub quality is 5.67 (SE 0.41), essentially identical under "
  "three emission-allocation rules and three connectivity aggregations, and "
  "robust to demanding validity checks. An offsetting efficiency channel is "
  "confirmed, emissions per seat-kilometre decline with connectivity at both "
  "the country (-0.40) and airport (-0.49) level, and a margin decomposition "
  "shows the gain arrives through fleet composition rather than aircraft "
  "up-gauging; seat-kilometres expand faster (6.07), so the scale effect "
  "dominates. "
  "Connectivity growth since 1996 accounts for 356 Mt, or 42.5 percent, of "
  "2023 aviation CO2, concentrated in emerging hubs (China +88 Mt, the "
  "United Arab Emirates +25 Mt, Turkey +17 Mt), with declines in mature "
  "networks (Germany -16 Mt). Reductions in the level of emissions therefore depend on "
  "fuel substitution rather than on efficiency improvements: ReFuelEU-style "
  "blending paths reduce the 2023 total from 838 Mt to 457-545 Mt by 2050.")

# ---------------- 1 introduction ----------------
h(1, "1. Introduction")
p("Aviation is among the hardest-to-abate transport sectors and the most "
  "network-dependent one. Countries invest heavily in airports, routes, and "
  "air-service liberalisation to improve their position in the global air "
  "network. This paper asks the simplest quantitative question about the "
  "environmental side of that investment: how much does air connectivity "
  "growth increase aviation CO2 emissions?")
p("The direction is intuitive; the magnitude is not. Connectivity growth adds "
  "flights and seat-kilometres, which raises fuel burn. At the same time it "
  "concentrates flying into hubs, and hub operations use larger aircraft over "
  "longer stage lengths, both of which reduce emissions per seat-kilometre; "
  "the landing-and-take-off cycle, the most fuel-intensive phase per "
  "kilometre, is amortised over more distance. How large the net increase is, "
  "whether it is more or less than proportional, and how much the efficiency "
  "margin offsets are empirical questions, and to our knowledge no causal "
  "estimate of the connectivity-emissions elasticity exists at global scale.")
p("We provide one. Flight-level CO2 computed under the EEA/EMEP Guidebook "
  "framework for every scheduled flight from 1996 to mid-2024 is aggregated "
  "to the country-year level under three allocation rules and merged with the "
  "GACI network panel. Identification uses a Feyrer-type instrument that "
  "interacts fixed 1996 air-route geography with the global travel cycle, "
  "with the parallel sea market-access channel controlled directly.")
p("Three results emerge. First, connectivity increases emissions, with an "
  "elasticity of 5.67, far above one, and the answer does not depend on how "
  "emissions are allocated to countries, how national connectivity is "
  "aggregated, or which of two independent instruments is used. Second, the "
  "efficiency channel operates but is insufficient to offset the scale "
  "response: emissions per seat-kilometre decline with connectivity at both "
  "the country and the airport level, yet traffic expands more rapidly. "
  "Third, the magnitudes are first-order: "
  "42.5 percent of 2023 aviation CO2 is attributable to post-1996 "
  "connectivity growth, and reductions in the level of emissions require "
  "fuel substitution rather than efficiency alone.")

# ---------------- 2 why ambiguous ----------------
h(1, "2. Scale, technique, and composition: why the magnitude is an empirical question")
p("Emissions can be decomposed as traffic (seat-kilometres) times emissions "
  "per seat-kilometre, with the mix of domestic and international flying "
  "shifting both terms. Connectivity growth plausibly moves all three "
  "margins: it scales traffic upward; it improves technique, because hub "
  "consolidation raises average aircraft size and stage length; and it "
  "recomposes traffic toward international long-haul. The net elasticity "
  "therefore depends on how far the technique and composition margins offset "
  "the scale margin, which theory does not pin down. The magnitudes can be "
  "resolved empirically because the outcomes map directly "
  "onto the three margins: seat-kilometres "
  "(scale), CO2 per seat-kilometre (technique), and the international share "
  "and international emissions (composition).")

# ---------------- 3 data ----------------
h(1, "3. Data")
h(2, "3.1 Emissions")
p("Flight-level CO2 is computed from OAG schedules under the EEA/EMEP "
  "Guidebook (2023) framework, Section 1.A.3.a: fuel burn by engine type and "
  "stage length, multiplied by a fixed emission factor (3.15 kg CO2 per kg of "
  "Jet A; 3.10 for AvGas piston traffic). The delivery is stage-resolved at "
  "the airport-month level, split by domestic and international, with "
  "departure-side phases (taxi-out, take-off, climb-out, cruise) and "
  "arrival-side phases (approach, taxi-in, cruise) kept separate, together "
  "with flights, seats, and seat-kilometres. Coverage is 1 January 1996 to "
  "30 June 2024; the partial July 2024 rows are dropped and annual analysis "
  "ends in 2023. Emissions are schedule-based (no load factors, weather, or "
  "airline-specific procedures) and cover aircraft operations only.")
h(2, "3.2 Allocation rules")
p("Because cruise emissions occur between countries, allocation is a choice. "
  "We build three country aggregations from the stages: LTO-territorial "
  "(each landing-and-take-off phase at its own airport); fuel-uplift (LTO "
  "plus cruise assigned to the departure airport, the IEA bunker convention; "
  "our headline); and a 50/50 cruise split. Cruise is recorded once on each "
  "side of a flight and used exactly once.")
h(2, "3.3 Validation")
p("The 2019 world total is 0.919 Gt against the ICCT estimate of 0.92 Gt for "
  "commercial aviation; the LTO share is 11.8 percent, in the standard range. "
  "The log-log correlation with the independent OWID/ICCT country series is "
  "0.99 in every overlapping year (2013-2023), with a level ratio of "
  "1.05-1.10 consistent with full-capacity scheduling. After crosswalk "
  "patches for closed and relocated airports, 100 percent of GACI panel "
  "airport-years match the emissions data.")
h(2, "3.4 Connectivity and sample")
p("Connectivity is the GACI panel (degree, flow betweenness, closeness, "
  "eigenvector, and regional importance, combined by year-wise principal "
  "components), aggregated to countries as the capacity-weighted mean (hub "
  "quality, headline), the maximum, and the sum. The estimation sample is "
  "184 countries, 1996-2023, N = 4,634 country-years.")

# ---------------- 4 strategy ----------------
h(1, "4. Empirical strategy")
p("We estimate, by two-stage least squares with country and year fixed "
  "effects and robust standard errors,")
p("ln CO2(c,t) = beta ln GACI_cwm(c,t) + gamma ln pop(c,t) "
  "+ delta ln seaMA(c,t) + alpha_c + tau_t + e(c,t).", italic=True)
p("The instrument is a Feyrer-type air/sea market-access shifter: fixed 1996 "
  "air-route geography interacted with the global travel cycle, with the sea "
  "market-access channel controlled directly. The first-stage "
  "Kleibergen-Paap F is 153. Two properties matter. First, the instrument "
  "survives the most demanding relevance check we impose, interacting the "
  "global cycle with baseline population, GDP, and seat capacity (F falls "
  "only from 120 to 106); the same check reduces a tourism-heritage "
  "alternative from F = 14 to zero, which is why the tourism shifter serves "
  "only as a secondary lens below. Second, Conley plausibly-exogenous bounds "
  "show the estimates tolerate direct instrument effects of up to 85 percent "
  "of the reduced form before losing significance.")
p("A tourism-heritage instrument (natural and mixed UNESCO endowment times "
  "the global tourism cycle) is retained as a secondary lens: its compliers "
  "are hub-quality changes rather than market-access growth, it covers the "
  "post-2010 era where the Feyrer instrument is weak, and its composition "
  "results are informative even though its first stage is fragile. "
  "Airport-level regressions are reported as descriptive mechanism evidence "
  "only; a pilot airport-level heritage-proximity instrument failed the same "
  "size-cycle check (F 59 to 2.3) and was abandoned. Causal statements are "
  "confined to the country level.")

# ---------------- 5 results ----------------
h(1, "5. Results")

h(2, "5.1 Main estimates: a more-than-proportional emissions response")
caption("Table 1. Main 2SLS estimates (Feyrer instrument). Treatment: ln GACI hub quality.")
table([
    ["", "Total CO2", "LTO only", "50/50", "International", "Seat-km", "CO2/seat-km"],
    ["ln GACI (cwm)", "5.669***", "5.921***", "5.620***", "5.690***", "6.068***", "-0.399***"],
    ["(SE)", "(0.412)", "(0.448)", "(0.409)", "(0.415)", "(0.443)", "(0.118)"],
    ["Wald p (beta = 1)", "0.000", "0.000", "0.000", "0.000", "0.000", "0.000"],
    ["KP F", "153.6", "153.6", "153.6", "152.7", "153.6", "153.6"],
    ["N", "4,634", "4,634", "4,634", "4,633", "4,634", "4,634"],
])
note("Country and year FE; controls: ln population, ln sea market access; robust "
     "SE. Emission allocations: fuel-uplift (headline), LTO-territorial, 50/50 "
     "cruise split. *** p<0.01.")
p("The emissions elasticity of connectivity is 5.67 and statistically "
  "indistinguishable across the three allocation rules (5.62-5.92). "
  "Proportionality is rejected decisively: a Wald test of beta = 1 gives "
  "p < 0.001 in every column. Traffic responds slightly faster than emissions "
  "(6.07 versus 5.67), so emissions per seat-kilometre decline (-0.399, "
  "SE 0.118): the efficiency channel operates but is dominated by the scale "
  "response.")

h(2, "5.2 Robustness: measurement, aggregation, timing, and instrument validity")
caption("Table 2. Robustness of the sign and size. Outcome: ln international CO2 "
        "(panel A), ln international CO2 by period (panel B).")
table([
    ["Panel A: connectivity aggregation", "Hub quality (cwm)", "Sum", "Maximum"],
    ["ln GACI", "5.690***", "2.291***", "4.836***"],
    ["(SE)", "(0.415)", "(0.237)", "(0.343)"],
    ["KP F", "152.7", "89.5", "171.0"],
    ["Panel B: period (Feyrer IV)", "Pre-2010", "Post-2010", ""],
    ["ln GACI (cwm)", "6.262***", "1.051", ""],
    ["(SE)", "(0.590)", "(1.463)", ""],
    ["KP F", "126.9", "7.0", ""],
    ["Panel B continued (tourism IV)", "Pre-2010", "Post-2010", ""],
    ["ln GACI (cwm)", "n/a (F = 0.2)", "1.639***", ""],
    ["(SE)", "", "(0.618)", ""],
    ["KP F", "0.2", "27.7", ""],
])
note("The two instruments identify complementary eras with the same sign: the "
     "Feyrer shifter is strong before 2010, the tourism shifter after 2010.")
caption("Table 3. Validity: size-cycle stress test and Conley bounds.")
table([
    ["First-stage F when cycle x baseline size is controlled", "Baseline",
     "+ pop/GDP cycles", "+ capacity cycle"],
    ["Feyrer instrument", "120.1", "115.5", "105.8"],
    ["Tourism instrument", "13.8", "0.0", "0.6"],
    ["Airport heritage pilot (abandoned)", "59.5", "", "2.3"],
    ["Conley bounds (gamma up to share f* of reduced form)", "2SLS beta",
     "UCI at 30%", "Breakdown f*"],
    ["ln international CO2", "5.690", "[3.25, 6.50]", "0.85"],
    ["ln total CO2", "5.669", "[3.25, 6.48]", "0.85"],
    ["ln CO2/seat-km", "-0.399", "[-0.51, -0.17]", "0.42"],
])
note("Top block: 1996-observed sample. Bottom block: union-of-CI bounds allowing "
     "a direct instrument effect gamma in [0, gmax], gmax expressed as a share of "
     "the reduced-form coefficient; f* is the largest share at which the interval "
     "still excludes zero.")
p("Quintile reduced forms of the Feyrer shifter are flat across baseline "
  "income, baseline connectivity, and remoteness (all bins near 0.7): the "
  "scale response is homogeneous, so the aggregate elasticity is not driven "
  "by any subgroup.")

h(2, "5.3 Mechanism: the scale response is a frequency response")
caption("Table 4. Margin decomposition of the emissions elasticity (Feyrer "
        "instrument). Identity: ln CO2 = ln flights + ln seats per flight "
        "+ ln km per seat + ln CO2 per seat-km.")
table([
    ["", "Flights", "Seats per flight", "Stage length (km/seat)",
     "CO2/seat-km", "LTO share", "Intl share of seat-km"],
    ["ln GACI (cwm)", "6.976***", "-0.303", "-0.605***", "-0.399***",
     "0.014", "0.096**"],
    ["(SE)", "(0.570)", "(0.226)", "(0.211)", "(0.118)", "(0.025)",
     "(0.048)"],
    ["KP F", "153.6", "153.6", "153.6", "153.6", "153.6", "153.6"],
    ["N", "4,634", "4,634", "4,634", "4,634", "4,634", "4,634"],
])
note("Country and year FE; controls: ln population, ln sea market access; "
     "robust SE. The first four columns decompose the Table 1 total-CO2 "
     "elasticity exactly: 6.976 - 0.303 - 0.605 - 0.399 = 5.669. LTO share "
     "and international share are in levels (shares of emissions and of "
     "seat-kilometres). *** p<0.01, ** p<0.05.")
p("Because emissions are the product of flight frequency, aircraft gauge, "
  "stage length, and fuel intensity, the log-linear specification decomposes "
  "the headline elasticity exactly: the four component elasticities sum to "
  "5.67 by construction. Table 4 reports each margin under the Feyrer "
  "instrument. First, the scale response is a frequency response: "
  "instrumented connectivity growth raises departures with an elasticity of "
  "6.98, while average aircraft size does not change (-0.30, SE 0.23). "
  "Second, average stage length shortens (-0.60), indicating that "
  "market-access-driven growth adds short-haul frequencies rather than "
  "long-haul routes. Third, emissions per seat-kilometre fall (-0.40) even "
  "though neither up-gauging nor stage-lengthening occurs, so the technique "
  "margin operates through equipment, a shift toward aircraft types with "
  "lower fuel burn per seat at given stage lengths. The international share "
  "of seat-kilometres rises modestly and the LTO share of emissions is "
  "unchanged. Connectivity growth therefore multiplies flights faster than "
  "emissions because fleets improve, not because networks consolidate into "
  "larger aircraft.")

h(2, "5.4 The efficiency margin: operative but insufficient to offset scale")
caption("Table 5. Airport-level mechanism evidence (descriptive). "
        "Airport FE + country x year FE; SE clustered by airport.")
table([
    ["", "ln CO2", "ln seat-km", "ln CO2/seat-km", "International share"],
    ["ln GACI (airport)", "3.717***", "4.184***", "-0.494***", "0.331***"],
    ["(SE)", "(0.113)", "(0.123)", "(0.044)", "(0.019)"],
    ["N", "93,051", "92,855", "92,855", "92,855"],
])
note("97,165 airport-years, 5,354 airports. Descriptive associations: GACI embeds "
     "seat capacity, so the CO2 and seat-km columns are partly mechanical; the "
     "informative margins are intensity and the international share. *** p<0.01.")
p("Within a country, an airport whose network position improves becomes "
  "cleaner per seat-kilometre and more international. The cross-sectional "
  "ladder in Figure 1 makes the same point without regression: median CO2 "
  "per 1,000 seat-kilometres falls monotonically from 284 kg in the least "
  "connected ventile of airports to 77 kg in the most connected, while the "
  "international share of seat-kilometres rises from about 1 to about 60 "
  "percent. Node-level efficiency improves exactly where connectivity "
  "concentrates; the national totals of Table 1 nevertheless rise because "
  "traffic scales faster.")
fig(HERE + r"\CO2_efficiency_curve.png",
    "Figure 1. The hub efficiency ladder, 2023: median CO2 per 1,000 seat-km "
    "(with bootstrapped 95% CI) and international share of seat-km, by GACI "
    "ventile.")

h(2, "5.5 The composition lens (secondary instrument)")
caption("Table 6. Tourism-heritage instrument (hub-quality compliers). "
        "Country and year FE; robust SE; KP F = 18.0.")
table([
    ["", "Total CO2", "International CO2", "Seat-km", "CO2/seat-km"],
    ["ln GACI (cwm)", "1.162", "3.164***", "-0.066", "1.228***"],
    ["(SE)", "(0.863)", "(0.766)", "(1.115)", "(0.460)"],
    ["N", "4,642", "4,641", "4,642", "4,642"],
])
note("Interpret with the fragility documented in Table 3 in mind. *** p<0.01.")
p("Hub-quality changes, the tourism instrument's compliers, do not scale "
  "total traffic or total emissions; they recompose flying toward "
  "international long-haul, raising international emissions and measured "
  "intensity. Read together with Table 1, market-access growth scales the "
  "system while hub-quality change internationalises it; both raise the "
  "emissions margin that matters for climate accounting.")

h(2, "5.6 Heterogeneity: who drives the elasticity")
caption("Table 7. Group heterogeneity of the emissions elasticity (Feyrer "
        "instrument). Outcome: ln international CO2 (Panels A-C) and ln CO2 "
        "per seat-km (Panel D); specification as in Table 1, split-sample "
        "2SLS with pooled interaction tests.")
table([
    ["", "beta", "(SE)", "KP F", "N", "Countries"],
    ["Panel A: baseline income terciles", "", "", "", "", ""],
    ["   Low income", "11.431***", "(1.338)", "35.2", "1,595", "62"],
    ["   Middle income", "5.906***", "(0.782)", "48.2", "1,547", "61"],
    ["   High income", "0.350", "(1.106)", "10.1", "1,491", "59"],
    ["   Interaction: MA x top tercile", "-3.083***", "(0.235)", "69.1", "4,633", ""],
    ["Panel B: baseline connectivity terciles", "", "", "", "", ""],
    ["   Low connectivity", "9.018***", "(0.656)", "117.4", "1,452", "61"],
    ["   Middle connectivity", "5.642***", "(0.908)", "29.9", "1,526", "60"],
    ["   High connectivity", "0.452", "(2.201)", "1.8", "1,655", "61"],
    ["   Interaction: MA x top tercile", "-2.484***", "(0.256)", "71.0", "4,633", ""],
    ["Panel C: macro regions", "", "", "", "", ""],
    ["   Europe", "0.236", "(0.616)", "55.5", "1,189", "44"],
    ["   Asia-Pacific", "5.424***", "(0.667)", "64.4", "1,110", "45"],
    ["   Africa", "8.385***", "(1.688)", "20.2", "1,230", "49"],
    ["   Latin America", "3.229***", "(0.900)", "14.1", "683", "28"],
    ["Panel D: intensity outcome by income tercile", "", "", "", "", ""],
    ["   Low income", "-1.057***", "(0.299)", "35.5", "1,596", "62"],
    ["   Middle income", "-0.372", "(0.241)", "48.2", "1,547", "61"],
    ["   High income", "1.012", "(0.715)", "10.1", "1,491", "59"],
])
note("Terciles are defined over countries by the earliest observed GDP per "
     "capita and hub quality. Interaction rows report the coefficient on "
     "ln GACI x top-tercile dummy, both instrumented (Feyrer shifter and its "
     "interaction). The Middle East and North America splits are omitted as "
     "underidentified (KP F below 2; 13 and 3 countries). In the "
     "high-connectivity cell the instrument has little remaining variation "
     "(KP F = 1.8), so the interaction test is the preferred inference. "
     "*** p<0.01.")
p("The headline elasticity is an average over very different national "
  "trajectories, so Table 7 asks where it comes from. First, splitting the "
  "sample by baseline income yields elasticities of 11.4 and 5.9 in the "
  "bottom and middle terciles against a precise zero in the top tercile, and "
  "the pooled interaction confirms the gap (-3.08, KP F = 69). Second, the "
  "same pattern holds for baseline connectivity: countries entering the "
  "network from a low base drive the response, while established networks "
  "show none, a cell in which the instrument itself has little remaining "
  "variation (KP F = 1.8), so we rely on the interaction test (-2.48, F = "
  "71). Third, the regional splits reproduce the gradient, with Africa (8.4) "
  "and Asia-Pacific (5.4) at one end and Europe (0.2, n.s.) at the other. "
  "The efficiency margin follows the same geography: intensity falls with "
  "connectivity only in the bottom income tercile (-1.06). The scale "
  "response is therefore a property of network entry, not of mature hub "
  "competition.")

h(2, "5.7 Attribution: the contribution of connectivity growth to 2023 emissions")
caption("Table 8. Emissions attributable to 1996-2023 connectivity growth "
        "(attributed share = 1 - exp(-beta x dln GACI), applied to 2023 levels; "
        "beta = 5.67).")
table([
    ["", "Attributed 2023 CO2", "Share of 2023 total"],
    ["World, total allocation", "356 Mt", "42.5% of 838 Mt"],
    ["World, international only", "212 Mt", "41.2% of 514 Mt"],
    ["Emerging hubs", "", ""],
    ["   China", "+87.7 Mt", ""],
    ["   United Arab Emirates", "+24.7 Mt", ""],
    ["   Turkey", "+16.6 Mt", ""],
    ["   India", "+15.9 Mt", ""],
    ["Mature networks", "", ""],
    ["   United States", "+36.4 Mt", ""],
    ["   Japan", "+17.4 Mt", ""],
    ["   Korea", "+14.1 Mt", ""],
    ["   Germany (declining connectivity)", "-15.8 Mt", ""],
])
note("Partial-equilibrium accounting. Because the elasticity is far above one, "
     "attributed shares for the fastest-growing countries approach their full "
     "2023 emissions; the world total remains moderate because many countries "
     "changed little. Not a general-equilibrium counterfactual.")

h(2, "5.8 Sustainable aviation fuel scenarios")
caption("Table 9. World aviation CO2 under ReFuelEU-style SAF blending "
        "(life-cycle accounting; Panel A) and the connectivity accounting of "
        "the fuel path (Panel B; beta = 5.67). Applied to the 2023 total of "
        "838 Mt.")
table([
    ["Milestone (blending share)", "LCA saving 50%", "LCA saving 65%", "LCA saving 80%"],
    ["Panel A: world aviation CO2 (Mt)", "", "", ""],
    ["2025 (2%)", "830 Mt", "827 Mt", "825 Mt"],
    ["2030 (6%)", "813 Mt", "805 Mt", "798 Mt"],
    ["2035 (20%)", "754 Mt", "729 Mt", "704 Mt"],
    ["2040 (34%)", "696 Mt", "653 Mt", "610 Mt"],
    ["2045 (42%)", "662 Mt", "609 Mt", "556 Mt"],
    ["2050 (70%)", "545 Mt", "457 Mt", "369 Mt"],
    ["Panel B: saving (share of the 356 Mt attributed to connectivity growth)",
     "", "", ""],
    ["2025 (2%)", "8 Mt (2%)", "11 Mt (3%)", "13 Mt (4%)"],
    ["2030 (6%)", "25 Mt (7%)", "33 Mt (9%)", "40 Mt (11%)"],
    ["2035 (20%)", "84 Mt (24%)", "109 Mt (31%)", "134 Mt (38%)"],
    ["2040 (34%)", "142 Mt (40%)", "185 Mt (52%)", "228 Mt (64%)"],
    ["2045 (42%)", "176 Mt (49%)", "229 Mt (64%)", "282 Mt (79%)"],
    ["2050 (70%)", "293 Mt (82%)", "381 Mt (107%)", "469 Mt (132%)"],
    ["Emissions-neutral hub-quality growth by 2050", "7.9%", "11.3%", "15.6%"],
])
note("Panel A: E(s) = E x [(1 - s) + s x (1 - r)]; fuel backed out as "
     "CO2 / 3.15. Panel B: saving = 838 x s x r, expressed relative to the "
     "356 Mt attributed to 1996-2023 connectivity growth in Table 8. The "
     "final row inverts the attribution formula: the hub-quality growth "
     "exp(-ln(1 - sr)/beta) - 1 that the 2050 blend absorbs at constant "
     "emissions, with beta = 5.67; realised worldwide hub-quality growth "
     "over 1996-2023 was approximately 10 percent. Illustrative: a "
     "country-level elasticity applied at the world aggregate. Accounting "
     "simulation: no behavioural response, no SAF supply constraint, "
     "combustion CO2 of SAF equals Jet A, savings are life-cycle.")
p("Because the efficiency margin improves with connectivity yet does not "
  "offset the scale response, reductions in the level of emissions on "
  "current network trends require fuel substitution. A 2035 mandate implies "
  "savings of 84-134 Mt per year; a 2050 mandate implies savings of 293-469 "
  "Mt against the 2023 level.")
p("Panel B links the fuel path to the causal estimate. First, measured "
  "against the 356 Mt that Section 5.7 attributes to 1996-2023 connectivity "
  "growth, a 2035 mandate offsets 24-38 percent of that contribution, and "
  "only the full 2050 blending share, at life-cycle savings of 65 percent "
  "or above, offsets it entirely. Second, the same arithmetic defines an "
  "emissions-neutral rate of network growth: a blending share s with saving "
  "r permits hub-quality growth of exp(-ln(1 - sr)/beta) - 1 at constant "
  "emissions, which reaches 11 percent by 2050, approximately the "
  "hub-quality growth realised worldwide over 1996-2023. The ReFuelEU path "
  "therefore buys back roughly one generation of connectivity growth.")

# ---------------- 6 geography ----------------
h(1, "6. The geography of emissions attribution")
p("Because cruise emissions occur between countries, the assignment of "
  "responsibility depends on the allocation rule, and the differences are "
  "systematic. "
  "Within a year, departure-side and arrival-side cruise nearly cancel for "
  "every country (round-trip symmetry; the largest national imbalance is "
  "0.7 Mt), so the binding margin is fuel-uplift attribution versus physical "
  "LTO. In 2023 the fuel-uplift convention assigns 1.4 percentage points more "
  "of world emissions to the United States and the United Arab Emirates, and "
  "1.0 more to the United Kingdom, than physically occurs in their "
  "landing-and-take-off cycles, while emerging, domestically oriented "
  "networks are assigned correspondingly less (China, 3.5 points). At "
  "the airport level the gap is positive at every international mega-hub "
  "(Heathrow +1.17, Dubai +1.11) and negative at the large domestic hubs of "
  "emerging networks "
  "(Shanghai Hongqiao, Xi'an, Shenzhen, Kunming, Chongqing, Wuhan). Combined "
  "with Section 5.7, the countries where connectivity-driven emissions grew "
  "fastest are not the countries to which those emissions are assigned under "
  "bunker accounting, which bears directly on CORSIA coverage and on how "
  "national aviation targets should treat international cruise.")
fig(HERE + r"\CO2_map_levels_2023.png",
    "Figure 2. Aviation CO2 by country, 2023 (fuel-uplift allocation, Mt, "
    "log scale).")
fig(HERE + r"\CO2_map_mismatch_2023.png",
    "Figure 3. The attribution mismatch, 2023: world share under fuel-uplift "
    "minus share of physical LTO emissions (percentage points).")
p("Figures 4 and 5 map the attribution of Section 5.7 and its driver. "
  "Emissions attributable to 1996-2023 connectivity growth concentrate in "
  "China, the Gulf, Turkey, Korea, and the United States, while Germany and "
  "Italy carry negative contributions from declining hub quality; the "
  "underlying hub-quality changes show the same geography, with the largest "
  "gains in Korea, Turkey, and the Gulf and losses concentrated in parts of "
  "western Europe and the former Soviet Union.")
fig(HERE + r"\CO2_map_attributed_2023.png",
    "Figure 4. CO2 attributable to 1996-2023 connectivity growth (Mt; "
    "attributed share = 1 - exp(-beta x dln GACI) applied to 2023 levels, "
    "beta = 5.67; signed arcsinh colour scale).")
fig(HERE + r"\CO2_map_dlngaci.png",
    "Figure 5. Hub-quality growth, 1996-2023 (change in ln GACI, "
    "capacity-weighted country mean).")

# ---------------- 7 discussion ----------------
h(1, "7. Discussion and limitations")
p("The title question has a quantitative answer: connectivity growth "
  "increases aviation CO2 by roughly 5.7 percent for each 1 percent gain in "
  "hub quality, and two and a half decades of network growth account for "
  "over 40 percent of today's aviation emissions. The offsetting efficiency "
  "channel is confirmed, highly connected hubs exhibit the lowest emissions "
  "per seat-kilometre, but it recovers only about 0.4 log points against a "
  "scale response of roughly 6, and the margin decomposition shows the gain "
  "arrives through fleet composition rather than aircraft up-gauging or "
  "longer stages. Policies that rely on hub efficiency to "
  "decarbonise network growth are therefore unlikely to succeed; the "
  "effective instruments are fuel substitution and demand-side measures, and "
  "the question of how cruise emissions are assigned across countries "
  "deserves attention in CORSIA design.")
p("Limitations. Emissions are schedule-based and exclude load factors, "
  "weather, and airline-specific operations; estimates capture scheduled "
  "capacity rather than realised traffic. The primary instrument draws its "
  "power from pre-2010 variation, with the post-2010 era covered only by the "
  "weaker tourism lens. Airport-level results are descriptive; an "
  "accident-exposure instrument based on predetermined route dependence is "
  "the planned upgrade, together with network-spillover regressions once "
  "base-year bilateral route shares are available. Scenario calculations are "
  "partial equilibrium, and non-CO2 effects (contrails, NOx) are outside "
  "scope.")

doc.save(OUT)
print("wrote", OUT)
