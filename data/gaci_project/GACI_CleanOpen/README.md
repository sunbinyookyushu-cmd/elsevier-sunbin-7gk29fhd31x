# GACI_CleanOpen — Is air openness clean openness?

Question. Trade openness has ambiguous environmental effects (Antweiler, Copeland & Taylor 2001; Managi, Hibiki &
Tsurumi 2009, JEEM). Openness arrives by two modes: aircraft move people and light, high value-to-weight goods; ships
move heavy, pollution-intensive goods. We ask whether a country's air connectivity (GACI) and its sea connectivity
(UNCTAD LSCI) have different effects on the carbon/pollution intensity of the economy, and whether the air effect runs
through industrial composition (light, clean industries) rather than through income (scale/technique).

Design (Managi et al. transposed).
    ln Y_ct = b_air ln GACI_ct + b_sea ln LSCI_ct + g ln y_ct + d ln pop_ct + a_c + l_t + e
  Y: CO2/GDP, energy/GDP, CO2/energy, SO2 pc, PM2.5, pollution-intensive manufacturing share. Instruments for GACI:
  heritage x world tourism (trade paper) and Feyrer-type air market access; LSCI instrumented by sea market access.
  Composition test: Gelbach decomposition with mediators (manufacturing share, pollution-intensive share, services share,
  trade share, income). Heterogeneity by baseline income (Managi's OECD vs non-OECD). Dynamic GMM as robustness.

Data in hand: gaci_panel_combined.csv (GACI, trade, income, tourism_int, feyrer_int, sea market access), OWID CO2/energy.
Data to add (public, country-year):
  - UNCTAD Liner Shipping Connectivity Index (LSCI), 2006- quarterly -> annual mean  (unctadstat.unctad.org)
  - WDI: NV.IND.MANF.ZS (manufacturing % GDP), NV.SRV.TOTL.ZS (services), EN.ATM.PM25.MC.M3 (PM2.5 exposure, 1990/1995/2000/2005/2010-2019)
  - CEDS SO2 and NOx national emissions 1750-2022 (McDuffie et al.; github.com/JGCRI/CEDS release files)
  - UNIDO INDSTAT2: value added by ISIC 2-digit -> pollution-intensive share (ISIC 17, 19, 20, 23, 24 under Rev.3; Mani-Wheeler list)
  - (optional) EDGAR v8 SO2/NOx/PM2.5 by country for a second emissions source

Files: analysis_clean_openness.py (first pass on data in hand), _out_clean_openness.txt, stata/08_clean_openness.do (template).
