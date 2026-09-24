"""Stage 1 sampling-bias sensitivity analysis.

Re-estimates overall Delta-beta (mean pairwise Simpson dissimilarity,
predator minus herbivore) under alternative sampling corrections:

A. raw: no correction
B. no_dominant_quarries: drop collections above the 95th percentile of
   occurrences (typically monodominant bone beds)
C. no_singletons: drop collections with fewer than 2 sampled genera
D. equalized_collections: subsample the larger guild's collections down to
   the smaller guild's count, repeated R=999 times
E. spatial_thinning: keep one randomly chosen collection per 1-degree cell,
   repeated R=999 times
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import TABLES, write_table
from beta_utils import (
    guild_pieces,
    load_clean_genus_occurrences,
    mean_beta,
    pairwise_simpson,
)

RNG_SEED = 20240921
N_REP = 999
THIN_CELL_DEG = 1.0


def delta_beta(occ: pd.DataFrame) -> float:
    vals = {}
    for guild in ("herbivore", "predator"):
        mat, _ = guild_pieces(occ[occ["guild"] == guild], guild)
        vals[guild] = mean_beta(pairwise_simpson(mat.to_numpy()))
    return vals["predator"] - vals["herbivore"]


def replicate(fn, n: int) -> np.ndarray:
    return np.array([fn() for _ in range(n)])


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    occ = load_clean_genus_occurrences()

    rows = []

    def record(name, dist: np.ndarray):
        dist = dist[~np.isnan(dist)]
        rows.append(
            {
                "correction": name,
                "delta_beta_mean": dist.mean(),
                "lo95": np.quantile(dist, 0.025),
                "hi95": np.quantile(dist, 0.975),
                "prop_gt0": (dist > 0).mean(),
                "n_rep": len(dist),
            }
        )

    # A: raw
    record("raw", replicate(lambda: delta_beta(occ), 1))

    # B: exclude dominant quarries (top 5% occurrence counts)
    counts = occ.groupby("collection_no").size()
    cap = counts.quantile(0.95)
    keep = counts[counts <= cap].index
    record("no_dominant_quarries", replicate(lambda: delta_beta(occ[occ["collection_no"].isin(keep)]), 1))

    # C: exclude collections with <2 sampled genera
    richness = occ.groupby("collection_no")["taxon"].nunique()
    keep2 = richness[richness >= 2].index
    record("no_singletons", replicate(lambda: delta_beta(occ[occ["collection_no"].isin(keep2)]), 1))

    # D: equalize the number of collections entering each guild's matrix:
    # subsample each guild's collections down to the smaller guild's count.
    coll = {
        g: occ[occ["guild"] == g]["collection_no"].unique()
        for g in ("herbivore", "predator")
    }
    n_min = min(len(v) for v in coll.values())

    def rep_equalized():
        vals = {}
        for g, c in coll.items():
            pick = rng.choice(c, size=n_min, replace=False)
            sub = occ[(occ["guild"] == g) & (occ["collection_no"].isin(pick))]
            mat, _ = guild_pieces(sub, g)
            vals[g] = mean_beta(pairwise_simpson(mat.to_numpy()))
        return vals["predator"] - vals["herbivore"]

    record("equalized_collections", replicate(rep_equalized, N_REP))

    # E: spatial thinning - one collection per 1-degree cell
    coll_tbl = (
        occ.groupby("collection_no")[["lng", "lat"]]
        .median()
        .assign(cell=lambda d: (d["lng"] // THIN_CELL_DEG).astype(int).astype(str)
                                + "_" + (d["lat"] // THIN_CELL_DEG).astype(int).astype(str))
    )

    def rep_thinned():
        keep_ids = coll_tbl.groupby("cell")["lng"].apply(
            lambda s: rng.choice(s.index)
        )
        return delta_beta(occ[occ["collection_no"].isin(keep_ids.values)])

    record("spatial_thinning_1deg", replicate(rep_thinned, N_REP))

    out = pd.DataFrame(rows)
    write_table(out, "stage1_sampling_sensitivity.csv")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
