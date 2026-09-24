"""Stage 1, steps E-F: herbivore vs predator beta diversity vs distance.

Primary quantity: Delta-beta(d) = beta_predator(d) - beta_herbivore(d).

Dissimilarity metric: Simpson turnover (beta_sim) between genus incidence
matrices of collection pairs -- insensitive to richness differences, matching
the hypothesis that predator communities turn over faster in space.
Sorensen dissimilarity is reported alongside as the alternative-metric
sensitivity.

Uncertainty: collections are bootstrapped within each guild (n=999) to get
CIs on beta(d); the Delta-beta bootstrap CI is the difference of guild
bootstrap replicates. A Mantel test (Spearman, 9999 permutations) assesses
distance-decay significance per guild.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import FIG_MAIN, PROCESSED, TABLES, write_table
from beta_utils import (
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

    results: dict[str, float] = {}
    for metric_name, fn in METRICS.items():
        curves: dict[str, tuple[pd.Series, np.ndarray]] = {}
        for guild in ("herbivore", "predator"):
            sub = occ[occ["guild"] == guild]
            mat, dist = guild_pieces(occ, guild)
            diss = fn(mat.to_numpy())
            obs = beta_by_distance(dist, diss)
            curves[guild] = (obs, dist)

            r, p = mantel(dist, diss, N_PERM, rng)
            results[f"{guild}_{metric_name}_mean_pairwise_beta"] = mean_beta(diss)
            results[f"{guild}_{metric_name}_mantel_r"] = r
            results[f"{guild}_{metric_name}_mantel_p"] = p
            results[f"{guild}_{metric_name}_n_collections"] = int(mat.shape[0])

        # bootstrap Delta-beta across bins
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
        write_table(delta, f"stage1_beta_vs_distance_{metric_name}.csv")
        # overall Delta-beta = difference of mean pairwise dissimilarities,
        # the same estimand the collection bootstrap below resamples.
        results[f"delta_beta_{metric_name}_overall"] = float(
            results[f"predator_{metric_name}_mean_pairwise_beta"]
            - results[f"herbivore_{metric_name}_mean_pairwise_beta"]
        )

        # bootstrap CI for overall Delta-beta: resample incidence-matrix rows
        # (collections) with replacement inside each guild
        deltas = bootstrap_delta_beta(occ, fn, N_BOOT, rng)
        results[f"delta_beta_{metric_name}_boot_lo"] = float(np.quantile(deltas, 0.025))
        results[f"delta_beta_{metric_name}_boot_hi"] = float(np.quantile(deltas, 0.975))
        results[f"delta_beta_{metric_name}_boot_p_gt0"] = float((deltas > 0).mean())

    pd.Series(results).rename("value").to_csv(TABLES / "stage1_beta_summary.csv")
    print(pd.Series(results).to_string())

    # Figure 2: occurrence map + beta(d) curves
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
    ax.set_title("Morrison Formation occurrences")
    ax.legend()

    ax = axes[1]
    for metric_name, ls in (("simpson", "-"), ("sorensen", "--")):
        d = pd.read_csv(TABLES / f"stage1_beta_vs_distance_{metric_name}.csv")
        ax.plot(
            d["distance_km"], d["beta_herbivore"], ls, color="tab:green",
            label=f"herbivore ({metric_name})",
        )
        ax.plot(
            d["distance_km"], d["beta_predator"], ls, color="tab:red",
            label=f"predator ({metric_name})",
        )
    ax.set_xlabel("Pairwise distance (km)")
    ax.set_ylabel("Mean pairwise dissimilarity")
    ax.set_title("Beta diversity vs geographic distance")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_MAIN / "figure2_morrison_beta_diversity.png", dpi=200)
    print("wrote figures/main/figure2_morrison_beta_diversity.png")


if __name__ == "__main__":
    main()
