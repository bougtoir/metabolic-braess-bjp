"""05: sampling perturbation + pool x sampling factorial (spec s.10).

Independently reduces collection number (subsample collections before
matrix construction) in a factorial design with the taxonomic-pool
fractions. Stage scheme only, to keep the design fixed. Every
replicate stored.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from importlib import import_module

from _common import (DATA_PROC, OUT, POOL_FRACTIONS, RNG_SEED,
                     SAMP_FRACTIONS)

b3 = import_module("03_core_beta")
b4 = import_module("04_pool_perturbation")

REPS = 50


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    df = pd.read_csv(DATA_PROC / "harmonized_occurrences.csv",
                     low_memory=False)
    tb_meta = pd.read_csv(OUT / "time_bins.csv")
    meta = {(r["scheme"], str(r["time_bin"])): r
            for _, r in tb_meta.iterrows()}
    df["site"] = (np.round(df["plat"] / 10).astype(int).astype(str) + ":"
                  + np.round(df["plng"] / 10).astype(int).astype(str))
    rows = []
    for (clade, tb), g in df.groupby(["clade", "stage"]):
        site_ids = sorted(g["site"].unique())
        if len(site_ids) < 5 or g["genus"].nunique() < 5:
            continue
        coords = (g.groupby("site")[["plat", "plng"]].median()
                  .loc[site_ids].to_numpy())
        colls = g["collection_id"].unique()
        m = meta.get(("stage", str(tb)))
        for fp in POOL_FRACTIONS:
            for fs in SAMP_FRACTIONS:
                for rep in range(REPS if (fp < 1 or fs < 1) else 1):
                    valid = True
                    gs = g
                    if fs < 1.0:
                        keep_c = rng.choice(
                            colls, max(1, int(round(len(colls) * fs))),
                            replace=False)
                        gs = g[g["collection_id"].isin(keep_c)]
                    mat = (pd.crosstab(gs["site"], gs["genus"])
                           .reindex(site_ids, fill_value=0)
                           .clip(upper=1).to_numpy())
                    ks = mat.sum(1) > 0
                    mat, co = mat[ks], coords[ks]
                    if mat.shape[0] < 5:
                        valid = False
                    if valid and fp < 1.0:
                        nk = max(1, int(round(mat.shape[1] * fp)))
                        keep = rng.choice(mat.shape[1], nk,
                                          replace=False)
                        ks2 = mat[:, keep].sum(1) > 0
                        mat, co = mat[np.ix_(ks2, keep)], co[ks2]
                        if mat.shape[0] < 5:
                            valid = False
                    if valid:
                        b, s = b4.dataset_metrics(mat, co)
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
                        "n_sites": mat.shape[0], "gamma": mat.shape[1],
                        "pool_fraction": fp, "sampling_fraction": fs,
                        "temporal_aggregation": "stage",
                        "beta_metric": "jaccard", "beta_value": b,
                        "distance_decay_model": "ols_jaccard_km",
                        "distance_decay_slope": s, "replicate": rep,
                        "analysis_version": "paleo_v1",
                        "valid": valid})
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "sampling_factorial_replicates.csv", index=False)
    piv = out.groupby(["pool_fraction", "sampling_fraction"])[
        "beta_value"].mean().unstack().round(3)
    print(piv.to_string())


if __name__ == "__main__":
    main()
