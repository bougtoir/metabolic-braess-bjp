"""Verify candidate references via Crossref and build
manuscript/GEB/reference_audit.csv + bibliography.bib.

Each candidate is queried by title; the top Crossref hit must match
on normalized title similarity to count as DOI-verified.
"""
from __future__ import annotations

import difflib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GEB = ROOT / "manuscript" / "GEB"
GEB.mkdir(parents=True, exist_ok=True)

# (key, expected title substring for matching, topic, claim supported)
CANDIDATES = [
    # beta diversity fundamentals
    ("whittaker1960", "Vegetation of the Siskiyou Mountains", "beta_fundamentals", "beta diversity as compositional variation"),
    ("tuomisto2010a", "A diversity of beta diversities", "beta_fundamentals", "beta diversity is a family of distinct concepts"),
    ("tuomisto2010b", "A consistent terminology for quantifying species diversity", "beta_fundamentals", "terminology"),
    ("baselga2010", "Partitioning the turnover and nestedness components of beta diversity", "beta_fundamentals", "turnover vs nestedness partition"),
    ("baselga2012", "The relationship between species replacement, dissimilarity derived from nestedness, and nestedness", "beta_fundamentals", "Jaccard family decomposition"),
    ("anderson2011", "Navigating the multiple meanings of beta diversity", "beta_fundamentals", "beta-diversity roadmap"),
    ("legendre2014", "Interpreting the replacement and richness difference components of beta diversity", "beta_fundamentals", "replacement vs richness difference"),
    # gamma-beta / pool size
    ("kraft2011", "Disentangling the drivers of beta diversity along latitudinal and elevational gradients", "gamma_beta", "species-pool size affects turnover"),
    ("chase2011", "Using null models to disentangle variation in community dissimilarity from variation in alpha-diversity", "gamma_beta", "null models for pool-size effects"),
    ("chase2018", "Embracing scale-dependence to achieve a deeper understanding of biodiversity and its change across communities", "gamma_beta", "scale dependence of diversity comparisons"),
    # distance decay
    ("nekolawhite1999", "The distance decay of similarity in biogeography and ecology", "distance_decay", "similarity decays with distance"),
    ("soininen2007", "The distance-decay of similarity in ecological communities", "distance_decay", "meta-analysis of distance decay"),
    ("morlon2008", "A general framework for the distance-decay of similarity in ecological communities", "distance_decay", "framework"),
    ("nekola2009", "Scale dependence in the biodiversity of forested islands", "spatial_scale", "scale dependence"),
    ("barton2013", "The spatial scaling of beta diversity", "spatial_scale", "beta diversity scales with grain/extent"),
    ("wiens1989", "Spatial scaling in ecology", "spatial_scale", "scale is fundamental in ecology"),
    # dominance / occupancy
    ("avolio2019", "A comprehensive approach to analyzing community dynamics using rank abundance curves", "dominance", "dominant species shape dissimilarity"),
    ("lennon2004", "The general importance of the common and the rare", "dominance", "common species drive dissimilarity"),
    ("gaston2008", "The ecological distribution of bird abundance and range size", "dominance", "occupancy-frequency distributions"),
    # taxonomic resolution
    ("terlizzi2009", "Is taxonomic relatedness of marine communities an effective tool", "taxonomic_resolution", "coarse taxonomy effects"),
    ("bevilacqua2012", "Taxonomic sufficiency in the detection of natural and human-induced changes in marine assemblages", "taxonomic_resolution", "genus-level aggregation preserves some patterns"),
    ("mueller2013", "Effects of taxonomic level, abundance and habitat on analyses of benthic assemblages", "taxonomic_resolution", "taxonomic level alters assemblage analyses"),
    # temporal aggregation / time averaging
    ("olszewski1999", "Taking advantage of time-averaging", "temporal_aggregation", "time averaging in fossil assemblages"),
    ("kidwell1995", "Time-averaged marine faunas", "temporal_aggregation", "time averaging mechanics"),
    ("tomasovych2009", "Unraveling the contributions of temporal and spatial mixing to time-averaging", "temporal_aggregation", "temporal vs spatial mixing"),
    ("tomasovych2010", "Predicting the effects of increasing temporal scale on species composition", "temporal_aggregation", "temporal grain effects"),
    ("magurran2019", "Temporal beta diversity", "temporal_aggregation", "temporal beta diversity literature"),
    ("korhonen2010", "A quantitative analysis of temporal turnover in aquatic species assemblages", "temporal_aggregation", "temporal turnover"),
    # sampling / detection
    ("gotelli2001", "Quantifying biodiversity: procedures and pitfalls in the measurement and comparison of species richness", "sampling", "rarefaction/comparability"),
    ("chao2014", "Rarefaction and extrapolation with Hill numbers", "sampling", "coverage-based standardization"),
    ("mackenzie2002", "Estimating site occupancy rates when detection probabilities are less than one", "sampling", "imperfect detection"),
    ("colwell2012", "Models and estimators linking individual-based and sample-based rarefaction", "sampling", "sample completeness"),
    # historical/aggregated data
    ("shaffer1998", "Museum collections and conservation biology", "aggregated_data", "museum records in biodiversity"),
    ("pyke2010", "Biological collections and ecological/environmental research", "aggregated_data", "collection-based inference biases"),
    ("lavoie2013", "Biological collections in an ever changing world", "aggregated_data", "collection biases"),
    ("graham2004", "New developments in museum-based informatics and applications in biodiversity analysis", "aggregated_data", "museum data analysis"),
    # palaeo / fossil
    ("maidment2024", "Local environments and diverse dinosaur communities in the Late Jurassic Morrison Formation", "palaeo", "Morrison occurrence dataset"),
    ("alroy2008", "Dynamics of origination and extinction in the marine fossil record", "palaeo", "PBDB-derived analyses"),
    ("behrensmeyer2000", "Taphonomy and paleobiology", "palaeo", "taphonomic filters"),
    ("dunhill2013", "Beta diversity and latitude gradients in marine faunas", "palaeo", "fossil beta diversity"),
    ("benson2016", "Cope's rule in fossil vertebrates", "palaeo", "fossil vertebrate macroevolution context"),
    ("lockley2015", "Theropod dinosaur ichnogenus Hispanosauropus identified from the Morrison Formation", "palaeo", "trackway evidence context"),
    ("drumheller2020", "High frequencies of theropod bite marks provide evidence for feeding", "palaeo", "Allosaurus feeding ecology"),
    ("foster2003", "Paleoecological analysis of the vertebrate fauna of the Morrison Formation", "palaeo", "Morrison palaeoecology"),
    ("fostersmith2009", "The vertebrate ichnological record of the Morrison Formation", "palaeo", "track record"),
    ("kowalewski1996", "Time-averaging, fidelity of fossil assemblages", "palaeo", "fossil assemblage fidelity"),
    # occupancy-beta / community structure extras
    ("heino2015", "A comparative analysis of metacommunity types", "community", "metacommunity comparisons across taxa"),
    ("meinen2020", "Global analysis of beta diversity components across taxonomic groups", "community", "cross-guild beta comparisons"),
    ("ugland2003", "Species-occupancy distributions", "dominance", "occupancy structure"),
    ("mcgill2007", "Species abundance distributions: moving beyond single prediction theories", "dominance", "SAD context"),
    ("socolar2016", "The use of ecological null models to infer mechanisms", "gamma_beta", "null model use"),
    ("hillebrand2008", "Consequences of dominance", "dominance", "dominance effects on community metrics"),
    ("partel2011", "Dark diversity", "gamma_beta", "pool-community links"),
    ("zobel2016", "The species pool factor", "gamma_beta", "species pool concept"),
]


def norm(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalnum())


def crossref(title: str):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 3})
    url = f"https://api.crossref.org/works?{q}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            items = json.load(r)["message"]["items"]
    except Exception:
        return None
    best, bs = None, 0.0
    for it in items:
        t = (it.get("title") or [""])[0]
        s = difflib.SequenceMatcher(None, norm(title), norm(t)).ratio()
        if s > bs:
            bs, best = s, it
    return best, bs


def main() -> None:
    rows = []
    bib = []
    for key, qtitle, topic, claim in CANDIDATES:
        res = crossref(qtitle)
        if not res or res[1] < 0.55:
            rows.append(dict(citation_key=key, authors="", year="",
                             title=qtitle, journal="", doi="", topic=topic,
                             specific_claim_supported=claim,
                             primary_source_verified="no",
                             keep_yes_no="no"))
            print("MISS", key)
            continue
        it, score = res
        auth = "; ".join(
            f"{a.get('family','')}, {a.get('given','')}"
            for a in it.get("author", [])[:6])
        rows.append(dict(
            citation_key=key,
            authors=auth,
            year=(it.get("issued", {}).get("date-parts", [[None]])[0][0]),
            title=(it.get("title") or [""])[0],
            journal=(it.get("container-title") or [""])[0],
            doi=it.get("DOI", ""), topic=topic,
            specific_claim_supported=claim,
            primary_source_verified="yes",
            keep_yes_no="yes"))
        bib.append(it)
        print("OK", key, it.get("DOI", ""))
        time.sleep(0.3)
    df = pd.DataFrame(rows)
    df.to_csv(GEB / "reference_audit.csv", index=False)
    with open(GEB / "bibliography_raw.json", "w") as f:
        json.dump(bib, f, indent=1)
    kept = df[df.keep_yes_no == "yes"]
    print(f"kept {len(kept)}/{len(df)}")
    print(kept.groupby("topic").size())


if __name__ == "__main__":
    main()
