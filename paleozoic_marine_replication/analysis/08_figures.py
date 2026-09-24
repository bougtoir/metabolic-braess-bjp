"""08: figures F1-F6, structurally parallel to the dinosaur manuscript.

F1 study design + Paleozoic sampling coverage
F2 pool-size perturbation vs beta-diversity bias
F3 pool-size perturbation vs distance-decay bias
F4 sampling x pool-size interaction
F5 temporal aggregation effect
F6 cross-clade replication
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import DATA_PROC, FIG, OUT


def f1() -> None:
    df = pd.read_csv(DATA_PROC / "harmonized_occurrences.csv",
                     low_memory=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    for c, g in df.groupby("clade"):
        ax.hist(g["age_mid"], bins=40, histtype="step", label=c,
                density=True)
    ax.invert_xaxis()
    ax.set_xlabel("Age (Ma)")
    ax.set_ylabel("Density")
    ax.legend(fontsize=7)
    ax.set_title("Sampling coverage")
    ax = axes[1]
    sub = df.sample(min(20000, len(df)), random_state=0)
    ax.scatter(sub["plng"], sub["plat"], s=1, alpha=0.3,
               c=sub["age_mid"], cmap="viridis")
    ax.set_xlabel("Paleolongitude")
    ax.set_ylabel("Paleolatitude")
    ax.set_title("Paleocoordinate coverage")
    fig.tight_layout()
    fig.savefig(FIG / "F1_study_design_coverage.png", dpi=200)
    plt.close(fig)


def f2_f3() -> None:
    pool = pd.read_csv(OUT / "pool_perturbation_replicates.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    ax = axes[0]
    for c, g in pool[pool["pool_fraction"] < 1].groupby("clade"):
        s = g.groupby("pool_fraction")["bias_beta"].mean()
        ax.plot(s.index, s.values, marker="o", ms=3, label=c)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("Pool fraction retained")
    ax.set_ylabel("Bias_beta (Jaccard)")
    ax.set_title("F2 pool-size perturbation vs beta bias")
    ax.legend(fontsize=7)
    ax = axes[1]
    for c, g in pool[(pool["pool_fraction"] < 1)
                     & pool["bias_decay"].notna()].groupby("clade"):
        s = g.groupby("pool_fraction")["bias_decay"].median()
        ax.plot(s.index, s.values, marker="o", ms=3, label=c)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("Pool fraction retained")
    ax.set_ylabel("Bias_decay (slope)")
    ax.set_title("F3 pool-size perturbation vs decay bias")
    fig.tight_layout()
    fig.savefig(FIG / "F2_pool_beta_bias.png", dpi=200)
    # also save right panel standalone for manuscript use
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    for c, g in pool[(pool["pool_fraction"] < 1)
                     & pool["bias_decay"].notna()].groupby("clade"):
        s = g.groupby("pool_fraction")["bias_decay"].median()
        ax2.plot(s.index, s.values, marker="o", ms=3, label=c)
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set_xlabel("Pool fraction retained")
    ax2.set_ylabel("Bias_decay (slope)")
    ax2.legend(fontsize=7)
    fig2.tight_layout()
    fig2.savefig(FIG / "F3_pool_decay_bias.png", dpi=200)
    plt.close("all")


def f4() -> None:
    fac = pd.read_csv(OUT / "sampling_factorial_replicates.csv")
    piv = fac.groupby(["pool_fraction", "sampling_fraction"])[
        "beta_value"].mean().unstack()
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(piv.values, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(piv.columns)), piv.columns)
    ax.set_yticks(range(len(piv.index)), piv.index)
    ax.set_xlabel("Sampling fraction")
    ax.set_ylabel("Pool fraction")
    ax.set_title("F4 mean Jaccard beta (pool x sampling)")
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(FIG / "F4_sampling_pool_interaction.png", dpi=200)
    plt.close(fig)


def f5() -> None:
    ta = pd.read_csv(OUT / "temporal_aggregation.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    for m, g in ta.groupby("metric"):
        s = g.groupby("coarse_scheme")["bias_time"].mean()
        ax.plot(s.index, s.values, marker="o", label=m)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Bias_time (coarse - fine)")
    ax.set_title("F5 temporal aggregation effect")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "F5_temporal_aggregation.png", dpi=200)
    plt.close(fig)


def f6() -> None:
    cs = pd.read_csv(OUT / "cross_clade_summary.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    w = 0.12
    x = np.arange(len(cs["clade"].unique()))
    for k, f in enumerate(sorted(cs["pool_fraction"].unique())):
        g = cs[cs["pool_fraction"] == f].set_index("clade")
        ax.bar(x + k * w,
               [g.loc[c, "bias_beta_mean"] for c in
                sorted(cs["clade"].unique())],
               width=w, label=f"pool {f}")
    ax.set_xticks(x + w, sorted(cs["clade"].unique()), rotation=30,
                  ha="right")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Bias_beta mean")
    ax.set_title("F6 cross-clade replication")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "F6_cross_clade.png", dpi=200)
    plt.close(fig)


def main() -> None:
    f1(); f2_f3(); f4(); f5(); f6()


if __name__ == "__main__":
    main()
