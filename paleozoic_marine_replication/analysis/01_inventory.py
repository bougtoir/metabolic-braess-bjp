"""01: data inventory + feasibility table by clade and stage.

Reads the harmonised occurrence CSVs, builds the stage-level binning,
and writes:
  - data_inventory.csv          (clade-level counts + field coverage)
  - feasibility_by_stage.csv    (clade x stage: n_colls, n_occs,
                                 n_genera, n_cells10deg)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from _common import CLADES, DATA_PROC, OUT


def load_all() -> pd.DataFrame:
    frames = []
    for c in CLADES:
        f = DATA_PROC / f"occs_{c.lower()}.csv"
        if f.exists():
            frames.append(pd.read_csv(f, low_memory=False))
    df = pd.concat(frames, ignore_index=True)
    df["age_mid"] = (df["early_age"] + df["late_age"]) / 2
    return df


def stage_of(age_mid: np.ndarray, stages: pd.DataFrame) -> np.ndarray:
    """Map numeric age to stage name (PBDB scale-1 stage rows)."""
    s = stages.sort_values("max_ma", ascending=False)
    out = np.full(len(age_mid), None, dtype=object)
    edges = np.sort(s["min_ma"].unique())
    for _, r in s.iterrows():
        m = (age_mid <= r["max_ma"]) & (age_mid > r["min_ma"])
        out[m] = r["interval"]
    return out


def main() -> None:
    df = load_all()
    iv = pd.read_csv(DATA_PROC / "intervals.csv")
    stages = iv[iv["level"] == "age"].copy()  # PBDB stage = 'age' level
    df["stage"] = stage_of(df["age_mid"].to_numpy(), stages)
    df.to_csv(DATA_PROC / "occurrences_staged.csv", index=False)

    # inventory
    inv = []
    for c, g in df.groupby("clade"):
        inv.append({
            "clade": c,
            "n_occurrences": len(g),
            "n_collections": g["collection_id"].nunique(),
            "n_genera": g["genus"].nunique(),
            "n_species_ids": (g["accepted_rank_no"] <= 5).sum(),
            "frac_with_paleocoord": g["plat"].notna().mean(),
            "frac_with_env": g["environment"].notna().mean(),
            "frac_with_lithology": g["lithology1"].notna().mean(),
        })
    pd.DataFrame(inv).to_csv(OUT / "data_inventory.csv", index=False)

    # feasibility by clade x stage
    df["cell10"] = (np.round(df["plat"] / 10).astype("Int64").astype(str)
                    + ":" + np.round(df["plng"] / 10)
                    .astype("Int64").astype(str))
    fe = (df.dropna(subset=["stage"])
            .groupby(["clade", "stage"])
            .agg(n_occurrences=("occurrence_id", "count"),
                 n_collections=("collection_id", "nunique"),
                 n_genera=("genus", "nunique"),
                 n_cells10deg=("cell10", "nunique"))
            .reset_index())
    fe["feasible"] = ((fe["n_collections"] >= 10)
                      & (fe["n_genera"] >= 5)
                      & (fe["n_cells10deg"] >= 5))
    fe.to_csv(OUT / "feasibility_by_stage.csv", index=False)
    print(pd.DataFrame(inv).to_string(index=False))
    print(fe.groupby("clade")["feasible"].sum().to_string())


if __name__ == "__main__":
    main()
