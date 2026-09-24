"""04: taxonomic-pool perturbation (spec section 9).

Holds the observed spatial framework (grid cells, site membership)
fixed and reduces the observable regional genus pool to fractions
{1, 0.75, 0.5, 0.25} with Monte Carlo draws. For every replicate:
  Bias_beta  = beta_perturbed - beta_reference   (Jaccard mean pairwise)
  Bias_decay = slope_perturbed - slope_reference (OLS, Jaccard ~ km)

Every replicate is stored.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from _common import (DATA_PROC, MIN_PAIRS_DECAY, OUT, POOL_FRACTIONS,
                     RNG_SEED, great_circle_km, pairwise_dissimilarity)
from importlib import import_module

b3 = import_module("03_core_beta")

REPS = 200
SCHEMES = {"stage": "stage", "10myr": "bin10"}


def dataset_metrics(mat, coords):
    pd_ = pairwise_dissimilarity(mat)
    la, lo = coords[:, 0], coords[:, 1]
    dist = great_circle_km(la[:, None], lo[:, None],
                           la[None, :], lo[None, :])
    iu = np.triu_indices(mat.shape[0], 1)
    d = dist[iu]
    jac = pd_["jaccard"]
    slope = (np.polyfit(d[d > 0], jac[d > 0], 1)[0]
             if (d > 0).sum() >= MIN_PAIRS_DECAY else np.nan)
    return float(jac.mean()), slope


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    df = pd.read_csv(DATA_PROC / "harmonized_occurrences.csv",
                     low_memory=False)
    tb_meta = pd.read_csv(OUT / "time_bins.csv")
    meta = {(r["scheme"], str(r["time_bin"])): r
            for _, r in tb_meta.iterrows()}
    rows = []
    for scheme, col in SCHEMES.items():
        for clade, tb, mat, coords in b3.build_matrices(df, col, 10):
            if mat.shape[0] < 5 or mat.shape[1] < 5:
                continue
            ref_beta, ref_slope = dataset_metrics(mat, coords)
            m = meta.get((scheme, str(tb)))
            for f in POOL_FRACTIONS:
                n_keep = max(1, int(round(mat.shape[1] * f)))
                for rep in range(REPS if f < 1.0 else 1):
                    valid = True
                    if f >= 1.0:
                        pm, pc = mat, coords
                    else:
                        keep = rng.choice(mat.shape[1], n_keep,
                                          replace=False)
                        keep_sites = mat[:, keep].sum(1) > 0
                        pm = mat[np.ix_(keep_sites, keep)]
                        pc = coords[keep_sites]
                        if pm.shape[0] < 5:
                            valid = False
                    if valid:
                        b, s = dataset_metrics(pm, pc)
                    else:
                        b, s = np.nan, np.nan
                    rows.append({
                        "system": "paleozoic_marine", "realm": "marine",
                        "geological_period": "Paleozoic",
                        "time_bin": tb,
                        "time_start_ma": (m["time_start_ma"]
                                          if m is not None else np.nan),
                        "time_end_ma": (m["time_end_ma"]
                                        if m is not None else np.nan),
                        "duration_myr": (m["duration_myr"]
                                         if m is not None else np.nan),
                        "clade": clade, "taxonomic_level": "genus",
                        "spatial_resolution": 10,
                        "n_sites": pm.shape[0], "gamma": pm.shape[1],
                        "pool_fraction": f, "sampling_fraction": 1.0,
                        "temporal_aggregation": scheme,
                        "beta_metric": "jaccard",
                        "beta_value": b,
                        "distance_decay_model": "ols_jaccard_km",
                        "distance_decay_slope": s,
                        "replicate": rep,
                        "analysis_version": "paleo_v1",
                        "valid": valid,
                        "beta_reference": ref_beta,
                        "decay_reference": ref_slope,
                        "bias_beta": b - ref_beta,
                        "bias_decay": s - ref_slope,
                    })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "pool_perturbation_replicates.csv", index=False)
    print(out.groupby(["clade", "pool_fraction"])["bias_beta"]
          .mean().unstack().round(3).to_string())


if __name__ == "__main__":
    main()
