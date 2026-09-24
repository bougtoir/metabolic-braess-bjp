"""Stage 1, step D: spatial occupancy and geographic ranges per guild.

Grid occupancy is computed at several cell sizes (sensitivity to grid size is
a mandatory sensitivity analysis in the analysis plan).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESSED, haversine_km, write_table

GRID_SIZES_DEG = [0.5, 1.0, 2.0]


def genus_max_range_km(sub: pd.DataFrame) -> float:
    pts = sub[["lng", "lat"]].drop_duplicates()
    if len(pts) < 2:
        return 0.0
    d = haversine_km(
        pts["lng"].to_numpy()[:, None],
        pts["lat"].to_numpy()[:, None],
        pts["lng"].to_numpy()[None, :],
        pts["lat"].to_numpy()[None, :],
    )
    return float(d.max())


def main() -> None:
    occ = pd.read_csv(PROCESSED / "occurrences_clean.csv")
    occ = occ[occ["resolution"] == "genus"]

    rows = []
    for size in GRID_SIZES_DEG:
        g = occ.copy()
        g["cell"] = (
            (g["lng"] // size).astype(int).astype(str)
            + "_"
            + (g["lat"] // size).astype(int).astype(str)
        )
        for guild, gg in g.groupby("guild"):
            rows.append(
                {
                    "grid_size_deg": size,
                    "guild": guild,
                    "n_cells": gg["cell"].nunique(),
                    "n_collections": gg["collection_no"].nunique(),
                    "n_genera": gg["genus"].nunique(),
                    "mean_genera_per_cell": gg.groupby("cell")["genus"].nunique().mean(),
                }
            )
    write_table(pd.DataFrame(rows), "stage1_grid_occupancy.csv")

    ranges = (
        occ.groupby(["guild", "genus"])
        .apply(lambda s: genus_max_range_km(s), include_groups=False)
        .rename("max_range_km")
        .reset_index()
    )
    write_table(ranges, "stage1_genus_ranges.csv")

    summary = (
        ranges.groupby("guild")["max_range_km"]
        .describe()[["count", "mean", "50%", "max"]]
        .rename(columns={"50%": "median"})
    )
    write_table(summary.reset_index(), "stage1_range_summary.csv")
    print(summary)


if __name__ == "__main__":
    main()
