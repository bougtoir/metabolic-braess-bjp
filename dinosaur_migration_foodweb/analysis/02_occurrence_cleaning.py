"""Stage 1, step B: clean occurrences and build guild assignment.

Outputs:
- data/processed/occurrences_clean.csv  (one row per occurrence)
- data/processed/collections_clean.csv  (one row per collection, with coords)
- metadata/taxonomy_reconciliation.csv  (identified -> accepted -> guild)

Cleaning rules:
- keep dinosaur occurrences with valid lng/lat;
- taxon label = genus when present, else accepted_name (indeterminate rows kept
  but flagged resolution='indeterminate' and excluded from matrices);
- guild from the PBDB clade field (class): Sauropoda/Ornithischia -> herbivore,
  Theropoda -> predator.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import METADATA, PROCESSED, assign_guild, load_dino_occurrences


def main() -> None:
    df = load_dino_occurrences()
    df["guild"] = df["class"].map(assign_guild)

    keep = [
        "occurrence_no",
        "collection_no",
        "collection_name",
        "identified_name",
        "identified_rank",
        "accepted_name",
        "accepted_rank",
        "genus",
        "family",
        "class",
        "guild",
        "diet",
        "lng",
        "lat",
        "Systems_tract",
        "early_interval",
        "late_interval",
        "max_ma",
        "min_ma",
        "state",
        "county",
        "formation",
        "member",
        "abund_value",
        "abund_unit",
    ]
    occ = df[keep].copy()

    occ["taxon"] = occ["genus"].fillna(occ["accepted_name"])
    occ["taxon"] = occ["taxon"].astype(str).str.strip()
    occ["resolution"] = "genus"
    indet = occ["genus"].isna() | occ["accepted_name"].str.contains(
        r"\bsp\.|indet|n\. gen", case=False, na=False
    )
    occ.loc[indet, "resolution"] = "indeterminate"

    occ = occ.dropna(subset=["lng", "lat"])
    occ.to_csv(PROCESSED / "occurrences_clean.csv", index=False)

    coll = (
        occ.groupby("collection_no")
        .agg(
            collection_name=("collection_name", "first"),
            lng=("lng", "median"),
            lat=("lat", "median"),
            systems_tract=("Systems_tract", "first"),
            n_occurrences=("occurrence_no", "count"),
            n_genera=("genus", "nunique"),
            n_herbivore=("guild", lambda s: (s == "herbivore").sum()),
            n_predator=("guild", lambda s: (s == "predator").sum()),
        )
        .reset_index()
    )
    coll.to_csv(PROCESSED / "collections_clean.csv", index=False)

    recon = (
        occ.groupby(["identified_name", "accepted_name", "genus", "class", "guild"])
        .size()
        .rename("n_occurrences")
        .reset_index()
        .sort_values("n_occurrences", ascending=False)
    )
    METADATA.mkdir(exist_ok=True)
    recon.to_csv(METADATA / "taxonomy_reconciliation.csv", index=False)

    print(
        f"occurrences={len(occ)} collections={len(coll)} "
        f"genera={occ['genus'].nunique()} indeterminate={int(indet.sum())}"
    )


if __name__ == "__main__":
    main()
