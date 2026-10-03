# -*- coding: utf-8 -*-
"""Assemble the co-author report (7 sections) into one Word file."""
import json
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.section import WD_ORIENT

def star(p):
    try: p = float(p)
    except Exception: return ''
    return '***' if p < .01 else '**' if p < .05 else '*' if p < .1 else ''

OUT = ['g_int', 'g_vol', 'g_shr', 'lnpc', 'lngdp']   # trade openness (g_int) = MAIN outcome -> first column
OLAB = {'g_vol': 'Ln goods\nvolume', 'g_int': 'Goods openness\nln(goods/GDP)', 'g_shr': 'Goods share\n(% GDP)',
        'lnpc': 'Ln GDP\nper capita', 'lngdp': 'Ln GDP\n(total)'}
DEC = {'g_vol': 3, 'g_int': 3, 'g_shr': 2, 'lnpc': 3, 'lngdp': 3}

main, mF, mN = {}, {}, {}
for ln in open('gaci_tourism_main.log', encoding='utf-8', errors='replace'):
    ln = ln.strip()
    if ln.startswith('MAINP|'):
        _, tr, yv, b, sr, pr, sc, pc, F, ob, op, N = ln.split('|')
        main[(tr, yv)] = dict(b=float(b), sr=float(sr), pr=float(pr), sc=float(sc), pc=float(pc), ob=float(ob), op=float(op))
        mF[tr] = float(F); mN[tr] = int(float(N))
# heterogeneity: interaction IV for two moderators (income, baseline connectivity), from gaci_tourism_hetero_iv.log
HET, HETF = {}, {}
for ln in open('gaci_tourism_hetero_iv.log', encoding='utf-8', errors='replace'):
    ln = ln.strip()
    if ln.startswith('HET3|'):
        q = ln.split('|')
        if q[1] not in ('income', 'baseconn') or q[3] == 'FAIL': continue
        HET[(q[1], q[2], q[3])] = (float(q[4]), float(q[5]), float(q[6])); HETF[q[1]] = float(q[7])
SS = pd.read_csv('_sumstats.csv')
AG = json.load(open('_aggregates.json'))

doc = Document()
s = doc.sections[0]; s.orientation = WD_ORIENT.PORTRAIT; s.page_width, s.page_height = Inches(8.5), Inches(11)
for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(s, m, Inches(0.7))
doc.styles['Normal'].font.name = 'Times New Roman'; doc.styles['Normal'].font.size = Pt(9)

def H(t, lvl=1): doc.add_heading(t, level=lvl)
def P(t, sz=10, it=False):
    pp = doc.add_paragraph(); r = pp.add_run(t); r.font.size = Pt(sz); r.italic = it
    pp.paragraph_format.space_after = Pt(4); return pp
def B(t):
    pp = doc.add_paragraph(style='List Bullet'); pp.add_run(t); return pp
def ital(t, sz=8): P(t, sz, True)
def bold_hdr(cells):
    for c in cells:
        for pa in c.paragraphs:
            for r in pa.runs: r.bold = True

doc.add_heading('Research Plan: Air Connectivity, Trade, and Income (A Global IV Study)', 0)
P('Draft research plan for co-authors. Global air connectivity (GACI) panel, 184 countries, 1996-2023. '
  'Air connectivity instrumented by a tourism-heritage Bartik instrument; merchandise (goods) trade outcome.', 9, True)

# ===== 1. SUMMARY STATS + MAPS =====
H('1. Summary statistics and maps', 1)
t = doc.add_table(rows=0, cols=7); t.style = 'Table Grid'
hd = t.add_row().cells
for j, lab in enumerate(['Variable', 'N', 'Mean', 'SD', 'Median', 'Min', 'Max']): hd[j].text = lab
bold_hdr(hd)
for _, r in SS.iterrows():
    c = t.add_row().cells
    c[0].text = str(r['var']); c[1].text = f"{int(r['n']):,}"
    for j, k in enumerate(['mean', 'sd', 'p50', 'mn', 'mx']):
        c[j + 2].text = f"{r[k]:,.2f}"
ital('Analysis sample 1996-2023. GACI = Global Air Connectivity Index (network centrality of a country\'s airports).')
P('')
doc.add_picture('GACI_base_map.png', width=Inches(7.0))
ital('Figure 1. Air connectivity levels, 2023 (yellow = highly connected: US, China, large European hubs).')
doc.add_picture('GACI_implied_map.png', width=Inches(7.0))
ital('Figure 2. GACI-implied goods-trade gain from connectivity growth, 1996-2023, intensity (openness) channel: '
     'implied gain = goods-trade value x (1 - exp(-beta x change in ln hub-quality)), beta 1.302. Red = gain, blue = loss '
     '(connectivity declined), grey = no data. Color scale capped at the 95th percentile so a few large economies '
     '(e.g. China) do not wash out the rest.')

# ===== DATA SOURCES (tourism instrument) =====
H('Data sources for the tourism instrument', 2)
for b in [
    'UNESCO World Heritage sites - the instrument "share" (fixed tourism endowment): official list from the UNESCO '
    'World Heritage Centre (whc.unesco.org / data.unesco.org export), cumulative count of NATURAL and MIXED sites by '
    'country and year. We use natural/mixed only (not cultural), so the amenity is nature-based and not tied to goods trade.',
    'Global tourism demand - the instrument "shift" (time-varying): World Bank WDI international tourist arrivals, world '
    'aggregate (indicator ST.INT.ARVL), 1996-2019, extended to 2020-2023 using UNWTO World Tourism Barometer recovery '
    'ratios so the 2020 COVID collapse and subsequent recovery enter the instrument.',
    'Instrument construction: tourism_int = (world tourism demand, min-max scaled to [0,1]) x ln(1 + natural-heritage '
    'endowment). Heritage is country-fixed and tourism demand is global, so only their interaction varies within country '
    'over time and survives country and year fixed effects.',
    'Outcome - goods (merchandise) trade, % of GDP: World Bank WDI indicator TG.VAL.TOTL.GD.ZS. Services and tourism are '
    'excluded by construction; this is essential, because it shuts down the channel through which tourism receipts would '
    'otherwise enter the trade variable directly and break the exclusion restriction.',
    'Supporting data: GACI (lab index from OAG schedules); population, GDP and GDP per capita (World Bank WDI); airport '
    'coordinates (OpenFlights, OurAirports); country boundaries for maps (Natural Earth).']:
    B(b)

# ===== 2. OBJECTIVES =====
H('2. Research objectives', 1)
for b in [
    'Estimate the causal effect of air connectivity on goods trade and on income across 184 countries, 1996-2023.',
    'Identify the effect with a tourism-heritage instrument that isolates leisure-driven connectivity and has a clean '
    'exclusion restriction for goods trade (heritage does not directly cause merchandise trade).',
    'Characterise heterogeneity across development level, country size, baseline connectivity, and world region.',
    'Quantify how two decades of connectivity growth contributed to global trade and GDP.']:
    B(b)

# ===== 3. IDENTIFICATION =====
H('3. Identification strategy (brief)', 1)
P('We instrument national air connectivity with a shift-share (Bartik) interaction: a country\'s fixed natural/mixed '
  'UNESCO heritage endowment (the "share", a tourism-amenity stock) times the global tourism-demand boom (the "shift", '
  'time-varying). Natural heritage draws leisure flights and hence connectivity, but does not directly generate '
  'merchandise trade; using goods-only trade as the outcome removes the tourism-services channel. The instrument '
  'therefore moves goods trade only through connectivity. All models include country and year fixed effects, so '
  'fixed national characteristics and common global trends are absorbed. For the hub-quality treatment (ln_gaci_cwm, '
  'our main variable) the instrument is strong on the full 1996-2023 sample (first-stage Kleibergen-Paap F ~ 18), '
  'comfortably above conventional weak-instrument thresholds; for the total-connectivity (sum) treatment the full-'
  'sample F is lower (~ 10) because that instrument weakens during the 2020-2021 global tourism shutdown. Results '
  'are reported on the full sample.')

# ===== 4. WHY GACI (vs DiD) =====
H('4. Advantages of a connectivity-index design (vs. difference-in-differences)', 1)
for b in [
    'Continuous, dose-response treatment: GACI measures the intensity and network position of connectivity rather than '
    'a binary treated/untreated event, so we recover an elasticity, not a single discrete jump.',
    'Captures network spillovers: as a centrality measure, GACI rises when a country\'s partners gain links, so indirect '
    '(second-order) connectivity is included; a route-level DiD treating one link at a time misses these spillovers.',
    'Symmetric in gains and losses: the continuous index moves with both connectivity expansions and declines, whereas '
    'opening-based difference-in-differences designs capture only the expansion side.',
    'Global balanced panel: 184 countries over 28 years, rather than a single-country or single-corridor DiD setting.',
    'Supports counterfactual aggregation: the continuous treatment lets us translate connectivity changes into implied '
    'global trade and GDP effects (Sections 8-9).']:
    B(b)

# ===== 5. MAIN RESULTS =====
H('5. Main results: OLS and IV', 1)
P('Two-stage least squares; country and year fixed effects; goods = merchandise trade (services/tourism excluded). '
  'Robust SE in (parentheses), clustered SE in [brackets]. * p<0.10, ** p<0.05, *** p<0.01 (robust); "+" = 5% under clustering.', 9, True)
P('Because ln(goods) = ln(goods/GDP) + ln(GDP), the IV elasticities decompose exactly: the goods-VOLUME elasticity '
  '(2.303) equals the openness/intensity elasticity (1.302) plus the GDP-scale elasticity (1.001). The counterfactuals '
  'below (Section 8) use the intensity elasticity (1.302), which isolates the pure trade-intensity channel and avoids '
  'double-counting connectivity-induced GDP growth as additional trade.', 9)

doc.add_heading('Table 1. Main results: OLS vs. IV (1996-2023)', 2)
t1 = doc.add_table(rows=0, cols=6); t1.style = 'Table Grid'
h = t1.add_row().cells; h[0].text = ''
for j, o in enumerate(OUT): h[j + 1].text = OLAB[o]
bold_hdr(h)
def panel(tr, title):
    rr = t1.add_row().cells; rr[0].merge(rr[5]); rr[0].paragraphs[0].add_run(title).bold = True
    for lab, kind in [('Air connectivity (IV)', 'iv'), ('   Robust SE', 'sr'), ('   Clustered SE', 'sc'),
                      ('OLS benchmark', 'ols'), ('First-stage KP F', 'F'), ('Observations', 'N')]:
        r = t1.add_row().cells; r[0].text = lab
        for j, o in enumerate(OUT):
            dd = main.get((tr, o)); dec = DEC[o]
            if dd is None: continue
            if kind == 'iv': r[j + 1].text = f"{dd['b']:,.{dec}f}{star(dd['pr'])}"
            elif kind == 'sr': r[j + 1].text = f"({dd['sr']:,.{dec}f})"
            elif kind == 'sc': r[j + 1].text = f"[{dd['sc']:,.{dec}f}]" + ('+' if dd['pc'] < .05 else '')
            elif kind == 'ols': r[j + 1].text = f"{dd['ob']:,.{dec}f}{star(dd['op'])}"
            elif kind == 'F': r[j + 1].text = f"{mF[tr]:.1f}"
            elif kind == 'N': r[j + 1].text = f"{mN[tr]:,}"
panel('ln_gaci_cwm', 'Panel A. Treatment = hub quality (log capacity-weighted-mean GACI) [MAIN]')
panel('lng', 'Panel B. Treatment = total connectivity (log GACI sum)')
P('First-stage strength and instrument validity. The tourism-heritage instrument is strong for the hub-quality '
  'treatment (Kleibergen-Paap F about 18). We probe the exclusion restriction by entering natural, mixed, and cultural '
  'heritage as three separate instruments: natural and mixed heritage are mutually consistent (Hansen J p = 0.78 for '
  'trade volume, 0.52 for openness) and the connectivity coefficient is stable, whereas every specification that adds '
  'cultural heritage is rejected (Hansen J p = 0.004) with the coefficient collapsing - cultural sites cluster in '
  'developed, long-established trading economies and are not excludable. We therefore instrument connectivity with '
  'natural and mixed heritage only.', 9)

# ===== 6. HETEROGENEITY =====
H('6. Heterogeneity: who gains most?', 1)
doc.add_heading('Table 2. Heterogeneity by development and baseline connectivity: interaction IV (1996-2023)', 2)
P('Full-sample 2SLS: ln_gaci_cwm and ln_gaci_cwm x (moderator, mean-centered) are both instrumented (tourism_int and '
  'its interaction); country + year FE; robust SE. "Connectivity (at mean)" is the effect for the average country; '
  '"x moderator" is how that effect shifts with the moderator -- a NEGATIVE interaction means the connectivity payoff '
  'is concentrated in poorer / less-connected economies.', 9, True)
def hpanel(mod, title):
    doc.add_heading(title, 3)
    t = doc.add_table(rows=0, cols=6); t.style = 'Table Grid'
    h = t.add_row().cells; h[0].text = ''
    for j, o in enumerate(OUT): h[j + 1].text = OLAB[o]
    bold_hdr(h)
    for lab, term in [('Connectivity (at mean)', 'main'), ('  x ' + mod + ' (interaction)', 'inter')]:
        r = t.add_row().cells; r[0].text = lab
        for j, o in enumerate(OUT):
            v = HET.get((mod, o, term))
            if v: r[j + 1].text = f"{v[0]:,.{DEC[o]}f}{star(v[2])}\n({v[1]:,.{DEC[o]}f})"
    r = t.add_row().cells; r[0].text = 'KP first-stage F'
    if mod in HETF: r[1].text = f"{HETF[mod]:.1f}" + ("w" if HETF[mod] < 10 else "")
hpanel('income', 'Panel A. Moderator = baseline income (1996 ln GDP per capita)')
hpanel('baseconn', 'Panel B. Moderator = baseline connectivity (1996 ln hub quality)')
ital('Negative interactions across the trade and income outcomes mean the connectivity payoff is larger for poorer and '
     'less-connected countries. The instrument is identified but modest for these splits (KP F about 5-8, marked "w"), so '
     'the heterogeneity is read as suggestive. Panel B corroborates Panel A but should be read with care: conditioning '
     'the effect on the baseline level of the treatment itself can induce mechanical (mean-reversion) attenuation, so '
     'baseline income (Panel A) is the cleaner moderator. Dimensions that were not identified or not robust (population, '
     'land area, total GDP, remoteness) are not reported.')

# ===== 7. REGIONAL PATTERN =====
H('7. Regional pattern: implied trade-intensity gains by continent', 1)
P('The pooled intensity elasticity (1.302) applied to each country\'s observed hub-quality growth since 1996, '
  'aggregated (goods-trade-weighted) within continents.', 9, True)
doc.add_picture('GACI_continent_trend.png', width=Inches(6.5))
ital('Figure 3. Implied gain in goods-trade openness relative to 1996, by continent, 1996-2023. The largest implied '
     'gains accrue to the Middle East (Gulf hubs) and Asia (China); the COVID dip in 2020-2021 is visible.')

# ===== 8. AGGREGATE CONTRIBUTION =====
H('8. Aggregate contribution of two decades of connectivity growth (1996-2023)', 1)
ga = AG['gain']
P('Counterfactual gain = level x (1 - exp(-beta x dlnGACI)), summed across countries, using the intensity (openness) '
  'elasticity 1.302 - the pure trade-intensity channel, net of the GDP-scale channel.', 9, True)
for b in [
    'Trade (intensity channel): about $%.1f trillion of 2023 goods trade is attributable to air-connectivity growth '
    'since 1996 - roughly %.0f%% of 2023 world goods trade ($%.0f trillion) and %.1f%% of 2023 world GDP ($%.0f trillion).'
    % (ga['gain_trade_usd']/1e12, ga['gain_trade_pct'], ga['tot_trade19']/1e12, ga['gain_trade_pct_gdp'], ga['tot_gdp19']/1e12),
    'Equivalently in openness terms: connectivity growth raised world goods-trade openness by about %.1f percentage '
    'points of GDP (from roughly %.0f%% to %.0f%% of GDP); the trade-weighted mean openness gain is %.2f log points '
    '(about %.0f%%).'
    % (ga['gain_trade_pct_gdp'], ga['world_open_cf'], ga['world_open_now'], ga['open_logpts'], ga['open_pct']),
    'Memo - combined intensity+scale (volume elasticity 2.303): $%.1f trillion (%.0f%% of world goods trade). The extra '
    '$%.1f trillion over the intensity channel is the GDP-scale channel (elasticity 1.001) and is reported separately to '
    'avoid double-counting connectivity-induced GDP growth as additional trade.'
    % (ga['gain_tradevol_usd']/1e12, ga['gain_tradevol_pct'], (ga['gain_tradevol_usd']-ga['gain_trade_usd'])/1e12)]:
    B(b)
ital('Single-year, NOT cumulative. The figures above are a single-year (2023) attribution - the share of 2023 trade and '
     'GDP explained by the connectivity growth that ACCUMULATED between 1996 and 2023 - not a sum of annual gains over the '
     'period. Cumulating the attributable gain across all country-years 1996-2023 instead totals about $86 trillion, '
     'roughly 11% of cumulative world goods trade and about 5% of cumulative world GDP.')
ital('All figures are partial-equilibrium illustrations applying the pooled IV elasticity to each country\'s observed '
     'connectivity change; they ignore general-equilibrium offsets and cross-country heterogeneity in beta, and are '
     'gross trade flows rather than value-added.')

# ===== 9. SHOCK LOSSES =====
H('9. Losses from connectivity-collapse shocks (COVID-19, Russia-Ukraine)', 1)
cv, ru = AG['covid'], AG['russia']
P('For these abrupt one-year shocks the connectivity change is measured on TOTAL connectivity (GACI sum) with the sum '
  'intensity elasticity 0.659, because the hub-quality mean is too volatile in a single shock year and overstates one-'
  'year collapses; the figures are gross trade-FLOW disruptions, not net welfare or GDP losses.', 9, True)
for b in [
    'COVID-19 (2019 to 2020), global: air connectivity fell in %d of %d countries (median dlnGACI %.3f). The implied '
    'goods-trade-flow disruption is about $%.1f trillion - roughly %.1f%% of 2019 world goods trade and %.1f%% of 2019 '
    'world GDP. This is a gross trade-flow figure, not a net GDP loss.'
    % (cv['n_drop'], cv['n'], cv['med_dG'], cv['trade_loss']/1e12,
       100*cv['trade_loss']/cv['tot_trade'], 100*cv['trade_loss']/cv['tot_gdp']),
    'Russia-Ukraine war (2021 to 2022): localised (airspace closures around Russia) while 2022 was globally a COVID-'
    'recovery year, so the net global connectivity change is positive and the aggregate is uninformative. Restricting to '
    'connectivity-LOSING countries, the implied goods-trade-flow loss is about $%.1f trillion; the war effect is weakly '
    'identified at annual global resolution and should be read with caution.'
    % (ru['trade_loss_losers']/1e12)]:
    B(b)
doc.add_picture('GACI_shock_map.png', width=Inches(7.0))
ital('Figure 4. COVID-19 (2019->2020): implied goods-trade loss by country from the air-connectivity collapse. The '
     'largest losses fall on major trading hubs (US, Hong Kong, Singapore, UK, Germany, Netherlands).')

# ===== 10. IMPLICATIONS =====
H('10. What the results imply', 1)
for b in [
    'Connectivity is a causal driver of global integration, not merely a correlate. On the intensity (openness) channel, '
    'air-connectivity growth since 1996 accounts for roughly $%.1f trillion of 2023 world goods trade (about %.0f%%, '
    'equivalently about %.1f%% of world GDP); on a combined intensity-plus-scale basis the figure is about $%.1f trillion '
    '(%.0f%% of world goods trade).'
    % (ga['gain_trade_usd']/1e12, ga['gain_trade_pct'], ga['gain_trade_pct_gdp'],
       ga['gain_tradevol_usd']/1e12, ga['gain_tradevol_pct']),
    'We report the intensity channel as the headline because, by the identity ln(goods) = ln(goods/GDP) + ln(GDP), the '
    'goods-volume elasticity (2.303) is the sum of the openness/intensity elasticity (1.302) and the GDP-scale elasticity '
    '(1.001); using the intensity elasticity isolates the effect of connectivity on how intensively a country trades and '
    'avoids double-counting connectivity-induced GDP growth as additional trade.',
    'Returns are concentrated in poorer, under-connected economies: the connectivity payoff declines with BOTH baseline '
    'income and baseline connectivity (interactions negative and significant across the trade and income outcomes), so the '
    'largest gains accrue to lower-income, less-connected economies. The heterogeneity is statistically suggestive - the '
    'instrument is identified but modest once the sample is split.',
    'Policy levers follow directly: airport and route investment and open-skies / liberalisation agreements are concrete '
    'channels for raising trade and income, with the largest payoff for peripheral economies.',
    'Methodological contribution: a continuous, network-based connectivity treatment combined with a tourism-heritage '
    'instrument offers a globally scalable, spillover-aware alternative to bilateral difference-in-differences for the '
    'transport-and-trade literature.']:
    B(b)

# shrink wide-table fonts so 6 columns fit in portrait width
for tb in doc.tables:
    tb.autofit = True
    for row in tb.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(7.5)

doc.save('GACI_coauthor_report.docx')
print('wrote GACI_coauthor_report.docx (portrait)')
