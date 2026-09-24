"""Stage 1, step A: audit the raw Morrison occurrence dataset.

Produces results/tables/stage1_audit.csv plus a console summary covering
N collections, N occurrences, N taxa per guild, taxonomic resolution,
missingness, and spatial/temporal coverage.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DIAG, GUILD_MAP, OCC_ALL, OCC_DINOS, TABLES, assign_guild


def audit(df: pd.DataFrame, label: str) -> list[dict]:
    rows = []
    n_coll = df["collection_no"].nunique()
    rows += [
        ("dataset", label),
        ("n_occurrences", len(df)),
        ("n_collections", n_coll),
        ("n_genera_nonempty", df["genus"].dropna().nunique()),
        ("n_distinct_genera", df["genus"].nunique()),
        ("occurrences_genus_or_better", (df["accepted_rank"].isin(["genus", "species"])).sum()),
        ("missing_latlng", df[["lng", "lat"]].isna().any(axis=1).sum()),
        ("missing_systems_tract", df.filter(regex="[Ss]ystems").isna().all(axis=1).sum()),
        ("lat_min", df["lat"].min()),
        ("lat_max", df["lat"].max()),
        ("lng_min", df["lng"].min()),
        ("lng_max", df["lng"].max()),
        ("max_ma", df["max_ma"].max()),
        ("min_ma", df["min_ma"].min()),
    ]
    return rows


def main() -> None:
    all_occ = pd.read_excel(OCC_ALL)
    dinos = pd.read_excel(OCC_DINOS)
    rows = audit(all_occ, "all_tetrapods") + audit(dinos, "dinosauria")

    dinos = dinos.assign(guild=dinos["class"].map(assign_guild))
    for guild, g in dinos.groupby("guild"):
        rows += [
            (f"{guild}_occurrences", len(g)),
            (f"{guild}_collections", g["collection_no"].nunique()),
            (f"{guild}_genera", g["genus"].nunique()),
        ]

    out = pd.DataFrame(rows, columns=["metric", "value"])
    TABLES.mkdir(parents=True, exist_ok=True)
    out.to_csv(TABLES / "stage1_audit.csv", index=False)

    # rank resolution table
    rank = (
        dinos.groupby(["guild", "accepted_rank"])
        .size()
        .unstack(fill_value=0)
        .rename_axis("guild")
    )
    rank.to_csv(TABLES / "stage1_rank_resolution.csv")

    miss = dinos[["genus", "diet", "lng", "lat", "Systems_tract"]].isna().sum()
    miss.rename("n_missing").to_csv(TABLES / "stage1_missingness.csv")

    DIAG.mkdir(parents=True, exist_ok=True)
    with open(DIAG / "stage1_audit.txt", "w") as f:
        f.write(out.to_string(index=False))
        f.write("\n\nRank resolution:\n")
        f.write(rank.to_string())
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
