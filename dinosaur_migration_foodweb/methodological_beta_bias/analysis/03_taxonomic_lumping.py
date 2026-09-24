"""Simulation 03: taxonomic lumping (B_lumping).

A genus-level taxon in the fossil record often pools geographically
partitioned species. Simulate K sister species occupying DISJOINT
sub-regions that are collapsed into one genus column; report
B_lumping = beta_species - beta_genus and the induced Delta-beta shift.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim_core import delta_beta, gen_guild, mean_beta_jaccard

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

RNG_SEED = 20260922
N_LOC = 200
N_H, N_P = 26, 12
BREADTH = 0.45
OCC_P = 0.35
REPS = 200


def partitioned_species(n_loc: int, k: int, occ_p: float, rng) -> np.ndarray:
    """K species each confined to a disjoint k-th of the axis."""
    cols = []
    for i in range(k):
        lo, hi = i / k, (i + 1) / k
        x = np.arange(n_loc) / n_loc
        inside = (x >= lo) & (x < hi)
        v = np.zeros(n_loc)
        v[inside] = rng.random(inside.sum()) < occ_p
        cols.append(v)
    return np.stack(cols, axis=1)


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for k in (1, 2, 3, 4, 6):
        b_lump, d_obs_species, d_obs_genus = [], [], []
        for _ in range(REPS):
            mh = gen_guild(N_LOC, N_H, BREADTH, OCC_P, rng)
            # predator guild: first column replaced by k partitioned species
            mp_base = gen_guild(N_LOC, N_P - 1, BREADTH, OCC_P, rng,
                                keep_empty=True)
            spp = partitioned_species(N_LOC, k, 0.6, rng)
            mp_sp = np.concatenate([mp_base, spp], axis=1)
            mp_sp = mp_sp[mp_sp.sum(axis=1) > 0]
            mp_gen = np.concatenate([mp_base, spp.max(axis=1, keepdims=True)], axis=1)
            mp_gen = mp_gen[mp_gen.sum(axis=1) > 0]
            beta_sp = mean_beta_jaccard(mp_sp)
            beta_g = mean_beta_jaccard(mp_gen)
            b_lump.append(beta_sp - beta_g)
            d_obs_species.append(beta_sp - mean_beta_jaccard(mh))
            d_obs_genus.append(beta_g - mean_beta_jaccard(mh))
        rows.append(
            {
                "n_lumped_species": k,
                "B_lumping_mean": np.mean(b_lump),
                "delta_beta_species": np.mean(d_obs_species),
                "delta_beta_genus": np.mean(d_obs_genus),
                "shift_genus_minus_species": np.mean(d_obs_genus) - np.mean(d_obs_species),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim03_taxonomic_lumping.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
