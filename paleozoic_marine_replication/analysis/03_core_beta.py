"""03: core beta-diversity metrics + distance decay per eligible dataset.

Same core metric family as the dinosaur protocol (mean pairwise
Jaccard) plus the required Sorensen / turnover / nestedness components.
Distance decay: OLS slope of pairwise Jaccard ~ great-circle km on
paleocoords (same linear model family as the dinosaur analysis).

Output rows follow the section-18 schema (a superset; extra columns are
appended). Only reference (unperturbed) rows are written here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from _common import (CLADES, DATA_PROC, MIN_PAIRS_DECAY, MIN_SITES,
                     MIN_TAXA, OUT, great_circle_km, grid_cells,
                     pairwise_dissimilarity)

SCHEMES = {"stage": "stage", "stage2": "stage2",
           "10myr": "bin10", "20myr": "bin20", "5myr": "bin5"}
RES = 10  # primary spatial resolution; others are sensitivity


def build_matrices(df: pd.DataFrame, scheme_col: str, res: int):
    """Yield (clade, time_bin, matrix, site_coords)."""
    df = df.copy()
    df["site"] = grid_cells(df, res)
    for (clade, tb), g in df.groupby(["clade", scheme_col]):
        site_ids = sorted(g["site"].unique())
        if len(site_ids) < MIN_SITES or g["genus"].nunique() < MIN_TAXA:
            continue
        coords = (g.groupby("site")[["plat", "plng"]].median()
                  .loc[site_ids].to_numpy())
        mat = (pd.crosstab(g["site"], g["genus"])
               .reindex(site_ids, fill_value=0).clip(upper=1).to_numpy())
        keep = mat.sum(axis=1) > 0
        yield clade, tb, mat[keep], coords[keep]


def metrics_row(system="paleozoic_marine", realm="marine", **kw):
    base = dict(system=system, realm=realm, geological_period="Paleozoic",
                clade=None, taxonomic_level="genus",
                spatial_resolution=None, n_sites=None, n_collections=None,
                n_occurrences=None, gamma=None, median_alpha=None,
                pool_fraction=1.0, sampling_fraction=1.0,
                temporal_aggregation=None, beta_metric=None,
                beta_value=None, distance_decay_model="ols_jaccard_km",
                distance_decay_slope=None, replicate=None,
                analysis_version="paleo_v1")
    base.update(kw)
    return base


def main() -> None:
    df = pd.read_csv(DATA_PROC / "harmonized_occurrences.csv",
                     low_memory=False)
    tb_meta = pd.read_csv(OUT / "time_bins.csv")
    meta = {(r["scheme"], str(r["time_bin"])): r
            for _, r in tb_meta.iterrows()}
    rows = []
    for scheme, col in SCHEMES.items():
        for clade, tb, mat, coords in build_matrices(df, col, RES):
            pd_ = pairwise_dissimilarity(mat)
            la, lo = coords[:, 0], coords[:, 1]
            dist = great_circle_km(la[:, None], lo[:, None],
                                   la[None, :], lo[None, :])
            iu = np.triu_indices(mat.shape[0], 1)
            dvec = dist[iu]
            m = meta.get((scheme, str(tb)))
            n_pairs = len(pd_["jaccard"])
            for metric in ("jaccard", "sorensen", "turnover",
                           "nestedness"):
                rows.append(metrics_row(
                    time_bin=tb,
                    time_start_ma=m["time_start_ma"] if m is not None
                    else np.nan,
                    time_end_ma=m["time_end_ma"] if m is not None
                    else np.nan,
                    duration_myr=m["duration_myr"] if m is not None
                    else np.nan,
                    clade=clade, spatial_resolution=RES,
                    n_sites=mat.shape[0], gamma=mat.shape[1],
                    median_alpha=float(np.median(mat.sum(1))),
                    temporal_aggregation=scheme,
                    beta_metric=metric,
                    beta_value=float(pd_[metric].mean()),
                    distance_decay_slope=(
                        np.polyfit(dvec[pd_["jaccard"] >= 0],
                                   pd_["jaccard"], 1)[0]
                        if metric == "jaccard"
                        and n_pairs >= MIN_PAIRS_DECAY else np.nan),
                    replicate=0))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "core_beta_reference.csv", index=False)
    print(out.groupby(["clade", "beta_metric"]).size()
          .unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()
