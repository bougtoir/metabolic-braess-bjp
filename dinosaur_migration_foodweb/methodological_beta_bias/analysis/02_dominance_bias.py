"""Simulation 02: dominant-taxon bias (B_D).

Predator guild includes one dominant taxon occupying a fraction p_D of
all localities range-wide. Sweep p_D = 0.1..0.9 with true turnover held
constant; quantify apparent reduction of predator beta (Delta-beta bias).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim_core import delta_beta, gen_guild

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
    rows = []
    for p_d in np.arange(0.0, 0.95, 0.1):
        vals = []
        for _ in range(REPS):
            mh = gen_guild(N_LOC, N_H, BREADTH, OCC_P, rng)
            mp = gen_guild(N_LOC, N_P, BREADTH, OCC_P, rng, dominant_p=p_d)
            vals.append(delta_beta(mh, mp))
        vals = np.asarray(vals)
        rows.append(
            {
                "p_dominant": round(p_d, 2),
                "delta_beta_obs_mean": vals.mean(),
                "lo95": np.quantile(vals, 0.025),
                "hi95": np.quantile(vals, 0.975),
                "prop_negative": (vals < 0).mean(),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim02_dominance_bias.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
