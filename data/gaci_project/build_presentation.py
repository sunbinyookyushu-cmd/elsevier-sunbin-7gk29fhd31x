# -*- coding: utf-8 -*-
"""Conference deck for the GACI -> trade paper, styled after the UTokyo/BNU seminar
   template (navy + gold, lettered sections, roadmap, takeaway boxes). Opens
   conceptually ("What is GACI?") then builds the index in detail, then trade."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

NAVY  = RGBColor(0x23, 0x2A, 0x55)
NAVY2 = RGBColor(0xBC, 0xC5, 0xDE)     # light text on navy
GOLD  = RGBColor(0xE2, 0xA8, 0x5A)
TEAL  = RGBColor(0x1E, 0x6E, 0x8A)
GREEN = RGBColor(0x2F, 0x6F, 0x3E)
INK   = RGBColor(0x1E, 0x1E, 0x24)
GREY  = RGBColor(0x6E, 0x6E, 0x6E)
CARD  = RGBColor(0xF1, 0xF3, 0xF6)
TAKEBG = RGBColor(0xF2, 0xE9, 0xF7)
TAKEED = RGBColor(0x8E, 0x5B, 0xA6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HEAD  = 'Verdana'      # clean sans for titles
BODY  = 'Calibri'
FOOT  = 'Global Air Connectivity and Trade, 1996–2023'

prs = Presentation()
prs.slide_width  = Inches(13.333); prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]
_content = []   # slides that get footer + page number


def _set(run, size, bold=False, color=INK, font=BODY, italic=False, spacing=None):
    run.font.size = Pt(size); run.font.bold = bold; run.font.italic = italic
    run.font.color.rgb = color; run.font.name = font


def bg(slide, color=WHITE):
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = color


def rect(slide, x, y, w, h, color, line=None):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    if line is None: sp.line.fill.background()
    else: sp.line.color.rgb = line; sp.line.width = Pt(1)
    sp.shadow.inherit = False
    return sp


def spaced(t):
    return ' '.join(list(t))


def header(slide, kicker, title):
    """content-slide header: spaced kicker + gold rule + big title."""
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.32), Inches(12), Inches(0.5))
    p = tb.text_frame.paragraphs[0]; r = p.add_run(); r.text = spaced(kicker.upper())
    _set(r, 12, bold=True, color=NAVY, font=BODY)
    rect(slide, 0.62, 0.78, 1.4, 0.045, GOLD)
    tb2 = slide.shapes.add_textbox(Inches(0.58), Inches(0.92), Inches(12.1), Inches(1.0))
    tf = tb2.text_frame; tf.word_wrap = True
    p2 = tf.paragraphs[0]; r2 = p2.add_run(); r2.text = title
    _set(r2, 28, bold=True, color=INK, font=HEAD)


def bullets(slide, items, left=0.7, top=2.05, width=12.0, size=18, gap=10):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(4.8))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for it in items:
        lvl = 0; txt = it; bold = False; color = INK
        if isinstance(it, tuple):
            txt, lvl = it[0], it[1]
            if len(it) > 2: bold = it[2]
            if len(it) > 3: color = it[3]
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.level = lvl; p.space_after = Pt(gap); p.space_before = Pt(2)
        r = p.add_run(); r.text = ('•  ' if lvl == 0 else '–  ') + txt
        _set(r, size - 2*lvl, bold=bold, color=color)


def takeaway(slide, text, top=6.02, size=17):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.4), Inches(top),
                                 Inches(10.5), Inches(0.78))
    box.fill.solid(); box.fill.fore_color.rgb = TAKEBG
    box.line.color.rgb = TAKEED; box.line.width = Pt(1.25); box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text; _set(r, size, bold=True, color=NAVY)


def caption(slide, text, cx, top, width, size=12.5):
    tb = slide.shapes.add_textbox(Inches(cx), Inches(top), Inches(width), Inches(0.7))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text; _set(r, size, color=GREY, italic=True)


def content_slide(kicker, title):
    s = prs.slides.add_slide(BLANK); bg(s); header(s, kicker, title); _content.append(s)
    return s


def text_slide(kicker, title, items, take=None, **kw):
    s = content_slide(kicker, title); bullets(s, items, **kw)
    if take: takeaway(s, take)
    return s


def fig_slide(kicker, title, path, cap=None, take=None, top=2.0, maxw=11.8, maxh=4.6,
              side_text=None):
    s = content_slide(kicker, title)
    im = Image.open(path); ar = im.height / im.width
    if side_text: maxw = 7.3
    if take: maxh = min(maxh, 3.7)
    w = maxw; h = w * ar
    if h > maxh: h = maxh; w = h / ar
    left = (13.333 - w) / 2 if not side_text else 0.55
    s.shapes.add_picture(path, Inches(left), Inches(top), width=Inches(w))
    if cap:
        cw = max(w, 9.0); cx = (13.333 - cw) / 2 if not side_text else 0.55
        caption(s, cap, cx, top + h + 0.05, cw if not side_text else w)
    if side_text:
        bullets(s, side_text, left=8.1, top=2.1, width=4.9, size=16, gap=8)
    if take: takeaway(s, take)
    return s


def section_divider(num, title, subtitle):
    s = prs.slides.add_slide(BLANK); bg(s, NAVY)
    rect(s, 0.0, 3.05, 0.14, 1.2, GOLD)
    tb = s.shapes.add_textbox(Inches(0.7), Inches(2.55), Inches(11), Inches(2.2))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; r = p.add_run(); r.text = num
    _set(r, 54, bold=True, color=GOLD, font=HEAD)
    p2 = tf.add_paragraph(); r2 = p2.add_run(); r2.text = title
    _set(r2, 32, bold=True, color=WHITE, font=HEAD)
    p3 = tf.add_paragraph(); r3 = p3.add_run(); r3.text = subtitle
    _set(r3, 16, color=NAVY2, italic=True)
    return s


# ======================================================================
# TITLE
# ======================================================================
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
rect(s, 0.0, 0.0, 0.16, 7.5, GOLD)
tb = s.shapes.add_textbox(Inches(0.65), Inches(0.95), Inches(11), Inches(0.4))
p = tb.text_frame.paragraphs[0]; r = p.add_run(); r.text = spaced('CONFERENCE SEMINAR')
_set(r, 12, bold=True, color=NAVY2)
rect(s, 0.67, 1.35, 1.5, 0.05, GOLD)
tb = s.shapes.add_textbox(Inches(0.62), Inches(1.7), Inches(12.0), Inches(1.8))
tf = tb.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; r = p.add_run()
r.text = 'Global Air Connectivity and Trade Openness, 1996–2023'
_set(r, 33, bold=True, color=WHITE, font=HEAD)
tb = s.shapes.add_textbox(Inches(0.65), Inches(3.5), Inches(11.5), Inches(0.6))
p = tb.text_frame.paragraphs[0]; r = p.add_run()
r.text = 'Building a global aviation connectivity index, and estimating its effect on trade'
_set(r, 18, color=NAVY2, italic=True)
rect(s, 0.67, 4.5, 11.5, 0.02, RGBColor(0x44, 0x4D, 0x77))
tb = s.shapes.add_textbox(Inches(0.65), Inches(4.7), Inches(11.5), Inches(1.4))
tf = tb.text_frame
for txt, sz, col, it, first in [
        ('Authors', 17, WHITE, False, True),
        ('Kyushu University, Fukuoka, Japan', 13, NAVY2, True, False),
        ('184 countries · 1996–2023 · two-way fixed-effects 2SLS', 13, NAVY2, True, False)]:
    pp = tf.paragraphs[0] if first else tf.add_paragraph()
    rr = pp.add_run(); rr.text = txt; _set(rr, sz, color=col, italic=it)

# ======================================================================
# TODAY'S TALK
# ======================================================================
s = content_slide("Today's talk", 'What this paper does')
bullets(s, [
    ('We build a new measure of how connected each country is to the world by air, '
     'covering 184 countries from 1996 to 2023.', 0),
    ('We then ask whether that connectivity causally raises a country’s trade, using an '
     'instrument based on tourism and heritage to break reverse causality.', 0),
    ('Two takeaways:', 0, True, NAVY),
    ('connectivity raises trade mostly on the openness (intensity) margin, and', 1),
    ('the payoff is largest for poorer, less-connected economies.', 1),
], top=2.05, size=19, gap=12)
takeaway(s, 'A data contribution (the index) and a causal contribution (the effect on trade).')

# ======================================================================
# ROADMAP
# ======================================================================
s = content_slide('Roadmap', 'Five parts')
cards = [('01', 'Motivation', 'Why connectivity\n& trade'),
         ('02', 'Building GACI', 'What it is and\nhow we build it'),
         ('03', 'Identification', 'Tourism–heritage\nIV'),
         ('04', 'Results', 'Effect, who gains,\nhow much'),
         ('05', 'Conclusion', 'Policy &\nextensions')]
x = 0.62; cw = 2.34; gap = 0.18; cardtop = 2.35; ch = 3.4
for num, ti, sub in cards:
    rect(s, x, cardtop, cw, ch, CARD)
    rect(s, x, cardtop, cw, 0.08, TEAL)
    tb = s.shapes.add_textbox(Inches(x+0.18), Inches(cardtop+0.25), Inches(cw-0.3), Inches(3.0))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; r = p.add_run(); r.text = num; _set(r, 30, bold=True, color=TEAL, font=HEAD)
    p2 = tf.add_paragraph(); p2.space_before = Pt(6); r2 = p2.add_run(); r2.text = ti
    _set(r2, 17, bold=True, color=INK, font=HEAD)
    p3 = tf.add_paragraph(); p3.space_before = Pt(10)
    for j, line in enumerate(sub.split('\n')):
        rr = (p3.add_run() if j == 0 else p3.add_run())
        rr.text = (line + ' '); _set(rr, 12.5, color=GREY)
    x += cw + gap

# ======================================================================
# 01 MOTIVATION
# ======================================================================
section_divider('01', 'Motivation', 'Why air connectivity, and why trade')

text_slide('Motivation', 'Air connectivity shrinks economic distance', [
    ('A country’s position in the world air network sets how near it is, in time and '
     'cost, to markets, suppliers, and partners.', 0),
    ('Among the flows distance impedes (people, capital, ideas, goods), trade responds '
     'most robustly and is observed most cleanly.', 0),
    ('Trade is the proximate, observable margin on which connectivity acts; income is '
     'the distant, confounded end of the chain.', 0),
], top=2.1, size=19, gap=14,
   take='So we study trade: the clearest economic footprint of air access.')

text_slide('Motivation', 'Why connectivity should move trade: two channels', [
    ('1. People who make trade happen', 0, True, NAVY),
    ('Face-to-face contact: buyers meeting sellers, managers inspecting suppliers, the '
     'trust on which trade in differentiated goods relies.', 1),
    ('2. High-value, time-sensitive goods', 0, True, NAVY),
    ('Just-in-time, perishable, high-technology trade; each day in transit costs about '
     '0.6–2.3% ad valorem.', 1),
    ('Air carries a small share of trade by weight but about one third by value.', 1),
], top=2.05, size=18, gap=11)

# ======================================================================
# 02 BUILDING GACI  (starts conceptually)
# ======================================================================
section_divider('02', 'Building GACI', 'What is it, and how do we construct it?')

# concept 1: what is connectivity
text_slide('Concept', 'What is "air connectivity", really?', [
    ('It is not how many airports or routes a country has.', 0),
    ('It is a country’s POSITION in the world air network: how easily, through how many '
     'and how important partners, it can reach everywhere else.', 0, True, NAVY),
    ('Two countries with the same number of routes differ if one connects to global hubs '
     'and the other to dead-ends.', 0),
], top=2.1, size=19, gap=14,
   take='Connectivity = network position, not a simple count.')

# concept 2: how to measure it -> GACI
text_slide('Concept', 'How we measure it: the Global Air Connectivity Index', [
    ('GACI summarises each airport’s position in the weighted world air network as a '
     'single, time-comparable number (Cheung, Wong & Zhang, 2020).', 0),
    ('It blends three ideas:', 0, True, NAVY),
    ('REACH — how many and how well-placed are its connections;', 1),
    ('FLOW — how much passenger traffic moves through it;', 1),
    ('STANDING — how important are the airports it connects to.', 1),
], top=2.05, size=18, gap=11,
   take='One number that captures reach, flow, and standing in the global network.')

# pipeline
fig_slide('Building GACI', 'How the index is built: the pipeline', 'fig_pipeline.png',
          cap='Each step is computed for every year, then aggregated to countries.',
          top=2.9, maxw=12.6, maxh=2.3)

# why index not count
text_slide('Building GACI', 'Why an index, not a simple count', [
    ('Counting airports/routes misses position and ignores second-order spillovers '
     '(partner-of-partner reach).', 0),
    ('A network-centrality index captures position, flow, and reach in one comparable '
     'number, across countries and across 28 years.', 0, True, NAVY),
], top=2.1, size=19, gap=13)

# step 0 data + detail
text_slide('Building GACI', 'Step 0: building a clean weighted network', [
    ('Source: global airline schedule data (route-segment level).', 0),
    ('Keep only scheduled commercial service; exclude military, charter, seaplane, '
     'heliports, and airports that closed in-window.', 0),
    ('Aggregate segments per airport pair per year into one link; set the link weight to '
     'passenger seat capacity.', 0),
    ('Two matrices per year: adjacency A (who connects) and weight W (how much).', 0, True, NAVY),
], top=2.05, size=18, gap=10)

# coverage
fig_slide('Building GACI', 'A long, consistent panel, 1996–2023', 'fig_coverage.png',
          cap='Airports with scheduled service each year. We extend the index from '
              '2006–2016 to a balanced 184-country, 1996–2023 panel.',
          top=2.0, maxw=8.8, maxh=4.4)

# scale-free (paper gr2)
fig_slide('Building GACI', 'The structure we measure: a scale-free network',
          PFIG_GR2 := 'figure/1-s2.0-S1366554519301243-gr2_lrg.jpg',
          cap='Degree distribution (log–log): a few mega-hubs, a long tail of thin '
              'airports. Source: Cheung, Wong & Zhang (2020).',
          top=2.0, maxw=11.0, maxh=4.3)

# centrality I
text_slide('Building GACI', 'Step 1a: topological indicators (position)', [
    ('Degree — number of direct connections (raw reach).', 0),
    ('Closeness — inverse of the average number of hops to reach all others '
     '(accessibility).', 0),
    ('Eigenvector — importance weighted by the importance of neighbours; connecting to '
     'hubs counts more than connecting to spokes.', 0),
], top=2.1, size=19, gap=13)

# centrality II
text_slide('Building GACI', 'Step 1b: volumetric indicators (passenger flow)', [
    ('Flow betweenness — share of passenger "current" transferring through the airport; '
     'the hub / transfer role.', 0),
    ('Regional importance — average connection intensity within its own region.', 0),
    ('These two flow measures make GACI flow-aware, not purely topological.', 0, True, NAVY),
], top=2.1, size=19, gap=13)

# flow betweenness analogy (paper gr1 cropped)
fig_slide('Building GACI', 'Flow betweenness: passengers as electrical current',
          'figure/gr1_crop.jpg',
          cap='Each route is a resistor with resistance inversely proportional to its '
              'passenger intensity; betweenness = current through the node. '
              'Source: Cheung et al. (2020).',
          top=2.0, maxw=9.4, maxh=4.3)

# exact formulas
fig_slide('Building GACI', 'Step 1: the exact formulas', 'fig_eq_centrality.png',
          top=1.95, maxw=10.2, maxh=4.7)

# correlations -> PCA (paper gr11)
fig_slide('Building GACI', 'The five indicators are related but not redundant',
          'figure/1-s2.0-S1366554519301243-gr11_lrg.jpg',
          cap='Pairwise rank correlations 0.71–0.87: each adds information, so we combine '
              'rather than pick one. Source: Cheung et al. (2020).',
          top=1.95, maxw=6.2, maxh=4.7)

# PCA concept
text_slide('Building GACI', 'Step 2: combine the five into one index (PCA)', [
    ('Five indicators, different scales, partly correlated.', 0),
    ('GACI = the first principal component: the single weighted combination capturing '
     'the most variance across airports.', 0, True, NAVY),
    ('It explains about two-thirds of total variance, so one number retains most of the '
     'information.', 0),
], top=2.1, size=19, gap=13)

# PCA formula
fig_slide('Building GACI', 'Step 2: the aggregation formula', 'fig_eq_pca.png',
          top=1.95, maxw=10.2, maxh=4.7)

# PCA loadings (our data)
fig_slide('Building GACI', 'PCA weights, computed on our panel', 'fig_pca_loadings.png',
          cap='First-component loadings on our 1996–2023 data: all positive and similar; '
              'PC1 explains 74% of variance.',
          top=2.0, maxw=9.0, maxh=4.4)

# standardisation
text_slide('Building GACI', 'Making GACI comparable over time', [
    ('A naive yearly PCA would re-scale every year, so scores could not be compared '
     'across years.', 0),
    ('We standardise so rankings WITHIN a year and relative scores ACROSS years are both '
     'preserved.', 0, True, NAVY),
    ('Result: one index that tracks an airport or country up and down the global '
     'hierarchy from 1996 to 2023.', 0),
], top=2.1, size=19, gap=13)

# face validity (paper gr8)
fig_slide('Building GACI', 'Face validity: high GACI = the world’s major hubs',
          'figure/1-s2.0-S1366554519301243-gr8_lrg.jpg',
          cap='GACI tracks passenger volume; the top of the scale is ATL, PEK, DXB, LHR, '
              'HKG, SIN. Source: Cheung et al. (2020).',
          top=2.0, maxw=7.8, maxh=4.4)

# country aggregation choices
text_slide('Building GACI', 'Step 3: from airports to countries, two ways', [
    ('Hub quality = capacity-weighted MEAN (headline): average gateway quality, not '
     'inflated by having many tiny airports.', 0, True, NAVY),
    ('Total connectivity = SUM: overall network footprint, larger for big countries.', 0),
    ('We report both; hub quality is the headline because its first stage is stronger.', 0),
], top=2.1, size=19, gap=13)

# country formula
fig_slide('Building GACI', 'Step 3: the aggregation formulas', 'fig_eq_country.png',
          top=1.95, maxw=10.2, maxh=4.7)

# base map
fig_slide('Building GACI', 'The built index, mapped: connectivity by country, 2023',
          'GACI_base_map.png',
          cap='Total connectivity (country sum), 2023. Yellow = highly connected. '
              'This is the explanatory variable for Part 03.',
          top=2.0, maxw=11.4, maxh=4.5)

# ======================================================================
# 03 IDENTIFICATION
# ======================================================================
section_divider('03', 'Identification', 'Breaking reverse causality')

text_slide('Identification', 'The problem: connectivity is endogenous', [
    ('Airlines add capacity WHERE TRADE IS ALREADY GROWING (reverse causality).', 0),
    ('Routes open lumpily: a coarse proxy for the connectivity that actually changes.', 0),
    ('OLS mixes the true effect with demand-driven entry and measurement error.', 0),
], top=2.1, size=19, gap=14,
   take='We need variation in connectivity unrelated to goods-trade fundamentals.')

fig_slide('Identification', 'A tourism–heritage shift-share instrument', 'fig_eq_iv.png',
          top=1.95, maxw=10.4, maxh=4.7)

fig_slide('Identification', 'First stage: the instrument strongly predicts connectivity',
          'fig_firststage.png',
          cap='Binned partial-residual plot (country + year FE, population removed). '
              'Slope 0.032, Kleibergen–Paap F = 18.0.',
          top=2.0, maxw=8.0, maxh=4.4)

# ======================================================================
# 04 RESULTS
# ======================================================================
section_divider('04', 'Results', 'Effect, who gains, and how much')

fig_slide('Results', 'Connectivity raises trade (IV exceeds OLS)', 'fig_ols_iv.png',
          cap='A one-percent rise in hub quality: openness +1.30%, volume +2.30%, '
              'GDP +1.00% (ns).',
          top=2.0, maxw=8.2, maxh=4.4)

fig_slide('Results', 'The volume effect splits exactly into openness and scale',
          'fig_decomposition.png',
          cap='Identity ln g = ln(g/Y) + ln Y. Openness (intensity) is the headline.',
          top=2.0, maxw=8.0, maxh=4.4)

fig_slide('Results', 'Turning the elasticity into dollars', 'fig_eq_counterfactual.png',
          top=1.95, maxw=10.4, maxh=4.7)

fig_slide('Results', 'Where the gains fall: ~$7.8 trillion of 2023 trade',
          'GACI_implied_map.png',
          cap='≈17% of world trade, 7.4% of world GDP. Concentrated in China, the Gulf, '
              'and East/Southeast Asia.',
          top=2.0, maxw=11.6, maxh=4.5)

fig_slide('Results', 'When and where: Gulf and Asia pull away after 2005',
          'GACI_continent_trend.png',
          cap='Implied gain in trade openness relative to 1996, by continent.',
          top=2.0, maxw=8.8, maxh=4.5)

fig_slide('Results', 'Who gains most: poorer, less-connected economies',
          'GACI_hetero_quartile.png',
          cap='Implied openness elasticity falls monotonically with baseline income and '
              'connectivity: aviation as a convergence lever.',
          top=2.0, maxw=10.6, maxh=4.5)

text_slide('Results', 'Robustness: the design survives four checks', [
    ('Over-identification — heritage as two instruments: Hansen J not rejected '
     '(p = 0.52–0.84); volume 2.18.', 0),
    ('Falsification — adding cultural heritage: Hansen J rejects (p = 0.004).', 0),
    ('Independent instrument — Frankel–Romer/Feyrer geography: volume 2.26; combined, '
     'the two agree (J p = 0.95).', 0),
    ('Timing — identification concentrated post-2010 (pre-2010 first stage F = 0.29).', 0),
], top=2.05, size=18, gap=12)

fig_slide('Results', 'Symmetry: the COVID-19 connectivity collapse', 'GACI_shock_map.png',
          cap='2019→2020: connectivity fell in 140 of 177 countries; implied trade '
              'disruption ~$1.8 trillion, concentrated in major hubs.',
          top=2.0, maxw=11.6, maxh=4.5)

# ======================================================================
# 05 CONCLUSION
# ======================================================================
section_divider('05', 'Conclusion', 'What we learn, and what it implies')

text_slide('Conclusion', 'Summary and policy', [
    ('We build a 184-country, 1996–2023 panel of global aviation connectivity from the '
     'weighted world airport network (five centralities, PCA).', 0),
    ('Using a tourism–heritage IV, connectivity causally raises trade, mainly on the '
     'openness margin.', 0),
    ('Returns are largest for poorer, less-connected economies; large in aggregate '
     '(~$7.8 trillion); symmetric in collapses (COVID-19).', 0),
], top=2.05, size=18, gap=12,
   take='Airport/route investment and liberalisation: concrete trade levers, '
        'highest returns in peripheral economies.')

# thank you
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
rect(s, 0.0, 0.0, 0.16, 7.5, GOLD)
tb = s.shapes.add_textbox(Inches(0.9), Inches(3.0), Inches(11), Inches(1.5))
tf = tb.text_frame
p = tf.paragraphs[0]; r = p.add_run(); r.text = 'Thank you'
_set(r, 40, bold=True, color=WHITE, font=HEAD)
p2 = tf.add_paragraph(); r2 = p2.add_run()
r2.text = 'Global Air Connectivity and Trade Openness, 1996–2023'
_set(r2, 16, color=NAVY2, italic=True)

# ======================================================================
# footer + page numbers on content slides
# ======================================================================
total = len(prs.slides._sldIdLst)
for idx, slide in enumerate(prs.slides, start=1):
    # page number on every slide except the title (idx 1)
    if idx == 1:
        continue
    pn = slide.shapes.add_textbox(Inches(12.2), Inches(7.05), Inches(1.0), Inches(0.35))
    pp = pn.text_frame.paragraphs[0]; pp.alignment = PP_ALIGN.RIGHT
    rr = pp.add_run(); rr.text = f'{idx} / {total}'
    onnavy = slide in []  # dividers/thankyou drawn navy; detect by bg not trivial -> use _content
    _set(rr, 10, color=(GREY if slide in _content else NAVY2))
    if slide in _content:
        rect(slide, 0.62, 7.12, 0.55, 0.05, NAVY)
        ft = slide.shapes.add_textbox(Inches(1.25), Inches(7.0), Inches(8), Inches(0.35))
        fp = ft.text_frame.paragraphs[0]; fr = fp.add_run(); fr.text = FOOT
        _set(fr, 10, color=GREY, italic=True)

prs.save('GACI_presentation.pptx')
print('wrote GACI_presentation.pptx  (%d slides)' % total)
