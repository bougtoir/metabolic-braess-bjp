"""10: common 2-D simulation engine (spec section 12).

REUSES the dinosaur engine verbatim: grid structure, disc-range taxon
generation, perturbation logic and output metrics are the same
functions as dinosaur_migration_foodweb/methodological_beta_bias/
analysis/13_2d_robustness.py. Only parameter values differ; every
difference is logged in results/parameter_registry.csv.

Paleozoic parameterisation: median stage-level gamma across the six
marine clades replaces the Morrison herbivore gamma (26); the reduced
"pool" condition is parameterised directly by pool_fraction.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

DINO = (Path(__file__).resolve().parents[2]
        / "dinosaur_migration_foodweb" / "methodological_beta_bias"
        / "analysis")
sys.path.insert(0, str(DINO))
import importlib
r13 = importlib.import_module("13_2d_robustness")
from _common import OUT  # noqa: E402

RNG_SEED = 20260921
L = 40            # identical lattice (dinosaur: 40x40)
OCC_P = 0.35      # identical occupancy probability
R_FRAC = 0.225    # identical disc radius fraction
REPS = 100

PARAM_DIFFS = [
    ("grid LxL", "40x40", "40x40", "identical"),
    ("range model", "disc radius 0.225L", "disc radius 0.225L",
     "identical"),
    ("occupancy p", "0.35", "0.35", "identical"),
    ("reference gamma", "26 (Morrison herbivores)",
     "60 (typical Paleozoic stage-level clade gamma)",
     "parameter value only"),
    ("contrast axis", "predator vs herbivore pool",
     "full vs contracted pool (pool_fraction)", "reparameterised"),
]


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    xx, yy = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
    coords = np.stack([xx.ravel(), yy.ravel()], axis=1)
    N_REF = 60  # typical stage-level clade gamma (see param registry)
    rows = []
    for f in (1.0, 0.75, 0.5, 0.25):
        n_sub = max(1, int(round(N_REF * f)))
        betas, slopes = [], []
        for _ in range(REPS):
            m_full = r13.guild_2d(L, N_REF, R_FRAC, OCC_P, rng,
                                  drop_empty=False)
            if f < 1.0:
                keep = rng.choice(N_REF, n_sub, replace=False)
                m = m_full[:, keep]
            else:
                m = m_full
            ks = m.sum(1) > 0
            m, co = m[ks], coords[ks]
            if m.shape[0] < 5:
                continue
            betas.append(r13.mean_beta(m))
            slopes.append(r13.decay_slope(m, co))
        rows.append(dict(pool_fraction=f, n_taxa=n_sub,
                         beta_mean=np.mean(betas),
                         beta_lo95=np.quantile(betas, .025),
                         beta_hi95=np.quantile(betas, .975),
                         decay_slope_mean=np.nanmean(slopes)))
    df = pd.DataFrame(rows)
    ref = df[df["pool_fraction"] == 1.0].iloc[0]
    df["bias_beta"] = df["beta_mean"] - ref["beta_mean"]
    df["bias_decay"] = df["decay_slope_mean"] - ref["decay_slope_mean"]
    df.to_csv(OUT / "sim2d_paleozoic_pool.csv", index=False)
    print(df.round(4).to_string(index=False))

    pd.DataFrame(PARAM_DIFFS,
                 columns=["parameter", "dinosaur", "paleozoic",
                          "difference"]).to_csv(
        OUT / "parameter_registry.csv", index=False)


if __name__ == "__main__":
    main()
