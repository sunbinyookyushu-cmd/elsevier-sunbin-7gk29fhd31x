"""Download Eurostat route-level air passenger data (avia_par_XX) for European reporting countries.

Eurostat 'avia_par_<cc>' tables give passengers carried (PAS_CRD), seats available (SEATS? not in all),
and flights by airport pair (origin airport in reporting country x partner airport), monthly/quarterly/annual.
We pull annual (freq=A) passengers carried and commercial flights for every reporting country.

Host required: ec.europa.eu (currently BLOCKED by the session network policy -> run locally or
after allowing the host). Uses the SDMX 2.1 dissemination API, TSV format (gzip).
Output: data/raw/eurostat/avia_par_<cc>.tsv.gz
"""
import pathlib, sys, time, urllib.request, gzip, shutil
root = pathlib.Path(__file__).resolve().parents[1]
out = root/"data/raw/eurostat"; out.mkdir(parents=True, exist_ok=True)
# Reporting countries with avia_par tables (EU27 + EFTA + UK + candidates); lower-case Eurostat codes
CC = ["at","be","bg","ch","cy","cz","de","dk","ee","el","es","fi","fr","hr","hu","ie","is","it","lt","lu","lv","me","mk","mt","nl","no","pl","pt","ro","rs","se","si","sk","tr","uk"]
BASE = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/avia_par_{cc}/?format=TSV&compressed=true"
for cc in (sys.argv[1:] or CC):
    url = BASE.format(cc=cc); dest = out/f"avia_par_{cc}.tsv.gz"
    if dest.exists(): print("skip", dest.name); continue
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=300) as r, open(dest,"wb") as f: shutil.copyfileobj(r, f)
            print("ok", dest.name, dest.stat().st_size//1024, "KB"); break
        except Exception as e:
            print("retry", cc, attempt, e); time.sleep(2**attempt)
print("""
Parsing notes: TSV first column is 'freq,unit,tra_meas,airp_pr\\TIME_PERIOD'; airp_pr like 'DE_EDDF_ES_LEMD'
(reporting airport ICAO, partner airport ICAO). tra_meas codes: PAS_CRD (passengers carried),
PAS_BRD (boarded), CAF_PAS (commercial passenger flights), ST_PAS (seats available, where reported).
Flags ':' = missing, 'p' provisional. Annual series start 1993-2003 depending on country.""")
