"""Simulation 04: temporal averaging (B_L).

Taxa occupy different regions in different time slices. Aggregating
slices into wider temporal bins merges spatially separated faunas and
lowers apparent beta diversity. Sweep bin width.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim_core import delta_beta, gen_taxon, mean_beta_jaccard

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

RNG_SEED = 20260922
N_LOC = 200
N_H, N_P = 26, 12
BREADTH = 0.30  # narrower true ranges -> real spatial turnover
OCC_P = 0.4
T_SLICES = 8    # each slice has an independent fauna draw
REPS = 100


def slice_guild(n_loc, n_taxa, breadth, occ_p, rng, t):
    """Each taxon occupies a different random range in slice t."""
    return np.stack(
        [gen_taxon(n_loc, breadth, occ_p, rng) for _ in range(n_taxa)], axis=1
    )


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for n_bins in (8, 4, 2, 1):  # 8 = finest temporal resolution
        group = T_SLICES // n_bins
        vals = []
        for _ in range(REPS):
            mh_bins, mp_bins = [], []
            for b in range(n_bins):
                # per bin, each taxon's occupancy = presence in any slice of the bin
                mh = np.zeros((N_LOC, N_H))
                mp = np.zeros((N_LOC, N_P))
                for s in range(group):
                    mh = np.maximum(mh, np.stack(
                        [gen_taxon(N_LOC, BREADTH, OCC_P, rng) for _ in range(N_H)], axis=1))
                    mp = np.maximum(mp, np.stack(
                        [gen_taxon(N_LOC, BREADTH, OCC_P, rng) for _ in range(N_P)], axis=1))
                mh_b = mh[mh.sum(axis=1) > 0]
                mp_b = mp[mp.sum(axis=1) > 0]
                mh_bins.append(mean_beta_jaccard(mh_b))
                mp_bins.append(mean_beta_jaccard(mp_b))
            vals.append(np.mean(mp_bins) - np.mean(mh_bins))
        vals = np.asarray(vals)
        rows.append(
            {
                "temporal_bins": n_bins,
                "bin_width_slices": group,
                "delta_beta_obs_mean": vals.mean(),
                "lo95": np.quantile(vals, 0.025),
                "hi95": np.quantile(vals, 0.975),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim04_temporal_averaging.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
