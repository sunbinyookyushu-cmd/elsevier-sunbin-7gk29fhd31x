================================================================================
GACI report rebuild on the ln_gaci_cwm (hub-quality) main variable   [2026-06-18]
================================================================================
Main treatment is now ln_gaci_cwm (capacity-weighted-mean GACI = "hub quality"),
NOT lng (GACI sum). All tables/figures/counterfactuals aligned to cwm, EXCEPT the
one-year shock losses (Section 6), which stay on the sum measure (see note below).

Key cwm IV elasticities (Table 1 Panel A, full sample 1996-2023):
  volume  2.303  =  intensity 1.302  +  GDP-scale 1.001     (exact log identity)
  first-stage KP F ~ 18 on the FULL sample  (stronger than lng sum's F ~ 10 -> also
  answers the co-author's weak-instrument concern).

--------------------------------------------------------------------------------
RUN ORDER  (Stata steps are MANUAL - run them in your Stata, then the Python step)
--------------------------------------------------------------------------------
STEP 1 - STATA (run in your Stata; overwrites the .log file):
   1a. gaci_tourism_hetero2.do     (REQUIRED - Table 2 now uses ln_gaci_cwm)
   NOTE: gaci_tourism_main.do may be re-run for cleanliness, but the existing
         gaci_tourism_main.log already contains the ln_gaci_cwm (Panel A) results,
         so Table 1 builds without re-running it.
   NOTE: gaci_shock_export2.do is NO LONGER NEEDED -- Section 6 shock losses and
         Table 3 (shock interactions) were both REMOVED from the report (2026-06-18).

STEP 2 - PYTHON (rebuilds the Word report from the logs + aggregates):
   python build_report_docx.py     -> GACI_coauthor_report.docx

ALREADY RE-RUN BY CLAUDE (CSV-based, no Stata needed - do NOT need to redo):
   compute_aggregates.py  -> _aggregates.json  (cwm 20-yr gain; sum 1-yr shocks)
   build_gaci_map.py      -> GACI_implied_map.png (intensity channel, beta 1.302)
   build_continent_trend.py -> GACI_continent_trend.png / .csv  (Task 4)

--------------------------------------------------------------------------------
HEADLINE NUMBERS AFTER THE SWITCH (stable & defensible)
--------------------------------------------------------------------------------
20-yr gain (cwm, intensity channel, 1996-2023):
   $7.75T attributable goods trade = 16.5% of 2023 world goods trade = 7.4% of world GDP
   (vs sum+intensity $7.5T / 16% / 7.2% -> essentially unchanged)
Shock losses (old Section 6) and the shock-interaction Table 3: REMOVED 2026-06-18
   per co-author concern over magnitudes. The report no longer makes any COVID/Russia
   dollar-loss claim. (The cwm shock counterfactual was indefensible at ~$7.5T, and the
   sum-based $1.8T was dropped along with the section.)

--------------------------------------------------------------------------------
WHAT CHANGED IN EACH FILE
--------------------------------------------------------------------------------
gaci_tourism_main.do      : loop reordered -> ln_gaci_cwm first (Panel A). Still emits both.
gaci_tourism_hetero2.do   : treatment lng -> ln_gaci_cwm; baseline split on 1996 cwm.
gaci_shock_export2.do     : treatment + interactions built from ln_gaci_cwm; term renamed.
compute_aggregates.py     : TCOL=ln_gaci_cwm, betas 2.303/1.302/1.001; shocks kept on sum.
build_gaci_map.py         : implied map on ln_gaci_cwm, beta 1.302.
build_report_docx.py      : Table 1 Panel A = cwm; Table 3 term = ln_gaci_cwm; Sec 3/5/6/7/8
                            text + Fig 2 caption updated to cwm coefficients.
build_continent_trend.py  : NEW - Task 4, implied trade-intensity effect by continent.
