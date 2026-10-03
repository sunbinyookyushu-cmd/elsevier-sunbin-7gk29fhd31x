# Handoff: aviation tax paper (GACI_FuelShock/stata_paper)

Source conversation: https://claude.ai/code/session_011xviSjxiJwGFvqyrBhtG3S (cloud session, 2026-10-02).
Logs reviewed: 01_main_run.log, 02_events_mediation_run.log (run 3 Oct 2026, StataNow 19.5).
Data lives on the user's machine, not in that session. Nothing below was run; the do-files are untested.

## What the existing results support

Design: stacked DiD, 8 European ticket-tax increases (NLD 2008 handled separately, stk = 0),
airport x month, pre [A-36, A-1], post [E, E+11], anticipation (donut) months dropped.
FE: airport x calendar month x event (fe_u), month x event (fe_t). Controls lngdp lnpop. SE clustered by country (29).
stk codes (from the SDID loop): 0 NLD 2008, 1 IRL 2009, 2 DEU 2011, 3 AUT 2011, 4 NOR 2016, 5 SWE 2018, 6 GBR 2007, 7 DNK 1998, 8 MLT 2005.

CO2 (departing flights), treated x post:
- Table 4 col 1 unweighted -0.094 (10%); seat-weighted -0.003 (ns, SE 0.013)
- Table 5 event time: post year 1 -0.119***, year 2 -0.141**; pre [A-36,A-25] -0.080 (p 0.10), [A-24,A-13] -0.026
- Effective-date windows +-12..+-36: -0.103 to -0.115 (1-10%)
- Never-taxed controls -0.065 (ns), world controls -0.056 (ns), drop IRL -0.097 (10%)
- HonestDiD: CI excludes 0 up to M = 0.5, includes 0 at M = 1
- SDID by event: CO2 significant only IRL 2009 (-0.167); DEU, AUT ~0; MLT -0.13 (p 0.11)
- Global 19 events: post1 -0.079***, but Europe-subsample pre-trend -0.097** with region x month FE

Margins: seats effect ~ CO2 effect; CO2 per seat-km (ln_int) = 0 everywhere (weighted 0.009, SE 0.007).
Decomposition (annual): destinations -0.084**, flights per destination -0.024, CO2 per flight 0.007.
Size: small airports seats -0.22***, CO2 -0.20***; mid and large ns. Large airports gauge +0.031***.
Border airports (bp): ~0 in all European specs; negative in the global sample.

Network (annual, k <= 0): ln GACI -0.014**; destinations -0.084**; eigenvector -0.119*** (small -0.218***); betweenness noisy.
GACI event time: k=-3 0.0002 (SE 0.0098), k=-2 0.0008 (0.0035), k=0 -0.015***, k=+1 -0.018***. Cleanest result in the logs.
Country-level SDID on seat-weighted GACI: ~0 for every event (SWE -0.047, p 0.06).
IV mediation (tax -> network -> CO2): first-stage F for the mediator 0.9-5.7, indirect effects ns; weakiv failed (needs `ssc install avar`).

## Framing agreed in the conversation

Headline: ticket taxes concentrate the network rather than shrink it. Country connectivity is unchanged (SDID ~0),
peripheral (small) airports lose destinations and centrality, hubs hold and upgauge. Emissions fall only through the
volume margin, intensity is a precise zero, aggregate (seat-weighted) CO2 effect is ~0.
Mechanism: a per-passenger flat tax bites hardest on low-fare thin routes (LCC, small airports); hubs respond by upgauging.
Table order: network main (T3) -> GACI event study (T5B) -> size heterogeneity and margins (T2, T7B) -> country SDID (T6)
-> CO2 decomposition (T4, T7A, T8) -> HonestDiD, robustness, leakage in appendix.
Policy line: high cost per tonne, paid in peripheral connectivity; a fuel-based instrument would target intensity.
Journals: Transportation Research Part D first; JTEP, Transport Policy, Regional Studies.
Known attacks to pre-empt: (1) "country GACI is 0 so nothing happened" -> show within-country GACI dispersion / HHI rising;
(2) "it is a Ryanair effect" -> add carrier type (LCC share, carrier exit).
Link to the sibling GACI_Inequality paper: that paper's hub-concentration channel (03_conc_mech: share_max, hhi, primacy)
raises inequality; the tax paper shows taxes raise concentration. One HHI-after-tax table connects the two.

## Files produced (copy into stata_paper\)

03_leakage.do: net-of-leakage checks on existing stacks.
  A controls without adjacent-country airports; B spillover to adjacent-country hubs (w0 >= 1m);
  C bloc-level DiD and SDID (treated + adjacent countries summed); D stage length / CO2 per flight at foreign hubs.
  VERIFY the stk mapping and the adjacency lists in program nbr_list. Note IRL 2009's only neighbour (GBR) was already taxed.

04_regional_benefits.do: regional cost of connectivity loss + benefit/cost table.
  Within treated country, regions with small-airport-dominated catchments vs hub regions; country x month x event FE;
  control-country regions carry the same exposure x post term (triple diff). Outcomes: Eurostat nights (tour_occ_nim,
  FOR vs DOM as placebo), employment (lfst_r_lfe2en2, NACE I and total), GDP per head (nama_10r_2gdp).
  2SLS of nights on catchment seats / regional GACI instrumented by exposure x post.
  Section 7 writes benefits_by_event.csv: tonnes abated (weighted CO2 coef with 95% band), carbon value at 100/200 EUR,
  tax revenue (seats x load factor x dose), Harberger DWL, foreign-night loss x spend, jobs, cost per tonne, net benefit.
  Needs airports.csv (apid,lat,lon) and nuts2_centroids.csv (nuts2,lat,lon; GISCO NUTS 2021 label points).
  Three id/time variable names are auto-detected (airport id, month, year); set them at the top if detection fails.
  Parameters at the top: radius 100 km, decay 50 km, load factor 0.80, carbon 100 EUR/t, spend 120 EUR/night, co2_t unit factor.

## Next steps for the local session

1. `describe using stack_month.dta` / `stack_year.dta`: confirm airport id, month (%tm), year variable names; confirm ln_co2 units.
2. Run 03_leakage.do; read L_A..L_D tables. A1/A2 close to -0.094 => no control contamination. B hub coefficient > 0 => diversion.
3. Build airports.csv and nuts2_centroids.csv; run 04_regional_benefits.do; read R1-R5 and benefits_by_event.csv.
4. Add: within-country GACI HHI after tax; carrier-type split; `ssc install avar` then rerun weakiv in 02_events_mediation.do.
5. Optional: wild cluster bootstrap (boottest) for the 29-cluster baseline; rail passengers (Eurostat rail_pa_quartal) for net effect.
