"""Cenozoic step 6: genus-pool null models (required negative control).

Two nulls (promoted to primary per PROTOCOL_DEVIATIONS.md deviation 5):

A. size_matched: draw n_predator-sized random genus subsets from the combined
   genus pool, compute mean_beta for that subset's collections vs a
   n_herbivore-sized subset — null distribution for guild-pool asymmetry.
B. label_shuffle: permute guild labels across genera (keeping pool sizes),
   recompute Delta-beta — null for "any split of this guild asymmetry gives
   the same answer".

Exports observed Delta-beta against each null distribution (quantile).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "common"))
from _common import write_table
from beta_utils import mean_beta, pairwise_simpson  # noqa: E402

RNG_SEED = 20240922
N_NULL = 999


def delta_beta_for(occ: pd.DataFrame) -> float:
    vals = {}
    for guild in ("herbivore", "predator"):
        sub = occ[occ["guild"] == guild]
        mat = pd.crosstab(sub["collection_no"], sub["taxon"]).clip(upper=1)
        vals[guild] = mean_beta(pairwise_simpson(mat.to_numpy()))
    return vals["predator"] - vals["herbivore"]


def main() -> None:
    from _common import PROCESSED

    rng = np.random.default_rng(RNG_SEED)
    occ = pd.read_csv(PROCESSED / "occurrences_clean.csv", low_memory=False)
    occ = occ[(occ["resolution"] == "genus")
              & occ["guild"].isin(["herbivore", "predator"])].copy()

    obs = delta_beta_for(occ)
    n_herb = occ.loc[occ.guild == "herbivore", "taxon"].nunique()
    n_pred = occ.loc[occ.guild == "predator", "taxon"].nunique()
    genera = occ["taxon"].unique()

    rows = []

    # A: size-matched random splits of the combined genus pool
    nulls = np.empty(N_NULL)
    for i in range(N_NULL):
        perm = rng.permutation(genera)
        pred_pool = set(perm[:n_pred])
        herb_pool = set(perm[n_pred:n_pred + n_herb])
        sub = occ[occ["taxon"].isin(pred_pool | herb_pool)].copy()
        sub["guild"] = np.where(sub["taxon"].isin(pred_pool), "predator", "herbivore")
        nulls[i] = delta_beta_for(sub)
    rows.append({"null": "size_matched_split", "observed": obs,
                 "null_mean": nulls.mean(), "null_lo": np.quantile(nulls, 0.025),
                 "null_hi": np.quantile(nulls, 0.975),
                 "quantile": float((nulls <= obs).mean()),
                 "n_rep": N_NULL,
                 "notes": f"random {n_pred}/{n_herb} genus splits"})

    # B: label permutation preserving guild sizes
    nulls2 = np.empty(N_NULL)
    taxa = occ[["taxon", "guild"]].drop_duplicates()
    labels = taxa["guild"].to_numpy()
    for i in range(N_NULL):
        perm_labels = rng.permutation(labels)
        mapping = dict(zip(taxa["taxon"], perm_labels))
        sub = occ.copy()
        sub["guild"] = sub["taxon"].map(mapping)
        sub = sub[sub["guild"].isin(["herbivore", "predator"])]
        nulls2[i] = delta_beta_for(sub)
    rows.append({"null": "label_shuffle", "observed": obs,
                 "null_mean": nulls2.mean(),
                 "null_lo": np.quantile(nulls2, 0.025),
                 "null_hi": np.quantile(nulls2, 0.975),
                 "quantile": float((nulls2 <= obs).mean()),
                 "n_rep": N_NULL,
                 "notes": "permute guild labels across genera, keep pool sizes"})

    out = pd.DataFrame(rows)
    write_table(out, "pool_null.csv")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
