"""06: temporal aggregation experiment (spec section 11).

Progressively merges adjacent temporal bins and measures changes in
beta diversity (Jaccard), turnover, nestedness and the distance-decay
slope. Two aggregations: stage -> 2-stage pairs, and the absolute
ladder 5 -> 10 -> 20 Myr.

Bias_time = metric_aggregated - metric_finest_resolution.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from importlib import import_module

from _common import DATA_PROC, OUT
b3 = import_module("03_core_beta")
b4 = import_module("04_pool_perturbation")


def bin_metrics(df, col):
    """mean per-bin metrics for every eligible (clade, bin)."""
    out = {}
    for clade, tb, mat, coords in b3.build_matrices(df, col, 10):
        if mat.shape[0] < 5 or mat.shape[1] < 5:
            continue
        pd_ = b3.pairwise_dissimilarity(mat)
        beta, slope = b4.dataset_metrics(mat, coords)
        out[(clade, str(tb))] = {
            "beta_jaccard": beta,
            "sorensen": float(pd_["sorensen"].mean()),
            "turnover": float(pd_["turnover"].mean()),
            "nestedness": float(pd_["nestedness"].mean()),
            "decay_slope": slope,
        }
    return out


def main() -> None:
    df = pd.read_csv(DATA_PROC / "harmonized_occurrences.csv",
                     low_memory=False)
    rows = []
    ladders = [("stage", "stage", "stage2", "stage2"),
               ("5myr", "bin5", "10myr", "bin10"),
               ("10myr", "bin10", "20myr", "bin20")]
    for fine_name, fine_col, coarse_name, coarse_col in ladders:
        fm = bin_metrics(df, fine_col)
        cm = bin_metrics(df, coarse_col)
        # map each fine bin to its coarse bin
        map_df = (df[["clade", fine_col, coarse_col]]
                  .dropna().drop_duplicates())
        for _, r in map_df.iterrows():
            key_f = (r["clade"], str(r[fine_col]))
            key_c = (r["clade"], str(r[coarse_col]))
            if key_f not in fm or key_c not in cm:
                continue
            for k in ("beta_jaccard", "sorensen", "turnover",
                      "nestedness", "decay_slope"):
                rows.append({
                    "clade": r["clade"], "fine_scheme": fine_name,
                    "coarse_scheme": coarse_name,
                    "fine_bin": r[fine_col], "coarse_bin": r[coarse_col],
                    "metric": k, "fine_value": fm[key_f][k],
                    "coarse_value": cm[key_c][k],
                    "bias_time": cm[key_c][k] - fm[key_f][k]})
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "temporal_aggregation.csv", index=False)
    print(out.groupby(["coarse_scheme", "metric"])["bias_time"]
          .mean().unstack().round(4).to_string())


if __name__ == "__main__":
    main()
