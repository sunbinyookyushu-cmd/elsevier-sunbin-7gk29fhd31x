# Strand 4: Methods notes (staggered DiD, synthetic control, few-treated inference, spillovers, continuous treatment)

Compiled 2026-10-02. Citations verified with refcheck (Crossref / Semantic Scholar) unless noted. "Read" = what was actually read: abstract (OpenAlex, arXiv, NBER, publisher page) or full text (PDF). Package availability checked on 2026-10-02 against the SSC archive (fmwww.bc.edu/repec/bocode/<letter>/<name>.pkg) and CRAN package pages.

Package check results (2026-10-02):
- SSC present: csdid, drdid, eventstudyinteract, did_multiplegt, did_multiplegt_old, did_multiplegt_dyn, did_multiplegt_stat, did_had, did_imputation, did2s, jwdid, stackedev, stackdid, lpdid, synth, allsynth, sdid, sdid_event, boottest, summclust, bacondecomp, honestdid, event_plot, xtevent, rwolf.
- SSC not found: synth_runner (distributed outside SSC), csdid2, any Conley-Taber command.
- CRAN present: did, fixest, DIDmultiplegt, DIDmultiplegtDYN, DIDHAD, didimputation, did2s, Synth, tidysynth, scpi, contdid (0.1.1), bacondecomp, HonestDiD, etwfe.
- CRAN absent or removed: synthdid (not on CRAN, distributed on GitHub), fwildclusterboot (removed from CRAN), summclust (removed from CRAN), wildrwolf (removed), DIDmultiplegtSTAT (not on CRAN).
- Note on two SSC stacking commands: `stackedev` describes itself as the stacked event study of Cengiz et al.; `stackdid` describes itself as stacking "as described in Gormley and Matsa (2011)". Neither describes the Wing, Freedman and Hollingsworth corrective weights; their weights are distributed as R and Stata example code on GitHub (hollina/stacked-did-weights).

---

## M1. Goodman-Bacon (2021)
- Citation: Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. Journal of Econometrics 225(2), 254-277. DOI 10.1016/j.jeconom.2021.03.014. refcheck: verified.
- Read: abstract (NBER w25018 page).
- Problem solved: shows the two-way fixed effects (TWFE) DiD with staggered timing is "a weighted average of all possible two-group/two-period DD estimators in the data", and that it "is biased when effects change over time" (abstract). The bias comes from comparisons that use already-treated units as controls.
- When to use for us: as a diagnostic on any TWFE baseline that pools Germany/Austria 2011, Norway 2016, Sweden 2018, France 2020, etc. Shows how much weight sits on late-vs-early comparisons.
- Packages: Stata `bacondecomp` (SSC); R `bacondecomp` (CRAN).

## M2. Callaway and Sant'Anna (2021)
- Citation: Callaway, B., Sant'Anna, P.H.C. (2021). Difference-in-Differences with multiple time periods. Journal of Econometrics 225(2), 200-230. DOI 10.1016/j.jeconom.2020.12.001. refcheck: verified.
- Read: abstract (arXiv 1803.09015).
- Problem solved: identification, estimation and inference for group-time average treatment effects with "(i) multiple time periods, (ii) variation in treatment timing, and (iii) when the parallel trends assumption holds potentially only after conditioning on observed covariates"; outcome regression, IPW or doubly robust estimands; aggregation schemes; bootstrap for "simultaneous (instead of pointwise) inference" (abstract).
- When to use for us: main estimator for binary, absorbing national ticket-tax adoption, with never-treated or not-yet-treated airports as controls. The estimator is built for staggered adoption (treatment stays on once adopted), so the Netherlands (tax in 2008-09, then removed, then reintroduced in 2021) needs separate handling (drop, or treat 2021 as the event with a clean pre-period, or use M5).
- Packages: Stata `csdid` (SSC; also `drdid`); R `did` (CRAN).

## M3. Sun and Abraham (2021)
- Citation: Sun, L., Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. Journal of Econometrics 225(2), 175-199. DOI 10.1016/j.jeconom.2020.09.006. refcheck: verified.
- Read: abstract (arXiv 1804.05785).
- Problem solved: in TWFE event studies with leads and lags, "the coefficient on a given lead or lag can be contaminated by effects from other periods, and apparent pretrends can arise solely from treatment effects heterogeneity"; proposes an interaction-weighted estimator "free of contamination" (abstract).
- When to use for us: event-study plots for ticket taxes, as a robustness check to M2/M7.
- Packages: Stata `eventstudyinteract` (SSC); R `fixest` (CRAN, `sunab()`).

## M4. de Chaisemartin and D'Haultfoeuille (2020)
- Citation: de Chaisemartin, C., D'Haultfoeuille, X. (2020). Two-Way Fixed Effects Estimators with Heterogeneous Treatment Effects. American Economic Review 110(9), 2964-2996. DOI 10.1257/aer.20181169. refcheck: matched (Crossref).
- Read: abstract (OpenAlex).
- Problem solved: TWFE regressions "estimate weighted sums of the average treatment effects (ATE) in each group and period, with weights that may be negative", so the coefficient "may for instance be negative while all the ATEs are positive"; proposes an alternative estimator (abstract).
- When to use for us: computing the share of negative weights in our TWFE; their estimator allows treatment switching on and off.
- Packages: Stata `did_multiplegt_old` (original command, SSC) and `did_multiplegt` (SSC); R `DIDmultiplegt` (CRAN).

## M5. de Chaisemartin and D'Haultfoeuille (intertemporal effects, REStat)
- Citation: de Chaisemartin, C., D'Haultfoeuille, X. Difference-in-Differences Estimators of Intertemporal Treatment Effects. Review of Economics and Statistics 108(4), 863-880. DOI 10.1162/rest_a_01414. Crossref lists the issue year as 2026; working paper versions NBER w29873 (2022) and SSRN 3731856. Verified via Crossref and OpenAlex (refcheck matched the SSRN version).
- Read: abstract (arXiv 2007.04267).
- Problem solved: "The treatment may be non-binary, non-absorbing, and the outcome may be affected by treatment lags"; event-study estimators of "the effect of being exposed to a weakly higher treatment dose for l periods"; shows TWFE and a local-projection version can be biased (abstract).
- When to use for us: the cleanest fit for ticket taxes as they actually happened: the Dutch tax switched on and off, and several taxes changed rates or distance bands after introduction (exact dates to be taken from our own tax-schedule files, not from this note). Treatment can be the tax in EUR per departing passenger.
- Packages: Stata `did_multiplegt_dyn` (SSC); R `DIDmultiplegtDYN` (CRAN).

## M6. de Chaisemartin, D'Haultfoeuille, Pasquier, Sow and Vazquez-Bare (continuous treatments)
- Citation: de Chaisemartin, C., D'Haultfoeuille, X., Pasquier, F., Sow, D., Vazquez-Bare, G. Difference-in-Differences Estimators for Treatments Continuously Distributed at Every Period. arXiv 2201.06898 (v7, July 2026). Earlier title: "Difference-in-Differences for Continuous Treatments and Instruments with Stayers", SSRN DOI 10.2139/ssrn.4011782 (2022; refcheck partial match). Working paper, not yet published as far as checked.
- Read: abstract (arXiv).
- Problem solved: "When studying the effects of taxes, tariffs, or prices using panel data, the treatment is often continuously distributed in every period." Units are split into switchers and stayers; slopes are "identified by DID comparisons between switchers and stayers sharing the same baseline treatment level", and conditioning on baseline treatment "accommodates time-varying treatment effects"; doubly robust estimators; IV extension; application to gasoline taxes (abstract).
- When to use for us: continuous ticket-tax levels and effective carbon cost per seat, where some airports never change tax (stayers).
- Packages: Stata `did_multiplegt_stat` (SSC; its description says binary, discrete, or continuous treatment). A related design without stayers: de Chaisemartin, D'Haultfoeuille and Vazquez-Bare (2024), AEA Papers and Proceedings 114, 610-613, DOI 10.1257/pandp.20241049; Stata `did_had` (SSC), R `DIDHAD` (CRAN).

## M7. Borusyak, Jaravel and Spiess (2024)
- Citation: Borusyak, K., Jaravel, X., Spiess, J. (2024). Revisiting Event-Study Designs: Robust and Efficient Estimation. Review of Economic Studies 91(6), 3253-3285. DOI 10.1093/restud/rdae007. refcheck: verified.
- Read: abstract (OpenAlex).
- Problem solved: "conventional regression-based estimators fail to provide unbiased estimates of relevant estimands absent strong restrictions on treatment-effect homogeneity"; derives the efficient estimator, which "takes an intuitive imputation form"; tests for identifying assumptions; works "with time-varying controls, in triple-difference designs, and with certain non-binary treatments" (abstract).
- When to use for us: imputation is attractive with many never-treated airports worldwide and monthly seat data; the paper also develops tests for the identifying assumptions (pre-trends). The triple-difference extension fits a design comparing taxed vs untaxed airports, before vs after, and route types (e.g. short-haul vs long-haul bands).
- Packages: Stata `did_imputation` (SSC); R `didimputation` (CRAN). Gardner's two-stage DiD is a close relative: Stata `did2s` (SSC), R `did2s` (CRAN).

## M8. Wooldridge (2025)
- Citation: Wooldridge, J.M. (2025). Two-way fixed effects, the two-way Mundlak regression, and difference-in-differences estimators. Empirical Economics 69(5), 2545-2587. DOI 10.1007/s00181-025-02807-z. Verified via Crossref (SSRN version 2021).
- Read: abstract (OpenAlex).
- Problem solved: an extended TWFE (ETWFE) with cohort-by-period interactions is equivalent to pooled OLS with cohort and period indicators and to an imputation estimator; allows "considerable treatment effect heterogeneity" and "cohort-specific trends" (abstract).
- When to use for us: regression-based alternative that easily adds controls and nonlinear models (e.g. Poisson for seat counts with zeros).
- Packages: Stata `jwdid` (SSC); R `etwfe` (CRAN).

## M9. Cengiz, Dube, Lindner and Zipperer (2019): stacked DiD
- Citation: Cengiz, D., Dube, A., Lindner, A., Zipperer, B. (2019). The Effect of Minimum Wages on Low-Wage Jobs. Quarterly Journal of Economics 134(3), 1405-1454. DOI 10.1093/qje/qjz014. refcheck: verified.
- Read: full text of NBER working paper w25434 (stacked design is in Online Appendix C there).
- What they did: "we create 138 data sets for each event h. The data sets include the state of event j and all clean control states for 8 year panel by event time. Clean control states are those that do not have any non-trivial state minimum wage increases in the 8 year panel around event h; other states are dropped". Stacking "prevents negative weighting of some events that may occur with a staggered design". Main estimates cluster by state ("the level at which policy is assigned"); event-specific confidence intervals use Ferman and Pinto because the procedure is "appropriate for a single treated unit" and corrects for heteroskedasticity from very different state sample sizes.
- When to use for us: one stack per tax event (DE 2011, AT 2011, NO 2016, SE 2018, FR 2020, NL 2021, UK changes), with clean controls defined as airports in countries with no tax change in the event window. This is also the natural place to drop nearby foreign airports from controls (see M22).
- Packages: Stata `stackedev` (SSC).

## M10. Wing, Freedman and Hollingsworth (2024): weighted stacked DiD
- Citation: Wing, C., Freedman, S.M., Hollingsworth, A. (2024). Stacked Difference-in-Differences. NBER Working Paper 32054. DOI 10.3386/w32054 (also SSRN 10.2139/ssrn.4702247). refcheck: verified (working paper; no journal version found).
- Read: abstract (NBER page).
- Problem solved: "the most basic stacked estimator does not identify the target aggregate or any other average causal effect because it applies different implicit weights to treatment and control trends. The bias can be eliminated using corrective sample weights." Defines a "trimmed aggregate ATT" with compositional balance across the event window.
- When to use for us: if we stack tax events, use their weights; trim to a balanced event window (for example, -3 to +4 years) so that event-time comparisons are not driven by changes in which events contribute.
- Code: R and Stata example code (GitHub hollina/stacked-did-weights, linked from the NBER page). No dedicated SSC command found.

## M11. Abadie, Diamond and Hainmueller (2010): synthetic control
- Citation: Abadie, A., Diamond, A., Hainmueller, J. (2010). Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program. Journal of the American Statistical Association 105(490), 493-505. DOI 10.1198/jasa.2009.ap08746. refcheck: verified.
- Read: full text of NBER working paper w12831 (donor pool and inference sections).
- What they did: donor pool excludes units exposed to similar interventions: "we discard from the donor pool states that adopted some other large-scale tobacco control program during our sample period" and "all states that raised their state cigarette taxes by 50 cents or more". Inference by placebo permutation: "we apply the synthetic control method to every potential control in our sample"; in-time placebos when there are few comparison units.
- When to use for us: single-country tax events (Netherlands 2008-09, Sweden 2018, Norway 2016) with a country-level or airport-level outcome. Donor pool must exclude countries with their own ticket tax changes and, given displacement, airports close to the treated border.
- Packages: Stata `synth` (SSC), `allsynth` (SSC, bias correction and automated placebo); R `Synth`, `tidysynth`, `scpi` (CRAN).

## M12. Arkhangelsky, Athey, Hirshberg, Imbens and Wager (2021): synthetic DiD
- Citation: Arkhangelsky, D., Athey, S., Hirshberg, D.A., Imbens, G.W., Wager, S. (2021). Synthetic Difference-in-Differences. American Economic Review 111(12), 4088-4118. DOI 10.1257/aer.20190159. refcheck: verified.
- Read: abstract (OpenAlex). Implementation paper also read at abstract level: Clarke, D., Pailanir, D., Athey, S., Imbens, G. (2024). On synthetic difference-in-differences and related estimation methods in Stata. Stata Journal 24(4), 557-598. DOI 10.1177/1536867X241297914 (refcheck: verified), which covers "a single treatment adoption date and when adoption is staggered".
- Problem solved: an estimator that "builds on insights behind the widely used difference-in-differences and synthetic control methods", with "desirable robustness properties" when the outcome model includes "latent unit factors interacted with latent time factors" (abstract).
- When to use for us: a natural estimator for single-country taxes with airport-level panels and many untreated airports; the Stata implementation also handles staggered adoption (Clarke et al. 2024 abstract).
- Packages: Stata `sdid` and `sdid_event` (SSC); R `synthdid` (GitHub; not on CRAN).

## M13. Conley and Taber (2011)
- Citation: Conley, T.G., Taber, C.R. (2011). Inference with "Difference in Differences" with a Small Number of Policy Changes. Review of Economics and Statistics 93(1), 113-125. DOI 10.1162/REST_a_00049. refcheck: verified.
- Read: abstract (OpenAlex; NBER t0312).
- Problem solved: when identification comes from "a small number of groups" changing policy, usual inference fails; they use "information from a large sample of nonchanging groups" to estimate the distribution of the estimator under a point null and build confidence intervals by test inversion. Point estimators are not consistent with a fixed number of treated groups.
- When to use for us: national ticket taxes give roughly 6 to 10 treated countries; if we cluster by country, this is the textbook case. Requires that the error distribution of control groups is informative about treated groups (problematic with very different airport sizes, see M17).
- Code: Stata do files and Matlab files on Christopher Taber's website (users.ssc.wisc.edu/~ctaber/DD/diffdiff.html). No SSC command found.

## M14. Cameron, Gelbach and Miller (2008)
- Citation: Cameron, A.C., Gelbach, J.B., Miller, D.L. (2008). Bootstrap-Based Improvements for Inference with Clustered Errors. Review of Economics and Statistics 90(3), 414-427. DOI 10.1162/rest.90.3.414. refcheck: verified.
- Read: abstract (OpenAlex).
- Problem solved: "Standard asymptotic tests can over-reject, however, with few (five to thirty) clusters"; cluster bootstrap-t procedures (the wild cluster bootstrap) bring rejection rates "of 10% using standard methods" down to "the nominal size of 5%".
- When to use for us: few clusters overall (e.g. clustering by country within Europe, about 30 countries).
- Packages: Stata `boottest` (SSC).

## M15. MacKinnon and Webb (2017)
- Citation: MacKinnon, J.G., Webb, M.D. (2017). Wild Bootstrap Inference for Wildly Different Cluster Sizes. Journal of Applied Econometrics 32(2), 233-254 (online 2016). DOI 10.1002/jae.2508. refcheck: verified (Crossref year 2016 = online date).
- Read: abstract (OpenAlex).
- Problem solved: the "rule of 42" fails with unbalanced clusters; the wild cluster bootstrap helps, "However, this procedure fails when a small number of clusters is treated."
- When to use for us: warns that country-clustered wild bootstrap will not rescue inference when only a handful of countries are taxed, and that cluster sizes (number of airports or seats per country) are very unequal.

## M16. MacKinnon and Webb (2018)
- Citation: MacKinnon, J.G., Webb, M.D. (2018). The wild bootstrap for few (treated) clusters. Econometrics Journal 21(2), 114-135. DOI 10.1111/ectj.12107. refcheck: verified.
- Read: abstract (OpenAlex).
- Problem solved: proposes the "subcluster wild bootstrap", which includes the ordinary wild bootstrap as a limiting case; works well in pure treatment models when cluster sizes are similar, but "the analogue of this requirement is not likely to hold for difference-in-differences regressions".
- When to use for us: subcluster bootstrap (bootstrap at airport level, cluster at country level) as one of several inference checks; report alongside randomization inference.
- Packages: Stata `boottest` (SSC) implements wild and subcluster variants.

## M17. Ferman and Pinto (2019)
- Citation: Ferman, B., Pinto, C. (2019). Inference in Differences-in-Differences with Few Treated Groups and Heteroskedasticity. Review of Economics and Statistics 101(3), 452-467. DOI 10.1162/rest_a_00759. refcheck: verified.
- Read: abstract (OpenAlex).
- Problem solved: with few treated and many control groups, "heteroskedasticity generated by variation in group sizes can invalidate existing inference methods" (including Conley-Taber type methods); their method remains valid.
- When to use for us: treated countries differ greatly in size (Germany vs Austria vs Norway), so Conley-Taber should be paired with this correction. Cengiz et al. (2019) used it for event-specific intervals.
- Packages: none verified on SSC or CRAN.

## M18. MacKinnon and Webb (2020)
- Citation: MacKinnon, J.G., Webb, M.D. (2020). Randomization inference for difference-in-differences with few treated clusters. Journal of Econometrics 218(2), 435-450. DOI 10.1016/j.jeconom.2020.04.024. Verified via Crossref.
- Read: abstract (Semantic Scholar).
- Problem solved: with few treated clusters, CRVE t-tests "severely overreject" and wild cluster bootstrap variants "can either overreject or underreject dramatically"; randomization inference based on t-statistics "typically performs better (although by no means perfectly)" than RI based on coefficients when clusters are heterogeneous.
- When to use for us: permutation of tax adoption across countries (placebo countries and placebo dates), using the t-statistic as the test statistic.
- Packages: Stata `ritest` (SSC, general randomization inference and permutation tests; checked 2026-10-02); country-level permutation scheme coded by the user.

## M19. Roodman, Nielsen, MacKinnon and Webb (2019): boottest
- Citation: Roodman, D., Nielsen, M.O., MacKinnon, J.G., Webb, M.D. (2019). Fast and wild: Bootstrap inference in Stata using boottest. Stata Journal 19(1), 4-60. DOI 10.1177/1536867X19830877. refcheck: verified.
- Read: abstract (OpenAlex).
- What it provides: wild (cluster) bootstrap after regress, areg, reghdfe, ivregress, ivreg2 and ML commands, for situations with "few clusters, few treated clusters, or weak instruments"; multiway clustering; test inversion for confidence sets.
- Packages: Stata `boottest` (SSC). R `fwildclusterboot` has been removed from CRAN (checked 2026-10-02).

## M20. MacKinnon, Nielsen and Webb (2023): cluster-robust inference guide
- Citation: MacKinnon, J.G., Nielsen, M.O., Webb, M.D. (2023). Cluster-robust inference: A guide to empirical practice. Journal of Econometrics 232(2), 272-299. DOI 10.1016/j.jeconom.2022.04.001. Verified via Crossref.
- Read: abstract (OpenAlex).
- What it provides: practical guidance on choosing the clustering level and inference method, based on recent theory and simulations.
- When to use for us: choosing between airport, country, and airport-pair (route) clustering; cluster leverage diagnostics.
- Packages: Stata `summclust` (SSC; cluster leverage, influence and CV3 jackknife).

## M21. Callaway, Goodman-Bacon and Sant'Anna (2024): continuous treatment
- Citation: Callaway, B., Goodman-Bacon, A., Sant'Anna, P.H.C. (2024). Difference-in-differences with a Continuous Treatment. NBER Working Paper 32117, DOI 10.3386/w32117; arXiv 2107.02637 (v8, 31 Dec 2025; no journal reference listed). refcheck: verified (working paper). Companion: Callaway, Goodman-Bacon, Sant'Anna (2024). Event Studies with a Continuous Treatment. AEA Papers and Proceedings, DOI 10.1257/pandp.20241047 (Crossref).
- Read: abstracts (NBER via OpenAlex; arXiv).
- Problem solved: ATT-type parameters for a dose are identified under a parallel trends assumption analogous to the binary case, but "comparing these parameters across treatments is challenging because parallel trends does not rule out selection bias"; stronger assumptions are needed to interpret dose-response; "popular two-way fixed effects estimands admit multiple interpretations", all with limitations (arXiv abstract).
- When to use for us: the EU ETS design "EEA airport x EUA price" is a TWFE with a continuous dose. Their results imply that the TWFE slope is hard to interpret and that comparing high-exposure vs low-exposure airports requires a strong parallel trends assumption across doses. A cleaner dose is airport-level exposure (e.g. share of seats on ETS-covered intra-EEA routes) with an untreated group (non-EEA airports, or EEA airports with no covered routes).
- Packages: R `contdid` (CRAN, version 0.1.1). No Stata command verified; `did_multiplegt_stat` (M6) covers continuous treatments with stayers.

## M22. Butts (2023 working paper): DiD with spatial spillovers
- Citation: Butts, K. Difference-in-Differences Estimation with Spatial Spillovers. arXiv 2105.03737 (v3, 10 June 2023). Working paper; refcheck search did not find a journal version (refcheck verify returned not_found because the work is arXiv only). Verified on arXiv.
- Read: abstract and Sections 1-3 (arXiv PDF).
- Problem solved: when treatment effects cross borders, "classical difference-in-differences estimation produces biased estimates" because "(1) the control group no longer identifies the counterfactual trend because their outcomes are affected by treatment and (2) changes in treated units' outcomes reflect the effect of their own treatment status and the effect from the treatment status of close units". Proposed fix: "a set of distance bins from the treated units (e.g. being 0-20 miles, 20-40 miles, 40-60 miles from the treated units) ... interacting them with a treatment indicator"; each ring indicator estimates the average spillover in that band, but "interpreting these estimates causally requires that each ring satisfies a parallel trends assumption with the far-away control units". Staggered timing is handled with an imputation (two-stage) approach; the paper points to the R/Stata package did2s.
- When to use for us: this is the template for displacement. Define rings of foreign airports by road distance or drive time from the taxed country border or from the taxed airports' catchments (e.g. 0-100 km, 100-200 km), estimate the spillover on ring airports as a separate outcome, and use only far-away airports as controls. Extends naturally to a "network ring": non-EU hubs (IST, DXB, DOH, AUH) whose connections to taxed countries are exposed.
- Packages: Stata/R `did2s` for the imputation step (both verified on SSC/CRAN); rings are built by the user.

## M23. Rambachan and Roth (2023): sensitivity to parallel trends violations
- Citation: Rambachan, A., Roth, J. (2023). A More Credible Approach to Parallel Trends. Review of Economic Studies 90(5), 2555-2591. DOI 10.1093/restud/rdad018. refcheck: verified.
- Read: abstract (OpenAlex).
- Problem solved: robust inference when parallel trends may fail, by restricting how different post-treatment violations can be from pre-trends; partial identification and sensitivity analysis.
- When to use for us: airports in countries that tax aviation may already be on different growth paths (e.g. LCC expansion), so report breakdown values for the hub-centrality effects.
- Packages: R `HonestDiD` (CRAN); Stata `honestdid` (SSC).

## M24. Roth, Sant'Anna, Bilinski and Poe (2023): DiD survey
- Citation: Roth, J., Sant'Anna, P.H.C., Bilinski, A., Poe, J. (2023). What's trending in difference-in-differences? A synthesis of the recent econometrics literature. Journal of Econometrics 235(2), 2218-2244. DOI 10.1016/j.jeconom.2023.03.008. refcheck: verified.
- Read: abstract (Semantic Scholar / arXiv).
- What it provides: practitioner recommendations organized around "(i) multiple periods and variation in treatment timing, (ii) potential violations of parallel trends, or (iii) alternative frameworks for inference".
- When to use for us: as the citation that justifies the estimator menu and inference choices in the methods section.

## Applied exemplars from energy and environmental economics

## A1. Andersson (2019): single-country carbon tax, synthetic control
- Citation: Andersson, J.J. (2019). Carbon Taxes and CO2 Emissions: Sweden as a Case Study. American Economic Journal: Economic Policy 11(4), 1-30. DOI 10.1257/pol.20170144. refcheck: verified.
- Read: abstract only (AEA page). PARTIAL.
- Design (from abstract): carbon tax and VAT on transport fuel in Sweden; synthetic control "constructed from a comparable group of OECD countries".
- Headline: "carbon dioxide emissions from transport declined almost 11 percent, with the largest share due to the carbon tax alone"; "the carbon tax elasticity of demand for gasoline is three times larger than the price elasticity".
- Lesson: an Energy Economics audience accepts synthetic control for a single-country price instrument; tax-specific responses can differ from price elasticities, which argues against simulating tax effects from fare elasticities.

## A2. Dechezlepretre, Nachtigall and Venmans (2023): EU ETS, matching plus DiD
- Citation: Dechezlepretre, A., Nachtigall, D., Venmans, F. (2023). The joint impact of the European Union emissions trading system on carbon emissions and economic performance. Journal of Environmental Economics and Management 118, 102758. DOI 10.1016/j.jeem.2022.102758. refcheck: verified.
- Read: full text (LSE Research Online, CC BY).
- Data and unit: installation-level emissions from national PRTRs of France, Netherlands, Norway and UK (low reporting thresholds, so unregulated installations are observed); firm-level financial data for 31 ETS countries.
- Identification: matching on installation-level inclusion criteria plus DiD. Main matching: "exact matching on country and NACE3 sector, Mahalanobis distance matching using pre-ETS emissions and pre-ETS emissions growth rate, caliper of 0.3", with replacement; Poisson regressions with installation and year fixed effects, plus country and sector trends; 240 matched pairs for emissions.
- Inference: "Standard errors are clustered at both the match and the installation-year level (for repeated control installations)", following Abadie and Spiess (2022) for matched samples.
- Headline: "a reduction in carbon emissions in the order of -10% between 2005 and 2012" (abstract); Table 5 ETS*Post = -0.10* to -0.11* (SE 0.06). Effect concentrated in the largest installations. Robustness estimates "ranging between 6% and 13%".
- Lesson: for the ETS, a credible control group comes from units just outside coverage, matched on pre-period levels and growth within country and sector; for us the analogue is matching EEA airports to non-EEA airports (or to EEA airports with low ETS-covered seat shares) on pre-2012 traffic level and growth, and clustering at the matched-set level.
