"""Per-flight fuel burn and CO2 by aircraft type and great-circle distance.

Model: FEAT reduced-order model (Seymour, Held, Georges & Boulouchos, 2020, TR-D 88:102528)
    fuel_kg = a1 * d^2 + a2 * d + intercept,   d = mission distance in km
Coefficients: data/raw/emissions/feat_ac_model_coefficients.csv (133 ICAO types), with an
IATA->ICAO designator table from the same repository (data/raw/emissions/feat_aircraft_type_designators.csv).

Conventions used here (document in the paper's data appendix):
  * Mission distance = great-circle distance x (1 + detour) + 40 km, detour default 0.05
    (en-route inefficiency; Seymour et al. use a distance-correction regression; EEA/EUROCONTROL
    report ~3-6% horizontal inefficiency in Europe). Both parameters are arguments.
  * CO2 = 3.16 kg per kg jet fuel (ICAO / IPCC default).
  * Unknown aircraft type -> fallback to the median coefficients of the same (engine type, wake
    category) class, then to the all-jet medium median. The fallback level is returned so you can
    report the share of capacity priced with fallbacks.
Outputs: data/processed/co2_per_flight_lookup.csv (type x distance grid) for quick merging.
"""
import pandas as pd, numpy as np, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
COEF = pd.read_csv(root/"data/raw/emissions/feat_ac_model_coefficients.csv", index_col=0)
DESIG = pd.read_csv(root/"data/raw/emissions/feat_aircraft_type_designators.csv", index_col=0)
IATA2ICAO = dict(zip(DESIG.ac_code_iata.dropna(), DESIG.loc[DESIG.ac_code_iata.notna(), "ac_code_icao"]))
CO2_PER_KG_FUEL = 3.16
# OAG/IATA designators that FEAT's table lacks -> nearest FEAT ICAO type (generic family codes map to the
# most common member in 2010s European schedules; freighters to the passenger variant).
IATA_ALIAS = {"73H":"B738","73W":"B737","7S8":"B738","73C":"B733","73S":"B733","73F":"B733","73J":"B739","73N":"B733",
              "32A":"A320","32S":"A320","32B":"A321","32C":"A321","321":"A321","223":"BCS3","221":"BCS1",
              "787":"B788","74E":"B744","748":"B748","74H":"B748","747":"B744","74M":"B744","74Y":"B744","74F":"B744",
              "757":"B752","75W":"B752","767":"B763","76W":"B763","777":"B772","77X":"B779",
              "330":"A332","338":"A339","340":"A343","350":"A359","380":"A388","310":"A310","312":"A310","345":"A345",
              "CRJ":"CRJ2","CR2":"CRJ2","CR7":"CRJ7","CR9":"CRJ9","CRK":"CRJX","E90":"E190","E9L":"E190","E95":"E195","295":"E295","290":"E290",
              "E45":"E145","ERJ":"E145","ERD":"E145","ER3":"E135","ER4":"E145","E70":"E170","E75":"E75L","E7W":"E75L",
              "DH8":"DH8D","DH4":"DH8D","DH3":"DH8C","DH2":"DH8B","DH1":"DH8A","AT5":"AT45","AT4":"AT45","ATR":"AT72","AT7":"AT72",
              "146":"B463","141":"B461","142":"B462","143":"B463","AR8":"RJ85","AR1":"RJ1H",
              "M80":"MD82","M81":"MD81","M82":"MD82","M83":"MD83","M87":"MD87","M88":"MD88","M90":"MD90","D95":"DC95","D9S":"DC95","DC9":"DC95",
              "M11":"MD11","D10":"DC10","L10":"L101","100":"F100","F70":"F70","F50":"F50","SF3":"SF34","S20":"SB20",
              "BEH":"BE20","BE1":"BE10","AN6":"AN26","AN4":"AN24","AN2":"AN2","IL9":"IL96","IL7":"IL76","TU3":"T134","TU5":"T154","YK2":"YK42","YK4":"YK40","SU9":"SU95",
              "717":"B712","722":"B722","733":"B733","734":"B734","735":"B735","736":"B736","738":"B738","739":"B739","73G":"B737","73L":"B732",
              "7M8":"B38M","7M9":"B39M","7M7":"B37M","319":"A319","318":"A318","320":"A320","32N":"A20N","32Q":"A21N","32M":"A21N",
              "332":"A332","333":"A333","339":"A339","342":"A342","343":"A343","346":"A346","351":"A35K","359":"A359","388":"A388",
              "752":"B752","753":"B753","762":"B762","763":"B763","764":"B764","772":"B772","773":"B773","77L":"B77L","77W":"B77W","781":"B78X","788":"B788","789":"B789",
              "744":"B744","AB4":"A30B","AB6":"A306","313":"A310"}

_by_icao = COEF.set_index("ac_code_icao")[["reduced_fuel_a1","reduced_fuel_a2","reduced_fuel_intercept","e_type","wake"]]
_class_med = COEF.groupby(["e_type","wake"])[["reduced_fuel_a1","reduced_fuel_a2","reduced_fuel_intercept"]].median()
_jet_med = COEF[(COEF.e_type=="Jet")&(COEF.wake=="M")][["reduced_fuel_a1","reduced_fuel_a2","reduced_fuel_intercept"]].median()

def resolve_type(code):
    """Return (icao_code or None, fallback_level). Accepts ICAO (B738) or IATA (738) designators."""
    if code is None or (isinstance(code,float) and np.isnan(code)): return None, 2
    c = str(code).strip().upper()
    if c in _by_icao.index: return c, 0
    if c in IATA2ICAO and IATA2ICAO[c] in _by_icao.index: return IATA2ICAO[c], 0
    if c in IATA_ALIAS and IATA_ALIAS[c] in _by_icao.index: return IATA_ALIAS[c], 0
    # family-level substitutes when the exact alias target is absent from FEAT
    FAMILY = {"A339":"A333","A338":"A332","B748":"B744","B779":"B77W","B78X":"B789","A35K":"A359","E190":"E195","E295":"E195","E290":"E195",
              "DH8A":"DH8C","DH8B":"DH8C","AT45":"AT72","B461":"B462","MD11":"B763","DC10":"B763","L101":"B763","AN26":"AT72","IL96":"A343","IL76":"B763","T134":"MD82","T154":"B752","F50":"AT72","BE20":"BE10","CRJX":"CRJ9","E135":"E145","SB20":"SF34"}
    tgt = IATA_ALIAS.get(c, c)
    if tgt in FAMILY and FAMILY[tgt] in _by_icao.index: return FAMILY[tgt], 1
    return None, 2

def fuel_kg(code, gc_km, detour=0.05, extra_km=40.0, e_type=None, wake=None):
    """Fuel burn in kg for one flight. Vectorised over gc_km (array-like ok)."""
    icao, lvl = resolve_type(code)
    if icao is not None:
        a1,a2,b = _by_icao.loc[icao, ["reduced_fuel_a1","reduced_fuel_a2","reduced_fuel_intercept"]]
    elif e_type is not None and wake is not None and (e_type,wake) in _class_med.index:
        a1,a2,b = _class_med.loc[(e_type,wake)]; lvl = 1
    else:
        a1,a2,b = _jet_med; lvl = 2
    d = np.asarray(gc_km, dtype=float)*(1+detour) + extra_km
    return a1*d**2 + a2*d + b, lvl

def co2_kg(code, gc_km, **kw):
    f, lvl = fuel_kg(code, gc_km, **kw)
    return f*CO2_PER_KG_FUEL, lvl

if __name__ == "__main__":
    grid = np.arange(100, 16001, 100)
    rows = []
    for icao, r in _by_icao.iterrows():
        f,_ = fuel_kg(icao, grid)
        rows.append(pd.DataFrame({"ac_icao":icao,"e_type":r.e_type,"wake":r.wake,"gc_km":grid,"fuel_kg":f.round(1),"co2_kg":(f*CO2_PER_KG_FUEL).round(1)}))
    out = pd.concat(rows); out.to_csv(root/"data/processed/co2_per_flight_lookup.csv", index=False)
    print("lookup rows:", len(out), "| types:", out.ac_icao.nunique())
    for ac,d in [("738",500),("B738",1000),("320",1000),("77W",8000),("A388",10000),("AT7",400),("E90",800),("ZZZ",1000)]:
        c,l = co2_kg(ac,d); print(f"{ac:5s} {d:6d} km -> CO2 {c/1000:7.1f} t  (fallback level {l})")
