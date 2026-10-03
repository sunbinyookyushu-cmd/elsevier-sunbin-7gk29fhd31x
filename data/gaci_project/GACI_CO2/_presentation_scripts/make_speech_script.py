# -*- coding: utf-8 -*-
"""Build the spoken presentation script docx for GACI_CO2_presentation.pptx (62 slides).
Output: ..\..\GACI_CO2_presentation_script.docx  (i.e., the GACI folder, next to the pptx)
Rerun after editing SLIDES below."""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "GACI_CO2_presentation_script.docx"))

# (slide_no, footer_page, section, title, minutes, [paragraphs]) ; paragraphs starting with ">>" are stage directions
SLIDES = [
(1, "1/61", "OPENING", "Title", "0:30", [
 ">> Deck on title slide. Smile, wait for the room to settle.",
 "Good afternoon, everyone. Thank you for coming. My name is Sunbin Yoo, from Sungkyunkwan University, and this is joint work with Jinwoo Lee at KAIST and Yifu Ou at the University of Hong Kong.",
 "The title is a question: how much does air connectivity increase aviation CO2? By the end of the hour you will have one number to take home, and the number is 5.7. Let me show you where it comes from and why it matters.",
]),
(2, "2/61", "BACKGROUND", "First: what is transportation economics?", "1:30", [
 ">> For the non-specialists in the room; skip if the audience is all transport people.",
 "Before the paper, thirty seconds of context, because this is a mixed audience. Transportation economics is the economics of moving people and goods: how mobility is demanded, supplied, priced, and built. The core questions are which roads, rails, and airports are worth building, how to price them, and what they cost society beyond the ticket: congestion, accidents, noise, and emissions.",
 "The central insight of the field is that transport is a derived demand. Nobody flies for the pleasure of sitting in seat 32E. We fly because something valuable is at the other end. So the field always asks two things at once: what is a connection worth, and who pays its full cost. Keep that pair in mind; the whole talk is one connection, valued and then billed.",
]),
(3, "3/61", "BACKGROUND", "And transportation and energy economics?", "1:30", [
 "This talk sits in the intersection of transport and energy economics. Transport runs almost entirely on energy, and mostly on oil. The field studies how transport choices and infrastructure drive energy use and emissions, and how to decarbonise mobility without losing the access benefits.",
 "Three facts frame today. Transport is about a quarter of global energy-related CO2. Aviation is two to three percent of global CO2 and growing. And, crucially, aviation has no near-term electrification path: you cannot put a battery in a long-haul aircraft. So today a network investment, connectivity, meets an energy outcome, jet fuel burned. That is exactly the intersection.",
]),
(4, "4/61", "OPENING", "The hook: 42.5%", "1:00", [
 ">> Pause after the number appears. Let it land.",
 "Here is the headline before the methods. Forty-two point five percent of the world's 2023 aviation CO2 traces to connectivity growth since 1996. That is 356 million tonnes of CO2, an external cost of roughly 18 to 68 billion dollars, every single year the traffic persists.",
 "This talk is about where that number comes from, how seriously you should take it causally, and what could change it.",
]),
(5, "5/61", "OPENING", "What this paper does", "1:30", [
 "Concretely, the paper does two things. First, a data contribution: we compute CO2 for every scheduled flight in the world, stage by stage, taxi to cruise to landing, for more than six thousand airports, from 1996 to 2023.",
 "Second, a causal contribution: we ask, when a country becomes better connected by air, how much does its aviation CO2 rise? The answer is: much more than proportionally. A one percent gain in connectivity raises national aviation CO2 by 5.7 percent.",
 "And we finish with the bill: who owes it, where it is booked, and the one policy lever that actually moves the level.",
]),
(6, "6/61", "OPENING", "One index, two ledgers", "1:30", [
 "Some of you have seen our companion paper on trade. Same countries, same connectivity index, same instrumental-variable logic. That paper found the benefit: a one percent rise in hub quality raises trade openness by 1.3 percent, which values 2023 connectivity at about 7.8 trillion dollars of trade, 17 percent of the world total.",
 "This paper prices the bill on the same ledger: the same one percent raises aviation CO2 by 5.67 percent, 356 megatonnes in 2023, 18 to 68 billion dollars per year. The benefit and the bill, measured with the same ruler. That symmetry is the point of the pair.",
]),
(7, "7/61", "OPENING", "Roadmap", "0:45", [
 "Seven parts. Motivation. The emissions data, CO2 for every scheduled flight. Building the connectivity index, and I will spend real time here because the index is the treatment. Identification, a geography instrument. Results, the elasticity and its anatomy. The carbon bill: attribution, mismatch, and sustainable aviation fuel. And a short conclusion. Feel free to interrupt throughout; this is a seminar.",
]),
(8, "8/61", "MOTIVATION", "Section divider: Motivation", "0:10", [
 ">> Click through, one line only.",
 "Part one: why this question.",
]),
(9, "9/61", "MOTIVATION", "Everyone wants connectivity; nobody priced the carbon", "1:30", [
 "Every government wants connectivity. Routes are subsidised, airports expanded, air-service agreements signed, all on the premise that connectivity raises trade, tourism, and productivity. And the premise is right; our companion paper confirms it causally.",
 "But aviation is among the hardest transport sectors to decarbonise. There is no near-term electrification path, and international emissions are booked under separate bunker conventions, outside national inventories, largely outside carbon pricing.",
 "So we have a policy area where the benefit side is celebrated and quantified, and the carbon side is essentially unpriced and, causally, unmeasured. The carbon consequence of connectivity policy is a first-order question with no causal answer. Until now.",
]),
(10, "10/61", "MOTIVATION", "Three empirical questions", "1:30", [
 "Three questions structure the paper. First, proportionality: does a one percent gain in connectivity raise emissions by more or less than one percent? This is genuinely not obvious, because hubs consolidate traffic into fewer, fuller, more efficient movements. Efficiency could in principle win.",
 "Second, incidence: whose emissions respond, poor or rich countries, and does the response spill across borders through the network?",
 "Third, accounting: are emissions booked where they are generated? International aviation follows bunker conventions, not territory.",
 "Magnitude, geography, and bookkeeping. All three turn out to matter.",
]),
(11, "11/61", "DATA", "Section divider: Data", "0:10", [
 "Part two: the emissions data.",
]),
(12, "12/61", "DATA", "Carbon for every flight, stage by stage", "1:30", [
 "The source is OAG schedules: every scheduled commercial flight on Earth, January 1996 to June 2024. For each flight we apply the EEA/EMEP Guidebook: fuel burn by engine type and stage length, times 3.15 kilograms of CO2 per kilogram of Jet A.",
 ">> Walk along the flight-phase strip on the slide.",
 "Each flight is decomposed into phases: taxi-out, take-off, climb, cruise, approach, taxi-in. The landing-and-take-off phases are about twelve percent of CO2; cruise is roughly 88 percent. We keep the departure and arrival sides separate.",
 "Why the fuss? Because emissions are stage-resolved once, they can be aggregated under any allocation rule, with no double counting. That flexibility pays off later, twice.",
]),
(13, "13/61", "DATA", "Validation: does it add up?", "1:00", [
 "Does a bottom-up calculation like this add up? Almost to the tonne. Our 2019 world total is 0.919 gigatonnes against ICCT's 0.92. Country by country, year by year, the log-log correlation with the OWID and ICCT series is 0.99. Our LTO share, 11.8 percent, sits right in the standard range.",
 "The panel: over six thousand airports with stage-resolved monthly CO2, 184 countries, 4,634 country-years. One caveat to flag honestly: this is schedule-based capacity, not load factors. It is the carbon content of the network itself, and I will come back to that in the limitations.",
]),
(14, "14/61", "DATA", "Three allocation rules", "1:00", [
 "Whose emissions are they? Three answers, one dataset. Territorial: each landing and take-off booked at its own airport; physical and local. Bunker, our headline: cruise assigned to the departure country, which is the IEA fuel-uplift convention. And a fifty-fifty split of cruise between the endpoints.",
 "Spoiler, so you do not worry about it for the next half hour: the elasticity barely moves across all three, 5.62 to 5.92. The result is not an accounting artefact.",
]),
(15, "15/61", "DATA", "Map: where aviation CO2 lives, 2023", "0:45", [
 ">> Give the room a few seconds on the map.",
 "This is the outcome variable: national aviation CO2 under the bunker convention in 2023. The United States and China dominate, then the big hub economies. Keep the geography in mind; we will come back to it with a very different colouring at the end.",
]),
(16, "16/61", "GACI", "Section divider: Building GACI", "0:10", [
 "Part three: the index. This is the treatment variable, so bear with me; the details matter.",
]),
(17, "17/61", "GACI", "What is air connectivity, really?", "1:00", [
 "First, what connectivity is not: it is not how many airports or routes a country has. It is a country's position in the world air network: how easily, through how many and how important partners, it can reach everywhere else.",
 "A Korean example makes it concrete. Incheon and Yangyang both have 'international' in their names. Incheon plugs into the global hub network; Yangyang has a handful of point-to-point routes. Connectivity is network position, not a count.",
]),
(18, "18/61", "GACI", "The Global Air Connectivity Index", "1:00", [
 "Our measure is the Global Air Connectivity Index, GACI, following Cheung, Wong and Zhang, 2020. It summarises each airport's position in the weighted world air network as a single, time-comparable number.",
 "It blends three ideas. Reach: how many, and how well-placed, are your connections. Flow: how much passenger traffic actually moves through you. Standing: how important are the airports you connect to. One number, three ingredients.",
]),
(19, "19/61", "GACI", "The pipeline", "0:45", [
 ">> Point along the pipeline figure left to right.",
 "Here is the whole pipeline from raw schedules to one number per airport per year: build the network, compute five centrality indicators, combine them by principal components, standardise over time, aggregate to countries. Each step is computed for every year. In the trade paper this fed the trade regressions; today it feeds CO2.",
]),
(20, "20/61", "GACI", "The raw data: OAG schedules", "0:45", [
 "This is what the raw material looks like: OAG airline schedules at the route-segment level, every scheduled commercial flight, 1996 to mid-2024. From each segment we take two things: a connected dummy, does this pair connect, and total seat capacity, which becomes the link weight.",
]),
(21, "21/61", "GACI", "Step 0: a clean weighted network", "1:00", [
 "Step zero, cleaning. We keep only scheduled commercial service; military, charter, seaplanes, heliports, and airports that closed within the window are excluded. Segments are aggregated to one link per airport pair per year, weighted by seat capacity.",
 "That gives two matrices per year: an adjacency matrix, who connects, and a weight matrix, how much. The slide shows the Korean corner of the matrix, and a fun fact: Gimpo to Jeju alone is the busiest air route in the world.",
]),
(22, "22/61", "GACI", "Step 1a: topological indicators", "1:00", [
 "From the network we compute five indicators; first the positional ones. Degree: the number of direct connections, raw reach. Closeness: the inverse of the average number of transfers needed to reach every other airport, accessibility. Eigenvector centrality: how connected am I to big airports.",
 "The toy network on the slide is domestic Korea. Note Yangyang: its one friend is a big hub, but one friend is still one friend. That is what eigenvector sees and degree misses.",
]),
(23, "23/61", "GACI", "Step 1b: volumetric indicators", "1:00", [
 "Position alone is not enough, so two flow measures. Flow betweenness: the share of passengers transferring through the airport, the hub role; transfers concentrate at Incheon, not Gimpo. Regional importance: average connection intensity within the airport's own region; there Gimpo beats Incheon, because Gimpo is the domestic backbone.",
 "Position says where you sit; flow says how much actually moves through you. These two make GACI flow-aware, not purely topological.",
]),
(24, "24/61", "GACI", "Five indicators, read through Korean airports", "1:00", [
 "Put the five together through Korean airports. Incheon: a global gateway, strong on every margin. Gimpo and Jeju: enormous traffic, the world's busiest route, but little global position; volume is not connectivity. Yangyang: connected on paper only.",
 "Five airports, five different network stories. No single indicator captures them all, which is exactly why we combine all five.",
]),
(25, "25/61", "GACI", "Flow betweenness as electrical current", "0:45", [
 "For intuition on the least familiar indicator: think of passengers as electrical current. Each route is a resistor, with resistance inversely proportional to passenger intensity; an airport's betweenness is the current flowing through it. Incheon plays this Hong Kong-style bridge role between North America and Southeast Asia.",
]),
(26, "26/61", "GACI", "Step 1: the exact formulas", "0:30", [
 ">> Do not read the formulas; gesture and move on.",
 "For completeness, the exact formulas for the five indicators. They are in the paper; I will not walk through them here, but happy to in questions.",
]),
(27, "27/61", "GACI", "Related but not redundant", "0:45", [
 "Are five indicators four too many? Pairwise rank correlations run 0.71 to 0.87: high enough to be one underlying concept, low enough that each adds information. So we combine rather than pick a favourite.",
]),
(28, "28/61", "GACI", "Step 2: PCA", "1:00", [
 "The combination is principal components. Five indicators, different scales, partly correlated; GACI is the first principal component, the single weighted combination capturing the most variance across airports. On our 1996 to 2023 panel, the first component explains 74 percent of total variance, so one number retains most of the information, with no arbitrary weights chosen by us.",
]),
(29, "29/61", "GACI", "Step 2: the aggregation formula", "0:20", [
 ">> Flash slide; move on quickly.",
 "The formula, for the record.",
]),
(30, "30/61", "GACI", "PCA weights on our panel", "0:45", [
 "And the actual loadings computed on our data: all five load positively and with similar magnitudes. No single indicator dominates the index; it really is a blend.",
]),
(31, "31/61", "GACI", "Comparable over time", "0:45", [
 "One technical point that matters enormously here: a naive year-by-year PCA would re-scale every year, so scores could not be compared across years. We standardise so that rankings within a year and relative scores across years are both preserved.",
 "For the trade paper this was a nicety. For this paper it is essential, because the CO2 question is entirely about changes over 28 years.",
]),
(32, "32/61", "GACI", "Face validity", "0:45", [
 "Does the index pass the smell test? The top of the scale is Atlanta, Beijing, Dubai, Heathrow, Hong Kong, Singapore. If your connectivity index does not put those on top, you have a problem. Ours does.",
]),
(33, "32/61", "GACI", "Face validity, full-bleed chart", "0:20", [
 ">> Full-screen version of the ranking chart; let it breathe for a few seconds, no new content.",
 "You can see the whole hierarchy here, and how stable the very top is over time.",
]),
(34, "33/61", "GACI", "Step 3: airports to countries", "1:00", [
 "Last construction step: airports to countries. Our headline is hub quality, the capacity-weighted mean of airport GACI: the average quality of the gateways a country actually uses, not inflated by owning many tiny airports. The alternative is the sum, total network footprint, which mechanically favours big countries.",
 "In this paper the treatment is hub quality; sum, max, and the unweighted mean all reappear as robustness checks, and, spoiler, they agree. Log GACI, capacity-weighted mean, is the right-hand side of everything that follows.",
]),
(35, "34/61", "GACI", "Step 3: the aggregation formulas", "0:20", [
 ">> Flash slide.",
 "Again, the formulas for the record.",
]),
(36, "35/61", "GACI", "Map: connectivity by country, 2023", "0:45", [
 "The built index, mapped: country connectivity in 2023, yellow meaning highly connected. North America, Europe, East Asia, the Gulf. So far, no surprises.",
]),
(37, "36/61", "GACI", "The treatment: who got connected", "1:00", [
 "But this map is the one that identifies the paper: the change in log connectivity, 1996 to 2023. The Gulf, Turkey, China, and Korea connect dramatically; parts of Europe quietly disconnect in relative terms.",
 "This variation, who rose and who fell in the network hierarchy, is the treatment. The question is what it did to emissions.",
]),
(38, "37/61", "IDENTIFICATION", "Section divider: Identification", "0:10", [
 "Part four: why you should believe a causal number.",
]),
(39, "38/61", "IDENTIFICATION", "The problem: airlines follow the economy", "1:15", [
 "The obvious problem: airlines add capacity where income, trade, and travel demand are already growing. Reverse causality, with upward and downward biases at once. And measurement error in a constructed index attenuates OLS; indeed our OLS is 3.59 against a 2SLS of 5.67.",
 "So we need variation in connectivity that has nothing to do with a country's economic trajectory. Our answer: geography that was fixed before the boom, interacted with a global technology cycle that no single country steers.",
]),
(40, "39/61", "IDENTIFICATION", "The Feyrer-type instrument", "1:30", [
 ">> Walk through the diagram: geography, times cycle, to GACI, to CO2.",
 "The instrument is Feyrer's logic from the trade literature, adapted to our index. Take each country's 1996 air-versus-sea market-access geography, fixed before the sample. Interact it with the world aviation technology cycle, global and unsteerable by any one country. That product predicts connectivity in the first stage; controls are log population, log sea market access, and country and year fixed effects.",
 "The first stage is strong: Kleibergen-Paap F of 154. We stress-test it by adding cycle interactions with baseline size, population, GDP, capacity; F falls only from 120 to 106 and the coefficient is stable. For contrast, our tourism instrument dies in the same test, F from 14 to zero. This is the only instrument we tried that survives its own execution squad, and we say that in the paper.",
]),
(41, "40/61", "IDENTIFICATION", "The exclusion restriction", "1:30", [
 "The fine print. The instrument may affect CO2 through one door only: connectivity. That is untestable by assumption, so we attack it three ways.",
 "One: geography also moves sea trade, so log sea market access is controlled directly in every regression. Two: maybe big rich countries just ride the global cycle anyway; that is the stress test I just showed, the test that killed our other instruments. Three: some direct effect might still remain, so we compute Conley bounds: the results survive direct effects up to 85 percent of the reduced form. That is an unusually generous margin.",
]),
(42, "41/61", "IDENTIFICATION", "The raw first look", "0:45", [
 "Before any 2SLS machinery, the raw reduced form: sort countries into quintiles of the instrument, plot emissions growth. Monotone: countries with stronger geography-driven connectivity growth emit more. The result is visible before a single regression is run.",
]),
(43, "42/61", "RESULTS", "Section divider: Results", "0:10", [
 "Part five: the number, and everything inside it.",
]),
(44, "43/61", "RESULTS", "The headline: +1% to +5.7%", "1:00", [
 ">> Pause on the big number.",
 "Here it is. Connectivity up one percent, national aviation CO2 up 5.67 percent, standard error 0.41.",
 "The benchmark to hold in your head is an elasticity of one: hubs could in principle absorb growth efficiently, proportional scaling. An elasticity of one is rejected at any conventional level. This is not proportional growth; it is amplification.",
]),
(45, "44/61", "RESULTS", "However you count it: far above one", "1:15", [
 "Is it the accounting? No. Bunker CO2, 5.67. Territorial LTO only, 5.92. Fifty-fifty cruise split, 5.62. International CO2, 5.69. Seat-kilometres, 6.07. And CO2 per seat-kilometre falls by 0.40, hold that thought for the next slide.",
 "Aggregation checks: GACI sum 2.28, max 4.82, unweighted mean 5.90, first stages all strong. Allocation rule, aggregation, instrument: nothing pushes the elasticity anywhere near one.",
]),
(46, "45/61", "RESULTS", "Scale versus technique", "1:15", [
 "Now decompose it. The same one percent of connectivity raises seat-kilometres, pure scale, by 6.07 percent. Emissions rise more slowly than capacity, so emissions per seat-kilometre fall by 0.40 percent. Hubbing genuinely delivers larger, fuller, longer-range operations. Efficiency is real.",
 "It is also hopelessly outgunned: the technique margin offsets less than one tenth of the scale response. The emissions consequence of connectivity is a volume story, not an efficiency story. That single sentence is the core of the paper.",
]),
(47, "46/61", "RESULTS", "The airport-level efficiency curve", "1:00", [
 "Zoom to the airport level and you see the efficiency in the cross-section: by connectivity ventile in 2023, median intensity falls from 284 to 77 kilograms per thousand seat-kilometres, while the international share climbs from one percent to sixty. Efficiency is real at the node. It is dominated by scale at the aggregate. Both statements are true, and the tension between them is the story.",
]),
(48, "47/61", "RESULTS", "Who drives it", "1:15", [
 "Whose elasticity is this? Split by 1996 income: 11.4 in the bottom tercile, 5.9 in the middle, 0.35 and insignificant at the top. By region: Africa 8.4, Asia-Pacific 5.4, Latin America 3.2, Europe essentially zero. Even the efficiency gains only appear in the bottom income tercile.",
 "So for mature networks, connectivity growth is roughly carbon-neutral at the margin. The elasticity is the sound of countries entering the network. That reframes the policy question: this is fundamentally about the developing world's coming connectivity boom.",
]),
(49, "48/61", "RESULTS", "And it is fading as the network matures", "1:15", [
 "The time dimension says the same thing. Excluding crisis years, the elasticity halves from 5.61 in 1996 to 2007 to 3.01 in 2010 to 2023, a significant fall, p of 0.005. And the efficiency margin only appears in the mature era, plus 0.78 early, minus 0.98 late.",
 "One honest caveat: COVID alone breaks the late-period first stage, F from 37 to 7 if you include 2020 and 2021, so the late period is identified excluding those years. But note: still far above one in both eras. Maturity slows the meter; it does not stop it.",
]),
(50, "49/61", "RESULTS", "Anatomy: what mediates it", "1:15", [
 "What carries the effect? Formal mediation: 86.5 percent runs through seat-kilometres, 83.9 through flight frequency, and essentially nothing through the international share. Market access scales flying.",
 "A different lever, hub quality identified off our secondary tourism instrument, does something qualitatively different: total CO2 does not respond, but international CO2 rises 3.16 and CO2 per seat-kilometre rises 1.23. Hub quality does not add flying; it recomposes flying toward international long-haul. Two levers, two fingerprints.",
]),
(51, "50/61", "RESULTS", "Your neighbour's hub, your emissions", "1:15", [
 "One more result, my favourite. Instrument your neighbours' connectivity: a one percent rise raises your own aviation CO2 by 7.45 percent, international CO2 by 10.2, first stage F of 134. And your trade? Plus 2.1 and insignificant.",
 "The margins are the converse of the own-network response: not more flights, but bigger aircraft, more international, shorter stages. This is the signature of feeding a foreign hub: the CO2 lands at home, the trade gains do not. National accounting misses a genuinely regional externality.",
]),
(52, "51/61", "BILL", "Section divider: The carbon bill", "0:10", [
 "Part six: the bill. Attribution, who pays, and the only real lever.",
]),
(53, "52/61", "BILL", "356 Mt: the CO2 the boom built", "1:00", [
 "Take the elasticity seriously and run history backwards: how much of today's aviation CO2 exists because of connectivity growth since 1996? Answer: 356 megatonnes of 2023 emissions, 42.5 percent of the world total. That is the map, and that is the hook number from the start of the talk, now with its full derivation behind it.",
]),
(54, "53/61", "BILL", "The price tag: the social cost of carbon", "1:30", [
 ">> Slower here; many in the audience will not know SCC. Walk the three-step strip.",
 "To price it we use the social cost of carbon: the present value of all future damage caused by one extra tonne of CO2. Emit a tonne today; it causes a century of damages, heat, crops, storms, sea level, health; discount those back to today and you get one price per tonne.",
 "Three standard price tags: 51 dollars from the US Interagency Working Group at a three percent discount rate; 185 from Rennert and coauthors in Nature; 190, the EPA's current central value. The gap between them is mostly the discount rate, not the climate science: how much do we care about damages fifty years out?",
 "Attach these to our 356 megatonnes and the bill is 18 to 68 billion dollars, recurring every year the traffic persists.",
]),
(55, "54/61", "BILL", "Who owes what", "1:00", [
 "The country bill. China, plus 88 megatonnes, about 17 billion dollars a year at the high SCC. The United States, 36 megatonnes. The UAE, 25. Japan and Turkey, 17 each; Korea, 14. And Germany is negative: minus 16 megatonnes, minus 3 billion, because its relative position in the network declined.",
 "World total: 18, 66, or 68 billion per year at the three SCC values. A climate bill in the tens of billions, annually.",
]),
(56, "55/61", "BILL", "Generated here, booked there", "1:00", [
 "Now the bookkeeping question from the start. Compare where emissions are booked under the bunker convention with where they physically occur: the US and the UAE book about 1.4 percentage points more of world emissions than they physically host; China books 3.5 points less. The mismatch is positive at every international mega-hub.",
 "Why care? Because any scheme that allocates responsibility by booked emissions, and CORSIA does, embeds a silent transfer across these lines.",
]),
(57, "56/61", "BILL", "The only lever: change the fuel", "1:30", [
 "So what actually bends the curve? Not efficiency, we showed that. Not accounting, that just moves the bill around. The fuel. This is a simple accounting exercise, not a forecast: we hold 2023 traffic fixed at 838 megatonnes and replace a share s of the jet fuel with sustainable aviation fuel that saves a fraction r of life-cycle CO2. Emissions are then 838 times one minus s times r. The blend share follows the ReFuelEU mandate, 2 percent in 2025 rising to 70 percent in 2050, and we bracket the life-cycle saving at 50, 65, and 80 percent.",
 ">> Point to the table on the right; walk down the 65 percent column.",
 "The figure shows the level, the table the numbers. At the 2035 mandate, 20 percent blend, the world level falls only to about 700 to 750 megatonnes. At the 2050 mandate, 70 percent blend, it falls to 370 to 545 megatonnes, and the carbon price of connectivity drops from 21 grams of CO2 per dollar of attributed trade to 9 to 14 grams.",
 "The green line is the reference point: 2023 minus the 356 megatonnes that connectivity growth created. The punchline: at a 65 percent life-cycle saving, the full 2050 path buys back 107 percent of that, so it offsets about as much CO2 as the entire past generation of connectivity growth created. Only at 50 percent does it fall short, at 82 percent.",
]),
(58, "57/61", "CONCLUSION", "Section divider: Conclusion", "0:10", [
 "Let me conclude.",
]),
(59, "58/61", "CONCLUSION", "Three comfortable myths, audited", "1:15", [
 "Three comfortable myths, audited against the data. 'Hub efficiency will absorb the traffic growth.' It offsets less than one tenth of the scale response. 'Emissions are booked where they are generated.' Hub accounting shifts up to 3.5 percentage points of world emissions across borders. 'Your emissions depend on your own network.' A one percent rise in your neighbours' connectivity raises your CO2 by seven and a half percent.",
 "The common thread: connectivity policy needs a carbon line in its cost-benefit table, and this paper's contribution is the number to put on that line.",
]),
(60, "59/61", "CONCLUSION", "Summary and policy", "1:00", [
 "In one slide. New data: flight-stage CO2 for six thousand airports, 28 years, valid under any allocation rule. New estimate: the connectivity-emissions elasticity is 5.67, far above one, concentrated in newly connecting countries, and spilling across borders. The bill: 42.5 percent of 2023 aviation CO2, 356 megatonnes, 18 to 68 billion dollars a year, traces to the post-1996 boom.",
 "Policy, in one sentence: connect if it pays, but put the carbon in the ledger, and bring the fuel.",
]),
(61, "60/61", "CONCLUSION", "Points to discuss", "0:45", [
 "And the honest list, framed as discussion points because they genuinely are. Our emissions are schedule-based, capacity not load factors. The instrument is strongest in the expansion era; the late period is identified only excluding COVID years. The airport-level results are descriptive, because no airport-level instrument survived our checks. And the attribution and SAF numbers are partial-equilibrium accounting, excluding non-CO2 climate effects like contrails, which would make the bill larger, not smaller.",
]),
(62, "61/61", "CONCLUSION", "Thank you", "0:30", [
 "To close where we started: one percent more connectivity, 5.7 percent more CO2; 356 megatonnes since 1996; and only fuel switching bends the level. Thank you very much, and I look forward to your questions.",
 ">> Leave the closing slide up during Q&A.",
]),
]

SKIP_45 = [
 ("Slides 2-3 (background primer)", "3:00", "Specialist audience already knows the field; open with slide 4."),
 ("Slide 20 (raw OAG screenshot)", "0:45", "Fold one sentence into slide 21."),
 ("Slide 25 (electrical-current intuition)", "0:45", "Mention 'current-flow betweenness' verbally on slide 23."),
 ("Slides 26, 29, 35 (formula slides)", "1:10", "Flash or skip; refer to the paper."),
 ("Slide 27 (indicator correlations)", "0:45", "One clause on slide 28: 'correlated 0.7-0.9 but not redundant'."),
 ("Slide 30 (PCA loadings)", "0:45", "One clause on slide 28: 'all five load positively and similarly'."),
 ("Slide 33 (full-bleed rank chart)", "0:20", "Stay on slide 32."),
 ("Slide 42 (RF quintile figure)", "0:45", "One sentence at the end of slide 41."),
 ("Slide 47 (airport efficiency curve)", "1:00", "Keep only the closing sentence, said on slide 46."),
 ("Slide 55 (country bill)", "1:00", "Read China/US/Germany off slide 53's map instead."),
]

SECTION_TIMES = [
 ("Opening + background (slides 1-7)", "8:15"),
 ("Motivation (8-10)", "3:10"),
 ("Data (11-15)", "4:25"),
 ("Building GACI (16-37)", "14:45"),
 ("Identification (38-42)", "5:10"),
 ("Results (43-51)", "9:45"),
 ("The carbon bill (52-57)", "6:10"),
 ("Conclusion (58-62)", "3:40"),
 ("TOTAL (before Q&A)", "~55 min"),
]

NAVY = RGBColor(0x1F, 0x33, 0x5C)
GRAY = RGBColor(0x66, 0x66, 0x66)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Georgia"
st.font.size = Pt(10.5)

t = doc.add_paragraph()
r = t.add_run("Presentation Script\nHow Much Does Air Connectivity Increase Aviation CO2?")
r.bold = True; r.font.size = Pt(18); r.font.color.rgb = NAVY
sub = doc.add_paragraph()
r = sub.add_run("Research seminar deck: GACI_CO2_presentation.pptx (62 slides / footer 61 pages). "
                "Target runtime ~55 minutes plus Q&A. Sunbin Yoo (SKKU), Jinwoo Lee (KAIST), Yifu Ou (HKU).")
r.italic = True; r.font.color.rgb = GRAY

h = doc.add_heading("Pacing at a glance", level=1)
tab = doc.add_table(rows=1, cols=2); tab.style = "Light Grid Accent 1"
tab.rows[0].cells[0].text = "Section"; tab.rows[0].cells[1].text = "Time"
for name, tm in SECTION_TIMES:
    row = tab.add_row(); row.cells[0].text = name; row.cells[1].text = tm

doc.add_heading("45-minute version: what to cut (~11 min saved)", level=1)
tab = doc.add_table(rows=1, cols=3); tab.style = "Light Grid Accent 1"
for i, txt in enumerate(["Cut", "Saves", "How to bridge"]):
    tab.rows[0].cells[i].text = txt
for cut, saves, how in SKIP_45:
    row = tab.add_row()
    row.cells[0].text = cut; row.cells[1].text = saves; row.cells[2].text = how
p = doc.add_paragraph()
r = p.add_run("Do not cut: slides 4, 6, 14, 37, 40-41, 44-46, 48, 51, 53-54, 57, 59. "
              "These carry the argument.")
r.italic = True; r.font.color.rgb = GRAY

doc.add_heading("Slide-by-slide script", level=1)
p = doc.add_paragraph()
r = p.add_run("Grey italic lines starting with an arrow are stage directions, not spoken text. "
              "Slide numbers are physical slide order in the pptx; the number in parentheses is the page shown in the deck footer.")
r.italic = True; r.font.color.rgb = GRAY

cur_sec = None
for no, page, sec, title, tm, paras in SLIDES:
    if sec != cur_sec:
        cur_sec = sec
    h = doc.add_heading(f"Slide {no}  ({page})  {title}", level=2)
    for run in h.runs:
        run.font.color.rgb = NAVY
    tp = doc.add_paragraph()
    r = tp.add_run(f"[{tm}]")
    r.bold = True; r.font.color.rgb = GRAY; r.font.size = Pt(9.5)
    for para in paras:
        if para.startswith(">>"):
            p = doc.add_paragraph()
            r = p.add_run("→ " + para[2:].strip())
            r.italic = True; r.font.color.rgb = GRAY; r.font.size = Pt(9.5)
        else:
            doc.add_paragraph(para)

doc.save(OUT)
print("saved:", OUT)
