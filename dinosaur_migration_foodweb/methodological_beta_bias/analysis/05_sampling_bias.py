"""Simulation 05: sampling / preservation bias (B_S).

Heterogeneous collection intensity and guild-specific detection
probability. Two depositional environments alternate along the axis
(20-locality blocks); predators are preserved preferentially in
environment A while herbivores are sampled uniformly. Quantify the
apparent guild beta shift under increasing sampling asymmetry.
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


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    env_a = (np.arange(N_LOC) % 40) < 20  # alternating env blocks
    rows = []
    for boost in (1.0, 2.0, 4.0, 8.0):
        vals = []
        for _ in range(REPS):
            mh = gen_guild(N_LOC, N_H, BREADTH, OCC_P, rng, keep_empty=True)
            mp = gen_guild(N_LOC, N_P, BREADTH, OCC_P, rng, keep_empty=True)
            keep_h = np.full(N_LOC, 0.6)
            keep_p = np.where(env_a, 0.6, 0.6 / boost)
            mh_o = mh[(rng.random(N_LOC) < keep_h) & (mh.sum(axis=1) > 0)]
            mp_o = mp[(rng.random(N_LOC) < keep_p) & (mp.sum(axis=1) > 0)]
            # after observation drop empty rows
            if mh_o.shape[0] < 5 or mp_o.shape[0] < 5:
                continue
            vals.append(delta_beta(mh_o, mp_o))
        vals = np.asarray(vals)
        rows.append(
            {
                "pred_sampling_ratio_A_vs_B": boost,
                "delta_beta_obs_mean": vals.mean(),
                "lo95": np.quantile(vals, 0.025),
                "hi95": np.quantile(vals, 0.975),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim05_sampling_bias.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
