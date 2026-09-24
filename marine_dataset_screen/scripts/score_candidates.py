"""Score candidates per Task-3 spec sections 5-7.

20 positive criteria (1 point each) + explicit penalties. Scores are a
screening aid only. Outputs outputs/tables/marine_candidate_ranking.csv.
"""
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
inv = pd.read_csv(os.path.join(ROOT, "metadata/marine_candidate_datasets.csv"))

# Per-criterion 0/1 flags keyed by candidate_id.
# Criteria order: [>=10 events, >=20 events, daily-or-better bio resolution,
# hourly-or-better telemetry, direct prey measurement, direct predator
# measurement, >=3 trophic layers, simultaneous layers, current data,
# env data, >=3 years, >=5 years, individual IDs, repeated obs within events,
# objective event onset, geographically repeated events, multiple sites,
# published benchmark, open license, scriptable download]
FLAGS = {
    "TOPP":                    [1,1,1,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1],
    "south-georgia-krill-predators":[1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,0],
    "seatrack-sandeel":        [1,0,1,1,1,1,0,0,1,1,1,1,1,1,1,0,1,1,1,1],
    "calCofi-cps-predator":    [1,1,0,0,1,0,0,1,1,1,1,1,0,1,1,1,1,1,1,1],
    "peru-anchoveta-seabird":  [1,0,0,0,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,0],
    "benguela-sardine-gannet": [1,0,1,1,1,1,0,0,1,1,1,1,1,1,1,0,0,1,0,0],
    "imos-aatams":             [0,0,1,1,0,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1],
    "otn-atlantic":            [0,0,1,1,0,1,0,0,1,1,1,1,1,1,0,1,1,1,0,0],
    "krillbase-whale":         [0,0,0,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1],
    "meop-southern":           [1,1,1,1,0,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
    "eddy-tuna":               [1,1,1,0,0,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0],
    "north-pacific-salmon-kw": [1,0,1,0,1,1,0,0,1,1,1,1,1,1,1,0,0,1,0,0],
    "herring-cod-norway":      [1,0,0,0,1,1,1,1,1,1,1,1,0,1,1,0,0,1,0,0],
    "davoren-capelin":         [1,0,0,0,1,1,0,1,1,0,1,1,0,1,1,0,0,1,1,1],
    "palmyra-pilot":           [1,1,1,1,0,1,1,1,1,1,0,0,1,1,1,0,0,0,1,1],
    "esas-northsea":           [1,1,0,0,1,1,0,1,1,1,1,1,0,0,1,1,1,1,0,0],
    "gbr-shark-herbivore":     [1,0,1,1,0,1,1,0,1,1,1,1,1,1,1,0,1,0,0,0],
    "ant-peninsula-gentoo":    [1,0,1,1,0,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1],
    "whaleshark-zooplankton":  [0,0,1,0,0,1,0,0,1,1,1,1,1,1,0,0,1,1,0,0],
    "california-ecomega":      [1,0,0,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0],
    "scotia-sea-krill-penguin":[1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,0,0],
    "gulf-of-maine-herring-whale":[1,0,0,0,1,1,0,1,1,1,1,1,0,1,1,0,0,1,0,0],
    "palmyra-like-french-polynesia":[0,0,1,0,0,1,0,0,1,1,1,1,1,1,0,0,1,0,0,0],
}

# Penalties: [events<5, not simultaneous, indirect prey, >7d sampling,
# heavy env interpolation, manual approval] -> [5,3,3,3,2,5]
PEN = {
    "TOPP":                    [0,0,3,0,0,0],
    "south-georgia-krill-predators":[0,3,0,0,0,0],
    "seatrack-sandeel":        [0,0,0,0,0,0],
    "calCofi-cps-predator":    [0,0,0,0,0,0],   # prey only; predator via TOPP fusion - no penalty (layers pair)
    "peru-anchoveta-seabird":  [0,0,0,3,0,5],
    "benguela-sardine-gannet": [0,3,0,0,0,0],
    "imos-aatams":             [5,3,3,0,0,0],
    "otn-atlantic":            [0,3,3,0,0,5],
    "krillbase-whale":         [5,3,0,0,2,0],
    "meop-southern":           [0,3,3,0,0,0],
    "eddy-tuna":               [0,3,3,0,0,0],
    "north-pacific-salmon-kw": [0,3,0,0,0,5],
    "herring-cod-norway":      [0,0,0,0,0,5],
    "davoren-capelin":         [0,0,0,3,0,0],
    "palmyra-pilot":           [0,0,3,0,2,0],
    "esas-northsea":           [0,0,0,3,0,5],
    "gbr-shark-herbivore":     [0,3,3,0,0,0],
    "ant-peninsula-gentoo":    [0,0,3,0,0,0],
    "whaleshark-zooplankton":  [0,3,3,0,0,0],
    "california-ecomega":      [0,0,0,0,0,0],
    "scotia-sea-krill-penguin":[0,3,0,0,0,0],
    "gulf-of-maine-herring-whale":[0,0,0,0,0,5],
    "palmyra-like-french-polynesia":[5,3,3,0,0,0],
}

STRENGTH = {
    "TOPP": "many independent env events + hundreds of multi-guild tracks",
    "south-georgia-krill-predators": "true 3-level chain, hourly telemetry",
    "seatrack-sandeel": "long multi-colony GPS panel + open sandeel surveys",
    "calCofi-cps-predator": ">=20 repeated upwelling pulses + direct prey acoustics",
    "peru-anchoveta-seabird": "strong natural contrast (El Nino), 40+ years",
    "benguela-sardine-gannet": "high-res GPS + direct prey surveys",
    "imos-aatams": "huge telemetry archive, open",
    "otn-atlantic": "large acoustic arrays",
    "krillbase-whale": "circumpolar prey database",
    "meop-southern": "hourly in-situ env + predator",
    "eddy-tuna": "many repeated eddy events",
    "north-pacific-salmon-kw": "iconic 2-layer chain",
    "herring-cod-norway": "20+ yr surveys, simultaneous layers",
    "davoren-capelin": "simultaneous prey+predator, prey-defined events",
    "palmyra-pilot": "multi-species telemetry + env",
    "esas-northsea": "30+ yr predator survey + prey surveys",
    "gbr-shark-herbivore": "3-layer reef, long monitoring",
    "ant-peninsula-gentoo": "high-res GPS, open",
    "whaleshark-zooplankton": "aggregation events",
    "california-ecomega": "simultaneous 3-layer ship surveys",
    "scotia-sea-krill-penguin": "3-level polar chain",
    "gulf-of-maine-herring-whale": "20+ yr simultaneous surveys",
    "palmyra-like-french-polynesia": "multi-year predator telemetry",
}
WEAK = {
    "TOPP": "prey layer is survey indices, not concurrent biomass at track scale",
    "south-georgia-krill-predators": "krill biomass rarely concurrent with tracks",
    "seatrack-sandeel": "events effectively annual (~1/yr)",
    "calCofi-cps-predator": "predator layer requires TOPP fusion",
    "peru-anchoveta-seabird": "predator sampling annual; data-request access",
    "benguela-sardine-gannet": "prey annual only",
    "imos-aatams": "no prey layer",
    "otn-atlantic": "restricted access",
    "krillbase-whale": "layers not contemporaneous",
    "meop-southern": "no prey layer",
    "eddy-tuna": "no prey layer - fails trophic criterion",
    "north-pacific-salmon-kw": "restricted predator data",
    "herring-cod-norway": "annual resolution",
    "davoren-capelin": "weekly; 1 pulse/yr; single site",
    "palmyra-pilot": "indirect prey; ~1 seasonal cycle",
    "esas-northsea": "irregular surveys; access forms",
    "gbr-shark-herbivore": "prey monitoring coarse",
    "ant-peninsula-gentoo": "no concurrent prey measurement",
    "whaleshark-zooplankton": "prey episodic",
    "california-ecomega": "raw counts via request; annual",
    "scotia-sea-krill-penguin": "concurrent krill sparse",
    "gulf-of-maine-herring-whale": "annual; access request",
    "palmyra-like-french-polynesia": "no prey layer",
}

rows = []
for _, r in inv.iterrows():
    cid = r["candidate_id"]
    fl = FLAGS[cid]
    pen = PEN[cid]
    rows.append({
        "candidate_id": cid, "ecosystem": r["ecosystem"], "region": r["region"],
        "resource_layer": r["resource_or_prey_layer"],
        "predator_layer": r["predator_layer"],
        "estimated_n_events": r["estimated_n_independent_events"],
        "temporal_resolution": r["temporal_resolution"],
        "years": r["duration_years"],
        "simultaneous_layers": r["contemporaneous_layers"],
        "open_access": r["open_download"],
        "raw_score": sum(fl), "penalty": sum(pen),
        "final_score": sum(fl) - sum(pen),
        "major_strength": STRENGTH[cid], "major_weakness": WEAK[cid],
    })
rank = pd.DataFrame(rows).sort_values("final_score", ascending=False)
rank.insert(0, "rank", range(1, len(rank) + 1))
rank.to_csv(os.path.join(ROOT, "outputs/tables/marine_candidate_ranking.csv"),
            index=False)
print(rank[["rank", "candidate_id", "raw_score", "penalty", "final_score"]].to_string(index=False))
