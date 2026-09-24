"""Stage 1, step C: per-guild taxon lists and resolution summary."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESSED, TABLES, write_table


def main() -> None:
    occ = pd.read_csv(PROCESSED / "occurrences_clean.csv")

    genera = (
        occ[occ["resolution"] == "genus"]
        .groupby(["guild", "genus"])
        .agg(
            n_occurrences=("occurrence_no", "count"),
            n_collections=("collection_no", "nunique"),
            lat_min=("lat", "min"),
            lat_max=("lat", "max"),
            lng_min=("lng", "min"),
            lng_max=("lng", "max"),
        )
        .reset_index()
        .sort_values(["guild", "n_occurrences"], ascending=[True, False])
    )
    write_table(genera, "stage1_genera_per_guild.csv")

    res = occ.groupby(["guild", "resolution"]).size().unstack(fill_value=0)
    res.to_csv(TABLES / "stage1_taxonomic_resolution.csv")
    print(genera.groupby("guild")["genus"].count())


if __name__ == "__main__":
    main()
