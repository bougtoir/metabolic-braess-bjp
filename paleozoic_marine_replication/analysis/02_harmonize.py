"""02: build harmonised datasets.

For each temporal scheme (stage, two-stage, 5/10/20 Myr bins) and each
spatial resolution (collection-level not used for beta; grid cells of
5/10/20 degrees on paleocoords), produce presence/absence community
matrices per time bin x clade x spatial unit.

Writes:
  data/processed/harmonized_occurrences.csv  (one row per occurrence with
    all binning columns)
  results/tables/dataset_summary.csv        (per eligible dataset:
    n_sites, n_taxa, gamma, median_alpha, occupancy, intensities)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from _common import (AGE_OLD, AGE_YOUNG, DATA_PROC, MIN_SITES, MIN_TAXA,
                     OUT, grid_cells)

MYR_BINS = [5, 10, 20]
GRID_RES = [5, 10, 20]


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA_PROC / "occurrences_staged.csv",
                     low_memory=False)
    df = df.dropna(subset=["plat", "plng", "genus", "age_mid"])
    return df


def abs_bins(age_mid: np.ndarray, width: float) -> np.ndarray:
    """Absolute-duration bins anchored at the Cambrian base."""
    idx = np.floor((AGE_OLD - age_mid) / width).astype(int)
    return idx


def bin_edges(idx: int, width: float):
    hi = AGE_OLD - idx * width
    lo = max(hi - width, AGE_YOUNG)  # clamp final bin at end-Permian
    return hi, lo


def stage_groups(stages: pd.DataFrame):
    """Ordered list of stage names oldest->youngest plus 2-stage pairs."""
    s = stages.sort_values("max_ma", ascending=False)["interval"].tolist()
    # odd stage count: the youngest stage becomes a singleton coarse bin
    pairs = ["+".join(s[i:i + 2]) for i in range(0, len(s), 2)]
    return s, pairs


def main() -> None:
    df = load()
    iv = pd.read_csv(DATA_PROC / "intervals.csv")
    stages = iv[iv["level"] == "age"].copy()  # PBDB stage = 'age' level
    stage_order, stage_pairs = stage_groups(stages)
    pair_map = {}
    for pair in stage_pairs:
        for s in pair.split("+"):
            pair_map[s] = pair
    df["stage2"] = df["stage"].map(pair_map)
    for w in MYR_BINS:
        df[f"bin{w}"] = abs_bins(df["age_mid"].to_numpy(), w)

    schemes = {"stage": "stage", "stage2": "stage2"} | {
        f"{w}myr": f"bin{w}" for w in MYR_BINS}

    df.to_csv(DATA_PROC / "harmonized_occurrences.csv", index=False)

    # boundary table for bins actually used
    rows = []
    for w in MYR_BINS:
        for idx in sorted(df[f"bin{w}"].unique()):
            hi, lo = bin_edges(idx, w)
            rows.append({"scheme": f"{w}myr", "time_bin": idx,
                         "time_start_ma": hi, "time_end_ma": lo,
                         "duration_myr": hi - lo})
    for _, r in stages.iterrows():
        rows.append({"scheme": "stage", "time_bin": r["interval"],
                     "time_start_ma": r["max_ma"],
                     "time_end_ma": r["min_ma"],
                     "duration_myr": r["max_ma"] - r["min_ma"]})
    for pair in stage_pairs:
        sub = stages[stages["interval"].isin(pair.split("+"))]
        rows.append({"scheme": "stage2", "time_bin": pair,
                     "time_start_ma": sub["max_ma"].max(),
                     "time_end_ma": sub["min_ma"].min(),
                     "duration_myr": sub["max_ma"].max()
                     - sub["min_ma"].min()})
    pd.DataFrame(rows).to_csv(OUT / "time_bins.csv", index=False)

    # dataset summary per scheme x resolution x clade x bin
    drows = []
    for scheme, col in schemes.items():
        for res in GRID_RES:
            df["site"] = grid_cells(df, res)
            for (clade, tb), g in df.groupby(["clade", col]):
                sites = g.groupby("site")
                n_sites = g["site"].nunique()
                gamma = g["genus"].nunique()
                alpha = sites["genus"].nunique()
                if n_sites < MIN_SITES or gamma < MIN_TAXA:
                    continue
                occ_per_site = g.groupby("site")["genus"].count()
                taxon_site = g.groupby("genus")["site"].nunique()
                drows.append({
                    "system": "paleozoic_marine", "realm": "marine",
                    "scheme": scheme, "time_bin": tb, "clade": clade,
                    "spatial_resolution_deg": res,
                    "n_sites": n_sites,
                    "n_collections": g["collection_id"].nunique(),
                    "n_occurrences": len(g),
                    "gamma": gamma,
                    "median_alpha": float(alpha.median()),
                    "median_occupancy": float(taxon_site.median()),
                    "collections_per_site":
                        float(g.groupby("site")["collection_id"]
                              .nunique().median()),
                    "occurrences_per_site": float(occ_per_site.median()),
                })
    ds = pd.DataFrame(drows)
    ds.to_csv(OUT / "dataset_summary.csv", index=False)
    print(ds.groupby(["scheme", "clade"]).size().unstack(fill_value=0)
          .to_string())


if __name__ == "__main__":
    main()
