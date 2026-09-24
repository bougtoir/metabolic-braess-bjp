"""Cenozoic step 2: clean occurrences, assign guilds (strict replication of
dinosaur analysis/02_occurrence_cleaning.py).

Outputs:
- data/processed/occurrences_clean.csv   (occurrence_no, collection_no, taxon,
  guild, lng, lat, mid_ma, oei, env, ...)
- data/processed/collections_clean.csv   (per-collection summary)
- metadata/taxonomy_reconciliation.csv

Cleaning rules:
- drop occurrences in marine/marginal-marine envs (MARINE_ENV_SUBSTRINGS);
- drop occurrences without coords;
- guild from order (herbivore order set) / Carnivora minus marine families;
- taxon = genus (gnl); indeterminate rows flagged and excluded from matrices;
- mid_ma = mean(eag, lag).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    EXCLUDE_ORDERS,
    MARINE_ENV_SUBSTRINGS,
    METADATA,
    PROCESSED,
    assign_guild,
    load_raw,
)


def main() -> None:
    df = load_raw()
    df.columns = [c.strip() for c in df.columns]

    env_str = df["env"].fillna("").str.lower()
    marine = env_str.str.contains("|".join(MARINE_ENV_SUBSTRINGS))
    df = df[~marine].copy()
    print(f"after marine-env drop: {len(df)}")

    df["guild"] = [assign_guild(o, f) for o, f in zip(df["odl"], df["fml"])]
    df.loc[df["odl"].isin(EXCLUDE_ORDERS), "guild"] = "other"

    df["collection_no"] = df["cid"].astype(str).str.replace("col:", "", regex=False)
    df["taxon"] = df["gnl"].astype("string").str.strip()
    df["resolution"] = "genus"
    indet = df["gnl"].isna() | df["tna"].astype(str).str.contains(
        r"\bsp\.|indet|n\. gen", case=False, na=False
    )
    df.loc[indet, "resolution"] = "indeterminate"

    df["mid_ma"] = (pd.to_numeric(df["eag"], errors="coerce")
                    + pd.to_numeric(df["lag"], errors="coerce")) / 2
    df = df.dropna(subset=["lng", "lat", "mid_ma"])

    keep = [
        "oid", "collection_no", "tna", "gnl", "fml", "odl", "guild",
        "resolution", "taxon", "lng", "lat", "eag", "lag", "mid_ma",
        "oei", "env", "sfm", "smb", "cnm", "stp", "abu", "abv",
    ]
    occ = df[[c for c in keep if c in df.columns]].rename(
        columns={"oid": "occurrence_no", "tna": "accepted_name",
                 "gnl": "genus", "fml": "family", "odl": "order",
                 "oei": "early_interval", "sfm": "formation", "smb": "member",
                 "cnm": "collection_name"}
    )
    PROCESSED.mkdir(parents=True, exist_ok=True)
    occ.to_csv(PROCESSED / "occurrences_clean.csv", index=False)

    coll = (
        occ.groupby("collection_no")
        .agg(
            collection_name=("collection_name", "first"),
            lng=("lng", "median"),
            lat=("lat", "median"),
            mid_ma=("mid_ma", "median"),
            formation=("formation", "first"),
            n_occurrences=("occurrence_no", "count"),
            n_genera=("genus", "nunique"),
            n_herbivore=("guild", lambda s: (s == "herbivore").sum()),
            n_predator=("guild", lambda s: (s == "predator").sum()),
        )
        .reset_index()
    )
    coll.to_csv(PROCESSED / "collections_clean.csv", index=False)

    METADATA.mkdir(exist_ok=True)
    recon = (
        occ.groupby(["accepted_name", "genus", "family", "order", "guild"])
        .size().rename("n_occurrences").reset_index()
        .sort_values("n_occurrences", ascending=False)
    )
    recon.to_csv(METADATA / "taxonomy_reconciliation.csv", index=False)

    g = occ[occ["resolution"] == "genus"]
    print(
        f"occurrences={len(occ)} collections={len(coll)} "
        f"genera={occ['genus'].nunique()} indeterminate={int(indet.sum())} "
        f"herbivore_gen={g.loc[g.guild=='herbivore','genus'].nunique()} "
        f"predator_gen={g.loc[g.guild=='predator','genus'].nunique()}"
    )


if __name__ == "__main__":
    main()
