"""Simulation 06: factorial bias map (Figure 3).

Grid over (gamma ratio P/H, dominant prevalence p_D, lumping k). For each
cell, Δβ_true = 0 by construction (equal breadths); Δβ_obs is computed
after distortion. Outputs sign-reversal / false-difference flags.
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

RNG_SEED = 20260923
N_LOC = 200
N_H = 26
BREADTH = 0.45
OCC_P = 0.35
REPS = 100


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for n_p in (4, 12, 26):                    # gamma ratio axis
        for p_d in (0.0, 0.3, 0.5, 0.7, 0.9):  # dominance axis
            for k in (1, 3, 6):                # lumping axis
                vals = []
                for _ in range(REPS):
                    mh = gen_guild(N_LOC, N_H, BREADTH, OCC_P, rng)
                    mp = gen_guild(N_LOC, n_p, BREADTH, OCC_P, rng,
                                   dominant_p=p_d)
                    if k > 1 and mp.shape[1] >= 2:
                        # collapse k columns into one genus column
                        kk = min(k, mp.shape[1])
                        lump = mp[:, :kk].max(axis=1)
                        mp = np.concatenate(
                            [mp[:, kk:], lump[:, None]], axis=1
                        )
                        mp = mp[mp.sum(axis=1) > 0]
                    vals.append(delta_beta(mh, mp))
                vals = np.asarray(vals)
                obs = vals.mean()
                rows.append(
                    {
                        "n_pred_taxa": n_p,
                        "p_dominant": p_d,
                        "n_lumped": k,
                        "delta_beta_true": 0.0,
                        "delta_beta_obs_mean": obs,
                        "bias": obs,
                        "prop_sign_negative": (vals < 0).mean(),
                        "prop_false_difference": (np.abs(vals) > 0.1).mean(),
                    }
                )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim06_factorial.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
