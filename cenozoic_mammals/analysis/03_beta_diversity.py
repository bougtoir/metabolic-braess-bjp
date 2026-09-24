"""Cenozoic step 3: herbivore vs predator beta diversity vs distance.

Strict replication of dinosaur_migration_foodweb/analysis/05_beta_diversity.py:
same estimand (Delta-beta = mean pairwise Simpson, predator - herbivore),
same bootstrap (collection rows with replacement, n=999), same Mantel
(Spearman, 9999), same 100 km distance bins. Shared math lives in
src/common/beta_utils.py (byte-identical to the dinosaur module).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "common"))
from _common import FIG_MAIN, TABLES, write_table
from beta_utils import (  # noqa: E402
    beta_by_distance,
    bootstrap_delta_beta,
    guild_pieces,
    load_clean_genus_occurrences,
    mantel,
    mean_beta,
    pairwise_simpson,
    pairwise_sorensen,
)

RNG_SEED = 20240920
N_BOOT = 999
N_PERM = 9999
METRICS = {"simpson": pairwise_simpson, "sorensen": pairwise_sorensen}


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    occ = load_clean_genus_occurrences()
    print(f"genus-resolved guild occurrences: {len(occ)}")

    results: dict[str, float] = {}
    for metric_name, fn in METRICS.items():
        curves = {}
        for guild in ("herbivore", "predator"):
            mat, dist = guild_pieces(occ[occ["guild"] == guild], guild)
            diss = fn(mat.to_numpy())
            obs = beta_by_distance(dist, diss)
            curves[guild] = (obs, dist)
            r, p = mantel(dist, diss, N_PERM, rng)
            results[f"{guild}_{metric_name}_mean_pairwise_beta"] = mean_beta(diss)
            results[f"{guild}_{metric_name}_mantel_r"] = r
            results[f"{guild}_{metric_name}_mantel_p"] = p
            results[f"{guild}_{metric_name}_n_collections"] = int(mat.shape[0])

        h_obs, _ = curves["herbivore"]
        p_obs, _ = curves["predator"]
        delta = pd.DataFrame(
            {
                "distance_km": p_obs.index.union(h_obs.index),
                "beta_predator": p_obs,
                "beta_herbivore": h_obs,
            }
        )
        delta["delta_beta"] = delta["beta_predator"] - delta["beta_herbivore"]
        write_table(delta, f"beta_vs_distance_{metric_name}.csv")
        results[f"delta_beta_{metric_name}_overall"] = float(
            results[f"predator_{metric_name}_mean_pairwise_beta"]
            - results[f"herbivore_{metric_name}_mean_pairwise_beta"]
        )
        deltas = bootstrap_delta_beta(occ, fn, N_BOOT, rng)
        results[f"delta_beta_{metric_name}_boot_lo"] = float(np.quantile(deltas, 0.025))
        results[f"delta_beta_{metric_name}_boot_hi"] = float(np.quantile(deltas, 0.975))
        results[f"delta_beta_{metric_name}_boot_p_gt0"] = float((deltas > 0).mean())

    TABLES.mkdir(parents=True, exist_ok=True)
    pd.Series(results).rename("value").to_csv(TABLES / "beta_summary.csv")
    print(pd.Series(results).to_string())

    # Figure: occurrence map + beta(d) curves (same architecture as dinosaur fig 2)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIG_MAIN.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    for guild, color in (("herbivore", "tab:green"), ("predator", "tab:red")):
        sub = occ[occ["guild"] == guild]
        ax.scatter(sub["lng"], sub["lat"], s=12, alpha=0.6, c=color, label=guild)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Cenozoic (23-5 Ma) North American mammal occurrences")
    ax.legend()
    ax = axes[1]
    for metric_name, ls in (("simpson", "-"), ("sorensen", "--")):
        d = pd.read_csv(TABLES / f"beta_vs_distance_{metric_name}.csv")
        ax.plot(d["distance_km"], d["beta_herbivore"], ls, color="tab:green",
                label=f"herbivore ({metric_name})")
        ax.plot(d["distance_km"], d["beta_predator"], ls, color="tab:red",
                label=f"predator ({metric_name})")
    ax.set_xlabel("Pairwise distance (km)")
    ax.set_ylabel("Mean dissimilarity")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_MAIN / "cenozoic_beta_diversity.png", dpi=200)
    print("wrote figures/main/cenozoic_beta_diversity.png")


if __name__ == "__main__":
    main()
