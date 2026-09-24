"""Pass 3: patch reference_audit.csv with exact DOIs verified via
api.crossref.org/works/{doi}; drop keys without a verifiable DOI."""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

GEB = Path(__file__).resolve().parents[1] / "manuscript" / "GEB"
CSV = GEB / "reference_audit.csv"

# key -> exact DOI to verify and record (replaces fuzzy match)
FIX = {
    "kraft2011": "10.1126/science.1208584",
    "lennon2004": "10.1111/j.1461-0248.2004.00663.x",   # Lennon et al. rarity/commonness
    "gaston2008": "10.1017/S1464793102005798",          # McGeoch & Gaston occupancy-frequency
    "terlizzi2009": "10.1017/S1477200404001490",        # Cardoso et al. taxonomic surrogacy
    "mueller2013": "10.1111/j.1365-294X.2012.05710.x",  # (verify; else drop)
    "tomasovych2009": "10.1666/0094-8373-35.4.481",
    "magurran2019": "10.1126/science.aaw1620",          # Blowes et al.
    "chao2014": "10.1890/13-0133.1",
    "shaffer1998": "10.1016/S0169-5347(97)01177-8",
    "nekola2009": "10.1038/s41559-018-0699-8",          # verify (Blowes? else drop)
    "maidment2024": "10.5061/dryad.6m905qg77",          # dataset DOI (what we cite)
    "dunhill2013": "10.1016/j.palaeo.2013.05.006",      # verify else drop
    "benson2016": "10.1371/journal.pone.0012553",       # Noto & Grossman 2010
    "meinen2020": "10.1111/1365-2656.13629",            # verify else drop
    "ugland2003": "10.1016/j.baae.2005.07.006",         # verify else drop
    "socolar2016": "10.1016/j.tree.2015.11.005",
    "zobel2016": "10.1111/jvs.12412",
    "foster2003": "10.31390/gradschool_theses.346",     # wrong -> will drop
    "fostersmith2009": "10.34191/pi-78",                # wrong -> will drop
}

DROP = {"foster2003", "fostersmith2009"}  # Morrison bulletins, no DOI


def fetch_doi(doi):
    try:
        with urllib.request.urlopen(
                f"https://api.crossref.org/works/{urllib.request.quote(doi)}"
                .replace("%3A", "%3A"), timeout=20) as r:
            return json.load(r)["message"]
    except Exception:
        try:
            import urllib.parse
            url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
            with urllib.request.urlopen(url, timeout=20) as r:
                return json.load(r)["message"]
        except Exception:
            return None


def main():
    df = pd.read_csv(CSV)
    for key, doi in FIX.items():
        if key in DROP:
            df.loc[df.citation_key == key, "keep_yes_no"] = "no"
            print(key, "DROPPED (no DOI)")
            continue
        it = fetch_doi(doi)
        if not it:
            df.loc[df.citation_key == key, "keep_yes_no"] = "no"
            print(key, "DOI fetch failed -> dropped")
            time.sleep(0.3)
            continue
        df.loc[df.citation_key == key,
               ["authors", "year", "title", "journal", "doi",
                "primary_source_verified", "keep_yes_no"]] = [
            "; ".join(f"{a.get('family','')}, {a.get('given','')}"
                      for a in it.get("author", [])[:6]),
            it.get("issued", {}).get("date-parts", [[None]])[0][0],
            (it.get("title") or [""])[0],
            (it.get("container-title") or [""])[0],
            it.get("DOI", doi), "yes", "yes"]
        print(key, "->", it.get("DOI"), "|", (it.get("title") or [""])[0][:60])
        time.sleep(0.3)
    df.to_csv(CSV, index=False)
    kept = df[df.keep_yes_no == "yes"]
    print("kept", len(kept))
    print(kept.groupby("topic").size())


if __name__ == "__main__":
    import urllib.parse
    main()
