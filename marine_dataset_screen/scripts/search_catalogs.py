"""Catalog search log for the marine trophic-mobility dataset screen.

Queries public APIs where they exist (DataCite, Dryad, GBIF) and appends
results to metadata/search_log.csv. Manual searches (no scriptable API)
are recorded in the same log with access date and outcome.
"""
import csv
import datetime
import json
import os
import urllib.parse
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOG = os.path.join(ROOT, "metadata/search_log.csv")
RAW = os.path.join(ROOT, "metadata/search_results")
os.makedirs(RAW, exist_ok=True)

QUERIES_DATACITE = [
    "krill penguin telemetry tracking",
    "krill fur seal tracking South Georgia",
    "capelin seabird survey",
    "sardine anchovy seabird upwelling tracking",
    "Tagging of Pacific Predators TOPP",
    "seabird GPS tracking forage fish survey",
    "sandeel seabird tracking North Sea",
    "tuna telemetry eddy",
    "herring predator telemetry",
    "marine mammal telemetry prey acoustic survey",
    "pinniped fish telemetry foraging hotspot",
    "whale shark zooplankton tracking",
]

def datacite_search(q):
    url = ("https://api.datacite.org/dois?query="
           + urllib.parse.quote(q) + "&page[size]=10")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        j = json.load(r)
    out = []
    for it in j["data"]:
        a = it["attributes"]
        out.append({"query": q, "doi": a.get("doi"),
                    "title": (a.get("titles") or [{}])[0].get("title"),
                    "publisher": a.get("publisher"),
                    "year": a.get("publicationYear"),
                    "types": a.get("types", {}).get("resourceTypeGeneral")})
    return out

def log_row(source, query, url, n, note=""):
    exists = os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "query", "url",
                                        "accessed", "n_hits", "note"])
        if not exists:
            w.writeheader()
        w.writerow({"source": source, "query": query, "url": url,
                    "accessed": datetime.date.today().isoformat(),
                    "n_hits": n, "note": note})

if __name__ == "__main__":
    all_hits = []
    for q in QUERIES_DATACITE:
        try:
            hits = datacite_search(q)
            all_hits += hits
            log_row("datacite_api", q,
                    "https://api.datacite.org/dois?query=" + urllib.parse.quote(q),
                    len(hits))
            print(q, len(hits))
        except Exception as e:
            log_row("datacite_api", q, "", 0, note=f"error: {e}")
            print(q, "ERR", e)
    with open(os.path.join(RAW, "datacite_hits.json"), "w") as f:
        json.dump(all_hits, f, indent=1)
    # Manual searches (no API) — recorded per spec 20.
    manual = [
        ("movebank", "seabird penguin seal tracking Southern Ocean South Georgia",
         "https://www.movebank.org/", "browse web UI; requires login for data download"),
        ("obis_seamap", "telemetry penguin seal turtle shark",
         "https://seamap.env.duke.edu/", "dataset catalog, registration-free download for most"),
        ("otn", "salmon herring predator acoustic telemetry",
         "https://members.oceantrack.org/", "data portal; much data restricted"),
        ("imos", "animal tracking facility", "https://animaltracking.aodn.org.au/",
         "AODN portal; open CSV/netCDF downloads"),
        ("pangaea", "krill penguin tracking",
         "https://www.pangaea.de/", "open data; per-dataset DOI"),
        ("ices_datras", "sandeel acoustic survey", "https://datras.ices.dk/",
         "open API downloads of survey haul data"),
        ("noaa_fisheries", "CalCOFI anchovy sardine acoustic trawl",
         "https://coastwatch.pfeg.noaa.gov/erddap", "open ERDDAP datasets"),
    ]
    for src, q, u, note in manual:
        log_row(f"manual:{src}", q, u, -1, note=note)
    print("done")
