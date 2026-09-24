"""Simulation 01: gamma-diversity imbalance bias (B_gamma).

Holds true turnover equal for both guilds but varies the predator pool
size relative to the herbivore pool. Fewer predator taxa over the same
geographic extent mechanically lowers mean pairwise predator beta.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim_core import delta_beta, gen_guild, mean_beta_jaccard, sign_class

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

RNG_SEED = 20260922
N_LOC = 200
N_H = 26          # Morrison-like herbivore gamma
BREADTH = 0.45    # range breadth shared by both guilds
OCC_P = 0.35
REPS = 200


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for n_p in (2, 4, 6, 8, 12, 16, 20, 26):
        obs, true = [], []
        for _ in range(REPS):
            mh = gen_guild(N_LOC, N_H, BREADTH, OCC_P, rng)
            mp = gen_guild(N_LOC, n_p, BREADTH, OCC_P, rng)
            # "true" contrast defined at the same pool sizes? No: true
            # ecological turnover is equal breadth -> true delta-beta = 0
            true.append(0.0)
            obs.append(delta_beta(mh, mp))
        obs = np.asarray(obs)
        rows.append(
            {
                "n_pred_taxa": n_p,
                "gamma_ratio_P_over_H": n_p / N_H,
                "delta_beta_true": 0.0,
                "delta_beta_obs_mean": obs.mean(),
                "bias_mean": obs.mean(),
                "lo95": np.quantile(obs, 0.025),
                "hi95": np.quantile(obs, 0.975),
                "prop_negative": (obs < 0).mean(),
                "prop_abs_gt_0.1": (np.abs(obs) > 0.1).mean(),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim01_gamma_bias.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
