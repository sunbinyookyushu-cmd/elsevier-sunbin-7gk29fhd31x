# How Much Does Air Connectivity Increase Aviation CO2?

Sunbin Yoo (Sungkyunkwan University), Jinwoo Lee (KAIST), Yifu Ou (University of Hong Kong)

## Abstract (long, ~454 words)

Transport accounts for roughly one quarter of global energy-related CO2 and remains almost entirely dependent on petroleum, so that transport infrastructure decisions determine fuel consumption for decades. Within transport, aviation is the sector in which this dependence is most difficult to reduce. It emits two to three percent of global CO2, has grown faster than other transport modes, lacks a near-term electrification pathway, and reports its international emissions under bunker-fuel conventions that lie outside national inventories and largely outside carbon pricing. Aviation is also the mode whose expansion is most actively pursued by governments, through route subsidies, airport capacity investment, and air-service agreements, on the grounds that air connectivity raises trade, tourism, and productivity. The emissions consequences of such policies have not been estimated causally. This paper provides the first global causal estimate of the effect of air connectivity on aviation CO2. We compute stage-resolved CO2 (taxi, take-off, climb, cruise, approach, and landing) for every scheduled commercial flight in OAG schedules under the EEA/EMEP methodology, covering more than 6,000 airports and 184 countries over 1996 to 2023, and validate the series against ICCT and OWID totals. Because emissions are resolved by flight stage, the same data support territorial, fuel-uplift, and split allocation rules without double counting. We match the emissions to the Global Air Connectivity Index and identify the effect with a Feyrer-type instrument that interacts each country's pre-sample air-versus-sea market-access geography with the world aviation technology cycle (first-stage F = 154, robust to size-by-cycle controls and to Conley bounds allowing direct effects up to 85 percent of the reduced form). A one percent increase in connectivity raises national aviation CO2 by 5.7 percent, an elasticity well above unity and invariant to the allocation rule. Connectivity does reduce CO2 per seat-kilometre, but this efficiency margin offsets less than one tenth of the scale response. The elasticity is concentrated in low-income, newly connecting countries and in the pre-2008 expansion period, and it extends across borders: a one percent increase in neighbouring countries' connectivity raises domestic aviation CO2 by 7.5 percent without a corresponding increase in trade. Connectivity growth since 1996 accounts for 42.5 percent (356 Mt) of 2023 aviation CO2, corresponding to an annual external cost of 18 to 68 billion dollars at standard social-cost-of-carbon values, and hub-based accounting reallocates up to 3.5 percentage points of world emissions across national ledgers. Scenario analysis along a ReFuelEU-style sustainable aviation fuel (SAF) blending path indicates that fuel substitution, rather than efficiency gains from network development, is the only margin that reduces the level of emissions: holding 2023 traffic fixed, the full 2050 mandate lowers aviation CO2 from 838 Mt to below 550 Mt, a reduction comparable in magnitude to the emissions attributable to connectivity growth since 1996.

## Abstract (short, ~232 words)

Transport accounts for about one quarter of global energy-related CO2, and its infrastructure determines fuel consumption for decades. Aviation is the sector in which this dependence is most difficult to reduce: it emits two to three percent of global CO2, has grown faster than other modes, lacks a near-term electrification pathway, and reports international emissions outside national inventories. It is also the mode whose expansion governments pursue most actively, through route subsidies, airport investment, and air-service agreements, yet the emissions consequences of connectivity have not been estimated causally. We compute stage-resolved CO2 for every scheduled flight worldwide (6,000+ airports, 184 countries, 1996 to 2023), match it to the Global Air Connectivity Index, and identify the effect with a Feyrer-type air-versus-sea market-access instrument. A one percent increase in connectivity raises national aviation CO2 by 5.7 percent, well above unity and invariant to the emissions allocation rule. Efficiency gains per seat-kilometre offset less than one tenth of the traffic response. The effect is concentrated in newly connecting low-income countries and extends across borders. Connectivity growth since 1996 accounts for 42.5 percent (356 Mt) of 2023 aviation CO2, an annual external cost of 18 to 68 billion dollars. Only fuel substitution reduces the level of emissions: a ReFuelEU-style sustainable aviation fuel (SAF) path lowers 2023 emissions from 838 Mt to below 550 Mt by 2050, a reduction comparable to the emissions attributable to connectivity growth.

## Keywords

air connectivity; aviation emissions; market access; instrumental variables; social cost of carbon; sustainable aviation fuel

## JEL

Q54, R41, L93, F18, Q56

## Number check (source: deck 2026-09-01 and main_co2_20260826.tex)

| Claim | Value | Source |
|---|---|---|
| Headline elasticity | 5.67 (SE 0.41), KP F 153.6 | co2_feyrer_full.log |
| Allocation range | 5.62 to 5.92 | Table 1 |
| Seat-km / intensity | 6.07 / -0.40 | Table 1 |
| Spillover | 7.45 (intl 10.2), trade +2.1 ns, F 134 | co2_ext*.log |
| Attribution | 356 Mt, 42.5% of 2023 | 14_attribution_scc.py |
| SCC bill | $18B / $66B / $68B at $51 / $185 / $190 | slide 54 |
| Mismatch | USA/ARE +1.4pp, CHN -3.5pp | CO2_map_mismatch_2023 |
| Conley | f* = 0.85 | co2_conley.log |
