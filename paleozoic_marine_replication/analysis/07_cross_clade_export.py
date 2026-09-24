"""07: cross-clade analysis + cross-system export (spec s.14, 18-19).

Produces:
  results/tables/cross_system_export.csv
    Only the shared schema columns - directly concatenable with the
    dinosaur / mammal / Quaternary / modern exports.
  results/tables/paleozoic_extended.csv
    Paleozoic-only metadata kept separate.
  results/tables/cross_clade_summary.csv
    Per-clade replication summary (direction/significance of the
    pool-perturbation bias and decay-slope bias).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from _common import OUT

SHARED_COLS = ["system", "realm", "geological_period", "time_bin",
               "time_start_ma", "time_end_ma", "duration_myr", "clade",
               "taxonomic_level", "spatial_resolution", "n_sites",
               "n_collections", "n_occurrences", "gamma", "median_alpha",
               "pool_fraction", "sampling_fraction",
               "temporal_aggregation", "beta_metric", "beta_value",
               "distance_decay_model", "distance_decay_slope",
               "replicate", "analysis_version"]


def main() -> None:
    ref = pd.read_csv(OUT / "core_beta_reference.csv", low_memory=False)
    pool = pd.read_csv(OUT / "pool_perturbation_replicates.csv",
                       low_memory=False)
    fac = pd.read_csv(OUT / "sampling_factorial_replicates.csv",
                      low_memory=False)

    for d in (ref, pool, fac):
        for c in SHARED_COLS:
            if c not in d.columns:
                d[c] = np.nan
    export = pd.concat([d[SHARED_COLS] for d in (ref, pool, fac)],
                       ignore_index=True)
    export.to_csv(OUT / "cross_system_export.csv", index=False)

    # paleozoic-only extended metadata
    ext = pool[["time_bin", "clade", "pool_fraction", "replicate",
                "beta_reference", "decay_reference", "bias_beta",
                "bias_decay"]]
    ext.to_csv(OUT / "paleozoic_extended.csv", index=False)

    # per-clade replication summary: direction of pool-perturbation bias
    rows = []
    for (clade, f), g in pool[pool["pool_fraction"] < 1].groupby(
            ["clade", "pool_fraction"]):
        n_attempted = len(g)
        if "valid" in g.columns:
            n_invalid = int((~g["valid"]).sum())
            g = g[g["valid"]]
        else:
            n_invalid = 0
        bb = g["bias_beta"].to_numpy()
        bd = g["bias_decay"].dropna().to_numpy()
        rows.append({
            "clade": clade, "pool_fraction": f, "n_replicates": len(g),
            "n_attempted": n_attempted, "n_invalid": n_invalid,
            "bias_beta_mean": bb.mean(),
            "bias_beta_lo95": np.quantile(bb, 0.025),
            "bias_beta_hi95": np.quantile(bb, 0.975),
            "prop_bias_beta_positive": (bb > 0).mean(),
            "bias_decay_mean": bd.mean() if len(bd) else np.nan,
            "prop_bias_decay_positive":
                (bd > 0).mean() if len(bd) else np.nan,
        })
    cs = pd.DataFrame(rows)
    cs.to_csv(OUT / "cross_clade_summary.csv", index=False)
    print(cs[cs["pool_fraction"] == 0.5].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
