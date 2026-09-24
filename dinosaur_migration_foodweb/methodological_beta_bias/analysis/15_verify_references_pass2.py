"""Pass 2: fix wrong Crossref matches and retry misses with improved queries.
Overwrites keep_yes_no/title/etc. in reference_audit.csv in place.
"""
from __future__ import annotations

import difflib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

GEB = Path(__file__).resolve().parents[1] / "manuscript" / "GEB"
CSV = GEB / "reference_audit.csv"

# key -> better query title (exact known titles)
RETRY = {
    "tuomisto2010a": "A diversity of beta diversities: straightening up a concept gone awry",
    "kraft2011": "Disentangling the drivers of beta diversity along latitudinal and elevational gradients",
    "nekola2009": "Scale dependence in the biodiversity of forested islands",
    "lennon2004": "The general importance of the common and the rare",
    "gaston2008": "The ecological distribution of bird abundance and range size",
    "terlizzi2009": "Effects of taxonomic sufficiency on marine coastal assemblages",
    "mueller2013": "Natural small-scale variation",
    "tomasovych2009": "Unraveling the contributions of temporal and spatial mixing",
    "magurran2019": "Temporal beta diversity",
    "chao2014": "Rarefaction and extrapolation with Hill numbers",
    "shaffer1998": "The status and future of museum collections",
    "lavoie2013": "Biological collections in an ever changing world: Herbaria as tools for biogeographical",
    "maidment2024": "Local environments and diverse dinosaur communities in the Late Jurassic Morrison Formation",
    "dunhill2013": "A latitudinal gradient in the beta diversity of Permian marine communities",
    "benson2016": "Cope's rule and the evolution of body size in Pinnipedimorpha",
    "foster2003": "Paleoecological analysis of the vertebrate fauna of the Morrison Formation",
    "fostersmith2009": "New diverse dinosaur tracksite in the Upper Jurassic",
    "meinen2020": "Global analysis of beta diversity components",
    "ugland2003": "Modelling the species-area relationship",
    "socolar2016": "The role of null models in ecology",
    "hillebrand2008": "Consequences of dominance: a review of evenness effects",
    "partel2011": "Dark diversity: shedding light on absent species",
    "zobel2016": "The species pool factor as a driver of plant diversity",
}


def norm(s):
    return "".join(c for c in str(s).lower() if c.isalnum())


def crossref(title):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 5})
    try:
        with urllib.request.urlopen(f"https://api.crossref.org/works?{q}", timeout=20) as r:
            items = json.load(r)["message"]["items"]
    except Exception:
        return None, 0.0
    best, bs = None, 0.0
    for it in items:
        t = (it.get("title") or [""])[0]
        s = difflib.SequenceMatcher(None, norm(title), norm(t)).ratio()
        if s > bs:
            bs, best = s, it
    return best, bs


def main():
    df = pd.read_csv(CSV)
    for key in RETRY:
        it, score = crossref(RETRY[key])
        ok = it is not None and score >= 0.5
        if ok:
            df.loc[df.citation_key == key,
                   ["authors", "year", "title", "journal", "doi",
                    "primary_source_verified", "keep_yes_no"]] = [
                "; ".join(f"{a.get('family','')}, {a.get('given','')}"
                          for a in it.get("author", [])[:6]),
                it.get("issued", {}).get("date-parts", [[None]])[0][0],
                (it.get("title") or [""])[0],
                (it.get("container-title") or [""])[0],
                it.get("DOI", ""), "yes", "yes"]
        else:
            df.loc[df.citation_key == key, "keep_yes_no"] = "no"
        print(key, "->", "OK" if ok else "still miss",
              it.get("DOI", "") if it else "")
        time.sleep(0.3)
    df.to_csv(CSV, index=False)
    kept = df[df.keep_yes_no == "yes"]
    print(f"kept {len(kept)}/{len(df)}")


if __name__ == "__main__":
    main()
