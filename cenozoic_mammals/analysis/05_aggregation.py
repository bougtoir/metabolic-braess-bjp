"""Cenozoic step 5: temporal aggregation sensitivity (Core metric M6).

Recomputes delta_beta_simpson under coarser->finer binnings:
pooled (single window), epoch (early_interval), 5 Ma bins, 1 Ma bins.
Within each bin the pooled Delta-beta is computed and then averaged over
bins (unweighted mean of bin-level estimates, only bins with >=5 collections
per guild). Exported as effect_coarse - effect_fine vs the pooled baseline.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "common"))
from _common import PROCESSED, write_table
from beta_utils import mean_beta, pairwise_simpson  # noqa: E402

MIN_COLL_PER_GUILD = 5


def bin_delta(occ: pd.DataFrame, key: pd.Series) -> float:
    """Mean of per-bin delta_beta over qualifying bins."""
    deltas = []
    for _, grp in occ.groupby(key):
        vals = {}
        ok = True
        for guild in ("herbivore", "predator"):
            sub = grp[grp["guild"] == guild]
            if sub["collection_no"].nunique() < MIN_COLL_PER_GUILD:
                ok = False
                break
            mat = pd.crosstab(sub["collection_no"], sub["taxon"]).clip(upper=1)
            vals[guild] = mean_beta(pairwise_simpson(mat.to_numpy()))
        if ok:
            deltas.append(vals["predator"] - vals["herbivore"])
    return float(np.mean(deltas)) if deltas else np.nan


def main() -> None:
    occ = pd.read_csv(PROCESSED / "occurrences_clean.csv", low_memory=False)
    occ = occ[(occ["resolution"] == "genus")
              & occ["guild"].isin(["herbivore", "predator"])]

    schemes = {
        "pooled": pd.Series("pooled", index=occ.index),
        "epoch": occ["early_interval"].fillna("unassigned"),
        "ma5": (occ["mid_ma"] // 5 * 5).astype(int).astype(str) + "-"
               + (occ["mid_ma"] // 5 * 5 + 5).astype(int).astype(str) + "Ma",
        "ma1": occ["mid_ma"].astype(int).astype(str) + "Ma",
    }
    rows = []
    pooled = bin_delta(occ, schemes["pooled"])
    for name, key in schemes.items():
        d = bin_delta(occ, key)
        rows.append({
            "binning": name,
            "delta_beta": d,
            "delta_vs_pooled": d - pooled if name != "pooled" else 0.0,
        })
    out = pd.DataFrame(rows)
    write_table(out, "aggregation_sensitivity.csv")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
